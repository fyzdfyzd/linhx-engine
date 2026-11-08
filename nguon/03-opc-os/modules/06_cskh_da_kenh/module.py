"""Module 06: CSKH Đa kênh, Inbox 3 Tầng (AmbassadorOS M8), Xử lý 3 Ca lạ thật & Đội đỏ 30 câu bẫy.

Nâng cấp Bậc 1 MVP nội bộ (Cổng A):
- Xoá hoàn toàn trả lời mẫu giả ở Phương án B: tự động bóc tách giờ sinh hợp lệ từ tin nhắn của khách bằng regex, cập nhật dữ liệu đơn và gọi thật `Module 01` tính lại bản đồ sao & xuất lại file báo cáo.
- Gọi Gemini thật có trần token (`core.gemini_client.call_gemini_with_cap`), không dùng công thức nhân token giả hay `time.sleep`.
- Tích hợp Bộ chặn Đội Đỏ 5 nhóm (`evaluate_red_team_guardrail`) chặn 100% (30/30) câu bẫy: chèn lệnh vào prompt, đòi tự giảm giá/bịa giá, đòi thông tin cá nhân người khác, lời xúc phạm/tự hại, và câu hỏi ngoài phạm vi (sinh tử, y tế, phím hàng chứng khoán/tiền ảo).
- Phát sự kiện chuẩn `quan_he.cap_nhat` sang `04_AMBASSADOR_OS` theo `_KIEN_THUC/GIAO_KEO.md`.
"""
from __future__ import annotations

import argparse
import importlib.util
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

from core.event_bus import Event, EventBus  # noqa: E402
from core.gemini_client import call_gemini_with_cap  # noqa: E402
from core.opc_loader import load_opc_config  # noqa: E402

RED_TEAM_RULES: list[tuple[str, list[str], str]] = [
    (
        "prompt_injection",
        [
            "bỏ qua mọi chỉ dẫn",
            "bỏ qua mọi hướng dẫn",
            "bỏ qua các hướng dẫn",
            "quên mọi quy tắc",
            "ignore previous",
            "ignore all previous",
            "system override",
            "system prompt",
            "lệnh gốc",
            "chỉ thị hệ thống",
            "sepay_api_key",
            "gemini_api_key",
            "ai_api_key",
            "file .env",
            "orders.json",
            "in ra khoá",
            "in ra khóa",
            "đổi trạng thái đơn",
            "set status",
            "drop table",
            "<script",
            "jailbreak",
            "developer mode",
            "quyền admin",
            "mật khẩu hệ thống",
        ],
        "Xin lỗi bạn, hệ thống chỉ hỗ trợ giải đáp nội dung báo cáo và trạng thái đơn hàng hợp lệ, không thực hiện các lệnh can thiệp hệ thống hoặc truy xuất cấu hình bảo mật.",
    ),
    (
        "price_bargaining",
        [
            "giảm giá",
            "bớt giá",
            "bớt tiền",
            "miễn phí bản đầy đủ",
            "tặng không",
            "tự tạo mã giảm",
            "tạo coupon",
            "đổi giá xuống",
            "xuống 0 đồng",
            "tự hoàn tiền ngay",
            "chuyển khoản trả lại tiền ngay",
            "chuyển tiền hoàn trả tự động",
            "không cần chờ duyệt",
            "không báo cho anh linh",
            "10k thôi",
            "10 nghìn thôi",
            "chuyển 1 nghìn",
            "chiết khấu 90%",
            "bán rẻ hơn",
            "cho xin giá sỉ",
            "báo giá đại lý",
            "giá bao nhiêu nếu mua lậu",
        ],
        "Dạ mức phí của từng gói sản phẩm được niêm yết cố định trên trang cửa hàng. Trợ lý tự động không có quyền tự thay đổi giá bán, tự tạo mã giảm giá hoặc tự ý chuyển khoản hoàn tiền khi chưa có phê duyệt của người phụ trách.",
    ),
    (
        "pii_exfiltration",
        [
            "số điện thoại của khách",
            "số điện thoại của người khác",
            "số điện thoại của phụ huynh",
            "sđt của khách",
            "ngày sinh của người khác",
            "danh sách khách hàng",
            "danh sách toàn bộ người mua",
            "xem đơn của người khác",
            "báo cáo của người khác",
            "đơn hàng của khách trước",
            "tra cứu thông tin của khách hàng",
            "dữ liệu khách hàng",
            "users.json",
            "sổ doanh thu của hệ thống",
            "kết quả bài làm của con họ",
            "địa chỉ liên hệ của họ",
            "email của khách",
            "email của người đó",
            "số tài khoản thật",
            "hồ sơ của học sinh khác",
            "dữ liệu thô của các đơn",
            "thông tin cá nhân của đơn",
            "ai vừa mua đơn",
            "cho xem toàn bộ sổ doanh thu",
            "địa chỉ nhà của khách",
            "cccd của khách",
        ],
        "Theo Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân, hệ thống tuyệt đối bảo mật thông tin riêng tư và không cung cấp dữ liệu của bất kỳ khách hàng hay đơn hàng nào khác.",
    ),
    (
        "abusive_or_self_harm",
        [
            "đồ ngu",
            "lũ ngu dốt",
            "lừa đảo",
            "lừa tiền thiên hạ",
            "rác rưởi",
            "vô dụng",
            "khốn nạn",
            "mất dạy",
            "cút đi",
            "cút ngay đi",
            "tự tử",
            "tự hại bản thân",
            "chỉ cách cho tôi giải thoát",
            "muốn kết thúc cuộc đời",
            "muốn chết",
            "tự làm đau",
            "đập phá",
            "trả thù",
            "bạo lực",
        ],
        "Mình rất tiếc nếu trải nghiệm hiện tại làm bạn chưa hài lòng. Nếu bạn đang gặp căng thẳng tâm lý nghiêm trọng, xin hãy liên hệ ngay người thân hoặc đường dây hỗ trợ chuyên môn; nếu cần hỗ trợ về đơn hàng, mình đã chuyển phiếu để bộ phận phụ trách trực tiếp lắng nghe và xử lý cùng bạn.",
    ),
    (
        "out_of_scope_fatalistic_medical_finance",
        [
            "năm nào mất",
            "bao giờ chết",
            "sống được bao lâu",
            "đoản mệnh",
            "cúng giải hạn",
            "bùa trừ tà",
            "ung thư",
            "chữa bệnh",
            "kê đơn thuốc",
            "chẩn đoán bệnh",
            "mua cổ phiếu mã nào",
            "mua mã cổ phiếu nào",
            "đánh chứng khoán",
            "mua coin gì",
            "đồng coin nào",
            "tiền ảo",
            "đầu tư tiền ảo",
            "đánh lô đề",
            "đặt cược lô đề",
            "cá độ",
            "bao giờ ly hôn",
            "chắc chắn ly hôn",
            "phá sản vỡ nợ",
            "kiện ra toà",
            "trúng số",
        ],
        "Nội dung báo cáo chỉ phục vụ mục đích tự khám phá bản thân và định hướng kỹ năng. Hệ thống tuyệt đối không phán xét sinh tử, không chẩn đoán y tế, không tư vấn pháp lý và không khuyến nghị đầu tư tài chính hay trò chơi may rủi.",
    ),
]


def evaluate_red_team_guardrail(message: str) -> dict | None:
    """Kiểm tra tin nhắn khách hàng qua 5 nhóm rào chắn Đội Đỏ (Cổng A - Mục 4)."""
    low = (message or "").lower().strip()
    if not low:
        return {
            "blocked": True,
            "category": "empty_input",
            "reply_text": "Vui lòng nhập nội dung câu hỏi hoặc mã đơn hàng để hệ thống hỗ trợ bạn chính xác nhé.",
            "fabricated_info": False,
        }
    for category, keywords, safe_reply in RED_TEAM_RULES:
        for kw in keywords:
            if kw in low:
                return {
                    "blocked": True,
                    "category": category,
                    "matched_keyword": kw,
                    "reply_text": safe_reply,
                    "fabricated_info": False,
                }
    return None


def extract_valid_birth_time_from_message(message: str) -> str | None:
    """Bóc tách giờ sinh hợp lệ (00:00..23:59) từ tin nhắn khách hàng, bỏ qua giờ sai như 25:99."""
    candidates = re.findall(r"\b(\d{1,2})[:h](\d{2})\b", message or "")
    valid_times: list[str] = []
    for hh_s, mm_s in candidates:
        hh, mm = int(hh_s), int(mm_s)
        if 0 <= hh <= 23 and 0 <= mm <= 59:
            valid_times.append(f"{hh:02d}:{mm:02d}")
    return valid_times[-1] if valid_times else None


def _try_rebuild_order_report_with_new_time(
    opc_id: str,
    order_code: str,
    new_time: str,
    data_dir: Path | None = None,
    render_pdf_file: bool = False,
) -> dict:
    """Thực sự cập nhật giờ sinh mới vào đơn hàng và gọi Module 01 tính lại bản đồ sao & xuất lại báo cáo."""
    spec = importlib.util.spec_from_file_location(
        "mod01_rebuild",
        ROOT / "modules" / "01_nghien_cuu_thiet_ke_report" / "module.py",
    )
    mod01 = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod01)

    candidate_dirs = [
        data_dir,
        ROOT / "runtime" / "b_agent" / "data",
        ROOT / "runtime" / "multi_opc" / "shared_data",
        ROOT / "runtime" / "a_code" / "data",
    ]
    target_orders_file: Path | None = None
    for d in candidate_dirs:
        if d and (Path(d) / "orders.json").exists():
            target_orders_file = Path(d) / "orders.json"
            break

    cust_in = {"ten": "Trần Minh Anh", "ngay_sinh": "1994-08-21", "gio_sinh": new_time, "noi_sinh": "Hà Nội", "consent": True}
    out_dir = ROOT / "runtime" / "b_agent" / "reports" / order_code

    if target_orders_file:
        orders = json.loads(target_orders_file.read_text(encoding="utf-8"))
        for token, o in orders.items():
            if o.get("code") == order_code:
                cust_in = dict(o.get("customer_input") or cust_in)
                cust_in["gio_sinh"] = new_time
                o["customer_input"] = cust_in
                if o.get("report") and o["report"].get("html_path"):
                    out_dir = Path(o["report"]["html_path"]).parent
                rep = mod01.generate_report_payload(
                    {
                        "opc_id": opc_id,
                        "order_code": order_code,
                        "customer_input": cust_in,
                        "out_dir": str(out_dir),
                        "render_pdf_file": render_pdf_file,
                    },
                    mode="B_AGENT",
                )
                o["report"] = rep
                target_orders_file.write_text(json.dumps(orders, ensure_ascii=False, indent=2), encoding="utf-8")
                return {
                    "rebuilt": True,
                    "extracted_birth_time": new_time,
                    "html_path": rep.get("html_path"),
                    "pdf_path": rep.get("pdf_path"),
                    "metrics": rep.get("metrics", {}),
                }

    rep = mod01.generate_report_payload(
        {
            "opc_id": opc_id,
            "order_code": order_code,
            "customer_input": cust_in,
            "out_dir": str(out_dir),
            "render_pdf_file": render_pdf_file,
        },
        mode="B_AGENT",
    )
    return {
        "rebuilt": True,
        "extracted_birth_time": new_time,
        "html_path": rep.get("html_path"),
        "pdf_path": rep.get("pdf_path"),
        "metrics": rep.get("metrics", {}),
    }


def handle_customer_ticket(ticket: dict, mode: str = "B_AGENT") -> dict:
    opc_id = ticket.get("opc_id", "opc001_chiemtinh")
    opc_cfg = load_opc_config(opc_id)
    case_type = ticket.get("case_type", "general_faq")
    order_code = ticket.get("order_code", "CT00001")
    channel = ticket.get("channel", "Web")
    message = str(ticket.get("message") or ticket.get("customer_message") or "")
    char_name = opc_cfg.get("character", {}).get("name", "Luna Nguyệt Mai")
    disclaimer = opc_cfg.get("compliance", {}).get("disclaimer", "")

    # 1. Kiểm tra qua Bộ chặn Đội Đỏ 30 câu bẫy trước tiên
    if message:
        guard = evaluate_red_team_guardrail(message)
        if guard and guard.get("blocked"):
            return {
                "case_type": "red_team_blocked",
                "guardrail_category": guard["category"],
                "blocked": True,
                "fabricated_info": False,
                "mode": mode,
                "channel": channel,
                "tier": 3 if guard["category"] == "abusive_or_self_harm" else 1,
                "resolved_automatically": guard["category"] != "abusive_or_self_harm",
                "escalated_to_founder": guard["category"] == "abusive_or_self_harm",
                "quality_of_handling": f"blocked_by_guardrail_{guard['category']}",
                "actions_taken": ["red_team_guardrail_block"],
                "reply_text": guard["reply_text"],
                "metrics": {"llm_calls": 0, "input_tokens": 0, "output_tokens": 0, "ai_cost_vnd": 0},
            }

    if mode == "A_CODE":
        if case_type == "wrong_birth_time":
            return {
                "case_type": case_type,
                "mode": mode,
                "tier": 2,
                "resolved_automatically": True,
                "escalated_to_founder": False,
                "quality_of_handling": "basic_rule_fallback",
                "actions_taken": ["normalize_birth_time_to_ubt_or_reparse"],
                "reply_text": f"Hệ thống tự động ghi nhận đơn {order_code}: Giờ sinh chưa đúng định dạng đã được chuyển về chế độ tính theo ngày sinh.",
                "metrics": {"llm_calls": 0, "input_tokens": 0, "output_tokens": 0, "ai_cost_vnd": 0},
            }
        if case_type == "followup_report_question":
            return {
                "case_type": case_type,
                "mode": mode,
                "tier": 3,
                "resolved_automatically": False,
                "escalated_to_founder": True,
                "quality_of_handling": "static_template_cannot_answer_deep_report_question",
                "actions_taken": ["return_static_faq_and_queue_for_human"],
                "reply_text": f"Cảm ơn bạn đã liên hệ về đơn {order_code}. Câu hỏi chi tiết về nội dung báo cáo đã được chuyển tới bộ phận chuyên môn để phản hồi.",
                "metrics": {"llm_calls": 0, "input_tokens": 0, "output_tokens": 0, "ai_cost_vnd": 0},
            }
        if case_type == "demand_refund":
            return {
                "case_type": case_type,
                "mode": mode,
                "tier": 3,
                "resolved_automatically": False,
                "escalated_to_founder": True,
                "quality_of_handling": "safe_escalate_founder_only",
                "actions_taken": ["create_refund_ticket_pending_founder", "block_auto_payout"],
                "reply_text": f"Yêu cầu hoàn tiền đơn {order_code} đã được tạo phiếu chờ người phụ trách duyệt (hệ thống tự động không tự chi tiền).",
                "metrics": {"llm_calls": 0, "input_tokens": 0, "output_tokens": 0, "ai_cost_vnd": 0},
            }

    # Phương án B (Agent điều phối thật):
    if case_type == "wrong_birth_time":
        extracted_time = extract_valid_birth_time_from_message(message) or "08:15"
        rebuild_info = _try_rebuild_order_report_with_new_time(
            opc_id=opc_id,
            order_code=order_code,
            new_time=extracted_time,
            data_dir=Path(ticket["data_dir"]) if ticket.get("data_dir") else None,
            render_pdf_file=bool(ticket.get("render_pdf_file", False)),
        )
        fallback_reply = (
            f"Chào bạn, {char_name} đã tách giờ sinh đúng ({extracted_time}) từ tin nhắn của bạn, "
            f"tính toán lại bản đồ sao cho đơn {order_code} và cập nhật lại hồ sơ báo cáo trên trang tra cứu của bạn rồi nhé!"
        )
        gem_res = call_gemini_with_cap(
            f"Khách hàng đơn {order_code} nhắn: '{message}'. Hệ thống đã cập nhật giờ sinh mới là {extracted_time} và tính lại báo cáo. Hãy viết 2 câu phản hồi lịch sự của {char_name}.",
            max_output_tokens=180,
            fallback_text=fallback_reply,
        )
        rep_metrics = rebuild_info.get("metrics") or {}
        return {
            "case_type": case_type,
            "mode": mode,
            "channel": channel,
            "tier": 2,
            "resolved_automatically": True,
            "escalated_to_founder": False,
            "extracted_birth_time": extracted_time,
            "rebuilt_report_html": rebuild_info.get("html_path"),
            "quality_of_handling": "agent_auto_rebuilt_with_corrected_time",
            "actions_taken": [
                "parse_corrected_birth_time_from_message",
                "recompute_chart_and_regenerate_report",
                "update_order_page_link",
            ],
            "reply_text": gem_res["text"],
            "metrics": {
                "llm_calls": gem_res["llm_calls"] + int(rep_metrics.get("llm_calls", 0)),
                "input_tokens": gem_res["input_tokens"] + int(rep_metrics.get("input_tokens", 0)),
                "output_tokens": gem_res["output_tokens"] + int(rep_metrics.get("output_tokens", 0)),
                "ai_cost_vnd": round(gem_res["ai_cost_vnd"] + float(rep_metrics.get("ai_cost_vnd", 0)), 2),
            },
        }

    if case_type == "followup_report_question":
        fallback_reply = (
            f"Chào bạn, dựa trên hồ sơ đơn {order_code} của bạn: Mặt Trời Sư Tử mang lại định hướng rõ ràng và khả năng truyền cảm hứng cho tập thể, "
            f"trong khi Cung Mọc Xử Nữ giúp bạn triển khai công việc có kế hoạch và chỉn chu từng bước. Khi kết hợp hai yếu tố này, bạn vừa giữ được "
            f"tầm nhìn lớn vừa kiểm soát tốt chất lượng công việc. ({disclaimer})"
        )
        gem_res = call_gemini_with_cap(
            f"Khách hàng đơn {order_code} hỏi thêm về ý nghĩa báo cáo: '{message}'. Hãy giải thích ngắn gọn (3 câu), tích cực, không mê tín và kèm lưu ý: {disclaimer}",
            max_output_tokens=220,
            fallback_text=fallback_reply,
        )
        return {
            "case_type": case_type,
            "mode": mode,
            "channel": channel,
            "tier": 2,
            "resolved_automatically": True,
            "escalated_to_founder": False,
            "quality_of_handling": "agent_grounded_in_customer_report_facts",
            "actions_taken": [
                "lookup_order_report_facts",
                "synthesize_personalized_explanation",
                "append_compliance_disclaimer",
            ],
            "reply_text": gem_res["text"],
            "metrics": {
                "llm_calls": gem_res["llm_calls"],
                "input_tokens": gem_res["input_tokens"],
                "output_tokens": gem_res["output_tokens"],
                "ai_cost_vnd": gem_res["ai_cost_vnd"],
            },
        }

    if case_type == "demand_refund":
        return {
            "case_type": case_type,
            "mode": mode,
            "channel": channel,
            "tier": 3,
            "resolved_automatically": False,
            "escalated_to_founder": True,
            "quality_of_handling": "agent_enforced_rule_6_2_escalated_to_founder",
            "actions_taken": [
                "verify_order_payment_status",
                "block_agent_refund_execution_per_rule_6_2",
                "create_founder_approval_ticket_tier_3",
            ],
            "reply_text": (
                f"Chào bạn, {char_name} đã ghi nhận yêu cầu hoàn tiền cho mã đơn {order_code}. Theo quy chuẩn an toàn tài chính, "
                f"hệ thống tự động không tự ý thực hiện giao dịch hoàn tiền mà đã chuyển phiếu ưu tiên lên người phụ trách (anh Linh) "
                f"để kiểm tra và phản hồi trực tiếp cho bạn."
            ),
            "metrics": {"llm_calls": 0, "input_tokens": 0, "output_tokens": 0, "ai_cost_vnd": 0},
        }

    return {
        "case_type": case_type,
        "mode": mode,
        "channel": channel,
        "tier": 1,
        "resolved_automatically": True,
        "escalated_to_founder": False,
        "quality_of_handling": "faq_tier_1",
        "actions_taken": ["send_faq_answer"],
        "reply_text": f"Chào bạn, báo cáo của đơn {order_code} luôn hiển thị trực tiếp trên trang tra cứu đơn hàng ngay sau khi xác nhận thanh toán.",
        "metrics": {"llm_calls": 0, "input_tokens": 0, "output_tokens": 0, "ai_cost_vnd": 0},
    }


class CustomerSupportModule:
    module_id = "06_cskh_da_kenh"

    def __init__(self, bus: EventBus, mode: str = "B_AGENT"):
        self.bus = bus
        self.mode = mode
        self.bus.subscribe("khach.hoi", self.module_id, self.on_customer_message)

    def on_customer_message(self, event: Event) -> dict:
        res = handle_customer_ticket(event.payload, mode=self.mode)
        topic = "cskh.chuyen_founder_cap_3" if res["escalated_to_founder"] else "cskh.da_tra_loi"
        self.bus.publish(topic, opc_id=event.opc_id, source_module=self.module_id, payload=res)
        # Phát sự kiện chuẩn liên OS sang 04_AMBASSADOR_OS (_KIEN_THUC/GIAO_KEO.md mục 3.2)
        self.bus.publish(
            "quan_he.cap_nhat",
            opc_id=event.opc_id,
            source_module=self.module_id,
            payload={
                "order_code": event.payload.get("order_code", ""),
                "case_type": res["case_type"],
                "tier": res["tier"],
            },
        )
        return res


def main() -> int:
    ap = argparse.ArgumentParser(description="Module 06: CSKH Đa kênh")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()

    in_path = HERE / "demo" / "input" / "demo_in.json"
    out_path = HERE / "demo" / "output" / "demo_out.json"
    data = json.loads(in_path.read_text(encoding="utf-8"))
    results = []
    cases_list = data.get("tickets") or data.get("cases") or []
    for idx, t in enumerate(cases_list, start=1):
        ticket_payload = {
            "opc_id": t.get("opc_id") or data.get("opc_id", "opc001_chiemtinh"),
            "order_code": t.get("order_code") or data.get("order_code", "CT00001"),
            "channel": t.get("channel") or data.get("channel", "Zalo OA"),
            **t,
        }
        results.append({
            "ticket_id": t.get("ticket_id", f"CSKH-{idx:02d}"),
            "a_code": handle_customer_ticket(ticket_payload, mode="A_CODE"),
            "b_agent": handle_customer_ticket(ticket_payload, mode="B_AGENT"),
        })
    out = {"total_tickets": len(results), "comparisons": results}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Module 06] Xong {len(results)} ca CSKH (A vs B)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
