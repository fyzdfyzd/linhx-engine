# Người ngoài đã làm: WF11

Cập nhật 9/11 (máy WF-NC). Code clone ở `_refs\WF11\src\` (dữ liệu, không chạy). LAB018 đã đọc 30 repo hồi 9/10 (`D:\LINHX\LAB\LAB018-GRANT-WRITER\01-NGHIEN-CUU-NEN.md` và `refs\repos\`); nguồn đó dùng lại, không đọc lại.

| Nguồn | Link | Đã đọc gì | Lấy | Bỏ |
|---|---|---|---|---|
| darylalim/grant-writer-agent [đọc] | https://github.com/darylalim/grant-writer-agent | `skills/rfp-decomposition/SKILL.md`, `evals/README.md`, `src/prompts.py` (marker, phân cấp lỗi) | Bóc call ra `requirements.md` (trích nguyên văn + số trang, `MET/NOT MET/UNKNOWN`, một `NOT MET` là dừng); `[NEEDS INPUT: câu hỏi]` thay số bịa; lỗi BLOCKING/SUBSTANTIVE/MINOR; eval chấm bằng code là chính, LLM chấm chỉ phần code không làm được; ca "dương tính" đối trọng ca từ chối | App LangGraph/Streamlit; cả hạ tầng eval LangSmith |
| MaxGiu67/grantwriter-studio [đọc] | https://github.com/MaxGiu67/grantwriter-studio | `skills/gw-review/SKILL.md`, `gw-fit/SKILL.md` | Phản biện 3 lượt: chấm lệch tiêu chí, soi điểm yếu, rồi mới đánh bóng; trần 2 vòng; chấm fit trước khi viết (go/no-go) | Chỉ Horizon Europe tiếng Ý; không có license rõ nên chỉ học ý |
| jiankang1991/nsfc-benzi-audit [đọc] (MIT) | https://github.com/jiankang1991/nsfc-benzi-audit | `SKILL.md`, `README.md`, `evals/README.md`, `evals/craft/rubric.md` | Bộ bài thử có **bẫy hai chiều**: bản yếu cài lỗi + bản mạnh cài "bẫy báo sai"; chấm mù cùng thang; ghi `commit`, sha256 fixture, chấm khác họ model | Nội dung riêng NSFC; thang Trung Quốc |
| mohitagw15856/pm-claude-skills `rfp-response` [đọc] (MIT) | https://github.com/mohitagw15856/pm-claude-skills | `exports/windsurf/pm-gov/rfp-response/rfp-response.md` | Ma trận tuân thủ làm xương sống; mỗi tiêu chí chấm một mục, bằng chứng thay tính từ; kiểm hình thức | Mỏng, không có đo, không có lỗi bẫy |
| seb1n/awesome-ai-agent-skills `proposal-generation` [đọc] (MIT) | https://github.com/seb1n/awesome-ai-agent-skills | `sales/proposal-generation/SKILL.md` | Phân loại "must-have / nice-to-have", cờ rủi ro bị loại; tóm tắt điều hành 250–400 từ nói bằng lời khách | Số liệu mẫu bịa (ví dụ 34%, 22%) không nguồn; không có kiểm số |
| KurtLehnardt/granted [đọc lướt] | https://github.com/KurtLehnardt/granted | README, cấu trúc thư mục | Không lấy gì: là công cụ tìm cơ hội tài trợ Mỹ (trùng LAB013), không viết hồ sơ | Toàn bộ |
| Shipley / GovEagle: pink-red-gold [đọc] | https://www.shipleywins.com/blogs/color-team-reviews · https://www.goveagle.com/blog/pink-red-gold-team-reviews-playbook | Hai trang | Ba lượt rà theo mốc hoàn thành bản nháp; Red Team chấm bằng bảng mirror tiêu chí bên mời; Gold chỉ xác nhận, cắt mốc 48–72 giờ trước hạn | Mô hình đội nhiều người (Linh làm một mình) |
| Enabel: Annex F1a / F2a (lưới chấm EuropeAid) [đọc, đã tải vào `vang/`] | https://www.enabel.be/app/uploads/2025/06/Annex-F1a.-ConceptNote_EVA_Grid_Annex.pdf | Toàn bộ lưới | Bước hình thức/điều kiện trước, rồi chấm 1–5 từng ý, có điểm sàn | — |
| Winrock RFA-6997-24-22 bản tiếng Việt [đọc, đã tải] | https://winrock.org/wp-content/uploads/2024/11/RFA-6997-24-22_Support-TEDP_VN_20241118_final.pdf | Mục tiêu chí đánh giá | Call VN thật có thang 100 điểm công khai | — |
| afrexai rfp-responder · grant-writer · travisjneuman grant-proposal-builder (từ đề) [chỉ thấy] | https://clawhub.ai/1kalin/afrexai-rfp-responder · https://smithery.ai/skills/travisjneuman/grant-proposal-builder | Chưa vào được trang trong phiên này | — | Chưa đánh giá |
| LAB018 (30 repo, 12 mẫu thiết kế) [đọc lại tóm tắt] | `D:\LINHX\LAB\LAB018-GRANT-WRITER\01-NGHIEN-CUU-NEN.md` | Toàn tệp | 12 mẫu thiết kế (call thành hợp đồng, sổ dữ kiện, ngân sách do code tính...) | Repo AGPL/không license: chỉ học ý |

## Chưa tìm được
- Mẫu proposal sự kiện/activation đã thắng (agency không công bố). Đã viết `DR/DE-1.md` hỏi thêm.
- Nguồn tiếng Trung đã nằm trong LAB018 (nsfc-benzi-audit, claude-bid-gen...).
