# Giải mã vì sao slide mẫu đẹp

Làm ngay sau khi lọc mẫu (chỉ mẫu ≥ 4/5), trước khi điền thẻ phong cách và trước khi tạo template bằng ChatGPT/Gemini. Mục đích: biến "đẹp" thành nguyên tắc đo được để thợ và model ảnh làm theo, thay vì bắt chước bề mặt.

## Với từng mẫu, ghi đủ 9 mục (số ước lượng là được, cấm khen chung)

1. **Bố cục**: lưới mấy cột; chủ thể nằm ô nào (1/3, trục giữa, tràn cạnh); mắt đi theo thứ tự nào.
2. **Khoảng trống**: ước lượng % diện tích trống; khoảng trống nằm đâu và làm nổi cái gì.
3. **Số khối**: đếm khối thị giác (chữ, ảnh, mảng màu).
4. **Chữ**: số cỡ chữ; tỉ lệ tiêu đề : thân (vd 3,5 : 1); serif/sans; độ đậm; chữ hoa giãn cho nhãn.
5. **Màu**: mã ước lượng; tỉ lệ diện tích (vd 60/30/10); màu nhấn đặt ở đâu.
6. **Ảnh**: tràn hay khung; góc chụp; ánh sáng; tỉ lệ ảnh/chữ.
7. **Chi tiết cao cấp**: những thứ nhỏ tạo cảm giác đắt (đường mảnh 1px, chữ nhỏ giãn rộng, căn đường cơ sở, chất giấy).
8. **Điều mẫu KHÔNG làm**: những thứ AI hay thêm mà mẫu bỏ (icon, vạch dưới tiêu đề, thẻ đổ bóng, nhiều màu, chữ dài).
9. **Một câu**: nếu chỉ học được một điều từ mẫu này thì đó là gì.

## Tổng hợp

- 8–12 nguyên tắc lặp lại ở ít nhất 2 mẫu; mỗi nguyên tắc ghi mẫu nào có và một con số kiểm được (vd "khoảng trống ≥ 50%", "tiêu đề ≥ 3 lần cỡ thân", "1 màu nhấn ≤ 10% diện tích").
- Nguyên tắc nào máy đo được thì đưa vào `cau-hinh.json` (toi_gian, so_co_chu_toi_da, ...). Nguyên tắc nào chỉ mắt thấy thì đưa vào thẻ phong cách cho người chấm.

## Đưa vào prompt tạo ảnh/template

Thêm đoạn "Học từ tham chiếu:" liệt kê phần Tổng hợp, đính kèm đúng các mẫu đã giải mã, nói rõ học gì từ mẫu nào (bố cục từ mẫu A, màu từ mẫu B), và giữ các luật cấm ở mục 8.

## Soi thêm theo Before & After (McWade)
Khi tổng hợp nguyên tắc và khi chấm, soi 4 luật của `thiet-ke/references/before-after.md`: A3 một điểm nhìn mỗi slide, A4 các cấp chữ khác hẳn nhau, A5 bảng số liệu bỏ kẻ ô thay bằng dải nền nhạt, A10 nhóm rõ nhờ khoảng cách. Mỗi vòng sửa xuất cặp trước–sau cùng khổ.
