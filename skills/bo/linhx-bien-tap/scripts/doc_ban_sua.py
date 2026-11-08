#!/usr/bin/env python3
"""doc_ban_sua.py - đọc bản sửa của biên tập viên, ra danh sách từng chỗ sửa (cặp câu trước/sau).

Hai kiểu đầu vào:
  python doc_ban_sua.py docx bai-co-track-changes.docx -o mau-sua/<ten-bai>/
      Word có bật Track Changes: tách ra truoc.md (bản tác giả) và sau.md (bản đã sửa),
      kèm comment của biên tập viên (nếu có) vào ghi-chu-bien-tap.md.
  python doc_ban_sua.py cap truoc.md sau.md -o mau-sua/<ten-bai>/
      Hai file trước/sau sẵn có (md, txt, hoặc docx không track changes).

Cả hai đều ghi thêm cac-cho-sua.json và cac-cho-sua.md: mỗi chỗ sửa gồm câu trước, câu sau,
kiểu sửa đoán bằng máy (cắt, thêm, nối câu, tách câu, thay chữ, viết lại) và các chữ bị bỏ/thêm.
Skill `hoc-tu-ban-sua` đọc file này để rút luật. Chỉ dùng thư viện chuẩn.
"""
import argparse, difflib, json, re, sys, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def doc_docx(path, che_do):
    """che_do: 'truoc' bỏ chữ chèn, giữ chữ xoá; 'sau' ngược lại; 'tho' đọc như bình thường."""
    with zipfile.ZipFile(path) as z:
        goc = ET.fromstring(z.read('word/document.xml'))
        ghi = []
        if 'word/comments.xml' in z.namelist():
            for c in ET.fromstring(z.read('word/comments.xml')).iter(W + 'comment'):
                ghi.append({'tac_gia': c.get(W + 'author', ''),
                            'noi_dung': ''.join(t.text or '' for t in c.iter(W + 't'))})
    doan = []
    for p in goc.iter(W + 'p'):
        # xác định chữ nào nằm trong w:ins
        trong_ins = set()
        for ins in p.iter(W + 'ins'):
            for t in ins.iter(W + 't'):
                trong_ins.add(id(t))
        out = []
        for el in p.iter():
            if el.tag == W + 't':
                if id(el) in trong_ins and che_do == 'truoc':
                    continue
                out.append(el.text or '')
            elif el.tag == W + 'delText':
                if che_do in ('truoc', 'tho'):
                    out.append(el.text or '')
            elif el.tag == W + 'tab':
                out.append('\t')
        doan.append(''.join(out).strip())
    return '\n\n'.join(d for d in doan if d), ghi


def doc_file(path):
    p = Path(path)
    if p.suffix.lower() == '.docx':
        return doc_docx(p, 'tho')[0]
    return p.read_text(encoding='utf-8')


def tach_cau(text):
    cau = []
    for doan in re.split(r'\n\s*\n', text):
        doan = ' '.join(doan.split())
        if not doan or doan.startswith(('|', '---', '#')):
            continue
        cau += [c.strip() for c in re.split(r'(?<=[.!?…])["”»]?\s+(?=[A-ZÀ-Ỹ"“«(\[*])', doan) if c.strip()]
    return cau


DUNG = set('và là của có không những các cho với đã được này ấy đó thì mà một người ta tôi bạn nó cũng như khi lại rồi ra vào'.split())
BUOC = [(1, 1), (2, 1), (3, 1), (4, 1), (1, 2), (1, 3), (2, 2)]


def bo_tu(cau_list):
    return {w for w in re.findall(r'[^\W\d_]+', ' '.join(cau_list).lower()) if w not in DUNG}


def giong(a, b):
    x, y = bo_tu(a), bo_tu(b)
    return len(x & y) / len(x | y) if x and y else 0.0


def can_cau(a, b):
    """Gióng câu bản trước với bản sau bằng quy hoạch động: cho phép cắt, thêm, nối 2–4 câu, tách 2–3 câu."""
    n, m = len(a), len(b)
    INF = float('inf')
    f = [[INF] * (m + 1) for _ in range(n + 1)]
    tu = [[None] * (m + 1) for _ in range(n + 1)]
    f[0][0] = 0
    for i in range(n + 1):
        for j in range(m + 1):
            if f[i][j] == INF:
                continue
            if i < n and f[i][j] + 1 < f[i + 1][j]:
                f[i + 1][j], tu[i + 1][j] = f[i][j] + 1, (i, j)
            if j < m and f[i][j] + 1 < f[i][j + 1]:
                f[i][j + 1], tu[i][j + 1] = f[i][j] + 1, (i, j)
            for k, l in BUOC:
                if i + k <= n and j + l <= m:
                    sim = 1.0 if a[i:i + k] == b[j:j + l] else giong(a[i:i + k], b[j:j + l])
                    if sim < 0.15:
                        continue
                    c = f[i][j] + (k + l) * (1 - sim) / 0.7
                    if c < f[i + k][j + l]:
                        f[i + k][j + l], tu[i + k][j + l] = c, (i, j)
    cap, i, j = [], n, m
    while (i, j) != (0, 0):
        pi, pj = tu[i][j]
        cap.append((pi, i, pj, j))
        i, j = pi, pj
    return cap[::-1]


def kieu_sua(truoc, sau):
    if not truoc:
        return 'thêm'
    if not sau:
        return 'cắt'
    if len(truoc) > 1 and len(sau) == 1:
        return 'nối câu'
    if len(truoc) == 1 and len(sau) > 1:
        return 'tách câu'
    tt, ts = ' '.join(truoc).split(), ' '.join(sau).split()
    return 'thay chữ' if difflib.SequenceMatcher(None, tt, ts).ratio() > 0.6 else 'viết lại'


def doi_chieu(truoc_txt, sau_txt):
    a, b = tach_cau(truoc_txt), tach_cau(sau_txt)
    kq = []
    cap = []
    for i1, i2, j1, j2 in can_cau(a, b):
        # gộp các câu bị cắt liền nhau thành một chỗ sửa
        if cap and j1 == j2 and cap[-1][2] == cap[-1][3] and cap[-1][1] == i1:
            cap[-1] = (cap[-1][0], i2, j1, j2)
        else:
            cap.append((i1, i2, j1, j2))
    for i1, i2, j1, j2 in cap:
        t, s = a[i1:i2], b[j1:j2]
        if t == s:
            continue
        tt, ts = ' '.join(t).split(), ' '.join(s).split()
        bo, them = [], []
        for o, x1, x2, y1, y2 in difflib.SequenceMatcher(None, tt, ts, autojunk=False).get_opcodes():
            if o in ('delete', 'replace'):
                bo.append(' '.join(tt[x1:x2]))
            if o in ('insert', 'replace'):
                them.append(' '.join(ts[y1:y2]))
        kq.append({'stt': len(kq) + 1, 'vi_tri_truoc': f'câu {i1+1}–{i2}' if t else f'sau câu {i1}',
                   'kieu': kieu_sua(t, s), 'truoc': ' '.join(t), 'sau': ' '.join(s),
                   'chu_bo': bo, 'chu_them': them,
                   'tu_truoc': len(tt), 'tu_sau': len(ts)})
    thong_ke = {'cau_truoc': len(a), 'cau_sau': len(b),
                'tu_truoc': len(' '.join(a).split()), 'tu_sau': len(' '.join(b).split()),
                'so_cho_sua': len(kq)}
    for k in ('cắt', 'thêm', 'nối câu', 'tách câu', 'thay chữ', 'viết lại'):
        thong_ke[k] = sum(x['kieu'] == k for x in kq)
    return kq, thong_ke


def ghi(out, kq, tk, ten):
    out.mkdir(parents=True, exist_ok=True)
    (out / 'cac-cho-sua.json').write_text(json.dumps({'thong_ke': tk, 'cho_sua': kq}, ensure_ascii=False, indent=1), encoding='utf-8')
    dong = [f'# Các chỗ sửa: {ten}', '',
            f"{tk['cau_truoc']} câu → {tk['cau_sau']} câu · {tk['tu_truoc']} → {tk['tu_sau']} từ · {tk['so_cho_sua']} chỗ sửa "
            f"(cắt {tk['cắt']}, thêm {tk['thêm']}, nối câu {tk['nối câu']}, tách câu {tk['tách câu']}, thay chữ {tk['thay chữ']}, viết lại {tk['viết lại']})", '']
    for x in kq:
        dong += [f"## {x['stt']}. {x['kieu']} ({x['vi_tri_truoc']})", '',
                 f"- Trước: {x['truoc'] or '(không có)'}", f"- Sau: {x['sau'] or '(cắt)'}"]
        if x['kieu'] == 'thay chữ':
            dong.append(f"- Bỏ: {' | '.join(x['chu_bo']) or '-'} · Thêm: {' | '.join(x['chu_them']) or '-'}")
        dong.append('')
    (out / 'cac-cho-sua.md').write_text('\n'.join(dong), encoding='utf-8')


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='lenh', required=True)
    d = sub.add_parser('docx'); d.add_argument('file'); d.add_argument('-o', required=True)
    c = sub.add_parser('cap'); c.add_argument('truoc'); c.add_argument('sau'); c.add_argument('-o', required=True)
    a = ap.parse_args()
    out = Path(a.o)
    if a.lenh == 'docx':
        truoc, ghi_chu = doc_docx(a.file, 'truoc')
        sau, _ = doc_docx(a.file, 'sau')
        if truoc == sau:
            print('Cảnh báo: file không có Track Changes (bản trước và sau giống nhau). Dùng lệnh "cap" với hai file.', file=sys.stderr)
        out.mkdir(parents=True, exist_ok=True)
        (out / 'truoc.md').write_text(truoc + '\n', encoding='utf-8')
        (out / 'sau.md').write_text(sau + '\n', encoding='utf-8')
        if ghi_chu:
            (out / 'ghi-chu-bien-tap.md').write_text('\n'.join(f"- {g['tac_gia']}: {g['noi_dung']}" for g in ghi_chu) + '\n', encoding='utf-8')
        ten = Path(a.file).name
    else:
        truoc, sau = doc_file(a.truoc), doc_file(a.sau)
        ten = f'{Path(a.truoc).name} → {Path(a.sau).name}'
    kq, tk = doi_chieu(truoc, sau)
    ghi(out, kq, tk, ten)
    print(f"{ten}: {tk['so_cho_sua']} chỗ sửa, {tk['tu_truoc']} → {tk['tu_sau']} từ. Ghi ở {out}/cac-cho-sua.md")


if __name__ == '__main__':
    main()
