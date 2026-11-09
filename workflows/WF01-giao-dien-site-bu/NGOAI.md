# Người ngoài đã làm: WF01 (gộp WF07)

Bước 0. Tìm sơ bộ 9/11 sáng; **đọc code 9/11 trưa** (clone về cloud, bản mới nhất trên GitHub). Đọc 5 nguồn, gồm 3 bên giao diện và 2 bên lịch/nội dung.

## Đã đọc code

| Nguồn | Bản đọc | Lấy | Bỏ |
|---|---|---|---|
| **taste-skill** (leonxlnx/taste-skill, `design-taste-frontend` 2.5) | f6b7657, 7/11 | (1) **Viết chữ trước, dựng sau**: bảng dữ kiện + thẻ giọng trước khi có bố cục. (2) **Cổng kiểm bằng script** chạy ở 1440/1024/768/390/320: tràn ngang, chạm ≥ 44px, đè chữ, ảnh rỗng, tốc độ; lỗi nào cũng chặn; chỉ được miễn bằng `waivers.json` có lý do. (3) Dữ kiện tự giả định gắn `data-assumed`, báo cáo liệt kê hết. (4) Cấm bịa nhận xét, khách, con số; ảnh thay thế phải khai là ảnh thay thế. (5) Loại doanh nghiệp quyết định khung trang (dịch vụ: ảnh người thật và công việc thật dẫn). | Bốc thăm bảng màu ngẫu nhiên (ta đã có token brand). copy-lint chỉ có từ điển tiếng Anh. Bộ kit Node 22 + WebGL quá nặng cho trang dịch vụ. Luật "mỗi khối đúng một màn hình" quá cứng. |
| **impeccable** (pbakaus/impeccable 4.8) | 4b6b80f, 8/11 | (1) **PRODUCT.md** (sự thật sản phẩm: ai dùng, việc gì, khác ở đâu) tách khỏi **DESIGN.md** (thế giới thị giác). (2) Bốn chế độ trang: Thuyết phục / Thao tác / Đọc / Trải nghiệm; trang chủ BU là Thuyết phục, công cụ T1/T2 là Thao tác. (3) Danh sách "từ chối" chống mùi AI: nhãn nhỏ trên tiêu đề, 01/02/03 khi không phải trình tự, lưới thẻ giống hệt nhau, chữ gradient, kính mờ trang trí, viền trái màu. (4) Rubric kỹ thuật 5 mục × 0–4 = /20 (a11y, tốc độ, token, responsive, toàn vẹn). | Binary detector tải ngoài (không chạy trong sandbox máy cty). Lệnh live/variant. Luật cấm chữ gradient: **brand thắng** (Sakédemy v1.0 Linh duyệt có chữ gradient theo guideline). |
| **frontend-design** (anthropics/skills) | 2c5958e, 6/11 | (1) Năm cụm "mặc định AI" để soi: nền kem + serif + cam đất; **nền gần đen + một màu nhấn chói**; báo kẻ chỉ; bộ thẻ SaaS; nhãn IN HOA, dấu "·", mũi tên "→" trên nút. (2) Hai lượt: lên kế hoạch token → **soi kế hoạch với đề** ("đề khác có ra y hệt không?") → mới dựng. (3) Dồn táo bạo vào một chỗ. | Không có gì đáng bỏ; ngắn, dùng làm luật nền. |
| **marketingskills / social** (coreyhaines31 2.4) | 96798cf, 6/11 | (1) 3–5 trụ nội dung có tỉ lệ %. (2) Một bài gốc dài → bóc thành mảnh cho từng kênh. (3) **Danh sách dấu hiệu văn AI** cho bài MXH: "không phải X mà là Y", chuỗi phủ định, tự hỏi tự đáp, hai chấm bật mí, gạch ngang dài, mỗi câu một dòng, câu mồi "Bạn nghĩ sao?", emoji làm gạch đầu dòng. | Tần suất và thuật toán X, TikTok theo thị trường Mỹ. |
| **claude-repurpose / repurpose-calendar** (agricidaniel) | 669187e, 10/4 | (1) Bảng lịch: Ngày, Giờ, Kênh, Loại bài, **File**, Cần ảnh, Ghi chú. (2) Luật: ≤ 3 bài/ngày, mỗi bài một kênh khác; bài dài đi trước, mảnh ngắn theo sau; cùng một kênh cách nhau ≥ 2 ngày. (3) Nhắc trả lời bình luận trong giờ đầu. | Khung 7 ngày cố định theo "ngày chủ đề"; kênh không dùng ở VN (Snapchat, Quora, Skool, Reddit); giờ đăng theo Mỹ. |

Chưa đọc code, lý do: web-design-engineer (garden-skills), minoan-frontend-design, ag-kit frontend-design là biến thể của frontend-design; ClaudeKit social đã học ở LAB072; claude-gtm-plugin social-media-management trùng marketingskills.

## So với skill LINHX đang có

| Skill LINHX | Đã tốt hơn bên ngoài | Còn thiếu, lấy từ bên ngoài |
|---|---|---|
| `web-thiet-ke` (LAB058) | Moodboard thật, ảnh ChatGPT làm đích, token từ brand.json, bắt mở trang ứng dụng guideline, chấm `onbrand-cham` | Viết chữ trước; bảng dữ kiện + `data-assumed`; cổng script nhiều cỡ (đang chỉ 360/1280); danh sách "từ chối" mùi AI; rubric kỹ thuật /20; bước soi kế hoạch với đề; form lead nối CRM |
| `brand-ifagent` | Luật màu, chữ, tương phản, giọng rất kỹ | **Đã cũ**: vẫn ghi "AI Event Technology" và "không ghi CEO"; Linh 6/11 đã chuyển ifagent.net về Agent Force, CEO Nguyễn Thị Hằng. Phải sửa trước khi dựng. |
| `chuyen-kenh`, `tao-bai`, `duyet-dang`, `ban-dang`, Postiz | Khuôn từng báo, người ảo, hàng duyệt, lớp đăng | Không có **lịch BU nhiều kênh** gắn file + link đo; không có luật giãn bài; soat-giong thiếu bản tiếng Việt của danh sách dấu hiệu văn AI |
| `onbrand-cham` | Chấm 100 điểm theo guideline | Không chấm được "mùi AI" của bố cục; cần thêm bước soi 5 cụm mặc định |

## Đổi vào skill (áp ngay ở vòng 1, ghi bằng chứng vào BAI-HOC.md)
1. `web-thiet-ke` bước 1 thêm `PRODUCT.md` (JTBD, khách, cơ chế khác biệt, dữ kiện được phép nói) và **bảng dữ kiện**: số/case chưa có thật thì không lên trang, giả định phải gắn `data-assumed`.
2. Bước 3 thêm **soi kế hoạch với đề** + 5 cụm mặc định AI. Riêng ifAgent: nền tối + gradient xanh nằm sát cụm "nền gần đen + màu chói", nên điểm nhớ phải đến từ thứ thật (agent chạy trong Zalo, phiếu Khám), không đến từ màu.
3. Bước 6 thay "chụp 360/1280" bằng **cổng script** 1280/1024/768/390/360: tràn ngang, chạm ≥ 44px, ảnh rỗng, chữ < 16px, form gửi được; miễn lỗi phải ghi `waivers.json`.
4. Skill lịch kênh mới cho BU (hoặc thêm vào `chuyen-kenh`): bảng lịch có cột File, Link đo (`?kenh=`), Người duyệt, Trạng thái; luật ≤ 3 bài/ngày, cùng kênh cách ≥ 2 ngày, bài dài trước.
5. `soat-giong` thêm danh sách dấu hiệu văn AI bản tiếng Việt.

## Còn có thể tìm thêm (không chặn vòng 1)
Nhóm Facebook VN về growth B2B, bài LinkedIn VN về lịch nội dung; bên Trung Quốc (小红书 运营 SOP) khi làm Zalo OA.
