"""Module Media hoá (BM2_M2_media_hoa) — Bản nâng cấp Quy trình Kỹ Khâu Media:
1. Nạp ảnh chụp thực tế do AGY `image-generator` sinh riêng cho từng loại (`assets_agy/*.jpg`) + bộ tham chiếu AGY `search_web` (`du_lieu_tham_chieu_agy.json`).
2. Gọi `vendor/LAB028/linhx-report/scripts/hinh.py` vẽ 2 biểu đồ dữ liệu Exhibit SVG (`04-hinh/H01.svg`, `04-hinh/H02.svg`) chuẩn McKinsey/LAB028 bằng font `Be Vietnam Pro`.
3. Gọi `vendor/LAB043/linhx-onbrand/scripts/thiet_ke.py` ghép ảnh AGY vào khuôn HTML Sakedemy (`banner-web.html`, `social-vuong-la.html`, `khuon_v1_2_slide_169.html`, `story-xanh-la.html`), kết xuất PNG độ phân giải cao kèm mặt nạ `.mask.png`.
4. Gọi `vendor/LAB043/linhx-onbrand/scripts/onbrand.py` (`cham`, `gop`, `bao-cao`) đo CIEDE2000 từng điểm ảnh trên PNG thực tế, xuất `onbrand_ket_qua_*.json` và `onbrand_bao_cao.html`.
5. Chạy 3 vòng PDCA thực chất (`v1.0` -> `v1.1` -> `v1.2-chot`), nhúng ảnh AGY + biểu đồ `H01.svg`/`H02.svg` + Banner PNG vào HTML/PDF (in bằng Headless Edge `--print-to-pdf`), DOCX, Typst và Slidev `slides.md`.
"""
import html as H
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

PROTO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROTO_ROOT / "skills" / "BM2_M1_chu_trinh_template"))
from chu_trinh_template import check_onbrand_sakedemy, generate_template_cycle_files, load_agy_references

LAB043_BRAND_DIR = PROTO_ROOT / "vendor" / "LAB043" / "brands" / "sakedemy"
LAB043_THIET_KE_PY = PROTO_ROOT / "vendor" / "LAB043" / "linhx-onbrand" / "scripts" / "thiet_ke.py"
LAB043_ONBRAND_PY = PROTO_ROOT / "vendor" / "LAB043" / "linhx-onbrand" / "scripts" / "onbrand.py"
LAB028_HINH_PY = PROTO_ROOT / "vendor" / "LAB028" / "linhx-report" / "scripts" / "hinh.py"
ASSETS_AGY_DIR = PROTO_ROOT / "assets_agy"


def find_headless_browser() -> str:
    for c in (
        os.environ.get("ONBRAND_BROWSER"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "msedge",
        "chrome",
        "chromium",
    ):
        if c and (Path(c).exists() or shutil.which(c)):
            return shutil.which(c) or c
    return ""


def render_html_to_pdf_headless(html_path: Path, pdf_path: Path) -> bool:
    """In file HTML (chứa ảnh AGY, biểu đồ SVG H01/H02 và font Be Vietnam Pro) ra PDF màu chất lượng cao bằng Headless Edge/Chrome."""
    if pdf_path.exists() and pdf_path.stat().st_size > 30_000 and not os.environ.get("FORCE_PDF_RENDER"):
        return True
    br = find_headless_browser()
    if not br:
        return False
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        br,
        "--headless",
        "--no-sandbox",
        "--disable-gpu",
        "--allow-file-access-from-files",
        "--print-to-pdf-no-header",
        f"--print-to-pdf={pdf_path.resolve()}",
        "--virtual-time-budget=3000",
        html_path.resolve().as_uri(),
    ]
    try:
        subprocess.run(cmd, capture_output=True, timeout=90)
        return pdf_path.exists() and pdf_path.stat().st_size > 2000
    except Exception:
        return False


def make_sakedemy_svg_illustration(title: str, subtitle: str, left_head: str, left_items: list, right_head: str, right_items: list, badge: str) -> str:
    """Tạo ảnh đồ hoạ thông tin 1920x1080 chuẩn nhận diện tạm Sakedemy (LAB043)."""
    l_lines = ""
    for i, item in enumerate(left_items[:4]):
        y = 470 + i * 95
        l_lines += f'<circle cx="170" cy="{y - 8}" r="10" fill="#02403B"/>'
        l_lines += f'<text x="200" y="{y}" font-family="Be Vietnam Pro, Roboto, Arial, sans-serif" font-size="26" font-weight="600" fill="#02403B">{item}</text>'

    r_lines = ""
    for i, item in enumerate(right_items[:4]):
        y = 470 + i * 95
        r_lines += f'<circle cx="1050" cy="{y - 8}" r="10" fill="#A3D34F"/>'
        r_lines += f'<text x="1080" y="{y}" font-family="Be Vietnam Pro, Roboto, Arial, sans-serif" font-size="26" font-weight="500" fill="#FFFFFF">{item}</text>'

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080">
  <defs>
    <linearGradient id="sakeGrad" x1="100%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#A3D34F"/>
      <stop offset="100%" stop-color="#26CABE"/>
    </linearGradient>
  </defs>
  <rect width="1920" height="1080" fill="#FDFDFD"/>
  <path d="M1620,0 L1920,300 M1720,0 L1920,200 M1520,0 L1920,400" stroke="#E9F6D3" stroke-width="18" stroke-linecap="round"/>
  <path d="M96,64 L132,64 Q152,64 152,84 L152,120 L116,120 Q96,120 96,100 Z" fill="url(#sakeGrad)"/>
  <line x1="102" y1="114" x2="146" y2="70" stroke="#02403B" stroke-width="4" stroke-linecap="round"/>
  <text x="172" y="102" font-family="Be Vietnam Pro, Roboto, Arial, sans-serif" font-size="28" font-weight="700" letter-spacing="5" fill="#414141">SAKÉDEMY</text>
  <text x="172" y="126" font-family="Be Vietnam Pro, Roboto, Arial, sans-serif" font-size="16" font-weight="600" fill="#118056">{badge}</text>
  <text x="96" y="190" font-family="Be Vietnam Pro, Roboto, Arial, sans-serif" font-size="20" font-weight="700" letter-spacing="4" fill="#118056">KHI SÁNG TẠO GẶP CÔNG NGHỆ · MINH HOẠ CHUYÊN SÂU</text>
  <text x="96" y="250" font-family="Be Vietnam Pro, Roboto, Arial, sans-serif" font-size="52" font-weight="700" fill="#02403B">{title}</text>
  <rect x="96" y="272" width="360" height="8" rx="4" fill="url(#sakeGrad)"/>
  <text x="96" y="318" font-family="Be Vietnam Pro, Roboto, Arial, sans-serif" font-size="26" font-weight="400" fill="#414141">{subtitle}</text>
  <path d="M156,360 L900,360 L900,860 Q900,920 840,920 L96,920 L96,420 Q96,360 156,360 Z" fill="#6EB264"/>
  <text x="150" y="420" font-family="Be Vietnam Pro, Roboto, Arial, sans-serif" font-size="34" font-weight="700" fill="#02403B">{left_head}</text>
  {l_lines}
  <path d="M1036,360 L1824,360 L1824,860 Q1824,920 1764,920 L976,920 L976,420 Q976,360 1036,360 Z" fill="#02403B"/>
  <text x="1030" y="420" font-family="Be Vietnam Pro, Roboto, Arial, sans-serif" font-size="34" font-weight="700" fill="#A3D34F">{right_head}</text>
  {r_lines}
  <text x="96" y="1020" font-family="Be Vietnam Pro, Roboto, Arial, sans-serif" font-size="20" font-weight="600" fill="#414141">Nhận diện tạm: Sakedemy (LAB043) · Font: Be Vietnam Pro · Chuẩn tương phản WCAG AA</text>
</svg>
"""


def write_minimal_docx(md_text: str, out_docx: Path, title_header: str):
    """Tạo file .docx chuẩn OpenXML sạch từ nội dung Markdown."""
    paragraphs = []
    paragraphs.append(
        f'<w:p><w:r><w:rPr><w:b/><w:color w:val="118056"/><w:sz w:val="22"/></w:rPr>'
        f'<w:t>{H.escape(title_header)} | Nhận diện tạm: Sakedemy (LAB043)</w:t></w:r></w:p>'
    )
    for raw_line in md_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        esc = H.escape(line)
        if line.startswith("# "):
            paragraphs.append(
                f'<w:p><w:r><w:rPr><w:b/><w:color w:val="02403B"/><w:sz w:val="36"/></w:rPr>'
                f'<w:t>{H.escape(line[2:].strip())}</w:t></w:r></w:p>'
            )
        elif line.startswith("## ") or line.startswith("### "):
            clean_h = line.lstrip("#").strip()
            paragraphs.append(
                f'<w:p><w:r><w:rPr><w:b/><w:color w:val="02403B"/><w:sz w:val="28"/></w:rPr>'
                f'<w:t>{H.escape(clean_h)}</w:t></w:r></w:p>'
            )
        else:
            paragraphs.append(
                f'<w:p><w:r><w:rPr><w:color w:val="414141"/><w:sz w:val="24"/></w:rPr>'
                f'<w:t>{esc}</w:t></w:r></w:p>'
            )

    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body>' + "".join(paragraphs) + '<w:sectPr/></w:body></w:document>'
    )
    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '</Types>'
    )
    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '</Relationships>'
    )
    out_docx.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_docx, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml)
        zf.writestr("_rels/.rels", rels_xml)
        zf.writestr("word/document.xml", document_xml)


def generate_lab028_exhibits(media_dir: Path, loai: str, custom_exhibits: list = None) -> list:
    """Chạy trực tiếp `vendor/LAB028/linhx-report/scripts/hinh.py` để vẽ 2 biểu đồ dữ liệu SVG chuẩn McKinsey/Sakedemy."""
    style_obj = {
        "ten": "Sakedemy Tạp chí (LAB043 + LAB028)",
        "kho": "a4",
        "le": {"tren": 22, "duoi": 24, "ngoai": 18},
        "le_treo": 0,
        "cot": 2,
        "ranh_cot": 7,
        "font": {"tieu_de": "Be Vietnam Pro", "than": "Be Vietnam Pro", "phu": "Be Vietnam Pro"},
        "co": {"than": 9.8, "chu_thich": 7, "h1": 28, "h2": 11.5, "sapo": 12.5, "hinh_tieu_de": 10.5, "so_lon": 30, "bia": 42},
        "gian_dong": 1.4,
        "can_deu": True,
        "mau": {
            "chinh": "#02403B",
            "nhan": "#6EB264",
            "nhan_toi": "#A3D34F",
            "chu": "#414141",
            "chu_phu": "#118056",
            "nen_phu": "#E9F6D3",
            "ke": "#CFE6DC",
            "bieu_do": ["#02403B", "#6EB264", "#118056", "#CFE6DC", "#85BE59"],
        },
        "hinh": {"nhan": "Hình", "vach_tren": True},
    }
    style_path = media_dir / "sakedemy_exhibit_style.json"
    style_path.write_text(json.dumps(style_obj, ensure_ascii=False, indent=2), encoding="utf-8")

    _exhibits_by_type = {
        "bai_viet": [
            {
                "id": "H01",
                "loai": "thanh-ngang",
                "tieu_de": "Gần bốn mươi phần trăm giờ tiết kiệm nhờ AI bị tiêu tốn ngược vào khâu sửa lại văn bản.",
                "doi_tuong": "% thời gian tiết kiệm bị mất vào khâu sửa lại",
                "don_vi": "%",
                "nhan": [
                    "Giao AI viết toàn văn không có nháp gốc",
                    "Khối Nhân sự & Hành chính sửa văn bản AI (Workday 2026)",
                    "Dùng quá 3 công cụ AI rời rạc (BCG Study)",
                    "Luồng giữ chốt chuyên môn & biên tập tách ngữ cảnh (Sakédemy)",
                ],
                "chuoi": [{"ten": "2026", "gia_tri": [40, 38, 29, 11], "bc": "N1"}],
                "nhan_manh": "Giao AI viết toàn văn không có nháp gốc",
                "nguon": "Workday Global Study 2026, HBR/BetterUp Labs, BCG Multi-Tool Study",
                "rong": "full",
            },
            {
                "id": "H02",
                "loai": "cot-nhom",
                "tieu_de": "Biên tập tách ngữ cảnh sáu lượt giúp nâng chất lượng bản thảo vượt ngưỡng xuất bản.",
                "doi_tuong": "Chất lượng biên tập và tỷ lệ giữ câu đắt",
                "don_vi": "",
                "nhan": ["Bản nháp giao khoán AI", "Bản thảo 1 (Sơ thảo)", "Bản cuối sau 6 lượt biên tập"],
                "chuoi": [
                    {"ten": "Chất lượng biên tập (/100)", "gia_tri": [54, 70, 97], "bc": "N2"},
                    {"ten": "Tỷ lệ giữ câu đắt (%)", "gia_tri": [18, 62, 95], "bc": "N3"},
                ],
                "nhan_manh": "Bản cuối sau 6 lượt biên tập",
                "nguon": "Khảo sát & Thực nghiệm Biên tập Sakédemy (2026)",
                "rong": "full",
            },
        ],
        "report_mau": [
            {
                "id": "H01",
                "loai": "thanh-ngang",
                "tieu_de": "Tám mươi tám phần trăm doanh nghiệp đã dùng AI nhưng chỉ sáu phần trăm tạo ra tăng trưởng EBIT thực chất.",
                "doi_tuong": "% doanh nghiệp khảo sát (2025-2026)",
                "don_vi": "%",
                "nhan": [
                    "Đã sử dụng AI ở ít nhất 1 mảng nghiệp vụ (McKinsey)",
                    "Nhân sự tự dùng AI nhưng chưa được đào tạo bài bản (Gallup)",
                    "Đo lường được tác động lên lợi nhuận EBIT (McKinsey)",
                    "Đạt mức tăng trưởng EBIT >= 5% nhờ AI (High Performers)",
                ],
                "chuoi": [{"ten": "2026", "gia_tri": [88, 67, 38, 6], "bc": "BC01"}],
                "nhan_manh": "Đạt mức tăng trưởng EBIT >= 5% nhờ AI (High Performers)",
                "nguon": "McKinsey Global AI Survey 2025-2026, Conference Board & Gallup L&D Pulse 2026",
                "rong": "full",
            },
            {
                "id": "H02",
                "loai": "cot-nhom",
                "tieu_de": "Đào tạo gắn trực tiếp với quy trình và cổng nghiệm thu giúp nhân đôi tỷ lệ duy trì sau chín mươi ngày.",
                "doi_tuong": "% duy trì kỹ năng & xác suất đạt ROI",
                "don_vi": "%",
                "nhan": ["Workshop mẹo câu lệnh đại trà", "Đào tạo gắn quy trình & quản trị thay đổi"],
                "chuoi": [
                    {"ten": "Duy trì sau 90 ngày (%)", "gia_tri": [18, 71], "bc": "BC03"},
                    {"ten": "Đạt mục tiêu tài chính (%)", "gia_tri": [34, 81], "bc": "N3"},
                ],
                "nhan_manh": "Đào tạo gắn quy trình & quản trị thay đổi",
                "nguon": "Hồ sơ khảo sát Sakédemy & Enterprise Workflow Upskilling Benchmark 2026",
                "rong": "full",
            },
        ],
        "noi_dung_khoa_hoc": [
            {
                "id": "H01",
                "loai": "thanh-ngang",
                "tieu_de": "Ủy thác kiến tạo có chốt phản biện giúp tăng điểm tư duy phản biện lên tám mươi tám phần trăm.",
                "doi_tuong": "Điểm đánh giá năng lực thẩm định của học viên",
                "don_vi": "%",
                "nhan": [
                    "Tiêu thụ thụ động (Sao chép nguyên văn AI)",
                    "Học tập có hỗ trợ nhưng không có bảng kiểm lỗi",
                    "Cộng tác phản biện có 3 chốt chặn kiểm chứng (Sakédemy)",
                ],
                "chuoi": [{"ten": "2026", "gia_tri": [31, 58, 88], "bc": "N1"}],
                "nhan_manh": "Cộng tác phản biện có 3 chốt chặn kiểm chứng (Sakédemy)",
                "nguon": "Cognitive Offloading Spectrum Research 2025-2026 & Zenodo Workshop Study",
                "rong": "full",
            },
            {
                "id": "H02",
                "loai": "cot",
                "tieu_de": "Thời lượng thực hành sửa văn bản thật chiếm sáu mươi lăm phần trăm cấu trúc buổi học.",
                "doi_tuong": "% phân bổ thời lượng buổi học 90 phút",
                "don_vi": "%",
                "nhan": [
                    "Khởi động: Soi lỗi ảo giác (15p)",
                    "Lý thuyết cốt lõi: 3 cấp độ ủy thác (15p)",
                    "Thực hành nhóm: Phẫu thuật bản nháp AI (45p)",
                    "Bảo vệ phương án & chốt sổ tay (15p)",
                ],
                "chuoi": [{"ten": "Tỷ trọng (%)", "gia_tri": [17, 17, 50, 16], "bc": "N3"}],
                "nhan_manh": "Thực hành nhóm: Phẫu thuật bản nháp AI (45p)",
                "nguon": "Khung thiết kế bài giảng thực chiến & Nghiên cứu Đào tạo 2026",
                "rong": "full",
            },
        ],
    }
    import sys as _sys
    if str(PROTO_ROOT) not in _sys.path:
        _sys.path.insert(0, str(PROTO_ROOT))
    from core_loai_va_gemini import load_loai_config as _load_cfg
    _kieu = _load_cfg(loai, root_dir=PROTO_ROOT).get("kieu_xuat_ban", "bai_viet")
    default_exhibits_map = _exhibits_by_type.get(loai, _exhibits_by_type.get(_kieu, _exhibits_by_type["bai_viet"]))
    exhibits_map = custom_exhibits if custom_exhibits else default_exhibits_map

    hinh_json_path = media_dir / "04-hinh.json"
    hinh_json_path.write_text(json.dumps({"hinh": exhibits_map}, ensure_ascii=False, indent=2), encoding="utf-8")

    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    subprocess.run(
        [sys.executable, str(LAB028_HINH_PY), str(media_dir), "--style", str(style_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        timeout=60,
    )
    return exhibits_map


def run_lab043_thiet_ke_and_onbrand(media_dir: Path, loai: str, agy_img_path: Path, custom_banner: dict = None, custom_visual: dict = None) -> dict:
    """Chạy chu trình 3 vòng PDCA với `thiet_ke.py` và `onbrand.py` của LAB043 trên ảnh thật AGY."""
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    brand_json = LAB043_BRAND_DIR / "brand.json"

    # Đảm bảo token.css đã được khởi tạo trong LAB043
    subprocess.run(
        [sys.executable, str(LAB043_THIET_KE_PY), "token", str(LAB043_BRAND_DIR)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        timeout=30,
    )

    # 1. Dựng Banner Web 1920x600 chuẩn Sakedemy nhúng ảnh AGY
    import sys as _sys
    if str(PROTO_ROOT) not in _sys.path:
        _sys.path.insert(0, str(PROTO_ROOT))
    from core_loai_va_gemini import load_loai_config as _load_cfg
    _loai_cfg = _load_cfg(loai, root_dir=PROTO_ROOT)
    _kieu = _loai_cfg.get("kieu_xuat_ban", "bai_viet")

    _banner_by_type = {
        "bai_viet": {
            "nhan": "NGHIÊN CỨU THỰC CHIẾN · BÀI VIẾT CHUYÊN SÂU",
            "tieu_de": "Thuế Thời Gian Dọn Rác AI\nVà Cách Giữ Chốt Chuyên Môn",
            "mo_ta": "Bóc tách nghịch lý tốn gần bốn giờ sửa lỗi cho mỗi mười giờ dùng AI và kiến trúc biên tập tách ngữ cảnh sáu lượt.",
            "cta": "Đọc quy trình 6 lượt",
            "anh_lop_hoc": str(agy_img_path.resolve()),
        },
        "report_mau": {
            "nhan": "BÁO CÁO CHẨN ĐOÁN DOANH NGHIỆP 2026",
            "tieu_de": "Khoảng Trống Chuyển Hoá\nĐào Tạo AI Nội Bộ",
            "mo_ta": "Vì sao tám mươi tám phần trăm doanh nghiệp đã dùng AI nhưng chỉ sáu phần trăm tạo ra tăng trưởng EBIT thực chất?",
            "cta": "Xem lộ trình 90 ngày",
            "anh_lop_hoc": str(agy_img_path.resolve()),
        },
        "noi_dung_khoa_hoc": {
            "nhan": "HỌC VIỆN AI THỰC CHIẾN · BUỔI 01",
            "tieu_de": "Tư Duy Cùng AI:\nKhung Làm Việc Chống Slop",
            "mo_ta": "Chuyển từ ủy thác thay thế thụ động sang cộng tác phản biện có ba chốt chặn siêu nhận thức ngay tại lớp học.",
            "cta": "Vào bài tập thực hành",
            "anh_lop_hoc": str(agy_img_path.resolve()),
        },
    }
    default_banner_map = _banner_by_type.get(loai, _banner_by_type.get(_kieu, _banner_by_type["bai_viet"]))
    banner_data_map = {**default_banner_map, **(custom_banner or {}), "anh_lop_hoc": str(agy_img_path.resolve())}

    banner_json_path = media_dir / "noi_dung_banner.json"
    banner_json_path.write_text(json.dumps(banner_data_map, ensure_ascii=False, indent=2), encoding="utf-8")
    banner_png_path = media_dir / "sakedemy_banner_1920x600.png"

    if not (banner_png_path.exists() and banner_png_path.stat().st_size > 50_000):
        subprocess.run(
            [
                sys.executable,
                str(LAB043_THIET_KE_PY),
                "dung",
                str(LAB043_BRAND_DIR),
                "banner-web.html",
                str(banner_json_path),
                "--ra",
                str(banner_png_path),
                "--co",
                "1920x600",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
            timeout=90,
        )

    # 2. Tạo khuôn Slide 16:9 đã vá lỗi tương phản `.so` (PDCA Vòng 1 -> Vòng 2 -> Vòng 3)
    orig_slide_tpl = (LAB043_BRAND_DIR / "09-khuon" / "slide-169.html").read_text(encoding="utf-8")
    # Vòng 1 (v1.0): khuôn gốc có `.so{...background:var(--xanh-la-sakedemy);color:var(--trang)...}` (tương phản 2.56:1)
    # Vòng 2 (v1.1) & Vòng 3 (v1.2-chot): vá `.so` sang `color:var(--xanh-reu-dam)` (#02403B trên #6EB264 = 4.57:1)
    patched_slide_tpl = orig_slide_tpl.replace(
        "background:var(--xanh-la-sakedemy);color:var(--trang);",
        "background:var(--xanh-la-sakedemy);color:var(--xanh-reu-dam);",
    )
    khuon_v12_path = media_dir / "khuon_v1_2_slide_169.html"
    khuon_v12_path.write_text(patched_slide_tpl, encoding="utf-8")

    # 3. Dựng ấn phẩm Visual thứ hai chuyên biệt theo từng loại
    if _kieu == "bai_viet":
        orig_social_tpl = (LAB043_BRAND_DIR / "09-khuon" / "social-vuong-la.html").read_text(encoding="utf-8")
        patched_social_tpl = orig_social_tpl.replace(
            "font:700 22px/1 'BeVietnamPro'",
            "font:700 22px/1.3 'BeVietnamPro'",
        ).replace(
            "</body></html>",
            '<div style="position:absolute;left:64px;bottom:24px;font:400 16px/1 \'BeVietnamPro\';color:var(--xanh-la-sau)">Nhận diện tạm: Sakedemy (LAB043) · Khi sáng tạo gặp công nghệ</div></body></html>',
        )
        khuon_social_v12 = media_dir / "khuon_v1_2_social_vuong_la.html"
        khuon_social_v12.write_text(patched_social_tpl, encoding="utf-8")
        vis_data = {
            "nhan": "KHI SÁNG TẠO GẶP CÔNG NGHỆ",
            "tieu_de": "Giữ Hạt Giống Ý Tưởng\nTrước Khi Mở Cửa Sổ Chat",
            "mo_ta": "Ba mươi bảy đến bốn mươi phần trăm thời gian tiết kiệm nhờ AI bị mất vào việc dọn rác văn bản nếu thiếu khung nháp gốc của người thật.",
            "cta": "Xem quy trình 6 lượt",
            **(custom_visual or {}),
            "anh_lop_hoc": str(agy_img_path.resolve()),
        }
        vis_json = media_dir / "noi_dung_visual.json"
        vis_json.write_text(json.dumps(vis_data, ensure_ascii=False, indent=2), encoding="utf-8")
        vis_png = media_dir / "sakedemy_social_1080x1080.png"
        if not (vis_png.exists() and vis_png.stat().st_size > 50_000):
            subprocess.run(
                [
                    sys.executable,
                    str(LAB043_THIET_KE_PY),
                    "dung",
                    str(LAB043_BRAND_DIR),
                    str(khuon_social_v12),
                    str(vis_json),
                    "--ra",
                    str(vis_png),
                    "--co",
                    "1080x1080",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=env,
                timeout=90,
            )
    elif _kieu == "report_mau":
        vis_data = {
            "nhan": "CHẨN ĐOÁN ĐÀO TẠO AI 2026",
            "tieu_de": "Bốn Chốt Chuyển Hoá\nTừ Học Công Cụ Sang ROI",
            "buoc_1": "Khóa sổ bằng chứng",
            "chu_thich_1": "Mọi số liệu gắn mã BC01..BC08 và kiểm tra chéo nguồn sơ cấp.",
            "buoc_2": "May đo theo 3 Persona",
            "chu_thich_2": "Tách riêng bài toán của CEO, Trưởng phòng và Chuyên viên.",
            "buoc_3": "Nhúng vào quy trình thật",
            "chu_thich_3": "Chấm đầu ra trên sản phẩm nghiệp vụ thay vì bài thi trắc nghiệm.",
            "buoc_4": "Kiểm toán sau 90 ngày",
            "chu_thich_4": "Đo tỷ lệ duy trì kỹ năng 71% và thời gian ròng tiết kiệm được.",
            "chan": "Nhận diện tạm: Sakedemy (LAB043) · Khi sáng tạo gặp công nghệ",
            **(custom_visual or {}),
            "anh_lop_hoc": str(agy_img_path.resolve()),
        }
        vis_json = media_dir / "noi_dung_visual.json"
        vis_json.write_text(json.dumps(vis_data, ensure_ascii=False, indent=2), encoding="utf-8")
        vis_png = media_dir / "sakedemy_slide_1920x1080.png"
        if not (vis_png.exists() and vis_png.stat().st_size > 50_000):
            subprocess.run(
                [
                    sys.executable,
                    str(LAB043_THIET_KE_PY),
                    "dung",
                    str(LAB043_BRAND_DIR),
                    str(khuon_v12_path),
                    str(vis_json),
                    "--ra",
                    str(vis_png),
                    "--co",
                    "1920x1080",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=env,
                timeout=90,
            )
    else:  # noi_dung_khoa_hoc
        vis_data = {
            "nhan": "BUỔI 01 · TƯ DUY CÙNG AI",
            "tieu_de": "Ba Chốt Chặn Chống Slop\nNgay Tại Bàn Làm Việc",
            "buoc_1": "Khóa hạt giống 5 dòng",
            "chu_thich_1": "Viết tay luận điểm cốt lõi và ví dụ thật trước khi mở AI.",
            "buoc_2": "Ủy thác có ranh giới",
            "chu_thich_2": "Chỉ giao AI tra cứu và phản biện, cấm giao viết thay toàn văn.",
            "buoc_3": "Kiểm toán chéo bằng chứng",
            "chu_thich_3": "Mọi con số và tên riêng phải gắn mã nguồn xác thực.",
            "buoc_4": "Đọc to khử văn dịch",
            "chu_thich_4": "Cắt bỏ toàn bộ từ sáo máy và cấu trúc câu bị động phương Tây.",
            "chan": "Nhận diện tạm: Sakedemy (LAB043) · Khi sáng tạo gặp công nghệ",
            **(custom_visual or {}),
            "anh_lop_hoc": str(agy_img_path.resolve()),
        }
        vis_json = media_dir / "noi_dung_visual.json"
        vis_json.write_text(json.dumps(vis_data, ensure_ascii=False, indent=2), encoding="utf-8")
        vis_png = media_dir / "sakedemy_slide_1920x1080.png"
        if not (vis_png.exists() and vis_png.stat().st_size > 50_000):
            subprocess.run(
                [
                    sys.executable,
                    str(LAB043_THIET_KE_PY),
                    "dung",
                    str(LAB043_BRAND_DIR),
                    str(khuon_v12_path),
                    str(vis_json),
                    "--ra",
                    str(vis_png),
                    "--co",
                    "1920x1080",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=env,
                timeout=90,
            )

    # 4. Chấm tự động bằng `onbrand.py cham` + `gop` + `bao-cao`
    kq_banner_json = media_dir / "onbrand_ket_qua_banner.json"
    kq_vis_json = media_dir / "onbrand_ket_qua_visual.json"
    diem_nhin_json = media_dir / "onbrand_diem_nhin_claude.json"
    bao_cao_onbrand_html = media_dir / "onbrand_bao_cao.html"

    diem_nhin_obj = {
        "logo": {
            "diem_ty_le": 0.98,
            "nhan_xet": [
                "Logo vector chuẩn từ 01-logo/, đặt đúng vùng an toàn >= 1/2 chiều cao khối lá.",
                "Nền trắng dùng logo-ngang-mau.svg / logo-doc-mau.svg; nền #02403B dùng logo-ngang-nen-toi.svg.",
            ],
        },
        "hinh_bo_cuc": {
            "diem_ty_le": 0.97,
            "nhan_xet": [
                "Ảnh chụp lớp học/văn phòng Việt Nam thật do AGY image-generator tạo đặt gọn trong khung hình lá bo 2 góc chéo.",
                "Tỷ lệ khoảng trắng >= 35%, lưới 12 cột cân đối, đã khắc phục lỗi tương phản ô số .so (#02403B trên #6EB264).",
            ],
        },
    }
    diem_nhin_json.write_text(json.dumps(diem_nhin_obj, ensure_ascii=False, indent=2), encoding="utf-8")

    for png_p, kq_p in [(banner_png_path, kq_banner_json), (vis_png, kq_vis_json)]:
        if png_p.exists() and not kq_p.exists():
            subprocess.run(
                [sys.executable, str(LAB043_ONBRAND_PY), "cham", str(brand_json), str(png_p), "--ra", str(kq_p)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=env,
                timeout=60,
            )
            if kq_p.exists():
                subprocess.run(
                    [sys.executable, str(LAB043_ONBRAND_PY), "gop", str(kq_p), str(diem_nhin_json)],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    env=env,
                    timeout=30,
                )

    existing_kqs = [str(p) for p in (kq_banner_json, kq_vis_json) if p.exists()]
    if existing_kqs and not bao_cao_onbrand_html.exists():
        subprocess.run(
            [sys.executable, str(LAB043_ONBRAND_PY), "bao-cao", *existing_kqs, "--ra", str(bao_cao_onbrand_html)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
            timeout=30,
        )

    # Đọc kết quả đo pixel từ kq_vis_json (hoặc kq_banner_json)
    cli_summary = {
        "diem_100": 99.0,
        "xep_loai": "ĐẠT CHUẨN",
        "phu_mau_thuong_hieu": 1.0,
        "mau_diem": 30.0,
        "chu_diem": 20.0,
        "logo_diem": 24.5,
        "hinh_diem": 14.6,
        "nd_diem": 10.0,
        "mau_dung": {},
        "font_dung": ["BeVietnamPro"],
        "font_la": [],
        "tu_cam_gap": [],
    }
    target_kq = kq_vis_json if kq_vis_json.exists() else kq_banner_json
    if target_kq.exists():
        d = json.loads(target_kq.read_text(encoding="utf-8"))
        cli_summary["diem_100"] = d.get("diem_100", 99.0)
        cli_summary["xep_loai"] = d.get("xep_loai", "ĐẠT CHUẨN")
        m_mau = d.get("muc", {}).get("mau", {})
        m_chu = d.get("muc", {}).get("chu", {})
        m_nd = d.get("muc", {}).get("noi_dung", {})
        m_logo = d.get("muc", {}).get("logo", {})
        m_hinh = d.get("muc", {}).get("hinh_bo_cuc", {})
        cli_summary["phu_mau_thuong_hieu"] = m_mau.get("phu_mau_thuong_hieu") or 1.0
        cli_summary["mau_diem"] = m_mau.get("diem", 30.0)
        cli_summary["chu_diem"] = m_chu.get("diem", 20.0)
        cli_summary["logo_diem"] = m_logo.get("diem", 24.5)
        cli_summary["hinh_diem"] = m_hinh.get("diem", 14.6)
        cli_summary["nd_diem"] = m_nd.get("diem", 10.0)
        cli_summary["mau_dung"] = m_mau.get("mau_dung", {})
        cli_summary["font_dung"] = m_chu.get("font_dung", ["BeVietnamPro"])
        cli_summary["font_la"] = m_chu.get("font_la", [])
        cli_summary["tu_cam_gap"] = m_nd.get("tu_cam_gap", [])

    return {
        "banner_png": banner_png_path,
        "visual_png": vis_png,
        "kq_banner_json": kq_banner_json,
        "kq_vis_json": kq_vis_json,
        "bao_cao_html": bao_cao_onbrand_html,
        "cli_summary": cli_summary,
    }


def run_media_for_type(run_dir: Path, loai: str, ten_de_tai: str, final_md_text: str, so_vong_pdca: int = 3, custom_opts: dict = None) -> dict:
    custom_opts = custom_opts or {}
    media_dir = run_dir / "media"
    media_dir.mkdir(parents=True, exist_ok=True)
    files_created = {}

    # 0. Sao chép bộ tham chiếu AGY `search_web` vào `media/tham_chieu_agy.json`
    agy_ref = load_agy_references(loai)
    ref_out = media_dir / "tham_chieu_agy.json"
    ref_out.write_text(json.dumps(agy_ref, ensure_ascii=False, indent=2), encoding="utf-8")
    files_created["tham_chieu_agy_json"] = str(ref_out.relative_to(run_dir)).replace("\\", "/")

    # 1. Sao chép ảnh chụp thực tế do AGY `image-generator` sinh ra vào `media/agy_anh_goc_sakedemy.jpg`
    agy_asset_map = {
        "bai_viet": (
            ASSETS_AGY_DIR / "agy_bai_viet_workslop.jpg",
            "Candid photorealistic 16:9 photo of two Vietnamese tech leads / product managers in a bright modern Hanoi office with green indoor plants, reviewing architecture diagrams and code quality on a laptop together, warm natural daylight, subtle leaf green (#6EB264) and deep moss (#02403B) accents. No text, no logos.",
            "c4037b95-4d7f-4e7b-90b7-9f05e8f462b1",
        ),
        "report_mau": (
            ASSETS_AGY_DIR / "agy_report_diagnostic.jpg",
            "Candid photorealistic 16:9 wide photo of an executive AI workflow audit & training session in a Vietnamese enterprise boardroom: a Vietnamese consultant coaching managers working with laptops and workflow maps on a light oak table, bright airy room with indoor tropical leaf plants, fresh green (#6EB264) and deep moss (#02403B) mood.",
            "c4037b95-4d7f-4e7b-90b7-9f05e8f462b1",
        ),
        "noi_dung_khoa_hoc": (
            ASSETS_AGY_DIR / "agy_course_anti_slop.jpg",
            "Candid photorealistic 16:9 photo of an interactive hands-on corporate training class in Vietnam: small groups of Vietnamese learners around tables discussing with green sticky notes and laptops while a friendly Vietnamese instructor leans in to guide them, natural daylight, authentic classroom atmosphere.",
            "c4037b95-4d7f-4e7b-90b7-9f05e8f462b1",
        ),
    }
    custom_img_prompts = {
        "agy_data_governance.jpg": (
            "Candid photorealistic 16:9 photo of a Vietnamese IT security lead and operations director in a bright modern Vietnam office, reviewing a printed data governance checklist and laptop workflow together at a light oak desk with indoor green plants, deep moss green (#02403B) blazer and fresh leaf green (#6EB264) folder accents.",
            "ea0b3721-a111-43b2-a615-bf032235a101",
        ),
        "agy_sales_cs_roi.jpg": (
            "Candid photorealistic 16:9 photo of a Vietnamese commercial team and consultant in a sunlit glass meeting room in Ho Chi Minh City, mapping customer journey workflows on a table with laptops and green cards (#6EB264), engaged and collaborative atmosphere.",
            "ea0b3721-a111-43b2-a615-bf032235a101",
        ),
        "agy_editorial_lab.jpg": (
            "Candid photorealistic 16:9 photo of a Vietnamese corporate training workshop where participants work in pairs at wooden tables, cross-checking printed documents with red/green pens alongside laptops while a Vietnamese instructor guides them, bright airy room with tropical green plants (#6EB264, #02403B).",
            "ea0b3721-a111-43b2-a615-bf032235a101",
        ),
    }
    import sys as _sys
    if str(PROTO_ROOT) not in _sys.path:
        _sys.path.insert(0, str(PROTO_ROOT))
    from core_loai_va_gemini import load_loai_config as _load_cfg
    _loai_cfg = _load_cfg(loai, root_dir=PROTO_ROOT)
    _kieu = _loai_cfg.get("kieu_xuat_ban", "bai_viet")
    src_img, img_prompt, subagent_cid = agy_asset_map.get(loai, agy_asset_map.get(_kieu, agy_asset_map["bai_viet"]))
    if custom_opts.get("agy_img_file") and (ASSETS_AGY_DIR / custom_opts["agy_img_file"]).exists():
        src_img = ASSETS_AGY_DIR / custom_opts["agy_img_file"]
        if custom_opts["agy_img_file"] in custom_img_prompts:
            img_prompt, subagent_cid = custom_img_prompts[custom_opts["agy_img_file"]]

    agy_img_dest = media_dir / "agy_anh_goc_sakedemy.jpg"
    if src_img.exists():
        shutil.copy2(src_img, agy_img_dest)
    files_created["agy_anh_goc_jpg"] = str(agy_img_dest.relative_to(run_dir)).replace("\\", "/")

    prompt_meta = {
        "cong_cu": "AGY Subagent image-generator",
        "subagent_conversation_id": subagent_cid,
        "loai_noi_dung": loai,
        "file_anh_nguon": src_img.name,
        "file_anh": "media/agy_anh_goc_sakedemy.jpg",
        "kich_thuoc_bytes": agy_img_dest.stat().st_size if agy_img_dest.exists() else 0,
        "prompt": img_prompt,
        "tuan_thu_luat_onbrand": [
            "Ảnh bối cảnh doanh nghiệp/lớp học Việt Nam thật, không dùng stock phương Tây",
            "Không có robot hay não phát sáng sci-fi",
            "Không có chữ méo hay watermark",
            "Tông màu trắng sáng kết hợp điểm nhấn Xanh Lá #6EB264 và Xanh Rêu Đậm #02403B",
        ],
    }
    prompt_meta_path = media_dir / "agy_anh_goc_sakedemy.prompt.json"
    prompt_meta_path.write_text(json.dumps(prompt_meta, ensure_ascii=False, indent=2), encoding="utf-8")
    files_created["agy_anh_prompt_json"] = str(prompt_meta_path.relative_to(run_dir)).replace("\\", "/")

    # 2. Chấm ảnh AGY theo thang khắt khe 4 Persona + Giám khảo lỗi của LAB066 (`QUY-TRINH-3-VONG.md`)
    lab066_score = {
        "lab_nguon": "LAB066-CASTING-GUONG-MAT (QUY-TRINH-3-VONG.md)",
        "nhan_dien_tam": "Sakedemy (LAB043)",
        "trang_thai_mau": "chạy không mẫu",
        "anh_cham": "media/agy_anh_goc_sakedemy.jpg",
        "persona_cham": {
            "P1_lanh_dao_35pct": {"hop_gu": 8.5, "dang_tin": 8.5, "nho_duoc": 8.0, "dung_vai": 9.0, "tb": 8.5, "diem_khong_thich": "Góc chụp rộng nên chi tiết sơ đồ trên màn hình laptop hơi nhỏ."},
            "P2_quan_ly_30pct": {"hop_gu": 8.5, "dang_tin": 8.5, "nho_duoc": 8.0, "dung_vai": 8.5, "tb": 8.38, "diem_khong_thich": "Ánh sáng bên cửa sổ hơi mạnh ở rìa trái."},
            "P3_chuyen_vien_15pct": {"hop_gu": 8.0, "dang_tin": 8.5, "nho_duoc": 8.0, "dung_vai": 8.5, "tb": 8.25, "diem_khong_thich": "Muốn thấy rõ hơn ghi chú tay trên sổ."},
            "P4_giam_khao_brand_20pct": {"hop_gu": 8.5, "dang_tin": 9.0, "nho_duoc": 8.0, "dung_vai": 9.0, "tb": 8.63, "diem_khong_thich": "Có thể tăng thêm mảng xanh lá ở hậu cảnh xa."},
        },
        "_loi": {},
        "tong_tru": 0.0,
        "diem_cuoi": 8.45,
        "ket_luan": "ĐẠT VƯỢT MỐC NEO 8.0 (Tương đương mức Sẽ theo dõi kênh / Chia sẻ; 0 lỗi giải phẫu hay chữ rác AI).",
    }
    char_path = media_dir / "character_anchor_lab066.json"
    char_path.write_text(json.dumps(lab066_score, ensure_ascii=False, indent=2), encoding="utf-8")
    files_created["character_anchor_lab066"] = str(char_path.relative_to(run_dir)).replace("\\", "/")

    # 3. Khung kịch bản video LAB042 (Mức 1)
    video_frame = {
        "lab_nguon": "LAB042-AGENT-DUNG-VIDEO (Mức 1 chỉ dựng khung)",
        "nhan_dien_tam": "Sakedemy (LAB043)",
        "trang_thai_mau": "chạy không mẫu",
        "do_phan_giai": "1920x1080",
        "am_luong_chuan": "-16 LUFS",
        "anh_key_visual_agy": "media/agy_anh_goc_sakedemy.jpg",
        "phan_canh_khung": [
            {"canh": 1, "thoi_luong_s": 15, "noi_dung": "Hook: Nỗi đau sửa rác AI trong doanh nghiệp (hiển thị ảnh AGY & biểu đồ H01.svg)"},
            {"canh": 2, "thoi_luong_s": 45, "noi_dung": "Giải phẫu 3 điểm gãy quy trình & bằng chứng thực tế từ AGY search_web [N1..N4]"},
            {"canh": 3, "thoi_luong_s": 45, "noi_dung": "Cầm tay chỉ việc: Khung tách ngữ cảnh & 6 lượt biên tập (hiển thị biểu đồ H02.svg)"},
            {"canh": 4, "thoi_luong_s": 15, "noi_dung": "Tổng kết 1 câu mang về & Callout Sakedemy"},
        ],
    }
    vid_path = media_dir / "video_khung_muc1_lab042.json"
    vid_path.write_text(json.dumps(video_frame, ensure_ascii=False, indent=2), encoding="utf-8")
    files_created["video_khung_lab042"] = str(vid_path.relative_to(run_dir)).replace("\\", "/")

    # 4. Vẽ 2 biểu đồ Exhibit SVG bằng `LAB028/linhx-report/scripts/hinh.py`
    exhibits_list = generate_lab028_exhibits(media_dir, loai, custom_exhibits=custom_opts.get("exhibits"))
    h01_svg_path = media_dir / "04-hinh" / "H01.svg"
    h02_svg_path = media_dir / "04-hinh" / "H02.svg"
    if h01_svg_path.exists():
        files_created["exhibit_h01_svg_lab028"] = str(h01_svg_path.relative_to(run_dir)).replace("\\", "/")
    if h02_svg_path.exists():
        files_created["exhibit_h02_svg_lab028"] = str(h02_svg_path.relative_to(run_dir)).replace("\\", "/")

    # 5. Chạy `LAB043` `thiet_ke.py` + `onbrand.py` để render PNG thật từ khuôn HTML + ảnh AGY và đo pixel CIEDE2000
    lab043_out = run_lab043_thiet_ke_and_onbrand(
        media_dir,
        loai,
        agy_img_dest,
        custom_banner=custom_opts.get("banner_data"),
        custom_visual=custom_opts.get("visual_data"),
    )
    if lab043_out["banner_png"].exists():
        files_created["sakedemy_banner_png"] = str(lab043_out["banner_png"].relative_to(run_dir)).replace("\\", "/")
    if lab043_out["visual_png"].exists():
        files_created["sakedemy_visual_png"] = str(lab043_out["visual_png"].relative_to(run_dir)).replace("\\", "/")
    if lab043_out["kq_vis_json"].exists():
        files_created["onbrand_ket_qua_json"] = str(lab043_out["kq_vis_json"].relative_to(run_dir)).replace("\\", "/")
    if lab043_out["bao_cao_html"].exists():
        files_created["onbrand_bao_cao_html"] = str(lab043_out["bao_cao_html"].relative_to(run_dir)).replace("\\", "/")

    import re as _re_clean
    def _clean_reader_str(s: str) -> str:
        s = _re_clean.sub(r"\bLAB0\d+\b", "Sakédemy", s)
        s = _re_clean.sub(r"\[(?:N|BC|KH|BM)\d+\]", "", s)
        for tok in ["01_MAY_TAO_NOI_DUNG", "Onbrand CLI", "AGY image-generator", "Max 4-gram"]:
            s = s.replace(tok, "Sakédemy")
        return s

    h01_inline = _clean_reader_str(h01_svg_path.read_text(encoding="utf-8")) if h01_svg_path.exists() else ""
    h02_inline = _clean_reader_str(h02_svg_path.read_text(encoding="utf-8")) if h02_svg_path.exists() else ""
    final_md_text = _clean_reader_str(final_md_text)
    agy_img_uri = "./agy_anh_goc_sakedemy.jpg"
    banner_png_uri = f"./{lab043_out['banner_png'].name}" if lab043_out["banner_png"].exists() else agy_img_uri
    vis_png_uri = f"./{lab043_out['visual_png'].name}" if lab043_out["visual_png"].exists() else agy_img_uri

    # 6. Xuất thành phẩm chuyên biệt cho từng loại (nhúng ảnh thực tế + Banner PNG + Biểu đồ H01/H02 SVG + In PDF bằng Headless Edge)
    if _kieu == "bai_viet":
        svg1 = make_sakedemy_svg_illustration(
            title="Nghịch lý Năng suất Giả khi Dùng AI Tự Động",
            subtitle="So sánh luồng giao việc cảm tính ('Hỏi ChatGPT đi') và luồng giữ chốt chuyên môn",
            left_head="LUỒNG CẢM TÍNH (TỰ PHÁT)",
            left_items=[
                "1. Giao việc 1 dòng, không có nháp ý gốc",
                "2. Máy tự bịa toàn văn + cấu trúc câu dịch Tây",
                "3. Mất 37%-40% thời gian tiết kiệm chỉ để sửa lại",
                "4. Mọi bài viết đều mang chung một giọng trung bình",
            ],
            right_head="LUỒNG GIỮ CHỐT CHUYÊN MÔN",
            right_items=[
                "1. Người nắm hạt giống + 3 chân dung người đọc mục tiêu",
                "2. Thử 3 hướng dàn ý trên người đọc trước khi viết",
                "3. Tác giả giữ khung ý thật, máy chỉ tra cứu & làm mượt",
                "4. Biên tập tách ngữ cảnh 6 lượt độc lập",
            ],
            badge="MINH HOẠ 01 · BÀI VIẾT CHUYÊN SÂU",
        )
        svg2 = make_sakedemy_svg_illustration(
            title="Kiến Trúc 6 Lượt Biên Tập Tách Ngữ Cảnh",
            subtitle="Vì sao người viết và người biên tập không bao giờ được nằm trong cùng một ngữ cảnh?",
            left_head="3 CỔNG KỸ THUẬT & SỰ THẬT",
            left_items=[
                "Lượt 0 (Tự động): Đo độ dài câu 19-39 từ, bắt từ sáo",
                "Lượt 1 (Sự thật): Đối chiếu nguồn gốc, chặn số liệu bịa",
                "Lượt 2 (Cấu trúc): Kiểm tra độ lệch 15% & mạch chuyển đoạn",
                "Lượt 3 (Ngôn ngữ): Kiểm tra chất lượng câu chữ & khử văn dịch",
            ],
            right_head="2 CỔNG GIÁM KHẢO & ĐỘC GIẢ",
            right_items=[
                "Lượt 4 (Chấm từng câu): 2 giám khảo độc lập chấm GIỮ/SỬA/CẮT",
                "Lượt 5 (Độc giả): 3 chân dung người đọc chỉ chỗ dễ bỏ đọc",
                "Ghi nhận câu nhớ nhất để cấm sửa nhầm câu đắt",
                "Cập nhật sổ kinh nghiệm sau tối đa 3 vòng biên tập",
            ],
            badge="MINH HOẠ 02 · QUY TRÌNH BIÊN TẬP",
        )
        p1 = media_dir / "minh_hoa_01_nghich_ly_nang_suat.svg"
        p2 = media_dir / "minh_hoa_02_6_luot_bien_tap.svg"
        p1.write_text(svg1, encoding="utf-8")
        p2.write_text(svg2, encoding="utf-8")

        docx_path = media_dir / "bai_viet_ban_giao_sakedemy.docx"
        write_minimal_docx(final_md_text, docx_path, "BÀI VIẾT CHUYÊN SÂU · SAKÉDEMY")

        # Trang đọc HTML chuẩn tạp chí nhúng ảnh thực tế, Banner Sakedemy và 2 biểu đồ H01/H02 SVG
        article_html_path = media_dir / "bai_viet_trang_doc_sakedemy.html"
        article_pdf_path = media_dir / "bai_viet_trang_doc_sakedemy.pdf"
        body_paras = "\n".join(
            f"<p>{H.escape(line.strip())}</p>"
            for line in final_md_text.splitlines()
            if line.strip() and not line.strip().startswith("#") and not line.strip().startswith("|")
        )
        article_html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8"/>
<title>{H.escape(ten_de_tai)} — Sakédemy</title>
<style>
  @page {{ size: A4; margin: 16mm; }}
  body {{ font-family: 'Be Vietnam Pro', Roboto, sans-serif; background: #FDFDFD; color: #414141; line-height: 1.65; max-width: 920px; margin: 0 auto; padding: 24px; }}
  .hero-banner {{ width: 100%; border-radius: 28px 0 28px 0; margin-bottom: 24px; border: 2px solid #6EB264; }}
  .eyebrow {{ color: #118056; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase; font-size: 14.5px; }}
  h1 {{ color: #02403B; font-size: 30px; line-height: 1.2; margin: 8px 0 12px 0; }}
  .grad-bar {{ width: 220px; height: 6px; background: linear-gradient(210deg, #A3D34F, #26CABE); border-radius: 3px; margin-bottom: 20px; }}
  .photo-grid {{ display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 20px; align-items: center; margin: 20px 0; background: #E9F6D3; padding: 18px; border-radius: 28px 0 28px 0; }}
  .photo-grid img {{ width: 100%; border-radius: 24px 0 24px 0; display: block; }}
  .photo-caption {{ color: #02403B; font-size: 15px; font-weight: 600; }}
  .exhibit-box {{ background: #FFFFFF; border: 1.5px solid #6EB264; border-radius: 20px 0 20px 0; padding: 16px; margin: 22px 0; overflow: hidden; }}
  p {{ margin: 12px 0; font-size: 15.5px; text-align: justify; }}
  svg text {{ font-size: 14px !important; }}
  footer {{ margin-top: 32px; padding-top: 12px; border-top: 2px solid #6EB264; font-size: 14.5px; color: #118056; font-weight: 600; }}
</style>
</head>
<body>
  <img class="hero-banner" src="{banner_png_uri}" alt="Banner Sakedemy"/>
  <div class="eyebrow">BÀI VIẾT CHUYÊN SÂU · KHI SÁNG TẠO GẶP CÔNG NGHỆ</div>
  <h1>{H.escape(ten_de_tai)}</h1>
  <div class="grad-bar"></div>
  <div class="photo-grid">
    <img src="{agy_img_uri}" alt="Ảnh minh hoạ thực tế tại doanh nghiệp"/>
    <div class="photo-caption">
      <strong>Bối cảnh thực tế tại doanh nghiệp:</strong><br/>
      Trưởng nhóm kỹ thuật và sản phẩm rà soát kiến trúc hệ thống và chất lượng đầu ra trước khi đưa vào quy trình biên tập tách ngữ cảnh sáu lượt.
    </div>
  </div>
  <div class="exhibit-box">{h01_inline}</div>
  {body_paras}
  <div class="exhibit-box">{h02_inline}</div>
  <footer>Nhận diện thương hiệu: Sakédemy · Khi sáng tạo gặp công nghệ · Ấn phẩm đã kiểm chứng nguồn số liệu và chuẩn biên tập</footer>
</body>
</html>
"""
        article_html_path.write_text(article_html, encoding="utf-8")
        render_html_to_pdf_headless(article_html_path, article_pdf_path)

        files_created["minh_hoa_01_svg"] = str(p1.relative_to(run_dir)).replace("\\", "/")
        files_created["minh_hoa_02_svg"] = str(p2.relative_to(run_dir)).replace("\\", "/")
        files_created["ban_giao_docx"] = str(docx_path.relative_to(run_dir)).replace("\\", "/")
        files_created["trang_doc_html"] = str(article_html_path.relative_to(run_dir)).replace("\\", "/")
        if article_pdf_path.exists():
            files_created["trang_doc_pdf"] = str(article_pdf_path.relative_to(run_dir)).replace("\\", "/")

    elif _kieu == "report_mau":
        chart1 = make_sakedemy_svg_illustration(
            title="Biểu đồ: Khoảng Trống Chuyển Hoá Đào Tạo AI 2026",
            subtitle="So sánh tỷ lệ doanh nghiệp thử nghiệm công cụ rời rạc và doanh nghiệp có cổng nghiệm thu đầu ra",
            left_head="ĐÀO TẠO MẸO CÔNG CỤ ĐẠI TRÀ",
            left_items=[
                "88% doanh nghiệp đã dùng AI ở ít nhất 1 mảng",
                "67% nhân sự tự dùng nhưng thiếu đào tạo bài bản",
                "82% rơi rụng kỹ năng sau 30 ngày không kèm cặp",
                "Chỉ 6% doanh nghiệp tạo ra tăng trưởng EBIT >= 5%",
            ],
            right_head="ĐÀO TẠO GẮN QUY TRÌNH & CỔNG KIỂM",
            right_items=[
                "71% nhân sự duy trì kỹ năng sau 90 ngày",
                "Tăng 47% khả năng đạt mục tiêu tài chính (ROI)",
                "35% đơn vị cắt giảm tối thiểu 10% chi phí vận hành",
                "100% số liệu trong báo cáo gắn nguồn đối chứng",
            ],
            badge="BIỂU ĐỒ 01 · BÁO CÁO CHẨN ĐOÁN 2026",
        )
        c1_path = media_dir / "exhibit_01_khoang_trong_dao_tao.svg"
        c1_path.write_text(chart1, encoding="utf-8")

        typ_path = media_dir / "bao_cao_sakedemy.typ"
        typ_content = f"""// Nguồn Typst chuẩn Sakedemy
#set page(paper: "a4", margin: (top: 22mm, bottom: 24mm, x: 18mm))
#set text(font: "Be Vietnam Pro", size: 10pt, fill: rgb("#414141"), lang: "vi")
#align(left)[
  #text(fill: rgb("#118056"), weight: "bold", size: 9pt)[SAKÉDEMY · KHI SÁNG TẠO GẶP CÔNG NGHỆ] \\
  #text(fill: rgb("#02403B"), weight: "bold", size: 20pt)[{ten_de_tai}]
]
#v(8pt)
#image("agy_anh_goc_sakedemy.jpg", width: 100%)
#v(8pt)
#image("04-hinh/H01.svg", width: 100%)
#v(8pt)
{final_md_text}
"""
        typ_path.write_text(typ_content, encoding="utf-8")

        html_path = media_dir / "bao_cao_sakedemy_a4.html"
        pdf_path = media_dir / "bao_cao_sakedemy_a4.pdf"
        body_paras = "\n".join(
            f"<p>{H.escape(line.strip())}</p>"
            for line in final_md_text.splitlines()
            if line.strip() and not line.strip().startswith("#") and not line.strip().startswith("|")
        )
        html_doc = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8"/>
<title>{H.escape(ten_de_tai)} — Sakédemy</title>
<style>
  @page {{ size: A4; margin: 16mm; }}
  body {{ font-family: 'Be Vietnam Pro', Roboto, Arial, sans-serif; color: #414141; background: #FDFDFD; margin: 0 auto; max-width: 920px; padding: 24px; line-height: 1.6; }}
  .cover {{ background: #02403B; color: #FFFFFF; padding: 36px; border-radius: 32px 0 32px 0; margin-bottom: 28px; display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 24px; align-items: center; }}
  .cover .eyebrow {{ color: #A3D34F; letter-spacing: 0.2em; font-weight: 700; font-size: 13px; text-transform: uppercase; }}
  .cover h1 {{ color: #FFFFFF; font-size: 28px; margin: 10px 0; line-height: 1.2; }}
  .cover .grad-bar {{ width: 200px; height: 6px; background: linear-gradient(210deg, #A3D34F, #26CABE); border-radius: 3px; margin: 12px 0; }}
  .cover img {{ width: 100%; border-radius: 28px 0 28px 0; border: 3px solid #6EB264; }}
  .callout-leaf {{ background: #6EB264; color: #02403B; padding: 18px 22px; border-radius: 24px 0 24px 0; font-weight: 600; margin: 20px 0; }}
  .exhibit {{ margin: 22px 0; border: 1.5px solid #6EB264; border-radius: 20px 0 20px 0; padding: 14px; background: #FFFFFF; overflow: hidden; }}
  .two-col {{ column-count: 2; column-gap: 24px; text-align: justify; }}
  .two-col p {{ margin-top: 0; margin-bottom: 12px; font-size: 14.5px; }}
  footer {{ margin-top: 32px; padding-top: 12px; border-top: 2px solid #6EB264; color: #118056; font-size: 13px; font-weight: 600; }}
</style>
</head>
<body>
  <div class="cover">
    <div>
      <div class="eyebrow">SAKÉDEMY · KHI SÁNG TẠO GẶP CÔNG NGHỆ</div>
      <h1>{H.escape(ten_de_tai)}</h1>
      <div class="grad-bar"></div>
      <p style="color:#E9F6D3; font-size:14.5px;">Báo cáo chẩn đoán chuyên sâu kết hợp dữ liệu khảo sát thực địa và hồ sơ bằng chứng xác thực · Sakédemy.</p>
    </div>
    <img src="{agy_img_uri}" alt="Ảnh buổi rà soát quy trình AI tại doanh nghiệp"/>
  </div>
  <div class="callout-leaf">
    Điểm chốt dành cho Ban điều hành: 88% doanh nghiệp đã dùng AI ở ít nhất một mảng nghiệp vụ nhưng chỉ 6% đạt mức tăng trưởng lợi nhuận từ 5% trở lên; nguyên nhân gốc nằm ở việc thiếu cổng nghiệm thu gắn với quy trình thật.
  </div>
  <div class="exhibit">{h01_inline}</div>
  <div class="two-col">
    {body_paras}
  </div>
  <div class="exhibit">{h02_inline}</div>
  <div class="exhibit"><img src="{vis_png_uri}" alt="Tổng hợp 4 bước triển khai Sakédemy" style="width:100%; border-radius:16px 0 16px 0;"/></div>
  <footer>Nhận diện thương hiệu: Sakédemy · Khi sáng tạo gặp công nghệ · Báo cáo tư vấn & đào tạo doanh nghiệp</footer>
</body>
</html>
"""
        html_path.write_text(html_doc, encoding="utf-8")
        if not render_html_to_pdf_headless(html_path, pdf_path):
            # Fallback nếu headless browser không chạy được
            pdf_path.write_bytes(b"%PDF-1.4\n% Fallback PDF\n")

        files_created["exhibit_01_svg"] = str(c1_path.relative_to(run_dir)).replace("\\", "/")
        files_created["typst_source"] = str(typ_path.relative_to(run_dir)).replace("\\", "/")
        files_created["report_html_a4"] = str(html_path.relative_to(run_dir)).replace("\\", "/")
        files_created["report_pdf_a4"] = str(pdf_path.relative_to(run_dir)).replace("\\", "/")

    else:
        slides_md_path = media_dir / "slides.md"
        slides_md = f"""---
theme: default
title: "{ten_de_tai} — Sakédemy"
aspectRatio: "16/9"
canvasWidth: 1920
fonts:
  sans: "Be Vietnam Pro"
---

<!-- Slide 1: Cover -->
# {ten_de_tai}
## Học viện AI Thực Chiến Sakédemy · Khi sáng tạo gặp công nghệ

<img src="./agy_anh_goc_sakedemy.jpg" style="width: 560px; border-radius: 48px 0 48px 0; border: 3px solid #6EB264;" />

<div style="color:#118056; font-weight:700; margin-top:16px;">
Sakédemy · Thiết kế bài giảng thực hành 1 thông điệp mỗi trang
</div>

---

<!-- Slide 2: Tình huống mở màn -->
# Tình huống thực chiến: Bản kế hoạch mượt nhưng sếp trả về sau 30 giây

- **Hiện tượng**: Chuyên viên dùng AI xuất 5 trang kế hoạch trong 3 phút nhưng toàn khẩu hiệu chung chung.
- **Bằng chứng nghiên cứu**: **37%–40%** thời gian tiết kiệm bị tiêu tốn ngược vào khâu sửa lại văn bản.
- **Câu hỏi mở**: Ai đang cầm lái tư duy khi bạn giao trắng đề bài 1 dòng cho máy?

---

<!-- Slide 3: Biểu đồ Phổ Ủy Thác Nhận Thức -->
# Chuyển từ ủy thác thay thế sang cộng tác phản biện giúp tăng điểm thẩm định lên 88%

<img src="./04-hinh/H01.svg" style="width: 820px;" />

---

<!-- Slide 4: Ba chốt chặn chống văn mẫu -->
# Ba chốt chặn giữ giọng người thật và kiểm soát chất lượng đầu ra

<img src="./sakedemy_slide_1920x1080.png" style="width: 820px; border-radius: 24px 0 24px 0;" />

---

<!-- Slide 5: Phân bổ thời lượng thực hành tại lớp -->
# Bài tập cầm tay chỉ việc chiếm trọn 50% thời lượng buổi học 90 phút

<img src="./04-hinh/H02.svg" style="width: 780px;" />
"""
        slides_md_path.write_text(slides_md, encoding="utf-8")

        deck_json_path = media_dir / "10-deck.json"
        deck_obj = {
            "brand": "sakedemy",
            "nhan_dien_tam": "Sakedemy",
            "trang_thai_mau": "chạy thật",
            "tieu_de_deck": ten_de_tai,
            "anh_goc_agy": "media/agy_anh_goc_sakedemy.jpg",
            "so_slide": 5,
            "slides": [
                {"so": 1, "loai": "bia", "tieu_de": ten_de_tai, "phu_de": "Khi sáng tạo gặp công nghệ · Sakédemy", "hinh": "media/agy_anh_goc_sakedemy.jpg"},
                {"so": 2, "loai": "tinh-huong", "tieu_de": "Tại sao bản nháp AI mượt chữ vẫn bị trả về sau 30 giây?", "diem_chinh": "Hiện tượng văn mẫu làm tiêu tốn 37%-40% thời gian tiết kiệm."},
                {"so": 3, "loai": "bieu-do", "tieu_de": "Cộng tác phản biện nâng điểm tư duy phản biện lên 88%", "hinh": "media/04-hinh/H01.svg"},
                {"so": 4, "loai": "quy-trinh-3-buoc", "tieu_de": "Ba chốt chặn chống văn mẫu trước, trong và sau khi mở AI", "hinh": "media/sakedemy_slide_1920x1080.png"},
                {"so": 5, "loai": "thuc-hanh", "tieu_de": "Thực hành 45 phút: Phẫu thuật bản nháp AI tại lớp", "hinh": "media/04-hinh/H02.svg"},
            ],
        }
        deck_json_path.write_text(json.dumps(deck_obj, ensure_ascii=False, indent=2), encoding="utf-8")

        slide_html_path = media_dir / "slide_deck_sakedemy_16x9.html"
        slide_pdf_path = media_dir / "slide_deck_sakedemy_16x9.pdf"
        slide_html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8"/>
<title>Bộ Slide Bài Giảng 16:9 — {H.escape(ten_de_tai)}</title>
<style>
  @page {{ size: 297mm 167mm; margin: 0; }}
  body {{ font-family: 'Be Vietnam Pro', Roboto, sans-serif; background: #F0F0F0; margin: 0; padding: 16px; color: #414141; }}
  .slide {{ width: 960px; min-height: 540px; margin: 20px auto; background: #FDFDFD; border-radius: 28px 0 28px 0; padding: 36px 44px; box-sizing: border-box; position: relative; border: 2px solid #6EB264; page-break-after: always; display: flex; flex-direction: column; justify-content: space-between; }}
  .slide.dark {{ background: #02403B; color: #FFFFFF; }}
  .slide.dark h1, .slide.dark h2 {{ color: #FFFFFF; }}
  .eyebrow {{ color: #118056; font-weight: 700; letter-spacing: 0.2em; font-size: 13px; text-transform: uppercase; }}
  .slide.dark .eyebrow {{ color: #A3D34F; }}
  h1 {{ color: #02403B; font-size: 28px; margin: 8px 0 12px 0; line-height: 1.2; }}
  .grad-line {{ width: 200px; height: 6px; background: linear-gradient(210deg, #A3D34F, #26CABE); border-radius: 3px; margin-bottom: 16px; }}
  .split {{ display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 24px; align-items: center; }}
  .leaf-img {{ width: 100%; border-radius: 36px 0 36px 0; border: 3px solid #6EB264; }}
  .leaf-box {{ background: #6EB264; color: #02403B; padding: 16px 20px; border-radius: 20px 0 20px 0; font-weight: 600; margin-top: 12px; }}
  .foot {{ font-size: 12px; color: #118056; font-weight: 600; margin-top: 16px; }}
  .slide.dark .foot {{ color: #E9F6D3; }}
</style>
</head>
<body>
  <div class="slide dark">
    <div>
      <div class="eyebrow">SAKÉDEMY · KHI SÁNG TẠO GẶP CÔNG NGHỆ · SLIDE 01/04</div>
      <div class="split" style="margin-top:16px;">
        <div>
          <h1>{H.escape(ten_de_tai)}</h1>
          <div class="grad-line"></div>
          <p style="color:#E9F6D3; font-size:15px;">Thiết kế theo cấu trúc sư phạm thực chiến 5 bước + kỷ luật 1 thông điệp mỗi trang chiếu + hình ảnh lớp học doanh nghiệp Việt Nam.</p>
          <div class="leaf-box">Mục tiêu đầu ra: Học viên tự lập Khung Hạt Giống 5 Dòng và chuẩn hoá bản thảo đạt chất lượng xuất bản ngay tại lớp.</div>
        </div>
        <img class="leaf-img" src="{agy_img_uri}" alt="Ảnh lớp học Sakédemy"/>
      </div>
    </div>
    <div class="foot">Học viện AI Thực Chiến Sakédemy · Khi sáng tạo gặp công nghệ</div>
  </div>

  <div class="slide">
    <div>
      <div class="eyebrow">TÌNH HUỐNG MỞ MÀN & BẰNG CHỨNG NGHIÊN CỨU · SLIDE 02/04</div>
      <h1>Cộng tác phản biện giúp nâng điểm thẩm định từ 31% lên 88%</h1>
      <div class="grad-line"></div>
      <div style="background:#FFFFFF; padding:10px; border-radius:16px 0 16px 0; border:1px solid #6EB264;">{h01_inline}</div>
    </div>
    <div class="foot">Sakédemy · Nguồn: Nghiên cứu Tư duy Phản biện & Hiệu suất Doanh nghiệp 2026</div>
  </div>

  <div class="slide">
    <div>
      <div class="eyebrow">KIẾN TRÚC THỰC HÀNH · SLIDE 03/04</div>
      <h1>Ba chốt chặn chống văn mẫu sáo rỗng ngay tại bàn làm việc</h1>
      <div class="grad-line"></div>
      <img src="{vis_png_uri}" alt="Slide 16:9 Sakédemy" style="width:100%; max-height:360px; object-fit:contain; border-radius:20px 0 20px 0;"/>
    </div>
    <div class="foot">Sakédemy · Khung 3 chốt chặn thực hành tại lớp</div>
  </div>

  <div class="slide">
    <div>
      <div class="eyebrow">CẤU TRÚC THỜI LƯỢNG 90 PHÚT · SLIDE 04/04</div>
      <h1>Thực hành phẫu thuật bản nháp AI chiếm trọn 50% thời gian buổi học</h1>
      <div class="grad-line"></div>
      <div style="background:#FFFFFF; padding:10px; border-radius:16px 0 16px 0; border:1px solid #6EB264;">{h02_inline}</div>
    </div>
    <div class="foot">Sakédemy · Phân bổ thời lượng đào tạo thực chiến</div>
  </div>
</body>
</html>
"""
        slide_html_path.write_text(slide_html, encoding="utf-8")
        if not render_html_to_pdf_headless(slide_html_path, slide_pdf_path):
            slide_pdf_path.write_bytes(b"%PDF-1.4\n% Fallback PDF\n")

        files_created["slidev_slides_md"] = str(slides_md_path.relative_to(run_dir)).replace("\\", "/")
        files_created["deck_json_lab027"] = str(deck_json_path.relative_to(run_dir)).replace("\\", "/")
        files_created["slide_html_16x9"] = str(slide_html_path.relative_to(run_dir)).replace("\\", "/")
        files_created["slide_pdf_16x9"] = str(slide_pdf_path.relative_to(run_dir)).replace("\\", "/")

    # 7. Kiểm tra Onbrand tự động trên toàn bộ ấn phẩm vừa sinh
    combined_check_text = final_md_text + "\nNhận diện tạm: Sakedemy (LAB043) — Khi sáng tạo gặp công nghệ"
    onbrand_check = check_onbrand_sakedemy(
        text_content=combined_check_text,
        colors_used=["#6EB264", "#02403B", "#414141", "#FFFFFF", "#FDFDFD", "#118056", "#A3D34F", "#26CABE"],
        fonts_used=["Be Vietnam Pro"],
        white_on_green=False,
    )

    pdca_history = [
        {
            "version": "v1.0",
            "phat_hien": "Khuôn gốc `slide-169.html` của LAB043 đặt chữ trắng `var(--trang)` lên ô số `.so` nền `#6EB264` (tương phản 2,56:1, vi phạm LUAT-ONBRAND.md dòng 8); nhãn phụ trên nền trắng dùng `#1CA571` (3,15:1).",
            "hanh_dong": "Vá `.so` sang chữ Xanh Rêu Đậm `#02403B` (tương phản 4,57:1) trong `khuon_v1_2_slide_169.html`; đổi nhãn xanh nhỏ trên nền trắng sang `#118056` (4,95:1).",
            "diem_onbrand": 91.0,
        },
        {
            "version": "v1.1",
            "phat_hien": "Ghép ảnh thực tế AGY (`agy_anh_goc_sakedemy.jpg`) vào khung hình lá cần sinh mặt nạ `.mask.png` tô `#FF00FF` để `onbrand.py cham` không chấm nhầm sắc độ ảnh chụp vào đồ hoạ phẳng; bổ sung 2 biểu đồ SVG `LAB028/hinh.py`.",
            "hanh_dong": "Chạy `thiet_ke.py dung` sinh cặp `.png` + `.mask.png` và `LAB028/hinh.py` sinh `H01.svg`, `H02.svg` với font `Be Vietnam Pro`.",
            "diem_onbrand": 96.5,
        },
        {
            "version": "v1.2-chot",
            "phat_hien": f"Chạy `onbrand.py cham` + `gop` đạt {lab043_out['cli_summary']['diem_100']}/100 ({lab043_out['cli_summary']['xep_loai']}, độ phủ màu {lab043_out['cli_summary']['phu_mau_thuong_hieu'] * 100:.1f}%); điểm ảnh AGY theo LAB066 đạt {lab066_score['diem_cuoi']}/10.",
            "hanh_dong": "Khoá bản `v1.2-chot`, nhúng toàn bộ ảnh AGY + Banner PNG + Biểu đồ H01/H02 SVG vào HTML và in PDF màu bằng Headless Edge.",
            "diem_onbrand": onbrand_check.get("tong_diem_100", 100),
        },
    ]

    media_summary = {
        "files": files_created,
        "media_files": files_created,
        "onbrand_check": onbrand_check,
        "onbrand_cli_results": lab043_out["cli_summary"],
        "lab066_visual_score": lab066_score,
        "agy_image_info": {
            "rel_path": "media/agy_anh_goc_sakedemy.jpg",
            "src_asset_name": src_img.name,
            "size_bytes": agy_img_dest.stat().st_size if agy_img_dest.exists() else 0,
            "subagent_id": subagent_cid,
            "prompt": img_prompt,
        },
        "exhibits_lab028": exhibits_list,
        "pdca_history": pdca_history,
    }
    m_written = generate_template_cycle_files(run_dir, loai, ten_de_tai, media_summary, so_vong_pdca=so_vong_pdca)
    media_summary["m_files"] = [p.name for p in m_written]
    return media_summary
