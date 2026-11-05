# learn-video — how to produce a short explainer video (3Blue1Brown style)

## Scope and honesty

A 3–6 minute video on one mechanism or one chapter. Longer than that and the storyboard is doing two things. The output is a study aid; it will have rough edges. Say so in the video description rather than hiding them.

## Pipeline

1. **Storyboard first** (`videos/<nn>-<slug>/storyboard.md`). Scenes with: duration target, on-screen elements, the narration sentences, the source for every number shown. Total narration ≈ 130–150 words per minute. Show the storyboard to the user before rendering anything.
2. **Narration audio.** A shared toolchain is already installed at `~/.local/share/learn-kit/venv` (Python 3.12, Manim Community 0.21, Kokoro-82M TTS, soundfile, torch). Options, in order of preference:
   - **Default: Kokoro via the helper** `~/.local/share/learn-kit/venv/bin/python ~/.local/share/learn-kit/tts.py "<text>" audio/scene_<nn>.wav [--voice af_heart|am_adam|bf_emma|bm_george] [--speed 1.0]`. Prints the clip duration in seconds. First run downloads the model to `~/.cache/huggingface` (~330 MB). 24 kHz mono WAV.
   - Fallback if Kokoro fails: macOS `say -v Samantha -o scene.aiff --data-format=LEF32@22050 "<text>"`, then `ffmpeg -i scene.aiff scene.wav`.
   - A paid API (ElevenLabs etc.) only if the user supplies a key; read it from an environment variable, never from a file you create, never echo it.
3. **Animation with Manim Community** using the shared venv: `~/.local/share/learn-kit/venv/bin/manim -qm scenes/scene_<nn>.py <SceneClass>`. Do not create a per-topic venv unless the shared one is missing or the user asks for isolation. One `Scene` class per storyboard scene in `scenes/scene_<nn>.py`. Render at `-qm` (720p) first for review, `-qh` for the final cut. LaTeX is not installed: use `Text` (Unicode math) rather than `MathTex`, or ask before installing TeX.
4. **Timing.** Measure each narration clip with `ffprobe`; set each scene's animation durations so the scene length ≥ clip length + 0.5 s. Do not stretch audio.
5. **Assembly.** `ffmpeg` concat of scene videos muxed with their narration; a 1 s title card and a sources card at the end. Output `out/<slug>.mp4` and `out/<slug>-captions.srt` generated from the storyboard text and measured clip durations.
6. **Review.** Extract 3–4 frames (`ffmpeg -ss <t> -frames:v 1`) and read them back: text legible, nothing clipped, numbers match the storyboard. Watch the total duration. Fix and re-render.

## Visual grammar (what makes it 3b1b-like)

- Dark background, one accent colour per concept, consistent across scenes.
- Build equations and diagrams incrementally; never show a finished slide. Transform one object into the next (`Transform`, `ReplacementTransform`) instead of cutting.
- Numbers animate from the predicted value to the measured value where both exist; the gap is the moment of the video.
- Label everything on screen that the narration mentions, at the moment it is mentioned.
- Text on screen ≤ 12 words at a time. The narration carries the sentences; the screen carries the structure.
- Every scene that shows a number shows a small source tag in the corner.

## Reuse the lower rungs

- Pull constants from `explorers/params.json` or `notes/` if they exist; do not retype.
- Reuse the mechanism diagrams from `diagrams/` as reference for scene layout.
- If notes do not exist, say so and offer to run learn-notes first; a video built without the summaries tends to narrate the source's structure instead of its ideas.

## Environment rules

- Use the shared venv `~/.local/share/learn-kit/venv`. Extra packages go there via `uv pip install --python ~/.local/share/learn-kit/venv/bin/python <pkg>`; pin modern versions when adding ML packages (the resolver once backtracked to a 2021 `transformers` needing a Rust compiler; the fix was `"transformers>=4.45" "torch>=2.4"`). No `pip install` outside it, no `brew install` without asking.
- Manim needs a LaTeX distribution for `MathTex`; `latex` is not on PATH on this machine, so use `Text` for equations rather than installing TeX unasked.
- Rendering is slow; render one scene at low quality to validate the toolchain before writing the rest.

## Output

- `videos/<nn>-<slug>/{storyboard.md, scenes/, audio/, out/<slug>.mp4, out/<slug>-captions.srt}`
- `videos/INDEX.md`: file, duration, teaches, sources.
- Append to `SOURCES.md`.
