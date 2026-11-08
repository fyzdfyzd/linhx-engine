"""C3: ifagent.net bản mới trên khuôn, chạy trên IP VM (chưa đổi DNS). Trang chạy trên IP, form về bản cài ifagent.

Hợp đồng (HOP-DONG.md):
- sites/ifagent/site.json {"ten": "ifagent", "ban_cai": "ifagent", "noi_dung": {"tieu_de", "mo_ta", "muc": [...]}}
- trang-bu dựng theo SITE_JSON=<đường dẫn site.json>: nội dung từ "noi_dung" (NOI_DUNG_URL vẫn ưu tiên nếu có).
- deploy/: cấu hình phục vụ trang ifagent trên VM (vd. Caddy/nginx khối cho thư mục tĩnh) và chuyển
  /api/method/linhx_core.crm.api_form.* về bản cài ifagent (N5).
- Bằng chứng trên VM linhx-engine-1: bang-chung/C3/chay.json
    {"luc", "url": "http://<IP>/...", "status": 200, "tieu_de_thay": "<tieu_de trong site.json>",
     "form": {"status": 200, "ban_cai": "ifagent", "nguoi": "<name LX Nguoi mới>"}}
"""
import ipaddress
import json
from urllib.parse import urlparse

from _chung import GOC, bang_chung_json, dung_trang_bu

SITE = GOC / "sites" / "ifagent" / "site.json"


def _site():
    assert SITE.exists(), "thiếu sites/ifagent/site.json"
    return json.loads(SITE.read_text(encoding="utf-8"))


def test_site_json():
    d = _site()
    assert d.get("ten") == "ifagent" and d.get("ban_cai") == "ifagent"
    nd = d.get("noi_dung") or {}
    assert nd.get("tieu_de") and isinstance(nd.get("muc"), list) and nd["muc"]


def test_dung_theo_site_json():
    d = _site()
    out = dung_trang_bu({"SITE_JSON": str(SITE)})
    assert d["noi_dung"]["tieu_de"] in (out / "index.html").read_text(encoding="utf-8")


def test_deploy_co_cau_hinh():
    chu = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in (GOC / "deploy").rglob("*") if p.is_file())
    assert "ifagent" in chu and "api_form" in chu, "deploy/ phải phục vụ trang ifagent và chuyển form về bản cài ifagent"


def test_bang_chung_chay_tren_ip():
    d = bang_chung_json("C3", "chay.json")
    host = urlparse(d.get("url", "")).hostname or ""
    ipaddress.ip_address(host)  # chưa đổi DNS: phải là IP
    assert d.get("status") == 200
    assert d.get("tieu_de_thay") == _site()["noi_dung"]["tieu_de"]
    f = d.get("form") or {}
    assert f.get("status") == 200 and f.get("ban_cai") == "ifagent" and f.get("nguoi")
