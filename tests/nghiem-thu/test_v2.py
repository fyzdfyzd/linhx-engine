"""V2: CI GitHub xanh trên main: cài Playwright + Chromium, Node cho trang-bu, kiểm mọi features-dot*.json.

Hợp đồng (HOP-DONG.md, Đợt 2c):
- .github/workflows/linhx-engine.yml: cài pytest + playwright, chạy "playwright install --with-deps chromium",
  actions/setup-node khi có trang-bu/package.json (npm ci), vòng lặp cong_kiem kiem cho features-dot*.json (không chỉ dot1).
  Feature cần máy cty/VM thật (bằng chứng ghi từ máy thật) vẫn đọc bằng chứng đã commit, CI không gọi mạng ngoài GitHub.
- Bằng chứng: bang-chung/V2/ci.json {"run_url": "https://github.com/fyzdfyzd/linhx-engine/actions/runs/<số>",
  "ket_luan": "success", "sha": str (>= 7 ký tự hex)} của một lượt chạy trên nhánh thợ hoặc main.
"""
import re

from _chung import GOC, bang_chung_json

WF = GOC / ".github" / "workflows" / "linhx-engine.yml"


def test_workflow_cai_du():
    """Tiêu chí: workflow cài Playwright Chromium và Node, kiểm mọi features-dot*.json"""
    chu = WF.read_text(encoding="utf-8")
    assert "playwright install" in chu and "chromium" in chu
    assert "setup-node" in chu
    assert "features-dot*.json" in chu or "features-dot2" in chu
    assert "features-dot1*.json" not in chu, "phải kiểm cả dot2, không chỉ dot1"


def test_bang_chung_ci_xanh():
    """Tiêu chí: một lượt CI xanh có bằng chứng"""
    d = bang_chung_json("V2", "ci.json")
    assert re.fullmatch(r"https://github\.com/fyzdfyzd/linhx-engine/actions/runs/\d+", d["run_url"])
    assert d["ket_luan"] == "success" and re.fullmatch(r"[0-9a-f]{7,40}", d["sha"])
