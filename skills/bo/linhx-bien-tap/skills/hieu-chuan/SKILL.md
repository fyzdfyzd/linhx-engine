---
name: hieu-chuan
description: Kiểm giám khảo chấm từng câu có phân biệt được bản đã sửa của người thật với bản máy hay không, trên một cặp bài mẫu, trước khi tin điểm của họ. Dùng khi đổi mô hình giám khảo, đổi hồ sơ biên tập viên, hoặc thêm bài mẫu mới.
---

# Hiệu chuẩn giám khảo

## Đầu vào
Một cặp trong `mau-sua/`: bản trước (máy hoặc cộng tác viên viết) và bản sau (người thật sửa).

## Cách làm
1. Cắt khoảng 600 từ đầu của mỗi bản, cùng phần nội dung, tách câu:
   `python ${CLAUDE_PLUGIN_ROOT}/scripts/cham_cau.py truoc.md --xuat-cau x.txt` (tương tự cho `sau.md`), rồi cắt theo số từ.
2. Đặt tên mù `ban-X.txt`, `ban-Y.txt` (thứ tự ngẫu nhiên), ghi khoá vào `.khoa.txt`.
3. Hai giám khảo mới (`references/giam-khao-tung-cau.md`), một người đọc X trước, một người đọc Y trước. Cấm mở file khoá.
4. So: bản người sửa phải có tỉ lệ GIỮ cao hơn rõ (ít nhất gấp ba) và tỉ lệ CẮT thấp hơn rõ ở cả hai giám khảo, và cả hai phải chọn đúng bản gần giọng mẫu hơn.

## Kết quả lưu
`ho-so-bien-tap/<ten>/HIEU-CHUAN.md`: ngày, mô hình giám khảo, cặp bài, bảng GIỮ/ỔN/SỬA/CẮT từng bản, kết luận đạt hay không. Từ kết quả này chỉnh ngưỡng trong `scripts/tong_hop_cham.py` nếu cần: ngưỡng GIỮ nên thấp hơn tỉ lệ GIỮ mà bản người sửa đạt được.

## Kết quả đã có
Chưa có lượt hiệu chuẩn hợp lệ. Lượt 19/10/2026 dùng bài chưa đăng báo nên đã bỏ; lượt kế dùng một bài Linh đã đăng (bản đăng) đối với bản máy viết cùng đề. Đến lúc đó ngưỡng GIỮ ≥25%, CẮT 0, SỬA ≤10% chỉ là tạm.
