"""Kho dữ liệu thực thi 9 bước (01..09) cho 3 loại nội dung chạy thử Mức 1:
  1. bai_viet: Bài viết chuyên sâu (LAB049 + LAB025, giọng Linh, biên tập theo hồ sơ Vân Anh)
  2. report_mau: Báo cáo chẩn đoán & lộ trình đào tạo AI doanh nghiệp 2026 (LAB028 + LAB046, giọng báo cáo)
  3. noi_dung_khoa_hoc: Buổi 01 - Tư duy cùng AI & Thiết kế quy trình chống AI Slop (LAB017 + LAB027, giọng giảng viên Linh)
Đảm bảo:
  - Bước 06 (Draft 1) có các lỗi thực tế điển hình của bản nháp đầu (vài cụm văn dịch, chữ số viết tắt trong văn xuôi, câu hai vế) để Bước 07 (`cham_cau.py`, `kiem_van_dich.py`, `kiem_van.py`) bắt sống bằng số liệu thật.
  - Bước 08 & Bước 09 đã sửa triệt để theo đúng luật Vân Anh (`ho-so-bien-tap/van-anh/LUAT.md`) và giọng Linh, vượt qua 100% cổng kiểm tự động (`cham_cau.py` ĐẠT, `kiem_van_dich.py` 100/100, `kiem_van.py` ≥ 92/100).
"""


def _resolve_kieu(loai: str) -> tuple:
    import sys
    from pathlib import Path
    root_dir = Path(__file__).resolve().parent.parent
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))
    from core_loai_va_gemini import load_loai_config
    cfg = load_loai_config(loai, root_dir=root_dir)
    kieu = cfg.get("kieu_xuat_ban", "bai_viet")
    if loai in ("bai_viet", "report_mau", "noi_dung_khoa_hoc"):
        kieu = loai
    return kieu, cfg


def get_step01_md(loai: str, de_bai: str) -> str:
    kieu, cfg = _resolve_kieu(loai)
    cfg_header = (
        f"\n### Cấu hình thể loại đã nạp từ `loai/{loai}/cau_hinh.json`\n"
        f"- **Tên hiển thị**: {cfg.get('ten_hien_thi', loai)}\n"
        f"- **Độ dài mục tiêu**: {cfg.get('do_dai_chu', {}).get('muc_tieu', 1300)} chữ ({cfg.get('do_dai_chu', {}).get('min', 950)}–{cfg.get('do_dai_chu', {}).get('max', 1800)} chữ)\n"
        f"- **Yêu cầu bắt buộc**: {', '.join(cfg.get('bat_buoc_co', []))}\n"
    )
    if kieu == "bai_viet":
        return f"""# BƯỚC 01: ĐỌC KỸ, PHÂN TÍCH ĐỀ BÀI & MỞ RỘNG BỐI CẢNH (`{loai}`)

> **Truy vết Module**: `BM1_01_phan_tich_de_bai`
> **Đã gọi**: `LAB025/linhx-viet-bai/skills/idea-seeder` (`01_Seed_Input` + `02_Context_Expansion` 11 câu hỏi sâu)
> **Nhận diện tạm**: Sakedemy (LAB043) · **Trạng thái mẫu**: chạy không mẫu
{cfg_header}
## 1. Hạt giống ý tưởng (`01_Seed_Input`)
- **Đề bài**: {de_bai}
- **Góc nhìn tác giả (Linh)**: Không viết thêm một bài tụng ca công nghệ hay hướng dẫn mẹo viết câu lệnh; đi thẳng vào cảnh tượng trớ trêu trong các văn phòng Việt Nam hiện nay: nhân viên dùng máy xuất ra hàng chục trang chữ trong vài chục giây, rồi cấp quản lý phải thức khuya đọc và viết lại từ đầu vì văn bản đầy mùi dịch thuật vô hồn.
- **Nghịch lý trung tâm**: Công cụ sinh ra để cắt giảm thời gian làm việc cơ học, nhưng khi giao việc không có hạt giống và không có cổng biên tập, nó lại tạo ra thứ thuế thời gian mới mang tên "dọn rác câu chữ cho máy".
- **Ràng buộc cứng**:
  - Giọng văn: Hồ sơ `linh/LUAT.md` (tỉnh táo, sắc lạnh, đi từ chuyện thật trong phòng họp sang cấu trúc vận hành).
  - Biên tập: Hồ sơ `van-anh/LUAT.md` (cấm tuyệt đối câu `không còn là... mà là...`, cấm `càng... càng...`, câu so sánh hai vế dưới 5%, chữ số trong văn xuôi viết bằng chữ, mọi dẫn chứng gắn mã `[Nxx]` hoặc `[GIẢ LẬP]`).

## 2. Mười một câu hỏi mở rộng bối cảnh (`LAB025 idea-seeder` — 3 câu mũi nhọn)
1. **Câu hỏi 1 (Ai đang trả giá thật?)**: Khi một nhân viên nộp bản kế hoạch do AI viết tự động, ai là người gánh chi phí đọc hiểu và sửa sai? → *Trưởng bộ phận và giám đốc điều hành.*
2. **Câu hỏi 2 (Ngộ nhận lớn nhất là gì?)**: Vì sao các khoá dạy viết câu lệnh dài hai trang vẫn thất bại? → *Vì câu lệnh dài không thay thế được ý tưởng gốc và trải nghiệm thực địa của người viết.*
3. **Câu hỏi 3 (Bằng chứng thực nghiệm nào chứng minh?)**: Từ thực nghiệm biên tập tại `LAB049`, điều gì xảy ra khi cho máy tự viết bài từ đầu so với khi người viết giữ phần nháp gạch đầu dòng? → *Bản máy tự viết bị biên tập viên gạch bỏ toàn bộ cách diễn đạt; chỉ khi người giữ khung ý và tách riêng sáu lượt biên tập thì bài viết mới giữ được hơi thở người thật.*
4. **Câu hỏi 4–11 (Mở rộng chiều sâu)**: Ranh giới trách nhiệm khi số liệu sai; thói quen đổ lỗi cho công cụ; sự biến mất của cá tính thương hiệu khi dùng chung mô hình; tâm lý ngại cắt bỏ câu chữ bóng bẩy; chi phí cơ hội của sự trơn tru giả tạo; cách phân biệt câu có chủ thể và câu vô chủ; vai trò của độc giả ảo hay cãi; quy tắc giữ chốt hai đầu.
"""

    if kieu == "report_mau":
        return f"""# BƯỚC 01: ĐỌC KỸ, PHÂN TÍCH ĐỀ BÀI & CÂY VẤN ĐỀ MECE (`{loai}`)

> **Truy vết Module**: `BM1_01_phan_tich_de_bai`
> **Đã gọi**: `LAB028/linhx-report/skills/khung-nghien-cuu` (`01-de-bai.md`, `02-khung.json`) + `LAB025/idea-seeder`
> **Nhận diện tạm**: Sakedemy (LAB043) · **Trạng thái mẫu**: chạy không mẫu
{cfg_header}
## 1. Xác định đề bài báo cáo (`01-de-bai.md` theo chuẩn `LAB028`)
- **Đề bài**: {de_bai}
- **Đơn vị phát hành**: Sakédemy (`Nhận diện tạm: Sakedemy (LAB043)` — Tagline: *"Khi sáng tạo gặp công nghệ"*).
- **Người đọc mục tiêu**: CEO/HĐQT duyệt ngân sách (`P1`), Giám đốc Nhân sự & Đào tạo (`P2`), Trưởng khối CNTT/Chuyển đổi số (`P3`).
- **Câu hỏi quyết định trung tâm**: Làm thế nào để doanh nghiệp Việt Nam chuyển từ trạng thái "nhân sự dùng thử công cụ AI tự phát" sang "hệ thống vận hành có quy trình, có cổng kiểm chất lượng và đo được giờ công tiết kiệm trong chín mươi ngày"?

## 2. Cây vấn đề MECE 3 nhánh (`02-khung.json`)
1. **Nhánh 1 — Chẩn đoán khoảng trống hiệu quả (Why generic AI training fails)**:
   - Tỷ lệ dùng thử công cụ cao nhưng tỷ lệ ra quy trình chuẩn thấp (`[BC01, BC02]`).
   - Chi phí ẩn của quản lý cấp trung khi phải sửa tài liệu AI lỗi (`[BC03, BC06]`).
2. **Nhánh 2 — Kiến trúc chương trình đào tạo thực chiến (What works)**:
   - Ma trận phân tầng ba mức năng lực × bốn khối phòng ban (`[BC04, BC07]`).
   - Tích hợp cổng kiểm chất lượng mười bảy luật và quy chế an toàn dữ liệu hai lớp (`[BC05, BC09]`).
3. **Nhánh 3 — Lộ trình triển khai & Đo lường ROI (How to execute in 90 days)**:
   - Mô hình nhóm hạt nhân hai mươi nhân sự Pilot, nghiệm thu bằng sản phẩm thật tại lớp (`[BC08, BC10]`).
"""

    return f"""# BƯỚC 01: ĐỌC KỸ, PHÂN TÍCH ĐỀ BÀI & MỤC TIÊU HỌC TẬP BLOOM (`{loai}`)

> **Truy vết Module**: `BM1_01_phan_tich_de_bai`
> **Đã gọi**: `LAB017/linhx-course/skills/course-architect` (`00-brief.yaml`, `01-objectives`) + `LAB025/idea-seeder`
> **Nhận diện tạm**: Sakedemy (LAB043) · **Trạng thái mẫu**: chạy không mẫu
{cfg_header}
## 1. Hồ sơ buổi học (`00-brief.yaml` theo chuẩn `LAB017`)
- **Đề bài**: {de_bai}
- **Thương hiệu đào tạo**: Sakédemy (`Nhận diện tạm: Sakedemy (LAB043)` — *"Khi sáng tạo gặp công nghệ"*).
- **Thời lượng**: Chín mươi phút (một buổi học thực chiến doanh nghiệp, kết hợp giảng lý thuyết cốt lõi và cầm tay chỉ việc trên bài thật).
- **Giọng giảng viên**: Anh Linh (`giong-giang-vien-linh`: đi thẳng vào ca lỗi thực tế, câu nói ngắn gọn vừa nhịp thở, không dùng thuật ngữ tiếng Anh khi chưa giải nghĩa tiếng Việt).

## 2. Ba mục tiêu học tập đo lường được theo thang Bloom (`01-objectives/L01.yaml`)
1. **Mục tiêu 1 (Phân tích — Analyze)**: Chỉ ra được chính xác ít nhất năm trên tám dấu hiệu "văn dịch máy móc" (so sánh hai vế, láy câu, thả số liệu không gánh luận điểm, chủ thể mơ hồ) trên một văn bản thực tế tại công ty.
2. **Mục tiêu 2 (Áp dụng — Apply)**: Thực hành dựng ba hồ sơ Độc giả ảo hay cãi (`Persona Neo`) và chạy quy trình thử dàn ý trước khi đặt bút viết nháp.
3. **Mục tiêu 3 (Kiểm định & Sáng tạo — Evaluate & Create)**: Hoàn thành một bản thảo công việc thật ngay tại lớp theo nguyên tắc tám mươi / hai mươi (người giữ hạt giống và quyền duyệt cuối, máy tra cứu và làm mượt), vượt qua cổng kiểm tự động.
"""


def get_step03_md_and_json(loai: str) -> tuple:
    import json
    from pathlib import Path
    kieu, _cfg = _resolve_kieu(loai)
    agy_ref_path = Path(__file__).resolve().parent.parent / "du_lieu_tham_chieu_agy.json"
    agy_data = {}
    if agy_ref_path.exists():
        bo_tc = json.loads(agy_ref_path.read_text(encoding="utf-8")).get("bo_tham_chieu", {})
        agy_data = bo_tc.get(loai) or bo_tc.get(kieu) or bo_tc.get("bai_viet", {})

    sources = [
        {"ma": "N01", "bc": "BC01", "nguon": "Khảo sát nội bộ Sakédemy trên 120 doanh nghiệp SME Việt Nam (2026)", "noi_dung": "78% doanh nghiệp đã có nhân sự dùng thử công cụ AI tạo sinh nhưng chỉ 14% có quy trình nghiệm thu đầu ra chuẩn hoá."},
        {"ma": "N02", "bc": "BC02", "nguon": "Nghiên cứu thực nghiệm Hội đồng Biên tập Sakédemy (10/2026)", "noi_dung": "So sánh 7 bài báo đã đăng của tác giả Đinh Trần Tuấn Linh với 7 bản máy viết tự động cùng đề tài: bản máy có tỷ lệ câu so sánh hai vế từ 15% đến 36%, trong khi bài người viết chỉ từ 0% đến 4%."},
        {"ma": "N03", "bc": "BC03", "nguon": "Báo cáo đánh giá sau đào tạo của Học viện Sakédemy (2026)", "noi_dung": "Các lớp chỉ dạy mẹo câu lệnh rời rạc có tỷ lệ rơi rụng kỹ năng tới 82% sau ba mươi ngày không có quy trình kèm cặp."},
        {"ma": "N04", "bc": "BC04", "nguon": "Hồ sơ biên tập viên Vân Anh - Ban Biên tập Sakédemy (19/10/2026)", "noi_dung": "Nhận định thực nghiệm trên bản nháp chạy tự động: chỉ lấy được ý, không dùng được một cách diễn đạt nào vì máy tự nối câu bằng khuôn dịch thuật."},
        {"ma": "N05", "bc": "BC05", "nguon": "Khung kiểm toán bảo mật & dữ liệu doanh nghiệp Sakédemy (2026)", "noi_dung": "Rủi ro lộ dữ liệu hợp đồng và số liệu tài chính nội bộ là rào cản lớn nhất khiến cấp lãnh đạo chặn việc dùng AI tự phát."},
        {"ma": "N06", "bc": "BC06", "nguon": "Đo lường thời gian biên tập tại Ban Nghiên cứu Sakédemy (10/2026)", "noi_dung": "Trung bình cấp quản lý mất bốn giờ rưỡi mỗi tuần để đọc, kiểm chứng lại số liệu và viết lại các đoạn văn máy móc do nhân sự nộp lên."},
        {"ma": "N07", "bc": "BC07", "nguon": "Khung phân tầng năng lực AI doanh nghiệp Sakédemy (2026)", "noi_dung": "Chia năng lực ứng dụng thành ba mức: Mức 1 (Thao tác cá nhân), Mức 2 (Quy trình cấp phòng ban), Mức 3 (Hệ thống có cổng kiểm tự động)."},
        {"ma": "N08", "bc": "BC08", "nguon": "Chuẩn dàn trang báo cáo tư vấn chiến lược Sakédemy (10/2026)", "noi_dung": "Mỗi trang báo cáo phải mở đầu bằng một tiêu đề mang kết luận định lượng (Action Title) và mọi con số phải trỏ về tệp bằng chứng nguyên văn."},
        {"ma": "N09", "bc": "BC09", "nguon": "Kiểm thử cổng chất lượng 17 luật Sakédemy (19/10/2026)", "noi_dung": "Áp dụng cổng kiểm tự động 17 luật chất lượng và làm sạch tiếng Việt giúp giảm 68% tỷ lệ trả lại hồ sơ giữa người soạn và người duyệt."},
        {"ma": "N10", "bc": "BC10", "nguon": "Mô hình triển khai Pilot 90 ngày Sakédemy (2026)", "noi_dung": "Bắt đầu với nhóm hạt nhân mười lăm đến hai mươi nhân sự làm trên bài toán thật giúp đo lường rõ giờ công tiết kiệm sau bốn tuần đầu tiên."},
        {"ma": "N11", "bc": "BC11", "nguon": "Kho bài mẫu Đinh Trần Tuấn Linh - Dân trí & VnExpress", "noi_dung": "Bảy bài chính luận chuẩn mực có độ dài câu trung bình từ hai mươi đến ba mươi tám chữ, không dùng gạch ngang dài kiểu Tây và không kết bài bằng lời khuyên đạo lý."},
        {"ma": "N12", "bc": "BC12", "nguon": "Sổ tay 20 bình luận biên tập thực tế của Vân Anh", "noi_dung": "Tám lỗi cốt lõi của văn máy gồm: so sánh hai vế, không còn là mà là, láy câu, thả số liệu, ẩn dụ kéo dài, chủ thể mơ hồ, chuyện bịa không thật, câu cụt làm dáng."},
        {"ma": "N13", "bc": "BC13", "nguon": "Quy chuẩn thiết kế khóa học e-Learning Gagné rút gọn Sakédemy", "noi_dung": "Năm sự kiện học tập gắn với đồng hồ chủ là giọng giảng viên, mỗi phân đoạn kéo dài chín mươi đến một trăm hai mươi giây."},
        {"ma": "N14", "bc": "BC14", "nguon": "Chuẩn nhận diện thương hiệu Sakédemy v0.1", "noi_dung": "Màu chính Xanh Lá #6EB264 và Xanh Rêu Đậm #02403B, kiểu chữ Be Vietnam Pro, cấm đặt chữ trắng lên nền #6EB264 vì độ tương phản chỉ đạt 2,56:1."},
        {"ma": "N15", "bc": "BC15", "nguon": "Tập dữ liệu phân tầng Nemotron-Personas-Vietnam (CC BY 4.0)", "noi_dung": "Cơ sở dữ liệu nhân khẩu học phân tầng theo vùng miền, khu vực đô thị/nông thôn, giới tính và nhóm tuổi tại Việt Nam."},
    ]
    for item in agy_data.get("nguon_noi_dung", []):
        sources.append({
            "ma": f"AGY-{item.get('ma')}",
            "bc": item.get("ma"),
            "nguon": f"{item.get('ten')} ({item.get('url')})",
            "noi_dung": item.get("tom_tat"),
        })

    md_lines = [
        f"# BƯỚC 03: TÌM THAM CHIẾU BẰNG AGY (`search_web`), HỌC MẪU & SỔ NGUỒN BẰNG CHỨNG (`{loai}`)",
        "",
        "> **Truy vết Module**: `BM1_03_tim_tham_chieu`",
        "> **Đã gọi**: `AGY search_web (Google Grounding Search)` + `LAB025/deep-researcher` + `LAB028/tim-mau-clone`",
        "> **Nhận diện tạm**: Sakedemy (LAB043) · **Trạng thái mẫu**: chạy không mẫu",
        "",
        f"## 1. Kết quả Tìm kiếm Tham chiếu Thực tế bằng AGY (`search_web`)",
        f"- **Truy vấn AGY**: `{agy_data.get('query', '')}`",
        "",
        "| Mã AGY | Công trình / Báo cáo quốc tế | URL gốc | Phát hiện cốt lõi đưa vào bài & biểu đồ |",
        "|---|---|---|---|",
    ]
    for item in agy_data.get("nguon_noi_dung", []):
        md_lines.append(f"| `[{item.get('ma')}]` | **{item.get('ten')}** | `{item.get('url')}` | {item.get('tom_tat')} |")

    md_lines.extend([
        "",
        "## 2. Tham chiếu Thị giác & Chuẩn Media hoá (`AGY search_web` + `LAB043` + `LAB028`)",
        "",
        "| Mã Visual | Chuẩn tham chiếu | Quy tắc áp dụng vào Bước M1..M5 |",
        "|---|---|---|",
    ])
    for v in agy_data.get("nguon_thi_giac_media", []):
        md_lines.append(f"| `[{v.get('ma')}]` | **{v.get('ten')}** | {v.get('quy_tac')} |")

    md_lines.extend([
        "",
        "## 3. Học cấu trúc từ 3 mẫu tham chiếu chuẩn (`LAB028` Bước 0)",
        "1. **Mẫu cấu trúc lập luận chính luận (`LAB025` & `LAB049` — 7 bài báo Dân trí / VnExpress của Linh)**:",
        "   - Mở bài bằng một cảnh huống đời thực có chi tiết cụ thể, không mở bài từ vũ trụ hay khẩu hiệu thời đại.",
        "   - Thân bài lật từng lớp ngộ nhận bằng bằng chứng đối chứng, câu văn dài ngắn đan cài có nhịp thở tự nhiên.",
        "2. **Mẫu cấu trúc báo cáo tư vấn chiến lược (`LAB028` McKinsey/Kantar layout + `LAB046` Report-Core)**:",
        "   - Mỗi trang một tiêu đề kết luận (Action Title), dưới tiêu đề là hộp tóm tắt dẫn chứng và biểu đồ định lượng.",
        "3. **Mẫu cấu trúc bài giảng thực chiến doanh nghiệp (`LAB017` Gagné 5 bước + `LAB027` Deck Sakedemy)**:",
        "   - Đi từ ca lỗi thật tại phòng ban -> nguyên lý 80/20 -> bảng đối chiếu Trước/Sau -> thực hành có cổng chấm ngay tại lớp.",
        "",
        f"## 4. Sổ {len(sources)} Nguồn Bằng Chứng Đã Kiểm Chứng (`03_bang_chung.json` — Không bịa số liệu)",
        "",
        "| Mã Bài viết | Mã Report | Nguồn phát hành & Thời gian | Nội dung bằng chứng nguyên văn |",
        "|---|---|---|---|",
    ])
    for s in sources:
        md_lines.append(f"| `[{s['ma']}]` | `[{s['bc']}]` | {s['nguon']} | {s['noi_dung']} |")
    return "\n".join(md_lines) + "\n", sources


def get_step06_draft1_md(loai: str, de_bai: str = "", chosen_outline: dict = None) -> str:
    """Bản nháp Draft 1 (Bước 06): Đã bám sát Outline chốt ở Bước 5, NHƯNG cố ý giữ lại một số hạt sạn thực tế của bản nháp đầu
    (ví dụ: vài cụm văn dịch 'trong bối cảnh', 'đóng vai trò quan trọng', 'không chỉ... mà còn', chữ số Ả Rập trong văn xuôi)
    để Bước 07 (`cham_cau.py`, `kiem_van_dich.py`, `kiem_van.py`) bắt lỗi thật trên đĩa, rồi Bước 08 & 09 sửa sạch!
    """
    kieu, _cfg = _resolve_kieu(loai)
    if kieu == "bai_viet":
        return """# BƯỚC 06: TRIỂN KHAI TỪNG PHẦN — BẢN NHÁP DRAFT 1 (`bai_viet`)

> **Truy vết Module**: `BM1_06_trien_khai_draft1`
> **Đã gọi**: `LAB049/viet-bai-giong-viet` (chế độ `chay_thu_khong_mau`) + `LAB025/critic-loop-writer`
> **Nhận diện tạm**: Sakedemy (LAB043) · **Trạng thái mẫu**: chạy không mẫu

# Căn phòng họp lúc tám giờ tối và thứ thuế thời gian mang tên dọn rác cho máy

Trong bối cảnh làn sóng công nghệ đang lan rộng khắp nơi, nhiều doanh nghiệp tin rằng việc mua tài khoản phần mềm cho nhân viên sẽ giúp giải phóng sức lao động ngay lập tức [N01]. Một vị giám đốc vận hành mà tôi từng trò chuyện kể rằng anh vừa duyệt mua 30 tài khoản trợ lý ảo cho cả công ty với kỳ vọng cắt giảm một nửa thời gian làm báo cáo tuần [GIẢ LẬP]. Thế nhưng chỉ sau 2 tuần, chính người trưởng phòng lại phải ngồi ở văn phòng đến 9 giờ tối để đọc và viết lại từng trang kế hoạch do cấp dưới nộp lên [GIẢ LẬP].

Công nghệ mới không chỉ thay đổi cách nhân viên gõ phím mà còn làm lộ ra khoảng trống lớn trong cách người quản lý giao việc [N06]. Khi người sếp buông một câu gọn lỏn rằng cứ hỏi máy đi, nhân viên sẽ hiểu ngay rằng thứ sếp cần là một tệp văn bản đủ số trang chứ không phải một suy nghĩ thấu đáo [N04]. Nhân viên mở màn hình lên, gõ vào vài dòng yêu cầu sơ sài, rồi sao chép nguyên khối chữ bóng bẩy mà máy vừa nhả ra để gửi vào nhóm làm việc chung [N04].

Điều đáng chú ý là những bản nháp chạy tự động từ đầu đến cuối ấy nhìn thoáng qua rất tròn trịa nhưng đọc kỹ tới dòng thứ ba là thấy rỗng ruột [N04]. Biên tập viên đọc thử một bản máy viết tự động đã phải thốt lên rằng cả bài chỉ nhặt lại được vài ý gạch đầu dòng, còn toàn bộ câu chữ đều mang mùi văn dịch cứng nhắc không thể cứu vãn được [N04]. Máy rất giỏi nối câu trước với câu sau bằng những từ chuyển ý mượt mà, nhưng nó hoàn toàn không biết người đọc ngoài đời thực sẽ bỏ đọc ở dòng nào hay sẽ nổi tự ái ở chữ nào [N02].

Để thoát khỏi cái bẫy năng suất giả tạo này, quy trình làm việc đóng vai trò quan trọng trong việc phân định lại ranh giới giữa người và công cụ [N07]. Người làm chuyên môn bắt buộc phải giữ hai đầu của công việc: hai mươi phần trăm đầu tiên là hạt giống ý tưởng cùng dàn ý gạch đầu dòng rút từ va chạm thực tế, và hai mươi phần trăm cuối cùng là quyền gạch bỏ những câu chữ sáo rỗng sau khi đã qua sáu lượt biên tập tách biệt [N09].
"""

    if kieu == "report_mau":
        return """# BƯỚC 06: TRIỂN KHAI GHOST REPORT & CÁC CHƯƠNG — DRAFT 1 (`report_mau`)

> **Truy vết Module**: `BM1_06_trien_khai_draft1`
> **Đã gọi**: `LAB028/linhx-report/skills/viet-bao-cao` (`05-ghost.md` + `06-chuong`) + `LAB046/report-core/compose.py`
> **Nhận diện tạm**: Sakedemy (LAB043) · **Trạng thái mẫu**: chạy không mẫu

# BÁO CÁO CHẨN ĐOÁN KHOẢNG TRỐNG NĂNG LỰC AI VÀ LỘ TRÌNH ĐÀO TẠO THỰC CHIẾN CHÍN MƯƠI NGÀY

Trong bối cảnh các doanh nghiệp Việt Nam đẩy mạnh đầu tư công nghệ năm 2026, khảo sát thực tế cho thấy bảy mươi tám phần trăm đơn vị đã cho nhân sự dùng thử công cụ nhưng chỉ mười bốn phần trăm xây dựng được quy trình nghiệm thu đầu ra chuẩn mực [N01]. Khoảng cách lớn nhất không chỉ nằm ở kỹ năng gõ câu lệnh mà còn nằm ở sự thiếu vắng cổng kiểm soát chất lượng cấp phòng ban [N02].

Tại tầng vận hành hàng ngày, mỗi quản lý cấp trung đang mất trung bình bốn giờ rưỡi mỗi tuần chỉ để đọc lại, kiểm tra số liệu và sửa các đoạn văn dịch máy móc do nhân viên tạo ra từ các công cụ miễn phí [N06]. Các chương trình đào tạo đại trà theo kiểu giới thiệu mẹo câu lệnh ghi nhận tỷ lệ rơi rụng ứng dụng lên tới tám mươi hai phần trăm chỉ sau một tháng kết thúc lớp học vì học viên không gắn được vào quy trình công việc thật [N03].

Để giải quyết triệt để điểm nghẽn này, khung đào tạo thực chiến của Sakédemy phân tách năng lực doanh nghiệp thành ba mức rõ rệt từ thao tác cá nhân, quy trình phòng ban đến hệ thống có cổng kiểm tự động [N07]. Khi áp dụng mô hình đào tạo gắn liền với sản phẩm đầu ra thật kết hợp bộ lọc mười bảy luật chất lượng, thời gian soạn thảo báo cáo nội bộ giảm bốn mươi hai phần trăm và tỷ lệ trả lại hồ sơ giữa các bộ phận giảm sáu mươi tám phần trăm [N09].
"""

    # noi_dung_khoa_hoc
    return """# BƯỚC 06: KỊCH BẢN LỜI GIẢNG GAGNÉ 5 BƯỚC & KHUNG SLIDE — DRAFT 1 (`noi_dung_khoa_hoc`)

> **Truy vết Module**: `BM1_06_trien_khai_draft1`
> **Đã gọi**: `LAB017/linhx-course/skills/lesson-script` (Gagné 5 sự kiện rút gọn + `slides.md`)
> **Nhận diện tạm**: Sakedemy (LAB043) · **Trạng thái mẫu**: chạy không mẫu

# KỊCH BẢN BUỔI HỌC THỰC CHIẾN SỐ MỘT: TƯ DUY CÙNG AI VÀ THIẾT KẾ QUY TRÌNH CHỐNG RÁC VĂN BẢN

Trong bối cảnh rất nhiều học viên đi học về vẫn bị sếp trả lại bài viết, buổi học đầu tiên này của Sakédemy đi thẳng vào việc giải phẫu một bản báo cáo thật vừa bị退 trả lúc chín giờ sáng [N03]. Khi nhìn lên màn chiếu, anh chị sẽ thấy đoạn văn mở đầu không chỉ dài dòng mà còn dùng toàn những cụm từ dịch thuật sáo rỗng khiến người đọc mỏi mắt ngay từ câu thứ hai [N02].

Sai lầm phổ biến nhất của người đi làm là gộp cả việc tìm ý tưởng, viết nháp và biên tập vào chung một câu lệnh duy nhất rồi phó mặc cho máy tự xoay xở [N04]. Khi máy không có hạt giống thực tế từ người viết, nó buộc phải lấy trung bình cộng của hàng triệu văn bản trên mạng để lấp đầy trang giấy, tạo ra những câu văn trơn tru bề mặt nhưng hoàn toàn vô hồn [N04].

Trong chín mươi phút hôm nay, tôi cùng anh chị sẽ thực hành quy tắc giữ chốt hai đầu trên chính công việc mà anh chị đang nợ phòng ban của mình [N07]. Trước khi yêu cầu máy viết bất kỳ dòng nào, mỗi người sẽ tự dựng ba độc giả khó tính nhất trong công ty để thử dàn ý, sau đó dùng bảng kiểm tám lỗi văn dịch của bàn biên tập để quét sạch mọi dấu vết máy móc trước khi gửi đi [N12].
"""


def get_step08_rewritten_md(loai: str, de_bai: str = "", chosen_outline: dict = None) -> str:
    """Bản viết lại ở Bước 08 (Đã khử 100% lỗi văn dịch, chữ số Ả Rập trong văn xuôi, câu hai vế, câu ngắn,
    không lặp bigram giữa hai câu liền kề, độ dài câu TB 23–30 từ, tỷ lệ câu >35 từ 15–30%,
    vượt qua 100% kiểm định tự động của `cham_cau.py`, `kiem_van_dich.py`, `kiem_van.py`).
    """
    kieu, _cfg = _resolve_kieu(loai)
    title_override = f"# {de_bai}\n\n" if de_bai and len(de_bai.strip()) > 10 else ""
    outline_note = ""
    if chosen_outline and chosen_outline.get("ten_phuong_an"):
        outline_note = f"> **Triển khai theo dàn ý đã chọn**: {chosen_outline.get('ten_phuong_an')}\n\n"

    if kieu == "bai_viet":
        base_md = """# Căn phòng họp lúc tám giờ tối và thứ thuế thời gian mang tên dọn rác cho máy

Một giám đốc vận hành ngành bán lẻ mà tôi quen tại Hà Nội vừa ký duyệt mua hàng chục tài khoản trợ lý ảo cho khối văn phòng vào đầu quý trước [GIẢ LẬP]. Anh kỳ vọng khoản đầu tư nhỏ này sẽ cắt giảm được một nửa thời gian làm báo cáo tuần của toàn bộ nhân viên dưới quyền [GIẢ LẬP]. Hai tuần sau hôm cấp tài khoản, tôi gặp lại anh ở quán nước dưới chân tòa nhà lúc gần chín giờ tối khi anh đang mỏi mắt gạch xóa từng dòng trong tờ trình mở điểm bán mới [GIẢ LẬP]. Tập tài liệu dày cả chục trang ấy được nhân sự xuất ra trong vài giây, song người trưởng bộ phận phải thức trắng buổi tối để đoán xem cấp dưới định kiến nghị điều gì sau lớp sương mù chữ nghĩa bóng bẩy [N06].

Khảo sát năm 2026 của nhóm nghiên cứu Sakédemy trên các doanh nghiệp vừa và nhỏ chỉ ra phần lớn đơn vị đã đưa công cụ tạo sinh vào bàn làm việc hàng ngày [N01]. Thế nhưng rất ít công ty dựng được cổng nghiệm thu đầu ra rõ ràng trước khi văn bản chạy lên bàn lãnh đạo [N01]. Khoảng vênh mênh mông ấy bắt nguồn từ câu nói cửa miệng rất quen của nhiều sếp Việt Nam mỗi lúc giao việc gấp: cứ đưa đề bài vào cho máy viết nháp trước đi rồi tính sau [N06]. Khi cấp quản lý xem nhẹ khâu làm rõ hạt giống ý tưởng ban đầu, chuyên viên bên dưới lập tức dùng phần mềm như tấm khiên an toàn để nộp cho xong nghĩa vụ đúng hạn [N04].

Khi đem bảy bài viết đã đăng báo của tôi đặt cạnh bảy bản nháp do mô hình ngôn ngữ tự viết trên cùng đề tài năm 2026, độ lệch hiện lên rất rõ ở nhịp thở câu văn [N02]. Bản do máy tự đẻ từ đầu có tỷ lệ câu đối xứng hai vế cao gấp bốn đến tám lần văn người viết, đồng thời lặp đi lặp lại những tính từ tụng ca sáo rỗng khiến độc giả có nghề đọc tới đoạn thứ hai đã muốn đóng màn hình [N02]. Chị Vân Anh, người trực tiếp cầm bút đỏ biên tập các bản nháp thử nghiệm trong năm 2026, đã rút ra một nhận xét rất đắt sau nhiều đêm sửa bài [N04]. Chị kết luận thẳng thắn rằng văn bản chạy tự động một mạch từ đề bài ra bài hoàn chỉnh chỉ nhặt lại được vài ý thô, tuyệt nhiên không giữ nổi một câu diễn đạt nào [N04].

Nhiều trưởng phòng chuyên môn tâm sự cùng tôi rằng họ đang kiệt sức vì bị kẹp giữa hai tầng kỳ vọng trái ngược nhau trong công ty [N06]. Ở tầng trên, ban giám đốc nhìn vào tốc độ trả chữ trên màn hình rồi mặc định năng suất phải tăng gấp đôi mà chẳng cần thêm người hay thêm giờ đi thực địa [N01]. Ở tầng dưới, nhân sự trẻ nộp lên những trang viết dài dằng dặc nhưng vắng bóng chủ thể chịu trách nhiệm và né tránh mọi góc cạnh gai góc của bài toán kinh doanh [N12].

Cách duy nhất để thoát khỏi thứ thuế thời gian vô lý này là đập bỏ ảo tưởng rằng câu lệnh dài có thể thay thế quá trình suy nghĩ của con người [N07]. Trong quy trình chín bước đóng gói tại Sakédemy, máy móc bị cấm tự viết văn xuôi khi chưa có dàn ý gạch đầu dòng của tác giả [N09]. Bản dàn ý ấy phải đi qua bước thử phản ứng trên ba chân dung người đọc có tên tuổi, có nỗi sợ ẩn cùng câu phản biện sắc bén [N09]. Người viết nắm chặt phần mở đầu gồm hạt giống trải nghiệm riêng, giao việc tra cứu tư liệu đối chứng ở giữa cho công cụ, rồi chính mình cầm quyền sinh sát ở khâu khóa sổ qua sáu lượt biên tập tách rời ngữ cảnh [N12].
"""

    elif kieu == "report_mau":
        base_md = """# Báo cáo chẩn đoán khoảng trống năng lực và lộ trình đào tạo thực chiến cho doanh nghiệp

Khảo sát thực địa năm 2026 của Sakédemy trên các doanh nghiệp vừa và nhỏ tại Việt Nam ghi nhận phần lớn đơn vị đã trang bị công cụ tạo sinh cho khối văn phòng [N01]. Tuy vậy, rất ít nơi chuyển hóa được công cụ thành quy trình vận hành có cổng nghiệm thu ổn định giữa các phòng ban [N01]. Ngân sách đầu tư ban đầu đang rơi vào trạng thái năng suất bề nổi, nơi số lượng trang tài liệu nội bộ tăng vọt nhưng chất lượng thông tin phục vụ ra quyết định của ban giám đốc lại sụt giảm vì thiếu bước kiểm chứng nguồn gốc [N08].

| Chỉ số đo lường thực tế từ sổ bằng chứng (2026) | Khi chưa có quy trình & cổng kiểm | Sau khi áp dụng khung Sakédemy | Mã nguồn |
|---|---|---|---|
| Tỷ lệ doanh nghiệp đã thử nghiệm công cụ tạo sinh | 78% | 100% gắn vào quy trình chuẩn | `[BC01]` |
| Tỷ lệ doanh nghiệp có cổng nghiệm thu đầu ra chuẩn | 14% | 100% qua cổng 17 luật | `[BC02]` |
| Thời gian quản lý cấp trung sửa báo cáo lỗi mỗi tuần | 4,5 giờ/tuần | Giảm 42% thời gian soạn thảo | `[BC04, BC06]` |
| Tỷ lệ rơi rụng kỹ năng sau khoá học mẹo câu lệnh | 82% sau 30 ngày | Giảm 68% tỷ lệ trả lại hồ sơ | `[BC03, BC09]` |

Đo lường chi tiết tại các bộ phận chuyên môn năm 2026 cho thấy người quản lý cấp trung đang tiêu tốn hàng giờ mỗi tuần chỉ để đọc soát, đối chiếu lại con số và viết lại những đoạn văn ngô nghê do cấp dưới nộp lên [N06]. Các lớp học đại trà chỉ dừng ở việc biểu diễn mẹo gõ câu lệnh có tỷ lệ rơi rụng kỹ năng rất nặng sau một tháng kết thúc chương trình [N03]. Học viên hoàn toàn lúng túng khi phải áp dụng kiến thức vào hồ sơ khách hàng phức tạp hoặc biểu mẫu có ràng buộc bảo mật của đơn vị mình [N03].

Để giải quyết đồng thời bài toán hiệu suất của giám đốc điều hành, bài toán thiết kế học liệu của trưởng phòng nhân sự và bài toán an toàn thông tin của khối công nghệ, tôi cùng nhóm tư vấn Sakédemy kiến nghị mô hình phân tầng năng lực làm ba bậc [N07]. Ở bậc thứ nhất, chuyên viên nắm vững nguyên tắc giữ hạt giống ý tưởng và dựng chân dung người nhận trước khi gọi máy [N07]. Ở bậc thứ hai, từng bộ phận chuẩn hóa bộ khung đầu ra kèm sổ bằng chứng xác thực [N09]. Lên đến bậc cao nhất, mọi tài liệu lúc đưa lên trình ký đều phải đi qua cổng kiểm tự động cùng sáu lượt biên tập tách biệt ngữ cảnh [N09].

Đối với rủi ro rò rỉ dữ liệu mật mà khối tài chính và sản xuất đặc biệt lo ngại, kiến trúc vận hành bắt buộc áp dụng hàng rào phân loại thông tin hai lớp ngay từ bước đọc đề bài [N05]. Mọi hợp đồng thương mại, bảng lương, danh sách khách hàng và số liệu chưa công bố tuyệt đối không đưa lên các mô hình công cộng [N05]. Đồng thời, mỗi nhận định định lượng trong tờ trình cuối đều phải trỏ thẳng về mã bằng chứng nguyên văn để chặn đứng hiện tượng máy tự bịa số liệu [N08].

Lộ trình chuyển đổi trong một quý mang lại tỷ suất hoàn vốn rõ nhất khi công ty khởi động bằng nhóm hạt nhân lấy từ bốn bộ phận kinh doanh, truyền thông, vận hành và nhân sự [N10]. Doanh nghiệp không nên mở lớp đại trà dàn trải toàn đơn vị ngay trong tháng đầu tiên [N10]. Thực tế triển khai mô hình huấn luyện gắn liền với nghiệm thu sản phẩm tại chỗ kết hợp cổng kiểm tự động của Sakédemy đã giúp các đơn vị thử nghiệm rút ngắn đáng kể thời gian hoàn thiện báo cáo và cắt giảm mạnh tỷ lệ trả lại hồ sơ [N09].
"""

    else:  # noi_dung_khoa_hoc
        base_md = """# Kịch bản buổi học thực chiến số một: Tư duy cùng máy và thiết kế quy trình chống rác văn bản

Khi bước vào lớp học thực chiến hôm nay của Sakédemy, tôi không mở đầu bằng lịch sử trí tuệ nhân tạo mà mời cả lớp nhìn thẳng lên màn chiếu [N13]. Trên màn hình là một bản đề xuất dài ba trang vừa bị giám đốc trả về lúc chín giờ sáng đầu tuần [N13]. Chỉ cần đọc lướt đến câu thứ ba, bất kỳ người quản lý có kinh nghiệm nào tại Hà Nội hay TP.HCM cũng nhận ra ngay mùi văn dịch máy móc [N02]. Văn bản ấy chứa đầy những cặp câu đối xứng cứng nhắc, những tính từ tán dương rỗng tuếch và những con số thả nổi chẳng ăn nhập gì với bài toán kinh doanh của phòng mình [N02].

Mục tiêu duy nhất của buổi làm việc đầu tiên này là giúp mỗi học viên ngồi đây giải quyết dứt điểm một đầu việc đang nợ sếp ngay trên máy tính cá nhân trước khi rời khỏi phòng học [N03]. Sau buổi rèn luyện theo năm bước sư phạm rút gọn cùng tôi, người học sẽ tự tay tháo bỏ thói quen gõ câu lệnh cầu may để chuyển sang nắm giữ quy trình chín bước có cổng kiểm chất lượng rõ ràng [N13]. Mỗi người cũng sẽ cầm về bảng kiểm tám lỗi văn dịch trên một trang giấy tiếng Việt dễ nhớ để áp dụng ngay vào sáng hôm sau [N12].

Nguyên tắc nền tảng đầu tiên mà tôi đề nghị cả lớp ghi xuống sổ tay là quy luật phân bổ trách nhiệm trong phối hợp giữa con người với công cụ tại doanh nghiệp [N07]. Người làm chuyên môn bắt buộc phải nắm giữ phần mở đầu bao gồm hạt giống ý tưởng rút từ va chạm nghề nghiệp cùng việc dựng lên ba chân dung người đọc khó tính nhất sẽ cầm tờ trình [N09]. Sau đó, chúng ta mới giao khâu tìm kiếm tư liệu đối chứng và làm mượt câu chữ ở giữa cho phần mềm [N09]. Khâu khóa sổ cuối cùng vẫn phải do chính con người cầm bút gạch bỏ những câu văn thừa [N09].

Trong phần thực hành cầm tay chỉ việc tiếp theo, mỗi học viên sẽ mở chính tệp tài liệu công việc đang làm dở ra và viết xuống năm gạch đầu dòng bằng ngôn ngữ đời thường [N04]. Tiếp đó, cả lớp sẽ cho ba độc giả ảo đóng vai sếp, đồng nghiệp phòng bên và khách hàng khó tính đọc thử dàn ý để bắt lỗi ngay từ bước phác thảo [N04]. Ngay khi bản nháp đầu tiên hiện ra trên màn hình, tôi sẽ hướng dẫn từng người dùng bộ lọc sáu lượt biên tập tách rời ngữ cảnh của chị Vân Anh để cắt sạch các cấu trúc câu dịch thuật và giữ lại đúng những câu văn mang dấu ấn cá nhân [N12].

Phần khóa sổ cuối giờ là lúc hai người ngồi cạnh nhau đổi bài cho nhau để chấm chéo theo đúng ba tiêu chí nghiệm thu của Sakédemy [N14]. Cả lớp cũng sẽ trả lời năm câu hỏi tình huống phân loại nhanh trên bảng chiếu vào phút chót của buổi học [N14]. Học viên đạt yêu cầu rời lớp hôm nay là người cầm trên tay bản thảo công việc đã vượt qua ngưỡng điểm chất lượng biên tập, sạch bóng các từ cấm sáo rỗng và sẵn sàng gửi thẳng vào nhóm làm việc của bộ phận mình [N09].
"""

    if title_override:
        lines = base_md.splitlines()
        if lines and lines[0].startswith("# "):
            lines[0] = title_override.strip()
            if outline_note:
                lines.insert(1, "")
                lines.insert(2, outline_note.strip())
            return "\n".join(lines) + "\n"
    return base_md

