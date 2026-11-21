"""Hàm đọc câu hẹn giờ tiếng Việt thành đối tượng datetime."""

from datetime import datetime, timedelta
import re
import unicodedata

# Giờ mặc định theo buổi khi không chỉ rõ giờ cụ thể
PERIOD_DEFAULT_HOURS = {
    "sang": 8,
    "trua": 12,
    "chieu": 14,
    "toi": 19,
}

# Độ lệch ngày so với mốc gốc
RELATIVE_DAY_OFFSETS = {
    "hom nay": 0,
    "nay": 0,
    "ngay mai": 1,
    "mai": 1,
    "ngay kia": 2,
}

# Ánh xạ thứ tiếng Việt sang weekday() của Python (Thứ 2 = 0 .. Chủ nhật = 6)
WEEKDAY_MAP = {
    2: 0,
    3: 1,
    4: 2,
    5: 3,
    6: 4,
    7: 5,
}

RELATIVE_DURATION_RE = re.compile(r"^(\d+)\s+(tieng|gio|phut)\s+nua$")
DATE_DM_RE = re.compile(r"(?<!\S)(\d{1,2})/(\d{1,2})(?!\S)")
WEEKDAY_RE = re.compile(r"\b(?:thu\s+(\d+)|chu\s+nhat)\b")
RELATIVE_DAY_RE = re.compile(r"\b(hom\s+nay|ngay\s+mai|ngay\s+kia|nay|mai)\b")
TIME_RE = re.compile(
    r"(?<!\S)(?:(\d{1,2}):(\d{1,2})|(\d{1,2})\s*(?:h|gio)(?:\s*(\d{1,2})(?:\s*phut)?)?)(?!\S)"
)
PERIOD_RE = re.compile(r"\b(sang|trua|chieu|toi)\b")


def _normalize_text(raw_text: str) -> str:
    """Chuẩn hoá chuỗi: chữ thường, bỏ dấu tiếng Việt, gom khoảng trắng."""
    lowered = raw_text.strip().lower().replace("đ", "d")
    decomposed = unicodedata.normalize("NFD", lowered)
    stripped = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", stripped).strip()


def _extract_single(pattern: re.Pattern[str], text: str) -> tuple[re.Match[str] | None, str]:
    """Trích xuất tối đa một khớp của pattern; báo lỗi nếu xuất hiện nhiều hơn một lần."""
    matches = list(pattern.finditer(text))
    if not matches:
        return None, text
    if len(matches) > 1:
        raise ValueError(f"Thành phần bị lặp: {text}")
    match = matches[0]
    remaining = (text[: match.start()] + " " + text[match.end() :]).strip()
    remaining = re.sub(r"\s+", " ", remaining)
    return match, remaining


def _parse_relative_duration(normalized: str, base_dt: datetime) -> datetime | None:
    """Xử lý dạng 'N tiếng nữa' hoặc 'N phút nữa'."""
    match = RELATIVE_DURATION_RE.match(normalized)
    if not match:
        return None
    amount = int(match.group(1))
    unit = match.group(2)
    try:
        if unit in ("tieng", "gio"):
            return base_dt + timedelta(hours=amount)
        return base_dt + timedelta(minutes=amount)
    except OverflowError as exc:
        raise ValueError("Khoảng thời gian vượt giới hạn") from exc


def _resolve_time(
    time_match: re.Match[str] | None,
    period: str | None,
) -> tuple[int, int]:
    """Tính giờ và phút từ phần giờ và buổi đã trích xuất."""
    if time_match is None:
        if period is not None:
            return PERIOD_DEFAULT_HOURS[period], 0
        return 9, 0

    if time_match.group(1) is not None:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2))
    else:
        hour = int(time_match.group(3))
        minute = int(time_match.group(4)) if time_match.group(4) is not None else 0

    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError(f"Giờ hoặc phút không hợp lệ: {hour}:{minute}")

    # Chiều/tối cộng thêm 12 nếu giờ nhỏ hơn 12
    if period in ("chieu", "toi") and hour < 12:
        hour += 12

    return hour, minute


def doc_gio(chuoi: str, goc: datetime) -> datetime:
    """Đọc câu hẹn giờ tiếng Việt và trả về datetime tương ứng so với mốc goc."""
    if not isinstance(chuoi, str):
        raise ValueError("Đầu vào phải là chuỗi")

    normalized = _normalize_text(chuoi)
    if not normalized:
        raise ValueError("Chuỗi thời gian rỗng")

    # Kiểm tra dạng tương đối theo khoảng thời gian trước
    relative_result = _parse_relative_duration(normalized, goc)
    if relative_result is not None:
        return relative_result

    remaining = normalized

    # Tách các thành phần ngày (tối đa một loại ngày trong câu)
    date_dm_match, remaining = _extract_single(DATE_DM_RE, remaining)
    weekday_match, remaining = _extract_single(WEEKDAY_RE, remaining)
    rel_day_match, remaining = _extract_single(RELATIVE_DAY_RE, remaining)

    date_kinds = sum(m is not None for m in (date_dm_match, weekday_match, rel_day_match))
    if date_kinds > 1:
        raise ValueError(f"Không thể kết hợp nhiều mốc ngày: {chuoi}")

    # Tách giờ và buổi
    time_match, remaining = _extract_single(TIME_RE, remaining)
    period_match, remaining = _extract_single(PERIOD_RE, remaining)

    # Nếu còn từ dư không hiểu hoặc không có thành phần hợp lệ nào -> báo lỗi
    if remaining or (date_kinds == 0 and time_match is None and period_match is None):
        raise ValueError(f"Không hiểu câu thời gian: {chuoi}")

    period = period_match.group(1) if period_match else None
    hour, minute = _resolve_time(time_match, period)

    # Xác định ngày đích
    if date_dm_match is not None:
        day = int(date_dm_match.group(1))
        month = int(date_dm_match.group(2))
        try:
            candidate = datetime(goc.year, month, day, hour, minute, tzinfo=goc.tzinfo)
        except ValueError as exc:
            raise ValueError(f"Ngày tháng không hợp lệ: {day}/{month}") from exc
        if candidate <= goc:
            try:
                candidate = datetime(goc.year + 1, month, day, hour, minute, tzinfo=goc.tzinfo)
            except ValueError as exc:
                raise ValueError(f"Ngày tháng không hợp lệ ở năm kế tiếp: {day}/{month}") from exc
        return candidate

    if weekday_match is not None:
        if weekday_match.group(1) is not None:
            day_num = int(weekday_match.group(1))
            if day_num not in WEEKDAY_MAP:
                raise ValueError(f"Thứ không hợp lệ: {day_num}")
            target_weekday = WEEKDAY_MAP[day_num]
        else:
            target_weekday = 6
        days_ahead = (target_weekday - goc.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        target_date = goc.date() + timedelta(days=days_ahead)
        return datetime(target_date.year, target_date.month, target_date.day, hour, minute, tzinfo=goc.tzinfo)

    if rel_day_match is not None:
        day_key = rel_day_match.group(1)
        target_date = goc.date() + timedelta(days=RELATIVE_DAY_OFFSETS[day_key])
        return datetime(target_date.year, target_date.month, target_date.day, hour, minute, tzinfo=goc.tzinfo)

    # Chỉ có giờ hoặc buổi: lấy hôm nay nếu còn sau goc, không thì ngày mai
    candidate = goc.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if candidate <= goc:
        candidate += timedelta(days=1)
    return candidate
