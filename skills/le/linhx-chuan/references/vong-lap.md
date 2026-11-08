# Vòng tự cải thiện (luật 7)

Rút từ LAB099 (vòng lặp slide, `vls.py`) và LAB105 (cổng 2 tầng ở 4 pha). Khung chung cho mọi loại sản phẩm: **sinh → đo → sửa → dừng**.

## 1. Hai tầng đo

1. **Máy đo rẻ chạy trước**: `kiem.py`, lệnh kiểm riêng của từng loại (vls.py cho slide, Playwright cho web, OCR cho video). Trượt máy thì không gọi người chấm.
2. **Ba người chấm** ở ba ngữ cảnh khác thợ (ví dụ agy phiên mới, Gemini model khác đóng vai khách khó tính, Claude máy công ty). Người chấm mở tham chiếu trước khi đọc bài. Mỗi người ghi phiếu JSON theo `../cham.md`.

Đạt khi trung vị mọi tiêu chí ≥4 và 2/3 phiếu đạt.

## 2. Sáu luật chống sửa quá tay

1. Chỉ sửa lỗi **chặn** hoặc **nặng**. Lỗi nhẹ để lại.
2. Mỗi lượt sửa **tối đa 3 lỗi**, ghi trong `phieu-sua.md`. Thợ chỉ sửa đúng các lỗi đó.
3. Lỗi phải được **người thứ ba xác minh** trong ngữ cảnh khác trước khi đưa vào phiếu sửa.
4. Vòng sau **tệ hơn** vòng trước thì **hoàn tác** về bản tốt gần nhất và đổi cách sửa.
5. Cảnh báo khi thợ sửa ngoài phiếu hoặc đổi quá 60% (điểm ảnh với hình, dòng với chữ).
6. **Tối đa 3 vòng.** Hết 3 vòng chưa đạt: dừng, người ra đề quyết hoặc báo Linh.

Khi sửa, ưu tiên cắt bớt, tách ra, đổi cấu trúc, rồi mới thêm.

## 3. Giữ phiên bản

Mỗi vòng lưu bản chụp vào `.vong/ban-vN/`. Không ghi đè. Bản đầu có khi hay hơn (chị Hương 31/10).

## 4. Tầng 2: học

Sau mỗi lần chạy thật, ghi ≥3 dòng `BAI-HOC.md`. Dòng nào lặp lại ở 2 dự án thì đưa vào SKILL.md hoặc thành một kiểm trong máy đo. Học từ bản Linh sửa tay (LAB049 `hoc-tu-ban-sua`): so bản AI với bản Linh, rút luật.

## 5. Vòng tốt đã có để dùng lại

| Vòng | LAB | Dùng khi |
|---|---|---|
| `vls.py` vòng lặp slide | LAB099 | slide, deck |
| `qc4d.py` cổng, chấm, hoàn tác | LAB105 | mọi chiến dịch 4D |
| research-loop `nhat_ky.py` | LAB085 | thí nghiệm có phép đo |
| cong_kiem + features khoá | LAB098 | phần mềm |
| hiệu chuẩn, học từ bản sửa, chấm từng câu | LAB049, LAB025 | viết |
| critic-loop-writer, gemini-reviewer | `D:\@WF\TOOL\00_WRITING` | viết, Gemini phản biện |
| independent-reviewer 17 tiêu chí | RESEARCH AGENT | bài nghiên cứu |
| casting 3 vòng, persona khán giả chấm | LAB066 | ảnh nhân vật |
| vòng ads, vòng kiểm đăng | LAB084, LAB077 | quảng cáo, bài đăng |
| học ngày, học tuần | LAB040 | kênh tự chạy |
| `tqa.py` thói quen văn AI | LAB080 | soát văn |

## 6. Bài học đã trả giá

- Cổng chỉ đếm thì thợ AI qua bằng cách bịa (LAB105: 7 câu trích bịa, 10/17 link chết vẫn DAT). Máy phải kiểm nguyên văn.
- Không tin báo cáo của thợ, đọc nhật ký công cụ.
- Thước "dùng được" của AI thấp hơn mắt Linh nhiều (LAB099: slide "đạt" bị chê "quá xấu").
