# C1 — Simulation first: a browser-accessible robot and room as the first target

**Source:** generalised from internal design and requirements documents (see [`../SOURCES.md`](../SOURCES.md)); Cockburn, "Hexagonal architecture", https://alistair.cockburn.us/hexagonal-architecture/ (the simulation replaces adapters, not the core). · **Status:** concept primer. Every number is labelled illustrative.

## In one sentence
The first delivery target is a simulation, not the robot: the same production coordinator runs unchanged while only its surroundings are replaced — a browser supplies camera, microphone and controls, a physics simulator replaces the body and room, virtual actors supply contact and props — so every kernel rule can be proven on a workstation, while the design states plainly what simulation cannot prove.

## What it is
The simulation is an environment *around* the selected coordinator. It does not implement a second story machine. Its design lists what changes:

- browser-local perception replaces the robot's camera-derived visitor observations;
- a browser gateway replaces direct visitor access to robot sensors;
- a physics simulator replaces the physical body and room;
- virtual interaction actors create contact, gift presence and release conditions;
- the real behaviour engine, the real motion layer, the robot middleware and the coordinator's robot adapter stay in the command and feedback loop;
- a streamed simulator viewport and a renderer-neutral state stream replace looking at the robot.

The **simulation-first** rule in the platform design: the first milestone delivers a useful multi-experience platform and a recordable showcase entirely on the simulation target. Robot access, physical adapters and hardware-in-the-loop evidence are later work and must not block it.

## How it works
**Authority boundaries.** The central invariant is: *a visitor control may change an eligible simulated-world condition, but only the production controller and the coordinator's admission path may change the story.*

| Authority | Owner | Explicitly not allowed |
|---|---|---|
| Story state and transitions | the production reducer | browser, UI, scene extension, renderer |
| Behaviour completion | behaviour-engine outcome plus coordinator validation | a popup, an animation finishing |
| Grasp state | the behaviour engine, over reviewed simulated body telemetry | a browser-supplied "holding" |
| Audio forwarding | the coordinator's audio permit and the gateway | microphone permission alone |
| Cleanup completion | the cleanup protocol and clean-store proofs | the page closing |

So "Accept handshake", "choose gift" and "take gift" buttons change only the simulated world. A receive reported as success without a "holding" grasp state is normalised to failure.

**Same mode, isolated target.** The coordinator runs in its real-time live mode, because it consumes live observations and sends real commands. A distinct reviewed simulation deployment identity selects simulation credentials, endpoints, readiness checks and stop semantics. Several checks keep a simulation run from reaching a physical robot: a distinct robot identity and middleware domain, credentials valid only for simulation endpoints, an adapter that requires the simulation target, an identity and ABI fingerprint that must match the simulated stack, no physical route or certificate mounted, and a start-up comparison against a versioned simulation contract. Negative tests prove that simulation credentials cannot satisfy physical validation, and the reverse.

**Single-session ownership.** One visitor at a time.

- Opening a page does not acquire a session; an explicit "start" does.
- Other pages get a privacy-preserving "busy" view. A confirmed "end previous session and start here" revokes the old page through normal cleanup; the new page gains authority only after clean-store proof and a fresh acquisition.
- A dropped application channel revokes input authority at once. The same page may rebind within an illustrative 5 s grace (`sim_rebind_grace_s_illustrative`) with a single-use credential; queued audio and controls are not accepted.
- Only a closed list of meaningful activities renews the visitor inactivity deadline, an illustrative 90 s (`sim_inactivity_s_illustrative`). Heartbeats, raw audio frames, reconnect attempts and tab focus do not, so an abandoned page that keeps sending traffic still retires.

**Separate channels.** The viewport is an encrypted video stream; controls, structured perception, audio and diagnostics use a separate application channel. Every important change also has a versioned, non-video, renderer-neutral representation, for tests, accessibility and a future renderer.

**The native host lifecycle is slow, and bounded.** A physics-simulator cold start to a healthy scene is of the order of an illustrative 600 s (`sim_cold_start_s_illustrative`); launch is bounded by an illustrative 1 200 s (`sim_launch_timeout_s_illustrative`), deliberately larger than the cold start; retirement by an illustrative 300 s (`sim_retire_timeout_s_illustrative`). This is one reason profile validation is serial and why switching is not hot ([[B5-registration-selection-switching]]).

## What simulation cannot prove
The design is explicit, and its list is the most useful part for a reader.

- Approximate simulated grasp evidence validates controller logic; it does not prove contact force or hardware safety.
- Browser monocular depth is an estimate, not collision truth.
- Mechanical regression cannot claim perception quality, conversation quality, social timing or manipulation fidelity.
- A live human run is required for representative acceptance; it is never presented as a CI test.
- Trusted-network security for the simulation is not sufficient for public exposure.

## Design choices and trade-offs
- **Reuse the production brain** rather than fork a simulation story. A fork would drift and would not validate the robot experience.
- **Keep a static facilitator and spawn the gift at the receive pose.** Animating a human hand-over would cost art and control work without testing more of the coordinator.
- **Browser-first perception** with a fallback ladder (GPU in the browser, then CPU or a smaller model) avoids streaming webcam video to the host by default.

## Common confusions
- **"Simulation mode is a different reducer mode."** The reducer runs in its normal live mode; only the deployment target differs.
- **"A green simulation run means the robot is ready."** Physical enablement needs its own adapters, producers and hardware-in-the-loop acceptance ([[C2-the-conformance-ladder]]).
- **"The browser is part of the robot graph."** The browser never joins the middleware and holds no robot credentials; the gateway is its only path in.

## Why it matters for robot experiences
Robot time is scarce and a public visitor is not a test fixture. Simulation first lets a team land and break experiences daily, prove every kernel rule offline, and arrive at the robot with only the questions that need the robot.

## Terms introduced
- **simulation target** — the registered target in which a physics simulator, a browser and virtual actors replace the body, the room and the visitor's devices.
- **browser gateway** — the only component that translates browser input into typed coordinator events; the browser has no other authority.
- **virtual interaction actor** — simulated scene logic that creates world conditions such as contact or a held prop, never story outcomes.
- **renderer-neutral state** — a versioned non-video representation of every important story, action and scene change.
- **single-session ownership** — the rule that one browser page at a time holds visitor authority, transferred only through cleanup.
- **representative acceptance** — an operator-run session with a live human, distinct from mechanical CI regression.
