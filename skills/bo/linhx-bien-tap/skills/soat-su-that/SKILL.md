---
name: soat-su-that
description: Lượt biên tập 1, đối chiếu từng câu có số liệu, tên, sự kiện, luật với kho nguồn của bài; bắt chỗ nói nhiều hơn nguồn, bịa, sai thuật ngữ pháp lý. Dùng trong bien-tap-bai hoặc khi cần kiểm sự thật một bài.
---

# Soát sự thật (lượt 1)

Chạy trong subagent mới. Chỉ đọc: bài, kho nguồn, sổ hồi quy. Không đọc dàn ý hay ghi chú của người viết, để không bị thuyết phục bởi ý định thay vì chữ trên trang.

## Cách làm
1. Tách bài thành câu: `python ${CLAUDE_PLUGIN_ROOT}/scripts/cham_cau.py bai.md --xuat-cau cau.txt`.
2. Đánh dấu mọi câu có: con số, phần trăm, năm tháng, tên người, tổ chức, văn bản luật, sự kiện, lời trích, khẳng định về "người ta", "báo chí", "thị trường", "ai cũng".
3. Với từng câu đã đánh dấu:
   - Có mã [N..]/[T..]: mở đúng dòng mã ấy trong kho, so **từng vế** của câu với dữ kiện. Câu nói nhiều hơn kho một vế cũng là `NG`. Bỏ chữ giới hạn của nguồn ("tự khai", "số đăng ký", "sau bốn năm", "ở Mỹ") là `SO`.
   - Có [GIẢ LẬP]/[CẦN LINH]: không bắt bịa, ghi vào danh sách chờ tác giả.
   - Không mã, không dấu: là `NG` nếu là khẳng định kiểm được, `BI` nếu là cảnh hay lời nói của người cụ thể.
4. Thuật ngữ pháp lý, tên cơ quan, tên văn bản: kiểm đúng chữ (`PL`). Gặp điều luật thì ghi "cần đối chiếu văn bản gốc" nếu kho chưa trích nguyên văn.
5. Đối chiếu `so-loi-hoi-quy.json`: lỗi cũ quay lại dưới chữ khác (ví dụ "nhiều thành phố trả tiền máy" thành "có quận trợ tiền điện toán") vẫn là lỗi hồi quy.
6. Suy diễn trình như hệ quả của số liệu (số Na Uy "sau bốn năm" thành "một tuần nằm viện") là `SO`.

## Trả về `bt-1-su-that.md`
Bảng: `| Câu | Mã nguồn trong câu | Mã lỗi | Kho nói gì | Câu sửa hoặc "cắt" |`, xếp theo thứ tự trong bài. Sau bảng: danh sách dấu [GIẢ LẬP]/[CẦN LINH]; danh sách dòng mới nên thêm vào sổ hồi quy (tên, mẫu regex).
Không quá 20 dòng lỗi. Không có lỗi thì ghi rõ "không có lỗi sự thật" và số câu đã kiểm.
