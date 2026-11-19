May: may-4
loai: code
model: gemini-4-argon-high
tran_phut: 30
khong_tien_phut: 10
theo_doi: D:\LINHX\PRJ\IFAGENT-wt\bhc-prod-3

Lưu ý máy: KHÔNG background task/subagent; KHÔNG chờ/ngủ dài; MỖI LỆNH PHẢI XONG TRONG 3 PHÚT. Push sau mỗi bước. GẤP: đây là trang QR của bài nói. Chạy trên MSI (may-4) vì máy 2 hết hạn mức agy. Bước 0: kiểm `gcloud compute ssh ifagent-event --zone=asia-southeast1-b --project=ifagent-event-2026 --command="echo ok"` chạy được; nếu không thì DỪNG ngay, ghi KET-QUA. Ổ C MSI gần đầy: làm việc trên ổ D.
Linh đã duyệt deploy production (08:14 VN 19/11). Prod đang chạy b8c4b7ba nhưng TRANG CHỦ https://demo.ifagent.net/brand-health-check/ HỎNG GIAO DIỆN: Claude kiểm, `../chung/landing.css` và `../chung/logo/grad-notag.png` ra 404 (trình duyệt đổi thành /chung/...), trang hiện chữ trơn, logo vỡ. Link báo cáo mẫu `href="/bao-cao/2026-11-13-vinamilk-9b816db5/"` và `/bao-cao/2026-11-13-if-agent-bf460a21/` là đường tuyệt đối gốc → 404, và 2 mã này không có trong dữ liệu prod (prod có 2026-11-13-vinamilk-128ac969, 2026-11-13-if-agent-3534b096).
Nhánh agy/bhc-sua-8 từ agy/bhc-sua-7 (b8c4b7ba).
1. Sửa mọi đường dẫn trong apps/brand-health/public/**/*.html, *.js, *.css cho đúng khi app chạy dưới tiền tố /brand-health-check/ VÀ chạy ở gốc (staging 127.0.0.1:3920/): trang ở gốc public dùng `chung/...`, `bao-cao/...` (tương đối, không `../`, không `/` đầu). Kiểm cả quản trị /quan-tri/ và landing /bao-cao/<mã>/ (đã đúng, giữ nguyên).
2. Link báo cáo mẫu ở trang chủ: lấy mã từ cấu hình/API (báo cáo mẫu đang xuất bản trên chính máy chủ đó), không mã cứng; nếu không có thì ẩn khối link, không để link chết. Trên prod sau deploy phải mở được báo cáo mẫu Vinamilk và IF Agent (dùng mã có sẵn trên prod; nếu cần, cho phép đặt qua biến env BH_MAU_VINAMILK / BH_MAU_IFAGENT, ghi vào brand-health.env prod).
3. Test khoá mới (chạy trong npm test): dựng server, gọi GET /brand-health-check/ qua một proxy tiền tố giả (hoặc phân tích HTML), mọi href/src nội bộ trong mọi trang public phải trả 200 khi đặt dưới /brand-health-check/ và dưới gốc. Thêm luật lint: cấm `href="/` và `src="/` và `../chung/` trong public/*.html gốc.
4. npm test + node scripts/lint.js xanh (≥124 + test mới). Commit, push agy/bhc-sua-8.
5. Deploy prod như phiếu bhc-prod-2 (sao lưu data -c.tgz, git archive <sha>:apps/brand-health, scp, `sudo sh /opt/ifagent/infra/deploy-app.sh brand-health`). Sau đó kiểm bằng trình duyệt thật: https://demo.ifagent.net/brand-health-check/ có CSS + logo (không ảnh vỡ), 0 yêu cầu 404 trong tab mạng; bấm 2 link báo cáo mẫu → 200 có giao diện. event/lab/bd giữ HTTP như cũ. Chụp trang chủ prod 1280 + 360 sáng và báo cáo mẫu Vinamilk 1280 vào bang-chung/bhc-prod-3/ trên agy/bhc-prod-3. Staging cũng nâng lên SHA mới.
6. Nếu prod hỏng sau deploy: rollback về :prev, kiểm 200, ghi rõ.
CẤM: đụng service khác, Caddy/DNS, in khoá/mã, quét thật. KET-QUA: dat, SHA, số test, danh sách 404 trước/sau, ảnh.
