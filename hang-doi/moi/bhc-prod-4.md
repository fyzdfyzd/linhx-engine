May: may-4
loai: code
model: gemini-4-argon-high
tran_phut: 35
khong_tien_phut: 10
theo_doi: D:\LINHX\PRJ\IFAGENT-wt\bhc-prod-4

Lưu ý máy: KHÔNG background task/subagent; KHÔNG chờ/ngủ dài; MỖI LỆNH PHẢI XONG TRONG 3 PHÚT. Push sau mỗi bước.
LINH DUYỆT (09:21 VN 19/11, nguyên văn "đồng ý, chuyển sang mini"): (a) chép khoá OpenRouter vào production để có đủ ChatGPT, Perplexity, DeepSeek, Grok; (b) đổi làn ChatGPT sang bản mini.
Điều kiện chạy: phiếu bhc-prod-3b-gap đã push agy/bhc-sua-8 và prod trang chủ đã sửa (đọc KET-QUA của nó hoặc kiểm https://demo.ifagent.net/brand-health-check/chung/landing.css 200 và trang chủ không còn `../chung/`). Nếu chưa, DỪNG và ghi KET-QUA.
Nhánh agy/bhc-sua-9 từ agy/bhc-sua-8.
1. Lấy ID mini mới nhất của OpenAI trên GET https://openrouter.ai/api/v1/models (vd openai/gpt-5-mini hoặc bản mini mới hơn; ghi ID + giá). Đổi DEFAULT_OPENROUTER_MODELS: openai/gpt-5 → ID mini; cập nhật bảng giá ai-gia.js và test ước tính chi phí (lượt đầy đủ mặc định ≤ 2,2 USD). npm test + lint xanh, golden VNM/IFA không đổi. Push.
2. Thử thật nhỏ 3 câu CSMO bằng ID mini qua OpenRouter (≤ 0,05 USD), ghi thời gian + chi phí.
3. Deploy prod mã mới như phiếu bhc-prod-2 (sao lưu data -d.tgz; git archive <sha>:apps/brand-health; scp; `sudo sh /opt/ifagent/infra/deploy-app.sh brand-health`).
4. Env prod /opt/ifagent/infra/brand-health.env (giữ quyền như cũ, sao lưu file trước thành brand-health.env.bak-19-11 cùng quyền): chép NGAY TRÊN VM các dòng OPENROUTER_API_KEY, BH_GIA_OPENROUTER, BH_TY_GIA, BH_TIMEOUT_MS_OPENAI_TIM, BH_GIA_GEMINI_TIM, BH_GIA_GEMINI_NHO từ /opt/stg-brand/stg-brand.env (dùng sudo grep >> , KHÔNG in giá trị ra màn hình/log/KET-QUA). Thêm OPENROUTER_MODELS=<mini-id>,google/gemini-2.5-flash,perplexity/sonar,deepseek/deepseek-v4.1-flash-1017,x-ai/grok-4.7. Giữ BH_QUICK=1 và BH_TRAN_CHI_PHI_NGAY=50000. KHÔNG đặt BH_BAT_CLAUDE. Sau đó `cd /opt/ifagent/infra && sudo docker compose up -d --force-recreate brand-health` (chỉ service này), healthz 200.
5. Staging: env stg-brand cũng đổi OPENROUTER_MODELS sang mini, nâng lên SHA mới, healthz đúng SHA.
6. Kiểm prod KHÔNG quét thật: trang quản trị prod (mã đọc bằng sudo vào biến, không in) mục Cài đặt hiển thị các làn ChatGPT mini, Gemini OR, Perplexity, DeepSeek, Grok đang bật; trang chủ 200, CSS 200, 0 yêu cầu 404. event/lab/bd giữ HTTP. Chụp trang Cài đặt quản trị prod 1280 vào bang-chung/bhc-prod-4/ trên agy/bhc-prod-4.
7. Hỏng thì rollback image :prev và khôi phục brand-health.env.bak-19-11, kiểm 200, ghi rõ.
CẤM: đụng service khác, Caddy/DNS, in khoá/mã, quét thật trên prod. KET-QUA: dat, SHA, ID mini + giá, chi phí thử, danh sách TÊN env prod sau, ảnh.
