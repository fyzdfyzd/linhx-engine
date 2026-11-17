may: may-2
loai: khac
tran_phut: 20
theo_doi: C:\linhx\nhat-ky\yl-do-chi-phi-gemini
nhan: may-2 2026-11-18T04:46:56+0700

Linh duyệt 18/11 04:46 (thẻ quyết định: "Cho máy 2 đọc sổ"). Linh hỏi: vì sao chi phí Gemini mấy hôm nay cao, có phải do test? CHỈ ĐỌC, không sửa gì, không deploy, không in khoá/mật khẩu. Lệnh tiền cảnh, không background task. Ghi tiến độ vào `C:\linhx\nhat-ky\yl-do-chi-phi-gemini\tien-do.log`.
1. Đăng nhập admin bằng tài khoản test-btc có sẵn trên máy, gọi `/api/yl/v1/qt/chi-phi?nhom=ngay|tinh-nang|may&tu=2026-11-10&den=2026-11-18` trên prod (demo.ifagent.net) và staging. Không đăng nhập được thì đọc file sổ chi phí (do `apps/lab/server/v1/chi-phi/so-chi-phi.js` ghi) trên VM qua `gcloud compute ssh` như khi deploy, chỉ đọc.
2. Bảng 10/11 → 18/11: USD mỗi ngày; theo tính năng (Live kiosk, bìa ảnh, chat chữ, tạp chí, lọc an toàn, khác); theo nguồn: máy/IP nội bộ (máy 1/2/3, VM, test, staging) vs khách thật. Top 10 giờ tốn nhất và nguồn gọi.
3. Kiểm test/E2E nào gọi Gemini THẬT (rc7-chi-phi-live, e2e kiosk/booth, tạo bìa); khoá staging có trùng prod không (chỉ trả lời có/không).
4. Nếu máy có quyền Cloud Billing / AI Studio thì lấy số tiền thật theo ngày, không thì ghi KHONG_CO_QUYEN.
KET-QUA.md ≤ 1500 ký tự: bảng ngày, bảng tính năng, % test/nội bộ vs khách, 3 nguyên nhân lớn nhất có số, đề xuất cắt.

nhip: 04:56 9p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
