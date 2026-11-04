# Stories — robot stack contention

Picture-first, interactive pages. Open one before the notes to get the mental model; the notes are the reference.
**Every measurement in these stories is illustrative:** a round teaching number from [`../constants.json`](../constants.json), not data from any specific robot.

| Story | Teaches | Spec |
|---|---|---|
| [01 — Why the stack runs slow](01-why-the-stack-runs-slow.html) | Every service is slower in the full stack, and each has its own reason. The object detector waits for pool CPU, then for GPU turns next to the VLA (shown in a camera-plus-detector row; expected, not tested, in the full stack). The depth camera service loses frames to pool CPU and topic demand (provisional), not to GPU load alone. The interaction service's rise is mostly our own measurement probe. The voice chain pays for per-item logging that grows with history. The motor-control services do the same work in more cycles, and moving their cluster neighbours gives back about two thirds (path not isolated: board traffic also fell). The corrections are shown as part of the method. | [spec](01-why-the-stack-runs-slow.spec.md) |

Runtime: `../../stories/story.css` + `story.js`. They are linked, not copied, and were not edited.

Numbers: a throwaway generator copied 48 entries verbatim from `../constants.json` into the page's `#params` block. It found no missing keys. Captions fill numbers from that block with `{{key}}` templates, so no number is retyped in the prose. The footer table is rendered from the same block, with each entry's class (public, sibling, illustrative). Derived values are labelled "my estimate from `<key>`":
- wait share ≈ 50 %
- 1 + wait = 3 s of wall time per CPU-second
- 4.2× to 6× pool multiplier
- 150 × 1.5 = 225 ms of reading
- 1 − f = 0.35
- about 90 % observer share
- C\*/R ≈ 1
- the highest dose = 1.6 R, and the first test ≈ 40 % of R
- dose ×2 → wait ×4
- fan-out ≈ one fifth
- +100 ms for the detector next to the VLA

## Verification (shoot.py + a second Playwright pass)
- `shoot.py` (1280 px + 390 px, still mode): `problems: []`, 24 scene steps. I read back the desktop first screen, the contact sheet, the phone first screen and the phone page in sections. Fixes from this pass:
  - phone overflow from a long `code` key and a wrapping slider label
  - a camera verdict strip that covered the "one fifth" label
  - a mixed-up kitchen label on the camera's GPU bar
  - hero text touching the phone's left edge, because `header.hero` padding overrides `.wrap`
- The second pass, outside shot mode, checked:
  - the engineer view (hero and scene 1)
  - all five predicts answered with a wrong choice, with the gated reveals shown
  - every slider at both extremes
  - the log-filter toggle
  - a flipped card

  It logged no console errors and no failed asserts.
- Self-tests (`console.assert`) reproduce these claims:
  - detector: 100 + 50 + 30 + 20 = 200 ms
  - wait is half of the added time
  - 3 s of wall time per CPU-second
  - the curve's segment slopes equal `dose_slopes`
  - C\*/R = 1
  - 1.6 R and 40 % of R
  - convex: ×2 → ×4
  - 4.2× to 6×
  - 225 ms of reading
  - f above the line, and 1 − f = 0.35
  - 0.92 observer share
  - the camera's GPU-only loss is 0 Hz, and fan-out is one fifth
  - the VLA step is mostly blocked time

## QAE review applied (second pass)
- Gate ids renamed to generic ones (`p-insp`, `p-frac`, `frac`).
- Banner: "one worked case of a generic home-robot stack, simplified to teach the method".
- Hero line now says "two of the biggest full-stack numbers", not "reasons".
- Camera cause marked provisional on the hero ticket and the scene 1 chip. The scene 1 columns moved left so the wider chip fits.
- Motor row reads "cook time per loop"; scene 3 caption adds "(or the board's traffic)".
- Scene 6: dose ratio labelled "my estimate from `dose_curve_points`"; the corrections add the untested short bursts, worded as note B1 words it ("well below one time slice").
- Scene 7: last step adds B1's frame-time-slack caveat; the priority line now says it "brings back only part of it".
- The 0.05 s predict option is templated from `pool_wait_per_busy_camera_only`.
- Explorer 02 card says the fit is my estimate and per-process GPU time was not measured.
- Phone: the sources table renders as stacked cards (no letter-by-letter key breaks); the Motion button sits small at the bottom right with page padding below. Shared runtime not edited.
- Re-verified: `shoot.py` `problems: []` (24 steps); read back the desktop first screen, the contact sheet, the phone first screen and the phone sources table; a non-shot pass answered three predicts and shot the gated reveals.

## Rubric scores (story.md §9, 1–5)

| Story | Answer-first | Metaphor fidelity | Motion meaning | Text economy | Interaction | Truth | Craft | Access |
|---|---|---|---|---|---|---|---|---|
| 01 | 5 | 4 | 4 | 4 | 5 | 5 | 4 | 4 |

Notes on the 4s:
- **Metaphor fidelity:** the spice rack implies a single cause, and the alcove layout is a sketch. Both are listed under "Where the kitchen breaks".
- **Motion meaning:** the ticket flow, the oven alternation and the unrolling book carry meaning. Scene 1 mostly reveals values step by step.
- **Text economy:** scenes 6 and 7 need more caption text to keep the notes' verdict wording ("dose explains", "undecided at dose", post-hoc).
- **Craft:** on the phone, the hero's ticket row is below the first screen, and wide figures scroll sideways.
- **Access:** these are in place:
  - keyboard control
  - `aria-live` captions
  - a role and label on every SVG
  - encodings that do not rely on colour alone (hollow and dashed shapes)
  - the motion switch and reduced motion

  Contrast was checked by eye, not with a tool.

## Credits
- Shared-runtime ideas come from [nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer) (MIT): the scene player, one pure model per live figure, and "figures lead and words label".
- The narrative shape comes from Nicky Case, [How I make explorable explanations](https://blog.ncase.me/how-i-make-an-explorable-explanation/).
- One idea per scene comes from [geeklee/srt-whiteboard-animation](https://github.com/geeklee/srt-whiteboard-animation).
- The kitchen cast follows [the sibling kit's story 1](../../robot-workload-benchmarking/stories/01-the-robots-kitchen.html).

## Needs a constants entry
These numbers are not in `constants.json`, so the page draws them without a number:
- The stand-in speech service's fixed transcript delay after the commit. The head-of-line strip in scene 5 is schematic.
- The motor-control services' loop period. The bell has no number.
- How many cluster-mates were moved, and the window-to-window spread of f. Both are described in words.

The slider ranges are UI bounds, not claims:
- history items: 0 → `history_items`
- wait: `pool_wait_per_busy_camera_only` → 1.5 × `pool_wait_per_busy_full`
- O: 0 → the highest dose point

The order of GPU turns in scene 6 is labelled "illustrative order of turns".
