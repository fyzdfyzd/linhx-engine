"""Kiểm thử đơn vị và bảo mật (K4) cho `linhx_core.id.otp` và DocType `LX OTP` (I3)."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
import sqlite3
import sys
import threading
import types

import pytest

from linhx_core.id import otp


class _FakeFrappeSQLiteDB:
    """Giả lập `frappe.db` trên bảng SQLite `tabLX OTP` để kiểm thử giao dịch SQL thật."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(":memory:", check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._last_rowcount: int = 0
        self.so_lan_commit = 0
        self.so_lan_rollback = 0
        self.ep_rowcount_none = False
        self._conn.execute(
            """
            CREATE TABLE `tabLX OTP` (
                `name` TEXT PRIMARY KEY,
                `khoa_kenh` TEXT UNIQUE NOT NULL,
                `email` TEXT NOT NULL,
                `muc_dich` TEXT NOT NULL,
                `ma_bam` TEXT NOT NULL,
                `tao_luc` TEXT NOT NULL,
                `cap_nhat_luc` TEXT,
                `het_han_luc` TEXT NOT NULL,
                `so_lan_sai` INTEGER NOT NULL DEFAULT 0,
                `da_dung` INTEGER NOT NULL DEFAULT 0,
                `khoa_den` TEXT,
                `lich_su_phat_json` TEXT,
                `ip_cuoi` TEXT
            )
            """
        )
        self._conn.commit()

    def sql(self, query: str, values: tuple | list = (), as_dict: bool = False):
        with self._lock:
            q_strip = query.strip()
            if q_strip.upper().startswith("SELECT ROW_COUNT()"):
                if self.ep_rowcount_none:
                    return None
                if as_dict:
                    return [{"so_dong": self._last_rowcount}]
                return [(self._last_rowcount,)]

            q_sqlite = q_strip
            if q_sqlite.upper().endswith("FOR UPDATE"):
                q_sqlite = q_sqlite[: -len("FOR UPDATE")].rstrip()
            q_sqlite = q_sqlite.replace("%s", "?")

            cur = self._conn.cursor()
            cur.execute(q_sqlite, tuple(values or ()))
            if q_sqlite.upper().startswith("SELECT"):
                rows = cur.fetchall()
                if as_dict:
                    return [dict(r) for r in rows]
                return [tuple(r) for r in rows]

            self._last_rowcount = cur.rowcount if cur.rowcount is not None and cur.rowcount >= 0 else 0
            return []

    def commit(self) -> None:
        with self._lock:
            self._conn.commit()
            self.so_lan_commit += 1

    def rollback(self) -> None:
        with self._lock:
            self._conn.rollback()
            self.so_lan_rollback += 1


def _lap_moi_truong_frappe_db(
    monkeypatch,
    *,
    request_ip: str = "198.51.100.25",
    headers: dict | None = None,
    trusted_proxies: list[str] | None = None,
    co_request: bool = True,
) -> tuple[types.ModuleType, _FakeFrappeSQLiteDB]:
    db = _FakeFrappeSQLiteDB()
    fake_frappe = types.ModuleType("frappe")
    req_obj = types.SimpleNamespace(headers=headers or {}) if co_request else None
    fake_frappe.local = types.SimpleNamespace(
        request_ip=request_ip,
        request=req_obj,
        form_dict={},
    )
    fake_frappe.conf = {
        "otp_khoa_bi_mat": "khoa-bi-mat-otp-rieng-cho-kiem-thu-32b",
        "trusted_proxies": trusted_proxies or [],
    }
    fake_frappe.db = db
    monkeypatch.setitem(sys.modules, "frappe", fake_frappe)
    otp._CHI_MUC_PHAT_IP.clear()
    otp._CHI_MUC_SAI_IP.clear()
    return fake_frappe, db


def test_sinh_ma_ngau_nhien_6_chu_so_va_tach_biet_muc_dich():
    kho: dict = {}
    da_gui: list[tuple[str, str, str]] = []

    kq_dn = otp.phat_ma(
        kho,
        "  Khach.Hang@VD.vn ",
        "dang_nhap",
        "2026-11-09 10:00:00",
        gui_mail=lambda em, ma, md: da_gui.append((em, ma, md)),
    )
    assert kq_dn == {
        "email": "khach.hang@vd.vn",
        "muc_dich": "dang_nhap",
        "het_han_luc": "2026-11-09 10:10:00",
    }
    assert len(da_gui) == 1
    em_gui, ma_sinh, md_gui = da_gui[0]
    assert em_gui == "khach.hang@vd.vn"
    assert md_gui == "dang_nhap"
    assert len(ma_sinh) == 6 and ma_sinh.isdigit()
    assert ma_sinh not in json.dumps(kho)

    # Mã của mục đích "dang_nhap" không dùng được cho mục đích "marketing"
    kq_sai_md = otp.xac_minh(kho, "khach.hang@vd.vn", "marketing", ma_sinh, "2026-11-09 10:01:00")
    assert kq_sai_md == {"ok": False, "ly_do": "sai_ma"}

    # Xác minh đúng mục đích "dang_nhap" (email khác hoa thường) -> thành công
    kq_dung = otp.xac_minh(kho, "KHACH.HANG@VD.VN", "dang_nhap", ma_sinh, "2026-11-09 10:01:00")
    assert kq_dung == {"ok": True, "ly_do": None}


def test_bam_ma_hmac_khoa_rieng_va_chan_production_thieu_khoa(monkeypatch):
    b1 = otp.bam_ma("Lan@VD.vn", "dang_nhap", "123456")
    b2 = otp.bam_ma("lan@vd.vn", "marketing", "123456")
    assert b1 != b2
    assert len(b1) == 64
    assert "123456" not in b1
    assert otp.bam_ma("LAN@VD.VN", "dang_nhap", "482910") == otp.bam_ma("lan@vd.vn", "dang_nhap", "482910")

    with pytest.raises(ValueError):
        otp.bam_ma("u|x@vd.vn", "dang_nhap", "123456")
    with pytest.raises(ValueError):
        otp.bam_ma("u@vd.vn", "muc_dich_ngoai_danh_sach", "123456")

    # Không cho phép dùng chung encryption_key của Frappe khi thiếu otp_khoa_bi_mat
    fake_frappe = types.ModuleType("frappe")
    fake_frappe.conf = {"encryption_key": "khoa-ma-hoa-chung-frappe"}
    monkeypatch.setitem(sys.modules, "frappe", fake_frappe)
    monkeypatch.delenv("LINHX_OTP_KHOA_BI_MAT", raising=False)
    monkeypatch.delenv("LINHX_OTP_SECRET", raising=False)
    monkeypatch.delenv("LINHX_OTP_HMAC_KEY", raising=False)
    with pytest.raises(RuntimeError):
        otp.bam_ma("lan@vd.vn", "dang_nhap", "123456")

    # Môi trường production không có Frappe mà thiếu biến môi trường khoá -> báo lỗi cứng
    monkeypatch.delitem(sys.modules, "frappe", raising=False)
    monkeypatch.setenv("LINHX_ENV", "production")
    with pytest.raises(RuntimeError):
        otp.bam_ma("lan@vd.vn", "dang_nhap", "123456")


def test_giu_nguyen_so_lan_sai_va_gioi_han_5_lan_phat_moi_gio_email():
    kho: dict = {}
    otp.phat_ma(kho, "an@vd.vn", "dang_nhap", "2026-11-09 10:00:00", ma_otp="111111")

    # Chờ dưới 60 giây phát lại -> bị từ chối với thông báo chung
    with pytest.raises(ValueError, match=otp.THONG_BAO_TU_CHOI_PHAT_MA):
        otp.phat_ma(kho, "an@vd.vn", "dang_nhap", "2026-11-09 10:00:30", ma_otp="222222")

    # Đoán sai 4 lần rồi xin phát mã mới sau 2 phút -> bộ đếm sai vẫn giữ nguyên 4
    for phut in range(1, 5):
        kq = otp.xac_minh(kho, "an@vd.vn", "dang_nhap", "000000", f"2026-11-09 10:0{phut}:00")
        assert kq == {"ok": False, "ly_do": "sai_ma"}

    otp.phat_ma(kho, "an@vd.vn", "dang_nhap", "2026-11-09 10:06:00", ma_otp="333333")
    # Sai thêm 1 lần nữa (tổng 5 lần) -> khoá kênh ngay lập tức
    kq_khoa = otp.xac_minh(kho, "an@vd.vn", "dang_nhap", "000000", "2026-11-09 10:06:10")
    assert kq_khoa == {"ok": False, "ly_do": "bi_khoa"}

    # Kiểm giới hạn 5 lần phát mỗi giờ theo email (dùng chỉ mục O(1))
    kho_gioi_han: dict = {}
    for lan in range(otp.GIOI_HAN_PHAT_MOI_GIO_EMAIL):
        otp.phat_ma(
            kho_gioi_han,
            "gioihan@vd.vn",
            "dang_nhap",
            f"2026-11-09 11:{lan * 2:02d}:00",
            ma_otp=f"10000{lan}",
        )
    with pytest.raises(ValueError, match=otp.THONG_BAO_TU_CHOI_PHAT_MA):
        otp.phat_ma(
            kho_gioi_han,
            "gioihan@vd.vn",
            "marketing",
            "2026-11-09 11:20:00",
            ma_otp="100009",
        )


def test_chan_phat_ma_xac_minh_trong_http_va_chi_tin_proxy_tin_cay(monkeypatch):
    fake_frappe, db = _lap_moi_truong_frappe_db(
        monkeypatch,
        request_ip="203.0.113.50",
        headers={"X-Forwarded-For": "192.0.2.99"},
        trusted_proxies=["10.0.0.1"],
        co_request=True,
    )

    # Trong HTTP request, gọi trực tiếp phat_ma / xac_minh bị chặn tuyệt đối (kể cả khi wrapper đổi tên tham số)
    kho: dict = {}
    with pytest.raises(PermissionError):
        otp.phat_ma(kho, "lan@vd.vn", "dang_nhap", "2026-11-09 10:00:00", ma_otp="123456")
    with pytest.raises(PermissionError):
        otp.xac_minh(kho, "lan@vd.vn", "dang_nhap", "123456", "2026-11-09 10:01:00")

    # request_ip không nằm trong trusted_proxies -> bỏ qua X-Forwarded-For giả mạo, lấy đúng 203.0.113.50
    assert otp._lay_ip_khach_tin_cay() == "203.0.113.50"

    # Khi request_ip nằm trong trusted_proxies -> lấy đúng IP khách từ X-Forwarded-For
    fake_frappe.local.request_ip = "10.0.0.1"
    fake_frappe.local.request.headers = {"X-Forwarded-For": "198.51.100.77, 10.0.0.1"}
    assert otp._lay_ip_khach_tin_cay() == "198.51.100.77"

    # Gọi qua phat_ma_tu_api và xac_minh_tu_api lưu trực tiếp vào bảng DB `tabLX OTP`
    da_gui: list[tuple[str, str, str]] = []
    kq_phat = otp.phat_ma_tu_api(
        email="KhachDB@VD.vn",
        muc_dich="dang_nhap",
        gui_mail=lambda em, ma, md: da_gui.append((em, ma, md)),
    )
    assert kq_phat["email"] == "khachdb@vd.vn"
    assert len(da_gui) == 1
    ma_that = da_gui[0][1]

    dong_db = db.sql("SELECT email, ma_bam, da_dung, ip_cuoi FROM `tabLX OTP`", as_dict=True)
    assert len(dong_db) == 1
    assert dong_db[0]["email"] == "khachdb@vd.vn"
    assert dong_db[0]["ip_cuoi"] == "198.51.100.77"
    assert ma_that not in json.dumps(dong_db)

    kq_xm1 = otp.xac_minh_tu_api("khachdb@vd.vn", "dang_nhap", ma_that)
    kq_xm2 = otp.xac_minh_tu_api("khachdb@vd.vn", "dang_nhap", ma_that)
    assert kq_xm1 == {"ok": True, "ly_do": None}
    assert kq_xm2 == {"ok": False, "ly_do": "da_dung"}


def test_gioi_han_10_lan_phat_va_10_lan_sai_moi_gio_theo_ip(monkeypatch):
    _lap_moi_truong_frappe_db(
        monkeypatch,
        request_ip="198.51.100.88",
        co_request=False,
    )
    # Phát đủ 10 lần từ cùng 1 IP cho 10 email khác nhau -> lần thứ 11 bị chặn
    for i in range(otp.GIOI_HAN_PHAT_MOI_GIO_IP):
        otp.phat_ma(
            None,
            f"user{i}@vd.vn",
            "dang_nhap",
            f"2026-11-09 12:{i:02d}:00",
            ma_otp=f"65432{i}",
        )
    with pytest.raises(ValueError, match=otp.THONG_BAO_TU_CHOI_PHAT_MA):
        otp.phat_ma(
            None,
            "user10@vd.vn",
            "dang_nhap",
            "2026-11-09 12:15:00",
            ma_otp="654329",
        )

    # Đoán sai 10 lần từ cùng 1 IP trên nhiều tài khoản -> IP bị khoá trước khi khoá thêm nạn nhân mới
    for i in range(otp.GIOI_HAN_SAI_MOI_GIO_IP):
        em = f"user{i // 2}@vd.vn"
        kq_sai = otp.xac_minh(None, em, "dang_nhap", "000000", f"2026-11-09 12:09:{i:02d}")
        assert kq_sai == {"ok": False, "ly_do": "sai_ma"}

    # Lần thứ 11 từ cùng IP (kể cả nhập đúng mã cho user9@vd.vn) bị chặn do IP vượt ngưỡng sai
    kq_chan_ip = otp.xac_minh(None, "user9@vd.vn", "dang_nhap", "654329", "2026-11-09 12:09:30")
    assert kq_chan_ip == {"ok": False, "ly_do": "bi_khoa"}


def test_dua_song_song_db_va_fail_closed_rowcount(monkeypatch):
    _, db = _lap_moi_truong_frappe_db(
        monkeypatch,
        request_ip="198.51.100.99",
        co_request=False,
    )
    otp._CHI_MUC_PHAT_IP.clear()
    otp._CHI_MUC_SAI_IP.clear()

    otp.phat_ma(None, "race@vd.vn", "dang_nhap", "2026-11-09 10:00:00", ma_otp="777888")

    # Khi SELECT ROW_COUNT() không xác định được -> thất bại theo hướng đóng (fail-closed) và rollback
    db.ep_rowcount_none = True
    rollback_truoc = db.so_lan_rollback
    kq_loi_rc = otp.xac_minh(None, "race@vd.vn", "dang_nhap", "777888", "2026-11-09 10:01:00")
    assert kq_loi_rc == {"ok": False, "ly_do": "da_dung"}
    assert db.so_lan_rollback > rollback_truoc
    db.ep_rowcount_none = False

    # Hai luồng gửi song song cùng mã đúng -> đúng 1 luồng ok=True, luồng còn lại da_dung
    barrier = threading.Barrier(2)

    def _goi_dung(_: int) -> dict:
        barrier.wait()
        return otp.xac_minh(None, "race@vd.vn", "dang_nhap", "777888", "2026-11-09 10:02:00")

    with ThreadPoolExecutor(max_workers=2) as pool:
        ket_qua_song_song = list(pool.map(_goi_dung, range(2)))

    so_ok = sum(1 for kq in ket_qua_song_song if kq["ok"] is True)
    so_da_dung = sum(1 for kq in ket_qua_song_song if kq == {"ok": False, "ly_do": "da_dung"})
    assert so_ok == 1
    assert so_da_dung == 1


def test_kiem_tra_dau_vao_chong_lui_gio_va_controller_lx_otp(monkeypatch):
    kho: dict = {}
    with pytest.raises(ValueError):
        otp.phat_ma(None, "a@vd.vn", "dang_nhap", "2026-11-09 10:00:00")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        otp.phat_ma(kho, "khong-phai-email", "dang_nhap", "2026-11-09 10:00:00")
    with pytest.raises(ValueError):
        otp.phat_ma(kho, "a@vd.vn", "   ", "2026-11-09 10:00:00")
    with pytest.raises(ValueError):
        otp.phat_ma(kho, "a@vd.vn", "dang_nhap", "khong-phai-ngay")
    with pytest.raises(ValueError):
        otp.phat_ma(kho, "a@vd.vn", "dang_nhap", "2026-11-09 10:00:00", ma_otp="   ")

    otp.phat_ma(kho, "b@vd.vn", "dang_nhap", "2026-11-09 10:05:00", ma_otp="123456")
    kq_lui = otp.xac_minh(kho, "b@vd.vn", "dang_nhap", "123456", "2026-11-09 10:00:00")
    assert kq_lui["ok"] is False

    # Kiểm controller DocType LXOTP chặn lưu mã OTP trần
    fake_frappe = types.ModuleType("frappe")
    fake_doc_mod = types.ModuleType("frappe.model.document")

    class _DocBase:
        pass

    fake_doc_mod.Document = _DocBase
    monkeypatch.setitem(sys.modules, "frappe", fake_frappe)
    monkeypatch.setitem(sys.modules, "frappe.model", types.ModuleType("frappe.model"))
    monkeypatch.setitem(sys.modules, "frappe.model.document", fake_doc_mod)
    sys.modules.pop("linhx_core.id.doctype.lx_otp.lx_otp", None)
    from linhx_core.id.doctype.lx_otp.lx_otp import LXOTP

    doc = LXOTP()
    doc.khoa_kenh = '["b@vd.vn", "dang_nhap"]'
    doc.email = "b@vd.vn"
    doc.muc_dich = "dang_nhap"
    doc.ma_bam = "123456"
    with pytest.raises(ValueError):
        doc.validate()

    doc.ma_bam = "a" * 64
    doc.validate()
    assert doc.ma_bam == "a" * 64
