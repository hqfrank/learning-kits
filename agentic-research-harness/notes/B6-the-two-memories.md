# B6 — The two memories

**Source:** generalised from internal methodology notes, 2026 (§3.5); the harness memory module (`memory.py`) and README; the demonstration topic's `seed_lessons.md` and planner prompt. Size limit is a design parameter (`harness_lessons_max_lines`). · **Status:** concept note.

## In one sentence
The campaign keeps a fast, append-only log of every official attempt and a slow, short, curated lessons file that the planner rewrites every round, keeping negative results on purpose, plus one champion per track.

## What it is
Agents start every session with an empty context. The harness gives them memory in three files.

**Fast memory: the attempts log.** `attempts.jsonl` has one row per official evaluation: candidate, parent, agent, class, verdict, outcome, metric, paired baseline, binding ratio, note. Rows are only appended. Every agent sees a digest of the latest rows as a table.

**Slow memory: the lessons file.** `lessons.md` holds validated, transferable lessons. It is short (about `harness_lessons_max_lines` = 70 lines; design parameter, illustrative). Each lesson is short and cites a run id or a worklog section. The planner rewrites the whole file every round from the attempts and the researchers' reports. Each old version is kept as a backup. A fresh campaign seeds the file from the topic's `seed_lessons.md`, which is written from the hand-run rounds.

**Champions.** `champion.json` holds, per track, the champion's id and directory, its run id, metric, margin, since when, the reason for promotion and the previous champion.

## How it works
**Why two speeds.** The attempts log is complete but noisy: it grows every evaluation. The lessons file is selective: it says what the attempts mean. A researcher needs both: "what was tried" (fast) and "what we learned" (slow).

**Why negative results are kept.** An agent with no memory of a failed idea tries it again. The lessons file keeps failures deliberately, in the form "X did not help (run id); do not repeat without a new idea". The scheduling topic's seed lessons, for example, record that dispatch order alone did not move the metric under the baseline placement (see [[C3-calibration]]).

**Why the size limit.** A long lessons file is not read. The limit forces the planner to merge, drop what new evidence contradicts, and keep only what transfers.

**Structure that worked.** The scheduling topic's seed lessons have four sections: *Measurement* (how to compare, how noisy the metric is), *What the platform looks like* (calibration facts), *Open directions (no evidence yet)*, and diagnostics worth building first. Open directions are labelled as having no evidence, so they read as hypotheses.

Analogy: a coach who rewrites the team's one-page notes after every match, including the plays that failed.

## How it is used in a campaign
- The planner prompt includes the champions, the lessons and the attempts digest, and asks for a rewritten lessons file and the next tasks ([[B7-agents-and-the-loop]]).
- The researcher prompt includes the champions, the lessons and a shorter attempts digest.
- The evaluation worker writes attempts and champions. Agents never write either directly; the promotion policy does.

## Common confusions
- **"Memory means the model remembers."** The model remembers nothing between sessions. The memory is files the harness puts into each prompt.
- **"The lessons file is a summary of the worklog."** It is a curated, sourced set of rules that transfer. The worklog is the narrative; the lessons are what the next agent must know.
- **"Delete failures to keep it short."** Failures are the cheapest lessons to keep and the most expensive to rediscover.

## Why it matters
Without memory, each round of agents repeats the last round's mistakes. With an unbounded memory, nobody reads it. Two memories at two speeds, curated with sources, let each round start from what the campaign actually knows.

## Terms introduced
- **fast memory (attempts log)** — the append-only log of every official evaluation.
- **slow memory (lessons file)** — the short, curated, sourced lessons, rewritten by the planner each round.
- **seed lessons** — the initial slow memory, written from the hand-run rounds.
- **outcome** — the promotion result of an attempt: champion of a track, accepted, accepted with low margin, rejected, no evidence, or error.
