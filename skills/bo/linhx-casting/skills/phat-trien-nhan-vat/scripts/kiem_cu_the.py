# Kiểm luật "không chung chung" cho spec nhân vật.
# python kiem_cu_the.py <thu-muc-spec | file.json>  -> in lỗi, mã thoát 1 nếu còn lỗi
# Mỗi mục (dict có khoá "ten") phải có: số đo/mã (hex, số + đơn vị, AU), tham chiếu ("ref" không rỗng), lý do ("vi_sao").
import json, re, sys, pathlib
MO_HO = ["thanh lịch","hiện đại","trẻ trung","sang trọng","cá tính","nhẹ nhàng","tinh tế","đẹp","phù hợp","nổi bật","ấn tượng","đơn giản","basic","hài hoà"]
SO = re.compile(r"#[0-9A-Fa-f]{6}|\b\d+(?:[.,]\d+)?\s?(?:cm|mm|gsm|%|°|kg|m)\b|\bAU\d+|\b\d{2}-\d{4}\s?TCX\b")
def muc(o, path=""):
    if isinstance(o, dict):
        if "ten" in o: yield path, o
        for k, v in o.items(): yield from muc(v, f"{path}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from muc(v, f"{path}[{i}]")
def kiem(o):
    loi = []
    for p, m in muc(o):
        chu = json.dumps({k: v for k, v in m.items() if k not in ("ref",)}, ensure_ascii=False)
        if not SO.search(chu): loi.append((p, m["ten"], "thiếu số đo/mã (hex, cm, %, AU...)"))
        ref = m.get("ref")
        if not ref or (isinstance(ref, list) and not any(str(r).strip() for r in ref)): loi.append((p, m["ten"], "thiếu tham chiếu cụ thể"))
        if not str(m.get("vi_sao", "")).strip(): loi.append((p, m["ten"], "thiếu lý do gắn brief/persona"))
        for t in MO_HO:
            if re.search(rf"(?<!\w){re.escape(t)}(?!\w)", chu.lower()) and not SO.search(chu):
                loi.append((p, m["ten"], f"từ mơ hồ '{t}' không kèm số/mã"))
    return loi
if __name__ == "__main__":
    a = pathlib.Path(sys.argv[1]); fs = sorted(a.glob("*.json")) if a.is_dir() else [a]
    tong, sai = 0, 0
    for f in fs:
        o = json.load(open(f, encoding="utf-8")); n = sum(1 for _ in muc(o)); l = kiem(o)
        tong += n; sai += len({x[0] for x in l})
        for p, t, why in l: print(f"{f.name}{p} [{t}]: {why}")
    print(f"{tong} mục, {sai} mục lỗi, đạt {100*(tong-sai)/max(tong,1):.0f}%")
    sys.exit(1 if sai else 0)
