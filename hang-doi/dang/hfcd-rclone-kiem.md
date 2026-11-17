may: may-1
loai: khac
tran_phut: 40
theo_doi: D:\linhx\LAB129-BACKUP-HFCD
nhan: may-1 2026-11-17T19:34:12+0700

# HFCD bước 1: cài rclone, kiểm quyền + đo dung lượng 361 link (CHƯA tải folder)

BƯỚC 0: chạy `hostname`. Khác DESKTOP-PVHR2CD thì dừng, KET-QUA ghi `SAI_MAY: <hostname>`.

1. Cài rclone nếu chưa có (`winget install Rclone.Rclone`, hoặc tải zip bản chính thức từ rclone.org về `D:\linhx\tools\rclone`).
2. Tạo remote chỉ đọc:
   `rclone config create hfcd drive scope=drive.readonly`
   Lệnh in ra URL xin quyền (dùng `--config` không tự mở trình duyệt nếu cần: `rclone authorize drive` rồi dán token). Linh đã duyệt rclone chỉ đọc: agy mở URL đó bằng Browsentic (MCP browsentic, Chrome đã đăng nhập, cổng 8765), chọn tài khoản Google mở được sheet 189ECtfxS4fsKLK1MLbXwJNV8tUnLmA4a0itIRtRVXAg, bấm Cho phép, chỉ đúng phạm vi drive.readonly. Không được thì dừng, ghi CAN-LINH.
   Thử: `rclone lsf hfcd: --drive-root-folder-id 1_0nQxNl6zsjuk50ty_scetmtHiLXOwBu --max-depth 1`.
3. Với từng dòng `viec/hfcd-backup/DANH-SACH-LINK.csv`:
   - loai folder: `rclone size hfcd: --drive-root-folder-id <ID> --json` (timeout 60 giây/dòng). Được → `MO_DUOC`, ghi_chu = "<so file> file, <GB> GB". Lỗi notFound/403 → `CHUA_QUYEN`. Quá 60 giây → `MO_DUOC`, ghi_chu "lon, chua do het".
   - loai file/sheet/doc/slide: `rclone backend copyid hfcd: <ID> D:\linhx\LAB129-BACKUP-HFCD\_file\` (file lẻ nhỏ thì tải luôn, sheet/doc tự xuất xlsx/docx). Được → `MO_DUOC` + `duong_dan_luu`; lỗi → `CHUA_QUYEN`.
   - Nếu rclone báo notFound cho một ID, mở url bằng Browsentic để phân biệt: trang "Bạn cần quyền truy cập/Request access" → `CHUA_QUYEN`; 404 → `KHONG_TON_TAI`.
   - loai ngoai: Dropbox thử tải bản zip bằng cách đổi `dl=0` thành `dl=1` (curl -L, tối đa 2 phút, không tải nếu > 2 GB, chỉ ghi dung lượng). SharePoint/web khác: ghi `CAN_DANG_NHAP` hoặc `MO_DUOC`, không đăng nhập.
4. Lưu `D:\linhx\LAB129-BACKUP-HFCD\DANH-SACH-LINK-DA-KIEM.csv`, chép vào `xong/hfcd-rclone-kiem/` khi push.

Cấm: không xoá/sửa/chia sẻ gì trên Drive (remote chỉ đọc), không bấm nút xin quyền truy cập trên file của người khác, luật tab Chrome: tối đa 5 tab, đóng tab mình mở, KET-QUA ghi `Tab: đã đóng N/N`, không ghi token rclone hay email vào repo/KET-QUA. File cấu hình rclone để nguyên chỗ mặc định trên máy.

KET-QUA.md ≤ 2000 ký tự: số dòng mỗi trạng thái, tổng GB các folder MO_DUOC, 10 folder lớn nhất (stt + GB), dung lượng trống ổ D:, số file lẻ đã tải.

nhip: 19:47 13p đang chờ nền · log cuối 0 phút trước [log_cuoi=2026-11-17T19:47:28+0700] · root agent idle; waiting up to 40m0s for 1 ba
