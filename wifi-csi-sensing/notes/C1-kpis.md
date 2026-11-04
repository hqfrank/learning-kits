# C1 — KPIs: detection rate, false alarms, time to detect, per-scenario breakdown

**Source:** internal I5 (four-stage KPI ladder, six KPIs per stage), I7 (TPR at fixed FPR, false alarms per month, field shortfall, per-scenario results), generalised; Fawcett 2006 (ROC). · **Status:** concept note. Study numbers are illustrative; the false-alarm arithmetic is mine.

## In one sentence
A Wi-Fi sensing KPI must fix the false-alarm budget first, in false alarms per home per month, then report the detection rate at that budget for each scenario and each stage of difficulty, because a per-window false-positive rate that sounds small is enormous at product scale.

## What it is
A **KPI (key performance indicator)** is a metric with a target that decides whether the product ships. The KPI framework had two axes (internal I5):

- **motion versus presence** — motion detection needs the person to move; presence detection must also find a still person;
- **home level versus room level** — "someone is moving somewhere in the home" versus "in this room".

This gives four stages of increasing difficulty:

| Stage | Question | Hard part |
|---|---|---|
| 1 | Is there motion anywhere in the home? | false alarms from non-human change |
| 2 | Which room has motion? | adjacent rooms through walls |
| 3 | Is anyone in the home, moving or still? | a still person barely changes the CSI |
| 4 | Which room is a person in, moving or still? | both of the above |

Each stage has the same six KPIs, each with its own target (internal I5):

1. **true-positive ratio** — when a person moves (stage 1–2) or is present (stage 3–4), the probability of detecting it (in the right room, for stages 2 and 4);
2. **false-positive ratio** — when nobody is there (or nobody moves), the probability of a detection;
3. **true-negative ratio** — the complement of 2;
4. **false-negative ratio** — the complement of 1, including detection in the wrong room;
5. **blind-spot ratio** — the fraction of the home's area (or rooms) where false positives plus false negatives exceed a threshold;
6. **effective-coverage ratio** — the fraction of area (or rooms) where TPR and TNR both exceed a threshold.

Blind-spot and coverage ratios turn an average into a map. A system with a good average can still fail in one room every day.

## How it works
**Fix the false-alarm budget first.** A user experiences false alarms per month, not a per-window FPR. Convert:

- 30 days contain 2 592 000 s (`seconds_per_30_days`).
- With an illustrative 1 s decision window, a per-window FPR of 1% gives about 26 000 false windows per month (my arithmetic).
- A budget of an illustrative 4 false alarms per home per month (`false_alarm_budget_illustrative`) allows a per-window FPR near 1.5 × 10⁻⁶ if every false window counts (my arithmetic).

So "TPR at 1% FPR", the usual research number, is three to four orders of magnitude away from a product budget (my arithmetic). Two things close part of the gap: false windows that touch are merged into one false **event**, and a decision can require several positive windows in a row. Both trade detection latency for fewer alarms (my explanation).

**Event level versus window level.** A **window-level** metric scores every window. An **event-level** metric scores each scripted episode once: was it detected, and how long after it started? Event-level metrics match what a user sees; window-level metrics are easier to compute. State which one a number is (internal I7).

**Time to detect and time to clear.** **Time to detect** is the delay from the start of motion (or entry) to the first positive decision. **Time to clear** is the delay from the end of presence (or exit) to the decision "empty". Lights that turn on late annoy; lights that turn off while someone sits still annoy more. Report both as distributions, with a high percentile, not just a mean (my explanation; see the window trade-off in [[B3-classifiers-and-windows]]).

**Per-scenario breakdown.** Report each KPI per scenario, not only overall. The overall number depends on the scenario mix of the dataset, which is arbitrary. The scenarios of [[C2-data-collection-campaigns]] were the reporting rows: near a device, near the AP, at a door, far from devices, in a room with no device, small motion, still person, empty home.

## What the studies showed (illustrative)
- **Caution:** illustrative numbers; the direction is the lesson.
- In a small lab demonstration, accuracy looked near an illustrative 0.95. It had not yet been tested against false-positive cases (internal I6).
- The multi-home study reported TPR at 1% FPR per scenario, with a large spread between scenarios (see [[B4-multi-device-joint-detection]]).
- The later field study measured TPR at a product false-alarm budget of an illustrative 4 per month. It reached about an illustrative 0.5 against a target of 0.9 (`field_tpr_vs_target_illustrative`). The causes found were CSI outliers, CSI drift over time, and chip CSI quality (internal I7).

## Common confusions
- **"1% false positives is good."** At one decision per second, it is tens of thousands of false alarms per month.
- **"Accuracy summarises the system."** Accuracy mixes TPR and TNR in the dataset's class ratio. Report TPR at a fixed false-alarm budget.
- **"Motion detection solves presence."** Stages 3–4 need a still person to be detected. The motion detector's "no motion" is not "nobody".
- **"The overall TPR is the result."** The per-scenario table is the result. The hardest rows decide whether users trust the product.

## Why it matters
The KPI ladder lets a team ship value at stage 1 while working toward stage 4. The false-alarm conversion tells the team, before any model work, how far the research numbers are from the product requirement. It explains why lab demonstrations and field results disagreed.

## Terms introduced
- **KPI** — a metric with a target that gates a product decision.
- **TPR / FPR / TNR / FNR** — true-positive, false-positive, true-negative, false-negative ratios.
- **false-alarm budget** — the allowed false alarms per home per unit time.
- **blind-spot ratio** — the fraction of area or rooms where errors exceed a threshold.
- **effective-coverage ratio** — the fraction of area or rooms where both TPR and TNR exceed a threshold.
- **window-level / event-level metric** — scoring every window / scoring each episode once.
- **time to detect / time to clear** — the delay to the first positive decision after an event starts / to the "empty" decision after it ends.
- **per-scenario breakdown** — reporting each KPI separately for each scenario.
