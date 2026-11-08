"""Bảng thợ điều phối: đọc nhật ký phiếu (.canh/phieu.tsv, .canh/dang-chay.json) và tổng hợp theo tuần."""
from datetime import datetime
import json
import pathlib

COT = (
    "luc_giao",
    "luc_xong",
    "tho",
    "phieu",
    "feature",
    "loai",
    "dung",
    "ket_luan",
    "phut",
    "token_vao",
    "token_ra",
)
_COT_SO = {"tho", "phut", "token_vao", "token_ra"}
_GOC = pathlib.Path(__file__).resolve().parents[3]


def _so_nguyen(v) -> int:
    if v is None:
        return 0
    s = str(v).strip()
    if not s:
        return 0
    try:
        return int(float(s))
    except (TypeError, ValueError):
        return 0


def _tuan_iso(luc_giao: str) -> str:
    s = str(luc_giao or "").strip()
    if not s:
        return "0000-W00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        dt = datetime.fromisoformat(s[:10])
    iso = dt.isocalendar()
    return f"{iso.year:04d}-W{iso.week:02d}"


def doc_phieu(duong_dan=None) -> list[dict]:
    """Đọc file TSV nhật ký phiếu; thiếu file trả []. Các cột số (tho, phut, token_*) thành int, ô trống thành 0."""
    p = pathlib.Path(duong_dan) if duong_dan is not None else (_GOC / ".canh" / "phieu.tsv")
    if not p.exists() or not p.is_file():
        return []
    try:
        noi_dung = p.read_text(encoding="utf-8-sig")
    except OSError:
        return []
    cac_dong = [d for d in noi_dung.splitlines() if d.strip()]
    if not cac_dong:
        return []
    dau = [c.strip() for c in cac_dong[0].split("\t")]
    bat_dau = 1 if dau[:2] == ["luc_giao", "luc_xong"] else 0
    cot_dung = dau if bat_dau == 1 else list(COT)
    ket_qua = []
    for dong in cac_dong[bat_dau:]:
        o = dong.split("\t")
        ban_ghi = {}
        for i, ten_cot in enumerate(COT):
            idx = cot_dung.index(ten_cot) if ten_cot in cot_dung else i
            gia_tri = o[idx].strip() if idx < len(o) else ""
            ban_ghi[ten_cot] = _so_nguyen(gia_tri) if ten_cot in _COT_SO else gia_tri
        ket_qua.append(ban_ghi)
    return ket_qua


def doc_dang_chay(duong_dan=None) -> list[dict]:
    """Đọc danh sách phiếu đang chạy từ .canh/dang-chay.json; thiếu hoặc lỗi trả []."""
    p = pathlib.Path(duong_dan) if duong_dan is not None else (_GOC / ".canh" / "dang-chay.json")
    if not p.exists() or not p.is_file():
        return []
    try:
        raw = p.read_text(encoding="utf-8-sig").strip()
        if not raw:
            return []
        data = json.loads(raw)
    except (OSError, ValueError):
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        return [data]
    return []


def tong_hop(ds, dang_chay=None) -> dict:
    """Tổng hợp số phiếu, phút, token, số lần chạm trần (gio/ngu) và tỉ lệ phiếu sửa theo tuần ISO."""
    ds = list(ds or [])
    dc = list(dang_chay) if dang_chay is not None else []
    phut = 0
    token_vao = 0
    token_ra = 0
    cham_tran = 0
    nhom_tuan: dict[str, dict[str, int]] = {}

    for d in ds:
        phut += _so_nguyen(d.get("phut"))
        token_vao += _so_nguyen(d.get("token_vao"))
        token_ra += _so_nguyen(d.get("token_ra"))
        if str(d.get("dung") or "").strip() in ("gio", "ngu"):
            cham_tran += 1
        tuan = _tuan_iso(d.get("luc_giao", ""))
        muc = nhom_tuan.setdefault(tuan, {"so_phieu": 0, "so_sua": 0})
        muc["so_phieu"] += 1
        if str(d.get("loai") or "").strip() == "sua":
            muc["so_sua"] += 1

    theo_tuan = []
    for tuan in sorted(nhom_tuan.keys()):
        sp = nhom_tuan[tuan]["so_phieu"]
        ss = nhom_tuan[tuan]["so_sua"]
        theo_tuan.append({
            "tuan": tuan,
            "so_phieu": sp,
            "so_sua": ss,
            "ti_le_sua": round(ss / sp, 2) if sp > 0 else 0.0,
        })

    return {
        "so_phieu": len(ds),
        "dang_chay": dc,
        "phut": phut,
        "token_vao": token_vao,
        "token_ra": token_ra,
        "cham_tran": cham_tran,
        "theo_tuan": theo_tuan,
    }
