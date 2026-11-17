may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\ifagent-wt\bhc-code-openrouter
nhan: may-2 2026-11-17T08:05:28+0700

Lưu ý máy: KHÔNG dùng background task, subagent hay thợ con; mọi lệnh chạy tiền cảnh. Gọi `npm.cmd`/`npx.cmd`. Push sau MỖI commit.
Brand health check: thêm cổng OpenRouter để hỏi nhiều mô hình AI (chưa có khoá, chỉ dựng + test bằng AI giả).
1. Worktree C:\linhx\ifagent-wt\bhc-code-openrouter, nhánh mới agy/bhc-code-openrouter từ origin/agy/bhc-code-noi-app.
2. Trong apps/brand-health/server/lib/providers.js thêm provider "openrouter": gọi https://openrouter.ai/api/v1/chat/completions (API kiểu OpenAI), khoá đọc từ biến môi trường OPENROUTER_API_KEY, danh sách mô hình từ OPENROUTER_MODELS (vd "openai/gpt-5,anthropic/claude-sonnet-4.5,google/gemini-2.5-flash,perplexity/sonar"); mỗi mô hình là một làn riêng, nhãn người đọc (vd "ChatGPT, có tìm trên web") qua nhanNguon(). Bật tìm web bằng tuỳ chọn web/plugin của OpenRouter, có cờ OPENROUTER_WEB=1. Không có khoá thì provider tự tắt, app chạy như cũ (chỉ Gemini).
3. Tốc độ event: chạy song song các làn, timeout mỗi câu (BH_TIMEOUT_MS, mặc định 20000), một làn lỗi/chậm thì bỏ làn đó và ghi "không trả lời kịp", không chặn cả lượt; giữ hàng đợi + trần lượt/ngày hiện có. Thêm chế độ quét nhanh BH_QUICK=1: 6 câu đại diện (chọn trong bộ câu hiện có, ghi danh sách vào docs/PHUONG-PHAP.md) × mọi làn × 1 lượt.
4. Test (AI giả, không gọi mạng): provider bật/tắt theo biến; 1 làn treo → lượt vẫn xong trong timeout; nhãn nguồn không lộ mã thô (luật lint cũ phải xanh); quét nhanh đúng 6 câu. Thêm tên biến vào deploy/brand-health.env.example (chỉ tên, không giá trị). npm.cmd run verify xanh.
CẤM: gọi API thật, in/ghi khoá, deploy, đụng apps/event, apps/lab, packages/. Trạng thái cao nhất REVIEW.
KET-QUA.md: `dat: co|khong`; SHA; test mới; verify pass/fail.
