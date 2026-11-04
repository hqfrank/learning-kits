# B2 — Windows and log count vectors (the bag of events)

**Source:** He, Zhu, He, Lyu, "Experience Report: System Log Analysis for Anomaly Detection", ISSRE 2016 (https://jiemingzhu.github.io/pub/slhe_issre2016.pdf), §III-B (windows) and §III-C (feature extraction), §IV (setup, findings); generalised from internal design documents of a device-health programme (see [`../SOURCES.md`](../SOURCES.md)). · **Status:** concept primer.

## In one sentence
To feed a model, the parsed log stream is cut into finite chunks called windows, and each window becomes a vector of how many times each template occurred in it — a "bag of events" that keeps frequency and loses order.

## What it is
A **window** (log sequence) is a finite, contiguous chunk of the parsed stream. A **log count vector** (event count vector) for a window has one entry per template; entry *j* is the number of times template *j* appeared in the window. Stack the vectors and you have the **event count matrix**: one row per window, one column per template (He et al. 2016, §III-C).

Analogy: a count vector is a bag-of-words for logs. You know which "words" (templates) were in the paragraph and how often, but not in what order.

## How it works
**Three ways to cut windows** (He et al. 2016, §III-B):

- **Fixed window** — consecutive, non-overlapping chunks of fixed size Δt (time) or fixed line count. Simple; a fault that straddles a boundary is split in two.
- **Sliding window** — a window size and a smaller step size; windows overlap, so one line can belong to several windows. More windows, smoother coverage.
- **Session window** — windows defined by an identifier, so each window is one execution path. In the public HDFS data set each block ID defines a session; He et al. built 575,061 event count vectors this way, of which 16,838 are labelled anomalies (§IV-A). Device logs rarely carry such an identifier, which is why fixed or sliding windows are the practical default.

He et al. use, by default, a 1 h fixed window and a 6 h sliding window with a 1 h step on the BGL supercomputer log (§IV-B). They report that sliding windows can reach higher accuracy than fixed windows (Finding 2), and that window and step size affect supervised and unsupervised methods differently (Finding 4).

**The trade-off in window length.** Three quantities move together (my explanation; explored in the planned window explorer, see [`../README.md`](../README.md)):

- **Longer windows** collect more lines, so the count vector is less sparse and frequency changes are easier to see. But a short burst is diluted, and the earliest possible alarm comes later.
- **Shorter windows** react faster and localise the anomaly in time. But most entries are zero, and normal variation between windows looks large.
- **Smaller steps** (sliding windows) give finer time localisation at the cost of more, highly correlated windows.

Worked example (illustrative, my arithmetic): one device-day of 24 h with an illustrative 1 h window and 15 min step gives (24 − 1) ÷ 0.25 + 1 = 93 windows.

**Count vectors versus sequences.** Three feature families exist (He et al. 2016; the internal design used the same taxonomy):

- **quantitative** — counts per template (the count vector);
- **sequential** — the ordered list of template IDs in the window, used by sequence models such as DeepLog ([[B3-anomaly-detection-on-logs]]);
- **semantic** — embeddings of the template text from a language model.

Count vectors were the starting point in the internal design because they are simple to compute, easy to explain (each column is a template an engineer can read), and adequate for "too many / too few of event X" faults.

## How it is measured or used
- **Output shape.** One row per window: device ID, window start time, count of template 1 … count of template *p*. Only the count columns go into the model.
- **Normalisation.** Raw counts favour busy windows. Options are per-window normalisation or a log transform; whichever is chosen must be identical in training and inference.
- **Interleaving.** Partitioning the stream by process and thread before windowing makes each window more coherent ([[B5-from-anomaly-to-root-cause]]).

## Common confusions
- **"Counts capture everything."** Two windows with the same counts but different order are identical to a count-vector model. `connect → good → ping → done` and `connect → ping → bad → bounce` can share a vector if the multiset of events is the same. Ordering faults need sequence features or transition counts ([[B5-from-anomaly-to-root-cause]]).
- **"A sliding window gives more data."** It gives more *rows*, but neighbouring rows overlap and are not independent. Do not count them as independent samples when estimating error rates.
- **"The window size is a tuning detail."** It decides which faults are visible at all and how quickly an alarm can fire.

## Why it matters for fleet operations
The window is the unit the model judges and the unit the engineer is shown. Too long, and the engineer gets an hour of logs to read; too short, and the model cries wolf on normal jitter. The choice should be set from the fault classes you care about, not by default.

## Terms introduced
- **window (log sequence)** — a finite contiguous chunk of the parsed stream.
- **fixed window** — non-overlapping windows of constant size.
- **sliding window** — overlapping windows defined by a window size and a smaller step size.
- **session window** — a window that holds one execution path, defined by an identifier.
- **log count vector (event count vector)** — per window, the number of occurrences of each template.
- **event count matrix** — the stack of count vectors: windows × templates.
- **bag of events** — the count-vector representation; frequency kept, order lost.
- **quantitative / sequential / semantic features** — counts / ordered template IDs / text embeddings.
