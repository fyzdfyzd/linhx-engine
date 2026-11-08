---
name: soi-viet-nam
description: B5 radar khoảng trống. Mang từng cụm nhu cầu về Việt Nam, xếp mức còn trống, mỏng hay đã có người chiếm trên từng nền tảng VN (Facebook, YouTube, TikTok, Substack, Spiderum, LinkedIn, Threads, podcast, sách, báo). Dùng sau B4 của LAB029.
---

# B5. Soi về Việt Nam

Câu hỏi: ở VN đã có ai nói về nhu cầu này chưa, nói ở đâu, kênh lớn cỡ nào, có hiệu quả không.

1. Quét bổ sung phía Việt Nam bằng skill `hien-tuong` cho các nền tảng trong `cau-hinh.json` → `nen_tang_vn`, theo từ khoá `tu_khoa_vi` của từng cụm:
   - YouTube: tìm từ khoá, `doc_feed.js` lấy tít và lượt xem.
   - Facebook, Threads, LinkedIn VN: tìm kiếm bài theo từ khoá hoặc trang người viết lớn; `doc_feed.js`.
   - Spiderum: trang tìm kiếm hoặc chủ đề; đọc tay nếu cần.
   - Podcast: `apple_podcast.py vn 100`.
   - Sách: bảng bán chạy Fahasa, Tiki theo tháng; đọc tay, ghi `loai: "kenh"`, `hang: "fahasa#<hạng>"`.
   - TikTok: chỉ đọc tay trang tìm kiếm, ghi số view.
2. `python gapscan.py nhap --thi-truong vn b1-vn-*.jsonl`
3. `python gapscan.py so-vn` (thêm `--embed` nếu máy đã cài `sentence-transformers`, để bắt bài không trùng từ khoá).
   Mức mỗi nền tảng: `open` (đã quét, không thấy ai), `thin` (có người nhưng nhỏ), `covered` (có kênh vượt ngưỡng `nguong_kenh_lon`, hoặc ≥ 3 kênh vừa, hoặc lọt top 20 bảng xếp hạng), `chua_quet`.
4. Đọc `05-viet-nam.json`, kiểm tay mỗi cụm có mức `covered`: kênh đó có thật nói đúng nhu cầu không, hay chỉ trùng từ khoá. Ghi sửa vào `05-ghi-chu.md`; nếu khớp sai thì sửa `tu_khoa_vi` rồi chạy lại.
5. `python gapscan.py kiem b5`. Dưới 60% độ phủ dữ liệu: quét thêm, không suy "còn trống" từ chỗ chưa quét.

Ghi thêm ở `05-ghi-chu.md` cho mỗi cụm: kênh Việt lớn nhất là ai, giọng gì, yếu ở đâu (mỏng chuyên môn, chậm, chỉ dịch lại, quảng cáo nhiều).
