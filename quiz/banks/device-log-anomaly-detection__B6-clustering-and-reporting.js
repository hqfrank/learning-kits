// Generated from learning/device-log-anomaly-detection/notes/B6-clustering-and-reporting.md; numbers loaded from constants.json.
window.QUIZ_BANKS = window.QUIZ_BANKS || [];
window.QUIZ_BANKS.push({
 "topic": "device-log-anomaly-detection",
 "topicTitle": "Finding faults in a device fleet from logs and metrics",
 "section": "B6-clustering-and-reporting",
 "sectionTitle": "B6 — Clustering similar anomalies, and automated reports",
 "notePath": "../device-log-anomaly-detection/notes/B6-clustering-and-reporting.md",
 "knowledgePoints": {
  "join-distance": {
   "title": "Join and distance",
   "summary": "Each anomalous device-day becomes one row of m attributes, n metric features, and p log features; mixed types need scaling and a mixed-type measure such as Gower similarity, and that choice defines \"similar\".",
   "source": "B6-clustering-and-reporting §How it works"
  },
  "agglomerative": {
   "title": "Agglomerative clustering and the dendrogram",
   "summary": "Start with every row as a cluster, repeatedly merge the two closest under a linkage (single, complete, average, Ward), and cut the dendrogram at a distance threshold so the cluster count follows from the data.",
   "source": "B6-clustering-and-reporting §How it works"
  },
  "rank-dedup": {
   "title": "Rank and de-duplicate",
   "summary": "Rank clusters by affected devices, recurrence, and mean score; then drop, append to an existing ticket, or open a new one.",
   "source": "B6-clustering-and-reporting §How it works"
  },
  "ticket-loop": {
   "title": "Ticket content and closing the loop",
   "summary": "One ticket per cluster carries the device table, the metric anomaly, and the log snippet with raw logs; the resolved root-cause label (defect, environmental, data artefact) flows back as rules and ground truth.",
   "source": "B6-clustering-and-reporting §How it works; Common confusions"
  },
  "enrichment": {
   "title": "Enriching tickets people open",
   "summary": "User-reported and support tickets get auto-attached evidence via similar-device matching, release correlation, and known-issue matching, delivered where reviewers already work.",
   "source": "B6-clustering-and-reporting §How it works"
  },
  "symptoms-not-causes": {
   "title": "Clusters group symptoms; less is more",
   "summary": "Clustering groups similar symptoms, not causes; fewer, clearer ticket fields beat more information.",
   "source": "B6-clustering-and-reporting §Common confusions"
  },
  "cluster-measures": {
   "title": "Purity, duplicate rate, time to first action",
   "summary": "Cluster purity is the share of a cluster's devices sharing the resolved root cause; duplicate rate is the share of new tickets later merged; enrichment is judged by time to first action.",
   "source": "B6-clustering-and-reporting §How it is measured or used"
  }
 },
 "questions": [
  {
   "id": "q1",
   "type": "mcq",
   "kp": "join-distance",
   "prompt": "Which three blocks of columns make up the joined row for an anomalous device-day?",
   "choices": [
    "Templates, parameters, timestamps",
    "Attributes, metric features, log features",
    "Devices, days, scores",
    "Reason codes, bands, signal bars"
   ],
   "answer": 1,
   "explanation": "*m* attributes (family, version, country, OUI), *n* metric features, *p* log template counts.",
   "source": "B6-clustering-and-reporting §How it works"
  },
  {
   "id": "q2",
   "type": "mcq",
   "kp": "join-distance",
   "prompt": "Why use a measure such as Gower similarity on the joined rows?",
   "choices": [
    "It is fastest",
    "The rows mix numeric and categorical columns of different scales",
    "It needs no scaling",
    "It produces a fixed number of clusters"
   ],
   "answer": 1,
   "explanation": "Gower (1971) handles mixed types; the alternative is one-hot categories with block weights.",
   "source": "B6-clustering-and-reporting §How it works"
  },
  {
   "id": "q3",
   "type": "tf",
   "kp": "join-distance",
   "prompt": "The choice of distance decides what \"similar\" means for the clusters.",
   "answer": true,
   "explanation": "Scaling, encoding, and block weights change which anomalies group together.",
   "source": "B6-clustering-and-reporting §How it works"
  },
  {
   "id": "q4",
   "type": "mcq",
   "kp": "agglomerative",
   "prompt": "How does agglomerative hierarchical clustering proceed?",
   "choices": [
    "Picks k centres and reassigns points",
    "Starts with each row as its own cluster and repeatedly merges the two closest",
    "Splits the full set top-down",
    "Grows clusters from density peaks"
   ],
   "answer": 1,
   "explanation": "It is bottom-up; the linkage defines the distance between clusters.",
   "source": "B6-clustering-and-reporting §How it works"
  },
  {
   "id": "q5",
   "type": "mcq",
   "kp": "agglomerative",
   "prompt": "What does cutting the dendrogram at a distance threshold achieve?",
   "choices": [
    "Exactly ten clusters",
    "The number of clusters follows from the data",
    "Removes outliers",
    "Ranks the clusters"
   ],
   "answer": 1,
   "explanation": "The cluster count is not fixed in advance.",
   "source": "B6-clustering-and-reporting §How it works"
  },
  {
   "id": "q6",
   "type": "multi",
   "kp": "agglomerative",
   "prompt": "Which are linkage rules named in the note?",
   "choices": [
    "Single",
    "Complete",
    "Cosine",
    "Average",
    "Ward"
   ],
   "answer": [
    0,
    1,
    3,
    4
   ],
   "explanation": "Cosine is a similarity measure, not a linkage.",
   "source": "B6-clustering-and-reporting §How it works"
  },
  {
   "id": "q7",
   "type": "mcq",
   "kp": "rank-dedup",
   "prompt": "Which cluster is ranked first?",
   "choices": [
    "The most recent one",
    "Many devices, a recurring pattern, and high anomaly scores",
    "The one with the most templates",
    "The smallest one"
   ],
   "answer": 1,
   "explanation": "Ranking combines affected-device count, recurrence, and mean score.",
   "source": "B6-clustering-and-reporting §How it works"
  },
  {
   "id": "q8",
   "type": "multi",
   "kp": "rank-dedup",
   "prompt": "Which actions are possible when a cluster is checked against open tickets?",
   "choices": [
    "Drop it (known and closed as environmental)",
    "Append it to an existing ticket",
    "Open a new ticket",
    "Close every open ticket on that family"
   ],
   "answer": [
    0,
    1,
    2
   ],
   "explanation": "De-duplication has exactly three outcomes.",
   "source": "B6-clustering-and-reporting §How it works"
  },
  {
   "id": "q9",
   "type": "tf",
   "kp": "ticket-loop",
   "prompt": "Once a ticket is filed, the pipeline's job for that cluster is done.",
   "answer": false,
   "explanation": "The resolution label is the most valuable output for the next model iteration.",
   "source": "B6-clustering-and-reporting §Common confusions"
  },
  {
   "id": "q10",
   "type": "mcq",
   "kp": "ticket-loop",
   "prompt": "Which root-cause labels flow back from resolved tickets?",
   "choices": [
    "Critical, major, minor",
    "Device defect, environmental, data artefact",
    "Rule, model, human",
    "Fixed, won't fix, duplicate"
   ],
   "answer": 1,
   "explanation": "They feed the direction and drop rules and become ground truth (C1).",
   "source": "B6-clustering-and-reporting §How it works"
  },
  {
   "id": "q11",
   "type": "mcq",
   "kp": "enrichment",
   "prompt": "What does release correlation check?",
   "choices": [
    "Whether the ticket was filed on release day",
    "Whether the anomaly started with a software update",
    "Whether two releases share templates",
    "Whether the device is in the pre-release programme"
   ],
   "answer": 1,
   "explanation": "It is one of three enrichment checks with similar devices and known-issue matching.",
   "source": "B6-clustering-and-reporting §How it works"
  },
  {
   "id": "q12",
   "type": "multi",
   "kp": "enrichment",
   "prompt": "Which checks give ticket enrichment its value?",
   "choices": [
    "Similar-device matching",
    "Release correlation",
    "Retraining the isolation forest",
    "Known-issue matching"
   ],
   "answer": [
    0,
    1,
    3
   ],
   "explanation": "Retraining is a pipeline task, not an enrichment check.",
   "source": "B6-clustering-and-reporting §How it works"
  },
  {
   "id": "q13",
   "type": "mcq",
   "kp": "enrichment",
   "prompt": "How should ranked anomalies reach a weekly metrics review?",
   "choices": [
    "Through a new stand-alone tool",
    "As a new tab in the dashboard reviewers already use",
    "By email only",
    "As raw logs"
   ],
   "answer": 1,
   "explanation": "Meet people where they work.",
   "source": "B6-clustering-and-reporting §How it works"
  },
  {
   "id": "q14",
   "type": "tf",
   "kp": "symptoms-not-causes",
   "prompt": "Clustering anomalies finds their causes.",
   "answer": false,
   "explanation": "It groups similar symptoms; two causes with the same symptoms land together.",
   "source": "B6-clustering-and-reporting §Common confusions"
  },
  {
   "id": "q15",
   "type": "mcq",
   "kp": "symptoms-not-causes",
   "prompt": "One cause shows different symptoms on two device families. Where does it land?",
   "choices": [
    "In one cluster",
    "In two clusters",
    "In no cluster",
    "In the cluster with the most devices"
   ],
   "answer": 1,
   "explanation": "Clusters are built on symptoms, so different symptoms split one cause.",
   "source": "B6-clustering-and-reporting §Common confusions"
  },
  {
   "id": "q16",
   "type": "tf",
   "kp": "symptoms-not-causes",
   "prompt": "Adding more columns and statistical plots to a ticket makes it more useful.",
   "answer": false,
   "explanation": "In the survey, designer-chosen columns confused users and probability-mass charts were not understood; fewer, clearer fields win.",
   "source": "B6-clustering-and-reporting §Common confusions"
  },
  {
   "id": "q17",
   "type": "mcq",
   "kp": "cluster-measures",
   "prompt": "What is cluster purity?",
   "choices": [
    "The share of a cluster's devices that share the resolved root cause",
    "The mean anomaly score in the cluster",
    "The share of new tickets later merged",
    "The dendrogram height of the cluster"
   ],
   "answer": 0,
   "explanation": "It is measured from closed tickets.",
   "source": "B6-clustering-and-reporting §How it is measured or used"
  },
  {
   "id": "q18",
   "type": "mcq",
   "kp": "cluster-measures",
   "prompt": "What is the duplicate rate?",
   "choices": [
    "The share of rows that are identical",
    "The share of new tickets later merged into another",
    "The share of templates that duplicate",
    "The share of devices in two clusters"
   ],
   "answer": 1,
   "explanation": "A high rate means de-duplication against open tickets is failing.",
   "source": "B6-clustering-and-reporting §How it is measured or used"
  }
 ]
});
