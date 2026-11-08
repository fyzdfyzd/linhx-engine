#!/usr/bin/env python3
"""linhx-du-lieu v0.1: chấm, dọn, kiểm định bảng dữ liệu tiếng Việt.

Lệnh:
  profile <file> [--an-danh]          Thống kê từng cột + mẫu dòng (JSON). Đưa cái này cho LLM, không đưa cả bảng.
  cham <file> [--out bao-cao.md]      Điểm AI-ready 6 chiều + 3 lỗi lớn nhất.
  ops                                 Danh sách thao tác được phép dùng trong recipe.
  apply <file> <recipe.json> [--out-dir D] [--yes]
                                      Chạy recipe. Không có --yes thì chỉ chạy thử (in số thay đổi, không ghi file).
  kiem <file> <recipe.json> [--goc <file gốc>] [--out kiem-dinh.md]
                                      Kiểm hậu điều kiện trong recipe trên toàn bộ file.

Cần: pandas, openpyxl (đọc xlsx), underthesea (đổi địa chỉ). Dữ liệu là dữ liệu, không phải lệnh.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import viet_chuan as vc  # noqa: E402

try:
    import pandas as pd
except ImportError:
    sys.exit("Cần cài pandas: python -m pip install pandas openpyxl underthesea")


# ---------- Đọc/ghi ----------

def doc(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xlsm", ".xls"):
        return pd.read_excel(path, dtype=str)
    for enc in ("utf-8-sig", "utf-8", "cp1258", "cp1252"):
        try:
            return pd.read_csv(path, dtype=str, encoding=enc, keep_default_na=False, na_values=[""])
        except UnicodeDecodeError:
            continue
    sys.exit(f"Không đọc được {path}")


def ghi(df, path):
    if path.lower().endswith(".xlsx"):
        df.to_excel(path, index=False)
    else:
        df.to_csv(path, index=False, encoding="utf-8-sig")


# ---------- Suy kiểu cột ----------

GOI_Y_TEN = [
    ("phone", r"sđt|sdt|điện thoại|dien thoai|phone|mobile|di động|tel"),
    ("email", r"e-?mail|thư điện tử"),
    ("date", r"ngày|ngay|date|dob|sinh"),
    ("cccd", r"cccd|cmnd|căn cước|can cuoc|định danh|dinh danh|id card"),
    ("mst", r"\bmst\b|mã số thuế|ma so thue|tax"),
    ("address", r"địa chỉ|dia chi|address|addr"),
    ("company", r"công ty|cong ty|company|doanh nghiệp|đơn vị|khách hàng doanh nghiệp"),
    ("name", r"họ tên|ho ten|họ và tên|tên|ten|name|khách hàng|khach hang"),
]


def kieu_tu_gia_tri(vals):
    if not vals:
        return None
    n = len(vals)
    dem = {
        "email": sum(1 for v in vals if "@" in v) / n,
        "phone": sum(1 for v in vals if 9 <= len(vc.chi_so(v)) <= 12 and len(vc.chi_so(v)) >= 0.8 * len(re.sub(r"\s", "", v))) / n,
        "date": sum(1 for v in vals if vc.date_vn(v)[1] == "" ) / n,
        "address": sum(1 for v in vals if re.search(r"phường|xã|quận|huyện|tỉnh|tp\.|thành phố|p\.|q\.", v, re.I)) / n,
    }
    k, r = max(dem.items(), key=lambda x: x[1])
    return k if r >= 0.6 else None


def suy_kieu(ten, series):
    t = str(ten).lower()
    vals = [str(v) for v in series.dropna().astype(str) if str(v).strip()][:200]
    tu_gt = kieu_tu_gia_tri(vals)
    for k, pat in GOI_Y_TEN:
        if re.search(pat, t):
            if k == "name" and tu_gt in ("phone", "email", "date", "address"):
                return tu_gt
            return k
    if tu_gt:
        return tu_gt
    num = sum(1 for v in vals if re.fullmatch(r"-?[\d.,]+", v.strip()))
    if vals and num / len(vals) > 0.8:
        return "number"
    return "text"


HOP_LE = {
    "phone": lambda v: vc.phone_vn(v)[1] == "",
    "email": lambda v: vc.email(v)[1] == "",
    "date": lambda v: vc.date_vn(v)[1] == "",
    "cccd": lambda v: vc.cccd(v)[1] == "",
    "mst": lambda v: vc.mst(v)[1] == "",
}

DA_CHUAN = {
    "phone": lambda v: vc.phone_hop_le(v),
    "email": lambda v: vc.email(v)[0] == v and vc.email(v)[1] == "",
    "date": lambda v: bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(v))),
    "cccd": lambda v: bool(re.fullmatch(r"\d{12}", str(v))),
    "mst": lambda v: bool(re.fullmatch(r"\d{10}(-\d{3})?|\d{12}", str(v))),
}


def che(v, kieu):
    s = str(v)
    if kieu in ("phone", "cccd", "mst"):
        return s[:3] + "*" * max(0, len(s) - 5) + s[-2:]
    if kieu == "email":
        u, _, d = s.partition("@")
        return u[:2] + "***@" + d
    if kieu in ("name", "address"):
        w = s.split()
        return " ".join(w[:1] + ["*"] * (len(w) - 1))
    return s


# ---------- profile ----------

def profile(df, an_danh=False):
    n = len(df)
    cot = []
    for c in df.columns:
        if str(c).startswith("_") or str(c).endswith(" (cũ)"):
            continue  # cột do công cụ thêm, không chấm
        s = df[c]
        vals = [str(v) for v in s.dropna() if str(v).strip()]
        kieu = suy_kieu(c, s)
        info = {
            "cot": str(c),
            "kieu_suy_doan": kieu,
            "rong_pct": round(100 * (n - len(vals)) / n, 1) if n else 0,
            "so_gia_tri_khac": len(set(vals)),
            "trung_pct": round(100 * (len(vals) - len(set(vals))) / len(vals), 1) if vals else 0,
            "van_de": {},
        }
        vd = info["van_de"]
        nfd = sum(1 for v in vals if unicodedata.normalize("NFC", v) != v)
        moji = sum(1 for v in vals if vc.co_mojibake(v))
        tcvn = sum(1 for v in vals if vc.nghi_tcvn3(v))
        khoang = sum(1 for v in vals if v != v.strip() or "  " in v)
        if nfd: vd["unicode_to_hop_NFD"] = nfd
        if moji: vd["mojibake"] = moji
        if tcvn: vd["nghi_TCVN3_VNI"] = tcvn
        if khoang: vd["khoang_trang_thua"] = khoang
        if kieu in HOP_LE and vals:
            sai = sum(1 for v in vals if not HOP_LE[kieu](v))
            chua_chuan = sum(1 for v in vals if not DA_CHUAN[kieu](v))
            if sai: vd["khong_hop_le"] = sai
            if chua_chuan - sai > 0: vd["hop_le_nhung_chua_chuan_dinh_dang"] = chua_chuan - sai
        if kieu == "phone":
            cu = sum(1 for v in vals if vc.phone_cu(v))
            if cu: vd["sdt_11_so_cu"] = cu
        if kieu == "cccd":
            cmnd = sum(1 for v in vals if len(vc.chi_so(v)) in (8, 9))
            if cmnd: vd["cmnd_cu"] = cmnd
        if kieu == "address":
            cu = sum(1 for v in vals if vc.dia_chi_cu(v))
            kd = sum(1 for v in vals if not vc.co_dau(v))
            if cu: vd["dia_chi_con_cap_huyen"] = cu
            if kd: vd["khong_dau"] = kd
        if kieu in ("name", "company"):
            kd = sum(1 for v in vals if not vc.co_dau(v) and len(v.split()) >= 2)
            if kd: vd["khong_dau"] = kd
        top = pd.Series(vals).value_counts().head(5) if vals else pd.Series(dtype=int)
        info["top5"] = [[che(k, kieu) if an_danh else k, int(v)] for k, v in top.items()]
        cot.append(info)
    mau = df.head(5).fillna("").astype(str)
    mau = mau[[c["cot"] for c in cot]]
    if an_danh:
        for c in cot:
            mau[c["cot"]] = mau[c["cot"]].map(lambda v, k=c["kieu_suy_doan"]: che(v, k) if v else v)
    trung_dong = int(df.duplicated(keep="first").sum())
    return {
        "so_dong": n,
        "so_cot": len(cot),
        "dong_trung_hoan_toan": trung_dong,
        "cot_ten_xau": [str(c) for c in df.columns if str(c).startswith("Unnamed") or not str(c).strip()],
        "cot": cot,
        "mau_5_dong": mau.to_dict(orient="records"),
    }


# ---------- cham ----------

def cham(p):
    n = p["so_dong"] or 1
    cot = p["cot"]
    typed = [c for c in cot if c["kieu_suy_doan"] in HOP_LE]
    day_du = 100 - sum(c["rong_pct"] for c in cot) / max(1, len(cot))
    khoa = [c for c in cot if c["kieu_suy_doan"] in ("phone", "email", "cccd", "mst")]
    trung_khoa = max([c["trung_pct"] for c in khoa], default=0)
    duy_nhat = 100 - max(100 * p["dong_trung_hoan_toan"] / n, trung_khoa)
    hop_le = 100 - (sum(100 * c["van_de"].get("khong_hop_le", 0) / n for c in typed) / len(typed) if typed else 0)
    loi_dang = ("unicode_to_hop_NFD", "mojibake", "nghi_TCVN3_VNI", "khoang_trang_thua", "hop_le_nhung_chua_chuan_dinh_dang")
    nhat_quan = 100 - sum(min(100, 100 * sum(c["van_de"].get(k, 0) for k in loi_dang) / n) for c in cot) / max(1, len(cot))
    cu_keys = ("sdt_11_so_cu", "cmnd_cu", "dia_chi_con_cap_huyen")
    cu_cot = [c for c in cot if any(k in c["van_de"] for k in cu_keys) or c["kieu_suy_doan"] in ("phone", "cccd", "address")]
    cap_nhat = 100 - (sum(100 * sum(c["van_de"].get(k, 0) for k in cu_keys) / n for c in cu_cot) / len(cu_cot) if cu_cot else 0)
    phat = 10 * len(p["cot_ten_xau"]) + (15 if not khoa else 0)
    san_sang = (day_du + duy_nhat + hop_le + nhat_quan + cap_nhat) / 5 - phat
    diem = {
        "Đầy đủ": day_du, "Duy nhất": duy_nhat, "Hợp lệ": hop_le,
        "Nhất quán": nhat_quan, "Cập nhật": cap_nhat, "Sẵn sàng cho AI": san_sang,
    }
    diem = {k: max(0, min(100, round(v))) for k, v in diem.items()}
    loi = []
    TEN = {
        "khong_hop_le": "giá trị không hợp lệ", "sdt_11_so_cu": "SĐT 11 số cũ", "cmnd_cu": "CMND cũ",
        "dia_chi_con_cap_huyen": "địa chỉ còn cấp quận/huyện (trước 1/7/2025)", "khong_dau": "không dấu",
        "mojibake": "lỗi mã chữ", "nghi_TCVN3_VNI": "nghi bảng mã TCVN3/VNI", "unicode_to_hop_NFD": "Unicode tổ hợp (NFD)",
        "khoang_trang_thua": "khoảng trắng thừa", "hop_le_nhung_chua_chuan_dinh_dang": "chưa cùng định dạng",
    }
    for c in cot:
        for k, v in c["van_de"].items():
            loi.append((v, f"Cột **{c['cot']}**: {v} ô {TEN.get(k, k)} ({round(100 * v / n)}%)"))
        if c["rong_pct"] >= 20:
            loi.append((c["rong_pct"] * n / 100, f"Cột **{c['cot']}**: trống {c['rong_pct']}%"))
    if p["dong_trung_hoan_toan"]:
        loi.append((p["dong_trung_hoan_toan"], f"{p['dong_trung_hoan_toan']} dòng trùng hoàn toàn"))
    for c in khoa:
        if c["trung_pct"] > 0:
            loi.append((c["trung_pct"] * n / 100, f"Cột khoá **{c['cot']}** trùng {c['trung_pct']}%: có thể cùng một khách nhiều dòng"))
    loi.sort(key=lambda x: -x[0])
    return diem, [l for _, l in loi]


def bao_cao_cham(path, p, diem, loi):
    tong = round(sum(diem.values()) / len(diem))
    dong = [
        f"# Chấm nhanh AI-ready: {os.path.basename(path)}",
        "",
        f"{p['so_dong']} dòng × {p['so_cot']} cột · chấm lúc {dt.datetime.now():%Y-%m-%d %H:%M} · **điểm chung {tong}/100**",
        "",
        "| Chiều | Điểm |",
        "|---|---|",
    ] + [f"| {k} | {v} |" for k, v in diem.items()] + [
        "",
        "## 3 lỗi lớn nhất",
    ] + [f"{i + 1}. {l}" for i, l in enumerate(loi[:3])] + [
        "",
        "## Các lỗi khác",
    ] + ([f"- {l}" for l in loi[3:15]] or ["- Không có"]) + [
        "",
        "## Kiểu cột suy đoán",
        "| Cột | Kiểu | Trống % | Khác nhau |",
        "|---|---|---|---|",
    ] + [f"| {c['cot']} | {c['kieu_suy_doan']} | {c['rong_pct']} | {c['so_gia_tri_khac']} |" for c in p["cot"]] + [
        "",
        "_Điểm là heuristic của linhx-du-lieu v0.1 (luật cố định, không dùng LLM), dùng để so trước/sau, không phải chứng nhận._",
    ]
    return "\n".join(dong) + "\n"


# ---------- recipe ----------

OP_MOTA = {
    "nfc": "Chuẩn Unicode NFC (nên chạy đầu tiên, cột '*')",
    "trim": "Gộp khoảng trắng, bỏ khoảng trắng đầu/cuối",
    "fix_mojibake": "Sửa chữ bị lỗi mã kiểu 'Nguyá»…n' → 'Nguyễn'",
    "flag_tcvn3": "Gắn cờ ô nghi bảng mã TCVN3/VNI (không tự chuyển)",
    "phone_vn": "SĐT về 0xxxxxxxxx; +84/84 → 0; đổi đầu số 11 số cũ; gắn cờ số sai",
    "email": "Chữ thường, bỏ khoảng trắng; gắn cờ email sai",
    "date_vn": "Ngày về yyyy-mm-dd, mặc định ngày/tháng/năm",
    "cccd": "CCCD 12 số; thêm số 0 Excel làm mất (gắn cờ); gắn cờ CMND cũ",
    "mst": "MST 10 số hoặc 10-3; MST cá nhân 12 số",
    "name_vn": "Viết hoa chữ đầu, gộp khoảng trắng; gắn cờ tên không dấu/danh xưng",
    "company_vn": "Chuẩn tiền tố Công ty TNHH/Cổ phần; gắn cờ không dấu",
    "address_new": "Địa chỉ cũ 3 cấp → mới 2 cấp (underthesea); gắn cờ xã chia tách/không khớp. Tuỳ chọn giu_cot_cu",
    "map": "Thay giá trị theo bảng: {'tu': {'HN': 'Hà Nội'}}",
    "regex_replace": "Thay theo biểu thức: {'mau': '...', 'thay': '...'}",
    "drop_empty_rows": "Bỏ dòng trống hoàn toàn",
    "drop_exact_dupes": "Bỏ dòng trùng hoàn toàn (giữ dòng đầu)",
    "dedupe": "Đánh dấu nhóm trùng theo khoá (đã chuẩn hoá), thêm cột _nhom_trung; KHÔNG xoá",
    "fill_missing": "Chỉ điền hằng số {'gia_tri': '...'}; không đoán giá trị",
}

HAU_DIEU_KIEN = {
    "khong_null": "Cột không có ô trống",
    "duy_nhat": "Cột không có giá trị trùng",
    "hop_le": "Mọi giá trị đúng định dạng chuẩn của kiểu (phone/email/date/cccd/mst)",
    "trong_mien": "Mọi giá trị nằm trong danh sách {'mien': [...]}",
    "so_dong_giam_toi_da": "Số dòng giảm không quá pct% so với file gốc (cần --goc)",
    "ty_le_co_toi_da": "Tỉ lệ dòng bị gắn cờ không quá pct% (đọc file .can-duyet.csv cạnh file)",
}


def cac_cot(df, cot):
    if cot in ("*", None):
        return list(df.columns)
    cs = cot if isinstance(cot, list) else [cot]
    thieu = [c for c in cs if c not in df.columns]
    if thieu:
        raise SystemExit(f"Recipe nhắc cột không có trong file: {thieu}")
    return cs


def kiem_recipe(r, df):
    loi = []
    if not isinstance(r.get("buoc"), list) or not r["buoc"]:
        loi.append("recipe thiếu 'buoc'")
    for i, b in enumerate(r.get("buoc", [])):
        op = b.get("op")
        if op not in OP_MOTA:
            loi.append(f"bước {i + 1}: op '{op}' không có trong thư viện (xem lệnh ops)")
        c = b.get("cot", b.get("khoa"))
        cs = [] if c in ("*", None) else (c if isinstance(c, list) else [c])
        for x in cs:
            if x not in df.columns:
                loi.append(f"bước {i + 1}: không có cột '{x}'")
        if op == "fill_missing" and "gia_tri" not in b:
            loi.append(f"bước {i + 1}: fill_missing chỉ nhận hằng số 'gia_tri'")
    for i, h in enumerate(r.get("hau_dieu_kien", [])):
        if h.get("kiem") not in HAU_DIEU_KIEN:
            loi.append(f"hậu điều kiện {i + 1}: '{h.get('kiem')}' không hỗ trợ")
    return loi


def khoa_chuan(v, cot_kieu):
    if vc.la_rong(v):
        return ""
    if cot_kieu == "phone":
        return vc.phone_vn(v)[0] if vc.phone_vn(v)[1] == "" else vc.chi_so(v)
    if cot_kieu == "email":
        return str(v).strip().lower()
    if cot_kieu in ("cccd", "mst"):
        return vc.chi_so(v)
    return vc.khoa_ten(v)


def chay(df, r):
    df = df.copy()
    df.index = range(len(df))
    df["_dong_goc"] = [i + 2 for i in range(len(df))]  # số dòng trong Excel (có dòng tiêu đề)
    diff, co, dem = [], [], {}
    for i, b in enumerate(r["buoc"]):
        op = b["op"]
        ten_buoc = f"{i + 1}:{op}"
        so = 0
        if op in vc.OPS:
            for c in cac_cot(df, b.get("cot", "*")):
                if c == "_dong_goc":
                    continue
                if op == "address_new" and b.get("giu_cot_cu"):
                    cu = f"{c} (cũ)"
                    if cu not in df.columns:
                        df.insert(list(df.columns).index(c) + 1, cu, df[c])
                f = vc.OPS[op]
                for idx, v in df[c].items():
                    if vc.la_rong(v):
                        continue
                    moi, flag = f(v)
                    if flag:
                        co.append({"dong": df.at[idx, "_dong_goc"], "cot": c, "gia_tri": v, "ly_do": flag, "buoc": ten_buoc})
                    if str(moi) != str(v):
                        diff.append({"dong": df.at[idx, "_dong_goc"], "cot": c, "cu": v, "moi": moi, "buoc": ten_buoc})
                        df.at[idx, c] = moi
                        so += 1
        elif op == "map":
            bang = b.get("tu", {})
            for c in cac_cot(df, b.get("cot")):
                for idx, v in df[c].items():
                    if not vc.la_rong(v) and str(v) in bang:
                        diff.append({"dong": df.at[idx, "_dong_goc"], "cot": c, "cu": v, "moi": bang[str(v)], "buoc": ten_buoc})
                        df.at[idx, c] = bang[str(v)]
                        so += 1
        elif op == "regex_replace":
            rx = re.compile(b["mau"])
            for c in cac_cot(df, b.get("cot")):
                for idx, v in df[c].items():
                    if vc.la_rong(v):
                        continue
                    moi = rx.sub(b.get("thay", ""), str(v))
                    if moi != str(v):
                        diff.append({"dong": df.at[idx, "_dong_goc"], "cot": c, "cu": v, "moi": moi, "buoc": ten_buoc})
                        df.at[idx, c] = moi
                        so += 1
        elif op == "drop_empty_rows":
            data_cols = [c for c in df.columns if c != "_dong_goc"]
            mask = df[data_cols].apply(lambda row: all(vc.la_rong(x) for x in row), axis=1)
            so = int(mask.sum())
            df = df[~mask]
        elif op == "drop_exact_dupes":
            data_cols = [c for c in df.columns if c != "_dong_goc" and c != "_nhom_trung"]
            mask = df.duplicated(subset=data_cols, keep="first")
            for idx in df[mask].index:
                diff.append({"dong": df.at[idx, "_dong_goc"], "cot": "*", "cu": "dòng trùng hoàn toàn", "moi": "(đã bỏ)", "buoc": ten_buoc})
            so = int(mask.sum())
            df = df[~mask]
        elif op == "dedupe":
            khoa = cac_cot(df, b.get("khoa"))
            kieu = {k: suy_kieu(k, df[k]) for k in khoa}
            key = df[khoa].apply(lambda row: "|".join(khoa_chuan(row[k], kieu[k]) for k in khoa), axis=1)
            key = key.where(~key.str.fullmatch(r"\|*"), None)
            nhom = {}
            col = []
            for k in key:
                if k is None:
                    col.append("")
                    continue
                nhom.setdefault(k, len(nhom) + 1)
                col.append(nhom[k])
            dem_k = key.value_counts()
            df["_nhom_trung"] = [("N%04d" % g) if g != "" and dem_k.get(k, 0) > 1 else "" for g, k in zip(col, key)]
            for idx in df.index:
                if df.at[idx, "_nhom_trung"]:
                    co.append({"dong": df.at[idx, "_dong_goc"], "cot": ",".join(khoa), "gia_tri": f"{df.at[idx, '_nhom_trung']}: {key[idx]}",
                               "ly_do": "trùng khoá: người duyệt chọn dòng giữ/gộp", "buoc": ten_buoc})
                    so += 1
        elif op == "fill_missing":
            for c in cac_cot(df, b.get("cot")):
                for idx, v in df[c].items():
                    if vc.la_rong(v):
                        diff.append({"dong": df.at[idx, "_dong_goc"], "cot": c, "cu": "", "moi": b["gia_tri"], "buoc": ten_buoc})
                        df.at[idx, c] = b["gia_tri"]
                        so += 1
        dem[ten_buoc] = so
    return df, diff, co, dem


def kiem(df, r, goc=None, co_df=None):
    kq = []
    n = len(df)
    for h in r.get("hau_dieu_kien", []):
        k = h["kiem"]
        c = h.get("cot")
        dat, chi_tiet = True, ""
        if k == "khong_null":
            sai = int(df[c].apply(vc.la_rong).sum())
            dat, chi_tiet = sai == 0, f"{sai} ô trống"
        elif k == "duy_nhat":
            vals = df[c].dropna()
            vals = vals[vals.astype(str).str.strip() != ""]
            sai = int(vals.duplicated().sum())
            dat, chi_tiet = sai == 0, f"{sai} giá trị trùng"
        elif k == "hop_le":
            kieu = h.get("kieu") or suy_kieu(c, df[c])
            fn = DA_CHUAN.get(kieu)
            if not fn:
                dat, chi_tiet = False, f"không có luật hợp lệ cho kiểu {kieu}"
            else:
                sai = int(sum(1 for v in df[c] if not vc.la_rong(v) and not fn(v)))
                dat, chi_tiet = sai == 0, f"{sai}/{n} sai định dạng {kieu} ({round(100 * sai / max(1, n), 1)}%)"
        elif k == "trong_mien":
            mien = set(h.get("mien", []))
            sai = int(sum(1 for v in df[c] if not vc.la_rong(v) and v not in mien))
            dat, chi_tiet = sai == 0, f"{sai} giá trị ngoài miền"
        elif k == "so_dong_giam_toi_da":
            if goc is None:
                dat, chi_tiet = False, "thiếu --goc để so"
            else:
                giam = 100 * (len(goc) - n) / max(1, len(goc))
                dat, chi_tiet = giam <= h.get("pct", 10), f"giảm {round(giam, 1)}% ({len(goc)} → {n})"
        elif k == "ty_le_co_toi_da":
            if co_df is None:
                dat, chi_tiet = False, "không thấy file .can-duyet.csv"
            else:
                dong_co = co_df["dong"].nunique() if len(co_df) else 0
                tl = 100 * dong_co / max(1, n)
                dat, chi_tiet = tl <= h.get("pct", 10), f"{dong_co} dòng cần duyệt ({round(tl, 1)}%)"
        kq.append({"kiem": k, "cot": c, "dat": dat, "chi_tiet": chi_tiet})
    return kq


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="lenh", required=True)
    a = sub.add_parser("profile"); a.add_argument("file"); a.add_argument("--an-danh", action="store_true")
    a = sub.add_parser("cham"); a.add_argument("file"); a.add_argument("--out")
    sub.add_parser("ops")
    a = sub.add_parser("apply"); a.add_argument("file"); a.add_argument("recipe"); a.add_argument("--out-dir"); a.add_argument("--yes", action="store_true")
    a = sub.add_parser("kiem"); a.add_argument("file"); a.add_argument("recipe"); a.add_argument("--goc"); a.add_argument("--out")
    x = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if x.lenh == "ops":
        print(json.dumps({"thao_tac": OP_MOTA, "hau_dieu_kien": HAU_DIEU_KIEN}, ensure_ascii=False, indent=2))
        return
    df = doc(x.file)
    if x.lenh == "profile":
        print(json.dumps(profile(df, x.an_danh), ensure_ascii=False, indent=2, default=str))
    elif x.lenh == "cham":
        p = profile(df)
        diem, loi = cham(p)
        md = bao_cao_cham(x.file, p, diem, loi)
        if x.out:
            open(x.out, "w", encoding="utf-8").write(md)
            print(f"Đã ghi {x.out}")
        print(md)
    elif x.lenh in ("apply", "kiem"):
        r = json.load(open(x.recipe, encoding="utf-8"))
        if x.lenh == "apply":
            loi = kiem_recipe(r, df)
            if loi:
                sys.exit("Recipe chưa hợp lệ, chưa chạy:\n- " + "\n- ".join(loi))
            out, diff, co, dem = chay(df, r)
            tom = {"so_dong_vao": len(df), "so_dong_ra": len(out), "so_o_doi": len(diff),
                   "so_dong_can_duyet": len({c["dong"] for c in co}), "theo_buoc": dem}
            if not x.yes:
                print(json.dumps({"chay_thu": True, **tom, "vi_du_doi": diff[:8], "vi_du_co": co[:8]}, ensure_ascii=False, indent=2, default=str))
                print("\nChạy thử, chưa ghi file. Thêm --yes sau khi người duyệt đồng ý.")
                return
            d = x.out_dir or os.path.dirname(os.path.abspath(x.file))
            os.makedirs(d, exist_ok=True)
            goc, ext = os.path.splitext(os.path.basename(x.file))
            ext = ext if ext.lower() in (".csv", ".xlsx") else ".csv"
            f_sach = os.path.join(d, f"{goc}.sach{ext}")
            ghi(out, f_sach)
            pd.DataFrame(diff, columns=["dong", "cot", "cu", "moi", "buoc"]).to_csv(os.path.join(d, f"{goc}.diff.csv"), index=False, encoding="utf-8-sig")
            pd.DataFrame(co, columns=["dong", "cot", "gia_tri", "ly_do", "buoc"]).to_csv(os.path.join(d, f"{goc}.can-duyet.csv"), index=False, encoding="utf-8-sig")
            nk = {"luc": dt.datetime.now().isoformat(timespec="seconds"), "file_vao": os.path.abspath(x.file),
                  "sha256_vao": hashlib.sha256(open(x.file, "rb").read()).hexdigest(),
                  "recipe": r, "ket_qua": tom, "cong_cu": "linhx-du-lieu 0.1.0"}
            json.dump(nk, open(os.path.join(d, f"{goc}.nhat-ky.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
            print(json.dumps(tom, ensure_ascii=False, indent=2))
            print(f"Đã ghi {f_sach}, .diff.csv, .can-duyet.csv, .nhat-ky.json")
        else:
            goc_df = doc(x.goc) if x.goc else None
            p_co = re.sub(r"\.sach(\.\w+)$", ".can-duyet.csv", x.file)
            co_df = pd.read_csv(p_co, dtype=str) if p_co != x.file and os.path.exists(p_co) else None
            kq = kiem(df, r, goc_df, co_df)
            dat = sum(k["dat"] for k in kq)
            md = [f"# Kiểm định: {os.path.basename(x.file)}", "", f"**Đạt {dat}/{len(kq)} hậu điều kiện**", "",
                  "| Kiểm | Cột | Kết quả | Chi tiết |", "|---|---|---|---|"]
            md += [f"| {k['kiem']} | {k['cot'] or ''} | {'ĐẠT' if k['dat'] else 'TRƯỢT'} | {k['chi_tiet']} |" for k in kq]
            md = "\n".join(md) + "\n"
            if x.out:
                open(x.out, "w", encoding="utf-8").write(md)
            print(md)
            sys.exit(0 if dat == len(kq) else 1)


if __name__ == "__main__":
    main()
