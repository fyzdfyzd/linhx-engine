# -*- coding: utf-8 -*-
"""
Cập nhật các trang HTML xuất bản (`bai_viet_trang_doc_sakedemy.html`, `bao_cao_sakedemy_a4.html`, `slide_deck_sakedemy_16x9.html`)
trên toàn bộ 13 bài chạy trong `runs/` theo từng vòng E2E:
- `--stage round2`: Vá `REV-R1-01` (đổi URI `file:///D:/...` sang đường dẫn tương đối `./...` để hiển thị trên HTTP server)
  và `REV-R1-02` (bổ sung tiêu đề phân mục `<h2>` chuẩn biên tập & chuyển `**...**` thành `<strong>`).
- `--stage round3`: Vá triệt để `REV-R1-03` / `REV-R2-01` (đồng bộ động nội dung `.photo-caption`, `.callout-leaf` và tiêu đề `<h1>`
  của Slide 02/04 theo đúng đề tài, `noi_dung_banner.json` và `04-hinh.json` của từng bài).
"""

from __future__ import annotations

import argparse
import html as H
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RUNS_DIR = BASE_DIR / "runs"


def format_paragraphs_with_h2(clean_text: str, loai: str) -> str:
    paras = [
        line.strip()
        for line in clean_text.splitlines()
        if line.strip() and not line.strip().startswith("#") and not line.strip().startswith("|")
    ]
    if loai == "bai_viet":
        headings = [
            "1. Hiện tượng & Điểm nghẽn trong vận hành thực tế",
            "2. Bằng chứng nghiên cứu & Phân tích nguyên nhân gốc",
            "3. Kiến trúc giữ chốt chuyên môn & Quy trình nghiệm thu",
        ]
    else:
        headings = [
            "1. Chẩn đoán thực trạng & Rủi ro hệ thống",
            "2. Đối chiếu dữ liệu kiểm toán & Đo lường hiệu suất",
            "3. Khuyến nghị điều hành & Lộ trình triển khai 90 ngày",
        ]

    blocks: list[str] = []
    for idx, p in enumerate(paras):
        if idx == 0:
            blocks.append(f'<h2 style="color:#02403B; font-size:20px; margin:18px 0 8px 0;">{H.escape(headings[0])}</h2>')
        elif idx == 2 and len(paras) >= 4:
            blocks.append(f'<h2 style="color:#02403B; font-size:20px; margin:18px 0 8px 0;">{H.escape(headings[1])}</h2>')
        elif idx == 4 and len(paras) >= 5:
            blocks.append(f'<h2 style="color:#02403B; font-size:20px; margin:18px 0 8px 0;">{H.escape(headings[2])}</h2>')

        esc = H.escape(p)
        esc = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", esc)
        blocks.append(f"<p>{esc}</p>")
    return "\n".join(blocks)


def patch_all_runs(stage: str) -> int:
    count = 0
    for run_dir in sorted(RUNS_DIR.iterdir()):
        if not run_dir.is_dir():
            continue
        media_dir = run_dir / "media"
        if not media_dir.is_dir():
            continue

        p09b = run_dir / "09b_ban_sach_khong_ma_nguon.md"
        clean_md = p09b.read_text(encoding="utf-8") if p09b.exists() else ""

        banner_json = media_dir / "noi_dung_banner.json"
        banner_info = json.loads(banner_json.read_text(encoding="utf-8")) if banner_json.exists() else {}

        hinh_json = media_dir / "04-hinh.json"
        hinh_list = json.loads(hinh_json.read_text(encoding="utf-8")).get("hinh", []) if hinh_json.exists() else []
        h01_title = hinh_list[0]["tieu_de"] if len(hinh_list) >= 1 else "Biểu đồ dữ liệu thực chứng H01"
        h02_title = hinh_list[1]["tieu_de"] if len(hinh_list) >= 2 else "Biểu đồ dữ liệu thực chứng H02"

        # 1. Bài viết (`bai_viet_trang_doc_sakedemy.html`)
        art_html_path = media_dir / "bai_viet_trang_doc_sakedemy.html"
        if art_html_path.exists():
            txt = art_html_path.read_text(encoding="utf-8")
            if '<link rel="icon"' not in txt:
                txt = txt.replace('<meta charset="utf-8"/>', '<meta charset="utf-8"/>\n<link rel="icon" href="data:,"/>')
            # Fix REV-R1-01: relative image URLs
            txt = re.sub(r'src="file:///[^"]+/sakedemy_banner_1920x600\.png"', 'src="./sakedemy_banner_1920x600.png"', txt)
            txt = re.sub(r'src="file:///[^"]+/agy_anh_goc_sakedemy\.jpg"', 'src="./agy_anh_goc_sakedemy.jpg"', txt)
            txt = re.sub(r'src="file:///[^"]+/sakedemy_social_1080x1080\.png"', 'src="./sakedemy_social_1080x1080.png"', txt)

            # Fix REV-R1-02: insert structured h2 + paragraphs
            body_with_h2 = format_paragraphs_with_h2(clean_md, "bai_viet")
            txt = re.sub(
                r'(<div class="exhibit-box">.*?</svg>\s*</div>)\s*(?:<h2|<p>).*?(?=\s*<div class="exhibit-box">)',
                lambda m: m.group(1) + "\n  " + body_with_h2,
                txt,
                flags=re.DOTALL,
            )

            # Fix REV-R1-03 / REV-R2-01 in round3: dynamic photo caption
            if stage == "round3":
                mo_ta = banner_info.get("mo_ta", h01_title)
                dynamic_caption = (
                    f'<div class="photo-caption">\n'
                    f"      <strong>Ảnh minh hoạ thực tế (AGY image-generator):</strong><br/>\n"
                    f"      {H.escape(mo_ta)} (Biểu đồ trọng tâm: {H.escape(h01_title)})<br/><br/>\n"
                    f'      <img src="./sakedemy_social_1080x1080.png" alt="Social Card 1080x1080" style="max-width: 220px; margin-top: 8px;"/>\n'
                    f"    </div>"
                )
                txt = re.sub(
                    r'<div class="photo-caption">.*?</div>',
                    lambda _: dynamic_caption,
                    txt,
                    flags=re.DOTALL,
                )
            art_html_path.write_text(txt, encoding="utf-8")
            count += 1

        # 2. Report mẫu (`bao_cao_sakedemy_a4.html`)
        rep_html_path = media_dir / "bao_cao_sakedemy_a4.html"
        if rep_html_path.exists():
            txt = rep_html_path.read_text(encoding="utf-8")
            if '<link rel="icon"' not in txt:
                txt = txt.replace('<meta charset="utf-8"/>', '<meta charset="utf-8"/>\n<link rel="icon" href="data:,"/>')
            txt = re.sub(r'src="file:///[^"]+/agy_anh_goc_sakedemy\.jpg"', 'src="./agy_anh_goc_sakedemy.jpg"', txt)
            txt = re.sub(r'src="file:///[^"]+/sakedemy_slide_1920x1080\.png"', 'src="./sakedemy_slide_1920x1080.png"', txt)

            body_with_h2 = format_paragraphs_with_h2(clean_md, "report_mau")
            txt = re.sub(
                r'<div class="two-col">.*?</div>',
                lambda _: f'<div class="two-col">\n    {body_with_h2}\n  </div>',
                txt,
                flags=re.DOTALL,
            )

            if stage == "round3":
                mo_ta = banner_info.get("mo_ta", "")
                callout_str = (
                    f'<div class="callout-leaf">\n'
                    f"    Điểm chốt dành cho Ban điều hành: {H.escape(h01_title)} {H.escape(mo_ta)}\n"
                    f"  </div>"
                )
                txt = re.sub(
                    r'<div class="callout-leaf">.*?</div>',
                    lambda _: callout_str,
                    txt,
                    flags=re.DOTALL,
                )
            rep_html_path.write_text(txt, encoding="utf-8")
            count += 1

        # 3. Nội dung khoá học (`slide_deck_sakedemy_16x9.html`)
        sld_html_path = media_dir / "slide_deck_sakedemy_16x9.html"
        if sld_html_path.exists():
            txt = sld_html_path.read_text(encoding="utf-8")
            if '<link rel="icon"' not in txt:
                txt = txt.replace('<meta charset="utf-8"/>', '<meta charset="utf-8"/>\n<link rel="icon" href="data:,"/>')
            txt = re.sub(r'src="file:///[^"]+/agy_anh_goc_sakedemy\.jpg"', 'src="./agy_anh_goc_sakedemy.jpg"', txt)
            txt = re.sub(r'src="file:///[^"]+/sakedemy_slide_1920x1080\.png"', 'src="./sakedemy_slide_1920x1080.png"', txt)

            if stage == "round3":
                mo_ta = banner_info.get("mo_ta", "")
                vis_json_path = media_dir / "noi_dung_visual.json"
                vis_info = json.loads(vis_json_path.read_text(encoding="utf-8")) if vis_json_path.exists() else {}
                vis_title = vis_info.get("tieu_de", "Ba chốt chặn chống Slop").replace("\n", " ")
                txt = txt.replace(
                    "<h1>Cộng tác phản biện giúp nâng điểm thẩm định từ 31% lên 88% [N1]</h1>",
                    f"<h1>{H.escape(h01_title)}</h1>",
                )
                txt = txt.replace(
                    "<h1>Ba chốt chặn chống Slop (Ấn phẩm render từ khuôn LAB043 v1.2-chot)</h1>",
                    f"<h1>{H.escape(vis_title)} (Khuôn chuẩn LAB043 v1.2-chot)</h1>",
                )
                txt = txt.replace(
                    "<h1>Thực hành phẫu thuật bản nháp AI chiếm trọn 50% thời gian buổi học [N3]</h1>",
                    f"<h1>{H.escape(h02_title)}</h1>",
                )
                if mo_ta:
                    txt = txt.replace(
                        "Mục tiêu đầu ra: Học viên tự lập Khung Hạt Giống 5 Dòng và kiểm toán bản nháp AI đạt CQS &ge; 85 ngay tại lớp.",
                        f"Mục tiêu đầu ra: {H.escape(mo_ta)}",
                    )
            sld_html_path.write_text(txt, encoding="utf-8")
            count += 1

    return count


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True, choices=["round2", "round3"])
    args = parser.parse_args()
    n = patch_all_runs(args.stage)
    print(f"Patched {n} publication HTML files for stage={args.stage}")
