# Năm hệ thống mã mở đều đặt trần cho vòng lặp | Khuôn chung
> Đọc trực tiếp mã nguồn cho thấy mọi hệ thống đều giới hạn số vòng; hệ thống chặt nhất còn khoá luôn cách chấm điểm.

## Phép đo khoá là điều kiện đầu tiên để giao vòng cho agent

::: hinh H03

autoresearch để tệp chứa phép đánh giá ở chế độ chỉ đọc và cấm agent sửa nó [BC04]. Nếu agent được sửa cách chấm điểm, nó sẽ tối ưu cách chấm chứ không tối ưu bài toán. Mọi lần chạy cũng dùng chung ngân sách 5 phút để so sánh được với nhau [BC01].

AI Scientist v2 cho mỗi ý tối đa 3 tầng sửa lỗi và bắt đầu từ 3 bản nháp [BC06]. Open Deep Research mặc định 5 nhóm đọc chạy song song và tối đa 6 lượt [BC11].

## Khác biệt nằm ở cách giữ nhiều hướng còn sống

::: sidebar Bốn cách giữ nhiều hướng và giữ người | Đọc thêm
AI Scientist v2 chia việc thành 4 giai đoạn: chạy được, tinh chỉnh baseline, sáng tạo, ablation [BC07].
OpenEvolve chia quần thể thành 5 đảo và cho di cư mỗi 50 thế hệ [BC08].
OpenEvolve còn cố định tỷ lệ chọn: 70% khai thác, 20% khám phá, 10% tinh hoa [BC09].
Agent Laboratory có cờ bật, tắt cổng duyệt của người cho từng pha [BC10].
:::
