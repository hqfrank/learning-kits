# Benchmarking a robot's on-board compute workload: the stack, the metrics, and the method — study notes

**Start here: the story →** [The robot's kitchen](stories/01-the-robots-kitchen.html) — a picture-first, interactive tour of the whole kit in ten minutes ([all stories](stories/INDEX.md)).

## In one paragraph

A home robot runs its whole software stack — cameras, perception, mapping, locomotion, voice, and
large models — on one small on-board computer, as a crowd of concurrent services with different
deadlines sharing one CPU, one GPU, and one pool of memory. This kit teaches how to benchmark that
workload. **Part A** describes the stack: what each pipeline does, how it works, and which resource
it loads, with the recurring lesson that the CPU bookkeeping around small neural networks usually
costs more than the networks themselves, and that the real cost is often demand-gated or
per-message. **Part B** describes the metrics and their traps: CPU usage and the commonly-misread
throttling counter, GPU-busy as a time fraction not an occupancy, rates and latency across two
machines' clocks, deadline statistics done as rare events with block confidence intervals, and
profilers that perturb the thing they measure. **Part C** describes the method that keeps the
answer honest: characterise the workload class rather than copy one robot, predict each stage from
first principles before measuring, run each service solo before combining, put a faithful harness
on a second machine, gate every window for validity, pre-register the whole design, build the stack
up in tiers and attribute the first limit — and know the catalogue of ways the bench can lie. The
kit carries no measured numbers from any specific robot; every number is a public source, a value
from a sibling kit, or a labelled illustrative figure (see [`SOURCES.md`](SOURCES.md)).

This is rung 1 of a four-rung learning kit (notes → diagram → explorer → video). It assumes the
reader has read the two sibling kits — [`../nvidia-gpu-anatomy/`](../nvidia-gpu-anatomy/) and
[`../jetson-orin-thor-metrics/`](../jetson-orin-thor-metrics/) — and links to them rather than
re-explaining the GPU (SM, warp, L2, roofline) or the shared-SoC co-tenancy results.

## How to read these notes

Read Part A → Part B → Part C. Part A gives you the stack the metrics measure; Part B gives you the
metrics the method uses; Part C gives you the method.

### Start here
- [`SOURCES.md`](SOURCES.md) — what this kit is, where the method comes from, the public sources, and the reading conventions.

### Part A — the stack: what each piece does and how it works
- [`notes/A0-the-big-picture.md`](notes/A0-the-big-picture.md) — a robot stack as concurrent pipelines (sense → perceive → decide → act); rates, deadlines, timing classes, on-board vs cloud.
- [`notes/A1-depth-camera-and-odometry.md`](notes/A1-depth-camera-and-odometry.md) — stereo/neural depth, point cloud, VIO, video encode; the camera as a CPU+GPU+memory load; frame rate as a health signal.
- [`notes/A2-people-perception.md`](notes/A2-people-perception.md) — detection, face, re-ID, pose, active-speaker; tracking, smoothing, 3D projection; cost scaling with N; why CPU post-processing dominates.
- [`notes/A3-mapping-localization-navigation.md`](notes/A3-mapping-localization-navigation.md) — keyframes, DISK, LightGlue, MixVPR, loop closure, iSAM2, TSDF, planning; a bursty workload.
- [`notes/A4-locomotion-and-whole-body-control.md`](notes/A4-locomotion-and-whole-body-control.md) — the control policy, the hard-real-time loop and its deadline, the fast motor bus, core isolation.
- [`notes/A5-audio-and-voice.md`](notes/A5-audio-and-voice.md) — mic-array framing, VAD, wake-word, speaker-id, ASR, TTS; why per-message overhead can exceed model cost.
- [`notes/A6-vla-and-large-models.md`](notes/A6-vla-and-large-models.md) — VLAs (GR00T N1.x, π0.5), action chunks, denoising steps, re-planning rate; a VLA as a closed-loop GPU tenant.
- [`notes/A7-middleware-containers-and-platform.md`](notes/A7-middleware-containers-and-platform.md) — ROS 2 pub/sub, QoS, the router, containers, CPU quotas, core pinning; small in CPU, decisive for correctness.

### Part B — metrics: what each means and how it is collected
- [`notes/B0-cpu-metrics.md`](notes/B0-cpu-metrics.md) — cgroup usage in cores, quota throttling and its misreading, per-core busy, run-queue wait, the foreign-CPU census.
- [`notes/B1-gpu-power-memory-metrics.md`](notes/B1-gpu-power-memory-metrics.md) — GPU-busy as time not occupancy, EMC % relative to the clock, power rails, and why CPU and GPU memory must not be summed.
- [`notes/B2-rates-periods-and-latency.md`](notes/B2-rates-periods-and-latency.md) — topic rate, period percentiles, receive vs stamp, cross-machine clocks, clock-free latency, the busy-observer bias.
- [`notes/B3-deadlines-tails-and-statistics.md`](notes/B3-deadlines-tails-and-statistics.md) — misses per minute with a Poisson interval, tails not means, sample-count rules, block bootstrap, paired differences.
- [`notes/B4-profilers-and-the-observer-effect.md`](notes/B4-profilers-and-the-observer-effect.md) — tegrastats, Nsight Systems, Nsight Compute; why tracing perturbs; trace-only windows; profiler safety.

### Part C — method: why the campaign is designed this way
- [`notes/C0-reference-not-replica.md`](notes/C0-reference-not-replica.md) — workload class not exact copy; coverage over precision; labelled deviations; isolate vs chain.
- [`notes/C1-predict-then-measure.md`](notes/C1-predict-then-measure.md) — the compute-budget ledger, bound class, measured ÷ predicted, why batch-1 models are launch-bound.
- [`notes/C2-solo-runs-and-levels.md`](notes/C2-solo-runs-and-levels.md) — solo before combined; the deployed service as the unit; L1/L2/L3 levels; idle floors vs working costs.
- [`notes/C3-the-harness-and-fakes.md`](notes/C3-the-harness-and-fakes.md) — the second-machine harness, faithful fake boards, cloud stubs, synthetic inputs, bag replay, network islands.
- [`notes/C4-windows-gates-and-validity.md`](notes/C4-windows-gates-and-validity.md) — warm-up and fixed windows, sample-count rules, locked clocks, validity gates, void vs flagged.
- [`notes/C5-experimental-design.md`](notes/C5-experimental-design.md) — pre-registration, no tuning after data, interleaved order, replicate blocks, paired comparisons, confounds, addenda/supersedes.
- [`notes/C6-tiers-combined-runs-and-attribution.md`](notes/C6-tiers-combined-runs-and-attribution.md) — workload tiers, the interference factor, PASS/UNRESOLVED/FAIL bands, first-limit attribution, the saturated-baseline failure.
- [`notes/C7-how-the-bench-can-lie.md`](notes/C7-how-the-bench-can-lie.md) — the catalogue of bench artefacts, how each is detected, and the rule that catches it.

### Reference files
- [`glossary.md`](glossary.md) — one definition per term, alphabetical; terms shared with a sibling kit say so.
- [`constants.json`](constants.json) — every number this kit cites, each labelled public, sibling, or illustrative.

## Question a reader asks → note that answers it

| Question | Note |
|---|---|
| What is a robot stack, really? | [[notes/A0-the-big-picture]] |
| Why is the camera service so heavy, and what is demand-gated? | [[notes/A1-depth-camera-and-odometry]] |
| Why does perception cost grow with the number of people, and why is the GPU not the bottleneck? | [[notes/A2-people-perception]] |
| What makes mapping bursty, and how do I drive it into its busy state? | [[notes/A3-mapping-localization-navigation]] |
| Which service has a hard deadline, and how is it protected? | [[notes/A4-locomotion-and-whole-body-control]] |
| Why can audio plumbing cost more than the audio models? | [[notes/A5-audio-and-voice]] |
| Why does a VLA's latency cap the robot's re-planning rate? | [[notes/A6-vla-and-large-models]] |
| Why does the platform config matter if it uses almost no CPU? | [[notes/A7-middleware-containers-and-platform]] |
| How do I measure CPU per service, and what is the throttling counter really? | [[notes/B0-cpu-metrics]] |
| Is "GPU 40% busy" a utilisation? Can I add CPU and GPU memory? | [[notes/B1-gpu-power-memory-metrics]] |
| How do I measure latency across two machines without fooling myself? | [[notes/B2-rates-periods-and-latency]] |
| How do I put an honest confidence interval on a deadline-miss rate? | [[notes/B3-deadlines-tails-and-statistics]] |
| Which profiler, and why can't I trust a profiled latency? | [[notes/B4-profilers-and-the-observer-effect]] |
| Should I copy the robot exactly? | [[notes/C0-reference-not-replica]] |
| How do I turn a measurement into a test of understanding? | [[notes/C1-predict-then-measure]] |
| Why measure each service alone first, and at which level? | [[notes/C2-solo-runs-and-levels]] |
| Where does the harness go, and how faithful must a fake be? | [[notes/C3-the-harness-and-fakes]] |
| When does a window's number count? | [[notes/C4-windows-gates-and-validity]] |
| How do I stop myself from manufacturing a result? | [[notes/C5-experimental-design]] |
| How do I judge "does the whole stack carry?" and name the first limit? | [[notes/C6-tiers-combined-runs-and-attribution]] |
| What are the ways a bench produces a confident wrong answer? | [[notes/C7-how-the-bench-can-lie]] |

## Conventions

- Notes use the ASD-STE100-at-80% style: one fact per sentence, active voice, one term per concept, caveats before results, numbers with units.
- The subject is generic: "a home robot's software stack", "the reference robot", "a benchmarking campaign".
- Every number is public, a sibling-kit value, or labelled illustrative (see [`SOURCES.md`](SOURCES.md) and [`constants.json`](constants.json)); nothing is a measurement from a specific robot.
- `[[wikilinks]]` connect notes inside this kit; relative Markdown links reach the sibling kits.
