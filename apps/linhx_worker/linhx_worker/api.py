"""API hang viec agy. Tho (cloud hay may rieng) KEO viec, server khong goi vao may nao.

Tho:   heartbeat -> nhan_viec -> (chay agy) -> bao_ket_qua
Mat tien (linhx-front): bang, giao_viec, huy_viec
"""
import hmac
import json

import frappe
from frappe.rate_limiter import rate_limit

from linhx_worker import bao_cao, quy_trinh, so_lieu
from frappe.utils import add_to_date, now_datetime, time_diff_in_seconds

PHIEN_BAN_API = "0.1"
OFFLINE_SAU_GIAY = 120


# ---------- quyen ----------

def _la_dieu_hanh():
    roles = set(frappe.get_roles())
    if not roles & {"System Manager", "LX Operator"}:
        frappe.throw("Cần quyền LX Operator", frappe.PermissionError)


def _lay_tho(ma):
    if not ma or not frappe.db.exists("LX Worker", ma):
        frappe.throw(f"Không có thợ {ma}", frappe.DoesNotExistError)
    tho = frappe.get_doc("LX Worker", ma)
    if "System Manager" not in frappe.get_roles() and tho.user != frappe.session.user:
        frappe.throw("Khoá API không thuộc thợ này", frappe.PermissionError)
    return tho


def _ds(chuoi):
    return [x.strip() for x in (chuoi or "").replace("\n", ",").split(",") if x.strip()]


def _workflow_cho_tho(tho):
    nhan = set(_ds(tho.nhan))
    chi_nhan = set(_ds(tho.workflows))
    kq = []
    for wf in frappe.get_all("LX Workflow", filters={"bat": 1, "che_do": ["!=", "gop"]}, fields=["name", "nhan_can"]):
        if chi_nhan and wf.name not in chi_nhan:
            continue
        if wf.nhan_can and wf.nhan_can not in nhan:
            continue
        kq.append(wf.name)
    return kq


# ---------- tho ----------

@frappe.whitelist(methods=["POST"])
def heartbeat(ma, phien_ban=None, may=None):
    tho = _lay_tho(ma)
    vals = {"lan_cuoi": now_datetime()}
    if phien_ban:
        vals["phien_ban"] = phien_ban
    if may:
        vals["may"] = may
    if tho.trang_thai == "offline":
        vals["trang_thai"] = "ranh"
    frappe.db.set_value("LX Worker", ma, vals, update_modified=False)
    return {"ok": True, "tam_dung": tho.tam_dung, "api": PHIEN_BAN_API}


@frappe.whitelist(methods=["POST"])
def nhan_viec(ma, phien_ban=None, may=None):
    """Tra ve 1 viec hoac None. Khoa hang bang SKIP LOCKED de nhieu tho khong tranh nhau."""
    tho = _lay_tho(ma)
    heartbeat(ma, phien_ban, may)
    if tho.tam_dung:
        return None
    # tho hoi viec moi trong khi van con viec dang_chay: tho da chet giua chung -> tra viec cu ve hang
    if tho.viec_hien_tai and frappe.db.get_value("LX Job", tho.viec_hien_tai, "trang_thai") == "dang_chay":
        frappe.db.set_value("LX Job", tho.viec_hien_tai, {"trang_thai": "cho", "tho": None,
                            "nhat_ky": f"thợ {ma} khởi động lại giữa chừng, trả về hàng"})
    wfs = _workflow_cho_tho(tho)
    if not wfs:
        return None
    rows = frappe.db.sql(
        """select name from `tabLX Job`
        where trang_thai='cho' and workflow in %(wfs)s
          and (ifnull(muon_tho,'')='' or muon_tho=%(ma)s)
        order by creation asc limit 1 for update skip locked""",
        {"wfs": tuple(wfs), "ma": ma},
    )
    if not rows:
        frappe.db.rollback()
        return None
    job = frappe.get_doc("LX Job", rows[0][0])
    wf = frappe.get_doc("LX Workflow", job.workflow)
    de = (wf.de_mau or "{dau_vao}").replace("{dau_vao}", job.dau_vao or "")
    job.db_set({
        "trang_thai": "dang_chay", "tho": ma, "nhan_luc": now_datetime(),
        "de_gui": de, "lan_thu": (job.lan_thu or 0) + 1,
    }, notify=True)
    frappe.db.set_value("LX Worker", ma, {"trang_thai": "ban", "viec_hien_tai": job.name}, update_modified=False)
    frappe.db.commit()
    return {
        "viec": job.name, "workflow": wf.name, "che_do": wf.che_do or "agy",
        "de": de, "dau_vao": job.dau_vao, "tran_phut": wf.tran_phut or 40,
    }


@frappe.whitelist(methods=["POST"])
def bao_ket_qua(ma, viec, trang_thai, ket_qua=None, nhat_ky=None, token_vao=None, token_ra=None):
    _lay_tho(ma)
    if trang_thai not in ("xong", "loi"):
        frappe.throw("trang_thai phải là xong hoặc loi")
    job = frappe.get_doc("LX Job", viec)
    if job.tho != ma or job.trang_thai != "dang_chay":
        frappe.throw("Việc không còn thuộc thợ này", frappe.ValidationError)
    xong = now_datetime()
    job.db_set({
        "trang_thai": trang_thai, "xong_luc": xong,
        "so_giay": time_diff_in_seconds(xong, job.nhan_luc) if job.nhan_luc else 0,
        "ket_qua": (ket_qua or "")[:200000], "nhat_ky": (nhat_ky or "")[-50000:],
        "token_vao": int(token_vao or 0), "token_ra": int(token_ra or 0),
    }, notify=True)
    frappe.db.set_value("LX Worker", ma, {"trang_thai": "ranh", "viec_hien_tai": None}, update_modified=False)
    if job.cha:
        quy_trinh.gom(job.cha)
    frappe.db.commit()
    return {"ok": True}


# ---------- mat tien ----------

@frappe.whitelist(allow_guest=True)
def phien():
    """Mat tien goi dau tien: biet ai dang dang nhap va lay CSRF de POST."""
    from frappe.sessions import get_csrf_token
    u = frappe.session.user
    return {"user": u, "dieu_hanh": bool(set(frappe.get_roles()) & {"System Manager", "LX Operator"}),
            "csrf": get_csrf_token() if u != "Guest" else None}


@frappe.whitelist()
def bang():
    _la_dieu_hanh()
    workers = frappe.get_all("LX Worker", fields=["ma", "loai", "may", "trang_thai", "nhan", "lan_cuoi", "viec_hien_tai", "tam_dung", "phien_ban"], order_by="loai asc, ma asc")
    workflows = frappe.get_all("LX Workflow", filters={"bat": 1}, fields=["ma", "ten", "mo_ta", "che_do", "nhan_can", "tran_phut", "vi_du"], order_by="creation asc")
    jobs = frappe.get_all("LX Job", fields=["name", "workflow", "trang_thai", "tho", "muon_tho", "cha", "nhan_viec", "creation", "nhan_luc", "xong_luc", "so_giay", "dau_vao", "token_vao", "token_ra"], order_by="creation desc", limit=40)
    for j in jobs:
        j.dau_vao = (j.dau_vao or "")[:160]
        j["phut"] = so_lieu.phut(j.get("so_giay"))
    dem = {r[0]: r[1] for r in frappe.db.sql("select trang_thai, count(*) from `tabLX Job` group by trang_thai")}
    return {"workers": workers, "workflows": workflows, "jobs": jobs, "dem": dem, "luc": now_datetime(), "user": frappe.session.user}


@frappe.whitelist()
def bang_tho():
    _la_dieu_hanh()
    from linhx_worker import bang_tho as _bt
    kq = _bt.tong_hop(_bt.doc_phieu(), _bt.doc_dang_chay())
    # Lúc file dang-chay.json được đẩy lên VM gần nhất (giây epoch); front tô đỏ nếu quá 30 phút
    f = _bt._GOC / ".canh" / "dang-chay.json"
    kq["cap_nhat"] = int(f.stat().st_mtime) if f.exists() else None
    return kq


@frappe.whitelist()
def chi_tiet(viec):
    _la_dieu_hanh()
    return frappe.get_doc("LX Job", viec).as_dict()


@frappe.whitelist(methods=["POST"])
def giao_viec(workflow, dau_vao, muon_tho=None):
    _la_dieu_hanh()
    if not frappe.db.get_value("LX Workflow", workflow, "bat"):
        frappe.throw("Workflow không có hoặc đang tắt")
    job = frappe.get_doc({"doctype": "LX Job", "workflow": workflow, "dau_vao": dau_vao, "muon_tho": muon_tho or None})
    job.insert()
    if quy_trinh.la_gop(workflow):
        quy_trinh.chia(job)
    frappe.db.commit()
    return {"viec": job.name}


@frappe.whitelist(methods=["POST"])
def duyet_viec(viec):
    _la_dieu_hanh()
    job = frappe.get_doc("LX Job", viec)
    if job.trang_thai == "cho_duyet":
        if quy_trinh.la_gop(job.workflow):
            quy_trinh.chia(job)
        else:
            job.db_set("trang_thai", "cho", notify=True)
    return {"ok": True}


@frappe.whitelist(methods=["POST"])
def chay_lai(viec):
    _la_dieu_hanh()
    job = frappe.get_doc("LX Job", viec)
    if job.trang_thai in ("loi", "huy", "xong", "dang_chay"):
        if job.tho:
            frappe.db.set_value("LX Worker", job.tho, {"trang_thai": "ranh", "viec_hien_tai": None}, update_modified=False)
        if quy_trinh.la_gop(job.workflow):
            for c in frappe.get_all("LX Job", filters={"cha": job.name}, pluck="name"):
                frappe.delete_doc("LX Job", c, ignore_permissions=True, force=True)
            quy_trinh.chia(job)
        else:
            job.db_set({"trang_thai": "cho", "tho": None, "ket_qua": None}, notify=True)
            if job.cha:
                frappe.db.set_value("LX Job", job.cha, "trang_thai", "dang_chay")
    return {"ok": True}


@frappe.whitelist(methods=["POST"])
def gom_lai(viec):
    """Giu ket qua hoi AI (buoc 1), xoa cac buoc sau roi cham + viet lai."""
    _la_dieu_hanh()
    job = frappe.get_doc("LX Job", viec)
    qt = quy_trinh.QUY_TRINH.get(job.workflow)
    if not qt:
        frappe.throw("Không phải quy trình gộp")
    for c in frappe.get_all("LX Job", filters={"cha": viec, "workflow": ["!=", qt["buoc1"]]}, pluck="name"):
        frappe.delete_doc("LX Job", c, ignore_permissions=True, force=True)
    job.db_set({"trang_thai": "dang_chay", "ket_qua": None}, notify=True)
    quy_trinh.gom(viec)
    frappe.db.commit()
    return {"ok": True}


@frappe.whitelist(methods=["POST"])
def huy_viec(viec):
    _la_dieu_hanh()
    job = frappe.get_doc("LX Job", viec)
    if job.trang_thai in ("cho_duyet", "cho", "dang_chay"):
        job.db_set("trang_thai", "huy", notify=True)
        for c in frappe.get_all("LX Job", filters={"cha": job.name, "trang_thai": ["in", ["cho", "dang_chay"]]}, pluck="name"):
            frappe.db.set_value("LX Job", c, "trang_thai", "huy")
        if job.tho:
            frappe.db.set_value("LX Worker", job.tho, {"trang_thai": "ranh", "viec_hien_tai": None}, update_modified=False)
    return {"ok": True}


# ---------- khach (cong khai) ----------
# Khach KHONG bao gio kich agy truc tiep: viec cua khach vao trang thai cho_duyet,
# nguoi dieu hanh bam duyet thi moi vao hang.

WORKFLOW_KHACH = {"ai-noi-gi-ve-brand"}


def _ip():
    return getattr(frappe.local, "request_ip", None) or "?"


def _mot_dong(chuoi, toi_da, mac_dinh=""):
    s = str(chuoi or "").replace("\r", " ").replace("\n", " ").strip()
    if not s and mac_dinh:
        s = mac_dinh
    return s[:toi_da]


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=5, seconds=3600)
def dat_bao_cao(brand, nganh="", thi_truong="Việt Nam", doi_thu="", su_that="", email="", ten=""):
    brand = _mot_dong(brand, 80)
    if len(brand) < 2:
        frappe.throw("Cần tên thương hiệu")
    dau_vao = "\n".join([
        f"brand: {brand}",
        f"nganh: {_mot_dong(nganh, 80)}",
        f"thi_truong: {_mot_dong(thi_truong, 60, 'Việt Nam')}",
        f"doi_thu: {_mot_dong(doi_thu, 120)}",
        f"su_that: {_mot_dong(su_that, 600)}",
    ])
    ma_xem = frappe.generate_hash(length=12)
    job = frappe.get_doc({
        "doctype": "LX Job", "workflow": "ai-noi-gi-ve-brand", "dau_vao": dau_vao,
        "trang_thai": "cho_duyet", "nguon": "khach", "ma_xem": ma_xem,
        "email_khach": _mot_dong(email, 120) or None, "ten_khach": _mot_dong(ten, 80),
    })
    job.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"viec": job.name, "ma_xem": ma_xem}


@frappe.whitelist(allow_guest=True)
def xem_bao_cao(viec, ma_xem):
    d = frappe.db.get_value("LX Job", viec, ["ma_xem", "trang_thai", "ket_qua", "dau_vao", "creation", "xong_luc", "nguon"], as_dict=True)
    ma_db = str((d or {}).get("ma_xem") or "")
    ma_gui = str(ma_xem or "")
    if not d or d.nguon not in ("khach", "don") or not ma_db or not ma_gui or not hmac.compare_digest(ma_db.encode("utf-8"), ma_gui.encode("utf-8")):
        frappe.throw("Không tìm thấy báo cáo", frappe.DoesNotExistError)
    tr = d.trang_thai
    truoc = 0
    if tr in ("cho_duyet", "cho"):
        truoc = frappe.db.count("LX Job", {"trang_thai": ["in", ["cho", "dang_chay"]], "creation": ["<", d.creation]})
    return {
        "viec": viec, "trang_thai": tr, "dau_vao": d.dau_vao, "truoc": truoc,
        "bao_cao": bao_cao.dung(d.ket_qua) if tr == "xong" else None, "xong_luc": d.xong_luc,
        "tien_do": quy_trinh.tien_do(viec) if tr == "dang_chay" else [],
    }


# ---------- don dep moi phut ----------

def don_dep():
    moc = add_to_date(now_datetime(), seconds=-OFFLINE_SAU_GIAY)
    frappe.db.sql("update `tabLX Worker` set trang_thai='offline' where trang_thai!='offline' and (lan_cuoi is null or lan_cuoi < %s)", moc)
    for j in frappe.get_all("LX Job", filters={"trang_thai": "dang_chay", "tho": ["is", "set"]}, fields=["name", "workflow", "nhan_luc", "lan_thu", "tho"]):
        tran = (frappe.db.get_value("LX Workflow", j.workflow, "tran_phut") or 40) + 5
        if j.nhan_luc and time_diff_in_seconds(now_datetime(), j.nhan_luc) > tran * 60:
            moi = "cho" if (j.lan_thu or 0) < 2 else "loi"
            frappe.db.set_value("LX Job", j.name, {"trang_thai": moi, "tho": None, "nhat_ky": f"quá trần {tran} phút, chuyển {moi}"})
            frappe.db.set_value("LX Worker", j.tho, {"viec_hien_tai": None}, update_modified=False)
            if moi == "loi":
                cha = frappe.db.get_value("LX Job", j.name, "cha")
                if cha:
                    quy_trinh.gom(cha)
    frappe.db.commit()
