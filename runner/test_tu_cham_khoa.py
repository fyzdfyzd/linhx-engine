"""Kiểm thử Vá 1: runner tự chấm máy bằng bộ khoá (.khoa + lenh_kiem) sau khi agy xong."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runner import hang_doi_git, linhx_runner  # noqa: E402
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
    # Tạo thư mục tạm cục bộ trong runner/viec (không dùng conftest, không chạm ngoài vùng)
    work_root = linhx_runner.GOC / "viec"
    existed_before = work_root.exists()
    temp_root = work_root / f"pytest-tmp-va1-{os.getpid()}-{uuid.uuid4().hex[:8]}"
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


def _setup_queue_env(tmp_path: Path, tickets: dict[str, str]) -> tuple[Path, dict]:
    # Khởi tạo bare repo nhánh hang-doi và bản clone của máy thợ cục bộ
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
    # Đọc trực tiếp nội dung `hang-doi/xong/<id>/KET-QUA.md` từ bare repo nhanh gọn
    return _run_git(["show", f"hang-doi:hang-doi/xong/{ticket_id}/KET-QUA.md"], bare_repo)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_parse_headers_lenh_kiem_and_khoa():
    # Kiểm tra phân tích header `lenh_kiem:` (giữ dấu `;`, URL `#`, cắt chú thích cuối dòng) và `khoa:`
    raw = (
        "may: may-2\n"
        "loai: code\n"
        "theo_doi: C:\\linhx\\wt-a; D:\\linhx\\wt-b\n"
        "khoa: viec/sp/nghiem-thu/test_sp.py.khoa # bộ khoá nghiệm thu\n"
        'lenh_kiem: python -c "x = 1; print(\'http://127.0.0.1/#/ok\', x)" # chạy kiểm\n\n'
        "Làm tính năng sản phẩm.\n"
    )
    parsed = hang_doi_git.phan_tich_phieu(raw, "sp-code-1")
    assert parsed["khoa"] == "viec/sp/nghiem-thu/test_sp.py.khoa"
    assert parsed["lenh_kiem"] == 'python -c "x = 1; print(\'http://127.0.0.1/#/ok\', x)"'
    assert hang_doi_git.has_verification_gate(parsed) is True

    # Không có header `khoa` / `lenh_kiem` -> rỗng và tắt cổng tự chấm như cũ
    legacy = hang_doi_git.phan_tich_phieu("may: bat-ky\n\nViệc cũ.", "cu-1")
    assert legacy["khoa"] == ""
    assert legacy["lenh_kiem"] == ""
    assert hang_doi_git.has_verification_gate(legacy) is False
    assert hang_doi_git.VERIFY_TIMEOUT_MINUTES == 15.0


def test_verify_lock_formats_single_multi_crlf_and_features_json(tmp_path):
    # Kiểm tra đủ các định dạng `.khoa`: 1 dòng sha256 (kiểu test_landing.py.khoa), CRLF/LF,
    # nhiều dòng sha256sum (kiểu DESIGN.khoa), và JSON features của `canh/cong_kiem.py`
    proj = tmp_path / "wt-proj"
    nt_dir = proj / "viec" / "demo" / "nghiem-thu"
    nt_dir.mkdir(parents=True)

    # 1. File test checkout kiểu CRLF trên Windows nhưng `.khoa` chứa sha256 bản LF của Linux
    lf_source = b"def test_mot():\n    assert 1 + 1 == 2\n"
    (nt_dir / "test_mot.py").write_bytes(lf_source.replace(b"\n", b"\r\n"))
    (nt_dir / "test_mot.py.khoa").write_text(_sha256_bytes(lf_source) + "\n", encoding="utf-8")

    # 2. File `.khoa` dạng `sha256sum` nhiều dòng (cả đường dẫn tương đối gốc lẫn tương đối cạnh `.khoa`)
    src_hai = b"def test_hai():\n    assert 'a'.upper() == 'A'\n"
    src_ba = b"def test_ba():\n    assert len([1, 2]) == 2\n"
    (nt_dir / "test_hai.py").write_bytes(src_hai)
    (nt_dir / "test_ba.py").write_bytes(src_ba)
    (proj / "test_ba.py").write_bytes(b"# file cung ten o goc nhung khong phai file trong bo.khoa\n")
    multi_khoa = (
        f"{_sha256_bytes(src_hai)}  viec/demo/nghiem-thu/test_hai.py\n"
        f"{_sha256_bytes(src_ba)} *test_ba.py\n"
    )
    (nt_dir / "bo.khoa").write_text(multi_khoa, encoding="utf-8")

    # 3. Định dạng `<features>.json.khoa` của `canh/cong_kiem.py` (cho phép đổi `passes`, chặn sửa `lenh_kiem`)
    feat_data = {
        "muc_tieu": "demo",
        "features": [{"id": "F1", "mo_ta": "mục 1", "lenh_kiem": "pytest", "passes": True, "bang_chung": "bc"}],
    }
    (proj / "features.json").write_text(json.dumps(feat_data, ensure_ascii=False), encoding="utf-8")
    feat_lock = {
        "meta": hang_doi_git._hash_json_canonical({"muc_tieu": "demo"}),
        "features": {"F1": hang_doi_git._hash_json_canonical({"id": "F1", "mo_ta": "mục 1", "lenh_kiem": "pytest"})},
    }
    (proj / "features.json.khoa").write_text(json.dumps(feat_lock), encoding="utf-8")

    ok, err = hang_doi_git.verify_lock_files(
        proj,
        [
            "viec/demo/nghiem-thu/test_mot.py.khoa",
            "viec/demo/nghiem-thu/bo.khoa",
            "features.json.khoa",
        ],
    )
    assert ok is True and err == ""

    # Nếu thợ chèn `conftest.py` không nằm trong `.khoa` -> chặn ngay "sửa test khoá"
    conftest_file = nt_dir / "conftest.py"
    conftest_file.write_text("# hook lậu\n", encoding="utf-8")
    ok_hook, err_hook = hang_doi_git.verify_lock_files(proj, ["viec/demo/nghiem-thu/test_mot.py.khoa"])
    assert ok_hook is False and "sửa test khoá" in err_hook
    conftest_file.unlink()


def test_end_to_end_gate_legacy_tamper_fail_timeout_and_pass(tmp_path):
    # Kiểm thử trọn vòng trên nhánh `hang-doi`:
    # (1) Không header -> như cũ (`xong`)
    # (2) Lệch sha256 test khoá hoặc tự sửa đè `.khoa` -> `loi` "sửa test khoá", KHÔNG chạy `lenh_kiem`
    # (3) `lenh_kiem` thoát != 0 -> `loi`, ghi trọn 1500 ký tự cuối log vào KET-QUA, sinh phiếu `-sua-1`
    # (4) Ở `-sua-1`, thợ sửa code đạt `lenh_kiem` trong thư mục `theo_doi` đầu tiên -> `xong`
    # (5) `lenh_kiem` quá trần -> `loi` kèm đuôi log vào KET-QUA
    tracked_first = tmp_path / "wt-du-an-chinh"
    tracked_second = tmp_path / "wt-phu"
    nt_dir = tracked_first / "viec" / "app" / "nghiem-thu"
    nt_dir.mkdir(parents=True)
    tracked_second.mkdir(parents=True)

    test_code = (
        "import app_mod\n"
        "def test_cong():\n"
        "    assert app_mod.cong(2, 3) == 5\n"
    ).encode("utf-8")
    test_file = nt_dir / "test_app.py"
    lock_file = nt_dir / "test_app.py.khoa"
    test_file.write_bytes(test_code)
    lock_file.write_text(_sha256_bytes(test_code) + "\n", encoding="utf-8")
    (tracked_first / "app_mod.py").write_text("def cong(a, b):\n    return 0\n", encoding="utf-8")

    py_exe = Path(sys.executable).as_posix()
    marker_ran = tmp_path / "lenh_kiem_da_chay.txt"

    tickets = {
        "01-khong-header": (
            "may: may-2\n"
            "loai: code\n\n"
            "Phiếu truyền thống không khai báo khoa hay lenh_kiem.\n"
        ),
        "02-sua-test": (
            "may: may-2\n"
            "loai: code\n"
            f"theo_doi: {tracked_first}; {tracked_second}\n"
            "khoa: viec/app/nghiem-thu/test_app.py.khoa\n"
            f'lenh_kiem: "{py_exe}" -c "import pathlib; pathlib.Path(r\'{marker_ran}\').write_text(\'ran\')"\n\n'
            "Thử gian lận sửa file test.\n"
        ),
        "03-sua-de-khoa": (
            "may: may-2\n"
            "loai: code\n"
            f"theo_doi: {tracked_first}\n"
            "khoa: viec/app/nghiem-thu/test_app.py.khoa\n"
            f'lenh_kiem: "{py_exe}" -c "raise SystemExit(0)"\n\n'
            "Thử gian lận sửa cả test lẫn file .khoa.\n"
        ),
        "04-code-sai-tu-sua": (
            "may: may-2\n"
            "loai: code\n"
            f"theo_doi: {tracked_first}; {tracked_second}\n"
            "khoa: viec/app/nghiem-thu/test_app.py.khoa\n"
            f'lenh_kiem: "{py_exe}" runner_check.py\n'
            "tu_sua: 1\n\n"
            "Sửa hàm cong(a, b) cho đúng.\n"
        ),
        "05-qua-tran": (
            "may: may-2\n"
            "loai: code\n"
            f"theo_doi: {tracked_first}\n"
            f'lenh_kiem: "{py_exe}" -c "import sys, time; sys.stdout.write(\'BAT_DAU_TREO\\n\'); sys.stdout.flush(); time.sleep(5)"\n\n'
            "Kiểm trần thời gian của lenh_kiem.\n"
        ),
    }

    # Tạo script kiểm in > 2200 ký tự khi hàm `cong(2, 3) != 5` để kiểm đúng 1500 ký tự cuối log
    tail_expected = ("FileNotFoundError_429_DONG_LOI_" * 60 + "CUOI_LOG_1500_CHUAN")[-1500:]
    assert len(tail_expected) == 1500
    (tracked_first / "runner_check.py").write_text(
        "import os, pathlib, sys\n"
        "assert os.environ.get('PYTHONSAFEPATH') == '1'\n"
        "assert pathlib.Path.cwd().name == 'wt-du-an-chinh'\n"
        "sys.path.insert(0, str(pathlib.Path.cwd()))\n"
        "import app_mod\n"
        "if app_mod.cong(2, 3) != 5:\n"
        f"    sys.stdout.write('DAU_BO_QUA_' * 90 + {tail_expected!r})\n"
        "    sys.exit(1)\n"
        "print('TAT_CA_XANH')\n",
        encoding="utf-8",
    )

    bare_repo, cfg = _setup_queue_env(tmp_path, tickets)

    # --- (1) Không có header -> giữ nguyên hành vi cũ (`xong`) ---
    res_1 = hang_doi_git.xu_ly_mot_phieu(cfg, chay_agy_fn=lambda _c, _v: ("xong", "Xong việc cũ.", "exit=0", 5, 5))
    assert res_1["viec"] == "01-khong-header"
    assert res_1["trang_thai"] == "xong"
    assert "trang_thai: xong" in _read_ket_qua_from_bare(bare_repo, "01-khong-header")

    # --- (2) Thợ sửa file test -> `loi` "sửa test khoá", không được phép chạy `lenh_kiem` ---
    def _agy_sua_test(_c, _v):
        test_file.write_bytes(b"def test_cong():\n    assert True\n")
        return "xong", "Báo cáo giả đã xanh.", "exit=0", 10, 10

    res_2 = hang_doi_git.xu_ly_mot_phieu(cfg, chay_agy_fn=_agy_sua_test)
    assert res_2["viec"] == "02-sua-test"
    assert res_2["trang_thai"] == "loi"
    assert not marker_ran.exists(), "Lệch .khoa thì không được chạy lenh_kiem"
    kq_2 = _read_ket_qua_from_bare(bare_repo, "02-sua-test")
    assert "trang_thai: loi" in kq_2
    assert "sửa test khoá" in kq_2
    test_file.write_bytes(test_code)

    # --- (3) Thợ sửa cả test lẫn ghi đè luôn `.khoa` -> vẫn bị snapshot chặn `loi` "sửa test khoá" ---
    def _agy_sua_ca_khoa(_c, _v):
        fake_bytes = b"def test_cong():\n    pass\n"
        test_file.write_bytes(fake_bytes)
        lock_file.write_text(_sha256_bytes(fake_bytes) + "\n", encoding="utf-8")
        return "xong", "Đã cập nhật luôn khoá.", "exit=0", 8, 8

    res_3 = hang_doi_git.xu_ly_mot_phieu(cfg, chay_agy_fn=_agy_sua_ca_khoa)
    assert res_3["viec"] == "03-sua-de-khoa"
    assert res_3["trang_thai"] == "loi"
    kq_3 = _read_ket_qua_from_bare(bare_repo, "03-sua-de-khoa")
    assert "trang_thai: loi" in kq_3
    assert "sửa test khoá" in kq_3
    test_file.write_bytes(test_code)
    lock_file.write_text(_sha256_bytes(test_code) + "\n", encoding="utf-8")

    # --- (4a) Thợ báo xong nhưng chưa sửa đúng code -> `lenh_kiem` exit=1 -> `loi` + 1500 ký tự cuối log ---
    def _agy_code_sai(c, _v):
        for idx in range(12):
            (Path(c["thu_muc"]) / f"tep_phu_dai_kiem_tra_{idx:02d}.txt").write_text("x\n", encoding="utf-8")
        return "xong", "Tưởng đã xong.", "exit=0", 12, 15

    res_4 = hang_doi_git.xu_ly_mot_phieu(cfg, chay_agy_fn=_agy_code_sai)
    assert res_4["viec"] == "04-code-sai-tu-sua"
    assert res_4["trang_thai"] == "loi"
    kq_4 = _read_ket_qua_from_bare(bare_repo, "04-code-sai-tu-sua")
    assert "trang_thai: loi" in kq_4
    assert tail_expected in kq_4
    assert "DAU_BO_QUA_" not in kq_4

    # --- (4b) Phiếu tự sửa `04-code-sai-tu-sua-sua-1` được sinh tự động, thợ sửa đúng code -> `xong`! ---
    def _agy_sua_dung(_c, v):
        assert v["viec"] == "04-code-sai-tu-sua-sua-1"
        assert "CUOI_LOG_1500_CHUAN" in v["de"]
        (tracked_first / "app_mod.py").write_text("def cong(a, b):\n    return a + b\n", encoding="utf-8")
        return "xong", "Đã sửa hàm cong(a, b) trả về a + b.", "exit=0", 20, 25

    res_4_sua = hang_doi_git.xu_ly_mot_phieu(cfg, chay_agy_fn=_agy_sua_dung)
    assert res_4_sua["viec"] == "04-code-sai-tu-sua-sua-1"
    assert res_4_sua["trang_thai"] == "xong"
    kq_4_sua = _read_ket_qua_from_bare(bare_repo, "04-code-sai-tu-sua-sua-1")
    assert "trang_thai: xong" in kq_4_sua
    assert "Đã sửa hàm cong(a, b)" in kq_4_sua

    # --- (5) `lenh_kiem` chạy quá trần (giả lập trần ngắn qua `tran_kiem_phut`) -> diệt tiến trình & `loi` ---
    cfg_short_timeout = {**cfg, "tran_kiem_phut": 0.005}  # ~0.3 giây
    res_5 = hang_doi_git.xu_ly_mot_phieu(
        cfg_short_timeout,
        chay_agy_fn=lambda _c, _v: ("xong", "Xong code.", "exit=0", 3, 3),
    )
    assert res_5["viec"] == "05-qua-tran"
    assert res_5["trang_thai"] == "loi"
    kq_5 = _read_ket_qua_from_bare(bare_repo, "05-qua-tran")
    assert "trang_thai: loi" in kq_5
    assert "quá trần" in kq_5
    assert "BAT_DAU_TREO" in kq_5


def test_real_lvn_landing_khoa_and_skip_when_agy_failed(tmp_path):
    # Đối chiếu trực tiếp file `.khoa` thật trong repo (nếu có) và đảm bảo không chạy `lenh_kiem` khi agy đã `dung`/`loi`
    repo_root = linhx_runner.GOC.parent
    real_khoa = repo_root / "viec" / "lvn-landing" / "nghiem-thu" / "test_landing.py.khoa"
    if real_khoa.is_file():
        ok, err = hang_doi_git.verify_lock_files(
            repo_root,
            ["viec/lvn-landing/nghiem-thu/test_landing.py.khoa"],
        )
        assert ok is True, err

    # Khi agy trả `dung` (hoặc `loi`), `thuc_thi_phieu_da_nhan` giữ nguyên `dung` chứ không chạy `lenh_kiem`
    flag_file = tmp_path / "khong_duoc_chay.txt"
    py_exe = Path(sys.executable).as_posix()
    bare_repo, cfg = _setup_queue_env(
        tmp_path,
        {
            "01-agy-dung": (
                "may: may-2\n"
                "loai: code\n"
                f"theo_doi: {tmp_path}\n"
                f'lenh_kiem: "{py_exe}" -c "import pathlib; pathlib.Path(r\'{flag_file}\').write_text(\'1\')"\n\n'
                "Phiếu bị bộ canh dừng giữa chừng.\n"
            )
        },
    )
    res = hang_doi_git.xu_ly_mot_phieu(cfg, chay_agy_fn=lambda _c, _v: ("dung", None, "dừng agy: quá 20 phút", 0, 0))
    assert res["trang_thai"] == "dung"
    assert not flag_file.exists()
    assert "trang_thai: dung" in _read_ket_qua_from_bare(bare_repo, "01-agy-dung")

