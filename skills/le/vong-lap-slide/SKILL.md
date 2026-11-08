---
name: vong-lap-slide
description: Vòng lặp tự cải thiện cho slide (HTML Claude Slides/linhx-deck hoặc .pptx): đo trên bản render, người chấm tách thợ, xác minh lỗi, sửa cục bộ, hoàn tác khi tệ hơn, cổng cuối. Dùng sau khi dựng xong deck, trước khi giao.
---

# Vòng lặp slide

Mảng 1/6 của LAB099. Mục tiêu: deck đi qua một vòng **sinh → đo → sửa → dừng** có máy đo thật, và **không sửa quá tay**.

Script: `scripts/vls.py` (Python 3.11+, `pip install playwright pillow numpy python-pptx pymupdf`, `playwright install chromium`; nhánh pptx cần LibreOffice). Đề chấm: `references/cham-slide.md`. Bài học tích luỹ: `bai-hoc.md` (đọc TRƯỚC khi dựng deck mới).

## Ba vai, ba ngữ cảnh

| Vai | Ai | Được làm |
|---|---|---|
| Thợ | người dựng deck (Claude phiên chính, hoặc agy) | sửa đúng slide và đúng lỗi trong `phieu-sua.md` |
| Người chấm | ngữ cảnh khác: subagent Sonnet, `claude -p`, Gemini trong agy | chỉ nhìn ảnh, ghi phiếu theo đề |
| Người xác minh | ngữ cảnh thứ ba | chỉ giữ hoặc bác từng lỗi nặng, không thêm lỗi |

Ghi tên thợ vào `.vong-lap/cau-hinh.json` (`"tho": "agy"`). Script từ chối phiếu chấm hoặc xác minh có tên trùng thợ.

## Bước 0: mẫu top tier TRƯỚC khi dựng (Linh, 30/10)

AI có bệnh thừa chi tiết và trình bày quá nhiều. Nên trước khi dựng:
1. Tìm ≥ 6 slide mẫu top tier đúng loại deck: chuẩn brand (vd BTMH Guideline 2026), Dribbble/Behance (Popular, Most Appreciated), Pinterest, Envato Elements. Ưu tiên tối giản, nhiều khoảng trống. Cloud bị chặn các trang này: lấy bằng Chrome trên máy Linh.
2. `vls.py mau <deck> --anh "<thư mục mẫu>/*.jpg"` sinh bảng ảnh mẫu và `THE-PHONG-CACH.md`.
3. **Giải mã vì sao mẫu đẹp** theo `references/giai-ma-mau.md`: 9 mục đo được cho từng mẫu, rồi tổng hợp 8–12 nguyên tắc lặp lại. Tổng hợp này là guide cho thợ và được chèn vào prompt khi tạo ảnh/template.
4. `vls.py phong <deck>`: đếm đủ 134 chữ Việt dựng sẵn trong từng phông của deck.json và in `bang-dau.png` để soi kiểu dấu. Phông thiếu chữ thì trình duyệt mượn phông khác cho riêng chữ có dấu (Gilda Display, Bodoni Moda, Marcellus thiếu 92/134); `khoa-mau` tự chạy bước này và từ chối khoá. Cần phông brand chưa có tiếng Việt thì Việt hoá bằng Font Tàu Nhanh (xem `references/font-viet-hoa.md`).
5. Điền thẻ (vì sao đẹp, tổng hợp, 3 tính từ, nền, lưới, chữ, màu nhấn, ảnh, ngưỡng tối giản, danh sách cấm), người duyệt, `vls.py khoa-mau <deck>` (còn chỗ "…" thì không khoá được).
6. Thợ đọc thẻ và nhìn mẫu rồi mới dựng. Chưa khoá thì `do` từ chối chạy.

Nhánh template AI (Linh, 30/10): khi cần phong cách riêng cho deck, sau bước 3 cho ChatGPT Plus và Gemini Ultra tạo ảnh template (6 slide trên một ảnh) **kèm ảnh mẫu đã lọc ≥ 4/5** ("nếu ref đẹp": ref xấu thì template xấu). Ba người chấm chấm các ảnh template bằng cùng đề (tiêu chí tối giản, ngang mẫu); bản thắng vào bộ mẫu ở bước 2 và làm guide cho thợ. Ảnh template chỉ là guide: chữ, lưới, màu vẫn dựng bằng HTML/brand, không cắt ảnh AI làm slide (xem quyết định LAB032).

Đặt `"thuong_hieu": "<brand.json khuôn LAB043>"` trong cau-hinh.json để máy kiểm phông và màu ngoài brand.

## Quy trình

```
vls.py do <deck>                 # dựng ảnh 1920×1080, kiểm xác định, ảnh đánh dấu, bảng ảnh
vls.py trang-thai <deck>         # luôn cho biết bước tiếp
vls.py de-cham <deck>            # đề cho từng slide đã qua máy
  → người chấm ghi .vong-lap/de-cham/<id>.json
vls.py cham <deck> --tep <id>.json
vls.py de-xac-minh <deck>        # chỉ khi có lỗi chan/nang
  → người xác minh ghi <id>-xac-minh.json
vls.py xac-minh <deck> --tep <id>-xac-minh.json
vls.py phieu-sua <deck>          # thợ chỉ nhận lỗi máy + tối đa 3 lỗi đã xác minh
  → thợ sửa, rồi `do` lại
vls.py hoan-tac <deck> --slide ID   # khi trang-thai báo "lùi bước"
vls.py de-cham <deck> --deck     # khi mọi slide đạt: chấm nhịp, nhất quán trên bảng ảnh
vls.py ket-thuc <deck>           # cổng cuối, viết BAO-CAO.md; exit 0 chỉ khi đạt
```

`<deck>` là thư mục có `deck.json` + `slides/<id>.html` (Claude Slides, `13-claude-deck/project` của linhx-deck) hoặc tệp `.pptx`. Trạng thái nằm ở `<deck>/.vong-lap/` (pptx: `<ten>.vong-lap/`).

## Máy đo xác định (tầng rẻ, chạy trước người chấm)

HTML, đo trên DOM sau khi phông đã nạp:
- `tran-khung`, `bi-cat`, `tran-the`: chữ ra ngoài slide, bị khung cắt, tràn khỏi thẻ có nền/viền
- `chong-lan`: hai khối chữ đè nhau
- `chu-nho`: dưới 20px ở khung 1920 (lưu ý dưới 24px)
- `tuong-phan`: đo trên **nền thật** (dựng lại slide với chữ trong suốt, so màu chữ với phân vị 5% xấu nhất của điểm ảnh nền dưới chữ); ≥24px cần 3:1, nhỏ hơn cần 4.5:1
- `phong`: phông không nạp được thì số đo tràn không tin được, coi là lỗi
- `tieu-de-dai` (quá 2 dòng), `giu-cho` (lorem, TODO, [CẦN LINH]), `anh-hong`, `tai-nguyen`
- lưu ý: sát mép, chữ mồ côi ở tiêu đề, quá nhiều chữ, quá nhiều trục canh, quá 2 màu nhấn
- tối giản (lỗi cứng): quá 3 cỡ chữ, quá 8 khối thị giác, quá 40 chữ (deck trình bày), khoảng trống dưới 45% (slide không ảnh), vạch trang trí dưới tiêu đề
- brand (khi có `thuong_hieu`): phông ngoài danh sách, màu lệch bảng màu quá ngưỡng ΔE
- cấp deck: tiêu đề cùng loại lệch độ cao, 3 slide nặng liền nhau

PPTX: LibreOffice → PDF; chữ thật lấy bằng PyMuPDF, hộp bằng python-pptx. Dòng chữ nằm ngoài mọi hộp là tràn; tương phản là ước lượng. Phông ngoài danh sách an toàn của skill pptx thì kết quả tràn chỉ gần đúng.

## Người chấm: thước là mẫu, không phải "dùng được"

- 7 tiêu chí: ý chính, tâm điểm, đọc được, cân đối, nhất quán, **tối giản**, **ngang mẫu**. Đạt khi **mọi** tiêu chí ≥ 4. Điểm 3 là "sạch nhưng làm vội", chưa đạt.
- Người chấm mở ảnh mẫu trước, rồi mới nhìn slide.
- Một người chấm dao động (cùng slide lúc đạt lúc hỏng), nên mỗi ảnh cần `so_nguoi_cham` = 3 phiếu từ 3 ngữ cảnh. Điểm lấy trung vị; đạt khi đa số phiếu đạt.

## Sáu luật chống sửa quá tay

1. Chỉ lỗi `chan`/`nang` mới bắt sửa; `nhe` để lại.
2. Mỗi lượt thợ nhận tối đa 3 lỗi chấm (`toi_da_loi_moi_luot`), xếp chặn trước nặng.
3. Lỗi nặng phải qua người xác minh; bị bác thì bỏ. Bác hết và mọi tiêu chí vẫn ≥ 4 thì đạt; còn tiêu chí 3 điểm thì vẫn hỏng (điểm không bị bác theo lỗi).
4. Bản sửa có nhiều lỗi máy hơn, hoặc điểm chấm thấp hơn vòng trước, là **lùi bước**: `hoan-tac`. Ảnh trùng vòng cũ thì phiếu cũ được dùng lại, khỏi chấm lại.
5. Sửa slide không có trong phiếu sửa, hoặc đổi hơn 60% điểm ảnh trong một lượt: cảnh báo.
6. Mỗi slide tối đa 3 lượt sửa (`tran_vong`); quá thì dừng máy, người quyết (đổi bố cục, bỏ ý, tách slide).

## Hiệu chỉnh người chấm (làm định kỳ)

Linh chấm vài slide bằng cùng mẫu JSON rồi `cham --nguoi`. `hieu-chinh` báo tỉ lệ khớp và chỗ máy dễ dãi hoặc khắt khe. Máy dễ dãi thì siết `references/cham-slide.md`; mỗi lần siết ghi một dòng vào `bai-hoc.md` bằng `bai-hoc --ghi`.

## Nối với linhx-deck

Chạy sau bước 13 (xuất Claude Slides), trước khi publish: `vls.py do <deck>/13-claude-deck/project`. `deck.py kiem-deck` vẫn giữ vai kiểm nội dung trên JSON (tiêu đề kết luận, số có nguồn); vls kiểm cái khán giả nhìn thấy.

## Giả định cần biết

- CSS nền của Claude Slides không công khai. vls dùng reset tối thiểu (margin 0, box-sizing border-box) và nạp phông theo `faces` trong deck.json. Nếu trình chiếu thật khác, thêm CSS vào `css_them` trong cau-hinh.json.
- `<aside>` là ghi chú người nói, không tính vào slide.
