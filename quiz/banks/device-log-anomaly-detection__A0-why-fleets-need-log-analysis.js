// Generated from learning/device-log-anomaly-detection/notes/A0-why-fleets-need-log-analysis.md; numbers loaded from constants.json.
window.QUIZ_BANKS = window.QUIZ_BANKS || [];
window.QUIZ_BANKS.push({
 "topic": "device-log-anomaly-detection",
 "topicTitle": "Finding faults in a device fleet from logs and metrics",
 "section": "A0-why-fleets-need-log-analysis",
 "sectionTitle": "A0 — Why a device fleet needs log and metric analysis",
 "notePath": "../device-log-anomaly-detection/notes/A0-why-fleets-need-log-analysis.md",
 "knowledgePoints": {
  "three-problems": {
   "title": "Support cost, lost evidence, reactive rules",
   "summary": "Faults are found late and with little evidence: support has no device data, ring buffers overwrite before on-demand tools run, and rule-based tools find only foreseen faults.",
   "source": "A0-why-fleets-need-log-analysis §How it works"
  },
  "metrics-choose-logs": {
   "title": "Metrics say that, logs say what",
   "summary": "Metrics show that something changed; logs show what happened, in order; the pipeline uses metrics to choose which logs to read.",
   "source": "A0-why-fleets-need-log-analysis §What it is; Common confusions"
  },
  "four-stages": {
   "title": "The four-stage pipeline",
   "summary": "Detect a metric change, fetch and parse the affected devices' logs, find anomalous windows and their events, then group and report.",
   "source": "A0-why-fleets-need-log-analysis §How it works"
  },
  "on-device-vs-fleet": {
   "title": "On-device versus fleet-side analysis",
   "summary": "On-device analysis sees every line before overwrite but has tiny resources; fleet-side has compute and many devices but sees only uploaded logs; they are complementary.",
   "source": "A0-why-fleets-need-log-analysis §How it works"
  },
  "three-judgements": {
   "title": "Judged by detection, false alarms, and engineer time",
   "summary": "A pipeline is judged by detection rate, false-alarm rate, and whether it shortens an investigation.",
   "source": "A0-why-fleets-need-log-analysis §How it is measured or used"
  },
  "anomaly-not-bug": {
   "title": "Anomaly is not a bug; rules and models are partners",
   "summary": "Anomaly detection finds behaviour that differs from normal, some of it environmental; rules catch known faults and unsupervised models unknown ones.",
   "source": "A0-why-fleets-need-log-analysis §Common confusions"
  }
 },
 "questions": [
  {
   "id": "q1",
   "type": "mcq",
   "kp": "three-problems",
   "prompt": "Why does an on-demand diagnostic tool often find no trace of the fault it is asked about?",
   "choices": [
    "It cannot reach the network during a fault",
    "The ring buffer has overwritten the lines by the time it runs",
    "Metrics are aggregated only once per day",
    "Its templates do not cover error paths"
   ],
   "answer": 1,
   "explanation": "On-demand tools run after the fault is reported; a small buffer that overwrites old lines has usually lost the evidence by then.",
   "source": "A0-why-fleets-need-log-analysis §How it works"
  },
  {
   "id": "q2",
   "type": "mcq",
   "kp": "three-problems",
   "prompt": "Which fault can a typical rule-based diagnostic tool **not** find?",
   "choices": [
    "A weak signal-strength reading",
    "A failed ping test",
    "A fault that nobody wrote a rule for",
    "A failed HTTP test"
   ],
   "answer": 2,
   "explanation": "Rule-based tools apply a short decision tree to known checks; a fault outside the rules is invisible to them.",
   "source": "A0-why-fleets-need-log-analysis §How it works"
  },
  {
   "id": "q3",
   "type": "tf",
   "kp": "three-problems",
   "prompt": "A support agent handling an unresolved call usually has rich device evidence to pass to engineers.",
   "answer": false,
   "explanation": "The customer can rarely describe more than \"it cannot connect\", and the agent has no device evidence; engineers start from nothing.",
   "source": "A0-why-fleets-need-log-analysis §How it works"
  },
  {
   "id": "q4",
   "type": "mcq",
   "kp": "metrics-choose-logs",
   "prompt": "In the pipeline, what is the main role of fleet metrics?",
   "choices": [
    "They replace logs once enough devices report",
    "They trigger and choose which devices' logs to read",
    "They provide the ordered event sequence",
    "They label faults for a supervised model"
   ],
   "answer": 1,
   "explanation": "Metrics are cheap and cover every device but only say *that* something changed; they pick which logs to read for *what* happened.",
   "source": "A0-why-fleets-need-log-analysis §What it is; Common confusions"
  },
  {
   "id": "q5",
   "type": "tf",
   "kp": "metrics-choose-logs",
   "prompt": "Metrics are enough to explain a fault, because they record every event the device emits.",
   "answer": false,
   "explanation": "Metrics are small structured records of defined events; the ordered detail of what happened lives in the logs.",
   "source": "A0-why-fleets-need-log-analysis §Common confusions"
  },
  {
   "id": "q6",
   "type": "mcq",
   "kp": "four-stages",
   "prompt": "Which stage comes **first** in the four-stage pipeline?",
   "choices": [
    "Group and report similar anomalies",
    "Find anomalous log windows",
    "Detect a change in fleet or device metrics",
    "Fetch and parse device logs"
   ],
   "answer": 2,
   "explanation": "Detection on metrics comes first; it decides which devices' logs are fetched, parsed, and examined.",
   "source": "A0-why-fleets-need-log-analysis §How it works"
  },
  {
   "id": "q7",
   "type": "multi",
   "kp": "four-stages",
   "prompt": "Select the stages of the pipeline described in the note.",
   "choices": [
    "Detect a change in metrics",
    "Fetch and parse the logs of the driving devices",
    "Train a supervised classifier on labelled faults",
    "Find anomalous windows and the events behind them",
    "Group similar anomalies into one ticket with evidence",
    "Push a fix to the affected devices automatically"
   ],
   "answer": [
    0,
    1,
    3,
    4
   ],
   "explanation": "Detect, fetch and parse, find anomalous windows, group and report. There are no labels for a classifier, and the pipeline reports; it does not fix.",
   "source": "A0-why-fleets-need-log-analysis §How it works"
  },
  {
   "id": "q8",
   "type": "mcq",
   "kp": "on-device-vs-fleet",
   "prompt": "Which is an advantage of **on-device** analysis over fleet-side analysis?",
   "choices": [
    "Ample compute for large models",
    "It can compare many devices directly",
    "It sees every log line before the buffer overwrites it",
    "It has no memory or power constraints"
   ],
   "answer": 2,
   "explanation": "Running on the device reads lines before they are lost, works offline, and keeps raw logs local; the price is very little memory and power.",
   "source": "A0-why-fleets-need-log-analysis §How it works"
  },
  {
   "id": "q9",
   "type": "mcq",
   "kp": "on-device-vs-fleet",
   "prompt": "What is the key limitation of **fleet-side** analysis?",
   "choices": [
    "It cannot run statistical tests",
    "It sees only devices whose logs were collected, for the ranges kept",
    "It drains the device battery",
    "It cannot compare devices with each other"
   ],
   "answer": 1,
   "explanation": "Fleet-side analysis runs in the cloud on uploaded logs, so devices and time ranges that were never uploaded or kept are invisible.",
   "source": "A0-why-fleets-need-log-analysis §How it works"
  },
  {
   "id": "q10",
   "type": "tf",
   "kp": "on-device-vs-fleet",
   "prompt": "The note treats a fleet-side service as the practical first step and an on-device agent as the answer to lost evidence.",
   "answer": true,
   "explanation": "The two are complementary: the cloud service is easier to build first; on-device analysis reads the lines before they are overwritten.",
   "source": "A0-why-fleets-need-log-analysis §How it works"
  },
  {
   "id": "q11",
   "type": "multi",
   "kp": "three-judgements",
   "prompt": "Which questions does the note use to judge a pipeline like this?",
   "choices": [
    "Detection rate on real faults",
    "Number of templates in the parser",
    "False-alarm rate among the flags",
    "Whether it shortens an engineer's investigation",
    "Size of the anomaly model in memory"
   ],
   "answer": [
    0,
    2,
    3
   ],
   "explanation": "Detection rate, false-alarm rate, and engineer time; template counts and model size are means, not outcomes.",
   "source": "A0-why-fleets-need-log-analysis §How it is measured or used"
  },
  {
   "id": "q12",
   "type": "numeric",
   "kp": "three-judgements",
   "prompt": "Investigation time falls from an illustrative 90 min to 15 min per case. By what percentage is the time per case reduced?",
   "answer": 83.3,
   "unit": "%",
   "tolerance": 1,
   "explanation": "(90 − 15) ÷ 90 ≈ 83.3 %. The values are illustrative; the relation that decides adoption is engineer time saved.",
   "source": "A0-why-fleets-need-log-analysis §How it is measured or used"
  },
  {
   "id": "q13",
   "type": "mcq",
   "kp": "three-judgements",
   "prompt": "Why is detection rate alone not enough to judge the pipeline?",
   "choices": [
    "It needs no ground truth",
    "It ignores how many flags are not device faults",
    "It is always 100 %",
    "It measures engineer time only"
   ],
   "answer": 1,
   "explanation": "Many flags are environmental (a bad router, an outage). Without the false-alarm rate a high detection rate says little.",
   "source": "A0-why-fleets-need-log-analysis §How it is measured or used"
  },
  {
   "id": "q14",
   "type": "tf",
   "kp": "three-judgements",
   "prompt": "Measuring the detection rate requires ground truth, which is scarce for a device fleet.",
   "answer": true,
   "explanation": "You need cases where the true fault is known to compute the fraction caught; such cases are rare (see C1).",
   "source": "A0-why-fleets-need-log-analysis §How it is measured or used"
  },
  {
   "id": "q15",
   "type": "mcq",
   "kp": "anomaly-not-bug",
   "prompt": "The pipeline flags a healthy device whose home router keeps dropping clients. What kind of anomaly is this?",
   "choices": [
    "A data artefact",
    "A device defect",
    "An environmental anomaly",
    "A parsing error"
   ],
   "answer": 2,
   "explanation": "An environmental anomaly comes from the device's surroundings (router, provider, setup), not from a defect in the device.",
   "source": "A0-why-fleets-need-log-analysis §Common confusions"
  },
  {
   "id": "q16",
   "type": "tf",
   "kp": "anomaly-not-bug",
   "prompt": "Rules and machine learning compete, so a mature pipeline should pick one of them.",
   "answer": false,
   "explanation": "Rules are precise for known faults; unsupervised models find unknown ones. A mature pipeline uses both.",
   "source": "A0-why-fleets-need-log-analysis §Common confusions"
  }
 ]
});
