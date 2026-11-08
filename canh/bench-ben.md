# Bench WSL chạy bền (máy công ty DESKTOP-PVHR2CD, 08/11/2026)

Frappe bench trong WSL Ubuntu (`/home/frappe/frappe-bench`, cổng 8000, site test) chạy bằng systemd, không phụ thuộc phiên RC hay cửa sổ nào.

## Gồm
- `canh/linhx-bench.service`: chép vào `/etc/systemd/system/` trong Ubuntu, enabled. Chạy `bench serve --port 8000` bằng user frappe, `Restart=always`, sau mariadb và redis-server (hai service này cũng enabled).
- `%USERPROFILE%\.wslconfig`: thêm `vmIdleTimeout=-1` trong `[wsl2]`. Bản cũ để ở `.wslconfig.bak-0811`. Dòng này có hiệu lực từ lần WSL khởi động lại kế tiếp.
- Lịch Windows `ENGINE-BenchBen`: chạy lúc đăng nhập và mỗi 10 phút, bỏ qua nếu đang chạy, ẩn hoàn toàn qua `wscript //B chay-an.vbs`. Lịch gọi `canh/bench-ben.ps1`, giữ một tiến trình `wsl.exe ... sleep infinity` để distro không tắt khi không có phiên. Tiến trình đó chết thì lượt lịch kế dựng lại.

## Cài lại (nếu dựng máy mới)
```
wsl -d Ubuntu -u root -- bash -c "cp /mnt/d/LINHX/LINHX-ENGINE/canh/linhx-bench.service /etc/systemd/system/ && systemctl daemon-reload && systemctl enable --now mariadb redis-server linhx-bench"
```
Cần `/etc/wsl.conf` có `[boot] systemd=true`.

## Kiểm, xem log
- Ping: `wsl -d Ubuntu -- curl -s http://127.0.0.1:8000/api/method/ping` trả về `{"message":"pong"}`. Phía Windows, cổng 8000 là LINHX-Server8000, không phải bench.
- Trạng thái: `wsl -d Ubuntu -u root -- systemctl status linhx-bench`
- Log bench serve: `wsl -d Ubuntu -- tail -n 100 /home/frappe/frappe-bench/logs/bench-serve.log`
- Log systemd: `wsl -d Ubuntu -u root -- journalctl -u linhx-bench -n 100`
- Log lịch giữ sống: `D:\LINHX\ENGINE-canh\bench\<yyyyMMdd>.log` (dòng `bench-ben`)
- Khởi động lại bench (sau khi gắn app): `wsl -d Ubuntu -u root -- systemctl restart linhx-bench`

## Lưu ý
- `canh/bench.ps1 serve` và `dung` là cách cũ. Giờ bench do systemd giữ: `dung` sẽ pkill, rồi systemd dựng lại sau 5 giây. Muốn dừng hẳn thì dùng `systemctl stop linhx-bench`.
- Đã thử kill -9 tiến trình bench: systemd dựng lại (NRestarts=1), ping vẫn ra 200.
