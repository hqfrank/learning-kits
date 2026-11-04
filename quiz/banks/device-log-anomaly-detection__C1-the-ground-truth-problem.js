// Generated from learning/device-log-anomaly-detection/notes/C1-the-ground-truth-problem.md; numbers loaded from constants.json.
window.QUIZ_BANKS = window.QUIZ_BANKS || [];
window.QUIZ_BANKS.push({
 "topic": "device-log-anomaly-detection",
 "topicTitle": "Finding faults in a device fleet from logs and metrics",
 "section": "C1-the-ground-truth-problem",
 "sectionTitle": "C1 — The ground-truth problem: how to evaluate a detector with almost no labels",
 "notePath": "../device-log-anomaly-detection/notes/C1-the-ground-truth-problem.md",
 "knowledgePoints": {
  "gt-sources": {
   "title": "Where ground truth comes from",
   "summary": "Lab-induced faults (known fault and time, often wrong log format), resolved user reports (need a production-format log, an identified bug, and a closed ticket), and weaker labels; only a fraction of candidates qualify.",
   "source": "C1-the-ground-truth-problem §How it works; Common confusions"
  },
  "backward-forward": {
   "title": "Backward versus forward validation",
   "summary": "Backward validation shows the detector can find known faults; a forward pilot asks experts whether its output alone is enough to start on an unknown one.",
   "source": "C1-the-ground-truth-problem §How it works; Common confusions"
  },
  "confusion-matrix": {
   "title": "Confusion matrix and rates",
   "summary": "Detection rate (recall) = TP ÷ (TP + FN); precision = TP ÷ (TP + FP); false-alarm rate among flags = FP ÷ (TP + FP) = 1 − precision.",
   "source": "C1-the-ground-truth-problem §How it works"
  },
  "intervals": {
   "title": "Report the rate with its interval",
   "summary": "With 10 cases a 60 % detection rate has a 95 % Wilson interval of about 31–83 %; the Wald interval misbehaves; 100 cases narrow it to about 50–69 %.",
   "source": "C1-the-ground-truth-problem §How it works; Common confusions"
  },
  "far-beside-dr": {
   "title": "False alarms beside detection",
   "summary": "A detector that flags everything has 100 % detection; the detection rate means nothing without its false-alarm cost.",
   "source": "C1-the-ground-truth-problem §How it works"
  },
  "misses-and-cycle": {
   "title": "Misses, time-ordered validation, two KPIs",
   "summary": "Classify misses as fixable or unfixable; validate with time-ordered cross-validation; track the anomaly rate and the false-negative rate on known faults.",
   "source": "C1-the-ground-truth-problem §How it works"
  }
 },
 "questions": [
  {
   "id": "q1",
   "type": "mcq",
   "kp": "gt-sources",
   "prompt": "What is the typical weakness of lab-induced faults as ground truth?",
   "choices": [
    "The fault and its time are unknown",
    "Their logs are often in a test-framework format rather than the production format",
    "They are never stateful",
    "They are too numerous"
   ],
   "answer": 1,
   "explanation": "Lab cases are clean on the fault but often in the wrong format, and often stateful sequences production devices rarely hit.",
   "source": "C1-the-ground-truth-problem §Common confusions"
  },
  {
   "id": "q2",
   "type": "multi",
   "kp": "gt-sources",
   "prompt": "What does a resolved user report need to qualify as a ground-truth case?",
   "choices": [
    "A production-format log for the right time range",
    "An identified bug",
    "A closed ticket with the cause",
    "A lab reproduction",
    "A label from a supervised classifier"
   ],
   "answer": [
    0,
    1,
    2
   ],
   "explanation": "Only a fraction of reports have all three.",
   "source": "C1-the-ground-truth-problem §How it works"
  },
  {
   "id": "q3",
   "type": "numeric",
   "kp": "gt-sources",
   "prompt": "In an illustrative funnel, 60 candidate cases yield 10 usable ones. What percentage is usable?",
   "answer": 16.7,
   "unit": "%",
   "tolerance": 0.5,
   "explanation": "10 ÷ 60 ≈ 16.7 %; illustrative counts.",
   "source": "C1-the-ground-truth-problem §How it works"
  },
  {
   "id": "q4",
   "type": "mcq",
   "kp": "backward-forward",
   "prompt": "What does backward validation prove?",
   "choices": [
    "That output alone is enough to start an investigation",
    "That the detector can flag known faults on the same logs",
    "That false alarms are low",
    "That the model generalises to new releases"
   ],
   "answer": 1,
   "explanation": "It starts from a known fault and checks the detector flags the same device and snippet.",
   "source": "C1-the-ground-truth-problem §How it works"
  },
  {
   "id": "q5",
   "type": "tf",
   "kp": "backward-forward",
   "prompt": "Backward validation is sufficient to show the detector is useful on unknown faults.",
   "answer": false,
   "explanation": "It is necessary, not sufficient; forward usefulness is a separate question answered by a forward pilot.",
   "source": "C1-the-ground-truth-problem §Common confusions"
  },
  {
   "id": "q6",
   "type": "mcq",
   "kp": "backward-forward",
   "prompt": "In a forward pilot, which question do experts answer first?",
   "choices": [
    "Was the right anomaly flagged?",
    "Is the output sufficient to start?",
    "What is missing?",
    "What is the root cause?"
   ],
   "answer": 1,
   "explanation": "Order: sufficient to start? what is missing? was the right anomaly flagged? Confirmed anomalies go to RCA.",
   "source": "C1-the-ground-truth-problem §How it works"
  },
  {
   "id": "q7",
   "type": "mcq",
   "kp": "confusion-matrix",
   "prompt": "Which formula is the detection rate (recall)?",
   "choices": [
    "TP ÷ (TP + FP)",
    "TP ÷ (TP + FN)",
    "FP ÷ (FP + TN)",
    "TN ÷ (TN + FN)"
   ],
   "answer": 1,
   "explanation": "TP ÷ (TP + FP) is precision.",
   "source": "C1-the-ground-truth-problem §How it works"
  },
  {
   "id": "q8",
   "type": "mcq",
   "kp": "confusion-matrix",
   "prompt": "The false-alarm rate as the share of flags that are not device faults equals what?",
   "choices": [
    "1 − recall",
    "1 − precision",
    "FN ÷ (TP + FN)",
    "TN ÷ (FP + TN)"
   ],
   "answer": 1,
   "explanation": "FP ÷ (TP + FP) = 1 − precision; per window it can also be FP ÷ (FP + TN).",
   "source": "C1-the-ground-truth-problem §How it works"
  },
  {
   "id": "q9",
   "type": "numeric",
   "kp": "confusion-matrix",
   "prompt": "In an illustrative pilot of 10 tickets, 4 were environmental. Counting those as false positives and the rest as true, what is the precision?",
   "answer": 60,
   "unit": "%",
   "tolerance": 1,
   "explanation": "(10 − 4) ÷ 10 = 60 %.",
   "source": "C1-the-ground-truth-problem §How it works"
  },
  {
   "id": "q10",
   "type": "mcq",
   "kp": "intervals",
   "prompt": "The detector catches 6 of 10 ground-truth cases. Which is the approximate 95 % Wilson score interval?",
   "choices": [
    "31–83 %",
    "30–90 %",
    "50–69 %",
    "55–65 %"
   ],
   "answer": 0,
   "explanation": "About 31–83 %; the Wald interval 30–90 % is too wide at the top, and 50–69 % is for 100 cases.",
   "source": "C1-the-ground-truth-problem §How it works"
  },
  {
   "id": "q11",
   "type": "mcq",
   "kp": "intervals",
   "prompt": "With 100 cases and the same 60 % rate, roughly how wide does the Wilson interval become?",
   "choices": [
    "About 31–83 %",
    "About 50–69 %",
    "About 59–61 %",
    "It does not change"
   ],
   "answer": 1,
   "explanation": "More cases narrow the interval, roughly with √n.",
   "source": "C1-the-ground-truth-problem §How it works"
  },
  {
   "id": "q12",
   "type": "tf",
   "kp": "intervals",
   "prompt": "6 of 10 cases detected supports the claim that the method beats another method that scored 50 %.",
   "answer": false,
   "explanation": "Ten cases support \"the method works\", not a comparison: the interval is about ±25 percentage points.",
   "source": "C1-the-ground-truth-problem §Common confusions"
  },
  {
   "id": "q13",
   "type": "tf",
   "kp": "far-beside-dr",
   "prompt": "A detector that flags every window has a detection rate of 100 %.",
   "answer": true,
   "explanation": "That is why the detection rate must be reported with its false-alarm rate.",
   "source": "C1-the-ground-truth-problem §How it works"
  },
  {
   "id": "q14",
   "type": "mcq",
   "kp": "far-beside-dr",
   "prompt": "Why must the false-alarm rate sit next to the detection rate?",
   "choices": [
    "It is easier to compute",
    "The detection rate alone can be maximised by flagging everything",
    "Ground truth gives no false alarms",
    "They are always equal"
   ],
   "answer": 1,
   "explanation": "Detection without its cost in false alarms is meaningless.",
   "source": "C1-the-ground-truth-problem §How it works"
  },
  {
   "id": "q15",
   "type": "mcq",
   "kp": "misses-and-cycle",
   "prompt": "What is a **fixable** miss?",
   "choices": [
    "A miss caused by a parser crash",
    "One that more signal (components, kernel logs, metrics) would have caught",
    "One the fault leaves no trace of",
    "A false alarm"
   ],
   "answer": 1,
   "explanation": "Unfixable misses leave no trace in the signals; fixable misses become the roadmap (C4).",
   "source": "C1-the-ground-truth-problem §How it works"
  },
  {
   "id": "q16",
   "type": "mcq",
   "kp": "misses-and-cycle",
   "prompt": "What does time-ordered cross-validation do?",
   "choices": [
    "Shuffles windows randomly",
    "Trains on earlier periods and validates on later ones, then rolls the split forward",
    "Validates on the oldest faults",
    "Uses the same data for both"
   ],
   "answer": 1,
   "explanation": "Never validate on faults older than the training data.",
   "source": "C1-the-ground-truth-problem §How it works"
  },
  {
   "id": "q17",
   "type": "multi",
   "kp": "misses-and-cycle",
   "prompt": "Which are the two headline KPIs for fast iteration on a historical ground-truth set?",
   "choices": [
    "The anomaly rate (a proxy for false alarms)",
    "The number of templates",
    "The false-negative rate on known faults",
    "Training time"
   ],
   "answer": [
    0,
    2
   ],
   "explanation": "Together they guard against a model that catches more by alarming more.",
   "source": "C1-the-ground-truth-problem §How it works"
  }
 ]
});
