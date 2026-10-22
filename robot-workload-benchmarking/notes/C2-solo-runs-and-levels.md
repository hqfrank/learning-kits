# C2 — Solo runs and levels

**Source:** general measurement method, abstracted; `trtexec`-style engine timing (NVIDIA TensorRT, https://docs.nvidia.com/deeplearning/tensorrt/). · **Status:** concept primer, no measured numbers.

## In one sentence
Before measuring the whole stack together, the benchmark measures each service alone, at three levels of increasing realism — the bare inference engine, the service as actually deployed, and the service with its real upstream — so that each service has a clean solo baseline, and the combined-stack interference later has something to be compared against.

## What it is
**Solo before combined.** Every service is first measured running by itself, so its cost is known without contention. Only then is the full stack assembled (see [[C6-tiers-combined-runs-and-attribution]]). The solo numbers are the denominators for the interference the combined run reveals.

**The unit is the deployed service, not the model.** A solo measurement is of the service as it runs on the robot — its container, its runtime, its pre- and post-processing — not of the raw neural network. The network is a fraction of the service's cost (see [[A2-people-perception]]); measuring only the network would miss the CPU work that usually dominates.

**Three levels.** Each service can be measured at three levels of realism:

- **L1 — the engine alone.** The compiled inference engine timed in isolation (a `trtexec`-style run): no service wrapper, no middleware. This gives the network's own latency and throughput, the floor.
- **L2 — the service as deployed.** The real service in its real container, driven through its own interface, including its pre- and post-processing. This is the deployable cost.
- **L3 — the service with its real upstream.** The service plus the upstream services it consumes (for example, the camera feeding mapping). This captures the real input shape and timing.

## How it works
**Why levels.** The three levels separate three questions: L1 asks "how fast is the network?", L2 asks "how fast is the service?", and L3 asks "how fast is the service on real input?" The gaps between them are informative — L2 minus L1 is the service's own overhead (the CPU glue), L3 minus L2 is the cost of real upstream data.

**Idle floors versus working costs.** Many services are event-driven: they do almost nothing until an input arrives. An event-driven service measured with no input shows an **idle floor** — near-zero cost — which is not its working cost. To measure the working cost the service must be *driven*: a wake-word service needs real speech, a behaviour service needs real requests, a mapping service needs real motion (see [[A3-mapping-localization-navigation]] and [[A5-audio-and-voice]]). A solo window that shows an idle service at ~0 cost must be labelled an idle floor, not reported as the service's cost.

**Drivers exercise a service through its own API.** To get a service into its working state, the benchmark drives it the way the robot would: it commands the controller into a mode, plays a speech schedule into the voice pipeline, injects detections into perception, replays motion into mapping. The driver uses the service's real interface, so the service does real work.

**Replaced pairs.** Where a service is a sized stand-in (see [[C0-reference-not-replica]]), the solo run measures the stand-in, and the result is labelled as the stand-in's cost with its basis, so the combined run adds a known, labelled quantity.

## How it is measured or used in a benchmark
- **Measure solo before combined.** Get a clean per-service baseline first; it is the denominator for interference.
- **Measure the deployed service, not the model.** Include the container, runtime, and pre/post-processing.
- **Pick the level that answers the question.** L1 for the network floor, L2 for the deployable cost, L3 for real-input cost.
- **Drive event-driven services.** Feed real input through the service's own interface; never report an un-driven idle floor as a working cost.
- **Label idle floors and stand-ins.** Say explicitly when a number is an idle floor or a sized stand-in.

## Common confusions
- **"Measure the model to get the service's cost."** The service's CPU glue usually dominates; measure the deployed service (L2), not just the engine (L1).
- **"A service at ~0 cost is cheap."** If it is event-driven with no input, that is an idle floor, not its working cost; drive it.
- **"L3 is always the right level."** L3 captures real input but adds the upstream's variability; L2 is the clean deployable cost. Choose per question.
- **"Solo runs are a warm-up for the real test."** The solo numbers are the baseline the combined-run interference is measured against; they are a result, not a rehearsal.

## Why it matters for robotics workloads
A combined-stack number alone cannot say *why* a service slowed — you need its solo cost to compute the interference. And a solo number alone can lie, if the service was idle for want of input. The three levels and the idle-floor rule make each service's cost both clean (measured alone) and real (measured driven), which is what lets the combined run in [[C6-tiers-combined-runs-and-attribution]] attribute the interference honestly.

## Terms introduced
- **solo run** — a service measured alone, without contention; the baseline for interference.
- **deployed service as the unit** — measuring the service in its container with its pre/post-processing, not the bare network.
- **L1 / L2 / L3 levels** — the engine alone / the service as deployed / the service with its real upstream.
- **idle floor** — the near-zero cost of an event-driven service with no input; not its working cost.
- **working cost** — a service's cost when driven with real input.
- **driver** — a component that drives a service through its own interface to put it in its working state.
- **replaced pair** — a sized stand-in measured in place of a service that will not run, labelled with its basis.
