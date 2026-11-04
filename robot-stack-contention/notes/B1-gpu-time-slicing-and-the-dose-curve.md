# B1 — GPU time-slicing between processes: the dose curve

**Source:** NVIDIA MPS documentation, Architecture (https://docs.nvidia.com/deploy/mps/architecture.html, `mps_no_concurrency_quote`); contexts and time-slicing from [`../../nvidia-gpu-anatomy/notes/07-sharing-the-gpu.md`](../../nvidia-gpu-anatomy/notes/07-sharing-the-gpu.md); every number from [`../constants.json`](../constants.json) by key · **Status:** method note. **All measured values here are illustrative** (class `illustrative` in `constants.json`): round teaching numbers that keep the shape of a finding. They are not measurements.

## In one sentence
Without MPS, the CUDA contexts of different processes take turns on the GPU, so the object detector's extra GPU wait next to a VLA (vision-language-action model) follows the other processes' share of GPU time, not their DRAM traffic or their SM issue rate, and the cost grows faster than the share; the depth camera service is different, because GPU load alone costs it no frames.

## What it measures
**Caveat first.** The dose curve comes from a reduced row: the depth camera service and the object detector only, with an idle CPU pool, one window per arm. In the full stack (every module on) the same mechanism is expected but not tested. Placing full-stack windows on the curve afterwards is a post-hoc reading.

The victim metric is the object detector's **blocked time per frame**. This is the time inside the detector's frame callback when its thread neither runs nor waits for a CPU. Most of it is waiting for the GPU. **C** is one arm's blocked time minus the no-load window. **R** is the C of the VLA arm.

The dose axis is **O**: the other processes' share of GPU-active time, in percentage points. O removes the detector's own GPU time, scaled by the detector's frame rate in that arm.

**Why not "added GPU busy".** The board's GPU-busy percentage (see [`../../robot-workload-benchmarking/notes/B1-gpu-power-memory-metrics.md`](../../robot-workload-benchmarking/notes/B1-gpu-power-memory-metrics.md)) includes the victim's own GPU time. That time falls as the victim slows. So added GPU busy understates the co-tenant's dose.

## How
**Mechanism.** NVIDIA states: "Work launched to the compute engine from work queues belonging to different CUDA contexts cannot execute concurrently." (`mps_no_concurrency_quote`). In the stack, each GPU service and the VLA is its own process with its own CUDA context. So, without MPS, the GPU time-slices between contexts: one context runs and the others wait. A time slice per context is a few milliseconds, about 1 to 5 ms (illustrative, `timeslice_ms`), and it depends on the context's priority.

A process's extra GPU wait is therefore its share of the other contexts' turns plus the cost of each switch. A switch saves and restores state and refills caches and TLBs. In this mode there is **no SM contention between processes**. While another context holds the GPU, the detector's kernels cannot run at all.

Analogy: one stove shared by several cooks in turns. A cook waits for the other cooks' turns, not for a free burner.

**Experiments.**

1. **First test.** The camera service and the detector, with one co-tenant per arm: a compute kernel on all SMs; a streaming memory copy with the same GPU time; and the VLA.
2. **Dose series.** A compute co-tenant at several busy/idle patterns, the VLA arm, and no-load windows at the start and the end. Two burst lengths at the same duty test whether burst length matters.

## Predicted
These predictions were written before the dose series ran.

- Class "dose explains part, plus something else", or "dose explains". At the highest compute dose, C was predicted to stay below R.
- Longer bursts at the same share were predicted to cost more than short bursts.
- The class rule: C\* (the compute curve's value at the VLA's dose) ÷ R inside a band around 1 means "dose explains".

## Measured
**First test, first reading (class "neither alone", stands as recorded).** The compute arm gave about 40 % of R (my estimate from `dose_curve_points` and `dose_vla_point`: 40 ms ÷ 100 ms). The copy co-tenant at equal GPU time added 0 ms (illustrative, `dram_null_added_ms`).

**Dose series.** The detector's blocked time added per frame, an illustrative measurement:

| Point | O (points) | Added blocked (ms per frame) | Key |
|---|---|---|---|
| No load | 0 | 0 | `dose_curve_points` |
| Compute, low dose | 40 | 40 | `dose_curve_points` |
| Compute, middle dose | 60 | 80 | `dose_curve_points` |
| Compute, high dose | 80 | 160 | `dose_curve_points` |
| **VLA** | 65 | 100 | `dose_vla_point` |

All five rows are illustrative.

| Quantity | Value | Key |
|---|---|---|
| Slopes between points (0–40, 40–60, 60–80) | 1 / 2 / 4 ms per point (illustrative) | `dose_slopes` |
| Compute curve at the VLA's dose, C\* | 100 ms (my estimate from `dose_curve_points`, straight line from 60 to 80) | — |
| C\* ÷ R | 1.0 (my estimate from `dose_curve_points` and `dose_vla_point`) | — |
| C at the highest dose ÷ R | 1.6 (my estimate from `dose_curve_points` and `dose_vla_point`) | — |
| Burst length effect, 3 ms vs 30 ms bursts at the same share (lengths from the source text of `burst_length_effect_ms`) | 0 ms (illustrative) | `burst_length_effect_ms` |

**Where the detector's rise comes from next to the VLA.** In the full stack → full stack + VLA step (not the camera-plus-detector row), the rise is about 70 ms blocked, 20 ms CPU wait and 10 ms slower run per frame (illustrative, `detector_vla_added_blocked_wait_run`). Most of it is GPU wait.

## The gap, and what it means
**Verdict, as pre-registered: "dose explains".** The VLA point lies on the compute arms' curve. The compute co-tenant moves almost no DRAM traffic and keeps the SMs issuing far more often than the VLA does. It still costs the detector the same at the same share. So at the VLA's dose, extra DRAM traffic and SM issue rate add nothing measurable. The share of GPU time accounts for the cost.

**Correction kept visible: the first test's "neither alone" was the low end of a convex curve.** The first test's compute arm sat at about 40 points against the VLA's 65 (illustrative, `dose_curve_points`, `dose_vla_point`). The first reading judged the dose from added GPU busy and so overestimated it. On a convex curve, a dose well below the VLA's gives much less than R. The pre-registered class of the first test stands as recorded; the dose series explains it.

**Two predictions were wrong.** The highest dose cost more than R, not less (my estimate from `dose_curve_points` and `dose_vla_point`). Burst length did not matter (illustrative, `burst_length_effect_ms`). Bursts well below one time slice (under 1 ms, `timeslice_ms`) were not tested.

**Correction kept visible: "SM contention".** An earlier reading listed SM contention between the detector and the VLA as an alternative cause. None of these tests ran MPS, so there is no SM contention between processes and that alternative does not apply. How the wait splits between slice waiting and switch cost was not measured.

**The detector blocks; it does not spin.** Its user instructions per frame stay flat while its blocked time rises several-fold, and its voluntary context switches rise.

**Why the full stack sits below the curve (post-hoc).** In the full stack the detector also waits for the CPU (see [[A1-cpu-queueing-on-a-shared-pool]]). It then submits GPU work less often and meets less GPU contention per frame than in the idle-pool row. This was not separated from other causes.

### The camera is different
The depth camera service keeps about 30 Hz alone (illustrative, `camera_hz_alone`). One factor was varied per window:

| Factor | Camera loss (illustrative) | Key |
|---|---|---|
| GPU compute co-tenant, idle CPU pool | 0 Hz at every dose tested | `camera_gpu_only_loss_hz` |
| Shared-pool CPU load, at half the full stack's camera wait | 0.3 Hz | `camera_pool_loss_hz` (`half_full_wait`) |
| Shared-pool CPU load, at twice the full stack's camera wait | 6 Hz (window void by the rate gate) | `camera_pool_loss_hz` (`twice_full_wait`) |
| The full stack's extra topic subscribers (fan-out) | 1 Hz | `camera_fanout_loss_hz` |
| Full stack, reference | 5 Hz | `camera_full_stack_loss_hz` |

Pre-registered verdicts:

- **GPU: minor.** No measurable loss at any GPU dose tested (illustrative, `camera_gpu_only_loss_hz`).
- **Shared pool: "undecided at dose".** The only valid pool arm lies below the full stack's camera wait. The higher arm is void, so it cannot decide the class. A post-hoc reading that keeps the void arm gives the pool a larger share; it is labelled post-hoc and does not replace the verdict.
- **Fan-out: a minor share,** about one fifth of the full-stack loss (my estimate from `camera_fanout_loss_hz` and `camera_full_stack_loss_hz`).

**Correction kept visible: the camera's loss is CPU-side; GPU load alone costs it nothing.** A substantial GPU share of the camera loss was predicted. The illustrative measurement gives none. **The three loads were not tested together.** The GPU arms ran with frame-time slack that the full stack does not leave, and the full stack plus VLA dose lies beyond the highest GPU arm.

## So what
- **For a VLA next to the full stack (recommendation):** budget the VLA's GPU time. The lever is its rate, its batch or its model size, not its memory traffic. Near the VLA's dose each point of O costs more than the average (illustrative, `dose_slopes`), so the first points cut buy back the most. See [[C1-deployment-fidelity-and-batch-1-latency]].
- **General lesson (interpretation):** for time-sliced GPU sharing, plot the victim's wait against the other processes' share of GPU time, not against total GPU busy.

The sibling kit shows how a sharing discipline protects a control loop next to a VLA: [`../../jetson-orin-thor-metrics/notes/L4-scheduling-ladder.md`](../../jetson-orin-thor-metrics/notes/L4-scheduling-ladder.md).

## Terms introduced
- **time-slicing (GPU)** — the GPU runs one CUDA context at a time and switches between contexts; without MPS, kernels of different processes never overlap.
- **time slice** — how long the GPU runs one context's work before it switches; a few milliseconds, set by priority.
- **co-tenant** — a synthetic or real process that shares the GPU with the victim.
- **blocked time** — time inside a frame callback when the thread neither runs nor waits for a CPU; here mostly GPU wait.
- **dose (O)** — the other processes' share of GPU-active time, in percentage points; the x-axis of the dose curve.
- **dose curve** — the victim's added blocked time plotted against O.
- **C, R, C\*** — one arm's added blocked time; the VLA arm's added blocked time; the compute curve's value at the VLA's dose.
- **convex** — a curve whose slope rises with dose: each extra point costs more than the last.
- **fan-out** — extra subscribers and topics that a publisher must serve.
- **CUDA context** — a process's GPU state; the GPU time-slices between contexts. Reused from `../nvidia-gpu-anatomy/glossary.md`.
