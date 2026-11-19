dat: co
phieu: bhc-domain-3 (kiem DNS + SSL + trinh duyet that 1280/360 cho brandcheck.ifagent.net)
nhanh: agy/bhc-domain-3

# KET-QUA: bhc-domain-3

- **dat**: `dat` (`dat: co`)
- **IP DNS**: `34.87.102.182` (cả `8.8.8.8`, `1.1.1.1` và GoDaddy NS `ns59.domaincontrol.com` đều trả về `34.87.102.182`)
- **HTTP**: `HTTP/1.1 200 OK`
- **Chứng chỉ**:
  - **Subject / SAN**: `CN=brandcheck.ifagent.net` (`DNS:brandcheck.ifagent.net`)
  - **Nhà cấp chứng chỉ (Issuer)**: `Let's Encrypt` (`C=US, O=Let's Encrypt, CN=YE1`)
  - **Ngày cấp (Valid From)**: `Nov 19 05:10:00 2026 GMT`
  - **Ngày hết hạn (Valid To)**: `Feb 17 05:09:59 2027 GMT`
  - **Serial Number**: `0662CFAABDF95784F0ADE69284F560411620`
- **Lỗi (yêu cầu lỗi ≥ 400)**: `[]` (rỗng trên cả 3 trang × 2 khung hình `1280x800` và `360x800`)
- **Ảnh**:
  - `bang-chung/bhc-domain-3/trang-chu-1280.png`
  - `bang-chung/bhc-domain-3/trang-chu-360.png`
  - `bang-chung/bhc-domain-3/bao-cao-csmo-1280.png`
  - `bang-chung/bhc-domain-3/bao-cao-csmo-360.png`
  - `bang-chung/bhc-domain-3/quan-tri-1280.png`
  - `bang-chung/bhc-domain-3/quan-tri-360.png`

---

## 1. Kiểm tra IP DNS (`nslookup brandcheck.ifagent.net 8.8.8.8` và `1.1.1.1`)

| Máy chủ DNS | Lệnh kiểm tra | Kết quả trả về | Kỳ vọng | Trạng thái |
| --- | --- | --- | --- | --- |
| Google DNS (`8.8.8.8`) | `nslookup brandcheck.ifagent.net 8.8.8.8` | **`34.87.102.182`** | `34.87.102.182` | Đạt |
| Cloudflare DNS (`1.1.1.1`) | `nslookup brandcheck.ifagent.net 1.1.1.1` | **`34.87.102.182`** | `34.87.102.182` | Đạt |
| GoDaddy Authoritative NS (`ns59.domaincontrol.com`) | `nslookup brandcheck.ifagent.net ns59.domaincontrol.com` | **`34.87.102.182`** | `34.87.102.182` | Đạt |

---

## 2. Kiểm tra HTTP & Chứng chỉ (`curl -sv https://brandcheck.ifagent.net/`)

- Đã chạy `sudo docker compose exec -T caddy caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile --force` tại `/opt/ifagent/infra` (không restart container `ifagent-caddy-1`) sau khi DNS trỏ về `34.87.102.182`. Caddy giải thành công challenge `tls-alpn-01` và nhận chứng chỉ chính thức từ Let's Encrypt (`authorization finalized`, `authz_status: valid`).
- Kết quả `curl -sv https://brandcheck.ifagent.net/`:
  - Kết nối tới: `34.87.102.182:443`
  - Phản hồi HTTP: `HTTP/1.1 200 OK` (`Content-Type: text/html; charset=utf-8`, `Via: 1.1 Caddy`)
  - Nhà cấp chứng chỉ: `C=US, O=Let's Encrypt, CN=YE1`
  - Ngày hiệu lực – Ngày hết hạn: `Nov 19 05:10:00 2026 GMT` → **`Feb 17 05:09:59 2027 GMT`**

---

## 3. Kiểm tra bằng trình duyệt thật (Chromium `1280x800` + `360x800`, TLS chuẩn)

| Trang kiểm tra | URL | Khung hình | HTTP Status | Tổng số request | Danh sách yêu cầu lỗi ≥ 400 | Ảnh chụp |
| --- | --- | --- | --- | --- | --- | --- |
| Trang chủ | `https://brandcheck.ifagent.net/` | `1280x800` | `200` | `14` | `[]` (rỗng) | `trang-chu-1280.png` |
| Trang chủ | `https://brandcheck.ifagent.net/` | `360x800` | `200` | `14` | `[]` (rỗng) | `trang-chu-360.png` |
| Báo cáo mẫu CSMO | `https://brandcheck.ifagent.net/bao-cao/2026-11-19-csmo-d88de79d/` | `1280x800` | `200` | `19` | `[]` (rỗng) | `bao-cao-csmo-1280.png` |
| Báo cáo mẫu CSMO | `https://brandcheck.ifagent.net/bao-cao/2026-11-19-csmo-d88de79d/` | `360x800` | `200` | `18` | `[]` (rỗng) | `bao-cao-csmo-360.png` |
| Quản trị (trang đăng nhập) | `https://brandcheck.ifagent.net/quan-tri/` | `1280x800` | `200` | `12` | `[]` (rỗng) | `quan-tri-1280.png` |
| Quản trị (trang đăng nhập) | `https://brandcheck.ifagent.net/quan-tri/` | `360x800` | `200` | `12` | `[]` (rỗng) | `quan-tri-360.png` |
