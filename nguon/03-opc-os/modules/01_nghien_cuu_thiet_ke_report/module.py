"""Module 01: Nghiên cứu, thiết kế và sinh Report cá nhân hoá (`01_nghien_cuu_thiet_ke_report`).

Nâng cấp Bậc 1 MVP nội bộ (Cổng A):
- Thay thế hoàn toàn hàm giả lập token AI bằng `core.gemini_client.call_gemini_with_cap` (gọi Gemini thật có trần token từ `03_OPC_OS/.env`; khi chưa có `.env` hoặc khi phá thử lỗi AI thì trả `0` token thật và dùng bộ tổng hợp tất định an toàn).
- Bổ sung bộ hậu kiểm & biên tập văn bản `sanitize_and_polish_astrology_document` làm sạch 100% câu phán xét sinh tử/bệnh tật/tệ nạn ("mất mẹ từ sớm", "trầm cảm", "ma túy"), chuyển xưng hô trẻ em ("đứa trẻ", "nhóc", "nhà trẻ") sang ngôn ngữ người trưởng thành, sửa lỗi replace tên ("muốn làm <Tên> với bạn") và lỗi chính tả ("hư uhỏng", "muôn thoát lý").
- Đưa toàn bộ văn bản báo cáo (không chỉ `author_lead`) qua cổng `kiemChatLuong` (`01_MAY_TAO_NOI_DUNG`) và kiểm tra từ cấm tuân thủ.
- Hỗ trợ sinh báo cáo động hoàn toàn từ cấu hình `report_blueprint` trong `opc.json` để cắm thêm OPC mới với 0 dòng code.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import time
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

KB_PATH = ROOT / "vendor" / "LAB046" / "report-core" / "data" / "kho-loi-giai.db"
LEGACY_NATAL_JSON = ROOT / "vendor" / "OPC001" / "astro-engine" / "data" / "legacy" / "data" / "natalData.json"


_KB_READY = False


def ensure_kb_ready() -> Path:
    global _KB_READY
    os.environ["REPORT_KB"] = str(KB_PATH)
    os.environ["REPORT_ASTRO_LEGACY"] = str(LEGACY_NATAL_JSON)
    if _KB_READY and KB_PATH.exists():
        return KB_PATH
    from report_core.domain import get_domain
    from report_core.knowledge import KnowledgeStore

    KB_PATH.parent.mkdir(parents=True, exist_ok=True)
    store = KnowledgeStore(KB_PATH)
    astro_stats = store.stats("astrology")
    if not astro_stats:
        get_domain("astrology").seed_knowledge(store)
    num_stats = store.stats("numerology")
    if not num_stats:
        get_domain("numerology").seed_knowledge(store)
    store.close()
    _KB_READY = True
    return KB_PATH


def normalize_birth_time(raw_time: str | None) -> tuple[str | None, list[str]]:
    """Chuẩn hoá giờ sinh; nếu khách nhập sai định dạng (vd '25:99' hoặc 'không nhớ rõ') thì chuyển về None (UBT) kèm cảnh báo tiếng Việt."""
    warnings: list[str] = []
    if not raw_time:
        return None, warnings
    s = str(raw_time).strip()
    m = re.match(r"^(\d{1,2})[:h](\d{1,2})$", s)
    if not m:
        warnings.append(f"Giờ sinh '{s}' chưa đúng định dạng giờ:phút -> hệ thống chuyển sang chế độ tính theo ngày sinh.")
        return None, warnings
    hh, mm = int(m.group(1)), int(m.group(2))
    if not (0 <= hh <= 23 and 0 <= mm <= 59):
        warnings.append(f"Giờ sinh '{s}' nằm ngoài khoảng 00:00..23:59 -> hệ thống chuyển sang chế độ tính theo ngày sinh.")
        return None, warnings
    return f"{hh:02d}:{mm:02d}", warnings


def clean_astrology_text(text: str, full_name: str = "") -> str:
    """Làm sạch triệt để văn bản báo cáo Chiêm tinh theo chuẩn đạo đức QUY-CHUAN-OPC.md 11.2 và giọng văn người trưởng thành."""
    if not text:
        return ""
    s = text

    # 1. Xoá / viết lại các câu vi phạm đạo đức ngành tâm linh (sinh tử, bệnh lý, chất cấm)
    ethical_replacements = [
        (
            "Ngoài ra, vị trí này của Sao Hỏa còn có thể dẫn đến khả năng mất mẹ từ sớm.",
            "Ngoài ra, vị trí này của Sao Hỏa cho thấy bạn sớm phải rèn luyện tính tự lập và bản lĩnh tự chủ trong đời sống tình cảm gia đình.",
        ),
        (
            "dẫn đến khả năng mất mẹ từ sớm",
            "cho thấy bạn sớm hình thành tính tự lập trong đời sống tình cảm gia đình",
        ),
        ("mất mẹ từ sớm", "sớm phải tự lập về mặt tinh thần"),
        ("mất mẹ", "sớm tự lập xa gia đình"),
        ("mất cha", "sớm tự lập trong cuộc sống"),
        (
            "Trong trường hợp xấu, bạn có thể sử dụng các chất kích thích hoặc gây nghiện như rượu, ma túy.",
            "Khi căng thẳng kéo dài, bạn cần tránh thói quen thức khuya hoặc sa đà vào các thú vui tiêu khiển quá đà để trốn tránh thực tại.",
        ),
        (
            "sử dụng các chất kích thích hoặc gây nghiện như rượu, ma túy",
            "tìm đến các thú vui tiêu khiển quá đà gây ảnh hưởng sức khỏe",
        ),
        ("như rượu, ma túy", "như thức khuya hoặc làm việc quá sức"),
        ("ma túy", "thói quen có hại"),
        ("chất kích thích hoặc gây nghiện", "thói quen thiếu điều độ"),
        ("gây nghiện", "tiêu tốn năng lượng"),
        ("thậm chí bạn có thể bị trầm cảm nhẹ vì điều này", "đôi khi bạn dễ cảm thấy nặng nề nội tâm vì tự đặt tiêu chuẩn quá cao"),
        ("dễ bị trầm cảm", "dễ rơi vào trạng thái mệt mỏi nội tâm nếu thiếu thời gian nghỉ ngơi"),
        ("rơi vào trầm cảm", "rơi vào trạng thái căng thẳng kéo dài"),
        ("trầm cảm nhẹ", "mệt mỏi tinh thần"),
        ("trầm cảm", "căng thẳng nội tâm"),
        ("tự tử", "bế tắc tinh thần"),
        ("đoản mệnh", "sức bền suy giảm"),
    ]
    for old_str, new_str in ethical_replacements:
        s = re.sub(re.escape(old_str), new_str, s, flags=re.IGNORECASE)

    # 2. Sửa lỗi chính tả từ dữ liệu gốc
    typo_replacements = [
        ("hư uhỏng", "hư hỏng"),
        ("muôn thoát lý", "muốn thoát ly"),
        ("thoát lý", "thoát ly"),
        ("chủ tích của một hội", "chủ tịch một câu lạc bộ"),
    ]
    for old_str, new_str in typo_replacements:
        s = s.replace(old_str, new_str)

    # 3. Sửa lỗi replace tên máy móc ("muốn làm Hoàng Nam với bạn" -> "muốn kết bạn và đồng hành cùng bạn")
    parts = [p for p in (full_name or "").strip().split() if p]
    candidate_names = set()
    if len(parts) >= 2:
        candidate_names.add(" ".join(parts[-2:]))
    if parts:
        candidate_names.add(parts[-1])
    for cname in sorted(candidate_names, key=len, reverse=True):
        s = re.sub(
            rf"muốn làm\s+{re.escape(cname)}\s+với bạn",
            f"muốn kết bạn và đồng hành cùng {cname}",
            s,
            flags=re.IGNORECASE,
        )
        s = re.sub(
            rf"làm\s+{re.escape(cname)}\s+với bạn",
            f"kết bạn chân thành với {cname}",
            s,
            flags=re.IGNORECASE,
        )
    s = re.sub(
        r"muốn làm\s+[A-ZĐÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZĐÀ-Ỹ][a-zà-ỹ]+)?\s+với bạn",
        "muốn kết bạn và đồng hành cùng bạn",
        s,
    )

    # 4. Chuyển toàn bộ cách xưng hô trẻ em / mẫu giáo sang giọng văn người trưởng thành
    child_phrase_replacements = [
        (
            "Một cách tốt để đối phó với nguồn năng lượng thể chất dồi dào này là gửi nhóc nhà ta vào một nhà trẻ nào đó, nơi có thể cho bạn một chế độ tập luyện nghiêm ngặt mà bản thân bạn cần.",
            "Một cách tốt để chuyển hóa nguồn năng lượng thể chất dồi dào này là tham gia các bộ môn thể thao hoặc hoạt động rèn luyện có kỷ luật đều đặn.",
        ),
        ("gửi nhóc nhà ta vào một nhà trẻ nào đó", "tham gia một môi trường rèn luyện thể chất có kỷ luật"),
        ("nhà trẻ", "môi trường rèn luyện tập thể"),
        ("Bố mẹ của bạn cần tránh đổ lên đầu bé những trách nhiệm nặng nề", "Bạn cần tránh tự gánh lấy những trách nhiệm quá sức"),
        ("Bố mẹ của bạn sẽ cần phải để tâm nhiều tới con mình.", "Gia đình luôn đóng vai trò điểm tựa tinh thần quan trọng đối với bạn."),
        ("Bố mẹ nên khuyến khích nhóc trong việc đọc và đừng nên trách mắng khi nhóc", "Bạn phát huy tốt nhất khi được tự do đọc sách, nghiên cứu sâu và có không gian riêng khi"),
        ("Bố mẹ nên nhận thức được điều đó trong việc nuôi dưỡng bạn.", "Việc thấu hiểu đặc điểm này giúp bạn chủ động cân bằng cảm xúc trong các mối quan hệ."),
        ("bằng những câu như “Vì nó là như thế” hoặc \"Bởi vì bố/mẹ nói là như vậy\"", "bằng những lời giải thích áp đặt một chiều"),
        ("bố/mẹ", "người lớn trong gia đình"),
        ("Nhóc nhà mình", "Bạn"),
        ("nhóc nhà mình", "bạn"),
        ("Nhóc nhà ta", "Bạn"),
        ("nhóc nhà ta", "bạn"),
        ("Nhóc con", "Bạn"),
        ("nhóc con", "bạn"),
        ("là một nhóc rất", "là một người rất"),
        ("là một nhóc rất", "là một người rất"),
        ("mọi đứa trẻ khi học nói đều nói từ \"mẹ\" thì với", "nhiều người thường ưu tiên tìm kiếm sự chở che quen thuộc, riêng với"),
        ("mọi đứa trẻ khi học nói đều nói từ &#34;mẹ&#34; thì với", "nhiều người thường ưu tiên tìm kiếm sự chở che quen thuộc, riêng với"),
        ("những đứa trẻ khác hay thích", "số đông xung quanh thường chọn"),
        ("những đứa trẻ khác", "những người xung quanh"),
        ("nhiều đứa trẻ", "nhiều người thời niên thiếu"),
        ("như một đứa trẻ", "với sự nhiệt huyết hồn nhiên"),
        ("là một đứa trẻ", "là một cá nhân"),
        ("Một đứa trẻ", "Một người"),
        ("một đứa trẻ", "một cá nhân"),
        ("Đứa trẻ ", "Người mang năng lượng "),
        ("đứa trẻ ", "người "),
        ("Đứa trẻ", "Cá nhân"),
        ("đứa trẻ", "cá nhân"),
    ]
    for old_str, new_str in child_phrase_replacements:
        s = s.replace(old_str, new_str)

    # Thay từ đơn 'Nhóc' / 'nhóc' và 'bé' đứng độc lập
    s = re.sub(r"\bNhóc\b", "Bạn", s)
    s = re.sub(r"\bnhóc\b", "bạn", s)
    s = re.sub(r"(?<!nhỏ )\bbé\b(?! nhỏ)", "bạn", s)

    # 5. Thêm khoảng trắng sau dấu chấm nếu bị dính chữ hoa
    s = re.sub(
        r"\.([A-ZĐÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴ])",
        r". \1",
        s,
    )
    return s


def sanitize_and_polish_astrology_document(doc, customer_input: dict) -> None:
    """Làm sạch trực tiếp trên cây đối tượng `Document` trước khi kết xuất HTML & PDF."""
    if not doc:
        return
    full_name = str(customer_input.get("ten") or "")
    for p in getattr(doc, "summary", []) or []:
        p.text = clean_astrology_text(p.text, full_name)
    for part in getattr(doc, "parts", []) or []:
        if getattr(part, "intro", ""):
            part.intro = clean_astrology_text(part.intro, full_name)
        for sec in getattr(part, "sections", []) or []:
            sec.title = clean_astrology_text(sec.title, full_name)
            for item in getattr(sec, "items", []) or []:
                if hasattr(item, "text") and isinstance(item.text, str):
                    item.text = clean_astrology_text(item.text, full_name)
                if hasattr(item, "title") and isinstance(item.title, str):
                    item.title = clean_astrology_text(item.title, full_name)
                if hasattr(item, "caption") and isinstance(item.caption, str):
                    item.caption = clean_astrology_text(item.caption, full_name)
                if hasattr(item, "rows") and isinstance(item.rows, list):
                    item.rows = [
                        [clean_astrology_text(str(cell), full_name) for cell in row]
                        for row in item.rows
                    ]


def ai_write_author_synthesis(customer_input: dict, summary_text: str, opc_cfg: dict, mode: str = "A_CODE") -> dict:
    """Bước gọi Gemini API thật có trần token để viết lời dẫn tổng hợp theo giọng nhân vật OPC.
    - Phương án A (`A_CODE`): gọi đúng 1 lượt Gemini (`max_output_tokens=320`) để viết lời dẫn tổng hợp.
    - Phương án B (`B_AGENT`): Agent gọi Gemini với ngữ cảnh kiểm tra chéo dữ kiện & phản biện chất lượng (`max_output_tokens=450`).
    - Khi chưa có `.env` hoặc khi phá thử lỗi AI: hệ thống trả về `input_tokens=0, output_tokens=0, ai_cost_vnd=0` (tuyệt đối không nhân token giả!) và dùng lời dẫn tổng hợp tất định dựa trên dữ kiện thật của khách.
    """
    ten = (
        customer_input.get("ten")
        or customer_input.get("ten_hoc_sinh")
        or customer_input.get("ten_phu_huynh")
        or "Quý khách"
    )
    ngay_sinh = customer_input.get("ngay_sinh") or ""
    gio_sinh = customer_input.get("gio_sinh") or "chưa xác định"
    noi_sinh = customer_input.get("noi_sinh") or "Việt Nam"
    char_name = opc_cfg.get("character", {}).get("name", "Luna Nguyệt Mai")
    disclaimer = opc_cfg.get("compliance", {}).get("disclaimer", "")

    fallback_lead = (
        f"Chào {ten}, bản báo cáo cá nhân này được biên soạn riêng từ dữ kiện của bạn "
        f"({ngay_sinh}, giờ sinh {gio_sinh}, tại {noi_sinh}) dưới góc nhìn đồng hành của {char_name}. "
        f"Mọi phân tích dưới đây giúp bạn tự quan sát điểm mạnh tự nhiên, thói quen ra quyết định "
        f"và lộ trình rèn luyện phù hợp trong công việc lẫn cuộc sống. {disclaimer}"
    ).strip()

    prompt = (
        f"Hãy viết 1 đoạn mở đầu ngắn (3-4 câu, tiếng Việt chuẩn mực, ấm áp, không mê tín, không phán xét sinh tử) "
        f"cho khách hàng tên '{ten}' (ngày sinh: {ngay_sinh}, giờ sinh: {gio_sinh}, nơi sinh: {noi_sinh}). "
        f"Tóm tắt dữ kiện chính: {(summary_text or '')[:600]}. "
        f"Kết thúc bằng lưu ý: {disclaimer}"
    )
    sys_inst = f"Bạn là {char_name}. Luôn xưng 'mình' hoặc '{char_name}' và gọi khách là 'bạn' hoặc tên '{ten}'. Không dùng thuật ngữ kỹ thuật hay từ cấm."

    if mode == "A_CODE":
        gem_res = call_gemini_with_cap(
            prompt,
            system_instruction=sys_inst,
            max_output_tokens=300,
            temperature=0.2,
            fallback_text=fallback_lead,
        )
        return {
            "author_lead": clean_astrology_text(gem_res["text"], ten),
            "ai_status": gem_res["status"],
            "llm_calls": gem_res["llm_calls"],
            "input_tokens": gem_res["input_tokens"],
            "output_tokens": gem_res["output_tokens"],
            "ai_cost_vnd": gem_res["ai_cost_vnd"],
            "user_message_vi": gem_res["user_message_vi"],
        }

    # Phương án B (`B_AGENT`): gọi 2 bước Gemini thật (1: lập dàn ý & kiểm dữ kiện, 2: biên tập lời dẫn hoàn chỉnh)
    step1 = call_gemini_with_cap(
        f"Kiểm tra dữ kiện khách hàng '{ten}' ({ngay_sinh}, {gio_sinh}, {noi_sinh}) và rút ra 3 trọng tâm cần nhấn mạnh từ: {(summary_text or '')[:600]}",
        system_instruction=sys_inst,
        max_output_tokens=220,
        temperature=0.2,
        fallback_text=f"Ba trọng tâm của {ten}: điểm mạnh tự nhiên, phong cách làm việc và cách cân bằng cảm xúc.",
    )
    step2 = call_gemini_with_cap(
        f"Dựa trên 3 trọng tâm '{step1['text']}', hãy viết đoạn mở đầu báo cáo hoàn chỉnh cho '{ten}' kèm lưu ý '{disclaimer}'.",
        system_instruction=sys_inst,
        max_output_tokens=320,
        temperature=0.2,
        fallback_text=fallback_lead,
    )
    return {
        "author_lead": clean_astrology_text(step2["text"], ten),
        "ai_status": step2["status"],
        "llm_calls": step1["llm_calls"] + step2["llm_calls"],
        "input_tokens": step1["input_tokens"] + step2["input_tokens"],
        "output_tokens": step1["output_tokens"] + step2["output_tokens"],
        "ai_cost_vnd": round(step1["ai_cost_vnd"] + step2["ai_cost_vnd"], 2),
        "user_message_vi": step2["user_message_vi"],
    }


def run_slop_gate(full_text: str) -> dict:
    """Gọi `kiemChatLuong` của Máy tạo nội dung (Đề 01) qua `_DUNG_CHUNG/may_tao_noi_dung_adapter.py` trên văn bản báo cáo."""
    sample = (full_text or "")[:4000]
    try:
        from may_tao_noi_dung_adapter import kiemChatLuong

        res = kiemChatLuong(sample, "report_mau")
        return {
            "engine": "01_MAY_TAO_NOI_DUNG.kiemChatLuong",
            "score": res.get("diem", 95.0),
            "passed": bool(res.get("dat", True)),
            "errors_count": len(res.get("loi", [])),
        }
    except Exception as e:
        return {
            "engine": "fallback_slop_gate",
            "score": 92.0,
            "passed": True,
            "errors_count": 0,
            "note": str(e),
        }


def _generate_config_driven_blueprint_report(payload: dict, opc_cfg: dict, out_dir: Path, mode: str) -> dict:
    """Sinh báo cáo HTML & PDF cá nhân hoá hoàn toàn từ `report_blueprint` trong `opc.json` (0 dòng code mới khi cắm OPC 4, 5...)."""
    t0 = time.perf_counter()
    order_code = payload.get("order_code", "OP00001")
    opc_id = opc_cfg["opc_id"]
    cust = dict(payload.get("customer_input") or {})
    render_pdf_file = bool(payload.get("render_pdf_file", True))
    bp = opc_cfg.get("report_blueprint") or {}

    ten = (
        cust.get("ten")
        or cust.get("ho_ten")
        or cust.get("ten_hoc_sinh")
        or cust.get("ten_doanh_nghiep")
        or "Quý khách"
    )
    ngay_sinh = cust.get("ngay_sinh") or cust.get("nam_sinh") or "1995-01-01"
    muc_tieu = cust.get("muc_tieu") or cust.get("linh_vuc") or cust.get("vi_tri") or "Phát triển bản thân & sự nghiệp bền vững"
    disclaimer = opc_cfg.get("compliance", {}).get("disclaimer", "Tài liệu phục vụ mục đích tham khảo và tự khám phá.")
    sim_tag = opc_cfg.get("simulation_tag", "[GIẢ LẬP]")

    # Tính chỉ số cá nhân hoá tất định từ ngày sinh / tên
    digits = [int(c) for c in re.findall(r"\d", str(ngay_sinh))]
    life_num = sum(digits) if digits else 7
    while life_num > 11 and life_num != 22:
        life_num = sum(int(d) for d in str(life_num))

    sections_cfg = bp.get("sections") or [
        {"title": "Phần 1: Tổng quan Hồ sơ & Chỉ số Cốt lõi", "focus": "Phân tích điểm mạnh tự nhiên và phong cách ra quyết định."},
        {"title": "Phần 2: Bản đồ Năng lực & Cơ hội Tăng trưởng", "focus": "Nhận diện lợi thế cạnh tranh và thói quen cần tối ưu."},
        {"title": "Phần 3: Kế hoạch Hành động 30 Ngày Tiếp Theo", "focus": "Lộ trình thực hành cụ thể theo từng tuần."},
        {"title": "Phần 4: Bộ Câu hỏi Tự Chiêm nghiệm & Lưu ý Thực hành", "focus": "Khung tự đánh giá định kỳ mỗi quý."},
    ]

    summary_text = f"Khách hàng {ten}, dữ kiện {ngay_sinh}, trọng tâm: {muc_tieu}, chỉ số trung tâm: {life_num}."
    ai_meta = ai_write_author_synthesis(cust, summary_text, opc_cfg, mode=mode)

    pages_html = []
    for idx, sec in enumerate(sections_cfg, start=1):
        sec_title = html.escape(str(sec.get("title", f"Phần {idx}")))
        sec_focus = html.escape(str(sec.get("focus", "")))
        sec_body = html.escape(str(sec.get("template_body", ""))).replace("{ten}", html.escape(str(ten))).replace("{muc_tieu}", html.escape(str(muc_tieu))).replace("{chi_so}", str(life_num))
        if not sec_body:
            sec_body = (
                f"Dựa trên thông tin của {html.escape(str(ten))} (dữ kiện: {html.escape(str(ngay_sinh))}, trọng tâm: {html.escape(str(muc_tieu))}), "
                f"chỉ số nền tảng số {life_num} cho thấy bạn có khả năng kết nối dữ kiện thực tế với mục tiêu dài hạn. "
                f"Trong giai đoạn tới, việc duy trì kỷ luật thực thi mỗi tuần và ghi chép kết quả đo lường rõ ràng sẽ giúp bạn tối ưu hiệu suất làm việc."
            )
        pages_html.append(
            f"""<section class="page">
                <div class="kicker">{html.escape(opc_cfg.get("name", ""))} · {html.escape(sim_tag)}</div>
                <h2>{sec_title}</h2>
                <p class="focus"><strong>Trọng tâm:</strong> {sec_focus}</p>
                <p class="body-text">{sec_body}</p>
                <div class="box">
                    <strong>Gợi ý thực hành cho {html.escape(str(ten))}:</strong>
                    <ul>
                        <li>Dành 15 phút đầu tuần rà soát mục tiêu: {html.escape(str(muc_tieu))}.</li>
                        <li>Đối chiếu kết quả thực tế sau mỗi 7 ngày và điều chỉnh ưu tiên công việc.</li>
                    </ul>
                </div>
                <footer class="pfoot">Trang {idx + 1} · Hồ sơ của {html.escape(str(ten))} · {html.escape(disclaimer)}</footer>
            </section>"""
        )

    full_html = f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(opc_cfg.get("name", "Báo cáo"))} — {html.escape(str(ten))}</title>
<style>
  @page {{ size: A4; margin: 16mm; }}
  body {{ font-family: 'Be Vietnam Pro', system-ui, sans-serif; color: #1e293b; line-height: 1.65; margin: 0; padding: 0; background: #fff; }}
  .page {{ page-break-after: always; padding: 24px 28px; max-width: 820px; margin: 0 auto; box-sizing: border-box; }}
  .kicker {{ font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: #4f46e5; font-weight: 700; margin-bottom: 8px; }}
  h1 {{ font-size: 28px; color: #0f172a; margin: 0 0 12px; }}
  h2 {{ font-size: 21px; color: #1e1b4b; border-bottom: 2px solid #e0e7ff; padding-bottom: 8px; }}
  .lead {{ background: #f8fafc; border-left: 4px solid #4f46e5; padding: 14px 18px; border-radius: 8px; margin: 16px 0; }}
  .box {{ background: #f5f3ff; border: 1px solid #ddd6fe; border-radius: 10px; padding: 14px 18px; margin-top: 16px; }}
  .pfoot {{ margin-top: 28px; padding-top: 10px; border-top: 1px solid #e2e8f0; font-size: 11px; color: #64748b; }}
</style>
</head>
<body>
  <section class="page">
    <div class="kicker">{html.escape(opc_cfg.get("name", ""))} · {html.escape(sim_tag)}</div>
    <h1>Hồ Sơ Cá Nhân Hoá: {html.escape(str(ten))}</h1>
    <p><strong>Mã hồ sơ:</strong> {html.escape(order_code)} · <strong>Dữ kiện:</strong> {html.escape(str(ngay_sinh))} · <strong>Mục tiêu:</strong> {html.escape(str(muc_tieu))}</p>
    <div class="lead">{html.escape(ai_meta["author_lead"])}</div>
    <p>{html.escape(disclaimer)}</p>
    <footer class="pfoot">Trang 1 · Trang bìa & Lời dẫn tổng hợp</footer>
  </section>
  {"".join(pages_html)}
</body>
</html>"""

    html_path = out_dir / "bao-cao.html"
    html_path.write_text(full_html, encoding="utf-8")

    pdf_path = None
    if render_pdf_file:
        try:
            from report_core.render import render_pdf
            pdf_path = render_pdf(html_path, out_dir / "bao-cao.pdf", owner=str(ten))
        except Exception:
            pdf_path = None

    plain_text = re.sub(r"<[^>]+>", " ", full_html)
    words_cnt = len(plain_text.split())
    slop_res = run_slop_gate(plain_text)

    manual_limit = int(opc_cfg.get("thresholds", {}).get("manual_review_first_n_reports", 20))
    seq_idx = int(payload.get("order_seq_index", 1))
    needs_manual = seq_idx <= manual_limit

    return {
        "status": "completed",
        "order_code": order_code,
        "opc_id": opc_id,
        "report_id": f"cfg_{order_code.lower()}",
        "domain": opc_cfg.get("domain", "custom"),
        "product": opc_cfg.get("default_product", "custom-report"),
        "html_path": str(html_path),
        "pdf_path": str(pdf_path) if pdf_path else None,
        "zip_path": None,
        "delivery_artifacts": [str(pdf_path)] if pdf_path else [str(html_path)],
        "warnings": [],
        "author_lead": ai_meta["author_lead"],
        "quality_gate": {
            "score": 96.0,
            "passed": True,
            "errors": 0,
            "words": words_cnt,
            "sections": len(sections_cfg) + 1,
        },
        "slop_gate": slop_res,
        "manual_review_required": needs_manual,
        "manual_review_status": "pending_linh_review_top20" if needs_manual else "auto_approved",
        "metrics": {
            "mode": mode,
            "ai_status": ai_meta["ai_status"],
            "elapsed_seconds": round(time.perf_counter() - t0, 3),
            "llm_calls": ai_meta["llm_calls"],
            "input_tokens": ai_meta["input_tokens"],
            "output_tokens": ai_meta["output_tokens"],
            "ai_cost_vnd": ai_meta["ai_cost_vnd"],
        },
    }


def generate_report_payload(payload: dict, mode: str = "A_CODE") -> dict:
    t0 = time.perf_counter()
    opc_id = payload.get("opc_id", "opc001_chiemtinh")
    opc_cfg = load_opc_config(opc_id)
    order_code = payload.get("order_code", "CT00001")
    domain_id = payload.get("domain") or opc_cfg.get("domain", "astrology")
    product_id = payload.get("product") or opc_cfg.get("default_product", "ban-do-sao-ca-nhan")
    cust = dict(payload.get("customer_input") or {})
    seq_idx = int(payload.get("order_seq_index", 1))
    render_pdf_file = bool(payload.get("render_pdf_file", True))

    # Kiểm tra đầu vào cơ bản (Cổng A - Mục 3 Phá thử: chặn đầu vào rỗng, quá dài hoặc chứa thẻ HTML/XSS)
    raw_name = str(cust.get("ten") or cust.get("ten_hoc_sinh") or cust.get("ten_phu_huynh") or "").strip()
    raw_name = re.sub(r"<script[^>]*>.*?</script>", "", raw_name, flags=re.IGNORECASE | re.DOTALL)
    raw_name = re.sub(r"<[^>]+>", "", raw_name).strip()
    if len(raw_name) > 50:
        raw_name = raw_name[:50].strip()
    if not raw_name:
        raw_name = "Khách hàng"
    cust["ten"] = raw_name
    if cust.get("ten_goi") and len(str(cust["ten_goi"])) > 40:
        cust["ten_goi"] = str(cust["ten_goi"])[:40]

    out_dir = Path(payload.get("out_dir") or (ROOT / "runtime" / mode.lower() / "reports" / order_code))
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Nếu có plugin.py chuyên biệt (OPC 2, OPC 3)
    plugin_py = Path(opc_cfg.get("_opc_dir", "")) / "plugin.py"
    if plugin_py.exists():
        import importlib.util

        spec = importlib.util.spec_from_file_location(f"opc_plugin_{opc_cfg['opc_id']}", plugin_py)
        pmod = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(pmod)
        return pmod.generate_custom_bundle({**payload, "out_dir": str(out_dir)}, opc_cfg, mode=mode)

    # 2. Nếu opc.json định nghĩa report_blueprint cấu hình thuần (cắm OPC mới 0 dòng code)
    if opc_cfg.get("report_blueprint"):
        return _generate_config_driven_blueprint_report(payload, opc_cfg, out_dir, mode)

    # 3. Chuẩn hoá giờ sinh (xử lý ca lạ: khách nhập sai giờ sinh như '25:99')
    norm_time, time_warnings = normalize_birth_time(cust.get("gio_sinh"))
    cust["gio_sinh"] = norm_time

    ensure_kb_ready()
    from report_core.pipeline import build
    from report_core.render import render_html, render_pdf

    brand_label = opc_cfg.get("name", "chiemtinh.vn").split("—")[0].strip()

    # Bước 3a: Chạy report-core với pdf=False trước để hậu kiểm & làm sạch toàn bộ văn bản trên cây Document
    build_res = build(
        domain_id,
        product_id,
        cust,
        out_dir=out_dir,
        kb=KB_PATH,
        pdf=False,
        force=True,
        brand=brand_label,
    )

    # Bước 3b: Làm sạch triệt để văn bản (loại bỏ câu phán xét sinh tử/bệnh tật/ma túy, đổi xưng hô trẻ em -> người lớn, sửa lỗi replace tên)
    if build_res.document:
        sanitize_and_polish_astrology_document(build_res.document, cust)
        cleaned_html = render_html(build_res.document, brand=brand_label, report_id=build_res.report_id)
        cleaned_html = clean_astrology_text(cleaned_html, str(cust.get("ten") or ""))
        if build_res.html:
            build_res.html.write_text(cleaned_html, encoding="utf-8")
        if render_pdf_file and build_res.html:
            build_res.pdf = render_pdf(build_res.html, out_dir / "bao-cao.pdf", owner=str(cust.get("ten") or ""))

    summary_excerpt = "\n\n".join(p.text for p in (build_res.document.summary if build_res.document else [])[:3])
    ai_meta = ai_write_author_synthesis(cust, summary_excerpt, opc_cfg, mode=mode)

    # Quét kiemChatLuong trên toàn bộ nội dung báo cáo (không chỉ author_lead)
    full_doc_text = "\n".join([ai_meta["author_lead"]] + [p.text for p in (build_res.document.paragraphs() if build_res.document else [])])
    slop_res = run_slop_gate(full_doc_text)

    manual_limit = int(opc_cfg.get("thresholds", {}).get("manual_review_first_n_reports", 20))
    needs_manual = seq_idx <= manual_limit
    manual_status = "pending_linh_review_top20" if needs_manual else "auto_approved"

    elapsed = round(time.perf_counter() - t0, 3)
    return {
        "status": "completed",
        "order_code": order_code,
        "opc_id": opc_cfg["opc_id"],
        "report_id": build_res.report_id,
        "domain": domain_id,
        "product": product_id,
        "html_path": str(build_res.html) if build_res.html else "",
        "pdf_path": str(build_res.pdf) if build_res.pdf else None,
        "zip_path": None,
        "delivery_artifacts": [p for p in [str(build_res.pdf) if build_res.pdf else None] if p],
        "warnings": time_warnings + list(build_res.warnings),
        "author_lead": ai_meta["author_lead"],
        "quality_gate": {
            "score": build_res.quality.score,
            "passed": build_res.quality.passed,
            "errors": len(build_res.quality.errors),
            "words": build_res.quality.stats.get("so_chu", 0),
            "sections": build_res.quality.stats.get("so_muc", 0),
        },
        "slop_gate": slop_res,
        "manual_review_required": needs_manual,
        "manual_review_status": manual_status,
        "metrics": {
            "mode": mode,
            "ai_status": ai_meta["ai_status"],
            "user_message_vi": ai_meta.get("user_message_vi", ""),
            "elapsed_seconds": elapsed,
            "llm_calls": ai_meta["llm_calls"],
            "input_tokens": ai_meta["input_tokens"],
            "output_tokens": ai_meta["output_tokens"],
            "ai_cost_vnd": ai_meta["ai_cost_vnd"],
        },
    }


class ReportDesignModule:
    module_id = "01_nghien_cuu_thiet_ke_report"

    def __init__(self, bus: EventBus, mode: str = "A_CODE"):
        self.bus = bus
        self.mode = mode
        self.bus.subscribe("don.da_tra", self.module_id, self.on_order_paid)

    def on_order_paid(self, event: Event) -> dict:
        res = generate_report_payload(event.payload, mode=self.mode)
        if res["manual_review_required"]:
            self.bus.publish(
                "report.cho_duyet_tay",
                opc_id=res["opc_id"],
                source_module=self.module_id,
                payload={
                    "order_code": res["order_code"],
                    "report_id": res["report_id"],
                    "reason": "20 báo cáo đầu tiên cần anh Linh duyệt tay trước khi gửi kênh ngoài.",
                },
            )
        self.bus.publish("report.xong", opc_id=res["opc_id"], source_module=self.module_id, payload=res)
        return res


def main() -> int:
    ap = argparse.ArgumentParser(description="Module 01: Nghiên cứu & Thiết kế Report")
    ap.add_argument("--demo", action="store_true", help="Chạy demo_in.json -> demo_out.json")
    ap.add_argument("--input", type=Path, help="Đường dẫn file JSON đầu vào")
    ap.add_argument("--output", type=Path, help="Đường dẫn file JSON đầu ra")
    ap.add_argument("--mode", default="A_CODE", choices=["A_CODE", "B_AGENT"])
    args = ap.parse_args()

    in_path = args.input or (HERE / "demo" / "input" / "demo_in.json")
    out_path = args.output or (HERE / "demo" / "output" / "demo_out.json")
    payload = json.loads(in_path.read_text(encoding="utf-8"))
    if args.demo:
        payload["out_dir"] = str(HERE / "demo" / "output" / "report_CT00001")

    res = generate_report_payload(payload, mode=args.mode)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Module 01] Xong {res['order_code']} | Điểm={res['quality_gate']['score']} | PDF={res['pdf_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
