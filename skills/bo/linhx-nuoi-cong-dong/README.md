# linhx-nuoi-cong-dong v0.1 (LAB041)

Plugin Claude Code nuôi cộng đồng theo chuỗi content → cộng đồng → bán. Agent soạn, chấm, đề xuất; người duyệt và gửi. Hồ sơ đầu tiên: cộng đồng học viên LINHX.

## Cài
1. Chép thư mục này vào nơi để plugin (ví dụ `D:\LINHX\SKILLS\plugins\linhx-nuoi-cong-dong`) và bật như các plugin linhx khác. Với Antigravity: chép `skills/*` vào `.agents/skills`.
2. Tạo thư mục cộng đồng rồi chạy `python scripts/nuoi.py init` trong đó (tạo `data/cong-dong.db`, `config/cong-dong.json`, `nhap/`, `output/`).

## Lệnh
```
nuoi.py nhap thanh-vien|su-kien|don|link <file.csv>
nuoi.py tuan [--ngay YYYY-MM-DD]     # chấm + SOP + đề xuất + sức khoẻ → output/BAO-CAO-TUAN.md
nuoi.py cham | sop | de-xuat | suc-khoe
nuoi.py danh-dau <id> nhan|da-lam|bo|tu-choi
nuoi.py xong-sop <lớp> <mốc>
nuoi.py link tao --kenh zalo --chien-dich ws1511 --url https://...
```

## Skill
| Skill | Việc |
|---|---|
| nuoi-cong-dong | Điều phối vòng tuần |
| chan-doan-giai-doan | Cộng đồng đang ở tầng nào, nghẽn đâu |
| ke-hoach-90-ngay | Kế hoạch theo khung 5 tầng – 2 vòng |
| nhap-du-lieu | Danh sách lớp, chat nhóm, Zoom, đơn → CSV → CSDL |
| chao-don-gan-tag | Lời chào + câu hỏi chia nhánh + tin SOP theo mốc |
| de-xuat-tuan | Đề xuất → việc + tin nháp |
| cau-hoi-thanh-noi-dung | Câu hỏi cộng đồng → 3 đề bài nội dung |

Hook `cong_gui_ra`: công cụ MCP nào có vẻ gửi/đăng ra ngoài thì bắt hỏi duyệt; lỗi cũng hỏi duyệt.

## Mượn ý từ đâu
crowd.dev (bảng điểm, Apache-2.0), Orbit Model (cấp, MIT), Savannah (đề xuất có trạng thái, chỉ ý tưởng), easyink/OpenSCRM (SOP theo mốc, link nguồn `state`, chỉ ý tưởng), 源雀 (ý định mua), tg-spam/hivemtk (cổng duyệt). Chi tiết: LAB041 refs/B, refs/C. Không chép mã GPL/AGPL.

## Thử
`test/gia_lap.py` trong LAB041 sinh 158 học viên giả lập ở 6 lớp; chạy 2 tuần liên tiếp cho ra 25 đề xuất/tuần, SOP gom theo lớp, không nhắc lại đề xuất đã xử lý.
