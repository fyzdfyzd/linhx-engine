---
name: linhx-chuan
description: Lõi chất lượng LINHX. Đọc trước mọi việc tạo sản phẩm cho Linh hoặc khách (chiến lược, giáo trình, slide, báo cáo, thiết kế, ảnh, nghiên cứu). Có 14 luật, thang chấm 16 tiêu chí, khuôn sổ và kiem.py.
---

# linhx-chuan

Skill này là luật chung. Các workflow (`chien-luoc`, `slide`, `bao-cao`...) gọi nó ở bước đầu và bước cuối. Skill tự đủ, không cần mở file nào ngoài thư mục này:

| File | Khi nào đọc |
|---|---|
| `cham.md` | trước khi chấm |
| `khuon/` | đầu mọi việc, chép vào thư mục việc |
| `references/high-standard.md` | khi cần biết thước "chuẩn cao" lấy từ đâu |
| `references/nguon-tham-chieu.md` | khi tìm ≥5 mẫu top tier, tìm nguồn số |
| `references/cong-cu.md` | khi chọn Gemini Deep Research, crawler, agy, máy nào |
| `references/vong-lap.md` | khi chấm và sửa nhiều vòng |
| `references/van-viet-va-anh.md` | trước khi viết hoặc tạo ảnh |

Nếu có `linhx-4d` (chia pha, phiếu, tướng) thì dùng kèm; không có vẫn chạy được.

## Bước đầu mọi việc

1. Tạo thư mục việc, chép 4 khuôn trong `khuon/` vào: `STATUS.md`, `HANH-TRINH-NGUOI-XEM.md`, `THAM-CHIEU.md`, `DATA_GAPS.md`. Có khách thì thêm `ANCHOR.md`.
2. Điền **hành trình người xem** trước khi làm bất cứ thứ gì.
3. Tìm ≥5 mẫu top tier, ghi vào `THAM-CHIEU.md`, mỗi mẫu một dòng "học:".
4. Chạy `python scripts/kiem.py <thu-muc> --pha dau`.

## 14 luật

1. **Khán giả xem từ đầu đến cuối.** Biết ai xem, xem ở đâu (điện thoại, máy chiếu, giấy A4, email), theo thứ tự nào, xem xong phải làm gì. Bước cuối là một lượt duyệt như khán giả: mở bản cuối trên đúng thiết bị, đi hết từ đầu tới cuối, mỗi chặng một ảnh chụp, ghi vào `DUYET-E2E.md`. Chưa có ảnh là chưa xong.
2. **Tham chiếu top tier trước khi làm.** Thước chấm là mẫu, không phải "dùng được". Người chấm mở mẫu trước khi đọc bài.
3. **Tối giản.** AI hay nhồi. Sửa thì ưu tiên cắt, tách, đổi cấu trúc, rồi mới thêm.
4. **Làm tới đâu lưu tới đó.** Mỗi nghiên cứu hoặc mỗi bản là một file có số và ngày (`NC3_DOI_THU_20261102.md`), không ghi đè bản cũ. Sau mỗi file, sửa `STATUS.md`. Thiếu số thì ghi `DATA_GAPS.md`, không bịa. `ANCHOR.md` chỉ đổi khi khách hoặc Linh góp ý, và ghi ngày góp ý.
5. **Mọi số có nguồn.** Gắn `[BC-xxx]`, nguồn nằm trong `bang-chung/INDEX.md`. Câu trích dài từ 30 ký tự phải có nguyên văn trong `bang-chung/`. Người chấm tự mở 5 số ngẫu nhiên đối chiếu nguồn.
6. **Công cụ rẻ trước.** Nghiên cứu: skill `nghien-cuu` (Gemini Deep Research Ultra trên Chrome máy công ty, rồi crawler, Claude khi gấp). Việc tay: agy. Claude ra đề, chấm, phản biện. Trình duyệt luôn là Chrome máy công ty.
7. **Vòng tự cải thiện.** 3 người chấm khác thợ, mỗi lượt sửa ≤3 lỗi chặn hoặc nặng, tối đa 3 vòng, vòng sau tệ hơn thì hoàn tác. Giữ mọi phiên bản, vì bản đầu có khi hay hơn.
8. **Văn Việt chuẩn.** Thuần Việt, câu đủ ý, không giọng AI, không chêm tiếng Anh khi có từ Việt.
9. **Gửi khách.** Nhận yêu cầu thì trả lời ngay: đang làm gì, kế hoạch, giờ xong, sẽ gửi gì. Rà 3 lần trước khi gửi. Ngay trước khi gửi, đọc lại tin mới nhất của Linh.

10. **Bản vàng làm thước** (học stageshow, áp mọi loại việc: chiến lược, slide, báo cáo, giáo trình, thiết kế, nghiên cứu). Mỗi loại giữ vài bản vàng trong `tham-chieu/vang/`. Bắt đầu bằng cách chép cấu trúc của bản vàng gần nhất, không dựng từ một cái liếc. Đặt bản của mình cạnh bản vàng ở cùng khổ: trống hơn, phẳng hơn, mỏng hơn là lỗi sửa đầu tiên.
11. **Năm kiểu hỏng, soi trước khi chấm.** Quá nhiều (nhồi chữ, số, khối); như khung sườn (đúng mục mà không có thịt, không nhận ra sản phẩm hay khách thật); đóng hộp (mọi thứ trong thẻ/bảng đều nhau như dán vào); phẳng (mọi ý cùng sức nặng, không có điểm dừng mắt hay kết luận nổi lên); nhạt (bỏ tinh thần đề bài, thương hiệu, giọng để làm bản an toàn). Chỉ để nội dung thật nặng ký ở chỗ câu chuyện nói tới.
12. **Sửa lỗi lớn nhất trước:** khung và cấu trúc → thứ bậc và mật độ → chuyển động hoặc nhịp → chi tiết. Tưởng tượng người duyệt khó tính nhất chụp đúng một chỗ sai gửi lại; thấy được ảnh chụp đó là thấy lỗi kế tiếp.
13. **Người chấm mắt mới.** Chỉ nhận bản xuất ở đúng khổ người xem, bảng chấm và bản vàng; không nhận kế hoạch, lý do hay STATUS của thợ. Mỗi lỗi phải chỉ ra được trên một trang hoặc ảnh cụ thể. Thợ nói "cố ý" thì người chấm vẫn xét lại.
14. **Nạp đúng nơi xem và tinh thần trước khi làm.** Hình thức theo nơi người xem thật dùng (khách đến từ TikTok/Zalo thì điện thoại; hội đồng thì máy chiếu; in thì giấy). Nạp màu, chữ, giọng, tinh thần thương hiệu hoặc khách trước khi dựng, nếu không bản sạch sẽ trôi về xám và nhạt (bài học thử A/B hero CTS 2/11).

## Cải tiến skill (áp cho mọi skill LINHX)
Thử skill kiểu A/B: cùng một đề ngắn, giao 2 agent mới tinh, một có skill một không; đặt hai kết quả cạnh nhau. Thấy lỗi thì **sửa skill, không sửa sản phẩm**, rồi chạy lại cả bộ tình huống. Bản bị Linh chê lưu thành cặp đúng/sai trong `cap-dung-sai/` của skill để dạy; bản sai không bao giờ là điểm xuất phát. Ghi kết quả thử vào `BAI-HOC.md` của skill.

## Bước cuối mọi việc

1. Chấm theo `cham.md` (thang chung) cộng thang riêng của workflow.
2. Duyệt E2E theo luật 1, ghi `DUYET-E2E.md`.
3. Ghi ≥3 dòng `BAI-HOC.md`, dòng nào đáng thì đưa vào skill.
4. Chạy `python scripts/kiem.py <thu-muc> --pha cuoi`. Chỉ báo xong khi ra `DAT`.

## kiem.py kiểm gì

`--pha dau`: có đủ 4 sổ; hành trình người xem điền đủ 4 câu; `THAM-CHIEU.md` có ≥5 link, mỗi link có "học:".
`--pha cuoi`: thêm `DUYET-E2E.md` có ≥1 chặng và mọi ảnh trong đó tồn tại; `BAI-HOC.md` ≥3 dòng; mọi `[BC-xxx]` có trong `bang-chung/INDEX.md`; mọi câu trích ≥30 ký tự có nguyên văn trong `bang-chung/`; `STATUS.md` nhắc đến mọi file NC và bản nháp có trong thư mục.
`--loai <ten>`: kiểm thêm file và mục bắt buộc của workflow, đọc từ `scripts/loai.json`.
