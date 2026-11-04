// Generated from learning/device-log-anomaly-detection/notes/C4-lessons.md; numbers loaded from constants.json.
window.QUIZ_BANKS = window.QUIZ_BANKS || [];
window.QUIZ_BANKS.push({
 "topic": "device-log-anomaly-detection",
 "topicTitle": "Finding faults in a device fleet from logs and metrics",
 "section": "C4-lessons",
 "sectionTitle": "C4 — Lessons: anomaly is not issue, and what the misses teach",
 "notePath": "../device-log-anomaly-detection/notes/C4-lessons.md",
 "knowledgePoints": {
  "confidence-gap": {
   "title": "Anomaly is not issue",
   "summary": "Customer environments (deprecated security modes, overloaded access points, outages) make healthy devices look anomalous; confirm with an independent second signal before opening a ticket.",
   "source": "C4-lessons §How it works; Common confusions"
  },
  "human-localisation": {
   "title": "Fault localisation needs a human",
   "summary": "The detector's value is the reduction (a day of logs to a few windows); deciding what they mean needs domain expertise, so design a focused report, not a verdict.",
   "source": "C4-lessons §How it works; Common confusions"
  },
  "scope-too-narrow": {
   "title": "The cause sits outside the monitored scope",
   "summary": "Missed cases traced to DHCP, time sync, the kernel buffer, a log cut by a crash, or stateful order; connectivity problems often live in layers that depend on Wi-Fi.",
   "source": "C4-lessons §How it works"
  },
  "know-your-logs": {
   "title": "Know which logs you have; collection limits",
   "summary": "Scope the analyser explicitly, say so in the output, and fall back gracefully; on-demand upload and overwriting buffers argue for on-device analysis.",
   "source": "C4-lessons §How it works"
  },
  "hybrid": {
   "title": "Rules and models as partners",
   "summary": "A hybrid analyser extracts known signals by rule and feeds them to the model as extra features beside the count vectors; more well-templated components means fewer misses.",
   "source": "C4-lessons §How it works; Common confusions"
  },
  "release-and-clarity": {
   "title": "Release-health checks and understandable output",
   "summary": "Comparing each release with earlier ones turns \"no anomaly\" into a green flag; show the evidence next to the score and remove unused fields.",
   "source": "C4-lessons §How it works"
  },
  "miss-log": {
   "title": "Miss log and environmental share",
   "summary": "Record each missed ground-truth case with its missing signal and fix; track the environmental share of resolved tickets, which should fall as confirmation improves.",
   "source": "C4-lessons §How it is measured or used"
  }
 },
 "questions": [
  {
   "id": "q1",
   "type": "mcq",
   "kp": "confidence-gap",
   "prompt": "A healthy device near an old router that still uses TKIP produces anomalous logs. What is this?",
   "choices": [
    "A device defect",
    "An environmental anomaly",
    "A data artefact",
    "A parsing error"
   ],
   "answer": 1,
   "explanation": "TKIP was deprecated in IEEE 802.11-2012; the router, not the device, is unusual.",
   "source": "C4-lessons §How it works"
  },
  {
   "id": "q2",
   "type": "mcq",
   "kp": "confidence-gap",
   "prompt": "What rule does the note give before opening a ticket on a log anomaly?",
   "choices": [
    "Wait for three days",
    "Confirm with an independent second signal, such as a metric anomaly or similar devices on other access points",
    "Raise the contamination",
    "Ask the customer"
   ],
   "answer": 1,
   "explanation": "Second-signal confirmation closes part of the confidence gap.",
   "source": "C4-lessons §How it works"
  },
  {
   "id": "q3",
   "type": "numeric",
   "kp": "confidence-gap",
   "prompt": "In an illustrative pilot of 10 tickets, 4 were environmental. What percentage was environmental?",
   "answer": 40,
   "unit": "%",
   "tolerance": 1,
   "explanation": "4 ÷ 10 = 40 %; illustrative counts.",
   "source": "C4-lessons §How it works"
  },
  {
   "id": "q4",
   "type": "tf",
   "kp": "confidence-gap",
   "prompt": "A high false-alarm count means the model is bad.",
   "answer": false,
   "explanation": "It often means a missing second signal or a data artefact (C3).",
   "source": "C4-lessons §Common confusions"
  },
  {
   "id": "q5",
   "type": "numeric",
   "kp": "human-localisation",
   "prompt": "A detector reduces a day of logs to an illustrative 20 flagged windows out of 50,000. What percentage of windows is flagged?",
   "answer": 0.04,
   "unit": "%",
   "tolerance": 0.005,
   "explanation": "20 ÷ 50,000 = 0.04 %: a large reduction, but the windows still need an expert.",
   "source": "C4-lessons §How it works"
  },
  {
   "id": "q6",
   "type": "tf",
   "kp": "human-localisation",
   "prompt": "Automation removes the engineer from fault localisation.",
   "answer": false,
   "explanation": "It removes the search, not the judgement.",
   "source": "C4-lessons §Common confusions"
  },
  {
   "id": "q7",
   "type": "mcq",
   "kp": "scope-too-narrow",
   "prompt": "Repeated Wi-Fi disconnects turned out to be caused by the DHCP client rejecting packets. What did the pipeline need?",
   "choices": [
    "More Wi-Fi templates",
    "DHCP client logs",
    "A longer window",
    "A lower threshold"
   ],
   "answer": 1,
   "explanation": "The cause sat outside the monitored components.",
   "source": "C4-lessons §How it works"
  },
  {
   "id": "q8",
   "type": "mcq",
   "kp": "scope-too-narrow",
   "prompt": "A device reboots during a connection because of a Wi-Fi kernel-driver assertion. What did the pipeline need?",
   "choices": [
    "The kernel log buffer, processed separately from the main buffer",
    "Time-sync logs",
    "More metrics",
    "A sequence model"
   ],
   "answer": 0,
   "explanation": "Driver faults write to the kernel buffer (A1).",
   "source": "C4-lessons §How it works"
  },
  {
   "id": "q9",
   "type": "mcq",
   "kp": "scope-too-narrow",
   "prompt": "A failure happens only after a specific earlier test step. What does detection need?",
   "choices": [
    "Count vectors over longer windows",
    "Sequence or transition features",
    "More devices",
    "A gap detector"
   ],
   "answer": 1,
   "explanation": "It is a stateful, order-dependent fault; counts lose order (B2, B5).",
   "source": "C4-lessons §How it works"
  },
  {
   "id": "q10",
   "type": "multi",
   "kp": "scope-too-narrow",
   "prompt": "\"Connectivity\" problems often live in layers that depend on Wi-Fi. Which layers does the note name?",
   "choices": [
    "Addressing",
    "Time",
    "Name resolution",
    "Security",
    "Display rendering"
   ],
   "answer": [
    0,
    1,
    2,
    3
   ],
   "explanation": "DHCP, time sync, and TLS failures all looked like Wi-Fi problems in the lab cases.",
   "source": "C4-lessons §How it works"
  },
  {
   "id": "q11",
   "type": "tf",
   "kp": "scope-too-narrow",
   "prompt": "\"Connectivity\" problems are almost always Wi-Fi problems.",
   "answer": false,
   "explanation": "They often live in layers that depend on Wi-Fi: addressing, time, name resolution, security.",
   "source": "C4-lessons §How it works"
  },
  {
   "id": "q12",
   "type": "mcq",
   "kp": "know-your-logs",
   "prompt": "Some lab logs are in a test-framework format or lack a whole component. What is the rule?",
   "choices": [
    "Reject those logs",
    "Scope the analyser explicitly, say so in the output, and fall back gracefully",
    "Convert every format automatically",
    "Train one model per format"
   ],
   "answer": 1,
   "explanation": "Lesson 4: know which logs you have.",
   "source": "C4-lessons §How it works"
  },
  {
   "id": "q13",
   "type": "mcq",
   "kp": "know-your-logs",
   "prompt": "Central storage covers only devices allowed to upload, uploads come after the fault, and buffers overwrite. What does this argue for?",
   "choices": [
    "Longer retention only",
    "On-device analysis that reads lines before they are lost",
    "Fewer components",
    "Supervised models"
   ],
   "answer": 1,
   "explanation": "Lesson 5 links back to A0.",
   "source": "C4-lessons §How it works"
  },
  {
   "id": "q14",
   "type": "mcq",
   "kp": "hybrid",
   "prompt": "What is a hybrid analyser?",
   "choices": [
    "Two isolation forests",
    "A model that also takes rule-extracted known signals (ping result, reason codes) as features",
    "A rule set with a model fallback",
    "An LSTM plus a clustering step"
   ],
   "answer": 1,
   "explanation": "Rules give precision and a named cause; models find unknown faults.",
   "source": "C4-lessons §How it works"
  },
  {
   "id": "q15",
   "type": "tf",
   "kp": "hybrid",
   "prompt": "Adding more components to the analyser mainly adds noise.",
   "answer": false,
   "explanation": "More components with good templates means fewer misses; filter by component per question, not globally.",
   "source": "C4-lessons §Common confusions"
  },
  {
   "id": "q16",
   "type": "mcq",
   "kp": "release-and-clarity",
   "prompt": "What is a release-health check?",
   "choices": [
    "A code review before release",
    "Comparing a new release's fleet behaviour with earlier releases; consistency is a green flag",
    "Counting crash tickets",
    "A lab stress test"
   ],
   "answer": 1,
   "explanation": "\"No anomaly\" becomes information.",
   "source": "C4-lessons §How it works"
  },
  {
   "id": "q17",
   "type": "mcq",
   "kp": "release-and-clarity",
   "prompt": "Users relied on the anomaly score without understanding it. What does Lesson 8 prescribe?",
   "choices": [
    "Hide the score",
    "Show the evidence (lines, templates, trend) next to the score and remove unused fields",
    "Add more statistical plots",
    "Train users on statistics"
   ],
   "answer": 1,
   "explanation": "A correct output that nobody understands has no value.",
   "source": "C4-lessons §How it works"
  },
  {
   "id": "q18",
   "type": "mcq",
   "kp": "miss-log",
   "prompt": "What does each entry in a miss log record?",
   "choices": [
    "A false alarm and its ticket",
    "A missed ground-truth case, its missing signal, and the planned fix",
    "A template change",
    "A data-quality finding"
   ],
   "answer": 1,
   "explanation": "The miss list is the roadmap.",
   "source": "C4-lessons §How it is measured or used"
  },
  {
   "id": "q19",
   "type": "tf",
   "kp": "miss-log",
   "prompt": "The environmental share of resolved tickets should fall over time as second-signal confirmation improves.",
   "answer": true,
   "explanation": "It is tracked as a measure of the confidence gap.",
   "source": "C4-lessons §How it is measured or used"
  }
 ]
});
