"""Đóng gói bản sao chỉ-đọc (read-only copy) từ LAB060, LAB046, OPC001, AmbassadorOS, LAB072
vào `D:\\LINHX\\PROTO\\03_OPC_OS\\vendor\\` kèm VENDOR_MANIFEST.json (SHA256).
Tuyệt đối không sửa bất kỳ file nào ở thư mục nguồn.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_item(src: Path, dst: Path, manifest: list[dict], source_tag: str) -> None:
    if not src.exists():
        print(f"[SKIP] Không tìm thấy: {src}")
        return
    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        manifest.append({
            "source_group": source_tag,
            "src": str(src),
            "dst": str(dst.relative_to(ROOT)),
            "bytes": dst.stat().st_size,
            "sha256_src": sha256_file(src),
            "sha256_dst": sha256_file(dst),
        })
    elif src.is_dir():
        for item in src.rglob("*"):
            if item.is_file():
                rel = item.relative_to(src)
                if any(part in (".venv", "node_modules", "__pycache__", ".pytest_cache", ".ruff_cache", ".git", "var") for part in rel.parts):
                    continue
                target = dst / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target)
                manifest.append({
                    "source_group": source_tag,
                    "src": str(item),
                    "dst": str(target.relative_to(ROOT)),
                    "bytes": target.stat().st_size,
                    "sha256_src": sha256_file(item),
                    "sha256_dst": sha256_file(target),
                })


def main() -> int:
    VENDOR.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []

    # 1. LAB060-BAN-SO-QUA-QR
    lab060 = Path(r"D:\LINHX\LAB\LAB060-BAN-SO-QUA-QR")
    for rel in ["BAN-THU.md", "HUONG-DAN-SEPAY.md", "KHAO-SAT.md", "src", "web"]:
        copy_item(lab060 / rel, VENDOR / "LAB060" / rel, manifest, "LAB060")

    # 2. LAB046-REPORT-ENGINE (report-core + 09-REPORT-CORE)
    lab046 = Path(r"D:\LINHX\LAB\LAB046-REPORT-ENGINE")
    copy_item(lab046 / "src" / "report-core", VENDOR / "LAB046" / "report-core", manifest, "LAB046")
    for rel in ["KIEN-TRUC.md", "SO-SANH.md"]:
        copy_item(lab046 / "09-REPORT-CORE" / rel, VENDOR / "LAB046" / "09-REPORT-CORE" / rel, manifest, "LAB046")

    # 3. OPC001-CHIEMTINH-VN
    opc001 = Path(r"D:\LINHX\LINHX-OPC\OPC001-CHIEMTINH-VN")
    for rel in ["README.md", "PLAYBOOK.md", "TASKLIST.csv", "LICH.md", "mau", "bao-cao"]:
        copy_item(opc001 / rel, VENDOR / "OPC001" / rel, manifest, "OPC001")
    astro = opc001 / "src" / "astro-engine"
    for rel in [
        "src",
        "calc-service/src",
        "data/blueprints",
        "data/ephe",
        "data/legacy/chart/bg-light.png",
        "data/legacy/data/natalData.json",
    ]:
        copy_item(astro / rel, VENDOR / "OPC001" / "astro-engine" / rel, manifest, "OPC001")

    # 4. AmbassadorOS (Luna Nguyệt Mai & Inbox/Content config)
    amb = Path(r"D:\LINHX\PRJ\AmbassadorOS")
    for rel in ["README.md", "DESIGN.md", "seed/luna-vy.json", "server/governance.js"]:
        copy_item(amb / rel, VENDOR / "AmbassadorOS" / rel, manifest, "AmbassadorOS")

    # 5. LAB072-BANK-OPS-KIT (cho OPC 2 Ngân hàng)
    lab072 = Path(r"D:\LINHX\LAB\LAB072-BANK-OPS-KIT")
    copy_item(lab072 / "KHAO-SAT.md", VENDOR / "LAB072" / "KHAO-SAT.md", manifest, "LAB072")
    copy_item(lab072 / "src" / "linhx-bank-ops", VENDOR / "LAB072" / "linhx-bank-ops", manifest, "LAB072")

    # 6. LAB062-OPC-REPORT-QR
    lab062 = Path(r"D:\LINHX\LAB\LAB062-OPC-REPORT-QR")
    copy_item(lab062 / "NGHIEN-CUU-HOP-NHAT.md", VENDOR / "LAB062" / "NGHIEN-CUU-HOP-NHAT.md", manifest, "LAB062")

    all_match = all(m["sha256_src"] == m["sha256_dst"] for m in manifest)
    out = {
        "total_files": len(manifest),
        "total_bytes": sum(m["bytes"] for m in manifest),
        "integrity_100_percent": all_match,
        "files": manifest,
    }
    (VENDOR / "VENDOR_MANIFEST.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Đã đóng gói {len(manifest)} files ({out['total_bytes']:,} bytes) vào vendor/. Integrity={all_match}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
