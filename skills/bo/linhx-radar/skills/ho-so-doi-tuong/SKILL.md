---
name: ho-so-doi-tuong
description: Làm hồ sơ một doanh nghiệp hoặc KOL trong radar: họ đang nói gì, đã có gì, đau ở đâu, LINHX chia sẻ và bán được gì, cách tiếp cận, nháp lời mở. Dùng khi Linh hỏi "tìm hiểu brand X", "KOL Y là ai", "nên tiếp cận ai trước".
---

# Hồ sơ đối tượng

1. Lấy dòng có sẵn: đọc `output/csv/doanh-nghiep.csv` hoặc `kol.csv` (cộng đồng, vai trò, năm, điểm, gợi ý).
2. Nghiên cứu 90 ngày gần nhất (WebSearch + WebFetch): chiến dịch, phát ngôn, bài nói ở sự kiện, tuyển dụng (lộ nhu cầu), sản phẩm mới, khủng hoảng. Với KOL: bài nói, chủ đề hay viết, tổ chức đang làm.
3. Viết `output/ho-so/<slug>.md` gồm:
   - **Họ nói về gì** (3–5 ý, có link)
   - **Họ đã có gì** (công cụ, agency, đội AI, chương trình)
   - **Pain point suy ra** (ghi rõ "suy luận" nếu không có câu nói trực tiếp)
   - **LINHX chia sẻ gì trước** (miễn phí, tạo uy tín) và **dịch vụ agentic phù hợp** (lấy từ `config/offers.json`, chọn 1–2)
   - **Đường tiếp cận**: qua cộng đồng nào, sự kiện nào, người giới thiệu nào trong kho KOL
   - **Nháp lời mở** 80–120 chữ, giọng Linh, không bán ngay
4. Cập nhật giai đoạn nếu Linh đồng ý: `congdong.py mark dn|kol "<tên>" "đang tìm hiểu" "<ghi chú>"`.

Không gửi gì thay Linh. Không lưu thông tin liên lạc cá nhân không công khai.
