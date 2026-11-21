may: may-2
loai: kiem
tran_phut: 8

## Mục tiêu
Đẩy 3 commit A/B lên GitHub để Claude chấm bằng test ẩn.
## File được sửa
Không sửa file nào. Chỉ push.
## Cấm động
Không sửa code, không commit thêm, không push nhánh khác ngoài 3 nhánh dưới. Push lỗi (đăng nhập): DỪNG, trả `CAN-LINH: ...; LENH: ...`.
## Test bằng chứng
Chạy tiền cảnh, lần lượt với X = argon-high, neon-high, neon-medium:
`git -C C:\linhx\wt-neon-ab-X push https://github.com/fyzdfyzd/linhx-engine HEAD:refs/heads/agy/neon-ab-X`
KET-QUA ≤ 6 dòng: mỗi nhánh một dòng `X <sha> OK|LOI`.
