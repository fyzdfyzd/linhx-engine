#!/usr/bin/env python3
"""tqa.py — kiểm thử thói quen viết của AI trên nhiều model (LAB080). Chỉ dùng thư viện chuẩn.

  run      : gửi cùng bộ đề cho nhiều model, lưu jsonl (chạy tiếp được, không gọi lại câu đã có)
  import   : nhập kho có sẵn (slop-forensics jsonl, thư mục .md/.txt của người)
  test     : chạy giả thuyết trên dữ liệu → bảng theo model, CI bootstrap, p hoán vị, kết luận
  explore  : tìm thói quen chưa ai nói (cụm mở đầu câu/bài đặc trưng mỗi model)
  check    : in vài chỗ khớp để người kiểm regex có bắt đúng không

Mỗi dòng dữ liệu: {"model": ..., "prompt_id": ..., "sample": 0, "output": ...}. Model "human" là mốc người.
"""
import argparse, collections, concurrent.futures as cf, hashlib, json, math, os, random, re, subprocess, sys, urllib.request
from pathlib import Path

WORD = re.compile(r"[^\W_]+(?:['’][^\W_]+)?", re.U)
CWD = __import__('tempfile').gettempdir()  # CLI chạy ở thư mục trống, không đọc CLAUDE.md/GEMINI.md của dự án
SENT = re.compile(r"(?<=[.!?…])[\"”’)\]]*\s+|\n+")


# ---------- đọc, tách ----------
def doc_jsonl(paths):
    for p in paths:
        for line in Path(p).read_text(encoding='utf-8').splitlines():
            if line.strip():
                yield json.loads(line)


META = re.compile(r"(?im)^(?:tác giả|ngày đăng|url|nguồn|ảnh|author|date|source)\s*:.*$|^\((?:dân trí|vnexpress)\)\s*[-–—]\s*")  # siêu dữ liệu bài báo
TIEU_DE = re.compile(r"(?im)^\s*(?:#{1,6}\s.*|\*\*[^*\n]+\*\*:?\s*|title\s*:.*|-{3,}|\*{3,})$")


def tach_cau(t):
    """Tách câu, bỏ dòng tiêu đề (markdown #, dòng in đậm đứng riêng, 'Title:'), bỏ ký hiệu gạch đầu dòng."""
    out = []
    for s in SENT.split(TIEU_DE.sub('', t)):
        s = re.sub(r"^\s*(?:[-*•>]|\d+[.)]|#+)\s*", "", s).strip(" *_")
        if WORD.search(s):
            out.append(s)
    return out


def so_chu(t):
    return len(WORD.findall(t))


# ---------- đo ----------
def do_regex(t, m):
    fl = 0
    for c in m.get('flags', ''):
        fl |= {'i': re.I, 'm': re.M, 's': re.S}[c]
    rx = re.compile(m['pattern'], fl)
    scope, unit = m.get('scope', 'text'), m.get('unit', 'per_1k_words')
    cau = tach_cau(t)
    if scope == 'text':
        doan = [t]
    elif scope == 'first_sentence':
        doan = cau[:1]
    elif scope == 'last_sentence':
        doan = cau[-1:]
    elif scope == 'sentence_start':
        doan = [' '.join(WORD.findall(c)[:4]) + ' ' for c in cau]
    else:
        raise SystemExit(f'scope lạ: {scope}')
    n = sum(len(rx.findall(d)) for d in doan)
    if unit == 'presence':
        return 1.0 if n else 0.0
    if unit == 'count':
        return float(n)
    if unit == 'per_sentence':
        return n / max(1, len(cau))
    return 1000 * n / max(1, so_chu(t))


def do_stat(t, m):
    name = m['name']
    cau = tach_cau(t)
    lens = [so_chu(c) for c in cau] or [0]
    if name == 'sentence_len_mean':
        return sum(lens) / len(lens)
    if name == 'sentence_len_cv':  # thấp = câu đều nhau
        mu = sum(lens) / len(lens)
        return (sum((x - mu) ** 2 for x in lens) / len(lens)) ** .5 / mu if mu else 0.0
    if name == 'words':
        return float(so_chu(t))
    if name == 'bullet_share':
        ln = [l for l in t.splitlines() if l.strip()]
        return sum(bool(re.match(r"\s*(?:[-*•]|\d+[.)])\s", l)) for l in ln) / max(1, len(ln))
    if name == 'heading_count':
        return float(len(re.findall(r"(?m)^#{1,6}\s", t)))
    if name == 'bold_per_1k':
        return 1000 * len(re.findall(r"\*\*[^*\n]+\*\*", t)) / max(1, so_chu(t))
    if name == 'opener_repeat':  # tỉ lệ câu mở bằng cùng chữ với câu ngay trước
        f = [WORD.findall(c)[0].lower() for c in cau if WORD.findall(c)]
        return sum(a == b for a, b in zip(f, f[1:])) / max(1, len(f) - 1)
    raise SystemExit(f'stat lạ: {name}')


def do(t, m):
    return do_regex(t, m) if m['kind'] == 'regex' else do_stat(t, m)


# ---------- thống kê ----------
def tb(x):
    return sum(x) / len(x) if x else float('nan')


def _var(x):
    mu = tb(x)
    return sum((v - mu) ** 2 for v in x) / max(1, len(x) - 1)


def so_sanh(a, b, huong, rng=None, boot=0):
    """Tỉ lệ trung bình a/b, CI 95% (delta method trên log, hoặc bootstrap nếu boot>0 và mẫu nhỏ), p một phía (Welch z).
    Đơn vị là từng bài (không gộp chữ) để bài dài không lấn bài ngắn."""
    ma, mb, va, vb = tb(a), tb(b), _var(a), _var(b)
    se = math.sqrt(va / len(a) + vb / len(b)) or 1e-12
    z = (ma - mb) / se
    p = 0.5 * math.erfc((z if huong == 'higher' else -z) / math.sqrt(2))
    eps = 1e-9
    if mb < eps:  # mốc bằng 0: tỉ lệ vô nghĩa, chỉ còn p
        return (float('inf') if ma > eps else 1.0), None, None, (p if ma > eps else 1.0)
    r = (ma + eps) / (mb + eps)
    if boot and len(a) + len(b) <= 400:
        rng = rng or random.Random(0); rs = []
        for _ in range(boot):
            rs.append((tb([a[rng.randrange(len(a))] for _ in a]) + eps) / (tb([b[rng.randrange(len(b))] for _ in b]) + eps))
        rs.sort(); return r, rs[int(.025 * boot)], rs[int(.975 * boot)], p
    sl = math.sqrt(va / (len(a) * (ma + eps) ** 2) + vb / (len(b) * (mb + eps) ** 2))
    return r, r * math.exp(-1.96 * sl), r * math.exp(1.96 * sl), p


def holm(ps):
    idx = sorted(range(len(ps)), key=lambda i: ps[i])
    out, m, best = [0] * len(ps), len(ps), 0
    for r, i in enumerate(idx):
        best = max(best, min(1, (m - r) * ps[i]))
        out[i] = best
    return out


def wilson(k, n, z=1.96):
    if not n:
        return (0, 0)
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (c - h, c + h)


# ---------- gọi model ----------
def goi(spec, prompt, system, temp):
    kind, _, name = spec.partition(':')
    if kind == 'claude':
        cmd = ['claude', '-p', '--model', name, '--max-turns', '1', '--tools', '']
        if system:
            cmd += ['--system-prompt', system]
        r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding='utf-8', timeout=600, cwd=CWD)
        if r.returncode:
            raise RuntimeError(r.stderr[-300:])
        return r.stdout.strip()
    if kind == 'gemini':
        cmd = ['gemini', '-p', ((system + '\n\n') if system else '') + prompt] + (['-m', name] if name else [])
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', timeout=600, cwd=CWD)
        if r.returncode:
            raise RuntimeError(r.stderr[-300:])
        return r.stdout.strip()
    if kind in ('openrouter', 'oai'):
        base = 'https://openrouter.ai/api/v1' if kind == 'openrouter' else os.environ.get('OAI_BASE_URL', 'http://localhost:11434/v1')
        key = os.environ.get('OPENROUTER_API_KEY' if kind == 'openrouter' else 'OAI_API_KEY', 'x')
        msgs = ([{'role': 'system', 'content': system}] if system else []) + [{'role': 'user', 'content': prompt}]
        body = json.dumps({'model': name, 'messages': msgs, 'temperature': temp}).encode()
        req = urllib.request.Request(base + '/chat/completions', body, {'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=600) as f:
            return json.load(f)['choices'][0]['message']['content'].strip()
    raise SystemExit(f'model lạ: {spec} (claude:, gemini:, openrouter:, oai:)')


def cmd_run(a):
    de = list(doc_jsonl([a.prompts]))
    out = Path(a.out)
    co = set()
    if out.exists():
        co = {(r['model'], str(r['prompt_id']), r.get('sample', 0)) for r in doc_jsonl([out])}
    viec = [(m, d, s) for m in a.models.split(',') for d in de[:a.limit or None] for s in range(a.n)
            if (m, str(d['id']), s) not in co]
    print(f'{len(viec)} lượt cần chạy ({len(co)} đã có)', file=sys.stderr)

    def mot(v):
        m, d, s = v
        try:
            return {'model': m, 'prompt_id': d['id'], 'sample': s, 'output': goi(m, d['prompt'], a.system, a.temp)}
        except Exception as e:
            print(f'LỖI {m} {d["id"]}: {e}', file=sys.stderr)
    with cf.ThreadPoolExecutor(a.workers) as ex, out.open('a', encoding='utf-8') as f:
        for i, r in enumerate(ex.map(mot, viec), 1):
            if r:
                f.write(json.dumps(r, ensure_ascii=False) + '\n'); f.flush()
            if i % 10 == 0:
                print(f'{i}/{len(viec)}', file=sys.stderr)


def cmd_import(a):
    out = Path(a.out).open('a', encoding='utf-8')
    src = Path(a.src)
    if src.is_dir() and any(src.glob('*.jsonl')):  # slop-forensics: generated_<model>.jsonl
        for p in sorted(src.glob('*.jsonl')):
            n = 0
            for line in p.open(encoding='utf-8'):
                r = json.loads(line)
                if not r.get('output'):
                    continue
                pid = r.get('id', n)
                if a.ids and str(pid) not in a.ids:
                    continue
                out.write(json.dumps({'model': a.model or r.get('model', p.stem), 'prompt_id': pid, 'sample': 0, 'output': r['output']}, ensure_ascii=False) + '\n')
                n += 1
                if a.limit and n >= a.limit:
                    break
            print(f'{p.name}: {n}', file=sys.stderr)
    else:  # thư mục bài người
        for p in sorted(list(src.glob('*.md')) + list(src.glob('*.txt'))):
            t = META.sub('', p.read_text(encoding='utf-8'))
            out.write(json.dumps({'model': a.model or 'human', 'prompt_id': p.stem, 'sample': 0, 'output': t.strip()}, ensure_ascii=False) + '\n')


def nhom(rows, min_words):
    g = collections.defaultdict(list)
    for r in rows:
        if so_chu(r['output']) >= min_words:
            g[r['model']].append(r['output'])
    return g


def cmd_test(a):
    g = nhom(list(doc_jsonl(a.data)), a.min_words)
    bao, csv = [f'# Kết quả kiểm thử thói quen viết\n\nDữ liệu: {", ".join(a.data)} · {sum(map(len, g.values()))} bài · {len(g)} nguồn\n'], []
    for hp in a.hyp:
        for h in (json.loads(Path(hp).read_text(encoding='utf-8')) if hp.endswith('.json') else []):
            bao.append(test_mot(h, g, a, csv))
    Path(a.out).write_text('\n'.join(bao), encoding='utf-8')
    Path(a.out).with_suffix('.csv').write_text('\n'.join(['hyp,model,n,mean,ref_mean,ratio,ci_lo,ci_hi,p_holm,verdict'] + csv), encoding='utf-8')
    print(a.out)


def test_mot(h, g, a, csv):
    ex = h.get('expect', {})
    huong, ref, min_ratio = ex.get('direction', 'higher'), ex.get('against', 'others'), ex.get('min_ratio', 1.0)
    v = {m: [do(t, h['metric']) for t in ts] for m, ts in g.items()}
    models = [m for m in v if m != 'human']
    hang, ps = [], []
    for m in models:
        if ref == 'human':
            if 'human' not in v:
                return f'## {h["id"]}\n\nThiếu dữ liệu người (model "human"), bỏ qua.\n'
            b = v['human']
        elif ref == 'value':
            b = None
        else:
            b = [x for k in models if k != m for x in v[k]]
        x = v[m]
        if b is None:
            hang.append((m, len(x), tb(x), ex['value'], None, None, None)); ps.append(1.0)
            continue
        r, lo, hi, p = so_sanh(x, b, huong, boot=a.boot)
        hang.append((m, len(x), tb(x), tb(b), r, lo, hi))
        ps.append(p)
    padj = holm(ps)
    dong = [f'## {h["id"]}: {h["claim"]}\n', f'Đo: `{json.dumps(h["metric"], ensure_ascii=False)}` · so với: **{ref}** · kỳ vọng: {huong}'
            + (f' ≥ {min_ratio}×' if ref != 'value' else f' {ex.get("value")}') + '\n',
            '| Model | n | Trung bình | Mốc | Tỉ lệ | CI 95% | p (Holm) | Kết luận |', '|---|---|---|---|---|---|---|---|']
    dung = nguoc = 0
    for (m, n, mu, mb, r, lo, hi), p in sorted(zip(hang, padj), key=lambda z: -z[0][2]):
        if r is None:
            if h['metric'].get('unit') == 'presence':
                k = round(mu * n); wl, wh = wilson(k, n)
                ok = wl > mb if huong == 'higher' else wh < mb
                kl = 'ĐÚNG' if ok else ('SAI' if (wh < mb if huong == 'higher' else wl > mb) else 'CHƯA RÕ')
                ci = f'{wl:.2f}–{wh:.2f}'
            else:
                ok = mu > mb if huong == 'higher' else mu < mb
                kl, ci = ('ĐÚNG' if ok else 'SAI'), ''
            dong.append(f'| {m} | {n} | {mu:.3f} | {mb} | | {ci} | | {kl} |')
            csv.append(f'{h["id"]},{m},{n},{mu:.4f},{mb},,,,,{kl}')
        else:
            if lo is None:
                kl = 'ĐÚNG HƯỚNG, MỐC = 0' if p < .05 else 'CHƯA RÕ'
                dong.append(f'| {m} | {n} | {mu:.3f} | {mb:.3f} | {"∞" if r == float("inf") else "–"} | | {p:.3f} | {kl} |')
                csv.append(f'{h["id"]},{m},{n},{mu:.4f},{mb:.4f},,,,{p:.4f},{kl}')
                continue
            if huong == 'higher':
                kl = 'ĐÚNG' if p < .05 and lo >= min_ratio else ('ĐÚNG HƯỚNG, CHƯA ĐỦ MẠNH' if p < .05 else ('NGƯỢC' if hi < 1 else 'CHƯA RÕ'))
            else:
                kl = 'ĐÚNG' if p < .05 and hi <= 1 / min_ratio else ('ĐÚNG HƯỚNG, CHƯA ĐỦ MẠNH' if p < .05 else ('NGƯỢC' if lo > 1 else 'CHƯA RÕ'))
            dong.append(f'| {m} | {n} | {mu:.3f} | {mb:.3f} | {r:.2f}× | {lo:.2f}–{hi:.2f} | {p:.3f} | {kl} |')
            csv.append(f'{h["id"]},{m},{n},{mu:.4f},{mb:.4f},{r:.3f},{lo:.3f},{hi:.3f},{p:.4f},{kl}')
        dung += kl == 'ĐÚNG'
        nguoc += kl == 'NGƯỢC'
    dong.append(f'\n**Tóm lại:** đúng với {dung}/{len(models)} model, ngược với {nguoc}.\n')
    return '\n'.join(dong)


def cmd_explore(a):
    g = nhom(list(doc_jsonl(a.data)), a.min_words)
    dem = {}
    for m, ts in g.items():
        c = collections.Counter()
        for t in ts:
            cau = tach_cau(t)
            pick = cau[:1] if a.kind == 'opener_text' else cau
            seen = set()
            for s in pick:
                w = WORD.findall(s.lower().replace('’', "'"))[:a.k]
                if len(w) == a.k:
                    seen.add(' '.join(w))
            c.update(seen)  # đếm số BÀI có cụm, không đếm lặp trong bài
        dem[m] = (c, len(ts))
    print(f'# Cụm {a.k} chữ đầu {"bài" if a.kind == "opener_text" else "câu"} đặc trưng (tỉ lệ bài có cụm, so với các nguồn khác)\n')
    for m, (c, n) in sorted(dem.items()):
        khac = collections.Counter(); nk = 0
        for k, (c2, n2) in dem.items():
            if k != m:
                khac.update(c2); nk += n2
        hang = []
        for cum, k in c.items():
            if k < max(3, .03 * n):
                continue
            pm, po = k / n, (khac[cum] + .5) / (nk + 1)
            hang.append((math.log(pm / po), cum, pm, po))
        hang.sort(reverse=True)
        print(f'## {m} ({n} bài)')
        for lr, cum, pm, po in hang[:a.top]:
            print(f'- "{cum}" {pm:.0%} bài, nguồn khác {po:.1%} (×{math.exp(lr):.1f})')
        print()


def cmd_check(a):
    h = next(x for x in json.loads(Path(a.hyp).read_text(encoding='utf-8')) if x['id'] == a.id)
    m = h['metric']; rx = re.compile(m['pattern'], sum({'i': re.I, 'm': re.M, 's': re.S}[c] for c in m.get('flags', '')))
    rows = [r for r in doc_jsonl(a.data) if not a.model or r['model'] == a.model]
    random.Random(0).shuffle(rows)
    k = 0
    for r in rows:
        if m.get('scope') == 'sentence_start':
            hit = next((c for c in tach_cau(r['output']) if rx.search(' '.join(WORD.findall(c)[:4]) + ' ')), None)
            if hit:
                print(f'[{r["model"]}] {hit[:160]!r}'); k += 1
        else:
            for mt in rx.finditer(r['output']):
                s, e = max(0, mt.start() - 60), mt.end() + 60
                print(f'[{r["model"]}] …{r["output"][s:e]!r}…'); k += 1
                break
        if k >= a.n:
            break


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('run'); p.add_argument('--prompts', required=True); p.add_argument('--models', required=True)
    p.add_argument('--n', type=int, default=1); p.add_argument('--limit', type=int); p.add_argument('--out', required=True)
    p.add_argument('--system', default='You are a helpful assistant.'); p.add_argument('--temp', type=float, default=0.7); p.add_argument('--workers', type=int, default=4)
    p = sp.add_parser('import'); p.add_argument('src'); p.add_argument('--out', required=True); p.add_argument('--model'); p.add_argument('--limit', type=int)
    p.add_argument('--ids', nargs='*', help='chỉ lấy các prompt id này (để mọi model cùng đề)')
    for name in ('test', 'explore'):
        p = sp.add_parser(name); p.add_argument('--data', nargs='+', required=True); p.add_argument('--min-words', type=int, default=50)
        if name == 'test':
            p.add_argument('--hyp', nargs='+', required=True); p.add_argument('--out', default='KET-QUA.md'); p.add_argument('--boot', type=int, default=1000)
        else:
            p.add_argument('--kind', choices=['opener_text', 'opener_sentence'], default='opener_text'); p.add_argument('--k', type=int, default=2); p.add_argument('--top', type=int, default=6)
    p = sp.add_parser('check'); p.add_argument('--hyp', required=True); p.add_argument('--id', required=True); p.add_argument('--data', nargs='+', required=True)
    p.add_argument('--model'); p.add_argument('--n', type=int, default=10)
    a = ap.parse_args()
    {'run': cmd_run, 'import': cmd_import, 'test': cmd_test, 'explore': cmd_explore, 'check': cmd_check}[a.cmd](a)


if __name__ == '__main__':
    main()
