r"""linhx-runner: tho nhan viec cua LINHX ENGINE.

Chay o bat cu dau (may cty Windows, MSI, container tren cloud). Chi KEO viec qua HTTPS,
khong mo cong. Server chi gui DE (chu), khong bao gio gui lenh shell.

Cau hinh bang bien moi truong hoac file tho.env canh script:
  LINHX_NGUON   engine (mac dinh) hoac github (nhanh hang-doi)
  LINHX_URL     vd https://engine.linhx.vn
  LINHX_TOKEN   key:secret (bench execute linhx_worker.setup.tao_tho)
  LINHX_THO     ma tho, vd may-cty / may-1
  AGY_CMD       duong dan agy (mac dinh: agy)
  AGY_ARGS      them co cho agy (mac dinh: --output-format json)
  LINHX_MODEL   ten model agy mac dinh khi phieu khong co header model: (vd gemini-4-argon-high)
  LINHX_THU_MUC thu muc lam viec cua agy (mac dinh: ./viec)
  LINHX_NGHI    giay giua 2 lan hoi (mac dinh 15)
  LINHX_SO_PHIEU        so phieu code chay song song toi da tren moi may (mac dinh 1)
  LINHX_NHAN_BAT_KY     1 (mac dinh, nhan ca phieu bat-ky) hoac 0 (chi nhan phieu dich danh may)
  LINHX_TRAN_PHUT       tran phut toi da moi phieu truoc khi dung agy (mac dinh 40)
  LINHX_KHONG_TIEN_PHUT so phut khong tien truoc khi dung agy (mac dinh 20)
  LINHX_RAM_TOI_THIEU_GB nguong RAM trong toi thieu de nhan phieu (mac dinh 1.5)
  LINHX_GIOI_HAN_THU_MUC thu muc goc cho phep agy lam viec, vd D:\linhx
  LINHX_VAI              vai tro may ghi vao ho so may, vd "Máy chính: code, điều phối"
Chi stdlib, Python >= 3.9.
"""
from contextlib import contextmanager
import codecs
import ctypes
import json
import os
import platform
import re
import shlex
import signal
import subprocess
import sys
import threading
import time
import traceback
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

try:
    from runner import nhat_ky_agy
except ImportError:
    import nhat_ky_agy

PHIEN_BAN = "0.1.1"
DE_DAI = 6000  # ky tu; dai hon thi dua de qua file
PHUT_TOI_DA_MAC_DINH = 40
PHUT_KHONG_TIEN_MAC_DINH = 20
CUA_SO_CPU_GIAY = 120.0
NGUONG_CPU_TANG_GIAY = 0.02
NHIP_PHUT_MAC_DINH = 3.0
GIOI_HAN_DONG_NHIP = 120
NGUONG_RAM_TRONG_GB = 1.5
SO_PHIEU_CODE_MAC_DINH = 1
NHAN_BAT_KY_MAC_DINH = 1
THU_MUC_ENGINE_CAM = "d:/linhx/linhx-engine"
CO_MODEL_AGY = "--model"
MODEL_MAC_DINH_NHAN = "mac-dinh"
_MAU_TEN_MODEL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
DANH_SACH_MODEL_AGY_DA_BIET = (
    "gemini-4-carbon-medium",
    "gemini-4-carbon-high",
    "gemini-4-carbon-low",
    "gemini-4-argon-medium",
    "gemini-4-argon-high",
    "gemini-4-argon-low",
    "gemini-4-hydrogen-high",
    "gemini-4-hydrogen-xhigh",
    "gemini-4-hydrogen-medium",
    "gemini-4-hydrogen-low",
    "gemini-pro-orchestrator",
    "gemini-pro-orchestrator-argon",
    "gemini-3.8-flash-high",
    "gemini-3.8-flash-medium",
    "gemini-3.8-flash-low",
    "claude-opus-5-5-low",
    "claude-opus-5-5-medium",
    "claude-opus-5-5-high",
    "claude-sonnet-5-5-low",
    "claude-sonnet-5-5-medium",
    "claude-sonnet-5-5-high",
    "gpt-oss-120b-medium",
)
CAU_NHAC_CAN_LINH = (
    "Nếu gặp việc chỉ người làm được (đăng nhập, quyền Admin/UAC, captcha, cài phần mềm, duyệt), "
    "DỪNG việc đó và ghi khối `CAN-LINH: <việc>; LENH: <lệnh dán được nếu có>` trong câu trả lời."
)
CAU_NHAC_TIEN_CANH = "Không dùng background task hay thợ con trừ khi phiếu cho phép; chạy lệnh tiền cảnh."
LY_DO_CHO_TAC_VU_NEN = "cho-tac-vu-nen"
CAU_DAU_DE_SUA_CHO_NEN = (
    "Lượt trước bị dừng vì chạy tác vụ nền rồi chờ. "
    "Lượt này mọi lệnh phải chạy tiền cảnh, đợi xong trong cùng lệnh."
)
# Rà agy --help và mọi lệnh con (15/11/2026): không có cờ/thiết lập tắt background task hay subagent.
# Giữ tuple móc cấu hình nếu phiên bản agy sau này bổ sung cờ tắt chạy nền.
AGY_CO_TAT_NEN: tuple[str, ...] = ()
GOC = Path(__file__).resolve().parent
TEP_MODEL_THEO_LOAI = GOC / "model-theo-loai.json"

_SUBPROCESS_RUN_GOC = subprocess.run
_POPEN_GOC = subprocess.Popen
_tao_tien_trinh_agy = None
_doc_ds_model_agy = None
_doc_cpu_cay_agy = None
_dong_ho = None
_ngu = None
_CACHE_MODEL_AGY: dict[str, tuple[float, set[str]]] = {}


def _gio() -> float:
    return _dong_ho() if _dong_ho is not None else time.monotonic()


def _tam_nghi(giay: float) -> None:
    if _ngu is not None:
        _ngu(giay)
    else:
        time.sleep(giay)


def _ep_so_duong(gia_tri, mac_dinh: float) -> float:
    if gia_tri is None:
        return float(mac_dinh)
    s = str(gia_tri).strip()
    if not s:
        return float(mac_dinh)
    try:
        v = float(s)
        return v if v > 0 else float(mac_dinh)
    except (ValueError, TypeError):
        return float(mac_dinh)


def _ep_so_nguyen_khong_am(gia_tri, mac_dinh: int = SO_PHIEU_CODE_MAC_DINH) -> int:
    if gia_tri is None:
        return int(mac_dinh)
    s = str(gia_tri).strip()
    if not s:
        return int(mac_dinh)
    try:
        return max(0, int(s))
    except (ValueError, TypeError):
        return int(mac_dinh)


def _ep_cong_tac(gia_tri, mac_dinh: bool = True) -> bool:
    # Chuyển đổi công tắc cấu hình (0/1, true/false) sang kiểu bool
    if gia_tri is None:
        return bool(mac_dinh)
    if isinstance(gia_tri, bool):
        return gia_tri
    if isinstance(gia_tri, (int, float)):
        return gia_tri != 0
    s = str(gia_tri).strip().lower()
    if not s:
        return bool(mac_dinh)
    if s in ("0", "false", "no", "off", "khong"):
        return False
    if s in ("1", "true", "yes", "on", "co"):
        return True
    try:
        return int(s) != 0
    except ValueError:
        return bool(mac_dinh)


def _dinh_dang_phut(phut: float) -> str:
    n = float(phut)
    if abs(n - round(n)) < 1e-6:
        return str(int(round(n)))
    return f"{n:g}"


def _chuan_hoa_duong_dan_so_sanh(duong_dan) -> str:
    s = str(duong_dan or "").strip().replace("\\", "/")
    while "//" in s:
        s = s.replace("//", "/")
    if len(s) > 3:
        s = s.rstrip("/")
    return s.lower()


def _la_duong_dan_win_tuyet_doi(s: str) -> bool:
    return len(s) >= 2 and s[0].isalpha() and s[1] == ":"


def kiem_tra_thu_muc_lam_viec(thu_muc, gioi_han=None) -> tuple[bool, str]:
    """Kiem tra thu_muc lam viec cua agy:
    - Cam D:\\LINHX\\LINHX-ENGINE (khong phan biet hoa thuong, trung repo tho ENGINE).
    - Khi co gioi_han (vd D:\\linhx), bat buoc thu_muc (sau khi resolve symlink) nam trong gioi_han.
    """
    if thu_muc is None or not str(thu_muc).strip():
        return False, "thiếu thư mục làm việc của agy"

    p_raw = Path(thu_muc)
    ung_vien_kiem = [_chuan_hoa_duong_dan_so_sanh(p_raw)]
    try:
        p_thuc = p_raw.resolve()
        ung_vien_kiem.append(_chuan_hoa_duong_dan_so_sanh(p_thuc))
    except OSError:
        p_thuc = p_raw

    for chuan in ung_vien_kiem:
        if chuan == THU_MUC_ENGINE_CAM or chuan.startswith(THU_MUC_ENGINE_CAM + "/"):
            return (
                False,
                r"không được dùng D:\LINHX\LINHX-ENGINE (trùng repo đang chạy thợ ENGINE)",
            )

    if gioi_han is not None and str(gioi_han).strip():
        raw_gh = str(gioi_han).strip()
        raw_tm = str(thu_muc).strip()
        if os.name != "nt" and (_la_duong_dan_win_tuyet_doi(raw_gh) or _la_duong_dan_win_tuyet_doi(raw_tm)):
            gh_cmp = _chuan_hoa_duong_dan_so_sanh(raw_gh).rstrip("/")
            tm_cmp = _chuan_hoa_duong_dan_so_sanh(raw_tm)
            # Chan '..' leo ra ngoai tren duong dan kieu Windows khi test tren POSIX
            phan_tm = []
            for phan in tm_cmp.split("/"):
                if phan in ("", "."):
                    continue
                if phan == "..":
                    if phan_tm and not _la_duong_dan_win_tuyet_doi(phan_tm[-1]):
                        phan_tm.pop()
                else:
                    phan_tm.append(phan)
            tm_sach = "/".join(phan_tm)
            if tm_sach != gh_cmp and not tm_sach.startswith(gh_cmp + "/"):
                return False, f"thư mục làm việc '{thu_muc}' nằm ngoài giới hạn '{gioi_han}'"
            return True, ""

        try:
            gh_thuc = Path(gioi_han).resolve()
            tm_thuc = p_raw.resolve()
            gh_nc = os.path.normcase(str(gh_thuc))
            tm_nc = os.path.normcase(str(tm_thuc))
            chung = os.path.commonpath([gh_nc, tm_nc])
        except (OSError, ValueError):
            return False, f"thư mục làm việc '{thu_muc}' nằm ngoài giới hạn '{gioi_han}'"
        if chung != gh_nc:
            return False, f"thư mục làm việc '{thu_muc}' nằm ngoài giới hạn '{gioi_han}'"

    return True, ""


def _tach_agy_args(chuoi_args: str) -> list[str]:
    ds = shlex.split(chuoi_args or "", posix=os.name != "nt")
    if os.name == "nt":
        sach = []
        for muc in ds:
            if len(muc) >= 2 and muc[0] == muc[-1] and muc[0] in ('"', "'"):
                muc = muc[1:-1]
            sach.append(muc)
        return sach
    return ds


def _lam_sach_gia_tri_model(gia_tri) -> str:
    # Bỏ chú thích cuối dòng (# ...) và khoảng trắng thừa
    if gia_tri is None:
        return ""
    return str(gia_tri).split("#", 1)[0].strip()


def kiem_tra_ten_model(ten_model) -> tuple[bool, str]:
    # Tên model chỉ nhận chữ, số, `-`, `.`, `_` và bắt đầu bằng chữ/số (chặn chèn cờ hoặc lệnh)
    sach = _lam_sach_gia_tri_model(ten_model)
    if not sach:
        return True, ""
    if not _MAU_TEN_MODEL.fullmatch(sach):
        return (
            False,
            f"tên model không hợp lệ '{sach}' (chỉ nhận chữ, số, '-', '.', '_' và không bắt đầu bằng dấu)",
        )
    return True, sach


def _xoa_co_model_agy_args(ds_args: list[str]) -> list[str]:
    # Xoá mọi cờ --model <id> hoặc --model=<id> khỏi danh sách tham số AGY_ARGS
    ket_qua: list[str] = []
    i = 0
    while i < len(ds_args):
        muc = ds_args[i]
        if muc == CO_MODEL_AGY:
            i += 2 if (i + 1) < len(ds_args) else 1
            continue
        if muc.startswith(CO_MODEL_AGY + "="):
            i += 1
            continue
        ket_qua.append(muc)
        i += 1
    return ket_qua


def _trich_model_tu_agy_args(ds_args: list[str]) -> str:
    # Lấy giá trị --model sẵn có trong AGY_ARGS (nếu có)
    ket_qua = ""
    i = 0
    while i < len(ds_args):
        muc = ds_args[i]
        if muc == CO_MODEL_AGY:
            if (i + 1) < len(ds_args):
                ket_qua = ds_args[i + 1].strip()
                i += 2
            else:
                i += 1
            continue
        if muc.startswith(CO_MODEL_AGY + "="):
            ket_qua = muc.split("=", 1)[1].strip()
        i += 1
    return ket_qua


def _thay_co_model_agy_args(ds_args: list[str], ten_model: str) -> list[str]:
    # Xoá cờ --model sẵn có trong AGY_ARGS (nếu có) rồi gắn --model <ten_model>
    if not ten_model:
        return list(ds_args)
    ket_qua = _xoa_co_model_agy_args(ds_args)
    ket_qua.extend([CO_MODEL_AGY, ten_model])
    return ket_qua


def doc_bang_model_theo_loai(tep_json: str | Path | None = None) -> dict[str, str]:
    # Đọc bảng ánh xạ tiền tố loại việc -> model từ runner/model-theo-loai.json
    duong_dan = Path(tep_json) if tep_json else TEP_MODEL_THEO_LOAI
    if not duong_dan.is_file():
        return {}
    try:
        du_lieu = json.loads(duong_dan.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError, TypeError):
        return {}
    if not isinstance(du_lieu, dict):
        return {}
    ket_qua: dict[str, str] = {}
    for k, v in du_lieu.items():
        khoa = str(k or "").strip().lower()
        gia_tri = _lam_sach_gia_tri_model(v)
        if khoa and gia_tri:
            ket_qua[khoa] = gia_tri
    return ket_qua


def lay_loai_tu_ten_phieu(ma_phieu: str) -> str:
    # Tên phiếu dạng <du-an>-<loai>-<viec> -> lấy đoạn thứ 2 làm tiền tố loại việc
    sach = str(ma_phieu or "").strip()
    if sach.lower().endswith(".md"):
        sach = sach[:-3]
    cac_doan = sach.split("-")
    if len(cac_doan) < 3:
        return ""
    if not cac_doan[0].strip() or not cac_doan[1].strip():
        return ""
    if not any(d.strip() for d in cac_doan[2:]):
        return ""
    return cac_doan[1].strip().lower()


def phan_tich_dau_ra_agy_models(van_ban: str) -> list[str]:
    # Phân tích đầu ra của lệnh `agy models` (dạng `<id>\t<Tên hiển thị>` hoặc `<id>` trên từng dòng)
    ket_qua: list[str] = []
    da_thay: set[str] = set()
    for dong in str(van_ban or "").splitlines():
        s = dong.strip()
        if not s:
            continue
        ung_vien = ""
        if "\t" in dong:
            ung_vien = dong.split("\t", 1)[0].strip()
        elif " " not in s:
            ung_vien = s
        if ung_vien and _MAU_TEN_MODEL.fullmatch(ung_vien) and ung_vien not in da_thay:
            da_thay.add(ung_vien)
            ket_qua.append(ung_vien)
    return ket_qua


def lay_danh_sach_model_agy(cfg: dict | None = None, chay_lenh_fn=None) -> set[str]:
    # Lấy tập hợp model hợp lệ từ `agy models` (có bộ nhớ đệm; khi lỗi/offline thì dùng bảng đã biết)
    if cfg and cfg.get("ds_model_agy") is not None:
        return {str(m).strip() for m in cfg["ds_model_agy"] if str(m).strip()}
    if _doc_ds_model_agy is not None:
        ds = _doc_ds_model_agy(cfg)
        return {str(m).strip() for m in (ds or ()) if str(m).strip()}

    agy_cmd = str((cfg or {}).get("agy") or os.environ.get("AGY_CMD") or "agy").strip() or "agy"
    bay_gio = time.monotonic()
    if chay_lenh_fn is None and agy_cmd in _CACHE_MODEL_AGY:
        moc_cu, tap_cu = _CACHE_MODEL_AGY[agy_cmd]
        if (bay_gio - moc_cu) < 600.0 and tap_cu:
            return set(tap_cu)

    ham_chay = chay_lenh_fn or _SUBPROCESS_RUN_GOC
    kw = {"creationflags": 0x08000000} if os.name == "nt" else {}
    try:
        proc = ham_chay(
            [agy_cmd, "models"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            **kw,
        )
        if proc.returncode == 0:
            ds_parse = phan_tich_dau_ra_agy_models(proc.stdout or "")
            if ds_parse:
                tap_moi = set(ds_parse)
                if chay_lenh_fn is None:
                    _CACHE_MODEL_AGY[agy_cmd] = (bay_gio, tap_moi)
                return set(tap_moi)
    except Exception:
        pass
    return set(DANH_SACH_MODEL_AGY_DA_BIET)


def chon_model_phieu(
    cfg: dict | None,
    viec: dict | None,
    tap_model_hop_le: set[str] | None = None,
) -> dict:
    """Chọn model theo thứ tự ưu tiên:
    1. Header `model:` trong phiếu
    2. Tiền tố loại việc trong tên phiếu `<du-an>-<loai>-<viec>` (`runner/model-theo-loai.json`)
    3. Biến `LINHX_MODEL` trong `tho.env` / môi trường
    4. Giữ `AGY_ARGS` như cũ
    Nếu tên model chứa ký tự độc -> hop_le=False (báo lỗi, không chạy agy).
    Nếu model không có trong `agy models` -> ghi cảnh báo, chạy model mặc định, không lỗi.
    """
    meta_viec = (viec or {}).get("meta") if isinstance((viec or {}).get("meta"), dict) else {}
    ung_vien = ""
    nguon = "mac_dinh"

    # 1. Header `model:`
    raw_header = ""
    if meta_viec and "model" in meta_viec and _lam_sach_gia_tri_model(meta_viec.get("model")):
        raw_header = meta_viec.get("model")
    elif viec and "model" in viec and _lam_sach_gia_tri_model(viec.get("model")):
        raw_header = viec.get("model")

    if _lam_sach_gia_tri_model(raw_header):
        ok, sach = kiem_tra_ten_model(raw_header)
        if not ok:
            return {
                "hop_le": False,
                "model": "",
                "model_that": "khong-hop-le",
                "xoa_co_model": False,
                "canh_bao": "",
                "ly_do_loi": sach,
                "nguon": "header",
            }
        ung_vien = sach
        nguon = "header"

    # 2. Tiền tố loại việc trong tên phiếu `<du-an>-<loai>-<viec>`
    if not ung_vien:
        loai_tt = lay_loai_tu_ten_phieu(str((viec or {}).get("viec") or ""))
        if loai_tt:
            tep_bang = (cfg or {}).get("tep_model_theo_loai") if cfg else None
            bang_loai = doc_bang_model_theo_loai(tep_bang)
            raw_loai = bang_loai.get(loai_tt, "")
            if _lam_sach_gia_tri_model(raw_loai):
                ok, sach = kiem_tra_ten_model(raw_loai)
                if not ok:
                    return {
                        "hop_le": False,
                        "model": "",
                        "model_that": "khong-hop-le",
                        "xoa_co_model": False,
                        "canh_bao": "",
                        "ly_do_loi": sach,
                        "nguon": "tien_to",
                    }
                ung_vien = sach
                nguon = "tien_to"

    # 3. Biến `LINHX_MODEL` trong tho.env / môi trường
    if not ung_vien:
        if cfg and "model" in cfg and cfg["model"] is not None:
            raw_cfg = cfg["model"]
        else:
            raw_cfg = os.environ.get("LINHX_MODEL", "")
        if _lam_sach_gia_tri_model(raw_cfg):
            ok, sach = kiem_tra_ten_model(raw_cfg)
            if not ok:
                return {
                    "hop_le": False,
                    "model": "",
                    "model_that": "khong-hop-le",
                    "xoa_co_model": False,
                    "canh_bao": "",
                    "ly_do_loi": sach,
                    "nguon": "env",
                }
            ung_vien = sach
            nguon = "env"

    ds_agy_args = _tach_agy_args((cfg or {}).get("agy_args", "--output-format json"))
    model_san_co = _trich_model_tu_agy_args(ds_agy_args)

    # 4. Không chỉ định model -> giữ nguyên AGY_ARGS như cũ
    if not ung_vien:
        if model_san_co:
            ok_args, sach_args = kiem_tra_ten_model(model_san_co)
            if not ok_args:
                return {
                    "hop_le": False,
                    "model": "",
                    "model_that": "khong-hop-le",
                    "xoa_co_model": False,
                    "canh_bao": "",
                    "ly_do_loi": sach_args,
                    "nguon": "agy_args",
                }
            return {
                "hop_le": True,
                "model": "",
                "model_that": sach_args,
                "xoa_co_model": False,
                "canh_bao": "",
                "ly_do_loi": "",
                "nguon": "agy_args",
            }
        return {
            "hop_le": True,
            "model": "",
            "model_that": MODEL_MAC_DINH_NHAN,
            "xoa_co_model": False,
            "canh_bao": "",
            "ly_do_loi": "",
            "nguon": "mac_dinh",
        }

    # Kiểm tra model ứng viên có nằm trong `agy models` không
    tap_hop_le = tap_model_hop_le if tap_model_hop_le is not None else lay_danh_sach_model_agy(cfg)
    if tap_hop_le and ung_vien not in tap_hop_le:
        canh_bao = (
            f"[CẢNH BÁO] Model '{ung_vien}' không có trong agy models; "
            f"chuyển sang chạy model mặc định."
        )
        return {
            "hop_le": True,
            "model": "",
            "model_that": MODEL_MAC_DINH_NHAN,
            "xoa_co_model": True,
            "canh_bao": canh_bao,
            "ly_do_loi": "",
            "nguon": nguon,
        }

    return {
        "hop_le": True,
        "model": ung_vien,
        "model_that": ung_vien,
        "xoa_co_model": False,
        "canh_bao": "",
        "ly_do_loi": "",
        "nguon": nguon,
    }


def xac_dinh_model_phieu(cfg: dict | None, viec: dict | None) -> tuple[bool, str, str]:
    # Giữ hàm tương thích gọn trả (hop_le, ten_model_truyen_co, ly_do_loi)
    kq = chon_model_phieu(cfg, viec)
    if not kq["hop_le"]:
        return False, "", kq["ly_do_loi"]
    return True, kq["model"], kq["canh_bao"]


class _MemoryStatusEx(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def _doc_ram_win32_gb():
    kernel32 = getattr(getattr(ctypes, "windll", None), "kernel32", None)
    if kernel32 is None:
        return None
    st = _MemoryStatusEx()
    st.dwLength = ctypes.sizeof(_MemoryStatusEx)
    if not kernel32.GlobalMemoryStatusEx(ctypes.byref(st)):
        return None
    return float(st.ullAvailPhys) / float(1024 ** 3)


def _doc_ram_proc_meminfo_gb(duong_dan="/proc/meminfo"):
    p = Path(duong_dan)
    if not p.is_file():
        return None
    thong_so = {}
    try:
        for dong in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            if ":" not in dong:
                continue
            k, v = dong.split(":", 1)
            phan = v.strip().split()
            if phan and phan[0].isdigit():
                thong_so[k.strip()] = int(phan[0])
    except OSError:
        return None
    if "MemAvailable" in thong_so:
        return float(thong_so["MemAvailable"]) / float(1024 ** 2)
    if "MemFree" in thong_so:
        kb = thong_so["MemFree"] + thong_so.get("Buffers", 0) + thong_so.get("Cached", 0)
        return float(kb) / float(1024 ** 2)
    return None


def _doc_ram_he_thong_gb():
    """Tra ve dung luong RAM trong cua may tinh theo GB (GiB = 1024^3 byte)."""
    if os.name == "nt":
        return _doc_ram_win32_gb()
    ram = _doc_ram_proc_meminfo_gb()
    if ram is not None:
        return ram
    if hasattr(os, "sysconf"):
        try:
            trang = os.sysconf("SC_AVPHYS_PAGES")
            co_trang = os.sysconf("SC_PAGE_SIZE")
            if trang > 0 and co_trang > 0:
                return float(trang * co_trang) / float(1024 ** 3)
        except (ValueError, OSError):
            pass
    return None


lay_ram_trong_gb = _doc_ram_he_thong_gb


def du_ram_nhan_viec(cfg=None, lay_ram_fn=None):
    """Tra ve (du_ram: bool, ram_trong_gb: float | None)."""
    nguong = _ep_so_duong(
        (cfg or {}).get("nguong_ram_gb") if cfg else None,
        _ep_so_duong(os.environ.get("LINHX_RAM_TOI_THIEU_GB"), NGUONG_RAM_TRONG_GB),
    )
    ham = lay_ram_fn or lay_ram_trong_gb
    ram = ham()
    if ram is not None and ram < nguong:
        return False, ram
    return True, ram


def doc_env(tep_env=None):
    f = Path(tep_env) if tep_env else (GOC / "tho.env")
    if f.exists():
        for dong in f.read_text(encoding="utf-8-sig").splitlines():
            dong = dong.strip()
            if dong and not dong.startswith("#") and "=" in dong:
                k, v = dong.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    gioi_han_env = os.environ.get("LINHX_GIOI_HAN_THU_MUC", "").strip()
    cfg = {
        "nguon": os.environ.get("LINHX_NGUON", "engine").strip().lower(),
        "url": os.environ.get("LINHX_URL", "http://localhost:8080").rstrip("/"),
        "token": os.environ.get("LINHX_TOKEN", ""),
        "tho": os.environ.get("LINHX_THO", platform.node().lower()),
        "agy": os.environ.get("AGY_CMD", "agy"),
        "agy_args": os.environ.get("AGY_ARGS", "--output-format json"),
        "model": os.environ.get("LINHX_MODEL", "").strip(),
        "thu_muc": Path(os.environ.get("LINHX_THU_MUC", str(GOC / "viec"))),
        "gioi_han_thu_muc": Path(gioi_han_env) if gioi_han_env else None,
        "nghi": float(os.environ.get("LINHX_NGHI", "15")),
        "host": os.environ.get("LINHX_HOST", ""),
        "repo_hang_doi": Path(os.environ.get("LINHX_REPO_HANG_DOI", str(GOC.parent))),
        "nhanh_hang_doi": os.environ.get("LINHX_NHANH_HANG_DOI", "hang-doi"),
        "remote_hang_doi": os.environ.get("LINHX_REMOTE_HANG_DOI", "origin"),
        "wt_hang_doi": os.environ.get("LINHX_WT_HANG_DOI", ""),
        "thu_muc_drive": Path(os.environ["LINHX_DRIVE"]) if os.environ.get("LINHX_DRIVE", "").strip() else None,
        "thu_muc_log": Path(os.environ["LINHX_LOG_DIR"]) if os.environ.get("LINHX_LOG_DIR", "").strip() else None,
        "so_phieu": _ep_so_nguyen_khong_am(os.environ.get("LINHX_SO_PHIEU"), SO_PHIEU_CODE_MAC_DINH),
        "nhan_bat_ky": _ep_cong_tac(os.environ.get("LINHX_NHAN_BAT_KY"), bool(NHAN_BAT_KY_MAC_DINH)),
        "tran_phut": _ep_so_duong(os.environ.get("LINHX_TRAN_PHUT"), PHUT_TOI_DA_MAC_DINH),
        "khong_tien_phut": _ep_so_duong(os.environ.get("LINHX_KHONG_TIEN_PHUT"), PHUT_KHONG_TIEN_MAC_DINH),
        "nhip_phut": _ep_so_duong(os.environ.get("LINHX_NHIP_PHUT"), NHIP_PHUT_MAC_DINH),
        "nguong_ram_gb": _ep_so_duong(os.environ.get("LINHX_RAM_TOI_THIEU_GB"), NGUONG_RAM_TRONG_GB),
        "vai_tro": os.environ.get("LINHX_VAI", "").strip(),
    }
    ok_tm, _ = kiem_tra_thu_muc_lam_viec(cfg["thu_muc"], cfg["gioi_han_thu_muc"])
    if ok_tm:
        cfg["thu_muc"].mkdir(parents=True, exist_ok=True)
    return cfg


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def log_json(ban_ghi: dict) -> str:
    # Ghi một dòng JSON thuần vào luồng log của runner (stdout / tho.log)
    dong = json.dumps(ban_ghi, ensure_ascii=False)
    print(dong, flush=True)
    return dong


def _ghi_agy_raw(tep_log, phieu_id, returncode, giay, stdout, stderr, ghi_chu=""):
    try:
        p = Path(tep_log)
        p.parent.mkdir(parents=True, exist_ok=True)
        ban_ghi = {
            "luc": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "su_kien": "agy_raw",
            "viec": phieu_id,
            "returncode": returncode,
            "giay": round(giay, 2),
            "stdout": stdout,
            "stderr": stderr,
        }
        if ghi_chu:
            ban_ghi["ghi_chu"] = ghi_chu
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(ban_ghi, ensure_ascii=False) + "\n")
    except OSError:
        pass


def goi(cfg, method, **data):
    url = f"{cfg['url']}/api/method/linhx_worker.api.{method}"
    body = urllib.parse.urlencode({k: v for k, v in data.items() if v is not None}).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", f"token {cfg['token']}")
    req.add_header("Accept", "application/json")
    if cfg["host"]:
        req.add_header("Host", cfg["host"])
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode() or "{}").get("message")


def _goi_taskkill_cay(pid: int) -> None:
    """Dung taskkill /T /F tren Windows de diet ca cay tien trinh con cua agy (hoc dieu-phoi-engine.ps1)."""
    p = _POPEN_GOC(
        ["taskkill.exe", "/PID", str(pid), "/T", "/F"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=0x08000000,
    )
    p.wait(timeout=10)


def dung_tien_trinh_agy(proc) -> None:
    """Dung tien trinh agy va toan bo cay tien trinh con (hoc canh/dieu-phoi-engine.ps1)."""
    if proc is None:
        return
    try:
        if proc.poll() is not None:
            return
    except Exception:
        pass
    pid = getattr(proc, "pid", None)
    if os.name == "nt" and pid:
        try:
            _goi_taskkill_cay(int(pid))
        except Exception:
            pass
    elif pid:
        try:
            os.killpg(int(pid), signal.SIGKILL)
        except Exception:
            pass
    try:
        if proc.poll() is None:
            proc.kill()
    except Exception:
        pass
    try:
        proc.wait(timeout=5)
    except Exception:
        pass


def _tim_git_dir(thu_muc: Path):
    for tm in [thu_muc] + list(thu_muc.parents)[:3]:
        cham_git = tm / ".git"
        try:
            if cham_git.is_dir():
                return cham_git
            if cham_git.is_file():
                dong = cham_git.read_text(encoding="utf-8", errors="ignore").splitlines()
                if dong and dong[0].lower().startswith("gitdir:"):
                    gd = Path(dong[0].split(":", 1)[1].strip())
                    if not gd.is_absolute():
                        gd = (tm / gd).resolve()
                    if gd.is_dir():
                        return gd
        except OSError:
            continue
    return None


def _dau_git_head(thu_muc: Path):
    gd = _tim_git_dir(thu_muc)
    if gd is None:
        return None
    head_txt = ""
    thong_ke = []
    try:
        tep_head = gd / "HEAD"
        if tep_head.is_file():
            head_txt = tep_head.read_text(encoding="utf-8", errors="ignore").strip()
    except OSError:
        pass
    cac_tep = [gd / "HEAD", gd / "logs" / "HEAD", gd / "index"]
    if head_txt.startswith("ref:"):
        ref_rel = head_txt.split(":", 1)[1].strip()
        cac_tep.append(gd / ref_rel)
        tep_common = gd / "commondir"
        try:
            if tep_common.is_file():
                cd = Path(tep_common.read_text(encoding="utf-8", errors="ignore").strip())
                if not cd.is_absolute():
                    cd = (gd / cd).resolve()
                cac_tep.append(cd / ref_rel)
        except OSError:
            pass
    for p in cac_tep:
        try:
            st = p.stat()
            thong_ke.append((st.st_size, st.st_mtime_ns))
        except OSError:
            thong_ke.append(None)
    return (head_txt, tuple(thong_ke))


class _FILETIME(ctypes.Structure):
    _fields_ = [
        ("dwLowDateTime", ctypes.c_ulong),
        ("dwHighDateTime", ctypes.c_ulong),
    ]


class _PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", ctypes.c_ulong),
        ("cntUsage", ctypes.c_ulong),
        ("th32ProcessID", ctypes.c_ulong),
        ("th32DefaultHeapID", ctypes.c_size_t),
        ("th32ModuleID", ctypes.c_ulong),
        ("cntThreads", ctypes.c_ulong),
        ("th32ParentProcessID", ctypes.c_ulong),
        ("pcPriClassBase", ctypes.c_long),
        ("dwFlags", ctypes.c_ulong),
        ("szExeFile", ctypes.c_wchar * 260),
    ]


_K32_CPU = None


def _lay_k32_cpu():
    # Khởi tạo handle WinDLL riêng có khai báo kiểu con trỏ 64-bit an toàn cho đo CPU cây tiến trình
    global _K32_CPU
    if _K32_CPU is not None:
        return _K32_CPU
    if os.name != "nt":
        return None
    try:
        dll = ctypes.WinDLL("kernel32", use_last_error=True)
        dll.CreateToolhelp32Snapshot.argtypes = [ctypes.c_ulong, ctypes.c_ulong]
        dll.CreateToolhelp32Snapshot.restype = ctypes.c_void_p
        dll.Process32FirstW.argtypes = [ctypes.c_void_p, ctypes.POINTER(_PROCESSENTRY32W)]
        dll.Process32FirstW.restype = ctypes.c_int
        dll.Process32NextW.argtypes = [ctypes.c_void_p, ctypes.POINTER(_PROCESSENTRY32W)]
        dll.Process32NextW.restype = ctypes.c_int
        dll.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
        dll.OpenProcess.restype = ctypes.c_void_p
        dll.GetProcessTimes.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_FILETIME),
            ctypes.POINTER(_FILETIME),
            ctypes.POINTER(_FILETIME),
            ctypes.POINTER(_FILETIME),
        ]
        dll.GetProcessTimes.restype = ctypes.c_int
        dll.CloseHandle.argtypes = [ctypes.c_void_p]
        dll.CloseHandle.restype = ctypes.c_int
        _K32_CPU = dll
        return _K32_CPU
    except Exception:
        return None


def _ft_sang_u64(ft: _FILETIME) -> int:
    return (int(ft.dwHighDateTime) << 32) | int(ft.dwLowDateTime)


def _doc_cpu_cay_win32_giay(pid_goc: int, bo_nho_cay: dict | None = None) -> float:
    k32 = _lay_k32_cpu()
    if k32 is None or pid_goc <= 0:
        return 0.0
    TH32CS_SNAPPROCESS = 0x00000002
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    INVALID_HANDLE = ctypes.c_void_p(-1).value

    snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if not snap or snap == INVALID_HANDLE:
        return sum(bo_nho_cay.values()) if bo_nho_cay else 0.0

    con_theo_cha: dict[int, list[int]] = {}
    try:
        pe = _PROCESSENTRY32W()
        pe.dwSize = ctypes.sizeof(_PROCESSENTRY32W)
        ok = k32.Process32FirstW(snap, ctypes.byref(pe))
        while ok:
            p_id = int(pe.th32ProcessID)
            pp_id = int(pe.th32ParentProcessID)
            if p_id > 0:
                con_theo_cha.setdefault(pp_id, []).append(p_id)
            ok = k32.Process32NextW(snap, ctypes.byref(pe))
    finally:
        k32.CloseHandle(snap)

    cay_pid: list[int] = []
    da_duyet: set[int] = set()
    hang_doi = [int(pid_goc)]
    while hang_doi:
        hien_tai = hang_doi.pop()
        if hien_tai in da_duyet or hien_tai <= 0:
            continue
        da_duyet.add(hien_tai)
        cay_pid.append(hien_tai)
        for pid_con in con_theo_cha.get(hien_tai, ()):
            if pid_con not in da_duyet:
                hang_doi.append(pid_con)

    tong_hien_tai = 0.0
    ft_create = _FILETIME()
    ft_exit = _FILETIME()
    ft_kernel = _FILETIME()
    ft_user = _FILETIME()
    for p_id in cay_pid:
        h = k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, 0, p_id)
        if not h:
            continue
        try:
            if k32.GetProcessTimes(
                h,
                ctypes.byref(ft_create),
                ctypes.byref(ft_exit),
                ctypes.byref(ft_kernel),
                ctypes.byref(ft_user),
            ):
                cpu_giay = float(_ft_sang_u64(ft_kernel) + _ft_sang_u64(ft_user)) * 1e-7
                tong_hien_tai += cpu_giay
                if bo_nho_cay is not None:
                    khoa_proc = (p_id, _ft_sang_u64(ft_create))
                    cu = bo_nho_cay.get(khoa_proc, 0.0)
                    if cpu_giay > cu:
                        bo_nho_cay[khoa_proc] = cpu_giay
        finally:
            k32.CloseHandle(h)

    if bo_nho_cay is not None:
        return sum(bo_nho_cay.values())
    return tong_hien_tai


def _doc_cpu_cay_procfs_giay(pid_goc: int, bo_nho_cay: dict | None = None) -> float:
    goc_proc = Path("/proc")
    if pid_goc <= 0 or not goc_proc.is_dir():
        return 0.0
    try:
        clk_tck = float(os.sysconf("SC_CLK_TCK"))
        if clk_tck <= 0:
            clk_tck = 100.0
    except (AttributeError, ValueError, OSError):
        clk_tck = 100.0

    con_theo_cha: dict[int, list[int]] = {}
    thong_so_pid: dict[int, tuple[int, float]] = {}
    try:
        cac_muc = list(goc_proc.iterdir())
    except OSError:
        return sum(bo_nho_cay.values()) if bo_nho_cay else 0.0

    for muc in cac_muc:
        ten = muc.name
        if not ten.isdigit():
            continue
        p_id = int(ten)
        try:
            noi_dung = (muc / "stat").read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        vi_tri_ngoac = noi_dung.rfind(")")
        if vi_tri_ngoac < 0:
            continue
        truong = noi_dung[vi_tri_ngoac + 2 :].split()
        if len(truong) < 20:
            continue
        try:
            pp_id = int(truong[1])
            utime = int(truong[11])
            stime = int(truong[12])
            cutime = int(truong[13])
            cstime = int(truong[14])
            starttime = int(truong[19])
        except ValueError:
            continue
        con_theo_cha.setdefault(pp_id, []).append(p_id)
        cpu_ban_than = float(utime + stime) / clk_tck
        if p_id == pid_goc:
            cpu_ban_than += float(max(0, cutime) + max(0, cstime)) / clk_tck
        thong_so_pid[p_id] = (starttime, cpu_ban_than)

    da_duyet: set[int] = set()
    hang_doi = [int(pid_goc)]
    tong_hien_tai = 0.0
    while hang_doi:
        hien_tai = hang_doi.pop()
        if hien_tai in da_duyet or hien_tai <= 0:
            continue
        da_duyet.add(hien_tai)
        if hien_tai in thong_so_pid:
            st_time, cpu_g = thong_so_pid[hien_tai]
            tong_hien_tai += cpu_g
            if bo_nho_cay is not None:
                khoa_proc = (hien_tai, st_time)
                cu = bo_nho_cay.get(khoa_proc, 0.0)
                if cpu_g > cu:
                    bo_nho_cay[khoa_proc] = cpu_g
        for pid_con in con_theo_cha.get(hien_tai, ()):
            if pid_con not in da_duyet:
                hang_doi.append(pid_con)

    if bo_nho_cay is not None:
        return sum(bo_nho_cay.values())
    return tong_hien_tai


def doc_cpu_cay_tien_trinh(pid: int, bo_nho_cay: dict | None = None) -> float:
    """Đọc tổng thời gian CPU (giây) của toàn bộ cây tiến trình gốc `pid`."""
    if pid is None or int(pid) <= 0:
        return 0.0
    if os.name == "nt":
        return _doc_cpu_cay_win32_giay(int(pid), bo_nho_cay=bo_nho_cay)
    return _doc_cpu_cay_procfs_giay(int(pid), bo_nho_cay=bo_nho_cay)


def cpu_tang_trong_cua_so(
    lich_su_cpu: list[tuple[float, float]],
    bay_gio: float,
    cpu_moi: float,
    cpu_moc_cu: float,
    cua_so_giay: float = CUA_SO_CPU_GIAY,
    nguong_giay: float = NGUONG_CPU_TANG_GIAY,
) -> tuple[bool, float]:
    """Kiểm tra tổng CPU của cây tiến trình agy có tăng trong cửa sổ 2 phút gần nhất không."""
    bien_duoi = bay_gio - max(0.0, float(cua_so_giay))
    # Giữ lại 1 mẫu ngay trước biên dưới (nếu có) làm mốc đầu cửa sổ 2 phút và các mẫu trong cửa sổ
    mau_truoc_bien = None
    trong_cua_so: list[tuple[float, float]] = []
    for t_mau, v_mau in lich_su_cpu:
        if t_mau < bien_duoi:
            mau_truoc_bien = (t_mau, v_mau)
        else:
            trong_cua_so.append((t_mau, v_mau))
    lich_su_cpu.clear()
    if mau_truoc_bien is not None:
        lich_su_cpu.append(mau_truoc_bien)
    lich_su_cpu.extend(trong_cua_so)
    lich_su_cpu.append((bay_gio, float(cpu_moi)))

    if len(lich_su_cpu) < 2:
        return False, float(cpu_moc_cu)

    cpu_nho_nhat_cua_so = min(v for _, v in lich_su_cpu[:-1])
    co_tang = (float(cpu_moi) > float(cpu_moc_cu)) and (
        (float(cpu_moi) - cpu_nho_nhat_cua_so) >= float(nguong_giay)
    )
    if co_tang:
        return True, float(cpu_moi)
    return False, float(cpu_moc_cu)


def _dau_thu_muc_nhanh(thu_muc: Path, gioi_han_tep: int = 50000):
    if not thu_muc.is_dir():
        return (0, 0, 0, 0)
    so_tep = 0
    tong_co = 0
    max_mtime = 0
    dau_xor = 0
    bo_qua_tm = {".git", "node_modules", ".venv", "venv"}
    try:
        for goc_con, ds_tm, ds_tep in os.walk(str(thu_muc)):
            ds_tm[:] = [d for d in ds_tm if d not in bo_qua_tm]
            for ten in ds_tep:
                if so_tep >= gioi_han_tep:
                    return (so_tep, tong_co, max_mtime, dau_xor)
                duong = os.path.join(goc_con, ten)
                try:
                    st = os.stat(duong)
                except OSError:
                    continue
                so_tep += 1
                tong_co += st.st_size
                if st.st_mtime_ns > max_mtime:
                    max_mtime = st.st_mtime_ns
                dau_xor ^= hash((duong, st.st_size, st.st_mtime_ns))
    except OSError:
        pass
    return (so_tep, tong_co, max_mtime, dau_xor)


def _dau_nhip_tien_do(thu_muc: Path, dem_byte, tep_log=None, them_thu_muc=()):
    dau_log = None
    if tep_log:
        try:
            st = Path(tep_log).stat()
            dau_log = (st.st_size, st.st_mtime_ns)
        except OSError:
            dau_log = None
    return (
        dem_byte[0],
        dem_byte[1],
        _dau_thu_muc_nhanh(thu_muc),
        _dau_git_head(thu_muc),
        dau_log,
        tuple((_dau_thu_muc_nhanh(Path(t)), _dau_git_head(Path(t))) for t in them_thu_muc),
    )


def _thu_muc_theo_doi(meta_viec: dict, viec: dict | None = None) -> tuple:
    """Phieu ghi `theo_doi: C:\\a; D:\\b` khi agy lam viec ngoai thu muc phieu (vd repo clone rieng).
    Thay doi trong cac thu muc nay cung tinh la tien (tranh dung oan khi agy chay orchestration)."""
    gia_tri = (meta_viec or {}).get("theo_doi") or ((viec or {}).get("theo_doi") if isinstance(viec, dict) else "") or ""
    sach = str(gia_tri).split("#", 1)[0]
    return tuple(t.strip() for t in sach.split(";") if t.strip() and Path(t.strip()).is_dir())


_MAU_WAITING_BG_RE = re.compile(r"waiting\s+up\s+to\b.*\bbackground\s+task", re.IGNORECASE)
_MAU_ROOT_IDLE_RE = re.compile(r"\broot\s+agent\s+idle\b", re.IGNORECASE)
_MAU_STATUS_ERROR_RE = re.compile(r'(?:"status"\s*:\s*"error"|\bstatus\s*[:=]\s*error\b)', re.IGNORECASE)
_MAU_STATUS_SUCCESS_RE = re.compile(r'"status"\s*:\s*"(?:success|ok|done)"', re.IGNORECASE)
_MAU_UNICODE_ESCAPE_RE = re.compile(r"\\u([0-9a-fA-F]{4})")
_CUM_CHO_LENH_HOAN_TAT = unicodedata.normalize("NFC", "chờ lệnh hoàn tất").casefold()


def cho_phep_chay_nen(viec: dict | None) -> bool:
    """Cho biet phieu co header `cho_nen: co` (cho phep chay nen) hay khong."""
    if not isinstance(viec, dict):
        return False
    gia_tri = viec.get("cho_nen")
    if gia_tri in (None, "") and isinstance(viec.get("meta"), dict):
        gia_tri = viec["meta"].get("cho_nen")
    if isinstance(gia_tri, bool):
        return gia_tri
    sach = unicodedata.normalize("NFC", str(gia_tri or "").split("#", 1)[0].strip()).casefold()
    return sach in {"co", "có", "1", "true", "yes", "bat", "bật"}


def _giai_ma_unicode_don_gian(van_ban: str) -> str:
    if "\\u" not in van_ban:
        return van_ban
    return _MAU_UNICODE_ESCAPE_RE.sub(lambda m: chr(int(m.group(1), 16)), van_ban)


def _chuan_hoa_nfc_lower(van_ban: str | None) -> str:
    if not van_ban:
        return ""
    giai = _giai_ma_unicode_don_gian(str(van_ban))
    return unicodedata.normalize("NFC", giai).casefold()


def _la_json_ket_qua_thanh_cong(dong_hoac_chuoi: str) -> bool:
    sach = dong_hoac_chuoi.strip()
    if not sach.startswith("{"):
        return False
    try:
        obj = json.loads(sach)
    except (ValueError, TypeError):
        # Chi bo qua khi day la 1 JSON ket qua dang stream do dang co "status": "SUCCESS" + "response", khong phai NDJSON nhieu dong
        if "\n{" not in sach and '"response"' in sach[:700] and _MAU_STATUS_SUCCESS_RE.search(sach[:400]):
            return not _MAU_STATUS_ERROR_RE.search(sach[:400])
        return False
    if isinstance(obj, dict) and "status" in obj:
        return str(obj.get("status") or "").strip().upper() in ("SUCCESS", "OK", "DONE")
    return False


def _co_status_error_cho_lenh(van_ban: str) -> bool:
    chuan = _chuan_hoa_nfc_lower(van_ban)
    if _CUM_CHO_LENH_HOAN_TAT not in chuan:
        return False
    sach = van_ban.strip()
    if sach.startswith("{"):
        try:
            obj = json.loads(sach)
            if isinstance(obj, dict):
                if str(obj.get("status") or "").strip().upper() != "ERROR":
                    return False
                than_err = _chuan_hoa_nfc_lower(f"{obj.get('response') or ''} {obj.get('error') or ''}")
                return _CUM_CHO_LENH_HOAN_TAT in than_err
        except (ValueError, TypeError):
            pass
    if _MAU_STATUS_SUCCESS_RE.search(van_ban) and not _MAU_STATUS_ERROR_RE.search(van_ban):
        return False
    return bool(_MAU_STATUS_ERROR_RE.search(van_ban))


def phat_hien_dong_cho_tac_vu_nen(dong: str | None, la_stderr: bool = False) -> str:
    """Tra ve ten mau neu mot dong dau ra bao hieu agy cho tac vu nen / root agent idle; rong neu khong."""
    if not dong:
        return ""
    sach = str(dong).strip()
    if not sach:
        return ""
    if not la_stderr and _la_json_ket_qua_thanh_cong(sach):
        return ""
    if _co_status_error_cho_lenh(sach):
        return 'status ERROR ("chờ lệnh hoàn tất")'
    # Tranh bat nham van ban thong thuong ben trong truong `response` cua JSON ket qua
    if not la_stderr and sach.startswith("{"):
        try:
            obj = json.loads(sach)
            if isinstance(obj, dict):
                err_txt = str(obj.get("error") or obj.get("message") or "")
                if _MAU_WAITING_BG_RE.search(err_txt):
                    return "waiting up to ... background task"
                if _MAU_ROOT_IDLE_RE.search(err_txt):
                    return "root agent idle"
                return ""
        except (ValueError, TypeError):
            if '"response"' in sach[:600]:
                return ""
    if _MAU_WAITING_BG_RE.search(sach):
        return "waiting up to ... background task"
    if _MAU_ROOT_IDLE_RE.search(sach):
        return "root agent idle"
    return ""


def phat_hien_luong_cho_tac_vu_nen(van_ban: str | None, la_stderr: bool = False) -> str:
    """Quet toan bo hoac doan duoi luong ra agy (ho tro ca JSON nhieu dong va dong don)."""
    if not van_ban:
        return ""
    toan_bo = str(van_ban).strip()
    if not toan_bo:
        return ""
    if not la_stderr and _la_json_ket_qua_thanh_cong(toan_bo):
        return ""
    if _co_status_error_cho_lenh(toan_bo):
        return 'status ERROR ("chờ lệnh hoàn tất")'
    for dong in toan_bo.splitlines():
        khop = phat_hien_dong_cho_tac_vu_nen(dong, la_stderr=la_stderr)
        if khop:
            return khop
    return phat_hien_dong_cho_tac_vu_nen(toan_bo, la_stderr=la_stderr)


def ghep_de_gui_agy(de_goc: str, cho_nen: bool = False) -> str:
    """Thêm hướng dẫn CAN-LINH và câu cấm background task / thợ con vào cuối mọi đề gửi agy."""
    goc = str(de_goc or "").rstrip()
    cac_phan = [goc] if goc else []
    if CAU_NHAC_CAN_LINH not in goc:
        cac_phan.append(CAU_NHAC_CAN_LINH)
    if not cho_nen and CAU_NHAC_TIEN_CANH not in goc:
        cac_phan.append(CAU_NHAC_TIEN_CANH)
    return "\n\n".join(cac_phan)


def trich_dong_cuoi_agy(buf_out: list[bytes], buf_err: list[bytes], gioi_han: int = GIOI_HAN_DONG_NHIP) -> str:
    """Lay dong stdout/stderr cuoi cung khong rong cua agy (cat <= gioi_han ky tu)."""
    for buf in (buf_out, buf_err):
        if not buf:
            continue
        duoi_bytes = b"".join(buf[-4:])[-8192:]
        van_ban = duoi_bytes.decode("utf-8", errors="replace")
        for dong in reversed(van_ban.splitlines()):
            sach = " ".join(dong.strip().split())
            if sach:
                return sach[:gioi_han]
    return "(chưa có đầu ra)"[:gioi_han]


def _phan_tich_ket_qua_agy(returncode: int, giay_chay: float, stdout: str, stderr: str):
    nhat_ky = f"exit={returncode} giay={giay_chay:.0f}\n--- stderr ---\n{stderr[-8000:]}"
    out = stdout.strip()
    ket_qua, tv, tr = out, 0, 0
    try:
        j = json.loads(out)
        ket_qua = j.get("response") or j.get("result") or out
        u = j.get("usage") or j.get("stats") or {}
        tv = int(u.get("input_tokens") or u.get("prompt_tokens") or 0)
        tr = int(u.get("output_tokens") or u.get("completion_tokens") or 0)
        if str(j.get("status", "SUCCESS")).upper() not in ("SUCCESS", "OK", "DONE"):
            return "loi", ket_qua, nhat_ky + f"\nstatus={j.get('status')}", tv, tr
    except (ValueError, AttributeError, TypeError):
        pass
    if returncode != 0:
        return "loi", ket_qua, nhat_ky, tv, tr
    return "xong", ket_qua, nhat_ky, tv, tr


def _ghep_canh_bao_nhat_ky(nhat_ky: str, canh_bao: str) -> str:
    if not canh_bao:
        return nhat_ky
    if not nhat_ky:
        return canh_bao
    return f"{canh_bao}\n{nhat_ky}"


def _trich_token_json(stdout: str | None) -> tuple[int, int]:
    out = str(stdout or "").strip()
    if not out:
        return 0, 0
    try:
        j = json.loads(out)
        u = j.get("usage") or j.get("stats") or {}
        tv = int(u.get("input_tokens") or u.get("prompt_tokens") or 0)
        tr = int(u.get("output_tokens") or u.get("completion_tokens") or 0)
        return tv, tr
    except (ValueError, AttributeError, TypeError):
        return 0, 0


def _duoi_log_dung(stdout: str, stderr: str) -> str:
    return f"\n{stdout[-4000:]}" if stdout else (f"\n{stderr[-2000:]}" if stderr else "")


def _ghi_nhat_ky_debug_vao_viec(
    cfg: dict | None,
    viec,
    trang_thai: str,
    stdout: str = "",
    stderr: str = "",
    ly_do: str = "",
    de_da_gui: str = "",
    moc_epoch_bat_dau: float | None = None,
    la_mock: bool = False,
) -> None:
    if not isinstance(viec, dict):
        return
    if ly_do:
        viec["_ly_do_dung"] = ly_do
    cho_phep_hoi_thoai = (not la_mock) or bool(
        (cfg and cfg.get("thu_muc_agy_cli")) or os.environ.get("LINHX_AGY_CLI_DIR", "").strip()
    )
    try:
        viec["_nhat_ky_debug"] = nhat_ky_agy.tao_nhat_ky_debug_tu_phien(
            cfg=cfg,
            viec=viec,
            trang_thai=trang_thai,
            stdout=stdout,
            stderr=stderr,
            ly_do=ly_do,
            de_da_gui=de_da_gui,
            moc_epoch_bat_dau=moc_epoch_bat_dau,
            cho_phep_doc_hoi_thoai=cho_phep_hoi_thoai,
        )
    except Exception:
        pass


_MAU_TEN_LENH = re.compile(r"^[A-Za-z0-9._-]{1,80}$")
THU_MUC_LENH = GOC / "lenh"


def chay_lenh(cfg, viec):
    """Phieu `loai: lenh`: chay script da commit runner/lenh/<lenh>.ps1 (Windows) hoac .sh, khong mo agy."""
    meta = viec.get("meta") if isinstance(viec.get("meta"), dict) else {}
    ten = str(meta.get("lenh") or "").split("#", 1)[0].strip()
    if not ten or not _MAU_TEN_LENH.match(ten) or ".." in ten:
        return "loi", None, f"phiếu lenh thiếu hoặc sai tên script: '{ten}'", 0, 0
    ps1, sh = THU_MUC_LENH / f"{ten}.ps1", THU_MUC_LENH / f"{ten}.sh"
    if os.name == "nt" and ps1.is_file():
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps1)]
    elif sh.is_file():
        cmd = ["bash", str(sh)]
    elif ps1.is_file():
        cmd = ["pwsh", "-NoProfile", "-File", str(ps1)]
    else:
        return "loi", None, f"không có script runner/lenh/{ten}.ps1|.sh", 0, 0
    tran = _ep_so_duong(viec.get("tran_phut"), 10) * 60.0
    kw = {"creationflags": 0x08000000} if os.name == "nt" else {}
    t0 = _gio()
    try:
        p = _SUBPROCESS_RUN_GOC(cmd, cwd=str(cfg.get("thu_muc") or GOC), capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=tran, **kw)
    except subprocess.TimeoutExpired:
        return "dung", None, f"dừng lệnh {ten}: quá {tran/60:.0f} phút", 0, 0
    except OSError as e:
        return "loi", None, f"không chạy được {ten}: {e}", 0, 0
    ra = (p.stdout or "")[-4000:]
    nk = f"lenh={ten} exit={p.returncode} giay={_gio()-t0:.0f}\n--- stderr ---\n{(p.stderr or '')[-4000:]}"
    return ("xong" if p.returncode == 0 else "loi"), (ra or "(không in gì)"), nk, 0, 0


def chay_agy(cfg, viec):
    """Tra ve (trang_thai, ket_qua, nhat_ky, token_vao, token_ra).

    Dung agy (tra trang_thai='dung') khi:
    - Chay qua tran_phut (mac dinh 40 phut), hoac
    - Khong tien (khong stdout/stderr moi, khong thay doi tep trong thu_muc / theo_doi de quy,
      va tong CPU cua cay tien trinh agy khong tang trong 2 phut gan nhat)
      qua khong_tien_phut (mac dinh 20 phut).
    """
    if str(viec.get("loai") or "").strip().lower() == "lenh":
        return chay_lenh(cfg, viec)
    if viec.get("che_do") == "kiem":
        kq_m_kiem = chon_model_phieu(cfg, viec)
        if isinstance(viec, dict):
            viec["_model_da_dung"] = kq_m_kiem["model_that"] if kq_m_kiem["hop_le"] else MODEL_MAC_DINH_NHAN
            viec["_canh_bao_model"] = kq_m_kiem.get("canh_bao", "")
        return "xong", f"Thợ {cfg['tho']} trên {platform.node()} nhận được: {viec['de']}", "che_do=kiem, khong goi agy", 0, 0

    tran_cfg = _ep_so_duong(
        cfg.get("tran_phut"),
        _ep_so_duong(os.environ.get("LINHX_TRAN_PHUT"), PHUT_TOI_DA_MAC_DINH),
    )
    tran_viec = _ep_so_duong(viec.get("tran_phut"), tran_cfg)
    tran_phut = min(tran_viec, tran_cfg)
    tran_giay = tran_phut * 60.0

    kt_cfg = _ep_so_duong(
        cfg.get("khong_tien_phut"),
        _ep_so_duong(os.environ.get("LINHX_KHONG_TIEN_PHUT"), PHUT_KHONG_TIEN_MAC_DINH),
    )
    meta_viec = viec.get("meta") if isinstance(viec.get("meta"), dict) else {}
    kt_viec = _ep_so_duong(viec.get("khong_tien_phut") or meta_viec.get("khong_tien_phut"), kt_cfg)
    # phieu duoc nang nguong (viec lau: clone repo lon, test dai) nhung khong qua tran phut
    khong_tien_phut = min(kt_viec, tran_phut) if (viec.get("khong_tien_phut") or meta_viec.get("khong_tien_phut")) else min(max(kt_cfg, PHUT_KHONG_TIEN_MAC_DINH), tran_phut)  # tho.env cu ghi 10: san 20
    khong_tien_giay = khong_tien_phut * 60.0

    thong_tin_model = chon_model_phieu(cfg, viec)
    if isinstance(viec, dict):
        viec["_model_da_dung"] = thong_tin_model["model_that"]
        viec["_canh_bao_model"] = thong_tin_model["canh_bao"]
    if not thong_tin_model["hop_le"]:
        return "loi", None, thong_tin_model["ly_do_loi"], 0, 0

    ten_model = thong_tin_model["model"]
    canh_bao_model = thong_tin_model["canh_bao"]

    thu_muc = Path(cfg["thu_muc"])
    gioi_han = cfg.get("gioi_han_thu_muc")
    if gioi_han is None and os.environ.get("LINHX_GIOI_HAN_THU_MUC", "").strip():
        gioi_han = Path(os.environ["LINHX_GIOI_HAN_THU_MUC"].strip())
    ok_tm, ly_do_tm = kiem_tra_thu_muc_lam_viec(thu_muc, gioi_han)
    if not ok_tm:
        return "loi", None, ly_do_tm, 0, 0
    thu_muc.mkdir(parents=True, exist_ok=True)
    cho_nen = cho_phep_chay_nen(viec)
    de = ghep_de_gui_agy(viec["de"], cho_nen=cho_nen)
    if len(de) > DE_DAI:
        # Windows gioi han dong lenh 32.767 ky tu: de dai thi ghi ra file, -p chi tro toi file
        f = thu_muc / f"de-{viec['viec']}.md"
        f.write_text(de, encoding="utf-8")
        duoi_nhac = "" if cho_nen else f"\n\n{CAU_NHAC_TIEN_CANH}"
        de = (
            f"Đọc toàn bộ file {f.name} trong thư mục hiện tại (chỉ đọc, không chạy lệnh shell) "
            f"và làm đúng theo đề trong đó. Trả lời đúng khuôn đề yêu cầu.{duoi_nhac}"
        )
    ds_agy_args = _tach_agy_args(cfg.get("agy_args", "--output-format json"))
    if thong_tin_model["xoa_co_model"]:
        ds_agy_args = _xoa_co_model_agy_args(ds_agy_args)
    elif ten_model:
        ds_agy_args = _thay_co_model_agy_args(ds_agy_args, ten_model)
    if not cho_nen and AGY_CO_TAT_NEN:
        for co in AGY_CO_TAT_NEN:
            if co not in ds_agy_args:
                ds_agy_args.append(co)
    cmd = [cfg["agy"], "-p", de] + ds_agy_args
    tep_log_raw = cfg.get("_tep_log_phieu")
    moc_epoch_bat_dau = time.time()

    # Tuong thich nguoc khi test monkeypatch truc tiep subprocess.run
    if subprocess.run is not _SUBPROCESS_RUN_GOC:
        kw_run = {"creationflags": 0x08000000} if os.name == "nt" else {}
        t0_run = _gio()
        try:
            p = subprocess.run(cmd, cwd=str(thu_muc), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=tran_giay, **kw_run)
        except subprocess.TimeoutExpired as e:
            if tep_log_raw:
                _ghi_agy_raw(tep_log_raw, viec.get("viec"), -1, _gio() - t0_run, e.stdout or "", e.stderr or "", "qua_gio")
            _ghi_nhat_ky_debug_vao_viec(
                cfg, viec, "dung", stdout=e.stdout or "", stderr=e.stderr or "",
                ly_do="qua_gio", de_da_gui=de, moc_epoch_bat_dau=moc_epoch_bat_dau, la_mock=True,
            )
            nk_q = _ghep_canh_bao_nhat_ky(
                f"dừng agy: quá trần {_dinh_dang_phut(tran_phut)} phút\n{(e.stdout or '')[-4000:]}",
                canh_bao_model,
            )
            return "dung", None, nk_q, 0, 0
        except FileNotFoundError:
            return "loi", None, f"không thấy agy ở '{cfg['agy']}' (đặt AGY_CMD)", 0, 0
        except OSError as e:
            if getattr(e, "winerror", None) == 206:
                return "loi", None, f"dòng lệnh quá dài ({len(de)} ký tự)", 0, 0
            return "loi", None, f"không chạy được agy: {e}", 0, 0
        giay_chay = _gio() - t0_run
        if cho_nen:
            mau_cho_run = (
                ('status ERROR ("chờ lệnh hoàn tất")' if _co_status_error_cho_lenh(p.stderr or "") else "")
                or ('status ERROR ("chờ lệnh hoàn tất")' if _co_status_error_cho_lenh(p.stdout or "") else "")
            )
        else:
            mau_cho_run = (
                phat_hien_luong_cho_tac_vu_nen(p.stderr, la_stderr=True)
                or phat_hien_luong_cho_tac_vu_nen(p.stdout, la_stderr=False)
            )
        if mau_cho_run:
            if tep_log_raw:
                _ghi_agy_raw(tep_log_raw, viec.get("viec"), p.returncode, giay_chay, p.stdout, p.stderr, LY_DO_CHO_TAC_VU_NEN)
            tv_nen, tr_nen = _trich_token_json(p.stdout)
            _ghi_nhat_ky_debug_vao_viec(
                cfg, viec, "dung", stdout=p.stdout or "", stderr=p.stderr or "",
                ly_do=LY_DO_CHO_TAC_VU_NEN, de_da_gui=de, moc_epoch_bat_dau=moc_epoch_bat_dau, la_mock=True,
            )
            nk_nen = _ghep_canh_bao_nhat_ky(
                f"dừng agy ({LY_DO_CHO_TAC_VU_NEN}): {mau_cho_run}{_duoi_log_dung(p.stdout or '', p.stderr or '')}",
                canh_bao_model,
            )
            return "dung", None, nk_nen, tv_nen, tr_nen
        if tep_log_raw:
            _ghi_agy_raw(tep_log_raw, viec.get("viec"), p.returncode, giay_chay, p.stdout, p.stderr)
        tt_r, kq_r, nk_r, tv_r, tr_r = _phan_tich_ket_qua_agy(p.returncode, giay_chay, p.stdout, p.stderr)
        _ghi_nhat_ky_debug_vao_viec(
            cfg, viec, tt_r, stdout=p.stdout or "", stderr=p.stderr or "",
            de_da_gui=de, moc_epoch_bat_dau=moc_epoch_bat_dau, la_mock=True,
        )
        return tt_r, kq_r, _ghep_canh_bao_nhat_ky(nk_r, canh_bao_model), tv_r, tr_r

    kw = {}
    if os.name == "nt":
        kw["creationflags"] = 0x08000000  # CREATE_NO_WINDOW: chay an, khong bat console
    else:
        kw["start_new_session"] = True

    la_mock_popen = _tao_tien_trinh_agy is not None
    ham_popen = _tao_tien_trinh_agy if la_mock_popen else subprocess.Popen
    t0 = _gio()
    try:
        proc = ham_popen(
            cmd,
            cwd=str(thu_muc),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
            **kw,
        )
    except FileNotFoundError:
        return "loi", None, f"không thấy agy ở '{cfg['agy']}' (đặt AGY_CMD)", 0, 0
    except OSError as e:
        if getattr(e, "winerror", None) == 206:
            return "loi", None, f"dòng lệnh quá dài ({len(de)} ký tự)", 0, 0
        return "loi", None, f"không chạy được agy: {e}", 0, 0

    buf_out: list[bytes] = []
    buf_err: list[bytes] = []
    dem_byte = [0, 0]
    su_kien_cho_nen = threading.Event()
    khoa_cho_nen = threading.Lock()
    mau_cho_nen_tim_thay = ""
    bo_giai_ma = [
        codecs.getincrementaldecoder("utf-8")(errors="replace"),
        codecs.getincrementaldecoder("utf-8")(errors="replace"),
    ]
    duoi_van_ban = ["", ""]

    def _ghi_nhan_cho_nen(mau: str) -> None:
        nonlocal mau_cho_nen_tim_thay
        if not mau:
            return
        with khoa_cho_nen:
            if not mau_cho_nen_tim_thay:
                mau_cho_nen_tim_thay = mau
        su_kien_cho_nen.set()

    def _quet_chu_cho_nen(doan: str, idx: int) -> None:
        if not doan:
            return
        la_err = idx == 1
        duoi_moi = (duoi_van_ban[idx] + doan)[-16384:]
        duoi_van_ban[idx] = duoi_moi
        if cho_nen:
            if _co_status_error_cho_lenh(duoi_moi):
                _ghi_nhan_cho_nen('status ERROR ("chờ lệnh hoàn tất")')
            return
        for dong in duoi_moi[-2048:].splitlines():
            khop = phat_hien_dong_cho_tac_vu_nen(dong, la_stderr=la_err)
            if khop:
                _ghi_nhan_cho_nen(khop)
                return
        khop_duoi = phat_hien_luong_cho_tac_vu_nen(duoi_moi, la_stderr=la_err)
        if khop_duoi:
            _ghi_nhan_cho_nen(khop_duoi)

    def _doc_pipe(pipe, ds: list[bytes], idx: int):
        if pipe is None:
            return
        try:
            while True:
                khuc = pipe.read(4096)
                if not khuc:
                    break
                if isinstance(khuc, str):
                    doan = khuc
                    khuc_bytes = khuc.encode("utf-8", errors="replace")
                else:
                    khuc_bytes = khuc
                    doan = bo_giai_ma[idx].decode(khuc_bytes, final=False)
                ds.append(khuc_bytes)
                dem_byte[idx] += len(khuc_bytes)
                _quet_chu_cho_nen(doan, idx)
            duoi_cuoi = bo_giai_ma[idx].decode(b"", final=True)
            if duoi_cuoi:
                _quet_chu_cho_nen(duoi_cuoi, idx)
        except Exception:
            pass
        finally:
            try:
                pipe.close()
            except Exception:
                pass

    luong_out = threading.Thread(target=_doc_pipe, args=(proc.stdout, buf_out, 0), daemon=True)
    luong_err = threading.Thread(target=_doc_pipe, args=(proc.stderr, buf_err, 1), daemon=True)
    luong_out.start()
    luong_err.start()

    bo_nho_cpu_cay: dict = {}

    def _lay_cpu_cay() -> float:
        pid_p = getattr(proc, "pid", None)
        if _doc_cpu_cay_agy is not None:
            return float(_doc_cpu_cay_agy(pid_p) or 0.0)
        if isinstance(proc, subprocess.Popen) and pid_p:
            return doc_cpu_cay_tien_trinh(int(pid_p), bo_nho_cay=bo_nho_cpu_cay)
        return 0.0

    theo_doi = _thu_muc_theo_doi(meta_viec, viec=viec)
    dau_cu = _dau_nhip_tien_do(thu_muc, dem_byte, tep_log_raw, theo_doi)
    cpu_ban_dau = _lay_cpu_cay()
    lich_su_cpu: list[tuple[float, float]] = [(t0, cpu_ban_dau)]
    cpu_moc_tien = cpu_ban_dau
    moc_tien_cuoi = t0
    ham_ghi_nhip = cfg.get("_ghi_nhip_fn")
    nhip_phut = _ep_so_duong(
        cfg.get("nhip_phut"),
        _ep_so_duong(os.environ.get("LINHX_NHIP_PHUT"), NHIP_PHUT_MAC_DINH),
    )
    nhip_giay = nhip_phut * 60.0
    moc_nhip_cuoi = t0
    ly_do_dung = None
    buoc_nghi = min(1.0, max(0.01, min(tran_giay, khong_tien_giay) / 20.0))

    try:
        while True:
            if su_kien_cho_nen.is_set():
                ly_do_dung = LY_DO_CHO_TAC_VU_NEN
                dung_tien_trinh_agy(proc)
                break
            if proc.poll() is not None:
                break
            bay_gio = _gio()
            theo_doi = _thu_muc_theo_doi(meta_viec, viec=viec)
            dau_moi = _dau_nhip_tien_do(thu_muc, dem_byte, tep_log_raw, theo_doi)
            co_tien_tep = dau_moi != dau_cu
            if co_tien_tep:
                dau_cu = dau_moi
            cpu_hien_tai = _lay_cpu_cay()
            co_tien_cpu, cpu_moc_tien = cpu_tang_trong_cua_so(
                lich_su_cpu,
                bay_gio=bay_gio,
                cpu_moi=cpu_hien_tai,
                cpu_moc_cu=cpu_moc_tien,
                cua_so_giay=CUA_SO_CPU_GIAY,
            )
            if co_tien_tep or co_tien_cpu:
                moc_tien_cuoi = bay_gio
            if ham_ghi_nhip is not None and (bay_gio - moc_nhip_cuoi) >= nhip_giay:
                moc_nhip_cuoi = bay_gio
                try:
                    phut_da_chay = (bay_gio - t0) / 60.0
                    dong_cuoi = trich_dong_cuoi_agy(buf_out, buf_err, GIOI_HAN_DONG_NHIP)
                    ham_ghi_nhip(phut_da_chay, dong_cuoi)
                except Exception:
                    pass
            if (bay_gio - t0) >= tran_giay:
                ly_do_dung = "qua_gio"
                dung_tien_trinh_agy(proc)
                break
            if (bay_gio - moc_tien_cuoi) >= khong_tien_giay:
                ly_do_dung = "khong_tien"
                dung_tien_trinh_agy(proc)
                break
            if _ngu is not None:
                _tam_nghi(buoc_nghi)
            else:
                if su_kien_cho_nen.wait(buoc_nghi):
                    continue
    finally:
        if proc.poll() is None:
            dung_tien_trinh_agy(proc)
        luong_out.join(timeout=2.0)
        luong_err.join(timeout=2.0)

    giay_chay = _gio() - t0
    stdout = b"".join(buf_out).decode("utf-8", errors="replace")
    stderr = b"".join(buf_err).decode("utf-8", errors="replace")

    if cho_nen:
        mau_cho_cuoi = (
            mau_cho_nen_tim_thay
            or ('status ERROR ("chờ lệnh hoàn tất")' if _co_status_error_cho_lenh(stderr) else "")
            or ('status ERROR ("chờ lệnh hoàn tất")' if _co_status_error_cho_lenh(stdout) else "")
        )
    else:
        mau_cho_cuoi = (
            mau_cho_nen_tim_thay
            or phat_hien_luong_cho_tac_vu_nen(stderr, la_stderr=True)
            or phat_hien_luong_cho_tac_vu_nen(stdout, la_stderr=False)
        )
    if ly_do_dung == LY_DO_CHO_TAC_VU_NEN or (ly_do_dung is None and mau_cho_cuoi):
        if tep_log_raw:
            _ghi_agy_raw(tep_log_raw, viec.get("viec"), proc.returncode if proc.returncode is not None else -1, giay_chay, stdout, stderr, LY_DO_CHO_TAC_VU_NEN)
        tv_nen, tr_nen = _trich_token_json(stdout)
        _ghi_nhat_ky_debug_vao_viec(
            cfg, viec, "dung", stdout=stdout, stderr=stderr,
            ly_do=LY_DO_CHO_TAC_VU_NEN, de_da_gui=de, moc_epoch_bat_dau=moc_epoch_bat_dau, la_mock=la_mock_popen,
        )
        nk_cho_nen = _ghep_canh_bao_nhat_ky(
            f"dừng agy ({LY_DO_CHO_TAC_VU_NEN}): {mau_cho_cuoi}{_duoi_log_dung(stdout, stderr)}",
            canh_bao_model,
        )
        return "dung", None, nk_cho_nen, tv_nen, tr_nen

    if ly_do_dung == "qua_gio":
        if tep_log_raw:
            _ghi_agy_raw(tep_log_raw, viec.get("viec"), -1, giay_chay, stdout, stderr, "qua_gio")
        _ghi_nhat_ky_debug_vao_viec(
            cfg, viec, "dung", stdout=stdout, stderr=stderr,
            ly_do="qua_gio", de_da_gui=de, moc_epoch_bat_dau=moc_epoch_bat_dau, la_mock=la_mock_popen,
        )
        nk_qua_gio = _ghep_canh_bao_nhat_ky(
            f"dừng agy: quá trần {_dinh_dang_phut(tran_phut)} phút{_duoi_log_dung(stdout, stderr)}",
            canh_bao_model,
        )
        return "dung", None, nk_qua_gio, 0, 0

    if ly_do_dung == "khong_tien":
        if tep_log_raw:
            _ghi_agy_raw(tep_log_raw, viec.get("viec"), -1, giay_chay, stdout, stderr, "khong_tien")
        _ghi_nhat_ky_debug_vao_viec(
            cfg, viec, "dung", stdout=stdout, stderr=stderr,
            ly_do="khong_tien", de_da_gui=de, moc_epoch_bat_dau=moc_epoch_bat_dau, la_mock=la_mock_popen,
        )
        nk_khong_tien = _ghep_canh_bao_nhat_ky(
            f"dừng agy: quá {_dinh_dang_phut(khong_tien_phut)} phút không tiến{_duoi_log_dung(stdout, stderr)}",
            canh_bao_model,
        )
        return "dung", None, nk_khong_tien, 0, 0

    returncode = proc.returncode if proc.returncode is not None else -1
    if tep_log_raw:
        _ghi_agy_raw(tep_log_raw, viec.get("viec"), returncode, giay_chay, stdout, stderr)
    tt_cuoi, kq_cuoi, nk_cuoi, tv_cuoi, tr_cuoi = _phan_tich_ket_qua_agy(returncode, giay_chay, stdout, stderr)
    _ghi_nhat_ky_debug_vao_viec(
        cfg, viec, tt_cuoi, stdout=stdout, stderr=stderr,
        de_da_gui=de, moc_epoch_bat_dau=moc_epoch_bat_dau, la_mock=la_mock_popen,
    )
    return tt_cuoi, kq_cuoi, _ghep_canh_bao_nhat_ky(nk_cuoi, canh_bao_model), tv_cuoi, tr_cuoi


def vong(cfg, mot_lan=False, mot_viec=False):
    if str(cfg.get("nguon") or "engine").strip().lower() == "github":
        try:
            from runner import hang_doi_git
        except ImportError:
            import hang_doi_git
        return hang_doi_git.vong_git(cfg, mot_lan=mot_lan, mot_viec=mot_viec)
    log(f"linhx-runner {PHIEN_BAN} tho={cfg['tho']} url={cfg['url']}")
    while True:
        try:
            ok_ram, ram_gb = du_ram_nhan_viec(cfg)
            if not ok_ram:
                log(f"RAM trong {ram_gb:.2f} GB < {cfg.get('nguong_ram_gb', NGUONG_RAM_TRONG_GB)} GB, tam ngung nhan viec")
            else:
                viec = goi(cfg, "nhan_viec", ma=cfg["tho"], phien_ban=PHIEN_BAN, may=platform.node())
                if viec:
                    log("nhan", viec["viec"], viec["workflow"])
                    tt, kq, nk, tv, tr = chay_agy(cfg, viec)
                    tt_bao = "loi" if tt == "dung" else tt
                    goi(cfg, "bao_ket_qua", ma=cfg["tho"], viec=viec["viec"], trang_thai=tt_bao,
                        ket_qua=kq, nhat_ky=nk, token_vao=tv, token_ra=tr)
                    log("xong", viec["viec"], tt)
                    if mot_viec:
                        return
                    continue  # co viec thi hoi tiep ngay
        except urllib.error.HTTPError as e:
            log("loi HTTP", e.code, e.read()[:300])
        except Exception:
            log("loi", traceback.format_exc()[-800:])
        if mot_lan:
            return
        time.sleep(cfg["nghi"])


@contextmanager
def khoa_mot_tien_trinh(tep_khoa: Path):
    """Khoa cap he dieu hanh khong chan (non-blocking) de 1 may khong chay chong nhieu runner."""
    tep_khoa = Path(tep_khoa)
    tep_khoa.parent.mkdir(parents=True, exist_ok=True)
    fh = open(tep_khoa, "a+b")
    da_khoa = False
    try:
        fh.seek(0)
        if fh.read(1) == b"":
            fh.write(b"0")
            fh.flush()
        fh.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        da_khoa = True
    except OSError:
        fh.close()
        yield False
        return

    try:
        yield True
    finally:
        if da_khoa:
            try:
                fh.seek(0)
                if os.name == "nt":
                    import msvcrt

                    msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass
        fh.close()


def _duong_dan_khoa_runner(cfg: dict) -> Path:
    tho_an_toan = "".join(c if (c.isalnum() or c in "-_") else "_" for c in str(cfg.get("tho") or "tho"))
    if str(cfg.get("nguon") or "engine").strip().lower() == "github":
        repo = Path(cfg.get("repo_hang_doi") or GOC.parent).resolve()
        return repo.parent / f".{repo.name}-{tho_an_toan}-runner.lock"
    return GOC / "viec" / f"tho-{tho_an_toan}.lock"


def tu_cap_nhat(goc_repo: Path | None = None, chay=None) -> str:
    """Tu keo ban moi cua runner (git pull --ff-only) truoc moi luot, de Linh khong phai git pull tay.
    Tat bang LINHX_TU_CAP_NHAT=0. Loi mang/xung dot thi bo qua, chay ban dang co."""
    if os.environ.get("LINHX_TU_CAP_NHAT", "1").strip() == "0":
        return "tat"
    goc_repo = goc_repo or GOC.parent
    if not (goc_repo / ".git").exists():
        return "khong-phai-repo"
    chay = chay or subprocess.run
    try:
        r = chay(["git", "-C", str(goc_repo), "pull", "--ff-only", "-q"], capture_output=True, text=True, timeout=60)
        return "ok" if r.returncode == 0 else "loi"
    except Exception:
        return "loi"


def co_ban_runner_moi(goc_repo: Path | None = None, chay=None) -> bool:
    """Vong dai (khong --mot-lan): keo ban moi; True neu HEAD doi (code dang nap trong bo nho da cu).
    Tat bang LINHX_TU_CAP_NHAT=0."""
    if os.environ.get("LINHX_TU_CAP_NHAT", "1").strip() == "0":
        return False
    goc_repo = goc_repo or GOC.parent
    if not (goc_repo / ".git").exists():
        return False
    chay = chay or _SUBPROCESS_RUN_GOC
    try:
        truoc = chay(["git", "-C", str(goc_repo), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=30).stdout.strip()
        chay(["git", "-C", str(goc_repo), "pull", "--ff-only", "-q"], capture_output=True, text=True, timeout=60)
        sau = chay(["git", "-C", str(goc_repo), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=30).stdout.strip()
        return bool(truoc and sau and truoc != sau)
    except Exception:
        return False


def khoi_dong_lai_runner(argv=None, popen=None):
    """Mo tien trinh runner moi (an, tach roi) voi cung tham so, sau khi tien trinh cu da nha khoa."""
    argv = list(sys.argv if argv is None else argv)
    popen = popen or _POPEN_GOC
    kw = {"creationflags": 0x00000008 | 0x00000200 | 0x08000000} if os.name == "nt" else {"start_new_session": True}
    log("cap-nhat", "khoi dong lai runner voi ban moi")
    try:
        popen([sys.executable] + argv, cwd=str(GOC), stdin=subprocess.DEVNULL,
              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True, **kw)
        return True
    except OSError as e:
        log("loi", f"khong khoi dong lai duoc: {e}")
        return False

def chay_cli(argv=None, tep_env=None) -> int:
    ds_arg = list(sys.argv[1:] if argv is None else argv)
    mot_viec = "--mot-viec" in ds_arg
    mot_lan = "--mot-lan" in ds_arg or mot_viec
    tep_log_cli = None
    tep_khoa_cli = None
    i = 0
    while i < len(ds_arg):
        if ds_arg[i] == "--log" and i + 1 < len(ds_arg):
            tep_log_cli = Path(ds_arg[i + 1])
            i += 2
            continue
        if ds_arg[i] == "--tep-khoa" and i + 1 < len(ds_arg):
            tep_khoa_cli = Path(ds_arg[i + 1])
            i += 2
            continue
        i += 1

    cfg = doc_env(tep_env)
    tep_khoa = tep_khoa_cli or _duong_dan_khoa_runner(cfg)
    with khoa_mot_tien_trinh(tep_khoa) as co_khoa:
        if not co_khoa:
            return 0
        if mot_lan and argv is None:
            tu_cap_nhat()
        kq_vong = None
        if tep_log_cli is None:
            kq_vong = vong(cfg, mot_lan=mot_lan, mot_viec=mot_viec)
        else:
            tep_log_cli.parent.mkdir(parents=True, exist_ok=True)
            out_cu, err_cu = sys.stdout, sys.stderr
            with tep_log_cli.open("a", encoding="utf-8", buffering=1) as fh_log:
                try:
                    sys.stdout = fh_log
                    sys.stderr = fh_log
                    kq_vong = vong(cfg, mot_lan=mot_lan, mot_viec=mot_viec)
                finally:
                    sys.stdout = out_cu
                    sys.stderr = err_cu
    # da ra khoi khoa: tien trinh moi lay duoc khoa
    if kq_vong == "khoi_dong_lai" and argv is None:
        khoi_dong_lai_runner()
    return 0


if __name__ == "__main__":
    # --mot-lan: het viec thi thoat; --mot-viec: lam toi da 1 viec roi thoat; --log <tep>: ghi log chia se
    raise SystemExit(chay_cli())
