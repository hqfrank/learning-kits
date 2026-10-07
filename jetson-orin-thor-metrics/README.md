# Jetson Orin (sm_87) and Thor (sm_110): a Measured Reference for Robotics Workloads — study notes

## What the book says, in one paragraph

The book is a measured reference for two NVIDIA Jetson boards — AGX Orin (Ampere, sm_87) and Thor
T5000 (Blackwell, sm_110) — written for engineers deciding how to run robotics workloads on them.
Its single thesis is that **TOPS predicts almost nothing that matters for these workloads; memory
does.** Doc A measures the boards' fixed capabilities and shows the decisive differences are in
memory, not compute: Thor has 8× the L2 (32 vs 4 MB) and about 1.3× the DRAM bandwidth, an
L2-resident working set runs 12–15× faster than a DRAM-resident one, L2 latency did not improve
between generations (only capacity grew), and the datasheet tensor peaks need Thor's 5th-generation
`tcgen05` datapath that a hand-written kernel reaches at only 26–38% while a tuned library reaches
55–75%. Doc B measures what happens under interference and finds the hazards are memory and
scheduling, not compute: a compute kernel is immune to copy traffic (refuting an older Tegra
result), cache eviction punishes latency-bound victims at the L2 boundary before the controller
saturates, a GPU co-tenant on as little as 8–14% of the warp slots locks a victim out entirely
(bistable, not graded), a compute-bound tenant starves a memory-bound one far more than the
reverse, same-class pairs keep their aggregate throughput so the co-tenancy cost is tail latency
not throughput, and a 100 Hz control loop's p99 is inflated 141× (to 5.9 ms, still under its 10 ms
budget) by a full co-tenant roster plus CPU load. Doc C turns to the deployed models: the π0.5
vision-language-action model runs in 90 ms (16-bit) to 53 ms (8-bit) on Thor, is a bandwidth
problem not a TOPS problem (latency tracks bytes moved, not nominal precision), and a
first-principles prediction built from measured per-shape GEMM rates is optimistic by a consistent
1.40–1.50×. The supplementary L4 campaign closes the loop operationally: on one Thor GPU the GPU
**sharing discipline** decides whether the control loop holds — a shared context breaks it (64×
p99, 51% ticks dropped), a separate process plus a 25–35% MPS SM cap returns it to zero drops under
the deadline, and no discipline moves the ~172 GB/s CPU-memory-load floor at which everything
collapses.

These are study notes for that book (rung 1 of a four-rung learning kit: notes → diagram → explorer
→ video). Nothing here is a new measurement. Every number traces to the source; see `SOURCES.md`.

## How to read these notes

Read in this order. Doc A establishes the ceilings the rest of the book measures against; Doc B
builds on A; Doc C and the L4 ladder build on both.

### Start here
- [`SOURCES.md`](SOURCES.md) — what the material is, where it lives, how it was read, and the
  reading conventions.
- [`notes/00-platforms.md`](notes/00-platforms.md) — the two boards' device-queried facts (Table 1);
  every later note cites it.

### Doc A — measured hardware capabilities (the fixed ceilings)
Compute rates:
- [`notes/A1-fp-int-pipe-interleaving.md`](notes/A1-fp-int-pipe-interleaving.md) — issue rates and the dispatch bound; why FP/INT do not overlap.
- [`notes/A2-cuda-core-ceilings.md`](notes/A2-cuda-core-ceilings.md) — FP32 / FP16 / INT8 CUDA-core roofs; Thor has no double-rate packed FP16.
- [`notes/A3-tensor-core-ceilings.md`](notes/A3-tensor-core-ceilings.md) — classic `mma` floor vs `tcgen05` ceiling; the programmability cost.
- [`notes/A4-nvfp4-ceiling.md`](notes/A4-nvfp4-ceiling.md) — NVFP4 dense and 2:4-sparse; the delivered sparsity multiplier is 1.40×, not 2×.

Memory hierarchy:
- [`notes/A5-l1-bandwidth-ceiling.md`](notes/A5-l1-bandwidth-ceiling.md) — per-SM L1 read roof; clock-bound on a fixed port.
- [`notes/A6-bandwidth-vs-footprint.md`](notes/A6-bandwidth-vs-footprint.md) — L2 and DRAM plateaus and the capacity cliff; the 12–15× L2:DRAM ratio.
- [`notes/A7-latency-landmarks.md`](notes/A7-latency-landmarks.md) — L1 / L2 / DRAM dependent-load latencies; L2 latency did not improve.

### Doc B — proxy-workload behaviour under interference
- [`notes/B1-copy-engine-dram-direction.md`](notes/B1-copy-engine-dram-direction.md) — copy-on-compute refuted; direction decides memory interference; the `memset` exception.
- [`notes/B2-cache-level-interference.md`](notes/B2-cache-level-interference.md) — eviction at the L2 boundary; latency-bound victims are the casualties.
- [`notes/B3-matrix-profile-stall-decomposition.md`](notes/B3-matrix-profile-stall-decomposition.md) — occupancy does not predict issue rate; the dominant stall does.
- [`notes/B4-gemm-victim-interference.md`](notes/B4-gemm-victim-interference.md) — two mechanisms: controller contention at L2 spill vs bistable SM lockout at 8–14%.
- [`notes/B5-tensor-under-cpu-contention.md`](notes/B5-tensor-under-cpu-contention.md) — slowdown tracks operand-byte demand; the bandwidth cliff at half the CPU's ceiling.
- [`notes/B6-cotenancy-interference-matrix.md`](notes/B6-cotenancy-interference-matrix.md) — compute starves memory, not the reverse; the mechanism is SM co-scheduling.
- [`notes/B7-aggregate-throughput.md`](notes/B7-aggregate-throughput.md) — same-class pairs keep aggregate throughput; the cost is latency, not throughput.
- [`notes/B8-cotenancy-real-shape-mix-ladder.md`](notes/B8-cotenancy-real-shape-mix-ladder.md) — the WBC p99 tail: 141× solo under the full roster plus CPU hog, still under 10 ms.

### Doc C — real-workload behaviour (the deployed models)
- [`notes/C1-pi05-solo-latency.md`](notes/C1-pi05-solo-latency.md) — π0.5 observation→action latency; a bandwidth problem, prediction optimistic by 1.40–1.50×.
- [`notes/C2-cotenancy-under-gpu-load.md`](notes/C2-cotenancy-under-gpu-load.md) — the three-class deployment question; **objective only in the source — no result yet.**

### Supplementary — the operational conclusion
- [`notes/L4-scheduling-ladder.md`](notes/L4-scheduling-ladder.md) — from the L4 KEY-LEARNINGS: shared context → separate process → MPS → MPS + SM cap (the fix) → MIG (deferred); the ~172 GB/s floor.

### Reference files
- [`glossary.md`](glossary.md) — one definition per term, alphabetical.
- [`constants.json`](constants.json) — every measured constant the notes cite, each with value, unit, board and source. Load it; do not retype the numbers.

## Conventions

- "Orin" = NVIDIA Jetson AGX Orin (Ampere, sm_87). "Thor" = NVIDIA Jetson Thor T5000 (Blackwell, sm_110).
- All numbers are at MAXN with GPU clocks locked and devfreq-verified unless a note says otherwise.
- Ranges and `≈`/`~` marks are kept where the source uses them.
- Notes use the ASD-STE100-at-80% style: one fact per sentence, active voice, one term per concept, caveats before results.
