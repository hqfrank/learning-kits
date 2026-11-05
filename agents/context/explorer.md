# learn-explorer — how to build a single-file interactive explainer

## What an explorer is

A single HTML file that turns the source's equations and measured constants into something the learner can move. Sliders change inputs; outputs and a picture update immediately; the mechanism becomes visible. It is a study aid, built to be regenerated, not maintained.

## Non-negotiables

1. **One file, no build step.** Vanilla HTML + CSS + JS (ES2022). Open with a double-click. No npm, no bundler, no CDN dependency at runtime (inline a small chart helper or draw with SVG/canvas yourself).
2. **Parameters live in a JSON block, each with a source.** Either an inline `<script type="application/json" id="params">` or a sibling `params.json` loaded with `fetch` when served. Every entry: `{ "value": ..., "unit": "...", "source": "..." }`. The page renders the source table; a learner can audit every number. If `learning/<topic>/notes/` or a constants file exists, derive the params from it; never retype.
3. **Prediction functions are pure and named after the source's equation.** `predict_latency_C1_1(params, inputs)`. Each has a one-line comment with the equation in words and its source.
4. **Measured points are overlaid where the source has them**, visually distinct from predictions (dot vs line). The gap between them is the lesson; never hide it.
5. **Preloaded cases.** Buttons that set the sliders to the real cases from the source (named workloads, named boards) so the learner starts from reality, not from arbitrary defaults.
6. **Accessible.** Keyboard-operable controls, labels on every input, live-region text for the headline output, colour never the only channel, contrast ≥ 4.5:1, respects `prefers-reduced-motion`.
7. **Honest labels.** "predicted", "measured", "estimated", "datasheet" appear next to every number they apply to.

## Spec first

```
Explorer: <name>
Teaches: <one sentence>
Inputs (sliders/selects): <name, range, unit, default, why this range>
Outputs: <name, unit, how computed (equation + source)>
Picture: <what is drawn and what moves>
Preloaded cases: <list with their source>
Measured overlays: <which, source>
Out of scope: <...>
```

Show the spec to the user before building unless told to proceed.

## Page layout (keep it this simple)

1. Title = the finding. One-paragraph "what you are looking at".
2. Controls on the left (or top on narrow screens), picture on the right, headline number(s) above the picture in large type with their labels.
3. "Why" panel under the picture: two or three sentences that change with the inputs, naming the mechanism that currently dominates.
4. Sources table at the bottom, generated from the params block.
5. Footer: generated date, source material, "this is a study aid; numbers are from the listed sources or labelled estimates".

## Engineering notes

- Compute in plain functions; render in one `update()`; debounce slider input with `requestAnimationFrame`.
- Use SVG for charts (crisp, inspectable, easy to label). Log axes when the source uses them (rooflines).
- Keep the file under ~60 KB. If it grows past that, the explorer is trying to do two things; split it.
- Put a tiny self-test at the bottom of the script: evaluate each prediction function at the source's own parameter values and `console.assert` it reproduces the source's predicted number within a stated tolerance. If the source's table and your function disagree, the function is wrong or the source has a typo; report it, do not fudge.

## Verification before declaring done

- Open the file (`open <file>` on macOS) or render it headlessly if a browser tool is available; read the screenshot back.
- Run the self-tests (open the console or run the functions under node if you factored them to be importable).
- Check every slider's extremes do not produce NaN/Infinity or an unreadable chart.
- Confirm the sources table lists a source for every parameter.

## Output

- `learning/<topic>/explorers/<nn>-<slug>.html` (+ `params.json` if external).
- `explorers/INDEX.md`: file, teaches, inputs, sources.
- Append to `SOURCES.md`.
