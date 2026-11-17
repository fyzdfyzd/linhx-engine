may: may-1
loai: trinh-duyet
tran_phut: 40
theo_doi: D:\linhx\LAB129-BACKUP-HFCD

# Kiểm quyền 361 link HFCD + đo dung lượng (CHƯA tải)

Đầu vào: `viec/hfcd-backup/DANH-SACH-LINK.csv` trên nhánh hang-doi (361 link đã khử trùng: 261 folder, 45 file, 37 sheet, 6 doc, 1 slide, 11 link ngoài Dropbox/SharePoint/web).

Việc:
1. Chrome máy này: chọn profile/tài khoản Google mở được sheet gốc https://docs.google.com/spreadsheets/d/189ECtfxS4fsKLK1MLbXwJNV8tUnLmA4a0itIRtRVXAg (thử /u/0../u/6). Ghi tài khoản dùng là /u/N nào (không ghi email).
2. Với từng dòng CSV, mở url trong tab đó, điền cột `trang_thai`:
   - `MO_DUOC` nếu xem được nội dung;
   - `CHUA_QUYEN` nếu hiện trang "Bạn cần quyền truy cập / Request access / Yêu cầu quyền";
   - `KHONG_TON_TAI` nếu 404 / đã xoá;
   - `CAN_DANG_NHAP` cho Dropbox/SharePoint đòi đăng nhập.
   Cột `ghi_chu`: với folder MO_DUOC ghi số mục con + dung lượng ước tính (xem ở Drive, ví dụ "34 mục, ~2,1 GB"); với file ghi dung lượng.
3. Lưu CSV đã điền vào `D:\linhx\LAB129-BACKUP-HFCD\DANH-SACH-LINK-DA-KIEM.csv` và chép vào `xong/hfcd-kiem-quyen/` khi push.

Cấm: không tải, không bấm "Yêu cầu quyền truy cập", không sửa/xoá/chia sẻ file nào trên Drive, không đụng tab của Linh. Luật tab: tối đa 5 tab, đóng tab mình mở, cuối báo `Tab: đã đóng N/N`.

Gợi ý nhanh: có thể dùng một tab và đổi url liên tục; chờ trang tải xong rồi đọc chữ trên trang.

Trả lời KET-QUA.md (≤ 2000 ký tự): số dòng mỗi trạng thái, tổng dung lượng ước tính các mục MO_DUOC, 10 mục lớn nhất, tài khoản /u/N đã dùng, `Tab: đã đóng N/N`.
