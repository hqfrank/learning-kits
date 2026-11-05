# B3 — Gaze: look at the speaker, hold the addressee, never flicker

**Source:** internal gaze design documents I5 (see [`../SOURCES.md`](../SOURCES.md)); Kendon 1967; Argyle & Ingham 1972; Vertegaal et al. 2001; Mutlu et al. 2009/2012; Admoni & Scassellati 2017; Carpenter 1988. · **Status:** concept primer; numbers are public or labelled illustrative.

## In one sentence
A robot's head should point at whoever it is answering, follow the speaker only on trustworthy evidence, hold still when unsure, compose every camera bearing with the measured neck angle, and move with calm, bounded glides, because a confident wrong turn tells a group the robot is talking to someone else.

## What it is
In human conversation, gaze carries turn-taking and participant roles. Listeners look at speakers more than speakers look at listeners (Kendon 1967). Commonly cited dyadic figures are about 75 % of listening time and about 41 % of speaking time spent looking at the partner (`gaze_listener_share`, `gaze_speaker_share`, Argyle & Ingham 1972). In multiparty talk, the person looked at is the person listened to with probability 0.88 and the person spoken to with probability 0.77 (`gaze_predicts_listened_to`, `gaze_predicts_spoken_to`, Vertegaal et al. 2001). Robot gaze can shape who feels like the addressee, a side participant or a bystander (Mutlu et al. 2009, 2012). Admoni & Scassellati (2017) review the field.

Three roles matter at the stand:

- **active speaker** — the person talking now;
- **addressee** — the person the robot is answering;
- **bystander** — someone present but not in the conversation.

## How it works

### Why nearest is wrong
The first design pointed at the nearest visitor. At a stand the normal case is a group, and the nearest body is often not the talker. Design rule throughout: **when unsure, hold still**. Four defects after the first multi-visitor use came from one gap, the gaze path had no model of whom the speech was for: the head locked on the biggest face; it followed two visitors talking to each other like a head following a rally; it never looked toward an off-camera voice; and it never lost interest in speech not addressed to it.

### Layers
Attribution (who, and their bearing in *its* camera frame) → face selector → **interest layer** (what should the head do: a cell of the state matrix) → **gaze policy** (may I aim now: ordered gates) → head controller (eased motion, nod overlay) → robot gateway (frame composition, limits, the only publisher). The policy emits *intent, never angles*. Decision code is pure and testable without a robot, a camera or middleware, driven by injected inputs and a clock.

### Trust
Each nomination is graded:
- **lock-eligible** — the basis is a mouth-motion winner or bearing-matched face, and the latest label for that visitor was evidence-backed and not contradicted;
- **attention-only** — largest face, nearest bearing, or a guess: a bounded glance at most;
- **refused** — the label says the face's mouth contradicts the audio.

An aim during user speech must name the utterance's *subject*; otherwise hold. "Grading decides lock versus glance; subject-matching decides whether there is anything to look at."

**Whom the speech is for comes from the reasoner, not from vision.** Vision "facing" is unreliable on small faces. The reasoner's triage already decides per utterance ([[B1-the-voice-pipeline]]), and its verdict can be read from the sequence of reasoner states: user speaking → triage → executing (or → robot speaking) means *accepted*; triage → listening or idle means *ignored*; no edge in time means *expired*. The accepted speaker becomes the addressee. In the revised design, an accepted or greeted visitor is lock-eligible by verdict, which fixed "it only follows me while I talk".

### Frames
| Frame | Moves with the head? |
|---|---|
| head camera | yes |
| fixed stand camera | no |
| robot body (microphone array DoA) | no |

**Composition rule:** target yaw = *measured* neck yaw + camera bearing, then clip. A head-camera bearing is never an absolute yaw. Using the *commanded* yaw instead of the measured one lets error accumulate, and the head "walks away" over successive re-aims. Bearings always travel with their frame name; null, never 0, means "no bearing", because 0 is dead ahead.

**Field of view.** A linear mapping, bearing = (x − 0.5) × FOV, with a wrong FOV under- or over-turns consistently. Example with illustrative values: a face at a true 30° (`fov_example_bearing_true`) on a camera whose true FOV is 90° (`fov_true_illustrative`), converted with a leftover 60° webcam default (`fov_default_illustrative`), reads as 17.3° (`fov_example_linear_wrong_fov`, my arithmetic). The head under-turns by 13°. Even with the right FOV the linear formula reads 26.0° (`fov_example_linear_right_fov`); the pinhole form atan((x − cx)/fx) is exact. For a 90° FOV the linear error peaks at about 4.1° about halfway to the edge (`linear_vs_pinhole_max_err_90`, my arithmetic). Take the focal length from the camera's own reported (rectified) intrinsics for the mode in use, never from a datasheet.

Pitch is a configured constant for a standing adult; the design must not derive pitch from apparent face size (a distance proxy). Aim slightly above the face-box centre so the robot appears to meet the eyes. The head yaw limit (an illustrative ±80°, `head_yaw_limit_illustrative`) covers the service arc (an illustrative ±60°, `service_arc_illustrative`), so no torso motion is needed. Sign conventions differ between control paths; assert the sign on the real robot in both axes ("why is it looking at the floor" bugs).

### Arbitration
Several sources compete for the neck: the gaze policy, the platform's own conversation posture, gestures, scripted beats, a human driving the robot remotely, and a nod. Two platform facts drove the design: inside the behaviour framework, head commands resolve **last-wins** by list order, and a built-in conversation posture overwrote yaw exactly during conversation; downstream, the motor arbiter is **priority-based**. The team published from one gateway at a priority above the behaviour layer. Other rules:
- In a beat that owns the head (the hand-over), the beat wins and gaze stands down. A robot that looks away from the hand it offers reads as distracted.
- Do not release the head claim for a short look-away; re-claiming races the arbiter's inactivity timeout.
- Verify enablement by observing motion, never by reading back a state flag.
- Gaze loss degrades to the old nearest-visitor gaze, never to no gaze.

### Gates (in fixed order; the order is the safety argument)
1. **Staleness** — never act on an old label.
2. **Evidence** — grade-aware.
3. **Self-speech suppression** — while the robot speaks and for a tail, do not switch visitor, because DoA may point at the robot itself; pursuit of the locked face by vision continues.
4. **Slew hold** — bearings taken during a head pan are least trustworthy.
5. **Deadband** — ignore changes under an illustrative 0.05 rad (about 3°, `gaze_deadband_illustrative`).
6. **Dwell** — no re-aim within an illustrative 2 s (`gaze_dwell_illustrative`).
7. **Contested** — if labels alternate faster than the dwell, hold. Never average two speakers: "a head pointed between two people addresses neither".
8. **Pursuit** — follow the same locked face frame by frame; disengage on face loss, never keep driving to the last bearing.
9. **Sector glance** — for directed but unresolved off-camera speech: a stable bearing for an illustrative 0.6 s (`sector_glance_hold_illustrative`), robot quiet, no override, then one acquisition glance toward the modal sector, time-boxed to an illustrative 3 s (`sector_glance_box_illustrative`). The glance only positions the camera; a face it finds earns gaze through the normal gates.

Every look-at and every *suppressed* decision is logged with a reason: a gaze that does not happen is the interesting case during bring-up.

### The gaze policy as a state matrix
Rows are reasoner states (idle, listening, user speaking, triaging, executing, robot speaking, resetting); columns are perception situations (addressee visible, another visible speaker, off-camera speech, a group of accepted people, nobody visible). Each cell emits one intent: lock, glance, sector aim, neutral (keep the claim), hold, or release. Examples: idle → release; user speaking with a lock-eligible subject → lock with pursuit; triaging → hold; robot speaking → hold the addressee, suppress retargeting, add a small speech-driven nod.

**Duty cycle.** The first matrix scheduled look-aways to hit design bands bracketing the human figures: an illustrative 65–85 % engaged while listening and 35–55 % while speaking (`gaze_band_listening_illustrative`, `gaze_band_speaking_illustrative`). Plain alternation fails: an illustrative 5 s gaze (`gaze_episode_mean_illustrative`) and 2 s look-away (`lookaway_mean_illustrative`) give 71 % (`alternation_duty_illustrative`, my arithmetic), inside the listening band and outside the speaking band. So a scheduler tracks the duty and chooses the next episode, with randomised (truncated Gaussian) lengths because people notice periodicity. Regulating on a rolling window shorter than the gaze cycle aliased and missed both bands; a cumulative reference held them. Randomness used one seeded generator, with the seed logged, so any session can be replayed.

**What live use changed.** Head look-aways took the face out of frame; the "nobody visible → neutral" cell then sent the head to centre, the face returned, and the head oscillated. The revision locked the head on the addressee, moved the look-away to an **eyebrow beat** (a social aversion cue that does not move the camera), and replaced "nobody visible → neutral" with "hold the last aim if there is an addressee", with a short face-loss grace. A robot-initiated greeting now adopts the approaching visitor as addressee.

### Motion quality: glide, not saccade
A human saccade of 40° takes about 109 ms (`saccade_40deg_duration`, from duration ≈ 21 ms + 2.2 ms/° in `saccade_duration_intercept`, `saccade_duration_slope`, Carpenter 1988). The team chose not to imitate it. Every head move is an **eased glide**, smoothstep s = 3t² − 2t³, with a duration that grows with distance and a peak speed (1.5 × distance / duration) capped at an illustrative 1.5 rad/s (`head_slew_cap_illustrative`). Compared with a position PID loop, the glide gives synchronised arrival on both axes, zero velocity at both ends, a rate clamp, a settable time-to-target and a clean completion event. It can only get "how fast" wrong, never "how damped", which mattered with intermittent access to a shared robot. A platform alternative, exponential smoothing with an illustrative α = 0.1 per 50 Hz tick (`head_ema_alpha_illustrative`), reaches 95 % in about 0.57 s (`head_ema_t95_illustrative`, my arithmetic) but never finishes cleanly. The trade: human-like snap for calm, bounded motion on a child-sized robot in public.

Anti-flicker devices: deadband, dwell, contested hold, slew hold, a face-selector challenger margin (an illustrative 30 % larger, `face_challenger_margin_illustrative`), a dropout grace that holds a missing incumbent at its last bearing for an illustrative 0.7 s (`face_dropout_grace_illustrative`), and re-binding a new id at the same place to the same person.

### Latency
Drive gaze from the earliest trustworthy label tier (an illustrative 250 ms, `label_t0_illustrative`, see [[B2-who-is-speaking]]); a gaze that lands after the turn has no communicative value. Measure speech onset → motion onset on the robot; label latency and settle time are separately tunable.

## How it is designed and tested
- **Offline pointing metric**, scored independently of visitor id (id fragments still carry the right face box): face-switch rate per utterance, bearing spread per speaker, and the share of utterances with no bearing; later, angular error against sparse annotations.
- **Robot-free harness** running the real behaviour framework with a simulated actuator: does yaw survive during conversation; does suppression, pursuit and the glance behave.
- **On the robot:** static-target pointing error, multi-re-aim convergence, sign in both axes, step response.
- Every matrix cell driven offline with an injected clock; seeded duty conformance over many seeds; a configuration guard that fails on any new numeric literal in decision code.

## Common confusions
- **"Look at the speaker" is the whole policy.** Looking at the person you are *answering*, while you speak, is the socially important half.
- **"Read back the state to check it is on."** Read-back state can lie; observe the effect.
- **"Smoother is always better."** Too slow a settle reads as sluggish; the maximum time to 95 % is a visitor-experience decision, measured on the robot.

## Why it matters for public-robot interaction
Gaze is the cheapest channel that works across a room and in silence ([[A0-why-strangers-are-the-hard-case]]). It is also the channel where a wrong move is most visible. Holding still under uncertainty and holding the addressee while speaking do more for perceived attention than fast tracking.

## Terms introduced
- **active speaker / addressee / bystander** — the person talking / the person being answered / a person present but outside the conversation.
- **interest layer** — the component that maps reasoner state and perception situation to a gaze intent.
- **gaze policy** — the ordered gates that decide whether an aim may happen now.
- **lock / glance / hold / neutral / release** — the gaze intents.
- **lock-eligible / attention-only / refused** — the trust grades of a face nomination.
- **composition rule** — absolute target = measured neck yaw + camera bearing.
- **pinhole bearing** — atan((x − cx)/fx), the exact bearing for a rectified camera.
- **contested state** — labels alternating faster than the dwell; the robot holds.
- **sector glance** — a time-boxed acquisition turn toward an off-camera voice.
- **duty cycle (gaze)** — the fraction of time spent looking at the addressee.
- **eyebrow beat** — a facial aversion cue used instead of moving the head.
- **eased glide** — a smoothstep head trajectory with a peak-speed cap.
- **saccade** — a fast eye movement; duration grows about linearly with amplitude.
