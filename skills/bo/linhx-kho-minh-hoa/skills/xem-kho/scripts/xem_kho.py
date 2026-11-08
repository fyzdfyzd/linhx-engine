"""M7 xem-kho: sinh một trang HTML tĩnh để lướt kho, lọc theo họ phong cách × cơ chế ý tưởng.

  python xem_kho.py                 # đọc KHO/phong-cach/*/phong-cach.json + KHO/anh/the-anh.jsonl -> KHO/xem/index.html
  python xem_kho.py --the <thư mục json> --ra <file.html>   # dựng từ thư mục thẻ bất kỳ (vd mau-the)

Ảnh hiện trên trang là ảnh tự sinh trong mau/. Ảnh gốc của hoạ sĩ chỉ là link.
"""
import argparse, html, json, os
from pathlib import Path

KHO = Path(os.environ.get("KHO_MINH_HOA", r"D:\LINHX\KHO-MINH-HOA"))
TU_DIEN = Path(__file__).resolve().parents[3] / "schemas" / "tu-dien-y-tuong.json"


def doc_the(thu_muc):
    the = []
    for p in sorted(Path(thu_muc).glob("**/*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if "cong_thuc" in d:
            mau = sorted((p.parent / "mau").glob("*.png")) if (p.parent / "mau").exists() else []
            d["_mau"] = [os.path.relpath(m, KHO / "xem") for m in mau]
            the.append(d)
    return the


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--the"); ap.add_argument("--ra"); a = ap.parse_args()
    td = json.loads(TU_DIEN.read_text(encoding="utf-8"))
    ten_ho = {h["id"]: h["ten"] for h in td["ho_phong_cach"]}
    ten_cc = {c["id"]: c["ten"] for c in td["co_che_y_tuong"]}
    the = doc_the(a.the or KHO / "phong-cach")
    anh = KHO / "anh" / "the-anh.jsonl"
    so_anh = {}
    if anh.exists():
        for l in anh.read_text(encoding="utf-8").splitlines():
            if l.strip():
                for h in json.loads(l).get("ho_phong_cach", []):
                    so_anh[h] = so_anh.get(h, 0) + 1
    e = html.escape
    cards = []
    for t in the:
        cc = t.get("co_che_hop", [])
        mau = "".join(f'<img src="{e(m)}" alt="ảnh mẫu tự sinh" loading="lazy">' for m in t["_mau"]) or '<div class="trong">chưa có ảnh mẫu tự sinh</div>'
        ns = "".join(f'<li><a href="{e(n["link"])}" target="_blank" rel="noopener">{e(n["ten"])}</a></li>' if n.get("link") else f'<li>{e(n["ten"])}</li>' for n in t.get("nghe_si_tieu_bieu", []))
        cards.append(f'''<article class="the" data-ho="{e(t["ho"])}" data-cc="{e(" ".join(cc))}">
<div class="mau">{mau}</div>
<p class="ho">{e(ten_ho.get(t["ho"], t["ho"]))} · {so_anh.get(t["ho"], 0)} hình tham khảo</p>
<h2>{e(t["ten"])}</h2><p class="en">{e(t.get("ten_en", ""))}</p>
<p>{e(t["dinh_nghia"])}</p>
<ul class="dh">{"".join(f"<li>{e(x)}</li>" for x in t["dau_hieu"])}</ul>
<p class="cc">{" ".join(f'<span>{e(ten_cc.get(c, c))}</span>' for c in cc)}</p>
<p><b>Dùng khi:</b> {e(t.get("khi_nao_dung", ""))}<br><b>Tránh khi:</b> {e(t.get("khi_nao_tranh", ""))}</p>
<details><summary>Công thức</summary><pre>{e(t["cong_thuc"]["prompt"])}</pre><p class="neg">Tránh: {e(t["cong_thuc"].get("negative", ""))}</p>
<button onclick="navigator.clipboard.writeText(this.previousElementSibling.previousElementSibling.textContent)">Chép công thức</button></details>
<details><summary>Nghệ sĩ tiêu biểu (chỉ để tra cứu)</summary><ul>{ns}</ul></details>
</article>''')
    nut_ho = "".join(f'<button data-loc="ho" data-v="{e(k)}">{e(v)}</button>' for k, v in ten_ho.items())
    nut_cc = "".join(f'<button data-loc="cc" data-v="{e(k)}">{e(v)}</button>' for k, v in ten_cc.items())
    trang = f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kho minh hoạ ý tưởng</title><style>
:root{{--nen:#f7f5f0;--chu:#1d1d1f;--phu:#6b6b6b;--vien:#ddd8cc;--nhan:#c8553d;--the:#fff}}
@media (prefers-color-scheme:dark){{:root{{--nen:#161616;--chu:#eee;--phu:#a0a0a0;--vien:#333;--nhan:#e07a5f;--the:#202020}}}}
body{{margin:0;background:var(--nen);color:var(--chu);font:15px/1.5 system-ui,sans-serif;padding:24px 16px}}
h1{{font-size:28px;margin:0 0 4px}} .sub{{color:var(--phu);margin:0 0 16px}}
.loc{{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0}} .loc b{{width:100%;font-size:13px;color:var(--phu)}}
.loc button{{border:1px solid var(--vien);background:var(--the);color:var(--chu);border-radius:99px;padding:4px 10px;cursor:pointer;font:inherit;font-size:13px}}
.loc button.on{{background:var(--nhan);border-color:var(--nhan);color:#fff}}
.luoi{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px;margin-top:16px}}
.the{{background:var(--the);border:1px solid var(--vien);border-radius:12px;padding:16px}} .the h2{{margin:4px 0 0;font-size:19px}}
.mau{{display:grid;grid-template-columns:repeat(3,1fr);gap:4px}} .mau img{{width:100%;aspect-ratio:1;object-fit:cover;border-radius:6px}}
.trong{{grid-column:1/-1;aspect-ratio:3/1;display:grid;place-items:center;border:1px dashed var(--vien);border-radius:6px;color:var(--phu);font-size:13px}}
.ho,.en,.neg{{color:var(--phu);font-size:13px;margin:4px 0}} .dh{{padding-left:18px;font-size:14px}}
.cc span{{display:inline-block;background:var(--nen);border-radius:4px;padding:1px 6px;margin:2px;font-size:12px}}
pre{{white-space:pre-wrap;background:var(--nen);padding:8px;border-radius:6px;font-size:13px}} .an{{display:none}}
</style></head><body><h1>Kho minh hoạ ý tưởng</h1><p class="sub">{len(the)} phong cách · ảnh trên trang là ảnh tự sinh, ảnh gốc chỉ có link</p>
<div class="loc"><b>Họ phong cách</b>{nut_ho}</div><div class="loc"><b>Cơ chế ý tưởng</b>{nut_cc}</div>
<div class="luoi">{"".join(cards)}</div>
<script>
const chon={{ho:null,cc:null}};
document.querySelectorAll('.loc button').forEach(b=>b.onclick=()=>{{const k=b.dataset.loc;chon[k]=chon[k]===b.dataset.v?null:b.dataset.v;
document.querySelectorAll(`.loc button[data-loc=${{k}}]`).forEach(x=>x.classList.toggle('on',x.dataset.v===chon[k]));
document.querySelectorAll('.the').forEach(t=>{{const ok=(!chon.ho||t.dataset.ho===chon.ho)&&(!chon.cc||t.dataset.cc.split(' ').includes(chon.cc));t.classList.toggle('an',!ok)}})}});
</script></body></html>'''
    ra = Path(a.ra) if a.ra else KHO / "xem" / "index.html"
    ra.parent.mkdir(parents=True, exist_ok=True)
    ra.write_text(trang, encoding="utf-8")
    print(f"Đã dựng {ra} với {len(the)} phong cách.")


if __name__ == "__main__":
    main()
