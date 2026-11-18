May: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 40
khong_tien_phut: 20
theo_doi: C:\linhx\ifagent-wt\bhc-sua-6
nhan: may-2 2026-11-19T05:58:23+0700

Lưu ý máy: KHÔNG background task/subagent; KHÔNG chờ/ngủ dài; MỖI LỆNH PHẢI XONG TRONG 3 PHÚT (lượt quét chạy trên máy chủ; kiểm trạng thái bằng lệnh ngắn `Start-Sleep 50; curl ...`). E2E chạy từng bước (--buoc). Push mỗi bước.
Linh yêu cầu (05:13 VN 19/11): "bỏ claude sang những AI rẻ hơn". Lượt đầy đủ CSMO tốn 6,96 USD, riêng làn Claude 5,02 USD (gọi thẳng Anthropic claude-opus-5-5 vì có ANTHROPIC_API_KEY).
Nhánh mới agy/bhc-sua-6 từ agy/bhc-sua-5 (5496af5, đã có sửa chụp số đếm, hộp lưu ý, Ba việc; 119 test xanh).
PHIẾU NÀY CHỈ LÀM CODE (bước 1–4), push agy/bhc-sua-6 sau mỗi bước. Bước staging + quét thật ở phiếu bhc-bo-claude-b.
1. Bỏ làn Claude khỏi mặc định: providers.js chỉ bật làn Claude khi BH_BAT_CLAUDE=1 (mặc định tắt, kể cả khi có ANTHROPIC_API_KEY); DEFAULT_OPENROUTER_MODELS bỏ anthropic/*. Giao diện khách, landing, PDF, quản trị không còn nhắc Claude khi làn tắt (báo cáo cũ có dữ liệu Claude vẫn hiển thị đúng).
2. Thêm 2 làn rẻ qua OpenRouter có tra web: DeepSeek và Grok. Lấy ID model mới nhất còn chạy từ GET https://openrouter.ai/api/v1/models (chọn bản chat thường, không phải bản suy luận dài; ghi ID + giá vào KET-QUA). openrouterId nhận họ 'deepseek' (deepseek/) và 'grok' (x-ai/); thêm vào TRO_LY (DeepSeek viet_tat 'D', Grok viet_tat 'X'), nhan-nguon.js, DANH_SACH_LAN_AI + công tắc quản trị, bảng giá ai-gia.js, chú thích nguồn. Nhãn cho khách: "DeepSeek, có tìm trên web", "Grok, có tìm trên web".
3. Test khoá: (a) mặc định không có làn Claude dù có ANTHROPIC_API_KEY; (b) có làn deepseek-tim và grok-tim khi có OPENROUTER_API_KEY; (c) mã hiển thị không còn '?' cho mọi làn; (d) ước tính chi phí lượt đầy đủ mặc định ≤ 2,5 USD theo bảng giá. npm test + node scripts/lint.js xanh; golden landing VNM/IFA không đổi.
4. Thử thật nhỏ trên máy (không qua staging): mỗi làn mới 3 câu CSMO, in chi phí usage.cost. Tổng ≤ 0,2 USD. Làn nào trả rỗng/lỗi thì đổi sang ID khác trong cùng họ, ghi lý do.
KET-QUA: dat, SHA, số test, ID + giá 2 model mới, chi phí thử nhỏ.

nhip: 06:35 37p đang chờ nền · log cuối 2 phút trước [log_cuoi=2026-11-19T06:33:01+0700] · root agent idle; waiting up to 40m0s for 1 ba
