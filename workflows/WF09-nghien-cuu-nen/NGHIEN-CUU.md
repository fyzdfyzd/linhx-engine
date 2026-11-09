# WF09 · Nghiên cứu nền: kết quả nghiên cứu (9/11/2026)

## Kết luận
1. Lỗi gốc của WF09 ("agy bịa trích") là **không ai kiểm đoạn trích có thật nằm trong trang nguồn**. Các nguồn tốt đều tách ba việc: thu bằng chứng → viết → người/máy khác kiểm lại từng khẳng định với trang đã tải.
2. LINHX đã có khung tốt (`linhx-report`: sổ nguồn, sổ bằng chứng, `trich-sai`) nhưng cổng 3 chỉ kiểm link bằng HEAD và chỉ **cảnh báo**; không đối chiếu `trich` với nội dung trang. Đây là chỗ hở cần vá trước hết.
3. Máy đo chuẩn của ngành là FACT (DeepResearch Bench): trích cặp "câu khẳng định – URL", tải trang, chấm "nguồn có đỡ câu không"; hai chỉ số: độ chính xác trích dẫn và số trích dẫn hiệu quả. Dùng được ngay, không cần nghĩ lại.
4. Không tạo skill mới. Sửa 3 skill có sẵn (mục "Sửa vào skill nào"), bê thêm 4 thứ từ ngoài: kho bằng chứng bất biến, kiểm đỡ-câu kiểu 6 bậc, tách người kiểm khỏi người viết, sổ rút lại khẳng định.
5. Nghiên cứu sâu (số liệu VN, nguồn tiếng Việt) đã đẩy đề `DR/DE-1.md`; chưa có kết quả, không chờ.

## Quy trình đề xuất (ai làm)
| Bước | Việc | Ai |
|---|---|---|
| 0 | Hợp đồng: câu hỏi quyết định, ngày `AS_OF`, ranh giới, "bằng chứng nào sẽ lật kết luận" | Claude, Linh duyệt |
| 1 | Thu: mỗi nguồn tải về tệp (kèm URL, giờ, trạng thái OK/FAILED); mỗi bằng chứng = nguyên văn + định vị + id nguồn. Không viết kết luận | máy quét (`linhx-crawler`) + Gemini DR (rộng) |
| 2 | Kiểm máy: trích có nằm nguyên văn trong tệp đã tải; link sống; số/ngày có nguồn | script |
| 3 | Viết từ kho bằng chứng, mỗi câu mang id bằng chứng; chỗ chưa có nguồn ghi "chưa có" | agy |
| 4 | Kiểm mù: người kiểm không có hội thoại của người viết, chấm từng khẳng định VERIFIED / PARTIAL / INACCURATE / INACCESSIBLE / DRIFT / NOT FOUND, chép nguyên văn nguồn | Claude (phiên mới) |
| 5 | Tìm phản chứng có chủ đích; ghi vào mục "Điều chưa biết" | thợ riêng |
| 6 | D1 (Linh duyệt đề) và D4 (duyệt cuối); khẳng định bị bỏ ghi vào sổ rút lại | Linh |

## Máy đo + ngưỡng (rẻ → đắt)
| Tầng | Kiểm | Ngưỡng đạt |
|---|---|---|
| 1 tự động | mọi `trich` là chuỗi con nguyên văn (sau chuẩn hoá khoảng trắng/dấu) của tệp nguồn đã tải | **100%** (hụt 1 là rớt) |
| 1 | link mở được (GET, không chỉ HEAD), ghi mã trạng thái, ngày truy cập | **100%** sống; nguồn FAILED phải bị gỡ hoặc ghi INACCESSIBLE |
| 1 | mọi số và ngày trong bản viết có id bằng chứng trùng số (script đã có `kiem_so`) | 100% |
| 1 | tỷ lệ nguồn tầng A/B (có sẵn ở cổng 3) | ≥ 60% |
| 2 rubric | 4 trục RACE: đầy đủ, chiều sâu/insight, đúng yêu cầu, dễ đọc | chưa có số mốc của nguồn; **đặt tạm ≥ bản vàng −10%, hiệu chỉnh sau vòng 1** |
| 3 chấm mù | tỷ lệ khẳng định VERIFIED trên mẫu ≥ 30 khẳng định hoặc toàn bộ nếu ít hơn | VERIFIED ≥ 90%, INACCURATE = 0, PARTIAL được sửa hết trước D4 |
| 4 Linh | D1/D4 | không sửa lớn |

Các con số 100% / ≥ 90% / ≥ 60% là **ngưỡng đề xuất của mình**, riêng ≥ 60% lấy từ cổng 3 hiện có trong `report.py`; ba cái còn lại chưa có nguồn ngoài đặt sẵn, cần hiệu chỉnh bằng vòng 1.

## Bản vàng
Xem `vang/BAN-VANG.md` (4 mẫu: Reuters Institute DNR 2025, OECD Digital Economy Outlook 2024, Pew "Our Methods", bài kiểm của DeepResearch Bench). Chú ý: mới đọc trang giới thiệu, chưa đọc toàn văn; D1 Linh nên chọn lại mốc cho đúng đề NCT/thị trường VN.

## Sửa vào skill nào, sửa gì
- `linhx-report/scripts/report.py` cổng 3: (a) thêm cột `tep_tai` trong `03-nguon.csv` và kiểm `trich` ⊂ nội dung tệp (đổi từ cảnh báo sang **lỗi**); (b) `--kiem-link` dùng GET + ghi mã, mặc định bật; (c) thêm trạng thái `OK/FAILED`.
- `linhx-4d` (LAB105): thêm pha "kiểm mù" và nhãn VERIFIED/PARTIAL/…; hiện chỉ có "Bàng Thống chấm theo thang". Giữ luật "Claude không làm thợ", nhưng cho Claude làm người kiểm mù (đúng vai chấm).
- `research-loop`: giữ nguyên (đó là vòng thử nghiệm có phép đo khoá, khác việc nghiên cứu nguồn); chỉ trỏ sang đây để khỏi dùng nhầm.
- `deep-researcher` (linhx-viet-bai): ghi `source` không có nguyên văn lẫn định vị, tiêu chí "≥ 15 items" khiến thợ bịa cho đủ; bỏ số lượng, thêm `trich` nguyên văn + `tep_tai`, và dòng "không có web search thì dùng kiến thức LLM kèm disclaimer" phải đổi thành **dừng**.
- `nghien-cuu-thi-truong`: giữ; thêm ngày `AS_OF` và mức hạn dùng của từng loại số.
- Thêm vào `linhx_worker`: loại phiếu "kiem-mu-trich-dan" (chỉ đọc, không có lịch sử người viết).

## Rủi ro
- Chuỗi con nguyên văn không bắt được trường hợp trích đúng chữ nhưng sai ý ⇒ vẫn cần tầng 3 chấm mù.
- Trang động/cần đăng nhập/chặn bot không tải được (nguồn cited-research ghi 20–30% nguồn không vào được vào bất kỳ lúc nào): cần máy quét Chrome đã đăng nhập, không phải HEAD.
- FACT dựa vào LLM chấm; có thể sai, nên chỉ dùng như tầng sàng, không thay D4.
- Chưa biết đề NCT VN gốc: không đọc được định nghĩa "NCT" trong repo này (chưa kiểm LAB); đừng suy từ tên.
- Gemini DR có thể bịa link: mọi kết quả `DR/KQ-*.md` phải qua tầng 1 như mọi nguồn khác.

## Nguồn
[đọc] SKILL.md + `quality-gates.md` + `verify_claim_support.py` + `evidence.schema.json` của 199-biotechnologies/claude-deep-research-skill · [đọc] SKILL.md, `citation-format.md`, `agents/citation-audit.md`, `scripts/fetch_url.py` của jewzaam/claude-skill-cited-research · [đọc] SKILL.md của daymade/claude-code-skills/deep-research · [đọc] `skills/citation-validator/SKILL.md` của liangdabiao/Claude-Code-Deep-Research · [đọc] README + `evals/README.md` của assafelovic/gpt-researcher · [đọc] README của stanford-oval/storm, langchain-ai/open_deep_research, Ayanami0730/deep_research_bench · [chỉ thấy] https://deepresearch-bench.github.io (qua tìm kiếm; trang sống 200) · bản vàng: xem `vang/BAN-VANG.md`. Chi tiết đọc gì/lấy gì/bỏ gì ở `NGOAI.md`.
