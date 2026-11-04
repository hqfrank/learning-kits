// Generated from learning/agentic-device-control/notes/06-the-react-loop.md; numbers loaded from constants.json.
window.QUIZ_BANKS = window.QUIZ_BANKS || [];
window.QUIZ_BANKS.push({
 "topic": "agentic-device-control",
 "topicTitle": "Agentic control of a consumer device",
 "section": "06-the-react-loop",
 "sectionTitle": "06 — The ReAct loop: thought, action, observation",
 "notePath": "../agentic-device-control/notes/06-the-react-loop.md",
 "knowledgePoints": {
  "react-pattern": {
   "title": "The ReAct pattern",
   "summary": "Interleave reasoning, actions and observations; ReAct beat baselines by 34 pp (ALFWorld) and 10 pp (WebShop) with 1–2 in-context examples (public).",
   "source": "06-the-react-loop §What it is"
  },
  "react-mapping": {
   "title": "ReAct in the vision specialist",
   "summary": "Thought = reasoning about the screenshot; action = a computer-use tool call; observation = the next screenshot after the settle delay.",
   "source": "06-the-react-loop §What it is"
  },
  "loop-end": {
   "title": "How a turn ends",
   "summary": "A reply with no tool call (model believes its sub-goal is done) or the iteration limit; no tool call is not proof of success.",
   "source": "06-the-react-loop §How it works; Common confusions"
  },
  "nested-limits": {
   "title": "Three nested limits",
   "summary": "Inner iteration limit (illustrative 20), graph step limit (illustrative 10), watchdog (illustrative 5 min) catch a stuck inner loop, node ping-pong, and slow model or network.",
   "source": "06-the-react-loop §How it works; Common confusions"
  },
  "recovery-errors": {
   "title": "Recovery and error results",
   "summary": "A wrong click is normal; the next observation shows it; return failures as error results the model can read, not exceptions that end the loop.",
   "source": "06-the-react-loop §Design choices and trade-offs"
  },
  "loop-detection-sizing": {
   "title": "Loop detection and limit sizing",
   "summary": "Stop when identical actions leave the screen unchanged; size limits from the step-count distribution of successful runs, with headroom.",
   "source": "06-the-react-loop §Design choices and trade-offs"
  }
 },
 "questions": [
  {
   "id": "q1",
   "type": "mcq",
   "kp": "react-pattern",
   "prompt": "What does ReAct interleave?",
   "choices": [
    "Reasoning traces, actions and observations",
    "Training and inference",
    "Planning and caching",
    "Screenshots and audio"
   ],
   "answer": 0,
   "explanation": "Each action's result returns as an observation that the next reasoning step uses.",
   "source": "06-the-react-loop §What it is"
  },
  {
   "id": "q2",
   "type": "numeric",
   "kp": "react-pattern",
   "prompt": "By how many percentage points of absolute success rate did ReAct beat baselines on ALFWorld (public)?",
   "answer": 34,
   "unit": "pp",
   "tolerance": 0,
   "explanation": "Yao et al. 2022 report 34 pp on ALFWorld and 10 pp on WebShop.",
   "source": "06-the-react-loop §What it is; constants.json react_alfworld_gain_pp"
  },
  {
   "id": "q3",
   "type": "tf",
   "kp": "react-pattern",
   "prompt": "ReAct is a model feature that must be switched on in the API.",
   "answer": false,
   "explanation": "It is a loop you write: the model supplies thoughts and actions, your code supplies observations and limits.",
   "source": "06-the-react-loop §Common confusions"
  },
  {
   "id": "q4",
   "type": "mcq",
   "kp": "react-pattern",
   "prompt": "Roughly how many in-context examples did ReAct need for those results (public)?",
   "choices": [
    "1 or 2",
    "about 100",
    "thousands (fine-tuning)",
    "none at all"
   ],
   "answer": 0,
   "explanation": "Only 1 or 2 in-context examples (Yao et al. 2022, abstract).",
   "source": "06-the-react-loop §What it is; constants.json react_in_context_examples"
  },
  {
   "id": "q5",
   "type": "mcq",
   "kp": "react-mapping",
   "prompt": "In the vision specialist, what is the **observation**?",
   "choices": [
    "The next screenshot, after the settle delay",
    "The model's reasoning text",
    "The `left_click` call",
    "The orchestrator's routing decision"
   ],
   "answer": 0,
   "explanation": "Thought = reasoning, action = tool call, observation = next screenshot.",
   "source": "06-the-react-loop §What it is"
  },
  {
   "id": "q6",
   "type": "tf",
   "kp": "react-mapping",
   "prompt": "The observe step waits the settle delay (illustrative 1 s) before capturing and returning the screenshot as the tool result.",
   "answer": true,
   "explanation": "Waiting lets the UI finish changing before the model looks.",
   "source": "06-the-react-loop §How it works"
  },
  {
   "id": "q7",
   "type": "multi",
   "kp": "loop-end",
   "prompt": "Which conditions end one specialist turn? Select all that apply.",
   "choices": [
    "The model replies with text and no tool call",
    "The iteration count reaches the limit",
    "Loop detection reports \"stuck\"",
    "The cache entry expires"
   ],
   "answer": [
    0,
    1,
    2
   ],
   "explanation": "The vendor loop ends on no tool call or the limit; loop detection stops a stuck turn earlier. Cache expiry only costs money.",
   "source": "06-the-react-loop §How it works; Design choices and trade-offs"
  },
  {
   "id": "q8",
   "type": "tf",
   "kp": "loop-end",
   "prompt": "A reply with no tool call means the task succeeded.",
   "answer": false,
   "explanation": "It means the model believes its sub-goal is done; the orchestrator must still check the evidence.",
   "source": "06-the-react-loop §Common confusions"
  },
  {
   "id": "q9",
   "type": "mcq",
   "kp": "nested-limits",
   "prompt": "The orchestrator and a specialist hand the same sub-goal back and forth. Which limit catches it?",
   "choices": [
    "The graph step limit",
    "The inner iteration limit",
    "The de-duplication window",
    "The cache lifetime"
   ],
   "answer": 0,
   "explanation": "Ping-pong between nodes consumes graph steps, not inner iterations.",
   "source": "06-the-react-loop §Common confusions"
  },
  {
   "id": "q10",
   "type": "numeric",
   "kp": "nested-limits",
   "prompt": "What is the illustrative inner iteration limit per specialist turn?",
   "answer": 20,
   "unit": "iterations",
   "tolerance": 0,
   "explanation": "An illustrative 20; the graph step limit is 10 hops and the watchdog 5 min.",
   "source": "06-the-react-loop §How it works; constants.json react_iteration_limit_illustrative"
  },
  {
   "id": "q11",
   "type": "tf",
   "kp": "nested-limits",
   "prompt": "One limit is enough if it is chosen well.",
   "answer": false,
   "explanation": "The three limits catch different failures: stuck inner loop, ping-pong, slow model or network.",
   "source": "06-the-react-loop §Common confusions"
  },
  {
   "id": "q12",
   "type": "mcq",
   "kp": "recovery-errors",
   "prompt": "The requested coordinate is off-screen. What should the device return?",
   "choices": [
    "A tool result marked as an error with a short description",
    "An exception that ends the loop",
    "A blank screenshot",
    "FINISH"
   ],
   "answer": 0,
   "explanation": "The model reads the error result and re-plans; an exception gives it no chance to recover.",
   "source": "06-the-react-loop §Design choices and trade-offs"
  },
  {
   "id": "q13",
   "type": "multi",
   "kp": "recovery-errors",
   "prompt": "Which are common recovery moves after a wrong click? Select all that apply.",
   "choices": [
    "`go_back`",
    "Close an unexpected dialog",
    "Scroll to find a hidden target",
    "Restart the watchdog"
   ],
   "answer": [
    0,
    1,
    2
   ],
   "explanation": "Recovery works because the next observation shows the wrong screen.",
   "source": "06-the-react-loop §Design choices and trade-offs"
  },
  {
   "id": "q14",
   "type": "tf",
   "kp": "recovery-errors",
   "prompt": "A wrong click is an exceptional event that should end the specialist turn.",
   "answer": false,
   "explanation": "A wrong click is normal; the loop recovers from it.",
   "source": "06-the-react-loop §Design choices and trade-offs"
  },
  {
   "id": "q15",
   "type": "mcq",
   "kp": "loop-detection-sizing",
   "prompt": "How should the iteration limit be sized?",
   "choices": [
    "From the step-count distribution of successful runs, with headroom",
    "As low as possible to save tokens",
    "Equal to the graph step limit",
    "At the median step count"
   ],
   "answer": 0,
   "explanation": "Too low fails healthy long tasks; too high lets a stuck loop burn tokens.",
   "source": "06-the-react-loop §Design choices and trade-offs"
  },
  {
   "id": "q16",
   "type": "tf",
   "kp": "loop-detection-sizing",
   "prompt": "Loop detection in code (identical actions, unchanged screen) is cheaper than waiting for the iteration limit.",
   "answer": true,
   "explanation": "It stops the turn and reports \"stuck\" to the orchestrator early.",
   "source": "06-the-react-loop §Design choices and trade-offs"
  }
 ]
});
