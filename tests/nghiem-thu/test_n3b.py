"""N3b: cài linhx_core thật trên VM, kiểm HTTP với cờ crm bật/tắt."""
import re

from _chung import BANG_CHUNG


def test_cai_that_tren_vm():
    p = BANG_CHUNG / "N3b" / "install-app.log"
    assert p.exists(), "thiếu bang-chung/N3b/install-app.log"
    chu = p.read_text(encoding="utf-8", errors="ignore")
    assert "install-app linhx_core" in chu
    assert re.search(r"(?i)installing linhx_core", chu)
    assert re.search(r"(?i)exit[ _]?code[:= ]+0", chu), "log phải ghi mã thoát 0"
    assert re.search(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}", chu), "log phải có thời điểm"
    assert "Traceback" not in chu


def test_http_co_crm():
    p = BANG_CHUNG / "N3b" / "http.log"
    assert p.exists(), "thiếu bang-chung/N3b/http.log"
    chu = p.read_text(encoding="utf-8", errors="ignore")
    assert re.search(r"bat_crm=1.*?\b200\b", chu, re.S), "cờ bật phải có 200"
    assert re.search(r"bat_crm=0.*?\b(403|\[\])", chu, re.S), "cờ tắt phải 403 hoặc rỗng"
