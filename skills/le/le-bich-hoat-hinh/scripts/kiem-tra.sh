#!/usr/bin/env bash
# Kiểm tra máy chạy có gì, để chọn đường dựng. In kết quả, không cài gì, không cần mạng.
echo "== python";   python3 --version 2>&1
python3 -c "import PIL; print('Pillow', PIL.__version__)" 2>/dev/null || echo 'KHÔNG có Pillow'
python3 -c "from PIL import features; print('WebP động:', features.check('webp_anim'))" 2>&1 | tail -1
python3 -c "import imageio_ffmpeg; print('imageio-ffmpeg có')" 2>/dev/null || echo 'không có imageio-ffmpeg'
echo "== ffmpeg";   (ffmpeg -version 2>&1 | head -1) || echo "không có ffmpeg"
echo "== node";     node --version 2>&1 || echo "không có node"
echo "== trình duyệt"
for b in chromium chromium-browser google-chrome chrome; do command -v $b && break; done || echo "không thấy Chrome/Chromium"
python3 -c "import playwright; print('playwright (python) có')" 2>/dev/null || echo 'không có playwright'
echo "== gợi ý"
echo "Có Pillow  -> đường A (scripts/lebich.py): ảnh, GIF, WebP động dựng thẳng bằng Python."
echo "Có ffmpeg  -> MP4 bằng ffmpeg từ khung PNG; không có thì thử imageio-ffmpeg, cùng lắm xuất GIF + thư mục khung."
echo "Có Chrome + playwright -> đường B (HTML + GSAP, assets/lebich-rig.js), giống bản Claude."
