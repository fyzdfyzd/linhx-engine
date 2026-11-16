# TK-1 · Hai hướng giao diện event.ifagent.net
Thiết kế · Chân Cơ · 13/11/2026 · commit `ee69e3a` (bản đầu 348f0be) (nhánh `claude/project-thread-9c61ql`, thư mục `docs/thiet-ke/event-web/`)

## 1. Hai hướng
- **A · Sân khấu**: nền Đêm từ đầu tới cuối. Hero là ảnh tràn khung (kiosk AI). Có một dải Giấy để thở, chứa một câu. Đo trên trang chủ 1440: 5% sáng, 84% tối, 0,4% xanh điện. Trang giải pháp: 1% sáng.
- **B · Sân khấu + Giấy**: hero Đêm chia đôi, bên cạnh có thẻ nhân vật KAI. Các phần đọc, đề xuất và màn doanh nghiệp đặt trên nền Giấy. Đo trên trang chủ 1440: 47% sáng, 44% tối, 0,5% xanh điện. Trang giải pháp: 25% sáng.

**Đề xuất của Thiết kế:** chọn **A cho web công khai**, vì A khớp tỉ lệ Đêm 72% / Giấy 18% của DS. Phần đề xuất (11-thu-5) và các màn doanh nghiệp (20–35) nên lấy cách xử lý Giấy của B, vì phía B2B nằm gần phần thương hiệu ở DS §7. Trang chủ B có 47% sáng, vượt mức Giấy 18%.

## 2. Danh sách màn (mỗi hướng 31 màn)
Ảnh cỡ thật nằm ở `NOP/thiet-ke/anh/<a|b>-<trang>-<rộng>-ee69e3a.png`, khổ 390 và 1440. Trang chủ và phòng demo có thêm khổ 1920. Tổng 128 tấm.
Bảng ghép: `bang-ghep-a-1440.png`, `bang-ghep-a-390.png`, `bang-ghep-b-1440.png`, `bang-ghep-b-390.png`.

| Nhóm | Màn |
|---|---|
| Web | 01 trang chủ (12 khối theo 1-BAN-DO-TRANG), 02 menu điện thoại, 03 giải pháp (AI Photobooth), 04 phòng demo, 05 trang demo (Luna), 06 demo sắp ra mắt |
| Xưởng ý tưởng | 07 đề bài (trống, đã điền), 08 đang nghĩ, 08 ba ý tưởng, 09 hình thử, 10 chạy thử, 11 đề xuất, 11b form lead, 11c form lỗi, 11d đã nhận, 12 trạng thái (lỗi, hết lượt, chờ) |
| Blog | 13 danh sách, 14 bài viết "Agentic Event Technology là gì?" |
| Tạo sự kiện 6 bước | 20 nháp, 21 nhận diện, 22 sự kiện, 23 chữ, 24 xem trước, 25 xuất bản (có link và QR) |
| Agency | 30 đăng ký, 31 đã gửi, 32 nhận lời mời, 33 đặt mật khẩu, 34 danh sách khách hàng, 35 hạn mức gói |

## 3. Tự chấm theo RUBRIC (B/C/U)
| Tiêu chí | A | B | Ghi chú |
|---|---|---|---|
| Chỉ dùng Be Vietnam Pro và Montserrat, không màu ngoài hệ | Đạt | Đạt | Token lấy nguyên từ DS 1.0 (`css/ev.css`) |
| Một nhát cắt 34° mỗi khung | Đạt | Đạt | B bỏ nhát cắt ở hero để không đè lên ảnh |
| Một CTA chính "Thử cho công ty bạn", CTA phụ "Đặt lịch 20 phút" | Đạt | Đạt | |
| 390 không cuộn ngang, vùng chạm ≥ 48px | Đạt | Đạt | Lần chụp cuối không có màn nào cuộn ngang |
| Có dải thở một câu | Đạt | Đạt | |
| Không cắt đầu hay tay người | Đạt | Đạt | Trên điện thoại hero xếp dọc, ảnh 3:2 |
| Không hiện giá, không có case Unikon, đúng luật tên khách | Đạt | Đạt | Gói ghi "Giá: liên hệ"; đề xuất kết bằng "IF Agent sẽ gửi báo giá sau." |
| Chữ trên màn theo 1-BAN-DO-TRANG v1.0 | Đạt | Đạt | |
| Tỉ lệ Đêm/Giấy theo DS | Đạt | Lệch | B có 47% sáng |
| Màn doanh nghiệp: sang, tối giản, không từ kỹ thuật | Đạt | Tốt hơn | B đọc dễ hơn trên nền Giấy |

**Điểm tự chấm: A 8/10, B 7,5/10.** Theo RUBRIC, điểm bị chặn ở 8 khi chưa có video thao tác và ảnh demo thật.

## 4. Còn thiếu (đã biết)
1. **Ảnh bìa 21 demo đang dùng ảnh tạm.** Ảnh tạm gồm ảnh DS đã duyệt, nhân vật có sẵn và ảnh case thật. Yêu cầu tạo ảnh đã ghi ở `NOP/ANH-HANG-CHO.md` nhóm 1 (17 ảnh cần tạo, khung 3:2, 1800×1200), giao Thái Văn Cơ. Khi có ảnh, Thiết kế sẽ thay vào và chụp lại.
2. QR trong mockup chỉ là hình giữ chỗ.
3. Chưa có video thao tác, nên điểm bị chặn ở 8.
4. Thẻ Yên Lam: Quản trị đã chốt giữ hình và ghi tên "Yên Lam, đại sứ AI" (không ghi CSMO, VSMCamp, Đẹp).

## 5. Dựng lại
```
python3 docs/thiet-ke/event-web/sinh-khung.py   # sinh a/ b/
node docs/thiet-ke/event-web/chup.js            # chụp 390/1440/1920, báo CUON NGANG nếu tràn
```

## 6. Lần sửa 1 (ee69e3a), theo CHAM/TK-1-HAI-HUONG-348f0be-cham1.md và NOP/SP-DOC-CHU-TK-1.md
- Chữ theo bản đồ v1.8: bỏ mọi số "21" (S1–S6); thẻ "Yên Lam, đại sứ AI"; "KAI tư vấn sự kiện" nhãn Idea Generation; thứ tự Yên Lam · Emily · Luna · KAI; P1 "Bìa tạp chí AI … cùng Yên Lam"; link chạy thử event.ifagent.net/play/…; nút "Gửi bản PDF qua mail"; 4 câu lỗi chuẩn; "Lead" thành "Liên lạc"; câu bước Nháp mới.
- Nên sửa: thêm nhóm Hội nghị khách hàng (M7–M9) và tên mẫu đúng §4.5; tên công ty hư cấu (Nhà sách Trang Giấy, Trung tâm thương mại Bà Triệu); blog K1 cùng "8 phút đọc"; demo sắp ra mắt liên quan V1, V2 và bài G3; trang Luna liên quan Yên Lam, Emily.
- Giao diện: ở 390 nút "Thử" đầu trang thành nút viền (một nút xanh mỗi khung nhìn); xuất bản có "Tải bộ in A4" và bản xem trước A4; agency dùng "Đang thử / Chính thức", có dòng "Chạy bằng IF Agent" (hạn mức, xem nhanh màn khách); trang chủ A ở 1440 bớt khoảng trống (khoảng cách khối 160 px, cột Idea Adoption có ảnh).
- Bản đồ nhiệt (T1) bắt buộc gen, đã ghi ở ANH-HANG-CHO.md.
- Chụp lại 128 tấm, 0 cuộn ngang. Tấm so 2 hướng cỡ điện thoại: so-sanh-a-b-dien-thoai-ee69e3a.png.
