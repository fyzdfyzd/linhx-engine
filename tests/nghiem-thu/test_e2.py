"""E2: token và phút mỗi LX Job hiện trên bàn. Job xong có token vào/ra và phút.

Hợp đồng (HOP-DONG.md):
- apps/linhx_worker/linhx_worker/so_lieu.py thuần Python:
    phut(so_giay) -> float | None   round(so_giay / 60, 1); None/0 -> None
    dong(job: dict) -> {"token_vao": int, "token_ra": int, "phut": float | None}   trống -> 0 / None
- api.py `bang` trả thêm cho mỗi job "phut" (từ so_lieu.phut) cạnh token_vao, token_ra (đã có).
- front/index.html bảng #viec có cột tiêu đề "Token vào", "Token ra", "Phút"; job xong hiện số token (cho phép dấu chấm
  ngăn nghìn) và phút; job chưa xong hiện "–" hoặc để trống ở cột phút.
"""
import re

from _chung import GOC, dong_trang, khong_import_frappe_dau_file, nap_module, trang_front_engine

APP = GOC / "apps" / "linhx_worker"


def test_so_lieu():
    sl = nap_module("linhx_worker.so_lieu", APP)
    assert sl.phut(754) == 12.6 and sl.phut(60) == 1.0
    assert sl.phut(0) is None and sl.phut(None) is None
    assert sl.dong({"token_vao": 250000, "token_ra": 34000, "so_giay": 1500}) == {"token_vao": 250000, "token_ra": 34000, "phut": 25.0}
    assert sl.dong({}) == {"token_vao": 0, "token_ra": 0, "phut": None}
    khong_import_frappe_dau_file(APP / "linhx_worker" / "so_lieu.py")


def test_api_bang_tra_phut():
    chu = (APP / "linhx_worker" / "api.py").read_text(encoding="utf-8")
    m = re.search(r"def bang\(\):(.*?)\n@frappe", chu, re.S)
    assert m and "phut" in m.group(1), "bang() phải trả phut cho mỗi job"


def test_ban_hien_token_va_phut():
    jobs = [{"name": "VIEC-00031", "workflow": "ai-noi-gi-ve-brand", "trang_thai": "xong", "tho": "may-cty", "dau_vao": "x",
             "so_giay": 754, "phut": 12.6, "token_vao": 251234, "token_ra": 34567, "creation": "2026-11-09 09:00:00"},
            {"name": "VIEC-00032", "workflow": "kiem-duong-ong", "trang_thai": "dang_chay", "tho": "may-cty", "dau_vao": "y",
             "so_giay": 0, "phut": None, "token_vao": 0, "token_ra": 0, "creation": "2026-11-09 09:10:00"}]
    api = {"/api/method/linhx_worker.api.bang": lambda pt, b: (200, {"message": {"workers": [], "workflows": [], "jobs": jobs,
                                                                                    "dem": {}, "luc": "x", "user": "dh"}}, None)}
    p, b, pg, s, _ = trang_front_engine(api, cho='#viec tr[data-v="VIEC-00031"]')
    try:
        dau = pg.inner_text("#viec tr >> nth=0")
        for cot in ("Token vào", "Token ra", "Phút"):
            assert cot in dau, f"bảng việc thiếu cột {cot}"
        dong = pg.inner_text('#viec tr[data-v="VIEC-00031"]')
        so = dong.replace(".", "").replace(",", "")
        assert "251234" in so and "34567" in so, "job xong phải hiện token vào/ra"
        assert "12.6" in dong or "12,6" in dong, "job xong phải hiện phút"
    finally:
        dong_trang(p, b, s)
