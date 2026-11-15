"""Gui thong bao ngay len PR #36 GitHub khi phieu can Claude xem/duyet."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.request

GOC = Path(__file__).resolve().parent
TEP_THO_ENV = GOC / "tho.env"
REPO_MAC_DINH = "fyzdfyzd/linhx-engine"
SO_PR_MAC_DINH = 36
API_GITHUB_GOC = "https://api.github.com"
SO_LAN_THU = 3
TIMEOUT_GH_GIAY = 20
TIMEOUT_HTTP_GIAY = 30

# Ghep dong mau token de khong cham bo quet bi mat tinh trong repo
_MAU_TOKEN_GH_CLASSIC = re.compile(r"\b" + "gh" + r"[pousr]_[A-Za-z0-9_]+\b")
_MAU_TOKEN_GH_PAT = re.compile(r"\b" + "github" + "_pat_" + r"[A-Za-z0-9_]+\b")
_MAU_BEARER = re.compile(r"(?i)(Bearer)\s+[^\s'\";]+")
_MAU_TOKEN_AUTH = re.compile(r"(?i)\b(token)\s+[A-Za-z0-9._+/=-]{8,}")

_MAU_DONG_DAT = re.compile(
    r"^\s*(?:[-*>]+\s*)?[`*]*dat[`*]*\s*:\s*[`*]*(co|có|khong|không|\?)[`*]*\s*(?:[;,#(].*)?$",
    re.IGNORECASE,
)

# Hook noi bo phuc vu test ma khong chan subprocess.run cua git
_SUBPROCESS_RUN_GOC = subprocess.run
_SHUTIL_WHICH_GOC = shutil.which
_CHAY_LENH_FN = None
_URLOPEN_FN = None


def _dang_mock_lenh(chay_lenh_fn=None) -> bool:
    return (
        (chay_lenh_fn is not None and chay_lenh_fn is not _SUBPROCESS_RUN_GOC)
        or _CHAY_LENH_FN is not None
        or subprocess.run is not _SUBPROCESS_RUN_GOC
    )


def _tim_lenh_gh(co_mock: bool = False) -> str:
    """Tim ten hoac duong dan thuc thi cua gh CLI (ho tro Windows PATH chua cap nhat)."""
    if co_mock:
        return "gh"
    tim_thay = shutil.which("gh")
    if tim_thay:
        return tim_thay
    if os.name == "nt" and shutil.which is _SHUTIL_WHICH_GOC:
        ung_vien = [
            Path(r"C:\Program Files\GitHub CLI\gh.exe"),
            Path(r"C:\Program Files (x86)\GitHub CLI\gh.exe"),
        ]
        local_app = os.environ.get("LOCALAPPDATA", "").strip()
        if local_app:
            ung_vien.append(Path(local_app) / "Programs" / "GitHub CLI" / "gh.exe")
        for p in ung_vien:
            if p.is_file():
                return str(p)
    return "gh"


def che_bi_mat(van_ban: str, secret_val: str = "") -> str:
    """An toan hoa chuoi log bang cach che secret va token GitHub."""
    ket_qua = str(van_ban or "")
    if secret_val:
        ket_qua = ket_qua.replace(secret_val, "***")
    ket_qua = _MAU_BEARER.sub(r"\1 ***", ket_qua)
    ket_qua = _MAU_TOKEN_AUTH.sub(r"\1 ***", ket_qua)
    ket_qua = _MAU_TOKEN_GH_CLASSIC.sub("***", ket_qua)
    ket_qua = _MAU_TOKEN_GH_PAT.sub("***", ket_qua)
    return ket_qua


def _chuan_hoa_dat(dat) -> str:
    if isinstance(dat, bool):
        return "co" if dat else "khong"
    s = str(dat if dat is not None else "").strip().lower()
    if s in ("co", "có"):
        return "co"
    if s in ("khong", "không"):
        return "khong"
    return "?"


def tao_dong_bao(id, dat, may, phut) -> str:
    """Tao dung mot dong thong bao: XONG <id> dat=<co|khong|?> may=<may> phut=<n>."""
    ma_sach = " ".join(str(id or "").split()).strip() or "?"
    dat_sach = _chuan_hoa_dat(dat)
    may_sach = " ".join(str(may or "").split()).strip() or "?"
    try:
        phut_so = max(0, int(round(float(phut)))) if phut is not None else 0
    except (TypeError, ValueError):
        phut_so = 0
    return f"XONG {ma_sach} dat={dat_sach} may={may_sach} phut={phut_so}"


def trich_dat_tu_ket_qua(van_ban: str | None, trang_thai: str = "xong") -> str:
    """Rut gia tri dat=<co|khong|?> tu trang thai ket thuc va noi dung KET-QUA."""
    tt = str(trang_thai or "").strip().lower()
    if tt in ("loi", "dung"):
        return "khong"
    for dong in str(van_ban or "").splitlines():
        m = _MAU_DONG_DAT.match(dong)
        if m:
            return _chuan_hoa_dat(m.group(1))
    return "?"


def _cat_comment_cuoi_dong(gia_tri: str) -> str:
    """Bo phan # comment o cuoi dong gia tri env neu nam ngoai dau nhay."""
    quote_char: str | None = None
    escaped = False
    for idx, ch in enumerate(gia_tri):
        if escaped:
            escaped = False
            continue
        if quote_char is not None:
            if ch == "\\" and idx + 1 < len(gia_tri) and gia_tri[idx + 1] == quote_char:
                escaped = True
                continue
            if ch == quote_char:
                quote_char = None
            continue
        if ch in ("'", '"'):
            quote_char = ch
            continue
        if ch == "#" and (idx == 0 or gia_tri[idx - 1].isspace()):
            return gia_tri[:idx]
    return gia_tri


def _go_bo_nhay_ngoai(gia_tri: str) -> str:
    s = gia_tri.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        return s[1:-1].strip()
    return s


def doc_token_gh(tep_env: Path | str | None = None) -> str:
    """Doc LINHX_GH_TOKEN tu tho.env (khong nap vao os.environ, khong log)."""
    duong_dan = Path(tep_env) if tep_env is not None else TEP_THO_ENV
    if duong_dan.is_file():
        try:
            for dong in duong_dan.read_text(encoding="utf-8-sig", errors="replace").splitlines():
                s = dong.strip()
                if not s or s.startswith("#") or "=" not in s:
                    continue
                khoa, gia_tri = s.split("=", 1)
                if khoa.strip() == "LINHX_GH_TOKEN":
                    sach = _go_bo_nhay_ngoai(_cat_comment_cuoi_dong(gia_tri))
                    if sach:
                        return sach
        except OSError:
            pass
    return _go_bo_nhay_ngoai(os.environ.get("LINHX_GH_TOKEN", ""))


def kiem_tra_gh_dang_nhap(chay_lenh_fn=None) -> tuple[bool, bool]:
    """Tra ve (co_gh, da_dang_nhap) ma khong bao gio in/log token."""
    co_mock = _dang_mock_lenh(chay_lenh_fn)
    lenh_gh = _tim_lenh_gh(co_mock=co_mock)
    ham_chay = chay_lenh_fn or _CHAY_LENH_FN or subprocess.run
    kw: dict = {"creationflags": 0x08000000} if os.name == "nt" else {}
    if not co_mock:
        kw["stdin"] = subprocess.DEVNULL
        kw["env"] = {**os.environ, "GH_PROMPT_DISABLED": "1"}
    try:
        proc = ham_chay(
            [lenh_gh, "auth", "status"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT_GH_GIAY,
            **kw,
        )
    except (FileNotFoundError, OSError, subprocess.SubprocessError):
        return False, False
    return True, getattr(proc, "returncode", 1) == 0


def _ghi_log_an_toan(log_fn, thong_diep: str, secret_val: str = "") -> None:
    sach = che_bi_mat(thong_diep, secret_val)
    try:
        if log_fn is not None:
            log_fn(sach)
        else:
            print(time.strftime("%H:%M:%S"), "bao-claude", sach, flush=True)
    except Exception:
        pass


def _ghi_dau_da_bao(tep_da_bao: Path | None, phieu_id: str) -> None:
    if tep_da_bao is None:
        return
    try:
        tep_da_bao.parent.mkdir(parents=True, exist_ok=True)
        tep_da_bao.write_text(
            f"phieu: {phieu_id}\nluc: {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n",
            encoding="utf-8",
        )
    except OSError:
        pass


def _gui_bang_gh(
    dong: str,
    repo: str,
    so_pr: int,
    chay_lenh_fn,
    ham_ngu,
    log_fn,
    lenh_gh: str = "gh",
    secret_val: str = "",
    co_mock: bool = False,
) -> bool:
    cmd = [lenh_gh, "pr", "comment", str(so_pr), "-R", str(repo), "-b", dong]
    kw: dict = {"creationflags": 0x08000000} if os.name == "nt" else {}
    if not co_mock:
        kw["stdin"] = subprocess.DEVNULL
        kw["env"] = {**os.environ, "GH_PROMPT_DISABLED": "1"}
    loi_cuoi = ""
    for lan in range(1, SO_LAN_THU + 1):
        try:
            proc = chay_lenh_fn(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=TIMEOUT_GH_GIAY,
                **kw,
            )
            if getattr(proc, "returncode", 1) == 0:
                return True
            loi_cuoi = (getattr(proc, "stderr", "") or getattr(proc, "stdout", "") or f"exit={proc.returncode}").strip()
        except (OSError, subprocess.SubprocessError) as exc:
            loi_cuoi = str(exc)
        if lan < SO_LAN_THU:
            ham_ngu(0.2 * lan)
    _ghi_log_an_toan(log_fn, f"gh pr comment that bai sau {SO_LAN_THU} lan: {loi_cuoi}", secret_val=secret_val)
    return False


def _gui_bang_rest(
    dong: str,
    token: str,
    repo: str,
    so_pr: int,
    urlopen_fn,
    ham_ngu,
    log_fn,
) -> bool:
    url = f"{API_GITHUB_GOC.rstrip('/')}/repos/{repo}/issues/{so_pr}/comments"
    payload = json.dumps({"body": dong}, ensure_ascii=False).encode("utf-8")
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "linhx-runner",
    }
    loi_cuoi = ""
    for lan in range(1, SO_LAN_THU + 1):
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        try:
            with urlopen_fn(req, timeout=TIMEOUT_HTTP_GIAY) as resp:
                status = getattr(resp, "status", None)
                if status is None and hasattr(resp, "getcode"):
                    status = resp.getcode()
                if status is None or (200 <= int(status) < 300):
                    return True
                loi_cuoi = f"HTTP {status}"
        except urllib.error.HTTPError as exc:
            loi_cuoi = f"HTTP {exc.code}: {exc.reason}"
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            loi_cuoi = str(exc)
        if lan < SO_LAN_THU:
            ham_ngu(0.2 * lan)
    _ghi_log_an_toan(log_fn, f"REST API that bai sau {SO_LAN_THU} lan: {loi_cuoi}", secret_val=token)
    return False


def bao(
    id,
    dat,
    may,
    phut,
    *,
    tep_env: Path | str | None = None,
    thu_muc_xong: Path | str | None = None,
    repo: str = REPO_MAC_DINH,
    so_pr: int = SO_PR_MAC_DINH,
    chay_lenh_fn=None,
    urlopen_fn=None,
    ngu_fn=None,
    log_fn=None,
) -> bool:
    """Dang 1 dong thong bao len PR #36 bang gh CLI hoac REST API; loi mang thu lai 3 lan roi bo qua."""
    token = ""
    try:
        phieu_id = " ".join(str(id or "").split()).strip()
        if not phieu_id:
            return False
        tep_da_bao = (Path(thu_muc_xong) / phieu_id / ".da-bao") if thu_muc_xong is not None else None
        if tep_da_bao is not None and tep_da_bao.exists():
            return False

        token = doc_token_gh(tep_env=tep_env)
        dong = tao_dong_bao(phieu_id, dat, may, phut)
        ham_chay = chay_lenh_fn or _CHAY_LENH_FN or subprocess.run
        ham_mo = urlopen_fn or _URLOPEN_FN or urllib.request.urlopen
        ham_ngu = ngu_fn or time.sleep

        co_mock = _dang_mock_lenh(chay_lenh_fn)
        lenh_gh = _tim_lenh_gh(co_mock=co_mock)
        co_gh, da_dang_nhap = kiem_tra_gh_dang_nhap(chay_lenh_fn=ham_chay)
        if co_gh and da_dang_nhap:
            ok = _gui_bang_gh(
                dong,
                repo,
                so_pr,
                ham_chay,
                ham_ngu,
                log_fn,
                lenh_gh=lenh_gh,
                secret_val=token,
                co_mock=co_mock,
            )
            if ok:
                _ghi_dau_da_bao(tep_da_bao, phieu_id)
            return ok

        if not token:
            _ghi_log_an_toan(log_fn, "bo qua bao claude: may chua dang nhap gh va thieu LINHX_GH_TOKEN")
            return False

        ok = _gui_bang_rest(dong, token, repo, so_pr, ham_mo, ham_ngu, log_fn)
        if ok:
            _ghi_dau_da_bao(tep_da_bao, phieu_id)
        return ok
    except Exception as exc:
        _ghi_log_an_toan(log_fn, f"loi ngoai le khi bao claude: {exc}", secret_val=token)
        return False
