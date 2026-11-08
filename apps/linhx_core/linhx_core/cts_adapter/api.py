"""Endpoint Frappe cho adapter Chiêm Tinh Số (CTS): checkout và sepay_webhook."""
from __future__ import annotations

import json

import frappe

from linhx_core.cts_adapter import hop_dong

_KHO_TAM: dict[str, list] = {"don": [], "tx": []}
_CACHE_KEY = "linhx_cts_adapter_kho"


def _doc_payload(kwargs: dict) -> dict:
    req = getattr(frappe, "request", None)
    if req is not None:
        try:
            du_lieu = req.get_json(silent=True)
            if isinstance(du_lieu, dict):
                return dict(du_lieu)
        except Exception:
            pass
        try:
            raw = req.get_data(as_text=True)
            if raw:
                du_lieu = json.loads(raw)
                if isinstance(du_lieu, dict):
                    return dict(du_lieu)
        except Exception:
            pass
    return {k: v for k, v in (kwargs or {}).items() if k != "cmd"}


def _doc_secret_webhook() -> str:
    conf = getattr(frappe, "conf", None) or {}
    gia_tri = conf.get("cts_sepay_khoa") or conf.get("sepay_khoa")
    try:
        duong = frappe.get_site_path("site_config.json")
        with open(duong, encoding="utf-8") as f:
            cfg = json.load(f)
        if cfg.get("cts_sepay_khoa") or cfg.get("sepay_khoa"):
            gia_tri = cfg.get("cts_sepay_khoa") or cfg.get("sepay_khoa")
    except Exception:
        pass
    return str(gia_tri or "").strip()


def _doc_danh_muc() -> dict:
    conf = getattr(frappe, "conf", None) or {}
    dm = conf.get("cts_danh_muc")
    if isinstance(dm, dict) and dm:
        return dm
    return dict(hop_dong.DANH_MUC_MAC_DINH)


def _doc_kho() -> dict:
    kho_local = getattr(getattr(frappe, "local", None), "_cts_kho", None)
    if isinstance(kho_local, dict):
        return kho_local
    try:
        cache = frappe.cache()
        raw = cache.get_value(_CACHE_KEY)
        if isinstance(raw, dict) and isinstance(raw.get("don"), list) and isinstance(raw.get("tx"), list):
            return raw
    except Exception:
        pass
    return _KHO_TAM


def _luu_kho(kho: dict) -> None:
    try:
        frappe.cache().set_value(_CACHE_KEY, kho)
    except Exception:
        pass


@frappe.whitelist(allow_guest=True, methods=["POST"])
def checkout(**kwargs):
    """Nhận yêu cầu tạo đơn CTS (POST /v1/checkout) và trả kết quả cùng dạng CTS."""
    payload = _doc_payload(kwargs)
    danh_muc = _doc_danh_muc()
    kho = _doc_kho()
    ma_http, than = hop_dong.tao_don(payload, danh_muc, kho)
    _luu_kho(kho)
    if getattr(frappe.local, "response", None) is not None:
        frappe.local.response["http_status_code"] = ma_http
    return than


@frappe.whitelist(allow_guest=True, methods=["POST"])
def sepay_webhook(**kwargs):
    """Nhận webhook SePay của CTS (POST /v1/pay/sepay/webhook) và trả kết quả cùng dạng CTS."""
    authorization = frappe.get_request_header("Authorization")
    payload = _doc_payload(kwargs)
    kho = _doc_kho()
    ma_http, than = hop_dong.nhan_webhook(
        payload,
        kho,
        authorization,
        _doc_secret_webhook(),
    )
    _luu_kho(kho)
    if getattr(frappe.local, "response", None) is not None:
        frappe.local.response["http_status_code"] = ma_http
    return than
