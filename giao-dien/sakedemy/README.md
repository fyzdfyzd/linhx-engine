# sakedemy.com · mặt tiền lớp doanh nghiệp (bản dựng 9/11/2026)

**19 trang**, 3 form lead (đăng ký tư vấn lớp doanh nghiệp, gọi lại, học thử bằng email), trang cảm ơn có mã `SK-yymmdd-xxxx`. Giao diện theo landing v1.0 Linh duyệt 20/10 (phương án A, đã khoá: `DESIGN.md`, `DESIGN.khoa`, `khoa/anh-chuan/`). B và C cất ở `_phuong-an-bo/`.

## Chạy
```
node server.mjs                                   # Node ≥ 18, không cần cài gói, cổng 8080
RATE_MAX=1000 PORT=8103 LINHX_FORM_URL=http://127.0.0.1:8999/nhan node server.mjs   # chạy thử với máy giả
NODE_PATH=$(npm root -g) node kiem/kiem.cjs http://localhost:8103   # cổng K1–K10
```
Chuyển tiếp lead về engine qua `LINHX_FORM_URL` (mặc định `http://127.0.0.1/api/method/linhx_core.crm.api_form.nhan_form`), gắn `nguon: "sakedemy"`. Nếu `LINHX_FORM_URL` trỏ ra ngoài loopback thì bắt buộc dùng `https://` để mã hoá dữ liệu liên hệ. Sau proxy: `TRUST_PROXY=1`.

## Sửa nội dung
- Trang chủ: `public/index.html` (đã khoá; sửa thì chạy cổng, Linh duyệt rồi `--chup-chuan`).
- Trang con: `nguon/_trang-bu.py`, bài trụ: `../own-media/bai-tru-khoa-ai-ung-dung-uy-tin.md`. Sau đó: `python3 nguon/_trang-bu.py && python3 nguon/_bai-tru.py && python3 tao-trang.py`.
- Ảnh OG: `nguon/og.html` → `public/img/og.png`.

## Vân Anh / Linh cần điền (ở `public/cau-hinh.json`, null thì trang giữ chữ an toàn)
`zalo`, `dien_thoai`, `email`, `nguoi_lien_he`, `lien_he_nhanh`, `lien_he_chan`, `phap_nhan`, `ma_so_thue`, `gia_hero`, `faq_gia`, `link_hoc_thu` (cungai), `link_khoa_ca_nhan`, `cam_ket_phan_hoi`, xác nhận `thoi_luong_hero`. Có số Zalo thì nút Zalo nổi tự hiện trên điện thoại.

## Nguồn ảnh
`public/img/anh/*.jpg`: ảnh lớp học thật trích từ hồ sơ đào tạo doanh nghiệp Sakédemy (Canva 02/2026) qua LAB043 `brands/sakedemy/04-hinh-anh/` (ảnh Vinhomes trùng ảnh v1 `LAB058/sakedemy/v1/a/`). Logo, hoạ tiết lá, phông: LAB043 `01-logo`, `05-icon`, `03-chu` (Be Vietnam Pro, OFL). Không dùng ảnh ChatGPT của v1.

## Triển khai
1. Chép thư mục lên VM, chạy `node server.mjs` sau Caddy/Nginx (HTTPS).
2. sakedemy.com đang chạy WordPress: lấy danh sách đường dẫn cũ, giữ bằng 301 trước khi trỏ DNS.
3. Khi lõi engine xong: sửa hàm `guiDi()` trong `server.mjs`; trang không đổi.
