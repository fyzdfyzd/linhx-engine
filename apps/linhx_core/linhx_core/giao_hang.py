"""Luồng giao hàng chung: đơn chuyển sang da_tra -> phát don.da_tra -> gọi hàm giao của gói theo loai_giao."""
from __future__ import annotations

import copy
import importlib
import json
import pathlib
from typing import Callable

from linhx_core import dang_ky_module, su_kien

LOAI_GIAO_HOP_LE = ("bao_cao", "quyen_dung", "lich", "tep")
TEN_SU_KIEN_DA_TRA = "don.da_tra"

_TRUONG_RIENG_DON = ("so_tien", "trang_thai", "noi_dung_ck", "tx_id", "nguoi", "brand")


def _chuan_chuoi(gia_tri: object) -> str:
	if gia_tri is None or isinstance(gia_tri, bool):
		return ""
	if isinstance(gia_tri, str):
		return gia_tri.strip()
	return str(gia_tri).strip()


def _la_duong_ham_hop_le(duong_ham: object) -> bool:
	if not isinstance(duong_ham, str) or "." not in duong_ham:
		return False
	cac_phan = duong_ham.split(".")
	return len(cac_phan) >= 2 and all(phan.isidentifier() for phan in cac_phan)


def can_phat(trang_thai_cu: object, trang_thai_moi: object) -> bool:
	"""Trả True chỉ khi đơn chuyển từ trạng thái khác 'da_tra' sang 'da_tra'."""
	cu = _chuan_chuoi(trang_thai_cu)
	moi = _chuan_chuoi(trang_thai_moi)
	return moi == "da_tra" and cu != "da_tra"


def chon_ham(loai_giao: str, danh_sach_module: list[dict]) -> str:
	"""Chọn hàm khai ở 'giao' của module.json theo loai_giao; thiếu hoặc trùng đều ném ValueError."""
	if not isinstance(loai_giao, str) or not loai_giao.strip():
		raise ValueError(f"loai_giao không hợp lệ: {loai_giao!r}")
	loai = loai_giao.strip()
	if not isinstance(danh_sach_module, (list, tuple)):
		raise ValueError("danh_sach_module phải là list hoặc tuple")

	ung_vien: list[tuple[str, str]] = []
	for muc in danh_sach_module:
		if not isinstance(muc, dict):
			raise ValueError("phần tử trong danh_sach_module phải là dict")
		bang_giao = muc.get("giao")
		if bang_giao is None:
			continue
		ten_mod = _chuan_chuoi(muc.get("ten")) or "<module>"
		if not isinstance(bang_giao, dict):
			raise ValueError(f"{ten_mod}: trường 'giao' phải là dict")
		if loai not in bang_giao:
			continue
		duong_tho = bang_giao[loai]
		if not isinstance(duong_tho, str) or not _la_duong_ham_hop_le(duong_tho.strip()):
			raise ValueError(f"{ten_mod}: đường hàm giao cho {loai!r} không hợp lệ: {duong_tho!r}")
		ung_vien.append((ten_mod, duong_tho.strip()))

	if not ung_vien:
		raise ValueError(f"không có module nào khai giao cho loai_giao={loai!r}")
	if len(ung_vien) > 1:
		ds_ten = ", ".join(ten for ten, _ in ung_vien)
		raise ValueError(f"trùng khai báo giao cho loai_giao={loai!r} ở các module: {ds_ten}")
	return ung_vien[0][1]


def goi_ham_giao(duong_ham: str, don: dict, goi: dict) -> object:
	"""Nạp động và gọi hàm giao của gói theo đường dẫn 'module.ham' với đối số (don, goi)."""
	if not isinstance(duong_ham, str) or not _la_duong_ham_hop_le(duong_ham.strip()):
		raise ValueError(f"đường hàm giao không hợp lệ: {duong_ham!r}")
	duong_sach = duong_ham.strip()
	ten_module, ten_ham = duong_sach.rsplit(".", 1)
	module = importlib.import_module(ten_module)
	ham = getattr(module, ten_ham, None)
	if not callable(ham):
		raise AttributeError(f"không tìm thấy hàm giao gọi được: {duong_sach!r}")
	return ham(don, goi)


def _lay_danh_sach_module(thu_muc_apps: str | pathlib.Path | None = None) -> list[dict]:
	goc = (
		pathlib.Path(thu_muc_apps)
		if thu_muc_apps is not None
		else pathlib.Path(__file__).resolve().parents[2]
	)
	if not goc.is_dir():
		return []
	ds_module = dang_ky_module.quet(goc)
	if thu_muc_apps is None:
		da_cai = su_kien._lay_tap_app_da_cai_tren_site()
		if da_cai:
			ds_module = [m for m in ds_module if m.get("ten") in da_cai]
	return ds_module


def _doc_don_va_goi_frappe(ten_don: str) -> dict:
	import frappe

	ma_tim = _chuan_chuoi(ten_don)
	if not ma_tim:
		raise ValueError("thiếu mã đơn")

	if frappe.db.exists("LX Don", ma_tim):
		don_doc = frappe.get_doc("LX Don", ma_tim)
	else:
		ten_thuc = frappe.db.get_value("LX Don", {"ma": ma_tim}, "name")
		if not ten_thuc:
			raise ValueError(f"không tìm thấy LX Don '{ma_tim}'")
		don_doc = frappe.get_doc("LX Don", ten_thuc)

	don_dict = dict(don_doc.as_dict())
	don_dict["ma"] = don_dict.get("ma") or don_dict.get("name")

	ma_goi = _chuan_chuoi(don_dict.get("goi"))
	if not ma_goi:
		raise ValueError(f"đơn '{don_dict.get('name')}' thiếu trường goi")

	if frappe.db.exists("LX Goi", ma_goi):
		goi_doc = frappe.get_doc("LX Goi", ma_goi)
	else:
		ten_goi = frappe.db.get_value("LX Goi", {"ma": ma_goi}, "name")
		if not ten_goi:
			raise ValueError(f"không tìm thấy LX Goi '{ma_goi}' của đơn '{don_dict.get('name')}'")
		goi_doc = frappe.get_doc("LX Goi", ten_goi)

	goi_dict = dict(goi_doc.as_dict())
	goi_dict["ma"] = goi_dict.get("ma") or goi_dict.get("name")
	return {
		"don": don_dict,
		"goi": goi_dict,
		"name": don_dict.get("name"),
		"loai_giao": goi_dict.get("loai_giao"),
	}


def _tach_don_va_goi(ket_qua_doc: object, ten_don: str) -> tuple[dict, dict, str]:
	if isinstance(ket_qua_doc, tuple) and len(ket_qua_doc) == 2:
		don_raw, goi_raw = ket_qua_doc
		if not isinstance(don_raw, dict) or not isinstance(goi_raw, dict):
			raise ValueError(f"doc_goi({ten_don!r}) trả tuple không hợp lệ")
		don_dict = copy.deepcopy(don_raw)
		don_dict.setdefault("name", ten_don)
		goi_dict = copy.deepcopy(goi_raw)
		loai_giao = _chuan_chuoi(goi_dict.get("loai_giao") or don_dict.get("loai_giao"))
		return don_dict, goi_dict, loai_giao

	if not isinstance(ket_qua_doc, dict):
		raise ValueError(f"không lấy được thông tin đơn/gói cho đơn {ten_don!r}")

	if isinstance(ket_qua_doc.get("don"), dict) and isinstance(ket_qua_doc.get("goi"), dict):
		don_dict = copy.deepcopy(ket_qua_doc["don"])
		don_dict.setdefault("name", ten_don)
		goi_dict = copy.deepcopy(ket_qua_doc["goi"])
		loai_giao = _chuan_chuoi(
			goi_dict.get("loai_giao")
			or don_dict.get("loai_giao")
			or ket_qua_doc.get("loai_giao")
		)
		return don_dict, goi_dict, loai_giao

	if isinstance(ket_qua_doc.get("goi"), dict):
		don_dict = copy.deepcopy(ket_qua_doc)
		don_dict.setdefault("name", ten_don)
		goi_dict = copy.deepcopy(ket_qua_doc["goi"])
		loai_giao = _chuan_chuoi(ket_qua_doc.get("loai_giao") or goi_dict.get("loai_giao"))
		return don_dict, goi_dict, loai_giao

	la_ban_ghi_don = (
		"goi" in ket_qua_doc
		or _chuan_chuoi(ket_qua_doc.get("name")) == ten_don
		or _chuan_chuoi(ket_qua_doc.get("ma")) == ten_don
		or any(truong in ket_qua_doc for truong in _TRUONG_RIENG_DON)
	)
	loai_giao = _chuan_chuoi(ket_qua_doc.get("loai_giao"))
	if la_ban_ghi_don:
		don_dict = copy.deepcopy(ket_qua_doc)
		don_dict.setdefault("name", ten_don)
		ma_goi = _chuan_chuoi(ket_qua_doc.get("ma_goi") or ket_qua_doc.get("goi"))
		goi_dict = copy.deepcopy(ket_qua_doc)
		if ma_goi:
			goi_dict["name"] = ma_goi
			goi_dict["ma"] = ma_goi
		if loai_giao:
			goi_dict["loai_giao"] = loai_giao
		return don_dict, goi_dict, loai_giao

	goi_dict = copy.deepcopy(ket_qua_doc)
	ma_goi = _chuan_chuoi(goi_dict.get("name") or goi_dict.get("ma"))
	don_dict = copy.deepcopy(ket_qua_doc)
	don_dict["name"] = ten_don
	don_dict["ma"] = ten_don
	if ma_goi:
		don_dict["goi"] = ma_goi
	return don_dict, goi_dict, loai_giao


def xu_ly(
	ban_ghi_su_kien: dict,
	doc_goi: Callable[[str], dict] | None = None,
	danh_sach_module: list[dict] | None = None,
	goi: Callable[[str, dict, dict], object] | None = None,
) -> str:
	"""Đọc du_lieu.don từ sự kiện, lấy gói của đơn, chọn hàm theo loai_giao, gọi và trả đường hàm."""
	if not isinstance(ban_ghi_su_kien, dict):
		raise ValueError("ban_ghi_su_kien phải là dict")
	ten_sk = ban_ghi_su_kien.get("ten")
	if ten_sk is not None and _chuan_chuoi(ten_sk) and _chuan_chuoi(ten_sk) != TEN_SU_KIEN_DA_TRA:
		raise ValueError(f"sự kiện không hỗ trợ giao hàng: {ten_sk!r}")

	du_lieu_tho = ban_ghi_su_kien.get("du_lieu")
	if isinstance(du_lieu_tho, str):
		try:
			du_lieu = json.loads(du_lieu_tho)
		except json.JSONDecodeError as exc:
			raise ValueError("du_lieu của sự kiện không phải JSON hợp lệ") from exc
	else:
		du_lieu = du_lieu_tho

	if not isinstance(du_lieu, dict):
		raise ValueError("sự kiện thiếu du_lieu kiểu dict")

	ten_don = _chuan_chuoi(du_lieu.get("don"))
	if not ten_don:
		raise ValueError("sự kiện thiếu mã đơn trong du_lieu.don")

	ham_doc_goi = _doc_don_va_goi_frappe if doc_goi is None else doc_goi
	if not callable(ham_doc_goi):
		raise TypeError("doc_goi phải là hàm gọi được")

	ds_mod = _lay_danh_sach_module() if danh_sach_module is None else danh_sach_module
	ham_goi = goi_ham_giao if goi is None else goi
	if not callable(ham_goi):
		raise TypeError("goi phải là hàm gọi được")

	don_dict, goi_dict, loai_giao = _tach_don_va_goi(ham_doc_goi(ten_don), ten_don)
	duong_ham = chon_ham(loai_giao, ds_mod)
	ham_goi(duong_ham, don_dict, goi_dict)
	return duong_ham


def nghe(ban_ghi_su_kien: dict) -> str:
	"""Hàm nghe sự kiện 'don.da_tra' của lõi linhx_core (khai trong apps/linhx_core/module.json)."""
	return xu_ly(ban_ghi_su_kien)


def _la_doc_moi(doc: object) -> bool:
	flags = getattr(doc, "flags", None)
	if getattr(flags, "in_insert", False):
		return True
	if getattr(doc, "__islocal", False):
		return True
	is_new_fn = getattr(doc, "is_new", None)
	if callable(is_new_fn):
		try:
			return bool(is_new_fn())
		except Exception:
			return False
	return False


def _lay_trang_thai_tu_doi_tuong(doi_tuong: object) -> object:
	if isinstance(doi_tuong, dict):
		return doi_tuong.get("trang_thai")
	return getattr(doi_tuong, "trang_thai", None)


def _xac_dinh_trang_thai_truoc_luu(doc: object, truy_van_db: bool = False) -> tuple[bool, object]:
	if _la_doc_moi(doc):
		return True, None
	lay_truoc = getattr(doc, "get_doc_before_save", None)
	if callable(lay_truoc):
		truoc = lay_truoc()
		if truoc is not None:
			return True, _lay_trang_thai_tu_doi_tuong(truoc)
	truoc_attr = getattr(doc, "_doc_before_save", None)
	if truoc_attr is not None:
		return True, _lay_trang_thai_tu_doi_tuong(truoc_attr)
	if truy_van_db:
		ten_don = _chuan_chuoi(
			doc.get("name") if isinstance(doc, dict) else getattr(doc, "name", None)
		)
		if ten_don:
			try:
				import frappe

				db = getattr(frappe, "db", None)
				if db is not None and callable(getattr(db, "get_value", None)):
					if not callable(getattr(db, "exists", None)) or db.exists("LX Don", ten_don):
						return True, db.get_value("LX Don", ten_don, "trang_thai")
					return True, None
			except ImportError:
				pass
	return False, None


def ghi_nhan_trang_thai_truoc_luu(doc: object, method: str | None = None) -> None:
	"""Hook before_save trên LX Don: lưu trạng thái cũ trước khi db_insert/db_update ghi đè."""
	da_biet, trang_thai_cu = _xac_dinh_trang_thai_truoc_luu(doc, truy_van_db=True)
	if da_biet:
		try:
			setattr(doc, "_lx_trang_thai_truoc_luu", (True, trang_thai_cu))
		except Exception:
			pass


def _thoat_like_sql(chuoi: str) -> str:
	return chuoi.replace("|", "||").replace("%", "|%").replace("_", "|_")


def _tim_su_kien_da_phat_db(frappe_mod, ten_don: str) -> dict | None:
	db = getattr(frappe_mod, "db", None)
	if db is None:
		return None
	table_exists = getattr(db, "table_exists", None)
	if callable(table_exists) and not table_exists("LX Su Kien"):
		return None
	sql_fn = getattr(db, "sql", None)
	if callable(sql_fn):
		chuoi_json = json.dumps(ten_don, ensure_ascii=False)[1:-1]
		mau_like = f"%{_thoat_like_sql(chuoi_json)}%"
		rows = sql_fn(
			"SELECT name, ten, du_lieu, trang_thai, lan, da_giao, loi "
			"FROM `tabLX Su Kien` "
			"WHERE ten = %s AND du_lieu LIKE %s ESCAPE '|'",
			(TEN_SU_KIEN_DA_TRA, mau_like),
			as_dict=True,
		)
	else:
		rows = frappe_mod.get_all(
			"LX Su Kien",
			filters={"ten": TEN_SU_KIEN_DA_TRA},
			fields=["name", "ten", "du_lieu", "trang_thai", "lan", "da_giao", "loi"],
			ignore_permissions=True,
		)
	for r in rows or []:
		du_lieu = su_kien._doc_du_lieu_dict(r.get("du_lieu"))
		if _chuan_chuoi(du_lieu.get("don")) == ten_don:
			return {
				"name": r.get("name"),
				"ten": TEN_SU_KIEN_DA_TRA,
				"du_lieu": du_lieu,
				"trang_thai": r.get("trang_thai"),
				"lan": int(r.get("lan") or 0),
				"da_giao": su_kien._doc_danh_sach_da_giao(r.get("da_giao")),
				"loi": str(r.get("loi") or ""),
			}
	return None


def phat_khi_don_da_tra(
	doc: object,
	method: str | None = None,
	kho: list | None = None,
) -> dict | None:
	"""Hook on_update trên LX Don: chỉ phát 'don.da_tra' một lần khi đơn chuyển sang 'da_tra'."""
	da_luu = getattr(doc, "_lx_trang_thai_truoc_luu", None)
	if isinstance(da_luu, tuple) and len(da_luu) == 2 and da_luu[0]:
		trang_thai_cu = da_luu[1]
		try:
			delattr(doc, "_lx_trang_thai_truoc_luu")
		except Exception:
			pass
	else:
		_, trang_thai_cu = _xac_dinh_trang_thai_truoc_luu(doc, truy_van_db=False)

	trang_thai_moi = _lay_trang_thai_tu_doi_tuong(doc)
	if not can_phat(trang_thai_cu, trang_thai_moi):
		return None

	ten_don = _chuan_chuoi(
		doc.get("name") or doc.get("ma")
		if isinstance(doc, dict)
		else getattr(doc, "name", None) or getattr(doc, "ma", None)
	)
	if not ten_don:
		return None

	if kho is not None:
		if not isinstance(kho, list):
			raise TypeError("kho phải là list hoặc None")
		for ban_ghi in kho:
			if (
				isinstance(ban_ghi, dict)
				and ban_ghi.get("ten") == TEN_SU_KIEN_DA_TRA
				and _chuan_chuoi(su_kien._doc_du_lieu_dict(ban_ghi.get("du_lieu")).get("don")) == ten_don
			):
				return None
		return su_kien.phat(TEN_SU_KIEN_DA_TRA, {"don": ten_don}, kho=kho)

	import frappe

	db = getattr(frappe, "db", None)
	if db is not None and callable(getattr(db, "table_exists", None)) and db.table_exists("LX Don"):
		sql_fn = getattr(db, "sql", None)
		if callable(sql_fn):
			sql_fn("SELECT name FROM `tabLX Don` WHERE name = %s FOR UPDATE", (ten_don,))

	if _tim_su_kien_da_phat_db(frappe, ten_don) is not None:
		return None

	return su_kien.phat(TEN_SU_KIEN_DA_TRA, {"don": ten_don})
