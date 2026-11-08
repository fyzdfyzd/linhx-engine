#!/usr/bin/env python3
"""kiem_van.py - đo giọng và soát dấu hiệu giọng AI cho bài tiếng Việt của Linh.

Chỉ dùng thư viện chuẩn Python 3.8+. Chạy được trên Windows.

Lệnh:
  python kiem_van.py do-giong <thu-muc-hoac-file...> -o moc.json
      Đo "dấu vân tay" giọng từ các bài mẫu (.md/.txt): độ dài câu, độ dài đoạn,
      tỉ lệ "tôi"/"chúng ta", gạch ngang, chữ số, câu hỏi, câu ngắn đứng riêng...
  python kiem_van.py kiem <bai.md> [--moc moc.json] [--json]
      Soát bài nháp: liệt kê dấu hiệu giọng AI (AP-01..AP-20) theo dòng,
      so chỉ số với mốc giọng của Linh, cho điểm 0-100.

Không thay được người đọc. Điểm cao chỉ có nghĩa là bài không mắc lỗi máy móc;
giọng hay hay dở vẫn do Linh chấm.
"""
import argparse
import json
import math
import os
import re
import statistics
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------- tách văn bản

FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.S)


def doc_file(duong_dan):
    with open(duong_dan, encoding="utf-8", errors="replace") as f:
        t = f.read()
    return FRONTMATTER.sub("", t)


def tach_doan(van_ban):
    """Đoạn văn xuôi: bỏ tiêu đề, dòng kẻ, dòng trống, trích dẫn nguồn."""
    doan = []
    for khoi in re.split(r"\n\s*\n", van_ban):
        khoi = khoi.strip()
        if not khoi or re.fullmatch(r"[-*_]{3,}", khoi):
            continue
        if khoi.startswith("#"):
            continue
        doan.append(khoi)
    return doan


CAU_RE = re.compile(r"(?<=[.!?…])[\"”’)]*\s+(?=[\"“‘(]?[A-ZÀ-Ỹ0-9])")


def tach_cau(doan):
    t = re.sub(r"\s+", " ", doan.replace("*", "").replace("_", " ")).strip()
    if not t:
        return []
    return [c.strip() for c in CAU_RE.split(t) if c.strip()]


def dem_tu(cau):
    return len(re.findall(r"[0-9A-Za-zÀ-ỹđĐ]+", cau))


# ---------------------------------------------------------------- dấu hiệu AI

# (mã, tên, regex, gợi ý sửa). Regex chạy trên từng dòng, không phân biệt hoa thường.
DAU_HIEU = [
    ("AP-19", "Mở bài zoom từ vũ trụ",
     r"^\W*(trong bối cảnh|trong thời đại|trong thế giới|trong kỷ nguyên|ngày nay,|hiện nay,|thế kỷ 21)",
     "Mở bằng cảnh, người, con số hoặc câu tự thú cụ thể."),
    ("AP-03", "Đối lập giả 'không chỉ… mà còn'",
     r"không chỉ (là )?[^.!?]{0,80}?mà còn", "Nói thẳng một vế, bỏ vế làm nền."),
    ("AP-03", "Đối lập giả 'không phải… mà là'",
     r"không (phải|đơn thuần|chỉ đơn giản) (là )?[^.!?]{0,60}?(mà là|—|-) ",
     "Linh chỉ lật khi vế đầu là điều người đọc thật sự tin."),
    ("AP-20", "Giọng MC 'hãy cùng'",
     r"\b(hãy cùng|cùng khám phá|bạn đã sẵn sàng|đừng bỏ lỡ|cùng tìm hiểu)", "Bỏ, đi thẳng vào chuyện."),
    ("AP-08", "Kết giả triết lý",
     r"(điều (mà )?chúng ta cần suy ngẫm|hành trình (ý nghĩa|phía trước)|hãy sống chậm|suy cho cùng|rốt cuộc thì)",
     "Kết bằng cú lật hoặc hình ảnh mở bài quay lại (dark twist)."),
    ("AP-01", "Giọng bán rắn",
     r"(rõ ràng cho thấy|không thể phủ nhận|chắc chắn rằng|hoàn toàn có thể khẳng định)",
     "Thêm vết xước: điều mình không chắc, ví dụ mình từng sai."),
    ("AP-05", "Vòng 'nói cách khác'", r"\b(nói cách khác|hay nói đúng hơn|tức là nói)\b",
     "Nếu câu trước đã rõ thì xóa câu sau."),
    ("AP-09", "Né bất định",
     r"(theo nhiều nguồn|nhiều chuyên gia cho rằng|có thể thấy rằng|người ta thường nói)",
     "Nêu tên nguồn, hoặc nói 'tôi không biết'."),
    ("AP-11", "Từ ghép trừu tượng rỗng",
     r"(giải pháp (tích hợp|toàn diện)|hệ sinh thái toàn diện|bức tranh toàn cảnh|khía cạnh thiết yếu|bước tiến quan trọng|tác động đa chiều|chìa khóa (vàng|thành công)|đóng vai trò then chốt|mang tính đột phá)",
     "Thay bằng vật, việc, số cụ thể."),
    ("AP-12", "Động từ hóa danh từ", r"\b(đột phá hóa|nâng tầm hóa|tối ưu hóa hóa|số hóa hóa)\b", "Bỏ '-hóa' thừa."),
    ("AP-14", "Từ nối văn mẫu đầu câu",
     r"(^|[.!?]\s+)(tuy nhiên|hơn nữa|bên cạnh đó|ngoài ra|đặc biệt là|không những thế|có thể nói),",
     "Linh nối bằng mạch kể, không bằng từ nối."),
    ("AP-16", "Đồng thuận ép", r"(dù (có )?nhiều ý kiến khác nhau|song nhìn chung|mỗi bên đều có lý)",
     "Chọn phe, nói rõ vì sao."),
    ("AP-17", "Làm mềm cảm xúc", r"(thách thức cần vượt qua|cơ hội để chúng ta|bài học quý giá|tỏa sáng)",
     "Gọi đúng tên: thất bại, mất, đau."),
    ("AP-18", "Khẳng định trơn", r"(góp phần định hình|tạo nên bức tranh|mở ra (một )?chương mới)",
     "Bỏ câu tổng kết; để chi tiết tự nói."),
    ("AP-06", "Số liệu mơ hồ", r"(hàng triệu dữ liệu|vài giây|vô số|hàng loạt|rất nhiều người)",
     "Một con số có nguồn, viết bằng chữ nếu là bài tản văn."),
    ("AP-10", "Giọng đại diện nhân loại", r"\b(loài người|nhân loại|toàn thế giới)\b",
     "Đổi sang 'tôi', 'thằng bạn tôi', một người có tên."),
    ("EN", "Từ trigger dịch từ tiếng Anh",
     r"\b(delve|tapestry|leverage|landscape|navigate|robust|pivotal|foster|game.?changer)\b",
     "Viết bằng tiếng Việt thường ngày."),
]

EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐✅]")
BULLET_RE = re.compile(r"^\s*([-*•]|\d+[.)])\s+")
GACH_RE = re.compile(r"\s[—–]\s|—")
CHU_SO_RE = re.compile(r"(?<![\w/.-])\d+([.,]\d+)?(?![\w/])")
NAM_RE = re.compile(r"^(1[89]\d\d|20\d\d)$")
HOI_RE = re.compile(r"\?\s*$")


# ---------------------------------------------------------------- đo giọng

def do_chi_so(van_ban):
    doan = tach_doan(van_ban)
    cau = [c for d in doan for c in tach_cau(d)]
    do_dai_cau = [dem_tu(c) for c in cau if dem_tu(c) > 0]
    do_dai_doan = [dem_tu(d) for d in doan if dem_tu(d) > 0]
    tong_tu = sum(do_dai_doan) or 1
    thap = van_ban.lower()
    so = [m.group(0) for m in CHU_SO_RE.finditer(van_ban)]
    so_khong_nam = [s for s in so if not NAM_RE.match(s)]
    cau_ngan_rieng = sum(1 for d in doan if len(tach_cau(d)) == 1 and dem_tu(d) <= 8)
    dong = van_ban.splitlines()

    def moi_nghin(n):
        return round(n * 1000 / tong_tu, 2)

    def cv(xs):
        if len(xs) < 2:
            return 0.0
        m = statistics.mean(xs)
        return round(statistics.pstdev(xs) / m, 3) if m else 0.0

    return {
        "so_tu": tong_tu,
        "so_doan": len(doan),
        "so_cau": len(cau),
        "cau_tb": round(statistics.mean(do_dai_cau), 1) if do_dai_cau else 0,
        "cau_trung_vi": statistics.median(do_dai_cau) if do_dai_cau else 0,
        "cau_dai_nhat": max(do_dai_cau) if do_dai_cau else 0,
        "ti_le_cau_tren_35_tu": round(sum(1 for x in do_dai_cau if x > 35) / max(len(do_dai_cau), 1), 3),
        "ti_le_cau_duoi_8_tu": round(sum(1 for x in do_dai_cau if x < 8) / max(len(do_dai_cau), 1), 3),
        "doan_tb": round(statistics.mean(do_dai_doan), 1) if do_dai_doan else 0,
        "doan_cv": cv(do_dai_doan),
        "cau_ngan_dung_rieng_moi_1000": moi_nghin(cau_ngan_rieng),
        "toi_moi_1000": moi_nghin(len(re.findall(r"\btôi\b", thap))),
        "chung_ta_moi_1000": moi_nghin(len(re.findall(r"\bchúng ta\b", thap))),
        "ban_moi_1000": moi_nghin(len(re.findall(r"\bbạn\b", thap))),
        "gach_ngang_moi_1000": moi_nghin(len(GACH_RE.findall(van_ban))),
        "chu_so_moi_1000": moi_nghin(len(so_khong_nam)),
        "cau_hoi_moi_1000": moi_nghin(sum(1 for c in cau if HOI_RE.search(c))),
        "dong_gach_dau_dong": sum(1 for l in dong if BULLET_RE.match(l)),
        "emoji": len(EMOJI_RE.findall(van_ban)),
        "ngoac_kep_moi_1000": moi_nghin(len(re.findall(r"[\"“]", van_ban))),
    }


def soat_dau_hieu(van_ban):
    loi = []
    dong = van_ban.splitlines()
    dong_dau_tien = next((i for i, l in enumerate(dong) if l.strip() and not l.startswith("#")), 0)
    for i, l in enumerate(dong, 1):
        # bỏ phần trong ngoặc kép: thường là câu nhại giọng AI hoặc trích dẫn, không phải lời Linh
        thap = re.sub(r'"[^"]*"|“[^”]*”', lambda m: " " * len(m.group(0)), l).lower()
        for ma, ten, mau, goi_y in DAU_HIEU:
            if ma == "AP-19" and i - 1 > dong_dau_tien + 2:
                continue  # chỉ soát mở bài ở vài dòng đầu
            for m in re.finditer(mau, thap, re.M):
                loi.append({"dong": i, "ma": ma, "ten": ten, "trich": l.strip()[max(0, m.start() - 20):m.end() + 30],
                            "goi_y": goi_y})
        if EMOJI_RE.search(l):
            loi.append({"dong": i, "ma": "AP-20", "ten": "Emoji trong bài", "trich": l.strip()[:60],
                        "goi_y": "Bài của Linh không dùng emoji."})
    return loi


# ---------------------------------------------------------------- so với mốc

SO_MOC = [
    # (chỉ số, chiều tốt: "gan" = càng gần mốc càng tốt, "it" = càng ít càng tốt), ngưỡng lệch cho phép (tỉ lệ)
    ("cau_tb", "gan", 0.35),
    ("ti_le_cau_tren_35_tu", "gan", 0.6),
    ("doan_cv", "gan", 0.5),
    ("toi_moi_1000", "gan", 0.7),
    ("chung_ta_moi_1000", "it", 0.7),
    ("gach_ngang_moi_1000", "it", 0.7),
    ("chu_so_moi_1000", "gan", 0.8),
    ("cau_hoi_moi_1000", "gan", 0.8),
]


def so_moc(chi_so, moc):
    nhan_xet = []
    for ten, chieu, nguong in SO_MOC:
        if ten not in moc or ten not in chi_so:
            continue
        m, x = moc[ten], chi_so[ten]
        if not m:
            continue
        lech = (x - m) / m
        if chieu == "it" and lech <= nguong:
            continue
        if chieu == "gan" and abs(lech) <= nguong:
            continue
        nhan_xet.append({"chi_so": ten, "bai": x, "moc_linh": m, "lech_phan_tram": round(lech * 100)})
    return nhan_xet


# Trọng số trừ điểm. Linh cũng thỉnh thoảng dùng "không chỉ… mà còn" hay "rất nhiều người",
# nên các mã đó trừ nhẹ; mở bài vũ trụ, giọng MC, emoji trừ nặng.
TRONG_SO = {"AP-03": 2, "AP-06": 1, "AP-10": 2, "AP-14": 3, "AP-19": 8, "AP-20": 6, "AP-08": 6}


def cham_diem(loi, chi_so, lech):
    diem = 100
    diem -= sum(TRONG_SO.get(l["ma"], 4) for l in loi)
    diem -= 3 * len(lech)
    if chi_so["dong_gach_dau_dong"] > 0:
        diem -= min(15, 3 * chi_so["dong_gach_dau_dong"])
    return max(0, diem)


# ---------------------------------------------------------------- lệnh

def gom_file(duong_dan):
    out = []
    for p in duong_dan:
        if os.path.isdir(p):
            for goc, _, ten in os.walk(p):
                out += [os.path.join(goc, t) for t in sorted(ten) if t.endswith((".md", ".txt"))
                        and not t.upper().startswith(("DANH-MUC", "README"))]
        else:
            out.append(p)
    return out


def lenh_do_giong(args):
    files = gom_file(args.nguon)
    if not files:
        sys.exit("Không thấy bài mẫu .md/.txt nào.")
    tung_bai = {}
    for f in files:
        tung_bai[os.path.basename(f)] = do_chi_so(doc_file(f))
    khoa = [k for k in next(iter(tung_bai.values())) if k not in ("so_tu", "so_doan", "so_cau")]
    moc = {k: round(statistics.median(b[k] for b in tung_bai.values()), 3) for k in khoa}
    moc["_so_bai"] = len(tung_bai)
    moc["_tong_tu"] = sum(b["so_tu"] for b in tung_bai.values())
    ket_qua = {"moc": moc, "tung_bai": tung_bai}
    with open(args.o, "w", encoding="utf-8") as f:
        json.dump(ket_qua, f, ensure_ascii=False, indent=2)
    print(f"Đã đo {len(tung_bai)} bài, {moc['_tong_tu']} từ -> {args.o}")
    for k in khoa:
        print(f"  {k:32s} {moc[k]}")


def lenh_kiem(args):
    van_ban = doc_file(args.bai)
    chi_so = do_chi_so(van_ban)
    loi = soat_dau_hieu(van_ban)
    lech = []
    if args.moc:
        with open(args.moc, encoding="utf-8") as f:
            moc = json.load(f)
        lech = so_moc(chi_so, moc.get("moc", moc))
    diem = cham_diem(loi, chi_so, lech)
    if args.json:
        print(json.dumps({"diem": diem, "chi_so": chi_so, "dau_hieu_ai": loi, "lech_moc": lech},
                         ensure_ascii=False, indent=2))
        return
    print(f"# Soát giọng: {os.path.basename(args.bai)}  ·  điểm máy {diem}/100\n")
    print(f"{chi_so['so_tu']} từ · {chi_so['so_doan']} đoạn · câu TB {chi_so['cau_tb']} từ · "
          f"'tôi' {chi_so['toi_moi_1000']}/1000 từ · gạch ngang {chi_so['gach_ngang_moi_1000']}/1000 từ\n")
    if chi_so["dong_gach_dau_dong"]:
        print(f"- {chi_so['dong_gach_dau_dong']} dòng gạch đầu dòng: bài báo/tản văn của Linh viết văn xuôi liền.\n")
    if loi:
        print("## Dấu hiệu giọng AI")
        for l in loi:
            print(f"- dòng {l['dong']} [{l['ma']}] {l['ten']}: «{l['trich']}» → {l['goi_y']}")
        print()
    if lech:
        print("## Lệch so với giọng Linh")
        for x in lech:
            print(f"- {x['chi_so']}: bài {x['bai']} / mốc Linh {x['moc_linh']} ({x['lech_phan_tram']:+d}%)")
        print()
    if not loi and not lech:
        print("Không thấy lỗi máy móc. Việc còn lại là Linh đọc to một lượt.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="lenh", required=True)
    a = sub.add_parser("do-giong", help="đo mốc giọng từ bài mẫu")
    a.add_argument("nguon", nargs="+")
    a.add_argument("-o", default="moc-giong.json")
    a.set_defaults(f=lenh_do_giong)
    b = sub.add_parser("kiem", help="soát một bài nháp")
    b.add_argument("bai")
    b.add_argument("--moc")
    b.add_argument("--json", action="store_true")
    b.set_defaults(f=lenh_kiem)
    args = ap.parse_args()
    args.f(args)


if __name__ == "__main__":
    main()
