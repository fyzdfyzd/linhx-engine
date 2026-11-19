May: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 40
khong_tien_phut: 20
theo_doi: C:\linhx\ifagent-wt\bhc-staging
phu_thuoc: bhc-bo-claude-a2
nhan: may-2 2026-11-19T06:54:55+0700
moc: f9f46c36561bcdd97447ae60cc0601eb930a42db

Lưu ý máy: KHÔNG background task/subagent; KHÔNG chờ/ngủ dài; MỖI LỆNH PHẢI XONG TRONG 3 PHÚT (lượt quét chạy trên máy chủ; kiểm trạng thái bằng lệnh ngắn `Start-Sleep 50; curl ...`). E2E chạy từng bước (--buoc). Push mỗi bước.
Linh yêu cầu (05:13 VN 19/11): "bỏ claude sang những AI rẻ hơn". Lượt đầy đủ CSMO tốn 6,96 USD, riêng làn Claude 5,02 USD (gọi thẳng Anthropic claude-opus-5-5 vì có ANTHROPIC_API_KEY).
Nhánh mới agy/bhc-sua-6 từ agy/bhc-sua-5 (5496af5, đã có sửa chụp số đếm, hộp lưu ý, Ba việc; 119 test xanh).
Code đã xong ở agy/bhc-sua-6 (phiếu bhc-bo-claude-a + a2; ID 2 model: deepseek/deepseek-v4.1-flash-1017 và x-ai/grok-4.7, đã là mặc định trong DEFAULT_OPENROUTER_MODELS). PHIẾU NÀY CHỈ LÀM STAGING, QUÉT THẬT, CHỤP (bước 5–8). Push agy/bhc-staging sau mỗi bước chụp.
5. Staging stg-brand: gộp vào agy/bhc-staging, sửa /opt/stg-brand/stg-brand.env (root 600): thêm OPENROUTER_MODELS=openai/gpt-5,google/gemini-2.5-flash,perplexity/sonar,<deepseek-id>,<grok-id> (giữ model openai/perplexity/gemini đang dùng nếu khác, đọc từ code hiện tại); KHÔNG xoá ANTHROPIC_API_KEY, chỉ để BH_BAT_CLAUDE không đặt. Recreate STG_SHA=<sha mới> docker compose -p stg-brand up -d --force-recreate; healthz đúng SHA. Mã quản trị: `sudo cat /opt/stg-brand/ADMIN_CODE.txt` vào biến, không in.
6. Quét thật lại CSMO đầy đủ 1 lượt qua giao diện (BH_QUICK=0 và BH_TRAN_CHI_PHI_NGAY=300000 tạm thời, ghi giá trị cũ, trả lại sau). Dùng bảng sự thật đã có ở bang-chung/bhc-mau-csmo/su-that.md. Trần OpenRouter cho phiếu: 3 USD (kiểm GET https://openrouter.ai/api/v1/key usage trước/sau, chỉ in usage). Xuất bản báo cáo.
7. Chụp vào bang-chung/bhc-mau-csmo-v2/: trang chủ, bảng sự thật, đang quét, kết quả, landing full + chương 01–13 (chờ số đếm xong) ở 1280 và 360 sáng, landing đêm full, xem nguyên văn, form email, quản trị tổng quan / lượt quét / chi tiết lượt (chi phí từng làn) / lead; PDF Full + Light ra PNG 150 dpi. JPG 90 nếu > 40 MB. Push agy/bhc-staging.
8. Trả cấu hình BH_QUICK, BH_TRAN_CHI_PHI_NGAY; healthz ok; demo.ifagent.net/brand-health-check/ và event.ifagent.net 200.
CẤM: deploy prod, sửa /opt/ifagent, stg-event, Caddy, rollback-app.sh, in khoá/mã quản trị, quét thương hiệu khác. KET-QUA: dat, SHA, số test, ID + giá 2 model mới, mã báo cáo mới, 3 chỉ số, thời gian, chi phí từng làn (USD), tổng USD, danh sách ảnh.

nhip: 07:10 15p đang chờ nền · log cuối 0 phút trước [log_cuoi=2026-11-19T07:10:18+0700] · root agent idle; waiting up to 40m0s for 1 ba
