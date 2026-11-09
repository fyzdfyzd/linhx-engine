# Danh mục skill LINHX

Sinh tự động bằng `python scripts/skill_kiem.py --index`, không sửa tay. Tổng **235** skill.

| Nhóm | Số |
|---|---|
| Thiết kế: ảnh, slide, deck, brand, web, KV | 63 |
| Tự kiểm, tự sửa, vòng lặp chất lượng | 39 |
| Vận hành, điều phối, giao việc | 29 |
| Video, phim, hoạt hình | 17 |
| Viết, biên tập, nội dung | 37 |
| Marketing, cộng đồng, kênh | 26 |
| Nghiên cứu, radar, dữ liệu | 15 |
| Giáo dục, khoá học | 8 |
| Khác | 1 |

## Thiết kế: ảnh, slide, deck, brand, web, KV

| Skill | Làm gì | Ở đâu |
|---|---|---|
| `ai-photobooth-golden-standard` | Quy chuẩn vàng Prompt Engineering, kiến trúc đa góc chụp (Full-body, Waist-up, Close-up), khóa nhận diện khuôn mặt 1:1, tỉ lệ cơ thể siêu mẫu 1:8 chống đầu to, … | `le/ai-photobooth-golden-standard` |
| `anh-sang-slide` | Chế độ "ảnh trọn slide" của linhx-deck - viết prompt từng slide theo ảnh tham chiếu, tạo ảnh slide hoàn chỉnh (có chữ, sơ đồ) trên ChatGPT Plus, rồi chuyển bộ ả… | `le/anh-sang-slide` |
| `audit-brand` | Brand audit toàn diện cho một brand có brand.json (khuôn LAB043): nhận diện hình ảnh, nhất quán đa kênh, giọng và thông điệp, hiện diện trên AI, social. Gọi lại… | `bo/linhx-audit/skills/audit-brand` |
| `bang-su-that` | Lập bảng sự thật (brand-facts.json) cho brand check chuẩn ABC, bằng phỏng vấn chủ thương hiệu hoặc chuyển từ brand.json chuẩn LBS. Dùng ở bước 1 của brand-check… | `bo/linhx-brand-check/skills/bang-su-that` |
| `bao-cao` | Quy trình 13 bước ra báo cáo PDF cao cấp kiểu McKinsey, Kantar, Nielsen (sách trắng, báo cáo ngành, báo cáo khảo sát, báo cáo xu hướng) cho LINHX và các BU. Dùn… | `bo/linhx-report/skills/bao-cao` |
| `bao-cao-va-sua` | Ra báo cáo ABC (HTML + Markdown + kế hoạch 30 ngày), đọc kết quả cùng người dùng, và sinh bản sửa kỹ thuật (JSON-LD, llms.txt, robots). Dùng ở bước 6 của brand-… | `bo/linhx-brand-check/skills/bao-cao-va-sua` |
| `Bespoke Image Generator` | Skill sinh ảnh chuyên nghiệp bằng Gemini API. Sử dụng khi cần tạo ảnh, poster, banner, đồ họa. Tích hợp Forensic Analyzer để phân tích ref, đánh giá output, và … | `le/bespoke-image-generator` |
| `brand-<slug>` | Áp dụng thương hiệu <Tên> (<domain>) cho mọi thứ tạo ra: trang web, giao diện app, slide, bài đăng mạng xã hội, ảnh, email, bao bì, nội dung chữ. Dùng khi người… | `le/brand-mau` |
| `brand-btmh` | Áp dụng thương hiệu Bảo Tín Mạnh Hải (BTMH, vàng và trang sức 24K) cho mọi thứ tạo ra: web, giao diện, slide, bài đăng, ảnh, bao bì, văn bản Word/Excel, nội dun… | `le/brand-btmh` |
| `brand-check` | Kiểm sức khoẻ thương hiệu trong thời đại AI agent theo chuẩn ABC (GEO, AEO, AI visibility, độ đúng, nhất quán, được đề xuất, truth signal, agent-readiness). Dùn… | `bo/linhx-brand-check/skills/brand-check` |
| `brand-chiemtinh` | Áp dụng thương hiệu Chiêm Tinh Số (chiemtinh.vn, báo cáo bản đồ sao tiếng Việt, OPC001) cho mọi thứ tạo ra: landing, báo cáo PDF, bài TikTok/Facebook, blog, ema… | `le/brand-chiemtinh` |
| `brand-guideline-chuan` | Dựng hoặc làm lại brand guideline công ty theo chuẩn BTMH 2026 (LAB043): khung, bộ dựng, ảnh ChatGPT mockup, phương án chọn. Dùng khi Linh bảo làm/rà soát/chạy … | `le/brand-guideline-chuan` |
| `brand-ifagent` | Áp dụng thương hiệu IF Agent (ifagent.net, AI Event Technology) cho mọi thứ tạo ra: web, giao diện, slide, credential, proposal, bài đăng, ảnh, booth sự kiện, e… | `le/brand-ifagent` |
| `brand-sakedemy` | Áp dụng thương hiệu Sakedemy / Sakédemy (sakedemy.com, đào tạo AI thực chiến cho doanh nghiệp) cho mọi thứ tạo ra: web, e-learning, hồ sơ năng lực, proposal, sl… | `le/brand-sakedemy` |
| `brand-tuva` | Áp dụng thương hiệu TUVA (TUVA Communication, Tù Và, tuva.work, truyền thông phát triển cho NGO/donor/CSR) cho mọi thứ tạo ra: web, báo cáo, proposal, slide, bà… | `le/brand-tuva` |
| `brand-unikon` | Áp dụng thương hiệu Unikon (unikon.vn, sub-agency chiến dịch Generative AI) cho mọi thứ tạo ra: web, slide, credential, proposal, bài đăng, ảnh, nhân vật AI, em… | `le/brand-unikon` |
| `brand-urah` | Áp dụng thương hiệu URAH (URAH Network, urah.vn, xưởng sản xuất nội dung AI) cho mọi thứ tạo ra: web, proposal, credential deck, slide, bài LinkedIn/Facebook, ả… | `le/brand-urah` |
| `casting-mat` | Casting gương mặt nhân vật ảo: persona khán giả chấm, vẽ ChatGPT+Gemini có ảnh tham chiếu, 3 round chấm khắt khe 3 góc, Linh duyệt, character sheet. Khi Linh nó… | `bo/linhx-casting/skills/casting-mat` |
| `cham` | Gán nhãn câu trả lời của AI theo bảng sự thật chuẩn ABC (đúng, sai, nhầm, bịa, cũ, không biết, chưa kiểm; có nhắc không; lời khuyên; định vị; cảm nhận; tác vụ a… | `bo/linhx-brand-check/skills/cham` |
| `dan-trang` | Bước 9–12 của linhx-report. Ảnh bìa và mở chương có ref, dựng báo cáo bằng Typst theo phong cách nhà và brand, kiểm bản in bằng script (D01–D17), render từng tr… | `bo/linhx-report/skills/dan-trang` |
| `deck-proposal` | Quy trình 15 bước làm deck proposal kiểu tư vấn chiến lược cho các BU của Linh (Sakedemy, Unikon, URAH, TUVA, IF Agent, Chiêm Tinh Số, [DOANH NGHIỆP BÁN LẺ ĐÃ Ẩ… | `bo/linhx-deck/skills/deck-proposal` |
| `demo-ban-giao` | Bước 14 và 15 của quy trình deck proposal - dựng demo hoặc prototype cho offer (mockup Claude Design, trang HTML một màn, agent mẫu chạy được) và đóng gói bàn g… | `bo/linhx-deck/skills/demo-ban-giao` |
| `dung-deck` | Bước 10 và 13 của quy trình deck proposal - viết ghost deck bằng tiêu đề kết luận, dựng 10-deck.json theo khung proposal 6 phần phong cách tư vấn chiến lược, ki… | `bo/linhx-deck/skills/dung-deck` |
| `hieu-khach` | Bước 1–4 của quy trình deck proposal - tiếp nhận và làm rõ đề bài, nghiên cứu nền có bảng bằng chứng, xác định người nghe và mục tiêu, pain–gain của khách. Dùng… | `bo/linhx-deck/skills/hieu-khach` |
| `hinh-anh` | Bước 8, 11, 12 của quy trình deck proposal - Claude điều khiển Chrome của Linh để tìm và lưu ảnh moodboard trên Pinterest/Dribbble, rút thẻ phong cách, tạo ảnh … | `bo/linhx-deck/skills/hinh-anh` |
| `hinh-du-lieu` | Bước 4 của linhx-report. Biến bằng chứng thành hình (exhibit) chuẩn báo cáo tư vấn: tiêu đề là câu kết luận, dòng đối tượng và đơn vị, nhãn số trực tiếp, một mà… | `bo/linhx-report/skills/hinh-du-lieu` |
| `hoi-ai` | Hỏi nhiều mô hình AI bộ câu hỏi ABC như khách thật và lưu nguyên văn câu trả lời (claude -p, agy -p, codex, Gemini API, OpenRouter, hoặc dán tay từ ChatGPT/Gemi… | `bo/linhx-brand-check/skills/hoi-ai` |
| `ip-scout` | Dùng khi chấm và xếp hạng IP (truyện, game, phim) để học cấu trúc làm world: lấy metadata từ Wikidata/Bangumi/AniList/Fandom, chấm 6 tiêu chí 1-5, viết bài học … | `bo/linhx-artradar/skills/ip-scout` |
| `khung-nghien-cuu` | Bước 1–3 của linhx-report. Làm rõ đề bài báo cáo, dựng khung phân tích (cây vấn đề MECE, giả thuyết, bảng yêu cầu dữ liệu P0/P1/P2), rồi nghiên cứu song song bằ… | `bo/linhx-report/skills/khung-nghien-cuu` |
| `kiem-chu-anh` | Kiểm chính tả chữ trong ảnh AI (ChatGPT, Nano Banana, Flow…) ngay sau khi tải về, nhất là tiếng Việt có dấu; sai thì sửa/gen lại. Dùng sau MỌI lượt tạo ảnh có c… | `le/kiem-chu-anh` |
| `kiem-tin-hieu` | Kiểm 5 lớp truth signal và mức sẵn sàng giao dịch với agent của một thương hiệu (robots cho bot AI, schema, llms.txt, nhất quán đa kênh, bên thứ ba, người đứng … | `bo/linhx-brand-check/skills/kiem-tin-hieu` |
| `lesson-slides` | Dùng khi cần kết xuất file slides.md của Slidev thành bộ ảnh PNG độ phân giải 1920x1080 theo từng bước click và sinh file segments.json đồng bộ từng khung hình … | `bo/linhx-course/skills/lesson-slides` |
| `loc` | Lọc bản ghi mới của kho minh hoạ ý tưởng: bỏ mục NoAI, tải ảnh tạm, đánh dấu bài đăng lại bằng dHash, đưa vào hàng chờ phân loại; dọn ảnh tạm sau khi xong. | `bo/linhx-kho-minh-hoa/skills/loc` |
| `loi-the-offer` | Bước 5, 6, 7, 9 của quy trình deck proposal - lợi thế của Linh lấy từ hồ sơ năng lực LINHX, tìm khoảng trống và thiết kế offer giải nỗi đau khách có mapping năn… | `bo/linhx-deck/skills/loi-the-offer` |
| `lps-ui` | Thiết kế và tự kiểm giao diện web theo LPS (design token, trạng thái, mobile-first, WCAG 2.2 AA, Core Web Vitals, heuristic Nielsen). Dùng khi làm hoặc sửa màn … | `le/lps-ui` |
| `minh-hoa-y` | Khi Linh cần hình minh hoạ cho một ý (bài viết, slide, post), dùng kho minh hoạ ý tưởng để đề xuất 3 cơ chế × 2 phong cách, viết ý hình cụ thể và prompt sẵn để … | `bo/linhx-kho-minh-hoa/skills/minh-hoa-y` |
| `nguon-radar` | Dùng trước mọi lần quét art/nhân vật/IP để kiểm nguồn có trong sổ nguồn, đọc luật robots, giới hạn tốc độ và điều khoản; thêm nguồn mới vào sổ. | `bo/linhx-artradar/skills/nguon-radar` |
| `onbrand-cham` | Chấm một thiết kế (PNG, JPG, PDF, PPTX, HTML) có bám brand guideline không, thang 100 điểm theo 5 mục màu, chữ, logo, hình/bố cục, nội dung, kèm chỗ sai và cách… | `bo/linhx-onbrand/skills/onbrand-cham` |
| `onbrand-nap` | Nạp một brand guideline (PDF, AI, PPTX, thư mục logo) thành cây thư mục chuẩn và brand.json để chấm onbrand. Dùng khi có guideline mới hoặc guideline đổi. | `bo/linhx-onbrand/skills/onbrand-nap` |
| `onbrand-thi` | Đo năng lực bám chuẩn design của nhiều người hoặc nhiều AI trên cùng một brand: ra 5 đề chuẩn, thu bài, chấm onbrand từng bài, xếp hạng và chỉ ra điểm yếu theo … | `bo/linhx-onbrand/skills/onbrand-thi` |
| `onbrand-thiet-ke` | Thiết kế ấn phẩm (social, story, banner, slide, poster) đúng ngôn ngữ thiết kế của một brand đã nạp, dùng logo vector, font, hoạ tiết, ảnh thật của brand, xuất … | `bo/linhx-onbrand/skills/onbrand-thiet-ke` |
| `phan-bien` | Hội đồng phản biện cho deck proposal - hai agent đọc ghost deck và deck như khách hàng khó tính và như partner tư vấn chiến lược, chấm theo rubric Nội dung, Mạc… | `bo/linhx-deck/skills/phan-bien` |
| `phan-loai` | Phân loại các hình trong hàng chờ của kho minh hoạ ý tưởng theo hai trục họ phong cách × cơ chế ý tưởng, viết "hình này nói gì", ghi thẻ ảnh hoặc đưa vào hàng c… | `bo/linhx-kho-minh-hoa/skills/phan-loai` |
| `phat-trien-nhan-vat` | Phát triển nhân vật ảo sau khi duyệt casting: tủ đồ thời trang, trang điểm, chi tiết cơ thể, danh sách biểu cảm, tối đa chi tiết và có tham chiếu cụ thể, ra Cha… | `bo/linhx-casting/skills/phat-trien-nhan-vat` |
| `proposal-brief` | Analyses a client brief for an event or activation proposal – extracts objectives, audience, constraints, insights and lists what the brief is missing. Use when… | `bo/proposal-studio/skills/proposal-brief` |
| `proposal-ideas` | Researches world event technology and proposes 4–6 scored activation ideas for a brief (including IFAGENT talking-character ideas where they fit), before the fu… | `bo/proposal-studio/skills/proposal-ideas` |
| `proposal-images` | Writes the image prompt pack for a proposal (ChatGPT Plus / Google Flow), swaps generated images into the project folder by filename and rebuilds the deck. Use … | `bo/proposal-studio/skills/proposal-images` |
| `proposal-studio` | Turns an event/activation brief into a complete, replaceable proposal package – brief analysis, world event-tech research, solution ideas (using IFAGENT tech wh… | `bo/proposal-studio/skills/proposal-studio` |
| `quet-link` | Dùng khi cần quét bài/hồ sơ nghệ thuật (Bored Panda, ArtStation, Behance, Reddit, Tumblr, Lofter…) để lấy metadata và link nghệ sĩ vào records.jsonl, không tải … | `bo/linhx-artradar/skills/quet-link` |
| `so-nguon` | Dùng trước mọi lần thu link cho kho minh hoạ ý tưởng: kiểm nguồn có trong sổ, thêm nguồn hoặc hoạ sĩ hạt giống mới, kiểm link hoạ sĩ. | `bo/linhx-kho-minh-hoa/skills/so-nguon` |
| `tach-kv` | Phân rã một key visual (KV) phẳng JPG/PNG thành các element độc lập (chữ, logo, ảnh, QR, nền) dạng PNG trong suốt + kv.json vị trí + PSD + SVG, để dùng lại cho … | `le/tach-kv` |
| `tai-tao` | Sinh ảnh mẫu cho từng thẻ phong cách trong kho minh hoạ ý tưởng bằng công thức {y_tuong} với 3 đề chuẩn, để xem nhanh và so sánh công bằng; ghi lỗi hay gặp. | `bo/linhx-kho-minh-hoa/skills/tai-tao` |
| `the-nghe-si` | Dùng khi biến records.jsonl đã quét thành thẻ nghệ sĩ có tag phong cách theo từ điển có kiểm soát và ghi chú Obsidian. | `bo/linhx-artradar/skills/the-nghe-si` |
| `the-nhan-vat` | Dùng khi dựng thư viện nhân vật tham khảo từ Bangumi/AniList (hoặc mô tả của Linh), viết lại phần hình ảnh và vai trò theo từ điển phong cách, xuất ghi chú Obsi… | `bo/linhx-artradar/skills/the-nhan-vat` |
| `the-phong-cach` | Gom các thẻ ảnh cùng họ trong kho minh hoạ ý tưởng thành thẻ phong cách có định nghĩa, dấu hiệu nhận diện, khi dùng, khi tránh và công thức prompt {y_tuong} khô… | `bo/linhx-kho-minh-hoa/skills/the-phong-cach` |
| `thiet-ke` | Workflow thiết kế đầu cuối cho một ấn phẩm (logo, poster, pano, social, KV) hoặc một landing page - đề bài, tham chiếu thật, moodboard, nhiều phương án, chấm mù… | `le/thiet-ke` |
| `thu-link` | Thu metadata và link (không tải ảnh) từ bộ sưu tập Instagram KHO-Y-TUONG của Linh, Pinterest board, Behance, Bluesky hoặc link Linh dán, ghi vào kho minh hoạ ý … | `bo/linhx-kho-minh-hoa/skills/thu-link` |
| `tim-mau-clone` | Bước 0 của linhx-report. Tìm cảm hứng và mẫu báo cáo đẹp (thư viện PDF của Linh, Envato Elements, Dribbble, Behance, Issuu, Pinterest, trang báo cáo của các hãn… | `bo/linhx-report/skills/tim-mau-clone` |
| `viet-bao-cao` | Bước 5–8 của linhx-report. Ghost report (mỗi trang một thông điệp, kiểu trang, ảnh mẫu), viết từng chương bằng cú pháp chương có khối hình/số lớn/trích dẫn/side… | `bo/linhx-report/skills/viet-bao-cao` |
| `vong-lap-slide` | Vòng lặp tự cải thiện cho slide (HTML Claude Slides/linhx-deck hoặc .pptx): đo trên bản render, người chấm tách thợ, xác minh lỗi, sửa cục bộ, hoàn tác khi tệ h… | `le/vong-lap-slide` |
| `web-thiet-ke` | Quy trình 7 bước thiết kế landing page hoặc màn hình app đẹp, đúng brand bằng Claude: đề bài, moodboard ảnh tham chiếu, hướng thị giác, ảnh ChatGPT làm đích nhì… | `le/web-thiet-ke` |
| `world-lore` | Dùng khi dựng lorebook (world info) cho một IP để học cấu trúc hoặc cho world gốc của Linh: tách địa danh, phe, hệ sức mạnh, luật thế giới, sinh vật, vật phẩm, … | `bo/linhx-artradar/skills/world-lore` |
| `xem-kho` | Dựng lại trang HTML tĩnh để lướt kho minh hoạ ý tưởng, lọc theo họ phong cách và cơ chế ý tưởng, chép công thức; chạy sau khi thêm hoặc sửa thẻ phong cách. | `bo/linhx-kho-minh-hoa/skills/xem-kho` |

## Tự kiểm, tự sửa, vòng lặp chất lượng

| Skill | Làm gì | Ở đâu |
|---|---|---|
| `agy-tu-chay` | Cho Antigravity (agy) tự lập kế hoạch và tự chạy trọn một việc theo phiếu, tự kiểm, tự chấm chéo bằng phiên mới, ghi báo cáo một trang cho Claude và Linh. Dùng … | `le/agy-tu-chay` |
| `architecture-patterns-and-design-rules` | Quy chuẩn kiến trúc & nguyên tắc thiết kế mã nguồn chuẩn cho React, Next.js, Node.js, NestJS theo Antigravity Global Architecture Patterns & Design Rules. Bao g… | `le/architecture-patterns-and-design-rules` |
| `audit` | Điều phối brand audit và social content audit: chọn nhóm cần chấm, giao agent chạy song song, gộp điểm sức khoẻ 0-100 và kế hoạch theo mức. Dùng khi chưa rõ cần… | `bo/linhx-audit/skills/audit` |
| `audit-social` | Social content audit từ file xuất bài đăng (Meta Business Suite, TikTok Studio, CSV tự gõ): nhịp, tương tác theo dạng bài, trụ cột, chất lượng bài, đúng giọng b… | `bo/linhx-audit/skills/audit-social` |
| `backend-security-audit` | Quy trình tự động rà soát an toàn mã nguồn Backend NestJS/Express theo chuẩn OWASP API Security Top 10 (2023), OWASP LLM Applications (2025) và ASVS v4.0.3 Leve… | `le/backend-security-audit` |
| `bien-tap` | Chuyển bản làm mượt sang plugin linhx-bien-tap (hồ sơ Vân Anh) để biên tập, rồi sửa theo phiếu. Dùng sau bước làm mượt nháp của Linh. | `bo/linhx-viet-giong-viet/skills/bien-tap` |
| `bien-tap-bai` | Biên tập một bài tiếng Việt như một biên tập viên người, qua sáu lượt soát tách ngữ cảnh (máy, sự thật, cấu trúc, ngôn ngữ, chấm từng câu, độc giả ảo), ra phiếu… | `bo/linhx-bien-tap/skills/bien-tap-bai` |
| `BM1_05_cham_chon_huong` | Bước 5 của Big Module 1 (LÀM MỚI HOÀN TOÀN): Tự chấm 3 phương án Outline A/B/C theo phản ứng của 3 Persona Neo + tiêu chí 'đạt khi' + độ dày bằng chứng + chống … | `le/bm1_05_cham_chon_huong` |
| `cham-khoang-trong` | B6 radar khoảng trống. Chấm và xếp hạng cụm nhu cầu theo điểm khoảng trống = cầu nguồn × chuyển giao được × (1 − độ phủ VN) × thời điểm, kèm lý do và rủi ro. Dù… | `bo/linhx-khoang-trong/skills/cham-khoang-trong` |
| `cham-nhanh` | Chấm nhanh mức "AI-ready" của một file dữ liệu (Excel/CSV khách hàng, nhân sự, nhà cung cấp…) theo 6 chiều và chỉ ra 3 lỗi lớn nhất, có tính lỗi riêng của dữ li… | `bo/linhx-du-lieu/skills/cham-nhanh` |
| `cham-tung-cau` | Lượt biên tập 4, hai giám khảo tách ngữ cảnh chấm từng câu một nhãn GIỮ, ỔN, SỬA, CẮT có mã lỗi; gộp bằng script và so ngưỡng giao bài. Dùng trong bien-tap-bai … | `bo/linhx-bien-tap/skills/cham-tung-cau` |
| `chuan-code` | Chuẩn viết code của LINHX theo 4 nguyên tắc Karpathy: nghĩ trước khi code, tối giản, sửa đúng chỗ, làm theo mục tiêu kiểm được. Dùng khi viết, sửa, review hoặc … | `bo/linhx-core/skills/chuan-code` |
| `de-xuat-phuong-an` | Viết đề xuất 3–4 phương án tách module, có khuyến nghị, rồi đi tiếp bằng sổ quyết định thay vì đứng chờ. Dùng khi Linh hỏi "cho tôi phương án", "đề xuất hướng đ… | `bo/linhx-core/skills/de-xuat-phuong-an` |
| `doc-gia-ao` | Lượt biên tập 5, hai hoặc ba độc giả Việt cụ thể đọc mù bài như người đọc thật và chỉ ra chỗ bỏ đọc, chỗ không hiểu, chỗ muốn cãi, chỗ nghe như Tây dịch, điều m… | `bo/linhx-bien-tap/skills/doc-gia-ao` |
| `e2e-3-rounds-harsh-reviewer` | - | `le/e2e-3-rounds-harsh-reviewer` |
| `frontend-security-audit` | Quy trình tự động rà soát an toàn mã nguồn Frontend Next.js/React theo tiêu chuẩn hiện đại (CWE-522, CWE-79, CWE-284, CWE-200). Cung cấp ma trận kiểm thử, bộ lệ… | `le/frontend-security-audit` |
| `gemini-lay-cham` | Lấy kết quả một nhiệm vụ Gemini Task về máy (zip, CSV, PDF, câu trả lời), bỏ trùng, giải nén, chấm bằng máy rồi chấm tay và cho điểm Argon. Dùng khi Linh nhắn "… | `bo/linhx-gemini-task/skills/gemini-lay-cham` |
| `hieu-chuan` | Kiểm giám khảo chấm từng câu có phân biệt được bản đã sửa của người thật với bản máy hay không, trên một cặp bài mẫu, trước khi tin điểm của họ. Dùng khi đổi mô… | `bo/linhx-bien-tap/skills/hieu-chuan` |
| `hoc-luat-bien-tap` | Rút luật biên tập từ bản sửa thật của một biên tập viên (Vân Anh, Linh) - Word track changes hoặc cặp bản trước/sau - thành hồ sơ LUAT.md có bằng chứng, rồi kiể… | `bo/linhx-bien-tap/skills/hoc-tu-ban-sua` |
| `ke-hoach-lab` | Lập và giữ kế hoạch bằng file cho một lab LINHX (PLAN.md, LOG.md, refs/) để không lạc mục tiêu qua nhiều phiên. Dùng khi mở lab mới, khi việc có từ 3 bước trở l… | `bo/linhx-core/skills/ke-hoach-lab` |
| `linhx` | Lệnh quản trị plugin linhx-core (xem luật đang bơm, kiểm skill, cài sang Antigravity). Dùng khi Linh gõ /linhx, hỏi "luật LAB đang bơm gì", "cài skill LINHX cho… | `bo/linhx-core/skills/linhx` |
| `linhx-chuan` | Lõi chất lượng LINHX. Đọc trước mọi việc tạo sản phẩm cho Linh hoặc khách (chiến lược, giáo trình, slide, báo cáo, thiết kế, ảnh, nghiên cứu). Có 14 luật, thang… | `le/linhx-chuan` |
| `linhx-tu-chay` | Cho Claude và Antigravity tự đi từ ý định 4 câu tới sản phẩm chạy được - khám phá, PRD, features.json khoá, thợ làm từng feature, cổng kiểm độc lập ngoài tay th… | `le/linhx-tu-chay` |
| `lps-bao-mat` | Mô hình hoá mối đe doạ, quét bảo mật tự động và tự pentest một ứng dụng web theo LPS (OWASP ASVS, Top 10, WSTG, LLM Top 10). Dùng khi tính năng chạm đăng nhập, … | `le/lps-bao-mat` |
| `lps-khoi-tao` | Khởi tạo một dự án webapp/nền tảng mới (hoặc đưa dự án có sẵn) vào chuẩn LINHX Platform Standard (LPS). Dùng khi Linh nói "dự án mới", "khởi tạo theo LPS", "áp … | `le/lps-khoi-tao` |
| `lps-llm` | Thiết kế, viết, kiểm thử và red team một tính năng gọi LLM (chatbot, tóm tắt, trích xuất, phân loại, RAG, agent có tool) theo chuẩn LPS-AI. Dùng khi thêm hoặc s… | `le/lps-llm` |
| `lps-release` | Kiểm cổng phát hành (release gate) trước khi đưa bản mới lên production theo LPS. Dùng khi Linh nói "phát hành", "release", "deploy production", "lên bản mới". | `le/lps-release` |
| `lps-review` | Review/phản biện độc lập một thay đổi (diff, PR, SPEC) với ngữ cảnh sạch, ưu tiên mô hình hoặc công cụ khác với bên viết code. Dùng trước khi merge, khi Linh nó… | `le/lps-review` |
| `lps-spec` | Viết SPEC có tiêu chí chấp nhận kiểm được trước khi code một tính năng. Dùng khi bắt đầu tính năng mới, khi yêu cầu còn mơ hồ, hoặc khi Linh nói "lên spec", "th… | `le/lps-spec` |
| `lps-tdd` | Thực hiện một bước trong SPEC theo vòng test trước (đỏ → xanh → dọn). Dùng khi code logic nghiệp vụ, API, hoặc sửa bug ("sửa lỗi", "implement", "làm bước N của … | `le/lps-tdd` |
| `lps-tu-sua` | Vòng tự kiểm và tự sửa sau mỗi thay đổi code. Dùng sau khi sửa file, trước khi báo "xong", khi CI đỏ, hoặc khi Linh nói "kiểm lại", "chạy cho xanh", "fix CI". | `le/lps-tu-sua` |
| `lps-user-test` | Chuẩn bị, chạy và tổng hợp một vòng thử nghiệm người dùng (usability test) 5 người. Dùng khi tính năng lớn sắp phát hành, khi Linh nói "thử với người dùng", "te… | `le/lps-user-test` |
| `luong-hoa` | Lượng hoá bốn lớp kiểm trong đầu biên tập viên (hiểu, tin, ý, giọng) thành con số, bằng trích xuất lặp nhiều lượt đến khi ổn định rồi so với dải của bài Linh đã… | `bo/linhx-bien-tap/skills/luong-hoa` |
| `soat-cau-truc` | Lượt biên tập 2, soát bài ở mức đoạn - mạch, lặp ý, đoạn thừa, mở và kết, nhịp, độ dài theo đơn đặt hàng - và chấm từng đoạn GIỮ, SỬA, CẮT, VIẾT LẠI. Dùng trong… | `bo/linhx-bien-tap/skills/soat-cau-truc` |
| `soat-ngon-ngu` | Lượt biên tập 3, soát câu chữ theo hai prompt gốc của Linh - Tổng biên tập CQS 6 trụ cột và máy dò văn AI APS - cộng luật học từ bản sửa của biên tập viên; ra đ… | `bo/linhx-bien-tap/skills/soat-ngon-ngu` |
| `soat-su-that` | Lượt biên tập 1, đối chiếu từng câu có số liệu, tên, sự kiện, luật với kho nguồn của bài; bắt chỗ nói nhiều hơn nguồn, bịa, sai thuật ngữ pháp lý. Dùng trong bi… | `bo/linhx-bien-tap/skills/soat-su-that` |
| `thoi-quen-ai` | Kiểm thử một nhận xét về thói quen viết của AI (cụm mở đầu, cấu trúc câu, từ đặc trưng, gạch dài, định dạng...) trên nhiều model với số lượng lớn, ra thống kê. … | `bo/linhx-thoi-quen-ai/skills/thoi-quen-ai` |
| `viet-chuan` | Tra cứu và chuẩn hoá từng giá trị dữ liệu Việt (SĐT đầu số cũ 11 số, CCCD/CMND, MST, ngày, tên không dấu, Unicode NFD, lỗi mã, bảng mã TCVN3/VNI, địa chỉ trước/… | `bo/linhx-du-lieu/skills/viet-chuan` |
| `xac-minh-truoc-khi-bao-xong` | Cổng kiểm trước khi nói "xong", "chạy được", "đã sửa", "đã gửi file": phải có bằng chứng mới từ lượt này. Dùng khi sắp báo kết quả cho Linh, đánh dấu pha [x] tr… | `bo/linhx-core/skills/xac-minh-truoc-khi-bao-xong` |

## Vận hành, điều phối, giao việc

| Skill | Làm gì | Ở đâu |
|---|---|---|
| `agent-truong` | Agent trưởng điều phối đội subagent nhỏ: chia việc lớn thành đầu việc hẹp, giao cho thợ (tho-tim-nguon, tho-doc-nguon, tho-kiem-chung, tho-viet) chạy song song,… | `le/agent-truong` |
| `chien-luoc` | Xây chiến lược theo chuẩn cao kiểu Trân Bảo / Kim Gia Bảo Gift / BTMH IPO - nghiên cứu tới đâu lưu tới đó, đào sâu khách hàng mục tiêu và định vị đối thủ, tìm k… | `le/chien-luoc` |
| `chuyen-skill` | Chuyển một skill hoặc plugin Claude Code (SKILL.md, commands, agents) sang GitHub Copilot, Gemini CLI và Antigravity, kèm bảng cảnh báo chỗ chỉ Claude hiểu. Dùn… | `le/chuyen-skill` |
| `dong-thread` | Đóng một thread Claude Code đang dở: viết file bàn giao gọn để Antigravity (hoặc phiên mới) làm tiếp. Dùng khi Linh nói 'đóng thread', 'bàn giao', 'chuyển sang … | `le/dong-thread` |
| `gemini-gui` | Gửi một đề có sẵn vào Gemini Task trên tài khoản Ultra Art Urah (gemini.google.com/u/1, Nhiệm vụ, Argon) bằng Chrome của Linh, rồi ghi link vào sổ. Dùng khi Lin… | `bo/linhx-gemini-task/skills/gemini-gui` |
| `gemini-skill` | Đóng gói một Skill cho Gemini (Gemini không có plugin; Skill là SKILL.md ở gốc + script, chỉ file chữ, ≤100 MB, script không gọi mạng, gọi bằng @tên) và cài Ski… | `bo/linhx-gemini-task/skills/gemini-skill` |
| `gemini-task` | Giao việc cho Gemini Task (Gemini Ultra, chế độ Nhiệm vụ, model Argon) thay vì tự làm bằng token Claude. Dùng mỗi khi việc là nghiên cứu web diện rộng, gom dữ l… | `bo/linhx-gemini-task/skills/gemini-task` |
| `ho-so-tai-tro` | Khung kiến thức viết và tự phản biện hồ sơ xin tài trợ (concept note, full proposal, mục tiêu, khung logic, ngân sách, tác động), theo tiêu chí chấm của nhà tài… | `bo/linhx-linh-vuc/skills/ho-so-tai-tro` |
| `lab-moi` | Mở một thí nghiệm LAB mới hoặc gắn cuộc trò chuyện vào LAB hiện có. Tự động kích hoạt ở đầu mỗi cuộc trò chuyện trong D:\LINHX\LAB (Session Gate) hoặc khi Linh … | `le/lab-moi` |
| `linhx-4d` | Giao việc theo quy chuẩn 4D (Double Diamond x 100 Tasks x phòng Tam Quốc) cho mọi dự án - giáo trình, phần mềm OPC, ứng dụng, slide, kế hoạch. Dùng khi Linh nói… | `le/linhx-4d` |
| `linhx-be-phong` | Lập kế hoạch launch một OPC mới trên bệ phóng chung của LINHX (15 khâu, module dùng lại từ các lab) và so KPI giữa các OPC. Dùng khi Linh nói "launch OPC mới", … | `le/linhx-be-phong` |
| `linhx-crawler` | Crawl web content via LinhX Lab's self-hosted multi-tier FastAPI server. Supports waterfall fallback (httpx → Crawl4AI → Firecrawl → Playwright) for maximum rel… | `le/linhx-crawler` |
| `linhx-nhiem-vu` | Chuẩn làm nhiệm vụ dài cho LINHX trong Gemini Task: luật nguồn, cấu trúc thư mục, checkpoint zip, tự kiểm bằng script, nối lượt. Dùng khi đề gọi @linhx-nhiem-vu… | `bo/linhx-gemini-task/gemini-skills/linhx-nhiem-vu` |
| `mm-chon` | Chọn 0–3 mental model (thẻ Naval, Munger, Farnam Street hoặc thẻ riêng của Linh) cho một tình huống hay câu hỏi cụ thể rồi chạy câu hỏi kích hoạt của từng thẻ. … | `bo/linhx-tu-duy/skills/mm-chon` |
| `mm-ngay` | Bốc thẻ mental model của ngày cho Linh (ưu tiên thẻ có quyết định tới hạn, rồi thẻ lâu chưa dùng), và tối ghi một câu thẻ đó xuất hiện ở đâu; cũng dùng để thêm … | `bo/linhx-tu-duy/skills/mm-ngay` |
| `mm-quyet` | Ghi một quyết định vào nhật ký quyết định của Linh (chỉ thêm, không sửa) kèm các thẻ mental model đã dùng, độ chắc, điều làm đổi ý và ngày chấm; hoặc chấm một q… | `bo/linhx-tu-duy/skills/mm-quyet` |
| `mm-tuan` | Buổi chấm tuần cho bộ mental model của Linh: liệt kê quyết định tới hạn để chấm trước, thẻ đã dùng, độ phủ 30 ngày, thẻ bị bỏ quên, và hiệu chỉnh độ chắc so với… | `bo/linhx-tu-duy/skills/mm-tuan` |
| `morning` | Render the user's morning brief as a styled HTML artifact, or set it up as a recurring weekday task. Use only when the user explicitly asks to run, see, or set … | `le/morning` |
| `nghien-cuu-thi-truong` | Viết báo cáo nghiên cứu thị trường truy được nguồn, ước tính quy mô TAM/SAM/SOM theo kịch bản, phân tích đối thủ, dự báo có độ nhạy. Dùng khi Linh hỏi quy mô th… | `bo/linhx-linh-vuc/skills/nghien-cuu-thi-truong` |
| `office` | Mở, tắt, xem trạng thái hoặc chạy demo văn phòng ảo LINHX (2D pixel / 3D) hiển thị Claude Code, subagent và worker Antigravity đang làm gì; cài hook cho Antigra… | `bo/linhx-office/skills/office` |
| `pipeline` | Tổ chức và chạy một dự án nhiều bước theo bảng mục × tầng (slide, trang, chương, shot, milestone). Dùng khi Linh nói "làm lại slide 4", "chạy lại ảnh", "cái gì … | `bo/linhx-pipeline/skills/pipeline` |
| `proto-moi` | Đưa một EXP đã chạy được ở LAB lên PROTOTYPE khi Linh nói "lên prototype: LAB…" hoặc đồng ý sau khi chấm cổng. | `le/proto-moi` |
| `quan-tri-agy` | Claude làm quản trị dự án tổng cho agy với ít token nhất - nhận lệnh của Linh, viết LENH.md, khởi tạo kế hoạch, giao agy chạy trên máy công ty, rồi chỉ đọc BAO-… | `le/quan-tri-agy` |
| `quy-trinh-nghiep-vu` | Soạn hoặc chuẩn hoá quy trình nghiệp vụ ngân hàng (SOP) từ mô tả thô, ghi chú họp hoặc văn bản cũ, theo khung 10 mục có RACI, lưu đồ, điểm kiểm soát, SLA, rồi t… | `bo/linhx-bank-ops/skills/quy-trinh-nghiep-vu` |
| `ra-soat-kho` | Rà soát kho second brain khi Linh nói "rà soát kho": lọc INBOX, liệt kê LAB/PROTOTYPE/PRJ/EDU cần chú ý, làm đầu vào cho Weekly Planning của LINHX plan daily. K… | `le/ra-soat-kho` |
| `thu-ky` | Bật, mở, tắt hoặc cấu hình thư ký ảo LINHX (nhân vật video nói chuyện bằng giọng, kể tình hình các dự án và giao việc cho Claude Code ở từng thư mục). Dùng khi … | `bo/linhx-thu-ky/skills/thu-ky` |
| `tong-quan-tai-lieu` | Tổng quan tài liệu có phương pháp (tìm có ghi lại, sàng lọc, tổng hợp theo chủ đề, kiểm trích dẫn DOI) cho bài báo, nghiên cứu học thuật và báo cáo chính sách. … | `bo/linhx-linh-vuc/skills/tong-quan-tai-lieu` |
| `tra-cuu-luat` | Tra cứu văn bản pháp luật Việt Nam mới nhất về một chủ đề (mặc định luật đất đai, bất động sản) bằng Chrome của Linh, rồi ghi chú tiếng Việt có link nguồn, ngày… | `le/tra-cuu-luat` |
| `viet-overview` | Đóng một thí nghiệm LAB khi Linh nói "viết overview": hoàn thiện OVERVIEW.md, cập nhật INDEX, và chấm cổng PROTOTYPE nếu EXP chạy được. | `le/viet-overview` |

## Video, phim, hoạt hình

| Skill | Làm gì | Ở đâu |
|---|---|---|
| `Bespoke Video Generator` | Skill sinh video chuyên nghiệp bằng Veo API (Google). Tích hợp Forensic Analyzer để phân tích starting frame/ref, đánh giá chất lượng. Hỗ trợ text-to-video, ima… | `le/bespoke-video-generator` |
| `flow-canh-tron-khung` | Dựng cảnh hoạt hình nét vẽ bằng Flow/Veo trọn khung (nhân vật cùng object, chữ trong một ảnh), code chỉ chọn khung, đẩy máy, phụ đề, nhạc. Dùng khi Linh nói "ph… | `le/flow-canh-tron-khung` |
| `hybrid-canh-nhan-vat` | Dựng cảnh hoạt hình kiểu hybrid: Flow/Veo chỉ làm chuyển động riêng của nhân vật nét vẽ trên nền trắng, code lo object, chữ, máy, âm thanh và canh nhịp theo tho… | `le/hybrid-canh-nhan-vat` |
| `le-bich-hoat-hinh` | Vẽ nhân vật Lê Bích bụng phệ bằng code từ bộ rời gốc (PSD của tác giả) để làm trang truyện, sticker động, clip hoạt hình. Dùng khi được nhờ vẽ, làm truyện, stic… | `le/le-bich-hoat-hinh` |
| `le-bich-studio` | Nền tảng tạo nội dung và hoạt hình Lê Bích từ kho PSD/PNG chính chủ (4.000+ mảnh nhân vật, 15+ bộ trang phục thay được, đạo cụ, bóng thoại vẽ tay, hiệu ứng FX).… | `bo/linhx-le-bich-studio/skills/le-bich-studio` |
| `phim-code` | Dựng phim ngắn bằng code (canvas/WebGL, HTML/GSAP, React) với một quy trình chung và nhiều style để chọn, máy dựng là Lemo-Opuscar, HyperFrames hoặc Remotion, g… | `bo/linhx-phim-code/skills/phim-code` |
| `sd-bo-tham-chieu` | Quy trình làm ảnh bằng ChatGPT Plus cho một series: đoán khán giả (TA), chuẩn bị brand và logo, tìm 2–3 art style trên Pinterest, chọn style, tạo bộ ảnh tham ch… | `le/sd-bo-tham-chieu` |
| `sd-de-xuat` | Bước 0b Flow Pack. Từ bản nghiên cứu, đưa 3 hướng phim khác hẳn nhau kèm ước tính credit và một đoạn mẫu 8 giây cho mỗi hướng, để Linh chọn hoặc trộn. Dùng sau … | `le/sd-de-xuat` |
| `sd-dung` | Bước 7 Flow Pack. Ghép các bản giữ của một tập thành bản dựng nháp, chuẩn bị phụ đề và ghi chú hậu kỳ; tính credit trên mỗi giây và tỉ lệ giữ. Dùng khi mọi đoạn… | `le/sd-dung` |
| `sd-flow-pack` | Bước 5 Flow Pack. Xuất phiếu render cho Google Flow từ JSON tập đã ĐẠT kiem_nhip, kèm bảng duyệt credit; Linh dán tay vào Flow. Dùng khi tập sẵn sàng render. | `le/sd-flow-pack` |
| `sd-kich-ban` | Bước 2 Flow Pack. Viết kịch bản một tập short drama 60–90 giây theo nhịp hook, điểm sướng mỗi 15 giây, cliffhanger, với thoại vừa clip Veo 8 giây. Dùng sau khi … | `le/sd-kich-ban` |
| `sd-nghien-cuu` | Bước 0 Flow Pack. Nghiên cứu có nguồn trước khi viết series hoặc kịch bản (thể loại, khán giả, phim mẫu, nhịp, phong cách hình). Dùng khi bắt đầu một series hoặ… | `le/sd-nghien-cuu` |
| `sd-nhan-take` | Bước 6 Flow Pack. Nhận clip Linh tải từ Flow về, khớp với phiếu, ghi sổ credit, xem contact sheet, chọn bản giữ, cảnh báo ngân sách. Dùng mỗi khi Linh báo đã re… | `le/sd-nhan-take` |
| `sd-phan-tich-mau` | Phân tích một video mẫu (short drama, quảng cáo, trailer) theo 5 khía cạnh để lấy nhịp, khung hình, chuyển động máy cho tập của mình mà không sao chép. Dùng khi… | `le/sd-phan-tich-mau` |
| `sd-series` | Bước 1 Flow Pack. Từ một ý tưởng, viết series bible cho short drama dọc (logline, nhân vật, thế giới, arc nhiều tập, kiểu hook cuối tập). Dùng khi Linh mở một s… | `le/sd-series` |
| `sd-storyboard` | Bước 4 Flow Pack. Chuyển kịch bản thành các đoạn Veo 4/6/8 giây có nhiều shot theo mốc thời gian, chọn chế độ Flow và model cho từng đoạn, rồi chạy kiem_nhip.py… | `le/sd-storyboard` |
| `sd-tai-san` | Bước 3 Flow Pack. Lập thư viện tài sản cho một tập: đoạn khoá nhân vật và style bằng tiếng Anh, prompt ảnh neo nhân vật, ảnh bối cảnh không người, prompt keyfra… | `le/sd-tai-san` |

## Viết, biên tập, nội dung

| Skill | Làm gì | Ở đâu |
|---|---|---|
| `BM1_01_phan_tich_de_bai` | Bước 1 của Big Module 1: Đọc kỹ, phân tích đề bài, xác định hạt giống ý tưởng (Seed Input) và mở rộng bối cảnh bằng 11 câu hỏi sâu (3 câu ưu tiên). Gắn từ LAB02… | `le/bm1_01_phan_tich_de_bai` |
| `BM1_02_persona_neo` | Bước 2 của Big Module 1 (GỘP MỚI): Nghiên cứu người nhận, xác định khoảng trống độc giả (LAB029), lọc nhân khẩu học phân tầng Việt Nam (LAB048) và đắp khung tâm… | `le/bm1_02_persona_neo` |
| `BM1_03_tim_tham_chieu` | Bước 3 của Big Module 1: Tìm tham chiếu, học cách người khác làm và lập sổ nguồn bằng chứng (tối thiểu 15 nguồn cho bài viết/report). Gắn từ LAB025 deep-researc… | `le/bm1_03_tim_tham_chieu` |
| `BM1_04_outline_thu_persona` | Bước 4 của Big Module 1 (LÀM MỚI PHẦN THỬ PERSONA): Rút 30 insights và dựng 3 phương án Outline A/B/C khác biệt (gắn LAB025 content-synthesizer), sau đó đưa cả … | `le/bm1_04_outline_thu_persona` |
| `BM1_06_trien_khai_draft1` | Bước 6 của Big Module 1: Triển khai từng phần theo Outline đã chốt ở Bước 5, thiếu thì nghiên cứu thêm, lưu Draft 1. Tự động điều phối theo loại nội dung: Bài v… | `le/bm1_06_trien_khai_draft1` |
| `BM1_07_danh_gia_draft1` | Bước 7 của Big Module 1: Đánh giá Draft 1 bằng bộ công cụ định lượng và phản biện tách ngữ cảnh. Gắn từ LAB049 lượt 0 (cham_cau.py, kiem_van_dich.py, kiem_van.p… | `le/bm1_07_danh_gia_draft1` |
| `BM1_08_viet_lai_giong_tac_gia` | Bước 8 của Big Module 1: Viết lại theo giọng tác giả, cân bằng giữa nhu cầu độc giả (Persona Neo) và hồ sơ giọng (Linh / Vân Anh / Giảng viên / Báo cáo). Gắn từ… | `le/bm1_08_viet_lai_giong_tac_gia` |
| `BM1_09_bien_tap_3_vong` | Bước 9 của Big Module 1: Duyệt, biên tập qua 6 lượt tách ngữ cảnh (máy, sự thật, cấu trúc, ngôn ngữ, chấm từng câu, độc giả ảo), sửa tối đa 3 vòng và lưu kinh n… | `le/bm1_09_bien_tap_3_vong` |
| `BM2_M1_chu_trinh_template` | Big Module 2 - Chu trình Template dạng chung (LÀM MỚI theo mẫu LAB043 v2): Phân tích yêu cầu -> Tham chiếu & nạp luật Onbrand -> Dựng 2-3 phương án thiết kế -> … | `le/bm2_m1_chu_trinh_template` |
| `BM2_M2_media_hoa` | Big Module 2 - Điều phối Media hoá theo từng loại nội dung: Ảnh minh hoạ + DOCX (Bài viết), Biểu đồ SVG + Báo cáo HTML/PDF (Report mẫu), Slidev slides.md + Deck… | `le/bm2_m2_media_hoa` |
| `cafebiz-radar` | Phân tích tin công nghệ cho mảng công nghệ CafeBiz theo quy chuẩn News Listening (mã trend T01–T13, nước và hướng lan, khoảng trống VN, độ hút, 6 chỉ số H M V G… | `le/cafebiz-radar` |
| `chuyen-kenh` | Đưa bài của Linh về đúng khuôn từng kênh (Dân trí Tâm điểm, Bloomberg Businessweek VN, VnExpress Góc nhìn, CafeBiz AI4BIZ, Facebook, Substack, LinkedIn): tên ký… | `bo/linhx-viet-bai/skills/chuyen-kenh` |
| `co-hoi-kenh` | B7 radar khoảng trống. Với cụm Linh chọn, viết kế hoạch chiếm topic ở Việt Nam - định vị, nền tảng, nên nói gì cho độc giả Việt, 10 tít đầu, nhịp đăng, cách kiể… | `bo/linhx-khoang-trong/skills/co-hoi-kenh` |
| `content-synthesizer` | Skill tổng hợp và chọn lọc nội dung theo persona tác giả. Trigger khi chạy bước 5-6 của pipeline hoặc khi cần nén dữ liệu nghiên cứu thành insights có chọn lọc.… | `bo/linhx-viet-bai/skills/content-synthesizer` |
| `critic-loop-writer` | Skill viết và cải thiện bài viết qua vòng lặp Writer-Critic 2 giai đoạn. Trigger khi chạy bước 7-8-9 của pipeline hoặc khi cần viết/rewrite một bài dựa trên cur… | `bo/linhx-viet-bai/skills/critic-loop-writer` |
| `deep-researcher` | Skill nghiên cứu chuyên sâu cho bài viết. Trigger khi chạy bước 3-4 của pipeline hoặc khi cần tìm kiếm dữ liệu, số liệu, trích dẫn triết học cho một chủ đề. Tạo… | `bo/linhx-viet-bai/skills/deep-researcher` |
| `gemini-reviewer` | Module duyệt bài độc lập bằng Gemini CLI. 2-stage pipeline: AI Detector → Editorial QA. Antigravity gọi trực tiếp gemini CLI qua run_command. Fallback bằng Pyth… | `bo/linhx-viet-bai/skills/gemini-reviewer` |
| `giai-ma-hai` | Mổ một content hài viral (clip, meme, câu trend, status) xem vì sao buồn cười và vì sao lan, gom nhiều mẫu thành khuôn tái dùng, xuất thủ pháp chữ cho LAB087 vé… | `bo/linhx-giai-ma-hai/skills/giai-ma-hai` |
| `giong-linh` | Sổ tay giọng văn của Linh (Lê Bích / Đinh Trần Tuấn Linh), 11 nước đi có bằng chứng từ bài đã in và mốc số đo. Dùng khi cần viết, sửa, nhận xét một đoạn "cho gi… | `bo/linhx-viet-bai/skills/giong-linh` |
| `hien-tuong` | B1 radar khoảng trống. Quét top bài, top tác giả, top kênh trên Substack, Medium, kênh quan điểm (LinkedIn, X, Threads, Facebook), podcast, YouTube, cả quốc tế … | `bo/linhx-khoang-trong/skills/hien-tuong` |
| `hoc-tu-ban-sua` | So bản nháp AI với bản Linh sửa xong để rút luật giọng mới, ghi sổ học, chỉ đưa vào sổ tay giọng khi một cách sửa lặp lại từ 3 lần. Dùng khi Linh gửi lại bài đã… | `bo/linhx-viet-bai/skills/hoc-tu-ban-sua` |
| `idea-seeder` | Skill gieo mầm ý tưởng bài viết. Trigger khi user nhập một ý tưởng thô (seed idea) hoặc khi chạy bước 1-2 của pipeline viết bài. Tạo 01_Seed_Input.json và 02_Co… | `bo/linhx-viet-bai/skills/idea-seeder` |
| `linhx-toan-van` | Lấy toàn văn bài (Medium, Substack, web) theo danh sách URL bằng extension LINHX_CRAWLER trong Chrome đã đăng nhập của Linh, 0 token; tự bật server, lưu mỗi bài… | `le/linhx-toan-van` |
| `new-article` | Viết bài mới theo quy trình LinhX Write 9 bước của Linh (FLOW v FM): gieo ý → 11 câu hỏi Deep Inquiry → nghiên cứu → 30 tứ → 3 phương án A/B/C → viết → phản biệ… | `bo/linhx-viet-bai/skills/new-article` |
| `nguoi-thang` | B3 radar khoảng trống. Với mỗi cụm nhu cầu, tìm 3 đến 5 kênh, tác giả đang thắng và chưng cất vì sao họ thắng theo 3 tầng (nhận thức, chiến lược, nội dung). Dùn… | `bo/linhx-khoang-trong/skills/nguoi-thang` |
| `nhu-cau-doc-gia` | B2 radar khoảng trống. Từ dữ liệu hiện tượng, tính chỉ số cầu/cung, bài vượt trung vị, bài của tác giả nhỏ mà nổ, rồi gom thành cụm NHU CẦU độc giả (không phải … | `bo/linhx-khoang-trong/skills/nhu-cau-doc-gia` |
| `quy-mo-thi-truong` | B4 radar khoảng trống. Ước quy mô thị trường của mỗi cụm nhu cầu ở nguồn (tổng người theo, số kênh trả phí, tăng trưởng 4 tuần) và tính điểm cầu nguồn. Dùng sau… | `bo/linhx-khoang-trong/skills/quy-mo-thi-truong` |
| `radar-khoang-trong` | Chạy trọn radar khoảng trống độc giả 7 bước (hiện tượng → nhu cầu → ai thắng → quy mô → soi Việt Nam → khoảng trống → cơ hội kênh). Dùng khi Linh nói "tìm khoản… | `bo/linhx-khoang-trong/skills/radar-khoang-trong` |
| `resume-article` | Tiếp tục viết bài dở dang từ checkpoint. Hỗ trợ --variant flag để chạy 1 variant cụ thể (dùng cho parallel execution). | `bo/linhx-viet-bai/skills/resume-article` |
| `review-article` | Chạy lại vòng Critic Loop 2-stage (AI Detector + Editorial QA) trên bài viết đã có. Hỗ trợ chọn variant cụ thể hoặc review toàn bộ. | `bo/linhx-viet-bai/skills/review-article` |
| `soat-giong` | Soát bài nháp tiếng Việt theo giọng Linh: chạy script kiem_van.py (dấu hiệu AP-01..AP-20, so mốc giọng, điểm 0-100) rồi đọc 3 lượt độc lập và sửa tối đa 2 vòng.… | `bo/linhx-viet-bai/skills/soat-giong` |
| `soi-viet-nam` | B5 radar khoảng trống. Mang từng cụm nhu cầu về Việt Nam, xếp mức còn trống, mỏng hay đã có người chiếm trên từng nền tảng VN (Facebook, YouTube, TikTok, Substa… | `bo/linhx-khoang-trong/skills/soi-viet-nam` |
| `time-tracker` | Skill đo thời gian thực thi pipeline bằng cách đọc file timestamps. Trigger khi cần tạo timelog cho một project, hoặc khi chạy /resume-article cần biết bước cuố… | `bo/linhx-viet-bai/skills/time-tracker` |
| `viet-bai` | Quy trình viết bài chuẩn cho Linh (Lê Bích / Đinh Trần Tuấn Linh), từ đơn hàng đến bản giao, 7 trạm, không bịa chuyện. Dùng khi Linh nhờ viết bài báo, op-ed, tả… | `bo/linhx-viet-bai/skills/viet-bai` |
| `viet-bai-du-thi` | Cùng Linh viết bài dự thi (tiểu luận, tản văn, bài báo, hồ sơ đề cử, kịch bản video) đúng thể lệ, giọng Linh, rồi tự phản biện theo tiêu chí chấm. Dùng sau khi … | `bo/linhx-cuoc-thi/skills/viet-bai-du-thi` |
| `viet-bai-giong-viet` | Viết bài tiếng Việt cùng Linh theo luồng của biên tập viên Vân Anh - máy tìm ý và dữ liệu, Linh viết nháp gạch đầu dòng, máy chỉ làm mượt từng ý của Linh rồi gử… | `bo/linhx-viet-giong-viet/skills/viet-bai-giong-viet` |
| `y-tuong-bai` | Tìm tứ cho bài của Linh bằng vòng lặp ý tưởng tự tối ưu LAB024 (gieo 30 ý, khán giả ảo và giám khảo nghề chấm, giữ bản thắng, rút bài học), rồi đưa hướng thắng … | `bo/linhx-viet-bai/skills/y-tuong-bai` |

## Marketing, cộng đồng, kênh

| Skill | Làm gì | Ở đâu |
|---|---|---|
| `ban-dang` | Mở bàn đăng cho Linh: mọi bài, câu bình luận, câu trả lời và bài học của một hoặc nhiều persona đã soạn sẵn, Linh chỉ bấm Đăng, sửa hoặc Bỏ. Dùng khi Linh muốn … | `bo/linhx-kenh-ao/skills/ban-dang` |
| `btmh-monthly-retail-intelligence` | - | `le/btmh-monthly-retail-intelligence` |
| `cau-hoi-thanh-noi-dung` | Vòng nhỏ của khung: gom câu hỏi lặp lại trong cộng đồng 14 ngày qua thành 3 đề bài nội dung trụ cho tuần sau (bài LinkedIn/Facebook, bản tin, buổi Zoom). Dùng k… | `bo/linhx-nuoi-cong-dong/skills/cau-hoi-thanh-noi-dung` |
| `chan-doan-giai-doan` | Chẩn đoán một cộng đồng hoặc một người làm content đang ở tầng nào của chuỗi content → cộng đồng → bán (khung 5 tầng – 2 vòng) và giai đoạn 0→100 / 100→1.000 / … | `bo/linhx-nuoi-cong-dong/skills/chan-doan-giai-doan` |
| `chao-don-gan-tag` | Soạn lời chào người mới theo nguồn vào (lớp nào, workshop, giới thiệu), kèm một câu hỏi chia nhánh để gắn tag đầu tiên, và các tin SOP theo mốc D+1/3/7/14/30/90… | `bo/linhx-nuoi-cong-dong/skills/chao-don-gan-tag` |
| `de-xuat-tuan` | Biến danh sách đề xuất tuần (tín hiệu mua, champion sang sales, đã giúp người, sắp lên cấp, quay lại, im lặng) thành việc cụ thể và tin nháp cho Linh/SO. Dùng s… | `bo/linhx-nuoi-cong-dong/skills/de-xuat-tuan` |
| `duyet-dang` | Đưa bài cho Linh duyệt (nhận, sửa, góp ý, bỏ), rút luật viết từ lần sửa, và đăng qua cổng. Dùng khi có bài chờ duyệt hoặc tới giờ đăng. | `bo/linhx-kenh-ao/skills/duyet-dang` |
| `enterprise-imc-campaign-creator` | - | `le/enterprise-imc-campaign-creator` |
| `hoc-ngay` | Vòng tự học cuối mỗi ngày của kênh: tính lại hậu nghiệm từ số liệu, bàn đăng, quan hệ và cổng; tự áp thay đổi nhỏ có trần; rút luật viết từ lần Linh sửa để Linh… | `bo/linhx-kenh-ao/skills/hoc-ngay` |
| `hoc-tuan` | Vòng học hằng tuần: kéo số liệu, chạy retro, viết giả thuyết có kiểm cỡ mẫu, đề luật viết và điều chỉnh. Dùng Chủ nhật hoặc khi Linh hỏi "tuần này học được gì". | `bo/linhx-kenh-ao/skills/hoc-tuan` |
| `hop-thu` | Kéo bình luận và tin nhắn, phân loại xanh/vàng/đỏ, soạn trả lời đúng giọng nhân vật, gửi qua cổng, cập nhật điểm fan. Dùng cho bước hop_thu. | `bo/linhx-kenh-ao/skills/hop-thu` |
| `ke-hoach-90-ngay` | Lập kế hoạch 90 ngày cho chuỗi content → cộng đồng → bán theo khung 5 tầng – 2 vòng, gồm thang offer, nhịp cộng đồng, SOP người mới và chỉ số. Dùng sau chẩn đoá… | `bo/linhx-nuoi-cong-dong/skills/ke-hoach-90-ngay` |
| `kenh-ao` | Điều phối một phiên nuôi kênh người ảo (LAB040). Dùng khi Linh nói "chạy phiên", "nuôi kênh Mây", "tick kênh ảo", hoặc khi lịch gọi theo giờ. Đọc giai đoạn và p… | `bo/linhx-kenh-ao/skills/kenh-ao` |
| `ket-than` | Xây quan hệ dựa trên niềm tin với người trong vòng: chọn ai để chạm, chạm thế nào, có mục đích gì, ghi nhận khi họ đáp lại. Dùng cho bước vong, cham. | `bo/linhx-kenh-ao/skills/ket-than` |
| `lang-thang` | Người ảo lang thang đọc bài người khác, xem trend và tiêu hoá thành ghi chú. Dùng cho bước doc, tieu_hoa, trend của phiên kênh ảo. | `bo/linhx-kenh-ao/skills/lang-thang` |
| `lvn-listening` | Ra bản tin lắng nghe mạng xã hội tiếng Việt theo hồ sơ md (thương hiệu, ngành, chủ đề) từ dữ liệu LINHX_CRAWLER; 0 token cho phần số, ra BAO-CAO.md + feed.json … | `le/lvn-listening` |
| `nhap-du-lieu` | Biến dữ liệu thô về thành viên, hoạt động và đơn hàng (danh sách lớp, form, ghi chép nhóm Zalo, bình luận Facebook, file chat xuất ra) thành CSV đúng mẫu rồi nh… | `bo/linhx-nuoi-cong-dong/skills/nhap-du-lieu` |
| `nuoi-cong-dong` | Chạy vòng nuôi cộng đồng hằng tuần (chấm thành viên, việc SOP người mới, đề xuất, sức khoẻ) cho cộng đồng học viên LINHX hoặc cộng đồng khác. Dùng khi Linh nói … | `bo/linhx-nuoi-cong-dong/skills/nuoi-cong-dong` |
| `offer-cong-dong` | Thiết kế gói chia sẻ và hợp tác LINHX cho một cộng đồng hoặc sự kiện (talk, workshop, báo cáo đồng thương hiệu, công cụ miễn phí cho hội viên, tài trợ hiện vật … | `bo/linhx-radar/skills/offer-cong-dong` |
| `pheu-omni` | Lập kế hoạch marketing đa phễu may đo cho một biz bất kỳ (ads, SEO, content hub, personal brand, affiliate, cold reach, offline, search, community, group), giả … | `bo/linhx-pheu-omni/skills/pheu-omni` |
| `radar-cong-dong` | Quét định kỳ các hiệp hội, cộng đồng, sự kiện doanh nghiệp ở Việt Nam (CSMO, VSMCamp, Brands Vietnam, GPeC...), cập nhật CSDL nhà tài trợ và KOL, chấm điểm cơ h… | `bo/linhx-radar/skills/radar-cong-dong` |
| `tai-tao-flow` | Đọc một bài quảng cáo/khoe sản phẩm AI (agent, tool, khoá học), tái tạo flow kỹ thuật phía sau, chấm khả thi từng lời hứa, chấm khả năng kinh doanh cho LINHX, k… | `bo/linhx-tai-tao-flow/skills/tai-tao-flow` |
| `tao-bai` | Viết bài cho người ảo từ ghi chú tiêu hoá, theo persona, phong cách chung và luật viết; sinh nhiều ứng viên, tự chấm, đưa vào hàng duyệt. Dùng cho bước tao. | `bo/linhx-kenh-ao/skills/tao-bai` |
| `them-cong-dong` | Thêm một hiệp hội, cộng đồng hoặc sự kiện mới vào radar: tìm đủ kênh, nhà tài trợ các mùa, KOL, chủ đề, pain point, họ đã có gì, rồi tạo nguồn quét. Dùng khi Li… | `bo/linhx-radar/skills/them-cong-dong` |
| `vong-ads` | Một vòng tối ưu quảng cáo Meta/TikTok/Google kiểu Fastlane - đọc kết quả mẫu quảng cáo (CSV xuất từ Ads Manager hoặc qua MCP), chấm thắng/thua có xác suất, đề x… | `bo/linhx-vong-ads/skills/vong-ads` |
| `xuong-persona` | Tự học kiểu nhân vật nào làm người ta thích, chia sẻ, tranh luận; phát triển persona có character flaw theo phong cách chung. Dùng khi đọc được bài phản ứng mạn… | `bo/linhx-kenh-ao/skills/xuong-persona` |

## Nghiên cứu, radar, dữ liệu

| Skill | Làm gì | Ở đâu |
|---|---|---|
| `ban-do-chu-de` | Tổng hợp định kỳ (tháng, quý) từ các sự kiện đã index và hấp thu: mọi người đang nói gì, ai nói hay, pain point lặp lại, solution mới, khoảng trống chưa ai nói,… | `bo/linhx-radar/skills/ban-do-chu-de` |
| `don-bang` | Dọn một bảng dữ liệu tiếng Việt theo mục đích dùng (CRM, AI agent, chatbot, báo cáo) bằng recipe thao tác đóng có chạy thử, diff, hàng chờ duyệt và nhật ký tái … | `bo/linhx-du-lieu/skills/don-bang` |
| `hap-thu-su-kien` | Hấp thu nội dung một sự kiện đã đi hoặc chỉ xem lại: từ ghi chú, ảnh slide, video YouTube, bài tường thuật, ra talk, pain point, solution, số liệu, chấm diễn gi… | `bo/linhx-radar/skills/hap-thu-su-kien` |
| `ho-so-doi-tuong` | Làm hồ sơ một doanh nghiệp hoặc KOL trong radar: họ đang nói gì, đã có gì, đau ở đâu, LINHX chia sẻ và bán được gì, cách tiếp cận, nháp lời mở. Dùng khi Linh hỏ… | `bo/linhx-radar/skills/ho-so-doi-tuong` |
| `kiem-dinh` | Kiểm định file dữ liệu đã dọn theo hậu điều kiện trong recipe, chấm lại trước/sau và quyết định dừng hay dọn tiếp theo rubric 4 chiều. Dùng sau /don-bang, khi L… | `bo/linhx-du-lieu/skills/kiem-dinh` |
| `radar` | Radar LINHX hợp nhất. Chạy một lượt quét chung (cộng đồng, nhà tài trợ, KOL, sự kiện, giải thưởng, cuộc thi, quỹ tài trợ) và báo bản tin. Dùng khi Linh nói "chạ… | `bo/linhx-radar/skills/radar` |
| `radar-cuoc-thi` | Quét cuộc thi sáng tạo, viết lách, báo chí, marketing, AI và giải thưởng tại Việt Nam, cập nhật kho, ra bản tin hạn nộp và lịch .ics. Dùng khi Linh hỏi "có cuộc… | `bo/linhx-cuoc-thi/skills/radar-cuoc-thi` |
| `radar-giai-thuong` | Radar giải thưởng ở Việt Nam cho doanh nghiệp và cá nhân: giải nào LINHX, TUVA hoặc Linh nộp được, giải nào uy tín hay trả phí là có, ai vừa đoạt giải (danh sác… | `bo/linhx-radar/skills/radar-giai-thuong` |
| `radar-su-kien` | Quét và index sự kiện business, tech, AI, startup, marketing ở Việt Nam (offline và online), chấm nên đi hay không, ra lịch .ics và bản tin. Dùng khi Linh hỏi "… | `bo/linhx-radar/skills/radar-su-kien` |
| `research-loop` | Chạy vòng lặp nghiên cứu tự động qua đêm (hiểu đề → tài liệu → ý tưởng → thí nghiệm → phân tích) với phép đo khoá, nhật ký TSV và DIGEST buổi sáng. Dùng khi ngư… | `le/research-loop` |
| `research-write` | Viết bài báo từ kết quả research-loop theo thứ tự chứng cứ trước, lời sau - chuẩn bị đầu vào, cổng người duyệt, viết, phản biện độc lập. Dùng khi người nói "viế… | `le/research-write` |
| `tham-dinh-cuoc-thi` | Đọc thể lệ một cuộc thi hoặc giải thưởng, kiểm điều kiện, chấm giá trị branding và công sức, quyết định nên làm hay bỏ, lập lịch ngược. Dùng khi Linh gửi link t… | `bo/linhx-cuoc-thi/skills/tham-dinh-cuoc-thi` |
| `tham-dinh-su-kien` | Thẩm định một sự kiện trước khi đi: agenda, diễn giả đáng nghe, ai nên gặp, câu hỏi mang theo, có đáng tiền và thời gian không. Dùng khi Linh hỏi "event X có nê… | `bo/linhx-radar/skills/tham-dinh-su-kien` |
| `them-nguon-su-kien` | Thêm hoặc sửa nguồn quét của event radar (lịch Luma, Meetup, RSS báo, trang lịch sự kiện của hiệp hội, truy vấn Google News, truy vấn tìm kiếm). Dùng khi Linh g… | `bo/linhx-radar/skills/them-nguon-su-kien` |
| `theo-doi-ket-qua` | Theo dõi kết quả các bài Linh đã nộp, cập nhật pipeline và sổ giải thưởng, rồi lên kế hoạch khai thác branding khi đạt giải. Dùng khi hỏi "kết quả cuộc thi", "đ… | `bo/linhx-cuoc-thi/skills/theo-doi-ket-qua` |

## Giáo dục, khoá học

| Skill | Làm gì | Ở đâu |
|---|---|---|
| `course` | Dùng khi người dùng muốn biến một chủ đề thành khoá học e-learning hoàn chỉnh hoặc kiểm tra tiến độ hiện tại của khoá học để điều phối sang các skill thành phần… | `bo/linhx-course/skills/course` |
| `course-architect` | Dùng khi cần thiết kế khung chương trình khoá học theo phương pháp Backward Design: xác định chân dung người học, viết mục tiêu theo thang Bloom, thiết kế bộ câ… | `bo/linhx-course/skills/course-architect` |
| `course-package` | Dùng khi cần đóng gói toàn bộ khoá học (video bài giảng, phụ đề WebVTT, bài trắc nghiệm tương tác) thành gói chuẩn SCORM 1.2 (.zip), kiểm thử tự động trên LMS g… | `bo/linhx-course/skills/course-package` |
| `instructor-avatar` | Dùng khi cần tạo video giảng viên AI nói khớp môi với lời giảng tiếng Việt bằng mô hình tự chạy trên máy, hỗ trợ cả nhánh từ video gốc (MuseTalk 1.5) và nhánh t… | `bo/linhx-course/skills/instructor-avatar` |
| `instructor-voice` | Dùng khi cần tổng hợp lời giảng tiếng Việt cho từng phân đoạn bài học bằng VieNeu-TTS (giọng preset hoặc giọng clone của giảng viên) và kiểm tra chất lượng phát… | `bo/linhx-course/skills/instructor-voice` |
| `lesson-compose` | Dùng khi cần ghép ảnh các khung slide, các đoạn âm thanh lời giảng và video giảng viên AI thành video bài giảng hoàn chỉnh chuẩn 1920x1080 kèm phụ đề WebVTT và … | `bo/linhx-course/skills/lesson-compose` |
| `lesson-script` | Dùng khi cần viết kịch bản lời giảng chi tiết và bố cục slide Slidev cho từng bài học theo cấu trúc Gagné rút gọn, bảo đảm độ dài mỗi đoạn và tổng số âm tiết kh… | `bo/linhx-course/skills/lesson-script` |
| `screen-capture` | Dùng khi bài học có phần thực hành hoặc minh hoạ trực quan cần chụp ảnh hoặc quay lại màn hình trình duyệt, giao diện dòng lệnh và chèn vào slide hoặc ghép vào … | `bo/linhx-course/skills/screen-capture` |

## Khác

| Skill | Làm gì | Ở đâu |
|---|---|---|
| `bu-frontpage` | Dựng trọn mặt tiền web của một BU B2B (trang chủ lấy lead, 15–20 trang con, form brief + gọi lại, GEO, own media 3 pha) từ khuôn đã chạy thật ở event.ifagent.ne… | `le/bu-frontpage` |
