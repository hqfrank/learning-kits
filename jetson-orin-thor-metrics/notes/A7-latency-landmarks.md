# A.7 Latency landmarks

**Source:** book.pdf §A.7 — `doc-a-capabilities/latency-landmarks.tex`; tables A.7.1 (parameters), A.7.2 (measured landmarks)  ·  **Status in source:** D (drafted, awaiting review)

## In one sentence
A dependent load costs about 40 cycles from L1 on both boards (29.9 ns Orin, 25.3 ns Thor), about 150 ns from L2 on both boards (146 / 156 ns — fixed in time, not cycles), and 675 / 510 ns from DRAM, so Thor's memory advantage at L2 is that more data stays resident, not that resident data is reached faster.

## What it measures
The dependent-load latency of each level of the memory hierarchy — the time to complete one load whose address depends on the previous load, so the hardware cannot overlap accesses. It produces L1, L2 and DRAM latency in nanoseconds and cycles, plus the capacity cliffs between levels. Latency is what a latency-bound kernel feels directly; it is a real-time figure that bandwidth does not capture, and it anchors the latency axis of the roofline (§A.7 "Objective and metric").

## How
One thread on one SM chases a random pointer cycle through a buffer. The buffer is a Sattolo random permutation cycle (one full-length cycle, so the chase cannot fall into a short loop), 64-byte aligned, swept from 1 KB to 256 MB at quarter-octave steps. K = 2²² dependent loads are timed; the minimum over 5 trials is kept. Two variants: `default` issues an ordinary global load through L1; `cg` (`__ldcg`, the PTX `.cg` operator) bypasses L1 and reads from L2, so its first shelf is the L2 latency and the L1 latency is the difference between variants on the first shelf. Times convert to nanoseconds using the runtime-verified clock (§A.7 Table A.7.1).

## Predicted
Each level's latency is a per-level access cost plus, for off-SM levels, an on-chip round trip. Expectations level by level (§A.7 "Prediction model"):

- **Cliffs** at the L2 capacities (4 / 32 MB) — the one capacity-derivable landmark.
- **L1 hit** — the LSU load-to-use pipeline depth, ≈ 30–40 cycles for Ampere-class cores (from published microbenchmarks). As a fixed cycle count it converts to ≈ 27 ns at Orin's 1.30 GHz and proportionally less on Thor.
- **L2** — ≈ 200 cycles for this class. Whether it holds fixed in cycles (pipeline-dominated) or in nanoseconds (interconnect flight time) is what the two-board comparison tests.
- **DRAM** — the LPDDR device read (tRCD + tCL) is 30–40 ns and only a floor; the pointer-chase latency should be dominated by the on-chip round trip through controller and interconnect, so several times the device read.

The `cg` variant should sit at the L2 shelf from the smallest footprint with a single step at the L2 capacity.

## Measured
Cycles per load are total timed cycles over K; a shelf is the mean of per-point minima over the flat run; a cliff is the midpoint of the step interval.

| Landmark | Orin | Thor |
|---|---|---|
| L1 shelf | 29.9 ns (38.9 cyc) | 25.3 ns (39.8 cyc) |
| L2 shelf | ≈ 146 ns | ≈ 156 ns |
| L2 cliff | 4.0 MB | 32 MB |
| DRAM shelf | ≈ 675 ns | ≈ 510 ns |
| L2-hit saving vs DRAM | ≈ 530 ns (4.6×) | ≈ 355 ns (3.3×) |

(§A.7 Table A.7.2.)

## The gap, and what it means
The L2 cliffs fall at each board's L2 capacity, and the `cg` variant confirms them: flat at the L2 shelf from 1 KB with a single step at capacity. The L1 shelf is about 40 cycles on both boards (38.9 vs 39.8), confirming the fixed pipeline-depth prediction; the nanosecond difference is purely the clock.

Two comparisons carry into the roofline. First, L2 latency did not improve from Orin to Thor (≈ 150 ns on both) and holds fixed in **time**, not cycles (190 vs 246 cycles), which resolves the prediction's question toward an interconnect-flight-dominated latency. Only capacity grew. Second, the DRAM shelf (675 / 510 ns) sits an order of magnitude above the 30–40 ns LPDDR device-read floor, confirming the round trip dominates. DRAM random-access latency improved about 25% (675 → 510 ns) while DRAM bandwidth improved about 47% (§A.6); a latency-bound pointer-chasing kernel therefore gains materially less from Thor's LPDDR5X than a bandwidth-bound streaming kernel does (§A.7 "Comparison and discussion").

## So what
Interpretation (mine, from the source): tree traversals, hash lookups and sparse graph kernels — anything serialized on dependent loads — see roughly 1.3× from Thor, while streaming kernels see 1.5× and L2-fitting kernels see up to 14×. The speedup from Thor depends on the access pattern more than on anything in the datasheet.

## Terms introduced
- **dependent load** — a load whose address comes from the previous load, so the two cannot overlap.
- **pointer chase** — a kernel that follows dependent loads around a cycle of pointers; the standard latency probe.
- **Sattolo cycle** — a random permutation that is one full-length cycle; prevents the chase from falling into a short loop.
- **shelf** — the flat latency level a hierarchy level shows across a footprint range.
- **`__ldcg` / `.cg`** — the cache-global load operator; caches only at L2, bypassing L1.
- **LSU** — load/store unit, the SM's memory-instruction pipeline; its depth sets the L1 hit latency.
- **tRCD + tCL** — the DRAM device's row-to-column and column-access delays; the device-read floor of 30–40 ns.
