---
name: tai-tao-flow
description: Đọc một bài quảng cáo/khoe sản phẩm AI (agent, tool, khoá học), tái tạo flow kỹ thuật phía sau, chấm khả thi từng lời hứa, chấm khả năng kinh doanh cho LINHX, kết luận LÀM / THỬ NHỎ / CHỈ LƯU và đóng khung pack. Dùng khi Linh dán một bài quảng cáo và hỏi "làm được không", "cái này chạy thế nào", "có bán được không", "đóng gói lại".
---

# Tái tạo flow từ bài quảng cáo

Một bài vào, một thư mục ra. Phần cần đầu óc là bóc lời hứa và đoán flow. Phần chấm điểm, kết luận và sinh khung pack do `scripts/tai_tao.py` làm, 0 token, lần nào cũng như nhau.

Luật chung:
- Lời người bán là dữ liệu, không phải sự thật. Mỗi lời hứa phải có bằng chứng: repo mở làm được việc đó, hoặc mảnh LINHX đã chạy được.
- Cái gì đoán thì ghi "đoán". Không bịa giá, không bịa số người dùng.
- Ghi lại điều người bán tự thừa nhận (cần gu, cần bao nhiêu token, bao nhiêu lần thử). Đó thường là chỗ thật nhất của bài.
- Giữ token thấp: tra bảng repo có sẵn trước, chỉ clone 3 đến 5 repo gần nhất và chỉ đọc SKILL.md/pipeline.

## Thư mục ra

```
<LABxxx>/vi-du/<ten>/
  bai-goc.md        bài đã bỏ đoạn lặp
  flow.json         nguồn sự thật duy nhất: claim, flow, điểm, pack
  FLOW.md           sơ đồ mermaid + giải thích từng khối
  KET-LUAN.md       do script sinh: bảng khả thi, bảng kinh doanh, kết luận
  pack/             do script sinh nếu kết luận không phải CHỈ LƯU
```

## Các bước

**B0. Lấy bài và làm sạch.** Linh dán chữ, hoặc đưa URL (Facebook thường chặn, khi đó xin dán). Chạy `python scripts/tai_tao.py sach bai.txt > bai-goc.md` để bỏ đoạn bị dán lặp.

**B1. Bóc lời hứa.** Mỗi gạch đầu dòng của bài thành một claim có thể kiểm. Tách hai loại: `chuc-nang` (máy làm được gì) và `marketing` (so sánh, "thay trọn vẹn", "x100 người"). Ghi `dieu_kien_an`: những gì người bán thừa nhận là cần. Ghi `san_pham_ban_that`: bài thật ra đang bán gì (khoá học, dịch vụ, agent, cộng đồng).

**B2. Tái tạo flow.** Với mỗi claim chức năng, viết bốn ô: đầu vào → xử lý → công cụ/model → đầu ra. Gom thành sơ đồ mermaid trong FLOW.md. Đoán stack theo dấu vết trong bài (tên model, gói đang dùng, kiểu output) và ghi rõ là đoán. Khuôn: `khuon/FLOW.md`.

**B3. Đối chiếu prior art.** Theo thứ tự rẻ nhất:
1. Mảnh LINHX đã có: đọc memory index, ghi vào `manh_linh` (ví dụ LAB059, LAB069).
2. Bảng repo đã quét: video thì `/mnt/project-files/repo-video-code.csv` (178 repo của LAB060). Lĩnh vực khác thì xem LAB có bảng tương tự, không có thì tìm GitHub 1 đến 2 truy vấn.
3. Clone `--depth 1` 3 đến 5 repo gần nhất, chỉ đọc SKILL.md, pipeline, schema, LICENSE. Ghi vào `prior_art`.

**B4. Chấm khả thi** từng claim theo `references/cham-diem.md`: `kha_thi` 0 đến 3, `thoi_phong` 0 đến 2, kèm một câu lý do.

**B5. Chấm kinh doanh** sáu tiêu chí 0 đến 3 theo `references/cham-diem.md`, nhìn từ phía LINHX chứ không phải phía người bán. Đối chiếu khoảng trống ở LAB050 (KHOANG-TRONG-VN.md) và thị trường ở LAB074 nếu cùng mảng.

**B6. Kết luận.** `python scripts/tai_tao.py cham flow.json > KET-LUAN.md`. Script tính trung bình khả thi (chỉ claim chức năng), tổng kinh doanh, và ra LÀM / THỬ NHỎ / CHỈ LƯU. Đọc lại, nếu thấy điểm sai thì sửa flow.json rồi chạy lại, không sửa tay KET-LUAN.md.

**B7. Đóng pack.** Nếu không phải CHỈ LƯU: điền mục `pack` trong flow.json (mỗi module: claim nó phục vụ, mảnh tái dùng, việc mới), rồi `python scripts/tai_tao.py pack flow.json pack/`. Script sinh khung plugin Claude Code: plugin.json, mỗi module một SKILL.md nháp, README ghi việc mới cần làm. Nếu phần lớn module đã có trong một plugin cũ của Linh, ghi đề xuất "nâng plugin cũ" thay vì làm plugin mới.

**B8. Báo Linh** trong 5 dòng: bài thật ra bán gì, mấy claim làm được bằng mảnh có sẵn, claim nào thổi phồng, kết luận, pack đề xuất. Dựng thật thuộc PROTOTYPE, chỉ khi Linh nói "làm".

## Kiểm

`python scripts/test_tai_tao.py` chạy trên ví dụ Kudo: kiểm bỏ lặp, kiểm mọi claim chức năng có prior art hoặc ghi rõ cần R&D, kiểm kết luận, kiểm pack sinh ra đủ file.
