may: may-3
loai: khac
tran_phut: 15
theo_doi: D:\linhx\nhat-ky\may3-so-phieu-5

Linh 18/11 04:28 hỏi: máy 3 lên 5 phiếu song song được không. Chạy lệnh tiền cảnh, KHÔNG background task. Ghi mỗi bước 1 dòng vào `D:\linhx\nhat-ky\may3-so-phieu-5\tien-do.log`.
1. Đo (PowerShell): CPU (tên, số nhân, số luồng), RAM tổng, RAM trống NGAY LÚC NÀY (đang có phiếu chạy), ổ D: còn trống, số tiến trình node/agy đang chạy và RAM mỗi tiến trình agy + node (Get-Process | sort WS).
2. Đọc `runner\tho.env` trong thư mục hàng đợi máy này: giá trị LINHX_SO_PHIEU và LINHX_RAM_TOI_THIEU_GB hiện tại (không in AGY_ARGS hay bất kỳ khoá nào).
3. Tính N = min(5, floor((RAM tổng GB − 6) / 5), floor(số luồng / 3)). Ước mỗi phiếu code ~5 GB (agy + node test + Playwright).
4. Nếu N > giá trị hiện tại: sửa ĐÚNG MỘT dòng `LINHX_SO_PHIEU=<N>` trong tho.env (UTF-8 không BOM, giữ nguyên các dòng khác), đặt thêm `LINHX_RAM_TOI_THIEU_GB=3` nếu đang thấp hơn 3. KHÔNG khởi động lại runner, KHÔNG dừng phiếu đang chạy (runner đọc tho.env mỗi phút). Nếu N ≤ hiện tại thì không sửa.
5. Đợi 2 phút, đọc `runner\tho.log` dòng cuối xem runner đã nhận số mới chưa.
KET-QUA.md ≤ 800 ký tự: CPU, luồng, RAM tổng/trống, RAM mỗi phiếu đo được, số phiếu cũ → mới, có sửa hay không, lý do.
