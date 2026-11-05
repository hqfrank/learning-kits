# B4 — Turn-taking: barge-in, the robot hearing itself, and a loop between a nod and a missed utterance

**Source:** internal turn-taking defect investigations and the barge-in guard design I7 (see [`../SOURCES.md`](../SOURCES.md)); Sacks, Schegloff & Jefferson 1974; Stivers et al. 2009; Skantze 2021; Benesty et al. on acoustic feedback cancellation. · **Status:** concept primer; every robot measurement here is replaced by a labelled illustrative value.

## In one sentence
In a full-duplex robot, the microphone hears the robot's own voice and motors, the processed channel can make both louder than a person, a transcription model turns noise into words, and every guard against phantom turns is also a way to ignore a real visitor, so each fix must be measured against both failure directions and against the interaction it will meet.

## What it is
**Turn-taking** is how speakers decide who talks next. Sacks, Schegloff & Jefferson (1974) describe it as locally managed, with turns built so that the next speaker can predict their end. The typical gap is about 200 ms (`turn_gap_typical`, Stivers et al. 2009). **Barge-in** is the user starting to speak while the system is speaking; a **full-duplex** system keeps listening while it talks so it can yield. **Self-hearing** is the robot's microphone picking up the robot's own loudspeaker output. **Acoustic feedback cancellation (AEC)** subtracts an estimate of the loudspeaker signal from the microphone signal, using the loudspeaker feed as a reference (Benesty et al.).

## How it works

### How a barge-in is handled
1. The server-side VAD emits "speech started".
2. The dialogue layer closes a response gate and starts a debounce of an illustrative 0.4 s (`barge_in_debounce_illustrative`).
3. If the debounce fires, the robot stops mid-sentence and cancels its response.
4. The server commits the audio at end of turn, transcribes it and generates a reply.
5. Triage accepts or ignores it ([[B1-the-voice-pipeline]]).

Full duplex was the product requirement, so any fix that mutes or attenuates the microphone while the robot speaks was ruled out: it would kill real barge-ins.

### Two sources of phantom barge-ins
**(a) The robot's own motors.** While the robot talks, its neck nods, its eyebrows move and its arms gesture. The motion puts impulsive, structure-borne rumble into the microphones, mostly at low frequency (an illustrative 60–250 Hz band, `guard_low_band_illustrative`). The array's processed channel, the one the speech model reads, *amplified* it: in an illustrative case the raw microphone rose 8 dB and the processed channel 20 dB when the head moved (`actuator_lift_raw_illustrative`, `actuator_lift_processed_illustrative`). Automatic gain control winds up when no speech is present. On the processed channel the robot's own motion was an illustrative 3 dB louder than a person talking nearby (`motion_over_speech_processed_illustrative`). Noise-only clips sent to a transcription model came back as words every time, an illustrative 5 of 5 (`noise_only_transcripts_illustrative`), sometimes in other languages, the signature of a model given non-speech.

AEC cannot remove motor noise. It identifies a linear path from a live electrical reference to the microphone. Motors have no reference, servo noise is not repeatable sample for sample, and a pre-recorded servo sound is uncorrelated with the live one, so an adaptive filter converges to nothing or subtracts garbage.

**(b) The robot's own voice.** Measured by logging the array's per-frame levels against the reasoner's speech start and end times: the robot's voice sat an illustrative 15 dB above the room floor during speech (`self_hearing_lift_illustrative`), present in every speech window and absent in every silence window. That on-off correlation separates self-hearing from ambient noise. The array's own suppression was **late and incomplete**: the processed channel tracked the room for the first part of each robot sound, an illustrative 0.2–0.8 s (`self_hearing_leak_window_illustrative`), then dropped an illustrative 20 dB (`self_hearing_suppressed_drop_illustrative`). Phantom turns clustered inside that onset window. The likely root of the residue was **clipping**: a clipped acoustic return is nonlinear, and no linear canceller removes it. Phantom transcripts were the robot's own words cut into fragments.

Whether self-hearing breaks a session is stochastic. The VAD threshold is high, so leaked speech trips it only on peaks. **A run of clean utterances is a favourable sample, not evidence of a fix.**

### Options, and what each traded
| Option | Verdict |
|---|---|
| Mute the microphone while speaking | kills full duplex |
| Always-on high-pass filter | withdrawn after a pre-registered sweep: no behaviour win, and it degraded short wake-phrase recognition |
| Ignore VAD while the robot moves | rejects real barge-ins during motion; data showed real onsets were separable |
| Raise the VAD threshold | already near maximum |
| Build an own front end from the raw microphones | recommended medium term: escapes both gain wind-up and clipping ("clipping is damage no downstream stage can reverse") |
| **A spectral barge-in guard** | chosen |

### The spectral barge-in guard
When the VAD claims speech *while the robot is speaking* (or within a motion tail after it), the dialogue layer checks the audio it actually sent. For each illustrative 200 ms sub-window at a 50 ms stride (`guard_subwindow_illustrative`, `guard_stride_illustrative`) it computes 10·log10(E[speech band] / E[rumble band]), with an illustrative speech band of 400–3000 Hz (`guard_speech_band_illustrative`). The score is the **maximum** over sub-windows: any real voice, even over motor noise, has a vowel where the speech band dominates, and one good vowel is enough. In an illustrative fitted set, motor-noise onsets scored up to 3 dB and real onsets from 8 dB (`guard_phantom_max_illustrative`, `guard_real_min_illustrative`); the threshold was set mid-margin at 5 dB (`guard_threshold_illustrative`). The source states honestly that perfect separation on one robot, one room and one talker is a *fit*, not a generalisation.

Design properties worth copying:
- **Narrow scope.** Consulted only when the VAD event would interrupt the robot. Listening, waking and talking over a tool run are untouched.
- **Reuse the existing rejection path** verbatim, and insert the check at every place the "user speaking" state can be entered from a VAD event.
- **Fail open.** Any guard failure (empty or stale buffer, exception) allows the barge-in. "Phantom self-interruption is a quality bug; a deaf robot is a product failure." A test checks the bytes sent to the model are identical with the guard on and off.
- **Promotion by a written rule.** Shadow mode logs would-be decisions with no behaviour change. Default-on needs, all at once: an illustrative 60 in-scope evaluations, 15 scripted real barge-ins with none rejected, 85 % of motor onsets rejected, and a 3 dB worst-case margin (`guard_promo_evaluations_illustrative`, `guard_promo_real_bargeins_illustrative`, `guard_promo_reject_rate_illustrative`, `guard_promo_margin_illustrative`). "No behaviour change ships on the strength of an offline fit alone."

### Why the clever guard was turned off
The guard shipped off, was promoted on after its probe passed, and was later flipped back off. Two reasons:
1. **The benefit went away.** A platform audio update removed most of the self-hearing it was built for.
2. **A new interaction design moved the common case into its blind spot.** The guard had grown an "onset grace": reject VAD onsets within an illustrative 2 s of robot speech onset (`guard_onset_grace_illustrative`). Then a perception-triggered greeting of an illustrative 1.5 s (`proactive_greeting_illustrative`) became the normal opening. A visitor's prompt reply landed inside the grace and was rejected; the model, holding an unanswered greeting, stopped listening and the robot went idle. The design had argued "a rejection costs at most one utterance". Here **one rejection ended the whole visit.**

Lesson: a short robot utterance followed by a quick human reply is exactly the shape an onset grace cannot tell from self-hearing. A defence becomes a cost when the interaction design changes underneath it. The code, tests and promotion rule stayed; only the default moved, with a boot-log line as positive confirmation of the setting.

### Continuity defects
Self-hearing created phantom user turns; the dialogue layer's resume and continuation machinery then damaged the robot's speech. Two team-owned defects turned harmless ignored turns into visible failures:
- **Resume-on-ignored-input** re-joined interrupted speech, sometimes into a *different* story: dropped openings, skipped middles, crossed threads. On one model generation it was loud (a new spoken opener each time); on another it was quieter but the content damage remained. **Grade content continuity, not "did it interrupt itself".**
- **Forced continuation** existed to stop a model that speaks only a preamble ("let me take a look") from ending its turn unanswered. It could not tell a bare preamble from a finished answer, so a complete story got a forced extra step, and the robot spoke again. It never appeared on a laptop, which has no self-hearing to interrupt a finished response: **a defect that needs a hardware-only trigger passes every development test.**

A four-arm experiment varied one factor at a time (engine, model generation, platform audio). The decisive pair held model and platform fixed and changed only the engine. The model generation *amplified* the defect without causing it. The upstream engine, without the guard, failed differently: it answered phantom fragments and abandoned the task. "Neither engine is robust to self-hearing with the guard off."

### The head-nod loop and the missed utterance
A separate investigation chased three faults reported together: missed utterances after the wake phrase, a regular head nod "like a nervous tic", and a loop of cancelled responses.

- **Missed utterances.** The dialogue layer dropped microphone audio while idle and began streaming at the moment the wake phrase fired. Everything said up to that moment was lost; the server's prefix padding cannot pad audio never sent. Fix: an in-memory **pre-roll** ring buffer of an illustrative 1.5 s (`preroll_illustrative`), about 48 000 bytes at 16 kHz 16-bit mono (`preroll_bytes_1p5s_16k`, my arithmetic), flushed on detection.
- **Fragmentation.** An end-of-turn silence of an illustrative 250 ms (`vad_silence_short_illustrative`) was shorter than a mid-sentence pause (an illustrative median burst of 0.7 s, `speech_burst_median_illustrative`), so one sentence arrived as several turns and responses collided ("a response is already active"). An illustrative 600 ms (`vad_silence_long_illustrative`) removed the collisions at the cost of later turn ends. Separately, the client must check for an active response before requesting another.
- **A plausible loop that was not the cause.** Neck motor noise falsely triggered the wake phrase about an illustrative 2 times as often after a head move (`ghost_wake_relative_risk_illustrative`), the reasoner woke, timed out and dropped the head, which made more noise. Real, but every wake-phrase detection turned the face lights a particular colour, and the reported nod never did. **Absent evidence is evidence.**
- **The real nod.** The commanded head pose was constant. Below it, whenever the controller's loop stalled longer than an illustrative 400 ms (`override_timeout_illustrative`), the motor arbiter's head override timed out and the walking policy's own neck posture showed through for a moment. That is the *driver* (a starved control loop, owned by the platform). The *enabler* was the team's: the reasoner published its state only on transitions, so a crashed or restarted reasoner left the controller latched in a "head up" state forever, which made the dip visible. Fix for the enabler: publish state at start-up, republish on a heartbeat (an illustrative 2 s, `state_heartbeat_illustrative`), publish idle on shutdown, and give every non-idle state an escape timeout. Fixing only the enabler *masks* the nod; record it as masking.
- **An OR-of-conditions gate masks.** The head was forced down if any of several conditions held. A term that forces "down" hides all others; removing it unmasks them. Ask what a suppression lever *unmasks* before pulling it.

### Method lessons
- Pre-register the hypothesis, the scoring rule, the threshold, and the power. With 10 trials per arm even a perfect-versus-half split only reaches p ≈ 0.03 (`fisher_10of10_vs_5of10_p`); with 5 per arm, 5/5 vs 2/5 gives p ≈ 0.17 (`fisher_5of5_vs_2of5_p`, my arithmetic). An underpowered null is "no effect detected", not "harmless".
- Hold the confounder constant: when loudspeaker playback always co-occurred with motion, comparing playback on and off *within* bins of a motor-noise proxy separated the two.
- Plot the time course before averaging; one mean pooled a leaked onset and a suppressed remainder into a number describing neither.
- Characterise the loudest operating state (moving and speaking), not the quietest.
- Label the instrument reading ("loudspeaker active"), never the inference ("robot speaking").
- The human witness is an instrument: render recordings to audio and ask the person who was in the room.
- Read the code inside the deployed container, not a newer checkout.

## How it is designed and tested
Every turn-taking change gets two measurements: phantom turns caused (false barge-ins, ghost wakes) and real turns lost (rejected barge-ins, missed utterance starts), on the robot, moving and speaking, in the venue's noise. Report both with their sample sizes.

## Common confusions
- **"AEC solves self-hearing."** It removes the linear part of the loudspeaker path; it cannot remove clipping or motors.
- **"The guard costs at most one utterance."** That depends on what that utterance is. The first reply to a greeting is the whole visit.
- **"It works on the laptop."** The laptop lacks the trigger.

## Why it matters for public-robot interaction
A robot that interrupts itself, answers its own voice or ignores a child's first word loses the visitor in seconds. Turn-taking defects stack across owners (array firmware, platform, dialogue layer, model), so the method, measure both directions and vary one factor at a time, matters as much as any single fix.

## Terms introduced
- **turn-taking** — how participants decide who speaks next.
- **barge-in** — a user starting to speak while the system speaks.
- **full duplex / half duplex** — listening while speaking / closing the microphone while speaking.
- **self-hearing** — the robot's microphone picking up the robot's own loudspeaker.
- **acoustic feedback cancellation (AEC)** — subtracting an adaptive estimate of the loudspeaker signal from the microphone, using the loudspeaker feed as reference.
- **automatic gain control (AGC)** — a front-end stage that raises quiet input; it can amplify noise when no speech is present.
- **debounce (barge-in)** — the delay before a "speech started" event is allowed to stop the robot.
- **spectral barge-in guard** — a check that declines a barge-in when the audio looks like motor rumble rather than a voice.
- **fail open** — on guard failure, allow the barge-in (the pre-guard behaviour).
- **shadow mode** — running a check and logging its decisions without acting on them.
- **pre-roll** — a ring buffer of recent audio, flushed to the model when the wake phrase fires.
- **end-of-turn silence** — the trailing silence after which the VAD ends a turn.
- **driver / enabler** — the cause that produces a symptom / the condition that makes it visible.
