# D:\LINHX\BRAND · Kho thương hiệu chuẩn

Mỗi thương hiệu một thư mục, cùng một cấu trúc. Đây là nơi lấy tài sản chính thức (logo, màu, chữ, pattern, guideline, design system). Thư mục việc (LAB, PRJ) chỉ là nơi làm; bản đã duyệt luôn được chép về đây.

| Thương hiệu | Thư mục | Design system | Tình trạng |
|---|---|---|---|
| 2X.Lab | `2XLAB/` | https://claude.ai/artifact/Lk9zBrJNf6RW7mFoKKbBHF | Guideline bản 3 chị Hương duyệt 10/11/2026 |

## Tạo brand mới
Quy trình, bộ dựng và mẫu ở `_QUY-TRINH-TAO-BRAND/` (đọc README trong đó). Dự án nào cũng dùng được.

## Cấu trúc chuẩn cho một thương hiệu

```
<BRAND>/
  README.md              thẻ thương hiệu: tên đúng chính tả, tinh thần, màu, chữ, link, tình trạng
  00-goc/                Core value, Brand Persona nguyên văn của chủ thương hiệu
  01-logo/svg/           logo vector, chữ đã chuyển nét
  01-logo/png/           logo PNG trên các nền, cụm logo
  01-logo/avatar/        avatar mạng xã hội đã chốt
  02-mau-chu/            font (có giấy phép) và bảng màu
  03-pattern/            pattern và element đã chốt, bảng option
  04-guideline/          Brand Guideline PDF, PPTX sửa được, contact sheet, trang PNG
  05-design-system/      nguồn design system (project/ + script sinh lại)
  06-mau-tai-lieu/       mẫu tài liệu đã đạt (bản chào khách, bản nội bộ, năng lực)
  07-luat-quy-trinh/     luật thiết kế, sổ gu khách
  08-phien-ban/          sổ phiên bản các lần gửi
  09-nguon-lam-viec/     toàn bộ tệp làm việc (bản nháp, tham chiếu, nguồn dựng) để làm lại khi cần
```

Quy tắc:
1. Chỉ chép về đây bản đã được khách hoặc anh Linh duyệt. Bản nháp ở lại thư mục việc.
2. Thay tệp thì ghi một dòng vào `08-phien-ban/` và commit git.
3. Agent cần tài sản thương hiệu đọc `<BRAND>/README.md` trước, không lục thư mục việc.
4. Làm Brand ID mới theo `D:\LINHX\WF-CHUAN\WF-BRAND-ID\QUY-TRINH-BRAND-ID.md` (skill `brand-id-chuan`); xong thì tạo thư mục thương hiệu theo cấu trúc trên.
