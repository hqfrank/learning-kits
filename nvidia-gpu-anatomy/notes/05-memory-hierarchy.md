# 05 — The memory hierarchy

**Sources:** CUDA Programming Guide §1.2.3 (A-PM); metrics-kit `A5`, `A6`, `A7`, Table 1 (C-PLAT) and `constants.json`. See [[../SOURCES]].

## In one sentence
A GPU's memory is a ladder from fastest and smallest to slowest and largest — registers and L1/shared memory private to each SM, then one L2 cache shared by all SMs, then DRAM behind one memory controller — and on Orin and Thor that DRAM is physically shared with the CPU because both are integrated SoCs.

## What it is
The levels, from the top (A-PM §1.2.3):

- **Registers** — per thread, in the SM's register file; the fastest storage. Registers are listed here because every load ends in one, but they are **not a cache level**: the compiler fixes how many each thread gets, the hardware allocates them at block launch, and no address is ever looked up in them. A working set cannot "fit in registers" the way it fits in L2 ([[03-occupancy-and-registers]]).
- **L1 / shared memory** — one unified on-chip array per SM, split at runtime into hardware-managed L1 cache and programmer-managed shared memory. Private to the SM; shared memory is visible to all threads in a block (A-PM §1.2.3.3).
- **L2 cache** — one cache for the whole GPU, shared by every SM (A-PM §1.2.3.3.1).
- **DRAM (global memory)** — the GPU's main memory, reachable by all SMs through the memory controller (A-PM §1.2.3.1).

Latency rises and bandwidth falls as you descend, but **capacity rises** — the trade the whole hierarchy exists to manage.

## How it works
A thread's load first tries L1 on its own SM; a miss goes to the shared L2; an L2 miss goes to DRAM through the controller (A-PM §1.2.3.3.1). Because L1/shared is **per SM** and L2 is **device-wide**, L2 and DRAM are shared resources — every SM's traffic contends there ([[06-caches-and-working-sets]], [[07-sharing-the-gpu]]). The **L1/shared carveout** lets you trade cache for scratchpad: more shared memory for a tiling kernel, or more L1 for an irregular one (A-PM §1.2.3.3).

**Unified memory on an integrated SoC.** On a discrete GPU, DRAM is separate from CPU memory and data is copied across PCIe. On Orin and Thor the CPU and GPU share one physical LPDDR memory and **one memory controller** — there is no discrete GPU memory (C-PLAT "Measured" point 1). CUDA's unified-memory model lets one allocation be reached from CPU or GPU (A-PM §1.2.3.4); on these SoCs that sharing is physical, so CPU memory traffic and GPU memory traffic compete for the same controller ([[07-sharing-the-gpu]], C-KIT-NOTES B4/L4).

## On Orin and Thor (numbers from constants.json)
Capacity, bandwidth and latency per level, from `constants.json`:

| Level | Scope | Orin | Thor | keys |
|---|---|---|---|---|
| L1 + shared / SM | per SM | 164 KB | 228 KB | `l1_shared_per_sm` (C-PLAT) |
| L1 read datapath | per SM | 128 B/cycle | 128 B/cycle | `l1_read_datapath` (C-PLAT) |
| L1 dependent-load latency | per SM | 29.9 ns | 25.3 ns | `latency_l1` (C-KIT-NOTES A7) |
| L2 size | whole GPU | 4 MB | 32 MB | `l2_size` (C-PLAT) |
| L2 resident read BW | whole GPU | 2200 GB/s | 3790 GB/s | `l2_resident_read_bandwidth` (C-KIT-NOTES A6) |
| L2 dependent-load latency | whole GPU | 146 ns | 156 ns | `latency_l2` (C-KIT-NOTES A7) |
| DRAM read BW (measured) | whole GPU | 177 GB/s | 259 GB/s | `dram_bandwidth_read_measured` (C-KIT-NOTES A6) |
| DRAM dependent-load latency | whole GPU | 675 ns | 510 ns | `latency_dram` (C-KIT-NOTES A7) |

Two facts the kit stresses. First, **L2-resident streaming is 12.4× (Orin) / 14.6× (Thor) faster than DRAM** (`l2_dram_bandwidth_ratio`, C-KIT-NOTES A6). Second, **L2 latency did not improve Orin → Thor** (146 vs 156 ns); only L2 *capacity* grew, 8× (`l2_dram_capacity_ratio`, C-KIT-NOTES A7/A6). Thor's memory advantage is "more data stays resident," not "resident data is reached faster" (C-KIT-NOTES A7).

## Common confusions
- **Registers are storage, not a cache rung.** The three addressable levels are L1/shared → L2 → DRAM; a footprint is placed in one of them by capacity. Registers hold values the compiler assigned, never a working set. Listing the 256 KB register file (64K × 4 B) above the 164/228 KB L1 as if it were a bigger cache is a category error — it misled the first version of this kit's memory-ladder explorer (reader question, 2026-10-02).
- **L1 and shared memory are the same silicon.** One array, split by a runtime carveout; they are not two separate memories (A-PM §1.2.3.3).
- **L2 is shared; L1 is not.** Two kernels on different SMs do not share L1, but they share L2 and the controller — the root of GPU contention ([[07-sharing-the-gpu]]).
- **Integrated ≠ just "no copy."** The upside is zero-copy sharing; the downside is that CPU and GPU fight over one controller, which is a major theme of the metrics kit (C-KIT-NOTES B4/L4).
- **Bigger L2 does not mean faster L2.** Thor's L2 is 8× larger but about the same latency (C-KIT-NOTES A7).

## Why it matters for robotics workloads
Where a kernel's working set sits in this ladder decides its speed far more than its FLOP count. The metrics kit's framing: the first question to ask of a robot kernel is whether its working set is under 4 MB, between 4 and 32 MB, or over 32 MB — the answer picks which bandwidth regime it runs in (C-KIT-NOTES A6). A policy whose weights fit Thor's 32 MB L2 runs an order of magnitude faster than the same policy spilling to DRAM ([[06-caches-and-working-sets]]). And because the controller is shared with the CPU, a busy CPU can throttle the GPU's memory even when the GPU is idle on compute ([[07-sharing-the-gpu]], C-KIT-NOTES L4).

## Terms introduced
- **registers** — per-thread fastest storage in the SM register file; allocated at launch, not addressed, so not a cache level (A-PM §1.2.3.3). See [[03-occupancy-and-registers]].
- **L1 cache / shared memory** — the per-SM unified on-chip array, split by a runtime carveout into hardware L1 and programmer-managed shared memory (A-PM §1.2.3.3).
- **L1 carveout** — the share of the L1/shared array configured as L1 cache. Reused from `../jetson-orin-thor-metrics/glossary.md` (C-KIT-NOTES A5).
- **L2 cache** — the device-wide cache shared by all SMs (A-PM §1.2.3.3.1). See [[00-the-big-picture]].
- **global memory / DRAM** — the GPU's main memory behind the controller (A-PM §1.2.3.1).
- **unified memory** — CUDA allocations reachable from CPU or GPU; physically shared on an integrated SoC (A-PM §1.2.3.4; C-PLAT).
- **integrated SoC** — CPU and GPU on one chip sharing one physical memory and one controller. Reused from the metrics-kit glossary (C-PLAT).
- **L2:DRAM ratio** — L2-resident bandwidth over DRAM bandwidth; 12.4× Orin, 14.6× Thor. Reused from the metrics-kit glossary (C-KIT-NOTES A6).
