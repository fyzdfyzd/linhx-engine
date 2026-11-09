# WF02 · Nghiên cứu nền: trang bán OPC qua QR

Ngày 9/11/2026. Nguồn chi tiết: `NGOAI.md`. Phần luật còn chờ Deep Research (`DR/DE-1.md`).

## Kết luận
1. Người ngoài làm tốt phần **vẻ ngoài** (taste-skill, impeccable, frontend-design). Không ai làm trọn chuỗi "trang → QR → xác nhận → giao" cho Việt Nam; phần này chỉ có tài liệu từng cổng (SePay, Casso, payOS).
2. Cái đáng học nhất: **cổng kiểm bằng máy chạy Chrome thật** của taste-skill (chặn kết thúc khi còn lỗi, tối đa 3 vòng). Giống trần vòng của LINHX, nên lấy ý, không chép nguyên.
3. Skill `web-thiet-ke` của LINHX có quy trình tốt nhưng **chỉ là trang giới thiệu**: không có bước thanh toán, xác nhận, giao hàng, pháp chế. Đây là khoảng trống lớn nhất.
4. Máy đo hiện chỉ đo giao diện (chụp 360/1280, onbrand ≥ 85, axe). Thiếu máy đo **đơn đi trọn** và **webhook đúng**; hai thứ này mới là điều kiện "đạt" của đề.
5. Chưa có bản vàng đã xem tận mắt; dưới đây là ứng viên, cần Linh hoặc Claude máy cty mở xem rồi mới chốt.

## Quy trình đề xuất
| Bước | Việc | Ai |
|---|---|---|
| 0 | Kiểm sự kiện (giá, tên sản phẩm, điều khoản) trước khi thiết kế (garden-skills Step 0) | Claude |
| 1 | Đề bài 11 mục + thêm 4 mục: giá, nội dung cần thu (tối thiểu), cách giao, chính sách hoàn trả | Claude → Linh duyệt giá (D2) |
| 2 | Moodboard 6–12 trang + 1–2 bản vàng | Claude in Chrome |
| 3 | Kế hoạch token 4–6 màu, chữ, bố cục; tự so với "mặc định AI" rồi sửa (frontend-design) | Claude |
| 4 | Dựng trang + biểu mẫu + trang QR | agy |
| 5 | Dựng phía máy chủ: tạo đơn, mã thanh toán, webhook, giao hàng (khuôn dùng lại cho mọi OPC) | agy |
| 6 | Pháp chế: chân trang, chính sách, câu đồng ý dữ liệu | Claude (ra-phap-che) |
| 7 | Chạy bộ máy đo bên dưới, tối đa 3 vòng, tệ hơn thì hoàn tác | Claude chấm, tách khỏi thợ |
| 8 | Linh duyệt D4 | Linh |

## Máy đo + ngưỡng (rẻ → đắt)
**A. Tự động, không cần người**
- Đơn đi trọn trên sandbox: tạo đơn → QR → gửi webhook giả có chữ ký → trang tự báo đã trả → thư/liên kết giao đến ≤ 60 giây. Ngưỡng: 3/3 lần qua.
- Webhook: chữ ký sai bị từ chối; lệch giờ > 5 phút bị từ chối; gửi 2 lần chỉ giao 1 lần; tiền trả thiếu không giao, trả thừa vẫn giao; luôn trả 200. Ngưỡng: 5/5 ca. (Theo SePay: "Always compare transferAmount from the webhook with the order amount. Only confirm payment when the transferred amount is ≥ the order amount.")
- Chụp 360 và 1280: không tràn ngang, chữ thân ≥ 16px, nút bấm ≥ 44px (mức 44px là ngưỡng đề xuất, không phải trích nguồn).
- Tương phản: thân ≥ 4,5:1, chữ lớn ≥ 3:1 (impeccable craft-floor). Lưu ý brand-chiemtinh đã tự cấm vàng kim làm chữ trên nền kem (1,95:1).
- axe 0 lỗi nặng; `onbrand-cham` ≥ 85 (đã có).
- Quét từ cấm của brand (giải hạn, chắc chắn sẽ…): 0 lần.
- Số bước từ vào trang tới thấy QR ≤ 3; số ô phải nhập ≤ mức tối thiểu của đề bài (mẫu Baymard: 7 ô cho cả thanh toán đầy đủ).
- Tải trang: đo LCP bằng Lighthouse trên giả lập điện thoại; ngưỡng đề xuất ≤ 2,5 giây (ngưỡng "tốt" của Google, chưa kiểm lại nguồn trong phiên này).

**B. Rubric chấm mù** (người chấm không thấy lý do của thợ, 5 chiều, mỗi chiều 1–5, qua khi trung bình ≥ 4 và không chiều nào < 3): một chủ thể rõ trong 3 giây · hiểu sản phẩm làm gì trong 5 giây · tin cậy (giá, hoàn trả, liên hệ) · độc đáo, không "mùi AI" (danh sách của frontend-design) · đúng brand.

**C. Pháp chế**: 0 lỗi đỏ theo danh mục kiểm. Danh mục lấy từ kết quả DR; đã biết: công bố chính sách kiểm hàng, hoàn trả (NĐ 85/2021), đồng ý dữ liệu cá nhân theo luật 91/2025.

**D. Linh**: D2 (giá, hướng), D4. Số lần chạm ≤ 2.

## Bản vàng (ứng viên, chưa xem)
Chưa tải được mẫu vào `vang/`. Mốc đã có nguồn: taste-skill nói chuẩn của nó là "figma.com and x.ai" (SKILL.md, dòng 'are the bar'). Ứng viên cần mở xem: trang sản phẩm số trên land-book.com, lapa.ninja, godly.website (đã có trong skill web-thiet-ke); trang bán báo cáo cá nhân quốc tế; chiemtinh.vn bản hiện tại làm mốc "trước". **Việc kế**: Claude máy cty chụp 3–5 trang, ghi vì sao tốt, bỏ vào `vang/`.

## Sửa vào skill nào
- `web-thiet-ke`: thêm bước 5b "thanh toán và giao" (ghi chú trỏ khuôn), thêm vào bước 6 các máy đo A ở trên; thêm bước kế hoạch-so-với-mặc-định-AI; bước 0 kiểm sự kiện; đưa danh sách "Refuse" của impeccable vào bước tự kiểm.
- Thêm khuôn `khuon/thanh-toan-qr/` (tạo đơn, QR, webhook có chữ ký, giao) và bộ test sandbox.
- Skill `ra-phap-che` (LAB107): không có trong `skills/` của repo này; cần tìm nguồn hoặc tạo. [chưa kiểm LAB107 trên máy này]
- `brand-chiemtinh`: giữ; thêm câu đồng ý dữ liệu sinh (ngày, giờ, nơi) khi có kết quả DR.
- Thừa: bước ChatGPT ảnh đích cho trang bán nhỏ có thể bỏ khi có bản vàng thật.

## Rủi ro
- Luật thay đổi (luật dữ liệu 2025 mới hiệu lực), chỉ có tóm tắt từ báo luật; cần luật sư xác nhận.
- Ngân hàng đổi nội dung chuyển khoản (bỏ dấu gạch) → khớp đơn sai; cần khớp nhiều lớp.
- Webhook mất → khách trả tiền nhưng không nhận hàng; cần nút "tôi đã chuyển" kiểm tay và đối soát cuối ngày.
- Mã nguồn ngoài là dữ liệu, không chạy; chưa thử taste-skill gate trên máy này.

## Nguồn
[đọc] taste-skill, impeccable, anthropics/skills frontend-design, garden-skills web-design-engineer, vercel web-design-guidelines (SKILL.md) · [đọc qua tóm tắt] SePay QR, SePay webhook Node, SePay best-practices · [chỉ thấy] Casso, Baymard, Unbounce, luatvietnam NĐ 85/2021, luật dữ liệu 2025. Link đầy đủ ở `NGOAI.md`.
