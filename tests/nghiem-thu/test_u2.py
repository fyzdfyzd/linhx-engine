"""U2: form lead của giao diện BU gửi về engine (một chỗ nhận lead), bỏ ghi tệp và Telegram trong server.mjs.

Hợp đồng (HOP-DONG.md, Đợt 3, khối giao diện):
- giao-dien/<bu>/server.mjs: POST /api/brief (và các đường form khác của site) chuyển nguyên lead sang engine
  qua biến môi trường LINHX_FORM_URL (mặc định http://127.0.0.1/api/method/linhx_core.crm.api_form.nhan_form),
  gắn nguon "<bu>"; engine trả lỗi thì trả 502 cho trình duyệt, không nuốt lead im lặng.
  Không còn LEAD_DIR, TG_TOKEN, SHEET_WEBHOOK.
- Không viết cứng IP, token, mật khẩu trong giao diện.
- node kiem/kiem.cjs (cổng K1–K10 của skill bu-frontpage) vẫn đạt với server chạy LINHX_FORM_URL trỏ máy giả.
"""
import re

from _chung import GOC

BU = ["sakedemy", "tuva", "unikon"]


def test_form_ve_engine():
    """Tiêu chí: server.mjs của 3 BU chuyển lead về engine, bỏ lưu tệp và Telegram"""
    for b in BU:
        chu = (GOC / "giao-dien" / b / "server.mjs").read_text(encoding="utf-8")
        assert "LINHX_FORM_URL" in chu, b
        for cam in ["LEAD_DIR", "TG_TOKEN", "SHEET_WEBHOOK", "api.telegram.org"]:
            assert cam not in chu, f"{b}: còn {cam}"
        assert "502" in chu, f"{b}: engine lỗi phải trả 502"


def test_khong_viet_cung_bi_mat():
    """Tiêu chí: giao diện không chứa IP, token, mật khẩu viết cứng"""
    for b in BU:
        for p in (GOC / "giao-dien" / b).rglob("*"):
            if p.suffix not in {".js", ".mjs", ".cjs", ".html", ".json"} or not p.is_file():
                continue
            chu = p.read_text(encoding="utf-8", errors="ignore")
            assert not re.search(r"\b35\.198\.251\.2\b", chu), p
            assert not re.search(r"(sk-ant-|ghp_|AIza[0-9A-Za-z_-]{20}|bot\d{8,}:)", chu), p
