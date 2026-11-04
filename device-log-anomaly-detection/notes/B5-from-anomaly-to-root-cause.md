# B5 — From anomaly to root cause: workflows, transition edges, and state machines

**Source:** Du et al., "DeepLog", CCS 2017 (https://nlp.cs.utah.edu/assets/pdfs/du2017deeplog.pdf), §4.4 (workflow construction and diagnosis); He et al., ISSRE 2016, §III-B (session windows); generalised from internal design documents of a device-health programme (see [`../SOURCES.md`](../SOURCES.md)). · **Status:** concept primer.

## In one sentence
An anomaly score says *which window* is odd; root-cause analysis asks *which path through the code* was taken, so it rebuilds per-thread event sequences, compares their transitions with the normal workflow mined from many devices, and shows the engineer where the sequence left the normal path.

## What it is
**Root-cause analysis (RCA)** is the step from "this window is anomalous" to "this is what went wrong". In a log pipeline it has three parts:

1. **Narrow the search** — choose which devices and time ranges to read, using the metric anomaly ([[B4-fleet-trend-detection]]).
2. **Rebuild the workflow** — recover the ordered sequence of events for each task from the interleaved stream.
3. **Compare with normal** — find where the anomalous sequence departs from the normal workflow, and which parameters are out of range.

A **workflow** (empirical control-flow graph) is a directed graph whose nodes are templates and whose edges are observed transitions "template *i* is followed by template *j*". DeepLog builds such a workflow model from normal logs and uses it to show the engineer which task an anomaly belongs to (Du et al. 2017, §4.4).

## How it works
**Cascade, not parallel.** Two architectures were weighed in the internal design (generalised):

- **Cascade** — metrics detect first; the devices that contribute most to the anomaly are chosen; only their logs, for the anomaly's time range, are fetched and analysed. Fewer devices to process, and the metric says roughly when and what to look for. It misses faults that never show in metrics.
- **Parallel** — logs from the whole test population are analysed continuously, alongside metrics, either as one fused model or as two models whose results are fused. It learns group behaviour from logs and catches faults metrics miss. It costs far more compute and does not extend to devices whose logs are not uploaded.

The design started with the cascade: lower risk, a working result sooner, and a path to the parallel form later.

**Pass the context.** In a cascade the log analyser should be told *which* metric fired (for example, "disconnects with reason code 15", the IEEE 802.11 code for a 4-way handshake timeout) and *when*. Two traps: metrics may be aggregated hourly or daily, and device logs may use local time while metrics use UTC.

**Mining transition edges.** Count vectors lose order ([[B2-windows-and-count-vectors]]). Transition counts recover it:

1. **Partition** the stream by process ID and thread ID. This separates concurrent writers.
2. **Sort** each partition by timestamp. Drop lines with impossible timestamps (for example, from a log cache replayed after a reboot or a clock reset).
3. **Count transitions.** For *N* templates, build an *N* × *N* matrix *A*. For each consecutive pair (*i*, *j*) in a partition, add 1 to *A*[*i*][*j*]. Skip the edge into a "task start" template, so that one task's end is not linked to the next task's start.

*A* is the weighted adjacency matrix of the empirical control-flow graph. Ties in timestamp make some edges ambiguous; aggregated over many windows, the occasional wrong order averages out.

**Two kinds of graph anomaly** (internal research design, generalised):

- **Sequence anomaly** — an expected child node does not appear within its expected time lag after its parent. Example: `association started` is not followed by `association complete` within its usual interval.
- **Distribution anomaly** — the probability of an edge changes. Example: after `disconnected`, the share of transitions to `reconnect success` falls and the share to `network bounce` rises.

The statistics of normal transitions cannot be learned from one device in one short test. They need many devices over long periods, which is why fleet-scale mining matters.

**State-machine views.** Engineers think in state machines: `scanning → associating → authenticating → connected`. Two tools follow:

- **Golden sequence** — the normal event sequence for a task, learned from many healthy logs and shown next to the anomalous one, so a new engineer can see the divergence without reading source code.
- **State-machine search** — the user defines an ordered list of expected events and a maximum time span; the tool finds every match in a log and shows each one with its raw lines. This replaces hand-written matching scripts in lab stress tests.

**Parameters as evidence.** Template parameters carry the cause: the reason code, the signal level, the latency. Plotting a chosen parameter over time, or adding a few selected parameters as features, often names the cause directly. Add parameters selectively; each one adds a dimension.

**Execution replay.** If each template is linked to its print statement in the source, the event sequence becomes a path through the code, and the engineer can replay the execution that led to the fault.

## How it is measured or used
- The output is a short list of anomalous windows, their top templates, the departing edge, and the raw lines, not a verdict.
- Success is measured as engineer time to root cause and the share of cases where the output alone was enough to start an investigation ([[C1-the-ground-truth-problem]]).

## Common confusions
- **"Sort the whole log by time and read transitions."** Across threads that yields edges that never happen in the code. Partition first.
- **"The anomalous template is the cause."** It is often a symptom downstream of the cause, in another component (DHCP, time sync, a kernel driver) ([[C4-lessons]]).
- **"A workflow model is the source code's control-flow graph."** It is the *observed* graph. Paths the code allows but normal devices never take are absent, which is useful: their appearance is a signal.

## Why it matters for fleet operations
A score without a path leaves the engineer where they started: with a large log and a hunch. A transition view, a golden sequence, and the parameters at the departure point turn an anomaly into a hypothesis an engineer can test in minutes.

## Terms introduced
- **root-cause analysis (RCA)** — the step from "this is anomalous" to "this is what went wrong".
- **cascade architecture** — metrics detect first; logs of the contributing devices are analysed after.
- **parallel architecture** — logs and metrics are analysed continuously side by side, with fused results.
- **workflow (empirical control-flow graph)** — a graph of templates (nodes) and observed transitions (edges).
- **transition count matrix** — N × N counts of "template i followed by template j" within one thread.
- **sequence anomaly** — an expected child event is missing within its expected time lag.
- **distribution anomaly** — the probability of a transition edge has changed.
- **golden sequence** — the normal event sequence for a task, learned from healthy logs.
- **state-machine search** — finding every occurrence of a user-defined ordered event pattern within a time span.
- **execution replay** — mapping templates back to print statements to follow the code path taken.
