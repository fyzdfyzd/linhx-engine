# Kết quả dựng nốt deck CSMO v8 (slide 19–25)

- **Số slide**: **25/25** (`project/deck.json`, `project/slides/s01..s25.html`, `CSMO26_T21_v8.pptx` 25 slide, `CSMO26_T21_v8.pdf` 25 trang, `png/s01..s25.png` 1920×1080, `tong.png` 5×5).
- **Ràng buộc**: `s01`–`s18` giữ nguyên 100% (`git diff 140ffa44` = 0 byte trên `s01..s18.html` & `png/s01..s18.png`), giữ nguyên chữ `TEXT-A-v3.md`, không commit ảnh `viec/csmo-talk/`.
- **Slide 19–25**: `s19` mở Chặng 4 đúng khuôn `s04/s08/s14`; `s20` ảnh `a03`; `s21` ảnh `a06`; `s22` khung QR `540×540px` (`50%` chiều cao ≥ 45%) ghi `"QR"`; `s23` việc trước thứ Hai; `s24` dòng thời gian 4 tuần; `s25` kết + ảnh `a10` + 4 chặng sáng đủ. Notes = lời nói.
- **Kết quả `vls.py`**:
  - `phong`: ĐẠT `134/134` chữ Việt (`Playfair Display`, `Be Vietnam Pro`, `Be Vietnam Pro SemiBold`), xuất `.vong-lap/bang-dau.png`.
  - `do`: **17/25** slide `0` lỗi máy (riêng `s19`–`s25` đạt **6/7** slide `0` lỗi: `s19, s20, s21, s22, s23, s25`); `0` lỗi tràn khung, cắt chữ, chồng lấn, tương phản, cỡ chữ, số khối trên cả 25 slide.
- **Slide lệch luật (`vls.py`)**:
  - Lỗi `nhieu-chu` (>40 chữ, giữ nguyên văn bản gốc): **8 slide** — `s03` (61), `s06` (45), `s10` (46), `s11` (42), `s12` (41), `s15` (43), `s17` (47), `s24` (42).
  - Lưu ý `truc-canh` (>5 trục, không chặn): `s03, s04, s08, s14, s15, s18, s19, s25`.
