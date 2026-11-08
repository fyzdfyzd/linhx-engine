---
name: radar-su-kien
description: Quét và index sự kiện business, tech, AI, startup, marketing ở Việt Nam (offline và online), chấm nên đi hay không, ra lịch .ics và bản tin. Dùng khi Linh hỏi "tuần này có event gì", "quét sự kiện", "event radar", "nên đi event nào", hoặc chạy định kỳ.
---

# Radar sự kiện

**Thư mục radar** (mặc định `D:\LINHX\LAB\LAB035-RADAR-CONG-DONG\su-kien`, hoặc biến `RADAR_HOME`): `config/sources.json` (nguồn), `config/profile.json` (hồ sơ chấm), `..\data\radar.db` (SQLite dùng chung với radar cộng đồng), `output/` (lịch, bản đồ, digest).
Script: `${CLAUDE_PLUGIN_ROOT}/scripts/eventscan.py` (Python chuẩn, không cần cài gì). Schema JSON ở `references/schema.md`.

## Quy trình

1. **Quét máy**, đứng trong thư mục radar: `python "${CLAUDE_PLUGIN_ROOT}/scripts/eventscan.py" all`
   Nguồn RSS, Google News RSS, iCal (Luma, Meetup, Google Calendar), trang HTML danh sách. Dòng `LỖI` thì ghi `"active": false` và lý do vào `_note` của nguồn, không xoá.
2. **Quét bằng tìm kiếm web** cho phần máy không với tới (Facebook event, trang dựng bằng JS, Ticketbox): chạy các nguồn `kind: "websearch"` trong `sources.json`, thêm tháng/năm hiện tại. Mỗi sự kiện **còn sắp diễn ra**:
   - mở trang chính thức (WebFetch), không tin trang tổng hợp;
   - ghi vào `data/moi-<ngày>.json` theo `references/schema.md`: ngày, thành phố, hình thức, BTC, giá vé, chủ đề, **diễn giả** (tên, chức danh, tổ chức), **nhà tài trợ** (tên, hạng);
   - `chua_xac_minh: false` chỉ khi đã đọc trang chính thức hoặc trang đăng ký.
   Rồi `... eventscan.py seed data/moi-<ngày>.json` và `... eventscan.py all --no-fetch`.
3. **Xác minh ứng viên máy tự trích** (`extract` sinh ra, đều `chua_xac_minh`): với các sự kiện nhãn Đi/Cân nhắc trong 45 ngày tới, mở link, sửa ngày/nơi/diễn giả bằng file seed. Tin không phải sự kiện thì `mark <id> bỏ`.
4. **Báo Linh** ngắn: 3 đến 5 sự kiện nên đi (ngày, nơi, vì sao, ai nói), sự kiện cần Linh quyết đăng ký (vé trả phí, đi tỉnh), và nhắc sự kiện đã đi chưa hấp thu. Đính kèm `output/digest/MOI-NHAT.md`, `output/lich-su-kien.ics`. Không dán lại cả bảng.

## Nhãn
- **Đi**: hợp chủ đề, có diễn giả đáng nghe hoặc người cần gặp, đi lại được.
- **Cân nhắc**: hợp một phần, xem vé và lịch.
- **Xem bản ghi**: nội dung hợp nhưng giá trị gặp người thấp, đợi video hoặc bài tường thuật rồi chạy `hap-thu-su-kien`.
- **Bỏ**: lệch chủ đề hoặc thuộc danh sách `tranh`.
Điểm (0 đến khoảng 95) = quan tâm ≤30 + diễn giả ≤20 + người cần gặp ≤15 + đi lại ≤15 + chi phí ≤10 + mới lạ ≤5. Linh sửa trọng số trong `profile.json`.

## Luật
- Không đăng ký, không mua vé, không nhắn BTC thay Linh.
- Cùng một sự kiện đăng ở nhiều nơi: script gộp theo id hoặc tên giống và cùng tháng; kỳ năm sau là sự kiện riêng, ghi `lap_lai: "hằng năm"`.
- Dùng chung khoá diễn giả/doanh nghiệp với radar cộng đồng LAB035: `radar.py all` tự đồng bộ diễn giả, nhà tài trợ, người đoạt giải sang bảng DN/KOL.
