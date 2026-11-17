may: may-1
loai: trinh-duyet
tran_phut: 15
khong_tien_phut: 15
tu_sua: 0
phu_thuoc: kn-td-deep-research-m1-c

# kn-td-colab-m1-c
Lượt 3 (Browsentic máy 1 đã sửa 18/11 05:10, bridge chạy). Đọc lại DE-BAI.md, luật 3, 10–13 mới.
Đọc và làm theo luật chung `viec/kn-thu/DE-BAI.md` (bắt buộc).

Kỹ năng: chạy Google Colab. Dùng tài khoản chủ gói Ultra (aimarketing…, Chrome máy 1 /u/6) nếu thấy; không thì tài khoản đang mở, ghi rõ.
Tạo sổ tay mới tên `kn-thu-colab`, chọn GPU tốt nhất được phép (không bấm nâng cấp), chạy ô:
```
!nvidia-smi --query-gpu=name,memory.total --format=csv
print(sum(range(10**7)))
```
ĐẠT khi: ô chạy ra đúng 49999995000000. Trả: loại GPU (hoặc "chỉ CPU"), danh sách máy chạy hiện ra trong Đổi loại thời gian chạy, đơn vị tính toán còn lại nếu hiện. Xong thì Ngắt kết nối và xoá thời gian chạy.
