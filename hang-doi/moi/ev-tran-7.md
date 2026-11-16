may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
theo_doi: C:\linhx\ifagent-wt\ev-tran-7

Phiếu cụm event.ifagent.net (ev-tran-7): sửa lỗi Claude soi ảnh ev-chup-6 và khoá bằng test.
0. `git -C C:\linhx\ifagent fetch --all`. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\ev-tran-7 -b agy/ev-tran-7 origin/agy/ev-chup-6`. Trong apps/event: `npm ci`.
1. TEST KHOÁ trước (đỏ trước, xanh sau): thêm test/e2e/khong-tran-ngang.test.js: máy chủ test như scripts/web-chup.js, mở 18 trang trong bang-chung/ev-chup-6/kiem-trang.json ở bề rộng 360 và 1280, khẳng định `document.documentElement.scrollWidth <= window.innerWidth`. Thông báo lỗi phải nêu trang, bề rộng, số px tràn và phần tử rộng nhất (selector) để người sửa biết chỗ. Hiện / ở 360 tràn 20 px nên test phải ĐỎ.
2. Tìm phần tử gây tràn ở trang chủ 360 và sửa CSS (không dùng overflow-x:hidden trên body/html để che). Test xanh.
3. Chạy npm test + test mới + test/e2e/web-vo.test.js. Chụp lại 01-trang-chu ở 360 và 1280 vào bang-chung/ev-tran-7/.
4. Push agy/ev-tran-7.

LUẬT CHUNG cụm event: chạy mọi lệnh TIỀN CẢNH, không background task; chỉ sửa apps/event/ và bang-chung/ev-tran-7/; không đụng apps/lab, packages/, nhánh Yên Lam/brand; không deploy, không mail thật, không in khoá, không sửa/xoá test cũ, không sinh ảnh AI. Bộ quét bí mật runner báo nhầm dòng CŨ (apps/lab/..., platform.test.js:38, apps/veew-booth/..., infra/staging/stg-event/...): không sửa các tệp đó; phiếu sửa chỉ cần xác nhận `git diff origin/agy/ev-chup-6..HEAD` không có bí mật mới. KET-QUA ngắn: dat co/khong; SHA đỉnh; test mới đỏ→xanh; pass/fail npm test; phần tử gây tràn và cách sửa.
