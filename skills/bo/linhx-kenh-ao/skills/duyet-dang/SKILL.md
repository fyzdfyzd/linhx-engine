---
name: duyet-dang
description: Đưa bài cho Linh duyệt (nhận, sửa, góp ý, bỏ), rút luật viết từ lần sửa, và đăng qua cổng. Dùng khi có bài chờ duyệt hoặc tới giờ đăng.
---

# Duyệt và đăng

Gọi CLI là `python "${CLAUDE_PLUGIN_ROOT}/scripts/kenhao.py" --home <kênh>`.

1. `bai-ds --trang-thai cho_duyet`: trình Linh từng bài, kèm mục đích, ghi chú tiêu hoá gốc, điểm critic.
2. Theo lời Linh: nhận → `bai-duyet --id`; Linh sửa chữ → lưu bản sửa ra file rồi `bai-duyet --id --sua-file f --gop-y "..."`; góp ý → `--gop-y` (bài về trạng thái sửa); bỏ → `--bo`.
3. Sau mỗi lần Linh sửa: rút một luật viết ngắn, chỉ khi lần sửa nói rõ điều gì nên làm khác (`luat-viet --luat "..." --tu-duyet ID`).
4. `dang` (đăng mọi bài đã duyệt tới giờ) hoặc `dang --id`. Nếu bị chặn, báo lý do cho Linh; không tìm cách khác để đăng. Thêm `--thu` khi chạy thử.

Cổng đăng kiểm: giai đoạn cho đăng, trần bài/tuần, luật 10:1, có mục đích và ghi chú tiêu hoá, đã duyệt, điểm critic, nhãn AI, từ cấm, độ dài, giờ yên lặng, ngân sách ngày.
