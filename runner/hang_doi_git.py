"""Nguon viec GitHub (nhanh hang-doi) cho linhx-runner.

Cau truc tren nhanh `hang-doi`:
  hang-doi/moi/<id>.md            phieu cho (may: may-1|may-2|may-3|bat-ky; loai: code|trinh-duyet|khac)
  hang-doi/dang/<id>.md           da co may nhan (them dong nhan: <may> <gio>)
  hang-doi/xong/<id>/KET-QUA.md   trang thai (xong|loi|dung), file da doi, duong dan Drive, phut, token
"""
from __future__ import annotations

from contextlib import contextmanager
import json
import os
import random
import re
import shutil
import stat
import subprocess
import threading
import time
import traceback
from pathlib import Path

try:
    from runner import linhx_runner
except ImportError:
    import linhx_runner

try:
    from runner import ho_so_may
except ImportError:
    import ho_so_may

NHANH_MAC_DINH = "hang-doi"
REMOTE_MAC_DINH = "origin"
GIOI_HAN_KET_QUA = 2000
NGUONG_TEP_NANG = 1024 * 1024  # 1 MB
THU_MUC_DRIVE_MAC_DINH = Path(r"G:\My Drive\LINHX-VIEC")
THU_MUC_LOG_MAC_DINH = Path(r"D:\linhx\linhx-runner\log")
DUONG_DAN_PHIEU_PING_MAU = linhx_runner.GOC / "phieu-mau" / "ping.md"
SO_LAN_THU_PUSH = 8
SO_LAN_THU_PUSH_NHIP = 3
HO_SO_CHU_KY_PHUT_MAC_DINH = 60.0
_CAN_LINH_BLOCK_RE = re.compile(
    r"`?\bCAN-LINH\s*:\s*([^;\r\n`]+?)(?:\s*;\s*LENH\s*:\s*([^\r\n`]*))?`?(?:\r?\n|$)",
    re.IGNORECASE,
)
_NHIP_CUOI_DONG_RE = re.compile(r"^nhip\s*:\s*(.+)$", re.IGNORECASE)
SO_PHIEU_TRINH_DUYET_TOI_DA = 1
SO_PHIEU_CODE_MAC_DINH = linhx_runner.SO_PHIEU_CODE_MAC_DINH
NHAN_BAT_KY_MAC_DINH = linhx_runner.NHAN_BAT_KY_MAC_DINH
NGUONG_RAM_TRONG_GB = linhx_runner.NGUONG_RAM_TRONG_GB
MAX_SELF_REPAIR = 3
SELF_REPAIR_EXCERPT_LIMIT = 1500
SELF_REPAIR_SECTION_TITLE = "Lần trước trượt vì:"
_KHOA_DAU_DONG = re.compile(r"^([a-zA-Z0-9_-]+)\s*:\s*(.*)$")
_SEMI_LIST_HEADERS = frozenset({"phu_thuoc", "theo_doi"})
_SELF_REPAIR_SUFFIX_RE = re.compile(r"^(.*)-sua-(\d+)$")
_SELF_REPAIR_SECTION_SPLIT_RE = re.compile(r"\n+(?:##\s*)?Lần trước trượt vì:\s*\n", re.UNICODE)
_HTTP_429_RE = re.compile(r"(?<!\d)429(?!\d)")
_NON_HTTP_429_CONTEXT_RE = re.compile(
    r"(?:\bgiay=429\b|\bline\s+429\b|[A-Za-z0-9_./\\-]+:429(?::|\b))",
    re.IGNORECASE,
)
_MACHINE_ERROR_PATTERNS = (
    "không thấy agy",
    "khong thay agy",
    "không chạy được agy",
    "khong chay duoc agy",
    "tên model không hợp lệ",
    "ten model khong hop le",
    "thiếu agy",
    "thieu agy",
    "filenotfounderror",
    "command not found",
    "is not recognized as an internal or external command",
    "too many requests",
    "rate limit",
    "rate_limit",
    "ratelimit",
    "resource_exhausted",
    "quota exceeded",
    "exhausted your capacity",
    "out of quota",
)

_CHAY_AGY_GOC = linhx_runner.chay_agy
chay_agy = _CHAY_AGY_GOC

_LAY_RAM_GOC = linhx_runner.lay_ram_trong_gb
lay_ram_trong_gb = _LAY_RAM_GOC


def _lay_ham_chay_agy(chay_agy_fn=None):
    if chay_agy_fn is not None:
        return chay_agy_fn
    if chay_agy is not _CHAY_AGY_GOC:
        return chay_agy
    return linhx_runner.chay_agy


def _goi_lay_ram_trong_gb():
    if lay_ram_trong_gb is not _LAY_RAM_GOC:
        return lay_ram_trong_gb()
    return linhx_runner.lay_ram_trong_gb()


def du_ram_nhan_viec(cfg: dict | None = None) -> tuple[bool, float | None]:
    return linhx_runner.du_ram_nhan_viec(cfg, lay_ram_fn=_goi_lay_ram_trong_gb)


def lay_so_phieu_toi_da(cfg: dict | None = None) -> int:
    if cfg and "so_phieu" in cfg and cfg["so_phieu"] is not None:
        return linhx_runner._ep_so_nguyen_khong_am(cfg["so_phieu"], SO_PHIEU_CODE_MAC_DINH)
    return linhx_runner._ep_so_nguyen_khong_am(os.environ.get("LINHX_SO_PHIEU"), SO_PHIEU_CODE_MAC_DINH)


def co_nhan_bat_ky(cfg: dict | None = None) -> bool:
    # Kiểm tra máy có nhận phiếu bat-ky hay chỉ nhận phiếu đích danh tên máy (mặc định: có nhận)
    mac_dinh = bool(NHAN_BAT_KY_MAC_DINH)
    if cfg:
        if "nhan_bat_ky" in cfg and cfg["nhan_bat_ky"] is not None:
            return linhx_runner._ep_cong_tac(cfg["nhan_bat_ky"], mac_dinh)
        if "LINHX_NHAN_BAT_KY" in cfg and cfg["LINHX_NHAN_BAT_KY"] is not None:
            return linhx_runner._ep_cong_tac(cfg["LINHX_NHAN_BAT_KY"], mac_dinh)
    return linhx_runner._ep_cong_tac(os.environ.get("LINHX_NHAN_BAT_KY"), mac_dinh)


def chay_git(args, cwd, check=True, timeout=120):
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    kw = {}
    if os.name == "nt":
        kw["creationflags"] = 0x08000000  # CREATE_NO_WINDOW
    p = subprocess.run(
        ["git"] + list(args),
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        **kw,
    )
    if check and p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} loi ({p.returncode}): {(p.stderr or p.stdout).strip()}")
    return p


@contextmanager
def _khoa_tep(duong_dan_khoa: Path, timeout: float = 30.0):
    duong_dan_khoa.parent.mkdir(parents=True, exist_ok=True)
    han = time.monotonic() + timeout
    fd = None
    while True:
        try:
            fd = os.open(str(duong_dan_khoa), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, f"{os.getpid()} {time.time()}\n".encode("utf-8"))
            break
        except FileExistsError:
            try:
                if time.time() - duong_dan_khoa.stat().st_mtime > 300:
                    duong_dan_khoa.unlink(missing_ok=True)
                    continue
            except OSError:
                pass
            if time.monotonic() >= han:
                raise TimeoutError(f"Khong lay duoc khoa git: {duong_dan_khoa}")
            time.sleep(0.05)
    try:
        yield
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        try:
            duong_dan_khoa.unlink(missing_ok=True)
        except OSError:
            pass


def _tach_cap_khoa_gia_tri(dong: str):
    """Tach 1 dong header (ho tro ca 'may: bat-ky; loai: code')."""
    m = _KHOA_DAU_DONG.match(dong.strip())
    if not m:
        return None
    first_key = m.group(1).lower()
    if first_key in _SEMI_LIST_HEADERS:
        return [(first_key, m.group(2).strip())]
    phan = [p.strip() for p in dong.split(";") if p.strip()]
    ket_qua = []
    for p in phan:
        mp = _KHOA_DAU_DONG.match(p)
        if not mp:
            return [(first_key, m.group(2).strip())]
        ket_qua.append((mp.group(1).lower(), mp.group(2).strip()))
    return ket_qua


def parse_dependencies(raw_value) -> list[str]:
    # Phân tích danh sách mã phiếu phụ thuộc từ header `phu_thuoc: id1; id2`
    if raw_value is None:
        return []
    if isinstance(raw_value, (list, tuple)):
        items = [str(item).strip() for item in raw_value]
    else:
        cleaned = str(raw_value).split("#", 1)[0].strip()
        if not cleaned:
            return []
        items = [part.strip() for part in cleaned.split(";")]
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def parse_self_repair_count(raw_value) -> int:
    # Phân tích số lượt tự sửa từ header `tu_sua: N` (mặc định 0 = tắt, tối đa 3)
    if raw_value is None:
        return 0
    if isinstance(raw_value, bool):
        return int(raw_value)
    cleaned = str(raw_value).split("#", 1)[0].strip()
    if not cleaned:
        return 0
    try:
        count = int(cleaned)
    except ValueError:
        return 0
    return min(MAX_SELF_REPAIR, max(0, count))


def phan_tich_phieu(noi_dung: str, ma_phieu: str) -> dict:
    van_ban = noi_dung.lstrip("\ufeff")
    cac_dong = van_ban.splitlines()
    meta = {}
    chi_so_than = 0

    if cac_dong and cac_dong[0].strip() == "---":
        ket_thuc = None
        for i in range(1, len(cac_dong)):
            if cac_dong[i].strip() == "---":
                ket_thuc = i
                break
        if ket_thuc is not None:
            for dong in cac_dong[1:ket_thuc]:
                if not dong.strip() or dong.strip().startswith("#"):
                    continue
                cap = _tach_cap_khoa_gia_tri(dong)
                if cap:
                    for k, v in cap:
                        meta[k] = v
            chi_so_than = ket_thuc + 1
    else:
        for i, dong in enumerate(cac_dong):
            s = dong.strip()
            if not s:
                chi_so_than = i + 1
                break
            cap = _tach_cap_khoa_gia_tri(s)
            if not cap:
                chi_so_than = i
                break
            for k, v in cap:
                meta[k] = v
        else:
            chi_so_than = len(cac_dong)

    de = "\n".join(cac_dong[chi_so_than:]).strip()
    if not de:
        de = van_ban.strip() or ma_phieu

    may = (meta.get("may") or "bat-ky").split("#", 1)[0].strip().lower() or "bat-ky"
    if may in ("*", "all", "tat-ca"):
        may = "bat-ky"
    loai = (meta.get("loai") or "code").split("#", 1)[0].strip().lower() or "code"
    if loai in ("trinh_duyet", "browser"):
        loai = "trinh-duyet"
    che_do = (meta.get("che_do") or "thuc").split("#", 1)[0].strip().lower() or "thuc"
    tran_raw = str(meta.get("tran_phut") or "").split("#", 1)[0].strip()
    if tran_raw:
        try:
            tran_f = float(tran_raw)
            tran_phut = int(tran_f) if tran_f.is_integer() else tran_f
        except ValueError:
            tran_phut = 40
    else:
        tran_phut = 40

    phu_thuoc = parse_dependencies(meta.get("phu_thuoc"))
    tu_sua = parse_self_repair_count(meta.get("tu_sua"))

    return {
        "viec": ma_phieu,
        "may": may,
        "loai": loai,
        "che_do": che_do,
        "tran_phut": tran_phut,
        "phu_thuoc": phu_thuoc,
        "tu_sua": tu_sua,
        "de": de,
        "meta": meta,
    }


def tao_phieu_ping(may: str = "bat-ky", che_do: str | None = None, tran_phut: int = 3) -> str:
    """Doc phieu mau ping.md va tuy bien may dich / che_do de gui thu duong ong."""
    may_chuan = (may or "bat-ky").strip().lower()
    if DUONG_DAN_PHIEU_PING_MAU.is_file():
        mau = DUONG_DAN_PHIEU_PING_MAU.read_text(encoding="utf-8")
        p = phan_tich_phieu(mau, "ping")
        than = p["de"]
    else:
        than = (
            "Phiếu thử đường ống hàng đợi GitHub (ping).\n"
            "Trả lời ngắn gọn 1 dòng theo mẫu: `PONG <tên-máy-windows> <thư-mục-hiện-tại>` rồi kết thúc ngay.\n"
            "Không tạo, sửa hay xoá bất kỳ file nào."
        )
    dau = [
        f"may: {may_chuan}",
        "loai: code",
        f"tran_phut: {int(tran_phut)}",
    ]
    if che_do and str(che_do).strip().lower() not in ("", "thuc"):
        dau.append(f"che_do: {str(che_do).strip().lower()}")
    return "\n".join(dau) + "\n\n" + than.strip() + "\n"


def chen_dong_nhan(noi_dung: str, tho: str, thoi_gian: str = "") -> str:
    moc = thoi_gian or time.strftime("%Y-%m-%dT%H:%M:%S%z")
    dong_nhan = f"nhan: {tho} {moc}"
    van_ban = noi_dung.lstrip("\ufeff")
    cac_dong = van_ban.splitlines()

    if cac_dong and cac_dong[0].strip() == "---":
        for i in range(1, len(cac_dong)):
            if cac_dong[i].strip() == "---":
                cac_dong.insert(i, dong_nhan)
                return "\n".join(cac_dong) + ("\n" if van_ban.endswith("\n") else "")

    vi_tri = 0
    for i, dong in enumerate(cac_dong):
        if _tach_cap_khoa_gia_tri(dong.strip()):
            vi_tri = i + 1
        else:
            break
    cac_dong.insert(vi_tri, dong_nhan)
    ket_qua = "\n".join(cac_dong)
    if van_ban.endswith("\n") or not ket_qua.endswith("\n"):
        ket_qua += "\n"
    return ket_qua


def cap_nhat_dong_nhip_cuoi(
    noi_dung: str,
    phut_da_chay: float,
    dong_cuoi: str,
    gio_chuoi: str = "",
) -> str:
    """Ghi 1 dòng `nhip: <giờ> <phút đã chạy> <dòng stdout/stderr cuối ≤120 ký tự>` vào cuối phiếu (chỉ giữ 1 dòng nhip)."""
    gio = (gio_chuoi or time.strftime("%H:%M")).strip()
    phut_txt = f"{max(0, int(round(float(phut_da_chay))))}p"
    dong_sach = " ".join(str(dong_cuoi or "").splitlines()).strip()[: linhx_runner.GIOI_HAN_DONG_NHIP]
    if not dong_sach:
        dong_sach = "(chưa có đầu ra)"
    dong_nhip_moi = f"nhip: {gio} {phut_txt} {dong_sach}"

    cac_dong = str(noi_dung or "").splitlines()
    # Bỏ toàn bộ các dòng nhip cũ ở cuối phiếu để chỉ giữ đúng 1 dòng nhip mới nhất
    giu_lai = [d for d in cac_dong if not _NHIP_CUOI_DONG_RE.match(d.strip())]
    while giu_lai and not giu_lai[-1].strip():
        giu_lai.pop()
    giu_lai.append("")
    giu_lai.append(dong_nhip_moi)
    return "\n".join(giu_lai) + "\n"


def trich_khoi_can_linh(van_ban: str | None) -> tuple[str, str] | None:
    """Tách khối `CAN-LINH: <việc>; LENH: <lệnh>` từ câu trả lời của agy."""
    if not van_ban:
        return None
    s = str(van_ban)
    # Bỏ qua chính câu hướng dẫn mẫu nếu vô tình bị lặp lại nguyên văn
    s = s.replace(linhx_runner.CAU_NHAC_CAN_LINH, "")
    s = s.replace(linhx_runner.CAU_NHAC_TIEN_CANH, "")
    matches = list(_CAN_LINH_BLOCK_RE.finditer(s))
    for m in reversed(matches):
        viec_can = " ".join((m.group(1) or "").split()).strip(" `")
        lenh_dan = " ".join((m.group(2) or "").split()).strip(" `")
        if not viec_can or viec_can.startswith("<việc>"):
            continue
        if lenh_dan.startswith("<lệnh"):
            lenh_dan = ""
        return viec_can, lenh_dan
    return None


def tao_can_linh_md(
    phieu_id: str,
    tho: str,
    viec_can: str,
    lenh_dan: str = "",
    gio_iso: str = "",
) -> str:
    """Tạo nội dung file `hang-doi/can-linh/<id>.md` gồm máy, phiếu, việc, lệnh, giờ."""
    moc_gio = (gio_iso or time.strftime("%Y-%m-%dT%H:%M:%S%z")).strip()
    viec_sach = _cat_mot_dong(viec_can, 400)
    lenh_sach = _cat_mot_dong(lenh_dan, 500)
    cac_dong = [
        f"may: {_cat_mot_dong(tho, 80)}",
        f"phieu: {_cat_mot_dong(phieu_id, 120)}",
        f"viec: {viec_sach}",
        f"lenh: {lenh_sach}",
        f"gio: {moc_gio}",
    ]
    return "\n".join(cac_dong) + "\n"


def ghi_nhip_phieu_git(
    cfg: dict,
    phieu_id: str,
    phut_da_chay: float,
    dong_cuoi: str,
    gio_chuoi: str = "",
) -> bool:
    """Cập nhật dòng nhip vào cuối `hang-doi/dang/<id>.md`, pull --rebase và push tối đa 3 lần (lỗi bỏ qua)."""
    _, _, remote, nhanh = _duong_dan_wt(cfg)
    tho = cfg["tho"]
    try:
        with _khoa_tep(_duong_dan_khoa_wt(cfg), timeout=10.0):
            wt = dam_bao_worktree(cfg)
            if wt is None:
                return False
            for lan in range(SO_LAN_THU_PUSH_NHIP):
                if lan > 0:
                    chay_git(["pull", "--rebase", remote, nhanh], cwd=wt, check=False, timeout=45)
                goc_hd = thu_muc_hang_doi(wt)
                tep_dang = goc_hd / "dang" / f"{phieu_id}.md"
                if not tep_dang.is_file():
                    return False
                noi_dung_cu = tep_dang.read_text(encoding="utf-8", errors="replace")
                noi_dung_moi = cap_nhat_dong_nhip_cuoi(
                    noi_dung_cu,
                    phut_da_chay=phut_da_chay,
                    dong_cuoi=dong_cuoi,
                    gio_chuoi=gio_chuoi,
                )
                if noi_dung_moi == noi_dung_cu:
                    return True
                tep_dang.write_text(noi_dung_moi, encoding="utf-8")
                _commit_git(wt, tho, f"nhip: {phieu_id} ({int(round(phut_da_chay))}p)")
                pull_rb = chay_git(["pull", "--rebase", remote, nhanh], cwd=wt, check=False, timeout=45)
                if pull_rb.returncode != 0:
                    chay_git(["rebase", "--abort"], cwd=wt, check=False, timeout=15)
                    wt = dam_bao_worktree(cfg)
                    if wt is None:
                        return False
                    continue
                push = chay_git(["push", remote, f"HEAD:refs/heads/{nhanh}"], cwd=wt, check=False, timeout=45)
                if push.returncode == 0:
                    return True
                wt = dam_bao_worktree(cfg)
                if wt is None:
                    return False
    except Exception:
        return False
    return False


def cap_nhat_ho_so_may_git(cfg: dict, thu_thap_fn=None) -> bool:
    """Ghi `hang-doi/may/<ma-may>.json` và chỉ commit + push khi hồ sơ thay đổi (lỗi bỏ qua)."""
    if not linhx_runner._ep_cong_tac(cfg.get("ghi_ho_so_may", os.environ.get("LINHX_GHI_HO_SO", "1")), True):
        return False
    _, _, remote, nhanh = _duong_dan_wt(cfg)
    tho = str(cfg.get("tho") or "may").strip().lower()
    ten_tep = _ten_phieu_an_toan(tho)
    ham_thu_thap = thu_thap_fn or ho_so_may.thu_thap_ho_so_may
    try:
        with _khoa_tep(_duong_dan_khoa_wt(cfg), timeout=15.0):
            for lan in range(SO_LAN_THU_PUSH_NHIP):
                wt = dam_bao_worktree(cfg)
                if wt is None:
                    return False
                goc_hd = thu_muc_hang_doi(wt)
                tm_may = goc_hd / "may"
                tep_json = tm_may / f"{ten_tep}.json"
                ho_so_cu = None
                if tep_json.is_file():
                    try:
                        ho_so_cu = json.loads(tep_json.read_text(encoding="utf-8", errors="replace"))
                    except (OSError, ValueError):
                        ho_so_cu = None
                ho_so_moi = ham_thu_thap(cfg, wt=wt)
                if not ho_so_may.ho_so_da_doi(ho_so_cu, ho_so_moi):
                    return False
                tm_may.mkdir(parents=True, exist_ok=True)
                tep_json.write_text(json.dumps(ho_so_moi, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                _commit_git(wt, tho, f"may: cap nhat ho so {tho}")
                pull_rb = chay_git(["pull", "--rebase", remote, nhanh], cwd=wt, check=False, timeout=45)
                if pull_rb.returncode != 0:
                    chay_git(["rebase", "--abort"], cwd=wt, check=False, timeout=15)
                    continue
                push = chay_git(["push", remote, f"HEAD:refs/heads/{nhanh}"], cwd=wt, check=False, timeout=45)
                if push.returncode == 0:
                    return True
                time.sleep(0.05 * (lan + 1))
    except Exception:
        return False
    return False


def _cat_mot_dong(gia_tri: str, gioi_han_dong: int = 320) -> str:
    s = " ".join(str(gia_tri or "").splitlines()).strip()
    if len(s) <= gioi_han_dong:
        return s
    return s[: max(0, gioi_han_dong - 3)] + "..."


def rut_gon_van_ban(van_ban: str, gioi_han: int) -> str:
    """Cat van ban khong vuot qua `gioi_han` ky tu, giu ca phan dau va phan cuoi."""
    if gioi_han <= 0:
        return ""
    s = str(van_ban or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not s:
        return ""
    co_xuong_dong = s + "\n"
    if len(co_xuong_dong) <= gioi_han:
        return co_xuong_dong
    dau_cat = "\n...[cat bot]...\n"
    ngan_sach = gioi_han - len(dau_cat) - 1
    if ngan_sach >= 80:
        dau_phan = (ngan_sach * 7) // 10
        duoi_phan = ngan_sach - dau_phan
        return s[:dau_phan] + dau_cat + s[-duoi_phan:] + "\n"
    duoi_don = "\n...[cat bot]\n"
    if gioi_han > len(duoi_don):
        return s[: gioi_han - len(duoi_don)] + duoi_don
    return s[:gioi_han]


def tao_ket_qua_md(
    phieu_id: str,
    tho: str,
    trang_thai: str,
    ket_qua,
    nhat_ky: str = "",
    phut: float = 0.0,
    token_vao: int = 0,
    token_ra: int = 0,
    tep_doi=None,
    drive: str = "",
    gioi_han: int = GIOI_HAN_KET_QUA,
    model: str = "",
    canh_bao: str = "",
) -> str:
    if gioi_han <= 0:
        return ""
    tt = trang_thai if trang_thai in ("xong", "loi", "dung") else "loi"
    ds_tep = _cat_mot_dong(", ".join(tep_doi), 300) if tep_doi else "(khong)"
    duong_drive = _cat_mot_dong(drive, 350) if drive and str(drive).strip() else "(khong)"
    ten_model_hien_thi = (
        _cat_mot_dong(model, 120) if model and str(model).strip() else linhx_runner.MODEL_MAC_DINH_NHAN
    )
    dau = (
        f"model: {ten_model_hien_thi}\n"
        f"phieu: {_cat_mot_dong(phieu_id, 120)}\n"
        f"may: {_cat_mot_dong(tho, 80)}\n"
        f"trang_thai: {tt}\n"
        f"tep_doi: {ds_tep}\n"
        f"drive: {duong_drive}\n"
        f"phut: {phut:.2f}\n"
        f"token: vao={int(token_vao or 0)} ra={int(token_ra or 0)}\n\n"
    )
    nguon_than = ket_qua if ket_qua is not None and str(ket_qua).strip() else (nhat_ky or "")
    than = str(nguon_than).replace("\r\n", "\n").replace("\r", "\n").strip()
    cb_sach = str(canh_bao or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if cb_sach and cb_sach not in than:
        than = f"{cb_sach}\n\n{than}" if than else cb_sach
    toan_bo = dau + (than + "\n" if than else "")
    if len(toan_bo) <= gioi_han:
        return toan_bo
    if len(dau) >= gioi_han:
        return dau[:gioi_han]
    return dau + rut_gon_van_ban(than, gioi_han - len(dau))


def _ten_phieu_an_toan(phieu_id: str) -> str:
    ten = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", str(phieu_id or "").strip())
    while ".." in ten:
        ten = ten.replace("..", "_")
    ten = ten.strip(". ")
    return ten or "phieu"


def _thu_muc_drive(cfg: dict | None = None) -> Path:
    if cfg and cfg.get("thu_muc_drive"):
        return Path(cfg["thu_muc_drive"])
    env_val = os.environ.get("LINHX_DRIVE", "").strip()
    if env_val:
        return Path(env_val)
    return Path(THU_MUC_DRIVE_MAC_DINH)


def _thu_muc_log(cfg: dict | None = None) -> Path:
    if cfg and cfg.get("thu_muc_log"):
        return Path(cfg["thu_muc_log"])
    env_val = os.environ.get("LINHX_LOG_DIR", "").strip()
    if env_val:
        return Path(env_val)
    return Path(THU_MUC_LOG_MAC_DINH)


def duong_dan_log_phieu(phieu_id: str, cfg: dict | None = None, thu_muc_log: Path | str | None = None) -> Path:
    goc_log = Path(thu_muc_log) if thu_muc_log is not None else _thu_muc_log(cfg)
    return goc_log / f"{_ten_phieu_an_toan(phieu_id)}.jsonl"


def ghi_log_phieu(tep_log: Path, su_kien: str, **truong) -> Path:
    """Ghi 1 dong JSONL day du vao file log cua phieu tren may."""
    tep_log = Path(tep_log)
    tep_log.parent.mkdir(parents=True, exist_ok=True)
    ban_ghi = {
        "luc": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "su_kien": su_kien,
    }
    ban_ghi.update(truong)
    with tep_log.open("a", encoding="utf-8") as f:
        f.write(json.dumps(ban_ghi, ensure_ascii=False) + "\n")
    return tep_log


def chep_tep_nang_sang_drive(
    thu_muc_nguon: Path,
    phieu_id: str,
    thu_muc_drive: Path | str | None = None,
    chi_cac_tep: list[str] | None = None,
    nguong_byte: int | None = None,
    bo_qua: set[str] | None = None,
) -> list[Path]:
    """Chep cac file > 1 MB trong `thu_muc_nguon` sang `<thu_muc_drive>/<id>/`."""
    goc_nguon = Path(thu_muc_nguon)
    if not goc_nguon.is_dir():
        return []
    nguong = NGUONG_TEP_NANG if nguong_byte is None else int(nguong_byte)
    ds_bo_qua = set(bo_qua or ())
    goc_nguon_chuan = goc_nguon.resolve()

    if chi_cac_tep is not None:
        ung_vien_rel = [r for r in chi_cac_tep if r not in ds_bo_qua and not r.endswith(" (xoa)")]
    else:
        ung_vien_rel = []
        for p in sorted(goc_nguon.rglob("*")):
            if p.is_symlink() or not p.is_file():
                continue
            rel = p.relative_to(goc_nguon).as_posix()
            if rel == ".git" or rel.startswith(".git/") or rel in ds_bo_qua:
                continue
            ung_vien_rel.append(rel)

    can_chep: list[tuple[Path, str]] = []
    for rel in ung_vien_rel:
        nguon = goc_nguon / rel
        if nguon.is_symlink() or not nguon.is_file():
            continue
        try:
            nguon_chuan = nguon.resolve()
            nguon_chuan.relative_to(goc_nguon_chuan)
            if nguon.stat().st_size > nguong:
                can_chep.append((nguon, Path(rel).as_posix()))
        except (OSError, ValueError):
            continue

    if not can_chep:
        return []

    goc_drive = Path(thu_muc_drive) if thu_muc_drive is not None else _thu_muc_drive()
    tm_dich_phieu = goc_drive / _ten_phieu_an_toan(phieu_id)
    da_chep: list[Path] = []
    for nguon, rel_posix in can_chep:
        dich = tm_dich_phieu.joinpath(*rel_posix.split("/"))
        dich.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(nguon, dich)
        da_chep.append(dich)
    return da_chep


def dinh_dang_duong_dan_drive(da_chep: list[Path]) -> str:
    if not da_chep:
        return ""
    if len(da_chep) == 1:
        return str(da_chep[0])
    noi = ", ".join(str(p) for p in da_chep)
    if len(noi) <= 320:
        return noi
    ten_tep = ", ".join(p.name for p in da_chep)
    return _cat_mot_dong(f"{da_chep[0].parent} ({len(da_chep)} tep: {ten_tep})", 320)


def _duong_dan_wt(cfg: dict) -> tuple[Path, Path, str, str]:
    repo = Path(cfg.get("repo_hang_doi") or linhx_runner.GOC.parent).resolve()
    nhanh = (cfg.get("nhanh_hang_doi") or NHANH_MAC_DINH).strip()
    remote = (cfg.get("remote_hang_doi") or REMOTE_MAC_DINH).strip()
    wt_cfg = cfg.get("wt_hang_doi") or ""
    wt = Path(wt_cfg).resolve() if str(wt_cfg).strip() else (repo.parent / f".{repo.name}-{nhanh}")
    return repo, wt, remote, nhanh


def _duong_dan_khoa_wt(cfg: dict) -> Path:
    repo, wt, _, nhanh = _duong_dan_wt(cfg)
    return repo.parent / f".{repo.name}-{nhanh}.lock"


def dam_bao_worktree(cfg: dict):
    """Keo nhanh hang-doi tu remote va tra ve thu muc worktree da dong bo."""
    repo, wt, remote, nhanh = _duong_dan_wt(cfg)
    ref_remote = f"refs/remotes/{remote}/{nhanh}"
    p = chay_git(["fetch", remote, f"+refs/heads/{nhanh}:{ref_remote}"], cwd=repo, check=False)
    if p.returncode != 0:
        err = (p.stderr or p.stdout or "").lower()
        if "couldn't find remote ref" in err or "remote ref does not exist" in err:
            return None
        raise RuntimeError(f"Khong keo duoc nhanh {nhanh}: {(p.stderr or p.stdout).strip()}")

    nhanh_hien_tai = chay_git(["symbolic-ref", "--short", "-q", "HEAD"], cwd=repo, check=False)
    if nhanh_hien_tai.returncode == 0 and nhanh_hien_tai.stdout.strip() == nhanh:
        chay_git(["reset", "--hard", ref_remote], cwd=repo)
        chay_git(["clean", "-fd"], cwd=repo)
        return repo

    if not (wt / ".git").exists():
        if wt.exists():
            shutil.rmtree(wt, onerror=lambda fn, p, _: (os.chmod(p, stat.S_IWRITE), fn(p)))
        chay_git(["worktree", "prune"], cwd=repo, check=False)
        chay_git(["worktree", "add", "-B", nhanh, str(wt), ref_remote], cwd=repo)
    else:
        chay_git(["checkout", "-B", nhanh, ref_remote], cwd=wt)
        chay_git(["reset", "--hard", ref_remote], cwd=wt)
        chay_git(["clean", "-fd"], cwd=wt)
    return wt


def thu_muc_hang_doi(wt: Path) -> Path:
    chinh = wt / "hang-doi"
    if chinh.exists() or not (wt / "moi").exists():
        return chinh
    return wt


def dem_phieu_dang_chay(wt: Path, tho: str) -> dict[str, int]:
    """Dem so phieu dang nam trong hang-doi/dang/ cua may `tho` theo tung loai."""
    goc_hd = thu_muc_hang_doi(wt)
    tm_dang = goc_hd / "dang"
    dem: dict[str, int] = {}
    if not tm_dang.is_dir():
        return dem
    tho_chuan = tho.strip().lower()
    for tep in sorted(tm_dang.glob("*.md"), key=lambda p: p.name):
        try:
            noi_dung = tep.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        viec = phan_tich_phieu(noi_dung, tep.stem)
        nhan_raw = str(viec["meta"].get("nhan") or "").strip()
        if nhan_raw:
            may_giu = nhan_raw.split()[0].strip().lower()
        elif viec["may"] != "bat-ky":
            may_giu = viec["may"]
        else:
            may_giu = ""
        if may_giu == tho_chuan:
            loai = viec["loai"]
            dem[loai] = dem.get(loai, 0) + 1
    return dem


def co_the_nhan_loai(loai: str, dem_dang_chay: dict[str, int], so_phieu_code: int = SO_PHIEU_CODE_MAC_DINH) -> bool:
    """Kiem tra gioi han song song tren 1 may:
    - Moi may toi da 1 phieu `trinh-duyet` mot luc (computer use chiem chuot, ban phim, man hinh).
    - Moi may toi da `LINHX_SO_PHIEU` phieu `code` chay song song (mac dinh 1).
    """
    loai_chuan = (loai or "code").strip().lower()
    if loai_chuan in ("trinh_duyet", "browser"):
        loai_chuan = "trinh-duyet"
    if loai_chuan == "trinh-duyet":
        return dem_dang_chay.get("trinh-duyet", 0) < SO_PHIEU_TRINH_DUYET_TOI_DA
    if loai_chuan == "code":
        return dem_dang_chay.get("code", 0) < max(0, int(so_phieu_code))
    return dem_dang_chay.get(loai_chuan, 0) < max(1, int(so_phieu_code))


def read_result_status(wt: Path, dep_id: str) -> str | None:
    # Đọc `trang_thai` từ `hang-doi/xong/<id>/KET-QUA.md`; trả về None nếu chưa có hoặc id không hợp lệ
    clean_id = str(dep_id or "").strip()
    if not clean_id or "/" in clean_id or "\\" in clean_id or ".." in clean_id:
        return None
    goc_hd = thu_muc_hang_doi(wt)
    result_file = goc_hd / "xong" / clean_id / "KET-QUA.md"
    if not result_file.is_file():
        return None
    try:
        content = result_file.read_text(encoding="utf-8", errors="replace").lstrip("\ufeff")
    except OSError:
        return None
    lines = content.splitlines()
    header_lines: list[str] = []
    if lines and lines[0].strip() == "---":
        for idx in range(1, len(lines)):
            if lines[idx].strip() == "---":
                header_lines = lines[1:idx]
                break
    else:
        for line in lines:
            if not line.strip():
                break
            if not _KHOA_DAU_DONG.match(line.strip()):
                break
            header_lines.append(line)
    for line in header_lines:
        m = _KHOA_DAU_DONG.match(line.strip())
        if m and m.group(1).lower() == "trang_thai":
            return m.group(2).split("#", 1)[0].strip().lower()
    return ""


def are_dependencies_met(wt: Path, dependencies: list[str] | tuple[str, ...]) -> bool:
    # Mọi id trong `phu_thuoc` đều phải có `xong/<id>/KET-QUA.md` với `trang_thai: xong`.
    # Nếu chưa xong hoặc kết thúc `loi`/`dung` thì bỏ qua (không nhận phiếu, không ghi KET-QUA).
    if not dependencies:
        return True
    for dep_id in dependencies:
        if read_result_status(wt, dep_id) != "xong":
            return False
    return True


def is_machine_error(trang_thai: str, ket_qua, nhat_ky: str = "") -> bool:
    # Nhận diện lỗi máy (thiếu agy, HTTP 429 / hết hạn mức) để không sinh phiếu tự sửa vô ích
    if trang_thai not in ("loi", "dung"):
        return False
    combined = f"{ket_qua or ''}\n{nhat_ky or ''}"
    lowered = combined.lower()
    for pattern in _MACHINE_ERROR_PATTERNS:
        if pattern in lowered:
            return True
    scrubbed = _NON_HTTP_429_CONTEXT_RE.sub("", combined)
    if _HTTP_429_RE.search(scrubbed):
        return True
    return False


def extract_original_prompt(prompt_text: str) -> str:
    # Tách lấy phần đề gốc (bỏ mục "Lần trước trượt vì:" của lượt sửa trước nếu có)
    parts = _SELF_REPAIR_SECTION_SPLIT_RE.split(str(prompt_text or "").strip(), maxsplit=1)
    return parts[0].strip()


def next_self_repair_id(wt: Path, ticket_id: str) -> str:
    # Tính mã phiếu tự sửa kế tiếp `<id>-sua-<k>` (k tăng dần 1, 2, 3...)
    match = _SELF_REPAIR_SUFFIX_RE.match(ticket_id)
    if match:
        base_id = match.group(1)
        next_index = int(match.group(2)) + 1
    else:
        base_id = ticket_id
        next_index = 1
    goc_hd = thu_muc_hang_doi(wt)
    while (
        (goc_hd / "moi" / f"{base_id}-sua-{next_index}.md").exists()
        or (goc_hd / "dang" / f"{base_id}-sua-{next_index}.md").exists()
        or (goc_hd / "xong" / f"{base_id}-sua-{next_index}").exists()
    ):
        next_index += 1
    return f"{base_id}-sua-{next_index}"


def build_self_repair_ticket(viec: dict, ket_qua_md: str) -> str | None:
    # Tạo nội dung phiếu `hang-doi/moi/<id>-sua-<k>.md`: giữ nguyên header (giảm `tu_sua` đi 1),
    # thân = đề gốc + mục "Lần trước trượt vì:" chép 1500 ký tự cuối KET-QUA.
    raw_tu_sua = viec.get("tu_sua") if "tu_sua" in viec else (viec.get("meta") or {}).get("tu_sua")
    current_retries = parse_self_repair_count(raw_tu_sua)
    if current_retries <= 0:
        return None
    remaining = current_retries - 1

    meta = dict(viec.get("meta") or {})
    meta.pop("nhan", None)
    header_lines: list[str] = []
    has_may = False
    has_tu_sua = False
    for key, val in meta.items():
        if key == "tu_sua":
            header_lines.append(f"tu_sua: {remaining}")
            has_tu_sua = True
        else:
            if key == "may":
                has_may = True
            header_lines.append(f"{key}: {val}")
    if not has_may and viec.get("may"):
        header_lines.insert(0, f"may: {viec['may']}")
    if not has_tu_sua:
        header_lines.append(f"tu_sua: {remaining}")

    original_body = extract_original_prompt(viec.get("de") or viec.get("viec") or "")
    excerpt = str(ket_qua_md or "")[-SELF_REPAIR_EXCERPT_LIMIT:]
    if excerpt and not excerpt.endswith("\n"):
        excerpt += "\n"
    body = f"{original_body}\n\n## {SELF_REPAIR_SECTION_TITLE}\n{excerpt}"
    return "\n".join(header_lines) + "\n\n" + body


def chon_ung_vien(
    wt: Path,
    tho: str,
    so_phieu_code: int | None = None,
    cfg: dict | None = None,
    nhan_bat_ky: bool | None = None,
) -> list[tuple[Path, dict]]:
    goc_hd = thu_muc_hang_doi(wt)
    tm_moi = goc_hd / "moi"
    if not tm_moi.is_dir():
        return []
    tho_chuan = tho.strip().lower()
    so_phieu = lay_so_phieu_toi_da(cfg) if so_phieu_code is None else max(0, int(so_phieu_code))
    cho_bat_ky = co_nhan_bat_ky(cfg) if nhan_bat_ky is None else linhx_runner._ep_cong_tac(nhan_bat_ky, bool(NHAN_BAT_KY_MAC_DINH))
    dem_dang = dem_phieu_dang_chay(wt, tho_chuan)
    rieng, chung = [], []
    for tep in sorted(tm_moi.glob("*.md"), key=lambda p: p.name):
        noi_dung = tep.read_text(encoding="utf-8", errors="replace")
        viec = phan_tich_phieu(noi_dung, tep.stem)
        if not co_the_nhan_loai(viec["loai"], dem_dang, so_phieu):
            continue
        if not are_dependencies_met(wt, viec.get("phu_thuoc") or ()):
            continue
        if viec["may"] == tho_chuan:
            rieng.append((tep, viec))
        elif cho_bat_ky and viec["may"] == "bat-ky":
            chung.append((tep, viec))
    return rieng + chung


def _commit_git(wt: Path, tho: str, thong_diep: str):
    chay_git(["add", "-A"], cwd=wt)
    chay_git(
        [
            "-c", f"user.name={tho}",
            "-c", f"user.email={tho}@linhx.local",
            "-c", "commit.gpgsign=false",
            "commit", "-m", thong_diep,
        ],
        cwd=wt,
    )


def nhan_phieu_git(cfg: dict):
    """Keo nhanh hang-doi, chon phieu phu hop va giu phieu bang commit + push."""
    ok_ram, ram_gb = du_ram_nhan_viec(cfg)
    if not ok_ram:
        nguong = cfg.get("nguong_ram_gb", NGUONG_RAM_TRONG_GB)
        linhx_runner.log(f"RAM trong {ram_gb:.2f} GB < {nguong} GB, khong nhan phieu")
        return None
    _, _, remote, nhanh = _duong_dan_wt(cfg)
    tho = cfg["tho"]
    with _khoa_tep(_duong_dan_khoa_wt(cfg)):
        for lan in range(SO_LAN_THU_PUSH):
            ok_ram, ram_gb = du_ram_nhan_viec(cfg)
            if not ok_ram:
                return None
            wt = dam_bao_worktree(cfg)
            if wt is None:
                return None
            ung_vien = chon_ung_vien(wt, tho, cfg=cfg)
            if not ung_vien:
                return None
            tep_moi, viec = ung_vien[0]
            goc_hd = thu_muc_hang_doi(wt)
            tm_dang = goc_hd / "dang"
            tm_dang.mkdir(parents=True, exist_ok=True)
            tep_dang = tm_dang / tep_moi.name

            noi_dung_moi = chen_dong_nhan(tep_moi.read_text(encoding="utf-8", errors="replace"), tho)
            tep_moi.unlink()
            tep_dang.write_text(noi_dung_moi, encoding="utf-8")

            _commit_git(wt, tho, f"nhan: {viec['viec']} ({tho})")
            push = chay_git(["push", remote, f"HEAD:refs/heads/{nhanh}"], cwd=wt, check=False)
            if push.returncode == 0:
                return viec
            linhx_runner.log("tranh phieu", viec["viec"], "push bi tu choi, keo lai")
            time.sleep(random.uniform(0.02, 0.08) * (lan + 1))
    return None


def _xac_dinh_model_cho_ket_qua(cfg: dict, viec: dict) -> tuple[str, str]:
    # Trả về (model_that_dung, canh_bao_model) để ghi vào đầu KET-QUA.md
    if isinstance(viec, dict) and viec.get("_model_da_dung"):
        return str(viec["_model_da_dung"]), str(viec.get("_canh_bao_model") or "")
    kq_m = linhx_runner.chon_model_phieu(cfg, viec)
    return kq_m["model_that"], kq_m["canh_bao"]


def bao_ket_qua_git(
    cfg: dict,
    viec: dict,
    trang_thai: str,
    ket_qua,
    nhat_ky: str = "",
    token_vao: int = 0,
    token_ra: int = 0,
    phut: float = 0.0,
    tep_doi=None,
    drive: str = "",
    model: str = "",
    canh_bao: str = "",
) -> Path:
    """Xoa dang/<id>.md, ghi xong/<id>/KET-QUA.md va push len remote."""
    _, _, remote, nhanh = _duong_dan_wt(cfg)
    tho = cfg["tho"]
    phieu_id = viec["viec"]
    tt_chuan = trang_thai if trang_thai in ("xong", "loi", "dung") else "loi"
    model_tu_viec, canh_bao_tu_viec = _xac_dinh_model_cho_ket_qua(cfg, viec)
    model_ghi = model if model and str(model).strip() else model_tu_viec
    canh_bao_ghi = canh_bao if canh_bao and str(canh_bao).strip() else canh_bao_tu_viec
    noi_dung_kq = tao_ket_qua_md(
        phieu_id=phieu_id,
        tho=tho,
        trang_thai=tt_chuan,
        ket_qua=ket_qua,
        nhat_ky=nhat_ky,
        phut=phut,
        token_vao=token_vao,
        token_ra=token_ra,
        tep_doi=tep_doi,
        drive=drive,
        model=model_ghi,
        canh_bao=canh_bao_ghi,
    )
    can_linh_cap = trich_khoi_can_linh(str(ket_qua or "") + "\n" + str(nhat_ky or ""))
    noi_dung_can_linh = (
        tao_can_linh_md(phieu_id, tho, can_linh_cap[0], can_linh_cap[1])
        if can_linh_cap is not None
        else None
    )
    can_sua = (
        tt_chuan in ("loi", "dung")
        and noi_dung_can_linh is None
        and not is_machine_error(tt_chuan, ket_qua, nhat_ky)
    )
    loi_cuoi = ""
    with _khoa_tep(_duong_dan_khoa_wt(cfg)):
        for lan in range(SO_LAN_THU_PUSH):
            wt = dam_bao_worktree(cfg)
            if wt is None:
                raise RuntimeError(f"Khong tim thay nhanh {nhanh} khi bao ket qua {phieu_id}")
            goc_hd = thu_muc_hang_doi(wt)
            tep_dang = goc_hd / "dang" / f"{phieu_id}.md"
            viec_nguon = viec
            if tep_dang.is_file() and "tu_sua" not in viec and "meta" not in viec:
                viec_nguon = phan_tich_phieu(tep_dang.read_text(encoding="utf-8", errors="replace"), phieu_id)
            if tep_dang.exists():
                tep_dang.unlink()
            tep_kq = goc_hd / "xong" / phieu_id / "KET-QUA.md"
            tep_kq.parent.mkdir(parents=True, exist_ok=True)
            tep_kq.write_text(noi_dung_kq, encoding="utf-8")

            thong_diep = f"xong: {phieu_id} ({tt_chuan})"
            if noi_dung_can_linh is not None:
                tm_can_linh = goc_hd / "can-linh"
                tm_can_linh.mkdir(parents=True, exist_ok=True)
                (tm_can_linh / f"{_ten_phieu_an_toan(phieu_id)}.md").write_text(
                    noi_dung_can_linh,
                    encoding="utf-8",
                )
                thong_diep = f"{thong_diep} [can-linh]"
            if can_sua:
                noi_dung_sua = build_self_repair_ticket(viec_nguon, noi_dung_kq)
                if noi_dung_sua is not None:
                    ma_phieu_sua = next_self_repair_id(wt, phieu_id)
                    tm_moi = goc_hd / "moi"
                    tm_moi.mkdir(parents=True, exist_ok=True)
                    (tm_moi / f"{ma_phieu_sua}.md").write_text(noi_dung_sua, encoding="utf-8")
                    thong_diep = f"{thong_diep} -> {ma_phieu_sua}"

            _commit_git(wt, tho, thong_diep)
            push = chay_git(["push", remote, f"HEAD:refs/heads/{nhanh}"], cwd=wt, check=False)
            if push.returncode == 0:
                return tep_kq
            loi_cuoi = (push.stderr or push.stdout or "").strip()
            time.sleep(0.05 * (lan + 1))
    raise RuntimeError(f"Khong push duoc KET-QUA.md cho {phieu_id}: {loi_cuoi}")


def _chup_trang_thai_thu_muc(thu_muc: Path) -> dict[str, tuple[int, int]]:
    ket_qua = {}
    if not thu_muc.is_dir():
        return ket_qua
    try:
         cac_muc = list(thu_muc.rglob("*"))
    except OSError:
        return ket_qua
    for p in cac_muc:
        try:
            if not p.is_file():
                continue
            rel = p.relative_to(thu_muc).as_posix()
            if rel.startswith(".git/") or rel == ".git":
                continue
            st = p.stat()
            ket_qua[rel] = (st.st_mtime_ns, st.st_size)
        except OSError:
            pass
    return ket_qua


def _la_tep_tam_de(rel: str, bo_qua: set[str]) -> bool:
    if rel in bo_qua:
        return True
    return "/" not in rel and rel.startswith("de-") and rel.endswith(".md")


def _tim_tep_moi_hoac_sua(truoc: dict, sau: dict, bo_qua: set[str]) -> list[str]:
    return [k for k, v in sorted(sau.items()) if not _la_tep_tam_de(k, bo_qua) and truoc.get(k) != v]


def _tim_tep_doi(truoc: dict, sau: dict, bo_qua: set[str], gioi_han_tep: int | None = 20) -> list[str]:
    doi = _tim_tep_moi_hoac_sua(truoc, sau, bo_qua)
    for k in sorted(truoc.keys()):
        if not _la_tep_tam_de(k, bo_qua) and k not in sau:
            doi.append(f"{k} (xoa)")
    return doi[:gioi_han_tep] if gioi_han_tep is not None else doi


def _ghi_log_an_toan(tep_log: Path, su_kien: str, **truong):
    try:
        ghi_log_phieu(tep_log, su_kien, **truong)
    except OSError as e:
        linhx_runner.log("canh bao log", tep_log, e)


def thuc_thi_phieu_da_nhan(cfg: dict, viec: dict, chay_agy_fn=None):
    """Chay agy cho 1 phieu da giu trong dang/, chep Drive, ghi log jsonl va push KET-QUA.md."""
    phieu_id = viec["viec"]
    linhx_runner.log("nhan", phieu_id, viec["loai"], viec["may"])
    thu_muc = Path(cfg["thu_muc"])
    thu_muc.mkdir(parents=True, exist_ok=True)
    tep_log = duong_dan_log_phieu(phieu_id, cfg)

    bo_qua = {f"de-{phieu_id}.md"}
    try:
        bo_qua.add(tep_log.resolve().relative_to(thu_muc.resolve()).as_posix())
    except (OSError, ValueError):
        pass

    truoc = _chup_trang_thai_thu_muc(thu_muc)
    _ghi_log_an_toan(
        tep_log,
        "nhan",
        viec=phieu_id,
        may=cfg["tho"],
        loai=viec["loai"],
        che_do=viec["che_do"],
        tran_phut=viec["tran_phut"],
        de=viec["de"],
    )

    ham_agy = _lay_ham_chay_agy(chay_agy_fn)
    if ham_agy is linhx_runner.chay_agy:
        def _callback_nhip(phut_chay: float, dong_cuoi: str) -> None:
            ghi_nhip_phieu_git(cfg, phieu_id, phut_chay, dong_cuoi)

        cfg_agy = {**cfg, "_tep_log_phieu": tep_log, "_ghi_nhip_fn": _callback_nhip}
    else:
        cfg_agy = cfg
    t0 = time.monotonic()
    try:
        tt, kq, nk, tv, tr = ham_agy(cfg_agy, viec)
    except Exception:
        tt, kq, nk, tv, tr = "loi", None, traceback.format_exc(), 0, 0
    phut = (time.monotonic() - t0) / 60.0

    sau = _chup_trang_thai_thu_muc(thu_muc)
    tep_moi_sua = _tim_tep_moi_hoac_sua(truoc, sau, bo_qua)
    tat_ca_tep_doi = _tim_tep_doi(truoc, sau, bo_qua, gioi_han_tep=None)
    tep_doi = tat_ca_tep_doi[:20]

    tep_da_chep: list[Path] = []
    drive_str = ""
    try:
        tep_da_chep = chep_tep_nang_sang_drive(
            thu_muc,
            phieu_id,
            thu_muc_drive=_thu_muc_drive(cfg),
            chi_cac_tep=tep_moi_sua,
            nguong_byte=cfg.get("nguong_tep_nang"),
            bo_qua=bo_qua,
        )
        drive_str = dinh_dang_duong_dan_drive(tep_da_chep)
    except OSError as e:
        linhx_runner.log("loi chep Drive", phieu_id, e)
        drive_str = f"(loi chep Drive: {e})"

    _ghi_log_an_toan(
        tep_log,
        "ket_qua",
        viec=phieu_id,
        may=cfg["tho"],
        trang_thai=tt,
        phut=round(phut, 4),
        token_vao=int(tv or 0),
        token_ra=int(tr or 0),
        tep_doi=tat_ca_tep_doi,
        tep_drive=[str(p) for p in tep_da_chep],
        drive=drive_str,
        ket_qua=kq,
        nhat_ky=nk,
    )

    tep_kq = bao_ket_qua_git(
        cfg,
        viec,
        trang_thai=tt,
        ket_qua=kq,
        nhat_ky=nk,
        token_vao=tv,
        token_ra=tr,
        phut=phut,
        tep_doi=tep_doi,
        drive=drive_str,
    )
    _ghi_log_an_toan(
        tep_log,
        "bao_ket_qua",
        viec=phieu_id,
        may=cfg["tho"],
        trang_thai=tt,
        tep_ket_qua=str(tep_kq),
    )
    linhx_runner.log("xong", phieu_id, tt)
    return {
        "viec": phieu_id,
        "trang_thai": tt,
        "ket_qua": kq,
        "nhat_ky": nk,
        "token_vao": tv,
        "token_ra": tr,
        "phut": phut,
        "tep_doi": tep_doi,
        "drive": drive_str,
        "tep_drive": [str(p) for p in tep_da_chep],
        "tep_log": str(tep_log),
    }


def xu_ly_mot_phieu(cfg: dict, chay_agy_fn=None):
    """Nhan toi da 1 phieu, chay agy, chep file nang sang Drive, ghi log jsonl va push KET-QUA.md."""
    viec = nhan_phieu_git(cfg)
    if not viec:
        return None
    return thuc_thi_phieu_da_nhan(cfg, viec, chay_agy_fn=chay_agy_fn)


def _co_nen_kiem_ho_so_may(cfg: dict, chu_ky_giay: float) -> bool:
    """Chống đọc/fetch thừa mỗi phút khi chạy qua Task Scheduler (`--mot-lan`), chỉ kiểm lúc mới khởi động hoặc mỗi 60 phút."""
    tho_an_toan = _ten_phieu_an_toan(str(cfg.get("tho") or "may"))
    repo = Path(cfg.get("repo_hang_doi") or linhx_runner.GOC.parent).resolve()
    tep_dau = repo.parent / f".{repo.name}-{tho_an_toan}-ho-so.stamp"
    bay_gio = time.time()
    try:
        if tep_dau.is_file():
            lan_truoc = float(tep_dau.read_text(encoding="utf-8").strip() or "0")
            if 0 <= (bay_gio - lan_truoc) < chu_ky_giay:
                return False
        tep_dau.write_text(f"{bay_gio:.3f}\n", encoding="utf-8")
    except (OSError, ValueError):
        pass
    return True


def vong_git(cfg: dict, mot_lan: bool = False, mot_viec: bool = False, chay_agy_fn=None):
    linhx_runner.log(
        f"linhx-runner {linhx_runner.PHIEN_BAN} tho={cfg['tho']} nguon=github "
        f"nhanh={cfg.get('nhanh_hang_doi', NHANH_MAC_DINH)} so_phieu={lay_so_phieu_toi_da(cfg)}"
    )
    chu_ky_ho_so_phut = linhx_runner._ep_so_duong(
        cfg.get("ho_so_phut"),
        linhx_runner._ep_so_duong(os.environ.get("LINHX_HO_SO_PHUT"), HO_SO_CHU_KY_PHUT_MAC_DINH),
    )
    chu_ky_ho_so_giay = chu_ky_ho_so_phut * 60.0
    if not mot_lan or _co_nen_kiem_ho_so_may(cfg, chu_ky_ho_so_giay):
        cap_nhat_ho_so_may_git(cfg)
    moc_ho_so_cuoi = linhx_runner._gio()

    if mot_viec:
        while True:
            if (linhx_runner._gio() - moc_ho_so_cuoi) >= chu_ky_ho_so_giay:
                moc_ho_so_cuoi = linhx_runner._gio()
                cap_nhat_ho_so_may_git(cfg)
            try:
                kq = xu_ly_mot_phieu(cfg, chay_agy_fn=chay_agy_fn)
                if kq is not None:
                    return kq
            except Exception:
                linhx_runner.log("loi", traceback.format_exc()[-800:])
            if mot_lan:
                return None
            time.sleep(cfg["nghi"])

    dang_chay: list[threading.Thread] = []
    su_kien_xong = threading.Event()

    while True:
        if (linhx_runner._gio() - moc_ho_so_cuoi) >= chu_ky_ho_so_giay:
            moc_ho_so_cuoi = linhx_runner._gio()
            cap_nhat_ho_so_may_git(cfg)
        dang_chay = [t for t in dang_chay if t.is_alive()]
        su_kien_xong.clear()
        viec = None
        try:
            viec = nhan_phieu_git(cfg)
        except Exception:
            linhx_runner.log("loi", traceback.format_exc()[-800:])

        if viec is not None:
            def _chay_cong_viec(v=viec):
                try:
                    thuc_thi_phieu_da_nhan(cfg, v, chay_agy_fn=chay_agy_fn)
                except Exception:
                    linhx_runner.log("loi", traceback.format_exc()[-800:])
                finally:
                    su_kien_xong.set()

            luong = threading.Thread(target=_chay_cong_viec, name=f"phieu-{viec['viec']}", daemon=True)
            luong.start()
            dang_chay.append(luong)
            continue

        dang_chay = [t for t in dang_chay if t.is_alive()]
        if dang_chay:
            if not su_kien_xong.is_set():
                thoi_gian_cho = 5.0 if mot_lan else max(0.01, float(cfg.get("nghi", 15)))
                su_kien_xong.wait(timeout=thoi_gian_cho)
            continue

        if su_kien_xong.is_set():
            continue

        if mot_lan:
            return None
        time.sleep(cfg["nghi"])
