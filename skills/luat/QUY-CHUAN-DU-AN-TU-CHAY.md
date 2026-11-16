# Quy chuẩn dự án tự chạy (agy làm, Claude canh)

Bản 1.1 · 16/11/2026 (1.0 ngày 30/10) · Rút từ dự án Chiêm Tinh Số (repo fyzdfyzd/chiemtinhso) và LINHX ENGINE. Bản chính ở `linhx-engine/skills/luat/`. Áp cho mọi dự án production mới của Linh, ví dụ máy quét crawler.

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

## 9. Luật máy trước, văn xuôi sau (Linh 16/11, trọng tâm)
Thứ tự đầu tư, mạnh nhất trước: code sạch trong repo (thợ sau chép theo code trước) → luật máy (lint, test kiến trúc, `rao.py`) → bộ nghiệm thu → `AGENTS.md` và skill văn xuôi → người đọc diff.
- Mỗi lần chấm CHUA_DAT, Claude canh hỏi: máy bắt được lỗi này không? Được thì **trong ngày** thêm một luật vào `canh/luat-lint.json` (mã, nguồn là phiếu + commit, vùng, mẫu cấm, cách sửa, ví dụ sai, ví dụ đúng), chạy `canh/luat_lint.py --tu-kiem`, commit lên nhánh tích hợp. Không thêm câu dặn vào `AGENTS.md` cho lỗi máy bắt được.
- Thông báo lỗi phải nói **cách sửa**, vì thợ đọc nó như đề: `file:dòng [L003] Test gọi mạng thật. Sửa: dùng dữ liệu mẫu...`.
- Lỗi cấu trúc (import chéo module, sửa ngoài vùng) đưa vào test kiến trúc hoặc `rao.py`; lint dòng chỉ cho mẫu nhìn thấy trên một dòng.
- Lint chỉ soi **dòng thêm** của phiếu (`--goc <sha mốc phiếu>`) để không chặn nợ cũ. Nợ cũ (`luat_lint.py <repo>` không `--goc`) gom thành phiếu dọn riêng.
- Cấm comment biện minh cho chỗ vá tạm (L004): thợ sau đọc thấy "có lý" rồi chép khắp nơi. Vá không được thì ghi `.handoff/VAN-DE.md`.
- File luật nằm trong `canh/**`, thợ không sửa được. Lỗi lặp lần 2 mà chưa có luật là lỗi của người canh.
- 4 luật hạt giống (16/11): L001 test skip, L002 khoá bí mật, L003 test gọi mạng thật, L004 comment vá tạm. Đều chuyển từ câu văn xuôi trong `CLAUDE.md` sang máy.

## 10. Nghiệm thu bằng bằng chứng chạy thật
- Mỗi feature có `bang_chung` do **bộ chạy** tạo, thợ không tự chụp tay: giao diện thì ảnh 360 và 1280, có tương tác thì thêm video ngắn luồng chính; API, logic thì log `lenh_kiem`; job thì log một lượt chạy trên dữ liệu mẫu.
- Claude chấm theo thứ tự: máy (rào, lint, `cong_kiem`) → xem bằng chứng → đọc diff chỉ phần chạm tiền, quyền, chạy lệnh. Máy đã trượt thì không gọi Claude chấm.
- Linh nghiệm thu bằng ảnh ghép và video, không đọc code.

## 11. Bản đồ tính năng chung
- Mỗi sản phẩm có `docs/BAN-DO-TINH-NANG.md` (mẫu: `skills/le/linhx-tu-chay/mau/BAN-DO-TINH-NANG.md`): mọi màn hình, nút, luồng gọi theo cách người dùng gọi, mỗi cái một mã `TN-xx`, kèm đường dẫn, file chính, test e2e, ảnh mới nhất.
- Linh, Claude, agy dùng chung mã này trong đề và góp ý ("TN-07 nút Mua ở thẻ gói"), không tả kiểu "cái nút bên trái".
- Feature trong `features-dotN.json` ghi trường `tn`; phiếu đổi giao diện thì cập nhật bản đồ trong vùng của phiếu.
- Khác `scripts/ban_do.py`: đó là bản đồ code cho thợ, đây là bản đồ theo mắt người dùng.

## 12. Sạch một máy rồi mới nhân máy
Cổng trước khi thêm máy, thêm làn song song hoặc cho chạy đêm không người:
- 10 phiếu liền trên một máy: ≥ 70% đạt lần đầu (Linh chỉnh số này), 0 vi phạm rào K1/K3, 0 phiếu quá trần mà không bị cắt, lint sạch dòng thêm.
- Lỗi máy (RAM, timeout, hết hạn mức) ghi riêng, không tính vào tỉ lệ đạt.
- Chưa qua cổng thì sửa vòng trong (đề, luật, rào) trên chính máy đó. Nhân máy khi vòng trong còn sinh rác chỉ đốt token nhanh hơn để ra nhiều rác hơn.
- Số đo ghi `VONG.md`; Claude báo Linh một dòng khi qua cổng.

Không lấy từ bài Lauren Tan: TLA+, Lean (quá nặng cho đội nhỏ), agent tự merge (chỉ Linh merge main).

## Lịch sử
| Bản | Ngày | Thay đổi |
|---|---|---|
| 1.0 | 30/10/2026 | Bản đầu, từ Chiêm Tinh Số |
| 1.1 | 16/11/2026 | Thêm mục 9–12 từ bài "All Code Is Slop (Except Mine)" của Lauren Tan: luật máy + `canh/luat_lint.py`, bằng chứng, bản đồ tính năng, cổng nhân máy |
