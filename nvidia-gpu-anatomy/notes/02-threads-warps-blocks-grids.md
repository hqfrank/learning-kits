# 02 — Threads, warps, blocks and grids

**Sources:** CUDA Programming Guide §1.2.1–§1.2.2 (A-PM), §3.2.2.1 (A-HW); metrics-kit Table 1 (C-PLAT) and `constants.json`. See [[../SOURCES]].

## In one sentence
A kernel launch creates a grid of equally shaped blocks; each block is placed whole on one SM and its threads are grouped into warps of 32 for execution, and an SM holds as many blocks as fit within its warp, thread, block and register limits.

## What it is
These four words are the software ladder of [[00-the-big-picture]]:

- **thread** — one instance of the kernel function, with its own registers and program counter. Threads can branch independently (A-HW §3.2.2.1).
- **warp** — 32 threads the hardware schedules together; the real unit of execution. Lanes are numbered 0–31 (A-PM §1.2.2.2).
- **block (thread block)** — a programmer-chosen group of threads, 1-, 2- or 3-dimensional, that run together on one SM and share on-chip memory (A-PM §1.2.2.1).
- **grid** — all blocks of one launch; every block in a grid has the same size (A-PM §1.2.2.1).
- **kernel launch** — starting the grid running with a given execution configuration (grid and block dimensions) (A-PM §1.2.1).

## How it works
When you launch a kernel you specify the block shape and the grid shape (A-PM §1.2.1). The GPU's block scheduler hands each block to an SM. **All threads of a block run on one SM** and (in the common case) run there to completion; this is what lets threads in a block use fast shared memory and barrier-synchronise (A-PM §1.2.2.1). The hardware splits each block's threads into warps of 32 in a defined order and assigns the warps across the SM's four sub-partitions (A-PM §1.2.2.2; A-HW §3.2.2.1).

A grid may hold millions of blocks while the GPU has only tens of SMs, so blocks are scheduled onto SMs **in no guaranteed order**, in parallel or in series, and a block may not depend on another block (A-PM §1.2.2.1). An SM runs several blocks at once if they fit. "Fit" is set by four hardware limits, all per SM: maximum resident warps, maximum resident threads, maximum resident blocks, and the register file ([[03-occupancy-and-registers]]). The tightest limit wins.

**What "a block's threads share memory and can synchronise" guarantees.** Two things no larger unit gets (A-PM §1.2.2.3, §1.2.3.3):

1. *Shared memory.* "Shared memory" is CUDA's name for one specific thing: the programmer-managed scratchpad carved from the SM's L1/shared array. It is *not* L2. L2 is visible to every thread on the GPU but is a hardware cache nobody addresses deliberately; shared memory is shared only among the threads of one block. At launch the block receives its own allocation of its SM's L1/shared array ([[05-memory-hierarchy]]); every thread in the block can read and write any byte of it by address, no thread outside the block can see it, and it lives as long as the block. It is the only fast way for threads to pass data to each other: registers are private, and L2/DRAM are visible to all but cost ~150–500 ns a round trip against ~25–30 ns for the per-SM array (`latency_l1`, `latency_l2`, `latency_dram`). The kit's tiled GEMM is the standard use: each of the block's 1024 threads loads one element of a 32×32 tile into shared memory, then every thread reads the whole tile from there, so each element crosses from DRAM once instead of 32 times (C-KIT-NOTES B3). Two levels are in play: per *thread* the load is one scalar (4 B into one register); per *warp* the 32 threads' consecutive addresses coalesce into one 128 B cache-line request, so one warp instruction fetches one tile row and the block's 32 warps fetch the 32 rows. Production kernels go wider — `float4` loads make one warp instruction fetch 512 B (the kit's A5 probe uses them), and Ampere+ `cp.async` copies global → shared without touching registers — but the scalar version is the one whose stalls B3 decomposes (C-KIT-NOTES A5, B3; **my explanation** of the mapping).
2. *A barrier.* `__syncthreads()` stops every thread of the block until all have arrived. The tiled GEMM needs two: one after the tile is loaded (so nobody reads a slot not yet written) and one after it is consumed (so nobody overwrites it early). The barrier is cheap because the block is on one SM — the hardware counts arrivals in a per-block counter. The `barrier` row of the kit's stall table is warps waiting at exactly these points (C-KIT-NOTES B3, Table B.3.1).

Note the default: there is **no** ordering between warps otherwise, even inside one block. The scheduler issues from whichever warp is ready, so warp 3 may run far ahead of warp 0; the barrier is the only thing that imposes order, and it exists only at block scope. Two blocks on the *same* SM do not share shared memory and cannot barrier either; they are strangers sharing hardware.

**The warp row, unpacked.** *Lockstep by construction* means the 32 threads of a warp execute the same instruction at the same time because only one instruction is issued per warp — one program counter for 32 lanes. No barrier enforces it; the hardware cannot do otherwise. So within a warp a thread never needs to wait for a sibling to reach the same point. The exception is **warp divergence**: when threads branch differently the warp runs each path in turn with the other lanes masked, and lockstep is suspended until the paths reconverge; since Volta the warp-level intrinsics take an explicit lane mask (`0xffffffff`) and `__syncwarp()` re-establishes convergence (A-PM §1.2.2.2, §3.2.2.1). Two warps in a block have two program counters and are ordered only by `__syncthreads()`.

*Shuffle instructions* are the register-to-register channel this lockstep enables. Registers are private per thread, but in one warp instruction (`SHFL`; CUDA `__shfl_sync`, `__shfl_up/down_sync`, `__shfl_xor_sync`) every lane hands one register's value to another lane and receives one back — 32 values routed across the warp at once, through the register datapath, without shared memory or a barrier. A 32-value warp sum is five `__shfl_down_sync` steps (offsets 16, 8, 4, 2, 1); the same reduction across a block needs a shared-memory array and `__syncthreads()` between steps. Shuffles are the workhorse of reductions, prefix sums and the fragment rearrangement around tensor-core `mma` ([[04-cuda-cores-vs-tensor-cores]]) (A-PM warp shuffle functions; **my explanation** of the examples).

| Scope | Communicates through | Ordering guarantee |
|---|---|---|
| threads of one warp | registers via shuffle instructions, shared memory | lockstep by construction (one instruction) |
| warps of one block | shared memory | none, except at `__syncthreads()` |
| blocks on one SM | L2 / DRAM only | none |
| blocks across SMs | L2 / DRAM | none |
| kernels in one stream | L2 / DRAM | kernel N completes before N+1 starts |

Why no block-to-block barrier: blocks are not guaranteed to be co-resident. A 4096-block grid on 20 SMs runs in waves, so block 4000 may not start until block 1 has finished; a barrier across blocks could wait forever on a block not yet scheduled (A-PM §1.2.2.3, "blocks are required to execute independently"). Cross-block coordination therefore happens at the kernel boundary or through atomics on global memory. The same independence is what lets the hardware block scheduler interleave two kernels' blocks onto the SMs freely — the mechanism behind the kit's co-scheduling lockout (C-KIT-NOTES B4; [[07-sharing-the-gpu]]). (**My explanation** of the scope table and the examples.)

## On Orin and Thor (numbers from constants.json)
The per-SM residency limits, from `constants.json` (C-PLAT Table 1):

| Limit | Orin | Thor | key |
|---|---|---|---|
| Warp size | 32 | 32 | fixed by architecture (A-PM §1.2.2.2) |
| Max warps per SM | 48 | 48 | `max_warps_per_sm` |
| Max threads per SM | 1536 | 1536 | `max_threads_per_sm` (= 48 × 32) |
| Max blocks per SM | 16 | 24 | `max_blocks_per_sm` |
| Registers per SM | 65536 | 65536 | `registers_per_sm` |
| SMs per GPU | 16 | 20 | `sm_count` |

The only residency difference is max blocks per SM (16 vs 24). Both cap at 48 warps = 1536 threads per SM. Thor's extra capacity is more SMs and a higher clock, not a deeper SM.

## Common confusions
- **A warp is hardware, a block is software.** You never choose a warp size; you choose the block, and the hardware carves it into 32-thread warps (A-PM §1.2.2.2).
- **48 warps per SM is not 48 per sub-partition.** The 48-warp limit is for the whole SM; spread over four sub-partitions it is 12 warps each. That ceiling of 12 is what a scheduler draws from to hide latency ([[01-sm-and-smsp]]).
- **"Max blocks per SM" rarely binds alone.** A block of 256 threads (8 warps) hits the 48-warp limit at 6 blocks, well under Orin's 16-block cap. Warp count or registers usually bind first ([[03-occupancy-and-registers]]).
- **Grid order is not scheduling priority.** Blocks run in any order; code must not assume block 0 finishes before block 1 (A-PM §1.2.2.1).

## Why it matters for robotics workloads
Block and grid shape decide how a kernel shares an SM with others. A control-loop kernel launched as a single small block occupies one SM's slots and leaves the rest idle, yet a co-tenant's blocks can still land on that same SM and lock it out ([[07-sharing-the-gpu]], C-KIT-NOTES B4). The metrics kit sets a co-tenant's "requested occupancy" purely through its block count (C-KIT-NOTES B4), so understanding how blocks map to SM slots is how you reason about interference. For a 100 Hz loop, whether a block is resident now or queued behind a grid of someone else's blocks is the difference between meeting and missing the deadline (C-KIT-NOTES L4).

## Terms introduced
- **execution configuration** — the grid and block dimensions (and optional settings) given at kernel launch (A-PM §1.2.1).
- **resident warps / blocks** — the warps and blocks an SM holds at once; capped at 48 warps and 16 (Orin) / 24 (Thor) blocks per SM (A-HW §3.2.2; C-PLAT).
- **block scheduler** — the hardware unit that assigns blocks to SMs, in no guaranteed order (A-PM §1.2.2.1). See [[07-sharing-the-gpu]].
- **warp divergence** — threads of one warp taking different branches, serialising the paths; see [[00-the-big-picture]] (A-PM §1.2.2.2).
- (thread, warp, lane, block, grid, kernel defined in [[00-the-big-picture]].)
- **shared memory (per block)** — the block's private, programmer-managed allocation of its SM's L1/shared array; visible to all the block's threads and no one else (A-PM §1.2.3.3).
- **barrier / `__syncthreads()`** — a block-wide synchronisation point; no thread proceeds until every thread of the block has arrived. The only ordering guarantee between warps (A-PM §1.2.2.3).
- **coalescing** — the LD/ST unit merging a warp's 32 addresses into as few 128 B line requests as possible; a scalar load across consecutive addresses is one request per warp (A-PM §1.2.3.3.1).
- **lockstep** — the 32 threads of a warp executing one issued instruction together; the warp's built-in ordering, suspended only during divergence (A-PM §1.2.2.2).
- **shuffle (`__shfl_*_sync`)** — a warp instruction that moves a register value from one lane to another for all 32 lanes at once; the register-to-register channel within a warp (A-PM warp shuffle functions).
