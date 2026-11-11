"""Vẽ ngược cấu trúc thị giác & sinh prompt tái tạo cho `rea-anh`.

Cách gọi:
    python linhx-rea/scripts/ve_nguoc.py <thu_muc_anh>
    (Cũng hỗ trợ truyền <dir_ra> chứa nhiều thư mục ảnh con có do.json)

Đầu ra trong `<anh>/ve-nguoc/`:
    - khoi.png    : * Ảnh thường: bản khối 3 lớp xám (gần sáng 235, giữa 140, xa tối 45) + viền đen mảnh Canny.
                    * Ảnh phẳng (`do_sau.phang=true`): bản khối BỐ CỤC trên lưới 24×N ô (`chu`, `hinh`, `khoang_trong`)
                      tô 3 sắc xám khác nhau + viền + chú giải, kèm xuất `bo_cuc.json`.
    - bo_cuc.json : (chỉ khi `do_sau.phang=true`) tỉ lệ `chu` / `hinh` / `khoang_trong` và hộp các khối chữ lớn.
    - khung.png   : nền xám nhạt + lưới 1/3 + 2 đường chéo mảnh + điểm hút mắt đánh số + mũi tên đường dẫn mắt.
    - prompt.md   : prompt tái tạo tiếng Anh + tóm tắt tiếng Việt đủ 7 phần, kéo chi tiết cụ thể + toạ độ (≤25 từ/trục,
                    không dùng "...", bỏ nhận xét lỗi máy `MAY-SAI:` nhưng giữ vật thể thực người đọc chỉ ra).
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path
from typing import Any

import cv2
import numpy as np

THU_MUC_SCRIPTS = Path(__file__).resolve().parent
if str(THU_MUC_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(THU_MUC_SCRIPTS))

import anh_do  # noqa: E402
import anh_doc  # noqa: E402
import rea_core  # noqa: E402

CANH_DAI_CHUAN = 1024
BANG_XAM_R2 = np.array([45, 140, 235], dtype=np.uint8)  # 0: xa (tối), 1: giữa, 2: gần (sáng)
# Mã lớp bố cục phẳng: 0 = chu (45 tối), 1 = hinh (145 giữa), 2 = khoang_trong (235 sáng)
BANG_XAM_BO_CUC = np.array([45, 145, 235], dtype=np.uint8)

# Bảng ánh xạ nhãn từ vựng đóng sang tiếng Anh tự nhiên phục vụ prompt tái tạo
BAN_DICH_EN: dict[str, dict[str, str]] = {
    "chu_the_chinh": {
        "chan_dung_nguoi": "human portrait / single character",
        "nhom_nguoi": "group of people / multi-character ensemble",
        "co_the_ban_tay": "close-up body part / hands",
        "vat_the_dao_cu": "hero prop / key object",
        "khoi_chu_tieu_de": "typographic headline block",
        "hinh_khoi_do_hoa": "abstract geometric graphic forms",
        "kien_truc_khong_gian": "architectural space / perspective interior-exterior",
        "thien_nhien_canh_vat": "natural landscape / scenery",
    },
    "chu_the_phu": {
        "nguoi_phu": "secondary supporting figure",
        "dao_cu_vat_the": "secondary prop / object",
        "khoi_chu_thong_tin": "editorial / informational text block",
        "logo_nhan_hieu": "brand mark / logo element",
        "mang_hinh_trang_tri": "decorative / graphic motif shape",
        "tien_canh_che_mo": "out-of-focus foreground framing element",
        "hau_canh_boi_canh": "contextual background environment",
        "khong_co": "minimalist counterweight (no separate secondary object)",
    },
    "duong_dan_mat": {
        "duong_cheo": "diagonal leading lines",
        "duong_cong_chu_s": "S-curve visual flow",
        "duong_hoi_tu_phoi_canh": "converging perspective lines",
        "khung_trong_khung": "frame-within-a-frame",
        "huong_nhin_nhan_vat": "character eyeline / gaze vector",
        "luong_sang_tia_sang": "light beam / directional illumination path",
        "truc_luoi_chu_do_hoa": "typographic & graphic grid axis",
        "phan_bo_tinh_tam": "centripetal / symmetric center-locked focus",
        "khong_ro": "subtle / diffused eye flow",
    },
    "bo_cuc": {
        "mot_phan_ba": "rule of thirds",
        "cheo": "dynamic diagonal composition",
        "doi_xung": "symmetrical composition",
    },
    "anh_sang_huong": {
        "thuan_truoc": "frontal lighting",
        "chech_trai": "45-degree key light from the left",
        "chech_phai": "45-degree key light from the right",
        "ngang_trai": "low-angle side light grazing from the left",
        "ngang_phai": "low-angle side light grazing from the right",
        "nguoc_sang_vien": "backlighting / rim light silhouette",
        "dinh_chieu_xuong": "overhead top-down lighting",
        "duoi_hat_len": "under-lighting angled upward",
        "toa_deu_do_hoa_phang": "flat even 2D graphic illumination",
    },
    "anh_sang_cung_mem": {
        "cung_gat": "hard light with razor-sharp shadow edges",
        "vua_ro_khoi": "directional semi-soft light sculpting clear 3D form",
        "mem_khuech_tan": "soft diffused lighting with smooth tonal roll-off",
        "phang_khong_bong": "flat shadowless shading",
    },
    "nhiet_mau": {
        "nong_am": "warm golden/amber color temperature",
        "lanh_tram": "cool muted cyan/slate/greenish color temperature",
        "trung_tinh": "neutral balanced color temperature",
        "tuong_phan_nong_lanh": "warm-cool color contrast",
        "don_sac_trang_den": "monochrome / black-and-white palette",
    },
    "chat_lieu": {
        "da_nguoi_tu_nhien": "natural human skin texture",
        "vai_lua_trang_phuc": "fabric & garment folds",
        "kim_loai_kinh_phan_xa": "reflective metal and glass surfaces",
        "go_da_be_tong_tho": "raw concrete, stone, and weathered wood",
        "khoi_suong_nuoc": "atmospheric haze, smoke, and moisture",
        "hat_film_nhieu_anh": "analog film grain / CRT scanline texture",
        "mang_vector_phang": "clean flat digital vector surfaces",
        "giay_in_hat_tram": "matte print paper with halftone raster dots",
        "hon_hop": "mixed tactile contrast (multi-material surfaces)",
    },
    "phong_cach": {
        "dien_anh_kich_tinh": "dramatic narrative cinema / neo-noir still",
        "san_khau_mv": "stylized music video stage production",
        "chan_dung_studio": "controlled studio portrait",
        "doi_thuong_tai_lieu": "documentary / candid realism",
        "do_hoa_hien_dai_thuy_si": "Swiss International Typographic Style graphic design",
        "poster_su_kien_thuong_hieu": "editorial brand / event poster design",
        "toi_gian": "minimalist visual design",
        "sieu_thuc_y_niem": "conceptual surrealist aesthetic",
    },
    "cam_xuc": {
        "kich_tinh_cang_thang": "tense, dramatic, high-stakes mood",
        "lang_dong_u_buon": "melancholic, somber, introspective mood",
        "am_ap_gan_gui": "warm, intimate mood",
        "bi_an_lanh_lung": "mysterious, cold, detached atmosphere",
        "nang_dong_ruc_ro": "energetic, vibrant mood",
        "trang_trong_chuan_muc": "poised, authoritative, refined tone",
        "vui_tuoi_phong_khoang": "playful, expressive tone",
        "tinh_lang_chiem_nghiem": "quiet, contemplative stillness",
    },
    "tong": {
        "high-key": "high-key bright tonal distribution",
        "low-key": "low-key dark tonal distribution",
        "tuong-phan-cao": "high-contrast chiaroscuro tonal range",
        "trung-tinh": "balanced mid-tone luminance",
    },
}

# Từ điển cụm danh từ / tính từ thị giác cụ thể (ưu tiên cụm dài trước) để dịch sang tiếng Anh tự nhiên
CUM_TU_VI_EN: tuple[tuple[str, str], ...] = (
    ("sắc đỏ máu thẫm của đôi môi", "deep crimson red lips"),
    ("đôi môi đỏ rượu sẫm", "dark wine red lips"),
    ("đôi môi đỏ thẫm", "deep red lips"),
    ("đôi môi đỏ sẫm", "dark red lips"),
    ("môi đỏ như máu", "blood red lips"),
    ("môi đỏ thẫm", "deep red lips"),
    ("môi đỏ sẫm", "dark red lips"),
    ("môi đỏ", "red lips"),
    ("môi trên", "upper lip"),
    ("môi dưới bóng", "glossy lower lip"),
    ("môi dưới", "lower lip"),
    ("đôi môi", "lips"),
    ("son môi bóng ướt", "glossy wet lipstick"),
    ("hé mở lộ hàm răng", "slightly parted showing teeth"),
    ("lộ hàm răng", "showing teeth"),
    ("hé mở", "slightly parted"),
    ("đôi mắt kẻ viền đen sắc lạnh", "sharp dark-lined eyes"),
    ("cắt mất đôi mắt", "cropped eyes"),
    ("hốc mắt nhíu đau đớn", "furrowed pained eye sockets"),
    ("đôi mắt", "eyes"),
    ("vết rách rỉ máu trên trán", "bleeding forehead cut"),
    ("vệt máu/bụi trên má", "blood and dust streak on cheek"),
    ("gương mặt bị thương trung tâm", "central wounded face"),
    ("gương mặt nghiêng rất lớn", "large profile face"),
    ("gương mặt nghiêng", "profile face"),
    ("khuôn mặt dưới ám xanh ngọc", "cyan-tinted lower face"),
    ("màu da xanh ngọc/lục lam lạnh lẽo", "cold cyan-green skin tone"),
    ("hóa trang da xanh ma mị", "eerie cyan-painted skin"),
    ("da xanh xác lạnh", "cold pale cyan skin"),
    ("ám xanh ngọc", "cyan-green tinted"),
    ("làn da mịn lạnh", "smooth cold skin"),
    ("khuôn mặt", "face"),
    ("gương mặt", "face"),
    ("người đàn ông đầu trọc", "bald man"),
    ("người đàn ông", "man"),
    ("nam ca sĩ trung tâm", "central male singer"),
    ("nam ca sĩ", "male singer"),
    ("hai nhân vật", "two figures"),
    ("nhân vật đứng", "standing figure"),
    ("nhân vật lao ngang", "lunging figure"),
    ("nhân vật", "character"),
    ("đội hình 5-6 người", "5-6 person ensemble"),
    ("vũ công", "dancers"),
    ("bị còng hai tay", "with handcuffed hands"),
    ("hai tay còng", "handcuffed hands"),
    ("bàn tay đeo nhẫn bạc", "silver-ringed hand"),
    ("mu bàn tay", "back of hand"),
    ("bàn tay", "hand"),
    ("chỏm tóc bạch kim", "platinum hair crown"),
    ("hai lọn tóc xám bạc", "silver-gray hair locks"),
    ("mớ tóc xơ khô", "dry coarse hair strands"),
    ("sợi tóc khô", "dry hair strands"),
    ("chân tóc vàng", "bleached blonde hair roots"),
    ("mảng tóc đen đặc", "dense black hair"),
    ("mặt nạ quỷ hannya/oni hai sừng", "two-horned Hannya/Oni demon mask"),
    ("gương mặt quỷ oni mọc sừng", "horned Oni demon face"),
    ("mặt nạ quỷ oni", "Oni demon mask"),
    ("chiếc nanh quỷ", "demon fang"),
    ("hai sừng", "two horns"),
    ("hàm răng nanh", "fanged teeth"),
    ("ngực áo giao lĩnh trắng chói", "stark white cross-collar robe"),
    ("cổ áo giao lĩnh", "cross-collar robe"),
    ("vạt áo đen", "black coat hem"),
    ("vest kẻ sọc", "pinstriped suit"),
    ("vest trắng đen", "black-and-white suit"),
    ("vest xám rêu rộng", "oversized moss-gray suit"),
    ("áo khoác/lông đen", "black fur/coat"),
    ("áo sơ mi trắng", "white dress shirt"),
    ("cà vạt", "necktie"),
    ("áo tối", "dark robe"),
    ("cổ áo", "collar"),
    ("bàn thẩm vấn trung tâm", "central interrogation table"),
    ("hai ghế gỗ đen", "two black wooden chairs"),
    ("chiếc ghế dài màu đỏ", "red bench"),
    ("chiếc ghế đỏ", "red bench"),
    ("hành lang bê tông dài", "long concrete corridor"),
    ("hành lang bê tông", "concrete corridor"),
    ("hàng cột bê tông", "row of concrete columns"),
    ("bức tường bê tông", "concrete wall"),
    ("bê tông trần thô mộc", "raw exposed concrete"),
    ("nắng chiều chiếu xiên thấp", "low-angle late-afternoon sunlight"),
    ("nắng chiều", "warm afternoon sunlight"),
    ("nguồn sáng xanh lục lạnh", "cold cyan-green light"),
    ("dải đèn flash/slit trắng gắt", "harsh white slit/flash band"),
    ("vệt chớp flash rolling-shutter", "rolling-shutter flash band"),
    ("biên cắt sáng ngang", "razor-sharp horizontal light cut"),
    ("đường cắt sáng ngang", "sharp horizontal light cut"),
    ("đốm phản quang", "specular highlight"),
    ("đốm phản xạ bóng ướt", "wet specular highlight"),
    ("bóng đổ", "cast shadows"),
    ("vệt bóng", "cast shadow"),
    ("đèn pin", "flashlight"),
    ("thanh led xanh", "green LED bar"),
    ("thùng loa", "speaker cabinet"),
    ("xe hơi đỏ", "dark red car"),
    ("thân xe hơi", "car body"),
    ("nóc xe", "car roof"),
    ("tập hồ sơ", "dossier file"),
    ("bức ảnh mugshot kẹp ghim sắt", "paperclipped mugshot photo"),
    ("vân giấy mỹ thuật sần nhẹ màu kem", "lightly textured cream art paper"),
    ("nền giấy kem vàng", "warm cream paper ground"),
    ("nền giấy kem", "cream paper background"),
    ("hộp thông tin nền trắng", "white info card"),
    ("khối chữ tuyên ngôn cỡ lớn màu trắng ngà", "large ivory manifesto headline"),
    ("tiêu đề chính", "main headline"),
    ("lưới chữ thuỵ sĩ", "Swiss typographic grid"),
    ("lưới chữ thụy sĩ", "Swiss typographic grid"),
    ("sọc ngang crt", "horizontal CRT scanlines"),
    ("tiền cảnh phải", "right foreground"),
    ("tiền cảnh trái", "left foreground"),
    ("tiền cảnh", "foreground"),
    ("trung cảnh phải", "right midground"),
    ("trung cảnh", "midground"),
    ("hậu cảnh", "background"),
    ("chính diện", "frontal view"),
    ("góc nghiêng 3/4", "three-quarter profile"),
    ("trực diện ống kính", "facing the camera"),
    ("cắt đôi khung hình", "splitting the frame"),
    ("mảng đen sâu", "deep black expanse"),
    ("trắng lạnh", "stark cool white"),
    ("bóng đen", "deep shadow"),
)

_MAU_TOA_DO_GHI_CHU = re.compile(r"x\s*=\s*(0?\.\d+|1\.0+|0)\s*,\s*y\s*=\s*(0?\.\d+|1\.0+|0)")
_KY_TU_CO_DAU_VI = re.compile(r"[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]", re.IGNORECASE)
_TU_CHUC_NANG_VI = {
    "va", "voi", "cua", "o", "tai", "trong", "tren", "duoi", "sang", "tu", "den", "la", "co",
    "cac", "nhung", "mot", "hai", "ba", "cho", "khi", "nhu", "rat", "cuc", "manh", "nhe",
    "tao", "lam", "bi", "duoc", "theo", "cung", "giua", "ben", "phia", "phan", "vung", "mang",
    "diem", "anh", "khung", "hinh", "toan", "bo", "rieng", "chi", "khong", "ma", "de", "ve",
}


def _cau_hinh_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def _kich_thuoc_1024(kich_thuoc: list[int] | tuple[int, int]) -> tuple[int, int]:
    """Trả về (vw, vh) sao cho cạnh dài đúng bằng 1024."""
    w = max(1, int(kich_thuoc[0])) if len(kich_thuoc) >= 2 else CANH_DAI_CHUAN
    h = max(1, int(kich_thuoc[1])) if len(kich_thuoc) >= 2 else int(round(CANH_DAI_CHUAN * 0.75))
    m = max(w, h)
    ti_le = float(CANH_DAI_CHUAN) / float(m)
    vw = max(1, int(round(w * ti_le)))
    vh = max(1, int(round(h * ti_le)))
    if max(vw, vh) != CANH_DAI_CHUAN:
        if vw >= vh:
            vw = CANH_DAI_CHUAN
        else:
            vh = CANH_DAI_CHUAN
    return vw, vh


def _ve_chu_utf8(
    img_bgr: np.ndarray,
    text: str,
    xy: tuple[int, int],
    co_px: int = 16,
    mau_bgr: tuple[int, int, int] = (30, 30, 30),
) -> np.ndarray:
    """Vẽ chữ tiếng Việt UTF-8 bằng Pillow nếu có font hệ thống; dự phòng về cv2.putText ASCII."""
    try:
        from PIL import Image, ImageDraw, ImageFont  # type: ignore

        ds_font = [
            Path("C:/Windows/Fonts/segoeui.ttf"),
            Path("C:/Windows/Fonts/arial.ttf"),
            Path("C:/Windows/Fonts/tahoma.ttf"),
        ]
        p_font = next((p for p in ds_font if p.is_file()), None)
        if p_font is not None:
            pil_img = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_img)
            font = ImageFont.truetype(str(p_font), co_px)
            mau_rgb = (int(mau_bgr[2]), int(mau_bgr[1]), int(mau_bgr[0]))
            draw.text(xy, text, font=font, fill=mau_rgb)
            return cv2.cvtColor(np.asarray(pil_img), cv2.COLOR_RGB2BGR)
    except Exception:
        pass

    bang_khong_dau = str.maketrans(
        "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
        "ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ",
        "aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd"
        "AAAAAAAAAAAAAAAAAEEEEEEEEEEEIIIIIOOOOOOOOOOOOOOOOOUUUUUUUUUUUYYYYYD",
    )
    ascii_txt = text.translate(bang_khong_dau)
    cv2.putText(
        img_bgr,
        ascii_txt,
        (xy[0], xy[1] + co_px - 3),
        cv2.FONT_HERSHEY_SIMPLEX,
        max(0.42, co_px / 32.0),
        mau_bgr,
        1,
        cv2.LINE_AA,
    )
    return img_bgr


# ---------------- 1A. Bản khối 3 lớp xám + viền Canny (`khoi.png` cho ảnh không phẳng) ---------------

def tao_khoi_png(thu_muc_anh: Path, do_data: dict[str, Any]) -> np.ndarray:
    """Tạo `khoi.png` cho ảnh 3D: 3 lớp xám chuẩn R2 (gần=235 sáng, giữa=140, xa=45 tối) + viền đen mảnh Canny."""
    vw, vh = _kich_thuoc_1024(do_data.get("kich_thuoc") or [1024, 768])
    ds_info = do_data.get("do_sau") or {}
    nguong = ds_info.get("nguong") or [0.3333, 0.6667]
    t1 = float(nguong[0]) if len(nguong) >= 1 else 0.3333
    t2 = float(nguong[1]) if len(nguong) >= 2 else 0.6667

    p_depth = thu_muc_anh / "depth.png"
    p_lop = thu_muc_anh / "lop.png"

    if p_depth.is_file():
        raw = np.frombuffer(p_depth.read_bytes(), dtype=np.uint8)
        depth_u8 = cv2.imdecode(raw, cv2.IMREAD_GRAYSCALE)
        if depth_u8 is None:
            raise ValueError(f"Không đọc được depth.png: {p_depth}")
        dh, dw = depth_u8.shape[:2]
        interp = cv2.INTER_AREA if max(dh, dw) > CANH_DAI_CHUAN else cv2.INTER_LINEAR
        depth_1024 = cv2.resize(depth_u8, (vw, vh), interpolation=interp)
        if max(dh, dw) < CANH_DAI_CHUAN:
            depth_1024 = cv2.GaussianBlur(depth_1024, (5, 5), 1.0)
        d_norm = depth_1024.astype(np.float32) / np.float32(255.0)
        lop = np.where(d_norm >= t2, 2, np.where(d_norm >= t1, 1, 0))
        lop_u8 = BANG_XAM_R2[lop]
    elif p_lop.is_file():
        lop_bgr = anh_do.doc_anh_bgr(p_lop)
        lop_gray = cv2.cvtColor(lop_bgr, cv2.COLOR_BGR2GRAY)
        lop_1024 = cv2.resize(lop_gray, (vw, vh), interpolation=cv2.INTER_NEAREST)
        kc = np.abs(lop_1024[:, :, None].astype(np.int16) - BANG_XAM_R2[None, None, :].astype(np.int16))
        lop_idx = np.argmin(kc, axis=2)
        lop_u8 = BANG_XAM_R2[lop_idx]
    else:
        ti_le = ds_info.get("ti_le") or {"gan": 0.33, "giua": 0.34, "xa": 0.33}
        y_xa = int(round(float(ti_le.get("xa", 0.33)) * vh))
        y_giua = y_xa + int(round(float(ti_le.get("giua", 0.34)) * vh))
        lop_u8 = np.full((vh, vw), 235, dtype=np.uint8)
        lop_u8[:y_xa, :] = 45
        lop_u8[y_xa:y_giua, :] = 140

    vien_canny = cv2.Canny(lop_u8, 50, 150)
    khoi_bgr = cv2.cvtColor(lop_u8, cv2.COLOR_GRAY2BGR)
    khoi_bgr[vien_canny > 0] = (0, 0, 0)
    return khoi_bgr


# ---------------- 1B. Bản khối BỐ CỤC 24×N (`khoi.png` + `bo_cuc.json` cho ảnh phẳng) ----------------

def _tao_mat_na_chu_phang(anh_1024: np.ndarray) -> np.ndarray:
    """Phát hiện vùng nét chữ mảnh & chữ tiêu đề (xét tách riêng chữ tối nền sáng & chữ sáng nền tối + MSER)."""
    vh, vw = anh_1024.shape[:2]
    gray = cv2.cvtColor(anh_1024, cv2.COLOR_BGR2GRAY)
    k_hat = cv2.getStructuringElement(cv2.MORPH_RECT, (29, 29))
    bhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, k_hat)
    that = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, k_hat)
    net_manh = np.maximum(bhat, that)

    canh_lon = float(max(vh, vw))
    h_min = max(5, int(round(0.0045 * canh_lon)))
    h_max = max(h_min + 2, int(round(0.15 * canh_lon)))
    w_max = max(8, int(round(0.45 * canh_lon)))
    k3 = np.ones((3, 3), dtype=np.uint8)

    mask_ky_tu = np.zeros((vh, vw), dtype=np.uint8)
    for che_do, hat_map in (("toi", bhat), ("sang", that)):
        mask_hat = (hat_map >= 48).astype(np.uint8)
        mask_nen_loai = cv2.dilate((hat_map >= 24).astype(np.uint8), k3, iterations=1) > 0
        so_nhan, nhan_cc, thong_ke, _ = cv2.connectedComponentsWithStats(mask_hat, connectivity=8)
        for idx in range(1, so_nhan):
            x0 = int(thong_ke[idx, cv2.CC_STAT_LEFT])
            y0 = int(thong_ke[idx, cv2.CC_STAT_TOP])
            w_cc = int(thong_ke[idx, cv2.CC_STAT_WIDTH])
            h_cc = int(thong_ke[idx, cv2.CC_STAT_HEIGHT])
            dt_cc = int(thong_ke[idx, cv2.CC_STAT_AREA])
            if not (h_min <= h_cc <= h_max and 2 <= w_cc <= w_max and dt_cc >= 5):
                continue
            ti_so = w_cc / float(h_cc)
            do_dac = dt_cc / float(max(1, w_cc * h_cc))
            if not (0.08 <= ti_so <= 9.0 and 0.08 <= do_dac <= 0.88):
                continue
            rx0, ry0 = max(0, x0 - 5), max(0, y0 - 5)
            rx1, ry1 = min(vw, x0 + w_cc + 5), min(vh, y0 + h_cc + 5)
            bg_px = gray[ry0:ry1, rx0:rx1][~mask_nen_loai[ry0:ry1, rx0:rx1]]
            if bg_px.size < 6 or float(bg_px.std()) > 25.0:
                continue
            vung_con = nhan_cc[y0 : y0 + h_cc, x0 : x0 + w_cc] == idx
            fg_px = gray[y0 : y0 + h_cc, x0 : x0 + w_cc][vung_con]
            if fg_px.size == 0:
                continue
            hieu = (float(bg_px.mean()) - float(fg_px.mean())) if che_do == "toi" else (float(fg_px.mean()) - float(bg_px.mean()))
            if hieu >= 38.0:
                mask_ky_tu[y0 : y0 + h_cc, x0 : x0 + w_cc][vung_con] = 255

    # Bổ sung MSER cho chữ cỡ vừa/nhỏ nếu OpenCV hỗ trợ
    if hasattr(cv2, "MSER_create"):
        try:
            mser = cv2.MSER_create(5, 8, int(max(60, 0.004 * vh * vw)))
            _, bboxes = mser.detectRegions(gray)
            if bboxes is not None:
                for bx, by, bw, bh in bboxes:
                    if h_min <= bh <= int(0.10 * canh_lon) and 2 <= bw <= int(0.12 * canh_lon):
                        if 0.12 <= (bw / float(bh)) <= 3.5:
                            roi_hat = net_manh[by : by + bh, bx : bx + bw]
                            if roi_hat.size > 0 and float((roi_hat >= 35).mean()) >= 0.18:
                                mask_ky_tu[by : by + bh, bx : bx + bw] = np.maximum(
                                    mask_ky_tu[by : by + bh, bx : bx + bw],
                                    ((roi_hat >= 35).astype(np.uint8) * 255),
                                )
        except Exception:
            pass

    # Nối ngang nhẹ giữa các ký tự liền kề trong cùng một từ/cụm chữ
    k_noi = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 3))
    return cv2.dilate(mask_ky_tu, k_noi, iterations=1)


def tao_khoi_bo_cuc_phang(
    thu_muc_anh: Path,
    do_data: dict[str, Any],
) -> tuple[np.ndarray, dict[str, Any]]:
    """Chia ảnh phẳng thành lưới `24×N` ô, gán `chu` / `hinh` / `khoang_trong`,
    vẽ `khoi.png` (3 sắc xám + viền + chú giải) và trả kèm dữ liệu `bo_cuc.json`.
    """
    vw, vh = _kich_thuoc_1024(do_data.get("kich_thuoc") or [1024, 768])
    ten_anh = str(do_data.get("anh") or thu_muc_anh.name)
    p_goc = anh_doc.tim_path_anh_goc(thu_muc_anh, ten_anh, thu_muc_anh.parent)

    if p_goc is not None and p_goc.is_file():
        img_goc = anh_do.doc_anh_bgr(p_goc)
        anh_1024 = cv2.resize(
            img_goc,
            (vw, vh),
            interpolation=cv2.INTER_AREA if max(img_goc.shape[:2]) > CANH_DAI_CHUAN else cv2.INTER_LINEAR,
        )
    elif (thu_muc_anh / "do.png").is_file():
        anh_1024 = cv2.resize(anh_do.doc_anh_bgr(thu_muc_anh / "do.png"), (vw, vh), interpolation=cv2.INTER_LINEAR)
    else:
        anh_1024 = np.full((vh, vw, 3), 235, dtype=np.uint8)

    so_cot = 24
    so_hang = max(12, int(round(float(so_cot) * float(vh) / float(vw))))

    # Màu nền chủ đạo lấy từ màu số 1 trong bảng k-means (hoặc trung vị viền ảnh nếu thiếu)
    ds_mau = do_data.get("mau") or []
    if ds_mau and isinstance(ds_mau[0].get("hex"), str):
        nen_bgr = np.array(anh_do._hex_sang_bgr(ds_mau[0]["hex"]), dtype=np.float32)
    else:
        vien_px = np.concatenate([anh_1024[:8, :].reshape(-1, 3), anh_1024[-8:, :].reshape(-1, 3)], axis=0)
        nen_bgr = np.median(vien_px, axis=0).astype(np.float32)

    mask_chu = _tao_mat_na_chu_phang(anh_1024)
    gray = cv2.cvtColor(anh_1024, cv2.COLOR_BGR2GRAY)
    canny = cv2.Canny(gray, 60, 160)
    sobel_y = np.abs(cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3))

    # Phân loại từng ô lưới: 0 = chu, 1 = hinh, 2 = khoang_trong
    luoi_nhan = np.full((so_hang, so_cot), 2, dtype=np.uint8)
    ys_bien = np.linspace(0, vh, so_hang + 1, dtype=int)
    xs_bien = np.linspace(0, vw, so_cot + 1, dtype=int)

    for r in range(so_hang):
        y0, y1 = int(ys_bien[r]), int(ys_bien[r + 1])
        for c in range(so_cot):
            x0, x1 = int(xs_bien[c]), int(xs_bien[c + 1])
            o_bgr = anh_1024[y0:y1, x0:x1].astype(np.float32)
            o_chu = mask_chu[y0:y1, x0:x1] > 0
            o_canny = canny[y0:y1, x0:x1] > 0
            o_sy = sobel_y[y0:y1, x0:x1]

            mat_do_chu = float(o_chu.mean())
            mat_do_canh = float(o_canny.mean())
            canh_ngang = float((o_sy >= 48.0).mean())

            tb_bgr = o_bgr.mean(axis=(0, 1))
            lech_nen = float(np.max(np.abs(tb_bgr - nen_bgr)))
            do_lech_o = float(o_bgr.std(axis=(0, 1)).max())

            # Nếu ô là mảng đặc đồng nhất lệch xa màu nền (hình khối màu đặc) mà không có nét mảnh bên trong -> `hinh`
            la_mang_mau_dac = lech_nen >= 24.0 and do_lech_o < 12.0 and mat_do_canh < 0.04
            if (not la_mang_mau_dac) and (
                mat_do_chu >= 0.075 or (mat_do_chu >= 0.035 and mat_do_canh >= 0.045 and canh_ngang >= 0.04)
            ):
                luoi_nhan[r, c] = 0  # chu
            elif lech_nen >= 13.5 or do_lech_o >= 11.0 or mat_do_canh >= 0.028:
                luoi_nhan[r, c] = 1  # hinh
            else:
                luoi_nhan[r, c] = 2  # khoang_trong

    tong_o = float(so_hang * so_cot)
    tl_chu = round(float((luoi_nhan == 0).sum()) / tong_o, 4)
    tl_hinh = round(float((luoi_nhan == 1).sum()) / tong_o, 4)
    tl_trong = round(max(0.0, 1.0 - tl_chu - tl_hinh), 4)

    # Trích các hộp khối chữ lớn bằng gom cụm liên thông trên mặt nạ ô `chu` (nối ngang 1 ô kề)
    mat_na_o_chu = (luoi_nhan == 0).astype(np.uint8)
    mat_na_gom = cv2.dilate(mat_na_o_chu, np.ones((1, 2), dtype=np.uint8), iterations=1)
    so_cum, nhan_cum, tk_cum, _ = cv2.connectedComponentsWithStats(mat_na_gom, connectivity=8)

    ds_hop_chu: list[tuple[float, list[float]]] = []
    for idx_c in range(1, so_cum):
        mask_c = (nhan_cum == idx_c) & (luoi_nhan == 0)
        rs, cs = np.nonzero(mask_c)
        if rs.size == 0:
            continue
        r0, r1 = int(rs.min()), int(rs.max()) + 1
        c0, c1 = int(cs.min()), int(cs.max()) + 1
        so_o_thuc = int(rs.size)
        if so_o_thuc < 2 and int((luoi_nhan == 0).sum()) >= 4:
            continue
        hop = [
            round(c0 / float(so_cot), 4),
            round(r0 / float(so_hang), 4),
            round(c1 / float(so_cot), 4),
            round(r1 / float(so_hang), 4),
        ]
        dt_hop = (hop[2] - hop[0]) * (hop[3] - hop[1])
        ds_hop_chu.append((dt_hop, hop))

    ds_hop_chu.sort(key=lambda x: -x[0])
    khoi_chu_lon = [hop for _, hop in ds_hop_chu[:8]]

    # Vẽ ảnh `khoi.png` cho bố cục phẳng (cạnh dài đúng 1024)
    khoi_xam = np.full((vh, vw), 235, dtype=np.uint8)
    for r in range(so_hang):
        y0, y1 = int(ys_bien[r]), int(ys_bien[r + 1])
        for c in range(so_cot):
            x0, x1 = int(xs_bien[c]), int(xs_bien[c + 1])
            khoi_xam[y0:y1, x0:x1] = BANG_XAM_BO_CUC[int(luoi_nhan[r, c])]

    khoi_bgr = cv2.cvtColor(khoi_xam, cv2.COLOR_GRAY2BGR)

    # Kẻ lưới ô mờ nhạt + viền đen đậm giữa các miền khác nhãn
    for xv in xs_bien[1:-1]:
        cv2.line(khoi_bgr, (int(xv), 0), (int(xv), vh - 1), (208, 208, 208), 1)
    for yv in ys_bien[1:-1]:
        cv2.line(khoi_bgr, (0, int(yv)), (vw - 1, int(yv)), (208, 208, 208), 1)

    for r in range(so_hang):
        y0, y1 = int(ys_bien[r]), int(ys_bien[r + 1])
        for c in range(so_cot):
            x0, x1 = int(xs_bien[c]), int(xs_bien[c + 1])
            nh = int(luoi_nhan[r, c])
            if c + 1 < so_cot and int(luoi_nhan[r, c + 1]) != nh:
                cv2.line(khoi_bgr, (x1, y0), (x1, y1), (15, 15, 15), 2)
            if r + 1 < so_hang and int(luoi_nhan[r + 1, c]) != nh:
                cv2.line(khoi_bgr, (x0, y1), (x1, y1), (15, 15, 15), 2)

    # Thanh chú giải rõ ràng ở góc trên
    cao_cg = 34
    cv2.rectangle(khoi_bgr, (0, 0), (vw - 1, cao_cg), (28, 30, 34), -1)
    x_sw = 10
    for muc_xam, nhan_sw in (
        (45, f"chữ: {tl_chu * 100:.1f}%"),
        (145, f"hình: {tl_hinh * 100:.1f}%"),
        (235, f"khoảng trống: {tl_trong * 100:.1f}%"),
    ):
        cv2.rectangle(khoi_bgr, (x_sw, 9), (x_sw + 16, 25), (muc_xam, muc_xam, muc_xam), -1)
        cv2.rectangle(khoi_bgr, (x_sw, 9), (x_sw + 16, 25), (210, 210, 210), 1)
        khoi_bgr = _ve_chu_utf8(khoi_bgr, nhan_sw, (x_sw + 22, 7), co_px=15, mau_bgr=(245, 245, 245))
        x_sw += 175 if "khoảng" not in nhan_sw else 235

    if vw >= 680:
        khoi_bgr = _ve_chu_utf8(
            khoi_bgr,
            f"lưới {so_cot}×{so_hang}",
            (vw - 125, 7),
            co_px=15,
            mau_bgr=(195, 205, 220),
        )
    cv2.rectangle(khoi_bgr, (0, 0), (vw - 1, vh - 1), (40, 40, 40), 1)

    bo_cuc_json = {
        "anh": ten_anh,
        "luoi": [int(so_cot), int(so_hang)],
        "ti_le": {
            "chu": tl_chu,
            "hinh": tl_hinh,
            "khoang_trong": tl_trong,
        },
        "khoi_chu_lon": khoi_chu_lon,
    }
    return khoi_bgr, bo_cuc_json


# ---------------- 2. Khung bố cục & đường dẫn mắt (`khung.png`) --------------------------------------

def _tam_o_luoi(ma_o: str) -> tuple[float, float] | None:
    s = ma_o.strip().upper()
    if len(s) != 2 or s[0] not in "ABC" or s[1] not in "123":
        return None
    r = "ABC".index(s[0])
    c = "123".index(s[1])
    return ((c + 0.5) / 3.0, (r + 0.5) / 3.0)


def _tam_moc(moc: Any) -> tuple[float, float] | None:
    if moc is None:
        return None
    if isinstance(moc, str):
        s = moc.strip().upper()
        if "-" in s:
            a, b = s.split("-", 1)
            pa, pb = _tam_o_luoi(a), _tam_o_luoi(b)
            if pa and pb:
                return (0.5 * (pa[0] + pb[0]), 0.5 * (pa[1] + pb[1]))
        return _tam_o_luoi(s)
    if isinstance(moc, dict):
        if "x" in moc and "y" in moc:
            return (float(moc["x"]), float(moc["y"]))
        if "hop" in moc and isinstance(moc["hop"], (list, tuple)) and len(moc["hop"]) == 4:
            x0, y0, x1, y1 = [float(v) for v in moc["hop"]]
            return (0.5 * (x0 + x1), 0.5 * (y0 + y1))
        if "vung" in moc:
            return _tam_moc(moc["vung"])
        if "luoi" in moc:
            return _tam_moc(moc["luoi"])
        if "xy" in moc and isinstance(moc["xy"], (list, tuple)) and len(moc["xy"]) == 2:
            return (float(moc["xy"][0]), float(moc["xy"][1]))
    if isinstance(moc, (list, tuple)):
        if len(moc) == 2 and all(isinstance(v, (int, float)) for v in moc):
            return (float(moc[0]), float(moc[1]))
        if len(moc) == 4 and all(isinstance(v, (int, float)) for v in moc):
            return (0.5 * (float(moc[0]) + float(moc[2])), 0.5 * (float(moc[1]) + float(moc[3])))
        pts = [_tam_moc(m) for m in moc]
        pts = [p for p in pts if p is not None]
        if pts:
            return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
    return None


def _ve_mui_ten_cat_dau(
    canvas: np.ndarray,
    p0: tuple[int, int],
    p1: tuple[int, int],
    mau_bgr: tuple[int, int, int],
    do_day: int = 2,
    cat_dau: float = 0.0,
    cat_cuoi: float = 0.0,
) -> None:
    dx = float(p1[0] - p0[0])
    dy = float(p1[1] - p0[1])
    do_dai = math.hypot(dx, dy)
    if do_dai <= max(6.0, cat_dau + cat_cuoi + 4.0):
        return
    ux, uy = dx / do_dai, dy / do_dai
    sx = int(round(p0[0] + ux * cat_dau))
    sy = int(round(p0[1] + uy * cat_dau))
    ex = int(round(p1[0] - ux * cat_cuoi))
    ey = int(round(p1[1] - uy * cat_cuoi))
    seg_len = max(1.0, math.hypot(ex - sx, ey - sy))
    tip = min(0.32, max(0.06, 14.0 / seg_len))
    cv2.arrowedLine(canvas, (sx, sy), (ex, ey), mau_bgr, do_day, cv2.LINE_AA, tipLength=tip)


def _ve_hop_net_dut(
    canvas: np.ndarray,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    mau_bgr: tuple[int, int, int],
    buoc: int = 10,
) -> None:
    for xa in range(x0, x1, buoc * 2):
        cv2.line(canvas, (xa, y0), (min(x1, xa + buoc), y0), mau_bgr, 1, cv2.LINE_AA)
        cv2.line(canvas, (xa, y1), (min(x1, xa + buoc), y1), mau_bgr, 1, cv2.LINE_AA)
    for ya in range(y0, y1, buoc * 2):
        cv2.line(canvas, (x0, ya), (x0, min(y1, ya + buoc)), mau_bgr, 1, cv2.LINE_AA)
        cv2.line(canvas, (x1, ya), (x1, min(y1, ya + buoc)), mau_bgr, 1, cv2.LINE_AA)


def _trich_duong_nguoi_doc(
    muc_ddm: dict[str, Any],
    tam_chu_the: tuple[float, float] | None,
) -> tuple[list[tuple[float, float]], tuple[float, float, float, float] | None]:
    """Trích chuỗi điểm mũi tên (chuẩn hoá 0..1) và hộp vùng (nếu có) từ mục `duong_dan_mat`."""
    moc = muc_ddm.get("moc")
    hop_vung: tuple[float, float, float, float] | None = None

    if isinstance(moc, (list, tuple)) and len(moc) >= 2 and not all(isinstance(v, (int, float)) for v in moc):
        pts = [_tam_moc(m) for m in moc]
        pts_sach = [p for p in pts if p is not None]
        if len(pts_sach) >= 2:
            return pts_sach, None

    if isinstance(moc, str) and "-" in moc:
        trai, phai = moc.strip().upper().split("-", 1)
        pa, pb = _tam_o_luoi(trai), _tam_o_luoi(phai)
        if pa and pb and pa != pb:
            return [pa, pb], None
    if isinstance(moc, dict) and isinstance(moc.get("vung"), str) and "-" in moc["vung"]:
        trai, phai = moc["vung"].strip().upper().split("-", 1)
        pa, pb = _tam_o_luoi(trai), _tam_o_luoi(phai)
        if pa and pb and pa != pb:
            return [pa, pb], None

    if isinstance(moc, dict) and "hop" in moc and isinstance(moc["hop"], (list, tuple)) and len(moc["hop"]) == 4:
        x0, y0, x1, y1 = [float(v) for v in moc["hop"]]
        hop_vung = (x0, y0, x1, y1)
    elif isinstance(moc, (list, tuple)) and len(moc) == 4 and all(isinstance(v, (int, float)) for v in moc):
        x0, y0, x1, y1 = [float(v) for v in moc]
        hop_vung = (x0, y0, x1, y1)

    ghi_chu = loc_mo_ta_khoi_may_sai(str(muc_ddm.get("ghi_chu") or ""))
    ds_xy_gc: list[tuple[float, float]] = []
    for m in _MAU_TOA_DO_GHI_CHU.finditer(ghi_chu):
        px, py = float(m.group(1)), float(m.group(2))
        if 0.0 <= px <= 1.0 and 0.0 <= py <= 1.0:
            if not ds_xy_gc or math.hypot(px - ds_xy_gc[-1][0], py - ds_xy_gc[-1][1]) >= 0.08:
                ds_xy_gc.append((px, py))
    if len(ds_xy_gc) >= 2:
        if len(ds_xy_gc) > 4:
            ds_xy_gc = [ds_xy_gc[0], ds_xy_gc[len(ds_xy_gc) // 2], ds_xy_gc[-1]]
        return ds_xy_gc, hop_vung

    if hop_vung is not None:
        x0, y0, x1, y1 = hop_vung
        dich = tam_chu_the if tam_chu_the is not None else (0.5 * (x0 + x1), 0.5 * (y0 + y1))
        cac_goc = [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]
        goc_xa = max(cac_goc, key=lambda g: math.hypot(g[0] - dich[0], g[1] - dich[1]))
        if math.hypot(goc_xa[0] - dich[0], goc_xa[1] - dich[1]) >= 0.05:
            return [goc_xa, dich], hop_vung
        return [(x0, y0), (x1, y1)], hop_vung

    tam = _tam_moc(moc)
    if tam is not None:
        if tam_chu_the is not None and math.hypot(tam[0] - tam_chu_the[0], tam[1] - tam_chu_the[1]) >= 0.08:
            return [tam, tam_chu_the], None
        goc_xuat = (0.5, 0.5) if math.hypot(tam[0] - 0.5, tam[1] - 0.5) >= 0.12 else (0.18, 0.18)
        return [goc_xuat, tam], None

    return [], None


def tao_khung_png(do_data: dict[str, Any], doc_data: dict[str, Any] | None) -> np.ndarray:
    """Tạo `khung.png`: nền xám sáng, lưới 1/3, 2 đường chéo mảnh, điểm hút mắt đánh số + mũi tên đường dẫn mắt."""
    vw, vh = _kich_thuoc_1024(do_data.get("kich_thuoc") or [1024, 768])
    canvas = np.full((vh, vw, 3), (245, 246, 248), dtype=np.uint8)

    mau_luoi = (195, 198, 204)
    mau_cheo = (212, 210, 202)
    mau_may = (205, 88, 22)        # BGR xanh cô-ban đậm (#1658cd)
    mau_nguoi = (36, 66, 222)      # BGR đỏ cam (#de4224)
    mau_hop_nguoi = (120, 140, 232)

    cv2.line(canvas, (0, 0), (vw - 1, vh - 1), mau_cheo, 1, cv2.LINE_AA)
    cv2.line(canvas, (0, vh - 1), (vw - 1, 0), mau_cheo, 1, cv2.LINE_AA)

    x1, x2 = vw // 3, (2 * vw) // 3
    y1, y2 = vh // 3, (2 * vh) // 3
    for xv in (x1, x2):
        cv2.line(canvas, (xv, 0), (xv, vh - 1), mau_luoi, 1, cv2.LINE_AA)
    for yv in (y1, y2):
        cv2.line(canvas, (0, yv), (vw - 1, yv), mau_luoi, 1, cv2.LINE_AA)
    for gx in (x1, x2):
        for gy in (y1, y2):
            cv2.circle(canvas, (gx, gy), 3, (170, 175, 182), -1, cv2.LINE_AA)

    xs_o = (0, x1, x2)
    ys_o = (0, y1, y2)
    for r_idx, ch_h in enumerate("ABC"):
        for c_idx, ch_c in enumerate("123"):
            ty_o = ys_o[r_idx] + (46 if r_idx == 0 else 18)
            cv2.putText(
                canvas,
                f"{ch_h}{ch_c}",
                (xs_o[c_idx] + 8, ty_o),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.42,
                (178, 180, 185),
                1,
                cv2.LINE_AA,
            )

    co_duong_nguoi_doc = False
    ban_truc_doc: dict[str, dict[str, Any]] = {}
    if isinstance(doc_data, dict):
        ds_tl = (doc_data.get("doc") or {}).get("tra_loi") or []
        ban_truc_doc = {str(t.get("ma")): t for t in ds_tl if isinstance(t, dict) and t.get("ma")}

    muc_ddm = ban_truc_doc.get("duong_dan_mat")
    if muc_ddm and rea_core.kiem_tra_moc(muc_ddm.get("moc"), loai="anh"):
        muc_ctc = ban_truc_doc.get("chu_the_chinh")
        tam_ctc = _tam_moc(muc_ctc.get("moc")) if muc_ctc else None
        pts_nd, hop_nd = _trich_duong_nguoi_doc(muc_ddm, tam_ctc)
        if hop_nd is not None:
            hx0 = int(round(hop_nd[0] * (vw - 1)))
            hy0 = int(round(hop_nd[1] * (vh - 1)))
            hx1 = int(round(hop_nd[2] * (vw - 1)))
            hy1 = int(round(hop_nd[3] * (vh - 1)))
            _ve_hop_net_dut(canvas, hx0, hy0, hx1, hy1, mau_hop_nguoi, buoc=10)
            co_duong_nguoi_doc = True
        if len(pts_nd) >= 2:
            px_pts = [(int(round(px * (vw - 1))), int(round(py * (vh - 1)))) for px, py in pts_nd]
            for i in range(len(px_pts) - 1):
                _ve_mui_ten_cat_dau(canvas, px_pts[i], px_pts[i + 1], mau_nguoi, do_day=3, cat_dau=4.0, cat_cuoi=6.0)
            cv2.circle(canvas, px_pts[0], 5, mau_nguoi, -1, cv2.LINE_AA)
            cv2.circle(canvas, px_pts[-1], 7, mau_nguoi, 2, cv2.LINE_AA)
            co_duong_nguoi_doc = True

    ds_hm = sorted(
        do_data.get("hut_mat") or [],
        key=lambda p: -float(p.get("diem", 0.0)),
    )
    px_hm = [
        (int(round(float(p["x"]) * (vw - 1))), int(round(float(p["y"]) * (vh - 1))), float(p.get("diem", 0.0)))
        for p in ds_hm
    ]
    ban_kinh_hm = 17
    for i in range(len(px_hm) - 1):
        p_tu = (px_hm[i][0], px_hm[i][1])
        p_den = (px_hm[i + 1][0], px_hm[i + 1][1])
        _ve_mui_ten_cat_dau(
            canvas,
            p_tu,
            p_den,
            mau_may,
            do_day=2,
            cat_dau=float(ban_kinh_hm + 2),
            cat_cuoi=float(ban_kinh_hm + 3),
        )

    for idx, (px, py, diem) in enumerate(px_hm, start=1):
        cv2.circle(canvas, (px, py), ban_kinh_hm, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(canvas, (px, py), ban_kinh_hm, mau_may, 2, cv2.LINE_AA)
        chu_so = str(idx)
        (tw, th), _ = cv2.getTextSize(chu_so, cv2.FONT_HERSHEY_DUPLEX, 0.62, 2)
        cv2.putText(
            canvas,
            chu_so,
            (px - tw // 2, py + th // 2),
            cv2.FONT_HERSHEY_DUPLEX,
            0.62,
            mau_may,
            2,
            cv2.LINE_AA,
        )
        nhan_diem = f"{diem:.2f}"
        tx = px + ban_kinh_hm + 5 if px + ban_kinh_hm + 48 < vw else max(6, px - ban_kinh_hm - 44)
        ty = py + 5 if py > 44 else py + 22
        cv2.putText(canvas, nhan_diem, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (60, 65, 75), 1, cv2.LINE_AA)

    cao_chu_giai = 32
    cv2.rectangle(canvas, (0, 0), (vw - 1, cao_chu_giai), (235, 237, 240), -1)
    cv2.line(canvas, (0, cao_chu_giai), (vw - 1, cao_chu_giai), (195, 198, 204), 1)

    cv2.arrowedLine(canvas, (14, 16), (44, 16), mau_may, 2, cv2.LINE_AA, tipLength=0.32)
    canvas = _ve_chu_utf8(canvas, "máy (hút mắt giảm dần)", (52, 6), co_px=15, mau_bgr=mau_may)

    x_nd = 258
    cv2.arrowedLine(canvas, (x_nd, 16), (x_nd + 30, 16), mau_nguoi, 2, cv2.LINE_AA, tipLength=0.32)
    nhan_nd = (
        f"người đọc ({muc_ddm.get('gia_tri', 'duong_dan_mat')})"
        if co_duong_nguoi_doc and muc_ddm
        else "người đọc (chưa có mốc duong_dan_mat)"
    )
    canvas = _ve_chu_utf8(canvas, nhan_nd, (x_nd + 38, 6), co_px=15, mau_bgr=mau_nguoi)

    cv2.rectangle(canvas, (0, 0), (vw - 1, vh - 1), (175, 178, 184), 1)
    return canvas


# ---------------- 3. Sinh `prompt.md` tái tạo (kéo chi tiết cụ thể từ `dap_an`, ≤25 từ) ---------------

def _dich_nhan(truc: str, gia_tri: str | None) -> str:
    if not gia_tri:
        return "chưa đọc"
    return BAN_DICH_EN.get(truc, {}).get(gia_tri, gia_tri)


def loc_mo_ta_khoi_may_sai(ghi_chu: str) -> str:
    """Loại bỏ phần nhận xét lỗi máy (`MAY-SAI: ...`), chỉ giữ lại vật thể/hiện tượng thực của ảnh
    mà người đọc chỉ ra bên trong ghi chú.
    """
    s = re.sub(r"\s+", " ", (ghi_chu or "").strip())
    if not s:
        return ""
    s = s.replace("...", " ").replace("…", " ")

    if re.match(r"^MAY-SAI\s*:", s, flags=re.IGNORECASE):
        s = re.sub(r"^MAY-SAI\s*:\s*", "", s, flags=re.IGNORECASE)
        s = re.sub(r"^\[[A-Z]{2,4}-\d{2}\]\s*", "", s)

        # Ưu tiên câu bắt đầu bằng "Chủ thể (chính) thực sự là" hoặc "Thực tế" / "trong khi thực tế"
        cac_moc_thuc_te = (
            r"chủ thể chính thực sự là\s+",
            r"chủ thể thực sự là\s+",
            r"trong khi thực tế\s+",
            r"thực tế\s+",
        )
        da_tach = False
        for mau in cac_moc_thuc_te:
            m_tt = re.search(mau, s, flags=re.IGNORECASE)
            if m_tt:
                s = s[m_tt.end() :].strip()
                da_tach = True
                break

        if not da_tach:
            # Tách theo các cụm chuyển hướng từ lỗi máy sang vật thể thật bị bỏ sót
            cac_moc_vat_the = (
                r"thay vì chủ thể chính là\s+",
                r"thay vì đặt\s*#\d+\s*vào\s+",
                r"thay vì\s+",
                r"bỏ sót chủ thể thực sự là\s+",
                r"bỏ sót chủ thể chính là\s+",
                r"bỏ sót hoàn toàn\s+",
                r"bỏ sót\s+",
                r"trượt khỏi tiêu điểm biểu cảm thật của chân dung là\s+",
                r"đều trượt khỏi\s+",
                r"trượt khỏi\s+",
                r"đẩy\s+",
            )
            for mau in cac_moc_vat_the:
                m_vt = re.search(mau, s, flags=re.IGNORECASE)
                if m_vt:
                    s = s[m_vt.end() :].strip()
                    break

    # Gọt sạch các mệnh đề bình luận lỗi thuật toán/máy còn sót ở cuối câu và mã luật [XX-00]
    s = re.sub(r"\[[A-Z]{2,4}-\d{2}\]\s*", "", s)
    s = re.sub(r":\s*máy đặt\s*#\d+.*$", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s+do\s+(?:thuật toán|máy|thiên vị|thiên kiến|trọng số|sắc độ xe tối bị).*$", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s+xuống vị trí\s*#\d+\s*(?:\([^)]*\))?", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s+chỉ xếp\s*#\d+\b", "", s, flags=re.IGNORECASE)
    s = re.sub(r"^Không có chủ thể phụ tách rời\s*;\s*(?:yếu tố\s+)?", "", s, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", s).strip(" ,;:-")


def _can_bang_ngoac(s: str) -> str:
    """Đảm bảo không để ngoặc đơn mở dở cuối câu sau khi rút gọn số từ."""
    mo = s.count("(")
    dong = s.count(")")
    if mo > dong:
        vi_tri = s.rfind("(")
        if vi_tri > 0:
            s = s[:vi_tri].rstrip(" ,;:-")
        else:
            s = s + (")" * (mo - dong))
    return s.strip(" ,;:-.")


def rut_gon_so_tu(van_ban: str, toi_da_tu: int = 25) -> str:
    """Rút gọn chuỗi còn tối đa `toi_da_tu` từ, ưu tiên ngắt ở dấu câu tự nhiên, TUYỆT ĐỐI không dùng '...'."""
    sach = re.sub(r"\s+", " ", (van_ban or "").replace("...", " ").replace("…", " ")).strip(" ,;:-.")
    if not sach:
        return ""
    ds_tu = sach.split(" ")
    if len(ds_tu) <= toi_da_tu:
        return _can_bang_ngoac(sach)

    cat_tho = " ".join(ds_tu[:toi_da_tu])
    # Nếu trong khoảng 14..toi_da_tu từ có dấu ngắt mệnh đề tự nhiên (; hoặc . hoặc —) thì ngắt gọn tại đó
    ung_vien_ngat = []
    for dau in (". ", "; ", " — ", ", "):
        pos = cat_tho.rfind(dau)
        if pos > 0:
            so_tu_truoc = len(cat_tho[:pos].split())
            if so_tu_truoc >= max(12, toi_da_tu - 9):
                ung_vien_ngat.append((dau != ", ", pos))
    if ung_vien_ngat:
        ung_vien_ngat.sort(key=lambda x: (x[0], x[1]), reverse=True)
        cat_tho = cat_tho[: ung_vien_ngat[0][1]]

    cat_tho = _can_bang_ngoac(cat_tho)
    tu_ket_lung = {
        "và", "với", "của", "ở", "tại", "trong", "trên", "dưới", "từ", "đến", "là", "có", "các", "những", "một",
        "and", "with", "of", "at", "in", "on", "from", "to", "the", "a", "an", "by", "for",
    }
    ds_cuoi = cat_tho.split()
    while len(ds_cuoi) > 6 and ds_cuoi[-1].lower().strip(".,;:()[]") in tu_ket_lung:
        ds_cuoi.pop()
    return _can_bang_ngoac(" ".join(ds_cuoi))


def _bo_dau_viet(s: str) -> str:
    bang = str.maketrans(
        "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
        "ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ",
        "aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd"
        "AAAAAAAAAAAAAAAAAEEEEEEEEEEEIIIIIOOOOOOOOOOOOOOOOOUUUUUUUUUUUYYYYYD",
    )
    return s.translate(bang)


def dich_chi_tiet_sang_en(ghi_chu: str, toi_da_tu: int = 25) -> str:
    """Dịch các cụm danh từ cụ thể + toạ độ/mã màu/trích dẫn từ `ghi_chu` tiếng Việt sang tiếng Anh (≤25 từ)."""
    goc = loc_mo_ta_khoi_may_sai(ghi_chu)
    if not goc:
        return ""

    # Bảo toàn trích dẫn '...' (chuyển sang không dấu nếu có dấu tiếng Việt để câu tiếng Anh liền mạch)
    trich_dan_luu: list[str] = []

    def _giu_trich_dan(m: re.Match[str]) -> str:
        nd = _bo_dau_viet(m.group(1).strip())
        idx = len(trich_dan_luu)
        trich_dan_luu.append(f"'{nd}'")
        return f" __QUOTE{idx}__ "

    ban = re.sub(r"'([^']{1,60})'", _giu_trich_dan, goc)

    # Chuẩn hoá tiền tố toạ độ/hộp sang tiếng Anh
    ban = re.sub(r"\bở\s+(?=x\s*=|y\s*=|hop\s*=)", "at ", ban, flags=re.IGNORECASE)
    ban = re.sub(r"\btại\s+(?=x\s*=|y\s*=|hop\s*=)", "at ", ban, flags=re.IGNORECASE)
    ban = re.sub(r"\bô\s+([ABC][123](?:-[ABC][123])?)\b", r"grid \1", ban)
    ban = re.sub(r"\bhop\s*=\s*\[", "box [", ban, flags=re.IGNORECASE)

    # Áp dụng bảng dịch cụm danh từ cụ thể (từ dài đến ngắn)
    for vi_cum, en_cum in CUM_TU_VI_EN:
        ban = re.sub(re.escape(vi_cum), f" {en_cum} ", ban, flags=re.IGNORECASE)

    # Lọc bỏ các từ tiếng Việt còn sót (có dấu hoặc từ hư tiếng Việt), giữ lại cụm Anh, số đo, toạ độ, mã #hex
    ds_token_sach: list[str] = []
    for tok in re.split(r"\s+", ban):
        t = tok.strip()
        if not t:
            continue
        if t.startswith("__QUOTE") and t.endswith("__"):
            ds_token_sach.append(t)
            continue
        if _KY_TU_CO_DAU_VI.search(t):
            continue
        t_loi = t.strip(".,;:()[]/").lower()
        if not t_loi:
            continue
        if t_loi in _TU_CHUC_NANG_VI:
            continue
        ds_token_sach.append(t)

    ket_qua = " ".join(ds_token_sach)
    for idx, q_val in enumerate(trich_dan_luu):
        ket_qua = ket_qua.replace(f"__QUOTE{idx}__", q_val)

    # Dọn dấu câu thừa do lược từ hư tiếng Việt
    ket_qua = re.sub(r"\(\s*\)", "", ket_qua)
    ket_qua = re.sub(r"\(\s*[,;:]+\s*", "(", ket_qua)
    ket_qua = re.sub(r"\s*[,;:]+\s*\)", ")", ket_qua)
    ket_qua = re.sub(r"(?:[,;]\s*){2,}", ", ", ket_qua)
    ket_qua = re.sub(r"\s+", " ", ket_qua).strip(" ,;:-.")
    return rut_gon_so_tu(ket_qua, toi_da_tu=toi_da_tu)


def tom_chi_tiet_vi(ghi_chu: str, toi_da_tu: int = 25) -> str:
    """Lấy chi tiết tiếng Việt sạch (đã bỏ `MAY-SAI:`), rút gọn ≤25 từ, không dùng '...'."""
    goc = loc_mo_ta_khoi_may_sai(ghi_chu)
    if not goc:
        return ""
    # Chuẩn hoá cụm "sắc đỏ ... của đôi môi" -> nhắc rõ "đôi môi đỏ ..." để giữ cụm danh từ trực tiếp
    goc = re.sub(
        r"sắc đỏ máu thẫm của đôi môi",
        "đôi môi đỏ máu thẫm",
        goc,
        flags=re.IGNORECASE,
    )
    return rut_gon_so_tu(goc, toi_da_tu=toi_da_tu)


def _lay_truc(ban_truc: dict[str, dict[str, Any]], ma: str) -> dict[str, Any] | None:
    muc = ban_truc.get(ma)
    if not muc:
        return None
    gt = str(muc.get("gia_tri") or "").strip()
    if not gt:
        return None
    return muc


def _gan_chi_tiet_en(nhan_en: str, ghi_chu: str, toi_da_tu: int = 22) -> str:
    ct_en = dich_chi_tiet_sang_en(ghi_chu, toi_da_tu=toi_da_tu)
    if ct_en:
        return f"{nhan_en} ({ct_en})"
    return nhan_en


def _gan_chi_tiet_vi(nhan_vi: str, ghi_chu: str, toi_da_tu: int = 25) -> str:
    ct_vi = tom_chi_tiet_vi(ghi_chu, toi_da_tu=toi_da_tu)
    if ct_vi:
        return f"{nhan_vi} — {ct_vi}"
    return nhan_vi


_MAU_MA_LUAT_TRONG_GHI_CHU = re.compile(r"\[([A-Z]{2,4}-\d{2})\]")


def _trich_danh_sach_ma_luat(doc_data: dict[str, Any] | None) -> list[str]:
    if not isinstance(doc_data, dict):
        return []
    phan_doc = doc_data.get("doc") if isinstance(doc_data.get("doc"), dict) else {}
    ds_luat_khop = doc_data.get("luat_khop")
    if not isinstance(ds_luat_khop, list):
        ds_luat_khop = phan_doc.get("luat_khop")

    ket_qua: list[str] = []
    da_thay: set[str] = set()
    if isinstance(ds_luat_khop, list):
        for lk in ds_luat_khop:
            if isinstance(lk, dict):
                ma = str(lk.get("ma") or "").strip()
                if ma and ma not in da_thay:
                    da_thay.add(ma)
                    ket_qua.append(ma)

    for tl in phan_doc.get("tra_loi") or []:
        if isinstance(tl, dict):
            gc = str(tl.get("ghi_chu") or "")
            for m in _MAU_MA_LUAT_TRONG_GHI_CHU.finditer(gc):
                ma = m.group(1).strip()
                if ma and ma not in da_thay:
                    da_thay.add(ma)
                    ket_qua.append(ma)
    return ket_qua


def tao_prompt_md(
    do_data: dict[str, Any],
    doc_data: dict[str, Any] | None,
    bo_cuc_phang: dict[str, Any] | None = None,
) -> str:
    """Sinh `prompt.md` gồm prompt tái tạo tiếng Anh + tóm tắt tiếng Việt đủ 7 mục; trục thiếu ghi 'chưa đọc'."""
    ten_anh = str(do_data.get("anh") or "khong_ro")
    kt = do_data.get("kich_thuoc") or [0, 0]
    bc = do_data.get("bo_cuc") or {}
    khop_nhat = str(bc.get("khop_nhat") or "mot_phan_ba")
    diem_bc = float(bc.get(khop_nhat, 0.0)) if khop_nhat in bc else 0.0

    ds_info = do_data.get("do_sau") or {}
    la_phang = bool(ds_info.get("phang", False))
    tl_ds = ds_info.get("ti_le") or {}
    xa_pct = float(tl_ds.get("xa", 0.0)) * 100.0
    giua_pct = float(tl_ds.get("giua", 0.0)) * 100.0
    gan_pct = float(tl_ds.get("gan", 0.0)) * 100.0

    ds_hm = do_data.get("hut_mat") or []
    o_co_hm = {rea_core.xy_sang_luoi(float(p["x"]), float(p["y"])) for p in ds_hm}
    tat_ca_o = [f"{r}{c}" for r in "ABC" for c in "123"]
    o_it_hm = [o for o in tat_ca_o if o not in o_co_hm]
    ti_le_o_trong = (len(o_it_hm) / 9.0) * 100.0

    if la_phang and bo_cuc_phang and isinstance(bo_cuc_phang.get("ti_le"), dict):
        tl_bc = bo_cuc_phang["ti_le"]
        chu_pct = float(tl_bc.get("chu", 0.0)) * 100.0
        hinh_pct = float(tl_bc.get("hinh", 0.0)) * 100.0
        trong_pct = float(tl_bc.get("khoang_trong", 0.0)) * 100.0
        neg_pct = round(trong_pct, 1)
    else:
        chu_pct = hinh_pct = trong_pct = 0.0
        neg_pct = xa_pct if xa_pct >= 12.0 else round(0.5 * xa_pct + 0.5 * ti_le_o_trong, 1)

    tong = do_data.get("tong") or {}
    kieu_tong = str(tong.get("kieu") or "trung-tinh")
    tb_sang = float(tong.get("trung_binh", 0.0))

    ds_mau = do_data.get("mau") or []
    chuoi_palette_en = ", ".join(f"{m['hex']} ({float(m['ti_le']) * 100:.1f}%)" for m in ds_mau) or "chưa đọc"
    chuoi_palette_vi = ", ".join(f"`{m['hex']}` ({float(m['ti_le']) * 100:.0f}%)" for m in ds_mau) or "chưa đọc"

    ban_truc: dict[str, dict[str, Any]] = {}
    if isinstance(doc_data, dict):
        for t in (doc_data.get("doc") or {}).get("tra_loi") or []:
            if isinstance(t, dict) and t.get("ma"):
                ban_truc[str(t["ma"])] = t

    m_ctc = _lay_truc(ban_truc, "chu_the_chinh")
    m_ctp = _lay_truc(ban_truc, "chu_the_phu")
    m_ddm = _lay_truc(ban_truc, "duong_dan_mat")
    m_ash = _lay_truc(ban_truc, "anh_sang_huong")
    m_asc = _lay_truc(ban_truc, "anh_sang_cung_mem")
    m_nm = _lay_truc(ban_truc, "nhiet_mau")
    m_cl = _lay_truc(ban_truc, "chat_lieu")
    m_pc = _lay_truc(ban_truc, "phong_cach")
    m_cx = _lay_truc(ban_truc, "cam_xuc")

    # 1. Subject (lấy cả ghi_chu đã lọc MAY-SAI + toạ độ, ≤25 từ)
    if m_ctc:
        o_ctc = str(m_ctc.get("vung_luoi") or rea_core.moc_sang_vung_luoi(m_ctc.get("moc")) or "?")
        moc_ctc_str = rea_core.dinh_dang_moc(m_ctc.get("moc"))
        ct_ctc_en = dich_chi_tiet_sang_en(m_ctc.get("ghi_chu", ""), toi_da_tu=22)
        sub_main_en = f"{_dich_nhan('chu_the_chinh', m_ctc['gia_tri'])} at grid {o_ctc} ({moc_ctc_str})"
        if ct_ctc_en:
            sub_main_en = f"{sub_main_en}: {ct_ctc_en}"
        sub_main_vi = _gan_chi_tiet_vi(f"`{m_ctc['gia_tri']}` (ô `{o_ctc}`, {moc_ctc_str})", m_ctc.get("ghi_chu", ""))
    else:
        o_ctc = "chưa đọc"
        sub_main_en = "chưa đọc"
        sub_main_vi = "chưa đọc"

    if m_ctp:
        o_ctp = str(m_ctp.get("vung_luoi") or rea_core.moc_sang_vung_luoi(m_ctp.get("moc")) or "?")
        moc_ctp_str = rea_core.dinh_dang_moc(m_ctp.get("moc"))
        ct_ctp_en = dich_chi_tiet_sang_en(m_ctp.get("ghi_chu", ""), toi_da_tu=20)
        sub_sec_en = f"{_dich_nhan('chu_the_phu', m_ctp['gia_tri'])} at grid {o_ctp} ({moc_ctp_str})"
        if ct_ctp_en:
            sub_sec_en = f"{sub_sec_en}: {ct_ctp_en}"
        sub_sec_vi = _gan_chi_tiet_vi(f"`{m_ctp['gia_tri']}` (ô `{o_ctp}`, {moc_ctp_str})", m_ctp.get("ghi_chu", ""))
    else:
        sub_sec_en = "chưa đọc"
        sub_sec_vi = "chưa đọc"

    ddm_en = _gan_chi_tiet_en(_dich_nhan("duong_dan_mat", m_ddm["gia_tri"]), m_ddm.get("ghi_chu", ""), 18) if m_ddm else "chưa đọc"
    ddm_vi = (
        _gan_chi_tiet_vi(f"`{m_ddm['gia_tri']}` ({rea_core.dinh_dang_moc(m_ddm.get('moc'))})", m_ddm.get("ghi_chu", ""))
        if m_ddm
        else "chưa đọc"
    )

    # 2. Lighting (kéo chi tiết ghi_chu từ anh_sang_huong, anh_sang_cung_mem, nhiet_mau)
    ash_en = _gan_chi_tiet_en(_dich_nhan("anh_sang_huong", m_ash["gia_tri"]), m_ash.get("ghi_chu", ""), 20) if m_ash else "chưa đọc"
    asc_en = _gan_chi_tiet_en(_dich_nhan("anh_sang_cung_mem", m_asc["gia_tri"]), m_asc.get("ghi_chu", ""), 18) if m_asc else "chưa đọc"
    nm_en = _gan_chi_tiet_en(_dich_nhan("nhiet_mau", m_nm["gia_tri"]), m_nm.get("ghi_chu", ""), 18) if m_nm else "chưa đọc"

    ash_vi = (
        _gan_chi_tiet_vi(f"`{m_ash['gia_tri']}` ({rea_core.dinh_dang_moc(m_ash.get('moc'))})", m_ash.get("ghi_chu", ""))
        if m_ash
        else "chưa đọc"
    )
    asc_vi = _gan_chi_tiet_vi(f"`{m_asc['gia_tri']}`", m_asc.get("ghi_chu", "")) if m_asc else "chưa đọc"
    nm_vi = _gan_chi_tiet_vi(f"`{m_nm['gia_tri']}`", m_nm.get("ghi_chu", "")) if m_nm else "chưa đọc"

    # 3. Material/Texture (kéo chi tiết ghi_chu từ chat_lieu)
    cl_en = _gan_chi_tiet_en(_dich_nhan("chat_lieu", m_cl["gia_tri"]), m_cl.get("ghi_chu", ""), 22) if m_cl else "chưa đọc"
    cl_vi = (
        _gan_chi_tiet_vi(f"`{m_cl['gia_tri']}` ({rea_core.dinh_dang_moc(m_cl.get('moc'))})", m_cl.get("ghi_chu", ""))
        if m_cl
        else "chưa đọc"
    )

    # 4. Style & Mood (kéo chi tiết ghi_chu từ phong_cach và cam_xuc)
    pc_en = _gan_chi_tiet_en(_dich_nhan("phong_cach", m_pc["gia_tri"]), m_pc.get("ghi_chu", ""), 22) if m_pc else "chưa đọc"
    cx_en = _gan_chi_tiet_en(_dich_nhan("cam_xuc", m_cx["gia_tri"]), m_cx.get("ghi_chu", ""), 18) if m_cx else "chưa đọc"
    pc_vi = _gan_chi_tiet_vi(f"`{m_pc['gia_tri']}`", m_pc.get("ghi_chu", "")) if m_pc else "chưa đọc"
    cx_vi = _gan_chi_tiet_vi(f"`{m_cx['gia_tri']}`", m_cx.get("ghi_chu", "")) if m_cx else "chưa đọc"

    bo_cuc_en = _dich_nhan("bo_cuc", khop_nhat)
    tong_en = _dich_nhan("tong", kieu_tong)
    chuoi_o_it_hm = ", ".join(o_it_hm) if o_it_hm else "không có"

    if la_phang and bo_cuc_phang:
        comp_phan_sau_en = (
            f"flat 2D graphic layout (`bo_cuc.json`: text `chu` {chu_pct:.1f}%, "
            f"graphic/image `hinh` {hinh_pct:.1f}%, whitespace `khoang_trong` {trong_pct:.1f}%; "
            f"low-saliency grid cells: {chuoi_o_it_hm})"
        )
        comp_phan_sau_vi = (
            f"bố cục ảnh phẳng (`bo_cuc.json`): chữ `chu` **{chu_pct:.1f}%**, "
            f"hình `hinh` **{hinh_pct:.1f}%**, khoảng trống `khoang_trong` **{trong_pct:.1f}%** "
            f"(các ô ít hút mắt: `{chuoi_o_it_hm}`)"
        )
        ref_control_en = "dùng khoi.png làm bản khối bố cục phẳng (chữ/hình/khoảng trống), khung.png làm bố cục"
    else:
        comp_phan_sau_en = (
            f"negative space / breathing room ~{neg_pct:.1f}% "
            f"(far depth layer: {xa_pct:.1f}%, mid: {giua_pct:.1f}%, near: {gan_pct:.1f}%; "
            f"low-saliency grid cells: {chuoi_o_it_hm})"
        )
        comp_phan_sau_vi = (
            f"khoảng thở / negative space: **{neg_pct:.1f}%** "
            f"(lớp xa `do_sau.ti_le.xa` = {xa_pct:.1f}%, các ô ít hút mắt: `{chuoi_o_it_hm}`)"
        )
        ref_control_en = "dùng khoi.png làm ControlNet depth, khung.png làm bố cục"

    ds_ma_luat = _trich_danh_sach_ma_luat(doc_data)
    chuoi_luat_en = ", ".join(ds_ma_luat) if ds_ma_luat else "none"
    chuoi_luat_vi = ", ".join(f"`{m}`" for m in ds_ma_luat) if ds_ma_luat else "chưa ghi nhận"

    dong = [
        f"# Prompt tái tạo (`ve-nguoc`): `{ten_anh}`",
        "",
        "## 1. Reconstruction Prompt (English)",
        "",
        f"- **Subject**: Primary subject: {sub_main_en}. Secondary / counterweight element: {sub_sec_en}.",
        (
            f"- **Composition**: {bo_cuc_en} (`{khop_nhat}`, fit score {diem_bc:.2f}), aspect ratio {kt[0]}x{kt[1]}; "
            f"primary subject grid zone: `{o_ctc}`; eye-flow mechanism: {ddm_en}; "
            f"{comp_phan_sau_en}."
        ),
        (
            f"- **Lighting**: Direction: {ash_en}; shadow quality: {asc_en}; "
            f"color temperature: {nm_en}; measured tonal key: {tong_en} (`{kieu_tong}`, mean luminance {tb_sang:.2f})."
        ),
        f"- **Palette**: 6 dominant colors — {chuoi_palette_en}.",
        f"- **Material/Texture**: {cl_en}.",
        f"- **Style**: {pc_en}; mood: {cx_en}.",
        f"- **Reference**: Source `{ten_anh}` — {ref_control_en}.",
        f"- **Rules applied**: {chuoi_luat_en}.",
        "",
        "### Consolidated Generation Prompt",
        (
            f"> {pc_en}, {sub_main_en}, balanced by {sub_sec_en}. "
            f"{bo_cuc_en} with {ddm_en}; {comp_phan_sau_en}. "
            f"Lighting: {ash_en}, {asc_en}, {nm_en}, {tong_en} (mean {tb_sang:.2f}). "
            f"Surface texture: {cl_en}. Mood: {cx_en}. "
            f"Strict color palette: {chuoi_palette_en}. "
            f"Rules applied: {chuoi_luat_en}. "
            f"(Conditioning: {ref_control_en})."
        ),
        "",
        "---",
        "",
        "## 2. Tóm tắt tiếng Việt",
        "",
        f"- **Subject (Chủ thể)**: Chính: {sub_main_vi} | Phụ: {sub_sec_vi}",
        (
            f"- **Composition (Bố cục)**: Khớp nhất `{khop_nhat}` ({diem_bc:.2f}); "
            f"vị trí chủ thể theo ô lưới: `{o_ctc}`; đường dẫn mắt: {ddm_vi}; "
            f"{comp_phan_sau_vi}."
        ),
        (
            f"- **Lighting (Ánh sáng)**: Hướng: {ash_vi} | Cứng/mềm: {asc_vi} | "
            f"Nhiệt màu: {nm_vi} | Tông máy đo: `{kieu_tong}` (TB {tb_sang:.2f})."
        ),
        f"- **Palette (Bảng màu 6 hex + tỉ lệ)**: {chuoi_palette_vi}.",
        f"- **Material/Texture (Chất liệu)**: {cl_vi}",
        f"- **Style (Phong cách & cảm xúc)**: Phong cách: {pc_vi} | Cảm xúc: {cx_vi}",
        f"- **Reference (Tham chiếu)**: Ảnh gốc `{ten_anh}` — {ref_control_en}.",
        f"- **Luật DoP khớp (`Rules applied`)**: {chuoi_luat_vi}.",
        "",
    ]
    return "\n".join(dong)


# ---------------- Điều phối vẽ ngược -----------------------------------------------------------------

def ve_nguoc_mot_anh(thu_muc_anh: str | Path) -> dict[str, Path]:
    """Chạy vẽ ngược cho 1 thư mục ảnh (có `do.json`) -> `<anh>/ve-nguoc/{khoi.png, khung.png, prompt.md[, bo_cuc.json]}`."""
    p_anh = Path(thu_muc_anh)
    p_do = p_anh / "do.json"
    if not p_do.is_file():
        raise FileNotFoundError(f"Không tìm thấy do.json trong thư mục ảnh: {p_anh}")

    do_data = rea_core.doc_json(p_do)
    p_doc = p_anh / "doc.json"
    doc_data = rea_core.doc_json(p_doc) if p_doc.is_file() else None

    out_dir = p_anh / "ve-nguoc"
    out_dir.mkdir(parents=True, exist_ok=True)

    p_khoi = out_dir / "khoi.png"
    p_khung = out_dir / "khung.png"
    p_prompt = out_dir / "prompt.md"
    p_bo_cuc = out_dir / "bo_cuc.json"

    la_phang = bool((do_data.get("do_sau") or {}).get("phang", False))
    bo_cuc_phang: dict[str, Any] | None = None

    if la_phang:
        khoi_img, bo_cuc_phang = tao_khoi_bo_cuc_phang(p_anh, do_data)
        anh_do.ghi_anh(p_khoi, khoi_img)
        rea_core.ghi_json(p_bo_cuc, bo_cuc_phang)
    else:
        if p_bo_cuc.is_file():
            p_bo_cuc.unlink()
        anh_do.ghi_anh(p_khoi, tao_khoi_png(p_anh, do_data))

    anh_do.ghi_anh(p_khung, tao_khung_png(do_data, doc_data))
    p_prompt.write_text(tao_prompt_md(do_data, doc_data, bo_cuc_phang=bo_cuc_phang), encoding="utf-8")

    ket_qua = {"khoi": p_khoi, "khung": p_khung, "prompt": p_prompt}
    if la_phang:
        ket_qua["bo_cuc"] = p_bo_cuc
    return ket_qua


def chay_ve_nguoc(duong_dan: str | Path) -> list[dict[str, Path]]:
    """Hỗ trợ cả `<thu_muc_anh>` đơn lẻ lẫn `<dir_ra>` chứa nhiều thư mục ảnh."""
    goc = Path(duong_dan)
    ds_do = rea_core.tim_ban_do(goc)
    if not ds_do:
        raise FileNotFoundError(f"Không tìm thấy do.json nào tại: {goc}")
    return [ve_nguoc_mot_anh(p_do.parent) for p_do in ds_do]


def tao_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ve_nguoc.py", description="Vẽ ngược bản khối, khung bố cục và prompt tái tạo.")
    p.add_argument("thu_muc_anh", help="Thư mục ảnh chứa do.json (hoặc thư mục cha chứa nhiều ảnh).")
    return p


def main(argv: list[str] | None = None) -> int:
    _cau_hinh_utf8()
    args = tao_parser().parse_args(argv)
    ket_qua = chay_ve_nguoc(args.thu_muc_anh)
    print(f"Đã vẽ ngược cho {len(ket_qua)} ảnh.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
