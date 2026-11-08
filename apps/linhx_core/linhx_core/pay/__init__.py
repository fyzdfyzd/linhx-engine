"""Module thanh toán (pay) của linhx_core."""
import sys


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


def dang_ky_auth_hook() -> None:
	try:
		import linhx_core.hooks as _hooks

		hook_fn = "linhx_core.pay.api_sepay.xac_thuc_sepay_hook"
		ds = list(getattr(_hooks, "auth_hooks", None) or [])
		if hook_fn not in ds:
			ds.append(hook_fn)
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
