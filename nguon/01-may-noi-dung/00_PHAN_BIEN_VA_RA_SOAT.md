# PHẢN BIỆN ĐỀ BÀI, RÀ SOÁT 13 LAB & KIẾN TRÚC ĐÓNG GÓI ĐỘC LẬP
> **Dự án**: `D:\LINHX\PROTO\01_MAY_TAO_NOI_DUNG`
> **Căn cứ**: `00_CHUAN_PROTO.md` (25/10/2026) & `01_MAY_TAO_NOI_DUNG.md` (Bản 3 · CHỐT 25/10 11:45)
> **Nguyên tắc đóng gói**: Mọi tài liệu, skill, script, cấu hình, bộ nhận diện tạm và kết quả chạy thử đều được **đóng gói hoàn chỉnh bên trong thư mục `D:\LINHX\PROTO\01_MAY_TAO_NOI_DUNG\`** để sử dụng độc lập lâu dài, không sửa thư mục LAB gốc và không bị gãy khi các LAB cũ chuyển vào `ARCHIVE`.

---

## PHẦN 1. PHẢN BIỆN ĐỀ BÀI (6 ĐIỂM CỐT LÕI CẦN XỬ LÝ NGAY TRONG THIẾT KẾ)

### 1. Rủi ro đứt gãy đường dẫn khi Đề 00 chuyển LAB sang Archive → Phải đóng gói tự thân (`vendor/` + `skills/`)
- **Vấn đề trong đề**:
  - `00_CHUAN_PROTO.md` (mục 4) và `00_DUNG_THU_MUC_VA_ARCHIVE.md` quy định các thư mục trong `D:\LINHX\LAB\` sẽ được chuyển sang `D:\LINHX\ARCHIVE\PROTO_2026-10-25\`.
  - Nếu `01_MAY_TAO_NOI_DUNG` chỉ gọi các LAB qua đường dẫn tuyệt đối `D:\LINHX\LAB\LAB0xx\...`, ngay khi Đề 00 chạy lệnh di chuyển hoặc khi mang thư mục `01_MAY_TAO_NOI_DUNG` sang máy/môi trường khác, toàn bộ hệ thống sẽ lỗi `FileNotFoundError`.
- **Giải pháp đóng gói**:
  - Thực hiện đúng quyền được cấp trong Luật bắt buộc số 1 của Đề 01 (*"Bộ điều phối gọi skill của lab hoặc sao chép sang `PROTO\01…\vendor\<lab>\` rồi mới sửa. Ghi nguồn và phiên bản"*) và chỉ đạo của anh Linh (*"Phải đóng gói mọi việc trong thư mục, để còn sử dụng"*).
  - Gom toàn bộ các skill, script kiểm định (`cham_cau.py`, `kiem_van.py`, `kiem_van_dich.py`, `kiem_nhap.py`, `luong_hoa.py`, `quality.py`, `textclean.py`, `report.py`, `deck.py`, `anh2slide.py`, `onbrand.py`), hồ sơ biên tập (`linh`, `van-anh`), mẫu dữ liệu persona (`persona-1000.json` hoặc tập lọc chuẩn), và bộ nhận diện tạm `sakedemy` vào ngay trong `01_MAY_TAO_NOI_DUNG\vendor\` kèm `VENDOR_MANIFEST.json` ghi rõ đường dẫn gốc, ngày đóng gói và phiên bản.
  - Không chạm/sửa bất kỳ file nào trong `D:\LINHX\LAB\`.

### 2. Mâu thuẫn triết lý ở Bước 6 (Viết Draft 1) giữa `LAB025` và `LAB049` (Luồng Vân Anh)
- **Vấn đề trong đề**:
  - Bảng Big Module 1 (Bước 6) ghi cho loại Bài viết: *"LAB025 bước 7 `critic-loop-writer`, LAB049 `viet-bai-giong-viet`"*.
  - Tuy nhiên, trong `LAB049\src\linhx-viet-giong-viet\skills\viet-bai-giong-viet\SKILL.md` (bản v0.3 ngày 19/10/2026), quy tắc cốt lõi là: **"Từ 19/10/2026 máy KHÔNG viết bài từ đầu... Dừng, chờ Linh viết nháp gạch đầu dòng (`03-nhap.md`), kiểm ý (`03b-kiem-y.md`), rồi máy chỉ làm mượt (`04-ban-muot.md`)."**
  - Trong khi đó, `LAB025` (`critic-loop-writer`) lại cho máy tự viết nháp toàn văn từ 3 phương án A/B/C.
- **Giải pháp điều phối**:
  - Thiết kế Module 6 (`06-trien-khai-draft-1`) hỗ trợ **2 chế độ rõ ràng trong cấu hình `loai/bai_viet/cau_hinh.json`**:
    1. `che_do: "co_nhap_tac_gia"` (dùng khi vận hành thật cùng anh Linh): Dừng nhận gạch đầu dòng của anh Linh → chạy `kiem_nhap.py` → `03b-kiem-y.md` → làm mượt theo đúng luồng Vân Anh.
    2. `che_do: "chay_thu_khong_mau"` (dùng để chạy thông luồng Mức 1 hôm nay khi anh Linh chưa đưa nháp tay): Máy rút khung gạch đầu dòng từ Outline đã chốt ở Bước 5 + chất liệu thật trong `KHO-CHUYEN-THAT.md` (LAB025), **kiểm ý (`03b`)**, rồi làm mượt dưới sự kiểm soát chặt của 8 luật cấm Vân Anh (`ho-so-bien-tap/van-anh/LUAT.md`). Mọi giai thoại giả định (nếu có) bắt buộc gắn nhãn `[GIẢ LẬP]`, tuyệt đối không bịa số liệu hay trích dẫn.

### 3. Sự khác biệt bản chất giữa `LAB028` (`linhx-report`) và `LAB046` (`report-core`) ở loại "Report mẫu"
- **Vấn đề trong đề**:
  - Đề ghép chung *"Report mẫu: Bước 6 dùng LAB028 + LAB046, Media hoá: PDF qua LAB028"*.
  - Thực tế rà soát code:
    - `LAB028` (`linhx-report`) là quy trình **13 bước làm báo cáo nghiên cứu/tư vấn kiểu McKinsey/Kantar** (Ghost report `05-ghost.md` → viết chương → kiểm số `07-kiem-so.json` → dàn trang **Typst**).
    - `LAB046` (`report-core`) là **engine lắp ghép báo cáo cá nhân hoá bằng dữ kiện (`FactSet`) + kho lời giải SQLite** (Chiêm tinh, Thần số học...) → kiểm qua **cổng chất lượng 17 luật (`quality.py` + `textclean.py`)** → xuất PDF qua **HTML/Chromium**.
- **Giải pháp điều phối**:
  - Kết hợp thế mạnh của cả hai thay vì chồng chéo:
    - Ở **Bước 1 → 6 (Big Module 1)**: Dùng khung cấu trúc `02-khung.json` + `03-bang-chung.jsonl` + `05-ghost.md` + viết chương của `LAB028`.
    - Ở **Bước 7 → 9 (Đánh giá & Biên tập)**: Dùng cổng kiểm số/trích dẫn của `LAB028` **kết hợp** bộ lọc `textclean.py` + 17 luật chất lượng `quality.py` của `LAB046` và bộ đo giọng văn `LAB049`.
    - Ở **Big Module 2 (Media hoá)**: Dàn trang xuất ra cả bản cấu trúc chuẩn `LAB028` (Typst/HTML-PDF) áp đúng bảng màu, font `Be Vietnam Pro` và logo của nhận diện tạm **Sakedemy (`LAB043`)**.

### 4. Độ vênh giữa `LAB017` (`linhx-course`) và `LAB027` (`linhx-deck`) ở loại "Nội dung khoá học (1 buổi)"
- **Vấn đề trong đề**:
  - Đề yêu cầu: *"Nội dung khoá học (1 buổi): Bước 6 dùng LAB017 `linhx-course`, Media hoá: slide qua LAB027, Giọng giảng viên Linh"*.
  - Thực tế: `LAB017` xuất ra `slides.md` theo chuẩn **Slidev** (kèm script lời giảng 5 bước Gagné rút gọn trong comment `<!-- ... -->` để đọc TTS), còn `LAB027` xuất ra `10-ghost-deck.md` + `10-deck.json` theo chuẩn **Deck tư vấn 15 bước**.
- **Giải pháp điều phối**:
  - Ở **Big Module 1 (Bước 1–9)**: Dùng `course-architect` (LAB017) cho Bước 1–4 (ra mục tiêu học tập Bloom + 3 phương án Outline buổi học + bài quiz), dùng Module 4–5 mới để thử trên Persona học viên và chốt hướng, dùng `lesson-script` (LAB017) ở Bước 6 để viết lời giảng chi tiết theo 5 sự kiện Gagné, và dùng `LAB049` ở Bước 7–9 để biên tập lời giảng theo giọng giảng viên Linh (chống văn dịch, chống câu quá dài khi nói).
  - Ở **Big Module 2 (Media hoá Slide)**: Viết bộ chuyển đổi (adapter) biến lời giảng + cấu trúc buổi học từ Bước 9 sang **cả 2 định dạng đóng gói**:
    1. `slides.md` (chuẩn Slidev của `LAB017` để sẵn sàng chạy TTS/Video ở Mức 2).
    2. `10-ghost-deck.md` + `10-deck.json` + bản trình chiếu HTML/PDF theo chuẩn bố cục slide của `LAB027` (`linhx-deck`) mang bộ nhận diện tạm **Sakedemy**.

### 5. Bẫy chọn mẫu Persona trong Module 2 & Module 4 (Cảnh báo từ thực tế `LAB048` + `LAB049`)
- **Vấn đề thực tế**:
  - `LAB048` chứa `persona-1000.json` lấy mẫu phân tầng từ dân số chung Việt Nam (Nemotron-Personas-Vietnam).
  - Chính `LAB049` (`doc-gia-ao/SKILL.md`) đã ghi bài học xương máu: *"Bộ persona dân số chung không hợp với độc giả báo kinh tế — phải lọc đúng tầng độc giả của kênh"*.
- **Giải pháp trong Module 2 (Gộp) & Module 4 (Làm mới)**:
  - Module 2 (`02-nghien-cuu-nguoi-nhan-persona`) không bốc ngẫu nhiên từ `LAB048`, mà chạy quy trình **3 tầng**:
    1. **Tầng Khoảng trống (`LAB029`)**: Xác định độc giả đang thiếu gì, câu hỏi nào chưa ai trả lời thỏa đáng.
    2. **Tầng Lọc Nhân khẩu (`LAB048`)**: Dùng script lọc từ `persona-1000.json` theo đúng độ tuổi, nghề nghiệp, trình độ, vùng miền phù hợp với loại nội dung.
    3. **Tầng Tâm lý & Phản biện (`LAB049 doc-gia-ao`)**: Đắp thêm vào mỗi persona: *Hoàn cảnh đọc/xem*, *Nỗi sợ ẩn*, *Định kiến ngành*, và *Câu cửa miệng hay dùng để cãi*.

### 6. Đáp ứng đồng thời Giao kèo của `00_CHUAN_PROTO.md` và Cấu trúc `runs/` của `01_MAY_TAO_NOI_DUNG.md`
- **Vấn đề**:
  - `00_CHUAN_PROTO.md` yêu cầu: (a) Đọc/ghi `_KIEN_THUC\INDEX.md` và `GIAO_KEO.md`, (b) Cung cấp 2 hàm giao kèo `taoNoiDung(mau, dauVao) → dauRa` và `kiemChatLuong(dauRa, loai) → diem, loi[]`, (c) Có `demo/input/` và `demo/output/`, `BAI_HOC.md`, `BAO_CAO/YYYY-MM-DD.md`, `README.md`, `verify`.
  - `01_MAY_TAO_NOI_DUNG.md` yêu cầu: (a) Thư mục `loai/<ten>/`, (b) Lưu mọi bước trong `runs/<ngày>_<loại>_<tên>/01…09` và `M1…M5`.
  - Ngoài ra, thư mục `D:\LINHX\PROTO\` hiện chưa có `_KIEN_THUC\` và `_DUNG_CHUNG\` (do Đề 00 chạy song song).
- **Giải pháp**:
  - Tự khởi tạo an toàn `_KIEN_THUC\INDEX.md`, `_KIEN_THUC\GIAO_KEO.md`, `_DUNG_CHUNG\README.md` (nếu chưa tồn tại).
  - Xây dựng đầy đủ cả `loai/`, `runs/` (theo Đề 01) và `demo/`, `BAI_HOC.md`, `BAO_CAO/2026-10-25.md`, `verify.ps1` / `verify.py` (theo Đề 00), kèm module giao kèo `giao_keo_api.py` (và `.ts`) cung cấp hàm `taoNoiDung` & `kiemChatLuong` dùng ngay được.

---

## PHẦN 2. RÀ SOÁT CHI TIẾT TÀI SẢN 13 LAB & BẢN ĐỒ ĐÓNG GÓI VÀO `01_MAY_TAO_NOI_DUNG`

| Mã LAB | Tài sản thực tế tìm thấy trên đĩa (`D:\LINHX\LAB\...`) | Vai trò trong `01_MAY_TAO_NOI_DUNG` | Cách đóng gói vào thư mục `01_MAY_TAO_NOI_DUNG` |
|---|---|---|---|
| **LAB025** (`QUY-TRINH-VIET-BAI`) | `skills/idea-seeder`, `deep-researcher`, `content-synthesizer`, `critic-loop-writer`, `gemini-reviewer`, `hoc-tu-ban-sua`; `du-lieu/KHO-CHUYEN-THAT.md`; `references/EDITORIAL_CHECKLIST.md`; `scripts/kiem_van.py` | Bước 1, 3, 4 (phần tạo 3 outline), 6 (nhánh bài viết), 7 | Đóng gói vào `vendor/LAB025/` + bọc trong `skills/01-phan-tich-de-bai`, `03-tim-tham-chieu`, `04-outline-va-thu-persona` |
| **LAB049** (`VIET-NHU-NGUOI`) | `linhx-bien-tap` (`bien-tap-bai`, `cham-tung-cau`, `doc-gia-ao`, `luong-hoa`, `soat-cau-truc`, `soat-ngon-ngu`, `soat-su-that`, `hoc-tu-ban-sua`, `ho-so-bien-tap/linh/LUAT.md`, `van-anh/LUAT.md`, `scripts/cham_cau.py`, `kiem_van.py`, `kiem_van_dich.py`, `kiem_nhap.py`, `luong_hoa.py`, `tu_may.py`, `build_docx.js`) + `linhx-viet-giong-viet` (`viet-bai-giong-viet`, `references/bai-mau/*`) | Bước 2 (phần `doc-gia-ao`), Bước 6, Bước 7, Bước 8, Bước 9 + Hàm `kiemChatLuong` | Đóng gói nguyên vẹn `linhx-bien-tap` & `linhx-viet-giong-viet` vào `vendor/LAB049/` + gắn vào `skills/06..09` |
| **LAB048** (`PERSONA-SURVEY-GIA-LAP`) | `src/lay_mau_1000.py`, `data/persona-1000.json` (1.000 hồ sơ phân tầng từ Nemotron-Personas-Vietnam) | Bước 2 (nguồn nhân khẩu học Việt Nam cho Persona Neo) | Đóng gói `lay_mau_1000.py` + bộ trích mẫu `persona-1000.json` vào `vendor/LAB048/` + tích hợp vào `skills/02-persona-neo` |
| **LAB029** (`KHOANG-TRONG-DOC-GIA`) | `src/linhx-khoang-trong` (`nhu-cau-doc-gia`, `cham-khoang-trong`, `radar-khoang-trong`, `soi-viet-nam`, `scripts/gapscan.py`) | Bước 2 (xác định khoảng trống độc giả trước khi dựng Persona) | Đóng gói vào `vendor/LAB029/` + tích hợp vào `skills/02-persona-neo` |
| **LAB028** (`REPORT-FLOW`) | `src/linhx-report` (`bao-cao`, `tim-mau-clone`, `khung-nghien-cuu`, `hinh-du-lieu`, `viet-bao-cao`, `dan-trang`, `scripts/report.py`, `clone.py`, `hinh.py`, `typst/`) | Bước 3 (tìm mẫu clone), Bước 6 & Media hoá cho loại **Report mẫu** | Đóng gói `linhx-report` vào `vendor/LAB028/` + gắn vào cấu hình `loai/report_mau/` và `skills/M2-media-pdf-report` |
| **LAB046** (`REPORT-ENGINE`) | `src/report-core` (`facts.py`, `compose.py`, `textclean.py`, `quality.py` 17 luật, `render.py`) | Bước 6, 7 (kiểm 17 luật chất lượng & làm sạch chữ tiếng Việt) cho **Report mẫu** | Đóng gói `report_core` vào `vendor/LAB046/` |
| **LAB017** (`ELEARNING-AI`) | `src/plugin/linhx-course` (`course`, `course-architect`, `lesson-script`, `lesson-slides`, `instructor-voice`, `instructor-avatar`, `lesson-compose`, `course-package`, `engine/*.py`) | Bước 1–6 cho loại **Nội dung khoá học (1 buổi)** | Đóng gói `linhx-course` (skills + engine scripts, không chép `.hf-cache`/weights nặng) vào `vendor/LAB017/` |
| **LAB027** (`DECK-PROPOSAL`) | `src/linhx-deck` (`deck-proposal`, `hieu-khach`, `loi-the-offer`, `hinh-anh`, `dung-deck`, `phan-bien`, `demo-ban-giao`, `scripts/deck.py`) | Media hoá **Slide** cho Khoá học / Deck | Đóng gói `linhx-deck` vào `vendor/LAB027/` + gắn vào `skills/M2-media-slide` |
| **LAB032** (`ANH-SANG-SLIDE`) | `src/anh-sang-slide` (`SKILL.md`, `scripts/anh2slide.py`) | Media hoá **Slide** (chuyển ảnh thiết kế sang PPTX chỉnh sửa được) | Đóng gói vào `vendor/LAB032/` |
| **LAB043** (`DESIGN-ONBRAND`) | `brands/sakedemy/` (`brand.json`, `LUAT-ONBRAND.md`, `01-logo/`, `02-mau/`, `03-chu/`, `05-icon/`, `09-khuon/`), `chuan-guideline/KHUNG-GUIDELINE-CHUAN.md`, `src/linhx-onbrand` (`onbrand-nap`, `onbrand-thiet-ke`, `onbrand-cham`, `onbrand-thi`, `scripts/onbrand.py`, `thiet_ke.py`) | **Nhận diện tạm Sakedemy** + Kiểm nhận diện + Mẫu gốc cho **Chu trình Template** | Đóng gói `brands/sakedemy`, `chuan-guideline` và `linhx-onbrand` vào `vendor/LAB043/` + xây mới `skills/M1-chu-trinh-template` |
| **LAB066** (`CASTING-GUONG-MAT`) | `QUY-TRINH-3-VONG.md`, `QUY-TRINH-PHAT-TRIEN-NHAN-VAT.md`, `scripts/tinh_diem.py`, `kiem_delta_e.py`, `character_sheet.py` | Media hoá **Nhân vật** (khung casting & kiểm đồng nhất nhân vật) | Đóng gói quy trình + scripts vào `vendor/LAB066/` |
| **LAB031** & **LAB036** | `LAB031` (`linhx-kho-minh-hoa`), `LAB036` (`linhx-brand-check`) | Media hoá **Ảnh minh hoạ** & **Kiểm đúng nhận diện** | Đóng gói vào `vendor/LAB031/` và `vendor/LAB036/` |

---

## PHẦN 3. CẤU TRÚC THƯ MỤC ĐÓNG GÓI `D:\LINHX\PROTO\01_MAY_TAO_NOI_DUNG\`

Toàn bộ công việc được đóng gói chuẩn hoá trong thư mục `D:\LINHX\PROTO\01_MAY_TAO_NOI_DUNG\` như sau:

```text
D:\LINHX\PROTO\01_MAY_TAO_NOI_DUNG\
├── 00_PHAN_BIEN_VA_RA_SOAT.md        # Bản phản biện đề bài & rà soát 13 LAB (file này)
├── 01_LICH_TRIEN_KHAI_MUC_1.md       # Lịch triển khai chi tiết từng bước & tiêu chí nghiệm thu
├── README.md                         # Hướng dẫn chạy lại toàn bộ trong ≤ 15 phút
├── STATUS.md                         # Trạng thái mức đang làm, mốc, kẹt, cần Linh, việc mới
├── BAI_HOC.md                        # Bài học rút ra trong quá trình lắp ráp & chạy thử
├── BAO_CAO\
│   └── 2026-10-25.md                 # Báo cáo kết quả phiên làm việc (giờ bắt đầu/kết thúc, mức đạt)
├── verify.py                         # Script tự động kiểm tra đủ cấu trúc, chạy test các cổng & giao kèo
├── dieu_phoi.py                      # Bộ điều phối trung tâm (chạy 9 bước + Media hoá M1-M5 + hàm giao kèo)
│
├── vendor\                           # Đóng gói nguyên bản các skill/script/data từ 12 LAB (không sửa LAB gốc)
│   ├── VENDOR_MANIFEST.json          # Ghi rõ nguồn, ngày chép, phiên bản của từng LAB
│   ├── LAB017\                       # linhx-course (skills + engine scripts)
│   ├── LAB025\                       # linhx-viet-bai (skills + KHO-CHUYEN-THAT + kiem_van.py)
│   ├── LAB027\                       # linhx-deck (skills + deck.py)
│   ├── LAB028\                       # linhx-report (skills + report.py + typst)
│   ├── LAB029\                       # linhx-khoang-trong (skills + gapscan.py)
│   ├── LAB031\                       # linhx-kho-minh-hoa
│   ├── LAB032\                       # anh-sang-slide (anh2slide.py)
│   ├── LAB036\                       # linhx-brand-check
│   ├── LAB043\                       # linhx-onbrand + brands/sakedemy + KHUNG-GUIDELINE-CHUAN.md
│   ├── LAB046\                       # report-core (quality.py, textclean.py, compose.py...)
│   ├── LAB048\                       # lay_mau_1000.py + mẫu persona phân tầng
│   ├── LAB049\                       # linhx-bien-tap + linhx-viet-giong-viet + ho-so-bien-tap (linh, van-anh)
│   └── LAB066\                       # QUY-TRINH-3-VONG.md + scripts casting
│
├── skills\                           # 9 Module của Big Module 1 + các Module của Big Module 2 (mỗi cái có SKILL.md)
│   ├── BM1_01_phan_tich_de_bai\      # Gắn LAB025 idea-seeder (hạt giống + 11 câu hỏi sâu)
│   ├── BM1_02_persona_neo\           # [GỘP MỚI] LAB029 khoảng trống + LAB048 persona + LAB049 doc-gia-ao
│   ├── BM1_03_tim_tham_chieu\        # Gắn LAB025 deep-researcher (≥15 nguồn) + LAB028 tim-mau-clone
│   ├── BM1_04_outline_thu_persona\   # [LÀM MỚI] LAB025 30 insights → 3 outline A/B/C + Thử trên 3 Persona Neo
│   ├── BM1_05_cham_chon_huong\       # [LÀM MỚI] Chấm 3 outline theo phản ứng persona + dat_khi + cờ duyet_outline
│   ├── BM1_06_trien_khai_draft1\     # Điều phối theo cấu hình: Bài viết (049+025) / Report (028+046) / Khoá học (017)
│   ├── BM1_07_danh_gia_draft1\       # Gắn LAB049 lượt 0 (máy) + soat-cau-truc + LAB025 APS/CQS
│   ├── BM1_08_viet_lai_giong_tac_gia\# Gắn LAB049 viet-bai-giong-viet + luong-hoa + hồ sơ Linh / Vân Anh
│   ├── BM1_09_bien_tap_3_vong\       # Gắn LAB049 bien-tap-bai (6 lượt tách ngữ cảnh) + hoc-tu-ban-sua
│   ├── BM2_M1_chu_trinh_template\    # [LÀM MỚI] Chu trình template 5 bước (phân tích → tham chiếu → 3 PA → chấm → biên tập ≤3 vòng)
│   └── BM2_M2_media_hoa\             # Điều phối Media hoá theo loại: Ảnh (031/043), PDF Report (028/046), Slide (027/032), Nhân vật (066), Video khung (042), Brand check (043/036)
│
├── loai\                             # Cấu hình 3 loại nội dung chạy thử hôm nay
│   ├── bai_viet\
│   │   ├── cau_hinh.json             # duyet_outline: "may"|"nguoi", giong: "linh", bien_tap: "van-anh", nhan_dien_tam: "sakedemy"
│   │   ├── dau_ra.md
│   │   ├── dat_khi.md
│   │   ├── loi_slop.md
│   │   ├── kinh_nghiem.md
│   │   └── mau\README.md             # "Chờ Linh duyệt bài mẫu đạt"
│   ├── report_mau\
│   │   ├── cau_hinh.json
│   │   ├── dau_ra.md
│   │   ├── dat_khi.md
│   │   ├── loi_slop.md
│   │   ├── kinh_nghiem.md
│   │   └── mau\README.md
│   └── noi_dung_khoa_hoc\
│       ├── cau_hinh.json
│       ├── dau_ra.md
│       ├── dat_khi.md
│       ├── loi_slop.md
│       ├── kinh_nghiem.md
│       └── mau\README.md
│
├── runs\                             # Lưu kết quả chạy thật Mức 1 (mỗi bước 1 file riêng, ghi rõ skill/lab đã gọi)
│   ├── 2026-10-25_bai_viet_ai-thuc-chien-doanh-nghiep\
│   │   ├── 01_phan_tich_de_bai.md ... 09_ban_cuoi_va_kinh_nghiem.md
│   │   └── M1_nhan_dien_template.md ... M5_ban_giao_media.md
│   ├── 2026-10-25_report_mau_dao-tao-ai-doanh-nghiep-2026\
│   │   ├── 01_phan_tich_de_bai.md ... 09_ban_cuoi_va_kinh_nghiem.md
│   │   └── M1_nhan_dien_template.md ... M5_ban_giao_media.md (+ file PDF/HTML Sakedemy)
│   └── 2026-10-25_noi_dung_khoa_hoc_buoi-01-tu-duy-cung-ai\
│       ├── 01_phan_tich_de_bai.md ... 09_ban_cuoi_va_kinh_nghiem.md
│       └── M1_nhan_dien_template.md ... M5_ban_giao_media.md (+ file Slide Deck Sakedemy)
│
└── demo\                             # Bản ánh xạ chuẩn theo 00_CHUAN_PROTO.md (input + output tóm tắt từ 3 runs)
    ├── input\
    └── output\
```
