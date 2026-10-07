# Storyboard — "From a thread to the chip: how work lands on an NVIDIA GPU"

Rung 4 (learn-video) of `learning/nvidia-gpu-anatomy`. A 3–5 minute concept primer for an engineer
meeting SM / warp / sub-partition / occupancy / L2 for the first time. Every number is loaded from
`explorers/params.json` (which copies the metrics-kit constants with their source strings); the
`params.json` key is cited on-screen as a small source tag and listed per scene below. One claim —
the "same occupancy, 4× runtime" twist — is not in `params.json`; it comes from note
`notes/03-occupancy-and-registers.md` (C-KIT-NOTES B3, Table B.3.1) and is tagged `note 03 / B3`.

Boards: **Orin** (Ampere, sm_87) and **Thor** (Blackwell, sm_110). Primary device shown for the
single-SM walk-through is **Orin** (16 SMs); Thor numbers appear where the source gives both.

## Visual grammar
- Background: near-black `#0d1117`. One accent colour per concept, held across scenes:
  - software/you-write = blue `#4F9DFF`
  - hardware/runs-it = green `#49C17A`
  - the scheduler / issue bound = orange `#F0A030`
  - tensor core = purple `#B080F0`
  - register / limit bite = red `#E5484D`
  - Orin = blue, Thor = green in the memory ladder (matches the diagrams)
- Build incrementally; transform one object into the next, never hard-cut between related states.
- ≤ 12 words of on-screen text at any moment. Narration carries sentences; screen carries structure.
- Every scene that shows a number carries a small corner source tag (the `params.json` key).
- Leave ≥ 0.4 screen-unit margin around bars/labels so nothing overprints (fix for the prior
  video's deadline-label-over-bars bug).
- Target narration pace ≈ 140 words/min. Scene animation length = measured clip length + ≥ 0.5 s.

## Accent / source legend card (shown once, end-adjacent sources card)
All constants: `explorers/params.json` → metrics-kit `constants.json` → Jetson Orin/Thor metrics kit
(Platforms Table 1; A.6; A.7). CUDA model facts: CUDA Programming Guide v13.4.2 §1.2 / §3.2.2.
"Same occupancy, 4× runtime": note 03 (C-KIT-NOTES B3).

---

## Scene 00 — Title card (≈ 4 s, no narration or 1 short line)
- On screen: title "From a thread to the chip" / subtitle "how work lands on an NVIDIA GPU".
- Small line: "a concept primer — Orin & Thor". Dark bg, blue+green accent underline.
- Narration: *(none; 1 s hold built into assembly as a title card)*

## Scene 01 — You write a kernel: the software ladder (target ≈ 35 s)
- Narration: "You program a GPU by writing a kernel — one function, run by thousands of threads.
  Launching it creates a grid of blocks, and each block is a group of threads. Thirty-two of those
  threads are bundled by the hardware into a warp — the unit it actually schedules. So the software
  ladder you write runs from a single thread, up through a warp of thirty-two, to a block, to the
  whole grid."
- On screen (build bottom-up, blue): `thread` → `warp = 32 threads` → `block` → `grid` → `kernel`.
  Each rung fades in as named. ≤ 3 words per rung label.
- Source tag: warp size 32 — CUDA PG §1.2.2.2 (not a params key; architecture-fixed).
- Validation scene (render this one first at -qm).

## Scene 02 — The hardware ladder beside it: the chip (target ≈ 38 s)
- Narration: "Beside that software ladder sits the hardware that runs it. A thread occupies one lane.
  A warp is issued by one sub-partition. A block lands whole on one streaming multiprocessor — an
  SM. And the grid spreads across every SM on the chip. On Orin that is sixteen SMs; on Thor,
  twenty — all sitting behind one shared L2 cache and one memory controller to DRAM. That shared L2
  is where, later, everything will contend."
- On screen: hardware ladder (green) builds beside the blue one: `lane` → `sub-partition` → `SM`
  → `GPU`. Mapping arrows (red) connect warp→sub-partition, block→SM, grid→GPU. Then a chip block
  appears: a grid of SM squares (16, labelled "Orin 16 SMs / Thor 20") over a wide `L2` bar over a
  `memory controller → DRAM` bar.
- Source tags: `sm_count` (16/20); `smsp_per_sm` (4).

## Scene 03 — Zoom into one SM: four sub-partitions (target ≈ 48 s)
- Narration: "Zoom into one SM. It is not one core — it is four sub-partitions. Each has a warp
  scheduler and a single dispatch port, so each issues at most one instruction per cycle. Behind
  that port sit thirty-two FP32 lanes — the CUDA cores — plus an integer pipe, load-store, and one
  tensor core, the matrix unit. Four sub-partitions, four instructions per cycle: that is the issue
  ceiling. Now watch work land. A block of five hundred twelve threads is sixteen warps; the
  hardware spreads them four warps to each sub-partition."
- On screen: one SM box expands into 4 sub-partition columns (orange header "1 inst/cycle" on each).
  Inside one column, build: `32 FP32 lanes` (blue), `INT`, `LD/ST`, `tensor core` (purple). Callout
  (orange): `4 × 1 = 4 inst/cycle`. Then animate: a blue `512-thread block` splits into `16 warps`,
  which fly into the 4 columns, `4 warps` settling per column. Keep margins; warp chips stack with
  gaps.
- Source tags: `smsp_per_sm` (4); `dispatch_bound_per_smsp` (1); `fp32_cores_per_sm` (128).

## Scene 04 — Occupancy, and the twist (target ≈ 50 s)
- Narration: "How many warps can one SM hold? Forty-eight slots, backed by a sixty-four-thousand
  register file. Fill them and occupancy is high — but there is a catch. Registers are shared across
  every thread resident. At sixty-four registers per thread, only thirty-two warps fit: occupancy
  caps at sixty-seven percent, and the register file, not the slots, is what bit. And here is the
  twist that trips people up. Occupancy is not issue rate. The metrics kit ran three kernels at the
  same occupancy; their runtimes differed by more than four times. More resident warps gives the
  scheduler more to choose from — it does not force an instruction out every cycle."
- On screen: a 48-slot grid (6×8). Warps fill it (green) up to a point; at the register limit a red
  line stops filling at 32 (label "32 / 48 = 67%", `registers_per_sm` tag). Then two bars side by
  side, same height labelled "same occupancy", but one 1× and one `4.24×` runtime (red) — predicted
  equal, measured very different. Source tag on the twist: `note 03 / B3`.
- Numbers: `max_warps_per_sm` (48); `registers_per_sm` (65536); 67% from note 03; 4.24× from note 03/B3.

## Scene 05 — The memory ladder (target ≈ 52 s)
- Narration: "Finally, where a kernel's data lives decides its speed. The memory ladder descends from
  registers, to per-SM L1 and shared memory, to the one shared L2, to DRAM. Watch the numbers animate
  in for Orin and Thor. L1 is tens of kilobytes at about twenty-five nanoseconds. L2 on Orin is four
  megabytes; on Thor it grew eight times, to thirty-two — yet its latency barely moved, around a
  hundred fifty nanoseconds. More data stays resident; it is not reached faster. And L2-resident
  streaming runs over twelve times the bandwidth of DRAM. That gap is the cliff: a working set that
  fits L2 flies; one that spills to DRAM crawls."
- On screen: vertical ladder, two columns (Orin blue, Thor green). Rows animate value from Orin→Thor:
  `L1 164→228 KB`, `L2 4→32 MB` (big "×8" badge), latency `L2 146→156 ns` (badge "~same"),
  bandwidth `L2 ÷ DRAM = 12.4× / 14.6×`. The 4 MB vs 32 MB "cliff" shown as a step. Keep each row's
  value label clear of the bar with margin.
- Source tags: `l1_shared_per_sm`; `l2_size`; `l2_dram_capacity_ratio` (8×); `latency_l2`
  (146/156 ns); `l2_dram_bandwidth_ratio` (12.4/14.6×).

## Scene 06 — Why a robot engineer cares (target ≈ 32 s)
- Narration: "So, two things to carry away for robotics. A tiny control kernel — one small block —
  cannot fill the schedulers; those four dispatch ports sit mostly idle, and the loop is bound by
  latency, not by cores. And a big model lives or dies by whether its working set fits L2: under
  thirty-two megabytes on Thor it stays resident; over it, every access pays the DRAM tax. Occupancy
  and TOPS do not tell you this — the memory ladder does."
- On screen: left, a nearly-empty SM (one small block, 3 of 4 ports greyed "idle"); right, two model
  blobs against a `32 MB` L2 line — one under (green "resident"), one over (red "spills to DRAM").
  ≤ 12 words of text total; narration carries it.
- Source tag: `l2_size` (Thor 32 MB).

## Scene 07 — Sources card (≈ 6 s, no narration)
- On screen: "Sources" + the legend: params.json → metrics-kit constants.json → Jetson Orin/Thor
  metrics kit (Platforms Table 1; A.6; A.7). CUDA model: CUDA Programming Guide v13.4.2 §1.2/§3.2.2.
  "Same occupancy, 4× runtime": note 03 (B3). Built as a static card in assembly.

---

## Per-scene source map (params.json keys)
| Scene | Keys / sources |
|---|---|
| 01 | warp=32 (CUDA PG §1.2.2.2) |
| 02 | `sm_count`, `smsp_per_sm` |
| 03 | `smsp_per_sm`, `dispatch_bound_per_smsp`, `fp32_cores_per_sm` |
| 04 | `max_warps_per_sm`, `registers_per_sm`; 67% & 4.24× from note 03 (B3) |
| 05 | `l1_shared_per_sm`, `l2_size`, `l2_dram_capacity_ratio`, `latency_l2`, `l2_dram_bandwidth_ratio` |
| 06 | `l2_size` |

## Render / assemble plan
- Narration: `~/.local/share/learn-kit/venv/bin/python ~/.local/share/learn-kit/tts.py "<text>" audio/scene_NN.wav` (voice af_heart).
- Animate: `~/.local/share/learn-kit/venv/bin/manim -qm scenes/scene_NN.py SceneNN`. Scene 01 first to validate, then the rest.
- Time each scene to its measured clip (ffprobe); scene length ≥ clip + 0.5 s.
- Assemble: ffmpeg — 1 s title card (scene 00), scenes 01–06 muxed with narration, ~6 s sources card (scene 07) → `out/what-is-an-sm.mp4`; generate `out/what-is-an-sm.srt` from narration + measured durations.
- Review: extract 4 frames, read back for legibility / no overlap / numbers match params.json.
