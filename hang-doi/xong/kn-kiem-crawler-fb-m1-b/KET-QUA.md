model: gemini-4-hydrogen-low
phieu: kn-kiem-crawler-fb-m1-b
may: may-1
trang_thai: xong
tep_doi: (khong)
drive: (khong)
phut: 2.63
token: vao=65971 ra=4473

I'm running `orchestrator.crawl` on `https://www.facebook.com/VnExpress` to see how `LINHX_CRAWLER` handles it and will check the output once it finishes.
**Trạng thái:** `CHUA_DANG_NHAP`

- **Endpoint / Engine:** `POST /api/crawl` ([routes.py](file:///D:/LINHX_CRAWLER/server/api/routes.py#L90-L106)) và `FacebookExtensionEngine` ([facebook.py](file:///D:/LINHX_CRAWLER/server/engines/social/facebook.py#L15-L39), đẩy task vào hàng đợi cho Chrome Extension worker).
- **Số bài:** 0 bài.
- **Thời gian:** ~5s (`t2_crawl4ai`: 4.90s, `t4_playwright` fallback).
- **Lỗi:** `t1_httpx` trả `400 Bad Request`; `t2_crawl4ai` và `t4_playwright` đều fail quality gate (`too_short, low_quality_score`, `len: 267`) do Facebook chặn/yêu cầu đăng nhập và chưa có Chrome Extension worker đã đăng nhập Facebook đang chạy.

`CAN-LINH: Đăng nhập tài khoản Facebook vào trình duyệt Chrome có cài extension LINHX_CRAWLER (hoặc nạp cookie/phiên đăng nhập Facebook cho crawler) để extension worker quét được trang công khai https://www.facebook.com/VnExpress; LENH: `
