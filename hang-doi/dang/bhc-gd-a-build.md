May: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 75
khong_tien_phut: 10
theo_doi: C:\linhx\ifagent-wt\bhc-gd-a
nhan: may-2 2026-11-19T21:56:22+0700

Lưu ý máy: KHÔNG background task/subagent; MỖI LỆNH XONG TRONG 3 PHÚT. KHÔNG in/ghi/commit khoá hay ADMIN_CODE. Không đụng service khác, DNS, Caddy, stg-event.
Linh (21:53 VN 19/11) đã DUYỆT phương án A (apps/brand-health/phac-thao/pa-a.html trên nhánh agy/bhc-gd-1 3e7216a). Linh đã cho phép tự deploy prod.
Nhánh mới agy/bhc-gd-a tách từ agy/bhc-gd-1.
1. Đưa bố cục PA A vào apps/brand-health/public/index.html (trang chủ thật), giữ: logo, đường dẫn tương đối (chung/..., bao-cao/... — KHÔNG dùng ../ hay / đầu, đã có test sua-8), dải 2 thẻ mẫu Vinamilk + CSMO, chế độ Sáng/Đêm. Ảnh anh-pa-a.jpg chuyển vào public/chung/ (nén ≤250 KB, giữ tỉ lệ, không crop). Nút CTA màn đầu cuộn tới form.
2. Ô Email bắt buộc (kiểm định dạng) + Số điện thoại tuỳ chọn gửi kèm yêu cầu quét; server lưu vào bản ghi báo cáo, hiện ở trang quản trị (cột Email/SĐT cạnh lead "Nhận bản Full"). Không hiện email/SĐT trên trang báo cáo công khai, PDF hay link chia sẻ.
3. Test khoá mới: trang chủ có ô email required; thiếu email → server trả 400 có thông báo tiếng Việt; email lưu vào bản ghi và có trong API quản trị; trang báo cáo công khai không chứa email. Toàn bộ test brand-health phải xanh (trước đó 129).
4. Commit, push nhánh agy/bhc-gd-a lên fyzdfyzd/ifagent. Deploy staging rồi prod theo cách cũ (đóng gói /tmp/brand-health-app.tgz, `sudo sh /opt/ifagent/infra/deploy-app.sh brand-health` trên VM ifagent-event). Không dùng rollback-app.sh cho staging.
5. Kiểm prod bằng playwright: https://demo.ifagent.net/brand-health-check/ và https://brandcheck.ifagent.net/ ở 1280x900 + 360 toàn trang, 0 yêu cầu lỗi ≥400; thử gửi form thiếu email (phải báo lỗi, KHÔNG chạy quét thật để khỏi tốn tiền). Lưu ảnh vào bang-chung/bhc-gd-a/ và push.
KET-QUA: SHA, số test, ảnh, mã đang chạy trên prod (:prev là gì).

nhip: 22:14 18p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
