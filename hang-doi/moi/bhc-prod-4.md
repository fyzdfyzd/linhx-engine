May: may-3
loai: code
model: gemini-4-argon-high
tran_phut: 45
khong_tien_phut: 10
theo_doi: D:\linhx\ifagent-wt\bhc-prod-4

Bước 0: kiểm `gcloud compute ssh ifagent-event --zone=asia-southeast1-b --project=ifagent-event-2026 --command="echo ok"`; nếu không chạy được thì chỉ làm bước 1–2 (code + thử nhỏ), push, DỪNG, ghi "can gcloud".
Lưu ý máy: KHÔNG background task/subagent; KHÔNG chờ/ngủ dài; MỖI LỆNH PHẢI XONG TRONG 3 PHÚT. Push sau mỗi bước.
LINH DUYỆT (09:28 VN 19/11: "ko để trần cho tôi, chạy 1 báo cáo mẫu"; 09:21 VN 19/11, nguyên văn "đồng ý, chuyển sang mini"): (a) chép khoá OpenRouter vào production để có đủ ChatGPT, Perplexity, DeepSeek, Grok; (b) đổi làn ChatGPT sang bản mini.
Điều kiện chạy: phiếu bhc-prod-3b-gap đã push agy/bhc-sua-8 và prod trang chủ đã sửa (đọc KET-QUA của nó hoặc kiểm https://demo.ifagent.net/brand-health-check/chung/landing.css 200 và trang chủ không còn `../chung/`). Nếu chưa, DỪNG và ghi KET-QUA.
Nhánh agy/bhc-sua-9 từ agy/bhc-sua-8.
1. Lấy ID mini mới nhất của OpenAI trên GET https://openrouter.ai/api/v1/models (vd openai/gpt-5-mini hoặc bản mini mới hơn; ghi ID + giá). Đổi DEFAULT_OPENROUTER_MODELS: openai/gpt-5 → ID mini; cập nhật bảng giá ai-gia.js và test ước tính chi phí (lượt đầy đủ mặc định ≤ 2,2 USD). npm test + lint xanh, golden VNM/IFA không đổi. Push.
2. Thử thật nhỏ 3 câu CSMO bằng ID mini qua OpenRouter (≤ 0,05 USD), ghi thời gian + chi phí.
3. Deploy prod mã mới như phiếu bhc-prod-2 (sao lưu data -d.tgz; git archive <sha>:apps/brand-health; scp; `sudo sh /opt/ifagent/infra/deploy-app.sh brand-health`).
4. Env prod /opt/ifagent/infra/brand-health.env (giữ quyền như cũ, sao lưu file trước thành brand-health.env.bak-19-11 cùng quyền): chép NGAY TRÊN VM các dòng OPENROUTER_API_KEY, BH_GIA_OPENROUTER, BH_TY_GIA, BH_TIMEOUT_MS_OPENAI_TIM, BH_GIA_GEMINI_TIM, BH_GIA_GEMINI_NHO từ /opt/stg-brand/stg-brand.env (dùng sudo grep >> , KHÔNG in giá trị ra màn hình/log/KET-QUA). Thêm OPENROUTER_MODELS=<mini-id>,google/gemini-2.5-flash,perplexity/sonar,deepseek/deepseek-v4.1-flash-1017,x-ai/grok-4.7. Giữ BH_QUICK=1. BỎ TRẦN theo lệnh Linh (09:28 VN, "ko để trần cho tôi"): đặt BH_TRAN_CHI_PHI_NGAY=1000000000 (mức tối đa code cho phép). KHÔNG đặt BH_BAT_CLAUDE. Sau đó `cd /opt/ifagent/infra && sudo docker compose up -d --force-recreate brand-health` (chỉ service này), healthz 200.
5. Staging: env stg-brand cũng đổi OPENROUTER_MODELS sang mini, nâng lên SHA mới, healthz đúng SHA.
6. Kiểm prod: trang quản trị prod (mã đọc bằng sudo vào biến, không in) mục Cài đặt hiển thị các làn ChatGPT mini, Gemini OR, Perplexity, DeepSeek, Grok đang bật; trang chủ 200, CSS 200, 0 yêu cầu 404. event/lab/bd giữ HTTP. Chụp trang Cài đặt quản trị prod 1280 vào bang-chung/bhc-prod-4/ trên agy/bhc-prod-4.
7. Hỏng thì rollback image :prev và khôi phục brand-health.env.bak-19-11, kiểm 200, ghi rõ.
6b. BÁO CÁO MẪU TRÊN PROD (Linh yêu cầu): tạm đặt BH_QUICK=0 trong brand-health.env, recreate brand-health. Quét thật đầy đủ CSMO đúng 1 lượt qua giao diện https://demo.ifagent.net/brand-health-check/ như khách (ngành "Cộng đồng giám đốc Sales & Marketing", web csmovietnam.com, bảng sự thật lấy đúng từ ifagent nhánh agy/bhc-staging bang-chung/bhc-mau-csmo/su-that.md). Theo dõi bằng lệnh ngắn đến xong. Vào quản trị prod: xuất bản công khai. Ghi usage OpenRouter trước/sau (GET https://openrouter.ai/api/v1/key, chỉ in usage). Trả BH_QUICK=1, recreate, healthz 200.
6c. Chụp vào bang-chung/bhc-prod-4/: trang chủ 1280 + 360, landing báo cáo CSMO prod full 1280 + 360 (chờ số đếm xong), chương 01–02 1280, PDF Full trang 1–3 và Light trang 1 (150 dpi), quản trị chi tiết lượt (chi phí từng làn) 1280. Ghi link công khai báo cáo vào KET-QUA.
CẤM: đụng service khác, Caddy/DNS, in khoá/mã, quét thương hiệu khác, quét quá 1 lượt (tối đa 1 lần chạy lại nếu lỗi mạng). KET-QUA: dat, SHA, ID mini + giá, chi phí thử, link báo cáo CSMO prod, 3 chỉ số, thời gian quét, chi phí từng làn và tổng USD, danh sách TÊN env prod sau, ảnh.
