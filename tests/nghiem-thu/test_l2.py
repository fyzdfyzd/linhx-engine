"""L2: sự kiện qua outbox: lõi phát, gói nghe, lỗi thì chạy lại, không giao trùng.

Hợp đồng (HOP-DONG.md, Đợt 3):
- DocType "LX Su Kien" (linhx_core): ten (Data), du_lieu (JSON hoặc Long Text), trang_thai (Select: cho, xong, hong),
  lan (Int), da_giao (Long Text: các hàm đã giao xong), loi (Long Text).
- apps/linhx_core/linhx_core/su_kien.py (thuần Python, kho là list[dict] khi kiểm; bản Frappe dùng DocType):
    phat(ten: str, du_lieu: dict, kho: list) -> dict  (thêm bản ghi trang_thai "cho", lan 0, da_giao [])
    chay(kho: list, bang_nghe: dict[str, list[str]], goi: callable(duong_ham, ban_ghi)) -> dict {"xong": n, "loi": n}
        mỗi bản ghi "cho": gọi từng hàm nghe chưa có trong da_giao; hàm lỗi thì lan += 1, ghi loi, giữ "cho";
        lan >= TRAN_LAN (5) thì "hong"; mọi hàm xong thì "xong". Hàm đã giao không gọi lại ở lượt sau.
- hooks.py linhx_core: scheduler_events chạy su_kien (all hoặc cron ≤ 5 phút).
"""
from _chung import CORE, nap_module, ten_truong, tim_doctype


def _m():
    return nap_module("linhx_core.su_kien", CORE)


def test_doctype_su_kien():
    """Tiêu chí: có DocType LX Su Kien đủ trường"""
    _, d = tim_doctype("LX Su Kien")
    assert d, "thiếu DocType LX Su Kien"
    tr = ten_truong(d)
    for f in ["ten", "du_lieu", "trang_thai", "lan", "da_giao", "loi"]:
        assert f in tr, f
    assert {"cho", "xong", "hong"} <= set(str(tr["trang_thai"].get("options", "")).split("\n"))
    assert "su_kien" in (CORE / "linhx_core" / "hooks.py").read_text(encoding="utf-8")


def test_phat_va_giao_mot_lan():
    """Tiêu chí: phát rồi chạy thì mỗi hàm nghe nhận đúng một lần"""
    m = _m()
    kho, nhan = [], []
    m.phat("don.da_tra", {"don": "DON-1"}, kho)
    bang = {"don.da_tra": ["a.giao", "b.ghi_so"]}
    kq = m.chay(kho, bang, lambda h, b: nhan.append((h, b["du_lieu"]["don"])))
    assert kq["xong"] == 1 and kho[0]["trang_thai"] == "xong"
    m.chay(kho, bang, lambda h, b: nhan.append((h, b["du_lieu"]["don"])))
    assert sorted(nhan) == [("a.giao", "DON-1"), ("b.ghi_so", "DON-1")]


def test_loi_chay_lai_khong_trung_va_hong_sau_tran():
    """Tiêu chí: hàm lỗi được chạy lại, hàm đã xong không gọi lại, quá trần thì hong"""
    m = _m()
    kho, goi = [], []
    m.phat("don.da_tra", {"don": "DON-2"}, kho)

    def g(h, b):
        goi.append(h)
        if h == "b.loi":
            raise RuntimeError("mạng")

    bang = {"don.da_tra": ["a.ok", "b.loi"]}
    for _ in range(m.TRAN_LAN + 2):
        m.chay(kho, bang, g)
    assert goi.count("a.ok") == 1
    assert goi.count("b.loi") == m.TRAN_LAN
    assert kho[0]["trang_thai"] == "hong" and "mạng" in kho[0]["loi"]
