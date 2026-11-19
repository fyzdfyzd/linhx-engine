model: gemini-4-argon-high
phieu: bhc-lite-1c
may: may-2
trang_thai: xong
tep_doi: KET-QUA.md, bang-chung/bhc-domain-2/KET-QUA.md, bang-chung/bhc-domain-2/bao-cao-csmo-1280.png, bang-chung/bhc-domain-2/bao-cao-csmo-360.png, bang-chung/bhc-domain-2/dns-hien-tai-1280.png, bang-chung/bhc-domain-2/dns-hien-tai-360.png, bang-chung/bhc-domain-2/quan-tri-1280.png, bang-chung/bhc-domai...
drive: G:\My Drive\LINHX-VIEC\bhc-lite-1c\bang-chung\bhc-lite-1c\landing-lite-1280.png
phut: 22.43
token: vao=251420 ra=47676

Đã hoàn tất deploy chế độ Lite (`33cb800` từ `agy/bhc-lite-1`) lên Production và Staging theo đúng 7 bước, push báo cáo cùng ảnh bằng chứng sau mỗi bước lên nhánh `agy/bhc-lite-1c` (commit `cbc2797d`).

### KET-QUA
- **KET-QUA**: `dat` (`dat: co`)
- **Nhánh bằng chứng**: `agy/bhc-lite-1c` ([KET-QUA.md](file:///C:/linhx/ifagent-wt/bhc-lite-deploy/bang-chung/bhc-lite-1c/KET-QUA.md))
- **SHA code & đang chạy**:
  - **Production (`/opt/ifagent`, service `brand-health`)**: `33cb800` (`BUILD_SHA_BRAND_HEALTH=33cb800`, `BUILD_SHA_BRAND_HEALTH_PREV=5bbcb0ce`; `https://demo.ifagent.net/brand-health-check/healthz` -> HTTP `200`, `/api/meta` -> `"cheDoKhach":"lite"`).
  - **Staging (`/opt/stg-brand`, service `stg-brand-app`)**: `33cb800` (`http://127.0.0.1:3920/healthz` -> HTTP `200`, `"BUILD_SHA":"33cb800"`, `/api/meta` -> `"cheDoKhach":"lite"`).

### Tóm tắt các bước & Kết quả Bước 6
1. **Bước 1 (Sao lưu)**: Đã tạo `/opt/ifagent/backup-brand-health-data-19-11-lite.tgz` (`1.7M`) và `/opt/ifagent/infra/brand-health.env.bak-1
...[cat bot]...
-chung/bhc-lite-1c/quan-tri-lead-1280.png) ([quan-tri-lead-mo-ban-full-1280.png](file:///C:/linhx/ifagent-wt/bhc-lite-deploy/bang-chung/bhc-lite-1c/quan-tri-lead-mo-ban-full-1280.png))
  - [quan-tri-lead-360.png](file:///C:/linhx/ifagent-wt/bhc-lite-deploy/bang-chung/bhc-lite-1c/quan-tri-lead-360.png) ([quan-tri-lead-mo-ban-full-360.png](file:///C:/linhx/ifagent-wt/bhc-lite-deploy/bang-chung/bhc-lite-1c/quan-tri-lead-mo-ban-full-360.png))
