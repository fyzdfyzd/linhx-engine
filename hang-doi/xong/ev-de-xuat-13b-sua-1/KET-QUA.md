model: mac-dinh
phieu: ev-de-xuat-13b-sua-1
may: may-2
trang_thai: xong
tep_doi: KET-QUA.md, bang-chung/ev-de-xuat-13b/TONG-SLIDE.png, bang-chung/ev-de-xuat-13b/de-xuat-slide-xanh.log, bang-chung/ev-de-xuat-13b/de-xuat-slide-y2-do.log, bang-chung/ev-de-xuat-13b/giao-dien-sang.log, bang-chung/ev-de-xuat-13b/khong-tran-ngang.log, bang-chung/ev-de-xuat-13b/npm-test.log, bang-chu...
drive: G:\My Drive\LINHX-VIEC\ev-de-xuat-13b-sua-1\bang-chung\ev-de-xuat-13b\pdf-1.png, G:\My Drive\LINHX-VIEC\ev-de-xuat-13b-sua-1\bang-chung\ev-de-xuat-13b\slide-1.png
phut: 15.12
token: vao=219687 ra=26035

`dat: co`
- **Nhánh**: `agy/ev-de-xuat-13b`
- **SHA**: `d7ac65e7ecd869c5172d3d8ed410aa400343963f`
- **Ý 1 (bỏ theo quy định)**: Trên nhánh `hang-doi` của `linhx-engine`, `hang-doi/xong/ev-anh-ly-12b/KET-QUA.md` ghi `KHONG_THAY` (không có tệp `ly-ngang.*` / `ly-vuong.*`) → bỏ ý 1, thực hiện ý 2–3.
- **Ý 2 — Test đỏ → xanh**:
  - Sửa bằng `text-wrap: balance` trên tiêu đề/nhãn/tên chỉ số ở cả 8 slide trong [de-xuat.css](file:///C:/linhx/ifagent-wt/ev-de-xuat-13b/apps/event/public/xuong/de-xuat.css) và nối 2 từ cuối bằng `\u00A0` trong [slide-du-lieu.js](file:///C:/linhx/ifagent-wt/ev-de-xuat-13b/apps/event/public/xuong/slide-du-lieu.js) cho cả Web và PDF.
  - Thêm ca test khoá 8 slide (`1920×1080` bằng `Range.getClientRects` từng từ + PDF 8 trang) trong [de-xuat-slide.test.js](file:///C:/linhx/ifagent-wt/ev-de-xuat-13b/apps/event/test/e2e/de-xuat-slide.test.js).
  - Đỏ: [de-xuat-slide-y2-do.log](file:///C:/linhx/ifagent-wt/ev-de-xuat-13b/bang-chung/ev-de-xuat-1
...[cat bot]...
- **Xác nhận bí mật**: `git diff origin/agy/ev-de-xuat-11..HEAD` chỉ chạm `apps/event/` và `bang-chung/ev-de-xuat-13b/`, `0` bí mật mới.
- **Bằng chứng**: [TONG-SLIDE.png](file:///C:/linhx/ifagent-wt/ev-de-xuat-13b/bang-chung/ev-de-xuat-13b/TONG-SLIDE.png), `slide-1.png`..`slide-8.png` (`1920×1080`), `pdf-1.png`..`pdf-8.png` (`1920×1080`), và [KET-QUA.md](file:///C:/linhx/hang-doi/runner/viec/lam-viec/KET-QUA.md).
