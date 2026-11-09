# BỔ SUNG V2 (cloud) · WF10 Chiến lược sản phẩm, giá, khách

9/11/2026, thread "Chuẩn hoá làm chiến lược sản phẩm". Lấp chỗ mỏng của `NGHIEN-CUU.md`, không sửa file đó. [đọc] = đã mở file/trang thật.

## 1. Năm điều thêm vào kết luận
1. **Red-team giả định chịu lực trước D4** (phuryn `strategy-red-team`, MIT) [đọc]: tách luận điểm "nếu sai thì chết", nêu bản mạnh nhất rồi mới đánh, viết "Hỏng nếu…", xếp theo tác động × khả năng sai × rẻ để thử; mỗi giả định có **bằng chứng lấy tuần này, tiêu chí dừng, phép thử rẻ nhất**. Luật: "No fabrication — if it's sound, say so." Đây là bước thiếu nhất của `chien-luoc`: hiện chỉ có Go/No-Go sau quyết định, chưa có đánh giả định trước quyết định.
2. **"Điều gì phải đúng"** (Playing to Win, amplitude/builder-skills `playing-to-win`) [đọc]: mỗi lựa chọn (chơi ở đâu, thắng thế nào) có 2–3 điều kiện phải đúng, độ tin, cách kiểm. Câu thử hay: "Would a competitor reading this strategy know exactly how to compete with you?" Bổ sung cho bước 5b "chẩn đoán" mà máy cty đề xuất.
3. **Giá đặt trước sản phẩm** (wondelai `monetizing-innovation`, MIT, theo Ramanujam & Tacke) [đọc]: hỏi sẵn lòng chi trả ở giai đoạn ý tưởng; đọc **đường cong**, không lấy trung bình (thị trường hai đỉnh thì trung bình là khách không tồn tại); số khai thì "cắt bớt", phải có bằng chứng hành vi (đặt trước, cửa giả, A/B giá thật). Cỡ mẫu B2C: 10–15 phỏng vấn lấy ngôn ngữ rồi 150–300 phiếu/phân khúc; dưới 10 thì chỉ là hướng. 4 kiểu hỏng: nhồi tính năng, định giá rụt rè, viên ngọc ẩn, sản phẩm xác sống. → Đúng bệnh CTS: giá 99k chọn trước, chưa đo WTP.
4. **Kinh tế đơn vị trước khi tiêu tiền** (the_opc LAB117): CAC cho phép = 1/3 LTV, tính cả token + giờ Linh. Số giả lịch vận 99k: CAC cho phép 50k < dự kiến 70k → không mở ads. Phải là mục bắt buộc trong `09-gia.md` máy cty đề xuất.
5. **PMF đo bằng khách thật sau launch** (wdavidturner `pmf-survey`, chuẩn Sean Ellis) [đọc]: câu hỏi cố định "thất vọng thế nào nếu không dùng được nữa", ngưỡng 40% "rất thất vọng", cần ≥30 người đã dùng (40–50 phiếu là đủ). Dùng làm một cổng Go/No-Go có số, thay cho "PMF 12 tiêu chí" vốn là so phương án chứ không phải đo PMF.

## 2. Nguồn tiếng Việt (chỗ thiếu của NGHIEN-CUU.md)
Cloud cũng bị chặn brandsvietnam.com và advertisingvietnam.com (proxy 403, WebFetch lỗi). Đọc được:
| Nguồn | Lấy |
|---|---|
| VnEconomy, Song Hà, 10/10/2025, PwC VN Khảo sát Người tiêu dùng 2025, **517 người** [đọc] https://vneconomy.vn/thi-truong-tieu-dung-viet-nam-2025-nguoi-tieu-dung-huong-toi-gia-tri-cong-nghe-so-va-ben-vung.htm | 47% xếp giá là yếu tố hàng đầu khi mua thực phẩm; 70% "chỉ mua những gì cần thiết"; vẫn 41% trả thêm cho hàng địa phương, 69% cho hàng thân thiện môi trường. Ý: khách Việt nhạy giá nhưng trả thêm khi giá trị rõ và có chứng nhận. Mẫu nhỏ, ngành thực phẩm: chỉ dùng làm bối cảnh, không làm số chính cho CTS. |
| VnBusiness, Thanh Hoa, 10/10/2025 (cùng khảo sát PwC) [đọc] https://vnbusiness.vn/pwc-viet-nam-gia-ca-la-moi-quan-tam-hang-dau-cua-nguoi-tieu-dung-viet.html | Trích: "định hình lại tuyên bố giá trị, cung cấp sản phẩm hợp túi tiền mà vẫn đảm bảo sức khỏe, tiện lợi và có tính bền vững". Không cộng dồn với dòng trên. |
| VnEconomy, Bảo Bình, 06/08/2025 (số của AVIA/CAP) [đọc] https://vneconomy.vn/techconnect/71-nguoi-viet-san-sang-tra-phi-nhung-vi-pham-ban-quyen-noi-dung-so-tai-viet-nam-van-cao.htm | "71% người Việt trả lời “sẵn sàng trả phí” nếu các dịch vụ vi phạm bản quyền bị ngăn chặn"; 62% từng ngừng trả tiền vì có nguồn lậu. **Cảnh báo**: câu hỏi giả định, nguồn có lợi ích, không cỡ mẫu → ví dụ tốt cho luật "số khai thì cắt bớt". |
| VnEconomy, Mai Anh, 20/01/2025 (tóm Fortune) [đọc] https://vneconomy.vn/techconnect/3-gia-dinh-co-the-khien-doanh-nghiep-khoi-nghiep-cong-nghe-that-bai.htm | "Nếu doanh nghiệp không thể nhận được cam kết mua hàng, sự phù hợp giữa sản phẩm và thị trường chỉ là may mắn." → bán thử trước, khảo sát ý kiến không đủ. |
| VnBusiness, Đỗ Kiều, 20/6/2026 [đọc] https://vnbusiness.vn/doc-gia-se-tra-tien-cho-dieu-gi-trong-thoi-dai-tin-tuc-mien-phi.html | "Độc giả chỉ trả tiền khi họ nhận được một giá trị rõ ràng." Mô hình thu phí nội dung ở VN còn sớm (VietnamPlus 2018, VietNamNet Premium 2021), ít số công khai. |
| LimeSurvey VN, Jory Nagel, 20/11/2024 [đọc] https://www.limesurvey.org/vi/blog/kien-thuc/toi-uu-gia-van-westendorp-cach-thiet-lap-gia-dung-voi-limesurvey | Cách dựng Van Westendorp tiếng Việt (4 câu, điểm OPP/IPP), bổ sung bằng A/B. Không có case VN. |
| [chỉ thấy, bị chặn] brandsvietnam: "Survey True – Xác định mức giá tối ưu…", "Chiến lược giá… quy trình 5 giai đoạn", "Định giá chính xác – Chiến lược thành công (P1, P2)", "Xây dựng Chiến lược Ngành hàng và Thương hiệu"; advertisingvietnam "Khách hàng nói giá cao chưa chắc họ muốn bạn giảm giá" | Đã đưa link vào `DR/DE-2.md` để máy cty mở bằng Chrome. |
Kết luận nguồn Việt: **chưa có quy trình chiến lược giá nào của đơn vị VN đọc được nguyên văn**; mốc VN thật vẫn là bộ Trân Bảo/KGBG/BTMH của chị Hương. Số WTP người Việt công khai rất mỏng → mọi giá CTS phải đo bằng hành vi (cửa giả, A/B giá trên QR thật), ghi DATA_GAPS.

## 3. Thử máy đo trên mẫu có sẵn
Viết `may-do/do_chien_luoc.py` (nấc 1, thuần Python, không mạng): đếm mục bắt buộc (chẩn đoán, không làm, giá, Go/No-Go, phải đúng, tiêu chí dừng, chỗ đối thủ hơn), tỉ lệ dòng có số mang `[BC-xxx]`, từ sáo/1.000 chữ, tỉ lệ câu >40 chữ, bốc 5 BC ngẫu nhiên để mở.

Mẫu: `KHOANG-TRONG_20261102.md` nhánh cts-B (bản đã qua D2 ngày 3/11), 12.617 chữ.
| Chỉ số | Kết quả | Ngưỡng thử | |
|---|---|---|---|
| Mục chẩn đoán / không làm / giá / phải đúng | có | có | đạt |
| Go/No-Go, tiêu chí dừng, chỗ đối thủ hơn mình | **không** | có | trượt (Go/No-Go thuộc bước 6, hai mục sau nên bắt ở mọi file quyết định) |
| Dòng có số mang [BC] | **62%** (146 dòng) | ≥90% | trượt; một phần là báo nhầm (tiêu đề "#1", mã gói) |
| Câu >40 chữ | **50%**, câu dài nhất 166 chữ | ≤15% | trượt nặng: trang D2 "1 trang" thực tế không đọc nổi trên điện thoại |
| Từ sáo | 0,55/1.000 chữ | ≤2 | đạt |
| Một nguồn gánh quá nhiều | BC-020 dùng 53 lần, BC-002 52 lần trên 100 lần gắn | — | dấu hiệu "nguồn gánh": nên thêm chỉ số ≤20% lượt gắn cho 1 nguồn |
| 5 BC mở ngẫu nhiên | BC-005, 019, 003, 009, 004 | 5/5 khớp | chưa mở được: bằng chứng ở máy cty |
Đối chứng: `LAB117/KHAO-SAT.md` và `KE-HOACH-NGUOC.md` (ghi chú ngắn) trượt hết mục bắt buộc, đúng ý (không phải bản chiến lược). Máy đo tách được bản chiến lược thật với ghi chú.

**Bài học từ lần thử**: bản qua D2 vẫn dở ở hai chỗ máy bắt được rẻ: **câu quá dài** (lỗi "quá nhiều" trong 5 kiểu hỏng) và **số không nguồn**. Hai kiểm này nên vào `kiem.py --loai chien-luoc` trước khi tốn người chấm. Ngưỡng là thử, cần chạy trên bản Trân Bảo (máy cty) để chỉnh: bản vàng phải qua.

## 4. Sửa vào skill (thêm vào danh sách của NGHIEN-CUU.md)
- `le/chien-luoc/SKILL.md`: bước **6b red-team** trước D4 (theo phuryn), người làm khác thợ; bảng "Điều gì phải đúng" cho mỗi phương án.
- `references/09-gia.md` (máy cty đã đề xuất) thêm: giá trước sản phẩm, đường cong WTP, cắt bớt số khai, cỡ mẫu B2C, 4 kiểu hỏng giá, thẻ kinh tế đơn vị the_opc.
- `references/05-quyet-dinh-pmf.md`: tách "so 12 tiêu chí phương án" với "đo PMF sau launch" (Sean Ellis 40%, ≥30 người dùng).
- `linhx-chuan/scripts/kiem.py`: nạp 4 kiểm từ `do_chien_luoc.py` (số có nguồn, câu dài, nguồn gánh, mục bắt buộc); bốc BC ngẫu nhiên in ra cho người chấm.

## Nguồn ngoài đọc thêm ở cloud (đã clone, coi là dữ liệu)
phuryn/pm-skills `pm-execution/skills/strategy-red-team` (MIT) · amplitude/builder-skills `product-skills/skills/playing-to-win` · wondelai/skills `monetizing-innovation` + `references/wtp-conversations.md` (MIT) · wdavidturner/product-skills `pmf-survey` · mohitagw15856 `strategy-memo` (Rumelt). [chỉ thấy] ericgandrade/claude-superskills `mckinsey-strategist` (có evals.json, đáng đọc vòng 1), wdavidturner `seven-powers`.
