# B1 — The pipeline: where an LLM is, and where it is not

**Source:** internal interaction-layer, component-flow and as-built stack documents I4, and the scripted-act debrief I2 (see [`../SOURCES.md`](../SOURCES.md)); Skantze 2021 for turn-taking components; Kelley 1984 for the Wizard-of-Oz method. · **Status:** concept primer; numbers are labelled illustrative.

## In one sentence
A public robot's voice runs microphone array → voice activity detection → a speech-to-speech reasoner → speaker, but only one box in the whole stack is a language model; perception, the engage trigger, the body and the gaze are plain code, and the open design question is whether the model or a deterministic coordinator decides the order of the visit.

## What it is
**Voice activity detection (VAD)** decides when someone is speaking. **Automatic speech recognition (ASR)** turns speech into text. **Text-to-speech (TTS)** turns text into speech. A classic **cascade** chains VAD → ASR → LLM → TTS. A **speech-to-speech model** replaces ASR, LLM and TTS with one model that takes audio in and gives audio out; the realtime variants also run VAD on the server and support function calling (Skantze 2021 surveys both designs).

The sources contain two designs side by side:

1. **On-rails dialogue (designed first).** Microphone → ASR → a small local LLM inside each beat → TTS plus a gesture id. The LLM is a component inside a beat, never the flow controller.
2. **Speech-to-speech reasoner (as built).** One cloud realtime speech-to-speech session is the voice *and* the sequencer. Greet → chat → ask → offer emerges from the prompt plus a handful of tools.

## How it works

### The components as built
Five components on two computers (the robot's on-board computer and a compute box inside the stand), connected by a publish/subscribe robot middleware.

| Component | Is it an LLM? | Role |
|---|---|---|
| Visitor perception | No | Small vision and audio models (face detector, face embedding for an anonymous session id, active-speaker detection, voice embedding) plus direction-of-arrival fusion and plain state machines (absent → arming → engaged). See [[B2-who-is-speaking]]. |
| Engage trigger | No | One deterministic edge: when perception says a visitor is engaged, send one system message telling the reasoner to greet. Cooldown, re-arm on idle, wake-word precedence, fail closed if perception is stale. |
| **The reasoner** | **Yes, the only one** | A realtime speech-to-speech model: audio in and out, server VAD, function calling. It is also the only "vision": it receives a camera frame per utterance. Wrapped by a local wake-word gate, a **triage** session that decides per utterance whether to answer, a barge-in guard, context compaction and tracing. |
| The behaviour library | No | A behaviour tree at an illustrative 100 Hz (`behaviour_tick_illustrative`) with blended priority layers. Face lights, eyebrows and a nod follow the speaker's output level while the robot talks. |
| Gaze controller | No | Active-speaker bearing → a gaze policy → head-pose command. See [[B3-gaze]]. |

Behaviour is written in different places for each: thresholds in code for perception; a small code file for the trigger; a stack of prompt files for the reasoner (base identity and safety ← stand profile ← one file per ability, where adding a capability is a configuration file, not code); code and configuration for the body.

**Triage** deserves a definition: it is a second LLM decision on each utterance, "accept or ignore", so side talk and bystanders are not answered. It is fed perception's evidence ("directed at the robot, visitor 2").

### One visitor, end to end
1. **Approach.** Head-camera frames stream to the stand computer; perception tracks a face as "visitor N"; distance, bearing and dwell together mean "engaged".
2. **Trigger.** The engage trigger sends one system message: a visitor has walked up, greet them.
3. **Greet.** The reasoner speaks a one-sentence greeting; the body animates from the output level.
4. **Converse.** The visitor answers; triage accepts; gaze follows the active speaker; the reasoner state cycles listening → user speaking → triaging → executing → robot speaking.
5. **Gesture.** "Give me a high five" → the model calls a gesture tool → the behaviour plays → the tool returns on completion → the model stays silent ("the behaviour is the response"). See [[B5-behaviours-from-language]].
6. **Offer.** "Can I have one?" → "go ahead and grab one" (self-serve).
7. **Wind-down.** The reasoner never returns to idle by itself after a chat; it sits in listening. Every consumer must infer "conversation over", for example after an illustrative 5 s of quiet listening (`wind_down_quiet_illustrative`).

### On-rails versus open conversation
In the on-rails design each beat gets the current state, the expected intents, an optional scene hint and a strict output schema: an `intent` from a per-beat set (receive-gift, chitchat, decline, unclear), a `line_id` from an approved pool or guarded text, an optional `pose_id`, and a confidence. In the greet beat the model can only greet or route. Off-topic or unsafe input maps to `unclear` and a canned reprompt.

| | On-rails | Open (speech-to-speech) |
|---|---|---|
| Robustness in noise | high | lower |
| Latency | near zero for canned lines | one model round trip |
| Surprise | none | some |
| Auditability | every sayable line enumerable, testable in continuous integration | not enumerable; safety is measured, not proven |
| Charm | repetitive without pools | varied, "no two conversations the same" |

A likely posture under crowd noise is a **hybrid**: canned openers, live follow-ups. A **voice pack** of pre-rendered lines (attract, greeting, celebrate, goodbye, error) is always available as a floor.

### Reasoner as sequencer, or a coordinator
- **(A) Reasoner as sequencer** (what ran live): the model holds tools for gestures and vision and decides order. To extend it, add an ability file.
- **(B) Deterministic coordinator, reasoner as voice only:** a coordinator supplies the beat, the allowed intents and a turn budget, and owns every physical action. The reasoner has no physical or visual authority.

The live runs are evidence for (A). Two seams remain open for (A): **audio ownership during a beat** (when a scripted beat plays its own audio, something must hold the reasoner's mouth) and **the completion signal** back to the model (so it neither talks over nor moves during a beat). At a hand-over to scripted beats, the reasoner once spoke almost simultaneously with the scripted audio, because both wrote to the same speaker and nothing held the reasoner.

### Degradation
An automatic, fail-closed audio ladder: open microphone with full duplex → open microphone with half duplex (microphone closed while the robot speaks, if acoustic feedback cancellation is insufficient) → push-to-talk → canned lines plus gesture driven by a hidden operator. The last rung is the **Wizard-of-Oz floor**: a human operator triggers each step, and the visitor cannot tell (Kelley 1984 named the technique). A cloud call is never awaited on the critical path; a stall falls back to a canned line from the beat's pool. See [[C1-failure-and-degradation-ux]].

### Design invariants from the component flow
- Camera data stays inside the stand; only processed outputs (bearings, flags, actions) cross to the robot.
- **Visitor context enriches conversation, not control.** Mood or clothing may shape a line, never a state transition.
- A safety supervisor sits above the state machine and pre-empts any state; the hardware power cut is never a software call.
- The robot gateway exposes a few intent-level verbs (speak, play pose, look at, hand over, cancel, health). Free conversation stays off that seam.

## How it is designed and tested
- Write the rendered prompt to a file at start-up and check that each ability is present, instead of inferring it from behaviour.
- Count publishers on the reasoner-state topic at bring-up: exactly one. A second publisher (for example a scripted-act sidecar) produced conflicting states.
- Log every state transition with a reason; consumers act on transitions, so a missing one is a stuck robot.

## Common confusions
- **"The robot is an LLM."** One component is. The parts that keep the robot safe and on time are not.
- **"Speech-to-speech removes the state machine."** It moves it into the prompt, where it is harder to test; termination and "a no is a no" still need a check.
- **"Idle means the conversation ended."** The reasoner may never publish idle; infer the end.

## Why it matters for public-robot interaction
Knowing which box is the language model tells you where to spend testing: the deterministic parts can be proven with unit tests; the model's behaviour must be measured live (see [[C2-the-validation-ladder]]). The split also bounds the blast radius: a model mistake can produce an odd sentence, but it should never move a motor without passing through a validated interface.

## Terms introduced
- **voice activity detection (VAD)** — deciding when speech is present.
- **ASR / TTS** — speech-to-text / text-to-speech.
- **cascade** — a VAD → ASR → LLM → TTS chain of separate components.
- **speech-to-speech model** — one model that takes audio in and gives audio out, optionally with server VAD and function calling.
- **on-rails dialogue** — an LLM used inside one beat with a fixed intent set and output schema.
- **triage** — a per-utterance LLM decision to accept or ignore the input.
- **engage trigger** — the deterministic rule that tells the reasoner to greet an engaged visitor.
- **ability (prompt file)** — a configuration file that adds a capability to the reasoner (prompt text plus tools).
- **reasoner as sequencer / coordinator** — the model decides the order of the visit / a deterministic layer decides and the model only speaks.
- **voice pack** — pre-rendered lines available without the model.
- **Wizard-of-Oz floor** — the fallback in which a hidden human operator drives each step.
- **robot gateway** — the component that exposes intent-level verbs to the robot and is the only one that talks to the robot middleware.
