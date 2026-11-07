"""N6: sao lưu DB hằng ngày mỗi bản cài + nhật ký truy cập dữ liệu khách.

Hợp đồng (HOP-DONG.md):
- deploy/sao-luu.sh: sao lưu từng site (bench --site <s> backup), giữ tối thiểu 7 bản; lịch hằng ngày
  khai trong deploy/ (cron, systemd timer hoặc service scheduler trong docker-compose.yml) gọi sao-luu.sh
- bang-chung/N6/sao-luu.json ghi trên VM:
  {"luc_kiem": ISO, "sites": [{"ten": "linhx", "file": str, "luc": ISO}, {"ten": "ifagent", ...}],
   "khoi_phuc_thu": {"site_tam": str, "tu_file": str, "ping": 200}}
- Bản sao lưu không nằm trong repo (không có *.sql.gz, *.sql trong linhx-engine)
"""
import datetime as dt

from _chung import GOC, CORE, cac_file, bang_chung_json, tim_doctype


def _iso(s):
    t = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone(dt.timedelta(hours=7)))


def test_co_script_va_lich_hang_ngay():
    sl = GOC / "deploy" / "sao-luu.sh"
    assert sl.exists(), "thiếu deploy/sao-luu.sh"
    chu = sl.read_text(encoding="utf-8")
    assert "backup" in chu, "sao-luu.sh phải gọi bench backup"
    co_lich = False
    for p in cac_file(GOC / "deploy"):
        if p.name == "sao-luu.sh":
            continue
        t = p.read_text(encoding="utf-8", errors="ignore")
        if "sao-luu.sh" in t:
            co_lich = True
    assert co_lich, "chưa có lịch nào trong deploy/ gọi sao-luu.sh"


def test_ban_sao_luu_moi_trong_24_gio():
    d = bang_chung_json("N6", "sao-luu.json")
    luc_kiem = _iso(d["luc_kiem"])
    sites = {s["ten"]: s for s in d.get("sites", [])}
    for ten in ["linhx", "ifagent"]:
        assert ten in sites, f"thiếu bản sao lưu của {ten}"
        assert sites[ten].get("file"), f"{ten}: thiếu tên file sao lưu"
        tuoi = luc_kiem - _iso(sites[ten]["luc"])
        assert dt.timedelta(0) <= tuoi <= dt.timedelta(hours=24), f"{ten}: bản sao lưu cũ hơn 24 giờ"


def test_khoi_phuc_thu_vao_site_tam():
    d = bang_chung_json("N6", "sao-luu.json")
    k = d.get("khoi_phuc_thu") or {}
    assert k.get("site_tam") and k["site_tam"] not in ("linhx", "ifagent"), "phải khôi phục vào site tạm, không đè site thật"
    assert k.get("tu_file"), "thiếu file nguồn khôi phục"
    assert k.get("ping") == 200, "site tạm sau khôi phục không trả ping 200"


def test_khong_ban_sao_luu_trong_repo():
    loi = [str(p) for p in cac_file(GOC) if p.name.endswith((".sql.gz", ".sql", ".tar.gz"))]
    assert not loi, "bản sao lưu bị đưa vào repo: " + ", ".join(loi)


def test_co_nhat_ky_truy_cap_du_lieu_khach():
    _, d = tim_doctype("LX Nhat Ky Truy Cap")
    assert d, "thiếu DocType LX Nhat Ky Truy Cap (ai xem bản ghi khách nào, lúc nào)"
    assert len(d.get("fields", [])) >= 3
