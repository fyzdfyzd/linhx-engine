# Báo cáo dựa trên mã nguồn đọc trực tiếp và một thí nghiệm nhỏ | Phương pháp
> Báo cáo dựa trên mã nguồn đọc trực tiếp và một thí nghiệm nhỏ do LINHX LAB tự chạy.

Mã nguồn: năm dự án trên GitHub (autoresearch, AI Scientist v2, OpenEvolve, Agent Laboratory, Open Deep Research), đọc lần đầu ngày 28/10/2026 và đọc lại ngày 9/11/2026 để lấy trích nguyên văn [BC18]. Các tham số trong báo cáo là giá trị mặc định trong mã, không phải giá trị các nhóm dùng trong bài báo của họ.

Thí nghiệm: một agent chạy các bước ý tưởng, triển khai và phân tích trên bài toán khớp hàm một chiều có nhiễu, ngày 28/10/2026 [BC17]. Phép đo là sai số bình phương trung bình trên tập giữ riêng, agent không được sửa. Mỗi lần chạy có ngân sách 60 giây, chạy một seed [BC17].

Giới hạn: bài toán nhỏ và có lời giải trơn, nên không đại diện cho bài toán nghiên cứu thật. Mức chênh giữa hai kết quả tốt nhất có thể nằm trong nhiễu. Báo cáo không đo chi phí token của lượt thử.

Báo cáo nối tiếp bài viết "Vài dòng về AI trong nghiên cứu" của Linh và anh Dũng, phần nói về việc dùng agent khi người là nút thắt.
