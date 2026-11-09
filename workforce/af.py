#!/usr/bin/env python3
"""af.py: lõi LINHX Agent Force. Một workforce = một thư mục. Chỉ Python stdlib.

Vòng: SETUP (moi) -> RUNNING (giao, chuyen, bang) -> LEARNING (phan-hoi, hoc) -> UPDATE (thang-cap, lui) -> RUNNING.

  python af.py moi <W> --ten "Nụ Event" --don-vi "ifAgent Event" [--kho ../skills --skills a,b]
  python af.py giao <W> --workflow tra-loi-lead --viec "..." [--nguoi-giao linh]
  python af.py chuyen <W> LX-0001 dang_lam|cho_duyet|xong|tra_lai|chan|huy [--ai hang] [--ly-do "..."]
  python af.py bang <W> [--html bang.html]
  python af.py phan-hoi <W> --dich skill:tra-ho-so --loai xau --noi-dung "..." [--viec LX-0001]
  python af.py nho <W> "điều cần nhớ"
  python af.py vang <W> --dich workflow:x --tep bai-tot.md --nguon "..." --vi-sao "..."   # thêm bản vàng
  python af.py ban-sua <W> --viec LX-0003 --ban-tho a.md --ban-nguoi b.md --ai hang --luat "..."   # học từ bản sửa
  python af.py hoc-ngoai <W> --dich skill:x --nguon "repo/người" --noi-dung "..."       # học từ chuẩn cao nhất
  python af.py hoc <W>                      # gom bài học thành đề xuất (chạy cuối ngày)
  python af.py thang-cap <W> <ma-de-xuat> --duyet linh
  python af.py lui <W> skill:tra-ho-so
  python af.py lenh <W> --tu <ma-nguoi> "/giao ..."   # cầu nối chat (Zalo/Telegram/email)
  python af.py nap-skill <W> --kho ../skills     # chép skill theo kenh.json (mẫu trong repo không kèm skill)
  python af.py kiem <W>
  python af.py moi <W> --mau ban-hang --ten ... --don-vi ... --kho ../skills   # dựng từ bộ mẫu
  python af.py muc <W>                       # chấm mức 1 (mở nhóm) / 2 (đạt 14 ngày)
  python af.py muc --mau ban-hang <W1> <W2>  # mức 3: bộ mẫu đã chạy ổn ở ≥ 2 đơn vị
  python af.py hoc-cheo ban-hang <W1> <W2> <W3>   # bài học lặp ở ≥ 3 đơn vị → sửa bộ mẫu
  python af.py dong-goi <W> <ra.zip> [--mot-file GOI.md]
  python af.py may-chu <W> [--cong 8120]    # server mỏng, token ở biến AF_TOKEN
"""
import argparse, difflib, fnmatch, html, json, os, re, shutil, sys, time, zipfile

GOC = os.path.dirname(os.path.abspath(__file__))
KHUON = os.path.join(GOC, 'khuon')
BO_MAU = os.path.join(GOC, 'bo-mau')
TRAN_NHO = 2200
TRANG_THAI = ['cho', 'dang_lam', 'cho_duyet', 'tra_lai', 'xong', 'chan', 'huy']
CHUYEN = {
    'cho': {'dang_lam', 'chan', 'huy'},
    'dang_lam': {'cho_duyet', 'chan', 'huy'},
    'cho_duyet': {'xong', 'tra_lai', 'huy'},
    'tra_lai': {'dang_lam', 'huy'},
    'chan': {'cho', 'dang_lam', 'huy'},
    'xong': set(), 'huy': set(),
}
DAU_HIEU_SLOP = re.compile(r'(lorem ipsum|TODO|TBD|\[điền[^\]]*\]|~~[a-z]|<chèn|xx\.xxx|as an ai|là một mô hình ngôn ngữ)', re.I)
CAM_DONG_GOI = ['*.env', '.env*', '*cookie*', '*.pem', '*.key', 'token*.json', '*.khoa-bi-mat']
MAU_BI_MAT = re.compile(r'(sk-ant-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{32,}|AIza[0-9A-Za-z_-]{35}|ghp_[A-Za-z0-9]{36}|-----BEGIN [A-Z ]*PRIVATE KEY-----)')


class Loi(Exception):
    pass


# ---------- tiện ích ----------
def doc_json(p, mac_dinh=None):
    if not os.path.exists(p):
        return mac_dinh
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def ghi_json(p, d):
    os.makedirs(os.path.dirname(p) or '.', exist_ok=True)
    tam = p + '.tam'
    with open(tam, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tam, p)


def them_dong(p, d):
    os.makedirs(os.path.dirname(p) or '.', exist_ok=True)
    with open(p, 'a', encoding='utf-8') as f:
        f.write(json.dumps(d, ensure_ascii=False) + '\n')


def doc_dong(p):
    if not os.path.exists(p):
        return []
    with open(p, encoding='utf-8') as f:
        return [json.loads(x) for x in f if x.strip()]


def bay_gio():
    return time.strftime('%Y-%m-%dT%H:%M:%S')


def doc(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def ghi(p, t):
    os.makedirs(os.path.dirname(p) or '.', exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(t)


def tang_ban(v, muc='phu'):
    a, b, c = (int(x) for x in v.split('.'))
    return f'{a + 1}.0.0' if muc == 'chinh' else (f'{a}.{b + 1}.0' if muc == 'phu' else f'{a}.{b}.{c + 1}')


class WF:
    """Một workforce trên đĩa."""

    def __init__(self, goc):
        self.goc = os.path.abspath(goc)
        if not os.path.exists(self.p('workforce.json')):
            raise Loi(f'{goc}: không phải workforce (thiếu workforce.json)')
        self.cau_hinh = doc_json(self.p('workforce.json'))
        self.to_chuc = doc_json(self.p('to-chuc.json'), {'nguoi': [], 'cong_nhan': []})

    def p(self, *x):
        return os.path.join(self.goc, *x)

    # --- tra cứu ---
    def nguoi(self, ma):
        return next((n for n in self.to_chuc['nguoi'] if n['ma'] == ma), None)

    def cong_nhan(self, ma):
        return next((c for c in self.to_chuc['cong_nhan'] if c['ma'] == ma), None)

    def workflow(self, ten):
        d = doc_json(self.p('workflow', ten + '.json'))
        if d is None:
            raise Loi(f'không có workflow "{ten}"')
        return d

    def ds_workflow(self):
        d = self.p('workflow')
        return sorted(f[:-5] for f in os.listdir(d) if f.endswith('.json')) if os.path.isdir(d) else []

    def ds_skill(self):
        d = self.p('.agents', 'skills')
        return sorted(x for x in os.listdir(d) if os.path.isfile(os.path.join(d, x, 'SKILL.md'))) if os.path.isdir(d) else []

    def duong_dich(self, dich):
        loai, _, ten = dich.partition(':')
        if loai == 'skill':
            return self.p('.agents', 'skills', ten)
        if loai == 'workflow':
            return self.p('workflow', ten + '.json')
        if loai == 'cong-nhan':
            return self.p('cong-nhan', ten)
        if dich == 'he-thong':
            return self.p('AGENTS.md')
        raise Loi(f'đích "{dich}" không hợp lệ (skill:x | workflow:x | cong-nhan:x | he-thong)')

    # --- phiên bản ---
    def kenh(self):
        return doc_json(self.p('phat-hanh', 'kenh.json'), {})

    def ban(self, dich):
        return self.kenh().get(dich, {}).get('production', '1.0.0')

    # --- việc ---
    def viec(self, ma):
        d = doc_json(self.p('viec', ma, 'viec.json'))
        if d is None:
            raise Loi(f'không có việc {ma}')
        return d

    def ds_viec(self):
        d = self.p('viec')
        return [self.viec(x) for x in sorted(os.listdir(d)) if os.path.exists(os.path.join(d, x, 'viec.json'))] if os.path.isdir(d) else []

    def su_kien(self, su_kien, **kw):
        them_dong(self.p('bang-viec.jsonl'), {'luc': bay_gio(), 'su_kien': su_kien, **kw})

    def thong_bao(self, cho, noi_dung, viec=None):
        """Ghi hộp thư ra. Bộ chuyển (Zalo hub, email) đọc file này rồi gửi; lõi không tự gọi mạng."""
        n = self.nguoi(cho) or {}
        them_dong(self.p('hop-thu', 'ra.jsonl'), {'luc': bay_gio(), 'cho': cho, 'kenh': n.get('kenh', self.cau_hinh.get('kenh_mac_dinh', 'zalo')),
                                                 'dia_chi': n.get('dia_chi', ''), 'viec': viec, 'noi_dung': noi_dung, 'da_gui': False})

    def thong_ke(self):
        return doc_json(self.p('thong-ke.json'), {'cong_nhan': {}, 'skill': {}, 'workflow': {}})


# ---------- SETUP ----------
def lenh_moi(a):
    if os.path.exists(a.thu_muc) and os.listdir(a.thu_muc):
        raise Loi(f'{a.thu_muc} đã có nội dung, không ghi đè')
    shutil.copytree(KHUON, a.thu_muc, dirs_exist_ok=True)
    skills = [x for x in (a.skills or '').split(',') if x]
    mau = None
    if getattr(a, 'mau', None):
        goc_mau = os.path.join(getattr(a, 'bo_mau', None) or BO_MAU, a.mau)
        mau = doc_json(os.path.join(goc_mau, 'mau.json'))
        if mau is None:
            raise Loi(f'không có bộ mẫu "{a.mau}" (cần {goc_mau}/mau.json)')
        for r, _, fs in os.walk(goc_mau):
            for f in fs:
                rel = os.path.relpath(os.path.join(r, f), goc_mau)
                if rel == 'mau.json' or rel.split(os.sep)[0] in ('de-xuat', 'HOC-CHEO.md'):
                    continue
                dich = os.path.join(a.thu_muc, rel)
                os.makedirs(os.path.dirname(dich), exist_ok=True)
                shutil.copy2(os.path.join(r, f), dich)
        skills = list(dict.fromkeys(mau.get('skills', []) + skills))
    w_json = os.path.join(a.thu_muc, 'workforce.json')
    d = doc_json(w_json)
    d.update({'ten': a.ten, 'don_vi': a.don_vi, 'tao_luc': bay_gio()})
    if mau:
        d['mau'] = {'ten': mau['ten'], 'ban': mau['ban']}
        d['tieu_chuan'] = {**d.get('tieu_chuan', {}), **mau.get('tieu_chuan', {})}
    ghi_json(w_json, d)
    kenh = {}
    for s in skills:
        nguon = tim_skill(a.kho, s)
        shutil.copytree(nguon, os.path.join(a.thu_muc, '.agents', 'skills', s))
        kenh[f'skill:{s}'] = {'production': '1.0.0', 'truoc': [], 'nguon': os.path.relpath(nguon, a.kho).replace('\\', '/')}
    for f in os.listdir(os.path.join(a.thu_muc, 'workflow')):
        if f.endswith('.json'):
            kenh[f'workflow:{f[:-5]}'] = {'production': '1.0.0', 'truoc': []}
    for c in doc_json(os.path.join(a.thu_muc, 'to-chuc.json'))['cong_nhan']:
        kenh[f'cong-nhan:{c["ma"]}'] = {'production': '1.0.0', 'truoc': []}
    kenh['he-thong'] = {'production': '1.0.0', 'truoc': []}
    ghi_json(os.path.join(a.thu_muc, 'phat-hanh', 'kenh.json'), kenh)
    print(f'Đã dựng {a.thu_muc}. Bước tiếp: điền 00-D0-NHU-CAU.md, nạp 01-nguon → 02-wiki, sửa to-chuc.json, rồi `af.py kiem`.')


def lenh_nap_skill(a, w=None):
    """Nạp lại skill từ kho theo kenh.json (dùng khi chép khuôn mẫu từ repo, hoặc kéo bản kho mới về cho skill chưa sửa riêng)."""
    w = w or WF(a.thu_muc)
    nap = []
    for dich, k in w.kenh().items():
        if not dich.startswith('skill:') or not k.get('nguon'):
            continue
        d = w.duong_dich(dich)
        if os.path.exists(os.path.join(d, 'SKILL.md')):
            continue
        nguon = os.path.join(a.kho, k['nguon'])
        if not os.path.exists(os.path.join(nguon, 'SKILL.md')):
            raise Loi(f'{dich}: không thấy {nguon}')
        shutil.copytree(nguon, d)
        nap.append(dich)
    print(f'đã nạp: {nap or "không cần"}')
    return nap


def tim_skill(kho, ten):
    if not kho:
        raise Loi('cần --kho (thư mục skills của linhx-engine) để lấy skill')
    for r, dd, fs in os.walk(kho):
        if os.path.basename(r) == ten and 'SKILL.md' in fs:
            return r
    raise Loi(f'không thấy skill "{ten}" trong {kho}')


# ---------- RUNNING ----------
def lenh_giao(a, w=None):
    w = w or WF(a.thu_muc)
    wf = w.workflow(a.workflow)
    so = 1 + max([int(v['ma'].split('-')[1]) for v in w.ds_viec()] or [0])
    ma = f'{w.cau_hinh.get("tien_to", "LX")}-{so:04d}'
    buoc0 = wf['buoc'][0]
    viec = {'ma': ma, 'viec': a.viec, 'workflow': a.workflow, 'ban_workflow': w.ban(f'workflow:{a.workflow}'),
            'nguoi_giao': a.nguoi_giao, 'cong_nhan': buoc0['cong_nhan'], 'nguoi_duyet': wf['nguoi_duyet'],
            'trang_thai': 'cho', 'vong': 1, 'tao_luc': bay_gio(), 'xong_luc': None, 'tran_phut': wf.get('tran_phut', 40),
            'lich_su': [{'luc': bay_gio(), 'tu': None, 'den': 'cho', 'ai': a.nguoi_giao, 'ly_do': 'giao'}]}
    d = w.p('viec', ma)
    for x in ('dau-vao', 'dau-ra'):
        os.makedirs(os.path.join(d, x), exist_ok=True)
    tieu_chi = '\n'.join(f'- [ ] {t}' for t in wf.get('tieu_chi', []))
    buoc = '\n'.join(f'{i + 1}. **{b["id"]}** · {b["cong_nhan"]} · skill `{b.get("skill", "-")}` · {b.get("viec", "")} → `dau-ra/{b.get("dau_ra", "")}`'
                     for i, b in enumerate(wf['buoc']))
    ghi(os.path.join(d, 'TASK.md'), f"""# {ma}: {a.viec}

Workflow `{a.workflow}` v{viec['ban_workflow']} · người giao {a.nguoi_giao} · người duyệt {wf['nguoi_duyet']} · trần {viec['tran_phut']} phút

## Làm trong thư mục này
Chỉ đọc `dau-vao/`, wiki và skill được nêu; chỉ ghi vào `dau-ra/` và `nhat-ky.md`. Không gửi gì ra ngoài.
Trước khi làm: đọc `../../NHO.md`, `../../02-wiki/INDEX.md`, và các dòng `HOC` của đích liên quan (`af.py` đã chép dưới đây).

## Các bước
{buoc}

## Tiêu chí xong (đánh [x] từng dòng khi đã kiểm, kèm bằng chứng trong nhat-ky.md)
{tieu_chi}

## Bản vàng (chuẩn cao nhất đã chọn): đọc trước, làm ít nhất bằng
{chr(10).join('- `../../' + x + '`' for x in ds_vang(w, 'workflow:' + a.workflow)) or '- (chưa có: báo người duyệt)'}

## Bài học đang áp
{bai_hoc_cho(w, wf)}
""")
    ghi(os.path.join(d, 'nhat-ky.md'), f'# Nhật ký {ma}\n')
    ghi_json(os.path.join(d, 'viec.json'), viec)
    w.su_kien('giao', viec=ma, workflow=a.workflow, ai=a.nguoi_giao)
    w.thong_bao(a.nguoi_giao, f'Em nhận, mã {ma}: {a.viec}', ma)
    print(ma)
    return ma


def ds_vang(w, dich):
    d = w.p('vang', dich.replace(':', '-'))
    return sorted(os.path.relpath(os.path.join(d, f), w.goc).replace('\\', '/') for f in os.listdir(d) if '.khong-dat' not in f) if os.path.isdir(d) else []


def bai_hoc_cho(w, wf):
    dich = {f'workflow:{wf["ten"]}', 'he-thong'} | {f'skill:{b["skill"]}' for b in wf['buoc'] if b.get('skill')} \
        | {f'cong-nhan:{b["cong_nhan"]}' for b in wf['buoc']}
    ds = [h for h in doc_dong(w.p('HOC.jsonl')) if h['dich'] in dich and h['trang_thai'] in ('mo', 'de_xuat')]
    return '\n'.join(f'- [{h["id"]}] ({h["dich"]}, +{h["ung_ho"]}/-{h["phan_doi"]}) {h["noi_dung"]}' for h in ds) or '- (chưa có)'


def kiem_dau_ra(w, ma):
    """Cổng chống slop trước khi trình duyệt: có sản phẩm thật, tiêu chí đã đánh dấu, không dấu hiệu làm dở."""
    d = w.p('viec', ma)
    loi = []
    ra = [os.path.join(r, f) for r, _, fs in os.walk(os.path.join(d, 'dau-ra')) for f in fs]
    if not ra:
        loi.append('dau-ra/ trống')
    for f in ra:
        if os.path.getsize(f) == 0:
            loi.append(f'{os.path.relpath(f, d)} rỗng')
        elif f.endswith(('.md', '.txt', '.html', '.json', '.csv')):
            m = DAU_HIEU_SLOP.search(doc(f))
            if m:
                loi.append(f'{os.path.relpath(f, d)} còn dấu hiệu làm dở: "{m.group(0)}"')
    task = doc(os.path.join(d, 'TASK.md'))
    chua = re.findall(r'^- \[ \] (.+)$', task, re.M)
    loi += [f'tiêu chí chưa kiểm: {t}' for t in chua]
    if len(doc(os.path.join(d, 'nhat-ky.md')).strip().splitlines()) < 2:
        loi.append('nhat-ky.md chưa ghi bằng chứng')
    return loi


def lenh_chuyen(a, w=None):
    w = w or WF(a.thu_muc)
    v = w.viec(a.ma)
    tu, den = v['trang_thai'], a.den
    if den not in CHUYEN.get(tu, set()):
        raise Loi(f'{a.ma}: không chuyển được {tu} → {den}')
    if den == 'cho_duyet':
        loi = kiem_dau_ra(w, a.ma)
        if loi:
            raise Loi(f'{a.ma} chưa trình duyệt được:\n  ' + '\n  '.join(loi))
    if den in ('xong', 'tra_lai'):
        if a.ai != v['nguoi_duyet'] and not (w.nguoi(a.ai) or {}).get('vai') == 'chu':
            raise Loi(f'{a.ma}: chỉ {v["nguoi_duyet"]} hoặc chủ được duyệt/trả')
        if den == 'tra_lai' and not a.ly_do:
            raise Loi('trả lại phải có --ly-do (lý do thành bài học)')
    v['trang_thai'] = den
    v['lich_su'].append({'luc': bay_gio(), 'tu': tu, 'den': den, 'ai': a.ai, 'ly_do': a.ly_do})
    tk = w.thong_ke()
    cn = tk['cong_nhan'].setdefault(v['cong_nhan'], {'dat_lan_dau': 0, 'xong': 0, 'tra_lai': 0})
    wfk = tk['workflow'].setdefault(v['workflow'], {'xong': 0, 'tra_lai': 0, 'phut': []})
    if den == 'tra_lai':
        v['vong'] += 1
        cn['tra_lai'] += 1
        wfk['tra_lai'] += 1
        ghi_phan_hoi(w, f'workflow:{v["workflow"]}', 'xau', a.ly_do, a.ma, a.ai)
        w.thong_bao(v['nguoi_giao'], f'{a.ma} bị trả lại vòng {v["vong"] - 1}: {a.ly_do}', a.ma)
    if den == 'xong':
        v['xong_luc'] = bay_gio()
        cn['xong'] += 1
        cn['dat_lan_dau'] += v['vong'] == 1
        wfk['xong'] += 1
        wfk['phut'].append(round((time.mktime(time.strptime(v['xong_luc'], '%Y-%m-%dT%H:%M:%S'))
                                  - time.mktime(time.strptime(v['tao_luc'], '%Y-%m-%dT%H:%M:%S'))) / 60, 1))
        w.thong_bao(v['nguoi_giao'], f'{a.ma} xong, file trong viec/{a.ma}/dau-ra', a.ma)
    if den == 'cho_duyet':
        w.thong_bao(v['nguoi_duyet'], f'{a.ma} chờ anh/chị duyệt: {v["viec"]}', a.ma)
    ghi_json(w.p('thong-ke.json'), tk)
    ghi_json(w.p('viec', a.ma, 'viec.json'), v)
    w.su_kien('chuyen', viec=a.ma, tu=tu, den=den, ai=a.ai, ly_do=a.ly_do)
    print(f'{a.ma}: {tu} → {den}')


def lenh_bang(a, w=None):
    w = w or WF(a.thu_muc)
    ds = w.ds_viec()
    dong = [f'# Bảng việc · {w.cau_hinh["ten"]} ({w.cau_hinh["don_vi"]})', '']
    for t in TRANG_THAI:
        nhom = [v for v in ds if v['trang_thai'] == t]
        if nhom:
            dong.append(f'## {t} ({len(nhom)})')
            dong += [f'- {v["ma"]} · {v["viec"]} · {v["cong_nhan"]} → duyệt {v["nguoi_duyet"]} · vòng {v["vong"]}' for v in nhom]
    xong = [v for v in ds if v['trang_thai'] == 'xong']
    if ds:
        dong += ['', f'Xong {len(xong)}/{len(ds)} · đạt lần đầu {sum(v["vong"] == 1 for v in xong)}/{len(xong) or 1}'
                     f' · bài học mở {sum(h["trang_thai"] == "mo" for h in doc_dong(w.p("HOC.jsonl")))}'
                     f' · đề xuất chờ duyệt {len(ds_de_xuat(w, "cho_duyet"))}']
    van_ban = '\n'.join(dong)
    if getattr(a, 'html', None):
        ghi(a.html, '<!doctype html><meta charset="utf-8"><title>Bảng việc</title><pre style="font:15px/1.5 system-ui;max-width:860px;margin:24px auto;white-space:pre-wrap">'
            + html.escape(van_ban) + '</pre>')
    print(van_ban)
    return van_ban


# ---------- LEARNING ----------
def chuan_hoa(t):
    return re.sub(r'\s+', ' ', t.lower()).strip()


def ghi_phan_hoi(w, dich, loai, noi_dung, viec=None, ai=None, nhan=None):
    """Mỗi phản hồi thành bullet ACE trong HOC.jsonl. Ý giống bullet cũ (≥ 0,75) thì cộng dồn, không thêm dòng."""
    w.duong_dich(dich)
    ds = doc_dong(w.p('HOC.jsonl'))
    tot = loai == 'tot'
    gan = None
    for h in ds:
        if h['dich'] == dich and h['trang_thai'] in ('mo', 'de_xuat') and \
                difflib.SequenceMatcher(None, chuan_hoa(h['noi_dung']), chuan_hoa(noi_dung)).ratio() >= 0.75:
            gan = h
            break
    if gan is None:
        gan = {'id': f'H{len(ds) + 1:03d}', 'dich': dich, 'loai': loai, 'noi_dung': noi_dung, 'ung_ho': 0, 'phan_doi': 0,
               'bang_chung': [], 'trang_thai': 'mo', 'tao_luc': bay_gio()}
        ds.append(gan)
    gan['ung_ho' if (tot == (gan['loai'] == 'tot')) else 'phan_doi'] += 1
    gan['bang_chung'].append({'viec': viec, 'ai': ai, 'luc': bay_gio(), 'loai': loai, 'noi_dung': noi_dung, 'nhan': nhan})
    ghi_lai_hoc(w, ds)
    w.su_kien('phan_hoi', dich=dich, loai=loai, viec=viec, ai=ai, bai_hoc=gan['id'], nhan=nhan)
    return gan['id']


def ghi_lai_hoc(w, ds):
    tam = w.p('HOC.jsonl.tam')
    with open(tam, 'w', encoding='utf-8') as f:
        f.writelines(json.dumps(h, ensure_ascii=False) + '\n' for h in ds)
    os.replace(tam, w.p('HOC.jsonl'))
    dong = ['# Điều cần học (sinh từ HOC.jsonl, đừng sửa tay)', '']
    for t in ('mo', 'de_xuat', 'da_ap', 'tia'):
        nhom = [h for h in ds if h['trang_thai'] == t]
        if nhom:
            dong.append(f'## {t}')
            dong += [f'- [{h["id"]}] {h["dich"]} · +{h["ung_ho"]}/-{h["phan_doi"]} · {h["noi_dung"]}' for h in nhom]
    ghi(w.p('HOC.md'), '\n'.join(dong) + '\n')


def lenh_phan_hoi(a, w=None):
    w = w or WF(a.thu_muc)
    if a.loai not in ('tot', 'xau'):
        raise Loi('--loai là tot hoặc xau')
    print(ghi_phan_hoi(w, a.dich, a.loai, a.noi_dung, a.viec, a.ai, getattr(a, 'nhan', None)))


def lenh_vang(a, w=None):
    """Thêm một bản vàng: sản phẩm tốt nhất đã thấy (của người giỏi nhất, skill tốt nhất, hoặc việc được khen), kèm nguồn và vì sao vàng."""
    w = w or WF(a.thu_muc)
    w.duong_dich(a.dich)
    if not os.path.exists(a.tep):
        raise Loi(f'không thấy {a.tep}')
    if not a.nguon or not a.vi_sao:
        raise Loi('bản vàng phải có --nguon và --vi-sao (đo được: điểm nào hơn bài thường)')
    d = w.p('vang', a.dich.replace(':', '-'))
    os.makedirs(d, exist_ok=True)
    dich = os.path.join(d, os.path.basename(a.tep))
    shutil.copy2(a.tep, dich)
    them_dong(w.p('vang', 'NGUON.jsonl'), {'luc': bay_gio(), 'dich': a.dich, 'tep': os.path.relpath(dich, w.goc).replace('\\', '/'),
                                           'nguon': a.nguon, 'vi_sao': a.vi_sao, 'ai': a.ai})
    w.su_kien('vang', dich=a.dich, nguon=a.nguon)
    print(os.path.relpath(dich, w.goc))


def lenh_hoc_ngoai(a, w=None):
    """Bài học rút từ chuẩn ngoài (skill tốt nhất, người tiêu chuẩn cao nhất). Mỗi nguồn là một bằng chứng; hai nguồn độc lập cùng ý thì thành đề xuất."""
    w = w or WF(a.thu_muc)
    if not a.nguon:
        raise Loi('học ngoài phải có --nguon (URL, repo:đường dẫn, tên người + tác phẩm)')
    print(ghi_phan_hoi(w, a.dich, 'tot', a.noi_dung, f'NGOAI:{a.nguon}', a.ai or 'chuan-ngoai', 'chuan-ngoai'))


def lenh_ban_sua(a, w=None):
    """Học từ bản sửa của người giỏi: bản người sửa thành bản vàng của workflow, bản thợ giữ làm phản ví dụ, mỗi luật rút ra thành bài học."""
    w = w or WF(a.thu_muc)
    v = w.viec(a.viec)
    if not a.luat:
        raise Loi('phải rút ít nhất 1 --luat từ chỗ người sửa (vì sao bản sửa hơn)')
    for f in (a.ban_tho, a.ban_nguoi):
        if not os.path.exists(f):
            raise Loi(f'không thấy {f}')
    dich = f'workflow:{v["workflow"]}'
    d = w.p('vang', dich.replace(':', '-'))
    os.makedirs(d, exist_ok=True)
    duoi = os.path.splitext(a.ban_nguoi)[1] or '.md'
    shutil.copy2(a.ban_nguoi, os.path.join(d, f'{a.viec}-ban-sua-{a.ai}{duoi}'))
    shutil.copy2(a.ban_tho, os.path.join(d, f'{a.viec}-ban-tho.khong-dat{os.path.splitext(a.ban_tho)[1] or ".md"}'))
    giong = difflib.SequenceMatcher(None, doc(a.ban_tho), doc(a.ban_nguoi)).ratio()
    them_dong(w.p('vang', 'NGUON.jsonl'), {'luc': bay_gio(), 'dich': dich, 'tep': f'{a.viec}-ban-sua-{a.ai}{duoi}', 'nguon': f'bản sửa của {a.ai}',
                                           'vi_sao': '; '.join(a.luat), 'giong_ban_tho': round(giong, 2)})
    ids = [ghi_phan_hoi(w, dich, 'xau', l, a.viec, a.ai, 'ban-sua') for l in a.luat]
    print(f'bản sửa giống bản thợ {giong:.0%}; bài học {", ".join(ids)}')
    return ids


def lenh_nho(a, w=None):
    w = w or WF(a.thu_muc)
    p = w.p('NHO.md')
    cu = doc(p)
    moi = cu.rstrip('\n') + f'\n- {a.noi_dung}\n'
    if len(moi) > TRAN_NHO:
        raise Loi(f'NHO.md sẽ vượt {TRAN_NHO} ký tự ({len(moi)}). Gộp các dòng cũ cho gọn trước, rồi thêm.')
    ghi(p, moi)
    w.su_kien('nho', noi_dung=a.noi_dung)
    print(f'NHO.md {len(moi)}/{TRAN_NHO} ký tự')


def ds_de_xuat(w, trang_thai=None):
    d = w.p('de-xuat')
    ds = [doc_json(os.path.join(d, x, 'de-xuat.json')) for x in sorted(os.listdir(d))] if os.path.isdir(d) else []
    return [x for x in ds if x and (trang_thai is None or x['trang_thai'] == trang_thai)]


def lenh_hoc(a, w=None):
    """LEARNING: bài học đủ bằng chứng thành đề xuất sửa; bài học bị phản đối nhiều thì tỉa."""
    w = w or WF(a.thu_muc)
    nguong = w.cau_hinh.get('nguong_de_xuat', 2)
    ds = doc_dong(w.p('HOC.jsonl'))
    moi, tia = [], []
    for h in ds:
        if h['trang_thai'] != 'mo':
            continue
        if h['phan_doi'] >= 2 and h['phan_doi'] >= h['ung_ho']:
            h['trang_thai'] = 'tia'
            tia.append(h['id'])
            continue
        so_viec = len({b['viec'] or b['luc'] for b in h['bang_chung'] if b['loai'] == h['loai']})
        if h['ung_ho'] >= nguong and so_viec >= nguong:
            ma = f'DX-{len(ds_de_xuat(w)) + 1:03d}'
            d = w.p('de-xuat', ma)
            os.makedirs(os.path.join(d, 'moi'), exist_ok=True)
            duong = os.path.relpath(w.duong_dich(h['dich']), w.goc).replace('\\', '/')
            ghi(os.path.join(d, 'DE-XUAT.md'), f"""# {ma}: sửa {h['dich']} theo bài học {h['id']}

Bài học: {h['noi_dung']} (+{h['ung_ho']}/-{h['phan_doi']})
Bằng chứng: {', '.join(str(b['viec']) for b in h['bang_chung'])}
Đích: `{duong}` (đang v{w.ban(h['dich'])})

## Thợ (Claude/agy) làm
1. Chép `{duong}` vào `moi/` giữ nguyên đường dẫn tương đối, rồi sửa NHỎ NHẤT có thể (patch, không viết lại). Ghi lý do cạnh luật mới.
2. Chạy bộ thử `thu/{h['dich'].replace(':', '-')}.jsonl` (nếu chưa có thì thêm ít nhất 1 ca từ bằng chứng trên) với bản CŨ và bản MỚI.
3. Ghi `ket-qua-thu.json`: {{"tong": N, "dat_moi": n1, "dat_cu": n0, "nguoi_cham": "<không phải thợ>"}}.
4. Không tự thăng cấp. Chờ `af.py thang-cap {ma} --duyet <chủ>`.
""")
            ghi_json(os.path.join(d, 'de-xuat.json'), {'ma': ma, 'bai_hoc': h['id'], 'dich': h['dich'], 'trang_thai': 'cho_sua',
                                                       'tao_luc': bay_gio(), 'ban_cu': w.ban(h['dich'])})
            h['trang_thai'] = 'de_xuat'
            moi.append(ma)
    ghi_lai_hoc(w, ds)
    # đề xuất đã có bản sửa + kết quả thử thì chuyển sang chờ duyệt
    for dx in ds_de_xuat(w, 'cho_sua'):
        d = w.p('de-xuat', dx['ma'])
        if os.listdir(os.path.join(d, 'moi')) and os.path.exists(os.path.join(d, 'ket-qua-thu.json')):
            dx['trang_thai'] = 'cho_duyet'
            ghi_json(os.path.join(d, 'de-xuat.json'), dx)
            w.thong_bao(w.cau_hinh['chu'], f'{dx["ma"]}: đề xuất sửa {dx["dich"]} chờ anh duyệt', None)
    w.su_kien('hoc', de_xuat=moi, tia=tia)
    print(f'đề xuất mới: {moi or "không"} · tỉa: {tia or "không"}')
    return moi


# ---------- UPDATE ----------
def lenh_thang_cap(a, w=None):
    w = w or WF(a.thu_muc)
    d = w.p('de-xuat', a.ma)
    dx = doc_json(os.path.join(d, 'de-xuat.json'))
    if dx is None:
        raise Loi(f'không có đề xuất {a.ma}')
    if (w.nguoi(a.duyet) or {}).get('vai') not in ('chu', 'quan_ly'):
        raise Loi(f'{a.duyet} không có quyền duyệt thăng cấp (cần vai chu hoặc quan_ly)')
    kq = doc_json(os.path.join(d, 'ket-qua-thu.json'))
    if not kq:
        raise Loi('chưa có ket-qua-thu.json: phải chạy bộ thử bản cũ và bản mới trước')
    if kq.get('nguoi_cham') in (None, '', 'tho'):
        raise Loi('kết quả thử phải có người chấm khác thợ')
    if kq['dat_moi'] < kq['tong'] or kq['dat_moi'] < kq.get('dat_cu', 0):
        raise Loi(f'bản mới đạt {kq["dat_moi"]}/{kq["tong"]} (cũ {kq.get("dat_cu")}): hồi quy phải đạt hết và không kém bản cũ')
    if not os.listdir(os.path.join(d, 'moi')):
        raise Loi('moi/ trống')
    dich = dx['dich']
    kenh = w.kenh()
    k = kenh.setdefault(dich, {'production': '1.0.0', 'truoc': []})
    cu = k['production']
    luu_ban(w, dich, cu)
    for r, _, fs in os.walk(os.path.join(d, 'moi')):
        for f in fs:
            nguon = os.path.join(r, f)
            dich_f = w.p(os.path.relpath(nguon, os.path.join(d, 'moi')))
            os.makedirs(os.path.dirname(dich_f), exist_ok=True)
            shutil.copy2(nguon, dich_f)
    moi = tang_ban(cu, 'phu')
    k['truoc'].append(cu)
    k['production'] = moi
    ghi_json(w.p('phat-hanh', 'kenh.json'), kenh)
    them_dong(w.p('phat-hanh', 'CHANGELOG.jsonl'), {'luc': bay_gio(), 'dich': dich, 'tu': cu, 'den': moi, 'de_xuat': a.ma,
                                                    'bai_hoc': dx['bai_hoc'], 'duyet': a.duyet, 'thu': kq})
    ds = doc_dong(w.p('HOC.jsonl'))
    for h in ds:
        if h['id'] == dx['bai_hoc']:
            h['trang_thai'] = 'da_ap'
            h['ap_vao'] = f'{dich}@{moi}'
    ghi_lai_hoc(w, ds)
    dx.update({'trang_thai': 'da_ap', 'ban_moi': moi, 'duyet': a.duyet})
    ghi_json(os.path.join(d, 'de-xuat.json'), dx)
    w.su_kien('thang_cap', dich=dich, tu=cu, den=moi, ai=a.duyet)
    print(f'{dich}: {cu} → {moi}')


def luu_ban(w, dich, ban):
    nguon = w.duong_dich(dich)
    dich_d = w.p('phat-hanh', 'ban', dich.replace(':', '-'), ban)
    if os.path.exists(dich_d):
        return
    if os.path.isdir(nguon):
        shutil.copytree(nguon, dich_d)
    else:
        os.makedirs(dich_d)
        shutil.copy2(nguon, dich_d)


def lenh_lui(a, w=None):
    w = w or WF(a.thu_muc)
    kenh = w.kenh()
    k = kenh.get(a.dich)
    if not k or not k['truoc']:
        raise Loi(f'{a.dich} không có bản trước để lùi')
    hien, ve = k['production'], k['truoc'].pop()
    nguon = w.p('phat-hanh', 'ban', a.dich.replace(':', '-'), ve)
    luu_ban(w, a.dich, hien)
    dich_p = w.duong_dich(a.dich)
    if os.path.isdir(dich_p):
        shutil.rmtree(dich_p)
        shutil.copytree(nguon, dich_p)
    else:
        shutil.copy2(os.path.join(nguon, os.path.basename(dich_p)), dich_p)
    k['production'] = ve
    k.setdefault('bi_lui', []).append(hien)
    ghi_json(w.p('phat-hanh', 'kenh.json'), kenh)
    them_dong(w.p('phat-hanh', 'CHANGELOG.jsonl'), {'luc': bay_gio(), 'dich': a.dich, 'tu': hien, 'den': ve, 'lui': True, 'ly_do': a.ly_do})
    w.su_kien('lui', dich=a.dich, tu=hien, den=ve, ly_do=a.ly_do)
    print(f'{a.dich}: lùi {hien} → {ve}')


# ---------- cầu nối chat ----------
QUYEN = {'giao': {'chu', 'quan_ly', 'nhan_vien'}, 'gopy': {'chu', 'quan_ly', 'nhan_vien'}, 'bang': {'chu', 'quan_ly', 'nhan_vien'},
         'duyet': {'chu', 'quan_ly'}, 'tra': {'chu', 'quan_ly'}, 'nho': {'chu', 'quan_ly'}, 'help': {'chu', 'quan_ly', 'nhan_vien'}}


def lenh_lenh(a, w=None):
    """Dịch một tin chat thành lệnh. Quyền kiểm ở đây (trong code), không dựa lời dặn."""
    w = w or WF(a.thu_muc)
    n = w.nguoi(a.tu)
    t = a.tin.strip()
    m = re.match(r'^/(\w+)\s*(.*)$', t, re.S)
    if not m:
        return None  # không phải lệnh: để bên trả lời nhanh xử lý
    ten, con = m.group(1).lower(), m.group(2).strip()
    if n is None or n.get('vai') not in QUYEN.get(ten, set()):
        return 'Lệnh này cần quyền khác, em chuyển anh/chị phụ trách.' if n else None  # người lạ: im
    ns = argparse.Namespace
    if ten == 'help':
        return '/giao <workflow> <việc> · /gopy <LX-…|đích> <góp ý> · /duyet LX-… · /tra LX-… <lý do> · /bang · /nho <điều cần nhớ>'
    if ten == 'bang':
        return lenh_bang(ns(html=None), w)
    if ten == 'giao':
        wf, _, viec = con.partition(' ')
        if wf not in w.ds_workflow():
            return f'Chưa có workflow "{wf}". Đang có: {", ".join(w.ds_workflow())}'
        return f'Em nhận, mã {lenh_giao(ns(workflow=wf, viec=viec, nguoi_giao=a.tu), w)}'
    if ten in ('duyet', 'tra'):
        ma, _, ly_do = con.partition(' ')
        lenh_chuyen(ns(ma=ma, den='xong' if ten == 'duyet' else 'tra_lai', ai=a.tu, ly_do=ly_do or None), w)
        if ten == 'duyet' and ly_do:
            ghi_phan_hoi(w, f'workflow:{w.viec(ma)["workflow"]}', 'tot', ly_do, ma, a.tu)
        return f'{ma}: đã {"duyệt" if ten == "duyet" else "trả lại"}'
    if ten == 'gopy':
        dau, _, noi_dung = con.partition(' ')
        if re.match(r'^[A-Z]+-\d+$', dau):
            dich, viec = f'workflow:{w.viec(dau)["workflow"]}', dau
        else:
            dich, viec = dau, None
        return f'Em ghi bài học {ghi_phan_hoi(w, dich, "xau", noi_dung, viec, a.tu)}'
    if ten == 'nho':
        lenh_nho(ns(noi_dung=con), w)
        return 'Em nhớ rồi.'
    return None


# ---------- KIỂM ----------
def kiem(w):
    loi = []
    for f in ('AGENTS.md', 'CLAUDE.md', 'NHO.md', 'to-chuc.json', '02-wiki/INDEX.md', '02-wiki/su-that.json', '00-D0-NHU-CAU.md'):
        if not os.path.exists(w.p(f)):
            loi.append(f'thiếu {f}')
    if os.path.exists(w.p('NHO.md')) and len(doc(w.p('NHO.md'))) > TRAN_NHO:
        loi.append(f'NHO.md vượt {TRAN_NHO} ký tự')
    nguoi = {n['ma'] for n in w.to_chuc['nguoi']}
    cn = {c['ma']: c for c in w.to_chuc['cong_nhan']}
    if w.cau_hinh.get('chu') not in nguoi:
        loi.append('workforce.json: "chu" phải là một người trong to-chuc.json')
    for c in cn.values():
        if c.get('chiu_trach_nhiem') not in nguoi:
            loi.append(f'công nhân {c["ma"]}: chiu_trach_nhiem phải là người thật trong to-chuc.json')
        if c.get('bao_cao_cho') not in nguoi | set(cn):
            loi.append(f'công nhân {c["ma"]}: bao_cao_cho "{c.get("bao_cao_cho")}" không có')
        for f in ('ROLE.md', 'POLICIES.md', 'HEARTBEAT.md'):
            if not os.path.exists(w.p('cong-nhan', c['ma'], f)):
                loi.append(f'thiếu cong-nhan/{c["ma"]}/{f}')
    for c in cn:  # vòng báo cáo
        thay, x = set(), c
        while x in cn:
            if x in thay:
                loi.append(f'vòng báo cáo ở {c}')
                break
            thay.add(x)
            x = cn[x].get('bao_cao_cho')
    skills = set(w.ds_skill())
    for ten in w.ds_workflow():
        wf = w.workflow(ten)
        if wf.get('ten') != ten:
            loi.append(f'workflow/{ten}.json: "ten" phải là {ten}')
        if wf.get('nguoi_duyet') not in nguoi:
            loi.append(f'workflow {ten}: người duyệt phải là người thật')
        if not wf.get('tieu_chi'):
            loi.append(f'workflow {ten}: thiếu tieu_chi (định nghĩa xong)')
        if not wf.get('vi_du'):
            loi.append(f'workflow {ten}: thiếu vi_du (câu người dùng hay nói, để định tuyến)')
        for b in wf.get('buoc', []):
            if b.get('cong_nhan') not in cn:
                loi.append(f'workflow {ten} bước {b.get("id")}: công nhân "{b.get("cong_nhan")}" không có')
            if b.get('skill') and b['skill'] not in skills:
                loi.append(f'workflow {ten} bước {b.get("id")}: skill "{b["skill"]}" chưa có trong .agents/skills')
    try:
        st = doc_json(w.p('02-wiki', 'su-that.json'), {})
        if 'chot' not in st:
            loi.append('su-that.json thiếu mục "chot"')
    except ValueError as e:
        loi.append(f'su-that.json hỏng: {e}')
    for r, _, fs in os.walk(w.goc):
        if os.sep + 'phat-hanh' + os.sep + 'ban' in r:
            continue
        for f in fs:
            fp = os.path.join(r, f)
            if any(fnmatch.fnmatch(f.lower(), x) for x in CAM_DONG_GOI) and not f.endswith('.mau'):
                loi.append(f'{os.path.relpath(fp, w.goc)}: file bí mật không được nằm trong workforce')
            elif f.endswith(('.md', '.json', '.jsonl', '.py', '.txt')) and os.path.getsize(fp) < 2 * 2**20:
                if MAU_BI_MAT.search(doc(fp)):
                    loi.append(f'{os.path.relpath(fp, w.goc)}: có chuỗi giống khoá API')
    return loi


def lenh_kiem(a):
    loi = kiem(WF(a.thu_muc))
    print('DAT' if not loi else 'CHUA_DAT\n' + '\n'.join('- ' + x for x in loi))
    return 0 if not loi else 1


# ---------- TIÊU CHUẨN 3 MỨC ----------
def d0_tra_loi(w):
    """D0 đã trả lời: mỗi câu có dòng '> ...' ngay sau, không còn '> (chưa'."""
    t = doc(w.p('00-D0-NHU-CAU.md')) if os.path.exists(w.p('00-D0-NHU-CAU.md')) else ''
    tl = [x for x in re.findall(r'^>\s*(.+)$', t, re.M) if x.strip()]
    return len([x for x in tl if not re.match(r'\(?chưa', x.strip(), re.I)]), len(tl)


def ket_qua_thu_moi(w):
    d = w.p('thu', 'ket-qua')
    fs = sorted(f for f in os.listdir(d) if f.endswith('.json')) if os.path.isdir(d) else []
    return doc_json(os.path.join(d, fs[-1])) if fs else None


def muc(w):
    """Chấm mức: 1 = mở được nhóm, 2 = đạt 14 ngày. Mức 3 (thành bộ mẫu) chấm trên nhiều đơn vị bằng `muc --mau`."""
    tc = w.cau_hinh.get('tieu_chuan', {})
    t1, t2 = tc.get('m1', {}), tc.get('m2', {})
    m1, m2 = [], []
    loi = kiem(w)
    m1.append(('kiem cấu trúc DAT (người chịu trách nhiệm, người duyệt, tiêu chí, câu ví dụ, không bí mật)', not loi, '; '.join(loi[:3])))
    da, tong = d0_tra_loi(w)
    m1.append(('D0 trả lời đủ 7 câu', da >= 7, f'{da}/7 (dòng "> " sau mỗi câu)'))
    ca = sum(len(doc_dong(w.p('thu', f))) for f in os.listdir(w.p('thu')) if f.endswith('.jsonl')) if os.path.isdir(w.p('thu')) else 0
    m1.append((f'bộ thử ≥ {t1.get("ca_thu_toi_thieu", 10)} ca thật', ca >= t1.get('ca_thu_toi_thieu', 10), f'{ca} ca'))
    kq = ket_qua_thu_moi(w)
    m1.append(('lần thử gần nhất đạt hết, người chấm khác thợ', bool(kq) and kq.get('dat') == kq.get('tong') and kq.get('nguoi_cham') not in (None, '', 'tho'),
               f'{kq.get("dat")}/{kq.get("tong")}' if kq else 'chưa có thu/ket-qua/*.json'))
    thieu_vang = [t for t in w.ds_workflow() if t != 'viec-chung' and not ds_vang(w, 'workflow:' + t)]
    m1.append(('mỗi workflow có ≥ 1 bản vàng có nguồn', not thieu_vang, 'thiếu: ' + ', '.join(thieu_vang) if thieu_vang else 'đủ'))
    gioi = t1.get('tra_loi_nhanh_giay', 60)
    m1.append((f'trả lời nhanh ≤ {gioi} giây (trung vị)', bool(kq) and (kq.get('giay_trung_vi') or 1e9) <= gioi,
               f'{kq.get("giay_trung_vi")} giây' if kq else '-'))
    ngay = t2.get('ngay', 14)
    moc = time.time() - ngay * 86400
    ds = [v for v in w.ds_viec() if time.mktime(time.strptime(v['tao_luc'], '%Y-%m-%dT%H:%M:%S')) >= moc]
    xong = [v for v in ds if v['trang_thai'] == 'xong']
    m2.append((f'≥ {t2.get("viec_toi_thieu", 20)} việc trong {ngay} ngày', len(ds) >= t2.get('viec_toi_thieu', 20), f'{len(ds)} việc'))
    ti_le = len(xong) / len(ds) if ds else 0
    m2.append((f'≥ {int(t2.get("ti_le_xong", .65) * 100)}% xong', ds and ti_le >= t2.get('ti_le_xong', .65), f'{ti_le:.0%}'))
    nguoi = {v['nguoi_giao'] for v in ds if (w.nguoi(v['nguoi_giao']) or {}).get('vai') != 'chu'}
    m2.append((f'≥ {t2.get("nguoi_dung_toi_thieu", 2)} người ngoài chủ giao việc', len(nguoi) >= t2.get('nguoi_dung_toi_thieu', 2), ', '.join(sorted(nguoi)) or '-'))
    cam = set(t2.get('nhan_cam', ['bia', 'lo-noi-bo']))
    nang = [b for h in doc_dong(w.p('HOC.jsonl')) for b in h['bang_chung']
            if b.get('nhan') in cam and time.mktime(time.strptime(b['luc'], '%Y-%m-%dT%H:%M:%S')) >= moc]
    m2.append(('0 lỗi nặng (bịa số, lộ nội bộ)', not nang, f'{len(nang)} lỗi'))
    dat1 = all(x[1] for x in m1)
    dat2 = dat1 and all(x[1] for x in m2)
    return {'muc': 2 if dat2 else 1 if dat1 else 0, 'm1': m1, 'm2': m2}


def lenh_muc(a):
    if a.mau:
        ds = [WF(x) for x in a.thu_muc]
        cung = [w for w in ds if w.cau_hinh.get('mau', {}).get('ten') == a.mau]
        dat = [w for w in cung if muc(w)['muc'] >= 2]
        can = (doc_json(os.path.join(a.bo_mau or BO_MAU, a.mau, 'mau.json')) or {}).get('tieu_chuan', {}).get('m3', {}).get('don_vi_toi_thieu', 2)
        print(f'Bộ mẫu {a.mau}: {len(dat)}/{len(cung)} đơn vị đạt mức 2 (cần {can}) → {"MỨC 3: dùng làm mẫu cho đơn vị sau" if len(dat) >= can else "chưa mức 3"}')
        return 0 if len(dat) >= can else 1
    w = WF(a.thu_muc[0])
    r = muc(w)
    print(f'{w.cau_hinh["ten"]}: MỨC {r["muc"]}')
    for nhom, ten in (('m1', 'Mức 1 · mở được nhóm'), ('m2', 'Mức 2 · đạt 14 ngày')):
        print(ten)
        for dieu, dat, ct in r[nhom]:
            print(f'  {"✓" if dat else "✗"} {dieu} ({ct})')
    return 0 if r['muc'] >= 1 else 1


def lenh_hoc_cheo(a):
    """Gom bài học xuyên đơn vị: cùng đích, ý giống nhau, ở ≥ N đơn vị cùng bộ mẫu → đề xuất sửa bộ mẫu (duyệt qua PR repo)."""
    goc_mau = os.path.join(a.bo_mau or BO_MAU, a.mau)
    if not os.path.exists(os.path.join(goc_mau, 'mau.json')):
        raise Loi(f'không có bộ mẫu {a.mau}')
    nhom = []  # [{dich, noi_dung, don_vi:set, id:[...]}]
    for x in a.thu_muc:
        w = WF(x)
        if w.cau_hinh.get('mau', {}).get('ten') != a.mau:
            continue
        for h in doc_dong(w.p('HOC.jsonl')):
            if h['trang_thai'] == 'tia':
                continue
            for g in nhom:
                if g['dich'] == h['dich'] and difflib.SequenceMatcher(None, chuan_hoa(g['noi_dung']), chuan_hoa(h['noi_dung'])).ratio() >= 0.6:
                    g['don_vi'].add(w.cau_hinh['don_vi']); g['id'].append(f'{w.cau_hinh["don_vi"]}:{h["id"]}')
                    break
            else:
                nhom.append({'dich': h['dich'], 'noi_dung': h['noi_dung'], 'don_vi': {w.cau_hinh['don_vi']}, 'id': [f'{w.cau_hinh["don_vi"]}:{h["id"]}']})
    du = [g for g in nhom if len(g['don_vi']) >= a.nguong]
    dong = [f'# Bài học xuyên đơn vị · bộ mẫu {a.mau} ({bay_gio()})', '',
            f'Bài học có ở ≥ {a.nguong} đơn vị. Designer sửa file tương ứng trong bộ mẫu bằng một PR; Linh duyệt PR là duyệt thăng cấp bộ mẫu.', '']
    dong += [f'- {g["dich"]} · {len(g["don_vi"])} đơn vị ({", ".join(sorted(g["don_vi"]))}) · {g["noi_dung"]} · [{", ".join(g["id"])}]' for g in du] or ['- (chưa có)']
    ghi(os.path.join(goc_mau, 'HOC-CHEO.md'), '\n'.join(dong) + '\n')
    print(f'{len(du)} bài học đủ ngưỡng → {os.path.join(goc_mau, "HOC-CHEO.md")}')
    return du


# ---------- ĐÓNG GÓI ----------
def lenh_dong_goi(a):
    w = WF(a.thu_muc)
    loi = kiem(w)
    if loi:
        raise Loi('kiem chưa đạt, không đóng gói:\n  ' + '\n  '.join(loi))
    bo = ['hop-thu', 'phat-hanh/ban'] + ([] if a.kem_viec else ['viec', 'bang-viec.jsonl'])
    with zipfile.ZipFile(a.ra, 'w', zipfile.ZIP_DEFLATED) as z:
        for r, dd, fs in os.walk(w.goc):
            rel_r = os.path.relpath(r, w.goc).replace('\\', '/')
            dd[:] = [x for x in dd if not any((rel_r + '/' + x).lstrip('./') == b for b in bo)]
            for f in fs:
                rel = os.path.relpath(os.path.join(r, f), w.goc).replace('\\', '/')
                if rel in bo or f.endswith('.tam'):
                    continue
                z.write(os.path.join(r, f), rel)
        z.write(os.path.abspath(__file__), 'af.py')
    print(f'Đã đóng {a.ra}')
    if a.mot_file:
        ghi_mot_file(w, a.mot_file)


def ghi_mot_file(w, ra):
    """Một file markdown cho nơi không nhận zip (Gemini app/Gem, ChatGPT project): hiến chương + tổ chức + workflow + skill + nhớ/học."""
    phan = [f'# Workforce {w.cau_hinh["ten"]} ({w.cau_hinh["don_vi"]}) · gói một file', '',
            'Đọc từ trên xuống. Phần "AGENTS" là luật; làm việc nào thì theo đúng workflow và skill của việc đó.', '']
    them = lambda tieu_de, p: phan.extend([f'\n---\n## {tieu_de}\n', doc(p)]) if os.path.exists(p) else None
    them('AGENTS', w.p('AGENTS.md'))
    them('NHO (điều cần nhớ)', w.p('NHO.md'))
    them('HOC (điều cần học)', w.p('HOC.md'))
    them('Wiki INDEX', w.p('02-wiki', 'INDEX.md'))
    phan.extend(['\n---\n## su-that.json\n', '```json', doc(w.p('02-wiki', 'su-that.json')), '```'])
    phan.extend(['\n---\n## to-chuc.json\n', '```json', doc(w.p('to-chuc.json')), '```'])
    for c in w.to_chuc['cong_nhan']:
        for f in ('ROLE.md', 'POLICIES.md'):
            them(f'Công nhân {c["ma"]}: {f}', w.p('cong-nhan', c['ma'], f))
    for t in w.ds_workflow():
        phan.extend([f'\n---\n## Workflow {t}\n', '```json', doc(w.p('workflow', t + '.json')), '```'])
    for s in w.ds_skill():
        them(f'Skill {s}', w.p('.agents', 'skills', s, 'SKILL.md'))
    ghi(ra, '\n'.join(phan) + '\n')
    print(f'Đã ghi {ra} ({os.path.getsize(ra)} byte)')


# ---------- SERVER MỎNG ----------
def lenh_may_chu(a):
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    token = os.environ.get('AF_TOKEN', '')
    if len(token) < 16:
        raise Loi('đặt biến AF_TOKEN (≥ 16 ký tự) trước khi mở server')
    goc = a.thu_muc

    class H(BaseHTTPRequestHandler):
        def tra(self, ma, noi_dung, loai='text/plain; charset=utf-8'):
            b = noi_dung.encode('utf-8')
            self.send_response(ma)
            self.send_header('Content-Type', loai)
            self.send_header('Content-Length', str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def do_GET(self):
            if self.headers.get('X-Token') != token:
                return self.tra(401, 'cần X-Token')
            w = WF(goc)
            if self.path == '/bang.json':
                return self.tra(200, json.dumps([{k: v[k] for k in ('ma', 'viec', 'trang_thai', 'cong_nhan', 'nguoi_duyet', 'vong')}
                                                 for v in w.ds_viec()], ensure_ascii=False), 'application/json')
            if self.path == '/hop-thu':
                return self.tra(200, json.dumps([x for x in doc_dong(w.p('hop-thu', 'ra.jsonl')) if not x['da_gui']], ensure_ascii=False), 'application/json')
            return self.tra(200, lenh_bang(argparse.Namespace(html=None), w))

        def do_POST(self):
            if self.headers.get('X-Token') != token:
                return self.tra(401, 'cần X-Token')
            if self.path != '/lenh':
                return self.tra(404, 'chỉ có POST /lenh')
            try:
                d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))).decode('utf-8'))
                kq = lenh_lenh(argparse.Namespace(tu=d['tu'], tin=d['tin']), WF(goc))
                self.tra(200, json.dumps({'tra_loi': kq}, ensure_ascii=False), 'application/json')
            except (Loi, KeyError, ValueError) as e:
                self.tra(400, json.dumps({'loi': str(e)}, ensure_ascii=False), 'application/json')

        def log_message(self, *x):
            pass

    print(f'af may-chu: http://{a.host}:{a.cong} (GET / bảng, /bang.json, /hop-thu; POST /lenh {{"tu","tin"}})')
    ThreadingHTTPServer((a.host, a.cong), H).serve_forever()


# ---------- CLI ----------
def tao_parser():
    p = argparse.ArgumentParser(prog='af.py', description='Lõi LINHX Agent Force')
    s = p.add_subparsers(dest='lenh', required=True)
    x = s.add_parser('moi'); x.add_argument('thu_muc'); x.add_argument('--ten', required=True); x.add_argument('--don-vi', required=True)
    x.add_argument('--kho'); x.add_argument('--skills'); x.add_argument('--mau', help='bộ mẫu trong workforce/bo-mau'); x.add_argument('--bo-mau')
    x = s.add_parser('giao'); x.add_argument('thu_muc'); x.add_argument('--workflow', required=True); x.add_argument('--viec', required=True)
    x.add_argument('--nguoi-giao', default='chu')
    x = s.add_parser('chuyen'); x.add_argument('thu_muc'); x.add_argument('ma'); x.add_argument('den', choices=TRANG_THAI)
    x.add_argument('--ai', default='tho'); x.add_argument('--ly-do')
    x = s.add_parser('bang'); x.add_argument('thu_muc'); x.add_argument('--html')
    x = s.add_parser('phan-hoi'); x.add_argument('thu_muc'); x.add_argument('--dich', required=True); x.add_argument('--loai', required=True)
    x.add_argument('--noi-dung', required=True); x.add_argument('--viec'); x.add_argument('--ai')
    x.add_argument('--nhan', help='bia | lo-noi-bo | ... (lỗi nặng, chặn mức 2)')
    x = s.add_parser('nho'); x.add_argument('thu_muc'); x.add_argument('noi_dung')
    x = s.add_parser('vang'); x.add_argument('thu_muc'); x.add_argument('--dich', required=True); x.add_argument('--tep', required=True)
    x.add_argument('--nguon', required=True); x.add_argument('--vi-sao', required=True); x.add_argument('--ai')
    x = s.add_parser('ban-sua'); x.add_argument('thu_muc'); x.add_argument('--viec', required=True); x.add_argument('--ban-tho', required=True)
    x.add_argument('--ban-nguoi', required=True); x.add_argument('--ai', required=True); x.add_argument('--luat', action='append')
    x = s.add_parser('hoc-ngoai'); x.add_argument('thu_muc'); x.add_argument('--dich', required=True); x.add_argument('--nguon', required=True)
    x.add_argument('--noi-dung', required=True); x.add_argument('--ai')
    x = s.add_parser('hoc'); x.add_argument('thu_muc')
    x = s.add_parser('thang-cap'); x.add_argument('thu_muc'); x.add_argument('ma'); x.add_argument('--duyet', required=True)
    x = s.add_parser('lui'); x.add_argument('thu_muc'); x.add_argument('dich'); x.add_argument('--ly-do')
    x = s.add_parser('lenh'); x.add_argument('thu_muc'); x.add_argument('--tu', required=True); x.add_argument('tin')
    x = s.add_parser('nap-skill'); x.add_argument('thu_muc'); x.add_argument('--kho', required=True)
    x = s.add_parser('kiem'); x.add_argument('thu_muc')
    x = s.add_parser('muc'); x.add_argument('thu_muc', nargs='+'); x.add_argument('--mau'); x.add_argument('--bo-mau')
    x = s.add_parser('hoc-cheo'); x.add_argument('mau'); x.add_argument('thu_muc', nargs='+'); x.add_argument('--nguong', type=int, default=3)
    x.add_argument('--bo-mau')
    x = s.add_parser('dong-goi'); x.add_argument('thu_muc'); x.add_argument('ra'); x.add_argument('--kem-viec', action='store_true')
    x.add_argument('--mot-file')
    x = s.add_parser('may-chu'); x.add_argument('thu_muc'); x.add_argument('--cong', type=int, default=8120); x.add_argument('--host', default='127.0.0.1')
    return p


def main(argv=None):
    a = tao_parser().parse_args(argv)
    try:
        if a.lenh == 'kiem':
            return lenh_kiem(a)
        if a.lenh == 'muc':
            return lenh_muc(a)
        if a.lenh == 'hoc-cheo':
            lenh_hoc_cheo(a)
            return 0
        if a.lenh == 'lenh':
            kq = lenh_lenh(a)
            if kq:
                print(kq)
            return 0
        {'moi': lenh_moi, 'giao': lenh_giao, 'chuyen': lenh_chuyen, 'bang': lenh_bang, 'phan-hoi': lenh_phan_hoi, 'nho': lenh_nho, 'vang': lenh_vang, 'hoc-ngoai': lenh_hoc_ngoai, 'ban-sua': lenh_ban_sua,
         'hoc': lenh_hoc, 'thang-cap': lenh_thang_cap, 'lui': lenh_lui, 'nap-skill': lenh_nap_skill, 'dong-goi': lenh_dong_goi, 'may-chu': lenh_may_chu}[a.lenh](a)
        return 0
    except Loi as e:
        print(f'LOI: {e}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    sys.exit(main())
