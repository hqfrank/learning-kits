# B3 — The effect vocabulary: primitives, resource claims, atomic dispatch, and cancellation proof

**Source:** generalised from internal design documents (see [`../SOURCES.md`](../SOURCES.md)); Kleppmann, *Designing Data-Intensive Applications* (O'Reilly, 2017), chapters 11–12 on idempotence and "effectively-once" processing; Richardson, "Transactional outbox" pattern (https://microservices.io/patterns/data/transactional-outbox.html). · **Status:** concept primer. Every number is labelled illustrative.

## In one sentence
An experience can act only by emitting effects from a small generic vocabulary; the one that touches the world, "invoke primitive", names an entry in a reviewed **primitive catalog** whose **resource claims** decide what can overlap, and the kernel prepares and commits everything for an event as one snapshot before it dispatches anything, then keeps every claim until positive proof that the work is quiet.

## What it is
**The effect vocabulary** has these effects.

| Effect | What the kernel checks |
|---|---|
| invoke primitive | The primitive is declared by the experience and in the profile; the target has a healthy adapter; every required resource is free; participant, audio, safety and grasp gates pass; the requested deadline is within bound. |
| cancel primitive | Idempotent; cancels only active work this experience owns. |
| start timer / cancel timer | The kernel owns bounds and the scheduler. |
| request completion cleanup | The kernel builds the canonical cleanup, its deadline and its releases. |
| report to operator | Bounded diagnostic evidence only; it sends no notification. |

Some effects are **kernel-only** and can never be declared by an experience: readiness behaviour start and yield, preemption, entry to not-ready, stopped or recovery, participant lock, update, retarget, reattach and release, gift recovery, and forced cleanup. The vocabulary simply has no effect that reaches them.

Display is not an effect. After a reduction commits, the kernel runs the story projector over committed state. An experience therefore cannot publish a display hint that outlives or contradicts its state.

**The primitive catalog** lists every robot behaviour, speech act, gaze request and session service an experience may invoke. Each entry declares a **contract kind**, the targets it supports with an adapter contract per target, an authority class, its resource claims, a timeout bound, cancellation support, and a completion contract. There are three contract kinds.

1. **Physical action** — any behaviour with ordinary run semantics (a wave, an expression, a handshake, canned speech through the robot's text-to-speech), and composite actions that hold motion authority.
2. **Gaze lease** — set and clear a gaze target through the motion layer's gaze lease. A gaze mode is mandatory, and the kernel derives the priority from it; no entry supplies a raw priority.
3. **Session service** — a coordinator-materialised service that is not a motion: enrolment, a conversation turn, a gift offer, a greeting, an operator alert. It holds no motion or gaze authority.

## How it works
**Resources and claims.** The kernel owns a closed set of resources: the **action slot** (the motion layer's single active command), body, head, gaze, and audio out. Listening is not claimable; it is the kernel's visitor-audio permit. Each primitive claims each resource at most once, as exclusive or shared.

| Contract kind | Permitted claims |
|---|---|
| gaze lease | exactly gaze, exclusive |
| session service | nothing, or audio out (exclusive) through an output lease |
| physical action | the action slot (always, exclusive), plus any subset of body, head, gaze, audio out |

Because every physical action claims the one action slot, two physical actions never run at once. The kernel resolves the conflict the same way the motion layer does: an equal-or-lower priority request is deferred; a higher one preempts and then waits for the old command's terminal cancellation. Concurrency exists only *between* kinds: one physical action, one gaze lease and one conversation turn may overlap. Head and gaze drive the same actuators, so one primitive may not claim both, and a primitive that claims the head exclusively is refused while a gaze lease is active.

A consequence the design spells out: conversation speech (a session service on an output lease) may overlap a wave (a physical action), but canned speech through the robot's text-to-speech cannot, because that speech path occupies the action slot. A synchronised line plus gesture is one composite primitive, not two.

**Atomic preparation, then dispatch.** For every accepted external event the kernel:

1. intercepts kernel-owned events and derives the tentative envelope ([[B4-kernel-interception-and-arbitration]]);
2. calls the reducer;
3. validates kernel invariants, then story invariants, then every effect;
4. derives command IDs deterministically;
5. materialises the commands and verifies the tentative snapshot;
6. commits envelope, local state, pending commands, leases and timers as **one** snapshot;
7. only then dispatches, in effect order.

Any failure before step 6 commits nothing and dispatches nothing. A dispatcher failure after commit follows the correlated failure path; it never erases or invents command state. This is the transactional-outbox idea: record the intent and the state change together, then send. It also prevents a fast completion from arriving before the state records the command it belongs to.

**Idempotence.** Command IDs are deterministic. Cancel is idempotent. In the earlier single-tracker design, repeating identical command bytes with the same ID is a no-op, and a reused ID with different bytes is rejected (Kleppmann's "effectively once": at-least-once delivery plus idempotent handling).

**Cancellation proof.** Cancel targets the original invocation; there is no separate "stop" primitive. Each completion contract defines positive proof of quiescence: an action is terminal and no longer holds its slot; a gaze clear is acknowledged; a speech stream is stopped or completed and its stop acknowledgement succeeded. Only then does the kernel release *all* the invocation's claims.

Lease expiry, readiness loss, adapter removal or a transport disconnect is **not** proof. Each target declares a settle bound, an illustrative 1 500 ms (`cancel_settle_target_ms_illustrative`); it must not exceed the catalog ceiling, an illustrative 2 000 ms (`cancel_settle_ceiling_ms_illustrative`), and must be strictly shorter than the cleanup acknowledgement deadline, an illustrative 10 000 ms (`cleanup_ack_timeout_ms_illustrative`). The settle deadline is the earlier of "request time + settle bound" and any active cleanup deadline; cancellation never extends cleanup. If the settle deadline passes, the kernel enters forced cleanup with reason "cancellation stuck", keeps every claim, and refuses conflicting work. If cleanup then cannot prove quiescence, the kernel enters recovery ([[B2-state-ownership]]).

**Kernel revocations are unconditional.** Safety and reset, readiness loss, participant departure, cleanup and generation change cancel every primitive on every target. A catalog entry may add *stricter* revokers; it cannot remove or reorder these.

## Design choices and trade-offs
- **Catalog work versus kernel work.** A primitive whose command, progress, lease and cancellation fit an existing kind is one catalog entry plus adapter contracts: no kernel, effect or wire change. A primitive with new authority semantics needs a new, versioned contract kind through a reviewed wire migration. It must not hide new authority in its parameter schema. The aim is that the second case is rare.
- **Conservative first claims.** The first wave primitive claims slot, body and head exclusively and no audio. That allows conversation to overlap the wave but forces gaze to clear (with acknowledgement) before the wave starts, and gaze to be reacquired after it ends. A lighter arm-only wave is a later catalog revision with its own acceptance scenario.

## Common confusions
- **"Cancelling is releasing."** Cancelling starts settlement. Release happens only after positive proof.
- **"Lease expiry means the speaker is quiet."** Expiry stops further forwarding of audio; the claim stays held until the stream proves it stopped.
- **"Report to operator alerts staff."** It records diagnostics only. A visible alert is the separate operator-alert session-service primitive.

## Why it matters for robot experiences
A robot that talks over itself, or waves while its head is being steered elsewhere, looks broken. Resource claims make every overlap a deliberate, reviewed decision, and positive cancellation proof means "stopped" in the logs is true on the robot.

## Terms introduced
- **effect** — a typed request from a reducer to the kernel; the only way an experience influences anything outside its local state.
- **kernel-only effect** — an effect the kernel may perform but no experience may declare.
- **primitive / primitive catalog** — one registered thing an experience may invoke / the reviewed registry of them.
- **contract kind** — the class of a primitive's command, lease and completion semantics: physical action, gaze lease, or session service.
- **resource claim** — a primitive's declared exclusive or shared hold on one kernel resource.
- **action slot** — the resource that models the motion layer's single active command.
- **output lease** — the per-turn authority that carries audio out for brokered conversation speech.
- **atomic preparation and dispatch** — validate, materialise and commit one snapshot for an event before sending any command.
- **quiescence proof** — positive, correlated evidence that a cancelled or completed primitive no longer acts.
- **settle bound** — a target's maximum time to produce quiescence proof after a cancel request.
- **idempotent** — safe to apply more than once with the same result.
