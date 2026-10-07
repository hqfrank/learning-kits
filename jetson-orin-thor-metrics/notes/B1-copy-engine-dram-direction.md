# B.1 Copy/exec-engine and DRAM-direction interference

**Source:** book.pdf §B.1 — `doc-b-proxy-workload/ce-interference.tex`; Table B.1.1 (predicted vs measured slowdown)  ·  **Status in source:** D (drafted, awaiting review)

## In one sentence
Copy-engine traffic does not slow a cache-resident compute kernel at all on Orin or Thor (S = 1.00–1.02), refuting the 3–8× hazard Olmedo found on older Tegra parts; a streaming victim slows 1.53× when the aggressor streams in the same direction and 1.03× when opposed, and the one exception is the engine `memset` blit path, which slows readers 1.89–2.43× on Orin and 2.33–4.01× on Thor.

## What it measures
The victim slowdown S_v|a: the victim kernel's wall time with memory aggressor a co-running, divided by its solo wall time. S = 1 means the aggressor is free; S = 2 means the victim runs twice as slowly. It is read for two victims: a compute-bound victim (the leg that replicates or refutes Olmedo's 3–8× copy-on-compute hazard) and a memory-bound victim (which exposes direction and controller-contention effects). The section also extends Olmedo along two axes: transfer direction (do the controller's read and write queues decouple?) and the CPU↔GPU quality-of-service split under joint saturation (§B.1 "Objective and metric").

## How
Caveat first: clock-locking is load-bearing. An unlocked clock would let the aggressor raise the shared SoC clock and produce a spurious victim speedup that masks contention (§B.1 "Experiment setup").

Victims (both on the SMs): a compute victim (cache-resident arithmetic chain) and a memory victim (streaming reader with footprint 4× L2). Aggressors, all contending for the shared controller from different engines: four GPU-side — copy-engine H2D, D2H and D2D transfers plus an asynchronous engine `memset` (the blit path) — and one CPU-side single-thread memory copy. Three sub-experiments: (i) each victim against each aggressor at 16, 64 and 256 MB; (ii) direction — a streaming read or write victim against a reading, writing or setting aggressor at 64 and 512 MB; (iii) saturation — 1–8 CPU bandwidth-hog threads against a GPU streaming kernel over ≥ 250 ms, reporting each side's retained bandwidth. Solo baseline is the minimum over 5 trials.

## Predicted
- **Compute victim: S ≈ 1 (immune).** A cache-resident kernel keeps its working set on-chip, disjoint from the DRAM the aggressor drives, so there is nothing to contend for. This is predicted despite Olmedo's 3–8× on TX2, Xavier and Pegasus — the discriminator.
- **Streaming victim — direction.** The controller has separate read and write queues and LPDDR is effectively half-duplex, so opposed streams decouple (S ≈ 1.0) while same-direction pairs share one queue and contend (S ≈ 1.5). A pure-write aggressor (engine `memset`) against a read victim is opposed, so S ≈ 1.0 is predicted for it too.

(§B.1 "Prediction model".)

## Measured
S_v|a = median(t_v|a) / min₅(t_v,solo). QoS retention η = median(B_co / B_solo) per side.

| Victim | Aggressor | Predicted | Orin | Thor |
|---|---|---|---|---|
| compute (cache-resident) | all (copy / memset / CPU) | ≈ 1 | 1.00–1.02 | 1.00–1.01 |
| memory-bound | copy engines | 1.0–1.5 | 1.07–1.14 | 1.58–1.69 |
| memory-bound | engine memset (16 → 256 MB) | 1.0 (opposed) | 1.89 → 2.43 | 2.33 → 4.01 |
| memory-bound | CPU copy (1 thread) | ≈ 1 (low BW) | 1.00 | 1.11–1.18 |
| stream-read | same-direction read | 1.5 | 1.53 | 1.53 |
| stream-read | opposed (write/set) | 1.0 | 1.03 | 1.03 |
| stream-write | same-direction write | 1.5 | 1.38 | 1.47 |

(§B.1 Table B.1.1.) The retained-bandwidth fractions from sub-experiment (iii) are not tabulated in §B.1; §B.6 Table B.6.1 carries them as η_cpu = 0.76–0.81 (Orin) / 0.45–0.58 (Thor) under a heavy CPU hog, cited to [M].

## The gap, and what it means
**The compute hazard is refuted.** On Orin and Thor a compute-bound tenant runs effectively free of concurrent copy traffic. Olmedo's 3–8× was a property of the earlier Tegra SoCs, not of integrated GPUs in general.

**The separate-queue direction model holds.** Interference is governed by transfer direction, not aggressor magnitude: same-direction streams serialize on one queue, opposed streams run nearly free. The read/write rows track the prediction to two decimals on both boards.

**The engine memset is the one model violation.** The queue model predicts a pure-write aggressor is free against a read victim, yet `memset` slows it severalfold and worsens with size, because the blit path bypasses the queue arbitration the model assumes. The violation is larger on Thor, consistent with Thor's softer QoS split: under a saturating CPU hog the GPU yields more of its bandwidth than on Orin. Thor's larger absolute bandwidth buys throughput, not isolation (§B.1 "Comparison and discussion").

## So what
The source says the retained-bandwidth fractions set the contended edge of the roofline's memory band. Interpretation (mine): in a robot pipeline, schedule frame-in (H2D) and result-out (D2H) copies so they oppose the dominant kernel direction, and avoid asynchronous `cudaMemsetAsync` on large buffers while a memory-bound kernel runs.

## Terms introduced
- **copy engine (CE)** — the GPU's dedicated DMA unit, separate from the SMs; moves H2D, D2H and D2D transfers.
- **slowdown (S_v|a)** — victim wall time with aggressor a co-running over its solo wall time.
- **victim / aggressor** — the kernel whose slowdown is measured / the co-runner that may cause it.
- **H2D / D2H / D2D** — host-to-device, device-to-host, device-to-device transfer directions.
- **blit path** — the engine `memset` route, which bypasses the controller's queue arbitration.
- **half-duplex (LPDDR)** — the memory bus carries reads or writes at a time, not both; opposed streams use separate controller queues.
- **QoS retention (η)** — a side's co-run bandwidth over its solo bandwidth under joint saturation.
- **bandwidth hog** — a CPU program that streams memory as fast as it can, to saturate the shared controller.
