May: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 40
khong_tien_phut: 10
theo_doi: C:\linhx\ifagent-wt\bhc-prod-4
nhan: may-2 2026-11-19T11:46:48+0700
moc: db102a722ee58c3c5f691b94e8291cf278332f67

Lưu ý máy: KHÔNG background task/subagent; KHÔNG chờ/ngủ dài; MỖI LỆNH PHẢI XONG TRONG 3 PHÚT (theo dõi lượt quét bằng lệnh ngắn `Start-Sleep 50; curl ...`). Push KET-QUA + ảnh vào bang-chung/bhc-prod-5b/ trên nhánh agy/bhc-prod-5b sau mỗi bước. KHÔNG in khoá/mã.
Linh (11:45 VN 19/11): "đã mở" (Gemini đã mở lại / nạp tiền). Linh đã yêu cầu chạy 1 báo cáo mẫu trên production, không trần (09:28).
0. Trong container ifagent-brand-health-1 gọi thử Gemini 1 câu (như phiếu bhc-prod-5a bước 1, có và không có google_search). Nếu vẫn 402/lỗi: DỪNG, ghi nguyên văn status/message.
1. Tạm BH_QUICK=0 trong /opt/ifagent/infra/brand-health.env, recreate CHỈ brand-health, healthz 200.
2. Quét thật CSMO đầy đủ đúng 1 lượt qua giao diện https://demo.ifagent.net/brand-health-check/ như khách (tên CSMO, ngành "Cộng đồng giám đốc Sales & Marketing", web csmovietnam.com; bảng sự thật đúng như ifagent nhánh agy/bhc-staging bang-chung/bhc-mau-csmo/su-that.md, điền đủ mọi dòng). Ghi usage OpenRouter trước/sau (chỉ usage). Khi xong: kiểm 2 làn gemini-tim/gemini-nho có đủ câu trả lời và chỉ số Đúng KHÁC null; nếu Đúng null hoặc Gemini lỗi > 10% thì ẩn báo cáo, ghi rõ, DỪNG (không quét lại).
3. Quản trị prod: xuất bản công khai báo cáo mới. Trả BH_QUICK=1, recreate brand-health, healthz 200.
4. Chụp (chờ số đếm xong): landing báo cáo full 1280 + 360 (sáng), chương 01–02 1280, PDF Full trang 1–3 + Light trang 1 (150 dpi), quản trị chi tiết lượt 1280 (chi phí từng làn). Tải PDF Full + Light vào bang-chung/bhc-prod-5b/pdf/. Nếu https://brandcheck.ifagent.net/ đã chạy thì chụp thêm landing báo cáo qua tên miền này 1280.
CẤM: quét quá 1 lượt (tối đa 1 lần chạy lại nếu lỗi mạng trước khi có câu trả lời), quét thương hiệu khác, đụng service khác, Caddy/DNS, in khoá. KET-QUA: dat, mã + link báo cáo, 3 chỉ số, thời gian, chi phí từng làn + tổng USD, ảnh.

nhip: 11:49 3p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
