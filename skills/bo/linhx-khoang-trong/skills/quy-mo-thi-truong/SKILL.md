---
name: quy-mo-thi-truong
description: B4 radar khoảng trống. Ước quy mô thị trường của mỗi cụm nhu cầu ở nguồn (tổng người theo, số kênh trả phí, tăng trưởng 4 tuần) và tính điểm cầu nguồn. Dùng sau B3 của LAB029.
---

# B4. Thị trường chủ đề có đủ lớn không

1. `python gapscan.py quy-mo` → `04-quy-mo.json`: số kênh, tổng người theo (số Substack công khai là số làm tròn), số kênh trả phí và bậc ("Thousands of paid subscribers"...), tăng trưởng số bài 28 ngày so với 28 ngày trước, `cau_nguon` 0 đến 1.
2. Đọc và bổ sung bằng tín hiệu ngoài nếu cần, ghi vào `04-quy-mo-ghi-chu.md` có link: sách bán chạy cùng chủ đề (Amazon, Goodreads), podcast top, Google Trends, khoá học lớn.
3. Cảnh báo khi đọc số:
   - Mẫu chỉ có bài mới quét thì tăng trưởng 28 ngày bị thổi phồng; ghi rõ khi phần lớn bài nằm trong 28 ngày gần nhất.
   - Một kênh rất lớn có thể kéo cả cụm; xem `top_kenh` trước khi kết luận.
4. `python gapscan.py kiem b4`.

Công thức `cau_nguon` (v0.1, cần hiệu chỉnh sau 3 lượt thật) nằm trong `references/cong-thuc.md`.
