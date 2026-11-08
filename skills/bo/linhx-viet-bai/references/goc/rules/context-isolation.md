# Context Isolation — Cách Ly Ngữ Cảnh

> **MỨC ĐỘ: BẮT BUỘC TUYỆT ĐỐI**

## Nguyên Tắc 1: Cách ly giữa các Project
Mỗi dự án viết (`Idea_{Timestamp}_{Slug}/`) là một **thực thể hoàn toàn độc lập**. KHÔNG được sử dụng ngữ cảnh, dữ liệu, hoặc ý tưởng từ bất kỳ folder `Idea_*/` nào khác.

### CẤM TUYỆT ĐỐI
- ❌ Đọc file từ folder `Idea_*/` khác
- ❌ Trích dẫn, tham chiếu, hoặc "nhớ lại" nội dung từ bài viết khác
- ❌ Copy ý tưởng, anecdotes, insights từ project khác
- ❌ Sử dụng `_lessons_learned.md` của project khác để ảnh hưởng nội dung bài viết
- ❌ So sánh hoặc liên hệ với bài viết trong project khác

### ĐƯỢC PHÉP
- ✅ Đọc files **trong chính folder project hiện tại** (01→08, _status, _agent_log...)
- ✅ Đọc `spec.md`, `.agent/rules/`, `.agent/skills/`, `.agent/workflows/`, `_templates/`
- ✅ Sử dụng `_lessons_learned.md` của project khác **CHỈ cho cải thiện quy trình**

---

## Nguyên Tắc 2: Cách ly giữa 3 Variants trong cùng Project
Khi viết **Variant A, B, C** từ cùng 1 đề bài:

### CẤM TUYỆT ĐỐI
- ❌ Khi viết Variant B, đọc `Variant_A/08_Final_Output.md` hoặc draft của A
- ❌ Copy câu, đoạn, anecdote, hoặc cấu trúc từ variant khác
- ❌ Tham khảo critic feedback của variant khác để "né lỗi" sẵn
- ❌ Dùng cùng personal anecdote cho 2+ variants

### ĐƯỢC PHÉP
- ✅ Đọc files **chung** (01→05) — vì research là shared
- ✅ Đọc `Variant_X/06_AI_Curated_List.json` **của chính variant đang viết**
- ✅ So sánh 3 variant **CHỈ ở bước Best Pick** (sau khi cả 3 đã hoàn thành)

### Lý Do
- Mỗi variant phải có góc nhìn, tone, và anecdotes riêng biệt
- Nếu variant lẫn ý nhau → mất ý nghĩa của hệ thống 3 phương án
- Critic feedback của A không liên quan đến B (vì khác góc nhìn)
