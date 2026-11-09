# Lượt thử nhỏ cho thấy vòng lặp chạy hết mà không cần người | Thử thật
> LINHX LAB cho một agent tự lo các bước ý tưởng, chạy thử và phân tích trên một bài toán nhỏ, với phép đo khoá và kho ý tưởng do người nạp.

## Sai số giảm từ 0,52843 xuống 0,00146 sau 14 dòng nhật ký

Bài toán là khớp một hàm một chiều từ dữ liệu có nhiễu, đo bằng sai số bình phương trung bình trên tập giữ riêng. Agent bắt đầu từ baseline 0,52843 và kết thúc ở 0,00146 sau 14 dòng nhật ký [BC12]. Trong đó 6 dòng được giữ, 7 dòng bị bỏ và 1 dòng lỗi [BC12].

::: hinh H01

Phép đo đã loại các ý không tốt hơn, kể cả khi trông hợp lý: đa thức bậc 7 cho 0,00181, kém bậc 5 ở mức 0,00153, nên bị bỏ [BC13]. Trong 6 dòng được giữ, chỉ 3 dòng là cải thiện thật; 2 dòng là dọn dẹp cùng code [BC20].

## Lượt đọc thêm theo luật cho một ý mới ngang với ý tốt nhất

Đa thức bậc 5 kẹt 5 vòng liền không cải thiện [BC14]. Theo luật người đặt sẵn, agent dừng thử, quay lại đọc tài liệu một lượt và thêm 3 ý vào kho [BC14]. Ý cho điểm thấp nhất là ý agent đề xuất: cơ sở Fourier, chọn số tần bằng kiểm định chéo [BC14].

Kết quả này cần đọc thận trọng. Mức hơn bậc 5 có thể chỉ là nhiễu, vì thí nghiệm chưa chạy nhiều seed [BC14]. Bài toán cũng nhỏ hơn rất nhiều so với một bài toán nghiên cứu thật.

::: hinh H02

::: sidebar Bốn lỗi chỉ lộ ra khi chạy thật | Bài học quy trình
Lượt thử tìm ra 4 lỗi trong chính quy trình và đã sửa [BC15].
Quay lui về bản trước đã xoá mất bản tốt nhất khi một lần sửa không ăn.
Nhật ký ghi kết quả cũ dưới tên ý mới.
Sau khi nạp ý mới, agent vẫn báo kẹt mãi.
Bộ hướng dẫn nằm trong thư mục thí nghiệm nên bị quay lui theo.
:::

Cùng nhóm cũng thử bước viết bài sau vòng lặp. Một bản thảo được cài bốn bẫy, gồm số bịa và trích dẫn bịa, và máy kiểm bắt đủ cả bốn [BC16]. Máy kiểm là một đoạn chương trình so số và trích dẫn với nguồn, không gọi AI nên không tốn phí.
