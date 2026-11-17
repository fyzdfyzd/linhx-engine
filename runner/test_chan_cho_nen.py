from __future__ import annotations

import ctypes
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import time
import uuid

import pytest

from runner import hang_doi_git, linhx_runner, nhat_ky_agy
from runner._gia_moi_truong import _gia_ram_va_moi_truong_h3  # noqa: F401  (fixture autouse, thay conftest)


def _remove_tree(target_dir: Path) -> None:
    if not target_dir.exists():
        return

    def _handle_readonly(func, path_str, _):
        try:
            os.chmod(path_str, stat.S_IWRITE)
            func(path_str)
        except OSError:
            pass

    shutil.rmtree(target_dir, onerror=_handle_readonly)


@pytest.fixture
def tmp_path():
    work_root = linhx_runner.GOC / "viec"
    existed_before = work_root.exists()
    temp_root = work_root / f"pytest-tmp-ccn-{os.getpid()}-{uuid.uuid4().hex[:8]}"
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


def _tao_kho_hang_doi(tmp_path: Path, phieu_moi: dict[str, str]) -> tuple[Path, Path, Path]:
    bare = tmp_path / f"remote-{uuid.uuid4().hex[:6]}.git"
    bare.mkdir(parents=True)
    _run_git(["init", "--bare"], bare)

    seed = tmp_path / f"seed-{uuid.uuid4().hex[:6]}"
    seed.mkdir()
    _run_git(["init"], seed)
    _run_git(["config", "user.name", "seed"], seed)
    _run_git(["config", "user.email", "seed@linhx.local"], seed)
    _run_git(["config", "commit.gpgsign", "false"], seed)

    _run_git(["checkout", "-b", "main"], seed)
    (seed / "README.md").write_text("linhx-engine\n", encoding="utf-8")
    _run_git(["add", "-A"], seed)
    _run_git(["commit", "-m", "init main"], seed)
    _run_git(["remote", "add", "origin", str(bare)], seed)
    _run_git(["push", "origin", "main"], seed)
    _run_git(["symbolic-ref", "HEAD", "refs/heads/main"], bare)

    _run_git(["checkout", "--orphan", "hang-doi"], seed)
    _run_git(["rm", "-rf", "."], seed)
    moi_dir = seed / "hang-doi" / "moi"
    moi_dir.mkdir(parents=True, exist_ok=True)
    for ten, noi_dung in phieu_moi.items():
        (moi_dir / f"{ten}.md").write_text(noi_dung, encoding="utf-8")
    (seed / "hang-doi" / "dang" / ".gitkeep").parent.mkdir(parents=True, exist_ok=True)
    (seed / "hang-doi" / "dang" / ".gitkeep").write_text("", encoding="utf-8")
    (seed / "hang-doi" / "xong" / ".gitkeep").parent.mkdir(parents=True, exist_ok=True)
    (seed / "hang-doi" / "xong" / ".gitkeep").write_text("", encoding="utf-8")
    _run_git(["add", "-A"], seed)
    _run_git(["commit", "-m", "init hang-doi"], seed)
    _run_git(["push", "origin", "hang-doi"], seed)

    clone = tmp_path / f"clone-{uuid.uuid4().hex[:6]}"
    _run_git(["clone", "-b", "main", str(bare), str(clone)], tmp_path)
    _run_git(["config", "user.name", "may-2"], clone)
    _run_git(["config", "user.email", "may-2@linhx.local"], clone)
    _run_git(["config", "commit.gpgsign", "false"], clone)
    return bare, clone, tmp_path / "viec"


def _tien_trinh_con_song(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        STILL_ACTIVE = 259
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
        if not handle:
            return False
        try:
            exit_code = ctypes.c_ulong(0)
            ok = ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
            return bool(ok and exit_code.value == STILL_ACTIVE)
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    try:
        os.kill(int(pid), 0)
        return True
    except OSError:
        return False


def _tao_cfg(tmp_path: Path, clone: Path, tm_viec: Path, agy_cli_dir: Path | None = None) -> dict:
    tm_viec.mkdir(parents=True, exist_ok=True)
    cfg = {
        "nguon": "github",
        "tho": "may-2",
        "agy": "agy-gia",
        "agy_args": "--output-format json",
        "thu_muc": tm_viec,
        "nghi": 0.01,
        "tran_phut": 40,
        "khong_tien_phut": 20,
        "repo_hang_doi": clone,
        "nhanh_hang_doi": "hang-doi",
        "remote_hang_doi": "origin",
        "wt_hang_doi": "",
        "thu_muc_drive": tmp_path / "drive",
        "thu_muc_log": tmp_path / "log",
    }
    if agy_cli_dir is not None:
        cfg["thu_muc_agy_cli"] = agy_cli_dir
    return cfg


def test_nhan_dien_cac_mau_cho_tac_vu_nen_va_bo_qua_success():
    assert linhx_runner.phat_hien_dong_cho_tac_vu_nen("waiting up to 40m0s for 1 background task(s)")
    assert linhx_runner.phat_hien_dong_cho_tac_vu_nen(
        "root agent idle; waiting up to 40m0s for 1 background task(s)",
        la_stderr=True,
    )
    assert linhx_runner.phat_hien_dong_cho_tac_vu_nen("root agent idle")

    json_err_escape = json.dumps(
        {
            "conversation_id": "11111111-1111-1111-1111-111111111111",
            "status": "ERROR",
            "response": "Dừng vì chờ lệnh hoàn tất quá lâu.",
        },
        ensure_ascii=True,
    )
    assert linhx_runner.phat_hien_luong_cho_tac_vu_nen(json_err_escape)

    json_success_nhac_loi = json.dumps(
        {
            "conversation_id": "22222222-2222-2222-2222-222222222222",
            "status": "SUCCESS",
            "response": "Đã sửa xong lỗi waiting up to 40m0s for 1 background task, root agent idle, và status ERROR chờ lệnh hoàn tất.",
        },
        ensure_ascii=False,
    )
    assert linhx_runner.phat_hien_luong_cho_tac_vu_nen(json_success_nhac_loi) == ""


def test_canh_nen_co_log_tang_hoac_doi_file_khong_dung(tmp_path, monkeypatch):
    """Gặp waiting background task nhưng log tác vụ nền tăng dòng trong 5 phút -> vẫn để chạy tới xong."""
    tm_theo_doi = tmp_path / "repo-theo-doi"
    tm_theo_doi.mkdir(parents=True)
    log_nen = tm_theo_doi / "bg-task.log"
    log_nen.write_text("line 1 init\n", encoding="utf-8")

    started_flag = tmp_path / "started.flag"
    done_flag = tmp_path / "done.flag"

    bare, clone, tm_viec = _tao_kho_hang_doi(
        tmp_path,
        {
            "yl-canh-nen-co-log": (
                "may: may-2\n"
                "loai: code\n"
                "tran_phut: 40\n"
                "khong_tien_phut: 20\n"
                "tu_sua: 2\n"
                f"theo_doi: {tm_theo_doi}\n\n"
                "Chạy tác vụ nền có log tăng dần."
            )
        },
    )

    payload_ok = {
        "conversation_id": "33333333-4444-5555-6666-777777777777",
        "status": "SUCCESS",
        "response": "Tác vụ nền ghi log xong.",
        "usage": {"input_tokens": 111, "output_tokens": 22},
    }
    script_ok = tmp_path / "agy_nen_co_log.py"
    script_ok.write_text(
        (
            "import json, pathlib, sys, time\n"
            "print('root agent idle; waiting up to 40m0s for 1 background task(s)', file=sys.stderr, flush=True)\n"
            f"pathlib.Path(r'{started_flag}').write_text('ok', encoding='utf-8')\n"
            f"done_p = pathlib.Path(r'{done_flag}')\n"
            "han = time.monotonic() + 30.0\n"
            "while not done_p.exists() and time.monotonic() < han:\n"
            "    time.sleep(0.01)\n"
            f"print({json.dumps(json.dumps(payload_ok))}, flush=True)\n"
        ),
        encoding="utf-8",
    )

    fake_clock = [0.0]
    da_cho_pipe = [False]
    cac_moc_log = {180.0: False, 360.0: False}  # 3p: tăng dòng log; 6p: file mới trong theo_doi -> sống qua 500s (> 180+300)
    nhip_ghi_lai: list[tuple[float, str]] = []
    goc_ghi_nhip = hang_doi_git.ghi_nhip_phieu_git

    def _theo_doi_ghi_nhip(cfg_p, phieu_id_p, phut_da_chay, dong_cuoi, gio_chuoi=""):
        nhip_ghi_lai.append((phut_da_chay, dong_cuoi))
        return goc_ghi_nhip(cfg_p, phieu_id_p, phut_da_chay, dong_cuoi, gio_chuoi=gio_chuoi)

    def _fake_sleep(giay: float) -> None:
        if not started_flag.exists():
            time.sleep(0.01)
            return
        if not da_cho_pipe[0]:
            time.sleep(0.06)
            da_cho_pipe[0] = True
        fake_clock[0] += float(giay)
        if fake_clock[0] >= 180.0 and not cac_moc_log[180.0]:
            cac_moc_log[180.0] = True
            with log_nen.open("a", encoding="utf-8") as fh:
                fh.write("line 2 progress at 3m\n")
        if fake_clock[0] >= 360.0 and not cac_moc_log[360.0]:
            cac_moc_log[360.0] = True
            (tm_theo_doi / "progress.txt").write_text("file moi trong theo_doi o 6m\n", encoding="utf-8")
        if fake_clock[0] >= 500.0 and not done_flag.exists():
            done_flag.write_text("done", encoding="utf-8")
            time.sleep(0.05)
        if int(fake_clock[0]) % 50 == 0:
            time.sleep(0.001)

    monkeypatch.setattr(hang_doi_git, "duong_dan_log_runner", lambda cfg: tmp_path / "runner.jsonl")
    monkeypatch.setattr(hang_doi_git, "ghi_nhip_phieu_git", _theo_doi_ghi_nhip)
    monkeypatch.setattr(linhx_runner, "_dong_ho", lambda: fake_clock[0])
    monkeypatch.setattr(linhx_runner, "_ngu", _fake_sleep)
    monkeypatch.setattr(linhx_runner, "_doc_cpu_cay_agy", lambda pid: 0.0)
    orig_popen = subprocess.Popen
    monkeypatch.setattr(
        linhx_runner,
        "_tao_tien_trinh_agy",
        lambda cmd, **kw: orig_popen([sys.executable, str(script_ok)], **kw),
    )

    cfg = _tao_cfg(tmp_path, clone, tm_viec)
    cfg["nhip_phut"] = 2.0
    kq = hang_doi_git.xu_ly_mot_phieu(cfg)

    assert kq is not None
    assert kq["trang_thai"] == "xong"
    assert fake_clock[0] >= 500.0
    assert kq["token_vao"] == 111
    assert kq["token_ra"] == 22
    assert any("đang chờ nền · log cuối" in d for _, d in nhip_ghi_lai)

    tm_kt = tmp_path / "kt-co-log"
    _run_git(["clone", "-b", "hang-doi", str(bare), str(tm_kt)], tmp_path)
    nd_kq = (tm_kt / "hang-doi" / "xong" / "yl-canh-nen-co-log" / "KET-QUA.md").read_text(encoding="utf-8")
    assert "trang_thai: xong\n" in nd_kq
    assert "Tác vụ nền ghi log xong." in nd_kq
    assert not (tm_kt / "hang-doi" / "moi" / "yl-canh-nen-co-log-sua-1.md").exists()


def test_canh_nen_log_tasks_agy_cli_tang_dong_khong_dung(tmp_path, monkeypatch):
    """Log `.system_generated/tasks/task-1.log` tăng dòng trong 5 phút -> vẫn cho chạy tiếp tới xong."""
    conv_id = "44444444-5555-6666-7777-888888888888"
    cli_dir = tmp_path / "agy-cli-tasks"
    tasks_dir = cli_dir / "brain" / conv_id / ".system_generated" / "tasks"
    tasks_dir.mkdir(parents=True)
    task_log = tasks_dir / "task-1.log"
    task_log.write_text("boot\n", encoding="utf-8")

    started_flag = tmp_path / "started_cli.flag"
    done_flag = tmp_path / "done_cli.flag"
    payload_ok = {"status": "SUCCESS", "response": "Task log ok"}
    script_ok = tmp_path / "agy_cli_task.py"
    script_ok.write_text(
        (
            "import pathlib, sys, time\n"
            "print('waiting up to 40m0s for 1 background task(s)', file=sys.stderr, flush=True)\n"
            f"pathlib.Path(r'{started_flag}').write_text('ok', encoding='utf-8')\n"
            f"done_p = pathlib.Path(r'{done_flag}')\n"
            "han = time.monotonic() + 30.0\n"
            "while not done_p.exists() and time.monotonic() < han:\n"
            "    time.sleep(0.01)\n"
            f"print({json.dumps(json.dumps(payload_ok))}, flush=True)\n"
        ),
        encoding="utf-8",
    )

    fake_clock = [0.0]
    da_cho_pipe = [False]
    moc_cli = {180.0: False, 360.0: False}

    def _fake_sleep(giay: float) -> None:
        if not started_flag.exists():
            time.sleep(0.01)
            return
        if not da_cho_pipe[0]:
            time.sleep(0.06)
            da_cho_pipe[0] = True
        fake_clock[0] += float(giay)
        if fake_clock[0] >= 180.0 and not moc_cli[180.0]:
            moc_cli[180.0] = True
            with task_log.open("a", encoding="utf-8") as fh:
                fh.write("task output line 2\n")
        if fake_clock[0] >= 360.0 and not moc_cli[360.0]:
            moc_cli[360.0] = True
            with task_log.open("a", encoding="utf-8") as fh:
                fh.write("task output line 3\n")
        if fake_clock[0] >= 480.0 and not done_flag.exists():
            done_flag.write_text("ok", encoding="utf-8")
            time.sleep(0.05)
        if int(fake_clock[0]) % 50 == 0:
            time.sleep(0.001)

    monkeypatch.setattr(linhx_runner, "_dong_ho", lambda: fake_clock[0])
    monkeypatch.setattr(linhx_runner, "_ngu", _fake_sleep)
    monkeypatch.setattr(linhx_runner, "_doc_cpu_cay_agy", lambda pid: 0.0)
    orig_popen = subprocess.Popen
    monkeypatch.setattr(
        linhx_runner,
        "_tao_tien_trinh_agy",
        lambda cmd, **kw: orig_popen([sys.executable, str(script_ok)], **kw),
    )

    cfg = _tao_cfg(tmp_path, tmp_path, tmp_path / "viec-cli-task", agy_cli_dir=cli_dir)
    viec = hang_doi_git.phan_tich_phieu("may: may-2\nloai: code\ntran_phut: 40\n\nTask cli.", "p-cli-task")
    tt, kq, _, _, _ = linhx_runner.chay_agy(cfg, viec)
    assert tt == "xong"
    assert "Task log ok" in kq
    assert fake_clock[0] >= 480.0


def test_dung_cay_va_tao_phieu_sua_khi_canh_nen_im_5_phut(tmp_path, monkeypatch):
    """Vào CANH NỀN rồi im hoàn toàn 5 phút (dù CPU tick nhẹ) -> dừng cả cây, lý do cho-nen-im-lang."""
    tm_theo_doi = tmp_path / "repo-im-lang"
    tm_theo_doi.mkdir(parents=True)
    bare, clone, tm_viec = _tao_kho_hang_doi(
        tmp_path,
        {
            "yl-cho-nen": (
                "may: may-2\n"
                "loai: code\n"
                "tran_phut: 40\n"
                "khong_tien_phut: 20\n"
                "tu_sua: 2\n"
                f"theo_doi: {tm_theo_doi}\n\n"
                "Sửa module ABC và kiểm bằng pytest."
            )
        },
    )
    pid_file = tmp_path / "grandchild.pid"
    script_gia = tmp_path / "agy_treo_nen.py"
    script_gia.write_text(
        (
            "import pathlib, subprocess, sys, time\n"
            f"chau = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)'])\n"
            f"pathlib.Path(r'{pid_file}').write_text(str(chau.pid), encoding='utf-8')\n"
            "print('root agent idle; waiting up to 40m0s for 1 background task(s)', file=sys.stderr, flush=True)\n"
            "time.sleep(120)\n"
        ),
        encoding="utf-8",
    )

    fake_clock = [0.0]
    da_cho_pipe = [False]

    def _fake_sleep(giay: float) -> None:
        if not pid_file.exists():
            time.sleep(0.01)
            return
        if not da_cho_pipe[0]:
            time.sleep(0.06)
            da_cho_pipe[0] = True
        fake_clock[0] += float(giay)
        if int(fake_clock[0]) % 50 == 0:
            time.sleep(0.001)

    monkeypatch.setattr(hang_doi_git, "duong_dan_log_runner", lambda cfg: tmp_path / "runner.jsonl")
    monkeypatch.setattr(linhx_runner, "_dong_ho", lambda: fake_clock[0])
    monkeypatch.setattr(linhx_runner, "_ngu", _fake_sleep)
    # Dev server rảnh vẫn nhích CPU nhỏ: không được phép kéo dài ngưỡng 5 phút canh nền
    monkeypatch.setattr(linhx_runner, "_doc_cpu_cay_agy", lambda pid: fake_clock[0] * 0.05)
    orig_popen = subprocess.Popen
    monkeypatch.setattr(
        linhx_runner,
        "_tao_tien_trinh_agy",
        lambda cmd, **kw: orig_popen([sys.executable, str(script_gia)], **kw),
    )

    cfg = _tao_cfg(tmp_path, clone, tm_viec)
    kq = hang_doi_git.xu_ly_mot_phieu(cfg)

    assert kq is not None
    # Không dừng ngay ở 0s, cũng không chờ tới khong_tien_phut (20p): dừng đúng quanh mốc 5 phút (300s)
    assert 300.0 <= fake_clock[0] <= 315.0, f"Thời gian dừng bất thường: {fake_clock[0]:.2f}s"
    assert kq["trang_thai"] == "dung"
    assert linhx_runner.LY_DO_CHO_NEN_IM_LANG in kq["nhat_ky"]

    # Cay tien trinh (cha + chau 120s) phai bi diet sach (cho toi da 2s cho Windows don handle)
    chau_pid = int(pid_file.read_text(encoding="utf-8").strip())
    han_don = time.monotonic() + 2.0
    while time.monotonic() < han_don and _tien_trinh_con_song(chau_pid):
        time.sleep(0.05)
    assert not _tien_trinh_con_song(chau_pid)

    # Kiem tra KET-QUA.md, NHAT-KY.md va phieu -sua-1 tren remote
    tm_kt = tmp_path / "kt-remote"
    _run_git(["clone", "-b", "hang-doi", str(bare), str(tm_kt)], tmp_path)
    nd_kq = (tm_kt / "hang-doi" / "xong" / "yl-cho-nen" / "KET-QUA.md").read_text(encoding="utf-8")
    assert "trang_thai: dung\n" in nd_kq
    assert "ly_do: cho-nen-im-lang\n" in nd_kq
    assert (tm_kt / "hang-doi" / "xong" / "yl-cho-nen" / "NHAT-KY.md").is_file()

    tep_sua = tm_kt / "hang-doi" / "moi" / "yl-cho-nen-sua-1.md"
    assert tep_sua.is_file()
    parsed_sua = hang_doi_git.phan_tich_phieu(tep_sua.read_text(encoding="utf-8"), "yl-cho-nen-sua-1")
    assert parsed_sua["tu_sua"] == 1
    assert parsed_sua["de"].startswith(
        "Lượt trước chạy tác vụ nền không ghi log rồi chờ. "
        "Tác vụ nền phải có timeout, ghi log vào thư mục theo_doi; dev server/watch phải tắt khi xong."
    )
    assert "Sửa module ABC và kiểm bằng pytest." in parsed_sua["de"]


def test_status_error_cho_lenh_hoan_tat_tao_dung_va_nhat_ky_tu_conv_id(tmp_path, monkeypatch):
    conv_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    cli_dir = tmp_path / "agy-cli"
    logs_dir = cli_dir / "brain" / conv_id / ".system_generated" / "logs"
    logs_dir.mkdir(parents=True)
    transcript = logs_dir / "transcript.jsonl"
    transcript.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "step_index": 0,
                        "type": "PLANNER_RESPONSE",
                        "created_at": "2026-11-15T06:00:00Z",
                        "tool_calls": [
                            {
                                "name": "run_command",
                                "args": {"CommandLine": '"python -m pytest -q"'},
                            }
                        ],
                    }
                ),
                json.dumps(
                    {
                        "step_index": 1,
                        "type": "GENERIC",
                        "status": "DONE",
                        "created_at": "2026-11-15T06:00:05Z",
                        "content": "Created At: 1\nCommand exited with code 0.\n\nCommand output:\n2 passed in 0.12s\n",
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    bare, clone, tm_viec = _tao_kho_hang_doi(
        tmp_path,
        {"yl-err-json": "may: may-2\nloai: code\ntu_sua: 1\n\nChạy test dự án."},
    )
    script_err = tmp_path / "agy_err_json.py"
    payload = {
        "conversation_id": conv_id,
        "status": "ERROR",
        "response": "Tiến trình hết giờ khi đang chờ lệnh hoàn tất.",
        "usage": {"input_tokens": 321, "output_tokens": 45},
    }
    script_err.write_text(
        f"import json, sys\nprint({json.dumps(json.dumps(payload))})\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(hang_doi_git, "duong_dan_log_runner", lambda cfg: tmp_path / "runner.jsonl")
    orig_popen = subprocess.Popen
    monkeypatch.setattr(linhx_runner, "_tao_tien_trinh_agy", lambda cmd, **kw: orig_popen([sys.executable, str(script_err)], **kw))

    cfg = _tao_cfg(tmp_path, clone, tm_viec, agy_cli_dir=cli_dir)
    kq = hang_doi_git.xu_ly_mot_phieu(cfg)
    assert kq is not None
    assert kq["trang_thai"] == "dung"
    assert kq["token_vao"] == 321
    assert kq["token_ra"] == 45

    tm_kt = tmp_path / "kt-err"
    _run_git(["clone", "-b", "hang-doi", str(bare), str(tm_kt)], tmp_path)
    nd_kq = (tm_kt / "hang-doi" / "xong" / "yl-err-json" / "KET-QUA.md").read_text(encoding="utf-8")
    assert "trang_thai: dung\n" in nd_kq
    assert "ly_do: cho-nen-im-lang\n" in nd_kq

    nd_nk = (tm_kt / "hang-doi" / "xong" / "yl-err-json" / "NHAT-KY.md").read_text(encoding="utf-8")
    assert f"conversation_id: {conv_id}" in nd_nk
    assert "run_command" in nd_nk
    assert "python -m pytest -q" in nd_nk
    assert "ma_thoat: `0`" in nd_nk
    assert "2 passed in 0.12s" in nd_nk

    tep_sua = tm_kt / "hang-doi" / "moi" / "yl-err-json-sua-1.md"
    assert tep_sua.is_file()
    assert tep_sua.read_text(encoding="utf-8").count(linhx_runner.CAU_DAU_DE_SUA_CHO_NEN) == 1


def test_cho_nen_co_bo_qua_co_tat_nen_va_cau_nhac(tmp_path, monkeypatch):
    cmds: list[list[str]] = []

    class _FakeCompleted:
        def __init__(self):
            self.returncode = 0
            self.stdout = json.dumps({"status": "SUCCESS", "response": "ok"})
            self.stderr = ""

    def _fake_run(cmd, **kw):
        cmds.append(list(cmd))
        return _FakeCompleted()

    monkeypatch.setattr(subprocess, "run", _fake_run)
    monkeypatch.setattr(linhx_runner, "AGY_CO_TAT_NEN", ("--khong-chay-nen",))

    cfg = _tao_cfg(tmp_path, tmp_path, tmp_path / "viec-cho-nen")
    v_mac_dinh = hang_doi_git.phan_tich_phieu("may: may-2\nloai: kiem\n\nKiểm tra mặc định.", "mac-dinh")
    v_cho_nen = hang_doi_git.phan_tich_phieu("may: may-2\nloai: kiem\ncho_nen: co\n\nCho phép chạy nền.", "cho-nen")

    assert v_mac_dinh["cho_nen"] is False
    assert v_cho_nen["cho_nen"] is True

    linhx_runner.chay_agy(cfg, v_mac_dinh)
    linhx_runner.chay_agy(cfg, v_cho_nen)

    assert "--khong-chay-nen" in cmds[0]
    assert linhx_runner.CAU_NHAC_TIEN_CANH in cmds[0][cmds[0].index("-p") + 1]
    assert "--khong-chay-nen" not in cmds[1]
    assert linhx_runner.CAU_NHAC_TIEN_CANH not in cmds[1][cmds[1].index("-p") + 1]


def test_cho_nen_co_khong_bi_giet_khi_stderr_co_waiting_background_task(tmp_path, monkeypatch):
    script_ok = tmp_path / "agy_cho_nen_ok.py"
    payload = {"status": "SUCCESS", "response": "Hoàn tất tác vụ nền được phép.", "usage": {"input_tokens": 10, "output_tokens": 5}}
    script_ok.write_text(
        (
            "import json, sys\n"
            "print('root agent idle; waiting up to 5m0s for 1 background task(s)', file=sys.stderr, flush=True)\n"
            f"print({json.dumps(json.dumps(payload))})\n"
        ),
        encoding="utf-8",
    )
    orig_popen = subprocess.Popen
    monkeypatch.setattr(
        linhx_runner,
        "_tao_tien_trinh_agy",
        lambda cmd, **kw: orig_popen([sys.executable, str(script_ok)], **kw),
    )
    cfg = _tao_cfg(tmp_path, tmp_path, tmp_path / "viec-cho-nen-ok")
    viec = hang_doi_git.phan_tich_phieu("may: may-2\nloai: code\ncho_nen: co\n\nCho phép chạy nền hợp lệ.", "p-cn-ok")
    tt, kq, nk, tv, tr = linhx_runner.chay_agy(cfg, viec)
    assert tt == "xong"
    assert "Hoàn tất tác vụ nền được phép." in kq
    assert tv == 10 and tr == 5


def test_nhat_ky_60_buoc_cuoi_cat_200_ky_tu_3_dong_cuoi_va_loc_bi_mat(tmp_path, monkeypatch):
    # Ghep manh bi mat gia bang phep cong chuoi de khong cham bo quet tinh MAU_BI_MAT cua repo
    bi_mat_sk = "sk" + "-ant-api03-" + "BiMatAnthropic0123456789ABCDEF"
    bi_mat_gh = "gh" + "p_" + "BiMatGitHub9876543210ZyXwVuTsRqPoNm"
    bi_mat_ai = "AI" + "za" + "SyBiMatGoogleKey1234567890abcdefghij"
    bi_mat_pw = "MatKhauCucKyBiMat999"
    bi_mat_tk = "my_secret_access_token_value_888"
    bi_mat_bearer = "Bearer " + "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9_fake_payload"

    conv_id = "99999999-8888-7777-6666-555555555555"
    cli_dir = tmp_path / "agy-cli-70"
    logs_dir = cli_dir / "brain" / conv_id / ".system_generated" / "logs"
    logs_dir.mkdir(parents=True)
    transcript = logs_dir / "transcript.jsonl"

    lines: list[str] = [
        json.dumps(
            {
                "step_index": 0,
                "type": "USER_INPUT",
                "created_at": "2026-11-15T06:00:00Z",
                "content": "Chạy kiểm tra 70 bước",
            }
        )
    ]
    # Dat 1 secret o dau va 1 secret vuot ranh gioi 200 ky tu de kiem chung che TRUOC khi cat 200 ky tu
    lenh_sieu_dai = f"echo --to" + f"ken {bi_mat_tk} {'X' * 145} --api-key {bi_mat_sk} tail"
    for i in range(1, 71):
        cmd_i = lenh_sieu_dai if i == 70 else f"python step_{i}.py --key={bi_mat_sk}"
        out_i = "\n".join(
            [
                f"line 1 step {i}",
                f"line 2 github={bi_mat_gh} url=https://user:{bi_mat_pw}@example.com/hook",
                f"line 3 {bi_mat_bearer}",
                f"line 4 " + "pass" + f"word={bi_mat_pw}",
                f"line 5 gemini={bi_mat_ai}",
                f"line 6 done step {i} OK",
            ]
        )
        lines.append(
            json.dumps(
                {
                    "step_index": i,
                    "type": "PLANNER_RESPONSE",
                    "created_at": f"2026-11-15T06:{i:02d}:00Z",
                    "tool_calls": [{"name": "run_command", "args": {"CommandLine": json.dumps(cmd_i)}}],
                }
            )
        )
        lines.append(
            json.dumps(
                {
                    "step_index": i,
                    "type": "GENERIC",
                    "status": "DONE",
                    "created_at": f"2026-11-15T06:{i:02d}:01Z",
                    "content": f"Created At: c\nCompleted At: d\nCommand exited with code {i % 3}.\n\nCommand output:\n{out_i}\n",
                }
            )
        )
    transcript.write_text("\n".join(lines) + "\n", encoding="utf-8")

    bare, clone, tm_viec = _tao_kho_hang_doi(
        tmp_path,
        {"yl-nk-70": "may: may-2\nloai: code\n\nKiểm tra nhật ký 60 bước."},
    )
    script_ok = tmp_path / "agy_ok_70.py"
    payload = {
        "conversation_id": conv_id,
        "status": "SUCCESS",
        "response": "Xong 70 bước",
        "usage": {"input_tokens": 500, "output_tokens": 100},
    }
    script_ok.write_text(f"import json\nprint({json.dumps(json.dumps(payload))})\n", encoding="utf-8")

    monkeypatch.setattr(hang_doi_git, "duong_dan_log_runner", lambda cfg: tmp_path / "runner.jsonl")
    orig_popen = subprocess.Popen
    monkeypatch.setattr(
        linhx_runner,
        "_tao_tien_trinh_agy",
        lambda cmd, **kw: orig_popen([sys.executable, str(script_ok)], **kw),
    )

    cfg = _tao_cfg(tmp_path, clone, tm_viec, agy_cli_dir=cli_dir)
    kq = hang_doi_git.xu_ly_mot_phieu(cfg)
    assert kq is not None
    assert kq["trang_thai"] == "xong"

    tm_kt = tmp_path / "kt-nk"
    _run_git(["clone", "-b", "hang-doi", str(bare), str(tm_kt)], tmp_path)
    tep_nk = tm_kt / "hang-doi" / "xong" / "yl-nk-70" / "NHAT-KY.md"
    assert tep_nk.is_file()
    nd_nk = tep_nk.read_text(encoding="utf-8")

    # Dung 60 buoc cuoi: buoc 1..10 bi cat, giu buoc 11..70 (06:11:00Z .. 06:70:00Z)
    assert "- so_buoc_ghi: 60\n" in nd_nk
    assert "[2026-11-15T06:10:00Z]" not in nd_nk
    assert "[2026-11-15T06:11:00Z]" in nd_nk
    assert "[2026-11-15T06:70:00Z]" in nd_nk

    # Lenh cat <= 200 ky tu va dau ra chi lay 3 dong cuoi
    cac_dong_lenh = [d for d in nd_nk.splitlines() if d.startswith("- lenh: `")]
    assert len(cac_dong_lenh) == 60
    for dong_lenh in cac_dong_lenh:
        noi_dung_lenh = dong_lenh[len("- lenh: `") : -1]
        assert len(noi_dung_lenh) <= 200
    assert "line 3 " not in nd_nk
    assert "line 4" in nd_nk
    assert "line 5 " in nd_nk
    assert "line 6 done step 70 OK" in nd_nk

    # Loc sach moi bi mat (ke ca secret nam o ranh gioi 200 ky tu)
    assert "[DA-CHE-BI-MAT]" in nd_nk
    assert ("sk" + "-ant-") not in nd_nk
    for secret in (bi_mat_sk, bi_mat_gh, bi_mat_ai, bi_mat_pw, bi_mat_tk):
        assert secret not in nd_nk
    assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9_fake_payload" not in nd_nk

    # Kiem tra them nguon luong stream-json NDJSON
    stream_ndjson = "\n".join(
        [
            json.dumps(
                {
                    "type": "tool_use",
                    "timestamp": "2026-11-15T06:50:00Z",
                    "tool": "run_command",
                    "args": {"CommandLine": "git status --api-key " + bi_mat_sk},
                    "exit_code": 0,
                    "output": "d1\nd2\nd3\nd4 " + bi_mat_gh,
                }
            )
        ]
    )
    buoc_stream = nhat_ky_agy.trich_buoc_tu_van_ban_json(stream_ndjson)
    assert len(buoc_stream) == 1
    assert buoc_stream[0]["cong_cu"] == "run_command"
    assert ("sk" + "-ant-") not in buoc_stream[0]["lenh"]
    assert buoc_stream[0]["dau_ra_cuoi"] == ["d2", "d3", "d4 [DA-CHE-BI-MAT]"]

