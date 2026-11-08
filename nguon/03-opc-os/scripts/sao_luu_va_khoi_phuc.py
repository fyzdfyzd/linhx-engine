"""Kịch bản Sao Lưu Hằng Ngày & Khôi Phục Thử 1 Lần (`scripts/sao_luu_va_khoi_phuc.py`) — Mục 1 `13_LENH_BAC_2.md`.

Thực hiện:
1. Đóng gói dữ liệu vận hành quan trọng của `03_OPC_OS` (`opc.json`, `opcs/*/opc.json`, `demo/output/multi_opc_summary.json`, sổ kế toán `so-doanh-thu.csv`, danh sách đơn hàng `orders.json`, nhật ký hoạt động/lỗi) vào `sao_luu/opc_os_backup_<YYYYMMDD>.zip`.
2. Khôi phục thử 1 lần ra `sao_luu/khoi_phuc_thu/` và đối chiếu mã băm SHA-256 từng tệp (khớp 100%).
3. Ghi biên bản kết quả ra `sao_luu/ket_qua_sao_luu_khoi_phuc.json` và `sao_luu/BAO_CAO_SAO_LUU.md`.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
BACKUP_DIR = ROOT / "sao_luu"
RESTORE_DIR = BACKUP_DIR / "khoi_phuc_thu"


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run_daily_backup_and_test_restore() -> dict:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if RESTORE_DIR.exists():
        shutil.rmtree(RESTORE_DIR)
    RESTORE_DIR.mkdir(parents=True, exist_ok=True)

    today_tag = datetime.now().strftime("%Y%m%d")
    zip_name = f"opc_os_backup_{today_tag}.zip"
    zip_path = BACKUP_DIR / zip_name

    candidates = [
        ROOT / "opc.json",
        ROOT / "opcs" / "opc001_chiemtinh" / "opc.json",
        ROOT / "opcs" / "opc002_bank_prompt_kit" / "opc.json",
        ROOT / "opcs" / "opc003_huong_nghiep_hs" / "opc.json",
        ROOT / "demo" / "output" / "multi_opc_summary.json",
        ROOT / "A_CODE" / "ket_qua_a.json",
        ROOT / "B_AGENT" / "ket_qua_b.json",
        ROOT / "runtime" / "multi_opc" / "shared_data" / "orders.json",
        ROOT / "runtime" / "multi_opc" / "shared_data" / "so-doanh-thu.csv",
        ROOT / "runtime" / "isolated_payment_vault" / "isolated_service_state.json",
    ]
    existing_files = [p for p in candidates if p.exists() and p.is_file()]

    manifest_before: dict[str, str] = {}
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in existing_files:
            rel = p.relative_to(ROOT).as_posix()
            manifest_before[rel] = _sha256(p)
            zf.write(p, arcname=rel)

    # Khôi phục thử 1 lần và đối chiếu SHA-256
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(RESTORE_DIR)

    matched_files = 0
    details = []
    for rel, expected_sha in manifest_before.items():
        restored_file = RESTORE_DIR / rel
        actual_sha = _sha256(restored_file) if restored_file.exists() else ""
        is_match = actual_sha == expected_sha
        if is_match:
            matched_files += 1
        details.append({
            "file": rel,
            "sha256_goc": expected_sha,
            "sha256_khoi_phuc": actual_sha,
            "khop_100pct": is_match,
        })

    all_matched = matched_files == len(manifest_before) and len(manifest_before) > 0
    result = {
        "thoi_gian": datetime.now().isoformat(timespec="seconds"),
        "da_sao_luu": True,
        "ten_ban_sao_luu": zip_name,
        "duong_dan_zip": str(zip_path),
        "kich_thuoc_zip_bytes": zip_path.stat().st_size,
        "so_tep_sao_luu": len(manifest_before),
        "so_tep_khoi_phuc_khop": matched_files,
        "khoi_phuc_thu_khop_100pct": all_matched,
        "thu_muc_khoi_phuc_thu": str(RESTORE_DIR),
        "chi_tiet_tep": details,
    }

    (BACKUP_DIR / "ket_qua_sao_luu_khoi_phuc.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    md_lines = [
        "# BIÊN BẢN SAO LƯU HẰNG NGÀY & KHÔI PHỤC THỬ (`03_OPC_OS`)",
        f"- **Thời gian**: `{result['thoi_gian']}`",
        f"- **Tệp nén sao lưu**: `{zip_name}` (`{result['kich_thuoc_zip_bytes']:,}` bytes)",
        f"- **Số tệp đã sao lưu & khôi phục thử**: `{matched_files}/{len(manifest_before)}` tệp",
        f"- **Kết quả đối chiếu SHA-256 sau khôi phục thử**: **`{'KHỚP 100% (PASS)' if all_matched else 'LỆCH (FAIL)'}`**",
        "",
        "| Tệp dữ liệu | SHA-256 bản gốc | SHA-256 sau khôi phục thử | Khớp |",
        "|---|---|---|---|",
    ]
    for d in details:
        md_lines.append(
            f"| `{d['file']}` | `{d['sha256_goc'][:16]}...` | `{d['sha256_khoi_phuc'][:16]}...` | `{'✅' if d['khop_100pct'] else '❌'}` |"
        )
    (BACKUP_DIR / "BAO_CAO_SAO_LUU.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    res = run_daily_backup_and_test_restore()
    print(
        f"[BackupRestore] OK={res['khoi_phuc_thu_khop_100pct']} "
        f"| Files={res['so_tep_khoi_phuc_khop']}/{res['so_tep_sao_luu']} "
        f"| Zip={res['ten_ban_sao_luu']} ({res['kich_thuoc_zip_bytes']}B)"
    )
