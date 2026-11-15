# Thẻ thủ pháp (`the-thu-phap`)

Mỗi tác phẩm sau khi đo và đọc xong đều được chưng cất thành các **thẻ thủ pháp** lưu ở định dạng JSON Lines (`thu-phap/thu-phap.jsonl`, mỗi dòng 1 object JSON độc lập) để tái sử dụng khi sáng tạo hoặc dựng lại tác phẩm mới.

Schema máy đọc được đặt tại: `the-thu-phap.schema.json`.

---

## 1. Các trường bắt buộc

Mỗi thẻ thủ pháp **bắt buộc** có đủ 7 trường sau (không trường nào được rỗng):

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| `ten` | `string` | Tên ngắn gọn, gợi nhớ ngay thủ pháp (3–12 từ). |
| `loai` | `string` | Nhóm thủ pháp (ví dụ: `bo_cuc`, `anh_sang`, `mau_sac`, `khong_gian`, `chat_lieu`, `chu`, `nhip`, `bieu_tuong`, `cau_truc`). |
| `moc` | `string \| array \| object` | Mốc bằng chứng trong tác phẩm gốc (với ảnh: toạ độ chuẩn hoá `[x, y]` `0..1` hoặc ô lưới `A1..C3`; với video: giây/shot; với văn bản: chương/đoạn). |
| `mo_ta` | `string` | Thủ pháp vận hành như thế nào trên chính tác phẩm gốc (kèm số đo hoặc chi tiết quan sát được). |
| `cach_lam` | `string` | Hướng dẫn thực hành từng bước để áp dụng lại thủ pháp này khi chụp, thiết kế hoặc viết prompt. |
| `khi_dung` | `string` | Ngữ cảnh, mục tiêu truyền thông hoặc cảm xúc phù hợp để dùng (và khi nào nên tránh). |
| `nguon` | `string` | Tên file hoặc định danh tác phẩm gốc nơi rút ra thẻ. |

Các trường tuỳ chọn có thể bổ sung: `id` (`string`), `tu_khoa` (`array<string>`), `chi_so_do` (`object` trích các số đo liên quan từ `do.json`).

---

## 2. Quy tắc chất lượng thẻ

1. **Neo vào bằng chứng**: `mo_ta` phải khớp với vùng `moc` và không mâu thuẫn số đo trong `do.json` (ví dụ: không gọi là `low-key` nếu `tong.trung_binh > 0.65`).
2. **Tái sử dụng được**: `cach_lam` phải viết ở mức thao tác cụ thể (tỉ lệ diện tích màu, vị trí đặt chủ thể trên lưới 1/3, hướng nguồn sáng, độ chênh sắc độ tiền/hậu cảnh), không chép lại tên riêng của nhân vật trong ảnh gốc.
3. **Đúng chuẩn JSONL**: mỗi thẻ nằm gọn trên 1 dòng UTF-8, kiểm hợp lệ bằng `the-thu-phap.schema.json`.

---

## 3. Ví dụ 1 dòng JSONL chuẩn

```jsonl
{"ten": "Điểm nhấn nóng lệch giao điểm 1/3 trên nền lạnh trầm", "loai": "mau_sac", "moc": {"luoi": "B3", "xy": [0.66, 0.38]}, "mo_ta": "Nền xanh than tối chiếm ~78% diện tích (low-key, TB độ sáng 0.21) đẩy cụm ánh sáng vàng cam ấm (~9% diện tích) tại giao điểm 1/3 bên phải thành điểm hút mắt số 1.", "cach_lam": "Giữ 75-85% khung hình ở dải màu lạnh độ sáng thấp (<0.25); đặt chủ thể hoặc nguồn sáng ấm bão hoà cao chiếm 5-12% diện tích đúng giao điểm 1/3 (B1/B3).", "khi_dung": "Dùng cho keyframe MV cao trào nội tâm, poster sự kiện đêm hoặc cảnh cần gom thị giác tức thì vào một nhân vật đơn độc.", "nguon": "002_002.2s_rai_goc.jpg"}
```
