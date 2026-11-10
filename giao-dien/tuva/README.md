# tuva.work · mặt tiền TUVA Communication (9/11/2026)

20 trang (trang chủ vi, trang chủ en, 3 dịch vụ + trang tổng, đề xuất tài trợ, bộ quy tắc AI, tự chấm, lĩnh vực, giới thiệu, liên hệ, hỏi đáp, cẩm nang + 2 bài trụ, chính sách dữ liệu, cảm ơn vi/en, 404). Ba form lead: trao đổi dự án (`loai: brief`), gọi lại (`goi-lai`), tải bộ quy tắc AI (`tai-bo-quy-tac`, nhận kèm kết quả tự chấm). Công cụ tự chấm 10 câu chạy bằng JS trên trang chủ và `/tu-cham-ai/`.

## Chạy
```
node server.mjs                                    # Node ≥ 18, không cần cài gói, cổng 8080
RATE_MAX=1000 PORT=8102 LINHX_FORM_URL=http://127.0.0.1:8999/nhan node server.mjs   # chạy thử với máy giả
```
Chuyển tiếp lead về engine qua `LINHX_FORM_URL` (mặc định `http://127.0.0.1/api/method/linhx_core.crm.api_form.nhan_form`), gắn `nguon: "tuva"`. Sau proxy HTTPS: `TRUST_PROXY=1`. Lead có mã `TV-yymmdd-xxxx`, câu đồng ý, thời điểm, IP, nguồn (`kenh`, utm), ngôn ngữ.

## Sửa nội dung
- Trang con: `nguon/_trang-bu.py` → `python3 nguon/_trang-bu.py && python3 nguon/_bai-tru.py && python3 tao-trang.py`.
- Bài trụ: `../own-media/bai-tru-*.md`.
- Liên hệ, PDF, lĩnh vực, pháp nhân: `public/cau-hinh.json` (null thì trang giữ chữ an toàn). Điền `pdf_bo_quy_tac` thì form tải hiện link tải ngay; điền `zalo` thì nút nổi trên điện thoại đổi thành Zalo; điền `email_cong_khai` thì báo lỗi form kèm đường lùi email.

## Giao diện đã khoá
Phương án B "Tự chấm ngay màn đầu". `DESIGN.md`, `DESIGN.khoa`, `khoa/anh-chuan/`. PA A và PA C ở `_phuong-an-bo/` (`python3 _phuong-an-bo/dung-pa.py` sinh lại; đổi sang PA khác thì chép khối `<section class="hero-…">` vào `public/index.html`, chạy cổng, Linh duyệt rồi `--chup-chuan`).
Cổng: `NODE_PATH=$(npm root -g) node kiem/kiem.cjs http://localhost:8102`.

## Triển khai
1. Chép thư mục lên VM, chạy `node server.mjs` sau Caddy/Nginx (HTTPS).
2. tuva.work đang là WordPress: lấy danh sách URL cũ, đặt 301 sang trang mới trước khi trỏ DNS. Không đổi DNS khi chưa chạy song song.
3. Khi lõi engine xong: chỉ sửa `guiDi()` trong `server.mjs`.
