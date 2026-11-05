# Stories — public robot interaction design

Picture-first, interactive pages. Open one before the notes to get the mental model; the notes stay
the reference.

| Story | Teaches | Spec |
|---|---|---|
| [01 — The host at the garden gate](01-the-host-at-the-garden-gate.html) | Speak first, listen only after a visible answer (answer-as-consent, the listening budget, the session lease, nothing kept); one offering at a time, a no is a no, offering runs out so every visit ends; beats → dwell → cycle → guests per hour (live); who spoke: coarse bearing bins gate, mouth motion chooses, the mode of the turn, honest abstention off camera; gaze: not the nearest, hold when contested, hold the addressee, eased glide vs saccade, ordered gates; self-hearing, the spectral guard and why its onset grace was switched off; the degradation rungs the visitor must never notice. | [spec](01-the-host-at-the-garden-gate.spec.md) |

## Rubric scores (story.md §9, 1–5)

| Story | Answer-first | Metaphor fidelity | Motion meaning | Text economy | Interaction | Truth | Craft | Access |
|---|---|---|---|---|---|---|---|---|
| 01 | 5 | 4 | 4 | 4 | 5 | 5 | 4 | 4 |

Notes on the scores:

- **Answer-first 5.** The hero shows the headline: the host looks at the child who spoke (not the nearer parent), holds the ear trumpet up because the child answered, the flower basket and the hourglass sit on the gateposts, passers-by keep walking along the lane, and the gardener and the "back soon" sign wait out of sight behind the hedge. Seven chips under it link A3, A1, A2, B2, B3, B4 and C1.
- **Metaphor fidelity 4.** Note A0 already uses the garden-gate host, so the story reuses it (principles: reuse the notes' analogy). The garden supplies the spatial parts the mechanisms need: fence panels = coarse direction bins, the hedge = the camera's field of view (off camera), the lane = open-world arrivals, the hidden gardener = the Wizard-of-Oz floor, the sign = the curtain, the clogs = the robot's own motors. It loses a point because a trumpet *is* hearing (the robot's microphones are always physically there) and because people do not hear their own footsteps amplified; six "where it breaks" items are in the footer.
- **Motion 4.** Passers-by walk the lane (arrivals never stop); a voice token travels from the speaker to the host's ears; the listening budget bars grow in order (detect, then show) against the 1 s flow limit; the lease bar grows and is cut when the guest leaves; a token walks the chat path; the gaze cone eases to its target (the transition is the glide), and two dots race the saccade and glide curves; a clatter token rises from the clogs to the trumpet. Still mode shows walkers mid-lane.
- **Text economy 4.** Captions are one bold claim plus one or two sentences; the guard caption (scene 6 step 3) and the fix caption (6b step 4) are at the upper limit.
- **Interaction 5.** Four predicts with tempting wrong answers (open on presence; "the reset does not count"; name the parent in front; "the host asks again"). The onset-grace scene is gated behind its predict. One live figure (converse beat and reset → cycle → guests per hour, with the chatty cap) and six scene players; five flip cards.
- **Truth 5.** 43 kit entries are inlined verbatim from `../constants.json` by a generator that scans the page for keys; three `story_*` picture values (guest bearings, one turn's bearing samples, the 40° glide distance) carry class and source. Captions pull every number through `{{key}}` placeholders. Self-tests (`console.assert`) reproduce: beats sum to 80 s, cycle 100 s, 36 and 25 per hour, 150 per day, a 10 s shorter reset gives about 3 more guests per hour; 300 + 200 = 500 ms under the 1 s limit; parent and child share a 45° bin and the radio is outside the 90° view; the modal panel holds 70 % of 10 samples; saccade 21 + 2.2 × 40 ≈ 109 ms; the 40° glide at 1.5 rad/s ≈ 0.7 s; the reply at 1.7 s lands inside the 2 s grace; the guard threshold sits between clatter and voices. The reply length in scene 6b and the spread of the guard dots are labelled schematic / illustrative; only the stated bounds are constants.
- **Craft 4.** One palette (sun = host speaking, sky = listening, plum = guests' voices, leaf = the flower, coral = mistakes and self-noise, stone = time and hidden help; guests' shirts are neutral so no hue is spent on them) and navy outlines. Verified with `shoot.py` (no console errors, no failed asserts, no overflow at 1280 px or 390 px, 27 steps) and an extra Playwright pass: four answered predicts, the live figure at four settings (default, minimum, maximum, reset −10 s), the engineer view of the hero and five scenes, a flipped card, and a DOM check that no `{{placeholder}}`, NaN or undefined is left. Fixes during verification: garden flowers on top of two hero labels, the headline pushing the hero below the fold, labels hidden under bars drawn later (consent and self-hearing scenes), step-1 bars staying on later steps (`st-at`), lit paths drawn over the host, crowded panel and hedge labels, a tall modal-bin bar over its sample row, glide labels clipped at the right edge, timeline labels running past the edge, the sign text overflowing its board.
- **Access 4.** Scene players work from the keyboard (←/→); every SVG has `role="img"` and an `aria-label` or `<title>`; captions and readouts are `aria-live`; sliders are labelled; a Motion-off switch; verdicts are written out (✓/✗ plus words), never colour only; the trumpet's state is a shape and a label, not a colour. Contrast was not measured with a tool.

## Credits

Shared runtime ideas adapted from [nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer)
(MIT): the stepper/scene player, one pure model per live figure, figures lead and words label.
Narrative shape from Nicky Case, [How I make explorable explanations](https://blog.ncase.me/how-i-make-an-explorable-explanation/).
One idea per scene from [geeklee/srt-whiteboard-animation](https://github.com/geeklee/srt-whiteboard-animation).
Metaphor from the kit brief ("the host at the garden gate") and note A0's own analogy, extended with the
hedge, fence panels, clogs and the hidden gardener.
