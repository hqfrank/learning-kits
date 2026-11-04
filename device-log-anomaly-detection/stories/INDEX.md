# Stories — device-log anomaly detection

Picture-first, interactive pages. Open one before the notes to get the mental model; the notes stay
the reference.

| Story | Teaches | Spec |
|---|---|---|
| [01 — The night-shift mechanic](01-the-night-shift-mechanic.html) | Ring buffers lose the evidence; a share of devices from a small family is noisy (SE ∝ 1/√n); weighted least squares, a slope test against a practical threshold and p → score; templates and parameters, and why mining misses error templates; windows, count vectors and isolation-forest scores; per-thread transition edges and the usual route; anomaly ≠ issue (second signal) and the detection rate with its Wilson interval. | [spec](01-the-night-shift-mechanic.spec.md) |

## Rubric scores (story.md §9, 1–5)

| Story | Answer-first | Metaphor fidelity | Motion meaning | Text economy | Interaction | Truth | Craft | Access |
|---|---|---|---|---|---|---|---|---|
| 01 | 5 | 4 | 4 | 4 | 5 | 5 | 4 | 4 |

Notes on the scores:

- **Answer-first 5.** The hero shows the whole pipeline in one picture (lit cars ping the depot board, the board picks cars, the mechanic reads an odd page, one work order leaves), and a four-stage ticket row under it links B4, B1, B3 and B6.
- **Metaphor fidelity 4.** The metaphor is the brief's "night-shift mechanic", made tighter: the self-tearing logbook is the ring buffer, rubber stamps with blanks are templates with parameters, and the road is the household network, so "the road, not the car" is the environmental anomaly. It loses a point because the Wi-Fi route nodes ("joining", "on the road") ask the reader to map a car onto a network connection. Five "where it breaks" items are listed in the footer.
- **Motion 4.** Torn pages fly out of the book (overwrite). Pings leave only the lit cars (metrics are event-triggered). The normal page keeps being written while the odd page stays fixed. Random cuts draw in one by one (each one is a question). Parameters lift out of their blanks, and a token runs along the departing edge. Every step changes something visible. The hero's ping loop is the only ambient motion.
- **Text economy 4.** Captions are one bold claim plus one or two sentences. Scenes 3 and 5 have six and five steps, and their captions sit near the upper word limit.
- **Interaction 5.** There are three predict-then-reveal moments, each with a plausible wrong answer ("3 % is 3 %", "0.82 = 82 % chance", "odd book, broken car"). There are three live figures, each on one pure model (share SE vs n, questions → score, Wilson interval vs k/n) and five scene players.
- **Truth 5.** 31 kit constants are inlined verbatim from `../constants.json` into `#params`, and seven `story_*` picture values sit in a second block with class and source. Captions pull every number through `{{key}}` placeholders. Eight `console.assert` self-tests reproduce the notes' numbers: SE 1.7 / 0.17 points, score 0.82 / 0.50, Wilson 31–83 % and 50–69 %, 93 windows, and score 20 / 50 at p = 0.01 / 10⁻⁵. Hedges follow A0/C4 ("a lead, not a verdict"; "almost all on normal paths").
- **Craft 4.** One palette with one meaning per hue (sun = metric, sky = log, coral = odd, leaf = normal, plum = environment, stone = people), and consistent navy outlines. Verified with `shoot.py` (no console errors, no failed asserts, no overflow at 1280 px or 390 px, 23 scene steps) and by reading the first screens, the contact sheet, the phone full page, the engineer view of scenes 3, 5 and 6, the three answered predicts and the sliders at their extremes (n = 10 000; 16 questions; k/n = 60/100 and 5/5). Fixes made during verification: the shared `svg text{font-family}` rule overrode the monospace attribute (moved to inline style); slope units were scaled twice; label collisions in the trend inset, the tallies and the road bubble; the cast road icon overflowed on phones.
- **Access 4.** Scene players work from the keyboard (←/→). Every SVG has `role="img"` and an `aria-label`/`<title>`, captions and readouts are `aria-live`, and there is a Motion-off switch. Reduced-motion and still mode show representative frames (pings mid-flight, a lit lamp, written lines). Garage/Engineer dual labels mean no state is encoded by colour alone (pens use letters and dash styles). Contrast was not measured with a tool.

## Credits

Shared runtime ideas adapted from [nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer)
(MIT): the stepper/scene player, one pure model per live figure, figures lead and words label.
Narrative shape (start from a question, concrete first, therefore/but beats, end in a sandbox) from
Nicky Case, [How I make explorable explanations](https://blog.ncase.me/how-i-make-an-explorable-explanation/).
One idea per scene from [geeklee/srt-whiteboard-animation](https://github.com/geeklee/srt-whiteboard-animation).
Metaphor seed ("the night-shift mechanic") from the kit brief.
