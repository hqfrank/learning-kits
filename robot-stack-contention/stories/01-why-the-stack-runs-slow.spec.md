# Spec — story 01: Why the stack runs slow

Rung: story (learn-story). Kit: `robot-stack-contention`. Page: `01-why-the-stack-runs-slow.html`.
Runtime: `../../stories/story.css` + `../../stories/story.js` (linked, not copied, not edited).
Numbers: only from `../constants.json`. A small generator copies every key the page uses, verbatim, into the
page's `<script type="application/json" id="params">` block. Captions fill numbers from that block with `{{key}}`
templates, so no number is retyped in prose. Derived values are labelled "my estimate from `<key>`".
**Every measurement on the page is illustrative** (class `illustrative` in `constants.json`): a round teaching
number that keeps the shape of a typical finding. The page says so under the headline, on every figure that shows
one (`illustrative` tag), and in the footer.

## The question (in the learner's words)
"Every service of the stack is slower when the whole stack runs on the board. Is it one thing, the GPU? Is the
board just too small?"

## The one-sentence answer (headline)
Everything is slower when the whole stack runs, and each service has its own reason.

Hero picture: one kitchen (an Orin-class 12-core board) with stations, each slowed by a different, coloured cause:
order tickets waiting for the eight shared cooks, a crowded spice rack behind the walled alcoves, one oven that
takes turns, our own inspector squeezed into an alcove, and a waiter who reads the whole order book aloud. A ticket
row under it names each service's cause and its scene.

## Metaphor + cast (kitchen family, the same as `../../robot-workload-benchmarking/stories/01-the-robots-kitchen.html`)

| Metaphor | Real term | Why it fits | Where it breaks |
|---|---|---|---|
| The kitchen | an Orin-class 12-core board (`board_cores`) | one place, shared resources | — |
| 8 cooks on the shared floor | the pool (`pool_cores`), shared under CFS | any free cook takes the next ticket; tickets queue | a scheduler does not give a ticket to a named cook; summed wait of parallel threads is not added latency |
| 4 walled alcoves | reserved cores (`reserved_cores`, `isolcpus` + cpuset) | only assigned cooks work there | alcoves still share a cluster cache (the spice rack) |
| Tickets on the rail | runnable threads: run-queue wait | a ticket waits for a free cook | — |
| The oven, one batch at a time | the GPU without MPS: time-slicing between CUDA contexts | a cook waits for the others' turns, not for a free tray | the GPU has 16 SMs (`sm_count_orin`); the picture cannot show MPS side-by-side running |
| The shared spice rack | the CPU cluster's shared cache and the board's memory traffic | same recipe, slower reach → more cycles | the path (cluster cache, board traffic, the services' own load) is not isolated |
| The inspector | our observers: the measurement probe and the request driver | standing in an alcove takes that alcove's cook time | the request driver itself did not wait: the number was measured correctly; it was caused by us |
| The waiter who reads the order book aloud | the dialogue engine's per-item INFO logging on its asyncio thread | the cost grows with the book (O(history)) | the cost is one log emit per item (stdout + `/rosout`), multiplied by CPU contention, not "speaking slowly" |
| The bell | the motor-control services' fast real-time bus loop | a beat that must not be late | no period is given (not in `constants.json`) |
| The notebook | pre-registration: prediction and refutation rule written before the run | predict → measure → correct | — |

## Palette meaning (one hue per real concept, whole page)
coral = CPU queueing on the pool · sky = same work, more cycles (shared cache / memory) · sun = GPU time-slicing ·
stone = our bench (observers) · plum = software cost (logging) · leaf = alone / after a fix.
Corrections: dashed ink outline + a "corrected" tag (shape, not hue). VOID windows: hollow markers.

## Scenes

| # | Claim | Beat | Figure | What moves = what it means | Interaction | Note | Numbers (keys, class) |
|---|---|---|---|---|---|---|---|
| 1 | Every service is slower together, each by its own amount and unit | concrete first | scene player (4 steps) | values per service appear alone → full stack → + VLA (state change); step 4: cause chips + the method strip (predict → change one thing → correct in the open) | step | A0 | `detector_frame_ms_solo_full`, `detector_vla_added_blocked_wait_run`, `camera_hz_alone`, `camera_full_stack_loss_hz`, `interaction_accepted_ms`, `transcript_latency_ms`, `cycles_growth_range`, `stack_services`, `vla_offered_hz` (all illustrative) |
| 2 | Four fifths busy still means tickets wait longer than they cook; for the detector the wait is the largest added term | therefore: CPU first | predict + gated live figure (wait per busy second → wall time per CPU second) + scene player (detector frame, 5 steps) | bars grow = added time per term | predict; slider w | A1 | `pool_busy_frac_full`, `pool_wait_per_busy_full`, `pool_wait_per_busy_camera_only`, `detector_frame_ms_solo_full`, `detector_added_wait_run_blocked`, `pool_cores` (illustrative) |
| 3 | A cook in a walled alcove still slows: same recipe, more cycles; moving the neighbours gave back about two thirds, on the class line, with a traffic caveat | but: no queue in the alcove | scene player (3 steps) + predict + gated f figure | IPC drops; f against the pre-registered line | predict | A2 | `instr_growth`, `cycles_growth_range`, `ipc_drop_range`, `l3_refill_ratio_range`, `cluster_move_recovered`, `cluster_move_class_line`, `cluster_move_camera_cost_hz` (illustrative) |
| 4 | The interaction service's big full-stack number was mostly our inspector in its alcove | but: check the bench | predict + gated scene player (4 steps) | the inspector moves to the floor; the number falls; the camera pays | predict; step | A5 | `interaction_accepted_ms`, `saturated_core_equal_share`, `probe_cores_wanted`, `probe_on_pool_camera_cost_hz`, `probe_receive_delay_ms` (illustrative) |
| 5 | The voice delay was a waiter reading the whole order book aloud | and the full stack multiplies it | live figure | the reading bar grows with items; the transcript ticket waits behind it (head-of-line, schematic) | slider items; filter toggle | A4 | `ms_per_history_item`, `history_items`, `context_build_ms_filtered`, `transcript_latency_ms`, `pool_wait_per_busy_full`, `cycles_growth_range` (illustrative) |
| 6 | Next to the VLA, the detector waits for the oven's turns, by amount, and the curve is convex | therefore: budget GPU time | scene player (4 steps) + predict + gated live dose curve | one tray in the oven at a time; the dot rides the curve | step; predict; slider O | B1 | `timeslice_ms`, `mps_no_concurrency_quote` (public), `dram_null_added_ms`, `dose_curve_points`, `dose_vla_point`, `dose_slopes`, `burst_length_effect_ms`, `detector_vla_added_blocked_wait_run` |
| 7 | The camera is not GPU-bound alone: pool CPU and topic demand (provisional) | but: same oven, different victim | predict + gated scene player (4 steps) | one load at a time; bars appear one per factor; the void arm is hollow | predict; step | B1 § camera, A3 | `camera_hz_alone`, `camera_gpu_only_loss_hz`, `camera_pool_loss_hz`, `camera_fanout_loss_hz`, `camera_full_stack_loss_hz` |
| 8 | The corrections are the method | therefore: predict, measure, correct | 6 flip cards | — | flip | A0 § gap, A3, B2, B4 | `interaction_accepted_ms`, `cpu_weight_default` (public), `weight_raised`, `weight_wait_per_cpu_s`, `weight_camera_hz`, `weight_others_wait_rise`, `camera_gpu_only_loss_hz`, `mps_no_concurrency_quote`, `kernel_time_sms_full_share`, `sm_issue_full_stack`, `vision_pred_bandwidth_form_ms`, `vision_compute_form_ms` |
| — | Your turn | sandbox | link cards | — | — | explorers 01–03, diagrams 01/02/04/06/07, notes, quiz, sibling kits | — |

The eighth correction in A0 (the withdrawn "within round-to-round spread" reading) is shown in scene 2 as a
dashed "corrected" box, because it is about the pool.

## Hedges kept from the public notes
- "expected, not tested, in the full stack" (B1: the dose curve comes from a camera-plus-detector row).
- "undecided at dose"; the post-hoc reading "is labelled post-hoc and does not replace the verdict" (B1 camera).
- "most (or less board traffic)"; "read it as about two thirds, not as a clean most"; "path not isolated" (A2).
- "about 90 %" (A5, my estimate from `interaction_accepted_ms`).
- "provisional" for the camera's cause (A0).
- "A code change in the engine was not tested; only the handler-level filter was" (A4).
- Kernel fill is "theoretical, from launch configurations" (B2).
- Split verdict for `cpu.weight` (A3).

## Not in `constants.json`, so drawn without a number
- The stand-in's fixed transcript delay after the commit: the head-of-line strip is schematic.
- The motor-control loop period: the bell has no number.
- The number of moved cluster-mates and the window-to-window spread of f: described in words.
- Slider ranges are UI bounds (0 → `history_items`; 0 → the highest dose point; `pool_wait_per_busy_camera_only` → 1.5 × `pool_wait_per_busy_full`), not claims.

## Where the metaphor breaks (footer)
The five "where it breaks" entries of the cast table.
