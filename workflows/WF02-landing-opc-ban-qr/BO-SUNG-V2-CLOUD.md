# WF02 · Bổ sung vòng 2 (cloud, 9/11/2026)

Bổ sung cho `NGHIEN-CUU.md`, không sửa file đó. Có ba phần: sửa chỗ sai, luật (thuế, hoá đơn, dữ liệu cá nhân, quảng cáo, thương mại điện tử) và chạy thử máy đo trên mẫu có sẵn.
Ghi chú cloud trước đó: `/mnt/project-files/WF-CHUAN/WF02-landing-opc-ban-qr/_ghi-chu-cloud.md`.

## 1. Năm điều NGHIEN-CUU.md bỏ sót hoặc ghi sai

1. **Đã có sẵn khuôn thanh toán.** Repo `fyzdfyzd/chiemtinhso` đã chạy đủ các phần mà NGHIEN-CUU gọi là "khoảng trống":
   - `modules/pay/api/router.py`: webhook SePay có kiểm khoá Apikey, chống trùng theo id giao dịch, đối soát hằng ngày `/admin/doi-soat`.
   - `core/vietqr.py`: tự sinh VietQR theo chuẩn EMVCo/Napas, có CRC.
   - `tests/e2e/E01_khach_mua_tron_ven.spec.ts`: đi trọn một lượt mua, giải QR bằng cv2 và kiểm CRC, mở PDF kiểm tên và nơi sinh, quét từ cấm, chụp 3 khổ 360/768/1280, chạy axe.
   - **Việc nên làm**: rút ba phần này thành `khuon/thanh-toan-qr/` và một bộ kiểm dùng chung, không viết lại từ đầu.
2. **Webhook SePay có 4 cách xác thực, không phải một.** Đã đọc tài liệu gốc (mục 5). NGOAI ghi HMAC là đúng nhưng chưa đủ. Code chiemtinhso đang dùng Apikey. Ca kiểm phải viết theo chế độ bảo mật đã chọn cho webhook trong bảng điều khiển SePay; khuyến nghị HMAC vì Apikey không chống sửa dữ liệu. Phát hiện thêm: theo tài liệu, SePay chỉ tính là thành công khi nhận body `{"success": true}`, nhưng webhook chiemtinhso trả `{"status": "ok", ...}` (`modules/pay/models.py:519`). Nếu tài liệu đúng, SePay sẽ gửi lại 7 lần rồi đánh dấu Failed. Chống trùng nên không giao hai lần, nhưng nhật ký SePay sẽ báo lỗi giả. Cần thử một đơn thật để xác nhận.
3. **Khớp đơn chỉ theo số tiền là lỗi, không phải cách dự phòng.** Bản best-practices SePay mà NGOAI dẫn có hai chiến lược 3 và 4: khớp "số tiền + khung giờ ±30 phút" và "chỉ số tiền". Với sản phẩm cùng giá (199.000đ), hai khách chuyển cùng lúc sẽ bị giao nhầm báo cáo, tức là lộ ngày giờ sinh của người này cho người khác. **Luật cho skill**: chỉ khớp theo mã đơn trong nội dung chuyển khoản; không khớp được thì đưa vào hàng chờ kiểm tay.
4. **Ngưỡng ô nhập là "7 ô theo Baymard".** Con số này đúng cho hàng vật lý cần địa chỉ giao. Báo cáo số chỉ cần: họ tên, ngày, giờ, nơi sinh, email (5 ô) và **các ô đồng ý tách riêng**. Ngưỡng đề xuất: ≤ 5 ô nhập + ô đồng ý.
5. **Đối thủ Việt có code mở**: `yukihanatuyethoa-a11y/huyen-so-server` (tử vi, SePay). Đơn lưu trên Google Sheet, khớp đơn bằng `content.includes(maCK)`, không chống trùng. Cách này làm mốc "tối thiểu chạy được", không nên học theo.

## 2. Luật (trích lời kèm link; mọi trích từ nguồn thứ cấp)

Không có trang nào là bản Công báo. thuvienphapluat.vn chặn máy đọc tự động, nên các số điều dưới đây **cần đối chiếu bản gốc** trước khi đưa vào skill như luật cứng.

### 2a. Thuế
| Ý | Trích nguyên văn | Link |
|---|---|---|
| Ngưỡng 1 tỷ/năm, NĐ 141/2026 sửa NĐ 68/2026 | "Sửa đổi cụm từ "500 triệu đồng" thành "01 tỷ đồng" tại Điều 3 (thuế giá trị gia tăng), Điều 4 (thuế thu nhập cá nhân)" | https://tapchicongthuong.vn/chinh-thuc--nang-nguong-chiu-thue-voi-ho-kinh-doanh-len-1-ty-dong-nam--ap-dung-tu-1-1-2026-514336.htm |
| Hiệu lực | "hiệu lực thi hành từ ngày 01/01/2026" | như trên |
| Dưới ngưỡng không nộp GTGT, TNCN (lời bình của MISA, không phải văn bản luật) | "có doanh thu năm từ 1 tỷ đồng trở xuống sẽ không phải nộp thuế giá trị gia tăng và thuế thu nhập cá nhân" | https://amis.misa.vn/269759/nghi-dinh-141-2026-nd-cp/ |
| Việc vẫn phải làm khi dưới ngưỡng (thông báo doanh thu, hạn, mẫu); cách tính và thuế suất khi vượt ngưỡng | **Không tìm thấy** trong các trang đã đọc. Bộ nhớ LAB060 ghi "thông báo doanh thu năm, hạn 31/01, mẫu 01/TKN-CNKD TT 50/2026" nhưng chưa có trích dẫn | cần nguồn |

### 2b. Hoá đơn
| Ý | Trích nguyên văn | Link |
|---|---|---|
| Doanh thu trên 1 tỷ thì phải dùng hoá đơn điện tử | "có doanh thu năm trên 01 tỷ đồng thì phải áp dụng hóa đơn điện tử có mã của cơ quan thuế" | tapchicongthuong (link trên) |
| Loại hoá đơn | "hóa đơn điện tử khởi tạo từ máy tính tiền có kết nối dữ liệu với cơ quan thuế" | như trên |
| Hạn đăng ký | "đăng ký sử dụng hóa đơn điện tử trong thời gian 30 ngày kể từ ngày cuối cùng của kỳ tính thuế" | như trên |
| Sàn khấu trừ thay người bán | sàn "có trách nhiệm khấu trừ, kê khai và nộp thay số thuế đã khấu trừ" | https://thoibaotaichinhvietnam.vn/chinh-thuc-quy-dinh-ho-kinh-doanh-co-doanh-thu-1-ty-dong-tro-len-phai-ap-dung-hoa-don-dien-tu-193181.html |

**Hệ quả cho khuôn**: dưới 1 tỷ thì trang không cần xuất hoá đơn, nhưng sổ doanh thu phải xuất được từ `/admin/doi-soat`. Vượt 1 tỷ thì phải nối hoá đơn điện tử. Khuôn để sẵn một chỗ cắm hoá đơn, mặc định tắt.

### 2c. Bảo vệ dữ liệu cá nhân (Luật 91/2025/QH15, hiệu lực 01/01/2026)
| Ý | Trích nguyên văn | Link |
|---|---|---|
| Định nghĩa dữ liệu nhạy cảm | "Dữ liệu cá nhân nhạy cảm là dữ liệu cá nhân gắn liền với quyền riêng tư của cá nhân" … "thuộc danh mục do Chính phủ ban hành." Danh mục cụ thể **chưa tìm thấy**, nên chưa biết ngày, giờ, nơi sinh có thuộc diện này không | https://hethongphapluat.com/luat-bao-ve-du-lieu-ca-nhan-2025/dieu-2 |
| Đồng ý theo từng mục đích (**bản dự thảo**, Điều 9) | "Thể hiện sự đồng ý đối với từng mục đích"; "Sự im lặng hoặc không phản hồi không được coi là sự đồng ý." | https://hethongphapluat.com/du-thao-luat-bao-ve-du-lieu-ca-nhan/dieu-9 |
| Miễn trừ cho hộ kinh doanh, doanh nghiệp siêu nhỏ (dự thảo, Điều 38) | "không phải thực hiện quy định tại Điều 21, Điều 22 và khoản 2 Điều 33". Miễn trừ này **không áp dụng** nếu "trực tiếp xử lý dữ liệu cá nhân nhạy cảm hoặc xử lý dữ liệu cá nhân của số lượng lớn chủ thể" | https://hethongphapluat.com/du-thao-luat-bao-ve-du-lieu-ca-nhan/dieu-38 |
| Mức phạt (dự thảo, Điều 8) | mua bán dữ liệu "10 lần khoản thu có được"; chuyển ra nước ngoài sai quy định "5% doanh thu"; vi phạm khác "03 tỷ đồng"; cá nhân bị phạt một nửa mức của tổ chức | https://hethongphapluat.com/du-thao-luat-bao-ve-du-lieu-ca-nhan/dieu-8 |
| Dùng dữ liệu cho quảng cáo, pixel (Điều 28) | "Việc xử lý dữ liệu cá nhân của khách hàng để kinh doanh dịch vụ quảng cáo phải được sự đồng ý của khách hàng"; quảng cáo theo hành vi chỉ thu "khi có sự đồng ý của chủ thể dữ liệu cá nhân" | https://lsvn.vn/quy-dinh-ve-bao-ve-du-lieu-ca-nhan-trong-mot-so-hoat-dong-tu-nam-2026-a161847.html |

**Hệ quả cho khuôn**: tách ít nhất 2 ô tích, không tích sẵn: (1) đồng ý cho xử lý dữ liệu sinh để làm báo cáo; (2) nhận tin tiếp thị, ô này không bắt buộc. Ô thứ ba cho bên xử lý nước ngoài (Gemini) nếu có. Pixel chỉ nạp sau khi bấm đồng ý (chiemtinhso đã làm đúng việc này).

### 2d. Thương mại điện tử (Luật 122/2025/QH15, hiệu lực 01/07/2026; NĐ 248/2026 ký 30/6/2026)
| Ý | Trích | Link |
|---|---|---|
| Người bán phải cung cấp thông tin | "từ ngày 1/7/2026, người bán trên nền tảng thương mại điện tử phải cung cấp thông tin" | https://baolaocai.vn/tu-hom-nay-172026-ban-hang-online-khong-the-an-danh-nguoi-ban-can-lam-gi-post902924.html |
| Thông tin công khai của chủ trang | "Tên, địa chỉ trụ sở chính của tổ chức, tên người đại diện theo pháp luật hoặc tên, địa chỉ cư trú của cá nhân;" … "mã số thuế của cá nhân hoặc mã số thuế của hộ kinh doanh." (NĐ 248 Điều 4) | https://hethongphapluat.com/nghi-dinh-248-2026-nd-cp-huong-dan-luat-thuong-mai-dien-tu.html |
| Nghĩa vụ chung của người bán | "Cung cấp thông tin chính xác, đầy đủ; bảo đảm chất lượng hàng hóa, dịch vụ;" (NĐ 248 Điều 6) | như trên |
| Trang tự bán có phải thông báo Bộ Công Thương không | **Chưa rõ**: theo bản tóm tắt NĐ 248, nền tảng bán trực tiếp được tỉnh xác nhận thông báo (Điều 23–24). Chưa đọc nguyên văn | cần luật sư |
| Định danh người bán | Theo tóm tắt NĐ 248 (chưa đọc nguyên văn), định danh áp dụng từ 01/01/2027. Báo Lào Cai thì ghi từ 1/7/2026. **Hai nguồn lệch nhau** | như trên |

**Hệ quả cho khuôn**: chân trang bắt buộc có tên chủ (cá nhân hoặc hộ kinh doanh), địa chỉ, mã số thuế, email, điện thoại. Kèm các link chính sách: bảo mật, điều khoản, hoàn tiền, giải quyết khiếu nại.

### 2e. Quảng cáo (Luật 75/2025/QH15 sửa Luật Quảng cáo, hiệu lực 01/01/2026)
| Ý | Trích | Link |
|---|---|---|
| Người có ảnh hưởng phải kiểm sản phẩm | "Xác minh về độ tin cậy của người quảng cáo; kiểm tra tài liệu liên quan đến sản phẩm, hàng hóa, dịch vụ quảng cáo;" | https://lsvn.vn/tu-2026-nguoi-co-anh-huong-khong-duoc-quang-cao-khi-chua-hieu-ro-san-pham-a159875.html |
| Chưa dùng thì không được giới thiệu | "trường hợp chưa sử dụng hoặc chưa hiểu rõ về sản phẩm, hàng hóa, dịch vụ thì không được giới thiệu về sản phẩm" | như trên |
| Phải báo đang quảng cáo | "Thông báo về việc quảng cáo ngay trước và trong khi thực hiện hoạt động quảng cáo." | như trên |
| Gắn nhãn quảng cáo trên mạng xã hội (luatvietnam diễn giải, dẫn Điều 23 khoản 2 điểm đ, chưa đọc nguyên văn) | "phải có dấu hiệu phân biệt nội dung quảng cáo hoặc nội dung được tài trợ với các nội dung khác" | https://luatvietnam.vn/linh-vuc-khac/diem-moi-cua-luat-quang-cao-sua-doi-2025-883-102813-article.html |

**Hệ quả**: người ảo (Luna Mai…) hay KOL dẫn khách về trang bán phải gắn nhãn quảng cáo. Lời khen trên trang chỉ dùng của người đã mua thật. Ghi chú cho WF07 và WF14: người ảo "chưa dùng sản phẩm" là điểm vướng cần hỏi luật sư.

### Câu cần luật sư xác nhận
1. Ngày, giờ, nơi sinh có thuộc danh mục dữ liệu nhạy cảm không. Nếu có thì hộ kinh doanh mất miễn trừ Điều 38.
2. Trang tự bán một sản phẩm số có phải thông báo với Sở Công Thương hoặc Bộ Công Thương theo NĐ 248 không, hạn bao giờ.
3. Định danh người bán bắt đầu từ 1/7/2026 hay 01/01/2027.
4. Báo cáo chiêm tinh thuộc nhóm "dịch vụ" hay "nội dung số" khi tính thuế lúc vượt 1 tỷ.
5. Người ảo AI làm phễu có bị coi là "người chuyển tải quảng cáo" phải dùng sản phẩm trước không.

## 3. Chạy thử máy đo trên mẫu có sẵn

### 3a. Máy đo QR (`kiem_qr.py`: giải mã ảnh chụp, tách trường VietQR, kiểm CRC)
Script ở `do/kiem_qr.py` (cần `opencv-python-headless`; chạy `python do/kiem_qr.py <ảnh...>`). Chạy trên 6 ảnh chụp có sẵn trong `/mnt/project-files/`:

| Ảnh | Giải được | CRC | Napas | Số tiền | Nội dung CK | Tài khoản |
|---|---|---|---|---|---|---|
| 01-man-qr-natal-360 | có | đúng | đúng | 199000 | CTS849CECF501 | 09***55 |
| 03-qr-360 | có | đúng | đúng | 5000 | CTS9325822837 | 33***30 |
| 04-qr-360 | có | đúng | đúng | 5000 | CTSDA63114F8C | 33***30 |
| 10e-man-qr-hop-doi-top-360 | có | đúng | đúng | 5000 | CTSB65CAFAA80 | 33***30 |
| don-hang-qr | có | đúng | đúng | 5000 | CTSA0B1DF42EF | 33***30 |
| 04-qr-thanh-toan-1280 | **không** | – | – | – | – | – |

Máy đo bắt được ba điều:
- **QR giả trong bản mẫu cũ**: ảnh 1280 (bản mẫu, tài khoản "MB · 0000000000") có hình giống QR nhưng không giải được. Màn này cũng ghi "Bước 4/4", vượt ngưỡng ≤ 3 bước.
- **Hai số tài khoản nhận khác nhau** giữa các lần chụp (09***55 và 33***30). Cần kiểm xem bản chạy thật dùng tài khoản nào. Máy đo nên so tài khoản trong QR với tài khoản cấu hình.
- Giá thử 5.000đ còn nằm trong ảnh, nên máy đo phải so số tiền trong QR với giá trong `features`/bảng giá.

**Ngưỡng đề xuất**: giải được 100%, CRC đúng, Napas `A000000727`, QR động (`01=12`), số tiền trong QR = giá đơn, tài khoản = tài khoản cấu hình, nội dung CK = mã đơn.

### 3b. Quét pháp chế trên code chiemtinhso (commit eebb1bd, 9/11)
- 🔴 **Vẫn còn** lỗi đỏ LAB107 #1: `apps/web/src/components/free-chart-tool.tsx:1054` gửi cứng `dong_y_dieu_khoan: true` từ form lấy lead, khách không tích ô nào.
- 🟡 Vẫn còn LAB107 #7: chân trang `components/store-shell.tsx:419` chỉ có "© 2026 Chiêm Tinh Số · hotro@chiemtinh.vn", thiếu tên chủ, địa chỉ, mã số thuế (xem 2d).
- Quét từ cấm brand: 1 lần chạm, `order-report-reader.tsx:1239`, câu "…không phải định mệnh cố định." Đây là **dương tính giả** vì từ cấm nằm trong câu phủ định. Máy quét cần cho phép phủ định ("không phải …") hoặc có danh sách ngoại lệ.
- **Kết luận**: theo máy đo "0 lỗi đỏ pháp chế" của đề, trang hiện tại **chưa đạt**. Vòng 2 (làm lại trang sản phẩm chiemtinh.vn) phải sửa hai chỗ trên trước.

Không chạy được trên cloud: mở trang sống chiemtinh.vn và chiemtinh.unikon.vn (proxy chặn), Lighthouse, đếm chạm thật. Ba việc này để máy cty.

## 4. Đề xuất sửa skill (bổ sung mục "Sửa vào skill nào")
- Thêm vào `web-thiet-ke` bước 6 (hoặc `thiet-ke` nhánh landing) bộ kiểm `kiem_ban_qr`: kiem_qr.py ở trên, các ca webhook (khoá sai → 401, gửi trùng → giao 1 lần, trả thiếu → không giao, nội dung CK bị ngân hàng đổi dạng → vẫn khớp, không có mã đơn → hàng chờ kiểm tay), và quét pháp chế logic (ô đồng ý không gửi cứng true, ô tách theo mục đích, chân trang đủ định danh).
- Luật cấm: khớp đơn theo số tiền.
- `ra-phap-che`: chưa có skill trong repo. Nên tạo từ LAB107 cộng bảng luật ở mục 2, kèm các câu cần luật sư.

## 5. Đối chiếu cách xác thực webhook SePay (tài liệu gốc, 9/11)
| Ý | Trích | Link |
|---|---|---|
| 4 cách | None, API Key, HMAC-SHA256, OAuth 2.0, chọn riêng cho từng webhook | https://developer.sepay.vn/en/sepay-webhooks/xac-thuc |
| HMAC | header `X-SePay-Signature` "sha256={hex_hash}", `X-SePay-Timestamp`; chuỗi ký "{timestamp}.{raw_body}"; "reject timestamps off by more than 5 minutes" | như trên; https://developer.sepay.vn/en/sepay-webhooks/lap-trinh-webhooks/lap-trinh-webhook-nodejs |
| Apikey | "Authorization: Apikey YOUR_API_KEY"; tài liệu ghi Apikey "doesn't guarantee the data wasn't modified in transit" | https://developer.sepay.vn/en/sepay-webhooks/xac-thuc |
| Phản hồi | "Return HTTP 200 with body {"success": true} within 30 seconds" | https://developer.sepay.vn/en/sepay-webhooks/tich-hop-webhook |
| Gửi lại | khoảng cách 1, 1, 2, 3, 5, 8, 13 phút; tổng 8 lần trong khoảng 33 phút, chỉ khi bật "Auto retry"; chống trùng theo `id` | https://developer.sepay.vn/en/sepay-webhooks/xu-ly-loi |

Sửa lại các ngưỡng: NGHIEN-CUU ghi "lệch giờ > 5 phút" (chỉ đúng với HMAC) và "luôn trả 200" (đúng hơn: trả 200 kèm `{"success": true}` cho mọi giao dịch đã nhận, kể cả gửi trùng; sai khoá thì 401). Bản claudekit ghi "thử lại ~5 giờ", tài liệu gốc ghi khoảng 33 phút. Đây là lý do cần thêm đối soát cuối ngày cộng nút "tôi đã chuyển" kiểm tay.
