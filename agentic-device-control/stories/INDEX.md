# Stories — Agentic control of a consumer device

Picture-first, interactive pages. Open one before the notes to get the mental model; the notes stay
the reference.

| Story | Teaches | Spec |
|---|---|---|
| [01 — The dispatcher and the two hands](01-the-dispatcher-and-two-hands.html) | The message path's four guards and "one result per task"; the orchestrator plans one step and routes to the vision specialist or the actuator, hub and spoke, and finishes only on evidence; reference-frame scaling and why a steady offset is a scaler bug; per-step reliability compounds (0.9⁵ ≈ 0.59) and the ReAct loop recovers; three nested limits; cost = calls × tokens and prompt caching (a miss costs more than no cache); screen text is data, allow-list, confirmation gate, audit log; evaluate with a Wilson interval and a failure taxonomy. | [spec](01-the-dispatcher-and-two-hands.spec.md) |

## Rubric scores (story.md §9, 1–5)

| Story | Answer-first | Metaphor fidelity | Motion meaning | Text economy | Interaction | Truth | Craft | Access |
|---|---|---|---|---|---|---|---|---|
| 01 | 4 | 5 | 4 | 4 | 5 | 5 | 4 | 4 |

Notes on the scores:

- **Answer-first 4.** The headline states the claim, and the hero shows the dispatcher at the hub with
  radio tokens going out to one hand and back, plus the guards and the single reply slip. At 1280 px the
  first screen shows the headline and the top of the hero, but not all of it.
- **Metaphor fidelity 5.** The radio dispatcher is note 02's own analogy. It enforces the mechanism: the
  hands never talk to each other, every turn returns to the hub, and the dispatcher only talks. "Where
  the crew breaks" lists five limits (the model runs in the cloud, there is no memory outside the state,
  one photo per look, plain-code guards, keys cover the OS only).
- **Motion meaning 4.** Order and slip tokens show the message path. Radio tokens show the hub-and-spoke
  round trip. Scene-player tokens show each hop. The scaler finger moves with the bug. The binder pages
  change colour by cache status. The blinking tap mark in the hero is the weakest motion.
- **Text economy 4.** You can follow the page from the captions and figures alone. Scenes 5 and 6 are
  close to the 60-word limit.
- **Interaction 5.** There are three predicts: BUSY or queue, the scale-back point (the uniform-scale
  distractor is a real bug), and 0.9⁵. There are two live figures: the scaler, with two bugs, and the
  cache binder, where a miss costs more than no caching. There are four scene players and six flip cards.
- **Truth 5.** 30 constants are inlined verbatim from `../constants.json` by key and rendered as the
  footer table. Captions use `{{key}}` templates, so no number is retyped. Derived values (scales,
  products, 2 425 units / 35 %, the 15 of 20 s budget, the Wilson 67–89 %) are computed on the page.
  Eight `console.assert` self-tests reproduce the notes' arithmetic. Illustrative values carry the tag.
  The invented task IDs and log entries are labelled as such.
- **Craft 4.** One palette and one outline style throughout. No overlaps or clipped text at 1280 px and
  390 px after fixes. Wide figures scroll sideways on phones.
- **Access 4.** Scene players work with the keyboard. Every SVG has `role="img"` and a label. Captions
  use `aria-live`. There is a motion-off switch and reduced-motion still frames. Crew/Engineer dual
  labels mean no meaning rests on colour alone.

Verification: `shoot.py` reports no console errors, failed asserts or overflow at 1280 px and 390 px
(20 scene steps). I also read the first screens, the contact sheet and the phone page. A scripted pass
covered: the Engineer view (hero, graph step 2, loop step 5, safety step 3), all three predicts answered
(right and wrong), the opened compounding figure, the scaler at both slider ends with each bug, the
cache select at "no caching" and "miss", and a flipped card.

## Credits

Shared runtime and patterns from the kit family's story runtime (`../../stories/`). Ideas adapted from
[nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer) (MIT): the scene player,
one pure model per live figure, figures lead and words label. Narrative shape (start from a question,
concrete first, therefore/but beats, end in a sandbox) from Nicky Case,
[How I make explorable explanations](https://blog.ncase.me/how-i-make-an-explorable-explanation/).
One idea per scene from [geeklee/srt-whiteboard-animation](https://github.com/geeklee/srt-whiteboard-animation).
