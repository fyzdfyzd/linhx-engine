# Đề mẫu đã chạy thật

Hai đề dưới đây chạy trên Argon ngày 17/10/2026 (LAB046). Đề quét rộng ngắn (khoảng 2,5 KB) và đề dài đệ quy (khoảng 8 KB).

## Đề quét rộng (LAB046 L1)
```
Bạn là nhà nghiên cứu thị trường. Nhiệm vụ: quét rộng thị trường **sản phẩm/dịch vụ "báo cáo hoặc tư vấn cá nhân hoá"**: khách đưa thông tin về bản thân (hoặc doanh nghiệp), nhận lại một báo cáo/bản đọc/lời khuyên làm riêng cho họ. Bao gồm cả huyền học (chiêm tinh, tử vi, tarot…), tâm lý (trắc nghiệm tính cách…), chuyên môn (da, màu, dáng, dinh dưỡng, gen, học tập, tài chính…) và báo cáo doanh nghiệp (brand, digital, SEO…).

**Lăng kính của phiên này:** L1. Chợ đang bán: thứ gì đang được bán dưới dạng "báo cáo / bản đọc / phân tích cá nhân" — Etsy, Fiverr, Gumroad, Upwork, Shopee, TikTok Shop, Lazada, Kmong (Hàn), Coconala (Nhật), Taobao/闲鱼

Đã biết sẵn (đừng chỉ lặp lại, hãy tìm thêm ngoài danh sách này): chiêm tinh, tarot, thần số học, tử vi, Kinh Dịch, bát tự, MBTI/16 kiểu, Enneagram, Big Five, DISC, Holland, chỉ tay, nhân tướng, nhóm máu, soi da, personal color, phối đồ, gen, InBody, brand GEO, SEO, hiện diện số.

**Yêu cầu:**
1. Tìm **ít nhất 40 thị trường/sản phẩm con**, ưu tiên cái lạ, đang có người trả tiền thật. Mỗi dòng phải có ít nhất một ví dụ đang bán (tên + URL thật).
2. Ghi rõ cái nào **chưa có hoặc mới manh nha ở Việt Nam**.
3. Không bịa URL, không bịa số. Số không có nguồn ghi `chua-kiem`.

**Đầu ra: một file `L1.md` gồm đúng 3 phần:**

### Phần 1. Bảng thị trường (markdown, đúng các cột sau, mỗi dòng một sản phẩm con)
| ten | mo_ta_1_dong | dau_vao | kieu_tinh (D tất định / Q trắc nghiệm / V ảnh / M đo-crawl / L chuyên gia-LLM) | dau_ra_dinh_dang | nguoi_mua | gia_tham_khao (kèm tiền tệ) | vi_du_dang_ban (tên + URL) | quoc_gia | quy_mo_hoac_tin_hieu (số + nguồn hoặc chua-kiem) | co_o_VN (co / manh-nha / chua) | rui_ro (pháp lý, dữ liệu nhạy cảm, y tế, mê tín) |

### Phần 2. Năm phát hiện bất ngờ
5 gạch đầu dòng: thị trường hoặc cách bán mà người làm báo cáo chiêm tinh ở Việt Nam ít khả năng biết, kèm lý do nó đáng chú ý.

### Phần 3. Nguồn
Danh sách mọi URL đã dùng, mỗi dòng: URL — đã mở được hay chỉ thấy trên kết quả tìm kiếm.

Viết tiếng Việt, tên riêng giữ nguyên.
```

## Đề dài đệ quy (LAB046 kho diễn giải chiêm tinh)
```
NHIỆM VỤ DÀI (chạy nhiều giờ, được chia nhiều lượt): DỰNG KHO DIỄN GIẢI CHIÊM TINH CÓ GHI NGUỒN, PHỦ MỌI "THỰC THỂ" CHIÊM TINH

Bạn có một máy làm việc riêng với Python và công cụ tìm, duyệt web. Hãy dùng thật: mở trang, đọc sitemap, chạy script, dựng SQLite, tự kiểm, đóng gói. Không hỏi lại tôi giữa chừng; chỗ nào phải chọn thì tự chọn hợp lý, ghi lý do vào NHAT-KY.md.

## Mục tiêu
Kho này là nền chất lượng cho report engine chiêm tinh của tôi: mỗi "thực thể" chiêm tinh (ví dụ Mặt Trời ở Bạch Dương, Sao Kim ở nhà 7, Mặt Trăng vuông Sao Thổ, cung nhà 10 ở Ma Kết, chủ nhà 7 ở nhà 10, Sao Mộc quá cảnh nhà 2…) phải có NHIỀU diễn giải từ NHIỀU nguồn, ghi nguồn rõ, để engine đối chiếu, tìm điểm đồng thuận và viết báo cáo có căn cứ. Chất lượng quan trọng hơn số lượng.


## Thực tế máy của bạn (đã đo ở lượt trước)
Bash trong máy KHÔNG ra được mạng (curl, pip, npm bị chặn) và không cài thêm được thư viện. Hãy lấy trang web bằng công cụ tìm kiếm và duyệt web của bạn, lưu nội dung đọc được vào file, rồi xử lý bằng Python có sẵn (sqlite3, pandas, Jinja2). Kiểm thử bằng `unittest` (không có pytest), không tạo file trùng tên thư viện.
Mọi đoạn viết (tom_y_vi, mô tả) phải là câu trọn vẹn: TUYỆT ĐỐI không cắt theo số chữ hay số ký tự; script tự kiểm mỗi đoạn kết thúc bằng dấu câu và báo số đoạn vi phạm.

## Luật nguồn và bản quyền (bắt buộc)
- Đọc robots.txt từng trang; không crawl phần bị cấm; tối đa 1 yêu cầu/giây/tên miền; không đăng nhập, không vượt paywall, không tải sách lậu.
- Văn bản có bản quyền: KHÔNG lưu toàn văn. Chỉ lưu: URL, tiêu đề, tác giả nếu có, một trích đoạn ngắn tối đa 40 từ trong ngoặc kép, và phần TÓM Ý viết lại bằng lời mình.
- Văn bản phạm vi công cộng (ví dụ sách chiêm tinh xuất bản trước 1930 trên Project Gutenberg, sacred-texts, Internet Archive có ghi public domain): được lưu toàn văn đoạn liên quan, ghi rõ giấy phép.
- Không bịa URL hay nội dung. Mỗi dòng diễn giải phải có URL đã thật sự mở được.

## Bước 1. Danh mục thực thể (bắt đầu từ cafeastrology.com)
1. Đọc sitemap/mục lục cafeastrology.com, lập danh sách mọi loại thực thể họ có diễn giải.
2. Chuẩn hoá thành bảng `entity_types` và `entities` với mã ổn định dạng `<boi_canh>.<loai>.<thanh_phan…>`, ví dụ:
   - `natal.planet_sign.venus.libra`, `natal.planet_house.mars.h10`, `natal.aspect.moon.square.saturn`,
   - `natal.house_cusp_sign.h7.aries`, `natal.ruler_in_house.h7.h10`, `natal.angle_sign.asc.leo`,
   - `transit.planet_house.jupiter.h2`, `transit.aspect.saturn.conjunct.sun`,
   - `synastry.aspect.venus.trine.mars`, `synastry.planet_house.moon.h4`, `composite.planet_sign…`, `progressed.moon_sign…`, `solar_return…`,
   - và các loại khác: retrograde, node/Lilith/Chiron/tiểu hành tinh (Ceres, Pallas, Juno, Vesta, Eris…), Part of Fortune, Vertex, mô hình bản đồ (grand trine, T-square, yod, stellium…), phân bố nguyên tố/tính chất, decan, độ (biểu tượng Sabian), sao cố định, pha Mặt Trăng lúc sinh, nhật/nguyệt thực.
3. Sinh tổ hợp đầy đủ bằng script (hành tinh × cung, hành tinh × nhà, cặp hành tinh × góc chiếu chính và phụ…). Bảng `entities` có cột: id, boi_canh, loai, thanh_phan (JSON), ten_en, ten_vi, uu_tien (1 = cốt lõi natal, 2 = transit/synastry, 3 = hiếm).

## Bước 2. Tìm trang diễn giải cho từng thực thể
1. Bắt đầu với 15–30 nguồn tiếng Anh lớn (ví dụ cafeastrology, astro.com/Astrodienst bài miễn phí, astrostyle, astrolibrary, astrotheme, astro-seek, astrology.com, horoscope.com, alabe, Skyscript cho chiêm tinh cổ điển) cộng sách phạm vi công cộng (Alan Leo, Sepharial, Raphael… nếu đúng là public domain) và nguồn tiếng Việt.
2. Với mỗi nguồn, tìm cấu trúc URL (sitemap, mục lục) để ánh xạ thẳng thực thể → URL, thay vì tìm kiếm từng cái.
3. Ghi bảng `sources` (id, ten_mien, kieu: web/sach/forum, ngon_ngu, truong_phai: hien_dai/tam_ly/co_dien/vedic, giay_phep, robots_ok, chat_luong 1–5 kèm lý do) và `pages` (url, source_id, entity_id, http_status, ngay_lay).

## Bước 3. Lặp đệ quy (lăn cầu tuyết) đến khi bão hoà
Bước 1–2–3 là một VÒNG LẶP, không phải chạy một lần:
- Mỗi trang đã đọc có thể làm lộ ra (a) loại thực thể mới hoặc thực thể mới chưa có trong danh mục, (b) nguồn mới được dẫn tới, (c) cách đặt URL mới của nguồn cũ. Thêm (a) vào `entities` với `moi=1, vong=N`; (b) vào `sources` với `de_cu=1, vong=N`; (c) vào ghi chú nguồn.
- Vòng N+1: sinh lại tổ hợp cho loại thực thể mới, chạy lại bước 2 cho nguồn mới có chất lượng ≥ 3 và cho thực thể mới trên mọi nguồn cũ.
- Dừng khi một vòng tìm ra dưới 5% thực thể mới và dưới 3 nguồn mới đạt chất lượng ≥ 3, hoặc hết thời gian. Ghi bảng `vong_lap` (vong, so_thuc_the_moi, so_nguon_moi, so_dien_giai_them, gio_bat_dau, gio_ket_thuc) để thấy độ bão hoà.
- Ghi `PHAT-HIEN.md`: loại thực thể và nguồn nào mới tìm ra ở vòng nào.

## Bước 4. Kho diễn giải chất lượng cao (SQLite `kho_dien_giai.db`)
Bảng `interpretations`: id, entity_id, source_id, url, tieu_de, tac_gia, ngon_ngu, trich_doan (≤ 40 từ, trong ngoặc kép), tom_y_vi (60–150 chữ tiếng Việt, viết lại bằng lời mình, giữ đúng ý nguồn), tu_khoa (5–10 từ khoá), chu_de (tính cách / tình yêu / sự nghiệp / tiền / sức khoẻ tinh thần / gia đình / tâm linh), sac_thai (tích cực / thách thức / trung tính), toan_van (chỉ khi public domain), giay_phep, ngay_lay.
Chất lượng (bắt buộc làm và có log):
- Bỏ trùng: cùng nguồn sao chép lại nhau (so độ giống văn bản) thì đánh dấu `trung_voi`.
- Bảng `consensus`: với mỗi thực thể có ≥ 3 nguồn, gom từ khoá chung, ghi `y_dong_thuan` (ý nhiều nguồn cùng nói) và `y_bat_dong` (ý trái nhau) bằng tiếng Việt.
- Bảng `coverage`: mỗi thực thể có bao nhiêu nguồn; báo cáo phủ theo loại (ví dụ planet_sign 100% có ≥ 3 nguồn).
- Lấy mẫu ngẫu nhiên 30 dòng, tự đối chiếu lại với trang gốc xem tóm ý có đúng không, ghi tỷ lệ đúng vào `KIEM-CHAT-LUONG.md`.
- Không có câu doạ, phán số phận, chẩn đoán y khoa trong `tom_y_vi`.
Thứ tự ưu tiên: hết ưu tiên 1 (natal planet_sign, planet_house, aspect chính, angle_sign, house_cusp_sign) rồi mới tới 2, 3.

## Bước 5. Đóng gói
- `kho_dien_giai.db` + CSV cho từng bảng + `SCHEMA.md` (giải thích bảng, mã thực thể, cách truy vấn mẫu).
- `TIEN-DO.md` sau mỗi bước và zip checkpoint `kho-buoc-N.zip`.
- `BAO-CAO-PHU.md`: số thực thể theo loại, số nguồn, số diễn giải, bảng phủ, 10 thực thể còn thiếu nguồn nhất.
- Nếu chưa xong toàn bộ: `TIEP-THEO.md` ghi đang dừng ở đâu, loại thực thể/nguồn nào còn lại, để lượt sau chạy tiếp từ đó (lượt sau tôi sẽ đính kèm zip này).
- Cuối cùng đóng `kho-dien-giai-FULL.zip`, đưa link tải, và trả lời tôi 10 dòng: đã phủ được bao nhiêu, nguồn nào tốt nhất, chỗ nào chưa làm được và vì sao.

Tự kiểm: mọi số trong báo cáo phải do script đếm từ DB (in log). Không tạo file trùng tên thư viện Python. Viết tiếng Việt cho tài liệu; tên cột và mã không dấu.
```
