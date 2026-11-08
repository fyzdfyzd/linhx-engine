# Đề cho agy chạy đêm

Dùng khi phim dài hơn khoảng 60 giây, hoặc làm loạt (nhiều tập, nhiều biến thể). Claude làm bước 1–6 và **một cảnh mẫu chuẩn**; agy (Antigravity, Gemini) làm hàng loạt phần còn lại theo khuôn. Cách chạy đêm giống LAB034 (agy làm game đêm).

Chép khối dưới vào `<phim>/DE-AGY.md`, điền chỗ `<>`:

```markdown
# Đề đêm: <tên phim>

## Đã có (không sửa)
- STYLE: <đường dẫn STYLE.md>  · máy dựng: <lemo|hyperframes|remotion>
- TREATMENT.md, loi.json, am-thanh/cues.json (lưới thời gian, KHÔNG đổi giây)
- Cảnh mẫu chuẩn: <đường dẫn file cảnh>, ảnh tham chiếu: <stills/...>
- Font: fonts/ (chỉ dùng font trong này)

## Việc
Dựng các cảnh <danh sách id> theo bảng cảnh trong TREATMENT.md, cùng cách viết với cảnh mẫu.
Mỗi cảnh: viết code → render khung tĩnh giữa cảnh → tự so với ảnh tham chiếu → sửa tối đa 3 vòng.

## Cổng chấm (phải qua hết mới ghi XONG)
1. Lệnh kiểm của máy dựng không lỗi (lemo: still + readcheck; hyperframes: `npx hyperframes check`; remotion: `npx remotion still`).
2. Không chữ tràn khung, không dấu tiếng Việt vỡ, không khung đen.
3. Mỗi cảnh bắt đầu và kết thúc đúng giây trong cues.json (±0,1 giây).
4. Render nháp 960×540 12 fps toàn phim chạy hết.

## Không được
- Đổi STYLE, đổi font, đổi lời, đổi giây.
- Thêm người thật, logo, ảnh tải trên mạng.
- Cài gói ngoài danh sách: <danh sách>.

## Sáng ra
Ghi `SANG-NAY.md`: cảnh nào XONG, cảnh nào kẹt (lý do, ảnh), lệnh render bản đủ. Chạy `to_sheet.sh` trên bản nháp, để contact sheet cạnh SANG-NAY.md.
```

Sáng hôm sau Claude chỉ đọc `SANG-NAY.md` và contact sheet, sửa cảnh kẹt, rồi render bản đủ và ghép tiếng.
