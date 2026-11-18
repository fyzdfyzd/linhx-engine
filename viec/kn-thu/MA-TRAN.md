# Ma trận kỹ năng agy (Claude ghi, cập nhật khi phiếu xong)

| Kỹ năng | Máy 1 PVHR2CD | Máy 3 2AUT482 | MSI (may-4) |
|---|---|---|---|
| Điều khiển Chrome + kiểm đăng nhập | ĐẠT Browsentic (sửa 18/11) | ĐẠT Browsentic (cài 18/11) | ĐẠT Browsentic, 6/6 đã đăng nhập |
| Ảnh Gemini | – | – | ĐẠT lượt 2: 1024×1024, Nano Banana 2 Lite (/u/1) |
| Nhạc Gemini | – | – | ĐẠT mp3 62 giây (/u/1); chưa chép Drive vì G: chưa gắn |
| Nhạc Suno | – | – | ĐẠT mp3 184 giây, còn 730 tín dụng |
| Video Google Flow | – | – | ĐẠT lượt 2: Veo 3.1 Lite, 7,9 giây, 10 tín dụng |
| Deep Research ChatGPT Plus | HỎNG lượt 3: Browsentic chạy, nhưng hết trần 25 phút; lượt 4 trần 40 | – | – |
| Google Colab | huỷ theo phiếu trước; lượt 4 chạy độc lập | – | – |
| Đổi tài khoản | huỷ theo phiếu trước; lượt 4 chạy độc lập | – | – |
| Gemini Task: tính toán + mạng | – | ĐẠT: đúng 2 đáp án + PNG; máy ảo KHÔNG có mạng | – |
| Gemini Task: video | – | ĐẠT: MP4 1080×1920 20 giây, nhạc sin, chữ Việt đủ dấu | – |
| Gemini Task: xlsx, pip, PDF | – | ĐẠT 2/2: xlsx 3 sheet có SUM; pip lỗi (không mạng) nhưng tự tính Mặt Trời 280,37° đúng | – |
| Crawler quét web | ĐẠT: POST /crawl, vnexpress 1,9 giây, 1.340 ký tự (cổng 8000 bị Frappe chiếm, chạy 8011) | – | – |
| Crawler quét Facebook | CHƯA ĐĂNG NHẬP: cần Chrome có extension LINHX Crawler đăng nhập Facebook | – | – |

Vòng 2: kỹ năng ĐẠT ở một máy thì thử lại trên máy còn lại. Máy 2 không thử (đang chạy Yên Lam).

## Luật rút ra
- Việc cần đăng nhập chỉ dùng Browsentic; hồ sơ Chrome riêng không mang đăng nhập.
- Khai MCP cho agy: UTF-8 không BOM; kiểm `agy mcp list` + `browsentic status` trước phiếu trình duyệt.
- Daemon Browsentic cũ có thể giữ cổng 8765: tắt rồi `browsentic start`.
- Không nối phu_thuoc giữa các kỹ năng độc lập (một phiếu hỏng kéo huỷ cả chuỗi).
- Deep Research cần trần 40 phút.
- Máy ảo Gemini Task không có mạng: không pip, không tải web.
- Máy 1: cổng 8000 là Frappe; crawler chạy cổng khác.
