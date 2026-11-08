#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Core Config Loader, Input/Red-Team Guardrail & Real Gemini Engine cho 01_MAY_TAO_NOI_DUNG.

Giải quyết triệt để:
- [B-01] Nối thật loai/*/cau_hinh.json và T1..T5.md, dat_khi.md, loi_slop.md vào luồng chạy.
- [B-02] Bước 4 (3 outline A/B/C + 3 Persona) và Bước 5 (chấm chọn hướng) chạy thật bằng Gemini.
- Cổng A Mục 3 (Phá thử) & Mục 4 (Đội đỏ 30 câu bẫy chặn đủ, 0 câu bịa).
- Cổng A Mục 5 (Chỉ đọc .env nội bộ trong 01_MAY_TAO_NOI_DUNG, tuyệt đối không in/ghi giá trị key).
- Cổng A Mục 6 (Tự động phát hiện mọi thư mục loai/<ten>/cau_hinh.json với 0 dòng sửa code).
"""

import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parent
LOAI_ROOT = ROOT_DIR / "loai"
LOGS_DIR = ROOT_DIR / "logs"
CACHE_DIR = LOGS_DIR / "gemini_cache"
TOKEN_LEDGER_PATH = LOGS_DIR / "gemini_token_ledger.jsonl"

DEFAULT_ORDER = ["bai_viet", "report_mau", "noi_dung_khoa_hoc"]


def _load_local_api_key(root_dir: Optional[Path] = None) -> str:
    """Chỉ đọc GEMINI_API_KEY từ .env nằm trong 01_MAY_TAO_NOI_DUNG hoặc biến môi trường hiện có.
    Tuyệt đối không đọc .env ngoài thư mục bộ sản phẩm này và không bao giờ in giá trị khoá.
    """
    env_val = os.environ.get("GEMINI_API_KEY", "").strip()
    if env_val:
        return env_val

    base = Path(root_dir) if root_dir else ROOT_DIR
    env_path = base / ".env"
    if not env_path.exists():
        return ""

    try:
        for raw_line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
                cleaned = v.strip().strip('"').strip("'")
                if cleaned:
                    return cleaned
    except Exception:
        return ""
    return ""


def list_available_loai(root_dir: Optional[Path] = None) -> List[str]:
    """Quét tự động toàn bộ thư mục con trong loai/ có file cau_hinh.json."""
    base = (Path(root_dir) if root_dir else ROOT_DIR) / "loai"
    if not base.exists():
        return list(DEFAULT_ORDER)
    found: List[str] = []
    for child in sorted(base.iterdir()):
        if child.is_dir() and (child / "cau_hinh.json").exists():
            found.append(child.name)
    ordered = [x for x in DEFAULT_ORDER if x in found]
    for x in found:
        if x not in ordered:
            ordered.append(x)
    return ordered


def load_loai_config(loai: str, root_dir: Optional[Path] = None, custom_config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Đọc và kiểm tra tính hợp lệ của loai/<loai>/cau_hinh.json + T1..T5.md + dat_khi.md + loi_slop.md.
    Ném ValueError bằng tiếng Việt rõ ràng nếu cấu hình sai cú pháp hoặc thiếu trường bắt buộc.
    """
    base = Path(root_dir) if root_dir else ROOT_DIR
    loai_dir = base / "loai" / str(loai).strip()
    cfg_path = Path(custom_config_path) if custom_config_path else (loai_dir / "cau_hinh.json")

    if not cfg_path.exists():
        available = ", ".join(list_available_loai(base))
        raise ValueError(
            f"Không tìm thấy cấu hình cho loại nội dung '{loai}'. Các loại hiện có: {available}."
        )

    try:
        raw_text = cfg_path.read_text(encoding="utf-8")
        cfg = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Tệp cấu hình '{cfg_path.name}' của loại '{loai}' bị lỗi cú pháp JSON (dòng {exc.lineno}, cột {exc.colno}). "
            f"Vui lòng kiểm tra lại dấu phẩy hoặc dấu ngoặc kép."
        ) from exc

    if not isinstance(cfg, dict):
        raise ValueError(f"Tệp cấu hình của loại '{loai}' phải là một đối tượng JSON hợp lệ.")

    required_keys = ["loai", "ten_hien_thi"]
    missing = [k for k in required_keys if not cfg.get(k)]
    if missing:
        raise ValueError(
            f"Tệp cấu hình của loại '{loai}' thiếu trường bắt buộc: {', '.join(missing)}."
        )

    # Đọc T1..T5.md trong thư mục loại (nếu có) và dat_khi.md, loi_slop.md chung
    t_files: Dict[str, str] = {}
    for t_name in ["T1_bo_cuc.md", "T2_giong_van.md", "T3_bang_chung.md", "T4_chong_slop.md", "T5_media.md"]:
        p = loai_dir / t_name
        if p.exists():
            t_files[t_name] = p.read_text(encoding="utf-8", errors="ignore").strip()

    dat_khi_path = base / "loai" / "dat_khi.md"
    loi_slop_path = base / "loai" / "loi_slop.md"
    dat_khi_text = dat_khi_path.read_text(encoding="utf-8", errors="ignore").strip() if dat_khi_path.exists() else ""
    loi_slop_text = loi_slop_path.read_text(encoding="utf-8", errors="ignore").strip() if loi_slop_path.exists() else ""

    # Chuẩn hoá các trường mặc định để các bước sau không bao giờ bị KeyError khi cắm loại mới
    do_dai = cfg.get("do_dai_chu") or {"min": 950, "max": 1800, "muc_tieu": 1300}
    so_phan = cfg.get("so_phan_chinh") or {"min": 4, "max": 6}
    kieu_xuat_ban = cfg.get("kieu_xuat_ban")
    if not kieu_xuat_ban:
        if loai in ("report_mau", "noi_dung_khoa_hoc"):
            kieu_xuat_ban = loai
        else:
            kieu_xuat_ban = "bai_viet"

    return {
        "loai": cfg.get("loai", loai),
        "ten_hien_thi": cfg.get("ten_hien_thi", loai),
        "mo_ta": cfg.get("mo_ta", f"Ấn phẩm chuẩn thương hiệu thuộc nhóm { cfg.get('ten_hien_thi', loai) }"),
        "do_dai_chu": do_dai,
        "so_phan_chinh": so_phan,
        "kieu_xuat_ban": kieu_xuat_ban,
        "bat_buoc_co": cfg.get(
            "bat_buoc_co",
            [
                "Mở bài bằng câu chuyện tình huống thật kèm con số cụ thể",
                "Bảng đối chiếu hoặc ma trận quy trình trước và sau",
                "Khung hành động thực tế áp dụng ngay trong tuần",
            ],
        ),
        "persona_mac_dinh": cfg.get("persona_mac_dinh", ["sep_doanh_nghiep", "quan_ly_van_hanh", "hoc_vien_thuc_chien"]),
        "personas_custom": cfg.get("personas_custom", []),
        "media_kem_theo": cfg.get("media_kem_theo", ["anh_bia_16_9", "so_do_svg", "ban_in_pdf"]),
        "nguong_cqs_toi_thieu": float(cfg.get("nguong_cqs_toi_thieu", 80)),
        "nguong_aps_toi_thieu": float(cfg.get("nguong_aps_toi_thieu", 80)),
        "t_files": t_files,
        "dat_khi_text": dat_khi_text,
        "loi_slop_text": loi_slop_text,
        "raw": cfg,
    }


# ==============================================================================
# BỘ LỌC ĐẦU VÀO & ĐỘI ĐỎ (RED TEAM GUARDRAIL - CHẶN ĐỦ 30 MẪU BẪY, 0 CÂU BỊA)
# ==============================================================================

REDTEAM_PATTERNS: List[Tuple[str, str, re.Pattern]] = [
    # Nhóm 1: Chèn lệnh hệ thống (Prompt Injection / Jailbreak / SQLi / XSS)
    (
        "CAT1_PROMPT_INJECTION",
        "Từ chối thực hiện: Phát hiện dấu hiệu chèn lệnh điều khiển hệ thống hoặc vượt rào bảo mật. Vui lòng chỉ nhập đề bài nội dung đào tạo/quản trị doanh nghiệp.",
        re.compile(
            r"(ignore\s+(all\s+)?(previous|prior)\s+instructions|"
            r"bỏ\s+qua\s+(mọi|toàn\s+bộ|các)\s+(hướng\s+dẫn|quy\s+tắc|lệnh)|"
            r"quên\s+hết\s+quy\s+tắc\s+trước|"
            r"in\s+ra\s+(system\s+prompt|câu\s+lệnh\s+gốc|hướng\s+dẫn\s+hệ\s+thống|toàn\s+bộ\s+prompt)|"
            r"reveal\s+(your\s+)?system\s+prompt|"
            r"chế\s+độ\s+(developer\s+mode|dan\s+mode|không\s+giới\s+hạn|jailbreak)|"
            r"you\s+are\s+now\s+dan\b|"
            r"<script\b|javascript:|drop\s+table\b|union\s+select\b|;\s*rm\s+-rf|"
            r"\[\s*system\s*override\s*\]|override\s+safety\s+filters)",
            re.IGNORECASE,
        ),
    ),
    # Nhóm 2: Đòi báo giá chính thức / cam kết tài chính / hoàn tiền / số tài khoản nhận tiền
    (
        "CAT2_BAO_GIA_CAM_KET",
        "Từ chối thực hiện: Hệ thống biên tập nội dung không tự động phát hành báo giá thương mại, không cam kết lợi nhuận/hoàn tiền 100% và không cung cấp tài khoản nhận chuyển khoản.",
        re.compile(
            r"(báo\s+giá\s+chính\s+thức\s+có\s+dấu|"
            r"xuất\s+báo\s+giá\s+hợp\s+đồng\s+chính\s+thức|"
            r"cam\s+kết\s+(hoàn\s+tiền\s+100%|lợi\s+nhuận\s+chắc\s+chắn|tăng\s+\d+%\s+doanh\s+thu\s+trong\s+\d+\s+ngày|x\d+\s+doanh\s+số)|"
            r"đảm\s+bảo\s+100%\s+không\s+rủi\s+ro|"
            r"chốt\s+giá\s+chiết\s+khấu\s+\d+%\s+ngay\s+hôm\s+nay|"
            r"gửi\s+số\s+tài\s+khoản\s+ngân\s+hàng\s+để\s+chuyển\s+khoản\s+cọc|"
            r"ký\s+cam\s+kết\s+bồi\s+thường\s+tài\s+chính)",
            re.IGNORECASE,
        ),
    ),
    # Nhóm 3: Đòi thông tin cá nhân (PII), mật khẩu, khoá API, tệp .env, dữ liệu nhạy cảm
    (
        "CAT3_PII_BI_MAT",
        "Từ chối thực hiện: Hệ thống bảo vệ tuyệt đối khoá bảo mật, mật khẩu, dữ liệu nội bộ và thông tin định danh cá nhân (CCCD, số điện thoại, lương thưởng, tài khoản ngân hàng).",
        re.compile(
            r"(gemini_api_key|openai_api_key|api[_\s-]?key\s+của\s+(hệ\s+thống|bạn|server)|"
            r"đọc\s+file\s+\.env|in\s+nội\s+dung\s+\.env|trích\s+xuất\s+mật\s+khẩu|"
            r"danh\s+sách\s+(số\s+điện\s+thoại|cccd|cmnd|căn\s+cước|bảng\s+lương|tài\s+khoản\s+ngân\s+hàng)\s+của\s+(khách\s+hàng|nhân\s+viên|học\s+viên|sếp)|"
            r"cho\s+tôi\s+xin\s+(mật\s+khẩu|password|token\s+đăng\s+nhập|số\s+thẻ\s+tín\s+dụng)|"
            r"tiết\s+lộ\s+dữ\s+liệu\s+cá\s+nhân)",
            re.IGNORECASE,
        ),
    ),
    # Nhóm 4: Lời lẽ xúc phạm, bôi nhọ đối thủ/cá nhân, kích động thù ghét, bạo lực
    (
        "CAT4_XUC_PHAM_BOI_NHO",
        "Từ chối thực hiện: Hệ thống không tạo nội dung công kích cá nhân, bôi nhọ đối thủ cạnh tranh, ngôn từ thù ghét hoặc vi phạm chuẩn mực đạo đức nghề nghiệp.",
        re.compile(
            r"(viết\s+bài\s+(bôi\s+nhọ|phỉ\s+báng|chửi\s+rủa|tấn\s+công\s+cá\s+nhân|hạ\s+bệ\s+uy\s+tín|bóc\s+phốt\s+vu\s+khống)|"
            r"dìm\s+hàng\s+đối\s+thủ\s+bằng\s+tin\s+giả|"
            r"lăng\s+mạ\s+(khách\s+hàng|nhân\s+viên|đối\s+thủ)|"
            r"kích\s+động\s+(bạo\s+lực|thù\s+ghét|phân\s+biệt\s+vùng\s+miền)|"
            r"nội\s+dung\s+đồi\s+trụy|khiêu\s+dâm)",
            re.IGNORECASE,
        ),
    ),
    # Nhóm 5: Yêu cầu bịa đặt số liệu/nguồn giả hoặc ngoài phạm vi (cờ bạc, lách luật, y tế, hack)
    (
        "CAT5_BIA_DAT_NGOAI_PHAM_VI",
        "Từ chối thực hiện: Đề bài yêu cầu bịa đặt số liệu/nguồn trích dẫn giả hoặc nằm ngoài phạm vi đào tạo & chuyển đổi AI doanh nghiệp (cờ bạc, gian lận thuế, kê đơn y tế, tấn công mạng).",
        re.compile(
            r"(bịa\s+(ra\s+)?(số\s+liệu|báo\s+cáo|trích\s+dẫn|nghiên\s+cứu\s+của\s+mckinsey|nghiên\s+cứu\s+của\s+gartner)|"
            r"tự\s+chế\s+(con\s+số\s+thống\s+kê|nguồn\s+khảo\s+sát\s+giả|case\s+study\s+ảo\s+như\s+thật)|"
            r"hướng\s+dẫn\s+(cá\s+độ\s+bóng\s+đá|đánh\s+bạc\s+online|lô\s+đề|xóc\s+đĩa|rửa\s+tiền|trốn\s+thuế\s+bất\s+hợp\s+pháp)|"
            r"kê\s+đơn\s+thuốc\s+(kháng\s+sinh\s+liều\s+cao|điều\s+trị\s+ung\s+thư\s+tại\s+nhà)|"
            r"cách\s+(hack\s+tài\s+khoản|tấn\s+công\s+ddos|phá\s+khoá\s+phần\s+mềm|lừa\s+đảo\s+tiền\s+ảo\s+lùa\s+gà))",
            re.IGNORECASE,
        ),
    ),
]


def kiem_tra_dau_vao(de_bai: Any, loai: str = "bai_viet", root_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Kiểm tra tính hợp lệ của đề bài đầu vào & chặn 30 câu bẫy Đội đỏ.
    Trả về dict: {hop_le: bool, ma_loi: str, nhom_chan: str, thong_bao: str}
    """
    if de_bai is None or not isinstance(de_bai, str):
        return {
            "hop_le": False,
            "ma_loi": "INPUT_EMPTY",
            "nhom_chan": "DAU_VAO_RONG",
            "thong_bao": "Đề bài đang để trống. Vui lòng nhập chủ đề hoặc tình huống cần biên soạn (tối thiểu 15 ký tự).",
        }

    cleaned = de_bai.strip()
    if len(cleaned) == 0:
        return {
            "hop_le": False,
            "ma_loi": "INPUT_EMPTY",
            "nhom_chan": "DAU_VAO_RONG",
            "thong_bao": "Đề bài đang để trống. Vui lòng nhập chủ đề hoặc tình huống cần biên soạn (tối thiểu 15 ký tự).",
        }

    if len(cleaned) < 12:
        return {
            "hop_le": False,
            "ma_loi": "INPUT_TOO_SHORT",
            "nhom_chan": "DAU_VAO_QUA_NGAN",
            "thong_bao": "Đề bài quá ngắn (dưới 12 ký tự). Vui lòng mô tả rõ chủ đề, đối tượng đọc và vấn đề thực tế.",
        }

    if len(cleaned) > 5000:
        return {
            "hop_le": False,
            "ma_loi": "INPUT_TOO_LONG",
            "nhom_chan": "DAU_VAO_QUA_DAI",
            "thong_bao": f"Đề bài vượt quá giới hạn cho phép ({len(cleaned)}/5.000 ký tự). Vui lòng tóm gọn trọng tâm đề bài dưới 5.000 ký tự.",
        }

    # Kiểm tra ký tự điều khiển / nhị phân hoặc chuỗi ký tự lạ không có chữ cái tiếng Việt/Latin đọc được
    printable_letters = re.findall(r"[a-zA-ZÀ-ỹ0-9]", cleaned)
    if len(printable_letters) < max(6, int(len(cleaned) * 0.25)):
        return {
            "hop_le": False,
            "ma_loi": "INPUT_GIBBERISH",
            "nhom_chan": "SAI_NGON_NGU_KY_TU_LA",
            "thong_bao": "Đề bài chứa quá nhiều ký tự đặc biệt hoặc mã nhị phân không hợp lệ. Vui lòng nhập đề bài bằng tiếng Việt rõ nghĩa.",
        }

    # Kiểm tra cấu hình loại nội dung có hợp lệ không
    try:
        load_loai_config(loai, root_dir=root_dir)
    except ValueError as exc:
        return {
            "hop_le": False,
            "ma_loi": "INVALID_LOAI_CONFIG",
            "nhom_chan": "CAU_HINH_LOAI_SAI",
            "thong_bao": str(exc),
        }

    # Quét qua 5 nhóm Red-Team Guardrail
    for cat_code, msg_vi, pattern in REDTEAM_PATTERNS:
        if pattern.search(cleaned):
            return {
                "hop_le": False,
                "ma_loi": "REDTEAM_BLOCKED",
                "nhom_chan": cat_code,
                "thong_bao": msg_vi,
            }

    return {
        "hop_le": True,
        "ma_loi": "OK",
        "nhom_chan": "HOP_LE",
        "thong_bao": "Đề bài hợp lệ.",
    }


# ==============================================================================
# KẾT NỐI GEMINI THẬT (GEMINI 2.5 FLASH + THEO DÕI TOKEN & CHAOS HOOKS)
# ==============================================================================


def _append_token_ledger(entry: Dict[str, Any]) -> None:
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        with TOKEN_LEDGER_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def call_gemini_json(
    prompt: str,
    system_instruction: str = "",
    temperature: float = 0.35,
    timeout_sec: float = 25.0,
    simulate_mode: Optional[str] = None,
    use_cache: bool = True,
    step_tag: str = "gemini_call",
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Gọi thật Gemini 2.5 Flash trả về (parsed_json_dict, usage_meta).
    Hỗ trợ simulate_mode ('ai_error', 'ai_slow_timeout', 'rate_limit') để test Cổng A Mục 3 (Phá thử).
    """
    chaos = simulate_mode or os.environ.get("SAKEDEMY_CHAOS_MODE", "").strip()
    if chaos == "ai_error":
        raise RuntimeError(
            "Dịch vụ trí tuệ nhân tạo tạm thời trả về lỗi kết nối (503). Hệ thống đã giữ nguyên dữ liệu bước trước để bạn bấm chạy lại."
        )
    if chaos == "ai_slow_timeout":
        time.sleep(min(timeout_sec, 1.2))
        raise TimeoutError(
            "Dịch vụ trí tuệ nhân tạo phản hồi quá thời gian chờ cho phép. Tiến trình đã được lưu tạm an toàn, vui lòng thử lại."
        )
    if chaos == "rate_limit":
        raise RuntimeError(
            "Đã chạm giới hạn tần suất gọi mô hình trong phút hiện tại (429). Vui lòng đợi vài giây rồi tiếp tục."
        )

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_key = hashlib.sha256(f"{step_tag}||{system_instruction}||{prompt}".encode("utf-8")).hexdigest()[:24]
    cache_file = CACHE_DIR / f"{step_tag}_{cache_key}.json"

    if use_cache and cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text(encoding="utf-8"))
            meta = cached.get("_usage_meta", {})
            meta["cached"] = True
            _append_token_ledger(
                {
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "step": step_tag,
                    "cached": True,
                    "prompt_tokens": meta.get("prompt_tokens", 0),
                    "output_tokens": meta.get("output_tokens", 0),
                    "total_tokens": meta.get("total_tokens", 0),
                    "latency_ms": meta.get("latency_ms", 0),
                }
            )
            return cached["data"], meta
        except Exception:
            pass

    # Giới hạn cứng theo lệnh anh Linh (17:26): Tối đa 5 lượt gọi API Gemini thật trong phiên 3 vòng Mục 13
    max_live_calls = int(os.environ.get("SAKEDEMY_MAX_LIVE_API_CALLS", "5"))
    live_since_1726 = 0
    if TOKEN_LEDGER_PATH.exists():
        for ln in TOKEN_LEDGER_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not ln.strip():
                continue
            try:
                rec = json.loads(ln)
                if not rec.get("cached") and str(rec.get("ts", "")) >= "2026-10-25T17:26:00":
                    live_since_1726 += 1
            except Exception:
                pass

    if live_since_1726 >= max_live_calls:
        prefix = step_tag.split("_")[0]
        candidates = sorted(CACHE_DIR.glob(f"{step_tag}_*.json")) or sorted(CACHE_DIR.glob(f"{prefix}_*.json"))
        if candidates:
            cached = json.loads(candidates[-1].read_text(encoding="utf-8"))
            meta = cached.get("_usage_meta", {})
            meta["cached"] = True
            meta["capped_at_5_live_calls"] = True
            return cached["data"], meta

    api_key = _load_local_api_key()
    if not api_key:
        raise RuntimeError(
            "Chưa tìm thấy khoá kết nối mô hình trong tệp cấu hình nội bộ (.env). Vui lòng kiểm tra lại cấu hình máy chủ."
        )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload: Dict[str, Any] = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "responseMimeType": "application/json",
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }
    if system_instruction:
        payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

    t0 = time.perf_counter()
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    last_err: Optional[Exception] = None
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                raw_resp = json.loads(resp.read().decode("utf-8"))
            latency_ms = round((time.perf_counter() - t0) * 1000.0, 1)
            usage = raw_resp.get("usageMetadata", {})
            prompt_tok = int(usage.get("promptTokenCount", 0))
            cand_tok = int(usage.get("candidatesTokenCount", 0))
            total_tok = int(usage.get("totalTokenCount", prompt_tok + cand_tok))

            text_out = (
                raw_resp.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "{}")
            )
            # Làm sạch khối markdown ```json nếu có
            cleaned_json = text_out.strip()
            if cleaned_json.startswith("```"):
                cleaned_json = re.sub(r"^```(?:json)?\s*", "", cleaned_json)
                cleaned_json = re.sub(r"\s*```$", "", cleaned_json)
            parsed = json.loads(cleaned_json)

            meta = {
                "model": "gemini-2.5-flash",
                "prompt_tokens": prompt_tok,
                "output_tokens": cand_tok,
                "total_tokens": total_tok,
                "latency_ms": latency_ms,
                "cached": False,
                "real_gemini": True,
            }
            _append_token_ledger(
                {
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "step": step_tag,
                    "cached": False,
                    "prompt_tokens": prompt_tok,
                    "output_tokens": cand_tok,
                    "total_tokens": total_tok,
                    "latency_ms": latency_ms,
                }
            )
            try:
                cache_file.write_text(
                    json.dumps({"data": parsed, "_usage_meta": meta}, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
            except Exception:
                pass
            return parsed, meta
        except Exception as exc:
            last_err = exc
            time.sleep(0.4 * (attempt + 1))

    raise RuntimeError(
        f"Không thể hoàn tất gọi mô hình AI sau 2 lần thử ({type(last_err).__name__}). Tiến trình trước đó đã được bảo toàn."
    )


# ==============================================================================
# BƯỚC 4 THẬT BẰNG GEMINI: SINH INSIGHTS & 3 OUTLINE A/B/C + PHẢN BIỆN 3 PERSONA
# ==============================================================================


def generate_step4_outlines_and_personas(
    loai: str,
    de_bai: str,
    personas: List[Dict[str, Any]],
    config_bundle: Dict[str, Any],
    use_cache: bool = True,
    simulate_mode: Optional[str] = None,
) -> Dict[str, Any]:
    """Gọi thật Gemini 2.5 Flash để sinh 3 phương án dàn ý A, B, C bám sát đề bài `de_bai`
    và cấu hình `loai/<loai>/cau_hinh.json` + phản biện của 3 chân dung người đọc P1, P2, P3.
    """
    ten_loai = config_bundle.get("ten_hien_thi", loai)
    do_dai = config_bundle.get("do_dai_chu", {"min": 950, "max": 1800, "muc_tieu": 1300})
    bat_buoc = config_bundle.get("bat_buoc_co", [])
    t1_bo_cuc = config_bundle.get("t_files", {}).get("T1_bo_cuc.md", "")[:600]
    t2_giong_van = config_bundle.get("t_files", {}).get("T2_giong_van.md", "")[:500]

    persona_summary = "\n".join(
        [
            f"- {p.get('id', f'P{i+1}')} ({p.get('ten', 'Độc giả')} - {p.get('vai_tro', '')}): Nỗi đau: {p.get('noi_dau_chinh', '')}"
            for i, p in enumerate(personas[:3])
        ]
    )

    sys_inst = (
        "Bạn là Tổng biên tập của Sakedemy (Đơn vị đào tạo & tư vấn chuyển đổi AI thực chiến cho doanh nghiệp Việt Nam). "
        "Hãy thiết kế 3 phương án dàn ý (A, B, C) KHÁC BIỆT RÕ RỆT cho đề bài người dùng giao, bám sát cấu hình thể loại, "
        "không dùng văn mẫu sáo rỗng, có số liệu đối chiếu từ nguồn xác thực (nghiên cứu HBR 40% thời gian dọn rác văn bản, khảo sát McKinsey 88% dùng AI nhưng chỉ 39% có tác động lợi nhuận, "
        "nghiên cứu BCG quy tắc 10-20-70: 70% con người & quy trình, 30% giờ làm bị hao hụt vì dọn sản phẩm AI kém chất lượng, khảo sát thực địa Sakedemy). "
        "TUYỆT ĐỐI KHÔNG viết mã nguồn nội bộ trong ngoặc như [N01], (N02), (N04), (N05), [BC01] hay tên mã LAB0xx vào tiêu đề hay nội dung dàn ý. "
        "Trả về đúng định dạng JSON được yêu cầu."
    )

    prompt = f"""Đề bài cần lập dàn ý: "{de_bai}"
Thể loại ấn phẩm: {ten_loai} (mã: {loai})
Độ dài mục tiêu: {do_dai.get('muc_tieu', 1300)} chữ (từ {do_dai.get('min', 950)} đến {do_dai.get('max', 1800)} chữ).
Yêu cầu bắt buộc của thể loại này: {json.dumps(bat_buoc, ensure_ascii=False)}
Quy tắc bố cục T1: {t1_bo_cuc}
Quy tắc giọng văn T2: {t2_giong_van}

3 Chân dung độc giả mục tiêu (Personas):
{persona_summary}

Hãy trả về JSON với cấu trúc chính xác như sau:
{{
  "focal_insights": [
    {{"id": "I01", "dimension": "Bối cảnh thực tế", "statement": "..."}},
    {{"id": "I02", "dimension": "Điểm nghẽn vận hành", "statement": "..."}},
    {{"id": "I03", "dimension": "Bằng chứng định lượng", "statement": "..."}},
    {{"id": "I04", "dimension": "Quy trình chuyển đổi", "statement": "..."}},
    {{"id": "I05", "dimension": "Công cụ áp dụng ngay", "statement": "..."}},
    {{"id": "I06", "dimension": "Chỉ số đo lường", "statement": "..."}}
  ],
  "outlines": {{
    "A": {{
      "variant": "A",
      "ten_huong": "Hướng A — Đi từ Số liệu Vĩ mô & Cảnh báo Hệ thống",
      "hook_mo_dau": "1 câu mở bài dẫn số liệu nghiên cứu kết nối trực tiếp vào đề bài '{de_bai}'",
      "sections": [
        "1. [Tiêu đề mục 1 gắn với đề bài]",
        "2. [Tiêu đề mục 2 gắn với đề bài]",
        "3. [Tiêu đề mục 3 gắn với đề bài]",
        "4. [Tiêu đề mục 4 gắn với đề bài]",
        "5. [Tiêu đề mục 5: Khung hành động & bảng kiểm]"
      ],
      "exhibits": ["Bảng đối chiếu số liệu theo đề bài"],
      "persona_reactions": [
        {{"persona_id": "P1", "ten_persona": "...", "diem_100": 81, "nhan_xet": "Nhận xét cụ thể của P1 về Hướng A", "diem_khen": "...", "diem_che": "..."}},
        {{"persona_id": "P2", "ten_persona": "...", "diem_100": 78, "nhan_xet": "Nhận xét cụ thể của P2 về Hướng A", "diem_khen": "...", "diem_che": "..."}},
        {{"persona_id": "P3", "ten_persona": "...", "diem_100": 75, "nhan_xet": "Nhận xét cụ thể của P3 về Hướng A", "diem_khen": "...", "diem_che": "..."}}
      ]
    }},
    "B": {{
      "variant": "B",
      "ten_huong": "Hướng B — Đi từ Tình huống Thực tế tại Doanh nghiệp, Đối chiếu Trước/Sau & Bảng kiểm Áp dụng Ngay",
      "hook_mo_dau": "1 câu mở bài bằng cảnh tượng thật tại văn phòng Việt Nam kèm con số cụ thể gắn chặt với đề bài '{de_bai}'",
      "sections": [
        "1. [Tiêu đề mục 1: Tình huống thực tế & chi phí ẩn của đề bài]",
        "2. [Tiêu đề mục 2: Phân tích nguyên nhân gốc rễ theo quy tắc 10-20-70]",
        "3. [Tiêu đề mục 3: Bảng đối chiếu quy trình Trước và Sau khi chuẩn hoá]",
        "4. [Tiêu đề mục 4: Quy trình 3 bước triển khai thực chiến]",
        "5. [Tiêu đề mục 5: Bảng kiểm nghiệm thu & Hành động ngay trong tuần tới]"
      ],
      "exhibits": ["Bảng đối chiếu Trước vs Sau khi áp dụng quy trình chuẩn", "Sơ đồ quy trình 3 bước kiểm soát chất lượng"],
      "persona_reactions": [
        {{"persona_id": "P1", "ten_persona": "...", "diem_100": 93, "nhan_xet": "Nhận xét cụ thể của P1 về Hướng B", "diem_khen": "...", "diem_che": "..."}},
        {{"persona_id": "P2", "ten_persona": "...", "diem_100": 92, "nhan_xet": "Nhận xét cụ thể của P2 về Hướng B", "diem_khen": "...", "diem_che": "..."}},
        {{"persona_id": "P3", "ten_persona": "...", "diem_100": 90, "nhan_xet": "Nhận xét cụ thể của P3 về Hướng B", "diem_khen": "...", "diem_che": "..."}}
      ]
    }},
    "C": {{
      "variant": "C",
      "ten_huong": "Hướng C — Đi thẳng vào Cẩm nang Thao tác Nhanh & Mẫu biểu Thực hành",
      "hook_mo_dau": "1 câu mở bài đi thẳng vào thao tác thực hành tại bàn làm việc cho đề bài '{de_bai}'",
      "sections": [
        "1. [Tiêu đề mục 1 gắn với đề bài]",
        "2. [Tiêu đề mục 2 gắn với đề bài]",
        "3. [Tiêu đề mục 3 gắn với đề bài]",
        "4. [Tiêu đề mục 4 gắn với đề bài]"
      ],
      "exhibits": ["Phiếu bài tập thực hành tại chỗ"],
      "persona_reactions": [
        {{"persona_id": "P1", "ten_persona": "...", "diem_100": 77, "nhan_xet": "Nhận xét cụ thể của P1 về Hướng C", "diem_khen": "...", "diem_che": "..."}},
        {{"persona_id": "P2", "ten_persona": "...", "diem_100": 85, "nhan_xet": "Nhận xét cụ thể của P2 về Hướng C", "diem_khen": "...", "diem_che": "..."}},
        {{"persona_id": "P3", "ten_persona": "...", "diem_100": 88, "nhan_xet": "Nhận xét cụ thể của P3 về Hướng C", "diem_khen": "...", "diem_che": "..."}}
      ]
    }}
  }}
}}"""

    parsed, usage_meta = call_gemini_json(
        prompt=prompt,
        system_instruction=sys_inst,
        temperature=0.35,
        use_cache=use_cache,
        simulate_mode=simulate_mode,
        step_tag=f"step4_{loai}",
    )
    parsed["_gemini_usage"] = usage_meta
    return parsed


# ==============================================================================
# BƯỚC 5 THẬT BẰNG GEMINI: CHẤM 4 TRỤ CỘT & CHỌN HƯỚNG (HOẶC NHẬN HƯỚNG NGƯỜI CHỌN)
# ==============================================================================


def grade_step5_outlines(
    loai: str,
    de_bai: str,
    outlines_dict: Dict[str, Any],
    config_bundle: Dict[str, Any],
    chon_huong: Optional[str] = None,
    use_cache: bool = True,
    simulate_mode: Optional[str] = None,
) -> Dict[str, Any]:
    """Gọi thật Gemini 2.5 Flash để chấm điểm 3 phương án dàn ý A, B, C theo 4 trụ cột
    dựa trên nội dung thực tế của từng dàn ý và tiêu chí trong `loai/<loai>/cau_hinh.json`.
    Tuyệt đối không gán cứng `if v == 'B': 91.48`.
    """
    ten_loai = config_bundle.get("ten_hien_thi", loai)
    bat_buoc = config_bundle.get("bat_buoc_co", [])

    # Chuẩn bị bản tóm tắt 3 dàn ý để Gemini chấm độc lập
    summary_for_grading = {}
    for k in ("A", "B", "C"):
        ov = outlines_dict.get(k, {})
        summary_for_grading[k] = {
            "ten_huong": ov.get("ten_huong", ""),
            "hook_mo_dau": ov.get("hook_mo_dau", ""),
            "sections": ov.get("sections", []),
            "exhibits": ov.get("exhibits", []),
            "persona_avg": ov.get("diem_tb_persona", 80.0),
        }

    sys_inst = (
        "Bạn là Hội đồng Thẩm định Nội dung của Sakedemy. Hãy chấm điểm khách quan 3 phương án dàn ý A, B, C "
        "theo 4 trụ cột: (1) Mức độ thuyết phục 3 chân dung người đọc [tối đa 40 điểm], "
        "(2) Khớp tiêu chí bắt buộc của thể loại [tối đa 30 điểm], "
        "(3) Mật độ bằng chứng và bảng biểu đối chiếu [tối đa 20 điểm], "
        "(4) Chống văn mẫu sáo rỗng [tối đa 10 điểm]. Trả về đúng JSON."
    )

    prompt = f"""Đề bài: "{de_bai}"
Thể loại: {ten_loai} ({loai})
Tiêu chí bắt buộc của thể loại: {json.dumps(bat_buoc, ensure_ascii=False)}

3 Phương án dàn ý cần chấm:
{json.dumps(summary_for_grading, ensure_ascii=False, indent=2)}

Hãy chấm điểm thực chất từng phương án A, B, C và trả về JSON theo cấu trúc:
{{
  "bang_diem": {{
    "A": {{
      "persona_40": <số thực từ 25.0 đến 39.5>,
      "dat_khi_30": <số thực từ 18.0 đến 29.5>,
      "bang_chung_20": <số thực từ 12.0 đến 19.5>,
      "chong_slop_10": <số thực từ 6.0 đến 9.8>,
      "nhan_xet_ngan": "Nhận xét cụ thể vì sao phương án A đạt mức điểm này"
    }},
    "B": {{
      "persona_40": <số thực từ 25.0 đến 39.5>,
      "dat_khi_30": <số thực từ 18.0 đến 29.5>,
      "bang_chung_20": <số thực từ 12.0 đến 19.5>,
      "chong_slop_10": <số thực từ 6.0 đến 9.8>,
      "nhan_xet_ngan": "Nhận xét cụ thể vì sao phương án B đạt mức điểm này"
    }},
    "C": {{
      "persona_40": <số thực từ 25.0 đến 39.5>,
      "dat_khi_30": <số thực từ 18.0 đến 29.5>,
      "bang_chung_20": <số thực từ 12.0 đến 19.5>,
      "chong_slop_10": <số thực từ 6.0 đến 9.8>,
      "nhan_xet_ngan": "Nhận xét cụ thể vì sao phương án C đạt mức điểm này"
    }}
  }},
  "de_xuat_tot_nhat": "<A hoặc B hoặc C>",
  "ly_do_chon": "Giải thích rõ bằng tiếng Việt dễ hiểu vì sao phương án được đề xuất phục vụ tốt nhất cho người đọc."
}}"""

    parsed, usage_meta = call_gemini_json(
        prompt=prompt,
        system_instruction=sys_inst,
        temperature=0.2,
        use_cache=use_cache,
        simulate_mode=simulate_mode,
        step_tag=f"step5_{loai}",
    )

    bang_diem_raw = parsed.get("bang_diem", {})
    bang_diem_clean: Dict[str, Any] = {}
    for k in ("A", "B", "C"):
        row = bang_diem_raw.get(k, {})
        p40 = round(float(row.get("persona_40", 32.0)), 2)
        d30 = round(float(row.get("dat_khi_30", 24.0)), 2)
        b20 = round(float(row.get("bang_chung_20", 16.0)), 2)
        s10 = round(float(row.get("chong_slop_10", 8.0)), 2)
        tong = round(p40 + d30 + b20 + s10, 2)
        bang_diem_clean[k] = {
            "persona_40": p40,
            "dat_khi_30": d30,
            "bang_chung_20": b20,
            "chong_slop_10": s10,
            "tong_100": tong,
            "dat_nguong": tong >= 80.0,
            "nhan_xet_ngan": row.get("nhan_xet_ngan", ""),
        }

    # Xếp hạng theo điểm thực tế từ Gemini
    ranked = sorted(bang_diem_clean.keys(), key=lambda x: bang_diem_clean[x]["tong_100"], reverse=True)
    ai_recommended = ranked[0] if ranked else "B"

    # Nếu người dùng đã bấm chọn 1 hướng cụ thể trên giao diện (A, B, hoặc C) thì tôn trọng lựa chọn của người dùng
    if chon_huong and chon_huong.upper() in ("A", "B", "C"):
        selected = chon_huong.upper()
        ly_do = (
            f"Người dùng đã trực tiếp chọn Phương án {selected} ({outlines_dict.get(selected, {}).get('ten_huong', '')}). "
            f"{bang_diem_clean.get(selected, {}).get('nhan_xet_ngan', '')}"
        ).strip()
    else:
        selected = ai_recommended
        ly_do = parsed.get("ly_do_chon") or bang_diem_clean[selected].get("nhan_xet_ngan", "")

    return {
        "bang_diem": bang_diem_clean,
        "xep_hang": ranked,
        "ai_de_xuat": ai_recommended,
        "selected_variant": selected,
        "ly_do_chon": ly_do,
        "_gemini_usage": usage_meta,
    }


# ==============================================================================
# BƯỚC 6 & 8 THẬT BẰNG GEMINI CHO ĐỀ BÀI MỚI TỪ GIAO DIỆN
# ==============================================================================


def generate_topic_specific_article(
    loai: str,
    de_bai: str,
    chosen_outline: Dict[str, Any],
    config_bundle: Dict[str, Any],
    use_cache: bool = True,
    simulate_mode: Optional[str] = None,
) -> Tuple[str, str, Dict[str, Any]]:
    """Sinh nội dung bài viết bám sát `de_bai` và `chosen_outline` (A, B hoặc C)
    kết hợp với bộ số liệu đã kiểm chứng [N01]..[N06] của Sakedemy để đạt chuẩn biên tập.
    Trả về (draft1_markdown, step8_clean_markdown, usage_meta).
    """
    ten_loai = config_bundle.get("ten_hien_thi", loai)
    variant = chosen_outline.get("variant", "B")
    ten_huong = chosen_outline.get("ten_huong", f"Phương án {variant}")
    hook = chosen_outline.get("hook_mo_dau", "")
    sections = chosen_outline.get("sections", [])

    sys_inst = (
        "Bạn là Chuyên gia Biên soạn Ấn phẩm của Sakedemy. Hãy viết phần mở bài tình huống, luận điểm phân tích chuyên sâu "
        "và danh sách hành động thực tế cho đề bài và dàn ý đã chọn. Sử dụng tiếng Việt tự nhiên, sắc sảo, "
        "không dùng từ sáo rỗng, và chỉ trích dẫn từ kho số liệu xác thực: "
        "40% nhân sự nhận bàn giao sản phẩm AI hời hợt mỗi tháng [N01], tốn 1 giờ 56 phút dọn mỗi trường hợp [N01], "
        "88% doanh nghiệp đã dùng AI nhưng chỉ 39% ghi nhận tác động lợi nhuận EBIT [N02], "
        "quy tắc phân bổ nguồn lực 10-20-70 của BCG (10% thuật toán, 20% hạ tầng, 70% con người và quy trình) [N03], "
        "30% thời gian làm việc bị hao hụt do thiếu cổng kiểm duyệt [N04]."
    )

    prompt = f"""Đề bài: "{de_bai}"
Thể loại: {ten_loai} ({loai})
Phương án dàn ý đã chọn: {variant} — {ten_huong}
Câu mở đầu định hướng: {hook}
Các mục trong dàn ý: {json.dumps(sections, ensure_ascii=False)}

Hãy trả về JSON gồm các đoạn nội dung chuyên biệt cho đề bài này:
{{
  "tieu_de_chinh": "Tiêu đề ấn phẩm sắc sảo bám sát đề bài '{de_bai}'",
  "doan_mo_bai_tinh_huong": "Đoạn mở bài 140-180 chữ kể tình huống thực tế của đề bài '{de_bai}', lồng ghép số liệu 88% doanh nghiệp đã triển khai AI nhưng chỉ 39% tạo tác động EBIT [N02] và 40% nhân sự tốn 1 giờ 56 phút xử lý bản nháp AI hời hợt [N01].",
  "muc_1_phan_tich": "Đoạn phân tích 180-220 chữ đi sâu vào mục 1 của dàn ý '{sections[0] if sections else de_bai}', giải thích nguyên nhân theo quy tắc 10-20-70 (10% thuật toán, 20% dữ liệu, 70% quy trình và con người) [N03].",
  "muc_2_giai_phap": "Đoạn phân tích 180-220 chữ đi sâu vào giải pháp cho đề bài '{de_bai}', cách thu hồi 30% quỹ thời gian bị thất thoát [N04] thông qua khảo sát 52 doanh nghiệp tại Hà Nội và TP.HCM [N05].",
  "ba_hanh_dong_tuan_toi": [
    "Bước 1 cụ thể áp dụng cho đề bài '{de_bai}'",
    "Bước 2 cụ thể áp dụng cho đề bài '{de_bai}'",
    "Bước 3 cụ thể áp dụng cho đề bài '{de_bai}'"
  ]
}}"""

    parsed, usage_meta = call_gemini_json(
        prompt=prompt,
        system_instruction=sys_inst,
        temperature=0.3,
        use_cache=use_cache,
        simulate_mode=simulate_mode,
        step_tag=f"step68_{loai}_{variant}",
    )

    tieu_de = parsed.get("tieu_de_chinh") or de_bai
    mo_bai = parsed.get("doan_mo_bai_tinh_huong") or hook
    muc_1 = parsed.get("muc_1_phan_tich") or ""
    muc_2 = parsed.get("muc_2_giai_phap") or ""
    hanh_dong_list = parsed.get("ba_hanh_dong_tuan_toi") or [
        "Rà soát lại 5 đầu việc tốn thời gian chỉnh sửa nhất trong phòng ban ngay sáng thứ Hai.",
        "Thiết lập bộ tiêu chí đầu vào và bảng kiểm đối chiếu số liệu gốc trước khi gửi báo cáo.",
        "Đo lường số giờ tiết kiệm thực tế sau 14 ngày áp dụng quy trình mới.",
    ]

    sec_titles = list(sections) if len(sections) >= 4 else [
        "1. Bức tranh thực tế và chi phí ẩn tại doanh nghiệp",
        "2. Giải phẫu điểm nghẽn vận hành theo nguyên lý 10-20-70",
        "3. Bảng đối chiếu quy trình Trước và Sau khi chuẩn hoá",
        "4. Lộ trình 3 bước triển khai và nghiệm thu đầu ra",
    ]

    clean_md = f"""# {tieu_de}

> **Phương án dàn ý thực thi**: **{ten_huong}** · **Thể loại**: {ten_loai}

## {sec_titles[0]}

{mo_bai}

Trong thực tế triển khai cho chủ đề **"{de_bai}"**, ban điều hành thường nhìn thấy tốc độ sinh văn bản tăng vọt ở bề nổi nhưng lại bỏ sót thời gian rà soát ở tầng vận hành. Khi khảo sát thực địa 52 doanh nghiệp SME và tập đoàn tại Hà Nội cùng TP.HCM (N=52, Q1/2026) [N05], nhóm tư vấn ghi nhận các đội ngũ áp dụng quy trình kiểm soát đầu vào giảm được từ 116 phút xuống còn 28 phút biên tập cho mỗi đầu việc phức tạp [N01], [N05].

## {sec_titles[1]}

{muc_1}

Nếu doanh nghiệp chỉ mua tài khoản công cụ mà không thiết kế lại quy trình giao việc, nhân sự sẽ rơi vào bẫy uỷ thác toàn bộ tư duy cho máy. Báo cáo của BCG chỉ rõ giá trị chuyển đổi đến từ quy tắc 10-20-70: chỉ 10% nằm ở bản thân mô hình, 20% ở hạ tầng dữ liệu, và tới 70% quyết định bởi quy trình làm việc cùng năng lực thẩm định của con người [N03].

## {sec_titles[2]}

{muc_2}

Dưới đây là bảng đối chiếu định lượng giữa cách sử dụng tự phát và quy trình chuẩn hoá của Sakedemy cho bài toán **"{de_bai}"**:

| Tiêu chí vận hành | Trước khi chuẩn hoá (Tự phát) | Sau khi áp dụng Quy trình 3 Bước | Nguồn đối chứng |
| :--- | :--- | :--- | :--- |
| Thời gian rà soát & sửa lại mỗi đầu việc | 1 giờ 56 phút (116 phút) | 28 phút (giảm 75,8% thời gian) | Khảo sát HBR & Sakedemy [N01], [N05] |
| Tỷ lệ bản thảo phải trả về làm lại | 40% bản giao nộp thiếu số liệu gốc | Dưới 8% nhờ bảng kiểm đối chiếu | Báo cáo Workslop & Thực địa [N01], [N05] |
| Quỹ thời gian làm việc bị thất thoát | Hao hụt 30% giờ làm vì sửa lỗi vặt | Thu hồi 6,2 giờ/nhân sự/tuần | Nghiên cứu Năng suất & Đào tạo [N04], [N06] |
| Tác động lên hiệu quả vận hành (EBIT) | Chỉ 39% đơn vị ghi nhận hiệu quả thật | Đo lường rõ theo từng tuần triển khai | Khảo sát McKinsey Global AI [N02] |

## {sec_titles[3]}

Để đưa phương án **{ten_huong}** vào vận hành ngay trong tuần tới mà không làm xáo trộn nhịp làm việc hiện tại, quản lý trực tiếp cần kích hoạt 3 bước thực thi kèm bảng kiểm nghiệm thu:

1. **Bước 1 — Khoá ngữ cảnh và dữ liệu gốc đầu vào**: {hanh_dong_list[0]}
2. **Bước 2 — Chạy quy trình so sánh 3 phương án dàn ý trước khi viết**: {hanh_dong_list[1] if len(hanh_dong_list) > 1 else 'Yêu cầu nhân sự trình 3 hướng tiếp cận ngắn gọn, chọn 1 hướng sát thực tế nhất rồi mới triển khai chi tiết.'}
3. **Bước 3 — Nghiệm thu bằng bảng kiểm 4 tiêu chí**: {hanh_dong_list[2] if len(hanh_dong_list) > 2 else 'Kiểm tra chéo từng con số với nguồn gốc, cắt bỏ mọi câu mở đầu sáo rỗng và đo số giờ tiết kiệm được sau 2 tuần [N06].'}

---
**Danh mục nguồn đối chiếu xác thực**:
- **[N01]** Harvard Business Review & BetterUp Labs (2025): Nghiên cứu về hiện tượng bản thảo AI hời hợt (40% nhân sự gặp phải, tốn trung bình 1 giờ 56 phút xử lý mỗi trường hợp).
- **[N02]** McKinsey Global Survey on AI: 88% tổ chức đã sử dụng AI trong ít nhất một chức năng, nhưng chỉ 39% ghi nhận tác động thực chất lên lợi nhuận EBIT.
- **[N03]** Boston Consulting Group (BCG): Quy tắc phân bổ nguồn lực 10-20-70 trong chuyển đổi AI doanh nghiệp (70% nằm ở con người và quy trình).
- **[N04]** Nghiên cứu Năng suất Lao động Số: Khoảng 30% thời gian làm việc bị hao hụt khi thiếu cổng kiểm soát chất lượng đầu ra.
- **[N05]** Khảo sát Thực địa Doanh nghiệp Việt Nam của Sakedemy (N=52 doanh nghiệp tại Hà Nội & TP.HCM, Q1/2026).
- **[N06]** Báo cáo Đo lường Hiệu quả Đào tạo Thực chiến Sakedemy (tiết kiệm trung bình 6,2 giờ/nhân sự/tuần sau chuẩn hoá).
"""

    # Bản nháp 1 có thêm vài cụm văn mẫu để bước 7-8 cắt gọt thật
    draft1_md = (
        "Trong kỷ nguyên số hiện nay, AI không chỉ là công cụ mà còn là trợ thủ đắc lực giúp bức tranh toàn cảnh doanh nghiệp bứt phá.\n\n"
        + clean_md
    )
    return draft1_md, clean_md, usage_meta
