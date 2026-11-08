# Nhánh landing page

Nền: `web-thiet-ke` LAB058 (Linh chốt 20/10). Khác LAB058: thêm chấm mù, kiểm đầu cuối bằng Playwright, đi trọn đường mua.

## Tham chiếu
land-book.com, lapa.ninja, godly.website, onepagelove.com, saaslandingpage.com; app: mobbin.com. Ngành chiêm tinh, tự hiểu bản thân: Co–Star, The Pattern, Sanctuary, Chani, Nebula, Moonly; Việt: Lịch Việt, AI Tử Vi (xem LAB101). Tải ảnh chụp trang vào `tham-chieu/` + link + "học:".

## Học người thắng (theo Appllama, 2/11)
- Chọn **5 trang thắng** theo doanh thu, lượt tải, đánh giá và độ hợp đề, không chỉ theo đẹp. Đi **trọn hành trình** từng trang (vào → hiểu → tin → giá → trả tiền), chụp mọi màn, lưu `tham-chieu/<ten>/` theo thứ tự.
- Ghi `MAU-HINH.md` 3 cột: điều mọi trang thắng đều làm (bắt buộc có), điều chỉ trang giỏi nhất làm (lợi thế), điều cả bọn làm dở (**khe hở của mình**).
- Sửa trang có sẵn: gọi tên **3 lỗi nặng nhất** trước, rồi mới tìm tham chiếu nhắm vào 3 lỗi đó. Tìm 2 kiểu: theo tên khối ("bảng giá", "hero") và theo cảm giác ("tối, yên, một con số lớn"); lấy 30 + 30, chọn 5–8, nói vì sao.
- Từ tham chiếu viết **đặc tả kiểm được bằng ảnh chụp** (bố cục, thứ tự, nút, nhịp khoảng cách, vai màu), không phải moodboard.
- Thư viện tham chiếu có MCP: Mobbin, Refero (có cả trang web), Appllama (app di động); không có thì land-book, godly, lapa.

## Đề bài landing có thêm
- Việc khách cần làm (JTBD) bằng một câu; hành động chính duy nhất (CTA) và số bước tới khi trả tiền.
- Nguồn khách đến (TikTok, Zalo, QR in) → khách đến bằng điện thoại 360 px là mặc định.
- Câu khách hay hỏi trước khi mua (từ TINH-HUONG, bình luận thật).

## Dựng
- HTML thật từ `tokens.css`, mobile-first 360 px, chữ thân ≥16 px, nút ≥44 px, font đủ dấu.
- Khối chuẩn: hero (lời hứa + CTA), chứng cứ (mẫu kết quả thật, lời người dùng), cách hoạt động 3 bước, giá, câu hỏi, CTA cuối. Bỏ khối nào không trả lời câu hỏi của khách.
- **Ảnh sản phẩm trong hero**: dựng giao diện sản phẩm giản lược bằng code (theo stageshow, MIT, React: cửa sổ/điện thoại, cắt chéo ra mép, chữ thật chỉ ở kết quả, phần còn lại là vạch), không chụp màn hình dán vào thẻ. Có bản hẹp riêng cho cột điện thoại 358 px, thiết kế lại chứ không bóp nhỏ. Chạy được thì có thể dùng thẳng kit stageshow.
  - Bài học thử A/B 2/11: (1) khung thiết bị theo nơi khách thật dùng; khách CTS đến từ TikTok/Zalo nên hero là **điện thoại**, không phải cửa sổ trình duyệt Mac. (2) stageshow gỡ được mùi AI (tím, lấp lánh, thẻ đóng hộp) nhưng nếu thiếu token brand thì trôi về xám SaaS, phạm lỗi **nhạt**; luôn nạp token và tinh thần brand ở bước Look trước khi dựng.
- Ảnh: ảnh chụp sản phẩm thật (màn hình kết quả, bản in) trước ảnh AI. Không dùng ảnh AI "cô gái nhìn trời sao".
- Không sửa repo sản phẩm. Làm trong thư mục việc; giao đội dev bằng đề sửa + HTML một file.

## Kiểm đầu cuối (Playwright, ghi `kiem/do.json`)
- Đo hộp chữ bằng DOM như film.mjs của stageshow: chữ cách mép thẻ/khối < 8 px (`sat-mep`), hai khối chữ chạm nhau (`cham`), nút bị cắt bởi khung (`bi-cat`) đều là lỗi không bao giờ "cố ý"; ghi số lỗi vào do.json.
- Chụp 360, 390, 768, 1280; `scrollWidth <= innerWidth` ở mọi khổ.
- Đi trọn: vào trang → bấm CTA → tới bước trả tiền (QR) → đếm số lần chạm; mục tiêu ≤3.
- Lighthouse mobile: hiệu năng ≥80, truy cập ≥90; axe 0 lỗi nặng.
- Đi 3 đường như khách mới: đường suôn, đường hoài nghi (bỏ qua mọi thứ bỏ được), đường phá (nhập sai, mạng mất, bấm quay lại sau khi trả tiền).
- **Xong khi** đặt cạnh 3 tham chiếu tốt nhất mà không khối nào kém hơn khối tương ứng của họ.
- Đọc 5 giây: đưa ảnh màn đầu cho người chấm, hỏi "trang bán gì, giá bao nhiêu, bấm đâu". Đúng cả 3 mới đạt.
