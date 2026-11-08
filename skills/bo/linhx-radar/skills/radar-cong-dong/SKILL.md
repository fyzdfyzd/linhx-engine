---
name: radar-cong-dong
description: Quét định kỳ các hiệp hội, cộng đồng, sự kiện doanh nghiệp ở Việt Nam (CSMO, VSMCamp, Brands Vietnam, GPeC...), cập nhật CSDL nhà tài trợ và KOL, chấm điểm cơ hội, xuất bảng xlsx và bản tin. Dùng khi Linh nói "quét cộng đồng", "radar cộng đồng", "có gì mới ở CSMO", "ai tài trợ", hoặc chạy định kỳ.
---

# Radar cộng đồng

Thư mục radar (mặc định `D:\LINHX\LAB\LAB035-RADAR-CONG-DONG`, hoặc biến `RADAR_HOME`; phần sự kiện, giải ở thư mục con `su-kien`):
`config/sources.json` (nguồn), `config/offers.json` (offer LINHX), `config/profile.json` (ngành ưu tiên),
`data/radar.db` (SQLite: community, company, kol, link, signal, page, log), `data/seed-*.json` (dữ liệu tuyển tay),
`output/RADAR-LINHX.xlsx`, `output/csv/`, `output/digest/`.
Script: `${CLAUDE_PLUGIN_ROOT}/scripts/congdong.py` (Python chuẩn; openpyxl để ra xlsx).

## Quy trình mỗi lượt

1. **Máy quét** (Google News, YouTube, RSS, trang nhà tài trợ/diễn giả), đứng trong thư mục radar:
   `python "${CLAUDE_PLUGIN_ROOT}/scripts/radar.py" all` (chạy cả cộng đồng, sự kiện, giải, cuộc thi, quỹ)
   Đọc dòng `LỖI`: nguồn chết thì đặt `"active": false` và ghi lý do vào `_note`.
2. **Quét bằng tìm kiếm web** phần máy không với tới (fanpage, group Facebook, LinkedIn, TikTok, trang JS).
   Với mỗi cộng đồng `uu_tien >= 5`, chạy WebSearch: `"<tên cộng đồng>" <tháng> <năm>`, `"<tên sự kiện> <năm> nhà tài trợ"`, `"<tên sự kiện> <năm> diễn giả"`.
   Mở trang gốc (WebFetch) trước khi ghi. Ghi DN, KOL, sự kiện, chủ đề, pain point mới vào `data/new-<ngày>.json` theo `references/schema.md`, rồi:
   `python ".../congdong.py" seed data/new-<ngày>.json` và `... score` `... export` `... digest`.
3. **Đọc tín hiệu có `ứng viên tài trợ`** trong digest: tên nào là doanh nghiệp thật thì thêm vào file new, tên rác thì bỏ.
4. **Báo Linh ngắn**: cái gì mới (sự kiện, nhà tài trợ, KOL), 3 cơ hội đáng làm tuần này kèm offer gợi ý, việc cần Linh quyết. Đính kèm `output/digest/MOI-NHAT.md` và xlsx. Không chép lại cả bảng.

## Luật
- Không nhắn tin, kết bạn, gửi email, comment thay Linh. Nháp tin nhắn thì để Linh gửi.
- Không cào Facebook/LinkedIn bằng script; chỉ đọc trang công khai qua tìm kiếm hoặc dữ liệu Linh dán.
- Chỉ lưu thông tin công khai về KOL (chức danh, chủ đề, link hồ sơ công khai). Không lưu số điện thoại, email cá nhân.
- Mỗi DN/KOL phải có `nguon`. Chưa mở được trang gốc thì `chua_xac_minh: true`.
- Giai đoạn CRM chỉ đổi bằng `congdong.py mark` (sửa trong xlsx sẽ bị ghi đè).
- Lịch: `dang-ky-lich-chay.ps1` đăng ký một lịch "LINHX Radar" 7:30 mỗi sáng; bước 2 chạy khi Linh mở Claude hoặc routine hằng tuần.
