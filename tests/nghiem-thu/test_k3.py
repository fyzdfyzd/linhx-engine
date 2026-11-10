"""K3: ifagent.net trỏ về bản mới trên VM (HTTPS), event.ifagent.net giữ nguyên.

Hợp đồng (HOP-DONG.md, Đợt 4):
- deploy/Caddyfile có khối ifagent.net và www.ifagent.net trỏ trang BU ifagent (khuôn C1), TLS tự động.
- Linh đổi bản ghi A ifagent.net, www về 35.198.251.2 ở nhà đăng ký (việc người).
- Bằng chứng: bang-chung/K3/dns.json {"luc": str, "ten_mien": "ifagent.net", "ip": "35.198.251.2", "https": 200, "event_https": 200}
"""
from _chung import GOC, bang_chung_json


def test_caddy_co_ifagent():
    """Tiêu chí: Caddy phục vụ ifagent.net và www"""
    chu = (GOC / "deploy" / "Caddyfile").read_text(encoding="utf-8")
    assert "ifagent.net" in chu and "www.ifagent.net" in chu


def test_bang_chung_dns():
    """Tiêu chí: ifagent.net trả HTTPS 200 từ VM, event.ifagent.net vẫn chạy"""
    d = bang_chung_json("K3", "dns.json")
    assert d["ip"] == "35.198.251.2" and d["https"] == 200 and d["event_https"] == 200
