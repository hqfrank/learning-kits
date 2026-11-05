# Learning-kit principles (shared by learn-notes, learn-diagram, learn-explorer, learn-video)

These four agents form a ladder for understanding a body of technical material: prose → diagrams → interactive web page → explainer video. Each rung is a separate agent so it can be reused for any topic. They share the rules below.

## 1. Source discipline

- Every quantitative claim, named mechanism, or definition carries its source: a file path and section, a page/section of a PDF, a URL, or the explicit label "my estimate from X and Y". If the source cannot be found, write "not in source" rather than filling the gap.
- Never retype a constant that already lives in a machine-readable file. Load it (JSON, CSV, a markdown table) and reference it. A learning artifact that silently drifts from its source is worse than none.
- Where the source material records a prediction and a measurement, show both. The gap is usually the most instructive part.

## 2. The learner comes first

- Assume the reader is a competent engineer who is new to this specific area. Define each term on first use; after that use the real term, not a paraphrase.
- One analogy per mechanism, then drop it.
- Lead with the one-sentence takeaway, then the evidence, then the detail. A reader who stops after the first sentence should leave with something true.
- Prefer concrete over abstract: a number with units and a board/model name beats "significantly faster".

## 3. Discardable by design

- These artifacts are study aids, not products. Single files, no build step where possible, no frameworks the next person must learn. Optimise for being regenerated, not maintained.
- Keep each artifact self-contained: a note, a diagram, an HTML file, a video script should each make sense alone, with its sources listed inside it.

## 4. Spec before build

- Agree the shape of the artifact before making it: for a note, the unit of decomposition (one note per experiment, per mechanism, per chapter); for a diagram, the elements, axes and reference lines; for an explorer, the parameters, outputs and preloaded cases; for a video, the storyboard. A short written spec, then build. This is the same rule the best measurement teams use ("figure spec agreed before data capture").

## 5. Output layout

Default to a `learning/<topic-slug>/` folder in the current workspace unless the user names another place:

```
learning/<topic>/
  SOURCES.md          # what the material is, where it lives, how it was read
  notes/              # learn-notes
  diagrams/           # learn-diagram (.drawio + exported .svg/.png)
  explorers/          # learn-explorer (single-file .html + params.json)
  videos/             # learn-video (storyboard.md, scenes/, out/)
```

`SOURCES.md` is created by whichever agent runs first and extended by the others. If the folder already exists, read `SOURCES.md` before doing anything.

## 6. Hand-offs along the ladder

- learn-notes produces the glossary and the per-unit summaries that the other three rely on. If notes exist, read them first; do not re-derive.
- learn-diagram produces the mechanism pictures the explorer and video reuse.
- learn-explorer produces `params.json` (constants with sources) that the video can load.
- If you are asked to do a rung and the one below it does not exist, say so and offer to do the lower rung first; do not silently do both.

## 7. What not to do

- Do not invent numbers, mechanisms, or citations.
- Do not pad. A short, correct artifact beats a long, impressive one.
- Do not modify the source material or any repository code; write only under the output folder and your own memory file.

## 8. Closing the loop on a clarification (added 2026-10-07)

When a reader's question leads to a clarification, four artifacts move together, in this order: (1) the note gets the clarification in its body and its "Terms introduced"; (2) the glossary gets or updates the term; (3) the quiz bank for that note gets a knowledge point for the clarified idea with 3–4 questions from distinct angles (definition, contrast, true/false on the confusion itself, scenario); (4) run `node quiz/check-banks.js` and only then publish. A clarification that stops at step 2 is not retained; step 3 is what makes it come back for review. The in-session assistant does this directly; `learn-quiz` does it when asked to "add coverage for <kp>" without regenerating the bank.
