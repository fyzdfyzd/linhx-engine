"""Logic thuần Python kiểm tra phiếu Agy và máy trạng thái nhap -> duyet -> giao -> nop -> dat|tra."""
import re

LOAI_PHIEU = ("feature", "sua_loi", "kiem_thu", "bao_tri")
TRANG_THAI = ("nhap", "duyet", "giao", "nop", "dat", "tra")
VAI_DIEU_HANH = ("System Manager", "LX Operator")

CHUYEN_HOP_LE = frozenset(
    {
        ("nhap", "duyet"),
        ("nhap", "tra"),
        ("duyet", "giao"),
        ("duyet", "tra"),
        ("giao", "nop"),
        ("giao", "duyet"),
        ("nop", "dat"),
        ("nop", "tra"),
    }
)

CHUYEN_CAN_DIEU_HANH = frozenset(
    {
        ("nhap", "duyet"),
        ("nhap", "tra"),
        ("duyet", "tra"),
    }
)

MAU_LENH_SHELL = (
    re.compile(r"\b(?:powershell|pwsh)(?:\.exe)?\b", re.IGNORECASE),
    re.compile(r"\bcmd\.exe\b", re.IGNORECASE),
    re.compile(r"\bcmd\s+/[ck]\b", re.IGNORECASE),
    re.compile(r"\b(?:ba|z|k|da|c)?sh(?:\.exe)?\s+-c\b", re.IGNORECASE),
    re.compile(r"\b(?:curl|wget)\b[^\n]*?\|\s*(?:sudo\s+)?(?:ba|z|k|da)?sh\b", re.IGNORECASE),
    re.compile(r"\|\s*(?:sudo\s+)?(?:ba|z|k|da)?sh\b", re.IGNORECASE),
    re.compile(r"\binvoke-expression\b", re.IGNORECASE),
    re.compile(r"\biex\b", re.IGNORECASE),
)


def kiem_de(de: str) -> None:
    """Kiểm tra nội dung đề phiếu: không được rỗng và không chứa mẫu lệnh shell nguy hiểm."""
    if not isinstance(de, str) or not de.strip():
        raise ValueError("Đề phiếu không được để trống")
    for mau in MAU_LENH_SHELL:
        if mau.search(de):
            raise ValueError(f"Đề phiếu chứa mẫu lệnh shell bị cấm: {mau.pattern}")


def kiem_phieu(phieu: dict) -> None:
    """Kiểm tra tính hợp lệ của dict phiếu Agy (loai_phieu, trang_thai, de, phut, token)."""
    if not isinstance(phieu, dict):
        raise ValueError("Phiếu phải là kiểu dict")

    loai = phieu.get("loai_phieu")
    if not isinstance(loai, str) or loai not in LOAI_PHIEU:
        raise ValueError(f"loai_phieu không hợp lệ: {loai!r}")

    if "trang_thai" in phieu and phieu["trang_thai"] is not None:
        tt = phieu["trang_thai"]
        if not isinstance(tt, str) or tt not in TRANG_THAI:
            raise ValueError(f"trang_thai không hợp lệ: {tt!r}")

    kiem_de(phieu.get("de", ""))

    if phieu.get("phut") is not None:
        try:
            phut_val = float(phieu["phut"])
        except (TypeError, ValueError) as exc:
            raise ValueError("phut phải là số") from exc
        if phut_val < 0:
            raise ValueError("phut không được âm")

    if phieu.get("token") is not None:
        try:
            token_val = int(phieu["token"])
        except (TypeError, ValueError) as exc:
            raise ValueError("token phải là số nguyên") from exc
        if token_val < 0:
            raise ValueError("token không được âm")


def _co_vai_dieu_hanh(vai_tro) -> bool:
    if not vai_tro:
        return False
    if isinstance(vai_tro, str):
        tap_vai = {vai_tro}
    else:
        tap_vai = set(vai_tro)
    return bool(tap_vai & set(VAI_DIEU_HANH))


def chuyen_trang_thai(
    phieu: dict,
    trang_thai_moi: str,
    vai_tro: list[str] | set[str] | tuple[str, ...] = (),
    ly_do_tra: str = "",
) -> dict:
    """Chuyển trạng thái phiếu theo đúng máy trạng thái và trả bản sao dict phiếu đã cập nhật."""
    if not isinstance(phieu, dict):
        raise ValueError("Phiếu phải là kiểu dict")

    if "loai_phieu" in phieu or "de" in phieu:
        if "loai_phieu" in phieu:
            loai = phieu.get("loai_phieu")
            if not isinstance(loai, str) or loai not in LOAI_PHIEU:
                raise ValueError(f"loai_phieu không hợp lệ: {loai!r}")
        if "de" in phieu:
            kiem_de(phieu.get("de", ""))

    trang_thai_cu = phieu.get("trang_thai")
    if not isinstance(trang_thai_cu, str) or trang_thai_cu not in TRANG_THAI:
        raise ValueError(f"Trạng thái hiện tại không hợp lệ: {trang_thai_cu!r}")
    if not isinstance(trang_thai_moi, str) or trang_thai_moi not in TRANG_THAI:
        raise ValueError(f"Trạng thái mới không hợp lệ: {trang_thai_moi!r}")

    buoc = (trang_thai_cu, trang_thai_moi)
    if buoc not in CHUYEN_HOP_LE:
        raise ValueError(f"Không được chuyển trạng thái từ {trang_thai_cu!r} sang {trang_thai_moi!r}")

    if buoc in CHUYEN_CAN_DIEU_HANH and not _co_vai_dieu_hanh(vai_tro):
        raise PermissionError("Chỉ vai điều hành (System Manager, LX Operator) mới được duyệt hoặc trả phiếu")

    ly_do = str(ly_do_tra or "").strip()
    if not ly_do and isinstance(phieu.get("ly_do_tra"), str):
        ly_do = phieu["ly_do_tra"].strip()

    if buoc == ("nhap", "tra") and not ly_do:
        raise ValueError("Trả phiếu từ trạng thái nhap bắt buộc có lý do trả")

    ket_qua = dict(phieu)
    ket_qua["trang_thai"] = trang_thai_moi
    if trang_thai_moi == "tra":
        ket_qua["ly_do_tra"] = ly_do
    return ket_qua
