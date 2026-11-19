May: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 35
khong_tien_phut: 10
theo_doi: C:\linhx\ifagent-wt\bhc-mau-csmo-tc

Lưu ý máy: KHÔNG background task/subagent; KHÔNG chờ/ngủ dài; MỖI LỆNH PHẢI XONG TRONG 3 PHÚT. Push sau mỗi bước. KHÔNG gọi AI thật. KHÔNG in khoá/mã.
LINH (13:04 VN 19/11, nguyên văn "xoá thông tin ifagent, để csmo"), đã duyệt deploy prod từ trước ("tự động deploy đi"). Cách hiểu: ở trang chủ công cụ, khối "Số thật đã đo · bấm để đọc báo cáo mẫu đầy đủ" bỏ thẻ báo cáo mẫu IF Agent (0/33/27), thay bằng thẻ báo cáo mẫu CSMO. Giữ logo/chân trang IF Agent (chủ công cụ) và thẻ Vinamilk.
Nhánh agy/bhc-mau-csmo-tc từ agy/bhc-lite-1 (33cb800, đang chạy prod).
1. Thẻ mẫu trang chủ (public/index.html, public/trang-chu.html, public/quan-tri/dang-nhap.html, public/quan-tri/index.html và khung bao-cao/khung/B-trang-chu nếu test dựa vào): thay IF Agent bằng CSMO — tên "CSMO", dòng phụ "Cộng đồng giám đốc Sales & Marketing · 93/71/71", câu một dòng: "AI nhắc CSMO 76/82 lần hỏi chung, nhưng vẫn gán nhầm người đứng sau." (đối chiếu số thật từ GET /api/reports/2026-11-19-csmo-d88de79d trên prod; nếu số khác thì dùng số thật), 3 số Có mặt / Đúng / Đề xuất, link "Xem báo cáo mẫu CSMO →" tới bao-cao/2026-11-19-csmo-d88de79d/ (tương đối, không "/" đầu). Màu số theo quy tắc hiện có. Không còn chữ "IF Agent" như một thương hiệu được đo ở trang khách.
2. Trên prod, ẩn báo cáo mẫu IF Agent 2026-11-13-if-agent-3534b096 khỏi công khai (công tắc ẩn trong quản trị), kiểm link cũ trả 404 lịch sự. Đảm bảo CSMO d88de79d đánh dấu "mẫu" (luôn full).
3. Sửa test/golden liên quan trang chủ cho khớp (chỉ phần thẻ mẫu; ghi rõ test nào đổi). npm test + node scripts/lint.js xanh.
4. Deploy prod như phiếu bhc-prod-2 (sao lưu data -mau.tgz, git archive <sha>:apps/brand-health, scp, `sudo sh /opt/ifagent/infra/deploy-app.sh brand-health`), giữ env hiện tại (BH_CHE_DO_KHACH=lite...). Staging nâng cùng SHA.
5. Kiểm trình duyệt thật 1280 + 360 trên https://demo.ifagent.net/brand-health-check/ (và brandcheck.ifagent.net nếu DNS đã ra 34.87.102.182): 0 lỗi ≥ 400, thẻ CSMO mở được báo cáo full, thẻ Vinamilk mở được. Chụp trang chủ 1280 + 360 vào bang-chung/bhc-mau-csmo-tc/.
Hỏng: rollback :prev, kiểm 200, ghi rõ.
CẤM: đụng service khác, Caddy/DNS, in khoá, quét thật. KET-QUA: dat, SHA, test, ảnh.
