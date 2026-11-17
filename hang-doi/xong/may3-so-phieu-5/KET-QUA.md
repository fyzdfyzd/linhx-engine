model: mac-dinh
phieu: may3-so-phieu-5
may: may-3
trang_thai: xong
tep_doi: (khong)
drive: (khong)
phut: 9.71
token: vao=133991 ra=16180

**Kết luận: ĐƯỢC (lên 5 phiếu song song).**
- **CPU**: AMD Ryzen 7 5800X (8 nhân, 16 luồng); ổ D: trống 282.86 GB.
- **RAM**: Tổng 63.91 GB, trống lúc đo 52.74 GB.
- **RAM mỗi phiếu**: 2 `agy` (197.2 MB, 204.7 MB WS), 1 `node` (101.7 MB WS) → ~0.2 GB/phiếu nền (ước ~5 GB/phiếu kèm test + Playwright).
- **Tính N**: `min(5, floor((63.91-6)/5), floor(16/3)) = min(5, 11, 5) = 5`.
- **Cũ → mới (CÓ SỬA)**: [tho.env](file:///D:/linhx/hang-doi/runner/tho.env) (UTF-8 không BOM): `LINHX_SO_PHIEU` `1 → 5`, `LINHX_RAM_TOI_THIEU_GB` `1.5 → 3` (do `N=5 > 1`, không restart runner).
- **Sau 2 phút**: [tho.log](file:///D:/linhx/hang-doi/runner/tho.log) dòng cuối `04:28:52 nhan may3-so-phieu-5 khac may-3` (tiến trình `--mot-lan` giữ khoá đến khi phiếu đang chạy xong mới nạp `so_phieu=5`). Nhật ký: [tien-do.log](file:///D:/linhx/nhat-ky/may3-so-phieu-5/tien-do.log).
