"""linhx-report: điều phối và cổng kiểm cho quy trình 13 bước (0–12) ra báo cáo PDF cao cấp.

Dùng: python report.py <lệnh> <thu-muc> [tuỳ chọn]
  moi <dir> --ten "..." [--phong-cach p1-chien-luoc|p4-tap-chi|<thư mục phong cách>] [--brand linhx]
  trang-thai <dir>
  cong <dir> <n>                 kiểm cổng bước n (0..12), ghi kết quả vào trang-thai.json
  duyet <dir> <n> [--nguoi Linh] Linh (hoặc luật 10 phút) duyệt bước n
  kiem-van <dir>                 luật viết V01–V11 trên 06-chuong/*.md
  kiem-so <dir>                  đối chiếu mọi con số với 03-bang-chung.jsonl, ghi 07-kiem-so.json
  dung <dir>                     06-chuong + 04-hinh + style → 10-bao-cao.json → Typst → bao-cao.pdf
  kiem-ban-in <dir>              luật dàn trang D01–D17 trên PDF, ghi 11-kiem-ban-in.json
  anh-trang <dir> [--dpi 70]     render từng trang PDF ra 11-anh-trang/ để Claude xem và chấm
Mọi luật in số đo thật. Không tự tuyên bố đạt: chỉ `cong` mới ghi đạt.
"""
import argparse
import csv
import datetime as dt
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
DU_LIEU = GOC / "du-lieu"

# ---------------------------------------------------------------- tiện ích

def doc_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def ghi_json(p, d):
    Path(p).write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def bay_gio():
    return dt.datetime.now().isoformat(timespec="seconds")


def tieng(s):
    return len([w for w in re.split(r"\s+", s.strip()) if w])


def trang_thai(d):
    p = Path(d) / "trang-thai.json"
    return doc_json(p) if p.exists() else {}


def luu_tt(d, tt):
    ghi_json(Path(d) / "trang-thai.json", tt)


class KQ:
    def __init__(self):
        self.loi, self.canh_bao, self.do = [], [], []

    def L(self, ma, s):
        self.loi.append(f"[{ma}] {s}")

    def C(self, ma, s):
        self.canh_bao.append(f"[{ma}] {s}")

    def M(self, s):
        self.do.append(s)

    def dat(self):
        return not self.loi

    def in_ra(self, ten):
        print(f"== {ten}: {'ĐẠT' if self.dat() else 'CHƯA ĐẠT'}")
        for s in self.do:
            print("  đo:", s)
        for s in self.loi:
            print("  LỖI", s)
        for s in self.canh_bao:
            print("  cảnh báo", s)


# ---------------------------------------------------------------- số tiếng Việt

RE_SO = re.compile(r"(?<![\w\[])(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d+))?(?![\w\]])")


def cac_so(s):
    """Trả các số trong câu theo định dạng Việt (1.234,5). Bỏ mã BCxx, năm 1900–2100 đứng riêng."""
    s2 = re.sub(r"\[[A-Z]+\d+\]", " ", s)
    s2 = re.sub(r"\^\[[^\]]*\]", " ", s2)
    out = []
    for m in RE_SO.finditer(s2):
        nguyen = m.group(1).replace(".", "")
        v = float(nguyen + ("." + m.group(2) if m.group(2) else ""))
        if m.group(2) is None and 1900 <= v <= 2100 and "." not in m.group(1):
            continue
        out.append(v)
    return out


def tach_cau(s):
    s = re.sub(r"\s+", " ", s)
    cau = re.split(r"(?<=[.!?…])\s+(?=[A-ZÀ-Ỹ“\"(\[])", s)
    return [c.strip() for c in cau if c.strip()]


DONG_TU = ["tăng", "giảm", "đạt", "dẫn", "vẫn", "đang", "sẽ", "cao hơn", "thấp hơn", "gấp", "chiếm", "là", "có",
           "không", "chưa", "cần", "phải", "nên", "mở", "đóng", "chuyển", "trở", "vượt", "thua", "kéo", "đẩy", "giữ",
           "bỏ", "mất", "thắng", "đi", "đến", "về", "lên", "xuống", "bằng", "hơn", "nhất", "đổi", "tạo", "làm", "học",
           "dùng", "trả", "bán", "mua", "chọn", "bắt đầu", "thiếu", "thừa", "đủ", "rơi", "nằm", "đứng", "co", "nở",
           "phụ thuộc", "quyết định", "thay", "biến", "mới", "cũ", "nhanh", "chậm", "rẻ", "đắt", "lớn", "nhỏ"]


def la_cau_ket_luan(s):
    n = tieng(s)
    if n < 6 or n > 30:
        return False, f"{n} tiếng (cần 6–30)"
    low = s.lower()
    if re.search(r"\d", s) or any(re.search(r"(?<!\w)" + re.escape(v) + r"(?!\w)", low) for v in DONG_TU):
        return True, f"{n} tiếng"
    return False, "giống cụm danh từ, thiếu động từ hoặc so sánh"


GIONG_AI = ["trong bối cảnh", "không chỉ", "đóng vai trò quan trọng", "ngày càng", "hãy cùng", "bức tranh toàn cảnh",
            "chìa khóa", "chìa khoá", "kỷ nguyên", "cuộc cách mạng", "then chốt", "vô cùng", "tóm lại", "nhìn chung",
            "có thể nói", "đáng chú ý là", "một cách", "hành trình", "khai phá", "tiềm năng to lớn", "mở ra cơ hội",
            "không thể phủ nhận", "thế giới đang thay đổi", "điều quan trọng là", "nói cách khác"]

# ---------------------------------------------------------------- dữ liệu dự án

def nguon(d):
    p = Path(d) / "03-nguon.csv"
    if not p.exists():
        return {}
    with open(p, encoding="utf-8") as f:
        return {r["ma"].strip(): r for r in csv.DictReader(f) if r.get("ma")}


def bang_chung(d):
    p = Path(d) / "03-bang-chung.jsonl"
    out = {}
    if p.exists():
        for i, dong in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if dong.strip():
                try:
                    o = json.loads(dong)
                    out[o["id"]] = o
                except Exception as e:  # noqa: BLE001
                    out[f"__loi_dong_{i}"] = {"loi": str(e)}
    return out


def chuong_files(d):
    p = Path(d) / "06-chuong"
    return sorted(x for x in p.glob("*.md")) if p.exists() else []


def can_muc(kq, text, muc, ten):
    for m in muc:
        rx = re.compile(r"^#+\s*" + re.escape(m), re.M | re.I)
        if not rx.search(text):
            kq.L("thieu-muc", f"{ten} thiếu mục '{m}'")
            continue
        than = text[rx.search(text).end():]
        nxt = re.search(r"^#+\s", than, re.M)
        than = than[: nxt.start()] if nxt else than
        if re.search(r"^\[(?!CẦN LINH)[^\]]*\]\s*$", than.strip(), re.M) and "…" not in m:
            kq.L("muc-mau", f"{ten} mục '{m}' vẫn là chữ mẫu trong ngoặc vuông")
        if not than.strip(" \n:-"):
            kq.L("muc-trong", f"{ten} mục '{m}' đang trống (ghi [CẦN LINH: ...] nếu chưa có)")


# ---------------------------------------------------------------- cổng 0–5

def cong_0(d, kq):
    p = Path(d) / "00-cau-truc.json"
    if not p.exists():
        kq.L("0", "thiếu 00-cau-truc.json: bước tìm mẫu luôn chạy đầu tiên")
        return
    ct = doc_json(p)
    mau = ct.get("mau", [])
    kq.M(f"{len(mau)} mẫu đã xem")
    if len(mau) < 3:
        kq.L("0", "cần xem ít nhất 3 mẫu trước khi chọn")
    chon = [m for m in mau if m.get("chon")]
    if len(chon) < 1:
        kq.L("0", "chưa đánh dấu mẫu chính (\"chon\": true)")
    for m in mau:
        if not m.get("nguon") or not m.get("duong_dan"):
            kq.L("0", f"mẫu '{m.get('ten')}' thiếu nguồn hoặc đường dẫn ảnh/PDF")
        if m.get("loai_giay_phep") not in ("hoc", "dung-duoc"):
            kq.L("0", f"mẫu '{m.get('ten')}' thiếu loai_giay_phep (hoc | dung-duoc)")
    tr = ct.get("trang", [])
    kq.M(f"{len(tr)} trang mẫu đã gán kiểu")
    if len(tr) < 8:
        kq.L("0", "mẫu chính cần ≥8 trang đã gán kiểu (T01–T23 hoặc kiểu mới)")
    for t in tr:
        if not re.fullmatch(r"T\d{2}[a-z]?|M\d{2}", str(t.get("kieu", ""))):
            kq.L("0", f"trang {t.get('so')} có kiểu '{t.get('kieu')}' không hợp lệ")
    if not ct.get("bai_hoc"):
        kq.L("0", "thiếu 'bai_hoc': 3–8 điều học được từ mẫu (lưới, nhịp, cách viết tiêu đề, cách ghi nguồn)")
    tt = trang_thai(d)
    st = Path(tt.get("style", ""))
    if not st.exists():
        kq.L("0", "chưa có style cho báo cáo")
    if (Path(d) / "00-style.json").exists():
        s = doc_json(Path(d) / "00-style.json")
        if not s.get("do_tu"):
            kq.L("0", "00-style.json thiếu 'do_tu' (số đo gốc từ clone.py)")
        if not list((Path(d) / "00-so-sanh").glob("*.png")):
            kq.L("0", "clone phong cách cần ảnh so sánh trong 00-so-sanh/ (clone.py so-sanh)")


def cong_1(d, kq):
    p = Path(d) / "01-de-bai.md"
    if not p.exists():
        kq.L("1", "thiếu 01-de-bai.md")
        return
    t = p.read_text(encoding="utf-8")
    can_muc(kq, t, ["Người đọc", "Câu hỏi chính", "Loại báo cáo", "Phong cách", "Độ dài", "Hạn", "Dữ liệu sẵn có",
                    "Điều cấm", "Ảnh"], "01-de-bai.md")
    m = re.search(r"(\d+)\s*trang", t)
    if m:
        n = int(m.group(1))
        kq.M(f"độ dài dự kiến {n} trang")
        if not 8 <= n <= 80:
            kq.L("1", "độ dài nên 8–80 trang")
    else:
        kq.L("1", "mục Độ dài phải có số trang, ví dụ '24 trang'")


def cong_2(d, kq):
    p = Path(d) / "02-khung.json"
    if not p.exists():
        kq.L("2", "thiếu 02-khung.json")
        return
    k = doc_json(p)
    if not k.get("cau_hoi_chinh"):
        kq.L("2", "thiếu cau_hoi_chinh")
    nh = k.get("nhanh", [])
    kq.M(f"{len(nh)} nhánh cây vấn đề")
    if not 3 <= len(nh) <= 6:
        kq.L("2", "cây vấn đề nên có 3–6 nhánh (MECE)")
    ids = set()
    for n in nh:
        ids.add(n.get("id"))
        if not n.get("gia_thuyet"):
            kq.L("2", f"nhánh {n.get('id')} chưa có giả thuyết")
        p0 = [x for x in n.get("du_lieu", []) if x.get("uu_tien") == "P0"]
        if not p0:
            kq.L("2", f"nhánh {n.get('id')} chưa có dữ liệu P0")
    phu = {x for c in k.get("chuong", []) for x in c.get("nhanh", [])}
    for i in ids - phu:
        kq.L("2", f"nhánh {i} chưa thuộc chương nào")
    if not k.get("chuong"):
        kq.L("2", "thiếu danh sách chương")


def cong_3(d, kq, kiem_link=False):
    ng = nguon(d)
    bc = bang_chung(d)
    if not ng:
        kq.L("3", "thiếu hoặc rỗng 03-nguon.csv")
    if not bc:
        kq.L("3", "thiếu hoặc rỗng 03-bang-chung.jsonl")
    for k_, v in bc.items():
        if k_.startswith("__loi"):
            kq.L("3", f"03-bang-chung.jsonl lỗi JSON: {v['loi']}")
    kq.M(f"{len(ng)} nguồn, {len(bc)} bằng chứng")
    tang = [r.get("tang", "").strip() for r in ng.values()]
    if tang:
        ab = sum(1 for t in tang if t in ("A", "B")) / len(tang)
        kq.M(f"nguồn tầng A/B: {ab:.0%}")
        if ab < 0.6:
            kq.L("3", "nguồn tầng A/B dưới 60%")
    for ma, r in ng.items():
        if r.get("loai") not in ("so-cap", "thu-cap"):
            kq.L("3", f"nguồn {ma}: loai phải là so-cap hoặc thu-cap")
        if r.get("loai") == "thu-cap" and not r.get("url", "").startswith("http"):
            kq.L("3", f"nguồn {ma}: thiếu url")
        if not r.get("ngay_truy_cap"):
            kq.L("3", f"nguồn {ma}: thiếu ngay_truy_cap")
    for i, o in bc.items():
        if i.startswith("__"):
            continue
        if o.get("nguon") not in ng:
            kq.L("3", f"{i}: nguồn '{o.get('nguon')}' không có trong 03-nguon.csv")
        if not o.get("trich"):
            kq.L("3", f"{i}: thiếu đoạn trích nguyên văn")
    kp = Path(d) / "02-khung.json"
    if kp.exists():
        for n in doc_json(kp).get("nhanh", []):
            for x in n.get("du_lieu", []):
                if x.get("uu_tien") != "P0":
                    continue
                cs = x.get("chi_so")
                ev = [o for o in bc.values() if o.get("chi_so") == cs]
                srcs = {o.get("nguon") for o in ev}
                so_cap = any(ng.get(o.get("nguon"), {}).get("loai") == "so-cap" for o in ev)
                if not ev:
                    kq.L("3", f"P0 '{cs}' chưa có bằng chứng (ghi chi_so trùng tên trong 02-khung)")
                elif len(srcs) < 2 and not so_cap:
                    kq.C("3", f"P0 '{cs}' mới có 1 nguồn; nên đối chiếu nguồn thứ hai")
    if kiem_link:
        import urllib.request
        for ma, r in ng.items():
            u = r.get("url", "")
            if u.startswith("http"):
                try:
                    urllib.request.urlopen(urllib.request.Request(u, method="HEAD"), timeout=10)
                except Exception as e:  # noqa: BLE001
                    kq.C("3", f"link {ma} không mở được: {type(e).__name__}")


def hinh_spec(d):
    p = Path(d) / "04-hinh.json"
    return doc_json(p).get("hinh", []) if p.exists() else []


def khop(v, tap):
    best = None
    for x in tap:
        if x == 0:
            sai = 0 if v == 0 else 1
        else:
            sai = abs(v - x) / abs(x)
        best = sai if best is None else min(best, sai)
    return best


def cong_4(d, kq):
    hs = hinh_spec(d)
    bc = bang_chung(d)
    if not hs:
        kq.L("4", "thiếu 04-hinh.json hoặc chưa có hình nào")
    seen = set()
    kq.M(f"{len(hs)} hình")
    for h in hs:
        i = h.get("id")
        if i in seen:
            kq.L("4", f"trùng id {i}")
        seen.add(i)
        td = h.get("tieu_de", "")
        if not td.endswith("."):
            kq.L("V02", f"{i}: tiêu đề hình phải là câu có dấu chấm")
        ok, ly = la_cau_ket_luan(td.rstrip("."))
        if not ok:
            kq.L("V02", f"{i}: tiêu đề hình chưa là câu kết luận ({ly})")
        if not h.get("doi_tuong"):
            kq.L("D03", f"{i}: thiếu dòng đối tượng và đơn vị")
        if not h.get("nguon"):
            kq.L("D02", f"{i}: thiếu nguồn")
        if h.get("loai") == "bang":
            if not h.get("bang") or not h.get("bc"):
                kq.L("4", f"{i}: bảng cần 'bang' và 'bc'")
            continue
        if not (Path(d) / "04-hinh" / f"{i}.svg").exists():
            kq.L("4", f"{i}: chưa vẽ SVG (chạy hinh.py)")
        for c in h.get("chuoi", []):
            ds = c.get("bc") if isinstance(c.get("bc"), list) else [c.get("bc")]
            thieu = [b for b in ds if b not in bc]
            if thieu:
                kq.L("4", f"{i}/{c.get('ten')}: mã bằng chứng {thieu} không có")
                continue
            tap = [float(x) for b in ds for x in bc[b].get("so", [])] + [x for b in ds for x in cac_so(bc[b].get("trich", ""))]
            b = ",".join(ds)
            for v in c.get("gia_tri", []):
                s = khop(float(v), tap) if tap else None
                if s is None or s > 0.10:
                    kq.L("4", f"{i}/{c.get('ten')}: giá trị {v} không có trong {b}")
                elif s > 0.01:
                    kq.C("4", f"{i}/{c.get('ten')}: giá trị {v} lệch {s:.0%} so với {b}")


def doc_ghost(d):
    p = Path(d) / "05-ghost.md"
    if not p.exists():
        return None
    trang = []
    for dong in p.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\s*-\s*\[(T\d{2}[a-z]?|M\d{2})\]\s*(.+)$", dong)
        if m:
            phan = [x.strip() for x in m.group(2).split("|")]
            o = {"kieu": m.group(1), "thong_diep": phan[0]}
            for x in phan[1:]:
                if ":" in x:
                    k_, v = x.split(":", 1)
                    o[k_.strip()] = v.strip()
            trang.append(o)
    return trang


def cong_5(d, kq):
    tr = doc_ghost(d)
    if tr is None:
        kq.L("5", "thiếu 05-ghost.md")
        return
    kq.M(f"{len(tr)} trang trong ghost report")
    kieu = [t["kieu"] for t in tr]
    for k_ in ["T01"]:
        if k_ not in kieu:
            kq.L("D15", f"thiếu trang {k_}")
    if "T06" not in kieu and "T07" not in kieu:
        kq.L("D15", "thiếu trang tóm tắt điều hành (T06 hoặc T07)")
    if len(tr) > 12 and "T04" not in kieu:
        kq.L("D15", "báo cáo >12 trang cần mục lục (T04)")
    bc = bang_chung(d)
    ng = nguon(d)
    if any(ng.get(o.get("nguon"), {}).get("loai") == "so-cap" for o in bc.values()) and "T21" not in kieu:
        kq.L("V10", "có dữ liệu sơ cấp nên cần trang phương pháp (T21)")
    chu = {"T10", "T11"}
    lien = 0
    for t in tr:
        lien = lien + 1 if t["kieu"] in chu else 0
        if lien > 2:
            kq.L("D08", f"quá 2 trang chữ thuần liền nhau quanh '{t['thong_diep'][:40]}'")
    for t in tr:
        if t["kieu"] in ("T01", "T04", "T23", "T22"):
            continue
        ok, ly = la_cau_ket_luan(t["thong_diep"].rstrip("."))
        if not ok:
            kq.L("V01", f"thông điệp trang chưa là câu kết luận: '{t['thong_diep'][:50]}' ({ly})")
        if re.match(r"T(0[9]|1\d|20)", t["kieu"]) and not t.get("mau"):
            kq.L("mau", f"trang '{t['thong_diep'][:40]}' chưa có ảnh mẫu tham chiếu (| mau: ...)")
    dung = {x.strip() for t in tr if t.get("hinh") for x in t["hinh"].split(",")}
    for h in hinh_spec(d):
        if h["id"] not in dung:
            kq.C("5", f"hình {h['id']} chưa được gán vào trang nào")


# ---------------------------------------------------------------- đọc chương (markdown có khối :::)

def parse_runs(s, fn_list=None):
    """Chuỗi markdown nhẹ → runs. **đậm**, *nghiêng*, ^[chú thích], [BCxx]."""
    out = []
    pos = 0
    rx = re.compile(r"\*\*(.+?)\*\*|\*(.+?)\*|\^\[(.+?)\]|\[(BC\d+)\]")
    for m in rx.finditer(s):
        if m.start() > pos:
            out.append({"t": s[pos:m.start()]})
        if m.group(1):
            out.append({"b": m.group(1)})
        elif m.group(2):
            out.append({"i": m.group(2)})
        elif m.group(3):
            out.append({"fn": m.group(3)})
        else:
            out.append({"bcid": m.group(4)})
        pos = m.end()
    if pos < len(s):
        out.append({"t": s[pos:]})
    # gộp khoảng trắng thừa trước mã nguồn
    for i, r in enumerate(out):
        if "bcid" in r and i > 0 and "t" in out[i - 1]:
            out[i - 1]["t"] = out[i - 1]["t"].rstrip()
    return out


def doc_chuong(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    ch = {"tieu_de": "", "ten_ngan": "", "sapo": None, "khoi": []}
    i = 0
    doan = []

    def xa():
        if doan:
            ch["khoi"].append({"k": "p", "md": " ".join(doan)})
            doan.clear()

    while i < len(lines):
        ln = lines[i].rstrip()
        if ln.startswith("# "):
            xa()
            phan = [x.strip() for x in ln[2:].split("|")]
            ch["tieu_de"] = phan[0]
            ch["ten_ngan"] = phan[1] if len(phan) > 1 else phan[0]
        elif ln.startswith("> ") and ch["sapo"] is None and not ch["khoi"]:
            xa()
            ch["sapo"] = ln[2:].strip()
        elif ln.startswith("## "):
            xa()
            ch["khoi"].append({"k": "h2", "t": ln[3:].strip()})
        elif ln.startswith("::: "):
            xa()
            dau = ln[4:].strip()
            loai, _, thamso = dau.partition(" ")
            if loai == "hinh":
                ch["khoi"].append({"k": "hinh", "id": thamso.strip()})
            else:
                body = []
                i += 1
                while i < len(lines) and lines[i].strip() != ":::":
                    body.append(lines[i])
                    i += 1
                ts = [x.strip() for x in thamso.split("|")]
                if loai == "trich":
                    ch["khoi"].append({"k": "trich", "md": " ".join(b.strip() for b in body if b.strip()),
                                       "ai": ts[0] if ts and ts[0] else None})
                elif loai == "so-lon":
                    items = []
                    for b in body:
                        if "|" in b:
                            so, gt = b.split("|", 1)
                            items.append({"so": so.strip(), "giai_thich": gt.strip()})
                    ng_ = thamso.replace("Nguồn:", "").strip() or None
                    ch["khoi"].append({"k": "so-lon", "items": items, "nguon": ng_})
                elif loai == "sidebar":
                    ch["khoi"].append({"k": "sidebar", "t": ts[0], "nhan": ts[1] if len(ts) > 1 else "Góc nhìn",
                                       "md": [b.strip() for b in body if b.strip()]})
                elif loai == "khuyen-nghi":
                    items = []
                    for b in body:
                        if "|" in b:
                            t_, r_ = b.split("|", 1)
                            items.append({"t": t_.strip(), "md": r_.strip()})
                    ch["khoi"].append({"k": "khuyen-nghi", "items": items})
        elif re.match(r"^\s*-\s+", ln):
            xa()
            items = []
            while i < len(lines) and re.match(r"^\s*-\s+", lines[i]):
                items.append(re.sub(r"^\s*-\s+", "", lines[i]).strip())
                i += 1
            ch["khoi"].append({"k": "ul", "md": items})
            continue
        elif re.match(r"^\d+\.\s+", ln):
            xa()
            ch["khoi"].append({"k": "diem", "md": re.sub(r"^\d+\.\s+", "", ln).strip()})
        elif not ln.strip():
            xa()
        else:
            doan.append(ln.strip())
        i += 1
    xa()
    return ch


def van_ban_chuong(ch):
    """Mọi đoạn văn (markdown) trong chương để kiểm văn và kiểm số."""
    out = []
    for b in ch["khoi"]:
        if b["k"] in ("p", "trich", "diem"):
            out.append(b["md"])
        elif b["k"] == "ul":
            out += b["md"]
        elif b["k"] == "sidebar":
            out += b["md"]
        elif b["k"] == "khuyen-nghi":
            out += [x["md"] for x in b["items"]]
    return out


# ---------------------------------------------------------------- cổng 6–7

def kiem_van(d, kq):
    fs = chuong_files(d)
    if not fs:
        kq.L("6", "chưa có chương nào trong 06-chuong/")
        return
    bc = bang_chung(d)
    hs = {h["id"] for h in hinh_spec(d)}
    tong_chu, ai_dem = 0, 0
    do_dai = []
    for f in fs:
        ch = doc_chuong(f)
        ten = f.name
        la_tt = f.name.startswith("00")
        if not la_tt:
            ok, ly = la_cau_ket_luan(ch["tieu_de"])
            if not ok:
                kq.L("V01", f"{ten}: tiêu đề chương chưa là câu kết luận ({ly})")
        for b in ch["khoi"]:
            if b["k"] == "h2":
                ok, ly = la_cau_ket_luan(b["t"])
                if not ok:
                    kq.L("V01", f"{ten}: mục '{b['t'][:40]}' chưa là câu kết luận ({ly})")
            if b["k"] == "hinh" and b["id"] not in hs:
                kq.L("6", f"{ten}: hình {b['id']} không có trong 04-hinh.json")
            if b["k"] == "so-lon" and not b.get("nguon"):
                kq.L("D17", f"{ten}: khối số lớn thiếu nguồn (::: so-lon Nguồn: ...)")
        diem = [b for b in ch["khoi"] if b["k"] == "diem"]
        if la_tt:
            kq.M(f"tóm tắt có {len(diem)} phát hiện")
            if not 3 <= len(diem) <= 7:
                kq.L("V03", "tóm tắt điều hành cần 3–7 phát hiện")
            for x in diem:
                m = re.match(r"\*\*(.+?)\*\*", x["md"])
                if not m:
                    kq.L("V03", f"phát hiện phải mở bằng câu kết luận in đậm: '{x['md'][:40]}'")
                    continue
                if tieng(m.group(1)) > 25:
                    kq.L("V03", f"câu kết luận dài {tieng(m.group(1))} tiếng (>25): '{m.group(1)[:40]}'")
                if not re.search(r"\d", x["md"]):
                    kq.L("V03", f"phát hiện chưa có con số: '{m.group(1)[:40]}'")
        for doan in van_ban_chuong(ch):
            tong_chu += tieng(doan)
            low = doan.lower()
            ai_dem += sum(low.count(g) for g in GIONG_AI)
            if "—" in doan or "–" in doan:
                kq.L("V09", f"{ten}: có gạch ngang dài: '{doan[:40]}'")
            if re.search(r"(?<![\d.])\d{1,3},\d{3}(?!\d)", doan):
                kq.L("V06", f"{ten}: số kiểu Anh (dấu phẩy nghìn): '{re.search(r'\d{1,3},\d{3}', doan).group(0)}'")
            if re.search(r"(?<![\d.,])\d+\.\d{1,2}(?![\d.])\s*%", doan):
                kq.L("V06", f"{ten}: thập phân phải dùng dấu phẩy: '{re.search(r'\d+\.\d{1,2}\s*%', doan).group(0)}'")
            for cau in tach_cau(doan):
                n = tieng(re.sub(r"\[BC\d+\]|\^\[[^\]]*\]", "", cau))
                do_dai.append(n)
                if n > 55:
                    kq.C("V08", f"{ten}: câu {n} tiếng: '{cau[:50]}'")
                so = cac_so(cau)
                ma = re.findall(r"\[(BC\d+)\]", cau)
                if so and not ma and not re.search(r"\[(SUY LUẬN|minh hoạ|minh họa)\]", cau, re.I):
                    kq.L("so-khong-nguon", f"{ten}: câu có số nhưng không có [BCxx]: '{cau[:60]}'")
                for x in ma:
                    if x not in bc:
                        kq.L("so-khong-nguon", f"{ten}: mã {x} không có trong 03-bang-chung.jsonl")
    if do_dai:
        kq.M(f"câu trung vị {statistics.median(do_dai):.0f} tiếng")
        if statistics.median(do_dai) > 28:
            kq.C("V08", "câu trung vị dài hơn 28 tiếng")
    if tong_chu:
        mat_do = ai_dem / tong_chu * 1000
        kq.M(f"{tong_chu} tiếng; mẫu giọng AI {mat_do:.1f}/1000 tiếng")
        if mat_do > 2:
            kq.L("giong-ai", f"mẫu giọng AI {mat_do:.1f}/1000 tiếng (>2)")
    vb = GOC.parent / "linhx-viet-bai" / "scripts" / "kiem_van.py"
    if vb.exists():
        kq.M("có linhx-viet-bai: chạy thêm kiem_van.py để soát giọng Linh")


def kiem_so(d, kq, ghi=True):
    bc = bang_chung(d)
    kq_so = []
    for f in chuong_files(d):
        ch = doc_chuong(f)
        for doan in van_ban_chuong(ch):
            for cau in tach_cau(doan):
                ma = re.findall(r"\[(BC\d+)\]", cau)
                if not ma:
                    continue
                tap = []
                for x in ma:
                    o = bc.get(x, {})
                    tap += [float(v) for v in o.get("so", [])] + cac_so(o.get("trich", ""))
                for v in cac_so(cau):
                    s = khop(v, tap) if tap else None
                    if s is None or s > 0.10:
                        muc = "mo-coi"
                        kq.L("so-mo-coi", f"{f.name}: số {v:g} không khớp {','.join(ma)}: '{cau[:60]}'")
                    elif s > 0.01:
                        muc = "can-duyet"
                        kq.C("so-xap-xi", f"{f.name}: số {v:g} lệch {s:.0%} so với {','.join(ma)}")
                    else:
                        muc = "dat"
                    kq_so.append({"tep": f.name, "so": v, "ma": ma, "muc": muc, "cau": cau[:200]})
                for q in re.findall(r"“([^”]{12,})”", cau):
                    if not any(q in bc.get(x, {}).get("trich", "") for x in ma):
                        kq.L("trich-sai", f"{f.name}: trích dẫn không khớp nguyên văn {','.join(ma)}: '{q[:50]}'")
    dem = {m: sum(1 for x in kq_so if x["muc"] == m) for m in ("dat", "can-duyet", "mo-coi")}
    kq.M(f"số đã đối chiếu: {dem}")
    if ghi:
        ghi_json(Path(d) / "07-kiem-so.json", {"luc": bay_gio(), "dem": dem, "chi_tiet": kq_so})


# ---------------------------------------------------------------- dựng IR + Typst

def style_bao_cao(d):
    tt = trang_thai(d)
    return doc_json(tt["style"])


def ir(d):
    d = Path(d)
    tt = trang_thai(d)
    th = style_bao_cao(d)
    bc = bang_chung(d)
    ng = nguon(d)
    hs = {h["id"]: h for h in hinh_spec(d)}
    thu_tu_nguon = []

    def so_nguon(bcid):
        o = bc.get(bcid)
        key = o["nguon"] if o else bcid
        if key not in thu_tu_nguon:
            thu_tu_nguon.append(key)
        return thu_tu_nguon.index(key) + 1

    def R(s):
        rs = parse_runs(s)
        out = []
        for r in rs:
            if "bcid" in r:
                out.append({"bc": so_nguon(r["bcid"])})
            else:
                out.append(r)
        return out

    dem_hinh = [0]

    def B(b):
        k = b["k"]
        if k == "p":
            return {"k": "p", "r": R(b["md"])}
        if k == "h2":
            return b
        if k == "ul":
            return {"k": "ul", "items": [R(x) for x in b["md"]]}
        if k == "diem":
            return {"k": "p", "r": R(b["md"])}
        if k == "trich":
            return {"k": "trich", "r": R(b["md"]), "ai": b.get("ai")}
        if k == "so-lon":
            return b
        if k == "sidebar":
            return {"k": "sidebar", "t": b["t"], "nhan": b["nhan"], "khoi": [{"k": "p", "r": R(x)} for x in b["md"]]}
        if k == "khuyen-nghi":
            return {"k": "khuyen-nghi", "items": [{"t": x["t"], "r": R(x["md"])} for x in b["items"]]}
        if k == "hinh":
            h = hs[b["id"]]
            dem_hinh[0] += 1
            o = {"k": "hinh", "so": dem_hinh[0], "tieu_de": h["tieu_de"], "doi_tuong": h.get("doi_tuong"),
                 "nguon": h["nguon"], "ghi_chu": h.get("ghi_chu"), "rong": h.get("rong", "full")}
            if h["loai"] == "bang":
                o["bang"] = h["bang"]
            else:
                o["svg"] = f"../04-hinh/{h['id']}.svg"
            return o
        raise ValueError(k)

    fs = chuong_files(d)
    tt_file = [f for f in fs if f.name.startswith("00")]
    tom = {"tieu_de": "Những điểm chính", "mo": None, "kpi": [], "diem": []}
    if tt_file:
        c = doc_chuong(tt_file[0])
        tom["tieu_de"] = c["tieu_de"] or tom["tieu_de"]
        tom["mo"] = c["sapo"]
        for b in c["khoi"]:
            if b["k"] == "so-lon":
                tom["kpi"] = b["items"]
                tom["kpi_nguon"] = b.get("nguon")
            if b["k"] == "diem":
                m = re.match(r"\*\*(.+?)\*\*\s*(.*)", b["md"])
                tom["diem"].append({"y": R(m.group(1)) if m else R(b["md"]), "chi_tiet": R(m.group(2)) if m else []})
    chuong = []
    pp = []
    so = 0
    for f in fs:
        if f.name.startswith("00"):
            continue
        c = doc_chuong(f)
        if f.stem.endswith("phuong-phap"):
            pp = [B(b) for b in c["khoi"]]
            continue
        so += 1
        anh = d / "09-anh" / f"chuong-{so}.jpg"
        chuong.append({"so": so, "tieu_de": c["tieu_de"], "ten_ngan": c["ten_ngan"], "sapo": c["sapo"],
                       "anh": f"../09-anh/chuong-{so}.jpg" if anh.exists() else None,
                       "khoi": [B(b) for b in c["khoi"]]})
    meta = {"tieu_de": tt.get("ten", ""), "tieu_de_ngan": tt.get("ten_ngan", tt.get("ten", "")),
            "phu_de": tt.get("phu_de", ""), "nhan_loat": tt.get("nhan_loat", "Báo cáo chuyên đề"),
            "tac_gia": tt.get("tac_gia", "LINHX"), "ngay": tt.get("ngay", dt.date.today().strftime("Tháng %m/%Y")),
            "don_vi": tt.get("don_vi", "LINHX"), "chan_trang": tt.get("chan_trang", tt.get("ten_ngan", "")),
            "ban_quyen": tt.get("ban_quyen", "© LINHX. Tài liệu lưu hành nội bộ."),
            # trang lót luận đề (T03) tuỳ chọn, gộp vào nửa dưới trang mục lục
            "luan_de": tt.get("luan_de"), "luan_de_phu": tt.get("luan_de_phu"),
            "luan_de_nhan": tt.get("luan_de_nhan", "Câu trả lời ngắn")}
    bia = d / "09-anh" / "bia.jpg"
    nguon_ds = []
    for key in thu_tu_nguon:
        r = ng.get(key, {})
        mo = ", ".join(x for x in [r.get("don_vi", ""), r.get("ten", key), r.get("ngay_xuat_ban", "")] if x)
        if r.get("url"):
            mo += f". {r['url']} (truy cập {r.get('ngay_truy_cap', '')})"
        nguon_ds.append({"ma": key, "mo_ta": mo})
    return {"meta": meta, "theme": th, "bia": {"anh": "../09-anh/bia.jpg" if bia.exists() else None},
            "tom_tat": tom, "chuong": chuong, "phuong_phap": pp, "nguon": nguon_ds}


def tim_typst():
    for c in [os.environ.get("TYPST_BIN"), shutil.which("typst"), str(GOC / "bin" / "typst"),
              str(GOC / "bin" / "typst.exe")]:
        if c and Path(c).exists():
            return c
    raise SystemExit("Không thấy Typst. Windows: winget install --id Typst.Typst ; hoặc đặt biến TYPST_BIN.")


def dung(d):
    d = Path(d)
    data = ir(d)
    out = d / "10-typst"
    out.mkdir(exist_ok=True)
    ghi_json(d / "10-bao-cao.json", data)
    shutil.copy(GOC / "typst" / "lib.typ", out / "lib.typ")
    shutil.copy(d / "10-bao-cao.json", out / "bao-cao.json")
    (out / "main.typ").write_text('#import "lib.typ": bao-cao\n#bao-cao(json("bao-cao.json"))\n', encoding="utf-8")
    cmd = [tim_typst(), "compile", "--root", str(d), "--font-path", str(GOC / "fonts"), "--ignore-system-fonts",
           str(out / "main.typ"), str(d / "bao-cao.pdf")]
    r = subprocess.run(cmd, capture_output=True, text=True)
    (out / "bien-dich.log").write_text(r.stdout + r.stderr, encoding="utf-8")
    if r.returncode != 0:
        print(r.stderr)
        raise SystemExit("Typst biên dịch lỗi, xem 10-typst/bien-dich.log")
    print("đã dựng", d / "bao-cao.pdf", "|", (r.stderr.strip() or "không cảnh báo")[:300])


def cong_10(d, kq):
    d = Path(d)
    pdf = d / "bao-cao.pdf"
    if not pdf.exists():
        kq.L("10", "chưa có bao-cao.pdf (chạy report.py dung)")
        return
    log = (d / "10-typst" / "bien-dich.log")
    if log.exists() and "error" in log.read_text(encoding="utf-8").lower():
        kq.L("10", "log biên dịch có lỗi")
    moi_nhat = max([f.stat().st_mtime for f in chuong_files(d)] + [(d / "04-hinh.json").stat().st_mtime]
                   if (d / "04-hinh.json").exists() else [0])
    if pdf.stat().st_mtime < moi_nhat:
        kq.L("10", "PDF cũ hơn nội dung: dựng lại")


# ---------------------------------------------------------------- kiểm bản in (D01–D17)

def kiem_ban_in(d, kq, ghi=True):
    import pymupdf
    d = Path(d)
    th = style_bao_cao(d)
    pdf = d / "bao-cao.pdf"
    if not pdf.exists():
        kq.L("11", "chưa có bao-cao.pdf")
        return
    doc = pymupdf.open(pdf)
    n = len(doc)
    kq.M(f"{n} trang")
    nhan_hinh = th["hinh"]["nhan"].upper()
    so_hinh, co_chu, ky_tu, phu, co_hinh, fonts = [], [], [], [], [], set()
    chi_tiet = []
    for i, pg in enumerate(doc):
        W, H = pg.rect.width, pg.rect.height
        dct = pg.get_text("dict")
        txt = pg.get_text()
        ky_tu.append(len(txt))
        dien_tich = 0
        tieu_de_cuoi = []
        for b in dct["blocks"]:
            if b.get("type") != 0:
                continue
            x0, y0, x1, y1 = b["bbox"]
            dien_tich += (x1 - x0) * (y1 - y0)
            for ln in b["lines"]:
                for sp in ln["spans"]:
                    t = sp["text"].strip()
                    if not t:
                        continue
                    fonts.add(re.sub(r"^[A-Z]{6}\+", "", sp["font"]).split("-")[0])
                    if 0 < i < n - 1 and H * 0.08 < ln["bbox"][1] < H * 0.92:
                        co_chu.extend([round(sp["size"], 1)] * len(t))
                    if "�" in t:
                        kq.L("D11", f"trang {i + 1}: ký tự hỏng '{t[:30]}'")
                    if 0 < i < n - 1 and sp["size"] >= th["co"]["h2"] - 0.5 and H * 0.85 < ln["bbox"][1] < H * 0.92 and sp["size"] < th["co"]["h1"]:
                        tieu_de_cuoi.append(t)
        phu.append(dien_tich / (W * H))
        # Trang có nhãn "HÌNH N" là trang có hình, kể cả biểu đồ SVG ít nét vẽ (2–3 cột) hay bảng.
        hinh = (len(pg.get_images()) > 0 or len(pg.get_drawings()) > 25
                or re.search(re.escape(nhan_hinh) + r"\s+\d+", txt) is not None)
        co_hinh.append(hinh)
        for m in re.finditer(nhan_hinh + r" (\d+)", txt):
            so_hinh.append((int(m.group(1)), i + 1))
            sau = txt[m.end():]
            if "Nguồn:" not in sau:
                kq.L("D02", f"trang {i + 1}: {nhan_hinh} {m.group(1)} không thấy 'Nguồn:' phía dưới")
        for t in tieu_de_cuoi:
            kq.L("D14", f"trang {i + 1}: tiêu đề mồ côi cuối trang '{t[:40]}'")
        if 0 < i < n - 1:
            if not re.search(r"(^|\n)\s*" + str(i + 1) + r"\s*(\n|$)", txt):
                kq.C("D13", f"trang {i + 1}: không thấy số trang")
            if len(txt.strip()) < 40 and not hinh:
                kq.L("11", f"trang {i + 1}: trang trắng hoặc gần trắng")
        chi_tiet.append({"trang": i + 1, "ky_tu": len(txt), "phu_chu": round(dien_tich / (W * H), 3), "co_hinh": hinh})
    # D01
    so = [s for s, _ in so_hinh]
    if so and so != list(range(1, len(so) + 1)):
        kq.L("D01", f"số hình không liên tục: {so}")
    kq.M(f"{len(so)} hình đánh số")
    # D04
    if co_chu:
        mode = statistics.mode(co_chu)
        kq.M(f"cỡ chữ phổ biến {mode} pt")
        if not 9 <= mode <= 11.5:
            kq.L("D04", f"cỡ chữ thân {mode} pt ngoài 9–11,5")
    # D06, D07, D08
    noi_dung = ky_tu[2:-1] if n > 4 else ky_tu
    if noi_dung:
        tv = statistics.median(noi_dung)
        kq.M(f"ký tự/trang trung vị {tv:.0f}, lớn nhất {max(noi_dung)}")
        for i, k_ in enumerate(ky_tu):
            if k_ > 4300 and i < n - 2:
                kq.L("D06", f"trang {i + 1}: {k_} ký tự (>4.300)")
    if phu:
        pv = statistics.median(phu[1:-1] if n > 2 else phu)
        lo, hi = th.get("nguong", {}).get("phu_chu", [0.18, 0.4])
        kq.M(f"phủ chữ trung vị {pv:.2f} (mục tiêu {lo}–{hi})")
        if not lo - 0.05 <= pv <= hi + 0.05:
            kq.C("D07", f"phủ chữ {pv:.2f} lệch mục tiêu phong cách")
    lien = 0
    for i, h in enumerate(co_hinh[1:-1], 2):
        lien = 0 if h else lien + 1
        if lien > 3:
            kq.C("D08", f"trang {i}: hơn 3 trang chữ thuần liền nhau")
    # D10, D11
    ho = {f.replace("SourceSerif4", "Source Serif 4").replace("BeVietnamPro", "Be Vietnam Pro") for f in fonts}
    kq.M(f"font: {sorted(ho)}")
    khai = {th["font"]["tieu_de"], th["font"]["than"], th["font"]["phu"]}
    la = {f for f in ho if not any(k_.replace(" ", "") in f.replace(" ", "") for k_ in khai)}
    if la:
        kq.L("D11", f"có font ngoài khai báo (rơi font dự phòng?): {sorted(la)}")
    if len(ho) > 2 + (1 if la else 0):
        kq.L("D10", f"{len(ho)} họ font (tối đa 2)")
    # chấm trang (Claude đã xem từng trang)
    cham = d / "11-cham-trang.json"
    if not cham.exists():
        kq.L("11", "chưa có 11-cham-trang.json: chạy anh-trang rồi xem và chấm từng trang theo rubric tạp chí")
    else:
        ct = doc_json(cham)
        da = {x["trang"] for x in ct}
        thieu = [i for i in range(1, n + 1) if i not in da]
        if thieu:
            kq.L("11", f"chưa chấm trang: {thieu[:15]}")
        for x in ct:
            dm = x.get("diem", {})
            if len(dm) < 5:
                kq.L("11", f"trang {x['trang']}: cần đủ 5 tiêu chí rubric")
                continue
            tb = sum(dm.values()) / len(dm)
            if tb < 3.5 or min(dm.values()) < 3:
                kq.L("tap-chi", f"trang {x['trang']}: điểm {tb:.1f} (min {min(dm.values())}), cần dựng lại: {x.get('sua', '')}")
        if cham.stat().st_mtime < pdf.stat().st_mtime:
            kq.L("11", "PDF mới hơn bảng chấm: chấm lại các trang đã đổi")
    if ghi:
        ghi_json(d / "11-kiem-ban-in.json", {"luc": bay_gio(), "loi": kq.loi, "canh_bao": kq.canh_bao,
                                             "do": kq.do, "trang": chi_tiet})


def anh_trang(d, dpi=70):
    import pymupdf
    d = Path(d)
    out = d / "11-anh-trang"
    out.mkdir(exist_ok=True)
    doc = pymupdf.open(d / "bao-cao.pdf")
    for i, pg in enumerate(doc):
        pg.get_pixmap(dpi=dpi).save(out / f"trang-{i + 1:02d}.png")
    # ảnh ghép xem nhanh 4 trang một hàng
    try:
        from PIL import Image
        ims = [Image.open(out / f"trang-{i + 1:02d}.png") for i in range(len(doc))]
        w, h = ims[0].size
        cot = 4
        hang = (len(ims) + cot - 1) // cot
        g = Image.new("RGB", (w * cot + 10 * (cot + 1), h * hang + 10 * (hang + 1)), "#8a8f98")
        for k, im in enumerate(ims):
            g.paste(im, (10 + (k % cot) * (w + 10), 10 + (k // cot) * (h + 10)))
        g.save(out / "tong-quan.jpg", quality=85)
    except ImportError:
        pass
    print(f"đã render {len(doc)} trang vào {out}")


# ---------------------------------------------------------------- cổng 8, 9, 12

def cong_8(d, kq):
    d = Path(d)
    p = d / "08-phan-bien.md"
    if not p.exists():
        kq.L("8", "thiếu 08-phan-bien.md")
    else:
        t = p.read_text(encoding="utf-8")
        for m in ["Người đọc mới", "Partner"]:
            if not re.search(r"^#+\s*" + m, t, re.M | re.I):
                kq.L("8", f"thiếu phần phản biện '{m}'")
        mo = [x for x in re.findall(r"^\s*-\s*\[ \]\s*(.+)$", t, re.M) if "Lý do:" not in x]
        if mo:
            kq.L("8", f"{len(mo)} điểm phản biện chưa xử lý (đánh [x] hoặc ghi 'Lý do:')")
    if not any(f.name.startswith("00") for f in chuong_files(d)):
        kq.L("8", "thiếu 06-chuong/00-tom-tat.md (viết sau cùng)")


def cong_9(d, kq):
    d = Path(d)
    de = (d / "01-de-bai.md").read_text(encoding="utf-8") if (d / "01-de-bai.md").exists() else ""
    m = re.search(r"^#+\s*Ảnh\s*\n+(.+)", de, re.M)
    khong = m and re.search(r"không", m.group(1), re.I)
    nk = d / "09-anh" / "nhat-ky.json"
    if khong and not nk.exists():
        kq.M("đề bài chọn không dùng ảnh: bìa và mở chương dùng khối màu")
        return
    if not nk.exists():
        kq.L("9", "thiếu 09-anh/nhat-ky.json (hoặc ghi 'Ảnh: không' trong đề bài)")
        return
    for a in doc_json(nk):
        if not a.get("ref"):
            kq.L("9", f"ảnh {a.get('ten')}: thiếu ảnh tham chiếu")
        if not a.get("dat"):
            kq.L("9", f"ảnh {a.get('ten')}: chưa qua rà H1–H8")
        if not (d / "09-anh" / a.get("ten", "?")).exists():
            kq.L("9", f"ảnh {a.get('ten')}: không có tệp")


def cong_12(d, kq):
    d = Path(d) / "12-ban-giao"
    for f in ["bao-cao.pdf", "README.md"]:
        if not (d / f).exists():
            kq.L("12", f"12-ban-giao thiếu {f}")
    if (d / "README.md").exists():
        t = (d / "README.md").read_text(encoding="utf-8")
        for m in ["Nguồn", "Linh cần làm"]:
            if m not in t:
                kq.L("12", f"README bàn giao thiếu mục '{m}'")


# ---------------------------------------------------------------- điều phối

TEN = {0: "Tìm mẫu, clone phong cách", 1: "Đề bài", 2: "Khung phân tích", 3: "Nghiên cứu, sổ nguồn",
       4: "Dữ liệu và hình", 5: "Ghost report", 6: "Viết chương", 7: "Kiểm số và trích dẫn",
       8: "Biên tập, phản biện, tóm tắt", 9: "Ảnh bìa, mở chương", 10: "Dàn trang Typst",
       11: "Kiểm bản in, chấm từng trang", 12: "Bàn giao"}
LINH_DUYET = {0, 1, 2, 5, 11, 12}


def chay_cong(d, n, **kw):
    kq = KQ()
    f = {0: cong_0, 1: cong_1, 2: cong_2, 3: cong_3, 4: cong_4, 5: cong_5, 6: kiem_van, 7: kiem_so,
         8: cong_8, 9: cong_9, 10: cong_10, 11: kiem_ban_in, 12: cong_12}[n]
    if n == 3:
        f(d, kq, kiem_link=kw.get("kiem_link", False))
    else:
        f(d, kq)
    tt = trang_thai(d)
    tt.setdefault("buoc", {})[str(n)] = {"dat": kq.dat(), "luc": bay_gio(), "loi": len(kq.loi),
                                         "canh_bao": len(kq.canh_bao),
                                         "duyet": tt.get("buoc", {}).get(str(n), {}).get("duyet")}
    luu_tt(d, tt)
    kq.in_ra(f"Cổng {n} · {TEN[n]}")
    if kq.dat() and n in LINH_DUYET and not tt["buoc"][str(n)].get("duyet"):
        print(f"  → cần Linh duyệt bước {n} (report.py duyet {d} {n}); 10 phút không trả lời thì duyệt theo khuyến nghị")
    return kq


def ap_brand(th, brand):
    """Đổ màu brand vào style. Style clone từ mẫu ngoài (có do_tu) luôn bị thay màu, không giữ nhận diện của hãng mẫu."""
    br = doc_json(DU_LIEU / "thuong-hieu.json").get(brand)
    if br is None:
        raise SystemExit(f"không có brand {brand}")
    m = br["mau"]
    if brand != "linhx" or th.get("do_tu"):
        th["mau_mau_goc"] = dict(th["mau"])
        nhan = m["nhan"] if tuong_phan(m["nhan"], "#FFFFFF") >= 3 else m.get("canh_bao", m["tieu_de"])
        th["mau"].update({"chinh": m["tieu_de"], "nhan": nhan, "nhan_toi": m["nhan_toi"], "chu": m["chu"],
                          "chu_phu": m["chu_phu"], "nen_phu": m["xen"], "ke": m["vien"]})
        th["mau"]["bieu_do"] = [m["tieu_de"], nhan, m["chu_phu"], m["vien"], m["xen"]]
    th["brand"] = brand
    return th


def ap_style(d, tu):
    tt = trang_thai(d)
    th = ap_brand(doc_json(tu), tt.get("brand", "linhx"))
    ghi_json(Path(d) / "style.json", th)
    tt["style"] = str((Path(d) / "style.json").resolve())
    tt["phong_cach"] = th.get("ten", Path(tu).parent.name)
    luu_tt(d, tt)
    print(f"đã áp style {th.get('ten')} + brand {tt.get('brand')} vào {d}/style.json")


def moi(d, ten, phong_cach, brand):
    d = Path(d)
    d.mkdir(parents=True, exist_ok=True)
    pc = Path(phong_cach)
    if not pc.exists():
        pc = DU_LIEU / "phong-cach" / phong_cach
    th = ap_brand(doc_json(pc / "style.json"), brand)
    ghi_json(d / "style.json", th)
    for f in [DU_LIEU / "mau" / x for x in ("01-de-bai.md", "05-ghost.md", "08-phan-bien.md")]:
        if not (d / f.name).exists():
            shutil.copy(f, d / f.name)
    (d / "06-chuong").mkdir(exist_ok=True)
    tt = {"ten": ten, "ten_ngan": ten, "phong_cach": str(pc.name), "brand": brand, "style": str((d / "style.json").resolve()),
          "tao_luc": bay_gio(), "buoc": {}}
    luu_tt(d, tt)
    print(f"đã tạo {d} · phong cách {pc.name} · brand {brand}")


def lum(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def tuong_phan(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


def trang_thai_in(d):
    tt = trang_thai(d)
    print(f"{tt.get('ten')} · {tt.get('phong_cach')} · {tt.get('brand')}")
    tiep = None
    for n in range(13):
        b = tt.get("buoc", {}).get(str(n))
        if b and b.get("dat"):
            dd = f" · duyệt: {b['duyet'].get('nguoi')}" if b.get("duyet") else (" · CHỜ LINH DUYỆT" if n in LINH_DUYET else "")
            print(f"  ✓ {n:>2} {TEN[n]}{dd}")
            if n in LINH_DUYET and not b.get("duyet") and tiep is None:
                tiep = n
        else:
            print(f"  ○ {n:>2} {TEN[n]}" + (f" (lỗi {b['loi']})" if b else ""))
            if tiep is None:
                tiep = n
    print(f"→ bước tiếp: {tiep} {TEN.get(tiep, '')}" if tiep is not None else "→ xong")


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="lenh", required=True)
    a = sp.add_parser("moi")
    a.add_argument("dir")
    a.add_argument("--ten", required=True)
    a.add_argument("--phong-cach", default="p1-chien-luoc")
    a.add_argument("--brand", default="linhx")
    for t in ["trang-thai", "kiem-van", "kiem-so", "dung", "kiem-ban-in"]:
        sp.add_parser(t).add_argument("dir")
    a = sp.add_parser("cong")
    a.add_argument("dir")
    a.add_argument("n", type=int)
    a.add_argument("--kiem-link", action="store_true")
    a = sp.add_parser("duyet")
    a.add_argument("dir")
    a.add_argument("n", type=int)
    a.add_argument("--nguoi", default="Linh")
    a = sp.add_parser("ap-style")
    a.add_argument("dir")
    a.add_argument("--tu", required=True, help="00-style.json hoặc du-lieu/phong-cach/<ten>/style.json")
    a = sp.add_parser("anh-trang")
    a.add_argument("dir")
    a.add_argument("--dpi", type=int, default=70)
    g = ap.parse_args()
    if g.lenh == "moi":
        moi(g.dir, g.ten, g.phong_cach, g.brand)
    elif g.lenh == "trang-thai":
        trang_thai_in(g.dir)
    elif g.lenh == "cong":
        sys.exit(0 if chay_cong(g.dir, g.n, kiem_link=g.kiem_link).dat() else 1)
    elif g.lenh == "duyet":
        tt = trang_thai(g.dir)
        b = tt.setdefault("buoc", {}).setdefault(str(g.n), {})
        if not b.get("dat"):
            raise SystemExit(f"bước {g.n} chưa qua cổng máy, không duyệt được")
        b["duyet"] = {"nguoi": g.nguoi, "luc": bay_gio()}
        luu_tt(g.dir, tt)
        print(f"đã ghi duyệt bước {g.n} bởi {g.nguoi}")
    elif g.lenh == "kiem-van":
        kq = KQ()
        kiem_van(g.dir, kq)
        kq.in_ra("Kiểm văn")
    elif g.lenh == "kiem-so":
        kq = KQ()
        kiem_so(g.dir, kq)
        kq.in_ra("Kiểm số")
    elif g.lenh == "dung":
        dung(g.dir)
    elif g.lenh == "kiem-ban-in":
        kq = KQ()
        kiem_ban_in(g.dir, kq)
        kq.in_ra("Kiểm bản in")
    elif g.lenh == "ap-style":
        ap_style(g.dir, g.tu)
    elif g.lenh == "anh-trang":
        anh_trang(g.dir, g.dpi)


if __name__ == "__main__":
    main()
