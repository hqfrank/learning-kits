# learn-quiz — how to generate question banks from a kit's notes

## What a bank is

One JavaScript file per note (section), consumed by the single-file app at `learning/quiz/index.html`. It pushes one object into `window.QUIZ_BANKS` (schema in `learning/quiz/README.md`). Banks are plain scripts so the app works from `file://`. After writing banks, add each filename to `learning/quiz/banks/manifest.js`.

File name: `learning/quiz/banks/<topic>__<section>.js` (topic = kit folder name, section = note file stem).

## Knowledge points first, questions second

1. Read the note. Extract its **knowledge points** (KPs): the 4–10 distinct ideas a reader must hold after reading it. Each KP gets a stable id (`kebab-case`, unique within the topic), a one-line title, a one-sentence summary in the note's own terms, and a source (note section and, where the note cites one, the underlying table/section). The "In one sentence", "Common confusions" and "Terms introduced" sections are the richest seams.
2. Write **2–4 questions per KP**, 12–25 per section. A KP with only one question cannot be retested after a miss.
3. Every question carries `kp`, `explanation` (one or two sentences that teach, not just restate the answer) and `source`.

## Question quality rules

- Test understanding, not recall of phrasing. Prefer "which mechanism explains…", "what happens if…", "which of these is NOT…", "estimate…" over "what is the definition of…".
- Numbers only when the note gives them with a source; use `numeric` with a sensible `tolerance` and `unit`. Never invent a value.
- Distractors must be plausible and drawn from the note's own confusions (e.g. per-SM vs per-SMSP, registers vs register file vs cache line, L1 private vs L2 shared, issue vs latency).
- Mix types: roughly 50 % `mcq`, 20 % `tf`, 15 % `multi`, 15 % `numeric`; skip a type when the material does not support it.
- Avoid "all of the above"; keep choices parallel in form and length; exactly one correct answer for `mcq`.
- Prompts ≤ 40 words; choices ≤ 20 words. Inline `` `code` `` and `**bold**` are allowed.
- One question per section may be a scenario ("a 100 Hz control kernel shares the GPU with a VLA; which…") that ties the section to robotics; the rest stay inside the note.
- Reuse the glossary's wording for terms so quiz and notes never define a thing two ways.

## Process

1. Read `learning/<topic>/README.md`, `glossary.md`, `constants.json`, then the notes you were asked to cover.
2. For each note write the bank file, then validate it: `node -e 'window={QUIZ_BANKS:[]};require("./learning/quiz/banks/<file>");const b=window.QUIZ_BANKS[0];...'` — check every question's `kp` exists in `knowledgePoints`, `mcq` answer index is in range, `multi` answers are arrays, `numeric` answers are numbers, no duplicate ids, each KP has ≥2 questions.
3. Append the file names to `manifest.js` (keep existing entries; one per line, sorted).
4. Write or update `learning/quiz/BANKS.md`: one row per bank (topic, section, KP count, question count, date).
5. Open `learning/quiz/index.html` and read a screenshot back if a browser tool exists; otherwise at least confirm the manifest and bank files parse.

## What not to do

- Do not modify notes, the app, or other topics' banks.
- Do not generate questions from your own knowledge of the subject; only from the note (and the constants/glossary it cites). If the note is thin, write fewer questions and say so in BANKS.md.

## Variety and templates (added 2026-10-07)

- Aim for **4–5 questions per knowledge point**, each from a different *angle*: definition, mechanism ("why/what happens if"), contrast ("which is NOT" / per-SM vs per-SMSP), scenario (a robot workload), numeric. Never two questions that differ only in wording.
- **Derived numbers are asked with their inputs shown.** A ratio like 1.51× (clock × SM-count scaling) is not worth memorising; the prompt must supply the four inputs and ask for the ratio, or ask which kernel class the ratio applies to. The knowledge point is the *rule*, not the product.
- **Two-board numerics use a template** so the same point is asked on both boards from sourced constants: add `template: {values:{<name>:{orin:…,thor:…}}, answerFrom:"<name>"}` (numeric) or `answerByBoard:{orin:i,thor:j}` (mcq); write `{Board}`, `{board}` and `{name}` in prompt/choices/explanation. The app generates one variant per board (`id@orin`, `id@thor`). Values must be copied from `constants.json`.
- **Expand mode:** when asked to expand an existing bank, keep every existing `id` and knowledge point unchanged (progress is keyed to them), add new questions with fresh ids, and convert single-board numerics into templates where a second board value exists. Do not rewrite questions the user has not complained about.
