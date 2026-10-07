# A.3 Tensor-core ceilings

**Source:** book.pdf §A.3 — `doc-a-capabilities/tensor-ceilings.tex`; tables A.3.1 (parameters), A.3.2 (classic mma vs architectural roof), A.3.3 (tcgen05 vs datasheet)  ·  **Status in source:** D (drafted, awaiting review)

## In one sentence
The portable warp-`mma` path reaches the whitepaper architectural roof within 1–2% on both boards (FP16 42.5 / 64.4 TFLOP/s, INT8 83.4 / 128.8 TOP/s), but the datasheet peaks assume Thor's 5th-generation `tcgen05` datapath, which a tuned library reaches at 55–75% of datasheet (FP16 192.5, INT8 324.5, FP8 345.4) and which sits 2.2–3.0× above what a hand-written kernel gets.

## What it measures
Achievable tensor-core throughput per precision, in two tiers. The **classic** tier is the warp-level `mma` instruction — the portable path a hand-written kernel issues; it is a floor. The **fifth-generation** tier (Thor only) is the `tcgen05` datapath reached through a tuned vendor library at the best problem shape; it is the achievable ceiling. The gap between tiers is the programmability cost: how much silicon a portable kernel leaves unused. Precisions: FP16, TF32, INT8 on both boards; FP8 additionally on Thor (§A.3 "Objective and metric").

## How
The classic tier issues standard warp `mma` instructions (m16n8k16 FP16, m16n8k32 INT8 and FP8, m16n8k8 TF32), sweeps ILP and warp count, and reads the saturated plateau (reached by ILP ≥ 6 and 8 warps per SMSP). The quantity read is φ_sat, saturated FMAs per clock per SM from on-chip `clock64` timestamps. The fifth-generation tier runs cuBLAS / CUTLASS across a sweep of problem shapes and records the wall time of the best shape; the executing kernel was confirmed by profiler name (`nvjet_sm110` / `cutlass3x_sm100`) to be a fifth-generation kernel, not a classic fallback. Both tiers pass a numerical-correctness gate before any rate is recorded (§A.3 "Experiment setup").

## Predicted
Classic tier vs the whitepaper architectural roof: R_arch,p = ω_p × n_TC × f × n_SM, with ω_p the operations per tensor core per clock (FP16 512, TF32 256, INT8 1024) and n_TC = 4 (§A.3 Table A.3.1). This gives FP16 42.6 / 64.5 TFLOP/s, TF32 21.3 / 32.3 TFLOP/s, INT8 85.2 / 129.0 TOP/s (Orin / Thor).

Fifth-generation tier vs the datasheet dense rates. Thor's datasheet publishes 517 dense TFLOP/s for FP8 (INT8 equal) and 1035 for NVFP4 dense-equivalent. FP16 and TF32 dense are not separately published; the book **estimates** them from 517 by halving per doubling of element width: ≈ 258 (FP16) and ≈ 129 (TF32) TFLOP/s. These are estimates, not published lines. No Orin fifth-generation comparison is made (§A.3 "Prediction model").

## Measured
Classic tier: R_classic = φ_sat × 2 × f × n_SM. Fifth-generation tier: R_5g = 2MNK / t for the best shape.

Classic warp-`mma` (§A.3 Table A.3.2):

| Precision | Arch. roof Orin | Arch. roof Thor | Measured Orin | Measured Thor |
|---|---|---|---|---|
| FP16 (TFLOP/s) | 42.6 | 64.5 | 42.5 | 64.4 |
| TF32 (TFLOP/s) | 21.3 | 32.3 | 20.7 | 32.0 |
| INT8 (TOP/s) | 85.2 | 129.0 | 83.4 | 128.8 |
| FP8 (TFLOP/s) | — | — | — | 132.1 |

Fifth-generation `tcgen05`, Thor only (§A.3 Table A.3.3):

| Precision | Datasheet dense | Measured tcgen05 | Fraction |
|---|---|---|---|
| FP16 (TFLOP/s) | ≈ 258 (estimate) | 192.5 | 75% |
| TF32 (TFLOP/s) | ≈ 129 (estimate) | 71.0 | 55% |
| INT8 (TOP/s) | 517 | 324.5 | 63% |
| FP8 (TFLOP/s) | 517 | 345.4 | 67% |

## The gap, and what it means
The classic path reaches the architectural roof for the standard precisions, within 1–2% on both boards. Orin's third-generation cores deliver the full per-precision rate; a portable hand-written kernel is not leaving standard-precision tensor throughput unused on either board. This is the portable floor.

The datasheet peaks assume the fifth-generation datapath, which the classic path cannot reach. Thor's `tcgen05` tier runs 2.2× (TF32) to 3.0× (FP16) above the classic floor. Against the datasheet dense rates the tuned library reaches 55–75% (about two-thirds for FP8 / INT8, the precisions with a published figure). The portable floor sits far lower: classic FP8 at 132.1 is 26% of the 517 datasheet and only 38% of what the tuned library extracts (§A.3 "Comparison and discussion").

## So what
Interpretation (mine, from the source): on Thor, which library runs the GEMM decides the ceiling by a factor of 2–3. A roofline for Thor must carry two tensor roofs per precision, and a kernel budget built from the datasheet TOPS figure overstates even the tuned-library ceiling by 1.3–1.8×.

## Terms introduced
- **classic mma** — the warp-level matrix-multiply-accumulate instruction (`mma.sync`), the portable tensor-core path; the floor tier.
- **φ_sat** — saturated FMAs per clock per SM, read at the plateau of the ILP × warp sweep.
- **architectural roof (R_arch)** — the whitepaper per-tensor-core operations per clock times cores, clock and SM count.
- **datasheet dense rate** — the vendor's published dense throughput per precision, assuming the tcgen05 datapath.
- **programmability cost** — the gap between the tuned-library tier and the portable classic tier.
- **FMA** — fused multiply-add, counted as two operations (a multiply and an add).
