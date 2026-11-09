"""Máy đo thử WF10 (nấc 1, cloud 9/11). Một file .md chiến lược vào, ra JSON chỉ số.
Chạy: python do_chien_luoc.py <file.md> [--hat 1]
Không thay kiem.py; là bản thử để chọn kiểm nào đáng nạp vào loai.json/kiem.py.
"""
import json, random, re, sys, unicodedata

MUC_BAT_BUOC = {
    "chan_doan": r"chẩn đoán",
    "khong_lam": r"không làm|sẽ không|không chơi|bỏ qua có chủ đích",
    "gia": r"\bgiá\b",
    "go_no_go": r"go/no-go|go / no-go|cổng go",
    "phai_dung": r"điều gì phải đúng|phải đúng|giả định",
    "tieu_chi_giet": r"tiêu chí (giết|dừng)|ngưỡng dừng|trượt thì",
    "doi_thu_hon": r"đối thủ (hơn|mạnh hơn)|chỗ (họ|đối thủ) hơn",
}
# Từ sáo hay gặp ở bản chiến lược AI (cờ Rumelt "nói suông"); đếm trên 1.000 chữ
SAO = ["đột phá", "toàn diện", "tối ưu", "hàng đầu", "chiếm lĩnh", "vượt trội", "bứt phá",
       "hệ sinh thái", "trải nghiệm liền mạch", "giá trị cốt lõi", "chiến lược then chốt", "kim chỉ nam"]

def chuan(s):
    return unicodedata.normalize("NFC", s).lower()

def dong_co_so(text):
    out = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s or s.startswith("#") or s.startswith("|---"):
            continue
        bo = re.sub(r"\[BC-\d+\]|BC-\d+|`[^`]*`|\d{1,2}/\d{1,2}(/\d{2,4})?|20\d\d|V\d+(\.\d+)?|P\d\d|TH-\d+|NC\d+", "", s)
        if re.search(r"\d", bo):
            out.append(s)
    return out

def main(argv):
    p = argv[0]
    hat = int(argv[argv.index("--hat") + 1]) if "--hat" in argv else 1
    t = open(p, encoding="utf-8").read()
    tc = chuan(t)
    chu = len(re.findall(r"\w+", tc))
    dong = dong_co_so(t)
    co_bc = [d for d in dong if re.search(r"\[BC-\d+\]", d)]
    cau = [c for c in re.split(r"(?<=[.!?])\s+|\n", t) if len(c.split()) > 2]
    dai = sorted((len(c.split()) for c in cau), reverse=True)
    bcs = sorted(set(re.findall(r"BC-\d+", t)))
    random.seed(hat)
    kq = {
        "file": p,
        "so_chu": chu,
        "muc": {k: bool(re.search(v, tc)) for k, v in MUC_BAT_BUOC.items()},
        "dong_co_so": len(dong),
        "ty_le_so_co_nguon": round(len(co_bc) / len(dong), 2) if dong else None,
        "vi_du_so_khong_nguon": [d[:160] for d in dong if d not in co_bc][:5],
        "tu_sao_tren_1000_chu": round(sum(tc.count(w) for w in SAO) * 1000 / max(chu, 1), 2),
        "cau_dai_nhat_chu": dai[:3],
        "ty_le_cau_tren_40_chu": round(sum(1 for d in dai if d > 40) / max(len(dai), 1), 2),
        "bc_mo_ngau_nhien": random.sample(bcs, min(5, len(bcs))),
    }
    nguong = {"ty_le_so_co_nguon": 0.9, "tu_sao_tren_1000_chu": 2.0, "ty_le_cau_tren_40_chu": 0.15}
    loi = []
    if kq["ty_le_so_co_nguon"] is not None and kq["ty_le_so_co_nguon"] < nguong["ty_le_so_co_nguon"]:
        loi.append("số thiếu nguồn")
    if kq["tu_sao_tren_1000_chu"] > nguong["tu_sao_tren_1000_chu"]:
        loi.append("nhiều từ sáo")
    if kq["ty_le_cau_tren_40_chu"] > nguong["ty_le_cau_tren_40_chu"]:
        loi.append("câu quá dài")
    kq["nguong"] = nguong
    kq["loi"] = loi
    print(json.dumps(kq, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main(sys.argv[1:])
