# B4 — Compute-bound on one board, near the ridge on another

**Source:** roofline, ridge and the board ceilings from the sibling kit [`../../jetson-orin-thor-metrics/`](../../jetson-orin-thor-metrics/README.md) (keys `tensor_fp16_orin`, `dram_read_orin`, `tensor_fp16_thor`, `pi05_sustained_bandwidth_thor` in [`../constants.json`](../constants.json)); a VLA's per-phase latency in [`../../jetson-orin-thor-metrics/notes/C1-pi05-solo-latency.md`](../../jetson-orin-thor-metrics/notes/C1-pi05-solo-latency.md); predict-then-measure from [`../../robot-workload-benchmarking/notes/C1-predict-then-measure.md`](../../robot-workload-benchmarking/notes/C1-predict-then-measure.md) · **Status:** method note. **The vision encoder and its forms are illustrative** (class `illustrative`); the board ceilings are class `sibling`. The ridges are my arithmetic.

## In one sentence
The same vision encoder sits well above the Orin's ridge, so it is compute-bound there and the compute form of the prediction is the right one, but it sits near Thor's effective ridge, so on Thor neither form alone is safe; a large "miss" of the bandwidth form on the Orin is the wrong form of the prediction, not a slow encoder.

## What it measures
The **ridge** is the arithmetic intensity at which the compute roof and the bandwidth roof of a roofline cross: compute rate ÷ bandwidth, in FLOP per byte. A stage with an intensity above the ridge is compute-bound. A stage below it is bandwidth-bound. The sibling kit teaches the roofline and the ridge ([`../../jetson-orin-thor-metrics/glossary.md`](../../jetson-orin-thor-metrics/glossary.md)); this note only uses them.

A prediction can take two forms:

- **compute form** — time = FLOP ÷ compute rate;
- **bandwidth form** — time = bytes ÷ bandwidth.

Only the form for the roof that actually binds predicts the time.

## How
A per-phase model of a VLA (vision-language-action model) predicts each phase on each board. For the Orin vision term, the first prediction used the bandwidth form (weights ÷ DRAM read bandwidth), because the encoder's matrix-multiply (GEMM) rates at its own shapes were not yet measured. The Orin run then measured each phase from a kernel trace, at batch 1 (see [[C1-deployment-fidelity-and-batch-1-latency]]).

**The ridge per board** (my estimate from the sibling keys):

| Board | Tensor FP16 roof | DRAM bandwidth | Ridge at the roof | Ridge at the model's shapes |
|---|---|---|---|---|
| Orin (Jetson AGX Orin) | 42.5 TFLOP/s (`tensor_fp16_orin`) | 177 GB/s read (`dram_read_orin`) | about 240 FLOP/B | about 96–144 FLOP/B |
| Thor | 192.5 TFLOP/s (`tensor_fp16_thor`) | 197.3 GB/s sustained by a pi0.5-class VLA (`pi05_sustained_bandwidth_thor`) | about 976 FLOP/B | about 390–585 FLOP/B |

The ridge at the roof is my estimate from the tensor key ÷ the bandwidth key. The ridge at the model's shapes is my estimate from the same keys × `shape_rate_fraction` (illustrative: GEMMs at a model's own shapes reach 0.4–0.6 of the ceiling). **Caveat:** applying that fraction to Thor is my assumption, not a Thor measurement. Thor's bandwidth key is the bandwidth that a VLA sustained, not a read peak. With Thor's read peak (`dram_read_thor`, 259 GB/s) the ridge is about 743 FLOP/B, and the ratio to the Orin is about 3, not 4; the encoder stays near the ridge.

Thor's compute roof is about 4.5 times the Orin's, its bandwidth only about 1.1 times, so its ridge is about 4 times higher (my estimate from the four sibling keys).

Analogy: the same lorry is limited by its engine on a flat road and by the road on a steep hill; which limit applies depends on the road, not the lorry.

## Predicted
**The vision encoder** (illustrative, `vision_encoder`): 0.5 TFLOP of work at a weight-side intensity of 500 FLOP/B. Its weights are therefore about 1 GB (my estimate from `vision_encoder`: 0.5 TFLOP ÷ 500 FLOP/B).

| Form, board | Predicted time | Key |
|---|---|---|
| Bandwidth form, Orin | about 6 ms (illustrative) | `vision_pred_bandwidth_form_ms` |
| Compute form, Orin (0.5 TFLOP ÷ the shape rate) | 20–30 ms (illustrative) | `vision_compute_form_ms` |
| Bandwidth form, Thor (1 GB ÷ 197.3 GB/s) | about 5 ms | my estimate from `vision_encoder` and `pi05_sustained_bandwidth_thor` |
| Compute form, Thor, at the roof | about 2.6 ms | my estimate from `vision_encoder` and `tensor_fp16_thor` |
| Compute form, Thor, at the model's shapes | about 4.3–6.5 ms | my estimate from `vision_encoder`, `tensor_fp16_thor` and `shape_rate_fraction` |

The first prediction on the Orin was the bandwidth form.

## Measured
In an illustrative measurement, the Orin vision phase takes about 25 ms (illustrative, `vision_measured_ms_orin`). That is inside the compute-form bracket (`vision_compute_form_ms`), not near the bandwidth form. The bandwidth form therefore misses by about 4 times (my estimate from `vision_measured_ms_orin` and `vision_pred_bandwidth_form_ms`). No Thor vision time is given here; see [`../../jetson-orin-thor-metrics/notes/C1-pi05-solo-latency.md`](../../jetson-orin-thor-metrics/notes/C1-pi05-solo-latency.md) for the sibling kit's per-phase numbers.

| Quantity | Value | Source |
|---|---|---|
| Encoder intensity ÷ Orin ridge, at the roof / at the shapes | about 2.1 / about 3.5–5.2 | my estimate from `vision_encoder`, `tensor_fp16_orin`, `dram_read_orin`, `shape_rate_fraction` |
| Encoder intensity ÷ Thor ridge, at the roof / at the shapes | about 0.5 / about 0.85–1.3 | my estimate from `vision_encoder`, `tensor_fp16_thor`, `pi05_sustained_bandwidth_thor`, `shape_rate_fraction` |

## The gap, and what it means
**On the Orin, the form was what mattered.** The encoder lies above the Orin's ridge, by any of the ridge estimates above. So it is compute-bound, and the compute form (illustrative, `vision_compute_form_ms`) brackets the illustrative measurement. The large miss of the bandwidth form is the wrong form, not a slow encoder.

**On Thor, the data do not decide.** At Thor's roof the encoder lies below the ridge, so on paper it is bandwidth-bound. At the model's own GEMM rates the effective ridge drops to about the encoder's intensity (my estimate above). The two forms then give about the same time, about 4 to 6.5 ms (my estimates above), so either roof could bind. A bandwidth form chosen for Thor is a modelling choice, not a measured bound. Thor's own GEMM rates at these shapes, or per-kernel SM versus DRAM throughput on Thor, would decide.

**Caveats.**

- The weight-side intensity is an upper bound for one pass. A measured intensity that counts all DRAM traffic is lower, which moves the encoder toward the ridge on both boards.
- The shape-rate fraction is illustrative and is applied to Thor by assumption.
- Thor's bandwidth key is a sustained value from a VLA, not a read peak.

## So what
Choose the form of each prediction per board from the ridge, not per model (interpretation). A model that moves to a board with a higher ridge can change from compute-bound to near the ridge. Then neither form alone is safe, and the prediction should carry both.

## Terms introduced
- **ridge** — the arithmetic intensity at which the compute roof and the bandwidth roof cross. Reused from `../jetson-orin-thor-metrics/glossary.md`.
- **roofline** — a plot of achievable rate against arithmetic intensity, bounded by compute roofs and memory roofs. Reused from `../jetson-orin-thor-metrics/glossary.md`.
- **arithmetic intensity** — operations per byte moved. Reused from `../jetson-orin-thor-metrics/glossary.md`.
- **compute form / bandwidth form** — a predicted time as FLOP ÷ compute rate, or as bytes ÷ bandwidth.
- **weight-side intensity** — FLOP divided by the bytes of the weights only; an upper intensity for one pass.
- **shape rate** — the GEMM rate a model reaches at its own matrix shapes, below the board's ceiling.
- **phase split** — the attribution of an inference's kernel time to its vision, prefill and action phases, from a trace.
