"""Tinh 4 chi so tu nhan agy gan. AI chi gan nhan, code tinh diem (khop bai CSMO Topic 07).
Khong import frappe de test duoc doc lap."""
import itertools
import json
import re

CAU_CO_MAT = {"Q1", "Q2", "Q3"}
CAU_DE_XUAT = {"Q3", "Q6", "Q7"}
NHAN_DUNG_MAU = {"dung", "sai", "nham", "bia", "cu", "khong_biet"}
DIEM_DE_XUAT = {"khuyen": 100, "co_dieu_kien": 60, "khong": 0}
DU_KIEN = ("cong_ty", "nam", "san_pham", "website")


def tach_json(chuoi):
    if not chuoi:
        return None
    if isinstance(chuoi, dict):
        return chuoi
    s = chuoi.strip()
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", s, re.S)
    if m:
        s = m.group(1)
    else:
        a, b = s.find("{"), s.rfind("}")
        if a < 0 or b <= a:
            return None
        s = s[a:b + 1]
    try:
        return json.loads(s)
    except ValueError:
        return None


def _ty_le(tu, mau):
    return round(100 * tu / mau) if mau else None


def _chuan(truong, v):
    v = (v or "").strip().lower()
    if truong == "website":
        v = re.sub(r"^https?://", "", v)
        v = re.sub(r"^www\.", "", v).split("/")[0]
    if truong == "nam":
        m = re.search(r"(19|20)\d\d", v)
        v = m.group(0) if m else ""
    return re.sub(r"\s+", " ", v)


def tinh(du_lieu):
    hang = []
    gia_tri = {k: {} for k in DU_KIEN}
    for ai in du_lieu.get("ai") or []:
        cau = [c for c in ai.get("cau") or [] if not c.get("loi")]
        cm = [c for c in cau if c.get("ma") in CAU_CO_MAT]
        dm = [c for c in cau if c.get("nhan") in NHAN_DUNG_MAU]
        dx = [c for c in cau if c.get("ma") in CAU_DE_XUAT and c.get("de_xuat") in DIEM_DE_XUAT]
        diem_dx = [DIEM_DE_XUAT[c["de_xuat"]] * (0.5 if c.get("ly_do_sai") else 1) for c in dx]
        hang.append({
            "ai": ai.get("ten"), "mo_hinh": ai.get("mo_hinh") or "", "loi": ai.get("loi") or "",
            "so_cau": len(cau),
            "co_mat": _ty_le(sum(1 for c in cm if c.get("nhac_brand")), len(cm)),
            "dung": _ty_le(sum(1 for c in dm if c.get("nhan") == "dung"), len(dm)),
            "de_xuat": round(sum(diem_dx) / len(diem_dx)) if diem_dx else None,
            "nguon": sorted({n for c in cau for n in (c.get("nguon") or []) if n})[:8],
        })
        for c in cau:
            for k in DU_KIEN:
                v = _chuan(k, (c.get("du_kien") or {}).get(k))
                if v:
                    gia_tri[k].setdefault(ai.get("ten"), v)
    cap_khop = cap = 0
    for k in DU_KIEN:
        for (_, a), (_, b) in itertools.combinations(gia_tri[k].items(), 2):
            cap += 1
            cap_khop += a == b or a in b or b in a
    return {"hang": hang, "nhat_quan": _ty_le(cap_khop, cap), "so_cap_nhat_quan": cap}


def dung(ket_qua):
    d = tach_json(ket_qua)
    if not d or not isinstance(d.get("ai"), list):
        return {"ok": False, "tho": ket_qua}
    d["chi_so"] = tinh(d)
    return {"ok": True, **d}
