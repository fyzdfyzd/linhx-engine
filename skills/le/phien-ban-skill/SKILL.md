---
name: phien-ban-skill
description: "Quy trình sửa, tăng bản và phát hành skill trong kho LINHX (linhx-engine/skills): chọn mức patch/minor/major, ghi CHANGELOG, chạy bộ kiểm, để CI gắn tag. Dùng mỗi khi tạo, sửa, đổi tên hay bỏ một skill hoặc bộ skill, hoặc khi được hỏi skill đang ở bản nào."
metadata:
  version: "0.1.0"
---

# Phiên bản skill LINHX

Kho chuẩn duy nhất là `skills/` của repo linhx-engine. Mỗi **đơn vị** có một số bản SemVer và một `CHANGELOG.md`:

- bộ `skills/bo/<ten>/`: bản nằm ở `.claude-plugin/plugin.json` (`"version"`), cả bộ chung một số.
- skill lẻ `skills/le/<ten>/`: bản nằm ở frontmatter `SKILL.md`, khoá `metadata.version`.

Quy ước đầy đủ: `skills/QUY-UOC-PHIEN-BAN.md`.

## Các bước khi sửa một skill

1. Sửa nội dung trong `skills/`, không sửa bản chép ở LAB hay `~\.claude\skills`.
2. Chọn mức tăng:
   - **patch** (x.y.**z**): sửa lỗi, sửa câu chữ làm skill chạy đúng hơn, không đổi cách gọi.
   - **minor** (x.**y**.0): thêm bước, thêm tham chiếu, thêm script hay skill con; người dùng cũ vẫn gọi như cũ.
   - **major** (**x**.0.0): đổi tên, đổi đầu vào hay đầu ra, bỏ bước mà quy trình khác đang dựa vào, bỏ skill con.
3. Chạy, ghi rõ việc đã đổi bằng câu trọn ý:
   `python scripts/skill_ban.py tang <ten> patch "Sửa bước 3 bỏ sót ảnh tham chiếu"`
   Thêm `--loai Bỏ` hoặc `--loai "Bảo mật"` khi cần; mặc định patch là Sửa, minor là Thêm, major là Đổi.
4. Chạy `python scripts/skill_ban.py marketplace` và `python scripts/skill_kiem.py --index`.
5. Chạy `python scripts/skill_ban.py kiem --base origin/main`; phải ra 0 lỗi rồi mới commit.
6. Commit cả skill, `CHANGELOG.md`, `INDEX.md`, `danh-muc.json`, `.claude-plugin/marketplace.json`.

Khi PR gộp vào `main`, CI tự gắn tag `<ten>@<bản>` cho mọi đơn vị vừa lên bản.

## Lên 1.0.0

Dưới 1.0.0 nghĩa là đang thử nghiệm. Chỉ đưa một đơn vị lên 1.0.0 khi nó đã chạy thật đạt chuẩn (với workflow: qua vòng 2 và vòng 3 của WF-CHUAN không phải sửa lớn) và Linh đồng ý.

## Không được

- Sửa skill mà không tăng bản: CI đỏ. Chỉ sửa chính tả thì gắn nhãn PR `khong-tang-ban`.
- Viết `description` có dấu hai chấm mà không bọc trong dấu nháy kép: YAML hỏng, trình nạp bỏ trống mô tả và skill không bao giờ được gọi.
- Lưu file có BOM đầu (Notepad cũ hay làm vậy).
- Hạ bản hay dùng lại một số bản đã gắn tag.

## Xem bản hiện có

`python scripts/skill_ban.py ds` in bản của mọi đơn vị; `skills/INDEX.md` có cột Bản; lịch sử một đơn vị ở `CHANGELOG.md` của nó hoặc `git tag -l "<ten>@*"`.
