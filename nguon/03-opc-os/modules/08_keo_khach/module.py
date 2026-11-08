"""Module 08: Kéo khách, gắn UTM/Pixel, đo phễu 5 bước, nối `kiemTraCuaPaidCFO` (Đề 07) & phát `quet.yeu_cau` (Đề 08)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.event_bus import EventBus  # noqa: E402
from core.opc_loader import load_opc_config  # noqa: E402


def evaluate_acquisition_funnel(payload: dict, bus: EventBus | None = None) -> dict:
    opc_id = payload.get("opc_id", "opc001_chiemtinh")
    cfg = load_opc_config(opc_id)
    canonical_opc_id = cfg["opc_id"]
    f = payload.get("funnel_data", {})
    spend = int(payload.get("smoke_test_spend_7d_vnd", 840_000))
    max_smoke = int(cfg.get("thresholds", {}).get("smoke_test_budget_7d_vnd", 1_000_000))
    default_price = int(cfg.get("pricing", {}).get("default_price", 199_000))

    views = max(1, int(f.get("landing_views", 1)))
    free_views = max(1, int(f.get("free_preview_views", 1)))
    submits = int(f.get("form_submits", 0))
    qr_shown = int(f.get("qr_shown", 0))
    paid = int(f.get("paid_orders", 0))
    delivered = int(f.get("pdf_delivered", 0))
    revenue_7d = paid * default_price

    cac_vnd = int(round(spend / paid)) if paid > 0 else spend
    gates = cfg.get("thresholds", {}).get("cac_gates", {"scale_max_vnd": 80000, "retarget_max_vnd": 150000})

    # Gọi cổng kiểm kinh tế Paid CFO dùng chung từ 07_CHANNEL_OS qua _DUNG_CHUNG/channel_os_adapter.py (_KIEN_THUC/GIAO_KEO.md)
    cfo_gate_detail = {}
    try:
        from channel_os_adapter import kiemTraCuaPaidCFO

        cfo_gate_detail = kiemTraCuaPaidCFO(
            chi_quang_cao_7d_vnd=spend,
            doanh_thu_7d_vnd=revenue_7d,
            so_don_7d=paid,
            la_thu_khoi=True,
        )
        decision = cfo_gate_detail.get("quyet_dinh") or "BAT_SCALE (CAC <= 80k)"
    except Exception:
        if cac_vnd <= int(gates.get("scale_max_vnd", 80000)):
            decision = "BAT_SCALE (CAC <= 80k)"
        elif cac_vnd <= int(gates.get("retarget_max_vnd", 150000)):
            decision = "CHI_RETARGET (80k < CAC <= 150k)"
        else:
            decision = "DUNG_QUANG_CAO (CAC > 150k)"

    # Phát sự kiện chuẩn quet.yeu_cau sang 08_CRAWLER_OS để lấy chủ đề/câu hỏi khách hàng (_KIEN_THUC/GIAO_KEO.md)
    crawler_request = {
        "event_type": "quet.yeu_cau",
        "source_os": "03_OPC_OS",
        "target_os": "08_CRAWLER_OS",
        "opc_id": canonical_opc_id,
        "domain": cfg.get("domain", ""),
        "query_focus": f"Câu hỏi thường gặp và nhu cầu thực tế của khách hàng mảng {cfg.get('name', canonical_opc_id)}",
    }
    if bus is not None:
        bus.publish("quet.yeu_cau", opc_id=canonical_opc_id, source_module="08_keo_khach", payload=crawler_request)

    return {
        "opc_id": canonical_opc_id,
        "utm_tracking": {
            "utm_source": "tiktok",
            "utm_medium": "short_video_organic_and_spark",
            "utm_campaign": payload.get("utm_campaign", f"smoke_{canonical_opc_id}"),
        },
        "funnel_counts": {
            "1_landing_views": views,
            "2_form_submits": submits,
            "3_qr_shown": qr_shown,
            "4_paid_orders": paid,
            "5_pdf_delivered": delivered,
        },
        "conversion_rates": {
            "form_per_view_pct": round((submits / views) * 100, 2),
            "paid_per_free_preview_pct": round((paid / free_views) * 100, 2),
            "paid_per_qr_pct": round((paid / max(1, qr_shown)) * 100, 2),
            "delivery_success_pct": round((delivered / max(1, paid)) * 100, 2),
        },
        "smoke_test_spend_7d_vnd": spend,
        "smoke_test_max_budget_7d_vnd": max_smoke,
        "smoke_test_budget_ok": spend <= max_smoke,
        "cac_vnd": cac_vnd,
        "cac_gate_decision": decision,
        "channel_os_cfo_gate": cfo_gate_detail,
        "crawler_os_event": crawler_request,
        "agent_policy_note": "Hệ thống chỉ đọc số liệu và đề xuất; mọi khoản chi quảng cáo đều phải do người phụ trách duyệt (QUY-CHUAN 6.2).",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Module 08: Kéo khách & Đo phễu")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()

    in_path = HERE / "demo" / "input" / "demo_in.json"
    out_path = HERE / "demo" / "output" / "demo_out.json"
    res = evaluate_acquisition_funnel(json.loads(in_path.read_text(encoding="utf-8")))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Module 08] Xong Phễu {res['opc_id']} | CAC={res['cac_vnd']:,}đ | Gate={res['cac_gate_decision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
