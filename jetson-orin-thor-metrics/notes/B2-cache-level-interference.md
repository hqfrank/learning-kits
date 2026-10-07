# B.2 Cache-level interference

**Source:** book.pdf §B.2 — `doc-b-proxy-workload/cache-interference.tex`; Table B.2.1 (plateau predictions), Figure B.2.1 (pointer-chase slowdown vs aggressor footprint)  ·  **Status in source:** D (drafted, awaiting review)

## In one sentence
A co-tenant degrades an L2-resident victim before the memory controller saturates, simply by evicting it: the slowdown rises off 1.0 exactly when the aggressor's footprint reaches (L2 capacity − victim footprint), a latency-bound pointer-chase then pays around the L2-to-DRAM latency ratio (predicted 4.6× Orin, 3.3× Thor), while a streaming victim slows only 1.3–1.8× against a 12–15× bandwidth-ratio prediction.

## What it measures
The victim slowdown S as the aggressor's cache footprint is swept. From the curve come the **eviction knee** (the footprint at which S rises off unity) and the **plateau** (the value S climbs to once the victim is fully evicted). The mechanism is upstream of the controller contention of §B.1 (§B.2 "Objective and metric").

## How
Victims, each pinned to a fixed L2 footprint of 2 or 16 MB: a pointer-chase (latency-bound; every load waits on whichever level holds its line) and a streaming reader (throughput-bound). Their slowdowns are read from different quantities, because a heavily evicted chase can take unbounded time: the chase from accesses completed in a fixed cycle budget, the streamer from wall time. Aggressor: one streaming kernel with footprint swept 1–256 MB by powers of two, capped at 25% of warp slots so it evicts the victim from L2 without displacing it by scheduling. A ≥ 90% co-execution overlap gate ensures the two run together. Solo baseline is the minimum over 5 trials (§B.2 "Experiment setup").

## Predicted
Knee-shaped: near unity while the aggressor fits beside the victim in L2, rising once the combined footprint exceeds capacity.

- **Eviction knee** at aggressor footprint = L2 capacity − victim footprint.
- **Plateau.** A latency-bound chase, L2-resident when solo, pays DRAM latency on every dependent load once evicted, so its plateau is the L2-to-DRAM latency ratio from §A.7. A throughput-bound streamer pays the L2-to-DRAM bandwidth ratio from §A.6 — an upper bound its overlapping accesses may not reach.

| Victim (bound) | Board | L2-resident | DRAM-evicted | Predicted plateau |
|---|---|---|---|---|
| pointer-chase (latency) | Orin | 146 ns | 675 ns | 4.6× |
| pointer-chase (latency) | Thor | 156 ns | 510 ns | 3.3× |
| streaming (bandwidth) | Orin | 2200 GB/s | 177 GB/s | 12.4× |
| streaming (bandwidth) | Thor | 3790 GB/s | 259 GB/s | 14.6× |

(§B.2 Table B.2.1.)

## Measured
S = median(t_co) / min₅(t_solo) for the streamer; S = max₅(A_solo) / median(A_co) for the chase, with A the accesses completed in the fixed cycle budget. Both ratios equal their predicted kind: the fully-serialized chase completes accesses at a rate inversely proportional to per-access latency, and the streamer's wall time is inversely proportional to bandwidth.

The measured pointer-chase plateau values appear in Figure B.2.1 only, which was not read (see SOURCES.md). The prose gives these measured facts:

- The knee is at exactly (L2 capacity − victim footprint) on both boards.
- Control: a 16 MB victim already larger than Orin's 4 MB L2 stays flat — nothing left to evict.
- The chase plateau **brackets** its predicted latency ratio: above it on Thor, below it on Orin.
- The streaming victim stays within 1.3–1.8× across the sweep.

(§B.2 "Comparison and discussion"; Figure B.2.1 caption.)

## The gap, and what it means
**The knee is eviction, not co-residence.** The 16 MB control confirms the effect is genuine L2 eviction, not the mere presence of a co-tenant.

**The latency-bound victim is the casualty.** The chase plateau brackets rather than matches the latency ratio, so the realised penalty is set not only by the resident-vs-evicted latency gap but by how completely the live aggressor evicts the victim and by what the contended controller adds — both board-specific. The streamer slows far less than its bandwidth-ratio prediction because its accesses overlap: it stays bandwidth-bound rather than latency-exposed. Eviction punishes the chase, not the stream.

Thor's larger eviction penalty is the cache-level face of the larger controller penalty it shows against copy traffic in §B.1 (§B.2 "Comparison and discussion").

## So what
The source states the consequence: for a robot mix, latency-critical victims are the casualties of cache contention, and the damage arrives at the L2 boundary well before the external controller saturates. Interpretation (mine): the practical knob is footprint budgeting — keep the sum of co-resident footprints under L2 (4 MB on Orin, 32 MB on Thor), or accept that the latency-bound tenant will pay 3–5×.

## Terms introduced
- **eviction knee** — the aggressor footprint at which the victim slowdown departs 1.0; equals L2 capacity − victim footprint.
- **plateau (slowdown)** — the slowdown reached once the victim is fully evicted from L2.
- **latency-bound / throughput-bound** — a kernel whose time is set by serialized access latency / by sustained bandwidth.
- **co-execution overlap gate** — a minimum fraction (here 0.90) of the victim's active time during which the aggressor is also active, required for a cell to count as co-tenancy.
- **warp slots** — the resident-warp capacity of an SM (48 per SM, Table 1); the aggressor here is capped at 25% of them.
