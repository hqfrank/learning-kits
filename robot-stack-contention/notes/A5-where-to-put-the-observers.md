# A5 — Where to put the observers (probe placement)

**Source:** the observer effect and the bench-artefact catalogue in [B4](../../robot-workload-benchmarking/notes/B4-profilers-and-the-observer-effect.md) and [C7](../../robot-workload-benchmarking/notes/C7-how-the-bench-can-lie.md); CFS sharing as in [[A1-cpu-queueing-on-a-shared-pool]]; numbers from [`constants.json`](../constants.json) by key · **Status:** teaching note; every measured value is illustrative.

## In one sentence
Our measurement probe and request driver on a reserved core saturate it next to the interaction service, so about 90 % of that service's full-stack latency rise is an observer effect (my estimate from the illustrative `interaction_accepted_ms`, derived below); on a pool core the probe slows the camera instead, so no placement is free on this layout, and the real fix is a lighter probe.

## What it measures
The **observers** are our measurement processes: the measurement probe, the request driver for the interaction service, the metric scrapes, a slow sampler and the captures. The question is where they can run without changing what they measure. [B4](../../robot-workload-benchmarking/notes/B4-profilers-and-the-observer-effect.md) explains the observer effect in general, and [C7](../../robot-workload-benchmarking/notes/C7-how-the-bench-can-lie.md) catalogues bench artefacts.

The interaction-service metric is **request accepted p50**: the round trip request driver → middleware router → interaction service → router → request driver, measured on the bench side.

## How
The experiment moves the measurement probe, the request driver, the clock probe, the scrape containers and the pre-window commands from the reserved core to one pool core. The samplers move off that pool core. The stack's own placement stays unchanged. The control is two full-stack windows from the same bench, image, speech plan and board boot, with the observers on the reserved core. There are two windows per arm. The plan's other arm (a second reserved core) was not run.

Analogy: a referee who stands in the middle of a narrow corridor slows the players he is timing.

## Predicted
Written before the run: the reserved core stops being saturated; the accepted p50 falls near its alone value; the probe's own latencies become valid. The prediction is refuted if the accepted p50 stays high while the reserved core is no longer saturated.

## Measured
Each value below is an illustrative measurement.

| Quantity | Value (illustrative) | Key |
|---|---|---|
| Accepted p50: alone / probe on the service's core / probe moved | 2 / 40 / 5 ms | `interaction_accepted_ms` |
| Share of a saturated reserved core per group, probe on the service's core | 0.33 cores | `saturated_core_equal_share` |
| Probe CPU demand | 0.5 cores | `probe_cores_wanted` |
| Probe receive delay, p50 / p99, full stack | 10 / 30 ms | `probe_receive_delay_ms` |
| Camera rate cost with the probe on a pool core | 2 Hz | `probe_on_pool_camera_cost_hz` |

With the probe moved, the reserved core is no longer saturated, and the interaction service's main thread waits much less. On the pool core the probe still wants about half a core (illustrative, `probe_cores_wanted`) and still waits.

## The gap, and what it means
**Against the pre-registered outcomes:** the reserved core is no longer saturated, met; the accepted p50 falls near alone, met, with no overlap between the two sets of windows; the probe's latencies are valid, partly met (the receive delay falls, but its p99 stays high); the refutation rule is not met.

**The interaction service's full-stack latency is an observer effect.** The service itself waits for its core behind our probe. The instrument (the request driver) does not wait, so the full-stack value is measured correctly; it is caused by us. About 90 % of the excess over alone comes from the bench (my estimate from `interaction_accepted_ms`: (40 − 5) ÷ (40 − 2) ≈ 0.92). The full stack + VLA value of this metric was taken under the same core load, and it is likely affected the same way (not measured).

**Every full-stack probe latency carries the probe's own receive delay** of about 10 ms p50 and 30 ms p99 (illustrative, `probe_receive_delay_ms`). That is the order of the bias in every full-stack probe latency. Full-stack probe latencies are therefore upper bounds.

**A pool core is not free either.** With the probe on a pool core the camera loses about 2 Hz (illustrative, `probe_on_pool_camera_cost_hz`). The pool gets busier and the camera's threads wait longer, while the camera's CPU and GPU work per frame stay the same.

**The motor-control cores are not candidates.** They hold the motor-control services, which run a fast real-time bus loop. The full stack already has some late loops there, and one of those cores already queues the motor-control services' own threads. The probe would roughly double that core's load and compete at every wake-up (reasoning, not measured). Never put observers there.

**The second reserved core was not tested.** It hosts the middleware router, which is on every message path, and it is in the motor-control services' CPU cluster ([[A2-same-work-more-cycles]]).

**New full-stack baseline with both bench fixes** (observers on a pool core, and the engine log filter from [[A4-costs-that-grow-with-history]]):

| Quantity | Value (illustrative) | Key |
|---|---|---|
| Interaction service, accepted p50 | 5 ms | `interaction_accepted_ms` (field `probe_moved`) |
| Speech recognizer, transcript p50 | 640 ms | `transcript_latency_ms` (field `full_filtered`) |
| Camera | pays about 2 Hz for the observers on the pool | `probe_on_pool_camera_cost_hz` |

## So what
- **Choose placement by what the window measures** (recommendation). Use the pool core for full-stack, interaction-service and voice windows; report the camera with its pool-core offset.
- **The real fix is a lighter probe.** It costs about half a core even on the pool (illustrative, `probe_cores_wanted`). Subscribing only to small topics, or a cheaper subscriber, might remove the camera offset. Not measured.
- **General lesson (interpretation):** on a robot computer with no free core, every observer is a tenant. Measure its share and its neighbours before trusting a latency.

## Terms introduced
- **observers** — our measurement processes (the measurement probe, the request driver, scrapes, samplers, captures).
- **measurement probe** — the bench process that subscribes to topics and records receive times.
- **request driver** — the bench process that sends requests to the interaction service and times the accepted reply.
- **request accepted p50** — the median round trip from request to acceptance, measured on the bench side.
- **probe receive delay** — the probe's own delay between a message's arrival and its receipt, measured with a calibrator heartbeat; it biases every probe latency.
- **calibrator heartbeat** — a fixed-rate test publisher used to measure the probe receive delay.
- **observer effect** — the change an instrument causes in the system it measures. Reused from `../robot-workload-benchmarking/glossary.md`.
