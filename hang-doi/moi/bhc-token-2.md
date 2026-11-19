May: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 8
khong_tien_phut: 5
theo_doi: C:\linhx\ifagent-wt\bhc-token

Lưu ý máy: KHÔNG background task/subagent; MỖI LỆNH XONG TRONG 2 PHÚT. Chỉ KIỂM, không sửa gì. TUYỆT ĐỐI KHÔNG in, ghi, commit giá trị khoá (chỉ ghi sha8 nếu cần). Push KET-QUA vào bang-chung/bhc-token-2/ trên nhánh agy/bhc-token-2.
Chạy trên VM prod qua `gcloud compute ssh ifagent-event --zone=asia-southeast1-b --project=ifagent-event-2026 --command "..."`, đọc khoá từ /opt/ifagent/infra/brand-health.env bằng biến shell (không echo):
1. OpenRouter: `curl -s https://openrouter.ai/api/v1/key -H "Authorization: Bearer $OPENROUTER_API_KEY"` và `curl -s https://openrouter.ai/api/v1/credits -H ...`. Ghi: limit, usage, limit_remaining, total_credits, total_usage, số dư = total_credits - total_usage (USD).
2. (bỏ qua — không gọi thử model OpenRouter)
3. Gemini: gọi generateContent model gemini-3.5-flash-lite với khoá GEMINI_API_KEY trong env đó, câu "ok". Ghi mã HTTP + lỗi nếu có.
KET-QUA: bảng số dư OpenRouter, từng model HTTP, Gemini HTTP, kết luận dat/khong.
Linh (14:13 VN) báo vừa nạp 10 USD. Ghi số dư OpenRouter và HTTP Gemini hiện tại.
