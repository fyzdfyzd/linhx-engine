may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\ifagent-wt\bhc-chi-phi
nhan: may-2 2026-11-17T18:29:22+0700

Lưu ý máy: KHÔNG dùng background task, subagent hay thợ con; mọi lệnh tiền cảnh. Gọi `npm.cmd`. Commit đầu trong 5 phút, commit + push mỗi 10 phút.
Brand health check: chi phí thật + làn ChatGPT quá giờ. Worktree C:\linhx\ifagent-wt\bhc-chi-phi, nhánh agy/bhc-chi-phi từ origin/agy/bhc-staging. CHỈ sửa apps/brand-health (+ bang-chung/bhc-chi-phi). Không deploy, không gọi AI thật.
Bối cảnh (quét thật staging 17/11 18:20): 4 làn OpenRouter tốn thực 0,77 USD (~20.000 đ) cho 1 lượt nhanh, app ước ~6.000 đ (BH_GIA_OPENROUTER=250/câu) → trần ngày ở quản trị tính thấp gấp ~3. Làn openai-tim (gpt-5) quá giờ 2/6 câu.
1. Provider OpenRouter: gửi `usage: {include: true}` trong body; đọc `usage.cost` (USD) trong phản hồi, lưu chi phí thật theo từng câu + từng làn vào kết quả quét. Tổng chi phí ngày ở quản trị dùng số thật (đổi VND bằng BH_TY_GIA, mặc định 26500); chỉ dùng đơn giá ước khi phản hồi không có cost. Nâng mặc định BH_GIA_OPENROUTER lên 800.
2. Màn quản trị chi tiết lượt quét: thêm cột chi phí từng làn (đ).
3. Thời gian chờ theo làn: cho phép BH_TIMEOUT_MS_<LAN> (vd BH_TIMEOUT_MS_OPENAI_TIM), mặc định làn openai-tim 90000; làn quá giờ ghi rõ "quá thời gian" trong báo cáo quản trị, không tính là sai.
4. Test khoá: AI giả trả usage.cost → tổng chi phí đúng; thiếu cost → dùng đơn giá; timeout riêng làn được tôn trọng. Lint giữ nguyên luật cũ (không delayMs, không nhãn thô).
5. verify + test:lap xanh; ảnh quản trị chi tiết 1280 vào bang-chung/bhc-chi-phi/. Push agy/bhc-chi-phi.
KET-QUA.md: dat co|khong, SHA, số test, ảnh.
