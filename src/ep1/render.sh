#!/bin/bash
# 4 分割で並列に書き出し（ONLY="2" で一部だけ書き直し、ASSEMBLE_ONLY=1 で結合だけ）、ナレーション入りの音声と合わせ、冒頭 30 秒（output/sample_30s.mp4）とつなぐ
set -e
cd "$(dirname "$0")"
D=$(python3 -c "import json;print(json.load(open('timeline.json'))['duration'])")
F=$(python3 -c "import math;print(math.ceil($D*30))")
P=${P:-4}
[ -z "$ASSEMBLE_ONLY" ] && for i in ${ONLY:-$(seq 0 $((P-1)))}; do
  node render.mjs $((F*i/P)) $((F*(i+1)/P)) build/part$i.mp4 &
done
wait
: > build/parts.txt; for i in $(seq 0 $((P-1))); do echo "file 'part$i.mp4'" >> build/parts.txt; done
ffmpeg -y -loglevel error -f concat -safe 0 -i build/parts.txt -c copy build/ep1_video.mp4
ffmpeg -y -loglevel error -i build/ep1_video.mp4 -i build/ep1_mix.wav -c:v copy -c:a aac -b:a 256k -ar 48000 -shortest build/ep1_body.mp4
# 冒頭と本編をつなぎ、全体に一定の音量補正（-15 LUFS）をかける。loudnorm の動的処理は静かな冒頭を持ち上げてしまうので使わない
ffmpeg -y -loglevel error -i ../../output/sample_30s.mp4 -i build/ep1_body.mp4 -filter_complex \
 "[0:a]aresample=48000,aformat=channel_layouts=stereo[a0];[1:a]aformat=channel_layouts=stereo[a1];[a0][a1]concat=n=2:v=0:a=1[a]" -map "[a]" build/joined.wav
I=$(ffmpeg -hide_banner -i build/joined.wav -af ebur128 -f null - 2>&1 | grep -A1 "Integrated loudness" | grep -oE "I: +-?[0-9.]+" | grep -oE "\-?[0-9.]+$")
G=$(python3 -c "print(-15 - ($I))")
ffmpeg -y -loglevel error -i ../../output/sample_30s.mp4 -i build/ep1_body.mp4 -i build/joined.wav -filter_complex \
 "[0:v][1:v]concat=n=2:v=1:a=0[v];[2:a]volume=${G}dB,alimiter=limit=0.84:level=false[an]" \
 -map "[v]" -map "[an]" -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -c:a aac -b:a 256k -ar 48000 -movflags +faststart build/ep1_first5min_master.mp4
# リポジトリ用の軽い版（GitHub の 100MB 制限のため）
ffmpeg -y -loglevel error -i build/ep1_first5min_master.mp4 -c:v libx264 -preset slow -crf 26 -maxrate 2200k -bufsize 4400k -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart ../../output/ep1_first5min.mp4
echo done
