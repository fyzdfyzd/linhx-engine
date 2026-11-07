"""N4: lệnh `linhx tao-site <ten> --cau-hinh <file>` tạo bản cài mới, cài linhx_core + linhx_worker, bật module theo cấu hình.

Hợp đồng (HOP-DONG.md):
- Gói CLI ở linhx-engine/cli/linhx_cli (chạy: python -m linhx_cli ..., PYTHONPATH=linhx-engine/cli)
- `tao-site <ten> --cau-hinh <file.json> --sites-dir <thư mục sites của bench> --chay-thu`
  in ra stdout một JSON {"lenh": [chuỗi lệnh shell sẽ chạy, theo thứ tự]} và KHÔNG chạy gì
- file cấu hình: {"modules": {"crm": true, "pay": false}}
- site đã có (<sites-dir>/<ten>/site_config.json tồn tại) thì không tạo lại, không drop, không reinstall
- Bằng chứng chạy thật trên VM: bang-chung/N4/tao-site.json
  {"site": str, "giay": số giây lần 1, "lan_hai": {"giay": số, "ma_thoat": 0, "site_cu_ping": 200}}
"""
import json
import os
import re
import subprocess
import sys

from _chung import GOC, bang_chung_json


def _chay(tmp_path, ten, modules, co_san=()):
    sites = tmp_path / "sites"
    sites.mkdir(exist_ok=True)
    for s in co_san:
        (sites / s).mkdir()
        (sites / s / "site_config.json").write_text(json.dumps({"db_name": "_" + s}), encoding="utf-8")
    ch = tmp_path / f"{ten}.json"
    ch.write_text(json.dumps({"modules": modules}), encoding="utf-8")
    env = dict(os.environ, PYTHONPATH=str(GOC / "cli"))
    r = subprocess.run([sys.executable, "-m", "linhx_cli", "tao-site", ten, "--cau-hinh", str(ch),
                        "--sites-dir", str(sites), "--chay-thu"],
                       capture_output=True, text=True, encoding="utf-8", env=env, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr
    lenh = json.loads(r.stdout)["lenh"]
    assert isinstance(lenh, list)
    return lenh, sites


def test_site_moi_co_du_buoc(tmp_path):
    lenh, sites = _chay(tmp_path, "thu1.local", {"crm": True, "pay": False})
    noi = "\n".join(lenh)
    assert "new-site thu1.local" in noi
    assert "install-app linhx_core" in noi and "install-app linhx_worker" in noi
    assert noi.index("new-site") < min(noi.index("install-app linhx_core"), noi.index("install-app linhx_worker")), \
        "phải tạo site trước rồi mới cài app"
    assert "bat_crm" in noi and "bat_pay" in noi, "phải đặt cờ module vào LX Cau Hinh theo cấu hình"
    assert not list(sites.iterdir()), "--chay-thu không được tạo gì trên đĩa"


def test_co_theo_cau_hinh(tmp_path):
    lenh, _ = _chay(tmp_path, "thu2.local", {"crm": False, "pay": True})
    noi = "\n".join(lenh)
    # cờ đúng giá trị: tên cờ và giá trị đứng gần nhau (cách viết lệnh do thợ chọn)
    assert re.search(r"bat_crm\W{0,6}(0|false|False)", noi), "bat_crm phải tắt"
    assert re.search(r"bat_pay\W{0,6}(1|true|True)", noi), "bat_pay phải bật"


def test_chay_lan_hai_khong_hong_site_cu(tmp_path):
    lenh, _ = _chay(tmp_path, "cu.local", {"crm": True, "pay": True}, co_san=["cu.local"])
    noi = "\n".join(lenh)
    assert "new-site cu.local" not in noi, "site đã có thì không tạo lại"
    for cam in ["drop-site", "reinstall", "--force", "restore"]:
        assert cam not in noi, f"lần hai không được chạy {cam}"


def test_khong_dung_site_khac(tmp_path):
    lenh, _ = _chay(tmp_path, "moi.local", {"crm": True, "pay": True}, co_san=["khac.local"])
    noi = "\n".join(lenh)
    assert "khac.local" not in noi, "lệnh tạo site mới không được đụng site khác"


def test_chay_that_tren_vm_duoi_10_phut():
    d = bang_chung_json("N4", "tao-site.json")
    assert d.get("site")
    assert 0 < float(d["giay"]) <= 600, "tạo site mới phải ≤ 10 phút"
    l2 = d.get("lan_hai") or {}
    assert l2.get("ma_thoat") == 0 and l2.get("site_cu_ping") == 200, "chạy lại lần hai phải thoát 0 và site cũ vẫn trả ping 200"
