# Đề xuất quy trình giao diện BU (bản 0.1, 9/11) · thử đầu trên event.ifagent.net

Linh 9/11 11:43: đích là **event.ifagent.net** (lấy lead), không phải ifagent.net; dùng lại quy trình đã có trong các lab, thêm Stitch, bài học khác, tìm tham chiếu, khoá giao diện.

## 1. Không viết skill mới: xương sống là `thiet-ke` nhánh landing (LAB106)
Đã có sẵn trong `linhx-engine/skills/le/thiet-ke` và đã gom LAB058 + LAB043 + stageshow + Appllama:
- 4 pha D1 Khám phá → D2 Định hướng (**Linh chọn**) → D3 Dựng → D4 Chấm và hoàn thiện (**Linh duyệt**), khớp KHUNG-CHUAN.
- Luật: có bộ design gốc thì AI không vẽ chữ/logo/giao diện; tham chiếu phải do người thật làm; bản vàng làm thước; chấm mù ≥ 2/3 đoán AI là trượt; sửa ≤ 3 lỗi/vòng, ≤ 3 vòng.
- Kiểm máy `kiem_thiet_ke.py --nhanh landing --pha d1|d2|d4` + Playwright 360/390/768/1280, đi trọn đường tới form.
- `web-thiet-ke` (LAB058) giữ làm phần chi tiết bước dựng: token từ brand.json, ảnh ChatGPT chỉ làm đích nhìn và thành phần, bản HTML một file khi gửi Linh.

## 2. Thêm vào (lấy từ lab khác và từ bên ngoài)
| # | Thêm gì | Từ đâu | Vào pha |
|---|---|---|---|
| 1 | **Tìm tham chiếu từ kho trước**: `hinh_tim` của kho mayquet (landing, đối thủ), thiếu mới lên land-book, godly, lapa, Refero, Mobbin qua Chrome máy cty; lấy 5 trang thắng, đi trọn hành trình, ghi `MAU-HINH.md` (ai cũng làm / người giỏi nhất làm / cả bọn làm dở) | thiet-ke, Appllama, mayquet | D1 |
| 2 | **Đối thủ event tech**: trang của các bên làm AI activation, photobooth, kiosk tương tác (VN + quốc tế), đi trọn tới form "gửi brief" | proposal-ideas (đã có nghiên cứu event tech thế giới) | D1 |
| 3 | **Bảng dữ kiện + PRODUCT.md**: số, khách, ảnh chưa có thật thì không lên trang; giả định gắn `data-assumed` | taste-skill, impeccable | D1 |
| 4 | **Stitch phác 3 hướng**: mô tả + DESIGN.md brand → Stitch ra 3 màn (tài khoản Ultra máy cty, LAB112 `tho-stitch`), Claude chỉnh về token thật; nhanh hơn tự dựng HTML từng hướng | LAB112, GOI-Y-THEM LAB058 | D2 |
| 5 | **Soi kế hoạch với 5 cụm mặc định AI** (nền gần đen + màu chói, bộ thẻ SaaS, nhãn IN HOA...). ifAgent nền tối + gradient xanh nằm sát cụm này, nên điểm nhớ phải từ ảnh sự kiện thật và demo chạy thật | frontend-design, impeccable | D2 |
| 6 | **Khoá giao diện** (mục 3 dưới) | features.khoa của engine, thẻ phong cách LAB031 | sau D2 và sau D4 |
| 7 | **Cổng script nhiều cỡ**: 1280/1024/768/390/360, tràn ngang, chạm ≥ 44px, chữ sát mép, ảnh rỗng; miễn lỗi phải ghi `waivers.json` có lý do | taste-skill gate, thiet-ke landing.md | D4 |
| 8 | **Chữ trước, giao diện sau**; danh sách dấu hiệu văn AI tiếng Việt cho mọi chữ trên trang và bài MXH | taste-skill copy, marketingskills | D1–D4 |
| 9 | **Thử với persona ảo** LAB048 (5 chủ agency/brand manager) đọc màn đầu: bán gì, bấm đâu | GOI-Y-THEM LAB058 | D4 |

## 3. Khoá giao diện (đề xuất mới, cần Linh duyệt)
Sau D2 khoá **hướng**, sau D4 khoá **bộ giao diện BU** để mọi trang con, bài MXH, Zalo OA, bản tin về sau không trôi:
- Bộ khoá: `DESIGN.md` (sinh từ brand.json, chuẩn Stitch đọc được) + `tokens.css` + khuôn khối đã duyệt + 3 ảnh chụp vàng (360/1280) + danh sách ảnh thật được dùng.
- Ghi băm vào `giao-dien.khoa` (cách `cong_kiem.py khoa` của engine). Đổi bất kỳ file nào phải qua Linh; agy chỉ được dùng, không được sửa.
- Kiểm trôi: mỗi trang mới chụp so với ảnh vàng + `onbrand-cham` ≥ 85; bài MXH dựng từ khuôn ấn phẩm của cùng bộ khoá.
- Engine: `site.json` của BU trỏ tới bộ khoá; khuôn Trang BU (C1) đọc token từ đó, nên BU thứ hai (C4) chỉ thay bộ khoá.

## 4. Áp vào event.ifagent.net (vòng 1)
- Mục tiêu một câu: agency/nhãn hàng **gửi brief** hoặc **đặt demo tại sự kiện**; mọi khối dẫn về form ghi CRM (engine C2).
- Brand: `brand-ifagent` đúng cho event (AI That Activates), dùng nguyên.
- Tài sản có thật: demo.ifagent.net (4 nhân vật AI, AI Photobooth, Minigame QR, "Gửi brief nhận demo"), proposal-studio, trailer CSMO do nhân vật AI dẫn.
- Thiếu: xem `NOI-DUNG-BU.md`.
