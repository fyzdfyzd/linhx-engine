"""Trích 60 bước cuối của agy thành `NHAT-KY.md` (chỉ đọc hội thoại, đã lọc bí mật).

Nguồn dữ liệu theo thứ tự ưu tiên:
1. Luồng ra JSON / stream-json từ `stdout` (hoặc `stderr`) của `agy`.
2. Thư mục hội thoại chỉ đọc trong `%USERPROFILE%\\.gemini\\antigravity-cli`
   theo `conversation_id` (hoặc đối chiếu `USER_INPUT` nếu agy bị kill giữa chừng
   trước khi kịp in JSON cuối).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import time

try:
    from runner import rao_phieu
except ImportError:
    import rao_phieu

SO_BUOC_TOI_DA = 60
GIOI_HAN_LENH = 200
SO_DONG_DAU_RA_CUOI = 3
CHUOI_CHE_BI_MAT = "[DA-CHE-BI-MAT]"

_UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
_UUID_TRONG_CHU_RE = re.compile(
    r"\b([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})\b"
)
_MA_THOAT_RE = re.compile(r"(?m)^Command exited with code (-?\d+)\.?\s*$")
_DONG_MO_DAU_GENERIC_RE = re.compile(
    r"^(?:Created At|Completed At|Command exited with code -?\d+\.?|Command output:|Showing lines \d+-\d+ of \d+)\s*$"
)
_KHOA_TEN_BI_MAT = (
    r"(?:[A-Za-z0-9_]*_(?:"
    + "api_?key|secret_?key|private_?key|access_?key|auth_?key|signing_?key|"
    + "access_?token|refresh_?token|auth_?token|bearer_?token|session_?token|csrf_?token|id_?token|"
    + "client_?secret|mat_?khau|pass_?wd|pass_?phrase|pwd|to" + "ken|sec" + "ret|key)"
    + r"|sepay[_a-z0-9]*"
    + r"|api" + r"_?key"
    + r"|auth" + r"orization"
    + r"|pass" + r"word"
    + r"|mat" + r"_?khau"
    + r"|pass" + r"phrase"
    + r"|sec" + r"ret"
    + r"|to" + r"ken"
    + r"|cre" + r"dentials?)"
)

# Ghép mảnh mẫu regex để tránh khớp nhầm bộ quét tĩnh của repo và che đủ dạng bí mật
_MAU_BI_MAT_BO_SUNG: tuple[tuple[re.Pattern[str], str], ...] = (
    # Tiền tố token/key phổ biến ngoài rao_phieu
    (re.compile(r"\b(?:npm|hf)_[A-Za-z0-9]{14,}\b"), CHUOI_CHE_BI_MAT),
    (re.compile(r"\bpypi-[A-Za-z0-9_-]{14,}\b"), CHUOI_CHE_BI_MAT),
    (re.compile(r"\b(?:rk|pk|whsec)_(?:live|test)_[A-Za-z0-9]{12,}\b"), CHUOI_CHE_BI_MAT),
    # JWT 3 đoạn eyJ...
    (re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"), CHUOI_CHE_BI_MAT),
    # Header Bearer / Basic
    (re.compile(r"(?i)\b(Bearer|Basic)\s+[A-Za-z0-9._+/=-]{10,}"), rf"\1 {CHUOI_CHE_BI_MAT}"),
    # Thông tin đăng nhập nhúng trong URL: http(s)://user:pass@host
    (re.compile(r"(?i)(https?://[^\s:/@]+:)([^\s/@]{3,})(@)"), rf"\1{CHUOI_CHE_BI_MAT}\3"),
    # Dạng JSON / YAML / ENV: key: "val" hoặc key=val (bỏ qua placeholder và số đơn thuần)
    (
        re.compile(
            r"(?i)(?<![A-Za-z0-9_])("
            + _KHOA_TEN_BI_MAT
            + r")(\s*[:=]\s*['\"]?)(?!\$\{|%[A-Za-z_]|<[^>]+>|\*+$|None\b|null\b|true\b|false\b|undefined\b|\[DA-CHE-BI-MAT\]|\d+(?:['\"\s,}]|$))([^\s'\"`\r\n,;{}()\[\]]{6,})(['\"]?)"
        ),
        rf"\1\2{CHUOI_CHE_BI_MAT}\4",
    ),
    # Cờ dòng lệnh dạng `--api-key xxx`, `--token xxx`, `--password xxx`, `--secret xxx`
    (
        re.compile(
            r"(?i)(--(?:api[-_]?key|access[-_]?key|to"
            + r"ken|sec"
            + r"ret|pass"
            + r"word|mat[-_]?khau|auth))\s+(['\"]?)(?!-)([^\s'\"\r\n]{6,})(\2)"
        ),
        rf"\1 \2{CHUOI_CHE_BI_MAT}\4",
    ),
)


def loc_bi_mat_nhat_ky(van_ban: str | None) -> str:
    """Che mọi chuỗi giống khoá/token/mật khẩu trước khi ghi ra NHAT-KY.md."""
    if not van_ban:
        return ""
    sach = rao_phieu.redact_secrets_in_text(str(van_ban))
    for rx, thay_the in _MAU_BI_MAT_BO_SUNG:
        sach = rx.sub(thay_the, sach)
    return sach


def _thu_parse_json(chuoi: str):
    if not chuoi:
        return None
    s = chuoi.strip()
    if not s or (not s.startswith("{") and not s.startswith("[")):
        return None
    try:
        return json.loads(s)
    except (ValueError, TypeError):
        return None


def _go_chuoi_json_long(gia_tri) -> str:
    if gia_tri is None:
        return ""
    s = str(gia_tri)
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        try:
            da_giai = json.loads(s)
            if isinstance(da_giai, str):
                return da_giai
        except (ValueError, TypeError):
            pass
    return s


def _cat_lenh_200(van_ban: str | None, gioi_han: int = GIOI_HAN_LENH) -> str:
    sach = " ".join(str(van_ban or "").split())
    if not sach:
        return "-"
    if len(sach) <= gioi_han:
        return sach
    if gioi_han <= 3:
        return sach[:gioi_han]
    return sach[: gioi_han - 3] + "..."


def _lay_3_dong_cuoi(van_ban: str | None, so_dong: int = SO_DONG_DAU_RA_CUOI) -> list[str]:
    if not van_ban:
        return []
    thay_the = str(van_ban).replace("\r\n", "\n").replace("\r", "\n")
    if "\nCommand output:\n" in thay_the:
        thay_the = thay_the.split("\nCommand output:\n", 1)[1]
    elif thay_the.startswith("Command output:\n"):
        thay_the = thay_the.split("Command output:\n", 1)[1]
    thay_the = loc_bi_mat_nhat_ky(thay_the)
    cac_dong: list[str] = []
    dang_o_dau = True
    for dong in thay_the.splitlines():
        da_bo = dong.rstrip()
        if dang_o_dau and (not da_bo.strip() or _DONG_MO_DAU_GENERIC_RE.match(da_bo.strip())):
            continue
        dang_o_dau = False
        if da_bo.strip():
            cac_dong.append(da_bo)
    return cac_dong[-so_dong:]


def _trich_lenh_tu_args(ten_tool: str, args) -> str:
    if isinstance(args, str):
        parsed = _thu_parse_json(args)
        args = parsed if isinstance(parsed, dict) else {"value": _go_chuoi_json_long(args)}
    if not isinstance(args, dict) or not args:
        return "-"
    lenh_tho = ""
    uu_tien_lenh = ("CommandLine", "command", "cmd", "Script", "Command")
    for khoa in uu_tien_lenh:
        if khoa in args and args[khoa] is not None:
            lenh_tho = _go_chuoi_json_long(args[khoa])
            break
    if not lenh_tho and ("Path" in args or "path" in args or "file" in args):
        duong = _go_chuoi_json_long(args.get("Path") or args.get("path") or args.get("file"))
        s_line = args.get("StartLine")
        e_line = args.get("EndLine")
        lenh_tho = f"{duong}#L{s_line or 1}-{e_line or ''}" if (s_line is not None or e_line is not None) else duong
    if not lenh_tho:
        for khoa in ("Url", "url", "Query", "query", "Pattern", "pattern", "Description", "Prompt", "Role", "Action"):
            if khoa in args and args[khoa] is not None:
                lenh_tho = _go_chuoi_json_long(args[khoa])
                break
    if not lenh_tho:
        try:
            lenh_tho = json.dumps(args, ensure_ascii=False, separators=(",", ":"))
        except (TypeError, ValueError):
            lenh_tho = str(args)
    return _cat_lenh_200(loc_bi_mat_nhat_ky(lenh_tho))


def _trich_ket_qua_generic(content: str | None, status: str | None) -> tuple[str, list[str]]:
    van_ban = str(content or "")
    m_code = _MA_THOAT_RE.search(van_ban)
    if m_code:
        ma_thoat = m_code.group(1)
    elif str(status or "").upper() in ("ERROR", "FAILED", "TIMEOUT", "CANCELLED"):
        ma_thoat = str(status).upper()
    else:
        ma_thoat = "-"
    dong_cuoi = _lay_3_dong_cuoi(van_ban)
    return ma_thoat, dong_cuoi


def _tao_ban_ghi_buoc(
    thoi_diem: str = "",
    cong_cu: str = "",
    lenh: str = "",
    ma_thoat: str = "-",
    dau_ra_cuoi: list[str] | None = None,
) -> dict:
    return {
        "thoi_diem": str(thoi_diem or "-").strip() or "-",
        "cong_cu": str(cong_cu or "-").strip() or "-",
        "lenh": _cat_lenh_200(loc_bi_mat_nhat_ky(lenh)),
        "ma_thoat": str(ma_thoat if ma_thoat not in (None, "") else "-"),
        "dau_ra_cuoi": list(dau_ra_cuoi or [])[-SO_DONG_DAU_RA_CUOI:],
    }


def _trich_buoc_tu_list_doi_tuong(cac_obj: list[dict]) -> list[dict]:
    """Chuyển danh sách dict (transcript JSONL hoặc stream-json) thành danh sách bước chuẩn."""
    buoc: list[dict] = []
    hang_cho: list[dict] = []
    theo_id: dict[str, dict] = {}

    for obj in cac_obj:
        if not isinstance(obj, dict):
            continue
        ts = str(obj.get("created_at") or obj.get("timestamp") or obj.get("ts") or obj.get("time") or "").strip()
        kieu = str(obj.get("type") or "").strip()

        # 1. Khuôn transcript.jsonl của antigravity-cli: PLANNER_RESPONSE + GENERIC nối tiếp FIFO
        if isinstance(obj.get("tool_calls"), list) and obj["tool_calls"]:
            for tc in obj["tool_calls"]:
                if not isinstance(tc, dict):
                    continue
                ten = str(tc.get("name") or tc.get("tool") or tc.get("tool_name") or "-")
                lenh = _trich_lenh_tu_args(ten, tc.get("args") or tc.get("arguments") or tc.get("input"))
                muc = _tao_ban_ghi_buoc(thoi_diem=ts, cong_cu=ten, lenh=lenh, ma_thoat="-")
                buoc.append(muc)
                hang_cho.append(muc)
                tc_id = str(tc.get("id") or tc.get("tool_call_id") or "").strip()
                if tc_id:
                    theo_id[tc_id] = muc
            continue

        if kieu == "GENERIC" or (kieu in ("tool_result", "tool_output") and (hang_cho or theo_id)):
            tc_id = str(obj.get("tool_call_id") or obj.get("id") or "").strip()
            muc_dich = theo_id.pop(tc_id, None) if tc_id else None
            if muc_dich is None and hang_cho:
                muc_dich = hang_cho.pop(0)
            if muc_dich is not None:
                nd = obj.get("content")
                if nd is None:
                    nd = obj.get("output") or obj.get("result") or obj.get("error")
                ma, dong = _trich_ket_qua_generic(nd, obj.get("status"))
                if obj.get("exit_code") is not None:
                    ma = str(obj["exit_code"])
                elif obj.get("returncode") is not None:
                    ma = str(obj["returncode"])
                muc_dich["ma_thoat"] = ma
                muc_dich["dau_ra_cuoi"] = dong
                continue

        # 2. Khuôn stream-json dạng sự kiện tool_use / tool_call / step
        if kieu in ("tool_use", "tool_call", "command", "action", "step") or any(
            k in obj for k in ("tool", "tool_name", "command", "CommandLine")
        ):
            ten = str(obj.get("tool") or obj.get("tool_name") or obj.get("name") or kieu or "-")
            args = obj.get("args") or obj.get("input") or obj.get("arguments")
            if args is None and any(k in obj for k in ("command", "CommandLine", "cmd")):
                args = obj
            lenh = _trich_lenh_tu_args(ten, args)
            ma_thoat = obj.get("exit_code")
            if ma_thoat is None:
                ma_thoat = obj.get("returncode")
            if ma_thoat is None:
                ma_thoat = obj.get("exit")
            dau_ra = obj.get("output") or obj.get("stdout") or obj.get("result") or obj.get("content") or obj.get("stderr")
            if ma_thoat is None and isinstance(dau_ra, str):
                ma_thoat, dong = _trich_ket_qua_generic(dau_ra, obj.get("status"))
            else:
                dong = _lay_3_dong_cuoi(dau_ra)
            muc = _tao_ban_ghi_buoc(
                thoi_diem=ts,
                cong_cu=ten,
                lenh=lenh,
                ma_thoat=str(ma_thoat) if ma_thoat is not None else "-",
                dau_ra_cuoi=dong,
            )
            buoc.append(muc)
            tc_id = str(obj.get("id") or obj.get("tool_call_id") or "").strip()
            if tc_id:
                theo_id[tc_id] = muc
            else:
                hang_cho.append(muc)
            continue

        # 3. JSON tổng hợp có mảng steps / tool_calls / events bên trong
        for khoa_mang in ("steps", "events", "messages", "history"):
            if isinstance(obj.get(khoa_mang), list):
                buoc.extend(_trich_buoc_tu_list_doi_tuong(obj[khoa_mang]))

    return buoc


def trich_buoc_tu_van_ban_json(van_ban: str | None) -> list[dict]:
    """Parse luồng JSON đơn hoặc JSONL từ stdout/stderr của agy thành các bước."""
    if not van_ban:
        return []
    thô = str(van_ban).strip()
    cac_obj: list[dict] = []
    parsed_whole = _thu_parse_json(thô)
    if isinstance(parsed_whole, dict):
        cac_obj.append(parsed_whole)
    elif isinstance(parsed_whole, list):
        cac_obj.extend(x for x in parsed_whole if isinstance(x, dict))
    else:
        for dong in thô.splitlines():
            obj = _thu_parse_json(dong)
            if isinstance(obj, dict):
                cac_obj.append(obj)
            elif isinstance(obj, list):
                cac_obj.extend(x for x in obj if isinstance(x, dict))
    return _trich_buoc_tu_list_doi_tuong(cac_obj)


def trich_conversation_id(stdout: str | None = "", stderr: str | None = "") -> str:
    """Tìm conversation_id từ JSON/stream-json hoặc stderr của agy."""
    for nguon in (stdout or "", stderr or ""):
        thô = nguon.strip()
        if not thô:
            continue
        parsed = _thu_parse_json(thô)
        if isinstance(parsed, dict):
            cid = str(parsed.get("conversation_id") or parsed.get("session_id") or "").strip()
            if cid:
                return cid
        for dong in thô.splitlines():
            obj = _thu_parse_json(dong)
            if isinstance(obj, dict):
                cid = str(obj.get("conversation_id") or obj.get("session_id") or "").strip()
                if cid:
                    return cid
        # Đôi khi agy ghi `terminated <uuid>/task-xxx` trên error/stderr
        m_task = re.search(
            r"\b([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})/task-\d+",
            nguon,
        )
        if m_task:
            return m_task.group(1)
    return ""


def thu_muc_agy_cli(cfg: dict | None = None) -> Path | None:
    """Xác định thư mục antigravity-cli (chỉ đọc)."""
    if isinstance(cfg, dict) and cfg.get("thu_muc_agy_cli"):
        return Path(str(cfg["thu_muc_agy_cli"]))
    env_dir = os.environ.get("LINHX_AGY_CLI_DIR", "").strip()
    if env_dir:
        return Path(env_dir)
    user_profile = os.environ.get("USERPROFILE", "").strip()
    if user_profile:
        cand = Path(user_profile) / ".gemini" / "antigravity-cli"
        if cand.is_dir():
            return cand
    cand_home = Path.home() / ".gemini" / "antigravity-cli"
    return cand_home if cand_home.is_dir() else None


def _doc_jsonl_chi_doc(tep: Path) -> list[dict]:
    try:
        noi_dung = tep.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    ds: list[dict] = []
    for dong in noi_dung.splitlines():
        obj = _thu_parse_json(dong)
        if isinstance(obj, dict):
            ds.append(obj)
    return ds


def _tep_transcript_cua_id(cli_dir: Path, conv_id: str) -> Path | None:
    if not conv_id or not _UUID_RE.match(conv_id):
        # Vẫn cho phép conv_id tuỳ chỉnh trong unit test miễn là tên an toàn không chứa ../
        if not conv_id or any(ch in conv_id for ch in ("/", "\\", "..")):
            return None
    brain_dir = cli_dir / "brain" / conv_id
    cac_ung_vien = (
        brain_dir / ".system_generated" / "logs" / "transcript_full.jsonl",
        brain_dir / ".system_generated" / "logs" / "transcript.jsonl",
        brain_dir / "transcript_full.jsonl",
        brain_dir / "transcript.jsonl",
        cli_dir / "conversations" / f"{conv_id}.jsonl",
    )
    for p in cac_ung_vien:
        try:
            if p.is_file():
                return p
        except OSError:
            continue
    return None


def _tim_conv_id_theo_de(
    cli_dir: Path,
    de_da_gui: str = "",
    de_goc: str = "",
    phieu_id: str = "",
    moc_epoch_bat_dau: float | None = None,
) -> tuple[str, Path | None]:
    """Khi agy bị kill trước lúc xuất JSON, dò read-only brain/<uuid> sửa gần đây khớp USER_INPUT."""
    brain_root = cli_dir / "brain"
    if not brain_root.is_dir() or moc_epoch_bat_dau is None:
        return "", None
    dau_hieu: list[str] = []
    for nguon in (de_goc, de_da_gui):
        dong_dau = next((d.strip() for d in str(nguon or "").splitlines() if d.strip()), "")
        if len(dong_dau) >= 8:
            dau_hieu.append(dong_dau[:80])
    if phieu_id:
        dau_hieu.append(f"de-{phieu_id}.md")
    if not dau_hieu:
        return "", None

    nguong_mtime = float(moc_epoch_bat_dau) - 15.0
    ung_vien: list[tuple[float, str, Path]] = []
    try:
        for thu_muc_id in brain_root.iterdir():
            if not thu_muc_id.is_dir():
                continue
            tep_tr = _tep_transcript_cua_id(cli_dir, thu_muc_id.name)
            if tep_tr is None:
                continue
            try:
                mtime = tep_tr.stat().st_mtime
            except OSError:
                continue
            if mtime >= nguong_mtime:
                ung_vien.append((mtime, thu_muc_id.name, tep_tr))
    except OSError:
        return "", None

    ung_vien.sort(key=lambda item: item[0], reverse=True)
    for _, cid, tep_tr in ung_vien[:25]:
        try:
            with tep_tr.open("r", encoding="utf-8", errors="replace") as f:
                dong_dau_tep = [f.readline() for _ in range(4)]
        except OSError:
            continue
        ghep = "\n".join(dong_dau_tep)
        if any(dh in ghep for dh in dau_hieu):
            return cid, tep_tr
    return "", None


def thu_thap_buoc_agy(
    cfg: dict | None = None,
    viec: dict | None = None,
    stdout: str = "",
    stderr: str = "",
    de_da_gui: str = "",
    moc_epoch_bat_dau: float | None = None,
    cho_phep_doc_hoi_thoai: bool = True,
) -> tuple[list[dict], str, str]:
    """Thu danh sách bước (tối đa toàn bộ để hàm gọi tự cắt 60 cuối), conv_id, và tên nguồn."""
    conv_id = trich_conversation_id(stdout, stderr)
    buoc_stream = trich_buoc_tu_van_ban_json(stdout)
    if not buoc_stream and stderr:
        buoc_stream = trich_buoc_tu_van_ban_json(stderr)
    if buoc_stream:
        return buoc_stream, conv_id, "luong-json"

    if not cho_phep_doc_hoi_thoai:
        return [], conv_id, "khong-co-buoc"

    cli_dir = thu_muc_agy_cli(cfg)
    if cli_dir is None or not cli_dir.is_dir():
        return [], conv_id, "khong-co-buoc"

    tep_tr: Path | None = _tep_transcript_cua_id(cli_dir, conv_id) if conv_id else None
    if tep_tr is None and not conv_id:
        phieu_id = str((viec or {}).get("viec") or "")
        de_goc = str((viec or {}).get("de") or "")
        conv_tim, tep_tim = _tim_conv_id_theo_de(
            cli_dir,
            de_da_gui=de_da_gui,
            de_goc=de_goc,
            phieu_id=phieu_id,
            moc_epoch_bat_dau=moc_epoch_bat_dau,
        )
        if conv_tim and tep_tim is not None:
            conv_id = conv_tim
            tep_tr = tep_tim

    if tep_tr is None:
        return [], conv_id, "khong-co-buoc"

    cac_obj = _doc_jsonl_chi_doc(tep_tr)
    buoc_tr = _trich_buoc_tu_list_doi_tuong(cac_obj)
    if buoc_tr:
        return buoc_tr, conv_id, f"hoi-thoai:{tep_tr.name}"
    return [], conv_id, "khong-co-buoc"


def dinh_dang_nhat_ky_md(
    phieu_id: str,
    trang_thai: str,
    cac_buoc: list[dict],
    ly_do: str = "",
    conversation_id: str = "",
    nguon_buoc: str = "",
    duoi_ra_du_phong: str = "",
) -> str:
    """Dựng nội dung NHAT-KY.md (tối đa 60 bước cuối, đã che mọi bí mật)."""
    buoc_cuoi = list(cac_buoc or [])[-SO_BUOC_TOI_DA:]
    dong: list[str] = [
        f"# Nhật ký debug agy: {phieu_id}",
        "",
        f"- trang_thai: {trang_thai or '-'}",
        f"- ly_do: {ly_do or '(khong)'}",
        f"- conversation_id: {conversation_id or '(khong)'}",
        f"- nguon_buoc: {nguon_buoc or 'khong-co-buoc'}",
        f"- so_buoc_ghi: {len(buoc_cuoi)}",
        "",
        f"## {SO_BUOC_TOI_DA} bước cuối",
    ]
    if not buoc_cuoi:
        dong.append("")
        dong.append("(Chưa trích được bước công cụ từ luồng JSON hay thư mục hội thoại agy.)")
        if duoi_ra_du_phong:
            dong.extend(["", "### Đầu ra cuối (rút gọn)", "```text"])
            for d in _lay_3_dong_cuoi(duoi_ra_du_phong, so_dong=10):
                dong.append(d.replace("```", "'''"))
            dong.append("```")
    else:
        for stt, b in enumerate(buoc_cuoi, start=1):
            ts = str(b.get("thoi_diem") or "-").strip() or "-"
            tool = str(b.get("cong_cu") or "-").strip() or "-"
            lenh = _cat_lenh_200(b.get("lenh") or "-").replace("`", "'")
            ma_thoat = str(b.get("ma_thoat") if b.get("ma_thoat") not in (None, "") else "-")
            dau_ra = list(b.get("dau_ra_cuoi") or [])[-SO_DONG_DAU_RA_CUOI:]
            dong.extend(
                [
                    "",
                    f"### {stt}. [{ts}] {tool}",
                    f"- lenh: `{lenh}`",
                    f"- ma_thoat: `{ma_thoat}`",
                    "- dau_ra_cuoi:",
                    "```text",
                ]
            )
            if dau_ra:
                for d in dau_ra:
                    dong.append(str(d).replace("```", "'''"))
            else:
                dong.append("(khong)")
            dong.append("```")
    return loc_bi_mat_nhat_ky("\n".join(dong).rstrip() + "\n")


def tao_nhat_ky_debug_tu_phien(
    cfg: dict | None,
    viec: dict | None,
    trang_thai: str,
    stdout: str = "",
    stderr: str = "",
    ly_do: str = "",
    de_da_gui: str = "",
    moc_epoch_bat_dau: float | None = None,
    cho_phep_doc_hoi_thoai: bool = True,
) -> str:
    """Tổng hợp NHAT-KY.md sau khi một phiên `chay_agy` kết thúc."""
    phieu_id = str((viec or {}).get("viec") or "phieu")
    cac_buoc, conv_id, nguon_buoc = thu_thap_buoc_agy(
        cfg=cfg,
        viec=viec,
        stdout=stdout,
        stderr=stderr,
        de_da_gui=de_da_gui,
        moc_epoch_bat_dau=moc_epoch_bat_dau,
        cho_phep_doc_hoi_thoai=cho_phep_doc_hoi_thoai,
    )
    duoi_du_phong = "\n".join(part for part in (stderr[-1500:] if stderr else "", stdout[-1500:] if stdout else "") if part)
    return dinh_dang_nhat_ky_md(
        phieu_id=phieu_id,
        trang_thai=trang_thai,
        cac_buoc=cac_buoc,
        ly_do=ly_do,
        conversation_id=conv_id,
        nguon_buoc=nguon_buoc,
        duoi_ra_du_phong=duoi_du_phong,
    )


def thu_tao_nhat_ky_debug_tu_ket_qua(
    cfg: dict | None,
    viec: dict | None,
    trang_thai: str,
    ket_qua=None,
    nhat_ky: str = "",
) -> str | None:
    """Dùng cho `bao_ket_qua_git` khi phiếu không đi qua `linhx_runner.chay_agy` hoặc chỉ truyền chuỗi/JSON."""
    if isinstance(viec, dict) and viec.get("_nhat_ky_debug"):
        return loc_bi_mat_nhat_ky(str(viec["_nhat_ky_debug"]))

    kq_str = str(ket_qua or "")
    nk_str = str(nhat_ky or "")
    co_dau_hieu = bool(
        trich_buoc_tu_van_ban_json(kq_str)
        or trich_conversation_id(kq_str, nk_str)
    )
    if not co_dau_hieu:
        return None
    return tao_nhat_ky_debug_tu_phien(
        cfg=cfg,
        viec=viec,
        trang_thai=trang_thai,
        stdout=kq_str,
        stderr=nk_str,
        ly_do=str((viec or {}).get("_ly_do_dung") or ""),
        cho_phep_doc_hoi_thoai=True,
    )
