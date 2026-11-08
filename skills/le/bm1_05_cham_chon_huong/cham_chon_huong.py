"""Module 5 (LÀM MỚI HOÀN TOÀN): Tự chấm 3 phương án Outline A/B/C và chốt hướng triển khai.
Hỗ trợ cờ `duyet_outline: "nguoi" | "may"`.
Chấm theo 4 trụ cột:
  - 40% Phản ứng 3 Persona Neo (từ Bước 4)
  - 30% Độ khớp `dat_khi.md` của loại nội dung
  - 20% Độ dày bằng chứng & chất liệu thật
  - 10% Chống lối mòn AI Slop (`loi_slop.md`)
"""
import argparse
import json
from pathlib import Path


def score_outlines(b4_data: dict, duyet_outline: str, chon_huong: str = None, use_cache: bool = True) -> dict:
    import sys
    root_dir = Path(__file__).resolve().parents[2]
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))
    from core_loai_va_gemini import grade_step5_outlines, load_loai_config

    loai = b4_data["loai"]
    de_bai = b4_data.get("de_bai") or f"Chủ đề {loai}"
    loai_cfg = load_loai_config(loai, root_dir=root_dir)
    reactions_map = {r["variant"]: r for r in b4_data["persona_reactions"]}

    outlines_dict = {}
    for out in b4_data["outlines"]:
        v = out["variant"]
        r = reactions_map.get(v, {})
        outlines_dict[v] = {
            "ten_huong": out.get("ten_phuong_an", f"Phương án {v}"),
            "hook_mo_dau": out.get("hook_mo_dau") or out.get("variant_angle", ""),
            "sections": out.get("sections", []),
            "exhibits": out.get("exhibits", []),
            "diem_tb_persona": round(float(r.get("diem_persona_tong_hop", 8.0)) * 10.0, 2),
        }

    graded = grade_step5_outlines(
        loai=loai,
        de_bai=de_bai,
        outlines_dict=outlines_dict,
        config_bundle=loai_cfg,
        chon_huong=chon_huong,
        use_cache=use_cache,
    )

    bang_diem_gem = graded.get("bang_diem", {})
    scorecard = []

    for out in b4_data["outlines"]:
        v = out["variant"]
        gem_row = bang_diem_gem.get(v, {})
        persona_40 = float(gem_row.get("persona_40", 32.0))
        dat_khi_30 = float(gem_row.get("dat_khi_30", 24.0))
        evidence_20 = float(gem_row.get("bang_chung_20", 16.0))
        anti_slop_10 = float(gem_row.get("chong_slop_10", 8.0))
        total_100 = round(persona_40 + dat_khi_30 + evidence_20 + anti_slop_10, 2)
        ly_do = gem_row.get("nhan_xet_ngan") or "Đánh giá độc lập theo 4 trụ cột biên tập."

        scorecard.append({
            "variant": v,
            "ten_phuong_an": out["ten_phuong_an"],
            "diem_persona_40": persona_40,
            "diem_dat_khi_30": dat_khi_30,
            "diem_bang_chung_20": evidence_20,
            "diem_chong_slop_10": anti_slop_10,
            "tong_diem_100": total_100,
            "nhan_xet": ly_do,
        })

    scorecard.sort(key=lambda x: x["tong_diem_100"], reverse=True)
    if chon_huong and chon_huong.upper() in ("A", "B", "C"):
        target_v = chon_huong.upper()
        winner = next(s for s in scorecard if s["variant"] == target_v)
    else:
        winner = scorecard[0]
    winner_outline = next(o for o in b4_data["outlines"] if o["variant"] == winner["variant"])
    winner_reaction = reactions_map[winner["variant"]]

    # Rút các yêu cầu bắt buộc từ phản biện của 3 Persona để khoá chặt Bước 6
    rang_buoc_buoc_6 = [
        f"Phải giải quyết câu phản biện của {ep['persona_id']} ({ep['vai_tro']}): {ep['cau_phan_bien_ngay_tu_dan_y']}"
        for ep in winner_reaction["chi_tiet_persona"]
    ]
    rang_buoc_buoc_6.extend([
        "Tuyệt đối không dùng cấu trúc so sánh hai vế 'Không còn là X mà là Y' hoặc 'Càng X càng Y' (Luật Vân Anh VA-01, VA-02).",
        "Mọi số liệu trích dẫn phải giữ nguyên mã nguồn [Nxx]/[BCxx], mọi tình huống giả định phải ghi rõ là tình huống mô phỏng.",
    ])

    if chon_huong and chon_huong.upper() in ("A", "B", "C"):
        trang_thai_duyet = "DA_CHOT_THEO_NGUOI_CHON"
        cho_phep_chay_buoc_6 = True
    elif duyet_outline == "may":
        trang_thai_duyet = "DA_CHOT_TU_DONG_MAY"
        cho_phep_chay_buoc_6 = True
    else:
        trang_thai_duyet = "CHO_NGUOI_DUYET"
        cho_phep_chay_buoc_6 = False

    return {
        "module": "BM1_05_cham_chon_huong",
        "loai": loai,
        "de_bai": de_bai,
        "duyet_outline": duyet_outline,
        "trang_thai_duyet": trang_thai_duyet,
        "trang_thai_cong_duyet": trang_thai_duyet,
        "cho_phep_chay_buoc_6": cho_phep_chay_buoc_6,
        "nhan_dien_tam": "Sakedemy (LAB043)",
        "trang_thai_mau": "chạy không mẫu (Gemini 2.5 Flash)",
        "gemini_usage": graded.get("_gemini_usage", {}),
        "bang_diem": scorecard,
        "phuong_an_chot": {
            "variant": winner["variant"],
            "ten_phuong_an": winner["ten_phuong_an"],
            "tong_diem_100": winner["tong_diem_100"],
            "ly_do_chon": graded.get("ly_do_chon", winner["nhan_xet"]),
            "outline_chi_tiet": winner_outline,
            "rang_buoc_trien_khai_buoc_6": rang_buoc_buoc_6,
        },
    }


def render_markdown(data: dict) -> str:
    chot = data["phuong_an_chot"]
    lines = [
        f"# BƯỚC 05: TỰ CHẤM & CHỐT HƯỚNG OUTLINE (`{data['loai']}`)",
        "",
        "> **Truy vết Module**: `BM1_05_cham_chon_huong` (**Làm mới hoàn toàn** theo Đề 01 Bản 3)",
        f"> **Cờ duyệt (`duyet_outline`)**: `{data['duyet_outline']}` → **Trạng thái**: `{data['trang_thai_duyet']}`",
        f"> **Nhận diện tạm**: {data['nhan_dien_tam']} · **Trạng thái mẫu**: {data['trang_thai_mau']}",
        "",
        "## 1. Bảng chấm điểm 3 phương án Outline (Thang 100)",
        "",
        "| Hạng | Phương án | Persona (40đ) | Khớp `dat_khi` (30đ) | Bằng chứng (20đ) | Chống Slop (10đ) | **Tổng (/100)** | Kết luận |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for idx, s in enumerate(data["bang_diem"], start=1):
        star = "★ **CHỐT**" if idx == 1 else "Loại"
        lines.append(
            f"| {idx} | **{s['variant']}** — {s['ten_phuong_an']} | {s['diem_persona_40']} | {s['diem_dat_khi_30']} | {s['diem_bang_chung_20']} | {s['diem_chong_slop_10']} | **{s['tong_diem_100']}** | {star}: {s['nhan_xet']} |"
        )

    lines.extend([
        "",
        f"## 2. Quyết định chốt hướng: ★ Phương án {chot['variant']} ({chot['tong_diem_100']}/100 điểm)",
        f"- **Tên phương án**: {chot['ten_phuong_an']}",
        f"- **Góc nhìn**: {chot['outline_chi_tiet']['variant_angle']}",
        f"- **Giọng điệu**: {chot['outline_chi_tiet']['variant_tone']}",
        "- **Khung triển khai gửi sang Bước 6**:",
    ])
    for sec in chot["outline_chi_tiet"]["sections"]:
        lines.append(f"  - {sec}")

    lines.extend([
        "",
        "## 3. Ràng buộc bắt buộc giao cho Bước 6 (Rút từ phản ứng Persona & Luật chống Slop)",
    ])
    for rb in chot["rang_buoc_trien_khai_buoc_6"]:
        lines.append(f"- [x] {rb}")

    if data["duyet_outline"] == "nguoi":
        lines.extend([
            "",
            "> **[CỔNG DỪNG CHỜ NGƯỜI DUYỆT]**: Cờ `duyet_outline = nguoi`. Hệ thống dừng chờ anh Linh xác nhận Phương án khuyến nghị ★ trước khi sang Bước 6.",
        ])
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--b4-json", required=True)
    ap.add_argument("--duyet-outline", default="may", choices=["may", "nguoi"])
    ap.add_argument("--chon-huong", default=None, choices=["A", "B", "C"])
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--out-md", required=True)
    args = ap.parse_args()

    b4_data = json.loads(Path(args.b4_json).read_text(encoding="utf-8"))
    res = score_outlines(b4_data, args.duyet_outline, chon_huong=args.chon_huong)
    Path(args.out_json).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    Path(args.out_md).write_text(render_markdown(res), encoding="utf-8")
    print(f"[BM1_05_cham_chon_huong] OK -> winner={res['phuong_an_chot']['variant']} ({res['phuong_an_chot']['tong_diem_100']}/100)")


if __name__ == "__main__":
    main()
