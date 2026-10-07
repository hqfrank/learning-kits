# Learning Quiz

Single-file quiz app over the learning kits in `learning/`. Double-click `index.html`. No server, no build.

- Topics → sections → quiz. Each section's questions come from that section's note.
- Every question is tagged with a **knowledge point**. A wrong answer drops the point to Leitner box 0 (asked again next session); right answers move it up (box 1 → 1 day, 2 → 3 days, 3 → 7 days, 4 → 21 days). The Review list and the "Review session" surface the weakest points first.
- Progress lives in this browser's `localStorage` under `learning-quiz-v1`. "Reset progress" clears it.

## Adding a bank

Banks are generated from a kit's notes by the `learn-quiz` agent (rung 5 of the learning kit). One file per section, `banks/<topic>__<section>.js`, listed in `banks/manifest.js`.

```js
window.QUIZ_BANKS = window.QUIZ_BANKS || [];
window.QUIZ_BANKS.push({
  topic: "nvidia-gpu-anatomy",                 // kit folder name
  topicTitle: "Anatomy of an NVIDIA GPU",
  section: "01-sm-and-smsp",                   // note file stem; sorts the section list
  sectionTitle: "01 — The SM and its four sub-partitions",
  notePath: "../nvidia-gpu-anatomy/notes/01-sm-and-smsp.md",
  knowledgePoints: {
    "smsp-dispatch-bound": { title: "One dispatch port per sub-partition", summary: "Each SMSP issues at most 1 warp instruction per cycle; the SM at most 4.", source: "01-sm-and-smsp §How it works; Table 1 (D)" }
  },
  questions: [
    { id: "q1", type: "mcq", kp: "smsp-dispatch-bound",
      prompt: "How many warp instructions can one SM issue per cycle at most?",
      choices: ["1", "4", "32", "128"], answer: 1,
      explanation: "Four sub-partitions × one dispatch port each.", source: "01-sm-and-smsp; Table 1" },
    { id: "q2", type: "tf", kp: "...", prompt: "...", answer: false, explanation: "...", source: "..." },
    { id: "q3", type: "numeric", kp: "...", prompt: "...", answer: 256, unit: "KB", tolerance: 1, explanation: "...", source: "..." },
    { id: "q4", type: "multi", kp: "...", prompt: "Select all that apply.", choices: ["a","b","c","d"], answer: [0,2], explanation: "...", source: "..." }
  ]
});
```

Question types: `mcq` (one correct index), `tf`, `numeric` (with optional `unit` and absolute `tolerance`; default ±5 %), `multi` (array of correct indices). Prompts and choices accept `` `code` `` and `**bold**`.
