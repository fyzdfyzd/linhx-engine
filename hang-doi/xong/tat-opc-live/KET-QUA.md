phieu: tat-opc-live
may: may-1
trang_thai: xong
tep_doi: (khong)
drive: (khong)
phut: 6.51
token: vao=34333 ra=5706

Đang kiểm tra lần cuối trạng thái cổng 4900, các tiến trình và lịch `\OPC-Live`, mình sẽ phản hồi ngay khi lệnh kiểm tra hoàn tất.
Kết quả thực hiện tạm tắt **OPC Live** (không xoá lịch, không xoá bất kỳ file nào):

### 1. Trạng thái lịch `\OPC-Live`
- Đã tìm thấy lịch: `\OPC-Live` (trỏ tới [chay-nen.ps1](file:///D:/LINHX/LINHX-OPC/OPC-LIVE-SRC/opc-live/chay-nen.ps1), cấu hình bởi [cai-dat.ps1](file:///D:/LINHX/LINHX-OPC/OPC-LIVE-SRC/opc-live/cai-dat.ps1#L16-L19)).
- Trạng thái chạy hiện tại đã chuyển từ `Running` sang `Ready` (lịch chỉ có trigger `At logon time`, không lặp định kỳ nên **sẽ không tự bật lại** trong phiên đăng nhập hiện tại).
- **Lưu ý vướng quyền UAC khi Disable:** Lệnh `schtasks /change /tn "\OPC-Live" /disable` (và `Disable-ScheduledTask -TaskName "OPC-Live"`) bị Windows chặn với lỗi `ERROR: Access is denied (0x80070005)` do phiên runner hiện chạy ở mức thường (`Medium Mandatory Level`, chưa nâng quyền UAC), trong khi lịch có trigger `AtLogOn` bắt buộc quyền **Administrator** để đổi trạng thái `Disabled`. Để tắt hẳn qua các lần khởi động lại máy, chạy 1 dòng sau trong PowerShell/CMD **Run as Administrator**:
  ```powershell
  schtasks /change /tn "\OPC-Live" /disable
  ```

### 2. Tiến trình đã dừng (đã kiểm tra cổng `4900` trống hoàn toàn)
Chỉ dừng đúng cây tiến tr
...[cat bot]...
--cong 4900`
- **PID `6844` (`python.exe` — nghe `127.0.0.1:4900`):** `python.exe server.py --cong 4900` ([server.py](file:///D:/LINHX/LINHX-OPC/OPC-LIVE-SRC/opc-live/server.py))

### 3. Lệnh bật lại
- **Bật lại lịch (chạy trong PowerShell/CMD quyền Administrator nếu đã Disable) và khởi động lại ngay:**
  ```powershell
  schtasks /change /tn "\OPC-Live" /enable
  schtasks /run /tn "\OPC-Live"
  ```
- **Xem lại link tunnel mới (sau khoảng 15 giây khi bật lại):**
  ```powershell
  Get-Content "D:\LINHX\LINHX-OPC\OPC-LIVE-SRC\opc-live\var\dia-chi.txt"
  ```
