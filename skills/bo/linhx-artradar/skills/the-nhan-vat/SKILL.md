---
name: the-nhan-vat
description: Dùng khi dựng thư viện nhân vật tham khảo từ Bangumi/AniList (hoặc mô tả của Linh), viết lại phần hình ảnh và vai trò theo từ điển phong cách, xuất ghi chú Obsidian và Character Card V2, lọc nhân vật.
---
# Thẻ nhân vật (M4)

1. Seeds: file JSON liệt kê tác phẩm (`bangumi[].keyword` tên Trung, `anilist[].search` tên romaji) và `chu_de`. Mẫu: `seeds-tuan-2.json`.
2. Nhập: `python scripts/nhap_nhan_vat.py --seeds seeds-tuan-2.json --out data/characters.json`
   - Bangumi: tìm tác phẩm, lấy nhân vật (主角 trước 配角), gọi chi tiết từng nhân vật. AniList: 1 truy vấn GraphQL mỗi tác phẩm.
   - Lưu link, link ảnh, độ nổi tiếng, `tom_tat_nguon` ≤300 ký tự. Chạy lại an toàn: giữ phần đã điền.
3. Viết lại theo lô 10 thẻ (Claude):
   - Đọc `tom_tat_nguon`, mở `source_url` nếu cần. Xem ảnh nhân vật: tải vào thư mục tạm, xem, **xoá ngay**.
   - Điền `mo_ta` (2-3 câu bằng lời mình), `hinh_khoi`, `bang_mau`, `dac_diem_nhan_dien`, `trang_phuc`, `ty_le` (giá trị trục `ty_le` của từ điển), `loai` và `vai_tro` (giá trị trục `loai`/`vai_tro` của `../../schemas/tu-dien-nhan-vat.json`: người, mèo, yêu/linh thú…; nhân vật chính, người dẫn đường/sư phụ, đối thủ, hài/làm nền, phản diện, dân làng/thường dân…), `archetype` (vd: phế vật nghịch thiên, sư phụ lười, linh thú tsundere), `style_tags` theo `../../schemas/tu-dien-phong-cach.json`, `dung_cho`.
4. Xuất: `python scripts/the_nhan_vat.py notes --cards data/characters.json --dir output/characters`; thẻ V2 (chỉ thẻ đã có `mo_ta`): `... v2 --cards data/characters.json --dir output/cards-v2`.
5. Lọc thử: `... loc --cards data/characters.json --chu-de mèo --vai-tro "người dẫn đường"`. Mỗi cờ khớp đúng trường của nó; `chu_de` gắn theo tác phẩm nên muốn chỉ lấy nhân vật là mèo thì thêm `--loai mèo`. `--q` tìm tự do (cả `mo_ta`). `--ty-le chibi` cũng khớp thú `mascot/blob` theo `ty_le_alias` trong `tu-dien-nhan-vat.json`.
6. Seeds khớp nhầm bản (tiểu thuyết ít nhân vật, phim ngắn hợp tác): ghi `subject_id` (Bangumi) hoặc `id` (AniList) vào seed để bỏ bước tìm.

Luật: nhân vật là IP của người khác, chỉ học cấu trúc (vai trò, archetype, cách thiết kế nhận diện); không đưa vào sản phẩm, không dùng ảnh. `tom_tat_nguon` không đưa vào thẻ V2.
