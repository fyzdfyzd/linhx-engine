---
description: Làm tiếp deck đang dở ở bước còn thiếu
argument-hint: "[thư mục deck]"
---
Dùng skill `deck-proposal`. Chạy `python "${CLAUDE_PLUGIN_ROOT}/scripts/deck.py" trang-thai $ARGUMENTS` (không có đối số thì tìm thư mục có `trang-thai.json` mới nhất trong `deck/`), rồi làm bước cần làm tiếp bằng skill tương ứng.
