# Vòng 1 WF18 · Hồ sơ số 0: chấm Linh trên AI

Đề: Linh chốt 9/11 12:15. Theo `DE-THREAD.md`, `NGHIEN-CUU.md`, `BO-SUNG-V2-CLOUD.md`. Mỗi phiếu ≤ 40 phút.

| # | Việc | Ai | Máy | Ra file |
|---|---|---|---|---|
| 1 | Điền `person.json` từ tên gọi + link Linh đưa; đọc từng link, mỗi dữ kiện có nguồn | Claude | cloud | `person.json` |
| 2 | **D2**: Linh duyệt `person.json` (đúng/sai, bỏ gì, điều nhạy cảm) | Linh | điện thoại | ghi trong thread |
| 3 | Sinh câu: `bo-cau-hoi-nguoi.json` gói C (25) + câu gài trùng tên | Claude | cloud | `cau-hoi.json` |
| 4 | Dán tay giao diện: 10 câu then chốt (P01 P02 P03 P07 P08 P09 P11 P14 P16 P21) × ChatGPT, Gemini, Claude, Perplexity × 2 lượt, cửa sổ ẩn danh mới mỗi câu, ghi ngày giờ + chế độ (có/không tra web) | agy (Chrome) hoặc Claude in Chrome | **máy công ty DESKTOP-PVHR2CD** | `tra-loi/dan-tay-*` |
| 5 | Hỏi API khối lớn: 25 câu × 5 lượt × 3 họ (claude-tim, gemini-tim, openrouter:openai/…:online) | agy | máy công ty | `tra-loi/` |
| 6 | Chấm: giám khảo Claude + giám khảo Gemini, không thấy tên mô hình; lệch Sai/Bịa/Nhầm > 10% đưa Claude kiểm | Claude + agy | cloud + máy cty | `cham/` |
| 7 | Báo cáo + việc sửa 30 ngày (tra web đo lại ngày 30, trí nhớ ngày 90) | agy dựng, Claude chấm | máy cty | `bao-cao.html` |
| 8 | Chạy lại bước 5 sau 1 ngày, đo lệch có mặt gộp (ngưỡng ≤ 10) | agy | máy cty | `on-dinh.json` |
| 9 | **D4**: Linh duyệt báo cáo | Linh | | |
| 10 | Ghi `BAI-HOC.md`, sửa skill | Claude | cloud | |

## Máy đo vòng 1 (ngưỡng từ BO-SUNG-V2-CLOUD)
1. Mọi khẳng định Sai/Bịa/Nhầm có nguyên văn, ngày, mô hình, đường lấy (API/giao diện).
2. Lệch có mặt gộp giữa hai lần chạy ≤ 10 điểm (25 × 5 × 3).
3. Lỗi nặng 1 lần là vào báo cáo; lỗi thường lặp ≥ 2/5.
4. Hai giám khảo lệch nhãn Sai/Bịa/Nhầm ≤ 10%.
5. Mỗi việc sửa có người làm, chế độ sẽ đổi, mốc đo lại, làm được trong 30 ngày.

## Lỗi quy trình đã thấy (chép sang BAI-HOC khi đủ bằng chứng)
- L1 `brandcheck.py cau-hoi` không nhận bộ câu riêng (hàm `build_questions` có tham số `bank` nhưng CLI không truyền) → bộ câu người phải gộp qua `abc.cau_hoi_them` hoặc thêm cờ `--bo-cau`. Chỗ: `skills/bo/linhx-brand-check/scripts/abc_lib.py:115`, `brandcheck.py:158`.
- L2 Bộ câu ABC toàn câu doanh nghiệp (giá, đổi trả, gian hàng) → chạy cho người sẽ ra câu vô nghĩa nếu dùng bộ mặc định.
