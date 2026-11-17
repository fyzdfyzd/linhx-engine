may: may-3
loai: soi
tran_phut: 40
theo_doi: C:\linhx\tong-duyet\kiosk.log
nhan: may-3 2026-11-17T20:44:57+0700

Phiếu TỔNG DUYỆT LUỒNG 2: kiosk chào + trò chuyện Lam + chụp bìa. Chỉ CHỤP và GHI, KHÔNG sửa code, KHÔNG deploy. Mọi lệnh tiền cảnh, không background task. Commit + push sau mỗi mục.
Đích (Linh 20:12: soi trên yenlam.ifagent.net): https://yenlam.ifagent.net/yen-lam/csmo/kiosk-lam (Lam trò chuyện) và màn booth AGENTIC:ME (/yen-lam/agentic-me-v5/kiosk hoặc đường kiosk BTC đang dùng: lấy từ trang chủ chân "Dành cho BTC" hoặc admin #cau-hinh). Kiosk đang MỞ TỰ DO (17/11), không cần mã; nếu bị khoá thì ghi lại, KHÔNG tự cấp mã.
Playwright Chromium, viewport 1080×1920 DPR 1, cờ --use-fake-ui-for-media-stream --use-fake-device-for-media-stream --use-file-for-fake-video-capture=<ảnh chân dung y4m/mjpeg của Linh hoặc ảnh mẫu tinh/mau/a1.jpg chuyển y4m>. Chụp VIEWPORT ở MỖI trạng thái (NN-mo-ta.png) + BANG.md: tên ảnh | URL | nút đang thấy | lỗi console/HTTP≥400/WS đóng | thời gian (ms).
Đi lần lượt:
1) Màn chờ kiosk (chụp 3 lần cách 5s để thấy clip đổi).
2) Chạm bắt đầu → Lam chào (chụp khi Lam nói) → hỏi bằng chữ (nếu có ô) 3 câu như phiếu dt → chụp.
3) Từ kiosk Lam, tìm đường sang chụp bìa: ghi rõ có nút chuyển thẳng không hay phải đổi màn/đổi máy. Chụp.
4) Booth: đồng ý ảnh → chụp ảnh (webcam giả) → kiểm ảnh → nhập tên/nghề → chọn diễn giả/track → chờ tạo bìa (ghi thời gian) → bìa + QR → quét QR (mở URL QR ở context iPhone 13, chụp trang khách nhận được).
5) Trên trang khách: có nút chia sẻ mạng xã hội không (Facebook/Zalo/tải ảnh)? Chụp. Nhánh "lên tạp chí" nằm ở đâu, chụp.
6) Lỗi: ảnh không mặt (chụp vật), 2 mặt; bấm "Làm lại"; để yên 60s xem kiosk có tự về màn chờ không.
Nộp: ảnh + BANG.md vào linhx-engine nhánh soi-rc8-17-11, thư mục soi/tong-duyet/kiosk/. KET-QUA ≤1500 ký tự: số ảnh, bước không đi được, lỗi, thời gian tạo bìa.

nhip: 21:15 30p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
