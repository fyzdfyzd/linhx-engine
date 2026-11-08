"""B3: webhook SePay: đối soát, chống trùng tx_id, chuyển đơn sang da_tra.
Gửi cùng tx_id hai lần chỉ ghi một lần. Sai số tiền thì không chuyển da_tra.

Hợp đồng (HOP-DONG.md):
- linhx_core/pay/sepay.py thuần Python:
    xu_ly(payload: dict, kho: dict, authorization: str | None, khoa: str) -> (ma_http: int, than: dict)
        payload dạng webhook SePay: {"id", "transferType": "in"|"out", "transferAmount", "content", ...}
        kho = {"don": [dict đơn như B2.tao_don], "tx": [str], "lech": [dict]}
        - Authorization khác "Apikey <khoa>" -> (401, ...) và không đổi kho
        - transferType khác "in" -> (200, {"success": True, "bo_qua": ...}), không đổi đơn
        - tx_id = str(payload["id"]) đã có trong kho["tx"] -> (200, {"success": True, "trung": True}), không đổi gì
        - tìm đơn có noi_dung_ck nằm trong content (không phân biệt hoa thường, bỏ dấu cách/gạch);
          không thấy -> ghi kho["lech"], (200, {"success": True, "khop": False})
        - đúng số tiền -> đơn trang_thai "da_tra", tx_id ghi vào đơn; sai số tiền -> đơn giữ cho_tra, ghi kho["lech"]
        - mọi tx hợp lệ (có id, đúng khoá) ghi vào kho["tx"] đúng một lần
- linhx_core/pay/api_sepay.py: @frappe.whitelist(allow_guest=True, methods=["POST"]) `webhook` đọc header Authorization,
  khoá từ site_config (frappe.conf), không viết khoá trong code; khoá cập nhật đơn (for update) khi chuyển da_tra.
"""
import copy

from _chung import CORE, khong_import_frappe_dau_file, nap_module

KHOA = "khoa-thu-b3"
AUTH = f"Apikey {KHOA}"


def _kho():
    return {"don": [{"ma": "DON-1", "so_tien": 99000, "trang_thai": "cho_tra", "noi_dung_ck": "LXDON1A7"},
                    {"ma": "DON-2", "so_tien": 5000, "trang_thai": "cho_tra", "noi_dung_ck": "LXDON2B8"}],
            "tx": [], "lech": []}


def _sp():
    return nap_module("linhx_core.pay.sepay", CORE)


def _tx(id_, tien, nd, loai="in"):
    return {"id": id_, "gateway": "VCB", "transactionDate": "2026-11-09 09:00:00", "accountNumber": "x",
            "transferType": loai, "transferAmount": tien, "content": nd, "referenceCode": "FT1"}


def test_sai_khoa():
    sp, kho = _sp(), _kho()
    cu = copy.deepcopy(kho)
    for a in (None, "", "Apikey sai", KHOA, f"Bearer {KHOA}"):
        ma, _ = sp.xu_ly(_tx(1, 99000, "LXDON1A7"), kho, a, KHOA)
        assert ma == 401
    assert kho == cu


def test_dung_tien_chuyen_da_tra_va_chong_trung():
    sp, kho = _sp(), _kho()
    ma, t = sp.xu_ly(_tx(9001, 99000, "MBVCB.123 lxdon1a7 chuyen tien"), kho, AUTH, KHOA)
    assert ma == 200 and t.get("success") is True
    d = kho["don"][0]
    assert d["trang_thai"] == "da_tra" and str(d.get("tx_id")) == "9001"
    ma, t = sp.xu_ly(_tx(9001, 99000, "LXDON1A7"), kho, AUTH, KHOA)
    assert ma == 200 and t.get("trung") is True
    assert kho["tx"].count("9001") == 1, "cùng tx_id chỉ ghi một lần"


def test_sai_so_tien_khong_chuyen():
    sp, kho = _sp(), _kho()
    sp.xu_ly(_tx(9002, 4000, "LXDON2B8"), kho, AUTH, KHOA)
    assert kho["don"][1]["trang_thai"] == "cho_tra"
    assert kho["lech"], "sai số tiền phải ghi lệch để người xem"
    sp.xu_ly(_tx(9003, 6000, "LXDON2B8"), kho, AUTH, KHOA)
    assert kho["don"][1]["trang_thai"] == "cho_tra", "thừa tiền cũng không tự chuyển, ghi lệch"


def test_noi_dung_co_dau_cach_va_tien_ra():
    sp, kho = _sp(), _kho()
    sp.xu_ly(_tx(9004, 5000, "LX DON2 B8"), kho, AUTH, KHOA)
    assert kho["don"][1]["trang_thai"] == "da_tra", "bỏ dấu cách khi khớp nội dung"
    kho2 = _kho()
    sp.xu_ly(_tx(9005, 99000, "LXDON1A7", loai="out"), kho2, AUTH, KHOA)
    assert kho2["don"][0]["trang_thai"] == "cho_tra", "tiền ra không được chuyển da_tra"
    ma, t = sp.xu_ly(_tx(9006, 1000, "khong co ma"), kho2, AUTH, KHOA)
    assert ma == 200 and t.get("khop") is False and kho2["lech"]


def test_api():
    p = CORE / "linhx_core" / "pay" / "api_sepay.py"
    chu = p.read_text(encoding="utf-8")
    assert "allow_guest=True" in chu and "def webhook(" in chu and "Authorization" in chu
    assert "frappe.conf" in chu or "get_site_config" in chu, "khoá SePay đọc từ site_config"
    assert "for_update" in chu or "for update" in chu.lower(), "khoá dòng đơn khi chuyển da_tra"
    khong_import_frappe_dau_file(CORE / "linhx_core" / "pay" / "sepay.py")
