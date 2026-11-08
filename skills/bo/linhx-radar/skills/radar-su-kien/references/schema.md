# Schema JSON của event radar

## Sự kiện (`seed`): `{"events": [ ... ]}`

```json
{
  "id": "vietnam-ai-summit-2026",
  "ten": "Vietnam AI Summit 2026",
  "ngay_bd": "2026-11-20", "ngay_kt": "2026-11-21",
  "thanh_pho": "Hà Nội", "dia_diem": "GEM Center",
  "hinh_thuc": "offline | online | hybrid",
  "linh_vuc": ["ai", "business"],
  "to_chuc": "Đơn vị A; Đơn vị B",
  "url": "https://...", "gia_ve": "miễn phí | 1.500.000đ", "quy_mo": "1.000 khách",
  "chu_de": ["AI agent trong doanh nghiệp", "dữ liệu"],
  "dien_gia": [{"ten": "Nguyễn Văn A", "chuc_danh": "CTO", "to_chuc": "Công ty X"}],
  "tai_tro": [{"ten": "Công ty Y", "hang": "kim cương"}],
  "da_noi": [{"loai": "pain_point", "noi_dung": "...", "nhom": "roi-ai-kho-do", "nguon": "https://bai-tuong-thuat"}],
  "lap_lai": "hằng năm, tháng 11",
  "nguon": ["https://trang-chinh-thuc"],
  "chua_xac_minh": false
}
```
Chỉ biết tháng: `"ngay_bd": "2026-11"` và `chua_xac_minh: true`.

## Hấp thu (`absorb`): một file cho một sự kiện

```json
{
  "event_id": "vietnam-ai-summit-2026",
  "giai_doan": "đã hấp thu",
  "talks": [{
    "tieu_de": "AI agent cho CSKH ngân hàng",
    "dien_gia": [{"ten": "Nguyễn Văn A", "chuc_danh": "CTO", "to_chuc": "Công ty X"}],
    "chu_de": ["ai agent", "cskh"],
    "tom_tat": "3 đến 5 câu",
    "url_video": "https://youtube.com/...",
    "insights": [
      {"loai": "pain_point", "noi_dung": "Doanh nghiệp không đo được ROI của AI", "nhom": "roi-ai-kho-do"},
      {"loai": "solution", "noi_dung": "Pilot một quy trình, đo bằng thời gian xử lý", "nhom": "pilot-mot-quy-trinh"},
      {"loai": "so_lieu", "noi_dung": "Giảm 40% thời gian trả lời", "nhom": "cskh-giam-thoi-gian"}
    ]
  }],
  "insights": [{"loai": "xu_huong", "noi_dung": "...", "nhom": "..."}],
  "danh_gia": [{"ten": "Nguyễn Văn A", "diem": 4.5, "ly_do": "ví dụ thật, có số"}]
}
```
`loai`: `chu_de | pain_point | solution | xu_huong | so_lieu | cau_noi | cong_cu`.
`nhom`: slug không dấu ngắn. **Trước khi đặt nhóm mới, đọc `output/BAN-DO-CHU-DE.md` và dùng lại nhóm đã có nếu cùng ý**; đó là cách bản đồ đếm được "ý này lặp lại ở bao nhiêu sự kiện".
`danh_gia.diem` 1 đến 5: 5 = có ví dụ thật, số liệu, cách làm mang về dùng được; 3 = đúng nhưng chung chung; 1 = bán hàng.

## Giải thưởng (`seed`): `{"awards": [ ... ]}`

```json
{
  "id": "sao-khue-2027", "ten": "Giải thưởng Sao Khuê 2027", "to_chuc": "VINASA",
  "doi_tuong": "doanh_nghiep | ca_nhan | ca_hai",
  "linh_vuc": ["công nghệ", "ai"], "hang_muc": ["Giải pháp AI"],
  "han_nop": "2027-01-31", "mua_nop": "tháng 11 đến tháng 1 hằng năm",
  "le_trao": "2027-04-20", "dia_diem_le_trao": "Hà Nội", "phi_tham_du": "...",
  "uy_tin": 5, "ly_do_uy_tin": "hiệp hội ngành, hội đồng độc lập, 20 năm",
  "tra_phi_de_nhan": false, "url": "https://...", "chu_ky": "hằng năm",
  "nguoi_doat_gan_nhat": [{"ten": "Công ty X", "loai": "doanh_nghiep", "nam": 2026, "hang_muc": "AI"}],
  "nguon": ["https://..."], "chua_xac_minh": false
}
```
Nhãn: `Nộp | Cân nhắc nộp | Theo dõi người thắng | Bỏ`. Giải nghi trả phí bị trừ 30 điểm.
