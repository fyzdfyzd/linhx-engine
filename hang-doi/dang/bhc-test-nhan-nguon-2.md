may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\ifagent-wt\bhc-code-nhan-nguon
phu_thuoc: bhc-test-nhan-nguon-1
nhan: may-2 2026-11-17T01:31:02+0700
moc: 139f3226610dfe54a25e66b6156bf4ba0679d532

Lưu ý máy: KHÔNG dùng background task, subagent hay thợ con; mọi lệnh chạy tiền cảnh và chờ xong. Trong PowerShell gọi `npm.cmd`/`npx.cmd`. Push nhánh sau MỖI commit. Nếu C:\linhx\ifagent-wt\bhc-code-nhan-nguon đã có thì dùng lại, nhánh agy/bhc-code-nhan-nguon.
Brand health check, phần 2/2: luật khoá + bằng chứng. Nền: nhánh agy/bhc-code-nhan-nguon (đã có hàm nhanNguon).
1. Thêm vào apps/brand-health/scripts/lint.js kiểm tra: dựng HTML landing và HTML trang PDF từ 2 JSON trong bao-cao/bien-tap/ (dùng hàm dựng sẵn có), nếu khớp /gemini-(nho|tim)|claude-|gpt-|openai/i thì lỗi: "Mã nguồn thô lọt ra người xem: <chuỗi> ở <nơi>. Dùng nhanNguon() trong server/lib/nhan-nguon.js." Chứng minh đỏ: tạm checkout 5942bf0 vào thư mục tạm khác và chạy luật thấy đỏ (ghi log), trên nhánh thì xanh.
2. `npm.cmd run verify` xanh. In PDF 2 thương hiệu bằng `node scripts/in-bao-cao.js <json> --ra out/<ten>`: số trang Full 40 / Light 4 không đổi.
3. `npm.cmd start` (cổng 3020, chạy tiền cảnh trong cửa sổ riêng bằng Start-Process, nhớ PID), chụp bằng Playwright trên http://localhost:3020: landing 2 thương hiệu màn đầu 1280×800 và 360×780; chép ảnh trang PDF Vinamilk p2 và IF Agent trang có bảng câu sai/nhầm. Vào apps/../bang-chung/bhc-code-nhan-nguon/ (gốc worktree), mỗi ảnh ≤ 600 KB. Tắt server bằng đúng PID.
4. Commit, push agy/bhc-code-nhan-nguon.
CẤM như phần 1.
KET-QUA.md: `dat: co|khong`; SHA; log luật đỏ trên 5942bf0 → xanh; verify pass/fail; số trang PDF; danh sách ảnh.

nhip: 01:46 15p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
