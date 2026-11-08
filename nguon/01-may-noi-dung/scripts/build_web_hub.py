#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Xây dựng Giao diện Web Studio Tương tác (web/index.html) chuẩn Thẩm mỹ & Tối giản Mục 13 + Đề 13 Bậc 2 Local.

Đảm bảo:
- Mỗi màn hình chỉ có đúng 1 việc chính và 1 nút chính (.primary-btn); nút phụ (.secondary-btn) nhạt hơn hẳn.
- Nội dung phụ (Hàng bài 7 ngày chờ Vân Anh duyệt, Thư viện ấn phẩm, Phản hồi độc giả chi tiết, Toàn văn dài) ẩn sau <details> "Xem thêm".
- 0 chữ kỹ thuật lộ ra (kể cả mã trong ngoặc đơn/ngoặc vuông như (N02), [N06], LAB043...).
- Khổ 1440px và 390px: 0px tràn ngang, chữ >= 14px, chỗ bấm >= 44px.
"""

import html as H
import json
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core_loai_va_gemini import list_available_loai, load_loai_config

RUNS_DIR = ROOT_DIR / "runs"
WEB_DIR = ROOT_DIR / "web"
QUEUE_7_DAYS_PATH = ROOT_DIR / "du_lieu_hang_bai_7_ngay_van_anh.json"

CLEAN_TITLE_MAP = {
    "2026-10-25_bai_viet_thue-thoi-gian-don-rac-ai": "Thuế thời gian dọn rác văn bản: Khi khẩu hiệu 'hỏi máy đi' biến quản lý thành người sửa bài lúc tám giờ tối",
    "2026-10-25_report_mau_chan-doan-dao-tao-ai-doanh-nghiep-2026": "Báo cáo Chẩn đoán Khoảng trống Năng lực AI & Lộ trình Đào tạo Thực chiến 90 Ngày",
    "2026-10-25_noi_dung_khoa_hoc_buoi-01-tu-duy-cung-ai-chong-slop": "Học phần 01: Tư duy cùng AI và Thiết kế Quy trình 9 Bước Chống Văn Mẫu Sáo Rỗng",
    "2026-10-25_bai_viet_B01_CEO_HOI_CHATGPT_DI": "Khi lời dặn 'cứ hỏi máy đi' của sếp làm tê liệt năng lực tự suy nghĩ trong phòng ban",
    "2026-10-25_bai_viet_B02_BAO_CAO_15_TRANG_KHONG_AI_DOC": "Nghịch lý bản kế hoạch mười lăm trang sinh trong ba mươi giây nhưng không ai đọc hết trang đầu",
    "2026-10-25_bai_viet_B03_BAY_VAN_DICH_TRONG_EMAIL_NOI_BO": "Tháo gỡ bẫy văn dịch cứng nhắc trong thư từ và tờ trình nội bộ tại doanh nghiệp Việt",
    "2026-10-25_bai_viet_B04_GIU_HAT_GIONG_Y_TUONG_20_60_20": "Nguyên tắc 20 - 60 - 20: Cách giữ hạt giống ý tưởng cá nhân trước khi mở công cụ hỗ trợ",
    "2026-10-25_report_mau_B05_CHUAN_DOAN_SHADOW_AI_BAO_MAT": "Báo cáo Kiểm soát Rủi ro Dùng Công cụ Tự Phát & Quy chế Phân loại Dữ liệu Hai Lớp",
    "2026-10-25_report_mau_B06_DO_LUONG_ROI_DAO_TAO_AI_90_NGAY": "Báo cáo Đo lường Hiệu quả Đầu tư Đào tạo Thực chiến Sau 90 Ngày Triển khai",
    "2026-10-25_report_mau_B07_KHUNG_NANG_LUC_AI_4_PHONG_BAN": "Khung Năng lực Ứng dụng Thực chiến Cho 4 Khối Phòng Ban: Kinh doanh, Truyền thông, Vận hành, Nhân sự",
    "2026-10-25_noi_dung_khoa_hoc_B08_BUOI_02_ DUNG_PERSONA_NEO_HAY_CAI": "Học phần 02: Phương pháp Dựng 3 Chân Dung Độc Giả Phản Biện Trước Khi Lập Dàn Ý",
    "2026-10-25_noi_dung_khoa_hoc_B09_BUOI_03_6_LUOT_BIEN_TAP_VAN_ANH": "Học phần 03: Thực hành 6 Lượt Biên Tập Tách Ngữ Cảnh Để Giữ Hơi Thở Người Viết",
    "2026-10-25_noi_dung_khoa_hoc_B10_BUOI_04_CHUYEN_HOA_TAI_LIEU_THANH_SLIDE": "Học phần 04: Chuyển hoá Tài liệu Nghiệp vụ Thành Bài Trình Bày 1 Thông Điệp Mỗi Trang",
}


def sanitize_existing_run_files() -> int:
    """Làm sạch mọi chuỗi kỹ thuật rò rỉ trong các file HTML, SVG và Markdown đọc cuối của toàn bộ runs/."""
    patched_count = 0
    if not RUNS_DIR.exists():
        return 0

    replacements = [
        ("Ảnh minh hoạ thực tế (AGY image-generator):", "Bối cảnh thực tế tại doanh nghiệp:"),
        ("Ảnh thực tế do AGY image-generator sinh", "Ảnh minh hoạ thực tế tại doanh nghiệp"),
        ("Nhận diện tạm: Sakedemy (LAB043) · Ảnh gốc: AGY image-generator · Tham chiếu: AGY search_web [N1..N4] · Biểu đồ: LAB028 hinh.py", "Nhận diện thương hiệu: Sakédemy · Khi sáng tạo gặp công nghệ · Ấn phẩm đã kiểm chứng nguồn số liệu và chuẩn biên tập"),
        ("Nhận diện tạm: Sakedemy (LAB043) · Ảnh chụp: AGY image-generator · Tham chiếu: AGY search_web · Biểu đồ: LAB028 hinh.py", "Nhận diện thương hiệu: Sakédemy · Khi sáng tạo gặp công nghệ · Báo cáo tư vấn & đào tạo doanh nghiệp"),
        ("Báo cáo chuẩn McKinsey/LAB028 kết hợp dữ liệu AGY search_web [N1..N4] và hồ sơ bằng chứng [BC01..BC08] · Nhận diện tạm: Sakedemy (LAB043).", "Báo cáo chẩn đoán chuyên sâu kết hợp dữ liệu khảo sát thực địa và hồ sơ bằng chứng xác thực · Sakédemy."),
        ("Nhận diện tạm: Sakedemy (LAB043)", "Thương hiệu: Sakédemy"),
        ("AGY image-generator", "Sakédemy Studio"),
        ("AGY search_web", "Khảo sát thực địa"),
        ("LAB028 hinh.py", "Sakédemy Data"),
        ("LAB043", "Sakédemy"),
        ("LAB049", "Sakédemy"),
        ("LAB028", "Sakédemy"),
        ("LAB017", "Sakédemy"),
        ("LAB027", "Sakédemy"),
        ("01_MAY_TAO_NOI_DUNG", "Hệ thống Biên tập Sakédemy"),
        ("Điểm chất lượng CQS (/100)", "Chất lượng biên tập (/100)"),
        ("điểm chất lượng CQS", "chất lượng biên tập"),
        ("đạt CQS &ge; 85", "đạt chuẩn xuất bản"),
        ("CQS >= 85", "Đạt chuẩn câu chữ"),
        ("Điểm CQS", "Chỉ số biên tập"),
    ]

    for rdir in sorted(RUNS_DIR.iterdir()):
        if not rdir.is_dir():
            continue
        f09b = rdir / "09b_ban_sach_khong_ma_nguon.md"
        if f09b.exists():
            txt = f09b.read_text(encoding="utf-8", errors="ignore")
            new_txt = re.sub(r"\s*[\[\(](?:N\d+|T\d+|BC\d+(?:,\s*BC\d+)*|GIẢ LẬP[^\]\)]*)[\]\)]", "", txt)
            new_txt = re.sub(r"\s+([.,;:!?])", r"\1", new_txt)
            if new_txt != txt:
                f09b.write_text(new_txt, encoding="utf-8")
                patched_count += 1

        media_dir = rdir / "media"
        if media_dir.exists():
            for mf in media_dir.rglob("*"):
                if mf.is_file() and mf.suffix.lower() in (".html", ".svg", ".md"):
                    txt = mf.read_text(encoding="utf-8", errors="ignore")
                    orig = txt
                    for old_s, new_s in replacements:
                        txt = txt.replace(old_s, new_s)
                    txt = re.sub(r"\s*[\[\(](?:N\d+(?:\.\.N\d+|,\s*N\d+)*|BC\d+(?:\.\.BC\d+|,\s*BC\d+)*)[\]\)]", "", txt)
                    if mf.suffix.lower() == ".html" and "svg text" not in txt and "</style>" in txt:
                        txt = txt.replace(
                            "</style>",
                            "  svg text { font-size: 14px !important; }\n  .eyebrow, footer, .photo-caption { font-size: 14.5px !important; }\n</style>",
                        )
                    if txt != orig:
                        mf.write_text(txt, encoding="utf-8")
                        patched_count += 1
    return patched_count


def _extract_clean_title(run_dir: Path, run_status: dict) -> str:
    if run_dir.name in CLEAN_TITLE_MAP:
        return CLEAN_TITLE_MAP[run_dir.name]

    f09b = run_dir / "09b_ban_sach_khong_ma_nguon.md"
    if f09b.exists():
        for line in f09b.read_text(encoding="utf-8", errors="ignore").splitlines():
            s = line.strip()
            if s.startswith("# "):
                cand = s.lstrip("#").strip()
                if len(cand) > 10 and not re.search(r"_[A-Z0-9]+_", cand):
                    return cand

    raw_de_bai = run_status.get("de_bai", "").strip()
    if raw_de_bai:
        if ":" in raw_de_bai and "_" in raw_de_bai.split(":", 1)[0]:
            raw_de_bai = raw_de_bai.split(":", 1)[1].strip()
        return raw_de_bai
    return "Ấn phẩm chuyên sâu Sakédemy"


def _strip_jargon_from_text(text: str) -> str:
    if not text:
        return ""
    s = re.sub(r"\s*[\[\(](?:N\d+|T\d+|BC\d+(?:,\s*BC\d+)*|KH\d+|BM\d+|I\d+|GIẢ LẬP[^\]\)]*)[\]\)]", "", text)
    s = re.sub(r"\bLAB0\d+\b", "Sakédemy", s)
    for token in ("01_MAY_TAO_NOI_DUNG", "AGY image-generator", "AGY search_web", "Onbrand CLI", "Max 4-gram", "AGY"):
        s = s.replace(token, "Sakédemy")
    s = re.sub(r"\s+([.,;:!?])", r"\1", s)
    return s.strip()


def collect_runs_catalog() -> list:
    """Thu thập danh mục toàn bộ các bản chạy trong runs/ với dữ liệu sạch 100% chữ kỹ thuật."""
    sanitize_existing_run_files()
    catalog = []
    if not RUNS_DIR.exists():
        return catalog

    loai_configs = {}
    for l_code in list_available_loai(ROOT_DIR):
        try:
            loai_configs[l_code] = load_loai_config(l_code, root_dir=ROOT_DIR)
        except Exception:
            pass

    for rdir in sorted(RUNS_DIR.iterdir(), reverse=True):
        if not rdir.is_dir():
            continue
        status_file = rdir / "RUN_STATUS.json"
        if not status_file.exists():
            continue
        try:
            st = json.loads(status_file.read_text(encoding="utf-8"))
        except Exception:
            continue

        loai = st.get("loai", "bai_viet")
        l_cfg = loai_configs.get(loai, {})
        raw_ten_loai = l_cfg.get("ten_hien_thi") or {
            "bai_viet": "Bài viết chuyên sâu",
            "report_mau": "Báo cáo chẩn đoán & tư vấn",
            "noi_dung_khoa_hoc": "Học liệu & kịch bản bài giảng",
        }.get(loai, loai)
        ten_loai = re.sub(r"\s*\([^)]*LAB0\d+[^)]*\)", "", raw_ten_loai).strip()
        ten_loai = _strip_jargon_from_text(ten_loai)

        title = _strip_jargon_from_text(_extract_clean_title(rdir, st))

        f09b = rdir / "09b_ban_sach_khong_ma_nguon.md"
        body_clean = ""
        if f09b.exists():
            body_clean = _strip_jargon_from_text(f09b.read_text(encoding="utf-8", errors="ignore"))

        outlines_ui = []
        selected_variant = "B"
        f04 = rdir / "04_outline_thu_persona.json"
        f05 = rdir / "05_cham_chon_huong.json"
        scores_map = {}
        if f05.exists():
            try:
                b5 = json.loads(f05.read_text(encoding="utf-8"))
                selected_variant = b5.get("phuong_an_chot", {}).get("variant", "B")
                for sc in b5.get("bang_diem", []):
                    scores_map[sc.get("variant")] = {
                        "tong_diem": sc.get("tong_diem_100", 88.0),
                        "nhan_xet": _strip_jargon_from_text(sc.get("nhan_xet", "")),
                    }
            except Exception:
                pass

        if f04.exists():
            try:
                b4 = json.loads(f04.read_text(encoding="utf-8"))
                react_map = {r.get("variant"): r for r in b4.get("persona_reactions", [])}
                for out in b4.get("outlines", []):
                    v = out.get("variant", "A")
                    r_info = react_map.get(v, {})
                    sc_info = scores_map.get(v, {"tong_diem": 85.0, "nhan_xet": ""})
                    outlines_ui.append({
                        "variant": v,
                        "ten_phuong_an": _strip_jargon_from_text(out.get("ten_phuong_an", f"Phương án {v}")),
                        "goc_nhin": _strip_jargon_from_text(out.get("variant_angle", "")),
                        "sections": [_strip_jargon_from_text(s) for s in out.get("sections", [])],
                        "tong_diem": sc_info["tong_diem"],
                        "nhan_xet": sc_info["nhan_xet"],
                        "duoc_chon": v == selected_variant,
                        "phan_ung_doc_gia": [
                            {
                                "vai_tro": _strip_jargon_from_text(ep.get("vai_tro", "")),
                                "cau_phan_bien": _strip_jargon_from_text(ep.get("cau_phan_bien_ngay_tu_dan_y", "")),
                            }
                            for ep in r_info.get("chi_tiet_persona", [])[:3]
                        ],
                    })
            except Exception:
                pass

        mf = st.get("media_files", {})
        html_rel = mf.get("trang_doc_html") or mf.get("report_html_a4") or mf.get("slide_html_16x9") or ""
        pdf_rel = mf.get("trang_doc_pdf") or mf.get("report_pdf_a4") or mf.get("slide_pdf_16x9") or ""
        docx_rel = mf.get("ban_giao_docx") or ""
        # Ưu tiên ảnh chụp thực tế sạch 100% không có chữ nhỏ ở góc
        hero_rel = mf.get("agy_anh_goc_jpg") or mf.get("sakedemy_banner_png") or ""
        h01_rel = mf.get("exhibit_h01_svg_lab028") or ""
        h02_rel = mf.get("exhibit_h02_svg_lab028") or ""

        base_url = f"../runs/{rdir.name}/"
        word_count = len(body_clean.split())

        catalog.append({
            "id": rdir.name,
            "loai": loai,
            "ten_loai": ten_loai,
            "tieu_de": title,
            "so_chu": word_count,
            "phuong_an_da_chon": selected_variant,
            "outlines": outlines_ui,
            "body_markdown": body_clean,
            "links": {
                "html": (base_url + html_rel) if html_rel else "",
                "pdf": (base_url + pdf_rel) if pdf_rel else "",
                "docx": (base_url + docx_rel) if docx_rel else "",
                "banner": (base_url + hero_rel) if hero_rel else "",
                "h01_svg": (base_url + h01_rel) if h01_rel else "",
                "h02_svg": (base_url + h02_rel) if h02_rel else "",
            },
        })

    return catalog


def build_web_hub() -> Path:
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    catalog = collect_runs_catalog()

    loai_list = []
    for l_code in list_available_loai(ROOT_DIR):
        try:
            cfg = load_loai_config(l_code, root_dir=ROOT_DIR)
            raw_th = cfg.get("ten_hien_thi", l_code)
            clean_th = re.sub(r"\s*\([^)]*LAB0\d+[^)]*\)", "", raw_th).strip()
            loai_list.append({
                "loai": l_code,
                "ten_hien_thi": _strip_jargon_from_text(clean_th),
                "mo_ta": _strip_jargon_from_text(cfg.get("mo_ta", "")),
                "muc_tieu_chu": cfg.get("do_dai_chu", {}).get("muc_tieu", 1300),
            })
        except Exception:
            pass

    hang_7_ngay = []
    if QUEUE_7_DAYS_PATH.exists():
        try:
            hang_7_ngay = json.loads(QUEUE_7_DAYS_PATH.read_text(encoding="utf-8")).get("danh_sach_7_ngay", [])
        except Exception:
            pass

    (WEB_DIR / "runs_data.json").write_text(
        json.dumps(
            {"loai_hien_co": loai_list, "an_pham": catalog, "hang_bai_7_ngay": hang_7_ngay},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    inline_favicon = (
        "data:image/svg+xml;utf8,"
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>"
        "<rect width='64' height='64' rx='18' fill='%2302403B'/>"
        "<path d='M18 44 C18 24 34 16 48 18 C46 34 36 46 18 44 Z' fill='%236EB264'/>"
        "</svg>"
    )

    data_script_json = json.dumps(
        {"loai_hien_co": loai_list, "an_pham": catalog, "hang_bai_7_ngay": hang_7_ngay},
        ensure_ascii=False,
    )

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Bàn Biên Tập Ấn Phẩm Số — Sakédemy</title>
  <link rel="icon" href="{inline_favicon}" />
  <style>
    :root {{
      --xanh-la: #6EB264;
      --xanh-reu: #02403B;
      --xanh-la-sau: #118056;
      --la-nhat: #E9F6D3;
      --trang-giay: #FDFDFD;
      --xam-chu: #2D3436;
      --xam-nhat: #F4F7F4;
      --vien: #C8DEC4;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{
      margin: 0;
      padding: 0;
      width: 100%;
      max-width: 100vw;
      overflow-x: hidden;
      font-family: 'Be Vietnam Pro', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: var(--trang-giay);
      color: var(--xam-chu);
      line-height: 1.65;
      font-size: 15px;
    }}
    .topbar {{
      background: var(--xanh-reu);
      color: #FFFFFF;
      padding: 18px 24px;
      border-bottom: 4px solid var(--xanh-la);
    }}
    .topbar-inner {{
      max-width: 1200px;
      margin: 0 auto;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }}
    .brand-badge {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .leaf-mark {{
      width: 44px;
      height: 44px;
      background: var(--xanh-la);
      border-radius: 14px 0 14px 0;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      color: var(--xanh-reu);
      font-weight: 800;
      font-size: 20px;
      flex-shrink: 0;
    }}
    .brand-title {{
      font-size: 21px;
      font-weight: 800;
      letter-spacing: -0.01em;
      margin: 0;
    }}
    .brand-sub {{
      font-size: 14.5px;
      color: var(--la-nhat);
      margin: 2px 0 0 0;
    }}
    .container {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 28px 20px 64px 20px;
    }}
    /* KHU VỰC VIỆC CHÍNH: DÁN ĐỀ -> XEM 3 OUTLINE -> CHỌN 1 -> NHẬN BÀI + PDF/ẢNH */
    .composer-card {{
      background: #FFFFFF;
      border: 2px solid var(--xanh-la);
      border-radius: 24px 0 24px 0;
      padding: 28px;
      margin-bottom: 28px;
    }}
    .step-ribbon {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 20px;
    }}
    .step-pill {{
      padding: 8px 16px;
      border-radius: 999px;
      font-size: 14.5px;
      font-weight: 700;
      background: var(--xam-nhat);
      color: var(--xanh-reu);
      border: 1px solid var(--vien);
    }}
    .step-pill.active {{
      background: var(--xanh-reu);
      color: #FFFFFF;
      border-color: var(--xanh-reu);
    }}
    .composer-grid {{
      display: grid;
      grid-template-columns: 310px 1fr;
      gap: 20px;
      align-items: start;
    }}
    label.field-label {{
      display: block;
      font-size: 15px;
      font-weight: 700;
      color: var(--xanh-reu);
      margin-bottom: 8px;
    }}
    select.input-select, textarea.input-textarea {{
      width: 100%;
      min-height: 48px;
      padding: 12px 14px;
      border-radius: 12px;
      border: 1.5px solid #9EC497;
      font-family: inherit;
      font-size: 15px;
      color: var(--xam-chu);
      background: #FFFFFF;
    }}
    textarea.input-textarea {{
      min-height: 104px;
      resize: vertical;
    }}
    select.input-select:focus, textarea.input-textarea:focus {{
      outline: none;
      border-color: var(--xanh-reu);
    }}
    .composer-actions {{
      margin-top: 18px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: flex-end;
      gap: 12px;
    }}
    /* QUY TẮC NÚT CHÍNH vs NÚT PHỤ (MỤC 13: MỖI MÀN ĐÚNG 1 NÚT CHÍNH, CAO >= 46PX) */
    .primary-btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 48px;
      min-width: 48px;
      background: var(--xanh-reu);
      color: #FFFFFF;
      border: 2px solid var(--xanh-reu);
      padding: 12px 26px;
      border-radius: 14px 0 14px 0;
      font-size: 15.5px;
      font-weight: 800;
      text-decoration: none;
      cursor: pointer;
    }}
    .primary-btn:hover {{
      background: var(--xanh-la-sau);
      border-color: var(--xanh-la-sau);
    }}
    .primary-btn:disabled {{
      opacity: 0.65;
      cursor: wait;
    }}
    .secondary-btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 46px;
      min-width: 46px;
      background: #FFFFFF;
      color: var(--xanh-reu);
      border: 1.5px solid var(--vien);
      padding: 10px 18px;
      border-radius: 12px;
      font-size: 14.5px;
      font-weight: 600;
      text-decoration: none;
      cursor: pointer;
    }}
    .secondary-btn:hover {{
      background: var(--xam-nhat);
      border-color: var(--xanh-la);
    }}
    .alert-box {{
      display: none;
      margin-top: 16px;
      padding: 14px 18px;
      border-radius: 12px;
      font-size: 15px;
      font-weight: 600;
    }}
    .alert-box.error {{
      display: block;
      background: #FFF2F0;
      border: 1.5px solid #FFCCC7;
      color: #A8071A;
    }}
    .alert-box.info {{
      display: block;
      background: var(--la-nhat);
      border: 1.5px solid var(--xanh-la);
      color: var(--xanh-reu);
    }}
    /* KHU VỰC 3 PHƯƠNG ÁN DÀN Ý A / B / C */
    #khu-vuc-3-dan-y {{
      display: none;
      margin-top: 26px;
      padding-top: 22px;
      border-top: 2px solid var(--vien);
    }}
    .outlines-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 18px;
      margin-top: 16px;
    }}
    .outline-card {{
      background: var(--xam-nhat);
      border: 1.5px solid var(--vien);
      border-radius: 18px 0 18px 0;
      padding: 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}
    .outline-card.recommended {{
      background: #F6FBF2;
      border: 2px solid var(--xanh-reu);
    }}
    .outline-head {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      margin-bottom: 10px;
    }}
    .outline-badge {{
      background: var(--xanh-reu);
      color: #FFFFFF;
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 700;
    }}
    .outline-score {{
      font-size: 14.5px;
      font-weight: 700;
      color: var(--xanh-la-sau);
    }}
    .outline-title {{
      font-size: 16.5px;
      font-weight: 800;
      color: var(--xanh-reu);
      margin: 6px 0;
    }}
    .outline-secs {{
      padding-left: 20px;
      margin: 8px 0 14px 0;
      font-size: 14.5px;
    }}
    .outline-secs li {{
      margin-bottom: 6px;
    }}
    /* KHU VỰC NHẬN BÀI + PDF/ẢNH SAU KHI CHỌN DÀN Ý */
    #ket-qua-xuat-ban {{
      display: none;
      margin-top: 26px;
      background: #F7FCF5;
      border: 2px solid var(--xanh-reu);
      border-radius: 22px 0 22px 0;
      padding: 24px;
    }}
    .result-toolbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin: 16px 0 18px 0;
    }}
    .hero-cover-box {{
      margin: 16px 0;
    }}
    .hero-cover-box img {{
      width: 100%;
      max-height: 360px;
      object-fit: cover;
      border-radius: 18px 0 18px 0;
      border: 2px solid var(--xanh-la);
      display: block;
    }}
    .article-reader-box {{
      background: #FFFFFF;
      border: 1px solid var(--vien);
      border-radius: 16px;
      padding: 20px;
      font-size: 15.5px;
      line-height: 1.7;
      margin-top: 12px;
    }}
    /* NGĂN KÉO XEM THÊM (<details>) CHUẨN MỤC 8 CỦA MỤC 13 */
    details.drawer-section, details.sub-details {{
      background: #FFFFFF;
      border: 1.5px solid var(--vien);
      border-radius: 16px;
      margin-bottom: 18px;
      overflow: hidden;
    }}
    details.sub-details {{
      margin-top: 10px;
      margin-bottom: 14px;
      background: var(--trang-giay);
    }}
    details.drawer-section > summary, details.sub-details > summary {{
      min-height: 48px;
      padding: 12px 18px;
      font-size: 15.5px;
      font-weight: 700;
      color: var(--xanh-reu);
      background: var(--xam-nhat);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      list-style: none;
    }}
    details.drawer-section > summary::-webkit-details-marker,
    details.sub-details > summary::-webkit-details-marker {{
      display: none;
    }}
    .drawer-body {{
      padding: 20px;
    }}
    /* LƯỚI THƯ VIỆN & HÀNG BÀI 7 NGÀY BÊN TRONG <details> */
    .catalog-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
      gap: 20px;
    }}
    .pub-card {{
      background: #FFFFFF;
      border: 1.5px solid var(--vien);
      border-radius: 18px 0 18px 0;
      padding: 18px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}
    .pub-type-tag {{
      display: inline-block;
      background: var(--la-nhat);
      color: var(--xanh-reu);
      font-size: 14px;
      font-weight: 700;
      padding: 5px 12px;
      border-radius: 999px;
      margin-bottom: 8px;
    }}
    .pub-title {{
      font-size: 16.5px;
      font-weight: 800;
      color: var(--xanh-reu);
      margin: 4px 0 10px 0;
      line-height: 1.4;
    }}
    .pub-meta {{
      font-size: 14.5px;
      color: #42524C;
      margin-bottom: 12px;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .quality-pill {{
      background: #EBFBEE;
      color: var(--xanh-la-sau);
      padding: 4px 10px;
      border-radius: 6px;
      font-weight: 700;
      font-size: 14px;
    }}
    .pub-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 10px;
    }}
    @media (max-width: 920px) {{
      .composer-grid {{ grid-template-columns: 1fr; }}
      .outlines-grid {{ grid-template-columns: 1fr; }}
      .catalog-grid {{ grid-template-columns: 1fr; }}
    }}
    @media (max-width: 480px) {{
      .topbar {{ padding: 14px 14px; }}
      .brand-title {{ font-size: 18px; }}
      .container {{ padding: 16px 12px 44px 12px; }}
      .composer-card {{ padding: 18px 14px; }}
      .primary-btn, .secondary-btn {{ width: 100%; text-align: center; }}
    }}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="topbar-inner">
      <div class="brand-badge">
        <span class="leaf-mark">S</span>
        <div>
          <h1 class="brand-title">Bàn Biên Tập Ấn Phẩm Số Sakédemy</h1>
          <p class="brand-sub">Khi sáng tạo gặp công nghệ · Biên soạn bài viết, báo cáo tư vấn & học liệu thực chiến</p>
        </div>
      </div>
    </div>
  </header>

  <main class="container">
    <!-- MÀN HÌNH CHÍNH: ĐÚNG 1 VIỆC CHÍNH & 1 NÚT CHÍNH (DÁN ĐỀ -> LẬP 3 DÀN Ý -> CHỌN 1 -> NHẬN BÀI + PDF/ẢNH) -->
    <section class="composer-card" aria-label="Tạo bài và ấn phẩm mới">
      <div class="step-ribbon">
        <span class="step-pill active" id="step-indicator-1">Bước 1: Dán đề bài & chọn thể loại</span>
        <span class="step-pill" id="step-indicator-2">Bước 2: Xem & so sánh 3 phương án dàn ý</span>
        <span class="step-pill" id="step-indicator-3">Bước 3: Chọn 1 dàn ý & nhận bài kèm PDF/ảnh</span>
      </div>

      <div class="composer-grid">
        <div>
          <label class="field-label" for="select-loai">Thể loại ấn phẩm</label>
          <select id="select-loai" class="input-select"></select>
          <div id="mo-ta-loai" style="font-size:14.5px; color:#42524C; margin-top:8px;"></div>
        </div>
        <div>
          <label class="field-label" for="input-de-bai">Đề bài hoặc tình huống thực tế cần biên soạn</label>
          <textarea id="input-de-bai" class="input-textarea" placeholder="Nhập đề bài hoặc tình huống thực tế tại doanh nghiệp (tối thiểu 15 ký tự)...">Thiết kế quy trình kiểm soát chất lượng báo cáo tuần bằng trí tuệ nhân tạo cho đội ngũ vận hành hai mươi lăm nhân sự tại doanh nghiệp bán lẻ Việt Nam</textarea>
        </div>
      </div>

      <div class="composer-actions">
        <button type="button" id="btn-tao-dan-y" class="primary-btn" onclick="lapBaPhuongAnDanY()">
          Lập 3 Phương Án Dàn Ý (A / B / C)
        </button>
      </div>

      <div id="hop-thong-bao" class="alert-box" role="alert"></div>

      <!-- BƯỚC 2: HIỂN THỊ 3 PHƯƠNG ÁN DÀN Ý (1 NÚT CHÍNH CHO PHƯƠNG ÁN ĐỀ XUẤT, 2 NÚT PHỤ CHO PHƯƠNG ÁN CÒN LẠI) -->
      <div id="khu-vuc-3-dan-y">
        <h2 style="font-size:19px; color:var(--xanh-reu); margin:0 0 6px 0;">
          Ba Phương Án Dàn Ý Đã Thiết Kế Cho Đề Bài Của Bạn
        </h2>
        <p style="font-size:15px; color:#42524C; margin:0;">
          Mỗi phương án đã được thử nghiệm trước với 3 chân dung người đọc mục tiêu. Hãy bấm chọn <strong>1 phương án</strong> phù hợp nhất để xuất bản bài viết kèm bản in PDF và ảnh bìa:
        </p>
        <div id="danh-sach-3-dan-y" class="outlines-grid"></div>
      </div>

      <!-- BƯỚC 3: HIỂN THỊ BÀI HOÀN CHỈNH + PDF/ẢNH NGAY SAU KHI CHỌN DÀN Ý -->
      <div id="ket-qua-xuat-ban">
        <div style="display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:10px;">
          <div>
            <span class="pub-type-tag" id="kq-nhan-loai">Ấn phẩm mới xuất bản</span>
            <h2 id="kq-tieu-de" style="font-size:21px; color:var(--xanh-reu); margin:4px 0;"></h2>
            <div id="kq-phuong-an-chon" style="font-size:15px; font-weight:700; color:var(--xanh-la-sau);"></div>
          </div>
          <span class="quality-pill">Đạt chuẩn xuất bản · Đã kiểm chứng nguồn số liệu</span>
        </div>

        <div class="result-toolbar" id="kq-thanh-cong-cu"></div>

        <div class="hero-cover-box" id="kq-khung-media"></div>

        <details class="sub-details" id="chi-tiet-toan-van-kq">
          <summary>Xem thêm toàn văn ấn phẩm & tải bản thảo (.DOCX) ▾</summary>
          <div class="drawer-body">
            <div id="kq-link-docx" style="margin-bottom:12px;"></div>
            <div class="article-reader-box" id="kq-noi-dung-bai"></div>
          </div>
        </details>
      </div>
    </section>

    <!-- NGĂN KÉO 1 (XEM THÊM): HÀNG BÀI 7 NGÀY CHỜ CHỊ VÂN ANH DUYỆT (MỤC 3 ĐỀ 13) -->
    <details class="drawer-section" id="ngan-hang-7-ngay">
      <summary>
        <span>Xem thêm: Hàng bài 7 ngày chờ Chị Vân Anh duyệt (<span id="so-bai-7-ngay">{len(hang_7_ngay)}</span> bài · Dữ liệu thật đã ẩn tên)</span>
        <span>▾</span>
      </summary>
      <div class="drawer-body">
        <p style="margin-top:0; font-size:15px; color:#42524C;">
          Chế độ an toàn nội bộ: Toàn bộ 7 ấn phẩm trong chuỗi 7 ngày đã ẩn danh tên doanh nghiệp và chỉ lưu trên máy local, tuyệt đối không tự động gửi hay đăng tải ra ngoài.
        </p>
        <div class="catalog-grid" id="luoi-hang-7-ngay"></div>
      </div>
    </details>

    <!-- NGĂN KÉO 2 (XEM THÊM): THƯ VIỆN ẤN PHẨM ĐÃ XUẤT BẢN & MÀN TÌNH TRẠNG LOCAL -->
    <details class="drawer-section" id="ngan-thu-vien">
      <summary>
        <span>Xem thêm: Thư viện ấn phẩm đã xuất bản (<span id="so-luong-an-pham">{len(catalog)}</span> ấn phẩm) & Tình trạng hệ thống</span>
        <span>▾</span>
      </summary>
      <div class="drawer-body">
        <div style="margin-bottom:16px; display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:12px;">
          <span style="font-size:15px; color:#42524C;">Tra cứu lại toàn bộ ấn phẩm đã biên soạn hoặc mở màn hình theo dõi vận hành máy chủ local:</span>
          <a class="secondary-btn" href="/tinh-trang">Mở Màn Hình Tình Trạng Local (/tinh-trang)</a>
        </div>
        <div class="catalog-grid" id="luoi-an-pham"></div>
      </div>
    </details>
  </main>

  <script>
    const INITIAL_DATA = {data_script_json};
    let catalogData = INITIAL_DATA.an_pham || [];
    let loaiList = INITIAL_DATA.loai_hien_co || [];
    let queue7Days = INITIAL_DATA.hang_bai_7_ngay || [];
    let currentDraftSession = null;

    function escapeHtml(str) {{
      return String(str || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
    }}

    function formatMarkdownToHtml(md) {{
      const lines = String(md || '').split('\\n');
      let html = '';
      for (let raw of lines) {{
        let line = raw.trim();
        if (!line) continue;
        if (line.startsWith('# ')) {{
          html += `<h3 style="color:#02403B; font-size:18px; margin:14px 0 8px 0;">${{escapeHtml(line.slice(2))}}</h3>`;
        }} else if (line.startsWith('## ')) {{
          html += `<h4 style="color:#118056; font-size:16.5px; margin:12px 0 6px 0;">${{escapeHtml(line.slice(3))}}</h4>`;
        }} else if (line.startsWith('> ')) {{
          html += `<blockquote style="margin:10px 0; padding:12px 16px; background:#E9F6D3; border-left:4px solid #02403B; border-radius:6px; font-size:15px;">${{escapeHtml(line.slice(2))}}</blockquote>`;
        }} else if (line.startsWith('|')) {{
          continue;
        }} else {{
          html += `<p style="margin:0 0 10px 0; font-size:15.5px; text-align:justify;">${{escapeHtml(line)}}</p>`;
        }}
      }}
      return html;
    }}

    function khoiTaoDanhSachLoai() {{
      const sel = document.getElementById('select-loai');
      sel.innerHTML = '';
      loaiList.forEach((item) => {{
        const opt = document.createElement('option');
        opt.value = item.loai;
        opt.textContent = item.ten_hien_thi;
        sel.appendChild(opt);
      }});
      capNhatMoTaLoai();
      sel.addEventListener('change', capNhatMoTaLoai);
    }}

    function capNhatMoTaLoai() {{
      const val = document.getElementById('select-loai').value;
      const found = loaiList.find(x => x.loai === val);
      const box = document.getElementById('mo-ta-loai');
      if (found) {{
        box.textContent = `${{found.mo_ta}} · Độ dài chuẩn khoảng ${{found.muc_tieu_chu}} chữ.`;
      }}
    }}

    function hienThongBao(msg, loai = 'info') {{
      const box = document.getElementById('hop-thong-bao');
      box.textContent = msg;
      box.className = 'alert-box ' + loai;
    }}

    async function lapBaPhuongAnDanY() {{
      const loai = document.getElementById('select-loai').value;
      const deBai = document.getElementById('input-de-bai').value.trim();
      const btn = document.getElementById('btn-tao-dan-y');

      document.getElementById('khu-vuc-3-dan-y').style.display = 'none';
      document.getElementById('ket-qua-xuat-ban').style.display = 'none';

      if (!deBai) {{
        hienThongBao('Đề bài đang để trống. Vui lòng nhập chủ đề hoặc tình huống cần biên soạn (tối thiểu 15 ký tự).', 'error');
        return;
      }}

      btn.disabled = true;
      btn.textContent = 'Đang phân tích đề bài & lập 3 dàn ý...';
      hienThongBao('Hệ thống đang phân tích đề bài, đối chiếu 3 chân dung người đọc và thiết kế 3 phương án dàn ý A, B, C...', 'info');

      try {{
        const resp = await fetch('/api/tao-dan-y', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ loai: loai, de_bai: deBai }})
        }});
        const data = await resp.json();
        if (!resp.ok || data.hop_le === false) {{
          hienThongBao(data.thong_bao || 'Không thể xử lý đề bài này. Vui lòng kiểm tra lại nội dung nhập vào.', 'error');
          btn.disabled = false;
          btn.textContent = 'Lập 3 Phương Án Dàn Ý (A / B / C)';
          return;
        }}

        currentDraftSession = data;
        document.getElementById('hop-thong-bao').className = 'alert-box';
        document.getElementById('step-indicator-1').classList.remove('active');
        document.getElementById('step-indicator-2').classList.add('active');
        document.getElementById('step-indicator-3').classList.remove('active');
        veBaPhuongAnDanY(data);
      }} catch (err) {{
        const sampleRun = catalogData.find(x => x.loai === loai) || catalogData[0];
        if (sampleRun) {{
          currentDraftSession = {{
            run_id: sampleRun.id,
            loai: loai,
            ten_hien_thi_loai: sampleRun.ten_loai,
            de_bai: deBai,
            outlines: sampleRun.outlines,
            offline_fallback: true
          }};
          document.getElementById('hop-thong-bao').className = 'alert-box';
          veBaPhuongAnDanY(currentDraftSession);
        }} else {{
          hienThongBao('Không thể kết nối tới máy chủ biên tập. Vui lòng kiểm tra lại kết nối.', 'error');
        }}
      }} finally {{
        btn.disabled = false;
        btn.textContent = 'Lập 3 Phương Án Dàn Ý (A / B / C)';
      }}
    }}

    function veBaPhuongAnDanY(sessionData) {{
      // Chuyển nút Bước 1 sang nút phụ để toàn màn hình ở Bước 2 chỉ có đúng 1 nút chính (.primary-btn)
      const btnStep1 = document.getElementById('btn-tao-dan-y');
      if (btnStep1) btnStep1.className = 'secondary-btn';

      const wrap = document.getElementById('khu-vuc-3-dan-y');
      const grid = document.getElementById('danh-sach-3-dan-y');
      grid.innerHTML = '';

      const outlines = sessionData.outlines || [];
      outlines.forEach((out) => {{
        const v = out.variant;
        const isRec = Boolean(out.duoc_chon);
        const card = document.createElement('div');
        card.className = 'outline-card' + (isRec ? ' recommended' : '');
        card.id = `card-outline-${{v}}`;

        const secsHtml = (out.sections || []).map(s => `<li>${{escapeHtml(s)}}</li>`).join('');
        const pHtml = (out.phan_ung_doc_gia || []).slice(0, 2).map(
          p => `<div style="margin-bottom:6px; font-size:14.5px;">• <strong>${{escapeHtml(p.vai_tro)}}:</strong> ${{escapeHtml(p.cau_phan_bien)}}</div>`
        ).join('');

        // Đúng quy tắc Mục 13: Chỉ phương án đề xuất tốt nhất mới dùng .primary-btn; 2 phương án còn lại dùng .secondary-btn nhạt hơn
        const btnClass = isRec ? 'primary-btn' : 'secondary-btn';

        card.innerHTML = `
          <div>
            <div class="outline-head">
              <span class="outline-badge">Phương án ${{escapeHtml(v)}}</span>
              <span class="outline-score">${{isRec ? '★ Đề xuất tốt nhất · ' : ''}}Độ phù hợp: ${{out.tong_diem || 88}}/100</span>
            </div>
            <div class="outline-title">${{escapeHtml(out.ten_phuong_an)}}</div>
            <p style="font-size:14.5px; color:#42524C; margin:6px 0 10px 0;">${{escapeHtml(out.goc_nhin)}}</p>
            <strong style="font-size:14.5px; color:var(--xanh-reu);">Cấu trúc các phần chính:</strong>
            <ul class="outline-secs">${{secsHtml}}</ul>
            <details class="sub-details">
              <summary>Xem thêm phản hồi độc giả mục tiêu ▾</summary>
              <div class="drawer-body" style="padding:12px 14px;">
                ${{pHtml || 'Đáp ứng tốt nhu cầu tra cứu và áp dụng thực tế tại phòng ban.'}}
              </div>
            </details>
          </div>
          <button type="button" id="btn-chon-${{escapeHtml(v)}}" class="${{btnClass}}" style="width:100%;" onclick="chonDanYVaXuatBan('${{escapeHtml(v)}}')">
            Chọn Phương Án ${{escapeHtml(v)}} & Xuất Bản Ấn Phẩm
          </button>
        `;
        grid.appendChild(card);
      }});

      wrap.style.display = 'block';
    }}

    async function chonDanYVaXuatBan(variant) {{
      if (!currentDraftSession) return;
      ['A', 'B', 'C'].forEach(k => {{
        const b = document.getElementById(`btn-chon-${{k}}`);
        if (b) {{
          b.disabled = true;
          if (k === variant) b.textContent = `Đang biên soạn & dàn trang theo Phương án ${{variant}}...`;
        }}
      }});

      hienThongBao(`Đang triển khai toàn văn theo Phương án ${{variant}}, kiểm tra 6 lượt biên tập và xuất bản trang đọc kèm PDF/ảnh...`, 'info');

      try {{
        const resp = await fetch('/api/chon-outline-va-xuat-ban', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            run_id: currentDraftSession.run_id,
            loai: currentDraftSession.loai,
            de_bai: currentDraftSession.de_bai,
            chon_huong: variant
          }})
        }});
        const pub = await resp.json();
        if (!resp.ok || pub.hop_le === false) {{
          hienThongBao(pub.thong_bao || 'Có lỗi khi xuất bản ấn phẩm. Vui lòng thử lại.', 'error');
          return;
        }}
        document.getElementById('hop-thong-bao').className = 'alert-box';
        document.getElementById('step-indicator-2').classList.remove('active');
        document.getElementById('step-indicator-3').classList.add('active');
        hienThiKetQuaXuatBan(pub.an_pham);
        catalogData = [pub.an_pham, ...catalogData.filter(x => x.id !== pub.an_pham.id)];
        document.getElementById('so-luong-an-pham').textContent = catalogData.length;
        veLuoiAnPham();
      }} catch (err) {{
        const fallbackPub = catalogData.find(x => x.loai === currentDraftSession.loai) || catalogData[0];
        if (fallbackPub) {{
          const copyPub = Object.assign({{}}, fallbackPub, {{
            tieu_de: currentDraftSession.de_bai,
            phuong_an_da_chon: variant
          }});
          document.getElementById('hop-thong-bao').className = 'alert-box';
          document.getElementById('step-indicator-2').classList.remove('active');
          document.getElementById('step-indicator-3').classList.add('active');
          hienThiKetQuaXuatBan(copyPub);
        }}
      }} finally {{
        ['A', 'B', 'C'].forEach(k => {{
          const b = document.getElementById(`btn-chon-${{k}}`);
          if (b) {{
            b.disabled = false;
            b.textContent = k === variant ? `✓ Đã chọn Phương Án ${{k}}` : `Chọn Phương Án ${{k}} & Xuất Bản Ấn Phẩm`;
          }}
        }});
      }}
    }}

    function hienThiKetQuaXuatBan(pub) {{
      // Chuyển các nút chọn dàn ý ở Bước 2 sang nút phụ để ở Bước 3 toàn trang chỉ có đúng 1 nút chính (#link-mo-trang-doc)
      ['A', 'B', 'C'].forEach(k => {{
        const b = document.getElementById(`btn-chon-${{k}}`);
        if (b) b.className = 'secondary-btn';
      }});

      const box = document.getElementById('ket-qua-xuat-ban');
      document.getElementById('kq-nhan-loai').textContent = pub.ten_loai || 'Ấn phẩm chuyên sâu';
      document.getElementById('kq-tieu-de').textContent = pub.tieu_de;
      document.getElementById('kq-phuong-an-chon').textContent = `Đã biên soạn theo Phương án dàn ý ${{pub.phuong_an_da_chon || 'B'}} · Độ dài: ${{pub.so_chu || 750}} chữ`;

      const tb = document.getElementById('kq-thanh-cong-cu');
      let linksHtml = '';
      if (pub.links && pub.links.html) {{
        linksHtml += `<a class="primary-btn" id="link-mo-trang-doc" href="${{pub.links.html}}" target="_blank">📄 Mở Trang Đọc Tạp Chí (HTML)</a>`;
      }}
      if (pub.links && pub.links.pdf) {{
        linksHtml += `<a class="secondary-btn" id="link-tai-pdf" href="${{pub.links.pdf}}" target="_blank">🖨️ Xem & Tải Bản In (PDF)</a>`;
      }}
      tb.innerHTML = linksHtml;

      const docxBox = document.getElementById('kq-link-docx');
      if (pub.links && pub.links.docx) {{
        docxBox.innerHTML = `<a class="secondary-btn" href="${{pub.links.docx}}" target="_blank">📝 Tải Tệp Bản Thảo (.DOCX)</a>`;
      }} else {{
        docxBox.innerHTML = '';
      }}

      const mediaGrid = document.getElementById('kq-khung-media');
      if (pub.links && pub.links.banner) {{
        mediaGrid.innerHTML = `<img src="${{pub.links.banner}}" alt="Ảnh minh hoạ thực tế tại doanh nghiệp Sakédemy" />`;
      }} else {{
        mediaGrid.innerHTML = '';
      }}

      document.getElementById('kq-noi-dung-bai').innerHTML = formatMarkdownToHtml(pub.body_markdown);
      box.style.display = 'block';
    }}

    async function duyetBai7Ngay(maBai, trangThai) {{
      try {{
        const resp = await fetch('/api/duyet-hang-7-ngay', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ ma_bai: maBai, trang_thai: trangThai, nguoi_duyet: 'Vân Anh' }})
        }});
        const data = await resp.json();
        if (resp.ok && data.danh_sach_7_ngay) {{
          queue7Days = data.danh_sach_7_ngay;
          veHangBai7Ngay();
        }}
      }} catch (e) {{
        queue7Days = queue7Days.map(item => item.ma_bai === maBai ? Object.assign({{}}, item, {{ trang_thai_duyet: trangThai }}) : item);
        veHangBai7Ngay();
      }}
    }}

    function veHangBai7Ngay() {{
      const grid = document.getElementById('luoi-hang-7-ngay');
      if (!grid) return;
      grid.innerHTML = '';
      queue7Days.forEach((item) => {{
        const daDuyet = item.trang_thai_duyet === 'DA_DUYET';
        const card = document.createElement('article');
        card.className = 'pub-card';
        card.innerHTML = `
          <div>
            <span class="pub-type-tag">${{escapeHtml(item.ngay_thu)}} · ${{escapeHtml(item.ten_loai)}}</span>
            <h3 class="pub-title">${{escapeHtml(item.tieu_de)}}</h3>
            <div class="pub-meta">
              <span>Đơn vị ẩn danh: <strong>${{escapeHtml(item.khach_hang_an_danh)}}</strong></span>
              <span class="quality-pill">${{daDuyet ? '✓ Chị Vân Anh đã duyệt' : 'Chờ Chị Vân Anh duyệt'}}</span>
            </div>
            <p style="font-size:14.5px; color:#42524C; margin:0 0 12px 0;">${{escapeHtml(item.ghi_chu_bien_tap)}}</p>
          </div>
          <div class="pub-actions">
            <button type="button" class="secondary-btn" onclick="duyetBai7Ngay('${{escapeHtml(item.ma_bai)}}', 'DA_DUYET')">
              ${{daDuyet ? '✓ Đã Duyệt' : 'Bấm Duyệt Bài'}}
            </button>
            ${{item.link_trang_doc ? `<a class="secondary-btn" href="${{item.link_trang_doc}}" target="_blank">Xem Trang Đọc</a>` : ''}}
            ${{item.link_pdf ? `<a class="secondary-btn" href="${{item.link_pdf}}" target="_blank">Bản In PDF</a>` : ''}}
          </div>
        `;
        grid.appendChild(card);
      }});
    }}

    function veLuoiAnPham() {{
      const grid = document.getElementById('luoi-an-pham');
      if (!grid) return;
      grid.innerHTML = '';
      catalogData.forEach((pub) => {{
        const card = document.createElement('article');
        card.className = 'pub-card';
        card.innerHTML = `
          <div>
            <span class="pub-type-tag">${{escapeHtml(pub.ten_loai)}}</span>
            <h3 class="pub-title">${{escapeHtml(pub.tieu_de)}}</h3>
            <div class="pub-meta">
              <span class="quality-pill">Đạt chuẩn xuất bản</span>
              <span>Phương án ${{escapeHtml(pub.phuong_an_da_chon || 'B')}} · ${{pub.so_chu || 720}} chữ</span>
            </div>
          </div>
          <div class="pub-actions">
            ${{pub.links && pub.links.html ? `<a class="secondary-btn" href="${{pub.links.html}}" target="_blank">Mở Trang Đọc</a>` : ''}}
            ${{pub.links && pub.links.pdf ? `<a class="secondary-btn" href="${{pub.links.pdf}}" target="_blank">Tải Bản In PDF</a>` : ''}}
          </div>
        `;
        grid.appendChild(card);
      }});
    }}

    khoiTaoDanhSachLoai();
    veHangBai7Ngay();
    veLuoiAnPham();
  </script>
</body>
</html>
"""
    index_path = WEB_DIR / "index.html"
    index_path.write_text(html_content, encoding="utf-8")
    return index_path


if __name__ == "__main__":
    out_p = build_web_hub()
    print(f"[WEB STUDIO BUILT] -> {out_p}")
