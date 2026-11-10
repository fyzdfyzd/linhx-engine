"""F3: Kho case có số (cred), hiện trên Trang BU ifagent qua cấu hình, không sửa code khuôn.

Hợp đồng (HOP-DONG.md):
- DocType JSON trong apps/linhx_core/linhx_core/cred/doctype/lx_case/lx_case.json:
    name = "LX Case", có trường tieu_de, khach_hang, chi_so (con số kết quả), mo_ta, da_duyet (Check).
- apps/linhx_core/linhx_core/cred/kho_case.py thuần Python (không import frappe ở đầu file):
    case_cong_khai(ds_case: list[dict]) -> list[dict]
        chỉ trả các case có da_duyet == True (hoặc 1) và có chi_so không rỗng;
        case chưa duyệt (da_duyet False/0) tuyệt đối không ra danh sách công khai
    noi_dung_trang_bu(site_cfg: dict, ds_case: list[dict]) -> dict
        nhận cấu hình site (từ sites/ifagent/site.json) và ds_case; ghép các case đã duyệt
        vào danh sách "muc" của noi_dung (mỗi case thành mục có "ten" chứa tieu_de + chi_so và "mo_ta")
        để khuôn trang-bu dựng tĩnh từ NOI_DUNG_URL hoặc SITE_JSON mà không cần sửa code trong trang-bu/**.
- apps/linhx_core/linhx_core/cred/api_cred.py:
    @frappe.whitelist(allow_guest=True) `danh_sach_case` và `noi_dung_ifagent` gọi kho_case.
- sites/ifagent/site.json có cấu hình case có số cho ifagent.
- Các commit "F3: ..." không đụng bất kỳ file nào trong trang-bu/**.
"""
import json

from _chung import ma, CORE, GOC, dung_trang_bu, git, khong_import_frappe_dau_file, may_chu_web, nap_module, tim_doctype

SITE_IFAGENT = GOC / "sites" / "ifagent" / "site.json"


def _kc():
    return nap_module("linhx_core.cred.kho_case", CORE)


def test_case_chua_duyet_khong_ra_api_cong_khai():
    """Tiêu chí: case chưa duyệt không ra API công khai."""
    kc = _kc()
    ds = [
        {"name": "CS-1", "tieu_de": "Tự động hoá chốt đơn Dược", "chi_so": "+42% tỷ lệ chuyển đổi", "mo_ta": "Sau 14 ngày pilot", "da_duyet": True},
        {"name": "CS-2", "tieu_de": "Case mật chưa duyệt", "chi_so": "+99% bí mật", "mo_ta": "Nội bộ", "da_duyet": False},
        {"name": "CS-3", "tieu_de": "Case nháp 0", "chi_so": "-50% chi phí", "mo_ta": "Chờ khách duyệt", "da_duyet": 0},
    ]
    cong_khai = kc.case_cong_khai(ds)
    assert [c["name"] for c in cong_khai] == ["CS-1"]
    chu = json.dumps(cong_khai, ensure_ascii=False)
    assert "Case mật chưa duyệt" not in chu and "Case nháp 0" not in chu

    _, d = tim_doctype("LX Case")
    assert d, "thiếu DocType LX Case"
    api_p = ma("cred/api_cred.py")
    assert api_p.exists() and "case_cong_khai" in api_p.read_text(encoding="utf-8")
    khong_import_frappe_dau_file(ma("cred/kho_case.py"))


def test_trang_ifagent_dung_co_muc_case_lay_tu_api():
    """Tiêu chí: trang ifagent dựng có mục case lấy từ API."""
    kc = _kc()
    site_cfg = json.loads(SITE_IFAGENT.read_text(encoding="utf-8"))
    ds_case = [
        {"name": "CS-10", "tieu_de": "Chuỗi Nha Khoa Toàn Tâm", "chi_so": "Giảm 68% thời gian phản hồi Lead", "mo_ta": "Triển khai Agent Force trong 2 tuần", "da_duyet": True},
        {"name": "CS-11", "tieu_de": "Case Chưa Duyệt Ẩn", "chi_so": "100x", "mo_ta": "Không được lên trang", "da_duyet": False},
    ]
    nd = kc.noi_dung_trang_bu(site_cfg, ds_case)
    s, url = may_chu_web(GOC / "sites" / "ifagent", {"/api/noi-dung": lambda pt, b: (200, nd, None)})
    try:
        out = dung_trang_bu({"NOI_DUNG_URL": url + "/api/noi-dung"})
        html = (out / "index.html").read_text(encoding="utf-8")
        assert "Chuỗi Nha Khoa Toàn Tâm" in html
        assert "Giảm 68% thời gian phản hồi Lead" in html
        assert "Case Chưa Duyệt Ẩn" not in html
    finally:
        s.shutdown()


def test_commit_f3_khong_dung_trang_bu():
    """Tiêu chí: commit F3 không đụng trang-bu/**."""
    cac = [x for x in git("log", "--format=%H", "--grep=^F3:", "--extended-regexp").split() if x]
    assert cac, "chưa có commit nào 'F3: ...'"
    for h in cac:
        for f in git("show", "--name-only", "--format=", h).split("\n"):
            f = f.strip().replace("\\", "/")
            assert not f.startswith("trang-bu/"), f"commit F3 {h[:8]} không được đụng trang-bu/**: {f}"
