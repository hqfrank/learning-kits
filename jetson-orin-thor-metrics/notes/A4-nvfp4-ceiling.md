# A.4 NVFP4 ceiling

**Source:** book.pdf §A.4 — `doc-a-capabilities/nvfp4-ceiling.tex`; tables A.4.1 (parameters), A.4.2 (dense and sparse vs datasheet)  ·  **Status in source:** D (drafted, awaiting review)

## In one sentence
On Thor the tuned dense NVFP4 ceiling is 627.8 TFLOP/s (60.7% of the 1035 datasheet) and the 2:4-sparse ceiling is 878.3 TFLOP/s (42.4% of the 2070 datasheet), so the delivered sparsity multiplier is 1.40× against an advertised 2× — and that multiplier depends on which library runs the kernel, not on the silicon.

## What it measures
The achievable NVFP4 tensor ceiling in two forms — dense and 2:4-structured-sparse — plus the measured sparsity multiplier relating them. NVFP4 is the block-scaled 4-bit floating format (E2M1 with a shared per-block scale) that Thor's fifth-generation tensor cores add; it carries the largest advertised TOPS figure. Orin has no FP4 datapath, so this section is Thor only. Rates are **dense-equivalent** TFLOP/s: they count the full multiply-add work even when half the operands are structurally zero, so a sparse rate is directly comparable to a dense one and to the datasheet (§A.4 "Objective and metric").

## How
Both tiers run on Thor at MAXN with the clock devfreq-verified per run. Dense uses the cuBLASLt block-scaled NVFP4 path (E2M1 operands, FP16 output, 32-bit accumulate, TN layout). Sparse uses the cuSPARSELt 0.9.1.1 2:4 path (native sm_110, autotuned). Each rate is the median of three runs at the shape that maximises it, after a numerical-correctness gate (max relative error 5 × 10⁻⁴ dense, 3.8 × 10⁻³ sparse). The 2:4 multiplier is measured as a **like-kernel** ratio — sparse over dense within one library at a matched shape — so the differing tuning of two libraries does not enter it (§A.4 "Experiment setup", Table A.4.1).

## Predicted
The datasheet quotes 2070 TFLOP/s for 2:4-sparse NVFP4 and, halving for the structural-zero factor, 1035 dense-equivalent. The advertised sparsity multiplier is therefore exactly 2×. The dense measurement is compared against 1035, the sparse against 2070, and the achievable multiplier against 2×. The experiment tests how far below 2× the multiplier falls and whether it depends on the vehicle (§A.4 "Prediction model").

## Measured
Ceilings are maxima of 2N³/t over the shape sweep at the peak shape.

| Quantity | Datasheet | Achieved (Thor) | Fraction |
|---|---|---|---|
| Dense NVFP4 | 1035 (dense-equiv) | 627.8 TFLOP/s @ N = 8192 | 60.7% |
| 2:4-sparse NVFP4 | 2070 | 878.3 TFLOP/s @ N = 16384 | 42.4% |
| 2:4 multiplier (sparse / dense) | 2× (advertised) | 1.40× (delivered, 878.3 / 627.8) | 70% |

The like-kernel multiplier within CUTLASS at a matched shape is m_2:4 = 1.86× (§A.4 Table A.4.2 and "Measurement").

## The gap, and what it means
The advertised number is a best-case datapath quantity, reached at under half its face value by a tuned library.

The sparsity multiplier is vehicle-dependent. Three multipliers separate cleanly: the advertised 2×, the like-kernel 1.86× (already below 2×), and the delivered cross-vehicle 1.40× (cuSPARSELt over cuBLASLt). The like-kernel figure does not transfer across vehicles because the tuned dense library gains far more from tuning than the tuned sparse one. A sparse ceiling projected by multiplying the measured dense rate by 1.86 would predict ≈ 56% of 2070; the achievable is 42.4%. The multiplier is a property of the vehicle, not the silicon — a projected rate is a prior, not a result, and must be labelled with the path it rests on (§A.4 "Comparison and discussion").

## So what
Interpretation (mine, from the source): a deployment plan that multiplies a measured dense rate by 2 (or even 1.86) to estimate a 2:4-sparse model's speed will be wrong by 30–40% on Thor today. Measure the sparse library directly.

## Terms introduced
- **NVFP4** — block-scaled 4-bit floating format: E2M1 element (2 exponent bits, 1 mantissa bit) with a shared per-block scale; Thor only.
- **2:4 structured sparsity** — every group of four weights has at most two non-zeros; the tensor core skips the zeros.
- **dense-equivalent rate** — a sparse rate counted as if the structural zeros were computed, so it compares to a dense rate.
- **sparsity multiplier** — sparse rate over dense rate; advertised 2×, like-kernel 1.86×, delivered 1.40×.
- **vehicle** — the library or kernel path through which a rate is reached (cuBLASLt, cuSPARSELt, CUTLASS); the book's word for it.
- **like-kernel ratio** — a ratio of two kernels within the same library at a matched shape, so library tuning cancels.
