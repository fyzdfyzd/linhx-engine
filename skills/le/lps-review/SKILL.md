---
name: lps-review
description: Review/phản biện độc lập một thay đổi (diff, PR, SPEC) với ngữ cảnh sạch, ưu tiên mô hình hoặc công cụ khác với bên viết code. Dùng trước khi merge, khi Linh nói "review", "phản biện", "critique", "soi lỗi".
metadata:
  version: "0.1.0"
---

# Review độc lập

Người viết không tự chấm bài của mình. Review chạy trong **ngữ cảnh mới** (subagent mới, phiên mới, hoặc công cụ khác: Claude viết thì Codex/Antigravity review, và ngược lại).

## Đầu vào
`git diff <nhánh chính>...HEAD`, SPEC liên quan, `AGENTS.md`. Không đưa lịch sử trò chuyện của bên viết code.

## Thứ tự soi (dừng ở mục nào có lỗi nghiêm trọng thì báo ngay)
1. **Đúng:** có làm đúng mọi AC? Trường hợp biên: rỗng, null, trùng, đồng thời, múi giờ (Asia/Ho_Chi_Minh), tiếng Việt có dấu, số tiền (dùng số nguyên đồng, không float).
2. **Bảo mật:** phân quyền ở mọi endpoint (đọc được dữ liệu người khác không?), validate đầu vào bằng Zod ở ranh giới, truy vấn tham số hoá, không lộ bí mật/dữ liệu cá nhân trong log hoặc phản hồi lỗi, đầu vào LLM được coi là không tin cậy.
3. **Test:** test có thật sự fail nếu code sai? Có test bị sửa/skip? Có mock quá tay?
4. **Kiến trúc:** module có import xuyên vào nội bộ module khác (ngoài `index.ts`)? Có logic nghiệp vụ trong UI hoặc route handler? Có phụ thuộc mới không có ADR?
5. **Đơn giản:** có code thừa, trừu tượng sớm, cấu hình không ai dùng? Có cách ngắn hơn một nửa?
6. **Giao diện** (nếu có): đủ trạng thái rỗng/đang tải/lỗi, nhãn tiếng Việt rõ, chạm được trên 360px, tương phản đủ.

## Đầu ra
Bảng phát hiện, sắp theo mức: **Chặn** (phải sửa trước merge) · **Nên sửa** · **Gợi ý**. Mỗi dòng: file:dòng, vấn đề, kịch bản cụ thể gây lỗi, cách sửa. Không có phát hiện mức Chặn thì ghi rõ "Không có lỗi chặn" và những gì đã kiểm.

Bên viết code xử lý từng phát hiện Chặn/Nên sửa (sửa, hoặc ghi lý do không sửa), chạy lại `lps-tu-sua`, dán kết quả vào PR.

## Cách gọi chéo công cụ
- Claude Code → nhờ Codex: `codex exec "Review theo .claude/skills/lps-review/SKILL.md cho diff hiện tại. Chỉ đọc, không sửa file."`
- Claude Code → nhờ Antigravity: `agy -p "<cùng câu trên, đường dẫn .agents/skills/...>"`
- Không có công cụ khác: mở subagent mới chỉ với đầu vào ở trên.
