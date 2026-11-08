# Tách hai file bộ thẻ trong LAB030/output thành từng file thẻ trong the/.
# Chạy lại sau khi sửa BO-MENTAL-MODEL-*.md:  python tach-the.py
import re, sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "the"); os.makedirs(out, exist_ok=True)
LAB = os.path.join(HERE, "..", "..", "..", "output")
SRC = [("naval", os.path.join(LAB, "BO-MENTAL-MODEL-NAVAL.md")),
       ("munger-fs", os.path.join(LAB, "BO-MENTAL-MODEL-MUNGER-FS.md"))]
NHOM = {"A":"lam-giau","B":"quyet-dinh","C":"tu-duy-nen","D":"ban-than","E":"quan-he","G":"cong-nghe-ai"}
MNHOM = {1:"tu-duy-nen",2:"tu-duy-nen",3:"tu-duy-nen",4:"tu-duy-nen",5:"quyet-dinh",6:"quyet-dinh",7:"quyet-dinh",8:"quyet-dinh",
         9:"con-nguoi",10:"con-nguoi",11:"con-nguoi",12:"con-nguoi",13:"he-thong",14:"he-thong",15:"he-thong",16:"thuc-hanh"}
index=[]
for bo, path in SRC:
    txt=open(path,encoding="utf-8").read()
    parts=re.split(r"^### ", txt, flags=re.M)[1:]
    for p in parts:
        head, body = p.split("\n",1)
        m=re.match(r"([A-Z]\d+)\. (.+)", head.strip())
        if not m: continue
        ma, ten = m.groups()
        body = re.split(r"^(---|## )", body, flags=re.M)[0].strip()
        kh = re.search(r"\*\*Câu hỏi kích hoạt:\*\* (.+)", body)
        nhom = MNHOM[int(ma[1:])] if bo=="munger-fs" else NHOM[ma[0]]
        fm = {"ma":ma,"ten":ten,"bo":bo,"nhom":nhom,"cau_kich_hoat":kh.group(1).strip() if kh else ""}
        slug = ma.lower()
        with open(f"{out}/{slug}.md","w",encoding="utf-8") as f:
            f.write("---\n"+"".join(f"{k}: {json.dumps(v,ensure_ascii=False)}\n" for k,v in fm.items())+"---\n")
            f.write(f"# {ma}. {ten}\n\n{body}\n")
        index.append(fm)
json.dump(index, open(f"{out}/_index.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(index), "cards")
