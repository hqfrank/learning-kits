// Generated from learning/device-log-anomaly-detection/notes/A2-fleet-metrics.md; numbers loaded from constants.json.
window.QUIZ_BANKS = window.QUIZ_BANKS || [];
window.QUIZ_BANKS.push({
 "topic": "device-log-anomaly-detection",
 "topicTitle": "Finding faults in a device fleet from logs and metrics",
 "section": "A2-fleet-metrics",
 "sectionTitle": "A2 — Fleet metrics: event counters, device-days, and the share of devices",
 "notePath": "../device-log-anomaly-detection/notes/A2-fleet-metrics.md",
 "knowledgePoints": {
  "event-triggered": {
   "title": "Event-triggered metrics",
   "summary": "A metric exists only when its event happened; absence is the normal state, so a zero can mean healthy, off, or not reporting.",
   "source": "A2-fleet-metrics §What it is; Common confusions"
  },
  "features-attributes": {
   "title": "Features and attributes",
   "summary": "Records are pivoted so each feature (metric name joined to one category) has one meaning; attributes such as software version or router vendor (from the MAC prefix, OUI) describe the device and are used for slicing.",
   "source": "A2-fleet-metrics §How it works"
  },
  "share-intensity": {
   "title": "Share of devices and intensity",
   "summary": "Per day and family: share = devices that emitted the feature ÷ active devices; intensity = total events ÷ active devices.",
   "source": "A2-fleet-metrics §How it works"
  },
  "share-se": {
   "title": "The share's standard error depends on n",
   "summary": "The share is a sample proportion with SE = √(p̂(1 − p̂)/n); halving n multiplies SE by √2, so a day with few devices is a noisy day.",
   "source": "A2-fleet-metrics §How it works"
  },
  "direction-percentiles": {
   "title": "Direction and tail percentiles",
   "summary": "A higher share is not always worse (direction is per metric), and tail percentiles over a small population are very noisy.",
   "source": "A2-fleet-metrics §Common confusions"
  },
  "population-proxies": {
   "title": "Population power, proxies, and levels",
   "summary": "Small pre-release populations have low power for rare events; production devices usually lack logs, so matching pre-release devices serve as proxies; family-level and device-level views can disagree.",
   "source": "A2-fleet-metrics §How it is measured or used; Common confusions"
  }
 },
 "questions": [
  {
   "id": "q1",
   "type": "tf",
   "kp": "event-triggered",
   "prompt": "On most days a healthy device emits nothing at all for a Wi-Fi-disconnect metric.",
   "answer": true,
   "explanation": "The metric is event-triggered: it exists only when a disconnect happened.",
   "source": "A2-fleet-metrics §What it is"
  },
  {
   "id": "q2",
   "type": "mcq",
   "kp": "event-triggered",
   "prompt": "A device shows zero for an event-triggered metric on a given day. What can that zero mean?",
   "choices": [
    "Only that the device was healthy",
    "Healthy, switched off, or not reporting",
    "Only that data ingestion failed",
    "That the metric was renamed"
   ],
   "answer": 1,
   "explanation": "Zero is ambiguous for event-triggered data; missing days look like zeros unless a gap detector finds them (C3).",
   "source": "A2-fleet-metrics §Common confusions"
  },
  {
   "id": "q3",
   "type": "mcq",
   "kp": "features-attributes",
   "prompt": "Why are raw metric records pivoted into features (metric name joined to one category)?",
   "choices": [
    "To compress the store",
    "Because a category field's meaning depends on the metric name; a feature gives every column one meaning",
    "To remove device IDs",
    "To convert counts into durations"
   ],
   "answer": 1,
   "explanation": "For example `disconnects__reason-code` with category 3 is a single, unambiguous column.",
   "source": "A2-fleet-metrics §How it works"
  },
  {
   "id": "q4",
   "type": "multi",
   "kp": "features-attributes",
   "prompt": "Which of these are **attributes** (descriptors of the device used for slicing) rather than features?",
   "choices": [
    "Software version",
    "Number of Wi-Fi disconnects with reason code 3",
    "Country",
    "Router vendor (from the OUI)",
    "Sum of disconnect duration in seconds"
   ],
   "answer": [
    0,
    2,
    3
   ],
   "explanation": "Attributes describe the device; disconnect counts and durations are behaviour, i.e. features.",
   "source": "A2-fleet-metrics §How it works"
  },
  {
   "id": "q5",
   "type": "mcq",
   "kp": "features-attributes",
   "prompt": "How is the router-vendor attribute derived?",
   "choices": [
    "From the Wi-Fi band",
    "From the reason code",
    "From the router MAC address prefix (OUI)",
    "From the device family"
   ],
   "answer": 2,
   "explanation": "The organisationally unique identifier is the vendor prefix of a MAC address.",
   "source": "A2-fleet-metrics §How it works"
  },
  {
   "id": "q6",
   "type": "tf",
   "kp": "features-attributes",
   "prompt": "Attributes describe the device's behaviour, such as how often it disconnects.",
   "answer": false,
   "explanation": "Attributes describe the device itself (software version, country, family, router vendor); behaviour lives in the features.",
   "source": "A2-fleet-metrics §How it works"
  },
  {
   "id": "q7",
   "type": "mcq",
   "kp": "share-intensity",
   "prompt": "Which formula defines **intensity** for a family on one day?",
   "choices": [
    "Devices that emitted the feature ÷ active devices",
    "Total events of the feature ÷ active devices",
    "Total events ÷ devices that emitted the feature",
    "Active devices ÷ all registered devices"
   ],
   "answer": 1,
   "explanation": "Intensity counts events per active device; the share of devices counts devices that emitted at least once.",
   "source": "A2-fleet-metrics §How it works"
  },
  {
   "id": "q8",
   "type": "mcq",
   "kp": "share-intensity",
   "prompt": "One device emits many disconnects; all other devices emit none. Which quantity rises more?",
   "choices": [
    "The share of devices",
    "Intensity",
    "Both rise equally",
    "Neither changes"
   ],
   "answer": 1,
   "explanation": "The share counts that one device only once; intensity counts all its events, so one bad device moves intensity much more.",
   "source": "A2-fleet-metrics §How it works"
  },
  {
   "id": "q9",
   "type": "numeric",
   "kp": "share-se",
   "prompt": "A family has 100 active devices and 3 emit a rare disconnect reason (p̂ = 0.03). Using SE = √(p̂(1 − p̂)/n), what is the SE in percentage points?",
   "answer": 1.7,
   "unit": "percentage points",
   "tolerance": 0.1,
   "explanation": "√(0.03 × 0.97 / 100) ≈ 1.7 pp: a jump to 3 % could be a few unlucky households.",
   "source": "A2-fleet-metrics §How it works"
  },
  {
   "id": "q10",
   "type": "numeric",
   "kp": "share-se",
   "prompt": "The same p̂ = 0.03 is observed in a family of 10,000 active devices. What is the SE in percentage points?",
   "answer": 0.17,
   "unit": "percentage points",
   "tolerance": 0.02,
   "explanation": "√(0.03 × 0.97 / 10,000) ≈ 0.17 pp: ten times smaller, so the same share is a fleet change.",
   "source": "A2-fleet-metrics §How it works"
  },
  {
   "id": "q11",
   "type": "numeric",
   "kp": "share-se",
   "prompt": "The number of active devices on a day halves. By what factor does the standard error of the share grow?",
   "answer": 1.414,
   "unit": "×",
   "tolerance": 0.01,
   "explanation": "SE ∝ 1/√n, so halving n multiplies SE by √2 ≈ 1.414.",
   "source": "A2-fleet-metrics §How it works"
  },
  {
   "id": "q12",
   "type": "tf",
   "kp": "share-se",
   "prompt": "A share of 3 % from 100 devices is as strong evidence of a fleet change as 3 % from 10,000 devices.",
   "answer": false,
   "explanation": "The standard error is about ten times larger in the small family; the variance of the share depends on sample size.",
   "source": "A2-fleet-metrics §How it works"
  },
  {
   "id": "q13",
   "type": "tf",
   "kp": "direction-percentiles",
   "prompt": "For every fleet metric, a higher share of devices is worse.",
   "answer": false,
   "explanation": "Direction matters per metric: more successful recoveries is an improvement. A filter must drop good changes before ticketing.",
   "source": "A2-fleet-metrics §Common confusions"
  },
  {
   "id": "q14",
   "type": "mcq",
   "kp": "direction-percentiles",
   "prompt": "A team reports the p99 of a duration metric for a small family. What does the note advise?",
   "choices": [
    "Tail percentiles are robust, so report as is",
    "Report the population size with the percentile, because it is very noisy",
    "Replace it with the maximum",
    "Report only the mean"
   ],
   "answer": 1,
   "explanation": "A tail percentile over a small population is very noisy.",
   "source": "A2-fleet-metrics §Common confusions"
  },
  {
   "id": "q15",
   "type": "mcq",
   "kp": "population-proxies",
   "prompt": "The large production population usually has no logs for anomalous devices. What is the common workaround?",
   "choices": [
    "Wait until customers call support",
    "Diagnose matching pre-release devices (same family, software version, anomaly) as proxies",
    "Infer logs from metrics",
    "Use only family-level trends"
   ],
   "answer": 1,
   "explanation": "A proxy device has logs and matches the anomalous group that has none.",
   "source": "A2-fleet-metrics §How it is measured or used"
  },
  {
   "id": "q16",
   "type": "mcq",
   "kp": "population-proxies",
   "prompt": "What is the statistical weakness of a small pre-release population?",
   "choices": [
    "Too many logs to parse",
    "Low power for rare events",
    "No software-version attribute",
    "Its metrics are not event-triggered"
   ],
   "answer": 1,
   "explanation": "With few devices, a rare event moves the share by a lot through chance alone.",
   "source": "A2-fleet-metrics §How it is measured or used"
  },
  {
   "id": "q17",
   "type": "tf",
   "kp": "population-proxies",
   "prompt": "A family-level trend can hide a few very bad devices, and a few very bad devices can look like a trend in a small family.",
   "answer": true,
   "explanation": "Device-level and family-level views need not agree, which is why both detectors exist (B4).",
   "source": "A2-fleet-metrics §Common confusions"
  }
 ]
});
