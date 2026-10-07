# B.7 Aggregate throughput

**Source:** book.pdf §B.7 — `doc-b-proxy-workload/cotenancy-homogeneous.tex`; Table B.7.1 (delivered aggregate throughput by mechanism)  ·  **Status in source:** D (drafted, awaiting review)

## In one sentence
Two same-class tenants sharing the GPU deliver the aggregate throughput of one tenant within about 10% on both boards, whether co-executed by CUDA streams or by MPS — so the co-tenancy penalty measured in §B.6 is per-kernel latency and jitter, not lost throughput — with one exception: Thor's memory-bound RM pair, whose doubled footprint spills the 32 MB L2 and delivers a quarter of the single-tenant rate (257 vs 960 GB/s).

## What it measures
Delivered aggregate throughput T_agg for same-class pairs: the total work of both tenants over the wall-clock window in which they were co-resident. It is well defined here because the two tenants share a class and their work is commensurable; it is not well defined across the mixed classes of §B.6. Reported across three co-execution mechanisms: serial, concurrent streams, and MPS (§B.7 "Objective and metric").

## How
The same four classes as §B.6 (IC, IM, RC, RM), each run as a same-class pair, grid-filling. RM's ≈ 27 MB weight matrix fits Thor's 32 MB L2 alone but not once a co-tenant shares it. Three drives: serial (back-to-back), streams (concurrent CUDA streams), MPS (concurrent via Multi-Process Service). Aggregate throughput uses each tenant's achieved rate over the co-residence span (§B.7 "Experiment setup").

## Predicted
Two saturating tenants split one chip, so T_agg should approach a single tenant's rate, and the mechanism should barely move it. The single-tenant rate is measured directly by running one tenant alone (§B.7 "Prediction model").

## Measured
T_agg = Σ_i w_i / (max_i e_i − min_i s_i), with w_i = r_i · ℓ_i the tenant's work, and s_i, e_i its start and end from on-device timestamps (Eq. B.7.1). A duty check (Σ ℓ_i) / span ≈ N confirms co-residence.

| Pair | Unit | Thor 1× pred. | Thor streams | Thor MPS | Orin 1× pred. | Orin streams | Orin MPS |
|---|---|---|---|---|---|---|---|
| IC (compute) | Top/s | 5.6 | 5.7 | 5.5 | 6.1 | 6.1 | 6.1 |
| RC (compute) | Top/s | 74.4 | 75.3 | 68.3 | 28.5 | 30.6 | 30.8 |
| IM (memory) | GB/s | 255 | 260 | 234 | 163 | 170 | 172 |
| RM (memory) | GB/s | 960 | 257 | 269 | 158 | 172 | 169 |

CPU idle. "1× pred." is the measured single-tenant rate (§B.7 Table B.7.1).

## The gap, and what it means
**Aggregate throughput holds at one tenant's rate.** Concurrent pairs match the single-tenant prediction within about ten percent on both boards, and streams and MPS deliver the same aggregate. The sole deviation is RM on Thor: its doubled footprint spills the 32 MB L2 and reverts to DRAM, so the pair delivers a quarter of the L2-resident single-tenant rate (§B.7 "Comparison and discussion").

**The co-tenancy cost is latency, not throughput.** Same-class co-tenancy costs no aggregate throughput and the concurrency mechanism does not change it. An aggregate-rate accounting shows two co-running same-class models as fully served; the cost surfaces only in the per-kernel latency each one feels.

## So what
Interpretation (mine, from the source): a throughput dashboard will not show the co-tenancy problem. Only per-kernel latency (and its tail) does, which is why §B.8 and the L4 work use p99 latency as the metric for the control loop. The Thor RM case also shows that L2 residency is a shared resource: a model that fits L2 alone may not fit once a sibling arrives.

## Terms introduced
- **aggregate throughput (T_agg)** — total work of co-resident tenants over their co-residence span.
- **co-residence span** — first tenant start to last tenant finish, from on-device timestamps.
- **duty check** — (Σ ℓ_i) / span ≈ N; confirms the tenants genuinely overlapped.
- **serial / streams / MPS (mechanisms)** — the three ways two kernels are driven: back-to-back, concurrent CUDA streams in one context, or concurrent processes under Multi-Process Service.
- **commensurable** — measured in the same unit, so the two tenants' work can be summed.
