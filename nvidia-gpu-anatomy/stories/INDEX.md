# Stories — NVIDIA GPU anatomy

Picture-first, interactive pages. Open one before the notes to get the mental model; the notes stay
the reference.

| Story | Teaches | Spec |
|---|---|---|
| [01 — The GPU city](01-the-gpu-factory.html) | A warp is 32 threads under one instruction; four sub-partitions cap a block at 4 issues/tick; latency is hidden by switching warps, not by guessing; the memory ladder (registers → L1/shared → L2 → DRAM) as travel distance; the L2 cliff (~12×); reuse/tiling as keeping the part on the bench. | [spec](01-the-gpu-factory.spec.md) |

## Rubric scores (story.md §9, 1–5)

| Story | Answer-first | Metaphor fidelity | Motion meaning | Text economy | Interaction | Truth | Craft | Access |
|---|---|---|---|---|---|---|---|---|
| 01 | 5 | 5 | 4 | 4 | 4 | 5 | 4 | 4 |

Notes on the scores: **Metaphor fidelity 5** — latency-as-distance and reuse-as-keep-on-the-bench are
literally spatial facts, so the city carries the mechanism rather than decorating it; the five
"where it breaks" items are listed in the footer. **Truth 5** — every board number is inlined
verbatim from `../constants.json` (a cited subset of the sibling metrics kit) and rendered as the
footer sources table; tick↔latency mappings and the 30 MB / 32× teaching values carry an
`illustrative` class; hedges ("an order of magnitude", "12–15×") match the notes. **Interaction 4**
and **Motion 4** — two predict-then-reveal gates (latency hiding, the L2 cliff), one live figure (the
memory map, Orin/Thor × four levels) and five scene players; motion shows issue cadence, runner
round trips, the capacity cliff and tiling, never decoration. **Access 4** — keyboard scene players,
`role="img"`/`aria-label` on every SVG, `aria-live` captions, a motion-off switch, reduced-motion and
still-mode frames, City/Engineer dual labels (no colour-only encoding). Verified with
`shoot.py` (no console errors, failed asserts or overflow at 1280 px and 390 px; 20 scene steps) and
by reading the first screens, the contact sheet, the phone page, the engineer view, both answered
predicts and the live map at both board/level extremes.

## Credits

Shared runtime ideas adapted from [nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer)
(MIT): the stepper/scene player, one pure model per live figure, figures lead and words label.
Narrative shape (start from a question, concrete first, therefore/but beats, end in a sandbox) from
Nicky Case, [How I make explorable explanations](https://blog.ncase.me/how-i-make-an-explorable-explanation/).
One idea per scene / ink-then-reveal from [geeklee/srt-whiteboard-animation](https://github.com/geeklee/srt-whiteboard-animation).
Ladder-of-abstraction framing (a slider that moves one concept up and down a hierarchy) after
Bret Victor, *Up and down the ladder of abstraction*.
