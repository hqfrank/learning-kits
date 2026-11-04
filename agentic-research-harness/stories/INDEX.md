# Stories — agentic research harness

Picture-first, interactive pages. Open one before the notes to get the mental model; the notes stay
the reference.

| Story | Teaches | Spec |
|---|---|---|
| [01 — The time trial](01-the-time-trial.html) | Fast but wrong and Goodhart; the frozen, hash-pinned evaluator, gates calibrated from legitimate runs, held-out inputs and the binding ratio vs the margin cap; negative controls that must fail (and a control that was itself broken); evidence records and "cite or it did not happen"; the two memories; one round of the loop with paired baselines and caps; disjoint-range promotion vs a median rule; the rule meeting the work floor; the order of construction. | [spec](01-the-time-trial.spec.md) |

## Rubric scores (story.md §9, 1–5)

| Story | Answer-first | Metaphor fidelity | Motion meaning | Text economy | Interaction | Truth | Craft | Access |
|---|---|---|---|---|---|---|---|---|
| 01 | 5 | 4 | 4 | 4 | 5 | 5 | 4 | 4 |

Notes on the scores:

- **Answer-first 5.** The hero shows the whole method in one picture: the workshop, an honest car lapping the full course, a decoy cutting the chicane past a marshal's flag, the secret course in a sealed envelope, the sealed timing hut printing a numbered slip, and a champion board where the challenger's whole range is faster. Four tickets under it link B2, B3, B4 and B7.
- **Metaphor fidelity 4.** The notes' own analogy (A0) is a sealed-envelope contest. A time trial keeps all of it (sealed rulebook, sealed secret course, decoys, a numbered logbook) and adds what the scenes need: a speed metric, many laps per car, cutting the course as "doing less work", weather as measurement context, and the track's limit as the work floor. B6's coach joins unchanged. It loses a point because the scheduling topic's candidates ("smarter lane choice" for placement) ask the reader to map a scheduler onto a car. Five "where it breaks" items are in the footer.
- **Motion 4.** The decoy laps faster than the honest car because its route is shorter at the same speed (the loop periods are set from the path lengths). Tokens carry the slip into its folder, the drills to the builders, one car at a time onto the course, and the champion's re-run under today's cloud. Logbook rows grow in one by one. Every step changes something visible.
- **Text economy 4.** Captions are one bold claim plus one or two sentences. Scenes 4 and 5 have five steps with captions near the upper limit.
- **Interaction 5.** Three predict-then-reveal moments, each with a plausible wrong answer ("average 0.68 is well inside", "a median almost never crowns an equal car", "better median and worst lap must win"). Two live figures (two gates → closest call → verdict; 20 laps each → median rule vs every-lap rule with 1 000 seeded redraws), six scene players and four flip cards.
- **Truth 5.** 40 kit entries are inlined verbatim from `../constants.json` and `../explorers/params.json` by a generator that scans the page for keys; three `story_*` picture values sit in a second block with class and source. Captions pull every number through `{{key}}` placeholders. Self-tests (`console.assert`) reproduce: binding = max ratio (0.49); the predict case is "accepted, low margin"; 1 / C(40, 20) = 7.25 × 10⁻¹²; a median rule crowns an equal car about half the time and the every-lap rule almost never; C3's round-1 promotions and non-promotions; A1's big-gain-by-hand shape. The first campaign appears only through the kit's illustrative `c1_*` shape values.
- **Craft 4.** One palette (sun = clock, leaf = honest, coral = shortcut/decoy, plum = sealed, sky = course, stone = people) and navy outlines throughout. Verified with `shoot.py` (no console errors, no failed asserts, no overflow at 1280 px or 390 px, 31 scene steps) and by reading the first screens, the contact sheet, the engineer view of four scenes, the three answered predicts, both live figures at their extremes and a flipped card. Fixes during verification: an oversized headline pushed the hero below the fold; stopwatch bars overlapped the clock; gate-calibration labels collided; the INVALID stamp covered its label; queue arrows ran into the queue label; the hut label crossed the hand-in arrow; collapsed spaces in an SVG axis label.
- **Access 4.** Scene players work from the keyboard (←/→). Every SVG has `role="img"` and an `aria-label`/`<title>`, captions and readouts are `aria-live`, and there is a Motion-off switch. Still mode shows representative frames (cars mid-lap, the decoy on its shortcut). Verdicts are always written out, never colour only. Contrast was not measured with a tool.

## Credits

Shared runtime ideas adapted from [nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer)
(MIT): the stepper/scene player, one pure model per live figure, figures lead and words label.
Narrative shape (start from a question, concrete first, therefore/but beats, end in a sandbox) from
Nicky Case, [How I make explorable explanations](https://blog.ncase.me/how-i-make-an-explorable-explanation/).
One idea per scene from [geeklee/srt-whiteboard-animation](https://github.com/geeklee/srt-whiteboard-animation).
Metaphor seed ("the sealed-envelope contest") from the kit brief and note A0, moved to a time trial; the coach from note B6.
