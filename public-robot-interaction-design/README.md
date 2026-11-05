# Designing a humanoid robot's conversation with strangers: beats, consent, gaze, attribution, and graceful failure — study notes

**Start here: the story** — [The host at the garden gate](stories/01-the-host-at-the-garden-gate.html): a picture-first, interactive page (about 10 minutes) before the notes.

## In one paragraph

A child-sized humanoid robot at a public demo stand must greet people who have no instructions, a
few seconds of attention and a loud room, often in groups that include children, and it must do so
privately and without ever letting a failure show. This kit teaches how such an interaction is
designed. **Part A** defines the interaction: why strangers are the hard case and why "the visitor
must never tell" which degradation tier is running; the visit as a small state machine with a hub of
optional offerings and invariants that guarantee termination and "a no is a no"; timed beats that sum
to a dwell budget, a cycle and a throughput; and consent by design, where the robot may speak first
but listens only after a visible, revocable visitor action. **Part B** covers the mechanics: a voice
pipeline in which only one box is a language model; speaker attribution that fuses a coarse
microphone-array bearing with faces and abstains honestly off camera; gaze that holds the addressee,
composes bearings with the measured neck angle and moves in calm glides; turn-taking where the robot
hears its own voice and motors and a clever barge-in guard became a cost when the greeting changed;
gestures requested by the model through a live id contract; and ambient awareness as a small typed
event contract with priced false positives. **Part C** covers making it hold up live: degradation
ladders down to a hidden operator and a curtain, a validation ladder that says which rung proves
what, and the lessons of a rehearsed scripted act and the first autonomous runs. The kit carries no
measured numbers from any specific robot or show; every number is public or a labelled illustrative
figure (see [`SOURCES.md`](SOURCES.md)).

This is rung 1 of a four-rung learning kit (notes → diagram → explorer → video). It stands alone.
For the on-board compute side of the same kind of robot (audio front ends, perception cost,
middleware), see the sibling kit [`../robot-workload-benchmarking/`](../robot-workload-benchmarking/).

## How to read these notes

Read Part A → Part B → Part C. Part A says what the interaction must achieve; Part B says how the
pieces achieve it; Part C says how to know it works in public.

### Start here
- [`SOURCES.md`](SOURCES.md) — what this kit is, where the method comes from, the public sources, and the number rules.

### Part A — what a public interaction is
- [`notes/A0-why-strangers-are-the-hard-case.md`](notes/A0-why-strangers-are-the-hard-case.md) — no training, seconds of attention, groups, noise, children; the robot acts first; host, not vending machine; "the visitor must never tell".
- [`notes/A1-the-experience-as-a-state-machine.md`](notes/A1-the-experience-as-a-state-machine.md) — the spine and the offer hub; arrival, groups, change of mind; the invariants; mention versus offer; transition hygiene and the confirmed reset.
- [`notes/A2-beats-and-dwell-budget.md`](notes/A2-beats-and-dwell-budget.md) — beats summed to a dwell budget, cycle and throughput; the responsiveness budget; pacing rules from a rehearsed scripted act.
- [`notes/A3-consent-and-privacy-by-design.md`](notes/A3-consent-and-privacy-by-design.md) — speak first, listen on consent; answer-as-consent and its qualifiers; the session lease; the listening indicator; what is kept; children and accessibility.

### Part B — the mechanics
- [`notes/B1-the-voice-pipeline.md`](notes/B1-the-voice-pipeline.md) — VAD, ASR, TTS and speech-to-speech; the components as built and which is an LLM; on-rails versus open dialogue; reasoner as sequencer versus coordinator.
- [`notes/B2-who-is-speaking.md`](notes/B2-who-is-speaking.md) — TDOA and GCC-PHAT; DoA gates, ASD selects; tiered labels; modal bearings; self-speech suppression; honest abstention off camera; passing attribution to the model.
- [`notes/B3-gaze.md`](notes/B3-gaze.md) — why look at the speaker; trust grades and the triage verdict; frames and field of view; arbitration; ordered gates; the state matrix and duty cycle; glide versus saccade.
- [`notes/B4-turn-taking-and-self-hearing.md`](notes/B4-turn-taking-and-self-hearing.md) — barge-in; motor noise and self-hearing; the spectral guard and why it was turned off; continuity defects; the head-nod loop and the missed utterance; method lessons.
- [`notes/B5-behaviours-from-language.md`](notes/B5-behaviours-from-language.md) — tool calls for gestures; the id-namespace contract; a silent failure traced; six layers; skew; the hand-over as choreography.
- [`notes/B6-ambient-awareness.md`](notes/B6-ambient-awareness.md) — a semantic event contract; whom to engage; enrichment off the critical path; the price of each false positive; crowds.

### Part C — making it hold up live
- [`notes/C1-failure-and-degradation-ux.md`](notes/C1-failure-and-degradation-ux.md) — conversation, duplex and show ladders; the Wizard-of-Oz floor and the curtain; case-by-case failure UX; bounds and honesty; a release ladder for the gift.
- [`notes/C2-the-validation-ladder.md`](notes/C2-the-validation-ladder.md) — from unit tests to live; what each rung proves; test isolation; a graded content-safety protocol; kill switches; a debrief method.
- [`notes/C3-lessons-from-a-live-show.md`](notes/C3-lessons-from-a-live-show.md) — what carried, what broke and what changed after a scripted act and the first autonomous runs; seams break before components.

### Reference files
- [`glossary.md`](glossary.md) — one definition per term, alphabetical, with the note that introduces it.
- [`constants.json`](constants.json) — every number this kit cites, each labelled public or illustrative, with a source.

## Question a reader asks → note that answers it

| Question | Note |
|---|---|
| Why is a public stand harder than a lab demo? | [[notes/A0-why-strangers-are-the-hard-case]] |
| How do I stop the robot from nagging, repeating itself or never ending? | [[notes/A1-the-experience-as-a-state-machine]] |
| How long may each beat be, and how many visitors per hour does that give? | [[notes/A2-beats-and-dwell-budget]] |
| When may the robot listen, and how does a visitor know it is listening? | [[notes/A3-consent-and-privacy-by-design]] |
| Which part is the LLM, and who decides the order of the visit? | [[notes/B1-the-voice-pipeline]] |
| How does the robot know who in a group spoke, and what if they are off camera? | [[notes/B2-who-is-speaking]] |
| Where should the head point, and how do I stop it flickering? | [[notes/B3-gaze]] |
| Why does the robot interrupt itself or miss the first words? | [[notes/B4-turn-taking-and-self-hearing]] |
| Why does the robot say "sure" and not move? | [[notes/B5-behaviours-from-language]] |
| What should the robot notice unprompted, and what does a false alarm cost? | [[notes/B6-ambient-awareness]] |
| What does the visitor see when something fails? | [[notes/C1-failure-and-degradation-ux]] |
| What does "proven live" mean, and which test proves what? | [[notes/C2-the-validation-ladder]] |
| What did a live show teach? | [[notes/C3-lessons-from-a-live-show]] |

## Conventions

- Notes use the ASD-STE100-at-80 % style: one fact per sentence, active voice, one term per concept, caveats before results, numbers with units.
- The subject is generic: "the robot" (a child-sized humanoid), "the team", "a public demo stand", "the show".
- Every number is public or labelled illustrative (see [`SOURCES.md`](SOURCES.md) and [`constants.json`](constants.json)); nothing is a measurement from a specific robot or show.
- `[[wikilinks]]` connect notes inside this kit; relative Markdown links reach sibling kits.
