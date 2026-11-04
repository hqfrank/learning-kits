// Generated from learning/agentic-device-control/notes/03-the-orchestrator.md; numbers loaded from constants.json.
window.QUIZ_BANKS = window.QUIZ_BANKS || [];
window.QUIZ_BANKS.push({
 "topic": "agentic-device-control",
 "topicTitle": "Agentic control of a consumer device",
 "section": "03-the-orchestrator",
 "sectionTitle": "03 — The orchestrator: plan, choose, stop",
 "notePath": "../agentic-device-control/notes/03-the-orchestrator.md",
 "knowledgePoints": {
  "plan-one-step": {
   "title": "Plan one step, observe, re-plan",
   "summary": "The orchestrator plans only the next sub-goal; a full plan goes stale after the first unexpected dialog.",
   "source": "03-the-orchestrator §How it works; Common confusions"
  },
  "structured-output": {
   "title": "Structured routing decision",
   "summary": "Output is a structured field (tool call or JSON) plus a short instruction, so plain code routes on one field.",
   "source": "03-the-orchestrator §What it is; How it works"
  },
  "tier-choice": {
   "title": "Stronger tier on the orchestrator",
   "summary": "One wrong route wastes a whole specialist turn, so the orchestrator uses the stronger, slower tier; specialists use the fast tier.",
   "source": "03-the-orchestrator §Design choices and trade-offs"
  },
  "temperature": {
   "title": "Temperature per node",
   "summary": "Orchestrator low but non-zero (illustrative 0.2) to escape loops; specialists 0 to repeat the same action; 0 is more repeatable, not guaranteed identical.",
   "source": "03-the-orchestrator §Design choices and trade-offs; Common confusions"
  },
  "max-tokens": {
   "title": "Maximum output tokens",
   "summary": "Illustrative 4 000 / 4 000 / 2 000 for orchestrator / vision / actuator; too small truncates a tool call, too large raises cost and latency.",
   "source": "03-the-orchestrator §Design choices and trade-offs; Common confusions"
  },
  "stop-on-evidence": {
   "title": "Stop only on evidence",
   "summary": "Premature FINISH comes from unverified success claims; FINISH only on visible evidence; the step limit is the backstop for stopping late.",
   "source": "03-the-orchestrator §Design choices and trade-offs"
  }
 },
 "questions": [
  {
   "id": "q1",
   "type": "mcq",
   "kp": "plan-one-step",
   "prompt": "Why does the orchestrator plan only the next step?",
   "choices": [
    "A full plan goes stale after the first unexpected dialog",
    "Planning more steps is not supported by the API",
    "The router can only read one step",
    "It saves the specialists' tokens"
   ],
   "answer": 0,
   "explanation": "Plan one step, observe, re-plan.",
   "source": "03-the-orchestrator §Common confusions"
  },
  {
   "id": "q2",
   "type": "tf",
   "kp": "plan-one-step",
   "prompt": "The orchestrator should write out the full task plan before routing to any specialist.",
   "answer": false,
   "explanation": "That is the note's listed confusion: a full plan goes stale.",
   "source": "03-the-orchestrator §Common confusions"
  },
  {
   "id": "q3",
   "type": "mcq",
   "kp": "structured-output",
   "prompt": "Why should the orchestrator's output be a structured field and not free text?",
   "choices": [
    "Plain code can then route on one field",
    "Free text costs more cache writes",
    "The model cannot produce free text",
    "The specialists cannot read text"
   ],
   "answer": 0,
   "explanation": "A structured decision lets the router be simple code.",
   "source": "03-the-orchestrator §How it works"
  },
  {
   "id": "q4",
   "type": "tf",
   "kp": "structured-output",
   "prompt": "A routing decision includes a short instruction for the chosen specialist, such as what to find and open.",
   "answer": true,
   "explanation": "For example `vision: \"Find the video app icon on the home screen and open it.\"`",
   "source": "03-the-orchestrator §What it is"
  },
  {
   "id": "q5",
   "type": "mcq",
   "kp": "tier-choice",
   "prompt": "Why does the orchestrator get the stronger, slower model tier?",
   "choices": [
    "One wrong route wastes a whole specialist turn",
    "It makes more calls than the specialists",
    "It must read screenshots at full resolution",
    "The fast tier cannot produce tool calls"
   ],
   "answer": 0,
   "explanation": "Mistakes at the planner are expensive; the specialists use the fast tier.",
   "source": "03-the-orchestrator §Design choices and trade-offs"
  },
  {
   "id": "q6",
   "type": "tf",
   "kp": "tier-choice",
   "prompt": "In this design the vision specialist uses the stronger tier and the orchestrator uses the fast tier.",
   "answer": false,
   "explanation": "It is the other way round.",
   "source": "03-the-orchestrator §Design choices and trade-offs"
  },
  {
   "id": "q7",
   "type": "numeric",
   "kp": "temperature",
   "prompt": "What illustrative temperature does the orchestrator use?",
   "answer": 0.2,
   "unit": "",
   "tolerance": 0.01,
   "explanation": "Low but non-zero, so it can try a different route after a failure.",
   "source": "03-the-orchestrator §Design choices and trade-offs; constants.json orchestrator_temperature_illustrative"
  },
  {
   "id": "q8",
   "type": "mcq",
   "kp": "temperature",
   "prompt": "Why do the specialists use temperature 0 while the orchestrator does not?",
   "choices": [
    "Specialists must repeat the same action for the same screen; the planner sometimes needs variation to leave a loop",
    "Temperature 0 is cheaper per token",
    "The orchestrator's tier does not support 0",
    "Specialists never see screenshots"
   ],
   "answer": 0,
   "explanation": "Consistency for doers, a little variation for the planner.",
   "source": "03-the-orchestrator §Design choices and trade-offs"
  },
  {
   "id": "q9",
   "type": "tf",
   "kp": "temperature",
   "prompt": "Temperature 0 guarantees identical output on every run.",
   "answer": false,
   "explanation": "It makes output far more repeatable, not guaranteed identical; still evaluate over repeated runs.",
   "source": "03-the-orchestrator §Common confusions"
  },
  {
   "id": "q10",
   "type": "numeric",
   "kp": "max-tokens",
   "prompt": "What is the illustrative maximum-output-token budget for the actuator?",
   "answer": 2000,
   "unit": "tokens",
   "tolerance": 0,
   "explanation": "The actuator's replies are short tool calls, so its budget is half the others' (illustrative).",
   "source": "03-the-orchestrator §Design choices and trade-offs; constants.json max_output_tokens_illustrative"
  },
  {
   "id": "q11",
   "type": "mcq",
   "kp": "max-tokens",
   "prompt": "A reply cap that is too small typically shows up as…",
   "choices": [
    "A malformed action, because the reply is cut mid tool call",
    "A cache miss",
    "A BUSY status",
    "A higher temperature"
   ],
   "answer": 0,
   "explanation": "Truncation in the middle of a tool call looks like a malformed action.",
   "source": "03-the-orchestrator §Design choices and trade-offs"
  },
  {
   "id": "q12",
   "type": "tf",
   "kp": "max-tokens",
   "prompt": "Larger output-token budgets are always safer.",
   "answer": false,
   "explanation": "They raise cost and latency on every call, and most routing replies are short.",
   "source": "03-the-orchestrator §Common confusions"
  },
  {
   "id": "q13",
   "type": "mcq",
   "kp": "stop-on-evidence",
   "prompt": "A specialist reports \"done\" but nothing was verified. The orchestrator returns FINISH. What failure is this?",
   "choices": [
    "Premature FINISH",
    "Stuck loop",
    "Grounding miss",
    "Wrong element"
   ],
   "answer": 0,
   "explanation": "Premature FINISH is stopping on an unverified success claim.",
   "source": "03-the-orchestrator §Design choices and trade-offs; Terms introduced"
  },
  {
   "id": "q14",
   "type": "multi",
   "kp": "stop-on-evidence",
   "prompt": "Which practices guard against stopping errors? Select all that apply.",
   "choices": [
    "FINISH only on visible evidence on screen",
    "Ask for a screenshot and explicit check after each step",
    "Use the step limit as a backstop for stopping late",
    "Raise the orchestrator's temperature to 1"
   ],
   "answer": [
    0,
    1,
    2
   ],
   "explanation": "Evidence-based stopping plus the step limit; raising temperature does not help stopping.",
   "source": "03-the-orchestrator §Design choices and trade-offs"
  },
  {
   "id": "q15",
   "type": "tf",
   "kp": "stop-on-evidence",
   "prompt": "When the orchestrator stops, it must say whether the task is done or judged impossible.",
   "answer": true,
   "explanation": "FINISH covers both outcomes, and the decision must say which.",
   "source": "03-the-orchestrator §How it works"
  }
 ]
});
