# Báo cáo nghiệm thu T-G1-UNIKON · Tham chiếu Brand ID cho Unikon

- **Mã công việc**: `T-G1-UNIKON`
- **Worker**: `antigravity` · Model: `Gemini 4 Carbon (Medium)`
- **Thời gian**: `2026-11-11 06:58` → `2026-11-11 07:12` (~14 phút, đạt chuẩn ≤40 phút)
- **Tệp bàn giao chính**:
  - `D:\LINHX\LAB\LAB122-BRAND-ID-4BU\UNIKON\01-tham-chieu\THAM-CHIEU.md` (36 mẫu thật có link sống HTTP 200, đánh dấu 8 mẫu `★`, kèm 3 dòng tự phản biện cuối file)
  - `D:\LINHX\LAB\LAB122-BRAND-ID-4BU\UNIKON\01-tham-chieu\anh\` (`01-runway.png`, `02-jasper.png`, `03-typeface.png`, `04-synthesia.jpg`, `05-cohere.jpg`, `06-monks.jpg`, `07-unit9.jpg`, `08-huge.jpg`)

---

## 1. Kết quả chạy kiểm tra tự động nguyên văn (`verify_deliverables.py`)

```text
Table header: | STT | Thương hiệu | Hạng | Link | Học gì (chữ/màu/hình/pattern, 1 dòng) | ★ |
Total reference rows: 36 (Requirement: >= 30)
Starred rows count: 8 (Requirement: 8) -> ['01-Runway', '02-Jasper', '03-Typeface', '04-Synthesia', '05-Cohere', '06-Monks (Media.Monks)', '07-UNIT9', '08-Huge']
Live HTTP 200 URLs: 36/36
Images in anh/: 8 -> ['01-runway.png', '02-jasper.png', '03-typeface.png', '04-synthesia.jpg', '05-cohere.jpg', '06-monks.jpg', '07-unit9.jpg', '08-huge.jpg']
  [OK] 01-runway.png: 640x336px, 14218 bytes
  [OK] 02-jasper.png: 640x336px, 138425 bytes
  [OK] 03-typeface.png: 640x360px, 131890 bytes
  [OK] 04-synthesia.jpg: 640x336px, 41738 bytes
  [OK] 05-cohere.jpg: 640x334px, 15865 bytes
  [OK] 06-monks.jpg: 640x336px, 28390 bytes
  [OK] 07-unit9.jpg: 640x336px, 26532 bytes
  [OK] 08-huge.jpg: 640x360px, 28577 bytes
Self-critique lines: 3 (Requirement: 3)
ALL VERIFICATION CHECKS PASSED 100%!
```

---

## 2. Trạng thái thư mục & Git (`git status -sb` / danh sách tệp tạo mới)

Workspace `D:\LINHX\LAB\LAB122-BRAND-ID-4BU` chưa khởi tạo `.git`:
```text
fatal: not a git repository (or any of the parent directories): .git
```

Danh sách tệp tạo mới trong `UNIKON\01-tham-chieu`:
```text
Mode   Length LastWriteTime         FullName
----   ------ -------------         --------
d-----        11/11/2026 7:06:46 AM D:\LINHX\LAB\LAB122-BRAND-ID-4BU\UNIKON\01-tham-chieu\anh
-a---- 11922  11/11/2026 7:10:12 AM D:\LINHX\LAB\LAB122-BRAND-ID-4BU\UNIKON\01-tham-chieu\THAM-CHIEU.md
-a---- 14218  11/11/2026 7:06:46 AM D:\LINHX\LAB\LAB122-BRAND-ID-4BU\UNIKON\01-tham-chieu\anh\01-runway.png
-a---- 138425 11/11/2026 7:04:31 AM D:\LINHX\LAB\LAB122-BRAND-ID-4BU\UNIKON\01-tham-chieu\anh\02-jasper.png
-a---- 131890 11/11/2026 7:08:02 AM D:\LINHX\LAB\LAB122-BRAND-ID-4BU\UNIKON\01-tham-chieu\anh\03-typeface.png
-a---- 41738  11/11/2026 7:04:33 AM D:\LINHX\LAB\LAB122-BRAND-ID-4BU\UNIKON\01-tham-chieu\anh\04-synthesia.jpg
-a---- 15865  11/11/2026 7:04:33 AM D:\LINHX\LAB\LAB122-BRAND-ID-4BU\UNIKON\01-tham-chieu\anh\05-cohere.jpg
-a---- 28390  11/11/2026 7:04:36 AM D:\LINHX\LAB\LAB122-BRAND-ID-4BU\UNIKON\01-tham-chieu\anh\06-monks.jpg
-a---- 26532  11/11/2026 7:04:38 AM D:\LINHX\LAB\LAB122-BRAND-ID-4BU\UNIKON\01-tham-chieu\anh\07-unit9.jpg
-a---- 28577  11/11/2026 7:04:38 AM D:\LINHX\LAB\LAB122-BRAND-ID-4BU\UNIKON\01-tham-chieu\anh\08-huge.jpg
```

---

## 3. Tự phản biện cho Claude review

- **Đã thoả mãn từng AC nào?**
  1. Số lượng ≥30 mẫu thật cùng hạng: đạt **36 mẫu** chia đủ 3 nhóm sát định vị Unikon (*AI Marketing/Content Platform*, *Creative-Tech & Sub-Agency đứng sau Big Agencies*, *Generative AI Creative Studio/Startup*).
  2. Không bịa link, mở được mới ghi: đã chạy kiểm tra tự động HTTP GET thực tế đạt **36/36 link HTTP 200** (đã loại bỏ các ứng viên trả 404 như `tome.app`, `koto.com/work/leonardo-ai`, hoặc trùng thương hiệu như `jam3.com` chuyển hướng về `monks.com`).
  3. Loại mẫu sai tinh thần dù cùng ngành: đã gạt bỏ nhóm AI quốc phòng/hạ tầng lạnh (Palantir, Scale AI, C3.ai) và nhóm sổ tay vẽ tay phản công nghệ (Granola).
  4. Bảng đúng cấu trúc 6 cột `STT | Thương hiệu | Hạng | Link | Học gì (chữ/màu/hình/pattern, 1 dòng) | ★` với đúng **8 mẫu `★`**.
  5. Đủ **8 ảnh tham chiếu nhỏ** (rộng 640px, 14–138 KB) tại `UNIKON/01-tham-chieu/anh/<stt>-<ten>.png|jpg`, đã đọc kiểm tra trực quan từng tấm đảm bảo hiện rõ logo/nhận diện thật.
  6. Đủ **3 dòng tự phản biện** cuối `THAM-CHIEU.md` và không chạm vào bất kỳ tệp nào khác ngoài khu vực được giao.
- **Điểm nào còn yếu / cần Claude lưu ý khi sang G6?**
  - Một số trang như Leonardo.Ai và Adobe Firefly chặn request tự động (HTTP 403 Cloudflare/Akamai) nên không đưa link trực tiếp vào bảng để giữ nguyên tắc 100% link kiểm tra tự động mở được; bù lại các bài học phối sắc độ hồng-magenta-cam trên nền tối và lưới vuông đã có đầy đủ qua Cohere (#05), Monks (#06), UNIT9 (#07) và Huge (#08).
  - Các mẫu SaaS tự phục vụ (#11 AdCreative.ai, #15 VEED.IO, #16 Photoroom) chỉ nên tham khảo cách tách khung ảnh/số liệu, tránh bê phong cách landing page nhiều nút CTA vào guideline B2B của Unikon.
- **Danh sách mã vấn đề trong `.handoff/VAN-DE.md`**:
  - `[VD-001]` (`RESOLVED`): Chuẩn hoá đường dẫn đích `LAB122-BRAND-ID-4BU$B\01-tham-chieu\` trong file đề thành `LAB122-BRAND-ID-4BU\UNIKON\01-tham-chieu\`.
