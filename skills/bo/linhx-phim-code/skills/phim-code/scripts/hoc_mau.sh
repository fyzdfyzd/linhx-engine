#!/bin/sh
# Mổ video mẫu để dựng lại bằng code (nhánh C): khung mỗi 0,25 giây, contact sheet theo đoạn 6 giây,
# danh sách điểm cắt, và tuỳ chọn dải cắt một vùng để đo đường cong chuyển động.
#   sh hoc_mau.sh mau.mp4 [thư-mục-ra] [--vung x:y:w:h --tu 3.0 --den 4.5]
set -e
V="$1"; shift; OUT="hoc-mau"
case "$1" in ""|--*) ;; *) OUT="$1"; shift;; esac
mkdir -p "$OUT/khung" "$OUT/sheet"
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,avg_frame_rate:format=duration -of default=nw=1 "$V" | tee "$OUT/thong-so.txt"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V")
# 1. Khung mỗi 0,25 giây, đánh giờ lên góc
ffmpeg -v error -y -i "$V" -vf "fps=4,scale=480:-2,drawtext=text='%{pts\\:hms}':x=6:y=6:fontsize=16:fontcolor=white:box=1:boxcolor=black@0.6" "$OUT/khung/%04d.jpg" 2>/dev/null \
  || ffmpeg -v error -y -i "$V" -vf "fps=4,scale=480:-2" "$OUT/khung/%04d.jpg"
# 2. Contact sheet: mỗi tấm 24 khung = 6 giây
N=$(ls "$OUT/khung" | wc -l); i=0; s=1
while [ $i -lt "$N" ]; do
  ffmpeg -v error -y -start_number $((i+1)) -i "$OUT/khung/%04d.jpg" -frames:v 24 -vf "tile=6x4:padding=3" -frames:v 1 "$OUT/sheet/$(printf %02d $s).jpg"
  i=$((i+24)); s=$((s+1))
done
# 3. Điểm cắt cảnh (đổi hình > 30%)
ffmpeg -v info -i "$V" -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | grep -o 'pts_time:[0-9.]*' | cut -d: -f2 > "$OUT/diem-cat.txt" || true
echo "điểm cắt: $(wc -l < "$OUT/diem-cat.txt") (xem $OUT/diem-cat.txt)"
# 4. Tuỳ chọn: dải cắt một vùng, mỗi khung gốc một hàng, để đo nhịp/easing
VUNG=""; TU=0; DEN=$D
while [ $# -gt 0 ]; do case "$1" in --vung) VUNG="$2"; shift;; --tu) TU="$2"; shift;; --den) DEN="$2"; shift;; esac; shift; done
if [ -n "$VUNG" ]; then
  X=$(echo "$VUNG" | cut -d: -f1); Y=$(echo "$VUNG" | cut -d: -f2); W=$(echo "$VUNG" | cut -d: -f3); H=$(echo "$VUNG" | cut -d: -f4)
  ffmpeg -v error -y -ss "$TU" -to "$DEN" -i "$V" -vf "crop=$W:$H:$X:$Y,scale=640:-2,tile=1x24:padding=1" -frames:v 1 "$OUT/dai-vung.jpg"
  echo "dải vùng: $OUT/dai-vung.jpg (24 khung liền, ${W}x${H} mỗi hàng)"
fi
echo "xong: $OUT/sheet/*.jpg"
