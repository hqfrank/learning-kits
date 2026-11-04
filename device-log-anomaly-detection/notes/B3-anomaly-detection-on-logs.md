# B3 — Anomaly detection on logs: isolation forest, and sequence models on the device

**Source:** Liu, Ting, Zhou, "Isolation Forest", ICDM 2008 (https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/icdm08b.pdf), §2–§3; scikit-learn `IsolationForest` documentation (https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html); Du, Li, Zheng, Srikumar, "DeepLog", CCS 2017 (https://nlp.cs.utah.edu/assets/pdfs/du2017deeplog.pdf), §3 and §5.1; Meng et al., "LogAnomaly", IJCAI 2019; He et al., ISSRE 2016, Finding 3; generalised from internal design documents of a device-health programme (see [`../SOURCES.md`](../SOURCES.md)). · **Status:** concept primer.

## In one sentence
With no labelled faults, the practical choice is to learn what normal windows look like and flag the ones that are easy to isolate — an isolation forest on count vectors in the cloud, or a small sequence model that predicts the next log event on the device.

## What it is
**Anomaly detection** flags data points that differ from the bulk of the data. **Unsupervised** anomaly detection learns from unlabelled data, usually data assumed to be mostly normal, and needs no examples of faults.

**Isolation forest** (iForest; Liu et al. 2008) rests on one idea: anomalies are "few and different", so random splits isolate them quickly. An **isolation tree** picks a random feature and a random split value between that feature's minimum and maximum, and repeats on each side until each point is alone or a height limit is reached. The number of splits from root to a point's leaf is its **path length** *h(x)*. Anomalies have short paths.

Analogy: in a game of twenty questions with random questions, the odd one out is named after very few questions.

## How it works
**The score.** Over a forest of trees, the expected path length E(*h(x)*) is normalised by *c(ψ)*, the average path length of an unsuccessful search in a binary search tree built on ψ points:

  *c*(*n*) = 2*H*(*n* − 1) − 2(*n* − 1)/*n*, with *H*(*i*) ≈ ln(*i*) + 0.5772156649,

  *s*(*x*) = 2^(−E(*h(x)*) / *c*(ψ)) (Liu et al. 2008, Eq. 1–2).

If E(*h*) equals *c*, *s* = 0.5. Scores very close to 1 are anomalies. Scores well below 0.5 are normal. If every point scores about 0.5, the sample has no distinct anomaly (Liu et al. 2008, §2).

**Defaults.** Each tree is built on a sub-sample of ψ = 256 points, the forest has *t* = 100 trees, and the height limit is ⌈log₂ ψ⌉ (Liu et al. 2008, §3; scikit-learn `max_samples='auto'` = min(256, n), `n_estimators=100`). Worked example (my arithmetic from the formulas): *c*(256) ≈ 10.24 and the height limit is 8. A window isolated after an average of 3 splits scores 2^(−3/10.24) ≈ 0.82; one isolated after 10.24 splits scores 0.50.

**Threshold.** In scikit-learn, `contamination='auto'` uses the paper's threshold (offset −0.5 on the shifted score). A numeric contamination sets the threshold so that that fraction of the training data is flagged. Contamination is a decision about how many alarms you want, not a property of the data.

**Training and inference for logs.** Train on count vectors from windows of devices believed healthy (for example, devices with a good connection and no unusual disconnects). At inference, score each new window; windows above threshold are anomalous ([[B2-windows-and-count-vectors]]).

**Per-device metric vectors.** The same model runs on per-device-day feature vectors from fleet metrics ([[A2-fleet-metrics]]). These vectors are very sparse because the metrics are event-triggered. Random splits on mostly-zero features isolate a non-zero value quickly, which is the behaviour you want; zero-inflated models are an alternative worth testing.

**Why not rules, and why not a classifier?**

| Approach | Strength | Weakness | Decision in the design |
|---|---|---|---|
| Rules (regular expressions) | Precise for known faults; the rule names the cause | Finds only what was foreseen; breaks when print statements change; usually matches one line, not a pattern across many | Keep as a complement, not the core |
| Supervised classifier | Learns complex patterns; best scores on labelled benchmarks (He et al. 2016, Finding 3) | Needs many labelled faults; device fleets have almost none | Not possible without labels |
| Unsupervised anomaly detection | Needs only normal data; can find unforeseen faults; retrains automatically | Does not name the cause; flags environmental anomalies too | Chosen |

Public benchmarks have labels because researchers labelled them: in the HDFS data set about 2.9 % of 11,197,954 entries are abnormal (Du et al. 2017, §5.1.2). Production device logs have no such labels ([[C1-the-ground-truth-problem]]).

**Sequence models on the device.** DeepLog (Du et al. 2017) treats a log as a language. An LSTM reads the last *h* template IDs and predicts a probability for each possible next template; the actual next template is normal if it is among the top *g* predictions. Its defaults are *g* = 9, *h* = 10, *L* = 2 layers, and α = 64 memory units per LSTM block (§5.1.3). LogAnomaly (Meng et al. 2019) adds template embeddings so that new, similar templates are handled, and combines sequential and quantitative patterns.

**The trade-off.**

- A count-vector forest is cheap to train, easy to retrain, and easy to explain. It ignores order.
- A sequence model detects order faults and flags the exact line where the sequence goes wrong. It costs more to train, and it must fit the device's memory and power budget if it runs on the device.
- The internal design used a sequence model for the on-device vision and an isolation forest for the cloud service (generalised).

## How it is measured or used
- **Output:** a flag per window, a score, and a **feature importance** — which templates drove the score. Isolation forest has no native per-point importance. The simplest proxy shows the window's unusual counts. Model-specific methods exist, such as DIFFI (Carletti, Terzi, Susto, 2020, arXiv:2007.11117), and model-agnostic Shapley-value attributions.
- **Evaluation:** detection rate and false-alarm rate on ground truth ([[C1-the-ground-truth-problem]]).

## Common confusions
- **"The score is a probability of a fault."** It is a normalised path length. The 0.82 of the worked example above means "easy to isolate", not "82 % likely to be a bug".
- **"Train on all data; anomalies are rare anyway."** Training data with many faults teaches the forest that faults are normal. Filter out obviously unhealthy devices first.
- **"Contamination is the true anomaly rate."** You set it. Change it and the alarm count changes; the data do not.
- **"An LSTM is always better."** It sees order, but it needs more data, more compute, and careful handling of new templates.

## Why it matters for fleet operations
The choice of model follows from the data you have: no labels forces unsupervised methods; uploaded windows in the cloud favour a cheap, explainable forest; lost evidence and privacy favour a small sequence model on the device.

## Terms introduced
- **anomaly detection** — flagging data points that differ from the bulk of the data.
- **unsupervised** — learning without labelled examples of the target class.
- **isolation forest (iForest)** — an ensemble of random trees that scores points by how quickly random splits isolate them.
- **isolation tree** — one random-split tree in the forest.
- **path length h(x)** — the number of splits needed to isolate point x.
- **c(n)** — the average path length of an unsuccessful binary-search-tree search on n points; the normaliser of the score.
- **sub-sampling size ψ** — the number of points each isolation tree is built on.
- **contamination** — the user-chosen fraction of training points the threshold flags.
- **feature importance** — the attribution of an anomaly score to individual features (templates).
- **sequence model** — a model of the order of template IDs, such as an LSTM.
- **LSTM (long short-term memory)** — a recurrent neural network that keeps a state across a sequence.
- **top-g rule** — DeepLog's test: the next template is normal if it is among the g most probable predictions.
