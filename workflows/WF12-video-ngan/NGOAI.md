# Người ngoài đã làm: WF12

Đọc 9/11/2026 trên máy cty; bản clone ở `D:\LINHX\WF-NC\_refs\WF12\` (dữ liệu, không chạy).

| Nguồn | Đã đọc gì | Lấy | Bỏ |
|---|---|---|---|
| HyperFrames https://github.com/heygen-com/hyperframes | `skills/hyperframes/SKILL.md`, `review.md`, `spec.md`, `story.md`, `captions.md`, `types/vertical.md`, `craftAudit.ts` | SPEC.md có số + danh sách CẤM; duyệt P0/P1/P2 không chấm điểm; ngưỡng đo (dead_stretch 3 giây, chữ ≥ 2,6% cạnh ngắn, giữ chữ 0,5+0,3/chữ); vùng an toàn dọc; ba cốt truyện bằng chữ trước khi dựng | telemetry `events`; app desktop "Framey" |
| OpenMontage https://github.com/calesthio/OpenMontage | `AGENT_GUIDE.md`, `skills/meta/reviewer.md`, `pipeline_defs/clip-factory.yaml` | quy tắc CHAI: lỗi nặng phải có sửa cụ thể, thiếu sửa thì chỉ là "điều tra"; mỗi bước có "đạo diễn" riêng và cổng duyệt | luật "mọi thứ qua pipeline YAML" (quá nặng cho reel); công cụ phải có API trả phí |
| OpenShorts https://github.com/mutonby/openshorts | `README.md`, `clip_selection.py`, `design.md` | số đo thật: nguồn dài nên ra 4–9 clip; chọn đoạn theo xếp hạng toàn cục, không theo từng lô | phần đám mây, đăng nhập, bảng giá |
| Remotion skills https://github.com/remotion-dev/skills | liệt kê 13 skill (captions, render, best-practices) | để dành cho loạt clip cá nhân hoá | chưa đọc sâu |
| ClipsAI https://github.com/ClipsAI/clipsai | `clip/texttiler.py` | ý TextTiling tách đoạn theo chủ đề để chọn điểm cắt | cần GPU và torch; không cần nếu đã có `cat_record.py` |
| MoneyPrinterV2 https://github.com/FujiwaraChoki/MoneyPrinterV2 | `AGENTS.md` | không có | công cụ đăng bài tự động, không có kiểm chất lượng |
| Remotion lõi, MoneyPrinterTurbo | clone hết giờ, chưa đọc | | |
| Blog hook 3 giây (dev.to, CapCut VN) | chỉ thấy tóm tắt | chỉ làm gợi ý | không dùng làm ngưỡng (nguồn thứ cấp, số khó kiểm) |
| Netflix Timed Text Style Guide (Việt) https://partnerhelp.netflixstudios.com/hc/en-us/articles/220447048-Vietnamese-Timed-Text-Style-Guide | mục 2, 14, 21 + quy định chung (vòng 2) | 17 cps người lớn, 42 ký tự/dòng, tối thiểu 5/6 giây, tối đa 7 giây | số cho phim dài, chưa chắc hợp reel |
| Meta thông số quảng cáo Reels https://www.facebook.com/business/ads-guide/update/video/instagram-reels | mục vùng an toàn (vòng 2) | 14% trên, 35% dưới, 6% mỗi bên | chỉ áp dụng cho quảng cáo |
| TikTok thông số in-feed https://ads.tiktok.com/help/article/video-ads-specifications | mục Safe Zone (vòng 2) | vùng an toàn phụ thuộc độ dài caption, có zip mẫu | không có số phần trăm |
| Remotion `@remotion/captions` https://www.remotion.dev/docs/captions/api | trang API (vòng 2) | định dạng `Caption` trung gian | trang docs gốc 404, chưa đọc phần render/phông |
