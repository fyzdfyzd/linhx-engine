"""Kiểm đề trước khi giao (A, Linh 10/11/2026). 0 token, chạy khi viết/khoá features.

  py -3.12 canh/kiem_de.py features-dotN.json [--ca-da-dat] [--json]

Bắt 3 loại lỗi đề đã làm thợ trượt oan (B4 thiếu hooks.py trong vùng, C2/D2 đòi kênh chưa có):
  1. VUNG: mọi đường dẫn mà test_<id>.py trỏ tới (GOC / "a" / "b", chuỗi "a/b.py", nap_module(.., DIR))
     phải nằm trong vung của feature, hoặc trong vung của feature nó phu_thuoc (đọc, không sửa).
  2. TIEU_CHI: mỗi tiêu chí có một test ghi docstring "Tiêu chí: <đúng câu đó>".
  3. PHU_THUOC: id phụ thuộc có thật (mọi features-dot*.json), không vòng; đường dẫn test đụng vào vùng
     của feature khác thì feature đó phải là phụ thuộc (trực tiếp hoặc bắc cầu).
Thêm: lenh_kiem phải gọi tests/nghiem-thu/test_<id>.py và file đó có thật.
Mặc định bỏ qua feature đã passes:true (đã khoá, đề cũ). Mã thoát 1 nếu có LOI.
"""
import ast
import fnmatch
import json
import pathlib
import re
import sys
import unicodedata

GOC = pathlib.Path(__file__).resolve().parents[1]
NT = GOC / "tests" / "nghiem-thu"
CHI_DOC = ("tests/nghiem-thu", "bang-chung", ".canh-tho", ".canh")  # đọc hoặc tự có, không cần vùng


def chuan(s):
    s = unicodedata.normalize("NFC", s).lower()
    return re.sub(r"[\s\W_]+", " ", s).strip()


def khop(duong, mau):
    """duong khớp glob vung (hỗ trợ **). Thư mục khớp nếu có file trong vùng nằm dưới nó."""
    m = mau.rstrip("/")
    if fnmatch.fnmatch(duong, m) or duong == m:
        return True
    if m.endswith("/**") and (duong == m[:-3] or duong.startswith(m[:-2])):
        return True
    goc_mau = re.split(r"[*?\[]", m)[0].rstrip("/")
    return bool(goc_mau) and goc_mau.startswith(duong + "/")  # duong là thư mục cha của vùng


class Duong:
    """Giải đường dẫn trong một file test: GOC / "a" / "b", biến gán từ đó, chuỗi "a/b.py"."""

    def __init__(self, p):
        self.cay = ast.parse(p.read_text(encoding="utf-8"))
        self.bien = {"GOC": "", "REPO": "", "CORE": "apps/linhx_core", "BANG_CHUNG": "bang-chung"}
        for _ in range(2):
            for n in ast.walk(self.cay):
                if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) \
                        and not isinstance(n.value, ast.Constant):
                    v = self.giai(n.value)
                    if v is not None:
                        self.bien[n.targets[0].id] = v

    def giai(self, n):
        if isinstance(n, ast.Name):
            return self.bien.get(n.id)
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            return n.value
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div):
            a, b = self.giai(n.left), self.giai(n.right)
            if a is not None and b is not None and isinstance(n.right, ast.Constant):
                return f"{a}/{b}".strip("/")
        if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "joinpath":
            a = self.giai(n.func.value)
            for x in n.args:
                b = self.giai(x)
                a = None if a is None or b is None else f"{a}/{b}".strip("/")
            return a
        return None

    def tat_ca(self):
        ra = set(self.bien.values())
        for n in ast.walk(self.cay):
            if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div):
                ra.add(self.giai(n))
            elif isinstance(n, ast.Constant) and isinstance(n.value, str):
                s = n.value.strip()
                if re.fullmatch(r"[\w.\-]+(/[\w.\-]+)+/?", s) and not s.startswith(("http", "/")):
                    ra.add(s.rstrip("/"))
        goc_co = {x.name for x in GOC.iterdir()}
        return {d for d in ra if d and d.split("/")[0] in goc_co and not d.startswith(CHI_DOC)}

    def doi_sua(self):
        """{đường: chuỗi test đòi có} cho file đọc bằng read_text rồi assert "x" in ..."""
        ra = {}
        for fn in ast.walk(self.cay):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            doc = [self.giai(c.func.value) for c in ast.walk(fn)
                   if isinstance(c, ast.Call) and getattr(c.func, "attr", "") == "read_text"]
            chuoi = {n.left.value for n in ast.walk(fn) if isinstance(n, ast.Compare) and isinstance(n.left, ast.Constant)
                     and isinstance(n.left.value, str) and any(isinstance(o, ast.In) for o in n.ops)}
            for d in doc:
                if d and chuoi:
                    ra.setdefault(d, set()).update(chuoi)
        return ra


def tieu_chi_trong_test(p):
    cay = ast.parse(p.read_text(encoding="utf-8"))
    ra = []
    for n in ast.walk(cay):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test"):
            ds = ast.get_docstring(n) or ""
            ra += [chuan(m) for m in re.findall(r"Tiêu chí:\s*(.+)", ds)]
    return ra


def tat_ca_features(file_chinh):
    ds = {}
    for ff in sorted(GOC.glob("features-dot*.json")) + [file_chinh]:
        for f in json.loads(ff.read_text(encoding="utf-8"))["features"]:
            ds[f["id"]] = f
    return ds


def bac_cau(ds, fid, da=None):
    da = set() if da is None else da
    for x in ds.get(fid, {}).get("phu_thuoc", []) or []:
        if x not in da:
            da.add(x)
            bac_cau(ds, x, da)
    return da


def kiem(file_chinh, ca_da_dat=False):
    file_chinh = pathlib.Path(file_chinh).resolve()
    rieng = json.loads(file_chinh.read_text(encoding="utf-8"))["features"]
    ds = tat_ca_features(file_chinh)
    loi, canh_bao = [], []
    for f in rieng:
        fid = f["id"]
        if f.get("passes") and not ca_da_dat:
            continue
        vung = list(f.get("vung") or [])
        if not vung:
            loi.append(f"{fid} VUNG: trống")
        for x in f.get("phu_thuoc") or []:
            if x not in ds:
                loi.append(f"{fid} PHU_THUOC: {x} không có trong features-dot*.json")
        if fid in bac_cau(ds, fid):
            loi.append(f"{fid} PHU_THUOC: vòng phụ thuộc")
        tep = NT / f"test_{fid.lower()}.py"
        if f"test_{fid.lower()}.py" not in (f.get("lenh_kiem") or ""):
            loi.append(f"{fid} LENH_KIEM: không gọi tests/nghiem-thu/test_{fid.lower()}.py")
        if not tep.exists():
            loi.append(f"{fid} TEST: thiếu {tep.relative_to(GOC).as_posix()}")
            continue
        truoc = bac_cau(ds, fid)
        dg = Duong(tep)
        for d in sorted(dg.tat_ca()):
            if any(khop(d, m) for m in vung):
                continue
            chu = [k for k, g in ds.items() if k != fid and not g.get("passes")
                   and any(khop(d, m) for m in g.get("vung") or [])]
            if chu and not any(k in truoc for k in chu) and pathlib.PurePath(d).suffix:
                loi.append(f"{fid} PHU_THUOC: test cần {d}, file do {','.join(chu)} làm (chưa đạt) mà không phụ thuộc")
            elif not (GOC / d).exists() and pathlib.PurePath(d).suffix and not chu:
                loi.append(f"{fid} VUNG: test cần {d} (chưa có) mà vùng {vung} không chứa")
        for d, chuoi in sorted(dg.doi_sua().items()):
            p = GOC / d
            if d.startswith(CHI_DOC) or any(khop(d, m) for m in vung) or not p.is_file():
                continue
            thieu = [c for c in chuoi if c not in p.read_text(encoding="utf-8", errors="ignore")]
            if thieu:
                loi.append(f"{fid} VUNG: test đòi sửa {d} (thiếu {thieu[:3]}) mà file ngoài vùng")
        tc_test = tieu_chi_trong_test(tep)
        for tc in f.get("tieu_chi") or []:
            c = chuan(tc)
            if not any(c == t or c in t or t in c for t in tc_test if t):
                loi.append(f"{fid} TIEU_CHI: không test nào ghi 'Tiêu chí: {tc}'")
    return loi, canh_bao


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if not a:
        print(__doc__)
        sys.exit(2)
    loi, cb = kiem(a[0], "--ca-da-dat" in sys.argv)
    if "--json" in sys.argv:
        print(json.dumps({"loi": loi, "canh_bao": cb}, ensure_ascii=False))
    else:
        for x in loi:
            print("LOI", x)
        for x in cb:
            print("CANH_BAO", x)
        print(f"{len(loi)} lỗi, {len(cb)} cảnh báo")
    sys.exit(1 if loi else 0)
