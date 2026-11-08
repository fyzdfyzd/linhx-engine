"""Module 02: Thiết kế gói giá, combo, quà theo dịp & kiểm cửa kinh tế đơn vị (`02_thiet_ke_goi_gia`)."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.event_bus import Event, EventBus  # noqa: E402
from core.opc_loader import load_opc_config  # noqa: E402


def evaluate_pricing(payload: dict) -> dict:
    opc_id = payload.get("opc_id", "opc001_chiemtinh")
    cfg = load_opc_config(opc_id)
    pricing = cfg.get("pricing", {})
    tier_id = payload.get("tier_id", "")
    coupon_code = (payload.get("coupon_code") or "").strip().upper()
    check_dt = date.fromisoformat(payload.get("check_date") or "2026-10-25")

    tiers = {t["id"]: t for t in pricing.get("tiers", [])}
    tier = tiers.get(tier_id) or {
        "id": tier_id or "default",
        "name": cfg.get("name", ""),
        "price": int(pricing.get("default_price", 199000)),
    }
    base_price = int(tier["price"])
    discount_pct = 0
    applied_coupon = None

    if coupon_code:
        for c in pricing.get("coupons", []):
            if c["code"].upper() == coupon_code:
                exp = date.fromisoformat(c["expires"])
                if check_dt <= exp:
                    discount_pct = int(c.get("discount_percent", 0))
                    applied_coupon = c
                break

    discount_amount = int(round(base_price * discount_pct / 100.0, -3)) if base_price > 0 else 0
    final_price = max(0, base_price - discount_amount)
    est_cogs = 12000 if final_price > 0 else 0
    gross_margin_pct = round(((final_price - est_cogs) / final_price) * 100, 1) if final_price > 0 else 100.0
    max_ad_cac_40pct = int(final_price * 0.40)
    gate_passed = (final_price == 0) or (final_price >= 150000 and gross_margin_pct >= 85.0)

    return {
        "opc_id": opc_id,
        "tier_id": tier["id"],
        "tier_name": tier["name"],
        "base_price": base_price,
        "coupon_applied": applied_coupon["code"] if applied_coupon else None,
        "occasion": applied_coupon.get("occasion") if applied_coupon else None,
        "discount_amount": discount_amount,
        "final_price": final_price,
        "estimated_cogs_vnd": est_cogs,
        "gross_margin_percent": gross_margin_pct,
        "max_ad_cac_allowed_40pct": max_ad_cac_40pct,
        "unit_economics_gate_passed": gate_passed,
        "agent_policy_note": "Agent không được tự đổi giá hoặc tạo mã giảm mới khi chưa có Founder duyệt (QUY-CHUAN 6.2).",
    }


class PricingModule:
    module_id = "02_thiet_ke_goi_gia"

    def __init__(self, bus: EventBus):
        self.bus = bus
        self.bus.subscribe("gia.yeu_cau_tinh", self.module_id, self.on_price_request)

    def on_price_request(self, event: Event) -> dict:
        res = evaluate_pricing(event.payload)
        self.bus.publish("gia.da_tinh", opc_id=res["opc_id"], source_module=self.module_id, payload=res)
        return res


def main() -> int:
    ap = argparse.ArgumentParser(description="Module 02: Thiết kế gói giá")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--input", type=Path)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    in_path = args.input or (HERE / "demo" / "input" / "demo_in.json")
    out_path = args.output or (HERE / "demo" / "output" / "demo_out.json")
    res = evaluate_pricing(json.loads(in_path.read_text(encoding="utf-8")))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Module 02] Xong {res['tier_id']} -> Giá cuối={res['final_price']:,}đ | Gate={res['unit_economics_gate_passed']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
