---
name: de-xuat-tuan
description: Biến danh sách đề xuất tuần (tín hiệu mua, champion sang sales, đã giúp người, sắp lên cấp, quay lại, im lặng) thành việc cụ thể và tin nháp cho Linh/SO. Dùng sau khi chạy nuoi.py tuan hoặc khi Linh hỏi "tuần này nên chăm ai".
---

# Đề xuất tuần

Mẫu ý tưởng: Savannah (đề xuất có trạng thái), Orbit (champion → sales), 源雀 (nhận diện ý định mua). Script đã chọn tối đa 25 người theo ưu tiên.

1. Đọc `output/DE-XUAT-TUAN.csv`. Với mỗi dòng xem thêm lịch sử: `sqlite3 data/cong-dong.db "select ngay,loai,noi_dung from event where ma_thanh_vien='<ma>' order by ngay desc limit 10"`.
2. Soạn cho từng dòng: 1 câu vì sao, 1 việc, 1 tin nháp (≤ 60 chữ, nhắc lại điều họ đã nói/làm). Người chưa đồng ý nhắn riêng: tin nháp là bình luận trong nhóm.
3. Tín hiệu mua: gợi bậc offer kế tiếp trong `thang_offer` hợp với `nhom` (nhân viên → K2 2.0; quản lý → K3/workshop; HR-L&D → tool HR & L&D; C-level → K5). Không báo giá khi chưa có giá Linh chốt.
4. Champion: tin mời làm AI Champion (quyền lợi: Zoom riêng, ghi tên trong case, ưu tiên workshop) và xin giới thiệu HR/L&D, một tầng, không hoa hồng nhiều tầng.
5. Xuất `output/VIEC-TUAN-<ngày>.md` dạng checklist. Nhắc Linh ghi lại bằng `danh-dau`.
