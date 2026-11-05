# Sources — Designing a humanoid robot's conversation with strangers

This kit teaches a general method. It carries no measured numbers from any specific robot, venue or
programme.

## What this kit is

Study notes (rung 1 of a four-rung learning kit: notes → diagram → explorer → video) for one
question: **how do you design a child-sized humanoid robot's conversation with strangers at a public
demo stand, so that it is warm, private, accessible and still coherent when things fail?** Part A
covers what a public interaction is (the hard case, the state machine, beats and dwell budget,
consent). Part B covers the mechanics (the voice pipeline, speaker attribution, gaze, turn-taking,
gestures from language, ambient awareness). Part C covers making it hold up live (degradation UX,
the validation ladder, lessons from a live show).

## Provenance of the method

The engineering ideas, the state machine and its invariants, the dwell-budget arithmetic, the
consent design, the component split, the fusion and abstention rules for speaker attribution, the
gaze gates and state matrix, the barge-in guard and why its default was reversed, the
behaviour-id contract, the degradation ladders, the validation ladder and the debrief template, are
abstracted from **internal product, design and research documents of a public humanoid-robot
demonstration programme, 2026**. No internal material is reproduced. No robot, company, person,
place, show, product, vendor, component or specification name, and no internal identifier, appears
here. No internal figure or diagram is copied, traced or described.

The internal documents are cited only by a generic tag, so that each claim can be traced to its kind
of source without naming it:

| Tag | Kind of document |
|---|---|
| I1 | visitor-experience definitions: a state machine of the visit, a beat-by-beat UX definition with decision records, an end-state experience brief with readiness gates |
| I2 | a rehearsed scripted act and its debrief presentation |
| I3 | an opening-greeting design: content safety, image handling, head posture, a validation protocol |
| I4 | an interaction-layer design, a one-visitor component flow, and an as-built snapshot of the stack |
| I5 | gaze designs: a speaker-gaze policy, a perception-and-control adoption study, a gaze state matrix, its research note and its revision |
| I6 | speaker-attribution designs (direction of arrival, off-camera speakers, attribution for a speech-to-speech model) and an ambient-perception design |
| I7 | turn-taking investigations (a barge-in guard, self-hearing and speech-continuity defects, a head-nod loop and missed utterances) and a behaviour tool-calling design |

## Number rules

Every number in this kit is one of two classes, recorded in [`constants.json`](constants.json):

- **public** — from a public paper, standard or regulation, or physics arithmetic on public values;
  the `source` field names it. "My arithmetic" marks derived values.
- **illustrative** — a round value of the same order of magnitude as a figure in the internal
  documents, invented to teach a relation (a sum, a ratio, a direction, an ordering). It is never a
  measurement. In prose each one is written "an illustrative X" with its key on first use in a note.

Illustrative values were chosen to keep the relations the source relied on: the beats sum to the
typical interaction; the reset plus the interaction gives the cycle and the throughput; the
listening-indicator budget sits below the public 1 s flow limit; the proactive greeting is shorter
than the barge-in guard's onset grace (which is why the guard turned into a cost); the gaze design
bands bracket the public human gaze shares; a plain gaze/look-away alternation lands inside one band
and outside the other. Where possible they differ from the internal values.

## How the material was read

- The internal documents were read in full by extraction passes that kept mechanisms, decisions,
  trade-offs and lessons, and listed every internal number separately so it could be replaced.
- The sources disagree in places. Where they do, the notes teach the disagreement as a design
  tension rather than picking silently: who delivers the gift (self-serve versus a physical
  hand-over), "assumed taken" versus "never claim a take that did not happen", whether to greet every
  passer-by or only interested ones, whether a remark on clothing is in the first release, the
  camera used as the attribution anchor, and "never withhold a label" versus honest abstention (the
  later document supersedes).
- Some internal documents cite no public literature. The public citations below were added for the
  general claims (turn gaps, gaze shares, proxemics, delay estimation, consent law, accessibility,
  inter-rater agreement) and were checked against the original publications or their abstracts.

## Public sources

Conversation and gaze
- Sacks, Schegloff, Jefferson, "A simplest systematics for the organization of turn-taking for conversation", *Language* 50(4), 1974.
- Stivers et al., "Universals and cultural variation in turn-taking in conversation", *PNAS* 106(26), 2009. https://www.pnas.org/doi/10.1073/pnas.0903616106
- Kendon, "Some functions of gaze-direction in social interaction", *Acta Psychologica* 26, 1967.
- Argyle & Ingham, "Gaze, mutual gaze and proximity", *Semiotica* 6, 1972; Argyle & Cook, *Gaze and Mutual Gaze*, 1976.
- Vertegaal, Slagter, van der Veer, Nijholt, "Eye gaze patterns in conversations: there is more to conversational agents than meets the eyes", CHI 2001.
- Mutlu, Shiwa, Kanda, Ishiguro, Hagita, "Footing in human-robot conversations: how robots might shape participant roles using gaze cues", HRI 2009; Mutlu, Kanda, Forlizzi, Hodgins, Ishiguro, "Conversational gaze mechanisms for humanlike robots", *Transactions on Interactive Intelligent Systems* 1(2), 2012.
- Admoni & Scassellati, "Social eye gaze in human-robot interaction: a review", *Journal of Human-Robot Interaction* 6(1), 2017.
- Bohus & Horvitz, "Models for multiparty engagement in open-world dialog", SIGDIAL 2009.
- Skantze, "Turn-taking in conversational systems and human-robot interaction: a review", *Computer Speech & Language* 67, 2021.
- Hall, *The Hidden Dimension*, 1966 (proxemic zones).
- Carpenter, *Movements of the Eyes*, 2nd ed., 1988; Bahill, Clark, Stark, "The main sequence, a tool for studying human eye movements", *Mathematical Biosciences* 24, 1975.

Audio and attribution
- Knapp & Carter, "The generalized correlation method for estimation of time delay", *IEEE Trans. ASSP* 24(4), 1976 (GCC-PHAT).
- DiBiase, Silverman, Brandstein, "Robust localization in reverberant rooms", in *Microphone Arrays*, Springer, 2001 (SRP-PHAT).
- Schmidt, "Multiple emitter location and signal parameter estimation", *IEEE Trans. Antennas and Propagation* 34(3), 1986 (MUSIC).
- Benesty, Gänsler, Morgan, Sondhi, Gay, a monograph on adaptive cancellation of the loudspeaker-to-microphone path in network and acoustic settings, Springer, 2001.
- ROS4HRI, REP-155 "Human-Robot Interaction in ROS" (person, face, body, voice model). https://www.ros.org/reps/rep-0155.html
- Yang et al., Set-of-Mark prompting for visual grounding in large multimodal models, arXiv:2310.11441, 2023 (title shortened to omit a model name).

Method, safety, privacy, accessibility
- Kelley, "An iterative design methodology for user-friendly natural language office information applications", *Transactions on Office Information Systems* 2(1), 1984 (Wizard-of-Oz).
- Nielsen, *Usability Engineering*, 1993, ch. 5 (response-time limits).
- Cohen, "A coefficient of agreement for nominal scales", *Educational and Psychological Measurement* 20, 1960; Landis & Koch, "The measurement of observer agreement for categorical data", *Biometrics* 33, 1977.
- Regulation (EU) 2016/679 (GDPR), Art. 4(11), 6, 7, 8, 9.
- W3C, Web Content Accessibility Guidelines (WCAG) 2.2, SC 1.4.1, 2.2.1, 2.3.1. https://www.w3.org/TR/WCAG22/
- ISO 13482:2014, Robots and robotic devices — Safety requirements for personal care robots.

## Reading conventions

- Notes follow ASD-STE100 at about 80 %: one fact per sentence, active voice, one term per concept,
  caveats before results, numbers with units.
- The subject is generic: "the robot" (a child-sized humanoid), "the team", "a public demo stand",
  "the show", "the reasoner" (a speech-to-speech LLM session), "the dialogue layer", "the behaviour
  library", "the robot gateway", "a small gift".
- `[[wikilinks]]` connect notes inside this kit.

## Rung 2 (diagrams)

- `diagrams/` (learn-diagram): six pages drawn from notes A1, A2, B1, B2, B3, B4 (with C2 for the endurance gate) and from `constants.json` only; every canvas number is loaded by key and tagged `[Pn]`/`[In]`/`[calc]`. No internal figure was used. See `diagrams/INDEX.md`.

## Rung 3 (explorers)

- `explorers/` (learn-explorer): four single-file HTML pages: gaze state matrix (B3), direction of arrival (B2), turn-taking timeline (B4), dwell budget (A2, with C2). Parameters are copied verbatim from `constants.json` into each page and into `explorers/params.json`. Page-only model choices are named `page_*`, class illustrative, and their source says "page model choice". No measured overlays; sources are this kit's notes, glossary and constants only. See `explorers/INDEX.md`.
