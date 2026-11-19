May: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 30
khong_tien_phut: 10
theo_doi: C:\linhx\ifagent-wt\bhc-lite-deploy-c
nhan: may-2 2026-11-19T12:36:22+0700

Lưu ý máy: KHÔNG background task/subagent; KHÔNG chờ/ngủ dài; MỖI LỆNH PHẢI XONG TRONG 3 PHÚT. Push KET-QUA + ảnh vào bang-chung/bhc-lite-1c/ trên nhánh agy/bhc-lite-1c sau mỗi bước. KHÔNG in khoá/mã. KHÔNG gọi AI thật.
LINH (12:00 VN 19/11): "tự động deploy đi" — deploy chế độ Lite lên production, không cần chờ duyệt.
Điều kiện đã đủ: bhc-lite-1a xong, Claude đã kiểm agy/bhc-lite-1 33cb800 (129/129 test, lint ok); bhc-prod-5b và bhc-prod-6 xong. Không có phiếu quét nào đang chạy. Deploy đúng SHA 33cb800.
1. Sao lưu data prod (backup-brand-health-data-19-11-lite.tgz) và brand-health.env (.bak-19-11-lite).
2. Deploy SHA cuối agy/bhc-lite-1 lên prod như phiếu bhc-prod-2 (git archive, scp, `sudo sh /opt/ifagent/infra/deploy-app.sh brand-health`).
3. Thêm BH_CHE_DO_KHACH=lite và BH_TIMEOUT_MS_GEMINI_TIM=45000 (Gemini có tra Google bị quá giờ 4/42 ở 20 s) vào /opt/ifagent/infra/brand-health.env, recreate CHỈ brand-health, healthz 200.
4. Đánh dấu "mẫu" (moFull) cho báo cáo mẫu Vinamilk, IF Agent và báo cáo CSMO mới của phiếu bhc-prod-5b (nếu có) qua quản trị.
5. Staging stg-brand cũng nâng SHA đó và BH_CHE_DO_KHACH=lite, healthz đúng SHA.
6. Kiểm bằng trình duyệt thật trên https://demo.ifagent.net/brand-health-check/ (và https://brandcheck.ifagent.net/ nếu DNS đã trỏ 34.87.102.182): trang chủ 0 lỗi 404; báo cáo mẫu mở full; một báo cáo khách cũ không phải mẫu (vd 2026-10-16-vinamilk-88ac335e nếu có) hiện bản Lite, /tai/full.pdf 403, light 200; gửi thử form "Nhận bản Full" với tên "TEST Claude", email test@ifagent.net, rồi vào quản trị thấy lead gắn báo cáo, bấm "Mở bản Full" thì link Full mở được; sau đó XOÁ lead test và khoá Full lại cho báo cáo đó. event/bd/lab giữ HTTP.
7. Chụp 1280 + 360: landing Lite, khối Nhận bản Full, lời cảm ơn, quản trị lead.
Hỏng: rollback image :prev + khôi phục env .bak, kiểm 200, ghi rõ.
CẤM: đụng service khác, Caddy/DNS, in khoá, quét thật. KET-QUA: dat, SHA, kết quả bước 6, ảnh.

nhip: 12:48 12p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
