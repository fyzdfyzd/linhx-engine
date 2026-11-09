# Những điểm chính
> AI agent đã chạy được vòng thí nghiệm mà không cần người nối từng bước, với điều kiện người đặt luật trước và giữ phép đo khỏi tay agent.

::: so-lon Nguồn: autoresearch (Karpathy), program.md; LINHX LAB, thí nghiệm 28/10/2026
12 | thí nghiệm mỗi giờ nếu mỗi lần chạy mất 5 phút, theo ước tính của tác giả autoresearch, LINHX chưa kiểm
3 | lần cải thiện thật trong 14 dòng nhật ký agent tự ghi ở lượt thử của LINHX
:::

1. **Người nghiên cứu là nút thắt chứ không phải AI.** Với ngân sách 5 phút mỗi lần chạy, một agent làm được khoảng 12 thí nghiệm mỗi giờ [BC02]; người nối từng bước không theo kịp nhịp đó.
2. **Mọi hệ thống mở được đọc đều đặt trần vòng.** autoresearch còn cấm agent sửa tệp chứa phép đánh giá [BC04]; AI Scientist v2 cho mỗi ý tối đa 3 tầng sửa lỗi [BC06].
3. **Lượt thử nhỏ cho thấy vòng lặp chạy hết mà không cần người.** Sai số giảm từ 0,52843 xuống 0,00146 sau 14 dòng nhật ký, phần lớn nhờ ý đa thức do người nạp [BC12].
4. **Một lượt thử chưa đủ để tin.** Ý agent đề xuất sau khi đọc thêm chỉ ngang ý tốt nhất, và lượt thử chạy một seed [BC14].
5. **Chạy thật làm lộ lỗi quy trình.** Lượt thử tìm ra 4 lỗi, có lỗi xoá mất bản tốt nhất [BC15].
