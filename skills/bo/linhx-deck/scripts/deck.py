#!/usr/bin/env python3
"""linhx-deck: công cụ dòng lệnh cho quy trình 15 bước làm deck proposal (LAB027).

Chỉ dùng thư viện chuẩn Python 3.9+. Chạy:  python deck.py <lệnh> <thư-mục-deck> [tuỳ chọn]

Lệnh:
  moi <dir> --brand B --ten "Tên deck"   tạo thư mục deck từ mẫu 15 bước
  trang-thai <dir>                        bảng 15 bước: có tệp chưa, cổng đạt chưa, Linh duyệt chưa
  cong <dir> <n>                          chạy cổng bước n (1..15), ghi cong.json, mã thoát 0 = đạt
  hoi <dir> <n> --cau "…"                 ghi câu hỏi + khuyến nghị đã gửi Linh và giờ hỏi (mốc của luật 10 phút)
  duyet <dir> <n> --nguoi "Linh"          ghi Linh đã duyệt bước n (nội dung phải đạt trước; tu-dong-10-phut cần 'hoi' ≥ 10 phút)
  duyet <dir> <n> --bo-qua "lý do"        bỏ qua một bước có lý do (trang-thai không còn báo bước đó)
  doi-chieu <dir>                         bảng offer ↔ pain ↔ năng lực (bước 6)
  ghost <dir>                             in ghost deck từ 10-deck.json ra 10-ghost-deck.md
  kiem-deck <dir> [--ban-cuoi]            kiểm 10-deck.json: tiêu đề kết luận, trần chữ, số có nguồn, từ cấm, tương phản
  goi-anh <dir>                           sinh 11-goi-anh/PROMPT-ANH.md + prompts.json cho ChatGPT Plus
  tai-anh <dir> --ds ung-vien.json        tải ảnh moodboard Claude đã chọn trong Chrome vào 08-moodboard/ + nguon.json
  nhan-anh <dir> --tu THU_MUC --vao moodboard|anh [--ten T] --ref a,b [--nguon URL]
                                          lấy ảnh mới nhất vừa tải về (Downloads), lưu đúng chỗ, giữ bản cũ, ghi nhật ký + ref
  ra-anh <dir>                            đo ảnh trong 11-goi-anh/anh/, tạo/cập nhật 12-ra-anh.json (ảnh đổi thì chấm lại)
  sua-anh <dir>                           sinh prompt sửa (revise) cho ảnh 'sua'/'loai', tối đa 3 vòng mỗi ảnh
  xuat <dir> [--anh-map f.json] [--logo SRC]   dựng 13-claude-deck/project/ cho Claude Slides (logo_ta, logo_khach lấy từ 10-deck.json)
  xem <dir>                               chụp từng slide (Playwright), bắt tràn chữ, lấn lề, chồng chữ, ô ảnh trống; ghép tờ to-slide.png
  logo <dir> [--ta F] [--khach F --khach-ten T]  chép logo gốc vào <dir>/logo/, ghi logo_ta/logo_khach/khach (ta mặc định lấy logo BU)
  bo-cuc ds | chon <dir> [--kieu K --ma ID] | them --ma ID --tep ẢNH --nguon URL   thư viện bố cục slide (bước 8b)
  hanh-trinh <dir>                        kiểm 10-hanh-trinh.json (bước 10b) và vẽ đường chú ý 10-hanh-trinh.png
  neo <dir> [--lay | --luu [--ghi-de]]    thư viện ảnh neo theo brand: lấy phong cách chung của brand, hoặc lưu phong cách deck này làm chung
"""
import argparse
import csv
import datetime
import hashlib
import html
import json
import re
import shutil
import struct
import sys
import time
import urllib.request
from pathlib import Path

for _luong in (sys.stdout, sys.stderr):  # Windows cp1252: lỗi tiếng Việt cũng phải in được
    if hasattr(_luong, "reconfigure"):
        _luong.reconfigure(encoding="utf-8")

GOC = Path(__file__).resolve().parent.parent
DU_LIEU = GOC / "du-lieu"
MAU = DU_LIEU / "mau"

BUOC = {
    1: ("Tiếp nhận, làm rõ đề bài", "01-de-bai.md"),
    2: ("Nghiên cứu nền", "02-bang-chung.csv"),
    3: ("Người nghe, mục tiêu", "03-nguoi-nghe.md"),
    4: ("Pain–gain", "04-pain-gain.json"),
    5: ("Lợi thế của Linh", "05-loi-the.md"),
    6: ("Khoảng trống, offer, mapping năng lực", "06-offer.json"),
    7: ("Ba giải pháp", "07-ba-giai-phap.md"),
    8: ("Moodboard, thẻ phong cách", "08-the-phong-cach.json"),
    9: ("Mô tả dịch vụ", "09-mo-ta-dich-vu.md"),
    10: ("Ghost deck + deck proposal", "10-deck.json"),
    11: ("Gói ảnh ChatGPT Plus", "11-goi-anh/PROMPT-ANH.md"),
    12: ("Rà soát ảnh", "12-ra-anh.json"),
    13: ("Đưa vào Claude deck", "13-claude-deck/project/deck.json"),
    14: ("Demo / prototype", "14-prototype/README.md"),
    15: ("Đóng gói, trình bày", "15-ban-giao/README.md"),
}
CAN_DUYET = {1, 6, 7, 8, 10}

TIEU_DE_CHUNG = ["bối cảnh", "tổng quan", "giới thiệu", "mục lục", "agenda", "nội dung", "phụ lục",
                 "về chúng tôi", "giải pháp", "kế hoạch", "đội ngũ", "kết luận", "cảm ơn", "câu hỏi"]
CUM_CAM = ["phân tích cho thấy", "slide này", "trang này trình bày", "chúng tôi xin trình bày",
           "this slide", "không chỉ là", "it's not", "game changer", "cách mạng hoá", "đột phá chưa từng có"]
KIEU_KHONG_CAN_KET_LUAN = {"bia", "chuong", "muc-luc", "ket"}
KIEU_KHONG_NOI_DUNG = {"bia", "chuong", "muc-luc", "ket"}
HINH_THUC = {  # hình thức chứng minh diem_chinh -> kiểu slide được phép
    "bieu-do": {"bieu-do"}, "bang": {"bang"}, "so-lon": {"so-lon"},
    "so-do": {"lo-trinh", "so-sanh", "the", "doi-ngu"}, "minh-hoa": {"hai-cot", "khang-dinh"},
    "cau": {"tom-tat", "khang-dinh"},  # chỉ slide tóm tắt và slide khẳng định được là câu chữ
}
TIEU_DIEM = {"the": "nhan_manh", "lo-trinh": "nhan_manh", "doi-ngu": "nhan_manh", "bang": "dong_nhan", "so-lon": "so_chinh"}
CAM_XUC = ("to-mo", "lo-lang", "cang", "nhe-nhom", "tin-tuong", "hao-hung", "san-sang")
CANG = {"lo-lang", "cang"}
NHE = {"nhe-nhom", "tin-tuong", "hao-hung"}
TRAN = {  # trần chữ theo kiểu slide (số từ)
    "tieu_de": 15, "diem": 30, "muc_noi_dung": 32, "o_bang": 14, "phu": 40,
    "so_diem_toi_da": 5, "so_muc_toi_da": 4, "so_dong_bang": 7, "so_cot_bang": 5,
}


# ---------------------------------------------------------------- tiện ích

def doc_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def gan_giong(a, b, nguong=0.6):
    """Hai câu gần trùng: tỉ lệ chữ chung trên câu ngắn hơn ≥ ngưỡng."""
    x = set(re.findall(r"\w+", (a or "").lower()))
    y = set(re.findall(r"\w+", (b or "").lower()))
    return bool(x and y) and len(x & y) / min(len(x), len(y)) >= nguong


def so_tu(s):
    return len(re.findall(r"\S+", s or ""))


def ghi_json(p, d):
    """Ghi qua tệp tạm rồi đổi tên: hai phiên cùng ghi không làm hỏng tệp nửa chừng."""
    p = Path(p)
    tam = p.with_name(p.name + f".tam{time.time_ns()}")
    tam.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tam.replace(p)


def bay_gio():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def trang_thai(d):
    p = Path(d) / "trang-thai.json"
    return doc_json(p) if p.exists() else {"duyet": {}}


def luu_trang_thai(d, tt):
    """Đọc lại bản trên đĩa và trộn duyet/cong/hoi trước khi ghi (hai phiên có thể cùng chạy)."""
    p = Path(d) / "trang-thai.json"
    if p.exists():
        cu = doc_json(p)
        for k in ("duyet", "cong", "hoi", "bo_qua"):
            if isinstance(cu.get(k), dict):
                tt[k] = {**cu[k], **(tt.get(k) or {})}
    ghi_json(p, tt)


def thuong_hieu(ten):
    bang = doc_json(DU_LIEU / "thuong-hieu.json")
    if ten not in bang:
        raise SystemExit(f"Không có brand '{ten}'. Có: {', '.join(k for k in bang if not k.startswith('_'))}")
    return bang[ten]


def nang_luc():
    return {x["id"]: x for x in doc_json(DU_LIEU / "nang-luc.json")}


def bang_chung(d):
    p = Path(d) / "02-bang-chung.csv"
    if not p.exists():
        return {}
    with p.open(encoding="utf-8-sig", newline="") as f:
        return {r["id"].strip(): r for r in csv.DictReader(f) if r.get("id", "").strip()}


def lum(hexs):
    h = hexs.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def tuong_phan(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


class KetQua:
    def __init__(self, buoc):
        self.buoc, self.loi, self.canh_bao, self.da_kiem = buoc, [], [], []

    def ok(self, s):
        self.da_kiem.append(s)

    def sai(self, s):
        self.loi.append(s)

    def luu_y(self, s):
        self.canh_bao.append(s)

    @property
    def dat(self):
        return not self.loi

    cho_duyet = False

    def in_ra(self):
        ten = BUOC[self.buoc][0] if self.buoc in BUOC else str(self.buoc)
        nhan = "ĐẠT" if self.dat else ("NỘI DUNG ĐẠT · CHỜ DUYỆT" if self.cho_duyet else "CHƯA ĐẠT")
        print(f"\n== Cổng {self.buoc}: {ten} -> {nhan}")
        for s in self.da_kiem:
            print(f"  ✓ {s}")
        for s in self.canh_bao:
            print(f"  ! {s}")
        for s in self.loi:
            print(f"  ✗ {s}")


def can_muc(kq, text, cac_muc, ten_tep):
    for m in cac_muc:
        if not re.search(r"^#{1,3}\s*" + re.escape(m), text, re.M | re.I):
            kq.sai(f"{ten_tep} thiếu mục '{m}'")


def muc_rong(text):
    """Trả về các tiêu đề ## mà bên dưới không có chữ nào (ngoài comment)."""
    rong = []
    phan = re.split(r"^(#{2,3} .*)$", re.sub(r"<!--.*?-->", "", text, flags=re.S), flags=re.M)
    for i in range(1, len(phan), 2):
        than = re.sub(r"^\s*-\s*[^:\n]*:\s*$", "", phan[i + 1], flags=re.M).strip()
        if not than:
            rong.append(phan[i].strip("# ").strip())
    return rong


# ---------------------------------------------------------------- cổng từng bước

def cong_1(d, kq):
    p = Path(d) / BUOC[1][1]
    if not p.exists():
        return kq.sai("chưa có 01-de-bai.md")
    t = re.sub(r"<!--.*?-->", "", p.read_text(encoding="utf-8"), flags=re.S)
    can_muc(kq, t, ["1. Khách hàng", "2. Người ra quyết định", "3. Họ đang cần gì", "4. Vì sao bây giờ",
                    "5. Kết quả", "6. Ngân sách", "7. Đối thủ", "8. Tiêu chí", "9. BU", "10. Hình thức",
                    "11. Phạm vi", "12. Tư liệu", "13. Quan hệ", "Câu hỏi gửi Linh", "Chốt tối thiểu"], p.name)
    rong = muc_rong(t)
    if rong:
        kq.sai("mục còn trống (ghi [CẦN LINH: …] nếu chưa biết): " + "; ".join(rong))
    can = len(re.findall(r"\[CẦN LINH", t))
    if can:
        kq.luu_y(f"{can} chỗ [CẦN LINH] chưa trả lời")
    for dong, trang_thai_chot in chot_toi_thieu(t).items():
        if trang_thai_chot == "trong":
            kq.luu_y(f"chốt tối thiểu còn trống: '{dong}' (bắt buộc trước bước 10)")
        elif trang_thai_chot == "mac-dinh":
            kq.luu_y(f"chốt tối thiểu '{dong}' mới là mặc định Claude đề xuất, chờ Linh xác nhận")
    hoi = re.search(r"^#{1,3}\s*Câu hỏi gửi Linh.*?(?=^#{1,3} |\Z)", t, re.M | re.S)
    so_hoi = len(re.findall(r"^\s*(?:\d+\.|-)\s+\S", hoi.group(0), re.M)) if hoi else 0
    if so_hoi > 5:
        kq.sai(f"câu hỏi gửi Linh có {so_hoi} câu, tối đa 5 (gộp lại, mỗi câu kèm mặc định)")
    if not kq.loi:
        kq.ok("đủ 13 mục đề bài, có quan hệ/xung đột lợi ích")


def chot_toi_thieu(t):
    """Ba dòng chốt tối thiểu: 'trong' | 'mac-dinh' (Claude đề xuất, chưa Linh xác nhận) | 'chot'."""
    out = {}
    for dong in ("Mục tiêu một câu:", "Giá/khung giá được phép nói:", "Điều tuyệt đối không nói:"):
        m = re.search(re.escape(dong) + r"[ \t]*(.*)", t)
        v = (m.group(1).strip() if m else "")
        out[dong] = "trong" if not v else ("mac-dinh" if re.search(r"mặc định|CẦN LINH|đề xuất", v, re.I) else "chot")
    return out


def cong_2(d, kq):
    bc = bang_chung(d)
    if not bc:
        return kq.sai("02-bang-chung.csv chưa có dòng nào")
    for i, r in bc.items():
        loai = (r.get("loai") or "").strip()
        if loai not in ("nguon", "uoc-tinh", "gia-thuyet", "noi-bo"):
            kq.sai(f"{i}: loai phải là nguon | noi-bo | uoc-tinh | gia-thuyet")
        if not (r.get("du_kien") or "").strip():
            kq.sai(f"{i}: thiếu du_kien")
        if loai == "nguon":
            if not (r.get("nguon_url") or "").strip():
                kq.sai(f"{i}: loai=nguon nhưng thiếu nguon_url")
            if not (r.get("ngay") or "").strip():
                kq.sai(f"{i}: thiếu ngày đọc nguồn")
            if not (r.get("trich_doan") or "").strip():
                kq.luu_y(f"{i}: nên có trich_doan nguyên văn để kiểm lại")
        if loai == "noi-bo" and not (r.get("nguon_ten") or "").strip():
            kq.sai(f"{i}: loai=noi-bo phải ghi nguon_ten (tệp/đường dẫn)")
        if loai == "noi-bo":
            ten = (r.get("nguon_ten") or "").strip()
            m_ = re.match(r"^((?:[A-Za-z]:[\\/]|/).*?\.[A-Za-z0-9]{2,5})(?=$|[\s,;(#])", ten)
            duong = m_.group(1) if m_ else (ten if re.match(r"^[A-Za-z]:[\\/]|^/", ten) else "")
            if duong and not Path(duong).exists() and not Path(ten).exists():
                kq.luu_y(f"{i}: không thấy tệp nội bộ {duong}")
        if loai == "noi-bo" and not (r.get("duoc_len_slide") or "").strip():
            kq.luu_y(f"{i}: số nội bộ chưa đánh dấu duoc_len_slide (co/khong/hoi-linh)")
        if (r.get("duoc_len_slide") or "").strip() not in ("", "co", "khong", "hoi-linh"):
            kq.sai(f"{i}: duoc_len_slide phải là co | khong | hoi-linh")
    n_nguon = sum(1 for r in bc.values() if r.get("loai") in ("nguon", "noi-bo"))
    n_cong_khai = sum(1 for r in bc.values() if r.get("loai") == "nguon")
    if n_nguon < 5:
        kq.sai(f"mới có {n_nguon} bằng chứng có nguồn, cần ít nhất 5")
    if n_cong_khai < 2:
        kq.sai(f"mới có {n_cong_khai} nguồn công khai (loai=nguon), cần ít nhất 2: deck chào khách không thể chỉ dựa vào tài liệu nội bộ")
    md = Path(d) / "02-nghien-cuu.md"
    if not md.exists():
        kq.sai("chưa có 02-nghien-cuu.md")
    else:
        la = sorted(set(re.findall(r"\bBC\d+\b", md.read_text(encoding="utf-8"))) - set(bc))
        if la:
            kq.sai(f"02-nghien-cuu.md trỏ mã không có trong CSV: {la}")
    kq.ok(f"{len(bc)} dòng bằng chứng, {n_nguon} có nguồn")


def cong_3(d, kq):
    p = Path(d) / BUOC[3][1]
    if not p.exists():
        return kq.sai("chưa có 03-nguoi-nghe.md")
    t = p.read_text(encoding="utf-8")
    can_muc(kq, t, ["1. Ai", "2. Lập trường", "3. Quyết định", "4. Họ có bao nhiêu", "5. Điều họ quan tâm",
                    "6. Sau buổi", "Trình tự lập luận"], p.name)
    rong = muc_rong(t)
    if rong:
        kq.sai("mục còn trống: " + "; ".join(rong))
    if not re.search(r"Trình tự:\s*(Trực tiếp|Gián tiếp)", t, re.I):
        kq.sai("chưa chọn trình tự: Trực tiếp hoặc Gián tiếp")
    kq.ok("đủ 5 câu người nghe + trình tự")


def cong_4(d, kq):
    p = Path(d) / BUOC[4][1]
    if not p.exists():
        return kq.sai("chưa có 04-pain-gain.json")
    pg = doc_json(p)
    bc = bang_chung(d)
    for loai, toi_thieu in (("pains", 3), ("gains", 2)):
        ds = pg.get(loai, [])
        if len(ds) < toi_thieu:
            kq.sai(f"cần ít nhất {toi_thieu} {loai}, mới có {len(ds)}")
        for x in ds:
            if not isinstance(x.get("diem"), int) or not 1 <= x["diem"] <= 10:
                kq.sai(f"{x.get('id')}: diem phải là số nguyên 1–10")
            ids = x.get("bang_chung") or []
            thieu = [i for i in ids if i not in bc]
            if thieu:
                kq.sai(f"{x.get('id')}: bằng chứng không có trong 02-bang-chung.csv: {thieu}")
            if not ids and x.get("nhan") != "gia-thuyet":
                kq.sai(f"{x.get('id')}: không có bằng chứng thì nhan phải là 'gia-thuyet'")
            if x.get("mo_ta", "").startswith("<"):
                kq.sai(f"{x.get('id')}: mô tả còn là mẫu")
    for x in pg.get("pains", []):
        if x.get("diem", 0) >= 7 and x.get("nhan") != "gia-thuyet":
            co_so = any((bc.get(i, {}).get("so_lieu") or "").strip() for i in x.get("bang_chung") or [])
            if not (x.get("trich") or "").strip() and not co_so:
                kq.sai(f"{x.get('id')}: điểm {x['diem']} nghĩa là khách đã nói ra hoặc có số: ghi 'trich' (nguyên văn lời khách) hoặc trỏ BC có so_lieu, không thì nhan='gia-thuyet'")
        if x.get("nhan") == "gia-thuyet" and x.get("bang_chung"):
            kq.luu_y(f"{x.get('id')}: vừa 'gia-thuyet' vừa có bằng chứng: chọn một")
    gt = [x["id"] for x in pg.get("pains", []) if x.get("nhan") == "gia-thuyet" and x.get("diem", 0) >= 7]
    if gt:
        kq.luu_y(f"pain điểm cao nhưng mới là giả thuyết, cần hỏi lại khách: {gt}")
    kq.ok(f"{len(pg.get('pains', []))} pain, {len(pg.get('gains', []))} gain")


def cong_5(d, kq):
    p = Path(d) / BUOC[5][1]
    if not p.exists():
        return kq.sai("chưa có 05-loi-the.md")
    t = p.read_text(encoding="utf-8")
    nl = nang_luc()
    ids = sorted(set(re.findall(r"NL-\d{2}", t)))
    la = [i for i in ids if i not in nl]
    if la:
        kq.sai(f"mã năng lực không có trong nang-luc.json: {la}")
    if len(ids) < 3:
        kq.sai(f"cần ít nhất 3 lợi thế có mã NL-xx, mới có {len(ids)}")
    chua = [i for i in ids if i in nl and nl[i]["muc_do"] != "da-chung-minh"]
    for i in chua:
        dong = next((l for l in t.splitlines() if i in l), "")
        if not re.search(r"đang thử|thí điểm|ý tưởng|dang-thu|y-tuong", dong, re.I):
            kq.sai(f"{i} mới ở mức '{nl[i]['muc_do']}', dòng đó phải ghi rõ 'đang thử' hoặc 'thí điểm'")
    if "Điểm yếu" not in t or any(m.startswith("Điểm yếu") for m in muc_rong(t)):
        kq.sai("phải viết điểm yếu thật sự và cách bù")
    kq.ok(f"{len(ids)} lợi thế trỏ về nang-luc.json")


def cong_6(d, kq, in_bang=False):
    p = Path(d) / BUOC[6][1]
    if not p.exists():
        return kq.sai("chưa có 06-offer.json")
    of = doc_json(p)
    pg = doc_json(Path(d) / BUOC[4][1]) if (Path(d) / BUOC[4][1]).exists() else {"pains": [], "gains": []}
    pains = {x["id"]: x for x in pg.get("pains", [])}
    gains = {x["id"]: x for x in pg.get("gains", [])}
    kt = {x["id"]: x for x in of.get("khoang_trong", [])}
    nl = nang_luc()
    bc = bang_chung(d)
    for k in kt.values():
        if not k.get("bang_chung"):
            kq.luu_y(f"{k['id']}: khoảng trống chưa có bằng chứng")
        for i in k.get("bang_chung", []):
            if i not in bc:
                kq.sai(f"{k['id']}: {i} không có trong 02-bang-chung.csv")
    offers = of.get("offers", [])
    if not offers:
        kq.sai("chưa có offer nào")
    bang = []
    for o in offers:
        oid = o.get("id")
        for i in o.get("giai_pain", []):
            if i not in pains:
                kq.sai(f"{oid}: pain {i} không có trong 04-pain-gain.json")
        for i in o.get("tao_gain", []):
            if i not in gains:
                kq.sai(f"{oid}: gain {i} không có trong 04-pain-gain.json")
        for i in o.get("lap_khoang_trong", []):
            if i not in kt:
                kq.sai(f"{oid}: khoảng trống {i} không có")
        manh = [i for i in o.get("giai_pain", []) if pains.get(i, {}).get("diem", 0) >= 7]
        if not manh:
            if o.get("nhan") == "phu":
                kq.luu_y(f"{oid}: offer phụ, không giải pain ≥ 7: chỉ bán kèm offer chính")
            else:
                kq.sai(f"{oid}: không giải pain nào có điểm ≥ 7, offer yếu (offer bổ trợ thì gắn nhan='phu')")
        nls = o.get("nang_luc", [])
        la = [i for i in nls if i not in nl]
        if la:
            kq.sai(f"{oid}: năng lực không có trong nang-luc.json: {la}")
        da_cm = [i for i in nls if nl.get(i, {}).get("muc_do") == "da-chung-minh"]
        chinh = nls[0] if nls else None  # năng lực đầu tiên là năng lực làm phần chính của offer
        if (not chinh or nl.get(chinh, {}).get("muc_do") != "da-chung-minh") and o.get("nhan") not in ("thi-diem",):
            kq.sai(f"{oid}: năng lực chính ({chinh}) chưa 'da-chung-minh': gắn nhan='thi-diem' (năng lực phụ đã chứng minh không đủ)")
        if not o.get("nang_luc_lam_gi"):
            kq.luu_y(f"{oid}: thiếu 'nang_luc_lam_gi' (mỗi NL làm phần nào của offer) để Linh soát")
        if str(o.get("ten", "")).startswith("<"):
            kq.sai(f"{oid}: tên còn là mẫu")
        bang.append((oid, o.get("ten", ""), ",".join(o.get("giai_pain", [])), ",".join(manh),
                     ",".join(nls), ",".join(da_cm) or "-", o.get("nhan", ""), o.get("gia", "")))
    if in_bang:
        print("| Offer | Tên | Giải pain | Pain ≥7 | Năng lực | Đã chứng minh | Nhãn | Giá |")
        print("|---|---|---|---|---|---|---|---|")
        for r in bang:
            print("| " + " | ".join(str(x) for x in r) + " |")
        khong_ai = [i for i, x in pains.items() if x.get("diem", 0) >= 7 and not any(i in o.get("giai_pain", []) for o in offers)]
        if khong_ai:
            print(f"\nPain ≥7 chưa offer nào giải: {khong_ai}")
    kq.ok(f"{len(offers)} offer đối chiếu với pain và năng lực")


def cong_7(d, kq):
    p = Path(d) / BUOC[7][1]
    if not p.exists():
        return kq.sai("chưa có 07-ba-giai-phap.md")
    t = re.sub(r"<!--.*?-->", "", p.read_text(encoding="utf-8"), flags=re.S)
    gp = re.findall(r"^## Giải pháp (\d)", t, re.M)
    if sorted(gp) != ["1", "2", "3"]:
        kq.sai(f"cần đúng 3 mục '## Giải pháp 1/2/3', đang có {gp}")
    if "<tên" in t:
        kq.sai("tên giải pháp còn là mẫu")
    if not re.search(r"^\|.*GP1.*GP2.*GP3", t, re.M):
        kq.sai("thiếu bảng so sánh GP1/GP2/GP3")
    m = re.search(r"Khuyến nghị:\s*Giải pháp\s*(\d)\s*,?\s*vì\s*(.+)", t)
    if not m or len(m.group(2).strip()) < 10:
        kq.sai("thiếu dòng 'Khuyến nghị: Giải pháp n, vì …' có lý do")
    of = doc_json(Path(d) / BUOC[6][1]) if (Path(d) / BUOC[6][1]).exists() else {"offers": []}
    ma_o = {o["id"]: o for o in of.get("offers", [])}
    tap = []
    for so in "123":
        khoi = re.search(rf"^## Giải pháp {so}.*?(?=^## |\Z)", t, re.M | re.S)
        if khoi and not re.search(r"\bP\d+\b", khoi.group(0)):
            kq.sai(f"Giải pháp {so} chưa trỏ pain nào (P1, P2…)")
        os_ = set(re.findall(r"\bO\d+\b", khoi.group(0))) if khoi else set()
        if khoi and not os_:
            kq.sai(f"Giải pháp {so} chưa trỏ offer nào (O1, O2…)")
        la = sorted(os_ - set(ma_o))
        if la:
            kq.sai(f"Giải pháp {so} trỏ offer không có trong 06-offer.json: {la}")
        tap.append(frozenset(os_))
        if m and m.group(1) == so and os_ and not any(ma_o.get(i, {}).get("nhan") in ("chinh", None) for i in os_):
            kq.sai(f"giải pháp khuyến nghị ({so}) không chứa offer chính nào")
    if len(tap) == 3 and len(set(tap)) == 1 and tap[0]:
        kq.luu_y("ba giải pháp trỏ cùng một tập offer: có thể chỉ là 3 mức giá của một thứ")
    kq.ok("ba giải pháp, có so sánh và khuyến nghị")


def cong_8(d, kq):
    p = Path(d) / BUOC[8][1]
    if not p.exists():
        return kq.sai("chưa có 08-the-phong-cach.json")
    s = doc_json(p)
    if len(s.get("huong", [])) != 3:
        kq.sai("cần đúng 3 hướng phong cách để Linh chọn bằng mắt")
    if s.get("huong_chon") not in [h.get("id") for h in s.get("huong", [])]:
        kq.sai("huong_chon không khớp hướng nào")
    mau = s.get("bang_mau", [])
    if not 3 <= len(mau) <= 7 or not all(re.fullmatch(r"#[0-9A-Fa-f]{6}", m) for m in mau):
        kq.sai("bang_mau cần 3–7 mã hex dạng #RRGGBB")
    anh = s.get("nguon_anh", [])
    if len(anh) < 6:
        kq.sai(f"moodboard cần 6–10 ảnh, mới có {len(anh)}")
    for a in anh:
        if not (Path(d) / a.get("tep", "")).exists():
            kq.sai(f"không thấy tệp moodboard {a.get('tep')}")
        if not a.get("nguon"):
            kq.sai(f"{a.get('tep')}: thiếu nguồn ảnh")
    for k in ("bo_cuc", "chu", "anh_minh_hoa"):
        if not s.get(k) or str(s.get(k)).startswith("<"):
            kq.sai(f"thẻ phong cách thiếu '{k}'")
    if (thu_neo(s.get("brand") or (doc_deck(d) or {}).get("brand", "linhx")) / "anh-neo.png").exists() and not s.get("neo_brand"):
        kq.luu_y("brand đã có ảnh neo chung (deck.py neo <dir> --lay); thẻ này tạo phong cách mới, chỉ đúng khi Linh yêu cầu")
    kq.ok("thẻ phong cách có bảng màu, 3 hướng, nguồn ảnh")


def cong_9(d, kq):
    p = Path(d) / BUOC[9][1]
    if not p.exists():
        return kq.sai("chưa có 09-mo-ta-dich-vu.md")
    t = re.sub(r"<!--.*?-->", "", p.read_text(encoding="utf-8"), flags=re.S)
    goi = re.split(r"^## Gói:", t, flags=re.M)[1:]
    if not goi:
        kq.sai("chưa có gói nào ('## Gói: …')")
    for g in goi:
        ten = g.splitlines()[0].strip()
        if ten.startswith("<"):
            kq.sai("tên gói còn là mẫu")
        for nhan in ("Làm gì", "Đầu ra", "Mốc", "Điều kiện", "Giá", "Bằng chứng"):
            m = re.search(r"\*\*" + nhan + r":\*\*[ \t]*(.*)", g)
            if not m or not m.group(1).strip():
                kq.sai(f"gói '{ten}': nhãn '{nhan}' còn trống")
        m = re.search(r"\*\*Bằng chứng:\*\*[ \t]*(.*)", g)
        if m and m.group(1).strip() and not re.search(r"NL-\d{2}|BC\d+", m.group(1)):
            kq.sai(f"gói '{ten}': bằng chứng phải trỏ NL-xx hoặc BCxx")
    kq.ok(f"{len(goi)} gói dịch vụ")


def doc_deck(d):
    p = Path(d) / BUOC[10][1]
    return doc_json(p) if p.exists() else None


def chu_slide(s, noi=" "):
    """Gom toàn bộ chữ hiển thị của một slide (không gồm ghi chú người nói). noi="
" giữ ranh giới trường."""
    out = []

    def gom(x):
        if isinstance(x, str):
            out.append(x)
        elif isinstance(x, list):
            for y in x:
                gom(y)
        elif isinstance(x, dict):
            for k, v in x.items():
                if k not in ("id", "kieu", "ghi_chu", "bang_chung", "anh", "minh_hoa", "so_la_nhan", "khuyen_nghi", "nguon"):
                    gom(v)
    gom({k: v for k, v in s.items()})
    return noi.join(out)


def tu_cam_brand(brand):
    ds = list(CUM_CAM)
    try:
        ds += thuong_hieu(brand).get("tu_cam", [])
    except SystemExit:
        pass
    p = DU_LIEU / "local" / f"{brand}.md"
    if p.exists():
        ds += [m.strip() for m in re.findall(r"^-\s*cấm:\s*(.+)$", p.read_text(encoding="utf-8"), re.M)]
    return [x.lower() for x in ds if x]


TI_LE_ANH = ("2:3", "4:5", "1:1", "3:2", "16:9")
# trần chữ thân (không tính tiêu đề) theo kiểu slide: (trình bày có người nói, gửi đọc)
TRAN_THAN = {"tom-tat": (80, 120), "the": (60, 100), "bang": (90, 130), "so-lon": (40, 60), "so-sanh": (75, 110),
             "lo-trinh": (60, 100), "hai-cot": (50, 90), "doi-ngu": (60, 100), "khang-dinh": (30, 50), "ket": (50, 70),
             "muc-luc": (40, 60)}


def doc_mat_do(d):
    p = Path(d) / BUOC[3][1]
    t = p.read_text(encoding="utf-8") if p.exists() else ""
    m = re.search(r"Mật độ:\s*(.*)", t)
    return "gửi đọc" if m and re.search(r"gửi đọc|đủ ý", m.group(1), re.I) and not re.search(r"ít chữ|có người nói", m.group(1), re.I) else "trình bày"


def tran_than(kieu, mat_do):
    t = TRAN_THAN.get(kieu)
    return (t[1] if mat_do == "gửi đọc" else t[0]) if t else None


KIEU_NO_NOI_DUNG_SAFE = KIEU_KHONG_NOI_DUNG


def kiem_tieu_diem(s, kieu, sid, kq, ban_cuoi=False):
    """Mỗi slide nội dung: một diem_chinh, một hình thức chứng minh, một tiêu điểm (không có hai khối ngang nhau)."""
    dc = s.get("diem_chinh")
    if not dc:
        kq.sai(f"{sid}: thiếu diem_chinh (một điểm duy nhất người nghe phải nhớ, ≤ 12 chữ)")
    elif so_tu(dc) > 12:
        kq.sai(f"{sid}: diem_chinh {so_tu(dc)} chữ, tối đa 12")
    elif gan_giong(s.get("tieu_de", ""), dc, 0.7):
        kq.luu_y(f"{sid}: diem_chinh gần trùng tiêu đề: tiêu đề là kết luận, diem_chinh là bằng chứng/điều cần nhớ")
    ht = s.get("hinh_thuc")
    if ht not in HINH_THUC:
        kq.sai(f"{sid}: hinh_thuc phải là một trong {', '.join(HINH_THUC)}")
    elif kieu not in HINH_THUC[ht]:
        kq.sai(f"{sid}: hinh_thuc '{ht}' không khớp kiểu '{kieu}' (cần {', '.join(sorted(HINH_THUC[ht]))}); slide toàn chữ phải đổi sang biểu đồ/bảng/số/sơ đồ/minh hoạ")
    if ht == "minh-hoa" and not s.get("anh"):
        kq.sai(f"{sid}: hinh_thuc 'minh-hoa' nhưng không có ô ảnh")
    k = TIEU_DIEM.get(kieu)
    so_khoi = len(s.get({"the": "muc", "lo-trinh": "buoc", "doi-ngu": "nguoi", "bang": "dong", "so-lon": "so"}.get(kieu, ""), []) or [])
    if k and so_khoi > 1 and not isinstance(s.get(k), int):
        kq.sai(f"{sid}: {so_khoi} khối ngang nhau, mắt bị chia: đặt '{k}' (chỉ số khối chứng minh diem_chinh)")
    if kieu == "so-sanh" and not any(x.get("khuyen_nghi") for x in s.get("phuong_an", [])):
        kq.sai(f"{sid}: so sánh không có phương án khuyến nghị: không có tiêu điểm")
    if kieu == "bieu-do":
        bd = s.get("bieu_do") or {}
        if bd.get("loai") not in ("cot", "ngang", "chong", "thac", "duong"):
            kq.sai(f"{sid}: bieu_do.loai phải là cot | ngang | chong | thac | duong (không dùng tròn, 3D)")
        gt = (bd.get("chuoi") or [{}])[0].get("gia_tri") or []
        if not gt or len(gt) != len(bd.get("nhan") or []):
            kq.sai(f"{sid}: bieu_do cần 'nhan' và 'chuoi[0].gia_tri' cùng độ dài")
        if not isinstance(bd.get("diem_nhan"), int):
            kq.sai(f"{sid}: bieu_do thiếu 'diem_nhan' (cột/điểm chứng minh diem_chinh, chỉ nó mang màu nhấn)")
        if not s.get("bang_chung") and not s.get("minh_hoa"):
            kq.sai(f"{sid}: biểu đồ phải trỏ bang_chung (BCxx) như mọi con số")
        if not s.get("nguon"):
            kq.luu_y(f"{sid}: biểu đồ nên có dòng nguồn ở chân trang ('nguon')")


def kiem_deck(d, kq, ban_cuoi=False):
    dk = doc_deck(d)
    if not dk:
        return kq.sai("chưa có 10-deck.json")
    brand = dk.get("brand", "linhx")
    th = thuong_hieu(brand)
    m = th["mau"]
    for a, b, ten, nguong in (("chu", "sang", "chữ thân trên nền sáng", 4.5), ("chu_phu", "sang", "chữ phụ trên nền sáng", 4.5),
                              ("tieu_de", "sang", "tiêu đề trên nền sáng", 3.0), ("chu", "xen", "chữ trên nền thẻ", 4.5),
                              ("tren_toi", "toi", "chữ trên nền tối", 4.5), ("tren_toi_phu", "toi", "chữ phụ trên nền tối", 4.5)):
        tp = tuong_phan(m[a], m[b])
        (kq.ok if tp >= nguong else kq.sai)(f"tương phản {ten} {tp:.2f}:1 (cần ≥ {nguong})")
    bc = bang_chung(d)
    cam = tu_cam_brand(brand)
    mat_do = doc_mat_do(d)
    cho_phep = {}
    ids = set()
    slides = dk.get("slides", [])
    if not slides:
        return kq.sai("10-deck.json chưa có slide")
    if slides[0].get("kieu") != "bia":
        kq.sai("slide đầu phải là bìa (kieu 'bia')")
    if not any(s.get("kieu") == "tom-tat" for s in slides[:4]):
        kq.sai("cần một slide tóm tắt (kieu 'tom-tat') trong 4 slide đầu: người bận chỉ đọc trang này")
    for s in slides:
        sid = s.get("id", "?")
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", sid):
            kq.sai(f"id slide không hợp lệ: {sid}")
        if sid in ids:
            kq.sai(f"trùng id slide: {sid}")
        ids.add(sid)
        kieu = s.get("kieu")
        if kieu not in RENDER:
            kq.sai(f"{sid}: kiểu '{kieu}' không có. Có: {', '.join(RENDER)}")
            continue
        td = s.get("tieu_de", "")
        if not td:
            kq.sai(f"{sid}: thiếu tieu_de")
        if kieu not in KIEU_KHONG_CAN_KET_LUAN:
            n = so_tu(td)
            if n < 6:
                kq.sai(f"{sid}: tiêu đề '{td}' chỉ {n} chữ, phải là một câu kết luận (6–{TRAN['tieu_de']} chữ)")
            if n > TRAN["tieu_de"]:
                kq.sai(f"{sid}: tiêu đề {n} chữ, quá {TRAN['tieu_de']}")
            if td.strip().lower().rstrip(":") in TIEU_DE_CHUNG or any(td.lower().startswith(x + ":") for x in TIEU_DE_CHUNG):
                kq.sai(f"{sid}: tiêu đề '{td}' là nhãn chủ đề, không phải kết luận")
            if td.strip().endswith(("?", ":")):
                kq.sai(f"{sid}: tiêu đề kết thúc bằng '?' hoặc ':' — viết thành câu khẳng định")
        if kieu not in KIEU_NO_NOI_DUNG_SAFE:
            kiem_tieu_diem(s, kieu, sid, kq, ban_cuoi)
        if kieu not in KIEU_KHONG_CAN_KET_LUAN and re.search(r"\s(và|and)\s", td):
            hai = re.split(r"\s(?:và|and)\s", td, maxsplit=1)
            if len(hai) == 2 and so_tu(hai[0]) >= 5 and so_tu(hai[1]) >= 5:
                kq.luu_y(f"{sid}: tiêu đề nối hai ý bằng 'và': mỗi slide một ý, cân nhắc tách")
        chu = chu_slide(s)
        thap = chu.lower()
        for c in cam:
            if c in thap:
                kq.sai(f"{sid}: có cụm cấm '{c}'")
        for k, gioi_han in (("diem", TRAN["so_diem_toi_da"]), ("muc", TRAN["so_muc_toi_da"])):
            if isinstance(s.get(k), list) and len(s[k]) > gioi_han:
                kq.sai(f"{sid}: {len(s[k])} {k}, tối đa {gioi_han}: tách slide, đừng co chữ")
        for x in s.get("diem", []) or []:
            if so_tu(x if isinstance(x, str) else json.dumps(x, ensure_ascii=False)) > TRAN["diem"]:
                kq.sai(f"{sid}: một ý quá {TRAN['diem']} chữ")
        for x in s.get("muc", []) or []:
            if so_tu(x.get("noi_dung", "")) > TRAN["muc_noi_dung"]:
                kq.sai(f"{sid}: thẻ '{x.get('tieu_de')}' quá {TRAN['muc_noi_dung']} chữ")
        if kieu == "bang":
            if len(s.get("cot", [])) > TRAN["so_cot_bang"] or len(s.get("dong", [])) > TRAN["so_dong_bang"]:
                kq.sai(f"{sid}: bảng quá {TRAN['so_dong_bang']} dòng × {TRAN['so_cot_bang']} cột")
            for r in s.get("dong", []):
                for o in r:
                    if so_tu(str(o)) > TRAN["o_bang"]:
                        kq.sai(f"{sid}: ô bảng quá {TRAN['o_bang']} chữ: '{str(o)[:40]}…'")
        if kieu == "so-sanh" and len(s.get("phuong_an", [])) != 3:
            kq.sai(f"{sid}: slide so sánh cần đúng 3 phương án")
        # số liệu phải có nguồn (ngày tháng, quý, tuần thứ… không phải số liệu)
        if kieu not in ("bia", "chuong", "muc-luc"):
            chu_so = re.sub(r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b|\btháng\s*\d{1,2}(?:/\d{2,4})?\b|\bT\d{1,2}\b|\b\d{1,2}/\d{4}\b|\b(?:tuần|ngày|bước|chặng|giai đoạn)\s*\d{1,2}(?:/\d{1,2}(?:/\d{2,4})?)?\b|\b\d+(?:\.\d+){2,}\b|\b(?:mục|điều|khoản|phần)\s*\d+(?:\.\d+)*\b|\b(?:Q|quý\s?)\d\b|\b(?:19|20)\d{2}\b|\b(?:GP|PA|O|P|G|K|H|BC|NL-)\d+\b", " ", chu, flags=re.I)
            so = [x for x in re.findall(r"\d[\d.,]*\s*%?", chu_so) if not re.fullmatch(r"0?\d", x.strip())]
            if so and not s.get("minh_hoa") and not s.get("so_la_nhan"):
                bcs = s.get("bang_chung", [])
                if not bcs:
                    kq.sai(f"{sid}: có số {so[:3]} nhưng không có bang_chung (hoặc đặt minh_hoa: true)")
                for i in bcs:
                    if i not in bc:
                        kq.sai(f"{sid}: {i} không có trong 02-bang-chung.csv")
                nguon_txt = " ".join((bc[i].get("so_lieu", "") + " " + bc[i].get("du_kien", "")) for i in bcs if i in bc)
                so_nguon = set(re.findall(r"\d[\d.,]*", re.sub(r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b", " ", nguon_txt)))
                td_so = re.sub(r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b|\b\d+\s*(?:tuần|tháng|ngày|buổi|bước|phút|giờ|chặng|cổng|gói|giai đoạn)\b", " ", td, flags=re.I)
                for x in re.findall(r"\d[\d.,]*", td_so):
                    if len(x) > 1 and x not in so_nguon:
                        kq.luu_y(f"{sid}: số '{x}' trong tiêu đề không thấy trong bằng chứng {bcs}")
        for i in s.get("bang_chung", []) or []:
            dls = (bc.get(i, {}).get("duoc_len_slide") or "").strip()
            if dls == "khong":
                kq.sai(f"{sid}: {i} đánh dấu không được lên slide (số nội bộ/nhạy cảm)")
            elif dls == "hoi-linh":
                cho_phep.setdefault(i, []).append(sid)
        if re.search(r"[\w.+-]+@[\w-]+\.[\w.]+|(?<!\d)(?:\+?84|0)(?:[\s.]?\d){9,10}(?!\d)", chu):
            kq.sai(f"{sid}: có email hoặc số điện thoại trên slide: bỏ (riêng tư)")
        than = (so_tu(re.sub(r"\[(?:CẦN LINH|Linh chốt|chưa tìm thấy)[^\]]*\]", " ", chu)) - so_tu(td) - so_tu(s.get("phan", ""))
                - so_tu(s.get("diem_chinh", "")))  # điểm chính là tiêu điểm, không tính vào trần chữ thân
        tran = tran_than(kieu, mat_do)
        if tran and than > tran * 1.6:
            kq.sai(f"{sid}: {than} chữ thân, trần {tran} cho kiểu '{kieu}' ({mat_do}): tách slide hoặc rút gọn, không co chữ")
        elif tran and than > tran:
            kq.luu_y(f"{sid}: {than} chữ thân, nên ≤ {tran} ({mat_do})")
        gc = so_tu(s.get("ghi_chu", ""))
        if kieu not in ("bia", "chuong", "ket") and s.get("ghi_chu") and not 40 <= gc <= 170:
            kq.luu_y(f"{sid}: ghi chú người nói {gc} chữ, nên 60–150")
        a = s.get("anh")
        if a is not None:
            for k in ("tep", "y_tuong", "ti_le", "mo_ta"):
                if not (isinstance(a, dict) and a.get(k)):
                    kq.sai(f"{sid}: ô ảnh thiếu '{k}'")
            if isinstance(a, dict):
                if a.get("ti_le") and a["ti_le"] not in TI_LE_ANH:
                    kq.sai(f"{sid}: ti_le '{a['ti_le']}' không hợp lệ, chọn {', '.join(TI_LE_ANH)}")
                yt = a.get("y_tuong", "")
                if yt and sum(c.isascii() for c in yt) < 0.9 * len(yt):
                    kq.sai(f"{sid}: y_tuong của ảnh phải viết tiếng Anh (prompt cho ChatGPT)")
                if re.search(r"\b(logo|text|slogan|chữ)\b", re.sub(r"no (?:text|logos?)|without (?:text|logos?)", "", yt, flags=re.I), re.I):
                    kq.sai(f"{sid}: y_tuong nhắc tới chữ/logo: ảnh AI không được có chữ, logo")
        con = re.findall(r"\[(?:CẦN LINH|Linh chốt)[^\]]*\]", chu)
        if con:
            (kq.sai if ban_cuoi else kq.luu_y)(f"{sid}: còn {len(con)} chỗ chờ Linh: {con[:2]}")
        if kieu not in ("bia",) and not s.get("ghi_chu"):
            kq.luu_y(f"{sid}: chưa có ghi chú người nói")
    if cho_phep:
        (kq.sai if ban_cuoi else kq.luu_y)("chờ Linh cho phép đưa lên slide: " + "; ".join(f"{i} ({', '.join(v)})" for i, v in sorted(cho_phep.items())))
    for l in kiem_logo(d, dk):
        (kq.sai if ban_cuoi else kq.luu_y)(l)
    so_anh = len(anh_trong_deck(dk))
    if not 2 <= so_anh <= 5:
        kq.luu_y(f"{so_anh} ô ảnh: deck proposal thường 3–4 ảnh (bìa, trang chương, 1–2 trang hai cột)")
    if slides and slides[0].get("kieu") == "bia" and not slides[0].get("anh"):
        kq.luu_y("bìa chưa có ô ảnh")
    bia_khach = slides[0].get("khach", "") if slides else ""
    if dk.get("khach") and bia_khach and dk["khach"].split(" –")[0].lower() not in bia_khach.lower():
        kq.luu_y(f"khach của deck ('{dk['khach']}') không thấy trong dòng khách ở bìa ('{bia_khach}')")
    p1 = Path(d) / BUOC[1][1]
    if p1.exists():
        t1 = p1.read_text(encoding="utf-8")
        toan_deck = " ".join(chu_slide(s_) + " " + (s_.get("ghi_chu") or "") for s_ in slides).lower()
        m_cam = re.search(r"Điều tuyệt đối không nói:[ \t]*(.*)", t1)
        for cum in re.findall(r"[\"“'‘]([^\"”'’]{3,60})[\"”'’]", m_cam.group(1) if m_cam else ""):
            if cum.lower() in toan_deck:
                kq.sai(f"deck có '{cum}' nằm trong 'Điều tuyệt đối không nói' (01)")
        m_gia = re.search(r"Giá/khung giá được phép nói:[ \t]*(.*)", t1)
        if m_gia and re.search(r"không nêu|không nói|chưa nói|không đưa", m_gia.group(1), re.I):
            for s_ in slides:
                bd_ = s_.get("bieu_do") or {}
                if re.search(r"đồng|vnđ|vnd|usd|eur|\$|€|triệu đồng|tỷ đồng", str(bd_.get("don_vi", "")), re.I):
                    kq.sai(f"{s_.get('id')}: biểu đồ đơn vị tiền ({bd_.get('don_vi')}) trong khi 01 ghi không nêu giá")
                c_ = chu_slide(s_, "\n")  # từng trường một dòng: "đầu tư" ở diem_chinh không bắt số doanh thu ở trường sau
                if re.search(r"\d[\d.,]*\s*(?:đ\b|đồng|vnđ|vnd|usd|eur|\$|€)|(?:\$|€)\s*\d|(?:giá|phí|chi phí|ngân sách|báo giá|đầu tư)[^.\n]{0,30}\d[\d.,]*\s*(?:triệu|tr\b|tỷ|nghìn)|\d[\d.,]*\s*(?:triệu|tỷ|nghìn)\s*(?:đồng|vnđ|vnd)", c_, re.I):
                    kq.sai(f"{s_.get('id')}: có con số tiền trong khi 01 ghi không nêu giá")
        for dong, tt_ in chot_toi_thieu(t1).items():
            if tt_ == "trong":
                kq.sai(f"chốt tối thiểu '{dong}' còn trống: deck đứng trên giả định (bước 1)")
            elif tt_ == "mac-dinh":
                (kq.sai if ban_cuoi else kq.luu_y)(f"chốt tối thiểu '{dong}' vẫn là mặc định, Linh chưa xác nhận")
    so_slide = len(slides)
    if so_slide > 25:
        kq.luu_y(f"{so_slide} slide: deck proposal nên ≤ 20 slide chính, phần còn lại đưa vào phụ lục")
    kq.ok(f"{so_slide} slide, brand {brand}")


def van_tieu_de_cu(d):
    dk = doc_deck(d) or {}
    return hashlib.sha1("\n".join(s.get("tieu_de", "") for s in dk.get("slides", [])).encode("utf-8")).hexdigest()[:12]


def van_tieu_de(d):
    """Dấu vân thứ Linh duyệt ở cổng 10: ghost deck (tiêu đề) + hành trình chú ý."""
    dk = doc_deck(d) or {}
    ht = Path(d) / "10-hanh-trinh.json"
    goc = "\n".join(s.get("tieu_de", "") for s in dk.get("slides", [])) + (ht.read_text(encoding="utf-8") if ht.exists() else "")
    return hashlib.sha1(goc.encode("utf-8")).hexdigest()[:12]


def kiem_hanh_trinh(d, kq):
    """Bước 10b: 10-hanh-trinh.json, một dòng mỗi slide: cảm xúc, tải chú ý, móc/nghỉ. Luật nhịp chú ý."""
    p = Path(d) / "10-hanh-trinh.json"
    dk = doc_deck(d) or {}
    if not p.exists():
        return kq.sai("chưa có 10-hanh-trinh.json (bước 10b: cảm xúc và tải chú ý từng slide)")
    ht = doc_json(p)
    rows = ht.get("slides", [])
    ids = [s_["id"] for s_ in dk.get("slides", [])]
    if [r.get("id") for r in rows] != ids:
        kq.sai("10-hanh-trinh.json phải có đúng một dòng mỗi slide, cùng thứ tự với 10-deck.json")
    che_do = ht.get("che_do")
    if che_do not in ("trinh-bay", "doc"):
        kq.sai("che_do phải là 'trinh-bay' (có người nói) hoặc 'doc' (gửi đọc một mình)")
    for r in rows:
        if r.get("cam_xuc") not in CAM_XUC:
            kq.sai(f"{r.get('id')}: cam_xuc phải là một trong {', '.join(CAM_XUC)}")
        if not isinstance(r.get("tai"), int) or not 1 <= r["tai"] <= 5:
            kq.sai(f"{r.get('id')}: tai (tải chú ý) phải là số 1–5")
    if not rows:
        return
    theo_id = {s_["id"]: s_ for s_ in dk.get("slides", [])}
    for r in rows:
        s_ = theo_id.get(r.get("id"))
        if not s_:
            continue
        than = so_tu(chu_slide(s_)) - so_tu(s_.get("tieu_de", ""))
        if r.get("tai", 3) <= 2 and than > 60:
            kq.luu_y(f"{r['id']}: khai tải {r['tai']} nhưng slide có {than} chữ thân: tải thật cao hơn")
        if r.get("tai", 3) >= 4 and than < 15 and s_.get("kieu") not in ("bang", "bieu-do"):
            kq.luu_y(f"{r['id']}: khai tải {r['tai']} nhưng slide chỉ {than} chữ: có thể là slide nghỉ")
    if not any(r.get("moc") == "moc-cau" for r in rows[:2]):
        kq.sai("cần một câu móc (moc: 'moc-cau') ở 2 slide đầu")
    chuoi = 0
    for i, r in enumerate(rows):
        chuoi = chuoi + 1 if r.get("tai", 0) >= 4 else 0
        if chuoi > 2:
            kq.sai(f"{r.get('id')}: quá 2 slide nặng (tải ≥ 4) liền nhau: chèn một slide nghỉ (ảnh toàn trang, số lớn, một câu)")
    cach, buoc = 0, (4 if che_do == "trinh-bay" else 6)
    for r in rows:
        cach = 0 if r.get("moc") in ("moc-cau", "nghi", "dat-lai", "khoanh-khac") else cach + 1
        if cach > buoc:
            kq.sai(f"{r.get('id')}: {cach} slide liền không có điểm đặt lại chú ý (moc: nghi/dat-lai), tối đa {buoc}")
            cach = 0
    kieu_id = {s_.get("id"): s_.get("kieu") for s_ in dk.get("slides", [])}
    vi_cang = [i for i, r in enumerate(rows) if r.get("cam_xuc") in CANG and kieu_id.get(r.get("id")) not in ("bia", "chuong")]
    vi_nhe = [i for i, r in enumerate(rows) if r.get("cam_xuc") in NHE]
    if not vi_cang or not vi_nhe or min(vi_cang) > min(vi_nhe):
        kq.sai("cần cung căng → nhẹ: ít nhất một slide 'lo-lang'/'cang' trước slide 'nhe-nhom'/'tin-tuong' đầu tiên (vấn đề trước giải pháp)")
    n = len(rows)
    if not any(r.get("moc") == "khoanh-khac" and 0.45 * n <= i <= 0.85 * n for i, r in enumerate(rows)):
        kq.luu_y("nên có một khoảnh khắc đáng nhớ (moc: 'khoanh-khac') ở khoảng 50–80% deck")
    cuoi = rows[-1]
    sl_cuoi = (dk.get("slides") or [{}])[-1]
    if cuoi.get("cam_xuc") != "san-sang":
        kq.sai("slide cuối phải để người nghe 'san-sang' hành động")
    if sl_cuoi.get("kieu") == "ket" and not sl_cuoi.get("hanh_dong_chinh"):
        kq.sai("slide kết thiếu 'hanh_dong_chinh': một việc rõ nhất người nghe làm tiếp")
    elif sl_cuoi.get("kieu") == "ket" and gan_giong(sl_cuoi.get("tieu_de", ""), sl_cuoi.get("hanh_dong_chinh", "")):
        kq.luu_y("slide kết: 'hanh_dong_chinh' gần trùng tiêu đề, renderer chỉ in một lần; tiêu đề nên là lý do, hành động là việc cụ thể")
    if che_do == "doc":
        for s_ in dk.get("slides", []):
            if s_.get("kieu") not in KIEU_KHONG_NOI_DUNG and so_tu(s_.get("tieu_de", "")) < 8:
                kq.sai(f"{s_['id']}: deck gửi đọc cần tiêu đề tự giải thích (≥ 8 chữ)")
    else:
        for s_ in dk.get("slides", []):
            if s_.get("kieu") not in KIEU_KHONG_NOI_DUNG and so_tu(s_.get("ghi_chu", "")) < 40:
                kq.luu_y(f"{s_['id']}: deck trình bày cần ghi chú người nói đủ ý (≥ 40 chữ), slide để thưa")
        tong10 = sum(so_tu(chu_slide(s_)) - so_tu(s_.get("tieu_de", "")) - so_tu(s_.get("phan", "")) for s_ in dk.get("slides", [])[:10])
        if tong10 > 400:
            kq.luu_y(f"10 slide đầu có {tong10} chữ thân: deck trình bày nên thưa hơn, đẩy chi tiết vào ghi chú người nói")
    kq.ok(f"hành trình chú ý {len(rows)} slide, chế độ {che_do}")


def ve_hanh_trinh(d):
    """Vẽ đường tải chú ý + cảm xúc thành 10-hanh-trinh.png (Pillow)."""
    p = Path(d) / "10-hanh-trinh.json"
    if not p.exists():
        raise SystemExit("chưa có 10-hanh-trinh.json")
    rows = doc_json(p).get("slides", [])
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        raise SystemExit("cần Pillow để vẽ đường chú ý")
    from PIL import ImageFont
    W, H, L, T = 1600, 640, 80, 70
    im = Image.new("RGB", (W, H), "#FFFFFF")
    v = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 16)
    except OSError:
        try:
            f = ImageFont.truetype("DejaVuSans.ttf", 16)
        except OSError:
            f = ImageFont.load_default()
    n = max(len(rows), 2)
    x = lambda i: L + i * (W - L - 60) / (n - 1)
    y = lambda t: T + (5 - t) * (H - T - 200) / 4
    v.text((20, 14), "tải chú ý (1 nhẹ – 5 nặng)", fill="#555555", font=f)
    for t in range(1, 6):
        v.text((30, y(t) - 9), str(t), fill="#888888", font=f)
    mau = {"to-mo": "#3B82C4", "lo-lang": "#C0392B", "cang": "#8E2A1F", "nhe-nhom": "#2E9E6B", "tin-tuong": "#1F7A4D",
           "hao-hung": "#D9822B", "san-sang": "#0E2A47"}
    pts = [(x(i), y(r.get("tai", 3))) for i, r in enumerate(rows)]
    v.line(pts, fill="#555555", width=3)
    for i, (r, (px, py)) in enumerate(zip(rows, pts)):
        rr = 11 if r.get("moc") in ("moc-cau", "khoanh-khac") else 8
        v.ellipse((px - rr, py - rr, px + rr, py + rr), fill=mau.get(r.get("cam_xuc"), "#999999"))
        if r.get("moc") and r.get("moc") != "khong":
            v.text((px - 24, py - 34), r["moc"], fill="#333333", font=f)
        v.text((px - 24, H - 150 + (i % 2) * 22), f"{i + 1}. {r.get('id') or ''}", fill="#333333", font=f)
    gx = L
    for k, c in mau.items():  # chú giải màu cảm xúc
        v.ellipse((gx, H - 42, gx + 16, H - 26), fill=c)
        v.text((gx + 22, H - 44), k, fill="#333333", font=f)
        gx += 30 + int(v.textlength(k, font=f)) + 24
    ra = Path(d) / "10-hanh-trinh.png"
    im.save(ra)
    print(f"Đã vẽ {ra}")
    return ra


def cong_10(d, kq):
    kiem_deck(d, kq)
    kiem_hanh_trinh(d, kq)
    kiem_bo_cuc_deck(d, kq)
    dy = trang_thai(d).get("duyet", {}).get("10") or {}
    # vân mới (tiêu đề + hành trình) hoặc vân cũ (chỉ tiêu đề, duyệt trước v0.3): khớp một trong hai là nội dung chưa đổi
    if dy.get("van_tieu_de") and dy["van_tieu_de"] not in (van_tieu_de(d), van_tieu_de_cu(d)):
        kq.sai("tiêu đề hoặc hành trình chú ý đã đổi sau khi Linh duyệt: hỏi lại (deck.py hoi <dir> 10) rồi duyệt lại")
    if not (Path(d) / "10-ghost-deck.md").exists():
        kq.sai("chưa in ghost deck (chạy: deck.py ghost <dir>)")


def anh_trong_deck(dk):
    out = []
    for s in dk.get("slides", []):
        a = s.get("anh")
        if isinstance(a, dict) and a.get("tep"):
            out.append((s["id"], a))
    return out


def kiem_logo(d, dk):
    """Logo là tệp gốc trong <dir>/logo/. Thiếu logo_ta, hoặc có khách mà thiếu logo_khach: lỗi."""
    loi = []
    for k in ("logo_ta", "logo_khach"):
        v = dk.get(k)
        if v and not (Path(d) / v).exists():
            loi.append(f"{k}: không thấy tệp {v} (đặt logo gốc vào <dir>/logo/)")
        if v and Path(v).suffix.lower() not in DUOI_ANH | {".svg"}:
            loi.append(f"{k}: {v} không phải png/jpg/webp/svg")
        if v and (Path(d) / v).exists() and Path(v).suffix.lower() in DUOI_ANH:
            kt = kich_thuoc_anh(Path(d) / v)
            if not kt or max(kt) < 120:
                loi.append(f"{k}: {v} hỏng hoặc quá nhỏ ({kt}): lấy lại bản gốc")
    if not dk.get("logo_ta"):
        loi.append("thiếu logo_ta (logo BU/LINHX gốc, lấy từ Design System hoặc thư mục brand của Linh)")
    if dk.get("khach") and not dk.get("logo_khach"):
        loi.append(f"deck cho khách '{dk['khach']}' nhưng thiếu logo_khach (logo chính thức của khách, chỉ dùng nội bộ cho proposal)")
    return loi


def cong_11(d, kq):
    dk = doc_deck(d)
    p = Path(d) / BUOC[11][1]
    if not p.exists():
        return kq.sai("chưa sinh gói ảnh (deck.py goi-anh <dir>)")
    pj = Path(d) / "11-goi-anh" / "prompts.json"
    if not pj.exists():
        return kq.sai("thiếu 11-goi-anh/prompts.json")
    pr = doc_json(pj)
    can = {a["tep"] for _, a in anh_trong_deck(dk or {})}
    co = {x["tep"] for x in pr.get("anh", [])}
    if can - co:
        kq.sai(f"ảnh trong deck chưa có prompt: {sorted(can - co)}")
    for x in pr.get("anh", []):
        if CAU_THAM_CHIEU not in x.get("prompt", ""):
            kq.sai(f"{x['tep']}: prompt thiếu câu tham chiếu cố định")
        if "11-goi-anh/anh/anh-neo.png" not in x.get("ref", []):
            kq.sai(f"{x['tep']}: danh sách ref thiếu ảnh neo")
    kq.ok(f"{len(co)} prompt ảnh, mỗi prompt có câu tham chiếu")


H_MUC = {
    "H1": "không có chữ, số, ký tự trong ảnh",
    "H2": "không có logo nào bị AI vẽ (logo ghép sau trong deck)",
    "H3": "không có người như chụp thật/bị AI quá (trừ khi đề bài cho phép)",
    "H4": "đúng phong cách ảnh neo: bảng màu, ánh sáng, chất liệu",
    "H5": "đúng tỉ lệ khung (máy đo)",
    "H6": "đủ độ phân giải, cạnh dài ≥ 1024 px (máy đo)",
    "H7": "không lộ nhận diện của khách/đối thủ khác, không giống công trình thật",
    "H8": "không lỗi hình: tay, mặt, vật thể méo, hoa văn vỡ",
    "H10": "ảnh nền hoà vào slide: 16:9 tràn mép, chủ thể ở một phần ba, phía chữ là vùng trống cùng tông nền, không khung/bệ/viền",
    "H9": "cùng một bộ: đặt cạnh ảnh neo và các ảnh khác (12-to-anh.png) thấy rõ cùng tay vẽ, cùng ánh sáng, cùng độ chi tiết",
}


def cong_12(d, kq):
    p = Path(d) / BUOC[12][1]
    if not p.exists():
        return kq.sai("chưa có 12-ra-anh.json (deck.py ra-anh <dir>)")
    ra = doc_json(p)
    dk = doc_deck(d) or {}
    can = {a["tep"] for _, a in anh_trong_deck(dk)}
    co = {x["tep"]: x for x in ra.get("anh", [])}
    if can - set(co):
        kq.sai(f"ảnh chưa rà: {sorted(can - set(co))}")
    nk = doc_json(Path(d) / NHAT_KY) if (Path(d) / NHAT_KY).exists() else {"anh": []}
    ref_cua = {}
    for r in nk.get("anh", []):
        ref_cua[r["tep"]] = r.get("ref", [])
    for t, x in co.items():
        if t not in ref_cua:
            kq.sai(f"{t}: không có trong nhật ký tạo ảnh (lưu ảnh bằng: deck.py nhan-anh … --ref …)")
        elif not ref_cua[t]:
            kq.sai(f"{t}: bản hiện tại tạo không có ảnh tham chiếu")
        elif t != "anh-neo.png" and not any(r.endswith("anh-neo.png") for r in ref_cua[t]):
            kq.sai(f"{t}: bản hiện tại không đính kèm ảnh neo")
        thieu = [h for h in H_MUC if x.get("kiem", {}).get(h) is None]
        if thieu:
            kq.sai(f"{t}: chưa chấm {thieu}")
        truot = [h for h in H_MUC if x.get("kiem", {}).get(h) is False]
        nang = [i for i in x.get("loi", []) if i.get("muc_do") == "nang"]
        if x.get("ket_luan") == "dat" and (truot or nang):
            kq.sai(f"{t}: ghi 'dat' nhưng còn trượt {truot} hoặc lỗi nặng {len(nang)} — không được tự cho qua")
        elif x.get("ket_luan") != "dat":
            kq.sai(f"{t}: kết luận '{x.get('ket_luan')}', cần làm lại theo 'sua' rồi rà lại")
    kq.ok(f"{len(co)} ảnh đã rà")


def cong_13(d, kq):
    p = Path(d) / BUOC[13][1]
    if not p.exists():
        return kq.sai("chưa xuất Claude deck (deck.py xuat <dir>)")
    dk = doc_json(p)
    so = len(list((Path(d) / "13-claude-deck/project/slides").glob("*.html")))
    if so != len(dk.get("order", [])):
        kq.sai(f"deck.json có {len(dk.get('order', []))} slide nhưng thư mục slides có {so} tệp")
    rong = []
    for f in (Path(d) / "13-claude-deck/project/slides").glob("*.html"):
        if re.search(r"<img(?![^>]*\ssrc=)[^>]*>", f.read_text(encoding="utf-8")):
            rong.append(f.stem)
    if rong:
        kq.sai(f"slide còn ô ảnh/logo chưa có ảnh: {rong} (tải lên asset, ghi vào anh-map, chạy lại xuat)")
    dkk = doc_deck(d) or {}
    for loi in kiem_logo(d, dkk):
        kq.sai(loi)
    bc = Path(d) / XEM_BAO_CAO
    if not bc.exists():
        kq.sai("chưa chụp kiểm slide: deck.py xem <dir>")
    else:
        x = doc_json(bc)
        if x.get("dau_van") != dau_van_slides(d):
            kq.sai("slide đã đổi sau lần chụp kiểm cuối: chạy lại deck.py xem <dir>")
        for l in x.get("loi", []):
            kq.sai(f"chuẩn slide: {l}")
    tt = trang_thai(d)
    if not tt.get("link_deck"):
        kq.sai("chưa ghi link deck: deck.py duyet <dir> 13 --link <url>")
    kq.ok(f"{so} slide Claude Slides")


def cong_14(d, kq):
    p = Path(d) / BUOC[14][1]
    if not p.exists():
        return kq.sai("chưa có 14-prototype/README.md")
    t = p.read_text(encoding="utf-8")
    if re.search(r"Loại:\s*bỏ qua", t, re.I):
        if not re.search(r"Lý do[^:\n]*:[ \t]*\S+", t):
            kq.sai("bỏ qua prototype thì phải ghi lý do")
        return kq.ok("bỏ qua prototype, có lý do")
    if not re.search(r"Kịch bản demo", t) or len(re.findall(r"^\d\.\s*\S", t, re.M)) < 3:
        kq.sai("cần kịch bản demo 3 bước")
    if not re.search(r"Đường dẫn / link:[ \t]*\S+", t):
        kq.sai("thiếu đường dẫn prototype")
    kq.ok("prototype có kịch bản demo")


def cong_15(d, kq):
    p = Path(d) / BUOC[15][1]
    if not p.exists():
        return kq.sai("chưa có 15-ban-giao/README.md")
    t = p.read_text(encoding="utf-8")
    for nhan in ("Link deck Claude Slides:", "PDF / PPTX:", "Câu hỏi phản biện", "Thư gửi khách:"):
        # nhãn có ':' thì giá trị nằm ngay sau; "Câu hỏi phản biện…:" thì bỏ qua phần chữ tới dấu ':' đầu tiên
        duoi = r"[ \t]*(\S.*)?$" if nhan.endswith(":") else r"[^\n:]*:[ \t]*(\S.*)?$"
        m = re.search(re.escape(nhan) + duoi, t, re.M)
        sau = t[m.end():m.end() + 3000] if m else ""
        if not m or not ((m.group(1) or "").strip() or re.search(r"^\s*(?:\d+\.|-|>)\s+\S", sau, re.M)):
            kq.sai(f"bàn giao thiếu '{nhan}'")
    so_hoi = len(re.findall(r"^\s*(?:\d+\.|-)\s+\S.*\?", t, re.M))  # mọi dòng danh sách có dấu '?' trong README
    if so_hoi < 5:
        kq.sai(f"câu hỏi phản biện mới có {so_hoi}, cần 5–10 câu (mỗi câu kèm câu trả lời ngắn)")
    if not re.search(r"NHÁP", t):
        kq.sai("thư gửi khách phải ghi rõ 'NHÁP, chưa gửi – chờ Linh': Claude không gửi gì cho khách")
    if not re.search(r"D\+1", t) or not re.search(r"D\+7", t):
        kq.sai("thiếu việc sau buổi D+1, D+7")
    dk = doc_deck(d)
    if dk:
        kq2 = KetQua(10)
        kiem_deck(d, kq2, ban_cuoi=True)
        for s in kq2.loi:
            kq.sai("deck: " + s)
    con = []
    for f in (BUOC[1][1], BUOC[15][1]):
        if (Path(d) / f).exists():
            con += re.findall(r"\[(?:CẦN LINH|Linh chốt)[^\]]*\]", (Path(d) / f).read_text(encoding="utf-8"))
    if con:
        kq.luu_y(f"{len(con)} chỗ chờ Linh trong 01/15 (ngoài slide): gom vào danh sách hỏi Linh trước buổi")
    dk2 = doc_deck(d) or {}
    for k in ("logo_ta", "logo_khach"):
        f = Path(d) / dk2[k] if dk2.get(k) else None
        kt = kich_thuoc_anh(f) if f and f.exists() and f.suffix.lower() in DUOI_ANH else None
        if kt and max(kt) < 400:
            kq.luu_y(f"{k} chỉ {kt[0]}×{kt[1]} px: xin bản gốc lớn hơn trước khi gửi")
    kq.ok("đủ mục bàn giao")


CONG = {i: globals()[f"cong_{i}"] for i in range(1, 16)}


def chay_cong(d, n, im_lang=False, chi_noi_dung=False):
    kq = KetQua(n)
    CONG[n](d, kq)
    tt0 = trang_thai(d)
    if str(n) in (tt0.get("bo_qua") or {}):
        kq.loi = []
        kq.ok(f"bỏ qua bước này: {tt0['bo_qua'][str(n)].get('ly_do')}")
    elif not chi_noi_dung and [b for b in sorted(CAN_DUYET) if b < n and n not in (8, 11, 12) and b != 8
                                and not tt0.get("duyet", {}).get(str(b)) and str(b) not in (tt0.get("bo_qua") or {})]:
        thieu = [b for b in sorted(CAN_DUYET) if b < n and b != 8 and not tt0.get("duyet", {}).get(str(b))
                 and str(b) not in (tt0.get("bo_qua") or {})]
        kq.sai(f"bước {', '.join(map(str, thieu))} chưa được duyệt: bước {n} đứng trên nội dung chưa duyệt")
    elif not chi_noi_dung and n in CAN_DUYET and not tt0.get("duyet", {}).get(str(n)):
        if not kq.loi:
            kq.cho_duyet = True
        kq.sai("chưa có Linh duyệt bước này: hỏi Linh (deck.py hoi <dir> %d --cau \"…\"), rồi deck.py duyet <dir> %d" % (n, n))
    if not im_lang:
        kq.in_ra()
    tt = trang_thai(d)
    tt.setdefault("cong", {})[str(n)] = {"dat": kq.dat, "luc": bay_gio(), "loi": kq.loi, "canh_bao": kq.canh_bao}
    luu_trang_thai(d, tt)
    return kq


# ---------------------------------------------------------------- ghost deck

def lenh_ghost(d):
    dk = doc_deck(d)
    if not dk:
        raise SystemExit("chưa có 10-deck.json")
    dong = [f"# Ghost deck: {dk.get('ten', '')}", "",
            "Đọc liền các tiêu đề dưới đây: phải ra một lập luận trọn vẹn. Tiêu đề nào đọc lên không nối được thì sửa trước khi dựng slide.", ""]
    n = 0
    for s in dk.get("slides", []):
        if s.get("kieu") == "chuong":
            if not s.get("so"):
                print(f"! slide chương '{s.get('id')}' thiếu 'so' (01, 02…)")
            dong += ["", f"## {s.get('so', '')} {s.get('tieu_de', '')}".replace("##  ", "## "), ""]
            continue
        n += 1
        dong.append(f"{n}. {s.get('tieu_de', '')}  _(`{s.get('kieu')}`, {s.get('id')})_")
    dong += ["", "## Đọc liền", "", " ".join(s.get("tieu_de", "").rstrip(".") + "." for s in dk.get("slides", [])
                                         if s.get("kieu") not in ("bia", "chuong", "muc-luc"))]
    (Path(d) / "10-ghost-deck.md").write_text("\n".join(dong) + "\n", encoding="utf-8")
    print("\n".join(dong))


# ---------------------------------------------------------------- gói ảnh ChatGPT Plus

CAU_THAM_CHIEU = "Match the attached anchor image's style exactly (palette, light, materials); do not copy its layout or objects."
KHOI_CAM = ("Strict rules: no text, letters, numbers, logos or watermarks anywhere in the image. "
            "Every object is complete and physically plausible: nothing pierces or intersects anything else. "
            "No real people, faces or hands unless asked. No brand marks of any real company. "
            "Leave clean negative space where the slide headline will sit.")


def thu_brand_lab012(brand):
    th = thuong_hieu(brand)
    if th.get("thu_brand") and Path(th["thu_brand"]).exists():
        return Path(th["thu_brand"])
    p = GOC.parents[2] / "LAB012-BRAND-STANDARD" / "brands" / brand
    return p if p.exists() else None


def khoi_anh_brand(brand):
    """Luật ảnh cố định của brand trong Design System (LAB012 prompt-kit/image.md, mục 'Khối cố định'): lấy Palette, Mood, Avoid.
    Phong cách (Style) lấy từ thẻ phong cách của deck/brand neo, không lấy từ kit (kit có thể là ảnh chụp người)."""
    t = thu_brand_lab012(brand)
    f = t / "prompt-kit" / "image.md" if t else None
    if not f or not f.exists():
        return {}
    m = re.search(r"Khối cố định.*?```\s*(.*?)```", f.read_text(encoding="utf-8"), re.S)
    if not m:
        return {}
    out = {}
    for dong in m.group(1).splitlines():
        k, _, v = dong.partition(":")
        if k.strip() in ("Palette", "Mood", "Avoid", "Composition") and v.strip():
            # dòng Mood của kit hay dính "Setting: … people" (ảnh chụp người): bỏ, deck chỉ dùng poster không người
            out[k.strip()] = re.split(r"\s+Setting\s*:", v.strip())[0].strip()
    out["_tep"] = str(f)
    return out


def lenh_goi_anh(d):
    dk = doc_deck(d)
    if not dk:
        raise SystemExit("chưa có 10-deck.json")
    th = thuong_hieu(dk.get("brand", "linhx"))
    p8 = Path(d) / BUOC[8][1]
    tp = doc_json(p8) if p8.exists() else {}
    mau = ", ".join(tp.get("bang_mau") or [v for k, v in th["mau"].items() if k in ("toi", "tieu_de", "nhan", "sang")])
    huong = next((h for h in tp.get("huong", []) if h.get("id") == tp.get("huong_chon")), {})
    ra = Path(d) / "11-goi-anh"
    (ra / "anh").mkdir(parents=True, exist_ok=True)
    co_neo = (ra / "anh" / "anh-neo.png").exists()
    if not co_neo and (thu_neo(dk.get("brand", "linhx")) / "anh-neo.png").exists():
        raise SystemExit(f"brand {dk.get('brand')} đã có ảnh neo chung: chạy deck.py neo <dir> --lay để mọi deck của brand cùng một phong cách "
                         "(chỉ tạo neo mới khi Linh yêu cầu đổi phong cách)")
    ds = anh_trong_deck(dk)
    ht_deck = doc_hanh_trinh(d)
    kit = khoi_anh_brand(dk.get("brand", "linhx"))
    luat_kit = (f"Brand rules from the brand kit: mood {kit['Mood']} " if kit.get("Mood") else "") + \
               (f"Avoid: {kit['Avoid']} " if kit.get("Avoid") else "")
    mo_dau = (f"Use the attached images ONLY as a style reference. Do NOT copy their layout, objects or any text. "
              f"Brand mood: {th.get('anh_en') or th.get('anh', '')} {luat_kit}"
              f"Palette (hex): {mau}. "
              f"Composition: {tp.get('bo_cuc', 'calm, one clear focal object, generous negative space')}. "
              f"Illustration style: {tp.get('anh_minh_hoa', 'conceptual poster, cinematic soft light')}. "
              f"{KHOI_CAM} I will ask for several images one by one; keep every image in this exact style.")
    mb = [m for m in (huong.get("anh") or [])][:2] or [x.get("tep") for x in tp.get("nguon_anh", [])][:2]
    ref_neo = ["11-goi-anh/anh/anh-neo.png"] + mb
    prompts = []
    for sid, a in ds:
        ti_le = a.get("ti_le", "16:9")
        cx = (ht_deck.get(sid) or {}).get("cam_xuc")
        anh_sang = {"lo-lang": "cooler, dimmer light, more shadow", "cang": "cool low-key light, tension",
                    "to-mo": "soft intriguing light", "nhe-nhom": "warmer, brighter, open light", "tin-tuong": "warm steady light",
                    "hao-hung": "warm glowing light, slight upward energy", "san-sang": "clear warm light"}.get(cx, "")
        if ti_le == "16:9":
            # ảnh nền (background plate): bối cảnh → chủ thể → chi tiết → ràng buộc; nói rõ chủ thể ở đâu và vùng trống trông thế nào
            pr = (f"Full-bleed 16:9 background plate for slide '{sid}'. Setting: the brand's atmosphere, depth and soft light filling the whole frame. "
                  f"Subject: {a.get('y_tuong', '').strip()} The subject sits in the right third of the frame. "
                  f"The left two thirds stay calm, empty and smoothly toned in the background colour, so slide text can sit there and the slide background melts into the image. "
                  + (f"Light and mood: {anh_sang}. " if anh_sang else "")
                  + f"No frame, no plinth, no border, no rounded box, nothing cut off at the edges. {CAU_THAM_CHIEU} {KHOI_CAM} Aspect ratio 16:9.")
        else:
            pr = (f"Image for slide '{sid}': {a.get('y_tuong', '').strip()} Aspect ratio {ti_le}. "
                  + (f"Light and mood: {anh_sang}. " if anh_sang else "") + f"{CAU_THAM_CHIEU} {KHOI_CAM}")
        prompts.append({"tep": a["tep"], "slide": sid, "ti_le": ti_le, "prompt": pr, "ref": ref_neo})
    dong = [f"# Gói ảnh ChatGPT Plus: {dk.get('ten', '')}", "",
            f"Brand: **{th['ten']}**. Hướng phong cách: **{huong.get('ten', '(chưa chọn)')}**.", "",
            "## Cách chạy (mặc định: Claude điều khiển Chrome, ChatGPT Plus đã đăng nhập)",
            "1. Claude mở tab mới `chatgpt.com`, **một chat mới** cho cả bộ ảnh. Không đụng chat cũ, không đổi cài đặt.",
            "2. Mỗi lượt tạo ảnh **đính kèm đúng các tệp ở cột Ref** (ảnh neo + ảnh moodboard của hướng đã chọn), dán prompt, chờ ảnh xong.",
            "3. Bấm tải ảnh về, rồi chạy `deck.py nhan-anh <dir> --tu <Downloads> --vao anh --ten <tệp> --ref <ref>` để lưu đúng tên, giữ bản cũ, ghi nhật ký.",
            "4. **Không** đính kèm logo để AI vẽ lại. Logo, ảnh sản phẩm, ảnh chụp màn hình thật ghép trong deck.",
            "5. Dự phòng khi Chrome không dùng được: Linh tự làm đúng các bước trên, lưu ảnh vào Downloads, Claude chạy `nhan-anh`.", "",
            "### Câu mở đầu", "```", mo_dau, "```", ""]
    if not co_neo:
        dong += ["## Bước 0: ảnh neo phong cách (làm trước, Linh duyệt rồi mới làm tiếp)",
                 "```",
                 f"Create one style-anchor image for this deck: a calm conceptual poster that shows the whole visual language "
                 f"(palette, light, materials, one hero object). Aspect ratio 16:9. {KHOI_CAM}",
                 "```", "Ref: " + (", ".join(f"`{m}`" for m in mb) or "2–3 ảnh moodboard của hướng đã chọn") + ".",
                 "Lưu thành `11-goi-anh/anh/anh-neo.png` (`nhan-anh … --ten anh-neo.png --ref …`). Linh duyệt ảnh neo rồi mới làm tiếp; mọi ảnh sau đính kèm ảnh này.", ""]
    dong += ["## Từng ảnh", ""]
    for i, x in enumerate(prompts, 1):
        dong += [f"### {i}. `{x['tep']}` (slide `{x['slide']}`, {x['ti_le']})", "Ref: " + ", ".join(f"`{r}`" for r in x["ref"]),
                 "```", x["prompt"], "```", ""]
    dong += ["## Câu sửa nhanh",
             "- Có chữ trong ảnh: `Remove all text, keep everything else.`",
             "- Lệch màu: `Keep everything, but match the color palette of the anchor image exactly.`",
             "- Có người như ảnh chụp: `Remove all people; keep the scene and the style.`", "",
             "## Bảng tên tệp", "", "| Tệp | Slide | Tỉ lệ |", "|---|---|---|"]
    dong += [f"| {x['tep']} | {x['slide']} | {x['ti_le']} |" for x in prompts]
    (ra / "PROMPT-ANH.md").write_text("\n".join(dong) + "\n", encoding="utf-8")
    if kit:
        print(f"Đã gộp luật ảnh của brand từ {kit['_tep']} (Mood, Avoid)")
    ghi_json(ra / "prompts.json", {"brand": dk.get("brand"), "mo_dau": mo_dau, "luat_kit": kit, "ref_neo": mb, "anh": prompts, "luc": bay_gio()})
    print(f"Đã ghi {ra / 'PROMPT-ANH.md'} ({len(prompts)} ảnh{'' if co_neo else ' + ảnh neo'})")


# ---------------------------------------------------------------- rà ảnh

def kich_thuoc_anh(p):
    b = Path(p).read_bytes()
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", b[16:24])
    if b[:2] == b"\xff\xd8":
        i = 2
        while i < len(b):
            if b[i] != 0xFF:
                i += 1
                continue
            m = b[i + 1]
            if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                h, w = struct.unpack(">HH", b[i + 5:i + 9])
                return w, h
            i += 2 + struct.unpack(">H", b[i + 2:i + 4])[0]
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        if b[12:16] == b"VP8X":
            return 1 + int.from_bytes(b[24:27], "little"), 1 + int.from_bytes(b[27:30], "little")
        if b[12:16] == b"VP8 ":
            w, h = struct.unpack("<HH", b[26:30])
            return w & 0x3FFF, h & 0x3FFF
    return None


def lenh_ra_anh(d):
    dk = doc_deck(d)
    if not dk:
        raise SystemExit("chưa có 10-deck.json")
    p = Path(d) / BUOC[12][1]
    cu = {x["tep"]: x for x in doc_json(p).get("anh", [])} if p.exists() else {}
    out = []
    for sid, a in anh_trong_deck(dk):
        tep = Path(d) / "11-goi-anh" / "anh" / a["tep"]
        x = cu.get(a["tep"], {"tep": a["tep"], "slide": sid, "kiem": {h: None for h in H_MUC}, "loi": [], "ket_luan": None})
        x["slide"] = sid
        if not tep.exists():
            x["co_tep"] = False
            x["ket_luan"] = "thieu"
            print(f"✗ {a['tep']}: chưa có tệp")
        else:
            x["co_tep"] = True
            ma = hashlib.sha1(tep.read_bytes()).hexdigest()[:12]
            if x.get("sha1") and x["sha1"] != ma:  # ảnh đã đổi (bản sửa): chấm lại từ đầu, giữ lịch sử
                x.setdefault("lich_su", []).append({"sha1": x["sha1"], "ket_luan": x.get("ket_luan"), "loi": x.get("loi", [])})
                x["kiem"] = {h: None for h in H_MUC}
                x["loi"], x["ket_luan"] = [], None
                print(f"↻ {a['tep']}: bản mới (vòng {len(x['lich_su']) + 1}), chấm lại")
            x["sha1"] = ma
            kt = kich_thuoc_anh(tep)
            x["kich_thuoc"] = list(kt) if kt else None
            x["dung_luong_mb"] = round(tep.stat().st_size / 1e6, 2)
            if kt:
                w, h = kt
                mt = a.get("ti_le", "16:9")
                tw, th_ = (float(v) for v in mt.split(":"))
                x["kiem"]["H5"] = abs(w / h - tw / th_) / (tw / th_) <= 0.03
                x["kiem"]["H6"] = max(w, h) >= 1024
            if x["dung_luong_mb"] > 14:
                x.setdefault("loi", []).append({"muc": "H6", "muc_do": "nang", "mo_ta": "quá 14 MB, không tải lên được", "sua": "nén lại"})
            print(f"{'✓' if x['kiem'].get('H5') and x['kiem'].get('H6') else '!'} {a['tep']}: {kt} {x['dung_luong_mb']} MB, "
                  f"tỉ lệ {'đúng' if x['kiem'].get('H5') else 'SAI'}, độ phân giải {'đủ' if x['kiem'].get('H6') else 'THIẾU'}")
        out.append(x)
    co = [Path(d) / "11-goi-anh" / "anh" / "anh-neo.png"] + [Path(d) / "11-goi-anh" / "anh" / x["tep"] for x in out if x.get("co_tep")]
    co = [c for c in co if c.exists()]
    if len(co) > 1:
        to_hinh(co, Path(d) / "12-to-anh.png", cot=min(4, len(co)), w=360, h=480)
    ghi_json(p, {"huong_dan": {h: m for h, m in H_MUC.items()},
                 "to_anh": "12-to-anh.png (ảnh neo + cả bộ, để chấm H4, H9)",
                 "cach_cham": "Claude mở từng ảnh và tờ 12-to-anh.png, điền kiem.H1–H9 true/false, loi[{muc, muc_do: nang|nhe, mo_ta, sua}], ket_luan: dat|sua|loai. Không được ghi 'dat' khi còn false hoặc lỗi nặng.",
                 "anh": out})
    print(f"Đã ghi {p}. Claude chấm H1–H4, H7–H9 bằng mắt (mở cả 12-to-anh.png) rồi chạy: deck.py cong <dir> 12")


# ---------------------------------------------------------------- Chrome: tải moodboard, nhận ảnh, vòng sửa

NHAT_KY = "11-goi-anh/nhat-ky.json"
DUOI_ANH = {".png", ".jpg", ".jpeg", ".webp"}
TOI_DA_MOODBOARD = 12
SO_VONG_SUA = 3


def duoi_that(b):
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if b[:2] == b"\xff\xd8":
        return ".jpg"
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        return ".webp"
    return None


def ghi_nguon_moodboard(d, muc):
    p = Path(d) / "08-moodboard" / "nguon.json"
    cu = doc_json(p) if p.exists() else {"ghi_chu": "Ảnh moodboard chỉ để tham chiếu nội bộ, không đưa lên deck gửi khách.", "anh": []}
    cu["anh"] = [x for x in cu["anh"] if x["tep"] != muc["tep"]] + [muc]
    ghi_json(p, cu)


def lenh_tai_anh(d, ds):
    """Tải ảnh moodboard Claude đã chọn khi duyệt Pinterest/Dribbble bằng Chrome. ds: [{anh_url, trang, tieu_de, ly_do}]."""
    muc = doc_json(ds)
    muc = muc.get("anh", muc) if isinstance(muc, dict) else muc
    thu = Path(d) / "08-moodboard"
    thu.mkdir(parents=True, exist_ok=True)
    da_co = sorted(thu.glob("mb-*"))
    if len(da_co) + len(muc) > TOI_DA_MOODBOARD:
        raise SystemExit(f"moodboard tối đa {TOI_DA_MOODBOARD} ảnh (đã có {len(da_co)}, muốn thêm {len(muc)}). Chọn lọc lại.")
    n, dat = len(da_co), 0
    for m in muc:
        url = m.get("anh_url", "")
        if not url.startswith("https://"):
            print(f"✗ bỏ qua (không phải https): {url}")
            continue
        # Pinterest: lưới tìm kiếm hay trả bản thu nhỏ (236x/474x/736x); thử bản gốc trước
        cac_url = [re.sub(r"i\.pinimg\.com/\d+x/", "i.pinimg.com/originals/", url), url] if re.search(r"i\.pinimg\.com/\d+x/", url) else [url]
        b = None
        for u in cac_url:
            rq = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130 Safari/537.36",
                                                    "Referer": m.get("trang") or u})
            try:
                with urllib.request.urlopen(rq, timeout=30) as r:
                    b = r.read(15_000_000)
                url = u
                break
            except Exception as loi:
                cuoi = loi
        if b is None:
            print(f"✗ không tải được {url}: {cuoi}. Dự phòng: tải trong Chrome rồi chạy nhan-anh --vao moodboard")
            continue
        duoi = duoi_that(b)
        if not duoi:
            print(f"✗ {url}: không phải ảnh png/jpg/webp")
            continue
        n += 1
        tep = thu / f"mb-{n:02d}{duoi}"
        tep.write_bytes(b)
        kt = kich_thuoc_anh(tep)
        if kt and min(kt) < 300:
            print(f"! {tep.name}: ảnh nhỏ {kt}, nên tìm bản lớn hơn")
        ghi_nguon_moodboard(d, {"tep": f"08-moodboard/{tep.name}", "nguon": m.get("trang") or url, "anh_url": url,
                                "tieu_de": m.get("tieu_de", ""), "ly_do": m.get("ly_do", ""), "kich_thuoc": list(kt) if kt else None,
                                "luc": bay_gio(), "ghi_chu": "chỉ tham chiếu nội bộ"})
        dat += 1
        print(f"✓ {tep.name} ← {m.get('trang') or url}")
        time.sleep(1.5)  # đi chậm như người, không dồn dập
    print(f"Đã tải {dat}/{len(muc)} ảnh vào {thu}. Nguồn ghi ở 08-moodboard/nguon.json")


def anh_moi_nhat(tu, phut):
    moc = time.time() - phut * 60
    ds = [f for f in Path(tu).expanduser().iterdir()
          if f.is_file() and f.suffix.lower() in DUOI_ANH and f.stat().st_mtime >= moc]
    return max(ds, key=lambda f: f.stat().st_mtime) if ds else None


def lenh_nhan_anh(d, tu, vao, ten, ref, nguon, phut):
    f = anh_moi_nhat(tu, phut)
    if not f:
        raise SystemExit(f"không thấy ảnh png/jpg/webp nào tải về trong {phut} phút qua ở {tu}")
    b = f.read_bytes()
    duoi = duoi_that(b)
    if not duoi:
        raise SystemExit(f"{f.name} không phải ảnh png/jpg/webp")
    refs = [r.strip().replace("\\", "/") for r in (ref or "").split(",") if r.strip()]
    if vao == "moodboard":
        thu = Path(d) / "08-moodboard"
        thu.mkdir(parents=True, exist_ok=True)
        if len(list(thu.glob("mb-*"))) >= TOI_DA_MOODBOARD:
            raise SystemExit(f"moodboard đã đủ {TOI_DA_MOODBOARD} ảnh")
        tep = thu / (ten or f"mb-{len(list(thu.glob('mb-*'))) + 1:02d}{duoi}")
        shutil.move(str(f), tep)
        ghi_nguon_moodboard(d, {"tep": f"08-moodboard/{tep.name}", "nguon": nguon or "[CẦN LINH: link nguồn]",
                                "luc": bay_gio(), "ghi_chu": "chỉ tham chiếu nội bộ"})
        print(f"✓ {f.name} → 08-moodboard/{tep.name}")
        return
    if not ten:
        raise SystemExit("--vao anh cần --ten <tên tệp trong 10-deck.json, hoặc anh-neo.png>")
    if not refs:
        raise SystemExit("ảnh deck phải có ảnh tham chiếu: thêm --ref <tệp ref đã đính kèm khi tạo>, cách nhau bằng dấu phẩy")
    thieu = [r for r in refs if not (Path(d) / r).exists()]
    if thieu:
        raise SystemExit(f"không thấy tệp ref: {thieu}")
    if ten != "anh-neo.png" and not any(r.endswith("anh-neo.png") for r in refs):
        raise SystemExit("ảnh deck phải đính kèm ảnh neo (11-goi-anh/anh/anh-neo.png) trong --ref")
    thu = Path(d) / "11-goi-anh" / "anh"
    thu.mkdir(parents=True, exist_ok=True)
    tep = thu / ten
    if Path(ten).suffix.lower() != duoi and not (duoi == ".jpg" and Path(ten).suffix.lower() == ".jpeg"):
        tep = thu / (Path(ten).stem + duoi)
        print(f"! ảnh tải về là {duoi}, lưu thành {tep.name}: sửa 'anh.tep' trong 10-deck.json cho khớp")
    pk = Path(d) / NHAT_KY
    nk = doc_json(pk) if pk.exists() else {"anh": [], "lich_su": []}
    cu = next((x for x in nk["anh"] if x["tep"] == tep.name), None)
    pb = (cu or {}).get("phien_ban", 0) + 1
    if tep.exists():
        (thu / "cu").mkdir(exist_ok=True)
        shutil.move(str(tep), thu / "cu" / f"{tep.stem}-v{pb - 1}{tep.suffix}")
    shutil.move(str(f), tep)
    dong = {"tep": tep.name, "phien_ban": pb, "ref": refs, "nguon": nguon or "chatgpt-plus", "luc": bay_gio(),
            "sha1": hashlib.sha1(b).hexdigest()[:12]}
    nk["anh"] = [x for x in nk["anh"] if x["tep"] != tep.name] + [dong]
    nk["lich_su"].append(dong)
    ghi_json(pk, nk)
    print(f"✓ {f.name} → 11-goi-anh/anh/{tep.name} (bản {pb}, ref: {', '.join(refs)})")


def lenh_sua_anh(d):
    p = Path(d) / BUOC[12][1]
    if not p.exists():
        raise SystemExit("chưa có 12-ra-anh.json: chạy ra-anh và chấm trước")
    ra = doc_json(p)
    pr = {x["tep"]: x for x in doc_json(Path(d) / "11-goi-anh/prompts.json").get("anh", [])} \
        if (Path(d) / "11-goi-anh/prompts.json").exists() else {}
    nk = doc_json(Path(d) / NHAT_KY) if (Path(d) / NHAT_KY).exists() else {"anh": []}
    pb = {x["tep"]: x.get("phien_ban", 1) for x in nk.get("anh", [])}
    viec, can_linh = [], []
    for x in ra.get("anh", []):
        if x.get("ket_luan") not in ("sua", "loai"):
            continue
        tep = x["tep"]
        if pb.get(tep, 1) > SO_VONG_SUA:
            can_linh.append(tep)
            continue
        loi = [i for i in x.get("loi", []) if i.get("sua") or i.get("mo_ta")]
        if not loi:
            raise SystemExit(f"{tep}: kết luận '{x['ket_luan']}' nhưng chưa ghi lỗi nào (loi[].sua) để sửa")
        goc = pr.get(tep, {})
        if x["ket_luan"] == "sua":
            # sửa trên đúng ảnh cần sửa: đính kèm nó đầu tiên (trong chat dài, "ảnh trước" thường là ảnh khác)
            prompt = (f"Revision for slide '{x.get('slide', '')}'. Edit the FIRST attached image only; the second attachment is the style anchor. Fix: "
                      + "; ".join(i.get("sua") or i["mo_ta"] for i in loi) +
                      f". Keep everything else exactly the same (composition, palette, light). Aspect ratio {goc.get('ti_le', '16:9')}. "
                      + CAU_THAM_CHIEU + " " + KHOI_CAM)
        else:
            prompt = (goc.get("prompt", "") + " The previous attempt failed because: " +
                      "; ".join(i["mo_ta"] for i in loi if i.get("mo_ta")) + ". Avoid that completely.")
        ref = goc.get("ref") or ["11-goi-anh/anh/anh-neo.png"]
        viec.append({"tep": tep, "vong": pb.get(tep, 1) + 1, "kieu": x["ket_luan"],
                     "dinh_kem": ([f"11-goi-anh/anh/{tep}"] if x["ket_luan"] == "sua" else []) + ref, "ref": ref, "prompt": prompt})
    ghi_json(Path(d) / "11-goi-anh" / "sua.json", {"luc": bay_gio(), "viec": viec, "can_linh": can_linh})
    for v in viec:
        print(f"\n## {v['tep']} (vòng {v['vong']}, {v['kieu']}) · đính kèm theo thứ tự: {', '.join(v['dinh_kem'])}\n{v['prompt']}")
    if can_linh:
        print(f"\n! Đã sửa {SO_VONG_SUA} vòng vẫn chưa đạt, hỏi Linh: {can_linh}")
    print(f"\nĐã ghi 11-goi-anh/sua.json: {len(viec)} ảnh cần sửa. Sửa xong: nhan-anh → ra-anh → chấm lại → cong 12")


# ---------------------------------------------------------------- xuất Claude Slides

def e(s):
    """Thoát ký tự cho chữ trên slide, giữ <b> <i> <br>."""
    s = html.escape(str(s or ""), quote=False)
    return re.sub(r"&lt;(/?)(b|i|br)\s*/?&gt;", r"<\1\2>", s)


class Ve:
    def __init__(self, th, dk, anh_map, logo):
        self.m, self.f, self.dk, self.anh_map = th["mau"], th["font"], dk, anh_map
        # logo là tệp gốc trong <dir>/logo/ (logo_ta: BU/LINHX, logo_khach: khách), tải lên như ảnh (anh-map)
        ta, kh = dk.get("logo_ta"), dk.get("logo_khach")
        self.lg_minh = (ta, anh_map.get(ta) or logo) if (ta or logo) else None
        self.lg_khach = (kh, anh_map.get(kh)) if kh else None
        self.ten_khach = dk.get("khach") or "khách"
        self.logo = self.lg_minh and self.lg_minh[1]
        self.ten_brand = th.get("ten_ngan") or th["ten"].split(" (")[0]
        self.nhan_ai = th.get("nhan_anh_ai")
        self.thu = None
        self.ht = None  # 10-hanh-trinh.json: cảm xúc từng slide (tông nền slide nghỉ)
        self.HF = f"'{self.f['tieu_de']}', Arial, sans-serif"
        self.BF = f"'{self.f['than']}', Arial, sans-serif"
        self.chan = dk.get("chan_trang") or f"{self.ten_brand} · {dk.get('ten', '')}"

    def img(self, a, w, h, r=16, fit="cover", toi=False):
        if not a:
            return ""
        src = self.anh_map.get(a.get("tep"))
        s = f' src="{src}"' if src else ""
        nhan = self.nhan_ai
        anh = (f'<img{s} alt="{e(a.get("mo_ta") or a.get("y_tuong", "")[:120])}" '
               f'style="width:{w}px;height:{(h - 40) if nhan else h}px;object-fit:{fit};border-radius:{r}px;background:{self.m["xen"]}">')
        if not nhan:
            return anh
        # brand bắt buộc ghi rõ ảnh AI (ví dụ TUVA): chú thích nhỏ ngay dưới ảnh
        mau = self.m["tren_toi_phu"] if toi else self.m["chu_phu"]
        return (f'<div style="display:flex;flex-direction:column;gap:12px;flex:none">{anh}'
                f'<p style="font-size:24px;line-height:1;color:{mau}">{e(nhan)}</p></div>')

    def logo_img(self, lg, ten, w, h, extra=""):
        """Logo luôn là tệp gốc (không để AI vẽ). Chưa có /_blob thì để <img> không src để cổng 13 bắt.
        Khung theo tỉ lệ thật của tệp (đo khi xuất), để logo vuông không bị thu nhỏ trong khung ngang."""
        f = Path(self.thu) / lg[0] if (self.thu and lg[0]) else None
        kt = kich_thuoc_anh(f) if f and f.exists() else None
        if kt and kt[1]:
            if kt[0] < kt[1] and h >= 56:  # logo dọc (TUVA, MSD): cho cao hơn trong thẻ để đọc được
                h = int(h * 1.6)
            w = int(min(max(h * kt[0] / kt[1], h * 0.6), h * 4.5))
            extra = extra.replace("height:", "height:")
        s = f' src="{lg[1]}"' if lg[1] else ""
        return (f'<img{s} alt="Logo {e(ten)}" style="{extra}width:{w}px;height:{h}px;object-fit:contain;'
                f'object-position:left">')

    def cum_logo(self, h=72):
        """Cụm logo trên nền tối: đặt trên thẻ sáng để logo màu nào cũng đọc được. Mình trước, khách sau."""
        o = []
        if self.lg_minh:
            o.append(self.logo_img(self.lg_minh, self.ten_brand, h * 3, h))
        if self.lg_khach:
            if o:
                o.append(f'<div style="width:2px;height:{h}px;background:{self.m["vien"]}"></div>')
            o.append(self.logo_img(self.lg_khach, self.ten_khach, h * 3, h))
        if not o:
            return ""
        return (f'<div style="display:flex;flex-direction:row;align-items:center;gap:32px;background:{self.m["sang"]};'
                f'border-radius:12px;padding:20px 32px;align-self:flex-start">{"".join(o)}</div>')

    def than(self, x):
        """Khối thân giãn giữa tiêu đề và chân trang để slide không dồn lên trên."""
        return f'<div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:28px">{x}</div>'

    def chan_trang(self, s, n, toi=False):
        mau = self.m["tren_toi_phu"] if toi else self.m["chu_phu"]
        ng = re.sub(r"^\s*Nguồn\s*:\s*", "", s.get("nguon") or "")
        nguon = f"Nguồn: {e(ng)} · " if ng else ""
        lg = ""
        if self.lg_minh and not toi:
            lg = self.logo_img(self.lg_minh, self.ten_brand, 160, 40,
                               "position:absolute;right:128px;bottom:58px;").replace("object-position:left", "object-position:right")
        return (f'<p style="position:absolute;left:128px;bottom:64px;width:{1440 if lg else 1664}px;font-size:24px;color:{mau}">'
                f'{nguon}{e(self.chan)} · {n}</p>{lg}')

    def dau(self, s):
        k = (f'<p style="font-size:24px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:{self.m["tieu_de"]}">'
             f'{e(s["phan"])}</p>') if s.get("phan") else ""
        return (f'<div style="display:flex;flex-direction:column;gap:12px">{k}'
                f'<h2 style="font-family:{self.HF};font-size:56px;font-weight:700;line-height:1.15;color:{self.m["tieu_de"]}">'
                f'{e(s.get("tieu_de"))}</h2></div>')

    def khung(self, s, n, inner, nen=None, toi=False, bo_cuc="display:flex;flex-direction:column;gap:40px", chan=True, extra=""):
        nen = nen or self.m["sang"]
        mau = self.m["tren_toi"] if toi else self.m["chu"]
        ghi = html.escape((s.get("ghi_chu") or "")[:3990], quote=False)
        ct = self.chan_trang(s, n, toi) if chan else ""
        return (f'<section id="{s["id"]}"{extra} style="background:{nen};color:{mau};font-family:{self.BF};'
                f'padding:112px 128px 160px;{bo_cuc}">\n{inner}\n{ct}\n<aside>{ghi}</aside>\n</section>\n')

    # ---- tiện ích bố cục v0.3: ảnh nền hoà vào slide, một tiêu điểm
    @staticmethod
    def H(hero):
        return ' data-hero="1"' if hero else ""

    @staticmethod
    def T(co):
        return ' data-transition="fade"' if co else ""

    def rgba(self, hexs, a):
        h = hexs.lstrip("#")
        return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{a})"

    def mau_vung_trong(self, a, ben="trai"):
        """Màu trung bình vùng trống của ảnh nền (phía chữ) để nền slide và lớp phủ tan vào ảnh. Cần Pillow + tệp cục bộ."""
        f = None
        if self.thu and a and a.get("tep"):
            for p in (Path(self.thu) / "11-goi-anh" / "anh" / a["tep"], Path(self.thu) / a["tep"]):
                if p.exists():
                    f = p
                    break
        if not f:
            return None
        try:
            from PIL import Image
        except ImportError:
            return None
        im = Image.open(f).convert("RGB")
        w, h = im.size
        vung = im.crop((0, 0, int(w * 0.3), h) if ben == "trai" else (int(w * 0.7), 0, w, h)).resize((24, 48))
        px = list(vung.getdata())
        r, g, b = (sorted(c[i] for c in px)[len(px) // 2] for i in range(3))
        return f"#{r:02X}{g:02X}{b:02X}"

    def bo_mau_nen(self, nen):
        """Chữ sáng trên nền tối, chữ đậm trên nền sáng (chọn theo độ sáng thật của nền)."""
        if lum(nen) < 0.25:
            cm = {"nen": nen, "chu": self.m["tren_toi"], "phu": self.m["tren_toi_phu"], "nhan": self.m["nhan_toi"], "toi": True}
        else:
            cm = {"nen": nen, "chu": self.m["tieu_de"], "phu": self.m["chu_phu"], "nhan": self.m["nhan"], "toi": False}
        if tuong_phan(cm["nhan"], nen) < 3:  # màu nhấn nhạt trên nền sáng (xanh lá, hổ phách): dùng màu chữ chính
            cm["nhan"] = cm["chu"]
        if tuong_phan(cm["phu"], nen) < 4.5:
            cm["phu"] = cm["chu"]
        return cm

    def anh_bia(self):
        for s in self.dk.get("slides", []):
            if s.get("kieu") == "bia" and s.get("anh"):
                return s["anh"]
        return None

    def nen_anh(self, a, cm, ben="trai"):
        """Bố cục 'toan-trang': ảnh tràn cả slide + lớp phủ chuyển sắc từ màu nền phía chữ. Không khung, không bo góc."""
        src = self.anh_map.get(a.get("tep")) if a else None
        s = f' src="{src}"' if src else ""
        n = cm["nen"]
        huong = "90deg" if ben == "trai" else "270deg"
        phu = (f'<div style="position:absolute;left:0;top:0;width:1920px;height:1080px;'
               f'background:linear-gradient({huong}, {self.rgba(n, 1)} 0%, {self.rgba(n, 0.94)} 30%, {self.rgba(n, 0.6)} 50%, {self.rgba(n, 0)} 72%)"></div>')
        nhan_ai = (f'<p style="position:absolute;right:48px;bottom:32px;width:480px;text-align:right;font-size:24px;color:{cm["phu"]}">{e(self.nhan_ai)}</p>'
                   if self.nhan_ai else "")
        return (f'<img{s} data-nen="1" alt="{e((a or {}).get("mo_ta") or "")}" style="position:absolute;left:0;top:0;width:1920px;height:1080px;object-fit:cover">'
                + phu + nhan_ai)

    @staticmethod
    def co_td(td, lon=84):
        n = len(td or "")
        return lon if n <= 34 else (int(lon * 0.84) if n <= 52 else int(lon * 0.72))

    def cot_chu(self, inner, rong=880):
        # position:relative: khối chữ vẽ đè lên ảnh nền (cả trên trình duyệt lẫn Claude Slides)
        return f'<div style="position:relative;width:{rong}px;display:flex;flex-direction:column;gap:32px">{inner}</div>'

    def diem(self, s, toi=False):
        """diem_chinh: điểm duy nhất slide phải để lại, đứng ngay dưới tiêu điểm."""
        if not s.get("diem_chinh"):
            return ""
        mau = self.m["tren_toi"] if toi else self.m["tieu_de"]
        return (f'<p data-diem="1" style="font-family:{self.HF};font-size:40px;font-weight:700;line-height:1.25;color:{mau}">'
                f'{e(s["diem_chinh"])}</p>')

    def tim(self, s, khoa, mac_dinh=None):
        v = s.get(khoa)
        return v if isinstance(v, int) else mac_dinh

    def khung_anh(self, s, n, a, inner, ben="trai", nen_du_phong=None, transition=True):
        cm = self.bo_mau_nen(self.mau_vung_trong(a, ben) or nen_du_phong or self.m["toi"]) if a else \
            self.bo_mau_nen(nen_du_phong or self.m["toi"])
        bg = self.nen_anh(a, cm, ben) if a else ""
        ghi = html.escape((s.get("ghi_chu") or "")[:3990], quote=False)
        noi = inner(cm)
        return (f'<section id="{s["id"]}"{self.T(transition)} style="background:{cm["nen"]};color:{cm["chu"]};'
                f'font-family:{self.BF};padding:128px;display:flex;flex-direction:column;justify-content:center;'
                f'align-items:{"flex-start" if ben == "trai" else "flex-end"};gap:40px">\n{bg}{noi}\n<aside>{ghi}</aside>\n</section>\n')

    # ---- kiểu slide
    def bia(self, s, n):
        def noi(cm):
            logo = self.cum_logo() or f'<p style="font-size:28px;font-weight:700;letter-spacing:4px;color:{cm["nhan"]}">{e(self.ten_brand.upper())}</p>'
            return self.cot_chu(
                logo
                + f'<h1 style="font-family:{self.HF};font-size:{self.co_td(s["tieu_de"])}px;font-weight:700;line-height:1.08;color:{cm["chu"]}">{e(s["tieu_de"])}</h1>'
                + (f'<p style="font-size:36px;line-height:1.35;color:{cm["phu"]}">{e(s.get("phu_de"))}</p>' if s.get("phu_de") else "")
                + f'<div style="width:120px;height:8px;background:{cm["nhan"]}"></div>'
                f'<p style="font-size:28px;line-height:1.5;color:{cm["chu"]}">{e(s.get("khach", ""))}<br>{e(s.get("ngay", ""))}</p>')
        return self.khung_anh(s, n, s.get("anh"), noi)

    def tom_tat(self, s, n):
        hang = "".join(
            f'<div style="display:flex;flex-direction:row;gap:28px;align-items:flex-start;padding:22px 0;border-top:2px solid {self.m["vien"]}">'
            f'<p style="font-family:{self.HF};font-size:36px;font-weight:700;color:{self.m["chu_phu"]};width:56px;flex:none">{i}</p>'
            f'<p style="flex:1;font-size:30px;line-height:1.4;color:{self.m["chu_phu"]}">{e(x)}</p></div>'
            for i, x in enumerate(s.get("diem", []), 1))
        chinh = s.get("diem_chinh") or s.get("ket_luan")
        kl = (f'<div data-hero="1" style="background:{self.m["toi"]};border-radius:12px;padding:32px 40px;border-left:12px solid {self.m["nhan_toi"]}">'
              f'<p style="font-family:{self.HF};font-size:40px;font-weight:700;line-height:1.3;color:{self.m["tren_toi"]}">{e(chinh)}</p></div>') if chinh else ""
        return self.khung(s, n, self.dau(s) + self.than(kl + f'<div style="display:flex;flex-direction:column">{hang}</div>'))

    def muc_luc(self, s, n):
        hang = "".join(
            f'<div style="display:flex;flex-direction:row;gap:32px;align-items:baseline;padding:20px 0;border-bottom:2px solid {self.m["vien"]}">'
            f'<p style="font-family:{self.HF};font-size:44px;font-weight:700;color:{self.m["tieu_de"]};width:96px">{i:02d}</p>'
            f'<p style="font-size:36px">{e(x)}</p></div>' for i, x in enumerate(s.get("muc", []), 1))
        return self.khung(s, n, self.dau(s) + f'<div style="display:flex;flex-direction:column">{hang}</div>')

    def chuong(self, s, n):
        def noi(cm):
            return self.cot_chu(
                f'<p data-hero="1" style="font-family:{self.HF};font-size:180px;font-weight:700;line-height:1;color:{cm["nhan"]}">{e(s.get("so", ""))}</p>'
                f'<h1 style="font-family:{self.HF};font-size:{self.co_td(s["tieu_de"], 80)}px;font-weight:700;line-height:1.1;color:{cm["chu"]}">{e(s["tieu_de"])}</h1>'
                + (f'<p style="font-size:34px;line-height:1.4;color:{cm["phu"]}">{e(s.get("phu_de"))}</p>' if s.get("phu_de") else ""))
        return self.khung_anh(s, n, s.get("anh"), noi)

    def khang_dinh(self, s, n):
        ht = (self.ht or {}).get(s["id"], {})
        cang = ht.get("cam_xuc") in ("lo-lang", "cang", "to-mo")
        a = s.get("anh")
        if not a:
            # slide nghỉ 'nen-mem': chuyển sắc mềm màu brand; căng thì tối, nhẹ nhõm thì sáng
            nen = self.m["toi"] if cang or not ht else self.m["sang"]
            cm = self.bo_mau_nen(nen)
            bg = (f'<div style="position:absolute;left:0;top:0;width:1920px;height:1080px;'
                  f'background:radial-gradient(ellipse at 82% 22%, {self.rgba(self.m["nhan"], 0.38 if cm["toi"] else 0.22)} 0%, {self.rgba(nen, 0)} 62%)"></div>')
            inner = (bg + '<div style="position:relative;display:flex;flex-direction:column;gap:40px">' + ((f'<p style="font-size:24px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:{cm["phu"]}">{e(s["phan"])}</p>' if s.get("phan") else "")
                     + f'<h2 data-hero="1" style="font-family:{self.HF};font-size:{self.co_td(s["tieu_de"], 80) if len(s["tieu_de"]) > 60 else 80}px;font-weight:700;line-height:1.15;width:1400px;color:{cm["chu"]}">{e(s["tieu_de"])}</h2>'
                     + (f'<p style="font-size:34px;line-height:1.45;width:1200px;color:{cm["phu"]}">{e(s.get("phu"))}</p>' if s.get("phu") else "")) + "</div>")
            return self.khung(s, n, inner, nen=nen, toi=cm["toi"], bo_cuc="display:flex;flex-direction:column;justify-content:center;gap:40px")

        def noi(cm):
            return self.cot_chu(
                (f'<p style="font-size:24px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:{cm["phu"]}">{e(s["phan"])}</p>' if s.get("phan") else "")
                + f'<h2 data-hero="1" style="font-family:{self.HF};font-size:{self.co_td(s["tieu_de"], 76)}px;font-weight:700;line-height:1.15;color:{cm["chu"]}">{e(s["tieu_de"])}</h2>'
                + (f'<p style="font-size:34px;line-height:1.45;color:{cm["phu"]}">{e(s.get("phu"))}</p>' if s.get("phu") else ""))
        return self.khung_anh(s, n, a, noi)

    def the(self, s, n):
        muc = s.get("muc", [])
        nm = self.tim(s, "nhan_manh")
        cot = max(1, min(len(muc), 4))
        ct, cn = (40, 32) if cot <= 3 else (34, 28)
        o = []
        for i, x in enumerate(muc):
            hero = i == nm
            nen, mau, phu = (self.m["toi"], self.m["tren_toi"], self.m["tren_toi_phu"]) if hero else (self.m["xen"], self.m["chu"], self.m["chu_phu"])
            vien = self.m["nhan_toi"] if hero else self.m["vien"]
            o.append(f'<div{self.H(hero)} style="flex:{1.45 if hero else 1};display:flex;flex-direction:column;gap:16px;background:{nen};border-radius:16px;padding:{40 if hero else 32}px;border-top:8px solid {vien}">'
                     + (f'<p style="font-family:{self.HF};font-size:{64 if hero else 44}px;font-weight:700;color:{mau}">{e(x["so"])}</p>' if x.get("so") else "")
                     + f'<h3 style="font-family:{self.HF};font-size:{ct + (6 if hero else 0)}px;font-weight:700;line-height:1.2;color:{mau}">{e(x.get("tieu_de"))}</h3>'
                     f'<p style="font-size:{cn}px;line-height:1.45;color:{phu}">{e(x.get("noi_dung"))}</p></div>')
        dai = "" if s.get("diem_chinh") else ((f'<p style="font-size:32px;font-weight:600;line-height:1.4;color:{self.m["tieu_de"]}">{e(s["dai"])}</p>') if s.get("dai") else "")
        return self.khung(s, n, self.dau(s) + self.than(f'<div style="display:flex;flex-direction:row;gap:28px;align-items:stretch">{"".join(o)}</div>' + self.diem(s) + dai))

    def bang(self, s, n):
        hl = s.get("cot_nhan")
        dn = self.tim(s, "dong_nhan")
        co = 30 if len(s.get("dong", [])) <= 5 else 26

        def o(x, j, i=None, th=False):
            hero = (i is not None and i == dn)
            nen = self.m["toi"] if th else (self.m["xen"] if hero else self.m["sang"])
            mau = self.m["tren_toi"] if th else (self.m["tieu_de"] if hero else (self.m["chu"] if dn is None else self.m["chu_phu"]))
            vien = f"border-left:8px solid {self.m['nhan']};" if hero and j == 0 else ""
            return (f'<{"th" if th else "td"} style="font-size:{co}px;font-weight:{700 if th or hero or j == 0 else 400};line-height:1.35;'
                    f'padding:16px 20px;background:{nen};color:{mau};{vien}border-bottom:2px solid {self.m["vien"]};text-align:left">{e(x)}</{"th" if th else "td"}>')
        tr = "<tr>" + "".join(o(x, j, th=True) for j, x in enumerate(s.get("cot", []))) + "</tr>"
        tr += "".join((f'<tr data-hero="1">' if i == dn else "<tr>") + "".join(o(x, j, i) for j, x in enumerate(r)) + "</tr>"
                      for i, r in enumerate(s.get("dong", [])))
        _ = hl
        return self.khung(s, n, self.dau(s) + self.than(f'<table style="width:1664px;border-collapse:collapse">{tr}</table>' + self.diem(s)))

    def so_lon(self, s, n):
        so = s.get("so", [])
        sc = self.tim(s, "so_chinh", 0)
        chinh = so[sc] if 0 <= sc < len(so) else (so[0] if so else {})
        phu = [x for i, x in enumerate(so) if x is not chinh]
        hero = (f'<div data-hero="1" style="flex:1.6;display:flex;flex-direction:column;gap:20px">'
                f'<p style="font-family:{self.HF};font-size:{220 if len(str(chinh.get("gia_tri", ""))) <= 6 else 150}px;font-weight:700;line-height:1;white-space:nowrap;color:{self.m["nhan"]}">{e(chinh.get("gia_tri"))}</p>'
                f'<p style="font-size:36px;line-height:1.35;font-weight:600;color:{self.m["tieu_de"]}">{e(chinh.get("nhan"))}</p></div>')
        cot_phu = "".join(
            f'<div style="display:flex;flex-direction:column;gap:6px;border-left:4px solid {self.m["vien"]};padding-left:28px">'
            f'<p style="font-family:{self.HF};font-size:64px;font-weight:700;line-height:1;white-space:nowrap;color:{self.m["chu_phu"]}">{e(x.get("gia_tri"))}</p>'
            f'<p style="font-size:28px;line-height:1.35;color:{self.m["chu_phu"]}">{e(x.get("nhan"))}</p></div>' for x in phu)
        than = (f'<div style="flex:1;display:flex;flex-direction:row;gap:80px;align-items:center">{hero}'
                + (f'<div style="flex:1;display:flex;flex-direction:column;gap:36px">{cot_phu}</div>' if phu else "") + "</div>")
        return self.khung(s, n, self.dau(s) + than + self.diem(s))

    def so_sanh(self, s, n):
        o = []
        for x in s.get("phuong_an", []):
            kn = x.get("khuyen_nghi")
            nen, mau, phu = (self.m["toi"], self.m["tren_toi"], self.m["tren_toi_phu"]) if kn else (self.m["xen"], self.m["chu_phu"], self.m["chu_phu"])
            nhan = (f'<p style="font-size:24px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:{self.m["nhan_toi"]}">Khuyến nghị</p>' if kn
                    else f'<p style="font-size:24px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:{phu}">Phương án</p>')
            diem = "".join(f'<li style="font-size:{30 if kn else 28}px;line-height:1.4;color:{mau}">{e(y)}</li>' for y in x.get("diem", []))
            o.append(f'<div{self.H(kn)} style="flex:{1.4 if kn else 1};display:flex;flex-direction:column;gap:18px;background:{nen};border-radius:16px;padding:{40 if kn else 32}px">{nhan}'
                     f'<h3 style="font-family:{self.HF};font-size:{46 if kn else 36}px;font-weight:700;line-height:1.2;color:{mau}">{e(x.get("ten"))}</h3>'
                     f'<p style="font-size:{30 if kn else 28}px;line-height:1.4;color:{phu}">{e(x.get("mo_ta"))}</p>'
                     f'<ul style="display:flex;flex-direction:column;gap:10px;padding-left:28px">{diem}</ul></div>')
        return self.khung(s, n, self.dau(s) + self.than(f'<div style="display:flex;flex-direction:row;gap:28px;align-items:stretch">{"".join(o)}</div>' + self.diem(s)))

    def lo_trinh(self, s, n):
        b = s.get("buoc", [])
        nm = self.tim(s, "nhan_manh")
        o = []
        for i, x in enumerate(b):
            hero = i == nm
            o.append(f'<div{self.H(hero)} style="flex:{1.3 if hero else 1};display:flex;flex-direction:column;gap:14px">'
                     f'<div style="height:{14 if hero else 8}px;background:{self.m["nhan"] if hero else self.m["vien"]};border-radius:7px"></div>'
                     f'<p style="font-size:24px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:{self.m["tieu_de"] if hero else self.m["chu_phu"]}">{e(x.get("moc"))}</p>'
                     f'<h3 style="font-family:{self.HF};font-size:{48 if hero else (40 if len(b) <= 4 else 34)}px;font-weight:700;line-height:1.2;color:{self.m["tieu_de"] if hero else self.m["chu"]}">{e(x.get("ten"))}</h3>'
                     f'<p style="font-size:{32 if hero else 28}px;line-height:1.4;color:{self.m["chu_phu"]}">{e(x.get("viec"))}</p></div>')
        return self.khung(s, n, self.dau(s) + self.than(f'<div style="display:flex;flex-direction:row;gap:32px">{"".join(o)}</div>' + self.diem(s)))

    def hai_cot(self, s, n):
        """Bố cục 'nua-trang': ảnh tràn mép phải, mép trái ảnh tan vào nền bằng dải chuyển sắc."""
        a = s.get("anh")
        nen = self.m["sang"]
        diem = "".join(
            f'<div style="display:flex;flex-direction:row;gap:20px;align-items:flex-start">'
            f'<div style="flex:none;width:14px;height:14px;margin-top:14px;background:{self.m["vien"]};border-radius:7px"></div>'
            f'<p style="flex:1;font-size:30px;line-height:1.4;color:{self.m["chu_phu"]}">{e(x)}</p></div>' for x in s.get("diem", []))
        bg = ""
        if a:
            nen = self.mau_vung_trong(a, "trai") or nen
            src = self.anh_map.get(a.get("tep"))
            sx = f' src="{src}"' if src else ""
            bg = (f'<img{sx} data-nen="1" alt="{e(a.get("mo_ta") or "")}" style="position:absolute;left:880px;top:0;width:1040px;height:1080px;object-fit:cover">'
                  f'<div style="position:absolute;left:880px;top:0;width:360px;height:1080px;background:linear-gradient(90deg, {self.rgba(nen, 1)} 0%, {self.rgba(nen, 0)} 100%)"></div>')
        cm = self.bo_mau_nen(nen)
        trai = f'<div style="position:relative;width:720px;display:flex;flex-direction:column;gap:28px">{self.dau(s)}{self.diem(s, cm["toi"])}{diem}</div>'
        return self.khung(s, n, bg + trai, nen=nen, toi=cm["toi"], bo_cuc="display:flex;flex-direction:column;justify-content:center;gap:40px")

    def doi_ngu(self, s, n):
        nm = self.tim(s, "nhan_manh")
        o = "".join(
            f'<div{self.H(i == nm)} style="display:flex;flex-direction:column;gap:12px;background:{self.m["toi"] if i == nm else self.m["xen"]};border-radius:16px;padding:32px">'
            f'<h3 style="font-family:{self.HF};font-size:34px;font-weight:700;color:{self.m["tren_toi"] if i == nm else self.m["chu"]}">{e(x.get("ten"))}</h3>'
            f'<p style="font-size:26px;font-weight:700;color:{self.m["nhan_toi"] if i == nm else self.m["chu_phu"]}">{e(x.get("vai"))}</p>'
            f'<p style="font-size:26px;line-height:1.4;color:{self.m["tren_toi_phu"] if i == nm else self.m["chu_phu"]}">{e(x.get("bang_chung_nang_luc", ""))}</p></div>'
            for i, x in enumerate(s.get("nguoi", [])))
        cot = max(1, min(len(s.get("nguoi", [])), 4))
        return self.khung(s, n, self.dau(s) + self.than(f'<div style="display:grid;grid-template-columns:repeat({cot}, 1fr);gap:28px">{o}</div>' + self.diem(s)))

    def bieu_do(self, s, n):
        """Biểu đồ dựng bằng HTML (không cần thư viện): cột, ngang, chồng 100%, thác nước, đường. Chỉ điểm nhấn mang màu nhấn."""
        bd = s.get("bieu_do") or {}
        loai = bd.get("loai", "cot")
        nhan = bd.get("nhan", [])
        chuoi = bd.get("chuoi", [])
        dv = bd.get("don_vi", "")
        dn = bd.get("diem_nhan")
        mn, xam = self.m["nhan"], self.rgba(self.m["chu_phu"], 0.32)
        gt = (chuoi[0].get("gia_tri", []) if chuoi else [])

        def so(v):
            return (f"{v:,.1f}".rstrip("0").rstrip(".") if isinstance(v, float) else f"{v:,}").replace(",", " ") + (f" {dv}" if dv else "")
        H = 400
        if loai in ("cot", "thac"):
            mx = max([abs(x) for x in gt] + [1]) if loai == "cot" else max([sum(gt[:i + 1]) for i in range(len(gt))] + [1])
            cot, tich = [], 0
            for i, v in enumerate(gt):
                hero = i == dn
                cao = int(H * abs(v) / mx)
                day = int(H * tich / mx) if loai == "thac" else 0
                tich += v
                cot.append(f'<div{self.H(hero)} style="flex:1;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;gap:12px;height:{H + 120}px">'
                           f'<p style="font-family:{self.HF};font-size:{44 if hero else 28}px;font-weight:700;color:{self.m["tieu_de"] if hero else self.m["chu_phu"]}">{e(so(v))}</p>'
                           f'<div style="width:100%;height:{max(cao, 4)}px;background:{mn if hero else xam};border-radius:8px 8px 0 0"></div>'
                           f'<div style="height:{day}px"></div>'
                           f'<p style="font-size:28px;line-height:1.2;text-align:center;color:{self.m["chu"] if hero else self.m["chu_phu"]}">{e(nhan[i] if i < len(nhan) else "")}</p></div>')
            hinh = f'<div style="width:1100px;display:flex;flex-direction:row;gap:28px;align-items:flex-end;border-bottom:3px solid {self.m["vien"]}">{"".join(cot)}</div>'
        elif loai == "ngang":
            mx = max([abs(x) for x in gt] + [1])
            hang = "".join(
                f'<div{self.H(i == dn)} style="display:flex;flex-direction:row;align-items:center;gap:20px">'
                f'<p style="width:300px;font-size:28px;text-align:right;color:{self.m["chu"] if i == dn else self.m["chu_phu"]}">{e(nhan[i] if i < len(nhan) else "")}</p>'
                f'<div style="width:{int(640 * abs(v) / mx)}px;height:{56 if i == dn else 40}px;background:{mn if i == dn else xam};border-radius:0 8px 8px 0"></div>'
                f'<p style="font-family:{self.HF};font-size:{40 if i == dn else 28}px;font-weight:700;color:{self.m["tieu_de"] if i == dn else self.m["chu_phu"]}">{e(so(v))}</p></div>'
                for i, v in enumerate(gt))
            hinh = f'<div style="width:1100px;display:flex;flex-direction:column;gap:22px">{hang}</div>'
        elif loai == "chong":
            hang = []
            for i, ten in enumerate(nhan):
                vs = [c.get("gia_tri", [0] * len(nhan))[i] for c in chuoi]
                tong = sum(vs) or 1
                o_ = "".join(
                    f'<div style="width:{int(800 * v / tong)}px;height:{56 if i == dn else 44}px;background:{(mn if j == 0 else self.rgba(self.m["chu_phu"], 0.18 + 0.14 * j)) if i == dn else self.rgba(self.m["chu_phu"], 0.14 + 0.12 * j)}"></div>'
                    for j, v in enumerate(vs))
                hang.append(f'<div{self.H(i == dn)} style="display:flex;flex-direction:row;align-items:center;gap:20px">'
                            f'<p style="width:240px;font-size:28px;text-align:right;color:{self.m["chu"] if i == dn else self.m["chu_phu"]}">{e(ten)}</p>'
                            f'<div style="display:flex;flex-direction:row">{o_}</div>'
                            f'<p style="font-size:28px;font-weight:700;color:{self.m["tieu_de"] if i == dn else self.m["chu_phu"]}">{e(so(vs[0]))}</p></div>')
            chu_giai = " · ".join(e(c.get("ten", "")) for c in chuoi)
            hinh = (f'<div style="width:1100px;display:flex;flex-direction:column;gap:22px">{"".join(hang)}'
                    f'<p style="font-size:24px;color:{self.m["chu_phu"]}">{chu_giai}</p></div>')
        else:  # duong
            mx = max(gt + [1])
            mi = min(gt + [0])
            W, Hh = 1100, 440
            dx = W / max(len(gt) - 1, 1)
            pts = [(round(i * dx), round(Hh - (v - mi) / ((mx - mi) or 1) * Hh)) for i, v in enumerate(gt)]
            poly = " ".join(f"{x},{y}" for x, y in pts)
            dot = "".join(f'<circle cx="{x}" cy="{y}" r="{16 if i == dn else 7}" fill="{mn if i == dn else self.m["chu_phu"]}"/>' for i, (x, y) in enumerate(pts))
            svg = (f'<svg aria-label="{e(s.get("diem_chinh") or s.get("tieu_de"))}" width="{W}" height="{Hh + 20}" viewBox="-20 -10 {W + 40} {Hh + 20}" style="width:{W}px;height:{Hh + 20}px">'
                   f'<polyline points="{poly}" fill="none" stroke="{self.m["chu_phu"]}" stroke-width="5"/>{dot}</svg>')
            nhan_x = "".join(f'<p style="flex:1;text-align:center;font-size:24px;color:{self.m["chu"] if i == dn else self.m["chu_phu"]}">{e(nhan[i] if i < len(nhan) else "")}</p>' for i in range(len(gt)))
            gt_dn = (f'<p data-hero="1" style="font-family:{self.HF};font-size:64px;font-weight:700;color:{mn}">{e(so(gt[dn]))}</p>'
                     if isinstance(dn, int) and dn < len(gt) else "")
            hinh = (f'<div style="width:1100px;display:flex;flex-direction:column;gap:12px">{gt_dn}{svg}'
                    f'<div style="display:flex;flex-direction:row">{nhan_x}</div></div>')
        than = (f'<div style="flex:1;display:flex;flex-direction:row;gap:64px;align-items:center">{hinh}'
                f'<div style="flex:1;display:flex;flex-direction:column;gap:20px">{self.diem(s)}'
                + (f'<p style="font-size:28px;line-height:1.4;color:{self.m["chu_phu"]}">{e(s.get("phu"))}</p>' if s.get("phu") else "") + "</div></div>")
        return self.khung(s, n, self.dau(s) + than)

    def ket(self, s, n):
        a = s.get("anh") or self.anh_bia()

        def noi(cm):
            chinh = s.get("hanh_dong_chinh")
            if chinh and gan_giong(s["tieu_de"], chinh):  # trùng tiêu đề: không in hai lần
                chinh = None
            b = "".join(f'<p style="font-size:30px;line-height:1.45;color:{cm["phu"]}">{i}. {e(x)}</p>' for i, x in enumerate(s.get("buoc_tiep", []), 1))
            return self.cot_chu(
                f'<h2{"" if chinh else self.H(True)} style="font-family:{self.HF};font-size:{self.co_td(s["tieu_de"], 72)}px;font-weight:700;line-height:1.12;color:{cm["chu"]}">{e(s["tieu_de"])}</h2>'
                + (f'<p data-hero="1" style="font-family:{self.HF};font-size:44px;font-weight:700;line-height:1.25;color:{cm["nhan"]}">{e(chinh)}</p>' if chinh else "")
                + f'<div style="display:flex;flex-direction:column;gap:10px">{b}</div>'
                f'<p style="font-size:28px;line-height:1.5;color:{cm["phu"]}">{e(s.get("lien_he", ""))}</p>'
                + self.cum_logo(56), rong=960)
        return self.khung_anh(s, n, a, noi)


RENDER = {"bia": "bia", "tom-tat": "tom_tat", "muc-luc": "muc_luc", "chuong": "chuong", "khang-dinh": "khang_dinh",
          "the": "the", "bang": "bang", "so-lon": "so_lon", "so-sanh": "so_sanh", "lo-trinh": "lo_trinh",
          "hai-cot": "hai_cot", "doi-ngu": "doi_ngu", "bieu-do": "bieu_do", "ket": "ket"}


def doc_hanh_trinh(d):
    p = Path(d) / "10-hanh-trinh.json"
    return {x["id"]: x for x in doc_json(p).get("slides", []) if x.get("id")} if p.exists() else {}


def lenh_xuat(d, anh_map_path=None, logo=None):
    dk = doc_deck(d)
    if not dk:
        raise SystemExit("chưa có 10-deck.json")
    brand = dk.get("brand", "linhx")
    th = thuong_hieu(brand)
    anh_map = doc_json(anh_map_path) if anh_map_path else {}
    ve = Ve(th, dk, anh_map, logo)
    ve.thu = d
    ve.ht = doc_hanh_trinh(d)
    goc = Path(d) / "13-claude-deck" / "project"
    if goc.exists():
        shutil.rmtree(goc / "slides", ignore_errors=True)
    (goc / "slides").mkdir(parents=True, exist_ok=True)
    order, sections, cho = [], {}, None
    for n, s in enumerate(dk["slides"], 1):
        if s["kieu"] == "chuong" or n == 1:
            cho = s.get("tieu_de")
            sections[f"s{len(sections) + 1}"] = {"description": cho, "start": s["id"]}
        (goc / "slides" / f"{s['id']}.html").write_text(getattr(ve, RENDER[s["kieu"]])(s, n), encoding="utf-8")
        order.append(s["id"])
    faces = {}
    for fam in {th["font"]["tieu_de"], th["font"]["than"]}:
        key = fam.lower().replace(" ", "-")
        faces[key] = {"family": fam, "href": "https://fonts.googleapis.com/css2?family=" + fam.replace(" ", "+") + ":wght@400;600;700&display=swap"}
    ds_list, files = [], {}
    if th.get("ds_url"):
        ns = re.sub(r"[^a-z0-9-]", "", brand.lower()) or "brand"
        ds_list.append({"title": th["ten"], "namespace": ns, "artifact": th["ds_url"], "version": None, "copiedAt": bay_gio()})
        files[f"project/ds/{ns}/tokens.json"] = {"artifact": th["ds_url"], "path": "project/tokens.json"}
    deck_json = {"v": 4, "createdOnFiles": {"v": 1, "at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
                 "lists": "css", "title": dk.get("ten", "Deck"), "order": order, "sections": sections,
                 "cover": order[0], "faces": faces, "designSystems": ds_list}
    ghi_json(goc / "deck.json", deck_json)
    huong_dan = {
        "root": str((Path(d) / "13-claude-deck").resolve()),
        "file_path": str((goc / "deck.json").resolve()),
        "files": {**{f"project/slides/{i}.html": f"project/slides/{i}.html" for i in order}, **files},
        "ghi_chu": "Artifact publish: lần đầu tạo deck bằng type_url Slides + title, rồi publish với url, root, file_path, files như trên. Ảnh: tải lên bằng asset:true, ghi /_blob/... vào anh-map.json, chạy lại xuat.",
    }
    ghi_json(Path(d) / "13-claude-deck" / "publish.json", huong_dan)
    thieu_anh = [a["tep"] for _, a in anh_trong_deck(dk) if a["tep"] not in anh_map]
    print(f"Đã dựng {len(order)} slide ở {goc}. Hướng dẫn đăng: 13-claude-deck/publish.json")
    if thieu_anh:
        print(f"! {len(thieu_anh)} ảnh chưa có /_blob trong anh-map: {thieu_anh}")


# ---------------------------------------------------------------- chụp kiểm chuẩn slide

XEM_BAO_CAO = "13-claude-deck/xem/bao-cao.json"
SO_CHU_TOI_DA_SLIDE = 110  # quá thì cảnh báo: slide là để nhìn, không phải để đọc

JS_KIEM = r"""() => {
  const sec = document.querySelector('section'); const loi = [], canh = [];
  const W = 1920, H = 1080, M = 128;
  const pinned = e => { for (let x = e; x && x !== sec; x = x.parentElement) if (getComputedStyle(x).position === 'absolute') return true; return false; };
  const coChu = e => [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
  const ten = e => e.tagName.toLowerCase() + (coChu(e) ? ` "${e.textContent.trim().replace(/\s+/g, ' ').slice(0, 40)}"` : '');
  const els = [...sec.querySelectorAll('*')].filter(e => !e.closest('aside'));
  const coChan = els.some(e => pinned(e) && e.getBoundingClientRect().top > 980);
  const day = coChan ? 920 : H - 112;
  const chu = [];
  for (const e of els) {
    const r = e.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) continue;
    const laAnh = e.tagName === 'IMG';
    if (!coChu(e) && !laAnh) continue;
    if (r.right > W + 1 || r.bottom > H + 1 || r.left < -1 || r.top < -1) loi.push(`tràn khung: ${ten(e)}`);
    if (!pinned(e)) {
      if (r.bottom > day + 2) loi.push(`lấn lề dưới (đáy ${Math.round(r.bottom)} > ${day}): ${ten(e)}`);
      if (r.left < M - 2 || r.right > W - M + 2) loi.push(`lấn lề trái/phải: ${ten(e)}`);
    }
    if (laAnh) {
      if (!e.getAttribute('src')) loi.push(`ô ảnh trống: ${e.alt.slice(0, 40)}`);
      else if (!e.naturalWidth) loi.push(`ảnh không tải được: ${e.alt.slice(0, 40)}`);
      continue;
    }
    const cs = getComputedStyle(e), fs = parseFloat(cs.fontSize);
    if (fs < 24) loi.push(`chữ ${fs}px dưới 24px: ${ten(e)}`);
    else if (fs < 28 && !pinned(e) && cs.textTransform !== 'uppercase' && e.tagName !== 'TD' && e.tagName !== 'TH') canh.push(`chữ thân ${fs}px, nên ≥ 28px: ${ten(e)}`);
    const rg = document.createRange(); rg.selectNodeContents(e); const t = rg.getBoundingClientRect();
    const du = Math.max(3, 0.45 * fs);  // phần đầu/đuôi glyph vượt line-height là bình thường
    if (t.right > r.right + 3 || t.bottom > r.bottom + du) loi.push(`chữ tràn hộp: ${ten(e)}`);
    if (e.scrollWidth > e.clientWidth + 3 && cs.overflowX !== 'visible') loi.push(`chữ bị cắt: ${ten(e)}`);
    if (!pinned(e)) chu.push([e, r]);
  }
  for (let i = 0; i < chu.length; i++) for (let j = i + 1; j < chu.length; j++) {
    const [a, ra] = chu[i], [b, rb] = chu[j];
    if (a.contains(b) || b.contains(a)) continue;
    const w = Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left), h = Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top);
    if (w > 4 && h > 4) loi.push(`chữ chồng nhau: ${ten(a)} / ${ten(b)}`);
  }
  if (!coChan || true) {
    const day_noi_dung = chu.reduce((m, [, r]) => Math.max(m, r.bottom), 0);
    const anh = [...sec.querySelectorAll('img')].filter(i => !pinned(i)).reduce((m, i) => Math.max(m, i.getBoundingClientRect().bottom), 0);
    if (coChan && Math.max(day_noi_dung, anh) < 0.62 * H) canh.push(`khối nội dung dừng ở ${Math.round(Math.max(day_noi_dung, anh))}px: nửa dưới slide trống (C12)`);
  }
  const hop = [];
  const coAnhNen = !!sec.querySelector('img[data-nen]');
  for (const [e, r] of chu) {
    const cs = getComputedStyle(e);
    hop.push({x: r.left, y: r.top, w: r.width, h: r.height, mau: cs.color, co: parseFloat(cs.fontSize), ten: ten(e)});
  }
  const heroEl = sec.querySelector('[data-hero]');
  let hero = null;
  if (heroEl) { const r = heroEl.getBoundingClientRect(); hero = {x: r.left, y: r.top, w: r.width, h: r.height}; }
  const tieuDe = sec.querySelector('h1, h2');
  let dongTieuDe = 0;
  if (tieuDe) { const cs = getComputedStyle(tieuDe); dongTieuDe = Math.round(tieuDe.getBoundingClientRect().height / (parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.15)); }
  const nhan = (window.__NHAN || []).map(x => x.toLowerCase());
  const rgb2hex = c => { const m = (c || '').match(/\d+/g); return m ? '#' + m.slice(0, 3).map(v => (+v).toString(16).padStart(2, '0')).join('') : ''; };
  let soNhan = 0;
  for (const e of els) {
    const cs = getComputedStyle(e);
    const r = e.getBoundingClientRect(); if (r.width * r.height < 30) continue;
    const dung = [cs.backgroundColor, cs.borderTopColor && parseFloat(cs.borderTopWidth) >= 4 ? cs.borderTopColor : '', cs.borderLeftColor && parseFloat(cs.borderLeftWidth) >= 4 ? cs.borderLeftColor : '',
                  coChu(e) ? cs.color : ''].map(rgb2hex);
    if (dung.some(h => nhan.includes(h))) soNhan++;
  }
  const diemEl = sec.querySelector('[data-diem]');
  let diem = null;
  if (diemEl) { const r = diemEl.getBoundingClientRect(); diem = {x: r.left, y: r.top}; }
  const tdr = tieuDe ? tieuDe.getBoundingClientRect() : null;
  const so = sec.innerText.replace(/\s+/g, ' ').trim().split(' ').length - (sec.querySelector('aside') ? sec.querySelector('aside').innerText.split(/\s+/).length : 0);
  if (so > %d) canh.push(`${so} chữ trên slide (nên ≤ %d)`);
  return {loi: [...new Set(loi)], canh, hop, coAnhNen, hero, dongTieuDe, soNhan, diem, tieuDe: tdr ? {y: tdr.top} : null,
          laNoiDung: !sec.querySelector('img[data-nen]') && !!sec.querySelector('h2') && !sec.querySelector('h1')};
}""" % (SO_CHU_TOI_DA_SLIDE, SO_CHU_TOI_DA_SLIDE)


def mau_css(c):
    m = re.findall(r"[\d.]+", c or "")
    return tuple(int(float(x)) for x in m[:3]) if len(m) >= 3 else (0, 0, 0)


def lum_rgb(t):
    f = lambda c: (c / 255) / 12.92 if c / 255 <= 0.03928 else ((c / 255 + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(t[0]) + 0.7152 * f(t[1]) + 0.0722 * f(t[2])


def phan_tich_anh_chup(png, kq_js, sid):
    """Đo trên điểm ảnh thật: tương phản chữ trên ảnh nền; thử nheo mắt (thu nhỏ còn thấy tiêu điểm)."""
    loi, canh = [], []
    try:
        from PIL import Image, ImageFilter, ImageStat
    except ImportError:
        return loi, canh
    im = Image.open(png).convert("RGB")
    if kq_js.get("coAnhNen"):
        for h in kq_js.get("hop", []):
            if h["w"] < 8 or h["h"] < 8:
                continue
            vung = im.crop((int(h["x"]), int(h["y"]), int(h["x"] + h["w"]), int(h["y"] + h["h"]))).resize((40, 12))
            chu = mau_css(h["mau"])
            px = list(vung.getdata())
            # nền = các điểm ảnh khác màu chữ nhất (bỏ nét chữ), lấy trung vị
            px.sort(key=lambda c: -sum(abs(c[i] - chu[i]) for i in range(3)))
            nen = px[:max(1, len(px) * 2 // 3)]
            nen_tb = tuple(sorted(c[i] for c in nen)[len(nen) // 2] for i in range(3))
            la, lb = sorted([lum_rgb(chu), lum_rgb(nen_tb)], reverse=True)
            tp = (la + 0.05) / (lb + 0.05)
            can = 3.0 if h["co"] >= 24 else 4.5
            if h["co"] < 24 or tp < can:
                loi.append(f"chữ trên ảnh tương phản {tp:.1f}:1 (cần ≥ {can}): {h['ten']}")
    hero = kq_js.get("hero")
    if hero and kq_js.get("laNoiDung"):
        nho = im.resize((192, 108)).filter(ImageFilter.GaussianBlur(2)).convert("L")
        nen = ImageStat.Stat(nho).median[0]
        sx = 192 / 1920
        hop = (int(hero["x"] * sx), int(hero["y"] * sx), int((hero["x"] + hero["w"]) * sx) + 1, int((hero["y"] + hero["h"]) * sx) + 1)
        trong = ImageStat.Stat(nho.crop(hop)).mean[0] if hop[2] > hop[0] and hop[3] > hop[1] else nen
        lech_hero = abs(trong - nen)
        lech_max = 0
        for y in range(0, 108 - 18, 9):
            for x in range(0, 192 - 32, 16):
                if x < hop[2] and x + 32 > hop[0] and y < hop[3] and y + 18 > hop[1]:
                    continue
                lech_max = max(lech_max, abs(ImageStat.Stat(nho.crop((x, y, x + 32, y + 18))).mean[0] - nen))
        if lech_hero < 0.6 * lech_max:
            canh.append("thử nheo mắt: thu nhỏ slide thì tiêu điểm không nổi bằng khối khác")
    return loi, canh


def dau_van_slides(d):
    h = hashlib.sha1()
    for f in sorted((Path(d) / "13-claude-deck/project/slides").glob("*.html")):
        h.update(f.name.encode())
        h.update(f.read_bytes())
    return h.hexdigest()[:12]


def to_hinh(cac_anh, ra, cot=4, w=480, h=270, nhan=None):
    """Ghép ảnh thành một tờ (cần Pillow; không có thì bỏ qua)."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("! không có Pillow, bỏ qua tờ ghép ảnh")
        return None
    hang = (len(cac_anh) + cot - 1) // cot
    to = Image.new("RGB", (cot * w + (cot + 1) * 16, hang * (h + 40) + 16), "#FFFFFF")
    v = ImageDraw.Draw(to)
    for i, p in enumerate(cac_anh):
        im = Image.open(p).convert("RGB")
        im.thumbnail((w, h))
        x, y = 16 + (i % cot) * (w + 16), 16 + (i // cot) * (h + 40)
        to.paste(im, (x + (w - im.width) // 2, y + 24))
        v.text((x, y + 4), (nhan[i] if nhan else Path(p).stem), fill="#1F2933")
    to.save(ra)
    return ra


def lenh_xem(d):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise SystemExit("cần Playwright: pip install playwright, rồi playwright install chromium (hoặc có sẵn Chromium)")
    dk = doc_deck(d)
    goc = Path(d) / "13-claude-deck"
    pj = goc / "project" / "deck.json"
    if not dk or not pj.exists():
        raise SystemExit("chưa xuất deck: deck.py xuat <dir>")
    th = thuong_hieu(dk.get("brand", "linhx"))
    order = doc_json(pj)["order"]
    am = doc_json(goc / "anh-map.json") if (goc / "anh-map.json").exists() else {}
    cuc_bo = {}  # dựng lại từ 10-deck.json với ảnh/logo cục bộ để soát bố cục thật
    for _, a in anh_trong_deck(dk):
        f = Path(d) / "11-goi-anh" / "anh" / a["tep"]
        if f.exists():
            cuc_bo[a["tep"]] = f.resolve().as_uri()
    for k in ("logo_ta", "logo_khach"):
        if dk.get(k) and (Path(d) / dk[k]).exists():
            cuc_bo[dk[k]] = (Path(d) / dk[k]).resolve().as_uri()
    ve = Ve(th, dk, cuc_bo, None)
    ve.thu = d
    ve.ht = doc_hanh_trinh(d)
    chua_tai = [k for k in cuc_bo if k not in am]
    fonts = "".join(f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={f.replace(" ", "+")}:wght@400;600;700&display=swap">'
                    for f in {th["font"]["tieu_de"], th["font"]["than"]})
    ra = goc / "xem"
    shutil.rmtree(ra, ignore_errors=True)
    (ra / "_html").mkdir(parents=True)
    loi, canh, hinh = [], [], []
    with sync_playwright() as pw:
        tr = mo_trinh_duyet(pw)
        tab = tr.new_page(viewport={"width": 1920, "height": 1080})
        theo_id = {s["id"]: (n, s) for n, s in enumerate(dk["slides"], 1)}
        for sid in order:
            n, s = theo_id[sid]
            sec = getattr(ve, RENDER[s["kieu"]])(s, n)
            trang = ('<!doctype html><html><head><meta charset="utf-8">' + fonts +
                     '<style>*{box-sizing:border-box;margin:0}html,body{margin:0;width:1920px;height:1080px;overflow:hidden}'
                     'section{width:1920px;height:1080px;position:relative;overflow:hidden}aside{display:none}</style></head><body>'
                     + sec + "</body></html>")
            f = ra / "_html" / f"{sid}.html"
            f.write_text(trang, encoding="utf-8")
            tab.goto(f.resolve().as_uri())
            tab.wait_for_load_state("networkidle")
            tab.evaluate("document.fonts.ready")
            png = ra / f"{sid}.png"
            tab.screenshot(path=str(png))
            hinh.append(png)
            tab.evaluate(f"window.__NHAN = {json.dumps([th['mau']['nhan'], th['mau']['nhan_toi']])}")
            kq = tab.evaluate(JS_KIEM)
            loi += [f"{sid}: {x}" for x in kq["loi"]]
            canh += [f"{sid}: {x}" for x in kq["canh"]]
            l2, c2 = phan_tich_anh_chup(png, kq, sid)
            loi += [f"{sid}: {x}" for x in l2]
            canh += [f"{sid}: {x}" for x in c2]
            if kq.get("dongTieuDe", 0) > 2:
                canh.append(f"{sid}: tiêu đề {kq['dongTieuDe']} dòng, nên ≤ 2")
            if s.get("kieu") not in KIEU_KHONG_NOI_DUNG and s.get("kieu") != "tom-tat":
                if not kq.get("hero"):
                    loi.append(f"{sid}: không có tiêu điểm (data-hero): mắt không biết nhìn đâu")
                if kq.get("soNhan", 0) > 2:
                    canh.append(f"{sid}: màu nhấn xuất hiện ở {kq['soNhan']} chỗ, nên chỉ ở tiêu điểm")
                if kq.get("hero") and kq.get("diem") and kq.get("tieuDe") and not (kq["tieuDe"]["y"] <= kq["hero"]["y"] + 1):
                    canh.append(f"{sid}: đường mắt: tiêu đề phải đứng trước tiêu điểm")
        tr.close()
    shutil.rmtree(ra / "_html", ignore_errors=True)
    to_hinh(hinh, ra / "to-slide.png", nhan=[f"{i}. {p.stem}" for i, p in enumerate(hinh, 1)])
    if chua_tai:
        canh.append(f"ảnh/logo chưa tải lên làm asset (cổng 13 sẽ chặn): {chua_tai}")
    ghi_json(ra / "bao-cao.json", {"dau_van": dau_van_slides(d), "luc": bay_gio(), "dat": not loi, "loi": loi, "canh_bao": canh,
                                   "chuan": "skills/dung-deck/references/chuan-slide.md"})
    for x in loi:
        print("✗ " + x)
    for x in canh:
        print("! " + x)
    print(f"{'ĐẠT' if not loi else 'CHƯA ĐẠT'}: {len(order)} slide chụp ở {ra}, tờ ghép {ra / 'to-slide.png'}. "
          "Claude mở tờ ghép, chấm thêm bằng mắt theo chuan-slide.md.")
    return not loi


# ---------------------------------------------------------------- logo

def logo_goc_brand(brand):
    """Logo gốc của BU: khoá logo_goc (đường dẫn tuyệt đối) trong thuong-hieu.json, hoặc tìm trong LAB012/brands/<brand>/assets."""
    th = thuong_hieu(brand)
    if th.get("logo_goc") and Path(th["logo_goc"]).exists():
        return Path(th["logo_goc"])
    lab012 = GOC.parents[2] / "LAB012-BRAND-STANDARD" / "brands" / brand / "assets"
    if th.get("logo") and (lab012 / th["logo"]).exists():
        return lab012 / th["logo"]
    return None


def mo_trinh_duyet(pw):
    try:
        return pw.chromium.launch()
    except Exception:  # không có Chromium của Playwright: dùng Chrome đã cài (headless, hồ sơ riêng)
        return pw.chromium.launch(channel="chrome")


def svg_sang_png(svg, png, cao=240):
    """Ảnh raster ổn định cho Claude Slides: đổi logo SVG sang PNG nền trong (Playwright)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise SystemExit("logo SVG cần Playwright để đổi sang PNG (hoặc tự xuất PNG rồi chạy lại)")
    with sync_playwright() as pw:
        tr = mo_trinh_duyet(pw)
        tab = tr.new_page(device_scale_factor=2)
        bao = Path(png).with_suffix(".bao.html")
        bao.write_text(f'<html><body style="margin:0;background:transparent"><img id="l" src="{Path(svg).resolve().name}" style="height:{cao}px"></body></html>', encoding="utf-8")
        shutil.copy(svg, bao.parent / Path(svg).name)
        tab.goto(bao.resolve().as_uri())
        tab.wait_for_load_state("networkidle")
        ok = tab.evaluate("(() => { const i = document.getElementById('l'); return i.complete && i.naturalWidth > 0; })()")
        if ok:
            tab.locator("#l").screenshot(path=str(png), omit_background=True)
        tr.close()
        bao.unlink(missing_ok=True)
        (bao.parent / Path(svg).name).unlink(missing_ok=True)
    if not ok:
        raise SystemExit(f"không đổi được {svg} sang PNG (ảnh không nạp được): xuất PNG từ Design System rồi chạy lại")
    return Path(png)


def cat_vien_logo(f, nguong=245, chua=0.04):
    """Logo gốc hay có viền trắng/trong rất rộng (Sakedemy: logo chiếm 1/3 khung): cắt sát rồi chừa 4%. Cần Pillow."""
    try:
        from PIL import Image
    except ImportError:
        return
    im = Image.open(f).convert("RGBA")
    px = im.load()
    w, h = im.size
    xs, ys = [], []
    for y in range(0, h, max(1, h // 400)):
        for x in range(0, w, max(1, w // 400)):
            r, g, b, a = px[x, y]
            if a > 16 and min(r, g, b) < nguong:
                xs.append(x)
                ys.append(y)
    if not xs:
        return
    hop = (min(xs), min(ys), max(xs) + 1, max(ys) + 1)
    if (hop[2] - hop[0]) * (hop[3] - hop[1]) > 0.85 * w * h:
        return
    c = int(chua * max(hop[2] - hop[0], hop[3] - hop[1])) + max(w, h) // 400
    hop = (max(0, hop[0] - c), max(0, hop[1] - c), min(w, hop[2] + c), min(h, hop[3] + c))
    im.crop(hop).save(f)


def lenh_logo_tu_tep(d, tep):
    """Rút ảnh nhúng trong pptx/docx (logo khách thường nằm trong tài liệu của họ) ra <dir>/logo/ung-vien/ + tờ ghép để chọn."""
    import zipfile
    ra = Path(d) / "logo" / "ung-vien"
    ra.mkdir(parents=True, exist_ok=True)
    co = []
    with zipfile.ZipFile(tep) as z:
        for ten in z.namelist():
            if re.search(r"/media/[^/]+\.(png|jpe?g|svg|webp)$", ten, re.I):
                b = z.read(ten)
                if len(b) < 2000:
                    continue
                f = ra / (Path(tep).stem[:20] + "-" + Path(ten).name)
                f.write_bytes(b)
                co.append(f)
    nho = [f for f in co if f.suffix.lower() != ".svg" and (kich_thuoc_anh(f) or (0, 0))[0] and max(kich_thuoc_anh(f)) < 1500]
    to_hinh(nho[:40] or co[:40], ra / "to-logo.png", cot=6, w=240, h=160)
    print(f"Đã rút {len(co)} ảnh vào {ra}; tờ ghép {ra / 'to-logo.png'}. Mở tờ ghép, chọn logo, rồi: deck.py logo <dir> --khach <tệp> --khach-ten …")


def lenh_logo(d, ta=None, khach=None, khach_ten=None, nguon=None):
    d = Path(d)
    dk = doc_deck(d)
    if dk is None:
        raise SystemExit("chưa có 10-deck.json")
    (d / "logo").mkdir(exist_ok=True)
    if not ta and not dk.get("logo_ta"):
        g = logo_goc_brand(dk.get("brand", "linhx"))
        ta = str(g) if g else None
    for khoa, tep_nguon in (("logo_ta", ta), ("logo_khach", khach)):
        if not tep_nguon:
            continue
        f = Path(tep_nguon)
        if not f.exists():
            raise SystemExit(f"không thấy tệp logo {f}")
        if f.suffix.lower() not in DUOI_ANH | {".svg"}:
            raise SystemExit(f"{f.name}: logo phải là png/jpg/webp/svg (svg sẽ cần đổi sang png khi đăng)")
        dich = d / "logo" / (("ta-" if khoa == "logo_ta" else "khach-") + re.sub(r"[^A-Za-z0-9._-]", "-", f.name))
        if f.suffix.lower() == ".svg":
            dich = svg_sang_png(f, dich.with_suffix(".png"))
        else:
            shutil.copy(f, dich)
        dk[khoa] = f"logo/{dich.name}"
        cat_vien_logo(dich)
        kt = kich_thuoc_anh(dich)
        print(f"✓ {khoa} = logo/{dich.name} (từ {f}, {kt[0]}×{kt[1]} px)" if kt else f"✓ {khoa} = logo/{dich.name} (từ {f})")
        if kt and max(kt) < 600:
            print(f"! {dich.name} chỉ {kt[0]}×{kt[1]} px: dễ vỡ trên bìa 1920 px; xin Linh/khách bản gốc (SVG hoặc PNG ≥ 1200 px)")
    if khach_ten:
        dk["khach"] = khach_ten
    if nguon and khach:
        dk["logo_khach_nguon"] = {"nguon": nguon, "luc": bay_gio()}
    ghi_json(d / BUOC[10][1], dk)
    for l in kiem_logo(d, dk):
        print("! " + l)


# ---------------------------------------------------------------- 8b thư viện bố cục slide

def thu_vien_bo_cuc():
    import os
    p = Path(os.environ.get("LINHX_DECK_BO_CUC") or DU_LIEU / "bo-cuc") / "thu-vien.json"
    return doc_json(p) if p.exists() else {"bo_cuc": []}


def kiem_bo_cuc_deck(d, kq):
    """Mọi kiểu slide dùng trong deck phải trỏ về một bố cục trong thư viện (08-the-phong-cach.json: bo_cuc_slide)."""
    p8 = Path(d) / BUOC[8][1]
    dk = doc_deck(d) or {}
    the = doc_json(p8) if p8.exists() else {}
    bc = the.get("bo_cuc_slide") or {}
    co = {x["id"] for x in thu_vien_bo_cuc().get("bo_cuc", [])}
    kieu = sorted({s_.get("kieu") for s_ in dk.get("slides", []) if s_.get("kieu")})
    thieu = [k for k in kieu if k not in bc]
    la = [f"{k}→{v}" for k, v in bc.items() if v not in co]
    if thieu:
        kq.sai(f"kiểu slide chưa chọn bố cục: {thieu} (deck.py bo-cuc chon <dir>)")
    if la:
        kq.sai(f"bố cục không có trong thư viện: {la}")


def lenh_bo_cuc(d, viec, kieu=None, ma=None, tep=None, nguon=None, loai=None, hop=None, chu_y=None):
    tv = thu_vien_bo_cuc()
    if viec == "ds":
        for x in tv["bo_cuc"]:
            print(f"- {x['id']}: {x['ten']} · hợp {', '.join(x.get('hop_voi', []))} · {x.get('chu_y', '')[:80]}")
        return
    if viec == "them":
        if not (ma and tep and nguon):
            raise SystemExit("bo-cuc them cần --ma, --tep (ảnh chụp slide), --nguon (link trang)")
        th = DU_LIEU / "bo-cuc"
        th.mkdir(exist_ok=True)
        f = Path(tep)
        dich = th / f"{ma}{f.suffix.lower()}"
        shutil.copy(f, dich)
        tv["bo_cuc"] = [x for x in tv["bo_cuc"] if x["id"] != ma] + [{
            "id": ma, "ten": ma, "loai": loai or "khac", "chu_y": chu_y or "", "hop_voi": (hop or "").split(",") if hop else [],
            "anh": f"du-lieu/bo-cuc/{dich.name}", "nguon": nguon, "luc": bay_gio(), "ghi_chu": "ảnh tham chiếu nội bộ"}]
        ghi_json(th / "thu-vien.json", tv)
        print(f"Đã thêm bố cục {ma}")
        return
    if viec == "chon":
        dk = doc_deck(d) or {}
        p8 = Path(d) / BUOC[8][1]
        the = doc_json(p8) if p8.exists() else {}
        bc = the.get("bo_cuc_slide") or {}
        if kieu and ma:
            bc[kieu] = ma
        else:
            for k in sorted({s_.get("kieu") for s_ in dk.get("slides", []) if s_.get("kieu")}):
                hop = [x["id"] for x in tv["bo_cuc"] if k in x.get("hop_voi", [])]
                if k not in bc and hop:
                    bc[k] = hop[0]
                if k in bc and bc[k] == "toan-trang" and "nen-mem" in hop:  # slide cùng kiểu mà không có ảnh: nền mềm
                    for s_ in dk.get("slides", []):
                        if s_.get("kieu") == k and not s_.get("anh"):
                            bc.setdefault(f"slide:{s_['id']}", "nen-mem")
        the["bo_cuc_slide"] = bc
        ghi_json(p8, the)
        for k, v in sorted(bc.items()):
            print(f"{k} → {v}")
        thieu = sorted({s_.get("kieu") for s_ in dk.get("slides", [])} - set(bc))
        if thieu:
            print(f"! chưa có bố cục cho {thieu}: thêm vào thư viện (bo-cuc them) hoặc chọn tay (bo-cuc chon --kieu K --ma ID)")
        return
    raise SystemExit("bo-cuc ds | them | chon")


# ---------------------------------------------------------------- thư viện ảnh neo theo brand

def thu_neo(brand):
    import os
    return Path(os.environ.get("LINHX_DECK_NEO") or DU_LIEU / "neo") / brand


def lenh_neo(d, lay, luu, ghi_de=False):
    dk = doc_deck(d) or {}
    brand = dk.get("brand") or trang_thai(d).get("brand") or "linhx"
    tn = thu_neo(brand)
    d = Path(d)
    if luu:
        neo = d / "11-goi-anh" / "anh" / "anh-neo.png"
        tp = d / BUOC[8][1]
        if not neo.exists() or not tp.exists():
            raise SystemExit("deck chưa có ảnh neo và thẻ phong cách để lưu")
        if tn.exists() and not ghi_de:
            raise SystemExit(f"brand {brand} đã có ảnh neo ở {tn}. Đổi phong cách brand chỉ khi Linh yêu cầu: thêm --ghi-de")
        if tn.exists():
            shutil.rmtree(tn)
        (tn / "moodboard").mkdir(parents=True)
        shutil.copy(neo, tn / "anh-neo.png")
        the = doc_json(tp)
        huong = next((h for h in the.get("huong", []) if h.get("id") == the.get("huong_chon")), {})
        giu = set(huong.get("anh") or []) | {x["tep"] for x in the.get("nguon_anh", [])}
        for t in giu:
            if (d / t).exists():
                shutil.copy(d / t, tn / "moodboard" / Path(t).name)
        if (d / "08-moodboard" / "nguon.json").exists():
            shutil.copy(d / "08-moodboard" / "nguon.json", tn / "nguon.json")
        the["neo_brand"] = {"brand": brand, "tu_deck": d.name, "luc": bay_gio()}
        ghi_json(tn / "the-phong-cach.json", the)
        ghi_json(tp, the)  # deck gốc của phong cách brand cũng mang dấu neo_brand (cổng 8 khỏi cảnh báo nhầm)
        print(f"Đã lưu phong cách brand {brand} vào {tn}: mọi deck sau của {brand} dùng chung ảnh neo này")
        return
    if lay:
        if not (tn / "anh-neo.png").exists():
            raise SystemExit(f"brand {brand} chưa có ảnh neo trong thư viện ({tn}). Làm bước 8 và 11 như thường rồi chạy neo --luu")
        (d / "08-moodboard").mkdir(exist_ok=True)
        for f in (tn / "moodboard").iterdir():
            shutil.copy(f, d / "08-moodboard" / f.name)
        if (tn / "nguon.json").exists():
            shutil.copy(tn / "nguon.json", d / "08-moodboard" / "nguon.json")
        the = doc_json(tn / "the-phong-cach.json")
        ghi_json(d / BUOC[8][1], the)
        (d / "11-goi-anh" / "anh").mkdir(parents=True, exist_ok=True)
        shutil.copy(tn / "anh-neo.png", d / "11-goi-anh" / "anh" / "anh-neo.png")
        huong = next((h for h in the.get("huong", []) if h.get("id") == the.get("huong_chon")), {})
        pk = d / NHAT_KY
        nk = doc_json(pk) if pk.exists() else {"anh": [], "lich_su": []}
        dong = {"tep": "anh-neo.png", "phien_ban": 1, "ref": list(huong.get("anh") or [])[:3], "nguon": f"neo-brand:{brand}",
                "luc": bay_gio(), "sha1": hashlib.sha1((tn / "anh-neo.png").read_bytes()).hexdigest()[:12]}
        nk["anh"] = [x for x in nk["anh"] if x["tep"] != "anh-neo.png"] + [dong]
        nk["lich_su"].append(dong)
        ghi_json(pk, nk)
        tt = trang_thai(d)
        tt.setdefault("duyet", {})["8"] = {"nguoi": f"neo-brand:{brand}", "luc": bay_gio(), "ghi_chu": "phong cách brand đã duyệt ở deck trước"}
        luu_trang_thai(d, tt)
        print(f"Đã lấy phong cách brand {brand}: moodboard, thẻ phong cách, ảnh neo. Bước 8 xong; sang goi-anh")
        return
    print(f"Thư viện neo {brand}: {'có' if (tn / 'anh-neo.png').exists() else 'chưa có'} ({tn})")


# ---------------------------------------------------------------- lệnh còn lại

def lenh_moi(d, brand, ten):
    d = Path(d)
    if (d / "trang-thai.json").exists():
        raise SystemExit(f"{d} đã có deck. Dùng: deck.py trang-thai {d}")
    thuong_hieu(brand)
    d.mkdir(parents=True, exist_ok=True)
    for f in MAU.iterdir():
        if f.name.startswith("14-"):
            (d / "14-prototype").mkdir(exist_ok=True)
            shutil.copy(f, d / "14-prototype" / "README.md")
        elif f.name.startswith("15-"):
            (d / "15-ban-giao").mkdir(exist_ok=True)
            shutil.copy(f, d / "15-ban-giao" / "README.md")
        elif f.is_file():
            shutil.copy(f, d / f.name)
    (d / "08-moodboard").mkdir(exist_ok=True)
    (d / "11-goi-anh" / "anh").mkdir(parents=True, exist_ok=True)
    p8 = d / "08-the-phong-cach.json"
    s8 = doc_json(p8)
    s8["brand"] = brand
    ghi_json(p8, s8)
    ghi_json(d / "10-deck.json", {"ten": ten, "brand": brand, "chan_trang": "", "khach": "", "slides": []})
    if logo_goc_brand(brand):
        lenh_logo(d)
    if (thu_neo(brand) / "anh-neo.png").exists():
        lenh_neo(d, lay=True, luu=False)
    luu_trang_thai(d, {"ten": ten, "brand": brand, "tao_luc": bay_gio(), "duyet": {}, "cong": {}, "link_deck": None})
    print(f"Đã tạo deck '{ten}' ({brand}) ở {d}")


def lenh_trang_thai(d):
    tt = trang_thai(d)
    print(f"Deck: {tt.get('ten')} · brand {tt.get('brand')} · link {tt.get('link_deck') or '-'}")
    print("| # | Bước | Tệp | Cổng | Linh duyệt |")
    print("|---|---|---|---|---|")
    tiep = None
    for n, (ten, tep) in BUOC.items():
        co = (Path(d) / tep).exists()
        kq = chay_cong(d, n, im_lang=True)
        dy = tt.get("duyet", {}).get(str(n))
        cd = "đạt" if kq.dat else f"{len(kq.loi)} lỗi"
        print(f"| {n} | {ten} | {'có' if co else '-'} | {cd} | {(dy or {}).get('nguoi', '-') if n in CAN_DUYET else ''} |")
        if tiep is None and not kq.dat:
            tiep = n
    print(f"\nBước cần làm tiếp: {tiep or 'xong cả 15 bước'}")
    can = []
    p1 = Path(d) / BUOC[1][1]
    if p1.exists():
        can += [f"01 chốt tối thiểu: {k}" for k, v in chot_toi_thieu(p1.read_text(encoding="utf-8")).items() if v != "chot"]
    for s_ in (doc_deck(d) or {}).get("slides", []):
        for m in re.findall(r"\[(?:CẦN LINH[^\]]*|Linh chốt[^\]]*)\]", chu_slide(s_)):
            can.append(f"slide {s_.get('id')}: {m}")
    if can:
        print(f"\nLinh cần chốt ({len(can)}):")
        for c in can:
            print(f"- {c}")


PHUT_TU_DUYET = 10


def van_buoc(d, n):
    """Dấu vân tệp của bước n (để biết nội dung đổi sau khi đã hỏi Linh)."""
    tep = [Path(d) / BUOC[n][1]]
    if n == 10:  # Linh duyệt ghost deck + hành trình chú ý + deck
        tep = [Path(d) / f for f in ("10-deck.json", "10-ghost-deck.md", "10-hanh-trinh.json")]
    h = hashlib.sha1()
    co = False
    for f in tep:
        if f.exists() and f.is_file():
            h.update(f.read_bytes())
            co = True
    return h.hexdigest()[:12] if co else None


def van_tung_tep(d, n):
    """Vân từng tệp của bước n. So theo từng tệp đã ghi lúc hỏi, nên đổi cách tính vân của plugin
    (thêm tệp vào danh sách) không làm hỏng một lần hỏi cũ khi nội dung không đổi."""
    ten = [BUOC[n][1]] if n != 10 else ["10-deck.json", "10-ghost-deck.md", "10-hanh-trinh.json"]
    return {f: hashlib.sha1((Path(d) / f).read_bytes()).hexdigest()[:12]
            for f in ten if (Path(d) / f).is_file()}


def lenh_hoi(d, n, cau):
    """Ghi câu hỏi + khuyến nghị đã gửi Linh và giờ hỏi: mốc để luật 10 phút kiểm được."""
    tt = trang_thai(d)
    tt.setdefault("hoi", {})[str(n)] = {"cau": cau, "luc": bay_gio(), "van": van_buoc(d, n), "van_tep": van_tung_tep(d, n)}
    luu_trang_thai(d, tt)
    luc = (datetime.datetime.now() + datetime.timedelta(minutes=PHUT_TU_DUYET)).strftime("%H:%M")
    print(f"Đã ghi câu hỏi bước {n}. Linh im lặng tới {luc} ({PHUT_TU_DUYET} phút) thì: deck.py duyet <dir> {n} --nguoi tu-dong-10-phut. "
          "Sửa 10-deck/ghost/hành trình trong lúc chờ thì phải hỏi lại.")


def lenh_duyet(d, n, nguoi, link=None, bo_qua=None):
    tt = trang_thai(d)
    if bo_qua:
        tt.setdefault("bo_qua", {})[str(n)] = {"ly_do": bo_qua, "luc": bay_gio()}
        luu_trang_thai(d, tt)
        print(f"Đã ghi: bỏ qua bước {n} ({bo_qua})")
        return
    if n in CONG and n != 13:
        kq = chay_cong(d, n, im_lang=True, chi_noi_dung=True)
        if not kq.dat:
            raise SystemExit(f"cổng {n} còn lỗi nội dung, chưa xin duyệt được:\n  " + "\n  ".join(kq.loi[:8]))
    if nguoi.startswith("tu-dong"):
        hoi = (tt.get("hoi") or {}).get(str(n))
        if not hoi:
            raise SystemExit(f"tự duyệt cần câu hỏi đã gửi Linh: deck.py hoi <dir> {n} --cau \"<câu hỏi + khuyến nghị>\"")
        da = (datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.fromisoformat(hoi["luc"])).total_seconds() / 60
        if da < PHUT_TU_DUYET:
            raise SystemExit(f"mới hỏi Linh {da:.0f} phút trước; luật là im lặng {PHUT_TU_DUYET} phút mới tự duyệt")
        if hoi.get("van_tep"):
            nay = van_tung_tep(d, n)
            doi = [f for f, v in hoi["van_tep"].items() if nay.get(f) != v]
        else:
            doi = ["?"] if hoi.get("van") and hoi["van"] != van_buoc(d, n) else []
        if doi:
            raise SystemExit(f"tệp bước {n} đã đổi sau khi hỏi Linh: hỏi lại (deck.py hoi) với bản mới rồi chờ {PHUT_TU_DUYET} phút")
    muc = {"nguoi": nguoi, "luc": bay_gio()}
    if n == 10:
        muc["van_tieu_de"] = van_tieu_de(d)
        muc["van_v3"] = True
    if (tt.get("hoi") or {}).get(str(n)):
        muc["cau_hoi"] = tt["hoi"][str(n)]
    tt.setdefault("duyet", {})[str(n)] = muc
    if link:
        tt["link_deck"] = link
    luu_trang_thai(d, tt)
    print(f"Đã ghi: bước {n} duyệt bởi {nguoi}" + (f", link {link}" if link else ""))


def main():
    ap = argparse.ArgumentParser(description="linhx-deck: quy trình 15 bước deck proposal")
    sp = ap.add_subparsers(dest="lenh", required=True)
    a = sp.add_parser("moi"); a.add_argument("dir"); a.add_argument("--brand", default="linhx"); a.add_argument("--ten", required=True)
    for ten in ("trang-thai", "doi-chieu", "ghost", "goi-anh", "ra-anh", "sua-anh", "xem"):
        sp.add_parser(ten).add_argument("dir")
    a = sp.add_parser("cong"); a.add_argument("dir"); a.add_argument("n", type=int)
    a = sp.add_parser("duyet"); a.add_argument("dir"); a.add_argument("n", type=int); a.add_argument("--nguoi", default="Linh"); a.add_argument("--link")
    a.add_argument("--bo-qua", help="lý do bỏ qua bước này")
    a = sp.add_parser("hoi"); a.add_argument("dir"); a.add_argument("n", type=int); a.add_argument("--cau", required=True)
    a = sp.add_parser("kiem-deck"); a.add_argument("dir"); a.add_argument("--ban-cuoi", action="store_true")
    a = sp.add_parser("xuat"); a.add_argument("dir"); a.add_argument("--anh-map"); a.add_argument("--logo")
    a = sp.add_parser("logo"); a.add_argument("dir"); a.add_argument("--ta"); a.add_argument("--khach"); a.add_argument("--khach-ten")
    a.add_argument("--nguon", help="link/tệp gốc của logo khách"); a.add_argument("--tu-tep", help="pptx/docx để rút ảnh nhúng")
    a = sp.add_parser("bo-cuc"); a.add_argument("viec", choices=["ds", "them", "chon"]); a.add_argument("dir", nargs="?")
    for k in ("--kieu", "--ma", "--tep", "--nguon", "--loai", "--hop", "--chu-y"):
        a.add_argument(k)
    a = sp.add_parser("hanh-trinh"); a.add_argument("dir")
    a = sp.add_parser("neo"); a.add_argument("dir"); a.add_argument("--lay", action="store_true"); a.add_argument("--luu", action="store_true")
    a.add_argument("--ghi-de", action="store_true")
    a = sp.add_parser("tai-anh"); a.add_argument("dir"); a.add_argument("--ds", required=True)
    a = sp.add_parser("nhan-anh"); a.add_argument("dir"); a.add_argument("--tu", default=str(Path.home() / "Downloads"))
    a.add_argument("--vao", choices=["moodboard", "anh"], required=True); a.add_argument("--ten"); a.add_argument("--ref")
    a.add_argument("--nguon"); a.add_argument("--phut", type=int, default=20)
    g = ap.parse_args()
    if g.lenh == "moi":
        lenh_moi(g.dir, g.brand, g.ten)
    elif g.lenh == "trang-thai":
        lenh_trang_thai(g.dir)
    elif g.lenh == "cong":
        kq = chay_cong(g.dir, g.n)
        sys.exit(0 if kq.dat else (3 if kq.cho_duyet else 1))
    elif g.lenh == "duyet":
        lenh_duyet(g.dir, g.n, g.nguoi, g.link, g.bo_qua)
    elif g.lenh == "hoi":
        lenh_hoi(g.dir, g.n, g.cau)
    elif g.lenh == "doi-chieu":
        kq = KetQua(6); cong_6(g.dir, kq, in_bang=True); kq.in_ra(); sys.exit(0 if kq.dat else 1)
    elif g.lenh == "ghost":
        lenh_ghost(g.dir)
    elif g.lenh == "kiem-deck":
        kq = KetQua(10); kiem_deck(g.dir, kq, g.ban_cuoi); kq.in_ra(); sys.exit(0 if kq.dat else 1)
    elif g.lenh == "goi-anh":
        lenh_goi_anh(g.dir)
    elif g.lenh == "ra-anh":
        lenh_ra_anh(g.dir)
    elif g.lenh == "xuat":
        lenh_xuat(g.dir, g.anh_map, g.logo)
    elif g.lenh == "tai-anh":
        lenh_tai_anh(g.dir, g.ds)
    elif g.lenh == "nhan-anh":
        lenh_nhan_anh(g.dir, g.tu, g.vao, g.ten, g.ref, g.nguon, g.phut)
    elif g.lenh == "sua-anh":
        lenh_sua_anh(g.dir)
    elif g.lenh == "xem":
        sys.exit(0 if lenh_xem(g.dir) else 1)
    elif g.lenh == "logo":
        if g.tu_tep:
            lenh_logo_tu_tep(g.dir, g.tu_tep)
        else:
            lenh_logo(g.dir, g.ta, g.khach, g.khach_ten, g.nguon)
    elif g.lenh == "bo-cuc":
        lenh_bo_cuc(g.dir, g.viec, g.kieu, g.ma, g.tep, g.nguon, g.loai, g.hop, g.chu_y)
    elif g.lenh == "hanh-trinh":
        kq = KetQua(10); kiem_hanh_trinh(g.dir, kq); kq.in_ra(); ve_hanh_trinh(g.dir); sys.exit(0 if kq.dat else 1)
    elif g.lenh == "neo":
        lenh_neo(g.dir, g.lay, g.luu, g.ghi_de)


if __name__ == "__main__":
    main()
