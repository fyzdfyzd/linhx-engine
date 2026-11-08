---
name: viet-chuan
description: Tra cứu và chuẩn hoá từng giá trị dữ liệu Việt (SĐT đầu số cũ 11 số, CCCD/CMND, MST, ngày, tên không dấu, Unicode NFD, lỗi mã, bảng mã TCVN3/VNI, địa chỉ trước/sau sáp nhập 1/7/2025). Dùng khi Linh hỏi nhanh "số này đổi sang gì", "địa chỉ mới của …", hoặc khi viết recipe cần biết thao tác nào xử lý lỗi nào.
---

# Chuẩn hoá giá trị Việt

Thư viện: `${CLAUDE_PLUGIN_ROOT}/scripts/viet_chuan.py`. Mỗi hàm trả `(giá_trị_mới, cờ)`; cờ rỗng là ổn.

Thử nhanh một giá trị:
```
python -c "import sys; sys.path.insert(0, r'${CLAUDE_PLUGIN_ROOT}/scripts'); import viet_chuan as v; print(v.address_new('P. Phúc Xá, Q. Ba Đình, TP. Hà Nội'))"
```

| Lỗi | Hàm | Ghi chú |
|---|---|---|
| SĐT +84, dấu chấm, mất số 0, đầu số 11 số cũ (0162→032…) | `phone_vn` | Bảng đổi đầu số trong code, nguồn ở `refs/THI-TRUONG-VIET-NAM.md` |
| CCCD mất số 0, CMND 9 số | `cccd` | CCCD luôn bắt đầu bằng 0 (mã tỉnh) nên thêm lại an toàn; CMND chỉ gắn cờ |
| MST 10 số, 10-3, MST cá nhân 12 số (từ 1/7/2025) | `mst` | |
| Ngày d/m/y, d-m-y, d.m.y | `date_vn` | Mặc định ngày trước tháng; nghi kiểu Mỹ thì gắn cờ |
| Unicode tổ hợp, khoảng trắng | `nfc`, `trim` | Chạy đầu tiên |
| `Nguyá»…n` | `fix_mojibake` | Không cứu được thì gắn cờ |
| `NguyÔn V¨n` (TCVN3/VNI) | `flag_tcvn3` | Chỉ phát hiện; chuyển mã bằng Unikey Toolkit rồi chạy lại |
| Địa chỉ 3 cấp cũ | `address_new` | Cần `pip install underthesea`. Xã bị chia tách, không dấu, chỉ khớp tỉnh: giữ nguyên + gắn cờ |
| Tên viết hoa/thường lộn xộn, không dấu | `name_vn`, `khoa_ten` | Không tự xoá danh xưng ("Anh" có thể là tên) |
| Tiền tố công ty | `company_vn` | |

Giới hạn đã đo trên bộ mẫu (xem `output/KET-QUA-THU-V01.md`): địa chỉ không dấu và một số phường không có trong dữ liệu underthesea thì không đổi được, phải duyệt.
