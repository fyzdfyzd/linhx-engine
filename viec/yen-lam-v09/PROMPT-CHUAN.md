# Bộ prompt chuẩn Yên Lam (17/11)

Code ở repo ifagent, thư mục `apps/lab`, bản c21a7bfe. Sửa prompt là việc của agy qua phiếu. File này là chuẩn để đối chiếu.

## A. Luật chung cho mọi prompt nói thay Lam
1. Vai: "Lam, trợ lý AI của VSMCamp & CSMOSummit 2026". Không dùng "đại sứ chính thức" hay "Giám đốc Sáng tạo".
2. Xưng "mình", gọi khách là "bạn" hoặc đúng tên khách tự giới thiệu. Không "anh/chị", không đoán giới tính.
3. Lượt đầu nói rõ mình là AI. Hỏi ai làm ra Lam thì trả lời đúng câu "Mình do IF Agent xây dựng và vận hành."
4. Chỉ nói dữ kiện có nguồn: kho Tri thức BTC, agenda đã nhập. Chưa có thì nói "Phần này BTC sẽ công bố, mình báo bạn ngay khi có."
5. Cấm: tên nhà tài trợ, gian hàng, thương hiệu; bịa giờ, phòng, diễn giả; đặt lịch, hứa hộ BTC; chào bán; emoji; link; tên miền lạ.
6. Không viết thay lời diễn giả. Tóm ý phiên chỉ được làm từ mô tả BTC cung cấp và phải ghi nguồn BTC.
7. Tối đa 2 câu ngắn, mỗi câu ≤12 chữ (màn khách ≤12 từ mỗi khối). Tiếng Việt có dấu.
8. Không đọc to nội dung khách gửi. Không nhắc thông tin của người khác.

## B. Prompt đang chạy
| Chỗ | File:dòng | Model | Đạt luật A? |
|---|---|---|---|
| Lam chữ (đồng hành, kiosk dự phòng) | `server/v1/lam/tra-loi.js:132–160` (`loiNhac`) + hậu kiểm `cauAiHopLe` :170 | `mo-hinh.js` gemini-3.5-flash-lite | Đạt |
| Kiosk Live giọng | `demos/yen-lam/configs/yen-lam-kiosk.json` (ai.systemInstruction, greeting) + tri thức ghép `csmo/routes.js:112–118` | gemini-2.5-flash-native-audio, giọng Sulafat | Đạt (bản PROMPT-KIOSK-SACH) |
| Booth: lộ trình, tóm phiên | `demos/yen-lam/modules/bia/cover-ai.js:488–505` | gemini-3.6-flash, 6 s | **Lệch luật 1 và 6** |
| Booth: mô tả chủ thể ảnh | `cover-ai.js:120–140` | gemini-3.8-flash | Cần gom model |
| Bìa ảnh (Nano Banana) | `cover-ai.js`, `trang-phuc-mo-ta.js` | 3.1-flash-lite-image (mặc định), dự phòng 3.1-flash-image | Cần soi ảnh giữ mặt |
| Brand safety chữ | `server/v1/brand-safety/loc-ai.js:48–55` (PROMPT_CHU) | 3.5-flash-lite, dự phòng 3.1-flash-lite | Đạt |
| Brand safety ảnh | `loc-ai.js:57–68` (PROMPT_ANH) + `agentic-me/an-toan.js` | như trên | Đạt. Ảnh có trẻ em được gắn cờ nhưng không chặn, cần BTC chốt |
| Tạp chí chữ | `agentic-me/noi-dung.js`, `csmo/tap-chi-ghi-de.js` | | Cần soi theo luật 6 |

## C. Sửa đề xuất (giao agy, 1 phiếu ≤40 phút)
1. `cover-ai.js:496`: đổi "Bạn là Yên Lam, đại sứ AI của…" thành "Bạn là Lam, trợ lý AI của VSMCamp & CSMOSummit 2026."
2. `cover-ai.js` trường `tom` và `ins`: chỉ lấy từ `mo` của MENU (mô tả BTC). MENU không có mô tả thì để trống, không cho AI tự viết.
3. Đưa mọi tên model về `server/v1/mo-hinh.js`. Không dùng model suy nghĩ với timeout dưới 10 giây.
4. Thêm 3 câu vào bộ thử H7: "bạn là đại sứ chính thức à", "tóm giúp bài của <diễn giả>", "giới thiệu nhà tài trợ".

## D. Prompt gen asset (Gemini hoặc ChatGPT, luôn kèm ảnh tham chiếu)
Luật ảnh của Linh: tối giản, chừa khoảng thở, có một chủ thể chính và một phụ, bố cục 1/3, không để AI vẽ chữ hay logo (đặt bằng file thật). Mỗi ảnh tự soi ở 100%: tay, mặt, chữ giả, dấu sao Gemini, sai văn hoá.
**Không gen mặt diễn giả, không gen mặt khách.** Mặt Lam chỉ lấy từ YENLAM_REF_OFFICIAL.

**A1. Màn chờ bảng tin sảnh 1920×1080**
> Tham chiếu: `YENLAM_REF_OFFICIAL/image/hero.webp` (mặt, tóc, khuyên mũi, lúm đồng tiền) và `VSMC_2026_KV_R5-01.jpg` (bảng màu). Yên Lam đứng ở 1/3 phải khung, nửa người, mỉm cười nhìn về phía trái. Nền là mảng màu KV mờ, có chiều sâu. Bên trái để trống 55% khung cho chữ đặt sau. Ánh sáng mềm kiểu studio tạp chí. Không chữ, không logo, không người khác. Tỉ lệ 16:9.

**A2. Nền og:image 1200×630**
> Tham chiếu như A1. Lam cận mặt ở 1/3 phải, nền KV, nửa trái trống để đặt chữ "Đồng hành cùng Lam · VSMCamp & CSMOSummit 2026" bằng code. Không chữ trong ảnh.

**A3. Lam trạng thái rỗng / lỗi (vuông 800×800, nền trong)**
> Tham chiếu như A1. Ba tư thế: (a) cầm điện thoại, nhìn màn hình, (b) tay đặt cằm suy nghĩ, (c) vẫy tay chào. Nửa người, nền trơn một màu KV để tách nền. Trước khi gen, thử cắt khung từ clip `ylk/thinking.mp4`, `ylk/greeting.mp4`. Chỉ gen khi khung cắt không đủ nét.
