"""Tổng hợp bộ hồ sơ đầu ra chung cho `rea_core.py tom <dir_ra>`:
- `cau-truc.md`    : bố cục, phân lớp không gian, chủ thể từng ảnh.
- `nhip.md`        : diễn tiến tông, độ sáng, màu chủ đạo theo thứ tự shot video + chuyển biến.
- `nguyen-lieu.md` : đạo cụ, chất liệu, thiết lập đèn/ánh sáng, bảng màu để dựng lại.
- `ve-dep.md`      : ma trận tương phản / tương đồng 7 thành phần thị giác Bruce Block tổng hợp.
- `ve-nguoc/README.md` : chỉ mục trỏ tới `khoi.png`, `khung.png`, `prompt.md` từng ảnh.
- `tom.md`         : tóm tắt toàn cục gọn ≤40 dòng, có mục "Máy sai cần sửa" đếm theo loại.
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any, Callable

TRUC_BRUCE_BLOCK: tuple[tuple[str, str], ...] = (
    ("khong_gian", "Không gian"),
    ("duong_net", "Đường nét"),
    ("hinh_khoi", "Hình khối"),
    ("sac_do", "Sắc độ"),
    ("mau", "Màu"),
    ("chuyen_dong", "Chuyển động"),
    ("nhip", "Nhịp"),
)

_MAU_SHOT_VIDEO = re.compile(r"^(?P<shot>\d{2,4})_(?P<giay>\d+(?:\.\d+)?)s(?:_(?P<phan_con_lai>.+))?$")


def phan_loai_may_sai(truc: str, mo_ta: str, gia_tri: str = "") -> str:
    """Phân loại ghi chú `MAY-SAI:` thành các nhóm chuẩn phục vụ thống kê và sinh test."""
    t = truc.strip().lower()
    m = mo_ta.lower()
    gt = gia_tri.strip().lower()

    if t == "khong_gian" or ("lop.png" in m and "hút mắt" not in m) or "bản đồ độ sâu" in m:
        return "do_sau"
    if t in ("duong_dan_mat", "bo_cuc") or "chấm bố cục" in m or "bố cục khớp nhất" in m:
        return "bo_cuc"
    if t == "chu_the_chinh" or "hút mắt" in m:
        if gt:
            la_nguoi = gt in ("chan_dung_nguoi", "nhom_nguoi", "co_the_ban_tay")
        else:
            la_nguoi = any(tu in m for tu in ("người", "nhân vật", "chân dung", "ca sĩ", "phạm nhân"))
        return "hut_mat_bo_sot_nguoi" if la_nguoi else "hut_mat_lech_chu_the_khac"
    if t == "mau" or "bảng 6 màu" in m or "6 màu" in m:
        return "bang_mau"
    return "khac"


def quet_may_sai_trong_dir(
    ds_muc_con: list[Path],
    doc_json_fn: Callable[[Path], dict[str, Any]],
) -> list[dict[str, str]]:
    """Quét mọi ghi chú bắt đầu bằng `MAY-SAI:` trong `dap_an.json` của các thư mục ảnh."""
    ket_qua: list[dict[str, str]] = []
    for thu_muc in ds_muc_con:
        p_dap = thu_muc / "dap_an.json"
        if not p_dap.is_file():
            continue
        try:
            dap = doc_json_fn(p_dap)
        except Exception:
            continue
        ten_anh = str(dap.get("anh") or thu_muc.name)
        tra_loi = dap.get("tra_loi") or []
        if not isinstance(tra_loi, list):
            continue
        for muc in tra_loi:
            if not isinstance(muc, dict):
                continue
            gc = str(muc.get("ghi_chu") or "").strip()
            if gc.upper().startswith("MAY-SAI:"):
                truc = str(muc.get("ma") or "").strip()
                gt = str(muc.get("gia_tri") or "").strip()
                ket_qua.append({
                    "anh": ten_anh,
                    "truc": truc,
                    "loai_loi": phan_loai_may_sai(truc, gc, gt),
                    "mo_ta": gc,
                    "trang_thai": "mo",
                })
    return ket_qua


def _lam_sach_bang(s: str, toi_da: int = 110) -> str:
    txt = re.sub(r"\s+", " ", s.replace("|", "/")).strip()
    txt = re.sub(r"^MAY-SAI:\s*", "", txt, flags=re.IGNORECASE)
    if len(txt) <= toi_da:
        return txt
    return txt[: toi_da - 3].rstrip() + "..."


def _lay_map_doc(doc_data: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not isinstance(doc_data, dict):
        return {}
    ds = (doc_data.get("doc") or {}).get("tra_loi") or []
    return {str(x["ma"]): x for x in ds if isinstance(x, dict) and x.get("ma")}


def _viet_cau_truc_md(
    goc: Path,
    ho_so: list[dict[str, Any]],
    xy_sang_luoi: Callable[[float, float], str],
    dinh_dang_moc: Callable[[Any], str],
) -> Path:
    dong = [
        "# Cấu trúc thị giác (`cau-truc`)",
        "",
        "Tổng hợp bố cục máy đo, phân lớp độ sâu 3 lớp (`inverse_depth`: gần sáng / xa tối) và hệ thống chủ thể chính – phụ của từng ảnh.",
        "",
        "| # | Ảnh | Bố cục khớp nhất | Đường dẫn mắt (`doc`) | Lớp sâu (gần / giữa / xa) & Tâm gần | Chủ thể chính | Chủ thể phụ |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, hs in enumerate(ho_so, start=1):
        d = hs["do"]
        mp = hs["map_doc"]
        bc = d.get("bo_cuc") or {}
        kn = str(bc.get("khop_nhat") or "?")
        diem_kn = float(bc.get(kn, 0.0)) if kn in bc else 0.0

        ds = d.get("do_sau") or {}
        tl = ds.get("ti_le") or {}
        vgt = ds.get("vung_gan_tam") or {}
        o_gan = xy_sang_luoi(float(vgt["x"]), float(vgt["y"])) if ("x" in vgt and "y" in vgt) else "?"
        if ds.get("phang"):
            chuoi_lop = (
                f"**PHẲNG** — {float(tl.get('gan', 0.0))*100:.0f}% / "
                f"{float(tl.get('giua', 0.0))*100:.0f}% / "
                f"{float(tl.get('xa', 0.0))*100:.0f}%"
            )
        else:
            chuoi_lop = (
                f"{float(tl.get('gan', 0.0))*100:.0f}% / "
                f"{float(tl.get('giua', 0.0))*100:.0f}% / "
                f"{float(tl.get('xa', 0.0))*100:.0f}% (`{o_gan}`)"
            )

        ddm = mp.get("duong_dan_mat")
        str_ddm = f"`{ddm['gia_tri']}` ({dinh_dang_moc(ddm.get('moc'))})" if ddm and ddm.get("gia_tri") else "chưa đọc"

        ctc = mp.get("chu_the_chinh")
        if ctc and ctc.get("gia_tri"):
            str_ctc = f"`{ctc['gia_tri']}` [{dinh_dang_moc(ctc.get('moc'))}]"
        else:
            str_ctc = "chưa đọc"

        ctp = mp.get("chu_the_phu")
        if ctp and ctp.get("gia_tri"):
            str_ctp = f"`{ctp['gia_tri']}` [{dinh_dang_moc(ctp.get('moc'))}]"
        else:
            str_ctp = "chưa đọc"

        dong.append(
            f"| {i} | `{hs['ten_anh']}` | `{kn}` ({diem_kn:.2f}) | {str_ddm} | {chuoi_lop} | {str_ctc} | {str_ctp} |"
        )

    dong.append("")
    out = goc / "cau-truc.md"
    out.write_text("\n".join(dong), encoding="utf-8")
    return out


def _viet_nhip_md(goc: Path, ho_so: list[dict[str, Any]]) -> Path:
    ds_shot: list[tuple[float, int, dict[str, Any]]] = []
    ds_le: list[dict[str, Any]] = []

    for hs in ho_so:
        m = _MAU_SHOT_VIDEO.match(hs["thu_muc"].name)
        if m:
            ds_shot.append((float(m.group("giay")), int(m.group("shot")), hs))
        else:
            ds_le.append(hs)

    ds_shot.sort(key=lambda x: (x[0], x[1]))

    dong = [
        "# Nhịp điệu & diễn tiến thị giác (`nhip`)",
        "",
    ]

    if ds_shot:
        dong.extend([
            f"## 1. Chuỗi {len(ds_shot)} shot trích từ cùng một video (sắp theo thời gian)",
            "",
            "| Shot | Thời điểm | Kiểu tông | Độ sáng TB (`ΔTB`) | Độ lệch | 2 màu chủ đạo | Nhiệt màu / Cảm xúc | Chuyển biến nhịp |",
            "|---|---|---|---|---|---|---|---|",
        ])
        tb_truoc: float | None = None
        kieu_truoc: str = ""
        for giay, so_shot, hs in ds_shot:
            d = hs["do"]
            mp = hs["map_doc"]
            tong = d.get("tong") or {}
            kieu = str(tong.get("kieu") or "?")
            tb = float(tong.get("trung_binh", 0.0))
            lech = float(tong.get("do_lech", 0.0))
            hai_mau = ", ".join(f"`{c['hex']}` ({float(c['ti_le'])*100:.0f}%)" for c in (d.get("mau") or [])[:2])
            nm = (mp.get("nhiet_mau") or {}).get("gia_tri") or "chưa đọc"
            cx = (mp.get("cam_xuc") or {}).get("gia_tri") or "chưa đọc"

            if tb_truoc is None:
                str_delta = "mở đầu"
                chuyen_bien = "Thiết lập nền tối ban đầu"
            else:
                delta = tb - tb_truoc
                str_delta = f"{delta:+.2f}"
                cac_y = []
                if abs(delta) >= 0.22:
                    cac_y.append("bước nhảy sáng gắt" if delta > 0 else "sập tối đột ngột")
                elif abs(delta) <= 0.05:
                    cac_y.append("giữ độ sáng liền mạch")
                else:
                    cac_y.append("tăng sáng nhẹ" if delta > 0 else "hạ trầm nhẹ")
                if kieu != kieu_truoc:
                    cac_y.append(f"`{kieu_truoc}` → `{kieu}`")
                chuyen_bien = "; ".join(cac_y)

            tb_truoc = tb
            kieu_truoc = kieu
            dong.append(
                f"| `#{so_shot:03d}` | `{giay:.1f}s` | `{kieu}` | {tb:.2f} ({str_delta}) | {lech:.2f} | "
                f"{hai_mau} | `{nm}` / `{cx}` | {chuyen_bien} |"
            )
        dong.append("")

    if ds_le:
        dong.extend([
            "## 2. Nhóm ấn phẩm độc lập (Poster / Key Visual)",
            "",
            "| Ảnh | Kiểu tông | Độ sáng TB | Độ lệch | 2 màu chủ đạo | Nhịp Bruce Block | Ghi chú chuyển biến đối chiếu |",
            "|---|---|---|---|---|---|---|",
        ])
        tb_kv_truoc: float | None = None
        for hs in ds_le:
            d = hs["do"]
            mp = hs["map_doc"]
            tong = d.get("tong") or {}
            kieu = str(tong.get("kieu") or "?")
            tb = float(tong.get("trung_binh", 0.0))
            lech = float(tong.get("do_lech", 0.0))
            hai_mau = ", ".join(f"`{c['hex']}` ({float(c['ti_le'])*100:.0f}%)" for c in (d.get("mau") or [])[:2])
            nhip_bb = (mp.get("nhip") or {}).get("gia_tri") or "chưa đọc"
            if tb_kv_truoc is None:
                cb = f"Khởi đầu cụm ấn phẩm (`{kieu}`)"
            else:
                d_kv = tb - tb_kv_truoc
                cb = f"Độ sáng đổi {d_kv:+.2f} sang tông `{kieu}`"
            tb_kv_truoc = tb
            dong.append(
                f"| `{hs['ten_anh']}` | `{kieu}` | {tb:.2f} | {lech:.2f} | {hai_mau} | `{nhip_bb}` | {cb} |"
            )
        dong.append("")

    out = goc / "nhip.md"
    out.write_text("\n".join(dong), encoding="utf-8")
    return out


def _viet_nguyen_lieu_md(goc: Path, ho_so: list[dict[str, Any]]) -> Path:
    dem_chat_lieu: Counter[str] = Counter()
    dem_huong_sang: Counter[str] = Counter()
    dem_cung_mem: Counter[str] = Counter()

    dong_bang = []
    for hs in ho_so:
        d = hs["do"]
        mp = hs["map_doc"]
        ctc = mp.get("chu_the_chinh") or {}
        ctp = mp.get("chu_the_phu") or {}
        bt = mp.get("bieu_tuong") or {}
        cl = (mp.get("chat_lieu") or {}).get("gia_tri") or "chưa đọc"
        ash = (mp.get("anh_sang_huong") or {}).get("gia_tri") or "chưa đọc"
        asc = (mp.get("anh_sang_cung_mem") or {}).get("gia_tri") or "chưa đọc"
        nm = (mp.get("nhiet_mau") or {}).get("gia_tri") or "chưa đọc"

        if cl != "chưa đọc":
            dem_chat_lieu[cl] += 1
        if ash != "chưa đọc":
            dem_huong_sang[ash] += 1
        if asc != "chưa đọc":
            dem_cung_mem[asc] += 1

        dao_cu_str = ", ".join(
            x for x in (ctc.get("gia_tri"), ctp.get("gia_tri"), bt.get("gia_tri")) if x and x != "khong_co"
        ) or "chưa đọc"
        gc_ngan = _lam_sach_bang(str(ctp.get("ghi_chu") or ctc.get("ghi_chu") or ""), toi_da=85)
        if gc_ngan:
            dao_cu_str = f"`{dao_cu_str}` — {gc_ngan}"

        palette_6 = ", ".join(f"`{m['hex']}` ({float(m['ti_le'])*100:.0f}%)" for m in (d.get("mau") or []))
        dong_bang.append(
            f"| `{hs['ten_anh']}` | {dao_cu_str} | `{cl}` | `{ash}` / `{asc}` / `{nm}` | {palette_6} |"
        )

    tk_cl = ", ".join(f"`{k}` ({v})" for k, v in dem_chat_lieu.most_common()) or "chưa đọc"
    tk_ash = ", ".join(f"`{k}` ({v})" for k, v in dem_huong_sang.most_common()) or "chưa đọc"
    tk_asc = ", ".join(f"`{k}` ({v})" for k, v in dem_cung_mem.most_common()) or "chưa đọc"

    dong = [
        "# Nguyên liệu tái tạo (`nguyen-lieu`)",
        "",
        "Danh mục đạo cụ/bối cảnh, chất liệu bề mặt, thiết lập nguồn sáng và bảng 6 màu định lượng cần chuẩn bị khi dựng lại.",
        "",
        "## 1. Tóm tắt nhóm nguyên liệu chủ đạo",
        f"- **Chất liệu phổ biến**: {tk_cl}",
        f"- **Hướng đèn / nguồn sáng**: {tk_ash}",
        f"- **Tính chất ánh sáng**: {tk_asc}",
        "",
        "## 2. Bảng nguyên liệu chi tiết theo từng ảnh",
        "| Ảnh | Đạo cụ, nhân vật & bối cảnh | Chất liệu chính | Thiết lập đèn (hướng / cứng-mềm / nhiệt màu) | Bảng 6 màu (`hex` + tỉ lệ) |",
        "|---|---|---|---|---|",
        *dong_bang,
        "",
    ]
    out = goc / "nguyen-lieu.md"
    out.write_text("\n".join(dong), encoding="utf-8")
    return out


def _viet_ve_dep_md(goc: Path, ho_so: list[dict[str, Any]]) -> Path:
    thong_ke: dict[str, Counter[str]] = {ma: Counter() for ma, _ in TRUC_BRUCE_BLOCK}
    dong_anh = []

    for hs in ho_so:
        mp = hs["map_doc"]
        cac_cot = []
        for ma, _ in TRUC_BRUCE_BLOCK:
            gt = str((mp.get(ma) or {}).get("gia_tri") or "").strip()
            if gt:
                thong_ke[ma][gt] += 1
                ky_hieu = "**TP**" if gt == "tuong_phan" else ("TĐ" if gt == "tuong_dong" else gt)
            else:
                ky_hieu = "—"
            cac_cot.append(ky_hieu)

        pc = (mp.get("phong_cach") or {}).get("gia_tri") or "chưa đọc"
        cx = (mp.get("cam_xuc") or {}).get("gia_tri") or "chưa đọc"
        dong_anh.append(f"| `{hs['ten_anh']}` | {' | '.join(cac_cot)} | `{pc}` | `{cx}` |")

    dong_tk = []
    for ma, ten_hien_thi in TRUC_BRUCE_BLOCK:
        tp = thong_ke[ma]["tuong_phan"]
        td = thong_ke[ma]["tuong_dong"]
        tong = tp + td
        tl_tp = f"{(tp / tong) * 100:.0f}%" if tong > 0 else "0%"
        xu_huong = "Thiên về va đập / kịch tính (`tuong_phan`)" if tp >= td else "Thiên về hài hoà / gắn kết (`tuong_dong`)"
        dong_tk.append(f"| **{ten_hien_thi}** (`{ma}`) | {tp} ({tl_tp}) | {td} | {xu_huong} |")

    dong = [
        "# Vẻ đẹp & Cấu trúc thẩm mỹ Bruce Block (`ve-dep`)",
        "",
        "Tổng hợp tương phản (`tuong_phan` — **TP**) và tương đồng (`tuong_dong` — **TĐ**) trên 7 thành phần thị giác *The Visual Story* của Bruce Block.",
        "",
        "## 1. Thống kê tổng hợp 7 thành phần Bruce Block",
        "| Thành phần | Số ảnh `tuong_phan` | Số ảnh `tuong_dong` | Khuynh hướng thẩm mỹ chung |",
        "|---|---|---|---|",
        *dong_tk,
        "",
        "## 2. Ma trận từng ảnh",
        "| Ảnh | Không gian | Đường nét | Hình khối | Sắc độ | Màu | Chuyển động | Nhịp | Phong cách | Cảm xúc |",
        "|---|---|---|---|---|---|---|---|---|---|",
        *dong_anh,
        "",
    ]
    out = goc / "ve-dep.md"
    out.write_text("\n".join(dong), encoding="utf-8")
    return out


def _viet_ve_nguoc_index(goc: Path, ho_so: list[dict[str, Any]]) -> Path:
    vn_dir = goc / "ve-nguoc"
    vn_dir.mkdir(parents=True, exist_ok=True)

    dong = [
        "# Chỉ mục Vẽ ngược (`ve-nguoc`)",
        "",
        " Liên kết trực tiếp tới bản khối 3 lớp (`khoi.png`), khung bố cục & đường dẫn mắt (`khung.png`), và prompt tái tạo (`prompt.md`) của từng ảnh.",
        "",
        "| # | Ảnh | Bản khối 3 lớp | Khung bố cục | Prompt tái tạo | Hồ sơ đo & đọc |",
        "|---|---|---|---|---|---|",
    ]
    for idx, hs in enumerate(ho_so, start=1):
        tm = hs["thu_muc"]
        ten_tm = tm.name
        vn_con = tm / "ve-nguoc"
        lk_khoi = f"[khoi.png](../{ten_tm}/ve-nguoc/khoi.png)" if (vn_con / "khoi.png").is_file() else "*(chưa tạo)*"
        if (vn_con / "bo_cuc.json").is_file():
            lk_khoi = f"{lk_khoi} + [bo_cuc.json](../{ten_tm}/ve-nguoc/bo_cuc.json)"
        lk_khung = f"[khung.png](../{ten_tm}/ve-nguoc/khung.png)" if (vn_con / "khung.png").is_file() else "*(chưa tạo)*"
        lk_prompt = f"[prompt.md](../{ten_tm}/ve-nguoc/prompt.md)" if (vn_con / "prompt.md").is_file() else "*(chưa tạo)*"
        lk_doc = f"[doc.md](../{ten_tm}/doc.md)" if (tm / "doc.md").is_file() else f"[do.png](../{ten_tm}/do.png)"
        dong.append(f"| {idx} | `{hs['ten_anh']}` | {lk_khoi} | {lk_khung} | {lk_prompt} | {lk_doc} |")

    dong.append("")
    p_readme = vn_dir / "README.md"
    p_readme.write_text("\n".join(dong), encoding="utf-8")
    return p_readme


def chay_tom_day_du(
    goc: Path,
    ds_do: list[Path],
    doc_json_fn: Callable[[Path], dict[str, Any]],
    xy_sang_luoi: Callable[[float, float], str],
    dinh_dang_moc: Callable[[Any], str],
    tom_mot_muc_fn: Callable[[dict[str, Any], str], str],
) -> Path:
    """Dựng toàn bộ thư mục ra chung (`cau-truc.md`, `nhip.md`, `nguyen-lieu.md`, `ve-dep.md`, `thu-phap/`,
    `ve-nguoc/README.md`) và ghi `tom.md` gọn ≤40 dòng có mục 'Máy sai cần sửa'.
    """
    la_don_vi_don = len(ds_do) == 1 and ds_do[0].parent.resolve() == goc.resolve()
    ho_so: list[dict[str, Any]] = []
    for p_do in ds_do:
        tm = p_do.parent
        d = doc_json_fn(p_do)
        p_doc = tm / "doc.json"
        doc_d = doc_json_fn(p_doc) if p_doc.is_file() else None
        ten_anh = str(d.get("anh") or d.get("ten") or tm.name)
        ho_so.append({
            "thu_muc": tm,
            "ten_anh": ten_anh,
            "do": d,
            "doc": doc_d,
            "map_doc": _lay_map_doc(doc_d),
        })

    la_bo_anh = any("tong" in hs["do"] and "mau" in hs["do"] for hs in ho_so)
    if la_bo_anh and not la_don_vi_don:
        _viet_cau_truc_md(goc, ho_so, xy_sang_luoi, dinh_dang_moc)
        _viet_nhip_md(goc, ho_so)
        _viet_nguyen_lieu_md(goc, ho_so)
        _viet_ve_dep_md(goc, ho_so)
        _viet_ve_nguoc_index(goc, ho_so)

        tp_dir = goc / "thu-phap"
        tp_dir.mkdir(parents=True, exist_ok=True)
        if not (tp_dir / "README.md").is_file():
            (tp_dir / "README.md").write_text(
                "# Thẻ thủ pháp (`thu-phap`)\n\nChạy `python linhx-rea/scripts/rea_core.py the <dir_ra>` sau bước `ap` để gom thẻ.\n",
                encoding="utf-8",
            )

    # Thống kê số thẻ hợp lệ (nếu đã chạy `the`) và số ảnh đã đọc / vẽ ngược
    so_da_doc = sum(1 for hs in ho_so if hs["doc"] is not None)
    so_ve_nguoc = sum(1 for hs in ho_so if (hs["thu_muc"] / "ve-nguoc" / "prompt.md").is_file())
    p_tp_jsonl = goc / "thu-phap" / "thu-phap.jsonl"
    so_the = (
        sum(1 for ln in p_tp_jsonl.read_text(encoding="utf-8").splitlines() if ln.strip())
        if p_tp_jsonl.is_file()
        else 0
    )

    # Thống kê "Máy sai cần sửa" từ ghi chú MAY-SAI: trong dap_an.json
    ds_may_sai = quet_may_sai_trong_dir([hs["thu_muc"] for hs in ho_so], doc_json_fn)
    dem_loai = Counter(x["loai_loi"] for x in ds_may_sai)
    hm_nguoi = dem_loai["hut_mat_bo_sot_nguoi"]
    hm_khac = dem_loai["hut_mat_lech_chu_the_khac"]
    tong_hm = hm_nguoi + hm_khac
    sai_do_sau = dem_loai["do_sau"]
    sai_bo_cuc = dem_loai["bo_cuc"]
    sai_khac = dem_loai["bang_mau"] + dem_loai["khac"]

    # Đảm bảo tom.md luôn ≤ 40 dòng (dành tối đa 25 dòng cho danh sách ảnh)
    gioi_han_anh = 24
    dong_anh_tom: list[str] = []
    for hs in ho_so[:gioi_han_anh]:
        d = hs["do"]
        mp = hs["map_doc"]
        if "tong" in d and "mau" in d and "bo_cuc" in d:
            tong = d.get("tong") or {}
            m1 = (d.get("mau") or [{"hex": "?", "ti_le": 0.0}])[0]
            bc = d.get("bo_cuc") or {}
            kn = str(bc.get("khop_nhat") or "?")
            hm = d.get("hut_mat") or []
            hm1 = (
                f"({float(hm[0]['x']):.2f},{float(hm[0]['y']):.2f})[{xy_sang_luoi(float(hm[0]['x']), float(hm[0]['y']))}]"
                if hm
                else "?"
            )
            ctc = (mp.get("chu_the_chinh") or {}).get("gia_tri")
            phan_ctc = f" | CT: {ctc}" if ctc else ""
            dong_anh_tom.append(
                f"- `{hs['ten_anh']}` | {tong.get('kieu','?')} (TB {float(tong.get('trung_binh',0.0)):.2f}) "
                f"| {m1['hex']} ({float(m1['ti_le'])*100:.0f}%) | {kn} | HM1 {hm1}{phan_ctc}"
            )
        else:
            dong_anh_tom.append(tom_mot_muc_fn(d, hs["thu_muc"].name))

    if len(ho_so) > gioi_han_anh:
        dong_anh_tom.append(f"- *(... và {len(ho_so) - gioi_han_anh} mục khác xem trong `cau-truc.md`)*")

    dong_tom: list[str] = [
        f"# Tóm tắt phân tích ngược ({len(ho_so)} mục)",
        (
            f"- Tiến độ: đọc `{so_da_doc}/{len(ho_so)}` | vẽ ngược `{so_ve_nguoc}/{len(ho_so)}` | thẻ `{so_the}` "
            f"| Hồ sơ: [cau-truc](cau-truc.md), [nhip](nhip.md), [nguyen-lieu](nguyen-lieu.md), "
            f"[ve-dep](ve-dep.md), [thu-phap](thu-phap/README.md), [ve-nguoc](ve-nguoc/README.md)"
        ),
        "",
        "## Danh sách ảnh",
        *dong_anh_tom,
        "",
        f"## Máy sai cần sửa (tổng {len(ds_may_sai)} ghi chú `MAY-SAI:`)",
        f"- Hút mắt bỏ sót người / chủ thể: {tong_hm} (hút mắt bỏ sót người: {hm_nguoi}; đạo cụ/chữ: {hm_khac})",
        f"- Độ sâu (`lop.png` / không gian phẳng): {sai_do_sau}",
        f"- Bố cục (`khop_nhat` lệch đường dẫn): {sai_bo_cuc}",
    ]
    if sai_khac > 0:
        dong_tom.append(f"- Bảng màu / khác (bỏ sót mảng màu tối): {sai_khac}")

    # Chốt cứng trần ≤ 40 dòng
    if len(dong_tom) > 40:
        dong_tom = dong_tom[:40]

    out_md = goc / "tom.md"
    out_md.write_text("\n".join(dong_tom) + "\n", encoding="utf-8")
    return out_md
