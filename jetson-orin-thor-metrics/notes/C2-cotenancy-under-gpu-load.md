# C.2 Co-tenancy under GPU load: control, perception, and a VLA on one GPU

**Source:** book.pdf §C.2 — `doc-c-real-workload/c2-cotenancy-gpu-load-body.tex`  ·  **Status in source:** **in progress — objective and metric only.** The source says: "a reader should take it as a statement of what that section will establish rather than as a result."

## In one sentence
This section will establish what a 100 Hz whole-body-control loop, a nine-network perception roster at 10–15 Hz each, and a vision-language-action model re-planning at a few Hz each achieve when they share one Thor GPU, and which of them still meets its requirement — but in the source as read it carries only the objective, so there is no result here; the committed findings it will draw on are summarised in [[L4-scheduling-ladder]].

## What it measures
Three classes of workload on one GPU, with a metric per class (§C.2 "Objective and metric"):

- **Control loop (WBC):** tail latency — the p99 of observation→torque time in milliseconds — plus the fraction of its 100 Hz ticks that do not complete. The deadline is 10 ms, so the metric is a tail quantity and a completion rate, not a mean throughput.
- **Perception roster (nine networks):** achieved rate in Hz against the rate offered.
- **VLA:** achieved re-planning rate in Hz, the same quantity §C.1 defines.

The median latency of the control loop is deliberately not reported. Its distribution has two modes — a request that reaches the GPU as it arrives, and one that waits behind the co-tenants' queued work — so a median reports which mode is more frequent, not how late the loop runs when it is late. The p99 and the mean retain the second mode.

## How
As stated in the objective (the setup subsection does not yet exist in the source): one Thor GPU, no CPU memory-bandwidth load, GPU-sharing discipline held fixed at a single unmanaged context shared by every tenant. Load is varied on the GPU side alone — by the rate offered to the perception roster and by the presence of the VLA. Precision is fixed per class: fp16 perception, fp32 control, bf16 VLA, so the numbers separate co-tenancy rather than precision. Two scope limits: workloads run on the benchmarking path, not over the robot's ROS2 transport; and the roster is measured on Thor only, so no cross-board comparison.

The CPU-load axis is deferred to a later section, because an effect that reaches across the shared memory controller can be attributed only once the GPU-side effect is known. Precision as a means of protecting the control loop is also its own later section.

## Predicted
Not in source (the prediction subsection is not yet written).

## Measured
Not in source (the measurement subsection is not yet written).

## The gap, and what it means
Not in source. Doc C's status paragraph lists what the later real-workload sections will cover, from committed data under `robot-kernels/`: the queueing decomposition that explains the starvation of the 100 Hz loop; precision as a co-tenancy fix and the shared-controller floor that limits it; serving topology and MPS reservation as the QoS lever; and a closing synthesis placing the real workloads on the roofline (Doc C "Scope and method", status 2026-09-23).

## So what
Interpretation (mine): §B.8 answered this question with proxies and found a 141× tail that still fit the 10 ms budget. §C.2 asks it with the real models. The L4 KEY-LEARNINGS note shows the answer is different: with a real VLA in a shared context the loop misses its deadline, and the fix is isolation plus an SM reservation, not more bits.

## Terms introduced
- **perception roster** — the nine throughput networks (detection, segmentation, pose, scene) that share the GPU with the control loop.
- **observation→torque latency** — the control loop's end-to-end time from sensor observation to torque command; p99 reported.
- **completion rate** — the fraction of the loop's 100 Hz ticks that finish in time.
- **unmanaged shared context** — one CUDA context shared by all tenants with no MPS limits or MIG partition; the baseline sharing discipline.
- **bimodal latency** — a distribution with two modes (served immediately / queued behind co-tenants), for which the median is uninformative.
