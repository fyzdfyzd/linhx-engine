---
name: dong-tab-chrome
description: Luật bắt buộc mọi agent (Claude in Chrome, agy/Antigravity, Playwright) đóng tab Chrome do mình mở khi xong việc, kèm script don-tab.ps1 dọn tab cũ khi quá ngưỡng hoặc RAM thấp. Dùng mỗi khi agent điều khiển trình duyệt, và khi máy cty hay MSI tràn RAM vì Chrome.
---

# Đóng tab Chrome sau khi xong việc

Luật Linh 11/11/2026. Lý do: Claude và agy điều khiển Chrome xong không đóng tab, Chrome ăn hết RAM (máy cty DESKTOP-PVHR2CD chạy Chrome cho mọi việc web; MSI cũng bị).

## Luật (bắt buộc, mọi agent)
1. **Ghi sổ tab**: mỗi tab tự mở thì nhớ id/URL của nó. Chỉ đóng tab mình mở. Không đóng tab Linh đang dùng, không đóng tab đã ghim.
2. **Xong bước là đóng**: đọc xong trang, tải xong file, chụp xong ảnh thì đóng tab đó ngay, không đợi cuối việc.
3. **Trần 5 tab**: cùng lúc mỗi agent mở tối đa 5 tab. Cần tab thứ 6 thì đóng tab cũ nhất của mình trước. Dùng lại tab đang có (điều hướng sang URL mới) thay vì mở tab mới khi được.
4. **Cuối việc**: trước khi báo xong, đóng hết tab mình mở, gồm cả tab lỗi, tab đăng nhập, tab tải về. Báo cáo ghi một dòng `Tab: đã đóng N/N`.
5. **Lỗi giữa chừng cũng đóng**: việc hỏng hay dừng giữa chừng vẫn dọn tab trước khi thoát.
6. **Trình duyệt riêng của agent** (Playwright, Chrome mở bằng `--remote-debugging-port`): xong việc thì `browser.close()` hoặc tắt hẳn tiến trình, không để mồ côi.

## Cách đóng theo công cụ
| Công cụ | Đóng tab | Kiểm |
|---|---|---|
| Claude in Chrome | công cụ đóng tab của extension (tab trong nhóm MCP); hết tab thì đóng cả nhóm | lấy lại danh sách tab trong nhóm, phải rỗng |
| agy (browser của Antigravity) | đóng page/tab vừa dùng; cuối phiên đóng cửa sổ browser của agy | `don-tab.ps1 -ThuKhong` không còn tab của agy |
| Playwright / Puppeteer | `page.close()` sau mỗi trang, `browser.close()` trong `finally` | không còn tiến trình chrome mồ côi |

## Chốt chặn: `don-tab.ps1`
Chạy định kỳ trên máy Windows (máy cty và MSI). Tìm mọi Chrome mở cổng debug (trình duyệt agent điều khiển), giữ tối đa `-MaxTab` tab mới dùng nhất, đóng phần còn lại. RAM trống dưới `-NguongMB` thì hạ trần xuống `-MaxTabKhiThieu`. Chrome thường của Linh (không cổng debug) không bị đóng tab, chỉ ghi cảnh báo RAM vào log.

```powershell
# Xem trước, không đóng gì
powershell -ExecutionPolicy Bypass -File skills\le\dong-tab-chrome\don-tab.ps1 -ThuKhong
# Chạy thật một lần
powershell -ExecutionPolicy Bypass -File skills\le\dong-tab-chrome\don-tab.ps1
# Cài lịch 15 phút một lần (Task Scheduler, user hiện tại, không cần admin)
powershell -ExecutionPolicy Bypass -File skills\le\dong-tab-chrome\don-tab.ps1 -CaiLich
```
Tham số mặc định: `-MaxTab 8`, `-MaxTabKhiThieu 3`, `-NguongMB 1500`. Log: `D:\linhx\.canh\don-tab.log` nếu có thư mục đó, không thì `%TEMP%\don-tab.log`.

## Thêm một lần trên mỗi máy
Bật Chrome Memory Saver: `chrome://settings/performance` → Tiết kiệm bộ nhớ (Memory Saver) → Bật, mức Tối đa. Chrome tự ngủ tab không dùng.
