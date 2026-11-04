# 03 — The orchestrator: plan, choose, stop

**Source:** generalised from internal design documents (see [`../SOURCES.md`](../SOURCES.md)); Anthropic Messages API and tool-use documentation, https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview · **Status:** concept primer. Every number is labelled illustrative.

## In one sentence
The orchestrator is the only node that decides what happens next; it reads the task and the latest specialist report, picks one specialist or FINISH, and its temperature and token budget are design knobs that trade consistency against flexibility.

## What it is
The orchestrator is one model call per graph step. Its input is:

- a system prompt that describes the two specialists and the FINISH option;
- the task text;
- the history of earlier routing decisions and specialist summaries;
- optionally, the latest screenshot.

Its output is a routing decision plus a short instruction for the chosen specialist, for example `vision: "Find the video app icon on the home screen and open it."`

## How it works
Each call does three things.

1. **Plan.** It splits the task into the next sub-goal. It does not plan every step in advance; it plans one step and looks at the result.
2. **Choose.** It routes screen work to the vision specialist and system work to the actuator. The rule of thumb in the prompt: if a system action can do it, use the actuator ([[05-the-actuator]]).
3. **Stop.** It returns FINISH when the evidence shows the task is done, or when it judges the task impossible. It must say which.

A good orchestrator output is structured (a tool call or a JSON field), not free text. Plain code then routes on one field ([[02-the-agent-graph]]).

## Design choices and trade-offs
Three knobs are set per node.

- **Model tier.** The orchestrator uses the stronger, slower tier, because one wrong route wastes a whole specialist turn. The specialists use the fast tier ([[07-cost-and-latency]]).
- **Temperature.** Temperature controls how random the model's token choice is; 0 is the most deterministic. The orchestrator uses a low but non-zero value (an illustrative 0.2). The specialists use 0. The reason: the specialists must repeat the same action for the same screen; the orchestrator sometimes needs to try a different route after a failure, and a small amount of variation helps it leave a loop.
- **Maximum output tokens.** This caps the length of one reply. Illustrative budgets are 4 000 tokens for the orchestrator and the vision specialist and 2 000 tokens for the actuator. A cap protects cost and latency. A cap that is too small cuts a reply in the middle of a tool call, which looks like a malformed action.

**Stopping is the hardest decision.** The orchestrator stops early when a specialist claims success that it did not verify. The vendor documentation warns that the model can act as if an action succeeded without checking, and recommends a prompt that asks for a screenshot and an explicit check after each step (computer-use tool documentation, "Optimize model performance with prompting"). Apply the same rule to the orchestrator: FINISH only on visible evidence, such as "the video app's home page is on screen".

The orchestrator stops late when it keeps routing after the goal is reached. The step limit ([[02-the-agent-graph]]) is the backstop.

## Common confusions
- **"Temperature 0 makes the model deterministic."** It makes it far more repeatable, not guaranteed identical. Evaluate over repeated runs anyway ([[09-evaluation]]).
- **"The orchestrator should plan the whole task first."** A full plan goes stale after the first unexpected dialog. Plan one step, observe, re-plan.
- **"More tokens is safer."** Long budgets raise cost and latency on every call; most routing replies are short.

## Why it matters
Almost every expensive failure is an orchestrator failure: a wrong route, a premature FINISH, or no FINISH at all. Put the stronger model here, make its output a structured field, and make it stop only on evidence.

## Terms introduced
- **routing decision** — the orchestrator's structured choice of the next node: a specialist or FINISH.
- **temperature** — a sampling setting that controls randomness in the model's output; 0 is the least random.
- **maximum output tokens** — the per-call cap on reply length.
- **model tier** — a class of model trading capability against speed and price (stronger/slower versus faster/cheaper).
- **premature FINISH** — stopping before the task is done, usually on an unverified success claim.
