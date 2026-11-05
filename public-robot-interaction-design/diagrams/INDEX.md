# Diagrams — Designing a humanoid robot's conversation with strangers (Rung 2, learn-diagram)

Six diagrams, one draw.io page each, exported to `.drawio` + `.svg` + `.png`. This is the picture
layer for the rung-1 notes: what a visit is (Part A) and the mechanics behind it (Part B). Every number
on every canvas is loaded from this kit's `constants.json` by key and tagged on the canvas: `[Pn]` =
public (a paper, standard or physics value, or my arithmetic on one), `[In]` = illustrative (a round
design value of the right order, **never a measurement of a real robot or visitor**), `[calc]` = my
arithmetic on tagged values, with the formula in the footnote. Each canvas carries its own legend and
sources block, so the exported image stands alone. A combined 6-page source,
`public-robot-interaction-design.drawio`, opens all pages at once.

**Sources used:** only this kit's `notes/`, `glossary.md` and `constants.json` (already generalised).
No internal figure was copied or traced; every picture is drawn fresh from the mechanism in the notes.
Positions in the top-down scene (04) and the length of the visitor's reply bar (06) are drawing
choices, not data; the canvases say so.

**Rendering:** each page is a list of cells in `specNN.py` (helpers in `_common.py`), rendered by
`.render_local.py` two ways from the same list: an editable `.drawio`, and a standalone `.svg`
(rect + XHTML `foreignObject` label per box) rasterised to `.png` with headless Chrome at 2x. Specs
never type a number: they call `V(key)` and `T(key)`, and several pages `assert` their own arithmetic
against the constants (the six beats sum to `interaction_typical_illustrative`; 3600 / cycle =
`throughput_theoretical_illustrative`; detection + signal = the listening budget; 0.10 m / c =
`tdoa_max_10cm`; the field-of-view readings, the 40 deg saccade, the smoothing t95 and the gaze duty
recomputed; greeting + turn gap < onset grace). Regenerate one page with
`python3 .render_local.py specNN.py`, then `python3 .render_local.py --combine`.

| File | Teaches (the finding in the title) | Sources used |
|---|---|---|
| `01-visit-state-machine` | A visit is a small state machine: every offering hangs off one hub and is offered at most once, so every visit provably ends; the language model only supplies the words inside each state. | Note A1 (overview, arrival, offer hub, eight invariants, mention vs offer, hub state, transition hygiene); B1 (safety supervisor); `offerings_illustrative` |
| `02-dwell-budget` | Beats add up to a dwell time, dwell plus reset is the cycle, and the cycle sets visitors per hour; the responsiveness budget sits under the public 1 s flow limit. | Note A2; C2 (endurance gate); `beat_*_illustrative`, `interaction_typical_illustrative`, `reset_turnover_illustrative`, `cycle_illustrative`, `take_timer_illustrative`, `per_turn_cap_illustrative`, `inactivity_timeout_illustrative`, `interaction_cap_illustrative`, `throughput_*_illustrative`, `queue_friction_factor_illustrative`, `show_day_illustrative`, `visits_per_day_illustrative`, `consecutive_cycles_gate_illustrative`, `listening_indicator_*_illustrative`; public `response_limit_instant`, `response_limit_flow`, `turn_gap_typical` |
| `03-where-the-llm-is` | Only one box in the stack is a language model; perception, the engage trigger, the body and the gaze are plain code that unit tests can prove; the model's behaviour can only be measured live. Also: on-rails vs speech-to-speech, the fail-closed audio ladder down to a hidden operator, the design invariants. | Note B1; `behaviour_tick_illustrative`, `wind_down_quiet_illustrative` |
| `04-who-is-speaking` | The face's moving mouth selects, the coarse microphone bearing only gates and corroborates, and a voice with no face is labelled 'unidentified'; permissive on "answer?", strict on "who?". | Note B2; public arithmetic `speed_of_sound_20c`, `tdoa_max_10cm`, `sample_period_16k`, `sample_path_16k`, `one_sample_angle_10cm_16k`, `spatial_alias_5cm`, `spatial_alias_10cm`; `doa_bin_illustrative`, `doa_face_gate_illustrative`, `doa_effective_window_illustrative`, `fov_true_illustrative`, `self_speech_tail_illustrative`, `label_t0/t1/t2_illustrative`, `asd_min_face_illustrative`, `voice_embedding_min_illustrative`, `voice_match_cosine_illustrative`, `voice_match_margin_illustrative`, `id_churn_token_cost_illustrative`, `cascade_turns_illustrative` |
| `05-gaze-gates` | Gaze aims the head only on trustworthy evidence, through gates in a fixed order where every failed gate means hold still; plus the frame rule, glide-not-saccade, and why plain alternation misses the speaking band. | Note B3; `gaze_deadband_illustrative`, `gaze_dwell_illustrative`, `sector_glance_*_illustrative`, `fov_*` examples, `linear_vs_pinhole_max_err_90`, public `saccade_duration_intercept`, `saccade_duration_slope`, `saccade_40deg_duration`, `gaze_listener_share`, `gaze_speaker_share`; `head_slew_cap_illustrative`, `head_ema_alpha_illustrative`, `head_ema_t95_illustrative`, `gaze_band_*_illustrative`, `gaze_episode_mean_illustrative`, `lookaway_mean_illustrative`, `alternation_duty_illustrative` |
| `06-guard-blind-spot` | Why the clever barge-in guard was turned off: its onset grace cannot tell a short greeting plus a quick human reply from self-hearing, so the visitor's first word was rejected and one rejection ended the visit. Also: the two sources of phantom barge-ins, how the guard scores, the written promotion rule, and "measure both failure directions". | Note B4; `proactive_greeting_illustrative`, `guard_onset_grace_illustrative`, public `turn_gap_typical`, `self_hearing_*_illustrative`, `actuator_lift_*_illustrative`, `motion_over_speech_processed_illustrative`, `noise_only_transcripts_illustrative`, `guard_*_illustrative`, `barge_in_debounce_illustrative` |

---

## Per-diagram specs (as built)

### 01-visit-state-machine
```
Teaches: one hub, offerings as equals, at most one offer each -> every visit terminates; the LLM fills words.
Type:    State machine (flowchart) + invariants side panel.
Elements: waiting, arrival, offer hub, three offerings, celebrate, no answer, just talking, closing, reset,
         needs staff; two global transitions drawn once (walks away, safety pause); eight invariants;
         mention vs offer; per-visit hub state.
Colour:  blue visit states, green offerings, amber no-answer/celebrate, red safety/staff.
Numbers: offerings_illustrative only.
Left out: groups and change-of-mind close-ups (prose in A1).
```

### 02-dwell-budget
```
Teaches: beats -> dwell -> cycle -> visitors/hour; the arithmetic runs both ways; responsiveness budget.
Type:    Waterfall timeline to scale (5.6 px/s) + arithmetic chain + ms-scale budget bar with reference lines.
Colour:  solid = planned beats, dashed = timers/caps, dashed verticals = totals or public limits.
Numbers: all beat lengths, caps, throughput chain illustrative; Nielsen limits and turn gap public.
Left out: pacing rules from the rehearsed act (C3/A2 prose).
```

### 03-where-the-llm-is
```
Teaches: one LLM among plain-code components; where to unit-test vs measure live.
Type:    Block diagram with message arrows + comparison table + staircase ladder.
Elements: mic array, head camera, perception, engage trigger, reasoner (+ wake gate, triage, guard),
         loudspeaker, behaviour library, gaze controller, robot gateway; on-rails vs open; 4-step ladder.
Colour:  purple = the LLM, blue = perception/trigger, green = body/gaze, grey = sensors/gateway.
Numbers: behaviour tick and wind-down quiet time, both illustrative.
```

### 04-who-is-speaking
```
Teaches: ASD selects, DoA gates/corroborates, abstain when the voice has no face.
Type:    Top-down scene (bins, FOV, face window) + physics box + tier timeline (to scale) + ladder + asymmetry.
Colour:  green talking, blue silent, grey bystander, red off-camera source/abstain.
Numbers: public DoA arithmetic; illustrative bins, gates, tiers, voice-match gates, churn cost.
Left out: roster/system-message formats and voice banking detail (B2 prose).
```

### 05-gaze-gates
```
Teaches: ordered gates, any failure -> HOLD; frame composition; glide not saccade; duty cycle.
Type:    Layer chain + gate pipeline with a shared HOLD sink + text panels + range chart.
Colour:  amber gates/bands, red hold/self-speech, green motion, blue frames, purple public gaze shares.
Numbers: public saccade and gaze shares; illustrative gates, slew, smoothing, bands, alternation.
Left out: the full state matrix (rows x columns) and arbitration details (B3 prose).
```

### 06-guard-blind-spot
```
Teaches: a defence becomes a cost when the interaction design changes underneath it.
Type:    Swimlane timeline to scale (220 px/s) + three panels + dB number line.
Colour:  purple robot speech, red self-hearing/rejection/failure, amber grace/threshold, green visitor.
Numbers: public turn gap; everything else illustrative; reply onset = greeting + gap [calc].
Left out: continuity defects and the head-nod loop (B4 prose).
```

## Files

Each diagram has `NN-slug.drawio` (editable), `NN-slug.svg` (vector, self-rendered, no draw.io
banner) and `NN-slug.png` (2x raster, read back and checked for legibility).
`public-robot-interaction-design.drawio` is the combined 6-page document. `specNN.py` is the cell
list each page is rendered from; `_common.py` holds the loader, tags and palette; `.render_local.py`
is the renderer.
