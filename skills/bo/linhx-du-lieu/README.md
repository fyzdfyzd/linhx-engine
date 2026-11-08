# linhx-du-lieu v0.1 (LAB033)

Dọn dữ liệu "AI-ready" cho doanh nghiệp Việt. Máy làm phần xác định bằng luật, LLM chỉ lập recipe và đề xuất cho phần đuôi mơ hồ, người duyệt mọi dòng bị gắn cờ.

## Cài
```
python -m pip install pandas openpyxl underthesea
/plugin marketplace add D:/LINHX/LAB/LAB033-AI-READY-DATA/src
/plugin install linhx-du-lieu@linhx-lab-033
```
Antigravity (agy): gọi thẳng `python .../scripts/du_lieu.py <lệnh>` và đọc `skills/*/SKILL.md`.

## Skill
| Gõ | Làm gì |
|---|---|
| `/cham-nhanh` | Điểm 6 chiều + 3 lỗi lớn nhất (trang mồi miễn phí cho khách) |
| `/don-bang` | Mục đích → profile → recipe thao tác đóng → chạy thử → duyệt → chạy thật |
| `/kiem-dinh` | Hậu điều kiện, trước/sau, rubric dừng 4 chiều, biên bản bàn giao |
| `/viet-chuan` | Tra/chuẩn hoá từng giá trị Việt |

## Lệnh script
```
python scripts/du_lieu.py profile <file> --an-danh
python scripts/du_lieu.py cham <file> --out cham.md
python scripts/du_lieu.py ops
python scripts/du_lieu.py apply <file> <recipe.json>            # chạy thử
python scripts/du_lieu.py apply <file> <recipe.json> --yes      # ghi .sach/.diff/.can-duyet/.nhat-ky
python scripts/du_lieu.py kiem <file.sach.csv> <recipe.json> --goc <file gốc>
```

## Thử
```
python mau/tao_du_lieu_ban.py 2000 thu/      # dữ liệu giả có lỗi kiểu Việt + đáp án
python -m unittest discover -s tests
```

## Chưa có ở v0.1
Chuyển mã TCVN3/VNI (mới phát hiện), khớp tên mờ (fuzzy) và gộp bản ghi, dòng tài liệu → kho tri thức (`tai-lieu-kb`), báo cáo chẩn đoán PDF (`chan-doan`), ẩn danh trước khi gửi LLM (`bao-mat`).

Giấy phép phụ thuộc: underthesea Apache-2.0. Không chép code từ repo không có LICENSE (CleanAgent, LLM4DC, DS-Agent).
