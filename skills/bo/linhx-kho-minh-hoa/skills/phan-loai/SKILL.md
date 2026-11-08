---
name: phan-loai
description: Phân loại các hình trong hàng chờ của kho minh hoạ ý tưởng theo hai trục họ phong cách × cơ chế ý tưởng, viết "hình này nói gì", ghi thẻ ảnh hoặc đưa vào hàng chờ Linh duyệt.
---
# Phân loại hình (M4)

Đầu vào: `KHO/nguon/cho-phan-loai.jsonl` (từ skill `loc`). Từ điển ĐÓNG:
- `../../schemas/tu-dien-y-tuong.json`: `ho_phong_cach` (10 họ), `co_che_y_tuong` (11 cơ chế), `dung_de`, `do_phuc_tap`
- `../../schemas/tu-dien-be-mat.json`: medium, net_ve, to_mau, bang_mau, ty_le, hinh_khoi
Không tự đặt giá trị mới. Thấy cần giá trị mới thì ghi vào `KHO/anh/de-xuat-tu-dien.md` cho Linh duyệt.

## Mỗi mục (làm theo lô 10)
1. Xem ảnh: đọc file `anh_tam` bằng Read. Không có ảnh (lỗi tải, link dán) thì mở `link_goc` trong Chrome và xem ở đó.
2. Đọc `chu_thich_goc` + `hashtag` để hiểu ý tác giả; không chép nguyên chú thích vào thẻ.
3. Trả lời theo thứ tự, mỗi câu 1 dòng:
   - **Hình nói gì?** (`y_tuong_1_cau`, tiếng Việt, ≤ 25 chữ, kiểu "mạng xã hội là cái lồng đẹp")
   - **Cơ chế nào làm nó đắt?** 1-2 id `co_che_y_tuong`. Hỏi: nếu bỏ cơ chế này hình còn ý không?
   - **Họ phong cách?** 1-2 id `ho_phong_cach`, đối chiếu `dau_hieu`.
   - **Bề mặt**: medium, net_ve, to_mau, so_mau (đếm), bo_cuc (giữa/lệch/đối xứng/khung đôi).
   - **Chủ đề**, **dung_de**, **do_phuc_tap**.
   - **Độ chắc** 1-3.
4. Độ chắc 3 → nối vào `KHO/anh/the-anh.jsonl` theo `../../schemas/the-anh.schema.json`. Độ chắc 1-2 → `KHO/anh/cho-duyet.jsonl` kèm câu hỏi ngắn cho Linh.
5. Mục có `trung_voi`: chỉ thêm `link_goc` vào trường `ban_dang_lai` của thẻ gốc, không tạo thẻ mới.

## Cuối lô
- Báo: số thẻ, phân bố họ × cơ chế (bảng nhỏ), 3 hình "đắt" nhất và vì sao.
- Lần đầu (50 hình): chọn 10 hình đưa Linh chấm để đo độ khớp ở trục cơ chế; mục tiêu ≥ 8/10, chưa đạt thì sửa `dau_hieu`/`mo_ta` trong từ điển rồi chạy lại.
- Nhắc chạy `loc.py --don-tam`.
