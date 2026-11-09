# NGHIÊN CỨU NỀN · WF14 Nhân vật ảo (9/11/2026)

## Kết luận
1. Quy trình LINHX (casting, bầu ảnh thật 3b, 3 góc, phát triển, sheet cuối) chặt hơn mọi skill ngoài tôi đọc; skill ngoài chủ yếu là một prompt sheet 7 góc ([laniameda](https://github.com/michailbul/laniameda-skills/blob/main/skills/ai-creatorship/character-consistency-character-sheet/SKILL.md)). Không viết lại, chỉ vá.
2. Lỗ hổng lớn nhất: **"giữ mặt qua mọi ảnh" hiện chỉ do Claude nhìn và chấm**. Skill ngoài cũng vậy; mckruz tự ghi "Cannot evaluate actual likeness preservation quality — only structural/parameter correctness" ([EVAL.md](https://github.com/mckruz/comfyui-expert/blob/main/skills/comfyui-character-gen/eval/EVAL.md)). Nên thêm máy đo số: điểm ArcFace.
3. Thêm ba trạng thái **match / không khớp / không thấy** khi đối chiếu ảnh với spec, và kiểm ảnh master với thẻ thiết kế trước khi lấy làm chuẩn ([Dreamina](https://dreamina.capcut.com/vi-vn/ai-video/character-reference-sheet-master-approval-animation)).
4. Bible mẫu ngoài có hai mục mà SKILL.md phat-trien-nhan-vat chưa thấy nhắc: **giọng nói** và **ngôn ngữ máy quay** ([Character Bible 7 asset](https://www.imaginary.app/blog/ai-influencer-videos-without-filming-2026-the-character-bible-system-to-keep-one)). Cần kiểm lại BIBLE.html thật.
5. Giấy phép: model InsightFace (gói buffalo_l) chỉ cho phi thương mại ([README](https://github.com/deepinsight/insightface)). Dùng cho việc công ty phải xin phép; AuraFace được [mckruz SKILL.md](https://github.com/mckruz/comfyui-expert/blob/main/skills/comfyui-character-gen/SKILL.md) mô tả là "Open-source ArcFace alternative" (chưa kiểm giấy phép gốc).

## Quy trình đề xuất (giữ khung LINHX; mục **đậm** là thêm)
| Bước | Ai | Ghi chú |
|---|---|---|
| 1 Brief + persona khán giả | Claude | giữ |
| 2 Tìm và bầu ảnh tham chiếu (3b) | Claude, Linh xem REF-BAU | bắt buộc, trước lượt vẽ đầu (BAI-HOC #39) |
| 3 Vẽ top 5, R0–R2, 3 góc | ChatGPT vẽ, Claude chấm | giữ |
| **3' Chốt master + thẻ bất biến** | Claude | một tập nhỏ bất biến nhìn thấy; đối chiếu master với thẻ; ảnh bị loại để vào `loai/`, không dùng làm tham chiếu |
| 4 Cổng C0 | Linh chọn mặt | giữ |
| 5 Phát triển (cơ thể, tủ đồ, biểu cảm) | ChatGPT/Gemini vẽ | **thêm Voice rules, Camera language vào spec** |
| **6 Đo mặt** | máy | điểm ArcFace mọi ảnh so với bộ 3 góc đã duyệt |
| 7 Bible + sheet cuối, cổng D4 | Claude ghép, Linh duyệt | giữ |

## Máy đo + ngưỡng
| Máy đo | Cách | Ngưỡng |
|---|---|---|
| Spec đủ | `kiem_cu_the.py` (đã có) | 100% mục |
| Ngân sách ảnh | LOG.md | ≤ 90 ảnh/nhân vật (Trần AI hết 99, BAI-HOC #50) |
| **Giữ mặt (mới)** | ArcFace buffalo_l, cosine giữa mặt ảnh và bộ 3 góc đã duyệt; lấy **điểm tệ nhất của lô**, không lấy trung bình | đề xuất **≥ 0,45** mỗi ảnh. Thang từ [AlchemicaFaceMatch](https://comfy.icu/node/AlchemicaFaceMatch): "0.45–0.60 same person, other pose / light / age"; "< 0.30 a different person" |
| Lưu ý | cùng nguồn | "ArcFace embeds identity, not style": ảnh cách điệu mạnh hoặc che mặt có thể < 0,45 dù người thấy giống; đọc là cờ xem xét, không phải phán quyết |
| Spec so với ảnh | Claude chấm mù | mỗi bất biến: match / không khớp / không thấy; không khớp thì vẽ lại; "không thấy" từ 2 mục trở lên thì đổi góc chụp |
| Thang khắt khe ba góc | giữ nguyên của LINHX | giữ |

**Phải hiệu chỉnh ngưỡng trước khi tin.** InsightFace: "Pick the threshold from a validation split, freeze it" và "never carry over a threshold across model versions" ([guide](https://insightface.ai/guides/choose-face-recognition-model-and-evaluate)); khoảng 0,30–0,45 trong guide là cho xác minh 1:1 ảnh thật. Việc làm: lấy ảnh Luna Mai, Trần AI, Cam Nhi, Gusto, Kai (LAB066 có đủ), lập cặp cùng người / khác người, chọn ngưỡng riêng. Số 0,45 ở trên là **điểm xuất phát chưa kiểm**.

## Bản vàng
Chưa tìm được mẫu top tier có giấy phép cho ảnh nhân vật người thật do AI. Mốc ngoài dùng cho *cấu trúc sheet*; mốc chất lượng dùng sheet LINHX đã duyệt.
1. `vang/fleischer-hound-dawg-1938.jpg`, model sheet Fleischer 1938, [Commons](https://commons.wikimedia.org/wiki/File:Color_Classics_-_Hold_It!_(1938)_-_Hound_Dawg_-_Character_Model_Sheet.jpg), "Public domain". Học: nhiều góc và biểu cảm trên một tờ, mỗi ô một ý.
2. `vang/altolin-reference-sheet.png`, [Commons](https://commons.wikimedia.org/wiki/File:Altolin_reference_sheet.png), CC BY-SA 4.0 (User:AltoHampton). Học: tờ tham chiếu hiện đại gom mặt, thân, màu.
3. Nội bộ: `D:\LINHX\LAB\LAB066-CASTING-GUONG-MAT\luna-mai\phat-trien\CHARACTER-SHEET.png`, và `cam-nhi`, `gusto`, `kai`. **Cần Linh xác nhận cái nào đã duyệt D4**; tôi chưa mở xem chất lượng.
4. Khuôn bố cục: laniameda hai hàng (4 toàn thân, 3 cận mặt), không phải mốc chất lượng.
Còn thiếu để đủ 3–5 mốc đáng tin: nhờ Linh chọn 1–2 sheet mình thích.

## Sửa vào skill nào
- `casting-mat`: thêm bước 3' (thẻ bất biến, master), thư mục `loai/`, bước đo ArcFace ở R2 và cổng C0, script `do_mat.py` (chỉ tính điểm).
- `phat-trien-nhan-vat`: giai đoạn G thêm điểm ArcFace (hiện chỉ có "lệch mặt -1.5 trần 6"); chấm spec bằng 3 trạng thái; BIBLE thêm Voice rules, Camera language; ghi thêm "hai bộ chuẩn dùng thường ngày" trong 20–30 món (mẫu ngoài khuyên hai bộ cho 90 ngày), không bỏ capsule.
- Prompt sheet: thử "photographic identity sheet / contact sheet" của laniameda khi nhân vật cần ra thật hơn.
- Không làm: LoRA/ComfyUI (LINHX vẽ bằng ChatGPT/Gemini).

## Rủi ro
- Giấy phép model InsightFace (phi thương mại): Linh quyết trước khi đưa vào quy trình công ty.
- Ngưỡng 0,45 chưa kiểm trên ảnh LINHX; ảnh cách điệu có thể rớt oan.
- Ảnh tham chiếu giống người thật: giữ bước Lens của skill.
- Chưa đọc nguồn tiếng Trung, Reddit, quy trình nội bộ studio top; `DR/DE-1.md` chờ kết quả.

## Nguồn
[đọc]: laniameda character-sheet và ai-avatar-realistic; inference-sh character-design-sheet; omer-metin art-consistency; mckruz comfyui-character-gen; Dreamina Master First; imaginary.app Character Bible; dev.to raxxostudios; Lumeflow; AlchemicaFaceMatch; InsightFace guide; eKYC thresholds; Commons 2 file; skill LINHX `skills/bo/linhx-casting/`; `LAB066\BAI-HOC.md`.
[chỉ thấy]: skills.sh wakqasahmed (nửa đầu); Wikipedia Model sheet; Reddit qua trang tổng hợp.
Chi tiết bảng Lấy/Bỏ: `NGOAI.md`.
