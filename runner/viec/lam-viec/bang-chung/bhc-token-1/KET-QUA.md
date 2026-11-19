dat: khong
phieu: bhc-token-1
nhanh: agy/bhc-token-1

# KET-QUA: bhc-token-1 — Kiểm tra khoá OpenRouter & Gemini trên VM prod (`ifagent-event`)

- **VM kiểm tra**: `ifagent-event` (`zone=asia-southeast1-b`, `project=ifagent-event-2026`)
- **File cấu hình**: `/opt/ifagent/infra/brand-health.env` (chỉ đọc bằng biến shell, không sửa, không in khoá)
- **Mã băm khoá (`sha8`)**:
  - `OPENROUTER_API_KEY` (`sha8`): `cf10d779`
  - `GEMINI_API_KEY` (`sha8`): `7f7f0125`
- **Cấu hình model trong env**:
  - `OPENROUTER_MODELS`: `openai/gpt-5.4-mini,google/gemini-2.5-flash,perplexity/sonar,deepseek/deepseek-v4.1-flash-1017`
  - `GEMINI_MODEL`: `gemini-3.5-flash-lite`
- **Kết luận (`dat/khong`)**: **`khong`**
  - **Lý do chính**:
    1. **Gemini (`gemini-3.5-flash-lite`) trả về `HTTP 402` (`RESOURCE_EXHAUSTED`)**: `Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing.` — Khoá `GEMINI_API_KEY` (`sha8: 7f7f0125`) đã cạn sạch prepayment credits.
    2. **OpenRouter còn hoạt động nhưng số dư thực còn rất thấp (`$0.6148 USD`)**: `total_credits = 20 USD`, `total_usage = 19.385236096 USD` → **số dư = `0.614763904 USD`** (dù `limit` của key đặt là `50 USD` và `limit_remaining = 30.614763904 USD`, số dư tín dụng thực nạp của tài khoản chỉ còn `~0.61 USD`).
    3. Trong 4 model OpenRouter khi gọi với `max_tokens: 10`, có 3 model trả `HTTP 200`, riêng `perplexity/sonar` trả `HTTP 400` vì Perplexity yêu cầu `max_tokens >= 16` (`max_tokens must be at least 16`; khi thử với `max_tokens: 16` thì `perplexity/sonar` trả `HTTP 200`).

---

## 1. Bảng số dư OpenRouter (`/api/v1/key` & `/api/v1/credits`)

| Chỉ số | Trước khi gọi thử (USD) | Sau khi gọi thử (USD) | Nguồn API | Ghi chú |
| --- | ---: | ---: | --- | --- |
| `limit` | `50` | `50` | `GET /api/v1/key` | Trần giới hạn cấu hình trên API key (`sha8: cf10d779`) |
| `usage` | `19.385169186` | `19.385236096` | `GET /api/v1/key` | Tổng mức sử dụng của API key (`usage_daily`: `10.782895361`) |
| `limit_remaining` | `30.614830814` | `30.614763904` | `GET /api/v1/key` | Trần còn lại của riêng API key (`limit - usage`) |
| `total_credits` | `20` | `20` | `GET /api/v1/credits` | Tổng tín dụng đã nạp vào tài khoản OpenRouter |
| `total_usage` | `19.385169186` | `19.385236096` | `GET /api/v1/credits` | Tổng tín dụng đã tiêu dùng của tài khoản |
| **Số dư (`total_credits - total_usage`)** | **`0.614830814`** | **`0.614763904`** | `total_credits - total_usage` | **Số dư thực còn lại của tài khoản (~$0.615 USD)** |

---

## 2. Kết quả gọi thử từng model trong `OPENROUTER_MODELS`

Câu thử: `"Trả lời: ok"`, tham số `max_tokens: 10` tới `https://openrouter.ai/api/v1/chat/completions`:

| STT | Model (`OPENROUTER_MODELS`) | Provider | Mã HTTP (`max_tokens=10`) | Phản hồi / 1 dòng lỗi (nếu có) | Kiểm chứng thêm |
| :-: | --- | --- | :-: | --- | --- |
| 1 | `openai/gpt-5.4-mini` | OpenAI | **`200`** | Không lỗi — `content: "ok"` (`prompt_tokens: 11, completion_tokens: 5, cost: $0.00003075`) | Đạt |
| 2 | `google/gemini-2.5-flash` | Google AI Studio | **`200`** | Không lỗi — `content: "Chào bạn! Bạn vừa sử dụng \"ok\""` (`finish_reason: "length", cost: $0.000029`) | Đạt |
| 3 | `perplexity/sonar` | Perplexity | **`400`** | `Provider returned error: {"error":{"message":"max_tokens must be at least 16","type":"invalid_request","code":400,"param":"max_tokens"}}` | Khi gọi với `max_tokens: 16` → **`HTTP 200`**, `content: "ok"` (`cost: $0.00501`) |
| 4 | `deepseek/deepseek-v4.1-flash-1017` | Particle AI | **`200`** | Không lỗi — `finish_reason: "length"`, `content: null`, `reasoning: "We need answer to user \"Trả lời"` (10 token dùng vào reasoning, `cost: $0.00000716`) | Đạt |

---

## 3. Kết quả gọi thử Gemini (`gemini-3.5-flash-lite`)

Endpoint: `POST https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent` với `GEMINI_API_KEY` (`sha8: 7f7f0125`), câu `"ok"`:

| Model | Khoá (`sha8`) | Mã HTTP | Status | 1 dòng lỗi (nếu có) | Kết luận |
| --- | :---: | :---: | :---: | --- | :---: |
| `gemini-3.5-flash-lite` | `7f7f0125` | **`402`** | `RESOURCE_EXHAUSTED` | `Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay.` | **Không đạt (`khong`)** |

---

## 4. Kết luận chung (`dat/khong`)

- **Kết luận sức khỏe token prod**: **`khong`**
  - **`GEMINI_API_KEY` (`sha8: 7f7f0125`)**: **Không đạt (`HTTP 402 RESOURCE_EXHAUSTED`)** — Đã hết sạch prepayment credits trên Google AI Studio.
  - **`OPENROUTER_API_KEY` (`sha8: cf10d779`)**: **Hoạt động (`HTTP 200` cho 3/4 model ở `max_tokens=10` và 4/4 model ở `max_tokens>=16`), nhưng số dư thực `total_credits - total_usage` chỉ còn `$0.614763904 USD` (~$0.615)**, cần nạp thêm credits sớm để tránh gián đoạn trên prod.
