# LINHX ENGINE 0.1: bản chạy đầu

Shop báo cáo chạy bằng agy. Khách đặt báo cáo trên mặt tiền → Linh duyệt → thợ agy rảnh (trên cloud hoặc máy riêng) kéo việc về chạy → khách mở link đọc báo cáo.
Báo cáo đầu tiên: **AI nói gì về thương hiệu của bạn** (8 câu × ChatGPT, Gemini, Claude; 4 chỉ số Có mặt, Độ đúng, Được đề xuất, Độ nhất quán, khớp bài CSMO Topic 07). AI chỉ gán nhãn, code tính điểm (`bao_cao.py`).

## Wiki chung
`wiki/` là bộ nhớ chung LINHX (kiểu LLM Wiki của Karpathy): đích cuối, kiến trúc, lộ trình, 63 hệ thống, dự án, quyết định, việc chờ. Bắt đầu ở `wiki/INDEX.md`. Rà: `python scripts/ra_wiki.py`.

## Thành phần
| Thư mục | Là gì |
|---|---|
| `apps/linhx_worker` | App Frappe: DocType `LX Worker`, `LX Workflow`, `LX Job`; API hàng việc (`api.py`), chấm điểm (`bao_cao.py`), đề agy (`de/`) |
| `front/` | linhx-front: 1 file HTML. `/#/` đặt báo cáo · `/#/bao-cao/<VIEC>/<ma>` khách xem · `/#/engine` bảng điều hành (đăng nhập) |
| `runner/` | linhx-runner: thợ nhận việc, chỉ stdlib Python. Chạy trên Windows (ẩn) hoặc trong container |
| `deploy/` | Docker Compose: MariaDB, Redis, Frappe (backend, websocket, queue, scheduler, nginx), Caddy (HTTPS + mặt tiền), thợ cloud |

## Luồng
```
khách ─▶ dat_bao_cao (cho_duyet) ─▶ Linh bấm Duyệt (cho) ─▶ thợ hợp nhãn gọi nhan_viec (SKIP LOCKED)
     ─▶ agy -p "<đề>" --output-format json ─▶ bao_ket_qua ─▶ khách xem_bao_cao (4 chỉ số)
```
- Server không gọi vào máy nào, không gửi lệnh shell; thợ chỉ nhận ĐỀ (chữ) cho workflow trong danh sách.
- Mỗi thợ một tài khoản API riêng, chỉ ghi được việc của mình.
- Workflow có `nhan_can`: `ai-noi-gi-ve-brand` cần `trinh-duyet` (Chrome đã đăng nhập ở máy cty); `lam-phieu-code` cần `repo`.
- Quá trần phút + 5: việc trả về hàng (tối đa 2 lần) rồi chuyển lỗi. Thợ im 2 phút: ngoại tuyến.

## Deploy lên VM (Ubuntu + Docker)
```
gcloud compute scp --recurse linhx-engine linhx-engine-1:~ --zone asia-southeast1-b
gcloud compute ssh linhx-engine-1 --zone asia-southeast1-b --command "cd linhx-engine/deploy && sudo bash len-may.sh http://<IP>"
```
Có tên miền thì truyền `https://engine.ten-mien` (Caddy tự lấy chứng chỉ). Bí mật nằm ở `/root/linhx-bi-mat.env` trên VM.

## Thợ trên máy Windows (máy cty)
1. Chép `runner/` vào `D:\linhx\linhx-runner`, tạo `tho.env` từ `tho.env.example` (URL + TOKEN_MAY_CTY).
2. `powershell -ExecutionPolicy Bypass -File dang-ky-lich.ps1` (không cần quyền quản trị; chạy ẩn qua `chay-an-tho.vbs`).
3. Bảng Engine thấy `may-cty` chấm xanh. Giao việc "Kiểm đường ống" để thử.

## agy trên cloud (thợ `cloud-1`)
Đăng nhập 1 lần: `sudo docker compose -f deploy/docker-compose.yml run --rm tho-cloud agy` → agy in đường dẫn + mã → mở trên điện thoại, đăng nhập zomplaza → thoát. Phiên lưu ở volume `agy-home`.
Chưa đăng nhập được thì `cloud-1` vẫn chạy được workflow `kiem-duong-ong`.

## Thử ở máy dev
```
cd deploy && cp .env.example .env && docker compose up -d --build
python3 apps/linhx_worker/linhx_worker/tests/test_bao_cao.py
```

## Việc kế tiếp (phiếu ≤ 40 phút)
1. Thanh toán VietQR + webhook SePay cho báo cáo (K1), bỏ bước duyệt tay với đơn đã trả.
2. Gửi email link báo cáo khi xong (email queue Frappe).
3. Tách repo `linhx-worker`, `linhx-front`; CI chạy test.
4. Bản PDF báo cáo; trang QR cho sân khấu CSMO.
