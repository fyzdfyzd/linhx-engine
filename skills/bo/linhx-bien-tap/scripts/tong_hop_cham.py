#!/usr/bin/env python3
"""tong_hop_cham.py - gộp bảng chấm từng câu của hai giám khảo, so với ngưỡng giao bài.

  python tong_hop_cham.py gk1.md gk2.md [-o tong-hop.md]

Mỗi file giám khảo có bảng `| Mã câu | Nhãn | Lỗi | Câu sửa | Ghi chú |` (references/giam-khao-tung-cau.md).
Ngưỡng (hiệu chuẩn 19/10/2026 trên bài Linh tự sửa): GIỮ ≥ 25% số câu, CẮT = 0, SỬA ≤ 10%,
mỗi đoạn từ hai câu trở lên có ít nhất một câu GIỮ. Câu hai giám khảo lệch nhau từ hai bậc trở lên thì đưa tác giả quyết.
Chỉ dùng thư viện chuẩn.
"""
import argparse, re
from collections import OrderedDict
from pathlib import Path

BAC = {'GIỮ': 0, 'ỔN': 1, 'SỬA': 2, 'CẮT': 3}
NGUONG = {'giu_min': 0.25, 'sua_max': 0.10, 'cat_max': 0}


def doc_bang(path):
    kq = OrderedDict()
    for dong in Path(path).read_text(encoding='utf-8').splitlines():
        o = [c.strip() for c in dong.strip().strip('|').split('|')]
        if len(o) < 2 or not re.match(r'^Đ\d+\.C\d+$', o[0]):
            continue
        nhan = o[1].upper().replace('*', '').strip()
        nhan = next((k for k in BAC if nhan.startswith(k)), None)
        if nhan:
            kq[o[0]] = {'nhan': nhan, 'loi': o[2] if len(o) > 2 else '',
                        'sua': o[3] if len(o) > 3 else '', 'ghi': o[4] if len(o) > 4 else ''}
    return kq


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('gk', nargs=2)
    ap.add_argument('-o')
    a = ap.parse_args()
    g1, g2 = doc_bang(a.gk[0]), doc_bang(a.gk[1])
    ma = list(OrderedDict.fromkeys(list(g1) + list(g2)))
    n = len(ma) or 1
    out = [f'# Tổng hợp chấm từng câu: {len(ma)} câu, hai giám khảo', '']
    out.append('| | GIỮ | ỔN | SỬA | CẮT |\n|---|---|---|---|---|')
    for ten, g in (('Giám khảo 1', g1), ('Giám khảo 2', g2)):
        dem = {k: sum(1 for x in g.values() if x['nhan'] == k) for k in BAC}
        out.append(f"| {ten} | {dem['GIỮ']} ({dem['GIỮ']/n:.0%}) | {dem['ỔN']} | {dem['SỬA']} | {dem['CẮT']} |")
    # nhãn chung: lấy nhãn nặng hơn, trừ khi lệch từ hai bậc (đưa tác giả)
    lech, can_sua, giu = [], [], []
    doan_giu = {}
    for m in ma:
        a1, a2 = g1.get(m), g2.get(m)
        b = [BAC[x['nhan']] for x in (a1, a2) if x]
        doan = m.split('.')[0]
        doan_giu.setdefault(doan, False)
        if 0 in b:
            doan_giu[doan] = True
        if len(b) == 2 and abs(b[0] - b[1]) >= 2:
            lech.append((m, a1, a2))
        elif max(b) >= 2:
            can_sua.append((m, a1, a2))
        if b and max(b) == 0:
            giu.append(m)
    ti_le = lambda k: sum(1 for m in ma if max(BAC[x['nhan']] for x in (g1.get(m), g2.get(m)) if x) == BAC[k]) / n
    truot = []
    tb_giu = (sum(x['nhan'] == 'GIỮ' for x in g1.values()) + sum(x['nhan'] == 'GIỮ' for x in g2.values())) / (2 * n)
    if tb_giu < NGUONG['giu_min']: truot.append(f'GIỮ trung bình {tb_giu:.0%} < 25%')
    so_cat = len([m for m, a1, a2 in can_sua if 'CẮT' in (a1 or {}).get('nhan', '') + (a2 or {}).get('nhan', '')])
    if so_cat > NGUONG['cat_max']: truot.append(f'{so_cat} câu bị chấm CẮT')
    so_sua = len(can_sua) - so_cat
    if so_sua / n > NGUONG['sua_max']: truot.append(f'{so_sua} câu SỬA ({so_sua/n:.0%} > 10%)')
    so_cau_doan = {}
    for m in ma:
        so_cau_doan[m.split('.')[0]] = so_cau_doan.get(m.split('.')[0], 0) + 1
    # đoạn một câu (sapo, câu dẫn bảng) không bắt buộc có câu GIỮ
    thieu = [d for d, ok in doan_giu.items() if not ok and so_cau_doan[d] >= 2]
    if thieu: truot.append(f"đoạn không có câu GIỮ: {', '.join(thieu)}")
    out += ['', f"**Kết luận: {'ĐẠT ngưỡng giao bài' if not truot else 'CHƯA ĐẠT'}**", '']
    out += [f'- {t}' for t in truot]
    out += ['', f'Câu cả hai cùng chấm GIỮ ({len(giu)}): ' + ', '.join(giu), '']
    out += ['## Câu phải sửa hoặc cắt (ít nhất một giám khảo, hai người không lệch quá một bậc)', '',
            '| Câu | GK1 | GK2 | Lỗi | Câu sửa đề xuất |', '|---|---|---|---|---|']
    for m, a1, a2 in can_sua:
        loi = ' / '.join(x['loi'] for x in (a1, a2) if x and x['loi'])
        sua = next((x['sua'] for x in (a1, a2) if x and x['sua']), '')
        out.append(f"| {m} | {(a1 or {}).get('nhan','')} | {(a2 or {}).get('nhan','')} | {loi} | {sua} |")
    out += ['', '## Câu hai giám khảo lệch từ hai bậc trở lên (tác giả quyết)', '',
            '| Câu | GK1 | Ghi chú GK1 | GK2 | Ghi chú GK2 |', '|---|---|---|---|---|']
    for m, a1, a2 in lech:
        out.append(f"| {m} | {a1['nhan']} | {a1['ghi'] or a1['loi']} | {a2['nhan']} | {a2['ghi'] or a2['loi']} |")
    txt = '\n'.join(out) + '\n'
    if a.o:
        Path(a.o).write_text(txt, encoding='utf-8')
    print(txt)


if __name__ == '__main__':
    main()
