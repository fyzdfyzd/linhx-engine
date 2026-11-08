"""Khởi tạo đầy đủ 3 thư mục cấu hình `loai/bai_viet`, `loai/report_mau`, `loai/noi_dung_khoa_hoc`
theo đúng yêu cầu Đề 01 (Bản 3, chốt):
Mỗi loại có: `cau_hinh.json`, `dau_ra.md`, `dat_khi.md`, `loi_slop.md`, `kinh_nghiem.md`, và `mau/README.md` ("chờ Linh").
"""
import json
from pathlib import Path

PROTO_ROOT = Path(r"D:\LINHX\PROTO\01_MAY_TAO_NOI_DUNG")
LOAI_ROOT = PROTO_ROOT / "loai"


CONFIGS = {
    "bai_viet": {
        "cau_hinh": {
            "loai": "bai_viet",
            "ten_hien_thi": "Bài viết chuyên sâu (Báo chí / Tạp chí kinh tế - công nghệ)",
            "buoc_6_dung": ["LAB049 (linhx-viet-giong-viet)", "LAB025 (critic-loop-writer)"],
            "buoc_7_8_9_dung": ["LAB049 (linhx-bien-tap: 6 lượt tách ngữ cảnh)", "LAB025 (APS/CQS)"],
            "media_hoa": ["LAB031 (1-2 ảnh minh hoạ)", "LAB043 (nhận diện tạm Sakedemy)", "LAB049 (build_docx)"],
            "giong_tac_gia": "ho-so-bien-tap/linh/LUAT.md",
            "ho_so_bien_tap": "ho-so-bien-tap/van-anh/LUAT.md",
            "duyet_outline": "may",
            "che_do_viet": "chay_thu_khong_mau",
            "nhan_dien_tam": "sakedemy",
            "do_dai_muc_tieu_chu": [1100, 1600],
        },
        "dau_ra": """# ĐẦU RA CHUẨN · LOẠI: BÀI VIẾT (`bai_viet`)

1. **Bản thảo bài viết hoàn chỉnh (`09_bien_tap_va_kinh_nghiem.md` & `bai_viet_sach.md`)**:
   - Độ dài: `1.100 – 1.600 chữ` (chuẩn chuyên mục Tâm điểm / Góc nhìn chuyên gia).
   - Có tiêu đề chính (không theo khuôn sáo *"X không biến mất, nó..."*), sapo 2–3 câu đi thẳng vào nghịch lý, và 3–4 tiểu mục rõ mạch.
2. **Hồ sơ truy vết 9 bước (`01..09`)**:
   - Đủ 3 Persona Neo (`02`), tối thiểu 15 nguồn tham chiếu có mã `[N01]..[N15]` (`03`), 3 phương án Outline đã thử trên Persona (`04`), bảng chấm chọn hướng (`05`), Draft 1 (`06`), bảng đo máy Lượt 0 + APS/CQS (`07`), bản viết lại theo giọng Linh (`08`), và phiếu biên tập 6 lượt theo hồ sơ Vân Anh (`09`).
3. **Đầu ra Media hoá (`M1..M5` & `media/`)**:
   - 02 ảnh đồ hoạ minh hoạ chuẩn `1920x1080` (`minh_hoa_01.svg`, `minh_hoa_02.svg`) mang **Nhận diện tạm: Sakedemy (`LAB043`)**.
   - 01 file bàn giao `.docx` sạch mã nguồn.
""",
        "dat_khi": """# TIÊU CHÍ ĐẠT KHI (`dat_khi.md`) · LOẠI: BÀI VIẾT (`bai_viet`)

1. **Về ý tưởng & cấu trúc**:
   - Có **1 nghịch lý trung tâm** xuyên suốt bài; trả lời trực diện câu cãi của ít nhất 2/3 Persona Neo đã lập ở Bước 2.
   - Không kết bài bằng lời khuyên đạo lý, không hô khẩu hiệu, không kêu gọi hành động kiểu quảng cáo.
2. **Về giọng văn & số đo kỹ thuật (`LAB049` + `LAB025`)**:
   - Qua cổng `cham_cau.py`, `kiem_van_dich.py`, `kiem_van.py`:
     - Độ dài câu trung bình nằm trong dải **16 – 24 chữ/câu**; tỷ lệ câu quá dài (>35 chữ) ≤ 10%.
     - Điểm chất lượng biên tập **CQS ≥ 85/100** và điểm dấu vân máy **APS ≤ 25/100**.
     - Không vi phạm 8 lỗi cấm trong hồ sơ biên tập Vân Anh (`ho-so-bien-tap/van-anh/LUAT.md`).
3. **Về sự thật & minh bạch nguồn**:
   - Tối thiểu 3 số liệu/dẫn chứng thực tế gắn mã nguồn `[Nxx]` khớp với sổ nguồn Bước 3.
   - Mọi tình huống giả định (nếu có) bắt buộc gắn nhãn `[GIẢ LẬP]`.
4. **Về Media hoá (`LAB043`)**:
   - Đạt ≥ 90/100 điểm `check_onbrand_sakedemy()`, ghi rõ `"Nhận diện tạm: Sakedemy"`.
""",
        "loi_slop": """# DANH MỤC LỖI AI SLOP CẤM TUYỆT ĐỐI (`loi_slop.md`) · LOẠI: BÀI VIẾT

> Rút từ `LAB049/ho-so-bien-tap/van-anh/LUAT.md`, `linh/LUAT.md` và `tu-may-gemini.json`.

1. **Tám lỗi cấu trúc câu máy (Luật Vân Anh `VA-01` → `VA-08`)**:
   - `VA-01`: Câu so sánh hai vế máy móc (*"X thì..., còn Y thì..."*, *"Chưa có... nhưng... thì đã"* — tối đa không quá 5% tổng số câu).
   - `VA-02`: Cấu trúc *"Không còn là X mà là Y"*, *"Càng X càng Y"* (0% — bài đăng báo của anh Linh không bao giờ dùng).
   - `VA-03`: Láy lại cụm từ cuối câu trước để mở đầu câu sau.
   - `VA-04`: Thả số liệu lơ lửng không gánh luận điểm hoặc lặp lại cùng một con số ở đoạn xa.
   - `VA-05`: Kéo một ẩn dụ xuyên suốt nhiều đoạn văn hoặc chồng nhiều danh từ trừu tượng.
   - `VA-06`: Chủ thể mơ hồ (*"nhiều chuyên gia cho rằng"*, *"các doanh nghiệp hiện nay"* mà không chỉ rõ tầng nào, ai).
   - `VA-07`: Bịa chuyện bạn bè/đồng nghiệp không có thật mà không gắn nhãn `[GIẢ LẬP]`.
   - `VA-08`: Câu cụt 3–5 chữ đứng riêng làm đoạn để tạo vẻ nguy hiểm giả tạo.
2. **Từ vựng mùi văn dịch & AI Slop**:
   - Cấm dùng: *"bức tranh toàn cảnh"*, *"chìa khóa vàng"*, *"đòn bẩy chiến lược"*, *"không thể phủ nhận"*, *"trong kỷ nguyên số bùng nổ"*, *"hành trình chuyển mình"*, *"bị đào thải"*, *"khai phá tiềm năng vô hạn"*.
""",
        "kinh_nghiem": """# SỔ KINH NGHIỆM TÍCH LUỸ (`kinh_nghiem.md`) · LOẠI: BÀI VIẾT

- **KN-BV-01 (Từ LAB049 19/10)**: Bài để máy tự viết một mạch từ đầu đến cuối sẽ hỏng toàn bộ cách diễn đạt. Phải chốt dàn ý qua Persona ở Bước 4–5 và bám sát gạch đầu dòng hạt giống ở Bước 6.
- **KN-BV-02 (Từ LAB049 22/10)**: Lượt 5 (`doc-gia-ao`) luôn tìm ra câu cãi thực tế đắt nhất (ví dụ: chuyện nhân viên biết cách tắt thông báo nhưng không dám tắt). Phải đưa câu cãi của Persona vào ngay Bước 4 để đỡ phải đập đi viết lại ở Bước 9.
- **KN-BV-03 (Từ LAB049 25/10 - VD-005)**: Tuyệt đối không gộp toàn bộ 9 bước vào 1 file duy nhất; mỗi bước phải ghi 1 file riêng để giữ ngữ cảnh sạch và không đứt kết nối.
""",
    },
    "report_mau": {
        "cau_hinh": {
            "loai": "report_mau",
            "ten_hien_thi": "Báo cáo mẫu chẩn đoán & tư vấn chiến lược (Chuẩn McKinsey/LAB028 + Report-Core LAB046)",
            "buoc_6_dung": ["LAB028 (linhx-report: viet-bao-cao, 05-ghost)", "LAB046 (report-core: compose.py)"],
            "buoc_7_8_9_dung": ["LAB028 (07-kiem-so, 08-phan-bien)", "LAB046 (quality.py 17 luật, textclean.py)", "LAB049 (kiem_van.py)"],
            "media_hoa": ["LAB028 (dan-trang Typst/PDF, hinh-du-lieu SVG)", "LAB046 (render HTML/PDF)", "LAB043 (nhận diện tạm Sakedemy)"],
            "giong_tac_gia": "giong-bao-cao-chien-luoc",
            "ho_so_bien_tap": "partner-tu-van-lab028 + van-anh-lab049",
            "duyet_outline": "may",
            "che_do_viet": "chay_thu_khong_mau",
            "nhan_dien_tam": "sakedemy",
            "so_trang_muc_tieu": 5,
        },
        "dau_ra": """# ĐẦU RA CHUẨN · LOẠI: REPORT MẪU (`report_mau`)

1. **Nội dung Báo cáo 5 phần chuẩn McKinsey/Kantar (`09_bien_tap_va_kinh_nghiem.md`)**:
   - Trang 1: Tóm tắt điều hành (Executive Summary) — viết sau cùng khi đã khoá số liệu các chương.
   - Trang 2: Giải phẫu hiện trạng & Chi phí ẩn (kèm bằng chứng `[BC01]..[BC06]`).
   - Trang 3: Ma trận phân tầng năng lực 3 mức × 4 khối phòng ban (`[BC07]`).
   - Trang 4: Kiến trúc cổng kiểm chất lượng 17 luật & an toàn dữ liệu 2 lớp (`[BC05, BC09]`).
   - Trang 5: Lộ trình Pilot 90 ngày & Bảng chỉ số đo lường ROI (`[BC04, BC10]`).
2. **Đầu ra Media hoá (`M1..M5` & `media/`)**:
   - 02 Biểu đồ dữ liệu vector SVG (`hinh_01_khoang_trong_roi.svg`, `hinh_02_ma_tran_3_muc.svg`).
   - 01 File mã nguồn dàn trang Typst (`10_bao_cao_sakedemy.typ`).
   - 01 File HTML chuẩn in A4 (`bao_cao_sakedemy.html`) và **01 File PDF (`bao_cao_sakedemy.pdf`)** mang **Nhận diện tạm: Sakedemy (`LAB043`)**.
""",
        "dat_khi": """# TIÊU CHÍ ĐẠT KHI (`dat_khi.md`) · LOẠI: REPORT MẪU (`report_mau`)

1. **Chuẩn Ghost Report & Action Title (`LAB028`)**:
   - Mỗi trang/mục phải mở đầu bằng **1 Action Title (Tiêu đề kết luận có số hoặc nhận định sắc)**, không dùng tiêu đề chung chung kiểu *"Chương 1: Thực trạng"*.
2. **Cổng kiểm số & bằng chứng (`LAB028 07-kiem-so`)**:
   - 100% con số trong báo cáo và biểu đồ phải trỏ về mã `[BC01]..[BC15]` trong sổ bằng chứng Bước 3. Không bịa số liệu hay tên khách hàng.
3. **Cổng chất lượng 17 luật (`LAB046 quality.py` & `textclean.py`)**:
   - Không lặp đoạn, không lỗi dấu câu tiếng Việt, không dùng từ sáo rỗng, độ dài mỗi phần cân đối, đạt ≥ 90/100 điểm cổng chất lượng.
4. **Chuẩn dàn trang tạp chí & Nhận diện Sakedemy (`LAB028` + `LAB043`)**:
   - Tương phản chữ/nền đạt chuẩn WCAG AA (không đặt chữ trắng lên nền `#6EB264`), sử dụng font `Be Vietnam Pro`, ghi rõ `"Nhận diện tạm: Sakedemy (LAB043)"`.
""",
        "loi_slop": """# DANH MỤC LỖI AI SLOP CẤM TUYỆT ĐỐI (`loi_slop.md`) · LOẠI: REPORT MẪU

1. **Lỗi cấu trúc báo cáo AI**:
   - Tiêu đề mục vô thưởng vô phạt (*"Tổng quan tình hình"*, *"Một số giải pháp đề xuất"*) thay vì tiêu đề mang kết luận định lượng.
   - Đổ lỗi chung chung hoặc đưa khuyến nghị kiểu khẩu hiệu (*"Doanh nghiệp cần nâng cao nhận thức..."*) mà không có chủ thể thực hiện, thời hạn và chỉ số đo.
2. **Lỗi dữ liệu & trích dẫn**:
   - Thả con số phần trăm không có mẫu khảo sát hoặc nguồn `[BCxx]`.
   - Hứa hẹn số liệu chưa kiểm chứng bị cấm trong `brand.json` của Sakedemy (*"cam kết tối ưu 30%"*, *"số 1 Việt Nam"*, *"hoàn tiền 100%"*).
3. **Lỗi ngôn ngữ dịch thuật**:
   - Dùng câu bị động dày đặc (*"được thực hiện bởi"*, *"sự gia tăng của"*), dùng cấu trúc *"Không còn là... mà là..."*.
""",
        "kinh_nghiem": """# SỔ KINH NGHIỆM TÍCH LUỸ (`kinh_nghiem.md`) · LOẠI: REPORT MẪU

- **KN-RP-01 (Từ LAB028)**: Ghost Report (danh sách Action Title của toàn bộ các trang) phải được chốt ở Bước 5–6 trước khi viết văn bản chi tiết; nếu Action Title ghép lại chưa thành một câu chuyện chặt chẽ thì viết chương dài mấy cũng hỏng.
- **KN-RP-02 (Từ LAB046)**: Cổng `textclean.py` và 17 luật `quality.py` giúp chặn sớm lỗi lặp ý giữa các chương và lỗi khoảng trắng trước dấu câu tiếng Việt.
- **KN-RP-03 (Từ LAB043)**: Khi lên biểu đồ và hộp Callout Sakedemy, nền `#6EB264` bắt buộc đi với chữ `#02403B`, còn nền `#02403B` đi với chữ `#FFFFFF` và nhãn `#A3D34F`.
""",
    },
    "noi_dung_khoa_hoc": {
        "cau_hinh": {
            "loai": "noi_dung_khoa_hoc",
            "ten_hien_thi": "Nội dung khoá học thực chiến (1 buổi · Kịch bản lời giảng Gagné + Bộ Slide 16:9)",
            "buoc_6_dung": ["LAB017 (linhx-course: course-architect, lesson-script)"],
            "buoc_7_8_9_dung": ["LAB049 (linhx-bien-tap + linhx-viet-giong-viet)", "LAB017 (kiem_do_dai_am_tiet)"],
            "media_hoa": ["LAB027 (linhx-deck: 10-deck.json, slide HTML/PDF)", "LAB017 (Slidev slides.md)", "LAB032 (anh-sang-slide)", "LAB043 (nhận diện tạm Sakedemy)"],
            "giong_tac_gia": "giong-giang-vien-linh",
            "ho_so_bien_tap": "ho-so-bien-tap/linh/LUAT.md + van-anh/LUAT.md",
            "duyet_outline": "may",
            "che_do_viet": "chay_thu_khong_mau",
            "nhan_dien_tam": "sakedemy",
            "thoi_luong_buoi_hoc_phut": 90,
        },
        "dau_ra": """# ĐẦU RA CHUẨN · LOẠI: NỘI DUNG KHOÁ HỌC 1 BUỔI (`noi_dung_khoa_hoc`)

1. **Kịch bản bài giảng & Lời giảng hoàn chỉnh (`09_bien_tap_va_kinh_nghiem.md`)**:
   - Thiết kế chuẩn **5 sự kiện Gagné rút gọn** (`LAB017`):
     1. *Gây chú ý (Hook)* bằng ca lỗi thực tế tại doanh nghiệp.
     2. *Thông báo mục tiêu đầu ra* (làm được ngay sản phẩm gì sau 90 phút).
     3. *Khơi gợi & Trình bày nguyên lý cốt lõi* (Luật 80/20 + Persona Neo).
     4. *Hướng dẫn thực hành cầm tay chỉ việc* (Tách bước & quét 8 lỗi văn dịch).
     5. *Kiểm tra & Đóng gói sản phẩm mang về* (5 câu hỏi tình huống + Checklist 1 trang).
   - Mỗi phân đoạn slide có phần **Chữ trên Slide (tối đa 35 chữ)** và phần **Lời giảng nói của giảng viên Linh (150–240 âm tiết/phân đoạn)** khớp chuẩn đọc tiếng Việt.
2. **Đầu ra Media hoá (`M1..M5` & `media/`)**:
   - `slides.md` (chuẩn Slidev của `LAB017` để sẵn sàng đưa vào TTS/Avatar ở Mức 2).
   - `10-deck.json` + `slide_cover_16x9_sakedemy.svg` + `slide_deck_sakedemy.html` + **`slide_deck_sakedemy.pdf`** theo chuẩn bố cục `LAB027` (`linhx-deck`) mang **Nhận diện tạm: Sakedemy (`LAB043`)**.
""",
        "dat_khi": """# TIÊU CHÍ ĐẠT KHI (`dat_khi.md`) · LOẠI: NỘI DUNG KHOÁ HỌC (`noi_dung_khoa_hoc`)

1. **Chuẩn sư phạm thực chiến (`LAB017` + `LAB043 Sakedemy`)**:
   - Đủ 3 mục tiêu học tập đo lường được theo thang Bloom (không dùng động từ mơ hồ như *"hiểu được"*, *"nắm được"* mà phải dùng *"phân tách được"*, *"kiểm tra và sửa được"*, *"thiết kế được"*).
   - Có ít nhất 1 cặp đối chiếu trực quan **"Trước khi sửa (Bản AI lỗi)"** và **"Sau khi sửa (Bản đạt chuẩn)"**.
2. **Chuẩn giọng nói giảng viên Linh (`LAB017` + `LAB049`)**:
   - Câu lời giảng ngắn gọn, vừa hơi thở khi nói (trung bình 15–20 chữ/câu), không dùng văn viết rườm rà hay câu so sánh hai vế máy móc.
   - Mọi thuật ngữ tiếng Anh bắt buộc giải nghĩa tiếng Việt ngay lần đầu và liệt kê vào mục `pronunciation`.
3. **Chuẩn Slide (`LAB027` + `LAB043`)**:
   - Mỗi slide đúng 1 điểm chính (`diem_chinh`), ít nhất 35% khoảng trắng, đạt ≥ 90/100 điểm `check_onbrand_sakedemy()`, ghi rõ `"Nhận diện tạm: Sakedemy (LAB043)"`.
""",
        "loi_slop": """# DANH MỤC LỖI AI SLOP CẤM TUYỆT ĐỐI (`loi_slop.md`) · LOẠI: NỘI DUNG KHOÁ HỌC

1. **Lỗi kịch bản giảng dạy kiểu AI**:
   - Mở đầu buổi học bằng *"Chào mừng các bạn đến với kỷ nguyên AI..."* hoặc dành 20 phút đầu giảng lịch sử hình thành trí tuệ nhân tạo.
   - Slide chép nguyên văn lời giảng (khiến học viên đọc chữ trên màn hình thay vì nghe giảng viên).
   - Dùng từ cấm của Sakedemy: *"siêu khoá học"*, *"khai phá tiềm năng vô hạn"*, *"không học sẽ bị đào thải"*.
2. **Lỗi văn nói giả tạo**:
   - Lời giảng dùng cấu trúc văn dịch (*"Việc tối ưu hoá quy trình tạo nội dung là một yếu tố then chốt..."*) thay vì câu nói trực tiếp của giảng viên (*"Anh chị nhìn vào đoạn văn trên màn hình: đọc tới dòng thứ ba là biết ngay máy viết, vì sao?"*).
""",
        "kinh_nghiem": """# SỔ KINH NGHIỆM TÍCH LUỸ (`kinh_nghiem.md`) · LOẠI: NỘI DUNG KHOÁ HỌC

- **KN-KH-01 (Từ LAB017)**: Giọng giảng là đồng hồ chủ. Phải khoá lời giảng trước, kiểm tra nhịp câu nói bằng `cham_cau.py` để không có câu nào dài quá 30 chữ gây hụt hơi khi thu âm/TTS.
- **KN-KH-02 (Từ LAB027)**: Khi chuyển kịch bản sang Slide Deck, chữ trên slide chỉ giữ vai trò điểm tựa thị giác (tiêu đề kết luận + 3 gạch ngắn), toàn bộ phần giải thích nằm ở lời giảng.
""",
    },
}


def main():
    for loai, data in CONFIGS.items():
        ldir = LOAI_ROOT / loai
        mau_dir = ldir / "mau"
        mau_dir.mkdir(parents=True, exist_ok=True)

        (ldir / "cau_hinh.json").write_text(json.dumps(data["cau_hinh"], ensure_ascii=False, indent=2), encoding="utf-8")
        (ldir / "dau_ra.md").write_text(data["dau_ra"], encoding="utf-8")
        (ldir / "dat_khi.md").write_text(data["dat_khi"], encoding="utf-8")
        (ldir / "loi_slop.md").write_text(data["loi_slop"], encoding="utf-8")
        (ldir / "kinh_nghiem.md").write_text(data["kinh_nghiem"], encoding="utf-8")
        (mau_dir / "README.md").write_text(
            f"# Ô MẪU ĐẠT (`loai/{loai}/mau/`)\n\n"
            "> **Trạng thái**: Chờ Linh duyệt và đưa bài mẫu đạt chuẩn vào thư mục này (theo Đề 01 Bản 3 chốt 25/10 11:45).\n"
            "> Khi thư mục này còn trống, mọi bước chạy trong `runs/` bắt buộc ghi rõ: `Trạng thái mẫu: chạy không mẫu`.\n",
            encoding="utf-8",
        )
    print("INIT 3 LOAI CONFIGS OK")


if __name__ == "__main__":
    main()
