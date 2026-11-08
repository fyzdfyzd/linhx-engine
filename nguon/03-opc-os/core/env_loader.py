"""Đọc cấu hình bảo mật từ `D:\\LINHX\\PROTO\\03_OPC_OS\\.env` do anh Linh tự tạo.

Quy tắc sắt (03_OPC_OS.md, 11_LO_TRINH_VAN_HANH_THAT.md & user_global):
- Chỉ đọc duy nhất file `.env` nằm trong thư mục `D:\\LINHX\\PROTO\\03_OPC_OS\\.env`, tuyệt đối không đọc `.env` ngoài thư mục bộ này.
- Khoá API SePay, khoá Gemini và số tài khoản Vân Anh tuyệt đối không ghi vào đề, không ghi vào code, không ghi vào log.
- Nếu chạy chế độ tiền thật (`OPC_OS_MODE=live`) mà thiếu file `.env` hoặc thiếu biến bắt buộc -> dừng ngay lập tức, báo "CẦN LINH".
- Khi chạy chế độ thử nội bộ (`OPC_OS_MODE=poc_mock`), hệ thống dùng khoá thử nghiệm trong RAM để kiểm thử luồng thanh toán QR giả.
"""
from __future__ import annotations

import os
import secrets
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"

_EPHEMERAL_POC_KEY = "test-ram-" + secrets.token_hex(8)


@dataclass(frozen=True)
class RuntimeEnv:
    mode: str  # "poc_mock" | "live"
    env_file_exists: bool
    has_sepay_key: bool
    has_account_number: bool
    has_ai_key: bool
    bank_code: str
    account_number_masked: str
    account_name: str
    # Giá trị nhạy cảm chỉ giữ trong bộ nhớ tiến trình, không bao giờ xuất ra to_public_dict()
    _sepay_api_key: str
    _sepay_api_token: str
    _account_number_raw: str
    _ai_api_key: str

    def verify_webhook_header(self, auth_header: str) -> bool:
        expected = f"Apikey {self._sepay_api_key}"
        return bool(self._sepay_api_key) and secrets.compare_digest(auth_header or "", expected)

    def get_poc_webhook_header_for_test(self) -> str:
        """Chỉ dùng cho bộ chạy thử nội bộ khi `mode == 'poc_mock'`."""
        if self.mode != "poc_mock":
            raise PermissionError("Không được lấy header thử nghiệm khi đang ở chế độ tiền thật.")
        return f"Apikey {self._sepay_api_key}"

    def to_public_dict(self) -> dict:
        """Trả về thông tin trạng thái đã che toàn bộ bí mật để ghi báo cáo / hiển thị dashboard."""
        return {
            "mode": self.mode,
            "mode_label_vi": "Chế độ thử nghiệm (Không thu tiền thật)" if self.mode == "poc_mock" else "Chế độ vận hành thật",
            "env_file_exists": self.env_file_exists,
            "has_sepay_key": self.has_sepay_key,
            "has_account_number": self.has_account_number,
            "has_ai_key": self.has_ai_key,
            "bank_code": self.bank_code,
            "account_number_masked": self.account_number_masked,
            "account_name": self.account_name,
            "can_linh": [] if (self.env_file_exists and self.has_sepay_key and self.has_account_number and self.has_ai_key) else [
                "Anh Linh tạo file .env trong thư mục 03_OPC_OS (gồm GEMINI_API_KEY, SEPAY_API_KEY, SEPAY_ACCOUNT_NUMBER, SEPAY_ACCOUNT_NAME) khi bật gọi Gemini trực tuyến và nhận tiền thật."
            ],
        }


def _parse_dotenv(path: Path) -> dict[str, str]:
    """Chỉ đọc duy nhất file `.env` trong `D:\\LINHX\\PROTO\\03_OPC_OS\\.env`."""
    out: dict[str, str] = {}
    resolved = path.resolve()
    if resolved.parent != ROOT.resolve():
        raise PermissionError("Vi phạm phạm vi: Không được đọc file .env ngoài thư mục 03_OPC_OS.")
    if not resolved.exists():
        return out
    for raw_line in resolved.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def _mask(val: str) -> str:
    if not val:
        return "Tài khoản thử nghiệm nội bộ"
    if len(val) <= 4:
        return "****"
    return "*" * (len(val) - 4) + val[-4:]


def load_runtime_env(require_live: bool = False) -> RuntimeEnv:
    file_vars = _parse_dotenv(ENV_PATH)

    def get_var(name: str, default: str = "") -> str:
        return file_vars.get(name) or os.environ.get(name) or default

    mode = get_var("OPC_OS_MODE", "poc_mock").lower()
    if require_live:
        mode = "live"

    raw_sepay_key = get_var("SEPAY_API_KEY", "")
    raw_sepay_token = get_var("SEPAY_API_TOKEN", "")
    raw_acc_num = get_var("SEPAY_ACCOUNT_NUMBER", "")
    raw_acc_name = get_var("SEPAY_ACCOUNT_NAME", "HỘ KINH DOANH VÂN ANH")
    raw_bank = get_var("SEPAY_BANK_CODE", "MBBank")
    raw_ai_key = get_var("GEMINI_API_KEY", "") or get_var("AI_API_KEY", "")

    has_sepay = bool(raw_sepay_key)
    has_acc = bool(raw_acc_num)
    has_ai = bool(raw_ai_key)

    if mode == "live":
        missing = []
        if not ENV_PATH.exists():
            missing.append("File D:\\LINHX\\PROTO\\03_OPC_OS\\.env chưa tồn tại")
        if not has_sepay:
            missing.append("Thiếu biến SEPAY_API_KEY")
        if not has_acc:
            missing.append("Thiếu biến SEPAY_ACCOUNT_NUMBER")
        if missing:
            raise RuntimeError(
                "CẦN LINH: Không thể chạy chế độ tiền thật (live) vì: " + "; ".join(missing)
            )
        effective_sepay_key = raw_sepay_key
    else:
        effective_sepay_key = raw_sepay_key if has_sepay else _EPHEMERAL_POC_KEY

    return RuntimeEnv(
        mode=mode,
        env_file_exists=ENV_PATH.exists(),
        has_sepay_key=has_sepay,
        has_account_number=has_acc,
        has_ai_key=has_ai,
        bank_code=raw_bank,
        account_number_masked=_mask(raw_acc_num),
        account_name=raw_acc_name,
        _sepay_api_key=effective_sepay_key,
        _sepay_api_token=raw_sepay_token,
        _account_number_raw=raw_acc_num,
        _ai_api_key=raw_ai_key,
    )
