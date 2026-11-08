# Cú pháp chương (06-chuong/*.md)

report.py đọc tệp này thành khối dàn trang. Chỉ dùng các cú pháp dưới đây.

```
# Tiêu đề chương là câu kết luận | Tên ngắn cho đầu trang
> Sapô 1–2 câu (dòng trích dẫn đầu tiên ngay sau tiêu đề).

Đoạn văn thường. Câu có số kèm mã bằng chứng 39% [BC03]. Chú thích cuối trang^[Nội dung chú thích.].
Chữ **đậm** và *nghiêng*.

## Tiêu đề mục là câu kết luận

::: hinh H01

::: so-lon Nguồn: Đơn vị, tài liệu, năm
52% | giải thích ngắn ≤ 30 tiếng
3,2 lần | giải thích
:::

::: trich | Tên, chức danh người nói
Câu trích dẫn (nếu là trích nguồn thì phải khớp nguyên văn và có [BCxx]).
:::

::: sidebar Tiêu đề hộp | Nhãn (Định nghĩa, Góc nhìn, Hỏi đáp…)
Nội dung hộp, mỗi dòng một đoạn.
:::

- Gạch đầu dòng
- Gạch đầu dòng

::: khuyen-nghi
Động từ mở đầu tiêu đề | Giải thích ngắn, có thể có [BCxx].
:::
```

Tóm tắt điều hành `00-tom-tat.md`:

```
# Những điểm chính
> Một câu mở.
::: so-lon Nguồn: …
39% | …
:::
1. **Câu kết luận ≤25 tiếng.** Một đến hai câu số có mốc so sánh [BC01].
```
