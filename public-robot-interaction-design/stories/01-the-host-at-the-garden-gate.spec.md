# Story 01 — The host at the garden gate (spec)

**The question.** "We put a small robot at a busy public stand. Strangers walk past in groups, in a loud
room, with no instructions. How should it greet them, listen, look at them, and fail, so that nobody
leaves with a bad moment?"

**Headline (the answer).** *A good host greets first, listens only after you answer, looks at whoever it is
answering, and fails so quietly that you never notice.*
Engineer view: *A public robot speaks first, opens its microphone only after a visitor action, aims its head at
the addressee, and degrades without a visible seam.*
Hedge source: A0 ("make every success need nothing from the visitor and make every failure invisible to them").

**Hero picture (one sentence).** A small gnome host at a garden gate turns its head to the child in a group of
three who just spoke, holds its ear trumpet up because the child answered, has a flower basket on one gatepost
and an hourglass on the other, while passers-by walk along the lane and a gardener with a cue card stays hidden
behind the hedge.

**Why this metaphor.** The brief's seed, and note A0 already uses it ("a good host at a garden gate greets each
guest, looks at whoever speaks, offers one small thing, and lets people go"). Principles: reuse the notes'
analogy. I checked two alternatives: a shop door-greeter (no group / off-sight mechanics) and a theatre (the
sibling kit `hri-experience-platform` already uses a stage manager; one family per kit). The garden gives
the spatial pieces the mechanisms need: a hedge for the camera's field of view, fence panels for coarse
direction bins, a lane for open-world arrivals, a hidden gardener for the Wizard-of-Oz floor, a gate sign for
the curtain. The host is drawn as a garden gnome so it reads as child-sized and not human.

## Metaphor + cast

| Metaphor | Real term | Why it fits | Where it breaks |
|---|---|---|---|
| The gnome host at the gate | the robot (a child-sized humanoid) | Acts first, greets, offers, lets people go (A0) | A real host remembers faces; the robot must never claim to remember anyone (A1 rule 8) |
| Passers-by on the lane | strangers at a public demo stand (open-world engagement) | No instructions, a few seconds, arrive and leave freely (A0) | — |
| The ear trumpet, raised | microphone capture + listening indicator under a session lease | Visible, shape not colour; up only after the guest answers; down when they leave (A3) | A trumpet *is* the hearing; the robot's microphones are always there, so "down" is a promise kept by an audio gate, and a content-free voice detector runs before consent |
| The flower basket | the small gift on a self-serve tray | Needs no words; reached at every tier (A3, C1) | — |
| Three garden paths from a little plaza | the offer hub and its offerings (chat, gift, photo) | One path at a time; a closed path stays closed (A1) | Paths are places; offerings are per-visit flags (mentioned / offered / declined) |
| The hourglass | the dwell budget and the cycle | Beats run down the glass; turning it over is the reset (A2) | — |
| Fence panels | direction-of-arrival bins (coarse, 45°) | A voice lights one panel; two guests can share a panel (B2) | Panels have sharp edges; real bins thrash within a turn and can point at the robot's own voice or a reflection |
| Watching lips | active-speaker detection | Chooses among guests the panel cannot separate (B2) | — |
| The hedge | the edge of the camera's view (off camera) | A voice from behind the hedge has no face to bind (B2, B3) | The hedge is fixed; the head camera's view turns with the head (composition rule) |
| The host's clogs clattering | the robot's own motors (and voice) heard by its microphones | Every nod makes a noise that the trumpet hears (B4) | A person barely hears their own footsteps; the robot's processed channel *amplifies* them (gain wind-up) |
| The vowel check | the spectral barge-in guard | A real voice has a vowel; a clatter has none (B4) | — |
| "Ignore the first 2 s after I speak" | the guard's onset grace | Looks wise until the greeting gets short (B4) | — |
| The hidden gardener with cue cards | the Wizard-of-Oz operator (rung 4) | Guests cannot tell he is there (C1) | At the stand the operator is a planned floor, not a trick; a privacy script is ready if asked |
| The "back soon" gate sign | the curtain (L3) | Ends a fault out of sight (C1) | — |

## Palette meaning (whole page)
- **sun** = the host speaking (greeting, offers, lines)
- **sky** = listening (ear trumpet, microphone open, lease)
- **plum** = the guests' voices and who said it (attribution, gaze target)
- **leaf** = the flower and every path that still ends well (gift, accepted)
- **coral** = mistakes and the host's own noise (self-hearing, wrong target, rejected)
- **stone** = time and hidden help (hourglass, reset, gardener, sign)
- navy ink = the host

## Scenes

| # | Claim | Beat | Figure | What moves and what it means | Interaction | Note | Numbers |
|---|---|---|---|---|---|---|---|
| 1 | Speak first; listen only after the guest answers | — | predict + scene player, 5 steps | Host waves and greets (trumpet down); guest answers; four qualifiers tick; trumpet rises within the budget (bars grow: detect + signal under the 1 s flow limit); lease bar; guest leaves, trumpet drops, notebook empty | predict: when may the trumpet go up? | A0, A3 | `listening_indicator_*_illustrative`, `response_limit_flow` (public), `interaction_cap_illustrative`, `mic_close_on_permit_loss_illustrative` |
| 2 | One path at a time; a no is a no; so every visit ends | therefore | scene player, 5 steps | Offer the flower path → "no thanks" closes it → chat path + a mention (dashed bubble) → silence → one specific thing → all paths used → wave, gate closes, slate wiped | ←/→ | A1 | `offerings_illustrative` |
| 3 | Beats add to a cycle, and the cycle sets the queue | therefore | predict + **live figure** | Stacked hourglass bar of six beats + reset; a row of guests served per hour (theory outlined, realistic filled) | sliders: converse beat, reset | A2 | `beat_*_illustrative`, `reset_turnover_illustrative`, `queue_friction_factor_illustrative`, `show_day_illustrative`, `interaction_cap_illustrative` |
| 4 | Panels gate, lips choose, and behind the hedge the host names nobody | but (guests come in groups) | predict + scene player, 5 steps | A voice wave reaches two ears with a delay → one panel lights; two faces in one panel → lips choose; samples thrash → mode of the turn; radio behind the hedge → old rule names the silent parent (struck out) → "someone off camera"; two signposts: answer? lean yes · who? only on evidence | predict: who does the host say spoke? | B2 | `tdoa_max_10cm`, `doa_bin_illustrative`, `modal_bin_share_illustrative`, `modal_bin_min_samples_illustrative`, `cascade_turns_illustrative` |
| 5 | Look at whoever you answer; hold still when unsure; glide | therefore | scene player, 5 steps | Gaze cone points at the nearest (wrong) → a rally between two friends vs a held head → hold the addressee while speaking, look-away as an eyebrow beat → yaw-vs-time: saccade vs eased glide (a dot runs each curve) → the ordered gates | ←/→ | B3 | `saccade_40deg_duration` (public), `head_slew_cap_illustrative`, `gaze_dwell_illustrative`, `gaze_deadband_illustrative` |
| 6 | The host hears himself; a clever guard fixed that, then ended visits | but (twist) | scene player, 3 steps + predict + gated scene player, 4 steps | Clogs clatter louder than a guest; noise becomes words; the vowel check separates clatter from voices. Then a timeline: 1.5 s greeting, 2 s grace, reply at 1.7 s is thrown away, trumpet drops, guest leaves; default flipped off | predict: the short greeting and a prompt reply | B4 | `actuator_lift_processed_illustrative`, `motion_over_speech_processed_illustrative`, `noise_only_transcripts_illustrative`, `guard_*_illustrative`, `proactive_greeting_illustrative`, `turn_gap_typical` (public) |
| 7 | The guest must never tell which rung is running | therefore | 5 flip cards | Each front shows the host and the flower (except the sign); back: guest sees / really runs / entered when | flip | C1, A0 | `take_timer_illustrative` |
| — | Your turn | — | link cards | — | — | explorers 01–04, quiz, notes | — |

Story-only values (class illustrative, source says "story 1 picture value"): guest bearings for scenes 4–5 and
the bearing samples of one turn for the modal-bin step; the 40° glide distance comes from the public saccade
example in B3.
