"""U1: giao diện BU lên site tự động: giao-dien/<bu>/ trong repo -> VM phục vụ ở <bu>.35-198-251-2.nip.io.

Hợp đồng (HOP-DONG.md, Đợt 3, khối giao diện):
- deploy/giao_dien.py (thuần Python chuẩn):
    cac_site(goc) -> list[dict] {"ten", "thu_muc"}: mỗi giao-dien/<ten> có server.mjs hoặc public/index.html, xếp theo tên
    caddy(cac, ip="35.198.251.2", cong_dau=8101) -> str: mỗi site một khối "<ten>.<ip gạch ngang>.nip.io { reverse_proxy 127.0.0.1:<cổng> }",
        cổng tăng dần theo thứ tự cac_site, ổn định
    systemd(site, cong) -> str: unit chạy node server.mjs với PORT=<cổng>, Restart=always, MemoryMax=256M, không chứa bí mật
- deploy/len-giao-dien.sh: trên VM, kéo main, sinh Caddyfile phần giao diện + unit từ giao_dien.py, nạp lại khi đổi;
  timer systemd 5 phút (deploy/linhx-giao-dien.timer). Không cần SSH từ CI.
- Bằng chứng: bang-chung/U1/vm.json {"luc": str, "commit": str, "site": [{"ten": str, "url": "http://<ten>.35-198-251-2.nip.io/", "ma": 200}]}
  đủ sakedemy, tuva, unikon, chụp sau khi một commit đổi giao diện tự lên (ghi "phut_tu_merge" số <= 10).
"""
import re

from _chung import GOC, bang_chung_json, nap_module


def _m():
    return nap_module("giao_dien", GOC / "deploy")


def test_cac_site_va_caddy():
    """Tiêu chí: sinh khối Caddy cho mọi giao diện BU, cổng ổn định"""
    m = _m()
    cs = m.cac_site(GOC)
    ten = [c["ten"] for c in cs]
    assert {"sakedemy", "tuva", "unikon"} <= set(ten) and ten == sorted(ten)
    c1 = m.caddy(cs)
    assert c1 == m.caddy(cs)
    for i, t in enumerate(ten):
        assert re.search(rf"{t}\.35-198-251-2\.nip\.io\s*\{{[^}}]*reverse_proxy 127\.0\.0\.1:{8101 + i}", c1), t


def test_unit_systemd():
    """Tiêu chí: mỗi site một unit node có trần RAM, tự chạy lại"""
    m = _m()
    u = m.systemd(m.cac_site(GOC)[0], 8101)
    assert "server.mjs" in u and "PORT=8101" in u and "Restart=always" in u and "MemoryMax=256M" in u
    assert not re.search(r"(TOKEN|SECRET|PASSWORD|KEY)=\S", u)
    assert (GOC / "deploy" / "len-giao-dien.sh").exists() and (GOC / "deploy" / "linhx-giao-dien.timer").exists()


def test_bang_chung_vm():
    """Tiêu chí: ba site BU trả 200 trên VM, tự lên trong 10 phút sau merge"""
    d = bang_chung_json("U1", "vm.json")
    ok = {s["ten"] for s in d["site"] if s["ma"] == 200 and s["url"] == f"http://{s['ten']}.35-198-251-2.nip.io/"}
    assert {"sakedemy", "tuva", "unikon"} <= ok
    assert float(d["phut_tu_merge"]) <= 10
