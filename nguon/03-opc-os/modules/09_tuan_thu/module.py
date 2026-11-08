"""Module 09: Tuân thủ pháp lý, Cổng chặn Go-Live, 3 Trang pháp lý nháp & Bảo vệ dữ liệu NĐ 13/2023.

Nâng cấp Bậc 1 MVP nội bộ (Cổng A):
- Quét toàn bộ văn bản báo cáo (hoặc file HTML báo cáo) thay vì chỉ quét 3 câu mở đầu.
- Bổ sung bộ từ cấm đạo đức ngành tâm linh và lỗi xưng hô trẻ em (`DEFAULT_ETHICAL_BANNED_PHRASES`).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.opc_loader import load_opc_config  # noqa: E402

LEGAL_DIR = HERE / "van_ban_phap_ly"

DEFAULT_ETHICAL_BANNED_PHRASES = [
    "mất mẹ từ sớm",
    "mất mẹ",
    "mất cha",
    "đoản mệnh",
    "tự tử",
    "rượu, ma túy",
    "ma túy",
    "bị trầm cảm",
    "rơi vào trầm cảm",
    "trầm cảm nhẹ",
    "nhóc nhà mình",
    "nhóc nhà ta",
    "vào một nhà trẻ",
    "hư uhỏng",
    "muôn thoát lý",
]


def check_compliance(payload: dict) -> dict:
    opc_id = payload.get("opc_id", "opc001_chiemtinh")
    cfg = load_opc_config(opc_id)
    comp = cfg.get("compliance", {})
    raw_text = str(payload.get("sample_text") or "")

    html_path_str = payload.get("report_html_path")
    if html_path_str and Path(html_path_str).exists():
        html_raw = Path(html_path_str).read_text(encoding="utf-8", errors="ignore")
        plain_from_html = re.sub(r"<[^>]+>", " ", html_raw)
        raw_text = f"{raw_text}\n{plain_from_html}"

    text = raw_text.lower()
    consent = bool(payload.get("consent_checked", True))

    all_banned_phrases = list(dict.fromkeys(list(comp.get("banned_phrases", [])) + DEFAULT_ETHICAL_BANNED_PHRASES))
    banned = [b for b in all_banned_phrases if b.lower() in text]
    disclaimer = comp.get("disclaimer", "")
    has_disclaimer_keywords = any(
        k in text
        for k in ["giải trí", "tự khám phá", "tham khảo", "không đưa dữ liệu khách hàng thật", "gợi ý"]
    )

    legal_files = sorted(str(p.relative_to(ROOT)) for p in LEGAL_DIR.glob("*.md"))
    human_gates_before_live = [
        {"id": "HKD_VAN_ANH_MST", "task": "Vân Anh đăng ký hộ kinh doanh và có MST (hạn 15/11/2026)", "status": "PENDING_HUMAN"},
        {"id": "ONLINE_GOV_VN", "task": "Thông báo website TMĐT trên online.gov.vn", "status": "PENDING_HUMAN"},
        {"id": "LAWYER_REVIEW", "task": "Luật sư rà 3 trang pháp lý nháp và nội dung ngành tâm linh / vị thành niên", "status": "DRAFT_READY_FOR_LAWYER"},
        {"id": "TAX_HOA_CONFIRM", "task": "Kế toán Hoa trả lời ngưỡng thuế (500 triệu hay 1 tỷ) — đang giữ báo đỏ ở 400 triệu", "status": "RED_ALERT_SET_AT_400M"},
        {"id": "LINH_REVIEW_20", "task": "Anh Linh duyệt tay 20 report đầu tiên trước khi mở tự động gửi khách", "status": "ENFORCED_IN_MODULE_01"},
    ]

    return {
        "opc_id": cfg["opc_id"],
        "sector": comp.get("sector", ""),
        "consent_verified": consent,
        "scanned_chars_count": len(raw_text),
        "banned_hits": banned,
        "has_disclaimer_spirit": has_disclaimer_keywords,
        "required_disclaimer": disclaimer,
        "content_compliance_passed": consent and len(banned) == 0 and has_disclaimer_keywords,
        "legal_pages": legal_files,
        "live_money_readiness": {
            "allow_real_money_now": False,
            "reason": "Chưa nhận tiền thật ở Bậc 1 MVP nội bộ; chờ hoàn tất 5 việc người (HKD Vân Anh + MST trước 15/11, luật sư rà 3 trang pháp lý).",
            "human_checklist": human_gates_before_live,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Module 09: Tuân thủ pháp lý")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()

    in_path = HERE / "demo" / "input" / "demo_in.json"
    out_path = HERE / "demo" / "output" / "demo_out.json"
    res = check_compliance(json.loads(in_path.read_text(encoding="utf-8")))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Module 09] Xong Tuân thủ {res['opc_id']} | Passed={res['content_compliance_passed']} | LegalPages={len(res['legal_pages'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
