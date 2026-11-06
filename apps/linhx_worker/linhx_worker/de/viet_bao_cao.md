Bạn viết phần nhận định cho báo cáo "AI nói gì về thương hiệu". Không dùng trình duyệt, KHÔNG chạy lệnh shell, không tạo hay sửa file. Chỉ dùng dữ liệu dưới đây: thông tin thương hiệu, CHI_SO (máy đã tính, không tính lại), DA_GAN_NHAN (trích câu trả lời kèm nhãn).

## Dữ liệu
{dau_vao}

## Viết
- trich_sai: tối đa 5 ý có nhãn sai/bia/nham/cu, trích ngắn nguyên văn, kèm điều đúng theo su_that. Không có thì để mảng rỗng.
- buoc_roi: thương hiệu rơi ở bước nào trong 5 bước agent: Tìm / Nhận diện / Đối chiếu / Lọc theo tiêu chí / Đề xuất và giải thích. Mở đầu bằng đúng tên bước, rồi 1 câu lý do khớp với CHI_SO (Có mặt thấp → Tìm; Đúng thấp → Đối chiếu; Đề xuất thấp → Lọc theo tiêu chí hoặc Đề xuất và giải thích).
- lop_yeu: 1–2 lớp tín hiệu yếu nhất trong: Sự thật có cấu trúc / Nhất quán đa kênh / Xác nhận từ bên thứ ba / Người thật đứng tên / Hành vi và phản hồi, mỗi lớp kèm lý do ngắn.
- ke_hoach_30_ngay: 4 tuần, mỗi tuần 2–3 việc cụ thể, làm được ngay.
- ket_luan: 3 câu ngắn: AI có biết brand không, nói đúng không, có khuyên chọn không. Số liệu phải khớp CHI_SO.

## Nộp: CHỈ in ra MỘT khối JSON hợp lệ, không thêm chữ nào khác
{"trich_sai": [{"ai": "", "ma": "", "nhan": "", "trich": "", "dung_ra": ""}], "buoc_roi": "", "lop_yeu": [""], "ke_hoach_30_ngay": [{"tuan": 1, "viec": [""]}], "ket_luan": ""}

Văn phong thuần Việt, câu đủ ý, không giọng quảng cáo, không chêm tiếng Anh ngoài tên riêng.
