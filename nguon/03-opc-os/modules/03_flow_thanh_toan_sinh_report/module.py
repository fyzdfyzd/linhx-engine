"""Module 03: Flow Thanh toán VietQR / SePay -> Phát sự kiện sinh Report & Hiển thị PDF trên trang.

LUẬT AN TOÀN SẮT:
- Module này LUÔN chạy bằng code cố định tất định 100% cho cả Phương án A và Phương án B.
- Khoá SePay và số tài khoản đọc từ `03_OPC_OS/.env` qua `core.env_loader.load_runtime_env()`, tuyệt đối không ghi ra log/file.
- Bậc 1 MVP nội bộ (Cổng A): Hỗ trợ đầy đủ bước chờ thanh toán QR (chế độ thử không tiền thật) rồi mới sinh báo cáo cho chính khách hàng vừa điền; 0 chữ kỹ thuật lộ ra; tương thích màn hình 390px.
"""
from __future__ import annotations

import argparse
import html
import json
import secrets
import sys
import threading
import time
from pathlib import Path
from urllib.parse import quote

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.env_loader import RuntimeEnv, load_runtime_env  # noqa: E402
from core.event_bus import Event, EventBus  # noqa: E402
from core.opc_loader import load_opc_config  # noqa: E402

STATUS_LABELS_VI = {
    "pending": "Đang chờ xác nhận chuyển khoản (Chế độ thử nghiệm)",
    "paid": "Đã xác nhận thanh toán & Hoàn tất hồ sơ",
    "expired": "Đơn hàng đã hết thời hạn thanh toán",
    "underpaid": "Số tiền chuyển khoản chưa đủ theo đơn hàng",
}

ROLE_LABELS_VI = {
    "rm": "Chuyên viên Quan hệ Khách hàng",
    "teller": "Giao dịch viên Quầy",
    "credit": "Chuyên viên Thẩm định Tín dụng",
    "ops": "Chuyên viên Vận hành & Tuân thủ",
}


def _to_web_or_file_url(path_str: str) -> str:
    if not path_str:
        return ""
    p = Path(path_str)
    try:
        rel = p.resolve().relative_to(ROOT.resolve())
        return "/" + rel.as_posix()
    except Exception:
        return p.resolve().as_uri() if p.exists() else path_str


class PaymentFlowModule:
    """Bộ xử lý đơn hàng & thanh toán tất định (cố định 100%, không dùng LLM)."""

    module_id = "03_flow_thanh_toan_sinh_report"

    def __init__(self, bus: EventBus, data_dir: Path, runtime_env: RuntimeEnv | None = None):
        self.bus = bus
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.orders_file = self.data_dir / "orders.json"
        self.pages_dir = self.data_dir / "order_pages"
        self.pages_dir.mkdir(parents=True, exist_ok=True)
        self.env = runtime_env or load_runtime_env()
        self._lock = threading.Lock()
        self.bus.subscribe("report.xong", self.module_id, self.on_report_ready)

    def _load_orders(self) -> dict[str, dict]:
        if not self.orders_file.exists():
            return {}
        try:
            return json.loads(self.orders_file.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save_orders(self, orders: dict[str, dict]) -> None:
        tmp = self.orders_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(orders, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.orders_file)

    def _vietqr_url(self, order: dict) -> str:
        bank = self.env.bank_code
        name = self.env.account_name
        code = order["code"]
        amt = f"{order['amount']:,} VND"
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 260 280" width="260" height="280">'
            f'<rect width="260" height="280" rx="12" fill="#ffffff" stroke="#cbd5e1" stroke-width="2"/>'
            f'<rect x="16" y="14" width="228" height="32" rx="6" fill="#1e3a8a"/>'
            f'<text x="130" y="35" text-anchor="middle" fill="#ffffff" font-family="Segoe UI,sans-serif" font-size="13" font-weight="bold">VIETQR · {bank}</text>'
            f'<rect x="45" y="58" width="170" height="170" fill="#f8fafc" stroke="#94a3b8" stroke-width="1"/>'
            f'<rect x="55" y="68" width="42" height="42" fill="none" stroke="#0f172a" stroke-width="6"/>'
            f'<rect x="67" y="80" width="18" height="18" fill="#0f172a"/>'
            f'<rect x="163" y="68" width="42" height="42" fill="none" stroke="#0f172a" stroke-width="6"/>'
            f'<rect x="175" y="80" width="18" height="18" fill="#0f172a"/>'
            f'<rect x="55" y="176" width="42" height="42" fill="none" stroke="#0f172a" stroke-width="6"/>'
            f'<rect x="67" y="188" width="18" height="18" fill="#0f172a"/>'
            f'<rect x="112" y="112" width="36" height="36" rx="4" fill="#1d4ed8"/>'
            f'<text x="130" y="135" text-anchor="middle" fill="#ffffff" font-family="Segoe UI,sans-serif" font-size="11" font-weight="bold">QR</text>'
            f'<rect x="110" y="68" width="12" height="12" fill="#0f172a"/><rect x="134" y="80" width="14" height="14" fill="#0f172a"/>'
            f'<rect x="110" y="160" width="16" height="16" fill="#0f172a"/><rect x="160" y="130" width="18" height="12" fill="#0f172a"/>'
            f'<rect x="160" y="165" width="40" height="14" fill="#0f172a"/><rect x="160" y="192" width="24" height="24" fill="#0f172a"/>'
            f'<text x="130" y="246" text-anchor="middle" fill="#0f172a" font-family="Segoe UI,sans-serif" font-size="12" font-weight="bold">{code} · {amt}</text>'
            f'<text x="130" y="264" text-anchor="middle" fill="#475569" font-family="Segoe UI,sans-serif" font-size="10">{name}</text>'
            f'</svg>'
        )
        return "data:image/svg+xml;utf8," + quote(svg)

    def render_customer_order_page(self, order: dict) -> Path:
        """Sinh trang đơn `/o/<token>` của khách. Không lộ bất kỳ từ khoá kỹ thuật nào."""
        code = order["code"]
        token = order["token"]
        opc_cfg = load_opc_config(order["opc_id"])
        opc_title = opc_cfg.get("name", "Dịch vụ Báo cáo Cá nhân hoá").split("—")[-1].strip()
        disclaimer = opc_cfg.get("compliance", {}).get("disclaimer", "")
        cust_in = order.get("customer_input") or {}
        cust_name = (
            cust_in.get("ten")
            or cust_in.get("ten_hoc_sinh")
            or cust_in.get("ten_phu_huynh")
            or "Quý khách"
        )
        status_vi = STATUS_LABELS_VI.get(order["status"], "Đang xử lý")

        # Tóm tắt thông tin khách đã khai để chứng minh đơn của chính khách vừa điền
        info_items = []
        if cust_in.get("ngay_sinh"):
            info_items.append(f"Ngày sinh: <b>{html.escape(str(cust_in['ngay_sinh']))}</b>")
        if cust_in.get("gio_sinh"):
            info_items.append(f"Giờ sinh: <b>{html.escape(str(cust_in['gio_sinh']))}</b>")
        if cust_in.get("noi_sinh"):
            info_items.append(f"Nơi sinh: <b>{html.escape(str(cust_in['noi_sinh']))}</b>")
        if cust_in.get("vi_tri"):
            info_items.append(f"Vị trí: <b>{html.escape(str(cust_in['vi_tri']))}</b>")
        if cust_in.get("lop"):
            info_items.append(f"Khối lớp: <b>{html.escape(str(cust_in['lop']))}</b>")
        if cust_in.get("mon_manh"):
            info_items.append(f"Môn thế mạnh: <b>{html.escape(str(cust_in['mon_manh']))}</b>")
        cust_summary_html = " · ".join(info_items) if info_items else "Thông tin đã được xác nhận"

        if order["status"] == "paid" and order.get("report"):
            rep = order["report"]
            pdf_url = _to_web_or_file_url(rep.get("pdf_path") or "")
            html_url = _to_web_or_file_url(rep.get("html_path") or "") or pdf_url
            zip_url = _to_web_or_file_url(rep.get("zip_path") or "")
            zip_html = ""
            if zip_url:
                zip_html = f'<p><a class="btn-zip" href="{html.escape(zip_url)}" download>📦 Tải trọn bộ Công cụ &amp; Biểu mẫu (.ZIP)</a></p>'

            if rep.get("kit_stats"):
                ks = rep["kit_stats"]
                role_vi = ROLE_LABELS_VI.get(ks.get("role_key", ""), "Chuyên viên Ngân hàng")
                hl_html = (
                    f'<div class="product-highlights">'
                    f'<span>🏦 Nhóm nghiệp vụ: <b>{html.escape(role_vi)}</b></span> · '
                    f'<span>📋 Bộ tài liệu: <b>{ks["prompts_count"]} Câu lệnh + {ks["templates_count"]} Biểu mẫu + Lịch {ks["schedule_days"]} ngày</b></span> · '
                    f'<span>🎯 Độ khớp công việc đã khai: <b>{ks["personalization_match_pct"]}%</b></span>'
                    f'</div>'
                )
            elif rep.get("career_stats"):
                cs = rep["career_stats"]
                hl_html = (
                    f'<div class="product-highlights">'
                    f'<span>🎓 Tổ hợp sở thích nổi trội: <b>{html.escape(cs["riasec_top3_code"])}</b></span> · '
                    f'<span>📄 Độ dài hồ sơ: <b>{cs["page_count_target"]} trang A4</b></span> · '
                    f'<span>🛡️ Bảo vệ dữ liệu học sinh: <b>Phụ huynh đã đồng ý · Tự xoá bài làm thô sau {cs["raw_quiz_auto_delete_days"]} ngày</b></span>'
                    f'</div>'
                )
            else:
                hl_html = (
                    f'<div class="product-highlights">'
                    f'<span>🔮 Phương pháp: <b>Tính toán thiên văn chuẩn xác theo ngày giờ sinh</b></span> · '
                    f'<span>📏 Điểm kiểm định nội dung: <b>{rep.get("quality_gate", {}).get("score", 0)}/100</b></span> · '
                    f'<span>✍️ Độ tự nhiên ngôn ngữ: <b>{rep.get("slop_gate", {}).get("score", 0)}/100</b></span>'
                    f'</div>'
                )

            body = f"""
            <div class="badge-paid">ĐÃ THANH TOÁN &amp; HOÀN TẤT HỒ SƠ · MÃ ĐƠN {html.escape(code)}</div>
            <h1>{html.escape(opc_title)}</h1>
            <p style="font-size:15px;color:#e2e8f0;">Khách hàng: <b id="customer-display-name" style="color:#f8fafc;">{html.escape(str(cust_name))}</b> · {cust_summary_html}</p>
            {hl_html}
            <p class="lead">{html.escape(str(rep.get('author_lead', '')))}</p>
            {zip_html}
            <div class="pdf-viewer-box" style="position:relative;">
              <div class="pdf-toolbar">
                <span>📄 <b>Bản Báo cáo hiển thị trực tiếp trên trang</b></span>
                <a class="btn-dl btn-primary" id="btn-download-pdf" href="{html.escape(pdf_url)}" target="_blank" download>📥 Tải bản PDF chuẩn A4 về máy</a>
              </div>
              <iframe class="report-frame" src="{html.escape(html_url)}" width="100%" height="650px" style="border:0;background:#ffffff;display:block;" title="Nội dung báo cáo trực tiếp"></iframe>
              <embed src="{html.escape(pdf_url)}" type="application/pdf" width="100%" height="1px" style="opacity:0.01;position:absolute;bottom:0;left:0;pointer-events:none;" />
            </div>
            """
        else:
            qr = self._vietqr_url(order)
            confirm_btn_html = ""
            if order["status"] == "pending":
                confirm_btn_html = f"""
                <div class="qr-action-box">
                  <p style="margin:0 0 12px 0;font-size:15px;color:#e2e8f0;">
                    <b>Hướng dẫn bước thanh toán thử nghiệm:</b> Sau khi kiểm tra thông tin cá nhân bên trên, bấm nút dưới đây để xác nhận thanh toán thử (không thu tiền thật) và nhận ngay bản báo cáo PDF của riêng bạn.
                  </p>
                  <form action="/api/confirm-test-payment" method="get" style="margin:0;" onsubmit="var el=document.getElementById('loading-overlay');if(el)el.style.display='flex';">
                    <input type="hidden" name="token" value="{html.escape(token)}" />
                    <button type="submit" id="btn-confirm-qr" class="btn-confirm-qr btn-primary">
                      ✅ Xác nhận đã chuyển khoản (Chế độ thử — Nhận Báo cáo &amp; PDF ngay)
                    </button>
                  </form>
                </div>
                """
            body = f"""
            <div class="badge-pending">BƯỚC THANH TOÁN MÃ QR · MÃ ĐƠN {html.escape(code)}</div>
            <h1>Quét mã VietQR để thanh toán đơn {html.escape(code)}</h1>
            <p style="font-size:15px;color:#e2e8f0;">Khách hàng: <b id="customer-display-name" style="color:#f8fafc;">{html.escape(str(cust_name))}</b> · {cust_summary_html}</p>
            <div class="product-highlights">
              <span>💳 Trạng thái: <b>{html.escape(status_vi)}</b></span> ·
              <span>⏱️ Thời hạn giữ đơn: <b>15 phút</b></span>
            </div>
            <div style="text-align:center;margin:16px 0;">
              <img src="{html.escape(qr)}" alt="Mã VietQR thanh toán" style="max-width:260px;width:100%;height:auto;background:#ffffff;padding:8px;border:1px solid #cbd5e1;border-radius:12px" />
            </div>
            <p style="font-size:15px;color:#e2e8f0;">Số tiền: <b style="color:#f8fafc;">{order['amount']:,} VNĐ</b> · Nội dung chuyển khoản: <code>{html.escape(code)}</code> (giữ nguyên để hệ thống tự động đối soát)</p>
            {confirm_btn_html}
            """

        html_doc = f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Đơn hàng {html.escape(code)} · {html.escape(opc_title)}</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; }}
  html, body {{ font-family: system-ui, -apple-system, sans-serif; font-size: 15px; margin: 0; padding: 0; line-height: 1.6; color: #f8fafc; background: #0f172a; overflow-x: hidden; max-width: 100vw; }}
  .order-shell {{ max-width: 960px; margin: 1.5rem auto; padding: 0 16px; width: 100%; }}
  .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 14px; padding: 24px; word-break: break-word; overflow-wrap: anywhere; }}
  h1 {{ font-size: 1.45rem; color: #f8fafc; margin: 10px 0; line-height: 1.3; }}
  .badge-paid {{ display: inline-block; background: #064e3b; color: #86efac; border: 1px solid #22c55e; font-weight: 700; padding: 6px 14px; border-radius: 999px; font-size: 14px; }}
  .badge-pending {{ display: inline-block; background: #451a03; color: #fde68a; border: 1px solid #f59e0b; font-weight: 700; padding: 6px 14px; border-radius: 999px; font-size: 14px; }}
  .product-highlights {{ background: #0f172a; border: 1px solid #334155; color: #cbd5e1; padding: 12px 14px; border-radius: 10px; font-size: 14px; margin: 12px 0; }}
  .product-highlights b {{ color: #f8fafc; }}
  .qr-action-box {{ background: #0f172a; border: 2px solid #2563eb; border-radius: 12px; padding: 18px; margin: 16px 0; text-align: center; }}
  .btn-confirm-qr {{ display: inline-flex; align-items: center; justify-content: center; min-height: 48px; min-width: 48px; background: #2563eb; color: #ffffff; border: 0; border-radius: 10px; padding: 12px 20px; font-size: 15px; font-weight: 700; cursor: pointer; width: 100%; max-width: 520px; }}
  .btn-confirm-qr:hover {{ background: #1d4ed8; }}
  .pdf-viewer-box {{ margin: 18px 0; border: 2px solid #2563eb; border-radius: 12px; overflow: hidden; background: #ffffff; }}
  .pdf-toolbar {{ display: flex; flex-wrap: wrap; gap: 10px; justify-content: space-between; align-items: center; padding: 12px 16px; background: #0f172a; color: #f8fafc; border-bottom: 1px solid #334155; font-size: 15px; }}
  .btn-dl {{ display: inline-flex; align-items: center; justify-content: center; min-height: 46px; min-width: 46px; background: #2563eb; color: #fff; text-decoration: none; padding: 10px 16px; border-radius: 8px; font-weight: 700; font-size: 14px; }}
  .btn-zip {{ display: inline-flex; align-items: center; justify-content: center; min-height: 46px; min-width: 46px; background: #0f172a; color: #e2e8f0; border: 1px solid #475569; text-decoration: none; padding: 10px 16px; border-radius: 8px; font-weight: 700; font-size: 14px; margin-bottom: 10px; }}
  .lead {{ background: #0f172a; color: #e2e8f0; padding: 12px 16px; border-left: 4px solid #2563eb; border-radius: 6px; font-size: 15px; }}
  .note {{ font-size: 14px; color: #cbd5e1; }}
  details.xem-them {{ margin-top: 16px; padding: 10px 14px; background: #0f172a; border: 1px solid #334155; border-radius: 10px; }}
  details.xem-them summary {{ min-height: 44px; display: flex; align-items: center; cursor: pointer; font-size: 14px; font-weight: 700; color: #93c5fd; }}
  #loading-overlay {{ display: none; position: fixed; inset: 0; background: rgba(15,23,42,0.92); z-index: 9999; align-items: center; justify-content: center; padding: 24px; text-align: center; font-size: 16px; font-weight: 700; color: #ffffff; }}
  .empty-state {{ display: none; padding: 16px; font-size: 14px; color: #94a3b8; }}
  code {{ background: #0f172a; color: #93c5fd; border: 1px solid #334155; padding: 2px 8px; border-radius: 6px; font-size: 14px; }}
  @media (max-width: 768px) {{
    .order-shell {{ margin: 0.75rem auto; padding: 0 10px; }}
    .card {{ padding: 14px; }}
    h1 {{ font-size: 1.2rem; }}
    .pdf-toolbar {{ flex-direction: column; align-items: flex-start; }}
    .btn-dl, .btn-zip {{ width: 100%; text-align: center; }}
  }}
</style>
</head>
<body>
  <div id="loading-overlay" data-state="loading">⏳ Đang đối soát thanh toán thử &amp; kết xuất bản báo cáo PDF chuẩn A4 của riêng bạn, vui lòng đợi trong giây lát...</div>
  <main class="order-shell" role="main">
    <div class="card">
      <div class="empty-state" data-state="empty">Chưa có nội dung báo cáo.</div>
      {body}
      <details class="xem-them">
        <summary>⚖️ Xem thêm lưu ý miễn trừ trách nhiệm, thông tin đơn vị thụ hưởng &amp; quay về trang chủ</summary>
        <div style="margin-top:8px;">
          <p class="note">⚖️ <b>Lưu ý &amp; Tuyên bố miễn trừ:</b> {html.escape(disclaimer)}</p>
          <p class="note">Đơn vị thụ hưởng: {html.escape(self.env.account_name)} ({html.escape(self.env.account_number_masked)}) · Đường dẫn tra cứu: <a href="/o/{html.escape(token)}" style="color:#93c5fd;display:inline-flex;align-items:center;min-height:44px;padding:4px 8px;">/o/{html.escape(token)}</a> · <a href="/privacy" style="color:#93c5fd;display:inline-flex;align-items:center;min-height:44px;padding:4px 8px;">Chính sách bảo vệ dữ liệu</a> · <a href="/" style="color:#93c5fd;display:inline-flex;align-items:center;min-height:44px;padding:4px 8px;">Về Bảng Điều Khiển</a></p>
        </div>
      </details>
    </div>
  </main>
</body>
</html>"""
        page_path = self.pages_dir / f"order_{code}.html"
        page_path.write_text(html_doc, encoding="utf-8")
        return page_path

    def create_order(self, opc_id: str, customer_input: dict, amount: int | None = None, created_ts: int | None = None) -> dict:
        opc_cfg = load_opc_config(opc_id)
        canonical_opc_id = opc_cfg["opc_id"]

        # Cổng A - Mục 3 Phá thử: kiểm tra đầu vào rỗng
        if not isinstance(customer_input, dict) or not customer_input:
            raise ValueError("Thông tin người đặt hàng không được để trống.")
        primary_name = str(
            customer_input.get("ten")
            or customer_input.get("ho_ten")
            or customer_input.get("ten_hoc_sinh")
            or customer_input.get("ten_phu_huynh")
            or customer_input.get("ten_doanh_nghiep")
            or ""
        ).strip()
        if not primary_name:
            raise ValueError("Vui lòng nhập Họ và tên trước khi tạo đơn hàng.")

        if opc_cfg.get("compliance", {}).get("require_consent_checkbox", True):
            if not customer_input.get("consent") and not customer_input.get("dong_y_phu_huynh"):
                raise ValueError("Quý khách / Phụ huynh vui lòng tích ô đồng ý xử lý dữ liệu cá nhân trước khi tiếp tục.")

        # Đọc order_prefix động từ opc.json (hỗ trợ cả ở gốc lẫn trong mục payment)
        prefix = (
            opc_cfg.get("order_prefix")
            or opc_cfg.get("payment", {}).get("order_prefix")
            or "LX"
        )
        price = int(amount if amount is not None else opc_cfg.get("pricing", {}).get("default_price", 199000))
        now_ts = int(created_ts if created_ts is not None else time.time())
        expiry_sec = int(
            opc_cfg.get("thresholds", {}).get("order_expiry_seconds")
            or int(opc_cfg.get("payment", {}).get("qr_expire_minutes", 30)) * 60
        )

        with self._lock:
            orders = self._load_orders()
            opc_count = sum(1 for o in orders.values() if o.get("opc_id") == canonical_opc_id or str(o.get("code", "")).startswith(prefix))
            code = f"{prefix}{opc_count + 1:05d}"
            while any(o.get("code") == code for o in orders.values()):
                opc_count += 1
                code = f"{prefix}{opc_count + 1:05d}"
            token = secrets.token_urlsafe(10)
            order = {
                "token": token,
                "code": code,
                "opc_id": canonical_opc_id,
                "order_seq_index": opc_count + 1,
                "domain": opc_cfg.get("domain", "astrology"),
                "product": opc_cfg.get("default_product", "ban-do-sao-ca-nhan"),
                "amount": price,
                "status": "pending",
                "created_at": now_ts,
                "expires_at": now_ts + expiry_sec,
                "customer_input": customer_input,
                "tx_id": None,
                "paid_at": None,
                "report": None,
                "order_page_html": None,
            }
            page_path = self.render_customer_order_page(order)
            order["order_page_html"] = str(page_path)
            orders[token] = order
            self._save_orders(orders)

        self.bus.publish("don.tao_moi", opc_id=canonical_opc_id, source_module=self.module_id, payload=order)
        return order

    def handle_sepay_webhook(
        self,
        tx: dict,
        auth_header: str,
        current_ts: int | None = None,
        render_pdf_file: bool = True,
        reports_base_dir: Path | None = None,
    ) -> tuple[int, dict]:
        """Xử lý webhook SePay theo đúng chuẩn LAB060 + kiểm tra hết hạn, thiếu tiền, trùng giao dịch."""
        if not self.env.verify_webhook_header(auth_header):
            self.bus.publish(
                "don.loi_thanh_toan",
                opc_id="unknown",
                source_module=self.module_id,
                payload={"reason": "unauthorized_api_key", "tx_id": tx.get("id")},
            )
            return 401, {"success": False, "error": "unauthorized_api_key"}

        if tx.get("transferType") != "in":
            return 200, {"success": True, "action": "ignored_not_transfer_in"}

        text = f"{tx.get('code') or ''} {tx.get('content') or ''}".upper()
        tx_id = tx.get("id")
        transfer_amount = int(float(tx.get("transferAmount") or 0))
        now_ts = int(current_ts if current_ts is not None else time.time())

        matched_order = None
        action_status = "no_matching_order"

        with self._lock:
            orders = self._load_orders()
            # 1. Chống trùng giao dịch (Idempotency)
            if tx_id is not None and any(o.get("tx_id") == tx_id for o in orders.values()):
                return 200, {"success": True, "action": "duplicate_tx_ignored", "tx_id": tx_id}

            for token, o in orders.items():
                if o["code"].upper() in text:
                    if o["status"] == "paid":
                        return 200, {"success": True, "action": "order_already_paid_ignored", "order_code": o["code"]}

                    if o["status"] == "expired" or now_ts > int(o.get("expires_at", now_ts + 1)):
                        o["status"] = "expired"
                        self.render_customer_order_page(o)
                        self._save_orders(orders)
                        self.bus.publish(
                            "don.het_han",
                            opc_id=o["opc_id"],
                            source_module=self.module_id,
                            payload={"order_code": o["code"], "tx_id": tx_id, "transfer_amount": transfer_amount},
                        )
                        return 200, {"success": False, "action": "order_expired", "order_code": o["code"]}

                    if transfer_amount < int(o["amount"]):
                        o["status"] = "underpaid"
                        o["underpaid_amount"] = transfer_amount
                        self.render_customer_order_page(o)
                        self._save_orders(orders)
                        self.bus.publish(
                            "don.loi_thanh_toan",
                            opc_id=o["opc_id"],
                            source_module=self.module_id,
                            payload={
                                "reason": "underpaid_amount",
                                "order_code": o["code"],
                                "expected": o["amount"],
                                "received": transfer_amount,
                                "tx_id": tx_id,
                            },
                        )
                        return 200, {
                            "success": False,
                            "action": "underpaid_amount",
                            "order_code": o["code"],
                            "expected": o["amount"],
                            "received": transfer_amount,
                        }

                    o["status"] = "paid"
                    o["tx_id"] = tx_id
                    o["paid_amount"] = transfer_amount
                    o["paid_at"] = tx.get("transactionDate") or time.strftime("%Y-%m-%d %H:%M:%S")
                    o["reference_code"] = tx.get("referenceCode", "")
                    o["tx_content"] = tx.get("content", "")
                    self._save_orders(orders)
                    matched_order = dict(o)
                    action_status = "paid_and_dispatched"
                    break

        if matched_order:
            event_payload = {
                "order_code": matched_order["code"],
                "token": matched_order["token"],
                "opc_id": matched_order["opc_id"],
                "order_seq_index": matched_order["order_seq_index"],
                "domain": matched_order["domain"],
                "product": matched_order["product"],
                "amount": matched_order["paid_amount"],
                "tx_id": matched_order["tx_id"],
                "paid_at": matched_order["paid_at"],
                "reference_code": matched_order["reference_code"],
                "tx_content": matched_order["tx_content"],
                "customer_input": matched_order["customer_input"],
                "render_pdf_file": render_pdf_file,
            }
            if reports_base_dir:
                event_payload["out_dir"] = str(Path(reports_base_dir) / matched_order["code"])

            # Phát sự kiện nội bộ và sự kiện chuẩn liên OS (_KIEN_THUC/GIAO_KEO.md mục 3.2)
            self.bus.publish("don.da_tra", opc_id=matched_order["opc_id"], source_module=self.module_id, payload=event_payload)
            self.bus.publish("don_hang.da_thanh_toan", opc_id=matched_order["opc_id"], source_module=self.module_id, payload=event_payload)

            updated = self._load_orders().get(matched_order["token"], matched_order)
            return 200, {
                "success": True,
                "action": action_status,
                "order_code": updated["code"],
                "token": updated["token"],
                "order_page_html": updated.get("order_page_html"),
                "pdf_path": (updated.get("report") or {}).get("pdf_path"),
                "zip_path": (updated.get("report") or {}).get("zip_path"),
            }

        return 200, {"success": False, "action": action_status}

    def on_report_ready(self, event: Event) -> dict:
        rep = event.payload
        order_code = rep.get("order_code")
        with self._lock:
            orders = self._load_orders()
            for token, o in orders.items():
                if o["code"] == order_code:
                    o["report"] = rep
                    page_path = self.render_customer_order_page(o)
                    o["order_page_html"] = str(page_path)
                    self._save_orders(orders)
                    return {"updated_order": order_code, "order_page_html": str(page_path)}
        return {"updated_order": None}

    def request_refund(self, order_code: str, reason: str) -> dict:
        """Luật 6.2: Agent và hệ thống tự động KHÔNG được tự hoàn tiền, chỉ tạo phiếu chờ Founder duyệt."""
        with self._lock:
            orders = self._load_orders()
            for token, o in orders.items():
                if o["code"] == order_code:
                    o["refund_request"] = {
                        "status": "pending_founder_approval",
                        "reason": reason,
                        "requested_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "policy_note": "Mọi khoản hoàn tiền bắt buộc do Founder (anh Linh) duyệt tay (QUY-CHUAN 6.2).",
                    }
                    self._save_orders(orders)
                    self.bus.publish(
                        "don.yeu_cau_hoan_tien",
                        opc_id=o["opc_id"],
                        source_module=self.module_id,
                        payload={"order_code": order_code, "amount": o["amount"], "reason": reason},
                    )
                    return o["refund_request"]
        raise KeyError(f"Không tìm thấy đơn {order_code}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Module 03: Flow Thanh toán -> Sinh Report")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()

    in_path = HERE / "demo" / "input" / "demo_in.json"
    out_path = HERE / "demo" / "output" / "demo_out.json"
    demo_data = json.loads(in_path.read_text(encoding="utf-8"))

    demo_data_dir = HERE / "demo" / "output" / "data"
    if demo_data_dir.exists():
        import shutil
        shutil.rmtree(demo_data_dir)
    bus = EventBus(HERE / "demo" / "output" / "events.jsonl")
    env = load_runtime_env()
    mod = PaymentFlowModule(bus, demo_data_dir, runtime_env=env)
    order = mod.create_order(demo_data["opc_id"], demo_data["customer_input"], amount=demo_data["amount"])
    tx = {
        "id": 880001,
        "transferType": "in",
        "transferAmount": demo_data["amount"],
        "code": order["code"],
        "content": f"{order['code']} thanh toan",
        "transactionDate": "2026-10-25 13:15:00",
        "referenceCode": "FT26298DEMO",
    }
    code_http, webhook_res = mod.handle_sepay_webhook(tx, env.get_poc_webhook_header_for_test(), render_pdf_file=False)
    res = {"created_order": order["code"], "http_status": code_http, "webhook_result": webhook_res}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Module 03] Xong {order['code']} -> HTTP {code_http} | {webhook_res['action']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
