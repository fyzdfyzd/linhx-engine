# Duyệt độc lập

Người dựng không tự duyệt bài của mình. Sau khi `kiem_khung.mjs` hết LỖI và đã render nháp, giao cho agent duyệt có ngữ cảnh sạch (không đọc hội thoại dựng). Học từ video-shotcraft, mg-styles-15, motion-designer (kaventro), opus-visual-motion-engine, anything2explainer.

## Cách chia
- Mỗi agent một đoạn khoảng 12 giây, chấm theo một góc: tổng thể, chuyển cảnh, chữ. Thêm một agent xem cả phim ở cỡ điện thoại (360 px rộng). Chạy song song.
- Phim ngắn hơn 20 giây: một agent tổng thể + một agent điện thoại là đủ.
- Đưa cho agent: đường dẫn `kiem/sheet.jpg` hoặc ảnh khung của đoạn đó (mỗi 0,25–0,5 giây), `TREATMENT.md`, `STYLE.md` của style, `loi.json`, rubric dưới. Không đưa code.
- Agent trả: điểm 1–10 cho từng tiêu chí, lỗi kèm **giây hoặc số khung**, đề xuất sửa một dòng. Hết lỗi thì ghi `sach`.
- Đạt khi mọi đoạn ghi `sach` và mọi điểm ≥ 8. Sửa rồi gửi lại đúng đoạn đã đổi. Tối đa 2 vòng; hết 2 vòng còn lỗi thì báo Linh kèm khung.

## Rubric
| Tiêu chí | Câu hỏi agent phải trả bằng quan sát cụ thể, không ghi "đạt" |
|---|---|
| Thông điệp | Xem một lần có nhắc lại được ý chính không? Ý đó có hiện từ 2 giây đầu tới cảnh đinh? |
| Bố cục | Ở mỗi khung chính, mắt dừng đầu tiên ở đâu? Đó có phải điều cần nói? Một khung không quá 5 thứ tranh nhau. |
| Chuyển động | Mỗi khung có đúng một thứ chuyển động quan trọng? Có độ trễ so le, không phải mọi thứ cùng 300 ms? Mọi thứ đã yên trước khi rời? |
| Chuyển cảnh | Mỗi cú chuyển có vật mang sang, không có khung trống? Không phải cảnh nào cũng mờ ra rồi mờ vào? |
| Chữ | Đủ to trên điện thoại, đủ lâu để đọc (≥ 1,2 giây cho 8 chữ), dấu tiếng Việt đúng, không đè hình chính, không nằm trong dải phụ đề. |
| Đúng style | So với `STYLE.md`: màu, nét, chất liệu, chuyển động có đúng bất biến của style? Khác demo của style ít nhất 4/6 điểm (mở, cảnh đinh, đường máy, nhạc, kết, cấu trúc)? |
| Tiếng | Mỗi cú hình có tiếng, mỗi tiếng có lý do trên hình? Giọng khớp chữ? (đọc `kiem_video.py`, agent không nghe được) |
| Sự thật | Mọi số, tên, năm trên hình có trong `NGUON.md`? Số minh hoạ có ghi "minh hoạ"? |

Câu cuối, trả lời thật: **"Trông như được thiết kế có chủ ý, hay chỉ là máy sinh ra?"** Nếu là máy sinh: chỉ ra cái gì rập khuôn.

## Dấu hiệu rập khuôn hay gặp (tránh khi đề bài để tự do)
| Dấu hiệu | Thay bằng |
|---|---|
| nền kem + chữ có chân + điểm nhấn cam đất; hoặc nền gần đen + một màu neon, dùng cho mọi chủ đề | bảng màu lấy từ chất liệu của chính chủ đề (gỗ nhà cổ, men gốm, màu ngành hàng) |
| thẻ bo góc giống hệt nhau, cùng bóng mờ | bo góc theo cấp bậc, chỉ đóng khung vật có ranh giới thật |
| gradient tím trang trí, kính mờ | màu phẳng; một gradient tối đa và chỉ cho thứ liên tục có thật (ánh sáng, nhiệt) |
| CHỮ IN HOA giãn rộng làm nhãn, dấu chấm giữa ngăn các mục, mũi tên "→" | viết thường theo câu; bỏ nhãn lặp lại nội dung |
| Inter/font hệ thống mặc định | font chọn cho chủ đề, có dấu Việt (Be Vietnam Pro, Noto Serif, Lora…) |
| mở bằng tiêu đề + phụ đề + nút + ảnh chụp | mở bằng thứ đặc trưng nhất của chủ đề |
| mọi thứ căn giữa, cùng một nhịp lưới | mỗi cảnh một hệ căn, đổi nhịp |
| logo giả, số bịa, chữ lorem | tư liệu thật; minh hoạ thì ghi rõ |

Dồn táo bạo vào một chỗ, rồi bỏ bớt một thứ trang trí.

## Mức nỗ lực theo chặng (claude-motion)
Bảng cảnh: thấp. Dựng: vừa. Duyệt: cao. Agent duyệt dùng model mạnh nhất; agent dựng loạt có thể dùng model rẻ hơn hoặc agy.
