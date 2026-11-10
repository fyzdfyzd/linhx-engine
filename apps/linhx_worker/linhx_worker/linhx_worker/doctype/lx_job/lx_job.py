import frappe
from frappe.model.document import Document


def _doc_index_cot_don() -> list[dict]:
	"""Đọc danh sách index của cột `don` trên bảng `tabLX Job` (MariaDB/MySQL chuẩn của Frappe v15)."""
	try:
		rows = frappe.db.sql(
			"SHOW INDEX FROM `tabLX Job` WHERE Column_name = 'don'",
			as_dict=True,
		)
		return list(rows or [])
	except Exception:
		return []


def chuan_hoa_don_lx_job(bo_qua_go_trung_neu_da_unique: bool = False) -> None:
	"""Chuyển `don = ''` thành `NULL` và gỡ trùng `don` trên dữ liệu cũ trước khi đồng bộ unique index.

	Khi `bo_qua_go_trung_neu_da_unique=True` (gọi từ `on_doctype_update` ở các lần migrate về sau)
	và bảng đã có sẵn unique index trên cột `don`, bỏ qua bước quét `GROUP BY don HAVING COUNT(*) > 1`
	vì ràng buộc unique của CSDL đã ngăn phát sinh bản ghi trùng mới.
	"""
	if not frappe.db.table_exists("LX Job") or not frappe.db.has_column("LX Job", "don"):
		return
	frappe.db.sql("UPDATE `tabLX Job` SET `don` = NULL WHERE `don` = ''")
	if bo_qua_go_trung_neu_da_unique:
		idxs = _doc_index_cot_don()
		da_co_unique = any(r.get("Key_name") and int(r.get("Non_unique", 1)) == 0 for r in idxs)
		if da_co_unique:
			return
	trung = frappe.db.sql(
		"""SELECT don, COUNT(*) AS so_luong
		FROM `tabLX Job`
		WHERE don IS NOT NULL
		GROUP BY don
		HAVING COUNT(*) > 1""",
		as_dict=True,
	)
	for dong in trung or []:
		ma_don = dong.get("don")
		ds = frappe.db.sql(
			"SELECT name FROM `tabLX Job` WHERE don = %s ORDER BY creation ASC, name ASC",
			(ma_don,),
			as_dict=True,
		)
		for ban_ghi in (ds or [])[1:]:
			frappe.db.sql(
				"UPDATE `tabLX Job` SET `don` = NULL WHERE name = %s",
				(ban_ghi["name"],),
			)


def dam_bao_unique_don_lx_job() -> None:
	"""Đảm bảo bảng `tabLX Job` (MariaDB/MySQL) có đúng một unique index trên cột `don`."""
	if not frappe.db.table_exists("LX Job") or not frappe.db.has_column("LX Job", "don"):
		return
	chuan_hoa_don_lx_job(bo_qua_go_trung_neu_da_unique=True)
	idxs = _doc_index_cot_don()
	unique_keys = {r.get("Key_name") for r in idxs if r.get("Key_name") and int(r.get("Non_unique", 1)) == 0}
	all_keys = {r.get("Key_name") for r in idxs if r.get("Key_name")}
	if not unique_keys:
		frappe.db.add_unique("LX Job", ["don"])
		unique_keys.add("unique_don")
	giu_unique = "don" if "don" in unique_keys else sorted(unique_keys)[0]
	for k in all_keys:
		if k != giu_unique and k in ("unique_don", "don_index"):
			frappe.db.sql_ddl(f"ALTER TABLE `tabLX Job` DROP INDEX `{k}`")


class LXJob(Document):
	def before_validate(self):
		don = str(getattr(self, "don", None) or "").strip()
		self.don = don if don else None

	def validate(self):
		don = str(getattr(self, "don", None) or "").strip()
		self.don = don if don else None
		if self.don:
			trung = frappe.db.exists("LX Job", {"don": self.don, "name": ["!=", self.name]})
			if trung:
				frappe.throw(
					f"Đơn {self.don} đã có việc {trung}",
					getattr(frappe, "DuplicateEntryError", None),
				)

	def on_doctype_update(self):
		dam_bao_unique_don_lx_job()
