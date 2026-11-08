# linhx-audit v0.1

Brand audit và social content audit, dựng theo kiến trúc claude-seo (AgriciDaniel, MIT): skill điều phối `audit` → skill `audit-brand`, `audit-social` → 5 agent chạy song song → `scripts/audit.py` đo 0 token → `audit-data.json` + `BAO-CAO.md` → mốc để so trôi.

Cài: chép thư mục này vào `~/.claude/plugins/` (hoặc `D:\LINHX\SKILLS`), hoặc gọi thẳng script.

```
python scripts/audit.py tu-kiem                                    # 11/11 XANH trên data/mau (brand giả lập)
python scripts/audit.py social bai.csv --brand brand.json -o ra/
python scripts/audit.py nhat-quan kenh.json --brand brand.json -o ra/
python scripts/audit.py tong-hop ra/ --loai brand
python scripts/audit.py moc ra/   ;   python scripts/audit.py so-sanh ra-moi/ --moc ra/moc.json
```

brand.json dùng khuôn LAB043, thêm khối `social` (nhip_tuan, er_chuan, tru_cot). Xem `data/mau/brand.json`.
Gọi lại: linhx-onbrand (LAB043) cho nhận diện, linhx-brand-check (LAB036) cho hiện diện AI, linhx-bien-tap (LAB049) cho văn máy (danh sách AP-xx chép rút gọn vào script).
Chỉ dùng thư viện chuẩn Python.
