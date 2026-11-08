# Bộ prompt ảnh – Jollibee Joy Station

> Đã tạo 30/09/2026 trên ChatGPT (bản không mascot): kv_hero, idea_01…05, booth_render_3d. Màn kiosk, khung hologram và vị trí cạnh photobooth được chừa trống để ghép file mascot chính thức (đặt `mascot/ong-bee-idle.png` rồi build lại).

Cách dùng:
1. Mở ChatGPT Plus (tạo ảnh) hoặc Google Flow. Với mọi ảnh có mascot: **tải lên ảnh mascot Ong Bee chính thức** do Jollibee cung cấp làm ảnh tham chiếu, dặn giữ nguyên thiết kế. Không để AI tự vẽ lại mascot.
2. Dán prompt, chọn đúng tỉ lệ khung.
3. Tải ảnh về, **đổi tên đúng tên file bên dưới** (đuôi .png / .jpg / .webp đều được), lưu vào thư mục `images/` cạnh `proposal.json`, ghi đè bản tạm.
4. Chạy lại build (hoặc nhắn Claude "build lại proposal"). Deck tự lấy ảnh mới nhất theo tên.

Câu dặn chung (dán thêm vào cuối mọi prompt có mascot):
> Use the uploaded mascot image as the exact character reference. Do not redesign, recolor or change its proportions, face, outfit or logo. Keep the brand red (#D7141A) and yellow (#FFC20E). No text other than what is specified. No real celebrity likeness.

---

## KV-01 · `kv_hero` · 16:9 · Ảnh bìa, ý tưởng chủ đạo
Công cụ: ChatGPT Plus hoặc Google Flow
```
Wide 16:9 key visual for a festive family activation called "Joy Station" inside a bright Vietnamese shopping mall during Lunar New Year. Center-right: the uploaded mascot waving happily next to a tall vertical interactive kiosk screen that shows the same mascot talking. A Vietnamese family (parents and two kids aged 5–9) laughs and dances in front of a large LED wall; red and gold Tet decorations, lanterns, apricot blossoms, confetti. Warm cinematic lighting, shallow depth of field, glossy commercial photography style, left third kept clean and darker for headline text.
```

## ID-01 · `idea_01_live_mascot` · 16:9 · Ý tưởng Trò chuyện cùng Ong Bee
```
A child around 6 years old talking to a 55-inch portrait kiosk screen in a mall; on the screen the uploaded mascot is animated and speaking, a subtitle bubble reads a friendly greeting. Parents watch smiling. Red and yellow booth branding, soft bokeh background, photorealistic commercial style, 16:9.
```

## ID-02 · `idea_02_dance` · 16:9 · Nhảy Vui Vẻ
```
Motion dance game in a mall: a 3x2 meter LED wall shows the uploaded mascot demonstrating a dance move and a live score; two kids and a dad copy the move on a marked 2x2 m floor square, glowing skeleton-tracking dots subtly overlaid on their bodies. Energetic, confetti, festive red and gold lighting, 16:9 photorealistic.
```

## ID-03 · `idea_03_photobooth` · 16:9 · Khung Tết Cả Nhà
```
Family photobooth with a red-and-gold Lunar New Year frame; the uploaded mascot stands beside a Vietnamese family holding a freshly printed 4x6 photo; a small QR code card on the counter. Bright ring light, cheerful, photorealistic, 16:9.
```

## ID-04 · `idea_04_hunt` · 16:9 · Săn Lì Xì Vui
```
Teenagers scanning a red envelope-shaped QR standee in a shopping mall corridor with a phone; the phone screen shows a digital stamp card with 3 of 5 stamps collected; small mascot sticker on the standee (use uploaded mascot). Festive, lively, 16:9, photorealistic.
```

## ID-05 · `idea_05_holo` · 16:9 · Hologram flagship
```
A premium glass hologram display box in a fast-food flagship restaurant, the uploaded mascot appears as a glowing 3D hologram talking to a child who waves at it, warm restaurant interior with red and yellow accents, cinematic, 16:9.
```

## Tuỳ chọn · `booth_render_3d` · 16:9 · Phối cảnh booth 3D
Dùng khi muốn thay `booth_layout` (mặt bằng) bằng phối cảnh. Đặt tên file `booth_layout` nếu muốn thay hẳn trong slide mặt bằng.
```
3D isometric render of a 40 square meter event booth in a mall atrium: entrance arch with two vertical kiosk screens, a dance zone with a 3x2 m LED wall, a photobooth corner with printer, a gift counter and a queue area with benches. Brand colors red #D7141A and yellow #FFC20E, clean architectural visualization, soft shadows, 16:9.
```

---

## Ảnh màn hình (scr01–scr10)
Các ảnh `scr01_attract` … `scr10_dashboard`, `tech_architecture`, `booth_layout` là mockup dựng tự động từ `mockups.json`, đúng bố cục thật nên thường **giữ nguyên**. Muốn bản đẹp hơn:
- Chụp màn hình từ bản demo IFAGENT thật (kiosk `/?id=…`, trang Điều khiển, Dashboard), lưu đè cùng tên. Đây là cách tốt nhất.
- Hoặc đưa ảnh mockup vào ChatGPT kèm câu: "Restyle this kiosk UI mockup into a polished, high-fidelity app screen. Keep the exact layout, texts and proportions (1080x1920). Replace the dashed mascot placeholder with the uploaded mascot image."

## Video demo (Google Flow / Veo) – tuỳ chọn
- `video_demo_01` (8 giây, 9:16): "The uploaded mascot on a vertical kiosk screen waves, then leans forward and speaks cheerfully to the viewer; soft festive background, seamless loop-friendly start and end pose."
- `video_demo_02` (8 giây, 16:9): "A family walks up to the Joy Station booth, the kid dances in front of the LED wall, then the family laughs holding a printed photo; handheld commercial style."
Video không tự vào deck; chèn tay vào slide ý tưởng chủ đạo khi thuyết trình.
