# Platforms (Table 1)

**Source:** book.pdf, "Platforms" (unnumbered section before Doc A), Table 1 — `common/platforms.tex`  ·  **Status in source:** shared front matter, cited by every later section

## In one sentence
Both boards are integrated SoCs where CPU and GPU share one LPDDR memory and one memory controller, and Thor beats Orin on SM count (20 vs 16), clock (1.575 vs 1.30 GHz), L2 capacity (32 vs 4 MB) and tensor-core generation (5th vs 3rd), while the structure inside each SM (4 sub-partitions, 1 instruction per cycle each) is the same.

## What it measures
This section measures nothing. It lists device-queried facts for the two boards at the standing configuration. The standing configuration is MAXN (NVIDIA's maximum-clock power regime) with GPU clocks locked and devfreq-verified per run. Measured rates (bandwidth, tensor throughput) are results and live in their own sections, not here.

## How
The campaign queried each device for its hardware attributes and recorded the software stack. Every later section cites Table 1 for clock, SM count, L2 size and DRAM specification instead of restating them.

## Predicted
Not applicable. The section states facts, not predictions.

## Measured
The three architectural facts the book says recur throughout:

1. **Integrated SoC.** On both modules the CPU and GPU share one physical LPDDR memory and one memory controller. There is no discrete GPU memory. Every CPU↔GPU contention result rests on this fact.
2. **SM sub-partitions.** Each SM has four sub-partitions (SMSPs). Each SMSP has one warp scheduler and one dispatch port. The issue bound per SMSP is therefore one instruction per cycle.
3. **Tensor-core generation asymmetry.** Orin's 3rd-generation tensor cores support FP16, TF32 and INT8. Thor's 5th-generation cores (the `tcgen05` datapath with tensor memory) add FP8 and NVFP4. Orin has neither.

Table 1, as given in the source:

| Property | Orin AGX (sm_87) | Thor T5000 (sm_110) |
|---|---|---|
| Architecture | Ampere | Blackwell |
| L4T / JetPack | R36.4.7 / JP6 | R39.2.0 / JP7.2 |
| CUDA | 12.6 | 13.2 |
| Unified RAM | 30 GB | 123 GB |
| CPU cores | 12 × Cortex-A78AE | 14 × Neoverse-V3AE |
| CPU max frequency | 2.20 GHz | 2.60 GHz |
| SMs (MAXN), n_SM | 16 | 20 |
| GPU clock (MAXN, locked), f | 1.30 GHz | 1.575 GHz |
| Sub-partitions (SMSP) per SM | 4 | 4 |
| Dispatch bound per SMSP, D | 1 inst/cycle | 1 inst/cycle |
| FP32 cores per SM | 128 | 128 |
| Max warps per SM | 48 | 48 |
| Max threads per SM | 1536 | 1536 |
| Max blocks per SM | 16 | 24 |
| Registers per SM | 64K | 64K |
| Tensor cores per SM, n_TC | 4 (3rd-gen) | 4 (5th-gen, tcgen05) |
| Tensor precisions | FP16, TF32, INT8 | + FP8, NVFP4 |
| L1 + shared memory per SM | 164 KB | 228 KB |
| L1 read datapath | 128 B/cycle/SM | 128 B/cycle/SM |
| L2 cache | 4 MB | 32 MB |
| DRAM | LPDDR5, 256-bit | LPDDR5X, 256-bit |
| DRAM bandwidth (spec) | 204.8 GB/s | ~273 GB/s |
| MIG (spatial partition) | none | tech-preview (r39.2) |

## The gap, and what it means
Not applicable here. The later notes compare measured rates against ceilings derived from these facts.

## So what
Interpretation (mine, from the table): the per-SM machinery is identical on the two boards, so a kernel bound by instruction issue scales by clock × SM count only (1.575 × 20 / (1.30 × 16) = 1.51×). The large differences are in memory: Thor has 8× the L2 and about 1.33× the DRAM specification. The book's Doc A shows that these memory differences, not the TOPS figures, decide most robotics workloads.

## Terms introduced
- **MAXN** — NVIDIA's maximum-clock power regime on Jetson; the standing configuration for every measurement in the book.
- **SM** — streaming multiprocessor, the GPU's compute unit; 16 on Orin, 20 on Thor.
- **SMSP** — SM sub-partition; each SM has four, each with one warp scheduler and one dispatch port.
- **dispatch bound (D)** — the number of warp instructions one SMSP can issue per cycle; 1 on both boards.
- **tcgen05** — Thor's 5th-generation tensor-core datapath with tensor memory; the datapath the datasheet peaks assume.
- **integrated SoC** — a system on chip where CPU and GPU share one physical memory and one memory controller.
- **L4T / JetPack** — NVIDIA's Linux for Tegra and the Jetson software stack version.
- **MIG** — multi-instance GPU, NVIDIA's spatial partitioning of a GPU; tech-preview on Thor, absent on Orin.
