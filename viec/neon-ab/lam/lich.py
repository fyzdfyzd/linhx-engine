from datetime import date, datetime, timedelta
import re
import unicodedata

BUOI_MAC_DINH = {"sang": 8, "trua": 12, "chieu": 14, "toi": 19}


def _bo_dau(chuoi: str) -> str:
    s = unicodedata.normalize("NFD", chuoi.lower()).replace("đ", "d")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return " ".join(s.split())


def doc_gio(chuoi: str, goc: datetime) -> datetime:
    if not isinstance(chuoi, str):
        raise ValueError("Chuỗi không hợp lệ")
    s = _bo_dau(chuoi)
    if not s:
        raise ValueError("Chuỗi rỗng")

    m_rel = re.fullmatch(r"(\d+)\s+(tieng|phut)\s+nua", s)
    if m_rel:
        so = int(m_rel.group(1))
        return goc + (timedelta(hours=so) if m_rel.group(2) == "tieng" else timedelta(minutes=so))

    gio = phut = buoi = ngay = None

    m_time = re.search(r"\b(\d+)\s*(?::(\d+)|(?:h|gio)(?:\s*(\d+))?)\b", s)
    if m_time:
        gio = int(m_time.group(1))
        phut = int(m_time.group(2) or m_time.group(3) or 0)
        if not (0 <= gio <= 23 and 0 <= phut <= 59):
            raise ValueError("Giờ không hợp lệ")
        s = (s[:m_time.start()] + " " + s[m_time.end():]).strip()

    m_buoi = re.search(r"\b(sang|trua|chieu|toi)\b", s)
    if m_buoi:
        buoi = m_buoi.group(1)
        s = (s[:m_buoi.start()] + " " + s[m_buoi.end():]).strip()

    m_dm = re.search(r"\b(\d{1,2})/(\d{1,2})\b", s)
    m_thu = re.search(r"\bthu\s+(\d+)\b", s)
    m_cn = re.search(r"\bchu\s+nhat\b", s)
    m_rel_day = re.search(r"\b(ngay\s+kia|(?:ngay\s+)?mai|(?:hom\s+)?nay)\b", s)

    if m_dm:
        d, m = int(m_dm.group(1)), int(m_dm.group(2))
        ngay = date(goc.year, m, d)
        if ngay < goc.date():
            ngay = date(goc.year + 1, m, d)
        s = (s[:m_dm.start()] + " " + s[m_dm.end():]).strip()
    elif m_thu:
        thu = int(m_thu.group(1))
        if not (2 <= thu <= 7):
            raise ValueError("Thứ không hợp lệ")
        delta = (thu - 2 - goc.weekday()) % 7 or 7
        ngay = goc.date() + timedelta(days=delta)
        s = (s[:m_thu.start()] + " " + s[m_thu.end():]).strip()
    elif m_cn:
        delta = (6 - goc.weekday()) % 7 or 7
        ngay = goc.date() + timedelta(days=delta)
        s = (s[:m_cn.start()] + " " + s[m_cn.end():]).strip()
    elif m_rel_day:
        tu = " ".join(m_rel_day.group(1).split())
        offset = 2 if tu == "ngay kia" else (1 if "mai" in tu else 0)
        ngay = goc.date() + timedelta(days=offset)
        s = (s[:m_rel_day.start()] + " " + s[m_rel_day.end():]).strip()

    if s or (gio is None and buoi is None and ngay is None):
        raise ValueError("Không hiểu câu hẹn giờ")

    if gio is not None:
        if buoi in ("chieu", "toi") and gio < 12:
            gio += 12
    elif buoi is not None:
        gio, phut = BUOI_MAC_DINH[buoi], 0
    else:
        gio, phut = 9, 0

    if ngay is not None:
        return datetime(ngay.year, ngay.month, ngay.day, gio, phut)

    ket_qua = datetime(goc.year, goc.month, goc.day, gio, phut)
    return ket_qua if ket_qua > goc else ket_qua + timedelta(days=1)
