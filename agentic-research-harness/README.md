# Running optimization research with AI agents: a frozen evaluator, evidence records, and the research loop — study notes

**Start here: the story →** [The time trial](stories/01-the-time-trial.html) — a picture-first, interactive tour of the method in ten minutes ([all stories](stories/INDEX.md)).

## In one paragraph

An AI agent that writes code has a test suite to tell it when it is wrong; an agent that does optimization
research does not, and the fastest way to a better number is usually to do less work. This kit teaches a
method that makes agent-driven optimization research trustworthy. **Part A** states the problem — claims drift,
fast-but-wrong results, Goodhart's law — and the order in which the method is built: reference and baseline,
then a frozen evaluator with negative controls, then hand-run rounds, then a report, and automation last.
**Part B** describes the eight building blocks: a trusted reference and legitimate-noise references that define
"equivalent"; a human-owned, hash-pinned evaluator with calibrated gates, a binding ratio, held-out inputs and
integrity checks; negative controls that must fail; evidence records and the rule "cite or it did not happen";
small, parent-linked, immutable candidates; a fast attempts log and a slow curated lessons file; a planner,
parallel researchers and an evaluation worker that promotes by disjoint ranges, not medians; and reporting
that leaves the right decisions to a human. **Part C** instantiates the method on a worked example — scheduling
periodic chains on a simulated CPU + GPU + DLA robot computer — walks through its calibration and first round,
and ends with the lessons and a ten-step checklist. The kit carries no measured result from any real platform;
every number is public, a design parameter, a demonstration-simulator output, or a labelled illustrative
value (see [`SOURCES.md`](SOURCES.md)).

This is rung 1 of a four-rung learning kit (notes → diagram → explorer → video). It links to the sibling kits
[`../agentic-device-control/`](../agentic-device-control/README.md) for the ReAct agent loop and
[`../robot-workload-benchmarking/`](../robot-workload-benchmarking/README.md) for pre-registration, bench
artefacts and the real robot stack, rather than re-explaining them.

## How to read these notes

Read Part A → Part B → Part C. Part A gives the problem and the order; Part B gives the parts; Part C shows
the parts working together on one topic and what running them taught.

### Start here
- [`SOURCES.md`](SOURCES.md) — what this kit is, where the method comes from, the number classes, and the public sources.

### Part A — the problem
- [`notes/A0-why-research-needs-a-different-setup.md`](notes/A0-why-research-needs-a-different-setup.md) — coding vs research with agents; claims drift, fast-but-wrong, Goodhart; the method in one paragraph.
- [`notes/A1-the-order-of-construction.md`](notes/A1-the-order-of-construction.md) — reference → evaluator with controls → hand-run rounds → report → automation; why the order matters.

### Part B — the building blocks
- [`notes/B1-reference-and-baseline.md`](notes/B1-reference-and-baseline.md) — frozen inputs and randomness, a trusted reference on another stack, legitimate-noise references, cross-device context.
- [`notes/B2-the-frozen-evaluator.md`](notes/B2-the-frozen-evaluator.md) — human-owned and hash-pinned; calibrated gates; binding ratio and margin cap; held-out inputs; integrity checks.
- [`notes/B3-negative-controls.md`](notes/B3-negative-controls.md) — cheats that must fail; "a gate that never rejected a plausible cheat is untested"; development vs evaluation host; device lock.
- [`notes/B4-evidence-records.md`](notes/B4-evidence-records.md) — one directory per run; diagnostics labelled; reports rebuilt from records; the worklog.
- [`notes/B5-the-candidate-contract.md`](notes/B5-the-candidate-contract.md) — small, parent-linked, runtime-patching, immutable candidates; numerics tags and champion tracks.
- [`notes/B6-the-two-memories.md`](notes/B6-the-two-memories.md) — the fast attempts log, the slow curated lessons file with negatives kept, champions per track.
- [`notes/B7-agents-and-the-loop.md`](notes/B7-agents-and-the-loop.md) — planner, parallel researchers, evaluation worker, coordinator; paired baselines; disjoint-range promotion; caps and cost.
- [`notes/B8-reporting.md`](notes/B8-reporting.md) — the one-page proposal and the weekly report; decisions only a human can take; asks with evidence.

### Part C — the worked example and the lessons
- [`notes/C1-instantiating-a-topic.md`](notes/C1-instantiating-a-topic.md) — the topic directory, `topic.json`, and the four plugin functions.
- [`notes/C2-the-scheduling-topic.md`](notes/C2-the-scheduling-topic.md) — question, simulated CPU/GPU/DLA platform, metric and gate, held-out workloads, controls, candidate API, what the model leaves out.
- [`notes/C3-calibration.md`](notes/C3-calibration.md) — the work floor, densifying the workload, the baseline choice, "GPU-greedy loses when a long job blocks the GPU", the first round, the rule at the floor.
- [`notes/C4-lessons-about-the-method.md`](notes/C4-lessons-about-the-method.md) — gates fail both ways, measurement artefacts, premises die fast, profile before planning, automate last, independent audit.
- [`notes/C5-the-checklist.md`](notes/C5-the-checklist.md) — the ten steps for a new topic.

### Reference files
- [`glossary.md`](glossary.md) — one definition per term, alphabetical; terms shared with a sibling kit say so.
- [`constants.json`](constants.json) — every number this kit cites, each labelled public or illustrative, with its source.

## Question a reader asks → note that answers it

| Question | Note |
|---|---|
| Why can't I just let agents optimize against a benchmark? | [[notes/A0-why-research-needs-a-different-setup]] |
| What do I build first, and when do I automate? | [[notes/A1-the-order-of-construction]] |
| How do I define "still correct" before optimizing? | [[notes/B1-reference-and-baseline]] |
| What makes an evaluator trustworthy, and what is a binding ratio? | [[notes/B2-the-frozen-evaluator]] |
| How do I know my gate would catch a cheat? | [[notes/B3-negative-controls]] |
| How do I stop claims drifting away from the measurements? | [[notes/B4-evidence-records]] |
| How should agents package their changes? | [[notes/B5-the-candidate-contract]] |
| How do agents remember across sessions without repeating failures? | [[notes/B6-the-two-memories]] |
| Who does what in the loop, and why promote by ranges, not medians? | [[notes/B7-agents-and-the-loop]] |
| What goes in the proposal and the weekly report? | [[notes/B8-reporting]] |
| What does a new topic have to provide? | [[notes/C1-instantiating-a-topic]] |
| What does a complete worked example look like? | [[notes/C2-the-scheduling-topic]] |
| How do I make sure the problem has something to find? | [[notes/C3-calibration]] |
| What went wrong when the method was run, and what changed? | [[notes/C4-lessons-about-the-method]] |
| What are the steps, in order, for my own topic? | [[notes/C5-the-checklist]] |

## Conventions

- Notes use the ASD-STE100-at-80% style: one fact per sentence, active voice, one term per concept, caveats before results, numbers with units.
- The subject is generic: "the first campaign", "the accelerator", "the vendor SDK", "the scheduling topic".
- Every number is public or labelled illustrative (design parameter, demonstration-simulator output, or an invented value that keeps the first campaign's shape); see [`SOURCES.md`](SOURCES.md) and [`constants.json`](constants.json).
- `[[wikilinks]]` connect notes inside this kit; relative Markdown links reach the sibling kits.
