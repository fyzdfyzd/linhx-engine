---
name: sd-bo-tham-chieu
description: Quy trình làm ảnh bằng ChatGPT Plus cho một series: đoán khán giả (TA), chuẩn bị brand và logo, tìm 2–3 art style trên Pinterest, chọn style, tạo bộ ảnh tham chiếu đầy đủ (nhân vật, bối cảnh, đạo cụ) và lưu vào thư viện. Dùng sau sd-de-xuat, trước sd-kich-ban, và mỗi khi thêm nhân vật hay bối cảnh mới.
---

# sd-bo-tham-chieu: bộ ảnh tham chiếu bằng ChatGPT Plus

**Tham chiếu luôn đi kèm prompt:** ảnh Pinterest (moodboard) và ảnh tham chiếu của ta **đều tải lên ChatGPT Plus** cùng prompt. Đây là tranh minh hoạ nội bộ, không phải tranh thương mại (Linh, 2026-10-12). Mọi prompt ảnh kết thúc bằng câu tham chiếu, dán nguyên văn:
```
Use the uploaded reference images (style board and our earlier images) for art style, rendering, lighting and palette; draw the characters and scenes described here, not the ones in the reference images.
```
`flow_pack.py` tự thêm câu này vào cuối mọi prompt ở Bước A.

**Luật gốc:** prompt ảnh không gắn tham chiếu thì gần như luôn ra xấu và lệch nhau. Vì vậy **mọi** ảnh của series (ảnh neo, bối cảnh, keyframe, ảnh bìa) đều tạo từ ảnh tham chiếu đã duyệt, không tạo "từ chữ không".

**Thư mục:** `data/series/`
```
TA.md                        bước 1
brand/                       bước 2: logo, bảng màu, font, BRAND.md
moodboard/<style>/           bước 3: ảnh Linh lưu từ Pinterest (chỉ dùng nội bộ để nhìn)
moodboard/PHONG-CACH.md      bước 3: thẻ style
tham-chieu/                  bước 4–5: ảnh do mình tạo, dùng làm tham chiếu thật
tham-chieu/tham-chieu.json   sổ ảnh (script tham_chieu.py ghi)
```
Khởi tạo: `python LAB016-PHIM-NGAN-AI/src/tools/tham_chieu.py LAB016-PHIM-NGAN-AI/data/series khoi-tao`

## Bước 1. Nghiên cứu và đoán TA (Claude, 0 credit)
Từ `NGHIEN-CUU.md` (nếu có) và logline, viết `TA.md`:
- 1–2 chân dung khán giả: tuổi, nền tảng xem (TikTok, Reels, YouTube Shorts), giờ xem, họ đang theo dõi kênh/phim gì.
- Gu hình ảnh của họ: màu, độ "dễ thương" hay "điện ảnh", 2D hay 3D, có chữ trên hình không.
- 3 video hoặc kênh mẫu khán giả này đang xem (có link), mỗi cái 1 dòng: vì sao họ dừng lướt.
- Ghi rõ đây là **phỏng đoán**, kèm cách kiểm (ví dụ: xem bình luận, số lưu của 3 video mẫu).

## Bước 2. Brand (ChatGPT Plus tạo, Claude viết brief)
Claude viết `brand/BRAND.md`: tên series, câu slogan, 5 màu (mã hex) lấy từ gu TA, 1 font tiêu đề có dấu tiếng Việt (Google Fonts), luật ảnh bìa (vị trí tiêu đề, cỡ chữ, nhân vật chiếm bao nhiêu khung).
Linh tạo trong ChatGPT (Images 2.0, chế độ Thinking):
- `brand/logo.png`: logo chữ tiếng Việt, nền trong hoặc nền trơn; xin 4 phương án, chọn 1.
- `brand/bang-mau.png`: dải 5 màu.
Logo xong mới làm style, vì màu brand sẽ dẫn màu của style.

## Bước 3. Tìm 2–3 art style (Linh trên Pinterest, Claude phân tích)
1. Claude đưa **3 hướng style** hợp TA và brand, mỗi hướng 3–4 cụm từ khoá tìm trên Pinterest (tiếng Anh và tiếng Việt), ví dụ `cozy 3d storybook cat`, `watercolor animal village illustration`.
2. Linh lưu 6–10 ảnh mỗi hướng vào `moodboard/<ten-style>/` (ghi link gốc vào `moodboard/<ten-style>/nguon.txt`). Bỏ ảnh tác giả ghi "NoAI" hoặc cấm dùng tham khảo. Nếu đã cài plugin LAB020, dùng skill moodboard của LAB020 thay bước lưu tay.
3. Claude xem ảnh, viết `moodboard/PHONG-CACH.md`, mỗi style một thẻ: chất liệu (3D, màu nước, giấy cắt…), đường nét, ánh sáng, bảng màu, tỉ lệ đầu/thân nhân vật, độ chi tiết nền, điều cần tránh. Cuối thẻ là **câu khoá style** tiếng Anh 1 đoạn, không nêu tên hoạ sĩ hay hãng phim.

Muốn xếp ảnh trên một bảng để so, dùng PureRef (offline). Ảnh moodboard được tải lên ChatGPT ở bước 4 và 5 làm tham chiếu style. Nếu sau này đăng bán hoặc dùng thương mại, xem lại luật của `AI-ASSET-WORKFLOW.md` (chỉ đưa ảnh của ta vào AI).

## Bước 4. Ảnh style của mình và chọn style (trạm `phong_cach`)
Trong **một cuộc chat ChatGPT mới cho series** (dùng lại chat này cho mọi ảnh về sau):
1. Với mỗi style: tải lên `brand/bang-mau.png` + 4–6 ảnh Pinterest của hướng đó, dán prompt sẵn trong `moodboard/PHONG-CACH.md` (đã có câu khoá style và câu tham chiếu), tạo **1 nhân vật chính** (chính diện, nền trơn) và **1 bối cảnh chính** (không người), tỉ lệ 9:16.
2. Lưu thành `tham-chieu/style-<ten>-nv.png`, `tham-chieu/style-<ten>-bc.png`.
3. Claude ghép bảng so sánh, Linh chọn 1 style (hoặc trộn). Ghi:
   `nhat_ky.py <thu_muc_tap> ghi --buoc phong_cach --loai phong_cach --chu-de "Art style series" --chon <ten> --phuong-an ... --ly-do ... --linh-duyet`
   rồi `duyet phong_cach --nguoi Linh`. Câu khoá của style được chọn thành `khoa_phong_cach` trong JSON tập.

## Bước 5. Bộ tham chiếu đầy đủ (trạm `anh_neo`)
Vẫn trong cùng cuộc chat; **mỗi lệnh đều tải lại ảnh style đã chọn, 2–3 ảnh Pinterest của hướng đó** (và ảnh neo nhân vật khi có) rồi mới viết prompt.

| Loại | File | Dùng ở đâu |
|---|---|---|
| Ảnh neo nhân vật: chính diện, toàn thân, nền trơn | `nv-<id>.png` | Gắn vào Flow (Ingredients/keyframe) |
| Sheet xoay 3 góc (trước, nghiêng, sau) | `nv-<id>-xoay.png` | Chỉ để tham khảo khi vẽ keyframe; **không** gắn vào Flow |
| Sheet biểu cảm 6 nét (vui, giận, sợ, buồn, ngạc nhiên, nghi ngờ) | `nv-<id>-bieu-cam.png` | Keyframe cảnh cảm xúc |
| Trang phục khác | `nv-<id>-<trang-phuc>.png` | Nhân vật con, có `khoa` riêng |
| Bối cảnh không người, ngày và đêm nếu cần | `bc-<id>[-dem].png` | Gắn vào Flow, keyframe |
| Đạo cụ quan trọng, nền trơn | `dc-<id>.png` | Keyframe cận cảnh |
| Ảnh "cả dàn" đứng cạnh nhau | `ca-dan.png` | Kiểm tỉ lệ chiều cao giữa các nhân vật |

Sau mỗi ảnh Linh duyệt, ghi sổ:
`python LAB016-PHIM-NGAN-AI/src/tools/tham_chieu.py LAB016-PHIM-NGAN-AI/data/series them nv-muop.png --loai nv_neo --doi-tuong muop --tham-chieu style-am-ap-nv.png --prompt "<prompt đã dùng>"`
Ảnh hỏng thì không lưu vào `tham-chieu/`. Sửa nhân vật: chỉ yêu cầu ChatGPT "giữ nguyên mọi thứ, chỉ sửa X", không tạo lại từ đầu.

## Bước 6. Dùng bộ tham chiếu cho từng tập
- Trong `<tap>.json`, mỗi mục `anh_can_tao` có trường `tham_chieu` (danh sách file trong `data/series/tham-chieu/` hoặc `data/<tap>/anh/`). `kiem_nhip.py` cảnh báo mục nào thiếu; `flow_pack.py` in "Tải lên trước" cho từng ảnh.
- Keyframe: gắn ảnh neo của từng nhân vật có mặt + ảnh bối cảnh, tối đa 3–4 ảnh.
- `python ... tham_chieu.py ... xem` liệt kê thư viện và báo file nào có trong sổ mà thiếu trên đĩa.

## Lưu ý ChatGPT Plus (tháng 10/2026)
- Không có khoá nhân vật giữa các phiên: luôn tải lại ảnh tham chiếu, giữ một cuộc chat cho cả series; chat quá dài thì mở chat mới và tải lại ảnh style + ảnh neo.
- Giới hạn số ảnh không công bố; tạo theo lô nhỏ, duyệt từng ảnh.
- Chữ tiếng Việt trên ảnh (logo, ảnh bìa) làm bằng ChatGPT tốt hơn Veo; trong video vẫn để "No on-screen text".
