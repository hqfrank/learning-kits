# B1 — Experiences as reducers: definition, chapters, and the authoring flow

**Source:** generalised from internal design documents (see [`../SOURCES.md`](../SOURCES.md)); Redux "three principles" (https://redux.js.org/understanding/thinking-in-redux/three-principles); The Elm Architecture (https://guide.elm-lang.org/architecture/); Bernhardt, "Functional core, imperative shell" (2012 talk). · **Status:** concept primer. Every number is labelled illustrative.

## In one sentence
An experience is a frozen, source-registered definition whose heart is a **pure reducer** — `(local state, read-only kernel envelope, event) → (next local state, ordered effects)` — built from a reviewed **chapter library** and produced through an offline **authoring flow** in which an LLM may write the code but mechanical gates and humans decide whether it is registered.

## What it is
The **experience definition** is one immutable record per experience. It holds:

- an identity and a revision number;
- the experience's own **local state** type and a factory for the initial state;
- a **transition matrix** over local states and the shared stimulus vocabulary;
- the **reducer**;
- a **story invariant validator**;
- a **participant policy** (only the typed options the kernel exposes, see [[B2-state-ownership]]);
- the required and optional input IDs, the allowed primitive IDs, and the allowed effect kinds;
- a **story projector** that derives browser-safe display values from the state;
- the acceptance scenario IDs.

The definition does not list required capabilities or behaviour IDs a second time. They are derived from the primitive and input IDs through the catalogs, so there is no second list to drift.

## How it works
**The reducer is pure.** It reads no clock, draws no random number, does no I/O, and mutates nothing shared. Time and random choices arrive as events. The reducer can read the kernel envelope but cannot write it. Its only influence on kernel-owned state is to emit an effect, which the kernel validates and applies ([[B3-the-effect-vocabulary]]).

This is the Redux and Elm pattern applied to a robot: state is read-only, and changes are made by pure functions of the current state and an event. It is also "functional core, imperative shell": the reducer is the functional core; the kernel's materializer and adapters are the shell.

**Results go through a resolver.** At registration, the transition matrix is compiled into a resolver with three operations.

1. *transition* — look up the one rule for `(current state, stimulus)` and move to its target, with optional effects;
2. *state update* — keep the local state name and change other fields, with a declared cause;
3. *reject* — return the original state with no effects.

The kernel accepts only resolver-produced results and keeps no second transition index. A source fence test rejects experience code that builds a result directly.

**Chapters are reusable story fragments.** The chapter library is reviewed, pure code that builds a valid `(next state, effects)` pair for a recurring fragment: enter a greeting, invite a handshake with a timeout, run a bounded multi-turn conversation with fallback, offer a gift, say farewell, request completion cleanup. Chapters are library code, not authority. They emit only ordinary effects and are validated like any reducer output.

A worked example, the wave experience. Its story is `greet → await_wave → wave`.

- The `greet` chapter runs first.
- The local state `await_wave` starts the experience's gesture-wait timer, an illustrative 10 s (`gesture_wait_timeout_s_illustrative`).
- A visitor-gesture input with `gesture = wave`, from the current visitor's track, cancels the timer and enters `wave`. A gesture from any other track is rejected at admission and never reaches the reducer ([[B4-kernel-interception-and-arbitration]]).
- Timer expiry enters the terminal local state `gesture_not_observed`, whose only effect is "request completion cleanup".

The wave experience is therefore the first that composes two chapters; `await_wave` and `gesture_not_observed` are local states with a timer, not chapters.

**The authoring flow is offline.** No step runs on the robot or in the coordinator.

1. **Description.** A natural-language description of the experience, reviewed by its owner.
2. **Contract export.** The pinned coordinator image exports, as versioned JSON, the whole authoring contract: kernel phases, stimulus and cause vocabularies, the effect vocabulary and the kernel-only list, the primitive and input catalogs, the kernel invariants, the chapter library, and the reserved-policy rules. The authoring agent's prompt is generated from this export, never from a design document, so what the agent is told matches what runs.
3. **Decomposition.** The agent produces the local state type and matrix, the reducer (from chapters where one fits), the validator, the policy file, the manifest, replay scenarios and simulation drivers for every transition, and a **gap report** (below).
4. **Gates.** Registry validation, the kernel conformance suite, the experience suite, deterministic replay, then simulation acceptance ([[C2-the-conformance-ladder]]). All fail closed.
5. **Approval.** An architecture reviewer approves the design and the gap-report classification; a quality reviewer approves the gates and scenarios. Then the experience is registered and its profile pinned.

The **gap report** classifies every behaviour or input the description needs, per target, as one of: (a) already registered; (b) new, but fits an existing contract kind (catalog work, no kernel change); (c) a new robot or perception capability behind an existing contract kind; (c′) new *authority semantics* that fit no contract kind (a reviewed kernel and wire extension); or (d) **reserved** — a safety, privacy, participant or cleanup policy that must not be authored as story.

## Design choices and trade-offs
- **An LLM may author; it never runs on the robot.** Agent-authored experiences are reviewed, verified and pinned exactly like hand-written code, and their tests are reviewed with the code.
- **The reserved-policy classifier is the one part written by people.** It names the policies an experience may not author: participant lock mechanism and thresholds, departure grace, enrolment consent and retention, gift recovery, audio permit rules, cleanup semantics, safety and stop handling. The registry refuses a definition that tries to implement one. Changing the classifier is a design review.
- **Chapters over a workflow language.** The library gives most of the ergonomics of a workflow language without a second language to validate.

## Common confusions
- **"Pure means the reducer cannot use time."** It uses time as data: a timer expiry is an event like any other.
- **"The agent decides what runs."** The agent proposes artifacts. Gates and two human reviewers decide.
- **"A chapter is a sub-state machine with its own authority."** A chapter is a builder function. Its output is checked exactly like hand-written reducer output.

## Why it matters for robot experiences
A pure reducer makes every interaction replayable byte for byte from its event log, and a gated authoring flow lets new ideas arrive quickly without letting the speed reach the robot unchecked.

## Terms introduced
- **experience definition** — the immutable, source-registered record of one experience: identity, state type, matrix, reducer, validator, policy, manifest, projector and scenarios.
- **reducer** — a pure function from (local state, read-only envelope, event) to (next local state, ordered effects).
- **transition matrix** — the declared rules `(source state, stimulus) → target state` for one experience.
- **resolver** — the registration-time compilation of the matrix that is the only way to build a reducer result.
- **chapter / chapter library** — a reviewed pure builder for a recurring story fragment / the set of such builders shipped in the coordinator image.
- **authoring flow** — the offline pipeline description → contract export → agent-produced artifacts → mechanical gates → human approval.
- **contract export** — the versioned, machine-readable description of the authoring contract, exported from the pinned image.
- **gap report** — the per-target classification of every needed behaviour or input into registered, catalog work, capability work, authority extension, or reserved.
- **reserved-policy classifier** — the human-maintained rule set naming policies an experience must not author.
- **story projector** — the experience's pure function that derives browser-safe display values from committed state.
