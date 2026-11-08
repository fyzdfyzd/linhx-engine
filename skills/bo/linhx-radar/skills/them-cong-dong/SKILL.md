---
name: them-cong-dong
description: Thêm một hiệp hội, cộng đồng hoặc sự kiện mới vào radar: tìm đủ kênh, nhà tài trợ các mùa, KOL, chủ đề, pain point, họ đã có gì, rồi tạo nguồn quét. Dùng khi Linh nói "thêm cộng đồng X", "theo dõi hội Y", "tìm các tổ chức giống CSMO".
---

# Thêm cộng đồng

1. Tìm (WebSearch, song song tiếng Việt + tiếng Anh): website, fanpage, group, YouTube, LinkedIn, TikTok, Zalo OA; bài báo về các mùa sự kiện 2–3 năm gần nhất.
2. Mở trang gốc (WebFetch) để lấy: đơn vị đứng sau, quy mô, mô hình doanh thu, chương trình đã có; danh sách nhà tài trợ theo hạng và năm; diễn giả, cố vấn, giám khảo; chủ đề từng mùa; pain point họ nêu (câu chữ của chính họ).
3. Ghi `data/new-<ngày>-<id>.json` theo `../radar-cong-dong/references/schema.md`. Đặt `uu_tien` 0–10 theo độ khớp với offer LINHX (`config/offers.json`) và quy mô.
4. Thêm nguồn vào `config/sources.json`: ít nhất 1 `gnews` (tên cộng đồng trong ngoặc kép), `youtube` nếu có kênh, `page` cho trang nhà tài trợ và trang diễn giả nếu có.
5. Chạy `congdong.py seed <file>` → `score` → `export`. Báo Linh: tổ chức là ai, cộng đồng đau gì, 3 DN và 3 KOL đáng chú ý nhất, offer nào hợp.

Không bịa tên nhà tài trợ hay diễn giả. Thấy logo mà không đọc được tên thì ghi vào `_note` cộng đồng, không đoán.
