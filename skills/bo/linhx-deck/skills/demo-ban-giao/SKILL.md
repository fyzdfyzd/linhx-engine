---
name: demo-ban-giao
description: Bước 14 và 15 của quy trình deck proposal - dựng demo hoặc prototype cho offer (mockup Claude Design, trang HTML một màn, agent mẫu chạy được) và đóng gói bàn giao (link deck, PDF, ghi chú người nói, nguồn, câu hỏi phản biện, thư gửi khách). Dùng khi Linh cần demo cho khách hoặc chuẩn bị đi trình bày.
---

# Demo và bàn giao (bước 14–15)

Script: `python "${CLAUDE_PLUGIN_ROOT}/scripts/deck.py"`.

## Bước 14. Demo / prototype → `14-prototype/`

Chọn loại theo offer, ghi vào `14-prototype/README.md`:
| Offer | Demo hợp | Cách làm |
|---|---|---|
| Đào tạo, workflow AI | Một quy trình thật của khách chạy trước/sau | Prompt + dữ liệu giả lập, kết quả tính bằng code |
| Agent, phần mềm | Agent mẫu hoặc màn hình chính | Trang HTML một màn, hoặc Claude Design (kiểu Design) dùng Design System BU |
| Chiến dịch, nội dung, phim | Key visual, kịch bản 30 giây, storyboard | Ảnh ChatGPT Plus theo gói bước 11 |
| Sự kiện | Sơ đồ trải nghiệm khách tham dự | Slide `lo-trinh` + 2–3 ảnh |
| Không cần | Bỏ qua | Ghi lý do |

- Demo phải chạy được trên máy Linh hoặc mở được bằng link. Dữ liệu khách thật không vào demo; dùng dữ liệu giả lập ghi rõ "GIẢ LẬP".
- Viết **kịch bản demo 3 bước** (3 phút) và mục **"Điều demo không chứng minh"** để Linh không hứa quá.

## Bước 15. Bàn giao → `15-ban-giao/`

1. `deck.py kiem-deck <dir> --ban-cuoi`: không còn `[CẦN LINH]`, `[Linh chốt]`.
2. Điền `15-ban-giao/README.md`: link deck, PDF/PPTX (tải từ Claude Slides), nguồn (02-bang-chung.csv), 5–10 câu phản biện khách có thể hỏi (mỗi câu kết thúc bằng '?') kèm câu trả lời ngắn (lấy từ skill `phan-bien` nếu đã chạy), thư gửi khách (5–8 câu, nhắc quyết định cần đưa ra và hạn; đầu thư ghi 'NHÁP, chưa gửi – chờ Linh', Claude không bao giờ gửi), việc D+1, D+7.
3. Thư gửi khách là **nháp**. Không gửi, không đăng gì ra ngoài khi Linh chưa bảo.
4. `deck.py cong <dir> 15`, rồi `deck.py trang-thai <dir>` báo Linh bảng 15 bước.
