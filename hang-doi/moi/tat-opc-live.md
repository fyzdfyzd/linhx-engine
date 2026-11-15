may: may-1
loai: khac
tran_phut: 10

Linh duyệt 15/11 07:34: tạm tắt OPC Live trên máy này (tắt lịch OPC-Live, không xoá; dừng server cổng 4900 và tunnel của nó).
1. `schtasks /query /fo list | findstr /i "OPC"` tìm lịch; Disable (KHÔNG xoá) lịch tên chứa OPC-Live/OPC Live.
2. Dừng tiến trình nghe cổng 4900 và cloudflared/chay-nen.ps1 có dòng lệnh trỏ vào D:\LINHX\LINHX-OPC\OPC-LIVE-SRC. Không đụng tiến trình khác.
3. Không xoá file nào.
Trả lời: lịch đã tắt, tiến trình đã dừng, lệnh bật lại.
