// Generated from learning/agentic-device-control/notes/01-the-message-path.md; numbers loaded from constants.json.
window.QUIZ_BANKS = window.QUIZ_BANKS || [];
window.QUIZ_BANKS.push({
 "topic": "agentic-device-control",
 "topicTitle": "Agentic control of a consumer device",
 "section": "01-the-message-path",
 "sectionTitle": "01 — The message path: cloud → device → agent → result",
 "notePath": "../agentic-device-control/notes/01-the-message-path.md",
 "knowledgePoints": {
  "five-stages": {
   "title": "Five stages of the path",
   "summary": "Channel down, receiver, work executor, agent graph, channel up with exactly one result.",
   "source": "01-the-message-path §What it is"
  },
  "result-status": {
   "title": "Four result statuses",
   "summary": "SUCCESS, ERROR, BUSY, TIMEOUT; BUSY is a normal concurrency answer, counted separately from ERROR.",
   "source": "01-the-message-path §What it is; Common confusions"
  },
  "dedup-idempotency": {
   "title": "De-duplication is not task idempotency",
   "summary": "The cache (illustrative 10 min) drops exact repeats by message ID; a retry with a new ID runs the task again.",
   "source": "01-the-message-path §How it works; Common confusions"
  },
  "lock-busy": {
   "title": "Execution lock and BUSY instead of a queue",
   "summary": "One screen means one task; a second gets BUSY at once so the cloud decides whether to retry, instead of a stale task running later.",
   "source": "01-the-message-path §How it works; Design choices and trade-offs"
  },
  "watchdog": {
   "title": "Watchdog timeout as a safety bound",
   "summary": "Stops the task after an illustrative 5 min, releases the lock, reports TIMEOUT; sized from the task-time distribution, well above the slow tail.",
   "source": "01-the-message-path §How it works; Design choices and trade-offs"
  },
  "one-result": {
   "title": "Exactly one result per accepted task",
   "summary": "Every exit path sends a result; a missing result is indistinguishable from a lost message.",
   "source": "01-the-message-path §Design choices and trade-offs"
  }
 },
 "questions": [
  {
   "id": "q1",
   "type": "mcq",
   "kp": "five-stages",
   "prompt": "Which component runs the task outside the user interface on the device?",
   "choices": [
    "The work executor",
    "The receiver",
    "The router",
    "The de-duplication cache"
   ],
   "answer": 0,
   "explanation": "The work executor is the background-work component (a job scheduler such as WorkManager on Android-type devices).",
   "source": "01-the-message-path §What it is"
  },
  {
   "id": "q2",
   "type": "mcq",
   "kp": "five-stages",
   "prompt": "What is the correct order of the message path?",
   "choices": [
    "Channel down → receiver → work executor → agent graph → channel up",
    "Receiver → channel down → agent graph → work executor → channel up",
    "Channel down → agent graph → receiver → work executor → channel up",
    "Work executor → receiver → channel down → agent graph → channel up"
   ],
   "answer": 0,
   "explanation": "The receiver validates before the expensive work, which the executor runs through the graph; one result goes back up.",
   "source": "01-the-message-path §What it is"
  },
  {
   "id": "q3",
   "type": "tf",
   "kp": "five-stages",
   "prompt": "The guards (validate, de-duplicate, lock, time-limit) are placed so that they answer their question before the expensive model work starts.",
   "answer": true,
   "explanation": "Each guard is cheap and removes an edge fault before any model token is spent.",
   "source": "01-the-message-path §How it works; Why it matters"
  },
  {
   "id": "q4",
   "type": "multi",
   "kp": "result-status",
   "prompt": "Which values can the result status take? Select all that apply.",
   "choices": [
    "SUCCESS",
    "ERROR",
    "BUSY",
    "TIMEOUT",
    "QUEUED"
   ],
   "answer": [
    0,
    1,
    2,
    3
   ],
   "explanation": "There are four statuses; there is no queue, so no QUEUED.",
   "source": "01-the-message-path §What it is"
  },
  {
   "id": "q5",
   "type": "tf",
   "kp": "result-status",
   "prompt": "BUSY should be counted as an ERROR on dashboards.",
   "answer": false,
   "explanation": "BUSY is a normal answer to concurrency; count it separately from ERROR.",
   "source": "01-the-message-path §Common confusions"
  },
  {
   "id": "q6",
   "type": "mcq",
   "kp": "result-status",
   "prompt": "A message arrives malformed. What happens?",
   "choices": [
    "ERROR is reported at once",
    "BUSY is reported",
    "It waits in a queue",
    "It is retried after the watchdog fires"
   ],
   "answer": 0,
   "explanation": "Validation fails fast with ERROR before any work runs.",
   "source": "01-the-message-path §How it works"
  },
  {
   "id": "q7",
   "type": "mcq",
   "kp": "dedup-idempotency",
   "prompt": "The cloud lost a result and resends the task with a **new message ID**. What does the de-duplication cache do?",
   "choices": [
    "Nothing; the task runs again",
    "Drops it as a repeat",
    "Returns the cached old result",
    "Reports BUSY"
   ],
   "answer": 0,
   "explanation": "The cache matches message IDs. A new ID is a new message, so a non-idempotent task such as \"add an item\" runs twice.",
   "source": "01-the-message-path §Common confusions"
  },
  {
   "id": "q8",
   "type": "tf",
   "kp": "dedup-idempotency",
   "prompt": "The de-duplication cache makes the task itself idempotent.",
   "answer": false,
   "explanation": "It makes exact message repeats safe; it does not make \"add an item to the list\" safe to run twice.",
   "source": "01-the-message-path §How it works"
  },
  {
   "id": "q9",
   "type": "numeric",
   "kp": "dedup-idempotency",
   "prompt": "For how many minutes does the de-duplication cache keep message IDs (illustrative)?",
   "answer": 10,
   "unit": "min",
   "tolerance": 0,
   "explanation": "An illustrative 10 min window covers duplicate deliveries from the channel.",
   "source": "01-the-message-path §How it works; constants.json dedup_window_illustrative"
  },
  {
   "id": "q10",
   "type": "mcq",
   "kp": "lock-busy",
   "prompt": "Why does the device answer a second task with BUSY rather than queueing it?",
   "choices": [
    "A queued task could run minutes later on a changed screen; the cloud knows if it is still wanted",
    "Queues are impossible on a mobile OS",
    "BUSY saves tokens inside the model call",
    "The lock cannot be released until reboot"
   ],
   "answer": 0,
   "explanation": "BUSY pushes the retry decision to the cloud; the cost is that the cloud must implement retry with back-off.",
   "source": "01-the-message-path §Design choices and trade-offs"
  },
  {
   "id": "q11",
   "type": "tf",
   "kp": "lock-busy",
   "prompt": "The execution lock exists because the device has one screen, so only one task can run at a time.",
   "answer": true,
   "explanation": "Two tasks would fight for one screen.",
   "source": "01-the-message-path §How it works"
  },
  {
   "id": "q12",
   "type": "numeric",
   "kp": "watchdog",
   "prompt": "After how many minutes does the watchdog stop a task (illustrative)?",
   "answer": 5,
   "unit": "min",
   "tolerance": 0,
   "explanation": "An illustrative 5 min; it cleans up, releases the lock and reports TIMEOUT.",
   "source": "01-the-message-path §How it works; constants.json watchdog_timeout_illustrative"
  },
  {
   "id": "q13",
   "type": "mcq",
   "kp": "watchdog",
   "prompt": "How should the watchdog timeout be chosen?",
   "choices": [
    "Well above the slow tail of successful task times, from their distribution",
    "Equal to the median task time",
    "As short as possible to save cost",
    "Equal to the de-duplication window"
   ],
   "answer": 0,
   "explanation": "A limit several times the illustrative 20 s simple-task time stops runaways without killing slow successes.",
   "source": "01-the-message-path §Design choices and trade-offs"
  },
  {
   "id": "q14",
   "type": "tf",
   "kp": "watchdog",
   "prompt": "A task that reaches the watchdog is best treated as a slow success.",
   "answer": false,
   "explanation": "The timeout is a safety bound, not a performance number; reaching it is a failure to investigate.",
   "source": "01-the-message-path §Common confusions"
  },
  {
   "id": "q15",
   "type": "mcq",
   "kp": "one-result",
   "prompt": "Why must every exit path, including exceptions, send a result?",
   "choices": [
    "A missing result looks like a lost message, so the cloud cannot decide whether to retry",
    "The model needs the result for its next call",
    "Results refresh the prompt cache",
    "The lock is released only when a result is sent"
   ],
   "answer": 0,
   "explanation": "One result per accepted task keeps the cloud's retry decision well-defined.",
   "source": "01-the-message-path §Design choices and trade-offs"
  },
  {
   "id": "q16",
   "type": "tf",
   "kp": "one-result",
   "prompt": "The note argues most production faults in a remote-control system are at the edges, not in the model.",
   "answer": true,
   "explanation": "Duplicate delivery, two tasks on one screen and a task that never reports are all edge faults.",
   "source": "01-the-message-path §Why it matters"
  }
 ]
});
