#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Đo lường tự động E2E + 10 mục Thẩm mỹ & Tối giản theo Mục 13 (11_LO_TRINH_VAN_HANH_THAT.md)."""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.build_web_hub import build_web_hub

VONG_DIR = ROOT_DIR / "VONG"
ANH_ROOT = ROOT_DIR / "BAO_CAO" / "anh_cong_a"
UTF8_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}


def _wait_server(port: int, timeout_s: float = 12.0) -> bool:
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/healthz", timeout=2.0) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(0.25)
    return False


JS_AUDIT_DOM = """
() => {
  const isVisible = (el) => {
    if (!el) return false;
    const style = window.getComputedStyle(el);
    if (style.display === 'none' || style.visibility === 'hidden' || parseFloat(style.opacity) === 0) return false;
    const detailsParent = el.closest('details');
    if (detailsParent && !detailsParent.open && el.tagName.toLowerCase() !== 'summary') {
      if (!detailsParent.querySelector('summary')?.contains(el)) return false;
    }
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };

  const clickables = Array.from(document.querySelectorAll('button, a[href], select, textarea, input, summary'))
    .filter(isVisible);

  const primaryButtons = Array.from(document.querySelectorAll('.primary-btn, .pub-btn.primary'))
    .filter(isVisible);

  const smallTargets = [];
  for (const el of clickables) {
    const r = el.getBoundingClientRect();
    if (Math.round(r.height) < 44 || Math.round(r.width) < 44) {
      smallTargets.push({
        tag: el.tagName.toLowerCase(),
        id: el.id || '',
        cls: el.className || '',
        text: (el.innerText || el.value || '').trim().slice(0, 40),
        w: Math.round(r.width),
        h: Math.round(r.height)
      });
    }
  }

  const smallFonts = [];
  const allEls = Array.from(document.querySelectorAll('body *')).filter(isVisible);
  for (const el of allEls) {
    const directText = Array.from(el.childNodes)
      .filter(n => n.nodeType === Node.TEXT_NODE)
      .map(n => n.textContent.trim())
      .join(' ');
    if (!directText) continue;
    const fs = parseFloat(window.getComputedStyle(el).fontSize);
    if (fs < 13.9) {
      smallFonts.push({
        tag: el.tagName.toLowerCase(),
        cls: el.className || '',
        fontSize: fs,
        text: directText.slice(0, 45)
      });
    }
  }

  const overflowPx = Math.max(0, document.documentElement.scrollWidth - document.documentElement.clientWidth);
  return {
    clickableCount: clickables.length,
    primaryButtonCount: primaryButtons.length,
    smallTargetCount: smallTargets.length,
    smallTargetsSample: smallTargets.slice(0, 10),
    smallFontCount: smallFonts.length,
    smallFontsSample: smallFonts.slice(0, 10),
    overflowPx: overflowPx,
    visibleText: document.body.innerText
  };
}
"""


def find_jargon_leaks(text: str) -> list:
    leaks = []
    tokens = [
        "01_MAY_TAO_NOI_DUNG",
        "LAB043",
        "LAB049",
        "LAB028",
        "LAB017",
        "LAB027",
        "AGY image-generator",
        "Onbrand CLI",
        "Max 4-gram",
        "CQS",
        "APS",
        "VD 100/100",
    ]
    for tok in tokens:
        if tok in text:
            leaks.append(tok)
    for m in re.findall(r"[\[\(](?:N|BC|KH|BM|I)\d+[\]\)]", text):
        if m not in leaks:
            leaks.append(m)
    return leaks


def run_vong(vong: int, port: int = 8011, de_bai: str = "") -> dict:
    from playwright.sync_api import sync_playwright

    VONG_DIR.mkdir(parents=True, exist_ok=True)
    vong_anh_dir = ANH_ROOT / f"vong_{vong}"
    vong_anh_dir.mkdir(parents=True, exist_ok=True)
    for old_f in vong_anh_dir.glob("*.png"):
        old_f.unlink()

    build_web_hub()

    srv = subprocess.Popen(
        [sys.executable, str(ROOT_DIR / "server_web.py"), "--port", str(port)],
        cwd=str(ROOT_DIR),
        env=UTF8_ENV,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    t0 = time.perf_counter()
    try:
        if not _wait_server(port):
            raise RuntimeError("Không thể khởi động server_web.py")

        if not de_bai:
            de_bai = (
                "Thiết kế quy trình kiểm soát chất lượng báo cáo tuần bằng trí tuệ nhân tạo "
                "cho đội ngũ vận hành hai mươi lăm nhân sự tại doanh nghiệp bán lẻ Việt Nam"
            )

        viewports = [("1440px", 1440, 900), ("390px", 390, 844)]
        vp_results = {}
        all_console_errors = []
        all_jargon = []

        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(channel="msedge", headless=True)
            except Exception:
                browser = p.chromium.launch(channel="chrome", headless=True)

            for vp_label, w, h in viewports:
                context = browser.new_context(viewport={"width": w, "height": h})
                page = context.new_page()
                errs = []
                page.on("console", lambda m, e=errs: e.append(m.text) if m.type == "error" else None)
                page.on("pageerror", lambda exc, e=errs: e.append(str(exc)))

                # Màn hình 1: Mở trang chính & nhập đề bài
                page.goto(f"http://127.0.0.1:{port}/web/index.html", wait_until="networkidle")
                audit_initial = page.evaluate(JS_AUDIT_DOM)

                page.select_option("#select-loai", "bai_viet")
                page.fill("#input-de-bai", de_bai)
                s1 = vong_anh_dir / f"01_{vp_label}_man_chinh_dan_de.png"
                page.screenshot(path=str(s1), full_page=False)

                # Màn hình 2: Bấm lập 3 phương án dàn ý (Cú bấm 1)
                page.click("#btn-tao-dan-y")
                page.wait_for_selector("#khu-vuc-3-dan-y", state="visible", timeout=45000)
                page.wait_for_selector("#btn-chon-B", state="visible", timeout=15000)
                page.locator("#khu-vuc-3-dan-y").scroll_into_view_if_needed()
                audit_outlines = page.evaluate(JS_AUDIT_DOM)
                s2 = vong_anh_dir / f"02_{vp_label}_xem_3_dan_y.png"
                page.screenshot(path=str(s2), full_page=False)

                # Màn hình 3: Bấm chọn 1 phương án dàn ý (Cú bấm 2)
                page.click("#btn-chon-B")
                page.wait_for_selector("#ket-qua-xuat-ban", state="visible", timeout=90000)
                page.locator("#ket-qua-xuat-ban").scroll_into_view_if_needed()
                audit_result = page.evaluate(JS_AUDIT_DOM)
                s3 = vong_anh_dir / f"03_{vp_label}_nhan_bai_va_pdf_anh.png"
                page.screenshot(path=str(s3), full_page=False)

                reader_href = page.get_attribute("#link-mo-trang-doc", "href")
                target_reader_url = urllib.parse.urljoin(f"http://127.0.0.1:{port}/web/index.html", reader_href)
                page.goto(target_reader_url, wait_until="networkidle")
                audit_reader = page.evaluate(JS_AUDIT_DOM)
                s4 = vong_anh_dir / f"04_{vp_label}_trang_doc_tap_chi_html.png"
                page.screenshot(path=str(s4), full_page=False)

                leaks = list(
                    set(
                        find_jargon_leaks(audit_initial["visibleText"])
                        + find_jargon_leaks(audit_outlines["visibleText"])
                        + find_jargon_leaks(audit_result["visibleText"])
                        + find_jargon_leaks(audit_reader["visibleText"])
                    )
                )
                all_jargon.extend(leaks)
                all_console_errors.extend(errs)

                vp_results[vp_label] = {
                    "initial": {k: v for k, v in audit_initial.items() if k != "visibleText"},
                    "outlines": {k: v for k, v in audit_outlines.items() if k != "visibleText"},
                    "result": {k: v for k, v in audit_result.items() if k != "visibleText"},
                    "reader": {k: v for k, v in audit_reader.items() if k != "visibleText"},
                    "jargon_leaks": leaks,
                    "console_errors": errs,
                    "screenshots": [s1.name, s2.name, s3.name, s4.name],
                }

                # Nếu là vòng 3, đồng bộ ảnh sang BAO_CAO/anh_cong_a/ gốc
                if vong == 3:
                    for src_shot in (s1, s2, s3, s4):
                        shutil.copy2(src_shot, ANH_ROOT / src_shot.name)

                context.close()
            browser.close()

        summary = {
            "vong": vong,
            "thoi_diem": datetime.now().isoformat(timespec="seconds"),
            "thoi_gian_chay_giay": round(time.perf_counter() - t0, 2),
            "so_phan_tu_bam_duoc_man_chinh_1440": vp_results["1440px"]["initial"]["clickableCount"],
            "so_nut_chinh_man_chinh_1440": vp_results["1440px"]["initial"]["primaryButtonCount"],
            "so_cu_bam_cho_viec_chinh": 2,
            "so_chu_nho_hon_14px_1440": vp_results["1440px"]["initial"]["smallFontCount"]
            + vp_results["1440px"]["outlines"]["smallFontCount"],
            "so_cho_bam_nho_hon_44px_1440": vp_results["1440px"]["initial"]["smallTargetCount"],
            "so_cho_bam_nho_hon_44px_390": vp_results["390px"]["initial"]["smallTargetCount"],
            "tran_ngang_1440px": vp_results["1440px"]["initial"]["overflowPx"],
            "tran_ngang_390px": vp_results["390px"]["initial"]["overflowPx"],
            "so_loi_console": len(all_console_errors),
            "chu_ky_thuat_lo_ra": sorted(list(set(all_jargon))),
            "chi_tiet_viewport": vp_results,
        }
        out_file = VONG_DIR / f"vong_{vong}_metrics.json"
        out_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({k: v for k, v in summary.items() if k != "chi_tiet_viewport"}, ensure_ascii=False, indent=2))
        return summary
    finally:
        srv.terminate()
        try:
            srv.wait(timeout=5)
        except Exception:
            srv.kill()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--vong", type=int, required=True)
    ap.add_argument("--de-bai", type=str, default="")
    args = ap.parse_args()
    run_vong(args.vong, de_bai=args.de_bai)
