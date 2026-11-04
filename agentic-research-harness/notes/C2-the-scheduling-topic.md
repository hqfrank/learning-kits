# C2 — The scheduling topic

**Source:** the demonstration topic's README (§1–§7), `topic.json`, AGENTS.md; numbers from the demonstration run of the local scheduling simulator (`sched_*`, `topic_*` keys; illustrative, not a real platform). Public background: Liu & Layland 1973; Mok 1983; Jeffay, Stanat & Martel 1991; Topcuoglu, Hariri & Wu 2002; Banks, Carson, Nelson & Nicol, *Discrete-Event System Simulation*. · **Status:** evaluator v0.1 frozen and calibrated in the source; one automated round run.

## In one sentence
The worked example asks how a robot computer with CPU cores, a GPU and a DLA should place and order its periodic processing jobs to cut the perception chain's tail latency while every chain keeps its deadline, judged by a simulator that is simple on purpose and says what it leaves out.

## What it is
**The question.** A robot runs periodic processing **chains**: control, perception, localization, planning, depth mapping, logging, telemetry. Each chain is a small directed acyclic graph (DAG) of **jobs**. The platform has heterogeneous **resources**: CPU cores, one GPU and one DLA (a deep-learning accelerator, a fixed-function inference engine). The scheduler makes two decisions:

- **placement** — for each ready job, which resource type it runs on;
- **dispatch** — for each free unit, which ready job runs next.

Units are **non-preemptive**: a started job runs to the end. GPU kernels and most accelerator jobs behave this way in practice.

**The simulated platform (visible workload).** `sched_cpu_cores` = 4 CPU cores, one GPU, one DLA, `sched_chains` = 7 chains. The metric chain is perception at `sched_perception_rate_hz` = 30 Hz: capture (CPU) → preprocess (CPU or GPU) → detector and segmenter in parallel (each GPU or DLA) → tracker (CPU). The per-option execution times are in `sched_node_ms`; for example the detector takes 10 ms on the GPU and 18 ms on the DLA. The control chain has a period of `sched_control_period_ms` = 10 ms and a deadline of `sched_control_deadline_ms` = 20 ms. (All illustrative.)

**Metric.** The p95 end-to-end latency (release to last job completion) of the perception chain, per seed, over `topic_visible_seeds` = 20 seeds of `topic_horizon_s` = 5 s each. The record reports the median over seeds and the range; promotion compares the range. Lower is better.

**Gate, per input set** (limits are design parameters, illustrative).
- every chain instance due inside the horizon completes;
- hard chains miss zero deadlines; soft chains miss at most `topic_soft_miss_limit` = 5 %;
- the scheduler's mean decision time is below `topic_decision_time_limit_ms` = 2 ms (host wall clock);
- results are identical when the seeds run in reverse order;
- the scheduler returns only ready jobs and allowed resources.

**Binding ratio.** The largest of: worst end-to-end ÷ deadline (hard chains), p99 end-to-end ÷ deadline and miss ratio ÷ limit (soft chains), decision time ÷ limit. Promotion needs at most `harness_margin_cap_scheduling` = 0.9 (design parameter, illustrative).

**Held-out workloads.** `topic_heldout_sets` = 2 workloads, `topic_heldout_seeds` = 8 seeds each, which agents must not read: (a) a lighter load on 3 cores with perception at 40 Hz (`sched_heldout_a`); (b) a different robot with a two-camera fan-in chain, a `sched_heldout_b_grasp_ms` = 200 ms GPU grasp planner, and no DLA. Agents know this much, not the files. (All illustrative.)

**Baseline and controls.** The baseline dispatches FIFO by ready time and places each job on its shortest-execution option — the obvious default. Three negative controls must be rejected ([[B3-negative-controls]]).

**Candidate API.** A candidate is a `Scheduler` class with `place(job)`, called once when a job becomes ready, and `pick(ready, resource, now_ms)`, called when a unit is free. A job exposes its per-option execution times, absolute deadline, release and ready times, period, hard/soft flag, dependencies, the shortest remaining work after it, and a scratch dict. A scheduler must be deterministic given platform, workload and seed: no wall clock, no unseeded randomness, no state between simulations.

## How it works
The evaluator is a **discrete-event simulation**: the simulator jumps from event to event (release, ready, start, finish) rather than stepping a clock (Banks et al.). It is deterministic, so a paired baseline stays valid for a day on the same host and evaluator id.

**Public background on the policies.** Earliest-deadline-first (EDF) runs the job with the nearest absolute deadline. On one *preemptive* processor with independent periodic tasks and deadline equal to period, EDF meets every deadline whenever total utilization is at most `pub_edf_utilization_bound` = 1 (Liu & Layland 1973). Least-laxity-first runs the job with the least slack (deadline minus now minus remaining work; Mok 1983). Neither guarantee carries over here. The units are non-preemptive, and Jeffay, Stanat & Martel (1991) showed that non-preemptive scheduling of periodic tasks is NP-hard in the strong sense. Placement on heterogeneous resources adds a second decision; HEFT (Topcuoglu et al. 2002) is the classic heuristic, which places each task on the resource that gives the earliest finish time.

## What the model leaves out
The README states the exclusions so that the model's limits are visible:

- preemption and priorities inside a unit;
- memory and bandwidth contention between units;
- data-transfer cost between resource types;
- power and thermal limits;
- scheduler overhead on the platform itself (only measured, as host wall time);
- multi-robot and network effects.

Each is a possible later extension; each extension is a new frozen evaluator version with a re-run baseline and controls. Results transfer to a real platform only as hypotheses to test there. The sibling kit [[../robot-workload-benchmarking/notes/A0-the-big-picture|robot-workload-benchmarking A0]] describes the real stack this model abstracts, and [[../jetson-orin-thor-metrics/notes/L4-scheduling-ladder|the scheduling ladder note]] shows measured GPU-sharing effects that this model leaves out.

## Common confusions
- **"EDF is optimal, so start there."** EDF's optimality is for one preemptive processor. On non-preemptive heterogeneous units it is only a heuristic, and in calibration it did not move the metric ([[C3-calibration]]).
- **"The simulator's numbers are a robot's numbers."** They are illustrative outputs of a deliberately simple model.
- **"Held-out b is just harder."** It is different: another chain shape and a resource missing. A policy that hard-codes the visible chain names, periods or resources fails there.

## Why it matters
The topic shows the method on a problem where everything is local and fast. Every part of the method — frozen evaluator, held-out sets, controls, paired baselines, records, two memories, the loop — has a concrete, inspectable form.

## Terms introduced
- **chain** — a periodic DAG of jobs with a deadline per instance.
- **job** — one node of one chain instance.
- **resource type / unit** — a kind of compute (CPU, GPU, DLA) / one instance of it.
- **DLA** — a deep-learning accelerator: a fixed-function inference engine next to the GPU.
- **placement** — choosing the resource type for a ready job.
- **dispatch** — choosing which ready job a free unit runs next.
- **non-preemptive** — a started job runs to completion.
- **hard / soft chain** — a chain whose deadline misses fail the gate / are allowed up to a limit.
- **EDF (earliest deadline first)** — dispatch the job with the nearest absolute deadline.
- **least laxity first** — dispatch the job with the least slack.
- **laxity** — deadline minus current time minus remaining work.
- **discrete-event simulation** — simulation that advances from event to event.
- **HEFT / earliest-finish-time placement** — place each job where it is predicted to finish first.
