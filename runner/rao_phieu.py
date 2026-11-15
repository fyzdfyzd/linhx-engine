"""Kiểm phạm vi sửa (`vung:`) và quét bí mật trên diff các commit mới sau khi agy chạy."""
from __future__ import annotations

import os
from pathlib import Path
import re

GIT_EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
OUT_OF_SCOPE_PREFIX = "sửa ngoài vùng"
SECRET_FOUND_PREFIX = "phát hiện bí mật"

# Nhận diện tệp nhạy cảm không được phép commit (.env, tho.env, khoá riêng, chứng chỉ)
_SECRET_FILE_RE = re.compile(
    r"(?i)(?:^|/)(?:\.env|tho\.env|id_rsa|id_ed25519)$"
    r"|(?:^|/)\.env\.(?!example$|mau$|sample$|template$)"
    r"|\.(?:pem|key|p12|pfx|keystore)$"
)

_HUNK_HEADER_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")

# Ghép mảnh mẫu regex để tránh khớp nhầm bộ quét tĩnh của repo và phát hiện đủ khoá bí mật trong diff
_SECRET_LINE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b" + "sk" + r"-[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"\b" + "AI" + "za" + r"[0-9A-Za-z_-]{12,}\b"),
    re.compile(
        r"\b(?:"
        + "gh"
        + r"[pousr]_[A-Za-z0-9_]{12,}|"
        + "github"
        + "_pat_"
        + r"[A-Za-z0-9_]{12,})\b"
    ),
    re.compile(r"\b" + "xox" + r"[a-z]?-[A-Za-z0-9-]{10,}\b"),
    re.compile(r"\b" + "AK" + "IA" + r"[0-9A-Z]{16}\b"),
    re.compile("-" * 5 + "BEGIN" + r" [A-Z0-9 ]*PRIVATE" + " KEY"),
    re.compile(
        r"(?i)\b[a-z0-9_]*"
        + "pass"
        + "word"
        + r"\s*=\s*['\"](?!\$\{|%[A-Za-z_]|<[^>]+>$|\*+$)[^'\"\r\n]{3,}['\"]"
    ),
    re.compile(
        r"(?i)(?:^|[\s?&;'\"-])[a-z0-9_]*"
        + "pass"
        + "word"
        + r"=(?!(?:None|null|true|false|undefined)\b|\$|<[^>]+>|\*+\b|"
        r"[A-Za-z_][A-Za-z0-9_.]*\s*[),\(\]\[])[^\s'\"`,;<>(){}\[\]]{3,}"
    ),
)

_PEM_BLOCK_RE = re.compile(
    "-" * 5
    + "BEGIN"
    + r" [A-Z0-9 ]*PRIVATE"
    + " KEY"
    + r"[\s\S]*?"
    + "-" * 5
    + "END"
    + r" [A-Z0-9 ]*PRIVATE"
    + " KEY"
    + "-" * 5
)


def normalize_rel_path(raw_path: str) -> str:
    # Chuẩn hoá đường dẫn tương đối theo dấu `/` kiểu POSIX
    norm = str(raw_path or "").strip().replace("\\", "/")
    while norm.startswith("./"):
        norm = norm[2:]
    return norm.lstrip("/")


def parse_vung_globs(raw_value, strip_comment_fn) -> list[str]:
    # Phân tích danh sách mẫu glob từ header `vung: glob1; glob2`
    if raw_value is None:
        return []
    if isinstance(raw_value, (list, tuple)):
        items = [str(item).strip() for item in raw_value]
    else:
        cleaned = strip_comment_fn(str(raw_value)).strip()
        if not cleaned:
            return []
        items = [part.strip() for part in cleaned.split(";")]
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        unquoted = (
            item[1:-1].strip()
            if len(item) >= 2 and item[0] == item[-1] and item[0] in ("'", '"')
            else item
        )
        norm = normalize_rel_path(unquoted)
        if norm and norm not in seen:
            seen.add(norm)
            result.append(norm)
    return result


def compile_glob_regex(pattern: str) -> re.Pattern[str]:
    # Chuyển mẫu glob kiểu git (`**` khớp nhiều cấp, `*` khớp trong 1 cấp) sang biểu thức chính quy
    glob_str = normalize_rel_path(pattern)
    if glob_str.endswith("/"):
        glob_str += "**"
    out_parts: list[str] = []
    idx = 0
    length = len(glob_str)
    while idx < length:
        if glob_str.startswith("**/", idx):
            out_parts.append(r"(?:.*/)?")
            idx += 3
        elif glob_str.startswith("**", idx):
            out_parts.append(r".*")
            idx += 2
        elif glob_str[idx] == "*":
            out_parts.append(r"[^/]*")
            idx += 1
        elif glob_str[idx] == "?":
            out_parts.append(r"[^/]")
            idx += 1
        else:
            out_parts.append(re.escape(glob_str[idx]))
            idx += 1
    return re.compile("^" + "".join(out_parts) + "$")


def matches_vung(rel_path: str, vung_globs: list[str] | tuple[str, ...]) -> bool:
    # Kiểm tra đường dẫn tương đối có khớp ít nhất một mẫu glob trong `vung` không
    norm = normalize_rel_path(rel_path)
    if not norm:
        return False
    return any(compile_glob_regex(glob_pat).match(norm) for glob_pat in vung_globs if str(glob_pat).strip())


def is_secret_file_path(rel_path: str) -> bool:
    # Kiểm tra tên tệp có thuộc nhóm tệp bí mật (.env, tho.env, khoá riêng) không
    norm = normalize_rel_path(rel_path)
    return bool(norm and _SECRET_FILE_RE.search(norm))


def line_has_secret(line_text: str) -> bool:
    # Kiểm tra một dòng thêm mới trong diff có chứa chuỗi bí mật không
    if not line_text:
        return False
    return any(rx.search(line_text) for rx in _SECRET_LINE_PATTERNS)


def redact_secrets_in_text(text: str | None) -> str:
    # Che mọi giá trị bí mật nếu vô tình xuất hiện trong văn bản nhật ký / câu trả lời
    if not text:
        return ""
    redacted = _PEM_BLOCK_RE.sub("[DA-CHE-BI-MAT]", str(text))
    for rx in _SECRET_LINE_PATTERNS:
        redacted = rx.sub("[DA-CHE-BI-MAT]", redacted)
    return redacted


def scan_unified_diff_for_secrets(diff_text: str) -> list[str]:
    # Quét unified diff (`-U0`) và chỉ trả danh sách `<file>:<dòng>`, tuyệt đối không lưu giá trị bí mật
    findings: list[str] = []
    seen: set[str] = set()
    current_file: str | None = None
    new_line_no = 0

    for raw_line in str(diff_text or "").splitlines():
        if raw_line.startswith("diff --git "):
            current_file = None
            new_line_no = 0
            continue
        if raw_line.startswith("+++ "):
            if raw_line == "+++ /dev/null" or raw_line.startswith("+++ /dev/null\t"):
                current_file = None
            elif raw_line.startswith("+++ b/"):
                current_file = normalize_rel_path(raw_line[6:])
            else:
                current_file = normalize_rel_path(raw_line[4:])
            continue
        if raw_line.startswith("@@ "):
            m_hunk = _HUNK_HEADER_RE.match(raw_line)
            new_line_no = int(m_hunk.group(1)) if m_hunk else 0
            continue
        if current_file is None or new_line_no <= 0:
            continue
        if raw_line.startswith("+") and not raw_line.startswith("+++"):
            if line_has_secret(raw_line[1:]):
                loc = f"{current_file}:{new_line_no}"
                if loc not in seen:
                    seen.add(loc)
                    findings.append(loc)
            new_line_no += 1
        elif raw_line.startswith(" "):
            new_line_no += 1
    return findings


def _parse_name_status(output_text: str) -> tuple[list[str], list[str]]:
    # Tách danh sách tất cả file đổi và danh sách file bí mật thêm/sửa (`status != D`) từ `--name-status`
    changed_files: list[str] = []
    changed_seen: set[str] = set()
    secret_files: list[str] = []
    secret_seen: set[str] = set()

    for raw_line in str(output_text or "").splitlines():
        line = raw_line.strip()
        if not line or "\t" not in line:
            continue
        parts = line.split("\t")
        status_code = parts[0].strip().upper()
        for raw_p in parts[1:]:
            rel = normalize_rel_path(raw_p)
            if not rel:
                continue
            if rel not in changed_seen:
                changed_seen.add(rel)
                changed_files.append(rel)
            if not status_code.startswith("D") and is_secret_file_path(rel) and rel not in secret_seen:
                secret_seen.add(rel)
                secret_files.append(rel)
    return changed_files, secret_files


def resolve_tracked_git_repo(
    cfg: dict | None,
    viec: dict | None,
    chay_git_fn,
    kiem_tra_thu_muc_fn,
    strip_comment_fn,
    goc_runner: Path,
) -> tuple[Path | None, Path | None, str, bool]:
    # Tìm gốc git của thư mục `theo_doi` đầu tiên (chặn trượt nhầm ra repo cha chứa `runner/viec`)
    meta = (viec or {}).get("meta") if isinstance((viec or {}).get("meta"), dict) else {}
    raw_tracked = meta.get("theo_doi") or ((viec or {}).get("theo_doi") if isinstance(viec, dict) else "") or ""
    cleaned = strip_comment_fn(str(raw_tracked))
    tracked_items = [item.strip() for item in cleaned.split(";") if item.strip()]

    limit_dir = (cfg or {}).get("gioi_han_thu_muc")
    if limit_dir is None and os.environ.get("LINHX_GIOI_HAN_THU_MUC", "").strip():
        limit_dir = Path(os.environ["LINHX_GIOI_HAN_THU_MUC"].strip())

    outer_roots: set[str] = {os.path.normcase(str(goc_runner.parent.resolve()))}
    if cfg and cfg.get("repo_hang_doi"):
        try:
            outer_roots.add(os.path.normcase(str(Path(cfg["repo_hang_doi"]).resolve())))
        except OSError:
            pass

    if tracked_items:
        first_item = tracked_items[0]
        if len(first_item) >= 2 and first_item[0] == first_item[-1] and first_item[0] in ("'", '"'):
            first_item = first_item[1:-1].strip()
        target = Path(first_item)
        ok_dir, reason = kiem_tra_thu_muc_fn(target, limit_dir)
        if not ok_dir:
            return None, None, reason, True
        if not target.is_dir():
            return target, None, f"không tìm thấy thư mục theo_doi đầu tiên: {target}", True
        p_top = chay_git_fn(["rev-parse", "--show-toplevel"], cwd=target, check=False, timeout=15)
        if p_top.returncode != 0 or not p_top.stdout.strip():
            return target, None, f"thư mục theo_doi đầu tiên chưa phải git repo: {target}", True
        toplevel = Path(p_top.stdout.strip()).resolve()
        target_resolved = target.resolve()
        if not (target / ".git").exists():
            top_nc = os.path.normcase(str(toplevel))
            target_nc = os.path.normcase(str(target_resolved))
            if target_nc != top_nc and top_nc in outer_roots:
                return target, None, f"thư mục theo_doi đầu tiên chưa phải git repo: {target}", True
        return target, toplevel, "", True

    fallback = (cfg or {}).get("thu_muc")
    if fallback:
        fb_path = Path(fallback)
        ok_dir, reason = kiem_tra_thu_muc_fn(fb_path, limit_dir)
        if ok_dir and fb_path.is_dir() and (fb_path / ".git").exists():
            p_top = chay_git_fn(["rev-parse", "--show-toplevel"], cwd=fb_path, check=False, timeout=15)
            if p_top.returncode == 0 and p_top.stdout.strip():
                return fb_path, Path(p_top.stdout.strip()).resolve(), "", False
    return None, None, "thiếu thư mục theo_doi", False


def capture_repo_head(repo_toplevel: Path | None, chay_git_fn) -> str:
    # Ghi lại SHA của `HEAD` lúc nhận phiếu (nếu repo mới `git init` chưa có commit thì trả cây rỗng)
    if repo_toplevel is None:
        return ""
    proc = chay_git_fn(["rev-parse", "--verify", "-q", "HEAD"], cwd=repo_toplevel, check=False, timeout=15)
    if proc.returncode == 0 and proc.stdout.strip():
        return proc.stdout.strip()
    return GIT_EMPTY_TREE_SHA


def infer_initial_base_when_cloned_in_agy(repo_toplevel: Path, chay_git_fn) -> str:
    # Khi `theo_doi` chưa tồn tại lúc nhận phiếu mà được agy `git clone` trong phiên, lấy mốc clone đầu tiên từ reflog
    proc = chay_git_fn(["reflog", "--format=%H\t%gs", "HEAD"], cwd=repo_toplevel, check=False, timeout=15)
    if proc.returncode == 0 and proc.stdout.strip():
        for raw_line in reversed(proc.stdout.splitlines()):
            sha, _, subject = raw_line.strip().partition("\t")
            if sha.strip() and subject.strip().lower().startswith("clone:"):
                return sha.strip()
    return GIT_EMPTY_TREE_SHA


def inspect_new_commits(
    repo_toplevel: Path,
    base_sha: str,
    vung_globs: list[str] | tuple[str, ...],
    chay_git_fn,
) -> dict:
    # Lấy diff các commit mới so với `base_sha`, kiểm phạm vi `vung` và quét bí mật (chỉ giữ `file:dòng`)
    p_head = chay_git_fn(["rev-parse", "--verify", "-q", "HEAD"], cwd=repo_toplevel, check=False, timeout=15)
    head_sau = p_head.stdout.strip() if p_head.returncode == 0 else ""
    if not head_sau:
        return {"dat": True, "so_file": 0, "file_doi": [], "ngoai_vung": [], "bi_mat": [], "thong_diep_loi": ""}

    effective_base = (base_sha or "").strip() or infer_initial_base_when_cloned_in_agy(repo_toplevel, chay_git_fn)
    if effective_base == head_sau:
        return {"dat": True, "so_file": 0, "file_doi": [], "ngoai_vung": [], "bi_mat": [], "thong_diep_loi": ""}

    if effective_base != GIT_EMPTY_TREE_SHA:
        p_check = chay_git_fn(["cat-file", "-e", f"{effective_base}^{{tree}}"], cwd=repo_toplevel, check=False, timeout=15)
        if p_check.returncode != 0:
            effective_base = infer_initial_base_when_cloned_in_agy(repo_toplevel, chay_git_fn)
            if effective_base == head_sau:
                return {"dat": True, "so_file": 0, "file_doi": [], "ngoai_vung": [], "bi_mat": [], "thong_diep_loi": ""}

    p_ns = chay_git_fn(
        ["-c", "core.quotepath=false", "diff", "--no-renames", "--name-status", effective_base, head_sau],
        cwd=repo_toplevel,
        check=False,
        timeout=30,
    )
    file_doi, secret_files = _parse_name_status(p_ns.stdout)

    ngoai_vung = [f for f in file_doi if not matches_vung(f, vung_globs)] if vung_globs else []

    p_diff = chay_git_fn(
        ["-c", "core.quotepath=false", "diff", "--no-renames", "-U0", effective_base, head_sau],
        cwd=repo_toplevel,
        check=False,
        timeout=60,
    )
    bi_mat = scan_unified_diff_for_secrets(p_diff.stdout)
    seen_bi_mat = set(bi_mat)
    seen_secret_files = set(secret_files)

    # Nếu có nhiều hơn 1 commit mới, quét thêm từng commit trung gian để chặn lộ bí mật rồi xoá ở commit sau
    if effective_base != GIT_EMPTY_TREE_SHA:
        p_revs = chay_git_fn(["rev-list", "--reverse", f"{effective_base}..{head_sau}"], cwd=repo_toplevel, check=False, timeout=15)
        commits = [c.strip() for c in p_revs.stdout.splitlines() if c.strip()] if p_revs.returncode == 0 else []
        if len(commits) > 1:
            for commit_sha in commits:
                p_c_ns = chay_git_fn(
                    ["-c", "core.quotepath=false", "show", "--format=", "--no-renames", "--name-status", commit_sha],
                    cwd=repo_toplevel,
                    check=False,
                    timeout=30,
                )
                _, c_sec_files = _parse_name_status(p_c_ns.stdout)
                for sf in c_sec_files:
                    if sf not in seen_secret_files:
                        seen_secret_files.add(sf)
                        secret_files.append(sf)
                p_c_diff = chay_git_fn(
                    ["-c", "core.quotepath=false", "show", "--format=", "--no-renames", "-U0", commit_sha],
                    cwd=repo_toplevel,
                    check=False,
                    timeout=30,
                )
                for loc in scan_unified_diff_for_secrets(p_c_diff.stdout):
                    if loc not in seen_bi_mat:
                        seen_bi_mat.add(loc)
                        bi_mat.append(loc)

    for sf in secret_files:
        if not any(loc.startswith(f"{sf}:") for loc in bi_mat):
            loc_file = f"{sf}:1"
            if loc_file not in seen_bi_mat:
                seen_bi_mat.add(loc_file)
                bi_mat.append(loc_file)

    error_lines: list[str] = [f"{OUT_OF_SCOPE_PREFIX}: {f}" for f in ngoai_vung]
    if bi_mat:
        error_lines.append(f"{SECRET_FOUND_PREFIX}: {', '.join(bi_mat)}")

    return {
        "dat": (not ngoai_vung) and (not bi_mat),
        "so_file": len(file_doi),
        "file_doi": file_doi,
        "ngoai_vung": ngoai_vung,
        "bi_mat": bi_mat,
        "thong_diep_loi": "\n".join(error_lines),
    }
