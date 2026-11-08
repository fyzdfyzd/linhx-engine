"""Gom skill LINHX tu nhieu nguon ve skills/ chuan (moi skill mot ban goc).

Chay: python scripts/skill_gom.py <thu_muc_nguon>[=<nhan>] ...
Vi du: python scripts/skill_gom.py D:\\LINHX=D:\\LINHX "%TEMP%\\goi\\THU-MUC-CHUNG=thu muc chung"
Nguon: goi chuyen may da giai nen, D:\\LINHX, thu muc chung... Ghi de skills/bo, skills/le.
Luat chon ban goc: ban co file sua gan nhat thang; hoa thi uu tien LAB goc > SKILLS > PROTO/PRJ.
"""
import os, re, sys, json, shutil, fnmatch

GOC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'skills')
BO_QUA_DIR = {'node_modules', '.git', '.venv', 'venv', '__pycache__', 'dist', '.next', 'output', 'outputs',
              'test-results', '.cache', '.remotion', '_cu', '_tmp', 'gstack', 'IFAGENT-wt', '_tam-lab043-nap',
              '_luu-tru-v0.1', 'vi-du', 'Du_Lieu_Mau_Vinhomes'}
BO_QUA_FILE = ['.env', '*.env', '.env.*', '*cookie*', '*.pem', '*.key', '*.pfx', 'oauth*', 'token*.json',
               '*.zip', '*.tgz', '*.mp4', '*.mov', '*.wav', '*.mp3', '*.psd', '*.exe', '*.dll']
# Skill co san cua Anthropic/Google: khong phai cua LINHX, khong gom
NGOAI = {'docx', 'pdf', 'pptx', 'xlsx', 'skill-creator', 'built-in-browser', 'chrome-browser', 'computer-use',
         'deep-research', 'docs', 'google-workspace', 'import-memory', 'web-mmorpg-packet-server-reconstructor',
         'rea-jadx-reverse-gdd-reconstructor'}
# Bo/repo chep tu ngoai ve de tham khao, khong phai skill LINHX
NGOAI_BO = {'video-shotcraft',
            'linhx-cong-dong', 'linhx-su-kien'}  # 2 bo nay da gop vao linhx-radar (14/10)
# Hai skill khac nhau trung ten: doi ten ban trong bo de agy noi khong de nhau
DOI_TEN = {('linhx-bien-tap', 'hoc-tu-ban-sua'): 'hoc-luat-bien-tap'}
TRAN_FILE = 5 * 2**20


def fm(p):
    t = open(p, encoding='utf-8', errors='ignore').read(4000)
    n = re.search(r'^name:\s*["\']?([^"\'\n]+)', t, re.M)
    d = re.search(r'^description:\s*(.+)$', t, re.M)
    return (n.group(1).strip() if n else ''), (d.group(1).strip().strip('"\'') if d else '')


def uu_tien(p):
    if '/LAB/' in p or 'THU-MUC-CHUNG' in p: return 0
    if '/SKILLS/' in p: return 1
    return 2


def moi_nhat(d):
    m = 0
    for r, ds, fs in os.walk(d):
        ds[:] = [x for x in ds if x not in BO_QUA_DIR]
        for f in fs:
            try: m = max(m, os.path.getmtime(os.path.join(r, f)))
            except OSError: pass
    return m


def bi_bo(r):
    return any(x in BO_QUA_DIR for x in r.replace('\\', '/').split('/'))


def chep(src, dst, bo):
    for r, ds, fs in os.walk(src):
        ds[:] = [x for x in ds if x not in BO_QUA_DIR]
        for f in fs:
            fp = os.path.join(r, f)
            if any(fnmatch.fnmatch(f.lower(), x) for x in BO_QUA_FILE) and not f.endswith('.example'):
                bo.append(fp); continue
            if os.path.getsize(fp) > TRAN_FILE:
                bo.append(f'{fp} ({os.path.getsize(fp) // 2**20} MB)'); continue
            to = os.path.join(dst, os.path.relpath(fp, src))
            os.makedirs(os.path.dirname(to), exist_ok=True)
            shutil.copy2(fp, to)


def main(args):
    nhan = {}
    nguon = []
    for a in args:
        p, _, l = a.partition('=')
        p = os.path.abspath(p); nguon.append(p); nhan[p] = l or p
    def ghi(p):
        p = os.path.abspath(p)
        for k, l in nhan.items():
            if p.startswith(k): return (l.rstrip('/\\') + '/' + os.path.relpath(p, k)).replace('\\', '/')
        return p
    bo_ung = {}; le_ung = {}
    for n0 in nguon:
        for r, ds, fs in os.walk(n0):
            ds[:] = [x for x in ds if x not in BO_QUA_DIR]
            if os.path.basename(r) == '.claude-plugin' and 'plugin.json' in fs:
                try: ten = json.load(open(os.path.join(r, 'plugin.json'), encoding='utf-8'))['name']
                except Exception: continue
                if ten in NGOAI_BO: continue
                bo_ung.setdefault(ten, []).append(os.path.dirname(r))
    bo_goc = {t: max(ps, key=lambda p: (moi_nhat(p), -uu_tien(p))) for t, ps in bo_ung.items()}
    trong_bo = set()
    for ps in bo_ung.values():
        trong_bo |= {os.path.abspath(p) for p in ps}
    ten_trong_bo = set()
    for t, p in bo_goc.items():
        for r, ds, fs in os.walk(p):
            if 'SKILL.md' in fs: ten_trong_bo.add(fm(os.path.join(r, 'SKILL.md'))[0] or os.path.basename(r))
    for n0 in nguon:
        for r, ds, fs in os.walk(n0):
            ds[:] = [x for x in ds if x not in BO_QUA_DIR]
            if 'SKILL.md' not in fs: continue
            if any(os.path.abspath(r).startswith(b + os.sep) for b in trong_bo): continue
            ten = fm(os.path.join(r, 'SKILL.md'))[0] or os.path.basename(r)
            ten = re.sub(r'[^A-Za-z0-9_-]+', '-', ten.replace('<slug>', 'mau')).strip('-').lower()
            if ten in NGOAI or ten in NGOAI_BO or ten in ten_trong_bo: continue
            le_ung.setdefault(ten, []).append(r)
    le_goc = {t: max(ps, key=lambda p: (os.path.getmtime(os.path.join(p, 'SKILL.md')), -uu_tien(p))) for t, ps in le_ung.items()}
    for k in ('bo', 'le'):
        shutil.rmtree(os.path.join(GOC, k), ignore_errors=True)
    bo = []; nguon_ghi = {}
    for t, p in sorted(bo_goc.items()):
        chep(p, os.path.join(GOC, 'bo', t), bo); nguon_ghi['bo/' + t] = ghi(p)
        for (b, cu), moi in DOI_TEN.items():
            f = os.path.join(GOC, 'bo', b, 'skills', cu, 'SKILL.md')
            if b == t and os.path.exists(f):
                s = open(f, encoding='utf-8').read()
                open(f, 'w', encoding='utf-8').write(re.sub(r'^name:.*$', 'name: ' + moi, s, count=1, flags=re.M))
    for t, p in sorted(le_goc.items()):
        chep(p, os.path.join(GOC, 'le', t), bo); nguon_ghi['le/' + t] = ghi(p)
    json.dump(nguon_ghi, open(os.path.join(GOC, '_nguon.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    open(os.path.join(GOC, '_bo-qua.txt'), 'w', encoding='utf-8').write('\n'.join(ghi(x.split(' (')[0]) for x in bo))
    print(f'{len(bo_goc)} bo, {len(le_goc)} skill le, bo qua {len(bo)} file')


if __name__ == '__main__':
    main(sys.argv[1:])
