# Bài Puracam (chia sẻ trên Facebook, Linh gửi 20/11/2026)

Tóm ý chính, không chép nguyên văn. Tác giả làm ở công ty outsourcing, dùng AI build Puracam (quét 3D phòng bằng LiDAR iPhone), gần như không tự gõ code: AI viết, người ra đề, đặt tiêu chí, kiểm.

1. AI tiến nhanh: mỗi model mới giải tiếp chỗ model cũ kẹt. Muốn thấy thì thử bài thật khó, không xem demo.
2. Vibe code không ra sản phẩm: bài khó (pose drift, TSDF, QEM, UV/texture, registration, giới hạn máy). Phải hiểu bài đủ sâu để biết hỏi gì và biết khi nào AI sai.
3. Đừng tin AI nói "xong": hơn 4.000 test, A/B trên bản quét thật, agent kiểm chéo, cuối cùng mắt người cầm máy thật.
4. Ra sớm, gắn analytics từ đầu; dữ liệu cho thấy cái tưởng quan trọng không ai dùng, chỗ không để ý lại cần sửa nhất.
5. $1 đầu tiên trả lời "có giá trị thật không".
Kỹ năng cần: chia nhỏ và viết tiêu chí kiểm được, hiểu domain, dựng test và đo, đọc dữ liệu người dùng.
