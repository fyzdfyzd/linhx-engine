#!/usr/bin/env python3
"""K8 đối chiếu VM (canh chạy mỗi vòng tổng hợp trên máy cty, có mạng tới VM). Thợ không sửa.

Với feature đã passes=true có bằng chứng HTTP trên VM, gọi lại URL thật:
  N5: bang-chung/N5/ping.json  sites[].url -> 200 và {"message":"pong"}
  C3: bang-chung/C3/chay.json  url -> 200 và chứa tieu_de_thay
  T1, T2: url_ifagent / url_linhx trả 200
Sai 2 lượt liền (lưu ở --trang-thai) thì hạ passes về false trong features-dot1*.json (thợ làm lại) và in "HẠ VỀ".
Lỗi mạng của chính máy cty (không gọi được cả trang gốc VM) thì bỏ qua lượt này, không tính.
In tối đa vài dòng; không có gì để báo thì không in.
"""
import argparse
import json
import pathlib
import urllib.error
import urllib.request
from urllib.parse import urlparse


def goi(url, timeout=15):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/json"}), timeout=timeout) as r:
            return r.status, r.read(200000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # mạng
        return None, str(e)


def kiem_n5(bc):
    loi = []
    for s in bc.get("sites", []):
        ma, than = goi(s.get("url", ""))
        if ma != 200 or "pong" not in than:
            loi.append(f"{s.get('ten')} {s.get('url')} -> {ma}")
    return loi


def kiem_c3(bc):
    ma, than = goi(bc.get("url", ""))
    if ma != 200:
        return [f"{bc.get('url')} -> {ma}"]
    if bc.get("tieu_de_thay") and bc["tieu_de_thay"] not in than:
        return [f"{bc.get('url')} không có tiêu đề '{bc['tieu_de_thay'][:40]}'"]
    return []


def kiem_url(*khoa):
    def f(bc):
        loi = []
        for k in khoa:
            u = bc.get(k)
            if u:
                ma, _ = goi(u)
                if ma != 200:
                    loi.append(f"{k} {u} -> {ma}")
        return loi
    return f


KIEM = {"N5": ("ping.json", kiem_n5), "C3": ("chay.json", kiem_c3),
        "T1": ("e2e.json", kiem_url("url_ifagent", "url_linhx")), "T2": ("e2e.json", kiem_url("url_linhx"))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goc", required=True)
    ap.add_argument("--trang-thai", required=True)
    a = ap.parse_args()
    goc = pathlib.Path(a.goc)
    tt_p = pathlib.Path(a.trang_thai)
    tt = json.loads(tt_p.read_text(encoding="utf-8")) if tt_p.exists() else {}
    files = [goc / "features-dot1.json", goc / "features-dot1b.json"]
    data = {p: json.loads(p.read_text(encoding="utf-8")) for p in files if p.exists()}
    can = [(p, f) for p, d in data.items() for f in d["features"] if f.get("passes") and f["id"] in KIEM]
    if not can:
        return
    host = None
    ra, doi = [], set()
    for p, f in can:
        ten, ham = KIEM[f["id"]]
        bcp = goc / "bang-chung" / f["id"] / ten
        if not bcp.exists():
            loi = [f"thiếu {bcp.relative_to(goc)}"]
        else:
            bc = json.loads(bcp.read_text(encoding="utf-8"))
            u = next((v for v in bc.values() if isinstance(v, str) and v.startswith("http")), None) or \
                next((s.get("url") for s in bc.get("sites", []) if s.get("url")), None)
            if u and host is None:
                h = urlparse(u)
                ma, _ = goi(f"{h.scheme}://{h.netloc}/", timeout=10)
                host = ma is not None
                if not host:
                    print("bỏ qua lượt này: máy cty không gọi được VM")
                    return
            loi = ham(bc)
        if loi:
            tt[f["id"]] = tt.get(f["id"], 0) + 1
            if tt[f["id"]] >= 2:
                f["passes"] = False
                doi.add(p)
                ra.append(f"- {f['id']} HẠ VỀ chưa đạt (sai 2 lượt liền): {'; '.join(loi)[:300]}")
                tt[f["id"]] = 0
            else:
                ra.append(f"- {f['id']} lệch lần 1, lượt sau kiểm lại: {'; '.join(loi)[:300]}")
        else:
            tt[f["id"]] = 0
    for p in doi:
        p.write_text(json.dumps(data[p], indent=2, ensure_ascii=False), encoding="utf-8")
    tt_p.parent.mkdir(parents=True, exist_ok=True)
    tt_p.write_text(json.dumps(tt), encoding="utf-8")
    if ra:
        print("\n".join(ra))


if __name__ == "__main__":
    main()
