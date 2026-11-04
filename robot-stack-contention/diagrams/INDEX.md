# Diagrams — robot-stack-contention (rung 2)

Nine diagrams, one draw.io page each, exported to `.drawio` + `.svg` + `.png`. They are the picture layer for notes A0, A1, A2, A5, B1, B2, B3 and B4. This is one merged index: pages 01–05 are described first; pages 06–09 follow under "Pages 06–09". On page 07 the number and spacing of the GPU dots are schematic, not data.

**Every number on every canvas is loaded from [`../constants.json`](../constants.json)** by the page's `specNN.py`; nothing is retyped. Each number carries its key in brackets. The first tag of an illustrative key on a page reads `[key, illustrative]`. Illustrative numbers are round teaching numbers that keep the shape of a finding; they are not measurements. Arithmetic derived from constants is written "my estimate from `key` and `key`". Each canvas has its own legend and a sources block, built from the keys used on that page, so an exported image stands alone.

Background is linked, not re-taught: GPU contexts, streams, time-slicing, MPS and MIG in [`../../nvidia-gpu-anatomy/`](../../nvidia-gpu-anatomy/README.md); board ceilings and the ridge in [`../../jetson-orin-thor-metrics/`](../../jetson-orin-thor-metrics/README.md); how to benchmark a robot stack in [`../../robot-workload-benchmarking/`](../../robot-workload-benchmarking/README.md).

## Shared conventions

- **Colour, always doubled by dash, shape or a text tag:** blue = CPU cause or CPU term; green = GPU cause or GPU term; amber = our bench or our software, not the platform; purple dashed border = a correction (first reading -> corrected); dashed outline or dashed line = a prediction or a pre-registered line.
- **Verdicts keep the notes' pre-registered wording** ("undecided at dose", "split", "dose explains", "most (or less board traffic)"). Post-hoc readings are labelled post-hoc.
- **Title states the finding.** One idea per page.
- **Generic names only:** a home-robot software stack ("the stack"; "full stack" = every module on), the depth camera service, the object detector, the interaction service, the speech recognizer, the dialogue engine, the motor-control services, the measurement probe, a VLA (vision-language-action model), an Orin-class 12-core board. Reserved cores are labelled A–D; the letters are labels, not core numbers.

## Per-diagram specs

### 01-diagnosis-map (note A0)
```
Teaches:  each service slows for its own reason: pool CPU from alone to the full stack, GPU turns from the
          full stack to full stack + VLA, and two of the largest full-stack numbers were our bench
          (the interaction service) and a logging bug (the voice chain), not the platform.
Type:     matrix, one row per service, four columns:
          service + symptom -> cause (+ confidence) -> experiment that showed it -> correction.
Elements: the depth camera service [camera_hz_alone, camera_full_stack_loss_hz, camera_gpu_only_loss_hz,
          camera_fanout_loss_hz, cpu_weight_default, weight_raised]; the object detector
          [detector_frame_ms_solo_full]; the voice chain [transcript_latency_ms, ms_per_history_item,
          history_items, context_build_ms_filtered]; the interaction service [interaction_accepted_ms];
          the motor-control services [cycles_growth_range, instr_growth, cluster_move_recovered,
          cluster_move_class_line]; the VLA [vla_offered_hz, vla_call_ms, vla_gpu_ms_per_call,
          gpu_free_next_to_stack]. Footer: corrections not tied to one service
          [kernel_time_sms_full_share (theoretical), vision_pred_bandwidth_form_ms, vision_compute_form_ms].
Colour:   cause cell blue [CPU] / green [GPU] / teal both / amber [BENCH] or [BUG]; corrections purple dashed.
Left out: the numbers behind each mechanism (pages 02–05 and the notes).
```

### 02-core-map-and-observers (notes A1, A5)
```
Teaches:  one reserved core was saturated by three equal tenants, one of them our probe; moving the probe
          to a pool core freed the interaction service but cost the camera frames, so no placement is free.
Type:     block diagram of the board's cores + before/after comparison table.
Elements: pool [pool_cores, pool_busy_frac_full, pool_wait_per_busy_full, pool_wait_per_busy_camera_only];
          reserved cores [reserved_cores, board_cores]: A = middleware router (not tested), B = saturated,
          three groups at equal CFS shares [saturated_core_equal_share], C-D = the motor-control services,
          "never observers"; cluster bracket (cores A, C and D share the motor-control services' CPU cluster). Table: accepted p50 [interaction_accepted_ms], core state,
          main-thread wait (qualitative), CPU shares (caps, not demands), probe receive delay
          [probe_receive_delay_ms], probe demand [probe_cores_wanted], camera cost
          [probe_on_pool_camera_cost_hz]. Panels: observer-effect verdict, "no placement is free",
          new baseline [interaction_accepted_ms: probe_moved, transcript_latency_ms: full_filtered].
Colour:   pool blue; reserved grey (thick dark border = motor control); our observers amber dashed.
Left out: which services sit on each pool core (attribution on the pool is approximate).
```

### 03-where-the-detectors-frame-goes (notes A1, B1)
```
Teaches:  from alone to the full stack the detector's frame grows mostly by CPU terms (wait + slower run);
          from the full stack to full stack + VLA it grows mostly by GPU-blocked time.
Type:     stacked horizontal bars, ms per frame, to scale; three bars: alone, full stack, + VLA.
Elements: [detector_frame_ms_solo_full]; full-stack added wait / run / blocked
          [detector_added_wait_run_blocked]; + VLA added blocked / wait / run
          [detector_vla_added_blocked_wait_run]; + VLA total and both shares = my estimates.
Colour:   wait mid-blue solid, run light blue dashed, blocked green solid, previous level grey.
Caveats:  the GPU mechanism was tested in a camera-plus-detector row; in the full stack it is expected,
          not tested. The correction to "within round-to-round spread" is shown as a correction.
```

### 04-same-work-more-cycles (note A2)
```
Teaches:  in the full stack fixed-work threads run the same instructions with more cycles (IPC falls);
          moving the motor-control services' cluster-mates removes about two thirds of the extra cycles,
          class "most (or less board traffic)", close to the pre-registered class line.
Type:     left: ratio-to-alone bars (range bars, solid to the low end, dashed to the high end);
          right: schematic baseline / moved / alone bars + removed-fraction strip with the class line.
Elements: [instr_growth, cycles_growth_range, ipc_drop_range, l3_refill_ratio_range];
          [cluster_move_recovered, cluster_move_class_line, cluster_move_camera_cost_hz].
          Full-stack ratio = 1 + growth and IPC = 1 − drop are my estimates.
Colour:   alone grey; full stack blue; IPC thick dark-blue border; prediction dashed; why-open purple
          dashed; cost of the fix amber.
Left out: per-thread values and cycle counts (the constants give ranges and the ratio f only, so the
          baseline / moved bars are labelled schematic). Arms are named "baseline" and "moved";
          f = (X_base − X_moved) ÷ (X_base − X_alone).
```

### 05-gpu-time-slicing-vs-mps (notes B1, B3)
```
Teaches:  without MPS two processes take turns on the whole GPU (each about half busy); under MPS one-SM
          kernels run side by side, but only for clients of one Linux user; a stack split over two users
          would stall.
Type:     two timelines (time-slicing vs MPS) + SM-cap strip; right panel = the one-user catch.
Elements: [mps_no_concurrency_quote, timeslice_ms, sm_count_orin, mps_probe_busy_frac,
          mps_thread_percentage_env, mps_cap_visible_sms, launch_overhead_us, mps_launch_path_quote,
          mps_one_user, mps_tegra_unsupported, mps_dynamic_parallelism, mps_tegra_since,
          kernel_time_sms_full_share].
Colour:   client A green solid; client B orange dashed; context switch dotted; deployment constraint amber;
          correction purple dashed.
Caveats:  synthetic one-SM test kernels only; the real services never ran under MPS; the gain for real
          services is a hypothesis; the deciding test was not run.
```

## As built

| File | Teaches | Sources used |
|---|---|---|
| `01-diagnosis-map.{drawio,svg,png}` | Each service slows for its own reason; two of the largest full-stack numbers were the bench and a logging bug. | Notes A0–A5, B1–B4, C1; keys listed on the canvas |
| `02-core-map-and-observers.{drawio,svg,png}` | A saturated reserved core gives equal caps; the probe was one tenant; no placement is free. | Notes A1, A5 |
| `03-where-the-detectors-frame-goes.{drawio,svg,png}` | Alone -> full stack is mostly CPU; full stack -> + VLA is mostly GPU-blocked time. | Notes A1, B1 |
| `04-same-work-more-cycles.{drawio,svg,png}` | Same instructions, more cycles; the cluster move recovers about two thirds, with caveats. | Note A2 |
| `05-gpu-time-slicing-vs-mps.{drawio,svg,png}` | Turns without MPS, side by side with MPS, but one Linux user only. | Notes B1, B3; NVIDIA MPS docs (public keys) |

## Rendering

Each page is one cell list in `specNN.py`, rendered two ways from the same list by `.render_local.py`: an editable `.drawio`, and a standalone `.svg` (a rect per box plus a `<foreignObject>` XHTML label; polylines for edges), rasterised to `.png` by headless Chrome at 2×. Helpers: `_common.py` (constants loader `V()`, tag registry `Tags()`, sources block), `_charts.py` (axes and bars, geometry only). To regenerate one page, from this folder:

```
python3 .render_local.py spec01.py
```

Each PNG was read back after rendering and fixed for clipped or overlapping labels. Every file was checked with `../../tools/public-scan.sh` (clean).

## Pages 06–09

Pages 06–09 of the robot-stack-contention kit, for notes B1, B2 and B4. Each page is one spec file (`specNN.py`). The local renderer (`.render_local.py`) turns it into an editable `.drawio`, a standalone `.svg` and a 2× `.png`. Every number on a canvas is loaded from [`../constants.json`](../constants.json) and tagged with its key. The first tag of an illustrative key on a page says "illustrative". Derived values say "my estimate from …". Each page has its own sources block.

**Most numbers here are illustrative**: round teaching numbers that keep the shape of a finding. They are not measurements. The board ceilings on page 09 are `sibling` keys from [`../../jetson-orin-thor-metrics/`](../../jetson-orin-thor-metrics/README.md). The CUDA limits on page 08 are `public` keys.

| File | Teaches | Note | Keys used |
|---|---|---|---|
| `06-dose-curve.drawio / .svg / .png` | Without MPS, the object detector's added GPU wait follows the other processes' share of GPU time on a convex curve. The VLA point lies on the compute co-tenant's curve ("dose explains"). A memory-copy co-tenant at the same GPU time adds nothing. Two predictions were wrong. The first test's "neither alone" is kept visible as a correction. | B1 | `dose_curve_points`, `dose_vla_point`, `dose_slopes`, `dram_null_added_ms`, `burst_length_effect_ms`, `timeslice_ms`, `detector_vla_added_blocked_wait_run`, `mps_no_concurrency_quote` |
| `07-camera-one-load-at-a-time.drawio / .svg / .png` | GPU load alone costs the depth camera service no frames (flat). Shared-pool CPU wait costs it frames (the one valid arm, at half the full stack's wait; the higher arm is void), so the pool verdict is "undecided at dose". The GPU dot count and spacing are schematic; the fan-out segment is a light-blue hatch (CPU-side). Fan-out takes a minor share. The three loads were not tested together. | B1 | `camera_hz_alone`, `camera_gpu_only_loss_hz`, `camera_pool_loss_hz`, `camera_fanout_loss_hz`, `camera_full_stack_loss_hz` |
| `08-full-sm-low-issue.drawio / .svg / .png` | A low SM issue rate is not free room. About half the kernel time fills an SM on some resource (registers or shared memory, not warps). Multi-wave kernels are expected to gain from more SMs. Fill numbers are theoretical, from launch configurations. | B2 | `sm_issue_full_stack`, `gpu_active_full_stack`, `kernel_time_sms_full_share`, `gemm_warp_slot_fill`, `multiwave_share`, `sm_count_orin`, `max_warps_per_sm`, `max_blocks_per_sm_cc87`, `registers_per_sm`, `l1_shared_per_sm_orin_kb`, `warp_size`, `register_alloc_unit_per_warp`, `max_registers_per_thread` |
| `09-ridge-two-boards.drawio / .svg / .png` | The same vision encoder sits well above the Orin's ridge, so it is compute-bound and the compute form of the prediction is right. It sits near Thor's effective ridge, so neither form alone is safe. Ridges and Thor times are my arithmetic from the sibling ceilings. | B4 | `tensor_fp16_orin`, `dram_read_orin`, `tensor_fp16_thor`, `pi05_sustained_bandwidth_thor`, `shape_rate_fraction`, `vision_encoder`, `vision_pred_bandwidth_form_ms`, `vision_compute_form_ms`, `vision_measured_ms_orin`, `dram_read_thor` (read-peak caveat: Thor's ridge at the read peak, about 3× the Orin's rather than 4×; the encoder stays near it) |

Related kits (not re-taught here): contexts, time-slicing, MPS and occupancy in [`../../nvidia-gpu-anatomy/`](../../nvidia-gpu-anatomy/); ceilings and the ridge in [`../../jetson-orin-thor-metrics/`](../../jetson-orin-thor-metrics/); how to benchmark a robot stack in [`../../robot-workload-benchmarking/`](../../robot-workload-benchmarking/).

## Re-render

```sh
cd learning/robot-stack-contention/diagrams
python3 .render_local.py spec06.py spec07.py spec08.py spec09.py   # or any specNN.py
```

The renderer needs headless Google Chrome (it runs with `--no-sandbox`) for the PNG step.

## Drawing choices that are not data

- Page 07, GPU panel: the number of circles on the flat line and their even spacing are schematic. The kit gives no GPU dose values, so the x axis has only "none" and "max" (the highest dose tested).
- Page 07, pool panel: the x position of each arm (0.5 and 2 times the full stack's wait) comes from the field names of `camera_pool_loss_hz`.
- Page 08: the gauges and the waves strip are schematics. The waves strip shows one block per SM for clarity.
- Page 08: the "full" threshold (90 %) is read from the source text of `kernel_time_sms_full_share`.
- Page 09: the axes are approximate (log scale). The labelled values are exact.
