// Generated from learning/device-log-anomaly-detection/notes/C3-data-quality.md; numbers loaded from constants.json.
window.QUIZ_BANKS = window.QUIZ_BANKS || [];
window.QUIZ_BANKS.push({
 "topic": "device-log-anomaly-detection",
 "topicTitle": "Finding faults in a device fleet from logs and metrics",
 "section": "C3-data-quality",
 "sectionTitle": "C3 — Data quality: the input problems that become false alarms",
 "notePath": "../device-log-anomaly-detection/notes/C3-data-quality.md",
 "knowledgePoints": {
  "four-dimensions": {
   "title": "Availability, accuracy, timeliness, consistency",
   "summary": "Availability: can you get the data; accuracy: are values right; timeliness: does data arrive without gaps; consistency: does each field mean one thing.",
   "source": "C3-data-quality §What it is; Terms introduced"
  },
  "availability-power": {
   "title": "Availability limits and low power",
   "summary": "Access may be limited to a pre-release population and a short retention window; tickets may fall outside them, and small families give little power for rare events.",
   "source": "C3-data-quality §How it works"
  },
  "accuracy-clocks": {
   "title": "Clock accuracy",
   "summary": "A device's event time must precede the cloud receive time; inversions show wrong clocks and move events between days, corrupting the series.",
   "source": "C3-data-quality §How it works; Common confusions"
  },
  "timeliness-gaps": {
   "title": "Gaps look like drops to zero",
   "summary": "A missing day for an event-triggered metric looks like a drop to zero; run a gap detector with an alarm before anomaly detection.",
   "source": "C3-data-quality §How it works"
  },
  "consistency-copies": {
   "title": "Consistency and extra copies",
   "summary": "Shuffled columns, per-family formats, fragile fixed-position parsing, and documentation drift; every extra copy between source and analysis is a chance to break the schema.",
   "source": "C3-data-quality §How it works; Common confusions"
  },
  "hygiene-report": {
   "title": "Hygiene checks and the report",
   "summary": "De-duplicate retries, alert on unseen values, filter stress-test devices; write one row per finding (dimension, check, rate, impact, fix); rule out data before tuning the model; track the data-artefact label.",
   "source": "C3-data-quality §How it works; How it is measured or used; Common confusions"
  }
 },
 "questions": [
  {
   "id": "q1",
   "type": "mcq",
   "kp": "four-dimensions",
   "prompt": "Which data-quality dimension asks whether each field means one thing across records, families, and time?",
   "choices": [
    "Availability",
    "Accuracy",
    "Timeliness",
    "Consistency"
   ],
   "answer": 3,
   "explanation": "Consistency covers shuffled columns and per-family formats.",
   "source": "C3-data-quality §What it is"
  },
  {
   "id": "q2",
   "type": "multi",
   "kp": "four-dimensions",
   "prompt": "Which are the four dimensions the note audits?",
   "choices": [
    "Availability",
    "Accuracy",
    "Sparsity",
    "Timeliness",
    "Consistency",
    "Latency"
   ],
   "answer": [
    0,
    1,
    3,
    4
   ],
   "explanation": "They are the dimensions that mattered for event-triggered fleet metrics.",
   "source": "C3-data-quality §What it is"
  },
  {
   "id": "q3",
   "type": "mcq",
   "kp": "four-dimensions",
   "prompt": "Which dimension asks whether data arrive when expected, without gaps?",
   "choices": [
    "Accuracy",
    "Timeliness",
    "Availability",
    "Consistency"
   ],
   "answer": 1,
   "explanation": "Missing days for a cohort are a timeliness problem.",
   "source": "C3-data-quality §Terms introduced"
  },
  {
   "id": "q4",
   "type": "mcq",
   "kp": "availability-power",
   "prompt": "With 100 devices in a family, 3 devices with a rare reason code move the share from about 0 % to 3 %. Why is that ambiguous?",
   "choices": [
    "The share formula is wrong",
    "A real defect and a few unlucky households look the same",
    "The reason code is invalid",
    "Retention is too long"
   ],
   "answer": 1,
   "explanation": "A small population has little power for rare events (A2).",
   "source": "C3-data-quality §How it works"
  },
  {
   "id": "q5",
   "type": "numeric",
   "kp": "availability-power",
   "prompt": "A family has 100 active devices. 3 of them emit a rare reason code on one day. What is the share of devices?",
   "answer": 3,
   "unit": "%",
   "tolerance": 0.1,
   "explanation": "3 ÷ 100 = 3 %: a jump from about 0 % driven by 3 households (illustrative).",
   "source": "C3-data-quality §How it works"
  },
  {
   "id": "q6",
   "type": "tf",
   "kp": "availability-power",
   "prompt": "With access limited to a pre-release population and an illustrative 60-day retention, many tickets refer to devices whose data cannot be fetched.",
   "answer": true,
   "explanation": "Availability limits which tickets can be enriched.",
   "source": "C3-data-quality §How it works"
  },
  {
   "id": "q7",
   "type": "mcq",
   "kp": "accuracy-clocks",
   "prompt": "Which accuracy check does the note use for timestamps?",
   "choices": [
    "Device time must be later than receive time",
    "Device event time must precede the cloud receive time",
    "All timestamps must be in local time",
    "Timestamps must be unique"
   ],
   "answer": 1,
   "explanation": "Device time after receive time means the device clock is wrong (unsynchronised, reset, wrong zone).",
   "source": "C3-data-quality §How it works"
  },
  {
   "id": "q8",
   "type": "mcq",
   "kp": "accuracy-clocks",
   "prompt": "Why do wrong device clocks matter for trend detection?",
   "choices": [
    "They change template IDs",
    "Events move between days and corrupt the daily series",
    "They break the parse tree",
    "They raise contamination"
   ],
   "answer": 1,
   "explanation": "Time-based detection relies on correct timestamps (B4).",
   "source": "C3-data-quality §How it works"
  },
  {
   "id": "q9",
   "type": "tf",
   "kp": "accuracy-clocks",
   "prompt": "An illustrative 3 % of mis-timed records is too small to matter.",
   "answer": false,
   "explanation": "It is enough to create spurious day-to-day changes in a rare metric.",
   "source": "C3-data-quality §Common confusions"
  },
  {
   "id": "q10",
   "type": "mcq",
   "kp": "timeliness-gaps",
   "prompt": "A whole day of data is missing for one cohort. How does it look to an anomaly detector on an event-triggered metric?",
   "choices": [
    "Like a spike",
    "Like a drop to zero",
    "Like a normal day",
    "It is skipped automatically"
   ],
   "answer": 1,
   "explanation": "Absence is the normal state of event-triggered data, so a gap looks like an improvement or a drop and gets flagged.",
   "source": "C3-data-quality §How it works"
  },
  {
   "id": "q11",
   "type": "mcq",
   "kp": "timeliness-gaps",
   "prompt": "Where should the gap detector run?",
   "choices": [
    "After ticketing",
    "Before anomaly detection, with an alarm",
    "Only weekly",
    "Inside the isolation forest"
   ],
   "answer": 1,
   "explanation": "It is cheaper than explaining false tickets.",
   "source": "C3-data-quality §How it works"
  },
  {
   "id": "q12",
   "type": "mcq",
   "kp": "consistency-copies",
   "prompt": "A parser reads `11a` instead of `11ac` after a serialisation step changed one space. What is the fix?",
   "choices": [
    "Pad every field with spaces",
    "Parse with a real JSON parser and validate against allowed values",
    "Drop the band field",
    "Use a longer fixed width"
   ],
   "answer": 1,
   "explanation": "Fixed-position parsing is fragile.",
   "source": "C3-data-quality §How it works"
  },
  {
   "id": "q13",
   "type": "mcq",
   "kp": "consistency-copies",
   "prompt": "Why consume directly from the source store with an explicit schema?",
   "choices": [
    "It is faster to query",
    "Each extra copy (export, re-import) is a chance to reorder columns, change types, and break parsing",
    "The source store has longer retention",
    "It removes duplicates"
   ],
   "answer": 1,
   "explanation": "Removing copies removes a class of faults.",
   "source": "C3-data-quality §How it works"
  },
  {
   "id": "q14",
   "type": "tf",
   "kp": "consistency-copies",
   "prompt": "The documented schema can be trusted to describe the data.",
   "answer": false,
   "explanation": "Verify the schema against a sample of real records; documentation drifts.",
   "source": "C3-data-quality §Common confusions"
  },
  {
   "id": "q15",
   "type": "multi",
   "kp": "hygiene-report",
   "prompt": "Which general hygiene checks does the note list?",
   "choices": [
    "De-duplicate events resent after a retry",
    "Alert on unseen category values after a release",
    "Filter devices in automated stress tests",
    "Impute missing days with the weekly mean"
   ],
   "answer": [
    0,
    1,
    2
   ],
   "explanation": "Imputing would hide gaps; the note flags them instead.",
   "source": "C3-data-quality §How it works"
  },
  {
   "id": "q16",
   "type": "mcq",
   "kp": "hygiene-report",
   "prompt": "What columns does each row of a data-quality report have?",
   "choices": [
    "Device, day, score",
    "Dimension, check, rate, downstream impact, fix",
    "Template, count, severity",
    "Owner, date, status"
   ],
   "answer": 1,
   "explanation": "One row per finding.",
   "source": "C3-data-quality §How it works"
  },
  {
   "id": "q17",
   "type": "tf",
   "kp": "hygiene-report",
   "prompt": "When false alarms rise, tune the model first.",
   "answer": false,
   "explanation": "Rule out gaps, clock errors, and format changes first; often the data are producing the false positives.",
   "source": "C3-data-quality §Common confusions"
  },
  {
   "id": "q18",
   "type": "mcq",
   "kp": "hygiene-report",
   "prompt": "What does the share of tickets resolved with the label \"data artefact\" measure?",
   "choices": [
    "Detection rate",
    "The false-alarm cost of poor data",
    "Template coverage",
    "Model drift"
   ],
   "answer": 1,
   "explanation": "Push fixes upstream to the source owners rather than patching downstream forever.",
   "source": "C3-data-quality §How it is measured or used"
  }
 ]
});
