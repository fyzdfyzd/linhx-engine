"""B2: LX Don + mã VietQR theo đơn; chuyển từ PROTO 03 m03. Đơn mới trả ảnh QR đúng số tiền và nội dung có mã đơn.

Hợp đồng (HOP-DONG.md):
- DocType JSON module pay: LX Don (goi Link LX Goi, nguoi Link LX Nguoi, so_tien Currency, trang_thai Select có
  cho_tra, da_tra, huy; noi_dung_ck Data unique; tx_id Data)
- linhx_core/pay/vietqr.py thuần Python:
    noi_dung_ck(ma_don) -> str   chữ hoa + số, không dấu cách, 6..25 ký tự, bắt đầu "LX", chứa ma_don đã bỏ ký tự lạ;
                                 hai mã đơn khác nhau cho hai nội dung khác nhau
    qr_url(so_tien: int, noi_dung: str, ngan_hang: dict) -> str
        ngan_hang {"bin", "so_tk", "ten_tk"} lấy từ cấu hình site (không viết số tài khoản trong code);
        URL ảnh https://img.vietqr.io/image/<bin>-<so_tk>-<mẫu>.png có amount=<so_tien>&addInfo=<noi_dung>&accountName=...
        so_tien <= 0 hoặc không phải số nguyên -> ValueError
    tao_don(goi: dict, nguoi: str, ngan_hang: dict, ma_don: str) -> dict
        số tiền = goi["gia"] nếu có, không thì goi["gia_san"]; dưới gia_san -> ValueError (dùng quyen_dung.gia_hop_le của B1)
        trả {"ma", "goi", "nguoi", "so_tien", "trang_thai": "cho_tra", "noi_dung_ck", "qr_url"}
- vietqr.py ghi chuyển từ file nào trong nguon/03-opc-os/ (đường dẫn có thật)
"""
import re
from urllib.parse import parse_qs, unquote, urlparse

import pytest

from _chung import ma, CORE, ghi_nguon_proto, khong_import_frappe_dau_file, nap_module, ten_truong, tim_doctype

NH = {"bin": "970436", "so_tk": "0011000999888", "ten_tk": "CONG TY THU"}
GOI = {"ma": "BC-AI", "ten": "Báo cáo AI nói gì", "gia": 99000, "gia_san": 5000}


def _vq():
    return nap_module("linhx_core.pay.vietqr", CORE)


def test_doctype():
    _, d = tim_doctype("LX Don")
    assert d and str(d.get("module", "")).lower() == "pay"
    tr = ten_truong(d)
    assert tr.get("goi", {}).get("options") == "LX Goi"
    assert tr.get("so_tien", {}).get("fieldtype") == "Currency"
    assert {"cho_tra", "da_tra", "huy"} <= set(str(tr.get("trang_thai", {}).get("options", "")).split("\n"))
    assert tr.get("noi_dung_ck", {}).get("unique") == 1, "noi_dung_ck phải unique để đối soát"
    assert "tx_id" in tr


def test_noi_dung_ck():
    vq = _vq()
    a, b = vq.noi_dung_ck("DON-2026-00017"), vq.noi_dung_ck("DON-2026-00018")
    for x in (a, b):
        assert re.fullmatch(r"LX[A-Z0-9]{4,23}", x), x
        assert "202600017" in a or "00017" in a
    assert a != b


def test_qr_dung_so_tien_va_noi_dung():
    vq = _vq()
    nd = vq.noi_dung_ck("DON-7")
    u = urlparse(vq.qr_url(99000, nd, NH))
    assert u.scheme == "https" and u.netloc == "img.vietqr.io"
    assert u.path.startswith("/image/970436-0011000999888-") and u.path.endswith(".png")
    q = {k: unquote(v[0]) for k, v in parse_qs(u.query).items()}
    assert q.get("amount") == "99000" and q.get("addInfo") == nd
    for sai in (0, -5, 10.5):
        with pytest.raises(ValueError):
            vq.qr_url(sai, nd, NH)


def test_tao_don():
    vq = _vq()
    d = vq.tao_don(GOI, "N1", NH, "DON-9")
    assert d["trang_thai"] == "cho_tra" and d["so_tien"] == 99000 and d["ma"] == "DON-9"
    assert d["noi_dung_ck"] == vq.noi_dung_ck("DON-9")
    q = parse_qs(urlparse(d["qr_url"]).query)
    assert q["amount"] == ["99000"] and q["addInfo"] == [d["noi_dung_ck"]]
    assert vq.tao_don({"ma": "X", "gia_san": 5000}, "N1", NH, "DON-10")["so_tien"] == 5000
    with pytest.raises(ValueError):
        vq.tao_don({"ma": "X", "gia": 1000, "gia_san": 5000}, "N1", NH, "DON-11")


def test_khong_viet_so_tai_khoan_va_ghi_nguon():
    p = ma("pay/vietqr.py")
    khong_import_frappe_dau_file(p)
    assert not re.search(r"['\"]\d{8,}['\"]", p.read_text(encoding="utf-8")), "không viết số tài khoản trong code"
    ghi_nguon_proto(p)
