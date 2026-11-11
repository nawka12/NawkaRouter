# nawka-router: Fable advisor (enabled)

`nawka-fable:advisor` runs Fable 5.2 at high effort as an advisor. It can't see the codebase: it reads only the brief you send, and it answers with advice. It never implements; you or a rung do that. Fable costs $8/$40 per million tokens, twice Opus 5.5 and 80 times Haiku, so ask it one focused question at a time, never as a working loop.

| Rung | Model @ effort | AA Intelligence (v5.0.1) | AA $/task | Use for |
|---|---|---|---|---|
| `nawka-fable:advisor` | Fable 5.2 @ high | 62 | $9.08 | second opinion on a hard call: a design choice, a plan or diff review, a root-cause hypothesis after a rung failed |

On the same index, Fable 5.2 xhigh also scores 62 but costs $14.83 per task, so it's dominated; max is banned. Opus 5.5's best score there is 59, at max.

## When to ask
- Before you commit to a design or plan that would be expensive to undo, when you're unsure.
- After opus-high or opus-xhigh failed and the root cause is still unclear. Ask before the next rung, or before you stop to ask the user.
- To review a risky plan or diff that you paste in.

Don't ask about anything a rung can simply try and check, routine reviews, or questions you can answer confidently yourself. Never send it implementation work.

## Brief
Gather the context first, yourself or with `haiku` for searches, and paste it in. Include the question · the relevant code excerpts, errors and output, verbatim and trimmed to what matters · what was tried and how it failed · constraints · the form of answer you want (a decision, a ranked list, yes/no). Every token of the brief is billed at Fable's rate, so trim it. If the advisor replies `NEED:`, send what it lists to the same agent with SendMessage instead of spawning a new one.

## After the advice
Advice is a hypothesis, not a result. Turn it into a brief for the right rung (or do it yourself if it's small) and verify the result as usual. Only the main thread calls the advisor; rungs report `ESCALATE:` to you as before.
