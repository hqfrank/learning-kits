#!/bin/bash
# Assemble the SM explainer: title card + scenes 01-06 (muxed with narration) + sources card.
set -e
cd "$(dirname "$0")"
VID=media/videos
OUT=out
mkdir -p $OUT work

# 1) mux each narrated scene (01-06) with its narration audio, padding video if needed.
#    Scenes are already >= clip + 0.5s, so audio is shorter than video; -shortest would cut
#    video, so instead pad audio to video length with apad and use -shortest on the (longer) side.
for s in 01 02 03 04 05 06; do
  V=$VID/scene_$s/720p30/Scene$s.mp4
  A=audio/scene_$s.wav
  ffmpeg -y -loglevel error -i "$V" -i "$A" \
    -filter_complex "[1:a]apad[a]" -map 0:v -map "[a]" \
    -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 160k -shortest \
    work/part_$s.mp4
done

# 2) title (00) and sources (07) cards: add silent audio track so concat is uniform.
for s in 00 07; do
  V=$VID/scene_$s/720p30/Scene$s.mp4
  ffmpeg -y -loglevel error -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 \
    -i "$V" -map 1:v -map 0:a \
    -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 160k -shortest \
    work/part_$s.mp4
done

# 3) concat in order 00,01,...,07
: > work/list.txt
for s in 00 01 02 03 04 05 06 07; do echo "file 'part_$s.mp4'" >> work/list.txt; done
ffmpeg -y -loglevel error -f concat -safe 0 -i work/list.txt -c copy $OUT/what-is-an-sm.mp4

echo "assembled:"
ffprobe -v error -show_entries format=duration -of csv=p=0 $OUT/what-is-an-sm.mp4
