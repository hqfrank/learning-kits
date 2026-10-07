# B.8 Co-tenancy with real-shape proxies (mix ladder)

**Source:** book.pdf §B.8 — `doc-b-proxy-workload/cotenancy-real-shape.tex`; Table B.8.1 (WBC p99 under each single co-tenant); Figure B.8.1 (mix ladder)  ·  **Status in source:** D (drafted, awaiting review)

## In one sentence
A tiny 100 Hz whole-body-control (WBC) policy with a solo p99 of 42 µs (Thor) / 60 µs (Orin) sees its p99 inflated into the millisecond range by an SM-saturating or memory-saturating co-tenant (1.70 ms and 0.64 ms on Thor, CPU idle), a concurrent CPU memory hog multiplies every cell 2–9×, and the worst observed tail — Thor, three tenants plus CPU hog — is 141× solo at 5.9 ms, under the 10 ms deadline but consuming most of it.

## What it measures
The WBC p99 latency slowdown S (co-run p99 over solo p99), with the median carried as a secondary line so the tail-vs-median gap is visible. The tail is the metric because the WBC policy must meet a 100 Hz deadline (10 ms budget). Two views: a mix ladder that adds tenants cumulatively, and a pairwise matrix that isolates which single co-tenant does the damage. All tenants are proxies derived from the deployment's model shapes, not full models (§B.8 "Objective and metric").

## How
Caveat first: a co-execution overlap gate. The overlap fraction o is the share of the WBC's GPU-active time during which a co-tenant is also active, reconstructed from per-trial GPU timestamps. A cell below o = 0.90 is reported as a **lower bound** on sustained co-tenancy, not a ceiling, because a short co-tenant that finishes before the victim only partially co-executes.

**Victim.** The WBC policy: a batch-1 INT8 multilayer perceptron (80 → 512 → 256 → 128 → 23), solo p99 41.6 µs (Thor) / 59.6 µs (Orin). **Aggressors.** VLM-decode (the memory-bound M = 1 Qwen2-VL-2B MLP GEMM) and VLM-prefill (the compute-bound M = 512 GEMM); the synthetic SM-saturating INT8 compute kernel and fp32 memory-bandwidth kernel of §B.6; and a VLA backbone GEMM (Gemma-2B MLP projection, NVFP4, Thor only). Independent CUDA streams; 32 trials per cell; CPU idle and under a CPU memory-bandwidth hog (§B.8 "Experiment setup").

## Predicted
From §B.6 and §B.4: the WBC tail should be poisoned most by aggressors that saturate the SMs (displacing the tiny victim grid) or saturate the memory controller; a co-tenant that draws neither should barely move it. The INT8 compute and fp32 memory kernels are predicted the strong poisoners, and the CPU hog multiplies every cell. The VLA backbone is a tensor-core GEMM on a datapath disjoint from the victim's INT8 CUDA-core path, so a first hypothesis is that it contends less — testable only in a cell where the two genuinely co-execute (§B.8 "Prediction model").

## Measured
S = ℓ_p99,co-run / ℓ_p99,solo over T = 32 trials.

WBC p99 latency (ms) under each single co-tenant, streams. Solo p99 0.042 ms (Thor) / 0.060 ms (Orin); deadline 10 ms. ‡ = below the 0.90 overlap gate, lower bound.

| Single aggressor | Thor CPU idle | Thor CPU hog | Orin CPU idle | Orin CPU hog |
|---|---|---|---|---|
| INT8 compute (SM-saturating) | 1.70 | 3.37 | 1.44 | 2.23 |
| fp32 memory-bandwidth | 0.64 | 4.71 | 0.84 | 1.17 |
| VLM prefill (compute GEMM) | 0.52‡ | 4.52 | 0.51 | 1.29 |
| VLM decode (memory GEMM) | 0.12‡ | 0.74‡ | 0.36‡ | 0.50‡ |
| VLA backbone (NVFP4 tensor) | 0.20‡ | 0.72‡ | N/A (no FP4) | N/A |

(§B.8 Table B.8.1.) Mix-ladder worst cell (Figure B.8.1, prose): Thor three-tenant cell under the CPU hog, 141× solo = 5.9 ms.

## The gap, and what it means
**The strong tail-poisoners are SM-saturating compute and memory-bandwidth contention**, as predicted. Among gated cells, they inflate the WBC p99 into the millisecond range, one to two orders of magnitude over solo. The mechanism is §B.4's: an SM-saturating co-tenant displaces the tiny WBC grid, and controller contention starves it. The effect lives in the tail — the WBC median stays near 1.0–1.4× across almost every cell.

**The CPU hog is the multiplier.** It grows every cell's tail 2–9×. The solo-GPU figure is a floor; the contended tail is the deployment-relevant number.

**The tensor-backbone question is unsettled.** VLA and VLM-decode show the lowest tails, hinting that a tensor co-tenant on a disjoint datapath contends less. But both finish before the WBC and fail the overlap gate (0.53–0.87), so their p99 is a lower bound. Confirming the hypothesis needs a duration-matched re-capture, left open.

**Deadline headroom.** 5.9 ms stays under the 10 ms budget but leaves little margin for the rest of a real pipeline. The gap between this proxy and a full-runtime deployment figure is not closed here (§B.8 "Comparison and discussion"). The L4 note shows that with a real VLA in a shared context the deadline is in fact missed.

## So what
Interpretation (mine, from the source): for a latency-critical control loop, measure p99 under the full co-tenant roster **and** CPU load, not the solo median. The solo number understates the deployed tail by two orders of magnitude.

## Terms introduced
- **WBC** — whole-body-control policy; here a batch-1 INT8 MLP (80 → 512 → 256 → 128 → 23) that must run at 100 Hz.
- **p99** — the 99th-percentile latency; the tail metric used for deadline-bound work.
- **mix ladder** — a sequence of cells that adds co-tenants cumulatively (solo; + VLM-decode; + VLM-decode + VLA).
- **VLM / VLA** — vision-language model / vision-language-action model; here Qwen2-VL-2B and a Gemma-2B backbone, proxied by single GEMMs.
- **prefill / decode** — the compute-bound (many tokens, M = 512) and memory-bound (one token, M = 1) operating modes of a transformer.
- **overlap fraction (o)** — share of the victim's GPU-active time during which some co-tenant is also active; gate at 0.90.
- **lower bound (cell)** — a slowdown from a cell that failed the overlap gate; sustained co-tenancy would be at least this bad.
