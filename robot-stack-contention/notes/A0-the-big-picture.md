# A0 — The big picture: from "slower in the full stack" to a mechanism

**Source:** general benchmarking practice, taught in [`../../robot-workload-benchmarking/`](../../robot-workload-benchmarking/README.md); mechanisms from the public documents listed in [SOURCES.md](../SOURCES.md); every number from [`constants.json`](../constants.json) by key · **Status:** teaching note. All measurements here are illustrative round numbers that keep the shape of a typical finding; they are not data from any specific robot. The investigation is written as one worked case of a generic home-robot stack. Its numbers are illustrative, and its qualitative steps and outcomes are simplified to teach the method. They do not describe any specific product.

## In one sentence
Every module of a home-robot software stack runs slower when the full stack runs, and a per-service investigation finds a different mechanism per service: from alone to the full stack it is mostly CPU on the shared core pool, from the full stack to the full stack plus a VLA it is mostly GPU time-sharing, and two of the largest full-stack numbers turn out to be the bench and a software bug, not the platform.

## What it measures
The question is per service: why does each service lose rate or gain latency when everything runs at once? The answer must come from evidence, not from a guess.

The example board is an Orin-class 12-core board (illustrative, `board_cores`), for example a Jetson AGX Orin with 16 SMs (sibling, `sm_count_orin`). Clocks are locked, so frequency changes do not explain a slowdown.

Three load levels are compared:

- **Alone** — one service (or one small group of services) alone on the board.
- **Full stack** — every module on at once, about 40 services (illustrative, `stack_services`). **Caution:** the full stack is heavier than a freshly booted robot by design (see [[C1-deployment-fidelity-and-batch-1-latency]]).
- **Full stack + VLA** — the full stack plus a VLA (vision-language-action model) offered at 5 Hz (illustrative, `vla_offered_hz`). The VLA is a bench addition for the test.

The size of the problem, per service (alone → full stack):

| Service | Alone → full stack (illustrative) | Key |
|---|---|---|
| The object detector, frame time | 100 → 200 ms per frame | `detector_frame_ms_solo_full` |
| The depth camera service, rate | loses 5 Hz | `camera_full_stack_loss_hz` |
| The interaction service, request accepted p50 | 2 → 40 ms | `interaction_accepted_ms` (fields `alone`, `probe_on_its_core`) |
| The speech recognizer, transcript p50 | 600 → 850 ms | `transcript_latency_ms` (fields `alone`, `full`) |
| The motor-control services, cycles for the same work | 1.4× to 2× (a growth of 0.4 to 1.0) | `cycles_growth_range` |

## How
The investigation runs in four steps. An independent reviewer should check each step before the next one starts.

1. **Inventory.** Read every existing measurement window. Split each service's extra time into run-queue wait (runnable, waiting for a CPU), run time, and blocked time (neither running nor runnable: GPU sync, locks, I/O). This step uses no new board time.
2. **One hypothesis per service**, tested against existing evidence. Each verdict is "supported", "weakened" or "open".
3. **One-factor experiments.** For each one, the prediction and the refutation rule are written down and frozen before board time. This is pre-registration; [C5 — experimental design](../../robot-workload-benchmarking/notes/C5-experimental-design.md) teaches it.
4. **Per-service conclusions**, with the size of each cause and what stays open.

## Predicted
Before the experiments, step 2 names four cross-cutting hypotheses:

- **X1** — pool CPU time-share: services on the shared pool of 8 cores (illustrative, `pool_cores`) queue for a CPU, and the wait adds to each frame and message.
- **X2** — the same work costs more CPU cycles, because cores share cache and memory with memory-heavy neighbours.
- **X3** — GPU contention adds to the full-stack slowdown.
- **X4** — GPU time is the main cause of the full stack → full stack + VLA step.

## Measured
The diagnosis map: the conclusion per service and the note that teaches each mechanism. Each measured value is an illustrative measurement.

| Service | Cause supported by evidence | Confidence | Note |
|---|---|---|---|
| The object detector, alone → full stack | Pool CPU: run-queue wait is the largest added term, plus the same work running slower | Medium–high | [[A1-cpu-queueing-on-a-shared-pool]], [[A2-same-work-more-cycles]] |
| The object detector, full stack → full stack + VLA | GPU time-sharing between processes: blocked time is most of the added frame time | Medium–high in a camera-plus-detector row; expected, not tested, in the full stack | [[B1-gpu-time-slicing-and-the-dose-curve]] |
| The depth camera service | Pool CPU load and extra topic demand (provisional; the pre-registered pool share is "undecided at dose"); GPU sharing alone costs no frames when the pool is idle | Medium | [[B1-gpu-time-slicing-and-the-dose-curve]], [[A3-priorities-in-containers]] |
| The interaction service | Mostly the bench: our measurement probe on the same reserved core | High | [[A5-where-to-put-the-observers]] |
| Voice chain (the speech recognizer → the dialogue engine) | A logging cost in the dialogue engine that grows with conversation history | High for alone → full stack | [[A4-costs-that-grow-with-history]] |
| The motor-control services | Same work, more cycles; moving their CPU-cluster neighbours away removes about two thirds of the extra cycles (illustrative, `cluster_move_recovered`; path not isolated) | Medium | [[A2-same-work-more-cycles]] |
| Priority as a fix | Priority acts per container, and it moves the wait rather than removing it | Medium | [[A3-priorities-in-containers]] |
| Free GPU room | A low SM issue rate does not mean room for another process | Theoretical | [[B2-low-issue-rate-is-not-free-room]] |
| Sharing the GPU better | MPS is possible on the board, but it needs deployment changes first | Hypothesis for real services | [[B3-mps-in-practice]] |
| The VLA's vision encoder | Compute-bound on one board, near the ridge on another | Medium | [[B4-compute-bound-or-near-the-ridge]] |
| The VLA | GPU-time-bound; every latency number needs its meaning stated | Medium | [[C1-deployment-fidelity-and-batch-1-latency]] |

All eleven notes of the kit, in reading order: A0 (this note), [[A1-cpu-queueing-on-a-shared-pool]], [[A2-same-work-more-cycles]], [[A3-priorities-in-containers]], [[A4-costs-that-grow-with-history]], [[A5-where-to-put-the-observers]], [[B1-gpu-time-slicing-and-the-dose-curve]], [[B2-low-issue-rate-is-not-free-room]], [[B3-mps-in-practice]], [[B4-compute-bound-or-near-the-ridge]], [[C1-deployment-fidelity-and-batch-1-latency]].

## The gap, and what it means
Several first readings were wrong. The investigation corrects them in writing and keeps the corrections visible. The kit shows them as part of the method:

| First reading | Correction | Note |
|---|---|---|
| "The CPU changes from full stack to full stack + VLA are within round-to-round spread" | Withdrawn: one full stack + VLA round had no speech in its window, so it was not a CPU-side replicate. With voice on in both, pool wait rises. | [[A1-cpu-queueing-on-a-shared-pool]] |
| "The interaction service's accepted latency rises from 2 ms to 40 ms (illustrative, `interaction_accepted_ms`) because the platform is loaded" | About 90 % of the rise was our probe on the same core (my estimate from `interaction_accepted_ms`: (40 − 5) ÷ (40 − 2) ≈ 0.92). | [[A5-where-to-put-the-observers]] |
| "nice on the camera's threads tests CPU priority" | Invalid test: each container is its own cgroup, so a nice inside it changes nothing against other containers. | [[A3-priorities-in-containers]] |
| "The camera is GPU-bound" | GPU sharing alone cost the camera 0 Hz (illustrative, `camera_gpu_only_loss_hz`) with an idle pool. GPU load together with pool load was not tested. | [[B1-gpu-time-slicing-and-the-dose-curve]] |
| "SM contention" between the object detector and the VLA | Without MPS, work from different CUDA contexts does not run at the same time (`mps_no_concurrency_quote`); the wait is time-slicing. | [[B1-gpu-time-slicing-and-the-dose-curve]] |
| "A low SM issue rate means free room for another process" | By launch configuration (theoretical), about half the kernel time (illustrative, `kernel_time_sms_full_share`) already fills the SMs on some resource. | [[B2-low-issue-rate-is-not-free-room]] |
| "More GPU compute would not help" | Multi-wave kernels would run in fewer waves on more SMs (expectation, not measured; no gain for memory-bound kernels). | [[B2-low-issue-rate-is-not-free-room]] |
| "The vision encoder is several times slower than predicted" | The prediction used the bandwidth form, 6 ms (illustrative, `vision_pred_bandwidth_form_ms`), on a board where vision is compute-bound; the compute form gives 20–30 ms (illustrative, `vision_compute_form_ms`). | [[B4-compute-bound-or-near-the-ridge]] |

**Verdicts stay as pre-registered.** Where a rule gives "undecided at dose", or a value sits on a class line, the notes keep that wording. A post-hoc reading is labelled post-hoc and does not replace the verdict.

## So what
Two lessons carry to any robot stack (interpretation). First, "slower in the full stack" is several mechanisms at once, and each one needs its own one-factor test. Second, check the bench before the platform: the largest full-stack numbers for the interaction service and the voice chain came from our probe placement and a logging bug.

## Terms introduced
- **alone / full stack / full stack + VLA** — the three load levels: one service alone; every module on at once (`stack_services`); the full stack plus a VLA at a fixed offered rate (`vla_offered_hz`).
- **the stack** — a home-robot software stack: many services in containers on one board.
- **pool** — the shared general-purpose CPU cores (`pool_cores`), used by most services (defined in [[A1-cpu-queueing-on-a-shared-pool]]).
- **blocked time** — time a thread is neither running nor waiting for a CPU (GPU sync, locks, I/O).
- **observers** — our measurement processes: the measurement probe, the request driver, the metric scrapes.
- **window** — one fixed measurement interval that passes or fails validity gates (see [C4](../../robot-workload-benchmarking/notes/C4-windows-gates-and-validity.md)).
- **camera-plus-detector row** — a test configuration that runs only the depth camera service and the object detector, with an idle CPU pool.
- **pre-registered verdict** — the class that a rule written before the run assigns to the result; it is not re-worded afterwards.
- **X1 / X2 / X3 / X4** — the step-2 cross-cutting hypotheses listed under "Predicted" above.
