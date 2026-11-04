# 02 — The agent graph as a state machine

**Source:** generalised from internal design documents (see [`../SOURCES.md`](../SOURCES.md)); LangGraph Graph API documentation, https://docs.langchain.com/oss/python/langgraph/graph-api · **Status:** concept primer. No measured numbers.

## In one sentence
The agent is a small state machine with one planner node, two specialist nodes, and a router that sends control back to the planner after every specialist turn until the planner says FINISH.

## What it is
An **agent graph** is a set of **nodes** (each node is one agent turn) joined by **edges** (each edge says which node runs next). A shared **state** object travels along the edges. This is the vocabulary of the LangGraph library: a `StateGraph` with nodes, normal edges, **conditional edges**, and the special `START` and `END` nodes (LangGraph Graph API documentation).

This design has three agent nodes.

- **Orchestrator** — the planner. It reads the task and the state, and chooses the next specialist or FINISH ([[03-the-orchestrator]]).
- **Vision specialist** — sees the screen and acts through it: tap, type, scroll ([[04-the-vision-specialist]]).
- **Actuator** — acts on the system directly: launch an app, change a setting ([[05-the-actuator]]).

## How it works
The graph is:

```
START → orchestrator → router ─┬→ vision specialist → orchestrator
                               ├→ actuator          → orchestrator
                               └→ FINISH            → END
```

1. The graph starts at the orchestrator.
2. The orchestrator returns a routing decision: one of `vision`, `actuator`, `FINISH`.
3. The **router** is a conditional edge. It reads the decision and selects the next node.
4. Each specialist runs its own inner loop ([[06-the-react-loop]]) and then always returns control to the orchestrator.
5. FINISH leads to END. The graph then hands the result to the reporting stage ([[01-the-message-path]]).

The state holds the task, the conversation history, the latest screenshot, each specialist's summary of what it did, and a step counter. A step limit on the outer loop stops a graph that never reaches FINISH. LangGraph calls this the recursion limit and raises an error when a run exceeds it (LangGraph Graph API documentation, "Recursion limit").

**Analogy:** a dispatcher on a radio with two field workers. The dispatcher never touches anything; each worker reports back before the dispatcher sends the next job.

## Design choices and trade-offs
**Why a hand-written graph and not the framework.** The device runtime is Java/Kotlin. The popular agent-graph frameworks are Python-first. The comparison was:

| Concern | Hand-written graph in the device language | Python framework |
|---|---|---|
| Runtime | Native; no extra interpreter | Needs an embedded Python runtime or bindings |
| Overhead | A loop and a switch statement | Framework layers per step |
| Debugging | Direct stack traces in one language | Framework internals between your code and the error |
| Dependencies | None | A large, fast-moving dependency tree |
| Flexibility | Anything; also nothing for free | Checkpoints, streaming, interrupts provided |

The deciding fact is that this graph is small and stable: three nodes and one router. A graph that size reduces to a `while` loop with a `switch` on the routing decision. A framework earns its cost when the graph is large, changes often, or needs features such as persisted checkpoints and human-in-the-loop interrupts.

The hand-written graph still borrows the framework's concepts — named nodes, explicit state, conditional edges, a step limit. These concepts make the code easy to read and make a later port to a framework mechanical.

**Why three agents and not one.**
- *Separation of concerns.* The planner reasons about what to do. The specialists only do.
- *Different model needs.* Planning needs a stronger, slower model. Seeing and tapping needs a fast one ([[07-cost-and-latency]]).
- *Different settings.* Each node gets its own temperature, token budget, and tool list ([[03-the-orchestrator]]).
- *Smaller prompts.* Each specialist sees only its own tools, which cuts tokens and wrong-tool errors.

The cost is extra hops: every specialist turn costs one more orchestrator call.

## Common confusions
- **"Multi-agent means agents talk to each other."** Here they do not. All traffic goes through the orchestrator and the shared state. This is a hub-and-spoke graph.
- **"The router is a model."** The router is plain code. It reads a field that the orchestrator wrote. Only the nodes call a model.
- **"A step limit is the same as a timeout."** The step limit counts graph steps; the watchdog counts seconds ([[01-the-message-path]]). Keep both: a slow step can exhaust time without exhausting steps.

## Why it matters
Writing the agent as an explicit state machine makes every run a trace of named states. That trace is what you debug, audit ([[08-safety]]), and evaluate ([[09-evaluation]]). The framework question is secondary: pick the smallest thing that gives you explicit nodes, explicit state, and a step limit.

## Terms introduced
- **agent graph** — a state machine whose nodes are agent turns and whose edges choose the next turn.
- **node** — one step of the graph; here, one agent's turn.
- **edge / conditional edge** — a link to the next node; a conditional edge picks its target from the state at run time.
- **state** — the shared object that carries task, history, and results between nodes.
- **orchestrator** — the planner node that chooses the next specialist or FINISH.
- **specialist** — a node with a narrow tool set that performs one kind of action.
- **router** — the conditional edge after the orchestrator; plain code, not a model.
- **FINISH / END** — the routing decision that ends the task / the terminal node.
- **step limit (recursion limit)** — the maximum number of graph steps in one run.
