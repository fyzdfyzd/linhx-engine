#!/usr/bin/env python3
"""cham_cau.py - chấm bài tiếng Việt ở mức từng câu (tầng 1 và 2 của khâu chấm khắt khe).

Tách bài thành câu đánh số Đ<đoạn>.C<câu>, gắn cờ từng câu, rồi so cả bài với ngưỡng cứng.
  python cham_cau.py bai.md [--hoi-quy so-loi-hoi-quy.json] [--cho-phep "Việt Nam,Zalo"] [--json]
  python cham_cau.py bai.md --xuat-cau cau.md      # danh sách câu đánh số cho giám khảo
  python cham_cau.py bai.md --sach ban-sach.md     # bỏ mã nguồn [N1] [T2] trước khi giao

Mã nguồn: câu nào có số, phần trăm hoặc tên riêng phải mang mã [N..]/[T..] ngay trong câu,
hoặc dấu [GIẢ LẬP] / [CẦN LINH]. Bảng (dòng bắt đầu bằng |), tiêu đề (#) và dòng nguồn bảng (*Nguồn) không chấm.
Chỉ dùng thư viện chuẩn.
"""
import argparse, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from kiem_van_dich import GOC  # noqa: E402

# Ngưỡng giọng = dải của 7 bài Linh đã đăng báo (moc-giong.json), đo bằng chính script này: câu TB 19,9–38,8, câu >35 từ 10–43%, "tôi" 1,3–9,9/1000, câu ngắn tới 1,6/300 chữ
NGUONG = {'cau_tb_min': 19, 'cau_tb_max': 39, 'cau_max': 100, 'ti_le_cau_dai_min': 0.10, 'toi_min': 0, 'toi_max': 12,
          'cau_ngan_moi_300_chu_max': 1.6, 'ti_le_hai_ve_max': 0.05}
MA = re.compile(r'\[(?:[NT]\d+(?:\s*,\s*[NT]\d+)*|GIẢ LẬP|CẦN LINH)\]')
CHO_PHEP_MAC_DINH = {'Việt', 'Nam', 'AI', 'OPC', 'Zalo', 'Facebook', 'Tôi', 'Hà', 'Nội', 'TP.HCM', 'Sài', 'Gòn', 'Tết'}
BO_BA = re.compile(r'(\b[^\W\d_]+(?: [^\W\d_]+){0,2}), ([^\W\d_]+(?: [^\W\d_]+){0,2}),? (?:và|hay|hoặc) ([^\W\d_]+(?: [^\W\d_]+){0,2})[.,]')
DUNG = {'một', 'người', 'là', 'của', 'và', 'thì', 'mà', 'có', 'không', 'những', 'các', 'cho', 'với', 'đã', 'được', 'này', 'ấy', 'đó', 'tôi', 'anh', 'cái'}


def doc_doan(text):
    doan = []
    for khoi in re.split(r'\n\s*\n', text):
        k = khoi.strip()
        if not k or k.startswith(('#', '|', '*Nguồn', '---')) or re.fullmatch(r'\*\*[^*]+\*\*', k):
            continue
        k = re.sub(r'(?m)^>\s?(-\s)?', '', k)
        doan.append(' '.join(k.split()))
    return doan


def tach_cau(doan):
    return [c.strip() for c in re.split(r'(?<=[.!?…])["”»]?\s+(?=[A-ZÀ-Ỹ"“«(\[*])', doan) if c.strip()]


def so_tu(c):
    return len(MA.sub('', c).split())


# Lỗi Vân Anh bắt (ho-so-bien-tap/van-anh/LUAT.md), đo trên 7 bài Linh đã đăng và 7 bản máy viết (19/10/2026):
# hai vế VA-01: bài đăng 0–4% số câu, bản máy 3–36% (PA1 v3 15%) -> ngưỡng 5%.
# "không còn là… mà là" VA-02 và "càng… càng": bài đăng 0 lần, bản máy 2 và 4 lần -> cờ mềm.
# ("không chỉ… mà còn", "không phải… mà là" Linh dùng 8 lần trong bài đăng, không gắn cờ.)
HAI_VE = re.compile(r', còn |; còn |\bchưa\b.{3,60}\bnhưng\b.{3,80}\bthì\b|\bthì\b.{3,80}, còn\b')
GUONG = re.compile(r'\bđược\b.{2,40}\bnhưng (không|chẳng|chưa)\b.{2,40}\bđược\b')
DIEU_KIEN = re.compile(r'^(khi|nếu|đến|lúc|hễ|sau|mỗi|càng|được|trước|giờ|bây giờ|hồi|nay|vậy|thế|rồi|cứ|lần|ngày|tháng|năm|đã|chừng|vừa|ai|gì|có|muốn|cần|để|nói|biết|hỏi|nghĩ|làm|ở|với|còn)\b', re.I)
KHONG_CON_LA = re.compile(r'không còn là\b.{2,80}\bmà là\b', re.I)
CANG = re.compile(r'\bcàng\b.{1,40}\bcàng\b', re.I)


# Chữ máy tiếng Việt (scripts/tu_may.py, 7 bài Linh đăng so với 7 bài Sonnet cùng tít, 19/10/2026).
# Bài đăng 0/1000 chữ; 6 bản máy đề OPC (ngoài mẫu) 4,3–7,8/1000. Cảnh báo khi > 2/1000; chưa chặn vì chưa có bài người ngoài mẫu.
CHU_MAY = re.compile(r'\b(chứ không phải|cái giá của|tử tế|thật sự|vẫn là|nghĩa là|ở chỗ|nghe thì|về phía|cho ta|ấy là|cụ thể|học được|có thật|thấy mình|chút|mười|mươi)\b', re.I)


def thi_doi(c):
    """Câu đối kiểu "X thì đã/vẫn/không…" (chủ đề + thì), bỏ "thì" sau mệnh đề điều kiện, thời gian."""
    w = c.split()
    for i, t in enumerate(w[:9]):
        if t.lower().strip(',') == 'thì' and i >= 1:
            truoc = ' '.join(w[:i]).lower()
            if DIEU_KIEN.match(truoc) or ',' in truoc:
                return False
            return bool(re.match(r'(đã|vẫn|lại|không|chưa|có|chỉ|cũng|đang|chẳng|vô|khác)\b', ' '.join(w[i+1:i+3]).lower()))
    return False


def co_cau(c, i_cau, n_cau, cau_truoc, cho_phep, hoi_quy):
    co = []
    sach = MA.sub('', c)
    thap = sach.lower()
    for mau, nhom, goi_y in GOC:
        if re.search(mau, thap):
            co.append(f'VD:{re.search(mau, thap).group(0)}')
    n = so_tu(c)
    if n < 8:
        co.append('ngắn')
    if i_cau == n_cau - 1 and n_cau >= 3 and n < 10:
        co.append('chốt-ngắn')
    if re.search(r'\d', re.sub(r'\b(19|20)\d\d\b|(Nghị quyết|Điều|NQ|Luật)\s*\d+[/\w-]*', '', sach)):
        co.append('chữ-số')
    if HAI_VE.search(sach) or GUONG.search(sach) or thi_doi(sach):
        co.append('hai-vế')
    if KHONG_CON_LA.search(sach):
        co.append('không-còn-là')
    if CANG.search(sach):
        co.append('càng-càng')
    if BO_BA.search(sach):
        co.append('bộ-ba?')
    tu = sach.split()
    rieng = [w.strip('.,;:!?"“”()') for t, w in zip(tu, tu[1:])
             if w[:1].isupper() and not re.search(r'[.:!?"“”(>-]$', t) and not w.startswith(('"', '“'))]
    rieng = [w for w in rieng if w and w not in cho_phep]
    if (re.search(r'\d|%', sach) or rieng) and not MA.search(c):
        co.append('thiếu-mã-nguồn' + (f'({",".join(rieng[:3])})' if rieng else ''))
    if cau_truoc:
        def bigram(s):
            w = [x for x in re.findall(r'[^\W\d_]+', s.lower())]
            return {(a, b) for a, b in zip(w, w[1:]) if not (a in DUNG and b in DUNG)}
        lap = bigram(sach) & bigram(MA.sub('', cau_truoc))
        if lap:
            co.append('lặp:' + ' '.join(sorted(lap)[0]))
    for luat in hoi_quy:
        if re.search(luat['mau'], thap):
            co.append('HỒI-QUY:' + luat['ten'])
    return co


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('bai')
    ap.add_argument('--hoi-quy')
    ap.add_argument('--cho-phep', default='')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--xuat-cau')
    ap.add_argument('--sach')
    a = ap.parse_args()
    text = Path(a.bai).read_text(encoding='utf-8')
    if a.sach:
        Path(a.sach).write_text(re.sub(r' ?\[[NT]\d+(?:\s*,\s*[NT]\d+)*\]', '', text), encoding='utf-8')
        print(f'Đã ghi bản bỏ mã nguồn: {a.sach}')
        return
    cho_phep = CHO_PHEP_MAC_DINH | {x.strip() for x in a.cho_phep.split(',') if x.strip()}
    hoi_quy = json.loads(Path(a.hoi_quy).read_text(encoding='utf-8')) if a.hoi_quy else []
    cau_all = []
    for p, d in enumerate(doc_doan(text), 1):
        cs = tach_cau(d)
        for i, c in enumerate(cs):
            cau_all.append({'id': f'Đ{p}.C{i+1}', 'cau': c, 'tu': so_tu(c),
                            'co': co_cau(c, i, len(cs), cs[i-1] if i else None, cho_phep, hoi_quy)})
    if a.xuat_cau:
        Path(a.xuat_cau).write_text('\n'.join(f"{x['id']} | {MA.sub('', x['cau']).strip()}" for x in cau_all) + '\n', encoding='utf-8')
        print(f'Đã ghi {len(cau_all)} câu: {a.xuat_cau}')
        return
    n = len(cau_all) or 1
    tong_tu = sum(x['tu'] for x in cau_all) or 1
    toi = sum(len(re.findall(r'\btôi\b', MA.sub('', x['cau']).lower())) for x in cau_all) * 1000 / tong_tu
    so_ngan = sum('ngắn' in x['co'] for x in cau_all)
    chi_so = {'so_cau': len(cau_all), 'so_tu': tong_tu, 'cau_tb': round(tong_tu / n, 1),
              'ti_le_cau_dai': round(sum(x['tu'] > 35 for x in cau_all) / n, 2),
              'toi_moi_1000': round(toi, 1), 'cau_ngan': so_ngan,
              'cau_ngan_moi_300_chu': round(so_ngan * 300 / tong_tu, 2)}
    truot = []
    if chi_so['cau_tb'] < NGUONG['cau_tb_min']: truot.append(f"câu TB {chi_so['cau_tb']} < {NGUONG['cau_tb_min']}")
    if chi_so['cau_tb'] > NGUONG['cau_tb_max']: truot.append(f"câu TB {chi_so['cau_tb']} > {NGUONG['cau_tb_max']} (dài quá mức Linh)")
    qua_dai = [x['id'] for x in cau_all if x['tu'] > NGUONG['cau_max']]
    if qua_dai: truot.append(f"câu trên {NGUONG['cau_max']} từ: {', '.join(qua_dai)}")
    if chi_so['ti_le_cau_dai'] < NGUONG['ti_le_cau_dai_min']: truot.append(f"câu >35 từ {chi_so['ti_le_cau_dai']:.0%} < {NGUONG['ti_le_cau_dai_min']:.0%}")
    if not NGUONG['toi_min'] <= chi_so['toi_moi_1000'] <= NGUONG['toi_max']: truot.append(f"'tôi' {chi_so['toi_moi_1000']}/1000 ngoài {NGUONG['toi_min']}–{NGUONG['toi_max']}")
    if chi_so['cau_ngan_moi_300_chu'] > NGUONG['cau_ngan_moi_300_chu_max']: truot.append(f"câu ngắn {so_ngan} (quá {NGUONG['cau_ngan_moi_300_chu_max']}/300 chữ)")
    hai_ve = sum('hai-vế' in x['co'] for x in cau_all)
    chi_so['ti_le_hai_ve'] = round(hai_ve / n, 2)
    if chi_so['ti_le_hai_ve'] > NGUONG['ti_le_hai_ve_max']: truot.append(f"câu so sánh hai vế {hai_ve} ({chi_so['ti_le_hai_ve']:.0%} > {NGUONG['ti_le_hai_ve_max']:.0%})")
    chu_may = [m.group(0).lower() for x in cau_all for m in CHU_MAY.finditer(MA.sub('', x['cau']))]
    chi_so['chu_may_1000'] = round(len(chu_may) * 1000 / tong_tu, 1)
    canh_bao = [f"chữ máy {chi_so['chu_may_1000']}/1000 (>2): {', '.join(sorted(set(chu_may)))}"] if chi_so['chu_may_1000'] > 2 else []
    cung = [x for x in cau_all if any(c.startswith(('HỒI-QUY', 'thiếu-mã', 'VD', 'chữ-số')) for c in x['co'])]
    if cung: truot.append(f'{len(cung)} câu có cờ cứng (hồi quy, thiếu mã nguồn, văn dịch, chữ số)')
    kq = {'bai': a.bai, 'chi_so': chi_so, 'dat': not truot, 'truot': truot, 'canh_bao': canh_bao, 'cau': cau_all}
    if a.json:
        print(json.dumps(kq, ensure_ascii=False, indent=1)); return
    print(f"# Chấm câu tầng 1–2: {Path(a.bai).name} · {'ĐẠT' if not truot else 'TRƯỢT'}")
    print(f"{chi_so['so_cau']} câu · {tong_tu} từ · câu TB {chi_so['cau_tb']} · câu >35 từ {chi_so['ti_le_cau_dai']:.0%} · 'tôi' {chi_so['toi_moi_1000']}/1000 · câu ngắn {so_ngan}")
    for t in truot:
        print(f'- TRƯỢT: {t}')
    for t in canh_bao:
        print(f'- CẢNH BÁO: {t}')
    print('\n| Câu | Từ | Cờ | Đầu câu |\n|---|---|---|---|')
    for x in cau_all:
        if x['co']:
            print(f"| {x['id']} | {x['tu']} | {'; '.join(x['co'])} | {MA.sub('', x['cau'])[:70]} |")


if __name__ == '__main__':
    try:
        main()
    except BrokenPipeError:
        pass
