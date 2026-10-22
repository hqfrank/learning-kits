# B4 — Profilers and the observer effect

**Source:** NVIDIA Nsight Systems (https://docs.nvidia.com/nsight-systems/), NVIDIA Nsight Compute (https://docs.nvidia.com/nsight-compute/), `tegrastats` (https://docs.nvidia.com/jetson/). Kernel-level detail in [[../nvidia-gpu-anatomy/notes/08-measuring-a-gpu|the sibling measuring-a-GPU note]]. · **Status:** concept primer, illustrative numbers only.

## In one sentence
Profilers tell you what a GPU workload is actually doing — a timeline of kernels and API calls, or per-kernel hardware counters — but the act of profiling perturbs the system under test, so the rule is to take the headline timing numbers from unperturbed windows and use the profiler only in separate trace-only windows, never beside the control loop.

## What it is
Three tools, at three levels of detail and intrusion:

- **`tegrastats`** — the cheapest: a periodic one-line summary of GPU-busy, memory-controller index, power, and temperature (see [[B1-gpu-power-memory-metrics]]). Low intrusion, coarse detail.
- **Nsight Systems** — a system-level **timeline**: when each CUDA kernel ran, when each API call was made, how the CPU and GPU lanes line up. It reveals launch gaps and which service held the GPU. Medium intrusion.
- **Nsight Compute** — a per-kernel **counter** profiler: occupancy, stalls, cache hit rates, memory sectors for a chosen kernel. It identifies what a kernel is bound by (see [[../jetson-orin-thor-metrics/notes/B3-matrix-profile-stall-decomposition|the sibling stall-decomposition note]]). High intrusion: it serialises and replays kernels.

## How it works
**What each answers.** `tegrastats` answers "how busy, roughly?" Nsight Systems answers "what ran when, and where are the gaps?" — it is how you see that a small-model service is **launch-bound** (the GPU idles between tiny kernels while the CPU prepares the next one). Nsight Compute answers "why is this kernel slow?" — compute-bound, memory-bound, or latency-bound (the bound class).

**Why tracing perturbs the system under test.** A timeline trace intercepts every CUDA API call and kernel launch, adding overhead to each. For a service that launches many small kernels, this overhead inflates its latency measurably (an illustrative order of several milliseconds added per inference) and can drop its rate. The counter profiler is worse: it serialises kernels and replays them, stretching kernel times and stalling the service's downstream topics entirely. A number measured while the profiler is attached is not the number the service has when it runs for real.

**The consequence: separate trace-only windows.** Because tracing changes timing, the benchmark takes its headline KPIs (rates, latencies, deadline misses) from **untraced** windows, and runs the profiler in **separate, short, trace-only windows** that are explicitly labelled "mechanism only, not a KPI." The two serve different purposes: the untraced window says *how fast*, the traced window says *why*. From the trace you take structure — kernel counts, launch gaps, the union of kernel intervals as a calibrated GPU-busy, the bound class — and from the untraced window you take the times.

**Profiler safety.** The counter profiler needs elevated privileges (a more-privileged container). The rules: grant the minimum privilege, never run it fully privileged, log every privileged launch, bound its runtime with a hard timeout (it does not stop a running server by itself), and **never run it next to the control loop** — a serialising, root-privileged tool beside a hard-real-time loop is a safety risk, and the control policy runs on the CPU anyway (see [[A4-locomotion-and-whole-body-control]]).

## How it is measured or used in a benchmark
- **Use the cheapest tool that answers the question.** `tegrastats` for duty and power, Nsight Systems for structure, Nsight Compute only for a chosen heavy kernel.
- **Keep KPIs out of traced windows.** Report rates and latencies from untraced windows; label trace outputs "mechanism only."
- **Calibrate GPU-busy from the timeline.** The union of kernel intervals is a true GPU-busy fraction to check the coarse counter against (see [[B1-gpu-power-memory-metrics]]).
- **Profile safely.** Minimum privilege, logged, time-bounded, never beside the control loop, perception services first.
- **Take times from nsys, structure from ncu.** The counter profiler stretches kernel times, so use it for bytes and bound class, not wall-clock times.

## Common confusions
- **"A profiled run gives the real latency."** Tracing adds overhead and can inflate latency by milliseconds; take latency from untraced windows.
- **"The counter profiler's kernel times are the kernel times."** It stretches them by replaying; take times from the timeline, structure from the counters.
- **"More tracing is better."** Heavier API coverage perturbs more; use the lightest trace that shows the mechanism.
- **"Profiling is harmless."** It needs elevated privilege and serialises work; never run it beside the control loop.

## Why it matters for robotics workloads
Profilers are how you move from "the CPU is the limit" to "*this* kernel, launched this many times, with these gaps, is why." But they change the thing they measure. A benchmark that reports a traced latency as the service's latency has recorded the profiler, not the robot. Keeping timing in untraced windows and mechanism in separate trace-only windows — and keeping the profiler far from the control loop — is what lets you have both the number and the explanation without corrupting either.

## Terms introduced
- **`tegrastats`** — the cheap periodic summary of GPU-busy, memory index, power, temperature.
- **Nsight Systems** — the system-level timeline of kernels and API calls; reveals launch gaps and GPU ownership.
- **Nsight Compute** — the per-kernel counter profiler; identifies a kernel's bound class. Also in [[../nvidia-gpu-anatomy/glossary|the sibling glossary]] (ncu).
- **observer effect (here)** — the perturbation a profiler adds to the system under test.
- **launch-bound** — a workload whose GPU idles between small kernels waiting for the CPU to launch the next.
- **bound class** — whether a kernel is compute-, memory-, or latency-bound.
- **trace-only window** — a separate, labelled window run with the profiler attached, used for mechanism not KPIs.
- **union of kernel intervals** — a true GPU-busy fraction computed from the timeline, used to calibrate the coarse counter.
- **profiler safety** — minimum privilege, logged, time-bounded, and never beside the control loop.
