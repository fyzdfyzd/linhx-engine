may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 30
khong_tien_phut: 15
theo_doi: C:\linhx\ifagent-wt\bhc-sua-3
nhan: may-2 2026-11-18T03:00:51+0700
moc: b35388c81b8ac62bab1851692208d236189b79d1

Lưu ý máy: KHÔNG background task/subagent; tiền cảnh; `npm.cmd`. Commit đầu trong 5 phút, push mỗi bước.
Hoàn tất đợt 3 trên nhánh agy/bhc-sua-3 (b35388c), worktree cũ C:\linhx\ifagent-wt\bhc-sua-3. KHÔNG đổi giao diện nữa.
1. Lint đang đỏ: public/quan-tri/render-qt.js 301 dòng (tối đa 300) → tách một phần sang file mới, không đổi hành vi.
2. Thêm luật lint khoá trong scripts/lint.js: CSS trong public/ và so-sanh-html.js có font-size < 14px (trừ selector chứa .kicker/.nhan/.eyebrow tối thiểu 12px) hoặc nút (button, .nut, a.nut) có min-height/height < 44px → báo lỗi, thông báo ghi "tăng lên ≥14px / ≥44px". Test cho luật này (một CSS giả vi phạm phải bị bắt).
3. Ảnh vàng landing NOP đã được Claude cập nhật theo cỡ chữ mới (test landing xanh trên cloud); không sửa test landing.
verify + test:lap xanh. Push agy/bhc-sua-3.

nhip: 03:13 12p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
