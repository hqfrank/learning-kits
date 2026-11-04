// Generated from learning/device-log-anomaly-detection/notes/C5-from-service-to-tool.md; numbers loaded from constants.json.
window.QUIZ_BANKS = window.QUIZ_BANKS || [];
window.QUIZ_BANKS.push({
 "topic": "device-log-anomaly-detection",
 "topicTitle": "Finding faults in a device fleet from logs and metrics",
 "section": "C5-from-service-to-tool",
 "sectionTitle": "C5 — From service to tool: what changes when the pipeline becomes a stand-alone analyzer",
 "notePath": "../device-log-anomaly-detection/notes/C5-from-service-to-tool.md",
 "knowledgePoints": {
  "why-tool": {
   "title": "Why the service was not enough",
   "summary": "Users wanted to use the pipeline without a metric trigger and wanted interactive, explainable output; the models stay the same, input, presentation, and access change.",
   "source": "C5-from-service-to-tool §How it works; Common confusions"
  },
  "workflow-metrics": {
   "title": "The manual workflow and the success metrics",
   "summary": "Manual analysis (download, unzip, grep, check against source) took an illustrative 90 min per case; the tool tracks weekly requests, self-reported time saving (the north-star), and weekly utility.",
   "source": "C5-from-service-to-tool §How it works; How it is measured or used"
  },
  "four-views": {
   "title": "Four linked views",
   "summary": "Log output (template scatter, anomaly overlay, parameter plot), log search (structured filters), state machine (ordered pattern search), and metrics (series, software-version timeline, family comparison).",
   "source": "C5-from-service-to-tool §How it works"
  },
  "local-and-v1": {
   "title": "Local parsing and a small first version",
   "summary": "Uploaded files are parsed locally with the same tree; detection covers only templated components while search and state machine cover all; v1 was one device, one OS family, main buffer, two Wi-Fi components.",
   "source": "C5-from-service-to-tool §How it works"
  },
  "transparency": {
   "title": "Transparent, not a black box",
   "summary": "Show intermediate layers so each engineer chooses how much automation to trust; one back end serves a UI and an API.",
   "source": "C5-from-service-to-tool §How it works; Common confusions"
  },
  "privacy-access": {
   "title": "Privacy and access by design",
   "summary": "The device ID is an input, never an output; results go only to the requester; only already-uploaded logs, for users with access to both groups; logs stay in the cloud.",
   "source": "C5-from-service-to-tool §How it works; Common confusions"
  },
  "survey-changes": {
   "title": "What the survey changed",
   "summary": "Unreadable probability-mass plots became time-series scatters; scores gained contributing templates and false-alarm feedback; columns split into views; cryptic codes got descriptions; metric false alarms are confirmed with logs.",
   "source": "C5-from-service-to-tool §How it works"
  }
 },
 "questions": [
  {
   "id": "q1",
   "type": "multi",
   "kp": "why-tool",
   "prompt": "Who wanted to use the pipeline without a metric trigger, according to the note?",
   "choices": [
    "Engineers with lab devices outside the monitored population",
    "Developers checking that a new feature looks normal",
    "Support engineers who already hold a log",
    "Triage engineers with undiagnosed user tickets",
    "Customers who want to switch logging off"
   ],
   "answer": [
    0,
    1,
    2,
    3
   ],
   "explanation": "Not every fault shows in metrics, and many users already hold a log.",
   "source": "C5-from-service-to-tool §How it works"
  },
  {
   "id": "q2",
   "type": "tf",
   "kp": "why-tool",
   "prompt": "The stand-alone analyzer is a new detection model.",
   "answer": false,
   "explanation": "The models are the same as in the service; input, presentation, and access change.",
   "source": "C5-from-service-to-tool §Common confusions"
  },
  {
   "id": "q3",
   "type": "numeric",
   "kp": "workflow-metrics",
   "prompt": "Analysis time falls from an illustrative 90 min to 15 min per case. By what factor is it faster?",
   "answer": 6,
   "unit": "×",
   "tolerance": 0.1,
   "explanation": "90 ÷ 15 = 6×; illustrative values.",
   "source": "C5-from-service-to-tool §How it is measured or used"
  },
  {
   "id": "q4",
   "type": "mcq",
   "kp": "workflow-metrics",
   "prompt": "Which success metric is the north-star?",
   "choices": [
    "Weekly requests",
    "Self-reported time saving",
    "Number of anomalies found",
    "Weekly utility"
   ],
   "answer": 1,
   "explanation": "The goal is faster troubleshooting, so time saved is the measure that states it.",
   "source": "C5-from-service-to-tool §How it is measured or used"
  },
  {
   "id": "q5",
   "type": "multi",
   "kp": "workflow-metrics",
   "prompt": "Which three success metrics does the tool collect?",
   "choices": [
    "Weekly requests",
    "Self-reported time saving",
    "Template coverage",
    "Weekly utility (did it help narrow down the root cause?)",
    "Model training loss"
   ],
   "answer": [
    0,
    1,
    3
   ],
   "explanation": "Engagement, time saved, and utility are collected inside the tool.",
   "source": "C5-from-service-to-tool §How it is measured or used"
  },
  {
   "id": "q6",
   "type": "mcq",
   "kp": "four-views",
   "prompt": "An engineer wants to see whether a change started with a software update. Which view?",
   "choices": [
    "Log search",
    "State machine",
    "Metrics, with its software-version timeline",
    "Log output"
   ],
   "answer": 2,
   "explanation": "The metrics view also compares the device with its family.",
   "source": "C5-from-service-to-tool §How it works"
  },
  {
   "id": "q7",
   "type": "mcq",
   "kp": "four-views",
   "prompt": "Which view filters raw lines by time, component, process ID, thread ID, severity, and regular expression?",
   "choices": [
    "Log output",
    "Log search",
    "State machine",
    "Metrics"
   ],
   "answer": 1,
   "explanation": "Structured filters replaced filters users found hard to use.",
   "source": "C5-from-service-to-tool §How it works"
  },
  {
   "id": "q8",
   "type": "mcq",
   "kp": "four-views",
   "prompt": "Where does the HTTP-test latency over time appear?",
   "choices": [
    "As a parameter plot in the log-output view",
    "In the state-machine view",
    "Only in raw search",
    "In the metrics view"
   ],
   "answer": 0,
   "explanation": "A parameter plot is the time series of one template parameter.",
   "source": "C5-from-service-to-tool §How it works"
  },
  {
   "id": "q9",
   "type": "mcq",
   "kp": "local-and-v1",
   "prompt": "For an uploaded log file, which analysis is limited to components that have templates?",
   "choices": [
    "Log search",
    "State-machine search",
    "Anomaly detection",
    "None"
   ],
   "answer": 2,
   "explanation": "Search and state-machine views work on every component.",
   "source": "C5-from-service-to-tool §How it works"
  },
  {
   "id": "q10",
   "type": "tf",
   "kp": "local-and-v1",
   "prompt": "The first version handled one device per request, one OS family, the main log buffer only, and templates for two Wi-Fi components.",
   "answer": true,
   "explanation": "A deliberately small first version; the roadmap adds more devices, families, buffers, and streaming.",
   "source": "C5-from-service-to-tool §How it works"
  },
  {
   "id": "q11",
   "type": "mcq",
   "kp": "transparency",
   "prompt": "What does \"transparent, not a black box\" mean in the tool's design?",
   "choices": [
    "Open-source code",
    "Showing intermediate layers (templates, counts, contributing events, raw lines) so engineers choose how much to trust",
    "No access control",
    "Publishing the model weights"
   ],
   "answer": 1,
   "explanation": "Experienced engineers drive manually; new engineers lean on the golden sequence and overlay.",
   "source": "C5-from-service-to-tool §How it works"
  },
  {
   "id": "q12",
   "type": "tf",
   "kp": "transparency",
   "prompt": "Full automation is the goal of the stand-alone tool.",
   "answer": false,
   "explanation": "Transparency is the goal.",
   "source": "C5-from-service-to-tool §Common confusions"
  },
  {
   "id": "q13",
   "type": "mcq",
   "kp": "privacy-access",
   "prompt": "How does the tool treat the device ID?",
   "choices": [
    "As an output listing affected devices",
    "As an input from the user, never an output",
    "As a public label",
    "It is removed from logs"
   ],
   "answer": 1,
   "explanation": "The tool reveals no new identities.",
   "source": "C5-from-service-to-tool §How it works"
  },
  {
   "id": "q14",
   "type": "multi",
   "kp": "privacy-access",
   "prompt": "Which are privacy and access rules of the design?",
   "choices": [
    "Results are visible only to the user who asked",
    "Only logs already uploaded are analysed",
    "Access needs membership of both the tool's and the log service's groups",
    "Logs are downloaded to the engineer's laptop for speed"
   ],
   "answer": [
    0,
    1,
    2
   ],
   "explanation": "Logs stay in the cloud, so no copy lands on a laptop.",
   "source": "C5-from-service-to-tool §How it works"
  },
  {
   "id": "q15",
   "type": "tf",
   "kp": "privacy-access",
   "prompt": "An interactive log tool necessarily increases privacy exposure compared with downloading logs by hand.",
   "answer": false,
   "explanation": "Designed as described, it reduces exposure.",
   "source": "C5-from-service-to-tool §Common confusions"
  },
  {
   "id": "q16",
   "type": "mcq",
   "kp": "survey-changes",
   "prompt": "Most users could not read the probability-mass plots. What replaced them?",
   "choices": [
    "Tables of p-values",
    "Time-series scatter plots with hover detail",
    "Histograms",
    "Nothing; they were removed"
   ],
   "answer": 1,
   "explanation": "One dot per template occurrence, hover for the line.",
   "source": "C5-from-service-to-tool §How it works"
  },
  {
   "id": "q17",
   "type": "mcq",
   "kp": "survey-changes",
   "prompt": "Users used the anomaly score without knowing what it meant. What was the response?",
   "choices": [
    "Remove the score",
    "Show contributing templates and raw lines next to it, and add false-alarm feedback",
    "Rename the score",
    "Add a tooltip with the formula"
   ],
   "answer": 1,
   "explanation": "Every false-alarm click also becomes future training data.",
   "source": "C5-from-service-to-tool §How it works"
  },
  {
   "id": "q18",
   "type": "tf",
   "kp": "survey-changes",
   "prompt": "Metric false alarms are answered by confirming metric anomalies with log evidence.",
   "answer": true,
   "explanation": "That is second-signal confirmation (C4).",
   "source": "C5-from-service-to-tool §How it works"
  }
 ]
});
