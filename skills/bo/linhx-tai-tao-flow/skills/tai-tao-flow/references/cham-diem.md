# Thang chấm

## Khả thi một claim (`kha_thi`)

| Điểm | Nghĩa |
|---|---|
| 3 | Có repo mở hoặc mảnh LINHX đã chạy làm đúng việc này |
| 2 | Ghép được từ mảnh có sẵn, chất lượng phụ thuộc thư viện/gu cần tự làm |
| 1 | Cần R&D thật, chưa thấy ai làm ổn |
| 0 | Không làm được như bài nói, hoặc chỉ là lời quảng cáo |

## Thổi phồng (`thoi_phong`)

| Điểm | Nghĩa |
|---|---|
| 0 | Nói đúng mức |
| 1 | Đúng trong điều kiện bài không nói ra (cần duyệt người, cần thư viện riêng) |
| 2 | Sai về số hoặc phạm vi ("10 giây", "nhiều bao nhiêu cũng được", "thay trọn vẹn") |

## Kinh doanh (nhìn từ phía LINHX), mỗi tiêu chí 0 đến 3

| Mã | Câu hỏi | 3 điểm khi |
|---|---|---|
| `nguoi_tra_tien` | Ai trả tiền, có rõ không? | Một nhóm khách cụ thể, đang tốn tiền cho việc này |
| `san_sang_tra` | Họ có đang trả cho cách cũ không? | Có giá tham chiếu đã kiểm |
| `canh_tranh` | Đồ miễn phí/rẻ thay thế được bao nhiêu? | Chưa có đồ thay thế tốt cho thị trường Việt |
| `loi_the_linh` | LINHX có gì người khác không có? | Mảnh đã chạy + quan hệ khách + nội dung Việt |
| `bien_loi_nhuan` | Mỗi đơn còn lại bao nhiêu sau token và giờ người? | Biên cao, giờ người thấp |
| `kenh` | Có sẵn kênh tới khách không? | Kênh của Linh đang có người |

## Kết luận (script tính)

- Khả thi TB = trung bình `kha_thi` các claim `chuc-nang`.
- Kinh doanh = tổng sáu tiêu chí, tối đa 18.
- **LÀM**: khả thi TB ≥ 2,2 và kinh doanh ≥ 12.
- **THỬ NHỎ**: khả thi TB ≥ 1,5 và kinh doanh ≥ 9. Làm một module rẻ nhất, bán thử cho 1 đến 3 khách.
- **CHỈ LƯU**: còn lại. Ghi vào memory, không dựng.
