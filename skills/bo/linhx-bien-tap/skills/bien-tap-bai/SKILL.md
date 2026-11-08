---
name: bien-tap-bai
description: Biên tập một bài tiếng Việt như một biên tập viên người, qua sáu lượt soát tách ngữ cảnh (máy, sự thật, cấu trúc, ngôn ngữ, chấm từng câu, độc giả ảo), ra phiếu biên tập và bản đã sửa. Dùng khi có bài nháp cần biên tập, chấm, hoặc duyệt trước khi giao.
---

# Biên tập bài (điều phối)

Plugin này là nửa còn lại của plugin viết `linhx-viet-giong-viet`. Người viết và người biên tập không bao giờ là cùng một ngữ cảnh: mọi lượt soát dưới đây chạy trong một subagent mới, nhận bài như **bài của cộng tác viên lạ**, và chỉ thấy đúng những file được giao.

## Đầu vào
- `bai.md`: bài cần biên tập. Mã nguồn `[N1]`, `[T2]` trong câu và dấu `[GIẢ LẬP]`, `[CẦN LINH]` được giữ nguyên trong suốt quá trình.
- `nhap.md` (nếu có): nháp gạch đầu dòng của tác giả. Có nháp thì mọi đoạn, chuyện, số không có trong nháp hay kho là lỗi chặn (máy tự thêm).
- `kho-nguon.md` (nếu có): bảng mã nguồn của bài. Không có kho thì lượt sự thật chỉ đánh dấu, không kết luận đúng sai.
- `don-dat-hang`: kênh, độ dài, độc giả chính. Hỏi người dùng nếu thiếu, mặc định "tạp chí, 1.200–1.500 chữ".
- `so-loi-hoi-quy.json` (nếu có): lỗi đã bắt ở các bản trước. Không có thì tạo mới từ phiếu biên tập lần này.
- Hồ sơ biên tập viên: `${CLAUDE_PLUGIN_ROOT}/ho-so-bien-tap/<ten>/LUAT.md`. Mặc định dùng `van-anh` nếu đã có luật, rồi tới `linh`; nếu cả hai còn trống thì chỉ dùng bảng mã chung và mốc giọng 7 bài đã đăng.

## Luật chung cho mọi lượt
1. Luật giọng của tác giả (`references/goc/EDITORIAL_CHECKLIST.md` phần C và `LUAT.md` của hồ sơ) đứng trên mọi luật chung. Câu đúng giọng tác giả thì giữ, kể cả khi luật chung bắt.
2. Mọi lỗi ghi bằng mã trong `references/ma-loi.md`, kèm câu gốc trích nguyên văn và câu sửa cụ thể. Không ghi lời khen chung, không ghi lỗi không trích được.
3. Biên tập viên **không viết lại cả bài**. Chỉ khi một đoạn bị chấm VIẾT LẠI ở lượt cấu trúc thì trả đoạn đó cho người viết.
4. Không bắt lỗi bịa ở chỗ có dấu [GIẢ LẬP]/[CẦN LINH], nhưng vẫn bắt lỗi cách viết ở đó, và liệt kê các dấu ấy trong phiếu để tác giả xác nhận.
5. Subagent soát dùng mô hình khác người viết nếu có thể (người viết Opus thì soát bằng Sonnet). Không yêu cầu subagent ghi lại quá trình suy nghĩ từng câu; chỉ yêu cầu bảng kết quả.

## Sáu lượt, theo thứ tự
| Lượt | Skill | Ra file | Chặn giao bài khi |
|---|---|---|---|
| 0. Máy | chạy script, không cần subagent | `bt-0-may.md` | trượt ngưỡng `cham_cau.py` hoặc trúng sổ hồi quy |
| 1. Sự thật | `soat-su-that` | `bt-1-su-that.md` | còn lỗi NG, SO, BI, PL |
| 2. Cấu trúc | `soat-cau-truc` | `bt-2-cau-truc.md` | có đoạn VIẾT LẠI, hoặc lệch độ dài quá 15% |
| 3. Ngôn ngữ | `soat-ngon-ngu` | `bt-3-ngon-ngu.md` | CQS dưới 85 hoặc APS trên 30 |
| 4. Chấm từng câu | `cham-tung-cau` | `bt-4-*.md`, `bt-4-tong-hop.md` | trượt ngưỡng ở `scripts/tong_hop_cham.py` |
| 5. Độc giả | `doc-gia-ao` | `bt-5-doc-gia-*.md` | độc giả mang về điều khác luận điểm của bài |

Lượt 0 chạy (thêm `python ${CLAUDE_PLUGIN_ROOT}/scripts/kiem_nhap.py bai nhap.md bai.md --kho kho-nguon.md` khi có nháp):
```
python ${CLAUDE_PLUGIN_ROOT}/scripts/cham_cau.py bai.md --hoi-quy so-loi-hoi-quy.json --cho-phep "<tên riêng có trong kho>"
python ${CLAUDE_PLUGIN_ROOT}/scripts/kiem_van_dich.py bai.md --hoc ${CLAUDE_PLUGIN_ROOT}/scripts/danh-sach-hoc.json --bo-qua "<chữ thuộc đề tài>"
python ${CLAUDE_PLUGIN_ROOT}/scripts/kiem_van.py kiem bai.md --moc ${CLAUDE_PLUGIN_ROOT}/scripts/moc-giong.json
```
Lượt 1, 2, 3, 5 chạy song song được (đều chỉ đọc bài). Lượt 4 chạy sau khi đã sửa theo lượt 1–3, vì chấm câu trên bài còn lỗi sự thật là phí.

## Vòng sửa
1. Gộp lượt 0–3 và 5 thành **phiếu biên tập** `PHIEU-BIEN-TAP.md` theo mẫu `references/mau-phieu.md`: lỗi chặn trước, rồi nặng, rồi nhẹ; tối đa 15 mục sửa, phần còn lại ghi "để sau".
2. Người viết (hoặc chính phiên này nếu người dùng nhờ sửa) sửa **theo danh sách**: câu gốc → câu sửa. Mỗi lỗi chặn đã bắt thành một dòng mới trong `so-loi-hoi-quy.json` (tên, mẫu regex).
3. Chạy lại lượt 0, rồi lượt 4 trên bản đã sửa. Trượt thì sửa theo bảng tổng hợp và chấm lại, tối đa ba vòng. Sau ba vòng vẫn trượt thì dừng, báo tác giả các câu còn bị chấm SỬA/CẮT.
4. Câu hai giám khảo chấm lệch từ hai bậc thì không tự quyết, đưa vào mục "tác giả quyết" của phiếu.

## Giao
- `PHIEU-BIEN-TAP.md` (bản cuối), bản đã sửa, bảng số đo qua các vòng (câu TB, câu dài, GIỮ, SỬA+CẮT).
- Danh sách mọi dấu [GIẢ LẬP]/[CẦN LINH] còn trong bài.
- Bản không mã nguồn: `python ${CLAUDE_PLUGIN_ROOT}/scripts/cham_cau.py bai.md --sach bai-sach.md`, docx: `node ${CLAUDE_PLUGIN_ROOT}/scripts/build_docx.js bai-sach.md bai.docx "DÒNG TRÊN TÍT"` (cần `npm i docx` một lần).
- Nếu tác giả hoặc biên tập viên người sửa thêm bản cuối, lưu cặp trước/sau vào `${CLAUDE_PLUGIN_ROOT}/mau-sua/` và chạy `hoc-tu-ban-sua`. Đây là cách plugin khá lên.
