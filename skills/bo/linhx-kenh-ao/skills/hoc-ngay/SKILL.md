---
name: hoc-ngay
description: Vòng tự học cuối mỗi ngày của kênh: tính lại hậu nghiệm từ số liệu, bàn đăng, quan hệ và cổng; tự áp thay đổi nhỏ có trần; rút luật viết từ lần Linh sửa để Linh bấm nhận. Dùng mỗi tối sau khi kéo số liệu, hoặc khi Linh hỏi "hôm nay học được gì".
---

# Tự học mỗi ngày

Gọi CLI là `python "${CLAUDE_PLUGIN_ROOT}/scripts/kenhao.py" --home <kênh>`. Lịch máy (Task Scheduler/cron) chạy bước 1 lúc 23:10; agent làm bước 2-3.

1. `so-lieu` rồi `hoc-ngay` → `bao-cao/HOC-<ngày>.md` và cập nhật `ho-so/bai-hoc.md`.
2. Đọc phần "Việc của agent tối nay" trong file HOC:
   - Với các lần Linh sửa hoặc bỏ: rút tối đa 2 luật viết có thể làm theo được (ví dụ "mở bằng chuyện đã xảy ra, không mở bằng kết luận"), ghi bằng `bai-hoc-them --noi-dung "..." --tang 2 --tu-duyet <id,id>`. Sáng mai Linh bấm Nhận trên bàn đăng.
   - Không rút luật từ một lần sửa lẻ không rõ ý. Không đề xuất đổi flaw, giọng gốc, hanh-vi, hang-rui-ro: đó là tầng 3, chỉ ghi vào mục đề xuất cho Linh.
3. Đầu phiên hôm sau: đọc `ho-so/bai-hoc.md` trước khi làm gì. Khi viết bài, chọn hook và cảm xúc bằng `goi-y --chieu hook --lua-chon a,b,c` (Thompson sampling: vẫn thử lựa chọn ít dữ liệu, dồn dần về cái thắng).

Ba tầng thay đổi:
- Tầng 1 tự áp: hậu nghiệm Beta, hệ số tỷ trọng trụ cột (±0,1 mỗi ngày, kẹp 0,5-1,5, có vùng trễ, xét lại sau 7 ngày và tự hoàn nếu kém), gợi ý hook/cảm xúc, bài học "agent tự soi" về lý do bị cổng chặn.
- Tầng 2 Linh bấm một lần: luật viết, dời giờ đăng, ưu tiên kiểu chạm.
- Tầng 3 Linh sửa tay: luật gốc và persona.

Tín hiệu chỉ thành bài học khi mỗi nhóm có ít nhất 5 mẫu và xác suất nhóm dẫn đầu tốt hơn nhóm thứ hai từ 0,9. Hệ thống tự chấm mình bằng điểm Brier theo tuần (0,25 là đoán bừa); nếu Brier không giảm sau 4 tuần, báo Linh là tín hiệu của kênh còn quá yếu để học, đừng tin các bài học tầng 1.
