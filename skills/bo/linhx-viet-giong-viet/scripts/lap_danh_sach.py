#!/usr/bin/env python3
"""lap_danh_sach.py - lập danh sách cụm "văn dịch / văn máy" bằng tỉ lệ tần suất.

So hai kho văn bản tiếng Việt: kho người (bài thật) và kho LLM (máy viết cùng đề).
Cụm 2-4 âm tiết nào xuất hiện trong văn LLM nhiều hơn hẳn văn người thì đưa vào danh sách.
Cách làm theo Kobak 2024 (excess vocabulary) và Antislop 2025.

  python lap_danh_sach.py <thu-muc-nguoi> <thu-muc-llm> -o danh-sach-hoc.json [--toi-thieu 3] [--ti-le 4]
Chỉ dùng thư viện chuẩn.
"""
import argparse, json, re, sys
from collections import Counter
from pathlib import Path

STOP_LINE = re.compile(r'^(Tác giả|Ngày đăng|URL|---|\(Dân trí\))')

def doc_kho(thu_muc, theo_bai=False):
    chu, bai = [], []
    for p in sorted(Path(thu_muc).glob('*.md')):
        cua_bai = []
        for dong in p.read_text(encoding='utf-8').splitlines():
            if STOP_LINE.match(dong.strip()) or dong.startswith('#') or dong.startswith('|'):
                continue
            cua_bai.extend(re.findall(r"[^\W\d_]+", dong.lower()))
        chu.extend(cua_bai); bai.append(cua_bai)
    return (chu, bai) if theo_bai else chu

def dem(chu, n):
    return Counter(' '.join(chu[i:i+n]) for i in range(len(chu)-n+1))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('nguoi'); ap.add_argument('llm')
    ap.add_argument('-o', '--out', default='danh-sach-hoc.json')
    ap.add_argument('--toi-thieu', type=int, default=3, help='số lần tối thiểu trong kho LLM')
    ap.add_argument('--ti-le', type=float, default=4.0, help='tỉ lệ LLM/người tối thiểu')
    ap.add_argument('--so-bai', type=int, default=3, help='cụm phải có mặt ở ít nhất chừng này bài LLM (lọc từ theo đề tài)')
    a = ap.parse_args()
    cn = doc_kho(a.nguoi)
    cl, bai_llm = doc_kho(a.llm, theo_bai=True)
    if not cn or not cl:
        sys.exit('kho rỗng')
    kq = []
    for n in (2, 3, 4):
        dn, dl = dem(cn, n), dem(cl, n)
        for cum, k in dl.items():
            if k < a.toi_thieu:
                continue
            if sum(1 for b in bai_llm if cum in ' '.join(b)) < a.so_bai:
                continue
            f_llm = k / len(cl) * 1000
            f_ng = (dn.get(cum, 0) + 0.5) / len(cn) * 1000
            r = f_llm / f_ng
            if r >= a.ti_le:
                kq.append({'cum': cum, 'n': n, 'llm_moi_1000': round(f_llm, 3),
                           'nguoi_moi_1000': round(dn.get(cum, 0) / len(cn) * 1000, 3), 'ti_le': round(r, 1)})
    # bỏ cụm con nằm trong cụm dài hơn có cùng tần suất
    kq.sort(key=lambda x: (-x['ti_le'], -x['n']))
    giu = []
    for x in kq:
        if any(x['cum'] in y['cum'] and abs(y['llm_moi_1000'] - x['llm_moi_1000']) < 0.05 for y in giu):
            continue
        giu.append(x)
    Path(a.out).write_text(json.dumps({'chu_nguoi': len(cn), 'chu_llm': len(cl), 'cum': giu}, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'người {len(cn)} chữ, LLM {len(cl)} chữ, {len(giu)} cụm -> {a.out}')
    for x in giu[:40]:
        print(f"{x['ti_le']:>6}x  {x['cum']}")

if __name__ == '__main__':
    main()
