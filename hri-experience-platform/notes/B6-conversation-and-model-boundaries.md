# B6 — Conversation and model boundaries: what the model is told, may ask for, and can never touch

**Source:** generalised from internal design documents (see [`../SOURCES.md`](../SOURCES.md)); OWASP Top 10 for LLM Applications 2025, LLM06 "Excessive Agency" (https://genai.owasp.org/llmrisk/llm062025-excessive-agency/). · **Status:** concept primer. Every number is labelled illustrative.

## In one sentence
The model gets a small per-phase context and no physical tools; it returns audio plus a typed, allowlisted turn result; every ID that could carry authority is minted on the trusted side, every requested act is grounded in the catalog and revalidated at dispatch, and chat is a bounded sequence of turns, each with its own speech-output lease that must stop before the next turn may speak.

## What it is
Three boundaries surround the reasoner.

1. **Configuration boundary.** Prompt, script, voice and wording changes are conversation-profile configuration. A different sequence of beats or a different physical decision is a different *experience*. Model output at run time must never select an experience, a state, a primitive or a command.
2. **Capability boundary.** The approved reasoner profile pins the model identity and has empty tool, context and ability sets, with camera images not sent on speech. Readiness attests the resolved runtime profile against the pinned one; any mismatch fails readiness. Checking the source file is not enough, because what runs can differ from what is checked in.
3. **Output boundary.** The model may produce audio and a bounded typed turn result: an intent, a terminal speech status, an ephemeral transcript reference, and an allowlisted expression suggestion. It must not invoke robot motion. The reducer decides whether an accepted result leads to another turn, a registered primitive, or cleanup ([[A1-the-reasoner-and-the-coordinator]]).

## How it works
**Chat is bounded turns, not one open session.** The chat chapter runs repeated conversation turns under one kernel-owned conversation session. Each turn has an intent list and a time budget, and the session has a bound. In the example chat experience: an illustrative 3 turns (`chat_turns_illustrative`), an illustrative 8 s per turn (`chat_turn_budget_s_illustrative`), and an illustrative 60 s session bound (`chat_session_bound_s_illustrative`). The bounds are consistent: 3 × 8 s = 24 s of turn budget fits well inside 60 s, which leaves time for the visitor's replies and the robot's other beats (my arithmetic).

**Two audio authorities, never one record.** Listening and speaking are separate.

- The **visitor-audio permit** is kernel-owned input authority. It may span turns.
- The **speech-output lease** is per turn. One lease authorises exactly one turn's stream. That stream must stop, give positive terminal evidence, and release audio out before the next turn can acquire its lease. Every audio frame is authorised against the lease before playback. Barge-in cancels the current turn's stream; it never lets that stream become the next turn's output.

**One canonical voice path.** The design selects one live conversation path: the realtime speech-to-speech model plus a coordinator-owned output broker. The robot's own text-to-speech stays available for canned lines and reviewed composites, but it is a physical action that occupies the action slot ([[B3-the-effect-vocabulary]]). The scripted fallback for chat uses the same brokered carrier with fixture content. If that carrier is unavailable, chat fails closed to a no-voice display and bounded cleanup. The runtime must never silently switch to the text-to-speech path, because that would acquire the action slot without review.

**Duplex depends on a measurement.** Full-duplex barge-in (the microphone stays open while the robot speaks) is allowed only when a gate passes: with the robot speaking at normal level through its own speakers, the open microphone must not trigger the turn detector on the robot's own voice, under a crowd-noise condition too. Otherwise the same chapter degrades to half-duplex and then to push-to-talk, without changing the experience reducer.

**Grounding requests in the catalog.** The model proposes an act by intent. The coordinator maps the intent to a primitive only if that primitive is on the current phase's allowlist, then the kernel checks the profile, the adapter, the resources and the gates. For a primitive backed by a behaviour-library ID, that ID must be in the configured allowlist *and* in the robot's currently advertised inventory, revalidated at dispatch.

**Skew handling.** Skew is the gap between what the model believes it can ask for and what is really available. The design closes it in four places.

1. The authoring agent's prompt is generated from the contract export of the *pinned image*, never from a document ([[B1-experiences-as-reducers]]).
2. Model-supplied IDs are untrusted. The model's tool schema carries no interaction, turn or generation IDs; the trusted service mints and attaches them.
3. A free-form behaviour tool that exposes the whole behaviour registry is allowed only in an isolated harness ([[C4-the-observatory]]); the product reasoner has only the typed intent tool.
4. Dispatch-time revalidation catches a behaviour that disappeared after readiness.

## Design choices and trade-offs
- **Fewer model capabilities, more natural talk.** Removing tools, context and camera from the model narrows what it can do, but the phase context keeps it fluent, and the coordinator supplies the actions. OWASP's "excessive agency" risk is exactly what the empty tool set removes.
- **Per-turn output leases** cost one stop-acknowledgement round trip between turns. In exchange, two turns can never talk over each other, and a barge-in has a precise meaning.
- **A live model is not a dependency of the simulation milestone.** The deterministic simulation milestone uses a fixture reasoner, so a cloud outage cannot invalidate it ([[C2-the-conformance-ladder]]).

## Common confusions
- **"Changing the prompt changes the experience."** Wording is configuration; only beats and physical decisions define an experience.
- **"The fallback voice is a different system."** The scripted fallback uses the same carrier and lease contract as live chat; only the content differs.
- **"Lease expiry ends the turn."** Expiry stops forwarding; the turn ends only on positive stop evidence.

## Why it matters for robot experiences
A model that cannot reach the motors cannot surprise anyone with them. A model that cannot see stale IDs or a stale catalog cannot ask for something the robot no longer has. What remains is the part visitors notice: a natural conversation.

## Terms introduced
- **conversation profile** — the pinned configuration of the reasoner: model identity, wording, voice, and its empty tool, context and ability sets.
- **profile attestation** — the readiness check that the resolved runtime reasoner profile equals the pinned one.
- **output broker** — the coordinator-owned component that alone writes robot audio and authorises each frame against the turn's lease.
- **barge-in** — the visitor speaking while the robot speaks, which cancels the current turn's stream.
- **full duplex / half duplex / push-to-talk** — microphone open while the robot speaks / open only between robot turns / open only while a control is held.
- **skew** — a mismatch between what the model or its author believes is available and what the pinned system really provides.
- **dispatch-time revalidation** — re-checking a primitive's backing behaviour against the live inventory at the moment of dispatch.
