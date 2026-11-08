"""Bộ gọi Gemini API thật có trần token (`core/gemini_client.py`).

Quy tắc sắt (Bậc 1 MVP nội bộ - Cổng A):
1. Chỉ đọc khoá `GEMINI_API_KEY` (hoặc `AI_API_KEY`) từ `D:\\LINHX\\PROTO\\03_OPC_OS\\.env` qua `core.env_loader`.
   Tuyệt đối không đọc `.env` ngoài thư mục `03_OPC_OS`, không in hay ghi khoá ra log/báo cáo.
2. Không dùng công thức nhân token giả, không dùng `time.sleep()`.
3. Áp đặt trần token cứng cho mỗi lượt gọi (`max_output_tokens`) và trần tổng token toàn phiên (`MAX_SESSION_TOKENS`).
4. Khi chưa có khoá trong `.env` hoặc khi Gemini trả lỗi / chậm / hết hạn mức (Cổng A - Mục 3 Phá thử),
   hệ thống không làm mất dữ liệu đơn hàng mà chuyển về chế độ tổng hợp tất định an toàn với `input_tokens = 0`, `output_tokens = 0`, `ai_cost_vnd = 0` và ghi rõ trạng thái thật.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any

from core.env_loader import load_runtime_env

# Giá tham chiếu Gemini 2.5 Flash quy đổi VNĐ (chỉ tính trên số token thật trả về từ usageMetadata)
TOKEN_PRICE_INPUT_VND_PER_1K = 3.9     # ~0.15 USD / 1M input tokens
TOKEN_PRICE_OUTPUT_VND_PER_1K = 15.6   # ~0.60 USD / 1M output tokens

DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_MAX_OUTPUT_TOKENS = 450
MAX_PROMPT_CHARS = 8000
MAX_SESSION_TOKENS = 250_000

_SESSION_STATE = {
    "total_tokens_used": 0,
    "total_calls": 0,
    "total_errors": 0,
    "fault_injection_mode": None,  # None | "timeout" | "quota_429" | "server_503" | "token_cap_exceeded"
}


def set_fault_injection(mode: str | None) -> None:
    """Dùng cho Cổng A - Mục 3 (Phá thử: giả lập AI lỗi, chậm hoặc hết hạn mức)."""
    _SESSION_STATE["fault_injection_mode"] = mode


def reset_session_token_counter(max_session_tokens: int | None = None) -> None:
    _SESSION_STATE["total_tokens_used"] = 0
    _SESSION_STATE["total_calls"] = 0
    _SESSION_STATE["total_errors"] = 0
    if max_session_tokens is not None:
        _SESSION_STATE["custom_cap"] = max_session_tokens
    else:
        _SESSION_STATE.pop("custom_cap", None)


def get_session_token_stats() -> dict[str, Any]:
    return {
        "total_tokens_used": _SESSION_STATE["total_tokens_used"],
        "total_calls": _SESSION_STATE["total_calls"],
        "total_errors": _SESSION_STATE["total_errors"],
        "session_token_ceiling": _SESSION_STATE.get("custom_cap", MAX_SESSION_TOKENS),
    }


def call_gemini_with_cap(
    prompt: str,
    *,
    system_instruction: str = "",
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    temperature: float = 0.2,
    timeout_sec: float = 12.0,
    fallback_text: str = "",
) -> dict[str, Any]:
    """Gọi Gemini API thật với trần token.
    Trả về dict chứa:
      - text: nội dung văn bản
      - status: "REAL_GEMINI_OK" | "NO_ENV_KEY_FALLBACK" | "FAULT_INJECTED_FALLBACK" | "TOKEN_CAP_FALLBACK" | "API_ERROR_FALLBACK"
      - llm_calls: số lượt gọi HTTP thật đã thực hiện (0 nếu chưa có .env)
      - input_tokens: promptTokenCount thật từ Gemini (0 nếu fallback)
      - output_tokens: candidatesTokenCount thật từ Gemini (0 nếu fallback)
      - total_tokens: tổng token thật
      - ai_cost_vnd: chi phí VNĐ tính trên token thật
      - latency_seconds: thời gian thực thi thật
      - user_message_vi: thông báo tiếng Việt dễ hiểu khi có sự cố
    """
    t0 = time.perf_counter()
    env = load_runtime_env()
    safe_prompt = (prompt or "")[:MAX_PROMPT_CHARS]
    cap = int(_SESSION_STATE.get("custom_cap", MAX_SESSION_TOKENS))
    hard_out_cap = max(32, min(int(max_output_tokens), 1024))

    # 1. Kiểm tra chế độ phá thử (Cổng A - Mục 3)
    fault = _SESSION_STATE.get("fault_injection_mode")
    if fault:
        _SESSION_STATE["total_errors"] += 1
        reason_map = {
            "timeout": "Dịch vụ AI phản hồi quá thời gian chờ cho phép; hệ thống đã tự động dùng bản tổng hợp an toàn để không gián đoạn báo cáo của bạn.",
            "quota_429": "Đã chạm hạn mức gọi AI trong phút; hệ thống đã tự động chuyển sang bộ biên tập tiêu chuẩn để bảo toàn dữ liệu đơn hàng.",
            "server_503": "Máy chủ AI đang bảo trì tạm thời; hệ thống đã tự động hoàn tất báo cáo bằng dữ liệu tính toán gốc.",
            "token_cap_exceeded": "Đã chạm trần ngân sách token an toàn của phiên; hệ thống tự động dùng lời dẫn tiêu chuẩn.",
        }
        return {
            "text": fallback_text,
            "status": "FAULT_INJECTED_FALLBACK",
            "fault_type": fault,
            "llm_calls": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "ai_cost_vnd": 0,
            "latency_seconds": round(time.perf_counter() - t0, 4),
            "user_message_vi": reason_map.get(fault, "Hệ thống đã tự động chuyển sang chế độ dự phòng an toàn."),
        }

    # 2. Kiểm tra trần tổng token toàn phiên
    if _SESSION_STATE["total_tokens_used"] + hard_out_cap > cap:
        _SESSION_STATE["total_errors"] += 1
        return {
            "text": fallback_text,
            "status": "TOKEN_CAP_FALLBACK",
            "llm_calls": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "ai_cost_vnd": 0,
            "latency_seconds": round(time.perf_counter() - t0, 4),
            "user_message_vi": "Đã chạm trần ngân sách token an toàn trong phiên; hệ thống tự động dùng bản tổng hợp chuẩn.",
        }

    # 3. Kiểm tra khoá Gemini trong D:\LINHX\PROTO\03_OPC_OS\.env
    if not env.has_ai_key or not env._ai_api_key:
        return {
            "text": fallback_text,
            "status": "NO_ENV_KEY_FALLBACK",
            "llm_calls": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "ai_cost_vnd": 0,
            "latency_seconds": round(time.perf_counter() - t0, 4),
            "user_message_vi": "Chưa có khoá GEMINI_API_KEY trong 03_OPC_OS/.env; hệ thống vận hành ở chế độ tổng hợp tất định (0 token AI).",
        }

    # 4. Gọi thật Gemini REST API
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{DEFAULT_MODEL}:generateContent?key={env._ai_api_key}"
    body: dict[str, Any] = {
        "contents": [{"role": "user", "parts": [{"text": safe_prompt}]}],
        "generationConfig": {
            "maxOutputTokens": hard_out_cap,
            "temperature": temperature,
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }
    if system_instruction:
        body["systemInstruction"] = {"parts": [{"text": system_instruction[:2000]}]}

    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        _SESSION_STATE["total_calls"] += 1
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            raw_json = json.loads(resp.read().decode("utf-8"))

        candidates = raw_json.get("candidates") or []
        parts = (candidates[0].get("content", {}).get("parts") or []) if candidates else []
        gen_text = "".join(p.get("text", "") for p in parts).strip() or fallback_text

        usage = raw_json.get("usageMetadata") or {}
        in_tok = int(usage.get("promptTokenCount", 0))
        out_tok = int(usage.get("candidatesTokenCount", 0))
        tot_tok = int(usage.get("totalTokenCount", in_tok + out_tok))
        _SESSION_STATE["total_tokens_used"] += tot_tok

        cost_vnd = round(
            (in_tok / 1000.0) * TOKEN_PRICE_INPUT_VND_PER_1K
            + (out_tok / 1000.0) * TOKEN_PRICE_OUTPUT_VND_PER_1K,
            2,
        )
        return {
            "text": gen_text,
            "status": "REAL_GEMINI_OK",
            "llm_calls": 1,
            "input_tokens": in_tok,
            "output_tokens": out_tok,
            "total_tokens": tot_tok,
            "ai_cost_vnd": cost_vnd,
            "latency_seconds": round(time.perf_counter() - t0, 4),
            "user_message_vi": "Đã tổng hợp bằng Gemini API thật.",
        }
    except Exception as exc:
        _SESSION_STATE["total_errors"] += 1
        err_type = type(exc).__name__
        return {
            "text": fallback_text,
            "status": "API_ERROR_FALLBACK",
            "error_type": err_type,
            "llm_calls": 1,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "ai_cost_vnd": 0,
            "latency_seconds": round(time.perf_counter() - t0, 4),
            "user_message_vi": "Kết nối AI tạm thời gián đoạn; hệ thống đã tự động dùng bản tổng hợp chuẩn để hoàn tất báo cáo cho bạn.",
        }
