"""Chuyển bài trụ own-media/bai-tru-*.md thành nguon/9x-*.json. Chạy trước tao-trang.py."""
import json, re, pathlib
D = pathlib.Path(__file__).parent
for i, f in enumerate(sorted((D / "../../own-media").glob("bai-tru-*.md"))):
    src = f.read_text(encoding="utf-8")
    fm = dict(re.findall(r'^(\w+):\s*"?(.*?)"?\s*$', src.split("---")[1], re.M))
    body = re.sub(r"<!--.*?-->", "", src.split("---", 2)[2], flags=re.S)
    body = re.sub(r"^# .*\n", "", body.strip(), count=1)
    mo, rest = body.split("\n\n", 1)
    faq_txt = re.search(r"## Câu hỏi hay gặp\n(.*?)(?=\n## |\Z)", rest, re.S).group(1)
    faq = [[q.strip(), a.strip()] for q, a in re.findall(r"\*\*(.+?)\*\*\n(.+?)(?=\n\n|\Z)", faq_txt, re.S)]
    rest = re.sub(r"## Câu hỏi hay gặp\n.*", "", rest, flags=re.S).replace("https://tuva.work/", "/")
    p = fm["path"]
    vet = [("Cẩm nang", "/cam-nang/"), (fm["h1"].split(":")[0], p)]
    t = dict(path=p, kenh="bai-" + p.strip("/").split("/")[-1], loai="article", ngay="2026-11-10",
             title=fm["title"], desc=fm["meta_description"], vet=vet, h1=fm["h1"], mo=mo.strip(), than=rest.strip(), hoi_dap=faq)
    (D / f"9{i}-{p.strip('/').replace('/', '-')}.json").write_text(json.dumps(t, ensure_ascii=False, indent=1), encoding="utf-8")
    print(p, "FAQ", len(faq), "| desc", len(t["desc"]), "| title", len(t["title"]))
