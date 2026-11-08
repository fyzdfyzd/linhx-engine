"""Module 07: Chi phí, Lợi nhuận, Sổ thu S1a-HKD, Cửa CAC & Báo đỏ 400 triệu gộp cả 3 OPC.

LUẬT AN TOÀN SẮT:
- Luôn chạy bằng code tất định cố định 100% (không dùng LLM).
- Ngưỡng báo đỏ 400.000.000 VNĐ tính gộp chung tài khoản Vân Anh trên toàn bộ các OPC.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import threading
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.event_bus import Event, EventBus  # noqa: E402

RED_ALERT_THRESHOLD_VND = 400_000_000


def evaluate_cac_gate(cac_vnd: int) -> dict:
    if cac_vnd <= 80_000:
        return {"cac_vnd": cac_vnd, "gate": "BAT_SCALE", "action": "Cho phép bật và tăng ngân sách quảng cáo (≤ 40% doanh thu 7 ngày)."}
    if cac_vnd <= 150_000:
        return {"cac_vnd": cac_vnd, "gate": "CHI_RETARGET", "action": "Dừng quảng cáo tệp lạnh; chỉ giữ retarget khách đã vào phễu."}
    return {"cac_vnd": cac_vnd, "gate": "DUNG_QUANG_CAO", "action": "Dừng ngay chiến dịch quảng cáo trả tiền; chuyển sang kênh tự nhiên."}


class FinanceLedgerModule:
    """Bộ ghi sổ doanh thu S1a-HKD & giám sát ngưỡng báo đỏ 400 triệu VNĐ (cố định 100%)."""

    module_id = "07_chi_phi_loi_nhuan"

    def __init__(self, bus: EventBus, data_dir: Path, prior_cumulative_vnd: int = 0):
        self.bus = bus
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.revenue_csv = self.data_dir / "so-doanh-thu.csv"
        self.cost_csv = self.data_dir / "so-chi-phi.csv"
        self.summary_json = self.data_dir / "pnl-summary.json"
        self.prior_cumulative_vnd = int(prior_cumulative_vnd)
        self._lock = threading.Lock()

        if self.prior_cumulative_vnd > 0 and not self.revenue_csv.exists():
            self._write_csv_row(
                ngay="2026-10-24 23:59:59",
                opc_id="SO_DU_DAU_KY_TK_VAN_ANH",
                ma_don="OPENING_BALANCE",
                so_tien=self.prior_cumulative_vnd,
                ma_gd="OPENING_2026",
                noi_dung="Doanh thu luy ke truoc phien thu nghiem tren TK Van Anh",
                luy_ke_gop=self.prior_cumulative_vnd,
                bao_do="AN_TOAN" if self.prior_cumulative_vnd < RED_ALERT_THRESHOLD_VND else "BAO_DO_VUOT_400TR",
            )

        self.bus.subscribe("don.da_tra", self.module_id, self.on_order_paid)
        self.bus.subscribe("report.xong", self.module_id, self.on_report_completed)

    def _read_rows(self) -> list[dict]:
        if not self.revenue_csv.exists():
            return []
        with self.revenue_csv.open("r", encoding="utf-8", newline="") as fp:
            return list(csv.DictReader(fp))

    def _write_csv_row(self, *, ngay: str, opc_id: str, ma_don: str, so_tien: int, ma_gd: str, noi_dung: str, luy_ke_gop: int, bao_do: str) -> None:
        new_file = not self.revenue_csv.exists()
        with self.revenue_csv.open("a", encoding="utf-8", newline="") as fp:
            writer = csv.writer(fp)
            if new_file:
                writer.writerow(["ngay", "opc_id", "ma_don", "so_tien", "ma_gd_ngan_hang", "noi_dung", "luy_ke_gop_vnd", "trang_thai_bao_do_400tr"])
            writer.writerow([ngay, opc_id, ma_don, so_tien, ma_gd, (noi_dung or "").replace('"', ""), luy_ke_gop, bao_do])

    def record_paid_order(self, payload: dict) -> dict:
        order_code = payload["order_code"]
        opc_id = payload.get("opc_id", "opc001_chiemtinh")
        amount = int(payload["amount"])
        paid_at = payload.get("paid_at", "2026-10-25 13:00:00")
        ref_code = payload.get("reference_code", "")
        content = payload.get("tx_content", order_code)

        with self._lock:
            rows = self._read_rows()
            if any(r["ma_don"] == order_code for r in rows):
                cur_total = sum(int(r["so_tien"]) for r in rows)
                return {
                    "action": "duplicate_order_skipped",
                    "order_code": order_code,
                    "cumulative_revenue_vnd": cur_total,
                    "red_alert_400m": cur_total >= RED_ALERT_THRESHOLD_VND,
                }

            prev_total = sum(int(r["so_tien"]) for r in rows)
            new_total = prev_total + amount
            is_red = new_total >= RED_ALERT_THRESHOLD_VND
            status_flag = "BAO_DO_VUOT_400TR" if is_red else "AN_TOAN_DUOI_400TR"

            self._write_csv_row(
                ngay=paid_at,
                opc_id=opc_id,
                ma_don=order_code,
                so_tien=amount,
                ma_gd=ref_code,
                noi_dung=content,
                luy_ke_gop=new_total,
                bao_do=status_flag,
            )

        res = {
            "action": "recorded",
            "opc_id": opc_id,
            "order_code": order_code,
            "amount_vnd": amount,
            "cumulative_revenue_vnd": new_total,
            "red_alert_threshold_vnd": RED_ALERT_THRESHOLD_VND,
            "red_alert_400m": is_red,
            "status_flag": status_flag,
        }
        self.bus.publish("so_cai.da_ghi", opc_id=opc_id, source_module=self.module_id, payload=res)
        if is_red:
            self.bus.publish(
                "canh_bao.doanh_thu_400tr",
                opc_id=opc_id,
                source_module=self.module_id,
                payload={
                    "alert_code": "RED_ALERT_400M_REACHED",
                    "trigger_order": order_code,
                    "trigger_opc": opc_id,
                    "cumulative_revenue_vnd": new_total,
                    "threshold_vnd": RED_ALERT_THRESHOLD_VND,
                    "message": (
                        f"BÁO ĐỎ THUẾ & PHÁP LÝ: Doanh thu luỹ kế gộp trên TK Vân Anh đạt {new_total:,} VNĐ "
                        f"(vượt ngưỡng cảnh báo {RED_ALERT_THRESHOLD_VND:,} VNĐ tại đơn {order_code}). "
                        f"Cần kiểm tra ngay nghĩa vụ thuế HKD và phản hồi của kế toán Hoa!"
                    ),
                },
            )
        self.save_summary()
        return res

    def record_ai_cost(self, opc_id: str, order_code: str, ai_cost_vnd: int, input_tokens: int = 0, output_tokens: int = 0) -> None:
        with self._lock:
            new_file = not self.cost_csv.exists()
            with self.cost_csv.open("a", encoding="utf-8", newline="") as fp:
                writer = csv.writer(fp)
                if new_file:
                    writer.writerow(["opc_id", "ma_don", "loai_chi_phi", "input_tokens", "output_tokens", "so_tien_vnd"])
                writer.writerow([opc_id, order_code, "AI_API_TOKEN", input_tokens, output_tokens, int(ai_cost_vnd)])
        self.save_summary()

    def get_summary(self, current_cac_vnd: int = 75_000) -> dict:
        with self._lock:
            rev_rows = self._read_rows()
            cost_rows = []
            if self.cost_csv.exists():
                with self.cost_csv.open("r", encoding="utf-8", newline="") as fp:
                    cost_rows = list(csv.DictReader(fp))

        total_cum_rev = sum(int(r["so_tien"]) for r in rev_rows)
        session_orders = [r for r in rev_rows if r["ma_don"] != "OPENING_BALANCE"]
        session_rev = sum(int(r["so_tien"]) for r in session_orders)
        total_ai_cost = sum(int(r["so_tien_vnd"]) for r in cost_rows)

        by_opc: dict[str, dict] = {}
        for r in session_orders:
            oid = r["opc_id"]
            b = by_opc.setdefault(oid, {"orders_paid": 0, "revenue_vnd": 0, "ai_cost_vnd": 0})
            b["orders_paid"] += 1
            b["revenue_vnd"] += int(r["so_tien"])
        for c in cost_rows:
            oid = c["opc_id"]
            b = by_opc.setdefault(oid, {"orders_paid": 0, "revenue_vnd": 0, "ai_cost_vnd": 0})
            b["ai_cost_vnd"] += int(c["so_tien_vnd"])

        red_rows = [r for r in rev_rows if r["trang_thai_bao_do_400tr"] == "BAO_DO_VUOT_400TR"]
        return {
            "shared_account_pool": "VAN_ANH_HKD",
            "prior_opening_balance_vnd": self.prior_cumulative_vnd,
            "session_orders_paid_count": len(session_orders),
            "session_revenue_vnd": session_rev,
            "cumulative_revenue_vnd": total_cum_rev,
            "red_alert_threshold_vnd": RED_ALERT_THRESHOLD_VND,
            "red_alert_400m": total_cum_rev >= RED_ALERT_THRESHOLD_VND,
            "red_alert_first_triggered_by": red_rows[0]["ma_don"] if red_rows else None,
            "total_ai_cost_vnd": total_ai_cost,
            "ai_cost_to_session_revenue_pct": round((total_ai_cost / session_rev) * 100, 4) if session_rev > 0 else 0.0,
            "max_ad_budget_7d_40pct_vnd": int(session_rev * 0.40),
            "cac_gate_evaluation": evaluate_cac_gate(current_cac_vnd),
            "by_opc": by_opc,
            "ledger_csv_path": str(self.revenue_csv),
            "cost_csv_path": str(self.cost_csv),
        }

    def save_summary(self, current_cac_vnd: int = 75_000) -> dict:
        summary = self.get_summary(current_cac_vnd=current_cac_vnd)
        self.summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        return summary

    def on_order_paid(self, event: Event) -> dict:
        return self.record_paid_order(event.payload)

    def on_report_completed(self, event: Event) -> dict:
        p = event.payload
        m = p.get("metrics", {})
        self.record_ai_cost(
            opc_id=p.get("opc_id", event.opc_id),
            order_code=p.get("order_code", ""),
            ai_cost_vnd=int(m.get("ai_cost_vnd", 0)),
            input_tokens=int(m.get("input_tokens", 0)),
            output_tokens=int(m.get("output_tokens", 0)),
        )
        return {"recorded_cost_for": p.get("order_code")}


def main() -> int:
    ap = argparse.ArgumentParser(description="Module 07: Chi phí, Lợi nhuận & Báo đỏ 400 triệu")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()

    in_path = HERE / "demo" / "input" / "demo_in.json"
    out_path = HERE / "demo" / "output" / "demo_out.json"
    data = json.loads(in_path.read_text(encoding="utf-8"))

    demo_data_dir = HERE / "demo" / "output" / "data"
    if demo_data_dir.exists():
        for f in demo_data_dir.glob("*"):
            f.unlink()

    bus = EventBus()
    mod = FinanceLedgerModule(bus, demo_data_dir, prior_cumulative_vnd=int(data.get("prior_cumulative_revenue_vnd", 0)))
    for tx in data.get("transactions", []):
        mod.record_paid_order(tx)
        mod.record_ai_cost(tx["opc_id"], tx["order_code"], int(tx.get("ai_cost_vnd", 25)), 650, 320)

    summary = mod.save_summary(current_cac_vnd=int(data.get("current_cac_vnd", 72000)))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"[Module 07] Xong Sổ cái | Luỹ kế gộp={summary['cumulative_revenue_vnd']:,}đ "
        f"| Báo đỏ 400tr={summary['red_alert_400m']} (tại đơn {summary['red_alert_first_triggered_by']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
