"""Kịch bản đo tự động 10 tiêu chí Thẩm mỹ & Tối giản (Mục 13 `11_LO_TRINH_VAN_HANH_THAT.md`) cho từng vòng của `03_OPC_OS`."""
from __future__ import annotations

import json
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.opc_loader import list_all_opcs  # noqa: E402


def wait_port(port: int = 8300, timeout_s: float = 10.0) -> bool:
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def measure_round(round_num: int, capture_screens: bool = False) -> dict:
    _ = list_all_opcs()
    v_dir = ROOT / "BAO_CAO" / "anh_cong_a" / f"vong_{round_num}"
    v_dir.mkdir(parents=True, exist_ok=True)

    if not capture_screens:
        for png in (ROOT / "BAO_CAO" / "anh_cong_a").glob("*.png"):
            shutil.copy2(png, v_dir / png.name)

    proc = subprocess.Popen(
        [sys.executable, str(ROOT / "server_ui.py")],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if not wait_port(8300):
        proc.kill()
        raise RuntimeError("Không khởi động được server_ui.py")

    try:
        from report_core.render import _get_browser

        b = _get_browser()
        ctx = b.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()

        urls = [
            ("dashboard", "http://127.0.0.1:8300/"),
            ("store_opc1", "http://127.0.0.1:8300/store/opc001_chiemtinh"),
            ("store_opc2", "http://127.0.0.1:8300/store/opc002_bank_prompt_kit"),
            ("store_opc3", "http://127.0.0.1:8300/store/opc003_huong_nghiep_hs"),
            ("ab_page", "http://127.0.0.1:8300/ab"),
            ("privacy_page", "http://127.0.0.1:8300/privacy"),
            ("status_page", "http://127.0.0.1:8300/tinh-trang"),
        ]
        results = {}
        for key, url in urls:
            page.goto(url, wait_until="load")
            stats = page.evaluate(
                """() => {
                const isVis = (el) => {
                    if (!el.offsetParent && getComputedStyle(el).position !== 'fixed') return false;
                    const details = el.closest('details');
                    if (details && !details.open && el.tagName.toLowerCase() !== 'summary') return false;
                    const r = el.getBoundingClientRect();
                    return r.width > 0 && r.height > 0;
                };
                const clickables = Array.from(document.querySelectorAll('a, button, input:not([type=hidden]), select, textarea, summary')).filter(isVis);
                const smallTargets = clickables.filter(el => {
                    const target = (el.tagName === 'INPUT' && (el.type === 'radio' || el.type === 'checkbox') && el.closest('label')) ? el.closest('label') : el;
                    const r = target.getBoundingClientRect();
                    return r.height < 43.5 || r.width < 43.5;
                });
                const leafEls = Array.from(document.querySelectorAll('body *')).filter(el => isVis(el) && el.children.length === 0 && (el.innerText || '').trim().length > 0);
                const smallFonts = leafEls.filter(el => parseFloat(getComputedStyle(el).fontSize) < 13.9);
                const primaryBtns = Array.from(document.querySelectorAll('.btn, .btn-primary, a[style*="#2563eb"], a[style*="#1d4ed8"], button[style*="#2563eb"]')).filter(isVis);
                const detailsCount = document.querySelectorAll('details').length;
                const hasEmptyState = !!document.querySelector('[data-state="empty"], .empty-state');
                const hasLoadingState = !!document.querySelector('[data-state="loading"], #loading-overlay');
                return {
                    visible_clickables: clickables.length,
                    small_targets_under_44px: smallTargets.length,
                    small_fonts_under_14px: smallFonts.length,
                    primary_styled_buttons: primaryBtns.length,
                    details_collapsible_blocks: detailsCount,
                    has_empty_state_hook: hasEmptyState,
                    has_loading_state_hook: hasLoadingState
                };
            }"""
            )
            results[key] = stats
        ctx.close()
        return results
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    rn = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    out = measure_round(rn)
    (ROOT / "BAO_CAO" / f"do_tham_my_vong_{rn}.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(out, ensure_ascii=False, indent=2))
