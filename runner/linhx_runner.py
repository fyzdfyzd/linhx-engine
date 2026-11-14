"""linhx-runner: tho nhan viec cua LINHX ENGINE.

Chay o bat cu dau (may cty Windows, MSI, container tren cloud). Chi KEO viec qua HTTPS,
khong mo cong. Server chi gui DE (chu), khong bao gio gui lenh shell.

Cau hinh bang bien moi truong hoac file tho.env canh script:
  LINHX_NGUON   engine (mac dinh) hoac github (nhanh hang-doi)
  LINHX_URL     vd https://engine.linhx.vn
  LINHX_TOKEN   key:secret (bench execute linhx_worker.setup.tao_tho)
  LINHX_THO     ma tho, vd may-cty / may-1
  AGY_CMD       duong dan agy (mac dinh: agy)
  AGY_ARGS      them co cho agy (mac dinh: --output-format json)
  LINHX_THU_MUC thu muc lam viec cua agy (mac dinh: ./viec)
  LINHX_NGHI    giay giua 2 lan hoi (mac dinh 15)
Chi stdlib, Python >= 3.9.
"""
import json
import os
import platform
import shlex
import subprocess
import sys
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PHIEN_BAN = "0.1.1"
DE_DAI = 6000  # ky tu; dai hon thi dua de qua file
GOC = Path(__file__).resolve().parent


def doc_env(tep_env=None):
    f = Path(tep_env) if tep_env else (GOC / "tho.env")
    if f.exists():
        for dong in f.read_text(encoding="utf-8").splitlines():
            dong = dong.strip()
            if dong and not dong.startswith("#") and "=" in dong:
                k, v = dong.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    cfg = {
        "nguon": os.environ.get("LINHX_NGUON", "engine").strip().lower(),
        "url": os.environ.get("LINHX_URL", "http://localhost:8080").rstrip("/"),
        "token": os.environ.get("LINHX_TOKEN", ""),
        "tho": os.environ.get("LINHX_THO", platform.node().lower()),
        "agy": os.environ.get("AGY_CMD", "agy"),
        "agy_args": os.environ.get("AGY_ARGS", "--output-format json"),
        "thu_muc": Path(os.environ.get("LINHX_THU_MUC", str(GOC / "viec"))),
        "nghi": float(os.environ.get("LINHX_NGHI", "15")),
        "host": os.environ.get("LINHX_HOST", ""),
        "repo_hang_doi": Path(os.environ.get("LINHX_REPO_HANG_DOI", str(GOC.parent))),
        "nhanh_hang_doi": os.environ.get("LINHX_NHANH_HANG_DOI", "hang-doi"),
        "remote_hang_doi": os.environ.get("LINHX_REMOTE_HANG_DOI", "origin"),
        "wt_hang_doi": os.environ.get("LINHX_WT_HANG_DOI", ""),
        "thu_muc_drive": Path(os.environ["LINHX_DRIVE"]) if os.environ.get("LINHX_DRIVE", "").strip() else None,
        "thu_muc_log": Path(os.environ["LINHX_LOG_DIR"]) if os.environ.get("LINHX_LOG_DIR", "").strip() else None,
    }
    cfg["thu_muc"].mkdir(parents=True, exist_ok=True)
    return cfg


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


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


def chay_agy(cfg, viec):
    """Tra ve (trang_thai, ket_qua, nhat_ky, token_vao, token_ra)."""
    if viec["che_do"] == "kiem":
        return "xong", f"Thợ {cfg['tho']} trên {platform.node()} nhận được: {viec['de']}", "che_do=kiem, khong goi agy", 0, 0
    tran = int(viec.get("tran_phut") or 40) * 60
    de = viec["de"]
    if len(de) > DE_DAI:
        # Windows gioi han dong lenh 32.767 ky tu: de dai thi ghi ra file, -p chi tro toi file
        f = cfg["thu_muc"] / f"de-{viec['viec']}.md"
        f.write_text(de, encoding="utf-8")
        de = (f"Đọc toàn bộ file {f.name} trong thư mục hiện tại (chỉ đọc, không chạy lệnh shell) "
              f"và làm đúng theo đề trong đó. Trả lời đúng khuôn đề yêu cầu.")
    cmd = [cfg["agy"], "-p", de] + shlex.split(cfg["agy_args"], posix=os.name != "nt")
    kw = {}
    if os.name == "nt":
        kw["creationflags"] = 0x08000000  # CREATE_NO_WINDOW: chay an, khong bat console
    t0 = time.time()
    tep_log_raw = cfg.get("_tep_log_phieu")
    try:
        p = subprocess.run(cmd, cwd=str(cfg["thu_muc"]), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=tran, **kw)
    except subprocess.TimeoutExpired as e:
        if tep_log_raw:
            _ghi_agy_raw(tep_log_raw, viec.get("viec"), -1, time.time() - t0, e.stdout or "", e.stderr or "", "timeout")
        return "loi", None, f"quá trần {tran // 60} phút\n{(e.stdout or '')[-4000:]}", 0, 0
    except FileNotFoundError:
        return "loi", None, f"không thấy agy ở '{cfg['agy']}' (đặt AGY_CMD)", 0, 0
    except OSError as e:
        if getattr(e, "winerror", None) == 206:
            return "loi", None, f"dòng lệnh quá dài ({len(de)} ký tự)", 0, 0
        return "loi", None, f"không chạy được agy: {e}", 0, 0
    giay_chay = time.time() - t0
    if tep_log_raw:
        _ghi_agy_raw(tep_log_raw, viec.get("viec"), p.returncode, giay_chay, p.stdout, p.stderr)
    nhat_ky = f"exit={p.returncode} giay={giay_chay:.0f}\n--- stderr ---\n{p.stderr[-8000:]}"
    out = p.stdout.strip()
    ket_qua, tv, tr = out, 0, 0
    try:
        j = json.loads(out)
        ket_qua = j.get("response") or j.get("result") or out
        u = j.get("usage") or j.get("stats") or {}
        tv = int(u.get("input_tokens") or u.get("prompt_tokens") or 0)
        tr = int(u.get("output_tokens") or u.get("completion_tokens") or 0)
        if str(j.get("status", "SUCCESS")).upper() not in ("SUCCESS", "OK", "DONE"):
            return "loi", ket_qua, nhat_ky + f"\nstatus={j.get('status')}", tv, tr
    except (ValueError, AttributeError):
        pass
    if p.returncode != 0:
        return "loi", ket_qua, nhat_ky, tv, tr
    return "xong", ket_qua, nhat_ky, tv, tr


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
            viec = goi(cfg, "nhan_viec", ma=cfg["tho"], phien_ban=PHIEN_BAN, may=platform.node())
            if viec:
                log("nhan", viec["viec"], viec["workflow"])
                tt, kq, nk, tv, tr = chay_agy(cfg, viec)
                goi(cfg, "bao_ket_qua", ma=cfg["tho"], viec=viec["viec"], trang_thai=tt,
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


if __name__ == "__main__":
    # --mot-lan: het viec thi thoat; --mot-viec: lam toi da 1 viec roi thoat
    vong(doc_env(), mot_lan="--mot-lan" in sys.argv or "--mot-viec" in sys.argv, mot_viec="--mot-viec" in sys.argv)
