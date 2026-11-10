# Quy trình viết giọng Linh · bản 0.2 · MÁY MSI (sửa theo bài thử 1, 11/11)

Ngày 10/11/2026. Concept do Linh đặt trong thread "Gom bộ skill viết theo giọng Linh"; Claude phản biện và ghép luật Vân Anh. Quy trình cũ (new-article 9 bước, viet-bai 7 trạm, BM1) KHÔNG dùng. Chỉ giữ phản biện của Vân Anh.

Chạy trên **máy MSI (máy cá nhân)**, Antigravity (agy). Bộ này tự đủ, không cần repo: mọi file tham chiếu và script nằm trong `D:\LINHX\writing\_BO-QUY-TRINH\` (gọi tắt là `<BO>`).

```
<BO>\QUY-TRINH-VIET-GIONG-LINH.md   file này
<BO>\tham-chieu\bai-mau\            7 bài Linh đã đăng (mốc giọng)
<BO>\tham-chieu\LUAT-VAN-ANH.md      luật Vân Anh
<BO>\tham-chieu\GIONG-LINH.md        sổ tay 11 nước đi
<BO>\scripts\                        kiem_nhap.py, kiem_van.py, cham_cau.py, moc-giong.json (đo lại từ 7 bài: trung vị 27,0 từ/câu)
```
Cần Python 3 trên MSI (`py -3`).

---

## 0. Cách test tay

1. Tạo thư mục bài: `D:\LINHX\writing\<yyyy-mm-dd>-<ten-ngan>\`. Mọi file của bài nằm ở đây.
2. Mỗi bước dưới đây có một **khung lệnh**. Mở **phiên agy mới** cho từng bước, dán khung lệnh, thay chỗ `<...>`.
3. Bước có chữ **CHẤM** thì mở thêm một phiên agy mới khác để chấm. Phiên chấm không được là phiên đã làm.
4. Bước có chữ **CỔNG** thì agy dừng. Anh đọc, sửa, rồi gõ `DUYET <cổng>` vào `NHAT-KY.md` mới sang bước sau.
5. Sau mỗi bước, anh ghi một dòng vào `TEST-QUY-TRINH.md` (mẫu ở mục 9). Đây là phần bàn giao lại cho Claude.

### Khung chung, dán ĐẦU mọi phiên agy
```
Bạn đang làm MỘT bước trong quy trình viết giọng Linh.
Đọc trước: D:\LINHX\writing\_BO-QUY-TRINH\QUY-TRINH-VIET-GIONG-LINH.md, mục 1 (luật chung) và mục của bước <mã bước>.
Thư mục bài: D:\LINHX\writing\<thư mục bài>\. Chỉ ghi file đầu ra của bước này. Không sửa file của bước khác.
Không bịa. Mọi câu trích, chuyện, số phải có link gốc và trích nguyên văn. Không tìm được thì ghi "CHƯA CÓ NGUỒN", không đoán.
Xong thì ghi 1 dòng vào NHAT-KY.md: giờ bắt đầu, giờ xong, file đã ghi, chỗ còn yếu.
```

---

## 1. Luật chung (mọi bước)

**L1. Ý là của Linh.** Máy tìm, đề xuất, chấm. Linh chốt ý và viết nháp. Vân Anh: "chỉ dùng được ý, không dùng được một sự diễn đạt nào"; "bài chạy tự động càng nhiều càng nát".

**L2. Nhãn nguồn cho từng mục.**
- `LINH`: câu Linh đã viết hoặc nói (bài cũ, nháp, ghi âm).
- `NGUON`: có link gốc + trích nguyên văn ngôn ngữ gốc + bản dịch nếu cần.
- `GIA-LAP`: máy tự nghĩ hoặc suy ra. Không được vào bài nếu Linh chưa xác nhận.

**L3. Giọng tác giả đè luật chung.** Mốc giọng là 7 bài Linh đã đăng ở `<BO>\tham-chieu\bai-mau\`. Mốc đo (7 bài): câu trung vị 27,0 từ, trung bình 27,4 (dải 20–39), câu trên 35 từ chiếm khoảng 20%, chữ "tôi" khoảng 4,9/1.000 từ.

**L4. Luật Vân Anh** (`<BO>\tham-chieu\LUAT-VAN-ANH.md`):
| Mã | Luật |
|---|---|
| VA-01 | Bỏ lối so sánh hai vế ("X thì…, còn Y thì…"). Cả bài chỉ vài câu. |
| VA-02 | Không "không còn là… mà là". |
| VA-03 | Không láy lại cụm của câu trước để nối câu sau. |
| VA-04 | Số phải gánh luận điểm. Số trang trí thì bỏ. Không nhắc lại số ở đoạn xa. |
| VA-05 | Ẩn dụ không kéo từ đoạn này sang đoạn khác; không xếp nhiều ẩn dụ, định nghĩa liên tiếp cho một người. |
| VA-06 | Chủ thể gọi được tên: chính phủ nào, nhà kinh tế nào, hội thảo nào. |
| VA-07 | Chuyện mở bài phải nghe thật: chi tiết đời thường, thời gian hợp lý, không tóm tắt kiểu bệnh án. (CHẶN) |
| VA-08 | Câu cụt mang ý lớn thì viết đủ ý. |
| Ứng viên | Không tiêu đề kiểu "X không biến mất, nó chuyển nhà"; tránh cụm dịch văn Mỹ; thuật ngữ giải nghĩa lần đầu; không kết có hậu gọn gàng. |

**L5. Kho chung là vault của Linh**, không lập kho mới. Vault ở 3 bản rời trên MSI, tìm cả 3 (bản nào không có trên MSI thì ghi vào NHAT-KY rồi bỏ qua):
- `D:\LINHX\LAB\LAB070-VAULT-MEDIUM` (vault Medium, ĐANG BẮT ĐẦU LÀM 10/11: dùng phần đã có; chưa có gì liên quan thì ghi "vault chưa có" vào NHAT-KY rồi đi tiếp, không chờ)
- `D:\LINHX\IDEA\CONTENT_VAULT` (có `_DIGEST`, nugget)
- `D:\@WF\TOOL\CONTENT_VAULT`
Bài cũ của Linh: 7 bài mẫu ở trên.

**L6. Hạn mức để bài không phình.** Mỗi loại nguyên liệu tối đa 5 mục, chuyện thật tối đa 10. Đủ thì dừng, không tìm cho đủ số.

**L7. Việc cần trình duyệt** (nguồn tiếng Trung, Zhihu, Medium trả phí, Gemini Deep Research): chạy trên Chrome MSI nếu đã đăng nhập; chưa đăng nhập thì ghi "cần trình duyệt" vào TEST-QUY-TRINH.md, không đoán nội dung.

---

### Chế độ chạy
- **Đủ cổng** (mặc định): Linh duyệt D1–D4, Linh viết nháp K5.
- **Linh chỉ đưa ý**: Claude chốt D1, D2 thay và ghi lý do vào NHAT-KY; chỉ dừng chờ Linh ở D3 (chọn phương án) và D4 (bản cuối). K5: Linh chọn "tự viết nháp" hoặc "cho máy viết nháp từ phiếu" — chọn máy viết thì ghi rõ trong NHAT-KY, và lúc D4 Vân Anh/Linh đọc kỹ hơn (luật L1 bị nới).

### Ai đang cầm bài
Dòng đầu NHAT-KY.md: `CAM: <ai> · <máy> · <giờ>`. Thấy có người cầm thì không chạy song song cùng bài.

### Nguồn mồi
Claude được bỏ vào đề B3 các nguồn đã kiểm sẵn (link mở được, trích khớp), ghi `MOI-DA-KIEM`. agy kiểm lại 1 lần rồi dùng, không tìm lại từ đầu.

### Cho agy tự chạy (không dán tay)
agy -p không người duyệt sẽ tự từ chối ghi file và chạy lệnh (bài thử 1: 3 phiên dừng < 1 phút, 0 file). Muốn tự chạy phải cấp quyền trước cho phiên đó (Linh cho phép toàn quyền trong thư mục bài). Không cấp được thì dán tay từng phiên.

## 2. Thư mục một bài

```
<thư mục bài>\
  NHAT-KY.md              mỗi bước một dòng + các dòng DUYET
  TEST-QUY-TRINH.md       Linh ghi khi test (mục 9)
  00-Y-GOC.md             B1
  01-DOC-GIA.md           B2
  02-KHO-Y.md             B3   ← CỔNG D1
  03-HUONG.md             B4a
  03-CHAM-HUONG.md        B4b (phiên chấm)
  04-PHIEU-NGUYEN-LIEU.md B4c  ← CỔNG D2
  05-KHUON.md             K1
  06-GIONG.md             K2
  07-PHUONG-AN.md         K3 + K4
  07-CHAM-PHUONG-AN.md    K4 (phiên chấm)  ← CỔNG D3
  08-NHAP-LINH.md         K5 (Linh viết)
  09-BAN-MUOT.md          K5 (máy làm mượt)
  10-BIEN-TAP.md          K6 (phiếu biên tập)
  11-BAN-CUOI.md          K6  ← CỔNG D4
  THU-HOACH.md            cuối mỗi giai đoạn (mục 6)
  SO-QUY-UOC.md           mở từ B3, cập nhật tới cuối
```

---

## 3. KIM CƯƠNG 1 · Giai đoạn 1: phát triển ý, tìm nguyên liệu

### B1. Ý gốc (Linh nói, máy ghi, 5 phút)
Linh nói tự do hoặc ghi âm, một lúc nhiều ý cũng được. Máy ghi nguyên lời vào `00-Y-GOC.md` (nhãn LINH), rồi đề xuất 2 câu quan điểm từ chính lời Linh để Linh chọn/sửa. Kênh kèm độ dài mặc định (CafeBiz Góc nhìn ~1.500 từ, Dân trí Tâm điểm ~1.500–2.000, Facebook ~400–800).
Đủ các mục:
- Ý loé lên (1–3 dòng, lời của Linh).
- Kênh đăng (Dân trí, VnExpress, CafeBiz, Facebook, Substack...) và độ dài dự kiến.
- **Một câu quan điểm tạm:** "Tôi nghĩ ……, điều người khác chưa nói là ……". Được phép mơ hồ, đổi sau.

Đạt khi: có đủ 3 mục.

### B2. Độc giả (agy)
```
<khung chung>, bước B2.
Đọc 00-Y-GOC.md.
1. Dựng 3 độc giả cho kênh <kênh>, NEO VÀO ĐỘC GIẢ THẬT: bình luận thật dưới bài cùng chủ đề trên kênh đó, bài cũ cùng kênh, phân tầng người Việt (tuổi, nghề, thu nhập, vùng). Mỗi ý về độc giả ghi nguồn (link bình luận/bài) hoặc nhãn GIA-LAP.
2. Mỗi độc giả: là ai (1 dòng cụ thể, có tên giả, tuổi, nghề), đang tin gì về chủ đề này, ĐÃ ĐỌC GÌ về chủ đề này (3 bài/nguồn họ có thể đã gặp, có link), nỗi đau, mong muốn, kỳ vọng từ bài, điều họ ghét (giọng dạy đời, số liệu dồn, chuyện bịa...).
3. Chọn MỘT độc giả chính, giải thích 2 dòng vì sao.
4. Ghi "khoảng trống": điều độc giả chính chưa được ai nói cho.
Ghi 01-DOC-GIA.md, tối đa 600 từ.
```
Đạt khi: 3 độc giả, mỗi người có mục "đã đọc gì" có link; có 1 độc giả chính; mục GIA-LAP không quá một nửa.

### B3. Kho ý (agy, có thể chia nhiều phiên theo loại)
Thứ tự rẻ tới đắt. Mỗi loại tối đa 5 mục (chuyện thật tối đa 10). Lọc theo **độc giả chính**, không theo chủ đề chung.
1. Bài cũ của Linh (7 bài mẫu + nháp cũ): ý Linh đã viết có liên quan. Nhãn `LINH`.
2. Vault (3 bản ở L5): bài tâm đắc, câu trích Linh đã lưu.
3. Chuyện thật thú vị, sâu sắc, đặc biệt, **đa ngôn ngữ** (Việt, Anh, Trung, Nhật, Hàn, Đông Nam Á...). Đây là phần quan trọng nhất.
4. Quote sâu sắc, hài hước, triết lý. Phải truy được người nói và nơi nói.
5. Ngạn ngữ, ca dao, tục ngữ, thành ngữ cổ (Việt và nước khác). Ghi xuất xứ (sách, tuyển tập, vùng).
6. Chuyện xuyên ngành làm nền: văn học, sinh học, động vật học, vật lý, hoá học, tôn giáo... Mỗi chuyện có nguồn khoa học hoặc văn bản gốc.
7. Khung lý thuyết (xã hội, kinh tế, tâm lý, triết học): tối đa 2.
8. Meme, phim, bài hát, tranh, sách: ghi tên + vì sao hợp. Không chép lời bài hát.

```
<khung chung>, bước B3, loại <số loại> (<tên loại>).
Đọc 00-Y-GOC.md, 01-DOC-GIA.md (độc giả chính).
Tìm tối đa <5 hoặc 10> mục loại này hợp với độc giả chính và câu quan điểm tạm. Tìm trong vault (L5) trước, rồi mới ra ngoài.
Mỗi mục ghi 1 dòng bảng vào 02-KHO-Y.md:
| # | Loại | Tóm 1 câu | Trích nguyên văn (ngôn ngữ gốc) | Link gốc | Nhãn LINH/NGUON/GIA-LAP | Hợp với độc giả chính 1–3 | Dùng để làm gì (mở bài, đỡ ý, phản bác, kết) |
Mở link kiểm lại từng mục. Link chết hoặc trích không khớp thì bỏ, ghi vào phụ lục "đã loại".
Tên riêng, thuật ngữ, cách viết số mới gặp: ghi vào SO-QUY-UOC.md.
```
Đạt khi: không mục nào thiếu link; 100% trích nguyên văn khớp nguồn (người chấm mở ngẫu nhiên 5 link để thử); có ít nhất 1 mục `LINH`.

**CỔNG D1.** Linh đọc `02-KHO-Y.md`: gạch, thêm, phản biện. Ghi `DUYET D1`. Rồi chạy **THU HOẠCH 1** (mục 6).

---

## 4. KIM CƯƠNG 1 · Giai đoạn 2: ấn định ý và nguyên liệu viết

Ý ở giai đoạn 2 **được phép khác** giai đoạn 1, nhưng:
- ghi 1 dòng vào NHAT-KY: "đổi từ …… sang …… vì nguyên liệu ……";
- ý đổi thì chấm lại toàn bộ nguyên liệu theo ý mới; thiếu thì quay B3 một vòng hẹp, chỉ tìm cho chỗ thiếu, tối đa 1 lần;
- ý mới do Linh chốt, máy chỉ đề xuất.

### B4a. Ba hướng (agy)
```
<khung chung>, bước B4a.
Đọc 00-Y-GOC.md, 01-DOC-GIA.md, 02-KHO-Y.md (bản Linh đã duyệt).
Đề xuất 3 hướng bài KHÁC NHAU Ở LUẬN ĐỀ (không chỉ khác mở bài). Mục tiêu lớn: đổi nhận thức của độc giả chính, đưa tới điều mới.
Mỗi hướng:
- Luận đề 1 câu.
- Câu X→Y: "Trước khi đọc, <độc giả chính> nghĩ X. Sau khi đọc, họ nghĩ Y." X phải là niềm tin phổ biến, có dẫn chứng từ 01-DOC-GIA.md.
- 2–3 ý phụ, mỗi ý 1 dòng + 1 dòng "vậy thì sao" cho độc giả.
- Nguyên liệu dùng cho mỗi ý (số # trong 02-KHO-Y.md).
- Phản bác mạnh nhất + câu trả lời.
- Gợi ý mở (chuyện/cảnh) + điều độc giả mang về ở kết.
Ghi 03-HUONG.md. Không tự chấm.
```

### B4b. Chấm ba hướng (CHẤM, phiên agy mới)
```
<khung chung>, bước B4b. Bạn là người chấm, KHÔNG sửa bài.
Đọc 01-DOC-GIA.md, 02-KHO-Y.md, 03-HUONG.md, mục 7 (ma trận) của file quy trình.
Chấm 3 hướng theo ma trận. Mỗi điểm phải có 1 câu lý do trỏ về file và dòng cụ thể.
Chấm theo thứ tự C, B, A (đảo thứ tự để tránh thiên vị vị trí).
Áp cổng loại trước khi cộng điểm.
Ghi 03-CHAM-HUONG.md: bảng điểm, hướng bị loại và vì sao, xếp hạng, 3 điểm yếu nhất của hướng đứng đầu.
```

### B4c. Phiếu nguyên liệu (agy, sau khi Linh chọn hướng)
Linh chọn hướng (có thể trộn), ghi vào NHAT-KY.
```
<khung chung>, bước B4c.
Đọc 03-HUONG.md, 03-CHAM-HUONG.md, lựa chọn của Linh trong NHAT-KY.md, 02-KHO-Y.md.
Viết 04-PHIEU-NGUYEN-LIEU.md theo đúng 8 điều ở dưới. Tối đa 800 từ. Mục bị loại để ở phụ lục, không xoá.
Kiểm mật độ ý theo mục 8 so với độ dài kênh.
```
**Phiếu đạt khi đủ cả 8:**
1. 1 ý lớn viết thành câu X→Y, ma trận ý lớn ≥ 40/55, qua cổng loại.
2. 2–3 ý phụ, mỗi ý ≥ 15/25, mỗi ý có 1 dòng "vậy thì sao".
3. Mỗi ý phụ 1–2 chất liệu, trong đó ≥ 1 chuyện thật. Cả phiếu ≥ 1 chuyện xuyên ngành hoặc ngạn ngữ, ≤ 2 khung lý thuyết.
4. 100% chất liệu có link gốc + trích nguyên văn + nhãn. 0 mục không nguồn.
5. 1 phản bác mạnh nhất + câu trả lời.
6. 1 gợi ý mở + 1 điều mang về ở kết.
7. Mật độ ý nằm trong dải của 7 bài (mục 8).
8. Đọc trong 5 phút.

**Phép thử cuối:** Linh viết được nháp gạch đầu dòng ngay từ phiếu, không phải tìm thêm gì. Phải tìm thêm thì ghi thiếu gì vào TEST-QUY-TRINH.md (để sửa B3).

**CỔNG D2.** Linh duyệt phiếu. Ghi `DUYET D2`. Chạy **THU HOẠCH 2**.

---

## 5. KIM CƯƠNG 2 · Triển khai: khuôn × giọng → viết → biên tập

### K1. Khuôn (agy)
```
<khung chung>, bước K1.
Đọc 04-PHIEU-NGUYEN-LIEU.md.
Tìm khuôn bài (cấu trúc) hợp với mục tiêu ĐỔI NHẬN THỨC và độ dài kênh, theo thứ tự:
(1) kho bài mẫu hay trong vault, (2) bài kinh điển, (3) sách/tài liệu dạy viết (kim tự tháp ngược, bánh kẹp, khuôn WSJ, "niềm tin cũ → bằng chứng lạ → niềm tin mới", khuôn kim cương...).
Tối đa 5 khuôn. Mỗi khuôn: tên, sơ đồ các khối (mỗi khối 1 dòng), hợp loại bài nào, độ dài nào, 1 bài thật làm ví dụ (link), vì sao hợp/không hợp phiếu này.
Lưu ý: kim tự tháp ngược hợp tin, ít hợp bài đổi nhận thức.
Ghi 05-KHUON.md.
```

### K2. Giọng (agy)
```
<khung chung>, bước K2.
Đọc 04-PHIEU-NGUYEN-LIEU.md, 7 bài mẫu của Linh, <BO>\tham-chieu\GIONG-LINH.md (sổ tay 11 nước đi).
1. Từ 7 bài của Linh: chọn 3–5 NƯỚC ĐI giọng hợp phiếu này (nhịp câu, cách mở, cách chuyển đoạn, cách dùng "tôi", cách đặt số), mỗi nước đi trích 1 câu thật làm mẫu.
2. Tìm tối đa 3 bài có hành văn kinh điển hợp chủ đề (Việt hoặc nước ngoài). Chỉ rút NƯỚC ĐI cụ thể (không nhại cả giọng), mỗi nước đi trích 1 câu mẫu + link.
3. Đóng gói thành tối đa 3 "giọng" = tổ hợp nước đi. Giọng 1 bắt buộc là giọng Linh thuần.
Ghi 06-GIONG.md. Mốc đo vẫn là 7 bài của Linh (L3).
```

### K3. Ghép phương án (agy)
```
<khung chung>, bước K3.
Đọc 01-DOC-GIA.md, 04-PHIEU-NGUYEN-LIEU.md, 05-KHUON.md, 06-GIONG.md.
Chấm sơ từng khuôn và từng giọng RIÊNG theo độc giả chính (1–5, 1 câu lý do). Lấy top 2 khuôn × top 2 giọng = tối đa 4 phương án. Không ghép hết a×b.
```

### K4. Mẫu ngắn mỗi phương án (agy) + chấm (CHẤM, phiên mới)
```
<khung chung>, bước K4.
Với mỗi phương án (khuôn × giọng): viết MẪU NGẮN, tối đa 300 từ: đoạn mở + dàn ý theo các khối của khuôn (mỗi khối 1 dòng, ghi nguyên liệu # dùng) + 1 đoạn thân.
Không viết cả bài. Chỉ dùng nguyên liệu trong phiếu; không thêm chuyện, số mới.
Ghi 07-PHUONG-AN.md.
```
```
<khung chung>, bước K4-chấm. Bạn là người chấm, không sửa bài.
Chấm 4 phương án trong 07-PHUONG-AN.md theo mục 7 (ma trận phần Phong cách + Ý phụ) và luật Vân Anh L4.
So cặp từng đôi, mỗi đôi chấm 2 lần đảo trái/phải; ghi cả hai kết quả.
Kiểm nhắc lại: chỉ đọc mẫu, tóm ý lớn và các ý phụ; so với phiếu.
Ghi 07-CHAM-PHUONG-AN.md: xếp hạng, lỗi VA mỗi phương án (mã + câu), phương án khuyên dùng.
```
Ghi chú chống chấm ảo: nếu có thể, đưa 1 phương án cho một phiên/mô hình khác (Gemini) chấm mù làm nhóm giữ riêng. Điểm chỉ để xếp hạng, Linh chọn.

**CỔNG D3.** Linh chọn 1 phương án. Ghi `DUYET D3 <phương án>`.

### K5. Linh viết nháp, máy làm mượt
1. **Linh** viết `08-NHAP-LINH.md`: nháp gạch đầu dòng theo phương án thắng, ít nhất nửa độ dài bài (bài 2.000 chữ → nháp ≥ 1.000 chữ). Không cần câu đẹp, cần đủ ý và hàm ý.
2. Máy báo mục mỏng trước khi làm mượt:
```
py -3 D:\LINHX\writing\_BO-QUY-TRINH\scripts\kiem_nhap.py nhap <thư mục bài>\08-NHAP-LINH.md
```
   Mục mỏng thì hỏi lại Linh, không tự lấp.
3. Làm mượt (agy):
```
<khung chung>, bước K5.
Đọc 08-NHAP-LINH.md, 04-PHIEU-NGUYEN-LIEU.md, phương án thắng trong 07-PHUONG-AN.md, 06-GIONG.md, luật L3 và L4.
Làm mượt TỪNG Ý của Linh thành văn xuôi theo khuôn và giọng đã chọn.
CHỈ ĐƯỢC: nối câu, sắp lại, thêm chuyển ý, chỉnh nhịp theo mốc giọng.
KHÔNG ĐƯỢC: thêm chuyện, thêm số, thêm người, đổi mức chắc chắn của câu (rào đón, "có thể", "phần lớn"), đổi ai nói gì, đổi nhân quả, bỏ ý của Linh.
Chỉ thêm thái độ với điều nguồn đã nói, không thêm sự kiện.
Độ dài không quá 1,25 lần nháp (tính theo nội dung, không tính gạch đầu dòng).
Ghi 09-BAN-MUOT.md. Cuối file: bảng "câu nào lấy từ dòng nào của nháp".
```

### K6. Tráng giọng, biên tập, đọc lại
1. Máy kiểm (chạy tay):
```
py -3 D:\LINHX\writing\_BO-QUY-TRINH\scripts\kiem_van.py kiem <thư mục bài>\09-BAN-MUOT.md --moc D:\LINHX\writing\_BO-QUY-TRINH\scripts\moc-giong.json
py -3 D:\LINHX\writing\_BO-QUY-TRINH\scripts\kiem_nhap.py bai <thư mục bài>\08-NHAP-LINH.md <thư mục bài>\09-BAN-MUOT.md
py -3 D:\LINHX\writing\_BO-QUY-TRINH\scripts\cham_cau.py <thư mục bài>\09-BAN-MUOT.md
```
   (`kiem_giu_nghia.py` đang chờ agy viết. Khi chưa có, làm tay bảng kiểm ở bước 2.)
2. Biên tập (CHẤM, phiên mới):
```
<khung chung>, bước K6-biên tập. Bạn là biên tập viên, ra phiếu, KHÔNG viết lại bài.
Đọc 08-NHAP-LINH.md, 09-BAN-MUOT.md, 04-PHIEU-NGUYEN-LIEU.md, SO-QUY-UOC.md, luật L4.
Theo tầng, cấu trúc trước câu chữ sau:
(1) Cấu trúc: luận đề còn đúng 1 câu không? ý phụ ≤ 3? mạch theo khuôn? đoạn thừa?
(2) Giữ nghĩa: so 09 với 08 — số thêm/mất; câu đổi mức chắc chắn; quy kết đổi; nhân quả mới; ý Linh bị bỏ. Liệt kê từng chỗ.
(3) Sự thật: mỗi câu có số, tên, sự kiện → trỏ về mục # trong phiếu. Câu không trỏ được → đánh dấu.
(4) Luật Vân Anh: từng lỗi VA-01..08, ghi mã + câu + gợi ý sửa.
(5) Nhịp: câu đều quá? so mốc L3.
(6) Mật độ ý: đoạn nào > 1 khái niệm mới hoặc > 2 con số.
(7) Kiểm nhắc lại: tóm ý lớn + ý phụ sau khi đọc; khớp phiếu không.
Ghi 10-BIEN-TAP.md: tối đa 10 lỗi nặng nhất, mỗi lỗi có câu gốc.
```
3. Sửa theo phiếu (agy phiên mới), chỉ sửa đúng chỗ phiếu nêu, ghi `11-BAN-CUOI.md`. Tối đa 3 vòng biên tập–sửa. Một lỗi sửa 2 lần vẫn trượt thì dừng, hỏi Linh.
4. **CỔNG D4.** Linh đọc kỹ bản cuối (và gửi Vân Anh nếu cần). Mỗi chỗ Linh/Vân Anh sửa ghi vào THU-HOACH. Ghi `DUYET D4`. Chạy **THU HOẠCH 3**.

---

## 6. Vừa viết vừa tăng kho: THU HOẠCH (máy làm, Linh ≤ 5 phút)

```
<khung chung>, bước THU HOẠCH <1|2|3>.
Đọc các file của giai đoạn vừa xong. Ghi THU-HOACH.md và CHÉP vào vault D:\LINHX\IDEA\CONTENT_VAULT (chưa gộp vault thì ghi vào đây trước):
```
| Lúc | Thu gì | Ghi vào đâu |
|---|---|---|
| Sau D1 | Mọi mục KHO-Y, cả mục bị loại kèm lý do; thẻ chủ đề + loại + nhãn + cờ "đã kiểm nguồn" | vault, thư mục theo loại |
| Sau D2 | Phiếu nguyên liệu; câu X→Y; phản bác + trả lời | vault |
| Sau K1–K2 | Khuôn và nước đi giọng, kèm "dùng ở bài nào" | vault `khuon\`, `giong\` |
| Sau K5 | Câu của Linh trong 08-NHAP-LINH.md → nugget nhãn LINH (đây là cách lấp vault đang 0 nugget lời Linh) | vault `_DIGEST\nuggets\` |
| Sau D4 | Mỗi chỗ Linh/Vân Anh sửa: trước → sau → luật rút ra. Luật có ≥ 2 bằng chứng mới vào hồ sơ giọng | `<BO>\tham-chieu\LUAT-LINH.md` (tạo mới) |
| Sau đăng | Bài đăng (Linh xác nhận) vào bộ bài mốc, đo lại mốc giọng | `<BO>\tham-chieu\bai-mau\`, rồi `py -3 <BO>\scripts\kiem_van.py do-giong <BO>\tham-chieu\bai-mau\*.md -o <BO>\scripts\moc-giong.json` |
| Sau 7 ngày | Số đọc, bình luận thật | hồ sơ độc giả kênh (cho B2 bài sau) |

---

## 7. Ma trận chấm

Thang 1–5. Mức 1, 3, 5 có mô tả neo; 2 và 4 là giữa.

### Ý lớn (luận đề), tổng 55
| Tiêu chí | Hệ số | 1 | 3 | 5 |
|---|---|---|---|---|
| Đổi nhận thức | ×3 | không viết được X→Y | có X→Y nhưng X mờ hoặc Y là điều độc giả đã nghĩ | X→Y rõ, X là niềm tin phổ biến có dẫn chứng |
| Mới với độc giả chính | ×3 | trùng điều họ đã đọc (B2) | góc mới cho chuyện cũ | họ chưa gặp ở đâu; không phải nói ngược cho lạ |
| Đứng vững | ×2 | dựa GIA-LAP | 1–2 nguồn đỡ, chưa trả lời phản bác | ≥ 3 mục NGUON đỡ, đã trả lời phản bác mạnh nhất |
| Của Linh | ×2 | ai viết cũng được | Linh có liên quan | có trong vault/kinh nghiệm Linh, Linh có quyền nói |
| Hợp kênh | ×1 | sai độ dài, giọng kênh | tạm | đúng |

**Cổng loại:** "Đổi nhận thức" < 4, hoặc không viết được X→Y → loại, bất kể tổng.

### Ý phụ (≤ 3 mỗi hướng), mỗi ý tổng 25
| Tiêu chí | 1 | 5 |
|---|---|---|
| Đỡ ý lớn | bỏ đi không sao | bỏ đi ý lớn yếu hẳn |
| Bằng chứng có nguồn | GIA-LAP | NGUON, trích khớp |
| Chất liệu bất ngờ | chuyện ai cũng biết | chuyện thật, xuyên ngành, ngạn ngữ ít người biết |
| Chạm độc giả chính | chung chung | đúng nỗi đau/mong muốn trong B2 |
| Không trùng ý khác | lặp | riêng |
Ý phụ < 15 → thay.

### Phong cách tác giả, tổng 15
| Tiêu chí | 1 | 5 |
|---|---|---|
| Dùng nước đi giọng Linh | 0 nước đi | ≥ 3 nước đi có mẫu |
| Chuyện người thật + tầm vóc + điều mang về | thiếu 2 | đủ 3 |
| Không bị làm phẳng | ≥ 3 lỗi VA | 0 lỗi VA |

### Hiệu chuẩn (làm 1 lần trước khi tin ma trận)
Chấm ma trận lên 7 bài đã đăng của Linh (coi mỗi bài là một "hướng"). Bài của Linh phải đạt ≥ 40/55 ý lớn. Bài nào dưới thì ma trận sai chỗ đó, sửa ma trận trước khi dùng.

---

## 8. Lượng ý vừa sức đọc

- **Ngân sách ý theo độ dài:** dải đo từ 7 bài đã đăng (số ý phụ/1.000 từ, khái niệm mới/đoạn, số liệu/đoạn). Chưa đo. Khi chưa có, tạm dùng: 1 ý lớn + tối đa 3 ý phụ cho bài ≤ 2.000 chữ.
- **Mỗi ý phụ có chỗ thở:** 1 chất liệu + 1 câu "vậy thì sao". Không có chỗ thở thì bỏ hoặc gộp.
- **Cờ đoạn quá tải:** > 1 khái niệm mới hoặc > 2 con số trong một đoạn (VA-04).
- **Kiểm nhắc lại:** phiên mới đọc mù, tóm ý lớn + ý phụ. Thiếu hoặc lẫn → quá tải.
- **Thứ tự cắt khi thừa:** ý phụ điểm thấp nhất → khung lý thuyết → chất liệu trùng chức năng.

---

## 9. Phiếu test quy trình (Linh ghi, để bàn giao)

`TEST-QUY-TRINH.md`, mỗi bước một dòng:
| Bước | Phút | Chạy mấy lần | Đầu ra đạt? (có/không/một phần) | Agy làm sai gì | Prompt cần sửa chỗ nào | Có thừa/bỏ được không |
|---|---|---|---|---|---|---|

Cuối file trả lời 5 câu:
1. Bài cuối có dùng được không, Vân Anh nói gì?
2. Bước nào tốn thời gian nhất, có đáng không?
3. Bước nào agy hay bịa hoặc lạc?
4. Phiếu nguyên liệu có đủ để anh viết nháp không, thiếu gì?
5. Nên gộp, bỏ hay thêm bước nào?

Bàn giao: gửi lại file này + thư mục bài cho Claude trong thread "Gom bộ skill viết theo giọng Linh". Claude sửa quy trình, rồi agy dựng skill `viet-giong-linh` (các phiếu P04–P07 đang khoá chờ).
