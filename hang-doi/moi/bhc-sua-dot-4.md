may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 50
khong_tien_phut: 20
theo_doi: C:\linhx\ifagent-wt\bhc-sua-4

Lưu ý máy: KHÔNG background task/subagent; tiền cảnh; KHÔNG chờ/ngủ; `npm.cmd`/`npx.cmd`. Commit đầu trong 5 phút, push mỗi bước.
Đợt 4 (lên 9). Worktree C:\linhx\ifagent-wt\bhc-sua-4, nhánh agy/bhc-sua-4 từ origin/agy/bhc-sua-3 (0d979a3). Đọc bang-chung/bhc-e2e-lan-2/loi.md trên origin/agy/bhc-e2e-lan-2. CHỈ apps/brand-health. Không gọi AI thật.
1. LOI-K8: form trang chủ dùng novalidate + kiểm bằng JS, câu tiếng Việt dưới ô: tên trống hoặc toàn khoảng trắng ("Bạn nhập tên thương hiệu giúp nhé"), website sai dạng ("Website chưa đúng dạng, ví dụ vinamilk.com.vn") ngay ở trang chủ, không sang màn B; KHÔNG bao giờ rơi về mặc định Vinamilk. Server cũng từ chối tên toàn khoảng trắng.
2. PDF: khi lượt quét xong, dựng sẵn PDF Light + Full ở hàng đợi nền của server (một luồng, không chặn) để lần tải đầu < 2 giây; trang chờ hiện có sẵn giữ nguyên làm dự phòng.
3. Câu mở đầu báo cáo tự quét: bỏ khung "Đúng là: ..." vụng; dạng: dòng lớn = điều AI nói (trích ngắn), dòng phụ = "Sự thật: ..." theo bảng sự thật; với AI giả cũng phải đọc tự nhiên. Không đổi bố cục.
4. Chi tiết lượt quản trị: gom 4 nút đầu trang (Chấm lại, Quét lại, Xuất bản, Ẩn) — Xuất bản/Ẩn thành một nút bật tắt; 360: thẻ lượt quét chỉ giữ một nút chính "Mở chi tiết", "Mở báo cáo" + "Sao chép mã" vào dòng phụ.
Test khoá cho 1, 2 (thời gian tải lần đầu sau khi quét xong < 2s với AI giả), 3 (không có chuỗi "Đúng là:"). Chạy lại e2e-giao-dien K1–K9 và Q4 một lần, ảnh 1280/360 vào bang-chung/bhc-sua-4/. verify + test:lap xanh. Push agy/bhc-sua-4.
