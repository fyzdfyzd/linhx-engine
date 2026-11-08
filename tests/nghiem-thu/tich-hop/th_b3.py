"""Tích hợp B3: webhook SePay thật trên bench. Khoá ở site_config "sepay_khoa". Cùng tx_id hai lần chỉ ghi một lần,
sai số tiền không chuyển da_tra, sai khoá 401/403, đúng thì LX Don chuyển da_tra."""
import time

from th_chung import ADMIN, Phien, bat_co, bench, chay, ghi

KHOA = "khoa-tich-hop-b3-" + str(int(time.time()))
URL = "/api/method/linhx_core.pay.api_sepay.webhook"


def kiem():
    bench("set-config", "sepay_khoa", KHOA)
    ad = Phien(*ADMIN)
    bat_co(ad, bat_pay=1, bat_crm=1)
    goi = ad.tao("LX Goi", {"ten": "Gói tích hợp", "gia_san": 5000})
    m = str(int(time.time()))
    nd = "LXTH" + m
    don = ad.tao("LX Don", {"goi": goi["name"], "so_tien": 99000, "trang_thai": "cho_tra", "noi_dung_ck": nd})
    khach = Phien()
    tx = lambda i, tien: {"id": int(m) * 10 + i, "gateway": "VCB", "transactionDate": "2026-11-08 10:00:00",
                          "accountNumber": "x", "transferType": "in", "transferAmount": tien,
                          "content": f"chuyen tien {nd.lower()}", "referenceCode": "FT"}
    ma, _ = khach.goi("POST", URL, tx(1, 99000), {"Authorization": "Apikey sai"})
    assert ma in (401, 403), f"sai khoá phải 401/403, được {ma}"
    ma, _ = khach.goi("POST", URL, tx(2, 50000), {"Authorization": f"Apikey {KHOA}"})
    assert ma == 200, f"webhook sai số tiền phải 200, được {ma}"
    assert ad.goi("GET", f"/api/resource/LX%20Don/{don['name']}")[1]["data"]["trang_thai"] == "cho_tra", "sai số tiền không được chuyển da_tra"
    for _ in range(2):
        ma, t = khach.goi("POST", URL, tx(3, 99000), {"Authorization": f"Apikey {KHOA}"})
        assert ma == 200, f"webhook đúng phải 200, được {ma}: {t}"
    d = ad.goi("GET", f"/api/resource/LX%20Don/{don['name']}")[1]["data"]
    assert d["trang_thai"] == "da_tra", f"đúng tiền phải da_tra, đang {d['trang_thai']}"
    assert str(d.get("tx_id")) == str(int(m) * 10 + 3)
    ma, ds = ad.ds("LX Don", [["tx_id", "=", str(int(m) * 10 + 3)]])
    assert len(ds) == 1, "tx_id chỉ gắn một đơn"
    ghi("don", don["name"], "da_tra, chống trùng ok")


chay(kiem)
