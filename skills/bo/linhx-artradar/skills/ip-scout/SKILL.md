---
name: ip-scout
description: Dùng khi chấm và xếp hạng IP (truyện, game, phim) để học cấu trúc làm world: lấy metadata từ Wikidata/Bangumi/AniList/Fandom, chấm 6 tiêu chí 1-5, viết bài học cấu trúc, xuất bảng xếp hạng.
---
# Thám IP (M6)

1. Seeds: `seeds-tuan-3.json` liệt kê IP theo `nhom`. Mỗi IP ghi `wikidata` (QID đã kiểm nhãn) hoặc `wikidata_search` (lấy kết quả đầu, phải kiểm), `bangumi` (subject id), `anilist` (media id), `fandom` (tên miền con).
2. Lấy: `python scripts/ip_scout.py lay --seeds seeds-tuan-3.json --out data/ips.json`
   - Wikidata: SPARQL trước, gặp 429/403/503 thì dùng Action API `wbgetentities`. Lấy loại hình (P31), tác giả (P50/P170), chủ sở hữu/phát hành (P123/P178/P127/P272), năm (P577/P571).
   - Bangumi: số nhân vật, lượt thu thập. AniList: popularity, favourites. Fandom: chỉ số bài trong `siteinfo` (API hay trả 403 với UA của lab; khi đó chỉ giữ link, không đổi UA để lách).
   - Kiểm nhãn Wikidata từng IP. Khớp nhầm (phim truyền hình thay vì tiểu thuyết, game thay vì truyện) thì ghi QID đúng vào seed rồi chạy lại. Chạy lại giữ nguyên phần đã chấm.
3. Chấm (Claude), mỗi tiêu chí 1-5, ghi vào `diem`:
   - `do_sau_the_gioi`: địa lý, lịch sử, luật, hệ sức mạnh có ăn khớp không.
   - `nhan_vat_co_ca_tinh`: số nhân vật nhớ được tính cách; ghi ước lượng vào `so_nhan_vat_co_ca_tinh`.
   - `kha_nang_mo_rong`: cấu trúc có cho thêm phần/tập/vùng mà không phá thế giới không.
   - `cong_dong_fan`: dựa trên số liệu API + hiểu biết chung; ghi rõ khi là ước lượng.
   - `khac_biet_hinh_anh`: nhận ra từ hình bóng/màu không.
   - `ban_quyen_kha_nang_hoc`: 5 = tài liệu công khai nhiều, cấu trúc dễ tách để học. IP vẫn là của người khác.
   - Ghi `nam_goc` (năm ra bản gốc; Wikidata hay trả năm bản dịch).
   - `bai_hoc`: 3-5 dòng bài học cấu trúc (cách dựng phe, hệ sức mạnh, nhịp kể, cách nhận diện), không kể lại cốt truyện.
4. Xếp hạng: `python scripts/ip_scout.py xep --ips data/ips.json --md output/ip-xep-hang.md` (tổng 6 tiêu chí, xếp theo `nhom`).
5. Lấy 2 IP đứng đầu mỗi nhóm làm lorebook mẫu bằng skill `world-lore`.

Luật: chỉ lưu metadata, link, số đếm và chữ tự viết. Chữ Fandom là CC BY-SA, trích thì ngắn và ghi nguồn. IP người khác chỉ để học cấu trúc; world của ta phải là bản gốc.
