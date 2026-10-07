# C.1 π0.5 solo latency: observation to action

**Source:** book.pdf §C.1 — `doc-c-real-workload/c1-pi05-latency-body.tex` and the Doc C front matter `models.tex`; tables C.0.1–C.0.2 (model shapes, deployed config), C.1.1 (engines), C.1.2 (symbols), C.1.3 (M ladder), C.1.4 (predicted per phase), C.1.5 (all predicted), C.1.6 (measured), C.1.7 (predicted vs measured), C.1.8 (phase attribution)  ·  **Status in source:** data-backed on both sides for Thor; Orin predicted only, not yet measured (status 2026-09-23)

## In one sentence
The π0.5 vision-language-action model runs observation→action in 90.06 ms at 16-bit and 53.03 ms at 8-bit on Thor, a first-principles prediction built from measured per-shape GEMM rates and the DRAM roof is optimistic by a consistent 1.40–1.50×, and the model is a bandwidth problem, not a TOPS problem: the 16→8-bit latency ratio (1.70×) tracks the measured byte ratio (1.68×), not the nominal 2× cut in bytes per parameter.

## What it measures
The solo observation→action latency of π0.5 in milliseconds — the time from a new observation entering the model to a new action chunk leaving it — and its inverse, the re-planning rate in Hz. One inference emits a chunk of H = 10 future timesteps, so the controller can run at H times the re-planning rate; that consumption rate is a deployment parameter outside this section. The section does not report TTFT or tokens-per-second, because a controller consumes action chunks, not tokens. Also measured per engine: DRAM bytes per inference (read/write split), engine size on disk, and fidelity (median cosine similarity of the action chunk against the PyTorch reference over N = 30 input draws) (§C.1 "Objective and metric", "What we measure").

## How
**Model.** π0.5 = a PaliGemma-class VLM backbone (Gemma-2B: d_model 2048, 18 layers, d_mlp 16384, 8 query heads : 1 KV head, d_head 256, 1.98 B transformer + 0.53 B embedding) + a flow-matching action expert (Gemma-300M: d_model 1024, 18 layers, d_mlp 4096, 0.30 B) + a SigLIP-So400m vision encoder (d_model 1152, 27 layers, 16 dense heads, 0.41 B). Deployed config `pi05_libero`: action horizon H = 10, 32 action dimensions, 200 language tokens (padded to 208), 2 camera views, prefix S ≈ 712 tokens, n_steps = 10 denoising iterations (Doc C "Models used in this note", Tables C.0.1–C.0.2).

**Engines.** Four TensorRT engines from one export path (openpi `pytorch_to_onnx.py` → `trtexec`, `--stronglyTyped`) plus a `torch.compile` PyTorch reference. Named W*weights*A*activations*@*base*: `Wbf16Abf16` (whole graph bf16, 6.27 GB), `Wfp8Afp8@fp16.attn16` (fp8 linears, attention matmuls stay fp16, 3.68 GB), `Wfp8Afp8@fp16` (fp8 on attention too, 3.69 GB), `Wnvfp4Afp8@fp16.llm` (NVFP4 LLM weights, fp8 elsewhere, 2.86 GB). Normalisations, softmax and denoising-loop accumulators stay fp32 on every engine. No int8 engine was built on this path (§C.1 Table C.1.1).

All runs on Thor at MAXN, clocks locked. Latency is the upstream deployment script's median model time over 10 inferences after 3 warmups; the whole inference is one enqueue. An independent `trtexec` run agrees within 1.6% at bf16 and 1.1% on quantized engines. DRAM bytes from `ncu` L2↔DRAM sector counters × 32 B.

## Predicted
Latency splits into three strictly ordered phases, each one term:

- **Prefill (backbone)** — compute-limited, FLOPs over a measured per-shape rate, summed over 18 layers (Eq. C.1.1): gate/up, down, QKVO projections and the attention matmuls. Rates measured standalone at the model's own shapes at M = 712: R_gate/up, R_down, R_qkvo ≈ 94 TFLOP/s (Thor) / ≈ 24 (Orin); R_attn 35.2 / 11.9 TFLOP/s [D] (§C.1 Table C.1.2).
- **Vision** and **action** — bandwidth-limited, weight-bytes over B_DRAM = 259 / 177 GB/s (read-only roof, so up to 6% optimistic): t_vision = N_vis · b / B_DRAM; t_action = n_steps · N_ae · b / B_DRAM (Eq. C.1.3). The action expert re-reads all 0.30 B of its weights at each of 10 denoising steps to emit 10 timesteps.

Arithmetic intensity is 2T/b FLOP per byte: prefill 731, vision 512, action 10 at b = 2 — a factor of 70 across one model. The ridge for the rates this workload reaches (52.8–110.1 TFLOP/s against the 197.3 GB/s the model sustains [C]) is 268–558 FLOP/byte: action is 27–56× below it (memory-bound), prefill 1.3–2.7× above it (compute-bound), vision inside the band (carried in bandwidth form pending its own GEMM rates). No KV term: ≈ 13 MB of KV at S ≈ 712 is three orders of magnitude below the weight traffic.

**The delivered prefill rate is a discontinuous function of M.** MLP down-projection, FP16, Thor (§C.1 Table C.1.3): M = 640 → 109.5 TFLOP/s; 704 → 75.1; 708 → 32.4 (falls back to an sm_80 CUTLASS kernel); **712 → 52.8**; 716 → 32.4; 720 → 54.4; 816 → 71.5. M mod 16 = 0 reaches the widest tiles, 8 a narrower one, 4 falls two generations back. The measured shape rates span 52.8–110.1 TFLOP/s, all 1.7–3.6× under Thor's 192.5 TFLOP/s tcgen05 FP16 ceiling (§A.3).

Predicted per phase at S ≈ 712 (§C.1 Table C.1.4), Thor: vision 3.2 / 1.6 / 0.8 ms; backbone 37.7 / 24.2 / 10.0 ms; action 23.2 / 11.6 / 5.8 ms at 16-bit / 8-bit / NVFP4. Orin: vision 4.7 / 2.3; backbone 124.1 / 67.7; action 33.9 / 16.9 at 16-bit / 8-bit.

Predicted totals (§C.1 Table C.1.5):

| Board, precision | Latency (ms) | Re-plan (Hz) | DRAM traffic (GB) | Engine size (GB) |
|---|---|---|---|---|
| Thor 16-bit | 64.1 | 15.6 | 11.14–16.66 | 6.47 |
| Thor 8-bit | 37.4 | 26.7 | 5.57–9.07 | 3.76 |
| Thor NVFP4 | 16.6 | 60.1 | 4.58–7.35 | 2.77 |
| Orin 16-bit | 162.7 | 6.1 | as Thor | as Thor |
| Orin 8-bit | 87.0 | 11.5 | — | as Thor |

The DRAM bracket's lower bound is every weight once plus KV once per denoising step (11.14 GB at 16-bit); the upper bound adds every unfused activation round trip, of which the fp32 attention logits are a fixed 1.49 GB at every rung (Eqs. C.1.4–C.1.5). Fidelity is not predicted.

## Measured
Thor, solo (§C.1 Table C.1.6):

| Engine | Latency (ms) | DRAM (GB) | Size (GB) | Cosine median | σ | min |
|---|---|---|---|---|---|---|
| `Wbf16Abf16.torch` (reference) | 126.14 | — | — | 1.0 | — | — |
| `Wbf16Abf16` | **90.06** | 19.44 | 6.27 | 0.9956 | 0.097 | 0.580 |
| `Wfp8Afp8@fp16.attn16` | 56.13 | 10.24 | 3.68 | **0.9994** | 0.051 | 0.718 |
| `Wfp8Afp8@fp16` | **53.03** | 11.58 | 3.69 | 0.9871 | 0.315 | 0.007 |
| `Wnvfp4Afp8@fp16.llm` | **45.65** | 9.43 | 2.86 | 0.2757 | 0.453 | −0.596 |

Phase attribution by launch count, 16-bit engine (§C.1 Table C.1.8): vision 4.49 ms (4.9%, predicted 5%); prefill 43.80 ms (47.5%, predicted 59%); action 35.48 ms (38.5%, predicted 36%); unclassified 8.42 ms (9.1%, mostly one GEMM launched 71 times). Kernel-trace total 92.18 ms vs 90.06 ms end-to-end (2.4%).

## The gap, and what it means
**The prediction is optimistic by a consistent 1.40–1.50×** (§C.1 Table C.1.7): 64.1 → 90.06 ms (1.40×) at 16-bit; 37.4 → 53.03 ms (1.42×) and 56.13 ms (1.50×) at 8-bit. No NVFP4 comparison, because the prediction assumes whole-model b = 0.5.

**Halving the bytes roughly halves the latency.** The 16→8-bit ratio is 1.70×, tracking the measured byte ratio 1.68× rather than the nominal 2×. Weight compression is not traffic reduction; latency follows traffic. The upper bound of the bracket falls by only 1.84× because the fp32 attention logits do not shrink; the measured 1.68× is below even that, so some precision-invariant traffic is unaccounted for.

**The traffic is weight streaming**, read-dominated at 3.2–4.9 reads per write; KV is 0.68% of it. Three of four engines reach 84–88% of the DRAM roof (taken against the read-only 259 GB/s, so lower bounds; Thor's mixed-direction roof is 241.6–247.2 GB/s [M]). The `.attn16` engine reaches only 74%: it moves 11.6% fewer bytes than its sibling yet takes 5.8% longer, because quantizing the attention matmuls adds 1.34 GB of quantize/dequantize traffic and 214 kernels and is still 3.1 ms faster — the fp8 attention computes faster by more than its extra traffic costs.

**The engine moves more bytes than an unfused implementation would**: 19.44 GB against the 16.66 GB upper bound. A per-kernel audit shows the fused elementwise family moves 3.50 GB against 5.52 GB unfused (fusion worth 2.02 GB), while the GEMM family moves 15.53 GB, 2.38× the weights the engine holds, at a 44.9% L2 hit rate; two kernels launching 180 times (18 layers × 10 steps) carry 4.59 GB between them — the unrolled flow-matching loop streaming the action expert's weights ten times. The 2.78 GB byte residual is about 13 ms at the engine's rate against a 27 ms latency residual, so unaccounted traffic covers more than half the gap; the rest (launch overhead, kernels saturating neither resource) is not resolved.

**Engine size is predicted within 3%** (6.47 / 3.76 / 2.77 vs 6.27 / 3.68 / 2.86 GB), with residual signs the build implies. **The NVFP4 engine's fidelity (0.2757) is too low** for its 45.65 ms to mean much as a deployable number; a build that recovered fidelity would hold more of the graph at higher precision and move more bytes (§C.1 "Discussion").

**Appendix (int8 cells).** The marked int8 predictions take their rate at the nearest aligned M, because at M = 712 the microbenchmark falls back to an sm_80 WMMA kernel on Thor (≈ 154 → 15.5 TOP/s) and a CUDA-core kernel on Orin (≈ 10 vs ≈ 42 TOP/s tensor). Predicting from the fallback rates would give 189 ms on Thor and over 300 ms on Orin, slower than the 16-bit predictions.

## So what
The source's central claim, confirmed and sharpened: this is a bandwidth problem, not a TOPS problem. Interpretation (mine): the practical levers are byte count (precision, fusion) and the GEMM shape the library sees (a prefix 10% shorter would run the down-projection 2.07× faster at the same precision). The datasheet's NVFP4 TOPS never enters; the model sustains ≈ 35 TFLOP/s equivalent against a 192.5 TFLOP/s FP16 ceiling.

## Terms introduced
- **π0.5** — a vision-language-action model: Gemma-2B backbone + Gemma-300M flow-matching action expert + SigLIP-So400m vision encoder.
- **observation→action latency** — time from a new observation entering the model to a new action chunk leaving it; the deployable VLA latency.
- **re-planning rate** — the inverse of observation→action latency, in Hz.
- **action chunk / horizon (H)** — the H = 10 future timesteps one inference emits, executed open-loop until replaced.
- **prefix (S)** — the backbone's input tokens: 256 per camera view × 2 + language + state ≈ 712.
- **denoising steps (n_steps)** — the 10 iterations of the flow-matching action expert, each re-reading its weights.
- **grouped-query attention** — several query heads share one key/value head (8:1 here), shrinking the KV cache.
- **ridge** — the arithmetic intensity at which the compute roof and the bandwidth roof cross; here 268–558 FLOP/byte.
- **engine (TensorRT)** — a compiled, serialized inference graph; named W*A*@*base* by the precisions of its quantized layers and its base.
- **fidelity (cosine)** — median cosine similarity of an engine's action chunk against the PyTorch reference over 30 input draws.
- **M mod 16 effect** — the GEMM library's kernel choice depends on how the row count M divides, so delivered rate is discontinuous in M.
- **phase attribution by launch count** — assigning kernels to vision / prefill / action by how many times they launch per inference (27 / 18 / multiples of 10).
