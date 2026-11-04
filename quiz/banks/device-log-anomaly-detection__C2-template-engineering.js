// Generated from learning/device-log-anomaly-detection/notes/C2-template-engineering.md; numbers loaded from constants.json.
window.QUIZ_BANKS = window.QUIZ_BANKS || [];
window.QUIZ_BANKS.push({
 "topic": "device-log-anomaly-detection",
 "topicTitle": "Finding faults in a device fleet from logs and metrics",
 "section": "C2-template-engineering",
 "sectionTitle": "C2 — Template engineering: post-processing, versions, and retraining",
 "notePath": "../device-log-anomaly-detection/notes/C2-template-engineering.md",
 "knowledgePoints": {
  "post-process": {
   "title": "Four repairs for mined templates",
   "summary": "Merge values mistaken for constants, mask variables the preprocessor missed, check each template against its print statement, and group templates by function.",
   "source": "C2-template-engineering §How it works"
  },
  "validate-known-different": {
   "title": "Validate on known-different devices",
   "summary": "Parse healthy and known-problem devices over the same week; problem devices should show extra recovery and error templates; a component can separate normal from abnormal without explaining it.",
   "source": "C2-template-engineering §How it works"
  },
  "versions-drift": {
   "title": "Versions, OS drift, stable IDs",
   "summary": "Keep one template set per OS family and component, expect print statements to change per release, and derive IDs from a hash of the normalised template text.",
   "source": "C2-template-engineering §How it works"
  },
  "retraining-cascade": {
   "title": "The retraining cascade",
   "summary": "A template change rebuilds the tree, changes the feature space, forces a model retrain, and requires a ground-truth re-run; cadence follows the release train.",
   "source": "C2-template-engineering §How it works; Common confusions"
  },
  "coverage-monitor": {
   "title": "Monitor coverage and the unmatched bucket",
   "summary": "Track the share of lines matched and the unmatched bucket per release and component; a jump after a release is the signal to update; unmatched lines are not noise.",
   "source": "C2-template-engineering §How it works; Common confusions"
  },
  "toward-automation": {
   "title": "Toward automation",
   "summary": "Extract print statements automatically, treat the source-code set as the benchmark, add data-driven discoveries from the unmatched bucket, and compare on the same ground truth before switching.",
   "source": "C2-template-engineering §How it works"
  }
 },
 "questions": [
  {
   "id": "q1",
   "type": "mcq",
   "kp": "post-process",
   "prompt": "A miner emits `pingTest target=GATEWAY` and `pingTest target=LOCALHOST` separately. What must post-processing decide?",
   "choices": [
    "Which one to delete",
    "Whether `target` is a parameter (merge into `target=<*>`) or a meaningful constant",
    "Which severity to assign",
    "Which OS family it belongs to"
   ],
   "answer": 1,
   "explanation": "Host names in an HTTP test are usually parameters; a state name usually is not.",
   "source": "C2-template-engineering §How it works"
  },
  {
   "id": "q2",
   "type": "mcq",
   "kp": "post-process",
   "prompt": "When mined templates are checked against the source, what are templates with **no** print statement?",
   "choices": [
    "Gaps in coverage",
    "Parsing errors",
    "Error paths",
    "Stable IDs"
   ],
   "answer": 1,
   "explanation": "Print statements with no template are the gaps, usually error and warning paths.",
   "source": "C2-template-engineering §How it works"
  },
  {
   "id": "q3",
   "type": "multi",
   "kp": "post-process",
   "prompt": "Which are the four repairs the note applies to mined templates?",
   "choices": [
    "Merge values mistaken for constants",
    "Mask variables the preprocessor missed",
    "Delete templates seen fewer than ten times",
    "Check each template against the source",
    "Group templates by function"
   ],
   "answer": [
    0,
    1,
    3,
    4
   ],
   "explanation": "Deleting rare templates would remove exactly the error paths anomaly detection needs.",
   "source": "C2-template-engineering §How it works"
  },
  {
   "id": "q4",
   "type": "tf",
   "kp": "post-process",
   "prompt": "IP addresses, MAC addresses, host names, and file paths should become `<*>` before mining.",
   "answer": true,
   "explanation": "Otherwise they create one template per value.",
   "source": "C2-template-engineering §How it works"
  },
  {
   "id": "q5",
   "type": "mcq",
   "kp": "validate-known-different",
   "prompt": "Logs of 10 healthy and 5 known-problem devices are parsed over the same week (illustrative). What should the problem devices show?",
   "choices": [
    "Exactly the same templates",
    "Extra recovery and error templates that never appear on the healthy ones",
    "Fewer lines overall",
    "Only parameter changes"
   ],
   "answer": 1,
   "explanation": "Healthy devices show a regular, periodic pattern of status and test templates.",
   "source": "C2-template-engineering §How it works"
  },
  {
   "id": "q6",
   "type": "mcq",
   "kp": "validate-known-different",
   "prompt": "In that check, the problem devices show no templates the healthy ones lack. What follows?",
   "choices": [
    "The problem is environmental",
    "The template set cannot separate the two, and no model will",
    "The model needs more trees",
    "The week was too short"
   ],
   "answer": 1,
   "explanation": "Separation must be visible in the templates before any model can use it.",
   "source": "C2-template-engineering §How it works"
  },
  {
   "id": "q7",
   "type": "tf",
   "kp": "validate-known-different",
   "prompt": "If a component's templates separate normal from abnormal devices, they also explain the cause.",
   "answer": false,
   "explanation": "A diagnostics service may show something is wrong while the cause lives in the supplicant, DHCP client, or kernel driver.",
   "source": "C2-template-engineering §How it works"
  },
  {
   "id": "q8",
   "type": "mcq",
   "kp": "versions-drift",
   "prompt": "How should a stable template ID be derived?",
   "choices": [
    "From the order in which templates were mined",
    "From a hash of the normalised template text",
    "From the line number in the log",
    "From the component name only"
   ],
   "answer": 1,
   "explanation": "The same template then keeps its ID across rebuilds and devices.",
   "source": "C2-template-engineering §How it works"
  },
  {
   "id": "q9",
   "type": "tf",
   "kp": "versions-drift",
   "prompt": "Two OS families running the same Wi-Fi stack can share one template set.",
   "answer": false,
   "explanation": "They have different components and print statements; keep one set per family and per component.",
   "source": "C2-template-engineering §How it works"
  },
  {
   "id": "q10",
   "type": "mcq",
   "kp": "versions-drift",
   "prompt": "Developers change a print statement in a release. How do a rule-based tool and a template pipeline differ?",
   "choices": [
    "Both adapt automatically",
    "The rule breaks silently; the pipeline at least sees new lines falling into the unmatched bucket",
    "The pipeline breaks silently; the rule adapts",
    "Neither notices"
   ],
   "answer": 1,
   "explanation": "Coverage monitoring makes the drift visible.",
   "source": "C2-template-engineering §How it works"
  },
  {
   "id": "q11",
   "type": "mcq",
   "kp": "retraining-cascade",
   "prompt": "In what order does a template change ripple through the pipeline?",
   "choices": [
    "Retrain model → rebuild tree → re-run ground truth → new features",
    "Rebuild tree → new feature space → retrain model → re-run ground truth",
    "Re-run ground truth → rebuild tree → retrain model",
    "New features → retrain → rebuild tree"
   ],
   "answer": 1,
   "explanation": "One column per template means every template change changes the feature space.",
   "source": "C2-template-engineering §How it works"
  },
  {
   "id": "q12",
   "type": "numeric",
   "kp": "retraining-cascade",
   "prompt": "How many steps does a single template change trigger in the retraining cascade (tree, features, model, ground truth)?",
   "answer": 4,
   "unit": "steps",
   "tolerance": 0,
   "explanation": "Rebuild the parse tree, the feature space changes, retrain the model, re-score the ground-truth set.",
   "source": "C2-template-engineering §How it works"
  },
  {
   "id": "q13",
   "type": "mcq",
   "kp": "retraining-cascade",
   "prompt": "How should the template rebuild cadence be set?",
   "choices": [
    "Fixed monthly calendar",
    "By the release train: when a release that changes the monitored components ships",
    "Only after a missed fault",
    "Daily"
   ],
   "answer": 1,
   "explanation": "Rebuild when the code that writes the monitored lines changes.",
   "source": "C2-template-engineering §How it works"
  },
  {
   "id": "q14",
   "type": "tf",
   "kp": "retraining-cascade",
   "prompt": "A template change without a ground-truth re-run can lower detection silently.",
   "answer": true,
   "explanation": "The template set is a model artefact with versions, tests, and a release process.",
   "source": "C2-template-engineering §Common confusions"
  },
  {
   "id": "q15",
   "type": "tf",
   "kp": "coverage-monitor",
   "prompt": "Unmatched lines are noise and can be ignored.",
   "answer": false,
   "explanation": "They are usually new code or a mis-masked variable; review them.",
   "source": "C2-template-engineering §Common confusions"
  },
  {
   "id": "q16",
   "type": "mcq",
   "kp": "coverage-monitor",
   "prompt": "What is the signal that templates need updating?",
   "choices": [
    "The anomaly score rises",
    "A jump in unmatched lines after a release",
    "Fewer devices report",
    "The parse tree gets deeper"
   ],
   "answer": 1,
   "explanation": "Track coverage and the unmatched bucket per release and per component.",
   "source": "C2-template-engineering §How it works"
  },
  {
   "id": "q17",
   "type": "mcq",
   "kp": "toward-automation",
   "prompt": "How are print statements extracted automatically?",
   "choices": [
    "By running Drain on source files",
    "Find logging calls, take the format string, replace format specifiers with `<*>`",
    "By diffing two log files",
    "By clustering log lines"
   ],
   "answer": 1,
   "explanation": "The source-code set then serves as the benchmark.",
   "source": "C2-template-engineering §How it works"
  },
  {
   "id": "q18",
   "type": "tf",
   "kp": "toward-automation",
   "prompt": "Before switching template approaches, compare them on the same ground-truth set.",
   "answer": true,
   "explanation": "That is the third step of the internal automation roadmap.",
   "source": "C2-template-engineering §How it works"
  }
 ]
});
