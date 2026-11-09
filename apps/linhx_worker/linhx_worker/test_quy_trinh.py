"""Kiểm thử đơn vị cho linhx_worker.quy_trinh (tách việc con từ việc cha quy trình gộp ở trạng thái `cho`)."""
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import sys


def test_chia_viec_gop_cho_tu_tach_viec_con():
	fake_frappe = MagicMock()
	fake_utils = MagicMock()
	fake_utils.now_datetime.return_value = "2026-11-09 10:00:00"

	viec_con_da_tao = []
	trang_thai_cha = {"tt": "cho"}

	def fake_get_all(doctype, filters=None, **kwargs):
		if doctype == "LX Workflow":
			return [SimpleNamespace(name="ai-noi-gi-ve-brand")]
		if doctype == "LX Job" and isinstance(filters, dict) and filters.get("cha") == "VIEC-00001":
			return list(viec_con_da_tao)
		return []

	fake_frappe.get_all.side_effect = fake_get_all
	fake_frappe.db.sql.return_value = [("VIEC-00001",)]

	doc_cha = MagicMock()
	doc_cha.name = "VIEC-00001"
	doc_cha.workflow = "ai-noi-gi-ve-brand"
	doc_cha.dau_vao = "brand: Trà Đồi Mây\nnganh: Trà\nthi_truong: Việt Nam\ndoi_thu: \nsu_that: "

	def _doc_trang_thai():
		return trang_thai_cha["tt"]

	type(doc_cha).trang_thai = property(lambda self: _doc_trang_thai())

	def fake_db_set(vals, notify=False):
		if isinstance(vals, dict) and "trang_thai" in vals:
			trang_thai_cha["tt"] = vals["trang_thai"]

	doc_cha.db_set.side_effect = fake_db_set

	def fake_get_doc(arg1, arg2=None):
		if arg1 == "LX Job" and arg2 == "VIEC-00001":
			return doc_cha
		if isinstance(arg1, dict) and arg1.get("doctype") == "LX Job":
			doc_con = MagicMock()

			def _insert_con(ignore_permissions=False):
				viec_con_da_tao.append(
					SimpleNamespace(
						name=f"VIEC-{len(viec_con_da_tao) + 2:05d}",
						workflow=arg1["workflow"],
						trang_thai=arg1["trang_thai"],
						nhan_viec=arg1["nhan_viec"],
						cha=arg1["cha"],
					)
				)

			doc_con.insert.side_effect = _insert_con
			return doc_con
		return MagicMock()

	fake_frappe.get_doc.side_effect = fake_get_doc

	with patch.dict(sys.modules, {"frappe": fake_frappe, "frappe.utils": fake_utils}):
		sys.modules.pop("linhx_worker.quy_trinh", None)
		from linhx_worker import quy_trinh

		quy_trinh.chia_viec_gop_cho()
		assert trang_thai_cha["tt"] == "dang_chay"
		assert len(viec_con_da_tao) == 9
		assert all(c.workflow == "hoi-mot-ai" and c.trang_thai == "cho" for c in viec_con_da_tao)

		# Gọi lại lần 2 không tách trùng việc con
		quy_trinh.chia_viec_gop_cho()
		assert len(viec_con_da_tao) == 9
