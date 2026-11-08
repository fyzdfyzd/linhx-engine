# Chuyển dữ liệu MSI sang máy cty (8/11/2026)

MSI = máy cá nhân. Máy cty = DESKTOP-PVHR2CD.

## 1. Ưu tiên 1: skill, workflow, quy trình cho agy máy cty (đã làm)

- Gói sạch 164 MB: 3.763 file từ `D:\LINHX` (SKILLS, .agents, .claude, plugin trong LAB/PROTO/PRJ, luật AGENTS/CLAUDE/GEMINI) + skill riêng của agy MSI (`~\.gemini\config\skills`, `linhx-course`, `linhx-tracking`, `knowledge`, luật tổng `GEMINI.md`) + 25 bộ skill mới chỉ có ở thư mục chung (thiet-ke, linhx-chuan, vong-lap-slide, web-thiet-ke, tach-kv, casting, linhx-4d, agy-tu-chay…).
- Đã bỏ: `.env`, cookie, khoá, `oauth_creds`, `mcp_config`, zip, video, file trên 8 MB, node_modules, .venv, .git, output. Danh sách bỏ: `goi-skill-msi-0811b-bo-qua.txt`.
- Đường đi: nhánh `chuyen/skill-0811` của repo linhx-engine (như lần chuyển PROTO). Máy cty kéo về, chạy `CAI-SKILL-MAY-CTY.ps1`: chép vào đúng chỗ cũ trên `D:\LINHX` (không đè file mới hơn), rồi nối từng skill vào thư mục skill toàn cục của agy bằng junction, nên agy mở dự án nào cũng thấy.
- Danh mục 263 skill theo nhóm: `DANH-MUC-SKILL-MSI.md`.

## 2. Dữ liệu dự án (chờ Linh chốt)

| Thư mục MSI | Cỡ | Chuyển | Ghi chú |
|---|---|---|---|
| `PRJ\BESPOKEAI` (chị Hương) | 1 GB | chuyển, bỏ ~470 MB | bỏ 3 bản trùng PDF VML 122 MB và 2 zip bàn giao; máy cty mới có `CHI-HUONG` |
| `PRJ\KIMGIABAOGIFT-Q4` | 78 MB | chuyển cả | việc chị Hương |
| `BACKUP\email-quynh-huong` | 1 MB | chuyển | |
| `PRJ\IFAGENT` | lớn | chuyển, bỏ node_modules, .venv, test-results, v6/v7-ket-qua | là git cục bộ, 151 file chưa commit |
| `PRJ\IFAGENT-*`, `event-ifagent*` | lớn | chỉ code + tài liệu | |
| `LAB` (86 lab) | lớn | chỉ lab máy cty chưa có | máy cty đã có 17 lab |
| `EDU` (Sakédemy, TCB-VinUni) | lớn | deck + chương trình, bỏ video | |
| `PRJ\UNIKON` | trống | | Unikon nằm trong LAB012/043 brands + `00-INBOX\CRED` |
| `THU-VIEN-BAO-CAO` 1,4 GB, `ARCHIVE` 1 GB, `ai-ugc-video` 745 MB, `SanKhau3D`, `GAME ENGINE` | nặng | không chuyển | để lại MSI |

## 3. Bí mật (chép tay, không qua repo, không qua Drive chung)

`PRJ\_ENV\ifagent.env`, `PRJ\*\.env` (8 dự án ifAgent), `PRJ\CAFEBIZ-CONGNGHE\cau-hinh.env`, `PRJ\ifagent-infra\cau-hinh.env`, `LAB\LAB005-ZALO-NEWS\...\.env`, `00-INBOX\CRED` (Urah credential zip), profile Chrome có cookie trong `LAB043\.chrome-chatgpt`. Mang bằng USB hoặc dán tay qua UltraViewer.

## 4. Đồng bộ về sau

- Skill: sửa ở bản gốc, chạy lại gói này (nhánh mới `chuyen/skill-<ngay>`), máy cty chạy lại lệnh cài. Lâu dài: đưa `D:\LINHX\SKILLS` thành thư mục `skills/` trong repo linhx-engine, cả hai máy `git pull`.
- Dữ liệu dự án: Google Drive máy cty đã có `I:\My Drive\LINHX-CHUYEN-MAY`. Nếu MSI cài Google Drive cho máy tính thì đẩy qua đó; giải nén bằng Python zipfile để giữ tên tiếng Việt.
