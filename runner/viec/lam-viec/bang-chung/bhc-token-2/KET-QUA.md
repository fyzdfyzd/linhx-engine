dat: khong
phieu: bhc-token-2
nhanh: agy/bhc-token-2

# KET-QUA: bhc-token-2 — Kiểm tra lại số dư OpenRouter & HTTP Gemini sau khi nạp 10 USD (`ifagent-event`)

- **Thời điểm kiểm tra**: `2026-11-19 14:17:38 +07:00` (sau khi Linh báo vừa nạp 10 USD lúc `14:13 VN`)
- **VM kiểm tra**: `ifagent-event` (`zone=asia-southeast1-b`, `project=ifagent-event-2026`)
- **File cấu hình**: `/opt/ifagent/infra/brand-health.env` (chỉ đọc bằng biến shell, không sửa, không in giá trị khoá)
- **Mã băm khoá (`sha8`)**:
  - `OPENROUTER_API_KEY` (`sha8`): `cf10d779`
  - `GEMINI_API_KEY` (`sha8`): `7f7f0125`
- **Cấu hình model trong env**:
  - `OPENROUTER_MODELS`: `openai/gpt-5.4-mini,google/gemini-2.5-flash,perplexity/sonar,deepseek/deepseek-v4.1-flash-1017`
  - `GEMINI_MODEL`: `gemini-3.5-flash-lite`
- **Kết luận (`dat/khong`)**: **`khong`** (OpenRouter: **`dat`** — đã nhận 10 USD nạp thêm; Gemini trực tiếp: **`khong`** — vẫn `HTTP 402`)
  - **Tóm tắt hiện trạng sau khi nạp 10 USD (14:13 VN)**:
    1. **OpenRouter (`OPENROUTER_API_KEY`, `sha8: cf10d779`) — ĐẠT**: Khoản `10 USD` vừa nạp đã vào tài khoản OpenRouter (`total_credits` tăng từ `20 USD` lên **`30 USD`**). Số dư thực hiện tại: `total_credits - total_usage = 30 - 19.390246096 =` **`10.609753904 USD`** (~**`$10.61 USD`**).
    2. **Gemini trực tiếp (`GEMINI_API_KEY`, `sha8: 7f7f0125`) — KHÔNG ĐẠT (`HTTP 402 RESOURCE_EXHAUSTED`)**: Gọi `generateContent` model `gemini-3.5-flash-lite` với câu `"ok"` vẫn trả về **`HTTP 402`** (`Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing.`). Lý do: `GEMINI_API_KEY` gọi trực tiếp Google AI Studio (`generativelanguage.googleapis.com`), tách biệt với ví OpenRouter, và ví prepayment trên Google AI Studio hiện vẫn cạn credit.

---

## 1. Bảng số dư OpenRouter (`/api/v1/key` & `/api/v1/credits`)

| Chỉ số | Trước khi nạp (`bhc-token-1`, 14:01 VN) | Hiện tại sau khi nạp 10 USD (`bhc-token-2`, 14:17 VN) | Thay đổi | Nguồn API | Ghi chú |
| --- | ---: | ---: | ---: | --- | --- |
| `limit` | `50` | **`50`** | `0` | `GET /api/v1/key` | Trần giới hạn cấu hình trên API key (`sha8: cf10d779`) |
| `usage` | `19.385236096` | **`19.390246096`** | `+0.00501` | `GET /api/v1/key` | Tổng mức sử dụng của API key (`usage_daily`: `10.787905361`) |
| `limit_remaining` | `30.614763904` | **`30.609753904`** | `-0.00501` | `GET /api/v1/key` | Trần còn lại của riêng API key (`limit - usage`) |
| `total_credits` | `20` | **`30`** | **`+10.00000`** | `GET /api/v1/credits` | Tổng tín dụng đã nạp vào tài khoản OpenRouter (đã nhận +10 USD) |
| `total_usage` | `19.385236096` | **`19.390246096`** | `+0.00501` | `GET /api/v1/credits` | Tổng tín dụng đã tiêu dùng của tài khoản |
| **Số dư (`total_credits - total_usage`)** | **`0.614763904`** | **`10.609753904`** | **`+9.99499`** | `total_credits - total_usage` | **Số dư thực còn lại của tài khoản OpenRouter (~$10.61 USD)** |

---

## 2. Bảng từng model OpenRouter HTTP

Theo yêu cầu phiếu `bhc-token-2`: **Bước 2 bỏ qua — không gọi thử lại model OpenRouter** để tiết kiệm token (tham chiếu kết quả kiểm thử ở `bhc-token-1`):

| STT | Model (`OPENROUTER_MODELS`) | Trạng thái ở `bhc-token-2` | Mã HTTP tham chiếu (`bhc-token-1`) | Ghi chú |
| :-: | --- | :---: | :---: | --- |
| 1 | `openai/gpt-5.4-mini` | Bỏ qua (theo đề) | `200` (`max_tokens=10`) | Hoạt động bình thường |
| 2 | `google/gemini-2.5-flash` | Bỏ qua (theo đề) | `200` (`max_tokens=10`) | Hoạt động bình thường |
| 3 | `perplexity/sonar` | Bỏ qua (theo đề) | `200` (`max_tokens=16`) / `400` (`max_tokens=10`) | Yêu cầu `max_tokens >= 16` |
| 4 | `deepseek/deepseek-v4.1-flash-1017` | Bỏ qua (theo đề) | `200` (`max_tokens=10`) | Hoạt động bình thường |

---

## 3. Kết quả gọi thử Gemini (`gemini-3.5-flash-lite`)

Endpoint: `POST https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent` với `GEMINI_API_KEY` (`sha8: 7f7f0125`), câu `"ok"`:

| Model | Khoá (`sha8`) | Mã HTTP | Status | Thông báo lỗi từ Google API | Kết luận |
| --- | :---: | :---: | :---: | --- | :---: |
| `gemini-3.5-flash-lite` | `7f7f0125` | **`402`** | `RESOURCE_EXHAUSTED` | `Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay.` | **Không đạt (`khong`)** |

---

## 4. Kết luận (`dat/khong`)

- **Kết luận tổng**: **`khong`**
  - **OpenRouter (`OPENROUTER_API_KEY`, `sha8: cf10d779`)**: **`dat`** — Đã nhận thêm `10 USD`, `total_credits = 30 USD`, `total_usage = 19.390246096 USD`, **số dư = `10.609753904 USD`** (`limit = 50 USD`, `limit_remaining = 30.609753904 USD`).
  - **Gemini trực tiếp (`GEMINI_API_KEY`, `sha8: 7f7f0125`)**: **`khong`** — Vẫn trả **`HTTP 402` (`RESOURCE_EXHAUSTED`)** do `GEMINI_API_KEY` dùng billing riêng trên Google AI Studio (`https://ai.studio/projects`) chưa có prepayment credits.
