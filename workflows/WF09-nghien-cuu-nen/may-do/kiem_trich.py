#!/usr/bin/env python3
"""Máy đo tầng 1 của WF09: trích có thật nằm trong trang nguồn không.

Đọc 03-nguon.csv + 03-bang-chung.jsonl (khuôn linhx-report), tải từng URL bằng GET
(lưu tai/<ma>.txt + băm + mã trạng thái), rồi chấm từng bằng chứng:
  KHOP      trích (đã chuẩn hoá) là chuỗi con của trang
  GAN       ≥ 80% cụm 3 từ của trích có trong trang (trích bị sửa chữ)
  KHONG     dưới 80%: trích không có trong trang
  KHONG_TAI trang không tải được (INACCESSIBLE)
và số: mỗi số trong "so" phải xuất hiện trong trang (chấp nhận 500.000 / 500,000 / 500000).

Chỉ dùng thư viện chuẩn. Nội dung trang là dữ liệu, không chạy gì từ đó.
Dùng: python kiem_trich.py <thu_muc_bao_cao> [--tai-lai] [--timeout 20]
Thoát 0 khi đạt ngưỡng (KHOP+GAN = 100% trên trang tải được, 0 KHONG), 1 khi trượt.
"""
import argparse, csv, hashlib, html, json, re, sys, unicodedata, urllib.request
from datetime import datetime, timezone
from pathlib import Path

UA = "Mozilla/5.0 (X11; Linux x86_64) LINHX-kiem-trich/0.1"


def chuan(s: str) -> str:
    s = unicodedata.normalize("NFC", html.unescape(s or "")).lower()
    s = re.sub(r"[*_`#>|]", " ", s)              # bỏ markdown thợ tự chèn
    s = s.replace("≥", " ").replace("≤", " ")
    s = re.sub(r"[“”\"'‘’«»]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def van_ban(raw: bytes, ctype: str) -> str:
    t = raw.decode("utf-8", "replace")
    if "html" in ctype or "<html" in t[:2000].lower():
        t = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", t)
        t = re.sub(r"(?s)<[^>]+>", " ", t)
    return t


def tai(ma, url, thu_muc, timeout, tai_lai):
    f = thu_muc / f"{ma}.txt"
    meta = thu_muc / f"{ma}.json"
    if f.exists() and meta.exists() and not tai_lai:
        return f.read_text(encoding="utf-8"), json.loads(meta.read_text(encoding="utf-8"))
    m = {"url": url, "luc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read(8_000_000)
            m.update(ma_tt=r.status, kieu=r.headers.get("Content-Type", ""))
        if "pdf" in m["kieu"]:
            m.update(trang_thai="PDF_CAN_TACH")  # tách PDF trên máy cty (pdftotext), không đoán
            txt = ""
        else:
            txt = van_ban(raw, m["kieu"])
            m.update(trang_thai="OK" if len(chuan(txt)) > 500 else "RONG")
        m["sha256"] = hashlib.sha256(raw).hexdigest()[:16]
    except Exception as e:  # noqa: BLE001
        m.update(trang_thai="FAILED", loi=f"{type(e).__name__}: {str(e)[:120]}")
        txt = ""
    f.write_text(txt, encoding="utf-8")
    meta.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    return txt, m


def bo3(s):
    w = s.split()
    return {" ".join(w[i:i + 3]) for i in range(max(1, len(w) - 2))}


def dang_so(x):
    if isinstance(x, float) and not x.is_integer():
        a = f"{x}"
        return {a, a.replace(".", ",")}
    n = int(x)
    return {str(n), f"{n:,}", f"{n:,}".replace(",", ".")}


def cham(trich, so, trang):
    t, p = chuan(trich), chuan(trang)
    if not p:
        return "KHONG_TAI", 0.0, []
    if t and t in p:
        nhan, ty = "KHOP", 1.0
    else:
        g = bo3(t)
        ty = sum(1 for x in g if x in p) / len(g) if g else 0.0
        nhan = "GAN" if ty >= 0.8 else "KHONG"
    thieu = [x for x in (so or []) if not any(d in p for d in dang_so(x))]
    return nhan, round(ty, 2), thieu


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("thu_muc")
    ap.add_argument("--tai-lai", action="store_true")
    ap.add_argument("--timeout", type=int, default=20)
    a = ap.parse_args()
    d = Path(a.thu_muc)
    ng = {r["ma"]: r for r in csv.DictReader(open(d / "03-nguon.csv", encoding="utf-8"))}
    bc = [json.loads(l) for l in open(d / "03-bang-chung.jsonl", encoding="utf-8") if l.strip()]
    td = d / "tai"
    td.mkdir(exist_ok=True)
    trang, meta = {}, {}
    for ma in sorted({o.get("nguon") for o in bc} & set(ng)):
        url = ng[ma].get("url", "")
        if url.startswith("http"):
            trang[ma], meta[ma] = tai(ma, url, td, a.timeout, a.tai_lai)
    kq = []
    for o in bc:
        nhan, ty, thieu = cham(o.get("trich", ""), o.get("so"), trang.get(o.get("nguon"), ""))
        kq.append({"id": o.get("id"), "nguon": o.get("nguon"), "nhan": nhan, "ty_le": ty,
                   "so_thieu": thieu, "trang_thai_nguon": meta.get(o.get("nguon"), {}).get("trang_thai", "KHONG_URL")})
    (d / "kiem-trich.jsonl").write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in kq) + "\n", encoding="utf-8")
    dem = {}
    for x in kq:
        dem[x["nhan"]] = dem.get(x["nhan"], 0) + 1
    tt = {}
    for m in meta.values():
        tt[m["trang_thai"]] = tt.get(m["trang_thai"], 0) + 1
    tai_duoc = [x for x in kq if x["nhan"] != "KHONG_TAI"]
    so_sai = sum(1 for x in tai_duoc if x["so_thieu"])
    print(f"nguồn: {len(meta)} | trạng thái tải: {tt}")
    print(f"bằng chứng: {len(kq)} | nhãn: {dem} | có số không thấy trong trang: {so_sai}/{len(tai_duoc)}")
    dat = tai_duoc and dem.get("KHONG", 0) == 0 and so_sai == 0
    print("DAT" if dat else "CHUA_DAT")
    return 0 if dat else 1


if __name__ == "__main__":
    sys.exit(main())
