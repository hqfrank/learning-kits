# A0 — Why a device fleet needs log and metric analysis

**Source:** generalised from internal design documents of a device-health programme (see [`../SOURCES.md`](../SOURCES.md)); public framing from He et al., "Experience report: system log analysis for anomaly detection", ISSRE 2016. · **Status:** concept primer. Every number is public with a citation or labelled illustrative (see [`../constants.json`](../constants.json)).

## In one sentence
A maker of connected consumer devices learns about most faults too late and with too little evidence, so it needs a pipeline that watches fleet metrics for changes, pulls the logs of the affected devices, and turns thousands of log lines into a short, checkable account of what went wrong.

## What it is
A **fleet** is the full population of devices of one maker that are in use: smart speakers, streaming devices, tablets, and similar consumer devices. Each device produces two kinds of evidence about its own health.

- **Metrics** are small, structured records that the device sends to the cloud when a defined event happens: a Wi-Fi disconnect, a crash, a reboot. See [[A2-fleet-metrics]].
- **Logs** are the free-text lines that the software writes as it runs. They hold much more detail than metrics, but they are large, semi-structured, and often lost. See [[A1-what-a-device-log-is]].

**Log and metric analysis** is the set of methods that turns this evidence into answers: is something wrong, on which devices, since when, and why.

## How it works
Three problems make the work necessary.

1. **Support cost.** A customer who calls support can rarely describe a fault beyond "it cannot connect". The call is long, and the support agent has no device evidence. A fraction of calls (an illustrative 5 %) cannot be resolved and go to engineers, who then start from nothing.
2. **Lost evidence.** A device keeps its logs in a small buffer that overwrites old lines (see [[A1-what-a-device-log-is]]). Most diagnostic tools run only on demand, after a fault is reported. By then the lines that showed the fault are often gone.
3. **Reactive, rule-based tools.** Typical diagnostic tools collect a few low-level values (signal strength, noise), run a ping and an HTTP test, and apply a short decision tree. They find known faults. They cannot find a fault that nobody wrote a rule for. Many sessions end with "cannot resolve, please contact support".

The answer described in this kit is a pipeline with four stages (Part B):

1. **Detect** a change in fleet metrics or in one device's metrics ([[B4-fleet-trend-detection]]).
2. **Fetch and parse** the logs of the devices that drive the change ([[B1-log-parsing-to-templates]], [[B2-windows-and-count-vectors]]).
3. **Find the anomalous log windows** and the events that make them anomalous ([[B3-anomaly-detection-on-logs]], [[B5-from-anomaly-to-root-cause]]).
4. **Group and report** similar anomalies as one ticket with the evidence attached ([[B6-clustering-and-reporting]]).

**On-device versus fleet-side.** The pipeline can run in two places.

- **On-device** analysis runs on the device itself. It sees every log line before the buffer overwrites it, it works when the network is down, and raw logs never leave the device. It must fit in very little memory and must not drain a battery. A small sequence model is a typical choice (see [[B3-anomaly-detection-on-logs]]).
- **Fleet-side** analysis runs in the cloud on logs that devices have already uploaded. It has ample compute and can compare many devices. It sees only the devices whose logs were collected, and only the time ranges that were kept.

The two are complementary. A fleet-side service is the practical first step. An on-device agent is the answer to lost evidence.

## How it is measured or used
A pipeline like this is judged by three questions, not one.

- **Detection rate** — of the real faults, what fraction does it flag? This needs ground truth, which is scarce ([[C1-the-ground-truth-problem]]).
- **False-alarm rate** — of the flags, what fraction are not device faults? Many flags are environmental: a bad router, an internet outage ([[C4-lessons]]).
- **Engineer time** — does the output shorten an investigation? An illustrative reduction from 90 minutes to 15 minutes per case is the kind of result that decides adoption ([[C5-from-service-to-tool]]).

## Common confusions
- **"Anomaly detection finds bugs."** It finds behaviour that differs from normal. Some of that behaviour is a bug; some is the customer's network. The pipeline narrows the search; an engineer still decides ([[C4-lessons]]).
- **"Metrics are enough."** Metrics say *that* something changed. Logs say *what* happened, in order. The pipeline uses metrics to choose which logs to read.
- **"Rules and machine learning compete."** Rules are precise for known faults. Unsupervised models find unknown faults. A mature pipeline uses both ([[C4-lessons]]).

## Why it matters for fleet operations
A fleet of millions of devices produces far more evidence than any team can read. Without a pipeline, faults are found by customers, one complaint at a time, and the evidence is gone before an engineer looks. With a pipeline, a regression in a new software release can be seen in the fleet metrics within days and explained from logs before most customers notice it.

## Terms introduced
- **fleet** — the full population of a maker's devices that are in use.
- **metric** — a small structured record a device sends when a defined event happens.
- **log** — the free-text lines that device software writes as it runs.
- **on-device analysis** — analysis that runs on the device, before logs are overwritten or uploaded.
- **fleet-side analysis** — analysis that runs in the cloud on uploaded metrics and logs from many devices.
- **rule-based tool** — a diagnostic tool that flags only patterns an engineer wrote down in advance.
- **environmental anomaly** — an anomaly caused by the device's surroundings (router, internet provider, setup), not by a device defect.
