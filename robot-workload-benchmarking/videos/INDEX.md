# Videos — Benchmarking a robot's on-board compute workload (Rung 4, learn-video)

The explainer-video layer of the kit. Each video turns the notes, diagrams, and explorers into a
short narrated animation. Numbers shown on screen come only from this kit's `constants.json` /
`explorers/params.json` and are tagged **illustrative** where their class is `illustrative`; public
values carry their source. No measured robot or campaign number appears.

**Public-safety:** generic subjects only ("a home robot", "the harness machine", "the control
loop"). No codename, company, person, host, internal path/URL, commit, issue, or campaign number.
A case-insensitive `grep -rniE` scan of the forbidden-term alternation was run over every file
written in this rung — **0 hits**.

**Toolchain:** narration by the Kokoro helper (`~/.local/share/learn-kit/tts.py`, voice `af_heart`);
animation by Manim Community 0.21 from the shared venv (`~/.local/share/learn-kit/venv`); `Text`
(Unicode) throughout, not `MathTex` (no LaTeX installed); assembly with `ffmpeg`. `ffmpeg`'s
`drawtext` filter was unavailable in this environment (no libfreetype build), so the title card is a
Manim scene (`scene_00.py`) rather than a `drawtext` overlay.

| File | Duration | Teaches | Sources |
|---|---|---|---|
| `01-measuring-a-robot-stack/out/measuring-a-robot-stack.mp4` | ~3m16s | How to benchmark a home robot's whole on-board stack without fooling yourself: the stack as concurrent pipelines; the two questions (does it fit / what runs out first); predict-then-measure with the budget ledger and why small models are launch-bound; three solo levels (L1/L2/L3), idle floor vs driven cost; the two-machine harness with fakes and stubs; how the bench can lie; windows, gates and pre-registration; combine and attribute the first limit (often CPU before GPU). | Notes A0, B0, B2, C1–C7; diagrams `01`,`03`,`04`,`06`; `explorers/params.json` / `constants.json` (rates, warm-up/window, foreign-CPU gate, nsys perturbation — all illustrative); public docs (Linux cgroups/CFS, ROS 2, SNTP RFC 4330, NVIDIA Nsight) |

## Per-video assets

### 01-measuring-a-robot-stack/
```
storyboard.md                         # scenes, durations, narration, on-screen elements, per-number source
narration.txt                         # narration text per scene (pipe-delimited)
scenes/common.py                      # shared palette + helpers (one accent colour per concept)
scenes/scene_00.py .. scene_09.py     # one Scene per storyboard scene (00 title, 09 sources, both silent)
audio/scene_01.wav .. scene_08.wav    # Kokoro narration clips (24 kHz mono)
assemble.sh                           # mux each scene with its narration, concat with title + sources cards
make_srt.py                           # build captions from measured segment durations
out/measuring-a-robot-stack.mp4       # final 720p30 video
out/measuring-a-robot-stack-captions.srt  # 48-cue captions
```

Measured narration clip lengths (s): 01 19.43 · 02 17.35 · 03 24.90 · 04 26.20 · 05 20.75 ·
06 23.93 · 07 24.52 · 08 24.95. Each scene's video is held to clip length + ~0.6 s via
`self.wait(max(0.5, CLIP + 0.6 - self.renderer.time))`, and the narration audio is `apad`-padded so
`-shortest` trims to the (longer) video — no audio is stretched or cut.

To regenerate: render each scene (`manim -qm scenes/scene_NN.py SceneNN`), then
`bash assemble.sh`, then `python3 make_srt.py`.
