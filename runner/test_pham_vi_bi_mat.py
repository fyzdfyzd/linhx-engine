"""Kiểm thử Vá 2: phạm vi sửa (`vung:`) và quét bí mật trên diff commit mới ở `theo_doi` đầu tiên."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import uuid

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runner import hang_doi_git, linhx_runner, rao_phieu  # noqa: E402
from runner._gia_moi_truong import _gia_ram_va_moi_truong_h3  # noqa: F401


def _remove_tree(target_dir: Path) -> None:
    # Xoá thư mục tạm an toàn kể cả tệp chỉ-đọc trong .git trên Windows
    if not target_dir.exists():
        return

    def _on_readonly(func, path_str, _):
        try:
            os.chmod(path_str, stat.S_IWRITE)
            func(path_str)
        except OSError:
            pass

    shutil.rmtree(target_dir, onerror=_on_readonly)


@pytest.fixture
def tmp_path():
    # Tạo thư mục tạm cục bộ trong runner/viec (không conftest, không chạm ngoài vùng)
    work_root = linhx_runner.GOC / "viec"
    existed_before = work_root.exists()
    temp_root = work_root / f"pytest-tmp-va2-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    temp_root.mkdir(parents=True, exist_ok=True)
    try:
        yield temp_root
    finally:
        _remove_tree(temp_root)
        if not existed_before and work_root.exists():
            try:
                next(work_root.iterdir())
            except StopIteration:
                work_root.rmdir()


def _run_git(args: list[str], cwd: Path) -> str:
    # Chạy git cục bộ ở tiền cảnh, không gọi mạng
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    extra_kw = {"creationflags": 0x08000000} if os.name == "nt" else {}
    proc = subprocess.run(
        ["git"] + list(args),
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        **extra_kw,
    )
    return proc.stdout.strip()


def _init_project_repo(repo_dir: Path, initial_files: dict[str, str]) -> str:
    # Khởi tạo repo dự án mẫu cục bộ để giả lập thư mục `theo_doi`
    repo_dir.mkdir(parents=True, exist_ok=True)
    _run_git(["init"], repo_dir)
    _run_git(["config", "user.name", "tho-test"], repo_dir)
    _run_git(["config", "user.email", "tho@linhx.local"], repo_dir)
    _run_git(["config", "commit.gpgsign", "false"], repo_dir)
    for rel, content in initial_files.items():
        p = repo_dir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    _run_git(["add", "-A"], repo_dir)
    _run_git(["commit", "-m", "init project"], repo_dir)
    return _run_git(["rev-parse", "HEAD"], repo_dir)


def _commit_files(repo_dir: Path, updates: dict[str, str | None], message: str = "cap nhat") -> str:
    # Ghi/xoá file và tạo 1 commit mới trong repo `theo_doi`
    for rel, content in updates.items():
        p = repo_dir / rel
        if content is None:
            if p.exists():
                p.unlink()
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
    _run_git(["add", "-A"], repo_dir)
    _run_git(["commit", "-m", message], repo_dir)
    return _run_git(["rev-parse", "HEAD"], repo_dir)


def _setup_queue_env(tmp_path: Path, tickets: dict[str, str]) -> tuple[Path, dict]:
    # Khởi tạo bare repo nhánh hang-doi và cấu hình máy thợ cục bộ
    bare_repo = tmp_path / "remote.git"
    bare_repo.mkdir()
    _run_git(["init", "--bare"], bare_repo)

    seed = tmp_path / "seed"
    seed.mkdir()
    _run_git(["init"], seed)
    _run_git(["config", "user.name", "seed"], seed)
    _run_git(["config", "user.email", "seed@linhx.local"], seed)
    _run_git(["config", "commit.gpgsign", "false"], seed)
    _run_git(["checkout", "-b", "main"], seed)
    (seed / "README.md").write_text("linhx\n", encoding="utf-8")
    _run_git(["add", "-A"], seed)
    _run_git(["commit", "-m", "init"], seed)
    _run_git(["remote", "add", "origin", str(bare_repo)], seed)
    _run_git(["push", "origin", "main"], seed)
    _run_git(["symbolic-ref", "HEAD", "refs/heads/main"], bare_repo)

    _run_git(["checkout", "--orphan", "hang-doi"], seed)
    _run_git(["rm", "-rf", "."], seed)
    moi_dir = seed / "hang-doi" / "moi"
    moi_dir.mkdir(parents=True, exist_ok=True)
    for tid, body in tickets.items():
        (moi_dir / f"{tid}.md").write_text(body, encoding="utf-8")
    _run_git(["add", "-A"], seed)
    _run_git(["commit", "-m", "seed queue"], seed)
    _run_git(["push", "origin", "hang-doi"], seed)

    clone_dir = tmp_path / "worker-clone"
    _run_git(["clone", str(bare_repo), str(clone_dir)], tmp_path)
    work_dir = tmp_path / "worker-work"
    work_dir.mkdir()
    cfg = {
        "nguon": "github",
        "tho": "may-2",
        "agy": "agy-gia",
        "agy_args": "--output-format json",
        "thu_muc": work_dir,
        "nghi": 0.01,
        "repo_hang_doi": clone_dir,
        "nhanh_hang_doi": "hang-doi",
        "remote_hang_doi": "origin",
        "wt_hang_doi": "",
        "thu_muc_drive": tmp_path / "drive",
        "thu_muc_log": tmp_path / "log",
    }
    return bare_repo, cfg


def _read_ket_qua_from_bare(bare_repo: Path, ticket_id: str) -> str:
    return _run_git(["show", f"hang-doi:hang-doi/xong/{ticket_id}/KET-QUA.md"], bare_repo)


def _make_runtime_fake_secrets() -> dict[str, str]:
    # Ghép các token giả lúc chạy để không chứa chuỗi giống bí mật trong mã nguồn
    return {
        "sk_val": "".join(["s", "k-", "ant-", "FakeTokenVal0123456789abcdef"]),
        "aiza_val": "".join(["AI", "za", "SyFakeGoogleKey0123456789abcdefgh"]),
        "ghp_val": "".join(["gh", "p_", "FakeGithubPat0123456789abcdefghijkl"]),
        "xox_val": "".join(["xo", "xb-", "9876543210-FakeSlackTokenAbcdef"]),
        "pem_hdr": "-" * 5 + "BEGIN " + "RSA " + "PRIVATE " + "KEY" + "-" * 5,
        "pwd_raw": "MatKhauGiaTuyetMat_2026!",
    }


def test_parse_vung_and_glob_matching():
    # Phân tích header `vung:` nhiều mẫu glob, cắt chú thích, chuẩn hoá đường dẫn và giữ khi `tu_sua`
    raw = (
        "may: may-2\n"
        "loai: code\n"
        "theo_doi: C:\\linhx\\wt-va2\n"
        'vung: runner/**; "skills\\le\\hang-doi-may\\**" # chỉ sửa 2 vùng này\n'
        "tu_sua: 2\n\n"
        "Cập nhật runner và tài liệu.\n"
    )
    parsed = hang_doi_git.phan_tich_phieu(raw, "va2-code-1")
    assert parsed["vung"] == ["runner/**", "skills/le/hang-doi-may/**"]
    assert hang_doi_git.get_ticket_vung_globs(parsed) == ["runner/**", "skills/le/hang-doi-may/**"]

    vung = parsed["vung"]
    assert rao_phieu.matches_vung("runner/hang_doi_git.py", vung) is True
    assert rao_phieu.matches_vung("runner/bang/bang.py", vung) is True
    assert rao_phieu.matches_vung("skills/le/hang-doi-may/SKILL.md", vung) is True
    assert rao_phieu.matches_vung("canh/rao.py", vung) is False
    assert rao_phieu.matches_vung("skills/le/linhx-chuan/SKILL.md", vung) is False
    assert rao_phieu.matches_vung("README.md", vung) is False

    repair_md = hang_doi_git.build_self_repair_ticket(parsed, "trang_thai: loi\n\nsửa ngoài vùng: canh/rao.py\n")
    assert repair_md is not None
    reparsed = hang_doi_git.phan_tich_phieu(repair_md, "va2-code-1-sua-1")
    assert reparsed["vung"] == ["runner/**", "skills/le/hang-doi-may/**"]
    assert reparsed["tu_sua"] == 1

    legacy = hang_doi_git.phan_tich_phieu("may: bat-ky\n\nViệc cũ không có vung.", "cu-1")
    assert legacy["vung"] == []


def test_secret_scanner_patterns_line_numbers_and_false_positive_safety():
    # Kiểm tra đủ mẫu bí mật, đúng số dòng mới trong diff, không báo nhầm văn bản hướng dẫn / biến code
    fakes = _make_runtime_fake_secrets()
    pwd_assign_quoted = "db_" + "pass" + "word" + f' = "{fakes["pwd_raw"]}"'
    pwd_assign_plain = "pass" + "word" + "=" + fakes["pwd_raw"]

    fake_diff = "\n".join(
        [
            "diff --git a/src/api.py b/src/api.py",
            "index 1111111..2222222 100644",
            "--- a/src/api.py",
            "+++ b/src/api.py",
            "@@ -4,0 +5,6 @@",
            "+def connect(user, password=None):",
            "+    # khoá API dạng sk-/AIza/ghp_/xox, PRIVATE KEY, password=, file .env, tho.env",
            f"+    k1 = '{fakes['sk_val']}'",
            "+    ok = call_db(user, password=user_pw)",
            f"+    k2 = '{fakes['aiza_val']}'",
            f"+    {pwd_assign_quoted}",
            "diff --git a/src/keys.txt b/src/keys.txt",
            "new file mode 100644",
            "--- /dev/null",
            "+++ b/src/keys.txt",
            "@@ -0,0 +1,3 @@",
            f"+{fakes['ghp_val']}",
            f"+{fakes['xox_val']}",
            f"+{fakes['pem_hdr']}",
            "diff --git a/conf/db.ini b/conf/db.ini",
            "new file mode 100644",
            "--- /dev/null",
            "+++ b/conf/db.ini",
            "@@ -0,0 +1,2 @@",
            "+host=127.0.0.1",
            f"+{pwd_assign_plain}",
        ]
    )

    found = rao_phieu.scan_unified_diff_for_secrets(fake_diff)
    assert found == [
        "src/api.py:7",
        "src/api.py:9",
        "src/api.py:10",
        "src/keys.txt:1",
        "src/keys.txt:2",
        "src/keys.txt:3",
        "conf/db.ini:2",
    ]
    joined_found = " | ".join(found)
    for secret_piece in fakes.values():
        assert secret_piece not in joined_found

    assert rao_phieu.is_secret_file_path(".env") is True
    assert rao_phieu.is_secret_file_path("apps/web/.env.production") is True
    assert rao_phieu.is_secret_file_path("runner/tho.env") is True
    assert rao_phieu.is_secret_file_path(".env.example") is False
    assert rao_phieu.is_secret_file_path("runner/tho.env.example") is False


def test_end_to_end_vung_head_recorded_on_claim_and_out_of_scope(tmp_path, capsys):
    # (1) Ghi lại HEAD lúc nhận phiếu ở `theo_doi` đầu tiên; sửa đúng vùng -> `xong`
    # (2) Sửa tràn ra ngoài vùng -> `loi` "sửa ngoài vùng: <file>", không chạy `lenh_kiem`, tự sinh `-sua-1`
    wt_first = tmp_path / "wt-chinh"
    wt_second = tmp_path / "wt-phu"
    head_ban_dau = _init_project_repo(
        wt_first,
        {
            "runner/core.py": "x = 1\n",
            "canh/rao.py": "# rao cu\n",
        },
    )
    _init_project_repo(wt_second, {"outside_ok_in_second.txt": "phu\n"})

    marker_lenh_kiem = tmp_path / "khong_chay_khi_ngoai_vung.txt"
    py_exe = Path(sys.executable).as_posix()

    tickets = {
        "01-dung-vung": (
            "may: may-2\n"
            "loai: code\n"
            f"theo_doi: {wt_first}; {wt_second}\n"
            "vung: runner/**; skills/le/hang-doi-may/**\n\n"
            "Sửa đúng trong phạm vi cho phép.\n"
        ),
        "02-ngoai-vung": (
            "may: may-2\n"
            "loai: code\n"
            f"theo_doi: {wt_first}; {wt_second}\n"
            "vung: runner/**; skills/le/hang-doi-may/**\n"
            f'lenh_kiem: "{py_exe}" -c "import pathlib; pathlib.Path(r\'{marker_lenh_kiem}\').write_text(\'1\')"\n'
            "tu_sua: 1\n\n"
            "Thử sửa nhầm sang canh/rao.py.\n"
        ),
    }
    bare_repo, cfg = _setup_queue_env(tmp_path, tickets)

    # Kiểm trực tiếp `nhan_phieu_git` đã ghi lại HEAD lúc nhận phiếu trước khi agy chạy
    claimed_1 = hang_doi_git.nhan_phieu_git(cfg)
    assert claimed_1 is not None
    assert claimed_1["viec"] == "01-dung-vung"
    assert claimed_1["head_nhan"] == head_ban_dau

    def _agy_dung_vung(_c, _v):
        # Đổi cả ở repo thứ 2 để chứng minh chỉ kiểm repo `theo_doi` đầu tiên theo đặc tả
        _commit_files(wt_second, {"bat_ky_o_wt_2.txt": "ok\n"}, "wt2")
        _commit_files(
            wt_first,
            {
                "runner/core.py": "x = 2\n",
                "skills/le/hang-doi-may/SKILL.md": "# Hàng đợi\n",
            },
            "sua dung vung",
        )
        return "xong", "Đã cập nhật đúng vùng.", "exit=0", 12, 18

    res_1 = hang_doi_git.thuc_thi_phieu_da_nhan(cfg, claimed_1, chay_agy_fn=_agy_dung_vung)
    assert res_1["trang_thai"] == "xong"
    assert res_1["so_file"] == 2
    assert res_1["ngoai_vung"] == []
    assert res_1["bi_mat"] == []
    assert "trang_thai: xong" in _read_ket_qua_from_bare(bare_repo, "01-dung-vung")

    # Phiếu 2: sửa ra ngoài vùng `canh/rao.py` -> bị chặn `loi` "sửa ngoài vùng: canh/rao.py"
    def _agy_ngoai_vung(_c, _v):
        _commit_files(
            wt_first,
            {
                "runner/core.py": "x = 3\n",
                "canh/rao.py": "# sua trai phep\n",
            },
            "sua tran vung",
        )
        return "xong", "Báo cáo xong nhưng sửa tràn vùng.", "exit=0", 15, 20

    res_2 = hang_doi_git.xu_ly_mot_phieu(cfg, chay_agy_fn=_agy_ngoai_vung)
    assert res_2["viec"] == "02-ngoai-vung"
    assert res_2["trang_thai"] == "loi"
    assert res_2["so_file"] == 2
    assert res_2["ngoai_vung"] == ["canh/rao.py"]
    assert not marker_lenh_kiem.exists(), "Ngoài vùng thì không được chạy lenh_kiem"
    kq_2 = _read_ket_qua_from_bare(bare_repo, "02-ngoai-vung")
    assert "trang_thai: loi" in kq_2
    assert "sửa ngoài vùng: canh/rao.py" in kq_2

    # Đã sinh phiếu tự sửa `02-ngoai-vung-sua-1` giữ nguyên `vung:`; lượt sửa chỉ sửa trong vùng -> `xong`
    res_2_sua = hang_doi_git.xu_ly_mot_phieu(
        cfg,
        chay_agy_fn=lambda _c, v: (
            _commit_files(wt_first, {"runner/core.py": "x = 4\n"}, "sua lai trong vung"),
            "xong",
            f"Đã sửa lại {v['viec']}.",
            "exit=0",
            9,
            9,
        )[1:],
    )
    assert res_2_sua["viec"] == "02-ngoai-vung-sua-1"
    assert res_2_sua["trang_thai"] == "xong"
    assert marker_lenh_kiem.exists()

    # Kiểm log runner: mỗi phiếu đúng 1 dòng JSON cả trên stdout (`tho.log`) và `runner.jsonl`
    stdout_lines = [ln.strip() for ln in capsys.readouterr().out.splitlines() if ln.strip().startswith("{")]
    parsed_stdout = [json.loads(ln) for ln in stdout_lines]
    assert [r["phieu"] for r in parsed_stdout] == ["01-dung-vung", "02-ngoai-vung", "02-ngoai-vung-sua-1"]

    runner_jsonl = cfg["thu_muc_log"] / "runner.jsonl"
    assert runner_jsonl.is_file()
    records = [json.loads(ln) for ln in runner_jsonl.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(records) == 3
    assert records[0]["phieu"] == "01-dung-vung" and records[0]["so_file"] == 2 and records[0]["ngoai_vung"] == []
    assert records[1]["phieu"] == "02-ngoai-vung" and records[1]["ngoai_vung"] == ["canh/rao.py"]
    assert records[2]["phieu"] == "02-ngoai-vung-sua-1" and records[2]["ngoai_vung"] == []


def test_end_to_end_secret_detection_redaction_and_env_files(tmp_path, capsys):
    # Quét bí mật trong diff (kể cả commit rồi xoá ở commit kế tiếp, và file .env / tho.env):
    # -> `loi`, chỉ in `file:dòng`, KHÔNG để lộ bất kỳ giá trị bí mật nào ở KET-QUA hay log
    wt_proj = tmp_path / "wt-bi-mat"
    _init_project_repo(wt_proj, {"runner/app.py": "# dau file\nx = 1\n"})
    fakes = _make_runtime_fake_secrets()

    tickets = {
        "01-lo-khoa-api": (
            "may: may-2\n"
            "loai: code\n"
            f"theo_doi: {wt_proj}\n"
            "vung: runner/**\n\n"
            "Kiểm tra chặn lộ khoá API trong code.\n"
        ),
        "02-lo-file-env": (
            "may: may-2\n"
            "loai: code\n"
            f"theo_doi: {wt_proj}\n"
            "vung: **\n\n"
            "Kiểm tra chặn commit file .env và tho.env.\n"
        ),
    }
    bare_repo, cfg = _setup_queue_env(tmp_path, tickets)

    def _agy_lo_khoa(_c, _v):
        # Commit 1 lộ ghp_ rồi xoá ở commit 2; commit 2 còn thêm sk- ở dòng 4 của runner/app.py
        _commit_files(wt_proj, {"runner/tam.py": f"TOKEN = '{fakes['ghp_val']}'\n"}, "commit 1 lo ghp")
        _commit_files(
            wt_proj,
            {
                "runner/tam.py": None,
                "runner/app.py": f"# dau file\nx = 1\ny = 2\nAPI_KEY = '{fakes['sk_val']}'\n",
            },
            "commit 2 xoa tam nhung them sk",
        )
        # Giả lập cả trường hợp agy vô tình nhắc lại giá trị key trong câu trả lời
        return "xong", f"Đã cấu hình {fakes['sk_val']}", f"stderr chua {fakes['ghp_val']}", 10, 10

    res_1 = hang_doi_git.xu_ly_mot_phieu(cfg, chay_agy_fn=_agy_lo_khoa)
    assert res_1["trang_thai"] == "loi"
    assert "runner/app.py:4" in res_1["bi_mat"]
    assert "runner/tam.py:1" in res_1["bi_mat"]

    kq_1 = _read_ket_qua_from_bare(bare_repo, "01-lo-khoa-api")
    assert "trang_thai: loi" in kq_1
    assert "runner/app.py:4" in kq_1
    assert "runner/tam.py:1" in kq_1

    def _agy_lo_env(_c, _v):
        _commit_files(
            wt_proj,
            {
                ".env": "PORT=3000\n",
                "runner/tho.env": "LINHX_THO=may-2\n",
                "runner/tho.env.example": "LINHX_THO=may-mau\n",
            },
            "commit env files",
        )
        return "xong", "Đã thêm cấu hình.", "exit=0", 5, 5

    res_2 = hang_doi_git.xu_ly_mot_phieu(cfg, chay_agy_fn=_agy_lo_env)
    assert res_2["trang_thai"] == "loi"
    assert ".env:1" in res_2["bi_mat"]
    assert "runner/tho.env:1" in res_2["bi_mat"]
    assert not any("tho.env.example" in item for item in res_2["bi_mat"])

    kq_2 = _read_ket_qua_from_bare(bare_repo, "02-lo-file-env")
    assert ".env:1" in kq_2
    assert "runner/tho.env:1" in kq_2

    # Tuyệt đối KHÔNG in giá trị bí mật ở bất kỳ đầu ra nào (KET-QUA, stdout, runner.jsonl, <id>.jsonl)
    out_txt = capsys.readouterr().out
    runner_log_txt = (cfg["thu_muc_log"] / "runner.jsonl").read_text(encoding="utf-8")
    ticket_log_txt = (cfg["thu_muc_log"] / "01-lo-khoa-api.jsonl").read_text(encoding="utf-8")
    combined_outputs = "\n".join(
        [
            kq_1,
            kq_2,
            str(res_1["ket_qua"]),
            str(res_1["nhat_ky"]),
            out_txt,
            runner_log_txt,
            ticket_log_txt,
        ]
    )
    assert fakes["sk_val"] not in combined_outputs
    assert fakes["ghp_val"] not in combined_outputs
    assert "FakeTokenVal0123456789abcdef" not in combined_outputs
    assert "FakeGithubPat0123456789abcdefghijkl" not in combined_outputs


def test_clone_created_inside_agy_session_checks_only_new_commits(tmp_path):
    # Khi `theo_doi` chưa tồn tại lúc nhận phiếu mà được agy `git clone` trong lúc làm:
    # chỉ chấm các commit mới sau mốc clone, không báo nhầm các file có sẵn từ trước khi clone
    origin_proj = tmp_path / "origin-proj"
    _init_project_repo(
        origin_proj,
        {
            "README.md": "co san ngoai vung\n",
            "runner/mod.py": "a = 1\n",
        },
    )
    wt_moi_chua_clone = tmp_path / "wt-clone-trong-agy"

    bare_repo, cfg = _setup_queue_env(
        tmp_path,
        {
            "01-clone-moi": (
                "may: may-2\n"
                "loai: code\n"
                f"theo_doi: {wt_moi_chua_clone}\n"
                "vung: runner/**\n\n"
                "Clone repo mới rồi sửa trong runner/**.\n"
            )
        },
    )

    def _agy_clone_va_sua(_c, _v):
        _run_git(["clone", str(origin_proj), str(wt_moi_chua_clone)], tmp_path)
        _run_git(["config", "user.name", "tho"], wt_moi_chua_clone)
        _run_git(["config", "user.email", "tho@linhx.local"], wt_moi_chua_clone)
        _run_git(["config", "commit.gpgsign", "false"], wt_moi_chua_clone)
        _commit_files(wt_moi_chua_clone, {"runner/mod.py": "a = 2\n"}, "sua runner")
        return "xong", "Clone và sửa xong.", "exit=0", 8, 8

    res = hang_doi_git.xu_ly_mot_phieu(cfg, chay_agy_fn=_agy_clone_va_sua)
    assert res["trang_thai"] == "xong"
    assert res["so_file"] == 1
    assert res["ngoai_vung"] == []
    assert "trang_thai: xong" in _read_ket_qua_from_bare(bare_repo, "01-clone-moi")


def test_worktree_new_branch_ignores_old_secret_and_catches_new_secret(tmp_path):
    # Worktree mới tạo bằng `-b` từ commit cũ có chuỗi giống khoá: base_sha "" chỉ quét commit mới
    fakes = _make_runtime_fake_secrets()
    repo_goc = tmp_path / "repo-goc"
    old_commit = _init_project_repo(
        repo_goc,
        {
            "apps/lab/old.txt": "du lieu cu ngoai vung\n",
            "apps/event/test/e2e/platform.test.js": f"const legacyKey = '{fakes['sk_val']}';\n",
        },
    )

    wt_sach = tmp_path / "wt-ev-sach"
    _run_git(["worktree", "add", str(wt_sach), "-b", "agy/ev-sach", old_commit], repo_goc)
    _commit_files(wt_sach, {"apps/event/src/clean.js": "export const ok = 1;\n"}, "commit sach")

    res_sach = rao_phieu.inspect_new_commits(wt_sach, "", ["apps/event/**"], hang_doi_git.chay_git)
    assert res_sach["bi_mat"] == []
    assert res_sach["ngoai_vung"] == []
    assert res_sach["file_doi"] == ["apps/event/src/clean.js"]
    assert res_sach["dat"] is True

    # Ca ngược: commit mới trên worktree thêm chuỗi giống khoá thì vẫn bắt được đúng dòng mới
    wt_lo = tmp_path / "wt-ev-lo"
    _run_git(["worktree", "add", str(wt_lo), "-b", "agy/ev-lo", old_commit], repo_goc)
    _commit_files(
        wt_lo,
        {"apps/event/src/leak.js": f"// header\nexport const k = '{fakes['ghp_val']}';\n"},
        "commit lo khoa",
    )

    res_lo = rao_phieu.inspect_new_commits(wt_lo, "", ["apps/event/**"], hang_doi_git.chay_git)
    assert res_lo["dat"] is False
    assert res_lo["bi_mat"] == ["apps/event/src/leak.js:2"]


def test_infer_initial_base_oldest_reflog_and_empty_fallback(tmp_path):
    # Lấy SHA mục reflog cũ nhất bất kể chủ đề; chỉ rơi về cây rỗng khi không có reflog
    for subject in (
        "branch: Created from origin/main",
        "reset: moving to abc1234",
        "checkout: moving from main to feat",
        "clone: from https://example.invalid/repo.git",
        "",
    ):
        fake_out = f"newsha999\tcommit: sua\noldsha111\t{subject}\n"
        got = rao_phieu.infer_initial_base_when_cloned_in_agy(
            tmp_path,
            lambda _args, **_kw: subprocess.CompletedProcess(["git"], 0, fake_out, ""),
        )
        assert got == "oldsha111"

    empty_got = rao_phieu.infer_initial_base_when_cloned_in_agy(
        tmp_path,
        lambda _args, **_kw: subprocess.CompletedProcess(["git"], 0, "", ""),
    )
    assert empty_got == rao_phieu.GIT_EMPTY_TREE_SHA

