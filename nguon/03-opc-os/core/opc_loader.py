"""Trình nạp cấu hình `opc.json` cho phép cắm rút nhiều OPC trên cùng một lõi OS mà không viết code mới."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Đảm bảo vendor report-core, astro-engine và calc-service nằm trong sys.path
VENDOR_PATHS = [
    Path("D:/LINHX/LINHX-OPC/OPC001-CHIEMTINH-VN/src/astro-engine/.venv/Lib/site-packages"),
    ROOT / "vendor" / "LAB046" / "report-core" / "src",
    ROOT / "vendor" / "OPC001" / "astro-engine" / "src",
    ROOT / "vendor" / "OPC001" / "astro-engine" / "calc-service" / "src",
    ROOT.parent / "_DUNG_CHUNG",
]
for vp in VENDOR_PATHS:
    if vp.exists() and str(vp) not in sys.path:
        sys.path.insert(0, str(vp))


ALL_10_MODULES = [
    "01_nghien_cuu_thiet_ke_report",
    "02_thiet_ke_goi_gia",
    "03_flow_thanh_toan_sinh_report",
    "04_quan_ly_user",
    "05_quan_ly_content",
    "06_cskh_da_kenh",
    "07_chi_phi_loi_nhuan",
    "08_keo_khach",
    "09_tuan_thu",
    "10_giam_sat_kpi",
]

REQUIRED_OPC_KEYS = ("opc_id", "name", "pricing")


def validate_opc_config(data: object, source_label: str = "opc.json") -> dict:
    if not isinstance(data, dict):
        raise ValueError(f"Cấu hình '{source_label}' không hợp lệ: nội dung phải là đối tượng JSON (dict).")
    missing = [k for k in REQUIRED_OPC_KEYS if not data.get(k)]
    if missing:
        raise ValueError(
            f"Cấu hình '{source_label}' thiếu các trường bắt buộc: {', '.join(missing)}. "
            "Vui lòng kiểm tra lại file opc.json."
        )
    pricing = data.get("pricing")
    if not isinstance(pricing, dict):
        raise ValueError(f"Cấu hình '{source_label}' có trường 'pricing' không đúng định dạng dict.")
    return data


def load_opc_config(opc_path_or_id: str | Path | None = None) -> dict:
    if opc_path_or_id is None:
        path = ROOT / "opc.json"
    else:
        p = Path(opc_path_or_id)
        if p.exists() and p.is_file():
            path = p
        elif (ROOT / "opcs" / str(opc_path_or_id) / "opc.json").exists():
            path = ROOT / "opcs" / str(opc_path_or_id) / "opc.json"
        elif str(opc_path_or_id) in ("opc001_chiemtinh", "opc.json") and (ROOT / "opc.json").exists():
            path = ROOT / "opc.json"
        else:
            path = ROOT / str(opc_path_or_id)

    if not path.exists() or not path.is_file():
        raise ValueError(f"Không tìm thấy tệp cấu hình OPC tại '{opc_path_or_id}'.")

    try:
        raw_text = path.read_text(encoding="utf-8")
        data = json.loads(raw_text)
    except Exception as exc:
        raise ValueError(f"Tệp cấu hình '{path.name}' bị lỗi cú pháp JSON: {exc}") from exc

    validate_opc_config(data, source_label=str(path.name))
    data["_config_path"] = str(path)
    data["_opc_dir"] = str(path.parent)
    return data


def list_all_opcs() -> list[dict]:
    opcs_dir = ROOT / "opcs"
    out = []
    if opcs_dir.exists():
        for p in sorted(opcs_dir.glob("*/opc.json")):
            try:
                out.append(load_opc_config(p))
            except ValueError:
                continue
    if not out and (ROOT / "opc.json").exists():
        try:
            out.append(load_opc_config(ROOT / "opc.json"))
        except ValueError:
            pass
    return out
