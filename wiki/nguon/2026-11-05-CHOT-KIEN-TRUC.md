# LINHX ENGINE · chốt kiến trúc (05/11/2026)

Thay cho bản tự viết lõi (KIEN-TRUC-LINHX-ENGINE.md và Claude Doc S6fTwDeW2…, nay chỉ để tham khảo).

## 1. Kiến trúc chốt: Frappe, ba tầng
```
TẦNG ĐIỀU HÀNH   site ops (Frappe): ý tưởng, đề, duyệt, phiếu agy, khách, đơn, nội dung, bảng tối giản
TẦNG THỢ         thợ agy trên máy/VPS (kéo phiếu), Claude chấm, Postiz đăng bài, cầu nối Zalo/Messenger
TẦNG SẢN PHẨM    mỗi sản phẩm một app Frappe (bộ não) + mặt tiền: Next.js, Zalo Mini App, bot, mobile/PWA
HẠ TẦNG          1 bench Docker trên VPS: site ops + site sản phẩm; Cloudflare phía trước; Postgres hoặc MariaDB
```
Luật:
1. Không sửa lõi Frappe. Đổi hành vi bằng hook trong app của mình.
2. Giá, đơn, quyền dùng chỉ nằm ở Frappe. Mặt tiền và kênh không chứa nghiệp vụ.
3. Frappe không gửi lệnh shell cho máy. Chỉ gửi đề và loại phiếu nằm trong danh sách cho phép.
4. CTS đang có khách giữ nguyên FastAPI, chuyển dần sau.

## 2. Ứng viên và so sánh
Điểm 1–5 theo mục tiêu "một nền, nhiều ý tưởng, launch nhanh, nhận cập nhật lõi". Giấy phép và cấu trúc đã xem trong code clone 05/11.

| Tiêu chí | **Frappe** | Odoo CE | Payload | Supabase + Next.js | Directus | Medusa | Tự viết (lõi CTS) |
|---|---|---|---|---|---|---|---|
| Giấy phép lõi | MIT | LGPL (Enterprise trả phí) | MIT | Apache 2.0 | BSL (miễn phí dưới ngưỡng doanh thu) | MIT | của mình |
| Ngôn ngữ | Python | Python | TypeScript | TypeScript + SQL | TypeScript | TypeScript | Python |
| Cắm module, đa site | 5 app + multi-site | 5 module | 4 plugin, multi-tenant | 2 | 3 extension | 4 module thương mại | 3 |
| Quản trị, phân quyền, duyệt sẵn | 5 | 5 | 4 | 1 | 4 | 3 | 2 |
| Bán hàng, đơn, thanh toán | 3 (tự viết SePay) | 4 | 3 (chỉ Stripe) | 1 | 1 | 5 | 4 (đã có) |
| Dịch vụ, B2B, CRM, CSKH | 5 (ERPNext, CRM, Helpdesk) | 5 (một số mục Enterprise) | 1 | 1 | 1 | 1 | 1 |
| CMS, SEO | 3 | 3 | 5 | 2 | 3 | 1 | 2 |
| AI, MCP | 4 (MCP trong lõi) | 2 | 4 (plugin MCP) | 3 | 3 | 2 | 2 |
| Cập nhật lõi do đội ngoài lo | 5 | 4 (lên bản lớn nặng) | 5 | 5 | 4 | 5 | 1 |
| Khớp code CTS, agy quen | 4 | 3 | 2 | 4 | 2 | 2 | 5 |
| Nhẹ khi vận hành | 2 (5 dịch vụ) | 2 | 4 | 5 | 4 | 3 | 4 |
| **Tổng /50** | **39** | 35 | 34 | 25 | 26 | 28 | 26 |

Vì sao chọn Frappe: cao nhất ở ba thứ khó tự làm nhất (quản trị và duyệt sẵn, dịch vụ/B2B, cập nhật lõi), cùng Python với CTS, giấy phép MIT.
Vai phụ được giữ: **Payload** nếu sau này cần content hub thật mạnh; **Medusa** chỉ để học cách chia module thương mại; **Odoo** là phương án dự phòng nếu Frappe vướng nặng (cùng loại, nhưng nhiều mục hay nằm ở bản trả phí).

Cũng đã cân, không vào bảng: **Django + Wagtail** (CMS/SEO rất mạnh, cùng Python, nhưng quản trị nghiệp vụ và workflow phải tự dựng nhiều; dự phòng cho content hub cùng Payload), **NocoBase** (low-code tool nội bộ nhanh, cộng đồng nhỏ, CMS yếu), **Strapi** (như Directus, workflow yếu). Phần cần realtime hoặc tải rất lớn có thể thêm Supabase làm dịch vụ riêng.
Bản sao trên máy công ty: D:\LINHX\LAB\LAB111-LINHX-ENGINE\KIEN-TRUC-CHOT.md (bản này ở thư mục chung là bản chính).

## 3. Tổ chức mã nguồn
| Repo | Chứa gì |
|---|---|
| `linhx-bench` | apps.json ghim phiên bản từng app, docker compose, deploy, CI, cấu hình site (không chứa bí mật) |
| `linhx_vn` | SePay, VietQR, đăng nhập Zalo, mẫu thư, hoá đơn VN |
| `linhx_quyen` | quyền dùng: cấp, kiểm, thu hồi; freemium, tín dụng, ghế |
| `linhx_ops` | dự án, ý tưởng, đề, Phiếu Agy, Workflow duyệt, nhật ký token, bảng tối giản |
| `linhx_kenh` | Zalo OA, Messenger, cầu nối Postiz, hộp thư chung |
| `linhx-mau` | mẫu app sản phẩm (`bench new-app` từ mẫu) + mẫu Next.js + bộ nghiệm thu chung |
| `linhx-tho` | script thợ nhận việc trên máy (Windows ẩn qua chay-an.vbs, Linux service) |
| `sp_<ten>` | mỗi sản phẩm một app: DocType riêng, động cơ, nội dung; kèm `web-<ten>` nếu có mặt tiền Next.js |

Mỗi repo giữ quy chuẩn hiện có: features-dotN.json khoá, tests/nghiem-thu, cong_kiem, nhánh tu-dong/* cho agy, Claude canh.
Site: `ops` (điều hành) và site sản phẩm tách riêng trên cùng bench; staging và production tách máy.

## 3b. Giao diện, CMS, SEO
- Frappe có: Website Theme (màu, font, SCSS), Jinja, Web Template/Web Page Block, Frappe Builder (app riêng), meta theo đường dẫn, sitemap, robots, redirect. Không có kho theme như WordPress.
- Cách LINHX: theme = gói token + ~8 khuôn trang Next.js (landing, sản phẩm, bài, danh mục, checkout, tài khoản…) trong `linhx-mau`; sản phẩm chọn theme bằng một dòng cấu hình trong Frappe; theme mới agy dựng từ ảnh tham chiếu theo web-thiet-ke (LAB058) → kho theme LINHX.
- Nội dung và meta soạn ở Frappe; Next.js dựng tĩnh/ISR sau Cloudflare; tự thêm schema.org, WebP, hreflang.
- Landing, trang chiến dịch: Frappe Builder để Linh hoặc người làm nội dung tự sửa, không cần agy (gần Elementor nhất; Builder là app riêng, kiểm giấy phép trước khi dùng).
- Module `SEO kit` dùng chung dựng một lần: schema.org, quản lý chuyển hướng 301, chấm meta, ảnh WebP.
- Phương án phụ: WordPress làm content hub cho đội content đông, Frappe lo nghiệp vụ, nối API. Chỉ dùng khi thật cần vì phải nuôi thêm PHP và vá plugin.

## 4. Các đợt triển khai (đơn vị phiếu ≤40 phút, gồm cả phiếu sửa)
| Đợt | Việc | Phiếu | Phụ thuộc |
|---|---|---|---|
| 0 | VPS staging + Docker + bench + CI | 4–6 | Linh cấp VPS |
| 1 | Phiếu thử Frappe K1 (đã viết) | 1–3 | đợt 0 |
| 2 | `linhx_ops` + `linhx-tho`: giao phiếu agy từ Frappe, chạy một phiếu thật | 8–12 | đợt 1 |
| 3 | `linhx_vn` + `linhx_quyen` | 10–15 | đợt 1 |
| 4 | `linhx-mau`: mẫu app, mẫu Next.js, công thức K0/K1, bộ nghiệm thu chung | 6–10 | đợt 3 |
| 5 | Sản phẩm đầu tiên từ danh sách của Linh (cỡ S hoặc M), đo thời gian golive thật | 8–30 | đợt 4 |
| 6 | `linhx_kenh`: Zalo OA, Messenger, Postiz; mẫu Zalo Mini App | 10–15 | đợt 3 |
| 7 | CTS chuyển dần (pay + order trước, user sau cùng) | ~300 | đợt 4, chạy song song bản cũ |
Đợt 2 và 3 chạy song song được.

## 5. Mẫu để Linh liệt kê dự án tối nay
| Tên | Loại (landing / sản phẩm số / dịch vụ / B2B / nền tảng) | Khách là ai, việc họ cần làm | Bán thế nào (lẻ, thuê bao, quà, B2B, đặt lịch…) | Kênh (web, Zalo, Messenger, mobile, live) | Có động cơ riêng không | Ưu tiên (1–3) |
|---|---|---|---|---|---|---|
| ví dụ: Lịch vận Tết | sản phẩm số | người muốn tặng quà Tết có ý nghĩa | lẻ + quà + B2B | web, Zalo | có (dùng lõi CTS) | 1 |

Có danh sách, em sẽ gom thành bản đồ: dự án nào dùng chung module nào, làm module nào trước thì mở được nhiều dự án nhất.

## 6. Cần Linh
1. VPS staging: dùng cloud nào (đang dùng cho CTS?).
2. Danh sách dự án theo mẫu mục 5.
3. Hạn mở mã AGPL 20/11: mở đúng hạn (em khuyên) hay lùi.

---
## Cập nhật 6/11/2026: bức tranh tổng thể (chờ Linh chốt)
- Bảng Phong Thần tab "Bức tranh": https://claude.ai/artifact/Wyeq3HaoB6pfgoeC11P2qY (db tong/buc_tranh; bản sao BUC-TRANH-TONG-THE-2026-11-06.json).
- ĐỔI so với bản 5/11 (đề xuất): MỘT site lõi chung cho mọi đơn vị (một người một hồ sơ). Chỉ tách site cho khách cài tại chỗ, dữ liệu nhạy cảm, xưởng clone. Module lõi gom vào app linhx_core; module dọc mỗi cái một app.
- Tái dùng PROTO 01–09 (D:\LINHX\PROTO máy cty): giữ logic, giao kèo, verify, cấu hình; bỏ server/dashboard riêng. 03 OPC OS là nguồn cho Làn A (khách) và B (tiền).
