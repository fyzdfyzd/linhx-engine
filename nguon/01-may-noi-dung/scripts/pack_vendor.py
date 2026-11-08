"""Đóng gói có chọn lọc (vendorize) các skill, script, dữ liệu chuẩn và bộ nhận diện tạm Sakedemy
từ 12 LAB gốc vào D:\\LINHX\\PROTO\\01_MAY_TAO_NOI_DUNG\\vendor\\ mà KHÔNG sửa bất kỳ file nào ở LAB gốc.
Sinh VENDOR_MANIFEST.json kèm SHA256 và phiên bản để truy vết.
"""
import hashlib
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

PROTO_ROOT = Path(r"D:\LINHX\PROTO\01_MAY_TAO_NOI_DUNG")
LAB_ROOT = Path(r"D:\LINHX\LAB")
VENDOR_ROOT = PROTO_ROOT / "vendor"

EXCLUDE_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv", ".pytest_cache",
    ".hf", ".hf-cache", ".uv-cache", ".uv-python", ".pw-browsers", ".npm-cache",
    ".node", ".chrome-chatgpt", "_luu-tru-v0.1"
}
EXCLUDE_EXTS = {".mp4", ".wav", ".tgz", ".zip", ".ai", ".pma", ".db", ".wal"}

# Danh mục đóng gói chính xác từ từng LAB
COPY_MAP = {
    "LAB017": {
        "ten_goc": "LAB017-ELEARNING-AI",
        "phien_ban": "v0.2-2026-10-19",
        "items": [
            ("src/plugin/linhx-course", "linhx-course"),
            ("seed/course", "seed-course"),
        ],
    },
    "LAB025": {
        "ten_goc": "LAB025-QUY-TRINH-VIET-BAI",
        "phien_ban": "v0.2-9-buoc-2026-10-13",
        "items": [
            ("QUY-TRINH-VIET-BAI.md", "QUY-TRINH-VIET-BAI.md"),
            ("src/linhx-viet-bai", "linhx-viet-bai"),
        ],
    },
    "LAB027": {
        "ten_goc": "LAB027-DECK-PROPOSAL",
        "phien_ban": "v0.3-15-buoc-2026-10",
        "items": [
            ("QUY-TRINH-DECK.md", "QUY-TRINH-DECK.md"),
            ("data", "data"),
            ("src/linhx-deck", "linhx-deck"),
        ],
    },
    "LAB028": {
        "ten_goc": "LAB028-REPORT-FLOW",
        "phien_ban": "v0.2-13-buoc-typst",
        "items": [
            ("OVERVIEW.md", "OVERVIEW.md"),
            ("src/linhx-report", "linhx-report"),
        ],
    },
    "LAB029": {
        "ten_goc": "LAB029-KHOANG-TRONG-DOC-GIA",
        "phien_ban": "v0.1-2026-10-13",
        "items": [
            ("OVERVIEW.md", "OVERVIEW.md"),
            ("src/linhx-khoang-trong", "linhx-khoang-trong"),
        ],
    },
    "LAB031": {
        "ten_goc": "LAB031-KHO-MINH-HOA",
        "phien_ban": "v0.1-2026-10",
        "items": [
            ("OVERVIEW.md", "OVERVIEW.md"),
            ("src/plugin/linhx-kho-minh-hoa", "linhx-kho-minh-hoa"),
        ],
    },
    "LAB032": {
        "ten_goc": "LAB032-ANH-SANG-SLIDE",
        "phien_ban": "v0.1-anh2slide",
        "items": [
            ("OVERVIEW.md", "OVERVIEW.md"),
            ("src/anh-sang-slide", "anh-sang-slide"),
        ],
    },
    "LAB036": {
        "ten_goc": "LAB036-BRAND-CHECK-AGENT",
        "phien_ban": "v0.1-chuan-abc",
        "items": [
            ("CHUAN-ABC-v1.md", "CHUAN-ABC-v1.md"),
            ("src/linhx-brand-check", "linhx-brand-check"),
        ],
    },
    "LAB043": {
        "ten_goc": "LAB043-DESIGN-ONBRAND",
        "phien_ban": "v2.0-2026-10-24",
        "items": [
            ("OVERVIEW.md", "OVERVIEW.md"),
            ("chuan-guideline/KHUNG-GUIDELINE-CHUAN.md", "chuan-guideline/KHUNG-GUIDELINE-CHUAN.md"),
            ("chuan-guideline/KET-QUA-V2-2026-10-23.md", "chuan-guideline/KET-QUA-V2-2026-10-23.md"),
            ("chuan-guideline/check/BAI-HOC-VONG-2.md", "chuan-guideline/check/BAI-HOC-VONG-2.md"),
            ("chuan-guideline/check/cuoi-sakedemy.md", "chuan-guideline/check/cuoi-sakedemy.md"),
            ("brands/sakedemy", "brands/sakedemy"),
            ("src/linhx-onbrand", "linhx-onbrand"),
        ],
    },
    "LAB046": {
        "ten_goc": "LAB046-REPORT-ENGINE",
        "phien_ban": "v1.0-report-core-2026-10-19",
        "items": [
            ("09-REPORT-CORE/KIEN-TRUC.md", "KIEN-TRUC.md"),
            ("src/report-core", "report-core"),
        ],
    },
    "LAB048": {
        "ten_goc": "LAB048-PERSONA-SURVEY-GIA-LAP",
        "phien_ban": "v0.1-nemotron-vn",
        "items": [
            ("src/lay_mau_1000.py", "src/lay_mau_1000.py"),
        ],
    },
    "LAB049": {
        "ten_goc": "LAB049-VIET-NHU-NGUOI",
        "phien_ban": "v2.0-va-flow-2026-10-25",
        "items": [
            ("HUONG-DAN-ANTIGRAVITY.md", "HUONG-DAN-ANTIGRAVITY.md"),
            ("src/linhx-bien-tap", "linhx-bien-tap"),
            ("src/linhx-viet-giong-viet", "linhx-viet-giong-viet"),
            ("agy-ra/va-flow/VA-FLOW.md", "va-flow/VA-FLOW.md"),
            ("agy-ra/quy-trinh-van-anh-doc-lap/SO-TAY-20-COMMENT-VAN-ANH.md", "va-flow/SO-TAY-20-COMMENT-VAN-ANH.md"),
        ],
    },
    "LAB066": {
        "ten_goc": "LAB066-CASTING-GUONG-MAT",
        "phien_ban": "v0.3-3-vong-casting",
        "items": [
            ("OVERVIEW.md", "OVERVIEW.md"),
            ("QUY-TRINH-3-VONG.md", "QUY-TRINH-3-VONG.md"),
            ("QUY-TRINH-PHAT-TRIEN-NHAN-VAT.md", "QUY-TRINH-PHAT-TRIEN-NHAN-VAT.md"),
            ("BAI-HOC.md", "BAI-HOC.md"),
            ("scripts", "scripts"),
        ],
    },
}


def sha256_short(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def copy_filtered(src: Path, dst: Path, files_log: list):
    if not src.exists():
        return
    if src.is_file():
        if src.suffix.lower() in EXCLUDE_EXTS:
            return
        # Bỏ các file PDF/PNG gốc quá nặng > 5MB trong 00-goc để giữ gói gọn nhẹ
        if src.stat().st_size > 5 * 1024 * 1024:
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        files_log.append({
            "rel_path": str(dst.relative_to(VENDOR_ROOT)).replace("\\", "/"),
            "size": dst.stat().st_size,
            "sha256_16": sha256_short(dst),
        })
        return

    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        rel_dir = Path(root).relative_to(src)
        target_dir = dst / rel_dir
        for fname in files:
            fpath = Path(root) / fname
            if fpath.suffix.lower() in EXCLUDE_EXTS:
                continue
            if fpath.stat().st_size > 5 * 1024 * 1024:
                continue
            tpath = target_dir / fname
            tpath.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(fpath, tpath)
            files_log.append({
                "rel_path": str(tpath.relative_to(VENDOR_ROOT)).replace("\\", "/"),
                "size": tpath.stat().st_size,
                "sha256_16": sha256_short(tpath),
            })


def pack_persona_sample(files_log: list):
    """Trích 60 persona đa dạng ngành nghề/tuổi/vùng từ LAB048 persona-1000.json để đóng gói gọn vào vendor/LAB048/data/."""
    src_json = LAB_ROOT / "LAB048-PERSONA-SURVEY-GIA-LAP" / "data" / "persona-1000.json"
    dst_json = VENDOR_ROOT / "LAB048" / "data" / "persona-sample-60.json"
    dst_json.parent.mkdir(parents=True, exist_ok=True)
    if src_json.exists():
        data = json.loads(src_json.read_text(encoding="utf-8"))
        # Lấy đều 60 persona trải khắp các tầng trong 1000 persona
        step = max(1, len(data) // 60)
        sample = data[::step][:60]
        dst_json.write_text(json.dumps(sample, ensure_ascii=False, indent=2), encoding="utf-8")
        files_log.append({
            "rel_path": str(dst_json.relative_to(VENDOR_ROOT)).replace("\\", "/"),
            "size": dst_json.stat().st_size,
            "sha256_16": sha256_short(dst_json),
            "note": f"Trích mẫu phân tầng 60/{len(data)} persona từ LAB048/data/persona-1000.json",
        })


def main():
    VENDOR_ROOT.mkdir(parents=True, exist_ok=True)
    manifest = {
        "proto": "01_MAY_TAO_NOI_DUNG",
        "packed_at": datetime.now().isoformat(timespec="seconds"),
        "rule": "Sao chép nguyên bản từ D:\\LINHX\\LAB sang vendor/ theo Luật 1 Đề 01. Không sửa LAB gốc.",
        "labs": {},
        "total_files": 0,
        "total_bytes": 0,
    }

    for lab_code, cfg in COPY_MAP.items():
        lab_dir = LAB_ROOT / cfg["ten_goc"]
        files_log = []
        for src_rel, dst_rel in cfg["items"]:
            src_path = lab_dir / src_rel
            dst_path = VENDOR_ROOT / lab_code / dst_rel
            copy_filtered(src_path, dst_path, files_log)
        if lab_code == "LAB048":
            pack_persona_sample(files_log)
        lab_bytes = sum(f["size"] for f in files_log)
        manifest["labs"][lab_code] = {
            "source_dir": str(lab_dir),
            "version": cfg["phien_ban"],
            "file_count": len(files_log),
            "total_bytes": lab_bytes,
            "files": files_log,
        }
        manifest["total_files"] += len(files_log)
        manifest["total_bytes"] += lab_bytes

    manifest_path = VENDOR_ROOT / "VENDOR_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"PACKED { len(manifest['labs']) } LABs -> { manifest['total_files'] } files ({ manifest['total_bytes']:,} bytes)")


if __name__ == "__main__":
    main()
