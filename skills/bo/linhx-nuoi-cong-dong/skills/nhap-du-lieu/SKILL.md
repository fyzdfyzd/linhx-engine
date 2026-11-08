---
name: nhap-du-lieu
description: Biến dữ liệu thô về thành viên, hoạt động và đơn hàng (danh sách lớp, form, ghi chép nhóm Zalo, bình luận Facebook, file chat xuất ra) thành CSV đúng mẫu rồi nhập vào CSDL cộng đồng. Dùng khi Linh đưa file hoặc dán nội dung nhóm và nói "nhập", "cập nhật cộng đồng".
---

# Nhập dữ liệu

Mẫu cột ở `${CLAUDE_PLUGIN_ROOT}/mau/`: `thanh-vien.csv`, `su-kien.csv`, `don.csv`, `link.csv`.

## Loại sự kiện (cột `loai`)
`vao_nhom, tra_loi_khao_sat, cam_xuc, binh_luan, hoi, tra_loi_giup, chia_se_case, du_zoom, du_workshop, gioi_thieu, hoi_gia, hoi_lich, mua`; bài admin: `admin_dang, admin_nhac`. Trọng số ở `config/cong-dong.json`.

## Cách làm
1. Danh sách lớp/khảo sát cuối khoá → `thanh-vien.csv`. `ma` ổn định (ví dụ mã lớp + số thứ tự), `khoa` = mã EDU, `nhom` ∈ nhan-vien / quan-ly / hr-ld / c-level, `dong_y_lien_he` = 1 chỉ khi học viên đã tick đồng ý nhận tin.
2. Nhóm Zalo không có API nhóm: Linh/SO chụp hoặc chép đoạn chat tuần; Claude đọc và phân loại từng tin thành một dòng `su-kien.csv` (ai, loại, ngày, tóm 1 câu). Hỏi lại khi không chắc ai là ai; không đoán tên.
3. Zoom: danh sách người dự → `du_zoom`. Form đăng ký có `?ref=` → điền cột `ref`.
4. Hợp đồng, báo giá → `don.csv` (`trang_thai`: hoi, bao-gia, chot, da-thu, mat).
5. Chạy `nuoi.py nhap <loại> <file>`; dòng trùng tự bỏ qua, chạy lại không sao.
6. Không lưu số điện thoại, email trong cột ghi chú; giữ file trong thư mục cộng đồng trên máy.
