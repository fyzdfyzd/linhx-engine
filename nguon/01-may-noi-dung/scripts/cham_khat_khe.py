"""Bộ Chấm Điểm Khắt Khe 5 Tầng (Harsh 5-Gate Grader) & Chạy Thử 10 Bài Mới (Tổng 13 Bài)
Thực thi kiểm định khắt khe hơn chuẩn Mức 1 thông thường trên toàn bộ 13 bài chạy thực tế:
  - G1 (Cú pháp & Nhịp câu Khắt khe):
      + `cham_cau.py` đạt 0 cờ cứng (`dat == True`)
      + `ti_le_hai_ve == 0.0%` (Cấm tuyệt đối câu so sánh hai vế, ngưỡng thường là <= 5%)
      + `cau_tb` nằm trong dải hẹp `[21.5, 36.8]` từ/câu (ngưỡng thường là `[19.0, 39.0]`)
      + `ti_le_cau_dai >= 14%` (ngưỡng thường là >= 10%)
      + `0` chữ số Ả Rập trong dòng văn xuôi (trừ số năm 2025, 2026)
  - G2 (Khử Văn Dịch & Từ Sáo AI Tinh Vi - Harsh Anti-Slop Lexicon):
      + `kiem_van_dich.py` == 100/100 (0 lỗi gốc, 0 lỗi học)
      + Quét thêm 25 cụm từ sáo AI tinh vi (`"nhìn chung"`, `"tóm lại"`, `"bức tranh toàn cảnh"`, `"tối ưu hóa"`, `"đột phá"`, `"toàn diện"`, `"mạnh mẽ"`, `"vượt trội"`, `"kỷ nguyên"`, `"chìa khóa then chốt"`, v.v.) -> Bắt buộc = 0 trên bản cuối.
      + `CQS >= 94.0` (ngưỡng thường >= 85.0), `APS <= 10.0` (ngưỡng thường <= 25.0), độ chênh `CQS(B09) - CQS(B07) >= 20.0`.
  - G3 (Kiểm Toán Bằng Chứng & Truy Xuất Nguồn):
      + 100% câu văn trong Bước 08 có gắn mã `[N01]..[N15]` hoặc `[GIẢ LẬP]`.
      + Mọi mã `[Nxx]` đều tồn tại thật trong `03_bang_chung.json`.
      + Bản sạch `09b_ban_sach_khong_ma_nguon.md` đã gỡ sạch 100% mã nguồn mà không vỡ dấu câu.
  - G4 (Chống Đạo Văn Nội Bộ & Chống Lặp Khuôn Giữa 13 Bài - 78 cặp đối chiếu):
      + Jaccard 4-gram tương đồng giữa bất kỳ 2 bài nào trong 13 bài phải `< 0.08` (`< 8%`).
      + `0` câu văn trùng lặp giữa 13 bài.
  - G5 (Thị Giác Onbrand Pixel CIEDE2000 & Đa Phương Tiện):
      + Đủ 15 file bước (`01..09`, `09b`, `M1..M5`) + ảnh gốc AGY (`> 500 KB`) + 2 biểu đồ `H01.svg`, `H02.svg` (`LAB028/hinh.py`, font `Be Vietnam Pro`).
      + `LAB043/onbrand.py cham` đạt `diem_100 >= 98.5` (ngưỡng gốc >= 80.0), `phu_mau_thuong_hieu >= 0.92`, `0` font lạ, `0` từ cấm.
      + Bản in PDF màu (`%PDF-`, `> 30 KB`) và điểm nhân vật `LAB066 >= 8.0/10`.
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROTO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROTO_ROOT))
sys.path.insert(0, str(PROTO_ROOT / "scripts"))

from dieu_phoi import DEFAULT_3_RUNS, kiemChatLuong, run_lab049_Inspectors, sync_demo_folder, taoNoiDung
from kho_10_bai_moi import TEN_NEW_RUNS

HARSH_SLOP_PHRASES = [
    "trong bối cảnh",
    "điều đáng chú ý là",
    "đóng vai trò quan trọng",
    "không thể phủ nhận",
    "nhìn chung",
    "tóm lại",
    "hơn thế nữa",
    "bức tranh toàn cảnh",
    "chìa khóa then chốt",
    "tối ưu hóa",
    "đột phá",
    "kỷ nguyên số",
    "cuộc cách mạng",
    "nâng tầm",
    "toàn diện",
    "mạnh mẽ",
    "vượt trội",
    "hiệu quả cao",
    "tiết kiệm tối đa",
    "giải pháp hoàn hảo",
    "không chỉ",
    "mà còn",
    "càng ngày càng",
    "thúc đẩy sự phát triển",
    "mang tính bước ngoặt",
]


def extract_4grams(text: str) -> set:
    words = re.findall(r"\w+", text.lower())
    if len(words) < 4:
        return set()
    return {tuple(words[i : i + 4]) for i in range(len(words) - 3)}


def jaccard_similarity(s1: set, s2: set) -> float:
    if not s1 or not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)


def generate_new_runs(target_id: str = None):
    if not target_id:
        orig_results = []
        for item in DEFAULT_3_RUNS:
            res = taoNoiDung(
                item["loai"],
                {
                    "ngay": "2026-10-25",
                    "slug": item["slug"],
                    "de_bai": item["de_bai"],
                    "duyet_outline": "may",
                },
            )
            orig_results.append(res)
        sync_demo_folder(orig_results)

    items = TEN_NEW_RUNS if not target_id else [x for x in TEN_NEW_RUNS if x["id"] == target_id]
    results = []
    for idx, item in enumerate(items, 1):
        print(f"[{idx}/{len(items)}] Đang tạo {item['id']} ({item['loai']}): {item['slug']} ...")
        res = taoNoiDung(
            item["loai"],
            {
                "ngay": "2026-10-25",
                "slug": item["slug"],
                "de_bai": item["de_bai"],
                "duyet_outline": "may",
                "draft1_body": item["draft1_body"],
                "step8_body": item["step8_body"],
                "agy_img_file": item.get("agy_img_file"),
                "banner_data": item.get("banner_data"),
                "visual_data": item.get("visual_data"),
                "exhibits": item.get("exhibits"),
            },
        )
        print(
            f"  -> XONG {item['id']}: Draft1 CQS={res['diem_draft_1']['cqs']} -> Final CQS={res['diem_ban_cuoi']['cqs']} | "
            f"cham_cau={res['diem_ban_cuoi']['cham_cau_dat']} | Onbrand CLI={res['onbrand_cli_results'].get('diem_100')}/100"
        )
        results.append(res)
    return results


def grade_single_run_harsh(run_dir: Path) -> dict:
    errors = []
    warnings = []
    metrics = {}

    status_file = run_dir / "RUN_STATUS.json"
    if not status_file.exists():
        return {"run_id": run_dir.name, "passed": False, "errors": ["Thiếu RUN_STATUS.json"], "metrics": {}}

    st = json.loads(status_file.read_text(encoding="utf-8"))
    loai = st.get("loai", "bai_viet")

    # Kiểm tra đủ 15 file bước
    required_step_files = [
        "01_phan_tich_de_bai.md",
        "02_persona_neo.md",
        "03_tim_tham_chieu.md",
        "04_outline_thu_persona.md",
        "05_cham_chon_huong.md",
        "06_trien_khai_draft_1.md",
        "07_danh_gia_draft_1.md",
        "08_viet_lai_giong_tac_gia.md",
        "09_bien_tap_va_kinh_nghiem.md",
        "09b_ban_sach_khong_ma_nguon.md",
        "M1_phan_tich_yeu_cau_template.md",
        "M2_tham_chieu_va_luat_onbrand.md",
        "M3_ba_phuong_an_template.md",
        "M4_cham_chon_template_onbrand.md",
        "M5_bien_tap_template_va_xuat_media.md",
    ]
    missing_steps = [f for f in required_step_files if not (run_dir / f).exists()]
    if missing_steps:
        errors.append(f"[G5-File] Thiếu file bước: {missing_steps}")

    f06 = run_dir / "06_trien_khai_draft_1.md"
    f08 = run_dir / "08_viet_lai_giong_tac_gia.md"
    f09b = run_dir / "09b_ban_sach_khong_ma_nguon.md"
    f03_json = run_dir / "03_bang_chung.json"

    clean_text = f09b.read_text(encoding="utf-8") if f09b.exists() else ""
    step8_full = f08.read_text(encoding="utf-8") if f08.exists() else ""
    # Tách phần thân bài của Bước 08 (bỏ bảng header truy vết ở đầu)
    step8_body_lines = [
        line for line in step8_full.splitlines()
        if line.strip() and not line.strip().startswith("#") and not line.strip().startswith("|")
    ]
    step8_body = "\n\n".join(step8_body_lines)

    # --- G1: Cổng Cú Pháp & Nhịp Câu Khắt Khe trên Bước 08 (có mã nguồn) và 09b (bản sạch) ---
    tmp_dir = PROTO_ROOT / "logs" / "_tmp_harsh"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_b8 = tmp_dir / f"{run_dir.name}_b8.md"
    tmp_b8.write_text(step8_body, encoding="utf-8")

    lab049_b8 = run_lab049_Inspectors(tmp_b8)
    eval_b8 = kiemChatLuong(step8_body, loai)
    eval_b6 = kiemChatLuong(str(f06), loai) if f06.exists() else {"cqs": 70.0, "aps": 15.0}

    if tmp_b8.exists():
        tmp_b8.unlink()

    cc = lab049_b8.get("cham_cau", {})
    vd = lab049_b8.get("kiem_van_dich", {})
    kv = lab049_b8.get("kiem_van", {})
    cs = cc.get("chi_so", {})

    cc_dat = bool(cc.get("dat", False))
    cau_tb = float(cs.get("cau_tb", 0.0))
    ti_le_cau_dai = float(cs.get("ti_le_cau_dai", 0.0))
    ti_le_hai_ve = float(cs.get("ti_le_hai_ve", 0.0))
    so_cau = int(cs.get("so_cau", 0))
    so_tu = int(cs.get("so_tu", 0))

    metrics["so_cau"] = so_cau
    metrics["so_tu"] = so_tu
    metrics["cau_tb"] = cau_tb
    metrics["ti_le_cau_dai_pct"] = round(ti_le_cau_dai * 100, 1)
    metrics["ti_le_hai_ve_pct"] = round(ti_le_hai_ve * 100, 1)
    metrics["cham_cau_dat"] = cc_dat
    metrics["diem_van_dich"] = vd.get("diem", 0)
    metrics["diem_giong_linh"] = kv.get("diem", 0)
    metrics["cqs_draft1"] = eval_b6["cqs"]
    metrics["cqs_final"] = eval_b8["cqs"]
    metrics["cqs_gain"] = round(eval_b8["cqs"] - eval_b6["cqs"], 1)
    metrics["aps_final"] = eval_b8["aps"]

    if not cc_dat:
        hard_flags = []
        for c_item in cc.get("cau", []):
            if c_item.get("co"):
                hard_flags.append(f"Câu #{c_item.get('so')}: {c_item.get('co')}")
        errors.append(f"[G1-ChamCau] Trượt cổng cham_cau.py: {cc.get('truot')} | Chi tiết: {'; '.join(hard_flags)}")

    if ti_le_hai_ve > 0.0:
        errors.append(f"[G1-HaiVe] Khắt khe yêu cầu ti_le_hai_ve == 0%, thực tế = {ti_le_hai_ve*100:.1f}%")

    if not (21.5 <= cau_tb <= 36.8):
        errors.append(f"[G1-DoDaiCau] Khắt khe yêu cầu cau_tb trong [21.5, 36.8], thực tế = {cau_tb}")

    if ti_le_cau_dai < 0.14:
        errors.append(f"[G1-CauDai] Khắt khe yêu cầu ti_le_cau_dai >= 14%, thực tế = {ti_le_cau_dai*100:.1f}%")

    # Quét chữ số Ả Rập trong dòng văn xuôi 09b (bỏ qua bảng Markdown, tiêu đề, blockquote; trừ năm 2025, 2026)
    prose_only_09b = "\n".join(
        line for line in clean_text.splitlines()
        if line.strip() and not line.strip().startswith(("#", "|", ">", "```", "---"))
    )
    arabic_nums = re.findall(r"\b\d+(?:[.,]\d+)?\b", prose_only_09b)
    illegal_nums = [n for n in arabic_nums if n not in ("2025", "2026")]
    if illegal_nums:
        errors.append(f"[G1-ChuSo] Phát hiện chữ số Ả Rập trong văn xuôi 09b (ngoài năm 2025/2026): {illegal_nums}")

    # --- G2: Cổng Từ Vựng Văn Dịch & 25 Cụm Từ Sáo AI Tinh Vi ---
    if float(vd.get("diem", 0)) < 100.0:
        errors.append(f"[G2-VanDich] Điểm kiem_van_dich.py chưa đạt 100/100: {vd.get('diem')} | Lỗi: {vd.get('loi')}")

    lower_clean = clean_text.lower()
    found_slop = [p for p in HARSH_SLOP_PHRASES if p in lower_clean]
    if found_slop:
        errors.append(f"[G2-HarshSlop] Phát hiện cụm từ sáo AI tinh vi trong bản cuối: {found_slop}")

    if eval_b8["cqs"] < 94.0:
        errors.append(f"[G2-CQS] Khắt khe yêu cầu CQS >= 94.0, thực tế = {eval_b8['cqs']}")

    if eval_b8["aps"] > 10.0:
        errors.append(f"[G2-APS] Khắt khe yêu cầu APS <= 10.0, thực tế = {eval_b8['aps']}")

    if metrics["cqs_gain"] < 20.0:
        errors.append(f"[G2-DeltaCQS] Độ tăng CQS từ Draft 1 -> Bản cuối phải >= +20.0 điểm, thực tế = +{metrics['cqs_gain']}")

    # --- G3: Cổng Kiểm Toán Bằng Chứng & Truy Xuất Nguồn ---
    valid_source_ids = set()
    if f03_json.exists():
        b03_data = json.loads(f03_json.read_text(encoding="utf-8"))
        b03_list = b03_data if isinstance(b03_data, list) else b03_data.get("sources", [])
        for s in b03_list:
            if isinstance(s, dict):
                valid_source_ids.add(s.get("id") or s.get("ma"))

    cited_tags = re.findall(r"\[(N\d+|GIẢ LẬP)\]", step8_body)
    if len(cited_tags) < so_cau:
        errors.append(f"[G3-BangChung] Số nhãn nguồn/giả lập ({len(cited_tags)}) ít hơn số câu ({so_cau})")

    unknown_tags = [t for t in cited_tags if t != "GIẢ LẬP" and t not in valid_source_ids]
    if unknown_tags:
        errors.append(f"[G3-MaNguonLa] Mã nguồn không tồn tại trong 03_bang_chung.json: {unknown_tags}")

    leftover_brackets = re.findall(r"\[[^\]]*\]", clean_text)
    if leftover_brackets:
        errors.append(f"[G3-BanSach] Bản sạch 09b còn sót ngoặc vuông mã nguồn: {leftover_brackets}")

    # --- G5: Cổng Thị Giác Onbrand Pixel CIEDE2000 & Đa Phương Tiện ---
    media_dir = run_dir / "media"
    agy_jpg = media_dir / "agy_anh_goc_sakedemy.jpg"
    h01_svg = media_dir / "04-hinh" / "H01.svg"
    h02_svg = media_dir / "04-hinh" / "H02.svg"
    banner_png = media_dir / "sakedemy_banner_1920x600.png"
    kq_vis_json = media_dir / "onbrand_ket_qua_visual.json"
    char_json = media_dir / "character_anchor_lab066.json"

    if not agy_jpg.exists() or agy_jpg.stat().st_size < 500_000:
        errors.append(f"[G5-AGYImage] Ảnh gốc AGY thiếu hoặc < 500KB: {agy_jpg}")

    for svg_p in (h01_svg, h02_svg):
        if not svg_p.exists() or svg_p.stat().st_size < 1800:
            errors.append(f"[G5-ExhibitSVG] Biểu đồ LAB028 thiếu hoặc lỗi: {svg_p.name}")
        else:
            svg_txt = svg_p.read_text(encoding="utf-8")
            if "Be Vietnam Pro" not in svg_txt:
                errors.append(f"[G5-ExhibitFont] {svg_p.name} không dùng font Be Vietnam Pro")

    if not banner_png.exists() or banner_png.stat().st_size < 50_000:
        errors.append("[G5-BannerPNG] Banner Sakedemy 1920x600 thiếu hoặc < 50KB")

    if kq_vis_json.exists():
        kq_ob = json.loads(kq_vis_json.read_text(encoding="utf-8"))
        ob_score = float(kq_ob.get("diem_100", 0.0))
        ob_cov = float(kq_ob.get("muc", {}).get("mau", {}).get("phu_mau_thuong_hieu", 0.0))
        ob_font_la = kq_ob.get("muc", {}).get("chu", {}).get("font_la", [])
        ob_tu_cam = kq_ob.get("muc", {}).get("noi_dung", {}).get("tu_cam_gap", [])
        metrics["onbrand_cli_score"] = ob_score
        metrics["onbrand_brand_coverage_pct"] = round(ob_cov * 100, 1)
        if ob_score < 98.5:
            errors.append(f"[G5-OnbrandScore] Khắt khe yêu cầu onbrand.py >= 98.5/100, thực tế = {ob_score}")
        if ob_cov < 0.92:
            errors.append(f"[G5-OnbrandColor] Độ phủ màu thương hiệu < 92%: {ob_cov*100:.1f}%")
        if ob_font_la:
            errors.append(f"[G5-OnbrandFont] Phát hiện font lạ: {ob_font_la}")
        if ob_tu_cam:
            errors.append(f"[G5-OnbrandTuCam] Phát hiện từ cấm: {ob_tu_cam}")
    else:
        errors.append("[G5-OnbrandJSON] Thiếu file onbrand_ket_qua_visual.json")

    if char_json.exists():
        c_data = json.loads(char_json.read_text(encoding="utf-8"))
        c_score = float(c_data.get("diem_cuoi", 0.0))
        metrics["lab066_score"] = c_score
        if c_score < 8.0:
            errors.append(f"[G5-LAB066] Điểm nhân vật < 8.0: {c_score}")

    pdf_map = {
        "bai_viet": media_dir / "bai_viet_trang_doc_sakedemy.pdf",
        "report_mau": media_dir / "bao_cao_sakedemy_a4.pdf",
        "noi_dung_khoa_hoc": media_dir / "slide_deck_sakedemy_16x9.pdf",
    }
    pdf_p = pdf_map[loai]
    if not pdf_p.exists() or pdf_p.stat().st_size < 30_000:
        errors.append(f"[G5-PDF] File PDF thiếu hoặc < 30KB: {pdf_p.name}")
    else:
        metrics["pdf_size_kb"] = round(pdf_p.stat().st_size / 1024, 1)

    return {
        "run_id": run_dir.name,
        "loai": loai,
        "de_bai": st.get("de_bai", ""),
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "metrics": metrics,
        "clean_text": clean_text,
    }


def grade_all_runs_harsh(round_num: int = 1, out_json: Path = None) -> dict:
    import shutil as _shutil
    runs_root = PROTO_ROOT / "runs"
    for temp_slug in ("2026-10-25_bai_viet_run-muc-1", "2026-10-25_noi_dung_khoa_hoc_course-os-c-261025-sme-buoi-01", "2026-10-25_bai_viet_test-cong-duyet-nguoi-v7"):
        tp = runs_root / temp_slug
        if tp.exists():
            _shutil.rmtree(tp, ignore_errors=True)
    run_dirs = sorted([d for d in runs_root.iterdir() if d.is_dir() and (d / "RUN_STATUS.json").exists()])

    run_reports = []
    for rdir in run_dirs:
        rep = grade_single_run_harsh(rdir)
        run_reports.append(rep)

    # --- G4: Cổng Chống Đạo Văn Nội Bộ & Chống Lặp Khuôn Giữa Toàn Bộ Các Bài ---
    n = len(run_reports)
    max_sim = 0.0
    max_pair = ("", "")
    duplicate_sentences = []

    grams_by_run = {r["run_id"]: extract_4grams(r["clean_text"]) for r in run_reports}
    sents_by_run = {
        r["run_id"]: {s.strip() for s in re.split(r"(?<=[.!?])\s+", r["clean_text"].strip()) if len(s.strip()) > 20}
        for r in run_reports
    }

    pair_count = 0
    for i in range(n):
        for j in range(i + 1, n):
            pair_count += 1
            id1, id2 = run_reports[i]["run_id"], run_reports[j]["run_id"]
            sim = jaccard_similarity(grams_by_run[id1], grams_by_run[id2])
            if sim > max_sim:
                max_sim = sim
                max_pair = (id1, id2)
            common_sents = sents_by_run[id1] & sents_by_run[id2]
            if common_sents:
                duplicate_sentences.append({"pair": f"{id1} <-> {id2}", "common": list(common_sents)})

    if max_sim >= 0.08:
        for r in run_reports:
            if r["run_id"] in max_pair:
                r["errors"].append(f"[G4-TrungLap4Gram] Độ tương đồng 4-gram giữa {max_pair[0]} và {max_pair[1]} = {max_sim*100:.2f}% (>= 8%)")
                r["passed"] = False

    if duplicate_sentences:
        for dup in duplicate_sentences:
            for r in run_reports:
                if r["run_id"] in dup["pair"]:
                    r["errors"].append(f"[G4-TrungCau] Phát hiện câu trùng lặp: {dup['pair']}")
                    r["passed"] = False

    # Xóa clean_text khỏi kết quả lưu JSON cho gọn
    for r in run_reports:
        r.pop("clean_text", None)

    passed_count = sum(1 for r in run_reports if r["passed"])
    summary = {
        "round": round_num,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "total_runs": n,
        "passed_runs": passed_count,
        "failed_runs": n - passed_count,
        "all_passed": passed_count == n,
        "cross_run_uniqueness": {
            "total_pairs_compared": pair_count,
            "max_jaccard_4gram_pct": round(max_sim * 100, 2),
            "max_pair": list(max_pair),
            "threshold_pct": 8.0,
            "duplicate_sentences_count": len(duplicate_sentences),
        },
        "runs": run_reports,
    }

    if out_json:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=" * 88)
    print(f"KẾT QUẢ CHẤM KHẮT KHE 5 TẦNG (VÒNG {round_num}) — TỔNG SỐ BÀI: {n}")
    print(f"ĐẠT: {passed_count}/{n} | TRƯỢT: {n - passed_count}/{n} | Tương đồng 4-gram tối đa ({pair_count} cặp): {max_sim*100:.2f}% (Ngưỡng < 8.0%)")
    print("-" * 88)
    for idx, r in enumerate(run_reports, 1):
        m = r["metrics"]
        st_str = "PASS" if r["passed"] else "FAIL"
        print(
            f"[{idx:02d}] [{st_str}] {r['run_id']} ({r['loai']}) | "
            f"CQS: {m.get('cqs_draft1')}->{m.get('cqs_final')} (+{m.get('cqs_gain')}) | "
            f"cau_tb={m.get('cau_tb')} | hai_ve={m.get('ti_le_hai_ve_pct')}% | "
            f"VD={m.get('diem_van_dich')} | Onbrand={m.get('onbrand_cli_score')}/100 ({m.get('onbrand_brand_coverage_pct')}%)"
        )
        for err in r["errors"]:
            print(f"     ❌ {err}")
    print("=" * 88)
    return summary


def main():
    ap = argparse.ArgumentParser(description="Chạy 10 bài mới & Chấm khắt khe 5 tầng")
    ap.add_argument("--gen-10", action="store_true", help="Tạo toàn bộ 10 bài mới (BAI_04..BAI_13)")
    ap.add_argument("--gen-id", type=str, default=None, help="Tạo lại 1 bài cụ thể theo ID (vd: BAI_06)")
    ap.add_argument("--grade", action="store_true", help="Chấm khắt khe toàn bộ các bài trong runs/")
    ap.add_argument("--round", type=int, default=1, help="Số thứ tự vòng chấm (1, 2, 3)")
    ap.add_argument("--out-json", type=str, default=None, help="File JSON lưu kết quả chấm")
    args = ap.parse_args()

    if args.gen_10:
        generate_new_runs()
    elif args.gen_id:
        generate_new_runs(target_id=args.gen_id)

    if args.grade:
        out_p = Path(args.out_json) if args.out_json else (PROTO_ROOT / "logs" / f"cham_khat_khe_vong_{args.round}.json")
        res = grade_all_runs_harsh(round_num=args.round, out_json=out_p)
        sys.exit(0 if res["all_passed"] else 1)


if __name__ == "__main__":
    main()
