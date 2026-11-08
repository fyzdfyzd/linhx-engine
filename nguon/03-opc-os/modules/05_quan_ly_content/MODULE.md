# Module 05: Quản lý Content & Nhân vật Đại diện (`05_quan_ly_content`)

## 1. Mục tiêu & Vai trò
Quản lý lịch nội dung, kho bài viết/kịch bản video ngắn, hồ sơ nhân vật đại diện (**Luna Nguyệt Mai** kế thừa từ `AmbassadorOS` `vendor/AmbassadorOS/seed/luna-vy.json` theo chỉ đạo của Chị Kể Chuyện CMO), và gọi **Máy tạo nội dung (Đề 01)** (`_DUNG_CHUNG/may_tao_noi_dung_adapter.py`) để chống AI slop.

- **Luật an toàn sắt (`QUY-CHUAN-OPC.md` 6.2 & 12.1)**: Mọi nội dung do Agent soạn đều ở trạng thái `pending_founder_approval` — tuyệt đối không tự đăng công khai khi chưa có Founder duyệt.

## 2. Năm Module con
1. **`5.1_nhan_vat_persona`**: Nạp Character Bible của `Luna Nguyệt Mai` (`luna-vy.json`, điểm nhất quán 97%, danh sách điều cấm `never`: không phán sức khoẻ, không hù doạ số phận, không bảo ai chia tay).
2. **`5.2_lich_noi_dung`**: Lập lịch 3–5 kịch bản TikTok/Reels + 2 bài blog SEO + 1 email danh sách chờ mỗi tuần.
3. **`5.3_xuat_bai_may_tao_noi_dung`**: Gọi `kiemChatLuong` / `taoNoiDung` của Đề 01 để kiểm tra chống AI slop.
4. **`5.4_kho_bai_cho_duyet`**: Lưu bài vào hàng đợi duyệt của Founder.
5. **`5.5_do_luong_bai`**: Theo dõi chỉ số lượt xem, tỷ lệ bấm sang landing page.

## 3. Giao kèo Sự kiện
- **Lắng nghe**: `content.yeu_cau_soan`
- **Phát ra**: `content.cho_founder_duyet`

## 4. Chạy độc lập
```powershell
python modules/05_quan_ly_content/module.py --demo
```
