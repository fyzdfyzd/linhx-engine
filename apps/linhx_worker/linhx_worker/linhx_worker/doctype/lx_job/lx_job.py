import frappe
from frappe.model.document import Document


def chuan_hoa_don_lx_job() -> None:
	"""Chuyển `don = ''` thành `NULL` và gỡ trùng `don` trên dữ liệu cũ trước khi đồng bộ unique index."""
	if not frappe.db.table_exists("LX Job") or not frappe.db.has_column("LX Job", "don"):
		return
	frappe.db.sql("UPDATE `tabLX Job` SET `don` = NULL WHERE `don` = ''")
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
				frappe.throw(f"Đơn {self.don} đã có việc {trung}")

	def on_doctype_update(self):
		chuan_hoa_don_lx_job()
