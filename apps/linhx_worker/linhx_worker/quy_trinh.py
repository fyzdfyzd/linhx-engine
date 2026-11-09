"""Quy trinh nhieu buoc (che_do = gop): server chia viec con, gom ket qua. Tho khong nhan viec cha.

ai-noi-gi-ve-brand:
  buoc 1: moi AI mot viec 'hoi-mot-ai' (can tho co trinh duyet), chep nguyen van 8 cau
  buoc 2: mot viec 'viet-bao-cao' (tho nao cung duoc, ke ca cloud): gan nhan + viet nhan dinh
  gom:    cau tra loi + nhan -> bao_cao.tinh() tinh 4 chi so
"""
import json

import frappe
from frappe.utils import now_datetime

from linhx_worker import bao_cao

QUY_TRINH = {
    "ai-noi-gi-ve-brand": {
        "buoc1": "hoi-mot-ai",
        "nhanh": [
            ("ChatGPT", "https://chatgpt.com (bật Trò chuyện tạm thời)"),
            ("Gemini", "https://gemini.google.com"),
            ("Claude", "https://claude.ai"),
        ],
        # moi luot agy ngan (<5 phut): moi AI chia 3 nhom cau
        "nhom_cau": [["Q1", "Q2", "Q3"], ["Q4", "Q5", "Q8"], ["Q6", "Q7"]],
        "buoc2": "cham-mot-ai",    # moi AI mot viec gan nhan (dau vao ngan, nhan on dinh)
        "buoc3": "viet-bao-cao",   # nhan dinh tu nhan da gan + trich ngan
    }
}

TRICH_TOI_DA = 700  # ky tu moi cau tra loi dua vao buoc viet nhan dinh


def la_gop(workflow):
    return frappe.db.get_value("LX Workflow", workflow, "che_do") == "gop"


def _con(cha, workflow, dau_vao, nhan):
    frappe.get_doc({"doctype": "LX Job", "workflow": workflow, "dau_vao": dau_vao, "cha": cha,
                    "nhan_viec": nhan, "trang_thai": "cho"}).insert(ignore_permissions=True)


def chia(job):
    qt = QUY_TRINH.get(job.workflow)
    if not qt:
        frappe.throw(f"Chưa khai quy trình gộp cho {job.workflow}")
    for ten, trang in qt["nhanh"]:
        for nhom in qt.get("nhom_cau") or [None]:
            cau = ",".join(nhom) if nhom else "Q1,Q2,Q3,Q4,Q5,Q6,Q7,Q8"
            _con(job.name, qt["buoc1"], f"{job.dau_vao}\nai: {ten}\ntrang: {trang}\ncau: {cau}", f"{ten}|{cau}")
    job.db_set({"trang_thai": "dang_chay", "nhan_luc": now_datetime()}, notify=True)


def chia_viec_gop_cho():
    """Tự tách các việc cha quy trình gộp đang ở trạng thái `cho` (như việc sinh từ đơn `da_tra`) thành các việc con."""
    wfs_gop = [
        r.name
        for r in frappe.get_all("LX Workflow", filters={"bat": 1, "che_do": "gop"}, fields=["name"])
        if r.name in QUY_TRINH
    ]
    if not wfs_gop:
        return
    rows = frappe.db.sql(
        """select name from `tabLX Job`
        where trang_thai='cho' and workflow in %(wfs)s
        order by creation asc for update skip locked""",
        {"wfs": tuple(wfs_gop)},
    )
    for (name,) in rows or []:
        job = frappe.get_doc("LX Job", name)
        if job.trang_thai == "cho" and not _cac_con(job.name):
            chia(job)


def _cac_con(cha):
    return frappe.get_all("LX Job", filters={"cha": cha}, fields=["name", "workflow", "trang_thai", "nhan_viec", "ket_qua", "nhat_ky"], order_by="creation asc")


def tien_do(cha):
    ten = {"hoi-mot-ai": "Hỏi", "cham-mot-ai": "Chấm", "viet-bao-cao": "Viết báo cáo"}
    return [{"buoc": f"{ten.get(c.workflow, c.workflow)} {(c.nhan_viec or '').replace('|', ' · ') if c.workflow != 'viet-bao-cao' else ''}".strip(),
             "trang_thai": c.trang_thai} for c in _cac_con(cha)]


def _tra_loi_buoc1(con):
    """Gom cac viec con theo AI (nhan_viec = 'ChatGPT|Q1,Q2,Q3')."""
    theo_ai = {}
    for c in con:
        ten, _, nhom = (c.nhan_viec or "").partition("|")
        a = theo_ai.setdefault(ten, {"ten": ten, "mo_hinh": "", "loi": "", "cau": []})
        d = bao_cao.tach_json(c.ket_qua) if c.trang_thai == "xong" else None
        if not d:
            ly_do = "không hỏi được" if c.trang_thai != "xong" else "kết quả không đúng khuôn"
            a["cau"] += [{"ma": m, "tra_loi": "", "loi": ly_do, "nguon": []} for m in nhom.split(",") if m]
            continue
        a["mo_hinh"] = a["mo_hinh"] or d.get("mo_hinh") or ""
        if d.get("loi") and not d.get("cau"):
            a["cau"] += [{"ma": m, "tra_loi": "", "loi": d["loi"], "nguon": []} for m in nhom.split(",") if m]
        a["cau"] += d.get("cau") or []
    for a in theo_ai.values():
        a["cau"].sort(key=lambda x: x.get("ma", ""))
        if a["cau"] and all(x.get("loi") for x in a["cau"]):
            a["loi"] = a["cau"][0]["loi"]
    return list(theo_ai.values())


def _brand(dau_vao):
    for dong in (dau_vao or "").splitlines():
        if dong.startswith("brand:"):
            return dong.split(":", 1)[1].strip()
    return ""


def _xong_het(ds):
    return ds and not any(c.trang_thai in ("cho", "dang_chay") for c in ds)


def gom(cha_name):
    """Day quy trinh: buoc1 xong -> tao buoc2 moi AI -> buoc2 xong -> tao buoc3 -> buoc3 xong -> ket qua cha."""
    cha = frappe.get_doc("LX Job", cha_name)
    if cha.trang_thai != "dang_chay":
        return
    qt = QUY_TRINH[cha.workflow]
    brand = _brand(cha.dau_vao)
    con = _cac_con(cha_name)
    b1 = [c for c in con if c.workflow == qt["buoc1"]]
    b2 = [c for c in con if c.workflow == qt["buoc2"]]
    b3 = [c for c in con if c.workflow == qt["buoc3"]]
    if not _xong_het(b1):
        return
    ai = _tra_loi_buoc1(b1)
    # code tu do 'co nhac ten' tren nguyen van, khong de AI gan nhan quyet
    for a in ai:
        for c in a.get("cau") or []:
            c["nhac_brand"] = bao_cao.co_nhac(brand, c.get("tra_loi"))
    co_tra_loi = [a for a in ai if any(c.get("tra_loi") for c in a.get("cau") or [])]
    if not co_tra_loi:
        cha.db_set({"trang_thai": "loi", "nhat_ky": "không AI nào hỏi được"}, notify=True)
        return
    if not b2:
        for a in co_tra_loi:
            goi = {"ten": a["ten"], "cau": [{"ma": c.get("ma"), "tra_loi": c.get("tra_loi"), "nhac_brand": c["nhac_brand"]} for c in a["cau"] if c.get("tra_loi")]}
            _con(cha_name, qt["buoc2"], f"{cha.dau_vao}\n\nTRA_LOI:\n{json.dumps(goi, ensure_ascii=False)}", a["ten"])
        return
    if not _xong_het(b2):
        return
    # tron nhan buoc2 vao tung cau (giu nhac_brand cua code)
    nhan = {}
    for c in b2:
        d = bao_cao.tach_json(c.ket_qua) if c.trang_thai == "xong" else None
        for n in (d or {}).get("nhan_cau") or []:
            nhan[(c.nhan_viec, n.get("ma"))] = n
    for a in ai:
        for c in a.get("cau") or []:
            n = nhan.get((a["ten"], c.get("ma"))) or {}
            c.update({k: x for k, x in n.items() if k in ("nhan", "de_xuat", "ly_do_sai", "du_kien")})
    kq = {"ai": ai}
    if not b3:
        gon = [{"ten": a["ten"], "cau": [{k: (c.get(k) or "")[:TRICH_TOI_DA] if k == "tra_loi" else c.get(k)
                                          for k in ("ma", "tra_loi", "nhac_brand", "nhan", "de_xuat", "du_kien")} for c in a.get("cau") or []]} for a in ai]
        chi_so = bao_cao.tinh({"ai": ai})
        _con(cha_name, qt["buoc3"], f"{cha.dau_vao}\n\nCHI_SO:\n{json.dumps(chi_so, ensure_ascii=False)}\n\nDA_GAN_NHAN:\n{json.dumps({'ai': gon}, ensure_ascii=False)}", "viet-bao-cao")
        return
    v = b3[-1]
    if v.trang_thai in ("cho", "dang_chay"):
        return
    nd = bao_cao.tach_json(v.ket_qua) if v.trang_thai == "xong" else None
    if nd:
        for k in ("trich_sai", "buoc_roi", "lop_yeu", "ke_hoach_30_ngay", "ket_luan"):
            kq[k] = nd.get(k)
    kq["ngay"] = now_datetime().strftime("%Y-%m-%d %H:%M")  # gio server (Asia/Ho_Chi_Minh)
    cha.db_set({"trang_thai": "xong" if nd else "loi", "xong_luc": now_datetime(),
                "ket_qua": json.dumps(kq, ensure_ascii=False),
                "nhat_ky": "" if nd else f"bước viết báo cáo lỗi: {(v.nhat_ky or '')[-500:]}"}, notify=True)
