# C0 — Reference, not replica

**Source:** general measurement-campaign method, abstracted (see [[../robot-workload-benchmarking/SOURCES|SOURCES]]); no internal material reproduced. · **Status:** concept primer, no measured numbers.

## In one sentence
The goal of a robot-compute benchmark is to characterise the *workload class* a robot represents, not to reproduce one exact robot bit-for-bit — so the design prizes coverage over precision, labels every place it over- or under-estimates, sizes a stand-in for anything that will not run, and isolates a service rather than chaining it when the chain would hide the service's real load.

## What it is
"Reference, not replica" is the governing principle of the whole method. The benchmark takes a real robot's stack as its *reference* for which services exist and how they fit together, but does not try to match it exactly. Four rules follow:

1. **Coverage over precision.** A realisation that captures about 95% of a service's workload is accepted. Chasing the last few percent is not worth the fidelity it costs elsewhere.
2. **Label every over- and under-estimate.** Wherever the benchmark runs something heavier or lighter than the real robot, it says so, with the direction and rough size.
3. **Replace what cannot run with a sized stand-in.** If the real code runs on the target, run it with synthetic or recorded input. If it does not run (missing hardware, unshippable weights, a cloud service), replace it with an alternative that captures the same workload, and state the alternative's size and basis.
4. **Isolate rather than chain when the upstream would limit the downstream.** Services are chained only where the chain costs nothing. Where an upstream service would cap a downstream service's load (for example, a recording holding only a few people when perception must be tested at ten), the downstream service is given its own input sized to its real load.

## How it works
**Why class, not copy.** The result is meant to predict future use — this robot, the next model, a heavier configuration — so a slight, labelled over-estimate is acceptable and even useful. An exact replica of today's robot would answer a narrower question and would be impossible anyway, because closed SDKs, unshippable weights, and absent hardware cannot be copied.

**Coverage over precision in practice.** Each service gets the cheapest realisation that still exercises its real work. Public model weights at the real input shapes give representative compute even though the outputs are wrong (see [[A3-mapping-localization-navigation]]). A faithful fake board gives the real message path even though no motor is attached (see [[C3-the-harness-and-fakes]]).

**Labelling the direction of error.** Every deviation is written down with its sign. Running a speaker-identification model on the CPU when the robot uses a tiny GPU model is an over-estimate of CPU; omitting a video-streaming peer is an under-estimate of the camera. The sum of these labels is the honest statement of how the benchmark relates to the real robot.

**Isolate versus chain.** Chaining is free when the upstream does not constrain the downstream — feeding navigation from the real camera is fine because the camera keeps up. Chaining is harmful when the upstream caps the downstream — feeding perception from a recording limits it to the few people in the recording. There, the downstream service gets its own sized input instead (synthetic people at the chosen N). This keeps each service's load representative even when the real pipeline could not deliver it.

## How it is measured or used in a benchmark
- **Decide per service: run real, or sized stand-in.** Record which, and the stand-in's basis.
- **State the coverage claim.** "At least X% of the expected load is real code; the rest is stand-ins totalling Y, each labelled."
- **Keep a signed deviation list.** Every over- and under-estimate, with direction and rough size, carried by every conclusion.
- **Choose isolate or chain per edge.** Chain where free; isolate with a sized input where the upstream would limit the downstream.

## Common confusions
- **"The benchmark must match the robot exactly."** It characterises the workload class; an exact replica is both impossible and narrower than the goal.
- **"Over-estimating is a bug."** A labelled, slight over-estimate is acceptable and helps predict future use; an *unlabelled* one is the bug.
- **"Always chain services for realism."** Chaining a capping upstream hides the downstream's real load; isolate and size the input there.
- **"Wrong weights mean wrong workload."** For fixed shapes the compute is weight-independent, so public weights at real shapes give a representative load.

## Why it matters for robotics workloads
Every later choice in the method — the budget, the solo runs, the harness, the gates — serves this one principle. If the benchmark forgets it is building a reference and starts chasing an exact copy, it will spend its effort on fidelity that does not matter and still fail on the parts that cannot be copied. "Reference, not replica, with every deviation labelled" is what makes the result both achievable and honest.

## Terms introduced
- **reference, not replica** — characterising the workload class, not reproducing one exact robot.
- **coverage over precision** — accepting a realisation that captures most of a service's workload rather than all of it.
- **signed deviation** — a labelled over- or under-estimate, with its direction and rough size.
- **sized stand-in** — a replacement for a service that will not run, chosen to capture the same workload, with its basis stated.
- **isolate versus chain** — giving a service its own sized input versus feeding it from the upstream service; chain only where the upstream does not limit the downstream.
- **coverage claim** — the stated fraction of the workload that is real code versus stand-ins.
