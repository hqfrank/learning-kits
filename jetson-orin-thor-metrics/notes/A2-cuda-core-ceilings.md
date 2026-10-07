# A.2 CUDA-core ceilings

**Source:** book.pdf §A.2 — `doc-a-capabilities/cuda-core-ceilings.tex`; tables A.2.1 (parameters), A.2.2 (predicted vs measured)  ·  **Status in source:** D (drafted, awaiting review)

## In one sentence
The CUDA-core FP32 roof is 5.15 TFLOP/s on Orin and 7.82 TFLOP/s on Thor (both 3% under the issue-rate prediction), INT8 dp4a is 10.63 / 16.10 TOP/s, and packed FP16 runs at 1.87× FP32 on Orin but only 1.01× FP32 on Thor — Thor's CUDA cores have no double-rate FP16 unit.

## What it measures
The achievable CUDA-core compute ceilings: FP32 in GFLOP/s, packed FP16 (`half2`) in GFLOP/s, INT8 (`dp4a`) in TOP/s. These are the horizontal compute roofs of the roofline for the non-tensor datapaths. The section also closes a trust loop: the FP32 ceiling measured by an independent tool (ERT) is compared against the value predicted from θ_FFMA of §A.1. If the two agree, both instruments are trustworthy (§A.2 "Objective and metric").

## How
FP32 and FP16 use the Empirical Roofline Toolkit (ERT), which times a fused multiply-add microkernel (A[i] = A[i]·c + d, two FLOP per element) while sweeping arithmetic intensity from 1 to 1024 FLOPs per element and the working-set size. The ceiling is the maximum rate where the kernel is compute-bound. ERT has no integer path, so INT8 uses a separate `dp4a` microprobe: each thread issues 1.28 × 10⁶ `__dp4a` instructions (four INT8 multiply-adds accumulated into INT32, i.e. eight integer operations each) along 8 independent dependency chains. Both report the minimum wall time over 5 trials (§A.2 Table A.2.1).

Both kernels passed a SASS gate. The dp4a probe compiles to hardware `IDP.4A`, not an IMAD emulation. The FP16 kernel issues packed `HFMA2` on both boards, with no scalar HFMA or FP32-promoted FFMA — so the Thor FP16 result below is not a compilation artifact (§A.2 "Measurement").

## Predicted
Every CUDA-core ceiling has one shape: R_c = θ_c × 32 lanes × w_c ops × 4 SMSP × f × n_SM, where w_c is the ops each lane retires per instruction (FP32: 2, FP16: 4, INT8: 8) and the other factors are Table 1 constants.

- FP32: θ_FFMA = 1, w = 2 → 5.32 TFLOP/s (Orin) / 8.06 TFLOP/s (Thor).
- FP16 (`half2`): θ = 1, w = 4 → predicted at 2× FP32 **if** the half-precision path runs at full packed rate. The 2× is a lane-width factor, not a θ change; whether it holds is what the measurement tests.
- INT8 (`dp4a`): soft-anchored at θ_IMAD = 0.5, w = 8 → ≈ 10.65 (Orin) / 16.13 (Thor) TOP/s.

(§A.2 "Prediction model", Eq. A.2.1.)

## Measured
| Ceiling | Predicted (Orin / Thor) | Orin | Thor |
|---|---|---|---|
| FP32 | 5.32 / 8.06 TFLOP/s | 5.15 TFLOP/s | 7.82 TFLOP/s |
| FP16 (`half2`) | ≈ 2× FP32 if full-rate | 9.64 TFLOP/s (1.87× FP32) | 7.86 TFLOP/s (1.01× FP32) |
| INT8 (`dp4a`) | 10.65 / 16.13 TOP/s | 10.63 TOP/s (θ = 0.499) | 16.10 TOP/s (θ = 0.499) |

(§A.2 Table A.2.2.)

## The gap, and what it means
FP32 lands −3.2% (Orin) and −3.0% (Thor) under the θ_FFMA prediction. Both boards miss by the same small margin in the same direction, so the independent throughput tool and the issue-rate model agree: the FP32 roof is trustworthy. INT8 matches the θ_IMAD anchor within 0.2% (θ_dp4a = 0.499 on both), so the dp4a datapath runs at the full integer issue rate.

FP16 is the informative divergence. On Orin packed `half2` runs at 1.87× FP32, the full packed rate. On Thor it runs at 1.01× FP32 — the same rate as FP32. The SASS gate rules out codegen: Thor executes packed HFMA2, so the packed instruction is present and simply issues at the FP32-lane rate. The 2×-wide packed FP16 unit that Orin (Ampere) carries is absent from Thor's (Blackwell) CUDA cores. Thor's CUDA-core FP16 roof is therefore its FP32 roof, 7.86 TFLOP/s. This is a property of the CUDA-core path only; Thor's high FP16 throughput lives on the tensor cores (§A.3). A roofline for Thor must draw the CUDA-core FP16 roof at the FP32 line (§A.2 "Comparison and discussion").

## So what
Interpretation (mine, from the source): hand-written FP16 CUDA kernels tuned on Orin for the packed-half speedup lose that speedup on Thor. On Thor, FP16 pays off only if the work reaches the tensor cores.

## Terms introduced
- **ERT** — Empirical Roofline Toolkit, an independent throughput probe that sweeps arithmetic intensity and working-set size to find compute and memory ceilings.
- **dp4a** — the 4-way INT8 dot-product instruction (`__dp4a`, SASS `IDP.4A`); four multiply-adds into INT32, counted as eight operations.
- **half2 / HFMA2** — packed FP16: two FP16 values per 32-bit lane, one fused multiply-add instruction per pair.
- **arithmetic intensity** — operations per byte moved (here, FLOPs per element in the ERT sweep); the x-axis of a roofline.
- **TFLOP/s, TOP/s** — 10¹² floating-point operations per second; 10¹² integer operations per second.
