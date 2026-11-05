# B5 — Behaviours from language: how an LLM asks for a gesture

**Source:** internal behaviour tool-calling design and turn-taking investigations I7; component-flow and scripted-act documents I2, I4 (see [`../SOURCES.md`](../SOURCES.md)). · **Status:** concept primer; numbers are labelled illustrative.

## In one sentence
When a language model triggers a gesture by naming it, the id must come from the live behaviour registry and reach the model through the prompt, the tool schema and a self-correcting error, the call must really reach the robot, and every rejection must be logged, because otherwise the robot says "sure" and stands still while every test passes.

## What it is
A **tool call** (function call) is a structured request a model emits instead of, or alongside, speech: `request_behavior(behavior="<id>")`. A **behaviour** is a named gesture or pose in **the behaviour library** (wave, nod, high five, face expressions, body poses, hand-over moves). The **id-namespace contract** is the agreement on which strings are valid ids, who owns the list, and how consumers learn it.

The observed failure: a visitor said "can you wave at me?", the robot answered in voice, sometimes describing the gesture or reading an internal error aloud, and did not move. No crash, no alarm, no failed health check; it worked on a laptop and failed only on hardware.

Why it is a design problem:
- **It is silent.** A rejected gesture looks like a model that chose to talk.
- **It passes in development and fails in production.**
- **It generalises.** Any tool whose argument is a string from a runtime-discovered set has the same exposure.

## How it works

### The path
Speech → the reasoner → `request_behavior(id)` → a tool executor → an HRI service (a real client, or a development double) checks `id ∈ available ids` → a behaviour request to the behaviour library → motors. In the other direction the library publishes its list of available ids once, on a latched topic. Two facts follow:
- **The vocabulary is discovered at runtime, not compiled in.** The library builds its registry per robot body type. An illustrative newer generation exposes 25 ids and an older one 4 unrelated ids (`behaviour_ids_new_illustrative`, `behaviour_ids_old_illustrative`). Any hard-coded list is wrong on some robot.
- **The model is the component that chooses the string.** Every other link forwards it.

### The id contract
- **Naming is irregular** (a prefix on some ids and not others; "shake" meaning a head shake, not a handshake). No transformation maps an English gesture name to an id. **"The list must be transmitted, never inferred."**
- **Advertised is not executable.** Hand-over behaviours appear in the list but fail when their precondition (a grasp state) is not met. A rejection of a valid id is normal.
- **The empty-list window.** Before the first list arrives, every id is invalid, including correct ones. If the library is not running, the window never closes.

### What actually happened (traced, not guessed)
The reasoner was bound to a **dummy** service, set on purpose because of a message-definition mismatch: the robot published a three-field state message and the team's pinned definitions had four. Under the middleware, a type mismatch **silently blocks data**, so with the real service the list stayed empty forever. The dummy advertised a hand-written list, the model chose an id from it, the tool returned "success" in an illustrative 10 ms (`dummy_success_latency_illustrative`), and nothing reached the robot.

Two corrections matter more than the defects. **The model was neither at fault nor uninformed**: putting the list in the prompt would have changed nothing, because it was the same wrong list. And **the failure was reported as success**. Earlier speculative rankings of causes were wrong; trace the live path before ranking causes.

### The latent defects
1. The development double advertised names a person assumed the robot would accept, so the model's natural-English guess was rewarded in development. That inverts the purpose of a test double.
2. Nothing told the model where the vocabulary lived.
3. The tool argument was a bare string with no description, and the rejection did not name valid alternatives.
4. Tool errors returned as text with no handling rule, so a voice-first model read them aloud, leaking internals to guests.

A legacy cascade stack never had the bug, by design: it never let the model choose a behaviour id; every set the model did choose from was listed in the prompt; and errors fed a bounded retry loop (an illustrative 10 planning turns, `legacy_retry_turns_illustrative`), not the speaker. A tool in the current stack that played a handshake from a configured constant worked on the robot. "The variable that decides success is not the execution path; it is who supplied the string."

### Six layers
Principle: **a model must never be asked to guess a string that a machine can enumerate.**

| Layer | What it does |
|---|---|
| L0 the path reaches the robot | no dummy on hardware; message definitions match the robot (a pre-deploy diff that is a gate, not a warning); until then, say "gestures are not wired", not "the model is wrong" |
| L1 dev/prod parity | the double advertises exactly the registry at the pinned upstream revision, enforced by a test |
| L2 vocabulary in the system prompt | the live list substituted into the context description, so it survives compaction and is present before the first call |
| L3 the tool declares its contract | the argument schema says "an exact id copied from the list, not an English name", with examples of *form*; deliberately not a static enum |
| L4 self-correcting, silent to the guest | validate before dispatch; the error lists valid ids; one retry; never read error text aloud |
| L5 telemetry | every rejection logged with correlation id, attempted id, the available set and the outcome |

Which layer catches what: a plain-English guess is prevented by L2 and recovered by L4; a renamed id fails the L1 test loudly and auto-updates in L2; the empty-list window is distinguished only in L5; **chronic degradation, where L4 repairs every request, is visible only in L5**; a dummy or a message mismatch is fixed only by L0 and revealed only by L5.

### Skew when the library changes underneath
The stand runs a pinned upstream revision; the robot updates on its own channel.
- **Message-level skew is fatal**: deserialisation fails and the vocabulary is absent. Only L0 catches it.
- **Vocabulary-level skew is survivable.** L2 and L4 read the live list and self-heal; L1 and L3 are pinned and advisory. So L3's examples show form, never the list.

A later twist: the platform added the missing field, so the team's compatibility overrides became the mismatch. The overrides were checked against the *compiled* type inside the platform image, because an install path without a type-hash check could leave an override silently inert. Lesson: **a compatibility shim needs a written exit condition and a check that fires when it is met.**

### Alternatives rejected
- A static enum: wrong on other bodies, stale on any change.
- Hard-code the list in the prompt: stale and duplicated. A short intent → id hint list is allowed.
- Fix upstream: consumed read-only; a review cycle would block the fix.
- Scripted gestures only: removes the conversational gesture the stand is built around, but stays the right fallback for the Wizard-of-Oz floor.
- Validate in the robot gateway: right long-term, but the gateway was not on this path.

Long-term, the gateway owns the semantic → id mapping: show beats name gestures semantically ("greet", "celebrate") and the gateway resolves them against the live registry, showing the empty-list window on its health surface.

### The hand-over moment as choreography
The sources treat the gift moment as where interaction and manipulation meet.
- **Self-serve (current):** the robot speaks the offer, turns its head and later points to the tray, and the visitor takes the gift. Only speak, look-at and pose verbs are used. Take evidence grows in steps: a fixed take timer (an illustrative 12 s, `take_timer_illustrative`), then tray perception that sees the count drop. The single authoritative "complete" event is synthesised by the coordinator.
- **Robot hand-over (later):** ease to a hand-over pose → torque-controlled grasp → hold until the visitor pulls → release. **Velocity-based release is primary; vision may raise confidence or veto, never trigger release.** Recovery keys off the reason: grasp failed, item missing, no take, dropped.
- In a scripted act a change of mind mid-reach ("actually, the green one") needed a policy interrupt that no learned motion supported, so that beat stayed scripted.
- Gaze during the hand-over frames the recipient, not the talker ([[B3-gaze]]). The robot looks at the work during the pick and restores eye contact *before* extending the arm.
- The high five became the first contact-driven beat: it completes on touch, not on a timer. The pattern named for it: **animation first, sensing second, policy third.**

## How it is designed and tested
- **The load-bearing check:** with parity applied and nothing else, a local gesture request must **fail**, reproducing the robot's failure off-robot. "A fix verified only by the final test cannot distinguish 'we fixed it' from 'the double was always permissive'."
- The built prompt contains the literal ids; an unknown id produces an error naming alternatives; a nonexistent gesture produces one retry and a spoken decline.
- On the robot: **the behaviour library's log is the proof, not the tool's return value.**

## Common confusions
- **"The model hallucinated the id."** Here the model obeyed the list it was given; the list was wrong and the call never left the machine.
- **"Success returned means it moved."** A dummy returns success instantly.
- **"An enum is safer."** Only if the set is fixed; a runtime set needs runtime delivery.

## Why it matters for public-robot interaction
Gestures land the moments that make a robot feel present. A gesture path that fails silently produces the worst shape of failure for an unattended demo day: the robot looks fine, talks fine, and quietly does nothing.

## Terms introduced
- **tool call (function call)** — a structured request a model emits to run code.
- **behaviour library** — the robot-side component that owns and plays named gestures and poses.
- **behaviour id** — the exact string naming a behaviour in the registry.
- **id-namespace contract** — the agreement on valid ids, their owner, and how consumers learn them.
- **empty-list window** — the period before the registry arrives in which every id is invalid.
- **test double / dummy service** — a stand-in for a real service used in development.
- **message ABI skew** — two sides disagreeing on a message's compiled layout, which can silently block data.
- **compatibility shim** — a local override that bridges a version difference until upstream catches up.
- **self-serve hand-over** — the robot offers and points; the visitor takes the gift.
- **velocity-based release** — releasing a held item when the arm senses the visitor's pull.
