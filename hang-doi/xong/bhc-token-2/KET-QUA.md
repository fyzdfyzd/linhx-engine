model: gemini-4-argon-high
phieu: bhc-token-2
may: may-2
trang_thai: xong
tep_doi: bang-chung/bhc-token-2/KET-QUA.md
drive: (khong)
phut: 4.76
token: vao=66697 ra=10817

Đã kiểm tra trên VM prod `ifagent-event` (`zone=asia-southeast1-b`, `project=ifagent-event-2026`) từ `/opt/ifagent/infra/brand-health.env` (chỉ đọc qua biến shell, không in/ghi giá trị khoá) và push kết quả lên nhánh `agy/bhc-token-2`:
- [KET-QUA.md](file:///C:/linhx/hang-doi/bang-chung/bhc-token-2/KET-QUA.md) ([bản trong lam-viec](file:///C:/linhx/hang-doi/runner/viec/lam-viec/bang-chung/bhc-token-2/KET-QUA.md))

---

### 1. Bảng số dư OpenRouter (`OPENROUTER_API_KEY`, `sha8: cf10d779`)

Khoản **+10 USD** Linh nạp lúc 14:13 VN đã vào ví OpenRouter (`total_credits` tăng từ `20` lên `30` USD):

| Chỉ số | Trước khi nạp (`bhc-token-1`) | Hiện tại (`bhc-token-2`) | Thay đổi | Nguồn API |
| --- | ---: | ---: | ---: | --- |
| `limit` | `50` | **`50`** | `0` | `/api/v1/key` |
| `usage` | `19.385236096` | **`19.390246096`** | `+0.00501` | `/api/v1/key` |
| `limit_remaining` | `30.614763904` | **`30.609753904`** | `-0.00501` | `/api/v1/key` |
| `total_credits` | `20` | **`30`** | **`+10.00000`** | `/api/v1/credits` |
| `total_usage` | `19.385236096` | **`19.390246096`** | `+0.00501` | `/api/v1/credits` |
| **Số dư (`total_credits - total_usage`)** | **`0.614763904` USD** | **`10.609753904` USD** | **`+9.99499` USD** | `total_credits - total_usage` |

---


...[cat bot]...
SD`).
  - **Gemini trực tiếp (`sha8: 7f7f0125`)**: **`khong`** — Vẫn trả **`HTTP 402` (`RESOURCE_EXHAUSTED`)** vì `GEMINI_API_KEY` gọi trực tiếp Google AI Studio (`generativelanguage.googleapis.com`), dùng ví Prepayment Credits riêng trên Google AI Studio chứ không dùng số dư OpenRouter.

```
CAN-LINH: Nạp thêm Prepayment Credits (hoặc bật Pay-as-you-go billing) cho project của GEMINI_API_KEY (sha8: 7f7f0125) trên Google AI Studio tại https://ai.studio/projects (hoặc cấp GEMINI_API_KEY mới còn credit); LENH: https://ai.studio/projects
```
