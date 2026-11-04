# B2 — The frozen evaluator

**Source:** generalised from internal methodology notes, 2026 (§3.2); the harness README (evaluator plugin contract, promotion policy); the demonstration topic's README §2. Limits are design parameters (`harness_*`, `topic_*` keys). · **Status:** concept note.

## In one sentence
The evaluator is the only judge: humans own it, a hash pins it, it refuses to run if changed, it gates correctness with limits calibrated from legitimate runs on visible and held-out inputs, it reports how close a candidate came to failing, and it checks for the known ways a fast result can be fake.

## What it is
The **frozen evaluator** is the program that decides whether a candidate is correct and how fast it is. "Frozen" means three things.

1. **Human-owned.** Agents may read it and may argue it is wrong in their reports. They may never edit it.
2. **Hash-pinned.** A freeze script writes a manifest of file hashes. Before every run the harness compares the tree with the manifest and refuses to evaluate if they differ.
3. **Versioned.** Every evidence record carries the evaluator's id. A change to the evaluator is a new version: re-freeze, re-run the baseline and the controls, and mark older records superseded for comparison.

## How it works
The evaluator has four jobs.

**1. Gate correctness with calibrated limits.** A **gate** is a set of pass/fail checks. Each check compares a measured value with a **limit**. The limits come from the legitimate-noise references of [[B1-reference-and-baseline]], per input set, not from a guess. Example from the scheduling topic: hard chains have zero deadline misses, soft chains miss at most `topic_soft_miss_limit` = 5 %, and the mean scheduler decision time is below `topic_decision_time_limit_ms` = 2 ms (design parameters, illustrative).

**2. Report a margin: the binding ratio.** For every check the evaluator computes measured ÷ limit. The **binding ratio** is the largest of these ratios over all checks and all input sets. A value below 1 passes. Promotion needs more than a pass: the binding ratio must be at most a **margin cap** (`harness_margin_cap_first_campaign` = 0.85 in the first campaign, `harness_margin_cap_scheduling` = 0.9 in the scheduling topic; design parameters, illustrative). A candidate that passes with a thin margin is recorded as "accepted, low margin" and never promoted.

**3. Use held-out inputs.** **Held-out inputs** are input sets that agents never read. In the first campaign they lived only on the evaluation host, were hash-pinned, and had different shapes than the visible set. In the scheduling topic they are two other workloads: a lighter load on fewer cores, and a different robot with another chain shape. A candidate tuned to the visible set must still generalize. This is the idea behind public/private leaderboards in open data-science competitions: the public score guides work, the private score decides.

**4. Check integrity.** Each check closes one way a fast result can be fake.

| Check | What it closes |
|---|---|
| The model ran exactly once per call | Skipping or caching calls |
| The fixed noise was consumed exactly once | Re-using or skipping denoising work |
| The output came from the device | Silent fall-back to the host |
| Order probe: re-run the set in reverse order, results must be bit-identical | Carried state, nondeterminism |
| Provenance hashes of every candidate file read | Running something other than the submitted candidate |
| Candidate tree hash before and after the run | An agent editing the candidate during its evaluation |

Speed is measured against a **paired baseline**: a baseline run in the same measurement context (same host boot, same evaluator id), not against a number from yesterday. See [[B7-agents-and-the-loop]].

## How it is used in a campaign
In the reusable harness the evaluator is a plugin with four functions: `verify` (is the frozen tree intact?), `context` (the id of the measurement environment), `run` (evaluate one candidate, return the evidence record) and `summarize` (verdict, reasons, metric, its range, margin, context, evaluator id). See [[C1-instantiating-a-topic]].

The verdict has three values: **ACCEPTED**, **REJECTED** and **INVALID**. INVALID marks a run that cannot count by design, for example a quick development run on the visible set only.

## Common confusions
- **"Pass is enough."** A pass at an illustrative 0.99 of a limit means the next small change breaks it, or that the candidate exploits the edge of the limit. The margin cap keeps headroom.
- **"Calibrate the limit tight, to be safe."** A limit tighter than legitimate noise rejects correct work. The first campaign's first gate rejected the real baseline for this reason (see [[C4-lessons-about-the-method]]).
- **"Held-out means a bigger test set."** Held-out means unseen by the optimizer. A held-out set with the same shapes as the visible set tests less than one with different shapes.
- **"Freezing stops improvement."** Freezing stops silent change. The evaluator still improves, one recorded version at a time.

## Why it matters
Every other part of the method trusts the evaluator. If an agent can change it, read its held-out inputs, or pass it with a cheat, every number downstream is suspect. A frozen, versioned, calibrated evaluator is what makes a reported gain checkable.

## Terms introduced
- **frozen evaluator** — the human-owned, hash-pinned, versioned judge of correctness and speed.
- **manifest** — the list of file hashes written by the freeze script and checked before every run.
- **gate** — the set of pass/fail checks that decide correctness.
- **limit** — the value a gate check compares against, calibrated from legitimate runs.
- **binding ratio** — the largest measured ÷ limit over all checks and input sets; below 1 passes. Also called: margin.
- **margin cap** — the largest binding ratio at which a candidate can be promoted.
- **held-out inputs** — input sets the agents never read, used to test generalization.
- **visible set** — the input set agents may read and develop against.
- **integrity check** — a check that closes one known way to fake a result.
- **order probe** — re-running the inputs in reverse order and requiring identical results.
- **provenance hash** — a hash of a file the evaluation read, stored in the record.
- **verdict** — ACCEPTED, REJECTED or INVALID.
