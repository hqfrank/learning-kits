# Explorers — rung 3 (learn-explorer)

Four single-file HTML explorers for *agentic-research-harness*. They need no build step and no network: open one with a double-click
(or `open 01-range-based-promotion.html`). Each page inlines its parameters in a `<script type="application/json" id="params">`
block, and the same entries are shipped as `params.json`. Entries from `../constants.json` are copied verbatim with their
`class` and `source`. A few choices belong to the pages themselves and are class `assumption`, with source "page model choice";
they are not in `constants.json`. Numbers in the page prose are filled from the params block, not typed. The pure model sits between
`/*MODEL-START*/` and `/*MODEL-END*/`. Its `selfTest` runs in the page (`console.assert`, with the result printed under the
sources table) and under node.

This kit carries no measured numbers. Values are `public` (my arithmetic on public mathematics), `illustrative` (design
parameters of the harness, the scheduling topic's configuration, output of the demonstration scheduling simulator, or round
values that keep the first campaign's shape) or `assumption`.

---

## Spec — 01-range-based-promotion.html (notes B7, C3)

```
Explorer: A median rule promotes noise half the time; the disjoint-range rule almost never, and pays in power
Teaches:  The loop promotes a candidate only if its worst sample beats the champion's best sample. Under no real change a median
          rule promotes with probability 1/2 and the disjoint-range rule with 1 / C(2n, n) (7.25e-12 at n = 20). The price is
          power: a gain smaller than the spread is not promoted, and one slow first call can block a real gain.
Inputs:   true gain (-2 … 10 % of the mean; negative = worse); spread (0.2 … 5 %); samples per side n (3 … 40, default 20
          = harness_timed_calls); one slow first call (toggle) and its extra time (0 … 30 %); redraw button.
Outputs:  P(promote) for each rule at this gain. Disjoint: exact integral of n·φ(y)(1−Φ(y))^(n−1)·Φ(y+d)^(n−1)·Φ(y+d−s) dy.
          Median: seeded Monte Carlo (4 000 pairs). False promotion for each rule at zero gain. One seeded draw with both verdicts.
Picture:  strip chart of one draw (dots, range bar, median tick); promotion probability against the true gain for both rules.
Cases:    no real change · small gain below the spread (default) · clear gain · clear gain + slow first call · n = 5.
Overlay:  the demonstration run's round-1 records (sched_baseline, sched_r1_*) as range bars against the 22.5 ms floor, and
          a table applying both rules to them.
Out of scope: paired per-seed tests, alternative rules (median + maximum), non-normal shapes for a real shift.
```

## Spec — 02-binding-ratio-and-limits.html (notes B1, B2, B3, C3, C4)

```
Explorer: A limit calibrated from one legitimate run rejects correct work half the time; the binding ratio says how close a pass came
Teaches:  Limit = multiple × the largest of K legitimate distances. Too few runs or too small a multiple rejects correct work;
          too large a multiple accepts a broken control. Binding ratio = the largest measured ÷ limit over all checks; below 1
          passes; promotion also needs it at or below the margin cap.
Inputs:   K (1 … 10); multiple (1 … 6, default 3 = harness_e2e_rmse_multiple); the control's offset (0 … 12 noise scales);
          the candidate's output distance, soft-miss % (limit 5 %), decision time (limit 2 ms); margin cap (0.5 … 1, default 0.9).
Outputs:  calibrated limit (from ten seeded half-normal legitimate draws); binding ratio and the check that binds; verdict
          (REJECTED / ACCEPTED low margin / ACCEPTED margin ok). P(new legitimate run rejected) = ∫ fmax_K(x)(1 − F(m·x)) dx,
          which is 1/(K+1) at m = 1. P(control accepted) = ∫ fmax_K(x) F(m·x − d) dx.
Picture:  legitimate draws with the limit and the candidate; a bar per check with the 1 line and the cap; both probabilities against K.
Cases:    one run, multiple 1 · three runs, 3× (default) · thin pass on decision time · same candidate at the 0.85 cap · loose limit.
Overlay:  the demonstration run's recorded binding ratios, classified live by the cap slider.
Out of scope: per-dimension limits, distances that are not half-normal, re-freezing and versioning.
```

## Spec — 03-placement-under-contention.html (notes C2, C3)

```
Explorer: The fastest unit is the wrong choice when it is busy — load-aware placement beats GPU-greedy as other chains load the GPU
Teaches:  On non-preemptive units, shortest-execution placement queues the chain behind other GPU work (and behind itself).
          Earliest-finish placement uses the DLA and the CPU and reaches the work floor. A long GPU job makes the gap large.
          Without a DLA there is little to move to.
Inputs:   other chains' GPU load (0 … 70 %, default 29.5 % derived = 91 % baseline GPU − this chain's 61.5 % greedy share);
          length of one other-chain GPU job (1 … 250 ms, log); perception rate (10 … 45 Hz); CPU cores (1 … 6); jitter
          (0 … 20 %); DLA present; timeline policy.
Outputs:  per-seed nearest-rank p95 of end-to-end latency from a discrete-event simulation (5 s horizon, 20 seeds, common random
          numbers), as median and range for both policies; GPU and DLA busy shares; whether the disjoint-range rule promotes
          balanced over greedy.
Picture:  median p95 with range bands against GPU load, for both policies; a Gantt chart of the first 110 ms of seed 1.
Cases:    no other load · others fill the GPU to about 91 % (default) · a 200 ms job blocks the GPU (greedy and balanced
          timelines) · long job with no DLA · heavy short-job load.
Overlay:  none on the chart, because the page model differs from the demonstration simulator. A table gives the simulator's own
          records: p95 34.7 → 27.8 ms, GPU 91 → 65 %, DLA 0 → 42 %, the held-out b probe 37 vs 29 ms.
Out of scope: other chains' deadlines (no gate), preemption, data-transfer cost, memory contention, dispatch policies other than FIFO.
```

## Spec — 04-cost-of-a-campaign.html (notes A1, B7, B8, C1, C4)

```
Explorer: Cost grows linearly with researchers and rounds, the gain does not; a broken meter hides the bill
Teaches:  Round cost = (planner + N × researcher credits) × USD/credit × share spent. An illustrative gain curve closes a share
          1 − (1 − h1)^N of the gap to an assumed floor each round, so dollars per ms rise every round. Once a round's gain is
          below the 1 % minimum win it promotes nothing. An unmetered campaign never trips its budget.
Inputs:   rounds (1 … 20); researchers N (1 … 8); researcher and planner credit caps; share of the caps spent (default derived
          so 5 rounds cost the illustrative 50 USD); budget (0 … 500 USD); metered (toggle); assumed floor (50 … 86 ms).
Outputs:  champion after the campaign, gain %, real and metered spend, promotions / rounds, cost per accepted improvement, USD
          per ms for each round. h1 is re-anchored from 100 → 88 ms in 5 rounds with 2 researchers (c1_* shape).
Picture:  champion latency against round (promoted rounds filled, others hollow, floor, anchor, budget pause); USD-per-ms bars.
Cases:    first-campaign shape (default) · 15 rounds · six researchers · full caps for 15 rounds · meter reads zero.
Overlay:  the c1_* anchor point only (an illustrative shape, not a measurement).
Out of scope: variance between rounds, tool and machine cost, changing direction after a stall.
```

---

## Files

| File | Teaches | Key inputs | Sources |
|---|---|---|---|
| `01-range-based-promotion.html` | disjoint ranges vs medians: false promotion against power | gain, spread, n, slow first call | notes B7, C3; `pub_*_null_probability*`, `sched_r1_*` |
| `02-binding-ratio-and-limits.html` | calibrated limits fail both ways; binding ratio and margin cap | K, multiple, control offset, candidate checks, cap | notes B1–B3, C3, C4; `harness_*`, `topic_*` limits |
| `03-placement-under-contention.html` | GPU-greedy vs earliest-finish placement on non-preemptive units | GPU load, job length, rate, cores, DLA | notes C2, C3; `sched_node_ms`, `sched_work_floor_ms` |
| `04-cost-of-a-campaign.html` | linear cost, diminishing gain, minimum win, metering | rounds, N, caps, spend share, budget, meter | notes A1, B7, B8, C1, C4; `topic_*` caps, `c1_*` shape |
| `params.json` | union of the four pages' params blocks | — | `../constants.json` + labelled page assumptions |

## Verification

- Self-tests: 13 / 17 / 11 / 10 asserts pass, both in the page and under node. Anchors reproduced: 1 / C(40, 20) = 7.25 × 10⁻¹²
  by the integral; 1/(K+1) false rejection at multiple 1; the round-1 records' promote / overlap / not-promotable outcomes;
  bindings 0.49 and 0.6; the 22.5 ms floor (balanced, no load) and 26.5 ms (greedy, no load); 140 USD at the caps; 88 ms after
  5 anchored rounds; a pause after 7 rounds at a 200 USD budget; an unmetered 420 USD that records 0.
- Inline params blocks are identical to `params.json`, and every copied entry is identical to `constants.json`.
- `shoot.py` (desk and phone, every preloaded case): no console errors, no failed asserts, no overflow, on all four pages.
- Browser sweep of every slider at its minimum and maximum, singly, all-min and all-max, × every select option × every checkbox
  state: 125 states, no NaN / Infinity / undefined in the rendered text.
- `learning/tools/public-scan.sh learning/agentic-research-harness`: clean.
