"""U3: CI giao diện: PR đổi giao-dien/* chạy cổng K1–K10 cho site bị đổi trước khi merge.

Hợp đồng (HOP-DONG.md, Đợt 3, khối giao diện):
- .github/workflows/giao-dien.yml: on pull_request + push main, paths "giao-dien/**";
  cài Node + Playwright Chromium; với mỗi site bị đổi: chạy server.mjs (LINHX_FORM_URL trỏ máy giả cục bộ) rồi node kiem/kiem.cjs.
- Bằng chứng: bang-chung/U3/ci.json {"run_url": "https://github.com/fyzdfyzd/linhx-engine/actions/runs/<số>", "ket_luan": "success",
  "site": list[str] các site đã kiểm}.
"""
import re

from _chung import GOC, bang_chung_json


def test_workflow_giao_dien():
    """Tiêu chí: workflow chạy cổng K1–K10 khi giao diện BU đổi"""
    chu = (GOC / ".github" / "workflows" / "giao-dien.yml").read_text(encoding="utf-8")
    assert "giao-dien/**" in chu and "pull_request" in chu
    assert "kiem/kiem.cjs" in chu and "server.mjs" in chu and "playwright" in chu


def test_bang_chung_ci():
    """Tiêu chí: một lượt CI giao diện xanh có bằng chứng"""
    d = bang_chung_json("U3", "ci.json")
    assert re.fullmatch(r"https://github\.com/fyzdfyzd/linhx-engine/actions/runs/\d+", d["run_url"])
    assert d["ket_luan"] == "success" and len(d["site"]) >= 1
