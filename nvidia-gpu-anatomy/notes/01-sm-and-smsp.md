# 01 — The SM and its four sub-partitions

**Sources:** CUDA Programming Guide §1.2.2, §3.2.2 (A-PM, A-HW); SM-internals forums (B-FORUMS); metrics-kit Table 1 (C-PLAT) and `constants.json`. See [[../SOURCES]].

## In one sentence
A streaming multiprocessor is split into four sub-partitions, each with its own warp scheduler and one dispatch port that issues at most one warp instruction per cycle into that sub-partition's arithmetic pipelines (FP32, INT, load/store, special-function, tensor).

## What it is
The SM is the GPU's compute unit ([[00-the-big-picture]]). Inside, it is not one monolithic core but four near-identical **sub-partitions** (NVIDIA's term is SM sub-partition, SMSP), plus resources the four share: the register file is split per sub-partition, while the unified data cache (L1 + shared memory), the texture/load-store machinery and the tensor-core access are shared across the SM (A-PM §1.2.2; B-FORUMS). Each sub-partition is the thing that actually schedules and issues warps.

Each sub-partition contains (B-FORUMS; corroborated by C-PLAT Table 1):
- **one warp scheduler** — picks a ready warp each cycle;
- **one dispatch port** — issues the chosen warp's instruction (the metrics kit calls this the dispatch bound D = 1 instruction per cycle);
- **one bank of the SM's register file** (one quarter of the 65536 registers, C-PLAT) from which its resident warps are each allocated a slice of registers at launch. Counting: one register file per SM, four banks per file, 65536 four-byte registers per file, a few dozen registers per *thread*. A thread has a slice of a bank, not a file of its own (B-FORUMS; **my clarification** after a reader question, 2026-10-02);
- **arithmetic pipelines**: FP32 CUDA cores, an INT pipe, a load/store (LD/ST) unit, a special-function unit (SFU) for transcendentals, and access to the SM's tensor core.

## How it works
Every cycle, each sub-partition's warp scheduler looks at the warps assigned to it, finds one that is not stalled, and issues one of its instructions to the matching pipeline (A-HW §3.2.2.1; B-FORUMS). The SM issues instructions **in order** and does no branch prediction or speculation — unlike a CPU core, it hides latency by having many warps to switch among, not by guessing ahead (A-HW §3.2.2). When the chosen warp's instruction is a 32-wide arithmetic op, the sub-partition's FP32 lanes execute all 32 threads; on GA10x/Ampere-class parts the sub-partition has two FP32-capable datapaths of 16 lanes each, which is why the SM reaches 128 FP32 CUDA cores (4 sub-partitions × 32) (B-FORUMS "Instruction scheduling in Ampere"; C-PLAT).

**What one warp instruction looks like.** The scheduler issues one instruction to one warp, and all 32 threads execute it together — same opcode, same register *numbers*, each thread's own register *values* (A-HW §3.2.2, the SIMT model). `FFMA R4, R2, R3, R4` means "every thread computes its R2×R3+R4 into its R4": 32 independent multiply-adds from one issue slot, one per FP32 lane. Lane count sets the pass time: the sub-partition's 32 FP32 lanes take an FFMA warp in one cycle (θ_FFMA = 1), but only one 16-lane half does integer math, so an IMAD warp needs two cycles (θ_IMAD = 0.5), and the separate 16-lane ALU pipe likewise (C-KIT-NOTES A1, Table A.1.3). A load is the same shape: 32 addresses go out, the LD/ST unit coalesces them into as few 128 B line requests as the addresses allow, and 32 values come back into 32 registers. Lanes sit idle only under **warp divergence**, when threads take different branches and each path runs with the others masked off ([[02-threads-warps-blocks-grids]]). A tensor-core instruction is also issued once per warp, but the matrix operands are spread across all 32 threads' registers; see [[04-cuda-cores-vs-tensor-cores]].

**Issue versus latency, and why the pipes are pipelined.** "Lane count sets the pass time" is about *issue*: how often the dispatch port can start a new warp instruction on a pipe (one per cycle for 32 lanes, one per two cycles for 16). It is not the time until the result exists. Each lane is a short pipeline of a few stages (about four for FFMA); a stage is busy for one cycle, then hands the work on and accepts the next instruction. So a single FFMA takes ~4 cycles from issue to usable result, yet the pipe can accept a new FFMA every cycle, holding four in flight at different stages — an assembly line that finishes a car every minute though each car spends four minutes on it (A-HW §3.2.2; **my explanation** of the stage count, which the kit does not publish).

This is what the kit's A1 probe exploits with "four independent chains" (C-KIT-NOTES A1, Table A.1.1). One chain `a = a*c + d; a = a*c + d; …` must wait the full latency between instructions, so the pipe issues once per ~4 cycles and three quarters of its stages sit empty; the measurement would be latency. Four accumulators `a0 … a3` updated in rotation give the scheduler a ready instruction every cycle:

```
cycle:  1  2  3  4  5  6  7  8
a0:     S1 S2 S3 S4 S1 S2 S3 S4
a1:        S1 S2 S3 S4 S1 S2 S3
a2:           S1 S2 S3 S4 S1 S2
a3:              S1 S2 S3 S4 S1
```

From cycle 4 on, every stage holds an instruction and the pipe issues one FFMA per cycle: θ_FFMA = 1. All of this is one warp on one sub-partition; the four sub-partitions then multiply it by four. Four chains, not more, because the pipe is about four stages deep; the deeper integer `dp4a` pipe needed ILP = 8 (C-KIT-NOTES A2). Real kernels fill the same pipe a second way — from *other* resident warps whenever this warp's next instruction is not ready — which is what occupancy supplies ([[03-occupancy-and-registers]]). The pipe does not care where the independent instruction comes from; it needs one every cycle from somewhere, and B3 shows the failure when neither source has one (C-KIT-NOTES B3).

The **issue bound** follows directly: one dispatch port per sub-partition, four sub-partitions, so the SM issues at most 4 warp instructions per cycle. Peak arithmetic rate is this issue rate times the lanes per instruction times the clock times the SM count — the shape every CUDA-core ceiling takes ([[04-cuda-cores-vs-tensor-cores]], C-KIT-NOTES A2).

## On Orin and Thor (numbers from constants.json)
The per-SM structure is identical on the two boards (C-PLAT "In one sentence"). From `constants.json`:

- **Sub-partitions per SM:** 4 on both — `smsp_per_sm`.
- **Dispatch bound per sub-partition:** 1 instruction/cycle on both — `dispatch_bound_per_smsp`.
- **FP32 CUDA cores per SM:** 128 on both — `fp32_cores_per_sm` (32 per sub-partition).
- **Tensor cores per SM:** 4 on both, one per sub-partition — `tensor_cores_per_sm` (Orin 3rd-gen, Thor 5th-gen; [[04-cuda-cores-vs-tensor-cores]]).

The boards differ only in SM count (16 vs 20) and clock (1.30 vs 1.575 GHz) — `sm_count`, `gpu_clock_maxn_locked`. So an issue-bound kernel's speedup is exactly the clock × SM-count ratio, 1.51× ([[00-the-big-picture]], C-PLAT).

## Common confusions
- **"128 CUDA cores" is per SM, not per sub-partition.** Each sub-partition has 32 FP32 lanes; four of them make 128 (B-FORUMS; C-PLAT).
- **The dispatch bound is per sub-partition, not per SM.** D = 1 means one instruction per cycle *per sub-partition*; the SM issues up to 4 (C-PLAT; B-FORUMS).
- **More FP32 cores does not mean more instructions issued.** The 32 lanes of a warp are driven by *one* instruction. Issue rate is bounded by dispatch ports (4/SM), not by core count. This is the seed of the occupancy-vs-issue-rate point in [[03-occupancy-and-registers]].
- **A GPU hides latency differently from a CPU.** A CPU core keeps one thread busy during a cache miss with **out-of-order execution** (running later, independent instructions from a window of a few hundred while the load is outstanding, then retiring in order) fed by **branch prediction** (guessing the branch so the window stays full; the two are separate tricks — one for data dependencies, one for control flow). A sub-partition does neither: it issues in order and never speculates, and instead switches to another resident warp that is ready (A-HW §3.2.2). Same goal, different source of independent work: the CPU finds it inside one thread, the GPU takes it from other warps. Consequences in the kit: A1's "four independent chains" is the programmer supplying the parallelism an out-of-order core would discover for itself (C-KIT-NOTES A1), and B3's "occupancy is not issue rate" is the GPU form of "a big window does not help when everything in it waits on the same miss" (C-KIT-NOTES B3). **My explanation** of the comparison.
- **The datacenter A100 (GA100) has 64 FP32 cores/SM, not 128.** Orin is a GA10x-class part (sm_87) with 128 (B-AMPERE describes GA100; C-PLAT gives Orin's 128). Do not read datacenter whitepaper per-SM numbers onto Jetson.

## Why it matters for robotics workloads
The sub-partition is where latency hiding happens. A control-loop kernel that is launch-bound or has too few warps per sub-partition leaves dispatch ports idle every cycle it stalls, and no amount of FP32 cores helps. The metrics kit shows a batch-1 control GEMM running far below the arithmetic roof precisely because it cannot fill the sub-partitions' schedulers (C-KIT-NOTES B4, L4). Understanding the four schedulers is the first step to reading a profiler's stall counters ([[08-measuring-a-gpu]], C-KIT-NOTES B3).

## Terms introduced
- **sub-partition (SMSP)** — one of four scheduling units in an SM; one warp scheduler, one dispatch port, one bank of the SM's register file, and arithmetic pipelines. Reused from `../jetson-orin-thor-metrics/glossary.md` (C-PLAT; B-FORUMS).
- **warp scheduler** — the per-sub-partition unit that selects a ready warp to issue each cycle (B-FORUMS).
- **dispatch port** — the per-sub-partition issue slot; one warp instruction per cycle (the metrics kit's dispatch bound D) (C-PLAT; B-FORUMS).
- **dispatch bound (D)** — warp instructions one sub-partition can issue per cycle; 1 on both boards. Reused from the metrics-kit glossary (C-PLAT).
- **FP32 CUDA core** — one lane of the sub-partition's FP32 arithmetic datapath; 32 per sub-partition, 128 per SM (B-FORUMS; C-PLAT).
- **INT pipe** — the integer arithmetic pipeline in a sub-partition, separate from FP32 on Ampere and later (B-FORUMS).
- **LD/ST unit** — the load/store pipeline that issues memory instructions. See **LSU** in the metrics-kit glossary (C-KIT-NOTES A7).
- **SFU (special-function unit)** — the pipeline for transcendentals (sin, exp, reciprocal) (B-FORUMS).
- **out-of-order execution** — a CPU technique: execute independent later instructions while an earlier one waits, retire in order; absent on GPU sub-partitions, which rely on other warps instead (A-HW §3.2.2; general CPU architecture).
- **branch prediction** — a CPU technique: guess a branch outcome and execute speculatively so the pipeline stays full; absent on GPU sub-partitions (A-HW §3.2.2; general CPU architecture).
- **pipelining** — splitting a lane's work into stages so a new instruction can enter every cycle while earlier ones are still in flight; gives per-cycle throughput despite multi-cycle latency (general CPU/GPU architecture).
- **instruction-level parallelism (ILP)** — independent instructions within one thread that can be in flight at once; the kit's "chains" (C-KIT-NOTES A1).
- **issue rate vs latency** — how often a pipe accepts a new warp instruction (θ) versus how many cycles one instruction takes to produce its result; lane count sets the former, pipeline depth the latter.
