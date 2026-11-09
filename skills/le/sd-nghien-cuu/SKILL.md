---
name: sd-nghien-cuu
description: Bước 0 Flow Pack. Nghiên cứu có nguồn trước khi viết series hoặc kịch bản (thể loại, khán giả, phim mẫu, nhịp, phong cách hình). Dùng khi bắt đầu một series hoặc một chủ đề mới.
metadata:
  version: "0.1.0"
---

# sd-nghien-cuu: nghiên cứu trước kịch bản

Học từ `research-director` của OpenMontage: không viết kịch bản từ trí nhớ; tìm nguồn thật, ghi lại, rồi mới đề xuất.

**Đầu vào:** chủ đề hoặc ý tưởng 1 câu của Linh, khán giả, nền tảng (TikTok, Reels, YouTube Shorts).
**Đầu ra:** `data/series/NGHIEN-CUU.md`. Trạm duyệt: `nghien_cuu`.

## Làm
1. Tìm ít nhất **5 nguồn** (web, báo, bài phân tích short drama, video mẫu trên nền tảng đích). Nếu Linh có ChatGPT Plus, có thể giao phần quét rộng cho **Deep Research** của ChatGPT rồi dán kết quả vào đây; Claude vẫn kiểm từng link trước khi dùng.
2. Ghi mỗi nguồn: link, ngày, 1–2 dòng rút ra, độ tin (cao/vừa/thấp).
3. Rút ra ít nhất **3 góc kể** khác nhau (ví dụ: hài đời thường, báo thù, bí ẩn), mỗi góc có bằng chứng từ nguồn.
4. Liệt kê **hình mẫu nhịp**: hook 3 giây đầu của 3 video mẫu, chúng làm gì ở giây 15 và ở cliffhanger.
5. Ghi **rủi ro**: nội dung trùng phim có bản quyền, chủ đề nhạy cảm, điều Veo làm kém (nhiều người, chữ trên hình, tay).
6. Nếu có video mẫu cụ thể, chạy thêm `sd-phan-tich-mau`.

## Mẫu `NGHIEN-CUU.md`
```
# Nghiên cứu: <chủ đề>
## Nguồn (≥ 5)
| # | Nguồn | Ngày | Rút ra | Độ tin |
## Góc kể (≥ 3)
## Hình mẫu nhịp
## Rủi ro
## Câu hỏi cho Linh
```

## Trạm
Trình bản nghiên cứu cho Linh. Chỉ khi Linh đồng ý mới ghi:
`python LAB016-PHIM-NGAN-AI/src/tools/nhat_ky.py LAB016-PHIM-NGAN-AI/data/<tap> duyet nghien_cuu --nguoi Linh`
rồi sang `sd-de-xuat`.
