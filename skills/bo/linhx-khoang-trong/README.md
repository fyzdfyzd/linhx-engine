# linhx-khoang-trong v0.1

Radar khoảng trống độc giả cho LINHX (LAB029). Đi từ top bài, top tác giả, top kênh trên Medium, Substack và kênh quan điểm (LinkedIn, X, Threads, Facebook) → nhu cầu và nỗi đau độc giả → ai đang thắng và vì sao → quy mô → soi về Việt Nam → khoảng trống → kế hoạch kênh, để Linh chiếm topic trước.

## Cài
- Claude Code: `claude plugin install <đường dẫn tới thư mục này>` hoặc chép vào thư mục plugin; agy: trỏ workspace vào thư mục này và đọc `skills/*/SKILL.md`.
- Python 3.10+ (không cần thư viện ngoài). Tuỳ chọn: `pip install sentence-transformers` để dùng `so-vn --embed`.
- Chrome đã đăng nhập Medium (cần cho `medium_tag.js`), LinkedIn, Facebook nếu muốn quét kênh quan điểm. Dùng Claude in Chrome để dán adapter.

## Chạy
Nói với Claude: "chạy radar khoảng trống toàn cảnh" (skill `radar-khoang-trong`). Hoặc từng bước:
```
cd D:\LINHX\LAB\LAB029-KHOANG-TRONG-DOC-GIA\chay\2026-10-20-toan-canh
python <plugin>\scripts\gapscan.py init
python <plugin>\scripts\gapscan.py nhap b1-substack.jsonl b1-medium.jsonl
python <plugin>\scripts\gapscan.py tin-hieu          # rồi Claude viết 02-cum.json
python <plugin>\scripts\gapscan.py gan-cum
python <plugin>\scripts\gapscan.py dau-vao-b3        # Claude viết 03-nguoi-thang.md
python <plugin>\scripts\gapscan.py quy-mo
python <plugin>\scripts\gapscan.py nhap --thi-truong vn b1-vn-*.jsonl
python <plugin>\scripts\gapscan.py so-vn
python <plugin>\scripts\gapscan.py cham              # Claude viết 07-co-hoi.md
```

## Cấu trúc
- `skills/`: 8 skill (1 điều phối + 7 bước).
- `scripts/gapscan.py`: đếm, gom, chấm, cổng kiểm.
- `scripts/adapters/trinh-duyet/`: `substack_bxh.js`, `medium_tag.js`, `doc_feed.js` (LinkedIn, Facebook, Threads, X, YouTube; thử nghiệm).
- `scripts/adapters/apple_podcast.py`: bảng xếp hạng podcast VN, US.
- `references/`: `schema.md`, `cong-thuc.md`.

## Giới hạn v0.1
- Adapter trình duyệt chưa chạy thử trên máy Linh (container cloud bị chặn medium.com, substack.com). `medium_tag.js` dùng cùng truy vấn `tagFeed` đã chạy được trong `medium_scan.js` của vault; `substack_bxh.js` dùng cùng endpoint với `substack_scan.js`.
- `doc_feed.js` phụ thuộc giao diện từng mạng; khi đọc ra 0 bài thì đọc tay theo skill `hien-tuong`.
- Khớp tiếng Việt bằng từ khoá có thể sót hoặc khớp nhầm; dùng `--embed` và kiểm tay mức `covered`.
- Công thức là v0.1, cần hiệu chỉnh sau 3 lượt thật.

Chỉ đọc dữ liệu công khai, nhịp chậm, cho nghiên cứu cá nhân. Không follow, like, đăng, nhắn thay Linh.
