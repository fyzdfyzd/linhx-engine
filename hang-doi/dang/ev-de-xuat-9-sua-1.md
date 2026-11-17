may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
theo_doi: C:\linhx\ifagent-wt\ev-de-xuat-9
nhan: may-2 2026-11-17T08:25:45+0700
moc: 2396c241922c6c3c637641b2f6571b14fe491b43

Phiếu sửa ev-de-xuat-9 (lượt trước quá 40 phút, CHƯA push). Làm tiếp trong worktree CÓ SẴN C:\linhx\ifagent-wt\ev-de-xuat-9 (nhánh agy/ev-de-xuat-9), KHÔNG tạo worktree mới, KHÔNG làm lại từ đầu.
1. NGAY ĐẦU: `git add -A` phần đã làm trong apps/event và bang-chung/ev-de-xuat-9, commit "ev-de-xuat-9: slide (dở)", `git push -u origin agy/ev-de-xuat-9`. Mỗi bước sau xong là commit + push ngay.
2. Đọc lại đề gốc ở cuối tệp này (mục 2–4 của ev-de-xuat-9) và làm nốt phần còn thiếu. Lượt trước đã sửa test cũ xuong-pdf-mail.test.js và xuong-ev4.test.js: chỉ được giữ thay đổi ở đúng dòng kiểm số trang/khổ PDF (vì PDF nay là 8 trang ngang); mọi thay đổi khác trong 2 tệp đó phải hoàn lại. Ghi rõ từng dòng đã đổi vào KET-QUA.
3. Chạy test TỪNG TỆP ở tiền cảnh: de-xuat-slide, xuong-ev4, xuong-pdf-mail, khong-tran-ngang; npm test chạy sau cùng. Không chạy cả bộ e2e.
4. Bằng chứng: bang-chung/ev-de-xuat-9/sau/ slide-1..8 (1920×1080 PNG ≤ 600 KB) từ web, pdf-1..8 PNG từ PDF, TONG-SLIDE.png (lưới 2×4), 3 ảnh 360. Commit + push.

Đề gốc mục 2 (tóm tắt): 8 slide 16:9 dùng chung web /de-xuat/<mã> và PDF: 1 Bìa ảnh tràn khung + tên khách lớn; 2 câu trích lớn; 3 ý tưởng ảnh ≥ 55%; 4 hành trình 4 bước số lớn; 5 giải pháp thẻ; 6 lịch ngang không gãy chữ; 7 ba chỉ số chữ lớn; 8 bước tiếp + lienhe@ifagent.net + QR. Chỉ dùng chữ có sẵn; font Be Vietnam Pro/Montserrat nhúng; bảng màu web.css; lề 96 px; test khoá de-xuat-slide.test.js (8 slide 16:9, không tràn, chữ ≥ 22 px ở 1920, ≤ 40 chữ/slide, ảnh bìa ≥ 60%, PDF 8 trang ngang có font nhúng).

LUẬT CHUNG cụm event: chạy mọi lệnh TIỀN CẢNH, không background task; chỉ sửa apps/event/ và bang-chung/ev-de-xuat-9/; không đụng apps/lab, packages/, bang-chung của cụm khác, nhánh Yên Lam/brand; không deploy, không mail thật, không in khoá, không sinh ảnh AI, không gọi AI thật. Bộ quét bí mật runner báo nhầm dòng CŨ (apps/lab/..., platform.test.js:38, apps/veew-booth/..., infra/staging/stg-event/...): không sửa các tệp đó; chỉ xác nhận `git diff origin/agy/ev-sang-8..HEAD` không có bí mật mới. KET-QUA ngắn: dat co/khong; SHA đỉnh; test mới; pass/fail; đường dẫn TONG-SLIDE.png.

nhip: 08:35 15p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
