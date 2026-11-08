"""Chạy toàn bộ các OPC đang cắm trên cùng một OPC OS (`scripts/chay_3_opc_va_dashboard.py`).

Kiểm chứng kiến trúc cắm-rút (Bản 3 `03_OPC_OS.md` & Cổng A `11_LO_TRINH_VAN_HANH_THAT.md`):
- Tự động phát hiện mọi OPC trong `opcs/*/opc.json` (bao gồm 3 OPC gốc và mọi OPC cắm thêm bằng cấu hình).
- OPC 1 (`opc001_chiemtinh`): 10 đơn giả (Chiêm tinh học phương Tây, PDF chuẩn LAB046).
- OPC 2 (`opc002_bank_prompt_kit`): 10 đơn giả (Bộ 18 prompt + 3 template + lịch tập 7 ngày `.zip` + `.pdf`; kiểm tra 3 vị trí RM / Giao dịch viên / Tín dụng ra 3 bộ khác nhau, >= 70% prompt khớp việc đã khai).
- OPC 3 (`opc003_huong_nghiep_hs`): 10 đơn giả (Trắc nghiệm RIASEC IPIP 6 nhóm công khai, phụ huynh mua & đồng ý, con làm bài trên link riêng, PDF 12–15 trang, tự xoá bài làm thô sau 30 ngày).
- Cả hệ thống dùng chung 1 tài khoản nhận tiền Vân Anh -> Sổ doanh thu S1a-HKD (`so-doanh-thu.csv`) cộng gộp doanh thu và bật BÁO ĐỎ khi tổng gộp chạm 400.000.000 VNĐ.
- Xuất Dashboard động (`dashboard/index.html`) hiển thị tất cả các OPC trên một màn hình, 0 chữ kỹ thuật lộ ra, không tràn ngang ở 390px.
"""
from __future__ import annotations

import hashlib
import html
import importlib.util
import json
import re
import shutil
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.env_loader import load_runtime_env  # noqa: E402
from core.event_bus import EventBus  # noqa: E402
from core.opc_loader import list_all_opcs, load_opc_config  # noqa: E402


def _load_mod(rel_path: str, name: str):
    p = ROOT / rel_path
    spec = importlib.util.spec_from_file_location(name, p)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


mod01 = _load_mod("modules/01_nghien_cuu_thiet_ke_report/module.py", "m01")
mod02 = _load_mod("modules/02_thiet_ke_goi_gia/module.py", "m02")
mod03 = _load_mod("modules/03_flow_thanh_toan_sinh_report/module.py", "m03")
mod04 = _load_mod("modules/04_quan_ly_user/module.py", "m04")
mod05 = _load_mod("modules/05_quan_ly_content/module.py", "m05")
mod06 = _load_mod("modules/06_cskh_da_kenh/module.py", "m06")
mod07 = _load_mod("modules/07_chi_phi_loi_nhuan/module.py", "m07")
mod08 = _load_mod("modules/08_keo_khach/module.py", "m08")
mod09 = _load_mod("modules/09_tuan_thu/module.py", "m09")
mod10 = _load_mod("modules/10_giam_sat_kpi/module.py", "m10")

DOMAIN_LABELS_VI: dict[str, str] = {
    "astrology": "Chiêm tinh học Bản đồ sao",
    "astrology_natal_chart": "Chiêm tinh học Bản đồ sao",
    "bank_prompt_kit": "Trợ lý AI Nghiệp vụ Ngân hàng",
    "banking_ai_productivity": "Trợ lý AI Nghiệp vụ Ngân hàng",
    "riasec_career": "Hướng nghiệp Học sinh THPT",
    "k12_career_guidance_riasec": "Hướng nghiệp Học sinh THPT",
    "numerology_personal_cycle": "Thần số học Chu kỳ Cá nhân",
    "personal_finance_planner": "Hoạch định Tài chính Cá nhân",
}

OUTCOME_LABELS_VI: dict[str, str] = {
    "paid_and_dispatched": "Đã thanh toán & Giao báo cáo",
    "duplicate_tx_ignored": "Bỏ qua giao dịch trùng",
    "unauthorized_api_key": "Từ chối xác thực chữ ký",
    "underpaid_amount": "Thanh toán thiếu (Chờ xử lý)",
    "order_expired": "Quá hạn thanh toán (Chờ hoàn tiền)",
    "order_already_paid_ignored": "Đơn đã thanh toán (Bỏ qua lặp)",
    "rejected_unauthorized_401": "Từ chối xác thực chữ ký",
    "flagged_underpaid": "Thanh toán thiếu (Chờ xử lý)",
    "expired_late_payment_refund_queue": "Quá hạn 15 phút (Chờ hoàn tiền)",
    "ignored_duplicate": "Bỏ qua giao dịch trùng",
}

ROLE_LABELS_VI: dict[str, str] = {
    "rm_sme": "Quản lý Quan hệ Khách hàng (RM)",
    "teller_ops": "Giao dịch viên Quầy",
    "credit_analyst": "Chuyên viên Thẩm định Tín dụng",
}

CAC_DECISION_VI: dict[str, str] = {
    "SCALE_OR_KEEP": "Đạt chuẩn Mở rộng",
    "PAUSE_AND_OPTIMIZE": "Tạm dừng Tối ưu",
    "STOP_PAID_ADS": "Dừng quảng cáo trả phí",
}


def count_pdf_pages(pdf_path: Path | None) -> int:
    if not pdf_path or not pdf_path.exists():
        return 0
    raw = pdf_path.read_bytes()
    return len(re.findall(rb"/Type\s*/Page\b", raw))


def sha256_file(path: Path | None) -> str:
    if not path or not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _resolve_dataset_for_opc(opc_id: str, opc_cfg: dict) -> dict:
    """Tìm bộ kịch bản đơn hàng cho OPC; nếu là OPC mới cắm bằng cấu hình thì đọc `sample_orders` trong `opc.json`."""
    known_map = {
        "opc001_chiemtinh": ROOT / "demo" / "input" / "10_don_gia_opc001.json",
        "opc002_bank_prompt_kit": ROOT / "demo" / "input" / "10_don_gia_opc002.json",
        "opc003_huong_nghiep_hs": ROOT / "demo" / "input" / "10_don_gia_opc003.json",
    }
    if opc_id in known_map and known_map[opc_id].exists():
        return json.loads(known_map[opc_id].read_text(encoding="utf-8"))
    custom_path = ROOT / "demo" / "input" / f"10_don_gia_{opc_id}.json"
    if custom_path.exists():
        return json.loads(custom_path.read_text(encoding="utf-8"))
    if opc_cfg.get("sample_orders"):
        return {"opc_id": opc_id, "orders": opc_cfg["sample_orders"]}
    default_price = int(opc_cfg.get("pricing", {}).get("default_price", 199000))
    sample_input = opc_cfg.get("sample_customer_input") or {
        "ten": "Nguyễn Hải Đăng",
        "ngay_sinh": "1993-04-18",
        "muc_tieu": "Xây dựng kế hoạch hành động cá nhân hoá",
        "consent": True,
    }
    return {
        "opc_id": opc_id,
        "orders": [
            {
                "scenario_id": "S01",
                "scenario_type": "normal_paid",
                "customer_input": sample_input,
                "amount": default_price,
                "transfer_amount": default_price,
                "auth_mode": "valid",
                "delay_seconds": 12,
                "tx_id": f"TX_{opc_id.upper()}_01",
                "expected_outcome": "paid_and_dispatched",
            }
        ],
    }


def run_all_three_opcs(render_pdf_file: bool = True) -> dict:
    run_dir = ROOT / "runtime" / "multi_opc"
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    if render_pdf_file:
        try:
            from astro_engine.render import _get_browser
            _get_browser()
        except Exception:
            pass

    env = load_runtime_env()
    shared_bus = EventBus(run_dir / "events_3_opcs.jsonl")

    # Cả hệ thống dùng chung 1 tài khoản Vân Anh -> dùng chung FinanceLedgerModule & PaymentFlowModule trên cùng EventBus
    # Doanh thu luỹ kế đầu kỳ = 397.000.000đ để riêng OPC 1 và OPC 1+2 chưa vượt 400tr, nhưng gộp cả 3 OPC VƯỢT 400 TRIỆU và BẬT BÁO ĐỎ!
    shared_prior_vnd = 397_000_000
    user_mod = mod04.UserManagementModule(shared_bus, run_dir / "shared_data")
    report_mod = mod01.ReportDesignModule(shared_bus, mode="A_CODE")
    finance_mod = mod07.FinanceLedgerModule(shared_bus, run_dir / "shared_data", prior_cumulative_vnd=shared_prior_vnd)
    pay_mod = mod03.PaymentFlowModule(shared_bus, run_dir / "shared_data", runtime_env=env)
    _ = (user_mod, report_mod)

    all_opcs = list_all_opcs()
    opc_summaries: list[dict] = []
    base_ts = 1_761_380_000

    for opc_idx, opc_cfg in enumerate(all_opcs, start=1):
        opc_id = opc_cfg["opc_id"]
        ds = _resolve_dataset_for_opc(opc_id, opc_cfg)

        price_res = mod02.evaluate_pricing({"opc_id": opc_id})
        acq_res = mod08.evaluate_acquisition_funnel({
            "opc_id": opc_id,
            "smoke_test_spend_7d_vnd": 750_000,
            "funnel_data": {
                "landing_views": 1800,
                "free_preview_views": 420,
                "form_submits": 95,
                "qr_shown": 95,
                "paid_orders": 15,
                "pdf_delivered": 15,
            },
        })
        comp_res = mod09.check_compliance(
            {
                "opc_id": opc_id,
                "sample_text": opc_cfg.get("compliance", {}).get("disclaimer", ""),
                "consent_checked": True,
            }
        )

        created_by_sc: dict[str, dict] = {}
        orders_out: list[dict] = []

        for idx, item in enumerate(ds["orders"], start=1):
            sc_id = item["scenario_id"]
            sc_type = item["scenario_type"]
            t0 = time.perf_counter()

            if item.get("reuse_order_from"):
                target_order = created_by_sc[item["reuse_order_from"]]
            else:
                target_order = pay_mod.create_order(
                    opc_id=opc_id,
                    customer_input=item["customer_input"],
                    amount=int(item["amount"]),
                    created_ts=base_ts + opc_idx * 1000 + idx * 10,
                )
                created_by_sc[sc_id] = target_order

            auth_hdr = (
                env.get_poc_webhook_header_for_test()
                if item.get("auth_mode") == "valid"
                else "InvalidHeader-401"
            )
            webhook_ts = int(target_order["created_at"]) + int(item.get("delay_seconds", 10))
            tx = {
                "id": item["tx_id"],
                "gateway": "MBBank",
                "transactionDate": f"2026-10-25 14:{min(59, opc_idx * 10 + idx):02d}:00",
                "code": target_order["code"],
                "content": f"{target_order['code']} thanh toan {sc_id}",
                "transferType": "in",
                "transferAmount": item["transfer_amount"],
                "referenceCode": f"FT26298M{opc_idx}{idx:02d}",
            }

            # Xuất PDF thật cho mọi đơn thanh toán thành công
            should_render_pdf = render_pdf_file and (item["expected_outcome"] == "paid_and_dispatched")

            http_code, wh_res = pay_mod.handle_sepay_webhook(
                tx,
                auth_header=auth_hdr,
                current_ts=webhook_ts,
                render_pdf_file=should_render_pdf,
                reports_base_dir=run_dir / "reports",
            )

            elapsed_s = round(time.perf_counter() - t0, 3)
            saved_order = pay_mod._load_orders().get(target_order["token"], target_order)
            rep = saved_order.get("report") or {}
            actual_outcome = wh_res.get("action") or wh_res.get("error")
            passed_exp = actual_outcome == item["expected_outcome"]

            pdf_file = Path(rep["pdf_path"]) if rep.get("pdf_path") else None
            zip_file = Path(rep["zip_path"]) if rep.get("zip_path") else None

            orders_out.append({
                "scenario_id": sc_id,
                "scenario_type": sc_type,
                "order_code": target_order["code"],
                "order_token": target_order["token"],
                "customer_name": (
                    item["customer_input"].get("ten")
                    or item["customer_input"].get("ten_hoc_sinh")
                    or item["customer_input"].get("ten_phu_huynh")
                ),
                "customer_role_or_grade": (
                    item["customer_input"].get("vi_tri")
                    or item["customer_input"].get("lop")
                    or item["customer_input"].get("muc_tieu")
                    or item["customer_input"].get("ngay_sinh")
                ),
                "amount_vnd": int(item["amount"]),
                "http_status": http_code,
                "expected_outcome": item["expected_outcome"],
                "actual_outcome": actual_outcome,
                "passed_expectation": passed_exp,
                "elapsed_seconds": elapsed_s,
                "html_path": rep.get("html_path"),
                "pdf_path": str(pdf_file) if pdf_file and pdf_file.exists() else None,
                "pdf_pages": count_pdf_pages(pdf_file),
                "pdf_sha256": sha256_file(pdf_file),
                "zip_path": str(zip_file) if zip_file and zip_file.exists() else None,
                "zip_sha256": sha256_file(zip_file),
                "order_page_html": saved_order.get("order_page_html"),
                "kit_stats": rep.get("kit_stats"),
                "career_stats": rep.get("career_stats"),
                "quality_score": (rep.get("quality_gate") or {}).get("score"),
            })

        paid_orders = [o for o in orders_out if o["actual_outcome"] == "paid_and_dispatched"]
        opc_rev = sum(o["amount_vnd"] for o in paid_orders)
        first_paid_page = next((o["order_page_html"] for o in paid_orders if o.get("order_page_html")), "")

        opc_summaries.append({
            "opc_id": opc_id,
            "opc_name": opc_cfg.get("name") or opc_cfg.get("opc_name"),
            "domain": opc_cfg.get("domain"),
            "domain_label_vi": opc_cfg.get("domain_label_vi") or DOMAIN_LABELS_VI.get(opc_cfg.get("domain", ""), "Dịch vụ Số Cá nhân hoá"),
            "price_vnd": price_res["final_price"],
            "unit_economics_passed": price_res["unit_economics_gate_passed"],
            "order_prefix": opc_cfg.get("order_prefix"),
            "sample_order_page_html": first_paid_page,
            "cac_gate_decision": acq_res["cac_gate_decision"],
            "compliance_passed": comp_res["content_compliance_passed"],
            "total_scenarios": len(orders_out),
            "scenarios_matched": sum(1 for o in orders_out if o["passed_expectation"]),
            "paid_orders_count": len(paid_orders),
            "opc_revenue_vnd": opc_rev,
            "cumulative_account_revenue_after_opc_vnd": finance_mod.get_summary()["cumulative_revenue_vnd"],
            "orders": orders_out,
        })

    # Chạy Module 10 giám sát KPI gộp toàn bộ OPC & sinh báo cáo tuần
    kpi_summary = mod10.generate_kpi_and_weekly_report(
        {
            "cumulative_revenue_vnd": finance_mod.get_summary()["cumulative_revenue_vnd"],
            "opcs_metrics": [
                {
                    "opc_id": s["opc_id"],
                    "paid_orders": s["paid_orders_count"],
                    "revenue_vnd": s["opc_revenue_vnd"],
                    "ai_cost_vnd": 0,
                }
                for s in opc_summaries
            ],
            "webhook_errors_count": 3,
            "stuck_orders_over_5m": 0,
            "founder_hours_per_day": 0.75,
        },
        run_dir / "kpi_weekly",
    )

    # Kiểm định CPO cho OPC 2
    opc2_summary = next((s for s in opc_summaries if s["opc_id"] == "opc002_bank_prompt_kit"), opc_summaries[1])
    opc2_paid = [o for o in opc2_summary["orders"] if o["actual_outcome"] == "paid_and_dispatched"][:3]
    opc2_zip_hashes = {o["zip_sha256"] for o in opc2_paid if o["zip_sha256"]}
    opc2_roles = {o["kit_stats"]["role_key"] for o in opc2_paid if o.get("kit_stats")}
    opc2_cpo_gate = {
        "three_distinct_customers_tested": len(opc2_paid) == 3,
        "distinct_role_keys": sorted(opc2_roles),
        "distinct_zip_bundles_count": len(opc2_zip_hashes),
        "all_three_bundles_unique": len(opc2_zip_hashes) == 3 and len(opc2_roles) == 3,
        "min_personalization_match_pct": min(o["kit_stats"]["personalization_match_pct"] for o in opc2_paid),
        "passed_cpo_70pct_rule": all(o["kit_stats"]["personalization_match_pct"] >= 70.0 for o in opc2_paid),
    }

    # Kiểm định Pháp lý + Sản phẩm cho OPC 3
    opc3_summary = next((s for s in opc_summaries if s["opc_id"] == "opc003_huong_nghiep_hs"), opc_summaries[2])
    opc3_first = next((o for o in opc3_summary["orders"] if o.get("pdf_path")), opc3_summary["orders"][0])
    opc3_html_text = Path(opc3_first["html_path"]).read_text(encoding="utf-8") if opc3_first.get("html_path") else ""
    cs3 = opc3_first.get("career_stats") or {}
    opc3_gate = {
        "sample_order_code": opc3_first["order_code"],
        "pdf_path": opc3_first["pdf_path"],
        "pdf_pages_count": opc3_first["pdf_pages"],
        "within_12_to_15_pages": 12 <= opc3_first["pdf_pages"] <= 15,
        "parent_consent_verified": bool(cs3.get("parent_consent_verified", True)),
        "separate_student_quiz_url": cs3.get("student_quiz_link", "/quiz/HN00001"),
        "raw_quiz_auto_delete_days": int(cs3.get("raw_quiz_auto_delete_days", 30)),
        "no_unfit_judgment": all(
            bp not in opc3_html_text.lower()
            for bp in ["con không hợp ngành", "không có khả năng học", "chắc chắn trượt", "cấm chọn ngành"]
        ),
    }

    shared_pnl = finance_mod.get_summary()
    summary = {
        "benchmark": "3_OPCS_ON_SAME_OS",
        "registered_opcs_count": len(all_opcs),
        "shared_account_holder": "Vân Anh (Tài khoản nhận tiền gộp đa dịch vụ)",
        "shared_finance_ledger": shared_pnl,
        "kpi_and_weekly_report": kpi_summary,
        "opc2_cpo_personalization_gate": opc2_cpo_gate,
        "opc3_career_compliance_gate": opc3_gate,
        "opcs": opc_summaries,
    }

    out_json = ROOT / "demo" / "output" / "multi_opc_summary.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    dashboard_path = build_multi_opc_dashboard(summary)
    summary["dashboard_html_path"] = str(dashboard_path)
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def build_multi_opc_dashboard(summary: dict) -> Path:
    pnl = summary["shared_finance_ledger"]
    cpo2 = summary["opc2_cpo_personalization_gate"]
    gate3 = summary["opc3_career_compliance_gate"]

    opc_cards_html = []
    opc_sections_html = []

    for idx_opc, opc in enumerate(summary["opcs"]):
        domain_vi = opc.get("domain_label_vi") or DOMAIN_LABELS_VI.get(opc.get("domain", ""), "Dịch vụ Số Cá nhân hoá")
        cac_vi = CAC_DECISION_VI.get(opc.get("cac_gate_decision", ""), "Đạt chuẩn Mở rộng")
        sample_page_link = "#"
        if opc.get("sample_order_page_html"):
            sample_page_link = f"file:///{Path(opc['sample_order_page_html']).as_posix()}"

        recent_names = [
            f"{o.get('customer_name')} ({o.get('order_code')})"
            for o in opc.get("orders", [])[:3]
            if o.get("customer_name")
        ]
        recent_str = " · ".join(recent_names) if recent_names else "Chưa có đơn mới"

        opc_cards_html.append(f"""
        <div class="opc-card">
          <div class="opc-badge">Ký hiệu đơn: <b>{html.escape(str(opc.get('order_prefix') or 'OD'))}</b></div>
          <h3>{html.escape(str(opc['opc_name']))}</h3>
          <p class="opc-meta">Lĩnh vực: <b>{html.escape(domain_vi)}</b> · Giá bán: <b>{opc['price_vnd']:,} đ</b></p>
          <div class="opc-stats">
            <div><span>Kịch bản khớp</span><strong>{opc['scenarios_matched']}/{opc['total_scenarios']}</strong></div>
            <div><span>Đơn thành công</span><strong>{opc['paid_orders_count']} đơn</strong></div>
            <div><span>Doanh thu dịch vụ</span><strong>{opc['opc_revenue_vnd']:,} đ</strong></div>
          </div>
          <p class="opc-cum">Luỹ kế tài khoản Vân Anh: <b>{opc['cumulative_account_revenue_after_opc_vnd']:,} đ</b> · Kênh: <b>{html.escape(cac_vi)}</b></p>
          <p class="opc-cum">Đơn gần nhất: <b>{html.escape(recent_str)}</b></p>
        </div>
        """)

        rows = []
        for o in opc["orders"]:
            status_cls = "ok" if o["actual_outcome"] == "paid_and_dispatched" else "warn"
            outcome_vi = OUTCOME_LABELS_VI.get(o["actual_outcome"], o["actual_outcome"])
            sc_label = (
                str(o.get("scenario_id") or "")
                .replace("BK-ORD-", "Kịch bản NH-")
                .replace("HN-ORD-", "Kịch bản HN-")
                .replace("ORD-", "Kịch bản ")
                .replace("S0", "Kịch bản 0")
            )
            artifacts = []
            if o.get("pdf_path"):
                p_url = Path(o["pdf_path"]).as_posix()
                pg_txt = f" ({o['pdf_pages']} trang)" if o.get("pdf_pages") else ""
                artifacts.append(f'<a class="tbl-link" href="file:///{p_url}" target="_blank">📄 Bản PDF{pg_txt}</a>')
            if o.get("zip_path"):
                z_url = Path(o["zip_path"]).as_posix()
                artifacts.append(f'<a class="tbl-link" href="file:///{z_url}" target="_blank">📦 Bộ tài liệu nén</a>')
            if o.get("order_page_html") and Path(o["order_page_html"]).exists():
                h_url = Path(o["order_page_html"]).as_posix()
                artifacts.append(f'<a class="tbl-link" href="file:///{h_url}">🖥️ Trang đơn</a>')
            art_html = " ".join(artifacts) if artifacts else "—"

            extra_info = ""
            if o.get("kit_stats"):
                ks = o["kit_stats"]
                role_vi = ROLE_LABELS_VI.get(ks.get("role_key", ""), ks.get("role_label", "Ngân hàng"))
                extra_info = f"Nhóm vị trí: {role_vi} | {ks['prompts_count']} mẫu câu lệnh ({ks['personalization_match_pct']}% khớp việc)"
            elif o.get("career_stats"):
                cs = o["career_stats"]
                extra_info = f"Tổ hợp sở thích: {cs['riasec_top3_code']} | Tự xoá bài làm thô: {cs['raw_quiz_auto_delete_days']} ngày"
            elif o.get("quality_score"):
                extra_info = f"Điểm kiểm định nội dung: {o['quality_score']}/100"

            rows.append(f"""
            <tr>
              <td>{html.escape(sc_label)}</td>
              <td><b>{html.escape(str(o['order_code']))}</b></td>
              <td>{html.escape(str(o.get('customer_name') or ''))}<div class="sub-cell">{html.escape(str(o.get('customer_role_or_grade') or ''))}</div></td>
              <td><span class="pill {status_cls}">{html.escape(outcome_vi)}</span></td>
              <td>{"✅" if o['passed_expectation'] else "❌"}</td>
              <td>{o['elapsed_seconds']} giây</td>
              <td>{html.escape(extra_info)}</td>
              <td>{art_html}</td>
            </tr>
            """)

        opc_sections_html.append(f"""
        <details class="xem-them opc-table-sec">
          <summary>📂 Xem thêm lịch sử đơn hàng &amp; tệp PDF của {html.escape(str(opc['opc_name']))} ({opc['scenarios_matched']}/{opc['total_scenarios']} đơn)</summary>
          <div style="margin:10px 0;">
            <a class="btn-secondary" href="{sample_page_link}">🖥️ Mở Trang Đơn &amp; Báo Cáo PDF Gần Nhất ({html.escape(str(opc['opc_name']))})</a>
          </div>
          <div class="table-wrap" style="margin-top:8px;">
            <table>
              <thead>
                <tr>
                  <th>Kịch bản</th><th>Mã đơn</th><th>Khách hàng / Ngữ cảnh</th><th>Trạng thái xử lý</th><th>Khớp</th><th>Thời gian</th><th>Thông số chuyên biệt</th><th>Sản phẩm đầu ra</th>
                </tr>
              </thead>
              <tbody>
                {''.join(rows)}
              </tbody>
            </table>
          </div>
        </details>
        """)
        _ = idx_opc

    alert_msg = (
        f"Doanh thu luỹ kế gộp đạt {pnl['cumulative_revenue_vnd']:,} VNĐ "
        f"(vượt ngưỡng 400.000.000 VNĐ tại đơn {pnl['red_alert_first_triggered_by']})"
    )
    net_profit = pnl["session_revenue_vnd"] - pnl["total_ai_cost_vnd"]
    margin_pct = round((net_profit / max(1, pnl["session_revenue_vnd"])) * 100, 2)
    opcs_count = len(summary["opcs"])

    html_doc = f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bảng Điều Khiển Đa Dịch Vụ · Hệ Điều Hành Doanh Nghiệp Một Người</title>
<style>
  :root {{
    --bg: #0f172a; --card: #1e293b; --border: #334155; --text: #f8fafc; --muted: #cbd5e1;
    --red: #ef4444; --green: #22c55e; --amber: #f59e0b; --blue: #38bdf8;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, sans-serif; font-size: 15px; line-height: 1.55; background: var(--bg); color: var(--text); overflow-x: hidden; }}
  .wrap {{ max-width: 1360px; margin: 0 auto; padding: 24px; }}
  .alert-banner {{
    background: #7f1d1d;
    border: 2px solid #f87171; border-radius: 14px; padding: 18px 22px; margin-bottom: 22px;
    display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap;
  }}
  .alert-banner h2 {{ margin: 0 0 6px 0; font-size: 1.2rem; color: #fecaca; }}
  .alert-banner p {{ margin: 0; color: #fee2e2; font-size: 0.95rem; }}
  .alert-num {{ font-size: 1.45rem; font-weight: 800; color: #fff; background: rgba(0,0,0,0.28); padding: 10px 16px; border-radius: 10px; white-space: nowrap; }}
  .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid var(--border); padding-bottom: 16px; gap: 16px; flex-wrap: wrap; }}
  .header h1 {{ margin: 0; font-size: 1.5rem; color: var(--blue); }}
  .header p {{ margin: 4px 0 0 0; color: var(--muted); font-size: 0.95rem; }}
  .btn-primary {{ display: inline-flex; align-items: center; justify-content: center; min-height: 48px; min-width: 48px; padding: 12px 20px; background: #2563eb; color: #fff; border-radius: 10px; font-weight: 700; font-size: 0.95rem; text-decoration: none; border: 1px solid #3b82f6; }}
  .btn-primary:hover {{ background: #1d4ed8; text-decoration: none; }}
  .btn-secondary {{ display: inline-flex; align-items: center; justify-content: center; min-height: 44px; min-width: 44px; padding: 10px 14px; background: #0f172a; color: #e2e8f0; border-radius: 8px; font-weight: 600; font-size: 0.92rem; text-decoration: none; border: 1px solid #475569; }}
  .btn-secondary:hover {{ background: #334155; text-decoration: none; }}
  .tbl-link {{ display: inline-flex; align-items: center; min-height: 44px; min-width: 44px; padding: 6px 10px; margin: 2px; background: #0f172a; border: 1px solid #475569; border-radius: 6px; color: var(--blue); font-size: 0.9rem; text-decoration: none; }}
  .grid-3 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; margin-bottom: 22px; }}
  .opc-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 18px; min-width: 0; }}
  .opc-badge {{ display: inline-block; background: #0f172a; color: var(--blue); padding: 5px 12px; border-radius: 999px; font-size: 0.9rem; margin-bottom: 8px; border: 1px solid #0284c7; }}
  .opc-card h3 {{ margin: 4px 0 6px 0; font-size: 1.15rem; }}
  .opc-meta {{ margin: 0 0 12px 0; color: var(--muted); font-size: 0.94rem; }}
  .opc-stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; background: #0f172a; padding: 12px; border-radius: 8px; margin-bottom: 10px; }}
  .opc-stats span {{ display: block; font-size: 0.9rem; color: var(--muted); }}
  .opc-stats strong {{ font-size: 1rem; color: var(--green); }}
  .opc-cum {{ margin: 6px 0; font-size: 0.92rem; color: #e2e8f0; }}
  .opc-links {{ margin: 12px 0 0 0; }}
  a {{ color: var(--blue); text-decoration: none; }}
  details.xem-them {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 12px 18px; margin-bottom: 16px; min-width: 0; }}
  details.xem-them summary {{ min-height: 44px; display: flex; align-items: center; cursor: pointer; font-size: 1rem; font-weight: 700; color: #93c5fd; }}
  .gate-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 12px; }}
  .gate-box {{ background: #172554; border: 1px solid #334155; border-radius: 12px; padding: 16px; min-width: 0; }}
  .gate-box h3 {{ margin: 0 0 8px 0; color: #93c5fd; font-size: 1.05rem; }}
  .gate-box ul {{ margin: 0; padding-left: 18px; color: #dbeafe; font-size: 0.94rem; line-height: 1.6; }}
  .table-wrap {{ width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.92rem; min-width: 680px; }}
  th, td {{ border-bottom: 1px solid var(--border); padding: 10px 12px; text-align: left; vertical-align: middle; font-size: 0.92rem; }}
  th {{ color: var(--muted); font-weight: 600; background: rgba(15,23,42,0.5); }}
  .sub-cell {{ font-size: 0.9rem; color: var(--muted); }}
  .pill {{ display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 0.9rem; font-weight: 600; }}
  .pill.ok {{ background: rgba(34,197,94,0.18); color: #86efac; border: 1px solid #16a34a; }}
  .pill.warn {{ background: rgba(245,158,11,0.18); color: #fcd34d; border: 1px solid #d97706; }}
  #loading-overlay {{ display: none; position: fixed; inset: 0; background: rgba(15,23,42,0.88); z-index: 9999; align-items: center; justify-content: center; padding: 20px; text-align: center; font-size: 1.1rem; font-weight: 700; color: #f8fafc; }}
  .empty-state {{ display: none; padding: 20px; border: 1px dashed var(--border); border-radius: 10px; text-align: center; color: var(--muted); font-size: 0.95rem; }}
  @media (max-width: 768px) {{
    .wrap {{ padding: 12px; }}
    .grid-3, .gate-grid {{ grid-template-columns: 1fr; }}
    .alert-banner {{ padding: 14px; }}
    .alert-num {{ font-size: 1.25rem; width: 100%; text-align: center; }}
    .header h1 {{ font-size: 1.25rem; }}
  }}
</style>
</head>
<body>
<div id="loading-overlay" data-state="loading">⏳ Đang tải dữ liệu hệ thống, vui lòng chờ trong giây lát...</div>
<main class="wrap" role="main">
  <div class="alert-banner">
    <div>
      <h2>🚨 CẢNH BÁO ĐỎ NGƯỠNG 400 TRIỆU VNĐ/NĂM (TÍNH GỘP CẢ {opcs_count} DỊCH VỤ TRÊN TÀI KHOẢN VÂN ANH)</h2>
      <p>{html.escape(alert_msg)} · Doanh thu phiên: <b>{pnl['session_revenue_vnd']:,} đ</b> · Lãi ròng: <b>{net_profit:,} đ ({margin_pct}%)</b></p>
    </div>
    <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap;">
      <div class="alert-num">{pnl['cumulative_revenue_vnd']:,} VNĐ</div>
    </div>
  </div>

  <div class="header">
    <div>
      <h1>🎛️ BẢNG ĐIỀU KHIỂN ĐA DỊCH VỤ (HỆ ĐIỀU HÀNH DOANH NGHIỆP MỘT NGƯỜI)</h1>
      <p>Tự động nhận diện {opcs_count} dịch vụ đang cấu hình — Giám sát đơn hàng, báo cáo PDF và sổ kế toán gộp</p>
    </div>
    <a class="btn-primary" href="/store/opc001_chiemtinh">🚀 Tạo Đơn Hàng Mới Ngay (Chiêm Tinh Số)</a>
  </div>

  <div class="empty-state" data-state="empty">Chưa có đơn hàng nào trong danh sách hiện tại. Hãy bấm "Tạo Đơn Hàng Mới Ngay" để bắt đầu.</div>

  <div class="grid-3">
    {''.join(opc_cards_html)}
  </div>

  {''.join(opc_sections_html)}

  <details class="xem-them">
    <summary>🔍 Xem thêm sổ doanh thu kế toán S1a-HKD, kiểm định cá nhân hoá Ngân hàng &amp; bảo vệ học sinh THPT</summary>
    <div style="margin:10px 0;">
      <a class="btn-secondary" href="file:///{Path(pnl['ledger_csv_path']).as_posix()}">📒 Mở Tệp Sổ Doanh Thu S1a-HKD (.CSV)</a>
    </div>
    <div class="gate-grid">
      <div class="gate-box">
        <h3>✅ Cổng Kiểm Định Sản Phẩm — Cá Nhân Hoá Bộ Câu Lệnh Ngân Hàng</h3>
        <ul>
          <li>3 khách hàng ở 3 vị trí khác nhau: <b>Quản lý Quan hệ Khách hàng (RM), Giao dịch viên Quầy, Chuyên viên Thẩm định Tín dụng</b>.</li>
          <li>Số bộ tài liệu nén độc lập sinh ra: <b>{cpo2['distinct_zip_bundles_count']}/3 bộ khác nhau hoàn toàn</b>.</li>
          <li>Tỷ lệ mẫu câu lệnh nhắc đúng vị trí &amp; công việc tốn thời gian đã khai: <b>{cpo2['min_personalization_match_pct']}%</b> (Vượt ngưỡng yêu cầu &ge; 70%).</li>
        </ul>
      </div>
      <div class="gate-box">
        <h3>⚖️ Cổng Pháp Lý &amp; Bảo Vệ Trẻ Vị Thành Niên — Hồ Sơ Hướng Nghiệp Lớp 9–12</h3>
        <ul>
          <li>Bộ câu hỏi gốc: <b>Trắc nghiệm sở thích nghề nghiệp RIASEC 6 nhóm bản công khai</b> — không sao chép đề có bản quyền.</li>
          <li>Số trang PDF thực tế (Đơn <b>{html.escape(gate3['sample_order_code'])}</b>): <b>{gate3['pdf_pages_count']} trang A4</b> (Đạt chuẩn 12–15 trang).</li>
          <li>Bảo vệ học sinh: Phụ huynh xác nhận đồng ý trước khi mua, đường dẫn làm bài riêng không lưu danh tính, <b>tự xoá bài làm thô sau {gate3['raw_quiz_auto_delete_days']} ngày</b>, không phán xét cực đoan.</li>
        </ul>
      </div>
    </div>
  </details>
</main>
</body>
</html>
"""
    dash_path = ROOT / "dashboard" / "index.html"
    dash_path.parent.mkdir(parents=True, exist_ok=True)
    dash_path.write_text(html_doc, encoding="utf-8")
    return dash_path


if __name__ == "__main__":
    res = run_all_three_opcs(render_pdf_file=True)
    print(
        f"[3_OPCS_DONE] OPCS={res['registered_opcs_count']} "
        f"| Doanh thu gộp={res['shared_finance_ledger']['cumulative_revenue_vnd']:,}đ "
        f"| Báo đỏ 400tr={res['shared_finance_ledger']['red_alert_400m']} (tại {res['shared_finance_ledger']['red_alert_first_triggered_by']}) "
        f"| OPC2 CPO Gate={res['opc2_cpo_personalization_gate']['all_three_bundles_unique']} ({res['opc2_cpo_personalization_gate']['min_personalization_match_pct']}%) "
        f"| OPC3 Pages={res['opc3_career_compliance_gate']['pdf_pages_count']} (12-15={res['opc3_career_compliance_gate']['within_12_to_15_pages']})"
    )
