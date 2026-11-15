from __future__ import annotations

import os
import shlex
import shutil
import stat
import subprocess
import uuid
from pathlib import Path

import pytest

from runner import hang_doi_git, linhx_runner
from runner._gia_moi_truong import _gia_ram_va_moi_truong_h3  # noqa: F401  (fixture autouse, thay conftest)
from runner.bang import bang


def _remove_tree(target_dir: Path) -> None:
    # Xoá thư mục tạm an toàn kể cả các file chỉ đọc trong .git trên Windows
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
    # Dựng thư mục tạm ngay trong runner/viec để chạy độc lập không cần mạng hay conftest
    work_root = linhx_runner.GOC / "viec"
    existed_before = work_root.exists()
    temp_root = work_root / f"pytest-tmp-va5-{os.getpid()}-{uuid.uuid4().hex[:8]}"
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
    # Chạy git tiền cảnh, khoá lời nhắc đăng nhập để test chạy thuần cục bộ
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


def _create_bare_queue_repo(
    tmp_path: Path,
    initial_tickets: dict[str, str],
    finished_results: dict[str, str] | None = None,
) -> Path:
    # Dựng bare repo cục bộ gồm nhánh main và nhánh hang-doi
    bare_repo = tmp_path / f"remote-{uuid.uuid4().hex[:6]}.git"
    bare_repo.mkdir(parents=True)
    _run_git(["init", "--bare"], bare_repo)

    seed_repo = tmp_path / f"seed-{uuid.uuid4().hex[:6]}"
    seed_repo.mkdir()
    _run_git(["init"], seed_repo)
    _run_git(["config", "user.name", "seed"], seed_repo)
    _run_git(["config", "user.email", "seed@linhx.local"], seed_repo)
    _run_git(["config", "commit.gpgsign", "false"], seed_repo)

    _run_git(["checkout", "-b", "main"], seed_repo)
    (seed_repo / "README.md").write_text("linhx-engine\n", encoding="utf-8")
    _run_git(["add", "-A"], seed_repo)
    _run_git(["commit", "-m", "init main"], seed_repo)
    _run_git(["remote", "add", "origin", str(bare_repo)], seed_repo)
    _run_git(["push", "origin", "main"], seed_repo)
    _run_git(["symbolic-ref", "HEAD", "refs/heads/main"], bare_repo)

    _run_git(["checkout", "--orphan", "hang-doi"], seed_repo)
    _run_git(["rm", "-rf", "."], seed_repo)
    moi_dir = seed_repo / "hang-doi" / "moi"
    moi_dir.mkdir(parents=True, exist_ok=True)
    (moi_dir / ".gitkeep").write_text("", encoding="utf-8")
    for ticket_id, content in initial_tickets.items():
        (moi_dir / f"{ticket_id}.md").write_text(content, encoding="utf-8")
    for done_id, result_md in (finished_results or {}).items():
        done_file = seed_repo / "hang-doi" / "xong" / done_id / "KET-QUA.md"
        done_file.parent.mkdir(parents=True, exist_ok=True)
        done_file.write_text(result_md, encoding="utf-8")

    _run_git(["add", "-A"], seed_repo)
    _run_git(["commit", "-m", "init hang-doi"], seed_repo)
    _run_git(["push", "origin", "hang-doi"], seed_repo)
    return bare_repo


def _create_project_repo(tmp_path: Path, name: str = "wt-du-an") -> tuple[Path, str]:
    # Tạo một git repo dự án riêng đóng vai trò thư mục `theo_doi`
    proj_dir = tmp_path / name
    proj_dir.mkdir(parents=True, exist_ok=True)
    _run_git(["init"], proj_dir)
    _run_git(["config", "user.name", "dev"], proj_dir)
    _run_git(["config", "user.email", "dev@linhx.local"], proj_dir)
    _run_git(["config", "commit.gpgsign", "false"], proj_dir)
    (proj_dir / "thue.py").write_text("def tinh_thue(thu_nhap: int) -> int:\n    return 0\n", encoding="utf-8")
    _run_git(["add", "-A"], proj_dir)
    _run_git(["commit", "-m", "moc goc"], proj_dir)
    sha0 = _run_git(["rev-parse", "HEAD"], proj_dir)
    return proj_dir, sha0


def _clone_worker_cfg(bare_repo: Path, tmp_path: Path, worker_name: str, **extra_cfg) -> dict:
    # Tạo clone hàng đợi và cấu hình runner riêng cho từng máy thợ
    clone_dir = tmp_path / f"clone-{worker_name}-{uuid.uuid4().hex[:4]}"
    _run_git(["clone", str(bare_repo), str(clone_dir)], tmp_path)
    work_dir = tmp_path / f"work-{worker_name}"
    work_dir.mkdir(parents=True, exist_ok=True)
    cfg = {
        "nguon": "github",
        "tho": worker_name,
        "agy": "agy-gia",
        "agy_args": "--output-format json",
        "thu_muc": work_dir,
        "nghi": 0.01,
        "repo_hang_doi": clone_dir,
        "nhanh_hang_doi": "hang-doi",
        "remote_hang_doi": "origin",
        "wt_hang_doi": "",
        "thu_muc_drive": tmp_path / f"drive-{worker_name}",
        "thu_muc_log": tmp_path / f"log-{worker_name}",
    }
    cfg.update(extra_cfg)
    return cfg


def _inspect_queue_branch(bare_repo: Path, tmp_path: Path, label: str = "inspect") -> Path:
    # Kéo nhánh hang-doi ra thư mục kiểm chứng độc lập
    inspect_dir = tmp_path / label
    if inspect_dir.exists():
        _run_git(["fetch", "origin", "hang-doi"], inspect_dir)
        _run_git(["reset", "--hard", "origin/hang-doi"], inspect_dir)
    else:
        _run_git(["clone", "-b", "hang-doi", str(bare_repo), str(inspect_dir)], tmp_path)
    return inspect_dir


def test_moc_head_recorded_in_dang_allows_revert(tmp_path):
    # Vá 5(a): khi nhận phiếu phải ghi `moc: <sha HEAD>` vào `dang/<id>.md` để hoàn tác được khi cần
    proj_dir, sha_goc = _create_project_repo(tmp_path, "wt-moc")
    bare_repo = _create_bare_queue_repo(
        tmp_path,
        initial_tickets={
            "01-thu-moc": (
                f"may: may-2\n"
                f"loai: code\n"
                f"theo_doi: {proj_dir}\n\n"
                "Cập nhật hàm tính thuế."
            )
        },
    )
    cfg = _clone_worker_cfg(bare_repo, tmp_path, "may-2")

    claimed = hang_doi_git.nhan_phieu_git(cfg)
    assert claimed is not None
    assert claimed["moc"] == sha_goc

    inspect_dang = _inspect_queue_branch(bare_repo, tmp_path, "kt-dang-moc")
    dang_file = inspect_dang / "hang-doi" / "dang" / "01-thu-moc.md"
    assert dang_file.is_file()
    dang_text = dang_file.read_text(encoding="utf-8")
    assert f"moc: {sha_goc}" in dang_text
    parsed_dang = hang_doi_git.phan_tich_phieu(dang_text, "01-thu-moc")
    assert parsed_dang["moc"] == sha_goc

    # Giả lập thợ commit bản lỗi làm tụt điểm rồi dùng `moc` từ dang/<id>.md để hoàn tác sạch
    (proj_dir / "thue.py").write_text("def tinh_thue(thu_nhap: int) -> int:\n    return -999\n", encoding="utf-8")
    _run_git(["add", "-A"], proj_dir)
    _run_git(["commit", "-m", "commit lam tut diem"], proj_dir)
    assert _run_git(["rev-parse", "HEAD"], proj_dir) != sha_goc

    _run_git(["reset", "--hard", parsed_dang["moc"]], proj_dir)
    assert _run_git(["rev-parse", "HEAD"], proj_dir) == sha_goc
    assert "return 0" in (proj_dir / "thue.py").read_text(encoding="utf-8")


def test_cham_1_spawns_clean_eye_review_ticket_with_diff_and_no_worker_excuse(tmp_path, monkeypatch):
    # Vá 5(a): `cham: 1` khi `xong` tự tạo `hang-doi/moi/<id>-cham.md` (loai: cham, cùng may, theo_doi)
    # kèm câu nhắc mắt mới, đề gốc sạch (không lộ lý do thợ / lịch sử trượt) và lệnh xem diff chạy được.
    proj_dir, sha_ban_dau = _create_project_repo(tmp_path, "wt-thue")
    de_goc = (
        "Viết hàm `tinh_thue(thu_nhap)` theo 2 bậc:\n"
        "- Dưới 10_000_000 trả 0.\n"
        "- Phần vượt 10_000_000 nhân 10%."
    )
    bare_repo = _create_bare_queue_repo(
        tmp_path,
        initial_tickets={
            "thue-code-bac1": (
                f"may: may-2\n"
                f"loai: code\n"
                f"tran_phut: 20\n"
                f"theo_doi: {proj_dir}\n"
                f"tu_sua: 1\n"
                f"cham: 1\n\n"
                f"{de_goc}\n"
            ),
            "phu-khong-cham": (
                f"may: may-2\n"
                f"loai: code\n"
                f"theo_doi: {proj_dir}\n\n"
                "Phiếu thường không bật cờ chấm."
            ),
        },
    )
    cfg = _clone_worker_cfg(bare_repo, tmp_path, "may-2")
    sha_truoc_sua_1: list[str] = []

    def fake_agy(worker_cfg, job):
        vid = job["viec"]
        if vid == "phu-khong-cham":
            return "xong", "Xong phiếu không có cờ chấm", "exit=0", 10, 5
        if vid == "thue-code-bac1":
            return "loi", "LY_DO_BAO_CHUA_LAN_1_KHONG_DUOC_LO", "exit=1", 20, 10
        if vid == "thue-code-bac1-sua-1":
            sha_truoc_sua_1.append(_run_git(["rev-parse", "HEAD"], proj_dir))
            (proj_dir / "thue.py").write_text(
                "def tinh_thue(thu_nhap: int) -> int:\n"
                "    return max(0, (thu_nhap - 10_000_000) // 10)\n",
                encoding="utf-8",
            )
            _run_git(["add", "-A"], proj_dir)
            _run_git(["commit", "-m", "cai dat tinh_thue"], proj_dir)
            return "xong", "LY_DO_THO_TU_KHEN_99_DIEM_CAM_XEM", "exit=0", 40, 20
        if vid == "thue-code-bac1-sua-1-cham":
            return "xong", "Đạt 10/10 tất cả tiêu chí.", "exit=0", 30, 15
        raise AssertionError(f"Phiếu lạ không mong đợi: {vid}")

    monkeypatch.setattr(hang_doi_git, "chay_agy", fake_agy)

    # 1. `phu-khong-cham` xong nhưng không có `cham: 1` -> không tạo `*-cham.md`
    r0 = hang_doi_git.xu_ly_mot_phieu(cfg)
    assert r0 is not None and r0["viec"] == "phu-khong-cham" and r0["trang_thai"] == "xong"
    ins0 = _inspect_queue_branch(bare_repo, tmp_path, "kt-cham-0")
    assert not (ins0 / "hang-doi" / "moi" / "phu-khong-cham-cham.md").exists()

    # 2. `thue-code-bac1` trượt (`loi`) -> chỉ tạo `-sua-1`, KHÔNG tạo `-cham.md` khi chưa xong
    r1 = hang_doi_git.xu_ly_mot_phieu(cfg)
    assert r1 is not None and r1["viec"] == "thue-code-bac1" and r1["trang_thai"] == "loi"
    ins1 = _inspect_queue_branch(bare_repo, tmp_path, "kt-cham-1")
    assert not (ins1 / "hang-doi" / "moi" / "thue-code-bac1-cham.md").exists()
    assert (ins1 / "hang-doi" / "moi" / "thue-code-bac1-sua-1.md").is_file()

    # 3. `thue-code-bac1-sua-1` hoàn tất `xong` -> tự tạo `thue-code-bac1-sua-1-cham.md` cùng commit KET-QUA
    r2 = hang_doi_git.xu_ly_mot_phieu(cfg)
    assert r2 is not None and r2["viec"] == "thue-code-bac1-sua-1" and r2["trang_thai"] == "xong"
    ins2 = _inspect_queue_branch(bare_repo, tmp_path, "kt-cham-2")
    cham_file = ins2 / "hang-doi" / "moi" / "thue-code-bac1-sua-1-cham.md"
    assert cham_file.is_file()

    cham_raw = cham_file.read_text(encoding="utf-8")
    parsed_cham = hang_doi_git.phan_tich_phieu(cham_raw, "thue-code-bac1-sua-1-cham")
    assert parsed_cham["loai"] == "cham"
    assert parsed_cham["may"] == "may-2"
    assert parsed_cham["meta"]["theo_doi"] == str(proj_dir)
    assert parsed_cham["cham"] is False

    expected_prompt = (
        "Bạn là người chấm mắt mới, KHÔNG xem lý do của thợ. "
        "Đọc đề gốc + diff, chấm từng tiêu chí đạt/không, điểm /10, ngưỡng 9; "
        "dưới ngưỡng ghi lỗi file:dòng."
    )
    assert parsed_cham["de"].startswith(expected_prompt)
    assert de_goc in parsed_cham["de"]
    assert "LY_DO_THO_TU_KHEN_99_DIEM_CAM_XEM" not in cham_raw
    assert "LY_DO_BAO_CHUA_LAN_1_KHONG_DUOC_LO" not in cham_raw
    assert "Lần trước trượt vì:" not in cham_raw

    # Lệnh xem diff trong phiếu chấm phải trỏ đúng mốc `sha_ban_dau..HEAD` và chạy ra diff thật
    assert sha_truoc_sua_1 == [sha_ban_dau]
    diff_lines = [
        line.strip("` ").strip()
        for line in parsed_cham["de"].splitlines()
        if line.strip("` ").strip().startswith("git ")
    ]
    assert len(diff_lines) == 1
    diff_cmd = diff_lines[0]
    assert f"{sha_ban_dau}..HEAD" in diff_cmd
    diff_args = shlex.split(diff_cmd, posix=os.name != "nt")
    if os.name == "nt":
        diff_args = [a[1:-1] if len(a) >= 2 and a[0] == a[-1] and a[0] in ('"', "'") else a for a in diff_args]
    diff_out = _run_git(diff_args[1:], tmp_path)
    assert "+    return max(0, (thu_nhap - 10_000_000) // 10)" in diff_out

    # 4. Bản thân phiếu `loai: cham` khi chạy xong không sinh tiếp `*-cham-cham.md`
    r3 = hang_doi_git.xu_ly_mot_phieu(cfg)
    assert r3 is not None and r3["viec"] == "thue-code-bac1-sua-1-cham" and r3["trang_thai"] == "xong"
    assert hang_doi_git.xu_ly_mot_phieu(cfg) is None
    ins3 = _inspect_queue_branch(bare_repo, tmp_path, "kt-cham-3")
    assert list((ins3 / "hang-doi" / "moi").glob("*.md")) == []


def test_dependency_waits_while_tu_sua_remaining_and_runs_if_repaired(tmp_path, monkeypatch):
    # Vá 5(b): khi phiếu cha trượt nhưng còn `tu_sua`, phiếu con KHÔNG bị huỷ sớm;
    # nếu lượt `-sua-1` đạt `xong` thì phiếu con được nhận và chạy bình thường.
    bare_repo = _create_bare_queue_repo(
        tmp_path,
        initial_tickets={
            "01-cha": "may: may-1\nloai: code\ntu_sua: 2\n\nBước cha có tự sửa.",
            "02-con": "may: may-1\nloai: code\nphu_thuoc: 01-cha\n\nBước con chờ bước cha.",
        },
    )
    cfg = _clone_worker_cfg(bare_repo, tmp_path, "may-1")
    ran: list[str] = []

    def fake_agy(worker_cfg, job):
        ran.append(job["viec"])
        if job["viec"] == "01-cha":
            return "loi", "Trượt lượt đầu", "exit=1", 10, 5
        return "xong", f"Đạt ở {job['viec']}", "exit=0", 15, 8

    monkeypatch.setattr(hang_doi_git, "chay_agy", fake_agy)

    # Lượt 1: `01-cha` trượt -> sinh `01-cha-sua-1`; `02-con` vẫn chờ trong `moi/`
    res1 = hang_doi_git.xu_ly_mot_phieu(cfg)
    assert res1 is not None and res1["viec"] == "01-cha" and res1["trang_thai"] == "loi"
    ins1 = _inspect_queue_branch(bare_repo, tmp_path, "kt-cho-sua-1")
    assert (ins1 / "hang-doi" / "moi" / "02-con.md").is_file()
    assert not (ins1 / "hang-doi" / "xong" / "02-con").exists()

    # Lượt 2 & 3: `01-cha-sua-1` đạt `xong` -> `02-con` mở khoá và chạy `xong`
    hang_doi_git.vong_git(cfg, mot_lan=True)
    assert ran == ["01-cha", "01-cha-sua-1", "02-con"]
    ins2 = _inspect_queue_branch(bare_repo, tmp_path, "kt-cho-sua-2")
    kq_con = (ins2 / "hang-doi" / "xong" / "02-con" / "KET-QUA.md").read_text(encoding="utf-8")
    assert "trang_thai: xong" in kq_con


def test_dependency_cascade_cancel_after_tu_sua_exhausted_and_board_status(tmp_path, monkeypatch):
    # Vá 5(b): khi phiếu cha kết thúc `loi`/`dung` và đã hết `tu_sua`, toàn bộ dây chuyền phụ thuộc
    # chuyển sang `xong/<id>/KET-QUA.md` trạng thái `huy` lý do "phụ thuộc trượt", không treo mãi ở `moi/`.
    bare_repo = _create_bare_queue_repo(
        tmp_path,
        initial_tickets={
            "01-goc": "may: may-1\nloai: code\ntu_sua: 1\n\nPhiếu gốc trượt hết lượt.",
            "02-tang-1": "may: may-2\nloai: code\nphu_thuoc: 01-goc\n\nPhụ thuộc trực tiếp.",
            "03-tang-2": "may: bat-ky\nloai: code\nphu_thuoc: 02-tang-1\n\nPhụ thuộc bắc cầu.",
        },
    )
    cfg = _clone_worker_cfg(bare_repo, tmp_path, "may-1")
    ran: list[str] = []

    def fake_agy(worker_cfg, job):
        ran.append(job["viec"])
        if job["viec"] == "01-goc":
            return "dung", None, "dừng agy: quá 20 phút không tiến", 0, 0
        return "loi", "Trượt nốt lượt sửa cuối", "exit=1", 12, 4

    monkeypatch.setattr(hang_doi_git, "chay_agy", fake_agy)

    # Lượt 1: còn `01-goc-sua-1` nên chưa huỷ `02-tang-1` và `03-tang-2`
    r1 = hang_doi_git.xu_ly_mot_phieu(cfg)
    assert r1 is not None and r1["viec"] == "01-goc" and r1["trang_thai"] == "dung"
    ins_mid = _inspect_queue_branch(bare_repo, tmp_path, "kt-huy-mid")
    assert (ins_mid / "hang-doi" / "moi" / "02-tang-1.md").is_file()
    assert (ins_mid / "hang-doi" / "moi" / "03-tang-2.md").is_file()

    # Lượt 2: `01-goc-sua-1` hết `tu_sua` và trượt -> huỷ dây chuyền cả `02-tang-1` lẫn `03-tang-2`
    r2 = hang_doi_git.xu_ly_mot_phieu(cfg)
    assert r2 is not None and r2["viec"] == "01-goc-sua-1" and r2["trang_thai"] == "loi"
    assert ran == ["01-goc", "01-goc-sua-1"]

    ins_done = _inspect_queue_branch(bare_repo, tmp_path, "kt-huy-done")
    assert list((ins_done / "hang-doi" / "moi").glob("*.md")) == []
    for cancelled_id in ("02-tang-1", "03-tang-2"):
        kq_path = ins_done / "hang-doi" / "xong" / cancelled_id / "KET-QUA.md"
        assert kq_path.is_file()
        kq_text = kq_path.read_text(encoding="utf-8")
        assert "trang_thai: huy" in kq_text
        assert "phụ thuộc trượt" in kq_text

    # Bảng theo dõi đọc đúng trạng thái `huy` mà không biến thành `loi`
    snap = bang.read_queue_snapshot(ins_done)
    by_id = {item["phieu"]: item for item in snap["xong_gan_nhat"]}
    assert by_id["02-tang-1"]["trang_thai"] == "huy"
    assert "phụ thuộc trượt" in by_id["02-tang-1"]["ly_do_ngan"]
    assert by_id["03-tang-2"]["trang_thai"] == "huy"

    # Trường hợp đẩy thêm một phiếu mới vào `moi/` phụ thuộc vào phiếu đã trượt từ trước -> `nhan_phieu_git` tự huỷ ngay
    (ins_done / "hang-doi" / "moi" / "04-vao-muon.md").write_text(
        "may: may-1\nloai: code\nphu_thuoc: 01-goc\n\nVào sau khi cha đã trượt.",
        encoding="utf-8",
    )
    _run_git(["config", "user.name", "pusher"], ins_done)
    _run_git(["config", "user.email", "pusher@linhx.local"], ins_done)
    _run_git(["config", "commit.gpgsign", "false"], ins_done)
    _run_git(["add", "-A"], ins_done)
    _run_git(["commit", "-m", "them 04-vao-muon"], ins_done)
    _run_git(["push", "origin", "hang-doi"], ins_done)

    assert hang_doi_git.nhan_phieu_git(cfg) is None
    ins_late = _inspect_queue_branch(bare_repo, tmp_path, "kt-huy-late")
    assert not (ins_late / "hang-doi" / "moi" / "04-vao-muon.md").exists()
    kq_late = (ins_late / "hang-doi" / "xong" / "04-vao-muon" / "KET-QUA.md").read_text(encoding="utf-8")
    assert "trang_thai: huy" in kq_late
    assert "phụ thuộc trượt" in kq_late


def test_quota_429_writes_flag_pauses_30_minutes_and_resumes_after_expiry(tmp_path, monkeypatch):
    # Vá 5(c): khi agy trả 429 / hết hạn mức -> máy ghi file cờ tạm nghỉ 30 phút, không nhận phiếu mới;
    # máy khác vẫn nhận việc bình thường; sau 30 phút máy tự xoá cờ và nhận phiếu trở lại.
    bare_repo = _create_bare_queue_repo(
        tmp_path,
        initial_tickets={
            "01-dinh-quota": "may: may-1\nloai: code\n\nPhiếu gặp 429 hết hạn mức.",
            "02-doi-mo-lai": "may: may-1\nloai: code\n\nPhiếu tiếp theo của may-1.",
            "03-may-khac": "may: may-2\nloai: code\n\nPhiếu của may-2 không bị ảnh hưởng.",
        },
    )
    cfg_1 = _clone_worker_cfg(bare_repo, tmp_path, "may-1")
    cfg_2 = _clone_worker_cfg(bare_repo, tmp_path, "may-2")

    fake_clock = [1_700_000_000.0]
    monkeypatch.setattr(hang_doi_git.time, "time", lambda: fake_clock[0])

    def fake_agy(worker_cfg, job):
        if job["viec"] == "01-dinh-quota":
            return (
                "loi",
                "Lỗi 429 RESOURCE_EXHAUSTED: hết hạn mức gói hiện tại",
                "exit=1 giay=2\n--- stderr ---\nHTTP 429 quota exceeded",
                0,
                0,
            )
        return "xong", f"Hoàn thành {job['viec']}", "exit=0", 25, 10

    monkeypatch.setattr(hang_doi_git, "chay_agy", fake_agy)

    # 1. `may-1` chạy `01-dinh-quota` gặp 429 -> ghi file cờ tạm nghỉ 30 phút (1800 giây)
    res_q = hang_doi_git.xu_ly_mot_phieu(cfg_1)
    assert res_q is not None and res_q["viec"] == "01-dinh-quota" and res_q["trang_thai"] == "loi"
    flag_path = hang_doi_git.duong_dan_co_tam_nghi_quota(cfg_1)
    assert flag_path.is_file()
    paused, rem_min = hang_doi_git.dang_tam_nghi_quota(cfg_1)
    assert paused is True
    assert 29.9 <= rem_min <= 30.0

    # 2. Trong suốt 30 phút tạm nghỉ (phút thứ 10 và 29p59s), `may-1` từ chối nhận `02-doi-mo-lai`
    fake_clock[0] += 600.0
    assert hang_doi_git.nhan_phieu_git(cfg_1) is None

    # Trong lúc đó `may-2` hoàn toàn không bị chặn, nhận và làm xong `03-may-khac`
    res_m2 = hang_doi_git.xu_ly_mot_phieu(cfg_2)
    assert res_m2 is not None and res_m2["viec"] == "03-may-khac" and res_m2["trang_thai"] == "xong"

    fake_clock[0] = 1_700_000_000.0 + 1799.0
    assert hang_doi_git.nhan_phieu_git(cfg_1) is None
    assert flag_path.is_file()

    # 3. Đúng sau mốc 30 phút (+1801s), cờ hết hạn tự xoá và `may-1` nhận `02-doi-mo-lai` chạy `xong`
    fake_clock[0] = 1_700_000_000.0 + 1801.0
    res_resume = hang_doi_git.xu_ly_mot_phieu(cfg_1)
    assert res_resume is not None and res_resume["viec"] == "02-doi-mo-lai" and res_resume["trang_thai"] == "xong"
    assert not flag_path.exists()
