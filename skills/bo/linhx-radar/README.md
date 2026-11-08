# linhx-radar (v0.2)

Radar LINHX hợp nhất (gộp 14/10/2026): radar cộng đồng LAB035 + radar sự kiện, giải thưởng LAB037, gọi kèm radar cuộc thi LAB022 và radar quỹ LAB013. Một thư mục, một CSDL `data/radar.db`, một bảng `output/RADAR-LINHX.xlsx`, một bản tin `output/BAN-TIN-MOI-NHAT.md`, một lịch chạy "LINHX Radar".

| Skill | Khi nào |
|---|---|
| `radar` | điều phối: chạy lượt chung, đọc bản tin |
| `radar-cong-dong`, `them-cong-dong`, `ho-so-doi-tuong`, `offer-cong-dong` | cộng đồng, nhà tài trợ, KOL, offer |
| `radar-su-kien`, `tham-dinh-su-kien`, `hap-thu-su-kien`, `ban-do-chu-de`, `them-nguon-su-kien` | sự kiện: nên đi, chuẩn bị, hấp thu, chủ đề |
| `radar-giai-thuong` | giải thưởng DN và cá nhân |

Scripts (Python chuẩn; openpyxl để ra xlsx):
- `radar.py all [--no-fetch] | ban-tin | cong-dong <lệnh> | su-kien <lệnh>`: chạy chung.
- `congdong.py`: cộng đồng, DN, KOL, pain → offer, CRM nhẹ.
- `eventscan.py`: sự kiện, giải thưởng; `config` ở `su-kien/config`, CSDL trỏ `..\data\radar.db`.
- `chay-radar.bat`, `dang-ky-lich-chay.ps1`: một lịch 7:30 mỗi sáng, gỡ 4 lịch cũ (Community, Event, Contest, Grants Radar).

Cài: chép thư mục `linhx-radar` vào chỗ chứa plugin, gỡ `linhx-cong-dong` và `linhx-su-kien` cũ. Plugin `linhx-cuoc-thi` (LAB022) giữ lại cho viết bài dự thi.
