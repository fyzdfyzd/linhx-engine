---
name: tong-quan-tai-lieu
description: Tổng quan tài liệu có phương pháp (tìm có ghi lại, sàng lọc, tổng hợp theo chủ đề, kiểm trích dẫn DOI) cho bài báo, nghiên cứu học thuật và báo cáo chính sách. Dùng khi Linh cần tổng quan nghiên cứu cho bài nói, khoá học, hồ sơ tài trợ, bài dự thi, hoặc khi nghiên cứu nền của lab cần nguồn học thuật chứ không chỉ repo code.
---

# Tổng quan tài liệu (bản LINHX)

Mượn từ skill `literature-review` của K-Dense Scientific Agent Skills (MIT, xem `goc/LICENSE-KDENSE.md`). Quy trình gốc ở `goc/SKILL-GOC.md` và `goc/references/core_workflow.md`. Hai script tạo hình bằng AI (cần OPENROUTER_API_KEY) đã được bỏ ra.

**Khác skill nghiên cứu nền của lab:** nghiên cứu nền đọc **code repo** (luật số 2 của LINHX). Skill này dành cho **tài liệu viết**: bài báo, báo cáo, chính sách. Một lab có thể cần cả hai; ghi chung vào `01-NGHIEN-CUU-NEN.md`, chia mục riêng.

## Quy trình

1. **Câu hỏi và phạm vi:** chọn loại tổng quan (hệ thống, phạm vi hay tường thuật), tiêu chí chọn và loại, khoảng năm, ngôn ngữ (tiếng Việt và tiếng Anh).
2. **Tìm có ghi lại.** Ghi từng truy vấn, nguồn, ngày chạy và số kết quả vào `refs/tim-kiem.md`. Nguồn gồm Google Scholar, Semantic Scholar, arXiv, PubMed nếu cần, và nguồn Việt Nam (tạp chí trong nước, báo cáo bộ ngành).
3. **Chuẩn hoá và khử trùng lặp:** lưu kết quả thành một mảng JSON, mỗi bài là `{"title", "authors": [...], "year", "doi", "source", "citations"}`. Sau đó chạy:
   `python "<skill>/goc/scripts/search_databases.py" ketqua.json --deduplicate --summary --format markdown --output refs/ket-qua.md`
4. **Sàng lọc** theo tiêu đề và tóm tắt, sau đó đọc toàn văn. Ghi lý do loại từng bài.
5. **Tổng hợp theo chủ đề**, không tóm tắt từng bài một. Khung bài ở `goc/assets/review_template.md`.
6. **Kiểm trích dẫn:** `python "<skill>/goc/scripts/verify_citations.py" bai.md -o refs/kiem-trich-dan.json` (cần mạng). DOI tồn tại không có nghĩa là bài đó ủng hộ khẳng định; vẫn phải đọc bài.
7. Chạy `xac-minh-truoc-khi-bao-xong` trước khi giao.

`<skill>` là thư mục chứa file này. Trong Claude Code, đường dẫn đó là `${CLAUDE_PLUGIN_ROOT}/skills/tong-quan-tai-lieu`.

## Luật

- Không bịa tài liệu, tác giả, DOI hay trích dẫn. Không tìm thấy thì ghi là không tìm thấy.
- Kết quả tìm web không chứng minh là đã phủ đủ; ghi rõ giới hạn của lần tìm.
