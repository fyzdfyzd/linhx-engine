"""Số liệu token vào/ra và thời lượng chạy (phút) cho mỗi LX Job."""


def phut(so_giay):
    """Đổi số giây sang phút làm tròn 1 chữ số thập phân; None hoặc <= 0 trả về None."""
    if so_giay is None:
        return None
    try:
        g = float(so_giay)
    except (TypeError, ValueError):
        return None
    if g <= 0:
        return None
    return round(g / 60, 1)


def dong(job: dict) -> dict:
    """Chuẩn hoá một dòng số liệu của LX Job: token_vao, token_ra, phut."""
    j = job or {}
    p = phut(j.get("so_giay"))
    if p is None and j.get("phut") is not None:
        try:
            v = float(j.get("phut"))
            p = round(v, 1) if v > 0 else None
        except (TypeError, ValueError):
            p = None
    return {
        "token_vao": int(j.get("token_vao") or 0),
        "token_ra": int(j.get("token_ra") or 0),
        "phut": p,
    }
