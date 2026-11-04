# B8 — Reporting

**Source:** generalised from internal methodology notes, 2026 (§3.7, checklist steps 1 and 9); the structure (section headings only) of an internal weekly report and of an internal one-page proposal. No content of either is reproduced. · **Status:** concept note.

## In one sentence
A campaign reports in two documents built from the evidence records — a one-page proposal before the work and a weekly report during it — and each lists the decisions only a human can take and the asks to outside teams, with evidence.

## What it is
**The one-page proposal** is written before the evaluator exists. It fixes the terms of the research so they cannot move after the results. Its sections:

1. Summary — what is optimized and how the harness decides.
2. Starting point — the baseline on the frozen protocol, with cross-device context.
3. What can be optimized — levels (program, kernel, layout, parallelism, numerics), each with its evidence and expected value.
4. What is open — which components the agents may change and which are closed environment.
5. System design — evaluator, agent roles, memory, infrastructure.
6. Metrics — usually two (for example latency, and throughput per dollar), with exact definitions.
7. Weekly report — what it will contain.
8. Roadmap — phases with deliverables and exit criteria.
9. Risks — each with a mitigation.
10. Asks — what outside teams (here: the accelerator vendor) can do, and what the campaign gives in return.

The proposal also fixes the acceptance thresholds. The first campaign's proposal required a timing win to exceed `harness_win_spread_multiple` = 3 times the rerun spread and to be at least `harness_win_min_rel` = 1 % (design parameters, illustrative).

**The weekly report** is generated from the run records. Its sections:

| Section | What it contains |
|---|---|
| Headline | The main paired comparison, with run ids |
| What changed | Accepted steps in order, each with its run id and gate result |
| Evaluator integrity | Controls and their verdicts; each hardening step and the failure it answers |
| What did not work, and why | Negative results with run ids |
| Where the time goes now | The current profile: what to attack next |
| Spend | Model usage and compute, and cost per accepted improvement |
| Roadmap status | Each proposal phase: done, in progress, changed |
| Asks | Updated asks to outside teams, each with its evidence |
| Next week | The plan |
| Decisions needed | Questions only the human owner can answer |

## How it works
**Built from records, not memory.** The headline and every table come from the evidence records (see [[B4-evidence-records]]). A number without a run id does not enter the report.

**Decisions only a human can take.** The promotion policy settles most questions mechanically. Some it cannot settle, because they change what counts:

- Do reduced-precision results count as a headline? (A track question, see [[B5-the-candidate-contract]].)
- The disjoint-range rule cannot fire near the work floor; should it change? (See [[C3-calibration]].)
- Should a gate limit change after a legitimate implementation fails it? (A calibration question, see [[B2-the-frozen-evaluator]].)

The coordinator collects these and puts them under "Decisions needed". It does not answer them.

**Asks with evidence.** An ask to an outside team (a vendor, an upstream project) is stronger with a minimal reproduction attached. The first campaign's asks for the accelerator vendor covered a recommended compilation path, machine-readable profiler counters, kernel guidance for its shapes, multi-core execution, correctness findings with reproductions, and a contribution path. Each was updated weekly with the evidence gathered since.

**Where the time goes.** This section is a profile, not a plan. It is what keeps the next week's tasks pointed at the largest remaining cost (see Amdahl's law in [[C4-lessons-about-the-method]]).

## How it is used in a campaign
The roadmap in the proposal becomes the "Roadmap status" table of each weekly report. A phase that changed says why. The scheduling topic's README has the same roadmap form: calibrate → campaign → harder model → real platform, each with an exit criterion ([[C2-the-scheduling-topic]]).

## Common confusions
- **"The weekly report is a status update."** It is an evidence document. Its integrity and negatives sections are as important as its headline.
- **"Spend is a finance detail."** Cost per accepted improvement tells the owner whether to continue, change caps, or stop.
- **"The coordinator can decide small things."** Small decisions that change what counts (a limit, a track rule) are not small. They go to the human.

## Why it matters
A reader who did not run the campaign must be able to trust its headline. A report built from records, with integrity checks, negatives, spend and open decisions next to the headline, lets that reader trust it without re-running anything.

## Terms introduced
- **one-page proposal** — the pre-registration of a campaign: target, equivalence, metrics, roles, roadmap, risks, asks.
- **weekly report** — the evidence document generated from the records each week.
- **decisions needed** — questions that change what counts, left to the human owner.
- **ask** — a request to an outside team, with evidence and a reproduction.
- **pre-registration** — freezing hypotheses, thresholds, and run order before any data; here the proposal plays this role. Reused from [`../robot-workload-benchmarking/glossary.md`](../robot-workload-benchmarking/glossary.md).
