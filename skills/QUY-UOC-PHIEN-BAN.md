# Quy ước phiên bản kho skill LINHX

Bản 1.0, 9/11/2026. Công cụ: `scripts/skill_ban.py`. Skill hướng dẫn cho agent: `le/phien-ban-skill`.

## 1. Đơn vị phiên bản

| Đơn vị | Số bản nằm ở | Nhật ký | Tag phát hành |
|---|---|---|---|
| Bộ `bo/<ten>/` (cả bộ chung một số) | `.claude-plugin/plugin.json` → `"version"` | `bo/<ten>/CHANGELOG.md` | `<ten>@x.y.z` |
| Skill lẻ `le/<ten>/` | frontmatter `SKILL.md` → `metadata.version` | `le/<ten>/CHANGELOG.md` | `<ten>@x.y.z` |

`luat/` và `tho/` chưa đánh số; đổi lớn ở đó ghi vào commit như cũ.

## 2. Khi nào tăng mức nào (SemVer)

- **patch**: sửa lỗi, sửa câu chữ để skill chạy đúng hơn, cách gọi giữ nguyên.
- **minor**: thêm bước, tham chiếu, script, skill con; ai đang dùng vẫn gọi như cũ.
- **major**: đổi tên, đổi đầu vào hay đầu ra, bỏ bước hoặc skill con mà quy trình khác đang dựa vào.

**Độ chín đọc từ số bản.** Dưới `1.0.0` là thử nghiệm. Lên `1.0.0` khi đã chạy thật đạt chuẩn (với workflow: qua vòng 2 và vòng 3 của WF-CHUAN không phải sửa lớn) và Linh đồng ý. Không hạ bản, không dùng lại số đã gắn tag.

## 3. Nhật ký thay đổi

Theo Keep a Changelog, mục mới nằm trên cùng, nhóm bằng tiêu đề tiếng Việt: **Thêm, Đổi, Sửa, Bỏ, Bảo mật**. Mỗi dòng là một câu trọn ý nói cái gì khác đi với người dùng skill, không chép lại commit.

```
## [0.4.0] - 2026-11-12
### Thêm
- Bước 7 kiểm ảnh bìa bằng ảnh vàng trước khi dàn trang.
```

## 4. Lệnh

```
python scripts/skill_ban.py tang <ten> patch|minor|major "ghi chú" [--loai Bỏ]
python scripts/skill_ban.py marketplace           # cập nhật .claude-plugin/marketplace.json
python scripts/skill_kiem.py --index              # cập nhật INDEX.md, danh-muc.json (có cột Bản)
python scripts/skill_ban.py kiem --base origin/main
python scripts/skill_ban.py ds                    # xem bản mọi đơn vị
```

## 5. CI chặn gì (`.github/workflows/skills.yml`)

Lỗi (đỏ): frontmatter không đọc được YAML; file có BOM; thiếu `name`/`description`; số bản không phải x.y.z; `CHANGELOG.md` thiếu mục của bản hiện tại; `plugin.json` sai tên; marketplace lệch; **đơn vị có sửa mà không tăng bản** (bỏ qua bằng nhãn PR `khong-tang-ban` khi chỉ sửa chính tả); kho đếm ra 0 đơn vị.
Cảnh báo (vàng): `name` chưa theo chuẩn chữ-thường-gạch-nối hoặc khác tên thư mục; `description` quá 1024 ký tự; `SKILL.md` quá 500 dòng.

Khi gộp vào `main`, job `phat-hanh` gắn tag `<ten>@<bản>` cho mọi đơn vị vừa có bản mới, nội dung tag là mục CHANGELOG của bản đó.

## 6. Cài và cập nhật

- Máy MSI hoặc máy cty DESKTOP-PVHR2CD: `git pull` rồi `skills\cai.ps1` như cũ (junction, luôn là bản mới nhất của `main`).
- Claude Code: `/plugin install <ten> --marketplace fyzdfyzd/linhx-engine` (hoặc `/plugin marketplace add fyzdfyzd/linhx-engine` rồi `/plugin install <ten>@linhx`). `claude plugin validate .` đạt ngày 9/11; chưa thử cài thật từ repo riêng tư, cần đăng nhập GitHub có quyền đọc. Claude Code chỉ kéo bản mới khi số bản tăng, nên sửa mà quên tăng bản là người dùng không nhận được (lý do CI chặn).
- Muốn ghim một bản cũ: `git checkout <ten>@x.y.z -- skills/<loai>/<ten>`.

## 7. Đối chiếu các kho skill quốc tế

Đọc trực tiếp mã nguồn ngày 9/11/2026.

| Kho | Cách đánh bản | LINHX lấy gì |
|---|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | `marketplace.json` gom skill thành plugin; frontmatter theo [chuẩn Agent Skills](https://agentskills.io/specification) (`name`, `description`, `license`, `metadata`) | để số bản skill lẻ ở `metadata.version` đúng chuẩn; marketplace gốc repo |
| [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) | mỗi plugin một `version` trong `plugin.json`; plugin ngoài ghim theo SHA, máy tự mở PR nâng | bộ = plugin có bản riêng; ghim bản bằng tag |
| [trailofbits/skills](https://github.com/trailofbits/skills) | `version` trong `plugin.json` phải khớp marketplace và **phải tăng khi sửa** (nhãn `no-version-bump` để bỏ qua); bắt YAML hỏng vì dấu hai chấm; bộ kiểm đếm 0 phải đỏ | gần như toàn bộ phần CI: kiểm tăng bản, nhãn bỏ qua, bắt YAML hỏng, cảnh báo 500 dòng, tự kiểm bộ kiểm |
| [obra/superpowers](https://github.com/obra/superpowers) | một số bản cho cả kho, `RELEASE-NOTES.md` viết cho người dùng có số đo trước/sau, script bump có kiểm lệch | nhật ký viết cho người dùng, nói cái gì khác đi |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | không đánh số; CI dựng chỉ mục khám phá và đóng gói zip mỗi lần đẩy | chỉ mục sinh tự động (đã có `INDEX.md`) |

Chọn bản theo từng đơn vị (như Trail of Bits, knowledge-work-plugins) thay vì một số cho cả kho (như Superpowers), vì kho LINHX có 116 đơn vị đi nhanh chậm khác nhau. Tag dạng `<ten>@x.y.z` theo lối monorepo (changesets) để mỗi đơn vị có lịch sử riêng trong một repo.

Chưa làm, để đợt sau: bộ eval cho từng skill (skill-creator của Anthropic, thử A/B có/không skill của Superpowers và stageshow), gói zip mỗi bản phát hành.
