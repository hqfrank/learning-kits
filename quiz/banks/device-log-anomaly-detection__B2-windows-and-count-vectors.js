// Generated from learning/device-log-anomaly-detection/notes/B2-windows-and-count-vectors.md; numbers loaded from constants.json.
window.QUIZ_BANKS = window.QUIZ_BANKS || [];
window.QUIZ_BANKS.push({
 "topic": "device-log-anomaly-detection",
 "topicTitle": "Finding faults in a device fleet from logs and metrics",
 "section": "B2-windows-and-count-vectors",
 "sectionTitle": "B2 — Windows and log count vectors (the bag of events)",
 "notePath": "../device-log-anomaly-detection/notes/B2-windows-and-count-vectors.md",
 "knowledgePoints": {
  "window-types": {
   "title": "Fixed, sliding, and session windows",
   "summary": "Fixed windows are non-overlapping; sliding windows overlap with a step smaller than the window; session windows hold one execution path defined by an identifier.",
   "source": "B2-windows-and-count-vectors §How it works"
  },
  "session-windows": {
   "title": "Why session windows are rare on devices",
   "summary": "Session windows need an identifier such as HDFS block IDs; device logs rarely carry one, so fixed or sliding windows are the practical default.",
   "source": "B2-windows-and-count-vectors §How it works"
  },
  "count-vector": {
   "title": "Log count vectors and the event count matrix",
   "summary": "Entry j of a window's count vector is how many times template j occurred; stacking vectors gives a windows × templates matrix.",
   "source": "B2-windows-and-count-vectors §What it is"
  },
  "length-tradeoff": {
   "title": "Window length trade-off",
   "summary": "Longer windows are less sparse but dilute bursts and alarm later; shorter windows react faster but are mostly zeros and look noisy; smaller steps localise better with more correlated windows.",
   "source": "B2-windows-and-count-vectors §How it works; Common confusions"
  },
  "order-lost": {
   "title": "Counts lose order",
   "summary": "Two windows with the same multiset of events but different order are identical to a count-vector model; order faults need sequence or transition features.",
   "source": "B2-windows-and-count-vectors §Common confusions"
  },
  "feature-families": {
   "title": "Quantitative, sequential, semantic features",
   "summary": "Counts per template, ordered template IDs, or text embeddings; counts were the starting point because they are simple, explainable, and fit too-many/too-few faults.",
   "source": "B2-windows-and-count-vectors §How it works"
  },
  "window-practicalities": {
   "title": "Normalisation, overlap, partitioning",
   "summary": "Normalise identically in training and inference; overlapping sliding windows are not independent samples; partitioning by process and thread makes windows more coherent.",
   "source": "B2-windows-and-count-vectors §How it is measured or used; Common confusions"
  }
 },
 "questions": [
  {
   "id": "q1",
   "type": "mcq",
   "kp": "window-types",
   "prompt": "Which window type is defined by a window size and a smaller step size, so one line can belong to several windows?",
   "choices": [
    "Fixed window",
    "Session window",
    "Sliding window",
    "Event window"
   ],
   "answer": 2,
   "explanation": "Sliding windows overlap; they give more windows and smoother coverage.",
   "source": "B2-windows-and-count-vectors §How it works"
  },
  {
   "id": "q2",
   "type": "mcq",
   "kp": "window-types",
   "prompt": "A fault straddles a window boundary and is split in two. Which window type has this weakness most directly?",
   "choices": [
    "Fixed window",
    "Session window",
    "Sliding window",
    "None of them"
   ],
   "answer": 0,
   "explanation": "Fixed windows are consecutive and non-overlapping, so a boundary can cut a fault in half.",
   "source": "B2-windows-and-count-vectors §How it works"
  },
  {
   "id": "q3",
   "type": "tf",
   "kp": "window-types",
   "prompt": "He et al. (2016) report that sliding windows can reach higher accuracy than fixed windows.",
   "answer": true,
   "explanation": "That is their Finding 2; they also find window and step size affect supervised and unsupervised methods differently.",
   "source": "B2-windows-and-count-vectors §How it works"
  },
  {
   "id": "q4",
   "type": "numeric",
   "kp": "window-types",
   "prompt": "One device-day of 24 h is cut into sliding windows of 1 h with a 15 min step. How many windows result, using (day − window) ÷ step + 1?",
   "answer": 93,
   "unit": "windows",
   "tolerance": 0,
   "explanation": "(24 − 1) ÷ 0.25 + 1 = 93. Illustrative inputs.",
   "source": "B2-windows-and-count-vectors §How it works"
  },
  {
   "id": "q5",
   "type": "mcq",
   "kp": "session-windows",
   "prompt": "Why are session windows rarely usable for device logs?",
   "choices": [
    "Device logs are too short",
    "Device logs rarely carry an identifier that defines one execution path",
    "Sessions overlap too much",
    "Session windows cannot be counted"
   ],
   "answer": 1,
   "explanation": "In HDFS each block ID defines a session; device logs lack such an ID, so fixed or sliding windows are the default.",
   "source": "B2-windows-and-count-vectors §How it works"
  },
  {
   "id": "q6",
   "type": "numeric",
   "kp": "session-windows",
   "prompt": "He et al. built 575,061 HDFS session count vectors, of which 16,838 are labelled anomalies. What percentage is anomalous?",
   "answer": 2.93,
   "unit": "%",
   "tolerance": 0.05,
   "explanation": "16,838 ÷ 575,061 ≈ 2.93 % (He et al. 2016, §IV-A).",
   "source": "B2-windows-and-count-vectors §How it works"
  },
  {
   "id": "q7",
   "type": "mcq",
   "kp": "count-vector",
   "prompt": "In a window's log count vector, what is entry *j*?",
   "choices": [
    "The position of template j in the window",
    "The number of times template j appeared in the window",
    "Whether template j is an error",
    "The parameter value of template j"
   ],
   "answer": 1,
   "explanation": "A count vector is a bag of events: frequency kept, order lost.",
   "source": "B2-windows-and-count-vectors §What it is"
  },
  {
   "id": "q8",
   "type": "mcq",
   "kp": "count-vector",
   "prompt": "What are the rows and columns of the event count matrix?",
   "choices": [
    "Templates × devices",
    "Windows × templates",
    "Devices × days",
    "Templates × parameters"
   ],
   "answer": 1,
   "explanation": "One row per window, one column per template (He et al. 2016, §III-C).",
   "source": "B2-windows-and-count-vectors §What it is"
  },
  {
   "id": "q9",
   "type": "mcq",
   "kp": "length-tradeoff",
   "prompt": "What happens when you make windows **longer**?",
   "choices": [
    "Vectors get sparser and alarms come sooner",
    "Vectors get less sparse, but short bursts are diluted and the earliest alarm comes later",
    "Nothing changes except speed",
    "Order information is recovered"
   ],
   "answer": 1,
   "explanation": "Longer windows collect more lines, which helps frequency changes stand out but hurts reaction time and burst visibility.",
   "source": "B2-windows-and-count-vectors §How it works"
  },
  {
   "id": "q10",
   "type": "tf",
   "kp": "length-tradeoff",
   "prompt": "With very short windows most count entries are zero, and normal variation between windows looks large.",
   "answer": true,
   "explanation": "That is the cost of fast reaction and fine time localisation.",
   "source": "B2-windows-and-count-vectors §How it works"
  },
  {
   "id": "q11",
   "type": "tf",
   "kp": "length-tradeoff",
   "prompt": "Window size is a tuning detail that does not affect which faults are visible.",
   "answer": false,
   "explanation": "It decides which faults are visible at all and how quickly an alarm can fire; set it from the fault classes you care about.",
   "source": "B2-windows-and-count-vectors §Common confusions"
  },
  {
   "id": "q12",
   "type": "mcq",
   "kp": "order-lost",
   "prompt": "Two windows contain the same events in a different order. How does a count-vector model see them?",
   "choices": [
    "As very different",
    "As identical",
    "As one normal and one anomalous",
    "It cannot score them"
   ],
   "answer": 1,
   "explanation": "`connect → good → ping → done` and a reordered window can share a vector; ordering faults need sequence or transition features.",
   "source": "B2-windows-and-count-vectors §Common confusions"
  },
  {
   "id": "q13",
   "type": "tf",
   "kp": "order-lost",
   "prompt": "A count-vector model reliably detects faults that appear only after a specific earlier order of events.",
   "answer": false,
   "explanation": "Count vectors keep frequency, not order; stateful faults need sequence features or transition counts (B5).",
   "source": "B2-windows-and-count-vectors §Common confusions"
  },
  {
   "id": "q14",
   "type": "multi",
   "kp": "feature-families",
   "prompt": "Which feature families does the note name?",
   "choices": [
    "Quantitative (counts per template)",
    "Spectral (frequency of log bursts)",
    "Sequential (ordered template IDs)",
    "Semantic (embeddings of template text)"
   ],
   "answer": [
    0,
    2,
    3
   ],
   "explanation": "The taxonomy is quantitative, sequential, and semantic.",
   "source": "B2-windows-and-count-vectors §How it works"
  },
  {
   "id": "q15",
   "type": "mcq",
   "kp": "feature-families",
   "prompt": "Why were count vectors the starting point in the internal design?",
   "choices": [
    "They capture event order",
    "They are simple, explainable per template, and adequate for too-many/too-few faults",
    "They need no parsing",
    "They are the only option for isolation forests"
   ],
   "answer": 1,
   "explanation": "Each column is a template an engineer can read, which makes results easy to explain.",
   "source": "B2-windows-and-count-vectors §How it works"
  },
  {
   "id": "q16",
   "type": "tf",
   "kp": "window-practicalities",
   "prompt": "Rows from a sliding window can be counted as independent samples when estimating error rates.",
   "answer": false,
   "explanation": "Neighbouring sliding windows overlap and are correlated; more rows is not more independent data.",
   "source": "B2-windows-and-count-vectors §Common confusions"
  },
  {
   "id": "q17",
   "type": "mcq",
   "kp": "window-practicalities",
   "prompt": "Whatever normalisation of raw counts is chosen, what must be true of it?",
   "choices": [
    "It is a log transform",
    "It is identical in training and inference",
    "It removes zero entries",
    "It is per device"
   ],
   "answer": 1,
   "explanation": "Raw counts favour busy windows; any fix must be applied the same way at train and inference time.",
   "source": "B2-windows-and-count-vectors §How it is measured or used"
  },
  {
   "id": "q18",
   "type": "mcq",
   "kp": "window-practicalities",
   "prompt": "Why partition the stream by process and thread before windowing?",
   "choices": [
    "To reduce template count",
    "To make each window more coherent despite interleaving",
    "To align with metric days",
    "To remove parameters"
   ],
   "answer": 1,
   "explanation": "Interleaved writers mix unrelated lines; partitioning separates them (B5).",
   "source": "B2-windows-and-count-vectors §How it is measured or used"
  }
 ]
});
