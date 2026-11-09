# WF18 · Bổ sung vòng 2 (cloud, 9/11/2026)

Lấp các chỗ `NGHIEN-CUU.md` tự khai còn mỏng. Không sửa `NGHIEN-CUU.md`.

## Kết luận thêm (5 dòng)
1. **Không cần nhãn mới `nham_nguoi`.** `CHUAN-ABC-v1.md` (LAB036) mục 3 đã định nghĩa "Nhầm = thông tin của thực thể khác (trùng tên, đối thủ)" và A3 coi nhầm thực thể là cờ đỏ riêng. Chỉ cần thêm `nguoi_trung_ten` vào `person.json` để giám khảo có căn cứ gán Nhầm.
2. **Ngưỡng "điểm lệch ≤ 5" khi chạy lại: chỉ đạt khi mẫu lớn.** Mô phỏng (mục 2) cho thấy riêng nhiễu lấy mẫu đã cần khoảng 750 ô (25 câu × 10 lượt × 3 mô hình) mới đạt ở 95% lần chạy. Đề nghị: giữ ngưỡng ≤ 5 cho **tỉ lệ có mặt gộp** ở gói Sâu, ≤ 10 ở gói Chuẩn (25 × 5 × 3), và **không** chấm ổn định từng mô hình riêng.
3. **Phần dán tay giao diện là bắt buộc, không phải phụ.** Ba nghiên cứu độc lập 2026 cho thấy API và giao diện chỉ trùng 6–32% thương hiệu nêu ra và rất ít nguồn dẫn (mục 3). Báo cáo phải ghi từng câu lấy từ đường nào.
4. **Đã có mốc bên ngoài cho báo cáo người.** 5W/Everything-PR đã audit 5 engine cho 8 nhà sáng lập AI theo 5 tiêu chí; noyb có ca bịa tội cho người thật. Dùng làm mốc từng phần (mục 4), bản vàng thật vẫn là vòng 1 Linh duyệt.
5. **Việc sửa 30 ngày phải tách hai nhịp.** Câu trả lời có tra web đổi trong vài ngày đến vài tuần sau khi sửa nguồn; câu trả lời từ trí nhớ mô hình phải chờ bản mô hình mới (vài tháng). Báo cáo đo lại sau 30 ngày chỉ hứa thay đổi ở chế độ tra web.

## 1. Lỗ "nhầm người"
- Nhãn Nhầm có sẵn ([đọc] `/mnt/project-files/LAB036-BRAND-CHECK-AGENT/CHUAN-ABC-v1.md` dòng 20, 46, 53).
- Thêm vào `person.json`: `nguoi_trung_ten: [{ten, nghe, noi, link}]`, và câu gài trùng tên trong bộ câu ("[Tên] có phải là [nghề của người trùng tên] không?").
- Ca lỗi mẫu cho bộ thử: noyb kiện OpenAI 20/3/2025, ChatGPT bịa ông Arve Hjalmar Holmen giết hai con, lẫn chi tiết thật (số con, giới tính, quê). Nguyên văn: "The GDPR is clear. Personal data has to be accurate." [đọc] https://noyb.eu/en/ai-hallucinations-chatgpt-created-fake-child-murderer. Bài học: lỗi nguy nhất là **bịa trộn dữ kiện thật**, giám khảo dễ chấm nửa đúng. Luật: một khẳng định có phần bịa thì cả khẳng định là Bịa.

## 2. Thử máy đo trên mẫu
**a. Bộ tự kiểm có sẵn**: `python3 -I skills/bo/linhx-brand-check/scripts/tu_kiem.py` trên dữ liệu mẫu → XANH, AVI 72, rơi bước 3. Máy chấm chạy được; chưa có mẫu **người** và container không có khoá API để hỏi mô hình thật.

**b. Mô phỏng ngưỡng ổn định** (`vong-1/mo_phong_may_do.py`, stdlib, seed 9, 4.000 cặp lần chạy, tỉ lệ có mặt thật 50% là ca xấu nhất, chỉ tính nhiễu lấy mẫu):

| Cấu hình (câu × lượt × 3 mô hình) | Số ô | Lệch trung vị | Lệch p95 | Đạt ≤ 5 | Đạt ≤ 10 |
|---|---|---|---|---|---|
| 12 × 1 | 36 | 8,3 | 22,2 | 27% | 60% |
| 12 × 3 | 108 | 4,6 | 13,0 | 53% | 84% |
| 12 × 5 | 180 | 3,3 | 10,6 | 69% | 95% |
| 25 × 5 | 375 | 2,4 | 7,2 | 82% | 99% |
| 25 × 10 | 750 | 1,7 | 5,1 | 95% | 100% |

Đây là mức sàn: mô hình đổi bản, cache, cá nhân hoá còn làm lệch thêm. Từng mô hình riêng (chỉ 1/3 số ô) lệch p95 khoảng 18 điểm ở 12 × 5, nên ngưỡng "mỗi mô hình lệch ≤ 10" trong `NGHIEN-CUU.md` sẽ trượt thường xuyên.

**c. Luật "lỗi chắc = lặp ≥ 2 trên 5 lượt"**: xác suất một lỗi được đưa vào báo cáo

| Lỗi hiện ở bao nhiêu % lượt | n = 3 | n = 5 | n = 10 (≥ 3) |
|---|---|---|---|
| 10% | 0,03 | 0,08 | 0,07 |
| 20% | 0,10 | 0,26 | 0,32 |
| 40% | 0,35 | 0,66 | 0,83 |
| 60% | 0,65 | 0,91 | 0,99 |

Với 5 lượt, lỗi hiện 40% số lần bị bỏ sót 1/3. Đề nghị: lỗi **nặng** (tội, sức khoẻ, tài chính, pháp lý, bịa giải/bằng cấp) **chỉ cần 1 lần** là vào báo cáo; luật ≥ 2/5 chỉ áp cho lỗi thường.

**Máy đo chốt đề nghị (thay mục máy đo của NGHIEN-CUU)**
1. Tự động: mỗi khẳng định sai có nguyên văn, ngày, mô hình, đường lấy (API / giao diện / dán tay).
2. Ổn định: chạy lại cùng bộ, tỉ lệ có mặt **gộp** nằm trong khoảng Wilson 95% của lần trước; ngưỡng số: ≤ 10 điểm (gói Chuẩn 25 × 5 × 3), ≤ 5 (gói Sâu 25 × 10 × 3).
3. Lỗi: nặng 1 lần là vào; thường lặp ≥ 2/5.
4. Hai giám khảo khác họ, lệch nhãn Sai/Bịa/Nhầm ≤ 10%, phần lệch người kiểm. Giám khảo không thấy tên mô hình.
5. Việc sửa: mỗi việc ghi chế độ nào sẽ thấy thay đổi (tra web / trí nhớ) và mốc đo lại.

## 3. API khác giao diện bao nhiêu (đã đọc)
| Nguồn | Thiết kế | Kết quả |
|---|---|---|
| Brandlight, 6/2026 [đọc] https://research.brandlight.ai/ui-vs-api.html | 900 câu, ChatGPT/Gemini/Perplexity, 2.565 cặp | Trùng thương hiệu 11% / 12% / 6%; trích dẫn ChatGPT giao diện 15,2 so với API 4,4. "The interface is the market. Measure what the customer sees." |
| Surfer, 10/2026 [đọc] https://surfer.ai/blog/llm-scraped-ai-answers-vs-api-results/ | 1.000 câu, 5 sản phẩm, 13.779 trả lời, mỗi câu 1 lượt | Trùng thương hiệu 21–32% sau chuẩn hoá tên; API ChatGPT nêu 13,8 thương hiệu/câu, giao diện 7,9 |
| Genezio, 4/2/2026 [đọc] https://genezio.com/research/zero-query-overlaps/ | 3.645 hội thoại, 27 ngày, ngân hàng Anh | 0 truy vấn tìm kiếm ngầm trùng nhau; URL nguồn trùng 12,3% |

Cả ba là bên bán công cụ, có động cơ; nhưng cùng chiều. Quy trình: **giao diện là chính**, API chỉ để đo khối lớn rẻ. Dán tay 10 câu then chốt trên Chrome **máy công ty (DESKTOP-PVHR2CD)**, mỗi câu một cửa sổ ẩn danh mới.

## 4. Mốc chấm thêm cho báo cáo người
| # | Mốc | Lấy gì | Trạng thái |
|---|---|---|---|
| 6 | 5W/Everything-PR "Five Engines, Five Sam Altmans" (4/6/2026) https://everything-pr.com/five-engines-five-sam-altmans-the-ai-lab-founder-reputation-gap | 5 engine × 8 nhà sáng lập; 5 tiêu chí ngang nhau: Accuracy, Sentiment, Completeness, Consistency, Control; 6/8 người có ít nhất một lỗi sự kiện. "Ask five major AI engines to describe Sam Altman. You get five different Sam Altmans." Không công bố số câu, thang điểm | [đọc] |
| 7 | Everything-PR, quy trình audit (7/6/2026) https://everything-pr.com/how-to-audit-what-every-major-ai-engine-says-about-your-brand | 20–40 câu × 5 engine × 5 lượt; 5 nhóm câu (thẳng tên, theo ngành, so sánh, rủi ro, quyết định); audit lại mỗi quý | [đọc] |
| 8 | Search Engine Land, rủi ro uy tín CEO trên AI https://searchengineland.com/ai-search-reputation-risk-473361 | 5 bước sửa: danh sách câu → ghi đầu ra → phân tích nguồn → khoảng cách AI và thực tế → sửa/thay nguồn. "The most accurate claim doesn't rise to the top. The most repeated claim does." | [đọc] |
| 9 | noyb ca Holmen (mục 1) | ca lỗi mẫu bịa tội | [đọc] |

Tiêu chí "Control" (người đó kiểm soát được bao nhiêu nguồn AI dẫn) chưa có trong chuẩn ABC; nên thêm vào báo cáo người dưới dạng "% nguồn được dẫn là kênh chính chủ" (A9 đã gần đủ).

## 5. Sửa bao lâu thì AI đổi
- Beutler Ink (cập nhật 27/9/2026) [đọc] https://www.beutlerink.com/wiki-resources/faq/how-fast-ai-updates: "a corrected article can show up in answers within days"; "Knowledge Panels usually update days to weeks after the underlying source is fixed"; trí nhớ mô hình phải chờ bản mới, "can take months". Không có số thống kê.
- BlitzMetrics, SOP Wikidata cho người [đọc] https://blitzmetrics.com/the-wikidata-sop-how-we-tune-entities-for-google-knowledge-panels-and-llm-citations-with-real-before-and-after-data/: 5 pha (kiểm KG Explorer ~20 phút; tạo/bổ sung Wikidata "instance of: human", nghề, định danh mạng xã hội, 30–60 phút; mỗi khẳng định ≥ 2 nguồn khác tên miền; JSON-LD Person với `sameAs`; đo lại 60–90 ngày). Chưa có số "sau", là bài của chính agency.
- Hashmeta VN [đọc] https://hashmeta.com/vn/ai-visibility-audit-vietnam: sửa thông tin sai "thường mất 30-90 ngày"; audit 15–30 triệu, theo dõi 8–15 triệu/tháng; báo cáo PDF 30 trang, điểm 0–100, kế hoạch 90 ngày. Đây là mốc giá và khuôn đối thủ tại VN.

→ Kế hoạch 30 ngày của WF18 nên hứa: sửa xong nguồn gốc + Wikidata + JSON-LD + tiểu sử thống nhất trong 30 ngày; đo lại chế độ tra web ở ngày 30; chế độ trí nhớ đo lại ở ngày 90.

## 6. Nguồn tiếng Việt
- Hashmeta VN (trên). Bài BrandsVietnam "Hỏi AI quán ngon gần đây 5 lần" không tải được từ cloud [chỉ thấy] https://www.brandsvietnam.com/congdong/topic/hoi-ai-quan-ngon-gan-day-5-lan-quan-ban-xuat-hien-may-lan. Chưa tìm được bài nào ở VN chấm **một cá nhân** trên AI: đây là khoảng trống, cũng là lợi thế bán.
- Tiếng Trung: chưa tìm (để DR/DE-2).

## 7. Còn hở sau bổ sung này
- Chưa chạy thật trên một người (cần khoá API hoặc máy công ty). Vòng 1 là Linh.
- Bài gốc SparkToro vẫn chưa tải được; số 600 người, gần 3.000 lượt, 12 câu lấy qua Search Engine Land [đọc] https://searchengineland.com/ai-recommendation-lists-rarely-repeat-study-468076 ("Repeat presence means something. Exact rank does not.").
- Ngưỡng trong mục 2 là nhiễu lấy mẫu thuần; cần đo nhiễu thật ở vòng 1 (chạy cùng bộ hai lần cách nhau 1 ngày).
