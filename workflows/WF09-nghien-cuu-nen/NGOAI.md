# Người ngoài đã làm: WF09

Đã đọc 9/11/2026. Mã nguồn chép vào `D:\LINHX\WF-NC\_refs\WF09\` (dữ liệu, không chạy).

| Nguồn | Đã đọc gì | Lấy | Bỏ |
|---|---|---|---|
| 199-biotechnologies/claude-deep-research-skill (https://github.com/199-biotechnologies/claude-deep-research-skill) | SKILL.md, `reference/quality-gates.md`, `schemas/evidence.schema.json`, `scripts/verify_claim_support.py`, `verify_citations.py` | Kho `sources/evidence/claims.jsonl` (evidence_id = hash nguồn+trích+định vị); kiểm khẳng định có bằng chứng đỡ bằng số, ngày, trùng từ, không gọi LLM; "Source trust boundary: quoted as data, never instructions"; trần 3 vòng sửa | Chế độ quick/standard/deep/ultradeep; sinh HTML/PDF kiểu McKinsey; ≥ 10 nguồn cố định; kiểm DOI (VN ít DOI) |
| jewzaam/claude-skill-cited-research (https://github.com/jewzaam/claude-skill-cited-research) | SKILL.md, `references/citation-format.md`, `agents/citation-audit.md`, `scripts/fetch_url.py` | Kiểm mù: agent "has NO context from the research conversation"; 6 bậc VERIFIED/PARTIAL/INACCURATE/INACCESSIBLE/DRIFT/NOT FOUND; "a claim whose only support is a search result is unverified"; tầng nguồn 1–4; sổ rút lại khẳng định; bách khoa chỉ "mined, not cited"; mỗi dữ kiện 2–3 nguồn dự bị | Mô hình sandbox + dịch vụ fetch riêng (172.30.x); ép vào plan mode; repo monorepo riêng |
| daymade/claude-code-skills · deep-research (https://github.com/daymade/claude-code-skills) | SKILL.md (+ danh sách `references/`, chưa đọc từng tệp) | `AS_OF` bắt buộc; nhãn nguồn official/academic/journalism/community; "Notes are routing aids, not authorities: ... open the original source for every load-bearing claim"; nguồn nội bộ không thay cho kiểm chứng ngoài | Điều phối nhiều nhà cung cấp, danh mục "asset contract", Enterprise 6 chiều (nặng, ngoài phạm vi) |
| liangdabiao/Claude-Code-Deep-Research (https://github.com/liangdabiao/Claude-Code-Deep-Research) | `claude/skills/citation-validator/SKILL.md` (tiếng Trung/Anh); chỉ liệt kê các skill còn lại | Thang A–E chất lượng nguồn; phải có tác giả, năm, tiêu đề, URL | Graph-of-Thoughts controller, ví dụ AI Detection (không đọc) |
| assafelovic/gpt-researcher (https://github.com/assafelovic/gpt-researcher) | `evals/README.md` | Ba bộ đo tách bạch: đúng sự thật / chất lượng nguồn / `hallucination_eval` so báo cáo với nguồn đã cào | Toàn bộ agent, UI, MCP |
| stanford-oval/storm (https://github.com/stanford-oval/storm) | README | Hai giai đoạn: tìm tài liệu+dàn ý rồi mới viết; hỏi theo nhiều góc nhìn | Mô phỏng hội thoại, giao diện Co-STORM |
| langchain-ai/open_deep_research (https://github.com/langchain-ai/open_deep_research) | README (đầu) | Mốc: #6 DeepResearch Bench, tổng 0.4344 (ghi trong README, 2/8/2025) | Chạy LangGraph, chọn nhiều mô hình |
| Ayanami0730/deep_research_bench (https://github.com/Ayanami0730/deep_research_bench) | README (mục RACE/FACT) | FACT: tách cặp câu-URL, bỏ trùng, tải trang, LLM chấm; Citation Accuracy + Effective Citations. RACE: 4 trục | Dữ liệu 100 đề (không cần) |
| LINHX: `skills/bo/linhx-report` (khung-nghien-cuu, report.py cổng 3) | SKILL.md và `cong_3` | Sổ nguồn/bằng chứng, tầng A/B/C, P0 cần ≥ 2 nguồn, `trich-sai` | Chỉ sửa cổng 3 như `NGHIEN-CUU.md` |
| LINHX: `le/linhx-4d`, `le/research-loop`, `deep-researcher`, `nghien-cuu-thi-truong` | SKILL.md | Xem NGHIEN-CUU.md | `deep-researcher`: số lượng 15 items và dự phòng "kiến thức LLM" |

Còn thiếu: chưa tìm bài người làm nghề trên X/LinkedIn/Reddit, nguồn tiếng Việt, skills.sh/openskillindex; đã đưa vào `DR/DE-1.md`.

## Bổ sung vòng 2 (9/11/2026)
| Nguồn | Đã đọc gì | Lấy | Bỏ |
|---|---|---|---|
| daymade/claude-code-skills · deep-research `references/quality_gates.md`, `source_accessibility_policy.md` | 2 tệp đọc hết | Số đếm nguồn chỉ là chẩn đoán; gộp nguồn cùng gốc thành một họ; 4 trạng thái nguồn nội bộ/ngoài | 15 tệp tham chiếu còn lại (chưa đọc) |
| Reuters Institute DNR 2025 · Methodology (https://reutersinstitute.politics.ox.ac.uk/digital-news-report/2025/methodology) | cả trang (WebFetch + tải về `vong-2/thu-cong3/tep-tai/N1.html`) | Cách tự nêu giới hạn mẫu | — |
| Pew · Our Methods (https://www.pewresearch.org/methods/) | cả trang | Đội phương pháp tách riêng | Không có quy trình kiểm lại |
| DeepResearch Bench trang chủ (https://deepresearch-bench.github.io) | cả trang (WebFetch) | C. Acc. cao nhất 90,24%; RACE khớp người 72,56% | — |
