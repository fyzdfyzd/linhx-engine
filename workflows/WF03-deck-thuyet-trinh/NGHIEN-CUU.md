# WF03 · Nghiên cứu nền: deck thuyết trình, chào khách

Ngày 9/11/2026. Máy Linh. Code clone ở `_refs/WF03/` (frontend-slides, ppt-master, anthropics/skills, claude-code-skills), coi là dữ liệu, không chạy.

## Kết luận
1. Skill LINHX (linhx-deck + vong-lap-slide) đã đi trước các skill công khai ở phần đo và chấm: đo tương phản trên nền thật, người chấm tách thợ ×3, xác minh lỗi, hoàn tác, trần vòng. Không viết lại, chỉ vá.
2. Thiếu rõ nhất ở **đầu vào** và **giữa đường**: chưa có cổng sớm sau 5 slide, D2 chưa dùng 3 bìa xem trước thật, chưa khai chế độ mật độ (nói / đọc).
3. Người ngoài có hai thứ đáng lấy: danh sách dấu hiệu "slide do AI làm" của Anthropic (đưa vào máy đo) và luật "lỗi lặp cùng kiểu là lỗi phương pháp" của ppt-master (sửa luật rồi mới dựng tiếp).
4. Chấm bằng bảng lỗi cụ thể tốt hơn chấm chung chung (SlideAudit), nhưng một người chấm máy vẫn dao động: giữ 3 phiếu + máy đo.
5. Bản vàng chưa tải được (cloud/máy này không lấy được ảnh từ Dribbble, Pinterest). Đã chọn 5 mốc, cần Chrome máy cty lấy ảnh vào `vang/`.

## Quy trình đề xuất
| Bước | Ai | Ghi chú |
|---|---|---|
| 0. Phiếu đầu vào: người nghe, quyết định muốn họ làm, chế độ mật độ nói/đọc | Claude | lấy ý daymade (10 câu có mặc định) + frontend-slides |
| 1. Ghost deck: chỉ tiêu đề hành động, đọc liền ra một lập luận | Claude (có sẵn) | tiêu đề ≤ ~90 ký tự, ≤ 2 dòng |
| 2. **D2**: 3 bìa xem trước thật (1 an toàn, 1 đậm, 1 tự thiết kế), che tên nhánh | Linh chọn | thay hỏi gu bằng lời |
| 3. Dựng 5 slide đầu | agy | khoá spec: màu, chữ, khoảng |
| 4. **Cổng sớm**: vls.py chấm 5 slide; lỗi lặp cùng kiểu thì sửa luật, không sửa từng trang | máy + Claude | mới, từ ppt-master |
| 5. Dựng phần còn lại | agy | |
| 6. Vòng lặp vls.py (≤ 3 vòng, ≤ 3 lỗi/lần) | máy + 3 người chấm | có sẵn |
| 7. Chấm "mắt mới" 3 giây | Claude máy cty | mới, từ Duarte |
| 8. **D4** | Linh | |

## Máy đo + ngưỡng
Giữ nguyên ngưỡng vls.py hiện có (tương phản 3:1 chữ ≥24px, 4.5:1 chữ nhỏ; chữ ≥ 20px; ≤ 3 cỡ chữ; ≤ 8 khối; ≤ 40 chữ; trống ≥ 45%; mỗi tiêu chí chấm ≥ 4; 3 phiếu lấy trung vị). Thêm:
- **Danh sách dấu hiệu AI** (kiểm tự động được): vạch dưới tiêu đề, sọc màu ở mép thẻ/mép slide, nền be/kem mặc định, một bố cục lặp liên tiếp. Đã có "vạch dưới tiêu đề"; thêm 3 cái còn lại.
- **Phép thử 3 giây**: người chấm xem slide 3 giây, viết ý chính, so với `diem_chinh`; lệch = lỗi nặng.
- **Bảng lỗi SlideAudit** (27 loại, 5 nhóm) nhét vào đề chấm.
- **Cổng sớm**: ≥ 2 slide trong 5 slide đầu dính cùng một mã lỗi → dừng, sửa luật.
- **Phiếu mất hiệu lực** khi đổi tài nguyên chung (màu, phông, lưới): chấm lại toàn bộ, không dùng phiếu cũ.
- Ngưỡng 3 phiếu và "≥ 4 mỗi tiêu chí" chưa có nguồn ngoài xác nhận, giữ vì Linh đã chốt; hiệu chỉnh bằng `hieu-chinh`.

## Bản vàng (mốc chấm; phải lấy ảnh bằng Chrome máy cty)
| # | Mẫu | Vì sao tốt | Trạng thái |
|---|---|---|---|
| 1 | Airbnb pitch deck 2009 (qua [Slidebean](https://slidebean.com/blog/startups/best-pitch-decks)) | mỗi slide một ý, chữ to, nhiều trống | [chỉ thấy] |
| 2 | Khuôn Sequoia (qua [Storydoc](https://www.storydoc.com/blog/sequoia-pitch-deck-examples)) | mạch chuẩn cho chào khách/vốn | [chỉ thấy] |
| 3 | Duarte, các deck mẫu ([glance test](https://www.duarte.com/resources/guides-tools/the-glance-test/)) | bài thử 3 giây | [đọc] phần thử, chưa tải deck |
| 4 | Mẫu tư vấn: [Slideworks 750 bài thật](https://slideworks.io/resources/750-real-consulting-presentations-from-mckinsey-deloitte-ey-and-more) | tiêu đề hành động, dòng nguồn | [chỉ thấy] |
| 5 | Deck Sakédemy chào VCB (LINHX, Linh OK 30/10) + BTMH Guideline 2026 | đúng brand, đã duyệt | nội bộ, chép vào `vang/` |
Việc cần làm: Linh (hoặc Claude máy cty) chọn 3–5 slide từ các mẫu trên, ≥ 4/5 theo 7 tiêu chí, lưu `vang/`.

## Sửa vào skill nào
- `linhx-deck/skills/dung-deck`: thêm bước 0 phiếu đầu vào (mật độ nói/đọc); cổng sớm 5 slide; slide kết là quyết định hoặc bước tiếp theo, không "Hỏi đáp?".
- `vong-lap-slide`: thêm 3 dấu hiệu AI vào máy đo; thêm bảng lỗi SlideAudit và phép thử 3 giây vào `references/cham-slide.md`; luật phiếu mất hiệu lực theo băm tài nguyên chung; lỗi màu brand đẩy lên cấp deck.
- D2: đổi sang 3 bìa xem trước thật.
- `anh-sang-slide`, `proposal-studio`: chưa thấy lý do sửa từ nghiên cứu này.
- **Bỏ/không nhận**: tự chấm bởi thợ (daymade), AI vẽ trọn slide thành ảnh (deer-flow; Linh bỏ 14/10), "mọi slide phải có hình" (trái luật tối giản).

## Rủi ro
- Nhiều nguồn là bài quảng cáo của hãng; chỉ tin phần có code.
- daymade ppt-creator đã bị tác giả rút (7/8/2026): chỉ học ý, không phụ thuộc.
- Số liệu PresentBench "khớp người hơn PPTEval" chưa kiểm.
- Bản vàng chưa có ảnh; vòng 1 không chấm "ngang mẫu" nghiêm được nếu thiếu.
- Chưa chạy Deep Research: 5+ nguồn đọc được đủ cho workflow này.

## Nguồn
[đọc] https://github.com/zarazhangrui/frontend-slides · https://github.com/hugohe3/ppt-master (skills/ppt-master/references/visual-review.md: "under-fixing beats oscillation") · https://github.com/anthropics/skills (pptx/SKILL.md: "NEVER use accent lines under titles — these are a hallmark of AI-generated slides") · https://github.com/icip-cas/PPTAgent · https://github.com/daymade/claude-code-skills · https://arxiv.org/abs/2508.03630 (SlideAudit) · https://www.duarte.com/resources/guides-tools/the-glance-test/ · https://deckary.com/blog/consulting-slide-standards
[chỉ thấy] https://arxiv.org/abs/2603.07244 (PresentBench) · https://slidebean.com/blog/startups/best-pitch-decks · https://www.storydoc.com/blog/sequoia-pitch-deck-examples · https://slideworks.io/resources/750-real-consulting-presentations-from-mckinsey-deloitte-ey-and-more · https://open-design.ai/blog/claude-ppt-skills/ · bytedance/deer-flow · MiniMax pptx-plugin · guizang-ppt-skill · PeterKalmstrom/claude-powerpoint-skill
