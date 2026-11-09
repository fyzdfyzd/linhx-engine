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

## Bổ sung vòng 2 (9/11/2026)

### Đã lấp những mục vòng 1 tự khai mỏng
- **Bản vàng đọc trang đầu (V1, V3)**: đã đọc tiếp trang phương pháp thật.
  - Reuters DNR 2025, trang Methodology (https://reutersinstitute.politics.ox.ac.uk/digital-news-report/2025/methodology): "Research was conducted by YouGov using this online questionnaire"; ngày thu: "from the middle of January to the end of February 2025"; mẫu: "Samples were assembled using nationally representative quotas for age, gender, and region in every market."; trọng số: "The data in all markets were weighted to targets based on census/industry-accepted data."; giới hạn tự khai: "differences of +/- 2 percentage points (pp) or less are very unlikely to be statistically significant and should be interpreted with a very high degree of caution" và "online samples will tend to under-represent the news consumption habits of people who are older and less affluent". Học được: một bản vàng tốt **tự nêu giới hạn của mình ngay trong phần phương pháp**; mốc này kiểm được bằng mục "Điều chưa biết" của bản viết. (Nguyên văn do WebFetch trích; đã tải thêm trang về `vong-2/thu-cong3/tep-tai/N1.html`, mã 200.)
  - Trang tóm tắt cùng báo cáo ghi: "based on data from six continents and 48 markets, including Serbia for the first time" (https://reutersinstitute.politics.ox.ac.uk/digital-news-report/2025/dnr-executive-summary).
  - Pew "Our Methods" (https://www.pewresearch.org/methods/): ngoài câu "committed to meeting the highest methodological standards" còn có đội riêng: "International Survey Methods Team … ensures that all cross-national and multicultural projects we conduct continue to meet the highest standards of data quality and representativeness". Trang này **không** có câu nào về quy trình kiểm lại hay phản biện (WebFetch báo "does not contain verbatim statements" về peer review); nên chỉ dùng V3 học cách tách đội phương pháp khỏi đội viết, không dùng làm mốc kiểm trích.
- **daymade/deep-research, danh sách `references/` chưa đọc từng tệp**: đã đọc `quality_gates.md` và `source_accessibility_policy.md` (chép sẵn ở `_refs/WF09/daymade_claude-code-skills/deep-research/references/`). Lấy:
  - Nguyên văn: "Source counts, domain counts, source-type percentages, citation density, and word counts are diagnostics. They may reveal thin work, but they never prove coverage or quality by themselves." ⇒ ngưỡng "≥ 60% nguồn tầng A/B" của cổng 3 chỉ nên là **chẩn đoán**, không là điều kiện đạt. (Đề xuất sửa: đổi lỗi thành cảnh báo.)
  - Gate 3 "Original readback": "Every load-bearing claim, conflict, exact number/date, and quotation was checked in the original" ⇒ khớp thiết kế bước 2 và 4.
  - "Evidence independence: Repeated reports derived from one disclosure, dataset, study, interview, or sponsor are grouped as one family" ⇒ cổng 3 hiện đếm số nguồn (P0 cần ≥ 2 nguồn) mà không gộp nguồn cùng gốc; đề xuất thêm cột `ho_bang_chung` để hai bài cùng trích một số liệu không tính là hai nguồn.
  - Mẫu chống bịa: "URL or identifier was never retrieved → Remove it"; "Number is more precise than the original → Use the original precision".
  - Chính sách riêng cho nguồn nội bộ của Linh: bốn trạng thái `internally-established / externally-corroborated / conflicted / externally-unknown`; "Do not upgrade it to external validation merely because the user authorized access."

### Mục vòng 1 chưa lấp được
- **WF14 / ArcFace**: nằm ngoài WF09, không đụng (đề bài vòng 2 nhắc WF14 nhưng thư mục làm việc là WF09).
- **Ngưỡng 100% / ≥ 90% vẫn là đề xuất của mình**, chưa tìm được nguồn ngoài đặt sẵn con số. Thứ duy nhất có thêm là lập luận của daymade ở trên (số đếm chỉ là chẩn đoán). Giữ nguyên, hiệu chỉnh bằng vòng 1.
- Nguồn tiếng Việt, bài người làm nghề trên X/LinkedIn/Reddit: vẫn nằm ở `DR/DE-1.md` (chưa có kết quả).

### Thử máy đo trên mẫu (lệnh và kết quả thật)
Mẫu: `vong-2/thu-cong3/` — 2 trang đã tải bằng `curl` (Reuters Methodology, Pew Our Methods, đều mã 200), 4 bằng chứng: E1–E3 là câu trích nguyên văn từ hai trang, **E4 do mình bịa có chủ đích** ("All samples were verified independently by Ipsos with a 97% response rate").

1. Cổng 3 hiện có của LINHX:
   `python D:\LINHX\skills\plugins\linhx-report\scripts\report.py cong . 3` (chạy trong `vong-2/thu-cong3`, `PYTHONUTF8=1`).
   Kết quả: `== Cổng 3 · Nghiên cứu, sổ nguồn: ĐẠT` — `2 nguồn, 4 bằng chứng`, `nguồn tầng A/B: 100%`, mã thoát 0. **Cổng cho qua cả câu trích bịa E4.** Xác nhận chỗ hở vòng 1 nêu: cổng chỉ kiểm có trường `trich` khác rỗng và nguồn có trong CSV (`report.py` dòng 289).
2. Máy kiểm trích đề xuất (`vong-2/thu-cong3/kiem_trich.py`, mình viết, ~20 dòng, chỉ đọc tệp đã tải, chuẩn hoá khoảng trắng/dấu nháy/thẻ HTML):
   `python kiem_trich.py .`
   Kết quả: `KHỚP E1`, `KHỚP E2`, `KHỚP E3`, `SAI E4`; `3/4 khớp nguyên văn · đạt=False`, mã thoát 1. **Bắt đúng trích bịa, không báo nhầm trích thật.**
3. Giới hạn của lần thử: mẫu rất nhỏ (4 bằng chứng, 1 câu bịa) nên chỉ chứng minh máy **chạy được và phân biệt được**, chưa đo tỉ lệ bắt sót/báo nhầm. Chưa thử trích đúng chữ nhưng sai ý (đã ghi ở Rủi ro: cần tầng 3 chấm mù). Chưa thử bản `.pdf`. Chưa chạy `--kiem-link`. Không dùng Chrome, không chạy mã tải về.
4. Lưu ý chạy: trên máy này ổ C: hết chỗ (0 byte trống), mình đặt `TMP/TEMP` về `D:\LINHX\WF-NC\_refs\WF09`; Windows mặc định bảng mã cp1252 làm `report.py` lỗi in tiếng Việt nếu không đặt `PYTHONUTF8=1` (lỗi riêng của console, không phải của cổng). Nên ghi vào hướng dẫn chạy của `linhx-report`.

### Việc nên làm tiếp (từ kết quả thử)
- Đưa logic `kiem_trich.py` vào `cong_3` thành **lỗi** (thêm cột `tep_tai` vào `03-nguon.csv`); mẫu ở `vong-2/thu-cong3/` dùng làm test hồi quy (E4 phải luôn bị bắt).

### Số liệu ngoài đầu tiên cho ngưỡng (https://deepresearch-bench.github.io, đọc 9/11/2026 qua WebFetch)
- Định nghĩa: "Citation Accuracy (C. Acc.)" là độ chính xác gán nguồn; "Effective Citations (E. Cit.)" đo khả năng thu thông tin.
- Số tự khai trên trang: Perplexity Deep Research có "highest Citation Accuracy (90.24%)"; Gemini-2.5-Pro Deep Research tổng RACE 48.88, OpenAI Deep Research 46.98; RACE đầy đủ khớp người chấm "72.56%", còn hai người chấm với nhau là "68.44%".
- Ý nghĩa cho ngưỡng: ngay cả tác tử tốt nhất trên bảng cũng chỉ ~90% trích dẫn được xác nhận khi **LLM chấm ý nghĩa**. Vì vậy: (a) ngưỡng **100% chuỗi con nguyên văn** của mình là phép đo khác, rẻ và cứng (đã chứng minh chạy ở phần thử trên), không so trực tiếp với 90,24%; (b) ngưỡng "VERIFIED ≥ 90%" của chấm mù có cơ sở đối chiếu: ngang mức tốt nhất đã công bố, nên **không nên đặt cao hơn** khi chưa có dữ liệu LINHX; (c) độ tin của máy chấm ~72% so với người ⇒ giữ Linh ở D4, không để máy chấm quyết một mình. Đây vẫn là lập luận, chưa phải ngưỡng do nguồn đặt.
