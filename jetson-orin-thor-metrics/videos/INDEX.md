# Videos — Jetson Orin (sm_87) vs Thor (sm_110), Rung 4 (learn-video)

Short explainer videos built from the notes, `constants.json` and `explorers/params.json`. Every
number shown on screen is loaded from `explorers/params.json` (the key is cited in each scene's
source tag on the canvas and in the storyboard). Nothing is retyped from prose. Narration is
Kokoro-82M (`af_heart`); animation is Manim Community from the shared venv; scenes are timed to the
measured narration clip lengths; captions (`.srt`) are generated from the storyboard text and the
measured clip durations.

| File | Duration | Teaches | Sources (params keys / notes) |
|---|---|---|---|
| `01-single-lane-bridge/out/single-lane-bridge.mp4` | 3 min 29 s (209 s) | Why a robot's 100 Hz control loop starves on a GPU shared with perception + a VLA: the datasheet TOPS looks ample, but SM co-scheduling is bistable (lockout at ~8% Orin / ~14% Thor occupancy), the real-shape WBC p99 inflates 141× (41.6 µs → 5.9 ms) under the full mix, a QoS ladder (separate process → MPS + 25% SM cap) recovers the loop at the cost of VLA Hz (5 → 3.6), and every discipline collapses at the ~172 GB/s shared-controller floor — scheduling cannot fix a memory problem. | A.3/A.4 (`nvfp4_dense_ceiling`, `tensor_tcgen05_fp16`); B.4 (`lockout_onset_occupancy`); B.8 (`wbc_solo_p99`, `wbc_worst_mix_p99`, `wbc_deadline`); L4 (`shared_context_wbc_p99`, `separate_context_wbc_p99`, `plain_mps_wbc_p99`, `mps_cap_wbc_p99`, `mps_cap_vla_rate_retained`, `cpu_memory_load_floor`, `dram_bandwidth_sustained_M`) |

## 01-single-lane-bridge — layout

```
01-single-lane-bridge/
  storyboard.md                 # scenes, durations, narration, on-screen elements, source per number
  scenes/
    theme.py                    # shared colours + constants loaded from ../../explorers/params.json
    scene_00_cards.py           # TitleCard + SourcesCard
    scene_01.py .. scene_06.py  # one Scene class per storyboard scene
    media/                      # Manim render output (720p30)
  audio/
    scene_01.wav .. scene_06.wav  # Kokoro narration, 24 kHz mono
  build_srt.py                  # builds the .srt from narration text + measured durations
  out/
    single-lane-bridge.mp4      # final cut (title → scenes 01–06 → sources card)
    single-lane-bridge.srt      # captions, timed to the narration clips
    parts/                      # per-scene muxed segments + concat list
```

### Scene arc (narration clip lengths)
1. **Three jobs, one GPU** (24.8 s) — control + perception + VLA funnel through one GPU → one memory controller → one LPDDR pool.
2. **The datasheet says there's room** (32.0 s) — NVFP4 1035→627.8 (60.7%), INT8/FP8 517→~two-thirds, tcgen05 FP16 258→192.5 (75%); the control loop needs almost none of it.
3. **The cliff: SM co-scheduling lockout** (37.9 s) — bistable; victim locked out above ~14% (Thor) / ~8% (Orin) warp-slot occupancy; the "fair share" line crossed out.
4. **The real rehearsal** (32.2 s) — WBC solo p99 41.6 µs → 5.9 ms (141×) under the full roster + CPU hog, under the 10 ms deadline but most of the budget gone.
5. **The ladder** (39.2 s) — shared ctx 110.7 ms/51% → separate process ~17 ms/4.9% (~90% back) → plain MPS 61 ms → MPS + 25% SM cap 7.5 ms/0% (the fix); VLA 5 → 3.6 Hz.
6. **The wall** (31.4 s) — every discipline collapses at ~172 GB/s CPU memory load (70% of the 245 GB/s roof); scheduling cannot fix a memory problem.
7. **Sources card** — all numbers from book.pdf (Docs A, B) + L4 KEY-LEARNINGS via params.json.

### How it was produced
- Narration: `~/.local/share/learn-kit/venv/bin/python ~/.local/share/learn-kit/tts.py "<text>" audio/scene_NN.wav --voice af_heart` (Kokoro-82M, CPU). One-time setup: the spaCy model `en_core_web_sm` had to be installed into the shared venv (`uv pip install --python …`) or misaki's g2p step fails trying to auto-download via uv.
- Animation: `~/.local/share/learn-kit/venv/bin/manim -qm scenes/scene_NN.py SceneNN` (720p30). `Text` is used throughout, not `MathTex` (no LaTeX on the machine); `Axes` number labels are drawn as `Text` to avoid the LaTeX dependency.
- Timing: each Manim scene's run time ≥ its narration clip + 0.5 s (clips measured with `ffprobe`); audio is never stretched.
- Assembly: each scene video muxed with its narration (`apad` + `-shortest`); concatenated with a 1 s title card and a sources card; `.srt` built by `build_srt.py` from the narration text and the per-part durations.
- Review: 4 frames extracted and read back for legibility and number-match; two overlap/clip issues (scene 02 row labels, scene 06 text + floor label) found and fixed before the final cut.
