---
name: dung-deck
description: Bước 10 và 13 của quy trình deck proposal - viết ghost deck bằng tiêu đề kết luận, dựng 10-deck.json theo khung proposal 6 phần phong cách tư vấn chiến lược, kiểm bằng script, rồi xuất và đăng lên Claude Slides theo Design System của BU. Dùng khi dựng slide proposal, pitch, đề xuất cho khách.
---

# Ghost deck, deck, Claude Slides (bước 10, 13)

Script: `python "${CLAUDE_PLUGIN_ROOT}/scripts/deck.py"`. Đọc trước: `references/khung-proposal.md` (mạch 6 phần, luật tiêu đề), `references/kieu-slide.md` (13 kiểu slide và trường dữ liệu), `references/chuan-slide.md` (12 chuẩn slide, ai kiểm).

## Bước 10a. Ghost deck

1. Kiểm cổng 1 (chốt tối thiểu đã có), 6, 7, 9 đạt.
2. Viết `10-deck.json` chỉ với `id`, `kieu`, `phan`, `tieu_de` cho mọi slide (chưa viết thân).
3. `deck.py ghost <dir>` in `10-ghost-deck.md`. Đọc mục "Đọc liền": phải ra một lập luận trọn vẹn, theo trình tự đã chọn ở bước 3. Tiêu đề nào không nối được thì sửa.
4. Gửi Linh ghost deck (chỉ danh sách tiêu đề). Linh duyệt → `deck.py duyet <dir> 10`.

## Bước 10b. Hành trình cảm xúc và chú ý

Đọc `references/hanh-trinh.md`. Viết `10-hanh-trinh.json` (một dòng mỗi slide: cảm xúc, tải chú ý 1–5, móc/nghỉ/đặt lại/khoảnh khắc; chế độ trình bày hay gửi đọc). `deck.py hanh-trinh <dir>` kiểm luật nhịp và vẽ `10-hanh-trinh.png`. Gửi Linh ghost deck **cùng** đường chú ý; Linh duyệt cả hai ở cổng 10.

## Bước 10c. Thân slide

- Mỗi slide nội dung: `diem_chinh` (≤ 12 chữ), `hinh_thuc` (biểu đồ, bảng, số lớn, sơ đồ, minh hoạ) và chỉ số tiêu điểm (`nhan_manh`, `dong_nhan`, `so_chinh`, `khuyen_nghi`, `bieu_do.diem_nhan`). Slide toàn chữ chỉ được ở tóm tắt và khẳng định. Chi tiết: `references/kieu-slide.md`.
- Số có trong bằng chứng thì ưu tiên đưa lên biểu đồ (`bieu-do`) hoặc số lớn, không viết thành câu.
- `deck.py bo-cuc chon <dir>`: mọi kiểu slide trỏ về một bố cục trong thư viện.

- Điền thân theo `kieu-slide.md`. Một slide một thông điệp; thân là bằng chứng cho tiêu đề.
- Số nào cũng có `bang_chung` (BCxx) trên slide đó, hoặc `minh_hoa: true` và chữ "minh hoạ" hiện trên slide.
- Mỗi slide có `ghi_chu` (lời nói, 60–150 chữ, viết như Linh nói). Trang có số thì ghi nguồn ở `nguon`.
- Tràn trần chữ thì **tách slide**, không co chữ, không bỏ bằng chứng.
- `deck.py kiem-deck <dir>` tới khi không còn lỗi. Còn `[Linh chốt]` là cảnh báo; bản cuối chạy `--ban-cuoi` thì thành lỗi.

## Bước 13. Đưa lên Claude Slides

1. Ảnh đã qua cổng 12. Tải từng ảnh lên deck bằng Artifact tool (`asset: true`) sau khi deck đã tạo; ghi `{ "<tep>": "/_blob/<id>" }` vào `13-claude-deck/anh-map.json`.
2. Logo (C8): `deck.py logo <dir> --khach <tệp logo khách> --khach-ten "<tên khách>"`. Logo ta tự lấy từ LAB012 (`logo_goc` trong `thuong-hieu.json`); logo khách lấy từ tệp của Linh hoặc trang chính thức của khách (Chrome, chỉ tải, chỉ dùng nội bộ cho proposal). Logo **không bao giờ** gửi cho ChatGPT vẽ lại. SVG: đổi sang PNG trước khi tải lên. Tải từng logo lên làm asset như ảnh, ghi vào `anh-map.json` với khoá là đường dẫn `logo/<tệp>`.
3. `deck.py xuat <dir> --anh-map <dir>/13-claude-deck/anh-map.json` dựng `13-claude-deck/project/` (deck.json + slides/*.html, font Google, bản ghi Design System) và `publish.json`. Bìa: logo ta + logo khách trên thẻ sáng; chân trang slide nội dung: logo ta nhỏ; slide kết: cả hai.
3b. `deck.py xem <dir>`: chụp từng slide, bắt tràn chữ, lấn lề, chồng chữ, chữ < 24 px (thân < 28 px cảnh báo), ô ảnh trống; đo tương phản chữ trên ảnh nền bằng điểm ảnh thật; kiểm tiêu điểm (có `data-hero`, nổi khi thu nhỏ, màu nhấn không rải nhiều chỗ, tiêu đề → tiêu điểm). Sửa trong `10-deck.json` tới khi đạt, rồi mở `xem/to-slide.png` soát C8, C10–C12 (`chuan-slide.md`). Cổng 13 không qua nếu chưa chụp hoặc slide đổi sau lần chụp.
4. Đăng: lần đầu tạo deck từ kiểu Slides (`type_url` của Slides, `title`), rồi publish với `url`, `root`, `file_path`, `files` theo `publish.json` (gồm cả `project/ds/<brand>/tokens.json` sao từ Design System). Lần sau chỉ gửi tệp đổi. `root` phải nằm trong thư mục làm việc hoặc scratchpad của phiên: nếu thư mục deck ở ổ gắn ngoài (ví dụ `/mnt/...`), chép `13-claude-deck/` sang scratchpad trước rồi đăng từ bản chép.
5. Ghi link: `deck.py duyet <dir> 13 --nguoi Claude --link <url>`. `deck.py cong <dir> 13`.
6. Linh muốn PowerPoint: dùng nút tải pptx/PDF của Claude Slides; nếu cần tệp sửa sâu thì dùng skill pptx dựng lại từ `10-deck.json`.
