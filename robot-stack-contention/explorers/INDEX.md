# Explorers — rung 3 (learn-explorer) · robot-stack-contention

Three single-file, no-build HTML explorers. Open one with a double-click (`open 01-gpu-dose-curve.html`).
There is no server, no network and no build step.

Each page inlines a `<script type="application/json" id="params">` block, and the same entries ship as
`params.json`. Every entry is copied verbatim from `../constants.json` (value, unit, class, source) by a generator
script. Nothing is retyped. The page renders these entries as its sources table. The pure model functions sit
between `/*MODEL-START*/ … /*MODEL-END*/`, run under node too, and carry a `selfTest(P)` that reproduces the
notes' numbers with `console.assert`.

**This kit carries no measured numbers from any specific robot.** Every value is `public` (a cited URL),
`sibling` (a key in a sibling public kit) or `illustrative` (a round teaching number that keeps the shape of a
finding). The pages label illustrative values "illustrative" on the plotted points, in the metric tags and in the
sources table.

The sibling kits teach the background. These pages link to them and do not re-teach it:
[`../../nvidia-gpu-anatomy/`](../../nvidia-gpu-anatomy/) (contexts, time-slicing, MPS, occupancy),
[`../../jetson-orin-thor-metrics/`](../../jetson-orin-thor-metrics/) (ceilings, ridge, per-SM limits),
[`../../robot-workload-benchmarking/`](../../robot-workload-benchmarking/) (how to benchmark a robot stack).

| File | Teaches | Inputs | Sources (keys) |
|---|---|---|---|
| `01-gpu-dose-curve.html` (B1) | Without MPS, the object detector's added GPU wait follows the other processes' share of GPU time (O), and the curve is convex. So the first points cut from the VLA's share buy back the most. | O (0 to the highest arm), cut x (0–30 points), preloaded arms | `dose_curve_points`, `dose_vla_point`, `dose_slopes`, `timeslice_ms`, `mps_no_concurrency_quote`, `dram_null_added_ms`, `burst_length_effect_ms`, `detector_vla_added_blocked_wait_run`, `camera_gpu_only_loss_hz` |
| `02-vla-gpu-budget.html` (C1, B1) | A VLA's GPU need is GPU time per call × rate, not call time × rate. At the offered 5 Hz it needs more than the free share next to the stack. About 2.5 Hz fits, 3 Hz is at the edge. This is a budget estimate, not a test. | rate (0.5–6 Hz), free share (10–80 %), sharing overhead (0–30 %) | `vla_call_ms`, `vla_gpu_ms_per_call`, `vla_offered_hz`, `gpu_free_next_to_stack`, `sharing_overhead`, `batch1_latency_ms`, `dose_slopes` |
| `03-kernel-fill-calculator.html` (B2) | Blocks per SM are the minimum over four limits, so a register-bound GEMM fills an SM with few warps. A low issue rate is not free room. Large grids run in waves. The fill is theoretical, from launch configuration. | threads per block, registers per thread, shared memory per block, grid (log) | `sm_count_orin`, `max_warps_per_sm`, `max_blocks_per_sm_cc87`, `registers_per_sm`, `l1_shared_per_sm_orin_kb`, `warp_size`, `register_alloc_unit_per_warp`, `max_threads_per_block`, `max_registers_per_thread`, `kernel_time_sms_full_share`, `gemm_warp_slot_fill`, `multiwave_share`, `sm_issue_full_stack`, `gpu_active_full_stack` |

---

## Spec — 01-gpu-dose-curve.html (note B1)

```
Explorer: The object detector's GPU wait follows the others' share of GPU time, and the curve is convex
Teaches:  In the reduced row (depth camera service + object detector, idle CPU pool), without MPS, the
          detector's added blocked time per frame rises with O faster than O itself. Near the VLA's
          dose each point of O costs more than the average, so the first points cut buy back the most.
Inputs:   O (slider) 0 … highest arm of dose_curve_points (no extrapolation); default = dose_vla_point O.
          cut x (slider) 0 … 30 points.
Outputs:  added_blocked_ms(O) = piecewise-linear through dose_curve_points (model).
          local slope = slope of the segment that holds O (vs dose_slopes).
          bought_back_ms(O, x) = added(O) − added(max(0, O − x)).
          C*/R = added(O_VLA) ÷ R (my estimate from dose_curve_points and dose_vla_point).
Picture:  SVG x = O, y = added ms/frame. Line = model; circles = illustrative compute arms; diamond =
          illustrative VLA arm; green band and bar = time bought back by the cut.
Cases:    the four compute arms and the VLA arm.
Overlays: the arms themselves (illustrative). Nulls table: copy co-tenant, burst length, short bursts not tested.
Out of scope: the full stack (expected, not tested); slice wait vs switch cost (not measured).
```

**Self-tests (20):** the curve passes through every arm. The slopes equal `dose_slopes` (1 / 2 / 4) and rise
(convex). C\* = 100 ms and C\*/R = 1.0 ("dose explains"). C at the highest dose ÷ R = 1.6, so the
prediction "below R" was wrong. The first test's arm gave 40 % of R and sits below the VLA's dose. The local slope
at the VLA's dose is above the average R ÷ O. Edge rules for the cut. No extrapolation (NaN by design). The nulls
are 0 ms. Blocked time is the largest part of the rise next to the VLA.

## Spec — 02-vla-gpu-budget.html (notes C1, B1)

```
Explorer: Next to the full stack, the offered VLA rate does not fit in the free GPU time
Teaches:  need = rate × vla_gpu_ms_per_call × (1 + overhead); compare with gpu_free_next_to_stack.
          Call time × rate (vla_call_ms) is the wrong budget.
Inputs:   rate 0.5 … 6 Hz (default vla_offered_hz); free share 10 … 80 % (default gpu_free_next_to_stack);
          overhead 0 … 30 % (default = high end of sharing_overhead, the conservative end; applying it
          per call is my assumption).
Outputs:  need share, highest fitting rate, naive share (call time × rate, the wrong method), verdict.
          Verdict across the sharing_overhead band: fits = fits at the high end; edge = fits only at
          the low end; does not fit otherwise. The band width sets the edge, not a page convention.
          The headline verdict uses the band while the overhead slider is inside it, and the slider's
          own value (fits / does not fit) outside it; its label names the overhead used.
Picture:  need line + overhead band, free-share line, fits region, naive dashed line, rate marker.
Cases:    5 Hz (does not fit), 3 Hz (edge), 2.5 Hz (fits); each resets the free share and the overhead.
Overlays: none. No rate below the offered one was run next to the stack (stated in the banner).
```

**Self-tests (11):** naive = 0.75 s/s and GPU need = 0.6 s/s at 5 Hz. The ceiling without overhead is about
3.3 Hz. With the overhead band it is 2.8–3.0 Hz (all as printed in C1). The defaults come from the params block.
5 Hz does not fit even at zero overhead. 2.5 Hz fits and 3 Hz is at the edge. The need is below the naive budget
at every rate. Overhead only lowers the ceiling. The re-planning rate is 1000 ÷ 250 ms = 4 Hz.

## Spec — 03-kernel-fill-calculator.html (note B2)

```
Explorer: An SM can be full with few warps
Teaches:  blocks per SM = min(warps, blocks, registers, shared-memory limits); binding fill = largest
          used fraction on the busiest SM in the first wave; full at >= 90 % (parsed from the source
          text of kernel_time_sms_full_share); waves = grid ÷ (SMs × blocks per SM).
Inputs:   threads 32 … max_threads_per_block (step warp_size); registers 16 … max_registers_per_thread;
          shared memory 0 … l1_shared_per_sm_orin_kb; grid 1 … 65 536 (log slider range).
Outputs:  per-limit blocks, binding resource, warp-slot fill, binding fill, waves, last-wave fill.
Picture:  four fill bars with the 90 % line; 16 SM tiles shaded by fill, block counts, wave count.
Cases:    my illustrative launch configurations: register-bound GEMM (warp-slot fill inside
          gemm_warp_slot_fill), warp-filling element-wise kernel, small grid.
Table:    the note's illustrative shares (kernel_time_sms_full_share, gemm_warp_slot_fill,
          multiwave_share) plus sm_issue_full_stack vs gpu_active_full_stack. No per-service table.
Out of scope: achieved occupancy, stalls, co-residency under MPS (not measured); L1 carve-out.
```

**Self-tests (26):** the limits match B2's table, and the threshold parses to 0.9. B2's worked example works:
at most 40 registers per thread fill all 48 warps, and 41 do not. The register granularity is 256. The per-thread
and per-block maxima are enforced. The GEMM case binds on registers at 91 % with 17 % of warp slots and runs in
10 waves. The element-wise case has warps binding and 43 waves. The small grid leaves 8 of 16 SMs idle. Exact
register-file fill holds. The illustrative shares are ordered fractions. Issue rate < GPU active, and GEMM
warp-slot fill < the full-kernel share.

---

## Verification

- **node:** each inline params entry deep-equals both `constants.json` and `params.json`.
- **Headless Chromium (Playwright), 1280 px and 390 px:** no console errors, failed asserts or horizontal
  overflow. Self-tests pass on every page (01: 20, 02: 11, 03: 26). Each slider at its min and its max, one
  at a time, then all at min and all at max, and every preloaded case: no "NaN", "Infinity" or "undefined"
  in the page text.
