---
type: nghien-cuu
status: xong-nen
created: 2026-11-09
updated: 2026-11-09
wf: WF06-bai-viet-hay
---

# WF06 · Nghiên cứu nền: bài viết hay

## Kết luận 5 dòng
1. LINHX đã đo văn tiếng Việt kỹ hơn mọi skill ngoài đã đọc. Skill ngoài (blader/humanizer, stop-slop, aihxp/humanizer…) đều tiếng Anh, chỉ là danh sách mẫu câu để viết lại. Không cái nào đo theo mốc tác giả, cũng không cái nào kiểm sự thật.
2. Lỗ hổng lớn nhất nằm trong nhà. Ba thứ chưa vào `skills/` của repo, vẫn nằm ở LAB049: chuẩn BTV longform của chị Vân Anh (29/10), quy trình v3 "4 nguyên liệu" và `kiem_longform.py`. Skill `viet-bai-giong-viet` vẫn ở v0.3 (luật 19/10, 8 lỗi).
3. Thước chính phải là chuẩn Vân Anh (Linh chốt 9/11). Nhưng `DE-THREAD.md` vẫn ghi "Gemini: phản biện CQS/APS", còn `bien-tap-bai` vẫn chặn bài bằng CQS < 85 / APS > 30. Hai chỗ này phải sửa.
4. "0 câu bịa" cần cách làm của toà soạn lớn: một bản chú nguồn cho từng khẳng định (NYT bắt tác giả gửi "annotated copy"), cộng bước tách bài thành từng khẳng định nhỏ rồi tra từng cái (SAFE của DeepMind). LINHX đã có mã `[N1]`, nhưng chưa có bước tách khẳng định và chưa đếm câu sự kiện thiếu mã.
5. Ngưỡng "chữ máy ≤ 2/1000" trong đề chưa có định nghĩa, và nếu đếm bằng `kiem_longform.py` thì chính bài của Linh cũng trượt. Bản Vân Anh tự sửa có 3,6 câu dính cờ trên 1.000 chữ. Trong 8 bài Linh đã đăng, có 6 bài trên 2 câu dính cờ/1.000 chữ. Ngưỡng phải hiệu chuẩn trên bản vàng.

## Quy trình đề xuất (giữ luồng Vân Anh, gắn thêm cổng đo)
| Bước | Việc | Ai | Ra |
|---|---|---|---|
| B0 | Phiếu 4 nguyên liệu: chuyện của Linh, chuyện ví dụ, quan điểm (1 câu), fact có nguồn. Ô nào trống thì dừng, ghi `[CẦN LINH]` | Linh (ô 1–3), máy (ô 4) | `00-nguyen-lieu.md` |
| B1 | Kiểm ý: mỗi ý thành câu hỏi kiểm được, gắn nhãn đúng / sai / một phần / chưa ai biết. Subagent tách ngữ cảnh làm | Claude/agy | `03b-kiem-y.md` |
| B2 | Linh viết nháp gạch đầu dòng (bài 2.000 chữ thì nháp ≥ 1.000 chữ, theo lời chị Vân Anh) | Linh | `03-nhap.md` |
| B3 | Làm mượt từng gạch, không thêm chuyện, số, ẩn dụ. Kèm mục "Cố ý giữ" và "Kiểm nghĩa" (học từ aihxp) | agy | `04-ban-muot.md` |
| B4 | Biên tập 6 lượt tách ngữ cảnh (`bien-tap-bai`), lấy chuẩn VA 29/10 làm hồ sơ chính | Claude chấm, model khác người viết | `PHIEU-BIEN-TAP.md` |
| B5 | Bản chú nguồn: mỗi khẳng định một dòng (câu, mã, link, trích nguyên văn nguồn), rồi tra lại kiểu SAFE | subagent khác | `chu-nguon.md` |
| D4 | Chị Vân Anh biên tập; Linh duyệt | Vân Anh, Linh | bản giao + cặp trước/sau → `hoc-tu-ban-sua` |

D2 (chọn hướng) đặt sau B1: Linh chọn quan điểm và ý giữ, không nhìn tên nhánh.

## Máy đo + ngưỡng (rẻ trước, đắt sau)
| # | Đo | Cách chạy | Ngưỡng đạt | Ghi chú |
|---|---|---|---|---|
| M1 | Câu sự kiện có mã nguồn | `cham_cau.py` cờ `thiếu-mã-nguồn` + `kiem_nhap.py` (số lạ) | 100% có mã; 0 số lạ | đã có |
| M2 | Khẳng định không được nguồn đỡ | B5: tách khẳng định, tra từng cái (chỉ dùng kho nguồn của bài, không tìm Google) | 0 "Không đỡ"; mọi "chưa ai biết" phải viết thành ý kiến | cần viết; mượn khung SAFE |
| M3 | Giọng | `kiem_van.py` + `cham_cau.py` (chạy với `-X utf8` trên Windows) | câu TB trong dải 7 bài (20–38; trung vị 27); câu > 35 từ ≥ 10%; hai vế ≤ 5% | đã có; bản VA ra câu TB 28,5 |
| M4 | Cờ văn máy theo chuẩn VA | `kiem_longform.py` (LAB049) | ≤ trung vị bản vàng, tạm ≤ 3 câu dính cờ/1.000 chữ; 0 cờ mức chặn | thay "≤ 2/1000"; xem số dưới |
| M5 | Chấm từng câu | `cham-tung-cau` + `tong_hop_cham.py` | GIỮ ≥ 25%, SỬA ≤ 10%, CẮT 0 | đã có, hiệu chuẩn 19/10 |
| M6 | Chấm mù theo checklist VA (mục 8, 12 ô) | 2 giám khảo khác model, không thấy lý do của thợ; trộn bài thợ với bản vàng V1, che tên | ≥ 11/12 ô; giám khảo không chỉ ra được bài nào là bài máy (`hieu-chuan` trước) | cần prompt chấm |
| M7 | Vân Anh | đếm chỗ chị sửa tay / comment | 0 lỗi chặn; ≤ 15 chỗ sửa/bài (mốc vòng 2: 50 chỗ) | Linh chốt số |

Số đo bằng `kiem_longform.py`, chạy hôm nay (số câu dính cờ trên 1.000 chữ): bản Vân Anh sửa 3,6 · vnexpress 2017: 1,9 · dantri 2024-01: 2,2 · dantri 2024-03: 1,3 · dantri 2025-05-02: 2,5 · dantri 2025-05-30: 6,1 · dantri 2025-07: 4,3 · dantri 2026-01: 9,4 · essay 2026-04: 2,7. Chính bản Vân Anh cũng dính hai cờ toàn bài: một tiêu đề "Kết luận" và OPC lẫn OCP. Vậy máy chỉ cắm cờ, không tự đánh trượt (đúng như ghi chú trong script).

## Bản vàng (trong `vang/`, xem `vang/README.md`)
- V1. Bản chị Vân Anh tự tay sửa vòng 2: "Công ty trách nhiệm hữu hạn, mệt mỏi vô hạn" (1.887 từ). Đây là thước sát nhất, vì người chấm D4 tự viết ra.
- V2. vnexpress 2017-12-02 "Thay thế hay sửa chữa": viết trước thời AI tạo sinh, 1,9 cờ/1.000 chữ.
- V3. dantri 2024-01-31 "Ngành công nghiệp nói đạo lý": mở bằng hành động của người đọc, câu dài chảy.
- V4. dantri 2024-03-22 "Lắng nghe mạng xã hội": ít cờ nhất (1,3/1.000 chữ), câu TB 38.
- Chưa dùng làm vàng: dantri 2026-01-02 (9,4 cờ) và 2025-05-30 (6,1 cờ). Bài 2025-05-02 có câu "Một báo cáo gần đây cho thấy", chính là kiểu câu skill `viet-bai` cấm. Đề nghị bỏ hai bài đầu khỏi `moc-giong.json`, hoặc Linh xác nhận đó là văn tay.
- Mẫu ngoài: không lấy bài báo ngoài làm vàng giọng. Lấy cách làm (NYT bản chú nguồn) làm vàng quy trình.

## Sửa vào skill nào, sửa gì
1. `bo/linhx-bien-tap/ho-so-bien-tap/van-anh/`: chép `quy-tac-bien-tap-longform-BTV.md` và `prompt-BTV-AI-longform.md` (29/10) vào. Nâng `LUAT.md` từ 8 luật lên đủ 8 mục chuẩn. Ghi rõ đây là hồ sơ chính.
2. `bo/linhx-viet-giong-viet/skills/viet-bai-giong-viet`: lên v0.4. Thêm B0 phiếu 4 nguyên liệu của v3, mục "Cố ý giữ" + "Kiểm nghĩa" (bắt suy luận mềm: nhân quả, "phần lớn thời gian…" mà nguồn không nói), và luật "chỉ thêm thái độ với điều nguồn đã nói, không thêm sự kiện".
3. `bo/linhx-bien-tap/skills/bien-tap-bai`: thay cổng "CQS < 85 / APS > 30" bằng checklist VA mục 8 (M6). Thêm `kiem_longform.py` vào lượt 0. Thêm lượt bản chú nguồn (M2).
4. `scripts/cham_cau.py` (cả các bản chép): thêm `sys.stdout.reconfigure(encoding='utf-8')`, vì trên Windows script đang chết ở lệnh `print`.
5. `DE-THREAD.md` WF06: đổi dòng máy đo theo bảng trên. Bỏ "Gemini: phản biện CQS/APS"; Gemini chỉ còn làm giám khảo mù thứ hai.
6. `viet-bai` (7 trạm) và `new-article` (9 bước) chồng việc với luồng Vân Anh. Ghi rõ luồng VA là luồng chính cho bài báo; `new-article` chỉ dùng tìm tứ.

## Rủi ro
- Mốc giọng 7 bài có thể lẫn văn có AI hỗ trợ (năm 2025–2026), nên đo "giống Linh" có thể kéo bài về phía văn máy.
- Giám khảo LLM chấm lệch (Linh đã ghi nhận 9/11). Phải qua `hieu-chuan` trên cặp V1 với bản máy trước khi tin điểm.
- Luật chống văn AI hết hạn theo phiên bản model (LAB080: Claude hiện tại không dính 15 nhận xét tiếng Anh phổ biến). Danh sách mẫu phải ghi ngày và model.
- Gỡ dấu vết máy kiểu "đổi chữ" chỉ dời vết sang chỗ khác (aihxp). Cái cần sửa là độ đều của câu và của ý, không phải danh sách từ.
- M2 tốn subagent; giới hạn trong kho nguồn của bài để không tốn tìm kiếm.

## Nguồn
- [đọc] blader/humanizer, SKILL.md v3.1.0, 66.639 sao: https://github.com/blader/humanizer. Câu trích nguyên văn: "Do not add a fact, name, number, date, quote, or citation unless it comes from the source or the user."
- [đọc] aihxp/humanizer, SKILL.md v1.3.1: https://github.com/aihxp/humanizer. Câu trích nguyên văn: "The reason AI prose reads as AI is not its vocabulary. It is its uniformity".
- [đọc] hardikpandya/stop-slop, 18.748 sao: https://github.com/hardikpandya/stop-slop. Thang 5 chiều × 10, "Below 35/50: revise."
- [đọc] jpeggdev/humanize-writing, 8 lượt sửa: https://github.com/jpeggdev/humanize-writing
- [đọc] cdeistopened/skill-stack (writing-style, ghostwriter, voice-analyzer): https://github.com/cdeistopened/skill-stack
- [đọc] majiayu000/claude-skill-registry-data (anti-ai-writing, anti-ai-validator tiếng Hàn): https://github.com/majiayu000/claude-skill-registry-data
- [đọc] google-deepmind/long-form-factuality (SAFE): https://github.com/google-deepmind/long-form-factuality. README ghi SAFE "roughly 72% agreement with human raters".
- [đọc] sam-paech/slop-forensics: https://github.com/sam-paech/slop-forensics (LAB080 đã đọc code; `tu_may.py` của LINHX làm theo cách này)
- [đọc] errata-ai/write-good, errata-ai/proselint (gói luật Vale): https://github.com/errata-ai/write-good
- [đọc] NYT Opinion Guest Essays: https://thenewyorktimeshelpcenter.helpjuice.com/115014809107-New-York-Times-Opinion-Guest-Essays. Câu trích nguyên văn: "Before we publish your article, it must be fact-checked."
- [đọc] Wikipedia: Signs of AI writing: https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing. Câu trích nguyên văn: "Do not solely rely on artificial intelligence content detection tools".
- [chỉ thấy] The Economist Style Guide, sáu luật Orwell (qua nguồn thứ cấp): https://webarchive.library.unt.edu/web/20130114104813/http://www.economist.com/styleguide/introduction
- [chỉ thấy] analyticsvidhya top 5 skill viết; playbooks.com; skillsmp (trang tổng hợp, đã đọc thẳng repo gốc)
- [đọc] Nội bộ: LAB049 `05_quy-tac-bien-tap-longform-BTV.md`, `quy-trinh-longform-v3/QUY-TRINH.md`, `kiem_longform.py`, `ban-van-anh-sua-round-2.md`; LAB080 `OVERVIEW.md`, `refs/GHI-CHU-REPO.md`; repo `skills/bo/linhx-viet-bai`, `linhx-viet-giong-viet`, `linhx-bien-tap`.
- Không tìm được quy định gửi bài của VnExpress Góc nhìn và Dân trí Tâm điểm trên mạng: đã viết đề DR-1.
