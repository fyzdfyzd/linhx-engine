# Người nên viết luật buổi tối và duyệt bản tóm buổi sáng | Vai người
> Người đặt luật, giữ phép đo và quyết định ở hai cổng; agent lo phần lặp ở giữa.

## Người nên giao phần lặp cho agent và giữ phần đặt đề bài

::: hinh H04

Bước đáng tiền nhất của người là bước đầu tiên. Ở đó người viết đề bài, phép đo khoá, phạm vi được sửa và ngân sách. Một đề bài viết tốt cho phép agent chạy cả đêm mà không cần hỏi [BC03].

::: sidebar Trước khi để agent chạy qua đêm | Rủi ro và chi phí
Chi phí: một lượt vòng tự tối ưu trước đó của LINHX tốn khoảng 0,9 đến 1,1 triệu token, nên cần trần token cứng [BC19].
Mất dữ liệu: chính lượt thử đã có lần quay lui xoá bản tốt nhất; chạy trong thư mục riêng có sao lưu [BC15].
Quyền: không đưa khoá API thật, không cho agent quyền mạng hay quyền ghi ngoài thư mục thí nghiệm.
Dừng khẩn: có một lệnh dừng mà người khác trong nhóm cũng biết.
:::

## Năm việc nên làm trước khi để agent chạy qua đêm

::: khuyen-nghi
Viết đề bài một trang trước khi chạy | Ghi mục tiêu, phép đo, tệp được sửa, ngân sách thời gian và token.
Khoá phép đo khỏi tay agent | Để tệp đánh giá chỉ đọc, như autoresearch [BC04].
Đặt trần cho mọi vòng | Trần sửa lỗi, trần lượt đọc, trần thí nghiệm mỗi đêm.
Chạy nhiều seed trước khi tin | Một lần tốt hơn vài phần trăm chưa phải phát hiện [BC14].
Chọn hai cổng người | Một cổng duyệt đề bài buổi tối, một cổng đọc bản tóm buổi sáng [BC10].
:::
