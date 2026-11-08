# Chuẩn slide (v0.3)

Mỗi chuẩn ghi ai chặn: `kiem-deck` (cổng 10, đọc 10-deck.json), `hanh-trinh` (cổng 10, đọc 10-hanh-trinh.json), `xem` (cổng 13, chụp slide thật bằng Playwright và đo trên điểm ảnh), hoặc mắt Claude/phản biện trên tờ ghép `13-claude-deck/xem/to-slide.png`. Nguồn ý tưởng ghi ở cột cuối; số liệu và luật cụ thể là của plugin.

| # | Chuẩn | Ngưỡng | Ai kiểm | Nguồn ý |
|---|---|---|---|---|
| C1 | Tiêu đề là một câu kết luận, một ý | 6–15 chữ, ≤ 2 dòng, không kết bằng `?` `:`; nối hai ý bằng "và" thì tách | kiem-deck, xem | Minto, *The Pyramid Principle* (action title) |
| C2 | Tóm tắt điều hành đứng đầu; đọc liền tiêu đề ra câu chuyện | `tom-tat` trong 4 slide đầu; ghost deck | kiem-deck | Minto (SCQA) |
| C3 | Một slide một điểm | `diem_chinh` ≤ 12 chữ bắt buộc; thử liếc 3 giây | kiem-deck, mắt | Duarte, *slide:ology* (glance test) |
| C4 | Một tiêu điểm, không hai khối ngang nhau | chỉ số tiêu điểm bắt buộc khi ≥ 2 khối; tiêu điểm to/đậm nhất; thu nhỏ còn thấy (nheo mắt) | kiem-deck, xem | Knaflic, *Storytelling with Data* (preattentive) |
| C5 | Màu nhấn chỉ ở tiêu điểm, phần còn lại xám | ≤ 2 chỗ dùng màu nhấn/slide | xem (cảnh báo) | Knaflic |
| C6 | Hình thức chứng minh: biểu đồ, bảng, số lớn, sơ đồ, minh hoạ | `hinh_thuc` khớp kiểu slide; slide toàn chữ chỉ được ở tóm tắt/khẳng định | kiem-deck | Duarte; Knaflic |
| C7 | Biểu đồ sạch | nhãn số ngay trên cột, không chú giải, không lưới, không viền, cột từ 0, không tròn/3D; số có BCxx + dòng nguồn | kiem-deck, renderer | Tufte, *The Visual Display of Quantitative Information* (data-ink) |
| C8 | Không trang trí thừa | chân trang mảnh một dòng; nhãn đặt cạnh thứ nó mô tả; không chiếu nguyên văn lời nói | renderer, mắt | Tufte; Mayer (redundancy) |
| C9 | Chữ đọc được khi chiếu | thân ≥ 28px (24–27 cảnh báo, < 24 lỗi); chỉ nhãn/chân trang được 24px | xem | |
| C10 | Không tràn, không lấn lề, không chồng chữ | 0 lỗi; lề 128px; đáy 920px khi có chân trang | xem | |
| C11 | Chữ trên ảnh đọc được, đo trên điểm ảnh thật | tương phản ≥ 4.5:1 (chữ < 24px) / ≥ 3:1 (chữ ≥ 24px) với nền ngay dưới chữ; chữ chỉ ở phía trống của ảnh | xem | WCAG 2.x (1.4.3) |
| C12 | Ảnh nền hoà vào slide | bìa/chương/kết/khẳng định: ảnh 16:9 tràn slide, chủ thể ở 1/3, phía chữ trống cùng tông nền, lớp phủ chuyển sắc (không dùng mask-image); không khung, không bệ, không bo góc | H10 (cổng 12), renderer, mắt | |
| C13 | Logo đúng chỗ, là tệp gốc | bìa: logo ta + logo khách trên thẻ sáng; chân trang: logo ta nhỏ; kết: cả hai | cổng 13 | |
| C14 | Cả bộ ảnh một phong cách | ảnh neo chung của brand; H4, H9 | cổng 12 | |
| C15 | Nhịp chú ý | câu móc ở 2 slide đầu; ≤ 2 slide nặng liền nhau rồi slide nghỉ; đặt lại chú ý mỗi ≤ 4 slide (trình bày) / ≤ 6 (gửi đọc); căng trước nhẹ; một khoảnh khắc đáng nhớ ở 50–80%; kết bằng một hành động | hanh-trinh | Duarte, *Resonate* (what is / what could be, STAR moment) |
| C16 | Trình bày và gửi đọc là hai tệp | `che_do`; trình bày: slide thưa, chi tiết trong ghi chú người nói; gửi đọc: tiêu đề tự giải thích | hanh-trinh | Duarte, *Slidedocs* |
| C17 | Đòn bẩy thuyết phục phải thật | không khan hiếm giả, không đếm ngược giả; mọi khẳng định có nguồn | kiem-deck (số có nguồn), phản biện | Cialdini (dùng có đạo đức) |

Không dùng các "con số chú ý" truyền miệng (chú ý 8 giây, 10 phút) trong slide hay luật: không có bằng chứng vững.

## Bố cục (thư viện `du-lieu/bo-cuc/thu-vien.json`)

Mỗi kiểu slide trong deck phải trỏ về một bố cục trong thư viện (`08-the-phong-cach.json` → `bo_cuc_slide`; `deck.py bo-cuc chon`). Bảy bố cục đã học từ deck đẹp (Dribbble, Pinterest, 13/10/2026): `toan-trang`, `nua-trang`, `so-lon-hero`, `nen-mem`, `the-nhan-manh`, `bieu-do-hero`, `bang-nhan-dong`. Chi tiết và công thức CSS: `skills/hinh-anh/references/bo-cuc-anh.md`.

## Cách dùng

1. `deck.py kiem-deck <dir>` và `deck.py hanh-trinh <dir>` tới khi sạch (C1–C7, C15–C16).
2. `deck.py xuat …` rồi `deck.py xem <dir>`: sửa tới khi `bao-cao.json` không còn lỗi (C9–C11). Lỗi thì sửa **nội dung** trong `10-deck.json`, không co chữ, không sửa tay HTML.
3. Mở `13-claude-deck/xem/to-slide.png` (Read), soát C3–C5, C8, C12–C14 bằng mắt; ghi lỗi vào `phan-bien/chuan-slide.json` dạng `{"slide", "chuan": "C4", "mo_ta", "sua"}`.
4. Phản biện (`phan-bien`) chấm `chuan_slide` 1–5: 5 = không lỗi; 4 = chỉ lỗi nhẹ C8/C12; 3 = lỗi C4, C5, C12 hoặc C14; ≤ 2 = còn lỗi máy kiểm được (lẽ ra cổng đã chặn: báo để sửa plugin).

## Xuất PPTX/PDF

Renderer chỉ dùng chuyển sắc (`linear-gradient`, `radial-gradient`) và ảnh `object-fit:cover`; không dùng `mask-image`, `mix-blend-mode`, `backdrop-filter`, `background-clip:text` vì chưa kiểm được khi Claude Slides xuất PPTX/PDF. Trước khi gửi khách, tải PPTX một lần và mở slide bìa để soát.
