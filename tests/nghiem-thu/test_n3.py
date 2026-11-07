"""N3: khung app Frappe linhx_core cài được trên bench; mỗi module bật/tắt bằng cờ trong LX Cau Hinh.

Hợp đồng (HOP-DONG.md):
- apps/linhx_core/pyproject.toml, apps/linhx_core/linhx_core/{__init__.py,hooks.py,modules.txt}
- DocType "LX Cau Hinh" (issingle) có trường Check bat_crm, bat_pay
- linhx_core/co_module.py thuần Python (không import frappe ở đầu file):
    module_bat(ten_module, cau_hinh: dict) -> bool
    doctype_bi_an(ten_doctype, cau_hinh: dict) -> bool
  cau_hinh là dict giá trị LX Cau Hinh, ví dụ {"bat_crm": 0, "bat_pay": 1}
- hooks.py nối co_module vào quyền (has_permission / permission_query_conditions) để DocType của module tắt ẩn khỏi API
- Bằng chứng cài thật: bang-chung/N3/install-app.log (đầu ra `bench --site test install-app linhx_core`)
"""
import re

from _chung import CORE, BANG_CHUNG, nap_module, tim_doctype, ten_truong


def test_khung_app_frappe():
    for p in ["pyproject.toml", "linhx_core/__init__.py", "linhx_core/hooks.py", "linhx_core/modules.txt"]:
        assert (CORE / p).exists(), f"thiếu apps/linhx_core/{p}"
    hooks = (CORE / "linhx_core" / "hooks.py").read_text(encoding="utf-8")
    assert re.search(r"app_name\s*=\s*['\"]linhx_core['\"]", hooks), "hooks.py thiếu app_name = 'linhx_core'"
    assert "__version__" in (CORE / "linhx_core" / "__init__.py").read_text(encoding="utf-8")
    mods = (CORE / "linhx_core" / "modules.txt").read_text(encoding="utf-8").lower()
    for m in ["crm", "pay"]:
        assert m in mods, f"modules.txt thiếu module {m}"


def test_lx_cau_hinh_co_co_module():
    p, d = tim_doctype("LX Cau Hinh")
    assert d, "thiếu DocType LX Cau Hinh"
    assert d.get("issingle") == 1, "LX Cau Hinh phải là Single"
    tr = ten_truong(d)
    for co in ["bat_crm", "bat_pay"]:
        assert co in tr and tr[co].get("fieldtype") == "Check", f"LX Cau Hinh thiếu trường Check {co}"


def test_tat_co_crm_thi_doctype_crm_an():
    cm = nap_module("linhx_core.co_module", CORE)
    assert cm.module_bat("crm", {"bat_crm": 1}) is True
    assert cm.module_bat("crm", {"bat_crm": 0}) is False
    assert cm.doctype_bi_an("LX Nguoi", {"bat_crm": 0, "bat_pay": 1}) is True
    assert cm.doctype_bi_an("LX Nguoi", {"bat_crm": 1, "bat_pay": 1}) is False
    # tắt crm không làm ẩn DocType của pay
    assert cm.doctype_bi_an("LX Goi", {"bat_crm": 0, "bat_pay": 1}) is False
    assert cm.doctype_bi_an("LX Goi", {"bat_crm": 1, "bat_pay": 0}) is True
    # DocType lõi (LX Cau Hinh) không bao giờ ẩn
    assert cm.doctype_bi_an("LX Cau Hinh", {"bat_crm": 0, "bat_pay": 0}) is False


def test_hooks_noi_co_module_vao_quyen():
    hooks = (CORE / "linhx_core" / "hooks.py").read_text(encoding="utf-8")
    assert "co_module" in hooks and re.search(r"has_permission|permission_query_conditions", hooks), \
        "hooks.py phải nối co_module vào has_permission hoặc permission_query_conditions"


def test_cai_that_tren_bench():
    p = BANG_CHUNG / "N3" / "install-app.log"
    assert p.exists(), "thiếu bang-chung/N3/install-app.log (chạy bench --site test install-app linhx_core trên VM/container)"
    chu = p.read_text(encoding="utf-8", errors="ignore")
    assert "install-app linhx_core" in chu, "log phải chứa lệnh install-app linhx_core"
    assert re.search(r"(?i)installing linhx_core", chu), "log không có dòng 'Installing linhx_core'"
    assert "Traceback" not in chu and not re.search(r"(?im)^\s*error\b", chu), "log cài có lỗi"
