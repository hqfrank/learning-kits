# Sources — Anatomy of an NVIDIA GPU

This primer explains the CUDA execution model and the GPU memory hierarchy for an engineer
reading `../jetson-orin-thor-metrics/notes/00-platforms.md` who does not yet know the terms.
It is a concept primer, not an experiment report. Every number is anchored to one of the
sources below. Anything the sources do not state is marked **(my explanation)** in the notes.

## Source A — NVIDIA CUDA Programming Guide (public)

The official programming-model and hardware-implementation text. Read 2026-10-02 with
`web_fetch`. The guide was reorganised in 2026; the version read is **v13.4.2** and the base
URL is `https://docs.nvidia.com/cuda/cuda-programming-guide/` (note: not `cuda-c-...`).

- **A-PM** — "1.2. Programming Model"
  `https://docs.nvidia.com/cuda/cuda-programming-guide/01-introduction/programming-model.html`
  Sections used: 1.2.1 Heterogeneous Systems; 1.2.2 GPU Hardware Model (SMs, GPCs, unified data
  cache, thread blocks and grids, how blocks are assigned to SMs); 1.2.2.2 Warps and SIMT
  (warp = 32 threads, lanes 0–31, divergence); 1.2.3 GPU Memory (global memory, on-chip
  register file and shared memory, L1/L2 caches, unified memory).
- **A-HW** — "3.2. Advanced Kernel Programming → 3.2.2 Hardware Implementation"
  `https://docs.nvidia.com/cuda/cuda-programming-guide/03-advanced/advanced-kernel-programming.html`
  Sections used: 3.2.2.1 SIMT Execution Model (warps created/managed/scheduled in groups of 32,
  in-order issue, no branch prediction or speculation, half-/quarter-warp); 3.2.1 Using PTX
  (PTX is the virtual ISA, below it SASS); independent thread scheduling (CC ≥ 7.0).

## Source B — Architecture notes (public, for SM internals and tensor-core generations)

Used for facts the programming guide states only generically (sub-partition layout, FP32/INT32
datapaths, tensor-core generations, tcgen05, MPS/MIG). Read 2026-10-02 with `web_search`/`web_fetch`.

- **B-AMPERE** — NVIDIA, "NVIDIA Ampere Architecture In-Depth" (developer blog, 2020-05-14).
  `https://developer.nvidia.com/blog/nvidia-ampere-architecture-in-depth/`
  Used for: Multi-Instance GPU (MIG) partitions one GPU into up to seven isolated instances
  with dedicated compute, cache and memory paths; third-generation tensor cores and their data
  types (TF32, BF16, FP64, INT8, INT4) and the 2× structured-sparsity feature. NOTE: this blog
  describes the datacenter GA100 (64 FP32 cores/SM). Orin is a GA10x-class part (sm_87) with
  **128** FP32 cores/SM — that number comes from the metrics kit Table 1 (Source C), not here.
- **B-FORUMS** — NVIDIA Developer Forums, SM sub-partition / warp-scheduler threads (2020–2024),
  e.g. "Mapping of pipelines to functional units" and "Instruction scheduling in Ampere".
  `https://forums.developer.nvidia.com/t/mapping-of-pipelines-to-functional-units/315200/2`
  `https://forums.developer.nvidia.com/t/instruction-scheduling-in-ampere/169072`
  Used for: Volta–Hopper/Ampere SM has 4 sub-partitions; each sub-partition has a warp scheduler,
  a register file, and dedicated pipelines (FP32, FP16, INT, SFU, Tensor); the scheduler issues
  1 instruction per cycle; GA10x adds FP32 on both datapaths (one datapath = 16 FP32 cores),
  doubling FP32 rate. These corroborate the metrics-kit Table 1 figures (4 SMSP, 128 FP32/SM,
  1 inst/cycle/SMSP).
- **B-BLACKWELL** — NVIDIA, Blackwell tensor-core / NVFP4 material:
  "Introducing NVFP4 for Efficient and Accurate Low-Precision Inference" (developer blog, 2026),
  `https://developer.nvidia.com/blog/introducing-nvfp4-for-efficient-and-accurate-low-precision-inference/`;
  NVIDIA CUTLASS docs, "tcgen05 MMA Programming Guide" and "Blackwell SM100 GEMMs",
  `https://docs.nvidia.com/cutlass/latest/media/docs/pythonDSL/guides/mma/tcgen05_programming.html`.
  Used for: fifth-generation Blackwell tensor cores; NVFP4 is a 4-bit format with micro-block
  (two-level) scaling; tcgen05 MMA stages operands in shared memory / tensor memory (TMEM) and
  accumulates in TMEM; tcgen05 supports legacy types plus 4/6/8-bit floating types with scale
  factors.

## Source C — Jetson Orin / Thor metrics kit (local, for every concrete number)

The sibling learning kit this primer is written for. Every board-specific number in this primer
is loaded from its machine-readable constants file and cited to the kit note that measured it.
Do not retype these numbers; load the JSON.

- **C-CONST** — `../jetson-orin-thor-metrics/constants.json`
  Machine-readable constants. Copied (not retyped) into this primer's own `constants.json`,
  keeping each value's original `source` string. Only the subset this primer cites is copied.
- **C-PLAT** — `../jetson-orin-thor-metrics/notes/00-platforms.md` (Table 1)
  Device-queried facts for Orin AGX (sm_87, Ampere) and Thor T5000 (sm_110, Blackwell): SM count,
  clock, sub-partitions, FP32 cores/SM, warps/threads/blocks per SM, registers per SM, tensor-core
  generation and precisions, L1+shared per SM, L2 size, DRAM spec, MIG status.
- **C-KIT-NOTES** — the kit notes cited for measured behaviour:
  - `A2-cuda-core-ceilings.md` — CUDA-core FP32/FP16/INT8 roofs; Thor has no double-rate FP16.
  - `A3-tensor-core-ceilings.md` — classic `mma` vs tcgen05 vs datasheet; two tensor roofs on Thor.
  - `A4-nvfp4-ceiling.md` — NVFP4 dense/sparse ceilings; vehicle-dependent sparsity multiplier.
  - `A6-bandwidth-vs-footprint.md` — L2-resident vs DRAM bandwidth plateaus and the L2 cliff.
  - `A7-latency-landmarks.md` — L1/L2/DRAM dependent-load latency landmarks.
  - `B2-cache-interference.md` — eviction knee; latency-bound victims pay the L2:DRAM ratio.
  - `B3-matrix-profile-stall-decomposition.md` — occupancy does not predict issue rate.
  - `B4-gemm-victim-interference.md` — controller contention vs SM co-scheduling lockout.
  - `B7-aggregate-throughput.md` — streams vs MPS deliver one tenant's aggregate throughput.
  - `L4-scheduling-ladder.md` — shared context → separate process → MPS → MPS+SM cap → MIG.

## How the numbers were handled

- Board-specific numbers (SM count, clock, cache sizes, latencies, ceilings) are **loaded** from
  `constants.json` and cited to the kit note or table that measured them.
- Generic architecture facts (what a warp is, what a sub-partition contains, what tensor memory
  is) come from Source A or Source B and are cited inline.
- Where a figure is the author's reasoning rather than a quoted source value — for example a
  derived ratio, or a "why it matters for robotics" judgement — it is labelled **(my
  explanation)**. The metrics kit uses the same convention ("interpretation (mine)").

## Rung 3 — interactive explorers (learn-explorer, 2026-10-02)

Two single-file HTML explorers under `explorers/`, built from the notes and `constants.json` (no new
sources were consulted; every number is loaded from `explorers/params.json`, copied from
`constants.json` with its original `source` string, which traces to the metrics kit).

- `explorers/01-launch-to-hardware.html` — the CUDA launch→residency model (notes 01/02/03; CUDA
  Programming Guide §1.2.2/§3.2.2; Platforms Table 1). The register limit uses note 03's teaching
  form (regs/thread × threads/block), not warp-granularity allocation; this is stated on the page.
- `explorers/02-memory-ladder.html` — the registers→L1/shared→L2→DRAM capacity ladder and the L2
  cliff (notes 05/06; metrics-kit A.5 L1 plateau, A.6 bandwidth plateaus + L2:DRAM ratio, A.7 latency
  landmarks; Platforms Table 1).
- `explorers/params.json` — the cited subset of `constants.json` the two pages load.

Preloaded-case provenance (all from existing sources, none invented):
- A.1 512-thread probe, B.3 1024-thread kernel → notes 02/03.
- WBC weights ≈ 0.5 MB → metrics-kit roofline INDEX / B.8 (WBC INT8 MLP).
- π0.5 KV cache ≈ 13 MB → metrics-kit note C.1 ("~13 MB of KV at S≈712").
- GR00T-scale ≈ 27.5 MB → metrics-kit B.6 Table B.6.1 (W_RM = 8960×1536×2, the RM fp16 decode-GEMM
  weight footprint), used as a labelled GR00T-scale proxy because the sources give no single GR00T
  "weights footprint"; GR00T streams ≈24 GB/inference across six engines (L4). The label and this
  provenance are stated on the page and in `explorers/INDEX.md`.

Verification: both pages' `console.assert` self-tests reproduce source numbers (67% occupancy for 32
of 48 warps; 4 warps/SMSP for the 512-thread block; L2:DRAM 12.4×/14.6×); a node NaN sweep of every
slider/selector extreme (512 and 20 combinations) found 0 bad outputs; both render under headless
Chrome with the self-tests passing. See `explorers/INDEX.md` for the full specs.

## Rung 2 — Diagrams (learn-diagram)

Four diagrams in `diagrams/` (`.drawio` + `.svg` + `.png` each, plus a combined `nvidia-gpu-anatomy.drawio`),
built from the notes above. Each turns one idea into a picture and carries its own legend and sources
footnote so the exported image stands alone. Every board-specific number is loaded from `constants.json`
and tagged on the canvas; nothing is retyped as a free constant.

- `01-two-ladders` — software ladder (thread -> warp -> block -> grid -> kernel) mapped onto the hardware
  ladder (lane -> SMSP -> SM -> GPU), with the key mappings (warp->one SMSP, block->one SM, grid->all SMs).
  Sources: CUDA Prog. Guide 1.2.2 (A-PM); `constants.json` smsp_per_sm, sm_count, gpu_clock_maxn_locked [C-PLAT].
- `02-inside-an-sm` — one SM exploded into four SMSPs (warp scheduler + dispatch port + 32 FP32 lanes +
  INT/ALU + LD/ST+SFU + tensor core each), shared L1/shared and 64K register file, "1 inst/cycle/SMSP" bound.
  Sources: `constants.json` smsp_per_sm, dispatch_bound_per_smsp, fp32_cores_per_sm, tensor_cores_per_sm,
  registers_per_sm, max_warps_per_sm, max_threads_per_sm, l1_shared_per_sm, l1_read_datapath [C-PLAT];
  pipe inventory B-FORUMS; in-order SIMT issue A-HW 3.2.2.
- `03-memory-hierarchy` — registers -> L1/shared (per SM) -> L2 (device-wide) -> controller -> LPDDR, also
  fed by CPU cores and copy engines; per-level capacity/bandwidth/latency for both boards. Title finding:
  Thor grew L2 8x but L2 latency did not change. Sources: `constants.json` l1_shared_per_sm, l1_read_datapath,
  l2_size, l2_dram_capacity_ratio, registers_per_sm [C-PLAT]; l2_resident_read_bandwidth,
  dram_bandwidth_read_measured, l2_dram_bandwidth_ratio [C-KIT-NOTES A6]; latency_l1/l2/dram [C-KIT-NOTES A7];
  hierarchy + unified memory A-PM 1.2.3.
- `04-sharing-mechanisms` — isolation matrix (rows = SM slots / L2 / memory controller; columns = shared
  context+streams / separate processes / MPS / MPS+SM cap / MIG; cells = yes/partial/no with the citing note).
  Sources: `constants.json` lockout_onset_occupancy, controller_contention_peak, mps_cap_vla_rate_retained,
  cpu_memory_load_floor [C-KIT-NOTES B4, L4]; MIG none/tech-preview [C-PLAT]; mechanisms + "streams are not
  isolation" note 07-sharing-the-gpu (B7, L4); A-PM 1.2.2.1; MIG B-AMPERE.

See `diagrams/INDEX.md` for the full per-diagram specs-as-built and the export/rendering notes.

## Rung 4 — explainer video (learn-video, 2026-10-02)

One short video under `videos/01-what-is-an-sm/`, built from the notes (00–03, 05), `explorers/params.json`
and the diagrams (no new sources were consulted). Every number shown is loaded from `params.json` — the
cited subset of `constants.json`, which traces to the Jetson Orin/Thor metrics kit — and carries an
on-screen source tag naming the `params.json` key. CUDA execution-model facts are from Source A (CUDA
Programming Guide v13.4.2); SM-internals framing from the notes (Source A/B). The one figure not in
`params.json` — "same occupancy, 4.24× runtime" — is from `notes/03-occupancy-and-registers.md`
(C-KIT-NOTES B3, Table B.3.1) and is tagged `note 03 / B3` on screen.

- `videos/01-what-is-an-sm/out/what-is-an-sm.mp4` — "From a thread to the chip: how work lands on an
  NVIDIA GPU" (3:26, 1280×720). Arc: software ladder → hardware ladder + the chip (16/20 SMs behind one
  L2 and one controller) → inside one SM (4 sub-partitions, 1 inst/cycle, 32 FP32 lanes + tensor core;
  a 512-thread block → 16 warps → 4 per sub-partition) → occupancy (48 slots, 64K registers, 67% cap)
  and the twist that occupancy ≠ issue rate → the memory ladder (registers → L1/shared → L2 → DRAM with
  Orin/Thor numbers; Thor's L2 grew 8× at ~unchanged latency; the 4 MB/32 MB cliff) → why a robot
  engineer cares → sources card.
- `videos/01-what-is-an-sm/out/what-is-an-sm.srt` — captions for the six narrated scenes, timed to the
  measured Kokoro clip lengths.
- `videos/01-what-is-an-sm/storyboard.md` — scenes, durations, narration text, on-screen elements and
  the `params.json` key cited per number. `videos/INDEX.md` — the per-video spec-as-built and the
  reproduce/verify notes.

`params.json` keys shown on screen: `sm_count`, `smsp_per_sm`, `dispatch_bound_per_smsp`,
`fp32_cores_per_sm`, `max_warps_per_sm`, `registers_per_sm`, `l1_shared_per_sm`, `l2_size`,
`l2_dram_capacity_ratio`, `latency_l2`, `l2_dram_bandwidth_ratio`, `dram_bandwidth_read_measured`.

Toolchain: Kokoro-82M narration via `~/.local/share/learn-kit/tts.py` (voice `af_heart`); Manim
Community from the shared venv `~/.local/share/learn-kit/venv` (`Text`, not `MathTex` — LaTeX absent);
ffmpeg assembly. Scene 01 rendered first at `-qm` to validate the toolchain, then the rest. Review by
extracting 4 frames and reading them back; three label-overlap issues were found and fixed before the
final assembly (scene 03 detail-under-warps, scene 04 label-over-title, scene 07 empty-line collapse).
