# B.4 GEMM-victim interference

**Source:** book.pdf §B.4 — `doc-b-proxy-workload/gemm-victim.tex`; Table B.4.1 (the two mechanisms), Figures B.4.1 (controller slowdown vs footprint), B.4.2 (lockout onset)  ·  **Status in source:** D (drafted, awaiting review)

## In one sentence
"Memory interference" on these boards is two different mechanisms with two different remedies: a CPU co-tenant contends for the memory controller only once the victim GEMM spills L2 (onset tracks 4 MB on Orin, 32 MB on Thor; up to 1.53× and 2.25–2.53×), while a GPU co-tenant starves the victim completely — not proportionally — once it occupies about 8% (Orin) or 14% (Thor) of the warp slots.

## What it measures
Two metrics for two conflicts, with a small compute-bound GEMM (a proxy for a small-CNN robot inference kernel) as victim. For **controller contention** from a CPU co-tenant: a count ratio — GEMMs completed solo in a fixed window over GEMMs completed with the aggressor present (invariant to batching per launch). For **SM co-scheduling** from a GPU co-tenant: does the victim run at all while the co-tenant is alive, and at what co-tenant occupancy does that change? Answered from per-GEMM completion times while sweeping the co-tenant's warp-slot occupancy (§B.4 "Objective and metric").

## How
**Controller sweep.** Two victims: an fp16-input FP32-accumulate tensor-core GEMM (memory-exposed) and a pure fp32 CUDA-core GEMM of the same shapes (compute-bound control). Footprint swept 2–128 MB across each board's L2 boundary. Aggressor: a CPU memory-bandwidth hog (≈ 108 GB/s), which occupies no SMs. 2 s counting window.

**Co-scheduling sweep.** One fixed fp16 tensor GEMM (N = 1024, 8 MB), one GEMM per host synchronisation so every completion is timestamped. Aggressor: a GPU streaming read-hog, grid-stride over a 64 MB buffer, whose warp-slot occupancy is set by block count independent of footprint. The co-tenant runs in the **same process and CUDA context** as the victim on a separate stream, so what is observed is the hardware block scheduler, not MPS and not OS time-slicing. 4 s window, longer than the co-tenant's ≈ 2.5 s lifetime (§B.4 "Experiment setup").

## Predicted
Two mechanisms with distinct signatures. **Controller contention** should appear only once the victim's footprint spills L2, tracking the L2 boundary. For **SM co-scheduling**, a discriminating prediction: if the block scheduler shares warp slots proportionally, a co-tenant at fraction f of the slots leaves roughly 1 − f for the victim, which degrades gracefully; if admission is all-or-nothing above some occupancy, the victim completes nothing until the co-tenant drains. The two are separable in the completion-time sweep: proportional sharing keeps the first completion near zero at every occupancy; a threshold makes it snap to the co-tenant's lifetime once crossed (§B.4 "Prediction model").

## Measured
Controller: slowdown = solo count / co-run count in 2 s. Co-scheduling: at each co-tenant occupancy, the first victim-GEMM completion time and the count of GEMMs completing before t = 1 s. The **lockout onset** is the occupancy at which the regime flips, reported in requested warp-slot occupancy (the profiler's achieved reading agrees at the working point, ≈ 25% requested reads ≈ 25% achieved, but is non-monotone at low block counts).

| Mechanism (isolating aggressor) | Orin | Thor |
|---|---|---|
| Controller contention (CPU hog) | peaks 1.53× at 8 MB | onsets at 32 MB, 2.25–2.53× |
| SM co-scheduling lockout onset (GPU hog) | ≈ 8% occupancy | ≈ 14% occupancy |

(§B.4 Table B.4.1.)

## The gap, and what it means
**Controller contention onsets at L2 spill.** The fp16 tensor victim slows only once its footprint spills L2 — just past 4 MB on Orin, 32 MB on Thor — the 8× ratio of L2 capacities. The fp32 CUDA-core victim at the same footprints stays flat: the discriminator is arithmetic intensity, not size. Tensor cores retire FLOPs fast enough to turn memory-bound on spilling L2; the slower fp32 path stays compute-bound.

**Past the peak the boards diverge, and a larger footprint is not worse.** On Orin the slowdown peaks just past 4 MB then recovers toward 1.0 by 128 MB; on Thor it onsets at 32 MB and keeps climbing at the largest footprint. As the square GEMM grows its arithmetic intensity rises (N³ compute against N² data), so on Orin it turns compute-bound and the exposure vanishes, while Thor's far higher tensor throughput keeps it memory-bound. Controller exposure is set by the victim's memory-demand rate, not its footprint — the faster datapath is the more exposed one. The profiler confirms it is the controller: under the CPU hog only `long_scoreboard` grows (same signature as §B.3).

**SM co-scheduling is bistable, not a graded share.** Below a board-specific co-tenant occupancy the victim co-runs, first GEMM completing immediately; above it the victim is locked out until the co-tenant drains. The transition is a sharp cliff at ≈ 8% (Orin) and ≈ 14% (Thor) of warp slots. This is far below fair share — a co-tenant on an eighth of the slots locks the victim out with the rest idle — and since both share one context, it is the hardware block scheduler's own behaviour, not MPS or OS (§B.4 "Comparison and discussion").

## So what
The source states it: a batch-1 robot-inference GEMM is compute-bound, so controller contention leaves it untouched, yet a light GPU co-tenant past the occupancy onset starves it for the co-tenant's whole life. Real-time work cannot rely on fair sharing; it needs QoS partitioning — MIG, MPS resource limits, or scheduling priority. The two mechanisms have different remedies (footprint control for the controller, occupancy control or spatial partitioning for lockout), so collapsing them into one "interference" number would mislead the silicon decision.

## Terms introduced
- **controller contention** — slowdown from two tenants sharing the memory controller's bandwidth; onsets when the victim spills L2.
- **SM co-scheduling** — the hardware block scheduler placing two kernels' blocks on the same SMs.
- **lockout onset** — the co-tenant warp-slot occupancy above which the victim completes no work until the co-tenant drains; ≈ 8% Orin, ≈ 14% Thor.
- **bistable** — having two stable regimes (co-running / locked out) with a sharp transition and no graded middle.
- **requested occupancy** — the warp-slot fraction set by the co-tenant's block count; the reproducible knob.
- **grid-stride loop** — a kernel pattern where each thread strides through a buffer by the grid size, so block count sets occupancy independent of footprint.
- **count ratio** — GEMMs completed solo over GEMMs completed co-run in a fixed window; robust to per-launch batching.
- **MPS** — NVIDIA Multi-Process Service, which lets several processes share one GPU context with optional per-client SM limits.
