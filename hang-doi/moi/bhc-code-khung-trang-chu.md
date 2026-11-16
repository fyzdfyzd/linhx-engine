may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\ifagent-wt\bhc-code-khung-trang-chu
phu_thuoc: bhc-code-nhan-nguon

Brand health check: VẼ KHUNG (chưa nối vào app) cho luồng khách tự quét, cùng ngôn ngữ hướng B "tạp chí" của báo cáo. Chạy tiền cảnh, tuần tự, không sinh thợ con.
Lý do: trang chủ hiện tại (http://localhost:3020/) là giao diện cũ nền tối, logo và kiểu chữ khác hẳn landing báo cáo /bao-cao/<mã>/ (nền giấy sáng, chữ lớn, nút Sáng/Đêm). Khách đi từ trang chủ sang báo cáo thấy hai sản phẩm khác nhau.
1. `git -C C:\linhx\ifagent fetch origin agy/bhc-code-nhan-nguon`, worktree `C:\linhx\ifagent-wt\bhc-code-khung-trang-chu` nhánh mới `agy/bhc-code-khung-trang-chu` từ origin/agy/bhc-code-nhan-nguon. Chưa có nhánh đó thì dừng, ghi CHUA_CO_NEN.
2. Đọc trước: bao-cao/khung/B (landing + PDF), server/lib/landing.js, public/ (trang chủ cũ), docs/ (phương pháp). Dùng ĐÚNG token màu, font, logo, khoảng cách, nút Sáng/Đêm của landing B; không bịa màu hay font mới.
3. Dựng HTML tĩnh trong apps/brand-health/bao-cao/khung/B-trang-chu/ (phục vụ qua http, không sửa server/app.js): 4 màn
   a) Trang chủ: tiêu đề mạnh kiểu tạp chí, 3 chỉ số Có mặt / Đúng / Được đề xuất giải thích một dòng mỗi chỉ số, ô nhập tên thương hiệu + ngành + website, nút "Quét thương hiệu", một dải số thật mẫu (Vinamilk 97/98/72, IF Agent 0/33/27) dẫn tới 2 báo cáo mẫu.
   b) Bảng sự thật: khách khai/xác nhận 4–6 sự thật (công ty, năm, sản phẩm chính, trụ sở…), giải thích ngắn vì sao cần.
   c) Đang quét: tiến độ theo từng mô hình AI và số câu đã hỏi, có thứ tự hàng đợi, không chữ kỹ thuật.
   d) Xong: 3 chỉ số + một câu "sốc" + nút xem báo cáo đầy đủ (dẫn tới /bao-cao/<mã>/), ô để lại email/SĐT có ô đồng ý.
   Mỗi màn chạy đẹp ở 1280×800 và 360×780, không tràn ngang, Sáng và Đêm. Chữ tiếng Việt đủ dấu, không chữ kỹ thuật (không "API", "model", "JSON", mã nguồn).
4. Thêm test khung (node --test) kiểm: 4 file tồn tại, không tràn ngang ở 360, không chuỗi cấm ở bước 3, dùng biến màu của khung B. `npm run verify` xanh.
5. Bằng chứng bang-chung/bhc-code-khung-trang-chu/: mỗi màn × {1280, 360} × {Sáng} ảnh màn đầu, thêm màn a ở Đêm 1280; ảnh ghép 4 màn 1280 cạnh nhau `ghep-1280.png`. Mỗi ảnh ≤ 600 KB.
6. Commit, push `agy/bhc-code-khung-trang-chu`.
CẤM: nối khung vào app, sửa server/, deploy, gọi AI thật, sinh ảnh bằng AI, in khoá, gửi mail, đụng apps/event, apps/lab, packages/, push nhánh khác. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md ngắn: `dat: co|khong`; SHA đỉnh; verify pass/fail; tràn 360 từng màn; đường dẫn ghep-1280.png.
