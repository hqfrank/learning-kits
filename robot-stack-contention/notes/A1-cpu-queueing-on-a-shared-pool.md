# A1 — CPU queueing on a shared core pool

**Source:** Linux scheduler statistics (`/proc/<tid>/schedstat`, `/proc/schedstat`) as taught in [B0 — CPU metrics](../../robot-workload-benchmarking/notes/B0-cpu-metrics.md); cgroup v2 CPU sharing (https://docs.kernel.org/admin-guide/cgroup-v2.html); numbers from [`constants.json`](../constants.json) by key · **Status:** teaching note; every measured value is illustrative.

## In one sentence
In the full stack the shared pool's threads wait longer for a CPU than they run, and that run-queue wait is the largest single added term in the object detector's frame, so most of the detector's alone → full stack slowdown is CPU, not GPU.

## What it measures
**Run-queue wait** is time a thread is runnable but not running, because every core it may use is busy. Linux reports it per thread and per CPU in `/proc/<tid>/schedstat` and `/proc/schedstat`. [B0 — CPU metrics](../../robot-workload-benchmarking/notes/B0-cpu-metrics.md) defines the counter; this note uses it.

The investigation normalises the wait as **wait per busy second**: seconds of summed run-queue wait per second of CPU time that the same threads ran. A value of 1 means that the threads wait as long as they run. This normalisation lets windows with different loads be compared.

**Caution:** summed wait over a service's threads is not added latency when the threads run in parallel. Only the wait of a one-thread worker adds directly to its output.

## How
The board has 12 cores (illustrative, `board_cores`), split in two:

- **The pool** — 8 cores (illustrative, `pool_cores`), shared by most services. The Completely Fair Scheduler (CFS) shares them between all runnable threads.
- **The reserved cores** — 4 cores (illustrative, `reserved_cores`), removed from the general scheduler with the `isolcpus` kernel parameter. Services are pinned there by their container cpuset.

An inventory script reads schedstat in every existing window. Per CPU it gives busy cores and summed wait. Per thread it gives run time, wait, and the core where the thread last ran. Attribution to a core is exact on the reserved cores and approximate on the pool, because pool threads migrate.

Analogy: a supermarket with eight tills and one queue. When the tills are mostly busy with bursty customers, the time in the queue can exceed the time at the till.

## Predicted
Hypothesis X1: services on the pool queue for a CPU, and the wait adds to each frame and message. If X1 holds, wait is a large measured term in each pool service's added time.

## Measured
Each value below is an illustrative measurement.

**Board level:**

| Quantity | Value (illustrative) | Key |
|---|---|---|
| Pool busy, full stack | a fraction of 0.8 | `pool_busy_frac_full` |
| Pool wait per busy second, full stack | 2.0 s | `pool_wait_per_busy_full` |
| Pool wait per busy second, camera-only row | 0.05 s | `pool_wait_per_busy_camera_only` |

**A saturated reserved core gives equal shares.** In the full stack one reserved core is fully busy. Three groups share it: the interaction service, a controller service, and our measurement probe. Each group gets about 0.33 cores (illustrative, `saturated_core_equal_share`). No service has a CPU quota. Equal shares on a saturated core are what CFS gives groups that all want more: **these are caps, not demands.** When the probe moved off that core, the interaction service used more than its full-stack share. See [[A5-where-to-put-the-observers]].

**Per-frame decomposition, the object detector.** The detector logs every frame. The inventory script splits the frame into worker run time, worker wait, and blocked time (the rest).

| Term | Value (illustrative) | Key |
|---|---|---|
| Frame time, alone → full stack | 100 → 200 ms | `detector_frame_ms_solo_full` |
| Added run-queue wait / run / blocked, alone → full stack | +50 / +30 / +20 ms per frame | `detector_added_wait_run_blocked` |

Wait is about half of the added frame time (my estimate from `detector_added_wait_run_blocked`: 50 ÷ (50 + 30 + 20) = 0.5). The added run time is "the same work running slower", see [[A2-same-work-more-cycles]]. CPU frequency is ruled out, because all cores are locked.

## The gap, and what it means
X1 is supported for the full stack. The test that could have failed is the decomposition: if the detector's added time had been mostly blocked time, X1 would be weak. It is mostly wait and run. The voice chain gives a second check: the dialogue engine's per-item cost rises by about the factor that time-share times slower work predicts (see [[A4-costs-that-grow-with-history]]).

**Correction kept visible.** Step 1 first said that the pool changes from the full stack to the full stack + VLA were "within round-to-round spread". That statement was withdrawn. One full stack + VLA round had no speech in its window, so it was not a CPU-side replicate. With voice on in both conditions, pool wait rises from the full stack to the full stack + VLA. The GPU step is still the larger change there (see [[B1-gpu-time-slicing-and-the-dose-curve]]).

**Caveat on every full-stack rate.** Probe rates in the full stack are lower bounds. The probe's own heartbeat loses a few percent of its rate in the full stack, so a rate loss of that size is not evidence.

## So what
On a small robot computer, a pool that is "only" four fifths busy can still triple a single thread's wall time per unit of CPU work (interpretation; my estimate from `pool_wait_per_busy_full`: 1 s of run plus 2.0 s of wait gives about 3 s of wall time per CPU second). Read run-queue wait, not busy percentage, to see CPU contention.

## Terms introduced
- **pool** — the shared general-purpose CPU cores (`pool_cores`), shared by most services under CFS.
- **reserved cores** — cores removed from the general scheduler (`isolcpus`) and assigned to services by cpuset (`reserved_cores`).
- **run-queue wait** — time a runnable thread waits for a CPU. Reused from `../robot-workload-benchmarking/glossary.md`.
- **wait per busy second** — summed run-queue wait divided by the summed run time of the same threads; 1 means they wait as long as they run.
- **timeslice** — one continuous run of a thread on a CPU between two scheduler switches.
- **CFS share** — the fraction of a contended CPU that the Completely Fair Scheduler gives each runnable group; on a saturated core it is a cap, not a demand.
- **saturated core** — a core that is 100 % busy, so any added demand turns into wait.
