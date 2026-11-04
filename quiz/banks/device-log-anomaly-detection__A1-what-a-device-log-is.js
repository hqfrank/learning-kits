// Generated from learning/device-log-anomaly-detection/notes/A1-what-a-device-log-is.md; numbers loaded from constants.json.
window.QUIZ_BANKS = window.QUIZ_BANKS || [];
window.QUIZ_BANKS.push({
 "topic": "device-log-anomaly-detection",
 "topicTitle": "Finding faults in a device fleet from logs and metrics",
 "section": "A1-what-a-device-log-is",
 "sectionTitle": "A1 — What a device log is",
 "notePath": "../device-log-anomaly-detection/notes/A1-what-a-device-log-is.md",
 "knowledgePoints": {
  "line-anatomy": {
   "title": "Header plus message",
   "summary": "Each line has a header (date, time, pid, tid, level, tag) and a free-text message produced by a print statement with run-time values filled in.",
   "source": "A1-what-a-device-log-is §What it is"
  },
  "params-reason-codes": {
   "title": "Constant words and parameters",
   "summary": "The constant words come from the print statement; the values after `=` are parameters, such as an IEEE 802.11 reason code (3 = leaving, 2 = previous authentication no longer valid).",
   "source": "A1-what-a-device-log-is §What it is"
  },
  "interleaving-ties": {
   "title": "Interleaving and timestamp ties",
   "summary": "Many threads write into one stream; order within a thread is meaningful, order across threads mostly is not, and equal millisecond timestamps leave the true order unknown.",
   "source": "A1-what-a-device-log-is §How it works; Common confusions"
  },
  "ring-buffers": {
   "title": "Named ring buffers that overwrite",
   "summary": "A logging daemon keeps fixed-size buffers (main, system, radio, events, crash, kernel); when full, new lines overwrite the oldest, so only hours of history survive.",
   "source": "A1-what-a-device-log-is §How it works; Common confusions"
  },
  "volume-relevance": {
   "title": "Most lines are irrelevant to one question",
   "summary": "Keeping only the components relevant to a question (for example Wi-Fi) can leave about 1 % of the lines (illustrative).",
   "source": "A1-what-a-device-log-is §How it works"
  },
  "collection-constraints": {
   "title": "Collection constraints",
   "summary": "Upload is selective, retention is short, a crash can end the log, formats differ, and privacy limits content; these decide what can be analysed.",
   "source": "A1-what-a-device-log-is §How it is measured or used"
  },
  "errors-not-fault": {
   "title": "Error lines are not where the fault is",
   "summary": "Error-severity lines are frequent on healthy devices; a fault often shows as a change in which lines appear and how often.",
   "source": "A1-what-a-device-log-is §Common confusions"
  }
 },
 "questions": [
  {
   "id": "q1",
   "type": "mcq",
   "kp": "line-anatomy",
   "prompt": "In the `<date> <time> <pid> <tid> <level> <tag>: <message>` layout, which field names the software component that wrote the line?",
   "choices": [
    "pid",
    "level",
    "tag",
    "tid"
   ],
   "answer": 2,
   "explanation": "The tag (component) names the writer, for example the Wi-Fi supplicant; pid and tid identify the process and thread.",
   "source": "A1-what-a-device-log-is §What it is"
  },
  {
   "id": "q2",
   "type": "mcq",
   "kp": "line-anatomy",
   "prompt": "Among the Android severity letters V, D, I, W, E, F, which is the most severe?",
   "choices": [
    "E",
    "W",
    "F",
    "I"
   ],
   "answer": 2,
   "explanation": "The scale runs verbose, debug, info, warning, error, fatal; F (fatal) is the top.",
   "source": "A1-what-a-device-log-is §What it is"
  },
  {
   "id": "q3",
   "type": "tf",
   "kp": "line-anatomy",
   "prompt": "The message part of a log line is produced by a print statement in the source code, with run-time values filled in.",
   "answer": true,
   "explanation": "That is why parsing can recover the print statement as a template and the run-time values as parameters (B1).",
   "source": "A1-what-a-device-log-is §What it is"
  },
  {
   "id": "q4",
   "type": "mcq",
   "kp": "params-reason-codes",
   "prompt": "In `CTRL-EVENT-DISCONNECTED bssid=<mac> reason=3 locally_generated=1`, what are the values after `=`?",
   "choices": [
    "Severity levels",
    "Parameters that change from line to line",
    "Component tags",
    "Template IDs"
   ],
   "answer": 1,
   "explanation": "The constant words come from the print statement; the values after `=` are run-time parameters.",
   "source": "A1-what-a-device-log-is §What it is"
  },
  {
   "id": "q5",
   "type": "numeric",
   "kp": "params-reason-codes",
   "prompt": "Which IEEE 802.11 reason code means \"previous authentication no longer valid\"?",
   "answer": 2,
   "unit": "",
   "tolerance": 0,
   "explanation": "Code 2 is previous authentication no longer valid; code 3 means the station is leaving (IEEE 802.11 reason-code table).",
   "source": "A1-what-a-device-log-is §What it is"
  },
  {
   "id": "q6",
   "type": "mcq",
   "kp": "interleaving-ties",
   "prompt": "Two adjacent lines in a log file come from different threads. What can you conclude about their order?",
   "choices": [
    "The first caused the second",
    "They ran in that exact order",
    "Little: order across threads mostly is not meaningful",
    "They share a template"
   ],
   "answer": 2,
   "explanation": "Concurrent writers interleave; only order within one thread is meaningful.",
   "source": "A1-what-a-device-log-is §How it works; Common confusions"
  },
  {
   "id": "q7",
   "type": "tf",
   "kp": "interleaving-ties",
   "prompt": "When several lines carry the same millisecond timestamp, their true order can be recovered from the timestamp.",
   "answer": false,
   "explanation": "Timestamps have fixed resolution; ties leave the true order unknown.",
   "source": "A1-what-a-device-log-is §How it works"
  },
  {
   "id": "q8",
   "type": "multi",
   "kp": "interleaving-ties",
   "prompt": "Which statements about a device log stream are true?",
   "choices": [
    "Order within one thread is meaningful",
    "Order across threads is guaranteed",
    "Several lines can share one timestamp",
    "Dozens of components write into the same stream"
   ],
   "answer": [
    0,
    2,
    3
   ],
   "explanation": "The log records what each thread chose to print, interleaved and with ties in time; cross-thread order is not guaranteed.",
   "source": "A1-what-a-device-log-is §How it works; Common confusions"
  },
  {
   "id": "q9",
   "type": "mcq",
   "kp": "ring-buffers",
   "prompt": "What happens when a log ring buffer is full?",
   "choices": [
    "Logging stops until upload",
    "New lines overwrite the oldest lines",
    "The buffer grows into flash storage",
    "Low-severity lines are compressed"
   ],
   "answer": 1,
   "explanation": "A ring buffer has a fixed size; new entries overwrite the oldest ones.",
   "source": "A1-what-a-device-log-is §How it works"
  },
  {
   "id": "q10",
   "type": "mcq",
   "kp": "ring-buffers",
   "prompt": "A Wi-Fi driver crashes. An analysis reads only the main buffer. What will it see of the crash?",
   "choices": [
    "The full crash trace",
    "Nothing: a driver crash writes to the kernel buffer",
    "Only the severity line",
    "A metric record of the crash"
   ],
   "answer": 1,
   "explanation": "The logging daemon keeps separate buffers; driver faults go to the kernel buffer, which must be read separately.",
   "source": "A1-what-a-device-log-is §Common confusions"
  },
  {
   "id": "q11",
   "type": "tf",
   "kp": "ring-buffers",
   "prompt": "At an illustrative 500,000 lines per device-day, a buffer of a few megabytes holds weeks of history.",
   "answer": false,
   "explanation": "At that rate a few-megabyte buffer holds only hours of history; lost evidence is the normal case.",
   "source": "A1-what-a-device-log-is §How it works"
  },
  {
   "id": "q12",
   "type": "numeric",
   "kp": "volume-relevance",
   "prompt": "A device writes an illustrative 500,000 lines per day. Keeping only the Wi-Fi components leaves an illustrative 1 %. How many lines remain per day?",
   "answer": 5000,
   "unit": "lines",
   "tolerance": 1,
   "explanation": "500,000 × 1 % = 5,000 lines; most lines are irrelevant to any one question.",
   "source": "A1-what-a-device-log-is §How it works"
  },
  {
   "id": "q13",
   "type": "tf",
   "kp": "volume-relevance",
   "prompt": "For a Wi-Fi question, filtering the log to the Wi-Fi components discards most of the lines.",
   "answer": true,
   "explanation": "Most lines are irrelevant to any one question; in the illustrative case about 1 % remain.",
   "source": "A1-what-a-device-log-is §How it works"
  },
  {
   "id": "q14",
   "type": "multi",
   "kp": "collection-constraints",
   "prompt": "Which are collection constraints the note lists?",
   "choices": [
    "Production devices upload logs only on demand",
    "Uploaded logs are kept only for a limited time",
    "Every device uploads its full log continuously",
    "A crash can end the log so later lines do not exist",
    "Lab, local, and production captures can use different formats"
   ],
   "answer": [
    0,
    1,
    3,
    4
   ],
   "explanation": "Upload is selective, retention is short, the window may be cut by a crash, and formats differ. Continuous full upload is not the norm.",
   "source": "A1-what-a-device-log-is §How it is measured or used"
  },
  {
   "id": "q15",
   "type": "tf",
   "kp": "collection-constraints",
   "prompt": "The note's privacy baseline never collects user identity, location, browsing history, or IP addresses, offers opt-out, and limits on-device retention.",
   "answer": true,
   "explanation": "That is the baseline expectation named in the note (see C5).",
   "source": "A1-what-a-device-log-is §How it is measured or used"
  },
  {
   "id": "q16",
   "type": "tf",
   "kp": "errors-not-fault",
   "prompt": "Error-severity lines mark the fault, so filtering to E and F lines is enough to find it.",
   "answer": false,
   "explanation": "Error lines are frequent on healthy devices too; the fault often shows as a change in which lines appear and how often.",
   "source": "A1-what-a-device-log-is §Common confusions"
  },
  {
   "id": "q17",
   "type": "mcq",
   "kp": "errors-not-fault",
   "prompt": "How does a fault most often show up in a device log, according to the note?",
   "choices": [
    "As a single fatal line",
    "As a change in which lines appear and how often",
    "As a gap in timestamps",
    "As a new log buffer"
   ],
   "answer": 1,
   "explanation": "That is why count vectors over windows (B2) are a useful representation.",
   "source": "A1-what-a-device-log-is §Common confusions"
  }
 ]
});
