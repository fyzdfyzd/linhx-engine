# linhx-pipeline v0.1

Lõi pipeline dùng chung cho các plugin LinhX, rút từ cách Koharu tổ chức pipeline dịch manga (xem `../../01-NGHIEN-CUU-NEN.md`, `../../02-KHUON-PIPELINE.md`).

## Cài

Claude Code: `/plugin marketplace add <đường dẫn tới thư mục src>` rồi `/plugin install linhx-pipeline@linhx-pipeline`.
Antigravity: chép `skills/pipeline/SKILL.md` vào `.agent/skills/pipeline/` của dự án và gọi `python <đường dẫn>/scripts/pipe.py`.
Chỉ cần Python 3.9+, không thư viện ngoài.

## Thư mục dự án

```
<du-an>/
  pipeline.json   tầng, phụ thuộc, cổng
  muc.json        danh sách mục theo thứ tự ưu tiên
  bang.json       chốt từng ô: hash đầu vào, hash đầu ra, nguồn, khoá (chỉ pipe.py ghi)
  chung/          tệp dùng chung
  muc/<id>/       đầu ra từng ô
  nhat-ky.jsonl   sự kiện
  SANG-NAY.md     tóm tắt cho buổi sáng
```

## Lệnh chính

`moi`, `bang`, `viec`, `xong`, `bo-qua`, `loi [--tai-nguyen]`, `lam-lai`, `nhan`, `mo-khoa`, `mo-dung`, `sang-nay`, `mau`. Chi tiết: `python scripts/pipe.py -h` và đầu tệp `pipe.py`.

## Kiểm

`python -m unittest tests/test_pipe.py`: 11 test, gồm ca "Linh sửa slide 4 thì chỉ 5 ô của slide 4 thành cũ", "đổi thẻ phong cách thì chỉ tầng prompt ảnh và tầng dựng thành cũ", "hết lượt ảnh lần hai thì dừng".

## Chưa làm (v0.2)

- Nối `linhx-deck` dùng `pipe.py` thay cho phần trạng thái bước 10-13 (hiện có công cụ chuyển `tu-linhx-deck.py`).
- Tầng `dung` của deck chưa gọi `deck.py xuat`; đang để Claude ghép tay.
- PA3: lệnh `dem` giao ô cho agy qua đêm, một lane cho mỗi dịch vụ có giới hạn.
