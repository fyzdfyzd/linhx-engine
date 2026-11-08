"""Chuẩn hoá dữ liệu tiếng Việt (LAB033, linhx-du-lieu v0.1).

Mỗi hàm chuẩn hoá trả về (giá_trị_mới, cờ). Cờ là chuỗi rỗng nếu ổn,
ngược lại là lý do cần người duyệt. Không hàm nào bịa giá trị: khi không
chắc, giữ nguyên giá trị cũ và gắn cờ.
"""
import re
import unicodedata

# ---------- Văn bản chung ----------

MOJIBAKE_HINTS = ("Ã", "Ä", "Æ", "á»", "áº", "Ä‘", "Æ°", "â€")
VIET_CHARS = set(
    "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
)


def la_rong(v):
    return v is None or (isinstance(v, float) and v != v) or str(v).strip() == ""


def nfc(v):
    if la_rong(v):
        return v, ""
    s = str(v)
    n = unicodedata.normalize("NFC", s)
    return n, ""


def trim(v):
    if la_rong(v):
        return v, ""
    s = re.sub(r"\s+", " ", str(v).replace(" ", " ")).strip()
    return s, ""


def co_mojibake(s):
    return any(h in s for h in MOJIBAKE_HINTS)


def fix_mojibake(v):
    if la_rong(v):
        return v, ""
    s = str(v)
    if not co_mojibake(s):
        return s, ""
    for enc in ("cp1252", "latin-1"):
        try:
            t = s.encode(enc).decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
        if not co_mojibake(t):
            return unicodedata.normalize("NFC", t), ""
    return s, "nghi lỗi mã (mojibake) nhưng không tự sửa được"


# Ký tự không bao giờ có trong văn bản tiếng Việt Unicode nhưng rất hay gặp trong TCVN3/VNI đọc sai
TCVN3_STRICT = set("¨©ª«¬®µ¶·¸¹»¼½¾×÷¢£¤¥¦§")
HOA_LATIN1 = set("ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝÆÇÐÑÞß")


def nghi_tcvn3(s):
    """True nếu chuỗi trông như TCVN3/VNI bị đọc sai (ví dụ 'NguyÔn V¨n An')."""
    if la_rong(s):
        return False
    s = str(s)
    strict = sum(1 for c in s if c in TCVN3_STRICT)
    giua_tu = sum(1 for a, b in zip(s, s[1:]) if a.islower() and b in HOA_LATIN1)
    if co_mojibake(s):
        return False  # để fix_mojibake xử lý, tránh gắn cờ hai lần
    return strict >= 1 and strict + giua_tu >= 2 or strict >= 3


def flag_tcvn3(v):
    if nghi_tcvn3(v):
        return v, "nghi bảng mã cũ TCVN3/VNI, cần chuyển mã bằng công cụ (Unikey Toolkit) rồi chạy lại"
    return v, ""


def bo_dau(s):
    s = unicodedata.normalize("NFD", str(s))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D")


def co_dau(s):
    return any(c in VIET_CHARS for c in str(s).lower())


def khoa_ten(s):
    """Khoá so khớp: bỏ dấu, chữ thường, gộp khoảng trắng."""
    if la_rong(s):
        return ""
    return re.sub(r"\s+", " ", bo_dau(s).lower()).strip()


# ---------- Số điện thoại ----------

# Đổi đầu số 11 → 10 số (15/9/2018 – 30/6/2019). Nguồn: LuatVietnam, xem refs/THI-TRUONG-VIET-NAM.md
DAU_SO_CU = {
    "0162": "032", "0163": "033", "0164": "034", "0165": "035", "0166": "036",
    "0167": "037", "0168": "038", "0169": "039",
    "0123": "083", "0124": "084", "0125": "085", "0127": "081", "0129": "082",
    "0120": "070", "0121": "079", "0122": "077", "0126": "076", "0128": "078",
    "0186": "056", "0188": "058", "0199": "059",
}
RE_DI_DONG = re.compile(r"^0[35789]\d{8}$")
RE_CO_DINH = re.compile(r"^02\d{9}$")


def chi_so(s):
    return re.sub(r"\D", "", str(s))


def phone_vn(v):
    if la_rong(v):
        return v, ""
    raw = str(v).strip()
    if raw.endswith(".0"):  # Excel đọc thành số thực
        raw = raw[:-2]
    if re.search(r"[/;,]|\s{2,}| - ", raw) and len(chi_so(raw)) > 11:
        return v, "nhiều số trong một ô, cần tách"
    d = chi_so(raw)
    if d.startswith("84") and len(d) in (11, 12):
        d = "0" + d[2:]
    elif len(d) in (9, 10) and not d.startswith("0") and d[0] in "35789" and len(d) == 9:
        d = "0" + d  # mất số 0 đầu do Excel
    elif len(d) == 10 and d.startswith("1"):
        d = "0" + d  # 1xx… 11 số mất số 0
    if len(d) == 11 and d[:4] in DAU_SO_CU:
        d = DAU_SO_CU[d[:4]] + d[4:]
        return d, ""
    if RE_DI_DONG.match(d) or RE_CO_DINH.match(d):
        return d, ""
    return v, "SĐT không hợp lệ"


def phone_hop_le(v):
    return not la_rong(v) and (RE_DI_DONG.match(str(v)) or RE_CO_DINH.match(str(v))) is not None


def phone_cu(v):
    d = chi_so(v)
    if d.startswith("84"):
        d = "0" + d[2:]
    return len(d) == 11 and d[:4] in DAU_SO_CU


# ---------- Email ----------

RE_EMAIL = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")


def email(v):
    if la_rong(v):
        return v, ""
    s = str(v).strip().lower().replace(" ", "")
    if RE_EMAIL.match(s):
        return s, ""
    return v, "email không hợp lệ"


# ---------- Ngày ----------

RE_NGAY = [
    (re.compile(r"^(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})$"), "dmy"),
    (re.compile(r"^(\d{4})[/\-.](\d{1,2})[/\-.](\d{1,2})(?:[ T].*)?$"), "ymd"),
    (re.compile(r"^(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{2})$"), "dmy2"),
]


def date_vn(v):
    """Về dạng ISO yyyy-mm-dd. Mặc định ngày trước tháng (kiểu Việt Nam)."""
    if la_rong(v):
        return v, ""
    s = str(v).strip()
    for rx, kieu in RE_NGAY:
        m = rx.match(s)
        if not m:
            continue
        a, b, c = (int(x) for x in m.groups())
        if kieu == "ymd":
            y, mo, d = a, b, c
        elif kieu == "dmy":
            d, mo, y = a, b, c
        else:
            d, mo, y = a, b, 2000 + c if c < 50 else 1900 + c
        if not (1 <= mo <= 12 and 1 <= d <= 31 and 1900 <= y <= 2100):
            if kieu != "ymd" and 1 <= d <= 12 and 1 <= mo <= 31:
                return v, "ngày có vẻ theo kiểu tháng/ngày, cần duyệt"
            return v, "ngày không hợp lệ"
        return f"{y:04d}-{mo:02d}-{d:02d}", ""
    return v, "không đọc được ngày"


# ---------- Giấy tờ ----------

def cccd(v):
    """CCCD 12 số. CMND 9 số đã hết giá trị từ 1/1/2025: giữ nguyên và gắn cờ."""
    if la_rong(v):
        return v, ""
    s = str(v).strip()
    if s.endswith(".0"):
        s = s[:-2]
    d = chi_so(s)
    if len(d) == 12:
        return d, ""
    if len(d) == 11:
        # 3 số đầu CCCD là mã tỉnh 001–096 nên luôn bắt đầu bằng 0: thêm lại an toàn
        return "0" + d, ""
    if len(d) == 9:
        return d, "CMND 9 số cũ, cần cập nhật CCCD"
    if len(d) == 8:
        return "0" + d, "CMND 9 số cũ (đã thêm số 0 đầu), cần cập nhật CCCD"
    return v, "số giấy tờ không hợp lệ"


def mst(v):
    """MST doanh nghiệp 10 số hoặc 10-3. Từ 1/7/2025 MST cá nhân là số định danh 12 số."""
    if la_rong(v):
        return v, ""
    s = str(v).strip()
    if s.endswith(".0"):
        s = s[:-2]
    d = chi_so(s)
    if len(d) == 10:
        return d, ""
    if len(d) == 13:
        return d[:10] + "-" + d[10:], ""
    if len(d) == 12:
        return d, ""
    if len(d) == 9:
        return "0" + d, "đã thêm số 0 đầu bị Excel làm mất, cần duyệt"
    return v, "MST không hợp lệ"


# ---------- Tên ----------

DANH_XUNG = ("anh ", "chị ", "chi ", "em ", "cô ", "chú ", "bác ", "a. ", "c. ", "mr ", "mr. ", "ms ", "ms. ", "mrs ", "mrs. ")


def name_vn(v):
    """Gộp khoảng trắng, viết hoa chữ đầu mỗi từ. Không tự xoá danh xưng (vì "Anh" có thể là tên)."""
    if la_rong(v):
        return v, ""
    s = re.sub(r"\s+", " ", unicodedata.normalize("NFC", str(v))).strip()
    s2 = " ".join(w[:1].upper() + w[1:].lower() for w in s.split(" "))
    co = []
    low = s.lower()
    if any(low.startswith(p) for p in DANH_XUNG) and len(s.split()) >= 3:
        co.append("có thể có danh xưng ở đầu")
    if not co_dau(s) and len(s.split()) >= 2:
        co.append("tên không dấu")
    if re.search(r"\d", s):
        co.append("tên có chữ số")
    return s2, "; ".join(co)


CONG_TY = [
    (r"^(c\.?ty|cty|cong ty|công ty)\s+(tnhh|trách nhiệm hữu hạn)\b", "Công ty TNHH"),
    (r"^(ctcp|c\.?ty\s*cp|cty\s*cp|cong ty cp|công ty cp|công ty cổ phần|cong ty co phan)\b", "Công ty Cổ phần"),
    (r"^(c\.?ty|cty|cong ty)\b", "Công ty"),
    (r"^(dntn|doanh nghiệp tư nhân)\b", "Doanh nghiệp tư nhân"),
]


def company_vn(v):
    if la_rong(v):
        return v, ""
    s = re.sub(r"\s+", " ", unicodedata.normalize("NFC", str(v))).strip()
    for pat, thay in CONG_TY:
        m = re.match(pat, s, flags=re.I)
        if m:
            s = thay + s[m.end():]
            break
    co = "" if co_dau(s) else "tên công ty không dấu"
    return s, co


# ---------- Địa chỉ ----------

_convert = None


def _lay_convert():
    global _convert
    if _convert is None:
        try:
            from underthesea import convert_address  # Apache-2.0, có dữ liệu 63→34 tỉnh
            _convert = convert_address
        except Exception:
            _convert = False
    return _convert


def address_new(v):
    """Đổi địa chỉ 3 cấp cũ sang 2 cấp mới (từ 1/7/2025). Trả (mới, cờ).

    Cần `pip install underthesea`. Xã bị chia tách (DIVIDED), không tìm thấy,
    địa chỉ không dấu: giữ nguyên và gắn cờ cho người duyệt.
    """
    if la_rong(v):
        return v, ""
    conv = _lay_convert()
    if not conv:
        return v, "chưa cài underthesea, chưa đổi địa chỉ"
    s = str(v).strip()
    try:
        r = conv(s)
    except Exception as e:  # dữ liệu lạ không làm hỏng cả lô
        return v, f"lỗi đổi địa chỉ: {e}"
    st = getattr(r.status, "name", str(r.status))
    mt = getattr(r.mapping_type, "name", str(r.mapping_type)) if r.mapping_type else ""
    if st == "SUCCESS":
        if mt == "DIVIDED":
            return v, "xã cũ bị chia tách, cần số nhà/toạ độ để chọn xã mới"
        return r.converted, ""
    if st == "PARTIAL":
        tail = "; địa chỉ không dấu" if not co_dau(s) else ""
        return v, f"chỉ khớp tỉnh ({r.converted}), không khớp xã{tail}"
    tail = ", địa chỉ không dấu: cần khôi phục dấu rồi chạy lại" if not co_dau(s) else ""
    return v, "không nhận ra tỉnh" + tail


RE_CAP_HUYEN = re.compile(r"\b(quận|huyện|thị xã|q\.|h\.|quan|huyen)\s*\S", re.I)


def dia_chi_cu(v):
    """True nếu địa chỉ còn cấp quận/huyện (định dạng trước 1/7/2025)."""
    return not la_rong(v) and RE_CAP_HUYEN.search(str(v)) is not None


OPS = {
    "nfc": nfc,
    "trim": trim,
    "fix_mojibake": fix_mojibake,
    "flag_tcvn3": flag_tcvn3,
    "phone_vn": phone_vn,
    "email": email,
    "date_vn": date_vn,
    "cccd": cccd,
    "mst": mst,
    "name_vn": name_vn,
    "company_vn": company_vn,
    "address_new": address_new,
}
