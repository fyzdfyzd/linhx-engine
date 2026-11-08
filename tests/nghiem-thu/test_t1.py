"""T1: Playwright: một lead đi trọn (T1 → hồ sơ + đồng ý → cơ hội → giao người → thấy trên bàn), 390 và 1280.
Hành trình xanh trên VM.

Hợp đồng (HOP-DONG.md):
- tests/e2e/test_hanh_trinh_lead.py: pytest + Playwright, URL gốc đọc từ biến môi trường E2E_IFAGENT_URL và
  E2E_LINHX_URL (không viết IP trong code), tài khoản điều hành đọc từ biến môi trường; chạy ở 390 và 1280:
  làm T1 trên trang ifagent → đưa email + đồng ý → (A5) lead sang linhx → Cơ hội có phu_trach → #lead-moi trên bàn linhx.
  Email thử dạng e2e+<thời điểm>@... để không trùng; không xoá dữ liệu thật.
- Bằng chứng: bang-chung/T1/e2e.json {"luc", "url_ifagent", "url_linhx", "ket_qua": "passed", "rong": [390, 1280],
  "so_test": int >= 2, "lead": "<name>", "phu_trach": "<user>"} ghi từ lần chạy thật trên VM, kèm bang-chung/T1/e2e.log
  (đầu ra pytest).
"""
import ipaddress
import re
from urllib.parse import urlparse

from _chung import GOC, bang_chung_json

E2E = GOC / "tests" / "e2e" / "test_hanh_trinh_lead.py"


def test_co_kich_ban():
    chu = E2E.read_text(encoding="utf-8")
    assert "E2E_IFAGENT_URL" in chu and "E2E_LINHX_URL" in chu
    assert "390" in chu and "1280" in chu
    assert not re.search(r"\b\d{1,3}(\.\d{1,3}){3}\b", chu), "không viết IP trong kịch bản"
    assert not re.search(r"(?i)(password|mat_khau)\s*=\s*['\"][^'\"]{4,}['\"]", chu), "mật khẩu đọc từ biến môi trường"
    assert "#lead-moi" in chu and "kham" in chu


def test_bang_chung_vm():
    d = bang_chung_json("T1", "e2e.json")
    assert d.get("ket_qua") == "passed" and sorted(d.get("rong") or []) == [390, 1280]
    assert int(d.get("so_test") or 0) >= 2 and d.get("lead") and d.get("phu_trach")
    for k in ("url_ifagent", "url_linhx"):
        ipaddress.ip_address(urlparse(d.get(k, "")).hostname or "")
    log = (GOC / "bang-chung" / "T1" / "e2e.log").read_text(encoding="utf-8", errors="ignore")
    assert re.search(r"\b\d+ passed\b", log) and not re.search(r"\b\d+ (failed|error)", log)
