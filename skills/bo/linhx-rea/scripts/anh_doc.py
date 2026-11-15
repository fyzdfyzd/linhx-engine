"""Phần hỗ trợ vòng đọc (`viec-doc` / `dap_an` / `ap`) riêng cho ảnh (`rea-anh`).

Được gọi từ `rea_core.py` khi mục cần đọc có cấu trúc `do.json` của ảnh:
- Trích `goi_y_do` (điểm hút mắt, tông, 3 màu đầu, bố cục, lớp gần + trọng tâm, trạng thái phẳng, mặt người).
- Tìm đường dẫn ảnh gốc để hiển thị trong `VIEC-DOC.md`, `viec_doc.json` và `ve_nguoc.py`.
- Đối chiếu vùng `duong_dan_mat` của người đọc với các điểm `hut_mat` của máy.
- Định dạng phần "Số đo máy" ngắn gọn trong `<anh>/doc.md`.
- Sinh ảnh tự sinh xác định phục vụ tự kiểm `ap` trong `chay_thu.py` và `tests/`.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Callable

import cv2
import numpy as np

GOC_REPO = Path(__file__).resolve().parents[2]

# Danh sách các khoá số đo của máy trong `do.json` tuyệt đối không được ghi đè bởi `dap_an.json`
KHOA_DO_ANH: tuple[str, ...] = ("mau", "tong", "nguoi", "hut_mat", "bo_cuc", "do_sau", "kich_thuoc", "ocr")

_HANG_LUOI = "ABC"
_COT_LUOI = "123"


def la_ban_do_anh(do_data: dict[str, Any]) -> bool:
    return all(k in do_data for k in ("mau", "tong", "hut_mat", "bo_cuc", "do_sau"))


def dinh_dang_duong_dan(p: Path) -> str:
    try:
        return p.resolve().relative_to(GOC_REPO.resolve()).as_posix()
    except Exception:
        return p.as_posix()


def tim_path_anh_goc(anh_dir: Path, ten_anh: str, dir_ra: Path | None = None) -> Path | None:
    if not ten_anh:
        return None
    cha_ra = dir_ra if dir_ra is not None else anh_dir.parent
    ung_vien = [
        anh_dir / ten_anh,
        anh_dir.parent / ten_anh,
        anh_dir.parent / "vao" / ten_anh,
        cha_ra.parent / "vao" / ten_anh,
        cha_ra.parent / ten_anh,
        cha_ra / ten_anh,
        GOC_REPO / "thu-anh" / "vao" / ten_anh,
    ]
    for p in ung_vien:
        if p.is_file():
            return p
    return None


def tim_anh_goc(anh_dir: Path, ten_anh: str, dir_ra: Path) -> str:
    p = tim_path_anh_goc(anh_dir, ten_anh, dir_ra)
    if p is not None:
        return dinh_dang_duong_dan(p)
    return ten_anh


def trich_goi_y_do_anh(do_data: dict[str, Any], xy_sang_luoi: Callable[[float, float], str]) -> dict[str, Any]:
    """Trích gợi ý số đo chính từ `do.json` để người đọc đối chiếu khi trả lời."""
    hm_raw = do_data.get("hut_mat") or []
    ds_hm = []
    for idx, p in enumerate(hm_raw, start=1):
        px, py = float(p["x"]), float(p["y"])
        ds_hm.append({
            "thu_tu": idx,
            "x": round(px, 4),
            "y": round(py, 4),
            "diem": round(float(p.get("diem", 0.0)), 4),
            "vung": xy_sang_luoi(px, py),
        })

    tong = do_data.get("tong") or {}
    ba_mau = [
        {"hex": m["hex"], "ti_le": round(float(m["ti_le"]), 4)}
        for m in (do_data.get("mau") or [])[:3]
    ]
    bc = do_data.get("bo_cuc") or {}
    kn = str(bc.get("khop_nhat", ""))

    ds = do_data.get("do_sau") or {}
    ti_le_ds = ds.get("ti_le") or {}
    vgt = ds.get("vung_gan_tam")
    thong_tin_lop_gan: dict[str, Any] = {
        "ti_le": ti_le_ds.get("gan"),
        "ti_le_3_lop": ti_le_ds,
        "phang": bool(ds.get("phang", False)),
    }
    if isinstance(vgt, dict) and "x" in vgt and "y" in vgt:
        gx, gy = float(vgt["x"]), float(vgt["y"])
        thong_tin_lop_gan["vung_gan_tam"] = {"x": round(gx, 4), "y": round(gy, 4)}
        thong_tin_lop_gan["vung_luoi"] = xy_sang_luoi(gx, gy)

    nguoi = do_data.get("nguoi") or {}
    goi_y: dict[str, Any] = {
        "hut_mat": ds_hm,
        "tong": {
            "kieu": tong.get("kieu"),
            "trung_binh": tong.get("trung_binh"),
            "do_lech": tong.get("do_lech"),
        },
        "ba_mau": ba_mau,
        "bo_cuc_khop_nhat": {"kieu": kn, "diem": bc.get(kn)} if kn else {},
        "lop_gan": thong_tin_lop_gan,
    }
    if nguoi.get("co_cong_cu"):
        goi_y["so_mat_nguoi"] = len(nguoi.get("mat") or [])
    return goi_y


def tap_o_luoi_tu_chuoi(chuoi: str) -> set[str]:
    s = chuoi.strip().upper()
    if "-" not in s:
        if len(s) == 2 and s[0] in _HANG_LUOI and s[1] in _COT_LUOI:
            return {s}
        return set()
    trai, phai = s.split("-", 1)
    if len(trai) == 2 and len(phai) == 2 and trai[0] in _HANG_LUOI and phai[0] in _HANG_LUOI and trai[1] in _COT_LUOI and phai[1] in _COT_LUOI:
        r0, r1 = sorted((_HANG_LUOI.index(trai[0]), _HANG_LUOI.index(phai[0])))
        c0, c1 = sorted((_COT_LUOI.index(trai[1]), _COT_LUOI.index(phai[1])))
        return {f"{_HANG_LUOI[r]}{_COT_LUOI[c]}" for r in range(r0, r1 + 1) for c in range(c0, c1 + 1)}
    return set()


def moc_chua_hut_mat(
    moc: Any,
    ds_hut_mat: list[dict[str, Any]],
    xy_sang_luoi: Callable[[float, float], str],
) -> bool:
    """Kiểm tra vùng/mốc của `duong_dan_mat` có chứa ít nhất 1 điểm hút mắt của máy hay không."""
    if not ds_hut_mat:
        return True
    if moc is None:
        return False

    if isinstance(moc, str):
        tap_o = tap_o_luoi_tu_chuoi(moc)
        if not tap_o:
            return False
        return any(xy_sang_luoi(float(p["x"]), float(p["y"])) in tap_o for p in ds_hut_mat)

    if isinstance(moc, dict):
        if "vung" in moc:
            return moc_chua_hut_mat(moc["vung"], ds_hut_mat, xy_sang_luoi)
        if "luoi" in moc:
            return moc_chua_hut_mat(moc["luoi"], ds_hut_mat, xy_sang_luoi)
        if "hop" in moc and isinstance(moc["hop"], (list, tuple)) and len(moc["hop"]) == 4:
            x0, y0, x1, y1 = [float(v) for v in moc["hop"]]
            xmin, xmax = min(x0, x1) - 0.02, max(x0, x1) + 0.02
            ymin, ymax = min(y0, y1) - 0.02, max(y0, y1) + 0.02
            return any(xmin <= float(p["x"]) <= xmax and ymin <= float(p["y"]) <= ymax for p in ds_hut_mat)
        if "x" in moc and "y" in moc:
            mx, my = float(moc["x"]), float(moc["y"])
            o_m = xy_sang_luoi(mx, my)
            return any(
                math.hypot(float(p["x"]) - mx, float(p["y"]) - my) <= 0.18
                or xy_sang_luoi(float(p["x"]), float(p["y"])) == o_m
                for p in ds_hut_mat
            )
        if "xy" in moc and isinstance(moc["xy"], (list, tuple)) and len(moc["xy"]) == 2:
            return moc_chua_hut_mat({"x": moc["xy"][0], "y": moc["xy"][1]}, ds_hut_mat, xy_sang_luoi)
        return False

    if isinstance(moc, (list, tuple)):
        if len(moc) == 2 and all(isinstance(v, (int, float)) for v in moc):
            return moc_chua_hut_mat({"x": moc[0], "y": moc[1]}, ds_hut_mat, xy_sang_luoi)
        if len(moc) == 4 and all(isinstance(v, (int, float)) for v in moc):
            return moc_chua_hut_mat({"hop": list(moc)}, ds_hut_mat, xy_sang_luoi)
        return any(moc_chua_hut_mat(m, ds_hut_mat, xy_sang_luoi) for m in moc)

    return False


def tom_so_do_may_md(do_data: dict[str, Any], xy_sang_luoi: Callable[[float, float], str]) -> list[str]:
    """Tạo các dòng Markdown ngắn gọn cho phần 'Số đo máy' trong `<anh>/doc.md`."""
    kt = do_data.get("kich_thuoc") or [0, 0]
    tong = do_data.get("tong") or {}
    ba_mau = (do_data.get("mau") or [])[:3]
    chuoi_mau = ", ".join(f"`{m['hex']}` ({float(m['ti_le']) * 100:.0f}%)" for m in ba_mau) or "không rõ"

    hm = do_data.get("hut_mat") or []
    chuoi_hm = "; ".join(
        f"#{i} ({float(p['x']):.2f}, {float(p['y']):.2f}) [ô {xy_sang_luoi(float(p['x']), float(p['y']))}, điểm {float(p['diem']):.2f}]"
        for i, p in enumerate(hm, start=1)
    ) or "không có"

    bc = do_data.get("bo_cuc") or {}
    kn = str(bc.get("khop_nhat", "?"))
    diem_kn = float(bc.get(kn, 0.0)) if kn in bc else 0.0

    ds = do_data.get("do_sau") or {}
    tl = ds.get("ti_le") or {}
    vgt = ds.get("vung_gan_tam") or {}
    chuoi_tam_gan = ""
    if "x" in vgt and "y" in vgt:
        gx, gy = float(vgt["x"]), float(vgt["y"])
        chuoi_tam_gan = f" | trọng tâm lớp gần: ({gx:.2f}, {gy:.2f}) [ô {xy_sang_luoi(gx, gy)}]"
    if ds.get("phang"):
        chuoi_tam_gan += f" | ảnh phẳng (`phang=true`: {ds.get('ly_do_phang', '')})"

    dong = [
        f"- **Kích thước & Tông**: {kt[0]}×{kt[1]} px | tông `{tong.get('kieu', '?')}` (TB {float(tong.get('trung_binh', 0.0)):.2f}, lệch {float(tong.get('do_lech', 0.0)):.2f})",
        f"- **3 màu chủ đạo**: {chuoi_mau}",
        f"- **Điểm hút mắt**: {chuoi_hm}",
    ]
    nguoi = do_data.get("nguoi") or {}
    if nguoi.get("co_cong_cu"):
        ds_mat = nguoi.get("mat") or []
        dong.append(f"- **Nhận diện mặt/người (YuNet)**: {len(ds_mat)} mặt")
    dong.extend([
        f"- **Bố cục**: khớp nhất `{kn}` ({diem_kn:.2f}) | một phần ba {float(bc.get('mot_phan_ba', 0.0)):.2f} | chéo {float(bc.get('cheo', 0.0)):.2f} | đối xứng {float(bc.get('doi_xung', 0.0)):.2f}",
        (
            f"- **Độ sâu 3 lớp** (`inverse_depth`, lớn = gần): "
            f"gần {float(tl.get('gan', 0.0)) * 100:.0f}%, "
            f"giữa {float(tl.get('giua', 0.0)) * 100:.0f}%, "
            f"xa {float(tl.get('xa', 0.0)) * 100:.0f}%"
            f"{chuoi_tam_gan}"
        ),
    ])
    return dong


def tao_anh_tu_sinh_mau(rong: int = 480, cao: int = 360) -> np.ndarray:
    """Sinh ảnh mẫu tổng hợp xác định (nền tối lạnh + luồng chéo + khối tròn đỏ cam ở B2 + khối phụ B3)
    dùng để tự kiểm `viec-doc` và `ap` mà không đụng tới 15 ảnh thật.
    """
    yy, xx = np.mgrid[0:cao, 0:rong].astype(np.float32)
    nx = xx / float(max(1, rong - 1))
    ny = yy / float(max(1, cao - 1))

    img = np.zeros((cao, rong, 3), dtype=np.uint8)
    img[:, :, 0] = np.clip(28.0 + 24.0 * (1.0 - ny), 0, 255).astype(np.uint8)
    img[:, :, 1] = np.clip(22.0 + 18.0 * (1.0 - ny), 0, 255).astype(np.uint8)
    img[:, :, 2] = np.clip(16.0 + 12.0 * nx, 0, 255).astype(np.uint8)

    pts_cheo = np.array(
        [
            [int(0.06 * rong), int(0.10 * cao)],
            [int(0.16 * rong), int(0.06 * cao)],
            [int(0.54 * rong), int(0.48 * cao)],
            [int(0.44 * rong), int(0.54 * cao)],
        ],
        dtype=np.int32,
    )
    lop_phu = img.copy()
    cv2.fillConvexPoly(lop_phu, pts_cheo, (95, 92, 82), lineType=cv2.LINE_AA)
    img = cv2.addWeighted(lop_phu, 0.55, img, 0.45, 0.0)

    cv2.rectangle(
        img,
        (int(0.73 * rong), int(0.44 * cao)),
        (int(0.86 * rong), int(0.62 * cao)),
        (175, 178, 182),
        -1,
    )

    tam_x, tam_y = int(0.50 * rong), int(0.48 * cao)
    ban_kinh = int(0.12 * min(rong, cao))
    cv2.circle(img, (tam_x, tam_y), ban_kinh + 6, (35, 45, 120), -1, cv2.LINE_AA)
    cv2.circle(img, (tam_x, tam_y), ban_kinh, (32, 54, 232), -1, cv2.LINE_AA)
    cv2.circle(img, (tam_x - ban_kinh // 4, tam_y - ban_kinh // 4), max(4, ban_kinh // 4), (110, 155, 250), -1, cv2.LINE_AA)

    return img
