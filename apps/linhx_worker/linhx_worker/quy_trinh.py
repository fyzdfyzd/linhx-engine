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
        "buoc2": "viet-bao-cao",
    }
}


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
        _con(job.name, qt["buoc1"], f"{job.dau_vao}\nai: {ten}\ntrang: {trang}", ten)
    job.db_set({"trang_thai": "dang_chay", "nhan_luc": now_datetime()}, notify=True)


def _cac_con(cha):
    return frappe.get_all("LX Job", filters={"cha": cha}, fields=["name", "workflow", "trang_thai", "nhan_viec", "ket_qua", "nhat_ky"], order_by="creation asc")


def tien_do(cha):
    return [{"buoc": c.nhan_viec, "trang_thai": c.trang_thai} for c in _cac_con(cha)]


def _tra_loi_buoc1(con):
    ds = []
    for c in con:
        d = bao_cao.tach_json(c.ket_qua) if c.trang_thai == "xong" else None
        if not d:
            d = {"ten": c.nhan_viec, "loi": "không hỏi được" if c.trang_thai != "xong" else "kết quả không đúng khuôn", "cau": []}
        d["ten"] = d.get("ten") or c.nhan_viec
        ds.append(d)
    return ds


def gom(cha_name):
    cha = frappe.get_doc("LX Job", cha_name)
    if cha.trang_thai != "dang_chay":
        return
    qt = QUY_TRINH[cha.workflow]
    con = _cac_con(cha_name)
    b1 = [c for c in con if c.workflow == qt["buoc1"]]
    b2 = [c for c in con if c.workflow == qt["buoc2"]]
    if any(c.trang_thai in ("cho", "dang_chay") for c in b1):
        return
    ai = _tra_loi_buoc1(b1)
    if not b2:
        if not any(a.get("cau") for a in ai):
            cha.db_set({"trang_thai": "loi", "nhat_ky": "không AI nào hỏi được"}, notify=True)
            return
        _con(cha_name, qt["buoc2"], f"{cha.dau_vao}\n\nTRA_LOI:\n{json.dumps({'ai': ai}, ensure_ascii=False)}", "viet-bao-cao")
        return
    v = b2[-1]
    if v.trang_thai in ("cho", "dang_chay"):
        return
    nd = bao_cao.tach_json(v.ket_qua) if v.trang_thai == "xong" else None
    kq = {"ai": ai}
    if nd:
        nhan = {(n.get("ai"), n.get("ma")): n for n in nd.get("nhan_cau") or []}
        for a in ai:
            for c in a.get("cau") or []:
                c.update({k: x for k, x in (nhan.get((a.get("ten"), c.get("ma"))) or {}).items() if k not in ("ai", "ma")})
        for k in ("ngay", "trich_sai", "buoc_roi", "lop_yeu", "ke_hoach_30_ngay", "ket_luan"):
            kq[k] = nd.get(k)
    kq["ngay"] = kq.get("ngay") or now_datetime().strftime("%Y-%m-%d %H:%M")
    cha.db_set({"trang_thai": "xong" if nd else "loi", "xong_luc": now_datetime(),
                "ket_qua": json.dumps(kq, ensure_ascii=False),
                "nhat_ky": "" if nd else f"bước viết báo cáo lỗi: {(v.nhat_ky or '')[-500:]}"}, notify=True)
