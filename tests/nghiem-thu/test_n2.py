"""N2: chép PROTO 03 OPC OS và 01 Máy nội dung vào nguon/ (chỉ đọc, không chạy); không .env, khoá, dữ liệu khách."""
import re

from _chung import GOC, cac_file, file_bi_mat, quet_bi_mat

NGUON = GOC / "nguon"
HAI_NGUON = ["03-opc-os", "01-may-noi-dung"]
DUOI_DU_LIEU = {".db", ".sqlite", ".sqlite3", ".xlsx", ".xls", ".parquet", ".dump", ".bak", ".sql"}


def test_co_hai_nguon_voi_readme_va_module_goc():
    for ten in HAI_NGUON:
        d = NGUON / ten
        assert d.is_dir(), f"thiếu nguon/{ten}"
        assert (d / "README.md").exists(), f"thiếu nguon/{ten}/README.md"
        assert list(d.rglob("module.py")), f"nguon/{ten} không có module.py gốc nào"


def test_co_so_ghi_nguon_goc():
    p = NGUON / "NGUON.md"
    assert p.exists(), "thiếu nguon/NGUON.md ghi đường dẫn gốc và ngày chép"
    chu = p.read_text(encoding="utf-8")
    for ten in HAI_NGUON:
        assert ten in chu, f"NGUON.md chưa ghi {ten}"
    assert re.search(r"20\d\d-\d\d-\d\d", chu), "NGUON.md chưa ghi ngày chép (YYYY-MM-DD)"


def test_khong_env_khoa():
    loi = file_bi_mat(NGUON)
    assert not loi, "nguon/ có file bí mật: " + ", ".join(loi)
    loi = quet_bi_mat(NGUON)
    assert not loi, "nguon/ có chuỗi giống bí mật: " + "; ".join(loi[:10])


def test_khong_du_lieu_khach():
    loi = []
    for p in cac_file(NGUON):
        duoi = p.suffix.lower()
        if duoi in DUOI_DU_LIEU:
            loi.append(str(p))
        elif duoi in {".csv", ".json", ".jsonl"} and p.stat().st_size > 50_000:
            loi.append(f"{p} ({p.stat().st_size} byte, quá lớn cho dữ liệu mẫu)")
        elif re.search(r"(?i)(khach|customer|lead|zalo-logs|export)", p.name) and duoi in {".csv", ".json", ".jsonl", ".txt"}:
            loi.append(f"{p} (tên giống dữ liệu khách)")
    assert not loi, "nguon/ có thứ giống dữ liệu khách: " + "; ".join(loi[:10])


def test_nguon_chi_doc_khong_bi_import():
    loi = []
    for p in (GOC / "apps").rglob("*.py"):
        chu = p.read_text(encoding="utf-8", errors="ignore")
        # "nguon" còn là tên trường (nguồn lead), nên chỉ bắt import thật, sys.path hoặc nạp file từ nguon/ trên cùng dòng; chuỗi ghi gốc "Chuyển từ: nguon/..." vẫn được.
        if (re.search(r"^\s*(from|import)\s+nguon\b", chu, re.M)
                or re.search(r"sys\.path.*nguon", chu)
                or re.search(r"(spec_from_file_location|SourceFileLoader|runpy|exec\(open)\(?.*nguon", chu)):
            loi.append(str(p))
    assert not loi, "code chạy không được import từ nguon/ (chỉ chép logic sang): " + ", ".join(loi)


def test_dung_luong_vua_phai():
    tong = sum(p.stat().st_size for p in cac_file(NGUON))
    assert tong < 50 * 1024 * 1024, f"nguon/ nặng {tong // 1048576} MB, quá 50 MB (bỏ ảnh/video/thư viện)"
