# C3 — Calibration: making the topic have something to find

**Source:** the demonstration topic's worklog ("Calibration", round 1) and seed lessons; all numbers from the demonstration run of the local scheduling simulator (`sched_*` keys; illustrative, not a real platform). · **Status:** evaluator v0.1 frozen; round 1 complete in the source.

## In one sentence
Calibration is the step where the owner makes the baseline pass and the controls fail, and also makes the problem hard enough to be worth a campaign — the first workload had a trivial answer, so it was made denser until placement under contention became the only lever.

## What it is
**Calibration** has two goals. The first is the standard one: the baseline is ACCEPTED on every input set with a margin clearly below 1, and every control is REJECTED ([[B3-negative-controls]]). The second is specific to a demonstration: the problem must have something for a campaign to find. A problem whose obvious policy already reaches the work floor teaches nothing.

## How it works
**The first workload had nothing to find.** On the original visible workload the FIFO baseline passed at an illustrative `sched_cal1_fifo_ms` = 29.2 ms (binding `sched_cal1_fifo_binding` = 0.66), but a simple EDF-with-GPU-first policy reached `sched_cal1_edf_ms` = 16.6 ms against a `sched_cal1_floor_ms` = 15.5 ms **work floor** — the shortest possible time given the job graph. With the CPU at `sched_cal1_util` 24 % and the GPU at 42 %, there was slack everywhere and nothing left for a campaign to discover.

The **work floor** is the key idea. It is the end-to-end time if every job starts the instant its inputs are ready, on its fastest option, with no queueing. No scheduler can beat it. If the baseline is already near the floor, the campaign's ceiling for improvement is tiny.

**Densifying the workload.** The owner made the problem harder, on purpose and documented:

- added a parallel segmenter to the perception chain and a new depth-mapping chain;
- made several jobs heavier;
- set the control deadline to `sched_control_deadline_ms` = 20 ms (illustrative).

Now, with every accelerator-optional job placed on its fastest option, the GPU runs at `sched_baseline_gpu_util` = 91 % while the DLA idles at `sched_baseline_dla_util` = 0 % and the CPUs sit at `sched_baseline_cpu_util` = 33 %. The lever becomes clear: move work off the saturated GPU onto the idle DLA and the idle CPUs.

**Baseline placement choice.** The first baseline placed jobs alphabetically, which put every accelerator job on the DLA and failed the new workload outright (perception at an illustrative `sched_alphabetical_perception_ms` = 626 ms). The owner changed the baseline to shortest-execution placement — the default an engineer ships first. A baseline should be the obvious first thing, not a strawman and not already clever.

**The calibration result (frozen v0.1; all values illustrative).** The baseline is ACCEPTED at `sched_baseline` 34.7 ms (range 32.3–45.4), binding 0.49 on the visible set. EDF with the same placement gives `sched_edf_gpu_first` 34.5 ms (range 31.6–41.6): the ranges overlap, so it is not promotable. A diagnostic probe found least-laxity at `sched_probe_least_laxity_ms` = 34.2 ms and CPU-first placement within the baseline's range. The reading, recorded in the seed lessons: **dispatch order alone does not move the metric under this placement; the open lever is load-aware placement across GPU, DLA and CPU.** The `wallclock` control was REJECTED at `sched_control_wallclock_ms` = 53.5 ms by the order probe.

**"GPU-greedy loses when a long job blocks the GPU."** The owner's probe tool ran four textbook policies on every workload during the first calibration. On held-out b, GPU-greedy placement *lost* to CPU placement (`sched_cal1_heldout_b`: 37 ms vs 29 ms, diagnostic), because a long grasp-planner job occupied the single non-preemptive GPU and every perception job queued behind it. The lesson transfers: on non-preemptive units, the fastest unit is the wrong choice when it is busy with a long job.

**The first round's result.** The first automated round confirmed the reading.

| Candidate | Median (range), ms, illustrative | Binding, illustrative | Outcome |
|---|---|---:|---|
| baseline (paired) | 34.7 (32.3–45.4) | 0.49 | champion before the round |
| earliest-finish placement | 27.8 (23.7–34.2) | 0.43 | accepted; range overlaps the baseline's |
| earliest-finish placement + perception-first dispatch | 25.8 (23.7–30.7) | 0.47 | **promoted** |
| baseline placement + GPU reservation for perception | 30.0 (27.9–31.2) | 0.81 | accepted; not promotable |
| earliest-finish placement + reservation | 23.9 (23.7–24.1) | 0.78 | accepted; not promotable |

(Values from `sched_baseline`, `sched_r1_eft_placement`, `sched_r1_eft_metric_first`, `sched_r1_metric_reserve`, `sched_r1_eft_reserve`; illustrative.) Earliest-finish placement moved the GPU from 91 % to `sched_r1_gpu_util` = 65 % and the DLA from 0 % to `sched_r1_dla_util` = 42 %. Placement alone cut the median by 6.9 ms (my arithmetic, 34.7 − 27.8). Perception-first dispatch helped only once placement had given the GPU headroom; under baseline placement it had done nothing.

**The rule meets the floor.** The last row has a better median (23.9 vs 25.8 ms) and a far better worst seed (24.1 vs 30.7 ms) than the champion (illustrative, keys above). It still cannot be promoted. The disjoint-range rule needs its worst seed below the champion's best seed, and the champion's best seed (23.7 ms) already sits near the `sched_work_floor_ms` = 22.5 ms floor plus execution jitter. No candidate can get below it. The researcher raised this as a decision for the owner: promote by median and maximum together, or by a paired per-seed comparison. The coordinator recorded it and did not change the rule ([[B8-reporting]]). Its binding ratio, 0.78, came from another chain on held-out b losing margin — the price of giving perception priority.

## How it is used in a campaign
Calibration ends the "calibrate" phase of the roadmap ([[C2-the-scheduling-topic]]). Its facts are written into the seed lessons as the slow memory the first planner inherits ([[B6-the-two-memories]]): the measurement rules, what the platform looks like, and the open directions marked "no evidence yet".

## Common confusions
- **"A passing baseline means the topic is ready."** It means the gate is calibrated. A topic is ready to run only if there is headroom above the work floor for a campaign to find.
- **"Make the baseline weak so gains look big."** A strawman baseline produces fake gains. The baseline is the obvious default; the gains are over that.
- **"The campaign found the answer."** Calibration found the lever (placement); the campaign quantified it and found where it costs other chains their margin.

## Why it matters
A campaign on a trivial problem produces a confident, meaningless leaderboard. Calibration is where the owner earns the right to run a campaign: the gate is honest, the baseline is fair, and the problem has an answer worth the agents' time.

## Terms introduced
- **calibration** — tuning the gate so the baseline passes and controls fail, and shaping the problem so a campaign has something to find.
- **work floor** — the shortest possible end-to-end time given the job graph; no scheduler beats it.
- **densifying the workload** — adding load so the obvious policy no longer reaches the floor.
- **load-aware placement** — choosing a job's resource from the current backlog, not a fixed rule.
