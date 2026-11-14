"""Phần lõi dùng chung của họ skill linhx-rea (ảnh, video, sách, báo cáo, bài).

Cung cấp:
- Đọc/ghi JSON, YAML chuẩn UTF-8.
- Kiểm tra và định dạng mốc bằng chứng (`{"x","y"}`, `{"vung"}`, `{"hop"}`, lưới 3x3 `A1..C3`).
- Kiểm tra thẻ thủ pháp theo `the-thu-phap.schema.json`.
- CLI các lệnh con:
  * `tom <dir_ra>`                     : dựng bộ hồ sơ ra chung (`cau-truc.md`, `nhip.md`, `nguyen-lieu.md`, `ve-dep.md`, `thu-phap/`, `ve-nguoc/`) và `tom.md` ≤40 dòng.
  * `viec-doc <dir_ra> --tu-vung <y>`  : sinh `<anh>/viec_doc.json`, mẫu `<anh>/dap_an.json` và `<dir_ra>/VIEC-DOC.md`.
  * `ap <dir_ra>`                      : kiểm và trộn `dap_an.json` với `do.json` (KHÔNG ĐÈ SỐ ĐO) -> `doc.json`, `doc.md`.
  * `the <dir_ra>`                     : gom `the_de_xuat` từ `doc.json`, kiểm schema -> `thu-phap/thu-phap.jsonl`, `thu-phap/README.md`, `the-loi.jsonl`.
  * `sua [dir_ra] [--mo-ta "..."]`     : gom ghi chú `MAY-SAI:` từ `dap_an.json` (hoặc lỗi lẻ) ghi nối vào `<dir_ra>/sua-sai.jsonl`.
  * `sua [dir_ra] --kiem-lai`          : kiểm tự động lại từng mục trong `<dir_ra>/sua-sai.jsonl` bằng `do.json` mới, cập nhật `trang_thai` tại chỗ và in bảng.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import re
import sys
import time
from pathlib import Path
from typing import Any

import yaml

THU_MUC_SCRIPTS = Path(__file__).resolve().parent
THU_MUC_SKILL = THU_MUC_SCRIPTS.parent
if str(THU_MUC_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(THU_MUC_SCRIPTS))

import anh_doc  # noqa: E402
import anh_tom  # noqa: E402

PHIEN_BAN = "0.2.0"
MAU_LUOI_3X3 = re.compile(r"^[ABC][123](?:-[ABC][123])?$")
TRUONG_BAT_BUOC_THE: tuple[str, ...] = ("ten", "loai", "moc", "mo_ta", "cach_lam", "khi_dung", "nguon")
DUONG_DAN_SUA_SAI_CU = THU_MUC_SKILL / "sua-sai.jsonl"
DUONG_DAN_TU_VUNG_ANH = THU_MUC_SKILL / "tu-vung" / "anh.yaml"
DUONG_DAN_LUAT_DOP = THU_MUC_SKILL / "references" / "luat-dop.md"
DUONG_DAN_SCHEMA_THE = THU_MUC_SKILL / "references" / "the-thu-phap.schema.json"
_CACHE_SCHEMA_THE: dict[str, Any] | None = None


def _cau_hinh_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


# ---------------- I/O & Mốc dùng chung ---------------------------------------------------------------

def doc_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def ghi_json(path: str | Path, data: Any) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return p


def doc_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def xy_sang_luoi(x: float, y: float) -> str:
    """Chuyển toạ độ chuẩn hoá (x, y) trong [0, 1] sang mã ô lưới 3x3 A1..C3."""
    hang = "A" if y < (1.0 / 3.0) else ("B" if y < (2.0 / 3.0) else "C")
    cot = "1" if x < (1.0 / 3.0) else ("2" if x < (2.0 / 3.0) else "3")
    return f"{hang}{cot}"


def _la_so_thuc(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _kiem_hop_01(hop: Any) -> bool:
    if not isinstance(hop, (list, tuple)) or len(hop) != 4:
        return False
    if not all(_la_so_thuc(v) for v in hop):
        return False
    x0, y0, x1, y1 = [float(v) for v in hop]
    if not all(0.0 <= c <= 1.0 for c in (x0, y0, x1, y1)):
        return False
    return x0 <= x1 and y0 <= y1 and (x1 > x0 or y1 > y0)


def kiem_tra_moc(moc: Any, loai: str = "anh") -> bool:
    """Kiểm tra mốc bằng chứng hợp lệ theo loại đầu vào."""
    if moc is None:
        return False
    if loai == "anh":
        if isinstance(moc, str):
            return bool(MAU_LUOI_3X3.match(moc.strip().upper()))
        if isinstance(moc, (list, tuple)):
            if len(moc) == 0:
                return False
            if len(moc) == 2 and all(_la_so_thuc(v) for v in moc):
                return 0.0 <= float(moc[0]) <= 1.0 and 0.0 <= float(moc[1]) <= 1.0
            if len(moc) == 4 and all(_la_so_thuc(v) for v in moc):
                return _kiem_hop_01(moc)
            return all(kiem_tra_moc(x, loai="anh") for x in moc)
        if isinstance(moc, dict):
            if not moc:
                return False
            if "x" in moc and "y" in moc:
                if not (_la_so_thuc(moc["x"]) and _la_so_thuc(moc["y"])):
                    return False
                return 0.0 <= float(moc["x"]) <= 1.0 and 0.0 <= float(moc["y"]) <= 1.0
            if "vung" in moc:
                return kiem_tra_moc(moc["vung"], loai="anh")
            if "luoi" in moc:
                return kiem_tra_moc(moc["luoi"], loai="anh")
            if "hop" in moc:
                return _kiem_hop_01(moc["hop"])
            if "xy" in moc and isinstance(moc["xy"], (list, tuple)) and len(moc["xy"]) == 2:
                return kiem_tra_moc(moc["xy"], loai="anh")
            return False
        return False

    if isinstance(moc, str):
        return bool(moc.strip())
    if isinstance(moc, (list, dict)):
        return len(moc) > 0
    return False


def moc_sang_vung_luoi(moc: Any) -> str:
    """Suy ra mã ô lưới 3x3 đại diện từ mốc ảnh."""
    if isinstance(moc, str) and MAU_LUOI_3X3.match(moc.strip().upper()):
        return moc.strip().upper()
    if isinstance(moc, dict):
        if "x" in moc and "y" in moc and _la_so_thuc(moc["x"]) and _la_so_thuc(moc["y"]):
            return xy_sang_luoi(float(moc["x"]), float(moc["y"]))
        if "vung" in moc:
            return moc_sang_vung_luoi(moc["vung"])
        if "luoi" in moc:
            return moc_sang_vung_luoi(moc["luoi"])
        if "hop" in moc and _kiem_hop_01(moc["hop"]):
            x0, y0, x1, y1 = [float(v) for v in moc["hop"]]
            return xy_sang_luoi(0.5 * (x0 + x1), 0.5 * (y0 + y1))
        if "xy" in moc and isinstance(moc["xy"], (list, tuple)) and len(moc["xy"]) == 2:
            return moc_sang_vung_luoi(moc["xy"])
    if isinstance(moc, (list, tuple)):
        if len(moc) == 2 and all(_la_so_thuc(v) for v in moc):
            return xy_sang_luoi(float(moc[0]), float(moc[1]))
        if len(moc) == 4 and _kiem_hop_01(moc):
            x0, y0, x1, y1 = [float(v) for v in moc]
            return xy_sang_luoi(0.5 * (x0 + x1), 0.5 * (y0 + y1))
        cac_o = [moc_sang_vung_luoi(x) for x in moc]
        cac_o = [o for o in cac_o if o]
        return ",".join(cac_o)
    return ""


def dinh_dang_moc(moc: Any) -> str:
    """Định dạng mốc dễ đọc cho `doc.md`, ví dụ: `x=0.42, y=0.31 / ô A2` hoặc `ô B2`."""
    if moc is None or moc == "" or moc == {} or moc == []:
        return ""
    if isinstance(moc, str):
        s = moc.strip().upper()
        return f"ô {s}" if MAU_LUOI_3X3.match(s) else moc.strip()
    if isinstance(moc, dict):
        if "x" in moc and "y" in moc and _la_so_thuc(moc["x"]) and _la_so_thuc(moc["y"]):
            fx, fy = float(moc["x"]), float(moc["y"])
            return f"x={fx:.2f}, y={fy:.2f} / ô {xy_sang_luoi(fx, fy)}"
        if "vung" in moc:
            return dinh_dang_moc(moc["vung"])
        if "luoi" in moc:
            return dinh_dang_moc(moc["luoi"])
        if "hop" in moc and _kiem_hop_01(moc["hop"]):
            x0, y0, x1, y1 = [float(v) for v in moc["hop"]]
            o_tb = xy_sang_luoi(0.5 * (x0 + x1), 0.5 * (y0 + y1))
            return f"hop=[{x0:.2f}, {y0:.2f}, {x1:.2f}, {y1:.2f}] / ô {o_tb}"
        if "xy" in moc and isinstance(moc["xy"], (list, tuple)) and len(moc["xy"]) == 2:
            return dinh_dang_moc({"x": moc["xy"][0], "y": moc["xy"][1]})
        return json.dumps(moc, ensure_ascii=False)
    if isinstance(moc, (list, tuple)):
        if len(moc) == 2 and all(_la_so_thuc(v) for v in moc):
            return dinh_dang_moc({"x": moc[0], "y": moc[1]})
        if len(moc) == 4 and _kiem_hop_01(moc):
            return dinh_dang_moc({"hop": list(moc)})
        return ", ".join(dinh_dang_moc(x) for x in moc)
    return str(moc)


def _tai_schema_the() -> dict[str, Any]:
    global _CACHE_SCHEMA_THE
    if _CACHE_SCHEMA_THE is None:
        if DUONG_DAN_SCHEMA_THE.is_file():
            _CACHE_SCHEMA_THE = doc_json(DUONG_DAN_SCHEMA_THE)
        else:
            _CACHE_SCHEMA_THE = {"required": list(TRUONG_BAT_BUOC_THE)}
    return _CACHE_SCHEMA_THE


def kiem_tra_the_thu_phap(the: Any, loai: str = "anh") -> list[str]:
    """Kiểm tra 1 thẻ thủ pháp theo `references/the-thu-phap.schema.json`. Trả về danh sách lỗi (rỗng nếu hợp lệ)."""
    if not isinstance(the, dict):
        return ["Thẻ thủ pháp phải là object JSON."]

    schema = _tai_schema_the()
    ds_bat_buoc = tuple(schema.get("required") or TRUONG_BAT_BUOC_THE)
    ds_loi: list[str] = []

    for truong in ds_bat_buoc:
        if truong not in the:
            ds_loi.append(f"Thiếu trường bắt buộc '{truong}'.")
            continue
        gt = the[truong]
        if truong == "moc":
            hop_kieu_moc = (
                (isinstance(gt, str) and len(gt.strip()) >= 1)
                or (isinstance(gt, list) and len(gt) >= 1)
                or (isinstance(gt, dict) and len(gt) >= 1)
            )
            if not hop_kieu_moc or not kiem_tra_moc(gt, loai=loai):
                ds_loi.append(f"Trường 'moc' của thẻ không hợp lệ: {gt!r}.")
        else:
            if not isinstance(gt, str) or not gt.strip():
                ds_loi.append(f"Trường '{truong}' phải là chuỗi không rỗng.")

    if "id" in the and (not isinstance(the["id"], str) or not the["id"].strip()):
        ds_loi.append("Trường tuỳ chọn 'id' phải là chuỗi không rỗng.")
    if "tu_khoa" in the:
        tk = the["tu_khoa"]
        if not isinstance(tk, list) or not all(isinstance(x, str) and x.strip() for x in tk):
            ds_loi.append("Trường tuỳ chọn 'tu_khoa' phải là mảng các chuỗi không rỗng.")
    if "chi_so_do" in the and not isinstance(the["chi_so_do"], dict):
        ds_loi.append("Trường tuỳ chọn 'chi_so_do' phải là object.")

    return ds_loi


def tim_ban_do(dir_ra: str | Path) -> list[Path]:
    """Tìm danh sách các file `do.json` trong thư mục đầu ra (1 mục hoặc nhiều mục con)."""
    goc = Path(dir_ra)
    if not goc.exists():
        return []
    truc_tiep = goc / "do.json"
    if truc_tiep.is_file():
        return [truc_tiep]
    return [p / "do.json" for p in sorted(goc.iterdir()) if p.is_dir() and (p / "do.json").is_file()]


# ---------------- Lệnh `tom` -------------------------------------------------------------------------

def tom_mot_muc(d: dict[str, Any], ten_mac_dinh: str = "") -> str:
    """Tạo 1 dòng tóm tắt ngắn gọn cho 1 bản ghi `do.json`."""
    if "tong" in d and "mau" in d and "bo_cuc" in d:
        ten = d.get("anh") or ten_mac_dinh or "khong_ro"
        tong = d.get("tong") or {}
        kieu = tong.get("kieu", "?")
        tb = float(tong.get("trung_binh", 0.0))
        lech = float(tong.get("do_lech", 0.0))

        ba_mau = (d.get("mau") or [])[:3]
        chuoi_mau = ", ".join(f"{m['hex']} ({float(m['ti_le']) * 100:.0f}%)" for m in ba_mau)

        bc = d.get("bo_cuc") or {}
        khop = str(bc.get("khop_nhat", "?"))
        diem_khop = float(bc.get(khop, 0.0)) if khop in bc else 0.0

        hm = d.get("hut_mat") or []
        chuoi_hm = ", ".join(
            f"({float(p['x']):.2f}, {float(p['y']):.2f}) [{xy_sang_luoi(float(p['x']), float(p['y']))}]"
            for p in hm
        ) or "khong_co"

        return (
            f"- `{ten}` | tông: {kieu} (TB {tb:.2f}, lệch {lech:.2f}) "
            f"| 3 màu: {chuoi_mau} | bố cục: {khop} ({diem_khop:.2f}) | hút mắt: {chuoi_hm}"
        )

    ten = d.get("ten") or d.get("anh") or ten_mac_dinh or "muc"
    loai = d.get("loai", "rea")
    return f"- `{ten}` | loại: {loai} | phiên bản: {d.get('phien_ban', PHIEN_BAN)}"


def chay_tom(dir_ra: str | Path) -> Path:
    """Dựng thư mục ra chung (`cau-truc.md`, `nhip.md`, `nguyen-lieu.md`, `ve-dep.md`, `thu-phap/`,
    `ve-nguoc/README.md`) và ghi `<dir_ra>/tom.md` ≤40 dòng có mục 'Máy sai cần sửa'.
    """
    goc = Path(dir_ra)
    ds_do = tim_ban_do(goc)
    if not ds_do:
        raise FileNotFoundError(f"Không tìm thấy do.json nào trong: {goc}")

    return anh_tom.chay_tom_day_du(
        goc=goc,
        ds_do=ds_do,
        doc_json_fn=doc_json,
        xy_sang_luoi=xy_sang_luoi,
        dinh_dang_moc=dinh_dang_moc,
        tom_mot_muc_fn=tom_mot_muc,
    )


# ---------------- Lệnh `viec-doc` --------------------------------------------------------------------

def la_dap_an_da_dien(dap_an: dict[str, Any]) -> bool:
    """Xác định một file `dap_an.json` đã được người đọc/agent điền hay vẫn chỉ là mẫu rỗng."""
    if not isinstance(dap_an, dict):
        return False
    tra_loi = dap_an.get("tra_loi")
    co_gia_tri = False
    if isinstance(tra_loi, list):
        co_gia_tri = any(isinstance(x, dict) and str(x.get("gia_tri") or "").strip() for x in tra_loi)
    elif isinstance(tra_loi, dict):
        co_gia_tri = any(
            (isinstance(v, dict) and str(v.get("gia_tri") or "").strip())
            or (isinstance(v, str) and v.strip())
            for v in tra_loi.values()
        )

    co_the = bool(dap_an.get("the_de_xuat"))
    co_khoa_do = any(k in dap_an for k in anh_doc.KHOA_DO_ANH)

    if dap_an.get("trang_thai") == "chua_dien" and not (co_gia_tri or co_the or co_khoa_do):
        return False
    return bool(co_gia_tri or co_the or co_khoa_do or dap_an.get("trang_thai") == "da_dien")


def co_dap_an_da_dien(dir_ra: str | Path) -> bool:
    """Kiểm tra trong `dir_ra` có ít nhất 1 mục đã điền `dap_an.json` hay không."""
    for p_do in tim_ban_do(dir_ra):
        p_dap = p_do.parent / "dap_an.json"
        if p_dap.is_file():
            try:
                if la_dap_an_da_dien(doc_json(p_dap)):
                    return True
            except Exception:
                return True
    return False


def _tao_dap_an_mau_rong(ten_anh: str, ds_cau_hoi: list[dict[str, Any]]) -> dict[str, Any]:
    tra_loi = []
    for ch in ds_cau_hoi:
        muc_tl: dict[str, Any] = {
            "ma": ch["ma"],
            "gia_tri": "",
            "ghi_chu": "",
        }
        if ch.get("can_moc"):
            muc_tl["moc"] = {}
        tra_loi.append(muc_tl)
    return {
        "anh": ten_anh,
        "trang_thai": "chua_dien",
        "nguoi_doc": "",
        "tra_loi": tra_loi,
        "luat_khop": [],
        "the_de_xuat": [],
    }


def chay_viec_doc(dir_ra: str | Path, tu_vung_path: str | Path) -> dict[str, Any]:
    """Sinh `<anh>/viec_doc.json`, mẫu `<anh>/dap_an.json` (nếu chưa có) và `<dir_ra>/VIEC-DOC.md`."""
    goc = Path(dir_ra)
    ds_do = tim_ban_do(goc)
    if not ds_do:
        raise FileNotFoundError(f"Không tìm thấy do.json nào trong: {goc}")

    tu_vung = doc_yaml(tu_vung_path)
    loai = str(tu_vung.get("loai", "anh"))
    ds_cau_hoi = [
        {
            "ma": str(t["ma"]),
            "cau_hoi": str(t.get("cau_hoi", "")),
            "gia_tri": [str(v) for v in (t.get("gia_tri") or [])],
            "can_moc": bool(t.get("can_moc", False)),
        }
        for t in (tu_vung.get("truc") or [])
    ]

    dong_bang_md: list[str] = []
    so_viec = 0
    so_dap_an_moi = 0
    dd_luat_dop = anh_doc.dinh_dang_duong_dan(DUONG_DAN_LUAT_DOP)

    for idx, p_do in enumerate(ds_do, start=1):
        thu_muc_muc = p_do.parent
        do_data = doc_json(p_do)
        ten_anh = str(do_data.get("anh") or do_data.get("ten") or thu_muc_muc.name)

        if anh_doc.la_ban_do_anh(do_data):
            goi_y_do = anh_doc.trich_goi_y_do_anh(do_data, xy_sang_luoi)
            duong_dan_goc = anh_doc.tim_anh_goc(thu_muc_muc, ten_anh, goc)
        else:
            goi_y_do = {k: v for k, v in do_data.items() if k not in ("anh", "ten")}
            duong_dan_goc = ten_anh

        p_do_png = thu_muc_muc / "do.png"
        p_hm_png = thu_muc_muc / "hut_mat.png"
        p_lop_png = thu_muc_muc / "lop.png"

        viec_muc = {
            "anh": ten_anh,
            "thu_muc": thu_muc_muc.name,
            "loai": loai,
            "phien_ban": PHIEN_BAN,
            "anh_goc": duong_dan_goc,
            "do_png": anh_doc.dinh_dang_duong_dan(p_do_png) if p_do_png.is_file() else "",
            "hut_mat_png": anh_doc.dinh_dang_duong_dan(p_hm_png) if p_hm_png.is_file() else "",
            "lop_png": anh_doc.dinh_dang_duong_dan(p_lop_png) if p_lop_png.is_file() else "",
            "tai_lieu_luat_dop": dd_luat_dop,
            "huong_dan_luat_dop": (
                f"Đối chiếu {dd_luat_dop}: gắn mã luật khớp vào đầu ghi_chu (vd '[AS-03] ...') "
                "và điền khoá gốc 'luat_khop' dạng [{'ma': 'AS-03', 'vi_sao': '...', 'moc': {...}}] tối thiểu ≥3 luật mỗi ảnh."
            ),
            "goi_y_do": goi_y_do,
            "cau_hoi": ds_cau_hoi,
        }
        ghi_json(thu_muc_muc / "viec_doc.json", viec_muc)
        so_viec += 1

        p_dap = thu_muc_muc / "dap_an.json"
        if not p_dap.is_file():
            ghi_json(p_dap, _tao_dap_an_mau_rong(ten_anh, ds_cau_hoi))
            so_dap_an_moi += 1
            trang_thai_str = "chua_dien"
        else:
            try:
                trang_thai_str = "da_dien" if la_dap_an_da_dien(doc_json(p_dap)) else "chua_dien"
            except Exception:
                trang_thai_str = "loi_json"

        dd_do_png = anh_doc.dinh_dang_duong_dan(p_do_png) if p_do_png.is_file() else f"{thu_muc_muc.name}/do.png"
        dd_dap = anh_doc.dinh_dang_duong_dan(p_dap)
        dong_bang_md.append(
            f"| {idx} | `{thu_muc_muc.name}` | `{duong_dan_goc}` | `{dd_do_png}` | `{dd_dap}` | `{trang_thai_str}` |"
        )

    noi_dung_md = [
        "# VIỆC ĐỌC (`rea-anh`)",
        "",
        "## 1. Hướng dẫn điền `dap_an.json` cho từng ảnh",
        "1. Mở đồng thời **ảnh gốc**, **`do.png`** (lưới 1/3 + điểm hút mắt + 6 màu) và **`viec_doc.json`** của từng ảnh.",
        "2. Mở `<anh>/dap_an.json`, đổi `\"trang_thai\"` thành `\"da_dien\"`, ghi tên `\"nguoi_doc\"`.",
        "3. Trong mảng `\"tra_loi\"`, chọn `\"gia_tri\"` thuộc danh sách nhãn đóng trong `viec_doc.json` (`tu-vung/anh.yaml`) và viết `\"ghi_chu\"` ngắn gọn dựa trên bằng chứng thị giác.",
        f"4. Đối chiếu **`{dd_luat_dop}`** (`references/luat-dop.md`): gắn mã luật vào đầu `\"ghi_chu\"` của trục khớp (ví dụ `\"[AS-03] ...\"`) và điền khoá gốc `\"luat_khop\"` dạng `[{{\"ma\", \"vi_sao\", \"moc\"}}]` với **tối thiểu ≥3 luật mỗi ảnh**.",
        "5. Với mọi trục có `can_moc: true`, **bắt buộc** điền `\"moc\"` theo 1 trong 3 dạng:",
        "   - Toạ độ điểm: `{\"x\": 0.42, \"y\": 0.31}` (`0..1`, gốc trái-trên)",
        "   - Ô lưới 3×3: `{\"vung\": \"B2\"}` (`A1..C3` hoặc dải `A2-B2`)",
        "   - Hộp giới hạn: `{\"hop\": [0.20, 0.15, 0.65, 0.70]}`",
        "6. Đề xuất tối thiểu 1 thẻ trong `\"the_de_xuat\"` đúng schema `the-thu-phap` (`ten, loai, moc, mo_ta, cach_lam, khi_dung, nguon`).",
        "7. **Không ghi đè số đo máy**: mọi khoá trùng tên trường đo (`mau, tong, hut_mat, bo_cuc, do_sau, kich_thuoc`) sẽ không sửa `do.json` mà bị chuyển vào `xung_dot`.",
        f"8. Sau khi điền xong, chạy: `python linhx-rea/scripts/rea_core.py ap {anh_doc.dinh_dang_duong_dan(goc)}`.",
        "",
        "## 2. Mẫu định dạng `dap_an.json`",
        "```json",
        '{',
        '  "anh": "ten_anh.jpg",',
        '  "trang_thai": "da_dien",',
        '  "nguoi_doc": "agy",',
        '  "tra_loi": [',
        '    {"ma": "chu_the_chinh", "gia_tri": "chan_dung_nguoi", "ghi_chu": "[BC-01] ...", "moc": {"x": 0.47, "y": 0.24}},',
        '    {"ma": "anh_sang_cung_mem", "gia_tri": "mem_khuech_tan", "ghi_chu": "[AS-03] ..."}',
        '  ],',
        '  "luat_khop": [',
        '    {"ma": "AS-03", "vi_sao": "...", "moc": {"x": 0.47, "y": 0.24}},',
        '    {"ma": "BC-01", "vi_sao": "...", "moc": {"vung": "B2"}},',
        '    {"ma": "MAU-03", "vi_sao": "...", "moc": {"hop": [0.20, 0.15, 0.65, 0.70]}}',
        '  ],',
        '  "the_de_xuat": [',
        '    {"ten": "...", "loai": "mau_sac", "moc": {"vung": "A2"}, "mo_ta": "...", "cach_lam": "...", "khi_dung": "...", "nguon": "ten_anh.jpg"}',
        '  ]',
        '}',
        "```",
        "",
        "## 3. Danh sách ảnh cần đọc",
        "| # | Thư mục ảnh | Ảnh gốc | Ảnh đo (`do.png`) | File `dap_an.json` | Trạng thái |",
        "|---|---|---|---|---|---|",
        *dong_bang_md,
        "",
    ]

    p_viec_md = goc / "VIEC-DOC.md"
    p_viec_md.write_text("\n".join(noi_dung_md), encoding="utf-8")

    return {
        "so_muc": so_viec,
        "dap_an_moi": so_dap_an_moi,
        "viec_doc_md": p_viec_md,
    }


# ---------------- Lệnh `ap` --------------------------------------------------------------------------

def _tai_ban_truc(thu_muc_muc: Path, loai_mac_dinh: str = "anh", tu_vung_path: str | Path | None = None) -> tuple[str, dict[str, dict[str, Any]]]:
    p_vd = thu_muc_muc / "viec_doc.json"
    if p_vd.is_file():
        vd = doc_json(p_vd)
        loai = str(vd.get("loai", loai_mac_dinh))
        ds_ch = vd.get("cau_hoi") or vd.get("truc") or []
        return loai, {str(t["ma"]): t for t in ds_ch if isinstance(t, dict) and "ma" in t}

    ung_vien_yaml = Path(tu_vung_path) if tu_vung_path else DUONG_DAN_TU_VUNG_ANH
    if ung_vien_yaml.is_file():
        tv = doc_yaml(ung_vien_yaml)
        loai = str(tv.get("loai", loai_mac_dinh))
        ds_ch = tv.get("truc") or []
        return loai, {str(t["ma"]): t for t in ds_ch if isinstance(t, dict) and "ma" in t}

    return loai_mac_dinh, {}


def _chuan_hoa_danh_sach_tra_loi(raw_tra_loi: Any) -> list[dict[str, Any]]:
    if isinstance(raw_tra_loi, list):
        return [x for x in raw_tra_loi if isinstance(x, dict)]
    if isinstance(raw_tra_loi, dict):
        ket_qua = []
        for ma, v in raw_tra_loi.items():
            if isinstance(v, dict):
                ket_qua.append({"ma": str(ma), **v})
            else:
                ket_qua.append({"ma": str(ma), "gia_tri": v})
        return ket_qua
    return []


def _viet_doc_md(
    p_doc_md: Path,
    ten_anh: str,
    nguoi_doc: str,
    ds_tra_loi_sach: list[dict[str, Any]],
    do_goc: dict[str, Any],
    xung_dot: list[dict[str, Any]],
    canh_bao: list[str],
    ds_luat_khop: list[dict[str, Any]] | None = None,
) -> Path:
    cac_dong: list[str] = [
        f"# Đọc ảnh: `{ten_anh}`",
        "",
        f"Người đọc: `{nguoi_doc or 'khong_ro'}`",
        "",
        "## Nhận xét theo trục",
    ]

    if ds_tra_loi_sach:
        for tl in ds_tra_loi_sach:
            ma = tl["ma"]
            gia_tri = tl["gia_tri"]
            chuoi_moc = dinh_dang_moc(tl.get("moc"))
            phan_moc = f" (mốc: {chuoi_moc})" if chuoi_moc else ""
            ghi_chu = str(tl.get("ghi_chu") or "").strip()
            phan_gc = f" — {ghi_chu}" if ghi_chu else ""
            cac_dong.append(f"- **{ma}**: {gia_tri}{phan_moc}{phan_gc}")
    else:
        cac_dong.append("- *(Chưa có câu trả lời theo trục)*")

    cac_dong.extend(["", "## Luật DoP khớp"])
    if ds_luat_khop:
        for lk in ds_luat_khop:
            ma_luat = str(lk.get("ma") or "").strip()
            vi_sao = str(lk.get("vi_sao") or "").strip()
            chuoi_moc_lk = dinh_dang_moc(lk.get("moc"))
            phan_moc_lk = f" (mốc: {chuoi_moc_lk})" if chuoi_moc_lk else ""
            phan_vs = f" — {vi_sao}" if vi_sao else ""
            cac_dong.append(f"- **`{ma_luat}`**{phan_moc_lk}{phan_vs}")
    else:
        cac_dong.append("- *(Chưa ghi nhận `luat_khop`)*")

    cac_dong.extend(["", "## Số đo máy"])
    if anh_doc.la_ban_do_anh(do_goc):
        cac_dong.extend(anh_doc.tom_so_do_may_md(do_goc, xy_sang_luoi))
    else:
        cac_dong.append(tom_mot_muc(do_goc, ten_mac_dinh=ten_anh))

    cac_dong.extend(["", "## Chỗ máy và người đọc khác nhau"])
    if not xung_dot and not canh_bao:
        cac_dong.append("- Không có xung đột hay cảnh báo giữa số đo máy và nhận định người đọc.")
    else:
        for xd in xung_dot:
            cac_dong.append(f"- **[Xung đột — {xd.get('loai', 'khac')}]** {xd.get('mo_ta', '')}")
        for cb in canh_bao:
            cac_dong.append(f"- **[Cảnh báo]** {cb}")

    cac_dong.append("")
    p_doc_md.write_text("\n".join(cac_dong), encoding="utf-8")
    return p_doc_md


def chay_ap(dir_ra: str | Path, tu_vung_path: str | Path | None = None) -> dict[str, Any]:
    """Áp `dap_an.json` đã điền cho từng mục trong `dir_ra`:
    - Giữ nguyên tuyệt đối `do.json` (KHÔNG ĐÈ SỐ ĐO).
    - Báo lỗi tường minh nếu trục `can_moc: true` thiếu hoặc sai mốc.
    - Giữ giá trị ngoài danh sách nhưng ghi vào `canh_bao`.
    - Ghi nhận xung đột khoá đo và xung đột `duong_dan_mat` không chứa `hut_mat` vào `xung_dot`.
    - Xuất `<anh>/doc.json` và `<anh>/doc.md`.
    """
    goc = Path(dir_ra)
    ds_do = tim_ban_do(goc)
    if not ds_do:
        raise FileNotFoundError(f"Không tìm thấy do.json nào trong: {goc}")

    da_ap: list[str] = []
    bo_qua: list[str] = []
    tong_loi: list[str] = []
    tong_canh_bao: list[str] = []
    tong_xung_dot: list[dict[str, Any]] = []

    for p_do in ds_do:
        thu_muc_muc = p_do.parent
        ten_muc = thu_muc_muc.name
        p_dap = thu_muc_muc / "dap_an.json"
        if not p_dap.is_file():
            bo_qua.append(ten_muc)
            continue

        dap_an = doc_json(p_dap)
        if not la_dap_an_da_dien(dap_an):
            bo_qua.append(ten_muc)
            continue

        do_goc = doc_json(p_do)
        ban_sao_do = copy.deepcopy(do_goc)
        la_anh = anh_doc.la_ban_do_anh(do_goc)
        loai, ban_truc = _tai_ban_truc(thu_muc_muc, loai_mac_dinh="anh" if la_anh else "rea", tu_vung_path=tu_vung_path)

        loi_muc: list[str] = []
        canh_bao_muc: list[str] = []
        xung_dot_muc: list[dict[str, Any]] = []

        # 1. Bảo vệ số đo máy: kiểm tra mọi khoá trùng khoá đo ở cấp cao nhất của dap_an.json
        tap_khoa_do = set(anh_doc.KHOA_DO_ANH) | {"do"}
        for khoa in tap_khoa_do:
            if khoa in dap_an:
                xung_dot_muc.append({
                    "loai": "trung_khoa_do",
                    "khoa": khoa,
                    "so_do_may": ban_sao_do.get(khoa),
                    "y_kien_nguoi_doc": dap_an[khoa],
                    "mo_ta": (
                        f"dap_an.json có khoá '{khoa}' trùng trường số đo của máy; "
                        f"giữ nguyên số đo máy trong 'do', ghi ý kiến người đọc vào xung_dot."
                    ),
                })

        # 2. Kiểm tra từng câu trả lời theo trục
        ds_tra_loi_raw = _chuan_hoa_danh_sach_tra_loi(dap_an.get("tra_loi"))
        ds_tra_loi_sach: list[dict[str, Any]] = []

        for muc_tl in ds_tra_loi_raw:
            ma = str(muc_tl.get("ma") or "").strip()
            if not ma:
                continue

            gt_raw = muc_tl.get("gia_tri")
            moc_raw = muc_tl.get("moc")
            ghi_chu = str(muc_tl.get("ghi_chu") or "").strip()

            # Trường hợp người đọc nhét khoá số đo máy (vd: tong, hut_mat, bo_cuc, do_sau, kich_thuoc) vào tra_loi
            # Lưu ý: "mau" trong `tu-vung/anh.yaml` là trục Bruce Block hợp lệ khi gia_tri là nhãn chuỗi!
            la_ghi_de_mau = ma == "mau" and not isinstance(gt_raw, str)
            if (ma in tap_khoa_do and ma not in ban_truc) or la_ghi_de_mau:
                xung_dot_muc.append({
                    "loai": "trung_khoa_do",
                    "khoa": ma,
                    "so_do_may": ban_sao_do.get(ma),
                    "y_kien_nguoi_doc": gt_raw if gt_raw is not None else muc_tl,
                    "mo_ta": (
                        f"Mục trả lời '{ma}' trùng trường số đo của máy; "
                        f"giữ nguyên số đo máy, ghi ý kiến người đọc vào xung_dot."
                    ),
                })
                continue

            gia_tri = str(gt_raw if gt_raw is not None else "").strip()
            thong_tin_truc = ban_truc.get(ma)

            # Nếu mục còn trống hoàn toàn (cả gia_tri lẫn moc rỗng trong bản điền dở), cảnh báo chưa điền
            moc_rong = moc_raw is None or moc_raw == "" or moc_raw == {} or moc_raw == []
            if not gia_tri and moc_rong:
                canh_bao_muc.append(f"Trục '{ma}' chưa có giá trị trả lời.")
                continue

            can_moc = bool(thong_tin_truc.get("can_moc", False)) if thong_tin_truc else False
            if can_moc and not kiem_tra_moc(moc_raw, loai=loai):
                loi_muc.append(
                    f"{ten_muc}: trục '{ma}' bắt buộc có mốc (can_moc=true) nhưng thiếu hoặc mốc không hợp lệ ({moc_raw!r})."
                )
                continue

            # Nếu trục không bắt buộc mốc nhưng người đọc có điền mốc khác rỗng thì vẫn kiểm định dạng
            co_moc_hop_le = (not moc_rong) and kiem_tra_moc(moc_raw, loai=loai)
            if (not can_moc) and (not moc_rong) and (not co_moc_hop_le):
                canh_bao_muc.append(f"Trục '{ma}': mốc tuỳ chọn không đúng định dạng chuẩn ({moc_raw!r}).")

            hop_tu_vung = True
            if thong_tin_truc is None:
                hop_tu_vung = False
                canh_bao_muc.append(f"Trục '{ma}' không nằm trong từ vựng chuẩn, vẫn giữ nguyên.")
            else:
                ds_cho_phep = [str(v) for v in (thong_tin_truc.get("gia_tri") or [])]
                if ds_cho_phep and gia_tri not in ds_cho_phep:
                    hop_tu_vung = False
                    canh_bao_muc.append(
                        f"Trục '{ma}': giá trị '{gia_tri}' nằm ngoài danh sách cho phép {ds_cho_phep}, vẫn giữ nguyên."
                    )

            # Đối chiếu riêng cho ảnh: `duong_dan_mat` không chứa điểm hút mắt nào của máy -> `xung_dot`
            if la_anh and ma == "duong_dan_mat" and co_moc_hop_le:
                ds_hm = ban_sao_do.get("hut_mat") or []
                if not anh_doc.moc_chua_hut_mat(moc_raw, ds_hm, xy_sang_luoi):
                    chuoi_hm_may = ", ".join(
                        f"({float(p['x']):.2f}, {float(p['y']):.2f}) [ô {xy_sang_luoi(float(p['x']), float(p['y']))}]"
                        for p in ds_hm
                    )
                    xung_dot_muc.append({
                        "loai": "duong_dan_mat_lech_hut_mat",
                        "truc": "duong_dan_mat",
                        "moc_nguoi_doc": moc_raw,
                        "hut_mat_may": ds_hm,
                        "mo_ta": (
                            f"Người đọc chỉ 'duong_dan_mat' vào ({dinh_dang_moc(moc_raw)}), "
                            f"vùng này không chứa điểm hút mắt nào của máy ({chuoi_hm_may})."
                        ),
                    })

            ban_ghi_tl: dict[str, Any] = {
                "ma": ma,
                "gia_tri": gia_tri,
                "ghi_chu": ghi_chu,
                "hop_tu_vung": hop_tu_vung,
            }
            if co_moc_hop_le or not moc_rong:
                ban_ghi_tl["moc"] = moc_raw
                vung_luoi = moc_sang_vung_luoi(moc_raw)
                if vung_luoi:
                    ban_ghi_tl["vung_luoi"] = vung_luoi
            ds_tra_loi_sach.append(ban_ghi_tl)

        # 3. Kiểm tra luật DoP khớp (`luat_khop`: [{ma, vi_sao, moc}])
        ds_luat_khop_sach: list[dict[str, Any]] = []
        raw_luat_khop = dap_an.get("luat_khop")
        if isinstance(raw_luat_khop, list):
            for idx_lk, lk in enumerate(raw_luat_khop, start=1):
                if not isinstance(lk, dict):
                    canh_bao_muc.append(f"luat_khop #{idx_lk} không phải object JSON.")
                    continue
                ma_lk = str(lk.get("ma") or "").strip()
                if not ma_lk:
                    continue
                vi_sao_lk = str(lk.get("vi_sao") or "").strip()
                moc_lk = lk.get("moc")
                ban_ghi_lk: dict[str, Any] = {
                    "ma": ma_lk,
                    "vi_sao": vi_sao_lk,
                }
                moc_lk_rong = moc_lk is None or moc_lk == "" or moc_lk == {} or moc_lk == []
                if not moc_lk_rong:
                    if not kiem_tra_moc(moc_lk, loai=loai):
                        canh_bao_muc.append(f"luat_khop '{ma_lk}': mốc không đúng định dạng chuẩn ({moc_lk!r}).")
                    ban_ghi_lk["moc"] = moc_lk
                    vl_lk = moc_sang_vung_luoi(moc_lk)
                    if vl_lk:
                        ban_ghi_lk["vung_luoi"] = vl_lk
                ds_luat_khop_sach.append(ban_ghi_lk)

        # 4. Kiểm tra thẻ đề xuất (theo schema the-thu-phap)
        ds_the_sach: list[dict[str, Any]] = []
        for idx_t, the in enumerate(dap_an.get("the_de_xuat") or [], start=1):
            loi_the = kiem_tra_the_thu_phap(the, loai=loai)
            if loi_the:
                canh_bao_muc.append(f"Thẻ đề xuất #{idx_t} chưa đạt schema: {'; '.join(loi_the)}")
            if isinstance(the, dict):
                ds_the_sach.append(the)

        if loi_muc:
            tong_loi.extend(loi_muc)
            continue

        ten_anh = str(ban_sao_do.get("anh") or dap_an.get("anh") or ten_muc)
        nguoi_doc = str(dap_an.get("nguoi_doc") or "agent").strip()

        doc_ket_qua = {
            "do": ban_sao_do,
            "doc": {
                "anh": ten_anh,
                "nguoi_doc": nguoi_doc,
                "tra_loi": ds_tra_loi_sach,
                "luat_khop": ds_luat_khop_sach,
                "the_de_xuat": ds_the_sach,
            },
            "luat_khop": ds_luat_khop_sach,
            "xung_dot": xung_dot_muc,
            "canh_bao": canh_bao_muc,
        }
        ghi_json(thu_muc_muc / "doc.json", doc_ket_qua)
        _viet_doc_md(
            thu_muc_muc / "doc.md",
            ten_anh=ten_anh,
            nguoi_doc=nguoi_doc,
            ds_tra_loi_sach=ds_tra_loi_sach,
            do_goc=ban_sao_do,
            xung_dot=xung_dot_muc,
            canh_bao=canh_bao_muc,
            ds_luat_khop=ds_luat_khop_sach,
        )

        da_ap.append(ten_muc)
        tong_canh_bao.extend(f"{ten_muc}: {cb}" for cb in canh_bao_muc)
        tong_xung_dot.extend({"muc": ten_muc, **xd} for xd in xung_dot_muc)

    return {
        "da_ap": da_ap,
        "bo_qua": bo_qua,
        "loi": tong_loi,
        "canh_bao": tong_canh_bao,
        "xung_dot": tong_xung_dot,
    }


# ---------------- Lệnh `the` (rút thẻ thủ pháp chuẩn schema) -----------------------------------------

def _lam_sach_o_md(val: str) -> str:
    return re.sub(r"\s+", " ", val.replace("|", "\\|")).strip()


def chay_the(dir_ra: str | Path, loai: str = "anh") -> dict[str, Any]:
    """Gom `the_de_xuat` từ `doc.json` của mọi mục trong `dir_ra`, kiểm schema `the-thu-phap.schema.json`:
    - Thẻ đúng -> `<dir_ra>/thu-phap/thu-phap.jsonl` + `<dir_ra>/thu-phap/README.md` (bảng ten | loai | moc | khi_dung).
    - Thẻ sai  -> `<dir_ra>/thu-phap/the-loi.jsonl` (và `<dir_ra>/the-loi.jsonl`).
    - Mỗi ảnh phải có ≥1 thẻ đúng schema; trả danh sách `anh_thieu_the` để báo.
    """
    goc = Path(dir_ra)
    ds_do = tim_ban_do(goc)
    if ds_do:
        ds_muc = [p.parent for p in ds_do]
    elif (goc / "doc.json").is_file():
        ds_muc = [goc]
    else:
        ds_muc = [p for p in sorted(goc.iterdir()) if p.is_dir() and (p / "doc.json").is_file()] if goc.is_dir() else []

    if not ds_muc:
        raise FileNotFoundError(f"Không tìm thấy mục nào có do.json/doc.json trong: {goc}")

    ds_hop_le: list[dict[str, Any]] = []
    ds_the_loi: list[dict[str, Any]] = []
    anh_thieu_the: list[str] = []

    for thu_muc in ds_muc:
        p_doc = thu_muc / "doc.json"
        p_do = thu_muc / "do.json"
        ten_anh = thu_muc.name
        if p_do.is_file():
            ten_anh = str(doc_json(p_do).get("anh") or ten_anh)

        if not p_doc.is_file():
            anh_thieu_the.append(ten_anh)
            continue

        doc_data = doc_json(p_doc)
        phan_doc = doc_data.get("doc") if isinstance(doc_data.get("doc"), dict) else doc_data
        ten_anh = str(phan_doc.get("anh") or ten_anh)
        ds_de_xuat = phan_doc.get("the_de_xuat") or []

        so_dung_anh = 0
        for idx_t, the in enumerate(ds_de_xuat, start=1):
            loi_schema = kiem_tra_the_thu_phap(the, loai=loai)
            if loi_schema:
                ds_the_loi.append({
                    "anh": ten_anh,
                    "thu_tu": idx_t,
                    "loi": loi_schema,
                    "the": the,
                })
            else:
                ds_hop_le.append(the)
                so_dung_anh += 1

        if so_dung_anh < 1:
            anh_thieu_the.append(ten_anh)

    tp_dir = goc / "thu-phap"
    tp_dir.mkdir(parents=True, exist_ok=True)
    p_tp_jsonl = tp_dir / "thu-phap.jsonl"
    noi_dung_jsonl = "\n".join(json.dumps(t, ensure_ascii=False) for t in ds_hop_le)
    p_tp_jsonl.write_text((noi_dung_jsonl + "\n") if noi_dung_jsonl else "", encoding="utf-8")

    dong_readme = [
        "# Thẻ thủ pháp (`thu-phap`)",
        "",
        f"Tổng số thẻ hợp lệ: **{len(ds_hop_le)}** | Thẻ sai schema: **{len(ds_the_loi)}** | Ảnh thiếu thẻ: **{len(anh_thieu_the)}**.",
        "",
        "| ten | loai | moc | khi_dung |",
        "|---|---|---|---|",
    ]
    for t in ds_hop_le:
        ten_s = _lam_sach_o_md(str(t["ten"]))
        loai_s = _lam_sach_o_md(str(t["loai"]))
        moc_s = _lam_sach_o_md(dinh_dang_moc(t["moc"]))
        khi_dung_s = _lam_sach_o_md(str(t["khi_dung"]))
        dong_readme.append(f"| {ten_s} | `{loai_s}` | {moc_s} | {khi_dung_s} |")
    dong_readme.append("")
    p_readme = tp_dir / "README.md"
    p_readme.write_text("\n".join(dong_readme), encoding="utf-8")

    p_loi_tp = tp_dir / "the-loi.jsonl"
    p_loi_goc = goc / "the-loi.jsonl"
    if ds_the_loi:
        noi_dung_loi = "\n".join(json.dumps(x, ensure_ascii=False) for x in ds_the_loi) + "\n"
        p_loi_tp.write_text(noi_dung_loi, encoding="utf-8")
        p_loi_goc.write_text(noi_dung_loi, encoding="utf-8")
    else:
        for p_cu in (p_loi_tp, p_loi_goc):
            if p_cu.is_file():
                p_cu.unlink()

    return {
        "hop_le": ds_hop_le,
        "the_loi": ds_the_loi,
        "anh_thieu_the": anh_thieu_the,
        "thu_phap_jsonl": p_tp_jsonl,
        "readme_md": p_readme,
        "the_loi_jsonl": p_loi_tp,
    }


# ---------------- Lệnh `sua` (ghi nối vào `<dir_ra>/sua-sai.jsonl`, không ghi đè) --------------------

def _doc_danh_sach_sua_sai(p_sua: Path) -> list[dict[str, Any]]:
    ds_hien_co: list[dict[str, Any]] = []
    if p_sua.is_file():
        for dong in p_sua.read_text(encoding="utf-8").splitlines():
            dong = dong.strip()
            if not dong:
                continue
            try:
                ds_hien_co.append(json.loads(dong))
            except Exception:
                continue
    return ds_hien_co


def _ghi_danh_sach_sua_sai(p_sua: Path, ds_muc: list[dict[str, Any]]) -> None:
    p_sua.parent.mkdir(parents=True, exist_ok=True)
    noi_dung = "\n".join(json.dumps(x, ensure_ascii=False) for x in ds_muc)
    p_sua.write_text((noi_dung + "\n") if noi_dung else "", encoding="utf-8")


def _chuan_hoa_dir_ra_sua(dir_ra: str | Path | None) -> Path:
    if dir_ra is not None and str(dir_ra).strip():
        p = Path(dir_ra)
        if not p.is_absolute():
            ung_vien_repo = THU_MUC_SKILL.parent / p
            if ung_vien_repo.exists() and not p.exists():
                return ung_vien_repo.resolve()
        return p.resolve()
    return (THU_MUC_SKILL.parent / "thu-anh" / "ra").resolve()


def _khoa_khu_trung_muc(muc: dict[str, Any]) -> tuple[str, ...]:
    anh = str(muc.get("anh") or "").strip()
    truc = str(muc.get("truc") or "").strip()
    mo_ta = str(muc.get("mo_ta") or "").strip()
    ma_loi = str(muc.get("ma_loi") or "").strip()
    if anh or truc:
        return ("anh_truc_mota", anh, truc, mo_ta)
    if ma_loi:
        return ("ma_loi", ma_loi)
    return ("mo_ta", mo_ta)


def _ghi_noi_khu_trung(p_sua: Path, ds_them: list[dict[str, Any]], cap_nhat_he_thong: bool = False) -> list[dict[str, Any]]:
    """Ghi nối vào `p_sua`, khử trùng theo `(anh, truc, mo_ta)` (hoặc `ma_loi` cho lỗi hệ thống),
    KHÔNG BAO GIỜ xoá mục cũ đã có trong `p_sua`.
    """
    ds_ket_qua = _doc_danh_sach_sua_sai(p_sua)
    vi_tri_khoa: dict[tuple[str, ...], int] = {}
    for idx, cu in enumerate(ds_ket_qua):
        if "anh" not in cu and "truc" not in cu and "trang_thai" not in cu:
            cu["trang_thai"] = "da_sua" if cu.get("cach_sua") else "mo"
        k = _khoa_khu_trung_muc(cu)
        if k not in vi_tri_khoa:
            vi_tri_khoa[k] = idx

    for moi in ds_them:
        k = _khoa_khu_trung_muc(moi)
        if k in vi_tri_khoa:
            if cap_nhat_he_thong and k[0] != "anh_truc_mota":
                idx_cu = vi_tri_khoa[k]
                cu_goc = ds_ket_qua[idx_cu]
                ban_cap_nhat = dict(moi)
                if "thoi_gian" in cu_goc:
                    ban_cap_nhat["thoi_gian"] = cu_goc["thoi_gian"]
                ds_ket_qua[idx_cu] = ban_cap_nhat
            continue
        vi_tri_khoa[k] = len(ds_ket_qua)
        ds_ket_qua.append(dict(moi))

    _ghi_danh_sach_sua_sai(p_sua, ds_ket_qua)
    return ds_ket_qua


def _di_chuyen_sua_sai_cu_neu_co(goc_hien_tai: Path | None = None) -> None:
    """Nếu file cũ `linhx-rea/sua-sai.jsonl` còn tồn tại, chuyển từng mục về đúng `<dir_ra>/sua-sai.jsonl`
    theo `dir_ra` hoặc tên ảnh, rồi xoá `linhx-rea/sua-sai.jsonl`.
    """
    if not DUONG_DAN_SUA_SAI_CU.is_file():
        return

    ds_cu = _doc_danh_sach_sua_sai(DUONG_DAN_SUA_SAI_CU)
    goc_repo = THU_MUC_SKILL.parent
    cac_dir_ung_vien: list[Path] = [
        goc_repo / "thu-anh" / "ra",
        goc_repo / "nguon" / "anh-giai" / "ra",
    ]
    if goc_hien_tai is not None and goc_hien_tai not in cac_dir_ung_vien:
        cac_dir_ung_vien.append(goc_hien_tai)

    map_anh_sang_dir: dict[str, Path] = {}
    for d_ra in cac_dir_ung_vien:
        if not d_ra.is_dir():
            continue
        for sub in sorted(d_ra.iterdir()):
            if not sub.is_dir():
                continue
            map_anh_sang_dir[sub.name] = d_ra
            for fn in ("do.json", "dap_an.json"):
                p_f = sub / fn
                if p_f.is_file():
                    try:
                        ten_a = str(doc_json(p_f).get("anh") or "").strip()
                        if ten_a:
                            map_anh_sang_dir[ten_a] = d_ra
                            map_anh_sang_dir[Path(ten_a).stem] = d_ra
                    except Exception:
                        pass

    nhom_theo_tep: dict[Path, list[dict[str, Any]]] = {}
    for muc in ds_cu:
        dich_dir: Path | None = None
        dir_ra_str = str(muc.get("dir_ra") or "").strip()
        ten_anh = str(muc.get("anh") or "").strip()
        if dir_ra_str:
            p_dr = Path(dir_ra_str)
            dich_dir = p_dr if p_dr.is_absolute() else (goc_repo / p_dr)
        elif ten_anh:
            dich_dir = map_anh_sang_dir.get(ten_anh) or map_anh_sang_dir.get(Path(ten_anh).stem)
        if dich_dir is None:
            dich_dir = goc_hien_tai if (goc_hien_tai is not None and goc_hien_tai.is_dir()) else (goc_repo / "thu-anh" / "ra")
        p_dich = dich_dir / "sua-sai.jsonl"
        nhom_theo_tep.setdefault(p_dich, []).append(muc)

    for p_dich, ds_chuyen in nhom_theo_tep.items():
        _ghi_noi_khu_trung(p_dich, ds_chuyen, cap_nhat_he_thong=False)

    DUONG_DAN_SUA_SAI_CU.unlink(missing_ok=True)


def chay_sua_tu_dap_an(
    dir_ra: str | Path | None = None,
    *,
    tep_ghi: str | Path | None = None,
) -> dict[str, Any]:
    """Gom mọi ghi chú bắt đầu bằng `MAY-SAI:` trong `dap_an.json` các ảnh ghi nối vào `<dir_ra>/sua-sai.jsonl`,
    khử trùng theo `(anh, truc, mo_ta)` và không bao giờ xoá mục cũ.
    """
    goc = _chuan_hoa_dir_ra_sua(dir_ra)
    _di_chuyen_sua_sai_cu_neu_co(goc)
    p_sua = Path(tep_ghi) if tep_ghi is not None else (goc / "sua-sai.jsonl")
    p_sua.parent.mkdir(parents=True, exist_ok=True)

    ds_do = tim_ban_do(goc)
    if ds_do:
        ds_muc = [p.parent for p in ds_do]
    elif goc.is_dir():
        ds_muc = [p for p in sorted(goc.iterdir()) if p.is_dir() and (p / "dap_an.json").is_file()]
    else:
        ds_muc = []

    ds_may_sai = anh_tom.quet_may_sai_trong_dir(ds_muc, doc_json)
    ds_them: list[dict[str, Any]] = [
        {
            "anh": m["anh"],
            "truc": m["truc"],
            "loai_loi": m["loai_loi"],
            "mo_ta": m["mo_ta"],
            "trang_thai": "mo",
        }
        for m in ds_may_sai
    ]

    tat_ca = _ghi_noi_khu_trung(p_sua, ds_them, cap_nhat_he_thong=False)
    return {
        "tep_ghi": p_sua,
        "so_may_sai": len(ds_them),
        "tong_muc": len(tat_ca),
        "danh_sach": tat_ca,
    }


def chay_sua(
    dir_ra: str | Path | None = None,
    mo_ta: str = "",
    *,
    ma_loi: str = "",
    nguyen_nhan: str = "",
    cach_sua: str = "",
    test_hoi_quy: str = "",
    trang_thai: str = "",
    tep_ghi: str | Path | None = None,
) -> Path:
    """Ghi nhận lỗi và cách sửa vào `<dir_ra>/sua-sai.jsonl` (ghi nối + khử trùng, không xoá mục cũ)."""
    goc = _chuan_hoa_dir_ra_sua(dir_ra)
    _di_chuyen_sua_sai_cu_neu_co(goc)
    p_sua = Path(tep_ghi) if tep_ghi is not None else (goc / "sua-sai.jsonl")
    p_sua.parent.mkdir(parents=True, exist_ok=True)

    mo_ta_sach = mo_ta.strip()
    if not mo_ta_sach:
        kq = chay_sua_tu_dap_an(goc, tep_ghi=p_sua)
        return Path(kq["tep_ghi"])

    ban_ghi_moi: dict[str, Any] = {
        "thoi_gian": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "mo_ta": mo_ta_sach,
        "trang_thai": trang_thai.strip() or ("da_sua" if cach_sua.strip() else "mo"),
    }
    if ma_loi.strip():
        ban_ghi_moi["ma_loi"] = ma_loi.strip()
    if dir_ra is not None and str(dir_ra).strip():
        ban_ghi_moi["dir_ra"] = Path(dir_ra).as_posix()
    if nguyen_nhan.strip():
        ban_ghi_moi["nguyen_nhan"] = nguyen_nhan.strip()
    if cach_sua.strip():
        ban_ghi_moi["cach_sua"] = cach_sua.strip()
    if test_hoi_quy.strip():
        ban_ghi_moi["test_hoi_quy"] = test_hoi_quy.strip()

    _ghi_noi_khu_trung(p_sua, [ban_ghi_moi], cap_nhat_he_thong=True)
    return p_sua


_MAU_XY_TRONG_MO_TA = re.compile(r"x\s*=\s*(0?\.\d+|1\.0+|0)\s*,\s*y\s*=\s*(0?\.\d+|1\.0+|0)", re.IGNORECASE)
_MAU_CAP_NGOAC_XY = re.compile(r"\(\s*(0?\.\d+|1\.0+|0)\s*,\s*(0?\.\d+|1\.0+|0)\s*\)")
_MAU_HOP_TRONG_MO_TA = re.compile(
    r"hop\s*=\s*\[\s*(0?\.\d+|1\.0+|0)\s*,\s*(0?\.\d+|1\.0+|0)\s*,\s*(0?\.\d+|1\.0+|0)\s*,\s*(0?\.\d+|1\.0+|0)\s*\]",
    re.IGNORECASE,
)


def _trich_ds_xy(van_ban: str) -> list[tuple[float, float]]:
    kq: list[tuple[float, float]] = []
    for m in _MAU_XY_TRONG_MO_TA.finditer(van_ban):
        kq.append((float(m.group(1)), float(m.group(2))))
    if not kq:
        for m in _MAU_CAP_NGOAC_XY.finditer(van_ban):
            kq.append((float(m.group(1)), float(m.group(2))))
    return kq


def _trich_ds_hop(van_ban: str) -> list[tuple[float, float, float, float]]:
    return [
        (float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)))
        for m in _MAU_HOP_TRONG_MO_TA.finditer(van_ban)
    ]


def _tach_loi_may_va_muc_tieu(mo_ta: str) -> tuple[str, str]:
    """Tách mô tả `MAY-SAI:` thành `(phan_loi_may, phan_muc_tieu_that)` để không lấy nhầm toạ độ điểm sai của máy."""
    s = re.sub(r"\s+", " ", (mo_ta or "").strip())
    s = re.sub(r"^MAY-SAI\s*:\s*", "", s, flags=re.IGNORECASE)
    s = re.sub(r"^\[[A-Z]{2,4}-\d{2}\]\s*", "", s)

    # Nếu cuối câu có dạng `: máy đặt #1 ...` (vd ảnh 111), đẩy phần sau dấu hai chấm về mệnh đề lỗi máy
    phu_loi_cuoi = ""
    m_duoi = re.search(r":\s*(máy đặt\s*#\d+.*)$", s, flags=re.IGNORECASE)
    if m_duoi:
        phu_loi_cuoi = " " + m_duoi.group(1)
        s = s[: m_duoi.start()].strip()

    cac_moc_tach = (
        r"chủ thể chính thực sự là\s+",
        r"chủ thể thực sự là\s+",
        r"trong khi thực tế\s+",
        r"thực tế\s+",
        r"thay vì chủ thể chính là\s+",
        r"thay vì đặt\s*#\d+\s*vào\s+",
        r"thay vì\s+",
        r"bỏ sót chủ thể thực sự là\s+",
        r"bỏ sót chủ thể chính là\s+",
        r"bỏ sót hoàn toàn\s+",
        r"bỏ sót\s+",
        r"trượt khỏi tiêu điểm biểu cảm thật của chân dung là\s+",
        r"đều trượt khỏi\s+",
        r"trượt khỏi\s+",
        r"đẩy\s+",
    )
    for mau in cac_moc_tach:
        m = re.search(mau, s, flags=re.IGNORECASE)
        if m:
            phan_loi = (s[: m.start()].strip() + phu_loi_cuoi).strip()
            phan_muc_tieu = s[m.end() :].strip()
            return phan_loi, phan_muc_tieu

    return phu_loi_cuoi.strip(), s


def _co_mau_do_trong_bang(ds_mau: list[dict[str, Any]]) -> bool:
    for m in ds_mau:
        hx = str(m.get("hex") or "").lstrip("#")
        if len(hx) == 6:
            r, g, b = int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16)
            if r >= 60 and (r - g) >= 25 and (r - b) >= 25:
                return True
    return False


def _danh_gia_mot_muc_sua_sai(
    muc: dict[str, Any],
    map_do: dict[str, dict[str, Any]],
    ban_kinh: float = 0.12,
) -> tuple[str, str]:
    """Kiểm tra tự động 1 bản ghi trong `sua-sai.jsonl` đối chiếu với `do.json` mới.
    Trả về `(trang_thai_moi, ghi_chu_kiem)`.
    """
    ma_loi = str(muc.get("ma_loi") or "").strip()
    ten_anh = str(muc.get("anh") or "").strip()
    loai_loi = str(muc.get("loai_loi") or "").strip()
    mo_ta = str(muc.get("mo_ta") or "").strip()
    mo_ta_thuong = mo_ta.lower()

    # 1. Các bản ghi lỗi hệ thống R1 (không gắn riêng 1 trường `anh`)
    if not ten_anh:
        if ma_loi == "R1-01-do-sau" and map_do:
            tl_co_dinh = {"gan": 0.25, "giua": 0.35, "xa": 0.40}
            khac_co_dinh = any((d.get("do_sau") or {}).get("ti_le") != tl_co_dinh for d in map_do.values())
            return ("da_sua", "k-means 1D động") if khac_co_dinh else ("mo", "vẫn cố định")
        if ma_loi == "R1-02-hut-mat":
            d_088 = map_do.get("088_0089.7s_dinh_goc.jpg") or map_do.get("088_0089.7s_dinh_goc")
            if d_088:
                hm_088 = d_088.get("hut_mat") or []
                co_moi = any(math.hypot(float(p["x"]) - 0.47, float(p["y"]) - 0.22) <= ban_kinh for p in hm_088)
                return ("da_sua", "bắt được vùng môi đỏ 088") if co_moi else ("mo", "chưa bắt được môi đỏ 088")
        return str(muc.get("trang_thai") or "da_sua"), "bản ghi hệ thống"

    do_data = map_do.get(ten_anh) or map_do.get(Path(ten_anh).stem)
    if do_data is None:
        return "chua_kiem_duoc", "không tìm thấy do.json"

    # 2. Nhóm lỗi hút mắt (`hut_mat_bo_sot_nguoi`, `hut_mat_lech_chu_the_khac`)
    if loai_loi in ("hut_mat_bo_sot_nguoi", "hut_mat_lech_chu_the_khac") or muc.get("truc") == "chu_the_chinh":
        ds_hm = do_data.get("hut_mat") or []
        if not ds_hm:
            return "mo", "hut_mat rỗng"

        phan_loi, phan_muc_tieu = _tach_loi_may_va_muc_tieu(mo_ta)
        diem_sai_cu = _trich_ds_xy(phan_loi)

        # Nếu ghi chú đồng thời phàn nàn điểm nhiễu cụ thể (vd #2 088) VÀ bảng 6 màu bỏ sót sắc đỏ
        can_them_mau_do = ("6 màu" in mo_ta_thuong or "bảng màu" in mo_ta_thuong) and ("sắc đỏ" in mo_ta_thuong or "màu đỏ" in mo_ta_thuong)
        if can_them_mau_do and not _co_mau_do_trong_bang(do_data.get("mau") or []):
            return "mo", "bảng 6 màu vẫn thiếu sắc đỏ"
        if "điểm hút mắt #2" in phan_loi.lower() and diem_sai_cu:
            sx, sy = diem_sai_cu[0]
            if any(math.hypot(float(p["x"]) - sx, float(p["y"]) - sy) <= 0.045 for p in ds_hm):
                return "mo", f"vẫn còn điểm nhiễu gần ({sx:.2f},{sy:.2f})"

        # Cắt bỏ phần phụ sau "cùng ..." nếu trước đó đã có toạ độ chủ thể chính bị bỏ sót (vd ảnh 074)
        phan_muc_tieu_chinh = phan_muc_tieu
        m_cung = re.search(r"\bcùng\s+", phan_muc_tieu_chinh, flags=re.IGNORECASE)
        if m_cung and _trich_ds_xy(phan_muc_tieu_chinh[: m_cung.start()]):
            phan_muc_tieu_chinh = phan_muc_tieu_chinh[: m_cung.start()]

        ds_xy_dich = _trich_ds_xy(phan_muc_tieu_chinh)
        ds_hop_dich = _trich_ds_hop(phan_muc_tieu_chinh)
        if not ds_xy_dich and not ds_hop_dich:
            ds_xy_dich = _trich_ds_xy(phan_muc_tieu)
            ds_hop_dich = _trich_ds_hop(phan_muc_tieu)
        if not ds_xy_dich and not ds_hop_dich:
            return "chua_kiem_duoc", "mô tả không có toạ độ đích"

        loi_thuong = phan_loi.lower()
        yeu_cau_hm1 = bool(
            re.search(r"điểm hút mắt(?:\s+của)?(?:\s+máy)?\s*#1", loi_thuong)
            and any(k in mo_ta_thuong for k in ("thay vì", "đẩy ", "cao gấp đôi"))
        )

        if yeu_cau_hm1:
            ung_vien_hm = ds_hm[:1]
        else:
            ung_vien_hm = [
                p
                for p in ds_hm
                if all(math.hypot(float(p["x"]) - wx, float(p["y"]) - wy) > 0.03 for wx, wy in diem_sai_cu)
            ]

        for p in ung_vien_hm:
            px, py = float(p["x"]), float(p["y"])
            for tx, ty in ds_xy_dich:
                kc = math.hypot(px - tx, py - ty)
                if kc <= ban_kinh:
                    return "da_sua", f"có điểm ({px:.2f},{py:.2f}) cách ({tx:.2f},{ty:.2f}) {kc:.3f}≤{ban_kinh}"
            for hx0, hy0, hx1, hy1 in ds_hop_dich:
                if (hx0 - 0.02) <= px <= (hx1 + 0.02) and (hy0 - 0.02) <= py <= (hy1 + 0.02):
                    return "da_sua", f"điểm ({px:.2f},{py:.2f}) nằm trong hop đích"

        hm1 = ds_hm[0]
        return "mo", f"chưa khớp đích (HM1={float(hm1['x']):.2f},{float(hm1['y']):.2f})"

    # 3. Nhóm lỗi độ sâu (`do_sau`)
    if loai_loi == "do_sau" or muc.get("truc") == "khong_gian":
        ds_info = do_data.get("do_sau") or {}
        # Trường hợp máy gán nhầm ảnh 3D thật thành phang=true (vd sony24-01_pavy.jpg)
        la_gan_nham_phang_true = any(
            cum in mo_ta_thuong
            for cum in (
                "nhầm do_sau.phang=true",
                "nhầm phang=true",
                "sai do_sau.phang=true",
            )
        )
        if la_gan_nham_phang_true:
            if not bool(ds_info.get("phang", False)):
                return "da_sua", "đã bỏ gán nhầm phang=true (do_sau.phang=false)"
            return "mo", f"vẫn gán nhầm phang=true ({ds_info.get('ly_do_phang', '')})"

        la_anh_phang_2d = any(
            cum in mo_ta_thuong
            for cum in (
                "poster phẳng",
                "áp phích phẳng",
                "vector thuần phẳng",
                "giấy tờ 2d hoàn toàn phẳng",
                "mặt trang hồ sơ",
                "ảnh phẳng",
            )
        )
        if la_anh_phang_2d:
            if bool(ds_info.get("phang", False)):
                return "da_sua", f"đã nhận phang=true ({ds_info.get('ly_do_phang', '')})"
            return "mo", "do_sau.phang vẫn false"

        if "tâm lớp gần" in mo_ta_thuong or "vung_gan_tam" in mo_ta_thuong:
            phan_loi, _ = _tach_loi_may_va_muc_tieu(mo_ta)
            xy_sai = _trich_ds_xy(phan_loi or mo_ta)
            vgt = ds_info.get("vung_gan_tam") or {}
            if xy_sai and "x" in vgt and "y" in vgt:
                sx, sy = xy_sai[0]
                kc = math.hypot(float(vgt["x"]) - sx, float(vgt["y"]) - sy)
                if kc > 0.15:
                    return "da_sua", f"vung_gan_tam đã dời sang ({vgt['x']:.2f},{vgt['y']:.2f})"
                return "mo", f"vung_gan_tam vẫn ở ({vgt['x']:.2f},{vgt['y']:.2f})"

        return "chua_kiem_duoc", "lỗi thứ tự vật thể 3D trên lop.png không kiểm tự động từ do.json"

    # 4. Nhóm lỗi bố cục (`bo_cuc`)
    if loai_loi == "bo_cuc" or muc.get("truc") in ("bo_cuc", "duong_dan_mat"):
        khop = str((do_data.get("bo_cuc") or {}).get("khop_nhat") or "")
        mong_doi = ""
        if "đường chéo" in mo_ta_thuong:
            mong_doi = "cheo"
        elif "đối xứng" in mo_ta_thuong:
            mong_doi = "doi_xung"
        elif "1/3" in mo_ta_thuong or "một phần ba" in mo_ta_thuong:
            mong_doi = "mot_phan_ba"
        if not mong_doi:
            return "chua_kiem_duoc", "không suy được nhãn bố cục đích"
        if khop == mong_doi:
            return "da_sua", f"bo_cuc.khop_nhat={khop}"
        return "mo", f"bo_cuc.khop_nhat={khop} (cần {mong_doi})"

    # 5. Nhóm lỗi bảng màu (`bang_mau`)
    if loai_loi == "bang_mau" or muc.get("truc") == "mau":
        if "sắc đỏ" in mo_ta_thuong or "màu đỏ" in mo_ta_thuong:
            if _co_mau_do_trong_bang(do_data.get("mau") or []):
                return "da_sua", "bảng 6 màu đã có sắc đỏ"
            return "mo", "bảng 6 màu chưa có sắc đỏ"
        return "chua_kiem_duoc", "không có quy tắc màu tự động"

    return "chua_kiem_duoc", "loại lỗi chưa hỗ trợ kiểm tự động"


def chay_sua_kiem_lai(
    dir_ra: str | Path | None = None,
    *,
    tep_ghi: str | Path | None = None,
    ban_kinh: float = 0.12,
) -> dict[str, Any]:
    """Kiểm tự động lại toàn bộ các mục trong `<dir_ra>/sua-sai.jsonl` bằng `do.json` mới,
    cập nhật trường `trang_thai` tại chỗ (`da_sua` / `mo` / `chua_kiem_duoc`), giữ nguyên mọi mục và trả về bảng tổng hợp.
    """
    goc = _chuan_hoa_dir_ra_sua(dir_ra)
    _di_chuyen_sua_sai_cu_neu_co(goc)
    p_sua = Path(tep_ghi) if tep_ghi is not None else (goc / "sua-sai.jsonl")
    if not p_sua.is_file() or not _doc_danh_sach_sua_sai(p_sua):
        chay_sua_tu_dap_an(goc, tep_ghi=p_sua)

    ds_muc = _doc_danh_sach_sua_sai(p_sua)
    map_do: dict[str, dict[str, Any]] = {}
    for p_do in tim_ban_do(goc):
        d = doc_json(p_do)
        ten = str(d.get("anh") or p_do.parent.name)
        map_do[ten] = d
        map_do[p_do.parent.name] = d

    chi_tiet: list[dict[str, str]] = []
    dem = {"da_sua": 0, "mo": 0, "chua_kiem_duoc": 0}

    for muc in ds_muc:
        tt_moi, ly_do = _danh_gia_mot_muc_sua_sai(muc, map_do, ban_kinh=ban_kinh)
        muc["trang_thai"] = tt_moi
        dem[tt_moi] = dem.get(tt_moi, 0) + 1
        dinh_danh = str(muc.get("anh") or muc.get("ma_loi") or "he_thong")
        loai_hien = str(muc.get("loai_loi") or muc.get("truc") or "he_thong")
        chi_tiet.append({
            "muc": dinh_danh,
            "loai": loai_hien,
            "trang_thai": tt_moi,
            "ghi_chu": ly_do,
        })

    _ghi_danh_sach_sua_sai(p_sua, ds_muc)

    tong = len(ds_muc)
    dong_bang = [
        f"BẢNG KIỂM LẠI SỬA SAI ({p_sua.name}): tổng {tong} | đã sửa: {dem['da_sua']} | còn mở: {dem['mo']} | chưa kiểm được: {dem['chua_kiem_duoc']}",
        "| # | Ảnh / Mã lỗi | Loại lỗi | Trạng thái | Ghi chú kiểm tự động |",
        "|---|---|---|---|---|",
    ]
    for idx, ct in enumerate(chi_tiet, start=1):
        dong_bang.append(f"| {idx} | {ct['muc']} | {ct['loai']} | {ct['trang_thai']} | {ct['ghi_chu']} |")

    return {
        "tep_ghi": p_sua,
        "tong": tong,
        "da_sua": dem["da_sua"],
        "con_mo": dem["mo"],
        "chua_kiem_duoc": dem["chua_kiem_duoc"],
        "chi_tiet": chi_tiet,
        "bang_text": "\n".join(dong_bang),
    }


# ---------------- CLI --------------------------------------------------------------------------------

def tao_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="rea_core.py", description="Điều phối lõi họ skill linhx-rea.")
    sub = p.add_subparsers(dest="lenh", required=True)

    p_tom = sub.add_parser("tom", help="Dựng bộ hồ sơ ra chung và tom.md ≤40 dòng.")
    p_tom.add_argument("dir_ra", help="Thư mục chứa kết quả đo/đọc.")

    p_vd = sub.add_parser("viec-doc", help="Sinh viec_doc.json, mẫu dap_an.json và VIEC-DOC.md theo từ vựng.")
    p_vd.add_argument("dir_ra", help="Thư mục đầu ra.")
    p_vd.add_argument("--tu-vung", required=True, dest="tu_vung", help="Đường dẫn file từ vựng YAML.")

    p_ap = sub.add_parser("ap", help="Áp dap_an.json đã điền, trộn với do.json (không đè số đo).")
    p_ap.add_argument("dir_ra", help="Thư mục đầu ra.")
    p_ap.add_argument("--tu-vung", required=False, default=None, dest="tu_vung", help="File từ vựng dự phòng (tuỳ chọn).")

    p_the = sub.add_parser("the", help="Gom the_de_xuat từ doc.json, kiểm schema -> thu-phap/thu-phap.jsonl + README.md.")
    p_the.add_argument("dir_ra", help="Thư mục đầu ra.")

    p_sua = sub.add_parser("sua", help="Gom ghi chú MAY-SAI: trong dap_an.json (hoặc lỗi lẻ) ghi nối vào <dir_ra>/sua-sai.jsonl.")
    p_sua.add_argument("dir_ra", nargs="?", default="", help="Thư mục đầu ra cần quét dap_an.json (mặc định: thu-anh/ra).")
    p_sua.add_argument("--mo-ta", required=False, default="", dest="mo_ta", help="Mô tả lỗi lẻ (nếu bỏ trống sẽ quét MAY-SAI: trong dap_an.json).")
    p_sua.add_argument("--ma", default="", dest="ma_loi", help="Mã định danh lỗi (tuỳ chọn).")
    p_sua.add_argument("--nguyen-nhan", default="", dest="nguyen_nhan", help="Nguyên nhân gốc (tuỳ chọn).")
    p_sua.add_argument("--cach-sua", default="", dest="cach_sua", help="Cách khắc phục (tuỳ chọn).")
    p_sua.add_argument("--test", default="", dest="test_hoi_quy", help="Tên test hồi quy dự kiến (tuỳ chọn).")
    p_sua.add_argument("--kiem-lai", action="store_true", dest="kiem_lai", help="Kiểm tự động lại từng mục trong <dir_ra>/sua-sai.jsonl bằng do.json mới.")

    return p


def main(argv: list[str] | None = None) -> int:
    _cau_hinh_utf8()
    args = tao_parser().parse_args(argv)

    if args.lenh == "tom":
        out_md = chay_tom(args.dir_ra)
        print(f"Đã ghi: {out_md}")
        return 0

    if args.lenh == "viec-doc":
        kq_vd = chay_viec_doc(args.dir_ra, args.tu_vung)
        print(
            f"Đã sinh việc đọc cho {kq_vd['so_muc']} mục "
            f"(mẫu dap_an mới: {kq_vd['dap_an_moi']}) | {kq_vd['viec_doc_md']}"
        )
        return 0

    if args.lenh == "ap":
        kq_ap = chay_ap(args.dir_ra, tu_vung_path=args.tu_vung)
        for msg_loi in kq_ap["loi"]:
            print(f"[LOI] {msg_loi}", file=sys.stderr)
        print(
            f"Áp đáp án: đã áp {len(kq_ap['da_ap'])} mục, "
            f"bỏ qua {len(kq_ap['bo_qua'])} mục chưa điền, "
            f"xung đột={len(kq_ap['xung_dot'])}, cảnh báo={len(kq_ap['canh_bao'])}, lỗi={len(kq_ap['loi'])}"
        )
        return 1 if kq_ap["loi"] else 0

    if args.lenh == "the":
        kq_the = chay_the(args.dir_ra)
        for ten_thieu in kq_the["anh_thieu_the"]:
            print(f"[THIEU THE] {ten_thieu}: chưa có thẻ thủ pháp nào đạt schema.", file=sys.stderr)
        print(
            f"Thẻ thủ pháp: hợp lệ={len(kq_the['hop_le'])}, sai schema={len(kq_the['the_loi'])}, "
            f"ảnh thiếu thẻ={len(kq_the['anh_thieu_the'])} | {kq_the['thu_phap_jsonl']}"
        )
        return 1 if kq_the["anh_thieu_the"] else 0

    if args.lenh == "sua":
        if args.kiem_lai:
            kq_kl = chay_sua_kiem_lai(args.dir_ra)
            print(kq_kl["bang_text"])
        elif args.mo_ta.strip():
            p_sua = chay_sua(
                args.dir_ra,
                args.mo_ta,
                ma_loi=args.ma_loi,
                nguyen_nhan=args.nguyen_nhan,
                cach_sua=args.cach_sua,
                test_hoi_quy=args.test_hoi_quy,
            )
            print(f"Đã ghi nhận sửa sai: {p_sua}")
        else:
            kq_sua = chay_sua_tu_dap_an(args.dir_ra)
            print(
                f"Đã quét và ghi nhận {kq_sua['so_may_sai']} ghi chú MAY-SAI vào: {kq_sua['tep_ghi']}"
            )
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
