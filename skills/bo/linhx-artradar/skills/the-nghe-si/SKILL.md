---
name: the-nghe-si
description: Dùng khi biến records.jsonl đã quét thành thẻ nghệ sĩ có tag phong cách theo từ điển có kiểm soát và ghi chú Obsidian.
---
# Thẻ nghệ sĩ (M3)

1. Gom: `python scripts/gom_nghe_si.py --records data/records.jsonl --cards data/artists.json --notes vault/artists`
2. Với mỗi thẻ chưa có `mo_ta_phong_cach` (làm theo lô 10 thẻ):
   - Đọc tiêu đề, mô tả, credit của bài phát hiện.
   - Xem 1-2 thumbnail: tải vào thư mục tạm của hệ điều hành, xem, **xoá ngay sau khi xem**. Không lưu ảnh vào lab hay vault.
   - Điền `style_tags` theo `../../schemas/tu-dien-phong-cach.json` (mỗi trục ≤2 giá trị, không thêm giá trị ngoài từ điển), `chu_de`, `dung_cho`, `medium`, `country` nếu bài có nói.
   - Viết `mo_ta_phong_cach` 2-4 câu bằng lời mình: hình khối, tỉ lệ, nét, màu, giọng. Không chép câu của bài báo.
   - Ghi thẻ trùng người (cùng nghệ sĩ khác handle) vào `ghi_chu`, gộp tay.
3. Chạy lại bước 1 để cập nhật ghi chú Markdown (dữ liệu đã điền được giữ vì script đọc artists.json cũ).
4. Báo cáo: số thẻ, phân bố theo `chu_de` và `ty_le`, 10 thẻ hợp Làng Mèo, 10 thẻ hợp tiên hiệp.

Luật: không đưa tên nghệ sĩ còn sống vào prompt sinh ảnh; thẻ có `noai: true` chỉ giữ link, không xem ảnh.
