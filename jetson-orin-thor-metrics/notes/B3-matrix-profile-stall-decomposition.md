# B.3 matrix_profile stall decomposition

**Source:** book.pdf §B.3 — `doc-b-proxy-workload/matrix-profile.tex`; tables B.3.1 (stall decomposition, solo), B.3.2 (Thor solo vs CPU hog)  ·  **Status in source:** D (drafted, awaiting review)

## In one sentence
Three matrix-multiply kernels held at nearly equal occupancy (62–74%) differ in runtime by up to 4.24×, so occupancy does not predict issue rate — the dominant stall class does — and under a CPU memory hog only the stall that crosses the controller to DRAM (`long_scoreboard`) grows, which is the signature of shared-controller contention that §B.4 and §B.5 rely on.

## What it measures
The warp-issue-stall decomposition: the average cycles a warp is stalled per issued instruction, broken down by reason — a long-latency memory-scoreboard wait (`long_scoreboard`, to DRAM), a load/store-unit throttle (`lg_throttle`), an on-chip memory-I/O throttle (`mio_throttle`), a short-latency scoreboard wait (`short_scoreboard`, shared memory / dependent math), and barrier. Being per-instruction, the metric is tolerant of clock variation. The experiment tests the common assumption that achieved occupancy is a proxy for issue rate (§B.3 "Objective and metric").

## How
One 1024 × 1024 FP32 matrix multiply (2N³ = 2.147 GFLOP) as three implementations of increasing data reuse: **naive** (every operand from DRAM), **tiled** (32 × 32 tiles staged in shared memory, about 32× global-load reuse), and **register-tiled** (a 4 × 4 register micro-tile over a 64 × 64 output block). All three do identical arithmetic and sit at 62–74% occupancy by design: the naive and tiled kernels launch 1024-thread (32-warp) blocks, two-thirds of the 48-warp maximum, and the register-tiled kernel's heavier register use holds it in the same band. Each is profiled solo and under a 12-thread CPU memory-bandwidth hog (≈ 108 GB/s aggregate, 60 s window) (§B.3 "Experiment setup").

## Predicted
Occupancy supplies warps to hide latency, so the occupancy-as-proxy assumption predicts similar issue efficiency and runtime across the three kernels at fixed occupancy. A large runtime spread at pinned occupancy disproves it (§B.3 "Prediction model").

## Measured
cyc/inst = 1 + Σ_r stall_r, and T ∝ N_inst × cyc/inst.

Solo, MAXN (§B.3 Table B.3.1):

| Stall (cyc/inst) | Orin naive | Orin tiled | Orin reg | Thor naive | Thor tiled | Thor reg |
|---|---|---|---|---|---|---|
| long_scoreboard (to DRAM) | 9.44 | 8.79 | 2.51 | 4.33 | 3.87 | **10.37** |
| lg_throttle (LSU) | 6.20 | 0.11 | 0.16 | 1.50 | 0.00 | 0.03 |
| mio_throttle (on-chip) | 0.00 | 12.24 | 3.22 | 0.02 | 11.70 | 1.26 |
| short_scoreboard | 0.01 | 0.13 | 1.97 | 0.01 | 0.49 | 2.88 |
| barrier | 0.00 | 3.51 | 1.38 | 0.00 | 1.93 | 0.99 |
| Achieved occupancy | 66.6% | 66.6% | 62.5% | 66.4% | 66.6% | 74.0% |
| Runtime (rel. to reg) | 4.24× | — | 1.0× | 3.21× | — | 1.0× |

Thor, solo vs CPU hog (§B.3 Table B.3.2; Orin contended was not run):

| Thor kernel | long_scoreboard solo | long_scoreboard + hog | mio_throttle solo | mio_throttle + hog |
|---|---|---|---|---|
| naive | 4.33 | 11.70 | 0.02 | 0.02 |
| tiled | 3.87 | 6.56 | 11.70 | 11.70 |
| reg | 10.37 | 18.09 | 1.26 | 0.68 |

## The gap, and what it means
**Occupancy does not predict issue rate.** Occupancy is nearly flat across the three kernels, yet runtime spans a factor of four. The register-tiled kernel makes the point across boards: its occupancy rises from Orin to Thor, yet its DRAM wait balloons to become its dominant cost. Occupancy and issue efficiency move in opposite directions.

**The mechanism is portable but the tuning is not.** On Orin, tiling collapses the load-throttle stall, register reuse cuts the on-chip throttle, and the register-tiled kernel is fastest on the lowest total stall. On Thor the register micro-tiling that hid Ampere's latency does not hide Blackwell's longer global-load latency; the register-tiled kernel's `long_scoreboard` becomes its dominant cost and narrows its lead. An Ampere-tuned kernel is not automatically Blackwell-tuned.

**Contention confirms the solo figures are a lower bound.** Under the CPU hog only `long_scoreboard` grows, while `mio_throttle` is unmoved, so the added degradation is specifically shared-controller contention. The kernel that lives on the DRAM stall (reg) is hit hardest; the on-chip-bottlenecked tiled kernel is the most robust (§B.3 "Comparison and discussion").

## So what
Interpretation (mine, from the source): when profiling a robotics kernel on these boards, read the stall breakdown, not the occupancy number. A kernel whose dominant stall is `long_scoreboard` will degrade under any CPU memory load; one bottlenecked on-chip will not.

## Terms introduced
- **warp-issue stall** — a cycle in which a resident warp is not selected to issue, attributed to a reason; measured as cycles per issued instruction.
- **long_scoreboard** — stall waiting on a long-latency (global/DRAM) memory dependency; the one stall that crosses the memory controller.
- **lg_throttle** — stall because the load/store unit's queue for global memory is full.
- **mio_throttle** — stall because the on-chip memory-I/O queue (shared memory, special ops) is full.
- **short_scoreboard** — stall waiting on a short-latency dependency (shared memory, dependent math).
- **achieved occupancy** — the active-warp fraction the profiler observes, as opposed to the theoretical maximum.
- **register tiling** — holding a small output micro-tile in registers so operands are reused without re-loading.
- **ncu** — NVIDIA Nsight Compute, the kernel profiler that reports the stall counters.
