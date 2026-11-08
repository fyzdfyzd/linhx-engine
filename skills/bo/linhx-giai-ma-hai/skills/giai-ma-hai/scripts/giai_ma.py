#!/usr/bin/env python3
"""LAB088 - kiểm, gom khuôn, xuất thủ pháp cho LAB087, 0 token.

  python giai_ma.py kiem <thu-muc-mau>
  python giai_ma.py gom <thu-muc-mau>        # -> KHUON.md cạnh thư mục mẫu
  python giai_ma.py xuat087 <thu-muc-mau>    # -> THU-PHAP-CHO-087.md + thu-phap-087.json
  python giai_ma.py doi-chieu <thu-muc-mau> <duong-dan-LAB087/src>
"""
import json, os, sys, glob, math, subprocess
from collections import defaultdict

SO_LOAI = {"that-gia", "binh-thuong-bat-thuong", "co-khong", "sang-hen", "tuc-thanh",
           "nghiem-dua", "nguoi-lon-tre-con", "ta-ho"}
LM = {"dao-vai", "suy-dien-sai", "ghep-nham-nghia", "nghia-den", "phong-dai", "cu-the-hoa",
      "ha-cap", "nhai-giong", "lap-leo-thang", "doi-cho", "tu-mau-thuan", "lech-ngu-vuc"}
NS = {"ke-chuyen", "hoi-dap", "doi-thoai", "mot-cau", "hinh", "clip-dien", "chu-tren-hinh"}
TP = {"lech-ky-vong", "vi-pham-lanh-tinh", "uu-the", "giai-toa"}
# Thủ pháp chữ: mô tả cho LAB087 + trạng thái luật bên LAB087.
LA = {
    "khong": ("Không có thủ pháp chữ, hài nằm ở tình huống.", "khong"),
    "noi-lai": ("Hoán vần/thanh giữa hai âm tiết ra nghĩa thứ hai.", "da-co-luat: lai.py"),
    "dong-am": ("Một chữ hai nghĩa, ngữ cảnh kéo sang nghĩa kia.", "can-luat-moi: từ điển có nghĩa"),
    "gieo-van": ("Hai vế cùng vần Việt, cùng bằng/trắc.", "da-co-luat: van.py viet"),
    "gieo-van-viet-anh": ("Vế Việt vần với vế Anh.", "da-co-luat: van.py ghep"),
    "viet-hoa-phien-am": ("Đọc từ/cụm tiếng Anh bằng âm tiết Việt có dấu, viết lại như chữ Việt. "
                          "Vần lấy theo âm Anh, phụ âm đầu có thể bị đồng hoá với âm tiết sau.",
                          "can-luat-moi: van.py có vần, thiếu luật phụ âm đầu"),
    "bien-am-genz": ("Biến âm một từ Việt quen theo kiểu nói nhõng/lười: đổi vần hoặc phụ âm.",
                     "can-luat-moi: bảng biến âm"),
    "che-thanh-ngu": ("Giữ khung thành ngữ/ca dao, thay một vế.", "can-luat-moi: kho thành ngữ"),
    "che-loi-bai-hat": ("Giữ giai điệu, số âm tiết và thanh, thay lời.", "can-llm"),
    "giong-vung-mien": ("Viết theo phát âm vùng miền.", "can-luat-moi: bảng phương âm"),
    "tron-viet-anh": ("Chèn từ Anh vào câu Việt.", "can-llm"),
    "lap-am": ("Lặp âm tiết hoặc láy để tạo nhịp.", "can-luat-moi: láy (bảng 087 #4)"),
}


def load(d):
    out = []
    for p in sorted(glob.glob(os.path.join(d, "*.json"))):
        with open(p, encoding="utf-8") as f:
            out.append((os.path.basename(p), json.load(f)))
    return out


def loi(m):
    e = []
    g, n = m.get("gtvh", {}), m.get("nguon", {})
    if not n.get("ngay"):
        e.append("thiếu nguon.ngay")
    if g.get("so_loai") not in SO_LOAI:
        e.append(f"so_loai lạ: {g.get('so_loai')}")
    if g.get("lm") not in LM:
        e.append(f"lm lạ: {g.get('lm')}")
    if g.get("ns") not in NS:
        e.append(f"ns lạ: {g.get('ns')}")
    if (g.get("la") or {}).get("thu_phap") not in LA:
        e.append(f"la.thu_phap lạ: {(g.get('la') or {}).get('thu_phap')}")
    if len(g.get("so") or []) != 2:
        e.append("so phải có đúng 2 kịch bản")
    for t in m.get("vi_sao_hai", {}).get("truong_phai", []):
        if t not in TP:
            e.append(f"truong_phai lạ: {t}")
    return e


def diem_lan(m):
    s = (m.get("nguon", {}).get("so_lieu") or {})
    v, sh = s.get("view"), s.get("share")
    if not v:
        return None
    return round(math.log10(v) + (10 * sh / v if sh else 0), 2)  # log view + thưởng tỉ lệ share


def cmd_kiem(d):
    bad = 0
    for name, m in load(d):
        e = loi(m)
        bad += bool(e)
        print(f"{'LOI ' if e else 'OK  '} {name}" + ("".join(f"\n      - {x}" for x in e)))
    return bad


def cmd_gom(d):
    nhom = defaultdict(list)
    for _, m in load(d):
        g = m["gtvh"]
        nhom[(g["so_loai"], g["lm"])].append(m)
    rows = ["# Khuôn gom từ mẫu", "",
            "| Đối lập | Cơ chế | Số mẫu | Điểm lan TB | Câu khuôn điền được |", "|---|---|---|---|---|"]
    for (so, lm), ms in sorted(nhom.items(), key=lambda x: -len(x[1])):
        ds = [x for x in (diem_lan(m) for m in ms) if x is not None]
        tb = f"{sum(ds) / len(ds):.2f}" if ds else "chưa có số"
        kh = "; ".join(m["vi_sao_lan"]["khuon_dien"] for m in ms if m["vi_sao_lan"].get("khuon_dien")) or "không"
        rows.append(f"| {so} | {lm} | {len(ms)} | {tb} | {kh} |")
    path = os.path.join(os.path.dirname(os.path.abspath(d)), "KHUON.md")
    open(path, "w", encoding="utf-8").write("\n".join(rows) + "\n")
    print(f"{len(nhom)} khuôn -> {path}")


def cmd_xuat087(d):
    tp = defaultdict(list)
    for _, m in load(d):
        la = m["gtvh"]["la"]
        if la["thu_phap"] != "khong":
            tp[la["thu_phap"]].append({"id": m["id"], "goc": la.get("goc"), "ket_qua": la.get("ket_qua")})
    base = os.path.dirname(os.path.abspath(d))
    out = {k: {"mo_ta": LA[k][0], "trang_thai": LA[k][1], "vi_du": v} for k, v in tp.items()}
    json.dump(out, open(os.path.join(base, "thu-phap-087.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    md = ["# Thủ pháp chữ chuyển LAB087", "",
          "Mỗi thủ pháp: mô tả + ví dụ gốc → kết quả. Đủ 3 ví dụ mới nên viết luật.", ""]
    for k, v in out.items():
        md.append(f"## {k} ({v['trang_thai']})\n{v['mo_ta']}\n")
        md += [f"- {e['goc']} → {e['ket_qua']}  ({e['id']})" for e in v["vi_du"]]
        if len(v["vi_du"]) < 3:
            md.append(f"- *còn thiếu {3 - len(v['vi_du'])} ví dụ*")
        md.append("")
    open(os.path.join(base, "THU-PHAP-CHO-087.md"), "w", encoding="utf-8").write("\n".join(md))
    print(f"{len(out)} thủ pháp -> {base}/THU-PHAP-CHO-087.md")


# Biến thể chính tả coi như một (từ điển 087 dùng "giầy", người viết dùng "giày").
BIEN_THE = {"giầy": "giày", "tầu": "tàu", "giầu": "giàu", "mầu": "màu"}


def chuan(s):
    return " ".join(BIEN_THE.get(w, w) for w in s.lower().split())


def cmd_doi_chieu(d, src087):
    """Ví dụ nói lái trong mẫu: luật lai.py có sinh ra đúng kết quả không."""
    ok = tong = 0
    for _, m in load(d):
        la = m["gtvh"]["la"]
        if la["thu_phap"] != "noi-lai":
            continue
        tong += 1
        r = subprocess.run([sys.executable, os.path.join(src087, "lai.py"), "lai", la["goc"]],
                           capture_output=True, text=True)
        sinh = {chuan(line[25:].split(" [")[0]) for line in r.stdout.splitlines() if line.strip()}
        hit = chuan(la["ket_qua"]) in sinh
        ok += hit
        print(f"{'DAT ' if hit else 'TRUOT'} {la['goc']} -> {la['ket_qua']}  ({len(sinh)} cách lái sinh ra)")
    print(f"{ok}/{tong} ví dụ nói lái tái tạo được bằng luật LAB087")
    return tong - ok


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    c, d = sys.argv[1], sys.argv[2]
    if c == "kiem":
        sys.exit(1 if cmd_kiem(d) else 0)
    elif c == "gom":
        cmd_gom(d)
    elif c == "xuat087":
        cmd_xuat087(d)
    elif c == "doi-chieu":
        sys.exit(1 if cmd_doi_chieu(d, sys.argv[3]) else 0)
    else:
        sys.exit(__doc__)
