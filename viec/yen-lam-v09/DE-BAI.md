# Yên Lam v0.9: đổi luồng, giữ giao diện (đêm 17/11 → sáng 18/11)

Nguồn chốt: Linh 22:27–22:51 17/11. Bản luồng đầy đủ: `LUONG-V09.html` (mở bằng trình duyệt, có sơ đồ). Ảnh khung: `khung/*.jpg`.

## Luật chung cho mọi phiếu yl09-*
1. Nền: repo ifagent, nhánh `yl-full-17-11` tại `6291514e` (đang ở staging). Mỗi phiếu tạo nhánh `agy/yl09-<ma>` từ nền hoặc từ nhánh phiếu phụ thuộc. Chỉ push nhánh đó.
2. **GIỮ NGUYÊN CSS kính, màu, phông đang có trong app.** Khung chỉ là bố cục và luồng. Màn mới dùng lại class kính sẵn có. Không thêm bảng màu mới.
3. Không gỡ cờ `thu_nghiem` (tối ưu Lam, ngắt mạng). Không sửa `infra/`, compose, env prod.
4. Không sửa test khoá cũ (`apps/lab/test/nghiem-thu-*`). Test mới để ngoài các thư mục đó. Không skip test.
5. CẤM: deploy staging/prod (trừ phiếu yl09-gop được deploy staging), gửi mail, in khoá/mật khẩu, xoá dữ liệu, AI sinh mặt người. Mọi lệnh chạy TIỀN CẢNH, không background task. Commit + push sau mỗi ý.
6. Prompt Lam theo `PROMPT-CHUAN` mục A: vai "Lam, trợ lý AI của VSMCamp & CSMOSummit 2026", không "đại sứ", không bịa giờ/phòng/diễn giả.
7. **Duyệt bằng mắt trên pixel**: mỗi màn đụng tới chụp Playwright đúng 390×844 (điện thoại, deviceScaleFactor 2) hoặc 1080×1920 (kiosk), ghép cạnh khung tương ứng thành `ghep-<man>.png`. Tự soi ở 100%: chữ tràn, chồng lớp, chữ mờ trên nền, nút < 44px, ảnh vỡ. Có lỗi thì sửa rồi chụp lại. Ghi điểm tự chấm 1–10 mỗi màn, < 8 là chưa xong.
8. Dữ liệu thật: `apps/lab/agenda/chuan/agenda.json` (41 phiên, 4 track, chiều 19/11 có 3 track chạy cùng giờ), `dien-gia.json` (48 người, ảnh thật mới 6). Thiết kế phải chịu được 48 diễn giả và vài trăm ảnh.
9. KET-QUA.md ≤ 2000 ký tự: dòng đầu `dat: co|khong`, SHA đỉnh, test trước/sau, danh sách ảnh ghép + điểm tự chấm, việc còn thiếu.

## Luồng chốt
**Kiosk (1 trang):** Chờ → K1 trò chuyện (giọng, widget tối đa 3) → K2 nhận ra khách (nhận mặt bằng đặc trưng nạp sẵn của khách ĐÃ đồng ý sinh trắc; QR dự phòng) → chào tên + phiên đã lưu → về K1. Nhánh chụp: nút "Chụp bìa cùng Lam" → màn đồng ý (2 nút lớn, "ảnh chỉ làm bìa, xoá sau 30 ngày") → 3-2-1 → lỗi mặt/xa thì "Lại gần chút nhé" chụp lại → K3b chờ bìa: chọn 1 trong 4 track (không bắt chọn diễn giả), Lam vẫn nói → K4 bìa + QR (quét mở thẳng tab Của tôi) → 60s về chờ. 90s im lặng về chờ. Mất mạng: Lam xin lỗi, còn widget tĩnh. Giữ logo Le Bros.
**Đồng hành (`/yen-lam/` = trang chủ):** 5 lối vào (Zalo/email, QR standee, QR bìa kiosk, link bìa /b/:mã, quay lại) đáp cùng một chỗ. Không màn đồng ý đầu; xin quyền đúng lúc (nhắc khi lưu, email khi nhận tạp chí, sinh trắc khi bật nhận mặt). 4 tab cố định Lam · Lịch · Bảng tin · Của tôi; trang con có nút quay lại, không mở tab mới.
- Lam: chat giọng + chữ, 10 lượt, làm quen trong chat (tên, track), Lam trả widget trong chat (thẻ phiên có nút Lưu, thẻ diễn giả, dải ảnh có bạn, QR) do công cụ trả từ dữ liệu BTC.
- Lịch: đoạn Phiên / Diễn giả / Đã lưu; ngày; track có đếm; tìm; nhóm theo khung giờ, phiên song song vuốt ngang; tự cuộn "Đang diễn ra". Trang phiên: lưu + nhắc, .ics, câu hỏi bình chọn, thảo luận.
- Bảng tin: thông báo BTC ghim, lọc Tất cả/Có bạn/Ảnh BTC/Bìa/Khách, lưới 3 cột tải 30 ảnh/lần, ảnh nhỏ webp.
- Của tôi: bìa (lưu, chia sẻ), Tạo tạp chí, Mã QR, Ảnh có tôi, Gặp gỡ (hai bên đồng ý), Đã lưu, hồ sơ (avatar, nghề), email, Lam nhớ gì, Quên tôi.
- Tạp chí (module riêng, kiosk không nạp): 3 câu (track, diễn giả nhớ nhất: gợi ý từ phiên đã lưu + ô tìm 48 người, điều mang về) → có tạp chí xem ngay 8 trang → tối 20/11 tự cập nhật thêm phiên/ảnh, email + PDF A5.
**Admin (1 màn):** Cần duyệt (ảnh/câu hỏi, chọn nhiều, duyệt một lần, nhãn cờ) · Kiosk & widget (trạng thái từng máy, bật tắt widget từng máy, kiosk đổi ≤10s) · Gửi thông báo (điện thoại + kiosk, hẹn giờ) · Hôm nay (số liệu). Các tab cũ vào "Nâng cao".
