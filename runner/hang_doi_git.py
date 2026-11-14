"""Nguon viec GitHub (nhanh hang-doi) cho linhx-runner.

Cau truc tren nhanh `hang-doi`:
  hang-doi/moi/<id>.md            phieu cho (may: may-1|may-2|may-3|bat-ky; loai: code|trinh-duyet|khac)
  hang-doi/dang/<id>.md           da co may nhan (them dong nhan: <may> <gio>)
  hang-doi/xong/<id>/KET-QUA.md   trang thai (xong|loi|dung), file da doi, duong dan Drive, phut, token
"""
from __future__ import annotations

from contextlib import contextmanager
import os
import re
import shutil
import stat
import subprocess
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
SO_LAN_THU_PUSH = 5
_KHOA_DAU_DONG = re.compile(r"^([a-zA-Z0-9_-]+)\s*:\s*(.*)$")

_CHAY_AGY_GOC = linhx_runner.chay_agy
chay_agy = _CHAY_AGY_GOC


def _lay_ham_chay_agy(chay_agy_fn=None):
    if chay_agy_fn is not None:
        return chay_agy_fn
    if chay_agy is not _CHAY_AGY_GOC:
        return chay_agy
    return linhx_runner.chay_agy


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
    che_do = (meta.get("che_do") or "thuc").strip().lower()
    tran_raw = str(meta.get("tran_phut") or "").strip()
    try:
        tran_phut = int(tran_raw) if tran_raw else 40
    except ValueError:
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
    tt = trang_thai if trang_thai in ("xong", "loi", "dung") else "loi"
    ds_tep = ", ".join(tep_doi) if tep_doi else "(khong)"
    duong_drive = drive.strip() if drive else "(khong)"
    dau = (
        f"phieu: {phieu_id}\n"
        f"may: {tho}\n"
        f"trang_thai: {tt}\n"
        f"tep_doi: {ds_tep}\n"
        f"drive: {duong_drive}\n"
        f"phut: {phut:.2f}\n"
        f"token: vao={int(token_vao)} ra={int(token_ra)}\n\n"
    )
    than = (ket_qua if ket_qua is not None and str(ket_qua).strip() else nhat_ky or "").strip()
    toan_bo = dau + than + ("\n" if than else "")
    if len(toan_bo) <= gioi_han:
        return toan_bo
    duoi_cat = "\n...[cat bot]\n"
    con_lai = max(0, gioi_han - len(dau) - len(duoi_cat))
    return dau + than[:con_lai] + duoi_cat


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


def chon_ung_vien(wt: Path, tho: str) -> list[tuple[Path, dict]]:
    goc_hd = thu_muc_hang_doi(wt)
    tm_moi = goc_hd / "moi"
    if not tm_moi.is_dir():
        return []
    tho_chuan = tho.strip().lower()
    rieng, chung = [], []
    for tep in sorted(tm_moi.glob("*.md"), key=lambda p: p.name):
        noi_dung = tep.read_text(encoding="utf-8", errors="replace")
        viec = phan_tich_phieu(noi_dung, tep.stem)
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
    _, _, remote, nhanh = _duong_dan_wt(cfg)
    tho = cfg["tho"]
    with _khoa_tep(_duong_dan_khoa_wt(cfg)):
        for _ in range(SO_LAN_THU_PUSH):
            wt = dam_bao_worktree(cfg)
            if wt is None:
                return None
            ung_vien = chon_ung_vien(wt, tho)
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
    for p in thu_muc.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(thu_muc).as_posix()
        if rel.startswith(".git/") or rel == ".git":
            continue
        try:
            st = p.stat()
            ket_qua[rel] = (st.st_mtime_ns, st.st_size)
        except OSError:
            pass
    return ket_qua


def _tim_tep_doi(truoc: dict, sau: dict, bo_qua: set[str]) -> list[str]:
    doi = []
    for k, v in sorted(sau.items()):
        if k in bo_qua:
            continue
        if truoc.get(k) != v:
            doi.append(k)
    for k in sorted(truoc.keys()):
        if k not in bo_qua and k not in sau:
            doi.append(f"{k} (xoa)")
    return doi[:20]


def xu_ly_mot_phieu(cfg: dict, chay_agy_fn=None):
    """Nhan toi da 1 phieu, chay agy va ghi KET-QUA.md len nhanh hang-doi."""
    viec = nhan_phieu_git(cfg)
    if not viec:
        return None
    phieu_id = viec["viec"]
    linhx_runner.log("nhan", phieu_id, viec["loai"], viec["may"])
    thu_muc = Path(cfg["thu_muc"])
    thu_muc.mkdir(parents=True, exist_ok=True)
    truoc = _chup_trang_thai_thu_muc(thu_muc)
    ham_agy = _lay_ham_chay_agy(chay_agy_fn)
    t0 = time.monotonic()
    try:
        tt, kq, nk, tv, tr = ham_agy(cfg, viec)
    except Exception:
        tt, kq, nk, tv, tr = "loi", None, traceback.format_exc()[-4000:], 0, 0
    phut = (time.monotonic() - t0) / 60.0
    sau = _chup_trang_thai_thu_muc(thu_muc)
    tep_doi = _tim_tep_doi(truoc, sau, {f"de-{phieu_id}.md"})

    bao_ket_qua_git(
        cfg,
        viec,
        trang_thai=tt,
        ket_qua=kq,
        nhat_ky=nk,
        token_vao=tv,
        token_ra=tr,
        phut=phut,
        tep_doi=tep_doi,
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
    }


def vong_git(cfg: dict, mot_lan: bool = False, mot_viec: bool = False, chay_agy_fn=None):
    linhx_runner.log(
        f"linhx-runner {linhx_runner.PHIEN_BAN} tho={cfg['tho']} nguon=github "
        f"nhanh={cfg.get('nhanh_hang_doi', NHANH_MAC_DINH)}"
    )
    while True:
        try:
            kq = xu_ly_mot_phieu(cfg, chay_agy_fn=chay_agy_fn)
            if kq is not None:
                if mot_viec:
                    return kq
                continue
        except Exception:
            linhx_runner.log("loi", traceback.format_exc()[-800:])
        if mot_lan:
            return None
        time.sleep(cfg["nghi"])
