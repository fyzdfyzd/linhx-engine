"""O3: API thợ nộp: commit, nhánh, nhật ký, phút, token ghi vào phiếu.

Hợp đồng (HOP-DONG.md):
- apps/linhx_core/linhx_core/ops/nop_phieu.py thuần Python (không import frappe ở đầu file):
    nop_phieu(kho: dict, ma_tho: str, khoa_tran: str | None, du_lieu: dict, luc: str) -> tuple[int, dict]
        - du_lieu: {"ma_phieu": str, "commit": str, "nhanh": str, "nhat_ky": str, "phut": int | float, "token": int}
        - xác thực khoá thợ qua keo_phieu.xac_thuc_tho(kho, ma_tho, khoa_tran); sai khoá -> (401, {"ok": False})
        - tìm phiếu có name == du_lieu["ma_phieu"] trong kho["phieu"]; không có -> (404, {"ok": False})
        - nếu phiếu đang giao cho thợ khác (phieu.get("tho") != ma_tho) -> trả (403, {"ok": False, "loi": ...}),
          không sửa phiếu
        - nếu phiếu đã ở trang_thai == "nop" của cùng ma_tho và cùng commit == du_lieu["commit"]:
          chống trùng (idempotent), không thêm bản ghi mới vào kho["lan_nop"], trả (200, {"ok": True, "trung": True, "phieu": ...})
        - hợp lệ: cập nhật phiếu trang_thai = "nop", commit, nhanh, nhat_ky, phut (int/float), token (int), nop_luc = luc;
          ghi 1 bản ghi vào kho.setdefault("lan_nop", []) và trả (200, {"ok": True, "trung": False, "phieu": ...}).
- apps/linhx_core/linhx_core/ops/api_tho.py thêm @frappe.whitelist(allow_guest=True, methods=["POST"]) `nop`.
"""
from _chung import CORE, khong_import_frappe_dau_file, nap_module


def _np():
    return nap_module("linhx_core.ops.nop_phieu", CORE)


def _kp():
    return nap_module("linhx_core.ops.keo_phieu", CORE)


def _kho_dang_giao():
    kp = _kp()
    kho = {
        "tho": {},
        "phieu": [
            {
                "name": "PH-201",
                "loai_phieu": "feature",
                "de": "Làm O3",
                "trang_thai": "giao",
                "tho": "tho-1",
                "giao_luc": "2026-11-09 10:00:00",
            }
        ],
        "lan_nop": [],
    }
    kp.dang_ky_tho(kho, "tho-1", "khoa-may-1")
    kp.dang_ky_tho(kho, "tho-2", "khoa-may-2")
    return kho


def test_nop_phieu_khong_phai_cua_minh_tra_403():
    """Tiêu chí: nộp phiếu không phải của mình trả 403."""
    np = _np()
    kho = _kho_dang_giao()
    ma, than = np.nop_phieu(
        kho,
        "tho-2",
        "khoa-may-2",
        {
            "ma_phieu": "PH-201",
            "commit": "abc1234",
            "nhanh": "tu-dong/engine-t2",
            "nhat_ky": "đã xong",
            "phut": 18,
            "token": 45000,
        },
        "2026-11-09 10:18:00",
    )
    assert ma == 403 and than.get("ok") is False
    assert kho["phieu"][0]["trang_thai"] == "giao" and kho["phieu"][0]["tho"] == "tho-1"
    assert len(kho["lan_nop"]) == 0


def test_phut_va_token_luu_dung():
    """Tiêu chí: phút và token lưu đúng."""
    np = _np()
    kho = _kho_dang_giao()
    ma, than = np.nop_phieu(
        kho,
        "tho-1",
        "khoa-may-1",
        {
            "ma_phieu": "PH-201",
            "commit": "deadbeef12",
            "nhanh": "tu-dong/engine-t1",
            "nhat_ky": "10 passed in 2.3s",
            "phut": 27,
            "token": 128500,
        },
        "2026-11-09 10:27:00",
    )
    assert ma == 200 and than.get("ok") is True
    p = kho["phieu"][0]
    assert p["trang_thai"] == "nop"
    assert p["commit"] == "deadbeef12" and p["nhanh"] == "tu-dong/engine-t1"
    assert p["nhat_ky"] == "10 passed in 2.3s"
    assert p["phut"] == 27 and p["token"] == 128500


def test_nop_hai_lan_cung_commit_khong_tao_ban_ghi_trung():
    """Tiêu chí: nộp hai lần cùng commit không tạo bản ghi trùng."""
    np = _np()
    kho = _kho_dang_giao()
    du_lieu = {
        "ma_phieu": "PH-201",
        "commit": "cafe9999",
        "nhanh": "tu-dong/engine-t1",
        "nhat_ky": "ok",
        "phut": 15,
        "token": 60000,
    }
    ma1, t1 = np.nop_phieu(kho, "tho-1", "khoa-may-1", du_lieu, "2026-11-09 10:15:00")
    ma2, t2 = np.nop_phieu(kho, "tho-1", "khoa-may-1", du_lieu, "2026-11-09 10:15:05")
    assert ma1 == 200 and ma2 == 200
    assert t2.get("trung") is True
    assert len(kho["lan_nop"]) == 1, "nộp hai lần cùng commit chỉ được lưu 1 bản ghi nộp"


def test_api_tho_nop():
    """Kiểm tra hàm nop trong api_tho.py và tính thuần Python của nop_phieu.py."""
    khong_import_frappe_dau_file(CORE / "linhx_core" / "ops" / "nop_phieu.py")
    chu = (CORE / "linhx_core" / "ops" / "api_tho.py").read_text(encoding="utf-8")
    assert "def nop(" in chu and "403" in chu
