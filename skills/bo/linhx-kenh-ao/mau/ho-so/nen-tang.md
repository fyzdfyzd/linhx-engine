# Nền tảng

Chỉ số chính: đăng qua **Postiz** (API chính thức) · hộp thư và số liệu qua **Graph API Meta** · chạy thử dùng adapter `thu` (`--thu`).

`khung` là [giờ, hạng ưu tiên]. `thu_dang` là thứ trong tuần được đăng (0 = thứ Hai).

```json
{
 "facebook": {"dang_adapter": "postiz", "hop_thu_adapter": "meta", "postiz_url": "http://127.0.0.1:5000",
              "postiz_integration_id": "DIEN-SAU", "postiz_provider": "facebook", "do_dai_toi_da": 3000,
              "adapter_bat_nhan_ai": false, "khung": [["20:00", "P1"]], "thu_dang": [0, 2, 4, 6]},
 "tiktok": {"dang_adapter": "postiz", "hop_thu_adapter": "thu", "postiz_url": "http://127.0.0.1:5000",
            "postiz_integration_id": "DIEN-SAU", "postiz_provider": "tiktok", "do_dai_toi_da": 2200,
            "adapter_bat_nhan_ai": true, "khung": [["12:00", "P2"]], "thu_dang": [1, 3, 5]}
}
```
