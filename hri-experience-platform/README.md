**Start here: the story** — [The stage manager](stories/01-the-stage-manager.html): one stage manager runs every act; the voice may improvise and ask, but only the stage manager calls the cues (a 10-minute visual story; [all stories](stories/INDEX.md)).

# A platform for many robot experiences: a coordinator kernel, experiences as reducers, an effect vocabulary, and simulation-first verification — study notes

## In one paragraph

A child-sized humanoid robot at a public demo stand greets strangers, talks with them, and does one small physical thing. One such interaction story is easy to build as one state machine; the second and third stories on the same robot collide over states, the microphone, the speaker, the head and the arms, and each would copy the safety and cleanup rules (**A0**). This kit teaches the platform that fixes it. A speech-to-speech **reasoner** owns what is said; a deterministic **coordinator** owns the agenda, what may be done, and every authority, and only it invokes anything (**A1**). Each experience is a frozen definition with a **pure reducer**, built from a chapter library through an offline authoring flow in which an LLM may write code but gates and humans decide (**B1**). The **kernel envelope** owns lifecycle, session, participant authority, leases, permits, timers and cleanup; each experience owns only an opaque local story (**B2**). Experiences act through a small **effect vocabulary**; primitives in a catalog declare **resource claims** that decide what may overlap, the kernel commits each event as one snapshot before dispatch, and claims are released only on positive quiescence proof (**B3**). The kernel **intercepts** safety, readiness, permits, faults, operator abort and cleanup before any experience sees them (**B4**). Experiences are registered in source, selected per process through a pinned profile, matched against **per-target** primitive and input catalogs, and switched only by a full stop–clean–restart (**B5**). The model gets a small context, no physical tools and per-turn speech leases, and every requested act is grounded in the catalog (**B6**). Verification starts in a **browser-accessible simulation** that replaces the world around the unchanged coordinator (**C1**), climbs a **conformance ladder** with named milestones and negative tests (**C2**), regenerates the richest old experience as a non-blocking experiment and compares evidence across targets structurally (**C3**), uses an **observatory** to exercise the real behaviour and conversation stack off the robot (**C4**), and inherits its event, command and cutover discipline from an earlier **single state tracker** (**C5**). The kit carries no measured numbers from any specific system; every number is public (cited) or a labelled illustrative design parameter (see [`SOURCES.md`](SOURCES.md)).

This is rung 1 of a four-rung learning kit (notes → diagram → explorer → video). It assumes a reader who knows what a state machine, a publish/subscribe topic and an LLM API call are, and nothing about social robots. For the robot stack and ROS 2 middleware from the compute side, see [`../robot-workload-benchmarking/`](../robot-workload-benchmarking/).

## How to read these notes

Read A → B → C. Part A gives you the problem and the role split; Part B gives you the kernel; Part C gives you how it is proven and run.

### Start here
- [`SOURCES.md`](SOURCES.md) — what this kit is, how the internal material was used, the public sources, and the number conventions.

### Part A — why a platform
- [`notes/A0-one-experience-versus-many.md`](notes/A0-one-experience-versus-many.md) — state collisions, shared hardware, switching, duplicated safety; what a scripted act needs from a platform; the decision to build a kernel and the alternatives rejected.
- [`notes/A1-the-reasoner-and-the-coordinator.md`](notes/A1-the-reasoner-and-the-coordinator.md) — the reasoner talks and proposes, the coordinator decides and invokes; accountability, measured convergence, reproducibility.

### Part B — the kernel design
- [`notes/B1-experiences-as-reducers.md`](notes/B1-experiences-as-reducers.md) — the experience definition, the pure reducer and resolver, chapters, the authoring flow, the gap report, the reserved-policy classifier.
- [`notes/B2-state-ownership.md`](notes/B2-state-ownership.md) — the kernel envelope, lifecycle phases, the local state contract, participant authority versus policy, cleanup failure to recovery, two levels of profile.
- [`notes/B3-the-effect-vocabulary.md`](notes/B3-the-effect-vocabulary.md) — effects and kernel-only effects, the primitive catalog and its three contract kinds, resource claims and the action slot, atomic preparation and dispatch, idempotence, cancellation proof.
- [`notes/B4-kernel-interception-and-arbitration.md`](notes/B4-kernel-interception-and-arbitration.md) — intercepted event classes, one ordered queue, admission and rejection, cross-host clocks, safety preemption, the conflict matrix.
- [`notes/B5-registration-selection-switching.md`](notes/B5-registration-selection-switching.md) — static registration, the input catalog, capability matching, target-scoped producers, adding an input, switching and the serial profile matrix.
- [`notes/B6-conversation-and-model-boundaries.md`](notes/B6-conversation-and-model-boundaries.md) — configuration, capability and output boundaries; bounded turns and per-turn speech leases; one voice path; duplex conditional on a measurement; skew.

### Part C — verification and operation
- [`notes/C1-simulation-first.md`](notes/C1-simulation-first.md) — the simulation replaces the world, not the brain; authority boundaries; isolated target; single-session ownership; what simulation cannot prove.
- [`notes/C2-the-conformance-ladder.md`](notes/C2-the-conformance-ladder.md) — kernel conformance, experience suite, platform-native done with milestones, simulation and physical acceptance, evidence rules.
- [`notes/C3-regeneration-and-comparison.md`](notes/C3-regeneration-and-comparison.md) — regenerating an old experience as an experiment; the semantic and cross-target comparators; canonical IDs, comparison schemas, permitted differences.
- [`notes/C4-the-observatory.md`](notes/C4-the-observatory.md) — fixture, live-cloud, real-observer and cloud-cell modes; sole writers; isolation; QoS mismatch; one release bundle; what it measures and what it does not.
- [`notes/C5-migrating-from-a-single-state-tracker.md`](notes/C5-migrating-from-a-single-state-tracker.md) — producers, actors and consumers; snapshot and transition stream; commands and outcomes; the speech fence; clear before the next visit; shadow mode and atomic cutover.

### Reference files
- [`glossary.md`](glossary.md) — one definition per term, alphabetical, linked to the note that introduces it.
- [`constants.json`](constants.json) — every number this kit cites, each labelled public or illustrative, with its source.

## Question a reader asks → note that answers it

| Question | Note |
|---|---|
| Why not just add the second story to the first state machine? | [[notes/A0-one-experience-versus-many]] |
| Why not let the LLM decide what happens next? | [[notes/A1-the-reasoner-and-the-coordinator]] |
| What exactly does an experience author write? | [[notes/B1-experiences-as-reducers]] |
| Can an LLM write a new experience, and what stops a bad one? | [[notes/B1-experiences-as-reducers]] |
| Who decides who the current visitor is? | [[notes/B2-state-ownership]] |
| What happens if cleanup cannot prove the robot is quiet? | [[notes/B2-state-ownership]] |
| Can the robot talk and wave at the same time? Speak twice at once? | [[notes/B3-the-effect-vocabulary]] |
| When is a cancelled gesture really stopped? | [[notes/B3-the-effect-vocabulary]] |
| Can an experience finish its sentence before a safety stop? | [[notes/B4-kernel-interception-and-arbitration]] |
| How does the robot know at start-up that it can run this experience here? | [[notes/B5-registration-selection-switching]] |
| Why can't experiences be switched mid-visit? | [[notes/B5-registration-selection-switching]] |
| What is the model allowed to see and ask for? | [[notes/B6-conversation-and-model-boundaries]] |
| Why test in a simulation first, and what can it not tell me? | [[notes/C1-simulation-first]] |
| When is the platform "done"? | [[notes/C2-the-conformance-ladder]] |
| How do I know simulation and robot behave the same? | [[notes/C3-regeneration-and-comparison]] |
| How do I develop conversation and gestures without a robot? | [[notes/C4-the-observatory]] |
| How do I move an existing robot stack onto this design safely? | [[notes/C5-migrating-from-a-single-state-tracker]] |

## Conventions
- Notes follow controlled language (about 80% ASD-STE100): one fact per sentence, active voice, one term per concept, terms defined before use, caveats before results.
- Every number is public with a citation, or labelled illustrative and keyed to [`constants.json`](constants.json); derived values say "my arithmetic".
- Wikilinks (`[[...]]`) are Obsidian-compatible; plain markdown links are used for files outside the notes.
