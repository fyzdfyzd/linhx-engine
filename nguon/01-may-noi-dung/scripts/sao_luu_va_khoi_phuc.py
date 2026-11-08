#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sao lưu dữ liệu mỗi ngày vào thư mục `sao_luu/` và thử khôi phục 1 lần (Mục 1 file 13_LENH_BAC_2.md)."""

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
import time
import zipfile
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
SAO_LUU_DIR = ROOT_DIR / "sao_luu"
LOGS_DIR = ROOT_DIR / "logs"
AUDIT_LOG_PATH = LOGS_DIR / "nhat_ky_hoat_dong.jsonl"
ERROR_LOG_PATH = LOGS_DIR / "bao_loi_he_thong.jsonl"


def ghi_nhat_ky(nguoi_dung: str, hanh_dong: str, doi_tuong: str, ket_qua: str = "OK", chi_tiet: dict = None):
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "ai_lam": nguoi_dung,
        "lam_gi": hanh_dong,
        "doi_tuong": doi_tuong,
        "ket_qua": ket_qua,
        "chi_tiet": chi_tiet or {},
    }
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def ghi_bao_loi(nguon: str, thong_bao: str, muc: str = "ERROR"):
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "muc": muc,
        "nguon": nguon,
        "thong_bao": thong_bao,
    }
    with ERROR_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_backup_targets() -> list:
    targets = []
    # 1. Toàn bộ cấu hình loại nội dung loai/
    loai_dir = ROOT_DIR / "loai"
    if loai_dir.exists():
        for p in sorted(loai_dir.rglob("*")):
            if p.is_file():
                targets.append(p)

    # 2. Hàng bài 7 ngày cho Vân Anh duyệt & dữ liệu chuẩn bị
    for fname in (
        "du_lieu_hang_bai_7_ngay_van_anh.json",
        "du_lieu_30_cau_bay_redteam.json",
        "STATUS.md",
        "CAM_RUT_LOG.md",
    ):
        fp = ROOT_DIR / fname
        if fp.exists():
            targets.append(fp)

    # 3. Các bản chạy trong runs/ (RUN_STATUS.json, 05_cham_chon_huong.json, 09b_ban_sach_khong_ma_nguon.md)
    runs_dir = ROOT_DIR / "runs"
    if runs_dir.exists():
        for rdir in sorted(runs_dir.iterdir()):
            if not rdir.is_dir():
                continue
            for key_f in ("RUN_STATUS.json", "05_cham_chon_huong.json", "09b_ban_sach_khong_ma_nguon.md"):
                kp = rdir / key_f
                if kp.exists():
                    targets.append(kp)

    # 4. Nhật ký vận hành & cổng kiểm chung
    if LOGS_DIR.exists():
        for lf in ("nhat_ky_hoat_dong.jsonl", "cong_kiem_chung_metrics.jsonl", "bao_loi_he_thong.jsonl"):
            lp = LOGS_DIR / lf
            if lp.exists():
                targets.append(lp)

    return targets


def run_daily_backup(force: bool = False) -> dict:
    today_str = datetime.now().strftime("%Y-%m-%d")
    day_dir = SAO_LUU_DIR / today_str
    day_dir.mkdir(parents=True, exist_ok=True)
    zip_path = day_dir / f"sao_luu_01_may_tao_noi_dung_{today_str}.zip"
    manifest_path = day_dir / "BACKUP_MANIFEST.json"

    if zip_path.exists() and manifest_path.exists() and not force:
        return json.loads(manifest_path.read_text(encoding="utf-8"))

    t0 = time.perf_counter()
    targets = collect_backup_targets()
    file_hashes = {}

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in targets:
            rel = str(p.relative_to(ROOT_DIR)).replace("\\", "/")
            zf.write(p, arcname=rel)
            file_hashes[rel] = _sha256_file(p)

    manifest = {
        "san_pham": "01_MAY_TAO_NOI_DUNG",
        "ngay_sao_luu": today_str,
        "thoi_diem_sao_luu": datetime.now().isoformat(timespec="seconds"),
        "duong_dan_zip": str(zip_path.relative_to(ROOT_DIR)).replace("\\", "/"),
        "kich_thuoc_zip_bytes": zip_path.stat().st_size,
        "so_luong_file": len(file_hashes),
        "thoi_gian_sao_luu_ms": round((time.perf_counter() - t0) * 1000.0, 1),
        "hashes_sha256": file_hashes,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (SAO_LUU_DIR / "LATEST_BACKUP.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    ghi_nhat_ky(
        nguoi_dung="HeThongSaoLuuTuDong",
        hanh_dong="SAO_LUU_HANG_NGAY",
        doi_tuong=manifest["duong_dan_zip"],
        ket_qua="OK",
        chi_tiet={"so_file": len(file_hashes), "kich_thuoc_bytes": manifest["kich_thuoc_zip_bytes"]},
    )
    return manifest


def run_restore_drill() -> dict:
    """Thử khôi phục 1 lần từ bản sao lưu mới nhất ra thư mục kiểm chứng độc lập và đối chiếu SHA-256."""
    manifest = run_daily_backup(force=True)
    zip_path = ROOT_DIR / manifest["duong_dan_zip"]
    expected_hashes = manifest.get("hashes_sha256", {})

    t0 = time.perf_counter()
    mismatches = []
    restored_count = 0

    with tempfile.TemporaryDirectory(prefix="restore_drill_01_") as tmp_dir:
        tmp_path = Path(tmp_dir)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp_path)

        for rel, exp_hash in expected_hashes.items():
            restored_file = tmp_path / rel
            if not restored_file.exists():
                mismatches.append({"file": rel, "ly_do": "MISSING_AFTER_EXTRACT"})
                continue
            actual_hash = _sha256_file(restored_file)
            if actual_hash != exp_hash:
                mismatches.append({"file": rel, "ly_do": "SHA256_MISMATCH"})
            else:
                restored_count += 1

    drill_report = {
        "san_pham": "01_MAY_TAO_NOI_DUNG",
        "thoi_diem_khoi_phuc_thu": datetime.now().isoformat(timespec="seconds"),
        "ban_sao_luu_nguon": manifest["duong_dan_zip"],
        "tong_so_file_kiem_tra": len(expected_hashes),
        "so_file_khoi_phuc_khop_sha256": restored_count,
        "so_file_sai_lech": len(mismatches),
        "thanh_cong_100_pct": len(mismatches) == 0 and restored_count == len(expected_hashes),
        "thoi_gian_khoi_phuc_ms": round((time.perf_counter() - t0) * 1000.0, 1),
        "chi_tiet_sai_lech": mismatches,
    }
    report_path = SAO_LUU_DIR / "BAO_CAO_KHOI_PHUC_THU.json"
    report_path.write_text(json.dumps(drill_report, ensure_ascii=False, indent=2), encoding="utf-8")
    ghi_nhat_ky(
        nguoi_dung="QuanTriVienLocal",
        hanh_dong="KHOI_PHUC_THU_1_LAN",
        doi_tuong=manifest["duong_dan_zip"],
        ket_qua="OK" if drill_report["thanh_cong_100_pct"] else "ERROR",
        chi_tiet={
            "so_file_khop_sha256": restored_count,
            "thoi_gian_ms": drill_report["thoi_gian_khoi_phuc_ms"],
        },
    )
    return drill_report


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--auto-daily", action="store_true")
    ap.add_argument("--test-restore", action="store_true")
    args = ap.parse_args()
    if args.test_restore:
        res = run_restore_drill()
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        res = run_daily_backup(force=not args.auto_daily)
        print(json.dumps({k: v for k, v in res.items() if k != "hashes_sha256"}, ensure_ascii=False, indent=2))
