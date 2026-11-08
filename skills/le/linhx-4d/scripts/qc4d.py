#!/usr/bin/env python3
"""qc4d.py - quy chuẩn giao việc 4D (Double Diamond x 100 Tasks x phòng Tam Quốc).

  qc4d.py phong                         in bảng tướng
  qc4d.py moi <loai> <thu_muc> <ten>    tạo chiến dịch 4 pha + phiếu mẫu
  qc4d.py kiem <thu_muc>                kiểm phiếu đúng luật (trước khi giao)
  qc4d.py cong <thu_muc> <PHA> [--chi-may]  cổng ra: máy đo + vòng chấm đã đạt
  Vòng tự chấm, tự sửa (LAB099) cho mọi pha:
  qc4d.py de-cham <thu_muc> <PHA>       đề cho người chấm (ngữ cảnh khác thợ)
  qc4d.py cham <thu_muc> <PHA> <phieu.json>...   gom ≥3 phiếu, ra phieu-sua.md
  qc4d.py hoan-tac <thu_muc> <PHA>      trả pha về bản trước khi vòng tệ đi
Mã thoát 0 = DAT, 1 = CHUA_DAT. Script chỉ đo, không sửa.
"""
import json, re, shutil, statistics, sys
from pathlib import Path

GOC = Path(__file__).resolve().parent
PHA = ["DISCOVER", "DEFINE", "DEVELOP", "DELIVER"]
TRUONG = ["ma", "pha", "tuong", "viec", "cong_cu", "dau_ra", "tieu_chi", "lenh_kiem", "tran_phut", "phu_thuoc"]


def doc(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


PHONG, LOAI = doc(GOC / "phong.json"), doc(GOC / "loai.json")


def phong():
    for ten, t in PHONG["tuong"].items():
        print(f"{ten:18} {t['ai']:28} {','.join(t['viec']):22} {t['ghi']}")
    return 0


def moi(loai, thu_muc, ten):
    if loai not in LOAI or loai.startswith("_"):
        print("loai phải là:", ", ".join(k for k in LOAI if not k.startswith("_")))
        return 1
    L, d = LOAI[loai], Path(thu_muc)
    phieu, n = [], 0
    for p in PHA:
        for x in LOAI["_chung"][p]["phieu"] + [y for y in L.get("phieu_them", []) if y["pha"] == p]:
            n += 1
            ph = {k: v for k, v in x.items() if k != "pha"}
            ph.update(ma=f"{p[:3]}-{n:02d}", pha=p, tran_phut=40,
                      phu_thuoc=[phieu[-1]["ma"]] if phieu and phieu[-1]["pha"] != p else [])
            phieu.append(ph)
    cd = {"ten": ten, "loai": loai, "loai_ten": L["ten"],
          "pha": {p: {"dau_ra": LOAI["_chung"][p]["dau_ra"] + L[p]["them_dau_ra"],
                      "ghi": L[p]["ghi"], "cong": LOAI["_chung"][p]["cong"]} for p in PHA},
          "phieu": phieu}
    for p in PHA:
        (d / p).mkdir(parents=True, exist_ok=True)
    (d / "chien-dich.json").write_text(json.dumps(cd, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Tạo {d}/chien-dich.json: {L['ten']}, {len(phieu)} phiếu")
    return 0


def kiem(thu_muc):
    cd = doc(Path(thu_muc) / "chien-dich.json")
    loi, ma = [], set()
    for ph in cd["phieu"]:
        m = ph.get("ma", "?")
        thieu = [k for k in TRUONG if k not in ph or ph[k] in ("", None)]
        if thieu:
            loi.append(f"{m}: thiếu {thieu}")
        if ph.get("pha") not in PHA:
            loi.append(f"{m}: pha sai")
        t = PHONG["tuong"].get(ph.get("tuong"))
        if not t:
            loi.append(f"{m}: tướng '{ph.get('tuong')}' không có trong phòng")
        elif ph.get("viec") not in t["viec"]:
            loi.append(f"{m}: {ph['tuong']} không làm việc '{ph.get('viec')}' (làm: {t['viec']})")
        if t and t["ai"].startswith("Claude") and ph.get("viec") in PHONG["claude_khong_lam"]:
            loi.append(f"{m}: Claude không làm thợ ({ph['viec']}), giao agy/Gemini")
        if int(ph.get("tran_phut") or 999) > PHONG["tran_phut"]:
            loi.append(f"{m}: quá {PHONG['tran_phut']} phút, chia nhỏ")
        if ph.get("viec") in ("anh", "thiet-ke") and (ph.get("ung_vien", 0) < 3 or ph.get("vong_sua", 9) > 3):
            loi.append(f"{m}: ảnh/thiết kế cần ≥3 ứng viên và ≤3 vòng sửa")
        # Công cụ nghiên cứu/quét tuỳ tình huống (Linh 1/11): chỉ cần ghi lý do khi khác mặc định
        if ph.get("viec") == "nghien-cuu" and "Gemini" not in ph.get("cong_cu", "") and not ph.get("ly_do_cong_cu"):
            loi.append(f"{m}: nghiên cứu không qua Gemini Deep Research thì ghi ly_do_cong_cu")
        if ph.get("viec") == "quet" and "crawler" not in ph.get("cong_cu", "").lower() and not ph.get("ly_do_cong_cu"):
            loi.append(f"{m}: quét không qua LINHX crawler thì ghi ly_do_cong_cu")
        if not re.search(r"\d|≥|DAT|đạt", str(ph.get("tieu_chi", ""))):
            loi.append(f"{m}: tiêu chí phải đo được (có số hoặc ngưỡng)")
        for p in ph.get("phu_thuoc", []):
            if p not in ma:
                loi.append(f"{m}: phụ thuộc '{p}' chưa có phía trước")
        ma.add(m)
    for p in PHA:
        if not any(ph.get("viec") == "tham-chieu" for ph in cd["phieu"] if ph.get("pha") in ("DISCOVER", "DEVELOP")):
            loi.append("chiến dịch thiếu phiếu tìm tham chiếu")
            break
    if not any(ph.get("viec") == "kiem-e2e" for ph in cd["phieu"]):
        loi.append("chiến dịch thiếu phiếu test đầu cuối")
    return bao(f"kiem {thu_muc}", loi)


def dem(d, f, mau):
    p = d / f
    return len(re.findall(mau, p.read_text(encoding="utf-8"))) if p.is_file() else 0


def cong(thu_muc, pha, co=""):
    d0 = Path(thu_muc)
    cd, d = doc(d0 / "chien-dich.json"), d0 / pha
    loi = [f"thiếu {f}" for f in cd["pha"][pha]["dau_ra"]
           if not ((d / f).is_dir() and any((d / f).iterdir()) if f.endswith("/") else (d / f).is_file() and (d / f).stat().st_size)]
    if pha == "DISCOVER":
        if dem(d, "THAM-CHIEU.md", r"(?m)^\s*[-|*\d].*https?://") < 5:
            loi.append("THAM-CHIEU.md: cần ≥5 mẫu có link")
        if len(set(re.findall(r"\[BC-\d+\]", (d / "KHAM-PHA.md").read_text(encoding="utf-8")))) < 10 if (d / "KHAM-PHA.md").is_file() else True:
            loi.append("KHAM-PHA.md: cần ≥10 bằng chứng [BC-xxx] khác nhau")
        if dem(d, "KHAM-PHA.md", r"[“\"][^”\"]{15,}[”\"]") < 5:
            loi.append("KHAM-PHA.md: cần ≥5 trích lời người dùng")
        loi += trich_that(d)
    if pha == "DEFINE":
        if dem(d, "TINH-HUONG.md", r"TH-\d+") < 3:
            loi.append("TINH-HUONG.md: cần ≥3 TH-xxx")
        t = (d / "DINH-NGHIA.md").read_text(encoding="utf-8") if (d / "DINH-NGHIA.md").is_file() else ""
        for muc in ["Phân khúc", "Persona", "Vấn đề", "CVP", "Mục tiêu"]:
            if muc.lower() not in t.lower():
                loi.append(f"DINH-NGHIA.md: thiếu mục {muc}")
        if not re.search(r"Mục tiêu[^\n]*\n?[^\n]*\d", t, re.I):
            loi.append("DINH-NGHIA.md: mục tiêu phải có số")
    if pha == "DEVELOP":
        if len(set(re.findall(r"PA-\d+", (d / "UNG-VIEN.md").read_text(encoding="utf-8")))) < 3 if (d / "UNG-VIEN.md").is_file() else True:
            loi.append("UNG-VIEN.md: cần ≥3 phương án PA-x")
    if pha == "DELIVER":
        th = set(re.findall(r"TH-\d+", (d0 / "DEFINE" / "TINH-HUONG.md").read_text(encoding="utf-8"))) if (d0 / "DEFINE" / "TINH-HUONG.md").is_file() else set()
        bc = (d / "BANG-CHUNG.md").read_text(encoding="utf-8") if (d / "BANG-CHUNG.md").is_file() else ""
        for t in sorted(th):
            dong = [l for l in bc.splitlines() if t in l]
            if not any("DAT" in l and "CHUA_DAT" not in l and re.search(r"\.(png|jpg|webp)", l) for l in dong):
                loi.append(f"BANG-CHUNG.md: {t} chưa có dòng DAT kèm ảnh")
    if co != "--chi-may" and not loi:
        nk = nhat_ky(d0, pha)
        if not nk or nk[-1]["ket_qua"] != "DAT":
            loi.append(f"vòng chấm {pha} chưa đạt (chạy de-cham → cham)")
    return bao(f"cong {pha}", loi)


def chuan(t):
    return re.sub(r"\s+", " ", t.replace("“", '"').replace("”", '"')).strip().lower()


def trich_that(d):
    """Trích lời ≥30 ký tự phải có nguyên văn trong bang-chung/ (chống lời bịa, bài học NCT 1/11)."""
    kp = d / "KHAM-PHA.md"
    if not kp.is_file():
        return []
    kho = chuan(" ".join(p.read_text(encoding="utf-8", errors="ignore")
                         for p in (d / "bang-chung").rglob("*") if p.is_file() and p.suffix in (".md", ".txt", ".csv")))
    bia = [t for t in re.findall(r"[“\"]([^”\"]{30,})[”\"]", kp.read_text(encoding="utf-8")) if chuan(t) not in kho]
    return [f"KHAM-PHA.md: {len(bia)} trích lời không có nguyên văn trong bang-chung/, ví dụ: {bia[0][:60]}…"] if bia else []


# ───────── vòng tự chấm, tự sửa (luật LAB099) ─────────
SO_PHIEU, TRAN_VONG, TRAN_LOI = 3, 3, 3


def nhat_ky(d0, pha):
    p = d0 / pha / ".vong" / "nhat-ky.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else []


def tho_cua(cd, pha):
    return {ph["tuong"] for ph in cd["phieu"] if ph["pha"] == pha and ph["viec"] not in ("cham", "phan-bien", "kiem-e2e", "de")}


def de_cham(thu_muc, pha):
    d0 = Path(thu_muc)
    cd, tc = doc(d0 / "chien-dich.json"), LOAI["_cham"][pha]
    v = len(nhat_ky(d0, pha)) + 1
    tham = [str(p.relative_to(d0)) for p in d0.rglob("THAM-CHIEU*.md")]
    dong = "\n".join(f"| {k} | {c} |" for k, c in tc.items())
    de = f"""# Đề chấm pha {pha}, vòng {v}/{TRAN_VONG} · {cd['ten']} ({cd['loai_ten']})

Bạn là người chấm khó tính, KHÔNG phải người làm (thợ: {', '.join(sorted(tho_cua(cd, pha)))}).
Mở tham chiếu TRƯỚC: {', '.join(tham) or 'chưa có, ghi lỗi chan'}. Thước là tham chiếu high standard, không phải "dùng được".
Máy đã kiểm phần đếm được (qc4d cong --chi-may), đừng chấm lại.
Đọc: {pha}/ ({', '.join(cd['pha'][pha]['dau_ra'])}).

| Tiêu chí (1–5, đạt khi mọi tiêu chí ≥4) | Câu hỏi |
|---|---|
{dong}

Mức lỗi: chan (không dùng được), nang (người duyệt sẽ trả), nhe (để lại).
Mỗi lỗi chỉ CHỖ (file, mục) và CÁCH SỬA cụ thể; ưu tiên cắt bớt, tách, đổi cấu trúc hơn là thêm.
Đừng chấm quá tay: không bới lỗi để có việc, không đề xuất thêm phần mới.

Trả JSON vào {pha}/.vong/phieu-v{v}-<ten>.json:
{{"nguoi_cham": "<tên ngữ cảnh>", "diem": {{{', '.join(f'"{k}": 0' for k in tc)}}},
 "loi": [{{"muc": "nang", "cho": "...", "sua": "..."}}], "ket_luan": "dat|hong"}}
"""
    p = d0 / pha / ".vong" / f"de-cham-v{v}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(de, encoding="utf-8")
    print(f"Đề: {p} · cần {SO_PHIEU} phiếu từ {SO_PHIEU} ngữ cảnh khác thợ")
    return 0


def chup(d, dich):
    if dich.exists():
        shutil.rmtree(dich)
    shutil.copytree(d, dich, ignore=shutil.ignore_patterns(".vong"))


def cham(thu_muc, pha, *tep):
    d0 = Path(thu_muc)
    cd, d, tc = doc(d0 / "chien-dich.json"), d0 / pha, LOAI["_cham"][pha]
    nk, tho = nhat_ky(d0, pha), tho_cua(cd, pha)
    if len(nk) >= TRAN_VONG:
        return bao(f"cham {pha}", [f"đã {TRAN_VONG} vòng: dừng, Khổng Minh quyết hoặc báo Linh"])
    ph, loi = [doc(t) for t in tep], []
    ten = [x.get("nguoi_cham", "") for x in ph]
    if len(set(ten)) < SO_PHIEU:
        loi.append(f"cần {SO_PHIEU} phiếu từ {SO_PHIEU} người chấm khác nhau (có {len(set(ten))})")
    if tho & set(ten):
        loi.append(f"người chấm trùng thợ: {tho & set(ten)}")
    for x in ph:
        thieu = [k for k in tc if not isinstance(x.get("diem", {}).get(k), (int, float))]
        if thieu:
            loi.append(f"phiếu {x.get('nguoi_cham')}: thiếu điểm {thieu}")
    if loi:
        return bao(f"cham {pha}", loi)
    diem = {k: statistics.median(x["diem"][k] for x in ph) for k in tc}
    tong = round(sum(diem.values()) / len(diem), 2)
    phieu_dat = sum(x.get("ket_luan") == "dat" and min(x["diem"].values()) >= 4
                    and not any(l["muc"] in ("chan", "nang") for l in x.get("loi", [])) for x in ph)
    dat = min(diem.values()) >= 4 and phieu_dat * 2 > len(ph)
    v = len(nk) + 1
    kq = "DAT" if dat else ("HOAN_TAC" if nk and tong < nk[-1]["tong"] else "SUA")
    nk.append({"vong": v, "diem": diem, "tong": tong, "ket_qua": kq, "nguoi_cham": ten})
    vg = d / ".vong"
    (vg / "nhat-ky.json").write_text(json.dumps(nk, ensure_ascii=False, indent=1), encoding="utf-8")
    if kq != "HOAN_TAC":
        chup(d, vg / f"ban-v{v}")
    loi_sua = [l for x in ph for l in x.get("loi", []) if l.get("muc") in ("chan", "nang")]
    loi_sua.sort(key=lambda l: l["muc"] != "chan")
    duy = list({l.get("cho", "") + l.get("sua", ""): l for l in loi_sua}.values())[:TRAN_LOI]
    (vg / "phieu-sua.md").write_text(
        f"# Phiếu sửa {pha} sau vòng {v}: {kq}\n\nĐiểm trung vị: {diem}\n\n"
        + ("Chỉ sửa đúng các lỗi dưới, không sửa ngoài phiếu.\n\n" if kq == "SUA" else "")
        + ("Vòng này TỆ HƠN vòng trước: chạy `qc4d.py hoan-tac`, đổi cách sửa.\n\n" if kq == "HOAN_TAC" else "")
        + "\n".join(f"- [{l['muc']}] {l.get('cho')}: {l.get('sua')}" for l in duy), encoding="utf-8")
    print(f"{kq} · cham {pha} vòng {v}: trung bình {tong}, thấp nhất {min(diem.values())}")
    for l in duy:
        print(f" - [{l['muc']}] {l.get('cho')}: {l.get('sua')}")
    return 0 if dat else 1


def hoan_tac(thu_muc, pha):
    d = Path(thu_muc) / pha
    nk = nhat_ky(Path(thu_muc), pha)
    ban = [b for b in sorted((d / ".vong").glob("ban-v*"))]
    if not ban:
        return bao(f"hoan-tac {pha}", ["chưa có bản nào để trả về"])
    for f in d.iterdir():
        if f.name != ".vong":
            shutil.rmtree(f) if f.is_dir() else f.unlink()
    for f in ban[-1].iterdir():
        (shutil.copytree if f.is_dir() else shutil.copy2)(f, d / f.name)
    print(f"Đã trả {pha} về {ban[-1].name}")
    return 0


def bao(ten, loi):
    print(("CHUA_DAT" if loi else "DAT") + f" · {ten}")
    for l in loi[:20]:
        print(" -", l)
    return 1 if loi else 0


if __name__ == "__main__":
    a = sys.argv[1:]
    lenh = {"phong": (phong, 0), "moi": (moi, 3), "kiem": (kiem, 1), "cong": (cong, 2),
            "de-cham": (de_cham, 2), "cham": (cham, 3), "hoan-tac": (hoan_tac, 2)}
    if not a or a[0] not in lenh or len(a) - 1 < lenh[a[0]][1]:
        print(__doc__); sys.exit(2)
    sys.exit(lenh[a[0]][0](*a[1:]))
