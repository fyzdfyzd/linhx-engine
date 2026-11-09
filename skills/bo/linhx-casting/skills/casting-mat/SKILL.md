---
name: casting-mat
description: "Casting gương mặt nhân vật ảo: persona khán giả chấm, vẽ ChatGPT+Gemini có ảnh tham chiếu, 3 round chấm khắt khe 3 góc, Linh duyệt, character sheet. Khi Linh nói casting mặt."
---
# Casting gương mặt nhân vật (v2, tối ưu 25/10/2026)

Nguồn: LAB066, chạy thật cho Luna Mai 24/10/2026. Trên máy: `D:\LINHX\LAB\LAB066-CASTING-GUONG-MAT` (QUY-TRINH.md, QUY-TRINH-TOI-UU.md, BAI-HOC.md, scripts\). Cloud: /mnt/project-files/LAB066-CASTING-GUONG-MAT.

Chuỗi: casting-mat dừng ở gương mặt 3 góc đã duyệt (cổng C0) → `phat-trien-nhan-vat` → character sheet là khâu sau cùng. Linh không trả lời sau 10 phút thì đi theo khuyến nghị.

Thư mục việc: `<LAB hoặc dự án>/casting/<ma-nhan-vat>/`: brief.json, persona.json, ung-vien.json, ref/, anh/r0..r2/, round-<n>.json, cai-thien-r<n>.md, VONG-LAP.html, diem-nhan-dien.md, LOG.md (giờ + số ảnh mỗi khâu).

## Luật cứng
- Ảnh tham chiếu ĐƯỢC đưa vào máy vẽ. Nguồn Unsplash/Pexels/stock có model release hoặc mặt AI; không người nổi tiếng, KOL, người quen. Mỗi nhân vật trộn 2-3 ảnh của NGƯỜI KHÁC NHAU, mỗi ảnh một vai (1 mặt và ánh mắt, 2 tóc và da, 3 khí chất/ánh sáng). Prompt: "tạo gương mặt MỚI pha trộn, không sao chép người trong ảnh", không ghi tên người mẫu. Ghi nguồn vào ref/nguon.json.
- Tra Google Lens trước khi duyệt (dồn cuối); khớp người thật cụ thể thì vẽ lại.
- Ảnh không chữ; nhãn, bảng màu do Claude ghép (HTML).
- Persona chấm là Claude nhập vai: để lọc, không thay khảo sát thật.
- Gương mặt hiện tại của nhân vật (nếu có) luôn làm mốc so sánh.

## 7 bước
1. Brief: nhân vật làm gì, kênh, khán giả, 3 cảm giác cần gợi, điều cấm (không hở hang, không idol hoá, không biểu tượng tôn giáo).
2. 3-5 persona khán giả: tiểu sử trước + trọng số theo tỷ lệ khán giả (khuôn LAB048).
3. 8 kiểu gương mặt chia nhóm khí chất (mô tả + nhóm).
3b. **TÌM VÀ BẦU ẢNH THAM CHIẾU (không được bỏ qua, quyết định chất lượng).** Mỗi kiểu mặt tìm 4-6 ảnh thật trên trang người mẫu/stock có phép (Unsplash, Pexels, agency), mỗi ảnh gắn vai (mặt và ánh mắt / tóc và da / khí chất). Dựng trang REF-BAU.html cho persona xem ảnh thật. Persona chấm TỪNG ẢNH theo thang khắt khe + 1 điều không thích; chấm luôn kiểu mặt dựa trên bộ ảnh tốt nhất. Kết quả: top 5 kiểu mặt (cham.py, tối đa 2/nhóm, cờ chia rẽ) và với mỗi kiểu, 1 ảnh thắng cho mỗi vai (3 ảnh của 3 người khác nhau). Ghi ref/bau.json + nguon.json. Linh có thể xem trang này và đổi ảnh trước khi vẽ.
4. Lượt rộng: vẽ top 5 ảnh nhìn thẳng, đính đúng 3 ảnh tham chiếu đã thắng bầu của kiểu đó. Gemini (nhanh) và ChatGPT song song nếu muốn so; chấm khắt khe (R0) → giữ top 3.
5. Vòng lặp tối đa 2 round chỉ bằng ChatGPT, mỗi round 3 góc: thẳng trước, rồi đính nó làm chuẩn vẽ 3/4 ("xoay 45°, mắt xa chỉ thấy một nửa, tai xa khuất") và nghiêng hẳn. Viết 3 cải thiện cụ thể/ảnh (nêu nét cần đổi: mắt, mũi, cằm, nốt ruồi; không chỉ ghi "giữ nguyên gương mặt"). Chỉ vẽ lại ảnh có lỗi hoặc < 6.5. Bản mới kém hơn thì giữ bản tốt nhất. Thêm R3 chỉ khi còn lỗi giám khảo.
6. Trang VONG-LAP.html: mỗi ảnh một hàng R0|R1|R2 với 3 góc, bảng điểm, cột chênh, lỗi hết/còn, cờ Lens, mốc gương mặt hiện tại.
7. Cổng C0: Linh chọn (thẻ 2-4 phương án, có phương án ghép). Ghi diem-nhan-dien.md, chuyển sang `phat-trien-nhan-vat`.

## Thang chấm khắt khe
Persona chấm 4 tiêu chí 1-10 (hợp gu, đáng tin, nhớ được, đúng vai), lấy trung bình. Mốc: 5 = lướt qua, là điểm xuất phát; 7 = xem hết; 8 = theo dõi kênh; 9 = chia sẻ, mỗi persona tối đa một điểm 9 mỗi round; không cho 10. Mỗi điểm kèm 1 điều không thích.
Giám khảo lỗi riêng, ghi `_loi` [mô tả, trừ, trần]: biểu tượng tôn giáo/chính trị, hở hang -2 trần 4; Lens khớp người thật -3 trần 3; bám mặt ảnh tham chiếu quá sát -1.5 trần 6; mặt không nhất quán giữa 3 góc -1.5 trần 6; sai mô tả cốt lõi -1; mỗi lỗi kỹ thuật (tóc phát sáng, răng, tay, mắt lệch, da nhựa) -0.5; góc xoay sai -0.5; nền/khung sai -0.5; idol hoá, bóng da AI -0.5. Điểm = trung bình có trọng số + tổng trừ, áp trần nhỏ nhất, tối thiểu 1.

## Vẽ (mọi prompt)
Câu đầu: "Dùng công cụ TẠO ẢNH, không dùng code." Kiểm ảnh đính kèm đã hiện trong tin trước khi chờ. Mỗi chat tối đa 8 ảnh rồi mở chat mới. Đi chậm khoảng 30 giây/ảnh, một tab Google một lúc; không giải CAPTCHA thay người. Chrome chỉ tải tự động 1 ảnh mỗi tab Gemini (Linh bấm "Cho phép tải nhiều tệp" hoặc chụp phần tử ảnh). Mở trang kết quả qua server python cục bộ (extension không mở file://).

## Bài học Luna
ChatGPT: đúng ~85% yêu cầu sửa, xoay góc chuẩn, 1,5-3 phút/ảnh; có lúc idol hoá, khoét cổ sâu. Gemini: nhanh, ảnh to, đúng mô tả lượt đầu nhưng bám mặt tham chiếu sát, bỏ qua sửa, 3/4 ít xoay. Máy vẽ tự thêm ngôi sao sáu cánh, tóc phát sáng, đạo cụ nền. Lens hay bám trang sức/kính hơn mặt. Thang khắt khe đưa điểm về 4-5.5, vòng lặp tăng 1-2 điểm.
