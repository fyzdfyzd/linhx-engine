---
name: xac-minh-truoc-khi-bao-xong
description: "Cổng kiểm trước khi nói \"xong\", \"chạy được\", \"đã sửa\", \"đã gửi file\": phải có bằng chứng mới từ lượt này. Dùng khi sắp báo kết quả cho Linh, đánh dấu pha [x] trong PLAN.md, đổi trạng thái lab sang WORKS, hoặc giao file."
---

# Xác minh trước khi báo xong

## Luật sắt

**KHÔNG BÁO XONG KHI CHƯA CÓ BẰNG CHỨNG MỚI.**

"Mới" nghĩa là lấy được trong chính lượt này, sau lần sửa cuối cùng. Kết quả của lần chạy trước, trí nhớ hay "chắc là được" đều không tính.

## Cổng 5 bước

Trước mỗi câu khẳng định:

1. **Xác định:** câu khẳng định này cần lệnh hay thao tác nào để chứng minh?
2. **Chạy:** chạy đầy đủ ngay bây giờ, không chạy một phần.
3. **Đọc:** đọc hết kết quả, kể cả mã thoát và số lỗi hoặc cảnh báo.
4. **Đối chiếu:** kết quả có thật sự khớp với câu khẳng định không?
5. **Báo:** chỉ khi khớp mới báo, và kèm bằng chứng (lệnh cộng dòng kết quả, đường dẫn file, link). Nếu không khớp, báo đúng trạng thái thật.

## Bằng chứng tối thiểu theo loại việc

| Khẳng định | Bằng chứng |
|---|---|
| Script hoặc plugin chạy được | Lệnh đã chạy và vài dòng kết quả, mã thoát 0 |
| Đã sửa lỗi | Chạy lại đúng kịch bản gây lỗi, thấy hết lỗi |
| Đã tạo hoặc sửa file | Mở lại file (đọc lại sau khoảng 10 giây nếu là thư mục dùng chung), thấy đúng nội dung |
| Đã giao file cho Linh | Đường dẫn file tồn tại; đính kèm thành công |
| Số liệu, hạn nộp, điều kiện | Link nguồn chính thức và ngày đọc |
| Lab đạt WORKS | Từng tiêu chí "chạy được" trong PLAN.md hoặc OVERVIEW.md có bằng chứng riêng |
| Chạy trên Windows hoặc agy | Chỉ nói đã thử khi đã thử thật trên đó; nếu chưa, ghi "chưa thử trên …" |

## Bảng kiểm khi có nhiều yêu cầu

Khi việc có từ 3 yêu cầu trở lên, báo bằng bảng, mỗi yêu cầu một dòng:

| Bước | Yêu cầu | Kết luận | Bằng chứng |
|---|---|---|---|
| … | … | đạt / không đạt / chưa rõ | lệnh và kết quả, file, link |

Yêu cầu chưa có bằng chứng thì ghi "chưa rõ", không bỏ dòng. Bước "không đạt" thì sửa lại riêng bước đó, tối đa 3 lần (luật 10), rồi chạy lại cả bảng.

## Dấu hiệu đang tự lừa

| Ý nghĩ | Thực tế |
|---|---|
| "Chắc là chạy" | Chạy đi. |
| "Lúc nãy chạy được rồi" | Sau đó đã sửa gì chưa? Chạy lại. |
| "Subagent báo xong" | Kiểm lại kết quả của subagent. |
| "Lỗi nhỏ, không ảnh hưởng" | Ghi rõ lỗi đó trong báo cáo. |
| "Không thử được trong container" | Nói thẳng là chưa thử và vì sao. Không viết như đã thử. |

Báo đúng sự thật, kể cả khi chưa xong. Đây không phải lỗi; viết "đã xong" khi chưa xong mới là lỗi.
