may: may-1
loai: khac
tran_phut: 40
theo_doi: D:\linhx\LAB129-BACKUP-HFCD

# HFCD bước 1: cài rclone, kiểm quyền + đo dung lượng 361 link (CHƯA tải folder)

BƯỚC 0: chạy `hostname`. Khác DESKTOP-PVHR2CD thì dừng, KET-QUA ghi `SAI_MAY: <hostname>`.

1. Cài rclone nếu chưa có (`winget install Rclone.Rclone`, hoặc tải zip bản chính thức từ rclone.org về `D:\linhx\tools\rclone`).
2. Tạo remote chỉ đọc:
   `rclone config create hfcd drive scope=drive.readonly`
   Lệnh mở trình duyệt xin quyền: Linh đã đồng ý sẽ bấm Cho phép trên máy này (chọn tài khoản Google mở được sheet 189ECtfxS4fsKLK1MLbXwJNV8tUnLmA4a0itIRtRVXAg). Chờ tối đa 15 phút. Quá giờ thì dừng, ghi CAN-LINH.
   Thử: `rclone lsf hfcd: --drive-root-folder-id 1_0nQxNl6zsjuk50ty_scetmtHiLXOwBu --max-depth 1`.
3. Với từng dòng `viec/hfcd-backup/DANH-SACH-LINK.csv`:
   - loai folder: `rclone size hfcd: --drive-root-folder-id <ID> --json` (timeout 60 giây/dòng). Được → `MO_DUOC`, ghi_chu = "<so file> file, <GB> GB". Lỗi notFound/403 → `CHUA_QUYEN`. Quá 60 giây → `MO_DUOC`, ghi_chu "lon, chua do het".
   - loai file/sheet/doc/slide: `rclone backend copyid hfcd: <ID> D:\linhx\LAB129-BACKUP-HFCD\_file\` (file lẻ nhỏ thì tải luôn, sheet/doc tự xuất xlsx/docx). Được → `MO_DUOC` + `duong_dan_luu`; lỗi → `CHUA_QUYEN`.
   - loai ngoai: Dropbox thử tải bản zip bằng cách đổi `dl=0` thành `dl=1` (curl -L, tối đa 2 phút, không tải nếu > 2 GB, chỉ ghi dung lượng). SharePoint/web khác: ghi `CAN_DANG_NHAP` hoặc `MO_DUOC`, không đăng nhập.
4. Lưu `D:\linhx\LAB129-BACKUP-HFCD\DANH-SACH-LINK-DA-KIEM.csv`, chép vào `xong/hfcd-rclone-kiem/` khi push.

Cấm: không xoá/sửa/chia sẻ gì trên Drive (remote chỉ đọc), không bấm xin quyền, không ghi token rclone hay email vào repo/KET-QUA. File cấu hình rclone để nguyên chỗ mặc định trên máy.

KET-QUA.md ≤ 2000 ký tự: số dòng mỗi trạng thái, tổng GB các folder MO_DUOC, 10 folder lớn nhất (stt + GB), dung lượng trống ổ D:, số file lẻ đã tải.
