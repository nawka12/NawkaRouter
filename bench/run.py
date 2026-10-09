#!/usr/bin/env python3
"""Run the bench tasks headlessly across model:effort configs, grade each run, report.

  python3 bench/run.py --configs haiku:low,haiku:medium --tasks t1,t2 --trials 3 --jobs 8
  python3 bench/run.py --summary bench/results/runs.jsonl

Each run copies tasks/<task>/repo into a scratch dir, runs `claude -p` there with
only file tools plus python/ls/cat/grep/find in Bash, then runs the hidden grader.
"""
import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

HERE = pathlib.Path(__file__).resolve().parent
TOOLS = "Read,Edit,Write,Glob,Grep,Bash"
ALLOW = ["Bash(python3 *)", "Bash(python *)", "Bash(ls *)", "Bash(cat *)", "Bash(grep *)", "Bash(find *)"]
WARMUP = "Read through this project's files and summarize what it does in two sentences. Don't change anything."
WARM = False  # --warm: run WARMUP first, then measure only the task turn on the resumed (cache-warm) session
lock = threading.Lock()


def run_one(task, model, effort, trial, workdir, out):
    tdir = next((HERE / "tasks").glob(f"{task}*"))
    run = workdir / tdir.name / f"{model}-{effort}-{trial}"
    shutil.rmtree(run, ignore_errors=True)
    shutil.copytree(tdir / "repo", run)
    router = model.startswith("r.")  # r.<model>: main session runs with this plugin loaded and may spawn rungs
    flags = ["--model", model.removeprefix("r."), "--effort", effort, "--setting-sources", "local",
             "--tools", TOOLS + (",Agent" if router else ""), "--permission-mode", "acceptEdits",
             "--allowedTools", *ALLOW, "--output-format", "stream-json", "--verbose",
             "--max-budget-usd", "6" if router else "3"]
    if router:
        flags += ["--plugin-dir", str(HERE.parent)]
    prompt = (tdir / "prompt.txt").read_text()
    if WARM:
        sid = str(uuid.uuid4())
        subprocess.run(["claude", "-p", WARMUP, *flags, "--session-id", sid], cwd=run,
                       capture_output=True, text=True, timeout=900, stdin=subprocess.DEVNULL)
        cmd = ["claude", "-p", prompt, *flags, "--resume", sid]
    else:
        cmd = ["claude", "-p", prompt, *flags, "--no-session-persistence"]
    t0 = time.time()
    spawned = []
    try:
        p = subprocess.run(cmd, cwd=run, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                           timeout=2400 if router else 1500)
        events = [json.loads(line) for line in p.stdout.splitlines() if line.startswith("{")]
        d = next(e for e in reversed(events) if e.get("type") == "result")
        spawned = [c["input"].get("subagent_type", "general-purpose") for e in events if e.get("type") == "assistant"
                   for c in e["message"].get("content", []) if c.get("type") == "tool_use" and c["name"] == "Agent"]
    except Exception as e:
        d = {"is_error": True, "result": repr(e)[:300]}
    try:
        g = subprocess.run([sys.executable, "-I", str(tdir / "grade.py"), str(run)],
                           capture_output=True, text=True, timeout=120)
        grade = json.loads(g.stdout.strip().splitlines()[-1])
    except Exception as e:
        grade = {"passed": 0, "total": 1, "fails": [f"grader: {e!r}"[:300]]}
    mu = d.get("modelUsage") or {}
    rec = {
        "task": tdir.name, "model": model, "effort": effort, "trial": trial,
        "model_id": ",".join(mu), "pass": grade["passed"] == grade["total"],
        "score": round(grade["passed"] / grade["total"], 3), "passed": grade["passed"], "total": grade["total"],
        "cost": d.get("total_cost_usd", 0), "turns": d.get("num_turns"),
        "out_tokens": sum(m.get("outputTokens", 0) for m in mu.values()), "warm": WARM,
        "by_model": {k: round(v.get("costUSD", 0), 4) for k, v in mu.items()},
        "secs": round(time.time() - t0), "is_error": d.get("is_error"), "spawned": spawned,
        "fails": grade.get("fails") or [k for k, v in grade.get("checks", {}).items() if not v],
        "result": (d.get("result") or "")[:300],
    }
    with lock:
        with open(out, "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(f"{rec['task']:<18} {model}:{effort:<7} #{trial} pass={rec['pass']!s:<5} "
              f"score={rec['score']:<5} ${rec['cost']:.4f} {rec['secs']}s", flush=True)


def summary(path):
    rows = defaultdict(list)
    for line in open(path):
        r = json.loads(line)
        rows[(r["task"], r["model"], r["effort"])].append(r)
    order = {"haiku": 0, "sonnet": 1, "opus": 2, "r.haiku": 3, "r.sonnet": 4, "r.opus": 5}
    eff = {"low": 0, "medium": 1, "high": 2, "xhigh": 3}
    print(f"{'task':<18} {'config':<14} {'n':>2} {'pass':>6} {'score':>6} {'$/run':>8} {'$/pass':>8} {'turns':>5} {'secs':>5}")
    for (t, m, e), rs in sorted(rows.items(), key=lambda k: (k[0][0], order.get(k[0][1], 9), eff.get(k[0][2], 9))):
        n = len(rs)
        p = sum(r["pass"] for r in rs)
        cost = sum(r["cost"] for r in rs)
        print(f"{t:<18} {m + ':' + e:<14} {n:>2} {p / n:>6.0%} {sum(r['score'] for r in rs) / n:>6.2f} "
              f"{cost / n:>8.4f} {(cost / p if p else float('nan')):>8.4f} "
              f"{sum(r['turns'] or 0 for r in rs) / n:>5.1f} {sum(r['secs'] for r in rs) / n:>5.0f}  "
              + " ".join("+".join(s.removeprefix("nawka-router:") for s in r.get("spawned", [])) or "-" for r in rs if m.startswith("r.")))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--configs", help="comma list of model:effort")
    ap.add_argument("--tasks", default="t1,t2,t3,t4,t5")
    ap.add_argument("--trials", type=int, default=2)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--out", default=str(HERE / "results" / "runs.jsonl"))
    ap.add_argument("--workdir", default=None, help="where run copies go (default: a temp dir)")
    ap.add_argument("--summary", metavar="JSONL")
    ap.add_argument("--warm", action="store_true", help="measure the task turn of an already-warm session")
    a = ap.parse_args()
    WARM = a.warm
    if a.summary:
        summary(a.summary)
        sys.exit()
    workdir = pathlib.Path(a.workdir or tempfile.mkdtemp(prefix="nawka-bench-"))
    pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    # resume: skip (task, model, effort, trial) already recorded without an error (e.g. after a usage limit)
    out = pathlib.Path(a.out)
    done = {(r["task"][:2], r["model"], r["effort"], r["trial"])
            for r in map(json.loads, out.read_text().splitlines() if out.exists() else [])
            if not r["is_error"] and r["cost"]}
    jobs = [(t, *c.split(":"), i, workdir, a.out)
            for i in range(1, a.trials + 1) for c in a.configs.split(",") for t in a.tasks.split(",")
            if (t[:2], *c.split(":"), i) not in done]
    print(f"{len(jobs)} runs to go ({len(done)} already recorded)", flush=True)
    with ThreadPoolExecutor(a.jobs) as ex:
        list(ex.map(lambda j: run_one(*j), jobs))
    summary(a.out)
