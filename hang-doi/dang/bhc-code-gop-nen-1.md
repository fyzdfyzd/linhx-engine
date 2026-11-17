may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\ifagent-wt\bhc-nen
nhan: may-2 2026-11-17T08:50:23+0700

Lưu ý máy: KHÔNG dùng background task, subagent hay thợ con; mọi lệnh chạy tiền cảnh. Gọi `npm.cmd`/`npx.cmd`. Push sau MỖI commit. Server chạy bằng Start-Process, tắt đúng PID.
Brand health check: gộp nhánh nền chung + sửa lỗi tải PDF.
1. `git -C C:\linhx\ifagent fetch origin`; worktree C:\linhx\ifagent-wt\bhc-nen, nhánh mới agy/bhc-nen từ origin/agy/bhc-code-noi-app; lần lượt `git merge --no-edit` origin/agy/bhc-test-e2e, origin/agy/bhc-code-openrouter, origin/agy/bhc-code-khung-quan-tri. Xung đột: giữ phần của cả hai, ghi lại file xung đột. Push.
2. Lỗi sản phẩm (E2E-02 trong bang-chung/bhc-test-e2e/so-sanh-2-lan.md): báo cáo vừa quét mở /bao-cao/<mã>/ được nhưng `GET /bao-cao/<mã>/tai/full.pdf` trả 404. Sửa: lần đầu tải thì dựng PDF Full/Light từ JSON báo cáo (dùng in-pdf.js sẵn có), lưu vào data/ cạnh báo cáo, các lần sau trả file đã lưu; đang dựng thì trả trang chờ có tự tải lại, lỗi dựng thì hiện câu dễ hiểu (không lộ lỗi kỹ thuật). Nút "Tải PDF" trên landing không bao giờ dẫn tới 404.
3. Test E2E-02 phải từ đỏ thành xanh. Chạy toàn bộ `npm.cmd run verify` HAI lần liên tiếp, cả hai lần 0 fail.
4. Bằng chứng bang-chung/bhc-nen/: log 2 lần verify, ảnh trang PDF trang 1 của một báo cáo vừa quét bằng AI giả.
CẤM: deploy, gọi AI thật, in khoá, sửa test cũ (trừ khi test cũ sai do gộp, ghi rõ), đụng apps/event, apps/lab, packages/. Trạng thái cao nhất REVIEW.
KET-QUA.md: `dat: co|khong`; SHA; file xung đột; E2E-02 đỏ→xanh; verify 2 lần pass/fail.

nhip: 08:56 6p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
