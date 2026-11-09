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
