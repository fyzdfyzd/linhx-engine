---
name: hinh-anh
description: Bước 8, 11, 12 của quy trình deck proposal - Claude điều khiển Chrome của Linh để tìm và lưu ảnh moodboard trên Pinterest/Dribbble, rút thẻ phong cách, tạo ảnh trên ChatGPT Plus đã đăng nhập với ảnh tham chiếu (ảnh neo + moodboard) và brand, rà ảnh theo 8 luật cứng, sửa nhiều vòng. Dùng khi làm moodboard, ảnh cho deck, slide, proposal.
---

# Moodboard, ảnh ChatGPT Plus, rà và sửa ảnh (bước 8, 11, 12)

Script: `python "${CLAUDE_PLUGIN_ROOT}/scripts/deck.py"`. Brand và bảng màu: `${CLAUDE_PLUGIN_ROOT}/du-lieu/thuong-hieu.json`; luật ảnh chi tiết của từng BU nằm trong Design System của BU đó (link trong `thuong-hieu.json`).

## Luật cứng

- Mặc định **poster ý tưởng không người**. Ảnh người như chụp thật từng bị chê "bị AI quá".
- **Không chữ, không logo, không số** trong ảnh. Chữ và logo ghép trong deck.
- **Mọi ảnh phải có tham chiếu.** Ảnh neo tạo từ ảnh moodboard; mọi ảnh sau đính kèm ảnh neo + 1–2 ảnh moodboard. `nhan-anh` từ chối lưu ảnh không khai `--ref`, cổng 12 từ chối ảnh không có ảnh neo trong ref.
- Không dùng nhận diện của khách khác hoặc đối thủ; không vẽ giống công trình, sản phẩm có thật.
- Ảnh Pinterest/Dribbble chỉ để tham chiếu nội bộ và làm ref cho ChatGPT, không đưa lên deck gửi khách.
- **Một brand một phong cách.** Mỗi brand có một ảnh neo chung ở `${CLAUDE_PLUGIN_ROOT}/du-lieu/neo/<brand>/` (ảnh neo, thẻ phong cách, moodboard, nguồn). Deck của brand đã có neo thì **không làm moodboard mới**: `deck.py neo <dir> --lay` (bước 8 xong luôn). Chỉ tạo phong cách mới khi Linh yêu cầu đổi, rồi `neo --luu --ghi-de`.
- **Logo không bao giờ đi qua ChatGPT.** Logo ta và logo khách là tệp gốc, ghép ở bước 13 (skill dung-deck).

## Dùng Chrome (mặc định)

Claude điều khiển Chrome của Linh qua Claude in Chrome (công cụ `mcp__claude-in-chrome__*`; trong Antigravity dùng trình duyệt của Antigravity). Đọc skill `chrome-browser` trước lần dùng đầu. Luật khi dùng:
- Làm trong **tab mới**, không đóng hay sửa tab Linh đang mở. Dùng tài khoản đã đăng nhập sẵn; không đăng nhập hộ, không gõ mật khẩu.
- Trên Pinterest/Dribbble **chỉ xem và tải**: không bấm lưu ghim, theo dõi, thích, bình luận. Mỗi lượt tối đa ~30 trang xem, tối đa 12 ảnh moodboard, đi chậm.
- Trên ChatGPT **chỉ tạo ảnh trong một chat mới của deck này**: không đổi cài đặt, không xoá chat, không tải lên tài liệu của khách (chỉ ảnh ref).
- Gặp captcha, đăng nhập lại, hết lượt tạo ảnh, cảnh báo chính sách: dừng, báo Linh một dòng, chờ.
- Thư mục tải về mặc định `%USERPROFILE%\Downloads` (đổi bằng `--tu`).
- Không có Chrome: dùng dự phòng ở cuối mỗi bước (Linh làm tay đúng các bước đó).

## Bước 8. Moodboard → `08-moodboard/`, `08-the-phong-cach.json`

0. `deck.py neo <dir>`: brand đã có ảnh neo thì chạy `deck.py neo <dir> --lay` và bỏ qua mục 1–6. Brand chưa có thì làm như dưới; sau khi ảnh neo được duyệt ở bước 11 thì `deck.py neo <dir> --luu` để mọi deck sau của brand dùng chung.

1. Từ đề bài, người nghe và brand, viết 6–10 cụm từ khoá tiếng Anh, chia hai nhóm: **bố cục slide** (Dribbble: "consulting proposal deck minimal navy", "banking pitch deck data visualization") và **chất ảnh** (Pinterest: "conceptual 3d poster soft light glass", "editorial annual report cover").
2. Mở `https://www.pinterest.com/search/pins/?q=<từ khoá>` và `https://dribbble.com/search/<từ khoá>` trong tab mới. Cuộn 1–2 màn, chụp màn hình, chọn ứng viên hợp brand và đủ khác nhau cho 3 hướng. Mở trang ảnh để lấy **link trang** và **link ảnh lớn nhất** (Pinterest: `i.pinimg.com/originals/...` hoặc `736x`; Dribbble: ảnh `cdn.dribbble.com`, đọc `src`/`srcset` lớn nhất qua `read_page` hoặc `javascript_tool`).
3. Ghi `08-moodboard/ung-vien.json`: `[{"anh_url", "trang", "tieu_de", "ly_do"}]`, 6–12 ảnh. Chạy `deck.py tai-anh <dir> --ds <dir>/08-moodboard/ung-vien.json`: tải về `08-moodboard/mb-NN.*`, ghi nguồn vào `08-moodboard/nguon.json`.
   - Ảnh nào script tải không được: trong Chrome mở ảnh, tải bằng nút tải hoặc `javascript_tool` (fetch → blob → thẻ `a download`), rồi `deck.py nhan-anh <dir> --vao moodboard --nguon <link trang>`.
4. Mở từng ảnh (Read), gom thành **3 hướng khác nhau thật** (H1–H3): bố cục, chữ, ảnh minh hoạ, biểu đồ, kèm ảnh đại diện. Dịch từ mơ hồ thành thông số ở `tu_mo_ho`. Màu bắt đầu từ brand, moodboard chỉ thêm sắc thái. `nguon_anh` lấy từ `nguon.json`.
5. Đưa Linh chọn bằng mắt (ghép 3 ảnh đại diện). **Vòng sửa:** Linh nói "đổi", "thêm kiểu X", "bỏ ảnh 3": quay lại mục 1–2 với từ khoá mới, tăng `vong` trong `08-the-phong-cach.json`. Chốt → `huong_chon`, `deck.py duyet <dir> 8`.
6. Dự phòng: Linh tự lưu 6–10 ảnh vào Downloads, Claude chạy `nhan-anh --vao moodboard` cho từng ảnh.

## Bước 8b. Học bố cục, chọn bố cục

1. Thư viện chung `${CLAUDE_PLUGIN_ROOT}/du-lieu/bo-cuc/thu-vien.json` (7 bố cục học từ deck đẹp, xem `references/bo-cuc-anh.md`). `deck.py bo-cuc ds` để xem.
2. Thấy bố cục đẹp mới (Dribbble "pitch deck", "keynote presentation"; Pinterest "keynote slide design editorial"; Behance nếu đã đăng nhập): xem toàn slide, không chỉ vật thể; chụp/tải ảnh, rồi `deck.py bo-cuc them --ma <id> --tep <ảnh> --nguon <link> --hop bia,chuong --chu-y "…"`.
3. `deck.py bo-cuc chon <dir>` ghi `bo_cuc_slide` (kiểu slide → bố cục) vào `08-the-phong-cach.json`; chỉnh tay bằng `--kieu K --ma ID`. Cổng 10 chặn kiểu slide chưa có bố cục.

## Bước 11. Tạo ảnh trên ChatGPT Plus → `11-goi-anh/`

**Ảnh nền, không phải vật thể dán khung.** Ảnh cho bìa, chương, kết, khẳng định là ảnh nền 16:9 tràn slide: chủ thể ở 1/3 phải, 2/3 trái trơn cùng tông nền để chữ đứng và nền slide tan vào ảnh; không khung, bệ, viền, bo góc. `goi-anh` tự viết prompt theo thứ tự bối cảnh → chủ thể → chi tiết → ràng buộc, thêm ánh sáng theo cảm xúc của slide ở 10b.

1. Trong `10-deck.json`, slide cần ảnh có `"anh": {"tep": "<ten>.png", "y_tuong": "<ẩn dụ, tiếng Anh>", "ti_le": "16:9|4:5|1:1", "mo_ta": "<alt tiếng Việt>"}`. Thường chỉ bìa, trang chương, 2–4 trang hai cột.
2. `deck.py goi-anh <dir>` sinh `PROMPT-ANH.md` + `prompts.json`: câu mở đầu, prompt từng ảnh, **cột Ref** từng ảnh. `deck.py cong <dir> 11`.
3. Chrome: tab mới `https://chatgpt.com/`, chat mới (Project riêng cho deck nếu có). Các đoạn JS đã chạy được (gửi prompt, chờ, tải ảnh) và lỗi hay gặp: `references/chatgpt-chrome.md`.
4. **Ảnh neo trước** (chỉ khi brand chưa có neo chung). Đính kèm 2–3 ảnh moodboard của hướng đã chọn (công cụ tải tệp của Claude in Chrome vào ô đính kèm, đường dẫn tuyệt đối; bản nào chỉ tải được ảnh chụp thì mở ảnh ref trong tab, chụp, tải lên). Dán câu mở đầu + prompt ảnh neo. Chờ ảnh xong (chụp màn hình kiểm mỗi 10–20 giây, tối đa ~3 phút). Bấm tải ảnh, rồi:
   `deck.py nhan-anh <dir> --vao anh --ten anh-neo.png --ref 08-moodboard/mb-01.jpg,08-moodboard/mb-04.jpg`
   Đưa Linh duyệt ảnh neo (luật 10 phút áp dụng). Chưa ổn thì sửa ngay trong chat đó, tối đa 3 vòng.
5. **Từng ảnh.** Mỗi lượt đính kèm đúng các tệp ở cột Ref (luôn có `anh-neo.png`), dán prompt, chờ, tải về, `nhan-anh … --ten <tệp> --ref <đúng các tệp đã đính kèm>`. Không gộp nhiều ảnh vào một lượt.
6. Ghi link chat vào `11-goi-anh/nhat-ky.json` (khoá `chat_url`) để vòng sửa quay lại đúng chat.
   Mẹo Chrome đã thử: tải tệp đính kèm xong thì **chờ 3 giây cho ảnh tải lên hết** rồi mới bấm vào ô chat và gõ (gõ sớm thì chữ rơi mất); gõ prompt một dòng (Enter là gửi); chờ ảnh bằng `javascript_tool` kiểm nút có `aria-label` chứa "Stop" đã biến mất và số `img[alt^="Generated image"]` tăng; tải ảnh bằng `fetch(img.src)` → blob → thẻ `a download` (về Downloads), rồi `nhan-anh --phut 3`. Ảnh dọc 2:3 ChatGPT trả 1024×1536.
7. Dự phòng: Linh làm tay theo `PROMPT-ANH.md`, ảnh tải về Downloads, Claude chạy `nhan-anh` từng ảnh với ref Linh đã dùng.

## Bước 12. Rà và sửa ảnh → `12-ra-anh.json`

1. `deck.py ra-anh <dir>`: máy đo tỉ lệ (H5), độ phân giải (H6), dung lượng; ảnh đã đổi bản thì tự xoá điểm cũ để chấm lại; ghép ảnh neo + cả bộ thành `12-to-anh.png`.
2. Claude mở từng ảnh (Read), ảnh neo và tờ `12-to-anh.png`, chấm H1–H4, H7, H8, H9, H10 (ảnh nền hoà vào slide) (cả bộ cùng tay vẽ, ánh sáng, độ chi tiết) `true/false`. Soi kỹ chỗ hình học: vật đâm xuyên vật, cột lơ lửng, bóng sai hướng (lỗi hay gặp nhất ở lần thử đầu), ghi `loi` (`muc`, `muc_do: nang|nhe`, `mo_ta`, `sua` viết tiếng Anh, cụ thể) và `ket_luan` `dat|sua|loai`.
3. **Vòng sửa:** `deck.py sua-anh <dir>` sinh prompt sửa (đính kèm theo thứ tự ở `dinh_kem`: ảnh cần sửa trước, rồi ảnh neo, rồi moodboard; prompt nói rõ "sửa ảnh đính kèm đầu tiên") cho ảnh `sua` (sửa trên ảnh vừa tạo, giữ phần còn lại) và `loai` (tạo lại, nói rõ lỗi lần trước), ghi `11-goi-anh/sua.json`. Quay lại đúng chat ChatGPT, đính kèm lại ref, dán prompt sửa, tải về, `nhan-anh` (bản cũ tự chuyển vào `anh/cu/`), `ra-anh`, chấm lại.
4. Mỗi ảnh tối đa **3 vòng sửa**; quá thì `sua-anh` liệt kê vào `can_linh`: hỏi Linh đổi ý tưởng ảnh hay bỏ ảnh.
5. `deck.py cong <dir> 12`. Script từ chối khi còn mục `false`, lỗi nặng, ảnh không có trong nhật ký, hoặc bản hiện tại không đính kèm ảnh neo.
