# 00 — The big picture: two ladders, one chip

**Sources:** CUDA Programming Guide §1.2 (A-PM); metrics-kit Table 1 (C-PLAT) and `constants.json` (C-CONST). See [[../SOURCES]].

## In one sentence
A GPU is a set of streaming multiprocessors behind one shared L2 cache and one memory controller, and you reach it through two ladders that stay separate on purpose: a **software ladder** (thread → warp → block → grid → kernel) that you write, and a **hardware ladder** (lane → sub-partition → SM → GPU) that runs it.

## What it is
The GPU is a throughput machine. It hides memory latency by keeping thousands of threads in flight and switching between them every cycle, instead of using the large caches and out-of-order execution a CPU uses to make one thread fast. To program it you describe a large amount of parallel work in software terms; the hardware maps that work onto its physical units. The two descriptions are deliberately decoupled so the same program runs on a GPU with one SM or hundreds (A-PM §1.2.2.1).

The two ladders, side by side:

| Software (what you write) | Hardware (what runs it) | Relationship |
|---|---|---|
| **thread** — one instance of the kernel | **lane** — one of 32 slots in a warp | one thread runs in one lane (A-PM §1.2.2.2) |
| **warp** — 32 threads, the scheduling unit | **sub-partition (SMSP)** — one warp scheduler | the hardware groups threads into warps; a warp is issued by one SMSP ([[01-sm-and-smsp]]) |
| **block** — threads that share memory and can sync | **SM** — streaming multiprocessor | all threads of a block run on one SM (A-PM §1.2.2.1) |
| **grid** — all blocks of one launch | **GPU** — all SMs behind one L2 | blocks are distributed across SMs in any order (A-PM §1.2.2.1) |
| **kernel** — the function launched on the grid | — | launching a kernel starts its grid of threads (A-PM §1.2.1) |

## How it works
You launch a **kernel** — a function compiled for the GPU — with an *execution configuration* that gives the grid and block dimensions (A-PM §1.2.1, §1.2.2.1). The launch creates a **grid** of **blocks**, each block a group of **threads**. The hardware assigns each block to one **SM** and keeps it there until it finishes; it groups the block's threads into **warps** of 32 and hands each warp to a **sub-partition** inside the SM to issue (A-PM §1.2.2.1–§1.2.2.2). There is no ordering guarantee between blocks, so a block may not depend on another block's result (A-PM §1.2.2.1). That rule is what lets one grid run on any size of GPU.

Below the SMs sit the shared parts: a single **L2 cache** that every SM reads and writes, and a single **memory controller** to DRAM (A-PM §1.2.3.3.1, §1.2.2). On the two boards this primer targets, the CPU and GPU share that one controller and one physical memory — they are integrated SoCs ([[05-memory-hierarchy]], C-PLAT).

## On Orin and Thor (numbers from constants.json)
Both boards have the same ladder; they differ in how many rungs wide each level is. From `constants.json`:

- **SMs per GPU:** 16 (Orin) vs 20 (Thor) — `sm_count` (C-PLAT Table 1).
- **Sub-partitions per SM:** 4 on both — `smsp_per_sm` (C-PLAT Table 1).
- **Threads per lane group (warp):** 32 on both — the warp size is fixed by the architecture (A-PM §1.2.2.2).
- **Clock:** 1.30 GHz (Orin) vs 1.575 GHz (Thor) — `gpu_clock_maxn_locked` (C-PLAT Table 1).

A kernel limited only by instruction issue therefore scales as clock × SM count. The metrics kit computes 1.575 × 20 / (1.30 × 16) = **1.51×** Thor over Orin for such a kernel (C-PLAT "So what"). The large differences between the boards are in the shared memory levels, not the per-SM ladder ([[05-memory-hierarchy]]).

## Common confusions
- **A warp is not something you declare.** You write threads and blocks; the hardware forms warps of 32. If a block is not a multiple of 32 threads, the last warp runs with unused lanes (A-PM §1.2.2.2).
- **A block does not span SMs.** All threads of one block run on one SM, which is why they can share memory and synchronise; threads in different blocks cannot assume they run together (A-PM §1.2.2.1).
- **"CUDA core" is a lane of the datapath, not an SM.** The SM is the whole compute unit; the CUDA cores are the FP32/INT arithmetic lanes inside it ([[01-sm-and-smsp]], [[04-cuda-cores-vs-tensor-cores]]).

## Why it matters for robotics workloads
A robot runs several things on one GPU at once: a control loop, perception networks, maybe a large policy model. Each is a kernel launching its own grid. Because blocks from different grids land on the same SMs and all traffic funnels through one L2 and one controller, the kernels interfere. The whole point of the metrics kit's Doc B and L4 work is that this interference, not raw throughput, decides whether the control loop meets its deadline ([[07-sharing-the-gpu]], C-KIT-NOTES L4). You cannot reason about that without the two-ladder picture: the software ladder says what you asked for, the hardware ladder says what physically shares a wire.

## Terms introduced
- **kernel** — a function launched to run on the GPU; launching it starts a grid of threads (A-PM §1.2.1).
- **thread** — one instance of the kernel's code, with its own registers and program counter (A-PM §1.2.2.2).
- **warp** — a group of 32 threads that the hardware schedules and issues together (A-PM §1.2.2.2).
- **lane** — one of the 32 thread slots in a warp, numbered 0–31 (A-PM §1.2.2.2).
- **block (thread block)** — a group of threads that run on one SM and can share memory and synchronise (A-PM §1.2.2.1).
- **grid** — all the blocks produced by one kernel launch (A-PM §1.2.2.1).
- **SM (streaming multiprocessor)** — the GPU's compute unit; it holds blocks and runs their warps. Reused from `../jetson-orin-thor-metrics/glossary.md` (C-PLAT).
- **SMSP (sub-partition)** — one of four scheduling units inside an SM; each has one warp scheduler. Reused from the metrics-kit glossary (C-PLAT).
- **L2 cache** — the one cache shared by all SMs on the GPU (A-PM §1.2.3.3.1).
- **memory controller** — the single path from the GPU (and, on an integrated SoC, the CPU too) to DRAM (A-PM §1.2.2; C-PLAT).
