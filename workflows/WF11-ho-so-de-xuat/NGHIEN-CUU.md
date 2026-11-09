# Nghiên cứu nền WF11: hồ sơ đề xuất, tài trợ

Làm 9/11/2026. Đã đọc code thật 5 nguồn (darylalim, grantwriter-studio, nsfc-benzi-audit, rfp-response, proposal-generation) cộng 30 repo của LAB018 (đọc lại tóm tắt). Chi tiết: `NGOAI.md`. Chưa có kết quả Deep Research (`DR/DE-1.md` đã viết).

## Kết luận
1. Bên thắng hồ sơ không viết hay hơn mà **khớp bên mời hơn**: "Proposals lose on *compliance* far more than on quality" (rfp-response, https://github.com/mohitagw15856/pm-claude-skills). Mọi bước phải đi từ yêu cầu và thang chấm của bên mời, không từ khung của mình.
2. Ba thứ đáng mượn nhất: (a) bóc call thành `requirements` trích nguyên văn + số trang, một điều kiện `NOT MET` là dừng (darylalim); (b) `[NEEDS INPUT: câu hỏi]` thay cho số bịa; (c) lỗi xếp BLOCKING / SUBSTANTIVE / MINOR.
3. Người làm nghề rà hồ sơ **ba lượt theo mốc**: Pink (20–40% bản nháp, kiểm cấu trúc), Red (80–90%, chấm theo bảng mirror tiêu chí bên mời), Gold (xác nhận, không sửa, cắt 48–72 giờ trước hạn). Không ai đo "đề bài tới bản gửi" công khai: mốc ≤ 1 ngày của Linh là mốc riêng.
4. Máy đo tốt nhất đã có người làm: chấm bằng **code trước, LLM chỉ chấm phần code không làm được**, và bộ bài thử có **bẫy hai chiều** (bản cài lỗi phải bị bắt, bản sạch không được bị báo giả) (nsfc-benzi-audit, darylalim).
5. LINHX đã có kiến thức nhưng thiếu **dây chuyền đo**: chưa có ma trận điều kiện loại, kiểm số, chấm theo lưới call, sổ thắng/thua.

## Quy trình đề xuất
| Bước | Việc | Ai |
|---|---|---|
| 0 | Nhận đề bài, ghi giờ bắt đầu (đồng hồ máy đo) | agy |
| 1 | Bóc `requirements.md`: mục, giới hạn trang/ký tự, tiêu chí + điểm (nguyên văn, có trang), điều kiện loại `MET/NOT MET/UNKNOWN`, phụ lục. Có `NOT MET` thì dừng, hỏi Linh | agy; Claude kiểm |
| 2 | Go/no-go ngắn (điểm khớp, nguồn lực, giá) | Linh quyết |
| 3 | Dàn ý cấp 1 khớp 1-1 với tiêu chí; kiểm phủ bằng code | agy |
| 4 | Viết nháp; thiếu dữ kiện thì `[NEEDS INPUT: ...]`, gom vào `gaps.md`; giá và ngân sách do Linh/ code tính | agy |
| 5 | Pink: Claude chấm cấu trúc và phủ tiêu chí | Claude |
| 6 | Red: chấm theo lưới của call, **mù, khác họ model với người viết**, lỗi xếp 3 cấp, tối đa 2 vòng | Claude/Codex |
| 7 | Gold: chạy toàn bộ máy đo, Linh duyệt D4, gửi | Linh |
| 8 | Ghi thắng/thua + lời nhận xét bên mời vào `won-lost.csv` | Linh/agy |

## Máy đo + ngưỡng (đề xuất; số ngưỡng là của máy nghiên cứu, chưa Linh duyệt)
| Đo | Cách | Ngưỡng |
|---|---|---|
| Thời gian | giờ ở bước 0 tới giờ file gửi (mtime/git) | ≤ 24 giờ (mốc Linh) |
| Phủ yêu cầu | script: mỗi dòng "phải/shall/must" trong `requirements.md` có đoạn trả lời, tên mục | 100% (mốc Linh) |
| Điều kiện loại | `NOT MET` còn lại | 0 |
| Độ dài | đếm trang/ký tự theo luật call | ≤ giới hạn, mỗi mục |
| Số liệu | script rút số/năm/%, đối chiếu `facts.json` + nguồn | 0 số lạ; mọi `[NEEDS INPUT]` đã xử lý |
| Chấm giả lập | lưới của chính call (hoặc lưới mẫu Enabel khi call không công bố); chấm mù, khác họ model | tổng ≥ 70% (đề xuất), không tiêu chí nào dưới điểm sàn của call; lỗi BLOCKING = 0 |
| Máy chấm có đáng tin | bài thử: 3 bản yếu cài lỗi + 2 bản mạnh cài bẫy; | bắt ≥ 80% lỗi cài; ≤ 20% báo giả (mốc LAB018) |
| Thắng/thua | `won-lost.csv` mỗi hồ sơ | đủ cột, không thiếu hồ sơ nào |
Lưu ý: LLM chấm có tương quan yếu với người (nguồn LAB018: arXiv 2603.08281, 2603.14565, chưa tự xác minh) nên điểm chỉ là mô phỏng, phải ghi.

## Bản vàng (xem `vang/README.md`)
Lưới chấm Enabel F1a/F2a (đã tải), RFA tiếng Việt Winrock có thang 100 điểm (đã tải), cặp hồ sơ trúng + lời phê NIAID, hồ sơ công khai Wellcome [chỉ thấy]. **Thiếu mẫu proposal sự kiện thắng thật**: cần Linh đưa 1–2 bản ifAgent/Unikon.

## Sửa vào skill nào, sửa gì (so với `skills/`)
- `ho-so-tai-tro` (khung kiến thức, bước 2 chỉ nói "ma trận tuân thủ"): **thiếu** bóc requirements nguyên văn + số trang, trạng thái điều kiện loại, `[NEEDS INPUT]`, phân cấp lỗi BLOCKING/SUBSTANTIVE/MINOR, kiểm số bằng code, chấm mù, sổ thắng/thua. **Thừa** phần NSF/NIH/DOE/DARPA (đã ghi "bỏ qua"). Chưa có script.
- `proposal-studio` (viết cho sự kiện): **sai chỗ** ép dàn ý cố định 25 mục (cover → … → next steps) thay vì khớp tiêu chí bên mời; **thiếu** ma trận yêu cầu từ brief, bước chấm, đo thời gian, thắng/thua; **thừa nặng** cho đề tài trợ: mockup, ảnh ChatGPT, deck PPTX. Nên tách đường "tài trợ/thầu theo thang" khỏi đường "pitch sáng tạo".
- Việc cụ thể: thêm skill nhỏ `doc-call` (bước 1), `kiem-ho-so` (script phủ, số, độ dài), `phan-bien-ho-so` (Red mù, 3 cấp lỗi), và `won-lost.csv`. Vòng 1 làm với call TUVA; mượn ý, không chép code AGPL/không license.

## Rủi ro
- Nhà tài trợ siết dùng AI (NIH, theo LAB018, chưa tự xác minh): phải có người chịu trách nhiệm và khai báo khi call yêu cầu.
- Chấm bằng LLM dễ bới lỗi giả: luôn có bản sạch đối chứng.
- Không bịa đối tác, thư cam kết, số liệu; không nộp thay Linh.
- Không dùng `bid_variants.py`/`bid_similarity.py` của claude-bid-gen (né phát hiện trùng).
- Ngưỡng 70% và 80% chưa có bằng chứng ngoài LAB018; hiệu chỉnh sau vòng 1.

## Nguồn
[đọc] https://github.com/darylalim/grant-writer-agent · https://github.com/MaxGiu67/grantwriter-studio · https://github.com/jiankang1991/nsfc-benzi-audit · https://github.com/mohitagw15856/pm-claude-skills · https://github.com/seb1n/awesome-ai-agent-skills · https://www.shipleywins.com/blogs/color-team-reviews · https://www.goveagle.com/blog/pink-red-gold-team-reviews-playbook · https://www.enabel.be/app/uploads/2025/06/Annex-F1a.-ConceptNote_EVA_Grid_Annex.pdf · https://winrock.org/wp-content/uploads/2024/11/RFA-6997-24-22_Support-TEDP_VN_20241118_final.pdf · LAB018 `01-NGHIEN-CUU-NEN.md`
[chỉ thấy] https://www.niaid.nih.gov/grants-contracts/sample-applications · https://wellcome.org/research-funding/open-research-fund-project-proposals-submitted-wellcome · https://clawhub.ai/1kalin/afrexai-rfp-responder · https://smithery.ai/skills/travisjneuman/grant-proposal-builder
