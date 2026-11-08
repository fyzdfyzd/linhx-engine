"""Kiểm thử chi tiết cho CTS Adapter (R1): cấu hình QR, từ chối số tiền <= 0,
đơn hết hạn -> can_hoan_tien, lưu trữ DocType DB, quyền PII, và đua đồng thời webhook.
"""
from __future__ import annotations

import copy
import json
import pathlib
import sqlite3
import sys
import threading
import types
from datetime import datetime, timedelta, timezone
from unittest import mock

import pytest

GOC_APP = pathlib.Path(__file__).resolve().parents[2]
if str(GOC_APP) not in sys.path:
    sys.path.insert(0, str(GOC_APP))

from linhx_core.cts_adapter import hop_dong


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

    def exists(self, doctype: str, filters: dict):
        self._begin_if_needed()
        bang = f"tab{doctype}"
        conds = []
        vals = []
        for k, v in filters.items():
            if isinstance(v, list) and len(v) == 2 and v[0] == "!=":
                conds.append(f"`{k}` != ?")
                vals.append(v[1])
            else:
                conds.append(f"`{k}` = ?")
                vals.append(v)
        where_sql = " AND ".join(conds)
        cur = self.conn.execute(
            f"SELECT name FROM `{bang}` WHERE {where_sql} LIMIT 1", tuple(vals)
        )
        row = cur.fetchone()
        return row["name"] if row else None


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

    class _FakeLogger:
        def warning(self, msg, *args):
            frappe_mod._warnings.append(msg % args if args else msg)

    frappe_mod.logger = lambda: _FakeLogger()

    def whitelist(allow_guest=False, methods=None):
        def _wrap(fn):
            return fn
        return _wrap

    def get_all(doctype, fields=None, ignore_permissions=False, limit_page_length=100):
        cols = ", ".join(fields or ["name"])
        return db.sql(f"SELECT {cols} FROM `tab{doctype}` LIMIT {int(limit_page_length)}", as_dict=True)

    def get_doc(data):
        return _FakeDoc(data, db)

    def get_request_header(ten):
        return getattr(frappe_mod.local, "auth_header", None) or frappe_mod._headers.get(ten)

    def throw(msg, exc=_ValidationError):
        raise exc(msg)

    frappe_mod.whitelist = whitelist
    frappe_mod.get_all = get_all
    frappe_mod.get_doc = get_doc
    frappe_mod.get_request_header = get_request_header
    frappe_mod.throw = throw

    model_mod = types.ModuleType("frappe.model")
    doc_mod = types.ModuleType("frappe.model.document")

    class Document:
        def is_new(self):
            return True

    doc_mod.Document = Document
    model_mod.document = doc_mod
    return frappe_mod, model_mod, doc_mod


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


def test_thieu_cau_hinh_qr_bao_loi_va_khong_dung_gia_tri_gia():
    kho = {"don": [], "tx": []}
    # doc_cau_hinh_qr không truyền cau_hinh -> trả (None, thong_bao_loi)
    thong_tin_rong, loi_rong = hop_dong.doc_cau_hinh_qr()
    assert thong_tin_rong is None and isinstance(loi_rong, str) and loi_rong

    # Truyền cau_hinh rỗng -> báo lỗi 500
    ma0, than0 = hop_dong.tao_don(
        copy.deepcopy(PAYLOAD_HOP_LE),
        hop_dong.DANH_MUC_MAC_DINH,
        kho,
        cau_hinh={},
    )
    assert ma0 == 500 and "detail" in than0
    assert kho["don"] == []

    # Truyền thiếu từng trường cấu hình -> báo lỗi 500 và nêu tên trường thiếu
    for thieu_cfg, ten_thieu in [
        ({"cts_so_tk": "0123456789", "cts_host": "https://pay.chiemtinh.vn"}, "ngan_hang"),
        ({"cts_ngan_hang": "VCB", "cts_host": "https://pay.chiemtinh.vn"}, "so_tk"),
        ({"cts_ngan_hang": "VCB", "cts_so_tk": "0123456789"}, "host"),
    ]:
        ma, than = hop_dong.tao_don(
            copy.deepcopy(PAYLOAD_HOP_LE),
            hop_dong.DANH_MUC_MAC_DINH,
            kho,
            cau_hinh=thieu_cfg,
        )
        assert ma == 500
        assert ten_thieu in than["detail"]
        assert kho["don"] == []

    # Truyền đủ cấu hình -> 200 và dùng đúng ngân hàng, số tài khoản, host
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
    assert "acc=0123456789" in than_ok["qr"]["url"]
    assert "bank=VCB" in than_ok["qr"]["url"]

    # Gọi thuần Python 3 tham số (hợp đồng hộp đen) -> không dùng số tài khoản hay host giả
    kho_thuan = {"don": [], "tx": []}
    ma_thuan, than_thuan = hop_dong.tao_don(
        copy.deepcopy(PAYLOAD_HOP_LE),
        hop_dong.DANH_MUC_MAC_DINH,
        kho_thuan,
    )
    assert ma_thuan == 200
    assert than_thuan["qr"]["ngan_hang"] == ""
    assert than_thuan["qr"]["so_tk"] == ""
    assert than_thuan["qr"]["url"] == ""


def test_webhook_tu_choi_so_tien_am_hoac_khong():
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
        assert ma == 422, f"transferAmount={gia_tri_sai!r} phải bị từ chối 422"
        assert "transferAmount" in than.get("detail", "")
        assert kho == kho_goc, "số tiền không hợp lệ không được thay đổi da_nhan hay tx"


def test_don_qua_expires_at_tu_chuyen_het_han_va_can_hoan_tien():
    kho = {"don": [], "tx": []}
    ma, than = hop_dong.tao_don(
        copy.deepcopy(PAYLOAD_HOP_LE),
        hop_dong.DANH_MUC_MAC_DINH,
        kho,
        cau_hinh=CAU_HINH_QR_HOP_LE,
    )
    assert ma == 200
    don = kho["don"][0]
    # Đặt expires_at về quá khứ 10 phút trước
    qua_khu = (datetime.now(timezone.utc) - timedelta(minutes=10)).replace(microsecond=0).isoformat()
    don["expires_at"] = qua_khu
    assert don["trang_thai"] == "cho_thanh_toan"

    wh = {
        "id": 880001,
        "content": f"TT {don['noi_dung_ck']}",
        "transferType": "in",
        "transferAmount": 199000,
    }
    ma_wh, than_wh = hop_dong.nhan_webhook(wh, kho, "Apikey k1", "k1")
    assert ma_wh == 200
    assert than_wh["status"] == "matched"
    assert than_wh["trang_thai"] == "can_hoan_tien"
    assert than_wh["chenh_lech"] == 199000
    assert don["trang_thai"] == "can_hoan_tien"
    assert don["da_nhan"] == 199000


def test_doctype_pii_permissions_va_unique_tx_id():
    thu_muc_dt = pathlib.Path(__file__).resolve().parent / "doctype"
    don_json = json.loads((thu_muc_dt / "lx_don_cts" / "lx_don_cts.json").read_text(encoding="utf-8"))
    gd_json = json.loads((thu_muc_dt / "lx_giao_dich_cts" / "lx_giao_dich_cts.json").read_text(encoding="utf-8"))

    truong_don = {f["fieldname"]: f for f in don_json["fields"]}
    assert truong_don["order_id"].get("unique") == 1
    assert truong_don["noi_dung_ck"].get("unique") == 1
    assert truong_don["email"].get("permlevel") == 1, "email (PII) phải đặt ở permlevel 1"
    assert truong_don["ho_so"].get("permlevel") == 1, "ho_so (PII) phải đặt ở permlevel 1"

    quyen_don = don_json.get("permissions", [])
    roles_perm1 = {p["role"] for p in quyen_don if p.get("permlevel") == 1 and p.get("read")}
    assert roles_perm1 == {"System Manager"}, "chỉ System Manager được đọc PII ở permlevel 1"

    truong_gd = {f["fieldname"]: f for f in gd_json["fields"]}
    assert truong_gd["tx_id"].get("unique") == 1, "tx_id phải có ràng buộc unique"


def test_api_luu_db_va_chong_dua_webhook_dong_thoi():
    db = _FakeSQLiteDB()
    conf = {
        **CAU_HINH_QR_HOP_LE,
        "cts_sepay_khoa": "bi-mat-test",
    }
    frappe_mod, model_mod, doc_mod = _tao_frappe_gia(db, conf)

    with mock.patch.dict(
        sys.modules,
        {
            "frappe": frappe_mod,
            "frappe.model": model_mod,
            "frappe.model.document": doc_mod,
        },
    ):
        sys.modules.pop("linhx_core.cts_adapter.api", None)
        from linhx_core.cts_adapter import api
        from linhx_core.cts_adapter.doctype.lx_don_cts import lx_don_cts

        # Kiểm quyền PII trên controller LX Don CTS
        frappe_mod.get_roles = lambda u: ["LX Nhan Vien"] if u == "nv@test.local" else ["System Manager"]
        assert lx_don_cts.co_quyen_don_cts(None, "read", "Guest") is False
        assert lx_don_cts.co_quyen_don_cts(None, "read", "nv@test.local") is False
        assert lx_don_cts.dieu_kien_truy_van_don_cts("Guest") == "1=0"
        assert lx_don_cts.dieu_kien_truy_van_don_cts("nv@test.local") == "1=0"
        assert lx_don_cts.co_quyen_don_cts(None, "read", "admin@test.local") is True

        # Endpoint checkout khi thiếu cấu hình QR trên site -> trả 500 và không lưu DB
        frappe_mod.conf = {"cts_sepay_khoa": "bi-mat-test"}
        frappe_mod.local.response = {}
        than_thieu = api.checkout(**copy.deepcopy(PAYLOAD_HOP_LE))
        assert frappe_mod.local.response.get("http_status_code") == 500
        assert "detail" in than_thieu

        # Tạo đơn qua endpoint checkout khi đủ cấu hình -> phải lưu vào bảng tabLX Don CTS
        frappe_mod.conf = conf
        frappe_mod.local.response = {}
        than_don = api.checkout(**copy.deepcopy(PAYLOAD_HOP_LE))
        assert frappe_mod.local.response.get("http_status_code") == 200
        ck = than_don["qr"]["noi_dung_ck"]
        oid = than_don["order_id"]

        rows_db = db.sql("SELECT * FROM `tabLX Don CTS` WHERE order_id = %s", (oid,), as_dict=True)
        db.commit()
        assert len(rows_db) == 1
        assert rows_db[0]["noi_dung_ck"] == ck
        assert rows_db[0]["email"] == "khach.test@vidu.vn"

        # 1) Hai luồng gửi CÙNG tx_id đồng thời -> chỉ cộng tiền 1 lần, luồng kia nhận idempotent
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
                transferAmount=100000,
            )
            ket_qua_trung.append((frappe_mod.local.response.get("http_status_code"), kq))

        t1 = threading.Thread(target=_gui_wh_cung_tx)
        t2 = threading.Thread(target=_gui_wh_cung_tx)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert len(ket_qua_trung) == 2
        assert all(ma == 200 for ma, _ in ket_qua_trung)
        so_matched = sum(1 for _, b in ket_qua_trung if b.get("status") == "matched")
        so_idem = sum(1 for _, b in ket_qua_trung if b.get("idempotent") is True)
        assert so_matched == 1 and so_idem == 1

        row_sau_1 = db.sql("SELECT da_nhan, trang_thai FROM `tabLX Don CTS` WHERE order_id = %s", (oid,), as_dict=True)[0]
        db.commit()
        assert row_sau_1["da_nhan"] == 100000
        assert row_sau_1["trang_thai"] == "thieu_tien"

        # 2) Hai luồng gửi KHÁC tx_id đồng thời (50000 và 49000) -> không mất cập nhật, đủ 199000
        ket_qua_khac = []
        rao_2 = threading.Barrier(2)

        def _gui_wh_khac_tx(tx_id_so: int, so_tien: int):
            frappe_mod.local.response = {}
            frappe_mod.local.auth_header = "Apikey bi-mat-test"
            rao_2.wait()
            kq = api.sepay_webhook(
                id=tx_id_so,
                content=f"bu tien {ck}",
                transferType="in",
                transferAmount=so_tien,
            )
            ket_qua_khac.append((frappe_mod.local.response.get("http_status_code"), kq))

        t3 = threading.Thread(target=_gui_wh_khac_tx, args=(555002, 50000))
        t4 = threading.Thread(target=_gui_wh_khac_tx, args=(555003, 49000))
        t3.start()
        t4.start()
        t3.join()
        t4.join()

        assert len(ket_qua_khac) == 2
        assert all(ma == 200 and b.get("status") == "matched" for ma, b in ket_qua_khac)
        row_sau_2 = db.sql("SELECT da_nhan, trang_thai FROM `tabLX Don CTS` WHERE order_id = %s", (oid,), as_dict=True)[0]
        so_gd = db.sql("SELECT COUNT(*) AS c FROM `tabLX Giao Dich CTS` WHERE order_id = %s", (oid,), as_dict=True)[0]["c"]
        db.commit()
        assert row_sau_2["da_nhan"] == 199000
        assert row_sau_2["trang_thai"] == "da_thanh_toan"
        assert so_gd == 3

        # 3) Giả lập trực tiếp va chạm DuplicateEntryError trên doc_tx.insert() -> rollback và trả idempotent
        goc_get_doc = frappe_mod.get_doc

        def _get_doc_nem_trung(data):
            doc = goc_get_doc(data)
            if data.get("doctype") == "LX Giao Dich CTS":
                def _insert_trung(ignore_permissions=False):
                    raise _DuplicateEntryError("Duplicate entry for key tx_id")
                doc.insert = _insert_trung
            return doc

        frappe_mod.get_doc = _get_doc_nem_trung
        try:
            frappe_mod.local.response = {}
            frappe_mod.local.auth_header = "Apikey bi-mat-test"
            kq_dup = api.sepay_webhook(
                id=555099,
                content=f"trung {ck}",
                transferType="in",
                transferAmount=50000,
            )
            assert frappe_mod.local.response.get("http_status_code") == 200
            assert kq_dup == {
                "ok": True,
                "idempotent": True,
                "tx_id": "555099",
                "order_id": oid,
            }
        finally:
            frappe_mod.get_doc = goc_get_doc

        # 4) Kiểm ghi log khi request.get_json / get_data lỗi
        class _BadReq:
            def get_json(self, silent=True):
                raise ValueError("json hỏng")

            def get_data(self, as_text=True):
                return "{bad json"

        frappe_mod.request = _BadReq()
        frappe_mod._warnings.clear()
        api._doc_payload({"sku": "X"})
        assert len(frappe_mod._warnings) >= 2
