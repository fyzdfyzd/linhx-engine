"""brandcheck.py: CLI bộ công cụ brand check chuẩn ABC v1.0 (LINHX LAB036).

  python brandcheck.py khoi-tao  -w <ws> --brand "Tên" --website x.vn --category "ngành"
  python brandcheck.py cau-hoi   -w <ws> --goi N|C|S
  python brandcheck.py hoi       -w <ws> --mo-hinh claude-tim,gemini-nho,dan-tay:chatgpt --luot 3
  python brandcheck.py cham      -w <ws> --giam-khao claude|gemini|phien
  python brandcheck.py tin-hieu  -w <ws> [--offline]
  python brandcheck.py bao-cao   -w <ws>
  python brandcheck.py tat-ca    -w <ws> --mo-hinh ... --luot 3 --giam-khao claude
  python brandcheck.py tu-kiem                      (dữ liệu mẫu, không gọi mạng, không tốn tiền)

Mọi lệnh trừ khoi-tao nhận --lan YYYY-MM-DD (mặc định hôm nay). Thư viện chuẩn Python 3.10+.
"""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import abc_baocao  # noqa: E402
import abc_cham  # noqa: E402
import abc_diem  # noqa: E402
import abc_hoi  # noqa: E402
import abc_tinhieu  # noqa: E402
from abc_lib import DATA, build_questions, load_json, save_json  # noqa: E402


def _ws(a) -> Path:
    return Path(a.w).resolve()


def _run(a) -> Path:
    return _ws(a) / "lan" / (a.lan or dt.date.today().isoformat())


def _facts(a) -> dict:
    p = _ws(a) / "brand-facts.json"
    if not p.exists():
        sys.exit(f"Chưa có {p}. Chạy khoi-tao trước.")
    return load_json(p)


def _questions(a) -> list[dict]:
    p = _ws(a) / "cau-hoi.json"
    if not p.exists():
        sys.exit("Chưa có cau-hoi.json. Chạy cau-hoi trước.")
    return load_json(p)


def cmd_khoi_tao(a):
    ws = _ws(a)
    ws.mkdir(parents=True, exist_ok=True)
    p = ws / "brand-facts.json"
    if p.exists():
        print(f"Đã có {p}, giữ nguyên.")
        return
    d = load_json(DATA / "brand-facts.mau.json")
    d.update({k: v for k, v in {"brand": a.brand, "website": a.website, "category": a.category}.items() if v})
    save_json(p, d)
    shutil.copy(DATA / "tin-hieu-tay.mau.json", ws / "tin-hieu-tay.mau.json")
    print(f"Tạo {p}. Điền bảng sự thật (skill bang-su-that) rồi chạy cau-hoi.")


def cmd_cau_hoi(a):
    qs = build_questions(_facts(a), a.goi)
    save_json(_ws(a) / "cau-hoi.json", qs)
    by = {}
    for q in qs:
        by[q["loai"]] = by.get(q["loai"], 0) + 1
    print(f"{len(qs)} câu (gói {a.goi}): " + ", ".join(f"{k} {v}" for k, v in by.items()))


def cmd_hoi(a):
    facts, qs = _facts(a), _questions(a)
    models = [m.strip() for m in a.mo_hinh.split(",") if m.strip()]
    paid = [m for m in models if not m.startswith("dan-tay")]
    print(f"Sẽ hỏi {len(qs)} câu × {a.luot} lượt × {len(paid)} mô hình tự động = {len(qs) * a.luot * len(paid)} lần gọi.")
    res = abc_hoi.collect(_run(a), qs, models, a.luot, facts.get("market", "Việt Nam"), (a.lan or dt.date.today().isoformat()))
    print(res)
    if res["file_cho_dan"]:
        print(f"Dán câu trả lời thật vào các file trong {_run(a) / 'tra-loi'} (thay dòng '(no response)').")


def cmd_cham(a):
    facts, qs = _facts(a), {q["id"]: q for q in _questions(a)}
    ans = abc_hoi.load_answers(_run(a))
    print(abc_cham.run(_run(a), facts, ans, qs, a.giam_khao))


def cmd_tin_hieu(a):
    res = abc_tinhieu.run(_ws(a), _facts(a), offline=a.offline)
    save_json(_run(a) / "tin-hieu.json", res)
    print({k: v.get("score") for k, v in res.items() if isinstance(v, dict) and "score" in v})


def _judgements(run: Path) -> dict:
    out = {}
    for p in (run / "cham").glob("*/*.json"):
        qid, _, l = p.stem.rpartition("__l")
        try:
            out[(p.parent.name, qid, int(l or 1))] = load_json(p)
        except ValueError:
            print(f"  ! file chấm hỏng: {p}", file=sys.stderr)
    return out


def cmd_bao_cao(a):
    run, facts = _run(a), _facts(a)
    qs = {q["id"]: q for q in _questions(a)}
    ans = abc_hoi.load_answers(run)
    if not ans:
        sys.exit("Chưa có câu trả lời nào trong lượt này.")
    sig_p = run / "tin-hieu.json"
    sig = load_json(sig_p) if sig_p.exists() else {}
    s = abc_diem.score_all(facts, ans, _judgements(run), qs, sig)
    date = run.name
    plan = abc_baocao.plan(facts, s, sig)
    save_json(run / "diem.json", s | {"ke_hoach": plan})
    (run / "bao-cao.md").write_text(abc_baocao.markdown(facts, s, plan, date), encoding="utf-8")
    (run / "bao-cao.html").write_text(abc_baocao.html_report(facts, s, plan, date), encoding="utf-8")
    print(f"AVI {s['avi']} hạng {s['hang']} · R {s['reputation']} · V {s['verifiable']} · rơi ở bước {s['roi_o_buoc']}")
    print(f"→ {run / 'bao-cao.html'}")


def cmd_tat_ca(a):
    cmd_hoi(a)
    cmd_cham(a)
    cmd_tin_hieu(a)
    cmd_bao_cao(a)


def cmd_tu_kiem(a):
    import tu_kiem
    sys.exit(tu_kiem.main())


def main():
    ap = argparse.ArgumentParser(description="Brand check chuẩn ABC")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def sp(name, fn, ws=True):
        s = sub.add_parser(name)
        if ws:
            s.add_argument("-w", required=True, help="thư mục làm việc của thương hiệu")
            s.add_argument("--lan", help="ngày lượt quét YYYY-MM-DD")
        s.set_defaults(fn=fn)
        return s

    s = sp("khoi-tao", cmd_khoi_tao)
    s.add_argument("--brand"), s.add_argument("--website"), s.add_argument("--category")
    sp("cau-hoi", cmd_cau_hoi).add_argument("--goi", default="N", choices=["N", "C", "S"])
    for name, fn in (("hoi", cmd_hoi), ("tat-ca", cmd_tat_ca)):
        s = sp(name, fn)
        s.add_argument("--mo-hinh", required=True)
        s.add_argument("--luot", type=int, default=1)
        if name == "tat-ca":
            s.add_argument("--giam-khao", default="claude", choices=["claude", "gemini", "phien"])
            s.add_argument("--offline", action="store_true")
    sp("cham", cmd_cham).add_argument("--giam-khao", default="claude", choices=["claude", "gemini", "phien"])
    sp("tin-hieu", cmd_tin_hieu).add_argument("--offline", action="store_true")
    sp("bao-cao", cmd_bao_cao)
    sp("tu-kiem", cmd_tu_kiem, ws=False)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
