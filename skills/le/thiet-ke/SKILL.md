---
name: thiet-ke
description: Workflow thiết kế đầu cuối cho một ấn phẩm (logo, poster, pano, social, KV) hoặc một landing page - đề bài, tham chiếu thật, moodboard, nhiều phương án, chấm mù chống mùi AI bởi người không phải thợ, sửa nhiều vòng, kiểm đầu cuối trên khổ thật. Chạy được trên agy qua agy-tu-chay. Dùng khi Linh bảo làm, làm lại hoặc sửa logo, poster, landing.
---

# thiet-ke

Cần cài cạnh: `linhx-chuan` (sổ, chấm, kiem.py) và `agy-tu-chay` (nếu giao agy).
Hai nhánh dùng chung 4 pha, khác ở bước dựng và bước kiểm:
- **an-pham**: logo, poster, pano, social, KV. Tham chiếu: `references/an-pham.md`.
- **landing**: landing page, trang bán hàng. Tham chiếu: `references/landing.md`.

## Luật gốc (đọc trước mọi bước)
1. **Có bộ design gốc** (logo vector, font, guideline) thì AI không vẽ chữ, logo, giao diện; chữ đặt bằng font thật. **Không có bộ gốc** (Linh 2/11) thì được cho AI vẽ logo và chữ, chấp nhận sai sót, nhưng mỗi chỗ AI vẽ phải ghi một dòng vào `THAY-SAU.md` (vị trí, AI vẽ gì, sai sót thấy được, thay bằng gì khi có bộ gốc). Ghi trong BRIEF dòng `Bộ design gốc: có | không`.
2. **Chống mùi AI** là tiêu chí cứng, không phải phần thưởng: `references/chong-mui-ai.md`. Bản nào ≥2/3 người chấm mù đoán "AI làm" thì trượt dù đẹp.
3. **Tham chiếu là tác phẩm người thật làm**, có tên tác giả hoặc studio, tải về thư mục việc, ghi "học: ..." (bố cục, màu, nét, chữ). Không lấy ảnh AI làm tham chiếu.
   **Tra kho LINHX trước, thiếu mới lên web.** Nếu có MCP `linhx-kho` thì gọi `hinh_tim` (landing, đối thủ, poster, logo; lọc `nganh`, `khoi`), không có MCP thì chạy `py -3.12 -m modules.kho.hinh tim ...` trong repo mayquet. Chép ảnh từ đường dẫn trả về vào `tham-chieu/`, ghi nguồn bằng url gốc và tác giả trong bản ghi. Tham chiếu nào dùng được thì gọi `hinh_de_nghi` với `huu_ich=<id>`; trang hay tìm được trên web thì gọi `hinh_de_nghi` với `url` để mẻ đêm thêm vào kho.
4. **Người xem đầu cuối trước**: viết `HANH-TRINH-NGUOI-XEM.md` (ai xem, xem ở đâu: A0 cách 3 m, điện thoại 360 px, feed lướt 1 giây; xem xong làm gì).
5. Luật ảnh của Linh: tối giản, khoảng thở, một chủ thể chính, bố cục 1/3 hoặc trục, không phủ kín khung.
6. Thợ không tự chấm. Người chấm là agy phiên mới, Gemini Ultra hoặc ChatGPT qua Chrome máy công ty, và Linh ở cổng.

7. **Có "bản vàng" làm thước** (học stageshow): mỗi loại việc giữ vài tác phẩm vàng trong `tham-chieu/vang/`. Bắt đầu bằng cách chép cấu trúc bản vàng gần nhất (khổ, cắt, cỡ chữ, nhịp), không dựng từ một cái liếc. Đặt bản của mình cạnh bản vàng ở cùng khổ; bản mình trống hơn, phẳng hơn, nhỏ hơn thì đó là lỗi sửa đầu tiên.
8. **Kế hoạch trước khi vẽ**: ghi đặt ở đâu, cỡ xem thật, vật trung tâm, việc xảy ra, kết quả, cái gì bỏ được; đếm ngân sách chữ thật (3–7 cụm).
9. **Sửa lỗi lớn nhất trước**: khung và cắt → thứ bậc → chuyển động → chi tiết. Nhìn như người designer khó tính nhất sẽ chụp đúng một chỗ sai gửi lại: tưởng tượng được ảnh chụp đó là thấy lỗi kế tiếp.

## Thư mục việc
```
BRIEF.md  ANCHOR.md  STATUS.md  HANH-TRINH-NGUOI-XEM.md  THAM-CHIEU.md  DATA_GAPS.md
tham-chieu/   (ảnh tải về + nguon.json)
MOODBOARD.md  moodboard.png
PHUONG-AN.md  pa/A/ pa/B/ pa/C/   (mỗi PA: file nguồn SVG/HTML, PNG xuất, prompt.txt nếu có ảnh AI)
cham/<vong>-<nguoi>.json   CHAM-MU.md
kiem/  (ảnh chụp khổ thật, mô phỏng xem xa, 360/1280)
DUYET-E2E.md  BAI-HOC.md  THAY-SAU.md (chỗ AI vẽ tạm, cần thay)
```

## 4 pha
| Pha | Việc | Đầu ra | Cổng |
|---|---|---|---|
| D1 Khám phá | Đọc bản cũ (nếu sửa) và ghi chính xác vì sao trượt; đề bài; người xem; ≥8 tham chiếu người thật | BRIEF, ANCHOR, HANH-TRINH, THAM-CHIEU, `CHAN-DOAN.md` (khi sửa bản cũ) | |
| D2 Định hướng | Moodboard 1 trang; 3 hướng khác nhau thật (khác bố cục, chất liệu, chữ, không chỉ khác màu); mỗi hướng 1 phác nhanh | MOODBOARD, PHUONG-AN.md | **Linh chọn 1–2 hướng** |
| D3 Dựng | Dựng hướng đã chọn bằng chữ thật và file nguồn sửa được; ảnh AI chỉ làm thành phần, đã qua soi lỗi | pa/<X>/ | |
| D4 Chấm và hoàn thiện | Chấm mù 3 người (16 tiêu chí linhx-chuan + 5 tiêu chí thiết kế + câu hỏi mùi AI); sửa ≤3 lỗi/vòng, ≤3 vòng, tệ hơn thì hoàn tác; kiểm khổ thật | cham/, CHAM-MU, kiem/, DUYET-E2E | **Linh duyệt bản cuối** |

## Tiêu chí thiết kế thêm (1–5, cộng với `linhx-chuan/cham.md`)
- **Đọc ở khổ thật**: thông điệp chính đọc được ở khoảng cách hoặc cỡ màn của HANH-TRINH.
- **Một điểm nhìn**: mắt dừng ở 1 chỗ trước, rồi đi theo thứ tự đã định.
- **Riêng**: đổi tên thương hiệu khác vào thì không còn đúng nữa (không chung chung).
- **Người làm**: không có dấu hiệu nào trong `chong-mui-ai.md` mục A.
- **Đúng văn hoá**: chi tiết Việt đúng (chữ có dấu, biển hiệu, trang phục, kiến trúc).

## Kiểm máy
`python {SKILLS}/thiet-ke/scripts/kiem_thiet_ke.py . --nhanh an-pham|landing --pha d1|d2|d4`
- d1: đủ sổ, ≥8 tham chiếu, mỗi tham chiếu có file ảnh thật trong `tham-chieu/` và có tác giả/nguồn + "học:".
- d2: ≥3 hướng trong PHUONG-AN.md, mỗi hướng có ảnh phác.
- d4: có THAY-SAU.md (BRIEF ghi "Bộ design gốc: không" thì phải có ≥1 dòng, mỗi dòng đủ 4 cột); ≥3 phiếu chấm từ ≥2 người khác thợ; tỉ lệ "đoán AI" ≤1/3 ở bản cuối; ảnh kiểm khổ thật có; landing thêm: ảnh 360 và 1280, không tràn ngang (đọc `kiem/do.json` do Playwright ghi).
Sau đó `python {SKILLS}/linhx-chuan/scripts/kiem.py . --pha cuoi`.

## Thử tình huống
**Thử skill kiểu A/B** (cách Benji làm stageshow): cùng một đề ngắn, giao 2 agent mới tinh, một có skill một không; đặt hai kết quả cạnh nhau; thấy lỗi thì **sửa skill, không sửa sản phẩm**, rồi chạy lại cả bộ. Cặp đúng/sai từ các bản Linh chê được lưu vào `cap-dung-sai/` để dạy (bản sai không bao giờ là điểm xuất phát).
`tinh-huong.md` có 12 tình huống (6 mỗi nhánh). Mỗi lần đổi skill, chạy lại ít nhất 2 tình huống mỗi nhánh; ghi kết quả vào `BAI-HOC.md` của skill.

## Giao agy
`ke_hoach.py moi <viec> --loai thiet-ke-an-pham` hoặc `--loai landing` (mẫu phiếu trong agy-tu-chay). Ảnh ChatGPT/Gemini và chấm mù qua Chrome **máy công ty**.
