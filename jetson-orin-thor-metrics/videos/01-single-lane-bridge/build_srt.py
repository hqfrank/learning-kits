#!/usr/bin/env python3
"""Build the .srt from narration text + measured scene part durations.

Each caption spans one scene. Start = cumulative part offset; end = start +
narration clip length (ffprobe of the WAV), so captions track the audio, not
the padded video tail.
"""
import subprocess, os

HERE = os.path.dirname(os.path.abspath(__file__))

# part file -> narration wav (None = silent card)
PARTS = [
    ("00_title.mp4", None),
    ("01.mp4", "scene_01.wav"),
    ("02.mp4", "scene_02.wav"),
    ("03.mp4", "scene_03.wav"),
    ("04.mp4", "scene_04.wav"),
    ("05.mp4", "scene_05.wav"),
    ("06.mp4", "scene_06.wav"),
    ("07_sources.mp4", None),
]

NARRATION = {
    "scene_01.wav": "A modern robot runs three jobs on one Jetson Thor: a 100 Hz control loop (10 ms deadline), perception, and a VLA planner at ~5 Hz. One GPU, one memory controller, one memory pool \u2014 a single-lane bridge.",
    "scene_02.wav": "The datasheet promises headroom: NVFP4 advertises 1035 dense TFLOP/s; a tuned library reaches 627.8 (~61%). INT8/FP8 advertise 517; measured ~two-thirds. The control loop needs a rounding error of that. TOPS is not the constraint.",
    "scene_03.wav": "Sharing one GPU context is not fair. Below a threshold the victim runs; above it \u2014 just 14% of warp slots on Thor, 8% on Orin \u2014 the victim is locked out until the co-tenant drains. Bistable: co-running or locked out, no graded middle.",
    "scene_04.wav": "The WBC policy's solo p99 is 41.6 us. Under the full co-tenant roster plus a CPU memory hog it inflates to 5.9 ms \u2014 141\u00d7. It still fits the 10 ms budget, but barely; almost all of it is spent waiting.",
    "scene_05.wav": "Shared context destroys the loop (110.7 ms p99, 51% dropped). A separate process recovers ~90% (~17 ms, still over budget). Plain MPS barely helps. MPS + a 25% SM cap returns it to 0% dropped \u2014 the planner pays: 5 \u2192 3.6 Hz.",
    "scene_06.wav": "But at ~172 GB/s of CPU memory load \u2014 70% of Thor's 245 GB/s roof \u2014 every discipline collapses. The bridge has a fixed capacity. Scheduling decides who pays; it cannot fix a memory problem.",
}


def dur(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", path]).decode().strip()
    return float(out)


def ts(sec):
    h = int(sec // 3600); sec -= h * 3600
    m = int(sec // 60); sec -= m * 60
    s = int(sec); ms = int(round((sec - s) * 1000))
    if ms == 1000:
        s += 1; ms = 0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main():
    parts_dir = os.path.join(HERE, "out", "parts")
    audio_dir = os.path.join(HERE, "audio")
    offset = 0.0
    idx = 1
    lines = []
    for part, wav in PARTS:
        pdur = dur(os.path.join(parts_dir, part))
        if wav:
            clip = dur(os.path.join(audio_dir, wav))
            start = offset
            end = offset + clip
            lines.append(f"{idx}\n{ts(start)} --> {ts(end)}\n{NARRATION[wav]}\n")
            idx += 1
        offset += pdur
    with open(os.path.join(HERE, "out", "single-lane-bridge.srt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote srt;", idx - 1, "captions; total", round(offset, 2), "s")


if __name__ == "__main__":
    main()
