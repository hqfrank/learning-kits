# Explorers — rung 3 (learn-explorer)

Four single-file HTML explorers for the *public-robot-interaction-design* kit. Open one with a double-click, or
`open 01-gaze-state-matrix.html`. They need no server, network or build step.

Each page inlines its parameters in a `<script type="application/json" id="params">` block, also shipped as `params.json`.
Every entry is copied verbatim (value, unit, class, source) from `../constants.json` by key. Nothing is retyped. Prose
numbers on the pages are filled from the same block. Values that only one page's model needs are named `page_*`. They are
class `illustrative`, and their source starts "page model choice (not in constants.json)". The pure model sits between
`/*MODEL-START*/` and `/*MODEL-END*/` and runs unchanged under node. Its `selfTest(P, assert)` runs `console.assert` on the
page and in node. The page prints the pass count above its sources table.

**This kit has no measurements.** Every number is `public` (a cited paper or physics arithmetic on public values) or
`illustrative` (a round teaching value, or a page choice). There are no measured overlays. Sources: this kit's `notes/`,
`glossary.md` and `constants.json` only.

| File | Teaches | Inputs | Notes |
|---|---|---|---|
| `01-gaze-state-matrix.html` | A gated gaze policy holds the addressee and refuses to rally; following every label flickers; "nearest" faces the wrong person | policy, 1–4 visitors, who speaks, robot answers, turn length, hold time, glide cap, label noise, picture time | B3 (B2, B4) |
| `02-direction-of-arrival.html` | TDOA → bearing; integer-lag coarseness, noise vs spacing and mic count, aliasing; the bearing gates faces and abstains | 2/4 mics, spacing, talker bearing, estimator, timing noise, binning, faces A/B | B2 |
| `03-turn-taking-timeline.html` | No VAD threshold separates motors from a talker; the spectral guard and its onset grace each move the error somewhere else | VAD threshold, debounce, self-voice suppression time, guard, onset grace | B4 |
| `04-dwell-budget.html` | Beats → dwell → cycle → visitors per hour; the queue grows when arrivals exceed the cycle | six beats, reset, friction, arrivals, show day | A2 (C2) |

---

## Spec — 01-gaze-state-matrix.html  (note B3, with B2 and B4)

```
Explorer: A gated gaze policy looks at fewer wrong people, less often, than one that follows every label
Teaches:  The head should face whoever it answers, change target only on trustworthy evidence, and hold still when unsure.
          A state-matrix cell (reasoner state × who the label names) says what the head wants. The gates (self-speech
          suppression, slew hold, deadband, dwell, contested) decide whether it may re-aim now. Motion is a smoothstep glide
          with a peak-speed cap, not a saccade.
Inputs:   policy: gated / follow every label / nearest visitor (first design); visitors 1–4 (page layouts inside the service
          arc and Hall's zones); who speaks (P1–P4 take turns); robot answers after each turn; turn length 0.6–6 s;
          hold time 0.2–5 s (default gaze_dwell_illustrative); glide cap 0.3–6 rad/s (default head_slew_cap_illustrative);
          label noise 0–40 %; picture time.
Outputs:  share of scored time within page_on_target_tol of the right person (speaker while a visitor talks, addressee
          otherwise); re-aims per minute; time in transit; 40° glide time vs 40° saccade; suppressed decisions per gate;
          active matrix cell. — simulate_gaze, glide_smoothstep_B3, glide_duration_B3 (T = 1.5·d/cap),
          saccade_duration_B3 (21 ms + 2.2 ms/°), ema_t95_B3, alternation_duty_B3.
Picture:  top-down stand with the head ray at the picture time; a yaw-vs-time history with visitor bearings, turn bands and
          re-aim marks; the state matrix with the active cell outlined.
Cases:    three visitors, robot answers (10 % noise) · two friends talk to each other (1.2 s turns, robot silent) · the far
          visitor asks · group of four, 30 % noisy labels · one visitor, quiet room.
Overlays: none.
Out of scope: pitch, frames and field of view, duty-cycle look-away scheduling, sector glance, pursuit of a moving face.
```

Page-model choices (all labelled on the page): the addressee changes only when the robot answers a turn (B3: the reasoner's
verdict, not vision); for one hold time after a visitor turn the cell is "triaging → hold"; a new label becomes the
gated policy's subject after `page_challenger_ticks` consecutive wins (B2: "a challenger must win several consecutive
evaluations"); "contested" = the subject changed at least twice within two hold times.

Self-tests (54): the note's saccade 109 ms, EMA 0.57 s, alternation duty 0.71 (inside the listening band, outside the
speaking band), the bands bracket the public 75 % / 41 %, the deadband is about 3°, smoothstep peak slope 1.5; layouts
inside the service arc and Hall's zones; the yaw limit covers the arc; rally: the label-follower re-aims ≥ 3× as often and
the contested gate fires; far visitor asks: nearest < 20 %, gated > 80 % on target; noisy group: the label-follower
flickers > 2× as often, the gated policy is on target more, and self-speech suppression fires; seeded runs replay exactly;
the head stays inside the yaw limit for every case and policy.

## Spec — 02-direction-of-arrival.html  (note B2)

```
Explorer: A small array hears direction coarsely, so the bearing gates faces and never picks one
Teaches:  τ = x·sin θ / c for microphones x apart; inverting it gives θ. Integer-sample lags are coarse (12.4° per sample
          on a 10 cm pair at 16 kHz near broadside, worse toward endfire); timing noise shrinks with aperture and mic
          count; phase wraps above c/(2d). Fusion (B2): one face in the window → bind; two → abstain (defer to active-
          speaker detection); none → flag "no face at that voice".
Inputs:   2 or 4 microphones (uniform line); spacing 2–20 cm (default 10 cm, recovered from tdoa_max_10cm); talker bearing
          −85…85°; estimator integer lag at 16 kHz / sub-sample; timing noise 0–60 µs per mic; continuous angle or 45° bin;
          face A bearing; face B on/off and bearing.
Outputs:  neighbour-pair TDOA, maximum TDOA, one seeded estimate, RMS error (page_mc_trials seeded trials), least-squares
          standard deviation, alias frequency, fusion verdict. — tdoa_B2, tdoa_max_B2, one_sample_angle_B2,
          spatial_alias_B2, bearing_std_ls, estimate (LS slope of delay vs position), fuse_B2.
Picture:  top-down array, plane wavefronts, true and estimated bearing rays, the face window wedge, faces; RMS error vs
          spacing with the region where aliasing falls inside the illustrative speech band shaded.
Cases:    10 cm pair, integer lag · same pair, talker near endfire · noisy room, four mics · two faces in one bin window ·
          a phone off camera.
Overlays: none.
Out of scope: reverberation as a physical model (timing noise stands in), front–back ambiguity, circular arrays, MUSIC,
          SRP-PHAT grids, the per-turn modal bin.
```

Self-tests (21): tdoa_max 292 / 146 µs, 62.5 µs sample period, 2.1 cm per sample, 12.4° per sample, alias 3.4 / 1.7 kHz,
effective window = gate + half a bin (37.5, printed 40); noise-free sub-sample estimates are exact; integer lag reads 0°
for 5° and 12.4° for 10°; Monte Carlo RMS matches the least-squares formula within 8 % for 2 and 4 mics; 2 → 4 mics cuts
the error by √10; error grows toward endfire; the three fusion verdicts; the endfire case's integer-lag error is more than
twice the broadside case's.

Finding: I first expected the endfire integer-lag error to be ≥ 3× the broadside error. The model gives 2.4× (13.0° vs
5.4°), so the test and wording say "more than twice".

## Spec — 03-turn-taking-timeline.html  (note B4)

```
Explorer: Every guard against phantom turns is also a way to miss a real visitor
Teaches:  On the processed channel the robot's motors (20 dB) are louder than a nearby talker (17 dB, my arithmetic: 20 − 3),
          and the leaked self-voice is 15 dB until suppression engages. No VAD threshold removes phantom barge-ins without
          losing a visitor. The spectral guard rejects motors but passes the robot's own voice. The onset grace rejects the
          self-voice but also a prompt reply to a 1.5 s greeting, and one rejection ends the visit.
Inputs:   VAD threshold 8–24 dB (default page_vad_threshold_default); debounce 0–1.2 s (default barge_in_debounce_
          illustrative); self-voice suppression time 0–1.5 s (default page_leak_default, the late end of the leak window);
          spectral guard on/off; onset grace on/off.
Outputs:  phantom barge-ins, ghost turns, visitor utterances heard (of those reached), barge-in latency, visit continues /
          stalls; decision log. — simulate_turns, talker_level_B4, threshold_sweep.
Picture:  lanes for robot speech (with the leak shaded), robot motion, visitor speech (heard / lost), processed level against
          the threshold, decisions; a sweep of phantoms and losses against the threshold.
Cases:    no guard · guard with onset grace · guard, no grace · guard, lower threshold · raise the threshold · long debounce.
Overlays: none.
Out of scope: end-of-turn silence and fragmentation, the pre-roll, transcription, continuity defects, the head-nod loop.
```

One scripted visit (`page_tt_script`): a greeting of `proactive_greeting_illustrative`, a reply `turn_gap_typical` after
it ends, a long answer with two nods and an arm gesture, a short interjection, a real barge-in, a goodbye, plus a head
turn while idle. The sweep plays the whole script without the stall rule so both directions are counted; stalls are
marked separately.

Self-tests (22): talker 17 dB, motors louder than the talker; the guard threshold sits between the fitted classes; a prompt
reply lands inside the grace; the default suppression time is inside the leak window; pre-roll 48 000 bytes; per case:
the arm gesture's phantom barge-in and the idle ghost turn (no guard), the rejected reply and stall (grace), no phantom
barge-in and a barge-in honoured after one debounce (guard, no grace), the ghost turn outside the guard's scope, the
self-voice passing the guard at a lower threshold, a stall and three losses above the talker level, the lost interjection
with a long debounce; for debounce 0.2 / 0.4 / 0.6 s without the guard, every threshold has a phantom or a loss; edge
cases at zero debounce.

Findings while building: (1) when a nod and the leaked self-voice overlap, the guard passes the onset because the
self-voice supplies a vowel; the decision log says so. (2) With zero debounce the first nod cuts the answer off, which
cancels the later nods; my first claim ("every nod cuts the robot off") was wrong and was replaced.

## Spec — 04-dwell-budget.html  (note A2, with C2)

```
Explorer: Throughput is 3600 divided by the cycle, not the dwell
Teaches:  Beats add to a dwell; dwell + reset = cycle; 3600 / cycle × friction = visitors per hour; the arithmetic runs
          backwards to say how much the cycle must shrink for a given arrival rate.
Inputs:   six beats (defaults beat_*_illustrative), reset, friction, arrivals per hour (default page_arrivals_default),
          show day.
Outputs:  cycle, theoretical and realistic throughput, served per day, queue at close and its wait; downstream checks
          (endurance gate, gifts per day, chatty cap). — dwell_A2, cycle_A2, throughput_theoretical_A2,
          throughput_realistic_A2, cycle_needed_A2, queue_fluid (page model), endurance_verdict.
Picture:  one cycle as a stacked bar with the chatty cap; queue length over the show day.
Cases:    the kit's budget · chatty visitors (converse to the cap) · halve the reset · busy hour (arrivals = theoretical
          throughput) · shorten converse to keep up (derived from cycle_needed).
Overlays: none.
Out of scope: bursty arrivals and walk-aways (the fluid queue forms only above capacity), per-beat variability.
```

Self-tests (16): beats sum to 80 s, cycle 100 s, 36 per hour, 25.2 printed as 25, 25 × 6 = 150 (unrounded 151.2), the
endurance gate covers a day, the cap is above the typical dwell, cycle_needed inverts throughput, and each case does what
its name says.

Finding: at the kit's own budget the unrounded 151.2 visits per day exceed the 150-cycle endurance gate by one. The
note's 150 comes from the rate printed as 25/h. The page shows "edge" (holds at the printed rate, not at the unrounded
rate) and does not change any number.

---

## Verification

- `node` (model extracted from each page): every params entry equals `params.json` and `constants.json`; class and source
  present. Self-tests: 54 + 21 + 22 + 16 = 113 passed, 0 failed. NaN sweep over selector options × slider extremes:
  312 940 model outputs, 0 non-finite.
- `learning/stories/tools/shoot.py` on each page (desk 1280 px and phone 390 px, every preloaded case): 0 console errors,
  0 failed asserts, 0 overflow. Screenshots were read back for every page.
- Playwright sweep (every range at min/max one at a time, then all-min and all-max, × every select option × checkboxes
  on/off): 432 page states, no NaN / Infinity / undefined in the rendered text, no page errors.
- `learning/tools/public-scan.sh` on the kit: clean.
