#!/usr/bin/env python3
"""Generate .srt captions from scene durations and narration text."""
import subprocess
import os

BASE = os.path.dirname(os.path.abspath(__file__))
WORK = "/tmp/rwb_assembly"

# order of segments in the final video; title (00) and sources (09) are silent
SEGMENTS = ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09"]

# narration text per scene (None = silent card)
NARR = {}
with open(os.path.join(BASE, "narration.txt")) as f:
    for line in f:
        line = line.rstrip("\n")
        if not line:
            continue
        num, text = line.split("|", 1)
        NARR[num] = text
NARR["00"] = None
NARR["09"] = None


def dur(path):
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path]).decode().strip()
    return float(out)


def fmt(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def split_text(text, n):
    """Split a sentence block into n roughly equal caption lines."""
    words = text.split()
    k = max(1, len(words) // n + (1 if len(words) % n else 0))
    chunks = [" ".join(words[i:i + k]) for i in range(0, len(words), k)]
    return chunks


entries = []
clock = 0.0
idx = 1
for seg in SEGMENTS:
    f = os.path.join(WORK, "00_title.mp4" if seg == "00" else f"scene_{seg}.mp4")
    d = dur(f)
    text = NARR.get(seg)
    if text:
        # break into ~2 caption lines proportional to length
        n_caps = max(1, round(len(text.split()) / 11))
        chunks = split_text(text, n_caps)
        per = d / len(chunks)
        for j, ch in enumerate(chunks):
            start = clock + j * per
            end = clock + (j + 1) * per
            entries.append((idx, start, end, ch))
            idx += 1
    clock += d

srt_path = os.path.join(BASE, "out", "measuring-a-robot-stack-captions.srt")
with open(srt_path, "w") as f:
    for i, start, end, text in entries:
        f.write(f"{i}\n{fmt(start)} --> {fmt(end)}\n{text}\n\n")
print(f"wrote {srt_path} with {len(entries)} cues, total {clock:.1f}s")
