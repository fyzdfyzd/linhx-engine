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

## Bổ sung vòng 2
Ngày 9/11/2026. Đọc thêm bằng WebFetch (qua tóm tắt, không phải nguyên trang), chạy thử máy đo trên máy này. Phần WF14 (ArcFace) không thuộc WF02, bỏ qua.

### 1. Ngưỡng tự đề xuất của vòng 1 nay đã có nguồn
| Ngưỡng | Kết quả | Nguồn |
|---|---|---|
| LCP ≤ 2,5 giây | Đúng. Nguyên văn: "sites should strive to have Largest Contentful Paint of 2.5 seconds or less"; 2,5–4,0 giây là cần cải thiện, trên 4,0 giây là kém; đo ở phân vị 75, tách điện thoại/máy tính ("a good threshold to measure is the 75th percentile of page loads, segmented across mobile and desktop devices"). Sửa máy đo: đo p75, không đo một lần. | https://web.dev/articles/lcp |
| Nút ≥ 44px | **Phải sửa lời.** WCAG 2.2 mức AA (2.5.8) chỉ đòi 24×24 CSS px: "The size of the target for pointer inputs is at least 24 by 24 CSS pixels". 44×44 là mức AAA (2.5.5 Enhanced). Đề xuất: 24px là mức cứng; 44px là mức mục tiêu cho nút chính trên điện thoại (nút "tôi đã chuyển", nút trả tiền). | https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html |

### 2. Số liệu Baymard (đọc trang gốc, sửa vòng 1)
Vòng 1 ghi "48% vì phí phát sinh" và "12 phần tử" từ kết quả tìm kiếm. Trang gốc hiện ghi (qua tóm tắt WebFetch): tỉ lệ bỏ giỏ trung bình **70,22%** (50 nghiên cứu, 2006–2025, khoảng 55–84%); lý do: **40%** phí phát sinh, 20% giao chậm, 19% lo an toàn thẻ, **18% bắt tạo tài khoản**, 17% thanh toán dài/rối; biểu mẫu trung bình 23,48 phần tử, lý tưởng **12–14**. Sửa máy đo: số phần tử biểu mẫu mục tiêu ≤ 12–14 (không phải "7 ô"), và đề bài ghi rõ "không bắt tạo tài khoản". Lưu ý: số của TMĐT Mỹ/EU, hàng vật lý; không có số cho Việt Nam. https://baymard.com/lists/cart-abandonment-rate

### 3. Unbounce (đọc trang gốc)
Báo cáo 2024: trung vị chuyển đổi **6,6%**, theo ngành 3,8–12,3%; 83% lượt xem trên điện thoại; "nearly 5x more visitors" trên điện thoại nhưng "desktop converts 8% better"; mẫu 41.000+ trang, 464 triệu khách. Chữ viết ở trình độ lớp 5–7 chuyển đổi 11,1%, cao hơn 56% so với lớp 8–9. **Sửa vòng 1**: "điện thoại 8,3% so với máy tính 11,6%" lấy từ kết quả tìm kiếm, không thấy ở trang gốc, bỏ cho đến khi kiểm được. Dùng được: thêm "câu chữ đơn giản" vào rubric (mốc tham khảo, mẫu quốc tế, không phải ngưỡng cứng). https://unbounce.com/conversion-benchmark-report/

### 4. SePay webhook: xác minh chữ ký (đọc lại trang Node.js)
Header: `x-sepay-signature`, `x-sepay-timestamp`. Chữ ký: `"sha256=" + crypto.createHmac('sha256', secret).update(timestamp + "." + body)`. Chống phát lại: `Math.abs(Date.now() / 1000 - timestamp) > 300` (300 giây). Mã trả về: **401** khi chữ ký sai, **400** khi body không hợp lệ/trống, **200** `{success:true}` khi thành công.
**Sửa vòng 1**: máy đo ghi "luôn trả 200". Theo tài liệu SePay thì chữ ký sai/lệch giờ trả 401; chỉ ca hợp lệ (kể cả trả thiếu, gửi trùng) trả 200. Ca webhook đổi thành: sai chữ ký → 401, lệch giờ → 401, còn lại 200. https://developer.sepay.vn/en/sepay-webhooks/lap-trinh-webhooks/lap-trinh-webhook-nodejs

### 5. Casso: vẫn mỏng
`https://developer.casso.vn/v1/thuc-hanh` chỉ ra mục lục; trang con "Tích hợp xác nhận thanh toán" chưa mở được; trang nói có bản `.md` cạnh mỗi trang và `llms.txt`. Chưa trích được gì nguyên văn. Việc kế: máy công ty mở (xem `DR/DE-2.md`).

### 6. Luật: chỉ thêm được một mảnh
Luật Bảo vệ quyền lợi người tiêu dùng 19/2023/QH15 (bản caselaw.vn, qua WebFetch): Điều 38 khoản 3 điểm b cho người tiêu dùng quyền "đơn phương chấm dứt thực hiện hợp đồng đã giao kết và thông báo cho tổ chức, cá nhân kinh doanh" trong **30 ngày** kể từ ngày giao kết, áp dụng khi bên bán cung cấp thông tin không chính xác hoặc không đầy đủ theo Điều 37; hoàn tiền trong 30 ngày kể từ khi người tiêu dùng thông báo. (Tóm tắt của công cụ, không phải nguyên văn điều luật.) Hệ quả cho trang bán: thông tin sản phẩm, giá, điều khoản phải đầy đủ, nếu thiếu khách có thể đòi huỷ trong 30 ngày. https://caselaw.vn/van-ban-phap-luat/411464-luat-bao-ve-quyen-loi-nguoi-tieu-dung-so-19-2023-qh15-ngay-20-06-2023-cua-quoc-hoi
**Chưa tìm được**: điều khoản nói rõ sản phẩm số giao ngay có được từ chối hoàn trả không; văn bản gốc NĐ 85/2021 và luật dữ liệu (thuvienphapluat.vn bị 403 ở vòng 1, vòng 2 chưa thử lại). Vẫn cần luật sư.

### 7. Thử máy đo trên máy này (lệnh và kết quả thật)
Thư mục `DO-THU/`.
- **Máy đo webhook 5 ca**: viết `DO-THU/webhook-5ca.mjs` (mã tự viết, không mạng, không gói ngoài; mô phỏng bên nhận theo định dạng chữ ký ở mục 4). Lệnh: `node webhook-5ca.mjs` (Node v24.21.0). Kết quả: **5/5 qua** (chữ ký sai 401; lệch giờ 400 giây 401; trả thiếu 200 không giao; trả thừa giao; gửi lại cùng id chỉ giao 1 lần). Giới hạn: đây là bản tham chiếu do tôi viết, **không phải đo một hệ thống thật**; chỉ chứng minh 5 ca viết được thành bài thử chạy tự động.
- **Máy đo `onbrand-cham`** (script có sẵn `LAB/LAB043-DESIGN-ONBRAND/src/linhx-onbrand/scripts/onbrand.py`). Lệnh: `python onbrand.py cham LAB/LAB043-DESIGN-ONBRAND/brands/btmh/brand.json LAB/LAB012-BRAND-STANDARD/brands/chiemtinh/guideline/chiemtinh-brand-guideline.html --ra DO-THU/onbrand-thu.json`. Ba phát hiện thật:
  1. `brand.json` của chiemtinh trong LAB012 **không chạy được** với máy này: `KeyError: 'trong_so_diem'` (khác lược đồ với LAB043). Nên "onbrand ≥ 85" cho chiemtinh hiện chưa chạy được; cần tạo brand.json đúng lược đồ.
  2. Chạy với brand.json btmh (chỉ để thử máy chạy; sai brand nên điểm không có ý nghĩa): ra 25/100 "LỆCH CHUẨN", nhưng **màu không chấm được với tệp .html** (ghi chú của máy: "không ra được ảnh (pptx cần LibreOffice)"), logo và bố cục chờ Claude nhìn. Với trang HTML, máy chỉ chấm chữ (font) và từ cấm. Muốn chấm màu trang bán phải chụp ảnh trang trước rồi chấm ảnh.
  3. Trên Windows mặc định, lệnh báo `UnicodeEncodeError` (cp1252) khi in dù đã ghi tệp; với `PYTHONUTF8=1` thoát mã 0. Cần ghi vào hướng dẫn chạy.
- Chưa thử: Lighthouse, axe, chụp 360/1280 (cần trình duyệt, theo lệnh không dùng Chrome); taste-skill gate (cần Node 22 và Chrome, mã ngoài, không chạy).

### 8. Còn thiếu sau vòng 2
Bản vàng chưa có (cần xem tận mắt, đã ghi `DR/DE-2.md`); Casso thân bài; văn bản gốc luật; số chuyển đổi/bỏ giữa chừng cho Việt Nam; open-design (nexu-io) chưa thử lại; bộ luật vercel web-interface-guidelines chưa đọc.
