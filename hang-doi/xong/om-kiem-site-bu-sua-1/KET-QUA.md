model: gemini-4-neon-medium
phieu: om-kiem-site-bu-sua-1
may: may-3
trang_thai: xong
tep_doi: KET-QUA.md, kiem-12-site-bu.csv
drive: (khong)
phut: 5.34
token: vao=70893 ra=16432

Đã hoàn tất kiểm tra HTTP 12 site BU và đối chiếu repo `linhx-engine` (`trang-bu/`, `sites/`).

### Tệp kết quả đã ghi
- [KET-QUA.md](file:///D:/linhx/hang-doi/runner/viec/lam-viec/KET-QUA.md) (1.936 ký tự, ≤ 2.000 ký tự)
- [kiem-12-site-bu.csv](file:///D:/linhx/hang-doi/runner/viec/lam-viec/kiem-12-site-bu.csv) (bảng chi tiết 12 site: mã HTTP, chuyển hướng, thời gian tải, `<title>`, form lead, `llms.txt`, `sitemap.xml`, `robots.txt`, SEO cơ bản, nguồn trong repo)

### Tóm tắt nhanh
- **9/12 site sống (HTTP 200, tải 288–773ms)**:
  - Đủ form + SEO + `llms.txt` (5): `tuva.work`, `unikon.vn`, `sakedemy.com`, `cungai.vn`, `genderation.vn`.
  - Đủ form + SEO, thiếu `llms.txt` (1): `urah.vn`.
  - Thiếu form trang chủ + thiếu `llms.txt` (2): `ifagent.net`, `chiemtinh.vn`.
  - Thiếu form + thiếu `llms.txt`/`sitemap.xml`/`robots.txt`/`canonical` (1): `event.ifagent.net`.
- **3/12 site không truy cập công khai được**:
  - `listening.vn`: lỗi DNS (`getaddrinfo failed`).
  - `linhx.info`: HTTPS timeout, HTTP 404.
  - `demo.ifagent.net`: chuyển hướng `302` tới `https://yenlam.ifagent.net/baocao/` và trả `401 Unauthorized`.
- **Repo `linhx-engine`** (`main` `438bc201`, đọc từ `C:\linhx\wt-ht-uu-tien` vì `C:\linhx\wt-om-kiem` trỏ remote cũ `linhx-ai/linhx-
...[cat bot]...
nt.net`, `chiemtinh.vn`.
2. Bổ sung `llms.txt` cho `ifagent.net`, `event.ifagent.net`, `urah.vn`, `chiemtinh.vn` và đủ `robots.txt` + `sitemap.xml` + `canonical` cho `event.ifagent.net`.
3. Xử lý 3 tên miền chết/khoá (`listening.vn`, `linhx.info`, `demo.ifagent.net`): dựng trang đích, chuyển hướng 301 hoặc thêm trang giới thiệu công khai trước cổng 401.
4. Mở rộng `<title>` quá ngắn trên `unikon.vn`, `cungai.vn`, `event.ifagent.net`.
5. Chuẩn hoá cấu hình/ánh xạ các site BU chủ lực vào `linhx-engine/sites/` ngoài `ifagent` và `unikon`.
