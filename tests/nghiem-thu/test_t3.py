"""T3: Hành trình ifagent: lead → đặt lịch → pilot → case.

Hợp đồng (HOP-DONG.md):
- tests/e2e/test_hanh_trinh_ifagent.py: pytest + Playwright, URL gốc đọc từ biến môi trường
  E2E_IFAGENT_URL và E2E_LINHX_URL (không viết cứng IP hay mật khẩu trong kịch bản),
  chạy ở cả hai bề rộng 390 và 1280:
  khách gửi lead trên trang ifagent → đặt lịch gọi tư vấn (F2) → tạo/chạy pilot 7 bước gắn cơ hội (F1) →
  case đã duyệt hiện trên trang ifagent (F3).
- Bằng chứng chạy thật trên VM: bang-chung/T3/hanh-trinh.json
    {"luc": str, "url_ifagent": "http://<IP>/...", "url_linhx": "http://<IP>/...",
     "ket_qua": "passed", "rong": [390, 1280], "so_test": int >= 2,
     "lead": str, "lich": str, "pilot": str, "case": str}
  kèm bang-chung/T3/e2e.log (đầu ra pytest xanh, không có failed/error).
"""
import ipaddress
import re
from urllib.parse import urlparse

from _chung import GOC, bang_chung_json

E2E = GOC / "tests" / "e2e" / "test_hanh_trinh_ifagent.py"


def test_co_kich_ban_hanh_trinh_ifagent():
    """Kiểm tra kịch bản Playwright tests/e2e/test_hanh_trinh_ifagent.py cho 390 + 1280."""
    assert E2E.exists(), "thiếu tests/e2e/test_hanh_trinh_ifagent.py"
    chu = E2E.read_text(encoding="utf-8")
    assert "E2E_IFAGENT_URL" in chu and "E2E_LINHX_URL" in chu
    assert "390" in chu and "1280" in chu
    assert not re.search(r"\b\d{1,3}(\.\d{1,3}){3}\b", chu), "không viết cứng IP trong kịch bản"
    assert not re.search(r"(?i)(password|mat_khau)\s*=\s*['\"][^'\"]{4,}['\"]", chu), "mật khẩu phải đọc từ biến môi trường"


def test_playwright_390_va_1280_xanh_tren_vm():
    """Tiêu chí: Playwright 390 + 1280 xanh trên VM."""
    d = bang_chung_json("T3", "hanh-trinh.json")
    assert d.get("ket_qua") == "passed"
    assert sorted(d.get("rong") or []) == [390, 1280]
    assert int(d.get("so_test") or 0) >= 2
    for k in ("lead", "lich", "pilot", "case"):
        assert d.get(k), f"bằng chứng thiếu khoá {k}"
    for k in ("url_ifagent", "url_linhx"):
        ipaddress.ip_address(urlparse(d.get(k, "")).hostname or "")
    log = (GOC / "bang-chung" / "T3" / "e2e.log").read_text(encoding="utf-8", errors="ignore")
    assert re.search(r"\b\d+ passed\b", log) and not re.search(r"\b\d+ (failed|error)", log)
