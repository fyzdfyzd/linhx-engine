phieu: yl-khoa-t1
may: claude
trang_thai: xong
dat: co

Claude rà T1 (agy/yl-test-t1 @200ee60e), 15/11 12:10 VN.
- Diff chỉ thêm apps/lab/test/nghiem-thu-rc6/* + bản chép NOP giống hệt claude/nop-phat-hanh. Không đụng code, không test cũ. ĐẠT.
- KHOÁ 01-a3-cach-ly (62 xanh: đợt B đã sửa, RC5 không ghi lỗi cách ly) và 02-a2-kiosk-nhan-lam (5 đỏ, đúng 5 lỗi RC5).
  Lưu ý: 02 dùng Gemini giả (40 ms) nên (a) ≤8 s thật phải đo ở ai-that/A6 trên staging; 02 gọi window.__kl.may.{hoiChu,tiengDau,clipHet,trangThai}, window.__kl.moChat → A2 phải giữ nguyên các móc này.
- CHƯA KHOÁ 03-a6-do-muc-9: (1) "lệch bố cục" đang so màu từng điểm ảnh với ảnh khung → 3,5–88%, không bao giờ đạt, sai ý "bố cục"; (2) đếm từ gộp cả màn, cần đối chiếu chữ đã duyệt CHU-TREN-MAN. Viết lại ở yl-test-a6-b.
- Huỷ yl-code-a3: nhóm (1) xanh hết, không còn gì để sửa.
