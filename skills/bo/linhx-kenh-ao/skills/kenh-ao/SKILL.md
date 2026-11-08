---
name: kenh-ao
description: Điều phối một phiên nuôi kênh người ảo (LAB040). Dùng khi Linh nói "chạy phiên", "nuôi kênh Mây", "tick kênh ảo", hoặc khi lịch gọi theo giờ. Đọc giai đoạn và phiên rồi gọi đúng skill con.
---

# Điều phối phiên kênh người ảo

Gọi CLI là `python "${CLAUDE_PLUGIN_ROOT}/scripts/kenhao.py" --home <kênh>`. Mọi ghi chép đi qua CLI; không ghi thẳng file CSDL.

0. Đọc `ho-so/bai-hoc.md` (bài học của chính kênh, do `hoc-ngay` viết) trước mọi việc.
1. `giai-doan`: biết đang ở G0, G1, G2 hay G3, hạn mức hôm nay, tiêu chí lên giai đoạn, tỷ lệ hấp thu/tạo 7 ngày.
2. `phien`: lấy kịch bản phiên gần giờ hiện tại. Chỉ làm các bước có trong `buoc`; bước nào không có nghĩa là giai đoạn chưa cho.
3. Gọi skill con theo loại bước: `doc`, `tieu_hoa`, `trend` → **lang-thang**; `vong`, `cham` → **ket-than**; `tao` → **tao-bai** rồi **duyet-dang**; `hop_thu` → **hop-thu**; `hoc` → **hoc-ngay** mỗi tối, thêm **hoc-tuan** Chủ nhật.
4. Tỷ lệ thời gian: phần đọc, xem, chạm, tiêu hoá phải chiếm ít nhất 10 lần phần tạo. Nếu `giai-doan` báo tỷ lệ dưới 10, phiên này bỏ bước tạo và đọc thêm.
5. Cuối phiên: `bang-tin`, báo Linh 3 dòng (đọc gì, chạm ai và vì sao, cái gì đang chờ Linh duyệt). Mọi việc chờ Linh nằm trên bàn đăng (skill **ban-dang**); Linh chỉ bấm. Brand (`hop-thu-ds --trang-thai chuyen_linh`) vẫn báo riêng.

Không bao giờ: giả là người thật, chạm persona cùng nhà, nhắn riêng người chưa nhắn trước, tranh luận chủ đề cấm, sửa luật gốc trong `ho-so/hanh-vi.md` khi chưa hỏi Linh.
