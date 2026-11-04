# A1 — The order of construction

**Source:** generalised from internal methodology notes, 2026 (§2 "how it was built, in order"; §4 lesson 5). Numbers of the first campaign are illustrative (`c1_*` keys in `constants.json`). · **Status:** concept note.

## In one sentence
Build the method in five steps — reference and baseline, frozen evaluator with controls, hand-run rounds, a report, and automation last — because each step finds the faults that would make the next one automate the wrong thing.

## What it is
The **order of construction** is the sequence in which the parts of the method are built. The first campaign built them in this order:

1. **Reference and baseline.** Port the system, make it run, and benchmark it on frozen inputs on several devices. See [[B1-reference-and-baseline]].
2. **Proposal.** Write a one-page design: what is optimized, what "equivalent" means, who owns the evaluator, the roles, the memory, the metrics, the roadmap, the risks, the asks. See [[B8-reporting]].
3. **Frozen evaluator with negative controls.** Build the judge, test it against cheats that must fail and against the real baseline that must pass. See [[B2-the-frozen-evaluator]] and [[B3-negative-controls]].
4. **Research by hand.** A coordinating agent gives one bounded question to each researcher session. A human watches every round.
5. **Evaluator hardening.** Each new check answers a failure seen the day before.
6. **First report.** Built from the evidence records.
7. **Automated loop.** Planner, parallel researchers, evaluation queue, promotion policy, memory, cost meter. See [[B7-agents-and-the-loop]].

## How it works
Each step depends on the one before it.

- **The evaluator needs the reference.** A correctness gate compares a candidate's output with a trusted output. Without the reference there is nothing to compare against, and the first fast-but-wrong result is accepted.
- **The evaluator needs controls before it judges candidates.** In the first campaign the first gate wrongly rejected the real baseline. The team found that on the day the evaluator was built, because the baseline was run before any candidate.
- **Automation needs the hand-run rounds.** The hand-run rounds showed which prompts, rules and checks the agents needed. The automated harness then encoded a process that already worked.

**Caveat first: the numbers below are illustrative, not the campaign's values.** The shape of the first campaign was a large gain by hand and a small gain by automation. An illustrative version: the hand-run rounds took one policy call from about `c1_baseline_ms_illustrative` = 400 ms to about `c1_after_handrun_ms_illustrative` = 100 ms in `c1_handrun_days_illustrative` = 3 days with about `c1_handrun_sessions_illustrative` = 12 researcher sessions. The automated loop then took it to about `c1_after_auto_ms_illustrative` = 88 ms in `c1_auto_rounds_illustrative` = 5 rounds for about `c1_auto_spend_usd_illustrative` = 50 USD of model usage (all illustrative).

The big gains were found by people steering agents; the automation found the smaller, harder ones cheaply. (Interpretation, mine: this is the expected shape, because hand-run rounds pick the low-hanging fruit first.)

## How it is used in a campaign
On a new topic the same order applies (see [[C5-the-checklist]]):

| Phase | Exit criterion |
|---|---|
| Calibrate | The baseline passes every input set with margin clearly below 1; every control is rejected |
| Hand-run | The evaluator has survived several rounds of real candidates; the lessons file "writes itself" |
| Automate | Small caps, few parallel researchers, cost metered from round one |

## Common confusions
- **"Automate first, then fix the prompts."** The first campaign's lesson is the reverse: automating earlier would have automated the wrong prompts.
- **"The proposal is paperwork."** The proposal fixes what "equivalent" means before the first result exists. That definition cannot be changed after the results without suspicion.
- **"Hardening is a phase."** Hardening never ends. Every evaluator version answers a failure seen on real candidates; see [[B2-the-frozen-evaluator]].

## Why it matters
An automated loop amplifies whatever it is given. If the judge is weak, the loop finds the weakness quickly. Building the judge and the process first, and automating last, means the loop amplifies good research rather than good cheating.

## Terms introduced
- **order of construction** — the sequence reference → evaluator with controls → hand-run rounds → report → automation.
- **hand-run round** — a round where a coordinating agent, watched by a human, gives one bounded question to each researcher session.
- **coordinating agent** — the human-facing agent that assigns questions, combines results and writes the worklog and reports.
- **evaluator hardening** — adding an integrity check in answer to a failure seen on a real candidate.
