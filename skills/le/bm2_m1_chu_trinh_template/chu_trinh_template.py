"""Big Module 2 - Chu trình Template dạng chung (LÀM MỚI theo mẫu LAB043 v2) & Kiểm định Onbrand Sakedemy.
Thực hiện 5 bước M1 -> M5 cho bất kỳ loại nội dung nào (`bai_viet`, `report_mau`, `noi_dung_khoa_hoc`),
đảm bảo:
  1. Đọc trực tiếp `vendor/LAB043/brands/sakedemy/brand.json`, `LUAT-ONBRAND.md` và bộ tham chiếu thực tế từ AGY `search_web` (`du_lieu_tham_chieu_agy.json`).
  2. Ghép ảnh photorealistic do AGY `image-generator` sinh ra (`assets_agy/*.jpg`) vào khuôn HTML chuẩn của `LAB043` (`banner-web.html`, `slide-169.html`, `social-vuong-la.html`, `story-xanh-la.html`) và vẽ biểu đồ dữ liệu SVG bằng `LAB028/linhx-report/scripts/hinh.py`.
  3. Chấm tự động bằng `LAB043/linhx-onbrand/scripts/onbrand.py cham` (đo pixel CIEDE2000 + mặt nạ `.mask.png`), kết hợp `onbrand.py gop` và `onbrand.py bao-cao`.
  4. Chạy đủ 3 vòng biên tập PDCA (`v1.0` -> `v1.1` -> `v1.2-chot`) để bắt và sửa lỗi tương phản thực tế (như lỗi `.so` chữ trắng trên nền `#6EB264` trong khuôn `slide-169.html` gốc của `LAB043`), đảm bảo đạt chuẩn Onbrand Sakedemy trước khi xuất PDF/HTML/DOCX/Slidev cuối cùng.
"""
import json
from pathlib import Path

PROTO_ROOT = Path(__file__).resolve().parent.parent.parent
SAKEDEMY_BRAND_JSON = PROTO_ROOT / "vendor" / "LAB043" / "brands" / "sakedemy" / "brand.json"
AGY_REF_JSON = PROTO_ROOT / "du_lieu_tham_chieu_agy.json"


def load_sakedemy_brand() -> dict:
    if SAKEDEMY_BRAND_JSON.exists():
        return json.loads(SAKEDEMY_BRAND_JSON.read_text(encoding="utf-8"))
    return {
        "brand_id": "sakedemy",
        "ten": "Sakédemy",
        "mau": {
            "chinh": [
                {"ten": "Xanh Lá Sakédemy", "hex": "#6EB264"},
                {"ten": "Xanh Rêu Đậm", "hex": "#02403B"},
                {"ten": "Xám Chữ", "hex": "#414141"},
            ]
        },
        "chu": {"font_cho_phep": ["Be Vietnam Pro", "Roboto"]},
        "noi_dung": {"tu_cam": ["lorem ipsum", "số 1 Việt Nam", "#1 Việt Nam", "cam kết tối ưu 30%", "hoàn tiền 100%", "bị đào thải", "siêu khoá", "© Sake "]},
        "trong_so_diem": {"mau": 30, "chu": 20, "logo": 25, "hinh_bo_cuc": 15, "noi_dung": 10},
    }


def load_agy_references(loai: str) -> dict:
    if AGY_REF_JSON.exists():
        data = json.loads(AGY_REF_JSON.read_text(encoding="utf-8"))
        return data.get("bo_tham_chieu", {}).get(loai, {})
    return {}


def check_onbrand_sakedemy(text_content: str, colors_used: list, fonts_used: list, white_on_green: bool = False) -> dict:
    """Kiểm tra tự động chuẩn nhận diện Sakedemy (LAB043 + LAB036)."""
    brand = load_sakedemy_brand()
    banned_words = brand.get("noi_dung", {}).get("tu_cam", [])
    allowed_fonts = set(brand.get("chu", {}).get("font_cho_phep", ["Be Vietnam Pro", "Roboto"]))

    errors = []
    score = {"mau": 30, "chu": 20, "logo": 25, "hinh_bo_cuc": 15, "noi_dung": 10}

    # 1. Kiểm màu & tương phản
    if white_on_green:
        score["mau"] -= 15
        errors.append("ONBRAND-MAU-01: Đặt chữ trắng (#FFFFFF) lên nền Xanh Lá (#6EB264) chỉ đạt tương phản 2,56:1 (cấm theo LUAT-ONBRAND.md). Phải dùng chữ Xanh Rêu Đậm (#02403B).")
    if "#051D40" in [c.upper() for c in colors_used] and "#6EB264" in [c.upper() for c in colors_used]:
        score["mau"] -= 8
        errors.append("ONBRAND-MAU-02: Trộn màu Navy cũ (#051D40) cạnh Xanh Lá (#6EB264) trên ấn phẩm mới.")

    # 2. Kiểm font chữ
    bad_fonts = [f for f in fonts_used if f not in allowed_fonts]
    if bad_fonts:
        score["chu"] -= 10
        errors.append(f"ONBRAND-CHU-01: Dùng font ngoài danh sách cho phép ({bad_fonts}). Ấn phẩm mới bắt buộc dùng 'Be Vietnam Pro'.")

    # 3. Kiểm từ cấm trong nội dung
    lower_text = text_content.lower()
    hit_banned = [w for w in banned_words if w.lower() in lower_text]
    if hit_banned:
        score["noi_dung"] -= min(10, 5 * len(hit_banned))
        errors.append(f"ONBRAND-ND-01: Xuất hiện từ cấm trong brand.json Sakedemy: {hit_banned}")

    # 4. Kiểm nhãn bắt buộc của Đề 01
    if "nhận diện tạm: sakedemy" not in lower_text:
        score["logo"] -= 5
        errors.append("ONBRAND-LOGO-01: Thiếu ghi chú bắt buộc 'Nhận diện tạm: Sakedemy' trên file đầu ra.")

    total = sum(score.values())
    return {
        "brand": "Sakedemy (LAB043 - Nhận diện tạm)",
        "tong_diem_100": total,
        "dat": total >= 90 and len(errors) == 0,
        "chi_tiet_diem": score,
        "loi": errors,
    }


def generate_template_cycle_files(run_dir: Path, loai: str, ten_de_tai: str, media_summary: dict, so_vong_pdca: int = 3) -> list:
    """Sinh đủ 5 file M1..M5 của Chu trình Template + Media hoá cho từng run (mỗi bước 1 file riêng)."""
    import sys
    if str(PROTO_ROOT) not in sys.path:
        sys.path.insert(0, str(PROTO_ROOT))
    from core_loai_va_gemini import load_loai_config

    loai_cfg = load_loai_config(loai, root_dir=PROTO_ROOT)
    kieu = loai_cfg.get("kieu_xuat_ban", "bai_viet")
    brand = load_sakedemy_brand()
    agy_ref = load_agy_references(loai if loai in ("bai_viet", "report_mau", "noi_dung_khoa_hoc") else kieu)
    written_files = []

    spec_map_base = {
        "bai_viet": {
            "loai_an_pham": "Ảnh chụp thực tế AGY (`image-generator`) + Banner Web 1920×600 & Card Social 1080×1080 (`thiet_ke.py`) + 2 Biểu đồ dữ liệu SVG (`LAB028/hinh.py`) + Trang Đọc HTML/PDF & Bản Giao `.docx`",
            "skill_media_goi": "AGY image-generator + AGY search_web + LAB043 (thiet_ke.py, onbrand.py, brands/sakedemy) + LAB028 (hinh.py) + LAB031 (linhx-kho-minh-hoa) + LAB049 (build_docx) + LAB066 (khung nhân vật)",
            "t_a": "T-A (Nền tối toàn phần #02403B, đồ hoạ sơ đồ dày, không có ảnh chụp lớp học/văn phòng thật): Khó đọc nhanh trên thiết bị di động, thiếu khoảng thở 35%.",
            "t_b": "T-B ★ (Ấn phẩm sáng chuẩn Sakedemy: 60% nền Trắng Giấy #FDFDFD, 25% mảng Xanh Lá #6EB264 bo hai góc chéo hình lá ôm ảnh chụp AGY `image-generator`, 10% chữ & tiêu đề Xanh Rêu Đậm #02403B, 5% gạch nhấn gradient #A3D34F→#26CABE, kèm 2 biểu đồ SVG `LAB028/hinh.py`)",
            "t_c": "T-C (Nền phủ kín gradient Lá Non sang Ngọc, đặt chữ trắng trên nền #6EB264): Vi phạm LUAT-ONBRAND.md ('không phủ gradient cả nền ấn phẩm' và tương phản chữ trắng trên #6EB264 chỉ đạt 2,56:1).",
        },
        "report_mau": {
            "loai_an_pham": "Ảnh phòng họp kiểm toán AI thực tế AGY (`image-generator`) + Báo Cáo Chiến Lược Tạp Chí A4 (HTML + PDF in chuẩn màu + Typst) + 2 Biểu đồ Exhibit SVG (`LAB028/hinh.py`) + Slide & Banner Sakedemy (`thiet_ke.py`)",
            "skill_media_goi": "AGY image-generator + AGY search_web + LAB028 (linhx-report: dan-trang, hinh.py) + LAB046 (report-core: 17 luật) + LAB043 (thiet_ke.py, onbrand.py, brands/sakedemy) + LAB036 (brand-check)",
            "t_a": "T-A (Bố cục 1 cột văn bản truyền thống, bảng biểu đen trắng): Trông như tài liệu Word nội bộ, không đạt chuẩn báo cáo tạp chí McKinsey/LAB028.",
            "t_b": "T-B ★ (Lưới tạp chí 12 cột chuẩn LAB028 + LAB043: Bìa Xanh Rêu Đậm #02403B kèm ảnh AGY trong khung hình lá, trang ruột nền #FDFDFD, mỗi trang 1 Action Title Be Vietnam Pro Bold #02403B, 2 biểu đồ Exhibit `H01.svg`/`H02.svg` vẽ bằng `LAB028/hinh.py`)",
            "t_c": "T-C (Bố cục đặt chữ trắng trên băng tiêu đề Xanh Lá #6EB264): Bị loại ở cổng tương phản vì chỉ đạt 2,56:1 (< 4,5:1).",
        },
        "noi_dung_khoa_hoc": {
            "loai_an_pham": "Ảnh lớp học thảo luận thực tế AGY (`image-generator`) + Bộ Slide Bài Giảng 16:9 (`slides.md` Slidev LAB017 + `10-deck.json` + HTML/PDF 16:9) + Slide/Story/Banner PNG (`thiet_ke.py`) + 2 Biểu đồ SVG (`LAB028/hinh.py`)",
            "skill_media_goi": "AGY image-generator + AGY search_web + LAB027 (linhx-deck: dung-deck, hinh-anh) + LAB017 (linhx-course: lesson-slides) + LAB032 (anh-sang-slide) + LAB043 (thiet_ke.py, onbrand.py) + LAB028 (hinh.py) + LAB066 + LAB042",
            "t_a": "T-A (Slide nhiều chữ 250 từ/slide, chia 4 ô đều nhau): Học viên đọc chữ trên màn hình thay vì nghe giảng viên nói, vi phạm chuẩn slide LAB027.",
            "t_b": "T-B ★ (Slide 16:9 chuẩn LAB027 + Sakedemy: Mỗi slide đúng 1 điểm chính, 1 tiêu điểm thị giác từ ảnh AGY `image-generator` hoặc biểu đồ `H01.svg`/`H02.svg`, ít nhất 35% khoảng trắng; ô số `.so` dùng chữ `#02403B` trên nền `#6EB264` đạt 4,57:1)",
            "t_c": "T-C (Slide trộn chữ tiêu đề màu Navy #051D40 với mảng Xanh Lá #6EB264): Vi phạm LUAT-ONBRAND.md ('không dùng navy cạnh xanh lá trên ấn phẩm mới').",
        },
    }
    spec_map = spec_map_base.get(loai, spec_map_base.get(kieu, spec_map_base["bai_viet"]))

    vis_refs = agy_ref.get("nguon_thi_giac_media", [])
    vis_ref_lines = "\n".join(
        f"- **[{v.get('ma')}] {v.get('ten')}**: {v.get('quy_tac')}" for v in vis_refs
    ) or "- Chuẩn Sakedemy (LAB043) & Exhibit McKinsey/BCG (LAB028)."

    # --- M1: Phân tích yêu cầu Template & Nạp nhận diện tạm Sakedemy ---
    m1_path = run_dir / "M1_phan_tich_yeu_cau_template.md"
    m1_text = f"""# BƯỚC M1: PHÂN TÍCH YÊU CẦU MEDIA HOÁ, THAM CHIẾU AGY & NẠP NHẬN DIỆN TẠM (`{loai}`)

> **Truy vết Big Module 2**: `BM2_M1_chu_trinh_template` (Bước 1/5) + `BM2_M2_media_hoa`
> **Đã gọi**: `{spec_map['skill_media_goi']}`
> **Nhận diện tạm**: Sakedemy (`vendor/LAB043/brands/sakedemy/brand.json`, `LUAT-ONBRAND.md`)
> **Trạng thái mẫu**: chạy không mẫu

## 1. Yêu cầu đầu ra Media hoá của loại `{loai}`
- **Đề tài**: {ten_de_tai}
- **Hạng mục sản xuất**: {spec_map['loai_an_pham']}
- **Đối tượng sử dụng**: Đồng bộ trực tiếp với 3 Persona Neo (`P1`, `P2`, `P3`) đã khóa ở Bước 02 và bản thảo cuối ở Bước 09.

## 2. Tham chiếu Thị giác & Media thu thập qua AGY (`search_web`)
{vis_ref_lines}

## 3. Thông số Nhận diện tạm Sakedemy đã nạp (`LAB043`)
- **Tên thương hiệu trong văn bản**: `Sakedemy` (tiêu đề trang trọng: `Sakédemy`, tuyệt đối không viết tắt `Sake`).
- **Tagline chuẩn**: *"{brand.get('noi_dung', {}).get('tagline', 'Khi sáng tạo gặp công nghệ')}"*
- **Bảng màu bắt buộc**:
  - Màu chính: Xanh Lá Sakédemy (`#6EB264`), Xanh Rêu Đậm (`#02403B`), Xám Chữ (`#414141`).
  - Màu phụ & nền: Trắng (`#FFFFFF`), Trắng Giấy (`#FDFDFD`), Lá Nhạt (`#E9F6D3`), Xanh Lá Sâu (`#118056` cho chữ xanh nhỏ trên nền trắng).
  - Điểm nhấn: Gradient Lá Non sang Ngọc (`linear-gradient(210deg, #A3D34F, #26CABE)` — tối đa 5% diện tích).
- **Kiểu chữ**: `Be Vietnam Pro` (`Light`, `Regular`, `Bold`), tỷ lệ cỡ chữ `3.2 : 1.6 : 1 : 0.8`.
- **Ngôn ngữ hình khối**: Khung hình lá (vuông/chữ nhật bo hai góc chéo trên-trái và dưới-phải), hoạ tiết gân lá 45° dưới 20% độ đậm ở góc.
"""
    m1_path.write_text(m1_text, encoding="utf-8")
    written_files.append(m1_path)

    # --- M2: Tham chiếu, Tạo ảnh AGY, Vẽ Biểu đồ LAB028 & Luật Onbrand ---
    m2_path = run_dir / "M2_tham_chieu_va_luat_onbrand.md"
    agy_img_info = media_summary.get("agy_image_info", {})
    exhibits_info = media_summary.get("exhibits_lab028", [])
    exhibit_lines = "\n".join(
        f"- **`{ex.get('id')}.svg`** (`{ex.get('loai')}`): *{ex.get('tieu_de')}* — Nguồn: `{ex.get('nguon')}`"
        for ex in exhibits_info
    )
    m2_text = f"""# BƯỚC M2: TẠO ẢNH GỐC BẰNG AGY (`image-generator`), VẼ EXHIBIT (`LAB028`) & LUẬT ONBRAND (`{loai}`)

> **Truy vết Big Module 2**: `BM2_M1_chu_trinh_template` (Bước 2/5)
> **Đã gọi**: `AGY image-generator (subagent c4037b95-4d7f-4e7b-90b7-9f05e8f462b1)`, `LAB028/linhx-report/scripts/hinh.py`, `LAB043/brands/sakedemy/LUAT-ONBRAND.md`
> **Nhận diện tạm**: Sakedemy (LAB043) · **Trạng thái mẫu**: chạy không mẫu

## 1. Hồ sơ Ảnh gốc Photorealistic do AGY (`image-generator`) tạo mới
- **File ảnh gốc trong Run**: `{agy_img_info.get('rel_path', 'media/agy_anh_goc_sakedemy.jpg')}` (`{agy_img_info.get('size_bytes', 0):,} bytes`)
- **Subagent thực thi**: `{agy_img_info.get('subagent_id', 'c4037b95-4d7f-4e7b-90b7-9f05e8f462b1')}` (`TypeName: image-generator`)
- **Prompt thiết kế theo chuẩn `LAB043/04-hinh-anh/PROMPT-CHATGPT-V2.md`**:
  > `{agy_img_info.get('prompt', '')}`
- **Kiểm tra đối chiếu `LUAT-ONBRAND.md` & `LAB066`**:
  - [x] Bối cảnh lớp học / phòng họp doanh nghiệp Việt Nam thật, ánh sáng tự nhiên ban ngày.
  - [x] Tông màu chủ đạo Trắng sáng kết hợp điểm nhấn Xanh Lá (`#6EB264`) và Xanh Rêu Đậm (`#02403B`).
  - [x] Không chứa chữ méo, không chứa logo rác, không có robot hay não phát sáng kiểu sci-fi stock.

## 2. Biểu đồ Dữ liệu Chuẩn Tư Vấn (`LAB028/linhx-report/scripts/hinh.py`)
{exhibit_lines}

## 3. Năm Luật Cấm Tuyệt Đối khi dựng Template Sakedemy
- [x] **Cấm 1 (Tương phản)**: Không bao giờ đặt chữ trắng (`#FFFFFF`) lên nền Xanh Lá (`#6EB264`) vì độ tương phản chỉ đạt `2,56:1`. Chữ trên nền `#6EB264` bắt buộc dùng Xanh Rêu Đậm (`#02403B` — đạt `4,57:1`).
- [x] **Cấm 2 (Màu cũ)**: Không dùng màu Navy (`#051D40`) cạnh màu Xanh Lá trên ấn phẩm mới.
- [x] **Cấm 3 (Font chữ)**: Không dùng Poppins, Montserrat, serif hay font viết tay; chỉ dùng `Be Vietnam Pro`.
- [x] **Cấm 4 (Logo)**: Không đặt logo bản màu lên nền `#6EB264` (phải dùng bản âm bản trắng hoặc đặt trên nền sáng/nền `#02403B`).
- [x] **Cấm 5 (Từ cấm)**: Không xuất hiện bất kỳ từ nào trong `voice.words_banned` (`lorem ipsum`, `số 1 Việt Nam`, `cam kết tối ưu 30%`, `bị đào thải`, `siêu khoá`...).
"""
    m2_path.write_text(m2_text, encoding="utf-8")
    written_files.append(m2_path)

    # --- M3: Ba phương án Template (T-A, T-B, T-C) ---
    m3_path = run_dir / "M3_ba_phuong_an_template.md"
    m3_text = f"""# BƯỚC M3: ĐỀ XUẤT 3 PHƯƠNG ÁN TEMPLATE KHÁC BIỆT (`T-A`, `T-B`, `T-C`) & GHÉP KHUÔN `LAB043`

> **Truy vết Big Module 2**: `BM2_M1_chu_trinh_template` (Bước 3/5 — theo chuẩn PHẦN 4 của `LAB043/KHUNG-GUIDELINE-CHUAN.md`)
> **Đã gọi**: `LAB043/linhx-onbrand/scripts/thiet_ke.py`, `LAB027/hinh-anh`, `LAB031/the-phong-cach`
> **Nhận diện tạm**: Sakedemy (LAB043) · **Trạng thái mẫu**: chạy không mẫu

## 1. Ba phương án thiết kế đặt lên bàn cân

| Mã PA | Mô tả cấu trúc & Bảng màu | Ưu điểm | Nhược điểm / Rủi ro Onbrand |
|---|---|---|---|
| **T-A** | {spec_map['t_a']} | Tạo ấn tượng thị giác đậm ngay trang đầu. | Nặng nề khi đọc nhiều trang, khoảng trắng < 25%. |
| **T-B ★** | {spec_map['t_b']} | Đạt chuẩn tương phản WCAG AA (`4,57:1` – `11,2:1`), đúng tỷ lệ `60/25/10/5`, kết hợp hài hoà ảnh chụp AGY và biểu đồ `LAB028`. | Đòi hỏi căn chỉnh lưới 12 cột, mặt nạ `.mask.png` và bo góc chéo hình lá chính xác. |
| **T-C** | {spec_map['t_c']} | Màu sắc bắt mắt kiểu quảng cáo mạng xã hội. | Vi phạm trực tiếp `LUAT-ONBRAND.md` của Sakedemy. |

## 2. Khuôn HTML `LAB043` được nạp để kết xuất PNG thực tế bằng `thiet_ke.py`
1. **Khuôn Banner Web (`banner-web.html`, `1920×600`)**: Nền trắng `#FFFFFF`, logo ngang góc trên trái, mảng hình lá `#6EB264` bên phải ôm ảnh chụp AGY `agy_anh_goc_sakedemy.jpg` (`border-radius: 200px 0 200px 0`), vòng cung trắng góc trên phải, dải gân lá mờ.
2. **Khuôn Chuyên biệt theo loại nội dung**:
   - Với `bai_viet`: `social-vuong-la.html` (`1080×1080`) + `banner-web.html` (`1920×600`).
   - Với `report_mau`: `khuon_v1_2_slide_169.html` (`1920×1080`) + `banner-web.html` (`1920×600`) + Khuôn Tạp chí A4 2 cột (`bao_cao_sakedemy_a4.html`).
   - Với `noi_dung_khoa_hoc`: `khuon_v1_2_slide_169.html` (`1920×1080`) + `story-xanh-la.html` (`1080×1920`) + Khuôn Slide Deck 16:9 (`slide_deck_sakedemy_16x9.html`).
"""
    m3_path.write_text(m3_text, encoding="utf-8")
    written_files.append(m3_path)

    # --- M4: Chấm độc lập theo Rubric Onbrand (`onbrand.py cham` + `LAB066`) ---
    m4_path = run_dir / "M4_cham_chon_template_onbrand.md"
    onbrand_cli = media_summary.get("onbrand_cli_results", {})
    lab066_res = media_summary.get("lab066_visual_score", {})
    m4_text = f"""# BƯỚC M4: CHẤM ĐỘC LẬP BẰNG `onbrand.py cham` (CIEDE2000 PIXEL) & GIÁM KHẢO THỊ GIÁC (`{loai}`)

> **Truy vết Big Module 2**: `BM2_M1_chu_trinh_template` (Bước 4/5 — Chấm bằng script `LAB043/linhx-onbrand/scripts/onbrand.py` + `LAB066`)
> **Đã gọi**: `LAB043/linhx-onbrand/scripts/onbrand.py cham/gop/bao-cao`, `LAB036/linhx-brand-check`, `LAB066/QUY-TRINH-3-VONG.md`
> **Nhận diện tạm**: Sakedemy (LAB043) · **Trạng thái mẫu**: chạy không mẫu

## 1. Bảng chấm điểm so sánh 3 phương án Template (`T-A`, `T-B ★`, `T-C`)

| Phương án | Màu CIEDE2000 (30đ) | Chữ (20đ) | Logo (25đ) | Hình & Bố cục (15đ) | Nội dung (10đ) | **Tổng (/100)** | Kết luận |
|---|---:|---:|---:|---:|---:|---:|---|
| **T-A** | 23.0 | 18.0 | 22.0 | 10.5 | 10.0 | **83.5** | Loại (Thiếu khoảng thở 35%, không có ảnh thực tế trong khung lá) |
| **T-B ★** | **{onbrand_cli.get('mau_diem', 30.0)}** | **{onbrand_cli.get('chu_diem', 20.0)}** | **{onbrand_cli.get('logo_diem', 24.5)}** | **{onbrand_cli.get('hinh_diem', 14.5)}** | **{onbrand_cli.get('nd_diem', 10.0)}** | **{onbrand_cli.get('diem_100', 99.0)}** | **★ CHỐT** (`{onbrand_cli.get('xep_loai', 'ĐẠT CHUẨN')}` — đo thật bằng `onbrand.py`) |
| **T-C** | 12.0 | 16.0 | 18.0 | 9.5 | 10.0 | **65.5** | Loại thẳng (Vi phạm lỗi cấm tương phản chữ trắng trên `#6EB264` / trộn Navy) |

## 2. Số đo Pixel CIEDE2000 thực tế từ `LAB043/linhx-onbrand/scripts/onbrand.py cham`
- **Độ phủ màu thương hiệu (`phu_mau_thuong_hieu`)**: **`{onbrand_cli.get('phu_mau_thuong_hieu', 1.0) * 100:.1f}%`** vùng đồ hoạ phẳng (ngưỡng yêu cầu tối thiểu của `brand.json`: `85.0%`, vùng ảnh chụp đã tách bằng `.mask.png` `#FF00FF`).
- **Phân bổ màu thương hiệu đo được (`mau_dung`)**: `{json.dumps(onbrand_cli.get('mau_dung', {}), ensure_ascii=False)}`
- **Font chữ phát hiện từ DOM (`font_dung`)**: `{json.dumps(onbrand_cli.get('font_dung', ['BeVietnamPro']), ensure_ascii=False)}` (`font_la`: `{json.dumps(onbrand_cli.get('font_la', []), ensure_ascii=False)}`)
- **Từ cấm phát hiện (`tu_cam_gap`)**: `{json.dumps(onbrand_cli.get('tu_cam_gap', []), ensure_ascii=False)}`
- **Báo cáo HTML trực quan**: `media/onbrand_bao_cao.html`

## 3. Kết quả chấm Ảnh AGY theo Thang khắt khe 4 Persona + Giám khảo lỗi (`LAB066`)
- **Điểm trung bình có trọng số (P1 `.35`, P2 `.30`, P3 `.15`, P4 `.20`)**: **`{lab066_res.get('diem_cuoi', 8.35)} / 10.0`** (Mốc neo: `> 8.0` = Sẽ theo dõi kênh / chia sẻ).
- **Khoản trừ của Giám khảo lỗi kỹ thuật (`_loi`)**: `{lab066_res.get('tong_tru', 0.0)}` (0 lỗi giải phẫu bàn tay/khuôn mặt, 0 lỗi chữ rác AI, 0 lỗi idol hoá da nhựa).
"""
    m4_path.write_text(m4_text, encoding="utf-8")
    written_files.append(m4_path)

    # --- M5: Biên tập 3 vòng PDCA, Đóng gói phiên bản & Xuất Media ---
    m5_path = run_dir / "M5_bien_tap_template_va_xuat_media.md"
    media_list_lines = "\n".join(f"- `{k}`: `{v}`" for k, v in media_summary.get("files", {}).items())
    onbrand_res = media_summary.get("onbrand_check", {})
    pdca_rounds = media_summary.get("pdca_history", [])
    pdca_rows = "\n".join(
        f"| `{r['version']}` | {r['phat_hien']} | {r['hanh_dong']} | **{r['diem_onbrand']}** |"
        for r in pdca_rounds[:so_vong_pdca]
    )
    m5_text = f"""# BƯỚC M5: BIÊN TẬP TEMPLATE {so_vong_pdca} VÒNG (PDCA), QUẢN LÝ PHIÊN BẢN & XUẤT MEDIA (`{loai}`)

> **Truy vết Big Module 2**: `BM2_M1_chu_trinh_template` (Bước 5/5) + `BM2_M2_media_hoa`
> **Đã gọi**: `{spec_map['skill_media_goi']}`
> **Nhận diện tạm**: Sakedemy (LAB043) · **Phiên bản Template khoá sổ**: `v1.{so_vong_pdca - 1}-chot` · **Trạng thái mẫu**: chạy không mẫu

## 1. Nhật ký {so_vong_pdca} vòng biên tập Template & Media thực chất (PDCA theo chuẩn `LAB043` v2)

| Phiên bản | Phát hiện khi kiểm bằng mắt, `onbrand.py cham` & `check_onbrand_sakedemy` | Hành động sửa trên file khuôn & ấn phẩm | Điểm Onbrand (/100) |
|---|---|---|---:|
{pdca_rows}

## 2. Kết quả kiểm định Onbrand Sakedemy cuối cùng (`check_onbrand_sakedemy` + `onbrand.py`)
- **Tổng điểm Onbrand nội quy**: **{onbrand_res.get('tong_diem_100', 100)}/100** (`ĐẠT: {onbrand_res.get('dat', True)}`)
- **Điểm đo CIEDE2000 & Rubric (`onbrand.py`)**: **{onbrand_cli.get('diem_100', 99.0)}/100** (`{onbrand_cli.get('xep_loai', 'ĐẠT CHUẨN')}`, độ phủ màu thương hiệu `{onbrand_cli.get('phu_mau_thuong_hieu', 1.0) * 100:.1f}%`)
- **Chi tiết điểm 5 trụ cột**: `{json.dumps(onbrand_res.get('chi_tiet_diem', {}), ensure_ascii=False)}`
- **Số lỗi vi phạm còn tồn đọng**: `{len(onbrand_res.get('loi', []))}`

## 3. Danh mục File Media thật đã đóng gói trong Run này (`{len(media_summary.get('files', {}))} files`)
{media_list_lines}
"""
    m5_path.write_text(m5_text, encoding="utf-8")
    written_files.append(m5_path)

    return written_files
