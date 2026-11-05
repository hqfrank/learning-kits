# Rung 1.5 — Visual stories (learn-story)

A story page is the **first thing a learner opens** on a topic. It makes one idea *felt* in 5–10 minutes
through a metaphor, pictures that move, and two or three moments where the learner must predict before
seeing. The notes stay the reference; the story is the hook and the mental model. It sits between the
notes (rung 1) and the explorers (rung 3): a story links down to notes for depth and out to explorers as
its sandboxes.

Reference implementation (read it before building anything):
`learning/robot-workload-benchmarking/stories/01-the-robots-kitchen.html` with the shared runtime
`learning/stories/story.css` + `learning/stories/story.js` and the checker `learning/stories/tools/shoot.py`.

Sources this guide distils (credit them in INDEX.md when you borrow an idea):
Nicky Case, *How I make explorable explanations* (start with a question, concrete first, "therefore/but"
beats, end in a sandbox) · Bret Victor, *Up and down the ladder of abstraction* · nicobailon/visual-explainer
(MIT: figures lead and words label, one claim per figure, every arrow a verb, every number a picture,
stepper/scene player, live figure with one pure model) · geeklee/srt-whiteboard-animation (one idea per
scene, ink-then-colour reveal, storyboard confirmed before render) · The Pudding, *Responsive scrollytelling*
(keep it scrolly or stack it; decide mobile on purpose).

---

## 1. The bar — a page ships only if every line is true

1. **First screen = the answer as a picture.** Headline states the claim in one sentence; the hero picture
   shows it without reading. A newcomer who stops here leaves with the right idea.
2. **One master metaphor, cast on screen.** A cast row maps every metaphor character to its real term.
   A **Kitchen view / Engineer view** switch (`data-view-switch`) swaps every label between the two.
3. **A "Where the metaphor breaks" list** in the footer: 3–5 places the analogy would mislead.
4. **5–8 scenes, one claim each**, linked by *therefore / but*. At least one twist ("but the counter
   says 200 ms").
5. **Pictures lead, words label.** ≤ 60 words of prose per scene outside captions; captions ≤ 2 lines.
6. **Motion carries meaning.** Every animation shows a rate, a flow, a queue, a state change or a cause.
   Decorative motion is cut.
7. **≥ 2 predict-then-reveal moments** (`.st-predict`), each with a specific "why" for every option,
   wrong ones included.
8. **≥ 1 live figure** (one pure `model(settings)` feeding picture + numbers + sentence) and **≥ 2 scene
   players** (stepped, user-driven).
9. **Truth.** Every number comes from the kit's `constants.json` / explorer `params.json`, inlined verbatim
   in `<script type="application/json" id="params">` and rendered as the footer sources table. Illustrative
   values carry a visible `illustrative` tag on the figure. Claims match the notes' own hedges
   ("usually", "often"). No new facts that the notes do not support.
10. **Ladder out.** Each scene links its note (`a.read-note`); the page ends with "Your turn" links to the
    explorers (sandboxes), the notes and the quiz.
11. **Access.** Keyboard for every control (←/→ in scene players), `role="img"` + `aria-label`/`<title>`
    on every SVG, `aria-live` captions, text contrast ≥ 4.5:1, no colour-only encoding, a Motion off
    switch, `prefers-reduced-motion` honoured, still mode shows a representative frame (not frame 0).
12. **Verified by eye.** `shoot.py` reports no problems and you have *looked at* the first screen, every
    step of every scene (contact sheet), the phone first screen, both label views, and one answered
    predict. Scores in §9 all ≥ 4.

## 2. Before building: the story spec (show it to the user unless told to proceed)

Write `stories/<NN>-<slug>.spec.md` (kept beside the page):

- **The question** the learner should come to care about, in their words.
- **The one-sentence answer** (the headline) and the hero picture in one sentence.
- **Metaphor + cast table:** metaphor character → real term → why it fits → where it breaks.
- **Scene list:** for each scene — claim · beat (therefore/but) · figure type (scene player / live / predict /
  cards / static) · what moves and what it means · interaction · note it comes from · numbers used (key in
  constants.json + class).
- **Palette meaning:** one hue per real concept, kept for the whole page (e.g. coral = CPU, sun = GPU,
  sky = memory, leaf = deadline, plum = large model, stone = observer).

Pick the metaphor for *mechanism fidelity*, not cuteness: the cast must behave like the real thing in the
ways the scenes rely on (a time card drains faster with more burners; a pantry door is shared). Good
families: a kitchen (shared resources, orders, deadlines), a factory floor or workshop (pipelines, teams in
lockstep), a city with roads and warehouses (memory hierarchy as distance/travel time), a post office
(messages, queues, sorting), a theatre crew (cues, timing). Reuse one family across a kit's stories so the
cast becomes familiar.

## 3. Narrative shape

1. **Hero:** the answer as a picture + headline + cast row.
2. **Concrete first:** the first scene is something the learner can watch or touch, grounded in the
   metaphor. Climb the ladder of abstraction one rung per scene; bring back the real term each time.
3. **Beats:** "this happens, *therefore* … *but* …". A scene that is just "and also" gets merged or cut.
4. **Predict before reveal** at the twists. The reveal is a picture, not a paragraph.
5. **End with a sandbox and an open question:** "Your turn" cards to the explorers and the quiz.

## 4. The motion vocabulary (all provided by `story.js`; see its header comment)

| Need | Use | Rules |
|---|---|---|
| A mechanism in order | `figure.st-scene` scene player: parts with `data-s`, captions `ol.st-cap > li` | Opens on step 1 with JS (no-JS/print shows all). Never autoplay; Play replays from 1. Something visibly changes at every step. 3–8 steps. |
| A part only on some steps | `.st-at[data-s="2 3"]` | Draw the empty slot underneath. |
| Lighting a part again | `data-s="1 4"` + class `lit` on the shape | The emphasis step is the "therefore". |
| A flow or a hand-off | `.st-tok` on `offset-path` (`--dur`, `--d`) | Runs once per lit step; bursts ~150 ms apart. |
| Growth along time | `.grow` (scaleX from the left) | For "runs until…" bars. |
| Feel a setting | live figure: `Story.bind(root, model, render)` with `input[data-k]` | 1–3 controls; default = the real/source value; formula in a `<details>`; pure model + `console.assert` self-tests reproducing the page's claims. |
| A guess before the answer | `.st-predict` + `[data-choice]`, one `[data-right]`, `data-why` each; `.st-gated[data-gate]` revealed after | The question is concrete and numeric when possible. |
| A catalogue | `button.st-card` flip cards: front = picture + metaphor name + real name, back = Looks like / Really / Caught by | ≤ 6 per page; link the full list. |
| Ambient life | `.st-loop` CSS animations | Only if it shows a real rate or flow; add a still-mode rule showing a representative frame; paused off-screen. |
| Point at the same thing twice | `data-ref` linked highlighting | Cast card ↔ figure part. |
| Two vocabularies | `.lbl-k` / `.lbl-e` pairs (helper `dual()`) | Every label in figures and key sentences gets both. |
| Phone | `svg[data-wide]` | Wide diagrams scroll sideways at a readable size instead of shrinking. |

Rendering rules:
- Draw with inline SVG built by a small `el()` helper; characters are `<symbol>`s reused with `<use>`, coloured
  through CSS custom properties (`style="fill:var(--c,#EE6A45)"`), outlines as **presentation attributes
  inside the symbol** (document CSS classes are unreliable inside `<use>` shadow trees).
- Never set a blanket `svg text{fill:…}` rule: CSS beats the `fill` attribute and silently recolours every
  label. Use `svg text:not([fill])`.
- Page drawing script runs **before** `story.js` (so `data-s` parts exist); live bindings run **after** it.
- `?shot=1` gives deterministic screenshots; `?scene=<id>&s=<n>` deep-links a step; `?view=eng` opens the
  engineer labels. `Story.go(id, n)` is the scripting hook.
- No CDN, no framework, no build. Shared CSS/JS by relative path `../../stories/`.

## 5. Visual style — register "Paper" (default)

- Warm paper `#F7EFE2`, cards `#FFFAF2`, ink navy `#1D2A44`, outline `#141C2E` at 2–3 px with round joins,
  flat fills with at most one shade band, dot eyes, a blush — friendly toon characters. Diverse skin tones.
- Display font stack `"Avenir Next","Nunito","Trebuchet MS"`, heavy (800) for headings; a hand font only
  for small "voice" labels. Never system-ui alone.
- 5–6 hues, each meaning one concept for the whole page; legend under the hero.
- A dark "Blueprint" register (navy ground, cyan/amber lines) is allowed for hardware internals; keep the
  same motion vocabulary.
- **Never:** emoji as icons, gradient blobs, glassmorphism, violet-on-white "AI" look, stock 3D, a wall of
  text, a chart without a picture of what it counts, more than one metaphor family on a page, a number
  without its class tag when it is illustrative.

## 6. Writing

- Headline = the claim, hedged exactly as the notes hedge it.
- Captions: lead with the bold claim ("**Hard real-time.** …"), then one sentence of why. Use the
  metaphor word with its real term the first time (`lbl-k`/`lbl-e` or "time card (CPU quota)").
- STE-ish plain English: short sentences, active voice, one term per concept. Numbers with units.
- Glossary links for real terms; a `.st-term[data-tip]` tooltip for a one-line definition.

## 7. Truth and public safety

- Same rules as principles.md: every number is public, sibling-kit, or labelled illustrative; load it,
  do not retype it. Reuse explorer cases (cite the case name) rather than inventing new values.
- If the kit is published publicly, run the public-safety scan the repo uses before handing back.

## 8. Verification loop (do it, then look)

```bash
~/.local/share/learn-kit/venv/bin/python learning/stories/tools/shoot.py learning/<kit>/stories/<page>.html /tmp/story-shots/<slug>
```
It loads the page at 1280 px and 390 px in still mode, records console errors and failed
`console.assert`s, flags horizontal overflow, saves the first screens, the full pages, every step of every
scene, and `contact.png`. Then **read the PNGs back** (first screens, contact sheet, phone full page) and
script a second pass for states the tool does not cover (an answered predict, the engineer view, a flipped
card, live figures at both slider extremes). Fix and re-run until clean. Typical bugs it catches: labels
recoloured by a CSS rule, ambient loops frozen at an invisible frame 0, text overlapping a character,
flip-card backs clipped, tables overflowing on phones, scenes captured mid-scroll.

## 9. Self-critique — score 1–5, ship only if all ≥ 4, write the scores into stories/INDEX.md

| Criterion | 5 looks like |
|---|---|
| Answer-first | Hero alone teaches the headline. |
| Metaphor fidelity | Each cast member behaves like its real counterpart in every scene; breaks are listed. |
| Motion carries meaning | Remove any animation and something is lost. |
| Text economy | You could read only the headline, captions and figures and still get it. |
| Interaction teaches | Predictions provoke a wrong guess that the reveal corrects. |
| Truth | Every number traceable to constants/params with class; hedges match the notes. |
| Craft | Consistent palette and outline; no overlaps or clipped text at either width. |
| Access | Keyboard, labels, reduced motion, contrast all checked. |

## 10. Files

```
learning/stories/story.css · story.js · tools/shoot.py        shared runtime (edit with care: every story uses it)
learning/<kit>/stories/NN-<slug>.html                          one self-contained page per story
learning/<kit>/stories/NN-<slug>.spec.md                       the agreed spec
learning/<kit>/stories/INDEX.md                                list, one line each, + rubric scores + credits
```
Link new stories from the kit README ("Start here: the story") and from the site landing page.
