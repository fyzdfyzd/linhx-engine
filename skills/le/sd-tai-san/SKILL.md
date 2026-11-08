---
name: sd-tai-san
description: Bước 3 Flow Pack. Lập thư viện tài sản cho một tập: đoạn khoá nhân vật và style bằng tiếng Anh, prompt ảnh neo nhân vật, ảnh bối cảnh không người, prompt keyframe. Dùng sau khi kịch bản tập đã duyệt.
---

# sd-tai-san: nhân vật, bối cảnh, ảnh cần tạo

**Đầu vào:** bible, `<tap>-kich-ban.md`.
**Đầu ra:** các trường `khoa_phong_cach`, `khoa_cuoi`, `nhan_vat`, `boi_canh`, `anh_can_tao` trong `data/<tap>/<tap>.json` (mẫu: `data/E01/E01.json`).

## Luật nhất quán
1. **Đoạn khoá** (`khoa`): 1 câu tiếng Anh cố định cho mỗi nhân vật (màu lông/da, dấu hiệu nhận dạng, trang phục, đạo cụ). Dán **y nguyên** vào mọi prompt; không diễn đạt lại.
2. `goi_la`: cách gọi chung trong prompt video ("the scrawny grey stray cat"), không dùng tên riêng (Veo không biết tên).
3. **Ảnh neo**: 1 ảnh chính diện toàn thân, nền trơn, cho mỗi nhân vật. Không dùng sheet nhiều góc làm tham chiếu (dễ ra nhiều nhân vật trong một khung).
4. Đổi trang phục = một nhân vật con mới có `khoa` và ảnh neo riêng.
5. **Bối cảnh không có người**, dọc 9:16. Đạo cụ quan trọng tả trong `khoa` của bối cảnh hoặc nhân vật.
6. **Keyframe**: mỗi khối dùng chế độ `frames` cần 1 ảnh khung đầu; prompt keyframe nói rõ "Using the provided images for …" và liệt kê ảnh neo phải gắn (trong `ghi_chu`).
7. `khoa_phong_cach` 1 đoạn, không nhắc tên hãng phim hay nghệ sĩ.

Linh tạo ảnh (bước A của pack) và duyệt ảnh neo trước khi Claude viết keyframe cuối cùng.
