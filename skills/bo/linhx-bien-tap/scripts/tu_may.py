#!/usr/bin/env python3
"""Danh sách chữ máy tiếng Việt theo tỉ lệ tần suất (cách của Kobak 2024), so bài người với bài máy CÙNG ĐỀ.

  python tu_may.py <thu-muc-bai-nguoi> <thu-muc-bai-may> [--top 30] [--json ra.json]

Chỉ giữ n-gram (1–3 chữ) xuất hiện >= 4 lần ở >= 3 bài máy. Tỉ lệ = tần suất máy / tần suất người (làm trơn 0,5).
Phải là cùng đề, nếu không danh sách sẽ toàn chữ của đề.
"""
import argparse, collections, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from cham_cau import doc_doan, tach_cau, MA  # noqa: E402


def cau(f):
    t = Path(f).read_text(encoding='utf-8')
    return [re.findall(r'[\wÀ-ỹ]+', MA.sub('', c).lower()) for d in doc_doan(t) for c in tach_cau(d)]


def dem(fs, n):
    out = []
    for f in fs:
        g = collections.Counter()
        for w in cau(f):
            g.update(' '.join(w[i:i + n]) for i in range(len(w) - n + 1))
        out.append(g)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('nguoi'); ap.add_argument('may'); ap.add_argument('--top', type=int, default=30); ap.add_argument('--json')
    a = ap.parse_args()
    H, M = sorted(Path(a.nguoi).glob('*.md')), sorted(Path(a.may).glob('*.md'))
    ra = {}
    for n in (1, 2, 3):
        dh, dm = dem(H, n), dem(M, n)
        th, tm = sum(dh, collections.Counter()), sum(dm, collections.Counter())
        ch, cm = sum(th.values()), sum(tm.values())
        hang = []
        for g, c in tm.items():
            so_bai = sum(g in x for x in dm)
            if c < 4 or so_bai < 3:
                continue
            hang.append((round(((c + .5) / cm) / ((th[g] + .5) / ch), 1), g, c, so_bai, th[g]))
        hang.sort(reverse=True)
        ra[f'{n}-gram'] = hang[:a.top]
        print(f'\n## {n}-gram (máy {cm} / người {ch})')
        for r, g, c, s, h in hang[:a.top]:
            print(f'{r:6.1f}  {g:30} máy={c} ({s} bài)  người={h}')
    if a.json:
        Path(a.json).write_text(json.dumps(ra, ensure_ascii=False, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()
