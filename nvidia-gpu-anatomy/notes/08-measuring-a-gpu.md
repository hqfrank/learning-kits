# 08 — Measuring a GPU

**Sources:** CUDA Programming Guide §3.2.1 (A-HW, PTX); metrics-kit `A2`, `A3`, `A6`, `B3`, `B8`, `L4`, Table 1 (C-PLAT) and `constants.json`. See [[../SOURCES]].

## In one sentence
To predict whether a kernel is fast you compare its arithmetic intensity (operations per byte moved) against the roofline — a plot bounded by a flat compute roof and a sloped bandwidth roof — then measure against a locked-clock solo baseline and report the p99 tail, because a datasheet TOPS figure says almost nothing about delivered performance.

## What it is
The vocabulary of GPU measurement:

- **Arithmetic intensity** — operations per byte moved (FLOPs per byte). Low intensity means memory-bound; high means compute-bound (C-KIT-NOTES A2 glossary).
- **Roofline** — a plot of achievable rate vs arithmetic intensity, capped by horizontal compute roofs and sloped memory roofs; the two meet at the **ridge** (C-KIT-NOTES A5/C1 glossary).
- **Bytes vs FLOPs** — a kernel's two demands: how much arithmetic it does and how much data it moves. The ratio places it on the roofline.
- **TOPS vs achievable** — the datasheet peak vs what a tuned (let alone portable) kernel reaches; the gap is large ([[04-cuda-cores-vs-tensor-cores]]).
- **Solo baseline** — the kernel's time running alone, the reference for any co-tenancy slowdown (C-KIT-NOTES B2/B4).
- **p99** — the 99th-percentile latency, the tail metric for deadline-bound work (C-KIT-NOTES B8 glossary).
- **Locked clocks / MAXN** — fixing the GPU clock (NVIDIA's maximum-clock regime on Jetson) so a measurement is not confounded by frequency scaling (C-PLAT glossary).
- **SASS / PTX** — PTX is the virtual instruction set CUDA compiles to; SASS is the native assembly the hardware runs. Checking SASS confirms the compiler emitted the instruction you meant (A-HW §3.2.1; C-KIT-NOTES A1/A2).
- **ncu (Nsight Compute)** — the kernel profiler that reports stall counters and achieved occupancy (C-KIT-NOTES B3 glossary).

## How it works
Place the kernel on the roofline. If its arithmetic intensity is left of the ridge it is memory-bound: its ceiling is bandwidth × intensity, and faster tensor cores will not help ([[06-caches-and-working-sets]]). If right of the ridge it is compute-bound: its ceiling is the compute roof. The metrics kit builds the roofline from measured ceilings, not datasheet ones — CUDA-core and tensor-core compute roofs (C-KIT-NOTES A2/A3) and the L2-resident and DRAM bandwidth roofs (C-KIT-NOTES A6) — because the measured values differ from the datasheet by large factors.

Then guard the measurement. Lock the clock (MAXN, devfreq-verified) so runs are comparable (C-PLAT). Take a solo baseline as the minimum over several trials (C-KIT-NOTES A6/B2). Check SASS so a result is not a codegen artifact — the kit's FP16 and dp4a probes pass a SASS gate for exactly this reason (C-KIT-NOTES A2). Read the profiler's **stall decomposition**, not just occupancy, because occupancy does not predict issue rate ([[03-occupancy-and-registers]], C-KIT-NOTES B3). For anything with a deadline, report **p99**, not the mean or median — a bimodal latency makes the median uninformative (C-KIT-NOTES B8).

## On Orin and Thor (numbers from constants.json)
Why the datasheet misleads, in numbers from `constants.json`:

- **Tensor peak vs achievable:** tcgen05 INT8 reaches 324.5 TOP/s, 63% of the 517 datasheet; the portable classic path reaches 128.8 (`tensor_tcgen05_int8`, `tensor_classic_int8`, C-KIT-NOTES A3). NVFP4 dense is 627.8 TFLOP/s, 60.7% of 1035 (`nvfp4_dense_ceiling`, C-KIT-NOTES A4).
- **Memory roofs:** DRAM read 177 (Orin) / 259 (Thor) GB/s; L2-resident 2200 / 3790 GB/s — a 12.4× / 14.6× gap that the roofline must show (`dram_bandwidth_read_measured`, `l2_resident_read_bandwidth`, `l2_dram_bandwidth_ratio`, C-KIT-NOTES A6).
- **Occupancy ≠ speed:** three kernels at 62–74% occupancy differ 4.24× (Orin) in runtime (C-KIT-NOTES B3).
- **The number that actually governs a robot:** at ≈172 GB/s CPU memory load the control loop collapses regardless of precision or cap (`cpu_memory_load_floor`, C-KIT-NOTES L4) — a p99 story no TOPS figure predicts.

## Common confusions
- **TOPS is a ceiling you rarely touch.** Real workloads sit 2–3 orders of magnitude below the advertised tensor numbers once memory and scheduling bind (C-KIT-NOTES L4).
- **Mean latency hides the tail.** Deadline work needs p99; a loop can have a fine mean and still drop ticks (C-KIT-NOTES B8).
- **Occupancy is not a performance metric.** It is an opportunity metric; read stalls (C-KIT-NOTES B3; [[03-occupancy-and-registers]]).
- **Unlocked clocks confound everything.** Without MAXN and a devfreq check, a "speedup" may be a clock change (C-PLAT).
- **PTX is not what runs.** The hardware runs SASS; always confirm the SASS for a microbenchmark (A-HW §3.2.1; C-KIT-NOTES A2).

## Why it matters for robotics workloads
A robot's question is never "how many TOPS" — it is "does the 100 Hz loop hold while perception and the policy run." That is a p99-under-contention question, answered by placing each kernel on a measured roofline, taking a locked-clock solo baseline, and measuring the tail under the real co-tenant mix ([[07-sharing-the-gpu]], C-KIT-NOTES B8/L4). The metrics kit's whole method — measure ceilings, then measure how contention erodes them — is the template: datasheet numbers set expectations, measured rooflines set reality, and p99 sets whether the robot works.

## Terms introduced
- **arithmetic intensity** — operations per byte moved; the roofline x-axis. Reused from `../jetson-orin-thor-metrics/glossary.md` (C-KIT-NOTES A2).
- **roofline** — achievable rate vs arithmetic intensity, bounded by compute and bandwidth roofs. Reused from the metrics-kit glossary (C-KIT-NOTES A5).
- **ridge** — the intensity where the compute and bandwidth roofs cross. Reused from the metrics-kit glossary (C-KIT-NOTES C1).
- **solo baseline** — a kernel's alone-time reference for slowdown. Related to the metrics-kit **slowdown (S)** (C-KIT-NOTES B1).
- **p99** — the 99th-percentile latency; the deadline tail metric. Reused from the metrics-kit glossary (C-KIT-NOTES B8).
- **MAXN / locked clocks** — the maximum-clock regime with GPU frequency fixed. Reused from the metrics-kit glossary (C-PLAT).
- **SASS / PTX** — native GPU assembly / the virtual ISA CUDA compiles to. Reused from the metrics-kit glossary (A-HW §3.2.1; C-KIT-NOTES A1).
- **ncu (Nsight Compute)** — the kernel profiler reporting stalls and occupancy. Reused from the metrics-kit glossary (C-KIT-NOTES B3).
- **TOPS / TFLOP/s** — trillion operations / floating-point operations per second; datasheet peaks. Reused from the metrics-kit glossary (C-KIT-NOTES A2).
