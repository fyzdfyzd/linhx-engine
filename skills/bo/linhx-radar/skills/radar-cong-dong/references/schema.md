# Schema nhập kho (`congdong.py seed <file>`)

Một file JSON có 3 mảng; thiếu mảng nào cũng được. Gộp theo tên (không dấu, bỏ "Công ty CP/TNHH/Tập đoàn/Việt Nam"), nên nhập lại không sinh bản trùng.

```json
{
  "communities": [{
    "id": "csmo", "ten": "CSMO Vietnam", "loai": "hiep_hoi|cong_dong|to_chuc_su_kien|media|giai_thuong",
    "linh_vuc": "", "mo_ta": "", "don_vi_dung_sau": "", "quy_mo": "",
    "kenh": {"web": "", "facebook": "", "fb_group": "", "youtube": "", "linkedin": "", "tiktok": "", "zalo": "", "newsletter": "", "khac": []},
    "su_kien": [{"ten": "", "nam": 2026, "thoi_gian": "", "dia_diem": "", "chu_de": ""}],
    "chu_de_dang_noi": [""], "pain_point": [""], "ho_da_co": [""],
    "mo_hinh_doanh_thu": "", "nguon": ["url"], "uu_tien": 0
  }],
  "companies": [{
    "ten": "", "nganh": "", "website": "", "cong_dong": ["csmo"], "vai_tro": "Nhà tài trợ Vàng",
    "nam": [2026], "ghi_chu": "alias: Tên ngắn, Tên khác", "nguon": ["url"], "chua_xac_minh": false
  }],
  "kols": [{
    "ten": "", "chuc_danh": "", "to_chuc": "", "cong_dong": ["vsmcamp"],
    "vai_tro": "dien_gia|co_van|giam_khao|sang_lap|chu_tich|host", "nam": [2025],
    "chu_de": "", "linkedin": "", "facebook": "", "nguon": ["url"], "chua_xac_minh": false
  }]
}
```

- `uu_tien` (0–10): cộng điểm cho mọi DN/KOL thuộc cộng đồng đó.
- `ghi_chu` của DN có thể chứa `alias: A, B` để dò tên trong tin.
- `chua_xac_minh: true` khi chỉ thấy ở trang tổng hợp, chưa mở trang chính thức (trừ 5 điểm).

# Nguồn quét (`config/sources.json`)

| kind | Trường | Ghi chú |
|---|---|---|
| `gnews` | `query` | Google News RSS tiếng Việt. Dùng dấu ngoặc kép cho tên riêng. |
| `youtube` | `channel_id` hoặc `url` (@handle) | Lần đầu script tự đổi @handle ra channel_id và ghi lại file. |
| `rss` | `url` | Blog, báo có RSS. |
| `page` | `url`, `label` | Trang nhà tài trợ / diễn giả / agenda. Lần đầu lưu mốc, lần sau báo phần chữ mới. |

Mọi nguồn có `community` (id cộng đồng) và `active`. Nguồn chết: `"active": false` + `_note`, không xoá.
Facebook, LinkedIn, TikTok không quét bằng script (cần đăng nhập, vi phạm điều khoản nếu cào); phần đó skill chạy bằng WebSearch hoặc Linh dán tay.
