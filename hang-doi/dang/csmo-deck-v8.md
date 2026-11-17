may: may-2
loai: code
tran_phut: 40
theo_doi: C:\linhx\wt-csmo-v8
nhan: may-2 2026-11-17T20:15:47+0700

Phiếu DỰNG DECK CSMO v8 từ chữ đã chấm 3 vòng (LAB130, Linh đã chọn bản A). Chữ đã chốt, KHÔNG sửa câu chữ.

Đầu vào:
- Nhánh claude/project-thread-j24agg của linhx-engine, thư mục viec/lab130-slide-nhieu-vong/thiet-ke/:
  - TEXT-A-v3.md: 25 slide (tiêu đề, chữ phụ, hình gợi ý, nguồn, lời nói). Lời nói đưa vào notes.
  - TIEU-CHUAN-THIET-KE.md: tiêu chí V1–V8 sẽ chấm.
  - build7-tham-khao.py: hàm dựng cũ (txt, rect, so_lon, chuong, luoi_cham, nen_anh, xuong_song). Dùng lại, 1pt = 2px.
  - v7-tong-cu.png: bảng ảnh bản cũ để tránh lặp lỗi.
- Nhánh hang-doi: viec/csmo-talk/mau/GHI-CHU.md + ảnh mẫu 01..06 (luật nhìn: nền trơn ngà #F4EFE6 / than #1C1B19, MỘT màu nhấn đỏ #9E2A1F, kẻ mảnh 1px #C9A86A, lề 120px, khoảng trống ≥45%); viec/csmo-talk/anh/a01..a14.jpg ảnh có giấy phép (NGUON.csv). Gợi ý: S2 a13, S5 a01, S7 a12, S9 a05, S10 a11, S19 a03, S20 a06, S25 a10. Ảnh đặt một bên, chừa vùng chữ sạch, KHÔNG chữ đè ảnh.

Cách làm:
git clone -b claude/project-thread-j24agg https://github.com/fyzdfyzd/linhx-engine C:\linhx\wt-csmo-v8 ; lấy ảnh/mẫu bằng: git fetch origin hang-doi && git checkout origin/hang-doi -- viec/csmo-talk/anh viec/csmo-talk/mau (không commit hai thư mục này). Làm trong viec/lab130-slide-nhieu-vong/thiet-ke/v8/.
1) build8.py: 25 slide 1920x1080 đúng thứ tự TEXT-A-v3. Slide mở chương 4/8/13/19 (chặng 1–4) cùng một khuôn, có thanh 4 chặng nhỏ sáng chặng hiện tại. Slide số (5,6,11,12,16) theo mẫu 02: một số rất lớn + một dòng nghĩa + dòng nguồn. S15 công thức nhân to giữa slide. S17 bảng 2 cột ≤3 hàng. S18 năm ô bằng nhau nét 1px. S22 QR ≥45% chiều cao, để ô trống ghi "QR" nếu chưa có link.
2) Luật cứng: chữ nhỏ nhất ≥12pt (24px); tiêu đề cùng vị trí, cùng cỡ; ≤3 cỡ chữ/slide; không thẻ bo góc, icon, gradient, bóng đổ; không AI vẽ ảnh có chữ; không nêu tên thương hiệu riêng của diễn giả.
3) Phông Playfair Display + Be Vietnam Pro, chạy kiểm đủ 134 chữ Việt (skills/le/vong-lap-slide/scripts/vls.py phong, có ở nhánh main: git checkout origin/main -- skills/le/vong-lap-slide, không commit) và kiểm PDF không thay phông.
4) Xuất CSMO26_T21_v8.pptx, .pdf, PNG từng slide 1920 (png/s01..s25.png), bảng ảnh tong.png (5x5).
5) Chạy vls.py do trên pptx (tràn chữ, tương phản); sửa đến khi sạch.
Chạy tiền cảnh. Commit + push lên nhánh claude/project-thread-j24agg sau mỗi 6 slide; hết giờ thì push phần đã xong và ghi rõ dừng ở slide nào.
Cấm: sửa TEXT-A-v3.md, đụng thư mục khác ngoài thiet-ke/v8/.
Trả KET-QUA.md ≤2000 ký tự: đường dẫn tệp, kết quả vls do/phong, slide nào lệch luật và vì sao.

nhip: 20:41 26p đang chờ nền · log cuối 0 phút trước [log_cuoi=2026-11-17T20:41:20+0700] · root agent idle; waiting up to 40m0s for 1 ba
