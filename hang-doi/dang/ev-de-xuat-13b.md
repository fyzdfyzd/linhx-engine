may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
phu_thuoc: ev-anh-ly-12b
theo_doi: C:\linhx\ifagent-wt\ev-de-xuat-13b
nhan: may-2 2026-11-17T19:26:22+0700

Phiếu ev-de-xuat-13b (vòng 4): gắn 2 ảnh ly cà phê Gemini vào bộ slide đề xuất mẫu và sửa chữ "AI" rơi dòng. COMMIT + PUSH SAU MỖI Ý.
0. `git -C C:\linhx\ifagent fetch --all`. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\ev-de-xuat-13b -b agy/ev-de-xuat-13b origin/agy/ev-de-xuat-11`. Trong apps/event: `npm ci`. Lấy 2 ảnh từ nhánh hang-doi của linhx-engine: `xong/ev-anh-ly-12b/ly-ngang.*` và `ly-vuong.*` (nếu KET-QUA ev-anh-ly-12b ghi KHONG_THAY hoặc SAI_MAY thì bỏ ý 1, làm ý 2–3, ghi rõ).
1. Chép ảnh vào `apps/event/public/web/anh/ds/` thành `ly-ca-phe-ngang.webp` và `ly-ca-phe-vuong.webp` (đổi sang webp chất lượng 82 bằng sharp đã có trong node_modules, KHÔNG cắt, giữ tỉ lệ gốc; mỗi tệp ≤ 400 KB). Slide 1 (bìa) dùng ảnh ngang; slide 3 (ý tưởng) dùng ảnh vuông; object-fit cover nhưng ảnh phải hiển thị đúng tỉ lệ khung chứa (khung slide 3 vuông). Thêm ca test trong de-xuat-slide.test.js: src slide 1 chứa `ly-ca-phe-ngang`, src slide 3 chứa `ly-ca-phe-vuong`, cả hai tải được (naturalWidth > 0).
2. Slide 7: chữ "AI" đang rơi xuống dòng riêng. Sửa bằng `text-wrap: balance` cho tiêu đề/tên chỉ số trên mọi slide và nối từ cuối bằng khoảng trắng không ngắt khi cần. Thêm ca test KHOÁ cho cả 8 slide (ở 1920×1080 và PDF): với mọi khối chữ có ≥ 3 từ, dòng cuối không được chỉ có 1 từ (đo bằng Range.getClientRects từng từ). Thông báo lỗi: "Slide N: từ '<từ>' bị rơi dòng một mình — dùng text-wrap: balance hoặc &nbsp; trước từ cuối".
3. Chạy từng tệp test tiền cảnh: de-xuat-slide, xuong-ev4, xuong-pdf-mail, khong-tran-ngang, giao-dien-sang; npm test sau cùng. Bằng chứng bang-chung/ev-de-xuat-13b/: slide-1..8, pdf-1..8 (1920×1080), TONG-SLIDE.png. Push agy/ev-de-xuat-13b.

LUẬT CHUNG cụm event: chạy TIỀN CẢNH, không background task; chỉ sửa apps/event/ và bang-chung/ev-de-xuat-13b/; không đụng apps/lab, packages/, bang-chung cụm khác, nhánh Yên Lam/brand; không deploy, không mail thật, không in khoá, không sửa/xoá test cũ (chỉ thêm ca mới), không sinh ảnh AI, không gọi AI thật, không viết chữ mới. Bộ quét bí mật runner báo nhầm dòng CŨ: không sửa các tệp đó; chỉ xác nhận `git diff origin/agy/ev-de-xuat-11..HEAD` không có bí mật mới. KET-QUA ngắn: dat co/khong; SHA; test đỏ→xanh; pass/fail; TONG-SLIDE.png.

nhip: 19:32 6p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
