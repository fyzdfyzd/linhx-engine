"""Module thanh toán (pay) của linhx_core."""
import importlib
import sys
import types


def _chuan_hoa_tx_id_rong() -> None:
	"""Đổi các giá trị `tx_id = ''` cũ trên `tabLX Don` thành `NULL` trước khi đồng bộ unique index."""
	try:
		frappe_mod = sys.modules.get("frappe")
		db = getattr(frappe_mod, "db", None) if frappe_mod is not None else None
		if db is not None and getattr(frappe_mod, "local", None) is not None:
			if getattr(db, "table_exists", None) and db.table_exists("LX Don"):
				db.sql("UPDATE `tabLX Don` SET `tx_id` = NULL WHERE `tx_id` = ''")
	except Exception:
		pass


def _ghi_so_s1a_tu_don_qua_cung_cap(doc_don, method: str | None = None) -> object | None:
	"""Tra hàm `vn.ghi_so_s1a_tu_don` qua `dang_ky_module` cho controller `LXDon`."""
	try:
		from linhx_core.api import tim_ham

		ds_ham = tim_ham("cung_cap", "vn.ghi_so_s1a_tu_don")
		if not ds_ham:
			return None
		ten_module, ten_ham = ds_ham[0].rsplit(".", 1)
		mod = importlib.import_module(ten_module)
		ham = getattr(mod, ten_ham, None)
		if callable(ham):
			return ham(doc_don)
	except Exception:
		pass
	return None


def dang_ky_auth_hook() -> None:
	try:
		if "linhx_core.pay.so_s1a" not in sys.modules:
			mod_proxy = types.ModuleType("linhx_core.pay.so_s1a")
			mod_proxy.ghi_so_s1a_tu_don = _ghi_so_s1a_tu_don_qua_cung_cap
			sys.modules["linhx_core.pay.so_s1a"] = mod_proxy

		import linhx_core.hooks as _hooks
		from linhx_core.api import tim_ham

		ds_hook = tim_ham("cung_cap", "vn.xac_thuc_sepay_hook")
		ds = list(getattr(_hooks, "auth_hooks", None) or [])
		co_thay_doi = False
		for hook_fn in ds_hook:
			if hook_fn not in ds:
				ds.append(hook_fn)
				co_thay_doi = True
		if co_thay_doi:
			_hooks.auth_hooks = ds

		frappe_mod = sys.modules.get("frappe")
		if frappe_mod is not None and getattr(frappe_mod, "local", None) is not None:
			load_fn = getattr(frappe_mod, "_load_app_hooks", None)
			if hasattr(load_fn, "clear_cache"):
				load_fn.clear_cache()
			cache_obj = getattr(frappe_mod, "cache", None)
			if hasattr(cache_obj, "delete_value"):
				cache_obj.delete_value("app_hooks")
			elif callable(cache_obj):
				c = cache_obj()
				if c is not None and hasattr(c, "delete_value"):
					c.delete_value("app_hooks")
	except Exception:
		pass


dang_ky_auth_hook()
_chuan_hoa_tx_id_rong()
