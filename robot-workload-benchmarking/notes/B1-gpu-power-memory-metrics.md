# B1 — GPU, power, and memory metrics

**Source:** `tegrastats` (NVIDIA Jetson Linux Developer Guide, https://docs.nvidia.com/jetson/), `nvidia-smi` utilization (https://developer.nvidia.com/system-management-interface), Linux cgroups v2 memory (https://docs.kernel.org/admin-guide/cgroup-v2.html). Integrated-SoC behaviour in [[../jetson-orin-thor-metrics/notes/00-platforms|the sibling platforms note]]. · **Status:** concept primer, no measured numbers.

## In one sentence
GPU, power, and memory metrics on an integrated robot board are all approximate and easy to misread: GPU-busy is a time-busy fraction not an occupancy, the memory-bandwidth index is relative to the current clock, the power rails step coarsely, and CPU and GPU memory share one pool so you must never blindly add them.

## What it is
On an integrated SoC (CPU and GPU share one memory and one controller — see [[../jetson-orin-thor-metrics/notes/00-platforms|the platforms note]]) the relevant counters are:

- **`tegrastats` fields** — a periodic line reporting GPU-busy (GR3D %), the memory-controller index (EMC %), power rails, and temperatures.
- **`nvidia-smi` utilization.gpu** — a GPU-busy percentage.
- **power rails** — per-rail power draw (CPU rail, GPU/SoC rail, system input), in coarse steps.
- **MemAvailable** — board-wide free memory, from `/proc/meminfo`.
- **cgroup `memory.current`** — a container's charged memory.
- **GPU allocations (nvmap)** — memory the GPU allocated, on a unified-memory board.

## How it works
**GPU-busy is time, not occupancy.** Both `tegrastats` GR3D % and `nvidia-smi` utilization.gpu report the **fraction of sample time during which at least one kernel was running** — not how many of the GPU's SMs or warps were used (see [[../nvidia-gpu-anatomy/notes/08-measuring-a-gpu|the sibling measuring-a-GPU note]]). A kernel using one SM of twenty reads as "busy" exactly like one using all twenty. On some boards the `nvidia-smi` number also reads systematically below the true kernel-busy fraction, so it needs calibration against a kernel-time trace before it can be trusted as a fraction. Treat GPU-busy as a coarse duty indicator, not a utilisation.

**EMC % is relative to the current clock.** The memory-controller field is an **integer index relative to the current memory clock**, not an absolute bandwidth. If the memory clock is not locked, a change in EMC % can mean the clock moved, not that traffic changed. Without calibrating against a known bandwidth you cannot convert EMC % to GB/s.

**Power rails step coarsely.** The rails are reported in coarse steps (a fraction of a watt), and on some dev boards the GPU and SoC share one rail, so GPU power cannot be separated from SoC power. Small differences are within the step size and mean nothing.

**Memory must not be summed blindly.** On a unified-memory board, `memory.current` (a cgroup's charged memory, including page cache) and GPU allocations (nvmap) can overlap or be charged differently, and some GPU buffers are not charged to the cgroup at all. Adding a cgroup figure and an nvmap figure can double-count shared buffers or miss uncharged ones. **Report them separately**, and use board-wide MemAvailable as the one honest total, remembering it falls with both CPU and GPU allocations because they share the pool.

## How it is measured or used in a benchmark
- **Lock the clocks.** Lock GPU and memory clocks so GPU-busy and EMC % are comparable across runs; verify the lock at the window's start and end (see [[C4-windows-gates-and-validity]]).
- **Calibrate GPU-busy.** Cross-check the GPU-busy counter against a kernel-time trace (the union of kernel intervals, see [[B4-profilers-and-the-observer-effect]]) before treating it as a fraction.
- **Do not convert EMC % to bandwidth without calibration.** Report it as a relative index, or calibrate against a known-bandwidth probe.
- **Report cgroup memory and GPU (nvmap) memory separately.** Use MemAvailable as the board-wide total.
- **Report power per rail, honouring the step size and shared rails.** Do not attribute sub-step differences.

## Common confusions
- **"GPU-busy is utilisation."** It is a time-busy fraction; a kernel on one SM reads the same as a kernel on all of them. Occupancy needs the kernel profiler (see [[../nvidia-gpu-anatomy/notes/08-measuring-a-gpu|the sibling note]]).
- **"EMC % is bandwidth."** It is an integer index relative to the current memory clock; it needs a locked clock and calibration.
- **"Add cgroup and GPU memory for the footprint."** They can overlap or miss buffers on unified memory; report separately and use MemAvailable.
- **"The GPU rail is the GPU's power."** On some boards the GPU and SoC share one rail, and steps are coarse.

## Why it matters for robotics workloads
Every one of these counters is tempting to read as a clean number and wrong to do so. A benchmark that reports "GPU 40% busy" as "40% utilised", or sums cgroup and GPU memory into a footprint, or reads EMC % as bandwidth, will draw confident conclusions from noise. On a shared integrated board, where CPU and GPU compete for one memory controller (the sibling kit's whole thesis), getting these metrics' meanings right is the difference between a real result and a plausible-looking fiction.

## Terms introduced
- **GR3D % / utilization.gpu** — GPU-busy: the fraction of sample time a kernel was running, not occupancy.
- **EMC %** — the memory-controller index in `tegrastats`, an integer relative to the current memory clock, not absolute bandwidth.
- **power rail** — a measured power supply line (CPU rail, GPU/SoC rail, system input), reported in coarse steps.
- **MemAvailable** — board-wide free memory from `/proc/meminfo`; the honest total on a shared-memory board.
- **`memory.current`** — a cgroup's charged memory, including page cache.
- **nvmap** — the GPU memory allocator; its allocations are not simply additive with cgroup memory on unified memory.
- **unified memory** — one physical memory shared by CPU and GPU; also in [[../nvidia-gpu-anatomy/glossary|the sibling glossary]].
- **clock lock** — fixing GPU and memory clocks so the busy and EMC counters are comparable across runs.
