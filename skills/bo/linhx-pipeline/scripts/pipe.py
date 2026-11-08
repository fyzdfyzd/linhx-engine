#!/usr/bin/env python3
"""linhx-pipeline: bảng mục × tầng cho mọi dự án nhiều bước (khuôn rút từ Koharu).

Chỉ dùng thư viện chuẩn Python 3.9+. Chạy:  python pipe.py <lệnh> <thư-mục-dự-án> [tuỳ chọn]

Ý chính:
  - Đơn vị việc là một ô = (một mục × một tầng), ví dụ (slide-04 × tạo ảnh).
  - Xong ô nào chốt ô đó: ghi hash đầu vào, hash đầu ra, nguồn (ai làm, model nào).
  - Đầu vào đổi thì ô thành CŨ, và mọi ô phía sau trên cùng mục cũng cũ theo.
  - Đầu ra bị sửa ngoài pipeline thì ô thành SỬA TAY; `nhan` để nhận là bản của Linh và khoá.
  - Ô khoá không bao giờ bị chạy lại đè lên; nếu cũ thì việc mới ghi ra tệp .de-xuat bên cạnh.
  - Lỗi do hết tài nguyên (credit, lượt, rate limit) chỉ thử lại một lần rồi dừng ô đó.

Lệnh:
  moi <dir> --mau <tên|đường dẫn> [--so N --tien-to slide | --muc a,b,c]
                                   tạo dự án: pipeline.json, muc.json, bang.json, chung/, muc/
  them-muc <dir> <id> [<id>...]    thêm mục (thứ tự = thứ tự ưu tiên)
  bang <dir> [--json]              ma trận mục × tầng
  viec <dir> [--tang T | --toi T] [--muc M[,M2]] [--het N] [--json]
                                   các ô cần làm, mục cũ nhất trước (giống bộ lập lịch Koharu)
  xong <dir> --muc M --tang T [--nguon claude] [--model X]
                                   chấm cổng ô đó; đạt thì chốt (mã thoát 0), trượt thì mã 1
  bo-qua <dir> --muc M --tang T --ly-do "..."   ô không có việc (vd slide không có ảnh) = xong
  loi <dir> --muc M --tang T --ly-do "..." [--tai-nguyen]
  nhan <dir> --muc M --tang T [--nguoi Linh]    nhận đầu ra hiện tại là bản người sửa, khoá ô
  mo-khoa <dir> --muc M --tang T
  lam-lai <dir> --muc M --tang T  xoá chốt ô (không xoá tệp) để làm lại
  mo-dung <dir> --muc M --tang T  Linh cho chạy lại ô đã DỪNG vì hết tài nguyên
  sang-nay <dir>                   viết SANG-NAY.md: đã xong gì, cái gì cũ, lỗi, cần Linh
  mau                              liệt kê pipeline mẫu có sẵn
"""
import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

GOC = Path(__file__).resolve().parent.parent
THU_MUC_MAU = GOC / "mau"

KY_HIEU = {
    "xong": "✓", "bo-qua": "–", "san-sang": "○", "cho": "·", "cu": "cũ",
    "cu-khoa": "cũ🔒", "sua-tay": "sửa", "loi": "lỗi", "dung": "DỪNG", "thieu-chung": "thiếu",
}


TEN = {
    "san-sang": "sẵn sàng", "cho": "chờ", "cu": "cũ", "cu-khoa": "cũ nhưng khoá", "sua-tay": "sửa tay",
    "loi": "lỗi", "dung": "dừng", "thieu-chung": "thiếu tệp chung",
}


class LoiPipe(Exception):
    pass


# ---------- tệp ----------

def doc_json(p, mac_dinh=None):
    p = Path(p)
    if not p.exists():
        if mac_dinh is not None:
            return mac_dinh
        raise LoiPipe(f"không thấy {p}")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def ghi_json(p, du_lieu):
    """Ghi qua tệp tạm rồi đổi tên: hỏng giữa chừng không làm mất bản cũ."""
    p = Path(p)
    tam = p.with_name(p.name + ".tam")
    with open(tam, "w", encoding="utf-8") as f:
        json.dump(du_lieu, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tam, p)


def bam(p):
    p = Path(p)
    if not p.exists():
        return None
    h = hashlib.sha256()
    if p.is_dir():
        for con in sorted(x for x in p.rglob("*") if x.is_file()):
            h.update(str(con.relative_to(p)).encode())
            h.update(con.read_bytes())
    else:
        h.update(p.read_bytes())
    return h.hexdigest()[:16]


def bay_gio():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


# ---------- mô hình ----------

class DuAn:
    def __init__(self, thu_muc):
        self.dir = Path(thu_muc)
        self.pipeline = doc_json(self.dir / "pipeline.json")
        self.muc = doc_json(self.dir / "muc.json", {"muc": []})["muc"]
        self.bang = doc_json(self.dir / "bang.json", {"o": {}})
        self.tang = self.pipeline["tang"]
        self.theo_id = {t["id"]: t for t in self.tang}
        kiem_pipeline(self.pipeline)

    # đường dẫn
    def ra(self, muc, tang_id):
        return self.dir / "muc" / muc / self.theo_id[tang_id]["ra"]

    def khoa_o(self, muc, tang_id):
        return f"{muc}/{tang_id}"

    def ban_ghi(self, muc, tang_id):
        return self.bang["o"].get(self.khoa_o(muc, tang_id))

    def dau_vao(self, muc, tang_id):
        """Các tệp ô này đọc: đầu ra của tầng `can` trên cùng mục + tệp chung."""
        t = self.theo_id[tang_id]
        vao = {}
        for c in t.get("can", []):
            vao[f"muc/{muc}/{self.theo_id[c]['ra']}"] = self.ra(muc, c)
        for c in t.get("doc_chung", []):
            vao[c] = self.dir / c
        return vao

    def van_tay_vao(self, muc, tang_id):
        return {k: bam(p) for k, p in self.dau_vao(muc, tang_id).items()}

    def luu(self):
        ghi_json(self.dir / "bang.json", self.bang)

    def nhat_ky(self, **su_kien):
        su_kien = {"luc": bay_gio(), **su_kien}
        with open(self.dir / "nhat-ky.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(su_kien, ensure_ascii=False) + "\n")

    # trạng thái
    def trang_thai(self, muc, tang_id, _nho=None):
        nho = {} if _nho is None else _nho
        k = (muc, tang_id)
        if k in nho:
            return nho[k]
        t = self.theo_id[tang_id]
        bg = self.ban_ghi(muc, tang_id)
        cha = [self.trang_thai(muc, c, nho) for c in t.get("can", [])]
        cha_on = all(s in ("xong", "bo-qua", "cu-khoa", "sua-tay") for s in cha)
        thieu_chung = [c for c in t.get("doc_chung", []) if not (self.dir / c).exists()]

        if bg is None:
            if cha and all(c == "bo-qua" for c in cha):
                s = "bo-qua"  # tầng trước không có việc thì tầng này cũng không (patch rỗng = xong)
            else:
                s = "thieu-chung" if thieu_chung else ("san-sang" if cha_on else "cho")
        elif bg["trang_thai"] in ("loi", "dung"):
            s = bg["trang_thai"]
        else:
            cu = any(c in ("cu", "san-sang", "cho", "loi", "dung", "thieu-chung") for c in cha)
            if not cu:
                cu = self.van_tay_vao(muc, tang_id) != bg.get("vao", {})
            ra_doi = bg["trang_thai"] == "xong" and bam(self.ra(muc, tang_id)) != bg.get("ra")
            if bg.get("khoa"):
                s = "cu-khoa" if cu else "xong"
                if ra_doi:
                    s = "sua-tay"
            elif ra_doi:
                s = "sua-tay"
            elif cu:
                s = "cu"
            else:
                s = bg["trang_thai"]
        nho[k] = s
        return s

    def ma_tran(self):
        nho = {}
        return {m: {t["id"]: self.trang_thai(m, t["id"], nho) for t in self.tang} for m in self.muc}


def kiem_pipeline(p):
    ids = [t["id"] for t in p.get("tang", [])]
    if not ids:
        raise LoiPipe("pipeline.json không có tầng nào")
    if len(set(ids)) != len(ids):
        raise LoiPipe("pipeline.json có id tầng trùng")
    da_thay = set()
    for t in p["tang"]:
        for k in ("id", "ra"):
            if not t.get(k):
                raise LoiPipe(f"tầng thiếu '{k}': {t}")
        for c in t.get("can", []):
            if c not in da_thay:
                raise LoiPipe(f"tầng '{t['id']}' cần '{c}' nhưng '{c}' phải khai trước nó")
        da_thay.add(t["id"])


def to_tien(du_an, tang_id):
    """Tầng `tang_id` và mọi tầng nó cần (giống Operation::Through của Koharu)."""
    can = set()
    dang = [tang_id]
    while dang:
        x = dang.pop()
        if x not in can:
            can.add(x)
            dang.extend(du_an.theo_id[x].get("can", []))
    return [t["id"] for t in du_an.tang if t["id"] in can]


# ---------- cổng ----------

def cham_cong(du_an, muc, tang_id):
    """Trả về danh sách lỗi; rỗng = đạt."""
    t = du_an.theo_id[tang_id]
    tep = du_an.ra(muc, tang_id)
    cong = t.get("cong", {"loai": "co-tep"})
    loai = cong.get("loai", "co-tep")
    if not tep.exists():
        return [f"chưa có tệp {tep.relative_to(du_an.dir)}"]
    if tep.is_file() and tep.stat().st_size == 0:
        return ["tệp rỗng"]
    loi = []
    if loai == "co-tep":
        pass
    elif loai == "json-truong":
        try:
            d = doc_json(tep)
        except json.JSONDecodeError as e:
            return [f"JSON hỏng: {e}"]
        for truong in cong.get("truong", []):
            if d.get(truong) in (None, "", [], {}):
                loi.append(f"thiếu hoặc rỗng trường '{truong}'")
    elif loai == "md-muc":
        noi_dung = tep.read_text(encoding="utf-8")
        for muc_md in cong.get("muc", []):
            if muc_md not in noi_dung:
                loi.append(f"thiếu mục '{muc_md}'")
        if "[CẦN LINH" in noi_dung and not cong.get("cho_phep_can_linh"):
            loi.append("còn chỗ [CẦN LINH …] chưa điền")
    elif loai == "anh":
        dau = tep.read_bytes()[:12]
        if not (dau.startswith(b"\x89PNG") or dau.startswith(b"\xff\xd8") or dau[8:12] == b"WEBP"):
            loi.append("không phải PNG/JPG/WEBP")
        if tep.stat().st_size < cong.get("toi_thieu_byte", 1024):
            loi.append("ảnh quá nhỏ, có thể hỏng")
    elif loai == "lenh":
        lenh = [x.replace("{tep}", str(tep)).replace("{goc}", str(GOC)) for x in cong["lenh"]]
        kq = subprocess.run(lenh, cwd=du_an.dir, capture_output=True, text=True)
        if kq.returncode != 0:
            loi.append((kq.stdout + kq.stderr).strip()[-800:] or f"lệnh trả mã {kq.returncode}")
    else:
        loi.append(f"không biết loại cổng '{loai}'")
    return loi


# ---------- lệnh ----------

def tim_mau(ten):
    p = Path(ten)
    if p.exists():
        return p
    p = THU_MUC_MAU / f"{ten}.json"
    if p.exists():
        return p
    raise LoiPipe(f"không thấy mẫu '{ten}'. Có: {', '.join(x.stem for x in THU_MUC_MAU.glob('*.json'))}")


def lenh_moi(a):
    d = Path(a.dir)
    if (d / "pipeline.json").exists():
        raise LoiPipe(f"{d} đã có pipeline.json")
    mau = doc_json(tim_mau(a.mau))
    kiem_pipeline(mau)
    if a.muc:
        muc = [x.strip() for x in a.muc.split(",") if x.strip()]
    else:
        tien_to = a.tien_to or mau.get("don_vi", "muc")
        muc = [f"{tien_to}-{i:02d}" for i in range(1, (a.so or 0) + 1)]
    (d / "chung").mkdir(parents=True, exist_ok=True)
    (d / "muc").mkdir(exist_ok=True)
    for m in muc:
        (d / "muc" / m).mkdir(exist_ok=True)
    ghi_json(d / "pipeline.json", mau)
    ghi_json(d / "muc.json", {"muc": muc})
    ghi_json(d / "bang.json", {"o": {}})
    du_an = DuAn(d)
    du_an.nhat_ky(su_kien="moi", mau=a.mau, so_muc=len(muc))
    chung = sorted({c for t in mau["tang"] for c in t.get("doc_chung", [])})
    print(f"Đã tạo {d} theo mẫu '{mau.get('ten', a.mau)}': {len(muc)} {mau.get('don_vi', 'mục')}, {len(mau['tang'])} tầng.")
    if chung:
        print("Tệp chung cần có trước khi chạy:", ", ".join(chung))


def lenh_them_muc(a):
    du_an = DuAn(a.dir)
    moi = [m for m in a.ids if m not in du_an.muc]
    for m in moi:
        (du_an.dir / "muc" / m).mkdir(parents=True, exist_ok=True)
    ghi_json(du_an.dir / "muc.json", {"muc": du_an.muc + moi})
    du_an.nhat_ky(su_kien="them-muc", muc=moi)
    print(f"Thêm {len(moi)} mục: {', '.join(moi) or '(không có mục mới)'}")


def in_bang(du_an):
    mt = du_an.ma_tran()
    cot = [t["id"] for t in du_an.tang]
    rong_muc = max([len("mục")] + [len(m) for m in du_an.muc])
    rong = [max(len(c), 5) for c in cot]
    print(" " * (rong_muc + 2) + "  ".join(c.ljust(w) for c, w in zip(cot, rong)))
    for m in du_an.muc:
        o = []
        for c, w in zip(cot, rong):
            s = mt[m][c]
            kh = KY_HIEU.get(s, s)
            bg = du_an.ban_ghi(m, c)
            if s == "xong" and bg and bg.get("nguon") and bg["nguon"] != "claude":
                kh += " " + bg["nguon"]
            if s == "xong" and bg and bg.get("khoa"):
                kh += "🔒"
            o.append(kh.ljust(w))
        print(m.ljust(rong_muc + 2) + "  ".join(o))
    dem = {}
    for m in mt.values():
        for s in m.values():
            dem[s] = dem.get(s, 0) + 1
    tong = sum(dem.values())
    print()
    print(f"{dem.get('xong', 0) + dem.get('bo-qua', 0)}/{tong} ô xong · "
          + " · ".join(f"{TEN.get(k, k)} {v}" for k, v in sorted(dem.items()) if k not in ("xong", "bo-qua")))
    print("Ký hiệu: ✓ xong, – bỏ qua, ○ sẵn sàng làm, · chờ tầng trước, cũ = đầu vào đã đổi, "
          "sửa = có người sửa tệp (chạy `nhan`), 🔒 khoá")


def lenh_bang(a):
    du_an = DuAn(a.dir)
    if a.json:
        print(json.dumps(du_an.ma_tran(), ensure_ascii=False, indent=1))
    else:
        in_bang(du_an)


def danh_sach_viec(du_an, tang=None, toi=None, muc=None, het=None):
    if tang:
        chon_tang = [tang]
    elif toi:
        chon_tang = to_tien(du_an, toi)
    else:
        chon_tang = [t["id"] for t in du_an.tang]
    for t in chon_tang:
        if t not in du_an.theo_id:
            raise LoiPipe(f"không có tầng '{t}'")
    chon_muc = muc.split(",") if muc else du_an.muc
    for m in chon_muc:
        if m not in du_an.muc:
            raise LoiPipe(f"không có mục '{m}'")
    mt = du_an.ma_tran()
    on = ("xong", "bo-qua", "cu-khoa", "sua-tay")
    viec = []
    # Mục cũ nhất trước, trong mục theo thứ tự tầng. Chỉ lấy ô có mọi tầng trước đã ổn,
    # nên nhánh song song (vd bố cục và ảnh) cùng hiện ra, còn ô cũ phía sau chờ ô cũ phía trước.
    for m in chon_muc:
        for t in chon_tang:
            s = mt[m][t]
            cha_on = all(mt[m][c] in on for c in du_an.theo_id[t].get("can", []))
            if s in ("san-sang", "cu", "cu-khoa") and cha_on:
                td = du_an.theo_id[t]
                ra = du_an.ra(m, t)
                if s == "cu-khoa":
                    ra = ra.with_name(ra.stem + ".de-xuat" + ra.suffix)
                viec.append({
                    "muc": m, "tang": t, "ly_do": {"san-sang": "chưa làm", "cu": "đầu vào đã đổi",
                                                  "cu-khoa": "đầu vào đã đổi nhưng ô do người sửa: chỉ viết đề xuất"}[s],
                    "ai": td.get("ai", "claude"), "viec": td.get("viec", ""),
                    "doc": sorted(du_an.dau_vao(m, t).keys()),
                    "ghi": str(ra.relative_to(du_an.dir)),
                    "cong": td.get("cong", {"loai": "co-tep"}),
                })
    return viec[:het] if het else viec


def lenh_viec(a):
    du_an = DuAn(a.dir)
    viec = danh_sach_viec(du_an, a.tang, a.toi, a.muc, a.het)
    if a.json:
        print(json.dumps(viec, ensure_ascii=False, indent=1))
        return
    if not viec:
        print("Không còn ô nào cần làm trong phạm vi này.")
        return
    for v in viec:
        print(f"[{v['muc']} × {v['tang']}] {v['ly_do']} · ai làm: {v['ai']}")
        if v["viec"]:
            print(f"   việc: {v['viec']}")
        print(f"   đọc: {', '.join(v['doc']) or '(không)'}")
        print(f"   ghi: {v['ghi']}")
        print(f"   xong thì: pipe.py xong {a.dir} --muc {v['muc']} --tang {v['tang']}")


def lay_o(du_an, a):
    if a.tang not in du_an.theo_id:
        raise LoiPipe(f"không có tầng '{a.tang}'")
    if a.muc not in du_an.muc:
        raise LoiPipe(f"không có mục '{a.muc}'")


def lenh_xong(a):
    du_an = DuAn(a.dir)
    lay_o(du_an, a)
    s = du_an.trang_thai(a.muc, a.tang)
    if s in ("cho", "thieu-chung"):
        raise LoiPipe(f"ô {a.muc} × {a.tang} chưa đủ đầu vào ({KY_HIEU[s]}); làm tầng trước đã")
    bg = du_an.ban_ghi(a.muc, a.tang) or {}
    if bg.get("khoa"):
        raise LoiPipe("ô đang khoá (người sửa). Đề xuất mới nằm ở tệp .de-xuat; muốn thay thì Linh chép đè rồi chạy `nhan`.")
    loi = cham_cong(du_an, a.muc, a.tang)
    if loi:
        print(f"TRƯỢT cổng {a.muc} × {a.tang}:")
        for x in loi:
            print("  -", x)
        du_an.nhat_ky(su_kien="truot-cong", muc=a.muc, tang=a.tang, loi=loi)
        sys.exit(1)
    du_an.bang["o"][du_an.khoa_o(a.muc, a.tang)] = {
        "trang_thai": "xong",
        "vao": du_an.van_tay_vao(a.muc, a.tang),
        "ra": bam(du_an.ra(a.muc, a.tang)),
        "nguon": a.nguon or du_an.theo_id[a.tang].get("ai", "claude"),
        "model": a.model,
        "luc": bay_gio(),
        "khoa": False,
    }
    du_an.bang.get("dem_loi", {}).pop(du_an.khoa_o(a.muc, a.tang), None)
    du_an.luu()
    du_an.nhat_ky(su_kien="xong", muc=a.muc, tang=a.tang, nguon=a.nguon, model=a.model)
    print(f"ĐẠT {a.muc} × {a.tang}, đã chốt.")


def lenh_bo_qua(a):
    du_an = DuAn(a.dir)
    lay_o(du_an, a)
    du_an.bang["o"][du_an.khoa_o(a.muc, a.tang)] = {
        "trang_thai": "bo-qua", "vao": du_an.van_tay_vao(a.muc, a.tang), "ra": None,
        "nguon": "claude", "ly_do": a.ly_do, "luc": bay_gio(), "khoa": False,
    }
    du_an.luu()
    du_an.nhat_ky(su_kien="bo-qua", muc=a.muc, tang=a.tang, ly_do=a.ly_do)
    print(f"Bỏ qua {a.muc} × {a.tang}: {a.ly_do}")


def lenh_loi(a):
    du_an = DuAn(a.dir)
    lay_o(du_an, a)
    k = du_an.khoa_o(a.muc, a.tang)
    dem = du_an.bang.setdefault("dem_loi", {})
    so_lan = dem.get(k, 0) + 1
    dem[k] = so_lan
    # Hết tài nguyên: thử lại đúng một lần (giống Koharu khi hết VRAM), lần hai thì dừng ô.
    trang_thai = "dung" if (a.tai_nguyen and so_lan >= 2) else "loi"
    du_an.bang["o"][k] = {"trang_thai": trang_thai, "ly_do": a.ly_do, "so_lan_loi": so_lan,
                         "tai_nguyen": a.tai_nguyen, "luc": bay_gio()}
    du_an.luu()
    du_an.nhat_ky(su_kien=trang_thai, muc=a.muc, tang=a.tang, ly_do=a.ly_do, lan=so_lan)
    if trang_thai == "dung":
        print(f"DỪNG {a.muc} × {a.tang} sau {so_lan} lần lỗi tài nguyên. Báo Linh, không thử nữa.")
    elif a.tai_nguyen:
        print(f"Lỗi tài nguyên lần {so_lan}: được thử lại một lần. Chạy `lam-lai` rồi làm lại ô này.")
    else:
        print(f"Ghi lỗi {a.muc} × {a.tang} (lần {so_lan}). Sửa nguyên nhân rồi chạy `lam-lai`.")


def lenh_lam_lai(a):
    du_an = DuAn(a.dir)
    lay_o(du_an, a)
    k = du_an.khoa_o(a.muc, a.tang)
    bg = du_an.bang["o"].get(k)
    if bg and bg.get("khoa"):
        raise LoiPipe("ô đang khoá; chạy `mo-khoa` trước nếu Linh đồng ý làm lại")
    if bg and bg.get("trang_thai") == "dung":
        raise LoiPipe("ô đã DỪNG vì lỗi tài nguyên lặp lại; chỉ làm lại khi Linh bảo (chạy `mo-dung`)")
    # Không xoá dem_loi: luật "thử lại một lần" vẫn tính lần lỗi trước.
    du_an.bang["o"].pop(k, None)
    du_an.luu()
    du_an.nhat_ky(su_kien="lam-lai", muc=a.muc, tang=a.tang)
    print(f"Ô {a.muc} × {a.tang} mở lại để làm.")


def lenh_mo_dung(a):
    du_an = DuAn(a.dir)
    lay_o(du_an, a)
    k = du_an.khoa_o(a.muc, a.tang)
    du_an.bang["o"].pop(k, None)
    du_an.bang.get("dem_loi", {}).pop(k, None)
    du_an.luu()
    du_an.nhat_ky(su_kien="mo-dung", muc=a.muc, tang=a.tang)
    print(f"Ô {a.muc} × {a.tang} được Linh cho chạy lại, đếm lỗi về 0.")


def lenh_nhan(a):
    du_an = DuAn(a.dir)
    lay_o(du_an, a)
    tep = du_an.ra(a.muc, a.tang)
    if not tep.exists():
        raise LoiPipe(f"chưa có tệp {tep.relative_to(du_an.dir)}")
    du_an.bang["o"][du_an.khoa_o(a.muc, a.tang)] = {
        "trang_thai": "xong", "vao": du_an.van_tay_vao(a.muc, a.tang), "ra": bam(tep),
        "nguon": a.nguoi.lower(), "model": None, "luc": bay_gio(), "khoa": True,
    }
    du_an.luu()
    du_an.nhat_ky(su_kien="nhan", muc=a.muc, tang=a.tang, nguoi=a.nguoi)
    print(f"Nhận {a.muc} × {a.tang} là bản của {a.nguoi}, đã khoá. Các ô phía sau dùng tệp này sẽ thành cũ.")


def lenh_mo_khoa(a):
    du_an = DuAn(a.dir)
    lay_o(du_an, a)
    bg = du_an.ban_ghi(a.muc, a.tang)
    if not bg or not bg.get("khoa"):
        print("Ô không khoá.")
        return
    bg["khoa"] = False
    du_an.luu()
    du_an.nhat_ky(su_kien="mo-khoa", muc=a.muc, tang=a.tang)
    print(f"Mở khoá {a.muc} × {a.tang}.")


def lenh_sang_nay(a):
    du_an = DuAn(a.dir)
    mt = du_an.ma_tran()
    nhom = {}
    for m, hang in mt.items():
        for t, s in hang.items():
            nhom.setdefault(s, []).append(f"{m} × {t}")
    tong = sum(len(v) for v in nhom.values())
    xong = len(nhom.get("xong", [])) + len(nhom.get("bo-qua", []))
    dong = [f"# Sáng nay: {du_an.pipeline.get('ten', du_an.dir.name)}", "",
            f"Cập nhật {bay_gio()}. {xong}/{tong} ô xong.", ""]
    can_linh = nhom.get("dung", []) + nhom.get("sua-tay", []) + nhom.get("cu-khoa", []) + nhom.get("thieu-chung", [])
    dong += ["## Cần Linh", ""]
    if can_linh:
        for s, nhan in (("dung", "dừng vì hết tài nguyên"), ("sua-tay", "có người sửa tệp, cần `nhan` hoặc `lam-lai`"),
                        ("cu-khoa", "ô Linh đã khoá nhưng đầu vào đổi, xem tệp .de-xuat"),
                        ("thieu-chung", "thiếu tệp chung")):
            for o in nhom.get(s, []):
                bg = du_an.ban_ghi(*o.split(" × ")) or {}
                dong.append(f"- {o}: {nhan}" + (f" ({bg['ly_do']})" if bg.get("ly_do") else ""))
    else:
        dong.append("- Không có.")
    dong += ["", "## Cần chạy tiếp", ""]
    viec = danh_sach_viec(du_an)
    dong += [f"- {v['muc']} × {v['tang']}: {v['ly_do']} ({v['ai']})" for v in viec] or ["- Không còn."]
    dong += ["", "## Lỗi", ""]
    dong += [f"- {o}: {(du_an.ban_ghi(*o.split(' × ')) or {}).get('ly_do', '')}" for o in nhom.get("loi", [])] or ["- Không có."]
    (du_an.dir / "SANG-NAY.md").write_text("\n".join(dong) + "\n", encoding="utf-8")
    print("\n".join(dong))


def lenh_mau(_a):
    for p in sorted(THU_MUC_MAU.glob("*.json")):
        m = doc_json(p)
        print(f"{p.stem}: {m.get('mo_ta', '')} ({m.get('don_vi', 'mục')}, {len(m['tang'])} tầng: "
              f"{' → '.join(t['id'] for t in m['tang'])})")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pipe.py", description="Bảng mục × tầng cho dự án LinhX")
    sp = ap.add_subparsers(dest="lenh", required=True)

    a = sp.add_parser("moi"); a.add_argument("dir"); a.add_argument("--mau", required=True)
    a.add_argument("--so", type=int); a.add_argument("--tien-to"); a.add_argument("--muc")
    a.set_defaults(f=lenh_moi)
    a = sp.add_parser("them-muc"); a.add_argument("dir"); a.add_argument("ids", nargs="+"); a.set_defaults(f=lenh_them_muc)
    a = sp.add_parser("bang"); a.add_argument("dir"); a.add_argument("--json", action="store_true"); a.set_defaults(f=lenh_bang)
    a = sp.add_parser("viec"); a.add_argument("dir"); g = a.add_mutually_exclusive_group()
    g.add_argument("--tang"); g.add_argument("--toi")
    a.add_argument("--muc"); a.add_argument("--het", type=int); a.add_argument("--json", action="store_true")
    a.set_defaults(f=lenh_viec)
    for ten, f in (("xong", lenh_xong), ("bo-qua", lenh_bo_qua), ("loi", lenh_loi), ("nhan", lenh_nhan),
                   ("mo-khoa", lenh_mo_khoa), ("lam-lai", lenh_lam_lai), ("mo-dung", lenh_mo_dung)):
        a = sp.add_parser(ten); a.add_argument("dir"); a.add_argument("--muc", required=True)
        a.add_argument("--tang", required=True); a.set_defaults(f=f)
        if ten == "xong":
            a.add_argument("--nguon"); a.add_argument("--model")
        if ten in ("bo-qua", "loi"):
            a.add_argument("--ly-do", required=True)
        if ten == "loi":
            a.add_argument("--tai-nguyen", action="store_true")
        if ten == "nhan":
            a.add_argument("--nguoi", default="Linh")
    a = sp.add_parser("sang-nay"); a.add_argument("dir"); a.set_defaults(f=lenh_sang_nay)
    a = sp.add_parser("mau"); a.set_defaults(f=lenh_mau)

    args = ap.parse_args(argv)
    try:
        args.f(args)
    except LoiPipe as e:
        print(f"LỖI: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
