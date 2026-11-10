# Bộ mẫu ban-hang 0.1.0
Tách từ Nụ Event. Dựng con mới:
```
python workforce/af.py moi <W> --mau ban-hang --ten "<tên bot>" --don-vi "<đơn vị>" --kho skills --skills brand-<don-vi>
```
Sau đó: trả lời D0 (dòng `> `), điền su-that.json, thay `chu/quan-ly/nhan-vien` trong to-chuc.json bằng người thật, thay `<...>` trong thu/*.jsonl bằng sự thật của đơn vị, thêm ≥ 4 ca thật, thêm bản vàng mỗi workflow, rồi `af.py muc <W>`.
Bộ thử ở đây là ca chung (gọi đúng, im đúng, không bịa, không lộ nội bộ); mỗi đơn vị phải thêm ca thật của mình.
