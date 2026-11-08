#!/usr/bin/env python3
"""Nhật ký thí nghiệm cho research loop (kiểu autoresearch results.tsv + journal AI Scientist v2).

Lệnh:
  init  <thu_muc> [--thap-tot|--cao-tot]       tạo nhat-ky.tsv, idea-bank.tsv
  ghi   <thu_muc> <y_tuong_id> <chi_so|crash> <keep|discard|crash> "mo ta" [--commit c] [--token n]
  y     <thu_muc> "mo ta y tuong" [--nguon s]  thêm ý vào idea bank
  chon  <thu_muc> [--seed n]                   gợi ý bước kế: khai thác / khám phá / quay lại đọc tài liệu
  tot   <thu_muc>                              in commit tốt nhất để reset về
  tom   <thu_muc>                              in DIGEST 1 trang cho người đọc buổi sáng
"""
import csv, json, os, random, sys, time

COT_NK = ["stt", "luc", "y_tuong", "chi_so", "trang_thai", "commit", "token", "mo_ta"]
COT_Y = ["id", "trang_thai", "so_lan_thu", "tot_nhat", "nguon", "mo_ta", "sau_dong"]
KHAI_THAC, KHAM_PHA = 0.7, 0.3   # OpenEvolve dùng 0.7/0.2/0.1; gộp elite vào khai thác
KET_SAU = 5                      # 5 lần liên tiếp không cải thiện -> gợi ý quay lại bước 2


def p(d, f): return os.path.join(d, f)

def doc(path):
    if not os.path.exists(path): return []
    with open(path, encoding="utf-8") as f: return list(csv.DictReader(f, delimiter="\t"))

def viet(path, cot, dong):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, cot, delimiter="\t"); w.writeheader(); w.writerows(dong)

def cau_hinh(d):
    with open(p(d, "cau-hinh.json"), encoding="utf-8") as f: return json.load(f)

def tot_hon(a, b, thap_tot): return a < b if thap_tot else a > b

def lay_co(args, ten, mac_dinh=""):
    return args[args.index(ten) + 1] if ten in args else mac_dinh


def init(d, args):
    os.makedirs(d, exist_ok=True)
    json.dump({"thap_tot": "--cao-tot" not in args}, open(p(d, "cau-hinh.json"), "w"))
    if not os.path.exists(p(d, "nhat-ky.tsv")): viet(p(d, "nhat-ky.tsv"), COT_NK, [])
    if not os.path.exists(p(d, "idea-bank.tsv")): viet(p(d, "idea-bank.tsv"), COT_Y, [])
    print("ok", d)


def them_y(d, args):
    ys = doc(p(d, "idea-bank.tsv"))
    i = f"Y{len(ys) + 1:03d}"
    ys.append({"id": i, "trang_thai": "mo", "so_lan_thu": "0", "tot_nhat": "",
               "nguon": lay_co(args, "--nguon", "nguoi"), "mo_ta": args[0],
               "sau_dong": str(len(doc(p(d, "nhat-ky.tsv"))))})
    viet(p(d, "idea-bank.tsv"), COT_Y, ys); print(i)


def ghi(d, args):
    y_id, chi_so, tt, mo_ta = args[:4]
    thap_tot = cau_hinh(d)["thap_tot"]
    nk = doc(p(d, "nhat-ky.tsv"))
    c = lay_co(args, "--commit")
    if c and any(r["commit"] == c for r in nk):
        print(f"LOI: commit {c} đã có trong nhật ký, tức là code không đổi. Không ghi."); sys.exit(2)
    nk.append({"stt": str(len(nk) + 1), "luc": time.strftime("%Y-%m-%d %H:%M"), "y_tuong": y_id,
               "chi_so": "" if chi_so == "crash" else chi_so, "trang_thai": tt,
               "commit": lay_co(args, "--commit"), "token": lay_co(args, "--token"), "mo_ta": mo_ta})
    viet(p(d, "nhat-ky.tsv"), COT_NK, nk)
    ys = doc(p(d, "idea-bank.tsv"))
    for y in ys:
        if y["id"] == y_id:
            y["so_lan_thu"] = str(int(y["so_lan_thu"] or 0) + 1)
            if chi_so != "crash" and (not y["tot_nhat"] or tot_hon(float(chi_so), float(y["tot_nhat"]), thap_tot)):
                y["tot_nhat"] = chi_so
            if y["trang_thai"] == "mo": y["trang_thai"] = "dang_thu"
    viet(p(d, "idea-bank.tsv"), COT_Y, ys)
    print("ghi", len(nk))


def phan_tich(d):
    thap_tot = cau_hinh(d)["thap_tot"]
    nk = doc(p(d, "nhat-ky.tsv"))
    co_so = [r for r in nk if r["chi_so"]]
    baseline = float(co_so[0]["chi_so"]) if co_so else None
    tot, ket = None, 0
    for r in co_so:
        v = float(r["chi_so"])
        if tot is None or tot_hon(v, tot, thap_tot): tot, ket = v, 0
        else: ket += 1
    return nk, baseline, tot, ket, thap_tot


def tot(d, args):
    """In commit của lần keep gần nhất (đỉnh nhánh đang giữ): reset về đây, không reset HEAD~1."""
    k = [r for r in doc(p(d, "nhat-ky.tsv")) if r["trang_thai"] == "keep" and r["commit"]]
    if k: print(k[-1]["commit"])


def chon(d, args):
    random.seed(int(lay_co(args, "--seed", str(int(time.time())))))
    nk, baseline, tot, ket, thap_tot = phan_tich(d)
    ys = doc(p(d, "idea-bank.tsv"))
    if not nk:
        print("BUOC: baseline — chạy nguyên trạng, ghi với y_tuong=BASE"); return
    # sau khi đã nạp ý mới thì đếm kẹt lại từ đầu, tránh vòng quay_lai_doc vô tận
    moc = max([int(y.get("sau_dong") or 0) for y in ys] + [0])
    ket = min(ket, len(nk) - moc)
    if ket >= KET_SAU:
        print(f"BUOC: quay_lai_doc — {ket} lần liên tiếp không cải thiện. Tìm tài liệu (trần 5 lượt), thêm 3 ý mới vào idea bank rồi chạy tiếp."); return
    mo = [y for y in ys if y["trang_thai"] == "mo"]
    dang = sorted([y for y in ys if y["trang_thai"] == "dang_thu" and y["tot_nhat"]],
                  key=lambda y: float(y["tot_nhat"]), reverse=not thap_tot)
    if dang and (not mo or random.random() < KHAI_THAC):
        print(f"BUOC: khai_thac — cải tiến tiếp {dang[0]['id']} ({dang[0]['mo_ta']}), tốt nhất {dang[0]['tot_nhat']}")
    elif mo:
        y = random.choice(mo); print(f"BUOC: kham_pha — thử ý mới {y['id']} ({y['mo_ta']})")
    else:
        print("BUOC: sinh_y — idea bank đã cạn: đọc nhật ký, viết 3 ý mới (nguon=agent) rồi chọn lại")


def tom(d, args):
    nk, baseline, tot, ket, thap_tot = phan_tich(d)
    ys = doc(p(d, "idea-bank.tsv"))
    dem = {k: sum(r["trang_thai"] == k for r in nk) for k in ("keep", "discard", "crash")}
    token = sum(int(r["token"] or 0) for r in nk)
    print("# DIGEST research loop\n")
    print(f"- Số thí nghiệm: {len(nk)} (giữ {dem['keep']}, bỏ {dem['discard']}, lỗi {dem['crash']}); token ghi nhận: {token:,}")
    if baseline is not None:
        thay = (baseline - tot) if thap_tot else (tot - baseline)
        print(f"- Baseline {baseline} → tốt nhất {tot} (cải thiện {thay:+.4g}, {'thấp' if thap_tot else 'cao'} là tốt)")
    print(f"- Số lần liên tiếp không cải thiện: {ket}\n")
    print("## Top 3 thí nghiệm (người nên xem diff những dòng này)")
    co = sorted([r for r in nk if r["chi_so"]], key=lambda r: float(r["chi_so"]), reverse=not thap_tot)[:3]
    for r in co: print(f"- #{r['stt']} {r['y_tuong']} = {r['chi_so']} [{r['trang_thai']}] {r['commit']} {r['mo_ta']}")
    print("\n## Cần người quyết")
    # nghi: một bước "keep" cải thiện hơn 50% so với mức tốt nhất ngay trước nó -> người xem diff
    nghi, truoc = [], None
    for r in [r for r in nk if r["chi_so"]]:
        v = float(r["chi_so"])
        if r["trang_thai"] == "keep" and truoc not in (None, 0) and abs(truoc - v) > 0.5 * abs(truoc): nghi.append((r, truoc))
        if r["trang_thai"] == "keep": truoc = v
    for r, t in nghi: print(f"- #{r['stt']} {r['y_tuong']} nhảy {t} → {r['chi_so']} trong một bước: xem diff, kiểm tra có lách phép đo không")
    # sau khi đã nạp ý mới thì đếm kẹt lại từ đầu, tránh vòng quay_lai_doc vô tận
    moc = max([int(y.get("sau_dong") or 0) for y in ys] + [0])
    ket = min(ket, len(nk) - moc)
    if ket >= KET_SAU: print("- Vòng đang kẹt: duyệt các ý mới agent thêm vào idea bank")
    if not nghi and ket < KET_SAU: print("- Không có gì bắt buộc")
    print("\n## Idea bank")
    for y in ys: print(f"- {y['id']} [{y['trang_thai']}] thử {y['so_lan_thu']} lần, tốt nhất {y['tot_nhat'] or '-'} ({y['nguon']}): {y['mo_ta']}")


if __name__ == "__main__":
    if len(sys.argv) < 3: print(__doc__); sys.exit(1)
    lenh, d, rest = sys.argv[1], sys.argv[2], sys.argv[3:]
    {"init": lambda: init(d, rest), "y": lambda: them_y(d, rest), "ghi": lambda: ghi(d, rest),
     "chon": lambda: chon(d, rest), "tot": lambda: tot(d, rest), "tom": lambda: tom(d, rest)}[lenh]()
