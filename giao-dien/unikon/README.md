# unikon.vn · mặt tiền BU Unikon (9/11/2026)

**19 trang** (trang chủ + 18 trang con), 3 form lead: brief pitch, gọi lại, tải Bộ kiểm an toàn thương hiệu (đổi email). Nút nổi trên điện thoại (ẩn ở màn đầu và vùng form), trang cảm ơn có mã `UK-yymmdd-xxxx`.
Sửa trang con ở `nguon/_trang-bu.py` (bài trụ ở `../own-media/bai-tru-ai-production-cho-agency.md`), rồi:
```
python3 nguon/_trang-bu.py && python3 nguon/_bai-tru.py && python3 tao-trang.py
```

## Chạy
```
node server.mjs                        # Node ≥ 18, không cần cài gói, mặc định cổng 8080
PORT=8101 LINHX_FORM_URL=http://127.0.0.1:8999/nhan node server.mjs
```
Lead chuyển tiếp về engine qua `LINHX_FORM_URL` (mặc định `http://127.0.0.1/api/method/linhx_core.crm.api_form.nhan_form`), gắn `nguon: "unikon"`, kèm `loai` (`brief | goi-lai | tai-bo-kiem`), nguồn (`?kenh=`, utm), câu đồng ý nguyên văn, thời điểm, IP.
Sau proxy: `TRUST_PROXY=1`. Giới hạn: `RATE_MAX` (mặc định 5 lần/10 phút/IP).

## Giao diện đã khoá
Phương án A "Bảng pitch 48 giờ" (Claude khoá theo khuyến nghị, chờ Linh duyệt). `DESIGN.md`, `DESIGN.khoa`, `khoa/anh-chuan/`. PA B, C ở `../_phuong-an-bo/`.
Cổng máy: `RATE_MAX=1000 PORT=8101 node server.mjs &` rồi `NODE_PATH=$(npm root -g) node kiem/kiem.cjs http://localhost:8101`.

## Điền khi có (public/cau-hinh.json, null thì trang giữ chữ an toàn)
`gia_hero`, `gia_job`, `phi_brand_kit`, `faq_gia`: cách nói giá / giá sàn. `zalo` (bật nút "Nhắn Zalo" trên điện thoại và đường lùi khi form lỗi), `lien_he_nhanh`, `lien_he_chan`: chữ liên hệ thật. `phap_nhan`: dòng © chân trang. Các khoá `gia_san_*`, `nguoi_lien_he`, `dien_thoai`, `email`, `giai_thuong` để dành, trang chưa đọc.

## Triển khai
1. Chép thư mục lên VM, chạy `node server.mjs` sau Caddy/Nginx (HTTPS), `TRUST_PROXY=1`.
2. unikon.vn đang có site cũ: chạy song song, đọc đường dẫn cũ và giữ bằng 301 trước khi trỏ DNS.
3. Khi lõi engine xong: chỉ sửa hàm `guiDi()` trong `server.mjs`.
