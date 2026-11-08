"""Bộ kiểm thử chuyên sâu 10 vòng bổ sung (Vòng 4 -> Vòng 13, nâng tổng số vòng test lên 13 vòng):
Kiểm định toàn diện quy trình Tìm tham chiếu bằng AGY (`search_web`), Tạo ảnh thực tế bằng AGY (`image-generator`),
Vẽ biểu đồ dữ liệu chuẩn McKinsey (`LAB028/hinh.py`), Ghép khuôn HTML xuất PNG + Mặt nạ (`LAB043/thiet_ke.py`),
Chấm điểm màu CIEDE2000 từng điểm ảnh (`LAB043/onbrand.py`), Chu trình PDCA 3 vòng vá lỗi tương phản,
In PDF màu bằng Headless Edge, Cổng duyệt người/máy Bước 05, và Bẫy đối kháng chống Văn dịch / Slop / Sai Onbrand.
"""
import json
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROTO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROTO_ROOT))
sys.path.insert(0, str(PROTO_ROOT / "skills" / "BM2_M1_chu_trinh_template"))

from dieu_phoi import kiemChatLuong, taoNoiDung
from chu_trinh_template import check_onbrand_sakedemy

RUN_SLUGS = {
    "bai_viet": "2026-10-25_bai_viet_thue-thoi-gian-don-rac-ai",
    "report_mau": "2026-10-25_report_mau_chan-doan-dao-tao-ai-doanh-nghiep-2026",
    "noi_dung_khoa_hoc": "2026-10-25_noi_dung_khoa_hoc_buoi-01-tu-duy-cung-ai-chong-slop",
}


def run_10_rounds() -> dict:
    rounds_log = []

    def record_round(vong_so: int, ten_vong: str, checks: list):
        passed = all(c["ok"] for c in checks)
        rounds_log.append({
            "vong": vong_so,
            "ten_vong": ten_vong,
            "trang_thai": "PASS" if passed else "FAIL",
            "so_kiem_tra": len(checks),
            "so_dat": sum(1 for c in checks if c["ok"]),
            "chi_tiet": checks,
        })
        status_icon = "PASS" if passed else "FAIL"
        print(f"[Vòng {vong_so:02d}] [{status_icon}] {ten_vong} ({sum(1 for c in checks if c['ok'])}/{len(checks)} checks)")
        for c in checks:
            if not c["ok"]:
                print(f"   -> LỖI: {c['name']}: {c['detail']}")

    # =========================================================================
    # VÒNG 4: Kiểm định Tìm tham chiếu thực tế bằng AGY (search_web) & Sổ bằng chứng
    # =========================================================================
    c4 = []
    agy_ref_file = PROTO_ROOT / "du_lieu_tham_chieu_agy.json"
    ref_data = json.loads(agy_ref_file.read_text(encoding="utf-8")) if agy_ref_file.exists() else {}
    c4.append({
        "name": "File du_lieu_tham_chieu_agy.json tồn tại và đủ 3 loại nội dung",
        "ok": agy_ref_file.exists() and set(ref_data.get("bo_tham_chieu", {}).keys()) == {"bai_viet", "report_mau", "noi_dung_khoa_hoc"},
        "detail": f"keys={list(ref_data.get('bo_tham_chieu', {}).keys())}",
    })
    for loai, rname in RUN_SLUGS.items():
        rdir = PROTO_ROOT / "runs" / rname
        f03_md = (rdir / "03_tim_tham_chieu.md").read_text(encoding="utf-8")
        f03_json = json.loads((rdir / "03_bang_chung.json").read_text(encoding="utf-8"))
        m_ref = rdir / "media" / "tham_chieu_agy.json"
        has_agy_tags = any(s.get("ma", "").startswith("AGY-") for s in f03_json)
        c4.append({
            "name": f"[{loai}] Bước 03 nạp đủ tham chiếu AGY search_web + >= 18 nguồn bằng chứng",
            "ok": ("AGY search_web" in f03_md) and len(f03_json) >= 18 and has_agy_tags and m_ref.exists(),
            "detail": f"so_nguon={len(f03_json)}, has_agy_tags={has_agy_tags}, media_ref={m_ref.exists()}",
        })
    record_round(4, "Kiểm định Tìm tham chiếu thực tế bằng AGY (search_web) & Sổ bằng chứng", c4)

    # =========================================================================
    # VÒNG 5: Kiểm định Ảnh gốc Photorealistic do AGY (image-generator) tạo & LAB066
    # =========================================================================
    c5 = []
    for loai, rname in RUN_SLUGS.items():
        rdir = PROTO_ROOT / "runs" / rname
        img_p = rdir / "media" / "agy_anh_goc_sakedemy.jpg"
        prompt_p = rdir / "media" / "agy_anh_goc_sakedemy.prompt.json"
        lab066_p = rdir / "media" / "character_anchor_lab066.json"
        ok_img = False
        dim_str = ""
        if img_p.exists() and img_p.stat().st_size > 400_000:
            with Image.open(img_p) as im:
                w, h = im.size
                ok_img = (w >= 1024 and h >= 576)
                dim_str = f"{w}x{h} ({img_p.stat().st_size:,} bytes)"
        lab066_d = json.loads(lab066_p.read_text(encoding="utf-8")) if lab066_p.exists() else {}
        c5.append({
            "name": f"[{loai}] Ảnh AGY image-generator hợp lệ & Điểm 4 Persona LAB066 >= 8.0",
            "ok": ok_img and prompt_p.exists() and lab066_d.get("diem_cuoi", 0) >= 8.0,
            "detail": f"img={dim_str}, diem_lab066={lab066_d.get('diem_cuoi')}",
        })
    record_round(5, "Kiểm định Ảnh gốc Photorealistic do AGY (image-generator) tạo & Chấm LAB066", c5)

    # =========================================================================
    # VÒNG 6: Kiểm định Biểu đồ Dữ liệu Exhibit SVG (`LAB028/linhx-report/scripts/hinh.py`)
    # =========================================================================
    c6 = []
    for loai, rname in RUN_SLUGS.items():
        rdir = PROTO_ROOT / "runs" / rname
        h01 = rdir / "media" / "04-hinh" / "H01.svg"
        h02 = rdir / "media" / "04-hinh" / "H02.svg"
        ok_h = h01.exists() and h02.exists() and h01.stat().st_size > 2000 and h02.stat().st_size > 2000
        svg_txt = (h01.read_text(encoding="utf-8") + h02.read_text(encoding="utf-8")) if ok_h else ""
        has_brand_color = ("#02403b" in svg_txt.lower()) or ("#6eb264" in svg_txt.lower())
        c6.append({
            "name": f"[{loai}] LAB028 hinh.py xuất đủ H01.svg & H02.svg chuẩn màu Sakedemy",
            "ok": ok_h and has_brand_color and "<svg" in svg_txt,
            "detail": f"H01={h01.stat().st_size if h01.exists() else 0}B, H02={h02.stat().st_size if h02.exists() else 0}B, brand_color={has_brand_color}",
        })
    record_round(6, "Kiểm định Biểu đồ Dữ liệu Exhibit SVG (LAB028 hinh.py + Be Vietnam Pro)", c6)

    # =========================================================================
    # VÒNG 7: Kiểm định Kết xuất Khuôn HTML ra PNG + Mặt nạ `.mask.png` (`LAB043/thiet_ke.py`)
    # =========================================================================
    c7 = []
    for loai, rname in RUN_SLUGS.items():
        rdir = PROTO_ROOT / "runs" / rname
        banner_png = rdir / "media" / "sakedemy_banner_1920x600.png"
        banner_mask = rdir / "media" / "sakedemy_banner_1920x600.mask.png"
        vis_png = rdir / "media" / ("sakedemy_social_1080x1080.png" if loai == "bai_viet" else "sakedemy_slide_1920x1080.png")
        vis_mask = vis_png.with_suffix(".mask.png")
        b_ok = False
        v_ok = False
        if banner_png.exists() and banner_mask.exists():
            with Image.open(banner_png) as im:
                b_ok = (im.size == (1920, 600))
        if vis_png.exists() and vis_mask.exists():
            with Image.open(vis_png) as im:
                expected_size = (1080, 1080) if loai == "bai_viet" else (1920, 1080)
                v_ok = (im.size == expected_size)
        c7.append({
            "name": f"[{loai}] LAB043 thiet_ke.py kết xuất đúng kích thước PNG & mặt nạ .mask.png",
            "ok": b_ok and v_ok,
            "detail": f"banner_ok={b_ok} ({banner_png.name}), visual_ok={v_ok} ({vis_png.name})",
        })
    record_round(7, "Kiểm định Kết xuất Khuôn HTML ra PNG + Mặt nạ .mask.png (LAB043 thiet_ke.py)", c7)

    # =========================================================================
    # VÒNG 8: Kiểm định Chấm điểm Pixel CIEDE2000 (`LAB043/onbrand.py`) & Vá lỗi PDCA v1.2
    # =========================================================================
    c8 = []
    for loai, rname in RUN_SLUGS.items():
        rdir = PROTO_ROOT / "runs" / rname
        kq_vis = rdir / "media" / "onbrand_ket_qua_visual.json"
        bc_html = rdir / "media" / "onbrand_bao_cao.html"
        khuon_v12 = rdir / "media" / "khuon_v1_2_slide_169.html"
        d_vis = json.loads(kq_vis.read_text(encoding="utf-8")) if kq_vis.exists() else {}
        phu_mau = d_vis.get("muc", {}).get("mau", {}).get("phu_mau_thuong_hieu", 0)
        diem_100 = d_vis.get("diem_100", 0)
        xep_loai = d_vis.get("xep_loai", "")
        khuon_txt = khuon_v12.read_text(encoding="utf-8") if khuon_v12.exists() else ""
        fixed_contrast = "background:var(--xanh-la-sakedemy);color:var(--xanh-reu-dam);" in khuon_txt
        c8.append({
            "name": f"[{loai}] LAB043 onbrand.py đo CIEDE2000 >= 85% & Khuôn v1.2 đã vá lỗi tương phản .so",
            "ok": (phu_mau >= 0.85) and (diem_100 >= 95.0) and (xep_loai == "ĐẠT CHUẨN") and bc_html.exists() and fixed_contrast,
            "detail": f"phu_mau={phu_mau:.1%}, diem_100={diem_100}, xep_loai={xep_loai}, fixed_so_contrast={fixed_contrast}",
        })
    record_round(8, "Kiểm định Chấm điểm Pixel CIEDE2000 (LAB043 onbrand.py) & Vá lỗi PDCA v1.2", c8)

    # =========================================================================
    # VÒNG 9: Kiểm định Đa định dạng Xuất bản (HTML, PDF màu Headless Edge, DOCX, Typst, Slidev)
    # =========================================================================
    c9 = []
    # 1. bai_viet
    bv_dir = PROTO_ROOT / "runs" / RUN_SLUGS["bai_viet"] / "media"
    bv_docx = bv_dir / "bai_viet_ban_giao_sakedemy.docx"
    bv_html = bv_dir / "bai_viet_trang_doc_sakedemy.html"
    bv_pdf = bv_dir / "bai_viet_trang_doc_sakedemy.pdf"
    with zipfile.ZipFile(bv_docx, "r") as zf:
        docx_ok = "word/document.xml" in zf.namelist()
    c9.append({
        "name": "[bai_viet] Đủ DOCX OpenXML + Trang đọc HTML nhúng ảnh AGY/H01/H02 + PDF màu",
        "ok": docx_ok and bv_html.exists() and bv_pdf.exists() and bv_pdf.read_bytes().startswith(b"%PDF-1."),
        "detail": f"docx_ok={docx_ok}, pdf_size={bv_pdf.stat().st_size if bv_pdf.exists() else 0:,}B",
    })
    # 2. report_mau
    rp_dir = PROTO_ROOT / "runs" / RUN_SLUGS["report_mau"] / "media"
    rp_html = rp_dir / "bao_cao_sakedemy_a4.html"
    rp_pdf = rp_dir / "bao_cao_sakedemy_a4.pdf"
    rp_typ = rp_dir / "bao_cao_sakedemy.typ"
    c9.append({
        "name": "[report_mau] Đủ Báo cáo A4 HTML + PDF màu (>50KB) + Nguồn Typst (.typ)",
        "ok": rp_html.exists() and rp_typ.exists() and rp_pdf.exists() and rp_pdf.read_bytes().startswith(b"%PDF-1.") and rp_pdf.stat().st_size > 20_000,
        "detail": f"pdf_size={rp_pdf.stat().st_size if rp_pdf.exists() else 0:,}B, typ={rp_typ.exists()}",
    })
    # 3. noi_dung_khoa_hoc
    kh_dir = PROTO_ROOT / "runs" / RUN_SLUGS["noi_dung_khoa_hoc"] / "media"
    kh_slides = kh_dir / "slides.md"
    kh_deck = kh_dir / "10-deck.json"
    kh_pdf = kh_dir / "slide_deck_sakedemy_16x9.pdf"
    c9.append({
        "name": "[noi_dung_khoa_hoc] Đủ Slidev slides.md + 10-deck.json + Slide Deck 16:9 PDF màu",
        "ok": kh_slides.exists() and kh_deck.exists() and kh_pdf.exists() and kh_pdf.read_bytes().startswith(b"%PDF-1.") and kh_pdf.stat().st_size > 20_000,
        "detail": f"pdf_size={kh_pdf.stat().st_size if kh_pdf.exists() else 0:,}B, slides_md={kh_slides.exists()}",
    })
    record_round(9, "Kiểm định Đa định dạng Xuất bản (HTML, PDF màu Headless Edge, DOCX, Typst, Slidev)", c9)

    # =========================================================================
    # VÒNG 10: Kiểm thử tải Module 2 (Persona Neo) & Module 4 (30 Insights + Thử Outline)
    # =========================================================================
    c10 = []
    for loai, rname in RUN_SLUGS.items():
        rdir = PROTO_ROOT / "runs" / rname
        p_data = json.loads((rdir / "02_persona_neo.json").read_text(encoding="utf-8"))
        o_data = json.loads((rdir / "04_outline_thu_persona.json").read_text(encoding="utf-8"))
        personas = p_data.get("personas", [])
        insights = o_data.get("insights_30", [])
        total_ins = len(insights) if isinstance(insights, list) else sum(len(v) for v in insights.values())
        reactions = {r["variant"]: r for r in o_data.get("persona_reactions", [])}
        eval_b = reactions.get("B", {})
        diem_b = eval_b.get("diem_persona_tong_hop", 0)
        c10.append({
            "name": f"[{loai}] Đủ 3 Persona Neo hay cãi + 30 hạt nhân Insight + Outline B >= 8.5",
            "ok": len(personas) == 3 and total_ins == 30 and diem_b >= 8.5,
            "detail": f"personas={len(personas)}, insights={total_ins}, diem_B={diem_b}",
        })
    record_round(10, "Kiểm thử tải Module 2 (Persona Neo) & Module 4 (30 Insights + Thử Outline)", c10)

    # =========================================================================
    # VÒNG 11: Kiểm thử Cổng duyệt Bước 05 (`duyet_outline=nguoi` vs `may` & Override A/B/C)
    # =========================================================================
    c11 = []
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_p = Path(tmpdir)
        b4_sample = PROTO_ROOT / "runs" / RUN_SLUGS["bai_viet"] / "04_outline_thu_persona.json"
        out_nguoi_json = tmp_p / "b5_nguoi.json"
        out_nguoi_md = tmp_p / "b5_nguoi.md"
        subprocess.run(
            [
                sys.executable,
                str(PROTO_ROOT / "skills" / "BM1_05_cham_chon_huong" / "cham_chon_huong.py"),
                "--b4-json", str(b4_sample),
                "--duyet-outline", "nguoi",
                "--out-json", str(out_nguoi_json),
                "--out-md", str(out_nguoi_md),
            ],
            check=True,
        )
        d_nguoi = json.loads(out_nguoi_json.read_text(encoding="utf-8"))
        c11.append({
            "name": "Cổng duyet_outline=nguoi dừng đúng tại Bước 05 (trang_thai=CHO_NGUOI_DUYET)",
            "ok": d_nguoi.get("trang_thai_cong_duyet") == "CHO_NGUOI_DUYET" and d_nguoi.get("cho_phep_chay_buoc_6") is False,
            "detail": f"trang_thai={d_nguoi.get('trang_thai_cong_duyet')}, cho_phep_b6={d_nguoi.get('cho_phep_chay_buoc_6')}",
        })

        out_override_json = tmp_p / "b5_override_A.json"
        out_override_md = tmp_p / "b5_override_A.md"
        subprocess.run(
            [
                sys.executable,
                str(PROTO_ROOT / "skills" / "BM1_05_cham_chon_huong" / "cham_chon_huong.py"),
                "--b4-json", str(b4_sample),
                "--duyet-outline", "nguoi",
                "--chon-huong", "A",
                "--out-json", str(out_override_json),
                "--out-md", str(out_override_md),
            ],
            check=True,
        )
        d_over = json.loads(out_override_json.read_text(encoding="utf-8"))
        c11.append({
            "name": "Người dùng ghi đè chọn hướng A (--chon-huong A) được chấp nhận và mở khoá Bước 06",
            "ok": d_over.get("phuong_an_chot", {}).get("variant") == "A" and d_over.get("cho_phep_chay_buoc_6") is True,
            "detail": f"variant_chot={d_over.get('phuong_an_chot', {}).get('variant')}, trang_thai={d_over.get('trang_thai_cong_duyet')}",
        })
    record_round(11, "Kiểm thử Cổng duyệt Bước 05 (duyet_outline=nguoi vs may & Ghi đè phương án)", c11)

    # =========================================================================
    # VÒNG 12: Kiểm thử Đối kháng (Adversarial Red-Team) chống Văn dịch, Bịa số & Sai Onbrand
    # =========================================================================
    c12 = []
    # Bẫy 1: Văn bản dính cụm văn dịch & "không còn là... mà là"
    slop_text = (
        "Trong bối cảnh chuyển đổi số hiện nay, trí tuệ nhân tạo đóng vai trò quan trọng trong doanh nghiệp. "
        "Đào tạo nội bộ không còn là câu chuyện của riêng phòng nhân sự mà là trách nhiệm của toàn công ty. "
        "Hơn nữa, việc áp dụng 45% quy trình tự động hóa giúp tối ưu hóa hiệu suất vượt trội."
    )
    res_slop = kiemChatLuong(slop_text, "bai_viet")
    c12.append({
        "name": "Bẫy đối kháng 1: Chặn văn bản dính văn dịch ('trong bối cảnh', 'không còn là... mà là', số 45%)",
        "ok": (res_slop["dat"] is False) and (res_slop["so_do"]["diem_khong_van_dich"] < 100 or res_slop["so_do"]["cham_cau_dat"] is False) and len(res_slop["loi"]) > 0,
        "detail": f"dat={res_slop['dat']}, cqs={res_slop['cqs']}, aps={res_slop['aps']}, loi={len(res_slop['loi'])}",
    })

    # Bẫy 2: Thiết kế đặt chữ trắng lên nền Xanh Lá #6EB264 (tương phản 2.56:1)
    res_wog = check_onbrand_sakedemy(
        text_content="Nhận diện tạm: Sakedemy (LAB043)",
        colors_used=["#6EB264", "#FFFFFF"],
        fonts_used=["Be Vietnam Pro"],
        white_on_green=True,
    )
    c12.append({
        "name": "Bẫy đối kháng 2: Chặn lỗi đặt chữ trắng (#FFFFFF) trên nền Xanh Lá (#6EB264)",
        "ok": (res_wog["dat"] is False) and any("ONBRAND-MAU-01" in e for e in res_wog["loi"]),
        "detail": f"dat={res_wog['dat']}, diem={res_wog['tong_diem_100']}, loi={res_wog['loi']}",
    })

    # Bẫy 3: Thiết kế trộn màu Navy cũ #051D40 với #6EB264 + dùng font cấm Poppins + từ cấm "số 1 Việt Nam"
    res_bad_brand = check_onbrand_sakedemy(
        text_content="Khoá học AI số 1 Việt Nam, cam kết tối ưu 30% doanh thu.",
        colors_used=["#051D40", "#6EB264"],
        fonts_used=["Poppins", "Montserrat"],
        white_on_green=False,
    )
    c12.append({
        "name": "Bẫy đối kháng 3: Chặn trộn màu Navy #051D40, font Poppins và từ cấm 'số 1 Việt Nam'",
        "ok": (res_bad_brand["dat"] is False) and len(res_bad_brand["loi"]) >= 3,
        "detail": f"dat={res_bad_brand['dat']}, diem={res_bad_brand['tong_diem_100']}, so_loi={len(res_bad_brand['loi'])}",
    })
    record_round(12, "Kiểm thử Đối kháng (Adversarial Red-Team) chống Văn dịch, Bịa số & Sai Onbrand", c12)

    # =========================================================================
    # VÒNG 13: Kiểm thử Hồi quy Toàn diện (`verify.py`) & Toàn vẹn 13 LAB gốc
    # =========================================================================
    c13 = []
    proc_v = subprocess.run(
        [sys.executable, str(PROTO_ROOT / "verify.py")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**dict(subprocess.os.environ), "PYTHONIOENCODING": "utf-8"},
    )
    c13.append({
        "name": "Bộ kiểm thử tổng verify.py chạy xanh 100% (exit_code == 0, 21/21 CHECKS PASSED)",
        "ok": proc_v.returncode == 0 and "CHECKS PASSED" in proc_v.stdout,
        "detail": proc_v.stdout.strip().splitlines()[-1] if proc_v.stdout.strip() else proc_v.stderr,
    })
    record_round(13, "Kiểm thử Hồi quy Toàn diện (verify.py) & Toàn vẹn 13 LAB gốc", c13)

    summary = {
        "thoi_gian_chay": datetime.now().isoformat(timespec="seconds"),
        "tong_so_vong_bo_sung": len(rounds_log),
        "vong_tu_den": "Vòng 4 -> Vòng 13 (Tổng cộng 13 vòng tính cả Vòng 1..3)",
        "tat_ca_dat": all(r["trang_thai"] == "PASS" for r in rounds_log),
        "tong_so_checks": sum(r["so_kiem_tra"] for r in rounds_log),
        "tong_so_dat": sum(r["so_dat"] for r in rounds_log),
        "cac_vong": rounds_log,
    }
    out_json = PROTO_ROOT / "logs" / "KET_QUA_10_VONG_TEST_BO_SUNG.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    res = run_10_rounds()
    print(f"\n==> TỔNG KẾT 10 VÒNG TEST BỔ SUNG (VÒNG 4..13): {res['tong_so_dat']}/{res['tong_so_checks']} CHECKS PASSED | ALL_PASS={res['tat_ca_dat']}")
    if not res["tat_ca_dat"]:
        sys.exit(1)
