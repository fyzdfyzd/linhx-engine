"""Phân tích chuỗi hẹn giờ tiếng Việt sang đối tượng datetime."""

from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime, timedelta

# Giờ mặc định cho từng buổi trong ngày
PERIOD_DEFAULTS: dict[str, tuple[int, int]] = {
    "sang": (8, 0),
    "trua": (12, 0),
    "chieu": (14, 0),
    "toi": (19, 0),
}

DEFAULT_TIME: tuple[int, int] = (9, 0)

# Biểu thức chính quy cho các thành phần thời gian
RELATIVE_PATTERN = re.compile(
    r"^(?:(\d+)\s*(?:tieng|gio)\s+(\d+)\s*phut"
    r"|(\d+)\s*(tieng|gio|phut))\s+nua$"
)
DATE_PATTERN = re.compile(
    r"(?<!\S)(?:"
    r"(?P<day>\d{1,2})/(?P<month>\d{1,2})(?:/(?P<year>\d{4}))?"
    r"|thu\s+(?P<weekday>[2-7])"
    r"|(?P<sunday>chu\s+nhat)"
    r"|(?P<rel_day>ngay\s+kia|ngay\s+mai|hom\s+nay|mai|nay)"
    r")(?!\S)"
)
TIME_PATTERN = re.compile(
    r"(?<!\S)(?:"
    r"(?P<colon_h>\d{1,2}):(?P<colon_m>\d{2})"
    r"|(?P<h_h>\d{1,2})h(?P<h_m>\d{1,2})?"
    r"|(?P<gio_h>\d{1,2})\s+gio(?:\s+(?P<gio_m>\d{1,2})(?:\s+phut)?)?"
    r")(?!\S)"
)
PERIOD_PATTERN = re.compile(r"(?<!\S)(sang|trua|chieu|toi)(?!\S)")


def _normalize(text: str) -> str:
    """Bỏ dấu tiếng Việt, chuyển chữ thường và chuẩn hóa khoảng trắng."""
    decomposed = unicodedata.normalize("NFD", text)
    no_marks = "".join(
        ch for ch in decomposed if unicodedata.category(ch) != "Mn"
    )
    ascii_text = no_marks.replace("đ", "d").replace("Đ", "d").lower()
    return " ".join(ascii_text.split())


def _resolve_dd_mm(day: int, month: int, year: int | None, base_date: date) -> date:
    """Tạo ngày hợp lệ từ dd/mm(/yyyy); nếu dd/mm đã qua trong năm thì chuyển năm sau."""
    if year is not None:
        return date(year, month, day)

    # Xử lý riêng ngày 29/2 để tìm năm nhuận phù hợp gần nhất
    if day == 29 and month == 2:
        candidate_year = base_date.year + (1 if (month, day) < (base_date.month, base_date.day) else 0)
        while True:
            try:
                return date(candidate_year, 2, 29)
            except ValueError:
                candidate_year += 1

    target = date(base_date.year, month, day)
    if target < base_date:
        target = date(base_date.year + 1, month, day)
    return target


def _extract_single(pattern: re.Pattern[str], text: str) -> tuple[re.Match[str] | None, str]:
    """Trích xuất tối đa một khớp từ chuỗi; báo lỗi nếu xuất hiện lặp lại."""
    matches = list(pattern.finditer(text))
    if len(matches) > 1:
        raise ValueError(f"Thành phần bị lặp: {text!r}")
    if not matches:
        return None, text
    match = matches[0]
    remainder = (text[: match.start()] + " " + text[match.end() :]).strip()
    return match, " ".join(remainder.split())


def _parse_date_match(match: re.Match[str], base_date: date) -> date:
    """Chuyển kết quả khớp ngày sang đối tượng date."""
    if match.group("day") is not None:
        day = int(match.group("day"))
        month = int(match.group("month"))
        year = int(match.group("year")) if match.group("year") else None
        return _resolve_dd_mm(day, month, year, base_date)

    if match.group("weekday") is not None:
        # thứ 2 -> 0 (Monday), ..., thứ 7 -> 5 (Saturday)
        target_wd = int(match.group("weekday")) - 2
        delta = (target_wd - base_date.weekday()) % 7 or 7
        return base_date + timedelta(days=delta)

    if match.group("sunday") is not None:
        # chủ nhật -> 6 (Sunday)
        delta = (6 - base_date.weekday()) % 7 or 7
        return base_date + timedelta(days=delta)

    rel_day = match.group("rel_day")
    if rel_day in ("hom nay", "nay"):
        return base_date
    if rel_day in ("ngay mai", "mai"):
        return base_date + timedelta(days=1)
    if rel_day == "ngay kia":
        return base_date + timedelta(days=2)

    raise ValueError(f"Không hiểu phần ngày: {match.group(0)!r}")


def _parse_time_match(match: re.Match[str]) -> tuple[int, int]:
    """Chuyển kết quả khớp giờ:phút và kiểm tra hợp lệ."""
    if match.group("colon_h") is not None:
        hour, minute = int(match.group("colon_h")), int(match.group("colon_m"))
    elif match.group("h_h") is not None:
        hour = int(match.group("h_h"))
        minute = int(match.group("h_m")) if match.group("h_m") is not None else 0
    else:
        hour = int(match.group("gio_h"))
        minute = int(match.group("gio_m")) if match.group("gio_m") is not None else 0

    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError(f"Giờ hoặc phút không hợp lệ: {hour}:{minute}")
    return hour, minute


def doc_gio(chuoi: str, goc: datetime) -> datetime:
    """Đọc câu hẹn giờ tiếng Việt dựa trên mốc thời gian goc."""
    if not isinstance(chuoi, str):
        raise ValueError("Chuỗi đầu vào phải là str")

    normalized = _normalize(chuoi)
    if not normalized:
        raise ValueError("Chuỗi thời gian rỗng")

    # Trường hợp khoảng thời gian tương đối ("N tiếng nữa", "N phút nữa")
    rel_match = RELATIVE_PATTERN.match(normalized)
    if rel_match:
        if rel_match.group(1) is not None:
            return goc + timedelta(hours=int(rel_match.group(1)), minutes=int(rel_match.group(2)))
        amount = int(rel_match.group(3))
        unit = rel_match.group(4)
        return goc + (timedelta(minutes=amount) if unit == "phut" else timedelta(hours=amount))

    # Trích xuất lần lượt ngày, giờ, buổi
    remainder = normalized
    date_match, remainder = _extract_single(DATE_PATTERN, remainder)
    time_match, remainder = _extract_single(TIME_PATTERN, remainder)
    period_match, remainder = _extract_single(PERIOD_PATTERN, remainder)

    # Từ chối nếu còn từ không nhận diện được hoặc không khớp thành phần nào
    if remainder or not (date_match or time_match or period_match):
        raise ValueError(f"Không hiểu chuỗi thời gian: {chuoi!r}")

    period = period_match.group(1) if period_match else None

    if time_match:
        hour, minute = _parse_time_match(time_match)
        if period in ("chieu", "toi") and hour < 12:
            hour += 12
        if not (0 <= hour <= 23):
            raise ValueError(f"Giờ sau quy đổi buổi không hợp lệ: {hour}")
    elif period:
        hour, minute = PERIOD_DEFAULTS[period]
    else:
        hour, minute = DEFAULT_TIME

    if date_match:
        target_date = _parse_date_match(date_match, goc.date())
        return goc.replace(
            year=target_date.year,
            month=target_date.month,
            day=target_date.day,
            hour=hour,
            minute=minute,
            second=0,
            microsecond=0,
        )

    # Chỉ có giờ hoặc buổi: lấy hôm nay nếu sau goc, ngược lại chuyển sang ngày mai
    candidate = goc.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if candidate <= goc:
        candidate += timedelta(days=1)
    return candidate
