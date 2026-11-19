model: gemini-4-argon-high
phieu: bhc-domain-3
may: may-2
trang_thai: xong
tep_doi: bang-chung/bhc-domain-3/KET-QUA.md, bang-chung/bhc-domain-3/bao-cao-csmo-1280.png, bang-chung/bhc-domain-3/bao-cao-csmo-360.png, bang-chung/bhc-domain-3/quan-tri-1280.png, bang-chung/bhc-domain-3/quan-tri-360.png, bang-chung/bhc-domain-3/trang-chu-1280.png, bang-chung/bhc-domain-3/trang-chu-360.png
drive: (khong)
phut: 6.94
token: vao=103104 ra=11674

# KET-QUA: bhc-domain-3

- **KET-QUA (`dat`)**: `dat` (`dat: co`)
- **IP DNS**: `34.87.102.182` (cả `8.8.8.8`, `1.1.1.1` và GoDaddy NS `ns59.domaincontrol.com` đều trả về `34.87.102.182`)
- **HTTP**: `HTTP/1.1 200 OK`
- **Chứng chỉ**:
  - **Subject / SAN**: `CN=brandcheck.ifagent.net` (`DNS:brandcheck.ifagent.net`)
  - **Nhà cấp chứng chỉ (Issuer)**: `Let's Encrypt` (`C=US, O=Let's Encrypt, CN=YE1`)
  - **Ngày cấp (Valid From)**: `Nov 19 05:10:00 2026 GMT`
  - **Ngày hết hạn (Valid To)**: `Feb 17 05:09:59 2027 GMT`
- **Lỗi (danh sách yêu cầu lỗi ≥ 400)**: `[]` (rỗng trên cả 3 trang ở cả 2 khung hình `1280x800` và `360x800`)
- **Ảnh & Báo cáo đã push lên nhánh `agy/bhc-domain-3`**:
  - [KET-QUA.md](file:///C:/linhx/ifagent-wt/bhc-domain/bang-chung/bhc-domain-3/KET-QUA.md)
  - [trang-chu-1280.png](file:///C:/linhx/ifagent-wt/bhc-domain/bang-chung/bhc-domain-3/trang-chu-1280.png)
  - [trang-chu-360.png](file:///C:/linhx/ifagent-wt/bhc-domain/bang-chung/bhc-domain-3/trang-chu-360.png)
  - [bao-cao-csmo-1280.png](file:///C:/linhx/ifagent-wt/bhc-domain/bang-chung/bhc-do
...[cat bot]...
 05:09:59 2027 GMT`.
   - `curl -sv https://brandcheck.ifagent.net/` trả về `HTTP/1.1 200 OK`.
3. **Trình duyệt thật Chromium (`1280x800` + `360x800`, TLS chuẩn)**:
   - Trang chủ `https://brandcheck.ifagent.net/`: HTTP `200`, lỗi ≥ 400: `[]`
   - Báo cáo mẫu CSMO `https://brandcheck.ifagent.net/bao-cao/2026-11-19-csmo-d88de79d/`: HTTP `200`, lỗi ≥ 400: `[]`
   - Quản trị (trang đăng nhập) `https://brandcheck.ifagent.net/quan-tri/`: HTTP `200`, lỗi ≥ 400: `[]`
