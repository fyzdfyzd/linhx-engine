"""Sinh trang wiki từ ảnh chụp bảng hệ thống (artifact Wyeq3HaoB6pfgoeC11P2qY).

Dùng: python scripts/wiki_tu_bang.py wiki/nguon/<ngay>-BANG-HE-THONG.json
Ghi đè các trang sinh tự động trong wiki/trang/ (dich-cuoi, kien-truc, lo-trinh,
danh-muc-he-thong, he-thong-*). Trang viết tay không bị đụng. Chỉ dùng stdlib.
"""
import json, re, sys, unicodedata
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent / "wiki"
TRANG = GOC / "trang"
NHAN = {
    "dich": "Đích", "lam": "Làm", "cong": "Cổng đạt", "den": "Đến", "phieu": "Phiếu",
    "dung": "Dùng ở", "tt": "Tình trạng", "viec": "Việc", "lay": "Lấy gì", "vao": "Vào đâu",
    "dem": "Đợt đầu", "muc": "Mức tái dùng", "khi_du": "Khi đủ", "nay": "Nay", "do": "Đo",
    "thanh": "Thành", "tu": "Từ", "de_xuat": "Chốt / đề xuất", "hoi": "Câu hỏi",
    "dat": "Đạt bằng", "vi_sao": "Vì sao", "hinh": "Hình", "du_an": "Dự án", "du": "Đủ chưa",
    "noi": "Gồm", "sua": "Chữa lỗi", "ma": "Mã", "mang": "Mảng", "buoc": "Bước", "doc": "Đọc",
    "tra_loi": "Cần trả lời", "nhom": "Nhóm",
}
TIEU = ("ten", "ma", "mang", "buoc", "hoi", "tu")
TT = {"co": "đã có", "moi": "mới", "y": "mới là ý"}


def slug(s):
    s = unicodedata.normalize("NFD", s.replace("đ", "d").replace("Đ", "D"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def chu(v):
    if isinstance(v, list):
        return "; ".join(chu(x) for x in v)
    if isinstance(v, dict):
        return "; ".join(f"{NHAN.get(k, k)}: {chu(x)}" for k, x in v.items())
    return str(v).strip()


def ve(v, sau=0):
    """Chuyển dữ liệu bảng thành gạch đầu dòng markdown."""
    pad = "  " * sau
    out = []
    if isinstance(v, str):
        return [pad + "- " + v.strip()] if v.strip() else []
    if isinstance(v, dict):
        v = [v]
    for x in v:
        if not isinstance(x, dict):
            out.append(pad + "- " + chu(x))
            continue
        k_tieu = next((k for k in TIEU if k in x), None)
        tieu = x.get(k_tieu, "") if k_tieu else ""
        out.append(pad + f"- **{tieu}**" if tieu else pad + "-")
        for k, y in x.items():
            if k == k_tieu:
                continue
            if k == "tt":
                y = TT.get(y, y)
            if isinstance(y, list) and y and isinstance(y[0], dict):
                out.append(pad + f"  - {NHAN.get(k, k)}:")
                out += ve(y, sau + 2)
            elif isinstance(y, list):
                out.append(pad + f"  - {NHAN.get(k, k)}: " + "; ".join(chu(z) for z in y))
            else:
                out.append(pad + f"  - {NHAN.get(k, k)}: {chu(y)}")
    return out


def dau(tieu, ngay, nguon, loai="tong-quan"):
    return [
        "---", f"tieu_de: {tieu}", f"loai: {loai}", "trang_thai: cho-linh", f"cap_nhat: {ngay}",
        f"nguon: [{nguon}]", "sinh_tu_dong: scripts/wiki_tu_bang.py (sửa ở bảng rồi chạy lại, đừng sửa tay)",
        "---", f"# {tieu}", "",
    ]


def muc(ten, v):
    return [f"## {ten}", ""] + ve(v) + [""] if v else []


def main(duong):
    snap = json.loads(Path(duong).read_text(encoding="utf-8"))
    ngay = snap["chup_luc"][:10]
    ng = f"nguon/{Path(duong).name}, {snap['nguon']}"
    b = snap["tong"]["buc_tranh"]
    v = b.get("vision", {})

    s = dau("Đích cuối đường LINHX ENGINE", ngay, ng)
    s += [f"**Vision:** {v.get('cau', '')}", "", f"_Bảng cập nhật: {b.get('cap_nhat', '')}_", ""]
    s += muc("Tóm tắt", b.get("tom_tat"))
    s += muc("Năm thay đổi", v.get("doi"))
    s += muc("Từng đơn vị: nay, khi đủ, đo bằng gì", v.get("don_vi"))
    for k, t in (("tong", "Tổng"), ("muc_tieu_linh", "Mục tiêu của Linh"), ("vi_sao", "Vì sao"),
                 ("khong_lam", "Không làm"), ("phan_bien", "Phản biện"), ("cau_hoi", "Câu hỏi chờ Linh")):
        s += muc(t, v.get(k))
    s += muc("Đích 30/6/2027 theo mảng", b.get("dich"))
    s += muc("Còn thiếu", b.get("thieu"))
    s += muc("Điểm vênh", b.get("vench"))
    s += muc("Đã hỏi và chốt", b.get("chot"))
    s += muc("Thứ tự đọc", b.get("doc_thu_tu"))
    s += ["Liên quan: [[tong-quan]] [[kien-truc]] [[lo-trinh]] [[hop-nhat]]", ""]
    (TRANG / "dich-cuoi.md").write_text("\n".join(s), encoding="utf-8")

    s = dau("Kiến trúc LINHX ENGINE khi đủ", ngay, ng, "loi")
    s += ["Bản kỹ thuật đang chạy: [[loi-engine]]. Trang này là bản quy hoạch đầy đủ.", ""]
    s += muc("Sáu tầng", b.get("tang"))
    s += muc("Module lõi theo nhóm", b.get("module"))
    s += muc("Máy nền (chạy qua hàng việc)", b.get("may_nen"))
    s += muc("Template", b.get("template"))
    td = b.get("tai_dung", {})
    if td:
        s += ["## Tái dùng 9 PROTO", "", td.get("doi_lo_trinh", ""), ""] + ve(td.get("ds", [])) + [""]
    s += ["Liên quan: [[dich-cuoi]] [[lo-trinh]] [[hop-nhat]] [[loi-engine]]", ""]
    (TRANG / "kien-truc.md").write_text("\n".join(s), encoding="utf-8")

    s = dau("Lộ trình LINHX ENGINE", ngay, ng)
    s += muc("Các chặng", b.get("lo_trinh"))
    dn = b.get("dem_nay", {})
    if dn:
        s += ["## Chặng 0 chia làn", ""] + ve(dn.get("dieu_kien", [])) + [""] + ve(dn.get("lan", [])) + [""]
    la = snap["tong"].get("launch", {})
    if la:
        s += muc("Khuôn launch một sản phẩm (cổng C1 trở đi)", la.get("cong"))
    s += ["Liên quan: [[dich-cuoi]] [[kien-truc]] [[hop-nhat]] [[danh-muc-de-bai]]", ""]
    (TRANG / "lo-trinh.md").write_text("\n".join(s), encoding="utf-8")

    nhom = {}
    for ma, r in snap["he_thong"].items():
        nhom.setdefault(r.get("nhom") or "Khác", []).append((ma, r))
    bang = dau("Danh mục hệ thống (59 dòng + bổ sung)", ngay, ng, "danh-muc")
    bang += ["Mỗi dòng là một hệ thống web, dự án hoặc quy trình nội bộ. Chi tiết từng dòng (khách, nỗi đau, việc khách cần, người dùng thấy gì, đề xuất, phản biện, đề bài) ở trang nhóm.", "",
             "| Mã | Tên | Nhóm | Dạng | Trạng thái | Quyết | Cấp | Mặt tiền |", "|---|---|---|---|---|---|---|---|"]
    T = {"mo_ta": "Là gì", "khach": "Khách", "dau": "Nỗi đau", "viec": "Việc khách cần (JTBD)",
         "nhan_nhi": "Khách tin khi / mất khách khi", "mat_tien": "Mặt tiền", "kenh": "Kênh", "ban": "Cách bán",
         "module": "Module cần", "de_xuat": "Đề xuất", "phan_bien": "Phản biện", "gop_vao": "Gộp vào",
         "dung_chung": "Dùng chung", "cach_thu": "Cách thử", "gia_thuyet": "Giả thuyết", "giai_doan": "Giai đoạn",
         "nguong": "Ngưỡng", "muc_tieu": "Mục tiêu", "de_bai": "Đề bài", "ghi_chu": "Ghi chú",
         "hinh_thai": "Hình thái", "nguon": "Nguồn"}
    for ten_nhom, ds in nhom.items():
        sl = "he-thong-" + slug(ten_nhom)
        p = dau(f"Hệ thống nhóm {ten_nhom}", ngay, ng, "unit")
        p += [f"{len(ds)} dòng. Danh mục đủ: [[danh-muc-he-thong]].", ""]
        for ma, r in sorted(ds, key=lambda x: x[0]):
            cap = r.get("cap") or r.get("cap_goi_y") or ""
            bang.append(f"| {ma} | {r.get('ten','')} | {ten_nhom} | {r.get('dang','')} | {r.get('trang_thai','')} | {r.get('quyet','') or '-'} | {cap} | {r.get('mat_tien','') or '-'} |".replace("\n", " "))
            p += [f"## {ma} · {r.get('ten','')}", "",
                  f"Dạng: {r.get('dang','')} · Trạng thái: {r.get('trang_thai','')} · Quyết: {r.get('quyet','') or 'chưa'} · Ưu tiên: {r.get('uu_tien','')} · Cấp: {cap or 'chưa'}" + (" · Claude đoán, chờ Linh" if r.get("claude_doan") else ""), ""]
            for k, t in T.items():
                y = r.get(k)
                if y not in (None, "", []):
                    p.append(f"- **{t}:** {chu(y)}")
            p.append("")
        p += [f"Liên quan: [[dich-cuoi]] [[kien-truc]] [[hop-nhat]]", ""]
        (TRANG / f"{sl}.md").write_text("\n".join(p), encoding="utf-8")
    bang += ["", "Trang nhóm: " + " ".join(f"[[he-thong-{slug(n)}]]" for n in nhom), ""]
    (TRANG / "danh-muc-he-thong.md").write_text("\n".join(bang), encoding="utf-8")
    print("đã sinh:", ["dich-cuoi", "kien-truc", "lo-trinh", "danh-muc-he-thong"] + ["he-thong-" + slug(n) for n in nhom])


if __name__ == "__main__":
    main(sys.argv[1])
