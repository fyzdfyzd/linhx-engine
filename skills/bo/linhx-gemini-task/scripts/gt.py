"""Sổ và công cụ cho việc giao nhiệm vụ cho Gemini Task (Ultra, model Argon). Chỉ dùng thư viện chuẩn.

Dùng:
  python gt.py moi <thu-muc-lab> <ma> [--loai quet|dai|media|code] [--muc-tieu "..."]
        tạo <lab>/argon/<ma>/DE.txt từ khuôn đề, CHAY.md, yeu-cau.json
  python gt.py gui <thu-muc-nhiem-vu> --link URL [--ghi-chu "..."]
        ghi giờ gửi + link vào CHAY.md và sổ chung
  python gt.py trang-thai <thu-muc-nhiem-vu> <dang-chay|xong|loi|gioi-han|da-cham> [--ghi-chu "..."]
  python gt.py so [--con-mo]           bảng mọi nhiệm vụ trong sổ chung
  python gt.py lay <thu-muc-nhiem-vu>  bỏ file trùng theo hash trong files/, giải nén zip vào giai-nen/,
                                       tách các khối '### FILE:' trong TRA-LOI.md
  python gt.py kiem <thu-muc-nhiem-vu> chấm máy theo yeu-cau.json, ghi KIEM-MAY.md
  python gt.py skill <thu-muc-skill>   kiểm Skill cho Gemini (SKILL.md ở gốc, chỉ file chữ, ≤100 MB, không gọi mạng) rồi nén zip
  python gt.py chieu-dai <file>        đếm ký tự, dòng, 120 ký tự đầu/cuối để so với ô nhập sau khi dán

Sổ chung: biến GT_SO, mặc định D:/LINHX/LAB/GEMINI-TASK/so-nhiem-vu.jsonl (ngoài Windows: ~/GEMINI-TASK/...).
"""
import csv
import datetime as dt
import hashlib
import json
import os
import random
import re
import sys
import zipfile
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
KHUON = GOC / "templates"
CAU_KET = tuple(".!?…:;)\"'”»*")
THU_VIEN_GIA = {"pytest", "unittest", "json", "csv", "re", "os", "sys", "pandas", "numpy", "requests",
                "sqlite3", "random", "math", "typing", "datetime", "pathlib", "logging", "string", "test"}
MA_MANG = re.compile(r"\b(requests\.|urllib\.request|http\.client|socket\.|urlopen|curl |wget |pip install|npm install)")


def so_path() -> Path:
    if os.environ.get("GT_SO"):
        return Path(os.environ["GT_SO"])
    base = Path("D:/LINHX/LAB/GEMINI-TASK") if os.name == "nt" else Path.home() / "GEMINI-TASK"
    return base / "so-nhiem-vu.jsonl"


def bay_gio() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M")


def ghi_so(muc: dict) -> None:
    p = so_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(muc, ensure_ascii=False) + "\n")


def doc_so() -> dict[str, dict]:
    """Gộp các dòng sự kiện theo khoá thư mục: dòng sau đè trường của dòng trước."""
    p, gop = so_path(), {}
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                e = json.loads(line)
                gop.setdefault(e["thu_muc"], {}).update({k: v for k, v in e.items() if v not in (None, "")})
    return gop


def them_chay(d: Path, dong: str) -> None:
    with open(d / "CHAY.md", "a", encoding="utf-8") as f:
        f.write(f"- {bay_gio()} {dong}\n")


def lenh_moi(lab: str, ma: str, loai: str, muc_tieu: str) -> None:
    d = Path(lab) / "argon" / ma
    d.mkdir(parents=True, exist_ok=True)
    de = d / "DE.txt"
    if de.exists():
        print(f"Đã có {de}, không ghi đè.")
    else:
        text = (KHUON / "khuon-de.txt").read_text(encoding="utf-8")
        text = text.replace("{{MA}}", ma).replace("{{MUC_TIEU}}", muc_tieu or "<viết mục tiêu>")
        text = text.replace("{{MAY}}", (KHUON / "may-argon.txt").read_text(encoding="utf-8").strip())
        de.write_text(text, encoding="utf-8")
    yc = d / "yeu-cau.json"
    if not yc.exists():
        yc.write_text(json.dumps({
            "_ghi_chu": "Sửa cho khớp đề. file: đường dẫn trong zip đã giải nén; csv: cột và số dòng tối thiểu.",
            "file": ["TONG-KET.md", "TIEN-DO.md"],
            "csv": {}, "cot_van_ban": ["tom_y_vi", "mo_ta", "doan_dien_giai"], "mau_url": 10}, ensure_ascii=False, indent=2),
            encoding="utf-8")
    if not (d / "CHAY.md").exists():
        (d / "CHAY.md").write_text(f"# {ma}\n\nLoại: {loai}. Mục tiêu: {muc_tieu}\n\n", encoding="utf-8")
    ghi_so({"thu_muc": str(d.resolve()), "ma": ma, "loai": loai, "muc_tieu": muc_tieu,
            "trang_thai": "nhap", "tao": bay_gio()})
    print(f"Tạo {d}: DE.txt, yeu-cau.json, CHAY.md. Viết nốt đề rồi chạy: python gt.py chieu-dai {de}")


def lenh_gui(d: Path, link: str, ghi_chu: str) -> None:
    them_chay(d, f"GỬI {link} {ghi_chu}".rstrip())
    ghi_so({"thu_muc": str(d.resolve()), "trang_thai": "dang-chay", "gui": bay_gio(), "link": link, "ghi_chu": ghi_chu})
    print("Đã ghi.")


def lenh_trang_thai(d: Path, tt: str, ghi_chu: str) -> None:
    them_chay(d, f"{tt.upper()} {ghi_chu}".rstrip())
    muc = {"thu_muc": str(d.resolve()), "trang_thai": tt, "ghi_chu": ghi_chu}
    muc[{"xong": "xong", "da-cham": "cham", "gioi-han": "gioi_han"}.get(tt, "cap_nhat")] = bay_gio()
    ghi_so(muc)
    print("Đã ghi.")


def lenh_so(con_mo: bool) -> None:
    rows = sorted(doc_so().values(), key=lambda r: r.get("gui") or r.get("tao", ""))
    if con_mo:
        rows = [r for r in rows if r.get("trang_thai") in ("nhap", "dang-chay", "xong")]
    print(f"Sổ: {so_path()}  ({len(rows)} nhiệm vụ)")
    for r in rows:
        print(f"{r.get('trang_thai', '?'):10} {r.get('ma', '?'):24} gửi {r.get('gui', '-'):16} {r.get('link', '')}")
    gh = [r for r in doc_so().values() if r.get("gioi_han")]
    if gh:
        print(f"\nĐã chạm giới hạn {len(gh)} lần, lần gần nhất {max(r['gioi_han'] for r in gh)}.")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def lenh_lay(d: Path) -> None:
    files = d / "files"
    files.mkdir(exist_ok=True)
    seen = {}
    for p in sorted(files.iterdir()):
        if p.is_file():
            h = sha(p)
            if h in seen:
                print(f"trùng hash, xoá {p.name} (giống {seen[h]})")
                p.unlink()
            else:
                seen[h] = p.name
    out = d / "giai-nen"
    for z in sorted(files.glob("*.zip")):
        dst = out / z.stem
        with zipfile.ZipFile(z) as zf:
            for m in zf.infolist():
                t = (dst / m.filename).resolve()
                if dst.resolve() not in t.parents and t != dst.resolve():
                    print(f"bỏ đường dẫn ra ngoài: {m.filename}")
                    continue
                zf.extract(m, dst)
        print(f"giải nén {z.name} → {dst}")
    tl = d / "TRA-LOI.md"
    if tl.exists() and re.search(r"^#{2,4}\s*FILE:", tl.read_text(encoding="utf-8"), re.M):
        sys.path.insert(0, str(Path(__file__).parent))
        from tach_file import tach
        for rel, body in tach(tl.read_text(encoding="utf-8")).items():
            p = (out / "tu-tra-loi" / rel).resolve()
            if (out / "tu-tra-loi").resolve() in p.parents:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(body, encoding="utf-8")
                print("tách", rel)
    lenh_trang_thai(d, "xong", f"lấy về {len(seen)} file")


def doc_csv(p: Path) -> tuple[list[str], list[dict]]:
    with open(p, encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames or []), list(r)


def lenh_kiem(d: Path) -> int:
    yc = json.loads((d / "yeu-cau.json").read_text(encoding="utf-8")) if (d / "yeu-cau.json").exists() else {}
    goc = d / "giai-nen" if (d / "giai-nen").exists() else d
    tat_ca = [p for p in goc.rglob("*") if p.is_file()]
    ten = {p.relative_to(goc).as_posix() for p in tat_ca}
    log, loi = [f"# Kiểm máy {d.name} ({bay_gio()})", "", f"{len(tat_ca)} file trong {goc}"], 0

    def tim(rel: str) -> list[Path]:
        return [p for p in tat_ca if p.relative_to(goc).as_posix().endswith(rel)]

    for rel in yc.get("file", []):
        ok = bool(tim(rel))
        loi += not ok
        log.append(f"- {'OK ' if ok else 'THIẾU'} file {rel}")
    cot_vb = set(yc.get("cot_van_ban", []))
    urls, cat_cung, gg = [], 0, 0
    for rel, can in yc.get("csv", {}).items():
        ps = tim(rel)
        if not ps:
            log.append(f"- THIẾU csv {rel}")
            loi += 1
            continue
        head, rows = doc_csv(ps[0])
        thieu = [c for c in can.get("cot", []) if c not in head]
        du = len(rows) >= can.get("toi_thieu", 0)
        loi += bool(thieu) + (not du)
        log.append(f"- {'OK ' if du and not thieu else 'THIẾU'} {rel}: {len(rows)} dòng (cần ≥ {can.get('toi_thieu', 0)})"
                   + (f", thiếu cột {thieu}" if thieu else ""))
    for p in tat_ca:
        if p.suffix.lower() != ".csv":
            continue
        try:
            head, rows = doc_csv(p)
        except (UnicodeDecodeError, csv.Error):
            continue
        for r in rows:
            for k, v in r.items():
                v = (v or "").strip()
                if k in cot_vb and len(v) > 40 and not v.endswith(CAU_KET):
                    cat_cung += 1
                if v.startswith("http"):
                    urls.append(v)
                    gg += "google.com/search" in v or "google.com/url" in v
    log.append(f"- {cat_cung} đoạn văn (cột {sorted(cot_vb)}) không kết thúc bằng dấu câu, nghi bị cắt cứng")
    log.append(f"- {len(urls)} URL trong CSV, {gg} URL bọc google.com/search hoặc /url")
    loi += bool(cat_cung) + bool(gg)
    gia = [p.relative_to(goc).as_posix() for p in tat_ca if p.suffix == ".py" and p.stem in THU_VIEN_GIA]
    if gia:
        loi += 1
        log.append(f"- CẢNH BÁO file trùng tên thư viện (có thể là test giả): {gia}")
    md = [p for p in tat_ca if p.suffix.lower() in (".md", ".txt")]
    so_tu_khai = []
    for p in md:
        for m in re.finditer(r"(\d+)\s*(test|bài kiểm|passed|đạt|trang|dòng|nguồn)", p.read_text(encoding="utf-8", errors="ignore"), re.I):
            so_tu_khai.append(f"{p.name}: {m.group(0)}")
    if so_tu_khai:
        log.append(f"- Số tự khai cần đối chiếu (tối đa 15): " + "; ".join(so_tu_khai[:15]))
    random.seed(len(urls))
    mau = random.sample(sorted(set(urls)), min(yc.get("mau_url", 10), len(set(urls))))
    log += ["", "## URL mẫu để Claude mở kiểm"] + [f"- {u}" for u in mau]
    log += ["", f"Kết luận máy: {loi} mục thiếu. Máy không chấm nội dung; Claude đọc 5 dòng ngẫu nhiên và mở URL mẫu."]
    (d / "KIEM-MAY.md").write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))
    return 1 if loi else 0


def la_chu(p: Path) -> bool:
    try:
        b = p.read_bytes()
        b.decode("utf-8")
        return b"\x00" not in b
    except UnicodeDecodeError:
        return False


def lenh_skill(d: Path) -> int:
    d = d.resolve()
    loi = []
    sk = d / "SKILL.md"
    if not sk.exists():
        loi.append("thiếu SKILL.md ở gốc")
    else:
        t = sk.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---", t, re.S)
        if not m or "name:" not in m.group(1) or "description:" not in m.group(1):
            loi.append("SKILL.md thiếu frontmatter name/description")
        elif not re.search(rf"^name:\s*{re.escape(d.name)}\s*$", m.group(1), re.M):
            loi.append(f"name trong SKILL.md nên trùng tên thư mục '{d.name}'")
    files = [p for p in d.rglob("*") if p.is_file()]
    tong = sum(p.stat().st_size for p in files)
    nhi_phan = [p.relative_to(d).as_posix() for p in files if p.suffix.lower() != ".pdf" and not la_chu(p)]
    mang = [p.relative_to(d).as_posix() for p in files if p.suffix in (".py", ".sh", ".js")
            and MA_MANG.search(p.read_text(encoding="utf-8", errors="ignore"))]
    duoi_la = sorted({p.suffix or p.name for p in files if p.suffix.lower() not in (".md", ".py", ".txt", ".csv", ".pdf")})
    if duoi_la:
        loi.append(f"Gemini chỉ nhận .md .py .txt .csv .pdf; đổi đuôi: {duoi_la}")
    if nhi_phan:
        loi.append(f"file không phải chữ (đổi sang base64 .txt): {nhi_phan[:10]}")
    if tong > 100 * 1024 * 1024:
        loi.append(f"quá 100 MB: {tong / 1e6:.1f} MB")
    if mang:
        print(f"Cảnh báo: script có dấu hiệu gọi mạng (máy Gemini chặn mạng): {mang}")
    print(f"{len(files)} file, {tong / 1024:.0f} KB")
    if loi:
        print("KHÔNG ĐẠT:\n- " + "\n- ".join(loi))
        return 1
    z = d.parent / f"{d.name}.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in files:
            zf.write(p, p.relative_to(d).as_posix())
    print(f"ĐẠT. Nén {z} (SKILL.md ở gốc zip). Gemini không nhận zip: Skills → Create → Upload → chọn thư mục {d}. Gọi bằng @{d.name}.")
    return 0


def lenh_chieu_dai(p: Path) -> None:
    t = p.read_text(encoding="utf-8")
    phang = " ".join(t.split())
    print(f"{len(t)} ký tự, {t.count(chr(10)) + 1} dòng")
    print(f"ĐẦU: {phang[:120]}")
    print(f"CUỐI: {phang[-120:]}")


def main() -> None:
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        return

    def opt(name: str, default: str = "") -> str:
        return a[a.index(name) + 1] if name in a else default

    cmd = a[0]
    if cmd == "moi":
        lenh_moi(a[1], a[2], opt("--loai", "quet"), opt("--muc-tieu"))
    elif cmd == "gui":
        lenh_gui(Path(a[1]), opt("--link"), opt("--ghi-chu"))
    elif cmd == "trang-thai":
        lenh_trang_thai(Path(a[1]), a[2], opt("--ghi-chu"))
    elif cmd == "so":
        lenh_so("--con-mo" in a)
    elif cmd == "lay":
        lenh_lay(Path(a[1]))
    elif cmd == "kiem":
        sys.exit(lenh_kiem(Path(a[1])))
    elif cmd == "skill":
        sys.exit(lenh_skill(Path(a[1])))
    elif cmd == "chieu-dai":
        lenh_chieu_dai(Path(a[1]))
    else:
        print(f"Không rõ lệnh {cmd}.\n{__doc__}")
        sys.exit(2)


if __name__ == "__main__":
    main()
