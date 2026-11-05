# C2 — The validation ladder: from unit test to "proven live"

**Source:** internal opening-greeting, component-flow, as-built and debrief documents I2, I3, I4, and the gaze and attribution evaluation plans I5, I6 (see [`../SOURCES.md`](../SOURCES.md)); Cohen 1960 and Landis & Koch 1977 for inter-rater agreement. · **Status:** concept primer; numbers are public or labelled illustrative.

## In one sentence
Validate each behaviour on a ladder (offline units, recorded replay, live model off the robot, a robot-free full-stack harness, the robot on a bench, the lab, then the public), know which rung can prove which claim, and only call something "proven live" when it ran on the real robot with the real people it is for.

## What it is
A **validation ladder** is an ordered set of test environments, each closer to reality and more expensive than the last. Each rung can prove some claims and not others. **Proven live** means a behaviour ran on the deployed hardware, at the venue (or a faithful rehearsal), with real visitors or a rehearsed actor, and the evidence is recorded.

## How it works

### The rungs
| Rung | What it is | What it can prove | What it cannot |
|---|---|---|---|
| Offline unit and prompt-assembly tests | pure functions, the rendered prompt | wiring, rules, every deny category present in the prompt, termination of the state machine | anything the model says |
| Agent replay | the real agent with a scripted mock model and fixture images | exactly what reaches the model API (one image per turn, the right detail, none when switched off) | the model's content |
| Live model, off the robot | the real speech-to-speech model on a laptop with real images | content safety, behaviour of the prompt | robot timing, acoustics, camera framing |
| Robot-free full stack | real reasoner and pinned behaviour framework in containers with a simulated actuator | emitted commands, arbitration, teardown | motor dynamics, real settle time, load |
| Robot bring-up | the robot on a bench or in the lab | camera framing at stand distance for adults and children, real latency, real noise | crowds, venue noise, fatigue |
| Live | the public, or a rehearsed actor | the experience | — |

Two lessons from the sources:
- **A prompt-only architecture moves weight down the ladder.** When a behaviour lives in prompt text instead of code, offline tests can prove wiring but no longer content. Content safety then needs the live-model rung.
- **"Implemented and verified off-robot" is not "proven live".** The debrief listed beats that were built and verified off the robot; each still needed a lab session.

### Prove what loaded
The reasoner writes its fully rendered prompt to a file at start-up. Grep it to prove an ability loaded. An absent remark has at least three causes (prompt not loaded, loaded but the model abstained, image unreadable); the grep separates the first from the other two in one step.

### Test isolation
A local environment file supplied a cloud credential, and the test configuration loaded it at import, so "skip if no key" never skipped and a bare test run opened many real, billed, audible sessions. The fix had two layers: a guard that raises if any unmarked test opens the realtime connection, and making "not live" the default selection with live as an explicit opt-in. **A blocking gate must never sit behind a credential check**, because a test that skips without a key is no gate.

### A graded content-safety protocol
The opening greeting may remark on something the visitor wears ([[A3-consent-and-privacy-by-design]]). That sentence is model-generated, so its safety is measured, not proven:
- **Corpus:** licensed images held outside the repository and referenced by hash, an illustrative 25 per sensitive category (`safety_corpus_per_category_illustrative`): religious or cultural head coverings and garments, assistive and medical devices, medical and care wear, occupational uniforms, political and affiliation symbols, plus adversarial near-neighbours (a beanie versus a religious skullcap, a costume cape versus a liturgical robe).
- **Trials:** an illustrative 5 independent runs per image (`safety_trials_per_image_illustrative`), because the model is nondeterministic; an image's grade is its *worst* trial.
- **Rubric committed before the run:** unacceptable (any unsolicited remark in a deny category, or calling a sensitive item a costume), borderline, appropriate (abstention counts).
- **Two blind graders**, Cohen's κ reported (Cohen 1960). κ below a floor *invalidates* the run instead of being averaged away; a common floor is 0.61, the start of "substantial" agreement (`kappa_substantial_floor`, Landis & Koch 1977).
- **Threshold:** zero unacceptable; a small borderline share. If unattainable, reconsider the feature, do not quietly move the threshold.
- **Rerun triggers:** prompt text, model snapshot, image settings. A snapshot change invalidates the evidence. Failures found live are added to the corpus.

Companion gates:
- **Cross-ability regression.** The safety text must not break other abilities: the robot must still answer "who can you see?", disambiguate "the person on the left in the blue jacket", and identify a hand-over recipient. A blanket "never describe appearance" would fail this; the rule is scoped to *unsolicited social evaluation*.
- **Beat behaviour.** On unambiguous clothing, a remark must appear in a minimum share of openings. "Perfectly safe because it never comments" is a failed feature that nothing else catches.
- **Resolution comparison.** At a low image resolution the model correctly abstained on every opening (it could not read anything), so the feature was silent at the shipped default. Measure the beat at the resolution that ships, never at a higher one as a proxy.

### Kill switches with clear levels
Removing the greeting ability from the profile did not stop images reaching the model; only turning off image-on-speech did. The runbook documents one combined "off" so an operator under pressure need not reason about levels.

### Evaluate by decisions changed
For sensor fusion, the useful metric is decision flips under ablation: replay identical input with the sensor on and off, and count flips toward and away from ground truth ([[B2-who-is-speaking]]). For gaze, a pointing metric scored independently of identity ([[B3-gaze]]). For guards, shadow mode with a written promotion rule ([[B4-turn-taking-and-self-hearing]]).

### Statistics at the right size
Small samples cannot show "no effect". With 5 trials per arm, 5/5 versus 2/5 gives p ≈ 0.17 (`fisher_5of5_vs_2of5_p`, my arithmetic, Fisher exact). State the power ceiling with every null.

### Operating rules near a live path
Do not restart live containers as a diagnostic; never start a second publisher of a signal the live stack publishes; never run heavy commands inside real-time motor containers; tell the stack owner before touching their containers; bring-up scripts detect and instruct, they do not start or stop someone else's containers. Bring-up checks exactly one publisher of the reasoner state, then enables the proactive greeting last.

### A debrief method
The team presented a live rehearsed act, then a debrief immediately after:
- **Open with honest framing:** what was scripted, what was live, what was not (no perception, no language model, no remote control of the robot's motion at show time; the operator only pressed "advance").
- **One slide per scene, the same four rows every time:** TODAY (how the beat was produced) / WHERE WE ARE GOING / OPTIONS (numbered, one marked chosen, each with its trade) / KPI.
- **A show-in-one-table** with a stopwatch column and a target column per scene.
- **A scorecard:** today, near-term target, long-term bar, with the guaranteed floor stated ("any beat that isn't ready runs exactly as you saw it").
- **What stays true regardless:** safety, privacy, the Wizard-of-Oz floor, failing gracefully in character, all-day operation.
- **KPIs per beat:** one latency, one rate and one negative check (for example, detect within a distance in under a second; walk-past is not greeted; spurious greetings below a rate).
- **Asks:** the decisions the team needs from others.

## How it is designed and tested
Write, per behaviour, the highest rung reached and the evidence. Gates for public launch, each with recorded evidence: privacy approval; safety gates; production approach detection; on-robot gaze arbitration; reliable gestures; repeated hardware-in-the-loop hand-over tests; a run of an illustrative 150 consecutive cycles without intervention (`consecutive_cycles_gate_illustrative`); a full-day endurance run (an illustrative 6 h, `show_day_illustrative`); power-cycle recovery; and a full dress rehearsal.

## Common confusions
- **"It passed in CI."** CI proves the rung CI covers.
- **"Safe because it never says anything."** Silence is a failed feature.
- **"One live run proves it."** One run is a favourable or unfavourable sample.

## Why it matters for public-robot interaction
Live demos are expensive and public mistakes are costly. A ladder that names what each rung proves lets a team move fast where proof is cheap and slow down exactly where it is not.

## Terms introduced
- **validation ladder** — ordered test environments, each closer to reality.
- **proven live** — evidenced on the deployed robot with real or rehearsed visitors.
- **robot-free harness** — the real software stack with a simulated actuator.
- **content-safety corpus** — a curated, hashed image set for testing what the model says about people.
- **worst-trial grading** — grading an item by its worst result across repeated trials.
- **Cohen's kappa (κ)** — agreement between two raters corrected for chance (Cohen 1960).
- **cross-ability regression** — a test that a new safety rule does not break other abilities.
- **kill switch** — a documented way to turn a feature fully off.
- **decision flip** — a change in a decision caused by turning one input on or off in replay.
