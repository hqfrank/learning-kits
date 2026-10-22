#!/bin/bash
set -e
cd "$(dirname "$0")"
SC=scenes/media/videos
OUT=out
WORK=/tmp/rwb_assembly
rm -rf "$WORK"; mkdir -p "$WORK"

# ---- title card (manim Scene00) ----
ffmpeg -y -i "$SC/scene_00/720p30/Scene00.mp4" \
  -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 -shortest \
  -c:v libx264 -pix_fmt yuv420p -r 30 -c:a aac "$WORK/00_title.mp4" 2>/dev/null

# ---- animated scenes with narration ----
declare -a NUM=(01 02 03 04 05 06 07 08)
for n in "${NUM[@]}"; do
  V="$SC/scene_${n}/720p30/Scene${n}.mp4"
  A="audio/scene_${n}.wav"
  ffmpeg -y -i "$V" -i "$A" \
    -filter_complex "[1:a]apad[a]" -map 0:v -map "[a]" -shortest \
    -c:v libx264 -pix_fmt yuv420p -r 30 -c:a aac -ar 48000 "$WORK/scene_${n}.mp4" 2>/dev/null
done

# ---- sources card (scene 09, silent) ----
ffmpeg -y -i "$SC/scene_09/720p30/Scene09.mp4" \
  -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 -shortest \
  -c:v libx264 -pix_fmt yuv420p -r 30 -c:a aac "$WORK/scene_09.mp4" 2>/dev/null

# ---- concat ----
LIST="$WORK/list.txt"
{
  echo "file '$WORK/00_title.mp4'"
  for n in "${NUM[@]}"; do echo "file '$WORK/scene_${n}.mp4'"; done
  echo "file '$WORK/scene_09.mp4'"
} > "$LIST"

mkdir -p "$OUT"
ffmpeg -y -f concat -safe 0 -i "$LIST" -c copy "$OUT/measuring-a-robot-stack.mp4" 2>/dev/null
echo "assembled:"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUT/measuring-a-robot-stack.mp4"
