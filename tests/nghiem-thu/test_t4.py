"""T4: hành trình lại sau khi chuyển lớp: lead -> đơn -> trả -> giao qua gói, trên VM.

Hợp đồng (HOP-DONG.md, Đợt 3):
- tests/e2e/test_hanh_trinh_lop.py: pytest + Playwright, URL từ E2E_LINHX_URL, 390 + 1280:
  gửi form lead ở một giao diện BU -> có LX Nguoi; tạo đơn gói loai_giao bao_cao -> webhook SePay thử (chữ ký thử, không gọi SePay thật)
  -> LX Su Kien don.da_tra "xong" -> báo cáo có link.
- Bằng chứng: bang-chung/T4/hanh-trinh.json {"luc": str, "url_linhx": "http://<IP>/...", "ket_qua": "passed", "rong": [390, 1280],
  "so_test": int >= 2, "su_kien": "xong"} kèm bang-chung/T4/e2e.log.
"""
from _chung import GOC, bang_chung_json
from _dot3 import kiem_kien_truc


def test_kich_ban_va_kien_truc():
    """Tiêu chí: kịch bản hành trình sau chuyển lớp có, luật ba lớp xanh"""
    chu = (GOC / "tests" / "e2e" / "test_hanh_trinh_lop.py").read_text(encoding="utf-8")
    assert "E2E_LINHX_URL" in chu and "390" in chu and "1280" in chu
    kiem_kien_truc()


def test_bang_chung_vm():
    """Tiêu chí: hành trình xanh trên VM, sự kiện giao xong"""
    d = bang_chung_json("T4", "hanh-trinh.json")
    assert d["ket_qua"] == "passed" and sorted(d["rong"]) == [390, 1280] and d["su_kien"] == "xong" and int(d["so_test"]) >= 2
