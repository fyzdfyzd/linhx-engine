"""O7: Hành trình: phiếu đi trọn tạo → duyệt → thợ kéo → nộp → chấm → thấy trên bàn.

Hợp đồng (HOP-DONG.md):
- tests/e2e/test_hanh_trinh_phieu.py: pytest + Playwright, URL gốc đọc từ biến môi trường E2E_LINHX_URL
  (không viết cứng IP hay mật khẩu trong kịch bản), chạy ở cả hai bề rộng 390 và 1280:
  tạo phiếu (nhap) → điều hành duyệt trên bàn /#/engine (duyet) → thợ kéo phiếu (giao) →
  thợ nộp phiếu (nop) → chấm tự động (dat) → thấy phiếu và trạng thái trên bàn /#/engine.
- Bằng chứng chạy thật trên VM: bang-chung/O7/hanh-trinh.json
    {"luc": str, "url_linhx": "http://<IP>/...", "ket_qua": "passed", "rong": [390, 1280],
     "so_test": int >= 2, "ma_phieu": str, "trang_thai_di_qua": ["nhap", "duyet", "giao", "nop", "dat"]}
  kèm bang-chung/O7/e2e.log (đầu ra pytest xanh, không có failed/error).
"""
import ipaddress
import re
from urllib.parse import urlparse

from _chung import GOC, bang_chung_json

E2E = GOC / "tests" / "e2e" / "test_hanh_trinh_phieu.py"


def test_co_kich_ban_hanh_trinh_phieu():
    """Kiểm tra kịch bản Playwright tests/e2e/test_hanh_trinh_phieu.py cho 390 + 1280."""
    assert E2E.exists(), "thiếu tests/e2e/test_hanh_trinh_phieu.py"
    chu = E2E.read_text(encoding="utf-8")
    assert "E2E_LINHX_URL" in chu
    assert "390" in chu and "1280" in chu
    assert not re.search(r"\b\d{1,3}(\.\d{1,3}){3}\b", chu), "không viết cứng IP trong kịch bản"
    assert not re.search(r"(?i)(password|mat_khau)\s*=\s*['\"][^'\"]{4,}['\"]", chu), "mật khẩu phải đọc từ biến môi trường"
    assert "#phieu-cho" in chu or "/#/engine" in chu


def test_playwright_390_va_1280_xanh_tren_vm():
    """Tiêu chí: Playwright 390 + 1280 xanh trên VM."""
    d = bang_chung_json("O7", "hanh-trinh.json")
    assert d.get("ket_qua") == "passed"
    assert sorted(d.get("rong") or []) == [390, 1280]
    assert int(d.get("so_test") or 0) >= 2
    assert d.get("ma_phieu")
    assert d.get("trang_thai_di_qua") == ["nhap", "duyet", "giao", "nop", "dat"]
    ipaddress.ip_address(urlparse(d.get("url_linhx", "")).hostname or "")
    log = (GOC / "bang-chung" / "O7" / "e2e.log").read_text(encoding="utf-8", errors="ignore")
    assert re.search(r"\b\d+ passed\b", log) and not re.search(r"\b\d+ (failed|error)", log)
