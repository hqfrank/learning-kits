// Generated from learning/device-log-anomaly-detection/notes/B5-from-anomaly-to-root-cause.md; numbers loaded from constants.json.
window.QUIZ_BANKS = window.QUIZ_BANKS || [];
window.QUIZ_BANKS.push({
 "topic": "device-log-anomaly-detection",
 "topicTitle": "Finding faults in a device fleet from logs and metrics",
 "section": "B5-from-anomaly-to-root-cause",
 "sectionTitle": "B5 — From anomaly to root cause: workflows, transition edges, and state machines",
 "notePath": "../device-log-anomaly-detection/notes/B5-from-anomaly-to-root-cause.md",
 "knowledgePoints": {
  "rca-parts": {
   "title": "What RCA adds to a score",
   "summary": "RCA narrows the search, rebuilds per-task event sequences, and compares them with normal; its output is a short list of windows, templates, departing edge, and raw lines, not a verdict.",
   "source": "B5-from-anomaly-to-root-cause §What it is; How it is measured or used"
  },
  "cascade-vs-parallel": {
   "title": "Cascade versus parallel",
   "summary": "Cascade: metrics detect first and only contributing devices' logs are analysed (cheaper, sooner, misses faults absent from metrics). Parallel: logs analysed continuously beside metrics (catches more, costs more). The design started with cascade.",
   "source": "B5-from-anomaly-to-root-cause §How it works"
  },
  "pass-context": {
   "title": "Pass the metric context",
   "summary": "Tell the log analyser which metric fired and when; beware hourly or daily aggregation, and device local time versus metric UTC.",
   "source": "B5-from-anomaly-to-root-cause §How it works"
  },
  "transition-mining": {
   "title": "Mining transition edges",
   "summary": "Partition by process and thread, sort each partition by time and drop impossible timestamps, count consecutive pairs into an N × N matrix, and skip edges into a task-start template.",
   "source": "B5-from-anomaly-to-root-cause §How it works; Common confusions"
  },
  "graph-anomalies": {
   "title": "Sequence and distribution anomalies",
   "summary": "A sequence anomaly is a missing expected child within its time lag; a distribution anomaly is a changed edge probability; normal statistics need many devices over long periods.",
   "source": "B5-from-anomaly-to-root-cause §How it works"
  },
  "state-machine-views": {
   "title": "Golden sequence and state-machine search",
   "summary": "A golden sequence is the normal sequence learned from healthy logs, shown beside the anomalous one; state-machine search finds every match of a user-defined ordered pattern within a time span.",
   "source": "B5-from-anomaly-to-root-cause §How it works"
  },
  "evidence-replay": {
   "title": "Parameters, replay, and observed graphs",
   "summary": "Parameters often name the cause; linking templates to print statements enables execution replay; the workflow is the observed graph, and the anomalous template is often a downstream symptom.",
   "source": "B5-from-anomaly-to-root-cause §How it works; Common confusions"
  }
 },
 "questions": [
  {
   "id": "q1",
   "type": "mcq",
   "kp": "rca-parts",
   "prompt": "An anomaly score says which window is odd. What question does root-cause analysis ask?",
   "choices": [
    "How many trees flagged it",
    "Which path through the code was taken and where it left the normal path",
    "What the contamination should be",
    "Which device family is largest"
   ],
   "answer": 1,
   "explanation": "RCA moves from \"this is anomalous\" to \"this is what went wrong\".",
   "source": "B5-from-anomaly-to-root-cause §What it is"
  },
  {
   "id": "q2",
   "type": "tf",
   "kp": "rca-parts",
   "prompt": "The output of the RCA stage is an automated verdict naming the defect.",
   "answer": false,
   "explanation": "It is a short list of anomalous windows, their top templates, the departing edge, and raw lines for an engineer.",
   "source": "B5-from-anomaly-to-root-cause §How it is measured or used"
  },
  {
   "id": "q3",
   "type": "mcq",
   "kp": "cascade-vs-parallel",
   "prompt": "In the cascade architecture, what triggers log analysis?",
   "choices": [
    "A fixed nightly schedule over all logs",
    "A metric anomaly; only the contributing devices' logs for that range are fetched",
    "A user opening the tool",
    "Any error-severity line"
   ],
   "answer": 1,
   "explanation": "Metrics detect first and tell roughly when and what to look for.",
   "source": "B5-from-anomaly-to-root-cause §How it works"
  },
  {
   "id": "q4",
   "type": "mcq",
   "kp": "cascade-vs-parallel",
   "prompt": "What is the main weakness of the cascade architecture?",
   "choices": [
    "It needs far more compute",
    "It misses faults that never show in metrics",
    "It cannot use templates",
    "It requires labelled faults"
   ],
   "answer": 1,
   "explanation": "Parallel analysis catches such faults but costs far more and does not extend to devices without uploaded logs.",
   "source": "B5-from-anomaly-to-root-cause §How it works"
  },
  {
   "id": "q5",
   "type": "multi",
   "kp": "cascade-vs-parallel",
   "prompt": "Why did the design start with the cascade?",
   "choices": [
    "Lower risk",
    "A working result sooner",
    "A path to the parallel form later",
    "It catches faults metrics miss",
    "It analyses every uploaded log"
   ],
   "answer": [
    0,
    1,
    2
   ],
   "explanation": "Catching faults metrics miss and analysing everything are properties of the parallel form.",
   "source": "B5-from-anomaly-to-root-cause §How it works"
  },
  {
   "id": "q6",
   "type": "numeric",
   "kp": "pass-context",
   "prompt": "Which IEEE 802.11 reason code is the 4-way handshake timeout, the note's example of context passed to the log analyser?",
   "answer": 15,
   "unit": "",
   "tolerance": 0,
   "explanation": "\"Disconnects with reason code 15\" tells the analyser what and when to look for.",
   "source": "B5-from-anomaly-to-root-cause §How it works"
  },
  {
   "id": "q7",
   "type": "mcq",
   "kp": "pass-context",
   "prompt": "Which trap does the note name when passing metric context to the log analyser?",
   "choices": [
    "Metrics are always per second",
    "Device logs may use local time while metrics use UTC",
    "Logs have no timestamps",
    "Metrics carry template IDs"
   ],
   "answer": 1,
   "explanation": "Metrics may also be aggregated hourly or daily, which blurs \"when\".",
   "source": "B5-from-anomaly-to-root-cause §How it works"
  },
  {
   "id": "q8",
   "type": "mcq",
   "kp": "transition-mining",
   "prompt": "What is the first step in mining transition edges from a log?",
   "choices": [
    "Sort the whole log by timestamp",
    "Partition the stream by process ID and thread ID",
    "Count templates per window",
    "Drop parameters"
   ],
   "answer": 1,
   "explanation": "Partitioning separates concurrent writers; then sort each partition and count consecutive pairs.",
   "source": "B5-from-anomaly-to-root-cause §How it works"
  },
  {
   "id": "q9",
   "type": "tf",
   "kp": "transition-mining",
   "prompt": "Sorting the whole log by time and reading consecutive pairs gives the code's transitions.",
   "answer": false,
   "explanation": "Across threads that yields edges that never happen in the code; partition first.",
   "source": "B5-from-anomaly-to-root-cause §Common confusions"
  },
  {
   "id": "q10",
   "type": "mcq",
   "kp": "transition-mining",
   "prompt": "Why skip the edge **into** a task-start template when counting transitions?",
   "choices": [
    "Task-start templates are rare",
    "So one task's end is not linked to the next task's start",
    "To keep the matrix symmetric",
    "Because they have no parameters"
   ],
   "answer": 1,
   "explanation": "Otherwise unrelated tasks would appear connected in the workflow.",
   "source": "B5-from-anomaly-to-root-cause §How it works"
  },
  {
   "id": "q11",
   "type": "mcq",
   "kp": "graph-anomalies",
   "prompt": "`association started` is not followed by `association complete` within its usual interval. What kind of graph anomaly is this?",
   "choices": [
    "Distribution anomaly",
    "Sequence anomaly",
    "Data artefact",
    "Parsing error"
   ],
   "answer": 1,
   "explanation": "An expected child node is missing within its expected time lag.",
   "source": "B5-from-anomaly-to-root-cause §How it works"
  },
  {
   "id": "q12",
   "type": "mcq",
   "kp": "graph-anomalies",
   "prompt": "After `disconnected`, the share of transitions to `reconnect success` falls and to `network bounce` rises. What is this?",
   "choices": [
    "Sequence anomaly",
    "Distribution anomaly",
    "One-to-many parsing",
    "Environmental anomaly by definition"
   ],
   "answer": 1,
   "explanation": "The probability of an edge has changed.",
   "source": "B5-from-anomaly-to-root-cause §How it works"
  },
  {
   "id": "q13",
   "type": "tf",
   "kp": "graph-anomalies",
   "prompt": "The statistics of normal transitions can be learned from one device in one short test.",
   "answer": false,
   "explanation": "They need many devices over long periods, which is why fleet-scale mining matters.",
   "source": "B5-from-anomaly-to-root-cause §How it works"
  },
  {
   "id": "q14",
   "type": "mcq",
   "kp": "state-machine-views",
   "prompt": "What is a golden sequence?",
   "choices": [
    "The longest sequence in a log",
    "The normal event sequence for a task, learned from many healthy logs and shown beside the anomalous one",
    "The source-code control-flow graph",
    "The highest-scoring window"
   ],
   "answer": 1,
   "explanation": "It lets a new engineer see the divergence without reading source code.",
   "source": "B5-from-anomaly-to-root-cause §How it works"
  },
  {
   "id": "q15",
   "type": "mcq",
   "kp": "state-machine-views",
   "prompt": "What does a user supply to state-machine search?",
   "choices": [
    "A trained LSTM",
    "An ordered list of expected events and a maximum time span",
    "A contamination value",
    "A template set"
   ],
   "answer": 1,
   "explanation": "The tool finds every match and shows each with its raw lines; it replaces hand-written matching scripts.",
   "source": "B5-from-anomaly-to-root-cause §How it works"
  },
  {
   "id": "q16",
   "type": "tf",
   "kp": "evidence-replay",
   "prompt": "A workflow model is the same as the source code's control-flow graph.",
   "answer": false,
   "explanation": "It is the observed graph; paths the code allows but normal devices never take are absent, so their appearance is a signal.",
   "source": "B5-from-anomaly-to-root-cause §Common confusions"
  },
  {
   "id": "q17",
   "type": "mcq",
   "kp": "evidence-replay",
   "prompt": "Is the anomalous template the cause of the fault?",
   "choices": [
    "Always",
    "Often it is a symptom downstream of the cause, in another component",
    "Never",
    "Only for kernel logs"
   ],
   "answer": 1,
   "explanation": "The cause may sit in DHCP, time sync, or a kernel driver (C4).",
   "source": "B5-from-anomaly-to-root-cause §Common confusions"
  },
  {
   "id": "q18",
   "type": "tf",
   "kp": "evidence-replay",
   "prompt": "If each template is linked to its print statement, the event sequence becomes a path through the code that can be replayed.",
   "answer": true,
   "explanation": "That is execution replay.",
   "source": "B5-from-anomaly-to-root-cause §How it works"
  }
 ]
});
