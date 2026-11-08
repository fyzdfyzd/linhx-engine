# Lối theo loại video

Đọc ở bước 0 của SKILL.md. Mỗi loại có khuôn riêng: đầu vào, độ dài, cấu trúc, máy dựng, tiếng, điểm dừng duyệt, kiểm thêm. Phần chung (giọng, font, kiểm khung, duyệt) vẫn theo SKILL.md.
Nguồn: rà 75 repo ngày 30/10/2026 (LAB095). Tên repo trong ngoặc là chỗ học, không phải thứ phải cài.

| Linh nói | Loại | Đi tiếp |
|---|---|---|
| clip bán hàng, ra mắt, quảng cáo, giới thiệu app/web/sản phẩm, bản cập nhật | 1. Bán hàng | nhánh A |
| giải thích, bài giảng, e-learning, "biến tài liệu/kế hoạch này thành video" | 2. Giải thích | nhánh A |
| hoạt hình, phim ngắn kể chuyện, MV, video theo bài hát | 3. Hoạt hình, ca nhạc | nhánh A |
| reel, short, TikTok, clip dọc, làm hàng loạt | 4. Clip dọc | nhánh A hoặc B |
| "làm giống video này", gửi link/file mẫu | 5. Bắt chước mẫu | nhánh C (`bat-chuoc.md`) |
| có file quay sẵn: mặt nói, màn hình, cảnh quay | 6. Dựng từ cảnh quay | nhánh B (`record.md`) |

## 1. Bán hàng, ra mắt
Học từ: shipvideo, product-launch-motion, video-shotcraft, guizang-product-video-skill, huashu-motion (product-fit), motion-designer (kaventro), cinetic, motion-video-kit, ai-promo-video-maker.

- **Đầu vào là hàng thật.** Link web thì chụp trang thật bằng Playwright (cuộn, bấm, gõ) chứ không vẽ lại giao diện giả. App thì dùng ảnh chụp màn hình thật đặt trong khung điện thoại/laptop. Mỗi tuyên bố trên hình (số liệu, tính năng) phải có nguồn trong `NGUON.md`; số minh hoạ ghi rõ "minh hoạ".
- **Độ dài**: 15 giây (quảng cáo), 30 giây (mặc định), 45–60 giây (ra mắt có nhiều tính năng).
- **Cấu trúc**: một vật hoặc một giao diện dẫn cả phim, ít cắt cứng (48 phim ra mắt nhiều tương tác tháng 10/2026: trung vị 0 cú cắt cứng). Móc 0–3 giây là sản phẩm ở trạng thái đẹp nhất. Kết bằng tên/logo; CTA không bắt buộc.
- **Ba hướng trước khi dựng** (cinetic, huashu): A hợp ngành (cách ngành này hay làm), B khuếch đại (đẩy một đặc điểm lên cực đại), C bất ngờ (một vật, một con số, không giải thích). Chọn một, viết 3–5 dòng "vì sản phẩm có X nên dùng thủ pháp Y". Không dùng thủ pháp không nói được lý do.
- **Khung 0 là ảnh bìa**: 5 khung đầu phải là hình hoàn chỉnh (thường là trạng thái xong của cảnh mở), không nền trống (guizang). `kiem_khung.mjs` và `kiem_video.py` đều bắt lỗi này.
- **Tiếng**: phim dưới 13 giây thiết kế để xem không tiếng (phụ đề/chữ tự đủ nghĩa); trên 30 giây thì nhạc dẫn. Cắt cảnh trên phách (`nhip_nhac.py`), mỗi cú bấm/gõ có SFX.
- **Máy dựng**: HyperFrames hoặc HTML một file. Remotion khi cần 10+ bản cho nhiều sản phẩm.
- **Giao**: 16:9 + 9:16 + 1:1 cùng nguồn, `poster.jpg`, bản có nhạc và bản chỉ có SFX, câu chữ đăng bài.
- **Duyệt**: dừng sau ba hướng + 3 khung mẫu, Linh chọn rồi mới dựng.

## 2. Giải thích, e-learning
Học từ: anything2explainer, video-talkcraft, vox-explainer-skill, vox-ai-motion-graphics-generator, weilanx-claude-videos, plan-to-video, explainer-studio, adu-motion-video, hbg-life-simulation. Nối LAB055 Anatomy (cỗ máy isometric).

- **Giọng trước, hình theo từng chữ.** `giong_viet.py` ra `cues.json` có mốc từng câu; mỗi phần tử hiện trong khoảng −6…+3 khung so với chữ nó minh hoạ (talkcraft, anything2explainer).
- **Bốn điểm dừng duyệt** (anything2explainer): (1) độ dài; (2) lời định bản, kèm tên các chương đứng riêng một dòng, hỏi "chỉ đọc mấy chữ này có biết chương nói gì không"; (3) giọng; (4) 30 giây đầu đã render. Sửa ở điểm 4 rẻ hơn nhiều so với sửa cả phim.
- **Lời**: một ví dụ xuyên suốt cả phim; mở bằng tình huống của người xem; số đổi sang thước đo cảm được; không tả lại cái hình đang chiếu. Lời định bản rồi thì không sửa chữ nữa (mọi mốc thời gian sẽ lệch).
- **Độ dài theo giọng thật**: tạo giọng xong đọc `dur.json`; lệch quá 15% so với độ dài muốn thì thêm/bớt câu, không chỉnh tốc độ đọc.
- **Cảnh theo đơn vị hình, không theo câu**: câu ngắn hơn 3 giây gộp vào cảnh kề; mỗi cảnh ít nhất 5 giây; một cảnh 2–4 câu. Mỗi khung một nhân vật chính, cỡ lớn, có ánh/viền; không có gì đứng yên quá 3 giây; cuối cảnh để yên 1–1,5 giây rồi mới chuyển. Không thêm "trôi lơ lửng" cho có chuyển động.
- **Dải phụ đề cấm đặt nội dung**, đường bay vào không cắt ngang dải phụ đề. Mỗi khối phụ đề ≤ 16 chữ, không xuống hai dòng.
- **Phong cách hợp**: cắt dán giấy kiểu Vox, vẽ tay/whiteboard, pixel, sơ đồ hệ thống, isometric Anatomy, thuỷ mặc cho chủ đề văn hoá.
- **Tài liệu thành video** (plan-to-video): đọc tài liệu → 5–8 ý chính → mỗi ý một cảnh → lời → như trên.
- **Máy dựng**: HyperFrames (nhiều chữ) hoặc Remotion (phim dài, nhiều chương, cần chia nhóm cảnh cho nhiều agent).
- **Phim trên 2 phút**: chia nhóm 5–7 cảnh, làm nhóm 1 làm mẫu, Linh duyệt, các nhóm còn lại đọc nhóm 1 làm chuẩn (agy chạy đêm theo `dem-agy.md`).

## 3. Hoạt hình, ca nhạc
Học từ: lemo-opuscar, mg-styles-15, opus-video-skills, xilo-opus-video, ClaudeAnimationBase, animate, motion-graphics-music-video-skill, vocaloid-style-mv-pipeline, story-to-video.

- **Ba phương án + bản xem trước rồi mới dựng** (xilo): ba hướng hình/nhịp khác nhau, mỗi hướng 1 khung tĩnh và 4–6 giây chuyển động. Linh chọn.
- **Kịch bản hình duyệt trước** (animate): bảng cảnh có khung phác cho từng nhịp.
- **MV**: nghe cả bài; chạy `nhip_nhac.py bai.mp3 --js` lấy BPM, phách, cú đánh, độ to từng khung; đánh dấu mở, verse, điệp khúc, drop, kết. Cắt cảnh trên phách, chuyển động lớn theo `low` (trống bass), chữ lời bài theo mốc (LRC hoặc whisper rồi chỉnh tay, whisper hay sót chữ khi hát). Làm cảnh mở và cao trào trước.
- **Phim dài chia chương**: viết `HUONG-DAN-HINH.md` chung (bảng màu, nét, nhịp, nhân vật) rồi mỗi agent một chương (PDoomVideo, ClaudeAnimationBase).
- **Nhân vật**: nhân vật vẽ bằng code (hình khối, nét, rối giấy) thì được. Nhân vật diễn xuất tự nhiên, khớp môi, người giống thật là việc của model video (Veo/Flow, LAB016); story-to-video và motion-graphics-music-video-skill dùng model ảnh/video trả phí, không phải code.
- **Máy dựng**: Lemo (51 style chất liệu) hoặc HTML một file với p5/canvas.

## 4. Clip dọc, làm hàng loạt
Học từ: claude-shorts, claude-faceless-shorts-creator, motion-graphics-skills, hyperframes-motion-reel-skill, avatar-mix, super-video-maker-skill.

- **Khổ 1080×1920**. Vùng an toàn: chữ chính không nằm ở 15% dưới cùng và 12% mép phải (nút và chú thích của TikTok/Reels/Shorts che).
- **3 giây đầu**: câu móc hiện bằng chữ ngay khung 0.
- **Cắt từ video dài** (claude-shorts): đọc bản chép lời, chọn 8–12 đoạn 15–55 giây, chấm theo 5 tiêu chí có trọng số: móc 0,30; đứng riêng không cần ngữ cảnh 0,25; cảm xúc 0,20; mật độ giá trị 0,15; kết thoả mãn 0,10. Đưa Linh bảng đoạn + điểm + câu móc, Linh duyệt rồi mới cắt. Điểm cắt dời tới chỗ im lặng gần nhất. Dùng `cat_record.py` để có lời từng chữ.
- **Làm loạt không lộ mặt** (faceless): một khuôn Remotion, dữ liệu từng clip trong CSV/JSON, render bằng `--props`. Khuôn qua kiểm và duyệt một lần, các bản sau chỉ chạy `kiem_video.py`.
- **Người dẫn ảo** (avatar-mix, super-video-maker): cần HeyGen hoặc dịch vụ avatar trả phí; ngoài phạm vi skill này, chuyển LAB040/LAB066 (người ảo, casting mặt).

## 5. Bắt chước video mẫu
Xem `bat-chuoc.md` (motion2code, animation-reverse-engineering, motion-prompt).

## 6. Dựng từ cảnh quay có sẵn
Học từ: video-use, herk-edit-kit, ffmpeg-skill, claude-youtube-editor, video-editor-skills, video-agent-skills, editor-pro-max, claude-code-video-toolkit (digitalsamba, wilwaldon), erduo-broll-loop-engineering, motion-graphics (Barty-Bart).

- **Đọc lời, không xem từng khung** (video-use): bản chép lời có mốc từng chữ là thứ Claude đọc chính (vài KB). Ảnh ghép khung + sóng âm chỉ xuất ở điểm cần quyết định (chỗ ngập ngừng, chọn giữa hai lần quay).
- **Chu trình**: chép lời → gói lời → Claude lập danh sách cắt (EDL) → render → tự kiểm ở mọi điểm cắt (nhảy hình, bụp tiếng, phụ đề bị che) → sửa, tối đa 3 vòng. Không đụng vào bản cắt trước khi Linh duyệt hướng.
- **Kho B-roll của Linh** (video-agent-skills): quét một lần mọi clip (ffprobe độ dài, khổ, ngày, GPS + một contact sheet), gắn nhãn bằng agent rẻ (Haiku), lưu một file text để `grep`. Khi dựng chỉ tìm trong kho.
- **B-roll từ phụ đề** (erduo): đọc file SRT, mỗi ý cần minh hoạ sinh một cảnh code ngắn (biểu đồ, chữ, sơ đồ) chèn đúng mốc.
- **Chèn đồ hoạ khớp lời nói** (Barty-Bart, herk): đồ hoạ HyperFrames trong suốt chồng lên cảnh quay; tách người khỏi nền khi cần chữ đi sau người.
- **Xuất YouTube**: H.264 high, yuv420p, gắn nhãn màu BT.709 để khỏi bị bạc màu; tiếng −14 LUFS. Nhánh B có sẵn trong `record.md`.
