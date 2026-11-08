#!/usr/bin/env python3
"""ve_anh.py: vẽ ảnh minh hoạ của brand bằng OpenAI Images API theo phiếu 04-hinh-anh/PROMPT-CHATGPT.md.

Dùng:  python ve_anh.py <brand-dir> [<brand-dir> ...] [--chi-xem] [--ve-lai] [--model gpt-image-1] [--chat-luong high]
Cần:   biến môi trường OPENAI_API_KEY (tính tiền API riêng, không dùng gói ChatGPT Plus).

Mỗi mục "## N." trong phiếu: tên file đích là chữ `gpt-*.png` đầu tiên, prompt là khối ``` đầu tiên,
tỉ lệ đọc từ "Aspect ratio X:Y" (16:9 và 3:1 ra ảnh ngang 1536x1024, 4:5 và 9:16 ra ảnh dọc 1024x1536, còn lại 1024x1024).
Ảnh lưu vào 04-hinh-anh/<file đích>, kèm <file>.txt ghi prompt và model để vẽ lại được. File đã có thì bỏ qua (trừ --ve-lai).
"""
import argparse, base64, json, os, re, sys, urllib.request
from pathlib import Path

API = "https://api.openai.com/v1/images/generations"

def doc_phieu(p):
    t = p.read_text("utf8"); muc = []
    for khoi in re.split(r"\n(?=## \d)", t)[1:]:
        f = re.search(r"`(gpt-[\w.-]+\.png)`", khoi); c = re.search(r"```\w*\n(.*?)```", khoi, re.S)
        if not (f and c):
            continue
        pr = c.group(1).strip(); r = re.search(r"[Aa]spect ratio (\d+):(\d+)", pr) or re.search(r"(\d+):(\d+)", khoi)
        w, h = (int(r.group(1)), int(r.group(2))) if r else (1, 1)
        co = "1536x1024" if w > h else "1024x1536" if h > w else "1024x1024"
        muc.append({"file": f.group(1), "prompt": pr, "co": co})
    return muc

def ve(prompt, co, model, chat_luong, key):
    body = json.dumps({"model": model, "prompt": prompt, "size": co, "quality": chat_luong, "n": 1}).encode()
    rq = urllib.request.Request(API, body, {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(rq, timeout=300) as r:
        d = json.load(r)["data"][0]
    if d.get("b64_json"):
        return base64.b64decode(d["b64_json"])
    with urllib.request.urlopen(d["url"], timeout=120) as r:
        return r.read()

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("brand_dir", nargs="+"); p.add_argument("--chi-xem", action="store_true", help="chỉ liệt kê, không gọi API")
    p.add_argument("--ve-lai", action="store_true"); p.add_argument("--model", default="gpt-image-1")
    p.add_argument("--chat-luong", default="high", choices=["low", "medium", "high"])
    a = p.parse_args(); key = os.environ.get("OPENAI_API_KEY")
    if not a.chi_xem and not key:
        sys.exit("Chưa có OPENAI_API_KEY. Đặt biến môi trường rồi chạy lại (hoặc thêm --chi-xem để xem danh sách).")
    for d in map(Path, a.brand_dir):
        thu_muc = d / "04-hinh-anh"; phieu = thu_muc / "PROMPT-CHATGPT.md"
        if not phieu.exists():
            print(f"[{d.name}] không có {phieu}"); continue
        for m in doc_phieu(phieu):
            ra = thu_muc / m["file"]
            if ra.exists() and not a.ve_lai:
                print(f"[{d.name}] bỏ qua {m['file']} (đã có)"); continue
            print(f"[{d.name}] {m['file']}  {m['co']}")
            if a.chi_xem:
                continue
            try:
                ra.write_bytes(ve(m["prompt"], m["co"], a.model, a.chat_luong, key))
                ra.with_suffix(".txt").write_text(f"model: {a.model}\nsize: {m['co']}\n\n{m['prompt']}\n", encoding="utf8")
            except Exception as e:
                print(f"   lỗi: {e}")

if __name__ == "__main__":
    main()
