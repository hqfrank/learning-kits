# C2 — The conformance ladder: from kernel rules to a live robot

**Source:** generalised from internal design documents (see [`../SOURCES.md`](../SOURCES.md)); Pact contract-testing documentation (https://docs.pact.io/); North, "Introducing BDD" (2006), https://dannorth.net/introducing-bdd/ . · **Status:** concept primer. No numbers beyond labelled illustrative ones.

## In one sentence
Every experience climbs the same ladder — kernel conformance, its own experience suite, simulation acceptance, then (separately) physical acceptance — and the platform's definition of done is written in platform-native terms with named milestones, each criterion proven by a failing negative test as well as a passing positive one, and every claim backed by schema-versioned evidence from which authority intervals are read, never inferred.

## What it is
The ladder, from bottom to top.

1. **Kernel conformance suite.** Parameterised over every registered experience, so a new registration is covered without new kernel tests.
2. **Experience suite.** Written per experience (by the authoring agent for agent-authored experiences, and reviewed with the code).
3. **Platform definition of done.** Milestone criteria that name no legacy experience.
4. **Simulation acceptance.** Per experience, on the simulation target.
5. **Physical acceptance.** Hardware-in-the-loop on the robot, with sign-off by the architecture and quality reviewers. Agent authorship does not change this gate.

## How it works
**What the kernel conformance suite proves** for every experience:

- deterministic replay;
- safety preemption from every local state;
- participant departure enters common cleanup;
- stale session, generation, command and timestamp rejection;
- no raw adapter or middleware access;
- effect and primitive allowlist enforcement, and reserved-policy refusal;
- materialisation before dispatch, and cleanup acknowledgement before new admission;
- back-to-back sessions without retained authority;
- bounded timers, queues, retries and diagnostics;
- the resource-claim matrix: two physical actions never admitted together; an audio-out conflict refused; an exclusive-head primitive refused while gaze is active; a head-defers-to-gaze primitive proven in *both* acquisition orders;
- a stuck cancellation enters forced cleanup, keeps every claim, and reaches recovery when quiescence never arrives;
- lease expiry never counts as quiescence;
- readiness fails, with a negative test, if the reasoner profile has tools, context, abilities or camera egress ([[B6-conversation-and-model-boundaries]]);
- a gesture from a track that is not the participant is rejected, with a negative test.

**What each experience suite contains:** transition-matrix tests, policy validation tests, happy-path and bounded-failure replay scenarios, capability-degradation scenarios, expected command and cancellation traces, and projection tests.

**The definition of done has milestones, and must name which one.**

- **Simulation milestone.** On the simulation target with no cloud credentials, no network egress and no hardware: kernel conformance; safety, authority and cleanup invariants each shown by a failing negative test; deterministic replay (identical inputs under the replay clock give identical canonical state encodings, invocation sequences and evidence digests); all three primitive contract kinds added through the catalog *and invoked* through success, cancellation and failure paths by a purpose-built contract-smoke experience; one new input added through the catalog; the first-registry experiences (a greeting, a chat, a wave, and the contract-smoke experience) landed through the authoring flow; and, per experience, a clean second browser session back to back with the first.
- **Showcase artifact.** One command runs a deterministic scenario and produces evidence plus a shareable video. The scenario proves, in order: participant gaze acquired; brokered speech overlapping gaze; positive gaze clear; brokered speech overlapping a wave; authoritative wave completion; correlated gaze reacquisition; cleanup with no retained claim.
- **Live-chat gate.** Live conversation through the real model, on the simulation target. A cloud outage may block this gate but must not invalidate the offline simulation milestone.
- **Cross-target milestone.** The same experiences pass hardware-in-the-loop with physical adapter and producer contracts, and produce equivalent evidence under the cross-target comparator ([[C3-regeneration-and-comparison]]). Until this holds, every profile is simulation-only and physical execution stays disabled.

The simulation milestone does not authorise physical deployment of anything.

**Evidence rules.** A schema-versioned generic projection carries: experience ID and revision, kernel phase, local state name and state schema version, primitive invocations with correlation, participant decisions, cleanup results, input admission decisions, the visitor-audio permit lifecycle, and the full resource lifecycle of every invocation (request, admit or defer, acquired, preemption, cancellation, settle bound and derived deadline, acknowledgement, quiescence proof, expiry, still-held claims, forced-cleanup reason, recovery, release). It exposes held-interval endpoints from acquisition to release, including intervals left open by a stuck cancellation. Comparators must read authority intervals from these fields and must not infer them from presentation events or terminal outcomes.

## Design choices and trade-offs
- **Platform-native done.** An earlier draft made parity with the richest old experience the exit criterion. The design rejected that: any single legacy experience as the definition of done bends the platform toward it. The draft had already added a contract kind that experience needed and misclassified a composite action while doing so. The old experience became a required but non-blocking experiment ([[C3-regeneration-and-comparison]]).
- **A purpose-built contract-smoke experience** proves the contract kinds, so that no demo story has to be inflated to cover them.
- **Contract tests, not only end-to-end tests.** Each adapter and producer contract names its own acceptance scenarios per target. This is the consumer-driven contract idea (Pact): the kernel states what it needs from each adapter, and each adapter proves it separately. Experience scenarios read like behaviour-driven tests: given a state and an input, when the event is admitted, then these effects and this evidence.

## Common confusions
- **"Done" without a milestone.** The design forbids it; "done" must say simulation or cross-target.
- **"A positive test proves an invariant."** Each invariant needs a negative test that fails when the rule is broken.
- **"The video proves the overlap."** The video illustrates; the authority intervals in the evidence prove.

## Why it matters for robot experiences
A ladder with explicit rungs stops two common failures: declaring victory in simulation, and testing safety only on the happy path. It also tells a team exactly which claim it may make in a review today.

## Terms introduced
- **conformance ladder** — the ordered gates kernel conformance → experience suite → simulation acceptance → physical acceptance.
- **kernel conformance suite** — the parameterised tests every registered experience must pass, covering kernel rules.
- **experience suite** — the per-experience matrix, policy, replay, degradation, trace and projection tests.
- **definition of done (platform-native)** — milestone criteria provable on the new kernel without any legacy experience.
- **simulation milestone / cross-target milestone** — done on the simulation target offline / done on both targets with equivalent evidence.
- **contract-smoke experience** — a non-visitor experience that invokes one primitive of each contract kind through every path.
- **negative test** — a test that demonstrates a rule by showing that violating it fails.
- **held interval** — the evidence record of when an invocation acquired and released a resource.
- **hardware-in-the-loop (HIL)** — acceptance with the real robot hardware in the control loop.
