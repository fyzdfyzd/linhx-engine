---
name: e2e-3-rounds-harsh-reviewer
description: >-
  Quy trình chuẩn chạy kiểm thử tích hợp End-to-End (E2E) tối thiểu 3 vòng
  (Round 1 -> Round 2 -> Round 3) trên trình duyệt thật bằng Playwright, chụp
  ảnh màn hình toàn bộ ứng dụng, đóng vai Reviewer Khó Tính soi trực tiếp ảnh
  chụp sản phẩm cuối và DOM/WCAG, ghi lại kinh nghiệm + lỗi + điểm cải thiện vào
  checkpoint trên ổ cứng (.handoff/e2e-checkpoint.json) để phiên/vòng sau chạy
  tiếp từ điểm đó cho đến khi đạt >= 9.2/10.
metadata:
  version: "0.1.0"
---

# E2E 3-Rounds Harsh Reviewer & Visual Screenshot Audit

## Overview
Skill này chuẩn hoá quy trình **tự chạy — tự kiểm thử End-to-End — chụp ảnh màn hình thực tế — tự phản biện bằng con mắt Reviewer Khó Tính tối thiểu 3 vòng liên tiếp (`Round 1`, `Round 2`, `Round 3`)** trước khi nghiệm thu bất kỳ ứng dụng Web / PWA / Mini App / Dashboard nào.

Thay vì chỉ chạy unit test hoặc chỉ kiểm tra mã trạng thái HTTP 200, quy trình này bắt buộc:
1. Khởi chạy server thật và điều khiển trình duyệt thật (Playwright Chromium / Edge headless).
2. Chụp ảnh màn hình toàn bộ các màn hình/trạng thái (`reports/screens/round{N}/*.png`).
3. **Mở đọc trực tiếp các file ảnh chụp màn hình bằng công cụ đọc ảnh** kết hợp kiểm tra DOM/CSS thực tế để phát hiện các lỗi thị giác mà test tự động thường bỏ sót (thanh điều hướng cố định đè lên nội dung khi cuộn trang, tràn chữ khỏi khung 9:16, thiếu bảng chú giải màu bản đồ, dữ liệu mẫu bị trùng nhóm hoặc kém tự nhiên).
4. Ghi lại biên bản từng vòng (`reports/E2E-ROUND-{N}.md`), kinh nghiệm rút ra (`.handoff/KINH-NGHIEM-E2E.md`), và lưu trạng thái vào `.handoff/e2e-checkpoint.json` để vòng tiếp theo hoặc phiên làm việc tiếp theo đọc lại và chạy tiếp từ đúng điểm đó.

## Dependencies
- `architecture-patterns-and-design-rules`: Áp dụng khi sửa cấu trúc component/layout phát hiện qua các vòng review.
- `frontend-security-audit` / `backend-security-audit`: Phối hợp khi kiểm tra bảo mật API, chữ ký webhook hoặc rò rỉ dữ liệu trên giao diện.

## Quick Start

```bash
# 1. Khởi tạo hoặc kiểm tra trạng thái checkpoint hiện tại
python .agents/skills/e2e-3-rounds-harsh-reviewer/scripts/e2e_review_runner.py status --checkpoint .handoff/e2e-checkpoint.json --output .handoff/e2e-status.json

# 2. Chạy vòng kiểm thử E2E kèm chụp ảnh màn hình và chấm điểm Reviewer Khó Tính
python .agents/skills/e2e-3-rounds-harsh-reviewer/scripts/e2e_review_runner.py run-round --round 1 --url http://127.0.0.1:8000/web/ --screens-dir reports/screens --output reports/round1-audit.json

# 3. Xuất báo cáo Markdown cho vòng vừa chạy và cập nhật checkpoint để vòng sau tiếp tục
python .agents/skills/e2e-3-rounds-harsh-reviewer/scripts/e2e_review_runner.py report --audit-file reports/round1-audit.json --output reports/E2E-ROUND-1.md
```

## Utility Scripts

Script CLI chuẩn nằm tại `scripts/e2e_review_runner.py`, hỗ trợ 3 lệnh con (`status`, `run-round`, `report`) và luôn ghi kết quả ra file (`--output`):

### 1. `status` — Đọc điểm dừng (Checkpoint Resume)
Kiểm tra xem dự án đã chạy tới vòng E2E nào (`round 1`, `2`, hay `3`), điểm số hiện tại bao nhiêu và danh sách lỗi (`findings`) nào cần sửa trước khi chạy vòng kế tiếp.
```bash
python scripts/e2e_review_runner.py status \
  --checkpoint .handoff/e2e-checkpoint.json \
  --output .handoff/e2e-status.json
```

### 2. `run-round` — Chạy trình duyệt thật, chụp màn hình & kiểm toán DOM/Thị giác
```bash
python scripts/e2e_review_runner.py run-round \
  --round 2 \
  --url http://127.0.0.1:8000/web/ \
  --screens-dir reports/screens \
  --checkpoint .handoff/e2e-checkpoint.json \
  --output reports/round2-audit.json
```

### 3. `report` — Sinh báo cáo nghiệm thu từng vòng (`E2E-ROUND-{N}.md`)
```bash
python scripts/e2e_review_runner.py report \
  --audit-file reports/round2-audit.json \
  --output reports/E2E-ROUND-2.md
```

## Workflow (Quy Trình Chuẩn 3 Vòng Bắt Buộc)

### Vòng 1 (Round 1): Chạy E2E thô, chụp toàn bộ màn hình & Tìm lỗi cấu trúc/thị giác lớn
1. Khởi chạy ứng dụng và chạy E2E qua tất cả các luồng người dùng cốt lõi (ví dụ: `<= 3 chạm` ra kết quả, chuyển đổi ngôn ngữ VI/EN, lọc dữ liệu, chế độ Offline).
2. Chụp ảnh toàn bộ các màn hình vào `reports/screens/round1/`.
3. **Bắt buộc dùng công cụ `read_file` mở xem trực tiếp ít nhất 3–5 ảnh chụp màn hình quan trọng nhất** (Màn hình chính, Màn hình kết quả dài, Bản đồ, Thẻ chia sẻ 9:16, Dashboard).
4. Đóng vai **Reviewer Khó Tính**, chấm điểm khắt khe trên thang 10 và lập bảng lỗi (`REV-R1-*`) trong `reports/E2E-ROUND-1.md`.
5. Sửa triệt để các lỗi phát hiện ở Vòng 1 trong mã nguồn và đóng gói lại ứng dụng.

### Vòng 2 (Round 2): Chạy lại từ Checkpoint, kiểm tra hồi quy & Tinh chỉnh chiều sâu dữ liệu/UX
1. Đọc `.handoff/e2e-checkpoint.json` để xác nhận danh sách lỗi Vòng 1 cần kiểm chứng lại.
2. Chạy lại toàn bộ kịch bản E2E, lưu ảnh chụp mới vào `reports/screens/round2/`.
3. Mở xem ảnh chụp `round2/*.png` để đối chiếu Before/After so với Vòng 1.
4. Tìm tiếp các điểm chưa hoàn hảo về mặt biên tập dữ liệu (ví dụ: tên địa điểm có hậu tố sinh tự động `#171` hoặc `số 99` thay vì địa danh biểu tượng; bảng chú giải chưa đồng bộ chỉ tiêu; chân trang 9:16 bị sát mép; thiếu `.skip-link` hoặc kích thước nút bấm `< 32px`).
5. Ghi `reports/E2E-ROUND-2.md` và sửa toàn bộ các điểm tinh chỉnh cho Vòng 3.

### Vòng 3 (Round 3): Nghiệm thu Xuất xưởng (`>= 9.2 / 10.0`, 0 lỗi tồn đọng)
1. Chạy lại toàn bộ kịch bản E2E lần thứ 3, xuất ảnh cuối vào `reports/screens/round3/` và đồng bộ ra `reports/screens/`.
2. Mở xem lại các ảnh chụp sản phẩm cuối để xác nhận **0 lỗi bố cục, 0 lỗi console, 0 lỗi tràn khung, 100% kịch bản PASS**.
3. Ghi `reports/E2E-ROUND-3.md` và đúc kết toàn bộ bài học xương máu vào `.handoff/KINH-NGHIEM-E2E.md`.

## Minimalist Spec & UI Review Gate (`TC-TG-01` → `TC-TG-06`)
Mọi đề bài thiết kế (`.handoff/DE-BAI-*.md`) và giao diện sản phẩm khi qua Reviewer Khó Tính đều phải đạt **6 Tiêu chí Tối giản (`.handoff/TIEU-CHI-RA-DE-TOI-GIAN.md`)**:
1. **`TC-TG-01` (Độ dài đề bài $\le 120$ dòng)**: Đặc tả chỉ liệt kê mục đích duy nhất + tối đa 4 thành phần hiển thị/màn hình.
2. **`TC-TG-02` (1 Màn hình = 1 Mục tiêu = 1 CTA chính)**: Không nhồi 2 luồng nghiệp vụ vào 1 màn hình; khoảng trắng $\ge 45\%$.
3. **`TC-TG-03` (Trần 3 thông tin / thẻ)**: Mỗi thẻ (`Card`) chỉ hiện đúng 3 dòng (`Tên điểm`, `Giờ & Khoảng cách`, `1 câu lý do ngắn`).
4. **`TC-TG-04` (Hệ thống thiết kế `3-1-3`)**: Tối đa 3 màu, 1 font chữ, 3 cỡ chữ (`20px / 15px / 13px`), tối đa 3 tab đáy.
5. **`TC-TG-05` (Bổ sung Zero-UI / 1 chạm tại chỗ)**: Tính năng mới không được đẻ thêm màn hình hay popup nhiều bước.
6. **`TC-TG-06` (Kiểm toán DOM tự động `maxStopCardChars <= 200`)**: Tự động trừ điểm nếu thẻ nội dung vượt trần 200 ký tự hoặc lồng hộp (`nested cards`).

## Common Mistakes (4 Bẫy Thực Tế Phải Tránh)
1. **Bẫy `position: fixed` / `position: sticky` trên thanh Bottom Nav khi chụp `full_page=True`**:
   - Khi trang dài hơn chiều cao viewport (`844px`), Chromium giữ thanh `position: fixed; bottom: 0` hoặc `sticky` ngay tại toạ độ `y = 844px`, khiến thanh điều hướng cắt ngang giữa thân trang và che khuất tiêu đề thẻ trên ảnh chụp!
   - **Cách sửa chuẩn**: Đặt khung bao `.app-shell` là `display: flex; flex-direction: column; min-height: 100vh;` và đặt `nav.bottom-nav` là `position: relative; margin-top: auto;`.
2. **Bẫy lấy mẫu `[:N]` đầu danh sách làm đồng nhất màu ghim bản đồ**:
   - Nếu dữ liệu được sắp xếp theo nhóm mà chỉ lấy `pois[:60]`, toàn bộ ghim trên bản đồ sẽ chỉ thuộc Nhóm 1. Phải luôn lấy mẫu phân tầng (`stratified round-robin`) đều qua tất cả các nhóm.
3. **Bẫy chỉ kiểm tra DOM text mà không mở xem file ảnh `.png`**:
   - DOM test không phát hiện được việc thẻ QR ở chân ảnh `1080×1920` bị cắt mất 15px do `overflow: hidden`. Bắt buộc phải mở xem file ảnh `.png` sau mỗi vòng chạy.
4. **Bẫy Playwright thiếu trình duyệt tải riêng trên máy Windows**:
   - Nếu `playwright install chromium` chưa chạy, hãy dùng `p.chromium.launch(channel="msedge", headless=True)` hoặc `channel="chrome"` để tận dụng ngay trình duyệt sẵn có trên Windows.
