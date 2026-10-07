# 06 — Caches and working sets

**Sources:** CUDA Programming Guide §1.2.3.3.1 (A-PM); metrics-kit `A6`, `A7`, `B2`, Table 1 (C-PLAT) and `constants.json`. See [[../SOURCES]]. Builds on [[05-memory-hierarchy]].

## In one sentence
A cache serves data in fixed-size lines and keeps only what fits, so a kernel whose working set fits L2 runs at the L2 bandwidth and one that spills runs at the DRAM bandwidth — and because the cliff between them is sharp and the gap is 12–15×, cache **capacity** often decides performance more than DRAM bandwidth does.

## What it is
A **cache** holds recently used data so later accesses are fast. Data moves in **cache lines** (a fixed block of bytes, typically 128 B on these GPUs — the kit aligns its probes to 64–128 B, C-KIT-NOTES A7). A requested line present in the cache is a **hit**; absent is a **miss**, served from the next level down. When the cache is full, a new line **evicts** an old one. The **working set** (or footprint) is the set of bytes a kernel touches in a pass (C-KIT-NOTES A6). If the working set fits a cache level, most accesses hit there; if it exceeds the level's capacity, accesses miss and fall to the slower level.

## How it works
Because L2 is a fixed size shared by all SMs ([[05-memory-hierarchy]]), there is a **capacity cliff**: as a streaming kernel's footprint grows past L2 capacity, its bandwidth collapses from the L2-resident plateau to the DRAM plateau. The metrics kit measured the cliff landing **exactly at each board's L2 capacity** — 4 MB on Orin, 32 MB on Thor (C-KIT-NOTES A6, Table A.6.2). This is "the L2 cliff."

The gap across the cliff is the **L2:DRAM ratio**: 12.4× on Orin, 14.6× on Thor (`l2_dram_bandwidth_ratio`, C-KIT-NOTES A6). So a working set of a few to a few tens of megabytes runs an order of magnitude faster on the board whose L2 holds it, at identical advertised TOPS (C-KIT-NOTES A6, "In one sentence"). The kit's load-bearing conclusion: these two roofs and the ratio are the memory ceilings a roofline is built on, and capacity can matter more than a bandwidth figure ([[08-measuring-a-gpu]]).

Caches also interact under sharing. A co-tenant that streams a large buffer **evicts** a victim's lines from L2 before the memory controller even saturates; the victim's slowdown rises off 1.0 exactly when the aggressor's footprint reaches (L2 capacity − victim footprint) — the "eviction knee" (C-KIT-NOTES B2). A latency-bound victim then pays about the L2:DRAM *latency* ratio: predicted 4.6× on Orin, 3.3× on Thor (`l2_eviction_plateau_pointerchase_predicted`, C-KIT-NOTES B2).

## On Orin and Thor (numbers from constants.json)
From `constants.json`:

| Quantity | Orin | Thor | key |
|---|---|---|---|
| L2 capacity (the cliff) | 4 MB | 32 MB | `l2_size` (C-PLAT) |
| L2-resident read BW | 2200 GB/s | 3790 GB/s | `l2_resident_read_bandwidth` (C-KIT-NOTES A6) |
| DRAM read BW | 177 GB/s | 259 GB/s | `dram_bandwidth_read_measured` (C-KIT-NOTES A6) |
| L2:DRAM bandwidth ratio | 12.4× | 14.6× | `l2_dram_bandwidth_ratio` (C-KIT-NOTES A6) |
| Eviction penalty, latency-bound (predicted) | 4.6× | 3.3× | `l2_eviction_plateau_pointerchase_predicted` (C-KIT-NOTES B2) |

Capacity is the big Orin→Thor change: 8× more L2 (`l2_dram_capacity_ratio`), while L2 *latency* barely moved ([[05-memory-hierarchy]], C-KIT-NOTES A7).

## Two access patterns: streaming and the dependent pointer chase
The kit measures every memory level two ways, because a kernel's speed depends not only on *where* its data sits but on *how* it asks for it (C-KIT-NOTES A6, A7).

**Streaming** reads consecutive addresses: `a[0], a[1], a[2], …` (the STREAM pattern, A6). Every address is known in advance, so the hardware issues many loads at once and overlaps them. The quantity you measure is **bandwidth**: bytes per second once the pipe is full. Latency hardly matters because dozens of loads are in flight.

**Dependent pointer chase** reads an address that the previous load returned: `p = buf[p]; p = buf[p]; …` (A7, B2). Load N+1 cannot start until load N comes back, so exactly one load is in flight and nothing overlaps. The quantity you measure is **latency**: one round trip to whichever level holds the line. The kit walks a Sattolo permutation — one random cycle through the whole buffer — so the chase cannot fall into a short loop and the hardware cannot predict the next address (C-KIT-NOTES A7).

The same hardware answers the two questions very differently. From `constants.json`, Thor streams at 3790 GB/s from L2 and 259 GB/s from DRAM (14.6×, `l2_dram_bandwidth_ratio`), but a chase pays ~156 ns per load from L2 and ~510 ns from DRAM (3.3×, `latency_l2`, `latency_dram`). That is why eviction hurts the two patterns so unequally (next section): the streamer's many in-flight loads absorb the extra latency, the chaser's single in-flight load cannot.

Robot-side examples (**my explanation**): streaming is reading a weight matrix during a GEMM, copying a camera frame, the fp16 perception layers of the L4 roster — bandwidth-bound, fixed by moving fewer bytes or having more bandwidth. Chasing is walking a KD-tree for nearest neighbours, an octree collision query, a planner's graph traversal, a hash-table or sparse-index lookup — latency-bound, fixed by keeping the structure L2-resident or by running several independent chases at once so their round trips overlap. One sentence: streaming asks how wide the pipe is; chasing asks how long the round trip is.

## Common confusions
- **Bandwidth is not the whole story.** Two boards can quote the same TOPS and differ ~10× in delivered bandwidth for the same workload, purely because one's L2 holds the working set and the other's does not (C-KIT-NOTES A6).
- **The cliff is sharp, not gradual.** Bandwidth is flat below L2 capacity, then drops; a kernel just over the capacity pays the full DRAM penalty (C-KIT-NOTES A6).
- **Eviction hurts latency-bound kernels most.** A streaming victim stays near its bandwidth bound (1.3–1.8× slowdown), but a pointer-chasing victim pays 3–5× once evicted (C-KIT-NOTES B2).
- **Capacity is shared.** A model that fits Thor's 32 MB L2 alone may not fit once a sibling kernel shares it, reverting to DRAM — the kit saw a 4× loss from exactly this (C-KIT-NOTES B7).

## Why it matters for robotics workloads
The practical knob is footprint budgeting. The kit's advice: keep the sum of co-resident working sets under L2 (4 MB Orin, 32 MB Thor), or accept that a latency-critical tenant pays 3–5× and a streaming tenant drops to the DRAM roof (C-KIT-NOTES B2, A6). For a robot, this means a control loop and a perception net whose combined footprint spills L2 will contend even if neither saturates the controller alone. Choosing a board, or a model size, is partly choosing whether the hot working set stays L2-resident ([[05-memory-hierarchy]], [[08-measuring-a-gpu]]).

## Common confusions resolved into one rule
Ask of each kernel: does its working set fit L2? If yes on this board and no on that board, expect ~12–15× (C-KIT-NOTES A6). That single question beats comparing datasheet TOPS.

## Terms introduced
- **cache line** — the fixed-size block (≈128 B here) a cache fetches and evicts as a unit (A-PM §1.2.3.3.1; C-KIT-NOTES A7).
- **hit / miss** — a requested line present in / absent from a cache level (A-PM §1.2.3.3.1). **(my explanation, standard cache terms applied to the GPU levels)**
- **eviction** — replacing a cached line to make room; a co-tenant can force it (C-KIT-NOTES B2).
- **working set / footprint** — the bytes a kernel touches per pass. Reused from `../jetson-orin-thor-metrics/glossary.md` (C-KIT-NOTES A6).
- **capacity cliff** — the footprint at which bandwidth falls from one plateau to the next; at L2 capacity for reads. Reused from the metrics-kit glossary (C-KIT-NOTES A6).
- **eviction knee** — the aggressor footprint at which a victim's slowdown departs 1.0; = L2 capacity − victim footprint. Reused from the metrics-kit glossary (C-KIT-NOTES B2).
- **L2 cliff** — the common name for the capacity cliff at L2 (C-KIT-NOTES A6). **(my label for the same phenomenon)**
- **streaming access** — consecutive addresses, many loads in flight; bandwidth-bound (C-KIT-NOTES A6).
- **dependent pointer chase** — each load returns the next address, one load in flight; latency-bound (C-KIT-NOTES A7, B2).
- **Sattolo permutation** — a random single-cycle permutation used to build a chase that visits every line once and cannot be predicted (C-KIT-NOTES A7).
