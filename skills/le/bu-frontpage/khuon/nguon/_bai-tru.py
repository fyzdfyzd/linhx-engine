"""Chuyển bài trụ own-media/*.md thành nguon/20-cong-nghe-su-kien.json. Chạy trước tao-trang.py."""
import json, re, pathlib
D = pathlib.Path(__file__).parent
src = (D / "../../own-media/bai-tru-cong-nghe-su-kien.md").read_text(encoding="utf-8")
fm = dict(re.findall(r'^(\w+):\s*"?(.*?)"?\s*$', src.split("---")[1], re.M))
body = re.sub(r"<!--.*?-->", "", src.split("---", 2)[2], flags=re.S)
body = re.sub(r"^# .*\n", "", body.strip(), count=1)
mo, rest = body.split("\n\n", 1)
faq_txt = re.search(r"## Câu hỏi hay gặp\n(.*?)(?=\n## |\Z)", rest, re.S).group(1)
faq = [[q.strip(), a.strip()] for q, a in re.findall(r"\*\*(.+?)\*\*\n(.+?)(?=\n\n|\Z)", faq_txt, re.S)]
rest = re.sub(r"## Câu hỏi hay gặp\n.*", "", rest, flags=re.S)  # FAQ + CTA cuối do khuôn dựng
rest = rest.replace("- [ ] ", "- ").replace("https://event.ifagent.net/", "/")
t = dict(path="/cong-nghe-su-kien/", kenh="bai-tru", loai="article", ngay="2026-11-10",
         title=fm["title"], desc=fm["meta_description"],
         vet=[("Cẩm nang", "/cam-nang/"), ("Công nghệ sự kiện", "/cong-nghe-su-kien/")],
         h1="Công nghệ sự kiện: chọn giải pháp tương tác AI cho gian hàng, activation và hội nghị",
         mo=mo.strip(), than=rest.strip(), hoi_dap=faq)
(D / "20-cong-nghe-su-kien.json").write_text(json.dumps(t, ensure_ascii=False, indent=1), encoding="utf-8")
print("FAQ", len(faq), "| desc", len(t["desc"]), "| title", len(t["title"]))
