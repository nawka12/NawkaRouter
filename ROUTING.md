# nawka-router: model routing policy (active)

You can send work to a cheaper or stronger model by spawning a router rung with the Agent tool: `subagent_type: "nawka-router:<rung>"`. The rung sets the model and effort, so don't pass `model` or `effort` yourself. Never use effort `max`; a hook blocks it.

| Rung | Model @ effort | AA Intelligence | Terminal-Bench 4 | AA $/task | Use for |
|---|---|---|---|---|---|
| `haiku` | Haiku 5.5 @ medium | 34 | ~20% | $0.05 | helper for bigger models: repo searches, triage of many items, verification (run checks, compare output to a spec); plus small code tasks with a runnable check |
| `sonnet-high` | Sonnet 5.5 @ high | 47 | 43.9% | $0.88 | multi-file features/bugs needing judgment, clear spec; code tasks without a runnable check |
| `opus-medium` | Opus 5.5 @ medium | 51 | 52.5% | $1.34 | design-sensitive or ambiguous work needing Opus judgment, not deep reasoning |
| `opus-high` | Opus 5.5 @ high | 54 | 56.6% | $1.82 | hard debugging, unclear root cause, cross-cutting refactors, subtle algorithms |
| `opus-xhigh` | Opus 5.5 @ xhigh | 56 | 59.6% | $3.46 | top rung: only after opus-high failed, or known-very-hard problems |

Every other combination is dominated, so never request it: Sonnet low/medium (Haiku xhigh matches Sonnet medium's score at 1/4 the cost), Sonnet xhigh (Opus high scores higher for less), Opus low (off the cost/quality frontier), and anything at max. Low effort isn't offered: in the local bench it saved only cents on Haiku, while AA shows it costs 5–21 points (Opus on Terminal-Bench: 52.5% at medium, 31.3% at low).

**Local bench (63 runs, hidden graders):** every model at every effort, including Haiku, solved all five well-specified tasks that had a runnable check (multi-file edit, feature plus CLI, root-cause date bug, semver range matcher, regex engine). Cost per task: Haiku $0.01–0.29, Sonnet $0.16–1.25, Opus $0.14–1.73. For specified work with a check, the stronger rungs buy nothing except a bigger bill.

## 1. Route before you work
Before starting any task that will take more than two tool calls, pick a rung. This is the default, not an option.
- **Do it yourself only for:** conversation, questions, planning with the user, edits you can finish in one or two tool calls with context you already hold, and small jobs whose right rung is your own model.
- **Delegate everything else** that you can state in a short brief: implement, fix, refactor, write tests or docs, sweep many files.
- **Haiku is the helper.** Repo searches, triage of many items (files, issues, failing tests) and long check runs go to `haiku`, not your own turns. Haiku 5.5 costs $0.10/$0.50 per million tokens, against $2/$10 for Sonnet and $4/$20 for Opus, so each tool-call turn you do yourself costs 20–40x more than the same turn on Haiku. That price holds only while a request's prompt is under 100K tokens (above it: $0.50/$2.50), and a subagent resends its whole context every turn, so keep Haiku jobs short and split big sweeps into several.
- **Spawn overhead:** a cold Sonnet or Opus subagent costs about $0.1–0.25 before it does any work (system prompt and tools written to cache); a Haiku subagent costs about $0.01. Don't send small jobs to Sonnet or Opus.

## 2. Pick the starting rung (break-even rule)
Start at a cheaper rung A instead of the next rung B only if you'd bet P(A succeeds) > cost(A) / cost(B):

| Instead of… | start lower if P(success) > |
|---|---|
| sonnet-high → try `haiku` first | 6% |
| opus-high → try `sonnet-high` first | 48% |
| opus-medium → try `sonnet-high` first | 66% |
| opus-high → try `opus-medium` first | 74% |
| opus-xhigh → try `opus-high` first | 53% |

In practice: a small, well-specified code task with a runnable check goes to `haiku` first, because a failed Haiku attempt costs almost nothing; that's the case the local bench tested. Code work that is long-horizon or has no runnable check starts at `sonnet-high`. Above that, only step down when you're fairly confident; otherwise start at the stronger rung so you don't pay twice.

## 3. Brief template
Goal · relevant files and what you already know · constraints (don't touch X, keep the API) · **acceptance check** (a command to run or a precise condition) · report format (what changed, how it was verified, or `ESCALATE:` with findings).

## 4. Verify, then escalate
- Check every result before accepting it: run the check and read the diff. For a long check (big test suite, data sweep), `haiku` can run it and return the output; you read that output and decide. A "done" claim isn't evidence; output is.
- On a verified failure or an `ESCALATE:` reply, go one step up the escalation path **haiku → sonnet-high → opus-high → opus-xhigh**. Pass along the original brief plus the failure report so the next rung starts from the findings, not from scratch. Discard the failed attempt's edits if they're wrong.
- Retry the same rung only for environmental failures (a flaky tool or a timeout).
- If opus-xhigh fails, stop and ask the user. There is no higher rung.

## 5. Nesting
Delegate down, escalate up. Rungs should hand searches, triage and long check runs to `haiku` instead of doing them themselves, and may hand other independent mechanical sub-pieces to cheaper rungs. They never spawn their own rung or a stronger one; they report `ESCALATE:` to you instead. Haiku can't spawn.
