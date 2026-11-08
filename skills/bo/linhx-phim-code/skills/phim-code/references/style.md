# Danh mục style

Nguồn chính: 51 style của Lemo-Opuscar (MIT), mỗi style có `$LIB/styles/<thư-mục>/STYLE.md` là luật hình bất biến. Gallery xem phim mẫu: https://lemomo-ai.github.io/lemo-opuscar/

Cách dùng: chọn style → đọc STYLE.md → giữ nguyên luật hình, còn câu chuyện, cảnh, số liệu là của chủ đề Linh. Không bê truyện hay cảnh của phim demo.

## Gợi ý theo việc của LINHX

| Việc | Style gợi ý | Máy |
|---|---|---|
| Văn hoá, lịch sử, nhà cổ, chuyện dân gian Việt | `ink-wash` (thuỷ mặc), `woodcut` (khắc gỗ, gần tranh Đông Hồ), `shadow-puppet` (gần rối/tuồng), `papercut-red` (Tết), `paper-lantern` (Trung thu) | Lemo |
| Du lịch, địa điểm, bản đồ | `silkscreen-poster`, `urban-sketch`, `watercolor`, `tilt-shift`, `satellite-briefing` | Lemo |
| Giải thích khái niệm, cỗ máy (nối Anatomy LAB055) | `iso-infographic`, `teardown`, `blueprint`, `whiteboard` | Lemo; chữ nhiều thì HyperFrames |
| Số liệu, báo cáo, radar | `dataviz`, `data-physical`, `swiss-motion`, `briefing-board` | HyperFrames hoặc Remotion (làm loạt) |
| Ra mắt sản phẩm, công nghệ, AI | `dark-keynote`, `glass-product`, `hologram-hud`, `living-screencast` | HyperFrames (3D thì Lemo) |
| Bài giảng e-learning (LAB017) | `whiteboard`, `swiss-motion`, `pictogram-motion`, `one-line` | HyperFrames |
| Thiếu nhi, kể chuyện vui | `crayon-book`, `midcentury-toon`, `rubber-hose`, `paper-popup` | Lemo |
| Game, cộng đồng trẻ | `pixel-rpg`, `hd-2d`, `microgame`, `game-show` | Lemo |

## Đủ 51 style (tên gallery · thư mục)

- **Phim bằng chứng** (8): Satellite Briefing `satellite-briefing` · Engineering Briefing Board `briefing-board` · LiDAR Survey `lidar-survey` · Projection on White Model `white-model` · Data Physicalization `data-physical` · Exploded Teardown `teardown` · Microscope Story `microscope` · Archive Light Table `archive-lighttable`
- **Vẽ tay, hội hoạ** (7): Crayon Picture Book `crayon-book` · Watercolor Brush `watercolor` · Chinese Ink Wash `ink-wash` · Impasto Oil Painting `impasto` · One-line Drawing `one-line` · Whiteboard Explainer `whiteboard` · Urban Sketch `urban-sketch`
- **Truyền thống Đông Á** (4): Shadow Puppetry `shadow-puppet` · Ukiyo-e `ukiyoe` · Red Paper-cut `papercut-red` · Paper-cut Lightbox `paper-lantern`
- **In ấn, khắc** (5): Risograph `risograph` · Halftone Dossier `halftone-dossier` · Woodcut `woodcut` · Copperplate Engraving `engraving` · Silkscreen Travel Poster `silkscreen-poster`
- **Đồ hoạ, chữ** (7): Swiss Motion `swiss-motion` · 60s Spy Titles `spy-titles` · Art Deco `art-deco` · Blueprint `blueprint` · Stained Glass `stained-glass` · Pictogram Motion `pictogram-motion` · ASCII/CRT `ascii-crt`
- **Thông tin, keynote** (5): Data Storytelling `dataviz` · Isometric Infographic `iso-infographic` · Dark Tech Keynote `dark-keynote` · Living Screencast `living-screencast` · Sci-fi Hologram HUD `hologram-hud`
- **Hoạt hình** (4): Rubber Hose 1930s `rubber-hose` · 80s Cel Anime `cel-anime-80s` · Sci-Fi Sitcom Toon `scifi-toon` · Mid-century Cartoon `midcentury-toon`
- **Game** (4): 16-bit Pixel RPG `pixel-rpg` · HD-2D `hd-2d` · Microgame Frenzy `microgame` · Game Show Flat `game-show`
- **Điện ảnh, thời đại** (2): 1920s Silent Film `silent-film` · Liminal Found Footage `backrooms`
- **Chất liệu, 3D** (5): Brick Toy `brick-toy` · Paper Pop-up `paper-popup` · Tilt-Shift `tilt-shift` · Low-poly Island `lowpoly-island` · Glass Product `glass-product`

## Lưu ý khi Việt hoá style
- Chữ trong STYLE.md hay chỉ định font Latin/Trung (Cormorant, ZCOOL...). Thay bằng font cùng tinh thần có dấu tiếng Việt: serif nghiêng → Noto Serif Italic; sans đậm → Be Vietnam Pro; chữ thư pháp → Dancing Script hoặc vẽ nét bằng code. Kiểm dấu chồng (ặ, ỗ, ữ) ở cỡ lớn.
- Style Đông Á gốc Trung/Nhật: giữ ngữ pháp hình (khoảng trắng, mực năm sắc, dấu son) nhưng đề tài, kiến trúc, trang phục phải là Việt (mái đình, nón lá, ruộng bậc thang), không bê hoạ tiết Trung.
- Style 3D (three.js) chạy chậm trên máy không GPU; làm nháp ở 960×540.
- Muốn biến một style thành style riêng của Linh: theo `$LIB/MY-STYLES.md`, lưu ở `~/lemo-my-styles/<ten>/`.
