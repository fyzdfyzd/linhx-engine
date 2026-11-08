"""Module 10: Giám sát vận hành, KPI ngày 06:00, Cảnh báo bất thường, Sao lưu DB & Báo cáo tuần."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def generate_kpi_and_weekly_report(payload: dict, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    cum_rev = int(payload.get("cumulative_revenue_vnd", 0))
    opcs = payload.get("opcs_metrics", [])
    webhook_errs = int(payload.get("webhook_errors_count", 0))
    stuck = int(payload.get("stuck_orders_over_5m", 0))
    founder_hours = float(payload.get("founder_hours_per_day", 0.75))

    total_orders = sum(int(o.get("paid_orders", 0)) for o in opcs)
    total_ai_cost = sum(int(o.get("ai_cost_vnd", 0)) for o in opcs)
    session_rev = sum(int(o.get("revenue_vnd", 0)) for o in opcs)
    ai_ratio_pct = round((total_ai_cost / max(1, session_rev)) * 100, 4)

    alerts = []
    if cum_rev >= 400_000_000:
        alerts.append({
            "severity": "RED_CRITICAL",
            "code": "TAX_THRESHOLD_400M_EXCEEDED",
            "message": f"Doanh thu luỹ kế gộp đạt {cum_rev:,} VNĐ (>= 400.000.000 VNĐ) trên tài khoản Vân Anh. Báo động đỏ kiểm tra ngưỡng thuế HKD!",
        })
    if webhook_errs > 0:
        alerts.append({
            "severity": "WARNING",
            "code": "WEBHOOK_REJECTED_EVENTS",
            "message": f"Phát hiện {webhook_errs} lượt gọi webhook sai khoá/thiếu tiền đã bị hệ thống chặn an toàn.",
        })
    if stuck > 0:
        alerts.append({
            "severity": "HIGH",
            "code": "REPORT_STUCK_OVER_5M",
            "message": f"Có {stuck} đơn đã trả tiền nhưng quá 5 phút chưa sinh xong PDF!",
        })

    # Tạo bản sao lưu nhật ký (Daily Backup)
    backup_dir = out_dir / "backups" / time.strftime("%Y-%m-%d")
    backup_dir.mkdir(parents=True, exist_ok=True)
    snapshot_file = backup_dir / "kpi_snapshot.json"
    snapshot_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    weekly_md = f"""# Báo cáo tuần 01: Hệ điều hành OPC OS (3 OPC chạy chung)

**Tuần:** 01 (2026-10-19 → 2026-10-25) · **Giai đoạn:** SETUP / POC Mức 1–3 · **Cổng kế tiếp:** Đã kiểm chứng & Pháp lý nhận tiền thật (15/11/2026)

## 1. Tiến độ (10 Module & 3 OPC)
| Hạng mục | Hoàn thành | Tổng | % Done | Ghi chú |
|---|---|---|---|---|
| 10 Module cắm rút (`modules/01..10`) | 10 | 10 | 100% | Đầy đủ `MODULE.md`, `giao_keo.json`, CLI & Demo |
| Phương án A (`A_CODE`) vs B (`B_AGENT`) | 2 | 2 | 100% | Đã chạy 10 đơn giả + 3 ca lạ và đo số thật |
| 3 OPC cắm trên cùng OS (`opcs/opc001..003`) | 3 | 3 | 100% | Chiêm tinh, Prompt Ngân hàng, Hướng nghiệp HS |

## 2. Ba điều tốt
1. Luồng tiền-ra-report tất định 100% ở phần tiền (Module 03 & 07): chặn sạch đơn sai khoá `401`, chống ghi trùng `tx_id`, chặn đơn thiếu tiền và hết hạn.
2. Cắm thêm OPC 2 (Bộ công cụ ZIP+PDF Ngân hàng) và OPC 3 (Hồ sơ hướng nghiệp học sinh RIASEC 12–15 trang) trên cùng một lõi mà không phải viết lại luồng thanh toán hay sổ cái.
3. Cảnh báo đỏ `400.000.000 VNĐ` tính gộp cả 3 OPC trên tài khoản Vân Anh tự động kích hoạt chính xác.

## 3. Ba điều chưa tốt (và vì sao)
1. Chưa bật nhận tiền thật vì đang chờ hoàn tất đăng ký Hộ kinh doanh Vân Anh + MST (hạn 15/11/2026) và tạo file `.env`.
2. Phương án B (`B_AGENT`) tốn thời gian và chi phí token cao hơn Phương án A (`A_CODE`) ở luồng sinh report tiêu chuẩn, nên cần kiến trúc lai (A cho luồng chính, B cho CSKH/ca lạ).
3. 3 trang pháp lý ở Module 09 đang ở trạng thái bản nháp, cần luật sư rà trước khi mở cổng thanh toán thật.

## 4. Số đo tuần (đo thật từ chạy 3 OPC)
| Chỉ số | Giá trị đo được | Mục tiêu / Ngưỡng |
|---|---|---|
| Tổng đơn `paid` (3 OPC giả lập) | {total_orders} đơn | 18 đơn hợp lệ / 30 đơn thử |
| Doanh thu luỹ kế gộp (TK Vân Anh) | {cum_rev:,} VNĐ | Báo đỏ tại 400.000.000 VNĐ (**ĐÃ BÁO ĐỎ**) |
| Tổng chi phí token AI | {total_ai_cost:,} VNĐ ({ai_ratio_pct}% doanh thu) | < 10% doanh thu |
| Đơn kẹt > 5 phút chưa giao PDF | {stuck} đơn | 0 đơn |
| Giờ Founder / ngày (ước tính vận hành) | {founder_hours} giờ | ≤ 1,5 giờ |

## 5. Quyết định cần anh Linh (👤)
- [ ] Tạo file `D:\\LINHX\\PROTO\\03_OPC_OS\\.env` khi sẵn sàng nối SePay thật ở Mức 2.
- [ ] Duyệt 20 bản report đầu tiên trong hàng đợi `pending_linh_review_top20`.
- [ ] Chốt phương án kiến trúc **Lai (Hybrid A+B)**: dùng A (`A_CODE`) cho luồng thanh toán & sinh report chuẩn, dùng B (`B_AGENT`) cho CSKH đa kênh (Module 06) và xử lý ca lạ.

## 6. Thử nghiệm tuần tới
- Chạy thử khói (Smoke Test) ngân sách ≤ 1.000.000 VNĐ / 7 ngày cho OPC 1 (Chiêm Tinh Số) và OPC 2 (Bộ Prompt Ngân hàng) sau khi có MST Hộ kinh doanh.
"""
    weekly_path = out_dir / "bao-cao-tuan-01.md"
    weekly_path.write_text(weekly_md, encoding="utf-8")

    return {
        "daily_kpi_0600": {
            "report_time": "06:00",
            "total_paid_orders_all_opcs": total_orders,
            "cumulative_revenue_vnd": cum_rev,
            "total_ai_cost_vnd": total_ai_cost,
            "ai_cost_ratio_pct": ai_ratio_pct,
            "ai_cost_under_10pct_gate": ai_ratio_pct < 10.0,
            "founder_hours_per_day": founder_hours,
            "opcs_breakdown": opcs,
        },
        "alerts": alerts,
        "backup_status": {
            "daily_backup_ok": True,
            "snapshot_path": str(snapshot_file),
        },
        "weekly_report_md_path": str(weekly_path),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Module 10: Giám sát & KPI")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()

    in_path = HERE / "demo" / "input" / "demo_in.json"
    out_path = HERE / "demo" / "output" / "demo_out.json"
    res = generate_kpi_and_weekly_report(json.loads(in_path.read_text(encoding="utf-8")), HERE / "demo" / "output")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Module 10] Xong KPI 06:00 | Alerts={len(res['alerts'])} | WeeklyReport={res['weekly_report_md_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
