# Brand Safety cho VSMCamp & CSMO Summit 2026 (Linh gửi 16:04 18/11, Claude chỉnh cho sự kiện)

Nguồn: bộ BTMH (thiệp kỷ niệm gia đình) của Linh. Sự kiện này khác: khách là dân marketing B2B, ảnh là ảnh sự kiện (sân khấu, slide, booth, networking), chữ là câu hỏi cho Lam, bình luận, câu hỏi diễn giả.
Code hiện có: `apps/lab/server/v1/brand-safety/` (tu-dien-goc.json, loc-lop1.js, loc-ai.js PROMPT_CHU/PROMPT_ANH, loc-anh.js). GIỮ khung 2 lớp, GIỮ `doi_tuong_bao_ve`, `tu_noi_xau`. Chỉ BỔ SUNG theo dưới.

## A. Ảnh (PROMPT_ANH + nhãn) — áp cho Bảng tin, ảnh BTC, chụp bìa kiosk
Chặn tuyệt đối (giữ nguyên ý bộ BTMH):
1. Trẻ em cởi trần/không áo/chỉ tã (giữ đủ phần "VẪN CHẤP NHẬN": ba lỗ, hai dây, đồ bơi trẻ em có áo, khăn quấn, yếm, váy). Ảnh trẻ em đã bị khoá công khai sẵn: giữ.
2. Giấy tờ tuỳ thân, thẻ ngân hàng lộ số, giấy khai sinh, bệnh án.
3. Biên lai chuyển khoản, sao kê, giấy nợ, cầm đồ.
4. Ảnh chụp màn hình tin nhắn chat (Messenger, Zalo, SMS), bài mạng xã hội toàn chữ kiểu bóc phốt. **NGOẠI LỆ SỰ KIỆN: ảnh chụp slide, màn LED sân khấu, standee, backdrop có nhiều chữ là ảnh hợp lệ.**
5. QR thanh toán (VietQR, Momo, ngân hàng) và QR/link lạ. **NGOẠI LỆ: QR trên backdrop, booth, standee, thẻ đeo sự kiện.**
6. Bàn thờ, bát hương, vàng mã, tang lễ, di ảnh, vòng hoa tang, bia mộ; tai nạn, máu, vết thương, ẩu đả, vũ khí, kinh dị.
7. Meme bôi nhọ, anime/hentai 18+.
8. Chân dung/ảnh ghép/deepfake lãnh tụ, lãnh đạo Đảng, Nhà nước (Bác Hồ, Võ Nguyên Giáp, Tô Lâm, Nguyễn Phú Trọng, Lương Cường, Phạm Minh Chính, Trần Thanh Mẫn...), chính khách quốc tế; tiền polymer in hình Bác Hồ. Người nổi tiếng: CHỈ chặn ảnh ghép/deepfake/giễu nhại, KHÔNG chặn ảnh thật chụp cùng diễn giả/khách mời tại sự kiện.
9. Quốc kỳ, cờ Đảng, búa liềm, quốc huy, huy hiệu Đoàn/Đội/Quân đội/Công an; cờ 3 sọc; biểu tượng tà đạo (Pháp Luân Công); biểu tình bạo động.
10. Khoả thân, bán khoả thân, đồ tắm hở hang gợi dục; ảnh cố tình làm mờ/vỡ hạt để lách.
11. Tội phạm, truy nã, còng tay, trại giam, phiên toà; giễu nhại quân phục.
12. Nhậu bê tha, say xỉn, bar bay lắc, bóng cười, shisha, ma tuý. **VẪN CHẤP NHẬN: nâng ly gala, tiệc networking, cụng ly văn minh.**
13. Ảnh rác: đen xì, trắng toát, nhoè nặng.
BỎ khỏi bộ BTMH: luật đối thủ vàng bạc (PNJ, SJC...) — không liên quan; luật "bắt buộc có mặt người" — **CHỈ áp cho ảnh "Lên bìa/Chụp bìa cùng Lam"** (bìa phải có ít nhất 1 mặt người rõ), Bảng tin thì ảnh sân khấu/slide không người vẫn hợp lệ.
Lý do từ chối: dùng câu thân thiện giọng Lam, theo mẫu `THONG_DIEP_MAC_DINH.anh`, kèm gợi ý cụ thể (vd "Bạn chọn ảnh khoảnh khắc ở sự kiện giúp Lam nhé").

## B. Chữ — lớp 1 từ điển (thêm vào tu-dien-goc.json, đúng nhóm)
Thêm vào chặn cứng (có dấu): đụ má, địt mẹ, chịch, nứng, quay tay, thủ dâm, dâm dục, gái gọi, mại dâm, gái dịch vụ, kích dục, ấu dâm, hiếp dâm, cuồng dâm, loạn luân, bú cu, húp sò, mẹ mày, đồ ngu, thằng ngu, chó chết, chó đẻ, đồ chó, súc vật, khốn nạn, loz, đcmm, bốc bát họ, vay nặng lãi, cờ bạc, lô đề, giết người, xả súng, đâm chết, cờ 3 sọc, cờ ba sọc, việt nam cộng hòa, vnch, phản động, việt tân, vịt tân, đảo chính, lật đổ, chống phá, chống cộng, khủng bố, bạo động, pháp luân công, cờ đảng, cờ búa liềm, búa liềm, đảng kỳ, bác hồ, cụ hồ, tô lâm, nguyễn phú trọng, bác trọng, lương cường, phạm minh chính, trần thanh mẫn, võ nguyên giáp, trần đại quang, phạm văn đồng, nguyễn bá thanh, trịnh xuân thanh, putin.
Không dấu: dit me, dit con me, con me may, dit me may, bu cu, loan luan, chem chet, giet nguoi, co ba soc, viet nam cong hoa, phap luan cong, gai goi, hiep dam, au dam, boc bat ho, vay nang lai, bieu tinh bao dong.
**KHÔNG THÊM (gây chặn nhầm ở sự kiện):**
- "hồ chí minh" — khách nói "TP Hồ Chí Minh", "từ Hồ Chí Minh ra" rất nhiều. Chỉ chặn "bác hồ", "cụ hồ".
- PNJ, SJC, DOJI, BTMC... — diễn giả/khách nói về thương hiệu là chuyện thường ở hội nghị marketing.
- "cc", "vl" đứng riêng: chuyển sang NGHI (gọi AI), vì "cc" (đồng gửi email) hay gặp.
- "quốc kỳ", "cờ tổ quốc", "đảng cộng sản", "biểu tình", "xuyên tạc", "đả kích", "thù địch": chuyển sang NGHI, vì câu hỏi trung tính vẫn có thể nhắc.
- "tự tử", "tự sát": KHÔNG chặn kiểu "nội dung chưa phù hợp". Với chat Lam: Lam trả lời ân cần, ngắn, gợi ý tìm người hỗ trợ (đường dây nóng sức khoẻ tâm thần), không giảng giải. Với nơi công khai (Bảng tin, câu hỏi diễn giả): giữ lại chờ BTC duyệt.
- "nắm quyền", "phang", "cave", "tình dục" đứng riêng: bỏ hoặc NGHI.

## C. Từ NGHI (chỉ kích hoạt lớp AI, không chặn)
Thêm: thổi kèn, giết, chém, súng, đâm, cướp, cút, đểu, vãi, chửi, ba sọc, cc, vl, quốc kỳ, cờ tổ quốc, đảng cộng sản, biểu tình, xuyên tạc, đả kích, thù địch, tự tử, tự sát.
**KHÔNG thêm** (hội nghị marketing dùng hằng ngày, sẽ gọi AI vô ích, chậm, tốn tiền): tiền, nợ, vay, đánh (đánh giá), tấn công (tấn công thị trường), chết, máu, tù, tội, thuốc, chính quyền (đã có trong cụm nghi).

## D. Ngoại lệ an toàn (whitelist)
Thay whitelist BTMH bằng: toàn bộ `doi_tuong_bao_ve` hiện có + "tp hồ chí minh", "thành phố hồ chí minh", "tp hcm", "hồ tây", "trúc bạch", "ascott", "le bros", "lê bros", "gelex", "đánh giá", "tấn công thị trường", "chiến dịch", "cc email". Whitelist chỉ gỡ khớp từ điển lớp 1 trong cụm đó, không tắt lớp AI.

## E. Mức áp theo nơi
- Chat riêng với Lam (điện thoại, kiosk): chặn cứng + nghi→AI. Lam từ chối khéo theo `THONG_DIEP_MAC_DINH.lam`. Không lưu công khai.
- Nơi công khai (Bảng tin, câu hỏi diễn giả, bình luận, chữ trên bìa): toàn bộ A–D; ca AI không chắc → vào hàng "Duyệt" của admin, không tự đăng.
- Câu Lam nói ra (kiosk đọc to): Lam không bình luận chính trị, tôn giáo, lãnh đạo, so sánh chê đối thủ/nhà tài trợ; lỡ bị hỏi thì lái về sự kiện.
