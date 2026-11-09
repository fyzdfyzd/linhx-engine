"""Quan ly phien ban kho skill LINHX (skills/). Quy uoc: skills/QUY-UOC-PHIEN-BAN.md

Don vi phien ban: moi bo skills/bo/<ten> (version trong .claude-plugin/plugin.json)
va moi skill le skills/le/<ten> (metadata.version trong frontmatter SKILL.md).
Moi don vi co CHANGELOG.md rieng; tag phat hanh la <ten>@<x.y.z>.

  python scripts/skill_ban.py ds                         # bang don vi + ban
  python scripts/skill_ban.py kiem [--base origin/main]  # CI: semver, CHANGELOG, YAML, tang ban
  python scripts/skill_ban.py tang <ten> patch|minor|major "ghi chu" [--loai Sua]
  python scripts/skill_ban.py marketplace                # sinh .claude-plugin/marketplace.json
  python scripts/skill_ban.py phat-hanh [--day]          # tag <ten>@<ban> con thieu (CI chay tren main)
  python scripts/skill_ban.py khoi-tao                   # gan moc 0.1.0 + CHANGELOG cho don vi chua co
"""
import datetime, json, os, re, subprocess, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
GOC = os.path.join(REPO, 'skills')
CHO = os.path.join(REPO, '.claude-plugin', 'marketplace.json')
SEMVER = re.compile(r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$')
TEN_CHUAN = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
LOAI = {'patch': 'Sửa', 'minor': 'Thêm', 'major': 'Đổi'}
LOAI_HOP_LE = ('Thêm', 'Đổi', 'Sửa', 'Bỏ', 'Bảo mật')
FM = re.compile(r'^(﻿?---\r?\n)(.*?)(\r?\n---[ \t]*(\r?\n|$))', re.S)
HOM_NAY = os.environ.get('LINHX_NGAY') or datetime.date.today().isoformat()


def doc(p):
    return open(p, encoding='utf-8').read()


def ghi(p, t):
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(t)


# ---------- don vi ----------

def don_vi(goc=GOC):
    ds = []
    for loai in ('bo', 'le'):
        d0 = os.path.join(goc, loai)
        for ten in sorted(os.listdir(d0)) if os.path.isdir(d0) else []:
            p = os.path.join(d0, ten)
            if os.path.isdir(p):
                ds.append({'ten': ten, 'loai': loai, 'thu_muc': p, 'rel': f'{loai}/{ten}'})
    return ds


def tep_ban(u):
    return os.path.join(u['thu_muc'], '.claude-plugin', 'plugin.json') if u['loai'] == 'bo' else os.path.join(u['thu_muc'], 'SKILL.md')


def ban_tu_text(loai, t):
    """Doc version tu noi dung plugin.json (bo) hoac SKILL.md (le)."""
    if loai == 'bo':
        try:
            return str(json.loads(t).get('version') or '')
        except ValueError:
            return ''
    m = FM.match(t)
    if not m:
        return ''
    k = re.search(r'^metadata:[ \t]*\r?\n((?:[ \t]+.*\r?\n?)*)', m.group(2) + '\n', re.M)
    if not k:
        return ''
    v = re.search(r'^[ \t]+version:[ \t]*["\']?([^"\'\r\n]+?)["\']?[ \t]*$', k.group(1), re.M)
    return v.group(1).strip() if v else ''


def ban(u):
    p = tep_ban(u)
    return ban_tu_text(u['loai'], doc(p)) if os.path.exists(p) else ''


def dat_ban(u, moi):
    p = tep_ban(u)
    t = doc(p)
    if u['loai'] == 'bo':
        if re.search(r'"version"\s*:\s*"[^"]*"', t):
            t = re.sub(r'("version"\s*:\s*)"[^"]*"', lambda m: f'{m.group(1)}"{moi}"', t, count=1)
        else:
            d = json.loads(t); d['version'] = moi
            t = json.dumps(d, ensure_ascii=False, indent=2) + '\n'
        ghi(p, t)
        return
    m = FM.match(t)
    if not m:
        raise SystemExit(f'{u["rel"]}/SKILL.md: không có frontmatter')
    nl = '\r\n' if '\r\n' in m.group(1) else '\n'
    than = m.group(2)
    km = re.search(r'^metadata:[ \t]*\r?\n', than + nl, re.M)
    if km:
        con = re.compile(r'^metadata:[ \t]*\r?\n((?:[ \t]+.*(?:\r?\n|$))*)', re.M).search(than + nl)
        kh = con.group(1)
        if re.search(r'^[ \t]+version:', kh, re.M):
            kh2 = re.sub(r'^([ \t]+version:).*$', lambda x: f'{x.group(1)} "{moi}"', kh, count=1, flags=re.M)
            than = (than + nl)[:con.start(1)] + kh2 + (than + nl)[con.end(1):]
            than = than[:-len(nl)] if than.endswith(nl) else than
        else:
            lui = re.match(r'[ \t]+', kh).group(0) if kh else '  '
            than = than[:km.end()] + f'{lui}version: "{moi}"{nl}' + than[km.end():]
            than = than.rstrip('\r\n')
    else:
        than = than.rstrip('\r\n') + f'{nl}metadata:{nl}  version: "{moi}"'
    ghi(p, m.group(1) + than + m.group(3) + t[m.end():])


def mo_ta(u):
    """description cua bo (plugin.json) hoac skill le (SKILL.md)."""
    if u['loai'] == 'bo':
        try:
            return json.loads(doc(tep_ban(u))).get('description', '')
        except (OSError, ValueError):
            return ''
    try:
        y = yaml_fm(doc(tep_ban(u)))
    except Exception:
        return ''
    return str((y or {}).get('description', '')) if isinstance(y, dict) else ''


# ---------- CHANGELOG ----------

def tieu_de_cl(ten):
    return (f'# Nhật ký thay đổi: {ten}\n\n'
            'Theo [Keep a Changelog](https://keepachangelog.com/vi/1.1.0/) và [SemVer](https://semver.org/lang/vi/). '
            'Quy ước: `skills/QUY-UOC-PHIEN-BAN.md`.\n')


def them_muc_cl(u, v, loai, ghi_chu):
    p = os.path.join(u['thu_muc'], 'CHANGELOG.md')
    t = doc(p) if os.path.exists(p) else tieu_de_cl(u['ten'])
    muc = f'## [{v}] - {HOM_NAY}\n\n### {loai}\n\n' + ''.join(f'- {x}\n' for x in ghi_chu) + '\n'
    m = re.search(r'^## \[', t, re.M)
    t = t[:m.start()] + muc + t[m.start():] if m else t.rstrip('\n') + '\n\n' + muc
    ghi(p, t.rstrip('\n') + '\n')


def muc_cl(u, v):
    p = os.path.join(u['thu_muc'], 'CHANGELOG.md')
    if not os.path.exists(p):
        return None
    m = re.search(rf'^## \[{re.escape(v)}\][^\n]*\n(.*?)(?=^## \[|\Z)', doc(p), re.S | re.M)
    return m.group(1).strip() if m else None


def so(v):
    return tuple(int(x) for x in v.split('.'))


def tang_so(v, muc):
    a, b, c = so(v)
    return {'major': f'{a + 1}.0.0', 'minor': f'{a}.{b + 1}.0', 'patch': f'{a}.{b}.{c + 1}'}[muc]


# ---------- YAML ----------

def yaml_fm(t):
    import yaml  # PyYAML; CI cai san
    m = FM.match(t.lstrip('﻿'))
    if not m:
        return None
    return yaml.safe_load(m.group(2))


# ---------- git ----------

def git(*a, kiem=False):
    r = subprocess.run(['git', '-C', REPO, *a], capture_output=True, text=True, encoding='utf-8')
    if kiem and r.returncode:
        raise SystemExit(r.stderr.strip())
    return r.stdout if r.returncode == 0 else None


# ---------- lenh ----------

def kiem(base=None, goc=GOC, cho=CHO):
    loi, canh = [], []
    try:
        import yaml  # noqa: F401
    except ImportError:
        print('LOI cần PyYAML để kiểm frontmatter: python -m pip install pyyaml')
        return 1
    ds = don_vi(goc)
    if not ds:
        loi.append('không thấy đơn vị nào trong skills/bo, skills/le (bộ kiểm không được đếm 0 mà vẫn xanh)')
    ten_gap = {}
    so_skill = 0
    for u in ds:
        v = ban(u)
        if u['ten'] in ten_gap:
            loi.append(f'trùng tên đơn vị "{u["ten"]}": {ten_gap[u["ten"]]} và {u["rel"]}')
        ten_gap[u['ten']] = u['rel']
        if not os.path.exists(tep_ban(u)):
            loi.append(f'{u["rel"]}: thiếu {os.path.relpath(tep_ban(u), u["thu_muc"])}')
            continue
        if not SEMVER.match(v):
            loi.append(f'{u["rel"]}: phiên bản "{v}" không phải x.y.z')
        elif muc_cl(u, v) is None:
            loi.append(f'{u["rel"]}/CHANGELOG.md: thiếu mục "## [{v}]"')
        if u['loai'] == 'bo':
            try:
                pj = json.loads(doc(tep_ban(u)))
                if pj.get('name') != u['ten']:
                    loi.append(f'{u["rel"]}: plugin.json name "{pj.get("name")}" khác tên thư mục')
                if 'author' in pj and not isinstance(pj['author'], dict):
                    loi.append(f'{u["rel"]}: plugin.json author phải là {{"name": "…"}}, không phải chuỗi')
                for k in ('skills', 'commands', 'agents'):
                    for x in pj.get(k) or [] if isinstance(pj.get(k), list) else []:
                        if isinstance(x, str) and not x.startswith('./'):
                            loi.append(f'{u["rel"]}: plugin.json {k} "{x}" phải bắt đầu bằng "./"')
            except ValueError as e:
                loi.append(f'{u["rel"]}: plugin.json hỏng ({e})')
        for r, dd, fs in os.walk(u['thu_muc']):
            dd.sort()
            if 'SKILL.md' not in fs:
                continue
            so_skill += 1
            rel = os.path.relpath(os.path.join(r, 'SKILL.md'), goc).replace('\\', '/')
            t = doc(os.path.join(r, 'SKILL.md'))
            if t.startswith('﻿'):
                loi.append(f'{rel}: có BOM đầu file, trình nạp không thấy frontmatter')
            try:
                y = yaml_fm(t)
            except Exception as e:  # yaml.YAMLError
                loi.append(f'{rel}: frontmatter không đọc được YAML ({str(e).splitlines()[0]}); bọc description trong dấu nháy')
                continue
            if not isinstance(y, dict):
                loi.append(f'{rel}: thiếu frontmatter'); continue
            n, de = str(y.get('name') or ''), y.get('description')
            if not n or not de:
                loi.append(f'{rel}: thiếu name hoặc description')
            if not isinstance(de, str):
                loi.append(f'{rel}: description không phải chuỗi')
            elif len(de) > 1024:
                canh.append(f'{rel}: description {len(de)} ký tự (chuẩn Agent Skills ≤ 1024)')
            if n and (not TEN_CHUAN.match(n) or len(n) > 64):
                canh.append(f'{rel}: name "{n}" chưa theo chuẩn chữ-thường-gạch-nối ≤ 64')
            elif n and n != os.path.basename(r):
                canh.append(f'{rel}: name "{n}" khác tên thư mục "{os.path.basename(r)}"')
            dong = t.count('\n')
            if dong > 500:
                canh.append(f'{rel}: {dong} dòng (> 500, nên tách sang references/)')
    if ds and not so_skill:
        loi.append('không đếm được SKILL.md nào')
    # marketplace phai khop
    moi = json.dumps(sinh_marketplace(ds), ensure_ascii=False, indent=2) + '\n'
    if not os.path.exists(cho) or doc(cho) != moi:
        loi.append('.claude-plugin/marketplace.json chưa khớp: chạy python scripts/skill_ban.py marketplace')
    # tang ban so voi base
    if base:
        loi += kiem_tang(base, ds)
    for x in canh:
        print('CANH', x)
    for x in loi:
        print('LOI', x)
    print(f'{len(ds)} đơn vị, {so_skill} skill, {len(loi)} lỗi, {len(canh)} cảnh báo')
    return 1 if loi else 0


def kiem_tang(base, ds):
    if os.environ.get('LINHX_KHONG_TANG') == '1':
        print('BO_QUA kiểm tăng bản (nhãn khong-tang-ban)')
        return []
    goc_mb = git('merge-base', base, 'HEAD')
    if goc_mb is None:
        return [f'không tìm thấy merge-base với {base} (checkout cần fetch-depth: 0)']
    goc_mb = goc_mb.strip()
    doi = (git('diff', '--name-only', f'{goc_mb}', '--', 'skills/') or '').split()
    doi += (git('ls-files', '--others', '--exclude-standard', '--', 'skills/') or '').split()
    loi = []
    theo_rel = {u['rel']: u for u in ds}
    cham = sorted({'/'.join(p.split('/')[1:3]) for p in doi if p.count('/') >= 3 and p.split('/')[1] in ('bo', 'le')})
    for rel in cham:
        u = theo_rel.get(rel)
        if not u:
            continue  # don vi da bi xoa
        v = ban(u)
        cu_text = git('show', f'{goc_mb}:{os.path.relpath(tep_ban(u), REPO).replace(os.sep, "/")}')
        if cu_text is None:
            continue  # don vi moi
        cu = ban_tu_text(u['loai'], cu_text)
        if not SEMVER.match(cu) or git('cat-file', '-e', f'{goc_mb}:skills/{rel}/CHANGELOG.md') is None:
            continue  # truoc day chua co ban hoac chua co CHANGELOG: lan nay la moc dau
        if not SEMVER.match(v) or so(v) <= so(cu):
            loi.append(f'{rel}: có sửa nhưng chưa tăng bản ({cu} → {v}); chạy skill_ban.py tang {u["ten"]} patch|minor|major "…" '
                       '(chỉ sửa chính tả thì gắn nhãn khong-tang-ban)')
    return loi


def sinh_marketplace(ds):
    pl = []
    for u in ds:
        e = {'name': u['ten'].lower().replace('_', '-'), 'description': re.sub(r'\s+', ' ', mo_ta(u) or '').strip(),
             'version': ban(u) or '0.0.0', 'category': 'bo' if u['loai'] == 'bo' else 'le'}
        if u['loai'] == 'bo':
            e['source'] = f'./skills/{u["rel"]}'
        else:
            e.update({'source': './', 'strict': False, 'skills': [f'./skills/{u["rel"]}']})
        pl.append(e)
    return {'name': 'linhx', 'owner': {'name': 'LINHX'},
            'metadata': {'description': 'Kho skill LINHX: bộ (bo) và skill lẻ (le), mỗi đơn vị một phiên bản SemVer'},
            'plugins': pl}


def lenh_tang(ten, muc, ghi_chu, loai=None):
    if muc not in LOAI:
        raise SystemExit('mức tăng: patch | minor | major')
    loai = loai or LOAI[muc]
    if loai not in LOAI_HOP_LE:
        raise SystemExit(f'--loai phải là một trong {LOAI_HOP_LE}')
    u = next((x for x in don_vi() if x['ten'] == ten or x['rel'] == ten), None)
    if not u:
        raise SystemExit(f'không thấy đơn vị "{ten}" trong skills/bo, skills/le')
    cu = ban(u) or '0.0.0'
    moi = tang_so(cu, muc)
    dat_ban(u, moi)
    them_muc_cl(u, moi, loai, ghi_chu)
    print(f'{u["rel"]}: {cu} → {moi}')
    return moi


def lenh_khoi_tao(ghi_chu_goc='Mốc đầu: gom về kho chuẩn linhx-engine/skills (PR #3, 8/11/2026).'):
    nguon_p = os.path.join(GOC, '_nguon.json')
    nguon = json.load(open(nguon_p, encoding='utf-8')) if os.path.exists(nguon_p) else {}
    n = 0
    for u in don_vi():
        v = ban(u)
        if not SEMVER.match(v):
            v = '0.1.0'
            dat_ban(u, v)
        if muc_cl(u, v) is None:
            gc = [ghi_chu_goc] + ([f'Bản gốc: `{nguon[u["rel"]]}`.'] if nguon.get(u['rel']) else [])
            them_muc_cl(u, v, 'Thêm', gc)
            n += 1
    print(f'khởi tạo {n} đơn vị')


def lenh_phat_hanh(day=False):
    co = set((git('tag', '-l') or '').split())
    moi = []
    for u in don_vi():
        v = ban(u)
        if SEMVER.match(v) and f'{u["ten"]}@{v}' not in co:
            moi.append((u, v))
    for u, v in moi:
        tag = f'{u["ten"]}@{v}'
        print('TAG', tag)
        if day:
            git('tag', '-a', tag, '-m', f'{tag}\n\n{muc_cl(u, v) or ""}', kiem=True)
    if day and moi:
        tags = [f'{u["ten"]}@{v}' for u, v in moi]
        for i in range(0, len(tags), 50):
            git('push', 'origin', *[f'refs/tags/{t}' for t in tags[i:i + 50]], kiem=True)
    print(f'{len(moi)} tag {"đã đẩy" if day else "cần tạo"}')


def main(a):
    if not a or a[0] in ('-h', '--help'):
        print(__doc__); return 0
    c = a[0]
    if c == 'ds':
        for u in don_vi():
            print(f'{ban(u) or "-":>8}  {u["rel"]}')
        return 0
    if c == 'kiem':
        return kiem(a[a.index('--base') + 1] if '--base' in a else None)
    if c == 'tang':
        if len(a) < 4:
            raise SystemExit('dùng: tang <ten> patch|minor|major "ghi chú" ["ghi chú 2" ...] [--loai Sửa]')
        loai = None
        if '--loai' in a:
            i = a.index('--loai'); loai = a[i + 1]; a = a[:i] + a[i + 2:]
        lenh_tang(a[1], a[2], a[3:], loai)
        return 0
    if c == 'marketplace':
        os.makedirs(os.path.dirname(CHO), exist_ok=True)
        ghi(CHO, json.dumps(sinh_marketplace(don_vi()), ensure_ascii=False, indent=2) + '\n')
        print('đã viết', os.path.relpath(CHO, REPO)); return 0
    if c == 'phat-hanh':
        lenh_phat_hanh('--day' in a); return 0
    if c == 'khoi-tao':
        lenh_khoi_tao(); return 0
    raise SystemExit(f'lệnh lạ: {c}')


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
