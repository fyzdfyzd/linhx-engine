"""API Frappe cho thợ kéo và nộp phiếu Agy."""
from __future__ import annotations

import json
import re

import frappe
from frappe.utils import now_datetime

from linhx_core.ops.keo_phieu import (
    DINH_DANG_TG,
    dang_ky_tho,
    keo_phieu,
    xac_thuc_tho,
)
from linhx_core.ops.nop_phieu import nop_phieu

_MAU_HEX_64 = re.compile(r"^[0-9a-fA-F]{64}$")


def _doc_payload(kwargs: dict) -> dict:
    """Đọc dữ liệu JSON từ body request HTTP hoặc kwargs khi gọi trực tiếp."""
    du_lieu: dict = {}
    req = getattr(frappe, "request", None)
    if req is not None:
        try:
            body = req.get_json(silent=True)
            if isinstance(body, dict):
                du_lieu.update(body)
        except Exception:
            pass
        if not du_lieu:
            try:
                raw = req.get_data(as_text=True)
                if raw:
                    body = json.loads(raw)
                    if isinstance(body, dict):
                        du_lieu.update(body)
            except Exception:
                pass
    for k, v in (kwargs or {}).items():
        if k != "cmd" and v is not None:
            du_lieu.setdefault(k, v)
    return du_lieu


def _nap_kho_tho() -> dict:
    """Đọc danh sách mã băm khoá của các thợ từ cấu hình site (`tho_khoa_bam` / `tho_khoa`)."""
    kho: dict = {"tho": {}, "phieu": []}
    cfg: dict = {}
    try:
        duong = frappe.get_site_path("site_config.json")
        with open(duong, encoding="utf-8") as f:
            doc_cfg = json.load(f)
        if isinstance(doc_cfg, dict):
            cfg.update(doc_cfg)
    except Exception:
        pass

    conf = getattr(frappe, "conf", None)
    if conf:
        for ten_muc in ("tho_khoa_bam", "tho_agy", "tho_khoa"):
            gia_tri = getattr(conf, ten_muc, None) or conf.get(ten_muc)
            if isinstance(gia_tri, dict):
                cfg[ten_muc] = gia_tri

    for ten_muc in ("tho_khoa_bam", "tho_agy"):
        bang_bam = cfg.get(ten_muc)
        if isinstance(bang_bam, dict):
            for ma, tt in bang_bam.items():
                ma_chuan = str(ma or "").strip()
                if not ma_chuan:
                    continue
                if isinstance(tt, dict) and isinstance(tt.get("khoa_bam"), str):
                    kho["tho"][ma_chuan] = {
                        "ma_tho": ma_chuan,
                        "khoa_bam": tt["khoa_bam"].strip().lower(),
                    }
                elif isinstance(tt, str) and _MAU_HEX_64.match(tt.strip()):
                    kho["tho"][ma_chuan] = {
                        "ma_tho": ma_chuan,
                        "khoa_bam": tt.strip().lower(),
                    }

    bang_khoa = cfg.get("tho_khoa")
    if isinstance(bang_khoa, dict):
        for ma, khoa_tran in bang_khoa.items():
            ma_chuan = str(ma or "").strip()
            if not ma_chuan or ma_chuan in kho["tho"]:
                continue
            if isinstance(khoa_tran, str) and khoa_tran:
                if _MAU_HEX_64.match(khoa_tran.strip()):
                    kho["tho"][ma_chuan] = {
                        "ma_tho": ma_chuan,
                        "khoa_bam": khoa_tran.strip().lower(),
                    }
                else:
                    dang_ky_tho(kho, ma_chuan, khoa_tran)

    return kho


def _trich_khoa_tran(payload: dict, khoa: str | None) -> str | None:
    if isinstance(khoa, str) and khoa:
        return khoa
    for truong in ("khoa_tran", "khoa"):
        val = payload.get(truong)
        if isinstance(val, str):
            return val
    try:
        hdr = frappe.get_request_header("X-Tho-Khoa")
        if isinstance(hdr, str) and hdr:
            return hdr
        auth = frappe.get_request_header("Authorization")
        if isinstance(auth, str) and auth.strip().lower().startswith("bearer "):
            return auth.strip()[7:].strip()
    except Exception:
        pass
    return khoa


@frappe.whitelist(allow_guest=True, methods=["POST"])
def keo(ma_tho: str | None = None, khoa: str | None = None, **kwargs):
    """API cho thợ kéo phiếu: kiểm khoá thợ, khoá dòng (FOR UPDATE), thu hồi quá hạn và giao phiếu."""
    payload = _doc_payload(kwargs)
    ma = ma_tho if isinstance(ma_tho, str) and ma_tho else payload.get("ma_tho") or payload.get("tho")
    ma_chuan = str(ma or "").strip()
    khoa_tran = _trich_khoa_tran(payload, khoa)

    kho = _nap_kho_tho()
    if not xac_thuc_tho(kho, ma_chuan, khoa_tran):
        frappe.local.response["http_status_code"] = 401
        return {"ok": False, "loi": "unauthorized"}

    luc_dt = now_datetime()
    luc_str = luc_dt.strftime(DINH_DANG_TG) if hasattr(luc_dt, "strftime") else str(luc_dt)

    try:
        dong_khoa = frappe.db.sql(
            """
            SELECT name, loai_phieu, de, vung, trang_thai, tho, giao_luc, so_lan_giao
            FROM `tabLX Phieu Agy`
            WHERE trang_thai IN ('giao', 'duyet')
            ORDER BY creation ASC
            FOR UPDATE
            """,
            as_dict=True,
        )
        ban_dau = {}
        ds_phieu = []
        for d in dong_khoa or []:
            gl = d.get("giao_luc")
            gl_str = gl.strftime(DINH_DANG_TG) if hasattr(gl, "strftime") else (str(gl) if gl else None)
            item = {
                "name": d.get("name"),
                "loai_phieu": d.get("loai_phieu"),
                "de": d.get("de"),
                "vung": d.get("vung"),
                "trang_thai": d.get("trang_thai"),
                "tho": d.get("tho"),
                "giao_luc": gl_str,
                "so_lan_giao": int(d.get("so_lan_giao") or 0),
            }
            ban_dau[item["name"]] = dict(item)
            ds_phieu.append(item)

        kho["phieu"] = ds_phieu
        ma_http, ket_qua = keo_phieu(kho, ma_chuan, khoa_tran, luc_str)
        if ma_http != 200:
            frappe.db.rollback()
            frappe.local.response["http_status_code"] = ma_http
            return ket_qua

        for p in ds_phieu:
            cu = ban_dau.get(p["name"], {})
            if (
                p.get("trang_thai") != cu.get("trang_thai")
                or p.get("tho") != cu.get("tho")
                or p.get("giao_luc") != cu.get("giao_luc")
                or p.get("so_lan_giao") != cu.get("so_lan_giao")
            ):
                frappe.db.set_value(
                    "LX Phieu Agy",
                    p["name"],
                    {
                        "trang_thai": p.get("trang_thai"),
                        "tho": p.get("tho"),
                        "giao_luc": p.get("giao_luc"),
                        "so_lan_giao": int(p.get("so_lan_giao") or 0),
                    },
                )
        frappe.db.commit()
        return ket_qua
    except Exception:
        frappe.db.rollback()
        raise


@frappe.whitelist(allow_guest=True, methods=["POST"])
def nop(
    ma_tho: str | None = None,
    khoa: str | None = None,
    ma_phieu: str | None = None,
    commit: str | None = None,
    nhanh: str | None = None,
    nhat_ky: str | None = None,
    phut: int | float | None = None,
    token: int | None = None,
    **kwargs,
):
    """API cho thợ nộp phiếu: kiểm khoá thợ, chặn nộp phiếu của thợ khác (403),
    lưu commit/nhánh/nhật ký/phút/token và chống tạo bản ghi trùng khi nộp lại cùng commit.
    """
    payload = _doc_payload(kwargs)
    du_lieu_con = payload.get("du_lieu")
    if isinstance(du_lieu_con, dict):
        for k, v in du_lieu_con.items():
            if v is not None:
                payload.setdefault(k, v)

    ma = ma_tho if isinstance(ma_tho, str) and ma_tho else payload.get("ma_tho") or payload.get("tho")
    ma_chuan = str(ma or "").strip()
    khoa_tran = _trich_khoa_tran(payload, khoa)

    kho = _nap_kho_tho()
    if not xac_thuc_tho(kho, ma_chuan, khoa_tran):
        frappe.local.response["http_status_code"] = 401
        return {"ok": False, "loi": "unauthorized"}

    ma_phieu_val = (
        ma_phieu
        if isinstance(ma_phieu, str) and ma_phieu
        else payload.get("ma_phieu") or payload.get("phieu") or payload.get("name")
    )
    ma_phieu_chuan = str(ma_phieu_val or "").strip()
    if not ma_phieu_chuan:
        frappe.local.response["http_status_code"] = 404
        return {"ok": False, "loi": "khong_tim_thay_phieu"}

    du_lieu = {
        "ma_phieu": ma_phieu_chuan,
        "commit": commit if commit is not None else payload.get("commit", ""),
        "nhanh": nhanh if nhanh is not None else payload.get("nhanh", ""),
        "nhat_ky": nhat_ky if nhat_ky is not None else payload.get("nhat_ky", ""),
        "phut": phut if phut is not None else payload.get("phut", 0),
        "token": token if token is not None else payload.get("token", 0),
    }

    luc_dt = now_datetime()
    luc_str = luc_dt.strftime(DINH_DANG_TG) if hasattr(luc_dt, "strftime") else str(luc_dt)

    try:
        dong_khoa = frappe.db.sql(
            """
            SELECT name, loai_phieu, de, vung, trang_thai, tho, giao_luc, so_lan_giao,
                   commit, nhanh, nhat_ky, phut, token, nop_luc
            FROM `tabLX Phieu Agy`
            WHERE name = %s
            FOR UPDATE
            """,
            (ma_phieu_chuan,),
            as_dict=True,
        )
        ds_phieu = []
        for d in dong_khoa or []:
            gl = d.get("giao_luc")
            gl_str = gl.strftime(DINH_DANG_TG) if hasattr(gl, "strftime") else (str(gl) if gl else None)
            nl = d.get("nop_luc")
            nl_str = nl.strftime(DINH_DANG_TG) if hasattr(nl, "strftime") else (str(nl) if nl else None)
            ds_phieu.append(
                {
                    "name": d.get("name"),
                    "loai_phieu": d.get("loai_phieu"),
                    "de": d.get("de"),
                    "vung": d.get("vung"),
                    "trang_thai": d.get("trang_thai"),
                    "tho": d.get("tho"),
                    "giao_luc": gl_str,
                    "so_lan_giao": int(d.get("so_lan_giao") or 0),
                    "commit": d.get("commit"),
                    "nhanh": d.get("nhanh"),
                    "nhat_ky": d.get("nhat_ky"),
                    "phut": d.get("phut"),
                    "token": d.get("token"),
                    "nop_luc": nl_str,
                }
            )

        kho["phieu"] = ds_phieu
        ma_http, ket_qua = nop_phieu(kho, ma_chuan, khoa_tran, du_lieu, luc_str)
        if ma_http in (401, 403, 404) or ma_http != 200:
            frappe.db.rollback()
            frappe.local.response["http_status_code"] = ma_http
            return ket_qua

        if not ket_qua.get("trung"):
            p_moi = ket_qua["phieu"]
            frappe.db.set_value(
                "LX Phieu Agy",
                p_moi["name"],
                {
                    "trang_thai": p_moi.get("trang_thai"),
                    "commit": p_moi.get("commit"),
                    "nhanh": p_moi.get("nhanh"),
                    "nhat_ky": p_moi.get("nhat_ky"),
                    "phut": p_moi.get("phut"),
                    "token": p_moi.get("token"),
                    "nop_luc": p_moi.get("nop_luc"),
                },
            )
            frappe.db.commit()
        else:
            frappe.db.rollback()
        return ket_qua
    except Exception:
        frappe.db.rollback()
        raise
