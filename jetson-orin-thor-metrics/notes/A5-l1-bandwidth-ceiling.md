# A.5 L1 bandwidth ceiling

**Source:** book.pdf §A.5 — `doc-a-capabilities/l1-bandwidth.tex`; Table A.5.1 (predicted vs measured)  ·  **Status in source:** D (drafted, awaiting review)

## In one sentence
One SM's L1 delivers a read plateau of 129 GB/s on Orin and 152 GB/s on Thor (78% and 75% of the 128 B/cycle/SM datapath peak), the ratio between boards (1.18×) matches the clock ratio (1.21×), and the plateau rolls off between 128 and 256 KB — so L1 bandwidth is clock-bound on a fixed-width port, not a wider port on Thor.

## What it measures
The per-SM L1 read bandwidth plateau — the rate at which one SM's L1 supplies data to its own resident block — and the working-set size at which that rate rolls off, which brackets the effective L1 capacity. This is the top roof of the memory roofline; the shared L2 and DRAM roofs under it are measured in §A.6 (§A.5 "Objective and metric").

## How
Each SM runs exactly one block reading a private working set, so the measurement is per-SM and not confounded by sibling blocks. The grid is sized to the SM count and co-residency is verified from a per-SM-identifier histogram (16 of 16 SMs on Orin, 20 of 20 on Thor). Blocks are 1024 threads (32 warps, 67% of maximum occupancy) issuing `float4` loads and driving at least 4 GB per SM per point. The working set is swept from 8 KB to 512 KB by doubling, with the L1 carveout at its maximum (164 KiB Orin, 228 KiB Thor). The plateau is the maximum per-SM rate on the small-footprint flat run (§A.5 "Experiment setup").

## Predicted
With the L1 read datapath at w_L1 = 128 B/cycle/SM (Table 1), the per-SM ceiling is w_L1 · f and the aggregate is w_L1 · f · n_SM (Eq. A.5.1): per-SM 166 / 202 GB/s and aggregate 2662 / 4032 GB/s (Orin / Thor). The roll-off is expected at the effective L1 capacity (§A.5 "Prediction model").

## Measured
| Quantity | Predicted (Orin / Thor) | Orin | Thor |
|---|---|---|---|
| Per-SM read plateau (GB/s) | 166 / 202 | 129 (78%) | 152 (75%) |
| Aggregate read (GB/s) | 2662 / 4032 | 2067 | 3038 |
| Roll-off region (KB) | 164 / 228 (carveout) | 128–256 | 128–256 |
| Per-SM copy plateau (GB/s) | — | 41 | 71 |

(§A.5 Table A.5.1.)

## The gap, and what it means
The per-SM plateau is 78% / 75% of the 128-byte-per-cycle peak — the honest achievable roof at 67% occupancy under the one-block-per-SM constraint. The per-SM ratio between boards, 1.18×, matches the clock ratio 1.21×, so L1 read bandwidth is clock-bound on a fixed 128-byte-per-cycle datapath: Thor's advantage is its higher clock, not a wider port. The roll-off brackets the effective L1 capacity (about 192 KB on Orin, 256 KB on Thor), consistent with the L1 cliffs in §A.7 — a cross-check that two probes locate the same boundary.

The aggregate datapath peak (2662 / 4032 GB/s) sits correctly above the L2 roof. The measured per-SM plateau dips below the L2 rate only because one block per SM under-drives the read port, so the roofline carries both the aggregate datapath peak and the achievable per-SM plateau as distinct lines (§A.5 "Comparison and discussion").

## So what
Interpretation (mine, from the source): L1 is the one level where Thor's advantage over Orin is only the clock. A kernel living in L1 gains about 1.2× moving to Thor; a kernel living in L2 or DRAM gains far more (§A.6).

## Terms introduced
- **L1 carveout** — the portion of the per-SM L1/shared-memory array configured as L1 cache; max 164 KiB on Orin, 228 KiB on Thor.
- **plateau** — the flat maximum of a rate over the small-footprint part of a sweep.
- **roll-off** — the footprint at which a plateau begins to fall; brackets a capacity boundary.
- **occupancy** — the fraction of an SM's maximum resident warps that are active; 32 of 48 warps = 67% here.
- **roofline** — a plot of achievable rate against arithmetic intensity, bounded by horizontal compute roofs and sloped memory roofs.
