# C1 — The ground-truth problem: how to evaluate a detector with almost no labels

**Source:** precision/recall/F-measure as defined in Du et al., "DeepLog", CCS 2017, §5.1; labelled public data sets in He et al., ISSRE 2016, §IV-A; Wilson score interval from Wilson, J. Am. Stat. Assoc. 22:209–212, 1927 (see also NIST e-Handbook §7.2.4.1, https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm); generalised from internal design documents of a device-health programme (see [`../SOURCES.md`](../SOURCES.md)). · **Status:** concept primer. All case counts below are illustrative.

## In one sentence
Production device logs carry no fault labels, so you build a small ground-truth set by hand from lab-induced faults and resolved user reports, report the detection rate with its wide confidence interval and next to the false-alarm rate, and then run a forward pilot, because finding a known fault is not the same as being useful on an unknown one.

## What it is
**Ground truth** is a set of cases where the true answer is known: this device, this time range, this fault, confirmed and fixed. Public research data sets have it because researchers labelled them. In HDFS, 16,838 of 575,061 session count vectors are labelled anomalous; in BGL, 348,460 of 4,747,963 messages are labelled failures (He et al. 2016, §IV-A). A device fleet has none of this by default.

## How it works
**Sources of ground truth.**

- **Lab-induced faults** — a lab test programme reproduces a known bug on a test device. The fault and its time are known. But lab logs are often in a test-framework format, not the production format.
- **Resolved user reports** — a pre-release user reports a problem, an engineer finds and fixes the bug, and the ticket is closed with the cause. Only a fraction qualify: the case needs a production-format log for the right time range, an identified bug, and a closed ticket. In an illustrative funnel, an illustrative 60 candidate cases give an illustrative 10 usable ones.
- **Support tickets, engineer judgement** — weaker labels that can extend the set over time.

**Backward validation.** For each ground-truth case, an engineer starts from the known fault, finds the log snippet that shows it, and records it. Then the detector runs on the same logs: does it flag the same device and snippet? For each case record four answers: what was the issue, when was it, did the detector catch it, and if not, why not and can it be fixed.

**Forward validation.** Backward validation proves the detector *can* find known faults. It does not prove that its output alone is enough to *start* an investigation when nobody knows the answer. A **forward pilot** fills the gap: generate a few cases per week, give them to domain experts, and ask in order: (1) is the output sufficient to start? (2) what is missing? (3) given the inputs, was the right anomaly flagged? Confirmed anomalies then go to root-cause analysis.

**The confusion matrix.** For a set of windows or cases:

| | Fault present | No fault |
|---|---|---|
| Flagged | true positive (TP) | false positive (FP) |
| Not flagged | false negative (FN) | true negative (TN) |

- **Detection rate (recall)** = TP ÷ (TP + FN).
- **Precision** = TP ÷ (TP + FP) (Du et al. 2017, §5.1).
- **False-alarm rate** — the share of flags that are not device faults, FP ÷ (TP + FP), which is 1 − precision; or, per window, FP ÷ (FP + TN).

**Report the rate with its interval.** Worked example (illustrative counts, my arithmetic): the detector catches 6 of 10 ground-truth cases. The detection rate is 60 %. The 95 % Wilson score interval is about 31 % to 83 %. The simple normal (Wald) interval, 30 % to 90 %, is too wide at the top and misbehaves near 0 and 1. With 100 cases and the same rate the Wilson interval narrows to about 50 % to 69 %. Ten cases support "the method works"; they do not support "the method is better than another method that scored 50 %".

**Why the false-alarm rate must sit next to the detection rate.** A detector that flags every window has a detection rate of 100 %. The detection rate means nothing without the cost in false alarms. In an illustrative pilot of 10 tickets, 4 were environmental (the customer's access point, not the device); that is the false-alarm side of the same experiment.

**Learn from the misses.** Classify each miss as **fixable** (more components, kernel logs, more metrics would have caught it) or **unfixable** (the fault leaves no trace in the signals at all). Fixable misses become the roadmap ([[C4-lessons]]).

**Make the cycle faster.** Waiting for operational ticket outcomes makes each design iteration take months. A historical ground-truth set lets a new model be tested in days. Two guards keep it honest:

- **time-ordered cross-validation** — train on earlier periods and validate on later ones, then roll the split forward and average; never validate on faults older than the training data;
- **two headline KPIs** — the anomaly rate (a proxy for false alarms) and the false-negative rate on known faults.

## How it is measured or used
- Track the ground-truth set as a versioned artefact: case ID, device, time range, component, root cause, log format, detector result.
- Re-run the whole set on every model or template change ([[C2-template-engineering]]).

## Common confusions
- **"60 % is a measurement of the detector."** With the illustrative 10 cases it is a measurement with an interval of about ±25 percentage points.
- **"Backward validation is validation."** It is necessary, not sufficient. Forward usefulness is a separate question.
- **"Lab cases are clean ground truth."** They are clean on the *fault*, but often in the wrong log format, and often stateful sequences that production devices rarely hit.
- **"Precision and recall are enough."** Engineer time to root cause, and whether the output was enough to start, are what decide adoption.

## Why it matters for fleet operations
Without ground truth, every claim about the detector is anecdote. A small, honest, versioned set, with intervals and false alarms reported together, is what lets a team decide whether a change helped.

## Terms introduced
- **ground truth** — cases where the true answer (device, time, fault) is known and confirmed.
- **lab-induced fault** — a known bug reproduced on a test device under controlled conditions.
- **backward validation** — starting from a known fault and checking that the detector flags it.
- **forward validation (forward pilot)** — giving detector output to experts with no prior answer and asking whether it is sufficient to start.
- **confusion matrix** — the 2 × 2 table of TP, FP, FN, TN.
- **detection rate (recall)** — TP ÷ (TP + FN).
- **precision** — TP ÷ (TP + FP).
- **false-alarm rate** — the share of flags that are not real device faults.
- **Wilson score interval** — a confidence interval for a proportion that behaves well for small n and rates near 0 or 1.
- **fixable / unfixable miss** — a missed fault that more signal would catch / one that leaves no trace in the signals.
- **time-ordered cross-validation** — training on earlier data and validating on later data, rolled forward.
