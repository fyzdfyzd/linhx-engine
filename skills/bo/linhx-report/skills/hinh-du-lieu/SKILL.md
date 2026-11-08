---
name: hinh-du-lieu
description: Bước 4 của linhx-report. Biến bằng chứng thành hình (exhibit) chuẩn báo cáo tư vấn: tiêu đề là câu kết luận, dòng đối tượng và đơn vị, nhãn số trực tiếp, một màu nhấn, nguồn có n, mỗi chuỗi số trỏ mã bằng chứng; vẽ bằng hinh.py ra SVG theo style. Dùng trong quy trình bao-cao hoặc khi cần vẽ hình báo cáo.
---

# Bước 4: dữ liệu và hình

Luật "vẽ hết hình trước khi viết": chương nào cũng viết quanh hình của nó.

## Viết `04-hinh.json`

Mỗi hình (mẫu ở `du-lieu/mau/04-hinh.json`):
- `id` H01…; `loai`: `thanh-ngang` (so sánh hạng mục, mặc định), `cot` / `cot-nhom` (so sánh theo nhóm, ít nhãn), `duong` (thời gian ≥4 mốc), `bang` (≤6 cột, ≤10 dòng).
- `tieu_de`: CÂU KẾT LUẬN có dấu chấm, 8–30 tiếng, nên có số hoặc so sánh. Sai: "Tỷ lệ dùng AI theo ngành." Đúng: "Ngân hàng dùng AI nhiều gấp đôi bán lẻ."
- `doi_tuong`: ai/cái gì được đo + đơn vị ("% doanh nghiệp, n = 1.200").
- `chuoi[].gia_tri` lấy đúng số trong bằng chứng; `chuoi[].bc` = mã BC. Script so từng giá trị với số trong bằng chứng (≤1% đạt, ≤10% cảnh báo, hơn nữa là lỗi).
- `nhan_manh`: hạng mục mang thông điệp (tô màu nhấn); chỉ một.
- `nguon`: "Đơn vị, tên tài liệu, tháng/năm; n = …" bằng tiếng Việt. `ghi_chu`: định nghĩa, câu hỏi khảo sát, cách tính.
- `rong`: `full` (trải hết khổ) hoặc `col` (một cột, phong cách 2 cột).

Một hình một thông điệp. Có hai thông điệp thì tách hai hình. Không dùng tròn (pie) quá 3 phần, không 3D, không trục kép.

## Vẽ

`python hinh.py <dir>` → `04-hinh/H01.svg`… theo màu và font của `style.json`. Mở vài SVG xem: nhãn không chồng, chữ có dấu đúng, hình không quá cao.

`report.py cong <dir> 4`.
