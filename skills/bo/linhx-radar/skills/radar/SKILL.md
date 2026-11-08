---
name: radar
description: Radar LINHX hợp nhất. Chạy một lượt quét chung (cộng đồng, nhà tài trợ, KOL, sự kiện, giải thưởng, cuộc thi, quỹ tài trợ) và báo bản tin. Dùng khi Linh nói "chạy radar", "tuần này có gì", "bản tin radar", hoặc khi không rõ nên dùng radar con nào.
---

# Radar LINHX

Một thư mục: `D:\LINHX\LAB\LAB035-RADAR-CONG-DONG` (biến `RADAR_HOME`). Một CSDL: `data/radar.db`.

| Phần | Ở đâu | Skill chi tiết |
|---|---|---|
| Cộng đồng, DN tài trợ, KOL, pain → offer | `config/`, bảng community/company/kol | `radar-cong-dong`, `them-cong-dong`, `ho-so-doi-tuong`, `offer-cong-dong` |
| Sự kiện, giải thưởng | thư mục con `su-kien/`, bảng event/award/person/org/role | `radar-su-kien`, `tham-dinh-su-kien`, `hap-thu-su-kien`, `radar-giai-thuong`, `ban-do-chu-de`, `them-nguon-su-kien` |
| Cuộc thi viết, sáng tạo | LAB022 (plugin `linhx-cuoc-thi`) | gọi qua `config/radar.json` |
| Quỹ, tài trợ, RFP | LAB013 (`callscan.py`) | gọi qua `config/radar.json` |

## Mỗi lượt
1. `python "${CLAUDE_PLUGIN_ROOT}/scripts/radar.py" all` trong thư mục radar. Lệnh này quét cộng đồng, sự kiện; nhập cuộc thi LAB022 vào bảng giải; đồng bộ diễn giả, nhà tài trợ, người đoạt giải sang bảng DN/KOL (cùng khoá tên); chấm điểm; chạy LAB022, LAB013; gom `output/BAN-TIN-MOI-NHAT.md` và `output/RADAR-LINHX.xlsx`.
2. Phần máy không với tới (Facebook, LinkedIn, Luma Hà Nội, Ticketbox): làm theo bước 2 của `radar-cong-dong` và `radar-su-kien`, ghi file seed, rồi `radar.py cong-dong seed <file>` hoặc `radar.py su-kien seed <file>`, cuối cùng `radar.py all --no-fetch`.
3. Báo Linh ngắn từ bản tin: sự kiện nên đi tuần này, giải sắp hết hạn, 3 DN/KOL đáng tiếp cận kèm offer, việc cần Linh quyết. Đính kèm bản tin và xlsx.

## Luật chung
- Không đăng ký, mua vé, nộp giải, nhắn tin, kết bạn hay gửi email thay Linh.
- Không cào Facebook/LinkedIn bằng script; chỉ đọc trang công khai hoặc dữ liệu Linh dán.
- Mỗi dòng có nguồn; chưa mở được trang gốc thì đánh dấu chưa xác minh.
- Đổi giai đoạn bằng lệnh `mark` (sửa tay trong xlsx sẽ bị ghi đè).
