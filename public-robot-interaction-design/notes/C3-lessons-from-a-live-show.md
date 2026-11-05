# C3 — Lessons from a live show

**Source:** internal scripted-act and debrief documents I2, as-built snapshot I4, and the opening-greeting design I3 (see [`../SOURCES.md`](../SOURCES.md)). · **Status:** a generic debrief; no visitor counts or timings from any real show. Numbers are labelled illustrative.

## In one sentence
A rehearsed scripted act run before autonomy gives a timing baseline, a guaranteed fallback and a list of what the audience actually notices; the first live autonomous runs then show that the seams between components, not the components, are where the robot breaks.

## What it is
This note collects what carried, what broke, and what the team changed after two kinds of live run: **a rehearsed scripted act** (every line pre-recorded, every motion authored, one operator pressing "advance"), and **the first live autonomous runs** (perception-triggered greeting, open conversation, model-chosen gestures). It is written as a generic debrief so the lessons transfer.

## How it works

### What carried
- **Lines keyed by stable ids.** Re-record or drop one line without disturbing the others. The line table is the source of truth for the audio catalogue.
- **The scripted act as a guaranteed floor.** Any beat not ready for autonomy runs exactly as rehearsed, pinned by a contract test that keeps it byte-identical.
- **The same voice for pre-recorded and live lines,** so mixing scripted and live beats is not jarring.
- **Live body behaviour inside a scripted act.** Balance, co-speech gestures and gaze stayed live while lines played, so a fully scripted act still felt alive.
- **A contact-completed beat.** The high five completes on touch, not on a timer: the first beat driven by sensing.
- **A timing baseline.** Every autonomy target is anchored to the act's stopwatch column ([[A2-beats-and-dwell-budget]]).
- **The dance is the beat people film.** It also exercises balance in front of an audience, which is why it got its own clearance rule.
- **Perception-triggered greeting worked live,** with no wake word and no operator. A hand-over from the live opening to scripted beats also worked: the live stack owned the opening, and a supervisor ended it on quiet listening and played the remaining scripted beats.

### What broke or surprised
- **The longest beat ran long.** A staged miss-and-recover reach took an illustrative 80 s (`reach_beat_scripted_illustrative`), twice the target; half of it was the gag.
- **Filler made it worse.** An extra line in the photo beat read as "machine-gun talking".
- **The space was too small.** The counter was too close to dance in place, so the robot now asks for room, steps back, dances, and steps in, with a lab clearance of an illustrative 2.5 m (`dance_clearance_illustrative`) and an emergency stop in hand.
- **Visitors could not find the camera.** The robot now points and looks at it twice, and a live mirror lets people place themselves.
- **A mid-reach change of mind** could not be done by any learned motion, so that beat stayed scripted.
- **The robot described something it had not seen.** On an image-less proactive greeting turn it praised a backpack that did not exist ([[B6-ambient-awareness]]).
- **A fail-closed default made a feature silent.** At the low image resolution that shipped, the greeting never commented ([[C2-the-validation-ladder]]).
- **Unprompted gestures.** During the greeting the robot raised its hand repeatedly in an offering motion; consistent with the model calling the gesture tool because handshake and high five were in its vocabulary and the prompt preferred the tool over describing a gesture.
- **Two voices at once.** At the hand-over from live to scripted, the reasoner spoke almost simultaneously with the scripted audio. Both wrote to the same speaker and nothing held the reasoner ([[B1-the-voice-pipeline]]).
- **The reasoner never returned to idle** after a chat, so every consumer had to infer "conversation over".
- **Two publishers of one state.** A scripted-act sidecar and the live reasoner both published the reasoner state. Solved by an explicit mode switch and a bring-up check for exactly one publisher.
- **A test run opened billed, audible cloud sessions** (see [[C2-the-validation-ladder]]).
- **A perception model ran on the CPU** instead of its accelerator, so the container idled at more than one CPU core.

### What the team changed
- The opening became two action-causing exchanges instead of a three-question interview.
- Reach commentary at a steady cadence; fewer lines and designed silences in the photo beat.
- A clearance rule and calibrated steps for the dance.
- The high five completes on contact.
- The greeting: one image per speech event, a state-machine-owned "opening" occasion, a rule never to describe what was not shown, a per-turn image disclosure, one combined kill switch, and a fail-closed default.
- **Scope decision:** the first public demo focuses on interaction; a physical robot-to-visitor hand-over moves to a later year, with a self-serve tray instead ([[C1-failure-and-degradation-ux]]).
- **Architecture decision:** the next automation phase is built on the live stack, not by growing the scripted player. The open question is reasoner-as-sequencer versus a deterministic coordinator, with audio ownership and completion signals as the seams to settle.
- Proposed: time boxes per beat and per session, a graceful in-character close line, a physical curtain, and a supervisor/director split.

### A debrief template that worked
For each scene: TODAY / WHERE WE ARE GOING / OPTIONS (one chosen, each with its trade) / KPI. Then a scorecard and a "what stays true regardless" slide. Speaker notes carry the honest risks: venue noise is the enemy of live voice; children are out of scope for some features until child-safety work lands; and the privacy line is said out loud ("a state machine over face size and position, discarded per frame").

### Generalisable lessons
1. **Script first, then automate beat by beat.** The scripted act is both the baseline and the fallback.
2. **Seams break before components.** Two-voice overlap, two publishers, a missing "conversation over", a gesture that returned success without moving: each lives between two components that work.
3. **Measure the shipped configuration.** A feature that is safe only because it is silent is not shipped.
4. **The audience notices pacing and gaze before intelligence.** Filler lines, a long reach and a robot that cannot show where the camera is were the visible defects; language quality rarely was.
5. **Write down what stays true.** Safety, privacy and the fallback floor are the commitments that let the team change everything else.

## How it is designed and tested
Run the debrief immediately after the show, while the operator and the audience's reactions are fresh. Fill the stopwatch column from logs, not memory. Turn each "what broke" item into a test at the lowest rung that can catch it ([[C2-the-validation-ladder]]).

## Common confusions
- **"A scripted act is a fake demo."** Framed honestly, it is a baseline and a floor; the debrief says exactly what was live.
- **"The autonomy failed, so roll back."** Most failures were seams with small fixes; the scripted floor kept the show running meanwhile.

## Why it matters for public-robot interaction
Live shows are the only place some failures appear. A team that runs a scripted act first, debriefs with a fixed template and turns each surprise into a test converts one public afternoon into a roadmap.

## Terms introduced
- **rehearsed scripted act** — a fully authored, timed performance with pre-recorded lines and a rehearsed visitor.
- **guaranteed floor** — the scripted version of each beat, used whenever autonomy is not ready.
- **seam** — the interface between two components, where ownership of audio, state or completion must be explicit.
- **debrief template** — a fixed per-scene structure: today, direction, options with trades, KPI.
