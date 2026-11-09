# Khung chung: thế nào là một workflow chuẩn

Áp cho mọi WF trong thư mục này. Luật chất lượng nền: skill `linhx-chuan` (14 luật) và vòng lặp LAB099.

## Một WF chuẩn gồm
1. **Một skill** trong `linhx-engine/skills/` (có rồi thì sửa, không tạo bản thứ hai).
2. **Khuôn đề bài**: điền là chạy được, không cần hỏi lại.
3. **Bản vàng**: ít nhất 1 mẫu top tier Linh đã duyệt, để chấm ngang.
4. **Máy đo** xếp rẻ tới đắt: kiểm tự động → rubric → chấm mù (người chấm tách thợ, không đọc lý do của thợ) → Linh.
5. **Hai cổng Linh**: D2 chọn hướng (che tên nhánh), D4 duyệt cuối. Ngoài hai cổng, máy tự quyết.
6. **Trần vòng**: ≤ 3 vòng sửa mỗi lượt, ≤ 3 lỗi mỗi lần sửa, tệ hơn thì hoàn tác.
7. **Nhật ký**: phút, token, số lần Linh phải chạm, ghi mỗi vòng.

## Bước 0: ai bên ngoài đã làm (bắt buộc, Linh 9/11)
Trước vòng 1: tìm trên GitHub, các trang skill (skills.sh, claudemarketplaces, openskillindex…), blog và mạng xã hội xem có ai nói về workflow hay skill này. Đọc code/quy trình của ít nhất 3 cái tốt nhất, ghi `NGOAI.md`: lấy gì, bỏ gì, so với skill LINHX đang có. Không tự nghĩ lại thứ người khác đã làm tốt.

## Ba vòng làm chuẩn (mỗi vòng một đề thật khác nhau)
- **Vòng 1**: Claude điều phối, agy làm thợ. Mục đích là tìm lỗi quy trình. Ghi mọi lỗi, sửa skill.
- **Vòng 2**: agy làm theo skill đã sửa, Claude chỉ chấm.
- **Vòng 3**: agy tự chạy cả kế hoạch (`agy-tu-chay`), Claude canh 20 phút/lần.

## Đạt chuẩn, được nạp vào LINHX ENGINE khi
- Vòng 2 và 3 qua D4 mà Linh không phải sửa lớn.
- Máy đo của WF đạt ngưỡng ở cả hai vòng.
- Số lần Linh chạm ở vòng 3 ≤ 2 (D2 + D4).

Nạp = skill chốt trong repo + loại phiếu trong `linhx_worker` + trang wiki + dòng trong bảng hệ thống.

## Vai
| Vai | Làm gì |
|---|---|
| Linh | Ý gốc khi cần, D2, D4 |
| Claude cloud | Ra đề, tìm bản vàng, chấm, sửa skill |
| Claude máy cty | Chấm mắt mới (không thấy lịch sử thợ) |
| agy | Thợ: dựng, viết, ghép |
| Gemini (Ultra, máy cty) | Deep Research, phản biện, ảnh, Flow/Veo |
| ChatGPT Plus (máy cty) | Ảnh |
| Vân Anh | Biên tập bài viết |

Việc trình duyệt (ChatGPT, Gemini, Dribbble…) luôn chạy Chrome **máy công ty**, không dùng MSI.
