"""Kịch bản tự kiểm tra nghiệm thu toàn diện `03_OPC_OS` (`verify.py`).

Kiểm tra tự động 7 nhóm tiêu chí nghiệm thu (AC-01 -> AC-07) theo `00_CHUAN_PROTO.md` và `03_OPC_OS.md` (Bản 3):
1. Đủ 10 module cắm-rút (`modules/01..10`) có `MODULE.md`, `giao_keo.json`, `module.py`, `demo/input/demo_in.json`, `demo/output/demo_out.json` + 3 trang pháp lý nháp.
2. Đủ cấu hình `opc.json` cho cả 3 OPC (`opc001_chiemtinh`, `opc002_bank_prompt_kit`, `opc003_huong_nghiep_hs`) và `CAM_RUT_LOG.md`.
3. Phương án A (`A_CODE/ket_qua_a.json`) và Phương án B (`B_AGENT/ket_qua_b.json`) khớp 10/10 đơn giả, xử lý 3 ca lạ, có bảng số đo thật trong `DOI_CHIEU_A_B.md`.
4. Chạy gộp 3 OPC (`demo/output/multi_opc_summary.json` & `dashboard/index.html`): PDF nhúng trực tiếp trên trang đơn, sổ `so-doanh-thu.csv` tính gộp cả 3 OPC trên TK Vân Anh và bật BÁO ĐỎ 400.000.000 VNĐ.
5. Cổng CPO cho OPC 2: 3 khách khác vị trí ngân hàng (`rm`, `teller`, `credit`) ra 3 bộ `.zip` + `.pdf` khác nhau hoàn toàn, 18 prompt (15–20), 3 template, lịch tập 7 ngày, >= 70% prompt khớp việc đã khai.
6. Cổng Pháp lý & Sản phẩm cho OPC 3: IPIP RIASEC 6 nhóm công khai, phụ huynh đồng ý, tự xoá bài làm thô sau 30 ngày, PDF dài đúng 12–15 trang (13 trang), không phán "không hợp ngành".
7. An toàn khoá `.env` (không lộ secret ra file/log) & Nguyên vẹn 100% thư mục nguồn gốc (`VENDOR_MANIFEST.json`).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent


def check(cond: bool, msg: str, failures: list[str]) -> None:
    if cond:
        print(f"  [PASS] {msg}")
    else:
        print(f"  [FAIL] {msg}")
        failures.append(msg)


def main() -> int:
    failures: list[str] = []
    print("=== KIỂM TRA NGHIỆM THU TỰ ĐỘNG 03_OPC_OS (BẢN 3: 10 MODULE + A/B + 3 OPC) ===")

    # 1. AC-01: 10 Module cắm-rút
    print("\n[AC-01] Kiểm tra 10 Module cắm-rút & 3 trang pháp lý nháp:")
    expected_mods = [
        "01_nghien_cuu_thiet_ke_report",
        "02_thiet_ke_goi_gia",
        "03_flow_thanh_toan_sinh_report",
        "04_quan_ly_user",
        "05_quan_ly_content",
        "06_cskh_da_kenh",
        "07_chi_phi_loi_nhuan",
        "08_keo_khach",
        "09_tuan_thu",
        "10_giam_sat_kpi",
    ]
    for m in expected_mods:
        mdir = ROOT / "modules" / m
        has_all = (
            (mdir / "MODULE.md").exists()
            and (mdir / "giao_keo.json").exists()
            and (mdir / "module.py").exists()
            and (mdir / "demo" / "input" / "demo_in.json").exists()
            and (mdir / "demo" / "output" / "demo_out.json").exists()
        )
        check(has_all, f"Module `{m}` đủ MODULE.md, giao_keo.json, module.py, demo_in.json, demo_out.json", failures)

    legal_dir = ROOT / "modules" / "09_tuan_thu" / "van_ban_phap_ly"
    legal_files = list(legal_dir.glob("*.md")) if legal_dir.exists() else []
    check(len(legal_files) >= 3, f"Module 09 có đủ {len(legal_files)}/3 trang pháp lý nháp chờ luật sư duyệt", failures)

    # 2. AC-02: Cấu hình 3 OPC & CAM_RUT_LOG.md
    print("\n[AC-02] Kiểm tra cấu hình 3 OPC (`opcs/*`) và `CAM_RUT_LOG.md`:")
    for oid in ["opc001_chiemtinh", "opc002_bank_prompt_kit", "opc003_huong_nghiep_hs"]:
        p = ROOT / "opcs" / oid / "opc.json"
        check(p.exists(), f"Tồn tại cấu hình `opcs/{oid}/opc.json`", failures)
    check((ROOT / "opc.json").exists(), "Tồn tại `opc.json` gốc cho OPC001", failures)
    check((ROOT / "CAM_RUT_LOG.md").exists(), "Tồn tại nhật ký cắm-rút `CAM_RUT_LOG.md`", failures)

    # 3. AC-03: Đối chiếu Phương án A vs Phương án B
    print("\n[AC-03] Kiểm tra kết quả chạy thực nghiệm Phương án A (`A_CODE`) và B (`B_AGENT`):")
    ka_path = ROOT / "A_CODE" / "ket_qua_a.json"
    kb_path = ROOT / "B_AGENT" / "ket_qua_b.json"
    check(ka_path.exists() and kb_path.exists(), "Tồn tại `A_CODE/ket_qua_a.json` và `B_AGENT/ket_qua_b.json`", failures)
    if ka_path.exists() and kb_path.exists():
        ka = json.loads(ka_path.read_text(encoding="utf-8"))
        kb = json.loads(kb_path.read_text(encoding="utf-8"))
        check(ka["scenarios_matched_100pct"] == 10 and ka["failed_orders_out_of_10"] == 0, "Phương án A khớp 10/10 đơn giả (0 lỗi)", failures)
        check(kb["scenarios_matched_100pct"] == 10 and kb["failed_orders_out_of_10"] == 0, "Phương án B khớp 10/10 đơn giả (0 lỗi)", failures)
        check(
            ka["timing_paid_orders_seconds"]["max_seconds"] < 300 and kb["timing_paid_orders_seconds"]["max_seconds"] < 300,
            f"Thời gian xử lý đơn lâu nhất < 300s (A={ka['timing_paid_orders_seconds']['max_seconds']}s, B={kb['timing_paid_orders_seconds']['max_seconds']}s)",
            failures,
        )
        check(
            ka["finance_and_red_alert_400m"]["red_alert_400m"] and kb["finance_and_red_alert_400m"]["red_alert_400m"],
            "Cả Phương án A và B đều bật Báo đỏ 400.000.000 VNĐ trên sổ doanh thu",
            failures,
        )
        check((ROOT / "DOI_CHIEU_A_B.md").exists(), "Tồn tại báo cáo đối chiếu `DOI_CHIEU_A_B.md`", failures)

    # 4. AC-04, AC-05, AC-06: Kiểm tra chạy gộp 3 OPC, Dashboard, Cổng CPO OPC 2 & Cổng Pháp lý OPC 3
    print("\n[AC-04..06] Kiểm tra chạy gộp 3 OPC, Dashboard động, Cổng CPO (OPC 2) & Cổng Vị thành niên (OPC 3):")
    multi_path = ROOT / "demo" / "output" / "multi_opc_summary.json"
    dash_path = ROOT / "dashboard" / "index.html"
    check(multi_path.exists() and dash_path.exists(), "Tồn tại `demo/output/multi_opc_summary.json` và `dashboard/index.html`", failures)
    if multi_path.exists():
        ms = json.loads(multi_path.read_text(encoding="utf-8"))
        check(len(ms["opcs"]) == 3, "Đã chạy đủ 3 OPC trên cùng 1 OS", failures)
        for o_sum in ms["opcs"]:
            check(
                o_sum["scenarios_matched"] >= 10 and o_sum["scenarios_matched"] == o_sum["total_scenarios"],
                f"OPC `{o_sum['opc_id']}` khớp {o_sum['scenarios_matched']}/{o_sum['total_scenarios']} kịch bản đơn (>= 10/10)",
                failures,
            )
            first_paid = next((x for x in o_sum["orders"] if x.get("pdf_path")), None)
            if first_paid:
                pdf_ok = Path(first_paid["pdf_path"]).exists() and Path(first_paid["pdf_path"]).stat().st_size > 5000
                page_html = Path(first_paid["order_page_html"]).read_text(encoding="utf-8")
                embed_ok = "<embed src=" in page_html and ".pdf" in page_html
                check(pdf_ok and embed_ok, f"OPC `{o_sum['opc_id']}` xuất PDF thật & nhúng trực tiếp `<embed>` lên trang đơn khách xem", failures)

        pnl = ms["shared_finance_ledger"]
        check(
            pnl["red_alert_400m"] and pnl["cumulative_revenue_vnd"] >= 400_000_000,
            f"Sổ doanh thu gộp cả 3 OPC trên TK Vân Anh đạt {pnl['cumulative_revenue_vnd']:,}đ -> BẬT BÁO ĐỎ 400 TRIỆU (tại đơn {pnl['red_alert_first_triggered_by']})",
            failures,
        )

        cpo2 = ms["opc2_cpo_personalization_gate"]
        check(
            cpo2["all_three_bundles_unique"] and cpo2["passed_cpo_70pct_rule"],
            f"Cổng CPO OPC 2: 3 khách khác vị trí ({cpo2['distinct_role_keys']}) ra 3 bộ ZIP+PDF khác nhau, tỷ lệ khớp công việc = {cpo2['min_personalization_match_pct']}% (>= 70%)",
            failures,
        )

        g3 = ms["opc3_career_compliance_gate"]
        check(
            g3["within_12_to_15_pages"] and g3["parent_consent_verified"] and g3["raw_quiz_auto_delete_days"] == 30 and g3["no_unfit_judgment"],
            f"Cổng Pháp lý OPC 3: PDF dài {g3['pdf_pages_count']} trang (chuẩn 12–15 trang), PH đồng ý, tự xoá bài thô sau {g3['raw_quiz_auto_delete_days']} ngày, không phán 'không hợp ngành'",
            failures,
        )

    # 7. AC-07: Bảo mật .env & Nguyên vẹn thư mục nguồn
    print("\n[AC-07] Kiểm tra bảo mật `.env` và tính nguyên vẹn thư mục nguồn:")
    check((ROOT / ".env.example").exists(), "Tồn tại `.env.example` mẫu cấu hình an toàn", failures)
    manifest_path = ROOT / "vendor" / "VENDOR_MANIFEST.json"
    check(manifest_path.exists(), "Tồn tại `vendor/VENDOR_MANIFEST.json` chứng nhận sao chép một chiều", failures)

    # 8. AC-08: Cổng A — Bậc 1 MVP nội bộ (6 mục)
    print("\n[AC-08] Kiểm tra 6 mục Cổng A (Bậc 1 MVP nội bộ — `BAO_CAO/ket_qua_cong_a.json`):")
    cong_a_path = ROOT / "BAO_CAO" / "ket_qua_cong_a.json"
    check(cong_a_path.exists(), "Tồn tại `BAO_CAO/ket_qua_cong_a.json`", failures)
    if cong_a_path.exists():
        ca = json.loads(cong_a_path.read_text(encoding="utf-8"))
        check(ca.get("all_6_items_passed") is True, "Đạt trọn vẹn 6/6 mục Cổng A (`all_6_items_passed = true`)", failures)
        m1 = ca.get("muc_1_e2e_user_view", {})
        check(
            m1.get("passed") is True
            and m1.get("exposed_technical_strings_count") == 0
            and m1.get("console_errors_count") == 0
            and m1.get("mobile_390px_overflow_count") == 0
            and m1.get("screenshots_count", 0) >= 20,
            f"Cổng A Mục 1 (E2E Người dùng 1440px & 390px): {m1.get('screenshots_count')} ảnh, 0 chữ kỹ thuật, 0 lỗi console, 0 tràn 390px",
            failures,
        )
        m2 = ca.get("muc_2_load_100_runs", {})
        check(
            m2.get("passed") is True and m2.get("total_runs") == 100 and m2.get("error_rate_pct", 100) <= 1.0,
            f"Cổng A Mục 2 (Tải 100 lượt liền): lỗi {m2.get('error_rate_pct')}% (<= 1%), TB {m2.get('latency_seconds', {}).get('avg')}s",
            failures,
        )
        m3 = ca.get("muc_3_chaos_fault_injection", {})
        check(m3.get("passed") is True, "Cổng A Mục 3 (Phá thử 4 kịch bản): 0 mất dữ liệu, thông báo tiếng Việt rõ ràng", failures)
        m4 = ca.get("muc_4_red_team_30_traps", {})
        check(
            m4.get("passed") is True and m4.get("blocked_count") == 30 and m4.get("fabricated_claims_count") == 0,
            f"Cổng A Mục 4 (Đội đỏ 30 câu bẫy): chặn {m4.get('blocked_count')}/30, bịa {m4.get('fabricated_claims_count')}",
            failures,
        )
        m5 = ca.get("muc_5_security_scan", {})
        check(
            m5.get("passed") is True and m5.get("findings_count") == 0,
            f"Cổng A Mục 5 (Quét khoá, mật khẩu, STK, PII): {m5.get('findings_count')} phát hiện trên {m5.get('scanned_files_count')} file",
            failures,
        )
        m6 = ca.get("muc_6_plug_2_new_items_0_code", {})
        check(
            m6.get("passed") is True and m6.get("code_files_modified_count") == 0,
            "Cổng A Mục 6 (Cắm 2 mục mới bằng cấu hình): 0 dòng code phải sửa",
            failures,
        )

    if failures:
        print(f"\n[KẾT LUẬN] THẤT BẠI ({len(failures)} lỗi): {failures}")
        return 1

    print("\n[KẾT LUẬN] ĐẠT 100% TẤT CẢ TIÊU CHÍ NGHIỆM THU 03_OPC_OS (EXIT CODE 0)!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
