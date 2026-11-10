"""M1: bản đồ repo cho thợ (học repo-map Aider): chữ ký hàm/lớp + trường DocType, không thân hàm, có trần ký tự.

Hợp đồng (HOP-DONG.md, Đợt 2b):
- scripts/ban_do.py, thuần Python chuẩn (không import frappe, không gọi mạng):
    tom_tat_file(duong: str | Path) -> str
        .py: mỗi def/class cấp đầu (và method trong class) một dòng chữ ký kèm dòng đầu docstring; KHÔNG có thân hàm.
        DocType .json ("doctype": "DocType"): tên DocType + mỗi trường "fieldname:fieldtype".
        file khác: chuỗi rỗng.
    ban_do(goc: str | Path, vung: list[str], gioi_han: int = 8000) -> str
        markdown; mỗi file một mục "### <đường tương đối, gạch xuôi>"; file khớp vung (glob, có **) trước,
        sau đó file .py mà chúng import trực tiếp trong cùng repo (một bậc); bỏ test_*.py, node_modules, .git;
        tổng độ dài <= gioi_han (cắt bớt file cuối, không cắt giữa dòng); cùng đầu vào cho cùng đầu ra.
- CLI: python scripts/ban_do.py --goc <thư mục> --vung "<glob>" [--vung ...] [--gioi-han N] in markdown ra stdout, mã 0.
- Bằng chứng: bang-chung/M1/ban-do.json
    {"luc": str, "vung": list[str], "so_file": int >= 1, "so_ky_tu": int, "gioi_han": int, "giay": số < 10}
    là kết quả chạy CLI thật trên repo này với vung ["apps/linhx_core/linhx_core/pay/**"].
"""
import json
import subprocess
import sys
import time

from _chung import GOC, bang_chung_json, nap_module

TEP = GOC / "scripts" / "ban_do.py"


def _bd():
    assert TEP.exists(), "thiếu scripts/ban_do.py"
    return nap_module("ban_do", GOC / "scripts")


def _repo_mau(tmp_path):
    (tmp_path / "app" / "x" / "doctype" / "lx_a").mkdir(parents=True)
    (tmp_path / "app" / "x" / "giao.py").write_text(
        'from app.x.tien import cong\n\n\ndef giao(don: dict, kenh: str = "zalo") -> bool:\n'
        '    """Giao hàng cho đơn đã trả."""\n    BI_MAT_THAN_HAM = 1\n    return cong(1, 2) > 0\n\n\n'
        'class Kho:\n    """Kho hàng."""\n\n    def lay(self, ma: str) -> int:\n        return 42\n', encoding="utf-8")
    (tmp_path / "app" / "x" / "tien.py").write_text(
        'def cong(a: int, b: int) -> int:\n    """Cộng hai số."""\n    return a + b\n', encoding="utf-8")
    (tmp_path / "app" / "x" / "test_giao.py").write_text("def test_x():\n    assert 1\n", encoding="utf-8")
    (tmp_path / "app" / "x" / "doctype" / "lx_a" / "lx_a.json").write_text(json.dumps(
        {"doctype": "DocType", "name": "LX A", "fields": [{"fieldname": "so_tien", "fieldtype": "Currency"},
                                                         {"fieldname": "trang_thai", "fieldtype": "Select"}]}), encoding="utf-8")
    return tmp_path


def test_tom_tat_py_co_chu_ky_khong_than(tmp_path):
    """Tiêu chí: tóm tắt .py có chữ ký hàm, lớp, method và dòng đầu docstring, không có thân hàm"""
    bd = _bd()
    g = _repo_mau(tmp_path)
    t = bd.tom_tat_file(g / "app" / "x" / "giao.py")
    dong = [d for d in t.splitlines() if "def giao(" in d]
    assert dong and "don: dict" in dong[0] and "kenh: str" in dong[0] and "zalo" in dong[0] and "-> bool" in dong[0]
    assert "Giao hàng cho đơn đã trả." in t
    assert "class Kho" in t and "def lay(self, ma: str) -> int" in t
    assert "BI_MAT_THAN_HAM" not in t and "return 42" not in t


def test_tom_tat_doctype(tmp_path):
    """Tiêu chí: tóm tắt DocType có tên và fieldname:fieldtype"""
    bd = _bd()
    g = _repo_mau(tmp_path)
    t = bd.tom_tat_file(g / "app" / "x" / "doctype" / "lx_a" / "lx_a.json")
    assert "LX A" in t and "so_tien:Currency" in t and "trang_thai:Select" in t
    (g / "ghi_chu.txt").write_text("abc", encoding="utf-8")
    assert bd.tom_tat_file(g / "ghi_chu.txt") == ""


def test_ban_do_vung_va_import_mot_bac(tmp_path):
    """Tiêu chí: bản đồ gồm file trong vùng rồi file chúng import một bậc, bỏ test_*.py, ổn định"""
    bd = _bd()
    g = _repo_mau(tmp_path)
    m = bd.ban_do(g, ["app/x/giao.py"], 8000)
    assert "### app/x/giao.py" in m and "### app/x/tien.py" in m
    assert m.index("### app/x/giao.py") < m.index("### app/x/tien.py")
    assert "test_giao.py" not in m
    assert m == bd.ban_do(g, ["app/x/giao.py"], 8000)
    m2 = bd.ban_do(g, ["app/x/**"], 8000)
    assert "### app/x/doctype/lx_a/lx_a.json" in m2


def test_ban_do_tran_ky_tu(tmp_path):
    """Tiêu chí: tổng độ dài không quá gioi_han"""
    bd = _bd()
    g = _repo_mau(tmp_path)
    for i in range(60):
        (g / "app" / "x" / f"m{i}.py").write_text("".join(f"def ham_{i}_{j}(a, b):\n    return a\n" for j in range(30)), encoding="utf-8")
    m = bd.ban_do(g, ["app/x/**"], 3000)
    assert 0 < len(m) <= 3000
    assert "### app/x/giao.py" in m, "file trong vùng khai trước phải còn khi cắt"


def test_cli_tren_repo_that():
    """Tiêu chí: CLI chạy trên repo thật dưới 10 giây, không import frappe"""
    chu = TEP.read_text(encoding="utf-8")
    assert "import frappe" not in chu and "requests" not in chu and "urllib.request" not in chu
    t0 = time.time()
    r = subprocess.run([sys.executable, str(TEP), "--goc", str(GOC), "--vung", "apps/linhx_core/linhx_core/pay/**",
                        "--gioi-han", "6000"], capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert r.returncode == 0, r.stderr
    assert time.time() - t0 < 10
    assert "### apps/linhx_core/linhx_core/pay/" in r.stdout and len(r.stdout) <= 6000 + 2


def test_bang_chung():
    """Tiêu chí: bằng chứng chạy thật trên repo này"""
    d = bang_chung_json("M1", "ban-do.json")
    assert d["vung"] == ["apps/linhx_core/linhx_core/pay/**"]
    assert int(d["so_file"]) >= 1 and int(d["so_ky_tu"]) <= int(d["gioi_han"]) and float(d["giay"]) < 10
