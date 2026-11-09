"""C2B: Xác minh chủ email/SĐT trước khi đồng ý marketing có hiệu lực (double opt-in) cho form C2 và T1 D2.

Hợp đồng (HOP-DONG.md):
- Khi khách gửi form công khai C2 (`linhx_core.crm.form.xu_ly`) hoặc T1 D2 (`linhx_core.crm.t1.ghi_ket_qua`)
  với `dong_y_marketing=True`:
    - Đồng ý "lien_he" vẫn ghi ngay và có hiệu lực ngay (`dong_y.hieu_luc(so_dong_y, nguoi, "lien_he") == True`).
    - Đồng ý "marketing" trong `so_dong_y` có `trang_thai = "cho_xac_minh"` (nên `dong_y.hieu_luc(so_dong_y, nguoi, "marketing") == False`
      tới khi chủ kênh xác nhận OTP đúng).
- apps/linhx_core/linhx_core/crm/xac_minh_marketing.py thuần Python (không import frappe ở đầu file),
  dùng lại OTP của I3 (`linhx_core.id.otp`):
    tao_yeu_cau(kho_otp: dict, email: str, nguoi: str, so_dong_y: list[dict], luc: str,
                ma_otp: str | None = None, gui_mail: callable | None = None) -> dict
        phát mã OTP (chỉ lưu băm trong kho_otp, hạn 10 phút, dùng 1 lần) cho kênh email;
        đảm bảo dòng marketing trong so_dong_y ở trạng thái "cho_xac_minh" (chưa có hiệu lực)
    xac_nhan_marketing(phuong_thuc: str, kho_otp: dict, email: str, nguoi: str, ma_nhap: str,
                       so_dong_y: list[dict], luc: str, nguon: str = "xac-minh-otp") -> tuple[int, dict]
        - Nếu phuong_thuc != "POST" (vd. "GET" khi bộ quét mail tự mở link):
          KHÔNG tiêu thụ mã OTP và KHÔNG ghi đồng ý marketing (`dong_y.hieu_luc(so_dong_y, nguoi, "marketing")` vẫn False),
          trả (405, {"ok": False, "can_post": True, "so_dong_y": so_dong_y}).
        - Nếu phuong_thuc == "POST": kiểm mã qua otp.xac_minh(kho_otp, email, "marketing", ma_nhap, luc):
          * Mã đúng, còn hạn, chưa dùng: ghi dòng đồng ý marketing đã xác minh (`trang_thai="da_xac_minh"`, `dong_y=True`)
            vào sổ mới để `dong_y.hieu_luc(so_moi, nguoi, "marketing") == True`; trả (200, {"ok": True, "so_dong_y": so_moi}).
          * Mã hết hạn, đã dùng hoặc sai: không kích hoạt đồng ý marketing, trả (400, {"ok": False, "ly_do": ..., "so_dong_y": so_dong_y}).
- apps/linhx_core/linhx_core/crm/api_form.py thêm @frappe.whitelist(allow_guest=True, methods=["POST"]) `xac_nhan_marketing`.
"""
import json

from _chung import CORE, khong_import_frappe_dau_file, nap_module

LUC = "2026-11-09 09:00:00"


def _dy():
    return nap_module("linhx_core.crm.dong_y", CORE)


def _form():
    return nap_module("linhx_core.crm.form", CORE)


def _t1():
    return nap_module("linhx_core.crm.t1", CORE)


def _xm():
    return nap_module("linhx_core.crm.xac_minh_marketing", CORE)


def test_dong_y_marketing_chi_co_hieu_luc_sau_khi_chu_kenh_xac_nhan():
    """Tiêu chí: Đồng ý marketing qua form công khai chỉ có hiệu lực sau khi chủ kênh xác nhận."""
    dy, f, t1, xm = _dy(), _form(), _t1(), _xm()

    # 1. Qua form C2: lien_he hiệu lực ngay, marketing ở trạng thái cho_xac_minh (chưa hiệu lực)
    r_c2 = f.xu_ly(
        {
            "ho_ten": "Lan",
            "dien_thoai": "0912345678",
            "email": "lan@vd.vn",
            "nhu_cau": "Tư vấn AI",
            "dong_y_lien_he": True,
            "dong_y_marketing": True,
        },
        [],
        [],
        LUC,
        "trang-ifagent",
    )
    so_c2 = r_c2["so_dong_y"]
    nguoi_c2 = so_c2[0]["nguoi"]
    assert dy.hieu_luc(so_c2, nguoi_c2, "lien_he") is True, "đồng ý liên hệ phải có hiệu lực ngay"
    assert dy.hieu_luc(so_c2, nguoi_c2, "marketing") is False, "đồng ý marketing chưa xác minh OTP thì chưa có hiệu lực"
    assert any(x["muc_dich"] == "marketing" and x.get("trang_thai") == "cho_xac_minh" for x in so_c2)

    # 2. Qua form T1 D2: tương tự, marketing chờ xác minh
    r_t1 = t1.ghi_ket_qua(
        {"email": "minh@vd.vn", "tong": 15, "muc": "Sẵn sàng một phần", "dong_y_lien_he": True, "dong_y_marketing": True},
        [],
        [],
        LUC,
    )
    so_t1 = r_t1["so_dong_y"]
    nguoi_t1 = so_t1[0]["nguoi"]
    assert dy.hieu_luc(so_t1, nguoi_t1, "lien_he") is True
    assert dy.hieu_luc(so_t1, nguoi_t1, "marketing") is False

    # 3. Chủ email xác nhận OTP qua POST -> marketing mới có hiệu lực
    kho_otp = {}
    xm.tao_yeu_cau(kho_otp, "lan@vd.vn", nguoi_c2, so_c2, LUC, ma_otp="314159")
    ma_http, kq = xm.xac_nhan_marketing("POST", kho_otp, "lan@vd.vn", nguoi_c2, "314159", so_c2, "2026-11-09 09:02:00")
    assert ma_http == 200 and kq["ok"] is True
    assert dy.hieu_luc(kq["so_dong_y"], nguoi_c2, "marketing") is True


def test_link_xac_nhan_can_post_bo_quet_mail_mo_get_khong_ghi_dong_y():
    """Tiêu chí: Link xác nhận cần thao tác của người (POST), bộ quét mail mở GET không ghi đồng ý."""
    dy, xm = _dy(), _xm()
    kho_otp = {}
    so = [{"nguoi": "lan@vd.vn", "muc_dich": "lien_he", "dong_y": True, "luc": LUC, "nguon": "form"}]
    xm.tao_yeu_cau(kho_otp, "lan@vd.vn", "lan@vd.vn", so, LUC, ma_otp="271828")

    # Bộ quét mail gọi GET với đúng mã OTP -> không ghi đồng ý và không làm mất mã OTP
    ma_get, kq_get = xm.xac_nhan_marketing("GET", kho_otp, "lan@vd.vn", "lan@vd.vn", "271828", so, "2026-11-09 09:01:00")
    assert ma_get == 405 or kq_get.get("ok") is False
    assert dy.hieu_luc(kq_get["so_dong_y"], "lan@vd.vn", "marketing") is False

    # Sau đó người thật bấm nút gửi POST với cùng mã -> thành công
    ma_post, kq_post = xm.xac_nhan_marketing("POST", kho_otp, "lan@vd.vn", "lan@vd.vn", "271828", so, "2026-11-09 09:02:00")
    assert ma_post == 200 and kq_post["ok"] is True
    assert dy.hieu_luc(kq_post["so_dong_y"], "lan@vd.vn", "marketing") is True


def test_ma_xac_nhan_luu_db_co_han_dung_dung_mot_lan():
    """Tiêu chí: Mã xác nhận lưu DB có hạn dùng, dùng một lần."""
    dy, xm = _dy(), _xm()
    kho_otp = {}
    so = []
    xm.tao_yeu_cau(kho_otp, "hoa@vd.vn", "hoa@vd.vn", so, "2026-11-09 09:00:00", ma_otp="556677")
    assert "556677" not in json.dumps(kho_otp), "chỉ lưu băm mã xác nhận, không lưu mã trần"

    # Quá 10 phút -> hết hạn
    ma_tre, kq_tre = xm.xac_nhan_marketing("POST", kho_otp, "hoa@vd.vn", "hoa@vd.vn", "556677", so, "2026-11-09 09:10:01")
    assert ma_tre == 400 and kq_tre["ok"] is False
    assert dy.hieu_luc(kq_tre["so_dong_y"], "hoa@vd.vn", "marketing") is False

    # Phát mã mới, dùng lần 1 thành công, dùng lại lần 2 bị từ chối
    xm.tao_yeu_cau(kho_otp, "hoa@vd.vn", "hoa@vd.vn", so, "2026-11-09 09:15:00", ma_otp="998877")
    ma1, kq1 = xm.xac_nhan_marketing("POST", kho_otp, "hoa@vd.vn", "hoa@vd.vn", "998877", so, "2026-11-09 09:16:00")
    ma2, kq2 = xm.xac_nhan_marketing("POST", kho_otp, "hoa@vd.vn", "hoa@vd.vn", "998877", kq1["so_dong_y"], "2026-11-09 09:16:10")
    assert ma1 == 200 and kq1["ok"] is True
    assert ma2 == 400 and kq2["ok"] is False

    khong_import_frappe_dau_file(CORE / "linhx_core" / "crm" / "xac_minh_marketing.py")
    chu = (CORE / "linhx_core" / "crm" / "api_form.py").read_text(encoding="utf-8")
    assert "def xac_nhan_marketing(" in chu
