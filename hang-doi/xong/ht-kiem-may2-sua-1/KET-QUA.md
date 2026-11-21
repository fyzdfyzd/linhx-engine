model: gemini-4-neon-medium
phieu: ht-kiem-may2-sua-1
may: may-2
trang_thai: xong
tep_doi: KET-QUA.md, o-c-may2.csv
drive: (khong)
phut: 5.40
token: vao=97455 ra=22304

Đã hoàn tất khảo sát ổ C trên máy 2 (`DESKTOP-LNRQBEE`, chỉ đọc, không xoá gì) và ghi kết quả vào:
- [KET-QUA.md](file:///C:/linhx/hang-doi/runner/viec/lam-viec/KET-QUA.md) (1,948 ký tự ≤ 2,000)
- [o-c-may2.csv](file:///C:/linhx/hang-doi/runner/viec/lam-viec/o-c-may2.csv) (229 dòng: Top 30 thư mục lớn nhất + mục cache bổ sung + 183 worktree con trong `C:\linhx\ifagent-wt` kèm ngày sửa cuối)

### Tóm tắt chính
- **Ổ đĩa hiện có**: Chỉ có **1 ổ NVMe vật lý** `SAMSUNG MZVLB512HBJQ-000L2` (476.94 GB), `C:` dùng **472.33 / 476.31 GB** (trống **3.98 GB**). Ổ `G:` (`Google Drive`) là ổ ảo stream dùng chung cache trên `C:` (trống 3.78 GB). Không có ổ phụ, USB/ổ ngoài hay ổ mạng SMB (`net use` trống).
- **Tổng tiềm năng dọn (~375.6 GB)**:
  - **An toàn dọn ngay (~20.8 GB)**:
    - `C:\Users\Admin\AppData\Local\Temp`: **18.53 GB** (gồm 137 thư mục `dongbo-*` = 16.96 GB + 0.59 GB file lẻ).
    - `C:\Users\Admin\.gemini\antigravity-cli\brain`: **1.23 GB** (368 phiên cũ).
    - `C:\Users\Admin\AppData\Local\npm-cache`: **0.89 GB**.
    - `C:\Users\Admin\AppData\Local\pip`: **0.15 GB**.
  - **Cần Linh xem trước (~354.8 GB)**:
    - `C:\linhx\ifagent-wt`: **323.08 GB** (~68% ổ C, 183 git worktree — trong đó **175 worktree cũ `<20/11` chiếm 307.95 GB**, 8 cái `20–2
...[cat bot]...
 `wt-ui-admin-17-11` 3.96 GB, `wt` 1.20 GB, `wt-csmo` 1.15 GB, 7 thư mục `wt-neon-*` ~2.7 GB…).
    - Khác (**9.63 GB**): `C:\linhx\nhat-ky` (2.58 GB), `DriveFS` cache (2.54 GB), `antigravity-cli\conversations` (1.83 GB), `ms-playwright` (1.43 GB), `C:\linhx\rc6-cuc-bo` (1.25 GB).

`CAN-LINH: Kiểm tra C:\Users\Huong\AppData\Local\Temp (bị từ chối truy cập, cần quyền Admin) hoặc cắm thêm ổ cứng ngoài/gắn ổ mạng SMB nếu muốn mở rộng dung lượng vật lý; LENH: Get-ChildItem C:\Users\Huong\AppData\Local\Temp -Force | Measure-Object Length -Sum`
