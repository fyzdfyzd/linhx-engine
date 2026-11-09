# WF12 · Video ngắn, reel: nghiên cứu nền (9/11/2026)

Bản nháp đầu, ghi sớm; bổ sung dần. Đã clone và đọc code thật 6 nguồn vào `_refs/WF12/` (dữ liệu, không chạy). Remotion lõi và MoneyPrinterTurbo clone hết giờ, chưa đọc.

## Kết luận
1. Skill `phim-code` đã mạnh hơn hầu hết người ngoài về máy đo (`kiem_khung.mjs`, `kiem_video.py`) và đã rà 75 repo. Không viết lại; chỉ vá.
2. Thứ LINHX thiếu rõ nhất, lấy từ HyperFrames: **SPEC.md biến tính từ thành số + danh sách CẤM mặc định**, và **duyệt theo lỗi P0/P1/P2 có sửa cụ thể, không chấm điểm**.
3. Skill đang lệch ngưỡng với code đo thật của HyperFrames: thời gian giữ chữ (quá lỏng), vùng an toàn dọc (thiếu mép trên, mép dưới quá hẹp), và luật "mọi điểm ≥ 8" (HyperFrames cấm chấm điểm).
4. Chưa có bản vàng tải được; chỉ có link nguồn mốc (mục Bản vàng). Cần Linh chọn 3–5 reel/trailer Việt làm mốc thật (D2 cho WF này).
5. Số liệu "3 giây đầu" trên blog là tin thứ cấp, không dùng làm ngưỡng; ngưỡng lấy từ code đo.

## Quy trình đề xuất
| Bước | Ai | Ra gì |
|---|---|---|
| 1 Đề bài, hỏi một lần | Claude | `DE-BAI.md` (đã có) |
| 2 Ba cốt truyện bằng chữ, chọn một | Claude → Linh (D2) | `STORYLINES.md`; che tên nhánh |
| 3 `SPEC.md`: mọi tính từ thành số, cảnh theo khung, **CẤM** mặc định | Claude | `SPEC.md` (mới) |
| 4 Giọng + `cues.json` trước, rồi dựng | agy | trang HyperFrames |
| 5 `kiem_khung` + `hyperframes check` + `kiem_video` | máy | 0 LỖI |
| 6 Duyệt mù: agent sạch xem 3 contact sheet + sheet 360 px, trả P0/P1/P2 | Claude khác phiên | `REVIEW.md` |
| 7 Sửa tối đa 2 vòng, hoàn tác nếu tệ hơn | agy | bản giao |
| 8 Linh duyệt D4 | Linh | |

## Máy đo + ngưỡng
Rẻ tới đắt. Ngưỡng ghi nguồn; "[đề xuất]" là của tôi, chưa thử.
- **Tự động, phim**: khổ, độ dài, LUFS, khung đen, đứng hình, khung đầu trơn (đã có ở `kiem_video.py`). Đổi LUFS thành −16…−14 và đỉnh ≤ −1 dBTP theo HyperFrames `sound.md` (hiện skill cho −18…−12).
- **Tự động, trang**: thêm các phép đo của HyperFrames `craftAudit.ts`: `line_unread`, `dead_stretch` (> 3 giây không đổi), `text_below_floor` (chữ < 2,6% cạnh ngắn, tức 28 px ở 1080), `first_frame_empty`, `film_silent`. Skill đã có phần lớn; thiếu `line_unread` kiểu mới.
- **Giữ chữ**: "hold it about 0.5 s + 0.3 s a word". Tám chữ = 2,9 giây. Skill đang ghi ≥ 1,2 giây cho 8 chữ: sửa.
- **Rubric**: giữ 8 tiêu chí của `duyet.md` làm câu hỏi, bỏ điểm số. Mỗi lỗi một dòng: `t=4.2s · chỗ · lỗi → sửa đúng một dòng · cái giữ lại`. Đạt khi 0 P0 và P1 còn lại có lý do. [đề xuất] Chấm mù: agent duyệt chỉ nhận `STORYBOARD`/`SPEC` + ảnh, không thấy lời thợ.
- **Bước "người lạ"**: mỗi khung beat, mô tả một câu như người lạ, gọi tên mọi vật; vật phải giải thích mới hiểu = P0 (HyperFrames `review.md`).
- **Loạt clip dọc**: [đề xuất] đủ 4–9 clip mỗi nguồn dài, dựa số đo thật của OpenShorts (xem Nguồn).
- **Vùng an toàn dọc 1080×1920**: HyperFrames: "nothing in the top 168 px … every word and the product inside the band from 168 to 1330 px". Skill ghi 15% dưới + 12% phải. Hai số lệch nhau; nguồn thứ cấp khác ghi trên 210 / dưới 320 / phải 120 [chỉ thấy]. [đề xuất] chữ trong 168–1330 theo HyperFrames cho tới khi Linh thử trên máy thật.

## Bản vàng
Chưa tải được tệp. Mốc nguồn (đều [chỉ thấy], chưa xem chất lượng; Linh/Claude cần xem rồi mới chọn):
1. HyperFrames showcase, phim ra mắt chính hãng, đo từng khung: https://hyperframes.heygen.com/examples
2. GitHub Unwrapped (Remotion), phim cá nhân hoá hàng loạt: https://github.com/remotion-dev/github-unwrapped-2023
3. OpenShorts demo tách thể loại clip dọc từ podcast (nguồn CC BY): https://github.com/mutonby/openshorts
4–5. Cần Việt: 2 reel/trailer Việt do Linh chỉ ra. Đề DR: `DR/DE-1.md`.

## Sửa vào skill nào, sửa gì (`phim-code`)
1. `SKILL.md` bước 5–6: thêm `SPEC.md` (mẫu lấy từ HyperFrames `spec.md`: GOAL/OUTPUT/TIME/LOOK/OBJECTS/MOTION/SHOTS/BANNED/QA).
2. `references/duyet.md`: thay "mọi điểm ≥ 8" bằng P0/P1/P2; thêm bước người lạ; thêm quy tắc CHAI của OpenMontage (lỗi nặng phải kèm sửa cụ thể, nếu không chỉ là "điều tra").
3. `duyet.md` bảng rập khuôn: bổ sung CẤM của HyperFrames chưa có (hào quang/phát sáng, nền đen có vật nhỏ nổi giữa, mọi thứ cùng mờ vào, chữ trôi sau khi đã vào, góc/khung HUD).
4. `loai-video.md` mục 4: vùng an toàn thêm mép trên; sửa số theo mục trên.
5. `kiem_video.py`: LUFS −16…−14, ≤ −1 dBTP. `kiem_khung.mjs`: giữ chữ = 0,5 + 0,3/chữ.
6. Thừa/không đổi: ba máy dựng, `giong_viet.py`, `cat_record.py` — không có gì tốt hơn ở nguồn đã đọc.

## Rủi ro
- Skill HyperFrames bảo chạy `npx hyperframes events` lúc bắt đầu, gửi tên skill kèm telemetry của CLI (có cách tắt): thợ cần tắt hoặc bỏ bước này.
- Ngưỡng hold/vùng an toàn lấy từ phim tiếng Anh/Trung; chữ Việt có dấu dài hơn, cần thử.
- Chưa có người làm nghề (agency) nào đọc được; mục "người giỏi nhất" mới dựa 2 bộ skill, chưa dựa studio thật.
- Bản vàng chưa duyệt ⇒ chưa chấm ngang được.

## Nguồn
- [đọc] HyperFrames repo: https://github.com/heygen-com/hyperframes (`skills/hyperframes/SKILL.md`, `references/review.md`, `spec.md`, `story.md`, `captions.md`, `types/vertical.md`, `packages/cli/src/utils/craftAudit.ts`)
- [đọc] OpenMontage: https://github.com/calesthio/OpenMontage (`AGENT_GUIDE.md`, `skills/meta/reviewer.md`, `pipeline_defs/clip-factory.yaml`)
- [đọc] OpenShorts: https://github.com/mutonby/openshorts (`clip_selection.py`)
- [đọc] Remotion skills: https://github.com/remotion-dev/skills; ClipsAI: https://github.com/ClipsAI/clipsai; MoneyPrinterV2: https://github.com/FujiwaraChoki/MoneyPrinterV2 (lướt, ít giá trị: là công cụ đăng bài, không có kiểm chất lượng)
- [chỉ thấy] blog hook 3 giây: https://dev.to/bulkdl/hook-engineering-the-science-of-the-first-3-seconds-in-short-form-video-2026-2jp9
- [chỉ thấy] tiếng Việt: https://www.capcut.com/vi-vn/resource/best-tiktok-hooks

## Bổ sung vòng 2 (9/11/2026)

Đọc thêm nguồn thật bằng đọc trang web (không Chrome, không chạy code tải về). [đọc] = đã mở trang và trích; [chỉ thấy] = chỉ thấy qua tìm kiếm hoặc bài thứ cấp.

### A. Vùng an toàn dọc: có số từ trang chính thức, lệch với số đang dùng
- [đọc] Meta, thông số quảng cáo Instagram Reels (trang trả bản tiếng Việt), nguyên văn: "Tránh thêm văn bản, logo hoặc các thành phần nội dung quan trọng khác trong khoảng 14% không gian trên cùng, 35% không gian dưới cùng và 6% không gian ở mỗi cạnh bên của tài sản." https://www.facebook.com/business/ads-guide/update/video/instagram-reels
  - Quy ra khung 1080×1920 (tôi tính: 14% × 1920 ≈ 269 px; 35% × 1920 = 672 px; 6% × 1080 ≈ 65 px): chữ nằm trong dải y ≈ 269–1248, cách mỗi bên ≈ 65 px. Bài flowjam ghi "roughly the top 270 pixels, the bottom 670 and 65 on each side", khớp phép tính. https://www.flowjam.com/blog/video-ad-specs [chỉ thấy]
- [đọc] TikTok, thông số quảng cáo in-feed (cập nhật "June 2026"), nguyên văn: "The safe zone size is determined by the dimension (vertical, horizontal, or square), ad caption length, and any additional formats used." Không có số phần trăm; vùng an toàn là tệp zip mẫu (chưa mở). https://ads.tiktok.com/help/article/video-ads-specifications
- YouTube: PDF "Universal Safe Zones for Video on YouTube" https://services.google.com/fh/files/misc/universalsafezones-youtube.pdf tải được nhưng là ảnh, chưa đọc được chữ. Đưa vào `DR/DE-2.md`.
- reap.video tự đề xuất "15 percent at the top and 25 to 35 percent at the bottom" và tự nói "Treat these as working margins, not official universal specifications." https://reap.video/blog/short-form-video-safe-zones [chỉ thấy]
- **Kết luận**: dải 168–1330 px của HyperFrames **rộng hơn** dải Meta (≈269–1248) ở cả hai đầu. Nếu làm quảng cáo Reels thì chữ sát mép sẽ bị che. [đề xuất, chưa thử] `kiem_khung.mjs` có hai chế độ: `organic` (168–1330, HyperFrames) và `ads` (Meta 14/35/6%).

### B. Phụ đề tiếng Việt: có số tốc độ đọc (lấp mục "chữ Việt có dấu dài hơn")
- [đọc] Netflix Vietnamese Timed Text Style Guide. Mục 2: "42 characters per line." Mục 14: "Adult programs: Up to 17 characters per second", "Children's programs: Up to 13 characters per second". Mục 21 (SDH): "Adult programs: Up to 20 characters per second". https://partnerhelp.netflixstudios.com/hc/en-us/articles/220447048-Vietnamese-Timed-Text-Style-Guide
- [đọc] Quy định chung: tối thiểu "5/6 (five-sixths) of a second per subtitle event", tối đa "7 seconds per subtitle event", "2 lines maximum". https://partnerhelp.netflixstudios.com/hc/en-us/articles/215758617-Timed-Text-Style-Guide-General-Requirements
- [đọc] Đối chiếu Anh Mỹ, mục I.14: "Adult programs: Up to 20 characters per second", "Children's programs: Up to 17 characters per second". https://partnerhelp.netflixstudios.com/hc/en-us/articles/217350977-English-USA-Timed-Text-Style-Guide
- Tôi tính từ số trên: dòng đầy 42 ký tự cần ≥ 42/17 ≈ 2,5 giây (Việt) so với 42/20 = 2,1 giây (Anh). [đề xuất, chưa thử] giữ chữ = số lớn hơn của (0,5 + 0,3 × số chữ) và (số ký tự ÷ 17). Lưu ý Netflix là phim dài, phụ đề dịch; không có số chính thức riêng cho reel.
- Bản cũ có "words per minute", đã bỏ ngày 2018-03-09 ("Revised section 14 Reading Speed - words per minute removed"): chỉ dùng cps.

### C. Số "3 giây đầu": thay blog bằng nguồn có tên bên đo
- [chỉ thấy] Social Media Today (Andrew Hutchinson, 22/3/2026) tóm báo cáo Emplifi, đo 10.110 Facebook Reels của 704 trang thương hiệu: "human speech performs even better than music, with 10-second retention increasing almost 25%"; "when a person appears for at least one second within the first three seconds of a Reels clip, retention improves by about 10% for 10-second views". https://www.socialmediatoday.com/news/human-speech-and-presence-help-drive-reels-engagement/815381 (gốc: https://emplifi.io/resources/facebook-reels-data/, chưa mở)
- Giới hạn: chỉ Facebook Reels của thương hiệu, bên thứ ba, không phải số của Meta. Câu "47% of the value … first three seconds" gán cho "Meta's own research" chỉ thấy ở blog bên thứ ba, không kiểm được, không dùng.
- Dùng làm gợi ý (có người nói/xuất hiện trong 3 giây đầu), không làm ngưỡng máy đo.

### D. Remotion lõi
- [đọc] "The `@remotion/captions` package provides utilities for dealing with subtitles." và "At the centre of this caption is the `Caption` type, which defines a standard shape for captions from different sources." https://www.remotion.dev/docs/captions/api
- Học: một định dạng trung gian giữa bước chuyển giọng và bước dựng, chỗ để chèn phép kiểm cps. LINHX đã có `cues.json`, chỉ cần thêm phép kiểm đó.
- Chưa đọc được: `/docs/` và `/docs/google-fonts/` trả 404; chưa có gì về kiểm tải phông chữ Việt của Remotion.

### E. Máy đo thử trên mẫu thật (script của repo, không chạy code lạ)
Script `skills/bo/linhx-phim-code/skills/phim-code/scripts/kiem_video.py` (cần ffmpeg/ffprobe, có sẵn). Mẫu: `D:\LINHX\ai-ugc-video\clips\scene1.mp4`, `scene2.mp4` (clip AI 8 giây của dự án UGC, không phải bản vàng).
- Lệnh 1: `PYTHONUTF8=1 python scripts/kiem_video.py D:/LINHX/ai-ugc-video/clips/scene1.mp4 --kho 9:16 --giay 4-10`. Kết quả thật: `720x1280 24.00fps 8.0s tiếng=có -16.8 LUFS, đỉnh -2.4 dBTP`; LỖI 0; CẢNH BÁO 1 ("cạnh ngắn 720px < 1080"); thoát 0.
- Lệnh 2: `scene2.mp4 --kho 16:9 --giay 4-10` (cố ý đặt sai khổ). Kết quả thật: `-22.7 LUFS, đỉnh -6.3 dBTP`; LỖI 2 ("khổ 720x1280 không phải 16:9", "độ to -22.7 LUFS, cần khoảng -14 (chấp nhận -18..-12)"); thoát 1. Nhánh báo lỗi chạy đúng.
- Lần chạy đầu (không đặt `PYTHONUTF8`) **lỗi** `UnicodeEncodeError: 'charmap' codec can't encode character '\u1ec3'` ở dòng in kết quả (Python 3.12, Windows, cp1252). Đây là lỗi thật của script trên Windows. [đề xuất] thêm `sys.stdout.reconfigure(encoding="utf-8")` ở đầu `kiem_video.py`, nếu không thợ sẽ tưởng máy hỏng.
- Đề xuất vòng 1 (LUFS −16…−14): `scene1` đo −16,8 LUFS vừa **qua** ngưỡng hiện tại (−18…−12) vừa **trượt** −16…−14, nên ngưỡng mới có tác dụng thật. Chưa biết −16…−14 có hợp nền tảng Việt (chỉ có nguồn HyperFrames).
- Chưa thử: `kiem_khung.mjs` (cần trang HyperFrames, máy này không có mẫu) và các đề xuất đổi (giữ chữ, dải an toàn).

### F. Còn thiếu sau vòng 2
- Chưa đọc nguồn studio làm nghề nào: công cụ đọc trang không tự tìm được URL; cần URL cụ thể hoặc máy công ty. Xếp vào `DR/DE-2.md`.
- Bản vàng chưa xem tận mắt; link ở `DR/DE-2.md`.
- Vùng an toàn YouTube Shorts, zip mẫu TikTok, số giữ chân xem từ nền tảng chính thức: chưa có.
- Mục ArcFace của WF14 không thuộc WF12, không làm ở đây.
