# Báo cáo nghiệm thu T-G1-CUNGAI · Tham chiếu Brand ID cho cungai (Cùng AI / Sống Cùng AI)

- **Mã công việc**: `T-G1-CUNGAI`
- **Worker**: `antigravity` · Model: `Gemini 4 Carbon (Medium)`
- **Thời gian**: `2026-11-11 07:39` → `2026-11-11 07:53` (~14 phút, đạt chuẩn ≤40 phút)
- **Tệp bàn giao chính**:
  - `D:\LINHX\LAB\LAB122-BRAND-ID-4BU\CUNGAI\01-tham-chieu\THAM-CHIEU.md` (36 mẫu thật có link sống HTTP 200, đánh dấu 8 mẫu `★`, kèm 3 dòng tự phản biện cuối file)
  - `D:\LINHX\LAB\LAB122-BRAND-ID-4BU\CUNGAI\01-tham-chieu\anh\` (`01-google-ai-essentials.png`, `02-elements-of-ai.png`, `03-duolingo.png`, `04-kurzgesagt.png`, `05-bbc-bitesize.png`, `06-hard-fork.jpg`, `07-science-friday.jpg`, `08-mozilla.png`)

---

## 1. Kết quả chạy kiểm tra tự động nguyên văn (`verify_cungai.py`)

```text
Table header: | STT | Thương hiệu | Hạng | Link | Học gì (chữ/màu/hình/pattern, 1 dòng) | ★ |
Total reference rows: 36 (Requirement: >= 30)
Starred rows count: 8 (Requirement: 8) -> ['01-Google AI Essentials (Grow with Google)', '02-Elements of AI', '03-Duolingo', '04-Kurzgesagt – In a Nutshell', '05-BBC Bitesize', '06-Hard Fork (The New York Times)', '07-Science Friday', '08-Mozilla']
Live HTTP 200 URLs: 36/36
Images in anh/: 8 -> ['01-google-ai-essentials.png', '02-elements-of-ai.png', '03-duolingo.png', '04-kurzgesagt.png', '05-bbc-bitesize.png', '06-hard-fork.jpg', '07-science-friday.jpg', '08-mozilla.png']
  [OK] 01-google-ai-essentials.png: 640x130px, 30711 bytes
  [OK] 02-elements-of-ai.png: 640x350px, 109992 bytes
  [OK] 03-duolingo.png: 640x178px, 25257 bytes
  [OK] 04-kurzgesagt.png: 640x336px, 124172 bytes
  [OK] 05-bbc-bitesize.png: 640x171px, 13725 bytes
  [OK] 06-hard-fork.jpg: 640x640px, 129860 bytes
  [OK] 07-science-friday.jpg: 640x334px, 19646 bytes
  [OK] 08-mozilla.png: 640x216px, 18032 bytes
Self-critique lines: 3 (Requirement: 3)
Guardrail check: CUNGAI/00-goc/CORE-VALUE.md untouched, zero unexpected files in CUNGAI/.
ALL VERIFICATION CHECKS PASSED 100%!
```

---

## 2. Trạng thái thư mục & Git (`git status -sb` / danh sách tệp tạo mới)

Workspace `D:\LINHX\LAB\LAB122-BRAND-ID-4BU` chưa khởi tạo `.git`:
```text
fatal: not a git repository (or any of the parent directories): .git
```

Danh sách tệp tạo mới trong `CUNGAI\01-tham-chieu`:
```text
Mode   Length LastWriteTime         FullName
----   ------ -------------         --------
d-----        11/11/2026 7:50:31 AM D:\LINHX\LAB\LAB122-BRAND-ID-4BU\CUNGAI\01-tham-chieu\anh
-a---- 13823  11/11/2026 7:51:54 AM D:\LINHX\LAB\LAB122-BRAND-ID-4BU\CUNGAI\01-tham-chieu\THAM-CHIEU.md
-a---- 30711  11/11/2026 7:46:01 AM D:\LINHX\LAB\LAB122-BRAND-ID-4BU\CUNGAI\01-tham-chieu\anh\01-google-ai-essentials.png
-a---- 109992 11/11/2026 7:46:04 AM D:\LINHX\LAB\LAB122-BRAND-ID-4BU\CUNGAI\01-tham-chieu\anh\02-elements-of-ai.png
-a---- 25257  11/11/2026 7:49:19 AM D:\LINHX\LAB\LAB122-BRAND-ID-4BU\CUNGAI\01-tham-chieu\anh\03-duolingo.png
-a---- 124172 11/11/2026 7:46:05 AM D:\LINHX\LAB\LAB122-BRAND-ID-4BU\CUNGAI\01-tham-chieu\anh\04-kurzgesagt.png
-a---- 13725  11/11/2026 7:49:17 AM D:\LINHX\LAB\LAB122-BRAND-ID-4BU\CUNGAI\01-tham-chieu\anh\05-bbc-bitesize.png
-a---- 129860 11/11/2026 7:46:06 AM D:\LINHX\LAB\LAB122-BRAND-ID-4BU\CUNGAI\01-tham-chieu\anh\06-hard-fork.jpg
-a---- 19646  11/11/2026 7:46:07 AM D:\LINHX\LAB\LAB122-BRAND-ID-4BU\CUNGAI\01-tham-chieu\anh\07-science-friday.jpg
-a---- 18032  11/11/2026 7:50:31 AM D:\LINHX\LAB\LAB122-BRAND-ID-4BU\CUNGAI\01-tham-chieu\anh\08-mozilla.png
```

---

## 3. Tự phản biện cho Claude review

- **Đã thoả mãn từng AC nào?**
  1. **Số lượng ≥30 mẫu thật cùng hạng**: đạt **36 mẫu** chia đủ 4 trụ cột định vị của `cungai` / `cungai.vn`:
     - *Kênh phổ cập khoa học/công nghệ & điểm tin AI* (Google AI Essentials, Kurzgesagt, Vox, MIT Technology Review, The Verge, Quanta Magazine, 3Blue1Brown, TLDR, One Useful Thing).
     - *Podcast / Radio đại chúng về AI & khoa học* (Hard Fork, Science Friday, This American Life, On Being, Radiolab, NPR, 99% Invisible, Latent Space).
     - *Cổng tri thức mở, Thước đo AI & Vault cộng đồng* (Elements of AI, BBC Bitesize, Mozilla, Wikimedia, Hugging Face, Stanford HAI AI Index, Allen Institute for AI, Our World in Data, Creative Commons, OpenStax, GOV.UK Design System).
     - *Thương hiệu học tập cộng đồng & chứng chỉ/hộ chiếu kỹ năng* (Duolingo, Khan Academy, Brilliant, TED-Ed, DeepLearning.AI, Codecademy, Kaggle, Code.org).
  2. **Đối chiếu sát file logo gốc thực tế (`Logo có màu.png`)**: phát hiện và phản ánh chính xác chi tiết wordmark `CUNGAI` thực tế tách 2 màu (`CUNG` xanh dương + `ΛI` xanh lá không gạch ngang chữ A) bên dưới bóng thoại vạch bo tròn + chấm tròn (xanh dương, xanh lá, vàng, tím nhạt) và đuôi thoại vàng.
  3. **Không bịa link, mở được mới ghi**: chạy kiểm chứng thực tế HTTP GET đạt **36/36 link HTTP 200** (đã loại bỏ các URL trả 403/404/refused như `nytimes.com/column/hard-fork`, `bbc.co.uk/bitesize` trực tiếp, `thecrashcourse.com`, `quizlet.com`, `morningbrew.com`).
  4. **Đủ 8 mẫu `★` kèm 8 ảnh tham chiếu nhỏ sạch (`01` → `08`)**: đã kiểm tra mắt trực tiếp từng tấm ảnh (`read_file`), thay ngay ảnh `Mozilla_all_hands.jpg` chụp lưng người bằng logo `moz://a` sắc nét trên nền trắng và nâng `BBC Bitesize` lên bản 3 thanh hình học 2022.
  5. **Đủ 3 dòng tự phản biện** cuối `THAM-CHIEU.md` và **tuyệt đối không chạm** vào `CORE-VALUE.md`, `CHO-CHOT.md` hay bất kỳ tệp dự án nào khác.
- **Điểm nào còn yếu / cần Claude lưu ý khi sang G4–G6?**
  - Lưu ý đồng bộ thông số màu wordmark ở `CUNGAI/00-goc/CORE-VALUE.md` (hiện ghi tóm tắt *"chữ CUNGAI in hoa, không chân, xanh dương"*, trong khi file ảnh gốc `Logo có màu.png` có phần `CUNG` màu xanh dương và phần `ΛI` không gạch ngang màu xanh lá — giống cách tách màu wordmark của Science Friday `#07` và xử lý ký tự đặc biệt của Mozilla `#08`).
  - Các mẫu `#21 Latent Space`, `#34 Codecademy`, `#35 Kaggle` chỉ nên mượn cấu trúc bảng xếp hạng benchmark và bậc huy hiệu cho *Thước đo AI tiếng Việt* & *Hộ chiếu AI*, tránh mang tông kỹ sư phần mềm vào trang chủ phổ cập cho thính giả đại chúng VOV.
- **Danh sách mã vấn đề trong `.handoff/VAN-DE.md`**:
  - `[VD-003]` (`RESOLVED`): Chuẩn hoá đường dẫn đích `LAB122-BRAND-ID-4BU$B\01-tham-chieu\` trong `T-G1-CUNGAI.md` thành `LAB122-BRAND-ID-4BU\CUNGAI\01-tham-chieu\`.
