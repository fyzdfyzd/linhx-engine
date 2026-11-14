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

NHANH_MAC_DINH = "hang-doi"
REMOTE_MAC_DINH = "origin"
GIOI_HAN_KET_QUA = 2000
NGUONG_TEP_NANG = 1024 * 1024  # 1 MB
THU_MUC_DRIVE_MAC_DINH = Path(r"G:\My Drive\LINHX-VIEC")
THU_MUC_LOG_MAC_DINH = Path(r"D:\linhx\linhx-runner\log")
DUONG_DAN_PHIEU_PING_MAU = linhx_runner.GOC / "phieu-mau" / "ping.md"
SO_LAN_THU_PUSH = 8
SO_PHIEU_TRINH_DUYET_TOI_DA = 1
SO_PHIEU_CODE_MAC_DINH = linhx_runner.SO_PHIEU_CODE_MAC_DINH
NGUONG_RAM_TRONG_GB = linhx_runner.NGUONG_RAM_TRONG_GB
_KHOA_DAU_DONG = re.compile(r"^([a-zA-Z0-9_-]+)\s*:\s*(.*)$")

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
    phan = [p.strip() for p in dong.split(";") if p.strip()]
    ket_qua = []
    for p in phan:
        mp = _KHOA_DAU_DONG.match(p)
        if not mp:
            return [(m.group(1).lower(), m.group(2).strip())]
        ket_qua.append((mp.group(1).lower(), mp.group(2).strip()))
    return ket_qua


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

    may = (meta.get("may") or "bat-ky").strip().lower()
    if may in ("*", "all", "tat-ca"):
        may = "bat-ky"
    loai = (meta.get("loai") or "code").strip().lower()
    if loai in ("trinh_duyet", "browser"):
        loai = "trinh-duyet"
    che_do = (meta.get("che_do") or "thuc").strip().lower()
    tran_raw = str(meta.get("tran_phut") or "").strip()
    if tran_raw:
        try:
            tran_f = float(tran_raw)
            tran_phut = int(tran_f) if tran_f.is_integer() else tran_f
        except ValueError:
            tran_phut = 40
    else:
        tran_phut = 40

    return {
        "viec": ma_phieu,
        "may": may,
        "loai": loai,
        "che_do": che_do,
        "tran_phut": tran_phut,
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
) -> str:
    if gioi_han <= 0:
        return ""
    tt = trang_thai if trang_thai in ("xong", "loi", "dung") else "loi"
    ds_tep = _cat_mot_dong(", ".join(tep_doi), 300) if tep_doi else "(khong)"
    duong_drive = _cat_mot_dong(drive, 350) if drive and str(drive).strip() else "(khong)"
    dau = (
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


def chon_ung_vien(
    wt: Path,
    tho: str,
    so_phieu_code: int | None = None,
    cfg: dict | None = None,
) -> list[tuple[Path, dict]]:
    goc_hd = thu_muc_hang_doi(wt)
    tm_moi = goc_hd / "moi"
    if not tm_moi.is_dir():
        return []
    tho_chuan = tho.strip().lower()
    so_phieu = lay_so_phieu_toi_da(cfg) if so_phieu_code is None else max(0, int(so_phieu_code))
    dem_dang = dem_phieu_dang_chay(wt, tho_chuan)
    rieng, chung = [], []
    for tep in sorted(tm_moi.glob("*.md"), key=lambda p: p.name):
        noi_dung = tep.read_text(encoding="utf-8", errors="replace")
        viec = phan_tich_phieu(noi_dung, tep.stem)
        if not co_the_nhan_loai(viec["loai"], dem_dang, so_phieu):
            continue
        if viec["may"] == tho_chuan:
            rieng.append((tep, viec))
        elif viec["may"] == "bat-ky":
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
) -> Path:
    """Xoa dang/<id>.md, ghi xong/<id>/KET-QUA.md va push len remote."""
    _, _, remote, nhanh = _duong_dan_wt(cfg)
    tho = cfg["tho"]
    phieu_id = viec["viec"]
    noi_dung_kq = tao_ket_qua_md(
        phieu_id=phieu_id,
        tho=tho,
        trang_thai=trang_thai,
        ket_qua=ket_qua,
        nhat_ky=nhat_ky,
        phut=phut,
        token_vao=token_vao,
        token_ra=token_ra,
        tep_doi=tep_doi,
        drive=drive,
    )
    loi_cuoi = ""
    with _khoa_tep(_duong_dan_khoa_wt(cfg)):
        for lan in range(SO_LAN_THU_PUSH):
            wt = dam_bao_worktree(cfg)
            if wt is None:
                raise RuntimeError(f"Khong tim thay nhanh {nhanh} khi bao ket qua {phieu_id}")
            goc_hd = thu_muc_hang_doi(wt)
            tep_dang = goc_hd / "dang" / f"{phieu_id}.md"
            if tep_dang.exists():
                tep_dang.unlink()
            tep_kq = goc_hd / "xong" / phieu_id / "KET-QUA.md"
            tep_kq.parent.mkdir(parents=True, exist_ok=True)
            tep_kq.write_text(noi_dung_kq, encoding="utf-8")

            _commit_git(wt, tho, f"xong: {phieu_id} ({trang_thai})")
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
    cfg_agy = {**cfg, "_tep_log_phieu": tep_log} if ham_agy is linhx_runner.chay_agy else cfg
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


def vong_git(cfg: dict, mot_lan: bool = False, mot_viec: bool = False, chay_agy_fn=None):
    linhx_runner.log(
        f"linhx-runner {linhx_runner.PHIEN_BAN} tho={cfg['tho']} nguon=github "
        f"nhanh={cfg.get('nhanh_hang_doi', NHANH_MAC_DINH)} so_phieu={lay_so_phieu_toi_da(cfg)}"
    )
    if mot_viec:
        while True:
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
