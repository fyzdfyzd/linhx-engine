---
name: minh-hoa-y
description: Khi Linh cần hình minh hoạ cho một ý (bài viết, slide, post), dùng kho minh hoạ ý tưởng để đề xuất 3 cơ chế × 2 phong cách, viết ý hình cụ thể và prompt sẵn để sinh ảnh.
---
# Minh hoạ một ý (M8)

Đầu vào: một câu ý ("người trẻ kiệt sức vì so sánh trên mạng"), nơi dùng (`dung_de`), tỉ lệ khung nếu có.

1. Rút ý về một mâu thuẫn hoặc một chân lý ngắn (≤ 12 chữ).
2. Chọn 3 cơ chế trong `tu-dien-y-tuong.json` hợp nhất. Với mỗi cơ chế viết **ý hình** cụ thể, vẽ được, không cần chữ (vd `dao-vai`: "điện thoại dắt người đi dạo").
3. Với mỗi ý hình, chọn 2 thẻ phong cách trong `KHO/phong-cach/` (hoặc `the-phong-cach/mau-the/` khi kho chưa có) có `co_che_hop` chứa cơ chế đó và `khi_nao_dung` hợp nơi dùng.
4. Ghép prompt: thay `{y_tuong}` bằng ý hình, thêm `negative`, `ti_le_khung`.
5. Trả bảng 3 × 2: ý hình, phong cách, prompt, 1 dòng "vì sao hợp". Đánh dấu phương án Claude khuyên.
6. Nếu cùng ý đã có thẻ ảnh tham khảo trong `KHO/anh/the-anh.jsonl` (tìm theo `chu_de`, `co_che`), đưa 1-2 link để Linh xem cách người khác làm, và nhắc: tránh bắt chước bố cục cụ thể của một tác phẩm.

Dùng kèm: LAB025 `linhx-viet-bai` (minh hoạ bài), LAB027 `linhx-deck` (slide 1 ý).
