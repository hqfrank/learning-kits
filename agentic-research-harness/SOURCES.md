# Sources — Running optimization research with AI agents

This kit teaches a general method. It carries no measured result from any specific company, product, team or platform.

## What this kit is

Study notes (rung 1 of a four-rung learning kit: notes → diagram → explorer → video) for one question: **how do you run optimization research with AI agents so that a reported gain is real?** Part A describes the problem and the order in which the method is built, Part B the eight building blocks (reference and baseline, frozen evaluator, negative controls, evidence records, candidate contract, two memories, agents and the loop, reporting), and Part C a worked example and the lessons.

## Provenance of the method

The method, its building blocks, the design trade-offs and the lessons are abstracted from **internal methodology notes and a reusable harness from an agentic optimization campaign, 2026**. That material comprised a methodology write-up, a one-page proposal, one weekly report (used for its section structure only), the reusable harness's README and three of its modules (evaluation queue and promotion policy, round loop, memory), and a worked-example topic (README, configuration, agent rules, seed lessons, worklog, planner and researcher prompts).

**No internal material is reproduced:** no name of a company, team, person, host, account, key or internal package; no result of the first campaign; no figure. The first campaign appears only as "a robot foundation model ported to a cloud inference accelerator", with "the accelerator", "the vendor SDK" and "the vendor's kernel language" standing for the specific hardware and software. GR00T (a public NVIDIA model) and the comparison hardware (L40S, A10G, CPU) are named because they are public and carry no result here. The generic file and function names of the harness (`topic.json`, `evaluator.py`, `verify` / `context` / `run` / `summarize`, `attempts.jsonl`, `lessons.md`, `champion.json`, `AGENTS.md`) are kept as the illustrative implementation. Notes that draw on this material say "generalised from internal methodology notes" and state only the generic idea.

## Number classes

Every number is one of two classes, recorded per entry in [`constants.json`](constants.json):

1. **public** — a real value from a cited public source (a year of publication, a theorem's bound), or my arithmetic on public mathematics (the probability that 20 samples all beat 20 samples by chance).
2. **illustrative** — never a measurement of a real platform. Three kinds, each named in its `source` field:
   - **"illustrative; keeps the shape of the first campaign"** (`c1_*` keys): round values invented to keep the story's shape (a large gain by hand, a smaller further gain by automation for a modest spend). They are not the campaign's values.
   - **"design parameter of the harness"** (`harness_*`, most `topic_*` keys): thresholds and limits of the method (margin caps 0.85 / 0.9, 20 timed calls, about 70 lessons lines, 5 % soft-miss limit, 2 ms decision time, 3× rerun spread, 1 % minimum win). They are choices, not results.
   - **"demonstration run of the local scheduling simulator"** (`sched_*` keys): output of a deliberately simple simulator built for a demonstration. They show the method at work; they say nothing about any real robot computer.

Values derived from illustrative inputs are also illustrative and say "my arithmetic".

## Public sources

| Topic | Source | Used in |
|---|---|---|
| Goodhart's law | Goodhart, "Problems of monetary management: the U.K. experience", Papers in Monetary Economics, Reserve Bank of Australia, 1975 | A0 |
| "When a measure becomes a target…" | Strathern, "Improving ratings: audit in the British University system", European Review 5(3):305–321, 1997 | A0 |
| ReAct: reason–act–observe agents | Yao et al., arXiv:2210.03629, 2022 (ICLR 2023) | A0 |
| Falsifiability | Popper, *The Logic of Scientific Discovery*, 1959 | B3 |
| Held-out evaluation; public vs private leaderboards | any machine-learning methods text; the public/private leaderboard split used by open data-science competitions | B2 |
| Paired comparison and blocking | any experimental-design text, e.g. Box, Hunter & Hunter, *Statistics for Experimenters* | B7 |
| Disjoint-range null probability 1 / C(40, 20) | my arithmetic (exchangeability of i.i.d. samples) | B7 |
| EDF, rate-monotonic bound | Liu & Layland, JACM 20(1):46–61, 1973 | C2 |
| Least-laxity-first | Mok, *Fundamental design problems of distributed systems for the hard-real-time environment*, PhD thesis, MIT, 1983 | C2 |
| Non-preemptive scheduling is NP-hard in the strong sense | Jeffay, Stanat & Martel, "On non-preemptive scheduling of periodic and sporadic tasks", IEEE RTSS 1991 | C2 |
| Earliest-finish-time placement on heterogeneous resources (HEFT) | Topcuoglu, Hariri & Wu, IEEE TPDS 13(3):260–274, 2002 | C2 |
| Discrete-event simulation | Banks, Carson, Nelson & Nicol, *Discrete-Event System Simulation*, Pearson | C2 |
| Amdahl's law | Amdahl, AFIPS Spring Joint Computer Conference, 1967 | C4 |

Sibling kits linked rather than re-taught: [`../agentic-device-control/`](../agentic-device-control/README.md) (the ReAct loop), [`../robot-workload-benchmarking/`](../robot-workload-benchmarking/README.md) (pre-registration, bench artefacts, the robot stack), [`../jetson-orin-thor-metrics/`](../jetson-orin-thor-metrics/README.md) (measured GPU-sharing effects).

## How the sources were read

- Internal material: read in full as text, for mechanisms, rules and trade-offs. Every first-campaign number was replaced by an illustrative value that keeps the relation it teaches. The weekly report was read for its section headings only. Numbers from the scheduling simulator's demonstration run were copied from its worklog and seed lessons and classed illustrative.
- One inconsistency in the demonstration topic's material is not resolved here: the seed lessons give an "everything on the GPU" floor that does not equal the sum of the listed job times; this kit uses only the worklog's floor (`sched_work_floor_ms`), which does (my arithmetic: 2 + 2.5 + 14 + 4 ms).
- Public sources were cited from their standard bibliographic records; no number other than the EDF bound and the rate-monotonic limit is taken from them.

## Conventions

- "my arithmetic" marks a value computed from cited or illustrative inputs.
- "my reading" or "interpretation, mine" marks a claim the sources do not make.
- "generalised" marks an idea taken from the internal material and restated generically.
- "diagnostic" marks a number that did not pass through the frozen evaluator.

## Rung 2 — diagrams

[`diagrams/`](diagrams/INDEX.md): six diagrams drawn fresh from notes A1, B1–B4, B6–B8, C2, C3, C4 and C5. Every number is loaded from `constants.json` by key and tagged on the canvas; no other source was used.

## Rung 3 — explorers

[`explorers/`](explorers/INDEX.md): four single-file HTML explorers. They cover range-based promotion (B7, C3), binding ratio and
calibrated limits (B1–B3, C3, C4), placement under contention as a tiny in-browser discrete-event simulator (C2, C3), and the cost
of a campaign (A1, B7, B8, C1, C4). Each page copies its constants verbatim from `constants.json` into an inline params block
(the union is in `explorers/params.json`). Page-only modelling choices (distribution shapes, default slider values, the assumed
floor of the gain curve, simulator jitter and background-job shapes) are class `assumption` with source "page model choice"; they
are not added to `constants.json`. No other source was used.
