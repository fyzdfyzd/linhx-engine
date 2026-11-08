"""Vòng tự học mỗi ngày. Chạy cuối ngày (`kenhao hoc-ngay`), sau `so-lieu`.

Hệ thống học từ bốn nguồn tín hiệu:
  1. Số liệu bài: bài nào vượt trung vị tỷ lệ tương tác của chính kênh.
  2. Bàn đăng: Linh bấm Đăng nguyên văn, sửa rồi đăng, hay bỏ (kèm lý do). Đây là khẩu vị của người duyệt.
  3. Quan hệ: kiểu chạm nào, mục đích nào được người kia đáp lại trong 3 ngày.
  4. Cổng: agent bị chặn vì lý do gì nhiều nhất, tức agent đang đề xuất sai ở đâu.

Thay đổi có ba tầng, càng khó hoàn tác càng cần người:
  Tầng 1 (tự áp, có trần): hậu nghiệm Beta cho từng hook/trụ cột/cảm xúc/giờ/kiểu chạm, hệ số tỷ trọng
          trụ cột (mỗi ngày đổi tối đa ±0,1, kẹp 0,5–1,5, xét lại sau 7 ngày, kém thì tự hoàn).
  Tầng 2 (bấm một lần trên bàn đăng): bài học bằng lời (luật viết, giờ đăng, cách chạm). Nhận thì thành luật viết.
  Tầng 3 (chỉ Linh sửa): đề xuất đổi luật gốc hanh-vi / phong-cach / hang-rui-ro / flaw. Chỉ ghi vào báo cáo.

Hệ thống tự chấm chính nó: mỗi bài lúc đăng được dự báo xác suất "vượt trung vị" từ hậu nghiệm hiện có
(`bai.du_doan`). Điểm Brier theo tuần cho biết mô hình của kênh có đang đoán đúng hơn không.
Tính lại từ đầu mỗi ngày với trọng số giảm dần (nửa đời 21 ngày) nên chạy lại bao nhiêu lần cũng ra một kết quả."""
import json
import os
import random
import re
import statistics
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

from .db import bay_gio

NUA_DOI = 21
TOI_THIEU_BAI = 5        # mẫu tối thiểu mỗi nhóm để nêu một bài học cho người duyệt (tầng 2)
TIN_CAY = 0.9
TOI_THIEU_TU_AP = 10     # tầng 1 tự áp cần chắc hơn: nhiều chiều cùng so một lúc thì dễ gặp may
TIN_CAY_TU_AP = 0.95
BUOC_NGAY = 0.1
KEP = (0.5, 1.5)
CHIEU_BAI = ("hook", "tru_cot", "cam_xuc", "gio", "nen_tang")
# Tín hiệu đáp nào trả lời cho kiểu chạm nào. Đáp không có trong bảng (bình luận bài mình, chia sẻ, nhắn…)
# là đáp chung, chỉ quy cho chạm sâu nhất gần nhất, để like rẻ không ăn công của bình luận.
DAP_CHO = {"tra_loi_binh_luan_minh": "binh_luan", "thich_binh_luan_minh": "binh_luan", "theo_doi_lai": "theo_doi"}
DO_SAU = {"binh_luan": 3, "theo_doi": 2, "luu": 1, "thich": 1, "nhan": 3}


def _w(luc, nay):
    tuoi = (nay - datetime.fromisoformat(luc)).total_seconds() / 86400
    return 0.5 ** (max(0.0, tuoi) / NUA_DOI)


def _ty_le(r):
    return (r["like_"] + r["comment"] + r["share"] + r["save"]) / r["view"] if r["view"] else 0.0


def bai_co_so(con):
    return [dict(r) for r in con.execute("""SELECT b.id, b.hook, b.tru_cot, b.cam_xuc, b.nen_tang, b.dang_luc, b.du_doan,
        substr(b.dang_luc,12,2) AS gio, s.view, s.like_, s.comment, s.share, s.save
        FROM bai b JOIN so_lieu s ON s.id=(SELECT MAX(id) FROM so_lieu WHERE bai_id=b.id)
        WHERE b.trang_thai='da_dang'""")]


def _beta(nhom):
    """nhom: {khoa: [(trong_so, thanh_cong 0/1)]} → {khoa: (alpha, beta, n)}"""
    return {k: (1 + sum(w * s for w, s in ds), 1 + sum(w * (1 - s) for w, s in ds), len(ds)) for k, ds in nhom.items()}


def p_hon(a, b, r, mau=4000):
    """P(nhóm a tốt hơn nhóm b) ước bằng lấy mẫu Beta."""
    return sum(r.betavariate(*a[:2]) > r.betavariate(*b[:2]) for _ in range(mau)) / mau


def hau_nghiem(con, nay=None):
    """Tính lại mọi hậu nghiệm từ dữ liệu. Trả về {khoa: (alpha, beta, n)} và ngưỡng trung vị."""
    nay = nay or bay_gio()
    rows = bai_co_so(con)
    nguong = statistics.median(_ty_le(r) for r in rows) if rows else None
    nhom = defaultdict(list)
    for r in rows:
        s = 1 if _ty_le(r) > nguong else 0
        w = _w(r["dang_luc"], nay)
        for c in CHIEU_BAI:
            if r[c]:
                nhom[f"{c}:{r[c]}"].append((w, s))
    # Khẩu vị người duyệt: đăng nguyên văn = 1, sửa hoặc bỏ = 0
    for p in con.execute("""SELECT p.hanh_dong, p.luc, b.hook, b.tru_cot, b.cam_xuc FROM phan_hoi p JOIN bai b ON b.id=p.muc_id
                            WHERE p.loai_muc='bai' AND p.hanh_dong IN ('dang','sua','bo')"""):
        s = 1 if p["hanh_dong"] == "dang" else 0
        w = _w(p["luc"], nay)
        for c in ("hook", "tru_cot", "cam_xuc"):
            if p[c]:
                nhom[f"duyet:{c}:{p[c]}"].append((w, s))
    # Quan hệ: chạm đã làm có được đáp trong 3 ngày không, quy công đúng kiểu chạm
    cham = [dict(h) for h in con.execute("SELECT id, vong_id, loai, muc_dich, lam_luc FROM hanh_dong_ra WHERE trang_thai='da_lam' AND lam_luc IS NOT NULL")]
    duoc = set()
    for sk in con.execute("SELECT vong_id, loai, luc FROM su_kien_vong"):
        t = datetime.fromisoformat(sk["luc"])
        ung = [h for h in cham if h["vong_id"] == sk["vong_id"] and timedelta(0) <= t - datetime.fromisoformat(h["lam_luc"]) <= timedelta(days=3)]
        dung = DAP_CHO.get(sk["loai"])
        ung = [h for h in ung if h["loai"] == dung] if dung else ung
        if ung:
            h = max(ung, key=lambda h: (DO_SAU.get(h["loai"], 0), h["lam_luc"]))
            duoc.add(h["id"])
    for h in cham:
        if (nay - datetime.fromisoformat(h["lam_luc"])).days < 3:
            continue  # chưa đủ cửa sổ để biết
        w = _w(h["lam_luc"], nay)
        s = 1 if h["id"] in duoc else 0
        nhom[f"cham:{h['loai']}"].append((w, s))
        if h["muc_dich"]:
            nhom[f"cham_md:{h['muc_dich']}"].append((w, s))
    return _beta(nhom), nguong


def du_doan(con, bai, hn=None):
    """Xác suất bài vượt trung vị, ghép từ hậu nghiệm hook và trụ cột (trung bình hai mean)."""
    hn = hn if hn is not None else hau_nghiem(con)[0]
    ps = [hn[k][0] / (hn[k][0] + hn[k][1]) for k in (f"hook:{bai['hook']}", f"tru_cot:{bai['tru_cot']}") if k in hn]
    return round(sum(ps) / len(ps), 3) if ps else 0.5


def goi_y(con, chieu, lua_chon, seed=None):
    """Thompson sampling: rút một mẫu từ hậu nghiệm từng lựa chọn, chọn cái cao nhất.
    Lựa chọn chưa có dữ liệu dùng Beta(1,1) nên vẫn được thử (khám phá)."""
    hn, _ = hau_nghiem(con)
    r = random.Random(seed)
    diem = {x: r.betavariate(*(hn.get(f"{chieu}:{x}", (1, 1, 0))[:2])) for x in lua_chon}
    return max(diem, key=diem.get), {k: round(v, 3) for k, v in diem.items()}


def nhom_ly_do(l):
    """Gom lý do chặn về một loại, bỏ tên người và con số, để mỗi loại lỗi chỉ thành một bài học."""
    if "không được đáp" in l:
        return "chạm người đã 3 lần không đáp lại"
    if "phải nghỉ" in l:
        return "chạm lại cùng người trước thời gian nghỉ"
    if "cho đúng bài này rồi" in l:
        return "chạm trùng một bài đã chạm"
    if "hết hạn mức" in l:
        return "vượt hạn mức chạm của giai đoạn"
    return re.sub(r"\d+", "N", l.split(":")[0])[:60]


def _brier(con):
    ra = []
    rows = bai_co_so(con)
    if not rows:
        return ra
    nguong = statistics.median(_ty_le(r) for r in rows)
    theo_tuan = defaultdict(list)
    for r in rows:
        if r["du_doan"] is None:
            continue
        s = 1 if _ty_le(r) > nguong else 0
        y, w, _ = date.fromisoformat(r["dang_luc"][:10]).isocalendar()
        tuan = f"{y}-W{w:02d}"
        theo_tuan[tuan].append((r["du_doan"] - s) ** 2)
    for t in sorted(theo_tuan):
        ra.append({"tuan": t, "bai": len(theo_tuan[t]), "brier": round(sum(theo_tuan[t]) / len(theo_tuan[t]), 3)})
    return ra


def _ghi_bai_hoc(con, nguon, khoa, noi_dung, bang_chung, tang, nay):
    """Bài học có khoá ổn định: hôm sau tín hiệu còn thì cập nhật bằng chứng, không đẻ bản sao."""
    cu = con.execute("SELECT id, trang_thai FROM bai_hoc WHERE khoa=?", (khoa,)).fetchone()
    if cu:
        if cu["trang_thai"] in ("de_xuat", "cu"):  # thẻ bị rút hôm trước mà nay tín hiệu quay lại thì đưa lại lên bàn
            con.execute("UPDATE bai_hoc SET noi_dung=?, bang_chung=?, luc=?, trang_thai='de_xuat' WHERE id=?", (noi_dung, bang_chung, nay, cu["id"]))
        return cu["id"], False
    cur = con.execute("INSERT INTO bai_hoc(nguon, khoa, noi_dung, bang_chung, tang, trang_thai, luc) VALUES (?,?,?,?,?,?,?)",
                      (nguon, khoa, noi_dung, bang_chung, tang, "de_xuat" if tang >= 2 else "ap_dung", nay))
    return cur.lastrowid, True


def _he_so_tru_cot(con, nv, hn, nay_s, ngay):
    """Tầng 1: hệ số nhân tỷ trọng trụ cột. Chỉ đổi khi đủ bài và chênh đủ tin cậy so với trung bình kênh."""
    ra = []
    ma = [t["ma"] for t in nv["tru_cot"]]
    co = [hn[f"tru_cot:{m}"] for m in ma if f"tru_cot:{m}" in hn]
    if not co:
        return ra
    tb = sum(a / (a + b) for a, b, _ in co) / len(co)
    for m in ma:
        k = f"tru_cot:{m}"
        cu_row = con.execute("SELECT gia_tri FROM tham_so WHERE khoa=?", (f"he_so:{m}",)).fetchone()
        cu = cu_row["gia_tri"] if cu_row else 1.0
        if k not in hn or hn[k][2] < TOI_THIEU_TU_AP:
            continue
        a, b, n = hn[k]
        muc_tieu = max(KEP[0], min(KEP[1], (a / (a + b)) / tb if tb else 1.0))
        moi = round(cu + max(-BUOC_NGAY, min(BUOC_NGAY, muc_tieu - cu)), 3)
        if abs(muc_tieu - cu) < 0.1:
            continue  # vùng trễ: chênh nhỏ thì giữ nguyên để hệ số không lật qua lật lại mỗi ngày
        con.execute("INSERT OR REPLACE INTO tham_so(khoa, gia_tri, alpha, beta, n, cap_nhat) VALUES (?,?,?,?,?,?)",
                    (f"he_so:{m}", moi, a, b, n, nay_s))
        con.execute("INSERT INTO thay_doi(khoa, cu, moi, ly_do, bang_chung, luc, xet_lai_ngay) VALUES (?,?,?,?,?,?,?)",
                    (f"he_so:{m}", cu, moi, f"trụ cột {m} vượt trung vị {a / (a + b):.0%} so với trung bình kênh {tb:.0%}",
                     json.dumps({"alpha": round(a, 2), "beta": round(b, 2), "n": n}), nay_s, (ngay + timedelta(days=7)).isoformat()))
        ra.append({"khoa": f"he_so:{m}", "cu": cu, "moi": moi, "n": n})
    return ra


def _xet_lai(con, nay_s, ngay):
    """Thay đổi tầng 1 đến hạn: so tỷ lệ vượt trung vị của trụ cột đó 7 ngày sau đổi với mức trước đổi. Kém đi rõ thì hoàn."""
    ra = []
    rows = bai_co_so(con)
    if not rows:
        return ra
    nguong = statistics.median(_ty_le(r) for r in rows)
    for td in con.execute("SELECT * FROM thay_doi WHERE ket_qua IS NULL AND xet_lai_ngay<=?", (ngay.isoformat(),)).fetchall():
        m = td["khoa"].split(":", 1)[1]
        bc = json.loads(td["bang_chung"])
        truoc = bc["alpha"] / (bc["alpha"] + bc["beta"])
        sau = [r for r in rows if r["tru_cot"] == m and td["luc"] <= r["dang_luc"] <= (datetime.fromisoformat(td["luc"]) + timedelta(days=7)).isoformat()]
        if len(sau) < 3:
            kq = "giu_chua_du_bai"
        else:
            ty = sum(1 for r in sau if _ty_le(r) > nguong) / len(sau)
            tang = td["moi"] > td["cu"]
            kq = "hoan" if (tang and ty < truoc - 0.15) else "giu"
            if kq == "hoan":
                con.execute("UPDATE tham_so SET gia_tri=?, cap_nhat=? WHERE khoa=?", (td["cu"], nay_s, td["khoa"]))
        con.execute("UPDATE thay_doi SET ket_qua=? WHERE id=?", (kq, td["id"]))
        ra.append({"khoa": td["khoa"], "ket_qua": kq})
    return ra


def chay(con, home, nv, hv):
    nay = bay_gio()
    nay_s = nay.isoformat(timespec="seconds")
    ngay = nay.date()
    r = random.Random(f"hoc|{ngay}")
    hn, nguong = hau_nghiem(con, nay)
    for k, (a, b, n) in hn.items():
        con.execute("INSERT OR REPLACE INTO tham_so(khoa, gia_tri, alpha, beta, n, cap_nhat) VALUES (?,?,?,?,?,?)",
                    (k, round(a / (a + b), 4), a, b, n, nay_s))
    bao = {"ngay": ngay.isoformat(), "nguong_trung_vi": nguong, "bai_hoc_moi": [], "thay_doi": [], "xet_lai": [], "tang3": []}

    # 1 + 2 + 3. So sánh trong từng chiều: nhóm dẫn đầu có chắc hơn nhóm thứ hai không
    nhan = {"hook": "hook", "tru_cot": "trụ cột", "cam_xuc": "cảm xúc nhắm tới", "gio": "giờ đăng", "nen_tang": "nền tảng",
            "duyet:hook": "Linh duyệt nguyên văn theo hook", "duyet:tru_cot": "Linh duyệt nguyên văn theo trụ cột",
            "duyet:cam_xuc": "Linh duyệt nguyên văn theo cảm xúc", "cham": "kiểu chạm được đáp", "cham_md": "mục đích chạm được đáp"}
    for chieu, ten in nhan.items():
        ds = sorted(((k.rsplit(":", 1)[1], v) for k, v in hn.items() if k.rsplit(":", 1)[0] == chieu and v[2] >= TOI_THIEU_BAI),
                    key=lambda x: -x[1][0] / (x[1][0] + x[1][1]))
        if len(ds) < 2:
            continue
        (a_ten, a), (b_ten, b) = ds[0], ds[1]
        cuoi_ten, cuoi = ds[-1]
        # Khẩu vị người duyệt và kiểu chạm: điều cần biết là nhóm nào tệ hẳn, nên so đầu với cuối.
        # Số liệu bài: điều cần biết là cái thắng có chắc thắng không, nên so đầu với nhóm thứ hai.
        p = p_hon(a, cuoi, r) if chieu.startswith(("duyet:", "cham")) else p_hon(a, b, r)
        tl = lambda v: v[0] / (v[0] + v[1])  # noqa: E731
        if p >= TIN_CAY:
            if chieu.startswith("duyet:"):
                nd = (f"{ten}: `{cuoi_ten}` hay bị sửa hoặc bỏ (đăng nguyên văn {tl(cuoi):.0%}, {cuoi[2]} lần) so với `{a_ten}` ({tl(a):.0%}). "
                      f"Agent đọc các lần sửa bài `{cuoi_ten}` và rút luật viết.")
                tang = 2
            elif chieu == "gio":
                nd = f"Giờ {a_ten}h vượt trung vị {tl(a):.0%} so với {b_ten}h {tl(b):.0%}. Đề nghị dời khung đăng sang {a_ten}h trong nen-tang.md."
                tang = 2
            elif chieu.startswith("cham"):
                nd = f"{ten}: `{a_ten}` được đáp {tl(a):.0%} ({a[2]} lần), `{cuoi_ten}` chỉ {tl(cuoi):.0%}. Ưu tiên `{a_ten}` trong phiên chạm."
                tang = 2
            elif a[2] >= TOI_THIEU_TU_AP and p >= TIN_CAY_TU_AP:
                nd = f"{ten}: `{a_ten}` vượt trung vị {tl(a):.0%} ({a[2]} bài) so với `{b_ten}` {tl(b):.0%}. Đã đưa vào gợi ý (tự áp)."
                tang = 1
            else:
                continue  # tín hiệu số liệu còn mỏng: chờ thêm bài, không nêu
            if chieu == "cham_md" and con.execute("SELECT 1 FROM bai_hoc WHERE khoa LIKE 'cham>%' AND trang_thai IN ('de_xuat','ap_dung')").fetchone():
                continue  # mục đích trùng ý với kiểu chạm vừa nêu: không đẻ hai thẻ cho một ý
            khoa = f"{chieu}<{cuoi_ten}" if chieu.startswith("duyet:") else f"{chieu}>{a_ten}"
            # Thẻ cũ cùng chiều mà nay không còn đúng thì rút khỏi bàn đăng, để Linh không bấm vào bài học lỗi thời
            con.execute("UPDATE bai_hoc SET trang_thai='cu' WHERE trang_thai='de_xuat' AND khoa LIKE ? AND khoa<>?",
                        (chieu + ("<%" if chieu.startswith("duyet:") else ">%"), khoa))
            id_, moi = _ghi_bai_hoc(con, "so_lieu" if ":" not in chieu else chieu.split(":")[0], khoa, nd,
                                    json.dumps({"p": round(p, 3), "dan_dau": a_ten, "n_dan": a[2], "thu_hai": b_ten, "n_hai": b[2]}, ensure_ascii=False), tang, nay_s)
            if moi:
                bao["bai_hoc_moi"].append({"id": id_, "tang": tang, "noi_dung": nd})

    # 4. Agent tự soi: tỷ lệ đề xuất chạm bị cổng chặn trong 7 ngày
    tu = (nay - timedelta(days=7)).isoformat()
    tong = con.execute("SELECT COUNT(*) FROM hanh_dong_ra WHERE tao_luc>=?", (tu,)).fetchone()[0]
    chan = con.execute("SELECT ly_do_chan FROM hanh_dong_ra WHERE tao_luc>=? AND trang_thai='bi_chan'", (tu,)).fetchall()
    if tong >= 20 and len(chan) / tong > 0.3:
        dem = Counter(nhom_ly_do(l) for x in chan for l in json.loads(x["ly_do_chan"]))
        top, so = dem.most_common(1)[0]
        nd = (f"Agent tự soi: {len(chan)}/{tong} đề xuất chạm 7 ngày qua bị cổng chặn ({len(chan) / tong:.0%}). Lý do hay gặp nhất: “{top}” ({so} lần). "
              "Trước khi đề xuất, agent lọc người theo lý do này.")
        id_, moi = _ghi_bai_hoc(con, "cong", f"cong>{top}", nd, json.dumps(dict(dem.most_common(5)), ensure_ascii=False), 1, nay_s)
        if moi:
            bao["bai_hoc_moi"].append({"id": id_, "tang": 1, "noi_dung": nd})

    # 5. Lần sửa chưa rút thành luật: chuyển cho agent (tầng 2)
    sua = con.execute("""SELECT d.id, d.bai_id, d.gop_y, d.ban_cu, d.ban_moi, b.hook FROM duyet d JOIN bai b ON b.id=d.bai_id
                         WHERE d.quyet_dinh IN ('sua','gop_y','bo') AND d.da_hoc=0 ORDER BY d.id DESC LIMIT 12""").fetchall()
    bao["sua_chua_hoc"] = [dict(x) for x in sua]
    bo = Counter(x["ly_do"] for x in con.execute("SELECT ly_do FROM phan_hoi WHERE hanh_dong='bo' AND luc>=?", (tu,)) if x["ly_do"])
    bao["ly_do_bo_7_ngay"] = dict(bo.most_common())
    if bo and sum(bo.values()) >= 3:
        top, so = bo.most_common(1)[0]
        bao["tang3"].append(f"Linh bỏ {sum(bo.values())} mục trong 7 ngày, nhiều nhất vì “{top}” ({so}). Nếu là “sai giọng” lặp lại, xem lại phần giọng trong hồ sơ persona (Linh sửa).")

    # 6. Tầng 1: hệ số trụ cột + xét lại thay đổi cũ
    bao["thay_doi"] = _he_so_tru_cot(con, nv, hn, nay_s, ngay)
    bao["xet_lai"] = _xet_lai(con, nay_s, ngay)
    bao["brier_theo_tuan"] = _brier(con)
    bao["hau_nghiem"] = {k: {"ty_le": round(a / (a + b), 3), "n": n} for k, (a, b, n) in sorted(hn.items())}

    _viet_file(home, con, bao)
    con.commit()
    return bao


def ty_trong_hoc(con, nv):
    """Tỷ trọng trụ cột sau khi nhân hệ số học được, chuẩn hoá lại và giữ sàn 50% tỷ trọng gốc để vẫn khám phá."""
    goc = {t["ma"]: t["ty_trong"] for t in nv["tru_cot"]}
    hs = {m: (con.execute("SELECT gia_tri FROM tham_so WHERE khoa=?", (f"he_so:{m}",)).fetchone() or [1.0])[0] for m in goc}
    tho = {m: max(goc[m] * 0.5, goc[m] * hs[m]) for m in goc}
    tong = sum(tho.values())
    return {m: round(v / tong, 3) for m, v in tho.items()}


def _viet_file(home, con, bao):
    ngay = bao["ngay"]
    out = [f"# Học ngày {ngay}", ""]
    out.append(f"Ngưỡng thành công: vượt trung vị tỷ lệ tương tác của kênh ({bao['nguong_trung_vi']:.1%})." if bao["nguong_trung_vi"] else "Chưa có số liệu bài.")
    out += ["", "## Bài học mới", ""]
    out += [f"- [tầng {b['tang']}] {b['noi_dung']}" for b in bao["bai_hoc_moi"]] or ["- Không có tín hiệu đủ tin cậy hôm nay (cần ≥ 5 mẫu mỗi nhóm và P ≥ 0,9)."]
    out += ["", "## Tự áp hôm nay (tầng 1)", ""]
    out += [f"- {t['khoa']}: {t['cu']} → {t['moi']} (n = {t['n']}), xét lại sau 7 ngày" for t in bao["thay_doi"]] or ["- Không đổi."]
    if bao["xet_lai"]:
        out += ["", "## Xét lại thay đổi cũ", ""] + [f"- {x['khoa']}: {x['ket_qua']}" for x in bao["xet_lai"]]
    out += ["", "## Hệ thống tự chấm (Brier, thấp là đoán tốt; 0,25 là đoán bừa)", ""]
    out += [f"- Tuần {b['tuan']}: {b['brier']} ({b['bai']} bài)" for b in bao["brier_theo_tuan"]] or ["- Chưa có bài có dự báo."]
    out += ["", "## Việc của agent tối nay", "",
            "1. Đọc các lần sửa dưới đây, rút tối đa 2 luật viết, ghi bằng `bai-hoc-them --tang 2` (Linh bấm nhận trên bàn đăng).",
            "2. Đọc bài học tầng 1 ở trên trước khi viết bài ngày mai; chọn hook/cảm xúc bằng `goi-y`.", ""]
    for s in bao["sua_chua_hoc"]:
        out.append(f"- duyệt #{s['id']} bài {s['bai_id']} (hook {s['hook']}): {s['gop_y'] or ''}")
        if s["ban_cu"] and s["ban_moi"]:
            out += [f"  - trước: {s['ban_cu'][:160]}", f"  - sau: {s['ban_moi'][:160]}"]
    if bao["tang3"]:
        out += ["", "## Đề xuất cho Linh (tầng 3, agent không tự sửa)", ""] + [f"- {x}" for x in bao["tang3"]]
    os.makedirs(os.path.join(home, "bao-cao"), exist_ok=True)
    open(os.path.join(home, "bao-cao", f"HOC-{ngay}.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    # Bộ nhớ của kênh: agent đọc file này đầu mỗi phiên. Chỉ giữ 20 bài học đang áp dụng mới nhất.
    ap = con.execute("SELECT noi_dung, luc FROM bai_hoc WHERE trang_thai='ap_dung' ORDER BY luc DESC LIMIT 20").fetchall()
    cho = con.execute("SELECT COUNT(*) FROM bai_hoc WHERE trang_thai='de_xuat'").fetchone()[0]
    mem = ["# Bài học của kênh", "", f"Cập nhật {ngay} bởi `hoc-ngay`. Agent đọc file này đầu mỗi phiên. {cho} bài học đang chờ Linh bấm nhận.", ""]
    mem += [f"- ({x['luc'][:10]}) {x['noi_dung']}" for x in ap] or ["- Chưa có."]
    open(os.path.join(home, "ho-so", "bai-hoc.md"), "w", encoding="utf-8").write("\n".join(mem) + "\n")
