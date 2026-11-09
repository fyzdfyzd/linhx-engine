---
name: world-lore
description: "Dùng khi dựng lorebook (world info) cho một IP để học cấu trúc hoặc cho world gốc của Linh: tách địa danh, phe, hệ sức mạnh, luật thế giới, sinh vật, vật phẩm, sự kiện thành mục có từ khoá, kiểm mâu thuẫn, xuất SillyTavern world info và ghi chú Obsidian."
---
# Lorebook (M5)

1. Tạo `data/lore/<ip>.json`: mảng mục theo `../../schemas/lore.schema.json`.
   - `loai`: địa danh | phe | hệ sức mạnh | luật thế giới | sinh vật | vật phẩm | sự kiện.
   - `keys`: từ khoá kích hoạt, key đầu là tên hiển thị; thêm tên gốc/tên tiếng Anh làm key phụ.
   - `noi_dung`: 2-4 câu **tự viết**, nói chức năng của mục trong thế giới (nó tạo xung đột gì, luật gì), không chép wiki.
   - `nguon`: link (Fandom, Bangumi, Wikidata). Chữ Fandom là CC BY-SA, trích thì ngắn và ghi nguồn.
   - `lien_quan`: id các mục liên quan. Mục luật nền đặt `"constant": true` để luôn bật.
   - Lorebook mẫu 15-25 mục: đủ 7 loại, ưu tiên luật thế giới + hệ sức mạnh + phe.
2. Kiểm: `python scripts/lore.py kiem --lore data/lore/<ip>.json`
   - Lỗi (dừng xuất): thiếu trường, `loai` ngoài danh sách, trùng id, trùng key trong cùng IP, `lien_quan` trỏ tới mục không có.
   - Cảnh báo: số câu ngoài 2-4, thiếu nguồn, mục mồ côi (không liên kết, không ai trỏ tới, key không được nhắc trong mục khác).
3. Xuất: `python scripts/lore.py xuat --lore data/lore/<ip>.json --st output/lore/<ip>.st.json --md output/lore/<ip>`
   - `.st.json`: nhập thẳng vào SillyTavern (World Info, Import). Luật thế giới và hệ sức mạnh có `order` cao hơn để model đọc nền trước.
   - Thư mục Markdown: mỗi mục một ghi chú có `[[liên kết]]` và `_index.md` theo loại.
4. Từ lorebook mẫu rút ra "hạt giống world" gốc: tên tạm, tiền đề 3 câu, 3 phe, 1 hệ sức mạnh/luật, 3 vai nhân vật (lấy archetype từ thẻ nhân vật), ghi học cấu trúc nào từ IP nào. Hạt giống không dùng tên, nhân vật, địa danh của IP khác.

Luật: lorebook IP người khác chỉ để học cấu trúc, không đưa vào sản phẩm. Lorebook world của ta dùng cùng định dạng, `ip` là tên hạt giống.
