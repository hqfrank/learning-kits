# B2 — Who is speaking: direction of arrival, faces, and honest abstention

**Source:** internal speaker-attribution designs I6 (see [`../SOURCES.md`](../SOURCES.md)); Knapp & Carter 1976 (GCC-PHAT); DiBiase, Silverman & Brandstein 2001 (SRP-PHAT); Schmidt 1986 (MUSIC); the ROS4HRI person model (REP-155); Yang et al. 2023 (Set-of-Mark prompting). · **Status:** concept primer; numbers are public arithmetic or labelled illustrative.

## In one sentence
Fuse a coarse microphone-array bearing with faces and mouth motion to label each utterance with an anonymous visitor id, let the bearing gate and corroborate but never choose on its own, and when the evidence points off camera, say "unidentified" instead of guessing, because a confident wrong name costs more than no name.

## What it is
**Speaker attribution** is labelling each unit of speech with who said it. At a stand the labels are **anonymous, session-stable ids** (`visitor_1`, `visitor_2`) with no enrolment, no names, and nothing kept after the visit (see [[A3-consent-and-privacy-by-design]]).

A speech-to-speech model needs attribution because its conversation is one linear chain of items shared by everyone at the stand. Without labels it sees one "user" who keeps changing voice and topic. With labels it can keep two interleaved conversations apart, address the right person, and let triage see that a topic break is a *new engaged person*, not noise ([[B1-the-voice-pipeline]]).

Three cues are available:

- **Direction of arrival (DoA)** — the bearing of a sound source, estimated from the time differences between microphones.
- **Active-speaker detection (ASD)** — a vision model that scores whether a visible face's mouth moves with the audio.
- **Voice embedding** — a vector that characterises a voice; similar voices give vectors with high cosine similarity.

## How it works

### DoA basics (public physics)
Sound travels at about 343 m/s (`speed_of_sound_20c`). For two microphones 10 cm apart, the largest possible delay is about 292 µs (`tdoa_max_10cm`, my arithmetic). At a 16 kHz sample rate one sample is 62.5 µs, or about 2.1 cm of path (`sample_period_16k`, `sample_path_16k`). So an integer-sample lag on a 10 cm pair resolves only about 12° near broadside (`one_sample_angle_10cm_16k`). Two consequences follow:

- Estimators interpolate below one sample. **GCC-PHAT** (generalised cross-correlation with phase transform, Knapp & Carter 1976) whitens the cross-spectrum so the correlation peak is sharp, then interpolates the peak. **SRP-PHAT** sums GCC-PHAT over all pairs on a grid of directions. **MUSIC** (Schmidt 1986) uses a subspace of the array covariance and can resolve several sources.
- Above c/(2d) the phase difference between a pair wraps (**spatial aliasing**): about 3.4 kHz for a 5 cm pair and 1.7 kHz for a 10 cm pair (`spatial_alias_5cm`, `spatial_alias_10cm`).

Small on-chip arrays often report only a quantised bearing. This kit uses an illustrative 45° bin (8 directions, `doa_bin_illustrative`), published only while the chip detects activity.

### The fusion rule
**ASD selects among visible faces; DoA gates, breaks ties and corroborates. The loudest direction never selects on its own.** This is an invariant, not a tuning default. Only DoA can do three things: rescue an off-camera visitor's directed speech from being ignored; reject a voice from a direction with no face (a phone, a bystander); and break a tie between adjacent faces. DoA binds to a visual *track*, never stands alone, because position and speaker are not one-to-one when people move.

A bearing and a face are compared within an illustrative 15° gate, widened by the bin's uncertainty to an illustrative ±40° window (`doa_face_gate_illustrative`, `doa_effective_window_illustrative`). If more than one face falls in the window, the bearing **abstains** and defers to ASD. At stand distances two visitors often share one bin, so DoA rarely names a speaker; its value is corroboration and bystander rejection. Evaluate it by the decisions it changes, not by how often it is the basis.

### Tiered labels
- **T0** at an illustrative 250 ms after speech start (`label_t0_illustrative`): DoA × visible faces (plus ASD if warm). Attach the turn to someone now; never block a response.
- **T1** by an illustrative 1 s (`label_t1_illustrative`): ASD picks the talker among co-located faces, re-evaluated on every frame while the turn is open, because one VAD segment can hold a whole two-person exchange. A challenger must win several consecutive evaluations before the label switches.
- **T2** up to an illustrative 4 s (`label_t2_illustrative`): voice and face embeddings confirm or repair identity. Correction is acceptable later because the requirement is "correct before the *next* turn".

Every label carries a **basis** (doa, asd, sole face, largest face, voice, last active, and so on). Bases differ hugely in strength. Without the basis, "bound by DoA" and "the only face on camera" look identical downstream. Weak bases are rendered to triage in plain language ("speaker id is probably wrong: the mouth is not moving with the speech").

### Bearings thrash; take the mode of the turn
Within one utterance a coarse bin can change several times per second, yet the **modal bin** over the turn is usually right. A per-turn mode is accepted only if it holds an illustrative 55 % of samples with at least 4 samples (`modal_bin_share_illustrative`, `modal_bin_min_samples_illustrative`). Spread, not bias: aggregation recovers the signal, and acoustic treatment becomes optional rather than required.

### The robot's own voice
On-chip DoA is computed on the raw microphones; the acoustic feedback canceller cleans only the speech channel. While the robot speaks, DoA may point at the robot itself or at a reflection off glass. Rules: suppress DoA evidence while the robot speaks and for an illustrative 400 ms tail (`self_speech_tail_illustrative`); discard bearings held during suppression; never touch the audio itself (the microphone stays open for barge-in). If the speaking-state signal is missing, fail closed: a bearing may corroborate, but never assert "no face at that voice".

### Off-camera speakers: honest abstention
A phone playing radio off camera was once attributed to the silent person in front, because the rule was "every path names somebody". The fix separates two questions:

- **"Should I respond?"** is about **directedness**. Under uncertainty, lean toward responding: an over-response is recoverable ("oh, were you asking me?"); silence toward an engaged visitor is not.
- **"Who said it?"** is about **identity**. A confident wrong name is not free. An illustrative churning id stream cost 30 % more input tokens per response (`id_churn_token_cost_illustrative`), the model hedged instead of confirming continuity, and one wrong bind passed to the next illustrative 4 turns through a "last active speaker" fallback (`cascade_turns_illustrative`).

So the attribution ladder per turn is: ASD among faces large enough to score → a voice match if the turn is long enough and passes a cosine and margin gate (an illustrative cosine of 0.55 and top-1 minus top-2 margin of 0.15, `voice_match_cosine_illustrative`, `voice_match_margin_illustrative`; the only path that can name an off-camera speaker) → **abstain**: `visitor_id: null` with a reason (off camera, contradicted, too short, blend suspected). Abstain only on *positive* evidence (every visible face's mouth contradicts the audio, or the modal bearing has no face, or nobody is visible). A neutral "can't tell" score is not evidence of absence. No sentinel id: a shared "off-camera speaker" id would merge two strangers into one persona. A null label is never a speaker switch.

Directedness must ship in the same change: "someone off camera is addressing you", with no name, still reaches the reasoner. Shipping abstention without it reintroduces the original failure.

### Voices are banked carefully
An off-camera voice long enough to embed (an illustrative 1.2 s, `voice_embedding_min_illustrative`) that matches nobody is banked silently. It becomes an id only on a second agreeing observation, and binds to a face only when two sensors agree (ASD confirms the face while the voice matches). Blends of two speakers in one segment are rejected by checking sub-window disagreement. "A missed enrolment delays recognition by one turn; a poisoned cluster corrupts every future match."

### Passing attribution to the model
- A per-turn **system message** sent between speech start and commit ("active speaker: visitor 2"), so it lands before the audio item and the response is attributed.
- A durable **roster** as a context property, re-emitted on change and after compaction: present visitors with a few-word anonymous descriptor and a line of thread state, capped in size.
- An **evidence block** for triage (identity, how long present, facing, ASD score). The LLM still decides; evidence is input, not an override.
- An optional **labelled image**: boxes marked with visitor ids. Public work shows multimodal models ground poorly on raw images but well when regions are marked (Set-of-Mark, Yang et al. 2023). Label a box only when the match is sure; "a missing label is far cheaper than a wrong one".
- **Corrections** go as one system message at a safe boundary, at most once per visitor per illustrative 2 minutes (`correction_rate_cap_illustrative`). History is not rewritten; a stable, possibly wrong label plus social repair beats an oscillating one.

The person model follows the public ROS4HRI pattern (REP-155): a permanent anonymous person bound to transient face, body and voice tracks, with merge and split.

## How it is designed and tested
- **Replay first.** Record once, replay forever, with ground truth established independently of the pipeline. Fix seeds; keep a regression gate before tuning.
- **Ablation by decision flips.** Replay with DoA on and off; DoA earns its place by flipping decisions toward ground truth off-axis and in two-speaker scenes, and by zero flips away in the bystander scene.
- **One-person scripts.** A phone plays the off-camera voice, so one tester can run every scenario.
- **Check the input-size gate.** An ASD model that ignores faces below an illustrative 40 px (`asd_min_face_illustrative`) was silently off on a low-resolution stream (an illustrative median face of 22 px, `face_median_low_res_illustrative`). Doubling the stream resolution (median 50 px, `face_median_high_res_illustrative`) turned it on, at a cost in frame rate.
- **Prove capability is fed.** "Has DoA" must mean "estimator exists *and* its feed is alive". An unfed estimator once produced no bearings while the code still believed it had them.

## Common confusions
- **"Point the robot at the loudest direction."** Reflections and the robot's own voice are often loudest.
- **"Unknown voice means bystander."** An unknown voice is exactly what a new visitor sounds like. Bystander rejection comes only from directedness evidence.
- **"Never withhold a label."** Withholding identity is safe; withholding a *response* is not. Keep the two decisions separate.

## Why it matters for public-robot interaction
Groups are the normal case at a stand. Attribution decides whether the robot answers the child who asked or the parent who did not, and whether a phone call nearby derails the conversation. The asymmetry, permissive on "answer?" and strict on "who?", is the core lesson.

## Terms introduced
- **speaker attribution** — labelling each utterance with who said it.
- **direction of arrival (DoA)** — the bearing of a sound source estimated from inter-microphone delays.
- **TDOA** — time difference of arrival between two microphones.
- **GCC-PHAT** — cross-correlation with phase-transform weighting for delay estimation (Knapp & Carter 1976).
- **SRP-PHAT** — steered response power: GCC-PHAT summed over microphone pairs on a grid of directions.
- **spatial aliasing** — phase wrapping between two microphones above c/(2d).
- **active-speaker detection (ASD)** — a vision score of whether a face's mouth moves with the audio.
- **voice embedding** — a vector characterising a voice, compared by cosine similarity.
- **basis** — the evidence branch that produced a label.
- **modal bin** — the most frequent bearing bin over a turn.
- **directedness** — whether speech is addressed to the robot.
- **honest abstention** — publishing a null id with a reason instead of guessing.
- **roster** — the durable list of present visitors given to the model.
