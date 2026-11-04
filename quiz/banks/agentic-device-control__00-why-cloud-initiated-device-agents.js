// Generated from learning/agentic-device-control/notes/00-why-cloud-initiated-device-agents.md; numbers loaded from constants.json.
window.QUIZ_BANKS = window.QUIZ_BANKS || [];
window.QUIZ_BANKS.push({
 "topic": "agentic-device-control",
 "topicTitle": "Agentic control of a consumer device",
 "section": "00-why-cloud-initiated-device-agents",
 "sectionTitle": "00 — Why cloud-initiated device agents",
 "notePath": "../agentic-device-control/notes/00-why-cloud-initiated-device-agents.md",
 "knowledgePoints": {
  "cida-definition": {
   "title": "What a cloud-initiated device agent is",
   "summary": "A server sends a plain-language task; the device completes it by looking at its own screen and acting, with no person and no cable.",
   "source": "00-why-cloud-initiated-device-agents §In one sentence; What it is"
  },
  "model-in-cloud": {
   "title": "The model runs in the cloud",
   "summary": "The device captures screenshots, sends them to a large multimodal model in the cloud, and executes the returned actions.",
   "source": "00-why-cloud-initiated-device-agents §What it is; Common confusions"
  },
  "use-cases": {
   "title": "Three use cases",
   "summary": "Automated testing, remote support, and fleet automation drive the design.",
   "source": "00-why-cloud-initiated-device-agents §How it works"
  },
  "agentic-vs-script": {
   "title": "Agentic versus scripted automation",
   "summary": "A script is a fixed command sequence naming each element; an agent loops look-decide-act-look and gains robustness to UI change, natural-language tasks and recovery.",
   "source": "00-why-cloud-initiated-device-agents §How it works; Design choices and trade-offs"
  },
  "agent-costs": {
   "title": "What the agent pays",
   "summary": "Latency (illustrative ~20 s per simple task), money (illustrative ~30 000 tokens) and non-determinism; a stable high-volume journey is often cheaper as a script.",
   "source": "00-why-cloud-initiated-device-agents §Design choices and trade-offs; Common confusions"
  },
  "cloud-not-cable": {
   "title": "Why cloud-initiated, not cable-initiated",
   "summary": "A cable needs a host computer next to each device; a cloud message reaches the whole fleet, but the device must capture, inject input and hold credentials itself.",
   "source": "00-why-cloud-initiated-device-agents §Design choices and trade-offs"
  }
 },
 "questions": [
  {
   "id": "q1",
   "type": "mcq",
   "kp": "cida-definition",
   "prompt": "Which description best fits a **cloud-initiated device agent**?",
   "choices": [
    "A server sends a natural-language task; software on the device completes it by acting on the device",
    "A server streams raw tap coordinates to the device over a cable",
    "A person operates the device remotely through a screen-sharing session",
    "A fixed test script is downloaded and replayed on the device"
   ],
   "answer": 0,
   "explanation": "The server sends only a task; the agent on the device decides and performs every action, with no person and no cable.",
   "source": "00-why-cloud-initiated-device-agents §In one sentence"
  },
  {
   "id": "q2",
   "type": "tf",
   "kp": "cida-definition",
   "prompt": "In this design the cloud sends individual tap commands and the device simply replays them.",
   "answer": false,
   "explanation": "The cloud sends only a task. All actions are decided by the agent loop and executed by the device's own input services.",
   "source": "00-why-cloud-initiated-device-agents §Common confusions"
  },
  {
   "id": "q3",
   "type": "mcq",
   "kp": "model-in-cloud",
   "prompt": "Where does the large multimodal model run in this kit's design?",
   "choices": [
    "In the cloud; the device sends screenshots and executes returned actions",
    "On the device's own processor",
    "On a host computer attached by debug cable",
    "Split evenly between device and cloud"
   ],
   "answer": 0,
   "explanation": "The device captures and acts; the decisions come from a model call in the cloud.",
   "source": "00-why-cloud-initiated-device-agents §Common confusions"
  },
  {
   "id": "q4",
   "type": "tf",
   "kp": "model-in-cloud",
   "prompt": "A **large multimodal model** accepts text and images and returns text or tool calls.",
   "answer": true,
   "explanation": "That is the glossary definition; it is why the model can read screenshots and reply with actions.",
   "source": "00-why-cloud-initiated-device-agents §Terms introduced"
  },
  {
   "id": "q5",
   "type": "multi",
   "kp": "use-cases",
   "prompt": "Which are among the three use cases that drive the design? Select all that apply.",
   "choices": [
    "Automated testing of user journeys",
    "Remote support on the user's behalf",
    "Fleet automation of a chore on many devices",
    "On-device model training"
   ],
   "answer": [
    0,
    1,
    2
   ],
   "explanation": "The note names testing, remote support and fleet automation. On-device training is not part of the design; the model runs in the cloud.",
   "source": "00-why-cloud-initiated-device-agents §How it works"
  },
  {
   "id": "q6",
   "type": "mcq",
   "kp": "use-cases",
   "prompt": "A fleet operator wants every device in a known state before an experiment. Which use case is that?",
   "choices": [
    "Fleet automation",
    "Remote support",
    "Automated testing",
    "Scripted cable control"
   ],
   "answer": 0,
   "explanation": "Putting many devices into a known state is the note's fleet-automation example.",
   "source": "00-why-cloud-initiated-device-agents §How it works"
  },
  {
   "id": "q7",
   "type": "mcq",
   "kp": "agentic-vs-script",
   "prompt": "A dialog unexpectedly appears mid-journey. Why does an agent cope better than a script?",
   "choices": [
    "It sees the new screen and adapts its next action",
    "It runs faster than a script",
    "It names elements by identifier in advance",
    "It never makes a wrong click"
   ],
   "answer": 0,
   "explanation": "Robustness to UI change comes from the observe-decide loop: the agent looks again after every action.",
   "source": "00-why-cloud-initiated-device-agents §Design choices and trade-offs"
  },
  {
   "id": "q8",
   "type": "multi",
   "kp": "agentic-vs-script",
   "prompt": "What does \"agentic\" add over a scripted automation, per the note? Select all that apply.",
   "choices": [
    "Robustness to UI change",
    "Natural-language tasks",
    "Recovery from a wrong result",
    "Lower latency per task"
   ],
   "answer": [
    0,
    1,
    2
   ],
   "explanation": "Those three are the gains. Latency is a cost of the agent, not a gain.",
   "source": "00-why-cloud-initiated-device-agents §Design choices and trade-offs"
  },
  {
   "id": "q9",
   "type": "tf",
   "kp": "agentic-vs-script",
   "prompt": "**Scripted automation** names each UI element by identifier or screen position in advance.",
   "answer": true,
   "explanation": "That fixed naming is exactly why a script breaks when a button moves.",
   "source": "00-why-cloud-initiated-device-agents §How it works"
  },
  {
   "id": "q10",
   "type": "numeric",
   "kp": "agent-costs",
   "prompt": "The note's illustrative simple task takes about how many seconds end to end (illustrative)?",
   "answer": 20,
   "unit": "s",
   "tolerance": 2,
   "explanation": "An illustrative ~20 s, against well under a second for a script; each decision is a network model call.",
   "source": "00-why-cloud-initiated-device-agents §Design choices and trade-offs; constants.json task_wall_time_illustrative"
  },
  {
   "id": "q11",
   "type": "mcq",
   "kp": "agent-costs",
   "prompt": "A stable journey runs thousands of times a day and its UI rarely changes. What does the note suggest?",
   "choices": [
    "A script is often cheaper",
    "The agent is always the better choice",
    "Use the strong model tier everywhere",
    "Run it once and trust the result"
   ],
   "answer": 0,
   "explanation": "An agent buys robustness with latency, cost and variance; a stable, high-volume journey does not need that robustness.",
   "source": "00-why-cloud-initiated-device-agents §Common confusions"
  },
  {
   "id": "q12",
   "type": "tf",
   "kp": "agent-costs",
   "prompt": "Because the agent is non-deterministic, evaluation must count success over many runs.",
   "answer": true,
   "explanation": "The same task can take a different path on two runs, so one run says little (see 09).",
   "source": "00-why-cloud-initiated-device-agents §Design choices and trade-offs"
  },
  {
   "id": "q13",
   "type": "numeric",
   "kp": "agent-costs",
   "prompt": "About how many tokens does the illustrative simple task consume (illustrative)?",
   "answer": 30000,
   "unit": "tokens",
   "tolerance": 2000,
   "explanation": "An illustrative ~30 000 tokens; every model call re-sends prompt, history and screenshots.",
   "source": "00-why-cloud-initiated-device-agents §Design choices and trade-offs; constants.json task_input_tokens_illustrative"
  },
  {
   "id": "q14",
   "type": "mcq",
   "kp": "cloud-not-cable",
   "prompt": "What is the main advantage of cloud-initiated over cable-initiated control?",
   "choices": [
    "One message reaches every device in a fleet, with no host computer per device",
    "It removes the need for screen capture",
    "It makes the agent deterministic",
    "It lets the model run on the device"
   ],
   "answer": 0,
   "explanation": "A cable needs a host computer beside each device; a cloud message scales to the fleet.",
   "source": "00-why-cloud-initiated-device-agents §Design choices and trade-offs"
  },
  {
   "id": "q15",
   "type": "multi",
   "kp": "cloud-not-cable",
   "prompt": "Without a cable host, what must the device now do on its own? Select all that apply.",
   "choices": [
    "Capture the screen",
    "Inject input",
    "Keep credentials",
    "Train the model"
   ],
   "answer": [
    0,
    1,
    2
   ],
   "explanation": "The note lists capture, input injection and credentials as the cost of dropping the host computer.",
   "source": "00-why-cloud-initiated-device-agents §Design choices and trade-offs"
  }
 ]
});
