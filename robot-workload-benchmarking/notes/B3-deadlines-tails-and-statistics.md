# B3 — Deadlines, tails, and statistics

**Source:** Garwood exact Poisson interval (Garwood 1936, Biometrika 28); moving-block bootstrap (Künsch 1989, Annals of Statistics 17); standard t-interval. · **Status:** concept primer, illustrative numbers only.

## In one sentence
Deadline metrics are counted and bounded as rare events, not averaged: you report misses per minute with an exact Poisson interval, you judge timing by the tail (p99) not the mean, and because consecutive samples from a running system are correlated you use block methods — not the naive formulas — to put an honest confidence interval on them.

## What it is
When the question is "does the control loop keep its deadline?", the statistics are different from ordinary averaging:

- **deadline misses per minute** — a rate of rare events, bounded by a **Garwood (exact Poisson) interval**.
- **tails, not means** — the p99 of the per-cycle time, because a deadline is about the worst cycle.
- **sample-count rules** — a minimum number of samples before a percentile is trustworthy.
- **the moving-block bootstrap** — a confidence interval for a statistic computed from correlated (autocorrelated) samples.
- **the t-interval across replicate blocks** — a confidence interval from a few independent repeats.
- **paired differences** — comparing two conditions by their within-pair difference, cancelling shared noise.
- **overdispersion** — variance larger than a simple model predicts, which widens the honest interval.

## How it works
**Rare events need a Poisson interval.** Deadline misses are rare and roughly independent, so their count follows a Poisson distribution. From an observed count over a known time you compute an exact (Garwood) interval on the rate. This is why window length matters: zero misses in two minutes gives a wide upper bound, while zero misses in thirty minutes gives a tight one. A short window cannot prove a low miss rate (see [[C4-windows-gates-and-validity]]).

**Tails, not means.** A deadline is crossed by the worst cycle, not the average cycle. So the metric is the p99 (or higher) of the per-cycle time, and a mean that looks healthy can hide a p99 that misses. The sibling kit shows a control loop whose p99 inflates dramatically under co-tenants while its mean barely moves ([[../jetson-orin-thor-metrics/notes/B8-cotenancy-real-shape-mix-ladder|the sibling B8 note]]).

**Sample-count rules.** A p99 needs enough samples to be stable: estimating a 99th percentile from a few hundred points is noisy. The benchmark fixes a minimum sample count, and the window length follows from the rate (an illustrative rule: run long enough to collect several thousand cycles). A window with too few samples is flagged, not trusted.

**Autocorrelation breaks the naive interval.** Consecutive cycles of a running system are correlated — a thermal drift or a scheduling hiccup spans many cycles — so the usual "divide by the square root of N" formula understates the uncertainty. The **moving-block bootstrap** resamples contiguous blocks of samples, preserving the correlation within each block, to give an honest interval. For a small number of independent repeats (replicate blocks), a **t-interval** across the block means is the right tool.

**Paired differences.** To measure the effect of one change (co-tenant on versus off), compare the two within the same block and take the difference. Shared noise — the day, the thermal state, the bring-up — cancels in the pair, so the paired difference is far more sensitive than comparing two separate averages (see [[C5-experimental-design]]).

**Overdispersion.** If the miss counts vary more between blocks than a single Poisson rate allows, the process is overdispersed (some blocks are simply worse). The honest interval must account for this, not assume one clean rate.

## How it is measured or used in a benchmark
- **Report misses per minute with a Garwood interval.** State the window length; a short window gives only a weak upper bound.
- **Report p99, not the mean, for deadline-bound work.** Pair it with a sample count.
- **Fix a sample-count rule and derive the window length.** Flag windows below it.
- **Use block methods for confidence intervals.** Moving-block bootstrap for autocorrelated series; t-interval across replicate blocks.
- **Prefer paired comparisons.** Difference the two conditions within a block to cancel shared noise.

## Common confusions
- **"Zero misses proves the loop is safe."** Zero misses in a short window gives only a wide upper bound; you need a long window for a tight one.
- **"Report the mean cycle time."** Deadlines are about the tail; report p99.
- **"Divide the standard deviation by root-N for the interval."** That assumes independence; running-system samples are correlated, so use block methods.
- **"Compare the two averages."** A paired within-block difference cancels shared noise and is far more sensitive.
- **"One Poisson rate fits all blocks."** Overdispersion means some blocks are worse; the interval must widen.

## Why it matters for robotics workloads
The control loop's deadline is the one metric where getting the statistics wrong is dangerous, because it is the metric that decides whether the robot is safe to run the workload. A naive average over a short window can declare a loop healthy that in truth misses its deadline under load. Counting misses as Poisson events, judging by the tail, and using block methods for the interval is what turns "it looked fine" into "its miss rate is below X per minute with 95% confidence."

## Terms introduced
- **deadline misses per minute** — the rate of cycles that overran their period; a rare-event rate.
- **Garwood (exact Poisson) interval** — an exact confidence interval for a Poisson rate from a count over a known time.
- **tail (p99)** — a high percentile of the per-cycle time; the metric for deadlines, versus the mean.
- **sample-count rule** — a minimum number of samples before a percentile is trusted; sets the window length.
- **autocorrelation** — correlation between consecutive samples of a running system, which breaks naive intervals.
- **moving-block bootstrap** — resampling contiguous blocks to get an honest interval for autocorrelated data.
- **t-interval across replicate blocks** — a confidence interval from a few independent repeats.
- **paired difference** — comparing two conditions by their within-pair difference, cancelling shared noise.
- **overdispersion** — variance larger than a single-rate model predicts; widens the honest interval.
