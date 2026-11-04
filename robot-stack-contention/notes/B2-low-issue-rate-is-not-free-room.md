# B2 — A low issue rate is not free room: kernel fill and waves

**Source:** per-SM limits from the CUDA Programming Guide compute-capability table (https://docs.nvidia.com/cuda/cuda-c-programming-guide/) and the sibling kit [`../../jetson-orin-thor-metrics/`](../../jetson-orin-thor-metrics/README.md); occupancy and issue rate from [`../../nvidia-gpu-anatomy/notes/03-occupancy-and-registers.md`](../../nvidia-gpu-anatomy/notes/03-occupancy-and-registers.md); every number from [`../constants.json`](../constants.json) by key · **Status:** method note. **All measured values here are illustrative** (class `illustrative`): round teaching numbers, not measurements.

## In one sentence
The SMs use only a small share of their instruction-issue slots in the full stack, but by launch configuration about half of the GPU kernel time leaves the SMs at least 90 % full on some resource (illustrative, `kernel_time_sms_full_share`), so a low issue rate does not mean room for another process; and many kernels run in several waves, so more SMs would be expected to shorten them unless memory limits them.

## What it measures
**Caution first: the fill numbers are theoretical.** They come from launch configurations in solo kernel traces. Achieved occupancy per kernel, stall reasons and real co-residency under MPS were not measured.

**SM issue rate** is the share of the GPU's instruction-issue slots that were used. In an illustrative measurement it is about 0.2 of peak in the full stack (illustrative, `sm_issue_full_stack`), while the GPU has work about 0.6 of the time (illustrative, `gpu_active_full_stack`). The sibling primer explains issue rate and occupancy in [`../../nvidia-gpu-anatomy/notes/03-occupancy-and-registers.md`](../../nvidia-gpu-anatomy/notes/03-occupancy-and-registers.md).

**Kernel fill** asks a different question: when a kernel runs, how full does it make each SM? An SM holds blocks up to four limits. On an Orin-class board (Jetson AGX Orin) the limits per SM are:

| Limit | Value | Key |
|---|---|---|
| Resident warps | 48 | `max_warps_per_sm` |
| Resident blocks | 16 | `max_blocks_per_sm_cc87` |
| Registers | 65 536 | `registers_per_sm` |
| Shared memory (max per SM) | 164 KB | `l1_shared_per_sm_orin_kb` |

For each launch, the **binding fill** is the largest used fraction of any of the four limits, on the busiest SM in the first wave. A binding fill of at least 90 % (threshold from the source text of `kernel_time_sms_full_share`) means that SM has little room left for a block of another kernel.

**Waves.** A kernel with more blocks than the 16 SMs (`sm_count_orin`) can hold at once runs in rounds. The number of waves is ⌈blocks ÷ (SMs × blocks per SM)⌉.

## How
A script reads existing solo kernel traces from a system-wide profiler. For each launch it takes the grid size, block size, registers per thread and shared memory per block. From these it computes how many of the kernel's blocks one SM can hold. It then weights each kernel's fill by the kernel's duration.

**Worked example of a register limit.** To fill all 48 warp slots, a kernel may use at most about 40 registers per thread (my estimate from `registers_per_sm`, `max_warps_per_sm`, `warp_size` and `register_alloc_unit_per_warp`: 65 536 ÷ 48 ≈ 1 365 registers per warp, rounded down to a multiple of 256 = 1 280, ÷ 32 threads = 40). A matrix-multiply kernel often uses far more, up to 255 per thread (`max_registers_per_thread`). Its SM is then full by registers with only a few warps resident.

Analogy: a car park can be "full" because a few wide vans take every space, even though few drivers are moving.

## Predicted
The earlier reading, before correction:

1. MPS helps when kernels leave SMs idle, as the low issue rate suggests.
2. More SMs mostly add idle SMs.

This note shows why both were too simple.

## Measured
Share of kernel time, from solo traces, theoretical, as an illustrative measurement:

| Quantity | Value (illustrative) | Key |
|---|---|---|
| Kernel time with SMs ≥ 90 % full on some resource | about 0.5 | `kernel_time_sms_full_share` |
| Warp-slot fill of the large matrix-multiply (GEMM) kernels | 0.1–0.3 | `gemm_warp_slot_fill` |
| Kernel time in kernels larger than one wave, per service | 0.35–0.7 | `multiwave_share` |

The large GEMM kernels belong to the object detector and to the VLA. Those SMs are full by registers or shared memory, not by warps. The per-service split is not given here; the qualitative pattern is that the depth camera service, the object detector and the VLA each spend a large part of their kernel time in full kernels.

## The gap, and what it means
**Correction kept visible: "a low issue rate means room".** A low issue rate and full SMs are compatible. A register-bound GEMM kernel occupies its SMs with few warps (illustrative, `gemm_warp_slot_fill`). Its issue rate is low, and still no other block fits. Why the issue rate is low, for example memory stalls, was not measured.

**Correction kept visible: "more SMs help multi-wave kernels".** The earlier statement was "mostly no, more SMs add idle SMs". That was wrong for multi-wave kernels (illustrative, `multiwave_share`). A GPU with more SMs could run them in fewer waves.

- For kernels with many waves the gain is roughly in proportion to the SM count.
- For kernels with only a few waves the gain comes in steps, and it can be zero, because the last wave rounds up.
- There is no gain where a kernel is limited by DRAM bandwidth, L2 or memory latency. This was not measured per kernel.

This is an expectation, not a measurement.

**What it means for MPS** (hypothesis, see [[B3-mps-in-practice]]). In the rest of the kernel time the SMs have room: small grids, partial last waves, and kernels below the 90 % threshold (`kernel_time_sms_full_share`) on every resource. There, kernels of two processes could overlap. During full kernels, MPS mainly changes the granularity of sharing. The other process's blocks can start as SM resources free up, instead of after a whole time slice and a context switch (see [[B1-gpu-time-slicing-and-the-dose-curve]]).

**Limits of the traces.**

- The VLA trace used a different model version from the one that runs next to the stack.
- The detector trace was fed by the measurement probe's replay, not by a live camera.
- The people-perception trace is an empty scene.
- One audio service's trace did not record CUDA graph nodes.
- The limits assume the 16-SM board (`sm_count_orin`).

## So what
A GPU can look mostly idle as a compute measure and still be full as a sharing measure (interpretation). Before predicting what MPS or a bigger GPU buys, compute the kernel fill and the wave count of the kernels that hold the GPU time.

## Terms introduced
- **SM issue rate** — the share of instruction-issue slots used. Related to **issue rate** in `../nvidia-gpu-anatomy/glossary.md`.
- **kernel fill (binding fill)** — the largest used fraction of an SM's warps, blocks, registers or shared memory for one kernel, from its launch configuration.
- **warp-slot fill** — the fraction of an SM's warp slots that a kernel's resident blocks use; theoretical occupancy. See **occupancy** in `../nvidia-gpu-anatomy/glossary.md`.
- **register-bound / shared-memory-bound** — a kernel whose blocks per SM are limited by registers or by shared memory rather than by warps.
- **wave** — one round of a kernel's blocks across all SMs; a kernel needs ⌈blocks ÷ (SMs × blocks per SM)⌉ waves.
- **SM active** — at least one warp resident on the SM; not the same as full.
- **theoretical vs achieved occupancy** — fill from the launch configuration vs fill measured on the hardware; only the first was computed here.
