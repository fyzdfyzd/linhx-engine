# Schema một mẫu (mau/<id>.json)

```json
{
  "id": "con-cai-nit",
  "nguon": {"link": null, "nen_tang": "tiktok", "ngay": "2022-06",
            "so_lieu": {"view": null, "share": null, "luu": null, "binh_luan": null},
            "loai_mau": "viral | doi-chung | dan-gian | tu-dat"},
  "noi_dung": "transcript hoặc mô tả ngắn",
  "gtvh": {
    "so": ["kịch bản A", "kịch bản B"],
    "so_loai": "xem enum SO_LOAI",
    "lm": "xem enum LM",
    "si": "tình huống, đồ vật, nhân vật",
    "ta": "ai bị cười, hoặc null",
    "ns": "xem enum NS",
    "la": {"thu_phap": "xem enum LA", "goc": "chữ gốc", "ket_qua": "chữ sau biến đổi"}
  },
  "vi_sao_hai": {"truong_phai": ["lech-ky-vong"], "ky_vong": "", "cu_be": "", "vi_sao_lanh": ""},
  "vi_sao_lan": {"stepps": {"S": 0, "T": 0, "E": 0, "P": 0, "Pr": 0, "St": 0},
                 "khuon_dien": "câu khuôn, ô trống viết [X]; null nếu không điền được",
                 "giay_chot": null},
  "ghi_chu_hinh": "",
  "do_chac": 2
}
```

STEPPS chấm 0 đến 2: S vốn xã hội, T gợi nhắc hằng ngày, E kích thích cảm xúc, P công khai, Pr thực dụng, St câu chuyện.

## Enum
- **SO_LOAI**: `that-gia`, `binh-thuong-bat-thuong`, `co-khong`, `sang-hen`, `tuc-thanh`, `nghiem-dua`, `nguoi-lon-tre-con`, `ta-ho`.
- **LM** (rút gọn từ danh sách cơ chế logic của Attardo 2002): `dao-vai`, `suy-dien-sai`, `ghep-nham-nghia`, `nghia-den`, `phong-dai`, `cu-the-hoa`, `ha-cap`, `nhai-giong`, `lap-leo-thang`, `doi-cho`, `tu-mau-thuan`, `lech-ngu-vuc`.
- **NS**: `ke-chuyen`, `hoi-dap`, `doi-thoai`, `mot-cau`, `hinh`, `clip-dien`, `chu-tren-hinh`.
- **LA**: `khong`, `noi-lai`, `dong-am`, `gieo-van`, `gieo-van-viet-anh`, `viet-hoa-phien-am`, `bien-am-genz`, `che-thanh-ngu`, `che-loi-bai-hat`, `giong-vung-mien`, `tron-viet-anh`, `lap-am`.
- **truong_phai**: `lech-ky-vong`, `vi-pham-lanh-tinh`, `uu-the`, `giai-toa`.

## Đề mổ (dán cho Gemini kèm schema)
> Bạn mổ một content hài tiếng Việt. Trả đúng một JSON theo schema, chỉ dùng giá trị enum đã cho. "so" là hai cách hiểu chồng nhau, viết cụ thể bằng lời. "khuon_dien" là câu khuôn mà người khác có thể điền chuyện của mình vào, viết ô trống là [X]; nếu content không điền được (chỉ buồn cười một lần) thì để null. Không biết nguồn hoặc số liệu thì để null, không đoán. Ghi do_chac 1 (đoán) đến 3 (chắc).
