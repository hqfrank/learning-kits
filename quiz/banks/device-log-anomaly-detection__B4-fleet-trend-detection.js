// Generated from learning/device-log-anomaly-detection/notes/B4-fleet-trend-detection.md; numbers loaded from constants.json.
window.QUIZ_BANKS = window.QUIZ_BANKS || [];
window.QUIZ_BANKS.push({
 "topic": "device-log-anomaly-detection",
 "topicTitle": "Finding faults in a device fleet from logs and metrics",
 "section": "B4-fleet-trend-detection",
 "sectionTitle": "B4 — Fleet trend detection: weighted least squares on a share of devices",
 "notePath": "../device-log-anomaly-detection/notes/B4-fleet-trend-detection.md",
 "knowledgePoints": {
  "why-not-ols": {
   "title": "Why OLS is wrong here",
   "summary": "Var(p̂ₜ) = p(1 − p)/nₜ changes as nₜ changes, so the errors are heteroscedastic; OLS gives a noisy day as much say as a precise one and its slope standard error is wrong.",
   "source": "B4-fleet-trend-detection §How it works"
  },
  "wls-weights": {
   "title": "WLS weights and what they change",
   "summary": "Weight each day by wₜ = nₜ / (p̂ₜ(1 − p̂ₜ)); with correct weights WLS is BLUE; it often changes the slope little but changes the standard error and p-value. p̂ = 0 or 1 needs a pooled p̄ or a floor.",
   "source": "B4-fleet-trend-detection §How it works; Common confusions"
  },
  "practical-threshold": {
   "title": "Test against a practical threshold s",
   "summary": "With enough devices every slope is significant, so test H₀: β = s, where s is the smallest slope worth an engineer's time; the p-value is one-sided.",
   "source": "B4-fleet-trend-detection §How it works; Common confusions"
  },
  "phred-score": {
   "title": "Phred-style score",
   "summary": "score = −10·log₁₀(p), capped (illustrative 100); each 10 points is a factor of 10 in p; it is a confidence, not a severity.",
   "source": "B4-fleet-trend-detection §How it works; Common confusions"
  },
  "direction-variants": {
   "title": "Direction filter and three daily models",
   "summary": "Good-direction changes are dropped by a rule table; the design ran time-based, attribute-based, and distribution-based (chi-square) models.",
   "source": "B4-fleet-trend-detection §How it works"
  },
  "family-vs-device": {
   "title": "Family level versus device level",
   "summary": "A WLS slope test on the family share catches fleet-wide regressions with few high-impact reports; an isolation forest on device-days catches odd devices with many lower-impact, often environmental reports.",
   "source": "B4-fleet-trend-detection §How it works"
  },
  "multiple-testing": {
   "title": "Multiple testing, autocorrelation, gaps",
   "summary": "Testing many series at a fixed p produces chance alarms (control FDR or rank); correlated residuals make se(β̂) too small; missing days can look like steps.",
   "source": "B4-fleet-trend-detection §How it is measured or used"
  }
 },
 "questions": [
  {
   "id": "q1",
   "type": "mcq",
   "kp": "why-not-ols",
   "prompt": "Why is ordinary least squares the wrong fit for a daily share-of-devices series?",
   "choices": [
    "The series is not linear",
    "Its variance p(1 − p)/nₜ changes as the number of active devices changes",
    "OLS cannot fit 56 points",
    "OLS requires integer data"
   ],
   "answer": 1,
   "explanation": "Weekends, outages, and new cohorts change nₜ, so the errors are heteroscedastic.",
   "source": "B4-fleet-trend-detection §How it works"
  },
  {
   "id": "q2",
   "type": "tf",
   "kp": "why-not-ols",
   "prompt": "When nₜ varies from day to day, the OLS slope standard error is still valid.",
   "answer": false,
   "explanation": "OLS assumes homoscedastic errors; with varying nₜ its standard error is wrong.",
   "source": "B4-fleet-trend-detection §How it works"
  },
  {
   "id": "q3",
   "type": "mcq",
   "kp": "wls-weights",
   "prompt": "Which weight does WLS give day *t*?",
   "choices": [
    "wₜ = nₜ",
    "wₜ = 1 / nₜ",
    "wₜ = nₜ / (p̂ₜ(1 − p̂ₜ))",
    "wₜ = p̂ₜ(1 − p̂ₜ)"
   ],
   "answer": 2,
   "explanation": "The weight is the inverse variance of p̂ₜ; with correct weights the WLS slope is the best linear unbiased estimator.",
   "source": "B4-fleet-trend-detection §How it works"
  },
  {
   "id": "q4",
   "type": "tf",
   "kp": "wls-weights",
   "prompt": "Switching from OLS to WLS often changes the slope only a little; its main effect is on the standard error and therefore the p-value.",
   "answer": true,
   "explanation": "The alarm uses the p-value, so the standard error is what matters.",
   "source": "B4-fleet-trend-detection §Common confusions"
  },
  {
   "id": "q5",
   "type": "mcq",
   "kp": "wls-weights",
   "prompt": "On some days p̂ₜ = 0, which makes the weight infinite. What does the note suggest?",
   "choices": [
    "Delete those days",
    "Use a pooled p̄ across the window in the variance, or a small floor",
    "Set the weight to 1",
    "Switch back to OLS"
   ],
   "answer": 1,
   "explanation": "This handling is the note's own suggestion; the source does not state one.",
   "source": "B4-fleet-trend-detection §How it works"
  },
  {
   "id": "q6",
   "type": "mcq",
   "kp": "practical-threshold",
   "prompt": "Why test H₀: β = *s* rather than β = 0?",
   "choices": [
    "β = 0 cannot be computed",
    "With enough devices every slope is significant; *s* asks whether the change is worth acting on",
    "*s* makes the test two-sided",
    "It removes the need for weights"
   ],
   "answer": 1,
   "explanation": "A slope of exactly zero is never true for a real fleet.",
   "source": "B4-fleet-trend-detection §Common confusions"
  },
  {
   "id": "q7",
   "type": "mcq",
   "kp": "practical-threshold",
   "prompt": "What is the practical threshold *s*?",
   "choices": [
    "The slope of the previous release",
    "The smallest slope worth an engineer's time",
    "The p-value cut-off",
    "The OLS slope"
   ],
   "answer": 1,
   "explanation": "It is the null-hypothesis value; the one-sided p-value is 1 − Φ((β̂ − s)/se(β̂)).",
   "source": "B4-fleet-trend-detection §How it works"
  },
  {
   "id": "q8",
   "type": "numeric",
   "kp": "phred-score",
   "prompt": "Using score = −10·log₁₀(p), what score does p = 10⁻⁵ give?",
   "answer": 50,
   "unit": "",
   "tolerance": 0,
   "explanation": "−10 × (−5) = 50.",
   "source": "B4-fleet-trend-detection §How it works"
  },
  {
   "id": "q9",
   "type": "numeric",
   "kp": "phred-score",
   "prompt": "On the Phred-style scale, an extra 10 score points corresponds to p being smaller by what factor?",
   "answer": 10,
   "unit": "×",
   "tolerance": 0,
   "explanation": "score = −10·log₁₀(p), so each 10 points is one decade of p (Ewing & Green 1998).",
   "source": "B4-fleet-trend-detection §How it works"
  },
  {
   "id": "q10",
   "type": "tf",
   "kp": "phred-score",
   "prompt": "The trend score measures how severe the problem is for customers.",
   "answer": false,
   "explanation": "It is a confidence that the slope exceeds *s*; severity also depends on how many devices are affected and how bad the event is (B6).",
   "source": "B4-fleet-trend-detection §Common confusions"
  },
  {
   "id": "q11",
   "type": "mcq",
   "kp": "direction-variants",
   "prompt": "The trend test finds that disconnects are falling significantly. What happens?",
   "choices": [
    "A high-priority ticket is opened",
    "The direction filter drops it as a good-direction change",
    "It is sent to the device-level model",
    "The score is doubled"
   ],
   "answer": 1,
   "explanation": "A small table of (feature, category, direction) rules drops improvements.",
   "source": "B4-fleet-trend-detection §How it works"
  },
  {
   "id": "q12",
   "type": "mcq",
   "kp": "direction-variants",
   "prompt": "Which daily model asks whether the distribution over reason codes differs for group X, and with what standard tool?",
   "choices": [
    "Time-based; WLS slope",
    "Attribute-based; t-test",
    "Distribution-based; chi-square test",
    "Device-based; isolation forest"
   ],
   "answer": 2,
   "explanation": "Distribution-based tests compare category distributions; chi-square is the standard tool.",
   "source": "B4-fleet-trend-detection §How it works"
  },
  {
   "id": "q13",
   "type": "multi",
   "kp": "direction-variants",
   "prompt": "Which three daily models did the design run?",
   "choices": [
    "Time-based (slope over time)",
    "Attribute-based (group X versus the rest)",
    "Sequence-based (LSTM on metrics)",
    "Distribution-based (categories for group X)",
    "Frequency-domain (weekly spectrum)"
   ],
   "answer": [
    0,
    1,
    3
   ],
   "explanation": "Each runs on the share of devices and on intensity.",
   "source": "B4-fleet-trend-detection §How it works"
  },
  {
   "id": "q14",
   "type": "mcq",
   "kp": "family-vs-device",
   "prompt": "A new release raises disconnects across a whole family. Which detector is built for this?",
   "choices": [
    "Device-level isolation forest",
    "Family-level WLS slope test on the share",
    "DeepLog on one device",
    "A chi-square test on one device"
   ],
   "answer": 1,
   "explanation": "Fleet-wide regressions are the family-level detector's target: few reports, each high impact.",
   "source": "B4-fleet-trend-detection §How it works"
  },
  {
   "id": "q15",
   "type": "tf",
   "kp": "family-vs-device",
   "prompt": "Device-level detection produces many reports, each lower impact and often environmental.",
   "answer": true,
   "explanation": "One household behaving oddly is often its router or setup.",
   "source": "B4-fleet-trend-detection §How it works"
  },
  {
   "id": "q16",
   "type": "numeric",
   "kp": "multiple-testing",
   "prompt": "An illustrative 10,000 series are tested daily at p < 0.01 with no real changes. About how many cross the line by chance per day?",
   "answer": 100,
   "unit": "series",
   "tolerance": 0,
   "explanation": "10,000 × 0.01 = 100.",
   "source": "B4-fleet-trend-detection §How it is measured or used"
  },
  {
   "id": "q17",
   "type": "mcq",
   "kp": "multiple-testing",
   "prompt": "What remedy for multiple testing does the note name?",
   "choices": [
    "Lower the cap on the score",
    "Control the false discovery rate (Benjamini–Hochberg), or rank by score and review the top",
    "Use OLS instead",
    "Test each series twice"
   ],
   "answer": 1,
   "explanation": "FDR control limits the expected share of flagged series that are false alarms.",
   "source": "B4-fleet-trend-detection §How it is measured or used"
  },
  {
   "id": "q18",
   "type": "mcq",
   "kp": "multiple-testing",
   "prompt": "Daily residuals of a fleet metric are autocorrelated (weekly cycles). What is the effect on the test?",
   "choices": [
    "se(β̂) too small and p-values too optimistic",
    "se(β̂) too large and p-values too pessimistic",
    "No effect with WLS",
    "The slope becomes biased toward zero"
   ],
   "answer": 0,
   "explanation": "A weekly dummy or a block bootstrap of the slope is a cheap check (the note's interpretation).",
   "source": "B4-fleet-trend-detection §How it is measured or used"
  }
 ]
});
