"""N5: hai bản cài linhx và ifagent trên VM linhx-engine-1, mỗi bản một DB.

Không gọi mạng thật trong test. Kiểm bằng:
- cấu hình bản cài trong repo: deploy/sites/linhx.json và deploy/sites/ifagent.json
  (đầu vào cho `linhx tao-site`, dạng {"modules": {...}}, có thể thêm trường khác)
- bằng chứng ghi trên VM: bang-chung/N5/ping.json
  {"luc": "ISO-8601", "may": "linhx-engine-1",
   "sites": [{"ten": "linhx", "url": str, "status": 200, "db_name": str}, {"ten": "ifagent", ...}]}
"""
import datetime as dt

from _chung import GOC, doc_json, bang_chung_json


def test_co_cau_hinh_hai_ban_cai():
    for ten in ["linhx", "ifagent"]:
        p = GOC / "deploy" / "sites" / f"{ten}.json"
        assert p.exists(), f"thiếu deploy/sites/{ten}.json"
        d = doc_json(p)
        assert isinstance(d.get("modules"), dict) and d["modules"], f"{ten}.json thiếu modules"


def test_ping_ca_hai_200_db_rieng():
    d = bang_chung_json("N5", "ping.json")
    assert d.get("may") == "linhx-engine-1"
    dt.datetime.fromisoformat(d["luc"].replace("Z", "+00:00"))
    sites = {s["ten"]: s for s in d.get("sites", [])}
    assert {"linhx", "ifagent"} <= set(sites), "ping.json phải có cả linhx và ifagent"
    for ten in ["linhx", "ifagent"]:
        s = sites[ten]
        assert s.get("status") == 200, f"{ten}: /api/method/ping không trả 200"
        assert "/api/method/ping" in s.get("url", ""), f"{ten}: url phải là /api/method/ping"
        assert s.get("db_name"), f"{ten}: thiếu db_name"
    assert sites["linhx"]["db_name"] != sites["ifagent"]["db_name"], "hai bản cài dùng chung DB"
    assert sites["linhx"]["url"] != sites["ifagent"]["url"], "hai bản cài cùng url"
