model: gemini-4-argon-high
phieu: bhc-lite-1a
may: may-2
trang_thai: xong
tep_doi: KET-QUA.md, bang-chung/bhc-domain-1/KET-QUA.md, bang-chung/bhc-domain-1/bao-cao-if-agent-1280.png, bang-chung/bhc-domain-1/bao-cao-if-agent-360.png, bang-chung/bhc-domain-1/bao-cao-vinamilk-1280.png, bang-chung/bhc-domain-1/bao-cao-vinamilk-360.png, bang-chung/bhc-domain-1/quan-tri-1280.png, bang...
drive: G:\My Drive\LINHX-VIEC\bhc-lite-1a\bang-chung\bhc-prod-5b (12 tep: 06-landing-sang-full-1280.png, 06-landing-sang-full-360.png, landing-csmo-full-1280.png, landing-csmo-full-360.png, 2026-11-19-csmo-d88de79d-full.pdf, csmo-full.pdf, 06-landing-sang-full-1280.png, 06-landing-sang-full-360.png, landing-csmo-full-1280....
phut: 39.58
token: vao=536765 ra=122108

Đã hoàn thành triển khai chế độ khách **Lite / Full** (`BH_CHE_DO_KHACH=lite|full`) trên nhánh `agy/bhc-lite-1` (tách từ `agy/bhc-sua-9` `5bbcb0c`):

1. **Cờ cấu hình & Quyền mở Full (`moFull`, `laMau`):**
   - Bổ sung [che-do-lite.js](file:///C:/linhx/ifagent-wt/bhc-lite-1/apps/brand-health/server/lib/che-do-lite.js), tích hợp vào [app.js](file:///C:/linhx/ifagent-wt/bhc-lite-1/apps/brand-health/server/app.js) và [landing.js](file:///C:/linhx/ifagent-wt/bhc-lite-1/apps/brand-health/server/lib/landing.js).
   - Cờ `BH_CHE_DO_KHACH=lite|full` mặc định `full`; báo cáo mẫu (Vinamilk, IF Agent ở trang chủ và báo cáo quản trị đánh dấu mẫu `laMau=true`) luôn coi như `moFull=true`.
2. **Chế độ Lite (`BH_CHE_DO_KHACH=lite` và `moFull=false`):**
   - Màn kết quả ([xong.html](file:///C:/linhx/ifagent-wt/bhc-lite-1/apps/brand-health/public/xong.html), [render
...[cat bot]...
-chung/bhc-lite-1/khoi-nhan-ban-full-360.png, bang-chung/bhc-lite-1/loi-cam-on-sau-gui-1280.png, bang-chung/bhc-lite-1/loi-cam-on-sau-gui-360.png, bang-chung/bhc-lite-1/quan-tri-lead-mo-ban-full-1280.png, bang-chung/bhc-lite-1/quan-tri-lead-mo-ban-full-360.png, bang-chung/bhc-lite-1/quan-tri-chi-tiet-cong-tac-1280.png, bang-chung/bhc-lite-1/man-ket-qua-lite-1280.png.
