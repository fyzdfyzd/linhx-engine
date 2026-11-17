may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 45
khong_tien_phut: 25
theo_doi: C:\linhx\ifagent-wt\bhc-theo-doi

Lưu ý máy: KHÔNG background task/subagent; tiền cảnh; `npm.cmd`/`npx.cmd` (npm.ps1 bị chặn). Commit đầu trong 5 phút, commit + push mỗi 10 phút.
Brand health check, gói theo dõi hằng tháng (bản đầu, chỉ AI giả). Worktree C:\linhx\ifagent-wt\bhc-theo-doi, nhánh agy/bhc-theo-doi từ origin/agy/bhc-chi-phi. CHỈ sửa apps/brand-health (+ bang-chung/bhc-theo-doi). Không deploy, không gọi AI thật, không đụng apps/event, apps/lab, packages/.
1. Dữ liệu: mỗi thương hiệu có thể bật "theo dõi tháng" ở quản trị (lịch: ngày trong tháng, số làn, chế độ nhanh/đầy đủ). Bộ hẹn giờ trong server (kiểm mỗi giờ, đồng hồ tiêm được để test) chạy lại lượt quét đúng câu hỏi + sự thật gốc của lượt trước, tôn trọng trần chi phí ngày.
2. Trang so sánh hai lượt (công khai theo mã báo cáo, phong cách hướng B tạp chí): 3 chỉ số kỳ này vs kỳ trước (mũi tên + chênh lệch), câu nào AI đổi ý, trợ lý nào đổi; một câu chốt tự sinh từ dữ liệu (không gọi AI). Đẹp ở 1280 và 360, không tràn ngang.
3. Quản trị: cột "Theo dõi" + nút bật/tắt + lịch; danh sách lượt theo thời gian của một thương hiệu.
4. Test khoá: lịch chạy đúng ngày với đồng hồ giả; vượt trần thì hoãn và ghi lý do; so sánh tính đúng chênh lệch; trang 360 không tràn ngang; lint cũ giữ nguyên.
5. verify + test:lap xanh. Ảnh 1280 + 360 trang so sánh (dữ liệu giả Vinamilk 2 kỳ) và màn quản trị vào bang-chung/bhc-theo-doi/. Push agy/bhc-theo-doi.
KET-QUA.md: dat co|khong, SHA, số test, ảnh.
