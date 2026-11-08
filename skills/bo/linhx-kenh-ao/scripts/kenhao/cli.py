"""CLI `kenhao`: tay chân và cổng chặn cho agent nuôi kênh người ảo.
Agent (Claude/agy) lo phần phán đoán: đọc, tiêu hoá, viết, chấm, soạn trả lời, rút bài học.
CLI lo phần không được sai: lưu trạng thái, kiểm luật, hạn mức, nhãn AI, nhật ký."""
import argparse
import json
import os
import random
import shutil
import sys
from collections import Counter
from datetime import date, datetime, timedelta

from . import ban_dang, cong, fan as fan_mod, hanh_vi, hoc, hoc_ngay, hop_thu, persona as persona_mod
from .adapters import lay as lay_adapter
from .db import bay_gio, dem_hanh_dong, ghi_hanh_dong, ghi_nhat_ky, mo
from .luat import doc, kiem_nhan_vat

GOC_PLUGIN = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def in_(x):
    print(json.dumps(x, ensure_ascii=False, indent=1) if not isinstance(x, str) else x)


def _home(a):
    return os.path.abspath(a.home or os.environ.get("KENHAO_HOME") or "kenh-ao")


def _ctx(a):
    home = _home(a)
    con = mo(home)
    return home, con, doc(home, "nhan_vat"), doc(home, "hanh_vi")


def _adapter(a, cfg, vai):
    ten = "thu" if (a.thu or os.environ.get("KENHAO_THU") == "1") else cfg.get(f"{vai}_adapter", "thu")
    return lay_adapter(ten)


def _now():
    return bay_gio().isoformat(timespec="seconds")


# ---------- khởi tạo, hồ sơ ----------

def c_init(a):
    home = _home(a)
    os.makedirs(home, exist_ok=True)
    dich = os.path.join(home, "ho-so")
    if not os.path.exists(dich):
        shutil.copytree(os.path.join(GOC_PLUGIN, "mau", "ho-so"), dich)
    for d in ("outbox", "bao-cao", "doc-vao"):
        os.makedirs(os.path.join(home, d), exist_ok=True)
    mo(home).close()
    in_(f"Đã tạo kênh ở {home}. Sửa ho-so/nhan-vat.md trước, rồi chạy `kiem-ho-so`.")


def c_kiem(a):
    home = _home(a)
    loi = kiem_nhan_vat(doc(home, "nhan_vat"))
    for t in ("hang", "diem", "nen_tang", "hanh_vi"):
        try:
            doc(home, t)
        except Exception as e:  # noqa: BLE001
            loi.append(f"{t}: {e}")
    in_({"ok": not loi, "loi": loi})
    sys.exit(1 if loi else 0)


# ---------- khung hành vi: vòng, đọc, tiêu hoá, trend, phiên, chạm ----------

def c_giai_doan(a):
    home, con, nv, hv = _ctx(a)
    gd, tuoi, ke, tieu_chi, cs = hanh_vi.giai_doan_hien_tai(con, nv, hv)
    hap, tao, can = hanh_vi.ty_le_hap_thu(con, hv, them_tao=0)
    in_({"giai_doan": gd["ma"], "ten": gd["ten"], "y_nghia": gd["y_nghia"], "tuoi_ngay": tuoi,
         "han_muc_ngay": gd["han_muc_ngay"], "len_tiep": ke["ma"] if ke else None, "tieu_chi_len": tieu_chi,
         "hap_thu_7_ngay": hap, "tao_7_ngay": tao, "ty_le": round(hap / tao, 1) if tao else None, "can": can})


def c_vong_them(a):
    home, con, nv, hv = _ctx(a)
    con.execute("INSERT OR IGNORE INTO vong(nen_tang, ma_ngoai, ten, nhom, ly_do, la_minh, la_nha, them_luc) VALUES (?,?,?,?,?,?,?,?)",
                (a.nen_tang, a.ma, a.ten, a.nhom, a.ly_do, int(a.la_minh), int(a.la_nha), _now()))
    ghi_nhat_ky(con, "vong_them", vars(a) | {"func": None})
    con.commit()
    in_(dict(con.execute("SELECT * FROM vong WHERE nen_tang=? AND ma_ngoai=?", (a.nen_tang, a.ma)).fetchone()))


def c_vong_ds(a):
    home, con, nv, hv = _ctx(a)
    rows = con.execute("SELECT * FROM vong ORDER BY bac_thang DESC, diem_tin DESC").fetchall()
    in_([dict(r) | {"thang": hanh_vi.THANG[r["bac_thang"]]} for r in rows])


def c_doc_nhap(a):
    """Nhập lượt đọc từ NDJSON (extension social của Linh, LAB039, hoặc agent tự ghi khi lướt).
    Mỗi dòng: {nen_tang, tac_gia_ma, tac_gia, url, noi_dung, chu_de:[...], tuong_tac, dang_luc}."""
    home, con, nv, hv = _ctx(a)
    moi = 0
    for dong in open(a.file, encoding="utf-8"):
        if not dong.strip():
            continue
        d = json.loads(dong)
        v = con.execute("SELECT id FROM vong WHERE nen_tang=? AND ma_ngoai=?", (d["nen_tang"], d["tac_gia_ma"])).fetchone()
        cur = con.execute("INSERT OR IGNORE INTO luot_doc(vong_id, nen_tang, url, tac_gia, noi_dung, chu_de, tuong_tac, dang_luc, doc_luc) VALUES (?,?,?,?,?,?,?,?,?)",
                          (v["id"] if v else None, d["nen_tang"], d["url"], d["tac_gia"], d["noi_dung"],
                           json.dumps(d.get("chu_de", []), ensure_ascii=False), d.get("tuong_tac", 0), d.get("dang_luc"), d.get("doc_luc") or _now()))
        if cur.rowcount:
            moi += 1
            if v:
                con.execute("UPDATE vong SET so_bai_da_doc=so_bai_da_doc+1 WHERE id=?", (v["id"],))
                n = con.execute("SELECT so_bai_da_doc FROM vong WHERE id=?", (v["id"],)).fetchone()[0]
                if n >= hv["luat_cham"]["doc_de_len_da_doc"]:
                    hanh_vi.len_thang(con, v["id"], "da_doc")
    ghi_nhat_ky(con, "doc_nhap", {"file": a.file, "moi": moi})
    con.commit()
    in_({"luot_doc_moi": moi})


def c_doc_ds(a):
    home, con, nv, hv = _ctx(a)
    q = "SELECT id, tac_gia, nen_tang, substr(noi_dung,1,160) AS trich, chu_de, tuong_tac, dang_luc FROM luot_doc"
    q += " WHERE id NOT IN (SELECT value FROM tieu_hoa, json_each(tieu_hoa.luot_doc_ids))" if a.chua_tieu_hoa else ""
    in_([dict(r) for r in con.execute(q + " ORDER BY id DESC LIMIT ?", (a.n,))])


def c_tieu_hoa(a):
    home, con, nv, hv = _ctx(a)
    if a.loai not in hv["tieu_hoa_loai"]:
        sys.exit(f"loại tiêu hoá phải là: {', '.join(hv['tieu_hoa_loai'])}")
    ids = [int(x) for x in a.tu.split(",")]
    co = con.execute(f"SELECT COUNT(*) FROM luot_doc WHERE id IN ({','.join('?' * len(ids))})", ids).fetchone()[0]
    if co != len(ids):
        sys.exit("có id lượt đọc không tồn tại")
    if len(a.ghi_chu.strip()) < 30:
        sys.exit("ghi chú tiêu hoá quá ngắn: viết rõ mình rút ra gì")
    cur = con.execute("INSERT INTO tieu_hoa(luot_doc_ids, loai, ghi_chu, luc) VALUES (?,?,?,?)",
                      (json.dumps(ids), a.loai, a.ghi_chu, _now()))
    con.commit()
    in_({"tieu_hoa_id": cur.lastrowid})


def c_trend(a):
    home, con, nv, hv = _ctx(a)
    tu = (bay_gio() - timedelta(days=a.ngay)).isoformat(timespec="seconds")
    dem, nang = Counter(), Counter()
    for r in con.execute("SELECT chu_de, tuong_tac FROM luot_doc WHERE doc_luc>=?", (tu,)):
        for cd in json.loads(r["chu_de"] or "[]"):
            dem[cd] += 1
            nang[cd] += r["tuong_tac"] or 0
    tru = {t["ma"] for t in nv["tru_cot"]}
    bang = [{"chu_de": k, "so_bai": dem[k], "tuong_tac": nang[k], "tb_tuong_tac": round(nang[k] / dem[k]),
             "khop_tru_cot": k in tru} for k, _ in dem.most_common(a.top)]
    duong = os.path.join(home, "bao-cao", f"TREND-{bay_gio().date()}.md")
    with open(duong, "w", encoding="utf-8") as f:
        f.write(f"# Trend {a.ngay} ngày tới {bay_gio().date()}\n\n| Chủ đề | Bài | Tổng tương tác | TB | Khớp trụ cột |\n|---|---|---|---|---|\n")
        for b in bang:
            f.write(f"| {b['chu_de']} | {b['so_bai']} | {b['tuong_tac']} | {b['tb_tuong_tac']} | {'có' if b['khop_tru_cot'] else ''} |\n")
        f.write("\nAgent ghi phần đọc hiểu (vì sao nổi, ai dẫn, mình nói gì được khác) bằng `tieu-hoa --loai trend`.\n")
    ghi_nhat_ky(con, "trend", {"file": duong, "top": bang[:5]})
    con.commit()
    in_({"file": duong, "trend": bang})


def c_phien(a):
    home, con, nv, hv = _ctx(a)
    ngay = date.fromisoformat(a.ngay) if a.ngay else bay_gio().date()
    gd, phien = hanh_vi.lap_phien(con, nv, hv, ngay)
    in_({"ngay": ngay.isoformat(), "giai_doan": gd["ma"], "han_muc_ngay": gd["han_muc_ngay"], "phien": phien})


def c_cham_de_xuat(a):
    home, con, nv, hv = _ctx(a)
    hd = {"vong_id": a.nguoi, "luot_doc_id": a.doc, "loai": a.loai, "muc_dich": a.muc_dich,
          "vi_sao": a.vi_sao, "noi_dung": a.noi_dung, "chi_tiet": a.chi_tiet}
    loi = hanh_vi.cong_ra(con, nv, hv, hd)
    gd, *_ = hanh_vi.giai_doan_hien_tai(con, nv, hv)
    tu_lam = (not loi) and a.loai in gd.get("tu_lam_khong_duyet", [])
    tt = "bi_chan" if loi else ("duyet" if tu_lam else "de_xuat")
    cur = con.execute("INSERT INTO hanh_dong_ra(vong_id, luot_doc_id, loai, muc_dich, vi_sao, noi_dung, chi_tiet, trang_thai, ly_do_chan, tao_luc) VALUES (?,?,?,?,?,?,?,?,?,?)",
                      (a.nguoi, a.doc, a.loai, a.muc_dich, a.vi_sao, a.noi_dung, a.chi_tiet, tt, json.dumps(loi, ensure_ascii=False), _now()))
    ghi_nhat_ky(con, "cham_de_xuat", {"id": cur.lastrowid, "trang_thai": tt, "loi": loi})
    con.commit()
    in_({"id": cur.lastrowid, "trang_thai": tt, "ly_do_chan": loi})


def c_cham_duyet(a):
    home, con, nv, hv = _ctx(a)
    hd = con.execute("SELECT * FROM hanh_dong_ra WHERE id=?", (a.id,)).fetchone()
    if hd["trang_thai"] != "de_xuat":
        sys.exit(f"hành động ở trạng thái {hd['trang_thai']}")
    if a.bo:
        con.execute("UPDATE hanh_dong_ra SET trang_thai='bo' WHERE id=?", (a.id,))
    else:
        nd = a.sua or hd["noi_dung"]
        moi = dict(hd) | {"noi_dung": nd}
        loi = hanh_vi.cong_ra(con, nv, hv, moi | {"_bo_qua_id": a.id})
        loi = [l for l in loi if "hết hạn mức" not in l]  # chính nó đang chiếm một suất
        if loi:
            sys.exit("vẫn bị chặn: " + "; ".join(loi))
        con.execute("UPDATE hanh_dong_ra SET trang_thai='duyet', noi_dung=? WHERE id=?", (nd, a.id))
    con.commit()
    in_(dict(con.execute("SELECT id, trang_thai, noi_dung FROM hanh_dong_ra WHERE id=?", (a.id,)).fetchone()))


def c_cham_viec(a):
    """Danh sách việc chạm đã duyệt để thực hiện: Linh tự làm trên app, hoặc trình duyệt có người xem.
    Phần lớn nền tảng không có API chính thức để thích/bình luận bài người khác."""
    home, con, nv, hv = _ctx(a)
    rows = con.execute("""SELECT h.id, h.loai, h.muc_dich, h.vi_sao, h.noi_dung, v.ten, v.nen_tang, d.url
                          FROM hanh_dong_ra h JOIN vong v ON v.id=h.vong_id LEFT JOIN luot_doc d ON d.id=h.luot_doc_id
                          WHERE h.trang_thai='duyet' ORDER BY h.id""").fetchall()
    in_([dict(r) for r in rows])


def c_cham_xong(a):
    home, con, nv, hv = _ctx(a)
    hd = con.execute("SELECT * FROM hanh_dong_ra WHERE id=?", (a.id,)).fetchone()
    if hd["trang_thai"] != "duyet":
        sys.exit(f"chỉ đánh dấu xong việc đã duyệt (đang: {hd['trang_thai']})")
    con.execute("UPDATE hanh_dong_ra SET trang_thai='da_lam', lam_luc=? WHERE id=?", (_now(), a.id))
    con.execute("UPDATE vong SET cham_khong_dap=cham_khong_dap+1 WHERE id=?", (hd["vong_id"],))
    bac = {"thich": "da_cham", "luu": "da_cham", "theo_doi": "da_cham", "binh_luan": "da_gop_chuyen"}.get(hd["loai"])
    if bac:
        hanh_vi.len_thang(con, hd["vong_id"], bac)
    con.commit()
    in_({"id": a.id, "trang_thai": "da_lam"})


def c_dap(a):
    """Ghi tín hiệu người kia đáp lại. Chỉ tín hiệu hai chiều mới cộng điểm tin."""
    home, con, nv, hv = _ctx(a)
    diem = hv["diem_tin"]["su_kien"].get(a.loai)
    if diem is None:
        sys.exit(f"loại đáp phải là: {', '.join(hv['diem_tin']['su_kien'])}")
    con.execute("INSERT INTO su_kien_vong(vong_id, loai, diem, luc, ghi_chu) VALUES (?,?,?,?,?)",
                (a.nguoi, a.loai, diem, _now(), a.ghi_chu))
    con.execute("UPDATE vong SET cham_khong_dap=0 WHERE id=?", (a.nguoi,))
    bac = hv["diem_tin"]["len_thang"].get(a.loai)
    if bac:
        hanh_vi.len_thang(con, a.nguoi, bac)
    tin = hanh_vi.cap_nhat_tin(con, hv, a.nguoi)
    if tin >= hv["diem_tin"]["dong_minh_tu"]:
        hanh_vi.len_thang(con, a.nguoi, "dong_minh")
    con.commit()
    r = con.execute("SELECT ten, bac_thang, diem_tin FROM vong WHERE id=?", (a.nguoi,)).fetchone()
    in_({"nguoi": r["ten"], "thang": hanh_vi.THANG[r["bac_thang"]], "diem_tin": r["diem_tin"]})


# ---------- xưởng persona ----------

def c_persona_gan(a):
    home, con, nv, hv = _ctx(a)
    cx = [c.strip() for c in a.cam_xuc.split(",")]
    sai = [c for c in cx if c not in hv["cam_xuc"]]
    if sai:
        sys.exit(f"cảm xúc không có trong danh sách hanh-vi.md: {', '.join(sai)}")
    if a.phan_ung not in hv["phan_ung"]:
        sys.exit(f"phản ứng phải là: {', '.join(hv['phan_ung'])}")
    con.execute("INSERT OR REPLACE INTO quan_sat_persona(luot_doc_id, kieu, cam_xuc, phan_ung, flaw, giong, ghi_chu, luc) VALUES (?,?,?,?,?,?,?,?)",
                (a.doc, a.kieu, json.dumps(cx, ensure_ascii=False), a.phan_ung, a.flaw, a.giong, a.ghi_chu, _now()))
    con.commit()
    in_({"doc": a.doc, "kieu": a.kieu})


def c_persona_xep_hang(a):
    home, con, nv, hv = _ctx(a)
    bang = persona_mod.xep_hang(con)
    duong = os.path.join(home, "bao-cao", f"PERSONA-{bay_gio().date()}.md")
    with open(duong, "w", encoding="utf-8") as f:
        f.write(f"# Kiểu nhân vật làm người ta phản ứng, tới {bay_gio().date()}\n\n")
        f.write("| Kiểu | Bài | TB tương tác | Cảm xúc chính | Phản ứng | Khuyết điểm hay gặp | Tín hiệu |\n|---|---|---|---|---|---|---|\n")
        for b in bang:
            f.write(f"| {b['kieu']} | {b['so_bai']} | {b['tb_tuong_tac']} | {', '.join(b['cam_xuc'])} | "
                    f"{', '.join(f'{k} {v}' for k, v in b['phan_ung'].items())} | {'; '.join(b['flaw_hay_gap'])} | {b['tin_hieu']} |\n")
        f.write("\nAgent dùng bảng này để phát triển persona ứng viên trong ho-so/persona/ (bắt buộc có flaw, theo phong-cach.md), rồi `persona-kiem`.\n")
    in_({"file": duong, "xep_hang": bang})


def c_persona_kiem(a):
    home, con, nv, hv = _ctx(a)
    pc = doc(home, "phong_cach")
    thu_muc = os.path.join(home, "ho-so", "persona")
    kq = {}
    for ten in sorted(os.listdir(thu_muc)) if os.path.isdir(thu_muc) else []:
        if ten.endswith(".md") and not ten.startswith("_"):
            from .luat import doc_json_md
            kq[ten] = persona_mod.kiem_persona(doc_json_md(os.path.join(thu_muc, ten)), pc, hv)
    nv_loi = persona_mod.kiem_persona(nv.get("persona", {}), pc, hv)
    kq["nhan-vat.md (persona chính)"] = nv_loi
    in_({"ok": not any(kq.values()), "loi": kq})
    sys.exit(1 if any(kq.values()) else 0)


# ---------- tạo: kế hoạch, bài, chấm, duyệt, đăng ----------

def c_ke_hoach(a):
    home, con, nv, hv = _ctx(a)
    nt = doc(home, "nen_tang")
    thu_hai = date.fromisoformat(a.tuan)
    da = Counter()
    tao = 0
    tt = hoc_ngay.ty_trong_hoc(con, nv)  # tỷ trọng gốc nhân hệ số học được (tầng 1)
    for i in range(7):
        ngay = thu_hai + timedelta(days=i)
        for ten, cfg in nt.items():
            for gio, uu in cfg.get("khung", []):
                if i not in cfg.get("thu_dang", list(range(7))):
                    continue
                # Bốc trụ cột ngẫu nhiên theo tỷ trọng (không xoay vòng cố định), để trụ cột không dính chặt vào
                # một nền tảng hay một giờ: nếu dính, vòng học sẽ tưởng trụ cột tốt trong khi thật ra là giờ tốt
                r = random.Random(f"khe|{ngay}|{gio}|{ten}")
                tc = r.choices(nv["tru_cot"], weights=[tt[t["ma"]] for t in nv["tru_cot"]])[0]
                da[tc["ma"]] += 1
                cur = con.execute("INSERT OR IGNORE INTO khe(ngay, gio, nen_tang, uu_tien, tru_cot, dinh_dang) VALUES (?,?,?,?,?,?)",
                                  (ngay.isoformat(), gio, ten, uu, tc["ma"], tc["dinh_dang"][0]))
                tao += cur.rowcount
    con.commit()
    in_({"khe_moi": tao, "phan_bo_tru_cot": dict(da), "ty_trong_dung": tt})


def c_bai_them(a):
    home, con, nv, hv = _ctx(a)
    khe = con.execute("SELECT * FROM khe WHERE id=?", (a.khe,)).fetchone()
    nd = open(a.file, encoding="utf-8").read().strip() if a.file else a.noi_dung
    pb = con.execute("SELECT MAX(phien_ban) FROM luat_viet WHERE con_hieu_luc=1").fetchone()[0] or 0
    cur = con.execute("""INSERT INTO bai(khe_id, nen_tang, tru_cot, dinh_dang, hook, noi_dung, media, trang_thai,
                         luat_viet_pb, hen_luc, tao_luc, muc_dich, cho_ai, tieu_hoa_ids, cam_xuc, phan_ung) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                      (a.khe, khe["nen_tang"], khe["tru_cot"], khe["dinh_dang"], a.hook, nd, a.media or "[]", "nhap",
                       pb, f"{khe['ngay']}T{khe['gio']}:00", _now(), a.muc_dich, a.cho_ai, a.tu_tieu_hoa, a.cam_xuc, a.phan_ung))
    con.execute("UPDATE khe SET bai_id=? WHERE id=?", (cur.lastrowid, a.khe))
    con.commit()
    in_({"bai_id": cur.lastrowid, "hen_luc": f"{khe['ngay']}T{khe['gio']}"})


def c_bai_cham(a):
    home, con, nv, hv = _ctx(a)
    b = con.execute("SELECT * FROM bai WHERE id=?", (a.id,)).fetchone()
    nt = doc(home, "nen_tang").get(b["nen_tang"], {})
    tu_dong = []
    if nv["nhan_ai"].lower() not in b["noi_dung"].lower() and not nt.get("adapter_bat_nhan_ai"):
        tu_dong.append("thiếu nhãn AI")
    tu_dong += [f"từ cấm: {w}" for w in nv["tu_cam"] if w.lower() in b["noi_dung"].lower()]
    if nt.get("do_dai_toi_da") and len(b["noi_dung"]) > nt["do_dai_toi_da"]:
        tu_dong.append("quá dài")
    tt = "cho_duyet" if (a.diem >= nv["nguong_critic"] and not tu_dong) else "sua"
    con.execute("UPDATE bai SET diem_critic=?, ghi_chu_critic=?, trang_thai=? WHERE id=?",
                (a.diem, json.dumps({"agent": a.ghi_chu, "tu_dong": tu_dong}, ensure_ascii=False), tt, a.id))
    con.commit()
    in_({"bai_id": a.id, "trang_thai": tt, "loi_tu_dong": tu_dong})


def c_bai_duyet(a):
    home, con, nv, hv = _ctx(a)
    b = con.execute("SELECT * FROM bai WHERE id=?", (a.id,)).fetchone()
    if a.sua_file:
        moi = open(a.sua_file, encoding="utf-8").read().strip()
        con.execute("INSERT INTO duyet(bai_id, quyet_dinh, gop_y, ban_cu, ban_moi, luc) VALUES (?,?,?,?,?,?)",
                    (a.id, "sua", a.gop_y, b["noi_dung"], moi, _now()))
        con.execute("UPDATE bai SET noi_dung=?, trang_thai='duyet' WHERE id=?", (moi, a.id))
    elif a.gop_y:
        con.execute("INSERT INTO duyet(bai_id, quyet_dinh, gop_y, luc) VALUES (?,?,?,?)", (a.id, "gop_y", a.gop_y, _now()))
        con.execute("UPDATE bai SET trang_thai='sua' WHERE id=?", (a.id,))
    elif a.bo:
        con.execute("INSERT INTO duyet(bai_id, quyet_dinh, luc) VALUES (?,?,?)", (a.id, "bo", _now()))
        con.execute("UPDATE bai SET trang_thai='bo' WHERE id=?", (a.id,))
    else:
        con.execute("INSERT INTO duyet(bai_id, quyet_dinh, luc) VALUES (?,?,?)", (a.id, "nhan", _now()))
        con.execute("UPDATE bai SET trang_thai='duyet' WHERE id=?", (a.id,))
    con.commit()
    in_({"bai_id": a.id, "trang_thai": con.execute("SELECT trang_thai FROM bai WHERE id=?", (a.id,)).fetchone()[0]})


def c_bai_ds(a):
    home, con, nv, hv = _ctx(a)
    q = "SELECT id, nen_tang, tru_cot, hook, trang_thai, diem_critic, hen_luc, dang_luc, substr(noi_dung,1,80) AS dau FROM bai"
    rows = con.execute(q + (" WHERE trang_thai=?" if a.trang_thai else "") + " ORDER BY id",
                       (a.trang_thai,) if a.trang_thai else ()).fetchall()
    in_([dict(r) for r in rows])


def c_dang(a):
    home, con, nv, hv = _ctx(a)
    nt = doc(home, "nen_tang")
    if a.id:
        ds = con.execute("SELECT * FROM bai WHERE id=?", (a.id,)).fetchall()
    else:
        ds = con.execute("SELECT * FROM bai WHERE trang_thai='duyet' AND hen_luc<=? ORDER BY hen_luc", (_now(),)).fetchall()
    kq = [ban_dang.dang_mot(home, con, nv, hv, nt, b, a.thu) for b in ds]
    in_(kq)


# ---------- hộp thư và fan ----------

def _fan(con, nen_tang, ma, ten, luc):
    con.execute("INSERT OR IGNORE INTO fan(nen_tang, ma_ngoai, ten, lan_dau, lan_cuoi) VALUES (?,?,?,?,?)", (nen_tang, ma, ten, luc, luc))
    con.execute("UPDATE fan SET lan_cuoi=? WHERE nen_tang=? AND ma_ngoai=?", (luc, nen_tang, ma))
    return con.execute("SELECT * FROM fan WHERE nen_tang=? AND ma_ngoai=?", (nen_tang, ma)).fetchone()


def c_hop_thu_keo(a):
    home, con, nv, hv = _ctx(a)
    nt = doc(home, "nen_tang")
    luat_d = doc(home, "diem")
    moi = 0
    for b in con.execute("SELECT * FROM bai WHERE trang_thai='da_dang'").fetchall():
        cfg = nt[b["nen_tang"]]
        for t in _adapter(a, cfg, "hop_thu").keo_binh_luan(home, b, cfg):
            if t["luc"] > _now():
                continue  # chưa tới giờ trong giả lập
            f = _fan(con, b["nen_tang"], t["fan_ma"], t["fan_ten"], t["luc"])
            cur = con.execute("INSERT OR IGNORE INTO tin(nen_tang, loai, ma_ngoai, bai_id, fan_id, noi_dung, luc) VALUES (?,?,?,?,?,?,?)",
                              (b["nen_tang"], t["loai"], t["ma_ngoai"], b["id"], f["id"], t["noi_dung"], t["luc"]))
            if cur.rowcount:
                moi += 1
                con.execute("INSERT INTO su_kien_fan(fan_id, loai, diem, luc, tham_chieu) VALUES (?,?,?,?,?)",
                            (f["id"], t["loai"], luat_d["su_kien"][t["loai"]], t["luc"], t["ma_ngoai"]))
                # Người trong vòng bình luận bài mình = tín hiệu hai chiều
                v = con.execute("SELECT id FROM vong WHERE nen_tang=? AND ma_ngoai=?", (b["nen_tang"], t["fan_ma"])).fetchone()
                if v:
                    con.execute("INSERT INTO su_kien_vong(vong_id, loai, diem, luc, ghi_chu) VALUES (?,?,?,?,?)",
                                (v["id"], "binh_luan_bai_minh", hv["diem_tin"]["su_kien"]["binh_luan_bai_minh"], t["luc"], t["ma_ngoai"]))
                    con.execute("UPDATE vong SET cham_khong_dap=0 WHERE id=?", (v["id"],))
                    hanh_vi.len_thang(con, v["id"], "hai_chieu")
                    hanh_vi.cap_nhat_tin(con, hv, v["id"])
    con.commit()
    in_({"tin_moi": moi})


def c_hop_thu_phan_loai(a):
    home, con, nv, hv = _ctx(a)
    luat_h = doc(home, "hang")
    dem = Counter()
    for t in con.execute("SELECT * FROM tin WHERE trang_thai='moi'").fetchall():
        hang, nhan, ly_do, hanh_dong = hop_thu.phan_loai(luat_h, t["noi_dung"])
        tt = {"an": "an", "chuyen_linh": "chuyen_linh"}.get(hanh_dong, "cho_soan")
        con.execute("UPDATE tin SET hang=?, nhan=?, ly_do=?, trang_thai=? WHERE id=?", (hang, nhan, ly_do, tt, t["id"]))
        if nhan == "brand":
            con.execute("INSERT INTO brand_lead(fan_id, tin_id, ten, ghi_chu, luc) VALUES (?,?,?,?,?)",
                        (t["fan_id"], t["id"], t["noi_dung"][:60], "tự tạo từ hộp thư", _now()))
        dem[f"{hang}/{nhan}"] += 1
    con.commit()
    in_(dict(dem))


def c_hop_thu_gan(a):
    home, con, nv, hv = _ctx(a)
    con.execute("UPDATE tin SET hang=?, nhan=?, ly_do=? WHERE id=?", (a.hang, a.nhan, "agent: " + a.ly_do, a.id))
    con.commit()
    in_({"id": a.id, "hang": a.hang, "nhan": a.nhan})


def c_hop_thu_ds(a):
    home, con, nv, hv = _ctx(a)
    q = """SELECT t.id, t.loai, t.hang, t.nhan, t.trang_thai, t.noi_dung, t.tra_loi, f.ten AS fan, f.bac, b.id AS bai_id
           FROM tin t LEFT JOIN fan f ON f.id=t.fan_id LEFT JOIN bai b ON b.id=t.bai_id"""
    rows = con.execute(q + (" WHERE t.trang_thai=?" if a.trang_thai else "") + " ORDER BY t.id",
                       (a.trang_thai,) if a.trang_thai else ()).fetchall()
    in_([dict(r) for r in rows])


def c_hop_thu_soan(a):
    home, con, nv, hv = _ctx(a)
    con.execute("UPDATE tin SET tra_loi=?, trang_thai='da_soan' WHERE id=? AND trang_thai IN ('cho_soan','da_soan','chuyen_linh')", (a.tra_loi, a.id))
    con.commit()
    in_(dict(con.execute("SELECT id, hang, trang_thai, tra_loi FROM tin WHERE id=?", (a.id,)).fetchone()))


def c_hop_thu_duyet(a):
    home, con, nv, hv = _ctx(a)
    if a.sua:
        con.execute("UPDATE tin SET tra_loi=? WHERE id=?", (a.sua, a.id))
    con.execute("UPDATE tin SET trang_thai='duyet', duyet_boi='linh' WHERE id=? AND trang_thai='da_soan'", (a.id,))
    con.commit()
    in_(dict(con.execute("SELECT id, trang_thai, tra_loi FROM tin WHERE id=?", (a.id,)).fetchone()))


def c_hop_thu_gui(a):
    home, con, nv, hv = _ctx(a)
    nt = doc(home, "nen_tang")
    ds = con.execute("SELECT * FROM tin WHERE id=?", (a.id,)).fetchall() if a.id else \
        con.execute("SELECT * FROM tin WHERE trang_thai IN ('da_soan','duyet') ORDER BY id").fetchall()
    kq = []
    for t in ds:
        f = con.execute("SELECT * FROM fan WHERE id=?", (t["fan_id"],)).fetchone()
        loi = cong.cong_tra_loi(con, nv, t, f, a.linh)
        if loi:
            kq.append({"tin_id": t["id"], "gui": False, "ly_do": loi})
            continue
        cfg = nt[t["nen_tang"]]
        _adapter(a, cfg, "hop_thu").gui_tra_loi(home, t, t["tra_loi"], cfg)
        con.execute("UPDATE tin SET trang_thai='da_tra', tra_luc=? WHERE id=?", (_now(), t["id"]))
        ghi_hanh_dong(con, "tra_loi", t["id"])
        con.commit()
        kq.append({"tin_id": t["id"], "gui": True})
    in_(kq)


def c_fan_cap_nhat(a):
    home, con, nv, hv = _ctx(a)
    doi = fan_mod.cap_nhat_tat_ca(con, doc(home, "diem"))
    con.commit()
    in_({"doi_bac": doi})


def c_fan_ds(a):
    home, con, nv, hv = _ctx(a)
    in_([dict(r) for r in con.execute("SELECT id, ten, nen_tang, diem, bac, lan_dau, lan_cuoi, khong_nhan FROM fan ORDER BY diem DESC LIMIT ?", (a.top,))])


# ---------- học ----------

def c_so_lieu(a):
    home, con, nv, hv = _ctx(a)
    nt = doc(home, "nen_tang")
    n = 0
    for b in con.execute("SELECT * FROM bai WHERE trang_thai='da_dang'").fetchall():
        cfg = nt[b["nen_tang"]]
        s = _adapter(a, cfg, "hop_thu").keo_so_lieu(home, b, cfg)
        if s:
            con.execute("INSERT INTO so_lieu(bai_id, luc, view, reach, like_, comment, share, save) VALUES (?,?,?,?,?,?,?,?)",
                        (b["id"], _now(), s["view"], s["reach"], s["like_"], s["comment"], s["share"], s["save"]))
            n += 1
    con.commit()
    in_({"bai_co_so_lieu": n})


def c_retro(a):
    home, con, nv, hv = _ctx(a)
    rows = [dict(r) for r in con.execute("""SELECT b.id, b.tru_cot, b.hook, b.cam_xuc, b.phan_ung, substr(b.dang_luc,12,2) AS gio, s.*
        FROM bai b JOIN so_lieu s ON s.id=(SELECT MAX(id) FROM so_lieu WHERE bai_id=b.id)""")]
    gd, tuoi, ke, tieu_chi, cs = hanh_vi.giai_doan_hien_tai(con, nv, hv)
    hap, tao, can = hanh_vi.ty_le_hap_thu(con, hv, them_tao=0)
    out = [f"# Retro tới {bay_gio().date()}", "",
           f"Giai đoạn {gd['ma']} ({gd['ten']}), ngày tuổi {tuoi}. Hấp thu/tạo 7 ngày: {hap}/{tao} (cần ≥ {can}:1).", ""]
    if not rows:
        out.append("Chưa có số liệu bài.")
    else:
        nen = sum(hoc.ty_le(r) for r in rows) / len(rows)
        out += [f"{len(rows)} bài, tỷ lệ tương tác trung bình {nen:.1%}.", ""]
        for ten, khoa in (("hook", lambda r: r["hook"]), ("giờ đăng", lambda r: r["gio"] + "h"), ("trụ cột", lambda r: r["tru_cot"]), ("cảm xúc nhắm tới", lambda r: r["cam_xuc"])):
            g = hoc.nhom(rows, khoa)
            out += [f"## Theo {ten}", "", "| Nhóm | Bài | View | Tỷ lệ |", "|---|---|---|---|"]
            out += [f"| {x['nhom']} | {x['so_bai']} | {x['view']} | {x['ty_le']:.1%} |" for x in g]
            if len(g) >= 2:
                d, du, ly = hoc.so_sanh(g[0], g[-1], nen)
                out.append(f"\nCao nhất so với thấp nhất: chênh {d:+.1%}; {ly}.")
            out.append("")
    vong = con.execute("SELECT bac_thang, COUNT(*) n FROM vong GROUP BY bac_thang").fetchall()
    out += ["## Vòng quan hệ", "", ", ".join(f"{hanh_vi.THANG[r['bac_thang']]}: {r['n']}" for r in vong) or "chưa có", ""]
    chan = con.execute("SELECT ly_do_chan FROM hanh_dong_ra WHERE trang_thai='bi_chan'").fetchall()
    if chan:
        dem = Counter(l.split(":")[0][:60] for r in chan for l in json.loads(r["ly_do_chan"]))
        out += ["## Hành động bị cổng chặn", ""] + [f"- {k}: {v}" for k, v in dem.most_common(6)] + [""]
    chua_hoc = con.execute("SELECT id, bai_id, gop_y FROM duyet WHERE quyet_dinh IN ('sua','gop_y') AND da_hoc=0").fetchall()
    out += ["## Lần Linh sửa bài chưa rút thành luật viết", ""] + [f"- duyệt #{r['id']} (bài {r['bai_id']}): {r['gop_y'] or 'sửa trực tiếp, xem bảng duyet'}" for r in chua_hoc] + [""]
    out += ["## Phần agent viết", "", "1. Ba giả thuyết, mỗi cái kèm kiểm cỡ mẫu (`can-mau`).", "2. Luật viết mới từ các lần sửa ở trên (`luat-viet them`).",
            "3. Người trong vòng nên đầu tư tuần tới và vì sao.", "4. Điều chỉnh tỷ trọng trụ cột hoặc giờ đăng nếu tín hiệu đủ mạnh.", ""]
    duong = os.path.join(home, "bao-cao", f"RETRO-{bay_gio().date()}.md")
    open(duong, "w", encoding="utf-8").write("\n".join(out))
    in_({"file": duong})


def c_can_mau(a):
    in_({"p": a.p, "d": a.d, "can_moi_nhanh": hoc.can_mau(a.p, a.d)})


def c_luat_viet(a):
    home, con, nv, hv = _ctx(a)
    pb = (con.execute("SELECT MAX(phien_ban) FROM luat_viet").fetchone()[0] or 0) + 1
    con.execute("INSERT INTO luat_viet(phien_ban, luat, tu_duyet, luc) VALUES (?,?,?,?)", (pb, a.luat, a.tu_duyet, _now()))
    if a.tu_duyet:
        con.execute("UPDATE duyet SET da_hoc=1 WHERE id=?", (a.tu_duyet,))
    with open(os.path.join(home, "ho-so", "luat-viet.md"), "a", encoding="utf-8") as f:
        f.write(f"\n- v{pb} ({bay_gio().date()}{', từ duyệt #' + str(a.tu_duyet) if a.tu_duyet else ''}): {a.luat}\n")
    con.commit()
    in_({"phien_ban": pb})


def c_bang_tin(a):
    home, con, nv, hv = _ctx(a)
    gd, tuoi, ke, tieu_chi, cs = hanh_vi.giai_doan_hien_tai(con, nv, hv)
    hap, tao, can = hanh_vi.ty_le_hap_thu(con, hv, them_tao=0)
    tong = {
        "nhan_vat": nv["ten"], "giai_doan": gd["ma"], "ten_giai_doan": gd["ten"], "tuoi_ngay": tuoi,
        "tieu_chi_len": tieu_chi, "hap_thu_7_ngay": hap, "tao_7_ngay": tao,
        "luot_doc": cs["so_bai_da_doc"], "tieu_hoa": con.execute("SELECT COUNT(*) FROM tieu_hoa").fetchone()[0],
        "cham": dict(con.execute("SELECT trang_thai, COUNT(*) FROM hanh_dong_ra GROUP BY trang_thai").fetchall()),
        "vong": [dict(r) | {"thang": hanh_vi.THANG[r["bac_thang"]]} for r in con.execute("SELECT ten, nhom, bac_thang, diem_tin, so_bai_da_doc FROM vong ORDER BY bac_thang DESC, diem_tin DESC")],
        "bai": dict(con.execute("SELECT trang_thai, COUNT(*) FROM bai GROUP BY trang_thai").fetchall()),
        "tin": dict(con.execute("SELECT trang_thai, COUNT(*) FROM tin GROUP BY trang_thai").fetchall()),
        "fan": dict(con.execute("SELECT bac, COUNT(*) FROM fan GROUP BY bac").fetchall()),
        "brand_lead": con.execute("SELECT COUNT(*) FROM brand_lead").fetchone()[0],
        "luat_viet": con.execute("SELECT COUNT(*) FROM luat_viet").fetchone()[0],
    }
    open(os.path.join(home, "bao-cao", "bang-tin.json"), "w", encoding="utf-8").write(json.dumps(tong, ensure_ascii=False, indent=1))
    in_(tong)


# ---------- tự học mỗi ngày và bàn đăng ----------

def c_hoc_ngay(a):
    home, con, nv, hv = _ctx(a)
    bao = hoc_ngay.chay(con, home, nv, hv)
    in_({"file": os.path.join(home, "bao-cao", f"HOC-{bao['ngay']}.md"), "bai_hoc_moi": bao["bai_hoc_moi"],
         "thay_doi": bao["thay_doi"], "xet_lai": bao["xet_lai"], "brier": bao["brier_theo_tuan"][-3:]})


def c_goi_y(a):
    home, con, nv, hv = _ctx(a)
    chon, diem = hoc_ngay.goi_y(con, a.chieu, [x.strip() for x in a.lua_chon.split(",")], a.seed)
    in_({"chon": chon, "mau": diem})


def c_bai_hoc_them(a):
    home, con, nv, hv = _ctx(a)
    id_, moi = hoc_ngay._ghi_bai_hoc(con, a.nguon, a.khoa or f"agent>{a.noi_dung[:60]}", a.noi_dung,
                                     json.dumps({"tu_duyet": a.tu_duyet}, ensure_ascii=False), a.tang, _now())
    if a.tu_duyet:
        for d in a.tu_duyet.split(","):
            con.execute("UPDATE duyet SET da_hoc=1 WHERE id=?", (int(d),))
    con.commit()
    in_({"id": id_, "moi": moi, "cho_linh_bam": a.tang >= 2})


def c_bai_hoc_ds(a):
    home, con, nv, hv = _ctx(a)
    in_([dict(r) for r in con.execute("SELECT id, tang, trang_thai, nguon, noi_dung, luc FROM bai_hoc ORDER BY id DESC")])


def c_ban_dang(a):
    goc = a.goc or _home(a)
    kenh = [ban_dang.Kenh(h, a.thu) for h in ban_dang.tim_kenh(goc)]
    if not kenh:
        sys.exit(f"không thấy kênh nào ở {goc}")
    if a.phuc_vu:
        ban_dang.phuc_vu(kenh, a.cong, os.path.join(GOC_PLUGIN, "giao-dien", "ban-dang.html"))
    elif a.bam:
        k = next((k for k in kenh if k.muc()[0]["persona"] == a.persona), kenh[0])
        in_(k.bam(a.loai, a.bam, a.hanh_dong, a.noi_dung, a.ly_do))
    else:
        in_(ban_dang.tat_ca(kenh))


def c_nhat_ky(a):
    home, con, nv, hv = _ctx(a)
    in_([dict(r) for r in con.execute("SELECT * FROM nhat_ky ORDER BY id DESC LIMIT ?", (a.n,))])


def main(argv=None):
    p = argparse.ArgumentParser(prog="kenhao", description="Vòng nuôi kênh người ảo (LAB040)")
    p.add_argument("--home")
    p.add_argument("--thu", action="store_true", help="dùng adapter thử, không chạm mạng")
    s = p.add_subparsers(dest="lenh", required=True)

    def add(ten, f, *args):
        sp = s.add_parser(ten)
        for a_ in args:
            sp.add_argument(*a_[0], **a_[1])
        sp.set_defaults(func=f)
        return sp

    A = lambda *n, **k: (n, k)  # noqa: E731
    add("init", c_init)
    add("kiem-ho-so", c_kiem)
    add("giai-doan", c_giai_doan)
    add("vong-them", c_vong_them, A("--nen-tang", required=True), A("--ma", required=True), A("--ten", required=True),
        A("--nhom", default="dong_nganh"), A("--ly-do", required=True), A("--la-minh", action="store_true"), A("--la-nha", action="store_true"))
    add("vong-ds", c_vong_ds)
    add("doc-nhap", c_doc_nhap, A("file"))
    add("doc-ds", c_doc_ds, A("--n", type=int, default=30), A("--chua-tieu-hoa", action="store_true"))
    add("tieu-hoa", c_tieu_hoa, A("--tu", required=True, help="id lượt đọc, cách nhau dấu phẩy"),
        A("--loai", required=True), A("--ghi-chu", required=True))
    add("trend", c_trend, A("--ngay", type=int, default=7), A("--top", type=int, default=10))
    add("phien", c_phien, A("--ngay"))
    add("cham-de-xuat", c_cham_de_xuat, A("--nguoi", type=int, required=True), A("--doc", type=int),
        A("--loai", required=True, choices=["thich", "luu", "theo_doi", "binh_luan", "nhan"]),
        A("--muc-dich"), A("--vi-sao"), A("--noi-dung"), A("--chi-tiet"))
    add("cham-duyet", c_cham_duyet, A("--id", type=int, required=True), A("--sua"), A("--bo", action="store_true"))
    add("cham-viec", c_cham_viec)
    add("cham-xong", c_cham_xong, A("--id", type=int, required=True))
    add("dap", c_dap, A("--nguoi", type=int, required=True), A("--loai", required=True), A("--ghi-chu", default=""))
    add("persona-gan", c_persona_gan, A("--doc", type=int, required=True), A("--kieu", required=True),
        A("--cam-xuc", required=True), A("--phan-ung", required=True), A("--flaw", default=""), A("--giong", default=""), A("--ghi-chu", default=""))
    add("persona-xep-hang", c_persona_xep_hang)
    add("persona-kiem", c_persona_kiem)
    add("ke-hoach", c_ke_hoach, A("--tuan", required=True, help="ngày thứ Hai, YYYY-MM-DD"))
    add("bai-them", c_bai_them, A("--khe", type=int, required=True), A("--file"), A("--noi-dung"),
        A("--hook", required=True), A("--media"), A("--muc-dich", required=True), A("--cho-ai", required=True),
        A("--tu-tieu-hoa", required=True), A("--cam-xuc", required=True), A("--phan-ung", required=True))
    add("bai-cham", c_bai_cham, A("--id", type=int, required=True), A("--diem", type=float, required=True), A("--ghi-chu", default=""))
    add("bai-duyet", c_bai_duyet, A("--id", type=int, required=True), A("--sua-file"), A("--gop-y"), A("--bo", action="store_true"))
    add("bai-ds", c_bai_ds, A("--trang-thai"))
    add("dang", c_dang, A("--id", type=int))
    add("hop-thu-keo", c_hop_thu_keo)
    add("hop-thu-phan-loai", c_hop_thu_phan_loai)
    add("hop-thu-gan", c_hop_thu_gan, A("--id", type=int, required=True), A("--hang", required=True, choices=["xanh", "vang", "do"]),
        A("--nhan", required=True), A("--ly-do", required=True))
    add("hop-thu-ds", c_hop_thu_ds, A("--trang-thai"))
    add("hop-thu-soan", c_hop_thu_soan, A("--id", type=int, required=True), A("--tra-loi", required=True))
    add("hop-thu-duyet", c_hop_thu_duyet, A("--id", type=int, required=True), A("--sua"))
    add("hop-thu-gui", c_hop_thu_gui, A("--id", type=int), A("--linh", action="store_true"))
    add("fan-cap-nhat", c_fan_cap_nhat)
    add("fan-ds", c_fan_ds, A("--top", type=int, default=20))
    add("so-lieu", c_so_lieu)
    add("retro", c_retro)
    add("can-mau", c_can_mau, A("--p", type=float, required=True), A("--d", type=float, required=True))
    add("luat-viet", c_luat_viet, A("--luat", required=True), A("--tu-duyet", type=int))
    add("bang-tin", c_bang_tin)
    add("hoc-ngay", c_hoc_ngay)
    add("goi-y", c_goi_y, A("--chieu", required=True, choices=["hook", "cam_xuc", "tru_cot", "gio"]),
        A("--lua-chon", required=True, help="các lựa chọn, cách nhau dấu phẩy"), A("--seed"))
    add("bai-hoc-them", c_bai_hoc_them, A("--noi-dung", required=True), A("--tang", type=int, default=2, choices=[1, 2, 3]),
        A("--nguon", default="agent"), A("--khoa"), A("--tu-duyet", help="id duyệt đã rút thành bài học, cách nhau dấu phẩy"))
    add("bai-hoc-ds", c_bai_hoc_ds)
    add("ban-dang", c_ban_dang, A("--goc", help="thư mục kênh, hoặc thư mục chứa nhiều kênh"), A("--phuc-vu", action="store_true"),
        A("--cong", type=int, default=8765), A("--bam", type=int, help="id mục để bấm (không cần giao diện)"),
        A("--loai", default="bai", choices=["bai", "cham", "tra_loi", "bai_hoc"]), A("--hanh-dong", default="dang"),
        A("--persona"), A("--noi-dung"), A("--ly-do"))
    add("nhat-ky", c_nhat_ky, A("--n", type=int, default=20))
    a = p.parse_args(argv)
    a.func(a)


if __name__ == "__main__":
    main()
