may: may-2
loai: code
tran_phut: 30
khong_tien_phut: 20
theo_doi: C:\linhx\ifagent-wt\bhc-test-nen
vung: bang-chung/bhc-test-nen/**
nhan: may-2 2026-11-16T22:56:22+0700

Phiếu kiểm nền "Brand health check" (công cụ đo brand IF Agent). CHỈ KIỂM VÀ CHỤP, KHÔNG SỬA CODE. Chạy mọi lệnh ở tiền cảnh, làm tuần tự, không sinh thợ con.
1. `git -C C:\linhx\ifagent fetch origin claude/project-thread-apl8gd` rồi `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\bhc-test-nen -b agy/bhc-test-nen origin/claude/project-thread-apl8gd`. HEAD phải là 5942bf0, khác thì dừng, ghi SAI_NEN.
2. Trong apps/brand-health: `npm run verify` (AI giả, không tốn tiền). Log thô vào bang-chung/bhc-test-nen/verify.txt (thư mục bang-chung ở gốc worktree). Ghi số pass/fail.
3. In PDF: với mỗi file trong apps/brand-health/bao-cao/bien-tap/*.json chạy `node scripts/in-bao-cao.js <json> --ra out/<ten>` (out/ không commit). Ghi số trang Full/Light. Chép ảnh trang 1 và 2 bản Full của mỗi thương hiệu vào bang-chung/bhc-test-nen/pdf-<ten>-p1.png, -p2.png (mỗi ảnh ≤ 600 KB, nén nếu cần).
4. `npm start` (cổng 3020), đợi /healthz 200. Tìm đường landing báo cáo /bao-cao/<mã>/ của 2 thương hiệu trong server/app.js (không tìm được thì ghi CHUA_RO_DUONG). Viết script Playwright nhỏ ngoài repo, chụp trên http://localhost:3020 (cấm file://): trang chủ / và 2 landing, mỗi trang ở 1280×800 và 360×780, dpr 1: ảnh màn đầu (viewport) và ảnh toàn trang. Tên: <trang>-1280-dau.png, <trang>-1280-toan.png, <trang>-360-dau.png, <trang>-360-toan.png, ≤ 600 KB mỗi ảnh (toàn trang dài thì chụp JPEG chất lượng 80). Với mỗi trang ghi: lỗi console, tràn ngang ở 360 (document.documentElement.scrollWidth > innerWidth), và bấm thử nút tải PDF (status HTTP của file). Tắt server bằng đúng PID của nó.
5. Commit chỉ bang-chung/bhc-test-nen/, tiêu đề "bhc: bằng chứng kiểm nền 5942bf0", push `agy/bhc-test-nen`.
CẤM: sửa bất kỳ file nào ngoài bang-chung/bhc-test-nen/, deploy, gọi AI thật hay dùng khoá API, in khoá/mật khẩu, gửi mail, xoá dữ liệu, tự sinh ảnh bằng AI, push nhánh khác. Gặp việc cần người thì trả CAN-LINH.
Trả lời KET-QUA.md (ngắn): dòng đầu `dat: co` hoặc `dat: khong`; SHA đỉnh agy/bhc-test-nen; verify pass/fail; số trang Full/Light mỗi thương hiệu; bảng trang × (console lỗi, tràn 360, PDF tải HTTP); danh sách ảnh đã commit.

nhip: 23:04 8p đang chờ nền · log cuối 0 phút trước [log_cuoi=2026-11-16T23:04:35+0700] · root agent idle; waiting up to 40m0s for 1 ba
