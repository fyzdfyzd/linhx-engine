---
tieu_de: Quy chuẩn dự án tự chạy (agy làm, Claude canh)
loai: he
trang_thai: dang-chay
cap_nhat: 2026-11-08
nguon: [nguon/2026-10-30-QUY-CHUAN-DU-AN-TU-CHAY.md]
---
# Quy chuẩn dự án tự chạy

**Một câu:** mọi repo sản phẩm theo cùng một khung: features-dotN.json khoá, nghiệm thu do Claude viết, agy làm phiếu, bộ điều phối 20 phút trên máy cty, Claude chấm DAT/CHUA_DAT.

## Khung
- `AGENTS.md` cho agy, `CLAUDE.md` cho Claude (vai người canh, không viết tính năng).
- `features-dotN.json` + `.khoa` (khoá bằng `scripts/cong_kiem.py khoa` sau khi Linh duyệt). `tests/nghiem-thu/` thợ không được đụng.
- Phiếu ≤ 40 phút, đo bằng trung vị phút trong `.canh/VONG.md`. Cấm ước lượng ngày/tuần. Ghi `phu_thuoc` để chạy song song.
- Kết luận ở `.canh/TRANG-THAI.md`: dòng đầu `DAT` hoặc `CHUA_DAT`, tối đa 10 điểm có file:dòng.
- Chấm CHUA_DAT ngay nếu: diff đụng nghiệm thu hay `*.khoa`, test bị skip, module import module khác, có bí mật, báo `passes:true` mà cong_kiem trượt.
- Mọi lệnh agy trên máy cty chạy ẩn (qua `chay-an.vbs`), không mở console.
- Token agy đo được: ~250k vào, ~34k ra mỗi phiếu.

## Repo đang theo khung
`fyzdfyzd/chiemtinhso`, `fyzdfyzd/mayquet`, `fyzdfyzd/linhx-engine` (đợt 1).

## Liên quan
[[loi-engine]] [[du-an-chiem-tinh-so]] [[du-an-may-quet]] [[he-may-va-tai-khoan]]
