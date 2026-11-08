---
name: giai-ma-hai
description: Mổ một content hài viral (clip, meme, câu trend, status) xem vì sao buồn cười và vì sao lan, gom nhiều mẫu thành khuôn tái dùng, xuất thủ pháp chữ cho LAB087 vét cạn, rồi sinh biến thể mới. Dùng khi Linh đưa link/clip hài và hỏi "vì sao viral", "học thủ pháp này", "làm lại kiểu này cho brand X".
---

# Giải mã content hài viral để tái tạo

Một mẫu vào, một file JSON ra. Nhiều JSON gom thành khuôn. Phần cần đầu óc (mổ mẫu, điền khuôn cho chủ đề mới) do LLM làm, nên giao Gemini qua agy khi có lô lớn. Phần kiểm, gom, xuất, đối chiếu do `scripts/giai_ma.py` làm, 0 token.

Hai câu hỏi tách riêng, không trộn:
- **Vì sao hài** → khung GTVH sáu trường (Attardo và Raskin 1991) cộng bốn trường phái (lệch kỳ vọng, vi phạm lành tính, ưu thế, giải toả).
- **Vì sao lan** → STEPPS (Berger 2013), mức kích thích cảm xúc (Berger và Milkman 2012), và quan trọng nhất: **có khuôn để người khác điền không** (Shifman 2014). Thứ đem đi tái tạo là khuôn, không phải bản gốc.

Luật chung:
- Nguồn gốc và số liệu phải có link và ngày. Không biết thì để `null`, ghi "chưa rõ". Không bịa view.
- Trend hài sống vài ngày: mỗi mẫu bắt buộc có `ngay`.
- Nhận định là của người mổ, ghi `do_chac` 1 đến 3.

## Các bước

**B0. Gom mẫu.** Mỗi mẫu: link, nền tảng, ngày, view/share/lưu/bình luận nếu thấy, transcript hoặc mô tả hình. Lô chuẩn 30 đến 50 mẫu cùng một khoảng thời gian, kèm 10 mẫu đối chứng cùng kênh mà KHÔNG viral (không có đối chứng thì chỉ biết cái gì phổ biến, không biết cái gì làm nên viral).

**B1. Mổ từng mẫu** theo `references/schema.md`, ra `mau/<id>.json`. Đề mổ ở cuối schema, dán nguyên cho Gemini được.

**B2. Kiểm.** `python scripts/giai_ma.py kiem <thu-muc-mau>`. Sai enum hoặc thiếu trường thì sửa trước khi gom.

**B3. Gom khuôn.** `python scripts/giai_ma.py gom <thu-muc-mau>` ra `KHUON.md`: nhóm theo (loại đối lập kịch bản, cơ chế logic), đếm mẫu, điểm lan trung bình nếu có số, liệt kê câu khuôn có ô trống.

**B4. Xuất thủ pháp chữ cho LAB087.** `python scripts/giai_ma.py xuat087 <thu-muc-mau>` ra `THU-PHAP-CHO-087.md`: mỗi thủ pháp ở trường Ngôn ngữ (LA) thành "mô tả + 3 đến 5 ví dụ gốc→kết quả", gắn nhãn `da-co-luat` (nói lái, gieo vần đã chạy ở LAB087), `can-luat-moi`, hoặc `can-llm`. Thủ pháp `da-co-luat` thì chạy `doi-chieu` để xem luật LAB087 có tái tạo được ví dụ không.

**B5. Tái tạo.** Chọn khuôn + chủ đề mới (brand, sự kiện). Phần chữ: gọi LAB087 vét cạn (ví dụ `lai.py an "<từ khoá brand>"`, `van.py ghep "<từ Anh>"`). Phần tình huống, đối tượng, cách kể: LLM điền khuôn, mỗi khuôn 10 biến thể. Giữ nguyên SO và LM của mẫu gốc, chỉ đổi SI, TA, LA.

**B6. Chấm trước khi đăng.** Persona ảo LAB048 (bản v2, tiểu sử trước rồi hỏi xác suất) chấm theo `references/phieu-cham.json`: hiểu được không, buồn cười, có thấy bị xúc phạm (kiểm "lành tính"), sẽ gửi cho ai. Đây là lọc thô, không thay đăng thật. Mọi tên và câu chốt chạy `lai.py kiem` để soát lái ra tục.

**B7. Đăng thử và ghi số về B0.** Biến thể đăng thật thành mẫu mới có số, vòng sau gom lại. Sau 2 đến 3 vòng mới biết khuôn nào thật sự thắng.

## Giới hạn đã biết
- LLM mổ hài hay "giải thích quá tay": đối chiếu bằng mẫu đối chứng, không tin một lần mổ.
- Phần hình, nhịp, biểu cảm diễn viên không nằm hết trong GTVH; ghi vào `ghi_chu_hinh`.
