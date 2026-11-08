---
name: bao-cao-va-sua
description: Ra báo cáo ABC (HTML + Markdown + kế hoạch 30 ngày), đọc kết quả cùng người dùng, và sinh bản sửa kỹ thuật (JSON-LD, llms.txt, robots). Dùng ở bước 6 của brand-check hoặc khi người dùng hỏi "nên sửa gì".
---

# Báo cáo và sửa

`brandcheck.py bao-cao -w <ws>` → `lan/<ngày>/bao-cao.html`, `bao-cao.md`, `diem.json`.

Đọc cùng người dùng theo thứ tự (không chỉ đưa con số):
1. **AVI và rơi ở bước nào** trong 5 bước agent đọc (Tìm, Nhận diện, Đối chiếu, Lọc, Đề xuất), và cờ đỏ.
2. **AI đang nói sai điều gì**: mở nguyên văn từng dòng (đường dẫn trong `diem.json → noi_sai[].file`), người dùng xác nhận.
3. **Có mặt và thị phần nhắc tên** kèm khoảng tin cậy; nếu khoảng rộng (> 30 điểm), nói rõ cần thêm lượt.
4. **Nguồn AI dẫn**: loại nguồn nào đang thắng; đối thủ được dẫn ở đâu.
5. **Kế hoạch 30 ngày**: tuần 1 sửa cái sai, tuần 2 bảng sự thật máy đọc được, tuần 3 nhất quán đa kênh, tuần 4 bên thứ ba + người đứng tên + đo lại.

Sinh bản sửa (công cụ gốc ai-visibility-skill trong `scripts/nen/`, MIT):
- JSON-LD: viết spec theo `nen/schema.example.json` từ brand-facts, chạy `python nen/aeo.py schema spec.json`.
- llms.txt: `python nen/aeo.py -w <thư mục tạm> init <domain> --name <tên>` rồi `llmstxt`.
- Kiểm một trang có trích được câu trả lời không: `python nen/aeo.py page <url>`, chấm theo `nen/content-rubric.md`.
- Mẫu robots.txt theo từng bot: `nen/technical-fixes.md`.

Đo lại sau 30 ngày: cùng `cau-hoi.json`, cùng mô hình, cùng số lượt, `--lan` mới; so hai `diem.json`. Đổi mô hình thì không so như xu hướng.
