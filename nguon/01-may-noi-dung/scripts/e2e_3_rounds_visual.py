# -*- coding: utf-8 -*-
"""
Script thực thi E2E 3-Rounds Harsh Reviewer & Visual Screenshot Audit (`e2e_3_rounds_visual.py`).
Khởi chạy HTTP server nội bộ, điều khiển trình duyệt thật bằng Playwright (Microsoft Edge Headless),
chạy kịch bản End-to-End qua Web Hub 13 bài + các trang xuất bản HTML (Bài viết, Report A4, Slide 16:9, Báo cáo Onbrand),
chụp ảnh màn hình độ phân giải cao vào `reports/screens/round{N}/*.png`,
kiểm toán DOM/Thị giác/WCAG và ghi checkpoint vào `.handoff/e2e-checkpoint.json`.
"""

from __future__ import annotations

import argparse
import functools
import http.server
import json
import shutil
import socket
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = BASE_DIR.parent
REPORTS_DIR = BASE_DIR / "reports"
HANDOFF_DIR = WORKSPACE_ROOT / ".handoff"


def start_local_http_server(root_dir: Path) -> tuple[http.server.ThreadingHTTPServer, int]:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(root_dir))

    class QuietServer(http.server.ThreadingHTTPServer):
        allow_reuse_address = True

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]

    httpd = QuietServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd, port


def audit_page_dom(page) -> dict[str, Any]:
    return page.evaluate(
        """() => {
        const imgs = Array.from(document.querySelectorAll('img'));
        const brokenImgs = imgs.filter(img => !img.complete || img.naturalWidth === 0).map(img => img.getAttribute('src') || '');
        const svgs = Array.from(document.querySelectorAll('svg'));
        const validSvgs = svgs.filter(s => {
            const r = s.getBoundingClientRect();
            return r.width > 50 && r.height > 50;
        }).length;
        const smallTapTargets = Array.from(document.querySelectorAll('button, a.action-link, a.filter-btn')).filter(el => {
            const r = el.getBoundingClientRect();
            return r.width > 0 && r.height > 0 && (r.width < 32 || r.height < 32);
        }).length;
        const cards = Array.from(document.querySelectorAll('.run-card'));
        const maxCardChars = cards.reduce((m, c) => Math.max(m, (c.innerText || '').trim().length), 0);
        const fixedFooter = (() => {
            const f = document.querySelector('footer.app-footer');
            if (!f) return false;
            return window.getComputedStyle(f).position === 'fixed';
        })();
        const hasSkipLink = !!document.querySelector('.skip-link');
        const hasLegendBar = !!document.querySelector('.legend-bar');
        const rawMarkdownBoldCount = (document.body.innerText.match(/\\*\\*[^*]+\\*\\*/g) || []).length;
        const h2Count = document.querySelectorAll('h2').length;
        const bodyText = document.body.innerText || '';
        return {
            totalImgs: imgs.length,
            brokenImgsCount: brokenImgs.length,
            brokenImgs: brokenImgs.slice(0, 5),
            svgCount: svgs.length,
            validSvgs: validSvgs,
            smallTapTargets: smallTapTargets,
            cardsCount: cards.length,
            maxCardChars: maxCardChars,
            fixedFooter: fixedFooter,
            hasSkipLink: hasSkipLink,
            hasLegendBar: hasLegendBar,
            rawMarkdownBoldCount: rawMarkdownBoldCount,
            h2Count: h2Count,
            bodyTextLen: bodyText.length,
            bodyTextSample: bodyText.slice(0, 600)
        };
    }"""
    )


def run_e2e_round(round_num: int) -> dict[str, Any]:
    screens_round_dir = REPORTS_DIR / "screens" / f"round{round_num}"
    screens_round_dir.mkdir(parents=True, exist_ok=True)
    HANDOFF_DIR.mkdir(parents=True, exist_ok=True)

    httpd, port = start_local_http_server(BASE_DIR)
    base_url = f"http://127.0.0.1:{port}"
    console_errors: list[str] = []
    screenshots: list[str] = []
    findings: list[dict[str, str]] = []
    scenarios_results: dict[str, Any] = {}

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="msedge", headless=True)

            # 1. Desktop Hub View (1440x900)
            page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1.5)
            page.on("console", lambda msg: console_errors.append(f"[hub] {msg.text}") if msg.type == "error" else None)
            page.goto(f"{base_url}/web/index.html", wait_until="networkidle")
            shot1 = screens_round_dir / "01-hub-desktop-all.png"
            page.screenshot(path=str(shot1), full_page=True)
            screenshots.append(str(shot1))
            hub_dom = audit_page_dom(page)
            scenarios_results["01_hub_desktop"] = hub_dom

            # 2. Filter "Report mẫu (4)" & Select BAI_08
            page.click("button[data-filter='report_mau']")
            page.wait_for_timeout(150)
            report_cards_count = page.locator(".run-card").count()
            bai08_selector = ".run-card[data-run-id='2026-10-25_report_mau_kiem-toan-rui-ro-shadow-ai-va-quyen-rieng-tu-2026']"
            if page.locator(bai08_selector).count() > 0:
                page.click(bai08_selector)
                page.wait_for_timeout(150)
            shot2 = screens_round_dir / "02-hub-filter-report.png"
            page.screenshot(path=str(shot2), full_page=True)
            screenshots.append(str(shot2))
            scenarios_results["02_hub_filter_report"] = {
                "report_cards_count": report_cards_count,
                "selected_title": page.locator("#detail-panel h2").inner_text(),
            }

            # 3. Mobile Hub View (390x844)
            page_mob = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
            page_mob.goto(f"{base_url}/web/index.html", wait_until="networkidle")
            shot3 = screens_round_dir / "03-hub-mobile-390x844.png"
            page_mob.screenshot(path=str(shot3), full_page=True)
            screenshots.append(str(shot3))
            mob_dom = audit_page_dom(page_mob)
            scenarios_results["03_hub_mobile"] = mob_dom
            page_mob.close()

            # 4. Article Publication Page (BAI_04: bay-do-luong-kpi-so-luong-prompt)
            page_art = browser.new_page(viewport={"width": 1200, "height": 900}, device_scale_factor=1.5)
            page_art.on("console", lambda msg: console_errors.append(f"[article] {msg.text}") if msg.type == "error" else None)
            art_url = f"{base_url}/runs/2026-10-25_bai_viet_bay-do-luong-kpi-so-luong-prompt/media/bai_viet_trang_doc_sakedemy.html"
            page_art.goto(art_url, wait_until="networkidle")
            shot4 = screens_round_dir / "04-bai-viet-publication.png"
            page_art.screenshot(path=str(shot4), full_page=True)
            screenshots.append(str(shot4))
            art_dom = audit_page_dom(page_art)
            art_caption = page_art.locator(".photo-caption").inner_text() if page_art.locator(".photo-caption").count() else ""
            art_dom["photo_caption"] = art_caption
            scenarios_results["04_bai_viet_publication"] = art_dom
            page_art.close()

            # 5. Report A4 Publication Page (BAI_08: kiem-toan-rui-ro-shadow-ai-va-quyen-rieng-tu-2026)
            page_rep = browser.new_page(viewport={"width": 1200, "height": 900}, device_scale_factor=1.5)
            page_rep.on("console", lambda msg: console_errors.append(f"[report] {msg.text}") if msg.type == "error" else None)
            rep_url = f"{base_url}/runs/2026-10-25_report_mau_kiem-toan-rui-ro-shadow-ai-va-quyen-rieng-tu-2026/media/bao_cao_sakedemy_a4.html"
            page_rep.goto(rep_url, wait_until="networkidle")
            shot5 = screens_round_dir / "05-report-a4-publication.png"
            page_rep.screenshot(path=str(shot5), full_page=True)
            screenshots.append(str(shot5))
            rep_dom = audit_page_dom(page_rep)
            callout_text = page_rep.locator(".callout-leaf").inner_text() if page_rep.locator(".callout-leaf").count() else ""
            rep_dom["callout_leaf_text"] = callout_text
            scenarios_results["05_report_a4_publication"] = rep_dom
            page_rep.close()

            # 6. Course Slide Deck 16:9 Page (BAI_11: buoi-02-thiet-ke-persona-neo-va-thu-dan-y)
            page_sld = browser.new_page(viewport={"width": 1280, "height": 800}, device_scale_factor=1.5)
            page_sld.on("console", lambda msg: console_errors.append(f"[slides] {msg.text}") if msg.type == "error" else None)
            sld_url = f"{base_url}/runs/2026-10-25_noi_dung_khoa_hoc_buoi-02-thiet-ke-persona-neo-va-thu-dan-y/media/slide_deck_sakedemy_16x9.html"
            page_sld.goto(sld_url, wait_until="networkidle")
            shot6 = screens_round_dir / "06-course-slide-deck.png"
            page_sld.screenshot(path=str(shot6), full_page=True)
            screenshots.append(str(shot6))
            sld_dom = audit_page_dom(page_sld)
            slide_h1s = [el.inner_text() for el in page_sld.locator(".slide h1").all()]
            sld_dom["slide_h1s"] = slide_h1s
            scenarios_results["06_course_slide_deck"] = sld_dom
            page_sld.close()

            # 7. LAB043 Onbrand Pixel Report Page (BAI_01)
            page_ob = browser.new_page(viewport={"width": 1280, "height": 900}, device_scale_factor=1.5)
            ob_url = f"{base_url}/runs/2026-10-25_bai_viet_thue-thoi-gian-don-rac-ai/media/onbrand_bao_cao.html"
            page_ob.goto(ob_url, wait_until="networkidle")
            shot7 = screens_round_dir / "07-onbrand-pixel-report.png"
            page_ob.screenshot(path=str(shot7), full_page=True)
            screenshots.append(str(shot7))
            ob_dom = audit_page_dom(page_ob)
            scenarios_results["07_onbrand_pixel_report"] = ob_dom
            page_ob.close()

            page.close()
            browser.close()
    finally:
        httpd.shutdown()

    # Đánh giá Reviewer Khó Tính (Harsh Reviewer Findings & Score)
    score = 9.8

    # Check 1: Broken images (`file:///` blocked over `http://`)
    total_broken_imgs = (
        scenarios_results["01_hub_desktop"]["brokenImgsCount"]
        + scenarios_results["04_bai_viet_publication"]["brokenImgsCount"]
        + scenarios_results["05_report_a4_publication"]["brokenImgsCount"]
        + scenarios_results["06_course_slide_deck"]["brokenImgsCount"]
    )
    if total_broken_imgs > 0:
        score -= 1.2
        findings.append(
            {
                "id": f"REV-R{round_num}-01",
                "severity": "CRITICAL",
                "screen": "04-bai-viet-publication.png, 05-report-a4-publication.png, 06-course-slide-deck.png",
                "issue": f"Phát hiện {total_broken_imgs} ảnh bị vỡ (`naturalWidth == 0`) khi mở qua HTTP server do `media_hoa.py` nhúng đường dẫn tuyệt đối `file:///D:/...` thay vì đường dẫn tương đối (`./...`), bị trình duyệt chặn (`Not allowed to load local resource`).",
                "fix": "Sửa `skills/BM2_M2_media_hoa/media_hoa.py` dùng đường dẫn tương đối (`./agy_anh_goc_sakedemy.jpg`, `./05-xuat/sakedemy_banner_1920x600.png`, `./05-xuat/sakedemy_social_1080x1080.png`) và tái xuất HTML/PDF cho cả 13 bài.",
            }
        )

    # Check 2: Raw Markdown `**...**` & thiếu thẻ `<h2>` trong trang xuất bản
    raw_md_count = (
        scenarios_results["04_bai_viet_publication"]["rawMarkdownBoldCount"]
        + scenarios_results["05_report_a4_publication"]["rawMarkdownBoldCount"]
    )
    if raw_md_count > 0 or scenarios_results["04_bai_viet_publication"]["h2Count"] == 0:
        score -= 0.6
        findings.append(
            {
                "id": f"REV-R{round_num}-02",
                "severity": "HIGH",
                "screen": "04-bai-viet-publication.png, 05-report-a4-publication.png",
                "issue": f"Trang đọc HTML hiển thị nguyên dấu sao Markdown `**...**` ({raw_md_count} vị trí) và bỏ qua toàn bộ tiêu đề mục `##` (`h2Count = {scenarios_results['04_bai_viet_publication']['h2Count']}`).",
                "fix": "Bổ sung bộ chuyển đổi Markdown sang HTML (`<h2>`, `<strong>`, bảng `<table>`) trong `skills/BM2_M2_media_hoa/media_hoa.py` trước khi kết xuất HTML và PDF.",
            }
        )

    # Check 3: Hardcoded Callout / Slide Titles ở các bài mới (BAI_04..BAI_13)
    rep_callout = scenarios_results["05_report_a4_publication"].get("callout_leaf_text", "")
    sld_h1s = scenarios_results["06_course_slide_deck"].get("slide_h1s", [])
    if "88% doanh nghiệp đã dùng AI" in rep_callout or any("Cộng tác phản biện giúp nâng điểm thẩm định từ 31%" in h for h in sld_h1s):
        score -= 0.5
        findings.append(
            {
                "id": f"REV-R{round_num}-03",
                "severity": "HIGH",
                "screen": "05-report-a4-publication.png, 06-course-slide-deck.png",
                "issue": "Hộp `.callout-leaf` của Report `BAI_08` (Shadow AI) và tiêu đề Slide 02/04 của `BAI_11` (Buổi 02) vẫn dùng câu chữ cố định của `BAI_02`/`BAI_03` thay vì trích xuất động từ đề tài và biểu đồ `H01`/`H02` của từng bài.",
                "fix": "Cập nhật `media_hoa.py` để lấy động tiêu đề `exhibits_map[0]['tieu_de']`, `exhibits_map[1]['tieu_de']` và câu mở đầu của từng bài đưa vào `.callout-leaf`, `.photo-caption` và tiêu đề Slide 02/04.",
            }
        )

    # Check 4: Web Hub UI/UX & WCAG checks (Fixed footer overlay, tap target < 32px, missing skip-link / legend bar)
    if (
        scenarios_results["03_hub_mobile"]["fixedFooter"]
        or scenarios_results["01_hub_desktop"]["smallTapTargets"] > 0
        or not scenarios_results["01_hub_desktop"]["hasSkipLink"]
        or not scenarios_results["01_hub_desktop"]["hasLegendBar"]
    ):
        score -= 0.4
        findings.append(
            {
                "id": f"REV-R{round_num}-04",
                "severity": "MEDIUM",
                "screen": "01-hub-desktop-all.png, 03-hub-mobile-390x844.png",
                "issue": (
                    f"Giao diện Web QA Hub có `fixedFooter={scenarios_results['03_hub_mobile']['fixedFooter']}` đè lên nội dung khi chụp full_page, "
                    f"`smallTapTargets={scenarios_results['01_hub_desktop']['smallTapTargets']}` nút bấm nhỏ hơn 32px, "
                    f"`hasSkipLink={scenarios_results['01_hub_desktop']['hasSkipLink']}`, `hasLegendBar={scenarios_results['01_hub_desktop']['hasLegendBar']}`."
                ),
                "fix": "Chuyển `footer.app-footer` sang `position: relative; margin-top: auto;`, tăng kích thước nút `.filter-btn`/`.action-link` lên `min-height: 36px`, bổ sung `.skip-link` WCAG và thanh chú giải `.legend-bar`.",
            }
        )

    score = round(max(0.0, score), 2)

    # Nếu là Round 3 và đạt chuẩn, đồng bộ ảnh ra `reports/screens/`
    if round_num == 3 and len(findings) == 0:
        for s_path in screenshots:
            shutil.copy2(s_path, REPORTS_DIR / "screens" / Path(s_path).name)

    result = {
        "round": round_num,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "reviewer_score": score,
        "pass_all_scenarios": len(findings) == 0 and score >= 9.2,
        "console_errors_count": len(console_errors),
        "console_errors": console_errors[:10],
        "scenarios": scenarios_results,
        "findings": findings,
        "screenshots_count": len(screenshots),
        "screenshots": screenshots,
    }

    # Ghi file JSON audit, Markdown report và Checkpoint
    audit_json_path = REPORTS_DIR / f"round{round_num}-audit.json"
    audit_json_path.parent.mkdir(parents=True, exist_ok=True)
    audit_json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    cp_path = HANDOFF_DIR / "e2e-checkpoint.json"
    cp_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    # Cập nhật e2e-status.json
    next_round = min(3, round_num + 1)
    status_obj = {
        "has_checkpoint": True,
        "last_completed_round": round_num,
        "recommended_next_round": next_round,
        "last_reviewer_score": score,
        "open_findings_count": len(findings),
        "open_findings": findings,
        "ready_for_release": score >= 9.2 and len(findings) == 0 and round_num >= 3,
    }
    (HANDOFF_DIR / "e2e-status.json").write_text(json.dumps(status_obj, ensure_ascii=False, indent=2), encoding="utf-8")

    # Xuất báo cáo Markdown E2E-ROUND-{N}.md
    md_lines = [
        f"# Báo Cáo Kiểm Thử E2E & Đánh Giá Reviewer Khó Tính — Vòng {round_num} (Round {round_num})",
        "",
        f"- **Thời gian**: `{result['timestamp']}`",
        f"- **Điểm số Reviewer Khó Tính**: **{score} / 10.0**",
        f"- **Số ảnh chụp màn hình**: `{len(screenshots)}`",
        f"- **Số lỗi Console trình duyệt**: `{len(console_errors)}`",
        f"- **Số vấn đề phát hiện**: `{len(findings)}`",
        "",
        "## 1. Danh sách ảnh chụp màn hình thực tế (`reports/screens/round" + str(round_num) + "/`)",
    ]
    for s in screenshots:
        md_lines.append(f"- `{Path(s).name}`: `{s}`")

    md_lines.extend(
        [
            "",
            "## 2. Kết quả kiểm toán DOM & Thị giác trên từng kịch bản",
            f"- **01_hub_desktop**: `{scenarios_results['01_hub_desktop']['cardsCount']}` thẻ bài chạy, `maxCardChars = {scenarios_results['01_hub_desktop']['maxCardChars']}` (trần `<= 200`), `brokenImgs = {scenarios_results['01_hub_desktop']['brokenImgsCount']}`, `smallTapTargets = {scenarios_results['01_hub_desktop']['smallTapTargets']}`.",
            f"- **02_hub_filter_report**: Lọc đúng `{scenarios_results['02_hub_filter_report']['report_cards_count']}` bài `report_mau`, mở chi tiết `{scenarios_results['02_hub_filter_report']['selected_title']}`.",
            f"- **03_hub_mobile (390x844)**: `fixedFooter = {scenarios_results['03_hub_mobile']['fixedFooter']}`, `hasSkipLink = {scenarios_results['03_hub_mobile']['hasSkipLink']}`, `hasLegendBar = {scenarios_results['03_hub_mobile']['hasLegendBar']}`.",
            f"- **04_bai_viet_publication (`BAI_04`)**: `brokenImgs = {scenarios_results['04_bai_viet_publication']['brokenImgsCount']}`, `validSvgs = {scenarios_results['04_bai_viet_publication']['validSvgs']}`, `rawMarkdownBoldCount = {scenarios_results['04_bai_viet_publication']['rawMarkdownBoldCount']}`, `h2Count = {scenarios_results['04_bai_viet_publication']['h2Count']}`.",
            f"- **05_report_a4_publication (`BAI_08`)**: `brokenImgs = {scenarios_results['05_report_a4_publication']['brokenImgsCount']}`, `validSvgs = {scenarios_results['05_report_a4_publication']['validSvgs']}`, `rawMarkdownBoldCount = {scenarios_results['05_report_a4_publication']['rawMarkdownBoldCount']}`.",
            f"- **06_course_slide_deck (`BAI_11`)**: `brokenImgs = {scenarios_results['06_course_slide_deck']['brokenImgsCount']}`, `validSvgs = {scenarios_results['06_course_slide_deck']['validSvgs']}`.",
            f"- **07_onbrand_pixel_report (`BAI_01`)**: `brokenImgs = {scenarios_results['07_onbrand_pixel_report']['brokenImgsCount']}`.",
            "",
            "## 3. Danh sách phát hiện & hướng khắc phục cho vòng tiếp theo",
        ]
    )
    if not findings:
        md_lines.append("- **0 lỗi tồn đọng** — Đạt chuẩn xuất xưởng (`>= 9.2 / 10.0`).")
    else:
        for f in findings:
            md_lines.append(
                f"- **[{f['id']}] ({f['severity']}) `{f['screen']}`**: {f['issue']}\n  - *Cách sửa*: {f['fix']}"
            )

    md_path = REPORTS_DIR / f"E2E-ROUND-{round_num}.md"
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(
        f"[E2E ROUND {round_num}] Score: {score}/10.0 | Findings: {len(findings)} | Console Errors: {len(console_errors)} | Screenshots: {len(screenshots)}"
    )
    for f in findings:
        print(f"  - [{f['id']}] ({f['severity']}): {f['issue']}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--round", type=int, required=True, choices=[1, 2, 3])
    args = parser.parse_args()
    run_e2e_round(args.round)
