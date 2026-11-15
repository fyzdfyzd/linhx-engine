# Nối máy 1 và máy 3 vào trạm giao việc trên máy 2 (qua Tailscale, không cần GitHub)

Trạm: `git://may-2/linhx-engine.git` (nhánh hang-doi) và `git://may-2/ifagent.git`, chỉ mở trong mạng Tailscale.

## Bước 0 (MÁY 2, làm trước, quyền admin)
`powershell -ExecutionPolicy Bypass -File C:\linhx\tram\CAI-TRAM-MAY-2.ps1`
Thấy "XONG: tram song" là được. Sau đó đổi runner máy 2 sang trạm:
```
cd C:\linhx\hang-doi
git remote add tram C:/linhx/tram/linhx-engine.git
copy runner\tho.env runner\tho.env.truoc-tram
```
Mở `runner\tho.env`, sửa dòng `LINHX_REMOTE_HANG_DOI=origin` thành `LINHX_REMOTE_HANG_DOI=tram` (chưa có thì thêm).

## Máy 1 (DESKTOP-PVHR2CD) và máy 3 (DESKTOP-2AUT482), PowerShell quyền admin
1. Cài và đăng nhập Tailscale (cùng gmail đã dùng ở máy 2, KHÔNG dùng @urah.vn). Thay `may-3` bằng `may-1` khi làm ở máy 1:
```
winget install --id Tailscale.Tailscale -e --silent --accept-package-agreements --accept-source-agreements
& "C:\Program Files\Tailscale\tailscale.exe" up --hostname=may-3 --unattended
```
2. Kiểm thấy trạm:
```
git ls-remote git://may-2/linhx-engine.git hang-doi
```
Ra một dòng có `refs/heads/hang-doi` là được. Không ra: chạy `tailscale status` xem có may-2 không.
3. Đổi hàng đợi của runner sang trạm (thư mục repo hàng đợi trên máy đó, máy 3 là `C:\linhx\hang-doi`):
```
cd C:\linhx\hang-doi
git remote add tram git://may-2/linhx-engine.git
git fetch tram
copy runner\tho.env runner\tho.env.truoc-tram
```
Mở `runner\tho.env`, đặt `LINHX_REMOTE_HANG_DOI=tram`.
4. Bật runner: `schtasks /Change /TN LINHX-HangDoi /ENABLE` rồi `schtasks /Run /TN LINHX-HangDoi`. Xem `runner\tho.log`: có dòng `tho=may-3` mỗi phút, không còn "push bi tu choi".

## Quay lại GitHub khi cần
Sửa `LINHX_REMOTE_HANG_DOI=origin` trong `runner\tho.env` (hoặc chép lại `tho.env.truoc-tram`).

## Ghi chú
- Ai trong tailnet cũng đẩy được vào trạm; chỉ mời máy của Linh vào tailnet.
- GitHub (origin) chỉ là bản sao: khi tài khoản mở lại, máy 2 đẩy trạm lên GitHub.
