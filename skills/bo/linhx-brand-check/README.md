# linhx-brand-check v0.1

Brand check thời đại agent theo **chuẩn ABC v1.0** (LAB036). Plugin Claude Code; Antigravity đọc `skills/*/SKILL.md` như hướng dẫn. Python 3.10+ thư viện chuẩn, không cần cài gì.

## Cài
1. Chép thư mục này vào `D:\LINHX\LAB\LAB036-BRAND-CHECK-AGENT\src\linhx-brand-check`.
2. Claude Code: `/plugin install` trỏ tới thư mục, hoặc chép `skills/*` vào `.claude/skills/`.
3. Kiểm: `python scripts\brandcheck.py tu-kiem` phải in XANH.

## Chạy nhanh (ví dụ)
```bat
cd scripts
python brandcheck.py khoi-tao -w D:\LINHX\BRAND-CHECK\vinamilk --brand Vinamilk --website vinamilk.com.vn --category "sữa tươi"
rem điền brand-facts.json (skill bang-su-that)
python brandcheck.py cau-hoi -w D:\LINHX\BRAND-CHECK\vinamilk --goi C
python brandcheck.py tat-ca  -w D:\LINHX\BRAND-CHECK\vinamilk --mo-hinh claude-tim,claude-nho,agy --luot 3 --giam-khao claude
```
Mở `lan\<ngày>\bao-cao.html`.

## Thư mục thương hiệu
```
<ws>/brand-facts.json        bảng sự thật
<ws>/cau-hoi.json            bộ câu hỏi đã sinh
<ws>/tin-hieu-tay.json       tín hiệu B2–B6 tra tay, có link
<ws>/lan/<ngày>/tra-loi/<mô hình>/<id>__l<lượt>.md   nguyên văn
<ws>/lan/<ngày>/cham/<mô hình>/<id>__l<lượt>.json     nhãn giám khảo
<ws>/lan/<ngày>/tin-hieu.json, diem.json, bao-cao.html, bao-cao.md
```

## Module
`brandcheck.py` (CLI) · `abc_lib` (sự thật, câu hỏi, dò tên, Wilson, phân loại nguồn) · `abc_hoi` (hỏi AI) · `abc_cham` (giám khảo) · `abc_tinhieu` (B1–B6) · `abc_diem` (16 chỉ số, AVI, bước agent) · `abc_baocao` (HTML, MD, kế hoạch) · `tu_kiem` · `nen/` (ai-visibility-skill, MIT).

## Chưa có ở v0.1
Tự gộp hai giám khảo; lịch chạy định kỳ và biểu đồ xu hướng (PA3); kịch bản agent bằng trình duyệt (hiện A10 chấm từ câu trả lời của mô hình có tra web); chạy thật với Gemini/OpenRouter chưa thử (container không có khoá).
