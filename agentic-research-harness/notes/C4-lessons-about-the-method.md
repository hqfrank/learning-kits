# C4 — Lessons about the method

**Source:** generalised from internal methodology notes, 2026 (§4, lessons 1–6), and the demonstration topic's worklog (harness observations). First-campaign numbers are illustrative (`c1_*` keys). Public background: Amdahl 1967 (`pub_amdahl_year`). · **Status:** concept note.

## In one sentence
Six lessons came out of running the method: gates fail in both directions, measurement artefacts mislead more often than bad ideas, premises die fast when every claim needs a record, profile before planning, automate last, and an independent audit plus controls that must fail is what makes a headline trustworthy.

## What it is
These are lessons about the **method**, not about the system optimized. Each one changed how the harness or its rules work.

## How it works

**1. Gates fail both ways.** On the first day the first campaign's gate caught a real failure: after a lowering bug the vision encoder produced noise, but the final actions still looked plausible. Only the stage-wise comparison with fixed noise exposed it. On the second day the gate wrongly rejected the real baseline, because one output (a gripper open/close decision) was ill-conditioned: legitimate noise could flip it. *Rule:* calibrate limits from legitimate runs, and from more than one legitimate implementation ([[B1-reference-and-baseline]]). The scheduling topic had the same experience in another form: its `wallclock` control was accidentally deterministic and passed the order probe until fixed ([[B3-negative-controls]]).

**2. Measurement artefacts are a recurring source of wrong conclusions.** **Caveat: the magnitudes below are illustrative.** The first campaign met four:

| Artefact | Effect | Found by |
|---|---|---|
| A sync call that returned before the device finished | Timings too short | A dedicated diagnostic tool |
| A component split shifted by one graph | Time attributed to the wrong component | A dedicated diagnostic tool |
| Stand-alone component profiles on random inputs | About `c1_standalone_slowdown_illustrative` = 2.5× slower than the same component in the model (illustrative), because random inputs changed the device's power behaviour | A dedicated diagnostic tool |
| A run's position in a batch | Medians shifted by about `c1_batch_position_shift_illustrative` = 1 % of the metric (illustrative) | Paired baselines per batch |

Each was written into the lessons file so no agent repeated it. *Rule:* a real completion barrier in the timer; real inputs, not random ones; compare only within a batch. The sibling kit catalogues the same family of traps for robot benchmarks in [[../robot-workload-benchmarking/notes/C7-how-the-bench-can-lie|how the bench can lie]].

**3. Premises die fast when every claim needs a record.** Three plausible premises in the first campaign — that one stage spilled a large amount of activations to memory, that the language model was bandwidth-bound, and that the compiler transposed one layer's weights — were each refuted within a session by a profile or an inspection of the compiled artefact. Each was recorded as a negative result. *Rule:* cite or it did not happen ([[B4-evidence-records]]).

**4. Profile before planning.** The largest single gain came from the host side: the software that launches work on the device. The proposal had listed it as "lowest effort, high value", but understated it by more than an order of magnitude: the plan assumed about `c1_launches_planned_illustrative` = 5 device-graph launches per call, and the first profile showed about `c1_launches_profiled_illustrative` = 80 (illustrative). Amdahl (`pub_amdahl_year`) gives the reason to profile first: the overall speed-up from improving a part is limited by the fraction of time that part takes, so the fraction must be measured before the work is ranked. The first profiling tool paid for the week.

**5. Automate last.** Hand-run rounds produced the large gain; the automated loop then produced a smaller further gain for a modest spend (illustrative shape in [[A1-the-order-of-construction]]). Automating earlier would have automated the wrong prompts. The scheduling topic's first automated round also found harness faults that only appear in automation: the agent tool emitted no usage events, so the credit meter read zero and the credit cap did nothing; and the agent tool rewrote the agent profiles into a newer schema on first use.

**6. Independent audit and controls that must fail.** An accepted candidate is reviewed by an agent that did not write it, and the controls are re-run on every evaluator version. These two together are what make a "several times faster" headline a claim a reader can trust without re-running it.

## How it is used in a campaign
Each lesson maps to a check in the checklist ([[C5-the-checklist]]): calibrate from two or more legitimate implementations (1); build diagnostic tools and record artefacts in the lessons (2); enforce citations (3); run the first profile before ranking tasks (4); hand-run before automating, and check the cost meter in round one (5); audit and re-run controls (6).

## Common confusions
- **"The gate rejecting the baseline means the gate is wrong."** It means one limit is wrong. Recalibrate that limit from legitimate runs, re-freeze, and record why.
- **"An artefact is a one-off bug."** Artefacts recur with every new tool and every new agent. Writing each into the lessons is what stops the recurrence.
- **"The proposal ranked the targets."** The proposal guessed. The profile ranks.

## Why it matters
The method's safeguards exist because each of these lessons was paid for once. Knowing them in advance turns a new campaign's first week from rediscovery into research.

## Terms introduced
- **measurement artefact** — a result caused by the measurement apparatus, not by the system under test. Also called: bench artefact (see [`../robot-workload-benchmarking/glossary.md`](../robot-workload-benchmarking/glossary.md)).
- **completion barrier** — a synchronization point that returns only after the device has finished the work being timed.
- **ill-conditioned output** — an output that legitimate noise can flip, such as a threshold decision near its threshold.
- **Amdahl's law** — the overall speed-up from improving one part is limited by that part's fraction of the total time (Amdahl 1967).
- **independent audit** — review of an accepted candidate by an agent that did not write it.
