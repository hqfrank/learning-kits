# B4 — Kernel interception and arbitration: what the kernel sees first

**Source:** generalised from internal design documents (see [`../SOURCES.md`](../SOURCES.md)); Lamport, "Time, clocks, and the ordering of events in a distributed system", *Communications* 21(7), 1978 (total order from a tie-break rule). · **Status:** concept primer. No numbers.

## In one sentence
Every input passes through the kernel before any experience sees it: the kernel orders events by a fixed priority, rejects stale, duplicate and uncorrelated ones, handles safety, readiness, audio permits, faults, operator abort and cleanup itself, and delegates only what is left to the experience's reducer, which can neither delay nor override any of it.

## What it is
The kernel **intercepts** a fixed set of event classes before delegation:

- safety and reset;
- readiness assessment, refresh and loss;
- start and yield of the idle "ready" behaviour;
- visitor-audio permit issue, revoke and refusal;
- runtime faults and queue overflow;
- operator abort;
- participant retirement that requires cleanup;
- cleanup acknowledgements and the cleanup deadline;
- the startup proof that every store is clean.

An experience must not override, delay or reject any of them. After delegation, the kernel validates the whole next envelope, local state and every effect before committing ([[B3-the-effect-vocabulary]]).

## How it works
**One ordered queue.** All inputs — perception, the reasoner, the motion layer, timers, the operator, the simulation — become immutable typed events in one bounded priority queue with one worker. The priority order is: safety, reset, operator control, correlated command outcomes, then observations. Inside one priority, a total order comes from normalised observation time, then source rank, then source sequence number, then event ID. Replay uses the recorded accepted order. (Lamport's rule: any deterministic tie-break over a partial order yields a total order every replica agrees on.)

**Admission before reduction.** Each event carries a context: source ID and sequence, observation and receive time, clock domain and synchronisation epoch, timestamp uncertainty, and, when relevant, session, generation and command ID. The kernel rejects at admission:

- stale, duplicate, wrong-generation, wrong-session or wrong-command events;
- outcomes for a command that is not pending;
- events whose age or timestamp uncertainty exceeds configured bounds;
- participant-bound inputs whose track does not equal the current session participant track ([[B2-state-ownership]]);
- inputs from a source not admitted for the deployment's target ([[B5-registration-selection-switching]]).

A rejected event never reaches the reducer, so no experience can act on it by mistake.

**Clocks across hosts.** Perception may run on a different computer. Its events carry source time, clock domain, epoch and measured uncertainty. Liveness and deadlines use the coordinator's own receive-time monotonic clock. Cross-host timestamps are used for association only after a bounded mapping, and too much uncertainty rejects or degrades the event. A network partition freezes no state: feeds become unhealthy on local receive-time expiry, new commands are withheld, and active visits take their configured bounded close path.

**Safety preemption from every state.** Safety outranks commands, outcomes, observations and timers. The kernel conformance suite proves preemption from every local state of every registered experience ([[C2-the-conformance-ladder]]). In the umbrella architecture the software path is explicitly *additive*: the guaranteed stop is a hardware relay in series with the emergency-stop loop, and no state in any software machine is load-bearing for the safety case. A paused robot leaves the pause only through staff reset plus safety clear, into cleanup — never directly back into service, and never because of a visitor event.

**Arbitration among outputs.** Overlaps are decided by resource claims and one closed conflict matrix ([[B3-the-effect-vocabulary]]): the action slot defers or preempts by authority priority; gaze refuses a lower priority and replaces at equal or higher priority after the prior clear succeeds; an audio-out conflict is refused. No primitive or experience may override the matrix. Safety priority is reserved for the kernel.

**World conditions are not story events.** In simulation, a visitor control (accept a handshake, choose a gift, take the gift) changes only an eligible condition in the simulated world. It never declares handshake, receive or give success. The rule in the simulation design reads: a visitor control may change an eligible simulated-world condition, but only the production controller and the coordinator's admission path may change the story ([[C1-simulation-first]]).

## Design choices and trade-offs
- **A single worker** gives determinism and simple reasoning at the cost of throughput. A public interaction produces few events per second, so throughput is not the constraint; replayability is.
- **Rejection, not deferral.** An event for a visitor who is not (or not yet) the participant is dropped, not queued. Queuing would let content from one visitor reach the next.
- **The kernel owns what "fails closed" means.** Missing data is never replaced by a default "ready"; an unknown source is rejected before it enters the queue.

## Common confusions
- **"The experience can catch a safety event and finish its line first."** It never sees the safety event before the kernel has acted on it.
- **"Priority order means safety events skip validation."** They are still typed and admitted; they simply sort first and are handled by the kernel.
- **"Software safety makes the robot safe."** Hardware is the safety guarantee. Software preemption is an additional layer that makes the experience behave well when hardware acts.

## Why it matters for robot experiences
The rules that protect a visitor must not depend on every story author remembering them. Interception puts those rules ahead of every story, and ordered admission makes the result the same on every replay.

## Terms introduced
- **interception** — the kernel handling a class of events itself before, and instead of, delegating them to the experience.
- **admission** — the kernel's checks that decide whether an event may enter the queue and reach the reducer.
- **event context** — the correlation and timing fields every event carries: source, sequence, times, clock domain, epoch, uncertainty, session, generation, command.
- **total order** — a sequence of events that every replay reproduces, built from priority and deterministic tie-breaks.
- **preemption** — a higher-priority authority taking a resource or the flow from a lower one.
- **conflict matrix** — the kernel's closed rules for which resource claims may coexist, defer, preempt or be refused.
