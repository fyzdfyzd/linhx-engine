May: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 40
khong_tien_phut: 10
theo_doi: C:\linhx\ifagent-wt\bhc-lite
nhan: may-2 2026-11-19T11:50:52+0700

Lưu ý máy: KHÔNG background task/subagent; KHÔNG chờ/ngủ dài; MỖI LỆNH PHẢI XONG TRONG 3 PHÚT. Commit + push agy/bhc-lite-1 sau mỗi bước. KHÔNG gọi AI thật, KHÔNG deploy trong phiếu này.
LINH YÊU CẦU (11:49 VN 19/11): "bật trên brandcheck và deploy domain, sau đó bật tính năng lite và để lại email để ifagent liên lạc -> full".
Ý nghĩa: khách tự quét trên brandcheck.ifagent.net chỉ nhận bản LITE. Muốn bản FULL thì để lại email (và SĐT tuỳ chọn) để IF Agent liên lạc; IF Agent mở Full cho từng báo cáo rồi gửi link.
Nhánh agy/bhc-lite-1 từ agy/bhc-sua-9 (5bbcb0c).
1. Cờ cấu hình BH_CHE_DO_KHACH=lite|full (mặc định full để không đổi hành vi cũ; prod sẽ đặt lite). Mỗi báo cáo có trường moFull (boolean). Báo cáo mẫu (đang hiện ở trang chủ: Vinamilk, IF Agent, và báo cáo quản trị đánh dấu "mẫu") luôn coi như moFull=true.
2. Khi lite và moFull=false:
   - Màn kết quả + landing /bao-cao/<mã>/: hiện đủ trang sốc (chương 01) + tóm tắt 60 giây (chương 02: 3 chỉ số, điều cần lưu ý nhất, ba việc). Các chương sau hiện tiêu đề + 1 dòng mô tả + lớp mờ khoá (không lộ số liệu trong HTML/JSON công khai — kiểm bằng test), kèm khối "Nhận bản Full" ở giữa và cuối trang.
   - Tải PDF: chỉ Light (4 trang). Đường /tai/full.pdf và API trả dữ liệu Full trả 403 với chữ thân thiện.
   - Khối "Nhận bản Full": form dùng lại form lead hiện có (họ tên, email bắt buộc, SĐT tuỳ chọn, đồng ý liên hệ), câu dẫn: "Để lại email, đội ngũ IF Agent sẽ liên lạc và gửi bản Full 40 trang cùng lộ trình 4 tuần." Gửi xong hiện lời cảm ơn rõ ràng. Lead gắn reportId.
3. Quản trị: danh sách lead có cột báo cáo + nút "Mở bản Full" cho báo cáo đó (đặt moFull=true) + nút "Sao chép link Full". Chi tiết lượt có công tắc Mở/Khoá Full và công tắc "Đánh dấu mẫu".
4. Link gốc dùng BH_URL_GOC (brandcheck.ifagent.net) cho link sao chép.
5. Chữ cho khách: không từ kỹ thuật, tiếng Việt có dấu đầy đủ, chữ ≥ 14px, nút ≥ 44px (theo lint hiện có).
6. Test khoá: lite + moFull=false → HTML/JSON công khai không chứa số liệu chương 03+, /tai/full.pdf 403, light 200; moFull=true → như cũ; full mode → như cũ; báo cáo mẫu luôn full; lead lưu reportId. npm test + node scripts/lint.js xanh, golden VNM/IFA không đổi.
7. Chụp chạy local (dữ liệu CSMO có sẵn ở bang-chung, không gọi AI): landing lite 1280 + 360, khối Nhận bản Full, lời cảm ơn sau gửi, quản trị lead với nút Mở bản Full — vào bang-chung/bhc-lite-1/.
KET-QUA: dat, SHA, số test, danh sách ảnh.

nhip: 12:11 21p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
