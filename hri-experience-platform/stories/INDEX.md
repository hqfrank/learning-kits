# Stories — A platform for many robot experiences

Picture-first, interactive pages. Open one before the notes to get the mental model; the notes stay
the reference.

| Story | Teaches | Spec |
|---|---|---|
| [01 — The stage manager](01-the-stage-manager.html) | Why the second experience forces a kernel (A0); the reasoner proposes, the coordinator decides and invokes (A1, B6); an experience as a pure reducer with a timer and participant-only admission (B1, B2, B4); resource claims and what may overlap, in the C2 showcase order (B3, C2); one ordered queue and safety interception first (B4); release only on quiescence proof, forced cleanup and recovery (B3, B2); the conformance ladder, what simulation cannot prove, and switching only between shows (C1, C2, B5). | [spec](01-the-stage-manager.spec.md) |

## Rubric scores (story.md §9, 1–5)

| Story | Answer-first | Metaphor fidelity | Motion meaning | Text economy | Interaction | Truth | Craft | Access |
|---|---|---|---|---|---|---|---|---|
| 01 | 5 | 4 | 4 | 4 | 5 | 5 | 4 | 4 |

Notes on the scores:

- **Answer-first 5.** The hero shows the whole split. The voice in the wing sends slips, every slip goes over the stage to the stage manager's desk, and cues go out from the desk only, to the control bar, the follow-spot and the microphone. The safety curtain hangs above. An audience member's wave is crossed out as "not the volunteer". The headline states the claim in both vocabularies.
- **Metaphor fidelity 4.** Note A0 already uses "the kernel is the stage manager; each experience is one act". The brief's improv troupe stays as *the voice*. A **puppet** is added so that "the model holds no motion tool" is visible: the voice can never reach the strings. Stations map one to one: control bar = action slot, follow-spot = gaze lease (it shares the head, which drives the "spot must clear first" step), microphone = per-turn audio-out lease. "Clear!" = quiescence proof, the repertoire = the registry, the rehearsal room = the simulation target. It loses a point because a stage manager has judgement and the kernel has none, and because a theatre's safety curtain *is* the guarantee, where on the robot the hardware stop is. Five "where it breaks" items are in the footer.
- **Motion 4.** In the hero, slips ride to the desk and cues ride out from it, which is the one-way authority flow. In the scenes, tokens carry the slip, the cue, the "not now" reply, the safety note to the curtain, and the act climbing the ladder. Held-interval bars grow lane by lane in scene 4. Still mode shows the riders partway along their paths.
- **Text economy 4.** Each caption is a bold claim plus one or two sentences. Scenes 4 and 7 have the longest captions.
- **Interaction 5.** Four predicts, each with a plausible wrong answer: "the puppet hands it over", "one thing at a time", "the lease expired", "the rules are proven". Two live figures. The cue sheet (wave time × volunteer/audience) shows the wave, timer-first and rejected-at-the-door branches. "Clear" timing × cleanup time left shows released, forced cleanup and recovery, including the C3 clamp. Five scene players.
- **Truth 5.** The 8 kit entries are inlined verbatim from `../constants.json` and `../explorers/params.json` by a generator that scans the page for keys and checks for drift. There is one `story_*` picture value, the default wave time. Captions pull numbers through `{{key}}` placeholders, and every number is tagged illustrative. Scene 4 is labelled "order only, not to scale" because the notes give no times there. Self-tests (`console.assert`) reproduce these rules: settle ≤ ceiling < cleanup (B3); a wave before the timer enters `wave` (B1); a non-participant's wave is rejected and the timer ends the act (B2/B4); a tie goes to the timer (explorer 01's queue order); clear after the settle deadline gives forced cleanup, and after the cleanup deadline gives recovery; a cancel 600 ms before the cleanup deadline is clamped to 600 ms (C3).
- **Craft 4.** One palette throughout (sky = act, plum = voice, sun = stations and cues, leaf = volunteer and proof, coral = safety and refusal, stone = audience and stand-ins) with navy outlines. Verified with `shoot.py`: no console errors, no failed asserts, no overflow at 1280 px or 390 px, 25 steps. An extra Playwright pass covered the engineer view of the hero and scene 1, both live figures at four and five settings (slider extremes included), an answered wrong predict, and the gated figure opening. Fixes made during verification: an arrow crossing the puppet and its label, slip text struck through by the slip's lines, a label colliding with the reset chips, the ladder's bottom label under the switch band, truncated lane labels, the audience clipped and colliding with its note, coinciding deadline labels, and a readout that mixed "after the invitation" with "into the act".
- **Access 4.** Scene players work from the keyboard (←/→). Every SVG has `role="img"` and an `aria-label` or `<title>`. Captions and readouts are `aria-live`. Sliders and the checkbox are labelled. There is a Motion-off switch. Verdicts are written out (✓/✗ plus words), never colour alone. Contrast was not measured with a tool.

## Credits

Shared runtime ideas adapted from [nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer)
(MIT): the stepper/scene player, one pure model per live figure, figures lead and words label.
Narrative shape from Nicky Case, [How I make explorable explanations](https://blog.ncase.me/how-i-make-an-explorable-explanation/).
One idea per scene from [geeklee/srt-whiteboard-animation](https://github.com/geeklee/srt-whiteboard-animation).
Metaphor seed ("the stage manager and the improv troupe") from the kit brief and note A0, extended with a puppet.
