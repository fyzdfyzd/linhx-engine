# NGHIEN-CUU WF10 · Chiến lược sản phẩm, giá, khách

Ngày 9/11/2026. Chi tiết nguồn: `NGOAI.md`. Đề Deep Research: `DR/DE-1.md` (chưa có kết quả).

## Kết luận
1. Skill `chien-luoc` (7 bước) đã **sâu hơn** mọi skill công khai đọc được (borghei, alirezarezvani, mohitagw15856, phuryn, deanpeters, Anthropic). Họ mỏng, mẫu SaaS tiếng Anh. Không chép nguyên, chỉ vá chỗ thiếu.
2. Thiếu lớn nhất: skill không có **lõi chiến lược** (chẩn đoán → chính sách dẫn đường → hành động nhất quán, theo Rumelt) và **không có bước giá** riêng (giá chỉ rải trong NC và PMF).
3. Thiếu **ngưỡng kiểm chứng đo được** ở cuối mỗi bước (alirezarezvani có dòng "Validation"). Cũng thiếu mục **"việc sẽ KHÔNG làm"** và "vì sao đối thủ khó chép" (phuryn).
4. Một nguồn cho phép thợ tự suy bằng chứng rồi gắn nhãn "assumed" (mohitagw15856). **Không nhận**, vì trái luật không bịa; thay bằng DATA_GAPS.
5. Bản vàng công khai chưa tải được (nhiều trang chặn). Mốc chính vẫn là bộ Trân Bảo/KGBG/BTMH của Linh.

## Quy trình đề xuất (giữ 7 bước, thêm 3 chỗ)
| Bước | Ai làm | Thêm |
|---|---|---|
| 0 | thợ | **Giả thuyết trả lời trước** (1 đoạn: "ta nghĩ nên làm X cho Y vì Z"), để các NC chứng minh hoặc bác (đáp án trước, kiểu McKinsey) |
| 1–5 | thợ (agy) | như skill hiện có |
| 5b (mới) | thợ | **Chẩn đoán**: 1 đoạn nêu thách thức cốt lõi và 2–3 thứ ta bỏ qua có chủ đích |
| 6 | thợ, Linh duyệt D2 | Quyết định viết dạng **chẩn đoán + chính sách + 3–5 hành động liên kết**; thêm **GIÁ** (mô hình, bậc, mỏ neo, ngưỡng, kiểm bằng Van Westendorp hoặc đối chiếu giá đối thủ) và mục **Không làm** |
| 7 | người chấm khác thợ | chứng thực số, 5 số mở ngẫu nhiên; Linh duyệt D4 |

## Máy đo + ngưỡng (rẻ → đắt)
1. **Tự động** (`kiem.py --loai chien-luoc`, thêm): có đủ file; mọi số có `[BC-xxx]`; DATA_GAPS không rỗng khi có giả định; có tiêu đề "Chẩn đoán", "Không làm", "Giá"; ≥4 đối thủ có tên + số; không còn chỗ trống/`[ADD…]`. Ngưỡng: qua 100%.
2. **Rubric 12 tiêu chí** (đã có) + 3 tiêu chí riêng. Ngưỡng hiện có: trung vị ≥4, 2/3 phiếu đạt. Thêm 4 dấu hiệu chiến lược dở của Rumelt làm cờ lỗi: nói suông, né thách thức, lấy mục tiêu làm chiến lược, mục tiêu rỗng. Mỗi cờ → "nặng".
3. **Chấm mù**: người chấm không đọc lý do của thợ, nhận bản đã che tên nhánh. Hỏi cố định: "chiến lược này bảo ta **không làm** gì?" Nếu không trả lời được → trượt.
4. **Giá trị chứng thực**: 5 số ngẫu nhiên khớp 5/5 (đã có). Thêm: mỗi phương án có cổng Go/No-Go với chỉ số và mốc (kiểu alirezarezvani "3+ paying customers … in first 90 days", chỉnh theo ngành).
5. **Linh**: D2, D4.
Ngưỡng cụ thể 10 khách phỏng vấn / cỡ mẫu giá là **gợi ý từ nguồn ngoài** (phuryn: "at least 10 customer interviews"), cần Linh/khách chốt cho từng đề.

## Bản vàng (mốc chấm)
1. Bộ Trân Bảo / Kim Gia Bảo Gift / BTMH IPO (chị Quỳnh Hương, 2026): mốc chính, ở máy Linh. [đọc qua skill, chưa mở gốc]
2. EY-Parthenon · Chiến lược sản phẩm BTMH; C+P/dentsu Redder · Cốt lõi định vị BTMH; OMC Customer Segmentation (`high-standard.md`). [chỉ thấy qua mô tả trong skill]
3. Tesla "Secret Master Plan" (Musk, 2006), Slack "We Don't Sell Saddles Here" (Butterfield): ứng viên mẫu ngắn, rõ chẩn đoán và thứ tự. [chỉ thấy, tải lỗi 403/đứt, chưa kiểm nội dung; không dùng làm mốc cho đến khi mở được]
Chưa đủ 3–5 mẫu công khai đã mở được. Việc tiếp: máy cty tải bằng Chrome, hoặc kết quả `DR/KQ-1.md`.

## Sửa vào skill nào
- `le/chien-luoc/SKILL.md`: thêm bước 0 (giả thuyết), 5b (chẩn đoán), mục Giá và "Không làm" ở bước 6; thêm dòng **Validation** cuối mỗi bước.
- `le/chien-luoc/references/`: thêm `09-gia.md` (mô hình giá, bậc, mỏ neo, Van Westendorp, kiểm tài chính ARPU/hoàn vốn); thêm bảng chọn **bãi đổ bộ (beachhead)** 4 tiêu chí vào `04` hoặc `05`.
- `le/chien-luoc/references/03-doi-thu-dinh-vi.md`: thêm luật "nói thật chỗ đối thủ hơn mình"; chống "For Everyone", "tagline", "liệt kê tính năng".
- `le/linhx-chuan/scripts/kiem.py` (loại `chien-luoc`): thêm các kiểm ở mục Máy đo 1. Không đụng `linhx-chuan/cham.md` ngoài cờ Rumelt.
- Không tạo skill mới; không lấy lõi nào từ skill ngoài.

## Rủi ro
- Dùng ngưỡng SaaS (churn, ICP) cho hàng quà tặng/tiêu dùng VN: sai ngành.
- Thợ bịa bằng chứng khi thiếu: đã chặn bằng DATA_GAPS, không nhận nhãn "assumed".
- Tài liệu khách có dấu mật: chỉ giữ cấu trúc, không chép số.
- Giá không có khảo sát thật thì chỉ là giả thuyết: phải ghi rõ.
- Nhiều nguồn tiếng Việt và bản vàng bị chặn 403; thiếu mẫu công khai.

## Nguồn
[đọc] borghei/claude-skills product-strategist · alirezarezvani/claude-skills marketing-strategy-pmm · mohitagw15856/pm-claude-skills go-to-market · phuryn/pm-skills · deanpeters/Product-Manager-Skills · anthropics/knowledge-work-plugins product-management (link ở `NGOAI.md`) · https://www.alexmurrell.co.uk/summaries/richard-rumelt-good-strategy-bad-strategy · https://www.heinzmarketing.com/blog/10-step-positioning-process-an-obviously-awesome-book-summary-part-3/
[chỉ thấy] https://strategyu.co/structure-your-ideas-pyramid-principle-part-1/ · https://conjointly.com/products/van-westendorp/ · brandsvietnam, advertisingvietnam (403) · Tesla, Slack, McKinsey (không mở được)
