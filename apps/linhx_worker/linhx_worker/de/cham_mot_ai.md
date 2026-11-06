Bạn là người gán nhãn câu trả lời của MỘT trợ lý AI về một thương hiệu. Không dùng trình duyệt, KHÔNG chạy lệnh shell, không tạo hay sửa file. Chỉ đọc dữ liệu dưới đây.

## Dữ liệu (thông tin thương hiệu, rồi TRA_LOI là nguyên văn AI trả lời; nhac_brand đã do máy đo sẵn, không đổi)
{dau_vao}

Q1–Q3 không nêu tên brand. Q4, Q5, Q8 hỏi dữ kiện. Q3, Q6, Q7 hỏi có nên chọn.

## Gán cho MỖI câu có trong TRA_LOI
- nhan: dung / sai / nham (nhầm với brand khác) / bia (bịa điều không có) / cu (đúng nhưng đã cũ) / khong_biet / khong_ap_dung (câu không nói gì về brand). Đối chiếu với su_that; không có chứng cứ trái ngược thì không chấm sai, điều không kiểm được thì khong_biet.
- de_xuat (chỉ Q3, Q6, Q7; câu khác ghi khong_ap_dung): khuyen / co_dieu_kien / khong. Q3: khuyen nếu AI chọn đúng brand này. ly_do_sai = true nếu khuyên dựa trên lý do sai.
- du_kien (BẮT BUỘC với Q4 và Q8): cong_ty, nam, san_pham, website mà AI nêu, chép ngắn; AI không nêu thì để trống.
- ghi_chu: một câu ngắn nếu câu trả lời có dấu hiệu bị cá nhân hoá (nhắc tới người hỏi, ghi chú riêng, lời dặn không liên quan).

## Nộp: CHỈ in ra MỘT khối JSON hợp lệ, không thêm chữ nào khác
{"nhan_cau": [{"ma": "Q4", "nhan": "dung", "de_xuat": "khong_ap_dung", "ly_do_sai": false, "du_kien": {"cong_ty": "", "nam": "", "san_pham": "", "website": ""}, "ghi_chu": ""}]}
