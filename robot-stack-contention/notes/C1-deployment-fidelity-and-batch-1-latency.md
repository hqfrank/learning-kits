# C1 — Deployment fidelity and what a latency number means

**Source:** reference-not-replica from [`../../robot-workload-benchmarking/notes/C0-reference-not-replica.md`](../../robot-workload-benchmarking/notes/C0-reference-not-replica.md); the observer effect from [`../../robot-workload-benchmarking/notes/B4-profilers-and-the-observer-effect.md`](../../robot-workload-benchmarking/notes/B4-profilers-and-the-observer-effect.md); re-planning and action chunks from [`../../robot-workload-benchmarking/notes/A6-vla-and-large-models.md`](../../robot-workload-benchmarking/notes/A6-vla-and-large-models.md); every number from [`../constants.json`](../constants.json) by key · **Status:** method note. **All measured values here are illustrative** (class `illustrative`): round teaching numbers, not measurements.

## In one sentence
The full stack runs each service as the robot deploys it but turns every module on at once, so its GPU contention is the stack's real process layout at a heavier load than a freshly booted robot; and every latency number needs its meaning stated: a VLA call is not its GPU time, a batch-1 latency sets a re-planning rate rather than a throughput, and a full-stack latency from the measurement probe is an upper bound.

## What it measures
Three questions decide how far a bench number transfers to the robot:

1. **Fidelity:** does the bench run the same processes, Linux users and core placements as the robot, and what does the bench add?
2. **Budget:** how much GPU time does a model need at its rate, compared with its call time?
3. **Meaning:** what does one latency number promise?

## How
**Counting GPU contexts.** Each process that holds GPU memory is likely one CUDA context (see [[B1-gpu-time-slicing-and-the-dose-curve]]). The method reads the board's per-process GPU-memory accounting in one full-stack window and maps each container to its service.

**The VLA budget.** The method measures a VLA (vision-language-action model) alone at its offered rate, and then next to the full stack. It records the call time and the GPU-busy fraction.

**Batch-1 latency.** The latency timer runs batch 1, one inference at a time. It reports a median over several fresh processes, so that one process's warm-up does not dominate.

## Predicted
This is not a pre-registered test. A naive budget takes the GPU need as call time × rate. The measurement shows that the real need is smaller, and that it is still too large (interpretation).

## Measured
**Fidelity** (illustrative measurement):

| Quantity | Value (illustrative) | Key |
|---|---|---|
| Services in the full stack | 40 | `stack_services` |
| Processes holding GPU memory in the full stack | 6 | `gpu_processes_full_stack` |

A freshly booted robot runs fewer services (source text of `stack_services`). Most of the GPU-memory holders come from the added modules, not from the boot services.

**VLA budget** (illustrative measurement):

| Quantity | Value | Key |
|---|---|---|
| Call time, alone | 150 ms (illustrative) | `vla_call_ms` |
| GPU work inside one call | 120 ms (illustrative) | `vla_gpu_ms_per_call` |
| Offered rate | 5 Hz (illustrative) | `vla_offered_hz` |
| GPU time left free next to the full stack | 0.4 of the time (illustrative) | `gpu_free_next_to_stack` |
| Extra GPU time per output when the GPU is shared | 0.1–0.2 (illustrative) | `sharing_overhead` |

**Batch-1 latency** (illustrative measurement):

| Quantity | Value | Key |
|---|---|---|
| One observation to one action chunk, batch 1 | 250 ms (illustrative) | `batch1_latency_ms` |
| Re-planning rate (1 ÷ latency) | 4 Hz | my estimate from `batch1_latency_ms` |

## The gap, and what it means
**Per service, the full stack is the robot's deployment.** The bench's container configuration should come from the robot's own resolved configuration: the same images, entry points, core sets and Linux users. Each deviation is labelled in the window's metadata. No deviation adds a process that holds GPU memory.

**The full stack is heavier than boot.** Only a few boot services hold GPU memory; most GPU users come from the added modules. So the full stack's GPU contention is the stack's real process layout, with every GPU module on at the same time. The VLA and the synthetic GPU and CPU loads are bench additions. They appear only in named experiments, never in full-stack baselines. Check whether the robot also runs a desktop session; it may hold GPU memory.

**A call is not its GPU time.** At the offered rate, call time × rate is 0.75 s per second (my estimate from `vla_call_ms` and `vla_offered_hz`). The GPU need is only 0.6 s per second (my estimate from `vla_gpu_ms_per_call` and `vla_offered_hz`), because each call contains CPU-side time. So the budget uses the GPU time per call, not the call time.

**The VLA is GPU-time-bound next to the stack.** The VLA needs 0.6 s of GPU time per second, and the stack leaves 0.4 s free (my estimate from `vla_gpu_ms_per_call`, `vla_offered_hz` and `gpu_free_next_to_stack`). The free time supports at most about 3.3 calls per second of the 5 offered (my estimate from `gpu_free_next_to_stack` and `vla_gpu_ms_per_call`). With the sharing overhead, the ceiling falls to about 2.8–3.0 Hz (my estimate from `gpu_free_next_to_stack`, `vla_gpu_ms_per_call` and `sharing_overhead`). The rest of the offered calls are dropped or delayed. B1 shows why the lever is the VLA's GPU time, not its memory traffic ([[B1-gpu-time-slicing-and-the-dose-curve]]).

**Correction kept visible: the VLA's GPU share.** An early estimate of the VLA's share next to the stack used the GPU time per call of a different model version. Recomputed with the version that actually runs next to the stack, the estimate changed. Per-process GPU time in the full stack is still not measured, so both values are estimates.

**Batch-1 latency is a re-planning rate, not a throughput.** At batch 1 and one inference at a time, 250 ms (illustrative, `batch1_latency_ms`) means the policy can re-plan about 4 times per second (my estimate from `batch1_latency_ms`). It does not say how many inferences per second the GPU could serve with batching or overlap. The sibling kit explains re-planning and action chunks in [`../../robot-workload-benchmarking/notes/A6-vla-and-large-models.md`](../../robot-workload-benchmarking/notes/A6-vla-and-large-models.md).

**A full-stack probe latency is an upper bound; a full-stack probe rate is a lower bound.** The measurement probe's own receive delay is about 10 ms at p50 and 30 ms at p99 on a saturated core (illustrative, `probe_receive_delay_ms`). That delay biases every full-stack latency upward (see [[A5-where-to-put-the-observers]]). The probe also loses a few messages in the full stack, so a small rate loss is not evidence of a service slowing down.

## So what
Next to every number, state what was deployed, what the bench added, and what the number promises (interpretation). A call time, a GPU-busy share, a re-planning rate and a probe latency are four different quantities; mixing them gives wrong budgets.

## Terms introduced
- **deployment fidelity** — how closely the bench reproduces the robot's processes, images, Linux users, core sets and placements.
- **GPU-memory holder** — a process that holds GPU memory; each is likely one CUDA context.
- **bench addition** — a process that the bench adds on purpose (the VLA, synthetic loads), only in named experiments.
- **GPU time per call** — the GPU work inside one model call; GPU-busy fraction ÷ call rate.
- **call time** — the wall time of one model call, including CPU-side work.
- **GPU-time-bound** — a model that needs more GPU time per second at its offered rate than its neighbours leave free.
- **batch-1 latency** — the time for one inference when inferences run one at a time with batch size 1.
- **re-planning rate** — the inverse of a VLA's observation-to-action latency; latency is a rate cap. Reused from `../robot-workload-benchmarking/glossary.md`.
- **upper / lower bound (probe)** — full-stack probe latencies include the probe's own delay (upper bound); full-stack probe rates miss some messages (lower bound).
