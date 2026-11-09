---
name: lps-release
description: Kiểm cổng phát hành (release gate) trước khi đưa bản mới lên production theo LPS. Dùng khi Linh nói "phát hành", "release", "deploy production", "lên bản mới".
metadata:
  version: "0.1.0"
---

# Cổng phát hành

1. Tạo `docs/releases/RELEASE-vX.Y.Z.md` từ `docs/templates/RELEASE-CHECKLIST.md`.
2. Tự chạy mọi mục kiểm được bằng máy, dán bằng chứng (lệnh + dòng kết quả, link CI) cạnh từng ô:
   - `pnpm verify`, e2e đầy đủ, build production.
   - Quét bảo mật ở `lps-bao-mat` bước 2; ZAP baseline lên staging.
   - axe và Lighthouse trên các màn chính của staging.
   - Thử migration trên bản sao DB, ghi lệnh lùi.
3. Mục cần người (user test, duyệt rủi ro chấp nhận) để trống và liệt kê cho Linh.
4. Viết CHANGELOG theo nhóm Thêm / Sửa / Bảo mật / Thay đổi phá vỡ, từ commit Conventional Commits. Đề xuất số phiên bản SemVer (phá vỡ → MAJOR, tính năng → MINOR, sửa → PATCH).
5. **Dừng và hỏi Linh.** Không tự deploy production, không tự gắn tag đẩy lên khi Linh chưa nói "phát hành" cho đúng phiên bản này. Khi Linh đồng ý: `git tag vX.Y.Z && git push origin vX.Y.Z`; workflow `deploy.yml` sẽ dừng chờ Linh bấm duyệt trong Environment `production` (lớp chặn thứ hai).
6. Sau khi Linh duyệt và deploy: xác nhận job health check xanh; theo dõi lỗi 30 phút đầu (Sentry/log), so tỉ lệ lỗi với bản trước; tăng bất thường → đề xuất lùi bản.
