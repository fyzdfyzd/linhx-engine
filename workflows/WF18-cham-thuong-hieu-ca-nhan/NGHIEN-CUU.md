# Nghiên cứu nền WF18: chấm thương hiệu cá nhân trên AI

Làm 9/11/2026. Đã đọc code thật 8 repo (clone ở `_refs/WF18/`, chỉ đọc, không chạy) và so với skill `linhx-brand-check` (LAB036), `linhx-audit`, Brand Truth (LAB015).

## Kết luận
1. Công cụ ngoài đều đo **"có được nhắc không, thứ hạng, cảm xúc"**. Không cái nào đối chiếu từng khẳng định với bảng sự thật. Khoảng trống này LINHX đã có (nhãn đúng/sai/nhầm/bịa/cũ trong `cham`, bảng sự thật trong `bang-su-that`). Giữ, không thay bằng công cụ ngoài.
2. Skill LINHX viết cho **doanh nghiệp** (Organization, sản phẩm, đối thủ). Thiếu hẳn phần **người**: hồ sơ `person.json`, bộ câu hỏi về người, lỗi **nhầm người trùng tên**. Đây là việc cần dựng.
3. Máy đo đề bài "chạy lại cùng bộ câu, điểm lệch ≤ 5" **sẽ không đạt nếu hiểu là điểm một lần chạy**. Nghiên cứu SparkToro/Gumshoe: dưới 1/100 khả năng ra cùng danh sách thương hiệu giữa hai lần hỏi cùng một câu. Phải đổi thành ngưỡng trên **tỉ lệ nhắc qua nhiều lượt** kèm khoảng tin cậy (LINHX đã có Wilson) và ngưỡng riêng cho **danh sách khẳng định sai** (tái hiện được hay không).
4. Chấm bằng **nhãn của giám khảo tách thợ** là đúng hướng. Thêm kiểm chéo hai giám khảo khác họ (skill `cham` ghi "v0.1 chưa tự gộp").
5. Việc sửa 30 ngày: nguồn ngoài đồng thuận một bộ việc (sửa nguồn gốc sai, thực thể Wikidata/JSON-LD Person, nhất quán đa kênh, bên thứ ba). LINHX đã có kế hoạch 30 ngày, chỉ cần bản **cho người**.

## Quy trình đề xuất
| Bước | Việc | Ai |
|---|---|---|
| 0 | `person.json`: tên, tên khác, nghề, mốc đời, công ty, **người trùng tên đã biết**, từ cấm, mỗi dữ kiện có nguồn và trạng thái confirmed/proposed | Claude dựng, Linh duyệt |
| 1 | Bộ câu: nhận biết không nêu tên ("chuyên gia X ở Việt Nam là ai"), nhận diện, sự nghiệp, sản phẩm/dịch vụ, bằng chứng, so với người cùng lĩnh vực, danh tiếng, **câu gài trùng tên** | Claude |
| 2 | Hỏi ≥ 3 họ mô hình, có cả chế độ nhớ và chế độ tra web, ≥ 5 lượt mỗi ô; lưu nguyên văn kèm ngày, tên mô hình, phiên bản | agy |
| 3 | Dán tay từ ChatGPT/Gemini/Perplexity bản web (khác API, [chưa rõ chênh bao nhiêu]) cho 10 câu then chốt | Linh hoặc máy cty |
| 4 | Gán nhãn từng khẳng định; hai giám khảo khác họ; câu một bên bắt được đưa người kiểm | Claude + giám khảo thứ hai |
| 5 | Nguồn Google/mạng xã hội: tra tay có link (mục tín hiệu) | agy |
| 6 | Báo cáo + 30 ngày, mỗi lỗi trỏ về **nguồn khả nghi** AI đã dẫn | agy dựng, Claude chấm |
| 7 | Đo lại sau 30 ngày cùng bộ câu, cùng mô hình, cùng số lượt | agy |

## Máy đo và ngưỡng (đề xuất, [GIẢ ĐỊNH] tới khi chạy vòng 1)
Rẻ tới đắt:
1. **Tự động**: mỗi khẳng định sai có file trả lời gốc, ngày, mô hình (đúng đề bài); số lượt ≥ 5 mỗi ô, dưới đó không được nói về độ ổn định (skill `hoi-ai` đang đặt 3, SparkToro cho thấy 3 là quá ít).
2. **Chấm đồng thuận**: hai giám khảo khác họ, độ lệch nhãn "sai/bịa/nhầm" ≤ 10% số khẳng định, phần lệch người kiểm.
3. **Ổn định**: chạy lại cùng bộ câu, **tỉ lệ nhắc đúng tên** mỗi mô hình lệch ≤ 10 điểm (hoặc nằm trong khoảng Wilson cũ). Thay "điểm lệch ≤ 5" bằng cái này; điểm tổng chỉ làm số phụ.
4. **Tái hiện lỗi**: khẳng định sai chỉ đưa vào báo cáo "lỗi chắc" khi lặp ≥ 2 trên ≥ 5 lượt; còn lại ghi "lỗi lẻ".
5. **Việc sửa**: mỗi việc có chủ làm, bằng chứng đo lại, và làm được trong 30 ngày (không đòi việc như "có trang Wikipedia").
6. **Mù**: giám khảo không thấy tên mô hình và không đọc lý do của thợ. Linh chỉ ở D4.

## Bản vàng
Không tìm được báo cáo kiểu "AI nói gì về một người" ở tầm top được công bố. Nói thẳng để khỏi tự lừa. Mốc dùng tạm, chi tiết ở `vang/BAN-VANG.md`:
1. Báo cáo demo AICW (cấu trúc: bảng nhắc, nguồn dẫn, miền dẫn, lọc theo mô hình).
2. Nghiên cứu SparkToro/Gumshoe (kỷ luật phương pháp: 60–100 lượt mỗi lời nhắc).
3. Quy trình 5 bước của Firon (hỏi tên, hỏi theo ngành, so sánh, cảm xúc, kiểm chính xác).
4. `BAO-CAO-mau-brand.md` của LINHX (mẫu nội bộ).
Cần **bản vàng thật**: một báo cáo chấm người do Linh duyệt ở vòng 1, rồi lấy làm mốc.

## Sửa vào skill nào, sửa gì
- `linhx-brand-check/bang-su-that`: thêm nhánh **người** (`person.json`): tên khác, người trùng tên, mốc đời, nguồn từng dữ kiện, từ cấm.
- `linhx-brand-check/cau-hoi` (`abc_lib.py`): bộ câu cho người + câu gài trùng tên; mở `--luot` mặc định Chuẩn lên 5.
- `cham`: thêm nhãn **`nham_nguoi`** (đúng sự thật nhưng của người khác). Dự án hiện chỉ có đúng/sai/nhầm/bịa/cũ; [chưa kiểm `nhầm` đã phủ ca này, cần đọc `CHUAN-ABC-v1.md` ở vòng 1]. Làm tự gộp hai giám khảo.
- `bao-cao-va-sua`: bản 30 ngày cho người (Wikidata, JSON-LD Person, tiểu sử thống nhất trên các kênh, đính chính nguồn dẫn sai); báo "lỗi chắc / lỗi lẻ".
- `linhx-audit`: chỉ gọi lại, không làm lại. Ngưỡng ở `nguong.md` toàn [GIẢ ĐỊNH]; không dùng cho WF18.
- Thừa: trọng số "Nhận diện hình ảnh 25%" của audit-brand không hợp với chấm người trên AI; bỏ khỏi WF18.

## Rủi ro
- Chạy API khác bản web mà khách dùng: SEJ ghi tác giả nghiên cứu còn để ngỏ "whether API calls yield the same variation as manual prompts". Nên có phần dán tay.
- Kết quả nhiều người dùng chung một câu hỏi bị cache, nên đổi cửa sổ, đăng xuất.
- Chấm người thật là dữ liệu cá nhân; không nạp bí mật, chỉ dùng thông tin công khai và hồ sơ người đó duyệt.
- Công cụ ngoài đều dùng danh sách từ khoá cảm xúc (xem `scoring.ts` của geo-aeo-tracker), thô, tiếng Anh. Không dùng cho tiếng Việt.
- Số liệu "đo sau 30 ngày" khó đủ mẫu; mô hình đổi bản làm mốc lệch.

## Nguồn
- [đọc] geo-aeo-tracker, `lib/scoring.ts` (điểm 0–100: nhắc +30, trong 200 ký tự đầu +20, ≥ 3 lần nhắc +15, có website trong nguồn +20, cảm xúc tới +15): https://github.com/danishashko/geo-aeo-tracker
- [đọc] aicw-ai-mentions, mẫu câu hỏi, prompt trích thực thể: https://github.com/aichatwatch/aicw-ai-mentions
- [đọc] llm-mentions-skills `mentions-check` (tham số `runs` 1–7 "to measure volatility"): https://github.com/nikhonit/llm-mentions-skills
- [đọc] geo-seo-claude `geo-brand-mentions`: https://github.com/zubair-trabzada/geo-seo-claude
- [đọc] geo-optimizer-skill: https://github.com/Auriti-Labs/geo-optimizer-skill
- [đọc lướt] limelit-co/open, aeo-radar, elmo: https://github.com/limelit-co/open · https://github.com/hellowalt/aeo-radar · https://github.com/elmohq/elmo
- [đọc] SEJ về SparkToro: "The data showed a <1-in-100 chance that ChatGPT or Google’s AI in Search (AI Overviews/AI Mode) would return the same list of brands across repeated runs of the same prompt." https://www.searchenginejournal.com/ai-recommendations-change-with-nearly-every-query-sparktoro/566242
- [đọc] Firon, 5 bước kiểm: https://fironmarketing.com/insights/what-does-chatgpt-say-about-your-brand-audit
- [chỉ thấy] trang gốc SparkToro (không tải được, 404), Search Engine Land hướng dẫn sửa ảo giác (403), Pixelmojo về nhầm thực thể (Wikidata P31/P452): https://www.pixelmojo.io/answers/why-does-chatgpt-confuse-my-company-with-another

## Bổ sung vòng 2 (9/11/2026)

### Máy đo thử (chạy thật, offline, không mạng, không code lạ)
- Lệnh: `cd D:\LINHX\LAB\LAB036-BRAND-CHECK-AGENT\src\linhx-brand-check\scripts` rồi `python brandcheck.py tu-kiem` (Python 3.12.2). Kết quả: toàn bộ 10 kiểm đơn vị và 16 kiểm trọn luồng (dữ liệu giả) đều ✓, dòng cuối `XANH`. Mẫu này là thương hiệu giả, **chưa phải mẫu người**.
- Lệnh thứ hai: gọi `wilson`, `mentions`, `negated_only` của `abc_lib.py` bằng tay. Khoảng Wilson (95%) với tỉ lệ nhắc 60%: n=3 → [21,94] (rộng 73 điểm); n=5 → [23,88] (65); n=10 → [31,83] (52); n=20 → [39,78] (39); n=60 → [47,71] (24); n=100 → [50,69] (19).
- Hệ quả, **sửa ngưỡng vòng 1**: ngưỡng "tỉ lệ nhắc lệch ≤ 10 điểm giữa hai lần đo" không thể kiểm bằng 5 lượt (khoảng rộng 65 điểm). Phải ghi rõ: 5 lượt chỉ đủ để thấy lỗi lặp, không đủ để nói độ ổn định; muốn ±10 điểm (rộng ~20) cần khoảng 100 lượt mỗi ô, nên ngưỡng ổn định đặt ở mức **"hai khoảng Wilson có chồng nhau"**, và ô nào n<20 ghi "chưa đủ mẫu".
- Hàm dò tên `mentions` khớp "Nguyễn Văn An" cả khi AI nói về một ca sĩ trùng tên ("nguyen van an la ca si" → True). Tức máy đo hiện **không phân biệt người trùng tên**; phải có bước giám khảo gán nhãn `Nhầm` dựa trên `person.json` (nghề, mốc đời, nơi ở).
- Chưa thử được: chạy `abc_hoi` với mô hình thật (cần khoá, không làm ở máy này).

### Lấp chỗ vòng 1 tự khai
1. **Nhãn nhầm người trùng tên: đã kiểm, vòng 1 nói chưa chắc, nay chắc.** `CHUAN-ABC-v1.md` dòng 53: "Nhầm | thông tin của thực thể khác (trùng tên, đối thủ)" và dòng 20 (A3): "Nhầm thực thể là cờ đỏ riêng". Vậy **không cần nhãn mới `nham_nguoi`**; chỉ cần `person.json` đủ để giám khảo phân biệt. Bỏ ý này khỏi mục "Sửa vào skill nào".
2. **Số 0,737 (geo-seo-claude): đã kiểm gốc.** Ahrefs, 12/12/2025, 75.000 thương hiệu: "YouTube mentions show the strongest correlation with AI visibility (~0.737), outperforming every other factor across ChatGPT, AI Mode, and AI Overviews." Kèm cảnh báo của chính Ahrefs: "correlation isn't causation". Nguồn: https://ahrefs.com/blog/ai-brand-visibility-correlations/ . Số này nói về **thương hiệu**, không phải người; chỉ dùng làm gợi ý ưu tiên kênh, không làm ngưỡng.
3. **Trang gốc SparkToro: tìm được link.** Nghiên cứu gốc: https://sparktoro.com/blog/new-research-ais-are-highly-inconsistent-when-recommending-brands-or-products-marketers-should-take-care-when-tracking-ai-visibility/ (link lấy từ trang Office Hours của SparkToro; trang này tôi chưa tải được trực tiếp, ghi [chỉ thấy link]). Tóm từ nguồn tìm được: 600 tình nguyện viên, 12 lời nhắc, 2.961 phản hồi, tháng 11–12/2025, mỗi lời nhắc 60–100 lượt mỗi nền tảng (WebSearch + SEJ); top thương hiệu xuất hiện 55–77% phản hồi (WebSearch, chưa kiểm trang gốc [chỉ thấy]).
4. **Số lượt tối thiểu: có số của Gumshoe.** SparkToro Office Hours (11/3/2026, đăng 8/5/2026): "if you want, you know, plus minus one, you would need to run ten prompts, seven phrasing, seven models. That means a single pass generates four hundred and ninety kind of results. You would need to run that twenty times to get plus or minus one percentage point. Or you could only run it once and you'd have plus or minus five percent". Tức 490 kết quả/lượt ≈ ±5 điểm; khớp với tính Wilson ở trên (cỡ trăm lượt cho ±10). https://sparktoro.com/blog/office-hours-can-you-actually-track-ai-visibility/ [đọc]
5. **API khác web?** SEJ: nghiên cứu SparkToro dùng người dán tay ("just copy and paste them"), còn việc API có cùng biến động hay không "left open". Vòng 2 không tìm thêm nguồn trả lời. Vẫn để phần dán tay (bước 3) và đề DR.
6. **Nguồn tiếng Việt:** chỉ tìm được một ca gần đề: Nguyễn Phi Vân đăng bài đính chính 10 lỗi mà ChatGPT, Perplexity, Google AI Overviews lặp lại về Go Global Holdings: "AI-powered research tools are surfacing outdated and fabricated information about the organizations doing this work." (về tổ chức, không phải cá nhân; năm đăng không rõ). https://en.nguyenphivan.com/post/setting-the-record-straight-the-facts-about-go-global-holdings [đọc]. Mẫu cách làm "trang đính chính công khai có danh sách lỗi" hợp với bước sửa 30 ngày. Không tìm thấy báo cáo tiếng Việt kiểm ChatGPT/Gemini nói gì về chuyên gia Việt Nam. Tiếng Trung: chưa tìm.
7. **WF14 ArcFace:** lệnh này không thuộc WF18, không làm.

### Còn thiếu sau vòng 2
- Bản vàng thật cho báo cáo chấm người: vẫn không có; đã thêm `DR/DE-2.md` (đưa link cần xem tận mắt cho máy công ty).
- Chưa chạy thử trên mẫu người thật và chưa chạy với mô hình thật.
- Chưa kiểm số "top thương hiệu 55–77%" ở trang gốc SparkToro; chưa có số thời gian AI cập nhật sau khi sửa Wikidata/JSON-LD.
- Nguồn tiếng Trung, nguồn Việt về cá nhân.
