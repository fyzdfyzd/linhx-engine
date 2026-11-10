"""O2: API thợ kéo phiếu: khoá riêng mỗi máy (băm, không lưu khoá trần), một phiếu một thợ, quá 150 phút tự về duyet.

Hợp đồng (HOP-DONG.md):
- apps/linhx_core/linhx_core/ops/keo_phieu.py thuần Python (không import frappe ở đầu file):
    PHUT_QUA_HAN = 150
    bam_khoa(khoa_tran: str) -> str
        băm SHA-256 hex của khoa_tran; không bao giờ trả khoá trần
    dang_ky_tho(kho: dict, ma_tho: str, khoa_tran: str) -> dict
        lưu {"ma_tho": ma_tho, "khoa_bam": bam_khoa(khoa_tran)} vào kho["tho"][ma_tho];
        tuyệt đối không lưu khoa_tran vào kho
    xac_thuc_tho(kho: dict, ma_tho: str, khoa_tran: str | None) -> bool
        so sánh hằng thời gian (hmac.compare_digest) băm của khoa_tran với kho["tho"][ma_tho]["khoa_bam"]
    thu_hoi_qua_han(ds_phieu: list[dict], luc: str, phut_qua_han: int = 150) -> list[dict]
        phiếu đang trang_thai == "giao" mà (luc - giao_luc) > phut_qua_han phút thì chuyển về
        trang_thai = "duyet", tho = None, và tăng so_lan_giao = int(so_lan_giao or 0) + 1
    keo_phieu(kho: dict, ma_tho: str, khoa_tran: str | None, luc: str) -> tuple[int, dict]
        - kho = {"tho": {...}, "phieu": [dict]}
        - sai khoá hoặc thiếu ma_tho -> trả (401, {"ok": False, ...}), không đổi kho["phieu"]
        - gọi thu_hoi_qua_han(kho["phieu"], luc) trước khi chọn phiếu
        - có khoá đồng bộ (threading.Lock) để nhiều luồng/thợ gọi cùng lúc không nhận trùng:
          chọn phiếu đầu tiên có trang_thai == "duyet", đặt trang_thai = "giao", tho = ma_tho,
          giao_luc = luc; trả (200, {"ok": True, "phieu": dict_phieu}). Hết phiếu -> (200, {"ok": True, "phieu": None}).
- apps/linhx_core/linhx_core/ops/api_tho.py: @frappe.whitelist(allow_guest=True, methods=["POST"]) `keo`
  kiểm khoá thợ, khoá dòng (for update) và trả 401 khi sai khoá.
"""
from concurrent.futures import ThreadPoolExecutor
import json

from _chung import ma, CORE, khong_import_frappe_dau_file, nap_module


def _kp():
    return nap_module("linhx_core.ops.keo_phieu", CORE)


def _kho_mau():
    kp = _kp()
    kho = {
        "tho": {},
        "phieu": [
            {"name": "PH-101", "loai_phieu": "feature", "de": "Làm O2", "trang_thai": "duyet", "so_lan_giao": 0},
        ],
    }
    kp.dang_ky_tho(kho, "tho-1", "khoa-bi-mat-may-1")
    kp.dang_ky_tho(kho, "tho-2", "khoa-bi-mat-may-2")
    return kp, kho


def test_hai_tho_keo_cung_luc_chi_mot_nhan():
    """Tiêu chí: hai thợ kéo cùng lúc chỉ một nhận."""
    kp, kho = _kho_mau()
    assert "khoa-bi-mat-may-1" not in json.dumps(kho), "không được lưu khoá trần trong kho"

    def _goi(tham_so):
        ma_tho, khoa = tham_so
        return kp.keo_phieu(kho, ma_tho, khoa, "2026-11-09 10:00:00")

    with ThreadPoolExecutor(max_workers=2) as ex:
        kq = list(ex.map(_goi, [("tho-1", "khoa-bi-mat-may-1"), ("tho-2", "khoa-bi-mat-may-2")]))

    assert all(ma == 200 for ma, _ in kq)
    nhan = [than["phieu"] for _, than in kq if than.get("phieu") is not None]
    khong_nhan = [than["phieu"] for _, than in kq if than.get("phieu") is None]
    assert len(nhan) == 1 and len(khong_nhan) == 1, "hai thợ kéo cùng lúc chỉ đúng 1 thợ nhận được phiếu"
    assert kho["phieu"][0]["trang_thai"] == "giao"
    assert kho["phieu"][0]["tho"] in ("tho-1", "tho-2")


def test_khoa_sai_tra_401():
    """Tiêu chí: khoá sai trả 401."""
    kp, kho = _kho_mau()
    for ma_tho, khoa_sai in (
        ("tho-1", "sai-khoa"),
        ("tho-1", ""),
        ("tho-1", None),
        ("tho-2", "khoa-bi-mat-may-1"),
        ("tho-la", "khoa-bi-mat-may-1"),
    ):
        ma, than = kp.keo_phieu(kho, ma_tho, khoa_sai, "2026-11-09 10:00:00")
        assert ma == 401 and than.get("ok") is False
    assert kho["phieu"][0]["trang_thai"] == "duyet", "khoá sai không được làm đổi trạng thái phiếu"


def test_phieu_giao_qua_150_phut_ve_duyet_va_tang_so_lan_giao():
    """Tiêu chí: phiếu giao quá 150 phút về duyet và tăng so_lan_giao."""
    kp, kho = _kho_mau()
    ma, than = kp.keo_phieu(kho, "tho-1", "khoa-bi-mat-may-1", "2026-11-09 10:00:00")
    assert ma == 200 and than["phieu"]["name"] == "PH-101"

    # Mới 140 phút: chưa quá 150 phút -> chưa thu hồi
    kp.thu_hoi_qua_han(kho["phieu"], "2026-11-09 12:20:00")
    assert kho["phieu"][0]["trang_thai"] == "giao"
    assert kho["phieu"][0].get("so_lan_giao", 0) == 0

    # 151 phút (> 150 phút): tự về duyet và tăng so_lan_giao lên 1
    kp.thu_hoi_qua_han(kho["phieu"], "2026-11-09 12:31:00")
    p = kho["phieu"][0]
    assert p["trang_thai"] == "duyet" and p.get("tho") is None
    assert p["so_lan_giao"] == 1


def test_api_tho_keo():
    """Kiểm tra file api_tho.py và tính thuần Python của keo_phieu.py."""
    khong_import_frappe_dau_file(ma("ops/keo_phieu.py"))
    p = ma("ops/api_tho.py")
    assert p.exists(), "thiếu apps/linhx_core/linhx_core/ops/api_tho.py"
    chu = p.read_text(encoding="utf-8")
    assert "def keo(" in chu and "401" in chu
