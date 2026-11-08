# linhx-onbrand v0.2

Plugin Claude Code thiết kế ấn phẩm đúng ngôn ngữ thiết kế của brand, chấm thiết kế có bám brand guideline không, và đo năng lực bám chuẩn của designer hoặc AI.

| Skill | Làm gì |
|---|---|
| `onbrand-nap` | guideline → cây thư mục brand + `brand.json` |
| `onbrand-thiet-ke` | dựng ấn phẩm từ khuôn HTML của brand (logo vector, font, hoạ tiết, ảnh thật), xuất PNG, tự chấm đến khi ≥85 |
| `onbrand-cham` | chấm một thiết kế, thang 100, 5 mục |
| `onbrand-thi` | 5 đề chuẩn, chấm nhiều người/AI, xếp hạng |

Thang điểm: Màu 30 (máy đo ΔE2000), Chữ 20 (máy đọc font, ảnh thì Claude nhìn), Logo 25 (Claude nhìn), Hình/bố cục 15 (Claude nhìn), Nội dung 10 (máy tìm từ cấm). ≥85 ĐẠT CHUẨN, 70–84 SỬA NHẸ, <70 LỆCH CHUẨN.

## Cài trên Windows
```
claude plugin marketplace add D:\LINHX\LAB\LAB043-DESIGN-ONBRAND\src
claude plugin install linhx-onbrand@linhx-onbrand
pip install pillow numpy
```
Thiết kế cần Edge hoặc Chrome (Windows có sẵn Edge). PDF cần poppler (`winget install oschwartz10612.Poppler`); PPTX ra ảnh cần LibreOffice (không có thì vẫn chấm font và chữ).

Antigravity: chép thư mục `skills/` vào `.agent/skills/` của workspace, script gọi bằng đường dẫn tuyệt đối.

## Thử nhanh
```
python scripts/onbrand.py cham ..\..\brands\listening-vietnam\brand.json <thiet-ke.png> --ra kq.json
python scripts/onbrand.py bao-cao kq.json --ra bao-cao.html
```

## Thiết kế nhanh ([DOANH NGHIỆP BÁN LẺ ĐÃ ẨN DANH])
```
python scripts/thiet_ke.py ds ..\..\brands\[DOANH NGHIỆP BÁN LẺ ĐÃ ẨN DANH]
python scripts/thiet_ke.py dung ..\..\brands\[DOANH NGHIỆP BÁN LẺ ĐÃ ẨN DANH] social-vuong-do.html noi-dung.json --ra ra\social.png
python scripts/onbrand.py cham ..\..\brands\[DOANH NGHIỆP BÁN LẺ ĐÃ ẨN DANH]\brand.json ra\social.png
```
