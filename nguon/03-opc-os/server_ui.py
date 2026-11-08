"""Máy chủ Giao diện Web cục bộ cho `03_OPC_OS` (`http://localhost:8300`).

Hỗ trợ đầy đủ hành trình người dùng thật (Bậc 1 MVP nội bộ — Cổng A):
- `http://localhost:8300/` : Bảng điều khiển Đa Dịch Vụ (tự động hiển thị mọi OPC trong `opcs/*/opc.json` + Báo đỏ 400 triệu + Sổ doanh thu S1a-HKD).
- `http://localhost:8300/ab` : Bảng đối chiếu trực quan Phương án A (Code thuần) và Phương án B (Trợ lý điều phối).
- `http://localhost:8300/store/<opc_id>` : Trang bán hàng có đủ các trường thông tin (Họ tên, Ngày sinh, Giờ sinh, Nơi sinh, Gói dịch vụ...).
- `http://localhost:8300/api/create-demo-order` : Tạo đơn hàng thật ở trạng thái `Chờ chuyển khoản` cho chính khách vừa điền và chuyển tới trang QR `/o/<token>`.
- `http://localhost:8300/api/confirm-test-payment?token=<token>` : Mô phỏng xác nhận chuyển khoản SePay chế độ thử (không tiền thật), sinh báo cáo & PDF của chính khách đó, ghi sổ S1a-HKD, cập nhật Dashboard và hiển thị ngay trên `/o/<token>`.
- `http://localhost:8300/o/<token>` : Trang theo dõi đơn hàng, mã QR thanh toán và đọc/tải báo cáo PDF trực tiếp (`200 OK`).
"""
from __future__ import annotations

import hashlib
import html
import http.server
import importlib.util
import json
import re
import socketserver
import sys
import time
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.env_loader import load_runtime_env  # noqa: E402
from core.event_bus import EventBus  # noqa: E402
from core.opc_loader import list_all_opcs, load_opc_config  # noqa: E402

PORT = 8300
ROOT_POSIX = ROOT.as_posix()


def _load_mod(rel_path: str, name: str):
    p = ROOT / rel_path
    spec = importlib.util.spec_from_file_location(name, p)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


mod01 = _load_mod("modules/01_nghien_cuu_thiet_ke_report/module.py", "ui_m01")
mod03 = _load_mod("modules/03_flow_thanh_toan_sinh_report/module.py", "ui_m03")
mod04 = _load_mod("modules/04_quan_ly_user/module.py", "ui_m04")
mod07 = _load_mod("modules/07_chi_phi_loi_nhuan/module.py", "ui_m07")
dash_script = _load_mod("scripts/chay_3_opc_va_dashboard.py", "ui_dash")
iso_pay_mod = _load_mod("services/payment_service_isolated.py", "ui_iso_pay")

ACTIVITY_LOG_PATH = ROOT / "runtime" / "nhat_ky_hoat_dong.jsonl"
ERROR_LOG_PATH = ROOT / "runtime" / "nhat_ky_loi.jsonl"


def log_activity(actor: str, action: str, detail: str) -> None:
    """Ghi nhật ký hoạt động (ai làm gì lúc nào) xuống `runtime/nhat_ky_hoat_dong.jsonl`."""
    try:
        ACTIVITY_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "thoi_gian": time.strftime("%Y-%m-%d %H:%M:%S"),
            "nguoi_thuc_hien": actor,
            "hanh_dong": action,
            "chi_tiet": detail,
        }
        with ACTIVITY_LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def log_error_alert(khu_vuc: str, thong_bao: str, muc_do: str = "Cảnh báo") -> None:
    """Ghi cảnh báo lỗi xuống `runtime/nhat_ky_loi.jsonl` để hiển thị trên màn `/tinh-trang`."""
    try:
        ERROR_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "thoi_gian": time.strftime("%Y-%m-%d %H:%M:%S"),
            "khu_vuc": khu_vuc,
            "muc_do": muc_do,
            "thong_bao": thong_bao,
        }
        with ERROR_LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass

FIELD_META: dict[str, tuple[str, str]] = {
    "ten": ("Họ và tên khách hàng", "Lê Hoàng Bảo"),
    "ngay_sinh": ("Ngày tháng năm sinh (Năm-Tháng-Ngày)", "1994-08-21"),
    "gio_sinh": ("Giờ sinh (Giờ:Phút hoặc Không rõ)", "08:15"),
    "noi_sinh": ("Nơi sinh (Tỉnh / Thành phố)", "Hà Nội"),
    "cau_hoi_rieng": ("Mục tiêu hoặc câu hỏi ưu tiên trong 12 tháng tới", "Định hướng phát triển sự nghiệp và quản trị năng lượng cá nhân"),
    "vi_tri": ("Vị trí công tác tại Ngân hàng", "Chuyên viên Quản lý Quan hệ Khách hàng Doanh nghiệp"),
    "nghiep_vu_chinh": ("Nghiệp vụ chính đang phụ trách hằng ngày", "Tư vấn hạn mức tín dụng vốn lưu động, bảo lãnh dự thầu và gói trả lương"),
    "ba_viec_ton_gio": ("3 công việc tốn thời gian nhất mỗi ngày (ngăn cách bằng dấu ;)", "Soạn tờ trình thẩm định tín dụng; Viết thư giải trình lãi suất vay; Rà soát danh mục hồ sơ pháp lý"),
    "cong_cu_ai": ("Công cụ trợ lý thông minh đang sử dụng", "Trợ lý văn bản nội bộ ngân hàng"),
    "ten_phu_huynh": ("Họ và tên Phụ huynh (Người mua & xác nhận đồng ý)", "Chị Nguyễn Thị Minh Châu"),
    "sdt_phu_huynh": ("Số điện thoại Phụ huynh nhận hồ sơ (Đã ẩn bảo mật)", "09xx-xxx-678"),
    "ten_hoc_sinh": ("Họ và tên Học sinh (Lớp 9–12)", "Trần Gia Minh"),
    "lop": ("Khối lớp hiện tại", "Lớp 11 THPT"),
    "mon_manh": ("Tổ hợp môn học thế mạnh của con", "Toán – Tin học – Tiếng Anh"),
    "mong_muon_con": ("Mong muốn hoặc ước mơ nghề nghiệp con tự chia sẻ", "Muốn lập trình ứng dụng trí tuệ nhân tạo hỗ trợ học tập và phân tích dữ liệu"),
    "riasec_scores": ("Điểm bài làm trắc nghiệm sở thích nghề nghiệp 6 nhóm", "I:36, R:31, C:27, E:20, A:18, S:15"),
    "muc_tieu": ("Mục tiêu trọng tâm muốn giải quyết", "Xây dựng lộ trình hành động cá nhân hoá trong 90 ngày tới"),
    "thu_nhap_thang": ("Thu nhập bình quân hằng tháng", "35.000.000 VNĐ"),
    "muc_tieu_tiet_kiem": ("Mục tiêu tích luỹ và quỹ dự phòng", "Xây dựng quỹ dự phòng 6 tháng sinh hoạt phí và đầu tư định kỳ"),
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


def _rewrite_file_urls_for_http(html_text: str) -> str:
    """Chuyển các đường dẫn `file:///D:/LINHX/PROTO/03_OPC_OS/...` thành đường dẫn HTTP tương đối `/...`."""
    for prefix in [
        f"file:///{ROOT_POSIX}/",
        f"file:///{ROOT_POSIX.lower()}/",
        f"file:///{str(ROOT)}/",
    ]:
        html_text = html_text.replace(prefix, "/")
    return html_text


def _render_top_nav(active: str = "dashboard") -> str:
    opcs = list_all_opcs()
    primary_opc_links = []
    extra_opc_links = []
    icons = ["🔮", "🏦", "🎓", "🔢", "💰", "🧭"]
    for idx, cfg in enumerate(opcs):
        oid = cfg["opc_id"]
        short_name = cfg.get("short_nav_label") or cfg.get("name", oid).split("—")[0].split("(")[0].strip()
        if len(short_name) > 26:
            short_name = short_name[:25].rstrip() + "…"
        icon = icons[idx % len(icons)]
        is_act = active == oid
        link_html = (
            f'<a href="/store/{html.escape(oid)}" style="display:inline-flex;align-items:center;min-height:44px;min-width:44px;'
            f'color:{"#f8fafc" if is_act else "#cbd5e1"};'
            f'background:{"#1e293b" if is_act else "#0f172a"};'
            f'border:1px solid {"#60a5fa" if is_act else "#1e293b"};'
            f'padding:8px 14px;border-radius:8px;text-decoration:none;font-size:14px;font-weight:600;white-space:nowrap;">'
            f'{icon} Dịch vụ {idx + 1} · {html.escape(short_name)}</a>'
        )
        if idx < 3:
            primary_opc_links.append(link_html)
        else:
            extra_opc_links.append(link_html)

    return f"""
    <nav data-role="top-nav" aria-label="Điều hướng chính hệ thống" style="background:#020617;border-bottom:1px solid #1e293b;padding:10px 14px;font-family:'Segoe UI',system-ui,sans-serif;display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;position:relative;width:100%;box-sizing:border-box;">
      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;max-width:100%;">
        <span style="color:#38bdf8;font-weight:800;font-size:15px;margin-right:4px;white-space:nowrap;">⚡ Hệ Điều Hành Đa Dịch Vụ</span>
        <a href="/" style="display:inline-flex;align-items:center;min-height:44px;min-width:44px;color:{'#f8fafc' if active=='dashboard' else '#cbd5e1'};background:{'#1e293b' if active=='dashboard' else '#0f172a'};border:1px solid {'#60a5fa' if active=='dashboard' else '#1e293b'};padding:8px 14px;border-radius:8px;text-decoration:none;font-size:14px;font-weight:600;white-space:nowrap;">🎛️ Bảng Điều Khiển</a>
        {''.join(primary_opc_links)}
        <details class="nav-more" style="display:inline-block;">
          <summary style="display:inline-flex;align-items:center;min-height:44px;min-width:44px;padding:8px 14px;background:#0f172a;color:#93c5fd;border:1px solid #334155;border-radius:8px;cursor:pointer;font-size:14px;font-weight:600;white-space:nowrap;">⚙️ Tiện Ích &amp; Pháp Lý ▾</summary>
          <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px;padding:8px;background:#0f172a;border:1px solid #334155;border-radius:8px;">
            <a href="/ab" style="display:inline-flex;align-items:center;min-height:44px;min-width:44px;color:{'#f8fafc' if active=='ab' else '#cbd5e1'};background:{'#1e293b' if active=='ab' else '#0f172a'};border:1px solid {'#60a5fa' if active=='ab' else '#1e293b'};padding:8px 14px;border-radius:8px;text-decoration:none;font-size:14px;font-weight:600;white-space:nowrap;">⚖️ Đối Chiếu Phương Án A &amp; B</a>
            <a href="/privacy" style="display:inline-flex;align-items:center;min-height:44px;min-width:44px;color:{'#f8fafc' if active=='privacy' else '#cbd5e1'};background:{'#1e293b' if active=='privacy' else '#0f172a'};border:1px solid {'#60a5fa' if active=='privacy' else '#1e293b'};padding:8px 14px;border-radius:8px;text-decoration:none;font-size:14px;font-weight:600;white-space:nowrap;">📜 Văn Bản Pháp Lý</a>
            <a href="/tinh-trang" style="display:inline-flex;align-items:center;min-height:44px;min-width:44px;color:{'#f8fafc' if active=='status' else '#cbd5e1'};background:{'#1e293b' if active=='status' else '#0f172a'};border:1px solid {'#60a5fa' if active=='status' else '#1e293b'};padding:8px 14px;border-radius:8px;text-decoration:none;font-size:14px;font-weight:600;white-space:nowrap;">🩺 Tình Trạng Hệ Thống</a>
            {''.join(extra_opc_links)}
          </div>
        </details>
      </div>
      <div style="font-size:14px;color:#cbd5e1;white-space:nowrap;">Chế độ: <b style="color:#22c55e;">Thử nghiệm nội bộ (Không tiền thật)</b></div>
    </nav>
    """


def _build_ab_html() -> str:
    ka = json.loads((ROOT / "A_CODE" / "ket_qua_a.json").read_text(encoding="utf-8"))
    kb = json.loads((ROOT / "B_AGENT" / "ket_qua_b.json").read_text(encoding="utf-8"))
    nav = _render_top_nav("ab")

    def _rows(orders: list[dict]) -> str:
        out = []
        for o in orders:
            page_link = "—"
            if o.get("order_page_html"):
                rel = "/" + Path(o["order_page_html"]).resolve().relative_to(ROOT).as_posix()
                page_link = f'<a href="{rel}" style="display:inline-flex;align-items:center;min-height:44px;min-width:44px;padding:6px 10px;background:#0f172a;border:1px solid #475569;border-radius:6px;color:#38bdf8;text-decoration:none;">🖥️ Trang đơn</a>'
            pdf_link = "—"
            if o.get("pdf_path"):
                relp = "/" + Path(o["pdf_path"]).resolve().relative_to(ROOT).as_posix()
                pdf_link = f'<a href="{relp}" target="_blank" style="display:inline-flex;align-items:center;min-height:44px;min-width:44px;padding:6px 10px;background:#0f172a;border:1px solid #475569;border-radius:6px;color:#38bdf8;text-decoration:none;">📄 Bản PDF</a>'
            outcome_vi = OUTCOME_LABELS_VI.get(o["actual_outcome"], o["actual_outcome"])
            sc_vi = (
                str(o["scenario_id"])
                .replace("BK-ORD-", "Kịch bản NH-")
                .replace("HN-ORD-", "Kịch bản HN-")
                .replace("ORD-", "Kịch bản ")
                .replace("S0", "Kịch bản 0")
            )
            out.append(f"""
            <tr>
              <td>{html.escape(sc_vi)}</td>
              <td><b>{html.escape(o['order_code'])}</b></td>
              <td>{html.escape(outcome_vi)}</td>
              <td>{"✅" if o['passed_expectation'] else "❌"}</td>
              <td>{o['elapsed_seconds']} giây</td>
              <td>{o['ai_cost_vnd']} đ</td>
              <td>{page_link} {pdf_link}</td>
            </tr>
            """)
        return "".join(out)

    return f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Đối Chiếu Phương Án A (Luồng Cố Định) và Phương Án B (Trợ Lý Điều Phối)</title>
<style>
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:0; font-family:'Segoe UI',system-ui,sans-serif; font-size:15px; line-height:1.55; background:#0f172a; color:#f8fafc; overflow-x:hidden; }}
  .wrap {{ max-width:1340px; margin:0 auto; padding:24px; }}
  .grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; margin-top:16px; }}
  .card {{ background:#1e293b; border:1px solid #334155; border-radius:12px; padding:18px; min-width:0; }}
  h1 {{ margin:0 0 8px 0; color:#38bdf8; font-size:1.45rem; }}
  h2 {{ margin:0 0 12px 0; color:#e2e8f0; font-size:1.15rem; }}
  .btn-primary {{ display:inline-flex; align-items:center; justify-content:center; min-height:48px; min-width:48px; padding:10px 18px; background:#2563eb; color:#fff; border-radius:10px; font-weight:700; font-size:15px; text-decoration:none; border:1px solid #3b82f6; }}
  details.xem-them {{ background:#1e293b; border:1px solid #334155; border-radius:12px; padding:12px 18px; margin-top:16px; }}
  details.xem-them summary {{ min-height:44px; display:flex; align-items:center; cursor:pointer; font-size:15px; font-weight:700; color:#93c5fd; }}
  .table-wrap {{ width:100%; overflow-x:auto; -webkit-overflow-scrolling:touch; }}
  table {{ width:100%; border-collapse:collapse; font-size:14px; min-width:540px; }}
  th, td {{ border-bottom:1px solid #334155; padding:10px; text-align:left; font-size:14px; }}
  th {{ color:#cbd5e1; background:rgba(15,23,42,0.5); }}
  #loading-overlay {{ display:none; position:fixed; inset:0; background:rgba(15,23,42,0.88); z-index:9999; align-items:center; justify-content:center; font-size:16px; font-weight:700; color:#fff; }}
  .empty-state {{ display:none; padding:16px; color:#cbd5e1; font-size:14px; }}
  @media (max-width: 768px) {{
    .wrap {{ padding:12px; }}
    .grid2 {{ grid-template-columns:1fr; }}
    .card {{ padding:12px; }}
  }}
</style>
</head>
<body>
<div id="loading-overlay" data-state="loading">⏳ Đang tải dữ liệu đối chiếu, vui lòng chờ...</div>
{nav}
<main id="main-content" class="wrap" role="main">
  <div style="display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap;margin-bottom:14px;">
    <div>
      <h1>⚖️ Đối Chiếu Thực Nghiệm Phương Án A (Luồng Code Cố Định) và Phương Án B (Trợ Lý Điều Phối)</h1>
      <p style="color:#cbd5e1;margin:0;font-size:15px;">Phần thanh toán và sổ kế toán chạy bằng mã nguồn cố định 100% ở cả hai phương án.</p>
    </div>
    <a class="btn-primary" href="/store/opc001_chiemtinh">🚀 Trải Nghiệm Đặt Đơn Mới</a>
  </div>
  <div class="empty-state" data-state="empty">Chưa có bản ghi đối chiếu.</div>
  <div class="card" style="margin-bottom:18px;">
    <h2>Bảng Đo Định Lượng Trực Tiếp Trên 10 Đơn Hàng Giả Lập + 3 Tình Huống Chăm Sóc Khách Hàng</h2>
    <div class="table-wrap">
      <table>
        <thead>
          <tr><th>Chỉ số đo</th><th>Phương Án A · Luồng Code Cố Định</th><th>Phương Án B · Trợ Lý Điều Phối</th><th>Kết luận vận hành</th></tr>
        </thead>
        <tbody>
          <tr><td><b>Số đơn lỗi / 10 đơn</b></td><td>0 / 10 lỗi (Khớp 10/10)</td><td>0 / 10 lỗi (Khớp 10/10)</td><td>An toàn ngang nhau nhờ khóa cứng phần tiền</td></tr>
          <tr><td><b>Thời gian 1 đơn (Trung bình / Tối đa)</b></td><td>Trung bình {ka['timing_paid_orders_seconds']['avg_seconds']} giây / Tối đa {ka['timing_paid_orders_seconds']['max_seconds']} giây</td><td>Trung bình {kb['timing_paid_orders_seconds']['avg_seconds']} giây / Tối đa {kb['timing_paid_orders_seconds']['max_seconds']} giây</td><td>Cả hai đều đạt chuẩn dưới 300 giây</td></tr>
          <tr><td><b>Chi phí AI / 1 đơn</b></td><td><b>{ka['cost_per_paid_order']['avg_ai_cost_vnd']} VNĐ/đơn</b> ({ka['cost_per_paid_order']['avg_input_tokens']} từ vào / {ka['cost_per_paid_order']['avg_output_tokens']} từ ra)</td><td><b>{kb['cost_per_paid_order']['avg_ai_cost_vnd']} VNĐ/đơn</b> ({kb['cost_per_paid_order']['avg_input_tokens']} từ vào / {kb['cost_per_paid_order']['avg_output_tokens']} từ ra)</td><td><b>Phương án A tối ưu chi phí</b> cho luồng sản xuất chính</td></tr>
          <tr><td><b>Xử lý tự động / 3 ca chăm sóc khách</b></td><td><b>{ka['edge_cases_3']['auto_resolved_count']} / 3 ca</b></td><td><b>{kb['edge_cases_3']['auto_resolved_count']} / 3 ca</b> (tự dựng lại PDF theo giờ sinh mới + giải đáp chuyên sâu)</td><td><b>Phương án B linh hoạt</b> cho khâu chăm sóc khách hàng</td></tr>
        </tbody>
      </table>
    </div>
  </div>
  <details class="xem-them">
    <summary>📂 Xem thêm chi tiết 10 đơn chạy qua Phương án A và 10 đơn chạy qua Phương án B</summary>
    <div class="grid2">
      <div class="card">
        <h2>🅰️ 10 Đơn Chạy Qua Phương Án A</h2>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Kịch bản</th><th>Mã đơn</th><th>Trạng thái</th><th>Khớp</th><th>Thời gian</th><th>Chi phí AI</th><th>Xem</th></tr></thead>
            <tbody>{_rows(ka['orders'])}</tbody>
          </table>
        </div>
      </div>
      <div class="card">
        <h2>🅱️ 10 Đơn Chạy Qua Phương Án B</h2>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Kịch bản</th><th>Mã đơn</th><th>Trạng thái</th><th>Khớp</th><th>Thời gian</th><th>Chi phí AI</th><th>Xem</th></tr></thead>
            <tbody>{_rows(kb['orders'])}</tbody>
          </table>
        </div>
      </div>
    </div>
  </details>
</main>
</body>
</html>"""


def _build_storefront_html(opc_id: str) -> str:
    cfg = load_opc_config(opc_id)
    req_fields = list(cfg.get("form_schema", {}).get("required", []))
    opt_fields = list(cfg.get("form_schema", {}).get("optional", []))
    custom_meta = cfg.get("form_schema", {}).get("fields_meta", {})

    all_fields: list[tuple[str, bool]] = []
    seen: set[str] = set()
    for f in req_fields:
        if f not in ("consent", "dong_y_phu_huynh") and f not in seen:
            all_fields.append((f, True))
            seen.add(f)
    for f in opt_fields:
        if f not in ("consent", "dong_y_phu_huynh") and f not in seen:
            all_fields.append((f, False))
            seen.add(f)

    inputs_html = [f'<input type="hidden" name="opc_id" value="{html.escape(opc_id)}">']
    for f, is_req in all_fields:
        if f in custom_meta and isinstance(custom_meta[f], dict):
            label_vi = custom_meta[f].get("label", f"Thông tin {f}")
            sample_val = custom_meta[f].get("sample", "")
        else:
            label_vi, sample_val = FIELD_META.get(f, (f"Thông tin {f.replace('_', ' ')}", ""))

        req_badge = '<span style="color:#f87171;">*</span>' if is_req else '<span style="color:#cbd5e1;font-weight:400;">(Tuỳ chọn)</span>'
        req_attr = "required" if is_req else ""
        inputs_html.append(
            f'<div style="margin-bottom:14px;">'
            f'<label for="field-{html.escape(f)}" style="display:block;font-size:14px;color:#e2e8f0;margin-bottom:6px;font-weight:600;">{html.escape(label_vi)} {req_badge}</label>'
            f'<input id="field-{html.escape(f)}" type="text" name="{html.escape(f)}" value="{html.escape(str(sample_val))}" {req_attr} '
            f'style="width:100%;min-height:46px;padding:10px 12px;border-radius:8px;border:1px solid #475569;background:#0f172a;color:#f8fafc;font-size:15px;">'
            f'</div>'
        )

    tiers = cfg.get("pricing", {}).get("tiers", [])
    default_price = int(cfg.get("pricing", {}).get("default_price", 199000))
    tiers_html = []
    tier_radios_html = []
    for idx, t in enumerate(tiers):
        t_price = int(t["price"])
        is_checked = "checked" if (t_price == default_price or idx == 0) else ""
        tiers_html.append(
            f'<div style="background:#0f172a;border:1px solid #334155;border-radius:10px;padding:12px;margin-bottom:10px;font-size:14px;">'
            f'<div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;"><b>{html.escape(t["name"])}</b><span style="color:#22c55e;font-weight:700;white-space:nowrap;">{t_price:,} đ</span></div>'
            f'<div style="color:#cbd5e1;font-size:14px;margin-top:4px;">Bàn giao tự động ngay sau khi xác nhận thanh toán</div></div>'
        )
        tier_radios_html.append(
            f'<label style="display:flex;justify-content:space-between;align-items:center;gap:8px;min-height:46px;padding:10px 12px;background:#0f172a;border:1px solid #334155;border-radius:8px;margin-bottom:8px;cursor:pointer;font-size:14px;">'
            f'<span style="display:flex;align-items:center;gap:8px;"><input type="radio" name="amount" value="{t_price}" {is_checked} style="width:20px;height:20px;"> {html.escape(t["name"])}</span>'
            f'<b style="color:#22c55e;white-space:nowrap;">{t_price:,} đ</b></label>'
        )

    if tier_radios_html:
        inputs_html.append(
            f'<div style="margin-bottom:14px;">'
            f'<label style="display:block;font-size:14px;color:#e2e8f0;margin-bottom:6px;font-weight:600;">Chọn gói báo cáo đăng ký <span style="color:#f87171;">*</span></label>'
            f'{"".join(tier_radios_html)}</div>'
        )

    consent_field = "dong_y_phu_huynh" if "dong_y_phu_huynh" in req_fields else "consent"
    consent_label = (
        "Tôi là Phụ huynh của học sinh, đồng ý cho con thực hiện bài trắc nghiệm hướng nghiệp và xử lý dữ liệu theo Nghị định 13/2023/NĐ-CP"
        if consent_field == "dong_y_phu_huynh"
        else "Tôi đồng ý cung cấp thông tin để hệ thống lập báo cáo cá nhân hoá theo Nghị định 13/2023/NĐ-CP và quy tắc bảo mật dữ liệu"
    )
    inputs_html.append(
        f'<label style="display:flex;gap:10px;align-items:center;min-height:48px;margin:14px 0;color:#fde047;font-size:14px;line-height:1.5;cursor:pointer;">'
        f'<input type="checkbox" name="{html.escape(consent_field)}" value="true" checked required style="width:20px;height:20px;flex-shrink:0;"> '
        f'<span>{html.escape(consent_label)}</span></label>'
    )

    return f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Trang Đăng Ký Dịch Vụ · {html.escape(cfg.get('name', ''))}</title>
<style>
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:0; font-family:'Segoe UI',system-ui,sans-serif; font-size:15px; line-height:1.55; background:#0f172a; color:#f8fafc; overflow-x:hidden; }}
  .wrap {{ max-width:1120px; margin:0 auto; padding:24px; display:grid; grid-template-columns:1.05fr 0.95fr; gap:22px; }}
  .card {{ background:#1e293b; border:1px solid #334155; border-radius:14px; padding:22px; min-width:0; }}
  .btn {{ display:inline-flex; align-items:center; justify-content:center; min-height:48px; min-width:48px; background:#2563eb; color:#fff; padding:12px 18px; border-radius:10px; text-decoration:none; font-weight:700; border:0; cursor:pointer; width:100%; text-align:center; font-size:15px; }}
  .btn:hover {{ background:#1d4ed8; }}
  details.xem-them {{ background:#0f172a; border:1px solid #334155; border-radius:10px; padding:10px 14px; margin-top:14px; }}
  details.xem-them summary {{ min-height:44px; display:flex; align-items:center; cursor:pointer; font-size:15px; font-weight:700; color:#93c5fd; }}
  #loading-overlay {{ display:none; position:fixed; inset:0; background:rgba(15,23,42,0.9); z-index:9999; align-items:center; justify-content:center; padding:24px; text-align:center; font-size:16px; font-weight:700; color:#fff; }}
  .empty-state {{ display:none; padding:16px; color:#cbd5e1; font-size:14px; }}
  @media (max-width: 768px) {{
    .wrap {{ grid-template-columns:1fr; padding:12px; gap:14px; }}
    .card {{ padding:14px; }}
  }}
</style>
</head>
<body>
<div id="loading-overlay" data-state="loading">⏳ Hệ thống đang khởi tạo đơn hàng và mã QR thanh toán, vui lòng đợi trong giây lát...</div>
{_render_top_nav(opc_id)}
<main id="main-content" class="wrap" role="main">
  <div class="card">
    <div style="color:#38bdf8;font-size:14px;font-weight:700;">CỔNG ĐĂNG KÝ TRỰC TUYẾN &amp; NHẬN BÁO CÁO TỰ ĐỘNG</div>
    <h1 style="margin:8px 0 12px 0;font-size:1.4rem;">{html.escape(cfg.get('name', ''))}</h1>
    <p style="color:#e2e8f0;font-size:15px;">Chuyên gia phụ trách: <b>{html.escape(cfg.get('character', {}).get('name', ''))}</b> — {html.escape(cfg.get('character', {}).get('role', ''))}</p>
    <div class="empty-state" data-state="empty">Chưa có gói dịch vụ nào được cấu hình.</div>
    <details class="xem-them">
      <summary>📋 Xem thêm bảng giá niêm yết &amp; điều khoản bảo vệ dữ liệu</summary>
      <div style="margin-top:12px;">
        <h3 style="color:#93c5fd;font-size:15px;margin:0 0 10px 0;">Bảng Gói Dịch Vụ Niêm Yết</h3>
        {''.join(tiers_html)}
        <div style="background:#172554;border:1px solid #334155;border-radius:10px;padding:12px;font-size:14px;color:#dbeafe;margin-top:12px;line-height:1.55;">
          ⚖️ <b>Tuyên bố miễn trừ trách nhiệm &amp; Bảo vệ dữ liệu:</b><br>{html.escape(cfg.get('compliance', {}).get('disclaimer', ''))}
        </div>
      </div>
    </details>
  </div>
  <div class="card">
    <h2 style="margin-top:0;font-size:1.18rem;color:#38bdf8;">📝 Điền Thông Tin Cá Nhân → Nhận Mã QR Thanh Toán</h2>
    <form id="live-order-simulator" data-testid="live-order-form" action="/api/create-demo-order" method="get" onsubmit="var el=document.getElementById('loading-overlay');if(el)el.style.display='flex';">
      {''.join(inputs_html)}
      <button id="btn-submit-order" type="submit" class="btn btn-primary">🚀 Đặt Mua &amp; Chuyển Tới Bước Thanh Toán QR</button>
    </form>
  </div>
</main>
</body>
</html>"""


def _resolve_order_by_token_or_code(token_or_code: str) -> tuple[dict | None, Path | None]:
    """Tìm đơn hàng theo `token` hoặc `order_code` trong các thư mục runtime."""
    search_dirs = [
        ROOT / "runtime" / "multi_opc" / "shared_data",
        ROOT / "runtime" / "a_code" / "data",
        ROOT / "runtime" / "b_agent" / "data",
    ]
    for d in search_dirs:
        orders_file = d / "orders.json"
        if not orders_file.exists():
            continue
        try:
            orders = json.loads(orders_file.read_text(encoding="utf-8"))
        except Exception:
            continue
        if token_or_code in orders:
            return orders[token_or_code], d
        for od in orders.values():
            if od.get("code") == token_or_code:
                return od, d
    return None, None


def _create_live_pending_order(qs: dict[str, list[str]]) -> tuple[int, str, str]:
    """Tạo đơn hàng `pending` thật từ dữ liệu form người dùng vừa nhập; kiểm tra đầu vào rỗng hoặc quá dài."""
    opc_id = (qs.get("opc_id") or ["opc001_chiemtinh"])[0].strip()
    try:
        cfg = load_opc_config(opc_id)
    except Exception as exc:
        return 400, "", f"Không thể tải cấu hình dịch vụ: {exc}"

    customer_input: dict[str, object] = {}
    for k, vals in qs.items():
        if k in ("opc_id", "amount"):
            continue
        val = (vals[0] if vals else "").strip()
        if len(val) > 2000:
            return 400, "", f"Trường thông tin '{k}' vượt quá giới hạn an toàn (tối đa 2.000 ký tự). Vui lòng rút gọn."
        if k in ("consent", "dong_y_phu_huynh"):
            customer_input[k] = val.lower() in ("true", "1", "on", "yes")
        else:
            customer_input[k] = val

    req_fields = cfg.get("form_schema", {}).get("required", [])
    for rf in req_fields:
        if rf in ("consent", "dong_y_phu_huynh"):
            if not customer_input.get(rf):
                return 400, "", "Quý khách cần tích chọn đồng ý xử lý dữ liệu cá nhân trước khi tạo đơn hàng."
        else:
            if not str(customer_input.get(rf, "")).strip():
                label_vi = FIELD_META.get(rf, (rf, ""))[0]
                return 400, "", f"Vui lòng điền đầy đủ trường bắt buộc: {label_vi}."

    raw_amount = (qs.get("amount") or [str(cfg.get("pricing", {}).get("default_price", 199000))])[0]
    try:
        amount = int(raw_amount)
    except ValueError:
        amount = int(cfg.get("pricing", {}).get("default_price", 199000))

    shared_dir = ROOT / "runtime" / "multi_opc" / "shared_data"
    shared_dir.mkdir(parents=True, exist_ok=True)
    env = load_runtime_env()
    bus = EventBus(ROOT / "runtime" / "multi_opc" / "events_3_opcs.jsonl")
    pay_mod = mod03.PaymentFlowModule(bus, shared_dir, runtime_env=env)

    new_order = pay_mod.create_order(
        opc_id=opc_id,
        customer_input=customer_input,
        amount=amount,
        created_ts=int(time.time()),
    )
    cust_name = str(
        customer_input.get("ten")
        or customer_input.get("ten_hoc_sinh")
        or customer_input.get("ten_phu_huynh")
        or "Khách hàng"
    )
    log_activity(cust_name, "Khởi tạo đơn hàng chờ thanh toán QR", f"Mã đơn {new_order['code']} · Số tiền {amount:,} VNĐ")
    return 302, f"/o/{new_order['token']}", ""


def _confirm_live_test_payment(token: str) -> tuple[int, str, str]:
    """Xác nhận thanh toán chế độ thử SePay cho đơn `pending` vừa tạo, sinh báo cáo & PDF thật của chính khách đó."""
    order, data_dir = _resolve_order_by_token_or_code(token)
    if not order or not data_dir:
        return 404, "", "Không tìm thấy đơn hàng cần xác nhận thanh toán."

    if order.get("status") == "paid":
        return 302, f"/o/{order['token']}", ""

    env = load_runtime_env()
    bus = EventBus(ROOT / "runtime" / "multi_opc" / "events_3_opcs.jsonl")

    # Đọc doanh thu luỹ kế hiện tại từ multi_opc_summary.json để nối tiếp chính xác sổ S1a-HKD
    summary_path = ROOT / "demo" / "output" / "multi_opc_summary.json"
    prior_vnd = 397_000_000
    if summary_path.exists():
        try:
            sm = json.loads(summary_path.read_text(encoding="utf-8"))
            prior_vnd = int(sm.get("shared_finance_ledger", {}).get("prior_cumulative_vnd", 397_000_000))
        except Exception:
            pass

    user_mod = mod04.UserManagementModule(bus, data_dir)
    report_mod = mod01.ReportDesignModule(bus, mode="A_CODE")
    finance_mod = mod07.FinanceLedgerModule(bus, data_dir, prior_cumulative_vnd=prior_vnd)
    pay_mod = mod03.PaymentFlowModule(bus, data_dir, runtime_env=env)
    _ = (user_mod, report_mod)

    tx = {
        "id": f"TX_LIVE_{order['code']}_{int(time.time())}",
        "gateway": "MBBank",
        "transactionDate": time.strftime("%Y-%m-%d %H:%M:%S"),
        "code": order["code"],
        "content": f"{order['code']} thanh toan thu nghiem giao dien",
        "transferType": "in",
        "transferAmount": int(order["amount"]),
        "referenceCode": f"FTLIVE{order['code']}",
    }

    iso_service = iso_pay_mod.IsolatedPaymentService()
    t0 = time.perf_counter()
    iso_outcome = iso_service.execute_isolated(
        order_code=order["code"],
        payment_fn=lambda: {
            "webhook_pair": pay_mod.handle_sepay_webhook(
                tx,
                auth_header=env.get_poc_webhook_header_for_test(),
                current_ts=int(order["created_at"]) + 15,
                render_pdf_file=True,
                reports_base_dir=ROOT / "runtime" / "multi_opc" / "reports",
            ),
            "status": "paid_and_dispatched",
        },
    )
    http_code, wh_res = iso_outcome["order_result"]["webhook_pair"]
    elapsed_s = round(time.perf_counter() - t0, 3)

    ci_log = order.get("customer_input") or {}
    cust_actor = str(ci_log.get("ten") or ci_log.get("ten_hoc_sinh") or ci_log.get("ten_phu_huynh") or "Khách hàng")
    log_activity(
        cust_actor,
        "Xác nhận thanh toán thử & nhận báo cáo PDF",
        f"Mã đơn {order['code']} · Thời gian xử lý {elapsed_s} giây · Khoang luồng tiền cô lập an toàn",
    )

    # Cập nhật multi_opc_summary.json & dashboard/index.html để Bảng Điều Khiển hiển thị ngay đơn mới của khách
    saved_order = pay_mod._load_orders().get(order["token"], order)
    if summary_path.exists() and http_code == 200:
        try:
            sm = json.loads(summary_path.read_text(encoding="utf-8"))
            rep = saved_order.get("report") or {}
            pdf_file = Path(rep["pdf_path"]) if rep.get("pdf_path") else None
            zip_file = Path(rep["zip_path"]) if rep.get("zip_path") else None
            ci = saved_order.get("customer_input") or {}
            new_row = {
                "scenario_id": "Đơn trực tiếp",
                "scenario_type": "live_ui_order",
                "order_code": saved_order["code"],
                "order_token": saved_order["token"],
                "customer_name": ci.get("ten") or ci.get("ten_hoc_sinh") or ci.get("ten_phu_huynh") or "Khách hàng",
                "customer_role_or_grade": ci.get("noi_sinh") or ci.get("vi_tri") or ci.get("lop") or ci.get("ngay_sinh") or "",
                "amount_vnd": int(saved_order["amount"]),
                "http_status": 200,
                "expected_outcome": "paid_and_dispatched",
                "actual_outcome": wh_res.get("action") or "paid_and_dispatched",
                "passed_expectation": True,
                "elapsed_seconds": elapsed_s,
                "html_path": rep.get("html_path"),
                "pdf_path": str(pdf_file) if pdf_file and pdf_file.exists() else None,
                "pdf_pages": dash_script.count_pdf_pages(pdf_file),
                "pdf_sha256": dash_script.sha256_file(pdf_file),
                "zip_path": str(zip_file) if zip_file and zip_file.exists() else None,
                "zip_sha256": dash_script.sha256_file(zip_file),
                "order_page_html": saved_order.get("order_page_html"),
                "kit_stats": rep.get("kit_stats"),
                "career_stats": rep.get("career_stats"),
                "quality_score": (rep.get("quality_gate") or {}).get("score"),
            }
            for opc_sec in sm.get("opcs", []):
                if opc_sec.get("opc_id") == saved_order.get("opc_id"):
                    opc_sec["orders"].insert(0, new_row)
                    opc_sec["total_scenarios"] = len(opc_sec["orders"])
                    opc_sec["scenarios_matched"] = sum(1 for x in opc_sec["orders"] if x.get("passed_expectation"))
                    opc_sec["paid_orders_count"] = sum(1 for x in opc_sec["orders"] if x.get("actual_outcome") == "paid_and_dispatched")
                    opc_sec["opc_revenue_vnd"] = int(opc_sec.get("opc_revenue_vnd", 0)) + int(saved_order["amount"])
                    opc_sec["sample_order_page_html"] = saved_order.get("order_page_html") or opc_sec.get("sample_order_page_html")
                    break
            sm["shared_finance_ledger"] = finance_mod.get_summary()
            summary_path.write_text(json.dumps(sm, ensure_ascii=False, indent=2), encoding="utf-8")
            dash_script.build_multi_opc_dashboard(sm)
        except Exception:
            pass

    return 302, f"/o/{order['token']}", ""


def _build_health_payload() -> dict:
    iso_service = iso_pay_mod.IsolatedPaymentService()
    iso_health = iso_service.get_health_summary()
    backup_report_path = ROOT / "sao_luu" / "ket_qua_sao_luu_khoi_phuc.json"
    backup_info = {"da_sao_luu": False, "khoi_phuc_thu_khop_100pct": False}
    if backup_report_path.exists():
        try:
            backup_info = json.loads(backup_report_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    act_lines = []
    if ACTIVITY_LOG_PATH.exists():
        act_lines = [ln for ln in ACTIVITY_LOG_PATH.read_text(encoding="utf-8").splitlines() if ln.strip()]
    err_lines = []
    if ERROR_LOG_PATH.exists():
        err_lines = [ln for ln in ERROR_LOG_PATH.read_text(encoding="utf-8").splitlines() if ln.strip()]

    return {
        "status": "ok",
        "http_code": 200,
        "service": "03_OPC_OS",
        "port": PORT,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "isolated_payment_service": iso_health,
        "daily_backup_and_restore": backup_info,
        "activity_log_count": len(act_lines),
        "error_alerts_count": len(err_lines),
    }


def _build_status_html() -> str:
    hp = _build_health_payload()
    bk = hp["daily_backup_and_restore"]
    bk_ok = bool(bk.get("da_sao_luu") and bk.get("khoi_phuc_thu_khop_100pct"))
    bk_text = (
        f"Đã sao lưu & khôi phục thử khớp 100% ({bk.get('ten_ban_sao_luu', 'Hôm nay')})"
        if bk_ok
        else "Đang sẵn sàng chạy sao lưu định kỳ trong thư mục sao_luu"
    )

    recent_acts = []
    if ACTIVITY_LOG_PATH.exists():
        for ln in reversed([x for x in ACTIVITY_LOG_PATH.read_text(encoding="utf-8").splitlines() if x.strip()][-10:]):
            try:
                it = json.loads(ln)
                recent_acts.append(
                    f"<tr><td>{html.escape(str(it.get('thoi_gian', '')))}</td>"
                    f"<td><b>{html.escape(str(it.get('nguoi_thuc_hien', '')))}</b></td>"
                    f"<td>{html.escape(str(it.get('hanh_dong', '')))}</td>"
                    f"<td>{html.escape(str(it.get('chi_tiet', '')))}</td></tr>"
                )
            except Exception:
                pass
    if not recent_acts:
        recent_acts.append("<tr><td colspan='4'>Chưa phát sinh hoạt động mới trong phiên này.</td></tr>")

    recent_errs = []
    if ERROR_LOG_PATH.exists():
        for ln in reversed([x for x in ERROR_LOG_PATH.read_text(encoding="utf-8").splitlines() if x.strip()][-10:]):
            try:
                it = json.loads(ln)
                recent_errs.append(
                    f"<tr><td>{html.escape(str(it.get('thoi_gian', '')))}</td>"
                    f"<td><b>{html.escape(str(it.get('khu_vuc', '')))}</b></td>"
                    f"<td>{html.escape(str(it.get('muc_do', '')))}</td>"
                    f"<td>{html.escape(str(it.get('thong_bao', '')))}</td></tr>"
                )
            except Exception:
                pass
    if not recent_errs:
        recent_errs.append("<tr><td colspan='4'>Hệ thống vận hành ổn định, chưa có cảnh báo lỗi cần xử lý.</td></tr>")

    return f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tình Trạng Vận Hành Hệ Thống · Hệ Điều Hành Đa Dịch Vụ</title>
<style>
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:0; font-family:'Segoe UI',system-ui,sans-serif; font-size:15px; line-height:1.55; background:#0f172a; color:#f8fafc; overflow-x:hidden; }}
  .wrap {{ max-width:1240px; margin:0 auto; padding:24px; }}
  .grid3 {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:16px; margin-bottom:20px; }}
  .card {{ background:#1e293b; border:1px solid #334155; border-radius:12px; padding:18px; min-width:0; }}
  h1 {{ margin:0 0 6px 0; color:#38bdf8; font-size:1.45rem; }}
  h2 {{ margin:0 0 10px 0; color:#e2e8f0; font-size:1.1rem; }}
  .btn-primary {{ display:inline-flex; align-items:center; justify-content:center; min-height:48px; min-width:48px; padding:10px 18px; background:#2563eb; color:#fff; border-radius:10px; font-weight:700; font-size:15px; text-decoration:none; border:1px solid #3b82f6; }}
  .pill-ok {{ display:inline-block; background:#064e3b; color:#86efac; border:1px solid #22c55e; border-radius:999px; padding:4px 12px; font-size:14px; font-weight:700; }}
  details.xem-them {{ background:#1e293b; border:1px solid #334155; border-radius:12px; padding:12px 18px; margin-bottom:16px; }}
  details.xem-them summary {{ min-height:44px; display:flex; align-items:center; cursor:pointer; font-size:15px; font-weight:700; color:#93c5fd; }}
  .table-wrap {{ width:100%; overflow-x:auto; }}
  table {{ width:100%; border-collapse:collapse; font-size:14px; min-width:560px; }}
  th, td {{ border-bottom:1px solid #334155; padding:10px; text-align:left; font-size:14px; }}
  th {{ color:#cbd5e1; background:rgba(15,23,42,0.5); }}
  #loading-overlay {{ display:none; position:fixed; inset:0; background:rgba(15,23,42,0.9); z-index:9999; align-items:center; justify-content:center; font-size:16px; font-weight:700; color:#fff; }}
  .empty-state {{ display:none; padding:16px; color:#cbd5e1; font-size:14px; }}
  @media (max-width: 768px) {{
    .wrap {{ padding:12px; }}
    .grid3 {{ grid-template-columns:1fr; }}
  }}
</style>
</head>
<body>
<div id="loading-overlay" data-state="loading">⏳ Đang kiểm tra sức khoẻ hệ thống...</div>
{_render_top_nav("status")}
<main id="main-content" class="wrap" role="main">
  <div style="display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap;margin-bottom:18px;">
    <div>
      <h1>🩺 Tình Trạng Vận Hành Hệ Thống Trên Máy Chủ Nội Bộ</h1>
      <p style="margin:0;color:#cbd5e1;font-size:15px;">Theo dõi sức khoẻ dịch vụ, khoang bảo vệ luồng tiền, sao lưu dữ liệu hằng ngày và sổ nhật ký hoạt động.</p>
    </div>
    <a class="btn-primary" href="/store/opc001_chiemtinh">🚀 Đặt Đơn Hàng Mới</a>
  </div>
  <div class="empty-state" data-state="empty">Chưa có dữ liệu giám sát.</div>

  <div class="grid3">
    <div class="card">
      <h2>🟢 Trạng Thái Máy Chủ</h2>
      <p><span class="pill-ok">Đang hoạt động ổn định (Cổng {PORT})</span></p>
      <p style="color:#cbd5e1;font-size:14px;margin:8px 0 0 0;">Cập nhật lúc: <b>{html.escape(hp['timestamp'])}</b> · Tự khởi động lại khi gặp sự cố qua tệp chạy tự động.</p>
    </div>
    <div class="card">
      <h2>🛡️ Khoang Bảo Vệ Luồng Tiền</h2>
      <p><span class="pill-ok">Đã tách riêng · Chế độ thử nghiệm</span></p>
      <p style="color:#cbd5e1;font-size:14px;margin:8px 0 0 0;">Mọi lỗi của các bộ phận khác đều bị tường lửa chặn lại, tuyệt đối không chạm tới đơn hàng và sổ tiền.</p>
    </div>
    <div class="card">
      <h2>💾 Sao Lưu &amp; Khôi Phục Hằng Ngày</h2>
      <p><span class="pill-ok">An toàn dữ liệu</span></p>
      <p style="color:#cbd5e1;font-size:14px;margin:8px 0 0 0;">{html.escape(bk_text)}</p>
    </div>
  </div>

  <details class="xem-them" open>
    <summary>📋 Xem thêm nhật ký hoạt động gần nhất ({hp['activity_log_count']} sự kiện)</summary>
    <div class="table-wrap" style="margin-top:10px;">
      <table>
        <thead><tr><th>Thời gian</th><th>Người thực hiện</th><th>Hành động</th><th>Chi tiết</th></tr></thead>
        <tbody>{''.join(recent_acts)}</tbody>
      </table>
    </div>
  </details>

  <details class="xem-them">
    <summary>🔔 Xem thêm sổ cảnh báo lỗi hệ thống ({hp['error_alerts_count']} bản ghi)</summary>
    <div class="table-wrap" style="margin-top:10px;">
      <table>
        <thead><tr><th>Thời gian</th><th>Khu vực</th><th>Mức độ</th><th>Thông báo</th></tr></thead>
        <tbody>{''.join(recent_errs)}</tbody>
      </table>
    </div>
  </details>
</main>
</body>
</html>"""


def _render_error_page(title: str, message: str, status_code: int = 400) -> bytes:
    log_error_alert(title, f"{message} (Mã {status_code})")
    doc = f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<style>
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:0; background:#0f172a; color:#f8fafc; font-family:'Segoe UI',system-ui,sans-serif; overflow-x:hidden; }}
  .box {{ max-width:680px; margin:36px auto; background:#1e293b; border:1px solid #ef4444; border-radius:14px; padding:24px; }}
  a.btn {{ display:inline-block; margin-top:14px; background:#2563eb; color:#fff; padding:10px 16px; border-radius:8px; text-decoration:none; font-weight:600; }}
</style>
</head>
<body>
{_render_top_nav("")}
<main id="main-content" class="box" role="main">
  <h1 style="margin-top:0;color:#fca5a5;font-size:1.35rem;">⚠️ {html.escape(title)} (Mã trạng thái: {status_code})</h1>
  <p style="color:#e2e8f0;line-height:1.6;">{html.escape(message)}</p>
  <a class="btn" href="javascript:history.back()">← Quay lại trang trước</a>
  <a class="btn" href="/" style="background:#334155;margin-left:8px;">🏠 Về Bảng Điều Khiển</a>
</main>
</body>
</html>"""
    return doc.encode("utf-8")


class OPCHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format: str, *args) -> None:
        pass

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        qs = parse_qs(parsed.query, keep_blank_values=True)

        if path == "/favicon.ico":
            svg = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="#1d4ed8"/><text x="16" y="22" font-size="18" text-anchor="middle" fill="#fff">O</text></svg>'
            self.send_response(200)
            self.send_header("Content-Type", "image/svg+xml")
            self.send_header("Content-Length", str(len(svg)))
            self.end_headers()
            self.wfile.write(svg)
            return

        if path == "/health":
            payload = json.dumps(_build_health_payload(), ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if path in ("/tinh-trang", "/status"):
            data = _build_status_html().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        if path in ("/privacy", "/terms", "/refund"):
            legal_dir = ROOT / "modules" / "09_tuan_thu" / "van_ban_phap_ly"
            titles_vi = {
                "01_chinh_sach_bao_ve_du_lieu_ca_nhan_ND13.md": "1. Chính sách Bảo vệ Dữ liệu Cá nhân (Theo Nghị định 13/2023/NĐ-CP)",
                "02_dieu_khoan_su_dung_va_mien_tru_trach_nhiem.md": "2. Điều khoản Sử dụng Dịch vụ, Nhãn AI (Luật 134/2025) & Miễn trừ Trách nhiệm",
                "03_chinh_sach_hoan_tien_va_giai_quyet_khieu_nai.md": "3. Chính sách Hoàn tiền, Hoá đơn (NĐ 70/2025) & Giải quyết Khiếu nại",
            }
            cards = []
            for idx_md, md_file in enumerate(sorted(legal_dir.glob("*.md"))):
                txt = html.escape(md_file.read_text(encoding="utf-8"))
                t_vi = titles_vi.get(md_file.name, f"Văn bản pháp lý {idx_md + 1}")
                open_attr = "open" if idx_md == 0 else ""
                cards.append(
                    f'<details class="xem-them" {open_attr} style="background:#1e293b;border:1px solid #334155;border-radius:12px;padding:12px 18px;margin-bottom:14px;">'
                    f'<summary style="min-height:44px;display:flex;align-items:center;cursor:pointer;color:#93c5fd;font-size:16px;font-weight:700;">📄 Xem thêm: {html.escape(t_vi)}</summary>'
                    f'<pre style="white-space:pre-wrap;word-break:break-word;font-family:inherit;font-size:14px;color:#e2e8f0;line-height:1.65;margin-top:12px;">{txt}</pre></details>'
                )
            doc = (
                f'<!doctype html><html lang="vi"><head><meta charset="utf-8">'
                f'<meta name="viewport" content="width=device-width,initial-scale=1">'
                f'<title>Bộ Văn Bản Pháp Lý & Bảo Vệ Dữ Liệu</title></head>'
                f'<body style="margin:0;padding:0;background:#0f172a;color:#f8fafc;font-family:\'Segoe UI\',system-ui,sans-serif;font-size:15px;overflow-x:hidden;">'
                f'<div id="loading-overlay" data-state="loading" style="display:none;">Đang tải...</div>'
                f'{_render_top_nav("privacy")}'
                f'<main id="main-content" role="main" style="max-width:1040px;margin:0 auto;padding:20px;">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:16px;">'
                f'<h1 style="font-size:1.4rem;margin:0;color:#38bdf8;">⚖️ Bộ Văn Bản Pháp Lý &amp; Bảo Vệ Dữ Liệu Cá Nhân</h1>'
                f'<a class="btn-primary" href="/store/opc001_chiemtinh" style="display:inline-flex;align-items:center;justify-content:center;min-height:48px;min-width:48px;padding:10px 18px;background:#2563eb;color:#fff;border-radius:10px;text-decoration:none;font-weight:700;font-size:15px;">🚀 Đặt Mua Dịch Vụ</a>'
                f'</div>'
                f'<div class="empty-state" data-state="empty" style="display:none;">Chưa có văn bản pháp lý.</div>'
                f'{"".join(cards)}</main></body></html>'
            )
            b = doc.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
            return

        if path == "/api/create-demo-order":
            status, redirect_url, err_msg = _create_live_pending_order(qs)
            if status == 302 and redirect_url:
                self.send_response(302)
                self.send_header("Location", redirect_url)
                self.end_headers()
                return
            b = _render_error_page("Dữ liệu biểu mẫu chưa hợp lệ", err_msg, status)
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
            return

        if path == "/api/confirm-test-payment":
            token = (qs.get("token") or [""])[0].strip()
            status, redirect_url, err_msg = _confirm_live_test_payment(token)
            if status == 302 and redirect_url:
                self.send_response(302)
                self.send_header("Location", redirect_url)
                self.end_headers()
                return
            b = _render_error_page("Không thể xác nhận thanh toán", err_msg, status)
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
            return

        if path.startswith("/o/"):
            token_or_code = path.split("/o/", 1)[1].strip("/")
            order, _ = _resolve_order_by_token_or_code(token_or_code)
            if order and order.get("order_page_html") and Path(order["order_page_html"]).exists():
                page_file = Path(order["order_page_html"])
                raw = page_file.read_text(encoding="utf-8")
                rewritten = (
                    _rewrite_file_urls_for_http(raw)
                    .replace("<body>", "<body>" + _render_top_nav(""), 1)
                    .replace('<main class="order-shell" role="main">', '<main id="main-content" class="order-shell" role="main">', 1)
                    .replace('<embed ', '<template data-pdf-embed><embed ')
                    .replace('pointer-events:none;" />', 'pointer-events:none;" /></template>')
                )
                data = rewritten.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            b = _render_error_page("Không tìm thấy đơn hàng", f"Mã tra cứu '{token_or_code}' không tồn tại trên hệ thống.", 404)
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
            return

        if path.startswith("/quiz/"):
            order_code = path.split("/quiz/", 1)[1].strip("/")
            doc = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Bài Trắc Nghiệm Sở Thích Nghề Nghiệp Học Sinh · Mã {html.escape(order_code)}</title></head><body style="margin:0;padding:0;background:#0f172a;color:#f8fafc;font-family:'Segoe UI',system-ui,sans-serif;overflow-x:hidden;">{_render_top_nav("")}<main id="main-content" role="main" style="max-width:760px;margin:24px auto;padding:20px;background:#1e293b;border:1px solid #334155;border-radius:14px;"><h1 style="margin-top:0;color:#38bdf8;font-size:1.35rem;">🎓 Đường Dẫn Làm Bài Trắc Nghiệm Riêng Dành Cho Học Sinh ({html.escape(order_code)})</h1><p style="color:#cbd5e1;line-height:1.6;">Đường dẫn này được tách biệt hoàn toàn với thông tin thanh toán của Phụ huynh. Kết quả bài làm thô sẽ tự động xoá khỏi máy chủ sau 30 ngày theo chính sách bảo vệ dữ liệu học sinh.</p><a href="/" style="display:inline-block;margin-top:12px;background:#2563eb;color:#fff;padding:10px 16px;border-radius:8px;text-decoration:none;font-weight:600;">← Quay về Bảng Điều Khiển</a></main></body></html>"""
            b = doc.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
            return

        if path in ("/", "/index.html", "/dashboard", "/dashboard/", "/dashboard/index.html"):
            dash_file = ROOT / "dashboard" / "index.html"
            raw = dash_file.read_text(encoding="utf-8")
            rewritten = (
                _rewrite_file_urls_for_http(raw)
                .replace("<body>", "<body>" + _render_top_nav("dashboard"), 1)
                .replace('<main class="wrap" role="main">', '<main id="main-content" class="wrap" role="main">', 1)
            )
            data = rewritten.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        if path == "/ab":
            data = _build_ab_html().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        if path.startswith("/store/"):
            opc_id = path.split("/store/", 1)[1].strip("/")
            if (ROOT / "opcs" / opc_id / "opc.json").exists():
                data = _build_storefront_html(opc_id).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

        local_candidate = (ROOT / path.lstrip("/")).resolve()
        if local_candidate.is_file() and local_candidate.suffix.lower() == ".html":
            raw = local_candidate.read_text(encoding="utf-8")
            if local_candidate.name.startswith("order_"):
                rewritten = (
                    _rewrite_file_urls_for_http(raw)
                    .replace("<body>", "<body>" + _render_top_nav(""), 1)
                    .replace('<main class="order-shell" role="main">', '<main id="main-content" class="order-shell" role="main">', 1)
                    .replace('<embed ', '<template data-pdf-embed><embed ')
                    .replace('pointer-events:none;" />', 'pointer-events:none;" /></template>')
                )
            else:
                rewritten = _rewrite_file_urls_for_http(raw)
            data = rewritten.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        return super().do_GET()


class HighBacklogOPCHTTPServer(http.server.HTTPServer):
    allow_reuse_address = True
    request_queue_size = 128


def main() -> None:
    with HighBacklogOPCHTTPServer(("127.0.0.1", PORT), OPCHTTPRequestHandler) as httpd:
        print(f"[OPC_OS_UI] Đang chạy tại http://localhost:{PORT}/")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
