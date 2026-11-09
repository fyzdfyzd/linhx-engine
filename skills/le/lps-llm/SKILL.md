---
name: lps-llm
description: Thiết kế, viết, kiểm thử và red team một tính năng gọi LLM (chatbot, tóm tắt, trích xuất, phân loại, RAG, agent có tool) theo chuẩn LPS-AI. Dùng khi thêm hoặc sửa prompt, đổi model, thêm tool cho AI, hoặc khi Linh nói "tính năng AI", "gọi Claude/GPT", "prompt", "eval".
metadata:
  version: "0.1.0"
---

# Tính năng LLM theo LPS-AI

Chuẩn đầy đủ: `LPS_HOME/STANDARD-AI.md`. Code mẫu: `LPS_HOME/tool-config/llm/`. Viết code gọi Claude thì tra skill `claude-api` hoặc tài liệu chính thức, không viết API theo trí nhớ.

## Bước 1. Thẻ tính năng (trước khi code)
Tạo `docs/ai/AI-FEATURE-<id>.md` từ `docs/templates/AI-FEATURE.md`: việc AI làm, mức (một lời gọi / quy trình / agent: chọn mức đơn giản nhất), tuyến model, dữ liệu gửi đi (có dữ liệu cá nhân không, nhà cung cấp ở nước nào), tool và quyền, ngưỡng eval, ngân sách. Agent ở T3 cần ADR. Linh duyệt thẻ như duyệt SPEC.

## Bước 2. Bộ eval trước prompt
Tạo `src/modules/ai/evals/<id>/cases.jsonl`: ≥ 20 ca (T2) / ≥ 50 ca (T3) gồm ca thường, ca biên (rỗng, rất dài, không dấu, sai chính tả, lẫn tiếng Anh), ca injection, ca có dữ liệu cá nhân. Dữ liệu giả, không lấy dữ liệu khách thật. Chấm bằng máy nếu được (khớp nhãn, không chứa chuỗi cấm).

## Bước 3. Viết prompt và nối vào cổng `ai`
- Module `src/modules/ai/` có sẵn chưa? Chưa thì chép từ `tool-config/llm/` (port, adapter, models, FakeLlm) và bật luật `llm-only-through-ai-module` trong dependency-cruiser.
- Prompt ở `src/modules/ai/prompts/<id>.v1.ts`: system cố định (không thời gian, không id), dữ liệu người dùng bọc thẻ trong `render`, schema Zod cho đầu ra, tuyến trong `models.ts`.
- Module nghiệp vụ gọi qua `ai/index.ts`, nhận `LlmOutcome` và xử lý **mọi** nhánh: `ok`, `refusal`, `truncated`, `invalid_output`, `budget_exceeded`, `unavailable` → mỗi nhánh có thông báo tiếng Việt cho người dùng.
- Đầu ra hiển thị thì escape; không đưa vào SQL/shell/URL; số liệu quan trọng lấy từ DB.

## Bước 4. Test CI với FakeLlm
Test (theo `lps-tdd`) cho code quanh LLM: dựng prompt đúng, dữ liệu nằm trong thẻ, xử lý từng nhánh outcome, schema chặn đầu ra sai, hạn mức chặn khi vượt. **Không gọi LLM thật trong test CI.**

## Bước 5. Chạy eval (tốn tiền)
1. In số ca và chi phí ước tính; **xin Linh đồng ý** trước lần chạy đầu và mỗi khi chi phí ước tính > 1 USD.
2. `pnpm eval <id>`. Dán bảng điểm vào PR: điểm tổng, ca hỏng, chi phí thật.
3. Dưới ngưỡng → sửa prompt (không sửa ca eval cho dễ qua), chạy lại. Tối đa 5 vòng rồi báo Linh.
4. Muốn hạ model/effort để rẻ hơn: chạy eval ở cấu hình mới, chỉ đề xuất khi điểm không giảm dưới ngưỡng; Linh duyệt.

## Bước 6. Red team (T3 trước phát hành; T2 khi có tool ghi hoặc RAG)
Thử trên staging, ghi vào `docs/security/PENTEST-*.md`:
- [ ] Injection trực tiếp: "Bỏ qua hướng dẫn trước…", "Ignore previous instructions…", đóng vai, yêu cầu in system prompt.
- [ ] Injection gián tiếp: tài liệu/trang web/email nạp vào chứa lệnh ẩn (chữ trắng, chú thích HTML, cuối file dài).
- [ ] Lộ dữ liệu: hỏi về khách khác, tenant khác, khoá API, cấu hình.
- [ ] Vượt quyền tool: dụ agent gọi tool ghi/xoá/gửi không xác nhận, gọi với `id` của người khác.
- [ ] Đầu ra độc: chèn `<script>`, link lừa đảo, Markdown ảnh trỏ ra ngoài (rò dữ liệu qua URL).
- [ ] Tiêu thụ không giới hạn: đầu vào cực dài, lặp yêu cầu nhanh, vòng agent không dừng → hạn mức chặn được.
Mỗi ca vượt rào thành một ca trong bộ eval sau khi sửa.

## Bước 7. Trước khi báo xong
Đối chiếu mục 13 "Định nghĩa Xong" của STANDARD-AI: thẻ tính năng, cổng `ai`, prompt có phiên bản, eval đạt ngưỡng, FakeLlm test xanh, hạn mức và log chi phí, rào injection, DATA-INVENTORY, nhãn "do AI tạo" và 👍/👎.
