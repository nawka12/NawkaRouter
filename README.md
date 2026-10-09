# nawka-router

A Claude Code plugin that lets your main model hand each task to the cheapest model and effort level that can do it, and escalate only when a result fails verification. It never uses `max` effort.

## How it works

| Piece | File | What it does |
|---|---|---|
| Routing policy | `ROUTING.md`, injected by a `SessionStart` hook | Rung table, the break-even rule for choosing a starting rung, a brief template, and the escalation path |
| Per-prompt nudge | `UserPromptSubmit` hook (one line) | Reminds the model to route before working. Without it, Sonnet knew the policy but still did tasks itself |
| Rungs | `agents/*.md` | Subagents with the model and effort fixed in frontmatter: `haiku`, `sonnet-high`, `opus-medium`, `opus-high`, `opus-xhigh` |
| Max guard | `PreToolUse` hook on `Agent` | Blocks any spawn that requests `effort: max` |

Delegation always goes down and escalation always goes up. A rung may hand mechanical sub-pieces to cheaper rungs (Claude Code allows nesting 3 levels deep), but it never spawns its own rung or a stronger one. Instead it replies `ESCALATE:` with its findings, and the main thread picks the next rung. Haiku has no `Agent` tool.

**Why subagents:** a model can't switch its own session's model or effort (`/model` and the PreModelSwitch hook only cover switches you or an SDK host request), so subagents are the only lever it can pull itself. The costs: a cold Sonnet or Opus subagent spends about $0.1–0.25 caching its system prompt before doing any work, and the result has to be handed back to the main thread. That is why the policy keeps tiny jobs in the main thread.

## Install

```bash
claude plugin marketplace add ~/Projects/NawkaRouter
claude plugin install nawka-router@nawka
# or, for one session only:
claude --plugin-dir ~/Projects/NawkaRouter
```

## The data behind the rungs

### Artificial Analysis (with fallback; cost = $ per Intelligence Index task)

| Config | Intelligence Index | Terminal-Bench 4.0 | $/task | Verdict |
|---|---|---|---|---|
| Haiku 5.5 low / med / high / xhigh | 29 / 34 / 38 / 41 | ~20% at medium (Anthropic) | 0.02 / 0.05 / 0.08 / ~0.12 | **medium** = `haiku` rung |
| Sonnet 5.5 low / med | 36 / 41 | 20.7% / 29.8% | 0.35 / 0.48 | dominated by Haiku high/xhigh |
| Sonnet 5.5 high | 47 | 43.9% | 0.88 | `sonnet-high` |
| Sonnet 5.5 xhigh | 52 | 57.1% | 2.01 | dominated: Opus high is better and cheaper |
| Opus 5.5 low | 42 | 31.3% | 0.55 | dominated (AA puts it off the frontier) |
| Opus 5.5 medium / high / xhigh | 51 / 54 / 56 | 52.5% / 56.6% / 59.6% | 1.34 / 1.82 / 3.46 | `opus-medium` / `opus-high` / `opus-xhigh` |
| any max | 43 / 56 / 58 | — | 0.21 / 5.46 / 5.98 | banned |

The break-even probabilities in `ROUTING.md` are cost ratios between adjacent rungs. Trying the cheaper rung first pays off only if P(it succeeds) > cost(cheap) / cost(next). Haiku's ratio is 6%, so it's worth trying on anything well-specified. Above Haiku the ratios are 48–74%, so only step down when you're confident.

### Local bench (`bench/`, hidden graders, ground truth from node-semver, Python `re`, and a verified reference solution)

| Task | What it tests | Result |
|---|---|---|
| t1 brand color | multi-file edit, including an `rgba()` form of the color | every config passed |
| t2 discount | feature plus CLI flag, validation | every config passed |
| t3 billing drift | root-cause bug shared by 3 callers | every config passed |
| t4 semver | npm range matcher, 91 cases | every config passed |
| t5 regex | backtracking engine, 94 cases vs `re` | every config passed |
| t6 max-k subarrays | speed up an O(n·k) DP (needs a non-obvious algorithm) | Haiku low, Haiku medium, Sonnet high and Opus high all passed (via subagents) |

That's 63 headless runs plus the T6 subagents, every one passing. Mean cost per run: Haiku $0.01–0.29, Sonnet $0.16–1.25, Opus $0.14–1.73. **For specified work with a runnable check, the stronger rungs bought nothing but a bigger bill.** The tasks where the tiers really differ are long-horizon agentic work, which is what Terminal-Bench measures; there, the AA numbers above decide.

### Low effort: not worth it, so medium is the floor

Low passed every bench task too, but on Haiku it saved only about $0–0.09 per task. A failed attempt costs an escalation to `sonnet-high` (about $0.9), so low pays off only if it fails less than about 3% more often than medium. AA measures low at 5–9 Intelligence Index points below medium on every model, and on Terminal-Bench Opus drops from 52.5% to 31.3%. Sonnet low and Opus low are dominated outright.

## Main-session model

The rungs work under any main model, but the main thread pays for every turn of conversation, review, and routing. Based on the table:
- **Sonnet 5.5 high** is the cheapest main model on the frontier with enough judgment to route. Don't use Sonnet medium: Haiku xhigh matches its score at 1/4 the cost.
- **Opus 5.5 medium** if you want stronger judgment in the main thread. Your current Opus xhigh main costs about 2.6× as much as Opus medium per AA task ($3.46 vs $1.34), and that applies to everything the main thread does itself, including routing and review.

## Limits

- Routing is the main model's judgment. With the per-prompt nudge, Sonnet high delegated a 3-file color change to `haiku`, but did a small feature (t2) itself.
- The bench didn't find where Haiku breaks, because every task had a runnable check that the model could iterate against. For unverifiable or long-horizon work, start higher. The policy says so.
- Numbers are tied to the 5.5 models. Agents pin full model IDs, so re-check the tables when new models ship.

## Re-running the bench

`python3 bench/run.py --configs haiku:medium,sonnet:high --tasks t1,t4 --trials 2` runs headless `claude -p` sessions, which **spend your usage**. The runner resumes after interruptions. `r.<model>:<effort>` configs run a main session with this plugin loaded and record which rungs it spawned. `--warm` measures only the task turn of an already-warm session; that's the fair way to compare routed and solo cost, but it hasn't been run yet. `--summary bench/results/runs.jsonl` prints the table.
