"""Controller DocType LX Xac Minh Marketing: lưu mã xác nhận dạng băm SHA-256 có hạn dùng và dùng một lần."""
from __future__ import annotations

import re

import frappe
from frappe.model.document import Document

_MAU_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _bao_loi(thong_diep: str) -> None:
    throw_fn = getattr(frappe, "throw", None)
    loi_dl = getattr(frappe, "ValidationError", ValueError)
    if callable(throw_fn):
        throw_fn(thong_diep, loi_dl)
    raise ValueError(thong_diep)


class LXXacMinhMarketing(Document):
    def autoname(self):
        khoa = str(getattr(self, "khoa_kenh", "") or "").strip()
        if khoa:
            self.khoa_kenh = khoa
            self.name = khoa

    def validate(self):
        khoa = str(getattr(self, "khoa_kenh", "") or "").strip()
        if not khoa:
            _bao_loi("LX Xac Minh Marketing bắt buộc phải có khoa_kenh")
        self.khoa_kenh = khoa

        em = str(getattr(self, "email", "") or "").strip()
        if not em:
            _bao_loi("LX Xac Minh Marketing bắt buộc phải có kênh xác nhận (email)")
        self.email = em

        nguoi = str(getattr(self, "nguoi", "") or "").strip()
        if not nguoi:
            _bao_loi("LX Xac Minh Marketing bắt buộc phải có người (nguoi)")
        self.nguoi = nguoi

        ma_bam = str(getattr(self, "ma_bam", "") or "").strip().lower()
        if not _MAU_SHA256.match(ma_bam):
            _bao_loi("Chỉ được lưu mã băm SHA-256 (64 ký tự hex), không lưu mã OTP trần")
        self.ma_bam = ma_bam
        self.da_dung = 1 if bool(int(getattr(self, "da_dung", 0) or 0)) else 0
        self.so_lan_sai = max(0, int(getattr(self, "so_lan_sai", 0) or 0))
