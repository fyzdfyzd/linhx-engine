---
name: lang-thang
description: Người ảo lang thang đọc bài người khác, xem trend và tiêu hoá thành ghi chú. Dùng cho bước doc, tieu_hoa, trend của phiên kênh ảo.
---

# Lang thang, xem trend, tiêu hoá

Gọi CLI là `python "${CLAUDE_PLUGIN_ROOT}/scripts/kenhao.py" --home <kênh>`.

**Đọc.** Nguồn đọc theo thứ tự: (1) file NDJSON từ extension social hoặc LAB039 trong `doc-vao/`; (2) nếu được Linh bật, trình duyệt có người xem, chỉ đọc. Mỗi dòng NDJSON: `{nen_tang, tac_gia_ma, tac_gia, url, noi_dung, chu_de:[...], tuong_tac, dang_luc}`. Gắn `chu_de` bằng từ trong trụ cột nhân vật khi khớp. Rồi `doc-nhap <file>`.

**Tiêu hoá.** `doc-ds --chua-tieu-hoa`, đọc kỹ, gom 4 đến 8 bài cùng ý thành một ghi chú: `tieu-hoa --tu 12,15,19 --loai insight|y_tuong|ve_nguoi|trend|ngon_ngu_cong_dong|dieu_khong_lam --ghi-chu "..."`. Ghi chú nói được điều mình rút ra, kèm câu chữ cộng đồng hay dùng. Một ghi chú tiêu hoá được tính gấp đôi một lượt đọc trong luật 10:1, vì nó là phần nghĩ.

**Trend.** Mỗi tuần `trend --ngay 7`, rồi viết một ghi chú `--loai trend`: chủ đề nào lên, ai dẫn, nhân vật nói được góc nào khác mà vẫn đúng tính cách.

**Persona.** Với bài có phản ứng mạnh, gắn nhãn cho xưởng persona (xem skill **xuong-persona**).

Không đọc để sao chép: ý tưởng đi vào ghi chú bằng lời của mình; không chép câu, ảnh, video của người khác vào bài.
