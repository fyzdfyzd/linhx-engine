May: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 30
khong_tien_phut: 10
theo_doi: C:\linhx\ifagent-wt\bhc-lite-deploy

Lưu ý máy: KHÔNG background task/subagent; KHÔNG chờ/ngủ dài; MỖI LỆNH PHẢI XONG TRONG 3 PHÚT. Push KET-QUA + ảnh vào bang-chung/bhc-lite-1b/ trên nhánh agy/bhc-lite-1b sau mỗi bước. KHÔNG in khoá/mã. KHÔNG gọi AI thật.
LINH (12:00 VN 19/11): "tự động deploy đi" — deploy chế độ Lite lên production, không cần chờ duyệt.
Điều kiện: phiếu bhc-lite-1a đã xong với dat và nhánh agy/bhc-lite-1 có test xanh (tự chạy lại npm test + lint ở SHA cuối, phải 0 hỏng). Phiếu bhc-prod-5b (quét CSMO prod) phải đã xong (xem hang-doi/xong/bhc-prod-5b) để không recreate giữa lượt quét. Chưa đủ thì DỪNG, ghi lý do.
1. Sao lưu data prod (backup-brand-health-data-19-11-lite.tgz) và brand-health.env (.bak-19-11-lite).
2. Deploy SHA cuối agy/bhc-lite-1 lên prod như phiếu bhc-prod-2 (git archive, scp, `sudo sh /opt/ifagent/infra/deploy-app.sh brand-health`).
3. Thêm BH_CHE_DO_KHACH=lite vào /opt/ifagent/infra/brand-health.env, recreate CHỈ brand-health, healthz 200.
4. Đánh dấu "mẫu" (moFull) cho báo cáo mẫu Vinamilk, IF Agent và báo cáo CSMO mới của phiếu bhc-prod-5b (nếu có) qua quản trị.
5. Staging stg-brand cũng nâng SHA đó và BH_CHE_DO_KHACH=lite, healthz đúng SHA.
6. Kiểm bằng trình duyệt thật trên https://demo.ifagent.net/brand-health-check/ (và https://brandcheck.ifagent.net/ nếu DNS đã trỏ 34.87.102.182): trang chủ 0 lỗi 404; báo cáo mẫu mở full; một báo cáo khách cũ không phải mẫu (vd 2026-10-16-vinamilk-88ac335e nếu có) hiện bản Lite, /tai/full.pdf 403, light 200; gửi thử form "Nhận bản Full" với tên "TEST Claude", email test@ifagent.net, rồi vào quản trị thấy lead gắn báo cáo, bấm "Mở bản Full" thì link Full mở được; sau đó XOÁ lead test và khoá Full lại cho báo cáo đó. event/bd/lab giữ HTTP.
7. Chụp 1280 + 360: landing Lite, khối Nhận bản Full, lời cảm ơn, quản trị lead.
Hỏng: rollback image :prev + khôi phục env .bak, kiểm 200, ghi rõ.
CẤM: đụng service khác, Caddy/DNS, in khoá, quét thật. KET-QUA: dat, SHA, kết quả bước 6, ảnh.
