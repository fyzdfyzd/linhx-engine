# Người nghiên cứu đang là nút thắt của vòng có AI | Nút thắt
> AI đã viết code, tóm tài liệu và gợi ý. Thứ còn chậm là khoảng chờ giữa các bước, khi mọi việc phải qua tay người.

Vòng nghiên cứu quen thuộc có năm bước: hiểu vấn đề, đọc tài liệu, đề xuất ý tưởng, triển khai thí nghiệm và phân tích kết quả. Cách làm hybrid hiện nay để AI hỗ trợ ở từng bước, còn người giữ vai nối các bước với nhau. Người đặt câu hỏi, giao việc, đọc kết quả rồi quyết định bước tiếp.

Cách này nhanh hơn làm một mình, nhưng tốc độ của cả vòng vẫn bằng tốc độ của người. Khi người ngủ, đi họp hay bận việc khác, vòng dừng lại. Bài viết "Vài dòng về AI trong nghiên cứu" của Linh và anh Dũng gọi đúng chỗ này: nút thắt là chính người nghiên cứu.

## Agent không phải chờ thì một đêm đủ cho khoảng 100 thí nghiệm

Dự án autoresearch của Andrej Karpathy cho thấy quy mô của khoảng chờ đó. Mỗi thí nghiệm được chạy trong ngân sách cố định 5 phút [BC01]. Với nhịp ấy, tác giả ước tính agent chạy khoảng 12 thí nghiệm mỗi giờ, tức khoảng 100 thí nghiệm trong một đêm ngủ [BC02].

::: so-lon Nguồn: autoresearch (Karpathy), program.md, đọc 9/11/2026
12 | thí nghiệm mỗi giờ khi mỗi lần chạy mất 5 phút
100 | thí nghiệm trong một đêm ngủ trung bình của người
:::

Điều kiện để đạt nhịp này là agent không dừng lại hỏi. Theo hướng dẫn của autoresearch, một khi vòng lặp đã bắt đầu, agent không được dừng để hỏi người có nên tiếp tục hay không [BC03]. Việc của người chuyển sang hai đầu: viết luật trước khi vòng chạy và đọc kết quả sau khi vòng dừng.

::: trich | Andrej Karpathy, autoresearch
NEVER STOP: Once the experiment loop has begun (after the initial setup), do NOT pause to ask the human if you should continue. [BC03]
:::
