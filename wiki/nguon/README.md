# Nguồn gốc

Tài liệu gốc, **chỉ thêm, không sửa**. Tên `YYYY-MM-DD-TEN.md`. Bản mới là file mới.

| File | Là gì | Gốc |
|---|---|---|
| 2026-10-30-QUY-CHUAN-DU-AN-TU-CHAY.md | Quy chuẩn agy làm, Claude canh | thư mục chung `QUY-CHUAN/` |
| 2026-11-05-CHOT-KIEN-TRUC.md | Chốt Frappe, so 7 ứng viên | `LAB111-LINHX-ENGINE/04-CHOT-KIEN-TRUC.md` |
| 2026-11-05-BAN-GIAO-LINHX-ENGINE-KIEN-TRUC.md | Bàn giao thread kiến trúc | `LAB111-LINHX-ENGINE/.handoff/` |
| 2026-11-06-BAN-GIAO-QUY-HOACH-TUNG-UNIT.md | Bàn giao EDU | như trên |
| 2026-11-06-BAN-GIAO-AGENT-FORCE.md | Bàn giao Agent Force | như trên |
| 2026-11-06-BAN-GIAO-PERSONAL-BRAND.md | Bàn giao Personal Brand | như trên |
| 2026-11-06-BAN-GIAO-CAC-BU.md | Bàn giao nhóm BU | như trên |
| 2026-11-08-BAN-DO-CTS-K6.md | Bản đồ Chiêm Tinh Số → engine | `LAB111-LINHX-ENGINE/dot1/` |
| 2026-11-08-HOC-HOI-K5.md | Học hỏi K5 | như trên |
| 2026-11-08-BANG-HE-THONG.json | Ảnh chụp db artifact Wyeq3 (he_thong 63 dòng + tong: buc_tranh, claude, launch) lúc 2026-11-07 23:15Z | artifact Wyeq3HaoB6pfgoeC11P2qY |

## Nguồn ngoài wiki (chưa chép, đọc khi cần)
- Thư mục chung dự án Claude `LINHX LAB`: `/mnt/project-files/LAB111-LINHX-ENGINE/` (01–03 nghiên cứu, KIEN-TRUC cũ, nguon/ PLAN, BU_INPUT, PROTO INDEX), `CHIEMTINH-VN/`, `BAN-GIAO-0311/`, `LINHX-second-brain/` (khung D:\LINHX 8/10).
- Máy cty: `D:\LINHX` (AGENTS.md gốc, LAB, PRJ, EDU, KB, SKILLS), `D:\@WF\WIKI` (LINHX plan daily, không đụng).
- Memory dự án Claude (chỉ Claude đọc được); sự thật chung phải có bản ở wiki này.

Làm lại trang từ bảng: lấy db artifact (ArtifactData list `he_thong`, `tong`), lưu thành file `nguon/<ngay>-BANG-HE-THONG.json` mới, chạy `python scripts/wiki_tu_bang.py wiki/nguon/<file>`.
