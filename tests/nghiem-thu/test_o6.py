"""O6: Chấm tự động: phiếu nộp chạy cổng kiểm + rào vùng trước, chỉ khi xanh mới gọi Claude chấm.

Hợp đồng (HOP-DONG.md):
- apps/linhx_core/linhx_core/ops/cham_phieu.py thuần Python (không import frappe ở đầu file):
    cham_phieu(phieu: dict, chay_rao: callable, chay_cong_kiem: callable, goi_claude: callable) -> dict
        - chay_rao(phieu) -> {"ok": bool, "loi": list[str]}
        - chay_cong_kiem(phieu) -> {"ok": bool, "dau_ra": str}
        - goi_claude(phieu) -> {"ket_luan": "DAT" | "CHUA_DAT", "nhan_xet": str}
        Luật:
        1. Chạy chay_rao và chay_cong_kiem trước. Nếu một trong hai trả ok == False:
           - TUYỆT ĐỐI KHÔNG gọi goi_claude (số lần gọi = 0)
           - phiếu chuyển trang_thai = "tra", ket_luan = "CHUA_DAT", loi_may = False,
             so_lan_chua_dat = int(phieu.get("so_lan_chua_dat") or 0) + 1, ghi ly_do_tra.
        2. Khi cả rào và cổng kiểm đều ok == True:
           - Gọi goi_claude(phieu) đúng 1 lần.
           - Nếu nhan_xet (hoặc ngoại lệ từ goi_claude) báo hết hạn mức Claude
             ("You've hit your weekly limit", "hit your daily limit", "usage limit", "rate_limit", "overloaded_error"):
             đánh dấu loi_may = True, ket_luan = "LOI_MAY", giữ nguyên so_lan_chua_dat (không cộng lần),
             giữ trang_thai = "nop" để chấm lại.
           - Nếu ket_luan == "DAT": trang_thai = "dat", ket_luan = "DAT", loi_may = False.
           - Nếu ket_luan == "CHUA_DAT": trang_thai = "tra", ket_luan = "CHUA_DAT", loi_may = False,
             so_lan_chua_dat = int(phieu.get("so_lan_chua_dat") or 0) + 1, ly_do_tra = nhan_xet.
"""
from _chung import ma, CORE, khong_import_frappe_dau_file, nap_module


def _cp():
    return nap_module("linhx_core.ops.cham_phieu", CORE)


def test_cong_hoac_rao_truot_khong_goi_claude_va_phieu_ve_tra():
    """Tiêu chí: cổng hoặc rào trượt thì không gọi hàm chấm Claude (đếm lượt gọi = 0), phiếu về tra."""
    cp = _cp()
    dem = {"claude": 0}

    def goi_claude_gia(_p):
        dem["claude"] += 1
        return {"ket_luan": "DAT", "nhan_xet": "ok"}

    # 1. Rào vùng trượt
    p1 = {"name": "PH-601", "trang_thai": "nop", "so_lan_chua_dat": 0}
    kq1 = cp.cham_phieu(
        p1,
        chay_rao=lambda _: {"ok": False, "loi": ["Sửa ngoài vùng O6: front/index.html"]},
        chay_cong_kiem=lambda _: {"ok": True, "dau_ra": "1 passed"},
        goi_claude=goi_claude_gia,
    )
    assert dem["claude"] == 0, "rào trượt thì không được gọi Claude"
    assert kq1["trang_thai"] == "tra" and kq1["ket_luan"] == "CHUA_DAT"
    assert kq1["so_lan_chua_dat"] == 1

    # 2. Cổng kiểm trượt
    p2 = {"name": "PH-602", "trang_thai": "nop", "so_lan_chua_dat": 1}
    kq2 = cp.cham_phieu(
        p2,
        chay_rao=lambda _: {"ok": True, "loi": []},
        chay_cong_kiem=lambda _: {"ok": False, "dau_ra": "1 failed"},
        goi_claude=goi_claude_gia,
    )
    assert dem["claude"] == 0, "cổng kiểm trượt thì không được gọi Claude"
    assert kq2["trang_thai"] == "tra" and kq2["ket_luan"] == "CHUA_DAT"
    assert kq2["so_lan_chua_dat"] == 2


def test_cong_xanh_thi_goi_cham_dung_mot_lan_ghi_dat_hoac_chua_dat():
    """Tiêu chí: cổng xanh thì gọi chấm đúng một lần, ghi DAT hoặc CHUA_DAT."""
    cp = _cp()
    dem = {"n": 0}

    def claude_dat(_p):
        dem["n"] += 1
        return {"ket_luan": "DAT", "nhan_xet": "DAT\n- Code sạch, đúng hợp đồng."}

    p_dat = {"name": "PH-603", "trang_thai": "nop", "so_lan_chua_dat": 0}
    kq_dat = cp.cham_phieu(
        p_dat,
        chay_rao=lambda _: {"ok": True, "loi": []},
        chay_cong_kiem=lambda _: {"ok": True, "dau_ra": "3 passed"},
        goi_claude=claude_dat,
    )
    assert dem["n"] == 1
    assert kq_dat["trang_thai"] == "dat" and kq_dat["ket_luan"] == "DAT"
    assert kq_dat.get("so_lan_chua_dat", 0) == 0

    dem["n"] = 0

    def claude_chua_dat(_p):
        dem["n"] += 1
        return {"ket_luan": "CHUA_DAT", "nhan_xet": "CHUA_DAT\n- Thiếu kiểm quyền."}

    p_cd = {"name": "PH-604", "trang_thai": "nop", "so_lan_chua_dat": 0}
    kq_cd = cp.cham_phieu(
        p_cd,
        chay_rao=lambda _: {"ok": True, "loi": []},
        chay_cong_kiem=lambda _: {"ok": True, "dau_ra": "3 passed"},
        goi_claude=claude_chua_dat,
    )
    assert dem["n"] == 1
    assert kq_cd["trang_thai"] == "tra" and kq_cd["ket_luan"] == "CHUA_DAT"
    assert kq_cd["so_lan_chua_dat"] == 1


def test_claude_het_han_muc_la_loi_may_khong_tinh_lan():
    """Tiêu chí: Claude hết hạn mức là lỗi máy, không tính lần."""
    cp = _cp()
    for thong_bao_het_han in (
        "You've hit your weekly limit · resets Nov 12",
        "Error: rate_limit_error: usage limit exceeded",
        "overloaded_error",
    ):
        p = {"name": "PH-605", "trang_thai": "nop", "so_lan_chua_dat": 2}
        kq = cp.cham_phieu(
            p,
            chay_rao=lambda _: {"ok": True, "loi": []},
            chay_cong_kiem=lambda _: {"ok": True, "dau_ra": "3 passed"},
            goi_claude=lambda _, tb=thong_bao_het_han: {"ket_luan": "CHUA_DAT", "nhan_xet": tb},
        )
        assert kq.get("loi_may") is True
        assert kq["so_lan_chua_dat"] == 2, "Claude hết hạn mức là lỗi máy, không được tăng so_lan_chua_dat"
        assert kq["trang_thai"] != "tra", "lỗi máy không được đẩy phiếu về tra như lỗi thợ"
    khong_import_frappe_dau_file(ma("ops/cham_phieu.py"))
