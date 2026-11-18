model: mac-dinh
phieu: yl10-trang-test
may: may-3
trang_thai: xong
tep_doi: (khong)
drive: (khong)
phut: 36.67
token: vao=1024132 ra=105646

dat: co
trang_thai: REVIEW
nhanh: `agy/yl10-trang-test`
sha_dinh: `147eda63` (code & ảnh: `234ccebf`)

### Biến / tệp cấu hình chứa mã `/yen-lam/ky-thuat/<ma>` (KHÔNG ghi giá trị)
- **Biến môi trường**: `YL_KY_THUAT_MA` (chuỗi ngẫu nhiên `>= 24` ký tự `[A-Za-z0-9_-]`, đặt trong `lab-staging.env` trên VM staging).
- **Tệp cấu hình staging thay thế**: `${DATA_DIR}/ky-thuat-staging.json` (trường `"ma"`) hoặc trường `"ky_thuat_ma"` trong `${DATA_DIR}/yl-cau-hinh.json`.
- **Cổng môi trường**: chỉ bật khi `YL_MOI_TRUONG=staging` hoặc `NODE_ENV=staging`; trên prod (`NODE_ENV=production` không có `YL_MOI_TRUONG=staging`) mặc định **TẮT** (trả `404`).

### Các phần đã hoàn thành
1. **Log chat Lam ([kho-ky-thuat.js](file:///D:/linhx/ifagent-wt/yl10-trang-test/apps/lab/server/v1/ky-thuat/kho-ky-thuat.js), [lam.js](file:///D:/linhx/ifagent-wt/yl10-trang-test/apps/lab/server/v1/lam/lam.js), [live-proxy.js](file:///D:/linhx/ifagent-wt/yl10-trang-test/packages/character/live-proxy.js))**: ghi mọi lượt kiosk + đồng hành + live WS vào SQLite `yl.db` (`ky_thuat_log_chat`: thời gian, máy/phiên, khách nói, Lam trả, widget hiện, độ trễ ms, lỗi/chặn), tự giữ 7 ngày.
2. **Trang `/yen-lam/ky-thuat/<ma>` ([routes.js](file:///D:/linhx/ifagent-wt/yl10-trang-test/apps/lab/demos/yen-lam/modules/k
...[cat bot]...
nt` (10/10), `kiosk-lam-a2-ab` (2/2), `yl09-dh-lam` (3/3).
- **Ảnh ghép (≤600 KB)**: [ghep-1280x800-truoc-sau.png](file:///D:/linhx/ifagent-wt/yl10-trang-test/bang-chung/yl10-trang-test/ghep-1280x800-truoc-sau.png) (**9/10**), [ghep-390x844-ba-khoi.png](file:///D:/linhx/ifagent-wt/yl10-trang-test/bang-chung/yl10-trang-test/ghep-390x844-ba-khoi.png) (**9/10**). Nhật ký: [KET-QUA.md](file:///D:/linhx/ifagent-wt/yl10-trang-test/bang-chung/yl10-trang-test/KET-QUA.md), [tien-do.log](file:///D:/linhx/nhat-ky/yl10-trang-test/tien-do.log).

CON_LAI: khong
