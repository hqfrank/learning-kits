// Generated from learning/agentic-device-control/notes/02-the-agent-graph.md; numbers loaded from constants.json.
window.QUIZ_BANKS = window.QUIZ_BANKS || [];
window.QUIZ_BANKS.push({
 "topic": "agentic-device-control",
 "topicTitle": "Agentic control of a consumer device",
 "section": "02-the-agent-graph",
 "sectionTitle": "02 — The agent graph as a state machine",
 "notePath": "../agentic-device-control/notes/02-the-agent-graph.md",
 "knowledgePoints": {
  "graph-vocab": {
   "title": "Nodes, edges, state",
   "summary": "An agent graph is a state machine: nodes are agent turns, edges choose the next node, a shared state carries task, history and results.",
   "source": "02-the-agent-graph §What it is"
  },
  "hub-and-spoke": {
   "title": "Hub-and-spoke topology",
   "summary": "Every specialist returns to the orchestrator; specialists never talk to each other; FINISH leads to END.",
   "source": "02-the-agent-graph §How it works; Common confusions"
  },
  "router-is-code": {
   "title": "The router is plain code",
   "summary": "The router is a conditional edge that reads the orchestrator's decision field; only nodes call a model.",
   "source": "02-the-agent-graph §How it works; Common confusions"
  },
  "step-limit": {
   "title": "Step limit versus timeout",
   "summary": "The step (recursion) limit counts graph steps; the watchdog counts seconds; keep both.",
   "source": "02-the-agent-graph §How it works; Common confusions"
  },
  "handwritten-vs-framework": {
   "title": "Hand-written graph versus Python framework",
   "summary": "A small, stable three-node graph on a Java/Kotlin runtime reduces to a while loop with a switch; a framework earns its cost for large, changing graphs needing checkpoints or interrupts.",
   "source": "02-the-agent-graph §Design choices and trade-offs"
  },
  "why-three-agents": {
   "title": "Why three agents, not one",
   "summary": "Separation of concerns, different model tiers, per-node settings and smaller prompts; the cost is an extra orchestrator hop per specialist turn.",
   "source": "02-the-agent-graph §Design choices and trade-offs"
  }
 },
 "questions": [
  {
   "id": "q1",
   "type": "mcq",
   "kp": "graph-vocab",
   "prompt": "In the agent graph, what is a **node**?",
   "choices": [
    "One agent's turn",
    "A message ID",
    "A cache breakpoint",
    "A screenshot"
   ],
   "answer": 0,
   "explanation": "Nodes are agent turns; edges say which node runs next.",
   "source": "02-the-agent-graph §What it is"
  },
  {
   "id": "q2",
   "type": "tf",
   "kp": "graph-vocab",
   "prompt": "The shared **state** carries the task, the history, the latest screenshot, specialist summaries and a step counter between nodes.",
   "answer": true,
   "explanation": "That is the state described in the note.",
   "source": "02-the-agent-graph §How it works"
  },
  {
   "id": "q3",
   "type": "mcq",
   "kp": "graph-vocab",
   "prompt": "What does a **conditional edge** do?",
   "choices": [
    "Picks its target node from the state at run time",
    "Always goes to the same next node",
    "Calls the model to decide",
    "Stops the graph after a timeout"
   ],
   "answer": 0,
   "explanation": "A conditional edge chooses its target from the state; the router is one.",
   "source": "02-the-agent-graph §Terms introduced"
  },
  {
   "id": "q4",
   "type": "mcq",
   "kp": "hub-and-spoke",
   "prompt": "After the vision specialist finishes its turn, control goes to…",
   "choices": [
    "The orchestrator",
    "The actuator",
    "END",
    "The receiver"
   ],
   "answer": 0,
   "explanation": "Each specialist always returns control to the orchestrator.",
   "source": "02-the-agent-graph §How it works"
  },
  {
   "id": "q5",
   "type": "tf",
   "kp": "hub-and-spoke",
   "prompt": "In this design \"multi-agent\" means the vision specialist and actuator message each other directly.",
   "answer": false,
   "explanation": "All traffic goes through the orchestrator and the shared state; it is hub-and-spoke.",
   "source": "02-the-agent-graph §Common confusions"
  },
  {
   "id": "q6",
   "type": "multi",
   "kp": "hub-and-spoke",
   "prompt": "Which routing decisions can the orchestrator return? Select all that apply.",
   "choices": [
    "`vision`",
    "`actuator`",
    "`FINISH`",
    "`router`"
   ],
   "answer": [
    0,
    1,
    2
   ],
   "explanation": "The router is the edge that reads the decision, not a decision itself.",
   "source": "02-the-agent-graph §How it works"
  },
  {
   "id": "q7",
   "type": "mcq",
   "kp": "router-is-code",
   "prompt": "What is the router?",
   "choices": [
    "Plain code that reads a field the orchestrator wrote",
    "A small fast-tier model",
    "The strong-tier model",
    "A second orchestrator"
   ],
   "answer": 0,
   "explanation": "Only the nodes call a model; the router reads one field.",
   "source": "02-the-agent-graph §Common confusions"
  },
  {
   "id": "q8",
   "type": "tf",
   "kp": "router-is-code",
   "prompt": "The router makes a model call to choose between the specialists.",
   "answer": false,
   "explanation": "The router is a conditional edge implemented in plain code.",
   "source": "02-the-agent-graph §Common confusions"
  },
  {
   "id": "q9",
   "type": "mcq",
   "kp": "step-limit",
   "prompt": "A single model call hangs on a slow network. Which limit catches it?",
   "choices": [
    "The watchdog timeout",
    "The step limit",
    "The de-duplication cache",
    "The router"
   ],
   "answer": 0,
   "explanation": "A slow step can exhaust time without exhausting steps; the watchdog counts seconds.",
   "source": "02-the-agent-graph §Common confusions"
  },
  {
   "id": "q10",
   "type": "tf",
   "kp": "step-limit",
   "prompt": "The step limit and the watchdog timeout are redundant, so one can be dropped.",
   "answer": false,
   "explanation": "The step limit counts graph steps and the watchdog counts seconds; they catch different failures.",
   "source": "02-the-agent-graph §Common confusions"
  },
  {
   "id": "q11",
   "type": "mcq",
   "kp": "step-limit",
   "prompt": "What does LangGraph call its equivalent of the step limit?",
   "choices": [
    "Recursion limit",
    "Iteration cap",
    "Watchdog",
    "Breakpoint"
   ],
   "answer": 0,
   "explanation": "LangGraph raises an error when a run exceeds its recursion limit.",
   "source": "02-the-agent-graph §How it works"
  },
  {
   "id": "q12",
   "type": "mcq",
   "kp": "handwritten-vs-framework",
   "prompt": "What was the **deciding fact** for a hand-written graph?",
   "choices": [
    "The graph is small and stable: three nodes and one router",
    "Python frameworks cannot express conditional edges",
    "Hand-written graphs are always faster to build",
    "The model requires Java"
   ],
   "answer": 0,
   "explanation": "A graph that size reduces to a `while` loop with a `switch`.",
   "source": "02-the-agent-graph §Design choices and trade-offs"
  },
  {
   "id": "q13",
   "type": "multi",
   "kp": "handwritten-vs-framework",
   "prompt": "When does a framework earn its cost? Select all that apply.",
   "choices": [
    "The graph is large",
    "The graph changes often",
    "You need persisted checkpoints or human-in-the-loop interrupts",
    "The graph has three nodes and never changes"
   ],
   "answer": [
    0,
    1,
    2
   ],
   "explanation": "The last case is exactly this design, where the framework's overhead buys nothing.",
   "source": "02-the-agent-graph §Design choices and trade-offs"
  },
  {
   "id": "q14",
   "type": "tf",
   "kp": "handwritten-vs-framework",
   "prompt": "The hand-written graph still borrows framework concepts — named nodes, explicit state, conditional edges, a step limit.",
   "answer": true,
   "explanation": "This keeps the code readable and makes a later port mechanical.",
   "source": "02-the-agent-graph §Design choices and trade-offs"
  },
  {
   "id": "q15",
   "type": "multi",
   "kp": "why-three-agents",
   "prompt": "Which are reasons for three agents instead of one? Select all that apply.",
   "choices": [
    "Planning needs a stronger model; tapping needs a fast one",
    "Each node gets its own temperature, token budget and tools",
    "Smaller prompts cut tokens and wrong-tool errors",
    "It removes the orchestrator hop"
   ],
   "answer": [
    0,
    1,
    2
   ],
   "explanation": "Three agents add an orchestrator hop per specialist turn; that is the cost, not a gain.",
   "source": "02-the-agent-graph §Design choices and trade-offs"
  },
  {
   "id": "q16",
   "type": "mcq",
   "kp": "why-three-agents",
   "prompt": "What is the main cost of the three-agent split?",
   "choices": [
    "Every specialist turn costs one more orchestrator call",
    "Specialists cannot use tools",
    "The router needs its own model",
    "State cannot be shared"
   ],
   "answer": 0,
   "explanation": "Extra hops are the price of separation of concerns.",
   "source": "02-the-agent-graph §Design choices and trade-offs"
  }
 ]
});
