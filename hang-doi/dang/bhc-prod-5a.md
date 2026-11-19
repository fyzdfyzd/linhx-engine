May: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 30
khong_tien_phut: 10
theo_doi: C:\linhx\ifagent-wt\bhc-prod-4
nhan: may-2 2026-11-19T10:46:22+0700
moc: 5bbcb0cef3b040085a109515b9d5910ec236987d

Lưu ý máy: KHÔNG background task/subagent; KHÔNG chờ/ngủ dài; MỖI LỆNH PHẢI XONG TRONG 3 PHÚT. Ghi KET-QUA vào bang-chung/bhc-prod-5/ trên nhánh agy/bhc-prod-5, push sau mỗi bước. KHÔNG in khoá.
Bối cảnh: phiếu bhc-prod-4b đã quét CSMO trên prod (2026-11-19-csmo-29040bd3) nhưng HỎNG: (1) 2 làn Gemini trực tiếp lỗi toàn bộ ("không trả lời kịp"), chỉ số Đúng = null "Chưa đối chiếu được"; agy thử khoá Gemini thấy HTTP 402. (2) Grok tốn 3,14 USD cho 13 câu (≈0,24 USD/câu) — quá đắt, Linh muốn AI rẻ. (3) ChatGPT mini chỉ giữ 20/42 câu. Báo cáo này KHÔNG xuất bản; nếu đang công khai thì ẩn.
Linh đã duyệt deploy prod và chạy báo cáo mẫu (08:14, 09:21, 09:28 VN 19/11).
1. Chẩn đoán Gemini (không quét): trong container ifagent-brand-health-1 (sudo docker exec) và stg-brand-app, gọi 1 câu ngắn tới Gemini bằng đúng biến GEMINI_API_KEY/GEMINI_MODEL của container (node -e với fetch tới https://generativelanguage.googleapis.com/v1beta/models/<GEMINI_MODEL>:generateContent, có và không có tools google_search). In: tên model, HTTP status, error.status, error.message (cắt 200 ký tự, KHÔNG in khoá). So sánh 2 khoá prod và staging có giống nhau không bằng sha256 8 ký tự đầu (không in khoá). Thử thêm model gemini-3.5-flash-lite nếu GEMINI_MODEL khác.
2. Sửa: nếu khoá/model staging chạy được mà prod không → chép GEMINI_API_KEY và GEMINI_MODEL từ /opt/stg-brand/stg-brand.env sang /opt/ifagent/infra/brand-health.env ngay trên VM (sudo, không in; sao lưu .bak-19-11-b). Nếu cả hai khoá đều lỗi thanh toán/hạn mức → DỪNG, ghi nguyên văn status + message, ghi "can Linh nap tien Gemini / khoa moi".
3. Bỏ Grok khỏi prod và staging: OPENROUTER_MODELS=<id mini đang dùng>,google/gemini-2.5-flash,perplexity/sonar,deepseek/deepseek-v4.1-flash-1017 (không x-ai). Kiểm thời gian chờ làn openai-tim: đặt BH_TIMEOUT_MS_OPENAI_TIM=60000 nếu nhỏ hơn.
4. Recreate chỉ service brand-health (cd /opt/ifagent/infra && sudo docker compose up -d --force-recreate brand-health) và stg-brand; healthz 200; thử lại bước 1 trong container prod phải 200. Trang chủ prod, event, bd giữ HTTP như cũ.
CẤM: quét thật, đụng service khác, Caddy/DNS, in khoá. KET-QUA: dat, kết quả chẩn đoán (status/message), đã đổi gì, HTTP sau.
