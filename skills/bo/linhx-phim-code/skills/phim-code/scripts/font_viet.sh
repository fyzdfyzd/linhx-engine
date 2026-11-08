#!/bin/sh
# Tải font có dấu tiếng Việt (OFL, Google Fonts) vào thư mục phim: sh font_viet.sh <phim>/fonts
set -e
OUT="${1:-fonts}"; mkdir -p "$OUT"
lay() { # $1 = family query, $2 = tên file
  url=$(curl -fsS "https://fonts.googleapis.com/css2?family=$1" | grep -o 'https://fonts.gstatic.com[^)]*' | head -1)
  [ -n "$url" ] || { echo "không lấy được $2" >&2; return 1; }
  curl -fsS -o "$OUT/$2" "$url" && echo "$OUT/$2"
}
lay "Be+Vietnam+Pro:wght@600" BeVietnamPro-600.ttf
lay "Be+Vietnam+Pro:wght@400" BeVietnamPro-400.ttf
lay "Noto+Serif:ital@1" NotoSerif-Italic.ttf
lay "Lora:wght@500" Lora-500.ttf
lay "Dancing+Script:wght@600" DancingScript-600.ttf
echo "Font OFL từ Google Fonts. Ghi vào CREDITS."
