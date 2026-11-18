# Brand Safety Yên Lam · VSMCamp & CSMO Summit 2026 (bộ đầy đủ, 18/11 16:10)

Gộp 2 nguồn: (1) LUẬT CŨ đang chạy trong code (`apps/lab/server/v1/brand-safety/`, Linh set từ v0.9), (2) bộ BTMH Linh gửi 16:04, đã chỉnh cho sự kiện marketing B2B. Mục F (3 mức) thắng mọi chỗ khác.
Khung chạy: Lớp 1 từ điển + regex cục bộ (< 1 ms) → Lớp 2 AI Gemini (timeout 4 s) khi lớp 1 nghi hoặc nội dung công khai. Ảnh: lọc màu da/đỏ cục bộ → AI ảnh. Từ BTC tự thêm lưu trong yl.db (bảng bs_tu_dien), sửa ở admin không cần deploy.

## 0. LUẬT CŨ ĐANG CHẠY (GIỮ NGUYÊN, chỉ bổ sung)
13 công tắc luật (`cau-hinh-bs.js`, mặc định bật hết): tuc_tiu, xuc_pham, chinh_tri, ton_giao, phan_biet, noi_xau_thuong_hieu, thong_tin_ca_nhan, quang_cao_link, prompt_injection, anh_khoa_than, anh_bao_luc, anh_bieu_tuong_cam, anh_nhay_cam.
Chữ (`tu-dien-goc.json` + `loc-lop1.js`):
- Tục tĩu: 13 từ có dấu (địt, đụ, lồn, cặc, buồi, đéo, đĩ, đcm, đmm, đkm, đm, đếch, cứt), 24 không dấu/tiếng Anh (vl, cl, djt, vcl, clgt, fuck, shit...), cụm (địt mẹ, đụ má, con cặc, vãi lồn...). Có bảng teencode 24 mục (ko, dc, bik...) để bắt viết lách.
- Xúc phạm: óc chó, súc vật, khốn nạn, mất dạy, vô học, ngu xuẩn... + regex "thằng/con/đồ/mày + ngu/điên/chó".
- Chính trị: phản động, lật đổ chế độ/chính quyền, việt tân, cờ vàng, bò đỏ, ba que, cộng sản độc tài, biểu tình lật đổ...
- Tôn giáo: tà đạo, báng bổ, hội thánh đức chúa trời, thánh chiến cực đoan...
- Phân biệt vùng miền/giới/chủng tộc: bắc kỳ chó, parky, tộc cối, bê đê, mọi rợ, da đen...
- Quảng cáo/cờ bạc/link: nhà cái, cá độ, nổ hũ, tài xỉu, kubet, fb88, w88, vay nóng, việc nhẹ lương cao, liên hệ zalo + regex mọi link/tên miền (http, www, bit.ly, t.me, zalo.me, .com/.vn/.bet...).
- Lộ thông tin cá nhân: regex email, dãy số ≥ 9 chữ số (SĐT), CCCD/CMND/số tài khoản.
- Prompt injection: ~60 cụm Việt/Anh (bỏ qua hướng dẫn, in ra system prompt, cho biết mật khẩu admin, ignore previous instructions, jailbreak...) + regex cấu trúc ([system], <|im_start|>).
- Bảo vệ thương hiệu: danh sách đối tượng bảo vệ (VSMCamp, CSMO, IF Agent, Yên Lam, BTC, nhà tài trợ, GELEX, Le Bros, Le Media, Tạp chí Đẹp, Cadivi, Viglacera, Thibidi, MEEPower, EMIC, "sự kiện này"...) × từ nói xấu (lừa đảo, lùa gà, scam, rác rưởi, tẩy chay, bóc phốt, cùi bắp, đạo nhái...) → chặn.
- Cụm nghi (gọi AI): nhạy cảm, chính quyền, biểu tình, đảng phái, khiếu nại btc, phí tiền mua vé, treo đầu dê bán thịt chó...
Ảnh (`loc-ai.js` PROMPT_ANH + `loc-anh.js`): khoả thân, nhạy cảm/gợi dục, bạo lực/máu/vũ khí, biểu tượng cấm/phát xít/thù ghét/chữ phản cảm trên áo, cử chỉ tục (ngón giữa), cờ trẻ em (ảnh có trẻ em không lên chỗ công khai). Ảnh nghi bị làm mờ (độ mờ 18 px). Ngưỡng màu da 0,58, màu đỏ 0,35.
Câu báo khách (giọng Lam): chung, tên, bìa, ảnh, mạng chậm, Lam từ chối, diễn đàn, đang chờ BTC xem.

## A. BỔ SUNG từ BTMH — Ảnh (thêm nhãn vào PROMPT_ANH; áp cho Bảng tin, ảnh BTC, chụp bìa kiosk)
Đã có trong luật cũ: khoả thân, gợi dục, bạo lực, biểu tượng cấm, cử chỉ tục, trẻ em. THÊM chặn tuyệt đối:
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

## B. BỔ SUNG từ BTMH — Chữ lớp 1 (thêm vào tu-dien-goc.json đúng nhóm, BỎ QUA từ đã có ở mục 0)
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

## F. LUẬT 3 MỨC (Linh 16:05, THẮNG mọi chỗ khác)
Mọi nội dung khách gửi lên nơi công khai (ảnh Bảng tin, chữ kèm ảnh, câu hỏi diễn giả, bình luận, chữ trên bìa, ảnh chụp bìa kiosk) chia đúng 3 mức:
1. **SẠCH → TỰ DUYỆT**, hiện ngay trên giao diện, không chờ admin. (Hiện nay mọi ảnh đều chờ duyệt: bỏ hành vi đó, trừ ảnh trẻ em vẫn khoá như cũ.)
2. **NGHI → hàng "Duyệt" của admin**, khách thấy "đang được BTC xem qua", admin bấm Duyệt mới hiện, Ẩn thì không hiện.
3. **VI PHẠM (chặn cứng lớp 1 hoặc AI kết luận vi phạm rõ) → LOẠI THẲNG**, báo khách lý do thân thiện, KHÔNG vào hàng admin (chỉ đếm số lượt bị chặn).
Lỗi/timeout AI → coi là NGHI (không tự duyệt).
Chat riêng với Lam không đăng công khai: chỉ dùng mức 3 (Lam từ chối khéo), không vào hàng duyệt.

## G. Thông tin cá nhân trong ngữ cảnh sự kiện
Luật cũ chặn email/SĐT trong chữ công khai: GIỮ cho Bảng tin, bình luận, câu hỏi diễn giả. NGOẠI LỆ: ô nhập email ở cổng vào và chat riêng với Lam khi khách tự đưa email của chính mình (không lưu ra chỗ công khai, không in log).
