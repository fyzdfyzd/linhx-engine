"""R2: chế độ bóng. Bản sao đơn và webhook SePay của CTS đẩy sang engine; engine ghi đơn bóng và báo lệch.
Cờ tắt mặc định; tắt thì engine không nhận. Không giao hàng (không tạo LX Job, không gửi mail).

Hợp đồng (HOP-DONG.md):
- apps/linhx_core/linhx_core/cts_adapter/bong.py thuần Python (không import frappe ở đầu file), dùng lại luật của hop_dong (R1):
    bat(cau_hinh: dict) -> bool                     True chỉ khi cau_hinh["bat_bong"] là True (mặc định tắt)
    nhan_don_bong(don_cts: dict, cau_hinh, kho_bong) -> dict | None
        don_cts {"order_id", "noi_dung_ck", "tong", "trang_thai"}; ghi đơn bóng da_nhan 0. Cờ tắt -> None, kho_bong không đổi.
    nhan_bong(webhook: dict, cau_hinh, kho_bong) -> dict | None
        webhook = thân SePay CTS nhận (không kiểm Apikey ở đây, CTS đã kiểm); áp luật như hop_dong.nhan_webhook lên kho_bong;
        trả {"tx_id", "noi_dung_ck", "trang_thai", "da_nhan", "giao": False}. Cờ tắt -> None, kho_bong không đổi.
    so_lech(don_cts: list[dict], kho_bong) -> list[dict]
        so theo noi_dung_ck các trường da_nhan, trang_thai; mỗi lệch {"noi_dung_ck", "truong", "cts", "bong"};
        đơn chỉ có một bên -> truong "thieu_don".
    kho_bong = {"don": [dict], "tx": [str]}
"""
import copy
import random
import re

from _chung import CORE, nap_module

BAT = {"bat_bong": True}


def _b():
    return nap_module("linhx_core.cts_adapter.bong", CORE)


def _cts_ap(don, tx_da, wh):
    """Luật CTS (handle_sepay_webhook + apply_webhook_payment_to_order), viết lại độc lập để đối chiếu."""
    tx = str(wh["id"])
    if tx in tx_da or wh.get("transferType", "in") != "in":
        return
    m = re.search(r"\b(CTS[0-9A-F]{10})\b", wh.get("content", ""), re.I)
    if not m or m.group(1).upper() != don["noi_dung_ck"]:
        return
    tx_da.add(tx)
    cu = don["trang_thai"]
    don["da_nhan"] += int(wh["transferAmount"])
    if cu in ("het_han", "da_huy", "can_hoan_tien"):
        don["trang_thai"] = "can_hoan_tien"
    elif don["da_nhan"] >= don["tong"]:
        if cu in ("cho_thanh_toan", "thieu_tien"):
            don["trang_thai"] = "da_thanh_toan"
    elif cu in ("cho_thanh_toan", "thieu_tien"):
        don["trang_thai"] = "thieu_tien"


def _sinh_100(seed=20261108):
    """100 đơn CTS + chuỗi webhook (đủ, thiếu, thiếu rồi bù, thừa, trùng tx, tiền ra, nội dung lạ)."""
    r = random.Random(seed)
    don, whs, n = [], [], 0
    for i in range(100):
        ck = "CTS" + "".join(r.choice("0123456789ABCDEF") for _ in range(10))
        tong = r.choice([99000, 149000, 199000, 249000, 299000])
        don.append({"order_id": f"ord_b{i:03d}", "noi_dung_ck": ck, "tong": tong, "da_nhan": 0, "trang_thai": "cho_thanh_toan"})
        kieu = i % 7

        def w(tien, nd=None, loai="in", lap=None):
            nonlocal n
            n += 1
            x = {"id": lap or 5000000 + n, "content": nd if nd is not None else f"{ck if r.random() < .5 else ck.lower()} ck",
                 "transferType": loai, "transferAmount": tien, "gateway": "MBBank"}
            whs.append(x)
            return x
        if kieu == 0:
            w(tong)
        elif kieu == 1:
            w(tong - 50000)
        elif kieu == 2:
            w(tong - 40000)
            w(40000)
        elif kieu == 3:
            w(tong + 1000)
        elif kieu == 4:
            x = w(tong)
            w(tong, lap=x["id"], nd=x["content"])
        elif kieu == 5:
            w(tong, loai="out")
        else:
            w(tong, nd="chuyen tien khong ma")
    r.shuffle(whs)
    return don, whs


def test_co_tat_mac_dinh_thi_khong_nhan():
    b = _b()
    assert b.bat({}) is False and b.bat({"bat_bong": False}) is False and b.bat(BAT) is True
    don, whs = _sinh_100()
    kho = {"don": [], "tx": []}
    for cau_hinh in [{}, {"bat_bong": False}, {"bat_bong": "1"}]:
        assert b.nhan_don_bong(copy.deepcopy(don[0]), cau_hinh, kho) is None
        assert b.nhan_bong(copy.deepcopy(whs[0]), cau_hinh, kho) is None
    assert kho == {"don": [], "tx": []}, "cờ tắt thì engine không ghi gì"


def test_100_don_khop_so_tien_trang_thai():
    b = _b()
    don, whs = _sinh_100()
    cts = copy.deepcopy(don)
    tx_da = set()
    kho = {"don": [], "tx": []}
    for d in don:
        assert b.nhan_don_bong(copy.deepcopy(d), BAT, kho) is not None
    theo_ma = {d["noi_dung_ck"]: d for d in cts}
    for wh in whs:
        m = re.search(r"\b(CTS[0-9A-F]{10})\b", wh.get("content", ""), re.I)
        if m and m.group(1).upper() in theo_ma:
            _cts_ap(theo_ma[m.group(1).upper()], tx_da, wh)
        kq = b.nhan_bong(copy.deepcopy(wh), BAT, kho)
        assert kq is None or kq.get("giao") is False, "chế độ bóng không bao giờ giao hàng"
    assert len(kho["don"]) == 100
    lech = b.so_lech(cts, kho)
    assert lech == [], f"engine bóng lệch CTS: {lech[:5]}"
    tt = {d["trang_thai"] for d in cts}
    assert {"da_thanh_toan", "thieu_tien", "cho_thanh_toan"} <= tt, "bộ mẫu phải phủ đủ trạng thái"


def test_bao_lech_khi_khac():
    b = _b()
    don, whs = _sinh_100()
    cts = copy.deepcopy(don)
    kho = {"don": [], "tx": []}
    for d in don:
        b.nhan_don_bong(copy.deepcopy(d), BAT, kho)
    cts[3]["da_nhan"] = 12345
    cts[7]["trang_thai"] = "da_thanh_toan"
    cts.append({"order_id": "ord_x", "noi_dung_ck": "CTS0000000000", "tong": 1000, "da_nhan": 0, "trang_thai": "cho_thanh_toan"})
    lech = b.so_lech(cts, kho)
    bo = {(x["noi_dung_ck"], x["truong"]) for x in lech}
    assert (cts[3]["noi_dung_ck"], "da_nhan") in bo
    assert (cts[7]["noi_dung_ck"], "trang_thai") in bo
    assert ("CTS0000000000", "thieu_don") in bo
    x = [y for y in lech if y["noi_dung_ck"] == cts[3]["noi_dung_ck"] and y["truong"] == "da_nhan"][0]
    assert x["cts"] == 12345 and x["bong"] == 0
    assert len(lech) == 3, f"chỉ báo đúng 3 chỗ lệch, đang báo {len(lech)}"


def test_khong_giao_hang_trong_ma():
    chu = (CORE / "linhx_core" / "cts_adapter" / "bong.py").read_text(encoding="utf-8")
    for cam in ["linhx_worker", "LX Job", "enqueue", "sendmail", "send_mail", "tao_job", "giao_bao_cao"]:
        assert cam not in chu, f"bong.py không được gọi giao hàng ({cam})"
    assert "hop_dong" in chu, "bong.py phải dùng lại luật của hop_dong (R1), không viết luật thứ hai"
