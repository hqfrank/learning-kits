# Stories — Wi-Fi CSI sensing

Picture-first, interactive pages. Open one before the notes to get the mental model; the notes are the reference.

| Story | Teaches | Spec |
|---|---|---|
| [01 — The spider's web](01-the-spiders-web.html) | CSI versus RSSI (notes, not loudness); where one link is sensitive; why room-independent features matter; why one link cannot tell which end; links grow with the square of the devices; the false-alarm budget; what still fools the system. | [spec](01-the-spiders-web.spec.md) |

## Rubric scores (story.md §9, 1–5)

| Story | Answer-first | Metaphor fidelity | Motion meaning | Text economy | Interaction | Truth | Craft | Access |
|---|---|---|---|---|---|---|---|---|
| 01 | 5 | 5 | 4 | 4 | 5 | 5 | 4 | 4 |

Notes on the scores: the hero alone shows "two threads shake, the third is calm → the fly is near A". Trembling threads are vibrating standing waves whose size tracks the modelled path amplitude (scene 2) and whose presence marks which links fluctuate (scenes 4, hero). Scene 1 and scene 2 numbers are computed live from the same multipath model as explorer 01, with `console.assert` self-tests for every claim the captions make. Craft and access are 4: checked by eye at 1280 px and 390 px, both label views, answered predicts, slider extremes and a flipped card; full assistive-technology testing was not done.

## Credits

Shared runtime ideas adapted from [nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer) (MIT): scene player, one pure model per live figure, figures lead and words label. Narrative shape from Nicky Case, [How I make explorable explanations](https://blog.ncase.me/how-i-make-an-explorable-explanation/). One idea per scene from [geeklee/srt-whiteboard-animation](https://github.com/geeklee/srt-whiteboard-animation). The spider's-web analogy is the one in note A1.
