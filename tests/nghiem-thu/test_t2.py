"""T2: Playwright: một đơn báo cáo trả QR (webhook giả lập SePay) rồi tự giao. Hành trình xanh trên VM, không gọi SePay thật.

Hợp đồng (HOP-DONG.md):
- tests/e2e/test_don_bao_cao.py: pytest + Playwright, URL gốc từ E2E_LINHX_URL, khoá webhook từ E2E_SEPAY_KHOA (biến môi trường):
  trang #/ chọn gói, bấm trả QR (Q1) → thấy img[data-qr] → gửi webhook giả lập đúng dạng SePay vào
  /api/method/linhx_core.pay.api_sepay.webhook với số tiền + nội dung của đơn → đơn da_tra (B3) → có LX Job nguon "don" (B4)
  trong 1 phút. Không gọi my.sepay.vn hay api SePay thật.
- Bằng chứng: bang-chung/T2/e2e.json {"luc", "url_linhx", "ket_qua": "passed", "don": "<ma>", "job": "<name>",
  "giay_tu_tra_toi_job": số <= 60} + bang-chung/T2/e2e.log.
"""
import ipaddress
import re
from urllib.parse import urlparse

from _chung import GOC, bang_chung_json

E2E = GOC / "tests" / "e2e" / "test_don_bao_cao.py"


def test_co_kich_ban_khong_goi_sepay_that():
    chu = E2E.read_text(encoding="utf-8")
    assert "E2E_LINHX_URL" in chu and "E2E_SEPAY_KHOA" in chu
    assert "api_sepay.webhook" in chu and "data-qr" in chu
    assert not re.search(r"(?i)sepay\.vn", chu), "không gọi SePay thật"
    assert not re.search(r"\b\d{1,3}(\.\d{1,3}){3}\b", chu), "không viết IP trong kịch bản"


def test_bang_chung_vm():
    d = bang_chung_json("T2", "e2e.json")
    assert d.get("ket_qua") == "passed" and d.get("don") and d.get("job")
    assert 0 <= float(d.get("giay_tu_tra_toi_job", 999)) <= 60
    ipaddress.ip_address(urlparse(d.get("url_linhx", "")).hostname or "")
    log = (GOC / "bang-chung" / "T2" / "e2e.log").read_text(encoding="utf-8", errors="ignore")
    assert re.search(r"\b\d+ passed\b", log) and not re.search(r"\b\d+ (failed|error)", log)
