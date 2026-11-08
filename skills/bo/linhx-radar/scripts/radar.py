#!/usr/bin/env python3
"""Radar LINHX hợp nhất: một lệnh chạy cả cộng đồng (congdong.py), sự kiện + giải thưởng (eventscan.py),
cuộc thi (LAB022) và quỹ tài trợ (LAB013), một CSDL data/radar.db, một bảng xlsx, một bản tin.

Đứng trong thư mục radar (D:\\LINHX\\LAB\\LAB035-RADAR-CONG-DONG) hoặc đặt RADAR_HOME:
    python radar.py all [--no-fetch]     # chạy hết, ra output/BAN-TIN-MOI-NHAT.md + output/RADAR-LINHX.xlsx
    python radar.py ban-tin              # chỉ gom lại bản tin từ kết quả đã có
    python radar.py cong-dong <lệnh...>  # chuyển lệnh cho congdong.py (seed, mark, ...)
    python radar.py su-kien <lệnh...>    # chuyển lệnh cho eventscan.py (mark, absorb, rate, ...)
Cấu hình mô-đun: config/radar.json.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOME = Path(os.environ.get("RADAR_HOME", Path.cwd())).resolve()
TODAY = dt.date.today()


def conf() -> dict:
    try:
        return json.loads((HOME / "config" / "radar.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"cong_dong": {"bat": True}, "su_kien": {"bat": True, "home": "su-kien"}}


def p(x: str) -> Path:
    q = Path(str(x).replace("\\", "/"))
    return q if q.is_absolute() or re.match(r"^[A-Za-z]:", str(x)) else (HOME / q).resolve()


def run(script: Path, args: list[str], home: Path, ten: str) -> bool:
    env = dict(os.environ, RADAR_HOME=str(home), PYTHONIOENCODING="utf-8")
    print(f"\n=== {ten}: {' '.join(args)}", flush=True)
    r = subprocess.run([sys.executable, str(script), *args], cwd=home, env=env)
    if r.returncode:
        print(f"LỖI {ten}: thoát mã {r.returncode}")
    return r.returncode == 0


def cd(args):  # congdong.py
    return run(HERE / "congdong.py", args, HOME, "cộng đồng")


def sk(args):  # eventscan.py
    return run(HERE / "eventscan.py", args, p(conf().get("su_kien", {}).get("home", "su-kien")), "sự kiện")


def cmd_all(no_fetch: bool):
    c = conf()
    nf = ["--no-fetch"] if no_fetch else []
    if c.get("cong_dong", {}).get("bat", True):
        cd(["init"])
        if not no_fetch:
            cd(["scan"])
    if c.get("su_kien", {}).get("bat", True):
        ct = c.get("cuoc_thi", {})
        if ct.get("bat") and p(ct["home"]).exists() and ct.get("nhap_vao_su_kien"):
            f = p(ct["home"]) / Path(ct["nhap_vao_su_kien"].replace("\\", "/"))
            if f.exists():
                sk(["import-lab022", str(f)])
        sk(["all", *nf])
        sk(["export-lab035"])  # diễn giả → KOL, tài trợ/đoạt giải → DN, cùng khoá tên
        x = p(c.get("su_kien", {}).get("home", "su-kien")) / "data" / "xuat-lab035.json"
        if x.exists():
            cd(["seed", str(x)])
    if c.get("cong_dong", {}).get("bat", True):
        cd(["match"]); cd(["score"]); cd(["export"]); cd(["digest"])
        sk(["score"])  # chấm lại sự kiện sau khi điểm DN/KOL đã cập nhật
    for key in ("cuoc_thi", "quy_tai_tro", "kol_ai"):
        m = c.get(key, {})
        if m.get("bat") and p(m["script"]).exists():
            run(p(m["script"]), m.get("lenh", ["all"]) + (nf if key == "cuoc_thi" else []), p(m["home"]), key)
        elif m.get("bat"):
            print(f"Bỏ qua {key}: không thấy {m.get('script')}")
    ban_tin()


def latest(path: Path) -> str:
    """Đọc file bản tin; nếu là thư mục thì lấy DIGEST mới nhất."""
    if path.is_dir():
        fs = sorted(path.glob("DIGEST-*.md")) or sorted(path.glob("*.md"))
        path = fs[-1] if fs else path
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, IsADirectoryError):
        return ""


def demote(md: str, bo_tieu_de=True) -> str:
    lines = md.splitlines()
    if bo_tieu_de and lines and lines[0].startswith("# "):
        lines = lines[1:]
    return "\n".join(("#" + l) if l.startswith("#") else l for l in lines).strip()


def ban_tin():
    c = conf()
    db = sqlite3.connect(HOME / "data" / "radar.db")
    db.row_factory = sqlite3.Row
    has = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    q = lambda sql, *a: db.execute(sql, a).fetchone()[0]
    L = [f"# Bản tin Radar LINHX · {TODAY.isoformat()}", ""]
    tong = []
    if "community" in has:
        n = q("SELECT count(*) FROM community WHERE coalesce(loai,'') NOT IN ('sự kiện','giải thưởng')")
        tong.append(f"{n} cộng đồng")
        tong.append(f"{q('SELECT count(*) FROM company')} doanh nghiệp")
        tong.append(f"{q('SELECT count(*) FROM kol')} KOL")
    if "event" in has:
        tong.append(f"{q('SELECT count(*) FROM event')} sự kiện")
    if "award" in has:
        tong.append(f"{q('SELECT count(*) FROM award')} giải thưởng")
    L += ["Kho chung `data/radar.db`: " + ", ".join(tong) + ". Bảng đầy đủ: `output/RADAR-LINHX.xlsx`.", ""]
    if "event" in has:
        den = (TODAY + dt.timedelta(days=30)).isoformat()
        rows = db.execute("SELECT * FROM event WHERE ngay_bd>=? AND ngay_bd<=? AND coalesce(nhan,'') IN ('Đi','Cân nhắc') "
                          "AND coalesce(giai_doan,'')!='bỏ' ORDER BY ngay_bd, diem DESC", (TODAY.isoformat(), den)).fetchall()
        L += ["## Sự kiện nên đi 30 ngày tới", ""]
        L += [f"- {e['ngay_bd']} · **{e['nhan']}** · {e['ten']} ({e['thanh_pho'] or e['hinh_thuc'] or ''}) · {e['diem']} điểm"
              + (f" · {e['url']}" if e["url"] else "") for e in rows[:15]] or ["- chưa có"]
        L.append("")
    if "award" in has:
        rows = db.execute("SELECT * FROM award WHERE coalesce(nhan,'') IN ('Nộp','Cân nhắc nộp') "
                          "AND coalesce(giai_doan,'')!='bỏ' AND (coalesce(han_nop,'')='' OR han_nop>=?) "
                          "ORDER BY nhan!='Nộp', coalesce(nullif(han_nop,''),'9999'), diem DESC", (TODAY.isoformat(),)).fetchall()
        L += ["## Giải nên nộp", ""]
        L += [f"- **{a['nhan']}** · {a['ten']} · hạn {a['han_nop'] or '?'} · {a['ai_nop'] or ''}".rstrip(" ·") for a in rows[:10]] or ["- chưa có"]
        L.append("")
    L += ["## Cộng đồng, doanh nghiệp, KOL", "", demote(latest(HOME / "output" / "digest" / "MOI-NHAT.md")), ""]
    skh = p(c.get("su_kien", {}).get("home", "su-kien"))
    L += ["## Sự kiện và chủ đề (chi tiết)", "", demote(latest(skh / "output" / "digest" / "MOI-NHAT.md")), ""]
    for key, ten in (("cuoc_thi", "Cuộc thi (LAB022)"), ("quy_tai_tro", "Quỹ, tài trợ (LAB013)"), ("kol_ai", "KOL và group AI VN (LAB077)")):
        m = c.get(key, {})
        if m.get("bat") and m.get("ban_tin"):
            txt = latest(p(m["home"]) / Path(m["ban_tin"].replace("\\", "/")))
            if txt:
                L += [f"## {ten}", "", demote(txt), ""]
    out = HOME / "output"
    out.mkdir(exist_ok=True)
    (out / "ban-tin").mkdir(exist_ok=True)
    txt = "\n".join(L) + "\n"
    (out / "ban-tin" / f"BAN-TIN-{TODAY.isoformat()}.md").write_text(txt, encoding="utf-8")
    (out / "BAN-TIN-MOI-NHAT.md").write_text(txt, encoding="utf-8")
    print(f"OK {out / 'BAN-TIN-MOI-NHAT.md'}")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__); return
    if a[0] == "all":
        cmd_all("--no-fetch" in a)
    elif a[0] == "ban-tin":
        ban_tin()
    elif a[0] == "cong-dong":
        sys.exit(0 if cd(a[1:]) else 1)
    elif a[0] == "su-kien":
        sys.exit(0 if sk(a[1:]) else 1)
    else:
        sys.exit(f"Lệnh lạ: {a[0]}. Xem: python radar.py --help")


if __name__ == "__main__":
    main()
