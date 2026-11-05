# A0 — One experience versus many: why the second experience forces a kernel

**Source:** generalised from internal product, design and research documents (see [`../SOURCES.md`](../SOURCES.md)); Harel, "Statecharts: a visual formalism for complex systems", *Science of Computer Programming* 8(3), 1987; the Redux "three principles" (https://redux.js.org/understanding/thinking-in-redux/three-principles). · **Status:** concept primer. Every number is public (cited) or labelled illustrative.

## In one sentence
A robot that runs one interaction story can keep the story, the safety rules, the microphone and the motors in one state machine, but when a second and a third story arrive on the same robot, those concerns collide, so the team splits them: one small, shared **coordinator kernel** owns everything that must be true for every story, and each story becomes a separate, reviewable **experience** that runs inside it.

## What it is
The setting is a child-sized humanoid robot at a public demo stand. It greets strangers, talks with them, and does one small physical thing, such as a wave or offering a small gift. An **experience** is one reviewed interaction story of this kind: the beats the robot moves through, the physical acts allowed in each beat, and the exits from each beat.

The first coordinator was built for one experience. Its state enum named story beats directly (greet, invite a handshake, enrol a voice, converse, offer a gift, farewell). Its effect list named story actions directly. This works well for one story. The design documents record four things that break when more stories arrive.

1. **State collisions.** A second story needs different beats. If those beats go into the same enum, every story sees every other story's states, and every transition table grows.
2. **Ownership of shared hardware.** Two stories both want the microphone, the speaker, the head and the arms. Without one owner, two pieces of code can each believe that they hold the speaker.
3. **Switching.** The stand must move from one story to another. Without a defined lifecycle, a switch can leave a lease, a timer or a half-finished gesture behind.
4. **Duplicated safety.** Each story would re-implement stop handling, cleanup and visitor-identity rules. Each copy drifts.

## How it works
The decision is to build a **coordinator kernel**: deterministic code that runs on the robot's compute and owns the concerns that are invariant across all stories. The design lists them: event admission and ordering, correlation, participant authority (who the current visitor is), safety preemption, command authority and leases, timer mechanics, cleanup and the proof that stores are clean, the lifecycle, and evidence.

Each experience then owns only its story: its own local state type, its transition matrix, a pure **reducer** (see [[B1-experiences-as-reducers]]), its story invariants, and its own timeout, retry and participant *policy* choices.

The boundary between the two is a small, generic **effect vocabulary** ([[B3-the-effect-vocabulary]]). An experience can only *ask* for things through it. It cannot call the robot middleware, the behaviour library, the browser, a model, the clock, the file system or the network.

The design states two things this is not.

- **Not a runtime plug-in system.** All experience code is packaged in the pinned coordinator image and registered in source. Nothing is loaded from a path or a URL at run time.
- **Not a workflow language.** There is no YAML graph interpreter. A workflow language turns validation into an interpreter and moves the safety analysis into a second language.

Analogy: the kernel is the stage manager; each experience is one act in the repertoire. The act decides its lines and blocking; only the stage manager owns the lights, the doors and the safety curtain.

## What a rehearsed scripted act needs from a platform
The team also ran a rehearsed scripted act: a timed sequence of beats driven by a cue sheet and an operator's keys, with speech files, replayed motions, lights and music. It was being made autonomous one beat at a time. An alignment document compared it with the deterministic single-visitor coordinator and found that the two had been built in parallel without a shared plan. Its list of what the scripted act still lacked is a good checklist for any platform.

1. **Inputs into the runner, not only outputs.** Perception events (visitor present or gone, speech ended, item taken) must be able to start, end and skip beats.
2. **A bounded exit set for every beat** — done, timeout, skip-when, safety, operator — declared and enforced. This is what makes "not every beat for every visitor" safe rather than accidental.
3. **A scripted twin for every autonomous beat,** so the act never dead-ends on a model or a sensor.
4. **One spine, one trigger, one conversation engine, one motion authority,** chosen explicitly, not by whichever effort ships first. Two triggers cannot both decide when to greet.

The comparison also named the core design question the kernel answers: is the story *code* (an enum and transition tables) or *data* (a cue sheet)? The kernel keeps stories as reviewed code, but makes each one small, separate and composed from a library ([[B1-experiences-as-reducers]]).

## Design choices and trade-offs
The design records the alternatives it rejected and the reason for each.

| Alternative | Why it was rejected |
|---|---|
| One coordinator process per experience | Safety, cleanup and correlation diverge; every fix must be copied. |
| One large reducer with configuration branches | Unrelated stories share one matrix; review and replay get worse. |
| A general workflow language | Validation becomes an interpreter; safety analysis moves to a second language. |
| Runtime plug-ins | Weakens pinning, determinism, review and the static allowlist. |
| An LLM that orchestrates at run time | Model output cannot own safety, cleanup, identity or physical authority. |

The cost of the kernel is up-front work: a generic vocabulary, a registry, catalogs and a conformance suite must exist before the second experience lands. The pay-off is the first design goal: a new experience that recombines registered parts becomes an authoring task measured in hours, with no kernel change.

The vocabulary shrinks a lot in the process. A story-specific effect list of an illustrative 30 kinds (`old_effect_kinds_illustrative`) becomes a handful of generic effects plus catalogs of primitives and inputs.

## Common confusions
- **"A kernel is an operating-system kernel."** Here it means the small core of the coordinator that every experience shares. It runs as ordinary application code.
- **"More experiences need more coordinators."** The design has exactly one coordinator worker and one authoritative state transition at a time, whatever the number of registered experiences.
- **"The kernel makes stories configurable at run time."** Experience selection is fixed for the life of one coordinator process ([[B5-registration-selection-switching]]).

## Why it matters for robot experiences
A demo robot that must run unattended, in public, for long days cannot afford a second copy of its safety and cleanup logic for each new idea. The kernel turns "can we try a new interaction?" from a risky edit of the core into a bounded, reviewable addition, and it keeps the rules that protect visitors in one place.

## Terms introduced
- **experience** — one reviewed interaction story: its beats, the physical acts allowed in each beat, and the exits from each beat.
- **coordinator kernel (kernel)** — the deterministic core that owns every concern that must hold for every experience: admission, ordering, correlation, participant authority, safety, leases, timers, cleanup, lifecycle and evidence.
- **single writer** — the rule that exactly one component changes the authoritative state, one transition at a time.
- **statechart** — a hierarchical state machine with nested and parallel regions (Harel 1987).
- **scripted twin** — a pre-authored fallback for an autonomous beat that runs when the model or a sensor fails.
- **bounded exit set** — the declared, enforced ways a beat may end: done, timeout, skip, safety, operator.
