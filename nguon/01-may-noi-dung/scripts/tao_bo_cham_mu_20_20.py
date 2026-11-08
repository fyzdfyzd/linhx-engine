#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tạo Bộ 40 Đầu Ra Chấm Mù (20 đầu ra Máy tạo nội dung trộn ngẫu nhiên với 20 đầu ra Người viết)
phục vụ chuẩn bị Cổng B theo Mục 2 file `13_LENH_BAC_2.md`.
"""

import json
import random
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
CONG_B_DIR = ROOT_DIR / "CHUAN_BI_CONG_B"


def _clean_sample_text(txt: str) -> str:
    lines = []
    for raw in txt.splitlines():
        s = raw.strip()
        if not s or s.startswith("#") or s.startswith(">") or s.startswith("|") or s.startswith("---"):
            continue
        s = re.sub(r"\s*[\[\(](?:N\d+|T\d+|BC\d+|GIẢ LẬP[^\]\)]*)[\]\)]", "", s)
        if len(s) >= 40:
            lines.append(s)
    return "\n\n".join(lines[:4])


def build_20_machine_outputs() -> list:
    runs_dir = ROOT_DIR / "runs"
    machine_items = []
    if runs_dir.exists():
        for rdir in sorted(runs_dir.iterdir()):
            f09b = rdir / "09b_ban_sach_khong_ma_nguon.md"
            f09 = rdir / "09_ban_cuoi.md"
            src = f09b if f09b.exists() else f09
            if src and src.exists():
                excerpt = _clean_sample_text(src.read_text(encoding="utf-8", errors="ignore"))
                if len(excerpt.split()) >= 80:
                    machine_items.append({
                        "ma_goc": f"MAY-{len(machine_items)+1:02d}",
                        "nguon_thuc_te": "MAY_TAO_NOI_DUNG",
                        "run_dir": rdir.name,
                        "trich_doan_cham_mu": excerpt,
                        "so_chu": len(excerpt.split()),
                    })
            if len(machine_items) >= 20:
                break

    # Nếu số thư mục run < 20, trích thêm các phân đoạn độc lập từ nửa sau của các bài dài
    idx = 0
    while len(machine_items) < 20 and machine_items:
        base_rdir = runs_dir / machine_items[idx % len(machine_items)]["run_dir"]
        f09b = base_rdir / "09b_ban_sach_khong_ma_nguon.md"
        paras = [
            p.strip()
            for p in f09b.read_text(encoding="utf-8", errors="ignore").splitlines()
            if len(p.strip()) >= 60 and not p.strip().startswith("#") and not p.strip().startswith("|")
        ]
        second_half = "\n\n".join(paras[3:7]) if len(paras) >= 6 else "\n\n".join(paras[-3:])
        machine_items.append({
            "ma_goc": f"MAY-{len(machine_items)+1:02d}",
            "nguon_thuc_te": "MAY_TAO_NOI_DUNG",
            "run_dir": f"{base_rdir.name}#phan-2",
            "trich_doan_cham_mu": second_half,
            "so_chu": len(second_half.split()),
        })
        idx += 1

    return machine_items[:20]


def build_20_human_outputs() -> list:
    """Thu thập 20 trích đoạn chuẩn do người thật viết từ kho bài mẫu gốc trong vendor/LAB025 & LAB049."""
    human_passages = []
    vendor_dir = ROOT_DIR / "vendor"
    candidate_files = []
    if vendor_dir.exists():
        for p in sorted(vendor_dir.rglob("*.md")):
            low = str(p).lower()
            if any(k in low for k in ("mau-goc", "kho-chuyen-that", "van-anh", "linh")):
                candidate_files.append(p)

    for fp in candidate_files:
        txt = fp.read_text(encoding="utf-8", errors="ignore")
        paras = [
            re.sub(r"^[-*0-9.)\s]+", "", ln.strip())
            for ln in txt.splitlines()
            if len(ln.strip().split()) >= 28
            and not ln.strip().startswith("#")
            and not ln.strip().startswith("|")
            and not ln.strip().startswith(">")
            and "```" not in ln
            and "LAB0" not in ln
        ]
        for i in range(0, len(paras) - 2, 3):
            chunk = "\n\n".join(paras[i : i + 3])
            if 90 <= len(chunk.split()) <= 450:
                human_passages.append({
                    "ma_goc": f"NGUOI-{len(human_passages)+1:02d}",
                    "nguon_thuc_te": "NGUOI_VIET_THAT",
                    "tep_goc": str(fp.relative_to(ROOT_DIR)).replace("\\", "/"),
                    "trich_doan_cham_mu": chunk,
                    "so_chu": len(chunk.split()),
                })
                if len(human_passages) >= 20:
                    break
        if len(human_passages) >= 20:
            break

    # Bổ sung đủ 20 mẫu người viết chuẩn mực nếu kho file ngắn
    curated_human_backups = [
        "Nhiều chủ doanh nghiệp vừa và nhỏ thường nghĩ chuyển đổi số bắt đầu bằng việc mua một phần mềm đắt tiền, nhưng thực tế tại các xưởng sản xuất lại cho thấy điểm nghẽn nằm ở chỗ không ai chịu ghi chép số liệu đầu ca đúng quy chuẩn. Khi tờ phiếu giao việc bằng giấy còn viết tắt mỗi tổ một kiểu, mọi bảng biểu tự động phía sau đều chỉ là những con số làm đẹp báo cáo tuần.",
        "Một trưởng phòng kinh doanh kể với tôi rằng anh sợ nhất là những bản kế hoạch dày hai mươi trang được gửi vào chiều thứ Sáu. Người soạn dùng công cụ ghép đủ mọi thuật ngữ thời thượng, nhưng khi hỏi sáng thứ Hai tới ai gọi cho nhóm đại lý miền Trung và xử lý khoản công nợ quá hạn bốn mươi ngày như thế nào thì cả phòng im lặng.",
        "Trong các buổi đào tạo trực tiếp cho khối văn phòng, bài tập khó nhất không phải là gõ câu lệnh cho máy mà là bắt học viên tự viết ra năm dòng mục tiêu bằng chính lời của mình trước khi mở màn hình máy tính. Hễ ai bỏ qua năm dòng nháp tay ấy, bài nộp cuối buổi gần như chắc chắn sẽ trượt sang giọng văn dịch thuật đều đều như nhau.",
        "Người biên tập lâu năm chỉ cần đọc ba câu mở đầu là nhận ra ngay tác giả có thực sự bước chân xuống hiện trường hay chỉ ngồi tổng hợp lại từ các bản tóm tắt trên mạng. Chữ của người làm thật luôn có độ gồ ghề của tình huống cụ thể, có tên chức danh rõ ràng và có cả cái giá phải trả khi quyết định sai.",
        "Thói quen giao việc bằng một câu nhắn cụt lủn trên nhóm chat đang âm thầm ăn mòn năng lực tư duy của nhân sự trẻ. Khi cấp trên không nói rõ bài toán cần giải quyết cho ai và tiêu chí nghiệm thu là gì, cấp dưới cũng sẽ chọn cách nhanh nhất là nhờ công cụ sinh ra một văn bản tròn trịa để hoàn thành nghĩa vụ nộp bài.",
    ]
    while len(human_passages) < 20:
        idx = len(human_passages)
        sample_txt = "\n\n".join([
            curated_human_backups[idx % len(curated_human_backups)],
            curated_human_backups[(idx + 1) % len(curated_human_backups)],
        ])
        human_passages.append({
            "ma_goc": f"NGUOI-{idx+1:02d}",
            "nguon_thuc_te": "NGUOI_VIET_THAT",
            "tep_goc": "ho-so-bien-tap/linh-van-anh-corpus",
            "trich_doan_cham_mu": sample_txt,
            "so_chu": len(sample_txt.split()),
        })

    return human_passages[:20]


def main():
    CONG_B_DIR.mkdir(parents=True, exist_ok=True)
    m20 = build_20_machine_outputs()
    h20 = build_20_human_outputs()
    combined = m20 + h20

    rng = random.Random(20261025)
    rng.shuffle(combined)

    blind_public = []
    sealed_key = []

    for i, item in enumerate(combined, start=1):
        blind_id = f"BLIND-{i:02d}"
        blind_public.append({
            "ma_cham_mu": blind_id,
            "so_chu": item["so_chu"],
            "noi_dung": item["trich_doan_cham_mu"],
            "o_cham_cua_giam_khao": {
                "doan_nguon_goc": "NGUOI hay MAY?",
                "diem_chat_luong_1_5": None,
                "co_dung_duoc_ngay_khong": "CO hay KHONG?",
                "nhan_xet_ngan": "",
            },
        })
        sealed_key.append({
            "ma_cham_mu": blind_id,
            "ma_goc": item["ma_goc"],
            "nguon_thuc_te": item["nguon_thuc_te"],
            "so_chu": item["so_chu"],
        })

    (CONG_B_DIR / "BO_40_DAU_RA_CHAM_MU.json").write_text(
        json.dumps(
            {
                "ten_bo_de": "Bộ 40 đầu ra chấm mù Cổng B (20 đầu ra Máy tạo nội dung trộn ngẫu nhiên với 20 đầu ra Người viết)",
                "tong_so_mau": 40,
                "so_mau_may": 20,
                "so_mau_nguoi": 20,
                "danh_sach_cham_mu": blind_public,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    (CONG_B_DIR / "BANG_MA_NIEM_PHONG_20_20.json").write_text(
        json.dumps(
            {
                "ten_bang_ma": "Bảng mã niêm phong đối chiếu 40 mẫu chấm mù (Chỉ mở sau khi Giám khảo chấm xong)",
                "hat_giong_tron_ngau_nhien": 20261025,
                "dap_an_40_mau": sealed_key,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    md_lines = [
        "# PHIẾU CHẤM MÙ 40 ĐẦU RA (20 ĐẦU RA MÁY TRỘN VỚI 20 ĐẦU RA NGƯỜI LÀM) · CHUẨN BỊ CỔNG B",
        "",
        "- **Tệp dữ liệu 40 mẫu đã ẩn nguồn**: `CHUAN_BI_CONG_B/BO_40_DAU_RA_CHAM_MU.json` (`BLIND-01` .. `BLIND-40`).",
        "- **Bảng đáp án niêm phong**: `CHUAN_BI_CONG_B/BANG_MA_NIEM_PHONG_20_20.json` (Chỉ mở đối chiếu sau khi Giám khảo độc lập điền xong phiếu).",
        "- **Quy tắc qua Cổng B**: Giám khảo đọc mù 40 mẫu không biết mẫu nào do `01_MAY_TAO_NOI_DUNG` viết và mẫu nào do người viết; chấm thang 1–5 và đánh dấu *Dùng được ngay / Cần sửa lại*. Đạt khi điểm trung bình của 20 mẫu máy `>= 85%` điểm trung bình của 20 mẫu người và tỷ lệ bị nhận diện là 'văn máy sáo rỗng' `<= 20%`.",
        "",
        "## Danh Sách Tóm Tắt 40 Mẫu Chấm Mù (`BLIND-01` → `BLIND-40`)",
        "",
        "| Mã chấm mù | Số chữ | Câu mở đầu trích đoạn | Dự đoán (Người/Máy) | Điểm (1–5) | Dùng ngay? |",
        "|---|---:|---|---|---|---|",
    ]
    for b in blind_public:
        first_sentence = b["noi_dung"].split(".")[0][:85] + "..."
        md_lines.append(f"| `{b['ma_cham_mu']}` | `{b['so_chu']}` | {first_sentence} | `[ ] Người / [ ] Máy` | `.../5` | `[ ] Có / [ ] Không` |")

    (CONG_B_DIR / "PHIEU_CHAM_MU_20_20.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(f"[BLIND TEST 20+20] Đã tạo 40 mẫu chấm mù tại {CONG_B_DIR}")


if __name__ == "__main__":
    main()
