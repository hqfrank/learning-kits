# Why a robot software stack runs slower than its parts — study notes

**Start here: the story →** [Start here — story](stories/01-why-the-stack-runs-slow.html) — a picture-first, interactive tour of the kit's diagnosis.

## In one paragraph

A home-robot software stack runs many services in containers on one small on-board computer, and
every service runs slower when the whole stack runs than when it runs alone. This kit teaches why,
and how to find each service's own reason from evidence instead of from a guess. The example board
is an Orin-class 12-core board (illustrative, `board_cores`), for example a Jetson AGX Orin. The
diagnosis splits each service's extra time into run-queue wait, run time and blocked time, names
one hypothesis per service, and tests it with a one-factor experiment whose prediction and
refutation rule are written before the run. The answer is different per service. From alone to
the full stack it is mostly CPU queueing on the shared core pool and the same work costing more
cycles; from the full stack to the full stack plus a VLA (vision-language-action model) it is
mostly GPU time-slicing between processes; and two of the largest full-stack numbers turn out to be
the bench and a software bug, not the platform. **Part A** covers the CPU-side mechanisms, **Part B**
the GPU-side mechanisms, and **Part C** what a bench latency number means for the deployed robot.
**Every measurement in this kit is illustrative:** a round teaching number that keeps the shape of a
typical finding, not data from any specific robot (see [`SOURCES.md`](SOURCES.md) and
[`constants.json`](constants.json)).

This is rung 1 of a four-rung learning kit (notes → diagram → explorer → video). It assumes the
reader knows the three sibling kits and links to them rather than re-explaining them:

- [`../nvidia-gpu-anatomy/`](../nvidia-gpu-anatomy/) — CUDA contexts, streams, time-slicing, MPS and MIG.
- [`../jetson-orin-thor-metrics/`](../jetson-orin-thor-metrics/) — the example boards' ceilings, the roofline and its ridge.
- [`../robot-workload-benchmarking/`](../robot-workload-benchmarking/) — how to benchmark a robot stack: run-queue wait, the observer effect, pre-registration, validity gates.

## How to read these notes

Read A0 first: it gives the question, the three load levels, the diagnosis map and the corrections.
Then read Part A → Part B → Part C, in this order.

### Start here
- [`SOURCES.md`](SOURCES.md) — what this kit is, the three classes of number, the public sources, and the reading conventions.
- [`notes/A0-the-big-picture.md`](notes/A0-the-big-picture.md) — from "slower in the full stack" to one mechanism per service; the diagnosis map; first readings and their corrections.

### Part A — CPU-side mechanisms
- [`notes/A1-cpu-queueing-on-a-shared-pool.md`](notes/A1-cpu-queueing-on-a-shared-pool.md) — run-queue wait on the shared core pool; wait per busy second; why a saturated core turns demand into wait.
- [`notes/A2-same-work-more-cycles.md`](notes/A2-same-work-more-cycles.md) — the same instructions need more cycles; the cluster move lands near its pre-registered class line, with a traffic caveat.
- [`notes/A3-priorities-in-containers.md`](notes/A3-priorities-in-containers.md) — `nice` does nothing across cgroups, `cpu.weight` does, and the wait moves to other services.
- [`notes/A4-costs-that-grow-with-history.md`](notes/A4-costs-that-grow-with-history.md) — a per-item logging cost on the dialogue engine's event loop that grows with conversation history.
- [`notes/A5-where-to-put-the-observers.md`](notes/A5-where-to-put-the-observers.md) — the measurement probe on the same core as the interaction service; probe placement and probe receive delay.

### Part B — GPU-side mechanisms
- [`notes/B1-gpu-time-slicing-and-the-dose-curve.md`](notes/B1-gpu-time-slicing-and-the-dose-curve.md) — GPU time-slicing between CUDA contexts; the dose curve; the camera's pool share is undecided at dose.
- [`notes/B2-low-issue-rate-is-not-free-room.md`](notes/B2-low-issue-rate-is-not-free-room.md) — kernel fill and waves; a low SM issue rate is not free room (kernel fill is theoretical, from launch configurations).
- [`notes/B3-mps-in-practice.md`](notes/B3-mps-in-practice.md) — MPS on Jetson: single-user mode, the SM cap, and why a stack that runs as two Linux users needs deployment changes first.
- [`notes/B4-compute-bound-or-near-the-ridge.md`](notes/B4-compute-bound-or-near-the-ridge.md) — the VLA's vision encoder: compute-bound on one board, near the ridge on another; compute form versus bandwidth form.

### Part C — what a bench number means
- [`notes/C1-deployment-fidelity-and-batch-1-latency.md`](notes/C1-deployment-fidelity-and-batch-1-latency.md) — deployment fidelity, the VLA's GPU-time budget, batch-1 latency, and upper and lower bounds from the probe.

### Other rungs
- Story: [Start here — story](stories/01-why-the-stack-runs-slow.html).
- Explorers: [`explorers/01-gpu-dose-curve.html`](explorers/01-gpu-dose-curve.html), [`explorers/02-vla-gpu-budget.html`](explorers/02-vla-gpu-budget.html), [`explorers/03-kernel-fill-calculator.html`](explorers/03-kernel-fill-calculator.html).
- Diagrams: [`diagrams/INDEX.md`](diagrams/INDEX.md).
- Quiz: [`../quiz/`](../quiz/) — spaced-repetition review of the notes.

### Reference files
- [`glossary.md`](glossary.md) — one definition per term, alphabetical; terms shared with a sibling kit link to that kit's glossary.
- [`constants.json`](constants.json) — every number this kit cites, each labelled public, sibling, or illustrative.

## Question a reader asks → note that answers it

| Question | Note |
|---|---|
| Why does every service run slower in the full stack, and is it one cause? | [[notes/A0-the-big-picture]] |
| How do I see CPU queueing per service, and what does "wait per busy second" mean? | [[notes/A1-cpu-queueing-on-a-shared-pool]] |
| Why does a thread need more cycles for the same work when neighbours are busy? | [[notes/A2-same-work-more-cycles]] |
| Can I fix a slow container by raising its priority? | [[notes/A3-priorities-in-containers]] |
| Why does a voice reply get slower the longer the conversation runs? | [[notes/A4-costs-that-grow-with-history]] |
| Can my own measurement probe be the cause of a slowdown? | [[notes/A5-where-to-put-the-observers]] |
| Do two GPU processes run at the same time, and how much does sharing cost? | [[notes/B1-gpu-time-slicing-and-the-dose-curve]] |
| The GPU's SM issue rate is low; is there room for another model? | [[notes/B2-low-issue-rate-is-not-free-room]] |
| Can MPS fix GPU sharing on the board? | [[notes/B3-mps-in-practice]] |
| Why was the vision encoder "slower than predicted"? | [[notes/B4-compute-bound-or-near-the-ridge]] |
| What does a VLA latency measured on the bench mean for the robot? | [[notes/C1-deployment-fidelity-and-batch-1-latency]] |

## Conventions

- Notes use the ASD-STE100-at-80% style: one fact per sentence, active voice, one term per concept, caveats before results, numbers with units.
- The subject is generic: "a home-robot software stack", "the stack", and role names for its services (the depth camera service, the object detector, the interaction service, the speech recognizer, the dialogue engine, the motor-control services, the measurement probe).
- Every number is public, a sibling-kit value, or labelled illustrative, and is cited by its key in [`constants.json`](constants.json); measured values are illustrative measurements, not data from a specific robot.
- Verdicts stay as pre-registered; post-hoc readings are labelled post-hoc, and corrections are shown as corrections.
- `[[wikilinks]]` connect notes inside this kit; relative Markdown links reach the sibling kits.
