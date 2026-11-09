---
name: phat-trien-nhan-vat
description: "Phát triển nhân vật ảo sau khi duyệt casting: tủ đồ thời trang, trang điểm, chi tiết cơ thể, danh sách biểu cảm, tối đa chi tiết và có tham chiếu cụ thể, ra Character Bible và character sheet cuối cùng. Dùng khi Linh nói \"phát triển nhân vật\", \"tủ đồ nhân vật\", \"bảng biểu cảm\"."
---
# Phát triển nhân vật (sau casting) (v2, tối ưu 25/10/2026)

Thứ tự cả chuỗi (Linh chốt 24/10): casting-mat (đến lúc duyệt gương mặt 3 góc) → skill này (cơ thể, trang điểm, tủ đồ, biểu cảm) → character sheet LÀ KHÂU SAU CÙNG.
Đầu vào: gương mặt đã duyệt (bộ 3 góc + diem-nhan-dien.md), brief.json, persona.json của skill casting-mat.
Thư mục: `<casting>/<ma>/phat-trien/` gồm `huong/`, `spec/*.json`, `ref/`, `anh/r0..r2/`, `round-<n>.json`, `BIBLE.html`.

## Luật "không chung chung" (cốt lõi)
Mỗi món, mỗi lớp trang điểm, mỗi chi tiết cơ thể, mỗi biểu cảm phải có đủ:
1. **Số đo hoặc mã**: màu hex (và Pantone TCX nếu có), số đo cm/mm, vị trí theo toạ độ (vd nốt ruồi "1,5 cm dưới đuôi mắt trái"), mã cơ mặt FACS cho biểu cảm.
2. **Tham chiếu cụ thể có tên**: link ảnh, hoặc tên bộ sưu tập/mùa/nhà mốt ("The Row FW24 look 12"), tên phong cách có định nghĩa ("dark academia"), tên chất liệu ("linen Ireland 180 gsm"). Không chấp nhận "phong cách hiện đại".
3. **Lý do gắn brief/persona**: món này phục vụ cảm giác nào, persona nào.
Từ mơ hồ (thanh lịch, hiện đại, trẻ trung, sang trọng, cá tính, nhẹ nhàng, tinh tế...) chỉ được dùng khi câu đó có thêm số đo hoặc tham chiếu. Chạy `python scripts/kiem_cu_the.py spec/` trước khi vẽ: mục nào thiếu thì bổ sung, không vẽ khi còn lỗi.

## Tham chiếu và quyền
- Tham chiếu thời trang, trang điểm, chất liệu: lookbook, runway (Vogue Runway), street style, trang hãng, Pinterest. Lấy link + mô tả, đính ảnh vào máy vẽ được (cho trang phục/đồ vật). Ảnh có gương mặt người thật thì chỉ dùng phần trang phục, không lấy mặt.
- Không in logo, tên thương hiệu thật lên đồ nhân vật. Lấy cảm hứng, không sao chép nguyên thiết kế đặc trưng.
- Gương mặt luôn lấy từ bộ 3 góc đã duyệt; luật giữ mặt của casting áp dụng mọi ảnh.

## 9 giai đoạn, 3 cổng duyệt của Linh
Bản đầy đủ trên máy: D:\LINHX\LAB\LAB066-CASTING-GUONG-MAT\QUY-TRINH-PHAT-TRIEN-NHAN-VAT.md. Kiểm 4 chữ C: Cụ thể (tên chuyên môn), Con số (số đo, hex, Pantone), Chứng cứ (link tham chiếu, ghi lấy gì và không lấy gì), Chặn lệch (danh sách cấm).
A. **Cơ thể** `co-the.json`: số đo, tỷ lệ đầu, dáng Kibbe, da Fitzpatrick + hex 3 vùng, nốt ruồi/tàn nhang có toạ độ, tay và móng, thuận tay.
B. **Tóc và trang điểm**: tóc (dài cm, kết cấu 1A-2C, hex chân/thân/ngọn, ngôi); 3 look (ngày, live, sự kiện) theo vùng, kỹ thuật, độ đậm %, hex, finish. → **Cổng 1: Linh duyệt.**
C. **Định hướng phong cách**: 3 hướng, mỗi hướng moodboard 12-20 ảnh có nguồn, bảng màu 60/30/10 có Pantone, chất liệu chủ đạo, món ký hiệu, điều cấm; persona chấm theo thang khắt khe (giám khảo trừ -1 mỗi mục chung chung). → **Cổng 2: Linh chọn hướng.**
D. **Tủ đồ capsule** 20-30 món, mỗi món một spec (chất liệu đến momme/gsm, hex, form, cổ, khuy, đường may, tham chiếu, cấm, đi với món nào) + 8-12 bộ phối theo bối cảnh. Vẽ flat-lay từng món trước, rồi ảnh mặc.
E. **Biểu cảm** 20-24 cái chia 4 nhóm: mã FACS + cường độ A-E, góc đầu, câu thoại mẫu, trạng thái videoMatrix (idle, talk, listening...), 2-3 biểu cảm chữ ký, biểu cảm cấm.
F. **Tư thế và cử chỉ** 10-12.
G. **Chấm và sửa** tối đa 2 vòng (R3 hiếm khi hơn R2): persona + giám khảo spec so ảnh với từng trường; màu món đồ lệch hex ΔE > 10 là lỗi; lệch mặt -1.5 trần 6.
H. **Bộ kinh nhân vật** BIBLE.html + PNG + JSON máy đọc. → **Cổng 3: Linh duyệt.**
I. **Character sheet, khâu sau cùng** (Linh chốt): vẽ từ spec đã duyệt, ChatGPT, từng phần thành ảnh riêng: toàn thân 4 góc trong bộ ký hiệu, biểu cảm chính, bộ phối chính, cận trang điểm, cận dấu riêng đúng toạ độ. Claude ghép CHARACTER-SHEET.html có nhãn, hex, tỷ lệ, luật giữ mặt, dòng "nhân vật ảo, hư cấu".

Trước khi vẽ mỗi giai đoạn: `python scripts/kiem_cu_the.py spec/` đạt 100%.
Prompt vẽ 4 khối theo thứ tự: giữ mặt (đính bộ 3 góc) → spec dán nguyên chữ → cấm → khung chụp. Mỗi chat ChatGPT tối đa ~8 ảnh rồi mở chat mới để mặt không trôi.

## Tối ưu v2 (từ Luna 24/10)
- Prompt mỗi ảnh: câu đầu "Dùng công cụ TẠO ẢNH, không dùng code"; câu khoá mặt (dáng mặt, tóc hex) + đính bộ 3 góc + 1 ảnh cận tốt nhất; mỗi chat tối đa 8 ảnh; kiểm ảnh đính kèm đã hiện.
- Spec theo cái nhìn thấy được: biểu cảm ghi góc đầu, miệng hé mm, số răng thấy (mã FACS thôi thì ra cùng một nụ cười); chi tiết ẩn ghi "không thấy khuy nào"; bộ phối luôn có giày; chi tiết nhỏ ở mắt ghi "nhìn thấy rõ qua mắt kính"; góc 3/4 ghi "xoay 45°, mắt xa chỉ thấy một nửa, tai xa khuất".
- Biểu cảm có chuyển động (gật, lắc) vẽ cặp khung đầu-cuối từ đầu. Hai biểu cảm gần nhau phải khác ít nhất 2 thứ nhìn thấy được (tay, hướng mắt, miệng).
- Chỉ vẽ lại ảnh có lỗi giám khảo hoặc < 6.5. Kiểm màu ΔE2000 món chính, ghi nhiệt độ đèn (3200K làm màu ngả nâu).
- Pantone ghi "gần nhất", đối chiếu quạt màu thật trước khi đặt vải. Loại ảnh moodboard có biểu tượng tôn giáo.
- Sheet (I) tái dùng ảnh đã duyệt, chỉ vẽ mới phần thiếu (turnaround 4 góc).
- Khối lượng tham khảo Luna: cổng 1 ~20 ảnh, cổng 2 ~6, cổng 3 46 vẽ/32 chốt, sheet 15 mới. Ghi giờ + số ảnh mỗi khâu vào LOG.md.
