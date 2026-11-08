#!/bin/sh
# Contact sheet 12 khung đều nhau từ một video: sh to_sheet.sh video.mp4 [ra.jpg] [số-khung]
set -e
V="$1"; OUT="${2:-${V%.*}-sheet.jpg}"; N="${3:-12}"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V")
FPS=$(awk "BEGIN{print $N/$D}")
ffmpeg -v error -y -i "$V" -vf "fps=$FPS,scale=480:-2,drawtext=text='%{pts\\:hms}':x=8:y=8:fontcolor=white:box=1:boxcolor=black@0.5,tile=4x$(( (N+3)/4 ))" -frames:v 1 "$OUT" 2>/dev/null \
 || ffmpeg -v error -y -i "$V" -vf "fps=$FPS,scale=480:-2,tile=4x$(( (N+3)/4 ))" -frames:v 1 "$OUT"
echo "$OUT"
