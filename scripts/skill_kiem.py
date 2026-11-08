"""Kiem thu muc skills/ va sinh INDEX.md + danh-muc.json.

  python scripts/skill_kiem.py          # kiem, tra ma 1 neu loi (CI dung)
  python scripts/skill_kiem.py --index  # kiem + viet lai skills/INDEX.md, skills/danh-muc.json
Luat: moi SKILL.md co name + description; name khong trung; khong file > 5 MB;
khong file bi mat (.env, cookie, khoa); khong chuoi giong khoa API.
"""
import os, re, sys, json, fnmatch

GOC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'skills')
TRAN = 5 * 2**20
CAM = ['.env', '*.env', '.env.*', '*cookie*', '*.pem', '*.key', '*.pfx', 'oauth*', 'token*.json']
MAU_BI_MAT = re.compile(r'(sk-ant-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{32,}|AIza[0-9A-Za-z_-]{35}|ghp_[A-Za-z0-9]{36}'
                        r'|github_pat_[A-Za-z0-9_]{40,}|xox[bp]-[0-9]{6,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)')
NHOM = [
    ('thiet-ke', 'Thiết kế: ảnh, slide, deck, brand, web, KV', r'brand|onbrand|deck|slide|thiet-ke|web|tach-kv|kho-minh-hoa|casting|photobooth|image|kiem-chu-anh|artradar|proposal|lps-ui|report|anh-sang'),
    ('tu-sua', 'Tự kiểm, tự sửa, vòng lặp chất lượng', r'chuan|core|lps|brand-check|thoi-quen|harsh|security|audit|tu-chay|bien-tap|architecture|cham|danh-gia'),
    ('van-hanh', 'Vận hành, điều phối, giao việc', r'agent-truong|lab-moi|proto-moi|ra-soat|overview|tra-cuu|4d|be-phong|agy|chien-luoc|gemini-task|chuyen-skill|pipeline|tracking|crawler|thu-ky|office|bank-ops|morning|dong-thread|tu-duy|linh-vuc'),
    ('video', 'Video, phim, hoạt hình', r'video|phim|sd-|le-bich|hybrid|flow-canh'),
    ('viet', 'Viết, biên tập, nội dung', r'viet|bm1|bm2|khoang-trong|giai-ma|toan-van|cafebiz'),
    ('marketing', 'Marketing, cộng đồng, kênh', r'cong-dong|pheu|tai-tao|vong-ads|listening|kenh|imc|btmh|retail'),
    ('nghien-cuu', 'Nghiên cứu, radar, dữ liệu', r'radar|research|su-kien|cuoc-thi|du-lieu'),
    ('giao-duc', 'Giáo dục, khoá học', r'course'),
]


def fm(p):
    t = open(p, encoding='utf-8', errors='ignore').read(4000)
    n = re.search(r'^name:\s*["\']?([^"\'\n]+)', t, re.M)
    d = re.search(r'^description:\s*(.+)$', t, re.M)
    return (n.group(1).strip() if n else ''), (d.group(1).strip().strip('"\'>|') if d else '')


def nhom(khoa):
    for k, _, rx in NHOM:
        if re.search(rx, khoa): return k
    return 'khac'


def main():
    loi = []; ds = []; ten_gap = {}
    nguon = json.load(open(os.path.join(GOC, '_nguon.json'), encoding='utf-8')) if os.path.exists(os.path.join(GOC, '_nguon.json')) else {}
    for loai in ('bo', 'le'):
        d0 = os.path.join(GOC, loai)
        for don_vi in sorted(os.listdir(d0)) if os.path.isdir(d0) else []:
            for r, dd, fs in os.walk(os.path.join(d0, don_vi)):
                dd.sort()
                for f in sorted(fs):
                    fp = os.path.join(r, f); rel = os.path.relpath(fp, GOC)
                    if os.path.getsize(fp) > TRAN: loi.append(f'{rel}: file > 5 MB')
                    if any(fnmatch.fnmatch(f.lower(), x) for x in CAM) and not f.endswith('.example'): loi.append(f'{rel}: file bí mật')
                    if fp.endswith(('.md', '.py', '.js', '.ts', '.json', '.yaml', '.yml', '.txt', '.sh', '.ps1')):
                        if MAU_BI_MAT.search(open(fp, encoding='utf-8', errors='ignore').read()): loi.append(f'{rel}: giống khoá API')
                    if f != 'SKILL.md': continue
                    n, de = fm(fp); relp = os.path.relpath(r, GOC).replace('\\', '/')
                    if not n: loi.append(f'{relp}/SKILL.md: thiếu name')
                    if not de: loi.append(f'{relp}/SKILL.md: thiếu description')
                    if n in ten_gap: loi.append(f'trùng tên "{n}": {ten_gap[n]} và {relp}')
                    ten_gap[n] = relp
                    ds.append({'ten': n, 'mo_ta': de, 'duong_dan': relp, 'bo': don_vi if loai == 'bo' else '',
                               'nhom': nhom(f'{don_vi} {n}'), 'ban_goc': nguon.get(f'{loai}/{don_vi}', '')})
    for x in loi: print('LOI', x)
    print(f'{len(ds)} skill, {len(loi)} loi')
    if '--index' in sys.argv:
        json.dump(ds, open(os.path.join(GOC, 'danh-muc.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        L = ['# Danh mục skill LINHX', '', f'Sinh tự động bằng `python scripts/skill_kiem.py --index`, không sửa tay. Tổng **{len(ds)}** skill.', '',
             '| Nhóm | Số |', '|---|---|']
        nh = [(k, t) for k, t, _ in NHOM] + [('khac', 'Khác')]
        for k, t in nh: L.append(f'| {t} | {sum(1 for x in ds if x["nhom"] == k)} |')
        for k, t in nh:
            xs = [x for x in ds if x['nhom'] == k]
            if not xs: continue
            L += ['', f'## {t}', '', '| Skill | Làm gì | Ở đâu |', '|---|---|---|']
            for x in sorted(xs, key=lambda x: x['ten'].lower()):
                mo = re.sub(r'\s+', ' ', x['mo_ta']).replace('|', '/')
                L.append(f"| `{x['ten']}` | {mo[:160] + ('…' if len(mo) > 160 else '')} | `{x['duong_dan']}` |")
        open(os.path.join(GOC, 'INDEX.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    sys.exit(1 if loi else 0)


if __name__ == '__main__':
    main()
