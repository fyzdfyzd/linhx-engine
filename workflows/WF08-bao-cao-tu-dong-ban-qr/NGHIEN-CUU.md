# WF08 · Nghiên cứu nền: báo cáo tự động bán QR

Làm 9/11/2026. Đọc code thật 5 nguồn (clone ở `_refs/WF08/`, chỉ đọc, không chạy), đọc 12 trang web, tải 3 PDF mẫu vào `vang/`. Đề Deep Research gửi ở `DR/DE-1.md`, chưa có kết quả.

## Kết luận
1. Không có repo mã mở nào làm trọn "trả QR → báo cáo cá nhân hoá → giao ≤ 10 phút". Phải ghép ba mảnh: lõi tính + kho lời giải (LINHX đã có, report-core), dựng PDF theo mẫu (Typst), lớp giao hàng sau thanh toán.
2. Chỗ LINHX còn trống nhất là **0 số bịa**: cổng 17 luật chỉ bắt lỗi văn (cụt câu, trùng, từ cấm, thiếu nguồn), chưa có luật nào đối chiếu từng con số và tên trong văn với dữ kiện đã tính. Cần luật Q18 chạy theo kiểu "không chứng minh được thì không in".
3. Lớp giao hàng chưa có trong skill nào. Mẫu tốt nhất đọc được: webhook chỉ xác thực rồi trả ngay, việc nặng chạy hàng đợi, khoá chống trùng theo mã giao dịch, thiếu tiền thì vào hàng duyệt tay.
4. Báo cáo tốt hơn không phải báo cáo dài hơn. Người bán báo cáo chiêm tinh tự nhận tiêu chí: có tính toán thật, đọc các yếu tố đối chiếu nhau, bỏ những gì không đáng đưa vào, có bằng chứng truy vết. Bản mới của LINHX (8.702 chữ, 34 trang) đã đi đúng hướng này.
5. Mốc vàng ngoài đời cho loại "báo cáo tính cách/thiên hướng" có thật và tải được (Truity 14 trang, Gallup 25 trang). Mốc vàng chiêm tinh tiếng Việt chưa có; mẫu đầu Linh duyệt (D4) sẽ thành mốc.

## Quy trình đề xuất
| # | Bước | Ai | Ghi chú |
|---|---|---|---|
| 1 | Khách điền ngày giờ nơi sinh, email, chọn gói; tạo đơn với mã thanh toán duy nhất, khó đoán | engine | mã đơn không tuần tự (SePay khuyên) |
| 2 | Hiện QR, trang chờ hỏi trạng thái 3 giây/lần, hết hạn 15 phút | engine | theo mẫu SePay |
| 3 | Webhook ngân hàng: kiểm chữ ký, ghi `id` giao dịch (UNIQUE) rồi trả 200 ngay | engine | Casso hạn 5 giây, SePay 8 giây |
| 4 | Khớp mã đơn, kiểm số tiền ≥ giá. Thiếu tiền hoặc không khớp mã → hàng duyệt tay, không giao | engine, Linh duyệt ngoại lệ | |
| 5 | Hàng đợi: tính FactSet → ghép từ kho → đánh bóng (nếu có) → **cổng số + cổng 17 luật** → PDF | report-core | lỗi thì thử lại từng bước, không chạy lại bước đã xong |
| 6 | Gửi email kèm liên kết có hạn; ghi giờ giao | engine | |
| 7 | Mỗi đêm đối soát: giao dịch đã vào tiền mà chưa có báo cáo | engine | Casso khuyên tra soát qua API |

## Máy đo + ngưỡng (đề xuất, xếp rẻ tới đắt)
| Mã | Đo gì | Cách đo | Ngưỡng |
|---|---|---|---|
| M1 | Số bịa | mọi số, tên hành tinh/cung/con số trong văn phải khớp một dòng FactSet; không khớp = lỗi | 0 |
| M2 | Cổng 17 luật | đã có | điểm ≥ 85, 0 lỗi |
| M3 | Tái lập | cùng đầu vào chạy 2 lần, băm văn bản (trước bước LLM) | giống hệt |
| M4 | Giao một lần | bắn cùng webhook 3 lần; bắn sai số tiền; bắn sai mã | 1 báo cáo; 0; 0 và vào hàng duyệt |
| M5 | Thời gian | từ webhook tới email, 20 đơn | p95 ≤ 10 phút (đề bài); nên đặt mục tiêu ≤ 3 phút nếu không gọi LLM |
| M6 | 20 mẫu ngẫu nhiên | persona Nemotron-Personas-VN + ca biên: thiếu giờ sinh, sinh 29/2, tên rất dài, nơi sinh ngoài Việt Nam | 0 lỗi |
| M7 | PDF | font tiếng Việt, không tràn, số trang trong khoảng | 0 lỗi |
| M8 | Rubric 9 tiêu chí (bên dưới) | chấm mù cặp A/B với bản vàng; người chấm không đọc lý do của thợ | ≥ 14/18 và không tiêu chí nào 0 |
| M9 | Linh | D2, D4 | ≤ 2 lần chạm ở vòng 3 |

Rubric M8 (mỗi tiêu chí 0–2), lấy từ tiêu chí bài [Bonnie Sorsby](https://bonniesorsby.com/astrology-reports-compared/) [đọc]: có tính toán thật · đọc các yếu tố đối chiếu nhau · giữ mâu thuẫn, không làm phẳng · bỏ cái không đáng đưa · kết bằng lời đời thường · truy vết được vì sao có câu đó · đọc lại được sau vài tháng · không lặp · dữ liệu vào đúng. Đây là đề xuất của tôi dựa trên bài đó, chưa có nơi nào công bố ngưỡng.

## Bản vàng (xem `vang/README.md`)
1. Truity, báo cáo Big Five mẫu, 14 trang [đọc]: mỗi chiều có điểm so với trung bình, giải nghĩa mức cao/thấp, mục "Where you fit in" nói riêng cho người đọc.
2. Gallup, CliftonStrengths 34 mẫu, 25 trang [đọc]: danh sách xếp hạng 34 mục, nhóm theo 4 vùng, mỗi mục có phần riêng.
3. O*NET Interest Profiler (Manual + báo cáo điểm) [đọc Manual]: mốc cho hướng nghiệp vòng 3, giấy phép Creative Commons.
4. Nội bộ: `chiem-tinh-minh-anh.pdf` và `than-so-an.pdf` (LAB046) làm mốc sàn, chưa phải vàng.
5. Chiêm tinh tiếng Việt: để trống tới khi Linh duyệt mẫu D4. Astro.com chặn máy tải nên chưa lấy được mẫu [chỉ thấy].

## Sửa vào skill nào
- **Chưa có skill cho report-core trong `skills/`** (code chỉ nằm ở LAB046/src). Tạo một skill `bao-cao-ca-nhan` (không phải sửa `linhx-report`, đó là báo cáo tư vấn PDF dài, loại khác) gồm: blueprint, kho lời giải, cổng, luật giao.
- Thêm luật **Q18 số-thật** vào `quality.py`: số trong văn phải có thẻ nguồn là mã FactSet; không có thì bỏ số hoặc chặn xuất. Mô hình: [Proof-Carrying Numbers](https://arxiv.org/abs/2509.06902) "only claim-checked numbers are marked as verified, and all others default to unverified." [đọc abstract].
- Thêm **luật giao** (M4, M5) và test bằng webhook giả; tách riêng khỏi lõi tính.
- Vòng 1 "AI nói gì" chạy bằng `brand-check`, `cham`, `bao-cao-va-sua` [chỉ đọc mô tả INDEX]: nên đưa kết quả chấm thành FactSet để dùng chung cổng số, khỏi viết cổng thứ hai.
- Bước "đánh bóng bằng LLM" (lộ trình mục 3 của KIEN-TRUC) chỉ được đặt trước cổng số, không sau.
- Giữ: kho theo mã thực thể, chọn đoạn cố định, Q01–Q17. Không thấy nơi nào làm tốt hơn.

## Rủi ro
- Ngày giờ nơi sinh là dữ liệu cá nhân; LAB046 ghi dữ liệu nhạy cảm chịu luật 2026. Cần xác nhận luật trước khi thu (DE-1 câu 6 chưa hỏi, thêm nếu cần).
- Kho thần số: 33 đoạn Claude tự viết chưa được Linh duyệt. 582 diễn giải cafeastro chỉ tham chiếu, không đăng nguyên văn.
- Chuyển khoản sai nội dung/thiếu tiền là ca thường gặp; phải có hàng duyệt tay và đối soát, nếu không sót khách.
- Casso tạm dừng webhook sau 24 giờ lỗi liên tục, hủy sau 7 ngày: phải có cảnh báo khi endpoint chết.
- Mẫu Truity, Gallup có bản quyền: chỉ để học bố cục và nhịp, không chép chữ.
- Độ trễ thực của webhook ngân hàng Việt chưa có số liệu (cả SePay và Casso không nêu): M5 phải đo thật.

## Nguồn
- [đọc code] `_refs/WF08/`: [kerykeion](https://github.com/g-battaglia/kerykeion), [immanuel-python](https://github.com/theriftlab/immanuel-python), [branded-pdf-service](https://github.com/tsayles/branded-pdf-service), [papermake](https://github.com/rkstgr/papermake), [nava2](https://github.com/pvotio/nava2), cộng [natal-charts](https://github.com/jc4p/natal-charts) [chỉ thấy README].
- [đọc] Chi tiết từng nguồn: `NGOAI.md`.
- [đọc] [SePay: tạo QR và form](https://developer.sepay.vn/en/sepay-webhooks/tao-qr-va-form-thanh-toan); [Casso: webhook thủ công](https://developer.casso.vn/webhook/thiet-lap-webhook-thu-cong); [freeCodeCamp](https://www.freecodecamp.org/news/stripe-webhooks-background-jobs); [dev.to Stripe giao hàng](https://dev.to/joeytbuilds/the-exact-stripe-webhook-code-i-use-to-deliver-digital-products-automatically-3d6o); [n8n 17213](https://n8n.io/workflows/17213-create-human-reviewed-personalized-pdfs-from-stripe-payments-using-openai/).
- [đọc] [O*NET IP Manual](https://www.onetcenter.org/dl_files/IP_Manual.pdf), [Truity mẫu](https://www.truity.com/sites/default/files/fillpdf/sample_big_five_personality_test_report.pdf), [Gallup mẫu](https://www.gallup.com/file/cliftonstrengths/en/260807/CliftonStrengths_34_Report.pdf).
- [chỉ thấy] [tianpan: narrated a number](https://tianpan.co/blog/2026/05/17/agent-narrated-a-number-it-should-have-computed) (phần công khai); astro.com, 16personalities (bị chặn).
- [DR] chưa có: `DR/DE-1.md`.
