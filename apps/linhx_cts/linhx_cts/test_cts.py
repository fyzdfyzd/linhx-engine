"""Kiểm thử đơn vị cho app `linhx_cts` (P3 / R1 / R2): nạp thuần Python, cấu hình QR,
từ chối số tiền <= 0, hết hạn -> can_hoan_tien, đua đồng thời webhook DB, và chế độ bóng.
"""
from __future__ import annotations

import copy
import importlib
import pathlib
import sqlite3
import sys
import threading
import types
from datetime import datetime, timedelta, timezone
from unittest import mock

GOC_APP = pathlib.Path(__file__).resolve().parents[1]
if str(GOC_APP) not in sys.path:
    sys.path.insert(0, str(GOC_APP))

from linhx_cts import bong, hop_dong


class _DuplicateEntryError(Exception):
    pass


class _PermissionError(Exception):
    pass


class _ValidationError(Exception):
    pass


class _FakeSQLiteDB:
    """Giả lập Frappe DB trên SQLite thật với khoá giao dịch và ràng buộc UNIQUE."""

    def __init__(self):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.lock = threading.RLock()
        self._tls = threading.local()
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE `tabLX Don CTS` (
                    name TEXT PRIMARY KEY,
                    order_id TEXT NOT NULL UNIQUE,
                    noi_dung_ck TEXT NOT NULL UNIQUE,
                    sku TEXT NOT NULL,
                    ten_san_pham TEXT,
                    kenh TEXT NOT NULL,
                    gia_goc INTEGER NOT NULL,
                    tong INTEGER NOT NULL,
                    da_nhan INTEGER NOT NULL DEFAULT 0,
                    trang_thai TEXT NOT NULL,
                    email TEXT,
                    ho_so TEXT,
                    dong_y_dieu_khoan INTEGER DEFAULT 1,
                    dong_y_nhan_tin INTEGER DEFAULT 0,
                    created_at TEXT,
                    expires_at TEXT
                )
                """
            )
            self.conn.execute(
                """
                CREATE TABLE `tabLX Giao Dich CTS` (
                    name TEXT PRIMARY KEY,
                    tx_id TEXT NOT NULL UNIQUE,
                    order_id TEXT,
                    noi_dung_ck TEXT,
                    loai_gd TEXT,
                    so_tien INTEGER,
                    trang_thai_ket_qua TEXT,
                    noi_dung_goc TEXT
                )
                """
            )

    def _begin_if_needed(self):
        if not getattr(self._tls, "in_tx", False):
            self.lock.acquire()
            self._tls.in_tx = True

    def sql(self, query: str, values=(), as_dict: bool = False):
        self._begin_if_needed()
        q_clean = query.replace("FOR UPDATE", "").replace("%s", "?")
        cur = self.conn.execute(q_clean, tuple(values))
        if q_clean.strip().upper().startswith("SELECT"):
            rows = cur.fetchall()
            if as_dict:
                return [dict(r) for r in rows]
            return [tuple(r) for r in rows]
        return []

    def commit(self):
        if getattr(self._tls, "in_tx", False):
            try:
                self.conn.commit()
            finally:
                self._tls.in_tx = False
                self.lock.release()

    def rollback(self):
        if getattr(self._tls, "in_tx", False):
            try:
                self.conn.rollback()
            finally:
                self._tls.in_tx = False
                self.lock.release()


class _FakeDoc:
    def __init__(self, data: dict, db: _FakeSQLiteDB):
        self._db = db
        for k, v in data.items():
            setattr(self, k, v)
        if self.doctype == "LX Don CTS":
            self.name = self.order_id
        elif self.doctype == "LX Giao Dich CTS":
            self.name = self.tx_id

    def insert(self, ignore_permissions: bool = False):
        self._db._begin_if_needed()
        try:
            if self.doctype == "LX Don CTS":
                self._db.conn.execute(
                    """
                    INSERT INTO `tabLX Don CTS`
                    (name, order_id, noi_dung_ck, sku, ten_san_pham, kenh, gia_goc, tong,
                     da_nhan, trang_thai, email, ho_so, dong_y_dieu_khoan, dong_y_nhan_tin,
                     created_at, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        self.name,
                        self.order_id,
                        self.noi_dung_ck,
                        self.sku,
                        self.ten_san_pham,
                        self.kenh,
                        self.gia_goc,
                        self.tong,
                        self.da_nhan,
                        self.trang_thai,
                        self.email,
                        self.ho_so,
                        self.dong_y_dieu_khoan,
                        self.dong_y_nhan_tin,
                        self.created_at,
                        self.expires_at,
                    ),
                )
            elif self.doctype == "LX Giao Dich CTS":
                self._db.conn.execute(
                    """
                    INSERT INTO `tabLX Giao Dich CTS`
                    (name, tx_id, order_id, noi_dung_ck, loai_gd, so_tien, trang_thai_ket_qua, noi_dung_goc)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        self.name,
                        self.tx_id,
                        self.order_id,
                        self.noi_dung_ck,
                        self.loai_gd,
                        self.so_tien,
                        self.trang_thai_ket_qua,
                        self.noi_dung_goc,
                    ),
                )
        except sqlite3.IntegrityError as exc:
            raise _DuplicateEntryError(str(exc)) from exc
        return self


def _tao_frappe_gia(db: _FakeSQLiteDB, conf: dict):
    frappe_mod = types.ModuleType("frappe")
    frappe_mod.db = db
    frappe_mod.conf = conf
    frappe_mod.DuplicateEntryError = _DuplicateEntryError
    frappe_mod.PermissionError = _PermissionError
    frappe_mod.ValidationError = _ValidationError
    frappe_mod.local = threading.local()
    frappe_mod.local.response = {}
    frappe_mod.session = types.SimpleNamespace(user="Guest")
    frappe_mod.request = None
    frappe_mod._headers = {}
    frappe_mod._warnings = []
    frappe_mod.whitelisted = set()
    frappe_mod.guest_methods = set()

    class _FakeLogger:
        def warning(self, msg, *args):
            frappe_mod._warnings.append(msg % args if args else msg)

    frappe_mod.logger = lambda: _FakeLogger()

    def whitelist(allow_guest=False, methods=None):
        def _wrap(fn):
            frappe_mod.whitelisted.add(fn)
            if allow_guest:
                frappe_mod.guest_methods.add(fn)
            return fn
        return _wrap

    def get_doc(data):
        return _FakeDoc(data, db)

    def get_request_header(ten):
        return getattr(frappe_mod.local, "auth_header", None) or frappe_mod._headers.get(ten)

    frappe_mod.whitelist = whitelist
    frappe_mod.get_doc = get_doc
    frappe_mod.get_request_header = get_request_header
    return frappe_mod


PAYLOAD_HOP_LE = {
    "sku": "SKU-CT-NATAL-FULL-STD",
    "kenh": "web",
    "ho_so": {
        "ho_ten": "Nguyễn Văn A",
        "ngay_sinh": "1992-05-15",
        "gio_sinh": "08:30",
        "noi_sinh": "Hà Nội",
    },
    "email": "khach.test@vidu.vn",
    "dong_y_dieu_khoan": True,
}

CAU_HINH_QR_HOP_LE = {
    "cts_ngan_hang": "VCB",
    "cts_so_tk": "0123456789",
    "cts_host": "https://pay.chiemtinh.vn",
}


def test_nap_thuan_python_khong_can_frappe():
    with mock.patch.dict(sys.modules, {"frappe": None}):
        sys.modules.pop("linhx_cts.api", None)
        api_mod = importlib.import_module("linhx_cts.api")
        assert callable(api_mod.checkout)
        assert callable(api_mod.sepay_webhook)


def test_thieu_cau_hinh_qr_va_gioi_han_du_lieu_dau_vao():
    kho = {"don": [], "tx": []}
    thong_tin_rong, loi_rong = hop_dong.doc_cau_hinh_qr()
    assert thong_tin_rong is None and isinstance(loi_rong, str) and loi_rong

    ma0, than0 = hop_dong.tao_don(
        copy.deepcopy(PAYLOAD_HOP_LE),
        hop_dong.DANH_MUC_MAC_DINH,
        kho,
        cau_hinh={},
    )
    assert ma0 == 500 and "detail" in than0
    assert kho["don"] == []

    # Từ chối email quá dài hoặc ho_so quá lớn
    p_email_dai = copy.deepcopy(PAYLOAD_HOP_LE)
    p_email_dai["email"] = ("a" * 140) + "@vidu.vn"
    ma_em, than_em = hop_dong.tao_don(p_email_dai, hop_dong.DANH_MUC_MAC_DINH, kho)
    assert ma_em == 422 and "email" in than_em["detail"]

    p_ho_so_lon = copy.deepcopy(PAYLOAD_HOP_LE)
    p_ho_so_lon["ho_so"]["ghi_chu"] = "x" * 9000
    ma_hs, than_hs = hop_dong.tao_don(p_ho_so_lon, hop_dong.DANH_MUC_MAC_DINH, kho)
    assert ma_hs == 422 and "ho_so" in than_hs["detail"]

    ma_ok, than_ok = hop_dong.tao_don(
        copy.deepcopy(PAYLOAD_HOP_LE),
        hop_dong.DANH_MUC_MAC_DINH,
        kho,
        cau_hinh=CAU_HINH_QR_HOP_LE,
    )
    assert ma_ok == 200
    assert than_ok["qr"]["ngan_hang"] == "VCB"
    assert than_ok["qr"]["so_tk"] == "0123456789"
    assert than_ok["qr"]["url"].startswith("https://pay.chiemtinh.vn/v1/pay/vietqr.png?")


def test_webhook_tu_choi_so_tien_am_va_het_han_chuyen_can_hoan_tien():
    kho_goc = {
        "don": [
            {
                "order_id": "ord_am01",
                "noi_dung_ck": "CTS0A1B2C3D4E",
                "tong": 199000,
                "da_nhan": 100000,
                "trang_thai": "thieu_tien",
            }
        ],
        "tx": [],
    }
    for gia_tri_sai in (-199000, -1, 0, None, False, True, 12.5, "abc", ""):
        kho = copy.deepcopy(kho_goc)
        wh = {
            "id": 990001,
            "content": "CTS0A1B2C3D4E",
            "transferType": "in",
            "transferAmount": gia_tri_sai,
        }
        ma, than = hop_dong.nhan_webhook(wh, kho, "Apikey k1", "k1")
        assert ma == 422
        assert "transferAmount" in than.get("detail", "")
        assert kho == kho_goc

    kho2 = {"don": [], "tx": []}
    ma, _ = hop_dong.tao_don(
        copy.deepcopy(PAYLOAD_HOP_LE),
        hop_dong.DANH_MUC_MAC_DINH,
        kho2,
        cau_hinh=CAU_HINH_QR_HOP_LE,
    )
    assert ma == 200
    don = kho2["don"][0]
    don["expires_at"] = (datetime.now(timezone.utc) - timedelta(minutes=10)).replace(microsecond=0).isoformat()
    ma_wh, than_wh = hop_dong.nhan_webhook(
        {"id": 880001, "content": f"TT {don['noi_dung_ck']}", "transferType": "in", "transferAmount": 199000},
        kho2,
        "Apikey k1",
        "k1",
    )
    assert ma_wh == 200 and than_wh["trang_thai"] == "can_hoan_tien" and than_wh["chenh_lech"] == 199000


def test_api_luu_db_thu_lai_trung_ma_va_chong_dua_webhook():
    db = _FakeSQLiteDB()
    conf = {
        **CAU_HINH_QR_HOP_LE,
        "cts_sepay_khoa": "bi-mat-test",
    }
    frappe_mod = _tao_frappe_gia(db, conf)

    with mock.patch.dict(sys.modules, {"frappe": frappe_mod}):
        sys.modules.pop("linhx_cts.api", None)
        import linhx_cts
        if hasattr(linhx_cts, "api"):
            delattr(linhx_cts, "api")
        from linhx_cts import api

        try:
            assert api.checkout in frappe_mod.guest_methods
            assert api.sepay_webhook in frappe_mod.guest_methods

            frappe_mod.local.response = {}
            than_don = api.checkout(**copy.deepcopy(PAYLOAD_HOP_LE))
            assert frappe_mod.local.response.get("http_status_code") == 200
            ck = than_don["qr"]["noi_dung_ck"]
            oid = than_don["order_id"]

            # Thử lại khi lần insert đầu báo trùng ("đã tồn tại")
            so_lan = {"n": 0}
            goc_get_doc = frappe_mod.get_doc

            def _get_doc_trung_lan_dau(data):
                doc = goc_get_doc(data)
                if data.get("doctype") == "LX Don CTS" and so_lan["n"] == 0:
                    so_lan["n"] += 1
                    def _insert_loi(ignore_permissions=False):
                        raise _ValidationError("Mã đơn CTS đã tồn tại")
                    doc.insert = _insert_loi
                return doc

            frappe_mod.get_doc = _get_doc_trung_lan_dau
            try:
                frappe_mod.local.response = {}
                than_don2 = api.checkout(**copy.deepcopy(PAYLOAD_HOP_LE))
                assert frappe_mod.local.response.get("http_status_code") == 200
                assert than_don2["order_id"] != oid
            finally:
                frappe_mod.get_doc = goc_get_doc

            # Đua đồng thời cùng tx_id
            ket_qua_trung = []
            rao_1 = threading.Barrier(2)

            def _gui_wh_cung_tx():
                frappe_mod.local.response = {}
                frappe_mod.local.auth_header = "Apikey bi-mat-test"
                rao_1.wait()
                kq = api.sepay_webhook(
                    id=555001,
                    content=f"chuyen khoan {ck}",
                    transferType="in",
                    transferAmount=199000,
                )
                ket_qua_trung.append((frappe_mod.local.response.get("http_status_code"), kq))

            t1 = threading.Thread(target=_gui_wh_cung_tx)
            t2 = threading.Thread(target=_gui_wh_cung_tx)
            t1.start()
            t2.start()
            t1.join()
            t2.join()

            assert sum(1 for _, b in ket_qua_trung if b.get("status") == "matched") == 1
            assert sum(1 for _, b in ket_qua_trung if b.get("idempotent") is True) == 1
            row = db.sql("SELECT da_nhan, trang_thai FROM `tabLX Don CTS` WHERE order_id = %s", (oid,), as_dict=True)[0]
            db.commit()
            assert row["da_nhan"] == 199000 and row["trang_thai"] == "da_thanh_toan"
        finally:
            sys.modules.pop("linhx_cts.api", None)
            if hasattr(linhx_cts, "api"):
                delattr(linhx_cts, "api")


def test_che_do_bong_khong_luu_pii_va_luon_khong_giao():
    kho = {"don": [], "tx": []}
    don_mau = {
        "order_id": "ord_bong_01",
        "noi_dung_ck": "cts1234567890",
        "tong": 199000,
        "da_nhan": 99999,
        "trang_thai": "cho_thanh_toan",
        "email": "khach@vidu.vn",
        "ho_so": {"ho_ten": "Khách"},
    }
    assert bong.nhan_don_bong(don_mau, {"bat_bong": False}, kho) is None
    d_bong = bong.nhan_don_bong(don_mau, {"bat_bong": True}, kho)
    assert d_bong is not None
    assert "email" not in d_bong and "ho_so" not in d_bong
    kq = bong.nhan_bong(
        {"id": 888001, "content": "TT CTS1234567890", "transferType": "in", "transferAmount": 199000},
        {"bat_bong": True},
        kho,
    )
    assert kq == {
        "tx_id": "888001",
        "noi_dung_ck": "CTS1234567890",
        "trang_thai": "da_thanh_toan",
        "da_nhan": 199000,
        "giao": False,
    }
