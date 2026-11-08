"""Bộ test cổng linhx-report: mỗi ca hỏng chỉ khác bản tốt đúng một chỗ, cổng phải bắt được.

Chạy: python tests/test_cong.py   (cần typst trên PATH hoặc TYPST_BIN cho ca dựng PDF)
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC / "scripts"))
import report  # noqa: E402

TOT = {
    "03-nguon.csv": "ma,ten,don_vi,url,ngay_xuat_ban,ngay_truy_cap,loai,tang,ghi_chu\n"
                    "S01,Khảo sát A,Đơn vị A,https://a.vn,2026-01,2026-10-13,thu-cap,A,\n"
                    "S02,Báo cáo B,Đơn vị B,https://b.vn,2026-02,2026-10-13,thu-cap,B,\n",
    "03-bang-chung.jsonl": json.dumps({"id": "BC01", "nguon": "S01", "chi_so": "tỷ lệ dùng", "trich": "39% người lao động dùng AI, tăng từ 16%", "so": [39, 16]}, ensure_ascii=False) + "\n"
                          + json.dumps({"id": "BC02", "nguon": "S02", "chi_so": "tỷ lệ dùng", "trich": "Doanh nghiệp: 18% đã ứng dụng", "so": [18]}, ensure_ascii=False) + "\n",
    "04-hinh.json": json.dumps({"hinh": [{"id": "H01", "loai": "thanh-ngang", "tieu_de": "Người lao động dùng AI nhiều gấp đôi doanh nghiệp.",
                                          "doi_tuong": "% người trả lời", "don_vi": "%", "nhan": ["Người lao động", "Doanh nghiệp"],
                                          "chuoi": [{"ten": "2026", "gia_tri": [39, 18], "bc": ["BC01", "BC02"]}], "nhan_manh": "Người lao động",
                                          "nguon": "Khảo sát A, 2026."}]}, ensure_ascii=False),
    "06-chuong/00-tom-tat.md": "# Những điểm chính\n> Người dùng đi trước tổ chức.\n"
                               "1. **Người lao động đi trước doanh nghiệp.** Có 39% người lao động dùng AI [BC01].\n"
                               "2. **Doanh nghiệp dùng còn nông.** Chỉ 18% doanh nghiệp đã ứng dụng [BC02].\n"
                               "3. **Khoảng cách đang nới rộng.** Tỷ lệ người dùng tăng từ 16% lên 39% [BC01].\n",
    "06-chuong/01-nguoi-dung.md": "# Người dùng đang đi trước tổ chức | Người dùng\n> Sapô ngắn.\n\n"
                                  "Có 39% người lao động dùng AI [BC01]. Doanh nghiệp mới đạt 18% [BC02].\n\n::: hinh H01\n\n"
                                  "## Doanh nghiệp cần đào tạo nhiều hơn\nĐoạn văn không có số.\n",
}


def tao(sua=None):
    d = Path(tempfile.mkdtemp(prefix="lr-test-"))
    report.moi(d, "Báo cáo thử", "p1-chien-luoc", "linhx")
    for k, v in TOT.items():
        (d / k).parent.mkdir(parents=True, exist_ok=True)
        (d / k).write_text(v, encoding="utf-8")
    if sua:
        sua(d)
    return d


def ve(d):
    subprocess.run([sys.executable, str(GOC / "scripts" / "hinh.py"), str(d)], check=True, capture_output=True)


def kq_cong(d, n):
    k = report.KQ()
    {3: report.cong_3, 4: report.cong_4, 5: report.cong_5, 6: report.kiem_van}.get(n, lambda d, k: None)(d, k) \
        if n != 7 else report.kiem_so(d, k, ghi=False)
    return k


def thay(tep, cu, moi):
    def f(d):
        p = d / tep
        p.write_text(p.read_text(encoding="utf-8").replace(cu, moi), encoding="utf-8")
    return f


CA = [
    ("ban tot qua cong 6", None, 6, True),
    ("ban tot qua cong 7", None, 7, True),
    ("ban tot qua cong 4", None, 4, True),
    ("so khong nguon", thay("06-chuong/01-nguoi-dung.md", "Doanh nghiệp mới đạt 18% [BC02].", "Doanh nghiệp mới đạt 18%."), 6, False),
    ("ma bang chung khong ton tai", thay("06-chuong/01-nguoi-dung.md", "[BC02]", "[BC09]"), 6, False),
    ("so lech nguon (mo coi)", thay("06-chuong/01-nguoi-dung.md", "18% [BC02]", "28% [BC02]"), 7, False),
    ("tieu de chuong la cum danh tu", thay("06-chuong/01-nguoi-dung.md", "# Người dùng đang đi trước tổ chức", "# Thực trạng người dùng AI"), 6, False),
    ("tieu de hinh khong phai cau", thay("04-hinh.json", "doanh nghiệp.\"", "doanh nghiệp\""), 4, False),
    ("hinh thieu nguon", thay("04-hinh.json", "\"nguon\": \"Khảo sát A, 2026.\"", "\"nguon\": \"\""), 4, False),
    ("gia tri hinh khong co trong bang chung", thay("04-hinh.json", "[39, 18]", "[39, 25]"), 4, False),
    ("so kieu Anh", thay("06-chuong/01-nguoi-dung.md", "Đoạn văn không có số.", "Khoảng 1,200 người [BC01]."), 6, False),
    ("gach ngang dai", thay("06-chuong/01-nguoi-dung.md", "Đoạn văn không có số.", "Đoạn văn — không có số."), 6, False),
    ("tom tat chi 2 diem", thay("06-chuong/00-tom-tat.md", "3. **Khoảng cách đang nới rộng.** Tỷ lệ người dùng tăng từ 16% lên 39% [BC01].\n", ""), 6, False),
    ("nguon tang C qua nhieu", thay("03-nguon.csv", ",A,\n", ",C,\n"), 3, False),
    ("trich dan khong khop nguyen van", thay("06-chuong/01-nguoi-dung.md", "Đoạn văn không có số.", "Báo cáo viết “người lao động dùng AI rất nhiều mỗi ngày” [BC01]."), 7, False),
]


def main():
    dat = 0
    for ten, sua, n, mong in CA:
        d = tao(sua)
        ve(d)
        k = kq_cong(d, n)
        ok = k.dat() == mong
        dat += ok
        print(("ĐẠT " if ok else "SAI ") + f"{ten}: cổng {n} {'qua' if k.dat() else 'chặn'}" + ("" if ok else f" | {k.loi[:2]}"))
        shutil.rmtree(d, ignore_errors=True)
    # dựng PDF + kiểm bản in (bỏ qua nếu không có typst)
    try:
        report.tim_typst()
        d = tao()
        ve(d)
        report.dung(d)
        k = report.KQ()
        report.kiem_ban_in(d, k, ghi=False)
        loi_khac = [x for x in k.loi if "11-cham-trang" not in x]
        ok = not loi_khac and any("11-cham-trang" in x for x in k.loi)
        dat += ok
        CA.append(("dung PDF va kiem ban in", None, 11, True))
        print(("ĐẠT " if ok else "SAI ") + f"dựng PDF + kiểm bản in: lỗi khác ngoài chấm trang = {loi_khac[:3]}")
        shutil.rmtree(d, ignore_errors=True)
    except SystemExit as e:
        print("bỏ qua ca dựng PDF:", e)
    print(f"{dat}/{len(CA)} ca đạt")
    sys.exit(0 if dat == len(CA) else 1)


if __name__ == "__main__":
    main()
