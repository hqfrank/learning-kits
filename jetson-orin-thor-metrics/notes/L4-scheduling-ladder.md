# L4 scheduling ladder: shared context → separate process → MPS → MPS + SM cap → MIG (deferred)

**Source:** `JetsonProfiling/robot-kernels/L4-realmodel-cotenancy/KEY-LEARNINGS.md` (branch `dev`), the committed summary of the L4 real-model co-tenancy campaign on one Thor GPU  ·  **Status in source:** working synthesis; the book's §C.2 and later sections are being written from this data. Not a book section.

## In one sentence
On one Thor GPU, the GPU-sharing discipline — not compute — decides whether a 100 Hz control loop holds: a shared context lets one π0.5 VLA blow the loop's p99 from 1.74 to 110.7 ms (64×) with 51% of ticks dropped; a separate process cuts that to ≈ 4.9% dropped (p99 17 ms); plain MPS does not help; MPS with the VLA capped to 25–35% of the SMs returns the loop to 0% dropped under the 10 ms deadline; and no discipline moves the ≈ 172 GB/s CPU-memory-load floor at which everything collapses.

## What it measures
The WBC control loop's p99 latency and dropped-tick fraction, and each co-tenant's achieved rate, as the sharing discipline is stepped up a ladder: (1) shared context (in-process Triton, every tenant on its own CUDA stream in one context); (2) separate context (the VLA in its own process, GPU time-slicing, no MPS); (3a) plain MPS (own context under Multi-Process Service, no limits); (3b) MPS + SM reservation (`CUDA_MPS_ACTIVE_THREAD_PERCENTAGE` cap on the VLA client); (4) MIG, deferred. Roster: 9 perception nets (yolo11m-det ×2, yolov8m-seg ×2, seg-scene, rf-detr ×2, yolov8m-pose, deeplab) + 3 WBC sessions at 100 Hz each (10 ms deadline) + one VLA (π0.5 or GR00T-N1.7). Thor, MAXN, 1575 MHz devfreq-locked (source: header and "MPS ③").

## How
Caveats first, as the source gives them: Thor only, benchmark path (no ROS2/DDS transport); fp16 perception = TensorRT engines while fp32/TF32 = ORT-CUDA, so the fp16 win mixes precision with TensorRT fusion; int8 engines are uncalibrated (latency and bytes only); the π0.5-shared vs GR00T-separate comparison mixes model × topology until the matched-topology run resolves it; the VLA-loaded co-tenancy sweep was "in flight" at the time of writing (source: "Scope / caveats").

The campaign first ran the perception + WBC roster without a VLA (STEP 1), then the two VLAs solo, then the VLA loaded co-tenancy at each rung. A CPU memory-bandwidth hog is swept as a second axis at several rungs.

## Predicted
The source frames priors rather than formal predictions: that fp16 would help because it moves fewer bytes (confirmed); that int8 would extend the fp16 headroom further by halving bytes again (refuted — see below); and a "Phase-2 prior" that plain MPS ≈ shared context for fair-share (confirmed).

## Measured
All numbers from KEY-LEARNINGS.md; the source gives many as approximations and the note keeps its marks.

**Rung 1 — shared context (perception + WBC, no VLA).** WBC is ≈ 99.9% queue wait (execute 0.03–0.1 ms); its latency is bimodal (slip ≈ 0.2 ms vs backlog ≈ 30–45 ms). The blockers are memory-bound perception glue (conv/gemm 35% > elementwise 30% > layout 17% of wait at fp32; the `nchwToNhwc` layout kernel at 0.17% L2 hit is the single dominant one). Perception rides the DRAM roof at ≈ 69% of bandwidth (AI 27–46); WBC is a launch-bound speck at AI 0.4. **fp16 holds WBC**: p99 ≤ 6.6 ms at full 100 Hz across 3–30 Hz perception, crossover pushed from ≈ 9 Hz to > 30 Hz, because fp16 moves 5–6× fewer DRAM bytes (2× precision × TensorRT fusion, 515 → 164 kernels/inference). TF32 = true-fp32 (same bytes, same starvation). Under a CPU hog, fp16 WBC holds to ≈ 158 GB/s, degrades from ≈ 172 (8.8% ticks dropped), collapses by 186 GB/s. **int8 breaks at ≈ 172 GB/s too** — identical to fp16 — and its solo p99 is worse (4.4 ms vs 0.99). Mechanism: int8 halves weights (engine ≈ 0.5× fp16) but DRAM traffic is dominated by activations and quant/dequant round trips, which do not halve; for rf-detr int8 moves 1.61× fp16 bytes.

**VLA solo (Thor, no co-tenants).** π0.5: 4344 GFLOP/inference at AI 176; GR00T-N1.7: 1016 GFLOP at AI 43; both far left of the ≈ 786 FLOP/byte bf16 tensor ridge. Delivered ≈ 35 TFLOP/s (π0.5, 84–85% of its bandwidth-roof cap) and ≈ 12 TFLOP/s (GR00T). Both move ≈ 24 GB/inference; GR00T is ≈ 1.5× faster (82 vs 124 ms) because its six discrete engines sustain ≈ 286 vs ≈ 206 GB/s. GR00T's DiT ×4 diffusion = 41% of its 23.6 GB. fp16 ≈ bf16. π0.5 misses 10 Hz solo (8 Hz); GR00T just meets it (12 Hz).

**Rung 1 with VLA — shared context (π0.5).** WBC p99 1.74 → 110.7 ms (64×), drop 0 → 51%, at 12 Hz perception, no CPU hog. π0.5 runs at 5 Hz, ≈ 152 ms/inference, ≈ 131 ms of GPU kernels per 200 ms period (≈ 66% duty); GPU occupancy ρ 0.39 → 0.98. A co-tenant inference overlapping a π0.5 inference runs ≈ 7–11× slower than one in a π0.5-idle gap (WBC p99 11.5 → 112 ms). With a VLA present there is no CPU-bandwidth break point — WBC is already broken at 0 GB/s.

**Rung 2 — separate context (own process, time-slice, no MPS).** GR00T: WBC p99 1.72 → 14.3 ms (≈ 8.3×), 98% throughput held; GR00T itself falls 10 → 5.3 Hz across perception load and 8.7 → 1.0 Hz under the CPU hog (p99 99 → 254 ms). CPU-bandwidth break point restored at ≈ 120–150 GB/s. Matched-topology π0.5 in a separate context: 4.9% dropped, p99 17 ms — so the shared-context 64× was ≈ 90% topology, not the model.

**Rung 3a — plain MPS.** π0.5: drop 51% → 25%, p99 110 → 61 ms, still far over budget. GR00T: slightly worse than rung 2 (8.5% vs 1.8% dropped). Plain MPS oversubscribes in the aggressor's favour.

**Rung 3b — MPS + SM reservation.** Cap sweep {75, 50, 40, 35, 25}% on the VLA client, 12 Hz perception, no hog: cap-25 p99 ≈ 7.5 ms and cap-35 p99 9.1 ms (π0.5) / 8.9 ms (GR00T) both hold WBC at 0% drop under 10 ms; cap-40 misses (GR00T p99 13 ms; π0.5 spin-livelocks on CPU-side engine setup at caps 40 and 75 — not a GPU effect; caps 25, 35, 50 run). Cost to the VLA: cap-35 π0.5 5 → 4.5 Hz, GR00T 10 → 8.7 Hz (≈ 0.87–0.90 retained); cap-25 → 3.6 / 7.1 Hz (≈ 0.72). Under a CPU hog both caps meet 10 ms only at 0 GB/s and both collapse at ≈ 172 GB/s; in the 37–158 GB/s band cap-25 degrades gracefully while cap-35 gives up ≈ 2× the drop/p99.

**Rung 4 — MIG.** Deferred (JetPack bug); MPS + reservation is the achievable isolation this revision.

## The gap, and what it means
The source's own synthesis:

- **The binding constraint is sharing discipline, not compute.** Every workload sits 2–3 orders of magnitude below the advertised tensor numbers (NVFP4 ≈ 2070 TOP/s, int8 324, fp16 192 TFLOP/s). TOPS predicts nothing here; co-tenancy is governed by queue/scheduling discipline, DRAM bandwidth and the shared controller, and kernel-launch granularity.
- **Precision is a QoS lever because it is a bytes lever — but only down to fp16.** Below fp16 the contended ceiling is not byte-set; it is a fixed per-kernel launch / controller-transaction floor at ≈ 172 GB/s. "Precision past fp16 is spent."
- **The GPU is a fixed pie; the discipline decides which tenant absorbs the deficit.** Shared context: the real-time loop pays. Separate context: the VLA pays (its rate halves) and the loop's throughput holds but its tail (14.3 ms) still misses. MPS + cap: the loop meets its deadline and the VLA's rate is capped by construction. QoS does not add capacity; it assigns the penalty.
- **Context isolation is the dominant lever; the reservation is the finisher** (closes the last ≈ 10×, from 4.9% dropped to 0%).
- **Recommendation is deployment-dependent:** cap-25 for robots with CPU DRAM load (robust); cap-35 for GPU-dominant deployments (more VLA rate). Neither beats the ≈ 172 GB/s floor.

Open in the source: the CPU-load axis for the loaded VLA rungs beyond the cap sweep, the Orin cross-board leg, MIG, calibrated int8, and the ROS2 transport.

## So what
Interpretation (mine): this is the operational conclusion of the whole book. Docs A and B measure why — SM co-scheduling lockout at ≈ 14% occupancy (§B.4), the controller cliff at about half the CPU's ceiling (§B.5), the compute-starves-memory asymmetry (§B.6), the bandwidth-bound VLA (§C.1). The L4 ladder turns those into a deployable setting: put the VLA in its own MPS client, cap it at 25–35% of the SMs, run perception at fp16, and keep CPU DRAM traffic well under 172 GB/s.

## Terms introduced
- **sharing discipline** — how tenants are placed on the GPU: shared context, separate process (time-slice), MPS, MPS + SM cap, or MIG.
- **shared context** — all tenants in one CUDA context (here in-process Triton), each on its own stream; streams do not isolate them.
- **separate context** — the VLA in its own process; the GPU time-slices between contexts.
- **SM reservation / cap** — `CUDA_MPS_ACTIVE_THREAD_PERCENTAGE`, limiting an MPS client to a fraction of the SMs.
- **dropped ticks** — the fraction of the control loop's 100 Hz ticks that do not complete in time.
- **saturation tax** — the slowdown a co-tenant pays when its inference overlaps a VLA inference that holds the GPU at ≈ 98% occupancy; ≈ 7–11× here.
- **172 GB/s floor** — the CPU memory-bandwidth load at which WBC collapses regardless of precision (fp16, int8) or MPS cap; ≈ 70% of the 245 GB/s sustained roof.
- **GR00T-N1.7** — NVIDIA Isaac's dual-system VLA (System-2 VLM backbone + System-1 diffusion action head), bf16, six discrete engines.
- **Triton (inference server)** — the serving framework hosting the roster in one process in the shared-context rung.
- **spin-livelock** — a CPU-side busy-wait that never completes; the cause of π0.5's hang at caps 40 and 75.
- **DiT** — diffusion transformer, GR00T's action head; four denoising steps re-stream its weights.
