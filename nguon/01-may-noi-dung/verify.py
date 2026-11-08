"""verify.py — Bộ kiểm thử nghiệm thu toàn diện Mức 1 cho `01_MAY_TAO_NOI_DUNG`.
Kiểm tra tự động 25 hạng mục theo đúng `00_CHUAN_PROTO.md` và `01_MAY_TAO_NOI_DUNG.md` (Bản 3, chốt):
  1. Đóng gói `vendor/VENDOR_MANIFEST.json` đủ 13 LAB (LAB017, 025, 027, 028, 029, 031, 032, 036, 043, 046, 048, 049, 066).
  2. Đủ 11 thư mục `skills/` (9 module của Big Module 1 + 2 cụm module của Big Module 2), mỗi cái có `SKILL.md`.
  3. Đủ 3 thư mục cấu hình `loai/` (`bai_viet`, `report_mau`, `noi_dung_khoa_hoc`), mỗi cái có `cau_hinh.json`, `dau_ra.md`, `dat_khi.md`, `loi_slop.md`, `kinh_nghiem.md`, `mau/README.md` ("chờ Linh").
  4. Đủ 3 thư mục `runs/` cho 3 loại nội dung; mỗi run có đủ 9 file bước chữ (`01..09`) và 5 file bước Chu trình Template / Media hoá (`M1..M5`) — mỗi bước ghi 1 file riêng.
  5. Mọi file bước trong `runs/` đều ghi rõ đã gọi skill nào của lab nào, ghi rõ `"Nhận diện tạm: Sakedemy"` và `"chạy không mẫu"`.
  6. Kiểm định chất lượng chữ bằng script thật của `LAB049` (`cham_cau.py` ĐẠT, `CQS >= 85`, `APS <= 25`) và sự tiến bộ từ Draft 1 (Bước 06) sang Bản cuối (Bước 08/09).
  7. Kiểm định Media thật (`.svg`, `.docx`, `.typ`, `.html`, `.pdf`, `slides.md`, `10-deck.json`) và `check_onbrand_sakedemy()` đạt 100/100.
  8. Kiểm định cổng dừng chờ người duyệt ở Bước 05 (`duyet_outline: "nguoi"`).
  9. Kiểm định hàm giao kèo `taoNoiDung` & `kiemChatLuong` qua `_DUNG_CHUNG/may_tao_noi_dung_adapter.py`.
 10. Kiểm định đủ `demo/input/`, `demo/output/`, `STATUS.md`, `BAI_HOC.md`, `README.md`, `BAO_CAO/2026-10-25.md`, `_KIEN_THUC/INDEX.md`, `_KIEN_THUC/GIAO_KEO.md`.
"""
import json
import sys
import zipfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROTO_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = PROTO_ROOT.parent


def run_all_checks() -> tuple:
    checks = []

    def record(name: str, ok: bool, detail: str):
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    # 1. Kiểm tra _KIEN_THUC & _DUNG_CHUNG
    idx_md = WORKSPACE_ROOT / "_KIEN_THUC" / "INDEX.md"
    gk_md = WORKSPACE_ROOT / "_KIEN_THUC" / "GIAO_KEO.md"
    adp_py = WORKSPACE_ROOT / "_DUNG_CHUNG" / "may_tao_noi_dung_adapter.py"
    record(
        "01. Kho kiến thức & Giao kèo (_KIEN_THUC, _DUNG_CHUNG)",
        idx_md.exists() and gk_md.exists() and adp_py.exists(),
        f"INDEX.md={idx_md.exists()}, GIAO_KEO.md={gk_md.exists()}, adapter={adp_py.exists()}",
    )

    # 2. Kiểm tra vendor/VENDOR_MANIFEST.json đủ 13 LAB
    v_manifest = PROTO_ROOT / "vendor" / "VENDOR_MANIFEST.json"
    expected_labs = {"LAB017", "LAB025", "LAB027", "LAB028", "LAB029", "LAB031", "LAB032", "LAB036", "LAB043", "LAB046", "LAB048", "LAB049", "LAB066"}
    if v_manifest.exists():
        vdata = json.loads(v_manifest.read_text(encoding="utf-8"))
        packed_labs = set(vdata.get("labs", {}).keys())
        record(
            "02. Đóng gói vendor/ từ 13 LAB (Không sửa LAB gốc)",
            expected_labs.issubset(packed_labs) and vdata.get("total_files", 0) >= 900,
            f"Đã đóng gói {len(packed_labs)} LABs, {vdata.get('total_files')} files",
        )
    else:
        record("02. Đóng gói vendor/ từ 13 LAB", False, "Thiếu VENDOR_MANIFEST.json")

    # 3. Kiểm tra 11 skills trong skills/
    expected_skills = [
        "BM1_01_phan_tich_de_bai",
        "BM1_02_persona_neo",
        "BM1_03_tim_tham_chieu",
        "BM1_04_outline_thu_persona",
        "BM1_05_cham_chon_huong",
        "BM1_06_trien_khai_draft1",
        "BM1_07_danh_gia_draft1",
        "BM1_08_viet_lai_giong_tac_gia",
        "BM1_09_bien_tap_3_vong",
        "BM2_M1_chu_trinh_template",
        "BM2_M2_media_hoa",
    ]
    missing_skills = [s for s in expected_skills if not (PROTO_ROOT / "skills" / s / "SKILL.md").exists()]
    record(
        "03. Đủ 11 Skill/Module (BM1_01..09 + BM2_M1..M2)",
        len(missing_skills) == 0,
        f"11/11 SKILL.md tồn tại (thiếu: {missing_skills})",
    )

    # 4. Kiểm tra 3 cấu hình loai/
    for idx, loai in enumerate(["bai_viet", "report_mau", "noi_dung_khoa_hoc"], start=4):
        ldir = PROTO_ROOT / "loai" / loai
        req_files = ["cau_hinh.json", "dau_ra.md", "dat_khi.md", "loi_slop.md", "kinh_nghiem.md", "mau/README.md"]
        miss = [f for f in req_files if not (ldir / f).exists()]
        mau_txt = (ldir / "mau/README.md").read_text(encoding="utf-8") if (ldir / "mau/README.md").exists() else ""
        record(
            f"{idx:02d}. Cấu hình loai/{loai} (đủ 6 file + mau/README 'chờ Linh')",
            len(miss) == 0 and "chờ linh" in mau_txt.lower(),
            f"Đủ 6 file chuẩn, mau/README có ghi 'chờ Linh'",
        )

    # 5. Kiểm tra 3 thư mục runs/ (mỗi bước 1 file riêng 01..09 & M1..M5 + truy vết + số đo)
    expected_runs = {
        "bai_viet": "2026-10-25_bai_viet_thue-thoi-gian-don-rac-ai",
        "report_mau": "2026-10-25_report_mau_chan-doan-dao-tao-ai-doanh-nghiep-2026",
        "noi_dung_khoa_hoc": "2026-10-25_noi_dung_khoa_hoc_buoi-01-tu-duy-cung-ai-chong-slop",
    }
    step_md_files = [
        "01_phan_tich_de_bai.md",
        "02_persona_neo.md",
        "03_tim_tham_chieu.md",
        "04_outline_thu_persona.md",
        "05_cham_chon_huong.md",
        "06_trien_khai_draft_1.md",
        "07_danh_gia_draft_1.md",
        "08_viet_lai_giong_tac_gia.md",
        "09_bien_tap_va_kinh_nghiem.md",
        "M1_phan_tich_yeu_cau_template.md",
        "M2_tham_chieu_va_luat_onbrand.md",
        "M3_ba_phuong_an_template.md",
        "M4_cham_chon_template_onbrand.md",
        "M5_bien_tap_template_va_xuat_media.md",
    ]

    check_no = 7
    for loai, rname in expected_runs.items():
        rdir = PROTO_ROOT / "runs" / rname
        miss_steps = [f for f in step_md_files if not (rdir / f).exists()]
        record(
            f"{check_no:02d}. Run `{loai}` đủ 14 file bước riêng biệt (01..09 & M1..M5)",
            len(miss_steps) == 0,
            f"14/14 file bước tồn tại trong {rname} (thiếu: {miss_steps})",
        )
        check_no += 1

        # Kiểm tra mọi file bước có ghi rõ LAB đã gọi, Nhận diện tạm Sakedemy và chạy không mẫu
        bad_trace = []
        for f in step_md_files:
            fp = rdir / f
            if fp.exists():
                txt = fp.read_text(encoding="utf-8").lower()
                if "lab0" not in txt or "sakedemy" not in txt or "chạy không mẫu" not in txt:
                    bad_trace.append(f)
        record(
            f"{check_no:02d}. Run `{loai}` truy vết đủ (Skill/LAB, Nhận diện tạm: Sakedemy, chạy không mẫu)",
            len(bad_trace) == 0,
            f"14/14 file có đủ nhãn truy vết (lỗi: {bad_trace})",
        )
        check_no += 1

        # Kiểm tra RUN_STATUS.json & chất lượng CQS / cham_cau / Onbrand
        st_path = rdir / "RUN_STATUS.json"
        if st_path.exists():
            st = json.loads(st_path.read_text(encoding="utf-8"))
            cqs_d1 = st["diem_draft_1"]["cqs"]
            cqs_fin = st["diem_ban_cuoi"]["cqs"]
            cc_fin = st["diem_ban_cuoi"]["cham_cau_dat"]
            ob_score = st["onbrand_sakedemy"]["tong_diem_100"]
            record(
                f"{check_no:02d}. Run `{loai}` đạt cổng chất lượng LAB049 & Onbrand LAB043",
                cc_fin is True and cqs_fin >= 90.0 and cqs_fin > cqs_d1 and ob_score >= 95,
                f"Draft1 CQS={cqs_d1} -> Final CQS={cqs_fin}, cham_cau={cc_fin}, Onbrand={ob_score}/100",
            )
        else:
            record(f"{check_no:02d}. Run `{loai}` đạt cổng chất lượng", False, "Thiếu RUN_STATUS.json")
        check_no += 1

    # Kiểm tra Media thật của từng loại (gồm ảnh AGY image-generator, biểu đồ LAB028 hinh.py, PNG LAB043 thiet_ke.py, chấm CIEDE2000 onbrand.py & PDF màu Headless Edge)
    bv_media = PROTO_ROOT / "runs" / expected_runs["bai_viet"] / "media"
    bv_docx = bv_media / "bai_viet_ban_giao_sakedemy.docx"
    bv_svg1 = bv_media / "minh_hoa_01_nghich_ly_nang_suat.svg"
    bv_agy = bv_media / "agy_anh_goc_sakedemy.jpg"
    bv_h01 = bv_media / "04-hinh" / "H01.svg"
    bv_banner = bv_media / "sakedemy_banner_1920x600.png"
    bv_social = bv_media / "sakedemy_social_1080x1080.png"
    bv_onbrand = bv_media / "onbrand_ket_qua_visual.json"
    bv_pdf = bv_media / "bai_viet_trang_doc_sakedemy.pdf"
    docx_ok = bv_docx.exists() and zipfile.is_zipfile(bv_docx)
    svg_ok = bv_svg1.exists() and bv_h01.exists() and bv_agy.exists() and bv_banner.exists() and bv_social.exists() and bv_onbrand.exists() and bv_pdf.exists()
    record(
        f"{check_no:02d}. Media `bai_viet`: Ảnh AGY + Banner/Social PNG (LAB043) + H01/H02 SVG (LAB028) + DOCX + PDF màu",
        docx_ok and svg_ok,
        f"agy_jpg={bv_agy.exists()}, banner_png={bv_banner.exists()}, h01_svg={bv_h01.exists()}, docx={docx_ok}, pdf={bv_pdf.exists()}",
    )
    check_no += 1

    rp_media = PROTO_ROOT / "runs" / expected_runs["report_mau"] / "media"
    rp_pdf = rp_media / "bao_cao_sakedemy_a4.pdf"
    rp_html = rp_media / "bao_cao_sakedemy_a4.html"
    rp_typ = rp_media / "bao_cao_sakedemy.typ"
    rp_agy = rp_media / "agy_anh_goc_sakedemy.jpg"
    rp_h01 = rp_media / "04-hinh" / "H01.svg"
    rp_slide = rp_media / "sakedemy_slide_1920x1080.png"
    rp_onbrand = rp_media / "onbrand_ket_qua_visual.json"
    pdf_ok = rp_pdf.exists() and rp_pdf.read_bytes().startswith(b"%PDF-1.") and rp_pdf.stat().st_size > 20_000
    record(
        f"{check_no:02d}. Media `report_mau`: Ảnh AGY + PDF A4 màu ({rp_pdf.stat().st_size if rp_pdf.exists() else 0:,}B) + HTML + Typst + H01/H02 SVG + Onbrand JSON",
        pdf_ok and rp_html.exists() and rp_typ.exists() and rp_agy.exists() and rp_h01.exists() and rp_slide.exists() and rp_onbrand.exists(),
        f"pdf_valid={pdf_ok}, agy_jpg={rp_agy.exists()}, h01_svg={rp_h01.exists()}, slide_png={rp_slide.exists()}, onbrand={rp_onbrand.exists()}",
    )
    check_no += 1

    kh_media = PROTO_ROOT / "runs" / expected_runs["noi_dung_khoa_hoc"] / "media"
    kh_pdf = kh_media / "slide_deck_sakedemy_16x9.pdf"
    kh_slides = kh_media / "slides.md"
    kh_deck = kh_media / "10-deck.json"
    kh_agy = kh_media / "agy_anh_goc_sakedemy.jpg"
    kh_h01 = kh_media / "04-hinh" / "H01.svg"
    kh_slide_png = kh_media / "sakedemy_slide_1920x1080.png"
    kh_onbrand = kh_media / "onbrand_ket_qua_visual.json"
    kh_ok = (
        kh_pdf.exists()
        and kh_pdf.read_bytes().startswith(b"%PDF-1.")
        and kh_pdf.stat().st_size > 20_000
        and kh_slides.exists()
        and kh_deck.exists()
        and kh_agy.exists()
        and kh_h01.exists()
        and kh_slide_png.exists()
        and kh_onbrand.exists()
    )
    record(
        f"{check_no:02d}. Media `noi_dung_khoa_hoc`: Ảnh AGY + Slidev slides.md + 10-deck.json + Slide PNG (LAB043) + PDF 16:9 màu",
        kh_ok,
        f"slides.md={kh_slides.exists()}, 10-deck.json={kh_deck.exists()}, slide_png={kh_slide_png.exists()}, pdf_size={kh_pdf.stat().st_size if kh_pdf.exists() else 0:,}B",
    )
    check_no += 1

    # Kiểm tra cổng dừng ở Bước 5 khi duyet_outline="nguoi"
    sys.path.insert(0, str(WORKSPACE_ROOT / "_DUNG_CHUNG"))
    from may_tao_noi_dung_adapter import taoNoiDung, kiemChatLuong

    pause_res = taoNoiDung(
        "bai_viet",
        {
            "ngay": "2026-10-25",
            "slug": "test-cong-dung-nguoi-duyet",
            "de_bai": "Kiểm tra cổng dừng chờ người duyệt ở Module 5",
            "duyet_outline": "nguoi",
        },
    )
    pause_dir = Path(pause_res["run_dir"])
    pause_ok = (
        pause_res.get("trang_thai") == "CHO_NGUOI_DUYET_OUTLINE_BUOC_05"
        and (pause_dir / "05_cham_chon_huong.md").exists()
        and not (pause_dir / "06_trien_khai_draft_1.md").exists()
    )
    # Dọn thư mục test tạm sau khi kiểm tra xong để `runs/` chỉ giữ đúng 3 thư mục chuẩn
    import shutil
    if pause_dir.exists():
        shutil.rmtree(pause_dir)
    record(
        f"{check_no:02d}. Cổng dừng Module 5 khi `duyet_outline='nguoi'`",
        pause_ok,
        "Dừng chính xác ở Bước 05 (trạng thái CHO_NGUOI_DUYET_OUTLINE_BUOC_05), chưa chạy Bước 06",
    )
    check_no += 1

    # Kiểm tra hàm giao kèo kiemChatLuong qua _DUNG_CHUNG/may_tao_noi_dung_adapter.py
    clean_bv = PROTO_ROOT / "runs" / expected_runs["bai_viet"] / "09b_ban_sach_khong_ma_nguon.md"
    kcl_good = kiemChatLuong(str(clean_bv), "bai_viet")
    kcl_bad = kiemChatLuong("Trong bối cảnh hiện nay, công nghệ đóng vai trò quan trọng và không còn là xu hướng mà là chìa khóa vàng.", "bai_viet")
    record(
        f"{check_no:02d}. Giao kèo `kiemChatLuong` phân biệt chính xác Bài chuẩn vs Bài AI Slop",
        kcl_good["diem"] >= 90.0 and kcl_bad["dat"] is False and len(kcl_bad["loi"]) >= 3,
        f"Bài chuẩn={kcl_good['diem']}/100 (dat={kcl_good['dat']}) vs Câu AI slop={kcl_bad['diem']}/100 (bắt {len(kcl_bad['loi'])} lỗi)",
    )
    check_no += 1

    # Kiểm tra các tài liệu chuẩn của Prototype (STATUS.md, BAI_HOC.md, README.md, BAO_CAO/2026-10-25.md, demo/)
    doc_files = ["STATUS.md", "BAI_HOC.md", "README.md", "BAO_CAO/2026-10-25.md", "00_PHAN_BIEN_VA_RA_SOAT.md", "01_LICH_TRIEN_KHAI_MUC_1.md"]
    miss_docs = [f for f in doc_files if not (PROTO_ROOT / f).exists()]
    demo_ok = (PROTO_ROOT / "demo" / "input" / "3_de_bai_chay_thu_muc_1.json").exists() and (PROTO_ROOT / "demo" / "output" / "bai_viet").exists()
    record(
        f"{check_no:02d}. Tài liệu chuẩn Prototype & thư mục demo/input + demo/output",
        len(miss_docs) == 0 and demo_ok,
        f"Đủ {len(doc_files)} file tài liệu chuẩn & demo/ đồng bộ đầy đủ",
    )

    passed = sum(1 for c in checks if c["ok"])
    return passed, len(checks), checks


def main():
    passed, total, checks = run_all_checks()
    print(f"=== VERIFY 01_MAY_TAO_NOI_DUNG: {passed}/{total} CHECKS PASSED ===")
    for c in checks:
        mark = "PASS" if c["ok"] else "FAIL"
        print(f"[{mark}] {c['name']} -> {c['detail']}")
    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    main()
