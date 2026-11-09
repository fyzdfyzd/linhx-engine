---
name: bu-frontpage
description: Dựng trọn mặt tiền web của một BU B2B (trang chủ lấy lead, 15–20 trang con, form brief + gọi lại, GEO, own media 3 pha) từ khuôn đã chạy thật ở event.ifagent.net, khoá giao diện và qua cổng máy K1–K10. Dùng khi Linh bảo làm site, landing, trang lấy lead hay own media cho một BU (IF Agent, Unikon, TUVA, Sakédemy...). Không đụng lõi engine.
---

# bu-frontpage

Bản mẫu chạy thật: `khuon/` (IF Agent Event, Linh duyệt 9/11/2026). Quy chuẩn: `references/quy-chuan.md`. Mục lục yêu cầu BU B2B: `references/muc-luc-b2b.md`. Own media mẫu: `references/vi-du-own-media/`.

## Luật cứng
1. **Trang chủ và form lấy lead đi trước mọi thứ khác** (Linh 9/11). Trang con, bài viết chỉ làm khi trang chủ đã qua cổng.
2. **Phạm vi**: frontend, giao diện, flow, own media, GEO. Không đụng lõi (CRM, chăm sóc tự động, thu tiền). Form nối `server.mjs` nhỏ; khi lõi xong chỉ đổi hàm `guiDi()`.
3. **Không bịa**: giá, thời gian dựng, case, số, tên khách, lời khen. Số chưa chốt để ở `public/cau-hinh.json` (null thì trang giữ chữ an toàn) hoặc gắn `data-can-xac-nhan`; trang chưa đủ dữ liệu có khối `ghi_chu`. Không có case thật thì **không có khối case**.
4. Ô đồng ý **không tick sẵn**; server lưu câu đồng ý, thời điểm, IP.
5. Brand lấy từ LAB043 (`/mnt/project-files/LAB043-DESIGN-ONBRAND/brands/<id>/`): logo SVG, màu, phông thật. Đọc trang ứng dụng website trong guideline trước khi dựng (bài học Sakédemy 20/10).
6. Mỗi lần Linh phải bấm duyệt trên máy, ghi rõ máy nào (MSI hay máy cty DESKTOP-PVHR2CD).

## Quy trình
| Bước | Việc | Đầu ra | Cổng |
|---|---|---|---|
| 0 | Chép `khuon/` sang thư mục việc của BU. Đọc `references/muc-luc-b2b.md`, lập bảng ✓/◐/✗ cho BU này | `MUC-LUC.md` | |
| 1 | Đầu vào: chân dung người mua, **ba câu người mua hỏi đầu tiên**, định vị một câu, danh mục giải pháp theo đầu ra, gói/offer, bằng chứng có thật, liên hệ thật | `PRODUCT.md` + bảng dữ kiện | thiếu liên hệ thật thì dừng |
| 2 | Viết **chữ trang chủ trước** (hero trả lời 3 câu trong 10 giây, giải pháp, gói, cách làm, form, hỏi đáp), soát văn AI tiếng Việt | chữ trong `public/index.html` | |
| 3 | Token từ brand vào `:root` của `site.css`, `DESIGN.md`. Dựng **3 phương án màn đầu** khác hẳn nhau (khác bố cục và câu chuyện, không chỉ khác màu), chụp 1280 + 390 ghép một ảnh | `anh-chup/3-phuong-an.png` | **D2: Linh chọn** (10 phút không trả lời thì đi theo khuyến nghị) |
| 4 | Khoá phương án: bỏ PA thừa, `node kiem/kiem.cjs <url> --chup-chuan` sinh `DESIGN.khoa` + ảnh chuẩn 5 cỡ | `DESIGN.khoa`, `khoa/anh-chuan/` | |
| 5 | Trang con: sửa `nguon/_trang-bu.py` (hoặc `nguon/*.json`), đầu/chân trong `tao-trang.py` (tên brand, SITE, nav, chân trang), chạy `python3 tao-trang.py` | 15–20 trang + sitemap | |
| 6 | GEO: JSON-LD (Organization, Service, FAQPage, Breadcrumb, Article), `robots.txt`, `llms.txt`, ảnh OG (`nguon/og.html` → `public/img/og.png`), bài trụ cho cụm từ BU muốn sở hữu | | |
| 7 | Own media: lịch theo pha (hoặc 14 ngày nếu không có sự kiện), toàn văn bài từng kênh, thư follow-up 24 giờ, soát giọng; link `?kenh=<kênh>-<mã>&utm_*` | `own-media/*.md` | chủ BU duyệt giọng |
| 8 | Cổng máy (dưới) + soát mắt trang chủ desktop/điện thoại như designer khó tính nhất, sửa lỗi lớn nhất trước | | **D4: Linh duyệt** |
| 9 | Đóng gói zip + README triển khai + danh sách việc chủ BU phải đưa | | |

## Trang tối thiểu (P0)
Trang chủ · giải pháp tổng + từng giải pháp · gói và giá · dự án/case (khung) · giới thiệu · liên hệ (form) · hỏi đáp · cẩm nang + bài trụ · cảm ơn (có mã lead) · chính sách dữ liệu (nháp, chờ pháp chế) · 404. P1: theo loại khách/ngữ cảnh, đối tác/agency, mẫu sản phẩm bàn giao (ví dụ mẫu báo cáo).

## Form lead
- Form chính (brief/đăng ký): bắt buộc tối thiểu, một trong hai điện thoại/email, đồng ý, bẫy bot, giữ nguồn `kenh`+utm theo phiên.
- Form gọi lại nhanh: tên + số + đồng ý (`loai: "goi-lai"`).
- Nút Zalo nổi trên điện thoại, ẩn khi đang ở vùng form. Gửi xong chuyển `/cam-on/?ma=`.
- Server: `RATE_MAX`, `TRUST_PROXY`, `TG_TOKEN`/`TG_CHAT`, `SHEET_WEBHOOK`, `LEAD_DIR`. Không ghi bí mật vào repo.

## Cổng máy `node kiem/kiem.cjs <url>` (cần Playwright; chạy server với `RATE_MAX=1000`)
K1 băm khoá · K2 màu ngoài token (cảnh báo) · K3 tràn ngang · K4 chạm ≥ 44 px (link trong câu được miễn theo WCAG 2.5.8) · K5 chữ < 14 px · K6 ảnh hỏng · K7 hai form gửi được · K8 màn đầu khớp ảnh chuẩn (≤ 100 điểm lệch) · K9 link nội bộ hỏng · K10 title ≤ 70, description 50–160, một h1, canonical, JSON-LD hợp lệ.
Đổi giao diện có chủ đích thì Linh duyệt rồi mới `--chup-chuan` lại.

## Sau cổng máy
Soát 5 cụm mặc định AI (`../thiet-ke/references/chong-mui-ai.md`), kiểm bàn phím trên form, chấm mù 3 người (≤ 1/3 đoán AI làm), onbrand-cham ≥ 85.

## Bẫy đã gặp
- Hai form cùng trang: mọi selector trong test và JS phải có phạm vi (`#form-brief [name=...]`), không dùng `.form-msg` trần.
- Ảnh chuẩn chụp lúc có hoạt ảnh sẽ lệch: chụp với `reducedMotion: 'reduce'`, `animations: 'disabled'`.
- Giới hạn gửi theo IP làm cổng K7 trượt khi chạy nhiều lần: chạy server thử với `RATE_MAX=1000`.
- Không đổi DNS trang đang có lead thật trước khi chạy song song đủ; giữ đường dẫn cũ bằng 301.
