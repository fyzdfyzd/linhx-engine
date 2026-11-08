"""Kiểm tích hợp trên Frappe bench WSL máy cty (site "test", http://127.0.0.1:8000). Chạy TRONG WSL bằng python3 hệ thống,
chỉ dùng thư viện chuẩn. Bộ điều phối gọi sau khi feature đạt nghiệm thu hộp đen (canh/bench.ps1 th). Thợ không sửa thư mục này.
Tên file th_*.py để pytest không tự gom. Mã thoát 0 = đạt.
"""
import http.cookiejar
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

GOC = os.environ.get("TH_URL", "http://127.0.0.1:8000")
SITE = os.environ.get("TH_SITE", "test")
BENCH = os.path.expanduser("~/frappe-bench")
ADMIN = ("Administrator", os.environ.get("TH_ADMIN_MK", "admin"))
MK_THU = "th-kiem-Thu-2026!"


def ghi(*a):
    print("[th]", *a, flush=True)


def cho_bench(giay=90):
    for _ in range(giay // 3):
        try:
            with urllib.request.urlopen(GOC + "/api/method/ping", timeout=5) as r:
                if r.status == 200:
                    return
        except Exception:
            pass
        time.sleep(3)
    raise SystemExit("bench không trả ping 200 ở " + GOC)


class Phien:
    def __init__(self, user=None, mk=None):
        self.cj = http.cookiejar.CookieJar()
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
        self.user = user or "Guest"
        if user:
            ma, t = self.goi("POST", "/api/method/login", {"usr": user, "pwd": mk})
            assert ma == 200, f"đăng nhập {user} lỗi {ma}: {t}"

    def goi(self, pt, duong, du_lieu=None, headers=None):
        url = GOC + duong
        than = None
        h = {"Accept": "application/json"}
        h.update(headers or {})
        if du_lieu is not None and pt == "GET":
            url += ("&" if "?" in url else "?") + urllib.parse.urlencode(du_lieu)
        elif du_lieu is not None:
            than = json.dumps(du_lieu).encode()
            h["Content-Type"] = "application/json"
        rq = urllib.request.Request(url, data=than, method=pt, headers=h)
        try:
            with self.op.open(rq, timeout=30) as r:
                b = r.read()
                ma = r.status
        except urllib.error.HTTPError as e:
            b = e.read()
            ma = e.code
        try:
            return ma, json.loads(b.decode() or "{}")
        except Exception:
            return ma, {"_raw": b.decode(errors="ignore")[:500]}

    def tao(self, doctype, doc):
        ma, t = self.goi("POST", "/api/resource/" + urllib.parse.quote(doctype), doc)
        assert ma == 200, f"tạo {doctype} lỗi {ma}: {str(t)[:400]}"
        return t["data"]

    def ds(self, doctype, loc, truong=("name",)):
        ma, t = self.goi("GET", "/api/resource/" + urllib.parse.quote(doctype),
                         {"filters": json.dumps(loc), "fields": json.dumps(list(truong)), "limit_page_length": 100})
        return ma, (t.get("data") or [])


def bench(*lenh):
    r = subprocess.run(["bench", "--site", SITE, *lenh], cwd=BENCH, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"bench {' '.join(lenh)} lỗi:\n{r.stdout[-800:]}{r.stderr[-800:]}")
    return r.stdout


def bat_co(admin, **co):
    ma, t = admin.goi("PUT", "/api/resource/LX%20Cau%20Hinh/LX%20Cau%20Hinh", co)
    assert ma == 200, f"bật cờ LX Cau Hinh lỗi {ma}: {t}"


def nguoi_dung(admin, email, vai_tro):
    ma, _ = admin.goi("GET", "/api/resource/User/" + urllib.parse.quote(email))
    if ma != 200:
        admin.tao("User", {"email": email, "first_name": email.split("@")[0], "new_password": MK_THU,
                           "send_welcome_email": 0, "user_type": "System User", "roles": [{"role": r} for r in vai_tro]})
    else:
        admin.goi("PUT", "/api/resource/User/" + urllib.parse.quote(email),
                  {"new_password": MK_THU, "roles": [{"role": r} for r in vai_tro]})
    return email


def chay(ham):
    try:
        cho_bench()
        ham()
    except AssertionError as e:
        ghi("TRƯỢT:", e)
        sys.exit(1)
    ghi("ĐẠT")
