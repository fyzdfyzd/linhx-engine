may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 0
theo_doi: C:\linhx\ifagent-wt\bhc-code-nhan-nguon
nhan: may-2 2026-11-17T00:14:15+0700
moc: 996f173a1fe2f6a0395f1151933fc88203a67c38

Brand health check: bỏ chữ kỹ thuật khỏi phần người xem đọc. Chạy mọi lệnh ở tiền cảnh, tuần tự, không sinh thợ con.
1. `git -C C:\linhx\ifagent fetch origin claude/project-thread-apl8gd` rồi `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\bhc-code-nhan-nguon -b agy/bhc-code-nhan-nguon origin/claude/project-thread-apl8gd` (HEAD 5942bf0). Thiếu module khi test thì đặt NODE_PATH như phiếu bhc-test-nen.
2. Lỗi: báo cáo PDF và landing in mã nguồn thô cho người xem, ví dụ "gemini-nho/D2.2", "gemini-tim/C1.3", "· gemini-nho/C1.3" cạnh nút "Xem nguyên văn" ở màn đầu landing. Sửa: viết MỘT hàm dùng chung (vd server/lib/nhan-nguon.js) đổi mã thành chữ người đọc: gemini-nho → "Gemini, trả lời từ trí nhớ", gemini-tim → "Gemini, có tìm trên web", phần id giữ dạng "câu D2.2". Thay mọi chỗ in mã trong bao-cao/khung/B/*.js, server/lib/landing.js và nơi khác dùng cùng kiểu. Không đổi số, không đổi bố cục, không đổi chữ khác.
3. Luật khoá: thêm vào scripts/lint.js một kiểm tra quét HTML landing + HTML trang PDF dựng từ 2 JSON trong bao-cao/bien-tap/: nếu còn chuỗi khớp /gemini-(nho|tim)|claude-|gpt-|openai/ thì báo lỗi với thông báo "Mã nguồn thô lọt ra người xem: <chuỗi> ở <file>. Dùng nhanNguon() trong server/lib/nhan-nguon.js." Viết test đỏ trước (chạy trên 5942bf0 phải đỏ), xanh sau.
4. `npm run verify` trong apps/brand-health phải xanh (không giảm số test). In lại PDF 2 thương hiệu bằng scripts/in-bao-cao.js: số trang Full/Light không đổi.
5. Bằng chứng ở bang-chung/bhc-code-nhan-nguon/: chụp trên http://localhost:3020 (cấm file://) landing 2 thương hiệu màn đầu 1280×800 và 360×780, ảnh trang PDF có nguồn (Vinamilk trang 2 và trang có bảng nguyên văn, IF Agent trang có bảng 9 câu sai/nhầm), mỗi ảnh ≤ 600 KB. Log verify thô. Tắt server đúng PID.
6. Commit từng ý, push `agy/bhc-code-nhan-nguon`.
CẤM: deploy, gọi AI thật/khoá API, in khoá, gửi mail, sửa test cũ, sửa JSON trong bao-cao/bien-tap, đụng apps/event, apps/lab, packages/, push nhánh khác. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md ngắn: `dat: co|khong`; SHA đỉnh; test luật mới đỏ→xanh; verify pass/fail; số trang PDF trước/sau; danh sách ảnh.

## Lần trước trượt vì:
model: gemini-pro-orchestrator
phieu: bhc-code-nhan-nguon
may: may-2
trang_thai: loi
ly_do: qua_gio
tep_doi: KET-QUA.md
drive: (khong)
phut: 40.32
token: vao=0 ra=0

phát hiện bí mật: apps/event/test/e2e/platform.test.js:38, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:73, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:86, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:111, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:212, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:265, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:275, apps/lab/test/agentic-me-luot.test.js:126, apps/lab/test/agentic-me-noi-dung.test.js:71, apps/lab/test/agentic-me-su-kien.test.js:35, apps/lab/test/t148-quan-tri-chung.test.js:18, apps/lab/test/yen-lam-t101.test.js:13, apps/veew-booth/server/setup-kiosks.js:7

nhip: 00:17 3p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
