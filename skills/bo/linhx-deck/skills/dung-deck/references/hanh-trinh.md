# Bước 10b. Hành trình cảm xúc và chú ý → `10-hanh-trinh.json`

Làm sau ghost deck, trước thân slide. Linh duyệt cùng ghost deck (cổng 10). `deck.py hanh-trinh <dir>` kiểm luật và vẽ `10-hanh-trinh.png`.

```json
{
  "che_do": "trinh-bay",
  "slides": [
    {"id": "bia", "cam_xuc": "to-mo", "tai": 1, "moc": "moc-cau", "ghi_chu": "câu hỏi mở: vì sao 12 tuần là đủ"},
    {"id": "tom-tat", "cam_xuc": "to-mo", "tai": 3, "moc": "khong"}
  ]
}
```

- `che_do`: `trinh-bay` (có người nói: slide thưa, chi tiết ở ghi chú người nói) hoặc `doc` (gửi đọc một mình: tiêu đề và `diem_chinh` tự giải thích). Hai chế độ là **hai tệp deck khác nhau**, không dùng một deck cho cả hai.
- `cam_xuc` (người nghe cảm thấy gì khi rời slide): `to-mo`, `lo-lang`, `cang`, `nhe-nhom`, `tin-tuong`, `hao-hung`, `san-sang`.
- `tai` (tải chú ý 1–5): 1 = một câu/một ảnh; 3 = một biểu đồ hoặc bảng gọn; 5 = bảng dày, nhiều số.
- `moc`: `moc-cau` (câu móc mở đầu), `nghi` (slide thở: ảnh toàn trang, một câu), `dat-lai` (đổi nhịp: số lớn, câu hỏi, trích dẫn), `khoanh-khac` (khoảnh khắc đáng nhớ, STAR), `khong`.

## Luật cổng (máy kiểm)

1. Câu móc ở 2 slide đầu.
2. Không quá 2 slide nặng (tải ≥ 4) liền nhau; sau đó là slide nghỉ.
3. Điểm đặt lại chú ý (`moc-cau`, `nghi`, `dat-lai`, `khoanh-khac`) cách nhau tối đa 4 slide (trình bày) / 6 slide (gửi đọc).
4. Cung căng → nhẹ: có slide `lo-lang`/`cang` trước slide `nhe-nhom`/`tin-tuong` đầu tiên (vấn đề trước giải pháp, kiểu SCQA).
5. Một `khoanh-khac` ở khoảng 50–80% deck (cảnh báo nếu thiếu).
6. Slide cuối `san-sang`, slide kết có `hanh_dong_chinh` (một việc).
7. Gửi đọc: tiêu đề ≥ 8 chữ. Trình bày: ghi chú người nói ≥ 40 chữ mỗi slide nội dung; 10 slide đầu thưa chữ.

## Renderer và ảnh dùng cảm xúc

- Slide `khang-dinh` không ảnh: `lo-lang`/`cang`/`to-mo` → nền tối; `nhe-nhom`/`tin-tuong` → nền sáng chuyển sắc nhẹ.
- `goi-anh` thêm ánh sáng theo cảm xúc của slide có ảnh: căng → lạnh, tối, nhiều bóng; nhẹ nhõm → ấm, sáng, mở.

Không dùng các "con số chú ý" truyền miệng (ví dụ người nghe chỉ chú ý 8 giây / 10 phút) trong slide hay luật: không có bằng chứng vững.
