---
name: ai-photobooth-golden-standard
description: Quy chuẩn vàng Prompt Engineering, kiến trúc đa góc chụp (Full-body, Waist-up, Close-up), khóa nhận diện khuôn mặt 1:1, tỉ lệ cơ thể siêu mẫu 1:8 chống đầu to, biểu cảm cười mỉm khép môi chống đơ/chống già, và 10 bài học thực chiến (Lessons Learnt) cho AI Photobooth sự kiện (Gemini Image). Kích hoạt khi thiết kế, viết prompt, tạo concept hoặc tối ưu chất lượng hình ảnh AI Photobooth.
---

# Quy Chuẩn Vàng AI Photobooth & 10 Bài Học Thực Chiến (VEEW 2026 Standard)

Tài liệu tham chiếu gốc đầy đủ tại repo IFAGENT:
- [`d:\LINHX\PRJ\IFAGENT\docs\TIEU-CHUAN-PHOTOBOOTH.md`](file:///d:/LINHX/PRJ/IFAGENT/docs/TIEU-CHUAN-PHOTOBOOTH.md)
- [`d:\LINHX\PRJ\IFAGENT\docs\standards\photobooth-reference\04-veew-2026-lessons-learnt\PROMPTS-VA-BAI-HOC-THUC-CHIEN.md`](file:///d:/LINHX/PRJ/IFAGENT/docs/standards/photobooth-reference/04-veew-2026-lessons-learnt/PROMPTS-VA-BAI-HOC-THUC-CHIEN.md)

---

## 1. Mười Bài Học Thực Chiến Bắt Buộc Nhớ (10 Production Lessons Learnt)

1. **Cấm yêu cầu cười tươi hở răng (`"radiant smile"` / `"celebrity smile"`) → Chỉ cười mỉm nhẹ khép môi (`gentle closed-lip micro-smile`):**
   - *Lý do:* Khi ép mô hình vẽ nụ cười tươi, AI tự động vẽ miệng há rộng lộ hàm răng giả đơ cứng, đồng thời **tự khắc sâu 2 rãnh cười (`nasolabial folds`), vết chân chim (`crow's feet`) và nếp nhăn dưới mắt** làm khách bị già thêm 5–10 tuổi.
   - *Quy tắc:* Luôn khóa `EXPRESSION LOCK — GENTLE CLOSED-LIP MICRO-SMILE ONLY, NEVER A BIG TOOTHY SMILE`.
2. **Khóa chống già & cấm tự ý thêm nếp nhăn (`STRICT ANTI-AGING & ZERO-WRINKLE LOCK`):**
   - Luôn chỉ định rõ: `looking 5-8 years YOUNGER and fresher than Image 1. STRICTLY FORBIDDEN: NEVER add forehead lines, NEVER add crow's feet, NEVER add nasolabial folds (smile lines/creases around the mouth), NEVER add under-eye bags or sunken cheeks.`
3. **Đồng bộ 100% gương mặt giữa góc Toàn thân (`full`), Nửa thân (`medium`) và Chân dung (`closeup`):**
   - *Lỗi kỹ thuật từng gặp:* Đặt timeout ngắn (`1200ms`) cho bước `detectSubjects` (Gemini Vision) ở góc chụp đầu tiên (`full` với cờ `fastFirst`) khiến góc `full` bị chạy với `subject = null` (mất khóa khuôn mặt 1:1), trong khi góc `medium` và `closeup` lấy được `subject` từ cache nên mặt góc Toàn thân khác hẳn 2 góc còn lại.
   - *Quy tắc:* Không bao giờ cắt ngang `detectSubjects` bằng timeout ở góc `full`. Cả 3 góc phải `await` chung một Promise `detectSubjects` đã cache + khóa `FULL-BODY 1:1 FACE CONSISTENCY LOCK`.
4. **Khóa tỉ lệ cơ thể siêu mẫu `1:8` chống đầu to (`SLENDER 1:8 RUNWAY MODEL HEAD-TO-BODY PROPORTION`):**
   - *Lý do:* Ảnh gốc `Image 1` là selfie chụp gần nên đầu rất to. Tuyệt đối **cấm dùng từ `"with a large, sharp face"`**.
   - *Quy tắc:* Phải chỉ rõ `scale the head DOWN to a sleek, compact 1:8 fashion-model head-to-body ratio: head height ~11-12% of total body height in full-body, ~18-20% in waist-up, shoulder width 2.5x to 3x head width, NEVER oversized head or bobblehead`.
5. **Chống đầu to ở các concept Hậu trường / Đạo diễn nền tối (`nguoi-to-chuc`):**
   - *Lý do:* Đeo tai nghe (`broadcast headset mic`) làm phình vùng đầu; cầm bảng cue trước ngực + bàn mixer tiền cảnh (`foreground console`) che mất thân người; mặc áo đen tuyền chìm vào nền tối làm mất hai bờ vai → gây ảo giác đầu to thân nhỏ.
   - *Quy tắc:* Cấm đạo cụ đội đầu (`NO headset on head`), cấm vật cản che thân người (`NO foreground console blocking torso`), dùng blazer có đệm vai rộng gấp **3 lần đầu** (`shoulder width 3x head width`) được đánh đèn viền vàng (`warm golden rim light`) tách rõ bờ vai khỏi nền tối.
6. **Tuỳ chỉnh độ mịn da theo tính chất Concept:**
   - Concept Thời trang / Dạ hội / Sân khấu / Cổ phục: Da mịn sáng hồng `flawless rosy-ivory matte-satin skin, zero oily shine`.
   - Concept Đạo diễn / Lãnh đạo hậu trường: Giữ hạt da DSLR tự nhiên `authentic, natural DSLR skin micro-texture with fine natural pores — DO NOT over-smooth, blur, or wax the skin`.
7. **Khóa khoảng cách 2 mắt tự nhiên (`EYE SPACING LOCK — NEVER CLOSE-SET EYES`):**
   - Ở góc rộng (Toàn thân / Nửa thân), AI hay vẽ hai con ngươi sát vào sống mũi. Phải khóa: `keep a wide, balanced, natural spacing between both eyes (at least one full eye-width apart) — NEVER pinch, narrow, or draw the eyes close together`.
8. **Tách bỏ từ khóa thân dưới khi chụp góc Nửa thân (`medium`) và Cận cảnh (`closeup`):**
   - Nếu giữ nguyên các từ `ankle-length robe, wide white silk trousers, shoes` khi chụp góc `medium` (cắt ngang eo), AI sẽ cố nhét cả quần trắng và gấu áo vào ngang bụng!
   - *Quy tắc:* Dùng `stripLowerBodyWardrobeTerms()` xóa sạch từ khóa thân dưới ở góc `medium`/`closeup` và thêm khóa `WAIST-UP CUT (UNBROKEN UPPER ROBE, NO TROUSERS OR HEM IN FRAME)`.
9. **Cổ phục Việt Nam (`Áo ngũ thân lập lĩnh tay chẽn`) — Cấm dùng từ `"tunic"`:**
   - Từ `"tunic"` làm AI vẽ áo ngắn ngang gối. Phải ghi rõ: `long ankle-length Vietnamese Imperial Áo ngũ thân lập lĩnh tay chẽn (traditional 5-panel long silk robe reaching all the way down to the ankles, calf/ankle-length hem well below the knees, upright mandarin collar cổ đứng lập lĩnh, diagonal right-side lapel fastening with five small gold/jade buttons, slim fitted sleeves tay chẽn) worn over wide-legged white silk trousers (quần lụa trắng ống rộng)`.
10. **Xoay vòng bảng màu tự động (`Colorway Rotation`) cho trang phục truyền thống:**
    - Không cố định 1 màu duy nhất trong prompt. Phải có mảng ≥ 6 phối màu Hoàng Gia (`AO_NGU_THAN_COLORWAYS`) tự động xoay vòng ở mỗi lượt chụp mới (`!opts.followUp`) và giữ cố định màu đó cho cả 3 góc trong cùng 1 lượt chụp.

---

## 2. Mẫu `CANON_HEADER` & `CANON_FOOTER` Chuẩn Vàng

### `CANON_HEADER`
```text
Masterpiece editorial fashion & celebrity portrait photograph shot on Canon EOS R5 with RF 85mm f/1.4L USM lens at f/2.0, ISO 100, 4K luxury magazine lookbook quality.
MANDATORY ANATOMY, HEAD-TO-BODY PROPORTION & YOUTHFUL K-BEAUTY FACE LOCK:
- SLENDER 1:8 RUNWAY MODEL HEAD-TO-BODY PROPORTION — NEVER OVERSIZED HEAD: Even though Image 1 is a close-up selfie with a large head in frame, you MUST scale the head DOWN to a sleek, compact, natural 1:8 fashion-model head-to-body ratio. In full-body shots, head height must be small and neat (~11-12% of total body height, with shoulder width 2.5x to 3x head width). In waist-up shots, head height must be ~18-20% of frame height with broad, graceful shoulders and elongated neck and torso. NEVER render a big head, bobblehead, or short torso.
- EYE SPACING LOCK — NEVER CLOSE-SET EYES: Strictly preserve the exact natural horizontal interpupillary distance (IPD) between the left and right eyes from Image 1. Keep a wide, balanced, natural spacing between both eyes (at least one full eye-width apart) — NEVER pinch, narrow, or draw the eyes close together toward the nose bridge.
- EXPRESSION LOCK — GENTLE CLOSED-LIP MICRO-SMILE ONLY, NEVER A BIG TOOTHY SMILE: Keep the mouth softly closed with a serene, subtle, graceful micro-smile at the corners of the lips (cười mỉm nhẹ nhàng, thanh lịch) or match the exact natural calm lip posture from Image 1. STRICTLY FORBIDDEN: NEVER generate a wide open-mouth smile, NEVER show big artificial teeth, NEVER force an exaggerated or stiff grin.
- STRICT ANTI-AGING & ZERO-WRINKLE LOCK (5-8 YEARS YOUNGER, ZERO ADDED WRINKLES): Keep 100% unmistakable identity and facial bone structure from Image 1, while making the subject look 5-8 years YOUNGER and fresher than in real life. STRICTLY FORBIDDEN: NEVER add forehead lines, NEVER add crow's feet around the eyes, NEVER add nasolabial folds (smile lines/creases around the mouth), NEVER add under-eye bags, tear troughs, Marionette lines, or sunken cheeks. Erase all shadows or lines that make the face look older.
```

### `CANON_FOOTER`
```text
 Lighting: soft flattering studio beauty key light + warm champagne-gold rim backlight, crisp diamond catchlights in both eyes, smooth optical bokeh.
STRICT PROHIBITIONS: NO giant/oversized head or bobblehead proportion, NO close-set or crossed eyes, NO wide open-mouth toothy grin or stiff fake smile, NO added wrinkles or nasolabial smile creases, NO aged or tired facial features, NO raw copy-paste of webcam background or harsh shadows, NO oily/greasy skin shine, NO matronly or old-fashioned outfits, NO short knee-length Ao Ngu Than tunic, NO trousers or lower hem visible in waist-up shots, NO extra fingers, NO text, NO logos, NO watermarks.
```
