// Generated from learning/device-log-anomaly-detection/notes/B3-anomaly-detection-on-logs.md; numbers loaded from constants.json.
window.QUIZ_BANKS = window.QUIZ_BANKS || [];
window.QUIZ_BANKS.push({
 "topic": "device-log-anomaly-detection",
 "topicTitle": "Finding faults in a device fleet from logs and metrics",
 "section": "B3-anomaly-detection-on-logs",
 "sectionTitle": "B3 — Anomaly detection on logs: isolation forest, and sequence models on the device",
 "notePath": "../device-log-anomaly-detection/notes/B3-anomaly-detection-on-logs.md",
 "knowledgePoints": {
  "why-unsupervised": {
   "title": "Why unsupervised, not rules or a classifier",
   "summary": "Rules find only foreseen faults and break when print statements change; a supervised classifier needs many labelled faults, which fleets lack; unsupervised detection needs only normal data but does not name the cause.",
   "source": "B3-anomaly-detection-on-logs §How it works"
  },
  "iforest-idea": {
   "title": "Isolation forest: few and different",
   "summary": "An isolation tree splits on a random feature at a random value between its min and max; anomalies are isolated after few splits, so they have short path lengths.",
   "source": "B3-anomaly-detection-on-logs §What it is"
  },
  "iforest-score": {
   "title": "The score s(x) = 2^(−E(h)/c(ψ))",
   "summary": "The expected path length is normalised by c(ψ); E(h) = c gives 0.5, scores near 1 are anomalies, and the score is a normalised path length, not a fault probability.",
   "source": "B3-anomaly-detection-on-logs §How it works; Common confusions"
  },
  "iforest-defaults": {
   "title": "Defaults: ψ = 256, t = 100",
   "summary": "Each tree is built on 256 sub-sampled points, the forest has 100 trees, and the height limit is ⌈log₂ ψ⌉ = 8; c(256) ≈ 10.24.",
   "source": "B3-anomaly-detection-on-logs §How it works"
  },
  "contamination": {
   "title": "Contamination is a choice",
   "summary": "Contamination sets the threshold so that fraction of training data is flagged; it is a decision about how many alarms you want, not a property of the data.",
   "source": "B3-anomaly-detection-on-logs §How it works; Common confusions"
  },
  "training-data": {
   "title": "Train on healthy windows; sparse vectors",
   "summary": "Train on windows of devices believed healthy, because faults in training teach the forest they are normal; on sparse event-triggered vectors random splits isolate non-zero values quickly.",
   "source": "B3-anomaly-detection-on-logs §How it works; Common confusions"
  },
  "sequence-models": {
   "title": "Sequence models and the trade-off",
   "summary": "DeepLog's LSTM predicts the next template from the last h and calls it normal if it is in the top g; sequence models see order but cost more; the design used a sequence model on the device and a forest in the cloud.",
   "source": "B3-anomaly-detection-on-logs §How it works; Common confusions"
  },
  "feature-importance": {
   "title": "Explaining a score",
   "summary": "Isolation forest has no native per-point importance; the simplest proxy shows the window's unusual counts; DIFFI and Shapley-value attributions exist.",
   "source": "B3-anomaly-detection-on-logs §How it is measured or used"
  }
 },
 "questions": [
  {
   "id": "q1",
   "type": "mcq",
   "kp": "why-unsupervised",
   "prompt": "Why is a supervised classifier not an option for production device logs?",
   "choices": [
    "It cannot handle count vectors",
    "It needs many labelled faults, and fleets have almost none",
    "It is too slow at inference",
    "It cannot be retrained"
   ],
   "answer": 1,
   "explanation": "Supervised methods score best on labelled benchmarks (He et al. 2016, Finding 3), but labels are what fleets lack.",
   "source": "B3-anomaly-detection-on-logs §How it works"
  },
  {
   "id": "q2",
   "type": "mcq",
   "kp": "why-unsupervised",
   "prompt": "What is the main weakness of rule-based (regular-expression) detection?",
   "choices": [
    "It is imprecise for known faults",
    "It finds only what was foreseen and breaks when print statements change",
    "It needs labelled data",
    "It cannot name a cause"
   ],
   "answer": 1,
   "explanation": "Rules are precise and name the cause, but only for faults someone anticipated; they are kept as a complement.",
   "source": "B3-anomaly-detection-on-logs §How it works"
  },
  {
   "id": "q3",
   "type": "tf",
   "kp": "why-unsupervised",
   "prompt": "Unsupervised anomaly detection names the root cause of each flagged window.",
   "answer": false,
   "explanation": "It flags what differs from normal, including environmental anomalies; naming the cause is root-cause analysis (B5).",
   "source": "B3-anomaly-detection-on-logs §How it works"
  },
  {
   "id": "q4",
   "type": "mcq",
   "kp": "iforest-idea",
   "prompt": "Why do anomalies get short path lengths in an isolation tree?",
   "choices": [
    "They have more features",
    "They are few and different, so random splits isolate them quickly",
    "They are always at the root",
    "Trees are trained on anomalies"
   ],
   "answer": 1,
   "explanation": "Like twenty questions with random questions: the odd one out is named after very few.",
   "source": "B3-anomaly-detection-on-logs §What it is"
  },
  {
   "id": "q5",
   "type": "tf",
   "kp": "iforest-idea",
   "prompt": "An isolation tree picks a random feature and a random split value between that feature's minimum and maximum.",
   "answer": true,
   "explanation": "It repeats on each side until each point is alone or the height limit is reached.",
   "source": "B3-anomaly-detection-on-logs §What it is"
  },
  {
   "id": "q6",
   "type": "numeric",
   "kp": "iforest-score",
   "prompt": "What is the isolation-forest score s(x) when the expected path length equals c(ψ)?",
   "answer": 0.5,
   "unit": "",
   "tolerance": 0.01,
   "explanation": "s = 2^(−c/c) = 2^(−1) = 0.5 (Liu et al. 2008, §2).",
   "source": "B3-anomaly-detection-on-logs §How it works"
  },
  {
   "id": "q7",
   "type": "numeric",
   "kp": "iforest-score",
   "prompt": "With ψ = 256, c(ψ) ≈ 10.24. A window is isolated after an average of 3 splits. What is s = 2^(−3/10.24)?",
   "answer": 0.82,
   "unit": "",
   "tolerance": 0.01,
   "explanation": "2^(−3/10.24) ≈ 0.82: easy to isolate, so anomalous.",
   "source": "B3-anomaly-detection-on-logs §How it works"
  },
  {
   "id": "q8",
   "type": "tf",
   "kp": "iforest-score",
   "prompt": "A score of 0.82 means the window is 82 % likely to contain a bug.",
   "answer": false,
   "explanation": "The score is a normalised path length meaning \"easy to isolate\", not a probability of a fault.",
   "source": "B3-anomaly-detection-on-logs §Common confusions"
  },
  {
   "id": "q9",
   "type": "mcq",
   "kp": "iforest-score",
   "prompt": "Every point in a sample scores about 0.5. What does that mean?",
   "choices": [
    "All points are anomalies",
    "The sample has no distinct anomaly",
    "The forest has too few trees",
    "Contamination is set too high"
   ],
   "answer": 1,
   "explanation": "Scores near 1 are anomalies; if everything scores ≈ 0.5 nothing stands out (Liu et al. 2008, §2).",
   "source": "B3-anomaly-detection-on-logs §How it works"
  },
  {
   "id": "q10",
   "type": "numeric",
   "kp": "iforest-defaults",
   "prompt": "Each isolation tree is built on ψ = 256 points. What is its height limit ⌈log₂ ψ⌉?",
   "answer": 8,
   "unit": "splits",
   "tolerance": 0,
   "explanation": "log₂ 256 = 8.",
   "source": "B3-anomaly-detection-on-logs §How it works"
  },
  {
   "id": "q11",
   "type": "mcq",
   "kp": "iforest-defaults",
   "prompt": "What is the default number of trees in an isolation forest (paper and scikit-learn)?",
   "choices": [
    "10",
    "100",
    "256",
    "1000"
   ],
   "answer": 1,
   "explanation": "t = 100 trees; ψ = 256 is the sub-sample size per tree, a common confusion.",
   "source": "B3-anomaly-detection-on-logs §How it works"
  },
  {
   "id": "q12",
   "type": "mcq",
   "kp": "contamination",
   "prompt": "What does a numeric `contamination` value do in scikit-learn's IsolationForest?",
   "choices": [
    "Estimates the true anomaly rate",
    "Sets the threshold so that fraction of training data is flagged",
    "Sets the number of trees",
    "Removes anomalies from training data"
   ],
   "answer": 1,
   "explanation": "Contamination is a decision about how many alarms you want.",
   "source": "B3-anomaly-detection-on-logs §How it works"
  },
  {
   "id": "q13",
   "type": "tf",
   "kp": "contamination",
   "prompt": "Contamination is the true anomaly rate of the data.",
   "answer": false,
   "explanation": "You set it; change it and the alarm count changes, while the data do not.",
   "source": "B3-anomaly-detection-on-logs §Common confusions"
  },
  {
   "id": "q14",
   "type": "mcq",
   "kp": "training-data",
   "prompt": "What goes wrong if the forest is trained on all data, including many faulty devices?",
   "choices": [
    "Training is slower but results are the same",
    "The forest learns that faults are normal",
    "The score exceeds 1",
    "Contamination becomes zero"
   ],
   "answer": 1,
   "explanation": "Filter out obviously unhealthy devices first; train on windows from devices believed healthy.",
   "source": "B3-anomaly-detection-on-logs §Common confusions"
  },
  {
   "id": "q15",
   "type": "mcq",
   "kp": "training-data",
   "prompt": "Per-device-day metric vectors are very sparse. How do random splits behave on them?",
   "choices": [
    "They never isolate anything",
    "They isolate a non-zero value quickly, which is the desired behaviour",
    "They require dense imputation first",
    "They ignore zero features"
   ],
   "answer": 1,
   "explanation": "Event-triggered metrics make vectors mostly zero; a non-zero value stands out. Zero-inflated models are an alternative worth testing.",
   "source": "B3-anomaly-detection-on-logs §How it works"
  },
  {
   "id": "q16",
   "type": "mcq",
   "kp": "sequence-models",
   "prompt": "How does DeepLog decide that the next log event is normal?",
   "choices": [
    "Its count is below a threshold",
    "It is among the top *g* templates the LSTM predicts",
    "Its path length is long",
    "It matches a regular expression"
   ],
   "answer": 1,
   "explanation": "The LSTM reads the last *h* template IDs and predicts a probability for each possible next template.",
   "source": "B3-anomaly-detection-on-logs §How it works"
  },
  {
   "id": "q17",
   "type": "numeric",
   "kp": "sequence-models",
   "prompt": "What is DeepLog's default *g* in its top-*g* rule?",
   "answer": 9,
   "unit": "candidates",
   "tolerance": 0,
   "explanation": "Defaults: g = 9, h = 10, L = 2 layers, α = 64 units (Du et al. 2017, §5.1.3).",
   "source": "B3-anomaly-detection-on-logs §How it works"
  },
  {
   "id": "q18",
   "type": "multi",
   "kp": "sequence-models",
   "prompt": "Which statements match the note's trade-off between the two model families?",
   "choices": [
    "A sequence model detects order faults and flags the line where the sequence goes wrong",
    "A count-vector forest is cheap to train and easy to explain but ignores order",
    "An LSTM is always better because it sees order",
    "The internal design used a sequence model on the device and a forest in the cloud"
   ],
   "answer": [
    0,
    1,
    3
   ],
   "explanation": "An LSTM needs more data and compute and careful handling of new templates; it is not always better.",
   "source": "B3-anomaly-detection-on-logs §How it works; Common confusions"
  },
  {
   "id": "q19",
   "type": "mcq",
   "kp": "feature-importance",
   "prompt": "Isolation forest has no native per-point feature importance. What is the simplest proxy the note names?",
   "choices": [
    "The tree depth",
    "Showing the window's unusual counts",
    "The contamination value",
    "The number of trees that split on a feature"
   ],
   "answer": 1,
   "explanation": "Model-specific methods such as DIFFI and model-agnostic Shapley-value attributions go further.",
   "source": "B3-anomaly-detection-on-logs §How it is measured or used"
  },
  {
   "id": "q20",
   "type": "tf",
   "kp": "feature-importance",
   "prompt": "DIFFI is a model-specific feature-importance method for isolation forests.",
   "answer": true,
   "explanation": "Carletti, Terzi, Susto, 2020; the note lists it next to Shapley-value attributions.",
   "source": "B3-anomaly-detection-on-logs §How it is measured or used"
  }
 ]
});
