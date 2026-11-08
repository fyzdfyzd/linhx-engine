# Kho skill LINHX (bản chuẩn duy nhất)

Mọi skill, workflow, luật làm việc của LINHX ở đây. Claude, Antigravity (agy), Gemini, Copilot đều đọc chuẩn `SKILL.md` (đầu file có `name`, `description`).

| Thư mục | Là gì |
|---|---|
| `bo/<ten-bo>/` | bộ nhiều skill kèm script, mẫu (có `.claude-plugin/plugin.json`) |
| `le/<ten>/` | skill lẻ |
| `luat/` | luật chung: luật tổng agy (`GEMINI-agy-toan-cuc.md`), luật kho `D:\LINHX`, LAB, PROTOTYPE, OPC, tri thức agy |
| `tho/` | đội thợ con (tìm nguồn, đọc nguồn, kiểm chứng, viết) |
| `INDEX.md`, `danh-muc.json` | danh mục theo nhóm, sinh tự động |
| `_nguon.json` | bản gốc cũ của từng skill (ở LAB nào) để đối chiếu |

## Luật

1. **Sửa ở đây, không sửa bản chép.** Bản trong các LAB, `D:\LINHX\SKILLS`, vendor của PROTO từ 8/11/2026 chỉ là bản cũ.
2. Mỗi tên skill chỉ có một. Trùng là CI đỏ.
3. Không đưa bí mật (`.env`, cookie, khoá, token), không file trên 5 MB. Ảnh mẫu nặng để Drive, ghi link.
4. Thêm hoặc sửa skill xong: `python scripts/skill_kiem.py --index`, rồi commit cả `INDEX.md`.

## Cài trên máy (MSI hoặc máy cty DESKTOP-PVHR2CD)

```powershell
cd <repo linhx-engine>
git pull
powershell -ExecutionPolicy Bypass -File skills\cai.ps1
```

Lệnh nối từng skill vào `~\.gemini\antigravity\skills` (agy) và `~\.claude\skills` (Claude Code) bằng junction, nên `git pull` là skill mới có ngay, không chép lại. Không xoá thư mục thật nào.

## Gom lại từ nguồn cũ

`python scripts/skill_gom.py "D:\LINHX=D:/LINHX" "<thư mục chung>=thư mục chung"`: chọn bản sửa gần nhất của mỗi skill, bỏ bản trùng, bỏ bí mật và file nặng, ghi đè `bo/`, `le/`.
