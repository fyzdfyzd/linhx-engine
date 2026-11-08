"""Bàn đăng: hệ thống soạn sẵn mọi việc cần ra ngoài của một hoặc nhiều persona, người chỉ bấm.

Bốn loại mục:
  bai      bài của kênh mình. Bấm Đăng = duyệt + qua cổng + đăng qua adapter (Postiz/Meta). Sửa chữ trước khi bấm cũng được.
  cham     bình luận/theo dõi/thích bài người khác. API chính thức không cho làm việc này, nên nút là
           "Chép và mở": chép câu bình luận, mở đúng bài, người dán và gửi rồi bấm Xong.
  tra_loi  câu trả lời bình luận/DM hạng vàng/đỏ đã soạn. Bấm Gửi = duyệt + gửi qua adapter hộp thư.
  bai_hoc  bài học tầng 2 từ `hoc-ngay`. Bấm Nhận = thành luật viết.
Mọi lần bấm (đăng nguyên văn, sửa, bỏ kèm lý do, thời gian chờ) ghi vào `phan_hoi` để `hoc-ngay` học khẩu vị người duyệt.
Máy chủ chỉ nghe 127.0.0.1 và đòi mã phiên trong header, nên trang web khác không gọi được."""
import difflib
import json
import os
import secrets
from datetime import timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import cong, hanh_vi, hoc_ngay
from .adapters import lay as lay_adapter
from .db import bay_gio, ghi_hanh_dong, ghi_nhat_ky, mo
from .luat import doc

LY_DO_BO = ["sai giọng", "nhạt", "rủi ro", "sai thời điểm", "trùng ý", "sai người"]


def _now():
    return bay_gio().isoformat(timespec="seconds")


def adapter_ten(cfg, vai, thu):
    return "thu" if (thu or os.environ.get("KENHAO_THU") == "1") else cfg.get(f"{vai}_adapter", "thu")


def dang_mot(home, con, nv, hv, nt, b, thu=False):
    """Một bài qua cổng rồi đăng. Dùng chung cho lệnh `dang` và bàn đăng."""
    loi = cong.cong_dang(con, nv, nt, b, hv)
    if loi:
        ghi_nhat_ky(con, "dang_bi_chan", {"bai_id": b["id"], "loi": loi})
        con.commit()
        return {"bai_id": b["id"], "dang": False, "ly_do": loi}
    cfg = nt[b["nen_tang"]]
    dd = hoc_ngay.du_doan(con, b)
    ma = lay_adapter(adapter_ten(cfg, "dang", thu)).dang(home, b, cfg)
    con.execute("UPDATE bai SET trang_thai='da_dang', dang_luc=?, ma_ngoai=?, du_doan=? WHERE id=?", (_now(), ma, dd, b["id"]))
    ghi_hanh_dong(con, "dang", b["id"])
    ghi_nhat_ky(con, "dang", {"bai_id": b["id"], "ma": ma})
    con.commit()
    return {"bai_id": b["id"], "dang": True, "ma_ngoai": ma, "du_doan": dd}


def _cho(con, bang, id_):
    r = con.execute(f"SELECT hien_luc FROM {bang} WHERE id=?", (id_,)).fetchone()
    if not r or not r[0]:
        return None
    from datetime import datetime
    return int((bay_gio() - datetime.fromisoformat(r[0])).total_seconds())


def _phan_hoi(con, loai, id_, hanh_dong, ly_do=None, khoang=None, bang=None):
    con.execute("INSERT INTO phan_hoi(loai_muc, muc_id, hanh_dong, ly_do, khoang_sua, cho_giay, luc) VALUES (?,?,?,?,?,?,?)",
                (loai, id_, hanh_dong, ly_do, khoang, _cho(con, bang, id_) if bang else None, _now()))


def _khoang(cu, moi):
    return round(1 - difflib.SequenceMatcher(None, cu or "", moi or "").ratio(), 3)


class Kenh:
    def __init__(self, home, thu=False):
        self.home = home
        self.thu = thu

    def _ctx(self):
        con = mo(self.home)
        return con, doc(self.home, "nhan_vat"), doc(self.home, "hanh_vi"), doc(self.home, "nen_tang")

    def muc(self):
        con, nv, hv, nt = self._ctx()
        ma = nv.get("persona", {}).get("ma") or os.path.basename(self.home)
        gd, tuoi, *_ = hanh_vi.giai_doan_hien_tai(con, nv, hv)
        hn, _ = hoc_ngay.hau_nghiem(con)
        ra = []
        nay = _now()
        # Bài đã duyệt mà quá giờ hẹn 24 giờ vẫn bị cổng giữ lại thì cho quá hạn, không bắt người duyệt lại mỗi ngày
        han = (bay_gio() - timedelta(hours=24)).isoformat(timespec="seconds")
        con.execute("UPDATE bai SET trang_thai='qua_han' WHERE trang_thai='duyet' AND hen_luc<?", (han,))
        # Đề xuất chạm quá 48 giờ thì hết hạn (bài của người ta đã trôi), câu trả lời quá 72 giờ cũng vậy. Hết hạn không tính là Linh bỏ.
        han_cham = (bay_gio() - timedelta(hours=48)).isoformat(timespec="seconds")
        con.execute("UPDATE hanh_dong_ra SET trang_thai='het_han' WHERE trang_thai IN ('de_xuat','duyet') AND tao_luc<?", (han_cham,))
        han_tin = (bay_gio() - timedelta(hours=72)).isoformat(timespec="seconds")
        con.execute("UPDATE tin SET trang_thai='qua_han' WHERE trang_thai IN ('da_soan','duyet') AND luc<?", (han_tin,))
        for b in con.execute("SELECT * FROM bai WHERE trang_thai IN ('cho_duyet','duyet') ORDER BY hen_luc").fetchall():
            gia = dict(b) | {"trang_thai": "duyet"}
            chan = cong.cong_dang(con, nv, nt, gia, hv)
            ra.append({"loai": "bai", "id": b["id"], "persona": ma, "ten": nv["ten"], "nen_tang": b["nen_tang"], "luc": b["hen_luc"],
                       "noi_dung": b["noi_dung"], "media": json.loads(b["media"] or "[]"), "muc_dich": b["muc_dich"], "cho_ai": b["cho_ai"],
                       "hook": b["hook"], "tru_cot": b["tru_cot"], "cam_xuc": b["cam_xuc"], "critic": b["diem_critic"],
                       "du_doan": hoc_ngay.du_doan(con, b, hn), "chan": chan, "trang_thai": b["trang_thai"],
                       "nut": "Đăng" if b["trang_thai"] == "cho_duyet" else "Đăng ngay"})
            if not b["hien_luc"]:
                con.execute("UPDATE bai SET hien_luc=? WHERE id=?", (nay, b["id"]))
        for h in con.execute("""SELECT h.*, v.ten AS nguoi, v.nen_tang, v.bac_thang, v.diem_tin, d.url, substr(d.noi_dung,1,160) AS bai_ho
                                FROM hanh_dong_ra h JOIN vong v ON v.id=h.vong_id LEFT JOIN luot_doc d ON d.id=h.luot_doc_id
                                WHERE h.trang_thai IN ('de_xuat','duyet') ORDER BY h.id""").fetchall():
            chan = []
            if h["trang_thai"] == "de_xuat":
                chan = [x for x in hanh_vi.cong_ra(con, nv, hv, dict(h) | {"_bo_qua_id": h["id"]}) if "hết hạn mức" not in x]
            ra.append({"loai": "cham", "id": h["id"], "persona": ma, "chan": chan, "ten": nv["ten"], "nen_tang": h["nen_tang"], "kieu": h["loai"],
                       "nguoi": h["nguoi"], "thang": hanh_vi.THANG[h["bac_thang"]], "diem_tin": h["diem_tin"], "url": h["url"],
                       "bai_ho": h["bai_ho"], "noi_dung": h["noi_dung"], "muc_dich": h["muc_dich"], "vi_sao": h["vi_sao"],
                       "nut": "Chép và mở" if h["url"] else "Xong"})
            if not h["hien_luc"]:
                con.execute("UPDATE hanh_dong_ra SET hien_luc=? WHERE id=?", (nay, h["id"]))
        for t in con.execute("""SELECT t.*, f.ten AS fan FROM tin t LEFT JOIN fan f ON f.id=t.fan_id
                                WHERE t.trang_thai IN ('da_soan','duyet') AND t.hang IN ('vang','do') ORDER BY t.luc""").fetchall():
            ra.append({"loai": "tra_loi", "id": t["id"], "persona": ma, "ten": nv["ten"], "nen_tang": t["nen_tang"], "hang": t["hang"],
                       "fan": t["fan"], "tin": t["noi_dung"], "noi_dung": t["tra_loi"], "nhan": t["nhan"], "nut": "Gửi"})
        for bh in con.execute("SELECT * FROM bai_hoc WHERE trang_thai='de_xuat' ORDER BY luc DESC").fetchall():
            ra.append({"loai": "bai_hoc", "id": bh["id"], "persona": ma, "ten": nv["ten"], "noi_dung": bh["noi_dung"],
                       "nguon": bh["nguon"], "bang_chung": json.loads(bh["bang_chung"] or "{}"), "nut": "Nhận"})
        con.commit()
        tom = {"persona": ma, "ten": nv["ten"], "giai_doan": gd["ma"], "ten_giai_doan": gd["ten"], "tuoi_ngay": tuoi,
               "nhan_ai": nv["nhan_ai"]}
        con.close()
        return tom, ra

    def bam(self, loai, id_, hanh_dong, noi_dung=None, ly_do=None):
        con, nv, hv, nt = self._ctx()
        try:
            return self._bam(con, nv, hv, nt, loai, id_, hanh_dong, noi_dung, ly_do)
        finally:
            con.commit()
            con.close()

    def _bam(self, con, nv, hv, nt, loai, id_, hanh_dong, noi_dung, ly_do):
        if loai == "bai":
            b = con.execute("SELECT * FROM bai WHERE id=?", (id_,)).fetchone()
            if hanh_dong == "bo":
                con.execute("INSERT INTO duyet(bai_id, quyet_dinh, gop_y, luc) VALUES (?,?,?,?)", (id_, "bo", ly_do, _now()))
                con.execute("UPDATE bai SET trang_thai='bo' WHERE id=?", (id_,))
                _phan_hoi(con, "bai", id_, "bo", ly_do, bang="bai")
                return {"ok": True, "trang_thai": "bo"}
            sua = noi_dung is not None and noi_dung.strip() != (b["noi_dung"] or "").strip()
            if b["trang_thai"] == "duyet" and not sua:
                return {"ok": True, **dang_mot(self.home, con, nv, hv, nt, b, self.thu)} if hanh_dong == "dang_ngay" else \
                    {"ok": True, "trang_thai": "duyet", "ghi_chu": "đã duyệt từ trước, chờ giờ hẹn"}
            if sua:
                con.execute("INSERT INTO duyet(bai_id, quyet_dinh, gop_y, ban_cu, ban_moi, luc) VALUES (?,?,?,?,?,?)",
                            (id_, "sua", ly_do or "sửa trên bàn đăng", b["noi_dung"], noi_dung.strip(), _now()))
                con.execute("UPDATE bai SET noi_dung=?, trang_thai='duyet' WHERE id=?", (noi_dung.strip(), id_))
            else:
                con.execute("INSERT INTO duyet(bai_id, quyet_dinh, luc) VALUES (?,?,?)", (id_, "nhan", _now()))
                con.execute("UPDATE bai SET trang_thai='duyet' WHERE id=?", (id_,))
            _phan_hoi(con, "bai", id_, "sua" if sua else "dang", ly_do, _khoang(b["noi_dung"], noi_dung) if sua else 0.0, bang="bai")
            con.commit()
            b = con.execute("SELECT * FROM bai WHERE id=?", (id_,)).fetchone()
            if b["hen_luc"] and b["hen_luc"] > _now() and hanh_dong != "dang_ngay":
                return {"ok": True, "trang_thai": "duyet", "ghi_chu": f"đã duyệt, tự đăng lúc {b['hen_luc'][11:16]} nếu qua cổng"}
            kq = dang_mot(self.home, con, nv, hv, nt, b, self.thu)
            return {"ok": kq["dang"], **kq}
        if loai == "cham":
            h = con.execute("SELECT * FROM hanh_dong_ra WHERE id=?", (id_,)).fetchone()
            if hanh_dong == "bo":
                con.execute("UPDATE hanh_dong_ra SET trang_thai='bo' WHERE id=?", (id_,))
                _phan_hoi(con, "cham", id_, "bo", ly_do, bang="hanh_dong_ra")
                return {"ok": True, "trang_thai": "bo"}
            nd = noi_dung if noi_dung is not None else h["noi_dung"]
            if h["trang_thai"] == "de_xuat":
                loi = hanh_vi.cong_ra(con, nv, hv, dict(h) | {"noi_dung": nd, "_bo_qua_id": id_})
                loi = [x for x in loi if "hết hạn mức" not in x]
                if loi:
                    return {"ok": False, "ly_do": loi}
            sua = nd != h["noi_dung"]
            con.execute("UPDATE hanh_dong_ra SET trang_thai='da_lam', noi_dung=?, lam_luc=? WHERE id=?", (nd, _now(), id_))
            con.execute("UPDATE vong SET cham_khong_dap=cham_khong_dap+1 WHERE id=?", (h["vong_id"],))
            bac = {"thich": "da_cham", "luu": "da_cham", "theo_doi": "da_cham", "binh_luan": "da_gop_chuyen"}.get(h["loai"])
            if bac:
                hanh_vi.len_thang(con, h["vong_id"], bac)
            _phan_hoi(con, "cham", id_, "sua" if sua else "xong", ly_do, _khoang(h["noi_dung"], nd) if sua else 0.0, bang="hanh_dong_ra")
            return {"ok": True, "trang_thai": "da_lam"}
        if loai == "tra_loi":
            t = con.execute("SELECT * FROM tin WHERE id=?", (id_,)).fetchone()
            if hanh_dong == "bo":
                con.execute("UPDATE tin SET trang_thai='bo' WHERE id=?", (id_,))
                _phan_hoi(con, "tra_loi", id_, "bo", ly_do)
                return {"ok": True, "trang_thai": "bo"}
            nd = noi_dung if noi_dung is not None else t["tra_loi"]
            sua = nd != t["tra_loi"]
            con.execute("UPDATE tin SET tra_loi=?, trang_thai='duyet', duyet_boi='ban_dang' WHERE id=?", (nd, id_))
            t = con.execute("SELECT * FROM tin WHERE id=?", (id_,)).fetchone()
            f = con.execute("SELECT * FROM fan WHERE id=?", (t["fan_id"],)).fetchone() if t["fan_id"] else None
            loi = cong.cong_tra_loi(con, nv, t, f, linh_duyet=True)
            if loi:
                return {"ok": False, "ly_do": loi}
            cfg = nt.get(t["nen_tang"], {})
            lay_adapter(adapter_ten(cfg, "hop_thu", self.thu)).gui_tra_loi(self.home, t, nd, cfg)
            con.execute("UPDATE tin SET trang_thai='da_tra', tra_luc=? WHERE id=?", (_now(), id_))
            ghi_hanh_dong(con, "tra_loi", id_)
            _phan_hoi(con, "tra_loi", id_, "sua" if sua else "gui", None, _khoang(t["tra_loi"], nd) if sua else 0.0)
            return {"ok": True, "trang_thai": "da_tra"}
        if loai == "bai_hoc":
            bh = con.execute("SELECT * FROM bai_hoc WHERE id=?", (id_,)).fetchone()
            if hanh_dong == "bo":
                con.execute("UPDATE bai_hoc SET trang_thai='bo', quyet_luc=? WHERE id=?", (_now(), id_))
                _phan_hoi(con, "bai_hoc", id_, "bo", ly_do)
                return {"ok": True, "trang_thai": "bo"}
            nd = noi_dung or bh["noi_dung"]
            con.execute("UPDATE bai_hoc SET trang_thai='ap_dung', noi_dung=?, quyet_luc=? WHERE id=?", (nd, _now(), id_))
            pb = (con.execute("SELECT MAX(phien_ban) FROM luat_viet").fetchone()[0] or 0) + 1
            con.execute("INSERT INTO luat_viet(phien_ban, luat, luc) VALUES (?,?,?)", (pb, nd, _now()))
            with open(os.path.join(self.home, "ho-so", "luat-viet.md"), "a", encoding="utf-8") as fh:
                fh.write(f"\n- v{pb} ({bay_gio().date()}, từ bài học #{id_} trên bàn đăng): {nd}\n")
            _phan_hoi(con, "bai_hoc", id_, "nhan")
            return {"ok": True, "trang_thai": "ap_dung", "luat_viet": pb}
        return {"ok": False, "ly_do": [f"loại mục lạ: {loai}"]}


def tim_kenh(goc):
    """Một thư mục kênh (có kenh.db) hoặc thư mục nhà chứa nhiều kênh con (Persona OS)."""
    goc = os.path.abspath(goc)
    if os.path.exists(os.path.join(goc, "ho-so", "nhan-vat.md")):
        return [goc]
    return sorted(os.path.join(goc, d) for d in os.listdir(goc) if os.path.exists(os.path.join(goc, d, "ho-so", "nhan-vat.md")))


def tat_ca(kenh_ds):
    ds, tom = [], []
    for k in kenh_ds:
        t, m = k.muc()
        tom.append(t)
        ds += m
    return {"luc": _now(), "persona": tom, "muc": ds, "ly_do_bo": LY_DO_BO}


def phuc_vu(kenh_ds, cong_mang=8765, giao_dien=None):
    ma_phien = secrets.token_urlsafe(16)
    theo_ma = {}
    for k in kenh_ds:
        theo_ma[k.muc()[0]["persona"]] = k
    html = ("<!doctype html><html lang='vi'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'></head><body>"
            + open(giao_dien, encoding="utf-8").read().replace("__MA_PHIEN__", ma_phien) + "</body></html>")

    class H(BaseHTTPRequestHandler):
        def _gui(self, ma, than, kieu="application/json; charset=utf-8"):
            b = than.encode() if isinstance(than, str) else json.dumps(than, ensure_ascii=False).encode()
            self.send_response(ma)
            self.send_header("Content-Type", kieu)
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def log_message(self, *a):
            pass

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                return self._gui(200, html, "text/html; charset=utf-8")
            if self.path == "/api/muc":
                if self.headers.get("X-Ma-Phien") != ma_phien:
                    return self._gui(403, {"loi": "sai mã phiên"})
                return self._gui(200, tat_ca(kenh_ds))
            self._gui(404, {"loi": "không có"})

        def do_POST(self):
            if self.path != "/api/bam" or self.headers.get("X-Ma-Phien") != ma_phien:
                return self._gui(403, {"loi": "sai mã phiên"})
            d = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            k = theo_ma.get(d.get("persona"))
            if not k:
                return self._gui(404, {"loi": "không có persona"})
            try:
                self._gui(200, k.bam(d["loai"], int(d["id"]), d.get("hanh_dong", "dang"), d.get("noi_dung"), d.get("ly_do")))
            except Exception as e:  # noqa: BLE001
                self._gui(500, {"ok": False, "ly_do": [str(e)]})

    sv = ThreadingHTTPServer(("127.0.0.1", cong_mang), H)
    print(f"Bàn đăng: http://127.0.0.1:{cong_mang}/  ({len(kenh_ds)} kênh). Ctrl+C để dừng.")
    sv.serve_forever()
