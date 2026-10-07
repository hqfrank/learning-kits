# A.1 FP/INT pipe interleaving

**Source:** book.pdf §A.1 — `doc-a-capabilities/fp-int-mix.tex`; tables A.1.1 (parameters), A.1.2 (predicted mix outcomes), A.1.3 (predicted vs measured)  ·  **Status in source:** E (exemplar / reviewed)

## In one sentence
On both boards a single SMSP issues one warp instruction per cycle (D = 1), FFMA issues at 1.0 per cycle and IMAD and ALU at 0.5 each, so two instruction classes overlap only when they use different pipes **and** their combined issue demand fits in that one slot — which means the Volta-era FP/INT overlap does not exist on Orin or Thor.

## What it measures
The metric is the pair (θ, D). θ_c is the sustained per-pipe issue rate of instruction class c, in warp instructions per cycle per SMSP. D is the dispatch bound, the number of instructions the one warp scheduler of an SMSP can issue per cycle. Together they decide whether a mixed instruction stream is limited by pipe capacity or by the shared issue slot. Peak arithmetic rate cannot express this, because it counts pipe throughput and not issue slots. (Source: §A.1 "Objective and metric".)

## How
Each thread performs a fixed count of one instruction class and the elapsed time gives the rate. Three classes are probed: FFMA (float fused multiply-add, 1 SASS instruction), IMAD (integer multiply-add, 1 SASS instruction) and ALU (logic-and-add, 2 SASS instructions: LOP3 then IADD3). Each thread runs four independent dependency chains (ILP = 4), unrolled 16 times, over 20,000 outer iterations, so S = 1.28 × 10⁶ operations per thread (§A.1 Table A.1.1). Warps are pinned either within one SMSP (the pipe-sharing test) or across SMSPs (the control). A 512-thread block gives 4 warps per SMSP for the issue-rate runs; a 256-thread block gives 2 warps per SMSP for the mix baselines. Latency is the minimum over 5 trials.

The SMSP has three execution paths of which only two are independent: FFMA and IMAD both use the FP32 datapath; a separate 16-lane ALU pipe handles logic/add. One warp scheduler with one dispatch port feeds all of them (§A.1 "Experiment setup").

## Predicted
From the datapath inventory: θ_FFMA = 1.0 (two FP32 datapath halves), θ_IMAD = θ_ALU = 0.5 (one pipe each). A class issued at θ_c has solo runtime T_solo = n · I_c · S / (θ_c · f). For two co-issued classes A and B, the victim's runtime is T_B_solo if the pipes are disjoint and θ_A + θ_B ≤ D (overlap), and T_A_solo + T_B_solo otherwise (serialize). Speedup over serialized execution is (T_A_solo + T_B_solo) / T_mix.

Predicted mix outcomes (§A.1 Table A.1.2):

| Mix | Pipes | θ_A + θ_B vs D = 1 | Predicted |
|---|---|---|---|
| FFMA + IMAD | same (FP32 datapath) | — | serialize, speedup 1.0 |
| FFMA + ALU | disjoint | 1.0 + 0.5 > 1 | serialize (dispatch-bound), speedup 1.0 |
| ALU + IMAD | disjoint | 0.5 + 0.5 = 1 | overlap, speedup ≈ 1.5 |

The FFMA + ALU case is the discriminator: disjoint pipes that still serialize because the issue demand exceeds the one slot.

## Measured
Caveat first: on Orin at MAXN the 256-thread FP32 probe under-saturates to θ_FFMA = 0.79 (mechanism unresolved, accepted as-is). This inflates Orin's FFMA-mix serial baselines, so Thor's 1.01 / 1.00 are the clean confirmations of the additive verdict (§A.1 "Comparison and discussion").

| Quantity | Predicted | Orin | Thor |
|---|---|---|---|
| θ_FFMA | 1.0 | 0.98 | 0.98 |
| θ_IMAD | 0.5 | 0.50 | 0.50 |
| θ_ALU | 0.5 | 0.49 | 0.50 |
| D | 1 | 1 | 1 |
| FFMA + IMAD speedup | 1.0 | 1.09* | 1.01 |
| FFMA + ALU speedup | 1.0 | 1.05* | 1.00 |
| ALU + IMAD speedup | ≈ 1.5 | 1.48 | 1.49 |

\* contaminated by the Orin under-saturation above. Model fit median |error| 1.9% (Orin) / 0.2% (Thor). (§A.1 Table A.1.3.)

## The gap, and what it means
Prediction and measurement agree on both boards. The issue rates (1, 0.5, 0.5) and D = 1 are confirmed. FFMA + IMAD and FFMA + ALU serialize; ALU + IMAD overlaps at about 1.5×. Olmedo et al. observed on Volta that FP and INT operations overlap fully, because Volta gave the integer pipe its own dispatch. Neither Ampere nor Blackwell restores a separately-dispatched integer path, so no Volta-style FP/INT overlap occurs for any FFMA-involving mix. The verdict is stable across the two generations (§A.1 "Comparison and discussion").

## So what
Interpretation (mine, from the source's verdict): a kernel that mixes FP32 math with integer address arithmetic pays for both in issue slots on these boards. Address arithmetic is not free, and a peak-FLOP figure overstates what a mixed kernel can issue. The measured θ_FFMA = 1 also feeds §A.2, where it predicts the FP32 ceiling within 3%.

## Terms introduced
- **issue rate (θ)** — sustained warp instructions issued per cycle per SMSP for one instruction class.
- **FFMA / IMAD / ALU** — the three CUDA-core instruction classes probed: float fused multiply-add, integer multiply-add, and logic/shift (LOP3 + IADD3).
- **SASS** — NVIDIA's native GPU assembly, the instructions the hardware issues; below the PTX intermediate.
- **ILP** — instruction-level parallelism; the number of independent dependency chains a thread advances at once.
- **pipe** — an execution datapath inside an SMSP; FFMA and IMAD share the FP32 datapath, ALU has its own.
- **serialize / overlap** — two co-issued classes serialize when the mixed runtime equals the sum of solo runtimes (speedup 1), and overlap when it is less (speedup up to 2).
