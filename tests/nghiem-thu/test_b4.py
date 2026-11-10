"""B4: đơn báo cáo 'AI nói gì' đã trả tự tạo LX Job, giao link báo cáo, bỏ duyệt tay. Đơn da_tra sinh Job trong 1 phút.

Hợp đồng (HOP-DONG.md):
- linhx_core/pay/sau_tra.py thuần Python:
    viec_can_tao(don: dict, goi: dict, job_da_co: list[dict]) -> dict | None
        chỉ khi don["trang_thai"] == "da_tra", goi có "workflow", và chưa có job nào job["don"] == don["ma"];
        trả {"workflow": goi["workflow"], "dau_vao": str (có brand của đơn), "trang_thai": "cho", "nguon": "don",
             "don": don["ma"], "email_khach": don.get("email")}
        trang_thai "cho" (vào hàng ngay), KHÔNG phải "cho_duyet"
    link_bao_cao(job: dict, goc_url: str) -> str   goc_url + "/#/bao-cao/<job name>/<ma_xem>"
- hooks.py linhx_core: doc_events "LX Don" on_update (hoặc on_change) gọi hàm tạo LX Job ngay (không đợi lịch giờ).
- LX Job (apps/linhx_worker) thêm trường "don" (Data) và nguon Select có "don".
"""
from _chung import ma, CORE, GOC, khong_import_frappe_dau_file, nap_module, ten_truong, tim_doctype

GOI = {"ma": "BC-AI", "workflow": "ai-noi-gi-ve-brand", "gia": 99000}


def _st():
    return nap_module("linhx_core.pay.sau_tra", CORE)


def _don(tt="da_tra"):
    return {"ma": "DON-1", "goi": "BC-AI", "so_tien": 99000, "trang_thai": tt, "brand": "Trà Đồi Mây", "email": "k@vd.vn"}


def test_da_tra_sinh_job_vao_hang():
    st = _st()
    v = st.viec_can_tao(_don(), GOI, [])
    assert v and v["workflow"] == "ai-noi-gi-ve-brand" and v["trang_thai"] == "cho"
    assert v["don"] == "DON-1" and v["nguon"] == "don" and "Trà Đồi Mây" in v["dau_vao"]
    assert v["email_khach"] == "k@vd.vn"


def test_khong_sinh_khi_chua_tra_trung_hoac_khong_workflow():
    st = _st()
    assert st.viec_can_tao(_don("cho_tra"), GOI, []) is None
    assert st.viec_can_tao(_don(), GOI, [{"name": "J1", "don": "DON-1"}]) is None, "một đơn chỉ một job"
    assert st.viec_can_tao(_don(), {"ma": "X", "gia": 1}, []) is None


def test_link_bao_cao():
    st = _st()
    assert st.link_bao_cao({"name": "VIEC-00012", "ma_xem": "ab12cd"}, "http://35.198.251.2") == \
        "http://35.198.251.2/#/bao-cao/VIEC-00012/ab12cd"


def test_noi_hook_va_lx_job():
    chu = (CORE / "linhx_core" / "hooks.py").read_text(encoding="utf-8")
    assert "doc_events" in chu and "LX Don" in chu and ("sau_tra" in chu or "giao_hang" in chu), "hooks.py phải nối doc_events LX Don vào sau_tra (từ đợt 3: giao_hang chung)"
    _, d = tim_doctype("LX Job", GOC / "apps" / "linhx_worker")
    tr = ten_truong(d)
    assert "don" in tr, "LX Job thiếu trường don"
    assert "don" in str(tr.get("nguon", {}).get("options", "")).split("\n")
    khong_import_frappe_dau_file(ma("pay/sau_tra.py"))
