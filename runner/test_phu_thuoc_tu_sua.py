from __future__ import annotations

import os
import shutil
import stat
import subprocess
import uuid
from pathlib import Path

import pytest

from runner import hang_doi_git, linhx_runner
from runner._gia_moi_truong import _gia_ram_va_moi_truong_h3  # noqa: F401  (fixture autouse, thay conftest)


def _remove_tree(target_dir: Path) -> None:
    # Xoá thư mục tạm an toàn kể cả file read-only trong .git trên Windows
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
    # Tạo thư mục tạm cục bộ trong runner/viec để không phụ thuộc ổ hệ thống ngoài vùng
    work_root = linhx_runner.GOC / "viec"
    existed_before = work_root.exists()
    temp_root = work_root / f"pytest-tmp-ptts-{os.getpid()}-{uuid.uuid4().hex[:8]}"
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
    # Chạy git cục bộ tiền cảnh, tắt toàn bộ hộp thoại hỏi mật khẩu
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
    # Dựng bare repo cục bộ có nhánh main và nhánh hang-doi (không gọi mạng)
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


def _clone_worker_cfg(bare_repo: Path, tmp_path: Path, worker_name: str, **extra_cfg) -> dict:
    # Tạo bản clone cho một máy thợ và trả về cấu hình runner tương ứng
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
    # Đồng bộ nhánh hang-doi từ bare repo ra thư mục kiểm tra kết quả
    inspect_dir = tmp_path / label
    if inspect_dir.exists():
        _run_git(["fetch", "origin", "hang-doi"], inspect_dir)
        _run_git(["reset", "--hard", "origin/hang-doi"], inspect_dir)
    else:
        _run_git(["clone", "-b", "hang-doi", str(bare_repo), str(inspect_dir)], tmp_path)
    return inspect_dir


def test_parse_headers_phu_thuoc_and_tu_sua():
    # Kiểm tra phân tích header phu_thuoc, tu_sua (mặc định 0, trần tối đa 3) và theo_doi nhiều ổ đĩa
    raw_ticket = (
        "may: may-2\n"
        "loai: code\n"
        "theo_doi: C:\\linhx\\wt-a; D:\\linhx\\wt-b\n"
        "phu_thuoc: id1; id2 # chờ 2 phiếu trước\n"
        "tu_sua: 5 # vượt trần thì kẹp về 3\n\n"
        "Đề bài kiểm thử.\n"
    )
    parsed = hang_doi_git.phan_tich_phieu(raw_ticket, "p-kiem")
    assert parsed["may"] == "may-2"
    assert parsed["phu_thuoc"] == ["id1", "id2"]
    assert parsed["tu_sua"] == 3
    assert parsed["meta"]["theo_doi"] == r"C:\linhx\wt-a; D:\linhx\wt-b"
    assert parsed["de"] == "Đề bài kiểm thử."

    # Phiếu không khai báo phu_thuoc / tu_sua -> mặc định rỗng và 0
    plain = hang_doi_git.phan_tich_phieu("may: bat-ky\n\nChạy như cũ.", "p-cu")
    assert plain["phu_thuoc"] == []
    assert plain["tu_sua"] == 0

    # Giá trị âm hoặc sai định dạng -> về 0
    assert hang_doi_git.parse_self_repair_count("-2") == 0
    assert hang_doi_git.parse_self_repair_count("khong-hop-le") == 0
    assert hang_doi_git.parse_self_repair_count(None) == 0


def test_dependencies_claim_in_order_only_when_all_done(tmp_path, monkeypatch):
    # A. Phiếu có phu_thuoc: id1; id2 chỉ được nhận sau khi CẢ id1 và id2 có KET-QUA.md trang_thai: xong;
    # phiếu không có phu_thuoc vẫn chạy bình thường như cũ.
    bare_repo = _create_bare_queue_repo(
        tmp_path,
        initial_tickets={
            "01-tong-hop": (
                "may: may-1\n"
                "loai: code\n"
                "phu_thuoc: 02-buoc-a; 03-buoc-b\n\n"
                "Tổng hợp kết quả của bước A và bước B."
            ),
            "02-buoc-a": "may: may-1\nloai: code\n\nChạy bước A.",
            "03-buoc-b": "may: bat-ky\nloai: code\n\nChạy bước B.",
        },
    )
    cfg = _clone_worker_cfg(bare_repo, tmp_path, "may-1")
    execution_order: list[str] = []

    def fake_agy(worker_cfg, job):
        execution_order.append(job["viec"])
        return "xong", f"Hoàn tất {job['viec']}", "exit=0", 20, 10

    monkeypatch.setattr(hang_doi_git, "chay_agy", fake_agy)

    # Lượt 1: dù 01-tong-hop đứng đầu bảng chữ cái và đích danh may-1, vẫn phải bỏ qua vì chưa đủ phụ thuộc
    res1 = hang_doi_git.xu_ly_mot_phieu(cfg)
    assert res1 is not None and res1["viec"] == "02-buoc-a"

    # Lượt 2: mới xong 02-buoc-a, còn thiếu 03-buoc-b -> vẫn chưa nhận 01-tong-hop, nhận 03-buoc-b
    res2 = hang_doi_git.xu_ly_mot_phieu(cfg)
    assert res2 is not None and res2["viec"] == "03-buoc-b"

    # Lượt 3: cả 02-buoc-a và 03-buoc-b đã có KET-QUA.md trang_thai: xong -> nhận 01-tong-hop
    res3 = hang_doi_git.xu_ly_mot_phieu(cfg)
    assert res3 is not None and res3["viec"] == "01-tong-hop"

    assert hang_doi_git.xu_ly_mot_phieu(cfg) is None
    assert execution_order == ["02-buoc-a", "03-buoc-b", "01-tong-hop"]

    inspect_dir = _inspect_queue_branch(bare_repo, tmp_path, "kt-phu-thuoc-ok")
    for done_id in ("02-buoc-a", "03-buoc-b", "01-tong-hop"):
        assert (inspect_dir / "hang-doi" / "xong" / done_id / "KET-QUA.md").is_file()


def test_dependencies_skip_without_ket_qua_when_dep_fails_or_stops(tmp_path, monkeypatch):
    # A. Nếu một id phụ thuộc kết thúc `loi` hoặc `dung` thì phiếu phụ thuộc bỏ qua (không nhận),
    # KET-QUA không ghi gì.
    bare_repo = _create_bare_queue_repo(
        tmp_path,
        initial_tickets={
            "01-bi-loi": "may: may-1\nloai: code\n\nBước bị lỗi.",
            "02-bi-dung": "may: may-1\nloai: code\n\nBước bị bộ canh dừng.",
            "03-can-loi": "may: may-1\nloai: code\nphu_thuoc: ket-qua-ok; 01-bi-loi\n\nChờ 01-bi-loi.",
            "04-can-dung": "may: bat-ky\nloai: code\nphu_thuoc: 02-bi-dung\n\nChờ 02-bi-dung.",
            "05-du-phu-thuoc": "may: may-1\nloai: code\nphu_thuoc: ket-qua-ok\n\nChỉ phụ thuộc phiếu đã xong.",
        },
        finished_results={
            "ket-qua-ok": hang_doi_git.tao_ket_qua_md("ket-qua-ok", "may-2", "xong", "Đã xong từ trước"),
        },
    )
    cfg = _clone_worker_cfg(bare_repo, tmp_path, "may-1")
    executed: list[str] = []

    def fake_agy(worker_cfg, job):
        executed.append(job["viec"])
        if job["viec"] == "01-bi-loi":
            return "loi", "Sai kết quả nghiệm thu", "exit=1", 10, 5
        if job["viec"] == "02-bi-dung":
            return "dung", None, "dừng agy: quá 10 phút không tiến", 0, 0
        return "xong", "Chạy thành công", "exit=0", 15, 8

    monkeypatch.setattr(hang_doi_git, "chay_agy", fake_agy)

    # Chạy hết vòng: chỉ chạy 01-bi-loi, 02-bi-dung, 05-du-phu-thuoc; tuyệt đối không nhận 03 và 04
    hang_doi_git.vong_git(cfg, mot_lan=True)
    assert set(executed) == {"01-bi-loi", "02-bi-dung", "05-du-phu-thuoc"}

    inspect_dir = _inspect_queue_branch(bare_repo, tmp_path, "kt-phu-thuoc-bo")
    assert (inspect_dir / "hang-doi" / "moi" / "03-can-loi.md").is_file()
    assert (inspect_dir / "hang-doi" / "moi" / "04-can-dung.md").is_file()
    assert not (inspect_dir / "hang-doi" / "xong" / "03-can-loi").exists()
    assert not (inspect_dir / "hang-doi" / "xong" / "04-can-dung").exists()
    assert (inspect_dir / "hang-doi" / "xong" / "05-du-phu-thuoc" / "KET-QUA.md").is_file()


def test_self_repair_exact_retries_preserves_headers_excerpt_and_pushes_together(tmp_path, monkeypatch):
    # B. tu_sua: 2 -> trượt 3 lần liên tiếp (cả loi và dung) sinh đúng 2 phiếu sửa (<id>-sua-1, <id>-sua-2),
    # giữ nguyên header (giảm tu_sua đi 1, cùng may, theo_doi), thân = đề gốc + mục "Lần trước trượt vì:"
    # chép 1500 ký tự cuối KET-QUA, push cùng commit với KET-QUA.md.
    original_prompt = "Dựng module thanh toán và chạy bộ test khoá cho tới khi đạt 100%."
    bare_repo = _create_bare_queue_repo(
        tmp_path,
        initial_tickets={
            "thanh-toan": (
                "may: may-2\n"
                "loai: code\n"
                "tran_phut: 25\n"
                "theo_doi: C:\\linhx\\wt-thanh-toan\n"
                "tu_sua: 2\n\n"
                f"{original_prompt}\n"
            )
        },
    )
    cfg = _clone_worker_cfg(bare_repo, tmp_path, "may-2")
    seen_jobs: list[tuple[str, str]] = []

    def fake_agy(worker_cfg, job):
        seen_jobs.append((job["viec"], job["de"]))
        if job["viec"] == "thanh-toan":
            long_failure = "DAU_BAO_CAO_LAN_1\n" + ("Chi tiết lỗi kiểm thử dòng số abc.\n" * 80) + "DUOI_LOI_LAN_1_XYZ"
            return "loi", long_failure, "exit=1 giay=20\n--- stderr ---\npytest failed", 200, 90
        if job["viec"] == "thanh-toan-sua-1":
            return "dung", None, "dừng agy: quá 10 phút không tiến\nLog cuối lần 2", 0, 0
        return "loi", "Vẫn trượt ở lần cuối cùng", "exit=1 giay=15", 100, 40

    monkeypatch.setattr(hang_doi_git, "chay_agy", fake_agy)

    # --- Lượt 1: chạy phiếu gốc `thanh-toan` -> kết thúc `loi`, tạo `thanh-toan-sua-1.md` cùng lúc với KET-QUA ---
    r1 = hang_doi_git.xu_ly_mot_phieu(cfg)
    assert r1 is not None and r1["viec"] == "thanh-toan" and r1["trang_thai"] == "loi"

    inspect_1 = _inspect_queue_branch(bare_repo, tmp_path, "kt-sua-1")
    commit_files_1 = set(_run_git(["show", "--name-only", "--pretty=format:", "HEAD"], inspect_1).splitlines())
    assert "hang-doi/xong/thanh-toan/KET-QUA.md" in commit_files_1
    assert "hang-doi/moi/thanh-toan-sua-1.md" in commit_files_1

    kq_1_text = (inspect_1 / "hang-doi" / "xong" / "thanh-toan" / "KET-QUA.md").read_text(encoding="utf-8")
    assert len(kq_1_text) > 1500
    sua_1_text = (inspect_1 / "hang-doi" / "moi" / "thanh-toan-sua-1.md").read_text(encoding="utf-8")
    parsed_sua_1 = hang_doi_git.phan_tich_phieu(sua_1_text, "thanh-toan-sua-1")
    assert parsed_sua_1["may"] == "may-2"
    assert parsed_sua_1["loai"] == "code"
    assert parsed_sua_1["tran_phut"] == 25
    assert parsed_sua_1["meta"]["theo_doi"] == r"C:\linhx\wt-thanh-toan"
    assert "nhan" not in parsed_sua_1["meta"]
    assert parsed_sua_1["tu_sua"] == 1
    assert parsed_sua_1["de"].startswith(original_prompt)
    assert "Lần trước trượt vì:" in sua_1_text
    assert kq_1_text[-1500:] in sua_1_text
    assert "DAU_BAO_CAO_LAN_1" not in sua_1_text  # phần đầu quá 1500 ký tự cuối không bị chép dư

    # --- Lượt 2: chạy `thanh-toan-sua-1` -> kết thúc `dung`, tạo `thanh-toan-sua-2.md` (tu_sua: 0) ---
    r2 = hang_doi_git.xu_ly_mot_phieu(cfg)
    assert r2 is not None and r2["viec"] == "thanh-toan-sua-1" and r2["trang_thai"] == "dung"

    inspect_2 = _inspect_queue_branch(bare_repo, tmp_path, "kt-sua-2")
    kq_2_text = (inspect_2 / "hang-doi" / "xong" / "thanh-toan-sua-1" / "KET-QUA.md").read_text(encoding="utf-8")
    sua_2_text = (inspect_2 / "hang-doi" / "moi" / "thanh-toan-sua-2.md").read_text(encoding="utf-8")
    parsed_sua_2 = hang_doi_git.phan_tich_phieu(sua_2_text, "thanh-toan-sua-2")
    assert parsed_sua_2["tu_sua"] == 0
    assert parsed_sua_2["may"] == "may-2"
    assert parsed_sua_2["meta"]["theo_doi"] == r"C:\linhx\wt-thanh-toan"
    assert sua_2_text.count("Lần trước trượt vì:") == 1  # giữ đề gốc, không chồng nhiều mục cũ
    assert parsed_sua_2["de"].startswith(original_prompt)
    assert kq_2_text[-1500:] in sua_2_text

    # --- Lượt 3: chạy `thanh-toan-sua-2` (tu_sua: 0) -> trượt nhưng hết lượt thì thôi ---
    r3 = hang_doi_git.xu_ly_mot_phieu(cfg)
    assert r3 is not None and r3["viec"] == "thanh-toan-sua-2" and r3["trang_thai"] == "loi"
    assert hang_doi_git.xu_ly_mot_phieu(cfg) is None

    inspect_3 = _inspect_queue_branch(bare_repo, tmp_path, "kt-sua-3")
    assert list((inspect_3 / "hang-doi" / "moi").glob("*.md")) == []
    assert not (inspect_3 / "hang-doi" / "xong" / "thanh-toan-sua-3").exists()
    assert [vid for vid, _ in seen_jobs] == ["thanh-toan", "thanh-toan-sua-1", "thanh-toan-sua-2"]


def test_self_repair_max_3_cap_and_stops_when_fixed(tmp_path, monkeypatch):
    # Kiểm tra trần tối đa 3 lượt sửa khi ghi tu_sua > 3, và dừng tạo phiếu ngay khi sửa đạt `xong`
    bare_repo = _create_bare_queue_repo(
        tmp_path,
        initial_tickets={
            "01-qua-tran": "may: may-1\nloai: code\ntu_sua: 9\n\nLuôn trượt để kiểm trần 3 lượt.",
            "02-sua-dat": "may: may-1\nloai: code\ntu_sua: 3\n\nTrượt lần đầu, đạt ngay ở sua-1.",
        },
    )
    cfg = _clone_worker_cfg(bare_repo, tmp_path, "may-1")
    run_history: list[str] = []

    def fake_agy(worker_cfg, job):
        run_history.append(job["viec"])
        if job["viec"] == "02-sua-dat-sua-1":
            return "xong", "Đã sửa đạt toàn bộ test!", "exit=0", 50, 25
        return "loi", f"Trượt ở {job['viec']}", "exit=1", 30, 10

    monkeypatch.setattr(hang_doi_git, "chay_agy", fake_agy)
    hang_doi_git.vong_git(cfg, mot_lan=True)

    # 01-qua-tran chỉ sinh tối đa 3 phiếu sửa (sua-1, sua-2, sua-3); 02-sua-dat dừng ngay sau sua-1
    sua_01 = [vid for vid in run_history if vid.startswith("01-qua-tran-sua-")]
    sua_02 = [vid for vid in run_history if vid.startswith("02-sua-dat-sua-")]
    assert sua_01 == ["01-qua-tran-sua-1", "01-qua-tran-sua-2", "01-qua-tran-sua-3"]
    assert sua_02 == ["02-sua-dat-sua-1"]


def test_self_repair_not_generated_on_machine_errors(tmp_path, monkeypatch):
    # B. Không sinh phiếu tự sửa khi gặp lỗi máy: thiếu agy hoặc lỗi 429 / hết hạn mức;
    # nhưng lỗi test thông thường (kể cả giay=429 hoặc line 429) vẫn sinh phiếu sửa đúng.
    bare_repo = _create_bare_queue_repo(
        tmp_path,
        initial_tickets={
            "01-thieu-agy": "may: may-1\nloai: code\ntu_sua: 3\n\nThử lỗi thiếu agy.",
            "02-loi-429": "may: may-1\nloai: code\ntu_sua: 3\n\nThử lỗi 429 quota.",
            "03-loi-code-429s": "may: may-1\nloai: code\ntu_sua: 1\n\nLỗi code chạy 429 giây ở line 429.",
        },
    )
    # Trường hợp 1: gọi chay_agy thật với binary không tồn tại -> thiếu agy
    cfg_missing_agy = _clone_worker_cfg(bare_repo, tmp_path, "may-1", agy="agy-khong-ton-tai-tren-he-thong-xyz")
    r_missing = hang_doi_git.xu_ly_mot_phieu(cfg_missing_agy)
    assert r_missing is not None
    assert r_missing["viec"] == "01-thieu-agy"
    assert r_missing["trang_thai"] == "loi"
    assert "không thấy agy" in r_missing["nhat_ky"]

    inspect_after_1 = _inspect_queue_branch(bare_repo, tmp_path, "kt-loi-may-1")
    assert not (inspect_after_1 / "hang-doi" / "moi" / "01-thieu-agy-sua-1.md").exists()

    # Trường hợp 2 & 3: lỗi 429 (không sinh phiếu sửa) vs lỗi code ở giay=429 / line 429 (có sinh phiếu sửa)
    cfg = _clone_worker_cfg(bare_repo, tmp_path, "may-1")

    def fake_agy(worker_cfg, job):
        if job["viec"] == "02-loi-429":
            return "loi", "", "exit=1 giay=4\n--- stderr ---\nHTTP Error 429: Too Many Requests", 0, 0
        if job["viec"] == "03-loi-code-429s":
            return (
                "loi",
                'File "app.py", line 429, in tinh_toan\nAssertionError: sai gia tri',
                "exit=1 giay=429\n--- stderr ---\n1 failed",
                80,
                30,
            )
        return "xong", "Đã sửa xong 03", "exit=0", 40, 20

    monkeypatch.setattr(hang_doi_git, "chay_agy", fake_agy)
    hang_doi_git.vong_git(cfg, mot_lan=True)

    inspect_final = _inspect_queue_branch(bare_repo, tmp_path, "kt-loi-may-final")
    assert not (inspect_final / "hang-doi" / "xong" / "01-thieu-agy-sua-1").exists()
    assert not (inspect_final / "hang-doi" / "xong" / "02-loi-429-sua-1").exists()
    assert (inspect_final / "hang-doi" / "xong" / "03-loi-code-429s-sua-1" / "KET-QUA.md").is_file()
    nd_ok = (inspect_final / "hang-doi" / "xong" / "03-loi-code-429s-sua-1" / "KET-QUA.md").read_text(encoding="utf-8")
    assert "trang_thai: xong" in nd_ok
