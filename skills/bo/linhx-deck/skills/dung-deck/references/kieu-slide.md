# 14 kiểu slide của `10-deck.json` (v0.3)

```json
{
  "ten": "Tên deck",
  "brand": "sakedemy",
  "khach": "Tên khách",
  "chan_trang": "Sakedemy · Đề xuất cho <khách> · 10/2026",
  "logo_ta": "logo/ta-….png", "logo_khach": "logo/khach-….png",
  "slides": [ { "id": "bia", "kieu": "bia", "...": "..." } ]
}
```

Trường chung mọi slide: `id` (chữ, số, `-`, `_`), `kieu`, `phan` (nhãn mục, ví dụ "01 | BỐI CẢNH"), `tieu_de`, `ghi_chu` (lời nói), `bang_chung` (["BC01"]), `nguon` (chữ chân trang, không viết "Nguồn:"), `minh_hoa` (true nếu số là minh hoạ), `so_la_nhan` (true nếu số trên slide chỉ là số thứ tự, không phải số liệu; ngày tháng không cần cờ này), `anh` ({tep, y_tuong, ti_le, mo_ta}).

## Mỗi slide nội dung: một điểm, một hình thức, một tiêu điểm

Mọi slide trừ `bia`, `chuong`, `muc-luc`, `ket` **bắt buộc**:

- `diem_chinh`: điều duy nhất người nghe phải nhớ, ≤ 12 chữ. Hiện to, đậm, ngay dưới tiêu điểm. Tiêu đề là kết luận; `diem_chinh` là câu mắt dừng lại.
- `hinh_thuc`: cách chứng minh `diem_chinh`, phải khớp kiểu slide:

| hinh_thuc | kiểu slide | tiêu điểm (`data-hero`) |
|---|---|---|
| `bieu-do` | `bieu-do` | cột/điểm `bieu_do.diem_nhan`, màu nhấn; còn lại xám |
| `bang` | `bang` | dòng `dong_nhan` nền nhấn nhạt, chữ đậm; dòng khác chữ phụ |
| `so-lon` | `so-lon` | số `so_chinh` rất to màu nhấn; số khác nhỏ, xám |
| `so-do` | `lo-trinh`, `so-sanh`, `the`, `doi-ngu` | khối `nhan_manh` (so-sanh: phương án `khuyen_nghi`) nền tối, to hơn |
| `minh-hoa` | `hai-cot`, `khang-dinh` | ảnh nền + câu chính |
| `cau` | chỉ `tom-tat`, `khang-dinh` | khung kết luận / câu lớn |

- Hai khối trở lên mà không chỉ ra khối chính (`nhan_manh`, `dong_nhan`, `so_chinh`, `khuyen_nghi`) thì `kiem-deck` chặn: mắt bị chia.
- Màu nhấn chỉ dùng ở tiêu điểm. Chữ phụ màu trầm, nhỏ hơn.
- Slide toàn chữ (ý gạch đầu dòng) không phải hình thức: đổi thành biểu đồ, bảng, số lớn, sơ đồ hoặc minh hoạ.

## Bảng kiểu

| kieu | Trường riêng | Bố cục mặc định (thư viện `du-lieu/bo-cuc`) |
|---|---|---|
| `bia` | `phu_de`, `khach`, `ngay`, `anh` (ảnh nền 16:9) | `toan-trang`: ảnh tràn slide, chữ ở phía trống, lớp phủ chuyển sắc |
| `tom-tat` | `diem` [3–5 câu], `diem_chinh` (khung kết luận lên đầu) | `nen-mem` |
| `muc-luc` | `muc` [tên phần] | `nen-mem` |
| `chuong` | `so` ("01"), `phu_de`, `anh` (ảnh nền 16:9) | `toan-trang` |
| `khang-dinh` | `phu`, `anh` (tuỳ) | không ảnh: `nen-mem` (tông theo cảm xúc ở 10b); có ảnh: `toan-trang` |
| `the` | `muc` [{`tieu_de`, `noi_dung`, `so` tuỳ}], `nhan_manh` | `the-nhan-manh` |
| `bang` | `cot` [..], `dong` [[..]], `dong_nhan` | `bang-nhan-dong` |
| `so-lon` | `so` [{`gia_tri`, `nhan`}], `so_chinh` | `so-lon-hero` |
| `so-sanh` | `phuong_an` [{`ten`, `mo_ta`, `diem` [..], `khuyen_nghi`}] | `the-nhan-manh` |
| `lo-trinh` | `buoc` [{`moc`, `ten`, `viec`}], `nhan_manh` | `the-nhan-manh` |
| `hai-cot` | `diem` [..], `anh` | `nua-trang`: ảnh tràn mép phải, mép trái tan vào nền |
| `doi-ngu` | `nguoi` [{`ten`, `vai`, `bang_chung_nang_luc`}], `nhan_manh` | `the-nhan-manh` |
| `bieu-do` | `bieu_do` {`loai`, `nhan`, `chuoi`, `diem_nhan`, `don_vi`}, `phu` | `bieu-do-hero` |
| `ket` | `buoc_tiep` [..], `hanh_dong_chinh` (một việc), `lien_he`, `anh` (tuỳ, mặc định dùng ảnh bìa) | `toan-trang` |

### `bieu_do`

```json
"bieu_do": {"loai": "cot", "nhan": ["2024", "2025", "2026"], "chuoi": [{"ten": "Doanh thu", "gia_tri": [12, 18, 31]}],
            "diem_nhan": 2, "don_vi": "tỷ"}
```

- `loai`: `cot` (cột), `ngang` (thanh ngang, xếp hạng), `chong` (thanh chồng 100%: nhiều `chuoi`), `thac` (thác nước: phần đóng góp cộng dồn), `duong` (đường, đánh dấu một điểm). **Không** tròn, không 3D.
- Nhãn số ghi thẳng trên cột, không chú giải, không lưới, cột bắt đầu từ 0.
- Mọi số trong biểu đồ trỏ `bang_chung` (BCxx) và có dòng `nguon`.

Chữ trong mọi trường được phép dùng `<b>`, `<i>`, `<br>`; ký tự khác được thoát tự động.
