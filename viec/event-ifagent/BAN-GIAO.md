# Bàn giao cụm event.ifagent.net sang agy (16/11/2026)
Quản trị mới: thread "Chuyển giao event.ifagent.net sang agy". Luật: LUẬT LÀM VIỆC 16/11 (agy là thợ ở máy 2, Claude ra đề + soi ảnh 1280/360). Đề gốc: DE-BAI.md (Linh đã duyệt 13/11 22:12; hạn 16/11 đã trễ, chờ Linh chốt ngày mới).
Cụm dừng từ 14/11 04:40, không ai đẩy thêm. Mọi SHA dưới đây khớp GitHub lúc 22:55 16/11.

## Nhánh cần gộp (repo fyzdfyzd/ifagent)
| Phần | Nhánh | SHA | Tình trạng |
|---|---|---|---|
| Nền (Phát hành) | claude/project-thread-es2prv | df1e518 | app 1fae081; npm test 353/362 (9 lỗi môi trường) |
| Lõi (Từ Hoảng) | claude/project-thread-en6gul | 935d69ec | gồm 2c1bbf56 + mail TK-5 + khoá đăng nhập; chưa Chấm |
| Trình tạo + agency (Mãn Sủng) | claude/project-thread-939spi | 2e855f45 | ĐẠT 9 |
| Video booth/AR/game (Hứa Chử) | claude/project-thread-2oqsoe | 3682b414 | video booth chờ chấm; AR, vòng quay, game chưa làm |
| Đo lường (Tào Nhân) | claude/project-thread-a9kpr7 | 59938a3e | màn R3, V3, T1, V2; chưa chấm |
| Vỏ web (Trương Liêu) | claude/project-thread-fyw6pv | 51c39a05 | 28 bài, form lead, E2E web-vo 8/8; còn TK-5, OG |
| Nội dung | claude/event-noi-dung | 7c09dd0 | 28/28 bài ĐẠT 9 chữ |
| Xưởng ý tưởng (Tuân Du) | claude/project-thread-9fhyvw | 194e6299 | CHƯA xong: PDF chưa nối route/mail |
| Thiết kế (Chân Cơ) | claude/project-thread-9c61ql | 559a2114 | TK-1..5 ĐẠT 9; khung trang con 50–59 dở |
| Kiểm thử (Điển Vi) | claude/project-thread-cetcxp | 2eeaa29 | bộ nghiệm thu kiem-thu/event/nghiem-thu.mjs v1.7 |
| Bảng ảnh | claude/project-thread-z8w4rl | 46c27f3 | 105 dòng, chưa gen |

## Việc còn lại (thành phiếu agy theo thứ tự)
1. ev-gop-nen-2: gộp lõi, Mãn Sủng, Hứa Chử, Tào Nhân, vỏ web, nội dung vào agy/ev-nen-2 + npm test.
2. ev-chup-nen-2: E2E đủ + ảnh 1280/360 các trang chính → Claude soi.
3. Vỏ web phần còn: TK-5 (404, trang lỗi, thẻ Sắp ra mắt, OG), mail lienhe@ifagent.net, /tao /agency đường gọn.
4. Xưởng ý tưởng: nối PDF tải + mail, /thu nhận ?nguon=yen-lam&ma=… (đang 404, Yên Lam cần).
5. V2 tường ảnh bật sau khi màn Tào Nhân vào nền; AR, vòng quay, game đông người (Hứa Chử).
6. Ảnh: gen 105 dòng bảng ảnh (máy công ty, Claude soi từng lô).
7. Staging stg-event + gói deploy (infra/staging/stg-event/, điền SHA cuối, thêm xoá LinhQuizPro + lệnh A2/A3).

## Bẫy đã biết (đưa vào phiếu)
- Chạy mọi lệnh tiền cảnh; phiếu yl-code-a2-1 chết vì chờ test nền.
- Không force-push; merge thường.
- Không bật V2 trước khi màn tường ảnh vào nền (lộ tên thương hiệu thật).
- 9 lỗi npm test môi trường có sẵn (clip nhân vật, Mùi Phở).
- Seed demo sau deploy: POST /api/admin/su-kien/demo/seed (một lần).

## Cần Linh
- Ngày mới lên staging và event.ifagent.net.
- Duyệt ảnh nền mới khi phiếu 2 xong.
- /bao-mat (nháp) chờ chị Hằng hoặc anh Linh.


---
# Phụ lục A. Bàn giao vỏ web (Trương Liêu)
# Bàn giao · Build · Trương Liêu · vỏ web event.ifagent.net (dừng 04:40 14/11)

**Nhánh:** `claude/project-thread-fyw6pv` @ `51c39a05` (đã push).
- `fa7b9bf3`: vỏ web hướng A gồm trang chủ 12 khối, /giai-phap(+slug), /demo(+slug), /blog 23 bài + /case 5 bài, /mau, /goi, /lien-he, /bao-mat, /quen-toi, 404, sitemap/robots/llms. Form lead gửi /api/kho-lead, có bước 2 bo-sung. Menu trỏ /tao/, chân trang trỏ /agency (302 về /tao/agency.html khi có tệp). Trang cũ giữ ở /cu/home.html và /cu/demo.html. demo.ifagent.net vẫn dùng / và /demo cũ. Tắt vỏ mới bằng WEB_MOI=0.
- `8b99e290`: gộp lõi en6gul f35423f2.
- `51c39a05` (WIP): server/web/og.js (khuôn OG theo TK-5 §4), du-lieu.og(), scripts/web-chup.js.

**Kiểm:**
- test:audit OK.
- npm test: 13 lỗi, trùng y lỗi có sẵn trên lõi en6gul (không có lỗi mới).
- E2E test/e2e/web-vo.test.js 8/8 xanh. site, demo-links, nhan-nguon-lead xanh.
- Bộ test:e2e đầy đủ chưa chạy hết vì dừng giữa chừng.
- Lưu ý cloud: playwright trong node_modules cần chromium-1248, máy có 1243. Chạy bằng PW_CHROMIUM=/opt/pw-browsers/chromium-1243/chrome-linux64/chrome hoặc symlink.

## Việc còn lại (theo thứ tự)
1. Gộp nền mới `claude/project-thread-es2prv` @ 1fae081 (lõi 2c1bbf56) bằng merge, không force-push.
2. **Dừng xưởng tới thứ Hai (Quản trị 13/11):**
   - Mọi lối vào /thu và /de-xuat, cùng nút "Thử cho công ty bạn" (linkThu trong server/web/khuon.js), dẫn tới thẻ/trang "Sắp ra mắt" có form để lại liên lạc. Form giữ đủ nguồn (?nguon=..., kể cả brand-health và diemYeu).
   - 3 demo Idea Generation hiện "Sắp ra mắt". Đề xuất: thêm cờ trong noi-dung/web/demo.json, du-lieu #demo() đọc cờ.
3. **TK-5 (Chân Cơ 659dea8, NOP/thiet-ke/TK-5-MAIL-LOI-OG.md §2–4):**
   - 404: thêm câu phụ "Đường dẫn có thể đã đổi. Bạn về trang chủ hoặc thử ngay cho công ty bạn.", nút **Về trang chủ** (chính) + **Thử cho công ty bạn →**, nhát cắt 34°. Sửa trong trang-phu.js khong().
   - Trang lỗi chung: index.js bọc trangMoi bằng try/catch → 500 với nhãn "Chưa tải được", H1 "Có chút trục trặc. Bạn bấm thử lại nhé.", câu "Nếu vẫn chưa được, bạn quay lại sau ít phút.", nút Thử lại + Về trang chủ.
   - Thẻ "Sắp ra mắt" trong phòng demo, 3 trạng thái (đóng, mở ô email với ô đồng ý để trống "Tôi đồng ý nhận một email báo khi demo mở.", đã gửi "Đã ghi. IF Agent báo bạn khi demo mở."). Lead gửi nhan `demo-cho-<slug>`. Máy nhớ đã gửi (localStorage). Thẻ hiện là <a> trong thanh-phan.js theDemo(), cần đổi thành div .dsoon với link tiêu đề.
   - OG: viết scripts/web-og.js, chụp dsOg() ở 1200×630 JPEG vào public/web/og/<ten>.jpg. Gắn t.og = w.du.og('blog-<slug>' | 'case-<slug>' | 'demo-<slug>') trong blog.js, demo.js. Mặc định của khuon.js head đổi sang og/mac-dinh.jpg SAU KHI đã có tệp.
4. Mail lienhe@ifagent.net (anh Linh chốt) đặt ở cột Liên hệ chân trang và /lien-he.
5. Chụp ảnh so khung (node scripts/web-chup.js), ghép cạnh khung a-*-ee69e3a.png, nộp Chấm.
6. Chạy đủ `npm run test:audit && npm test && npm run test:e2e`, báo SHA cho Quản trị.

## Điểm mở cần người khác chốt
- Chữ demo/giải pháp (6 khối ngoài photobooth), cachThu/oSuKien trong noi-dung/web/*.json là bản nháp của Build, chờ Sản phẩm.
- /bao-mat là nháp, chờ chị Hằng hoặc anh Linh duyệt.
- kho-lead bắt buộc `ten`. Form chờ demo đang gửi "Khách chờ demo", cần Từ Hoảng thêm chế độ cho-demo và trả details.o khi lọc chữ.
- Ca 1.7 cần nguon lien-he, nhưng lõi map nhãn web-* về web.
- Ảnh đang dùng ảnh DS dự phòng, chờ hàng chờ của Thái Văn Cơ.


---
# Phụ lục B. Bàn giao trình tạo (Mãn Sủng)
# Bàn giao · Build Mãn Sủng · dừng 04:42 14/11 (lệnh Linh)

**Trạng thái:** nhánh `claude/project-thread-939spi` @ **2e855f45**, sạch, đã đẩy, gộp sạch trên nền es2prv 1fae0812. Chấm lần 3 cho trình tạo + agency **ĐẠT 9** (CHAM/TAO-AGENCY-d006ccea-cham1.md). Phiếu nộp NOP/BUILD-MAN-SUNG-TAO.md, ảnh + video NOP/BUILD-MAN-SUNG-TAO/2e855f45/. Chưa báo SHA ĐẠT này cho Hạ Hầu Đôn (đến sau lệnh dừng) → Quản trị chuyển khi mở lại.

## Việc còn lại khi mở lại
1. **V2 tường ảnh:** Tào Nhân báo màn tường ảnh đã có ở 59938a3e (nhánh claude/project-thread-a9kpr7, commit be15e466). Khi commit này vào nền:
   - Trong `catalog/chien-dich/rap-phim-tuong-anh.json`, đổi trangThai thành "chay" và campaign.name thành "Rạp phim mẫu · Bước vào phim".
   - Thêm E2E: /play/rap-phim-tuong-anh chuyển tới /khoi/ai-data-viz/tuong-anh.
   - Chưa bật trước khi màn này vào nền: nếu bật sớm, /play mở cảnh canvas chao-mung, và cảnh đó có tên thương hiệu thật.
2. **Ảnh chờ tạo** (NOP/ANH-HANG-CHO.md): LOGO-ca-phe-moc và PC-tao-1..3 (thẻ phong cách). Có ảnh thì:
   - Đặt logo vào `public/tao/img/logo-mau-ca-phe-moc.png`; video sẽ tự dùng logo này.
   - Thêm `thumb` cho 3 phong cách trong `server/modules/trinh-tao/blocks.js` (phongCachSach) và trong `catalog/mau/*.json`.
   - Chạy lại tao-khung-a và tao-video, rồi chụp lại ảnh 21, 24, 26.
3. **Ảnh 26 (theo ghi chú của Chấm):** test đang điền câu cảm ơn vào ô Lời chào. Khi chụp lại, đổi sang tiêu đề giống trong video ("Gala Ra mắt Mộc Tết 2027").
4. **Đường gọn** /tao/ → /tao/index.html và /agency → /tao/agency.html: Trương Liêu nối (nếu sửa routes/api.js thì nhờ Từ Hoảng).
5. **Lịch cũ:** mẫu vòng quay (activation-game, /choi/<id>), P1 khi có ảnh, và 4 phong cách P2 khi có ảnh tạo lại.

## Ghi chú kỹ thuật
- Video thật: `test/e2e/tao-video.test.js` dùng screencast của Chromium qua CDP. Không dùng recordVideo của Playwright, vì nó cần ffmpeg-1013 mà máy chỉ có 1011.
- `npm test` trên cloud: 355 đạt; 9 lỗi còn lại là lỗi môi trường có sẵn (clip nhân vật, Mùi Phở).
