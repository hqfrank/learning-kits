# Explorers — rung 3 (learn-explorer)

Three single-file, no-build, double-click HTML explorers for the *device-log-anomaly-detection* kit, one per
explorer planned in the kit brief. Each page inlines the parameters it uses in a
`<script type="application/json" id="params">` block. The union ships as `params.json`. Every entry is copied
verbatim from `../constants.json` with its `class` (public / illustrative) and `source`; nothing is retyped.
The pure model of each page sits between `/*MODEL-START*/` and `/*MODEL-END*/` and contains a `selfTest(P, assert)`.
The page runs it with `console.assert` and prints the count in the sources section. The same code also runs under node.

This kit carries **no measured numbers from any fleet**. Fleet sizes, shares, slopes, rates, bursts and the
count-vector data are illustrative inputs or are simulated on the page with a fixed seed. No page has a
measured overlay, because the kit has no measurements to overlay. Public constants (isolation-forest
defaults, the score transform, the ISSRE 2016 window defaults) keep their real values with citations.

Verification (2026-11-10):
- Node self-tests: 01 = 10/10, 02 = 15/15, 03 = 12/12. Every inline param deep-equals `constants.json` and `params.json`.
- Playwright sweep at 1280 px and 390 px: every slider at min and at max (all together, then one at a time
  against the others), × every select option, + every preloaded case. That is 212 states. The sweep found no
  NaN, Infinity or undefined in the text or the SVGs, no "—" placeholders in the headline metrics, no
  console errors and no horizontal overflow.
- `learning/stories/tools/shoot.py` passes on all three pages with no problems. Each page defines an empty
  `window.Story` stub so that the story-page tool can run on a page without scenes.

---

## Spec — 01-isolation-forest-on-count-vectors.html  (notes B2, B3)

```
Explorer: An odd log window is isolated after a few random splits; that short path is its anomaly score
Teaches:  An isolation forest scores a count vector by the mean number of random splits that isolate it, normalised
          by c(psi): s = 2^(-E(h)/c(psi)). E(h) = c gives s = 0.5. You choose contamination, so it is an alarm budget,
          not a property of the data. More trees shrink the forest's own randomness.
Inputs:   trees t 1..300 (default 100, public); psi = 2^k, 16..256 (default 256, public);
          contamination 0 (= 'auto', s > 0.5) .. 20 %; probe window: "connected" count 0..40, "disconnected" count 0..20.
Outputs:  probe score s, ± from tree randomness (SE of mean path mapped to s; my estimate), mean path E(h),
          threshold, training windows flagged, planted odd windows caught.
Picture:  score heat map over the integer count lattice, training windows (dot = normal, square = flagged),
          yellow flag boundary, probe crosshair; second panel: s versus E(h), with c(psi), s = 0.5, the height
          limit and the probe marked.
Data:     400 illustrative windows from a seeded generator ("connected" ~ Poisson(lambda),
          "disconnected" ~ Poisson(0.15 lambda + 0.3), lambda ~ U(4, 16)) plus 6 planted odd windows.
Preloaded cases (probe, illustrative): typical window, burst of disconnects, silent component, busy but normal.
Out of scope: extended isolation forest, feature importance (DIFFI / Shapley), more than two templates.
```

Self-tests: c(256) ≈ 10.24; 3 splits → 0.82; E(h) = c → 0.5; height limit 8; c(2) = 1 and c(1) = 0;
the auto threshold is −offset = 0.5; each planted disconnect burst scores above the 95th percentile of the
normal windows; a contamination of 5 % flags 4–7 % of the training windows; the same seed gives the same
score; 300 trees give a smaller path SE than 10 trees.

## Spec — 02-fleet-trend-wls-vs-ols.html  (notes A2, B4)

```
Explorer: Weight each day by how many devices it rests on
Teaches:  The daily share of devices has variance p(1-p)/n_t. When n_t varies, OLS gives noisy days the same say:
          its true slope SE is larger than the WLS SE, and the SE that OLS reports can be wrong. Test the slope
          against a practical threshold s, then score = -10 log10 p, capped at 100. Extra noise that the weights
          do not model inflates the score (the reduced chi-square shows it).
Inputs:   mean devices/day 20..20 000 (log); n_t pattern (constant / weekend dip / growing cohort / two outage days);
          variation v 0..0.95; share on day 0 0.5..20 %; true slope -0.3..+0.6 pp/week; threshold s 0..0.3 pp/week;
          length 14..112 days; extra-noise factor phi 1..4 (my model); "new random draw".
Outputs:  WLS and OLS slopes (pp/week), WLS p-value, WLS and OLS scores; SE bars: OLS reported/true,
          WLS reported/true.
Picture:  daily share scatter (dot size ∝ √n_t), true, OLS and WLS lines in different dash styles, n_t strip;
          SE bar chart; score ruler with the note's p → score ticks.
Preloaded cases (illustrative): small family flat (100 devices, 3 %), large family release regression
          (10 000 devices), weekend dips, growing cohort.
Out of scope: autocorrelated residuals, attribute-based and distribution-based tests, FDR control (named in the callout).
```

Self-tests: p = 0.1 / 0.01 / 1e-5 / 1e-10 → 10 / 20 / 50 / 100; the score is capped; Φ(1.96) = 0.975;
β̂ = s → p = 0.5; 3 of 100 → SE 1.7 pp and 3 % of 10 000 → 0.17 pp; constant n gives equal true SEs for WLS
and OLS; weekend dips give a smaller true SE for WLS; noise-free lines are recovered exactly; with φ = 1 the
WLS SE it reports is within 15 % of its true SE; 10 000 × 0.01 = 100; 8 weeks = 56 days.

## Spec — 03-log-windowing.html  (note B2)

```
Explorer: The window length decides which faults you can see, and how soon
Teaches:  Longer windows give denser count vectors but dilute a short burst. Shorter windows react faster but are
          mostly zeros. A smaller step gives more windows and earlier alarms, but the windows overlap, so they are
          not independent samples.
Inputs:   window W 5 min..6 h (log); step as a share of W 0.05..1 (1 = fixed); templates 5..400;
          component lines/h 10..5000 (log; default = lines per device-day × share kept ÷ 24, my arithmetic);
          normal rate of the watched template 0.1..20 /h; extra burst rate 1..200 /h; burst duration 2 min..6 h (log);
          false-alarm budget alpha 0.1..10 % per window.
Outputs:  windows per day (B2 formula), empty share of the vector (1/rank template mix, my assumption),
          threshold k* (Poisson), P(burst flagged) in the best-aligned window, mean delay (expected-count rule
          + half a step; my estimate), false alarms per day (effective alpha × windows), lines to read per window.
Picture:  sweep of W: P(flagged) and empty share (top), mean delay (bottom, log), current W marked;
          timeline of the windows around a burst at hour 12, flagged windows in red with "!".
Preloaded cases: kit example 1 h / 15 min (illustrative); fixed 1 h and sliding 6 h / 1 h (He et al. 2016
          defaults, public); slow leak with 10 min windows (illustrative).
Out of scope: session windows, sequence features, multi-template detectors, correlation between overlapping windows.
```

Self-tests: 24 h / 1 h / 15 min → 93 windows; fixed 1 h → 24; sliding 6 h / 1 h → 19; the Poisson tail matches
the closed form and the pmf sum; k* is the smallest count within the budget; one template gives an empty
share of exp(−λW); 500 000 × 1 % ÷ 24 = 208.3 lines/h; more templates give sparser vectors; a 10 min burst
is diluted in a 6 h window; a slow 6 h leak is clearer in a long window; a smaller step shortens the delay.

---

## Files

| File | Teaches | Key inputs | Sources |
|---|---|---|---|
| `01-isolation-forest-on-count-vectors.html` | short isolation path → high score; contamination is an alarm budget | trees, ψ, contamination, probe counts | notes B2/B3; Liu, Ting, Zhou 2008; scikit-learn |
| `02-fleet-trend-wls-vs-ols.html` | WLS weights days by n_t; slope test against s; p → score | devices/day, n_t pattern, share, slope, s, days, φ | notes A2/B4; NIST e-Handbook §4.1.4.3; Ewing & Green 1998 |
| `03-log-windowing.html` | window length vs sparsity vs detection delay | W, step, templates, rates, burst, α | note B2; He et al. ISSRE 2016 |
| `params.json` | the constants the pages load | — | copied from `../constants.json` |

Open with a double-click, or `open 01-isolation-forest-on-count-vectors.html`. No server, no network, no build step.
