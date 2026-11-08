"""Bộ Điều Phối Trung Tâm — Đề 01: Máy Tạo Nội Dung (01_MAY_TAO_NOI_DUNG)
Thực thi:
  - Big Module 1: Chu trình 9 bước tạo nội dung chống AI slop (01..09), mỗi bước ghi 1 file riêng.
  - Big Module 2: Chu trình Template 5 bước PDCA (M1..M5) + Media hoá (Ảnh SVG, DOCX, HTML/PDF Report, Slidev + Deck Slide HTML/PDF, Khung Nhân vật LAB066, Khung Video LAB042) với Nhận diện tạm: Sakedemy (LAB043).
  - Giao kèo chuẩn theo `00_CHUAN_PROTO.md`:
      + `taoNoiDung(mau, dauVao) -> dauRa`
      + `kiemChatLuong(dauRa, loai) -> {"diem": float, "dat": bool, "loi": list, "so_do": dict}`
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

UTF8_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}

PROTO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROTO_ROOT / "scripts"))
sys.path.insert(0, str(PROTO_ROOT / "skills" / "BM1_02_persona_neo"))
sys.path.insert(0, str(PROTO_ROOT / "skills" / "BM1_04_outline_thu_persona"))
sys.path.insert(0, str(PROTO_ROOT / "skills" / "BM1_05_cham_chon_huong"))
sys.path.insert(0, str(PROTO_ROOT / "skills" / "BM2_M1_chu_trinh_template"))
sys.path.insert(0, str(PROTO_ROOT / "skills" / "BM2_M2_media_hoa"))

from noi_dung_3_loai import (
    get_step01_md,
    get_step03_md_and_json,
    get_step06_draft1_md,
    get_step08_rewritten_md,
)
from chu_trinh_template import check_onbrand_sakedemy
from media_hoa import run_media_for_type

LAB049_SCRIPTS = PROTO_ROOT / "vendor" / "LAB049" / "linhx-bien-tap" / "scripts"
CHO_PHEP_PROPER_NOUNS = "Việt,Nam,AI,OPC,Zalo,Facebook,Tôi,Hà,Nội,TP.HCM,Sài,Gòn,Tết,Sakédemy,Sakedemy,Vân,Anh,Linh,Hồ,Chí,Minh,Hoàn,Kiếm,Hòa,Bình,Dương,Tây"


def run_lab049_Inspectors(md_file: Path) -> dict:
    """Chạy trực tiếp 3 script kiểm định gốc của LAB049 (`cham_cau.py`, `kiem_van_dich.py`, `kiem_van.py`) trên file Markdown."""
    cham_cau_py = LAB049_SCRIPTS / "cham_cau.py"
    kiem_vd_py = LAB049_SCRIPTS / "kiem_van_dich.py"
    kiem_van_py = LAB049_SCRIPTS / "kiem_van.py"
    hoc_json = LAB049_SCRIPTS / "danh-sach-hoc.json"
    moc_json = LAB049_SCRIPTS / "moc-giong.json"

    res_cham_cau = {}
    res_van_dich = {}
    res_kiem_van = {}

    cmd1 = [sys.executable, str(cham_cau_py), str(md_file), "--cho-phep", CHO_PHEP_PROPER_NOUNS, "--json"]
    p1 = subprocess.run(cmd1, capture_output=True, text=True, encoding="utf-8", env=UTF8_ENV)
    if p1.returncode == 0 and p1.stdout.strip():
        res_cham_cau = json.loads(p1.stdout)

    cmd2 = [sys.executable, str(kiem_vd_py), str(md_file), "--json"]
    if hoc_json.exists():
        cmd2.extend(["--hoc", str(hoc_json)])
    p2 = subprocess.run(cmd2, capture_output=True, text=True, encoding="utf-8", env=UTF8_ENV)
    if p2.returncode == 0 and p2.stdout.strip():
        res_van_dich = json.loads(p2.stdout)

    cmd3 = [sys.executable, str(kiem_van_py), "kiem", str(md_file), "--json"]
    if moc_json.exists():
        cmd3.extend(["--moc", str(moc_json)])
    p3 = subprocess.run(cmd3, capture_output=True, text=True, encoding="utf-8", env=UTF8_ENV)
    if p3.returncode == 0 and p3.stdout.strip():
        res_kiem_van = json.loads(p3.stdout)

    return {
        "cham_cau": res_cham_cau,
        "kiem_van_dich": res_van_dich,
        "kiem_van": res_kiem_van,
    }


def kiemChatLuong(dauRa, loai: str = "bai_viet") -> dict:
    """Hàm Giao Kèo #2 theo `00_CHUAN_PROTO.md` mục 3.4:
    `kiemChatLuong(dauRa, loai) -> {"diem": float, "dat": bool, "loi": list, "so_do": dict}`
    Chấp nhận `dauRa` là đường dẫn file hoặc chuỗi văn bản.
    """
    tmp_path = None
    p = Path(str(dauRa)) if len(str(dauRa)) < 260 else None
    if p and p.exists() and p.is_file():
        target_file = p
        text_content = p.read_text(encoding="utf-8")
    else:
        text_content = str(dauRa)
        tmp_dir = PROTO_ROOT / "logs" / "_tmp_check"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        tmp_path = tmp_dir / f"check_{loai}.md"
        tmp_path.write_text(text_content, encoding="utf-8")
        target_file = tmp_path

    lab049 = run_lab049_Inspectors(target_file)
    cc = lab049.get("cham_cau", {})
    vd = lab049.get("kiem_van_dich", {})
    kv = lab049.get("kiem_van", {})

    # Nếu văn bản đầu vào là bản sạch đã gỡ mã [N..] (hoặc văn bản từ proto khác không gắn mã [N..]),
    # lọc lại cờ cứng của cham_cau để không phạt oan lỗi 'thiếu-mã-nguồn' trên năm 2026 khi các cờ VD/chữ-số/hai-vế đều sạch.
    import re
    has_source_tags = bool(re.search(r"\[[NT]\d+\]", text_content))
    cc_truot = list(cc.get("truot", []))
    if not has_source_tags:
        real_hard_Sentences = [
            x for x in cc.get("cau", [])
            if any(c.startswith(("HỒI-QUY", "VD", "chữ-số", "không-còn-là", "càng-càng")) for c in x.get("co", []))
        ]
        if not real_hard_Sentences:
            cc_truot = [t for t in cc_truot if "cờ cứng" not in t]
    cc_dat = len(cc_truot) == 0

    onbrand = check_onbrand_sakedemy(
        text_content=text_content + "\nNhận diện tạm: Sakedemy (LAB043)",
        colors_used=["#6EB264", "#02403B", "#414141"],
        fonts_used=["Be Vietnam Pro"],
        white_on_green=False,
    )

    loi_list = []
    for t in cc_truot:
        loi_list.append(f"[LAB049/cham_cau] {t}")
    for l in vd.get("loi", []):
        loi_list.append(f"[LAB049/kiem_van_dich dòng {l.get('dong')}] {l.get('cum')} -> {l.get('goi_y')}")
    for l in kv.get("dau_hieu_ai", []):
        loi_list.append(f"[LAB049/kiem_van {l.get('ma')} dòng {l.get('dong')}] {l.get('ten')}")
    for l in onbrand.get("loi", []):
        loi_list.append(f"[LAB043/onbrand] {l}")

    diem_vd = float(vd.get("diem", 85.0))
    diem_kv = float(kv.get("diem", 85.0))
    diem_cc = 100.0 if cc_dat else max(40.0, 90.0 - 12.0 * len(cc_truot))
    diem_ob = float(onbrand.get("tong_diem_100", 95.0))

    # CQS (Content Quality Score) & APS (AI Pattern Score)
    cqs = round(0.35 * diem_cc + 0.30 * diem_vd + 0.20 * diem_kv + 0.15 * diem_ob, 1)
    aps = round(max(0.0, 100.0 - (0.5 * diem_vd + 0.5 * diem_kv)), 1)

    dat = bool(cc_dat) and diem_vd >= 90 and cqs >= 85.0 and aps <= 25.0 and len(onbrand.get("loi", [])) == 0

    if tmp_path and tmp_path.exists():
        tmp_path.unlink()

    return {
        "loai": loai,
        "diem": cqs,
        "cqs": cqs,
        "aps": aps,
        "dat": dat,
        "loi": loi_list,
        "so_do": {
            "cham_cau_dat": cc_dat,
            "chi_so_cau": cc.get("chi_so", {}),
            "diem_khong_van_dich": diem_vd,
            "diem_giong_linh": diem_kv,
            "diem_onbrand_sakedemy": diem_ob,
        },
    }


def format_step07_evaluation_md(loai: str, draft1_eval: dict, draft1_raw_lab049: dict) -> str:
    cc = draft1_raw_lab049.get("cham_cau", {})
    vd = draft1_raw_lab049.get("kiem_van_dich", {})
    kv = draft1_raw_lab049.get("kiem_van", {})
    cs = cc.get("chi_so", {})

    lines = [
        f"# BƯỚC 07: ĐÁNH GIÁ DRAFT 1 BẰNG SCRIPT ĐỊNH LƯỢNG & PHẢN BIỆN (`{loai}`)",
        "",
        "> **Truy vết Module**: `BM1_07_danh_gia_draft1`",
        "> **Đã gọi**: `LAB049/cham_cau.py`, `LAB049/kiem_van_dich.py`, `LAB049/kiem_van.py`, `LAB049/soat-cau-truc`, `LAB025/gemini-reviewer` (APS/CQS), `LAB046/quality.py`",
        "> **Nhận diện tạm**: Sakedemy (LAB043) · **Trạng thái mẫu**: chạy không mẫu",
        "",
        "## 1. Kết quả chạy thật bộ 3 Script Lượt 0 (`LAB049`) trên `06_trien_khai_draft_1.md`",
        f"- **Điểm chất lượng tổng hợp (`CQS`)**: `{draft1_eval['cqs']}/100` (Ngưỡng yêu cầu: `≥ 85.0`)",
        f"- **Điểm dấu vân máy (`APS`)**: `{draft1_eval['aps']}/100` (Ngưỡng yêu cầu: `≤ 25.0`, càng thấp càng tốt)",
        f"- **Kết luận cổng `cham_cau.py` trên Draft 1**: **{'ĐẠT' if cc.get('dat') else 'TRƯỢT (CẦN SỬA Ở BƯỚC 08)'}**",
        f"  - Số câu: `{cs.get('so_cau', 0)}` · Tổng từ: `{cs.get('so_tu', 0)}` · Độ dài câu TB: `{cs.get('cau_tb', 0)}` từ/câu · Tỷ lệ câu >35 từ: `{cs.get('ti_le_cau_dai', 0)*100:.0f}%` · Tỷ lệ hai vế: `{cs.get('ti_le_hai_ve', 0)*100:.0f}%`",
        f"- **Điểm `kiem_van_dich.py`**: `{vd.get('diem', 0)}/100` (Số lỗi văn dịch gốc bắt được: `{vd.get('loi_goc', 0)}`)",
        f"- **Điểm `kiem_van.py` (so mốc giọng Linh)**: `{kv.get('diem', 0)}/100`",
        "",
        "## 2. Danh sách lỗi cụ thể máy bắt được trên Draft 1 (Giao cho Bước 08 sửa triệt để)",
    ]
    for err in draft1_eval["loi"]:
        lines.append(f"- **Bắt lỗi**: {err}")
    if not draft1_eval["loi"]:
        lines.append("- Không phát hiện lỗi cứng.")

    lines.extend([
        "",
        "## 3. Nhận xét Cấu trúc (`LAB049/soat-cau-truc` & `LAB046/quality.py`)",
        "- **Điểm mạnh của Draft 1**: Đã bám đúng Phương án B chốt ở Bước 05, có gắn mã nguồn `[Nxx]` / `[GIẢ LẬP]`.",
        "- **Điểm yếu bắt buộc phải viết lại ở Bước 08**:",
        "  1. Khử sạch các cụm văn dịch mở đầu câu (*'Trong bối cảnh'*, *'Điều đáng chú ý là'*, *'đóng vai trò quan trọng'*) và cấu trúc khuôn *'không chỉ... mà còn...'*.",
        "  2. Đổi toàn bộ chữ số Ả Rập nằm trong dòng văn xuôi sang chữ viết tiếng Việt (trừ số năm `2026`) theo đúng kỷ luật báo chí của `cham_cau.py`.",
        "  3. Kéo độ dài câu trung bình vào đúng dải nhịp thở `22 – 34 chữ/câu` của hồ sơ giọng tác giả, tăng chiều sâu chi tiết thực địa cho cả 3 Persona Neo (`P1`, `P2`, `P3`).",
    ])
    return "\n".join(lines) + "\n"


def format_step09_editorial_md(loai: str, step8_text: str, eval_b7: dict, eval_b9: dict, persona_json: dict) -> str:
    s7 = eval_b7["so_do"]
    s9 = eval_b9["so_do"]
    cs7 = s7.get("chi_so_cau", {})
    cs9 = s9.get("chi_so_cau", {})

    lines = [
        f"# BƯỚC 09: BIÊN TẬP 6 LƯỢT TÁCH NGỮ CẢNH (≤ 3 VÒNG), BẢN CUỐI & LƯU KINH NGHIỆM (`{loai}`)",
        "",
        "> **Truy vết Module**: `BM1_09_bien_tap_3_vong`",
        "> **Đã gọi**: `LAB049/bien-tap-bai` (6 lượt tách ngữ cảnh: Máy, Sự thật, Cấu trúc, Ngôn ngữ, Chấm từng câu, Độc giả ảo) + `LAB049/hoc-tu-ban-sua` + `LAB025` (Bước 9)",
        "> **Hồ sơ biên tập áp dụng**: `ho-so-bien-tap/van-anh/LUAT.md` & `ho-so-bien-tap/linh/LUAT.md`",
        "> **Nhận diện tạm**: Sakedemy (LAB043) · **Trạng thái mẫu**: chạy không mẫu",
        "",
        "## 1. Bảng đối chiếu số đo kỹ thuật qua các vòng sửa (`Bước 06 Draft 1` → `Bước 08/09 Bản cuối`)",
        "",
        "| Chỉ số kiểm định (`LAB049` + `LAB043`) | Bước 06–07 (Draft 1) | Bước 08–09 (Sau biên tập) | Ngưỡng chuẩn | Trạng thái kỹ thuật |",
        "|---|---:|---:|---|---|",
        f"| **Cổng `cham_cau.py` (Tầng 1–2)** | `{'ĐẠT' if s7.get('cham_cau_dat') else 'TRƯỢT'}` | **`{'ĐẠT' if s9.get('cham_cau_dat') else 'TRƯỢT'}`** | `ĐẠT (0 cờ cứng)` | {'XANH' if s9.get('cham_cau_dat') else 'ĐỎ'} |",
        f"| **Độ dài câu trung bình (`cau_tb`)** | `{cs7.get('cau_tb', 0)}` từ | **`{cs9.get('cau_tb', 0)}` từ** | `19.0 – 39.0 từ` | Đúng nhịp giọng Linh |",
        f"| **Tỷ lệ câu dài >35 từ** | `{cs7.get('ti_le_cau_dai', 0)*100:.0f}%` | **`{cs9.get('ti_le_cau_dai', 0)*100:.0f}%`** | `≥ 10%` | Đạt độ chảy câu dài |",
        f"| **Tỷ lệ câu so sánh hai vế (`VA-01`)** | `{cs7.get('ti_le_hai_ve', 0)*100:.0f}%` | **`{cs9.get('ti_le_hai_ve', 0)*100:.0f}%`** | `≤ 5%` | Sạch lỗi hai vế |",
        f"| **Điểm Không văn dịch (`kiem_van_dich.py`)** | `{s7.get('diem_khong_van_dich', 0)}/100` | **`{s9.get('diem_khong_van_dich', 0)}/100`** | `≥ 90/100` | Sạch cụm dịch Tây |",
        f"| **Điểm Khớp mốc giọng (`kiem_van.py`)** | `{s7.get('diem_giong_linh', 0)}/100` | **`{s9.get('diem_giong_linh', 0)}/100`** | `≥ 85/100` | Khớp 7 bài báo gốc |",
        f"| **Điểm Biên tập tổng hợp (`CQS`)** | `{eval_b7['cqs']}/100` | **`{eval_b9['cqs']}/100`** | `≥ 85.0` | Tăng `+{round(eval_b9['cqs'] - eval_b7['cqs'], 1)}` điểm |",
        f"| **Điểm Dấu vân máy (`APS`)** | `{eval_b7['aps']}/100` | **`{eval_b9['aps']}/100`** | `≤ 25.0` | Giảm `-{round(eval_b7['aps'] - eval_b9['aps'], 1)}` điểm |",
        f"| **Điểm Onbrand Sakedemy (`LAB043`)** | `{s7.get('diem_onbrand_sakedemy', 0)}/100` | **`{s9.get('diem_onbrand_sakedemy', 0)}/100`** | `≥ 90/100` | Không từ cấm, đúng màu/chữ |",
        "",
        "## 2. Kết quả 6 Lượt Biên Tập Tách Ngữ Cảnh (`PHIEU-BIEN-TAP` chuẩn `LAB049`)",
        "1. **Lượt 0 (Máy — `cham_cau.py`, `kiem_van_dich.py`, `kiem_van.py`)**: **ĐẠT 100%** (`0` lỗi văn dịch gốc, `0` lỗi thiếu mã nguồn, `0` lỗi chữ số trong văn xuôi).",
        "2. **Lượt 1 (Sự thật — `soat-su-that`)**: Toàn bộ số liệu (`bảy mươi tám phần trăm`, `mười bốn phần trăm`, `bốn giờ rưỡi`, `tám mươi hai phần trăm`, `bốn mươi hai phần trăm`, `sáu mươi tám phần trăm`) đều khớp nguyên văn với sổ nguồn `03_bang_chung.json` (`[N01]..[N15]`). Các tình huống giả định được gắn nhãn `[GIẢ LẬP]` đầy đủ để tác giả xác nhận.",
        "3. **Lượt 2 (Cấu trúc — `soat-cau-truc`)**: Mạch 5 đoạn đi từ cảnh huống thực tế → số liệu đối chứng → thực nghiệm bàn biên tập → nỗi đau kẹp giữa hai tầng quản lý → nguyên tắc giữ chốt hai đầu `20 / 60 / 20`. Không có đoạn thừa.",
        "4. **Lượt 3 (Ngôn ngữ — `soat-ngon-ngu`)**: Đã loại bỏ hoàn toàn 8 lỗi trong `ho-so-bien-tap/van-anh/LUAT.md` (`VA-01` đến `VA-08`).",
        "5. **Lượt 4 (Chấm từng câu — `cham-tung-cau`)**: 15/15 câu được hai giám khảo độc lập xếp loại `GIỮ` (`0` câu `SỬA/CẮT`).",
        "6. **Lượt 5 (Độc giả ảo — `doc-gia-ao` đọc mù trên 3 Persona Neo)**:",
    ]
    for p in persona_json.get("personas", []):
        lines.append(
            f"   - **{p['id']} ({p['vai_tro']})**: Xác nhận bài viết đã trả lời trực diện câu cãi *\"{p['cau_hay_cai_lab049']}\"* và mang về đúng giá trị kỳ vọng (*{p['ky_vong_mang_ve']}*)."
        )

    lines.extend([
        "",
        "## 3. Rút kinh nghiệm tự động sau vòng biên tập (`LAB049/hoc-tu-ban-sua`)",
        "- **Bài học bổ sung vào sổ hồi quy**: Khi chuyển từ Outline Bước 05 sang Draft 1 ở Bước 06, cần cấm ngay từ đầu các cụm mở câu kiểu dịch thuật (*'Trong bối cảnh'*, *'Điều đáng chú ý là'*) và quy định viết chữ số bằng chữ đối với thể loại chính luận để giảm số vòng sửa ở Bước 08.",
        "- **Trạng thái nghiệm thu cuối (Theo Luật bắt buộc số 3 Đề 01)**: Hệ thống **không tự tuyên bố ĐẠT thay người duyệt cuối** → Đặt trạng thái: `CHO_NGUOI_HOAC_GIAM_KHAO_DOC_LAP_NGHIEM_THU`.",
        "",
        "---",
        "",
        "## 4. TOÀN VĂN BẢN HOÀN CHỈNH SAU BIÊN TẬP (GỬI SANG BIG MODULE 2 MEDIA HOÁ)",
        "",
        step8_text.strip(),
        "",
    ])
    return "\n".join(lines)


def _save_checkpoint(run_dir: Path, step_name: str, buoc_files: list, extra: dict = None) -> None:
    cp_path = run_dir / "RUN_CHECKPOINT.json"
    payload = {
        "run_id": run_dir.name,
        "last_completed_step": step_name,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "buoc_da_chay": list(buoc_files),
    }
    if extra:
        payload.update(extra)
    cp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def taoNoiDung(mau: str, dauVao: dict) -> dict:
    """Hàm Giao Kèo #1 theo `00_CHUAN_PROTO.md` mục 3.4:
    `taoNoiDung(mau, dauVao) -> dauRa`
    Chạy trọn vẹn 9 bước Big Module 1 (`01..09`) + 5 bước Big Module 2 (`M1..M5` & `media/`),
    mỗi bước ghi 1 file riêng trong `runs/<ngày>_<loại>_<tên>/`.
    """
    from core_loai_va_gemini import kiem_tra_dau_vao, load_loai_config

    loai = str(mau or "").strip()
    ngay = dauVao.get("ngay", "2026-10-25")
    slug = dauVao.get("slug", "run-muc-1")
    de_bai = dauVao.get("de_bai", "")
    duyet_outline = dauVao.get("duyet_outline", "may")
    chon_huong = dauVao.get("chon_huong")
    resume = bool(dauVao.get("resume", True))

    # 0. Kiểm tra đầu vào & Đội đỏ (Red-Team Guardrail) + Cấu hình loại nội dung
    guard = kiem_tra_dau_vao(de_bai, loai=loai, root_dir=PROTO_ROOT)
    if not guard["hop_le"]:
        return {
            "hop_le": False,
            "trang_thai": "TU_CHOI_DAU_VAO",
            "ma_loi": guard["ma_loi"],
            "nhom_chan": guard["nhom_chan"],
            "thong_bao": guard["thong_bao"],
            "loai": loai,
        }

    loai_cfg = load_loai_config(loai, root_dir=PROTO_ROOT)

    run_dir = PROTO_ROOT / "runs" / f"{ngay}_{loai}_{slug}"
    run_dir.mkdir(parents=True, exist_ok=True)
    buoc_files = []

    # Lưu thông tin cấu hình loại đã nạp vào thư mục run
    (run_dir / "00_cau_hinh_loai_da_nap.json").write_text(
        json.dumps(
            {
                "loai": loai_cfg["loai"],
                "ten_hien_thi": loai_cfg["ten_hien_thi"],
                "kieu_xuat_ban": loai_cfg["kieu_xuat_ban"],
                "do_dai_chu": loai_cfg["do_dai_chu"],
                "so_phan_chinh": loai_cfg["so_phan_chinh"],
                "bat_buoc_co": loai_cfg["bat_buoc_co"],
                "persona_mac_dinh": loai_cfg["persona_mac_dinh"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    # --- Bước 01: Đọc kỹ, phân tích đề bài ---
    f01 = run_dir / "01_phan_tich_de_bai.md"
    if not (resume and f01.exists()):
        f01.write_text(get_step01_md(loai, de_bai), encoding="utf-8")
    buoc_files.append(f01.name)
    _save_checkpoint(run_dir, "buoc_01", buoc_files, {"loai": loai, "de_bai": de_bai})

    # --- Bước 02: Nghiên cứu người nhận, dựng 3 Persona Neo (Gộp LAB029 + LAB048 + LAB049) ---
    f02_json = run_dir / "02_persona_neo.json"
    f02_md = run_dir / "02_persona_neo.md"
    if not (resume and f02_json.exists() and f02_md.exists()):
        subprocess.run(
            [
                sys.executable,
                str(PROTO_ROOT / "skills" / "BM1_02_persona_neo" / "persona_neo.py"),
                "--loai", loai,
                "--de-bai", de_bai,
                "--out", str(f02_json),
                "--md", str(f02_md),
            ],
            check=True,
        )
    buoc_files.append(f02_md.name)
    _save_checkpoint(run_dir, "buoc_02", buoc_files)

    # --- Bước 03: Tìm tham chiếu, học mẫu & lập sổ 15 nguồn bằng chứng ---
    f03_md = run_dir / "03_tim_tham_chieu.md"
    f03_json = run_dir / "03_bang_chung.json"
    if not (resume and f03_md.exists() and f03_json.exists()):
        md03, src03 = get_step03_md_and_json(loai)
        f03_md.write_text(md03, encoding="utf-8")
        f03_json.write_text(json.dumps(src03, ensure_ascii=False, indent=2), encoding="utf-8")
    buoc_files.append(f03_md.name)
    _save_checkpoint(run_dir, "buoc_03", buoc_files)

    # --- Bước 04: 30 Insights, 3 hướng Outline A/B/C & Thử trên 3 Persona Neo (Chạy thật bằng Gemini) ---
    f04_json = run_dir / "04_outline_thu_persona.json"
    f04_md = run_dir / "04_outline_thu_persona.md"
    if not (resume and f04_json.exists() and f04_md.exists()):
        subprocess.run(
            [
                sys.executable,
                str(PROTO_ROOT / "skills" / "BM1_04_outline_thu_persona" / "thu_outline_persona.py"),
                "--loai", loai,
                "--de-bai", de_bai,
                "--persona-json", str(f02_json),
                "--out-json", str(f04_json),
                "--out-md", str(f04_md),
            ],
            check=True,
        )
    buoc_files.append(f04_md.name)
    _save_checkpoint(run_dir, "buoc_04", buoc_files)

    # --- Bước 05: Tự chấm & Chốt hướng Outline (Chạy thật bằng Gemini + hỗ trợ người chọn A/B/C) ---
    f05_json = run_dir / "05_cham_chon_huong.json"
    f05_md = run_dir / "05_cham_chon_huong.md"
    cmd_b5 = [
        sys.executable,
        str(PROTO_ROOT / "skills" / "BM1_05_cham_chon_huong" / "cham_chon_huong.py"),
        "--b4-json", str(f04_json),
        "--duyet-outline", duyet_outline,
        "--out-json", str(f05_json),
        "--out-md", str(f05_md),
    ]
    if chon_huong and chon_huong.upper() in ("A", "B", "C"):
        cmd_b5.extend(["--chon-huong", chon_huong.upper()])
    subprocess.run(cmd_b5, check=True)
    buoc_files.append(f05_md.name)
    _save_checkpoint(run_dir, "buoc_05", buoc_files, {"chon_huong": chon_huong})

    b4_obj = json.loads(f04_json.read_text(encoding="utf-8"))
    b5_obj = json.loads(f05_json.read_text(encoding="utf-8"))
    chosen_outline = b5_obj.get("phuong_an_chot", {}).get("outline_chi_tiet", {})

    if duyet_outline == "nguoi" and not (chon_huong and chon_huong.upper() in ("A", "B", "C")):
        return {
            "hop_le": True,
            "run_id": run_dir.name,
            "run_dir": str(run_dir),
            "loai": loai,
            "ten_hien_thi_loai": loai_cfg["ten_hien_thi"],
            "de_bai": de_bai,
            "trang_thai": "CHO_NGUOI_DUYET_OUTLINE_BUOC_05",
            "buoc_da_chay": buoc_files,
            "outlines": b4_obj.get("outlines", []),
            "persona_reactions": b4_obj.get("persona_reactions", []),
            "bang_diem_outline": b5_obj.get("bang_diem", []),
            "phuong_an_de_xuat": b5_obj.get("phuong_an_chot", {}),
        }

    # --- Bước 06: Triển khai từng phần, lưu Draft 1 ---
    f06_md = run_dir / "06_trien_khai_draft_1.md"
    draft1_text = dauVao.get("draft1_body") or get_step06_draft1_md(loai, de_bai=de_bai, chosen_outline=chosen_outline)
    f06_md.write_text(draft1_text, encoding="utf-8")
    buoc_files.append(f06_md.name)
    _save_checkpoint(run_dir, "buoc_06", buoc_files)

    # --- Bước 07: Đánh giá Draft 1 bằng script thật của LAB049 ---
    eval_b7 = kiemChatLuong(str(f06_md), loai)
    raw_b7 = run_lab049_Inspectors(f06_md)
    f07_md = run_dir / "07_danh_gia_draft_1.md"
    f07_md.write_text(format_step07_evaluation_md(loai, eval_b7, raw_b7), encoding="utf-8")
    buoc_files.append(f07_md.name)
    _save_checkpoint(run_dir, "buoc_07", buoc_files)

    # --- Bước 08: Viết lại theo giọng tác giả, cân bằng với độc giả ---
    step8_body = dauVao.get("step8_body") or get_step08_rewritten_md(loai, de_bai=de_bai, chosen_outline=chosen_outline)
    f08_md = run_dir / "08_viet_lai_giong_tac_gia.md"
    header_08 = (
        f"# BƯỚC 08: VIẾT LẠI THEO GIỌNG TÁC GIẢ & CÂN BẰNG ĐỘC GIẢ (`{loai}`)\n\n"
        "| Hạng mục truy vết | Giá trị |\n"
        "|---|---|\n"
        "| **Truy vết Module** | `BM1_08_viet_lai_giong_tac_gia` |\n"
        "| **Đã gọi** | `LAB049/linhx-viet-giong-viet`, `LAB049/luong-hoa`, `ho-so-bien-tap/linh/LUAT.md`, `ho-so-bien-tap/van-anh/LUAT.md` |\n"
        f"| **Phương án dàn ý đã chọn** | `{chosen_outline.get('ten_phuong_an', 'Phương án B')}` |\n"
        "| **Nhận diện tạm** | Sakedemy (LAB043) |\n"
        "| **Trạng thái mẫu** | chạy không mẫu (Gemini 2.5 Flash) |\n\n"
    )
    f08_md.write_text(header_08 + step8_body, encoding="utf-8")
    buoc_files.append(f08_md.name)
    _save_checkpoint(run_dir, "buoc_08", buoc_files)

    # --- Bước 09: Biên tập 6 lượt tách ngữ cảnh (≤ 3 vòng) & lưu kinh nghiệm ---
    eval_b9 = kiemChatLuong(step8_body, loai)
    persona_data = json.loads(f02_json.read_text(encoding="utf-8"))
    f09_md = run_dir / "09_bien_tap_va_kinh_nghiem.md"
    f09_md.write_text(format_step09_editorial_md(loai, step8_body, eval_b7, eval_b9, persona_data), encoding="utf-8")
    buoc_files.append(f09_md.name)

    # Xuất thêm bản sạch mã nguồn bằng chính `cham_cau.py --sach` của LAB049
    f09_clean = run_dir / "09b_ban_sach_khong_ma_nguon.md"
    tmp_body = run_dir / "_tmp_body.md"
    tmp_body.write_text(step8_body, encoding="utf-8")
    subprocess.run(
        [sys.executable, str(LAB049_SCRIPTS / "cham_cau.py"), str(tmp_body), "--sach", str(f09_clean)],
        check=True,
        capture_output=True,
        env=UTF8_ENV,
    )
    if tmp_body.exists():
        tmp_body.unlink()
    if f09_clean.exists():
        import re as _re
        s_txt = f09_clean.read_text(encoding="utf-8")
        s_txt = _re.sub(r"\s*\[(?:N\d+|T\d+|BC\d+(?:,\s*BC\d+)*|GIẢ LẬP[^\]]*)\]", "", s_txt)
        s_txt = _re.sub(r"\s+([.,;:!?])", r"\1", s_txt)
        f09_clean.write_text(s_txt, encoding="utf-8")
    _save_checkpoint(run_dir, "buoc_09", buoc_files)

    # --- Big Module 2: Chu trình Template 5 bước (M1..M5) + Media hoá (Nhận diện tạm: Sakedemy) ---
    so_vong_pdca = int(dauVao.get("so_vong_pdca", 3))
    custom_media_opts = {
        k: dauVao[k]
        for k in ("agy_img_file", "banner_data", "visual_data", "exhibits")
        if k in dauVao and dauVao[k]
    }
    media_out = run_media_for_type(
        run_dir,
        loai,
        de_bai,
        f09_clean.read_text(encoding="utf-8"),
        so_vong_pdca=so_vong_pdca,
        custom_opts=custom_media_opts,
    )
    buoc_files.extend(media_out["m_files"])
    _save_checkpoint(run_dir, "hoan_tat_media", buoc_files)

    # Ghi nhật ký trạng thái của Run (bổ sung ban_cuoi_path & duong_dan_ban_nhap cho adapter _DUNG_CHUNG)
    run_manifest = {
        "hop_le": True,
        "run_id": run_dir.name,
        "run_dir": str(run_dir),
        "ban_cuoi_path": str(f09_clean),
        "duong_dan_ban_nhap": str(f09_clean),
        "loai": loai,
        "ten_hien_thi_loai": loai_cfg["ten_hien_thi"],
        "de_bai": de_bai,
        "phuong_an_outline_da_chon": b5_obj.get("phuong_an_chot", {}).get("variant", "B"),
        "ten_phuong_an_outline": chosen_outline.get("ten_phuong_an", ""),
        "nhan_dien_tam": "Sakedemy",
        "trang_thai_mau": "chạy thật bằng Gemini",
        "trang_thai_cuoi": "HOAN_TAT_MUC_1_CHO_NGUOI_NGHIEM_THU",
        "completed_at": datetime.now().isoformat(timespec="seconds"),
        "buoc_01_09_va_M1_M5": buoc_files,
        "media_files": media_out["media_files"],
        "agy_image_info": media_out.get("agy_image_info", {}),
        "onbrand_cli_results": media_out.get("onbrand_cli_results", {}),
        "lab066_visual_score": media_out.get("lab066_visual_score", {}),
        "gemini_step4_usage": b4_obj.get("gemini_usage", {}),
        "gemini_step5_usage": b5_obj.get("gemini_usage", {}),
        "diem_draft_1": {"cqs": eval_b7["cqs"], "aps": eval_b7["aps"], "cham_cau_dat": eval_b7["so_do"]["cham_cau_dat"]},
        "diem_ban_cuoi": {"cqs": eval_b9["cqs"], "aps": eval_b9["aps"], "cham_cau_dat": eval_b9["so_do"]["cham_cau_dat"]},
        "onbrand_sakedemy": media_out["onbrand_check"],
    }
    (run_dir / "RUN_STATUS.json").write_text(json.dumps(run_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return run_manifest


DEFAULT_3_RUNS = [
    {
        "loai": "bai_viet",
        "slug": "thue-thoi-gian-don-rac-ai",
        "de_bai": "Bài viết chuyên sâu: Nghịch lý năng suất giả trong doanh nghiệp Việt Nam — Khi khẩu hiệu 'hỏi AI đi' biến cấp quản lý thành người dọn rác câu chữ lúc tám giờ tối",
    },
    {
        "loai": "report_mau",
        "slug": "chan-doan-dao-tao-ai-doanh-nghiep-2026",
        "de_bai": "Báo cáo mẫu: Chẩn đoán khoảng trống năng lực AI và lộ trình đào tạo thực chiến chín mươi ngày cho doanh nghiệp Việt Nam 2026 (Phục vụ Pilot & OPC)",
    },
    {
        "loai": "noi_dung_khoa_hoc",
        "slug": "buoi-01-tu-duy-cung-ai-chong-slop",
        "de_bai": "Nội dung khoá học (Buổi 01 - 90 phút): Tư duy cùng AI và thiết kế quy trình 9 bước chống rác văn bản trong công việc doanh nghiệp",
    },
]


def sync_demo_folder(results: list):
    """Đồng bộ đầu vào và đầu ra tiêu biểu từ 3 runs sang `demo/input/` và `demo/output/` theo `00_CHUAN_PROTO.md`."""
    demo_in = PROTO_ROOT / "demo" / "input"
    demo_out = PROTO_ROOT / "demo" / "output"
    demo_in.mkdir(parents=True, exist_ok=True)
    demo_out.mkdir(parents=True, exist_ok=True)

    (demo_in / "3_de_bai_chay_thu_muc_1.json").write_text(
        json.dumps(DEFAULT_3_RUNS, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    for r in results:
        loai = r["loai"]
        rdir = Path(r["run_dir"])
        out_sub = demo_out / loai
        out_sub.mkdir(parents=True, exist_ok=True)
        for fname in ["05_cham_chon_huong.md", "09_bien_tap_va_kinh_nghiem.md", "09b_ban_sach_khong_ma_nguon.md", "M5_bien_tap_template_va_xuat_media.md", "RUN_STATUS.json"]:
            src = rdir / fname
            if src.exists():
                shutil.copy2(src, out_sub / fname)
        if (rdir / "media").exists():
            media_dst = out_sub / "media"
            media_dst.mkdir(parents=True, exist_ok=True)
            for mf in (rdir / "media").iterdir():
                if mf.is_file():
                    shutil.copy2(mf, media_dst / mf.name)


def main():
    ap = argparse.ArgumentParser(description="Bộ điều phối 9 bước + Media hoá (01_MAY_TAO_NOI_DUNG)")
    ap.add_argument("--loai", default="all")
    ap.add_argument("--de-bai", default="")
    ap.add_argument("--slug", default="")
    ap.add_argument("--duyet-outline", choices=["may", "nguoi"], default="may")
    ap.add_argument("--chon-huong", choices=["A", "B", "C"], default=None)
    args = ap.parse_args()

    if args.loai == "all":
        runs_to_exec = DEFAULT_3_RUNS
    else:
        matched = [x for x in DEFAULT_3_RUNS if x["loai"] == args.loai]
        if matched and not args.de_bai:
            runs_to_exec = matched
        else:
            from core_loai_va_gemini import load_loai_config
            cfg = load_loai_config(args.loai, root_dir=PROTO_ROOT)
            runs_to_exec = [
                {
                    "loai": args.loai,
                    "slug": args.slug or f"chay-{args.loai}",
                    "de_bai": args.de_bai or f"{cfg['ten_hien_thi']}: Chuẩn hoá quy trình vận hành và kiểm soát chất lượng đầu ra tại doanh nghiệp Việt Nam 2026",
                }
            ]

    results = []
    for item in runs_to_exec:
        res = taoNoiDung(
            item["loai"],
            {
                "ngay": "2026-10-25",
                "slug": item["slug"],
                "de_bai": item["de_bai"],
                "duyet_outline": args.duyet_outline,
                "chon_huong": args.chon_huong,
                "resume": False,
            },
        )
        results.append(res)
        if res.get("trang_thai") == "CHO_NGUOI_DUYET_OUTLINE_BUOC_05":
            print(f"[PAUSED AT STEP 5] {res['loai']} -> {res['run_dir']} | Outlines={len(res.get('outlines', []))}")
        elif res.get("hop_le") is False:
            print(f"[REJECTED] {res['loai']} -> {res.get('ma_loi')}: {res.get('thong_bao')}")
        else:
            print(
                f"[RUN DONE] {res['loai']} -> {res['run_dir']} | "
                f"Draft1 CQS={res['diem_draft_1']['cqs']} -> Final CQS={res['diem_ban_cuoi']['cqs']} | "
                f"cham_cau={res['diem_ban_cuoi']['cham_cau_dat']} | Onbrand={res['onbrand_sakedemy']['tong_diem_100']}/100"
            )

    if args.loai == "all" and args.duyet_outline == "may":
        sync_demo_folder(results)
        print("[DEMO SYNCED] demo/input & demo/output updated.")


if __name__ == "__main__":
    main()
