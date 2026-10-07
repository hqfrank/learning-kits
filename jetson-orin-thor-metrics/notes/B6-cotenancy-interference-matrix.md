# B.6 Co-tenancy interference matrix

**Source:** book.pdf §B.6 — `doc-b-proxy-workload/cotenancy-heterogeneous.tex`; tables B.6.1 (parameters), B.6.2 (predictions by regime), B.6.3 (predicted vs measured cells); Figures B.6.1 (Thor matrix), B.6.2 (RC↔RM asymmetry)  ·  **Status in source:** E (exemplar / reviewed)

## In one sentence
When two GPU kernels of different classes share the SoC, the interference is one-sided: an SM-saturating compute kernel slows a memory-bound victim 2.66× (Orin) and 4.19× (Thor) where the DRAM-share model predicts ≈ 1, while the memory-bound kernel barely touches the compute one (1.01 / 1.12) — the mechanism is SM co-scheduling, not memory, and a concurrent CPU hog raises every cell, more on Thor.

## What it measures
An interference matrix S of slowdown factors: for ordered pair (victim v, aggressor a), S_v|a is v's per-kernel latency with a co-resident over its latency alone. From it: the pair asymmetry ρ_ij = S_i|j / S_j|i, and for kernels at the measurement floor a floor-corrected slowdown Ŝ. Per-kernel latency is the metric because the classes deliver work in incommensurable units (int8 TOP/s beside fp32 GB/s), and latency is what a control loop feels (§B.6 "Objective and metric").

## How
Four classes, each able to be victim or aggressor. **IC**: hand-tiled int8 GEMM, compute-bound. **IM**: fp32 GEMV, memory-bound. **RC** and **RM**: the dominant MLP weight GEMM of Qwen2-VL-2B (N = 8960, K = 1536) at a compute-bound point (M = 512, prefill) and a memory-bound point (M = 1, decode) — one GEMM each, not the whole model. Every class launches grid-filling (SM count × max resident blocks per SM), so a single tenant already fills every SM and the pair must time-multiplex. Latency is per-kernel `cudaEvent` wall time, median over T = 32 trials. Co-execution by independent CUDA streams in one context; `serial` is the control. Two conditions: CPU idle, and under a CPU memory-bandwidth hog (§B.6 "Experiment setup").

Parameters (§B.6 Table B.6.1, Orin / Thor): sustained DRAM bandwidth B_DRAM = 190 / 245 GB/s [M]; L2-resident B_L2 = 2200 / 3790 GB/s [M]; L2 capacity C = 4 / 32 MB; solo DRAM demand β: IC 10 / 10, IM 163 / 255, RC 56 / 145, RM 158 / (L2-resident) GB/s; RM fp16 weight footprint W_RM = 8960 × 1536 × 2 = 27.5 MB; GPU bandwidth retained under heavy CPU hog η_cpu = 0.76–0.81 / 0.45–0.58 [M].

## Predicted
Three mechanisms, each giving a predicted S:

1. **SM fair-share**: two grid-filling tenants time-multiplex equally, S_SM = N = 2. The null model for any SM-saturating pair.
2. **DRAM-controller share**: S_DRAM = max(1, (β_v + β_a) / B_DRAM). A compute aggressor (β ≈ 10 GB/s) adds almost nothing, so S ≈ 1 against it; any measured slowdown against a compute aggressor must come from mechanism 1.
3. **L2 eviction**: a victim L2-resident alone (W_v ≤ C) that spills once a co-tenant shares the cache loses B_L2 and reverts to DRAM: S_L2 = B_L2 / B_DRAM (full-eviction upper bound). Applies only to Thor RM, whose 27.5 MB fits Thor's 32 MB but not Orin's 4 MB.

| Regime | Model | Orin | Thor |
|---|---|---|---|
| Compute ∥ compute (IC∣IC) | SM fair-share | 2.0 | 2.0 |
| Memory ∥ memory (IM∣IM) | DRAM share | 2β_IM / B_DRAM = 1.7 | 2.08 |
| Memory victim, compute aggressor (IM∣IC) | DRAM share | max(1, 0.91) = 1.0 | max(1, 1.08) = 1.08 |
| Thor RM, any L2-sharing co-tenant | L2 eviction | n/a | ≤ 3790 / 245 = 15.5 |

(§B.6 Table B.6.2.)

## Measured
S_v|a = median_t(ℓ_pair) / median_t(ℓ_solo). Only Thor RM (25 µs solo; Orin's RM at 169 µs is above the floor) sits at the measurement floor, so for that victim the floor-corrected Ŝ = S_streams / S_serial re-baselines against its own serial run (Eq. B.6.3).

| Cell S_v|a | Governing model | Orin pred. | Orin meas. | Thor pred. | Thor meas. |
|---|---|---|---|---|---|
| IC∣IC | SM fair-share | 2.0 | 1.99 | 2.0 | 1.97 |
| IM∣IM | DRAM share | 1.7 | 1.92 | 2.08 | 1.96 |
| IC∣IM | DRAM share | 1.0 | 1.01 | 1.0 | 1.12 |
| IM∣IC | DRAM share | 1.0 | **2.66** | 1.08 | **4.19** |
| RC∣RC | SM fair-share | 2.0 | 1.86 | 2.0 | 1.94 |
| RC∣RM | SM fair-share | 2.0 | 1.30 | 2.0 | 1.50 |
| RM∣RC (Ŝ) | SM co-scheduling | 2.0 | **3.6** | 2.0 | 2.3 |
| RM∣RM (Ŝ) | L2 eviction (Thor) | — | 1.84 | ≤ 15.5 | 1.8 |

Streams, CPU idle. Bold = victim slowed well beyond its governing prediction (§B.6 Table B.6.3).

## The gap, and what it means
**The calibration block isolates the mechanism.** The null models hold on the synthetic diagonal — IC at fair-share 2, IM at the DRAM share. The meaningful result is off-diagonal: IC poisons IM far beyond the DRAM-share ≈ 1, while IM barely touches IC. Because IC draws negligible bandwidth, that one-sided poisoning cannot be controller contention — it is SM co-scheduling, the SM-saturating aggressor displacing the victim from the cores.

**CPU load amplifies every cell, more on Thor**, consistent with Thor retaining less GPU bandwidth under CPU load (η_cpu). A quantitative model of the compound effect is deferred.

**Deployment block: a compute-heavy workload starves a memory-bound one.** RC poisons RM substantially more than RM poisons RC. The compute workload is SM-saturating and the memory-bound one has a small compute grid; the co-tenant that fills the SMs starves the smaller kernel, as §B.4 established. Thor RM∣RM at 1.8 is far below the 15.5 full-eviction bound — the source does not explain the gap beyond labelling the bound an upper bound (§B.6 "Comparison and discussion").

## So what
The source says it: when two models share the SoC, one compute-bound and one memory-bound, the memory-bound workload pays, and on a latency-critical path that is the cost that matters. Interpretation (mine): the asymmetry is the reason a small control-policy network (memory-bound, tiny grid) cannot safely share an unmanaged context with a large compute-bound model — the theme §B.8, §C.2 and the L4 ladder pick up.

## Terms introduced
- **interference matrix** — the table of slowdowns S_v|a over all ordered (victim, aggressor) pairs.
- **asymmetry (ρ_ij)** — S_i|j / S_j|i; how one-sided the interference is.
- **IC / IM / RC / RM** — the four kernel classes: synthetic compute (int8 GEMM), synthetic memory (fp32 GEMV), real compute (Qwen2-VL-2B MLP GEMM at M = 512), real memory (same GEMM at M = 1).
- **grid-filling** — a launch sized to SM count × max blocks per SM, so one tenant occupies every SM alone.
- **floor-corrected slowdown (Ŝ)** — S_streams / S_serial, isolating concurrent execution from the fixed cost of being in a two-kernel run; used when the solo latency is at the measurement floor.
- **SM fair-share** — the null model in which N grid-filling tenants each get 1/N of the SMs, S = N.
- **β_k** — solo DRAM bandwidth demand of class k, in GB/s.
- **GEMV** — general matrix-vector multiply; the M = 1 case of a GEMM, memory-bound.
