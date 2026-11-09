---
name: cafebiz-radar
description: Phân tích tin công nghệ cho mảng công nghệ CafeBiz theo quy chuẩn News Listening (mã trend T01–T13, nước và hướng lan, khoảng trống VN, độ hút, 6 chỉ số H M V G R C, góc viết). Dùng khi được giao gom cụm hoặc chấm thẻ từ data/CAFEBIZ_TECH_RADAR/RUNS/<ngày>/. Trả JSON đúng schema được đưa, không tự tính điểm tổng.
metadata:
  version: "0.1.0"
---

# Skill: phân tích radar tin công nghệ CafeBiz

Đọc trước: `docs/radar/quy-chuan.md` (bản gốc của quy chuẩn). Ví dụ một bản tin đạt chuẩn: `docs/radar/fixtures/2026-10-14-chrome.md`.

Độc giả: người đi làm 25–45 tuổi ở đô thị, quản lý và kinh doanh. Nhóm TA: A chủ doanh nghiệp · B nhà đầu tư · C người đi làm trẻ · D giới công nghệ, startup. CafeBiz không đua tin gadget; góc là tiền, việc làm, doanh nghiệp, cộng góc Đông Á.

## Lượt 1: gom cụm (đầu vào `items.jsonl`, đầu ra theo `clusters.schema.json`)

1. Bỏ tin quảng cáo, khuyến mãi, game thuần, giải trí, tin chính trị nhạy cảm (chủ quyền, quan hệ quốc tế).
2. Gộp các tin cùng một sự kiện thành một cụm. Một cụm có thể nhiều nguồn, nhiều nước.
3. Gắn **một** mã trend chính (T01–T13, hoặc TNEW kèm tên đề xuất) và tối đa một mã phụ.
4. Ghi `origin` (nước gốc) và `spread` (nơi đang lan), dùng mã nước của quy chuẩn.
5. Viết 2–4 cụm từ khoá **tiếng Việt** để tìm xem báo VN đã đưa chưa (tên công ty, sản phẩm theo cách báo VN quen viết).
6. Giữ tối đa 30 cụm, ưu tiên AI & robot và Trung Nhật Hàn.

## Lượt 2: chấm thẻ (đầu vào `clusters.json` + `vn_gap.json`, đầu ra theo `cards.schema.json`)

Với mỗi cụm:
- **Tóm tắt** 2 câu bằng lời mình. Không chép nguyên văn bài nguồn. Tên riêng Trung Nhật Hàn viết theo cách báo VN quen dùng.
- **Vì sao quan trọng** 1–2 câu, nói bằng tiền, việc làm, doanh nghiệp.
- **Khoảng trống VN**: chỉ dựa vào `vn_gap.json`. Không có bài nào: `trong`. Có tin dịch ngắn: `moi`. Nhiều báo: `nhieu`. Quá nhiều, không còn góc: `bao_hoa`. Cụm không có trong `vn_gap.json` (chưa tìm được): `chua_kiem`. Ghi góc còn trống cụ thể.
- **Độ hút ở VN**: Cao / Vừa / Thấp, một câu lý do, nhóm TA.
- **Con số đắt**: 1–3 con số **có trong nguồn**, ưu tiên tiền, việc làm, quy mô. Không có thì để mảng rỗng và ghi "chưa có số liệu, cần tìm" vào `verify`. Không bịa, không ước tính.
- **Chỉ số** 0–5: H độ nóng, M động lượng trend, V liên quan VN, G khoảng trống VN (phải khớp mức khoảng trống: trong 5, moi 3–4, nhieu 1–2, bao_hoa 0; chua_kiem tự chấm nhưng ghi vào `verify`), R sức hút TA. C là chữ A/B/C theo nguồn tốt nhất của cụm (A báo/đơn vị chính thức, B chuyên ngành, C mạng xã hội, tin đồn).
- **Đề xuất bài**: tin hay chuyên môn, persona P1 Bản tin nhanh · P2 Chuyên gia AI & Robot · P3 Người quan sát Đông Á · P4 Góc nhìn nhà đầu tư, tiêu đề nháp tiếng Việt.
- **Cần kiểm chứng**: điều chưa chắc. Nguồn loại C luôn ghi "chưa kiểm chứng".

Không tính điểm tổng, không xếp hạng, không quyết định Viết ngay. Code làm việc đó.

## Luật
- Chỉ trả JSON đúng schema, không thêm lời.
- Không mở mạng, không ghi file, không chạy lệnh.
- Tiếng Việt có dấu, câu ngắn.
