---
name: radar-cuoc-thi
description: Quét cuộc thi sáng tạo, viết lách, báo chí, marketing, AI và giải thưởng tại Việt Nam, cập nhật kho, ra bản tin hạn nộp và lịch .ics. Dùng khi Linh hỏi "có cuộc thi nào", "quét cuộc thi", "radar giải thưởng", hoặc chạy định kỳ.
---

# Radar cuộc thi

Kho dữ liệu nằm ở **thư mục radar** (mặc định `D:\LINHX\LAB\LAB022-CUOC-THI-RADAR`, hoặc biến `RADAR_HOME`):
`config/sources.json` (nguồn), `config/profile.json` (hồ sơ chấm), `data/contests.json` (kho), `data/pipeline.json` (bài đang làm), `output/` (bảng, lịch, digest).
Script: `${CLAUDE_PLUGIN_ROOT}/scripts/contestscan.py` (Python chuẩn, không cần cài gì).

## Quy trình

1. **Quét máy** (nguồn RSS/HTML trong `sources.json`), đứng trong thư mục radar:
   `python "${CLAUDE_PLUGIN_ROOT}/scripts/contestscan.py" all --no-fetch`
   Đọc dòng `LỖI` trong kết quả: nguồn chết thì ghi `"active": false` và lý do vào `_note`, không xoá.
2. **Quét bằng tìm kiếm web** (phần máy không với tới: Facebook, trang JS, báo không có RSS). Chạy các truy vấn trong `config/sources.json` → `search_queries` bằng WebSearch, thêm tháng/năm hiện tại. Với mỗi kết quả là thể lệ cuộc thi **còn hạn hoặc sắp mở**:
   - mở trang thể lệ gốc (WebFetch), không tin trang tổng hợp;
   - ghi một mục vào `data/new-<ngày>.json` theo schema ở `references/schema.md`;
   - `deadline` chỉ điền khi đọc thấy trong thể lệ năm nay; nếu không, để `null` và điền `expected_deadline` theo mùa trước;
   - `verified: true` chỉ khi đã đọc trang chính thức hoặc bài báo đăng thể lệ.
   Rồi `python ".../contestscan.py" seed data/new-<ngày>.json` và `... score` `... report` `... digest`.
3. **Báo Linh** ngắn: số cuộc thi hạn trong 45 ngày, 3 cuộc thi đáng làm nhất (vì sao hợp branding), cuộc thi nào cần Linh quyết. Đính kèm `output/digest/DIGEST-<ngày>.md`. Không liệt kê lại cả bảng.

## Luật
- Không đăng ký, không nộp, không gửi email thay Linh.
- Đăng lại cùng cuộc thi ở nhiều báo: giữ một mục, link phụ vào `mentions` (script tự khử theo tiêu đề).
- Cuộc thi giới hạn tuổi, chỉ cho học sinh/sinh viên/hội viên hoặc chỉ nhận qua tổ chức: script tự gắn `Không đủ điều kiện` / `Kiểm điều kiện` / `Qua tổ chức`; nếu sai thì ghi đè bằng trường `"gate"` trong dữ liệu.
- Chạy định kỳ: Windows Task Scheduler gọi `chay-radar.bat` (thứ Hai 7:30), hoặc routine Claude hằng tuần chạy bước 2.
