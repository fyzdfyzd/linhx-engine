#!/usr/bin/env python3
"""Kiểm nháp gạch đầu dòng của tác giả và bài máy làm mượt từ nháp ấy (luồng Vân Anh, v0.3).

  python kiem_nhap.py nhap nhap.md
      Nháp đủ ý chưa: mỗi mục (## Ý ...) có bao nhiêu gạch, mục nào mỏng (dưới 2 gạch) để máy hỏi lại tác giả.
      Không đòi số chữ (Linh 19/10: gạch đầu dòng đủ lượng và hàm ý là được).
  python kiem_nhap.py bai nhap.md bai.md [--kho kho.md] [-o bao-cao.md]
      Mỗi gạch đầu dòng của tác giả nằm ở đoạn nào; gạch nào bị rơi;
      đoạn nào máy tự thêm (không khớp gạch nào); số nào trong bài không có trong nháp hay kho.
Chỉ dùng thư viện chuẩn.
"""
import argparse, re, sys
from pathlib import Path

DUNG = set('và là của có cho một những các được thì mà này ấy đó với trong khi đã sẽ đang không người cũng như để từ ra vào lại rồi nên vì nhưng còn bị theo đến hay thế nào gì ai tôi anh chị em nó họ mình ta rằng'.split())


def tu_noi_dung(s):
    s = re.sub(r'\[[^\]]*\]', ' ', s.lower())
    tu = re.findall(r'\w+', s)
    return {f'{a} {b}' for a, b in zip(tu, tu[1:]) if a not in DUNG or b not in DUNG} | {t for t in tu if t not in DUNG and len(t) > 2}


def doc_gach(nhap):
    gach, cha = [], None
    for dong in Path(nhap).read_text(encoding='utf-8').splitlines():
        m = re.match(r'^(\s*)[-*+•]\s+(.*)', dong)
        if m and m.group(2).strip():
            gach.append({'so': len(gach) + 1, 'cap': len(m.group(1)) // 2, 'chu': m.group(2).strip()})
    return gach


def doc_doan(bai):
    doan = []
    for k in re.split(r'\n\s*\n', Path(bai).read_text(encoding='utf-8')):
        k = k.strip()
        if not k or k.startswith(('#', '|', '*Nguồn', '---', '**')) or (k.startswith('*') and k.endswith('*')):
            continue
        doan.append(re.sub(r'^>\s*', '', k))
    return doan


def so_trong(s):
    return set(re.findall(r'\d[\d.,]*%?', re.sub(r'\[[^\]]*\]', '', s)))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='lenh', required=True)
    a1 = sub.add_parser('nhap'); a1.add_argument('nhap')
    a2 = sub.add_parser('bai'); a2.add_argument('nhap'); a2.add_argument('bai'); a2.add_argument('--kho'); a2.add_argument('-o')
    a = ap.parse_args()

    if a.lenh == 'nhap':
        muc, ten = {}, 'Không mục'
        for dong in Path(a.nhap).read_text(encoding='utf-8').splitlines():
            if dong.startswith('## '):
                ten = dong[3:].strip(); muc.setdefault(ten, 0)
            elif re.match(r'^\s*[-*+•]\s+\S', dong):
                muc[ten] = muc.get(ten, 0) + 1
        mong = [t for t, n in muc.items() if n < 2 and not t.lower().startswith(('kết', 'mở'))]
        print(f"{sum(muc.values())} gạch, {len(muc)} mục: " + '; '.join(f'{t} ({n})' for t, n in muc.items()))
        print(f"Mục mỏng, hỏi lại tác giả: {', '.join(mong)}" if mong else 'Đủ để làm mượt.')
        return

    gach, doan = doc_gach(a.nhap), doc_doan(a.bai)
    tg = [tu_noi_dung(g['chu']) for g in gach]
    td = [tu_noi_dung(d) for d in doan]
    gan, roi = {}, []
    for g, t in zip(gach, tg):
        diem = [len(t & d) / (len(t) or 1) for d in td]
        tot = max(range(len(doan)), key=lambda i: diem[i]) if doan else None
        if tot is None or diem[tot] < 0.25:
            roi.append(g)
        else:
            gan.setdefault(tot, []).append((g['so'], round(diem[tot], 2)))
    them = [i for i in range(len(doan)) if i not in gan]
    nguon = ' '.join(g['chu'] for g in gach) + (Path(a.kho).read_text(encoding='utf-8') if a.kho else '')
    so_la = sorted(so_trong(' '.join(doan)) - so_trong(nguon))

    ra = [f'# Kiểm bài theo nháp: {Path(a.bai).name}', '',
          f'{len(gach)} gạch nháp, {len(doan)} đoạn. Gạch bị rơi: {len(roi)}. Đoạn máy tự thêm: {len(them)}. Số không có nguồn: {len(so_la)}.', '',
          '| Đoạn | Gạch nháp (độ khớp) | Đầu đoạn |', '|---|---|---|']
    for i, d in enumerate(doan):
        g = ', '.join(f'{s} ({k})' for s, k in gan.get(i, [])) or '**MÁY THÊM**'
        ra.append(f'| Đ{i+1} | {g} | {d[:70]} |')
    if roi:
        ra += ['', '## Gạch của tác giả không thấy trong bài'] + [f"- {g['so']}. {g['chu']}" for g in roi]
    if so_la:
        ra += ['', '## Số trong bài không có trong nháp hay kho', ', '.join(so_la)]
    dat = not roi and not so_la and len(them) <= max(1, len(doan) // 10)
    ra += ['', f"**{'ĐẠT' if dat else 'TRƯỢT'}**: bài chỉ được làm mượt ý của tác giả; đoạn tự thêm tối đa một phần mười, không số lạ, không rơi gạch."]
    txt = '\n'.join(ra)
    if a.o:
        Path(a.o).write_text(txt + '\n', encoding='utf-8')
    print(txt)
    sys.exit(0 if dat else 1)


if __name__ == '__main__':
    try:
        main()
    except BrokenPipeError:
        pass
