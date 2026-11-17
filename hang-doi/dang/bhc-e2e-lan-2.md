may: may-2
loai: test
model: gemini-4-argon-high
tran_phut: 60
khong_tien_phut: 25
theo_doi: C:\linhx\ifagent-wt\bhc-e2e-lan-2
nhan: may-2 2026-11-18T00:56:23+0700

Lưu ý máy: KHÔNG background task/subagent; tiền cảnh; `npm.cmd`/`npx.cmd`. Commit + push mỗi 10 phút.
0. Chờ nền: `git fetch origin agy/bhc-sua-3`; nếu nhánh chưa có commit luật lint cỡ chữ/cỡ nút thì chờ 5 phút rồi kiểm lại, tối đa 60 phút; quá thì DỪNG, ghi CHUA_CO_NEN.
E2E giao diện vòng 2 (chấm lại sau sửa). Worktree C:\linhx\ifagent-wt\bhc-e2e-lan-2, nhánh agy/bhc-e2e-lan-2 từ origin/agy/bhc-sua-3. Lấy kịch bản apps/brand-health/e2e-giao-dien/khach.mjs từ origin/agy/bhc-e2e-khach và quan-tri.mjs từ origin/agy/bhc-e2e-quan-tri (giữ nguyên các bước K1–K9, Q1–Q7 và tự kiểm). KHÔNG sửa code app.
Chạy cả hai luồng 2 lần độc lập (DATA_DIR trắng mỗi lần, AI giả, không mạng ngoài). Ảnh 1280×800 + 360×780 full page mỗi bước: bang-chung/bhc-e2e-lan-2/<khach|quan-tri>/lan-<n>/<ma>-<1280|360>.png, video webm lan-1. Ghi so-sanh-2-lan.md và loi.md (mã bước, mức chặn/nặng/nhẹ, ảnh, cách sửa). Push agy/bhc-e2e-lan-2.
KET-QUA.md: số bước đạt/hỏng mỗi lần mỗi luồng, danh sách lỗi còn lại.
