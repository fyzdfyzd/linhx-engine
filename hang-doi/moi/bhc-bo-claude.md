May: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 75
khong_tien_phut: 20
theo_doi: C:\linhx\ifagent-wt\bhc-staging
phu_thuoc: bhc-mau-csmo-sua

Lưu ý máy: KHÔNG background task/subagent; KHÔNG chờ/ngủ dài; MỖI LỆNH PHẢI XONG TRONG 3 PHÚT (lượt quét chạy trên máy chủ; kiểm trạng thái bằng lệnh ngắn `Start-Sleep 50; curl ...`). E2E chạy từng bước (--buoc). Push mỗi bước.
Linh yêu cầu (05:13 VN 19/11): "bỏ claude sang những AI rẻ hơn". Lượt đầy đủ CSMO tốn 6,96 USD, riêng làn Claude 5,02 USD (gọi thẳng Anthropic claude-opus-5-5 vì có ANTHROPIC_API_KEY).
Nhánh mới agy/bhc-sua-6 từ agy/bhc-sua-5 (phiếu bhc-mau-csmo-sua).
1. Bỏ làn Claude khỏi mặc định: providers.js chỉ bật làn Claude khi BH_BAT_CLAUDE=1 (mặc định tắt, kể cả khi có ANTHROPIC_API_KEY); DEFAULT_OPENROUTER_MODELS bỏ anthropic/*. Giao diện khách, landing, PDF, quản trị không còn nhắc Claude khi làn tắt (báo cáo cũ có dữ liệu Claude vẫn hiển thị đúng).
2. Thêm 2 làn rẻ qua OpenRouter có tra web: DeepSeek và Grok. Lấy ID model mới nhất còn chạy từ GET https://openrouter.ai/api/v1/models (chọn bản chat thường, không phải bản suy luận dài; ghi ID + giá vào KET-QUA). openrouterId nhận họ 'deepseek' (deepseek/) và 'grok' (x-ai/); thêm vào TRO_LY (DeepSeek viet_tat 'D', Grok viet_tat 'X'), nhan-nguon.js, DANH_SACH_LAN_AI + công tắc quản trị, bảng giá ai-gia.js, chú thích nguồn. Nhãn cho khách: "DeepSeek, có tìm trên web", "Grok, có tìm trên web".
3. Test khoá: (a) mặc định không có làn Claude dù có ANTHROPIC_API_KEY; (b) có làn deepseek-tim và grok-tim khi có OPENROUTER_API_KEY; (c) mã hiển thị không còn '?' cho mọi làn; (d) ước tính chi phí lượt đầy đủ mặc định ≤ 2,5 USD theo bảng giá. npm test + node scripts/lint.js xanh; golden landing VNM/IFA không đổi.
4. Thử thật nhỏ trên máy (không qua staging): mỗi làn mới 3 câu CSMO, in chi phí usage.cost. Tổng ≤ 0,2 USD. Làn nào trả rỗng/lỗi thì đổi sang ID khác trong cùng họ, ghi lý do.
5. Staging stg-brand: gộp vào agy/bhc-staging, sửa /opt/stg-brand/stg-brand.env (root 600): thêm OPENROUTER_MODELS=openai/gpt-5,google/gemini-2.5-flash,perplexity/sonar,<deepseek-id>,<grok-id> (giữ model openai/perplexity/gemini đang dùng nếu khác, đọc từ code hiện tại); KHÔNG xoá ANTHROPIC_API_KEY, chỉ để BH_BAT_CLAUDE không đặt. Recreate STG_SHA=<sha mới> docker compose -p stg-brand up -d --force-recreate; healthz đúng SHA. Mã quản trị: `sudo cat /opt/stg-brand/ADMIN_CODE.txt` vào biến, không in.
6. Quét thật lại CSMO đầy đủ 1 lượt qua giao diện (BH_QUICK=0 và BH_TRAN_CHI_PHI_NGAY=300000 tạm thời, ghi giá trị cũ, trả lại sau). Dùng bảng sự thật đã có ở bang-chung/bhc-mau-csmo/su-that.md. Trần OpenRouter cho phiếu: 3 USD (kiểm GET https://openrouter.ai/api/v1/key usage trước/sau, chỉ in usage). Xuất bản báo cáo.
7. Chụp vào bang-chung/bhc-mau-csmo-v2/: trang chủ, bảng sự thật, đang quét, kết quả, landing full + chương 01–13 (chờ số đếm xong) ở 1280 và 360 sáng, landing đêm full, xem nguyên văn, form email, quản trị tổng quan / lượt quét / chi tiết lượt (chi phí từng làn) / lead; PDF Full + Light ra PNG 150 dpi. JPG 90 nếu > 40 MB. Push agy/bhc-staging.
8. Trả cấu hình BH_QUICK, BH_TRAN_CHI_PHI_NGAY; healthz ok; demo.ifagent.net/brand-health-check/ và event.ifagent.net 200.
CẤM: deploy prod, sửa /opt/ifagent, stg-event, Caddy, rollback-app.sh, in khoá/mã quản trị, quét thương hiệu khác. KET-QUA: dat, SHA, số test, ID + giá 2 model mới, mã báo cáo mới, 3 chỉ số, thời gian, chi phí từng làn (USD), tổng USD, danh sách ảnh.
