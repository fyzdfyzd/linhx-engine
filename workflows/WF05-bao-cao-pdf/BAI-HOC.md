# Bài học WF05

Mỗi vòng ghi lỗi gặp và luật rút ra. Luật có ≥ 2 bằng chứng thì sửa vào skill.

## Vòng thử 9/11 (cloud): báo cáo "AI trong nghiên cứu" từ LAB085 (Linh + anh Dũng)
Thư mục: `vong-1-thu/ai-trong-nghien-cuu/`. Chạy trọn bước 1–11 trên Linux, Typst 0.13.1.

| # | Lỗi gặp | Ở đâu | Luật rút ra / sửa |
|---|---|---|---|
| 1 | Nhãn số hình làm tròn sai: 0,00146 hiện "0,001", mọi thanh thành "0,002" | `hinh.py so_vn` (|v|<1 giữ 3 số lẻ, không phải 3 chữ số có nghĩa) | ĐÃ SỬA trong skill: giữ 3 chữ số có nghĩa |
| 2 | V01 báo sai câu kết luận có động từ "khoá", "thoát", "chạy" | `report.py` danh sách động từ hẹp | Mở rộng danh sách hoặc kiểm bằng có-động-từ theo từ điển; tạm né bằng "đang", "giảm" |
| 3 | Chương phương pháp vẫn bị đòi tiêu đề kết luận và [BCxx] cho từng ngày tháng, số thứ tự | cổng 6 | Miễn V01 + so-khong-nguon cho `NN-phuong-phap.md` (cùng lỗi LAB028 ghi "kiểm số quá chặt") |
| 4 | Ký tự "→" rơi font dự phòng Libertinus | D11 bắt đúng | Luật viết: không dùng mũi tên trong bảng; hoặc nạp font có → |
| 5 | Trang gần trống do chương tràn vài dòng (2 lần) | dàn trang | Thêm kiểm: trang cuối chương < 25% chữ thì cắt chữ hoặc gộp; nên tự động trong kiem-ban-in |
| 6 | `anh-trang` không xoá ảnh trang cũ khi PDF ngắn lại | `report.py anh_trang` | Xoá `trang-*.png` trước khi render |
| 7 | Không có bước 0 riêng: mượn mẫu của LAB028 | quy trình | Cho phép dùng lại `00-mau` của báo cáo trước cùng phong cách |
| 8 | Nhãn chương lặp ở đầu trang và cạnh số chương (chấm mù LAB028 cũng nêu) | `typst/lib.typ` | Bỏ nhãn đầu trang ở trang mở chương |
| 9 | Khối khuyến nghị dính vào đoạn trước, chữ đè đường kẻ | `typst/lib.typ khoi-khuyennghi` above: 0pt | ĐÃ SỬA: khối đầu cách 6 mm |
| 10 | Nhãn số thanh dài nhất bị cắt lề phải | `hinh.py` xlim ×1,12 | ĐÃ SỬA: ×1,22 |
| 11 | Chỉ số chú thích sát sau con số đọc thành số khác ("4" + chú thích 7 thành "47") | dàn trang | Đặt chú thích sau dấu câu, hoặc cách số; thêm kiểm |
| 12 | Nhãn [SUY LUẬN] in ra cho người đọc ngoài, người đọc mới thấy lạ | `report.py` | Ẩn khi in bản gửi ngoài, giữ trong bản duyệt |
| 13 | Nội dung nói quá dữ liệu mà mọi cổng script đều cho qua | quy trình | Giữ bắt buộc agent người đọc mới ở bước 8; người chấm mù chỉ thấy dàn trang |

### Điểm chấm mù qua các vòng
| Bản | Mù A | Mù B | Ghi chú |
|---|---|---|---|
| LAB028 (tự chấm 4,08) | 3,44 | 3,66 | 7/17 trang cả hai cùng trượt |
| AI trong nghiên cứu, bản 1 | 3,24 | 3,18 | chữ đè kẻ, nhãn cắt, trang trống cuối chương |
| AI trong nghiên cứu, bản 2 | 3,52 | 3,37 | còn 8–9/12 trang trượt; lỗi chính nằm ở khuôn `lib.typ` (mọi trang mở chương cùng một khuôn, nhãn chương lặp đầu trang, URL vỡ giữa chữ, nguồn dồn nửa trái) |

Kết luận vòng thử: sửa nội dung và 3 lỗi script nâng ~0,25 điểm; muốn qua 3,5 ở cả hai người chấm phải sửa khuôn Typst: (a) 2–3 kiểu trang mở chương xen nhau, (b) bỏ nhãn đầu trang ở trang mở chương, (c) trang nguồn 2 cột, ngắt URL ở dấu /, (d) chương ngắn thì không ép sang trang mới.
