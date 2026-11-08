#!/usr/bin/env python3
"""Lượng hoá bốn lớp kiểm của biên tập viên từ bản trích xuất JSON (references/trich-xuat-dau-van.md).

  python luong_hoa.py bai.md lan-1.json [lan-2.json ...] [--json]

Mỗi file JSON là một lượt trích độc lập của cùng một bài. Script dò lại từng trích dẫn trong bài
(mục không tìm thấy bị bỏ và đếm là "trích ảo"), tính chỉ số từng lượt, rồi báo trung bình và độ lệch
giữa các lượt. Lệch lớn nghĩa là chỉ số chưa ổn định: chạy thêm lượt trích (rà đệ quy) đến khi lệch nhỏ.

Lớp 1 Hiểu:  phải nhớ/1000 chữ, thuật ngữ chưa giải nghĩa, % chủ thể không tên
Lớp 2 Tin:   neo cụ thể mỗi câu chuyện, % câu tóm tắt trong chuyện
Lớp 3 Ý:     số liệu/1000 chữ, % số liệu không đỡ ý nào, số liệu nhắc lại cách >=4 đoạn
Lớp 4 Giọng: ẩn dụ/1000 chữ, ẩn dụ trải >=2 đoạn, độ trải lớn nhất (đoạn)
"""
import json, re, statistics, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cham_cau import doc_doan, tach_cau, MA  # noqa: E402


def chuan(s):
    return re.sub(r'\s+', ' ', re.sub(r'[“”"«»*_]', '', s.lower())).strip()


def doc_json(p):
    t = Path(p).read_text(encoding='utf-8')
    m = re.search(r'\{.*\}', t, re.S)
    return json.loads(m.group(0))


def chi_so(bai_chuan, so_chu, d):
    ao = 0

    def that(muc):
        nonlocal ao
        tr = chuan(muc.get('trich') or '')
        ok = bool(tr) and tr[:40] in bai_chuan
        ao += not ok
        return ok

    k = 1000 / so_chu
    ad = [x for x in d.get('an_du', []) if that(x)]
    sl = [x for x in d.get('so_lieu', []) if that(x)]
    ct = [x for x in d.get('chu_the', []) if that(x)]
    ch = d.get('chuyen', [])
    neo = sum(sum(c.get('neo', {}).values()) for c in ch)
    cau_ch = sum(c.get('so_cau', 0) for c in ch) or 1
    trai = [len(set(x.get('doan', []))) for x in ad]
    xa = [x for x in sl if any(abs(n - x.get('doan', 0)) >= 4 for n in x.get('nhac_lai_o_doan') or [])]
    tong = len(d.get('an_du', [])) + len(d.get('so_lieu', [])) + len(d.get('chu_the', []))
    return {
        'L1_phai_nho_1000': round(len(d.get('phai_nho', [])) * k, 1),
        'L1_thuat_ngu_chua_giai': sum(not x.get('giai_nghia_o_lan_dau') for x in d.get('thuat_ngu', [])),
        'L1_chu_the_khong_ten_pct': round(100 * sum(not x.get('co_ten') for x in ct) / (len(ct) or 1)),
        'L2_neo_moi_cau_chuyen': round(neo / cau_ch, 2) if ch else None,
        'L2_cau_tom_tat_pct': round(100 * sum(c.get('cau_tom_tat', 0) for c in ch) / cau_ch) if ch else None,
        'L3_so_lieu_1000': round(len(sl) * k, 1),
        'L3_so_lieu_khong_do_y_pct': round(100 * sum(not x.get('y_no_do') for x in sl) / (len(sl) or 1)),
        'L3_nhac_lai_xa': len(xa),
        'L4_an_du_1000': round(len(ad) * k, 1),
        'L4_an_du_trai_2_doan': sum(t >= 2 for t in trai),
        'L4_trai_lon_nhat': max(trai, default=0),
        '_trich_ao_pct': round(100 * ao / (tong or 1)),
    }


def main():
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    if len(a) < 2:
        sys.exit(__doc__)
    bai = Path(a[0]).read_text(encoding='utf-8')
    doan = doc_doan(bai)
    so_chu = sum(len(MA.sub('', c).split()) for d in doan for c in tach_cau(d)) or 1
    bc = chuan(MA.sub('', bai))
    luot = [chi_so(bc, so_chu, doc_json(p)) for p in a[1:]]
    kq = {'bai': Path(a[0]).name, 'so_chu': so_chu, 'so_luot': len(luot), 'chi_so': {}}
    for key in luot[0]:
        v = [x[key] for x in luot if x[key] is not None]
        if not v:
            kq['chi_so'][key] = None
            continue
        kq['chi_so'][key] = {'tb': round(statistics.mean(v), 2), 'lech': round(max(v) - min(v), 2)}
    if '--json' in sys.argv:
        print(json.dumps(kq, ensure_ascii=False))
        return
    print(f"# Lượng hoá: {kq['bai']} ({so_chu} chữ, {len(luot)} lượt trích)\n")
    print('| Chỉ số | Trung bình | Lệch giữa các lượt |\n|---|---|---|')
    for key, v in kq['chi_so'].items():
        print(f"| {key} | {v['tb'] if v else '-'} | {v['lech'] if v else '-'} |")


if __name__ == '__main__':
    main()
