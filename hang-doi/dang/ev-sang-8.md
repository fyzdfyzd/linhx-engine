may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
theo_doi: C:\linhx\ifagent-wt\ev-sang-8
nhan: may-2 2026-11-17T05:13:47+0700

Phiếu cụm event.ifagent.net (ev-sang-8): bổ sung GIAO DIỆN SÁNG (anh Linh yêu cầu 17/11). Tham chiếu: C:\linhx\hang-doi\viec\event-ifagent\khung\ (bang-ghep-b-1440.png, bang-ghep-b-390.png = hướng B nền Giấy; TK-1-HAI-HUONG.md).
0. `git -C C:\linhx\ifagent fetch --all`. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\ev-sang-8 -b agy/ev-sang-8 origin/agy/ev-tran-7`. Trong apps/event: `npm ci`.
1. TEST KHOÁ trước (đỏ trước, xanh sau), tệp mới test/e2e/giao-dien-sang.test.js, chạy trên 15 trang web (mọi trang trong bang-chung/ev-chup-6/kiem-trang.json trừ /play/*):
   a) mặc định vẫn nền Đêm: màu nền body = rgb(11, 18, 32);
   b) có nút đổi giao diện trong đầu trang (aria-label "Giao diện sáng" / "Giao diện tối"), bấm → html[data-giao-dien="sang"], tải lại vẫn giữ (localStorage, bọc try/catch);
   c) ở giao diện sáng: tương phản chữ thân bài với nền ≥ 4.5:1 và tiêu đề ≥ 3:1 (tính từ màu computed, thông báo lỗi nêu trang + selector + tỉ số);
   d) không tràn ngang ở 360 và 1280 cả hai giao diện (dùng lại cách đo của khong-tran-ngang.test.js).
2. Dựng: chuyển các màu cứng trong public/web/css/web.css (và CSS xưởng /thu /de-xuat, /tao, agency) sang biến ngữ nghĩa (--nen, --nen-the, --nen-alt, --chu, --chu-diu, --vien, --nhan) đặt trong :root (giá trị Đêm như hiện tại, giao diện Đêm KHÔNG đổi một pixel nào) và html[data-giao-dien="sang"] lấy bảng màu sẵn có: --giay #F4F6F8, --trang #FFFFFF, --giay-alt #E9EDF2, --vien #D9DEE5, chữ #0B1220 / --muc-diu #2B2F36, nhấn --xanh-dam #0066CC. Không thêm màu mới ngoài bảng. Ảnh hero giữ lớp phủ tối để chữ trên ảnh vẫn trắng; nhát cắt 34° giữ gradient. Logo dùng bản màu hiện có (đọc được trên nền sáng). Màn khách /play/* giữ Đêm, không có nút.
3. Sửa thêm lỗi Claude thấy: /de-xuat ở 1280 thanh 5 bước dính sát/đè chữ "IF Agent" ở đầu trang: tách khoảng cách ≥ 24 px, thêm kiểm vào test (hộp logo và hộp thanh bước không giao nhau).
4. Chạy npm test + test mới + khong-tran-ngang + web-vo (tiền cảnh). Chụp 15 trang ở giao diện sáng 1280 và 360 vào bang-chung/ev-sang-8/ (PNG fullPage ≤ 600 KB), ghép TONG-SANG-1280.png, TONG-SANG-360.png; chụp lại 2 trang (trang chủ, /giai-phap) ở giao diện Đêm để chứng minh không đổi.
5. Push agy/ev-sang-8.

LUẬT CHUNG cụm event: chạy mọi lệnh TIỀN CẢNH, không background task; chỉ sửa apps/event/ và bang-chung/ev-sang-8/; không đụng apps/lab, packages/, nhánh Yên Lam/brand; không deploy, không mail thật, không in khoá, không sửa/xoá test cũ, không sinh ảnh AI, không tự viết chữ mới trên màn (chỉ thêm 2 nhãn nút ở trên). Bộ quét bí mật runner báo nhầm dòng CŨ (apps/lab/..., platform.test.js:38, apps/veew-booth/..., infra/staging/stg-event/...): không sửa các tệp đó; phiếu sửa chỉ cần xác nhận `git diff origin/agy/ev-tran-7..HEAD` không có bí mật mới. KET-QUA ngắn: dat co/khong; SHA đỉnh; test mới đỏ→xanh; pass/fail npm test; trang nào chưa đạt tương phản.

nhip: 05:42 29p đang chờ nền · log cuối 0 phút trước [log_cuoi=2026-11-17T05:42:24+0700] · root agent idle; waiting up to 40m0s for 1 ba
