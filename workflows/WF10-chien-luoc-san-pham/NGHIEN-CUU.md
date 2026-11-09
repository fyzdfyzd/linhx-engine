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

## Bổ sung vòng 2
Ngày 9/11/2026 (giờ VN, buổi trưa). Chỉ lấp các mục vòng 1 tự khai là mỏng. Phần "ArcFace" của WF14 không thuộc WF10, bỏ qua.

### 1. Đã mở thêm nguồn (trước chỉ thấy)
| Nguồn | Link | Trạng thái |
|---|---|---|
| Van Westendorp (Conjointly) | https://conjointly.com/products/van-westendorp/ | [đọc] HTTP 200 |
| Gabor-Granger (Conjointly) | https://conjointly.com/products/gabor-granger/ | [đọc] HTTP 200 |
| Pyramid Principle phần 1, phần 2; MECE (StrategyU) | https://strategyu.co/structure-your-ideas-pyramid-principle-part-1/ · https://strategyu.co/pyramid-principle-part-2-communicate-top-down/ · https://strategyu.co/wtf-is-mece-mutually-exclusive-collectively-exhaustive/ | [đọc] HTTP 200 cả ba |
| Tesla Master Plan, Slack "Saddles" | xem `DR/DE-2.md` | [chỉ thấy] vẫn không mở được (Tesla 403; Slack lỗi tải; archive.org bị chặn ở máy này) |
| Brands Vietnam, Advertising Vietnam | xem `DR/DE-2.md` | [chỉ thấy] vẫn 403 |

### 2. Trích nguyên văn (đã đọc)
- Van Westendorp, bốn câu hỏi: "Priced so low that you would feel the quality couldn't be very good?" (too cheap); "A bargain—a great buy for the money?" (cheap); "So expensive that you would not consider buying it?" (too expensive). (https://conjointly.com/products/van-westendorp/)
- Cách đọc: "The intersection of “too cheap” and “expensive” is considered the lower end of the range of reasonable prices." và "The intersection of “cheap” and “too expensive” is considered the upper end of the range of reasonable prices." (cùng trang)
- Cảnh báo: "The “optimal” and “normal” price points do not necessarily optimise for profit, volume, or revenue." (cùng trang) → khoảng giá Van Westendorp chỉ là khoảng chấp nhận được, không phải giá tối ưu lợi nhuận.
- Gabor-Granger: "Each respondent is given a series of almost identical questions, such as “Would you buy product X at price Y?”." và số mức giá "ideally, between 8 and 15 price levels". (https://conjointly.com/products/gabor-granger/)
- Pyramid, đáp án trước: "The default way of using the pyramid principle is to start with the “answer.”" và "This is almost always the best way to communicate if you are delivering something in writing." (https://strategyu.co/pyramid-principle-part-2-communicate-top-down/)
- MECE: "MECE is an acronym for the phrase Mutually Exclusive, Collectively Exhaustive." (https://strategyu.co/wtf-is-mece-mutually-exclusive-collectively-exhaustive/)

### 3. Điều chỉnh nhận định vòng 1
- Bước 0 "giả thuyết trả lời trước" có nguồn đọc thật (Pyramid phần 2), nhưng trang cũng nói cách này không phải lúc nào cũng tối ưu với khán giả có thể phản đối; tài liệu cho Linh duyệt là văn bản viết nên áp dụng được.
- **Cỡ mẫu giá: hai trang Conjointly KHÔNG nêu cỡ mẫu tối thiểu cho Van Westendorp và Gabor-Granger** (số "8–15" là số mức giá, không phải số người). Vì vậy mục Máy đo vòng 1 không được ghi con số cỡ mẫu giá nào; ghi "chưa có nguồn, Linh chốt theo đề, và DE-2 mục 5 đi tìm bài Q&Me/Kantar VN". Ngưỡng "10 phỏng vấn" vẫn chỉ là gợi ý của phuryn cho chọn bãi đổ bộ, không phải cho khảo sát giá.
- Mục "ngưỡng" khác ở Máy đo vòng 1 (≥4 đối thủ, trung vị ≥4, 2/3 phiếu) là ngưỡng LINHX tự đặt trong skill/rubric, không phải số từ nguồn ngoài.

### 4. Thử máy đo (script của repo, không tải code lạ, không Chrome)
Script: `skills/le/linhx-chuan/scripts/kiem.py` (+ `loai.json`, loại `chien-luoc`). Python 3.12.2. Phải đặt `PYTHONUTF8=1`, nếu không script chết `UnicodeEncodeError` (cp1252) khi in tiếng Việt trên Windows này; không sửa script.
Mẫu: `skills/le/linhx-chuan/khuon/` (khuôn rỗng) và thư mục WF10 này. Mẫu vàng thật của chiến lược không có trên máy này (`WF-CHUAN` chỉ có WF13).

| # | Lệnh | Kết quả thật |
|---|---|---|
| 1 | `python kiem.py skills/le/linhx-chuan/khuon --pha dau` | CHUA_DAT, 5 lỗi: 4 mục hành trình người xem chưa điền, THAM-CHIEU.md 0 link (cần ≥5). Mã thoát 1 |
| 2 | `python kiem.py …/khuon --pha cuoi --loai chien-luoc` | CHUA_DAT, 14 lỗi: thêm thiếu BRIEF, PHAN-KHUC*, DOI-THU*, KHOANG-TRONG*, QUYET-DINH*, CHUNG-THUC*, 0 file NC (cần ≥3), BAI-HOC 0 dòng, ảnh E2E không tồn tại |
| 3 | `python kiem.py workflows/WF10-chien-luoc-san-pham --pha dau` | CHUA_DAT, 9 lỗi (thiếu 4 sổ STATUS/HANH-TRINH/THAM-CHIEU/DATA_GAPS…). Đúng, vì đây là thư mục nghiên cứu, không phải thư mục việc |
| 4 | Sao khuôn sang `_refs/WF10/mau-kiem/`, điền 4 mục hành trình và 5 link vào THAM-CHIEU.md (mẫu thử, nội dung giả), `python kiem.py _refs/WF10/mau-kiem --pha dau` | **DAT**, mã thoát 0 |

Kết luận về máy đo:
- Chạy được, phân biệt đúng khuôn rỗng (trượt) và bản điền đủ (qua). Đây là kiểm **cấu trúc và truy nguồn**, đúng như dòng đầu script ghi: "Chỉ kiểm cấu trúc và truy nguồn; chất lượng do người chấm".
- `loai.json` loại `chien-luoc` hiện chỉ đòi các mục cũ (BRIEF, PHAN-KHUC, DOI-THU, KHOANG-TRONG, QUYET-DINH, CHUNG-THUC, ≥3 NC). **Chưa có** kiểm "Chẩn đoán", "Không làm", "Giá" mà vòng 1 đề xuất: đề xuất thêm là đúng chỗ (thêm vào mảng mục của `QUYET-DINH*.md`), việc nhỏ.
- Chưa thử được: pha `cuoi` đầy đủ trên một việc chiến lược thật (CTS nhánh B) vì mẫu đó không có ở máy này. Việc cần máy Linh/máy công ty.
- Nhược điểm thấy khi chạy: lỗi mã hoá Windows (xem trên). Đề xuất thêm `sys.stdout.reconfigure(encoding="utf-8")` ở đầu `main` (chưa sửa; ngoài thư mục WF10).

### 5. Còn thiếu sau vòng 2
- Bản vàng công khai vẫn 0 mẫu mở được (Tesla, Slack). Đã ghi hàng đợi `DR/DE-2.md` cho máy cty.
- Nguồn tiếng Việt: 0 bài đọc được (2 bài vẫn 403; chưa tìm được bài Q&Me/Kantar VN vì máy này không có công cụ tìm kiếm trong lượt này).
- Cỡ mẫu tối thiểu cho nghiên cứu giá ở VN: chưa có nguồn.
- Rumelt: vẫn chỉ qua tóm tắt Alex Murrell, chưa mở sách/bài gốc.
