#!/usr/bin/env python3
"""linhx-nuoi-cong-dong v0.1 (LAB041).

Một CSDL SQLite cho một cộng đồng: thành viên, sự kiện, đơn, link nguồn,
đề xuất, nhắc việc. Script chỉ tính và ghi file; không gửi tin cho ai.

Chạy trong thư mục cộng đồng (mặc định thư mục hiện tại, hoặc biến NUOI_HOME):
  nuoi.py init
  nuoi.py nhap thanh-vien|su-kien|don|link <file.csv>
  nuoi.py cham
  nuoi.py sop [--ngay YYYY-MM-DD] [--so-ngay 7]
  nuoi.py de-xuat [--ngay YYYY-MM-DD]
  nuoi.py danh-dau <id> nhan|bo|tu-choi|da-lam
  nuoi.py xong-sop <lớp> <mốc>
  nuoi.py link tao --kenh K --chien-dich C --url U [--bai B]
  nuoi.py suc-khoe [--ngay YYYY-MM-DD]
  nuoi.py tuan [--ngay YYYY-MM-DD]      # cham + sop + de-xuat + suc-khoe + BAO-CAO-TUAN.md
"""
import argparse, csv, datetime as dt, json, os, sqlite3, sys
from pathlib import Path
from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl

PLUGIN = Path(__file__).resolve().parent.parent
HOME = Path(os.environ.get("NUOI_HOME", os.getcwd()))
DB = HOME / "data" / "cong-dong.db"
OUT = HOME / "output"

SCHEMA = """
CREATE TABLE IF NOT EXISTS member(ma TEXT PRIMARY KEY, ten TEXT, cong_ty TEXT, khoa TEXT,
  chuc_vu TEXT, nhom TEXT, nguon TEXT, ngay_vao TEXT, kenh TEXT, dong_y_lien_he INTEGER DEFAULT 0,
  ghi_chu TEXT, diem REAL DEFAULT 0, cap INTEGER DEFAULT 4, cap_truoc INTEGER, lan_cuoi TEXT);
CREATE TABLE IF NOT EXISTS event(id INTEGER PRIMARY KEY, ma_thanh_vien TEXT, loai TEXT, ngay TEXT,
  kenh TEXT, noi_dung TEXT, ref TEXT,
  UNIQUE(ma_thanh_vien, loai, ngay, noi_dung));
CREATE TABLE IF NOT EXISTS don(id INTEGER PRIMARY KEY, ma_thanh_vien TEXT, cong_ty TEXT, san_pham TEXT,
  gia_tri REAL, ngay TEXT, trang_thai TEXT, UNIQUE(cong_ty, san_pham, ngay));
CREATE TABLE IF NOT EXISTS link(ref TEXT PRIMARY KEY, kenh TEXT, chien_dich TEXT, bai TEXT, url TEXT, ngay TEXT);
CREATE TABLE IF NOT EXISTS de_xuat(id INTEGER PRIMARY KEY, ngay TEXT, ma_thanh_vien TEXT, loai TEXT,
  ly_do TEXT, hanh_dong TEXT, trang_thai TEXT DEFAULT 'moi', UNIQUE(ngay, ma_thanh_vien, loai));
CREATE TABLE IF NOT EXISTS nhac_viec(id INTEGER PRIMARY KEY, ma_thanh_vien TEXT, ngay TEXT, moc INTEGER,
  viec TEXT, mau TEXT, trang_thai TEXT DEFAULT 'cho', UNIQUE(ma_thanh_vien, moc));
"""


def cfg():
    p = HOME / "config" / "cong-dong.json"
    if not p.exists():
        p = PLUGIN / "config" / "cong-dong.json"
    return json.loads(p.read_text(encoding="utf-8"))


def conn():
    DB.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    return c


def d(s):
    return dt.date.fromisoformat(str(s)[:10])


def hom_nay(a):
    return d(a.ngay) if getattr(a, "ngay", None) else dt.date.today()


def doc_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return [{k.strip(): (v or "").strip() for k, v in r.items() if k} for r in csv.DictReader(f)]


def ghi_csv(path, rows, cols):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(dict(r))


# ---------- nhập ----------
def cmd_init(a):
    conn().close()
    (HOME / "config").mkdir(exist_ok=True)
    dst = HOME / "config" / "cong-dong.json"
    if not dst.exists():
        dst.write_text((PLUGIN / "config" / "cong-dong.json").read_text(encoding="utf-8"), encoding="utf-8")
    for sub in ("nhap", "output"):
        (HOME / sub).mkdir(exist_ok=True)
    print(f"Đã tạo {DB} và {dst}. Mẫu CSV ở {PLUGIN / 'mau'}.")


def cmd_nhap(a):
    c = conn()
    rows = doc_csv(a.file)
    n = 0
    if a.loai == "thanh-vien":
        for r in rows:
            if not r.get("ma"):
                continue
            c.execute("""INSERT INTO member(ma,ten,cong_ty,khoa,chuc_vu,nhom,nguon,ngay_vao,kenh,dong_y_lien_he,ghi_chu)
              VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(ma) DO UPDATE SET ten=excluded.ten, cong_ty=excluded.cong_ty,
              khoa=excluded.khoa, chuc_vu=excluded.chuc_vu, nhom=excluded.nhom, nguon=excluded.nguon,
              ngay_vao=excluded.ngay_vao, kenh=excluded.kenh, dong_y_lien_he=excluded.dong_y_lien_he, ghi_chu=excluded.ghi_chu""",
                      (r["ma"], r.get("ten"), r.get("cong_ty"), r.get("khoa"), r.get("chuc_vu"), r.get("nhom"),
                       r.get("nguon"), r.get("ngay_vao"), r.get("kenh"), int(r.get("dong_y_lien_he") or 0), r.get("ghi_chu")))
            n += 1
    elif a.loai == "su-kien":
        for r in rows:
            cur = c.execute("INSERT OR IGNORE INTO event(ma_thanh_vien,loai,ngay,kenh,noi_dung,ref) VALUES(?,?,?,?,?,?)",
                            (r.get("ma_thanh_vien"), r.get("loai"), r.get("ngay"), r.get("kenh"), r.get("noi_dung"), r.get("ref")))
            n += cur.rowcount
    elif a.loai == "don":
        for r in rows:
            cur = c.execute("INSERT OR IGNORE INTO don(ma_thanh_vien,cong_ty,san_pham,gia_tri,ngay,trang_thai) VALUES(?,?,?,?,?,?)",
                            (r.get("ma_thanh_vien"), r.get("cong_ty"), r.get("san_pham"), float(r.get("gia_tri") or 0),
                             r.get("ngay"), r.get("trang_thai") or "hoi"))
            n += cur.rowcount
    elif a.loai == "link":
        for r in rows:
            c.execute("INSERT OR REPLACE INTO link VALUES(?,?,?,?,?,?)",
                      (r["ref"], r.get("kenh"), r.get("chien_dich"), r.get("bai"), r.get("url"), str(dt.date.today())))
            n += 1
    c.commit()
    print(f"Nhập {n} dòng {a.loai} (dòng trùng bỏ qua).")


# ---------- chấm ----------
def tinh_diem(c, C, ngay):
    w = C["trong_so_hoat_dong"]
    tu = ngay - dt.timedelta(days=C["cua_so_ngay"])
    diem, cuoi = {}, {}
    for e in c.execute("SELECT ma_thanh_vien m, loai, ngay FROM event"):
        if e["loai"] in C["loai_do_admin_tao"]:
            continue
        nd = d(e["ngay"])
        cuoi[e["m"]] = max(cuoi.get(e["m"], nd), nd)
        if tu < nd <= ngay:
            diem[e["m"]] = diem.get(e["m"], 0) + w.get(e["loai"], 1)
    return diem, cuoi


def cap_cua(C, diem):
    for k in sorted(C["cap"], key=lambda x: -x["nguong"]):
        if diem >= k["nguong"]:
            return k
    return C["cap"][-1]


def cmd_cham(a, quiet=False):
    C, c, ngay = cfg(), conn(), hom_nay(a)
    diem, cuoi = tinh_diem(c, C, ngay)
    dem = {}
    for m in c.execute("SELECT ma, cap FROM member").fetchall():
        s = diem.get(m["ma"], 0)
        k = cap_cua(C, s)
        c.execute("UPDATE member SET cap_truoc=cap, cap=?, diem=?, lan_cuoi=? WHERE ma=?",
                  (k["so"], s, str(cuoi[m["ma"]]) if m["ma"] in cuoi else None, m["ma"]))
        dem[k["ten"]] = dem.get(k["ten"], 0) + 1
    c.commit()
    if not quiet:
        print("Chấm xong:", ", ".join(f"{k} {v}" for k, v in dem.items()))
    return dem


# ---------- SOP người mới ----------
def cmd_sop(a, quiet=False):
    C, c, ngay = cfg(), conn(), hom_nay(a)
    so_ngay = getattr(a, "so_ngay", 7) or 7
    for m in c.execute("SELECT ma, ngay_vao FROM member WHERE ngay_vao IS NOT NULL AND ngay_vao<>''").fetchall():
        for s in C["sop_nguoi_moi"]:
            c.execute("INSERT OR IGNORE INTO nhac_viec(ma_thanh_vien,ngay,moc,viec,mau) VALUES(?,?,?,?,?)",
                      (m["ma"], str(d(m["ngay_vao"]) + dt.timedelta(days=s["moc"])), s["moc"], s["viec"], s["mau"]))
    c.commit()
    den = str(ngay + dt.timedelta(days=so_ngay))
    rows = c.execute("""SELECT n.id, n.ngay, n.moc, m.ma, m.ten, m.cong_ty, m.kenh, m.dong_y_lien_he, n.viec, n.mau
        FROM nhac_viec n JOIN member m ON m.ma=n.ma_thanh_vien
        WHERE n.trang_thai='cho' AND n.ngay<=? AND n.ngay>=? ORDER BY n.ngay, n.moc""",
                     (den, str(ngay - dt.timedelta(days=3)))).fetchall()
    ghi_csv(OUT / "NHAC-VIEC-TUAN.csv", rows, ["id", "ngay", "moc", "ma", "ten", "cong_ty", "kenh", "dong_y_lien_he", "viec", "mau"])
    # ICS: một sự kiện mỗi ngày, gom việc, để Linh/SO thấy trên lịch
    theo_ngay = {}
    for r in rows:
        theo_ngay.setdefault(r["ngay"], []).append(f"D+{r['moc']} {r['ten']} ({r['cong_ty']}): {r['viec']}")
    ics = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//LINHX//nuoi-cong-dong//VI"]
    for ng, ds in sorted(theo_ngay.items()):
        x = ng.replace("-", "")
        mo_ta = "\\n".join(ds).replace(",", "\\,").replace(";", "\\;")
        ics += ["BEGIN:VEVENT", f"UID:nuoi-{x}@linhx", f"DTSTART;VALUE=DATE:{x}",
                f"SUMMARY:Nuôi cộng đồng: {len(ds)} việc", f"DESCRIPTION:{mo_ta}", "END:VEVENT"]
    ics.append("END:VCALENDAR")
    (OUT / "NHAC-VIEC-TUAN.ics").write_text("\r\n".join(ics), encoding="utf-8")
    if not quiet:
        print(f"{len(rows)} việc SOP đến {den} → output/NHAC-VIEC-TUAN.csv, .ics")
    return rows


# ---------- đề xuất ----------
UU_TIEN = ["tin-hieu-mua", "champion-sang-sales", "da-giup", "len-cap", "quay-lai", "sap-len-cap", "im-lang"]
def cmd_de_xuat(a, quiet=False):
    C, c, ngay = cfg(), conn(), hom_nay(a)
    caps = sorted(C["cap"], key=lambda x: x["nguong"])
    im = ngay - dt.timedelta(days=C["im_lang_ngay"])
    gan = ngay - dt.timedelta(days=7)
    moi = []

    def them(ma, loai, ly_do, hanh_dong):
        cur = c.execute("INSERT OR IGNORE INTO de_xuat(ngay,ma_thanh_vien,loai,ly_do,hanh_dong) VALUES(?,?,?,?,?)",
                        (str(ngay), ma, loai, ly_do, hanh_dong))
        if cur.rowcount:
            moi.append(loai)

    # bỏ qua người đã bị "tu-choi" cùng loại trong 30 ngày
    tu_choi = {(r[0], r[1]) for r in c.execute(
        "SELECT ma_thanh_vien, loai FROM de_xuat WHERE trang_thai='tu-choi' AND ngay>=?", (str(ngay - dt.timedelta(days=30)),))}
    # đã xử lý (nhận, làm, bỏ) trong 14 ngày thì không nhắc lại
    tu_choi |= {(r[0], r[1]) for r in c.execute(
        "SELECT ma_thanh_vien, loai FROM de_xuat WHERE trang_thai IN ('nhan','da-lam','bo') AND ngay>=? AND ngay<?",
        (str(ngay - dt.timedelta(days=14)), str(ngay)))}

    for m in c.execute("SELECT * FROM member").fetchall():
        ma = m["ma"]
        ev = c.execute("SELECT loai, ngay, noi_dung FROM event WHERE ma_thanh_vien=? ORDER BY ngay", (ma,)).fetchall()
        ev_tv = [e for e in ev if e["loai"] not in C["loai_do_admin_tao"]]
        tuan = [e for e in ev_tv if gan < d(e["ngay"]) <= ngay]
        cands = []
        # sắp lên cấp
        tren = [k for k in caps if k["nguong"] > m["diem"]]
        if tren and m["diem"] >= tren[0]["nguong"] * C["sap_len_cap_ty_le"] and m["diem"] > 0:
            cands.append(("sap-len-cap", f"{m['diem']:.0f}/{tren[0]['nguong']} điểm để lên {tren[0]['ten']}",
                          "Mời 1 việc cụ thể (trả lời 1 câu hỏi, chia sẻ 1 case) trong 7 ngày"))
        # vừa lên cấp
        if m["cap_truoc"] and m["cap"] < m["cap_truoc"]:
            ten = next(k["ten"] for k in C["cap"] if k["so"] == m["cap"])
            cands.append(("len-cap", f"Vừa lên {ten}", "Ghi nhận công khai (xin phép) hoặc nhắn cảm ơn riêng"))
        # im lặng: từng hoạt động nhưng >N ngày không có gì
        if ev_tv and d(ev_tv[-1]["ngay"]) < im and len(ev_tv) >= 2:
            cands.append(("im-lang", f"Im từ {ev_tv[-1]['ngay']} sau {len(ev_tv)} hoạt động",
                          "Hỏi thăm 1-1, gửi 1 mẹo đúng việc của họ, không chào bán"))
        # quay lại: có hoạt động tuần này sau khoảng nghỉ dài
        if tuan and len(ev_tv) > len(tuan):
            truoc = [e for e in ev_tv if d(e["ngay"]) <= gan]
            if truoc and (d(tuan[0]["ngay"]) - d(truoc[-1]["ngay"])).days >= C["im_lang_ngay"]:
                cands.append(("quay-lai", f"Quay lại {tuan[0]['ngay']} sau {(d(tuan[0]['ngay']) - d(truoc[-1]['ngay'])).days} ngày",
                              "Chào lại, hỏi họ đang cần gì"))
        # đã giúp người khác
        giup = [e for e in tuan if e["loai"] in C["tin_hieu_giup_nguoi"]]
        if giup:
            cands.append(("da-giup", f"{len(giup)} lần giúp/chia sẻ tuần này: {giup[-1]['noi_dung'][:80]}",
                          "Cảm ơn công khai; cân nhắc mời làm AI Champion"))
        # tín hiệu mua
        mua = [e for e in ev_tv if e["loai"] in C["tin_hieu_mua"] and d(e["ngay"]) > ngay - dt.timedelta(days=14)]
        if mua:
            cands.append(("tin-hieu-mua", "; ".join(f"{e['loai']} {e['ngay']}: {e['noi_dung'][:60]}" for e in mua[-2:]),
                          "Linh/SO liên hệ 1-1 trong 48h; đề xuất bậc thang offer phù hợp; hỏi ai là HR/L&D"))
        # champion chưa có đơn ở công ty
        if m["cap"] == 1 and m["cong_ty"]:
            co_don = c.execute("SELECT 1 FROM don WHERE cong_ty=? AND trang_thai IN ('chot','da-thu')", (m["cong_ty"],)).fetchone()
            if not co_don:
                cands.append(("champion-sang-sales", f"Champion ở {m['cong_ty']}, công ty chưa có đơn mới",
                              "Xin giới thiệu HR/L&D; mời dự workshop kèm 1 đồng nghiệp quản lý"))
        cands = [x for x in cands if (ma, x[0]) not in tu_choi]
        if not cands:
            continue
        cands.sort(key=lambda x: UU_TIEN.index(x[0]))
        if len(cands) > 1:  # gộp: một người một dòng, lý do phụ nối vào
            loai0, ly0, hd0 = cands[0]
            cands = [(loai0, ly0 + " · thêm: " + "; ".join(f"{l}: {y}" for l, y, _ in cands[1:]), hd0)]
        for loai, ly_do, hd in cands:
            if loai in ("tin-hieu-mua", "champion-sang-sales", "im-lang") and not m["dong_y_lien_he"]:
                hd = ("Chưa đồng ý nhắn riêng: trả lời hoặc ghi nhận ngay trong nhóm, "
                      "mời họ tự nhắn Linh/Zalo OA nếu muốn trao đổi thêm")
            them(ma, loai, ly_do, hd)
    c.commit()
    rows = c.execute("""SELECT x.id, x.loai, m.ma, m.ten, m.cong_ty, m.cap, m.diem, x.ly_do, x.hanh_dong, x.trang_thai
        FROM de_xuat x JOIN member m ON m.ma=x.ma_thanh_vien WHERE x.ngay=?""", (str(ngay),)).fetchall()
    rows.sort(key=lambda r: (UU_TIEN.index(r["loai"]), -r["diem"]))
    toi_da = C.get("toi_da_de_xuat_tuan", 25)
    for r in rows[toi_da:]:  # quá sức một người làm trong tuần: lùi sang tuần sau, không xoá
        c.execute("DELETE FROM de_xuat WHERE id=?", (r["id"],))
    c.commit()
    rows = rows[:toi_da]
    ghi_csv(OUT / "DE-XUAT-TUAN.csv", rows, ["id", "loai", "ma", "ten", "cong_ty", "cap", "diem", "ly_do", "hanh_dong", "trang_thai"])
    if not quiet:
        print(f"{len(rows)} đề xuất ({len(moi)} mới) → output/DE-XUAT-TUAN.csv")
    return rows


def cmd_xong_sop(a):
    c = conn()
    n = c.execute("""UPDATE nhac_viec SET trang_thai='xong' WHERE moc=? AND trang_thai='cho'
        AND ma_thanh_vien IN (SELECT ma FROM member WHERE khoa=? OR cong_ty=?)""", (a.moc, a.lop, a.lop)).rowcount
    c.commit()
    print(f"Đánh dấu xong {n} việc D+{a.moc} của {a.lop}")


def cmd_danh_dau(a):
    c = conn()
    c.execute("UPDATE de_xuat SET trang_thai=? WHERE id=?", (a.trang_thai, a.id))
    c.commit()
    print(f"Đề xuất {a.id} → {a.trang_thai}")


# ---------- link nguồn ----------
def cmd_link(a):
    c = conn()
    n = c.execute("SELECT COUNT(*) FROM link").fetchone()[0] + 1
    ref = f"{a.kenh[:3]}-{a.chien_dich}-{n:03d}".lower().replace(" ", "")
    u = urlparse(a.url)
    q = dict(parse_qsl(u.query))
    q.update({"ref": ref, "utm_source": a.kenh, "utm_campaign": a.chien_dich})
    url = urlunparse(u._replace(query=urlencode(q)))
    c.execute("INSERT OR REPLACE INTO link VALUES(?,?,?,?,?,?)", (ref, a.kenh, a.chien_dich, a.bai, url, str(dt.date.today())))
    c.commit()
    print(f"{ref}\t{url}")


# ---------- sức khoẻ ----------
def cmd_suc_khoe(a, quiet=False):
    C, c, ngay = cfg(), conn(), hom_nay(a)
    tuan = ngay - dt.timedelta(days=7)
    t30, t60 = ngay - dt.timedelta(days=30), ngay - dt.timedelta(days=60)
    mem = c.execute("SELECT * FROM member").fetchall()
    ev = c.execute("SELECT * FROM event").fetchall()
    admin = set(C["loai_do_admin_tao"])
    moi_tuan = sum(1 for m in mem if m["ngay_vao"] and tuan < d(m["ngay_vao"]) <= ngay)
    bai = set(C.get("loai_bai_dang", ["binh_luan", "hoi", "tra_loi_giup", "chia_se_case"])) | admin
    ev30_all = [e for e in ev if t30 < d(e["ngay"]) <= ngay]
    tv30 = [e for e in ev30_all if e["loai"] not in admin and e["loai"] != "vao_nhom"]
    dang30 = [e for e in ev30_all if e["loai"] in bai]
    ty_le_tv = sum(1 for e in dang30 if e["loai"] not in admin) / len(dang30) if dang30 else None
    nhom = [m for m in mem if m["ngay_vao"] and t60 < d(m["ngay_vao"]) <= t30]
    con = {e["ma_thanh_vien"] for e in tv30}
    ret30 = sum(1 for m in nhom if m["ma"] in con) / len(nhom) if nhom else None
    cty = {m["cong_ty"] for m in mem if m["cong_ty"]}
    cty_mua = {r[0] for r in c.execute("SELECT DISTINCT cong_ty FROM don WHERE trang_thai IN ('chot','da-thu') AND ngay>?", (str(ngay - dt.timedelta(days=365)),))}
    mua_lai = len(cty & cty_mua) / len(cty) if cty else None
    gt = sum(1 for e in ev if e["loai"] == "gioi_thieu" and t30 < d(e["ngay"]) <= ngay)
    hoat = len(con)
    k = gt / hoat if hoat else None
    pipeline = c.execute("SELECT trang_thai, COUNT(*) n, SUM(gia_tri) v FROM don GROUP BY trang_thai").fetchall()
    cap = {}
    for m in mem:
        cap[m["cap"]] = cap.get(m["cap"], 0) + 1
    pct = lambda x: "chưa đủ dữ liệu" if x is None else f"{x*100:.0f}%"
    so = {
        "Thành viên mới 7 ngày": str(moi_tuan),
        "% hoạt động do thành viên tạo (30 ngày; mốc FeverBee 50% rồi 90%)": pct(ty_le_tv),
        "Giữ chân 30 ngày (vào 30–60 ngày trước, còn hoạt động)": pct(ret30),
        "% công ty có đơn mới trong 12 tháng (thay free→paid cho B2B)": pct(mua_lai),
        "Lời giới thiệu 30 ngày / thành viên hoạt động (K)": "chưa đủ dữ liệu" if k is None else f"{gt}/{hoat} = {k:.2f}",
        "Thành viên hoạt động 30 ngày / tổng": f"{hoat}/{len(mem)}",
    }
    ten_cap = {x["so"]: x["ten"] for x in C["cap"]}
    lines = [f"## Sức khoẻ cộng đồng đến {ngay}", "", "| Chỉ số | Giá trị |", "|---|---|"]
    lines += [f"| {k_} | {v} |" for k_, v in so.items()]
    lines += ["", "**Phân bố cấp:** " + ", ".join(f"{ten_cap.get(s, s)} {n}" for s, n in sorted(cap.items())),
              "", "**Đơn theo trạng thái:** " + (", ".join(f"{r['trang_thai']} {r['n']} ({(r['v'] or 0):,.0f}đ)" for r in pipeline) or "chưa có")]
    if not quiet:
        print("\n".join(lines))
    return lines


def cmd_tuan(a):
    C = cfg()
    cmd_cham(a, quiet=True)
    sop = cmd_sop(a, quiet=True)
    dx = cmd_de_xuat(a, quiet=True)
    sk = cmd_suc_khoe(a, quiet=True)
    ngay = hom_nay(a)
    c = conn()
    hoi = c.execute("SELECT noi_dung FROM event WHERE loai='hoi' AND ngay>? ORDER BY ngay DESC",
                    (str(ngay - dt.timedelta(days=14)),)).fetchall()
    L = [f"# Bản tin tuần · {C['ten']} · {ngay}", "",
         "> Script chỉ tính. Mọi tin nhắn do Linh/SO đọc, sửa và tự gửi. Đề xuất nào không làm thì `danh-dau <id> bo|tu-choi`.", ""]
    L += sk + ["", f"## Đề xuất tuần ({len(dx)})", "", "| id | loại | ai | công ty | lý do | nên làm |", "|---|---|---|---|---|---|"]
    L += [f"| {r['id']} | {r['loai']} | {r['ten']} | {r['cong_ty'] or ''} | {r['ly_do']} | {r['hanh_dong']} |" for r in dx[:40]]
    if len(dx) > 40:
        L.append(f"| … | còn {len(dx)-40} dòng trong DE-XUAT-TUAN.csv | | | | |")
    gom = {}
    for r in sop:
        k = conn().execute("SELECT khoa FROM member WHERE ma=?", (r["ma"],)).fetchone()[0] or r["cong_ty"]
        gom.setdefault((r["moc"], k, r["viec"]), []).append(r)
    L += ["", f"## Việc SOP người mới 7 ngày tới ({len(sop)} người, gom {len(gom)} việc theo lớp)", "",
          "| ngày | mốc | lớp | số người | việc (đăng chung trong nhóm lớp, nhắn riêng chỉ người đã đồng ý) |", "|---|---|---|---|---|"]
    L += [f"| {min(x['ngay'] for x in v)} | D+{mc} | {k} | {len(v)} | {vc} |"
          for (mc, k, vc), v in sorted(gom.items(), key=lambda kv: min(x['ngay'] for x in kv[1]))]
    L += ["", "Làm xong một dòng: `nuoi.py xong-sop <lớp> <mốc>`."]
    L += ["", "## Nhịp cộng đồng tuần này", ""] + [f"- {x.get('thu') or ('tháng' if 'thang' in x else 'quý')}: {x['viec']}" for x in C["nhip_cong_dong"]]
    L += ["", f"## Câu hỏi 14 ngày qua ({len(hoi)}) → nguyên liệu nội dung tuần sau (skill cau-hoi-thanh-noi-dung)", ""]
    L += [f"- {h['noi_dung']}" for h in hoi[:30]]
    (OUT / "BAO-CAO-TUAN.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"Xong → output/BAO-CAO-TUAN.md ({len(dx)} đề xuất, {len(sop)} việc SOP, {len(hoi)} câu hỏi)")


def main():
    p = argparse.ArgumentParser(description="linhx-nuoi-cong-dong")
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("init")
    x = s.add_parser("nhap"); x.add_argument("loai", choices=["thanh-vien", "su-kien", "don", "link"]); x.add_argument("file")
    for n in ("cham", "de-xuat", "suc-khoe", "tuan"):
        s.add_parser(n).add_argument("--ngay")
    x = s.add_parser("sop"); x.add_argument("--ngay"); x.add_argument("--so-ngay", type=int, default=7)
    x = s.add_parser("danh-dau"); x.add_argument("id", type=int); x.add_argument("trang_thai", choices=["nhan", "bo", "tu-choi", "da-lam"])
    x = s.add_parser("xong-sop"); x.add_argument("lop"); x.add_argument("moc", type=int)
    x = s.add_parser("link"); x.add_argument("hanh", choices=["tao"]); x.add_argument("--kenh", required=True)
    x.add_argument("--chien-dich", required=True); x.add_argument("--url", required=True); x.add_argument("--bai", default="")
    a = p.parse_args()
    {"init": cmd_init, "nhap": cmd_nhap, "cham": cmd_cham, "sop": cmd_sop, "de-xuat": cmd_de_xuat,
     "danh-dau": cmd_danh_dau, "xong-sop": cmd_xong_sop, "link": cmd_link, "suc-khoe": cmd_suc_khoe, "tuan": cmd_tuan}[a.cmd](a)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
