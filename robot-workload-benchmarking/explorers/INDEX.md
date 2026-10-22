# Explorers — rung 3 (learn-explorer)

Three single-file, no-build, double-click HTML explorers for the *robot-workload-benchmarking*
concept primer. Each inlines its parameters in a `<script type="application/json">` block (also
shipped as `params.json`), every parameter copied from `../constants.json` with its `class` and
`source` — nothing retyped. Prediction functions are factored into a pure IIFE that also runs under
node (used for the `console.assert` self-tests and the NaN slider-extreme sweep). All three pass
their self-tests and a NaN sweep over every slider/selector extreme (964 outputs checked across the
three pages; 0 non-finite). Open with a double-click, or `open 01-cpu-quota-and-throttling.html`.
No server, no network, no build step.

This kit carries **no measured numbers from any specific robot or campaign**. Every number is
`public` (a cited source), `sibling` (a value already in a sibling kit), or `illustrative` (a round
teaching number). The per-frame / per-person *times* in explorer 03 are slider inputs and are all
labelled illustrative on the page.

---

## Spec — 01-cpu-quota-and-throttling.html  (notes A7, B0)

```
Explorer: A CPU quota caps delivered cores against demand — and throttled_usec is not that demand
Teaches:  A container with a CFS bandwidth quota (cpu.max = quota/period) is parked once it spends
          its quota each accounting period. The honest reading of throttling is the FRACTION OF
          PERIODS EXHAUSTED, not throttled_usec, which is summed over per-core run-queues and so
          scales with the number of runnable threads. The deployed quota is the baseline; an
          uncapped run is a separate call-out (notes B0, A7; CFS bandwidth control docs).
Inputs:
  - demand (slider): 0.1 … 6 cores. Why: an under-quota service to a 6-core hog, to cross the quota.
  - quota cpu.max (slider): 0.5 … 4 cores. Why: the task's requested quota range; the deployed cap.
  - CFS period (slider): 10 … 200 ms. Why: around the Linux default of 100 ms (illustrative).
  - runnable threads (slider): 1 … 8. Why: 1 thread to a fan-out; sets how fast the quota burns and
      how wide throttled_usec sums over run-queues.
Outputs (all derived):
  - delivered cores = min(demand, quota).
  - fraction of periods throttled = 1 if demand>quota else 0 (nr_throttled / periods reading, B0).
  - thread wait per period (ms) = throttled fraction × period.
  - extra latency a mid-period request sees (ms) = the throttled stretch it must wait out.
  - throttled_usec per period = throttled wall time × concurrent threads (the summed-over-run-queues
      counter, B0) — shown to contrast with wall-clock park.
Picture: SVG timeline of three accounting periods, each split green (running, quota not yet spent)
         then red (throttled, parked to the next period); a dashed "request arrives here" marker.
Preloaded cases: none (the three defaults already show under-quota vs over-quota via the sliders).
Measured overlays: none — this is a CFS behaviour model, not a measurement page.
Out of scope: burst (CFS cpu.max burst), per-thread accounting detail, cgroup v1, real scheduler
         latency distributions, memory throttling.
```

Self-tests (reproduce the model's own identities):
1. demand ≤ quota → never throttled, delivers full demand.
2. demand 2, quota 1, period 100 ms, 2 threads → runs 50% of the period, throttled 50%, delivers 1 core.
3. `throttled_usec` with 2 threads = 50 ms × 2 = 100,000 µs — summed over run-queues.
4. 4 threads inflate `throttled_usec` further but **not** the delivered cores.
5. thread wait per period = throttled fraction × period.

---

## Spec — 02-deadline-misses-and-sample-size.html  (notes B3, C4, C6)

```
Explorer: A short window cannot prove a low miss rate — exact Poisson interval & sample size
Teaches:  Deadline misses are rare Poisson events. From a count over a known time you compute the
          exact two-sided Garwood 95% interval on the rate, and a short window gives only a wide
          upper bound. A PASS/UNRESOLVED/FAIL verdict follows from pre-set bands. A second panel
          turns an output rate and window length into a sample count and shows a stable p99 needs
          several thousand samples (~3000 → ~30 tail points). (notes B3, C4, C6.)
Inputs:
  - events observed (slider): 0 … 60 misses. Why: 0 (prove-a-bound case) to a clearly-failing count.
  - minutes observed (slider): 1 … 120 min. Why: a too-short window to a long one that tightens the CI.
  - PASS band a (slider): 0 … 2 /min. Why: the pass ceiling; PASS needs rate ≤ a AND upper ≤ b.
  - FAIL band b (slider): 0 … 3 /min. Why: FAIL if lower > b; between a and b is UNRESOLVED.
  - output rate (slider): 1 … 200 Hz. Why: a slow topic to a 200 Hz loop.
  - window length (slider): 10 … 600 s. Why: around the kit's 300 s illustrative window.
Outputs (all derived):
  - point rate = events / minutes (per min).
  - 95% Garwood lower = 0 if k=0 else chi2inv(α/2, 2k)/2 / T; upper = chi2inv(1−α/2, 2k+2)/2 / T,
      with chi2inv = 2·gammaPinv(p, df/2) computed in-page (series + continued-fraction gamma).
  - verdict: FAIL if lower>b; PASS if rate≤a and upper≤b; else UNRESOLVED.
  - samples in window = rate(Hz) × seconds; top-1% tail points = samples × 0.01; p99 stable if ≥ 30.
Picture: SVG interval bar (point + lower/upper whiskers) over shaded PASS (≤a) and FAIL (>b) bands;
         a second SVG bar splitting the samples into the lower-99% body and the top-1% tail.
Preloaded cases: none (the two self-test points — 0/30 min and 12/30 min — are the reachable anchors).
Measured overlays: none — this is a statistics page; the "measurements" are the user's count/rate.
Out of scope: moving-block bootstrap, t-interval across replicate blocks, overdispersion, paired
         differences (named in note B3; not computed here).
```

Self-tests (reproduce the known Garwood bounds):
1. 0 events in 30 min → lower 0, upper ≈ 0.123 /min.
2. 12 events in 30 min → [0.207, 0.699] /min.
3. chi2inv(0.5, df=2) = −2·ln(0.5) (median sanity).
4. 50 Hz × 300 s = 15,000 samples; top 1% = 150 points.
5. 3000 samples → ~30 points in the top 1% tail (the kit's rule of thumb).

---

## Spec — 03-perception-scaling-with-people.html  (notes A2, C1)

```
Explorer: As people are added, CPU post-processing overtakes the GPU — and a rate cap hides it
Teaches:  People perception pays a fixed per-frame cost plus a per-person cost on BOTH the GPU
          (small networks) and the CPU (NMS, Kalman, Hungarian, projection, One Euro filtering,
          divided across the quota's cores). The larger side binds; there is a crossover N where
          CPU overtakes GPU; and a software rate cap can hold the output below both, hiding the
          compute limit. All time inputs are illustrative. (notes A2, C1; rate-cap trap from B2.)
Inputs:
  - N people (slider): 1 … 20. Why: only per-person stages scale with N; per-frame stays flat.
  - per-frame GPU time (slider): 0 … 30 ms. Why: whole-frame detection + NMS on GPU. Illustrative.
  - per-person GPU time (slider): 0 … 10 ms. Why: face/re-ID/pose per person. Illustrative.
  - per-frame CPU time (slider): 0 … 30 ms. Why: fixed CPU glue each frame. Illustrative.
  - per-person CPU time (slider): 0 … 10 ms. Why: Kalman/Hungarian/projection/filter. Illustrative.
  - CPU quota (slider): 1 … 8 cores. Why: CPU post-processing parallelises across the quota's cores.
  - target rate / frame budget (slider): 5 … 30 Hz. Why: budget = 1000/rate ms; 10 Hz illustrative.
Outputs (all derived):
  - GPU per-frame time = gpuFrame + N·gpuPerson.
  - CPU per-frame wall time = (cpuFrame + N·cpuPerson) / quotaCores.
  - which side binds: max(GPU,CPU) is the compute floor; if the frame budget ≥ floor, the software
      RATE CAP binds (delivered = target); else the larger compute side binds (delivered = 1000/floor).
  - latency per frame; delivered rate (Hz); crossover N where CPU overtakes GPU (continuous solve).
Picture: SVG line chart of GPU and CPU per-frame time vs N, the dashed frame-budget line, a marked
         crossover point, and a vertical marker at the current N.
Preloaded cases (illustrative): "CPU-heavy post-processing", "GPU-heavy networks", "Rate-capped service".
Measured overlays: none — all inputs are illustrative times, as the task requires.
Out of scope: occlusion (fewer than N detected), per-stage roofline, memory bandwidth, multi-camera.
```

Self-tests:
1. per-frame vs per-person: GPU at N=1 = frame+person; at N=0 = per-frame only.
2. CPU divides by quota cores: serial 20 ms over 2 cores = 10 ms wall.
3. crossover equalises GPU and CPU per-frame time at N* > 0.
4. rate cap binds (binder = RATE, delivered = target) when compute fits the budget.
5. a heavy N with a tight budget makes a compute side bind and delivered rate < target.

---

## Files

| File | Teaches | Key inputs | Sources |
|---|---|---|---|
| `01-cpu-quota-and-throttling.html` | a CFS quota caps cores against demand; throttled_usec ≠ demand | demand, quota, period, threads | notes A7/B0; CFS bandwidth docs |
| `02-deadline-misses-and-sample-size.html` | exact Garwood Poisson interval; a short window proves only a weak bound; p99 sample size | events, minutes, bands, rate, window | notes B3/C4/C6; Garwood 1936 |
| `03-perception-scaling-with-people.html` | CPU post-processing overtakes GPU as N grows; a rate cap hides the limit | N, per-frame/per-person GPU & CPU times, quota, rate | notes A2/C1; B2 rate-cap trap |
| `params.json` | the constants the pages load | — | copied from `../constants.json` |

Open with a double-click, or `open 01-cpu-quota-and-throttling.html`. No server, no network, no build step.
