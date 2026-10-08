#!/usr/bin/env bash
# Build the full Interstellar 8-bit film: score -> loudness -> render all shots -> out/interstellar_8bit.mp4
# Needs: python3 (Pillow, numpy) and ffmpeg.   Usage:  cd interstellar && ./build.sh
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p out
python3 music.py
ffmpeg -y -loglevel error -i out/score.wav \
  -af "acompressor=threshold=-24dB:ratio=4:attack=5:release=250:makeup=2,loudnorm=I=-16:TP=-1.5:LRA=11" \
  -ar 44100 out/score_n.wav
python3 render.py
echo "done: out/interstellar_8bit.mp4"
