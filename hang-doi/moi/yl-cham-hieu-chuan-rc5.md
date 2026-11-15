may: may-1
loai: code
model: gemini-pro-orchestrator
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
theo_doi: D:\linhx\cham-yl

Hiệu chuẩn AGY CHẤM ẢNH Yên Lam (độc lập: bạn KHÔNG phải thợ đã làm). Chỉ đọc, không sửa code, không deploy. Mọi lệnh tiền cảnh. Không dùng background task.
1. Clone thưa (ổ C máy 1 gần đầy, dùng D:): `git clone --filter=blob:none --no-checkout https://github.com/fyzdfyzd/ifagent D:\linhx\cham-yl`, rồi `git -C D:\linhx\cham-yl sparse-checkout set .handoff/yen-lam-dong-hanh/NOP ops/staging-rc5` và `git -C D:\linhx\cham-yl checkout origin/claude/nop-phat-hanh -- .handoff/yen-lam-dong-hanh/NOP` + `git -C D:\linhx\cham-yl checkout origin/claude/project-thread-4abpu3 -- ops/staging-rc5`.
2. Đọc NOP/**/CHUAN/RUBRIC.md, LOI-DA-BAT.md, CHUAN-9-DIEM-13-11.md, TIEU-CHUAN-NGHIEM-THU.md. KHÔNG đọc CHAM-RC5.md (đó là đáp án, chỉ dùng ở bước 4).
3. Chấm ảnh/video bằng chứng RC5 trong ops/staging-rc5 (kiosk "Nhắn Lam", trang BTC, bìa AGENTIC:ME) theo RUBRIC: mỗi phần một điểm 0–10 (điểm nhóm = tiêu chí thấp nhất), liệt kê lỗi thấy được, mỗi lỗi ghi tên ảnh + vùng (x,y,w,h). So ảnh với KHUNG/ khi có khung tương ứng. Ảnh tĩnh tối đa 8.
4. Sau khi ghi xong điểm của mình vào D:\linhx\cham-yl\CHAM-AGY-RC5.md, mới mở CHAM-RC5.md và lập bảng so: phần | điểm agy | điểm Claude | lệch; lỗi (a)–(e) kiosk: agy có bắt được không.
Không sửa điểm của mình sau khi xem đáp án.
Trả lời KET-QUA.md (ngắn): bảng so điểm, số lỗi kiosk bắt được /5, các lỗi agy thấy mà bài cũ không có, kết luận DÙNG ĐƯỢC nếu mọi phần lệch ≤ 0,5 và bắt ≥ 4/5 lỗi kiosk, ngược lại CHƯA.
