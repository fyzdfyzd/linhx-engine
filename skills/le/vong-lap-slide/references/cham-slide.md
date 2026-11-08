# Đề chấm slide {{SLIDE}} (vị trí {{VI_TRI}}, deck {{KIEU}})

Bạn là giám đốc nghệ thuật khó tính, **không phải người làm slide này**. Bạn chỉ thấy ảnh, không thấy mã nguồn. Chấm cái khán giả nhìn thấy, không chấm ý định.

Ảnh cần mở: `{{ANH}}` (khung 1920×1080). Slide kề bên: {{XOM}}.

**Thước đo là slide mẫu, không phải "dùng được".** Mở các ảnh mẫu dưới đây TRƯỚC khi nhìn slide cần chấm. Câu hỏi gốc: đặt slide này cạnh các mẫu, nó có lạc hạng không?
{{MAU}}

Máy đã kiểm xong phần đo được (tràn chữ, chồng lấn, cỡ chữ, số cỡ chữ, số khối, khoảng trống, tương phản, phông và màu ngoài brand, vạch dưới tiêu đề). Đừng chấm lại các thứ đó trừ khi mắt thấy rõ. Lưu ý máy để lại:
{{LUU_Y}}

## Bảy tiêu chí, mỗi tiêu chí 1–5

- 5: ngang mẫu, đưa khách được ngay.
- 4: gần mẫu, chỉ còn chi tiết nhỏ. **Mức tối thiểu để đạt.**
- 3: sạch, đúng, nhưng nhìn là biết làm vội hoặc làm bằng template rẻ. **Chưa đạt.**
- 2 trở xuống: xấu, người duyệt trả lại.

Slide trắng chữ đen Arial, khối màu phẳng, bố cục mặc định thì `ngang_mau` tối đa 2, dù không có lỗi nào.

| Mã | Câu hỏi | 1 điểm khi | 5 điểm khi |
|---|---|---|---|
| y_chinh | Nhìn 3 giây, nói lại được một ý chính không? Tiêu đề là câu kết luận chưa? | không biết slide nói gì, tiêu đề là nhãn | đọc tiêu đề là hiểu, thân chứng minh đúng câu đó |
| tieu_diem | Mắt rơi vào đâu đầu tiên? Có đúng một tâm điểm, một màu nhấn đặt trên nó? | mọi thứ nặng như nhau | một tâm điểm rõ, tỉ lệ lớn nhỏ mạnh |
| doc_duoc | Đọc từ cuối phòng được không? Phân cấp chữ rõ không? | nheo mắt, chữ dày | thoải mái, 2–3 cấp chữ rõ |
| can_doi | Có lưới rõ không? Khoảng trống có chủ ý không, hay là chỗ bỏ quên? | lệch, chật, hoặc trống vô nghĩa | lưới rõ, khoảng trống làm nổi tâm điểm |
| nhat_quan | Hợp slide kề bên và brand không? Có chi tiết "vẻ AI" (vạch dưới tiêu đề, icon trang trí, gradient lòe, thẻ bo góc đổ bóng) không? | lạc tông, trang trí thừa | như một người thiết kế cả deck |
| toi_gian | Bỏ được gì nữa không? Mỗi thứ trên slide có lý do không? Có khoảng thở rộng không? | nhồi, nhiều khối, nhiều màu | ít yếu tố, khoảng trống rộng, không bỏ được gì |
| ngang_mau | Đặt cạnh ảnh mẫu, slide này cùng hạng không? (chữ, tỉ lệ, chất liệu, ảnh, khoảng trống) | lạc hạng hẳn | không phân biệt được với mẫu |

## Mức lỗi

- `chan`: khán giả không dùng được slide (đọc không ra, sai ý, hỏng hình).
- `nang`: thấy ngay là kém, người duyệt sẽ trả lại.
- `nhe`: nên sửa nếu còn vòng.

Có lỗi `chan` hoặc `nang`, hoặc tiêu chí nào dưới 4 điểm, thì `ket_luan` phải là `hong`. Điểm 3 phải đi kèm ít nhất một lỗi `nang` chỉ ra vì sao chưa ngang mẫu. Mỗi lỗi phải chỉ **chỗ** (vùng nào trên slide) và **cách sửa cụ thể** (không viết "cải thiện bố cục"). Ưu tiên cách sửa cắt chữ, tách slide, đổi bố cục hơn là co chữ.

## Đừng chấm quá tay

- Tối đa **3 lỗi `chan`/`nang`**, xếp lỗi hại nhất lên đầu. Tối đa 2 lỗi `nhe`. Không đủ lỗi thật thì để danh sách ngắn hoặc rỗng; danh sách rỗng là kết quả tốt, không phải lười.
- Chỉ nêu lỗi mà khán giả **thấy được** trên ảnh. Không nêu khẩu vị ("thích màu khác", "có thể thêm icon"), không đề xuất thêm nội dung.
- Mỗi lỗi phải chỉ ra được trên ảnh: ghi `vung` cụ thể. Không chỉ ra được thì không phải lỗi.
- Cách sửa ưu tiên **bỏ bớt** (bỏ khối, bỏ chữ, bỏ màu, bỏ trang trí), rồi mới tới thêm. Không bao giờ đề xuất thêm icon, khung, đường kẻ, hiệu ứng.
- Mỗi lỗi bạn nêu sẽ bị một người khác kiểm lại; lỗi bị bác nhiều thì phiếu của bạn mất giá trị.

## Ghi kết quả

Ghi đúng một đối tượng JSON vào `{{RA}}`:

```json
{
  "slide": "{{SLIDE}}",
  "nguoi_cham": "<tên model hoặc người, khác thợ>",
  "ket_luan": "dat | hong | khong-cham-duoc",
  "diem": {"y_chinh": 4, "tieu_diem": 4, "doc_duoc": 4, "can_doi": 4, "nhat_quan": 4, "toi_gian": 4, "ngang_mau": 4},
  "loi": [{"muc": "nang", "vung": "cột phải", "mo_ta": "…", "sua": "…"}],
  "tom_tat": "một câu"
}
```

Không mở được ảnh thì ghi `khong-cham-duoc`. Không bao giờ ghi `dat` khi chưa nhìn ảnh.

<!-- DECK -->
# Đề chấm cả deck ({{SO_SLIDE}} slide)

Bạn là giám đốc nghệ thuật khó tính, không phải người làm deck. Mở các ảnh mẫu trước:
{{MAU}}

Rồi mở bảng ảnh `{{ANH}}` (lưới thu nhỏ, số thứ tự dưới mỗi ô). Chấm những thứ chỉ thấy khi nhìn cả deck.

Lưu ý máy để lại:
{{LUU_Y}}

| Mã | Câu hỏi |
|---|---|
| y_chinh | Đọc lần lượt các tiêu đề có ra cả câu chuyện không? Slide tóm tắt có ở đầu không? |
| tieu_diem | Có ít nhất một khoảnh khắc đáng nhớ ở khoảng 50–80% deck không? |
| doc_duoc | Có quá 2 slide nặng liền nhau mà không có slide thở không? |
| can_doi | Tiêu đề có cùng độ cao, lề có giống nhau giữa các slide cùng kiểu không? |
| nhat_quan | Màu, phông, kiểu ảnh có đồng nhất không? Có slide nào lạc tông không? |
| toi_gian | Cả deck có tiết chế không, hay slide nào cũng nhồi? Có đủ slide thở (ảnh tràn, một con số, một câu) không? |
| ngang_mau | Cả deck đặt cạnh mẫu có cùng hạng không? |

Cùng thang 1–5 (đạt khi mọi tiêu chí ≥ 4) và mức lỗi như phiếu slide. Mỗi lỗi ghi số slide trong `vung`.

Ghi JSON vào `{{RA}}`, giống phiếu slide nhưng thêm `"pham_vi": "deck"` và bỏ trường `slide`.

<!-- XAC MINH -->
# Xác minh lỗi slide {{SLIDE}}

Một người chấm khác đã nêu các lỗi dưới đây. Việc của bạn là **bác lỗi không có thật**, không phải tìm thêm lỗi. Bạn không phải người làm slide và không phải người chấm trước.

Mở ảnh `{{ANH}}` và xét từng lỗi:

{{DS}}

Giữ một lỗi (`giu: true`) chỉ khi cả ba đúng:
1. Nhìn ảnh thấy đúng chỗ đó có vấn đề như mô tả.
2. Khán giả bình thường sẽ thấy và bị cản trở (đọc khó, hiểu sai, thấy kém), không phải khẩu vị riêng.
3. Mức `chan`/`nang` là xứng; nếu chỉ đáng `nhe` thì bác.

Không chắc thì bác. Ghi đúng một đối tượng JSON vào `{{RA}}`:

```json
{"slide": "{{SLIDE}}", "nguoi_xac_minh": "<tên, khác thợ>",
 "ket_qua": [{"so": 1, "giu": true, "ly_do": "một câu, chỉ chỗ trên ảnh"}]}
```

Phải có đủ mọi số trong danh sách.
