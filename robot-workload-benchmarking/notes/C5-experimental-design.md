# C5 — Experimental design

**Source:** general experimental-design method, abstracted; paired/block statistics in [[B3-deadlines-tails-and-statistics]]. · **Status:** concept primer, no measured numbers.

## In one sentence
The design decisions that make a benchmark a real experiment rather than a demo are pre-registration (hypotheses, thresholds, and run order frozen before any data), no tuning after data, interleaved and mirrored A/B order, seeded randomised ordering, replicate blocks, paired comparisons, named confounds, and a disciplined way to record fixes (addenda) and re-runs (supersedes) with independent review.

## What it is
This note collects the experimental-design rules:

- **pre-registration** — writing down the hypotheses, the PASS/FAIL thresholds, and the exact run order *before* collecting data, and freezing them.
- **no tuning after data** — never changing a service's configuration to make a result pass.
- **interleaved A/B order** — alternating two conditions in a balanced sequence (ABBA, or mirror order) so slow drift cancels.
- **seeded randomised order** — generating the run order from a fixed random seed, so it is both unbiased and reproducible.
- **replicate blocks** — repeating each cell several times to get block-to-block variability.
- **paired comparisons** — comparing two conditions within the same block.
- **confounds** — variables that move with the thing under test (session, day, thermal state) and must be named.
- **addenda and supersedes** — the disciplined record of a bench fix and a re-run.
- **independent review** — a second person checking the analysis.

## How it works
**Pre-registration freezes the rules before the data.** The benchmark commits, at a named point before any measurement, to its hypotheses, its thresholds, and its full run order. After that commit, nothing frozen changes. This prevents the most common self-deception: adjusting a threshold or dropping a window once you have seen the result. If data must be seen before registration (early solo runs), it is disclosed, and which predictions it touches is stated.

**No tuning after data.** A service's configuration is frozen at registration. When a result surprises, the surprise is *explained*, not tuned away. A configuration change to make a window pass invalidates the experiment.

**Interleaved A/B and mirror order.** To compare two conditions (co-tenant on versus off), the benchmark does not run all the "on" windows then all the "off" windows — a slow drift (warming board, lengthening map) would then look like an effect. Instead it interleaves them in a balanced sequence (ABBA) or runs the second repeat in mirror order, so any monotonic drift cancels out of the comparison.

**Seeded randomised order.** The order of cells is generated from a fixed random seed. Randomising removes order bias; seeding makes the order reproducible and auditable. The order is part of the pre-registration, and it does not change because of a result.

**Replicate blocks and paired comparisons.** Each cell runs several times (replicate blocks) so the benchmark sees block-to-block variability, not one lucky window. Comparisons between conditions are made *within* a block (paired), so shared noise — the day, the thermal state, the bring-up — cancels, which is far more sensitive than comparing separate averages (see [[B3-deadlines-tails-and-statistics]]).

**Confounds are named, not hidden.** When the design cannot separate two variables — for example, if each session runs on a different day, then session and day are confounded — the confound is named and carried by every statement, and only variables independent of it are compared across sessions.

**Addenda and supersedes.** When a bench or instrument bug is found mid-campaign, it is recorded as a numbered **addendum**: the defect, the evidence, the fix, and its impact on windows already run. If the bug affected what was recorded, the affected run is **superseded** — re-run whole under the same seeds, with the old run kept and logged, never silently replaced. A *finding* about the stack's behaviour, by contrast, is never fixed or superseded; it is the result.

**Independent review.** A second person reviews the analysis — the gate logic, the statistics, the attribution — so that the result does not rest on one person's reading.

## How it is measured or used in a benchmark
- **Register hypotheses, thresholds, and order before data; freeze them.** Disclose any data seen earlier.
- **Never tune a service to pass; explain surprises instead.**
- **Interleave A/B in balanced or mirror order.** Do not block all of one condition then the other.
- **Generate the order from a fixed seed; make it part of the registration.**
- **Run replicate blocks; compare conditions paired within a block.**
- **Name every confound and carry it with every statement.**
- **Record bench fixes as addenda; re-run affected windows as named supersedes; keep the originals.**
- **Have the analysis independently reviewed.**

## Common confusions
- **"Adjust the threshold once you see the data."** That is the error pre-registration exists to prevent; the threshold is frozen before data.
- **"Run all the A windows, then all the B windows."** Drift then masquerades as an effect; interleave in balanced order.
- **"A surprising result means the config was wrong, so fix it."** A surprise about the stack is a finding, not a bug to tune away; only bench/instrument defects are fixed, and then via a logged supersede.
- **"Random order is enough."** Random *and* seeded: reproducible and auditable, and fixed at registration.
- **"One window per cell is fine."** Without replicate blocks you cannot see variability or make a paired comparison.

## Why it matters for robotics workloads
A robot benchmark runs for hours, on one shared machine, often across days, with a complex apparatus — exactly the conditions under which drift, selection, and after-the-fact tuning quietly manufacture results. Pre-registration, interleaving, seeded order, replicate blocks, paired comparisons, named confounds, and a logged fix/supersede discipline are what make the final "it carries" or "it does not" a claim you can defend, not a demo that happened to look good.

## Terms introduced
- **pre-registration** — freezing hypotheses, thresholds, and run order before any data.
- **no tuning after data** — never changing a service's configuration to make a result pass.
- **interleaved A/B order (ABBA, mirror order)** — alternating two conditions in a balanced sequence so drift cancels.
- **seeded randomised order** — a reproducible unbiased run order generated from a fixed seed.
- **replicate block** — a repeat of a cell, giving block-to-block variability.
- **paired comparison** — comparing two conditions within one block, cancelling shared noise.
- **confound** — a variable that moves with the thing under test (session, day, thermal) and must be named.
- **addendum** — the logged record of a bench/instrument fix mid-campaign.
- **supersede** — re-running an affected run whole under the same seeds, keeping the original.
- **independent review** — a second person checking the analysis.
