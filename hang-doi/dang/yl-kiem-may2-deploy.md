may: may-2
loai: khac
tran_phut: 15
nhan: may-2 2026-11-15T09:05:41+0700

Kiểm máy 2 đủ điều kiện deploy staging Yên Lam. Chỉ đọc, chạy tiền cảnh, không in nội dung bí mật.
1. `gcloud --version` (dòng đầu), `gcloud config get account`, `gcloud compute instances list --project=ifagent-event-2026` (ghi tên + STATUS).
2. `gcloud compute ssh ifagent-event --zone=asia-southeast1-b --project=ifagent-event-2026 --command "df -h / | tail -1; docker ps --format '{{.Names}}'"` (hỏi tạo khoá SSH thì đồng ý, không đặt passphrase). Chỉ GET/đọc, không sửa gì trên VM.
3. Có file `C:\linhx\_ENV\ifagent.env` không; nếu có, chỉ ghi DANH SÁCH TÊN biến (phần trước dấu =), KHÔNG ghi giá trị.
4. Có thư mục `C:\linhx\ifagent-nop\` không; nếu có, liệt kê cây 2 tầng (tên file, không đọc nội dung).
Trả lời KET-QUA.md: từng mục CÓ/KHÔNG + kết quả ngắn.
