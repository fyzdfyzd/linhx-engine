---
name: linhx-tu-chay
description: Cho Claude và Antigravity tự đi từ ý định 4 câu tới sản phẩm chạy được - khám phá, PRD, features.json khoá, thợ làm từng feature, cổng kiểm độc lập ngoài tay thợ, Linh chỉ duyệt ở cổng người. Dùng khi Linh nói "tự chạy", "tự viết PRD", "giao agy làm tới cuối".
metadata:
  version: "0.1.0"
---

# linhx-tu-chay (LAB098, nấc 1)

Mẫu ghép từ Anthropic (planner / generator / evaluator, feature list `passes:false`, file tiến độ),
spec-kit / Kiro (spec → plan → tasks), BMAD (vai PM, kiến trúc, QA) và bài học riêng của Linh
(agy IDE từng tự chấm giả, LAB034/LAB038).

## Luật sắt
1. Người viết đề không làm, thợ không tự chấm. Thợ chỉ được đổi `passes` và `bang_chung` trong features.json.
2. Mọi "đạt" phải qua `scripts/cong_kiem.py kiem` chạy NGOÀI phiên thợ. Không tin exit code hay lời thợ.
3. Mỗi feature có `lenh_kiem` chạy được bằng máy (test, curl, Playwright, cổng 17 luật report-core).
4. Một phiên thợ = một feature, rồi commit + ghi TIEN-DO.md. Phiên mới đọc TIEN-DO.md + git log trước.
5. 5 cổng người (LAB081): duyệt PRD, KYC/thanh toán, giá, tiêu tiền ads, đăng công khai.

## Các bước
0. Linh viết `Y-DINH.md` 4 câu: bán gì, cho ai, thu tiền thế nào, xong là khi nào.
1. Khám phá (tuỳ chọn): chạy đề LAB079 double diamond → `KET-QUA.md` (phân khúc, vấn đề, giải pháp, phép thử).
2. Planner (Claude): viết `PRD.md` theo `mau/PRD.md` + `features.json` theo `mau/features.json`.
   Cố ý viết PRD ở mức sản phẩm, không chi tiết code (chi tiết sai sẽ lan xuống).
   → CỔNG NGƯỜI 1: Linh duyệt PRD + danh sách feature (10 phút).
3. Khoá: `python scripts/cong_kiem.py khoa features.json` (Linh hoặc bộ chạy làm, không phải thợ).
4. Vòng thợ (agy -p hoặc claude -p), mỗi lượt:
   - đọc PRD.md, TIEN-DO.md, `git log -5`, chọn feature `passes:false` ưu tiên cao nhất
   - làm, tự chạy lenh_kiem, ghi file bằng chứng vào `bang-chung/`, đổi passes, commit, ghi TIEN-DO.md
5. Cổng kiểm: `python scripts/cong_kiem.py kiem features.json` → `KIEM-features.json`.
   Feature báo láo bị hạ về false và ghi vi phạm. Vi phạm ≥2 lần cùng feature → dừng, báo Linh.
6. Đánh giá cuối (evaluator): một phiên Claude riêng dùng Playwright đi luồng khách thật
   (nhập ngày sinh → xem trước → quét QR sandbox → nhận PDF), chấm theo PRD mục "Thước đo xong".
7. Sáng: chỉ đọc `SANG-NAY.md` (đạt thật x/y, vi phạm, việc cần người).

## Khi nào KHÔNG dùng
Việc dưới nửa ngày: một phiên Claude làm thẳng rẻ hơn. Anthropic đo harness đầy đủ đắt ~20 lần
chạy đơn (6 giờ $200 so với 20 phút $9), chỉ đáng khi chạy đơn hỏng.
