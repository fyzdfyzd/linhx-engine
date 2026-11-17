may: may-3
loai: soi
tran_phut: 40
theo_doi: C:\linhx\tong-duyet\dt.log
nhan: may-3 2026-11-17T20:04:54+0700

Phiếu TỔNG DUYỆT LUỒNG 1 (điện thoại): trang chủ → đồng hành. Chỉ CHỤP và GHI, KHÔNG sửa code, KHÔNG deploy, KHÔNG gửi mail/Zalo. Mọi lệnh tiền cảnh, không background task. Commit + push sau mỗi mục.
Đích (Linh 20:12: soi trên yenlam.ifagent.net): https://yenlam.ifagent.net/yen-lam/ (prod). Playwright Chromium, devices['iPhone 13'] (390×844, DPR 3), locale vi-VN, cấp quyền micro/camera/notifications, cờ --use-fake-device-for-media-stream. Tên khách thử: "Test Claude".
Chụp VIEWPORT (không fullPage) ở MỖI trạng thái, đặt tên NN-mo-ta.png; trang dài thì chụp thêm 1 ảnh fullPage. Mỗi ảnh ghi 1 dòng vào BANG.md: tên ảnh | URL | nút đang thấy | lỗi console/HTTP≥400 | thời gian từ bấm tới khi xong (ms).
Đi lần lượt (context MỚI, chưa cookie):
1) /yen-lam/ trang chủ; bấm từng ô (Đồng hành, Lịch, Diễn giả, Hỏi Lam, Giới thiệu) chụp trang đích rồi quay lại.
2) Đồng hành lần đầu: màn đồng ý → mở "Xem chi tiết" → "Đồng ý và tiếp tục" → làm quen (nhập tên, trả lời đủ các câu) → màn Lam. Thử cả "Không đồng ý" và "Để sau" ở context riêng.
3) Tab Lam: gõ 3 câu "Lễ khai mạc mấy giờ?", "Track Lavender ở phòng nào?", "Bạn là đại sứ chính thức à?" — chụp sau mỗi câu, chép nguyên văn trả lời.
4) Tab Phiên: lịch, mở 1 phiên, lưu phiên, "Bật nhắc", đặt câu hỏi, bình luận, thông tin thực dụng.
5) Tab Diễn đàn: danh sách, mở 1 mục, đăng thử 1 bài "Test Claude - xin bỏ qua" (ghi id để BTC gỡ).
6) Tab Của tôi: QR, email (chỉ mở màn, KHÔNG gửi mã), Lam nhớ gì, tạp chí/bìa, gặp gỡ, quên tôi (chỉ mở màn, KHÔNG bấm xác nhận).
7) Tab Thêm: mọi mục.
8) Diễn giả: /yen-lam/dien-gia/ + 3 trang (nguyen-tran-quang, jiang-na, 1 người không ảnh) + /yen-lam/lich.
9) Bấm nút "Tiếng" (âm thanh) và nút micro "Chạm để nói" ở tab Lam: chụp trạng thái.
Nộp: ảnh + BANG.md vào repo linhx-engine nhánh soi-rc8-17-11, thư mục soi/tong-duyet/dt/ (push từng mục). KET-QUA ≤1500 ký tự: số ảnh, các bước KHÔNG đi được, mọi lỗi 4xx/5xx.

nhip: 20:13 9p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
