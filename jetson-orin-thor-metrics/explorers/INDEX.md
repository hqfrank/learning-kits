# Explorers — rung 3 (learn-explorer)

Two single-file, no-build, double-click HTML explorers for the *jetson-orin-thor-metrics* kit.
Each inlines its parameters in a `<script type="application/json">` block (also written out as
`params.json`), every parameter copied from `../constants.json` with its source — nothing retyped.
Prediction functions are factored into a pure IIFE that also runs under node (used for the self-tests
and the NaN slider-extreme sweep). Both pass their `console.assert` self-tests and a NaN sweep over
every slider/selector extreme (64 and 300 combinations respectively; 0 bad).

---

## Spec — 01-roofline-explorer.html

```
Explorer: Roofline explorer (Orin / Thor)
Teaches:  A kernel's arithmetic intensity (FLOP/byte) decides which ceiling binds it — the sloped
          memory roof or the flat compute roof — so on these boards where a kernel lands is a memory
          question, not a TOPS question (§A.2/A.3/A.6, §C.1).
Inputs:
  - board (select): Thor T5000 (sm_110) | AGX Orin (sm_87) — picks the measured roofs.
  - precision roof (select): tcgen05 FP16 (Thor) | classic-mma FP16 | classic-mma INT8 |
      NVFP4 dense (Thor) | CUDA-core FP32. Thor-only roofs degrade gracefully on Orin.
  - bytes per inference (log slider): 1 MB … 50 GB. Why: spans WBC weights (~0.5 MB) to a
      16-bit π0.5 inference (~19 GB measured).
  - FLOPs per inference (log slider): 1 GFLOP … 20 TFLOP. Why: WBC (~1 MFLOP) to π0.5 (4344 GFLOP).
  - footprint (log slider): 1 KB … 256 MB. Why: straddles both boards' L2 (4 / 32 MB) to show the
      cache-level cliff.
Outputs:
  - arithmetic intensity (FLOP/byte) = FLOPs / bytes (derived).
  - binding roof: compute (TFLOP/s or TOP/s) if AI ≥ ridge, else memory (GB/s of the level the
      footprint lands in). Equation: attainable = min(roof, memBW·AI); ridge = roof·1e3 / memBW.
  - predicted latency (ms): memory-bound → bytes / bandwidth; compute-bound → FLOPs / roof (teaching
      form of §C.1's per-phase model).
  - cache level the footprint lands in: L2-resident plateau if footprint ≤ L2 capacity, else DRAM
      plateau (§A.6 Table A.6.2).
Picture: SVG log-log roofline that moves — sloped memory roof (bandwidth of the resident level)
         meeting the flat compute roof at the ridge; a predicted point (circle) and, for real cases,
         a measured point (diamond, distinct colour) at the same AI.
Preloaded cases (from the notes):
  - π0.5 16-bit (Wbf16Abf16): predicted 64.1 ms vs measured 90.06 ms (1.40× gap), §C.1 Tables C.1.5/C.1.6.
  - π0.5 8-bit (Wfp8Afp8@fp16): predicted 37.4 ms vs measured 53.03 ms (1.42× gap).
  - π0.5 action expert alone: memory-bound, AI ≈ 10 in C.1 (0.30 B weights re-read 10 denoising steps).
  - WBC MLP: INT8 80-512-256-128-23, measured solo p99 41.6 µs (Thor), B.8.
  - 1024² FP32 GEMM: compute-bound, right of the ridge (Orin CUDA-core FP32).
Measured overlays: π0.5 16-bit 90.06 ms, π0.5 8-bit 53.03 ms, WBC solo p99 41.6 µs (Thor) — diamonds,
  distinct from the predicted circles.
Out of scope: multi-GPU, write bandwidth asymmetry, the per-shape M-mod-16 GEMM discontinuity (noted in
  the why-panel but not modelled), fidelity, power.
```

Self-tests (reproduce the source's own numbers):
1. π0.5 16-bit bytes ÷ sustained 197.3 GB/s ≈ 98 ms (orders onto measured 90.06 ms within C.1's optimism band).
2. Thor tcgen05 FP16 ridge against 197.3 GB/s ≈ 975 FLOP/byte.
3. 1024³ FP32 GEMM latency on Orin = 2·N³ / 5.15 TFLOP/s (compute roof reproduced exactly).
4. π0.5 16-bit arithmetic intensity = 4344 GFLOP / 19.44 GB ≈ 208 FLOP/byte.

---

## Spec — 02-who-pays-explorer.html

```
Explorer: Who pays? (co-tenancy on one Thor GPU)
Teaches:  The GPU is a fixed pie; the sharing discipline decides which tenant absorbs the deficit, and
          a named mechanism governs each cell — SM fair-share, DRAM share, L2 eviction, SM-co-schedule
          lockout, the CPU-hog cliff, or the 172 GB/s floor (§B.4/B.5/B.6/B.8, L4 ladder).
Inputs:
  - victim class (select): WBC (INT8 MLP, 100 Hz) | IM (fp32 GEMV) | RM (real M=1 decode GEMM).
  - aggressor (select): INT8 compute (SM-saturating) | fp32 memory | VLM prefill | VLM decode |
      VLA backbone (NVFP4 tensor, Thor).
  - topology (select): shared context | separate process | MPS plain | MPS cap 25 | MPS cap 35
      (the L4 scheduling ladder).
  - CPU memory load (slider): 0 … 200 GB/s. Why: crosses the ~120 GB/s half-ceiling cliff (§B.5) and
      the 172 GB/s collapse floor (L4).
  - victim L2 footprint (log slider): 1 KB … 64 MB. Why: straddles Thor's 32 MB L2 to toggle eviction.
Outputs:
  - predicted slowdown (×) = 1 + (gpu_contended − 1)·topology_factor·cpu_hog_multiplier.
  - predicted p99 (ms) = victim solo p99 × slowdown, flagged against the 10 ms deadline.
  - governing mechanism, named, changing with the inputs (the why-panel).
Picture: horizontal bars of predicted vs measured victim p99 against a 10 ms deadline line; axis
         switches to log when any bar exceeds 30 ms (shared-context / plain-MPS rungs).
Preloaded cases (from the notes):
  - B.6 IM∣IC — compute aggressor poisons a memory victim 4.19× (Thor), §B.6 Table B.6.3.
  - B.8 WBC + INT8 + hog — measured 3.37 ms, §B.8 Table B.8.1.
  - B.8 worst mix — 141× solo = 5.9 ms, under the 10 ms deadline, §B.8 Fig B.8.1.
  - L4 shared context — π0.5 VLA blows WBC p99 to 110.7 ms (64×), 51% dropped.
  - L4 MPS cap-35 — the fix: 9.1 ms, 0% dropped under the deadline.
Measured overlays: B.8 Table B.8.1 single-aggressor cells (CPU-idle and CPU-hog columns) for every
  non-VLA aggressor; the L4 ladder rungs (110.7 / 17 / 61 / 7.5 / 9.1 ms) when the aggressor is the VLA.
Out of scope: Orin co-tenancy p99 absolutes (B.6 reports slowdown factors, not solo p99 for IM/RM),
  MIG (deferred in L4), calibrated int8, ROS2 transport, GR00T-specific rungs.
```

Self-tests (reproduce the source's own numbers):
1. SM fair-share null model = 2 (§B.6 Table B.6.2).
2. DRAM share IM∣IM on Thor = 2·255 / 245 ≈ 2.08 (§B.6 Table B.6.2).
3. CPU-hog multiplier ≈ 1 at 0 GB/s and collapses (≥ 20×) past the 172 GB/s floor (L4).
4. MPS cap-35 holds WBC under the 10 ms deadline with a VLA aggressor, no hog (L4 rung 3b).

---

## Files

| File | Teaches | Key inputs | Sources |
|---|---|---|---|
| `01-roofline-explorer.html` | which roof binds, and the predicted↔measured latency gap | board, precision, bytes, FLOPs, footprint | §A.2, §A.3, §A.4, §A.6, §C.1 |
| `02-who-pays-explorer.html` | which tenant pays and why, per sharing discipline | victim, aggressor, topology, CPU load, footprint | §B.4, §B.5, §B.6, §B.8, L4 KEY-LEARNINGS |
| `params.json` | the constants both pages load | — | copied from `../constants.json` |

Open with a double-click, or `open 01-roofline-explorer.html`. No server, no network, no build step.
