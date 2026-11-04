# 06 — The ReAct loop: thought, action, observation

**Source:** ReAct, Yao et al. 2022, https://arxiv.org/abs/2210.03629; Anthropic computer-use tool documentation, https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/computer-use-tool; generalised from internal design documents (see [`../SOURCES.md`](../SOURCES.md)) · **Status:** concept primer. Numbers are public (cited) or labelled illustrative.

## In one sentence
Each specialist runs a ReAct loop — reason about the current observation, request one action, observe the result — and the loop ends when the model replies without a tool call or when an iteration limit is reached.

## What it is
**ReAct** ("reasoning and acting") is a prompting pattern in which a language model interleaves reasoning traces with actions, and each action's result comes back as an observation that the next reasoning step uses (Yao et al. 2022). The paper reports that on two interactive decision-making benchmarks, ALFWorld and WebShop, ReAct beat imitation-learning and reinforcement-learning baselines by an absolute success rate of 34 and 10 percentage points, with only one or two in-context examples (Yao et al. 2022, abstract).

In a device agent the pattern maps directly:

| ReAct term | In the vision specialist |
|---|---|
| Thought | the model's reasoning about the screenshot |
| Action | a computer-use tool call, for example `left_click` |
| Observation | the next screenshot, after the settle delay |

## How it works
One specialist turn runs this loop.

1. **Reason.** Send the conversation history and the current screenshot to the model.
2. **Act.** If the reply contains tool calls, execute each one ([[04-the-vision-specialist]], [[05-the-actuator]]).
3. **Observe.** Wait the settle delay (an illustrative 1 s), capture a screenshot, and return it as the tool result.
4. **Repeat** from step 1.

The loop ends on one of two conditions, which is also the vendor's reference loop (computer-use tool documentation, "Understand the agent loop"):

- the model replies with text and no tool call — it considers its sub-goal done; or
- the iteration count reaches the limit — an illustrative 20 iterations per specialist turn.

The specialist then writes a summary to the shared state and returns to the orchestrator ([[02-the-agent-graph]]).

**Three nested limits** bound one task:

| Limit | Counts | Illustrative value |
|---|---|---|
| Inner iteration limit | ReAct iterations in one specialist turn | 20 |
| Graph step limit | orchestrator → specialist hops | 10 |
| Watchdog timeout | wall-clock time for the whole task | 5 min |

## Design choices and trade-offs
**Retries and recovery from a wrong click.** A wrong click is normal, not exceptional. Recovery works because the next observation shows the wrong screen. The prompt makes this explicit: after each action, describe the screenshot in one sentence and state whether the step succeeded; if not, try again (computer-use tool documentation, "Optimize model performance with prompting"). Common recovery moves are `go_back`, closing an unexpected dialog, or scrolling to find a hidden target.

**Error results instead of exceptions.** When an action fails on the device (coordinate off-screen, capture failed), return a tool result marked as an error with a short description. The model reads it and re-plans (computer-use tool documentation, "Handle errors"). Throwing an exception instead ends the loop without giving the model a chance to recover.

**Loop detection.** A model can repeat one failing action. Detect it in code: if the last few actions are identical and the screenshots are unchanged, stop the turn and report "stuck" to the orchestrator. This is cheaper than waiting for the iteration limit.

**Limit sizing.** A limit that is too low fails long but healthy tasks. A limit that is too high lets a stuck loop burn tokens. Size it from the step-count distribution of successful runs ([[09-evaluation]]), with headroom.

**Analogy:** a person following directions in an unfamiliar building: look, take one step, look again, and turn back at a dead end.

## Common confusions
- **"ReAct is a model feature."** It is a loop you write. The model supplies thoughts and actions; your code supplies observations and limits.
- **"No tool call means the task succeeded."** It means the model *believes* its sub-goal is done. The orchestrator must still check the evidence ([[03-the-orchestrator]]).
- **"One limit is enough."** The iteration limit, step limit, and watchdog catch different failures: a stuck inner loop, a ping-pong between nodes, and a slow model or network.

## Why it matters
The ReAct loop is what turns one fallible guess into a self-correcting process. The engineering is in the edges: honest observations, error results the model can read, loop detection, and limits sized from data.

## Terms introduced
- **ReAct** — a pattern that interleaves model reasoning, actions, and observations in a loop (Yao et al. 2022).
- **thought / action / observation** — the three parts of one ReAct iteration.
- **iteration limit** — the maximum ReAct iterations in one specialist turn.
- **error result** — a tool result that reports a failed action to the model so that it can re-plan.
- **loop detection** — code that stops a turn when the same action repeats with no change on screen.
