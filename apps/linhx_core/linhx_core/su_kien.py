"""Hàng đợi sự kiện outbox (thuần Python cho kiểm thử; nối DocType LX Su Kien khi chạy trên Frappe)."""
from __future__ import annotations

import copy
import importlib
import json
import pathlib
from typing import Callable

from linhx_core import dang_ky_module

TRAN_LAN = 5
TRANG_THAI_HOP_LE = ("cho", "xong", "hong")
GIOI_HAN_LO_OUTBOX = 100


def _chuan_ten_su_kien(ten: object) -> str:
	if not isinstance(ten, str) or not ten.strip():
		raise ValueError(f"tên sự kiện không hợp lệ: {ten!r}")
	return ten.strip()


def _chuan_du_lieu_su_kien(du_lieu: object) -> dict:
	if du_lieu is None:
		return {}
	if not isinstance(du_lieu, dict):
		raise ValueError("du_lieu của sự kiện phải là dict")
	return copy.deepcopy(du_lieu)


def _doc_du_lieu_dict(gia_tri: object) -> dict:
	if gia_tri is None or gia_tri == "":
		return {}
	if isinstance(gia_tri, dict):
		return copy.deepcopy(gia_tri)
	if isinstance(gia_tri, str):
		try:
			parsed = json.loads(gia_tri)
		except json.JSONDecodeError:
			return {}
		if isinstance(parsed, dict):
			return parsed
	return {}


def _doc_danh_sach_da_giao(gia_tri: object) -> list[str]:
	if gia_tri is None or gia_tri == "":
		return []
	if isinstance(gia_tri, (list, tuple)):
		return [x for x in gia_tri if isinstance(x, str) and x]
	if isinstance(gia_tri, str):
		try:
			parsed = json.loads(gia_tri)
		except json.JSONDecodeError:
			return []
		if isinstance(parsed, list):
			return [x for x in parsed if isinstance(x, str) and x]
	return []


def _lay_ds_ham_cua_su_kien(bang_nghe: dict[str, list[str]] | None, ten_su_kien: str) -> list[str]:
	if not isinstance(bang_nghe, dict) or not ten_su_kien:
		return []
	gia_tri = bang_nghe.get(ten_su_kien)
	if isinstance(gia_tri, str) and gia_tri.strip():
		return [gia_tri.strip()]
	if isinstance(gia_tri, (list, tuple)):
		return list(dict.fromkeys(x.strip() for x in gia_tri if isinstance(x, str) and x.strip()))
	return []


def _dinh_dang_loi(duong_ham: str, exc: BaseException) -> str:
	thong_diep = str(exc).strip()
	ten_loi = type(exc).__name__
	if thong_diep:
		return f"{duong_ham}: {ten_loi}: {thong_diep}"
	return f"{duong_ham}: {ten_loi}"


def _tao_ban_sao_su_kien(ban_ghi: dict) -> dict:
	ban_sao = copy.deepcopy(ban_ghi)
	ban_sao["du_lieu"] = _doc_du_lieu_dict(ban_sao.get("du_lieu"))
	ban_sao["da_giao"] = _doc_danh_sach_da_giao(ban_sao.get("da_giao"))
	return ban_sao


def goi_ham_nghe(duong_ham: str, ban_ghi: dict) -> object:
	"""Nạp động và gọi hàm nghe sự kiện theo đường dẫn 'module.ham'."""
	if not isinstance(duong_ham, str) or "." not in duong_ham:
		raise ValueError(f"đường hàm nghe không hợp lệ: {duong_ham!r}")
	cac_phan = duong_ham.split(".")
	if len(cac_phan) < 2 or not all(phan.isidentifier() for phan in cac_phan):
		raise ValueError(f"đường hàm nghe không hợp lệ: {duong_ham!r}")
	ten_module, ten_ham = duong_ham.rsplit(".", 1)
	module = importlib.import_module(ten_module)
	ham = getattr(module, ten_ham, None)
	if not callable(ham):
		raise AttributeError(f"không tìm thấy hàm nghe gọi được: {duong_ham!r}")
	return ham(ban_ghi)


def _tim_thu_muc_apps_mac_dinh() -> pathlib.Path:
	return pathlib.Path(__file__).resolve().parents[2]


def _lay_tap_app_da_cai_tren_site() -> set[str] | None:
	try:
		import frappe
	except ImportError:
		return None
	local_obj = getattr(frappe, "local", None)
	if not getattr(local_obj, "site", None):
		return None
	lay_ds = getattr(frappe, "get_installed_apps", None)
	if not callable(lay_ds):
		return None
	try:
		ds = lay_ds()
	except Exception:
		return None
	if isinstance(ds, (list, tuple, set)):
		return {str(x) for x in ds if x}
	return None


def lay_bang_nghe(thu_muc_apps: str | pathlib.Path | None = None) -> dict[str, list[str]]:
	"""Quét module.json của các app để dựng bảng ánh xạ tên sự kiện -> danh sách hàm nghe."""
	goc = pathlib.Path(thu_muc_apps) if thu_muc_apps is not None else _tim_thu_muc_apps_mac_dinh()
	if not goc.is_dir():
		return {}
	ds_module = dang_ky_module.quet(goc)
	if thu_muc_apps is None:
		da_cai = _lay_tap_app_da_cai_tren_site()
		if da_cai:
			ds_module = [m for m in ds_module if m.get("ten") in da_cai]

	cac_khoa: list[str] = []
	for khai_bao in ds_module:
		nghe = khai_bao.get("nghe")
		if isinstance(nghe, dict):
			for khoa in nghe:
				if khoa not in cac_khoa:
					cac_khoa.append(khoa)
	return {khoa: dang_ky_module.tim_ham(ds_module, "nghe", khoa) for khoa in cac_khoa}


def _phat_frappe(ten: str, du_lieu: dict) -> dict:
	import frappe

	doc = frappe.get_doc(
		{
			"doctype": "LX Su Kien",
			"ten": ten,
			"du_lieu": json.dumps(du_lieu, ensure_ascii=False, default=str),
			"trang_thai": "cho",
			"lan": 0,
			"da_giao": "[]",
			"loi": "",
		}
	)
	doc.insert(ignore_permissions=True)
	return {
		"name": doc.name,
		"ten": ten,
		"du_lieu": copy.deepcopy(du_lieu),
		"trang_thai": "cho",
		"lan": 0,
		"da_giao": [],
		"loi": "",
	}


def phat(ten: str, du_lieu: dict | None = None, kho: list | None = None) -> dict:
	"""Phát sự kiện mới vào outbox với trạng thái 'cho', lan = 0, da_giao = []."""
	ten_chuan = _chuan_ten_su_kien(ten)
	du_lieu_chuan = _chuan_du_lieu_su_kien(du_lieu)
	if kho is None:
		return _phat_frappe(ten_chuan, du_lieu_chuan)
	if not isinstance(kho, list):
		raise TypeError("kho phải là list hoặc None")
	ban_ghi = {
		"ten": ten_chuan,
		"du_lieu": du_lieu_chuan,
		"trang_thai": "cho",
		"lan": 0,
		"da_giao": [],
		"loi": "",
	}
	kho.append(ban_ghi)
	return ban_ghi


def _chay_kho_bo_nho(
	kho: list,
	bang_nghe: dict[str, list[str]],
	goi: Callable[[str, dict], object],
) -> dict[str, int]:
	so_xong = 0
	so_loi = 0
	for ban_ghi in kho:
		if not isinstance(ban_ghi, dict) or ban_ghi.get("trang_thai") != "cho":
			continue
		lan = int(ban_ghi.get("lan") or 0)
		da_giao = _doc_danh_sach_da_giao(ban_ghi.get("da_giao"))
		ban_ghi["da_giao"] = da_giao
		if lan >= TRAN_LAN:
			ban_ghi["trang_thai"] = "hong"
			so_loi += 1
			continue

		ds_ham = _lay_ds_ham_cua_su_kien(bang_nghe, str(ban_ghi.get("ten") or ""))
		tap_da_giao = set(da_giao)
		cac_loi: list[str] = []

		for duong_ham in ds_ham:
			if duong_ham in tap_da_giao:
				continue
			ban_ghi_goi = _tao_ban_sao_su_kien(ban_ghi)
			try:
				goi(duong_ham, ban_ghi_goi)
			except Exception as exc:
				cac_loi.append(_dinh_dang_loi(duong_ham, exc))
			else:
				da_giao.append(duong_ham)
				tap_da_giao.add(duong_ham)

		if cac_loi:
			lan += 1
			ban_ghi["lan"] = lan
			ban_ghi["loi"] = "; ".join(cac_loi)
			ban_ghi["trang_thai"] = "hong" if lan >= TRAN_LAN else "cho"
			so_loi += 1
		else:
			ban_ghi["trang_thai"] = "xong"
			ban_ghi["loi"] = ""
			so_xong += 1

	return {"xong": so_xong, "loi": so_loi}


def _ghi_log_loi_frappe(ma_su_kien: str, chi_tiet: str) -> None:
	try:
		import frappe

		log_fn = getattr(frappe, "log_error", None)
		if callable(log_fn):
			log_fn(title=f"Lỗi outbox LX Su Kien {ma_su_kien}", message=chi_tiet)
	except Exception:
		pass


def _chay_frappe(
	bang_nghe: dict[str, list[str]] | None = None,
	goi: Callable[[str, dict], object] | None = None,
) -> dict[str, int]:
	import frappe

	bang = lay_bang_nghe() if bang_nghe is None else bang_nghe
	ham_goi = goi_ham_nghe if goi is None else goi

	ds_ma = frappe.get_all(
		"LX Su Kien",
		filters={"trang_thai": "cho"},
		pluck="name",
		order_by="creation asc",
		limit_page_length=GIOI_HAN_LO_OUTBOX,
	)

	so_xong = 0
	so_loi = 0

	for ma_su_kien in ds_ma:
		doc = frappe.get_doc("LX Su Kien", ma_su_kien, for_update=True)
		if doc.trang_thai != "cho":
			frappe.db.commit()
			continue

		lan = int(doc.lan or 0)
		da_giao = _doc_danh_sach_da_giao(doc.da_giao)
		if lan >= TRAN_LAN:
			doc.trang_thai = "hong"
			doc.save(ignore_permissions=True)
			frappe.db.commit()
			so_loi += 1
			continue

		ds_ham = _lay_ds_ham_cua_su_kien(bang, str(doc.ten or ""))
		tap_da_giao = set(da_giao)
		if all(h in tap_da_giao for h in ds_ham):
			doc.trang_thai = "xong"
			doc.loi = ""
			doc.save(ignore_permissions=True)
			frappe.db.commit()
			so_xong += 1
			continue

		da_khoa = True
		da_hoan_tat = False
		da_nhuong_worker_khac = False
		cac_loi: list[str] = []

		for duong_ham in ds_ham:
			if not da_khoa:
				doc = frappe.get_doc("LX Su Kien", ma_su_kien, for_update=True)
				da_khoa = True
			if doc.trang_thai != "cho":
				frappe.db.commit()
				da_khoa = False
				da_nhuong_worker_khac = True
				break
			da_giao = _doc_danh_sach_da_giao(doc.da_giao)
			tap_da_giao = set(da_giao)
			if duong_ham in tap_da_giao:
				continue

			ban_ghi_goi = {
				"name": doc.name,
				"ten": str(doc.ten or ""),
				"du_lieu": _doc_du_lieu_dict(doc.du_lieu),
				"trang_thai": doc.trang_thai,
				"lan": int(doc.lan or 0),
				"da_giao": list(da_giao),
				"loi": str(doc.loi or ""),
			}
			try:
				ham_goi(duong_ham, copy.deepcopy(ban_ghi_goi))
			except Exception as exc:
				cac_loi.append(_dinh_dang_loi(duong_ham, exc))
				frappe.db.rollback()
				da_khoa = False
			else:
				da_giao.append(duong_ham)
				tap_da_giao.add(duong_ham)
				doc.da_giao = json.dumps(da_giao, ensure_ascii=False)
				if not cac_loi and all(h in tap_da_giao for h in ds_ham):
					doc.trang_thai = "xong"
					doc.loi = ""
					doc.save(ignore_permissions=True)
					frappe.db.commit()
					da_khoa = False
					da_hoan_tat = True
					break
				doc.save(ignore_permissions=True)
				frappe.db.commit()
				da_khoa = False

		if da_nhuong_worker_khac:
			continue
		if da_hoan_tat:
			so_xong += 1
			continue

		if not da_khoa:
			doc = frappe.get_doc("LX Su Kien", ma_su_kien, for_update=True)
		if doc.trang_thai != "cho":
			frappe.db.commit()
			continue

		if cac_loi:
			lan_moi = int(doc.lan or 0) + 1
			thong_diep_loi = "; ".join(cac_loi)
			doc.lan = lan_moi
			doc.loi = thong_diep_loi
			doc.trang_thai = "hong" if lan_moi >= TRAN_LAN else "cho"
			doc.save(ignore_permissions=True)
			frappe.db.commit()
			if doc.trang_thai == "hong":
				_ghi_log_loi_frappe(ma_su_kien, thong_diep_loi)
			so_loi += 1
		else:
			doc.trang_thai = "xong"
			doc.loi = ""
			doc.save(ignore_permissions=True)
			frappe.db.commit()
			so_xong += 1

	return {"xong": so_xong, "loi": so_loi}


def chay(
	kho: list | None = None,
	bang_nghe: dict[str, list[str]] | None = None,
	goi: Callable[[str, dict], object] | None = None,
) -> dict[str, int]:
	"""Quét các sự kiện 'cho' trong outbox và giao cho từng hàm nghe chưa nhận."""
	if kho is None:
		return _chay_frappe(bang_nghe=bang_nghe, goi=goi)
	if not isinstance(kho, list):
		raise TypeError("kho phải là list hoặc None")
	bang = lay_bang_nghe() if bang_nghe is None else bang_nghe
	ham_goi = goi_ham_nghe if goi is None else goi
	return _chay_kho_bo_nho(kho, bang, ham_goi)
