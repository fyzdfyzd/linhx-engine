# Quy chuẩn dự án tự chạy (agy làm, Claude canh)

Bản 1.0 · 30/10/2026 · Rút từ dự án Chiêm Tinh Số (repo fyzdfyzd/chiemtinhso). Áp cho mọi dự án production mới của Linh, ví dụ máy quét crawler.

## 1. Bộ khung bắt buộc của một dự án
| Phần | Nội dung | Mẫu |
|---|---|---|
| Repo GitHub private | một repo một dự án, nhánh `main` chỉ Linh merge | chiemtinhso |
| `docs/KIEN-TRUC.md` | 3 lớp (nền dùng chung, phần riêng của ngành, bộ vận hành agent), 4 giai đoạn Setup, Launch, Run, Scale, mỗi giai đoạn có cổng ra bằng số | KIEN-TRUC-OPC.md |
| `docs/DE-BAI-DEV.md` | module bật/tắt theo hợp đồng `module.yaml`, JTBD + ngân sách bước, ưu tiên P0–P3, đợt làm | DE-BAI-DEV-CHIEMTINHSO.md |
| `docs/TINH-HUONG.md` | mọi tình huống TH-xxx, mỗi cái thành một test e2e | TINH-HUONG.md |
| `AGENTS.md` | luật cho agy: vòng làm việc, điều cấm, stack | |
| `CLAUDE.md` | Claude là người canh, không viết tính năng | |
| `features-dotN.json` + `.khoa` | danh sách việc của đợt, khoá bằng `cong_kiem.py khoa`; chỉ thợ được bật `passes` | |
| `tests/nghiem-thu/` | bộ nghiệm thu hộp đen do Claude viết; agy không được sửa | |
| `dieu-khien.json` | lệnh từ xa: chay / tam_dung / dung_han, đợt, feature ưu tiên, ghi chú cho agy | |
| `.github/workflows` | CI (rào cứng, nghiệm thu, cong_kiem, luật kiến trúc) + Claude review PR | |
| `scripts/` | `cong_kiem.py`, `claude-canh.ps1`, `dieu-phoi.ps1`, `dang-ky-lich.ps1`, `cai-dat-may-cty.ps1` (file .ps1 lưu UTF-8 có BOM) | |

## 2. Ai làm gì
- **agy (thợ):** viết code theo phiếu trên worktree riêng `<REPO>-tu-dong`, nhánh `tu-dong/dotN`. Mỗi phiếu chạy một phiên mới. Cuối phiếu ghi 3 dòng vào `.canh/CAI-TIEN-AGY.md`.
- **Claude trên máy (người canh):** mỗi 20 phút kiểm commit mới qua rào cứng, `cong_kiem` và review đọc diff, rồi ghi `.canh/TRANG-THAI.md` (DAT/CHUA_DAT) và 3 dòng cải tiến vào `.canh/CAI-TIEN-CLAUDE.md`. Mỗi sáng viết `.canh/RA-SOAT-<ngày>.md`: rà token, gom đề xuất.
- **Claude ở cloud (luồng dự án):** viết đề, viết bộ nghiệm thu và features của đợt kế, đọc `.canh/` trên GitHub để báo Linh, ra lệnh qua `dieu-khien.json`.
- **Linh:** duyệt các cổng (DESIGN.md, mốc màn hình, merge vào main, tiền, đăng công khai), không ngồi canh.

## 3. Máy
- **Máy CÔNG TY = DESKTOP-PVHR2CD**, luôn bật: chạy bộ điều phối và agy tự động.
- **Máy CÁ NHÂN = MSI**: chỉ dùng khi việc cần đúng máy đó, ví dụ Chrome đã đăng nhập, extension hay file chỉ có trên MSI.
- Mỗi lần xin Linh bấm duyệt đều ghi rõ tên máy.

## 4. Luật an toàn
- agy toàn quyền chỉ khi Linh đồng ý bằng lời cho máy đó (cờ `agy_toan_quyen` trong `dieu-khien.json`); mặc định dùng danh sách quyền trong `docs/QUYEN-AGY.md`. Rào còn lại: worktree riêng, Claude canh, chỉ Linh merge main.
- Claude canh chỉ đọc (Read, Grep, git diff/log/show).
- Không commit bí mật hay dữ liệu khách. Dữ liệu cá nhân phải che trước khi agent đọc.
- Số token chỉ tin khi JSON đúng dạng thật. Không đo được thì ghi "khong-do-duoc", không ghi 0.

## 5. Nhịp
- 20 phút: kiểm, giao phiếu, đẩy nhật ký.
- Mỗi sáng: rà soát token và cải tiến.
- Hết đợt: Claude ở cloud viết đợt kế, Linh merge.

## 6. Mở dự án mới theo quy chuẩn
1. Linh tạo repo trống.
2. Claude ở cloud viết KIEN-TRUC, DE-BAI-DEV và TINH-HUONG, rồi chép khung `scripts/`, `AGENTS.md`, `CLAUDE.md`, CI từ chiemtinhso.
3. Claude viết `features-dot0.json` và bộ nghiệm thu đợt 0, khoá lại, đẩy lên main.
4. Trên máy công ty: clone, `dang-ky-lich.ps1` với tên lịch riêng cho dự án.

## 7. Bảng theo dõi cho Linh
Chỉ trả lời 3 câu: gần đích chưa, đang chạy gì, cần Linh làm gì. Một số lớn, một thanh tiến độ, một danh sách ngắn. Chi tiết token và nhật ký để trong `.canh/`, không đưa lên bảng.

## 8. Token phình thì chuyển thread (Linh 31/10, áp mọi LAB/PRJ)
- Dấu hiệu: thread đã bị tóm tắt ngữ cảnh, hoặc chạy nhiều giờ qua nhiều mốc, hoặc mỗi lượt đọc lại khối lớn.
- Claude tự báo Linh một dòng và đề xuất chuyển, không đợi Linh hỏi.
- Chuyển: viết BAN-GIAO-THREAD.md trong thư mục dự án (đang chạy gì, cơ chế, đường dẫn, chờ Linh, việc kế), nhờ coordinator mở thread mới, xoá lịch gắn thread cũ, thread mới tạo lại lịch.
