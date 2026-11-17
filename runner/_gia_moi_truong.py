from __future__ import annotations

import pytest

from runner import linhx_runner


@pytest.fixture(autouse=True)
def _gia_ram_va_moi_truong_h3(monkeypatch):
    """Dam bao test trong runner/ khong phu thuoc RAM trong that cua may dang chay test."""
    monkeypatch.setattr(linhx_runner, "lay_ram_trong_gb", lambda: 8.0)
    monkeypatch.setattr(linhx_runner, "_doc_ds_model_agy", lambda _cfg=None: linhx_runner.DANH_SACH_MODEL_AGY_DA_BIET)
    monkeypatch.delenv("LINHX_SO_PHIEU", raising=False)
    monkeypatch.delenv("LINHX_NHAN_BAT_KY", raising=False)
    monkeypatch.delenv("LINHX_TRAN_PHUT", raising=False)
    monkeypatch.delenv("LINHX_KHONG_TIEN_PHUT", raising=False)
    monkeypatch.delenv("LINHX_RAM_TOI_THIEU_GB", raising=False)
    monkeypatch.delenv("LINHX_GIOI_HAN_THU_MUC", raising=False)
    monkeypatch.delenv("LINHX_MODEL", raising=False)
    monkeypatch.delenv("LINHX_VAI", raising=False)
    monkeypatch.setenv("LINHX_GHI_HO_SO", "0")
