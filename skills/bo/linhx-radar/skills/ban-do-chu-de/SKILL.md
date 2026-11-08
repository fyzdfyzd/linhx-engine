---
name: ban-do-chu-de
description: Tổng hợp định kỳ (tháng, quý) từ các sự kiện đã index và hấp thu: mọi người đang nói gì, ai nói hay, pain point lặp lại, solution mới, khoảng trống chưa ai nói, và nên đi event nào tiếp theo. Dùng khi Linh hỏi "thị trường đang nói gì", "insight từ các event", "báo cáo tháng sự kiện".
---

# Bản đồ chủ đề sự kiện

1. Chạy `eventscan.py insight --days 90` (hoặc 30) rồi đọc `output/BAN-DO-CHU-DE.md` và `output/su-kien.csv`.
2. Bổ sung lớp "đang nói gì" cho sự kiện chưa hấp thu: lấy chủ đề và tiêu đề phiên trên lịch (cột `chu_de`) của các sự kiện đã diễn ra trong kỳ; với 3 đến 5 sự kiện lớn nhất chưa hấp thu, tìm bài tường thuật và chạy nhanh `hap-thu-su-kien` (chỉ phần insight).
3. Viết `output/ban-do/BAN-DO-<yyyy-mm>.md`, tối đa 2 trang:
   - **Đang nói gì**: 5 chủ đề nóng nhất, mỗi chủ đề kèm số sự kiện và ví dụ.
   - **Pain point lặp lại**: nhóm xuất hiện ở ≥2 sự kiện; nói bằng lời người đau.
   - **Solution mới**: ý `solution` có lần đầu trong kỳ; ai đưa ra; đã có ai làm ở VN chưa.
   - **Ai hay**: 5 diễn giả điểm cao, họ hay nói gì, nên theo dõi kênh nào.
   - **Ai tài trợ**: đơn vị chi tiền nhiều sự kiện nhất (tín hiệu ngân sách thị trường).
   - **Khoảng trống**: pain point nhiều nhưng ít solution; đó là chủ đề Linh có thể nói, viết, hoặc làm offer agentic.
   - **Kỳ tới nên đi**: 3 sự kiện từ `LICH-SU-KIEN.md` khớp với khoảng trống.
4. Báo Linh 5 dòng; đính kèm file. Mọi con số dẫn từ CSDL, không phỏng đoán; chỗ dữ liệu mỏng (dưới 5 sự kiện đã hấp thu) thì nói rõ là tín hiệu yếu.
