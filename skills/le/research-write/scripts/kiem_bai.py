#!/usr/bin/env python3
"""Máy đo xác định cho bản thảo (0 token). Mảnh "Results Agent" + "Citation Verifier" làm bằng code, không bằng LLM.

  kiem_bai.py so    <ban-thao.md> <nguon-ket-qua>...   số trong bài phải có trong nguồn kết quả (làm tròn theo độ chính xác của bài)
  kiem_bai.py trich <ban-thao.md> <evidence.tsv> [--mang]  mọi [@khoa] phải có trong evidence matrix, có DOI/PMID; --mang thì tra Crossref/PubMed
Mã thoát 1 nếu có lỗi.
"""
import re, sys, csv, json, urllib.request
from decimal import Decimal, ROUND_HALF_UP

SO = re.compile(r'(?<![\w.,])(\d+[.,]\d+|\d+)(\s?%)?(?![\w])')
CAU_CAN_NGUON = re.compile(r'(nghiên cứu (trước|khác)|y văn|đã được chứng minh|previous (stud|work)|has been shown|prior work)', re.I)

def chuan(s):
    return s.replace(',', '.')

def so_trong(text):
    out = []
    for m in SO.finditer(text):
        out.append((m.group(1), bool(m.group(2)), text.count('\n', 0, m.start()) + 1))
    return out

def khop(so_bai, nguon):
    d = Decimal(chuan(so_bai))
    le = len(chuan(so_bai).split('.')[1]) if '.' in chuan(so_bai) else 0
    q = Decimal(1).scaleb(-le)
    for n in nguon:
        for v in (n, n * 100):  # 0.153 trong nguồn = 15,3% trong bài
            if v.quantize(q, rounding=ROUND_HALF_UP) == d:
                return True
    return False

def lenh_so(bai, nguon_files):
    nguon = set()
    for f in nguon_files:
        for s, _, _ in so_trong(open(f, encoding='utf-8').read()):
            nguon.add(Decimal(chuan(s)))
    loi = 0
    for i, dong in enumerate(open(bai, encoding='utf-8'), 1):
        if dong.lstrip().startswith('#'):
            continue
        dong_bo_trich = re.sub(r'\[@[^\]]+\]', '', dong)
        for s, pt, _ in so_trong(dong_bo_trich):
            if '.' not in chuan(s) and not pt:
                continue  # bỏ số nguyên trần (năm, số mục); số thập phân và % mới kiểm
            if not khop(s, nguon):
                loi += 1
                print(f'SO_LA {bai}:{i}: "{s}{"%" if pt else ""}" không có trong nguồn kết quả')
    print(f'so: {loi} số không truy được')
    return loi

def tra_mang(doi, pmid):
    try:
        if doi:
            u = 'https://api.crossref.org/works/' + doi
            with urllib.request.urlopen(u, timeout=15) as r:
                return 'ok' if r.status == 200 else f'http {r.status}'
        if pmid:
            u = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json'
            with urllib.request.urlopen(u, timeout=15) as r:
                j = json.load(r)
                return 'ok' if 'error' not in j['result'].get(pmid, {'error': 1}) else 'pmid không tồn tại'
    except Exception as e:
        return f'KHONG_TRA_DUOC ({type(e).__name__})'
    return 'không có mã'

def lenh_trich(bai, ev, mang):
    rows = {r['khoa']: r for r in csv.DictReader(open(ev, encoding='utf-8'), delimiter='\t')}
    text = open(bai, encoding='utf-8').read().splitlines()
    loi, dung = 0, set()
    for i, dong in enumerate(text, 1):
        keys = re.findall(r'\[@([^\]]+)\]', dong)
        for k in [x.strip() for g in keys for x in g.split(';@')]:
            dung.add(k)
            if k not in rows:
                loi += 1; print(f'TRICH_BIA {bai}:{i}: [@{k}] không có trong evidence matrix')
        if CAU_CAN_NGUON.search(dong) and not keys:
            loi += 1; print(f'THIEU_NGUON {bai}:{i}: câu nhắc y văn mà không trích')
    for k in sorted(dung & rows.keys()):
        r = rows[k]
        if not (r.get('doi') or r.get('pmid')):
            loi += 1; print(f'KHONG_MA {ev}: {k} thiếu DOI/PMID'); continue
        if not r.get('cau_ho_tro'):
            loi += 1; print(f'KHONG_CAU {ev}: {k} thiếu câu gốc hỗ trợ (cau_ho_tro)')
        if mang:
            kq = tra_mang(r.get('doi'), r.get('pmid'))
            if kq != 'ok':
                loi += 1; print(f'MANG {k}: {kq}')
    print(f'trich: {len(dung)} trích dẫn, {loi} lỗi')
    return loi

if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) >= 3 and a[0] == 'so':
        sys.exit(1 if lenh_so(a[1], a[2:]) else 0)
    if len(a) >= 3 and a[0] == 'trich':
        sys.exit(1 if lenh_trich(a[1], a[2], '--mang' in a) else 0)
    print(__doc__); sys.exit(2)
