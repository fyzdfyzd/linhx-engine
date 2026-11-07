"""R1: adapter CTS. Engine nhận đúng payload tạo đơn (POST /v1/checkout) và webhook SePay (POST /v1/pay/sepay/webhook)
hiện nay của Chiêm Tinh Số, trả cùng dạng. 20 payload mẫu ở du-lieu/cts/ (đã ẩn danh, xem README trong đó).

Hợp đồng (HOP-DONG.md):
- apps/linhx_core/linhx_core/cts_adapter/__init__.py, hop_dong.py thuần Python (không import frappe ở đầu file):
    tao_don(payload: dict, danh_muc: dict, kho: dict) -> (ma_http: int, than: dict)
        danh_muc {sku: {"ten", "gia", "kenh": [...]}}; giá lấy từ danh_muc, bỏ qua gia/tong client gửi.
        Thành công: thêm {"order_id", "noi_dung_ck", "tong", "da_nhan": 0, "trang_thai": "cho_thanh_toan", "email", ...}
        vào kho["don"]; trả cùng dạng serialize_public_order của CTS (không có email, ho_so).
        Lỗi: (422 | 404, {"detail": str}) như CTS; detail nêu tên trường sai.
    nhan_webhook(payload: dict, kho: dict, authorization: str | None, khoa: str) -> (ma_http, than)
        401 khi Authorization không phải "Apikey <khoa>"; còn lại đúng luật handle_sepay_webhook của CTS
        (chống trùng theo tx_id trong kho["tx"], khớp mã CTS[0-9A-F]{10} không phân biệt hoa thường, thiếu/đủ/thừa/muộn).
    kho = {"don": [dict], "tx": [str]}
- apps/linhx_core/linhx_core/cts_adapter/api.py: endpoint Frappe @frappe.whitelist(allow_guest=True) `checkout` và
  `sepay_webhook` gọi hop_dong (đọc header Authorization, khoá từ cấu hình site, không viết khoá trong code).
"""
import copy
import json
import re

from _chung import CORE, DU_LIEU, nap_module

CTS = DU_LIEU / "cts"
KHOA = "khoa-thu-r1"


def _hd():
    return nap_module("linhx_core.cts_adapter.hop_dong", CORE)


def _mau(loai):
    ds = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(CTS.glob(f"{loai}-*.json"))]
    assert len(ds) == 10, f"thiếu payload mẫu {loai}"
    return ds


def _danh_muc():
    return json.loads((CTS / "danh-muc.json").read_text(encoding="utf-8"))


def _dang(x):
    if isinstance(x, dict):
        return {k: _dang(v) for k, v in x.items()}
    if isinstance(x, bool):
        return "bool"
    if isinstance(x, (int, float)):
        return "so"
    if isinstance(x, str):
        return "str"
    if isinstance(x, list):
        return "list"
    return None


def _cung_dang(mong, that, duong="body"):
    """Mọi khoá CTS trả phải có, cùng kiểu (None ở mẫu = kiểu nào cũng được)."""
    loi = []
    for k, v in mong.items():
        if k not in that:
            loi.append(f"{duong}.{k}: thiếu")
            continue
        if v is None:
            continue
        if isinstance(v, dict):
            if not isinstance(that[k], dict):
                loi.append(f"{duong}.{k}: phải là object")
            else:
                loi += _cung_dang(v, that[k], f"{duong}.{k}")
        elif that[k] != v:
            loi.append(f"{duong}.{k}: CTS kiểu {v}, adapter kiểu {that[k]}")
    return loi


def _kho_tu(mau):
    return {"don": copy.deepcopy(mau["truoc"]["don"]), "tx": list(mau["truoc"]["tx_da_co"])}


def test_thuan_python_va_co_endpoint():
    hd = _hd()
    assert callable(hd.tao_don) and callable(hd.nhan_webhook)
    api = CORE / "linhx_core" / "cts_adapter" / "api.py"
    assert api.exists(), "thiếu cts_adapter/api.py (endpoint Frappe)"
    chu = api.read_text(encoding="utf-8")
    assert chu.count("allow_guest=True") >= 2, "checkout và sepay_webhook phải whitelist allow_guest=True"
    assert "def checkout" in chu and "def sepay_webhook" in chu
    assert "hop_dong" in chu, "api.py phải gọi hop_dong (không viết lại luật)"
    assert re.search(r"(?i)authorization", chu), "sepay_webhook phải đọc header Authorization"
    assert not re.search(r"""(?i)khoa\w*\s*=\s*['"][^'"]{6,}['"]""", chu), "không viết khoá webhook trong code"


def test_tao_don_cung_dang_cts():
    hd, dm = _hd(), _danh_muc()
    kho = {"don": [], "tx": []}
    ma_ck = set()
    for m in _mau("checkout"):
        ma, than = hd.tao_don(copy.deepcopy(m["vao"]), dm, kho)
        mt = m["mo_ta"]
        assert ma == m["ra"]["http"], f"[{mt}] mã HTTP {ma}, CTS {m['ra']['http']}"
        if ma != 200:
            assert isinstance(than.get("detail"), str) and than["detail"], f"[{mt}] lỗi phải có detail"
            truong = re.findall(r"'([a-z_]+)'", m["ra"]["body"]["detail"])
            if ma == 422 and truong:
                assert truong[0] in than["detail"], f"[{mt}] detail phải nêu trường {truong[0]}"
            continue
        loi = _cung_dang(_dang(m["ra"]["body"]), _dang(than))
        assert not loi, f"[{mt}] khác dạng CTS: " + "; ".join(loi[:8])
        sp = dm[m["vao"]["sku"]]
        assert than["tong"] == sp["gia"] and than["gia_goc"] == sp["gia"], f"[{mt}] giá phải lấy từ danh mục"
        assert than["qr"]["so_tien"] == than["tong"]
        assert re.fullmatch(r"CTS[0-9A-F]{10}", than["qr"]["noi_dung_ck"]), f"[{mt}] noi_dung_ck phải dạng CTS + 10 hex"
        assert than["trang_thai"] == "cho_thanh_toan" and than["order_id"].startswith("ord_")
        assert "email" not in than and "ho_so" not in than, f"[{mt}] không trả email, ho_so ra API công khai"
        assert than["qr"]["noi_dung_ck"] not in ma_ck, "noi_dung_ck phải khác nhau giữa các đơn"
        ma_ck.add(than["qr"]["noi_dung_ck"])
    assert len(kho["don"]) == 6, "6 đơn hợp lệ phải vào kho, đơn lỗi không vào"
    d2 = [d for d in kho["don"] if d.get("email") == "khach02@vidu.vn"]
    assert d2 and d2[0]["tong"] == 199000, "email chuẩn hoá (bỏ cách, chữ thường) và tong theo danh mục"


def test_webhook_dung_luat_cts():
    hd = _hd()
    for m in _mau("webhook"):
        kho = _kho_tu(m)
        ma, than = hd.nhan_webhook(copy.deepcopy(m["vao"]), kho, f"Apikey {KHOA}", KHOA)
        mt = m["mo_ta"]
        assert ma == m["ra"]["http"], f"[{mt}] mã HTTP {ma}, CTS {m['ra']['http']}"
        if ma != 200:
            assert isinstance(than.get("detail"), str)
        else:
            assert than == m["ra"]["body"], f"[{mt}] CTS trả {m['ra']['body']}, adapter trả {than}"
        d = kho["don"][0]
        assert d["trang_thai"] == m["sau"]["trang_thai"] and d["da_nhan"] == m["sau"]["da_nhan"], \
            f"[{mt}] đơn sau xử lý phải là {m['sau']}, đang {d['trang_thai']}/{d['da_nhan']}"


def test_webhook_sai_khoa_401_va_khong_doi_kho():
    hd = _hd()
    m = _mau("webhook")[0]
    for auth in [None, "", f"Bearer {KHOA}", "Apikey sai-khoa", "Apikey"]:
        kho = _kho_tu(m)
        ma, _ = hd.nhan_webhook(copy.deepcopy(m["vao"]), kho, auth, KHOA)
        assert ma == 401, f"Authorization={auth!r} phải 401"
        assert kho == _kho_tu(m), "sai khoá thì không được đổi đơn"


def test_tao_don_roi_tra_tien_tron_vong():
    hd, dm = _hd(), _danh_muc()
    kho = {"don": [], "tx": []}
    m = _mau("checkout")[2]
    ma, than = hd.tao_don(copy.deepcopy(m["vao"]), dm, kho)
    assert ma == 200
    ck = than["qr"]["noi_dung_ck"]
    wh = {"id": 777001, "content": f"thanh toan {ck.lower()}", "transferType": "in", "transferAmount": than["tong"]}
    ma2, b2 = hd.nhan_webhook(dict(wh), kho, f"Apikey {KHOA}", KHOA)
    assert ma2 == 200 and b2["status"] == "matched" and b2["trang_thai"] == "da_thanh_toan" and b2["order_id"] == than["order_id"]
    ma3, b3 = hd.nhan_webhook(dict(wh), kho, f"Apikey {KHOA}", KHOA)
    assert ma3 == 200 and b3.get("idempotent") is True, "gửi lại cùng tx_id phải idempotent"
    don = [d for d in kho["don"] if d["noi_dung_ck"] == ck][0]
    assert don["da_nhan"] == than["tong"], "trùng tx_id không được cộng tiền hai lần"
