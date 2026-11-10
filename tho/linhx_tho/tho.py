"""Logic thuần Python và CLI cho thợ Windows (`linhx-tho`):
- Kéo phiếu từ Frappe qua HTTPS (chặn redirect, chỉ gửi khoá qua header, bắt buộc kiểm chữ ký HMAC-SHA256
  ràng buộc mã thợ, hạn dùng và nonce chống phát lại có khoá tệp độc quyền).
- Chuẩn hoá Unicode NFKC, loại bỏ ký tự điều khiển/ẩn và kiểm tra đề theo allowlist ký tự + loại phiếu.
- Lập kế hoạch chạy (`ke_hoach_chay`) và hỗ trợ chế độ `--chay-thu` không gọi `agy`.
- Ghi `.canh-tho/PHIEU.md` và gọi `agy` ẩn qua bản sao cô lập của `chay-an.vbs` + `CREATE_NO_WINDOW`
  bên trong cây thư mục tạm tách rời hoàn toàn (trích từ `git archive`, không có `.git` và không chép `tho/`),
  ở chế độ sandbox (`--mode accept-edits --sandbox --disable-slash-commands --settings`).
- Đối chiếu trực tiếp bảng băm SHA-256 trên cây tạm (không phụ thuộc `.gitignore`), chỉ sao chép và stage
  tệp hợp lệ thuộc allowlist `vung` (không phân biệt hoa thường trên NTFS), từ chối tệp tự thực thi và tệp chứa
  bí mật/khoá đang dùng, tự hoàn tác sạch worktree nếu thất bại.
"""
from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
from datetime import datetime, timezone
import functools
import hashlib
import hmac
import json
import os
import pathlib
import platform
import re
import shutil
import ssl
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
import unicodedata
from urllib import error as urlerror
from urllib import request as urlrequest
from urllib.parse import urlparse

from ._chay_an import (
    _DUOI_SCRIPT_CAM,
    _dong_job,
    _gan_job_kill_on_close,
    _giet_cay_tien_trinh,
    _tao_env_sach,
)

BUOC_CHUAN = ["keo_phieu", "kiem_de", "ghi_phieu_md", "chay_agy_an", "nop_phieu"]
LOAI_PHIEU_HOP_LE = ("feature", "sua_loi", "kiem_thu", "bao_tri")
MAX_HAN_DUNG_GIAY = 86400
PROMPT_PHIEU_CO_DINH = (
    "Doc va lam theo dung file .canh-tho/PHIEU.md (tieng Viet). "
    "Thu muc lam viec la thu muc hien tai."
)

THU_MUC_THO = pathlib.Path(__file__).resolve().parent.parent
CHAY_AN_VBS = THU_MUC_THO / "chay-an.vbs"
CAU_HINH_SANDBOX_AGY = THU_MUC_THO / "agy-sandbox-settings.json"
CO_KHONG_CUA_SO = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)

_KHOA_NONCE_LUONG = threading.Lock()

# Allowlist tường minh các thư mục gốc cụ thể được phép khai báo trong `vung` của phiếu
# (cấm `tho/`, `canh/`, `tests/nghiem-thu/`, `tests/**` rộng và mọi glob gốc kiểu `**/*.py`).
THU_MUC_GOC_CHO_PHEP = (
    "apps/",
    "cli/",
    "deploy/",
    "front/",
    "kiem-thu/",
    "bang-chung/",
    "nguon/",
    "runner/",
    "sites/",
    "tests/e2e/",
    "trang-bu/",
)

CHINH_SACH_LOAI_PHIEU: dict[str, dict[str, object]] = {
    "kiem_thu": {
        "mode_agy": "accept-edits",
        "vung_mac_dinh": ("kiem-thu/**", "bang-chung/**"),
        "max_do_dai_de": 2000,
        "duoi_tep_cho_phep": (".md", ".json", ".txt", ".py"),
    },
    "feature": {
        "mode_agy": "accept-edits",
        "vung_mac_dinh": (),
        "max_do_dai_de": 4000,
        "duoi_tep_cho_phep": (
            ".py",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".json",
            ".md",
            ".html",
            ".css",
            ".txt",
            ".toml",
            ".yml",
            ".yaml",
        ),
    },
    "sua_loi": {
        "mode_agy": "accept-edits",
        "vung_mac_dinh": (),
        "max_do_dai_de": 4000,
        "duoi_tep_cho_phep": (
            ".py",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".json",
            ".md",
            ".html",
            ".css",
            ".txt",
            ".toml",
            ".yml",
            ".yaml",
        ),
    },
    "bao_tri": {
        "mode_agy": "accept-edits",
        "vung_mac_dinh": (),
        "max_do_dai_de": 3000,
        "duoi_tep_cho_phep": (".py", ".json", ".md", ".txt", ".toml", ".yml", ".yaml"),
    },
}

_MAU_MA_PHIEU = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_MAU_MA_THO = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_MAU_NONCE = re.compile(r"^[A-Za-z0-9._-]{8,128}$")
_MAU_CHU_KY_HEX = re.compile(r"^[0-9a-fA-F]{64}$")
_DAU_CAU_CHO_PHEP = frozenset("\n\r\t .,;:!?()[]{}/_-+='\"%·–—“”‘’")
_TEN_THIET_BI_WINDOWS = frozenset(
    {
        "con",
        "prn",
        "aux",
        "nul",
        *(f"com{i}" for i in range(1, 10)),
        *(f"lpt{i}" for i in range(1, 10)),
    }
)

LUON_CAM_COMMIT = (
    ".git",
    ".git/**",
    ".*",
    "**/.*",
    "**/.*/**",
    "tho",
    "tho/**",
    ".agents/**",
    ".agent/**",
    "_agents/**",
    "_agent/**",
    "**/_agents/**",
    "**/_agent/**",
    ".gemini/**",
    ".claude/**",
    ".github/**",
    ".vscode/**",
    ".canh/**",
    ".canh-tho/**",
    "canh/**",
    "tests/nghiem-thu/**",
    "*.khoa",
    "**/*.khoa",
    "pyproject.toml",
    "**/pyproject.toml",
    "conftest.py",
    "**/conftest.py",
    "pytest.ini",
    "**/pytest.ini",
    ".pytest.ini",
    "**/.pytest.ini",
    "setup.cfg",
    "**/setup.cfg",
    "tox.ini",
    "**/tox.ini",
    "setup.py",
    "**/setup.py",
    "sitecustomize.py",
    "**/sitecustomize.py",
    "usercustomize.py",
    "**/usercustomize.py",
    "*.pth",
    "**/*.pth",
    "GEMINI.md",
    "**/GEMINI.md",
    "AGENTS.md",
    "**/AGENTS.md",
    "CLAUDE.md",
    "**/CLAUDE.md",
    "hooks.json",
    "**/hooks.json",
    "mcp_config.json",
    "**/mcp_config.json",
)

_MAU_TEN_TEP_BI_MAT = re.compile(
    r"(?i)(^|/)(\.env|tho\.env|id_rsa|id_ed25519|credentials\.json|token\.json|service-account\.json|site_config\.json)$"
    r"|(^|/)\.env\.(?!example$|mau$|sample$)"
    r"|\.(pem|key|p12|pfx|keystore|kdbx|env)$"
)

_TEN_BIEN_BI_MAT_MOI_TRUONG = (
    "LINHX_THO_KHOA",
    "LINHX_PHIEU_HMAC_KHOA",
    "SEPAY_KHOA",
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "OPENAI_API_KEY",
)


def _bien_dich_mau_bi_mat() -> tuple[re.Pattern[str], ...]:
    # LƯU Ý BẢO TRÌ: Tách đôi các tiền tố khoá/token thành cặp (dau, duoi) rồi mới ghép lúc chạy
    # để trình quét bí mật tĩnh trên `git diff` không báo dương tính giả vào chính mã nguồn bộ lọc.
    # Không gộp lại thành chuỗi liền nguyên văn.
    cac_cap = (
        ("sk", "-ant-" + r"[A-Za-z0-9_-]{10,}"),
        ("AI", "za" + r"[0-9A-Za-z_-]{30,}"),
        ("-----BEG" + "IN ", r"[A-Z ]*PRI" + "VATE KEY"),
        ("gh", "p_" + r"[A-Za-z0-9]{30,}"),
        ("github", "_pat_" + r"[A-Za-z0-9_]{30,}"),
        ("xo", r"x[bpas]-[A-Za-z0-9-]{10,}"),
        ("AK", "IA" + r"[0-9A-Z]{16}"),
        ("sk", r"-[A-Za-z0-9]{40,}"),
        (
            r"(?i)(sepay[_a-z]*|api_?key|secret|password|mat_?khau|token)",
            r"\s*[:=]\s*['\"][A-Za-z0-9+/_\-]{24,}['\"]",
        ),
    )
    return tuple(re.compile(dau + duoi) for dau, duoi in cac_cap)


_MAU_NOI_DUNG_BI_MAT = _bien_dich_mau_bi_mat()


def _thu_thap_gia_tri_bi_mat(
    ds_bo_sung: tuple[str, ...] | list[str] | None = None,
) -> tuple[str, ...]:
    """Thu thập giá trị thực tế của các khoá đang dùng (`LINHX_THO_KHOA`, `LINHX_PHIEU_HMAC_KHOA`...)
    kèm biến thể mã hoá Base64 / Hex để chặn rò rỉ khoá dạng trần không có tiền tố.
    """
    nguon: list[str] = []
    for ten_bien in _TEN_BIEN_BI_MAT_MOI_TRUONG:
        val = os.environ.get(ten_bien, "")
        if isinstance(val, str) and val.strip():
            nguon.append(val.strip())
    if ds_bo_sung:
        for item in ds_bo_sung:
            if isinstance(item, str) and item.strip():
                nguon.append(item.strip())

    ket_qua: list[str] = []
    for goc in nguon:
        if len(goc) < 4:
            continue
        ket_qua.append(goc)
        goc_bytes = goc.encode("utf-8")
        for bien_the in (
            base64.b64encode(goc_bytes).decode("ascii").rstrip("="),
            base64.urlsafe_b64encode(goc_bytes).decode("ascii").rstrip("="),
            goc_bytes.hex(),
        ):
            if len(bien_the) >= 6:
                ket_qua.append(bien_the)
    return tuple(dict.fromkeys(ket_qua))


def _chua_gia_tri_bi_mat_dang_dung(
    chu: str,
    ds_bo_sung: tuple[str, ...] | list[str] | None = None,
) -> bool:
    if not chu:
        return False
    chu_thap = chu.lower()
    for bm in _thu_thap_gia_tri_bi_mat(ds_bo_sung):
        if bm in chu:
            return True
        if len(bm) >= 8 and bm.lower() in chu_thap:
            return True
    return False


MAU_LENH_SHELL = (
    re.compile(r"\b(?:powershell|pwsh|command\.com)(?:\.exe)?\b", re.IGNORECASE),
    re.compile(r"\bcmd\.exe\b", re.IGNORECASE),
    re.compile(r"\bcmd\s+/[ck]\b", re.IGNORECASE),
    re.compile(r"\b(?:ba|z|k|da|c)?sh(?:\.exe)?\s+(?:-[a-z]+|[^\s]+\.sh\b|\./|/)", re.IGNORECASE),
    re.compile(r"\bwsl(?:\.exe)?\b", re.IGNORECASE),
    re.compile(r"\b(?:curl|wget|iwr|irm|iex|saps)\b", re.IGNORECASE),
    re.compile(r"\b(?:invoke-expression|invoke-webrequest|invoke-restmethod|start-process|new-object)\b", re.IGNORECASE),
    re.compile(r"\b(?:downloadstring|downloadfile|frombase64string|encodedcommand)\b", re.IGNORECASE),
    re.compile(
        r"\b(?:wscript|cscript|mshta|rundll32|regsvr32|certutil|bitsadmin|msiexec|schtasks|taskkill|netsh)(?:\.exe)?\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(?:python\d*(?:\.\d+)?|py)(?:\.exe)?\s+(?:-[A-Za-z0-9]|[^\s]+\.py\b)", re.IGNORECASE),
    re.compile(
        r"\b(?:node|deno|bun|perl|ruby|php)(?:\.exe)?\s+(?:-[A-Za-z]|[^\s]+\.(?:js|mjs|cjs|ts|pl|rb|php)\b)",
        re.IGNORECASE,
    ),
    re.compile(r"\b(?:os\.system|subprocess\.(?:run|popen|call|check_output|check_call))\b", re.IGNORECASE),
    re.compile(r"(?:https?|ftp|file)://", re.IGNORECASE),
    re.compile(r"\b[\w./-]+\.(?:exe|dll|bat|cmd|ps1|vbs|wsf|hta|msi|scr|sh)\b", re.IGNORECASE),
)


def _chuan_hoa_de_unicode(de: str) -> str:
    """Chuẩn hoá NFKC và từ chối mọi ký tự điều khiển, ký tự ẩn/zero-width hoặc bidi override."""
    if not isinstance(de, str):
        raise ValueError("Đề phiếu phải là kiểu chuỗi")
    for ch in de:
        cat = unicodedata.category(ch)
        if ch == "\x00" or (cat == "Cc" and ch not in ("\n", "\r", "\t")) or cat in ("Cf", "Cs", "Co"):
            raise ValueError("Đề phiếu chứa ký tự điều khiển hoặc ký tự ẩn Unicode không hợp lệ")

    da_chuan = unicodedata.normalize("NFKC", de)
    for ch in da_chuan:
        cat = unicodedata.category(ch)
        if ch == "\x00" or (cat == "Cc" and ch not in ("\n", "\r", "\t")) or cat in ("Cf", "Cs", "Co"):
            raise ValueError("Đề phiếu sau chuẩn hoá NFKC chứa ký tự điều khiển không hợp lệ")
        if cat[0] not in ("L", "M", "N", "Z") and ch not in _DAU_CAU_CHO_PHEP:
            raise ValueError(f"Đề phiếu chứa ký tự ngoài danh sách cho phép: {ch!r}")
    return da_chuan


def kiem_de_an_toan(de: str, loai_phieu: str | None = None) -> None:
    """Kiểm tra đề phiếu phía thợ bằng chuẩn hoá NFKC, allowlist ký tự và từ chối mọi mẫu lệnh shell."""
    loai_kiem = "kiem_thu" if loai_phieu is None else loai_phieu
    if not isinstance(loai_kiem, str) or loai_kiem not in CHINH_SACH_LOAI_PHIEU:
        raise ValueError(f"loai_phieu không thuộc allowlist: {loai_phieu!r}")

    da_chuan = _chuan_hoa_de_unicode(de)
    de_gon = da_chuan.strip()
    if not de_gon:
        raise ValueError("Đề phiếu không được để trống")

    max_len = int(CHINH_SACH_LOAI_PHIEU[loai_kiem]["max_do_dai_de"])  # type: ignore[arg-type]
    if len(de_gon) > max_len:
        raise ValueError(f"Đề phiếu vượt quá độ dài tối đa ({max_len}) của loại {loai_kiem}")

    for mau in MAU_LENH_SHELL:
        if mau.search(de_gon):
            raise ValueError(f"Đề phiếu chứa mẫu lệnh hoặc thực thi bị từ chối phía thợ: {mau.pattern}")


@functools.lru_cache(maxsize=512)
def _glob_thanh_regex(mau_glob: str) -> re.Pattern[str]:
    g = mau_glob.strip().replace("\\", "/").lower()
    if g.endswith("/"):
        g += "**"
    ket = ""
    i = 0
    while i < len(g):
        if g.startswith("**/", i):
            ket += r"(?:.*/)?"
            i += 3
        elif g.startswith("**", i):
            ket += r".*"
            i += 2
        elif g[i] == "*":
            ket += r"[^/]*"
            i += 1
        elif g[i] == "?":
            ket += r"[^/]"
            i += 1
        else:
            ket += re.escape(g[i])
            i += 1
    return re.compile("^" + ket + "$", re.IGNORECASE)


def _khop_glob(duong_tuong_doi: str, ds_glob: tuple[str, ...] | list[str]) -> bool:
    """So khớp glob không phân biệt hoa thường (tương thích hệ tệp Windows NTFS)."""
    chuan = duong_tuong_doi.replace("\\", "/").lstrip("/").lower()
    return any(_glob_thanh_regex(g.lower()).match(chuan) for g in ds_glob)


def _phan_duong_dan_hop_le_ntfs(phan: str) -> bool:
    if not phan or phan in (".", "..") or phan.startswith(".") or phan.endswith((".", " ")) or "~" in phan:
        return False
    goc_ten = phan.split(".", 1)[0].lower()
    if goc_ten in _TEN_THIET_BI_WINDOWS:
        return False
    return True


def _chuan_vung_cho_phep(phieu: dict, bat_buoc_co_vung: bool = False) -> list[str]:
    loai = str(phieu.get("loai_phieu") or "kiem_thu").strip()
    chinh_sach = CHINH_SACH_LOAI_PHIEU[loai]
    vung_raw = phieu.get("vung")
    ds_tho: list[str] = []
    if isinstance(vung_raw, list):
        ds_tho = [str(x).strip() for x in vung_raw if str(x).strip()]
    elif isinstance(vung_raw, str) and vung_raw.strip():
        ds_tho = [x.strip() for x in re.split(r"[,;\n]+", vung_raw) if x.strip()]

    if not ds_tho:
        mac_dinh = list(chinh_sach["vung_mac_dinh"])  # type: ignore[arg-type]
        if mac_dinh:
            ds_tho = mac_dinh
        elif bat_buoc_co_vung:
            raise ValueError(f"Phiếu loại {loai!r} bắt buộc khai báo vùng sửa hợp lệ")
        else:
            return []

    ket_qua: list[str] = []
    for g in ds_tho:
        chuan = g.replace("\\", "/").strip()
        if chuan.endswith("/") and chuan != "/":
            chuan = chuan + "**"
        chuan_thap = chuan.lower()
        cac_phan = chuan_thap.split("/")
        if (
            not chuan_thap
            or chuan_thap in ("*", "**", ".", "./", "/")
            or chuan_thap.startswith(("/", ".", "tho/", ".git", ".canh", "canh/", "tests/nghiem-thu"))
            or chuan_thap == "tho"
            or ":" in chuan_thap
            or any(
                not _phan_duong_dan_hop_le_ntfs(p)
                for p in cac_phan
                if p not in ("*", "**")
            )
            or any(not p for p in cac_phan)
        ):
            raise ValueError(f"Vùng cho phép của phiếu không an toàn: {g!r}")
        if not any(chuan_thap.startswith(goc_duoc) for goc_duoc in THU_MUC_GOC_CHO_PHEP):
            raise ValueError(f"Vùng cho phép không thuộc allowlist thư mục cụ thể: {g!r}")
        if _khop_glob(chuan_thap, LUON_CAM_COMMIT) or chuan_thap.endswith(".khoa"):
            raise ValueError(f"Vùng cho phép chạm tệp cấm: {g!r}")
        ket_qua.append(chuan)
    return ket_qua


def _chuan_ma_phieu(phieu: dict) -> str:
    ma = str(phieu.get("ma_phieu") or phieu.get("name") or "").strip()
    if not ma:
        raise ValueError("Phiếu thiếu ma_phieu/name")
    if ".." in ma or not _MAU_MA_PHIEU.match(ma):
        raise ValueError(f"Mã phiếu không hợp lệ: {ma!r}")
    return ma


def _kiem_phieu_hop_le(phieu: dict, bat_buoc_co_vung: bool = False) -> tuple[str, str, list[str]]:
    if not isinstance(phieu, dict):
        raise ValueError("Phiếu phải là kiểu dict")
    loai_raw = phieu.get("loai_phieu")
    if loai_raw is not None and (not isinstance(loai_raw, str) or loai_raw not in LOAI_PHIEU_HOP_LE):
        raise ValueError(f"loai_phieu không hợp lệ: {loai_raw!r}")
    loai = loai_raw if isinstance(loai_raw, str) else "kiem_thu"
    kiem_de_an_toan(phieu.get("de", ""), loai_phieu=loai)
    ma_phieu = _chuan_ma_phieu(phieu)
    vung = _chuan_vung_cho_phep(phieu, bat_buoc_co_vung=bat_buoc_co_vung)
    return ma_phieu, loai, vung


def _chuan_han_dung_epoch(han_dung: object) -> int:
    """Chuẩn hoá hạn dùng của phiếu sang mốc Unix epoch (giây)."""
    if isinstance(han_dung, bool) or han_dung is None:
        raise ValueError("Phiếu ký thiếu han_dung hợp lệ")
    if isinstance(han_dung, (int, float)):
        ep = int(han_dung)
    elif isinstance(han_dung, str):
        s = han_dung.strip()
        if not s:
            raise ValueError("han_dung không được để trống")
        if re.fullmatch(r"\d+", s):
            ep = int(s)
        else:
            try:
                dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ValueError(f"Định dạng han_dung không hợp lệ: {han_dung!r}") from exc
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            ep = int(dt.timestamp())
    else:
        raise ValueError(f"Kiểu han_dung không hợp lệ: {type(han_dung).__name__}")
    if ep <= 0:
        raise ValueError("han_dung phải là mốc thời gian dương")
    return ep


def _chuan_nonce_phieu(nonce_raw: object) -> str:
    if not isinstance(nonce_raw, str):
        raise ValueError("Phiếu ký bắt buộc có nonce kiểu chuỗi")
    nonce = nonce_raw.strip()
    if not _MAU_NONCE.match(nonce):
        raise ValueError("nonce của phiếu phải dài 8..128 ký tự thuộc [A-Za-z0-9._-]")
    return nonce


def _chuoi_ky_phieu(phieu: dict) -> str:
    """Chuẩn hoá dữ liệu ký HMAC của phiếu, bắt buộc ràng buộc `tho`, `han_dung` và `nonce`."""
    ma_phieu, loai, vung = _kiem_phieu_hop_le(phieu, bat_buoc_co_vung=True)
    tho = str(phieu.get("tho") or "").strip()
    if not tho or not _MAU_MA_THO.match(tho):
        raise ValueError("Phiếu ký bắt buộc có mã thợ hợp lệ (tho)")
    han_dung = _chuan_han_dung_epoch(phieu.get("han_dung"))
    nonce = _chuan_nonce_phieu(phieu.get("nonce"))
    de_sach = unicodedata.normalize("NFKC", str(phieu.get("de") or "")).strip()
    goc_ky = {
        "de": de_sach,
        "han_dung": han_dung,
        "loai_phieu": loai,
        "ma_phieu": ma_phieu,
        "nonce": nonce,
        "tho": tho,
        "vung": vung,
    }
    return json.dumps(goc_ky, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def tao_chu_ky_phieu(phieu: dict, khoa_hmac: str) -> str:
    """Ký nội dung chuẩn hoá của phiếu (kèm `tho`, `han_dung`, `nonce`) bằng HMAC-SHA256."""
    if not isinstance(khoa_hmac, str) or not khoa_hmac.strip():
        raise ValueError("Khoá HMAC ký phiếu không được để trống")
    thong_diep = _chuoi_ky_phieu(phieu).encode("utf-8")
    return hmac.new(khoa_hmac.encode("utf-8"), thong_diep, hashlib.sha256).hexdigest()


def _thu_muc_trang_thai_tho() -> pathlib.Path:
    """Thư mục lưu trạng thái cục bộ của thợ (ngoài worktree mà agy ghi)."""
    tu_env = os.environ.get("LINHX_THO_STATE_DIR", "").strip()
    if tu_env:
        return pathlib.Path(tu_env).resolve()
    local_app = os.environ.get("LOCALAPPDATA", "").strip()
    if local_app:
        return (pathlib.Path(local_app) / "linhx-tho").resolve()
    return (pathlib.Path.home() / ".local" / "share" / "linhx-tho").resolve()


@contextmanager
def _khoa_tep_nonce(duong_kho: pathlib.Path, timeout_giay: float = 10.0):
    """Khoá độc quyền giữa các luồng và tiến trình khi đọc-ghi tệp chống phát lại nonce."""
    duong_kho.parent.mkdir(parents=True, exist_ok=True)
    tep_lock = duong_kho.with_name(duong_kho.name + ".lock")
    han = time.monotonic() + timeout_giay
    with _KHOA_NONCE_LUONG:
        fd: int | None = None
        while fd is None:
            try:
                fd = os.open(str(tep_lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, f"{os.getpid()} {time.time()}\n".encode("ascii"))
            except FileExistsError:
                try:
                    if (time.time() - tep_lock.stat().st_mtime) > 60.0:
                        tep_lock.unlink(missing_ok=True)
                        continue
                except OSError:
                    pass
                if time.monotonic() >= han:
                    raise TimeoutError(f"Không giành được khoá tệp nonce: {tep_lock}")
                time.sleep(0.02)
        try:
            yield
        finally:
            try:
                os.close(fd)
            except OSError:
                pass
            try:
                tep_lock.unlink(missing_ok=True)
            except OSError:
                pass


def _kiem_va_luu_nonce(
    kho_nonce: pathlib.Path | str | set[str],
    tho: str,
    ma_phieu: str,
    nonce: str,
    han_dung: int,
    now_ts: float,
    ghi_nhan: bool,
) -> bool:
    khoa_day_du = f"{tho}:{ma_phieu}:{nonce}"
    if isinstance(kho_nonce, set):
        with _KHOA_NONCE_LUONG:
            if nonce in kho_nonce or khoa_day_du in kho_nonce:
                return False
            if ghi_nhan:
                kho_nonce.add(nonce)
                kho_nonce.add(khoa_day_du)
            return True

    duong_kho = pathlib.Path(kho_nonce).resolve()
    with _khoa_tep_nonce(duong_kho):
        muc_hien_tai: dict[str, int] = {}
        if duong_kho.is_file():
            try:
                du_lieu = json.loads(duong_kho.read_text(encoding="utf-8"))
                if isinstance(du_lieu, dict) and isinstance(du_lieu.get("muc"), dict):
                    for k, v in du_lieu["muc"].items():
                        if isinstance(k, str) and isinstance(v, (int, float)) and not isinstance(v, bool):
                            if float(v) > now_ts:
                                muc_hien_tai[k] = int(v)
            except Exception:
                return False

        if nonce in muc_hien_tai or khoa_day_du in muc_hien_tai:
            return False

        if ghi_nhan:
            muc_hien_tai[nonce] = han_dung
            muc_hien_tai[khoa_day_du] = han_dung
            tap_tam = duong_kho.with_suffix(f".{os.getpid()}.{threading.get_ident()}.tmp")
            tap_tam.write_text(
                json.dumps({"muc": muc_hien_tai}, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
            os.replace(tap_tam, duong_kho)
        return True


def xac_thuc_chu_ky_phieu(
    phieu: dict,
    khoa_hmac: str,
    *,
    ma_tho: str | None = None,
    thoi_diem: float | None = None,
    kho_nonce: pathlib.Path | str | set[str] | None = None,
    ghi_nhan_nonce: bool = False,
) -> bool:
    """Kiểm tra chữ ký HMAC-SHA256 hằng thời gian, đồng thời đối chiếu `tho`, `han_dung` và `nonce`."""
    if not isinstance(phieu, dict) or not isinstance(khoa_hmac, str) or not khoa_hmac.strip():
        return False
    chu_ky_nhan = str(phieu.get("chu_ky") or phieu.get("chu_ky_hmac") or "").strip().lower()
    if not _MAU_CHU_KY_HEX.match(chu_ky_nhan):
        return False
    try:
        chu_ky_dung = tao_chu_ky_phieu(phieu, khoa_hmac).lower()
        han_dung = _chuan_han_dung_epoch(phieu.get("han_dung"))
        nonce = _chuan_nonce_phieu(phieu.get("nonce"))
        tho_phieu = str(phieu.get("tho") or "").strip()
        ma_phieu = _chuan_ma_phieu(phieu)
    except ValueError:
        return False

    if not hmac.compare_digest(chu_ky_nhan.encode("ascii"), chu_ky_dung.encode("ascii")):
        return False

    if ma_tho is not None and tho_phieu != str(ma_tho).strip():
        return False

    now_ts = float(time.time() if thoi_diem is None else thoi_diem)
    if han_dung <= now_ts or (han_dung - now_ts) > MAX_HAN_DUNG_GIAY:
        return False

    if kho_nonce is not None:
        if not _kiem_va_luu_nonce(
            kho_nonce,
            tho=tho_phieu,
            ma_phieu=ma_phieu,
            nonce=nonce,
            han_dung=han_dung,
            now_ts=now_ts,
            ghi_nhan=ghi_nhan_nonce,
        ):
            return False

    return True


def tim_lenh_agy(lenh_agy_tuy_chon: str | None = None) -> str:
    """Xác định đường dẫn thực thi nhị phân `agy.exe` trên máy thợ."""
    if isinstance(lenh_agy_tuy_chon, str) and lenh_agy_tuy_chon.strip():
        return lenh_agy_tuy_chon.strip()
    tu_env = os.environ.get("LINHX_AGY_BIN", "").strip()
    if tu_env:
        return tu_env
    mac_dinh = pathlib.Path.home() / ".gemini" / "bin" / ("agy.exe" if os.name == "nt" else "agy")
    if mac_dinh.exists():
        return str(mac_dinh)
    tim_thay = shutil.which("agy.exe") or shutil.which("agy")
    if tim_thay:
        return tim_thay
    return str(mac_dinh)


def _tham_so_agy_co_dinh(
    loai_phieu: str = "kiem_thu",
    timeout_giay: int = 2400,
    tep_settings: pathlib.Path | None = None,
) -> list[str]:
    chinh_sach = CHINH_SACH_LOAI_PHIEU.get(loai_phieu, CHINH_SACH_LOAI_PHIEU["kiem_thu"])
    mode_agy = str(chinh_sach["mode_agy"])
    tham_so = [
        "-p",
        PROMPT_PHIEU_CO_DINH,
        "--output-format",
        "stream-json",
        "--mode",
        mode_agy,
        "--sandbox",
        "--disable-slash-commands",
        "--print-timeout",
        f"{max(30, int(timeout_giay))}s",
    ]
    duong_settings = tep_settings if tep_settings is not None else CAU_HINH_SANDBOX_AGY
    if duong_settings.is_file():
        tham_so.extend(["--settings", str(duong_settings)])
    return tham_so


def sinh_lenh_agy(
    lenh_agy_bin: str | None = None,
    dung_vbs: bool = True,
    loai_phieu: str = "kiem_thu",
    timeout_giay: int = 2400,
) -> list[str]:
    """Sinh danh sách tham số cố định để gọi `agy` ẩn trong sandbox (không cấp quyền dòng lệnh)."""
    agy_exe = tim_lenh_agy(lenh_agy_bin)
    tham_so_agy = [agy_exe, *_tham_so_agy_co_dinh(loai_phieu=loai_phieu, timeout_giay=timeout_giay)]
    if dung_vbs:
        return [
            "wscript.exe",
            "//B",
            str(CHAY_AN_VBS),
            *tham_so_agy,
        ]
    return tham_so_agy


def ke_hoach_chay(phieu: dict, thu_muc: str) -> dict:
    """Kiểm tra an toàn đề phiếu và trả kế hoạch chạy 5 bước mà KHÔNG gọi `agy`."""
    ma_phieu, loai, _ = _kiem_phieu_hop_le(phieu, bat_buoc_co_vung=False)
    if not isinstance(thu_muc, (str, pathlib.Path)) or not str(thu_muc).strip():
        raise ValueError("thu_muc không được để trống")
    _ = pathlib.Path(thu_muc).resolve()
    return {
        "ma_phieu": ma_phieu,
        "buoc": list(BUOC_CHUAN),
        "lenh_agy": sinh_lenh_agy(dung_vbs=True, loai_phieu=loai),
        "da_goi_agy": False,
    }


def ghi_phieu_md(phieu: dict, thu_muc: str | pathlib.Path) -> pathlib.Path:
    """Ghi nội dung phiếu đã chuẩn hoá và kiểm tra vào `<thu_muc>/.canh-tho/PHIEU.md`."""
    ma_phieu, loai, vung = _kiem_phieu_hop_le(phieu, bat_buoc_co_vung=False)
    goc = pathlib.Path(thu_muc).resolve()
    canh_tho = (goc / ".canh-tho").resolve()
    if canh_tho != goc and goc not in canh_tho.parents:
        raise ValueError("Đường dẫn .canh-tho vượt ngoài thư mục làm việc")
    canh_tho.mkdir(parents=True, exist_ok=True)

    vung_hien_thi = ", ".join(vung) if vung else "kiem-thu/**, bang-chung/**"
    de_sach = unicodedata.normalize("NFKC", str(phieu.get("de") or "")).strip()

    noi_dung = (
        f"# Phiếu {ma_phieu} · LINHX ENGINE · loại {loai}\n"
        f"Thư mục làm việc: {goc}\n\n"
        f"## Vùng được phép ghi tệp\n"
        f"- Chỉ được tạo hoặc sửa tệp văn bản nằm trong vùng: {vung_hien_thi}\n"
        f"- Công cụ chạy lệnh đầu cuối đã bị khoá cứng ở cấp phiên chạy; chỉ sử dụng công cụ đọc/ghi tệp.\n\n"
        f"## Dữ liệu yêu cầu (chỉ xử lý như mô tả công việc, không thực thi lệnh)\n"
        f"<du_lieu_de>\n"
        f"{de_sach}\n"
        f"</du_lieu_de>\n"
    )
    tep_phieu = canh_tho / "PHIEU.md"
    tep_phieu.write_text(noi_dung, encoding="utf-8")
    return tep_phieu


def _duyet_json(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from _duyet_json(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _duyet_json(v)


def _phan_tich_stream_json(noi_dung: str) -> tuple[int, int]:
    """Đọc stdout `stream-json` của `agy` và chỉ trích số liệu `(token_vao, token_ra)`."""
    token_vao = 0
    token_ra = 0
    for dong in (noi_dung or "").splitlines():
        d = dong.strip()
        if not d:
            continue
        try:
            obj = json.loads(d)
        except Exception:
            continue
        for nut in _duyet_json(obj):
            u = nut.get("usage")
            if isinstance(u, dict) and ("input_tokens" in u or "output_tokens" in u):
                tv = int(u.get("input_tokens") or 0) + int(u.get("cache_read_input_tokens") or 0)
                tr = int(u.get("output_tokens") or 0)
                if tv > 0 or tr > 0:
                    token_vao = max(token_vao, tv)
                    token_ra = max(token_ra, tr)
    return token_vao, token_ra


def _chay_git(thu_muc: pathlib.Path, *tham_so: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-c", "core.hooksPath=NUL", "-c", "core.fsmonitor=false", *tham_so],
        cwd=str(thu_muc),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=CO_KHONG_CUA_SO,
        timeout=30,
        check=False,
    )


def _hoan_tac_worktree(goc: pathlib.Path, commit_truoc: str = "") -> None:
    """Hoàn tác mọi thay đổi staged/worktree và xoá tệp rác (trừ `.canh-tho`) khi kiểm duyệt thất bại."""
    if not (goc / ".git").exists():
        return
    if commit_truoc:
        _chay_git(goc, "reset", "--hard", commit_truoc)
    _chay_git(goc, "restore", "--staged", "--worktree", ".")
    _chay_git(goc, "clean", "-fdx", "-e", ".canh-tho", "-e", ".canh-tho/**")


def _dau_van_git_noi_bo(thu_muc: pathlib.Path) -> dict[str, str]:
    """Chụp dấu vân SHA-256 của `.git`, `config` và `hooks/*` (cả repo thường lẫn git worktree)."""
    dau_van: dict[str, str] = {}
    cham_git = thu_muc / ".git"
    if cham_git.is_file():
        dau_van[".git_file"] = hashlib.sha256(cham_git.read_bytes()).hexdigest()
    cac_git_dir: list[pathlib.Path] = []
    if cham_git.is_dir():
        cac_git_dir.append(cham_git)
    for co_git in ("--git-dir", "--git-common-dir"):
        r = _chay_git(thu_muc, "rev-parse", co_git)
        if r.returncode == 0 and r.stdout.strip():
            p = pathlib.Path(r.stdout.strip())
            p = (thu_muc / p).resolve() if not p.is_absolute() else p.resolve()
            if p.is_dir() and p not in cac_git_dir:
                cac_git_dir.append(p)

    for idx, git_dir in enumerate(cac_git_dir):
        cfg = git_dir / "config"
        if cfg.is_file():
            dau_van[f"{idx}:config"] = hashlib.sha256(cfg.read_bytes()).hexdigest()
        hooks_dir = git_dir / "hooks"
        if hooks_dir.is_dir():
            for p in sorted(hooks_dir.rglob("*")):
                if p.is_file():
                    rel = p.relative_to(git_dir).as_posix()
                    dau_van[f"{idx}:{rel}"] = hashlib.sha256(p.read_bytes()).hexdigest()
    return dau_van


def _la_tep_bi_mat(
    duong_tuong_doi: str,
    duong_day_du: pathlib.Path,
    ds_bi_mat: tuple[str, ...] | list[str] | None = None,
) -> str | None:
    rel = duong_tuong_doi.replace("\\", "/").lstrip("/")
    if _MAU_TEN_TEP_BI_MAT.search(rel):
        return f"Tên tệp nhạy cảm bị cấm commit: {rel}"
    if duong_day_du.is_symlink():
        return f"Không cho phép commit symlink: {rel}"
    if duong_day_du.is_file():
        try:
            kich_thuoc = duong_day_du.stat().st_size
            if kich_thuoc > 2 * 1024 * 1024:
                return f"Tệp vượt giới hạn kích thước an toàn (2MB): {rel}"
            raw = duong_day_du.read_bytes()
        except OSError:
            return f"Không đọc được tệp để kiểm tra bí mật: {rel}"
        cac_ban_chu = [raw.decode("utf-8", errors="ignore")]
        if b"\x00" in raw:
            cac_ban_chu.append(raw.decode("utf-16", errors="ignore"))
        for chu in cac_ban_chu:
            for mau in _MAU_NOI_DUNG_BI_MAT:
                if mau.search(chu):
                    return f"Phát hiện mẫu giống bí mật/khoá trong tệp: {rel}"
            if _chua_gia_tri_bi_mat_dang_dung(chu, ds_bi_mat):
                return f"Phát hiện giá trị khoá/bí mật đang dùng xuất hiện trong tệp: {rel}"
    return None


def _liet_ke_thay_doi_porcelain(thu_muc: pathlib.Path) -> list[str]:
    r = subprocess.run(
        [
            "git",
            "-c",
            "core.hooksPath=NUL",
            "-c",
            "core.fsmonitor=false",
            "status",
            "--porcelain",
            "-z",
            "-uall",
            "--ignored=matching",
        ],
        cwd=str(thu_muc),
        capture_output=True,
        creationflags=CO_KHONG_CUA_SO,
        timeout=30,
        check=False,
    )
    if r.returncode != 0 or not r.stdout:
        return []
    phan = r.stdout.decode("utf-8", errors="replace").split("\x00")
    ket_qua: list[str] = []
    i = 0
    while i < len(phan):
        muc = phan[i]
        if len(muc) >= 4:
            trang_thai = muc[:2]
            duong = muc[3:].rstrip("/")
            if trang_thai != "!!":
                ket_qua.append(duong.replace("\\", "/"))
            elif duong and not duong.lower().startswith(".canh-tho") and "__pycache__" not in duong.lower():
                # Tệp bị .gitignore che nhưng mới xuất hiện ngoài .canh-tho vẫn phải kiểm duyệt
                p_check = thu_muc / duong
                if p_check.is_file() or p_check.is_symlink():
                    ket_qua.append(duong.replace("\\", "/"))
            if "R" in trang_thai or "C" in trang_thai:
                i += 1
                if i < len(phan) and phan[i]:
                    ket_qua.append(phan[i].replace("\\", "/"))
        i += 1
    return list(dict.fromkeys(ket_qua))


def _kiem_khong_symlink_cha(goc: pathlib.Path, rel: str) -> None:
    hien_tai = goc
    for phan in rel.split("/")[:-1]:
        hien_tai = hien_tai / phan
        if hien_tai.is_symlink():
            raise ValueError(f"Thư mục cha chứa symlink không an toàn: {rel}")


def _kiem_va_chon_tep_stage(
    thu_muc: pathlib.Path,
    ds_duong: list[str],
    vung_cho_phep: list[str],
    loai_phieu: str,
    ds_bi_mat: tuple[str, ...] | list[str] | None = None,
) -> list[str]:
    duoi_hop_le = tuple(CHINH_SACH_LOAI_PHIEU[loai_phieu]["duoi_tep_cho_phep"])  # type: ignore[arg-type]
    goc = thu_muc.resolve()
    tep_hop_le: list[str] = []

    for rel_raw in ds_duong:
        rel = rel_raw.replace("\\", "/").lstrip("/")
        rel_thap = rel.lower()
        if not rel or rel_thap == ".canh-tho" or rel_thap.startswith(".canh-tho/"):
            continue
        cac_phan = rel.split("/")
        if ":" in rel or any(not _phan_duong_dan_hop_le_ntfs(p) for p in cac_phan):
            raise ValueError(f"Đường dẫn tệp không an toàn trên NTFS: {rel}")
        if _khop_glob(rel, LUON_CAM_COMMIT):
            raise ValueError(f"Từ chối commit tệp nằm trong danh sách cấm: {rel}")
        if not _khop_glob(rel, vung_cho_phep):
            raise ValueError(f"Tệp thay đổi nằm ngoài vùng cho phép ({', '.join(vung_cho_phep)}): {rel}")

        _kiem_khong_symlink_cha(goc, rel)
        day_du = goc / rel
        if day_du.exists() or day_du.is_symlink():
            try:
                da_phan_giai = day_du.resolve()
            except OSError as exc:
                raise ValueError(f"Đường dẫn tệp không hợp lệ: {rel}") from exc
            if da_phan_giai != goc and goc not in da_phan_giai.parents:
                raise ValueError(f"Tệp trỏ ra ngoài gốc repo: {rel}")
            if day_du.is_file() and duoi_hop_le and day_du.suffix.lower() not in duoi_hop_le:
                raise ValueError(f"Đuôi tệp {day_du.suffix!r} không thuộc allowlist của loại {loai_phieu}: {rel}")
            loi_bm = _la_tep_bi_mat(rel, day_du, ds_bi_mat=ds_bi_mat)
            if loi_bm:
                raise ValueError(loi_bm)

        tep_hop_le.append(rel)
    return tep_hop_le


def _dam_bao_commit_ket_qua(
    thu_muc: pathlib.Path,
    ma_phieu: str,
    loai_phieu: str,
    vung_cho_phep: list[str],
    commit_truoc: str,
    ds_bi_mat: tuple[str, ...] | list[str] | None = None,
) -> tuple[str, str]:
    """Kiểm tra chặt vùng sửa + bí mật, chỉ `git add --` tệp hợp lệ; hoàn tác sạch worktree nếu thất bại."""
    goc = thu_muc.resolve()
    thanh_cong = False
    try:
        nhanh_r = _chay_git(goc, "rev-parse", "--abbrev-ref", "HEAD")
        nhanh = nhanh_r.stdout.strip() if nhanh_r.returncode == 0 and nhanh_r.stdout.strip() else "main"

        if commit_truoc:
            da_commit_r = _chay_git(goc, "diff", "--name-only", f"{commit_truoc}..HEAD")
            ds_da_commit = [x.strip() for x in da_commit_r.stdout.splitlines() if x.strip()]
            if ds_da_commit:
                _kiem_va_chon_tep_stage(goc, ds_da_commit, vung_cho_phep, loai_phieu, ds_bi_mat=ds_bi_mat)

        ds_thay_doi = _liet_ke_thay_doi_porcelain(goc)
        tep_can_stage = _kiem_va_chon_tep_stage(goc, ds_thay_doi, vung_cho_phep, loai_phieu, ds_bi_mat=ds_bi_mat)
        if tep_can_stage:
            r_add = _chay_git(goc, "add", "--", *tep_can_stage)
            if r_add.returncode != 0:
                raise RuntimeError(f"Không thể stage tệp hợp lệ: {r_add.stderr.strip()}")
            r_commit = _chay_git(goc, "commit", "-q", "-m", f"{ma_phieu}: hoàn thành phiếu thợ")
            if r_commit.returncode != 0:
                raise RuntimeError(f"Không thể tạo commit kết quả: {r_commit.stderr.strip()}")

        sha_r = _chay_git(goc, "rev-parse", "HEAD")
        sha = sha_r.stdout.strip() if sha_r.returncode == 0 else ""
        if not sha or sha == commit_truoc:
            raise RuntimeError(
                f"Phiếu {ma_phieu} chưa tạo thay đổi hợp lệ trong vùng cho phép ({', '.join(vung_cho_phep)})"
            )
        thanh_cong = True
        return sha, nhanh
    finally:
        if not thanh_cong:
            _hoan_tac_worktree(goc, commit_truoc)


def _tao_thu_muc_runner_co_lap() -> tuple[pathlib.Path, pathlib.Path, pathlib.Path]:
    """Sao chép `chay-an.vbs`, `_chay_an.py` và `agy-sandbox-settings.json` sang thư mục tạm độc lập
    ngoài worktree của phiếu để tiến trình thợ không bao giờ nạp mã nằm trong vùng ghi của `agy`.
    """
    thu_muc_bin = pathlib.Path(tempfile.mkdtemp(prefix="linhx-tho-bin-")).resolve()
    goi_con = thu_muc_bin / "linhx_tho"
    goi_con.mkdir(parents=True, exist_ok=True)
    vbs_tam = thu_muc_bin / "chay-an.vbs"
    settings_tam = thu_muc_bin / "agy-sandbox-settings.json"
    if CHAY_AN_VBS.is_file():
        shutil.copy2(CHAY_AN_VBS, vbs_tam)
    chay_an_py = THU_MUC_THO / "linhx_tho" / "_chay_an.py"
    if chay_an_py.is_file():
        shutil.copy2(chay_an_py, goi_con / "_chay_an.py")
    if CAU_HINH_SANDBOX_AGY.is_file():
        shutil.copy2(CAU_HINH_SANDBOX_AGY, settings_tam)
    return thu_muc_bin, vbs_tam, settings_tam


def _tao_cay_tam_co_lap(goc: pathlib.Path, commit_truoc: str) -> tuple[pathlib.Path, dict[str, str]]:
    """Trích xuất ảnh chụp sạch của `commit_truoc` qua `git archive` ra thư mục tạm hoàn toàn độc lập
    (không có `.git`, không liên kết ngược về repo gốc và loại bỏ sẵn mọi tệp thuộc `LUON_CAM_COMMIT`
    như `tho/**`, `canh/**`, `tests/nghiem-thu/**`, `*.khoa`, tệp ẩn).
    Trả về `(wt_tam, manifest_sha256)`.
    """
    wt_tam = pathlib.Path(tempfile.mkdtemp(prefix="linhx-tho-wt-")).resolve()
    manifest: dict[str, str] = {}
    try:
        proc = subprocess.Popen(
            [
                "git",
                "-c",
                "core.hooksPath=NUL",
                "-c",
                "core.fsmonitor=false",
                "archive",
                "--format=tar",
                commit_truoc,
            ],
            cwd=str(goc),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=CO_KHONG_CUA_SO,
        )
        assert proc.stdout is not None and proc.stderr is not None
        with tarfile.open(fileobj=proc.stdout, mode="r|") as tf:
            for member in tf:
                if not member.isfile():
                    continue
                rel = member.name.replace("\\", "/").lstrip("/")
                if not rel or _khop_glob(rel, LUON_CAM_COMMIT):
                    continue
                cac_phan = rel.split("/")
                if ":" in rel or any(not _phan_duong_dan_hop_le_ntfs(p) for p in cac_phan):
                    continue
                dich = (wt_tam / rel).resolve()
                if wt_tam not in dich.parents:
                    continue
                luong = tf.extractfile(member)
                if luong is None:
                    continue
                du_lieu = luong.read()
                dich.parent.mkdir(parents=True, exist_ok=True)
                dich.write_bytes(du_lieu)
                manifest[rel] = hashlib.sha256(du_lieu).hexdigest()
        err_bytes = proc.stderr.read()
        rc = proc.wait(timeout=30)
        if rc != 0:
            raise RuntimeError(
                f"Không thể trích xuất cây tạm từ commit {commit_truoc}: {err_bytes.decode('utf-8', 'replace').strip()}"
            )
        return wt_tam, manifest
    except Exception:
        shutil.rmtree(wt_tam, ignore_errors=True)
        raise


def _liet_ke_thay_doi_cay_tam(wt_tam: pathlib.Path, manifest_truoc: dict[str, str]) -> list[str]:
    """Quét trực tiếp hệ tệp của cây tạm (không theo symlink, không phụ thuộc `.gitignore`)
    và trả danh sách mọi đường dẫn thêm mới, sửa đổi hoặc bị xoá so với `manifest_truoc`.
    """
    goc_tam = wt_tam.resolve()
    truoc_thap = {k.lower(): (k, v) for k, v in manifest_truoc.items()}
    hien_tai_thap: set[str] = set()
    thay_doi: list[str] = []

    for dirpath, dirnames, filenames in os.walk(goc_tam, followlinks=False):
        thu_muc_ht = pathlib.Path(dirpath)
        giu_dir: list[str] = []
        for d in dirnames:
            p_dir = thu_muc_ht / d
            rel_dir = p_dir.relative_to(goc_tam).as_posix()
            if p_dir.is_symlink():
                raise ValueError(f"Phát hiện thư mục symlink trái phép trong vùng tạm: {rel_dir}")
            if rel_dir.lower() == ".canh-tho":
                continue
            giu_dir.append(d)
        dirnames[:] = giu_dir

        for fn in filenames:
            p_tep = thu_muc_ht / fn
            rel = p_tep.relative_to(goc_tam).as_posix()
            if rel.lower().startswith(".canh-tho/"):
                continue
            if p_tep.is_symlink():
                raise ValueError(f"Phát hiện tệp symlink trái phép trong vùng tạm: {rel}")
            rel_thap = rel.lower()
            hien_tai_thap.add(rel_thap)
            kich_thuoc = p_tep.stat().st_size
            if kich_thuoc > 2 * 1024 * 1024:
                thay_doi.append(rel)
                continue
            bam_moi = hashlib.sha256(p_tep.read_bytes()).hexdigest()
            cu = truoc_thap.get(rel_thap)
            if cu is None or cu[1] != bam_moi or cu[0] != rel:
                thay_doi.append(rel)

    for rel_thap, (rel_cu, _) in truoc_thap.items():
        if rel_thap not in hien_tai_thap:
            thay_doi.append(rel_cu)

    return list(dict.fromkeys(thay_doi))


def _dong_bo_tep_da_duyet(
    wt_nguon: pathlib.Path,
    goc_dich: pathlib.Path,
    tep_duyet: list[str],
) -> None:
    """Chỉ sao chép nội dung nhị phân thuần của các tệp đã vượt qua kiểm duyệt vùng và bí mật về repo đích."""
    for rel in tep_duyet:
        _kiem_khong_symlink_cha(wt_nguon, rel)
        _kiem_khong_symlink_cha(goc_dich, rel)
        nguon = wt_nguon / rel
        dich = goc_dich / rel
        if nguon.is_symlink() or dich.is_symlink():
            raise ValueError(f"Nguồn hoặc đích chứa symlink không an toàn: {rel}")
        if nguon.is_file():
            dich.parent.mkdir(parents=True, exist_ok=True)
            dich.write_bytes(nguon.read_bytes())
        elif not nguon.exists() and dich.is_file():
            dich.unlink()


def chay_agy_an(
    phieu: dict,
    thu_muc: str | pathlib.Path,
    lenh_agy_bin: str | None = None,
    timeout_giay: int = 2400,
    ds_bi_mat: tuple[str, ...] | list[str] | None = None,
) -> dict:
    """Chạy `agy` ẩn qua `chay-an.vbs` + `CREATE_NO_WINDOW` bên trong cây tạm tách rời hoàn toàn,
    chỉ sao chép tệp đã duyệt về `thu_muc` và tự hoàn tác nếu thất bại.
    """
    ma_phieu, loai, vung = _kiem_phieu_hop_le(phieu, bat_buoc_co_vung=True)
    goc = pathlib.Path(thu_muc).resolve()

    commit_truoc_r = _chay_git(goc, "rev-parse", "HEAD")
    commit_truoc = commit_truoc_r.stdout.strip() if commit_truoc_r.returncode == 0 else ""
    if not commit_truoc:
        raise ValueError("Thư mục làm việc phải là git repository đã khởi tạo commit gốc")

    ban_truoc = [
        p
        for p in _liet_ke_thay_doi_porcelain(goc)
        if p and not p.lower().startswith(".canh-tho/") and p.lower() != ".canh-tho"
    ]
    if ban_truoc:
        raise RuntimeError("Worktree đích đang có thay đổi chưa commit; từ chối chạy để tránh trộn lẫn tệp")

    ghi_phieu_md(phieu, goc)
    dau_van_git_truoc = _dau_van_git_noi_bo(goc)

    canh_tho = goc / ".canh-tho"
    tap_out = canh_tho / f"agy-{ma_phieu}.jsonl"
    tap_err = canh_tho / f"agy-{ma_phieu}.err"
    tap_pid = canh_tho / f"agy-{ma_phieu}.pid"
    if tap_pid.exists():
        tap_pid.unlink()

    agy_exe = tim_lenh_agy(lenh_agy_bin)
    duong_agy = pathlib.Path(agy_exe).resolve()
    if not duong_agy.is_file():
        raise FileNotFoundError(f"Không tìm thấy tệp thực thi agy: {agy_exe}")
    if duong_agy.suffix.lower() in _DUOI_SCRIPT_CAM:
        raise ValueError(f"Tệp thực thi agy không được là kịch bản shell/script: {duong_agy.suffix}")
    if duong_agy == goc or goc in duong_agy.parents:
        raise ValueError("Tệp thực thi agy không được nằm bên trong thư mục làm việc của phiếu")
    agy_exe = str(duong_agy)

    thu_muc_bin, vbs_co_lap, settings_co_lap = _tao_thu_muc_runner_co_lap()
    wt_tam: pathlib.Path | None = None
    thanh_cong_chay = False

    try:
        wt_tam, manifest_wt_truoc = _tao_cay_tam_co_lap(goc, commit_truoc)
        ghi_phieu_md(phieu, wt_tam)
        thu_muc_chay_agy = wt_tam

        tham_so_agy = _tham_so_agy_co_dinh(
            loai_phieu=loai,
            timeout_giay=timeout_giay,
            tep_settings=settings_co_lap if settings_co_lap.is_file() else CAU_HINH_SANDBOX_AGY,
        )

        wscript_he_thong = pathlib.Path(os.environ.get("SYSTEMROOT", r"C:\Windows")) / "System32" / "wscript.exe"
        wscript_exe = str(wscript_he_thong) if wscript_he_thong.is_file() else (shutil.which("wscript.exe") or "")
        co_wscript = os.name == "nt" and vbs_co_lap.is_file() and bool(wscript_exe)

        env_sach = _tao_env_sach()
        bat_dau = time.monotonic()

        if co_wscript:
            env_vbs = dict(env_sach)
            env_vbs["LINHX_THO_PYTHON"] = sys.executable
            env_vbs["LINHX_THO_EXE"] = agy_exe
            env_vbs["LINHX_THO_ARGS_JSON"] = json.dumps(tham_so_agy, ensure_ascii=False)
            env_vbs["LINHX_THO_CWD"] = str(thu_muc_chay_agy)
            env_vbs["LINHX_THO_STDOUT"] = str(tap_out)
            env_vbs["LINHX_THO_STDERR"] = str(tap_err)
            env_vbs["LINHX_THO_PID_FILE"] = str(tap_pid)
            env_vbs["LINHX_THO_TIMEOUT"] = str(int(timeout_giay))
            lenh_thuc_thi = [wscript_exe, "//B", str(vbs_co_lap), agy_exe, *tham_so_agy]

            proc = subprocess.Popen(
                lenh_thuc_thi,
                cwd=str(thu_muc_bin),
                env=env_vbs,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=CO_KHONG_CUA_SO,
            )
            job_handle = _gan_job_kill_on_close(proc.pid)
            try:
                ma_thoat = int(proc.wait(timeout=timeout_giay + 30))
            except subprocess.TimeoutExpired as exc:
                _giet_cay_tien_trinh(proc.pid)
                if tap_pid.is_file():
                    try:
                        pid_con = int(tap_pid.read_text(encoding="utf-8").strip())
                        _giet_cay_tien_trinh(pid_con)
                    except (OSError, ValueError):
                        pass
                try:
                    proc.kill()
                except OSError:
                    pass
                raise TimeoutError(f"Tiến trình agy vượt quá thời gian cho phép ({timeout_giay}s)") from exc
            finally:
                _dong_job(job_handle)
        else:
            lenh_thuc_thi = [agy_exe, *tham_so_agy]
            with open(tap_out, "wb") as f_out, open(tap_err, "wb") as f_err:
                proc = subprocess.Popen(
                    lenh_thuc_thi,
                    cwd=str(thu_muc_chay_agy),
                    env=env_sach,
                    stdin=subprocess.DEVNULL,
                    stdout=f_out,
                    stderr=f_err,
                    creationflags=CO_KHONG_CUA_SO,
                )
                job_handle = _gan_job_kill_on_close(proc.pid)
                try:
                    ma_thoat = int(proc.wait(timeout=timeout_giay))
                except subprocess.TimeoutExpired as exc:
                    _giet_cay_tien_trinh(proc.pid)
                    try:
                        proc.kill()
                    except OSError:
                        pass
                    raise TimeoutError(f"Tiến trình agy vượt quá thời gian cho phép ({timeout_giay}s)") from exc
                finally:
                    _dong_job(job_handle)

        if ma_thoat == 124:
            raise TimeoutError(f"Tiến trình agy vượt quá thời gian cho phép ({timeout_giay}s)")
        if ma_thoat != 0:
            raise RuntimeError(f"Tiến trình agy kết thúc với mã thoát khác 0 ({ma_thoat})")

        phut = round(max(0.0, (time.monotonic() - bat_dau) / 60.0), 2)
        if _dau_van_git_noi_bo(goc) != dau_van_git_truoc:
            raise RuntimeError("Phát hiện thay đổi trái phép bên trong .git/config hoặc .git/hooks sau khi chạy agy")

        ds_moi_wt = _liet_ke_thay_doi_cay_tam(wt_tam, manifest_wt_truoc)
        tep_duyet = _kiem_va_chon_tep_stage(wt_tam, ds_moi_wt, vung, loai, ds_bi_mat=ds_bi_mat)
        if not tep_duyet:
            raise RuntimeError(
                f"Phiếu {ma_phieu} chưa tạo thay đổi hợp lệ trong vùng cho phép ({', '.join(vung)})"
            )
        _dong_bo_tep_da_duyet(wt_tam, goc, tep_duyet)

        noi_dung_out = tap_out.read_text(encoding="utf-8", errors="replace") if tap_out.exists() else ""
        token_vao, token_ra = _phan_tich_stream_json(noi_dung_out)
        tong_token = token_vao + token_ra

        commit_sha, nhanh = _dam_bao_commit_ket_qua(
            goc,
            ma_phieu,
            loai,
            vung,
            commit_truoc,
            ds_bi_mat=ds_bi_mat,
        )
        thanh_cong_chay = True
        return {
            "ma_phieu": ma_phieu,
            "da_goi_agy": True,
            "cua_so_an": True,
            "ma_thoat": ma_thoat,
            "commit": commit_sha,
            "nhanh": nhanh,
            "phut": phut,
            "token_vao": token_vao,
            "token_ra": token_ra,
            "token": tong_token,
            "nhat_ky": f"ma_thoat={ma_thoat}; phut={phut}; token_vao={token_vao}; token_ra={token_ra}; token={tong_token}",
            "lenh_agy": lenh_thuc_thi,
        }
    finally:
        if wt_tam is not None:
            shutil.rmtree(wt_tam, ignore_errors=True)
        shutil.rmtree(thu_muc_bin, ignore_errors=True)
        if not thanh_cong_chay:
            _hoan_tac_worktree(goc, commit_truoc)


class _ChanRedirectHandler(urlrequest.HTTPRedirectHandler):
    """Chặn mọi HTTP redirect (301/302/303/307/308) để không rò header `X-Tho-Khoa` sang host khác."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urlerror.HTTPError(
            req.full_url,
            code,
            "Chặn HTTP redirect để bảo vệ khoá xác thực thợ",
            headers,
            fp,
        )


def _kiem_url_api(api_url: str) -> str:
    """Bắt buộc `https://` cho máy chủ từ xa; chỉ cho phép `http://` trên loopback cục bộ."""
    u = str(api_url or "").strip().rstrip("/")
    parsed = urlparse(u)
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("URL API không được chứa thông tin đăng nhập, query hoặc fragment")
    host = (parsed.hostname or "").lower()
    if not host:
        raise ValueError(f"URL API thiếu hostname: {api_url!r}")
    if parsed.scheme == "https":
        return u
    if parsed.scheme == "http" and host in ("127.0.0.1", "localhost", "::1"):
        return u
    raise ValueError(
        f"URL API từ xa bắt buộc dùng https:// (chỉ cho phép http:// với 127.0.0.1/localhost): {api_url!r}"
    )


def _lam_sach_nhat_ky(
    nhat_ky: object,
    ds_bi_mat: tuple[str, ...] | list[str] | None = None,
) -> str:
    """Chỉ giữ tóm tắt số liệu/trạng thái ngắn, lọc bỏ email, SĐT, đường dẫn và mọi khoá đang dùng."""
    chu = str(nhat_ky or "").strip()
    if not chu:
        return ""
    for bm in _thu_thap_gia_tri_bi_mat(ds_bi_mat):
        flags = re.IGNORECASE if len(bm) >= 8 else 0
        chu = re.sub(re.escape(bm), "[REDACTED]", chu, flags=flags)
    for mau in _MAU_NOI_DUNG_BI_MAT:
        chu = mau.sub("[REDACTED]", chu)
    chu = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[EMAIL]", chu)
    chu = re.sub(r"\b(?:\+?84|0)\d{8,10}\b", "[SDT]", chu)
    chu = re.sub(r"[A-Za-z]:\\[^\s;]+", "[PATH]", chu)
    chu = re.sub(r"(?<![A-Za-z0-9])/(?:home|root|Users|tmp|var|etc)/[^\s;]+", "[PATH]", chu)
    chu = re.sub(r"[\r\n]+", " ", chu)
    return chu[:200]


def _goi_json_http(url: str, payload: dict, khoa_tho: str) -> tuple[int, dict]:
    """Gửi POST JSON không theo redirect; khoá thợ chỉ nằm ở header `X-Tho-Khoa`, không đặt trong body."""
    if "khoa" in payload or "khoa_tran" in payload:
        raise ValueError("Không được gửi khoá xác thực thợ trong thân JSON")
    du_lieu_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urlrequest.Request(
        url,
        data=du_lieu_bytes,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
            "X-Tho-Khoa": khoa_tho,
        },
        method="POST",
    )
    ssl_ctx = ssl.create_default_context()
    opener = urlrequest.build_opener(
        _ChanRedirectHandler(),
        urlrequest.HTTPSHandler(context=ssl_ctx),
    )
    try:
        with opener.open(req, timeout=30) as resp:
            ma = int(resp.status)
            than_raw = resp.read(1024 * 1024).decode("utf-8", errors="replace")
    except urlerror.HTTPError as exc:
        ma = int(exc.code)
        than_raw = exc.read(65536).decode("utf-8", errors="replace") if exc.fp else ""
    try:
        than = json.loads(than_raw) if than_raw else {}
    except Exception:
        than = {"loi": "phan_hoi_khong_phai_json"}
    if isinstance(than, dict) and isinstance(than.get("message"), dict):
        than = than["message"]
    return ma, than if isinstance(than, dict) else {"du_lieu": than}


def keo_phieu_http(
    api_url: str,
    ma_tho: str,
    khoa_tho: str,
    khoa_hmac: str | None = None,
    *,
    kho_nonce: pathlib.Path | str | set[str] | None = None,
    ghi_nhan_nonce: bool = True,
) -> dict | None:
    """Gọi API Frappe `/api/method/linhx_core.ops.api_tho.keo` và bắt buộc kiểm chữ ký HMAC + chống phát lại."""
    goc = _kiem_url_api(api_url)
    ma = str(ma_tho or "").strip()
    if not ma or not _MAU_MA_THO.match(ma):
        raise ValueError(f"Mã thợ không hợp lệ: {ma_tho!r}")
    if not isinstance(khoa_tho, str) or not khoa_tho:
        raise ValueError("Thiếu khoá xác thực thợ")

    khoa_ky = (
        khoa_hmac
        if isinstance(khoa_hmac, str) and khoa_hmac.strip()
        else os.environ.get("LINHX_PHIEU_HMAC_KHOA", "").strip()
    )
    if not khoa_ky:
        raise ValueError("Thiếu khoá HMAC kiểm tra chữ ký phiếu (LINHX_PHIEU_HMAC_KHOA)")

    kho_nonce_thuc = kho_nonce
    if kho_nonce_thuc is None and ghi_nhan_nonce:
        kho_nonce_thuc = _thu_muc_trang_thai_tho() / "nonce-da-dung.json"

    ma_http, than = _goi_json_http(
        f"{goc}/api/method/linhx_core.ops.api_tho.keo",
        {"ma_tho": ma},
        khoa_tho,
    )
    if ma_http != 200 or not than.get("ok"):
        raise RuntimeError(f"Kéo phiếu thất bại (HTTP {ma_http}): {than.get('loi', 'unknown')}")
    phieu = than.get("phieu")
    if phieu is None:
        return None
    if not isinstance(phieu, dict):
        raise ValueError("Dữ liệu phiếu từ Frappe không hợp lệ")
    if "ma_phieu" not in phieu and "name" in phieu:
        phieu["ma_phieu"] = phieu["name"]
    tho_giao = str(phieu.get("tho") or "").strip()
    if tho_giao != ma:
        raise ValueError(f"Phiếu không được ký giao cho thợ hiện tại ({tho_giao!r} != {ma!r})")
    _kiem_phieu_hop_le(phieu, bat_buoc_co_vung=True)
    if not xac_thuc_chu_ky_phieu(
        phieu,
        khoa_ky,
        ma_tho=ma,
        kho_nonce=kho_nonce_thuc,
        ghi_nhan_nonce=ghi_nhan_nonce,
    ):
        raise ValueError("Chữ ký HMAC, hạn dùng hoặc nonce của phiếu từ Frappe không hợp lệ / đã phát lại")
    return phieu


def nop_phieu_http(
    api_url: str,
    ma_tho: str,
    khoa_tho: str,
    ket_qua_chay: dict,
    *,
    ds_bi_mat: tuple[str, ...] | list[str] | None = None,
) -> dict:
    """Gọi API Frappe `/api/method/linhx_core.ops.api_tho.nop` (khoá chỉ qua header, nhật ký đã lọc sạch)."""
    goc = _kiem_url_api(api_url)
    ma = str(ma_tho or "").strip()
    if not ma or not _MAU_MA_THO.match(ma):
        raise ValueError(f"Mã thợ không hợp lệ: {ma_tho!r}")
    if not isinstance(khoa_tho, str) or not khoa_tho:
        raise ValueError("Thiếu khoá xác thực thợ")
    bi_mat_gop = [khoa_tho, *(ds_bi_mat or ())]
    payload = {
        "ma_tho": ma,
        "ma_phieu": ket_qua_chay["ma_phieu"],
        "commit": ket_qua_chay["commit"],
        "nhanh": ket_qua_chay["nhanh"],
        "nhat_ky": _lam_sach_nhat_ky(ket_qua_chay.get("nhat_ky", ""), ds_bi_mat=bi_mat_gop),
        "phut": ket_qua_chay["phut"],
        "token": ket_qua_chay["token"],
    }
    ma_http, than = _goi_json_http(
        f"{goc}/api/method/linhx_core.ops.api_tho.nop",
        payload,
        khoa_tho,
    )
    if ma_http != 200 or not than.get("ok"):
        raise RuntimeError(f"Nộp phiếu thất bại (HTTP {ma_http}): {than.get('loi', 'unknown')}")
    return than


def chay_mot_phieu(
    phieu: dict | None,
    thu_muc: str | pathlib.Path,
    *,
    chay_thu: bool = False,
    api_url: str | None = None,
    ma_tho: str = "tho-1",
    khoa_tho: str | None = None,
    khoa_hmac: str | None = None,
    lenh_agy_bin: str | None = None,
    bang_chung_out: str | pathlib.Path | None = None,
    kho_nonce: pathlib.Path | str | set[str] | None = None,
) -> dict:
    """Thực thi trọn chu trình của thợ: kéo phiếu -> kiểm đề -> ghi PHIEU.md -> chạy agy ẩn -> nộp phiếu.
    Khi không `--chay-thu`, bắt buộc xác thực chữ ký HMAC-SHA256 kèm `tho`, `han_dung` và `nonce`
    cho cả phiếu kéo qua HTTP lẫn phiếu đọc từ `--phieu-json`.
    """
    goc_thu_muc = pathlib.Path(thu_muc).resolve()
    if phieu is not None and chay_thu:
        return ke_hoach_chay(phieu, str(goc_thu_muc))

    khoa_ky = (
        khoa_hmac.strip()
        if isinstance(khoa_hmac, str) and khoa_hmac.strip()
        else os.environ.get("LINHX_PHIEU_HMAC_KHOA", "").strip()
    )
    if not khoa_ky:
        raise ValueError("Khi chạy thật (không --chay-thu), bắt buộc cấu hình khoá HMAC (LINHX_PHIEU_HMAC_KHOA)")

    if kho_nonce is None:
        thu_muc_tt = _thu_muc_trang_thai_tho()
        if thu_muc_tt == goc_thu_muc or goc_thu_muc in thu_muc_tt.parents:
            raise ValueError("Thư mục trạng thái/khoá của thợ không được nằm bên trong worktree của phiếu")
        kho_nonce_thuc: pathlib.Path | str | set[str] = thu_muc_tt / "nonce-da-dung.json"
    else:
        kho_nonce_thuc = kho_nonce

    if phieu is None:
        if not api_url:
            raise ValueError("Cần cung cấp --phieu-json hoặc --api-url để kéo phiếu")
        phieu = keo_phieu_http(
            api_url,
            ma_tho,
            khoa_tho or "",
            khoa_hmac=khoa_ky,
            kho_nonce=kho_nonce_thuc,
            ghi_nhan_nonce=not chay_thu,
        )
        if phieu is None:
            return {"ok": True, "phieu": None, "da_goi_agy": False}
    else:
        if not xac_thuc_chu_ky_phieu(
            phieu,
            khoa_ky,
            ma_tho=ma_tho,
            kho_nonce=kho_nonce_thuc,
            ghi_nhan_nonce=not chay_thu,
        ):
            raise ValueError("Chữ ký HMAC, mã thợ, hạn dùng hoặc nonce của phiếu không hợp lệ / đã phát lại")

    ke_hoach = ke_hoach_chay(phieu, str(goc_thu_muc))
    if chay_thu:
        return ke_hoach
    ds_bi_mat = tuple(x for x in (khoa_tho or "", khoa_ky) if x)
    kq_agy = chay_agy_an(
        phieu,
        goc_thu_muc,
        lenh_agy_bin=lenh_agy_bin,
        ds_bi_mat=ds_bi_mat,
    )
    trang_thai_cuoi = "nop"
    if api_url:
        kq_nop = nop_phieu_http(
            api_url,
            ma_tho,
            khoa_tho or "",
            kq_agy,
            ds_bi_mat=ds_bi_mat,
        )
        phieu_sau_nop = kq_nop.get("phieu") if isinstance(kq_nop, dict) else None
        if isinstance(phieu_sau_nop, dict) and phieu_sau_nop.get("trang_thai") in ("nop", "dat"):
            trang_thai_cuoi = phieu_sau_nop["trang_thai"]

    ket_qua = {
        "luc": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "may": platform.node() or os.environ.get("COMPUTERNAME", "windows-tho"),
        "ma_phieu": kq_agy["ma_phieu"],
        "tho": ma_tho,
        "trang_thai_cuoi": trang_thai_cuoi,
        "commit": kq_agy["commit"],
        "nhanh": kq_agy["nhanh"],
        "phut": kq_agy["phut"],
        "token": kq_agy["token"],
        "token_vao": kq_agy["token_vao"],
        "token_ra": kq_agy["token_ra"],
        "cua_so_an": True,
        "buoc": list(BUOC_CHUAN),
        "da_goi_agy": True,
    }
    if bang_chung_out:
        duong_bc = pathlib.Path(bang_chung_out)
        duong_bc.parent.mkdir(parents=True, exist_ok=True)
        duong_bc.write_text(json.dumps(ket_qua, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return ket_qua


def _tao_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="linhx_tho",
        description="Trình thợ Windows kéo phiếu Agy từ Frappe, chạy agy ẩn và nộp kết quả",
    )
    parser.add_argument(
        "--phieu-json",
        dest="phieu_json",
        default=None,
        help="Đường dẫn tới file JSON chứa thông tin phiếu",
    )
    parser.add_argument(
        "--thu-muc",
        dest="thu_muc",
        default=".",
        help="Thư mục gốc repo/worktree để chạy phiếu (mặc định: thư mục hiện tại)",
    )
    parser.add_argument(
        "--chay-thu",
        dest="chay_thu",
        action="store_true",
        help="Chỉ kiểm tra đề và in JSON kế hoạch các bước, không gọi agy thật",
    )
    parser.add_argument(
        "--api-url",
        dest="api_url",
        default=os.environ.get("LINHX_API_URL") or None,
        help="URL gốc của Frappe (https://... hoặc http://127.0.0.1) để kéo và nộp phiếu",
    )
    parser.add_argument(
        "--ma-tho",
        dest="ma_tho",
        default=os.environ.get("LINHX_MA_THO") or "tho-1",
        help="Mã định danh thợ (mặc định: tho-1)",
    )
    parser.add_argument(
        "--lenh-agy",
        dest="lenh_agy",
        default=None,
        help="Đường dẫn thực thi agy.exe (mặc định: tự tìm ~/.gemini/bin/agy.exe)",
    )
    parser.add_argument(
        "--bang-chung",
        dest="bang_chung",
        default=None,
        help="Đường dẫn file JSON ghi bằng chứng kết quả chạy phiếu thật",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _tao_parser()
    args = parser.parse_args(argv)

    try:
        phieu = None
        if args.phieu_json:
            duong_p = pathlib.Path(args.phieu_json)
            phieu = json.loads(duong_p.read_text(encoding="utf-8"))
            if not isinstance(phieu, dict):
                raise ValueError("File --phieu-json phải là một JSON object")

        khoa_tho = os.environ.get("LINHX_THO_KHOA", "")
        khoa_hmac = os.environ.get("LINHX_PHIEU_HMAC_KHOA", "")
        ket_qua = chay_mot_phieu(
            phieu=phieu,
            thu_muc=args.thu_muc,
            chay_thu=args.chay_thu,
            api_url=args.api_url,
            ma_tho=args.ma_tho,
            khoa_tho=khoa_tho,
            khoa_hmac=khoa_hmac,
            lenh_agy_bin=args.lenh_agy,
            bang_chung_out=args.bang_chung,
        )
    except Exception as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(ket_qua, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
