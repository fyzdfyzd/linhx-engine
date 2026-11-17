may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 25
khong_tien_phut: 20
theo_doi: C:\linhx\ifagent-wt\bhc-quan-tri
nhan: may-2 2026-11-17T12:54:48+0700
moc: 7b793e205524a8e9e9f862148117aff7438ecb85

Lưu ý máy: KHÔNG dùng background task, subagent hay thợ con; mọi lệnh chạy tiền cảnh. Gọi `npm.cmd`/`npx.cmd`. Commit + push mỗi 10 phút.
Sửa thư báo cáo (nhánh agy/bhc-quan-tri, đỉnh 7b793e2, git pull trước). Claude soi bang-chung/bhc-email/thu-html-360.png:
1. Link trong thư là đường dẫn tương đối "/bao-cao/<mã>/" và "/bao-cao/<mã>/tai/light.pdf": trong Gmail sẽ hỏng. Dùng URL tuyệt đối từ biến BH_URL_GOC (vd https://demo.ifagent.net/brand-health-check). Thiếu biến thì không gửi, trạng thái "chưa cấu hình địa chỉ trang".
2. Bỏ dòng in thô "Đường dẫn: /bao-cao/..." và "(/bao-cao/.../tai/light.pdf)" và "Mã báo cáo: 2026-11-13-..." ở đầu thư (mã kỹ thuật). Giữ nút "Mở báo cáo tương tác" và link chữ "Tải PDF Light".
3. Luật khoá trong test/thu.test.js + lint: HTML thư không được có href bắt đầu bằng "/" hoặc chữ "/bao-cao/" hiển thị; thông báo lỗi chỉ cách sửa ("Link tương đối trong thư: dùng urlTuyetDoi() với BH_URL_GOC"). Đỏ trên 7b793e2, xanh sau sửa.
4. test:lap 5/5, verify xanh. Ghi đè ảnh bang-chung/bhc-email/thu-html-600.png, thu-html-360.png.
CẤM: gửi thư thật, gọi Resend thật, deploy, đụng apps/event, apps/lab, packages/. Trạng thái cao nhất REVIEW.
KET-QUA.md: `dat: co|khong`; SHA; luật mới đỏ→xanh; verify.
