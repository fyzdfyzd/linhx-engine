model: mac-dinh
phieu: ev-hieu-nang-14c-sua-1
may: may-3
trang_thai: xong
tep_doi: (khong)
drive: (khong)
phut: 23.46
token: vao=463829 ra=21468

## KET-QUA

- **dat**: co
- **nhánh / SHA**: `agy/ev-hieu-nang-14b` — `1ca6ea306aa982183bf401d6322e54450bcdc32e` (đã push lên `origin/agy/ev-hieu-nang-14b`)
- **Phạm vi & bảo mật**: chỉ sửa trong `apps/event/` và `bang-chung/ev-hieu-nang-14b/`; đã xác nhận `git diff origin/agy/ev-de-xuat-11..HEAD` không có bí mật mới và không sửa/xoá test cũ.

### Bảng điểm Lighthouse TRƯỚC / SAU (18 trang — chi tiết tại [BANG-DIEM.md](file:///D:/linhx/ifagent-wt/ev-hieu-nang-14b/bang-chung/ev-hieu-nang-14b/BANG-DIEM.md))

| Chế độ | Mốc | Hiệu năng | Trợ năng | Thực hành tốt | SEO |
|---|---|---:|---:|---:|---:|
| **Di động — TRƯỚC** | Trung bình | 97.3 | 94.9 | 99.8 | 97.0 |
| **Di động — TRƯỚC** | Thấp nhất | 78 (`/thu`) | 93 (`/de-xuat`) | 96 (`/khong-co`) | 86 (`/khong-co`) |
| **Di động — SAU** | Trung bình | **98.4** | **100** | **99.8** | **100** |
| **Di động — SAU** | Thấp nhất | **94** (`/play/tiec-cuoi-nam`, `/play/rap-phim-photobooth`) | **100** (mọi trang) | **96** (`/khong-co`) | **100** (mọi trang) |
| **Máy bàn — TRƯỚC** | Trung bình | 97.9 | 94.9 | 99.8 | 97.0 |
| **Máy bàn — TRƯỚC** | Thấp nhất | 83 (`/play/rap-phim-photobooth`) | 93 (`/de-xuat`) | 96 (`/khong-co`) | 86 (`/khong-co`) |
| **Máy bàn — SAU** | Trung bình | **98.2** | **100** | **99.8** | **100** |
|
...[cat bot]...
g.test.js)): **19 pass / 0 fail**
- `de-xuat-slide` ([de-xuat-slide.test.js](file:///D:/linhx/ifagent-wt/ev-hieu-nang-14b/apps/event/test/e2e/de-xuat-slide.test.js)): **7 pass / 0 fail**
- `web-vo` + `web-vo-tk5` + `tao-khung-a`: **18 pass / 0 fail**
- `test:audit` (`sast.js`): **OK (8 rules)**
- `npm test`: **372 pass / 9 fail** (8 case trong `characters-v2.test.js` & `kai-assets.test.js` thiếu kho video `.mp4` ngoài git `IFAGENT-ASSETS` trên `may-3`, 1 case `beta-t030.test.js` do mốc ngày hết hạn `mui-pho`; giữ nguyên test cũ theo luật chung).
