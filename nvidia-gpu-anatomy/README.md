# Anatomy of an NVIDIA GPU — the CUDA execution model and memory hierarchy

A concept primer for an engineer reading `../jetson-orin-thor-metrics/notes/00-platforms.md`
who meets terms like SM, SMSP, warp, L2, tcgen05 and MPS for the first time. It explains the
mechanisms behind Table 1 of the metrics kit, anchors every number to that kit's measured data,
and points back to the kit note that measured each one.

**One paragraph:** A GPU is many **streaming multiprocessors (SMs)** sitting behind one shared
**L2 cache** and one **memory controller**. You program it through a software ladder — **thread
→ warp → block → grid → kernel** — that the hardware maps onto a physical ladder — **lane →
sub-partition → SM → GPU**. Each SM is four **sub-partitions**, each issuing one warp
instruction per cycle into its **CUDA cores** (scalar FP32/INT lanes) and its **tensor core**
(a matrix unit). Performance is governed less by the advertised TOPS than by where a kernel's
**working set** sits in the memory hierarchy (registers → L1/shared → L2 → DRAM) and by how the
GPU is **shared** among co-tenants — because on Orin and Thor the CPU and GPU share one physical
memory, and the hardware block scheduler locks a victim out rather than sharing fairly. The
right way to measure all this is the **roofline** plus **p99 latency under contention**, not a
datasheet peak. These are the facts the sibling metrics kit measures; this primer explains the
machine they were measured on.

## Reading order

1. [[notes/00-the-big-picture]] — the two ladders (software thread→kernel, hardware lane→GPU) and the shared L2 + one controller.
2. [[notes/01-sm-and-smsp]] — inside an SM: four sub-partitions, warp scheduler, dispatch port, FP32/INT/LD-ST/SFU pipelines.
3. [[notes/02-threads-warps-blocks-grids]] — the software ladder in detail; how blocks map to SMs; per-SM residency limits.
4. [[notes/03-occupancy-and-registers]] — the register file, occupancy, and why occupancy is not issue rate.
5. [[notes/04-cuda-cores-vs-tensor-cores]] — scalar lanes vs matrix units; 3rd- vs 5th-gen; FP16/TF32/INT8/FP8/NVFP4; mma vs tcgen05.
6. [[notes/05-memory-hierarchy]] — registers → L1/shared → L2 → DRAM; latencies and bandwidths; unified memory on one controller.
7. [[notes/06-caches-and-working-sets]] — cache lines, hits/misses, the L2 cliff, why capacity can beat bandwidth.
8. [[notes/07-sharing-the-gpu]] — context, stream, block scheduler, time-slice, MPS, SM cap, MIG; what each isolates.
9. [[notes/08-measuring-a-gpu]] — roofline, arithmetic intensity, TOPS vs achievable, solo baseline, p99, locked clocks, SASS/PTX, ncu.

Supporting files: `SOURCES.md` (what was read and how numbers were handled), `glossary.md`
(every term once, reusing the metrics-kit definitions where they exist), `constants.json` (the
cited subset of the metrics kit's constants, copied with their sources — load it, do not retype).

## Map: `00-platforms.md` Table 1 row → the note that explains it

| Table 1 row (metrics kit) | Explained in |
|---|---|
| Architecture (Ampere / Blackwell) | [[notes/00-the-big-picture]], [[notes/04-cuda-cores-vs-tensor-cores]] |
| L4T / JetPack, CUDA version | [[notes/00-the-big-picture]] (context: software stack; not elaborated) |
| Unified RAM | [[notes/05-memory-hierarchy]] (unified memory, integrated SoC) |
| CPU cores, CPU max frequency | [[notes/05-memory-hierarchy]], [[notes/07-sharing-the-gpu]] (CPU shares the controller) |
| SMs (n_SM) | [[notes/00-the-big-picture]], [[notes/01-sm-and-smsp]] |
| GPU clock (MAXN, locked), f | [[notes/00-the-big-picture]], [[notes/08-measuring-a-gpu]] (MAXN / locked clocks) |
| Sub-partitions (SMSP) per SM | [[notes/01-sm-and-smsp]] |
| Dispatch bound per SMSP, D | [[notes/01-sm-and-smsp]] |
| FP32 cores per SM | [[notes/01-sm-and-smsp]], [[notes/04-cuda-cores-vs-tensor-cores]] |
| Max warps per SM | [[notes/02-threads-warps-blocks-grids]], [[notes/03-occupancy-and-registers]] |
| Max threads per SM | [[notes/02-threads-warps-blocks-grids]] |
| Max blocks per SM | [[notes/02-threads-warps-blocks-grids]] |
| Registers per SM | [[notes/03-occupancy-and-registers]] |
| Tensor cores per SM, n_TC (3rd / 5th gen) | [[notes/04-cuda-cores-vs-tensor-cores]] |
| Tensor precisions (FP16/TF32/INT8 (+FP8/NVFP4)) | [[notes/04-cuda-cores-vs-tensor-cores]] |
| L1 + shared memory per SM | [[notes/05-memory-hierarchy]], [[notes/03-occupancy-and-registers]] |
| L1 read datapath (128 B/cycle/SM) | [[notes/05-memory-hierarchy]] |
| L2 cache (4 / 32 MB) | [[notes/05-memory-hierarchy]], [[notes/06-caches-and-working-sets]] |
| DRAM (LPDDR5 / LPDDR5X, 256-bit) | [[notes/05-memory-hierarchy]] |
| DRAM bandwidth (spec) | [[notes/05-memory-hierarchy]], [[notes/06-caches-and-working-sets]], [[notes/08-measuring-a-gpu]] |
| MIG (spatial partition) | [[notes/07-sharing-the-gpu]] |

## Provenance

- CUDA execution-model and memory facts: NVIDIA CUDA Programming Guide v13.4.2 (public). See `SOURCES.md` → Source A.
- SM internals, tensor-core generations, MPS/MIG: NVIDIA architecture blogs, CUTLASS docs, developer forums (public). See `SOURCES.md` → Source B.
- Every board-specific number: `../jetson-orin-thor-metrics/constants.json` and its notes, cited per value. See `SOURCES.md` → Source C.
- Author's reasoning (derived ratios, robotics interpretation) is labelled **(my explanation)** in the notes.

This is a discardable study aid: plain markdown, Obsidian `[[wikilinks]]`, no build step. Regenerate it rather than maintain it.
