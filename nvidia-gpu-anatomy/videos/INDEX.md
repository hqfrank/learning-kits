# Videos — Anatomy of an NVIDIA GPU (Rung 4, learn-video)

Short explainer videos built from the notes, diagrams and `explorers/params.json`. Each video is a
discardable study aid: a storyboard, per-scene Manim sources, Kokoro narration timed to measured clip
lengths, assembled with ffmpeg into an MP4 plus an `.srt`. Every number shown is loaded from
`explorers/params.json` (which copies the metrics-kit constants with their source strings); each
scene that shows a number carries a small corner source tag naming the `params.json` key.

| File | Duration | Teaches | Sources |
|---|---|---|---|
| `01-what-is-an-sm/out/what-is-an-sm.mp4` | 3:26 (205.8 s) | From a thread to the chip: the CUDA software ladder (thread→warp→block→grid→kernel) mapped onto the hardware ladder (lane→SMSP→SM→GPU); inside one SM (4 sub-partitions, 1 inst/cycle each, 32 FP32 lanes + tensor core); a 512-thread block becoming 16 warps, 4 per sub-partition; occupancy (48 warp slots, 64K registers, 67% cap) and the twist that occupancy ≠ issue rate (same occupancy, 4.24× runtime); the memory ladder (registers→L1/shared→L2→DRAM) with Orin/Thor capacity, bandwidth and latency, Thor's 8× L2 at ~unchanged latency, the 4 MB/32 MB cliff; why a robot engineer cares. | `params.json`: `sm_count`, `smsp_per_sm`, `dispatch_bound_per_smsp`, `fp32_cores_per_sm`, `max_warps_per_sm`, `registers_per_sm`, `l1_shared_per_sm`, `l2_size`, `l2_dram_capacity_ratio`, `latency_l2`, `l2_dram_bandwidth_ratio`, `dram_bandwidth_read_measured` — all → metrics-kit Platforms Table 1 / A.6 / A.7. CUDA model facts: CUDA Programming Guide v13.4.2 §1.2 / §3.2.2. "Same occupancy, 4.24× runtime": `notes/03-occupancy-and-registers.md` (C-KIT-NOTES B3, Table B.3.1). warp=32: CUDA PG §1.2.2.2. |

## 01-what-is-an-sm — files
```
01-what-is-an-sm/
  storyboard.md              # scenes, durations, narration, on-screen elements, source per number
  scenes/
    theme.py                 # shared colours (software=blue, hardware=green, sched=orange,
                             #   tensor=purple, limit=red; Orin=blue, Thor=green) + helpers
    scene_00.py … scene_07.py  # one Scene class per storyboard scene (00 title, 07 sources card)
  audio/
    scene_01.wav … scene_06.wav  # Kokoro-82M narration (voice af_heart), 24 kHz mono
  out/
    what-is-an-sm.mp4        # 1280x720, 3:26
    what-is-an-sm.srt        # captions for the six narrated scenes, timed to measured clip lengths
  assemble.sh               # ffmpeg: mux scenes 01–06 with narration, bookend with 00/07, concat
  media/                    # Manim render cache (regenerable; not a deliverable)
  work/                     # ffmpeg intermediates (regenerable; not a deliverable)
```

## How it was built (reproduce)
1. Narration: `~/.local/share/learn-kit/venv/bin/python ~/.local/share/learn-kit/tts.py "<text>" audio/scene_NN.wav` (voice `af_heart`). Prints the clip duration; scene lengths were set to clip + ≥ 0.5 s.
2. Animation: `~/.local/share/learn-kit/venv/bin/manim -qm scenes/scene_NN.py SceneNN`. Scene 01 was rendered first to validate the toolchain, then the rest.
3. Timing: measured each clip with `ffprobe`; each scene's hold fills to clip + 0.5 s via a `self.wait(...)` keyed off `self.renderer.time`.
4. Assembly: `bash assemble.sh` — scenes 01–06 muxed with their narration (audio `apad`-ded to video length), title (00) and sources (07) cards get a silent track, all concatenated.
5. Review: 4 frames extracted with `ffmpeg -ss` and read back for legibility, label overlap and number-vs-`params.json` agreement; two overlaps found and fixed (scene 03 detail labels under landing warps → faded out before the warps land; scene 04 "same occupancy" over the title → moved below the title with margin; scene 07 sources card collapsed by empty-string `Text("")` lines → rebuilt without blank lines).

## Verification notes
- Numbers on screen match `params.json`: SM 16/20 (`sm_count`), SMSP 4 (`smsp_per_sm`), dispatch 1/cyc (`dispatch_bound_per_smsp`), FP32 128 (`fp32_cores_per_sm`), 48 warp slots (`max_warps_per_sm`), 65536 registers (`registers_per_sm`), L1 164→228 KB (`l1_shared_per_sm`), L2 4→32 MB & ×8 (`l2_size`, `l2_dram_capacity_ratio`), L2 latency 146→156 ns (`latency_l2`), L2:DRAM 12.4×/14.6× (`l2_dram_bandwidth_ratio`), DRAM 177→259 GB/s (`dram_bandwidth_read_measured`).
- The 67% occupancy and 4.24× runtime figures are from `notes/03` (C-KIT-NOTES B3), not `params.json`; they are tagged `note 03 / B3` on screen.
- warp = 32 threads is architecture-fixed (CUDA PG §1.2.2.2), not a `params.json` key, and is tagged as such.
