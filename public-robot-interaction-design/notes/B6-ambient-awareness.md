# B6 — Ambient awareness: noticing without being asked

**Source:** internal ambient-perception and attribution designs I6, opening-greeting design I3 (see [`../SOURCES.md`](../SOURCES.md)); Hall 1966 for proxemics; Bohus & Horvitz 2009. · **Status:** concept primer; numbers are public or labelled illustrative.

## In one sentence
Turn raw perception into a small set of anonymous events (someone is here, approaching, engaged, speaking from there, leaving), let only those events drive transitions, keep every richer observation as an optional hint off the critical path, and price each false positive before acting on it.

## What it is
**Ambient awareness** is what the robot notices without being asked: that someone slowed down, that a group arrived, that a voice comes from off camera, that the visitor walked away. In open-world terms it is the engagement model: deciding whom to engage and when, from cues people give off rather than commands they give (Bohus & Horvitz 2009).

The design converts perception into a **semantic event contract**, a small set of typed events, not pixels:

| Event | Meaning | Drives |
|---|---|---|
| present{count, zones} | at least one person in the engagement arc | attract → greet |
| approach{track, distance} | someone is coming closer | greet |
| primary{track, bearing} | whom to engage (first release: nearest) | greet target |
| departed{track} | the primary left | goodbye |
| attention{track, engaged} | facing the robot or walking away | later release |
| active_speaker{bearing} | where speech comes from | continuous gaze |
| child_present{likely} | a size heuristic, not identity or demographics | later release |

All ids are anonymous and visit-scoped ([[A3-consent-and-privacy-by-design]]). The engagement arc in this kit is an illustrative 120° (`engagement_arc_illustrative`). Distances map onto public proxemic zones: personal 0.45–1.2 m and social 1.2–3.6 m (`proxemics_personal`, `proxemics_social`, Hall 1966); a counter conversation happens at the near edge of the social zone.

## How it works

### Select whom to engage
An uninterested passer-by, who does not slow, look or enter the approach path, gets no greeting, no wave and no head-chase. An interested visitor (looks, slows, approaches) gets head-up, a turn, eye contact, a brighter face and one wave. A robot that greets everyone is needy; a robot that greets no one is a prop.

### A small first release, wide seams
The first release used presence, distance and bearing from one camera, plus the active-speaker bearing. The active-speaker signal was first deferred on the argument "push-to-talk tells us who spoke". The move to an open microphone made that argument false, because nothing else identified the speaker, so the signal came back in scope. The later rows (attention, child present) have interfaces now so no seam changes later, but are not built: "do not build them for the first release".

### Hand a target, not a gaze command
Stand perception decides "there is a primary visitor at this bearing". The robot's own camera and gaze policy take over the fine aiming ([[B3-gaze]]).

### Off-camera voices are an ambient cue
When directed speech arrives with no face at its bearing, the robot notices and makes one acquisition glance toward the sector, time-boxed to an illustrative 3 s (`sector_glance_box_illustrative`). An operator can confine the allowed sector or turn the behaviour off live, because rear reflections and coarse bins can produce spurious "someone is behind me" cues.

### Enrichment stays off the critical path
Later ideas include crowd density (throttle optional beats when busy), an aggregate delight proxy (tune celebration intensity), and scene captions for varied banter. All are best-effort, feature-flagged, and **never on a transition gate**. A caption is a context hint, still bounded by the beat's vocabulary. A captioning stall never blocks a transition; the coordinator proceeds on hard signals with a timeout. Enrichment is the first thing turned off under compute load.

The opening remark on what a visitor wears is the most visible piece of enrichment ([[C2-the-validation-ladder]]). Two rules from it generalise:
- **Never describe what you were not shown.** A perception-triggered greeting once went to the model without an image; the instruction "comment on something they wear" became, on a blind turn, an instruction to invent, and the robot praised a backpack that did not exist. The fix pairs a prompt rule with a per-turn statement of whether an image accompanies the turn.
- **When unsure, skip.** A greeting with no observation is a good outcome.

### The cost of false positives
The core teaching is that the price of an error depends on the decision:

| Decision | False positive costs | False negative costs | So |
|---|---|---|---|
| answer this speech? | an odd reply, recoverable | ignoring an engaged visitor, not recoverable | lean accept |
| who said it? | wrong identity carried forward, extra tokens, lost continuity ([[B2-who-is-speaking]]) | a turn without a name | strict; abstain |
| show a name on an image? | a wrong label in front of the visitor | a blank label | label only when sure |
| bank a new voice? | a polluted cluster that corrupts every later match | recognition one turn later | strictest gates |
| "a voice with no face" (bystander reject) | ignoring a real off-camera visitor | answering a phone | strictest predicate; only when the sensor is truly fed |
| scene caption | an odd line | a plainer line | best-effort, never a gate |
| greet a passer-by | needy robot, noise for the queue | a missed visitor | require slowing or looking |

An unfed sensor that asserts "no face at that voice" fabricates a false positive. The design therefore treats a sensor's capability as "exists *and* is fed", and makes thread death flip it within one tick.

### Crowds
Above an illustrative 8 people (`crowd_coarse_zone_illustrative`) the bearing cones overlap and fine attribution saturates. The design falls back to coarse zones (left, centre, right of the counter), lets mouth motion pick the talker within a zone, and addresses the group. Over-reaction is a real cost; coarse honesty beats pretended precision.

### Failure behaviour of the perception feed
- A silent microphone stream once froze a synchronous audio-video merge (no frames, no error). Fix: synthesise silence after a grace period with one warning.
- A stalled camera was masked by a replayed seed frame. Fix: end the stream after a stall timeout and degrade to voice-only. Frames cannot be honestly fabricated.
- Directedness cues flicker (a visitor glances away while thinking). Smooth with N-of-M persistence over the utterance and weight orientation at speech onset most.

## How it is designed and tested
- Count spurious greetings per hour and walk-pasts that were greeted; count missed engaged visitors. Report both.
- Replay recorded scenes with each enrichment feature off and on; transitions must be identical.
- Kill each perception feed during a replay; the event contract must report the loss within one tick and the experience must degrade, not freeze.

## Common confusions
- **"More perception makes the robot smarter."** More perception on the transition path makes it more fragile. Keep rich perception as hints.
- **"A false positive is always cheaper than a false negative."** True for answering, false for identity.
- **"Child detection lets us adapt content."** The design makes content child-safe for everyone instead, and uses size only for reach and operator help.

## Why it matters for public-robot interaction
Ambient awareness produces the "it noticed me" moment that makes a stand work. Done as a small, typed event contract with priced errors, it stays robust in a crowd and respects privacy; done as open-ended perception wired into control, it produces a robot that reacts to the wrong things.

## Terms introduced
- **ambient awareness** — noticing relevant events without a request.
- **semantic event contract** — a small set of typed, anonymous perception events that drive the interaction.
- **engagement arc** — the region in front of the stand in which an approach counts.
- **primary visitor** — the visitor the robot engages first.
- **proxemics** — the study of interpersonal distance zones (Hall 1966).
- **enrichment** — optional perception output used as a context hint, never as a transition gate.
- **fed capability** — a sensor that both exists and currently delivers data.
- **coarse zone fallback** — replacing fine bearings with left/centre/right zones in a crowd.
