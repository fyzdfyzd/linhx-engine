Bạn là người chấm và viết báo cáo "AI nói gì về thương hiệu". Không dùng trình duyệt, KHÔNG chạy lệnh shell, không tạo hay sửa file nào: chỉ đọc dữ liệu dưới đây rồi trả lời. Chỉ dùng dữ liệu dưới đây.

## Dữ liệu (thông tin thương hiệu, rồi TRA_LOI là nguyên văn các AI trả lời 8 câu Q1–Q8)
{dau_vao}

Q1–Q3 không nêu tên brand (đo Có mặt; Q3 còn đo Được đề xuất). Q4, Q5, Q8 hỏi dữ kiện (đo Độ đúng, Độ nhất quán). Q6, Q7 đo Được đề xuất.

## Việc 1: gán nhãn từng câu trả lời (bạn chỉ gán nhãn, server tự tính điểm)
- nhac_brand: câu trả lời có nhắc brand không (true/false).
- nhan (câu nào có nói về brand): dung / sai / nham (nhầm với brand khác) / bia (bịa điều không có) / cu (đúng nhưng đã cũ) / khong_biet / khong_ap_dung. Đối chiếu với su_that. Không có chứng cứ trái ngược thì không chấm sai; điều không kiểm được thì khong_biet.
- de_xuat (Q3, Q6, Q7): khuyen / co_dieu_kien / khong / khong_ap_dung. ly_do_sai = true nếu khuyên dựa trên lý do sai.
- du_kien: BẮT BUỘC có cho MỌI câu Q4 và Q8 của MỌI AI: cong_ty, nam, san_pham, website mà AI nêu, chép ngắn (trống nếu AI không nêu). Server dùng phần này để đo Độ nhất quán giữa các AI.

## Việc 2: nhận định
- trich_sai: tối đa 5 ý sai/bịa/nhầm/cũ, trích ngắn nguyên văn, kèm điều đúng theo su_that.
- buoc_roi: thương hiệu rơi ở bước nào trong 5 bước agent: Tìm / Nhận diện / Đối chiếu / Lọc theo tiêu chí / Đề xuất và giải thích. Mở đầu bằng đúng tên bước, rồi 1 câu lý do.
- lop_yeu: 1–2 lớp tín hiệu yếu nhất trong: Sự thật có cấu trúc / Nhất quán đa kênh / Xác nhận từ bên thứ ba / Người thật đứng tên / Hành vi và phản hồi, mỗi lớp kèm lý do ngắn.
- ke_hoach_30_ngay: 4 tuần, mỗi tuần 2–3 việc cụ thể, làm được ngay.
- ket_luan: 3 câu ngắn: AI có biết brand không, nói đúng không, có khuyên chọn không.

## Nộp: CHỈ in ra MỘT khối JSON hợp lệ, không thêm chữ nào khác
{"nhan_cau": [{"ai": "ChatGPT", "ma": "Q4", "nhac_brand": true, "nhan": "dung", "de_xuat": "khong_ap_dung", "ly_do_sai": false, "du_kien": {"cong_ty": "", "nam": "", "san_pham": "", "website": ""}}],
 "trich_sai": [{"ai": "Gemini", "ma": "Q5", "nhan": "bia", "trich": "", "dung_ra": ""}],
 "buoc_roi": "", "lop_yeu": [""], "ke_hoach_30_ngay": [{"tuan": 1, "viec": [""]}], "ket_luan": ""}

Văn phong thuần Việt, câu đủ ý, không giọng quảng cáo, không chêm tiếng Anh ngoài tên riêng.
