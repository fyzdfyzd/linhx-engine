# Schema dữ liệu LAB029

## Bản ghi hiện tượng (`01-hien-tuong.jsonl`, mỗi dòng một JSON)
| Trường | Bắt buộc | Ý nghĩa |
|---|---|---|
| `id` | có | duy nhất, có tiền tố nguồn: `sub:`, `subp:`, `med:`, `linkedin:`, `facebook:`, `podcast-vn:`... |
| `nguon` | có | `substack`, `medium`, `linkedin`, `facebook`, `threads`, `x`, `youtube`, `tiktok`, `spiderum`, `podcast`, `sach`, `bao`... |
| `thi_truong` | có | `quoc-te` hoặc `vn` |
| `loai` | có | `bai` (một bài, video, post) hoặc `kenh` (bản tin, trang, kênh, cuốn sách, podcast) |
| `tieu_de` | có | tít bài, tên kênh |
| `url` | có | link bằng chứng |
| `mo_ta` | | phụ đề, mô tả kênh, đoạn đầu bài |
| `tac_gia`, `tac_gia_id`, `kenh`, `kenh_id` | | |
| `ngay` | | `YYYY-MM-DD` ngày đăng |
| `the` | | danh sách tag, chủ đề bảng xếp hạng |
| `hang` | | chuỗi hạng, ví dụ `business/paid#3 apple-vn#12` |
| `bac_tra_phi` | | ví dụ `Thousands of paid subscribers` |
| `so_do` | | `like`, `comment`, `share`, `clap`, `view`, `subscriber`, `follower` (số nguyên) |
| `ngay_quet` | | tự điền khi nhập |
| `tt` | | tự tính khi nhập: tương tác quy đổi (chỉ so trong cùng nguồn) |

Tương tác quy đổi: Medium `clap + 5×comment`; Substack `like + 5×comment + 10×restack`; nguồn khác `like + 5×comment + 10×share + clap + 0,01×view`.

## Cụm nhu cầu (`02-cum.json`, Claude viết)
```json
{"cum": [{
  "id": "C1",
  "ten": "Tuổi trung niên và lão hoá",
  "nhu_cau": "một câu bằng lời người đọc",
  "noi_dau": ["lời độc giả", "giải pháp đã thất bại", "khoảnh khắc kích hoạt"],
  "bang_chung": ["tít bài (số đo)", "kênh (số người theo)"],
  "the": ["aging", "midlife"],
  "tu_khoa_en": ["getting older", "over 50"],
  "tu_khoa_vi": ["trung niên", "tuổi 50"],
  "chuyen_giao": 0.8,
  "ly_do_chuyen_giao": "một câu"
}]}
```
Khớp cụm: bài khớp nếu có tag trong `the`, hoặc tít/mô tả chứa từ khoá (so theo ranh giới từ). Văn bản tiếng Việt có dấu thì so có dấu; không dấu thì so bỏ dấu.

## Tệp ra
- `02-tin-hieu.json`: `nguon{}`, `tag[]` (chỉ số cầu/cung), `bai_vuot[]`, `nho_ma_no[]`.
- `02-nhu-cau.json`: mỗi cụm `so_bai`, `so_tac_gia`, `chi_so_cau_cung`, `so_bai_vuot`, `so_bai_nho_ma_no`, `top_bai`, `top_tac_gia`, `top_kenh`.
- `04-quy-mo.json`: `so_kenh`, `tong_nguoi_theo`, `so_kenh_tra_phi`, `bac_tra_phi`, `tang_truong_28_ngay`, `cau_nguon`.
- `05-viet-nam.json`: `do_phu_du_lieu`, mỗi cụm `phu_vn` và `nen_tang{ten: {muc, so_khop, lon_nhat[]}}`.
- `06-khoang-trong.json`: `ban_nhap`, `xep_hang[]`.
