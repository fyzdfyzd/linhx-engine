# Chọn công cụ và máy (luật 6)

## 1. Thứ tự rẻ trước

| Việc | Mặc định | Khi nào đổi | Ghi gì |
|---|---|---|---|
| Nghiên cứu rộng, nhiều nguồn | Gemini Deep Research, tài khoản Ultra | Câu hỏi hẹp, đã biết nguồn | `ly_do_cong_cu` |
| Lấy toàn văn từ danh sách link | LINHX crawler (0 token) | Vài trang lẻ: tải tay hoặc agy | `ly_do_cong_cu` |
| Bài Medium, Substack, web cần đăng nhập | skill `linhx-toan-van` (extension LINHX_CRAWLER trong Chrome đã đăng nhập) | | |
| Việc tay: viết, tổng hợp, dựng, code | agy, mỗi phiếu ≤40 phút, phiên mới | | mã phiếu trong commit |
| Ra đề, chấm, phản biện | Claude | | |
| Cần gấp, vài câu | Claude tìm web | | ghi "gấp" |
| Ảnh | ChatGPT Plus và Gemini Ultra qua Chrome | | |

Claude không làm thợ khi có agy. Lý do: tiết kiệm token và tách người làm với người chấm.

## 2. Máy nào làm gì (luôn ghi rõ máy khi nhờ Linh duyệt)

| Máy | Là gì | Dùng cho |
|---|---|---|
| **Máy công ty** DESKTOP-PVHR2CD | luôn bật | **mọi việc cần trình duyệt**: Gemini Deep Research, ChatGPT, Behance/Dribbble/Pinterest, Gmail |
| **MSI** | máy cá nhân | agy, crawler, file trong `D:\LINHX\LAB` |
| Cloud | phiên Claude | viết đề, chấm, script, test |

Luật 30/10: việc cần trình duyệt luôn dùng Chrome máy công ty, không dùng MSI.

## 3. Gemini Deep Research (cách chạy)

1. Chrome máy công ty, tab mới, chọn đúng tài khoản Ultra (xem `/u/<số>` trên URL). Hết hạn mức thì báo Linh đổi tài khoản, không ngồi chờ.
2. Bật Deep Research, dán đề. Đề gồm: câu hỏi, phạm vi (nước, năm), loại nguồn ưu tiên, yêu cầu **trả link cho mọi số**, định dạng bảng.
3. Duyệt kế hoạch nghiên cứu Gemini đưa ra, rồi chạy (thường 5–10 phút).
4. Xuất toàn văn về `bang-chung/gemini-dr-<chu-de>-<ngay>.md`. Không tóm tắt trước khi lưu.
5. Kiểm link sống trên máy có mạng thật. Ghi số link sống / tổng.
6. agy tổng hợp từ file nguyên văn, gắn `[BC-xxx]`.

## 4. Crawler

- LINHX Crawler server `http://localhost:8000` tại `D:\LINHX_CRAWLER` (`/health`, `/crawl`, `/batch`, `/sitemap`). Khởi động: `python -m uvicorn main:app --port 8000`.
- Máy quét LINHX (repo `fyzdfyzd/mayquet`, máy công ty `D:\LINHX\CRAWLER`): gom crawler, CafeBiz, Medium, vault.
- Kết quả lưu nguyên văn, mỗi bài một file, có URL và ngày quét ở đầu file.

## 5. Ghi lại

Mỗi lần dùng công cụ khác mặc định, ghi một dòng trong phiếu hoặc STATUS: công cụ, vì sao, kết quả. Lần sau đọc lại để chọn đúng.
