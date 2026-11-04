# B4 — Evidence records and "cite or it did not happen"

**Source:** generalised from internal methodology notes, 2026 (§3.3, §3.7); the harness README (layout, `report` command); the demonstration topic's AGENTS.md rule 5 and worklog conventions. · **Status:** concept note.

## In one sentence
Every evaluation writes one directory of evidence, every number anywhere in the campaign cites the run id of that directory, and reports are rebuilt from the directories, so no claim can drift away from what was measured.

## What it is
An **evidence record** is the output of one official evaluation, stored in its own directory. The directory is named by the UTC timestamp and the candidate id, for example `evidence/<timestamp>-<candidate>/`. It holds:

- the record itself (`evidence.json`): verdict, reasons, metric and its range over repeated samples, binding ratio, measurement context, evaluator id, creation time;
- the raw outputs (in the scheduling topic, per-seed simulator output per input set: per-chain percentiles, misses, utilization, decision counts);
- the log of the run.

The **run id** is the directory name. It is the citation key for the whole campaign.

## How it works
**The rule: cite or it did not happen.** A number counts only if it cites a run id. This applies to the worklog, the lessons file, the reports and every agent's final report. Agents are told the rule in their working rules.

**Diagnostics are labelled.** Agents may write their own tools: per-job queueing times, timelines, profiles. Their numbers are **diagnostics**. They are allowed, useful and labelled "diagnostic" every time. They are never speed results, because they did not pass through the frozen evaluator. In the scheduling topic, a development run (quick mode: `topic_quick_seeds` = 4 seeds, a design parameter, illustrative; visible set only) is also a diagnostic; its record is INVALID by design.

**Reports are rebuilt, not typed.** A report command walks the evidence directories and prints every record paired with its baseline. A report typed by hand drifts from the evidence; a report rebuilt from records cannot.

**The worklog.** The **worklog** is an append-only, dated file, newest entry last. Each entry has the same shape: question, what was tried (tools, candidates), numbers with run ids, reading, next. Researchers append their own section before their session ends, and re-read the file just before editing it so that parallel agents do not overwrite each other.

## How it is used in a campaign
- The planner reads records and the worklog to rewrite the lessons ([[B6-the-two-memories]]).
- The weekly report cites a run id for each headline number ([[B8-reporting]]).
- Records killed premises fast in the first campaign: three plausible beliefs about where time went were refuted within a session by a profile or an inspection of the compiled artefact, and written down as negative results ([[C4-lessons-about-the-method]], lesson 3).

## Common confusions
- **"A diagnostic number is a weaker result."** It is a different kind of thing. It can guide the next step; it cannot be reported as a gain.
- **"Keep only the accepted records."** Rejected and INVALID records are evidence too. A rejected candidate is a negative result that stops the next agent repeating it.
- **"The worklog is the record."** The worklog is a narrative that cites records. The records are the evidence.

## Why it matters
Agents write fluent reports. Fluency is not evidence. When every number points at a directory, a reader can check any claim in seconds, and an agent's mistaken belief is refuted by the next look at the record rather than copied into the next round.

## Terms introduced
- **evidence record** — the directory of record, raw outputs and log written by one official evaluation.
- **run id** — the evidence directory's name; the citation key for every number.
- **cite or it did not happen** — the rule that a number counts only if it cites a run id.
- **diagnostic** — a number from a tool outside the evaluator; labelled, never a speed result.
- **worklog** — the append-only, dated narrative of the campaign: question, tried, numbers, reading, next.
- **negative result** — a recorded finding that an idea did not work, kept so it is not repeated.
