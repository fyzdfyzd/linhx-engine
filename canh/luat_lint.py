#!/usr/bin/env python3
"""Luật lint của người canh: mỗi lỗi thật của thợ thành một luật máy bắt, có cách sửa (quy chuẩn tự chạy mục 9).

  py -3.12 canh/luat_lint.py <worktree> [--goc SHA] [--luat canh/luat-lint.json] [--json]
  py -3.12 canh/luat_lint.py --tu-kiem [--luat canh/luat-lint.json]

--goc SHA  chỉ soi DÒNG THÊM trong goc..HEAD (lỗi mới, không chặn nợ cũ). Bỏ --goc thì soi mọi file git theo dõi.
--tu-kiem  mỗi luật phải bắt được "vi_du_sai" và tha "vi_du_dung"; luật hỏng thì không được dùng.
In ra "file:dòng [ID] tên. Sửa: ..." (hoặc JSON {"loi": [...]}). Mã thoát 1 khi có lỗi, 2 khi gọi sai.
File luật nằm trong canh/** nên thợ không sửa được (rao.py LUON_CAM).
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from rao import git, khop  # noqa: E402

MAC_DINH = pathlib.Path(__file__).parent / "luat-lint.json"


def nap(duong):
    ds = json.loads(pathlib.Path(duong).read_text(encoding="utf-8"))["luat"]
    for l in ds:
        l["_re"] = re.compile(l["cam"])
    return ds


def dong_them(wt, goc):
    """{file: [(số dòng, nội dung)]} của các dòng thêm trong goc..HEAD."""
    ra, f, so = {}, None, 0
    for d in git(wt, "diff", "-U0", "--no-color", f"{goc}..HEAD").splitlines():
        if d.startswith("+++ "):
            f = d[6:] if d.startswith("+++ b/") else None
        elif d.startswith("@@"):
            so = int(re.search(r"\+(\d+)", d).group(1))
        elif f and d.startswith("+"):
            ra.setdefault(f, []).append((so, d[1:]))
            so += 1
    return ra


def moi_dong(wt):
    ra = {}
    for f in git(wt, "ls-files").splitlines():
        try:
            noi = (pathlib.Path(wt) / f).read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        ra[f] = list(enumerate(noi.splitlines(), 1))
    return ra


def soi(cac_dong, luat):
    loi = []
    for f, dong in cac_dong.items():
        for l in luat:
            if not khop(f, l["vung"]) or khop(f, l.get("tru", [])):
                continue
            for so, nd in dong:
                if l["_re"].search(nd):
                    loi.append({"file": f, "dong": so, "id": l["id"], "ten": l["ten"], "sua": l["sua"]})
    return loi


def tu_kiem(luat):
    hong = []
    for l in luat:
        for k in ("vi_du_sai", "vi_du_dung"):
            if isinstance(l[k], list):
                l[k] = "".join(l[k])
        for f in l["vung"]:
            mau = f.replace("**/", "a/").replace("**", "a").replace("*", "x")
            if not khop(mau, l["vung"]):
                continue
            if not soi({mau: [(1, l["vi_du_sai"])]}, [l]):
                hong.append(f"{l['id']}: không bắt được vi_du_sai")
            if soi({mau: [(1, l["vi_du_dung"])]}, [l]):
                hong.append(f"{l['id']}: bắt nhầm vi_du_dung")
            break
        else:
            hong.append(f"{l['id']}: vung không tạo được file mẫu")
    return hong


def main(argv):
    a = list(argv)
    duong_luat = a[a.index("--luat") + 1] if "--luat" in a else MAC_DINH
    luat = nap(duong_luat)
    if "--tu-kiem" in a:
        hong = tu_kiem(luat)
        print("\n".join(hong) if hong else f"tự kiểm đạt {len(luat)} luật")
        return 1 if hong else 0
    if not a or a[0].startswith("--"):
        print(__doc__)
        return 2
    wt = a[0]
    cac_dong = dong_them(wt, a[a.index("--goc") + 1]) if "--goc" in a else moi_dong(wt)
    loi = soi(cac_dong, luat)
    if "--json" in a:
        print(json.dumps({"loi": loi}, ensure_ascii=False))
    else:
        for x in loi:
            print(f"{x['file']}:{x['dong']} [{x['id']}] {x['ten']}. Sửa: {x['sua']}")
        print(f"{len(loi)} lỗi lint" if loi else "lint sạch")
    return 1 if loi else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
