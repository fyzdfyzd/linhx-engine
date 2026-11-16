"""Vá runner 15/11: phiếu loai: lenh chạy script đã commit."""
import io
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runner import linhx_runner as lr  # noqa: E402


@pytest.mark.skipif(os.name == "nt", reason="dùng script .sh giả trên Linux")
def test_phieu_lenh_chay_script_da_commit(tmp_path, monkeypatch):
    thu = tmp_path / "lenh"
    thu.mkdir()
    (thu / "chao.sh").write_text("echo xin-chao\n", encoding="utf-8")
    monkeypatch.setattr(lr, "THU_MUC_LENH", thu)
    tt, kq, *_ = lr.chay_agy({"thu_muc": str(tmp_path)}, {"viec": "hd-lenh-chao", "loai": "lenh",
                                                          "meta": {"lenh": "chao"}, "tran_phut": 3, "de": ""})
    assert tt == "xong" and "xin-chao" in kq


def test_phieu_lenh_ten_doc_hoac_khong_co(tmp_path, monkeypatch):
    monkeypatch.setattr(lr, "THU_MUC_LENH", tmp_path)
    for ten in ("../x", "a b", ""):
        tt, *_ = lr.chay_agy({}, {"viec": "v", "loai": "lenh", "meta": {"lenh": ten}, "de": ""})
        assert tt == "loi"
    tt, _, nk, *_ = lr.chay_agy({}, {"viec": "v", "loai": "lenh", "meta": {"lenh": "khong-co"}, "de": ""})
    assert tt == "loi" and "không có script" in nk


def test_co_ban_runner_moi_khi_head_doi(tmp_path):
    (tmp_path / ".git").mkdir()
    heads = iter(["aaa", "", "bbb"])

    class R:
        def __init__(self, out):
            self.stdout = out
            self.returncode = 0

    def chay(cmd, **kw):
        return R(next(heads) if "rev-parse" in cmd else "") if "rev-parse" in cmd else R("")
    heads = iter(["aaa", "bbb"])
    assert lr.co_ban_runner_moi(tmp_path, chay) is True
    heads = iter(["aaa", "aaa"])
    assert lr.co_ban_runner_moi(tmp_path, chay) is False
