may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 40
khong_tien_phut: 20
theo_doi: C:\linhx\ifagent-wt\bhc-sua-2
nhan: may-2 2026-11-17T23:37:03+0700

Lưu ý máy: KHÔNG background task/subagent; tiền cảnh; `npm.cmd`/`npx.cmd`. Commit đầu trong 5 phút, commit + push mỗi 10 phút.
Sửa lỗi E2E đợt 2 (quản trị, theo dõi tháng). CHỈ chạy khi origin/agy/bhc-sua-1 đã có commit test khoá thương hiệu thứ ba; chưa có thì DỪNG, ghi CHUA_CO_NEN. Worktree C:\linhx\ifagent-wt\bhc-sua-2, nhánh agy/bhc-sua-2 từ origin/agy/bhc-sua-1. Đọc bang-chung/bhc-e2e-quan-tri/loi.md trên origin/agy/bhc-e2e-quan-tri. CHỈ sửa apps/brand-health.
Sửa: LOI-Q6-01 (mỗi làn một ô bật/tắt riêng: gemini-tim, gemini-nho, openai-tim, claude-tim, openrouter-gemini-tim, perplexity-tim; AI giả tạo đủ 6 làn), LOI-Q7-01 (so sánh khác chế độ quét: quy về tỉ lệ, chỉ tính đổi khi trạng thái chính đổi; ghi chú "Kỳ trước quét đầy đủ, kỳ này quét nhanh"), LOI-Q7-API-NOW-ISO (nhận chuỗi ISO).
Test khoá cho từng lỗi. Chạy lại e2e-giao-dien/quan-tri.mjs (từ origin/agy/bhc-e2e-quan-tri) cho Q6, Q7, ảnh vào bang-chung/bhc-sua-2/. verify + test:lap xanh. Push agy/bhc-sua-2.
