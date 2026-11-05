# C4 — The observatory: running the real behaviour and conversation stack without a robot

**Source:** generalised from internal design and planning documents (see [`../SOURCES.md`](../SOURCES.md)); ROS 2 documentation, "Quality of Service settings" (request-versus-offered compatibility), https://docs.ros.org/en/kilted/Concepts/Intermediate/About-Quality-of-Service-Settings.html . · **Status:** concept primer. Every number is labelled illustrative.

## In one sentence
An **observatory harness** runs the real behaviour engine and the real conversation stack off the robot — against deterministic fixtures, a live cloud model, or a cloud host fed by a laptop browser — and renders the robot's face, head and body from their command output, or, in a separate read-only mode, observes a real robot; it measures integration and developer usability, and it is stamped "harness only" so its evidence is never mistaken for product evidence.

## What it is
The observatory is a development loop for the robot's *embodiment*: face lights, eyebrows, conversational head motion, arm gestures and the 3D body. It is not a robot simulator and not a product safety test. Its **actuator twin** displays synthetic command intent; it does not simulate dynamics, contact, torque, balance or measured motion. (The physics simulator of [[C1-simulation-first]] is the place for those.)

The plans separate the modes cleanly.

1. **Core fixture.** Deterministic, offline, isolated. No cloud, microphone, GPU, robot or production credentials. This is the mandatory CI and developer seam.
2. **Live cloud audio.** The real speech-to-speech model through a headset or a browser microphone, with a fail-closed audio gate that bounds what can leave the host.
3. **Real observer.** A secured, subscribe-only view of a physical robot. It contains no command producer and no synthetic publisher, and it is a separate deployment project, not an extra profile of the fixture.
4. **Cloud session cell.** The same release bundle on a private cloud GPU host, with a laptop camera and microphone streamed in through a browser and the robot rendered in the same page.

## How it works
**Replaying sessions and fixtures.** The core fixture feeds recorded or scripted inputs through the real behaviour engine. A deterministic fixture is the regression test; it is never presented as the shipping conversation path.

**Running the reasoner off the robot.** The live modes run the real reasoner container with a minimal profile: inherited tools and context cleared, and only what the harness needs. A behaviour ability that exposes the global registry is allowed only here, and only through a filtering proxy that permits a single behaviour ID ([[B6-conversation-and-model-boundaries]]).

**Sole writers.** The composition preserves one writer per authority: the audio gate is the only writer of canonical microphone input; the output broker is the only writer of robot audio and stop; the proxy is the only path from the reasoner to the behaviour engine. These are the same seams the product kernel later owns, so the harness exercises them early.

**Isolation is a stronger property than a separate domain.** The fixture graph publishes the real motor-command topic once dispatch is unlocked, so middleware domain separation and a deny-list are not treated as a safety boundary. The plan puts command-capable services in a private network namespace with no published router port, discovery scouting off, and default-deny outbound traffic; the live mode adds only one audited egress path to the model provider. The plan notes that the inherited isolation pattern isolated discovery only and still allowed outbound internet by default, so the egress denial was new work.

**QoS mismatches are caught at start-up.** One audit finding: a metrics publisher offered best-effort reliability while its subscriber requested reliable. In ROS 2's request-versus-offered model, a best-effort publisher and a reliable subscription are incompatible, so no messages flow (ROS 2 QoS documentation, "QoS compatibilities"). The harness relays the stream with a compatible profile, and endpoint tests compare offered and requested QoS separately.

**One release bundle.** A session consumes one lock file naming the source commit, per-platform image digests, message type hashes, asset and mesh digests, model hashes and host stack versions. The launcher rejects mixed commits, mutable tags, or images whose embedded message labels disagree. "Same image" across an ARM robot and an x86 cloud host is not possible where the base stack differs; the parity unit is one multi-architecture image family, or the same source and entrypoint built for each platform.

**Bounded, private cloud sessions.** Each cloud session cell has its own middleware domain, router, project name, browser-session identity, evidence directory and lifetime: an illustrative 2 h maximum (`observatory_session_ttl_h_illustrative`) and an illustrative 20 min idle timeout (`observatory_idle_min_illustrative`). Browser timestamps and requests are advisory; the server mints identity, validates bounds and owns teardown. Audio, video, transcripts and tool arguments are not persisted by construction, and acceptance checks that none appear in disks, logs or crash dumps after a session.

**What the observatory measures.** Its acceptance gates are integration and usability claims: the real behaviour engine reaches ready with no robot; one synthetic turn produces brokered reply audio and changing face, head and body output; joint snapshots animate the commanded joints; stale and malformed states are visibly distinct; media disconnect, tab close and lifetime expiry each stop tracks and wipe buffers; repeated start–talk–stop cycles pass without restart or retained content; two consecutive sessions do not match a visitor enrolled in the first.

## Design choices and trade-offs
- **Fixtures before physics.** Physics changes failure modes, start-up time, GPU sizing and clock ownership without being necessary to prove the conversation and behaviour loop. It is a later phase that replaces the actuator twin as the joint-state authority.
- **A synthetic soak is not the robot soak.** The plan states that a long synthetic run is useful software evidence but must not be presented as the physical endurance or hardware-in-the-loop gate.
- **The browser is an untrusted edge.** Treating client data as advisory costs some server work; it removes a class of spoofing.

## Common confusions
- **"The observatory and the simulation are the same thing."** The observatory renders command intent with no physics; the simulation runs the coordinator against a physics body and room.
- **"A clean observatory run is product evidence."** Every artifact is stamped harness-only; product authority, hardware safety and on-robot audio gates stay explicitly out of scope.
- **"A separate middleware domain isolates the graph."** Domain separation limits discovery; it does not stop commands or outbound traffic.

## Why it matters for robot experiences
Most bugs in a conversational robot live in the seams between speech, behaviour and display. An observatory lets a developer hit those seams on a laptop every day, and its strict labelling keeps that convenience from leaking into safety claims.

## Terms introduced
- **observatory harness** — the off-robot loop that runs the real behaviour and conversation stack and renders the robot from command output.
- **actuator twin** — the harness component that turns behaviour commands into displayed joint state, with no dynamics.
- **core fixture** — the deterministic, offline, isolated mode used as the CI seam.
- **real observer** — the separate, subscribe-only mode that views a physical robot.
- **session cell** — one isolated cloud session with its own domain, router, identity, evidence and lifetime.
- **harness only** — the provenance stamp that marks evidence as not valid for product claims.
- **release bundle (lock)** — the file that pins every image, message hash, asset and model used by a session.
- **QoS (quality of service)** — ROS 2 delivery policies (history, depth, reliability, durability, deadline, lifespan, liveliness) matched by a request-versus-offered rule.
