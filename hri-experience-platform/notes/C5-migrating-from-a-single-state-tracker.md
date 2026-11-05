# C5 — Migrating from a single authoritative state tracker: projections, events, commands, ordering and cutover

**Source:** generalised from internal design documents (see [`../SOURCES.md`](../SOURCES.md)); Fowler, "Event sourcing" (https://martinfowler.com/eaaDev/EventSourcing.html) and "CQRS" (https://martinfowler.com/bliki/CQRS.html); ROS 2 documentation, "Quality of Service settings", https://docs.ros.org/en/kilted/Concepts/Intermediate/About-Quality-of-Service-Settings.html ; Fowler, "Strangler fig application". · **Status:** concept primer. Every number is public (cited) or labelled illustrative.

## In one sentence
Before the kernel, the robot already had a single in-memory, deterministic, single-writer state tracker that published its state as a read-only snapshot and drove components only by explicit correlated commands; its ideas — producers versus commanded actors versus passive consumers, a snapshot plus a transition stream, commands with outcomes, a speech fence, clear-before-next-visit — carry straight into the kernel, and the cutover from the older activation path is done atomically, behind shadow mode, with rollback in reverse order.

## What it is
The earlier design sorts every component into one of three categories.

1. **Signal producers** publish observations and outcomes to the tracker: perception, speaker attribution, the reasoner's lifecycle, the photo service, safety, operator controls. None may change experience state.
2. **Commanded actors** receive explicit, correlated commands: the reasoner, the audio gate, the gaze policy, the expression controller, the photo service, and the components that hold visit-scoped data. They act only on a command addressed to them, never because they saw a state snapshot.
3. **Passive consumers** may react to the snapshot when the reaction is display-only and idempotent: the operator UI, observability, visitor indicators. They must not feed an implied completion back.

This avoids the failure the design names directly: a distributed state machine in which every subscriber guesses what should happen next.

## How it works
**State as phase plus activity.** The tracker holds a small stable *phase* (not ready, waiting, engaging, visit active, closing, paused) and a current *activity* inside it (welcome, chat, offering, photo, celebration, lingering, farewell, clearing, recovery and so on). A new conversational detail adds an activity, not a top-level state. This is the same idea as the kernel's closed lifecycle phase around a private story ([[B2-state-ownership]]).

**Two projections, neither a command.** The tracker publishes:

- a **state snapshot** on a reliable, *transient-local* topic that keeps only the latest sample, so a late subscriber gets the current state and no history. In ROS 2, transient-local durability makes the publisher keep samples for late joiners, which behaves like a "latched" publisher (ROS 2 QoS documentation); the default profile, by contrast, is keep-last with depth 10 (`ros2_default_history_depth`), reliable and *volatile*;
- a **transition stream** on a reliable, volatile topic with a bounded depth, an illustrative 50 (`transition_stream_depth_illustrative`).

The snapshot answers "where are we now"; the stream answers "how did we get here". In CQRS terms these are read models; the single writer is the only command side. In event-sourcing terms the accepted event log is the source of truth and the snapshot is derived from it. Neither projection carries a transcript, audio, an image, an embedding, a name or a persistent person identifier.

**Domain events with clear "must not mean" rules.** Thin adapters turn wire messages into immutable internal events. The design pairs each with what it must *not* be taken to mean, for example:

- a new raw visitor ID is not automatically a new visit;
- the reasoner going idle does not mean the conversation or the visit ended;
- low audio level is not proof that speech finished;
- one outcome cannot settle a later command;
- a timeout never fabricates success;
- missing capability data is never replaced by a default "ready".

**Commands and outcomes.** Every command carries a command ID, visit ID, generation, issue time, deadline and a closed operation. The actor returns an outcome with the same correlation. The tracker records the pending command *before* dispatch, so a fast completion always finds the command it belongs to. Commands across processes use an accepted action or a bounded service with a terminal result; a reliable topic alone is not enough, because a command published before discovery can vanish.

**The speech fence.** Before the speech owner changes or a new activity starts, the tracker waits for the correlated terminal speech outcome of the previous utterance and of any expression. The fence has a deadline; failure closes or degrades the visit, and never starts a second voice over the first.

**Clear before the next visit.** On closing, the tracker sends one clear command to every owner of visit-scoped data (conversation context, attribution and enrolment state, audio, gaze, expression, photo, the observability projection). Each returns a correlated acknowledgement. The waiting state is unreachable until every current-generation acknowledgement arrives. A new approach during clearing is observed but cannot start a visit. This is the privacy boundary and the duplicate-greeting boundary at once.

**Product rules as state.** The tracker counts offers per visit. An offering is proactively offered at most once; a declined one is never proactively offered again; an illustrative 3 consecutive declines (`decline_limit_illustrative`) stop proactive offers; a visitor who leaves view for less than an illustrative 8 s (`same_visit_absence_s_illustrative`) is still the same visit. The values come from a versioned product policy, and live mode refuses configuration that omits any of them.

**Ordering and QoS.** The queue priority is safety, reset, operator control, correlated outcomes, then observations, with deterministic tie-breaks ([[B4-kernel-interception-and-arbitration]]). Each adapter declares its exact reliability, durability, depth and deadline contract, and start-up refuses readiness on a mismatch. This specifically covers the known class of a best-effort publisher with a reliable subscriber, which ROS 2 does not connect.

**Cutover.**

1. Promote the shared contract types first, as one reviewed bundle with regenerated bindings and relocked type hashes.
2. Build the pure reducer, with no middleware import in the core.
3. Run **shadow mode**: consume live signals, publish state under a shadow namespace, issue no commands, and compare traces with the product diagrams.
4. Add typed reasoner authority, so proactive, continuation and resume speech happen only inside an active bounded command.
5. Add the other actor command–outcome pairs; enable the speech fence only after terminal outcomes are proven.
6. Cut gaze over at one existing injection point; never add a second head publisher.
7. Establish the product audio permit; harness wiring is prior art, not product authority.
8. **Cut activation over atomically:** stop and disable the old activation path, verify process inventory, configuration and command provenance (publisher counts alone are not proof), then enable the new authority. Rollback disables the new authority before re-enabling the old.
9. Retire compatibility inference, such as "reasoner idle for N seconds means the conversation ended".

## Design choices and trade-offs
- **Commands, not subscriptions.** Driving actors from a snapshot is simpler to wire and impossible to reason about. Explicit commands cost a contract per actor and buy one place where decisions are made.
- **Two activation authorities never coexist.** The migration accepts a moment of downtime at cutover in exchange for never having two components that can both decide to greet.

## Common confusions
- **"The state topic is how components are told what to do."** It is a read-only projection; acting on it is forbidden for commanded actors.
- **"Reliable delivery makes a topic a command channel."** A command needs acceptance and a terminal outcome.
- **"Shadow mode is a test environment."** It runs on live inputs in production and issues nothing.

## Why it matters for robot experiences
Most robot stacks start with components that watch a shared state and react. This design shows the path out: keep one writer, turn reactions into commands with outcomes, prove the new path in shadow, and switch the deciding authority in one atomic step.

## Terms introduced
- **signal producer / commanded actor / passive consumer** — a component that only reports / that acts only on explicit correlated commands / that only renders the published state.
- **state snapshot** — the latest-value, transient-local projection of current state; not a command.
- **transition stream** — the volatile, bounded record of each accepted state change.
- **domain event** — an immutable, validated internal event made from a wire message by an adapter.
- **command and outcome** — a correlated request to one actor and its correlated terminal result.
- **speech fence** — the guard that waits for the previous utterance's terminal outcome before any new speech or activity.
- **clearer / clear acknowledgement** — an owner of visit-scoped data / its correlated proof that the data is gone.
- **shadow mode** — running the new reducer on live inputs, publishing under a separate namespace, issuing no commands.
- **cutover** — the atomic switch of deciding authority from the old path to the new one, with a reverse-order rollback.
- **transient local / volatile** — ROS 2 durability that keeps samples for late subscribers / that keeps none.
- **event sourcing / CQRS** — storing the event log as the source of truth / separating the single command side from read models.
