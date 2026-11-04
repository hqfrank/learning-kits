// Generated from learning/agentic-device-control/notes/05-the-actuator.md; numbers loaded from constants.json.
window.QUIZ_BANKS = window.QUIZ_BANKS || [];
window.QUIZ_BANKS.push({
 "topic": "agentic-device-control",
 "topicTitle": "Agentic control of a consumer device",
 "section": "05-the-actuator",
 "sectionTitle": "05 — The actuator: system actions that bypass the UI",
 "notePath": "../agentic-device-control/notes/05-the-actuator.md",
 "knowledgePoints": {
  "actuator-role": {
   "title": "What the actuator does",
   "summary": "Acts through OS interfaces — launch an app, open a settings page, change device state — not through the screen.",
   "source": "05-the-actuator §In one sentence; What it is"
  },
  "function-calling": {
   "title": "Function-calling tools",
   "summary": "Each tool has a name, description and typed input schema; the model returns a structured call; same protocol as the computer-use tool but with your own schemas.",
   "source": "05-the-actuator §What it is; Common confusions"
  },
  "why-bypass": {
   "title": "Why bypass the UI",
   "summary": "Illustratively 1 model call and ~2 s versus 2 calls and ~10 s, no grounding error, and works when the target is off-screen or behind a dialog.",
   "source": "05-the-actuator §Design choices and trade-offs"
  },
  "why-keep-vision": {
   "title": "Why the vision route remains",
   "summary": "OS interfaces cover the OS, not the inside of apps; searching inside an app needs the screen.",
   "source": "05-the-actuator §Design choices and trade-offs"
  },
  "narrow-tools": {
   "title": "Narrow, allow-listed tools",
   "summary": "Named, typed operations only; a generic shell tool removes every guard; device code checks calls against an allow-list.",
   "source": "05-the-actuator §How it works; Common confusions"
  },
  "verify-on-screen": {
   "title": "Verify system actions on screen",
   "summary": "An API success is not the user-visible outcome (an app can crash on start); the orchestrator often sends vision to confirm.",
   "source": "05-the-actuator §Design choices and trade-offs; Common confusions"
  }
 },
 "questions": [
  {
   "id": "q1",
   "type": "mcq",
   "kp": "actuator-role",
   "prompt": "Which task fits the actuator rather than the vision specialist?",
   "choices": [
    "Open a specific settings page",
    "Type a search title inside a video app",
    "Tap a thumbnail in a list",
    "Scroll through a results page"
   ],
   "answer": 0,
   "explanation": "A settings intent is a direct OS route; the other three happen inside an app's UI.",
   "source": "05-the-actuator §What it is"
  },
  {
   "id": "q2",
   "type": "mcq",
   "kp": "actuator-role",
   "prompt": "On an Android-type device, `go_home()` is implemented by…",
   "choices": [
    "`performGlobalAction` with the home action",
    "An explicit launch intent",
    "Tapping the home icon via `dispatchGesture`",
    "A shell command"
   ],
   "answer": 0,
   "explanation": "Home and back are accessibility-service global actions.",
   "source": "05-the-actuator §What it is"
  },
  {
   "id": "q3",
   "type": "tf",
   "kp": "actuator-role",
   "prompt": "The actuator usually needs only a short inner loop: one or two tool calls, then a summary.",
   "answer": true,
   "explanation": "System actions are direct, so few iterations are needed.",
   "source": "05-the-actuator §How it works"
  },
  {
   "id": "q4",
   "type": "mcq",
   "kp": "function-calling",
   "prompt": "What defines a **function-calling tool**?",
   "choices": [
    "A name, a description and a typed input schema",
    "A pixel coordinate and an action",
    "A screenshot and a prompt",
    "A message ID and a session ID"
   ],
   "answer": 0,
   "explanation": "The model returns a call naming the tool and filling the inputs.",
   "source": "05-the-actuator §What it is"
  },
  {
   "id": "q5",
   "type": "tf",
   "kp": "function-calling",
   "prompt": "Function calling and the computer-use tool are different protocols.",
   "answer": false,
   "explanation": "Both are tool calls in the same protocol; the computer-use tool's schema is vendor-defined, actuator schemas are your own.",
   "source": "05-the-actuator §Common confusions"
  },
  {
   "id": "q6",
   "type": "mcq",
   "kp": "function-calling",
   "prompt": "What did Toolformer (Schick et al. 2023) show, as the note uses it?",
   "choices": [
    "A language model can learn when to call an external tool and what to pass",
    "Tools must be called through the screen",
    "Function calling removes prompt injection",
    "Tool calls are cheaper than text replies"
   ],
   "answer": 0,
   "explanation": "Vendor function-calling APIs turn the same idea into a request format.",
   "source": "05-the-actuator §What it is"
  },
  {
   "id": "q7",
   "type": "numeric",
   "kp": "why-bypass",
   "prompt": "Opening the video app through the screen takes an illustrative 2 model calls and ~10 s; through the OS, 1 call and ~2 s. How many times faster is the OS route?",
   "answer": 5,
   "unit": "×",
   "tolerance": 0.1,
   "explanation": "My arithmetic: 10 ÷ 2; the gain comes mostly from removing model calls.",
   "source": "05-the-actuator §Design choices and trade-offs; constants.json actuator_vs_screen_illustrative"
  },
  {
   "id": "q8",
   "type": "multi",
   "kp": "why-bypass",
   "prompt": "Which are advantages of the OS route over the screen route? Select all that apply.",
   "choices": [
    "Fewer model calls",
    "No grounding error is possible",
    "Works when the target is off-screen or in a folder",
    "Verifies the user-visible outcome by itself"
   ],
   "answer": [
    0,
    1,
    2
   ],
   "explanation": "An API result is not the user-visible outcome; verification still needs the screen.",
   "source": "05-the-actuator §Design choices and trade-offs"
  },
  {
   "id": "q9",
   "type": "tf",
   "kp": "why-bypass",
   "prompt": "The orchestrator's prompt says to prefer the actuator when it can do the job.",
   "answer": true,
   "explanation": "The cheapest model call is the one you do not make.",
   "source": "05-the-actuator §Design choices and trade-offs; Why it matters"
  },
  {
   "id": "q10",
   "type": "mcq",
   "kp": "why-keep-vision",
   "prompt": "Why keep the vision specialist if the actuator is cheaper?",
   "choices": [
    "System interfaces do not reach inside apps, e.g. searching for a title",
    "The actuator cannot launch apps",
    "Vision is cheaper per call",
    "The allow-list forbids actuator use"
   ],
   "answer": 0,
   "explanation": "The two specialists are complementary.",
   "source": "05-the-actuator §Design choices and trade-offs"
  },
  {
   "id": "q11",
   "type": "tf",
   "kp": "why-keep-vision",
   "prompt": "Searching for a title inside a video app has a direct OS call.",
   "answer": false,
   "explanation": "It has no OS call; it needs the screen.",
   "source": "05-the-actuator §Design choices and trade-offs"
  },
  {
   "id": "q12",
   "type": "mcq",
   "kp": "narrow-tools",
   "prompt": "Why is a generic \"run this command\" actuator tool a bad idea?",
   "choices": [
    "It removes every guard; any manipulated output could run anything",
    "It is slower than an intent",
    "It cannot be logged",
    "The model cannot fill its schema"
   ],
   "answer": 0,
   "explanation": "A safe actuator exposes named, typed operations only.",
   "source": "05-the-actuator §Common confusions"
  },
  {
   "id": "q13",
   "type": "tf",
   "kp": "narrow-tools",
   "prompt": "Device code checks each actuator call against an allow-list before running it.",
   "answer": true,
   "explanation": "The model proposes; device code decides what may run (see 08).",
   "source": "05-the-actuator §How it works"
  },
  {
   "id": "q14",
   "type": "mcq",
   "kp": "verify-on-screen",
   "prompt": "`launch_app` returns success but the app crashed on start. What design handles this?",
   "choices": [
    "The orchestrator sends the vision specialist to confirm the screen",
    "Trust the API result and FINISH",
    "Raise the actuator's token budget",
    "Retry with a new message ID"
   ],
   "answer": 0,
   "explanation": "System actions return an API result, not the visible outcome; confirm on screen when it matters.",
   "source": "05-the-actuator §Design choices and trade-offs"
  },
  {
   "id": "q15",
   "type": "tf",
   "kp": "verify-on-screen",
   "prompt": "System actions do not need checking because they return a structured result.",
   "answer": false,
   "explanation": "The structured result is not the user-visible outcome.",
   "source": "05-the-actuator §Common confusions"
  }
 ]
});
