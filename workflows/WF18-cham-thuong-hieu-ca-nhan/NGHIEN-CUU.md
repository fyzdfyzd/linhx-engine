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
