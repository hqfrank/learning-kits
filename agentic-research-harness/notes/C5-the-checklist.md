# C5 — The ten-step checklist for a new topic

**Source:** generalised from internal methodology notes, 2026 (§5 checklist); the reusable harness README ("How to put a new research topic on it"). · **Status:** concept note.

## In one sentence
To run the method on a new question, write the proposal, build the reference, build and freeze the evaluator with its controls, write the agents' rules, reproduce and profile the baseline, run research by hand, then automate with small caps, report weekly, and treat every evaluator change as a new version.

## What it is
The **checklist** is the order of construction ([[A1-the-order-of-construction]]) as ten concrete steps. Each step names the note that explains it.

## How it works

1. **Write the one-page proposal.** What is optimized; what "equivalent" means; the two metrics; who owns the evaluator; what the agents may touch; the roadmap; the risks; the asks. ([[B8-reporting]])
2. **Make the frozen input set, the trusted reference, and at least two legitimate-noise references.** ([[B1-reference-and-baseline]])
3. **Build the evaluator.** Static checks; run; gate with calibrated per-set limits and a binding ratio; timing with a paired baseline and a real completion barrier; integrity checks; provenance hashes; an evidence schema. Freeze it with a manifest. ([[B2-the-frozen-evaluator]], [[B4-evidence-records]])
4. **Build the negative controls at the same time.** The evaluator is done when every control is rejected and the baseline is accepted on every input set, including held-out sets that never leave the evaluation host. ([[B3-negative-controls]], [[C3-calibration]])
5. **Write the agents' rules (`AGENTS.md`).** Hard rules: never edit the evaluator; never edit an existing candidate; never read held-out inputs; label diagnostics; use the device lock; reach machines only through the sanctioned script. Then the access recipe, the evaluator facts and useful facts. ([[B5-the-candidate-contract]])
6. **Reproduce the baseline through the evaluator and record it. Run the first profile; let it reorder the plan.** ([[C4-lessons-about-the-method]], lesson 4)
7. **Run research by hand.** A coordinating agent gives one bounded question per researcher session, combines the results, appends to the worklog and commits. Continue until the evaluator has survived several rounds of real candidates and the lessons file writes itself. ([[A1-the-order-of-construction]])
8. **Seed the memory from the worklog, set the promotion policy, then start the automated loop** with few parallel researchers and strict caps. Meter cost from the first round, and check that the meter reads more than zero. ([[B6-the-two-memories]], [[B7-agents-and-the-loop]], [[C1-instantiating-a-topic]])
9. **Report weekly from the records.** List the decisions the human must take; keep the asks to outside teams current, with evidence. ([[B8-reporting]])
10. **Treat every evaluator change as a new version.** Freeze, re-run the baseline and the controls, and mark older records superseded for comparison. ([[B2-the-frozen-evaluator]])

## How it is used in a campaign
The scheduling topic followed the checklist in order and recorded each step in its worklog: topic created → owner checklist (freeze, verify, evaluate baseline and controls, set seed champions) → calibration with one fixed control and a densified workload → frozen v0.1 → first automated round with `topic_researchers_parallel` = 2 researchers (illustrative). See [[C2-the-scheduling-topic]] and [[C3-calibration]].

The topic README's roadmap carries the method forward one step at a time: add one left-out effect per evaluator version (data-transfer cost, preemptive CPU, contention), re-freeze and re-run; then replace simulated execution times with traces from a real robot stack, keeping the plugin unchanged.

## Common confusions
- **"Steps 3 and 4 are sequential."** They run together. A gate built without controls is untested.
- **"Step 7 can be skipped on a small topic."** On a small topic step 7 is short, not absent. It is where the prompts, rules and checks are found.
- **"Step 10 is housekeeping."** Without it, a record from an older evaluator is compared with a newer one, and a gain or a loss can be an evaluator change.

## Why it matters
The checklist turns the method into something a competent engineer can apply to a new model, a new chip, a new simulator or a new system without re-deriving it — and without repeating the first campaign's mistakes.

## Terms introduced
- **checklist** — the ten-step order for instantiating the method on a new topic.
- **agents' rules (`AGENTS.md`)** — the hard rules, access recipe and facts that every agent reads before working.
- **superseded record** — a record from an older evaluator version, kept but not compared with newer ones.
