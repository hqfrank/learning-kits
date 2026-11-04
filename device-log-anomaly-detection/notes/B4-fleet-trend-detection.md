# B4 — Fleet trend detection: weighted least squares on a share of devices

**Source:** weighted least squares and slope tests from any regression text (e.g. NIST/SEMATECH e-Handbook of Statistical Methods, §4.1.4.3 "Weighted Least Squares Regression", https://www.itl.nist.gov/div898/handbook/pmd/section1/pmd143.htm); Phred-style score Q = −10·log₁₀ P from Ewing & Green, Genome Research 8:186–194, 1998; Benjamini & Hochberg, J. R. Stat. Soc. B 57:289–300, 1995; generalised from internal design documents of a device-health programme (see [`../SOURCES.md`](../SOURCES.md)). · **Status:** concept primer.

## In one sentence
To ask "is this metric getting worse across the fleet?", fit a straight line to the daily share of devices over several weeks, weight each day by how many devices it rests on, test whether the slope exceeds a practical threshold, and turn the p-value into a 0–100 score.

## What it is
**Fleet trend detection** looks for a sustained change in a fleet-level series, one series per device family, feature, and category. The series is the daily **share of devices** *p̂*ₜ from [[A2-fleet-metrics]]. A trend is a non-zero slope of *p̂*ₜ over time.

## How it works
**Step 1 — one series per slice.** For each (family, feature, category), build *p̂*ₜ and the active-device count *n*ₜ for each day *t* over an illustrative 8 weeks (56 daily points).

**Step 2 — why ordinary least squares is wrong here.** Ordinary least squares (OLS) assumes every point has the same error variance (**homoscedasticity**). But Var(*p̂*ₜ) = *p*(1 − *p*)/*n*ₜ, and *n*ₜ changes from day to day: weekends, outages, a new cohort of devices. The variance is not constant (**heteroscedastic**). OLS gives a noisy day as much say as a precise day, and its slope standard error is wrong.

**Step 3 — weighted least squares (WLS).** Give each day the weight

  *w*ₜ = 1 / Var(*p̂*ₜ) = *n*ₜ / ( *p̂*ₜ (1 − *p̂*ₜ) ).

Minimise Σ *w*ₜ (*p̂*ₜ − α − β*t*)². With correct weights, the WLS slope β̂ is the best linear unbiased estimator, and its standard error se(β̂) is valid (NIST e-Handbook §4.1.4.3). Caution: when *p̂*ₜ is 0 or 1 the weight is infinite. Use a pooled *p̄* across the window in the variance, or a small floor (my note; the source does not state its handling).

**Step 4 — test against a practical threshold.** A slope of exactly zero is never true for a real fleet, so test against a threshold *s* that is the smallest slope worth an engineer's time:

  H₀: β = *s*,  one-sided p-value = P(β > β̂ | *s*, se) = 1 − Φ((β̂ − *s*) / se(β̂)).

With many daily points, a normal approximation for the slope's sampling distribution is reasonable.

**Step 5 — p-value to score.** Engineers read scores more easily than p-values. A Phred-style transform, borrowed from DNA-sequencing quality scores (Ewing & Green 1998), is

  score = −10 · log₁₀(p),

capped at an illustrative 100. Then *p* = 0.1 → 10, *p* = 0.01 → 20, *p* = 10⁻⁵ → 50, *p* = 10⁻¹⁰ → 100 (my arithmetic).

**Step 6 — filter by direction.** Drop changes in the good direction: falling disconnects, rising recovery successes, falling watchdog failures. The filter is a small table of (feature, category, direction) rules.

**Variants of the same idea.** The internal design ran three models daily (generalised):

- **time-based** — has the metric changed over time for a group? (the slope test above);
- **attribute-based** — does group X (a country, router vendor, software version) differ from the rest of the family?;
- **distribution-based** — does the distribution over categories (for example, over reason codes) differ for group X? A chi-square test is the standard tool.

Each runs on the share of devices and on intensity ([[A2-fleet-metrics]]).

**Family level versus device level.**

| Level | Method | Catches | Cost |
|---|---|---|---|
| Family | WLS slope test on the share | Fleet-wide regressions, for example a release that raises disconnects | Few reports (an illustrative 1 per week); each one is high impact |
| Device | Isolation forest on device-day vectors ([[B3-anomaly-detection-on-logs]]) | One device or household behaving oddly | Many reports; each one is lower impact and often environmental |

## How it is measured or used
- **Multiple testing.** With an illustrative 10 000 series tested daily at *p* < 0.01, about 100 series per day cross the line by chance alone (my arithmetic). Control the false discovery rate across series (Benjamini & Hochberg 1995), or rank by score and review only the top of the list.
- **Autocorrelation.** Daily residuals of a fleet metric are correlated (weekly cycles, slow drifts). Correlated residuals make se(β̂) too small and p-values too optimistic (my interpretation; the source does not address it). A weekly dummy or a block bootstrap of the slope is a cheap check.
- **Missing days.** A gap in the data can look like a step change ([[C3-data-quality]]).

## Common confusions
- **"WLS changes the slope a lot."** Often it changes the slope little. It changes the standard error, and therefore the p-value, which is what the alarm uses.
- **"Test β = 0."** With enough devices every slope is significant. Testing against a practical threshold *s* asks the question engineers care about.
- **"The score is a severity."** It is a confidence that the slope exceeds *s*. Severity also depends on how many devices are affected and how bad the event is ([[B6-clustering-and-reporting]]).
- **"A significant trend is a defect."** It can be a router-firmware rollout, a holiday, or a reporting change.

## Why it matters for fleet operations
The daily share of devices is the earliest cheap signal of a regression. Weighting by sample size stops small-population days from setting off alarms. A threshold slope and a direction filter keep the report list short enough to be read.

## Terms introduced
- **fleet trend detection** — testing a fleet-level series for a sustained slope.
- **ordinary least squares (OLS)** — linear regression with equal weight on every point.
- **homoscedastic / heteroscedastic** — constant / non-constant error variance across points.
- **weighted least squares (WLS)** — linear regression that weights each point by the inverse of its variance.
- **BLUE (best linear unbiased estimator)** — the minimum-variance linear unbiased estimator; WLS with correct weights is BLUE.
- **practical threshold s** — the smallest slope worth acting on; the null hypothesis value.
- **p-value** — the probability, under the null hypothesis, of a slope at least as extreme as the one observed.
- **Phred-style score** — −10·log₁₀(p); each 10 points is a factor of 10 in p.
- **direction filter** — rules that drop changes in the good direction.
- **false discovery rate (FDR)** — the expected share of flagged series that are false alarms.
