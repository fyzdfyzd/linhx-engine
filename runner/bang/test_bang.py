"""Kiểm thử bảng theo dõi web `runner/bang/` với dữ liệu giả (không gọi mạng, không dùng conftest.py)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import threading
import urllib.error
import urllib.request
import uuid

import pytest

BANG_DIR = Path(__file__).resolve().parent
RUNNER_DIR = BANG_DIR.parent
REPO_ROOT = RUNNER_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runner.bang import bang  # noqa: E402


def _remove_tree(target: Path) -> None:
    """Xóa thư mục tạm kể cả khi có file read-only của .git trên Windows."""
    if not target.exists():
        return

    def _on_err(fn, path_str, _exc_info):
        try:
            os.chmod(path_str, stat.S_IWRITE)
            fn(path_str)
        except OSError:
            pass

    shutil.rmtree(target, onerror=_on_err)


@pytest.fixture
def tmp_path():
    """Tạo thư mục tạm bên trong runner/viec (đã nằm trong .gitignore) và dọn sạch sau test."""
    viec_root = RUNNER_DIR / "viec"
    existed_before = viec_root.exists()
    temp_dir = viec_root / f"pytest-tmp-bang-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    try:
        yield temp_dir
    finally:
        _remove_tree(temp_dir)
        if not existed_before and viec_root.exists():
            try:
                next(viec_root.iterdir())
            except StopIteration:
                viec_root.rmdir()


def _git_local(args: list[str], cwd: Path, commit_iso: str | None = None) -> str:
    """Chạy git cục bộ cho test không cần mạng."""
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    if commit_iso:
        env["GIT_AUTHOR_DATE"] = commit_iso
        env["GIT_COMMITTER_DATE"] = commit_iso
    kwargs = {"creationflags": 0x08000000} if os.name == "nt" else {}
    proc = subprocess.run(
        ["git"] + list(args),
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        **kwargs,
    )
    return proc.stdout.strip()


def _write_done_ticket(
    qroot: Path,
    ticket_id: str,
    machine: str,
    status: str,
    minutes: float,
    tok_in: int,
    tok_out: int,
    body: str,
    mtime_epoch: float | None = None,
) -> Path:
    """Tạo file giả `hang-doi/xong/<id>/KET-QUA.md`."""
    kq_file = qroot / "xong" / ticket_id / "KET-QUA.md"
    kq_file.parent.mkdir(parents=True, exist_ok=True)
    content = (
        f"phieu: {ticket_id}\n"
        f"may: {machine}\n"
        f"trang_thai: {status}\n"
        "tep_doi: (khong)\n"
        "drive: (khong)\n"
        f"phut: {minutes:.2f}\n"
        f"token: vao={tok_in} ra={tok_out}\n\n"
        f"{body}\n"
    )
    kq_file.write_text(content, encoding="utf-8")
    if mtime_epoch is not None:
        os.utime(kq_file, (mtime_epoch, mtime_epoch))
    return kq_file


def test_parse_headers_tokens_and_iso_timestamps():
    """Kiểm tra phân tích frontmatter, dòng header, token và định dạng thời gian ISO."""
    meta1, body1 = bang.parse_markdown_headers(
        "---\nmay: may-2\nloai: code\nnote: thu nghiem\n---\nNoi dung de 1"
    )
    assert meta1["may"] == "may-2"
    assert meta1["loai"] == "code"
    assert body1 == "Noi dung de 1"

    meta2, body2 = bang.parse_markdown_headers(
        "may: bat-ky; loai: trinh-duyet\nnhan: may-1 2026-11-15T07:00:00+0700\n\nMo trang"
    )
    assert meta2["may"] == "bat-ky"
    assert meta2["loai"] == "trinh-duyet"
    assert meta2["nhan"].startswith("may-1 ")
    assert body2 == "Mo trang"

    assert bang.parse_tokens("vao=13566 ra=153") == (13566, 153, 13719)
    assert bang.parse_tokens("2500") == (2500, 0, 2500)
    assert bang.parse_tokens("khong-hop-le") == (0, 0, 0)

    dt_compact = bang.parse_iso_datetime("2026-11-15T07:30:27+0700")
    dt_utc = bang.parse_iso_datetime("2026-11-15T00:30:27Z")
    assert dt_compact is not None and dt_utc is not None
    assert int(dt_compact.timestamp()) == int(dt_utc.timestamp())

    assert bang.is_safe_ticket_id("ping-may-1_b.2") is True
    assert bang.is_safe_ticket_id("../bi-mat") is False
    assert bang.is_safe_ticket_id("a/b") is False
    assert bang.is_safe_ticket_id("a\\b") is False


def test_read_queue_snapshot_20_recent_done_and_machine_30min_red(tmp_path: Path):
    """Kiểm tra đủ 4 mục: đang chạy, đang chờ, 20 phiếu xong gần nhất, và máy đỏ khi quá 30 phút."""
    tz_vn = timezone(timedelta(hours=7))
    fixed_now = datetime(2026, 11, 15, 8, 0, 0, tzinfo=tz_vn)

    clone_dir = tmp_path / "bang-gia"
    qroot = clone_dir / "hang-doi"
    (qroot / "moi").mkdir(parents=True)
    (qroot / "dang").mkdir(parents=True)
    (qroot / "xong").mkdir(parents=True)

    # (1) Đang chạy: may-1 chạy 12 phút, may-2 mới nhận 3 phút trước
    t_run_may1 = (fixed_now - timedelta(minutes=12, seconds=30)).strftime("%Y-%m-%dT%H:%M:%S%z")
    t_run_may2 = (fixed_now - timedelta(minutes=3)).strftime("%Y-%m-%dT%H:%M:%S%z")
    (qroot / "dang" / "viec-dang-1.md").write_text(
        f"may: may-1\nloai: code\ntran_phut: 40\nnhan: may-1 {t_run_may1}\n\nĐang xử lý việc 1\n",
        encoding="utf-8",
    )
    (qroot / "dang" / "viec-dang-2.md").write_text(
        f"may: bat-ky\nloai: trinh-duyet\ntran_phut: 25\nnhan: may-2 {t_run_may2}\n\nĐang xử lý việc 2\n",
        encoding="utf-8",
    )

    # (2) Đang chờ: 1 việc cho bat-ky, 1 việc đích danh may-4 (chưa từng chạy -> phải báo đỏ)
    (qroot / "moi" / "cho-01.md").write_text(
        "may: bat-ky\nloai: code\ntran_phut: 20\n\nViệc chờ chung\n",
        encoding="utf-8",
    )
    (qroot / "moi" / "cho-02-may4.md").write_text(
        "may: may-4\nloai: khac\ntran_phut: 10\n\nViệc chờ riêng máy 4\n",
        encoding="utf-8",
    )

    # (3) Tạo 25 phiếu đã xong với đủ trạng thái xong/loi/dung và mtime tăng dần
    statuses = ["xong", "loi", "dung"]
    for idx in range(1, 26):
        # idx=25 mới nhất (5 phút trước), idx=1 cũ nhất (125 phút trước)
        finished_dt = fixed_now - timedelta(minutes=(26 - idx) * 5)
        machine = "may-3" if idx <= 19 else ("may-1" if idx % 2 == 0 else "may-2")
        # Với idx=19: (26-19)*5 = 35 phút trước -> may-3 quá 30 phút không hoạt động!
        _write_done_ticket(
            qroot=qroot,
            ticket_id=f"phieu-{idx:02d}",
            machine=machine,
            status=statuses[idx % 3],
            minutes=round(idx * 0.5, 2),
            tok_in=idx * 100,
            tok_out=idx * 10,
            body=f"Kết quả của phiếu {idx:02d}",
            mtime_epoch=finished_dt.timestamp(),
        )

    snap = bang.read_queue_snapshot(clone_dir, now=fixed_now)

    # Kiểm tra (1) Đang chạy
    assert len(snap["dang_chay"]) == 2
    by_run = {item["phieu"]: item for item in snap["dang_chay"]}
    assert by_run["viec-dang-1"]["may"] == "may-1"
    assert by_run["viec-dang-1"]["chay_giay"] == 750
    assert "12 phút 30 giây" == by_run["viec-dang-1"]["chay_bao_lau"]
    assert by_run["viec-dang-2"]["may"] == "may-2"
    assert by_run["viec-dang-2"]["chay_bao_lau"] == "3 phút"

    # Kiểm tra (2) Đang chờ
    assert len(snap["dang_cho"]) == 2
    assert [w["phieu"] for w in snap["dang_cho"]] == ["cho-01", "cho-02-may4"]

    # Kiểm tra (3) Xong gần nhất đúng 20 phiếu mới nhất (phieu-25 -> phieu-06)
    assert snap["tong_xong"] == 25
    assert len(snap["xong_gan_nhat"]) == 20
    assert snap["xong_gan_nhat"][0]["phieu"] == "phieu-25"
    assert snap["xong_gan_nhat"][-1]["phieu"] == "phieu-06"
    assert {d["trang_thai"] for d in snap["xong_gan_nhat"]} == {"xong", "loi", "dung"}
    newest = snap["xong_gan_nhat"][0]
    assert newest["token_vao"] == 2500
    assert newest["token_ra"] == 250
    assert newest["tong_token"] == 2750
    assert newest["phut"] == 12.5

    # Kiểm tra (4) Trạng thái từng máy (quá 30 phút không hoạt động -> qua_30_phut = True)
    machines = {m["may"]: m for m in snap["may"]}
    assert set(machines.keys()) == {"may-1", "may-2", "may-3", "may-4"}

    # may-2: nhận viec-dang-2 lúc 3 phút trước (mới hơn phieu-25 lúc 5 phút trước) -> hoạt động
    assert machines["may-2"]["su_kien_cuoi"] == "nhan"
    assert machines["may-2"]["phieu_cuoi"] == "viec-dang-2"
    assert machines["may-2"]["qua_30_phut"] is False

    # may-1: xong phieu-24 lúc 10 phút trước (mới hơn nhận viec-dang-1 lúc 12.5 phút trước) -> hoạt động
    assert machines["may-1"]["su_kien_cuoi"] == "xong"
    assert machines["may-1"]["phieu_cuoi"] == "phieu-24"
    assert machines["may-1"]["qua_30_phut"] is False

    # may-3: lần cuối xong phieu-19 lúc 35 phút trước (> 30 phút) -> ĐỎ
    assert machines["may-3"]["phieu_cuoi"] == "phieu-19"
    assert machines["may-3"]["khong_hoat_dong_phut"] == 35.0
    assert machines["may-3"]["qua_30_phut"] is True

    # may-4: có phiếu chờ nhưng chưa từng nhận/xong -> ĐỎ
    assert machines["may-4"]["qua_30_phut"] is True


def test_git_sync_periodic_fetch_from_local_bare_readonly(tmp_path: Path):
    """Kiểm tra `QueueMonitor` tự `git fetch` nhánh `hang-doi` từ bare repo cục bộ (không gọi mạng)."""
    tz_vn = timezone(timedelta(hours=7))
    t0 = datetime(2026, 11, 15, 7, 30, 0, tzinfo=tz_vn)

    bare = tmp_path / "remote.git"
    bare.mkdir(parents=True)
    _git_local(["init", "--bare"], bare)

    # Trường hợp 1: remote chưa có nhánh hang-doi -> không lỗi, trả bảng rỗng
    clone_dir = tmp_path / "bang-hang-doi"
    mon = bang.QueueMonitor(
        clone_dir=clone_dir,
        repo_url=str(bare),
        branch="hang-doi",
        fetch_interval=0.05,
        enable_git_sync=True,
        clock_fn=lambda: t0,
    )
    assert mon.sync_once() is True
    st_empty = mon.get_status()
    assert st_empty["dang_chay"] == []
    assert st_empty["xong_gan_nhat"] == []
    assert st_empty["loi_dong_bo"] == ""

    # Tạo nhánh orphan hang-doi trên seed và push vào bare cục bộ
    seed = tmp_path / "seed"
    seed.mkdir()
    _git_local(["init"], seed)
    _git_local(["config", "user.name", "seed"], seed)
    _git_local(["config", "user.email", "seed@linhx.local"], seed)
    _git_local(["config", "commit.gpgsign", "false"], seed)
    _git_local(["remote", "add", "origin", str(bare)], seed)
    _git_local(["checkout", "--orphan", "hang-doi"], seed)

    (seed / "hang-doi" / "moi").mkdir(parents=True)
    (seed / "hang-doi" / "moi" / "p-moi.md").write_text("may: may-1\nloai: code\n\nĐề mới\n", encoding="utf-8")
    _write_done_ticket(
        seed / "hang-doi",
        ticket_id="p-cu-may-3",
        machine="may-3",
        status="dung",
        minutes=10.0,
        tok_in=0,
        tok_out=0,
        body="dừng do quá hạn",
    )
    # Commit lúc 40 phút trước t0 -> may-3 phải bị đánh dấu quá 30 phút (qua_30_phut = True)
    t_old_iso = (t0 - timedelta(minutes=40)).isoformat(timespec="seconds")
    _git_local(["add", "-A"], seed)
    _git_local(["commit", "-m", "khoi tao hang-doi"], seed, commit_iso=t_old_iso)
    _git_local(["push", "origin", "hang-doi"], seed)

    assert mon.sync_once() is True
    st1 = mon.get_status()
    assert [w["phieu"] for w in st1["dang_cho"]] == ["p-moi"]
    assert [d["phieu"] for d in st1["xong_gan_nhat"]] == ["p-cu-may-3"]
    may_map1 = {m["may"]: m for m in st1["may"]}
    # Lấy đúng thời gian từ git commit (40 phút trước) dù file vừa được checkout ra đĩa!
    assert may_map1["may-3"]["khong_hoat_dong_phut"] == 40.0
    assert may_map1["may-3"]["qua_30_phut"] is True

    # Chạy đồng bộ nền tự động, đẩy thêm commit mới lên bare repo và chờ luồng nền tự fetch
    mon.start_background_sync()
    try:
        (seed / "hang-doi" / "moi" / "p-moi.md").unlink()
        _write_done_ticket(
            seed / "hang-doi",
            ticket_id="p-moi",
            machine="may-1",
            status="xong",
            minutes=1.5,
            tok_in=500,
            tok_out=120,
            body="PONG may-1",
        )
        t_recent_iso = (t0 - timedelta(minutes=2)).isoformat(timespec="seconds")
        _git_local(["add", "-A"], seed)
        _git_local(["commit", "-m", "xong: p-moi (xong)"], seed, commit_iso=t_recent_iso)
        _git_local(["push", "origin", "hang-doi"], seed)

        # Đợi tối đa 3 giây cho luồng nền (chu kỳ 0.05s) kéo commit mới
        deadline = threading.Event()
        updated_status = None
        for _ in range(40):
            cur = mon.get_status()
            if any(d["phieu"] == "p-moi" for d in cur["xong_gan_nhat"]):
                updated_status = cur
                break
            deadline.wait(0.05)

        assert updated_status is not None
        assert updated_status["dang_cho"] == []
        assert updated_status["xong_gan_nhat"][0]["phieu"] == "p-moi"
        may_map2 = {m["may"]: m for m in updated_status["may"]}
        assert may_map2["may-1"]["qua_30_phut"] is False
        assert may_map2["may-1"]["khong_hoat_dong_phut"] == 2.0
    finally:
        mon.stop_background_sync()

    # Đảm bảo bản clone hoàn toàn sạch (chỉ đọc, không phát sinh file rác hay commit cục bộ)
    assert _git_local(["status", "--porcelain"], clone_dir) == ""


def test_http_endpoints_html_json_ticket_detail_and_readonly(tmp_path: Path):
    """Kiểm tra server HTTP: `/`, `/api/trang-thai`, `/phieu/<id>`, `/api/ket-qua/<id>` và chặn ghi (405)."""
    tz_vn = timezone(timedelta(hours=7))
    fixed_now = datetime(2026, 11, 15, 9, 0, 0, tzinfo=tz_vn)

    clone_dir = tmp_path / "bang-web"
    qroot = clone_dir / "hang-doi"
    (qroot / "moi").mkdir(parents=True)
    (qroot / "dang").mkdir(parents=True)
    (qroot / "xong").mkdir(parents=True)

    claimed_iso = (fixed_now - timedelta(minutes=6)).strftime("%Y-%m-%dT%H:%M:%S%z")
    (qroot / "dang" / "dang-01.md").write_text(
        f"may: may-2\nloai: code\nnhan: may-2 {claimed_iso}\n\nĐang dựng bảng\n",
        encoding="utf-8",
    )
    (qroot / "moi" / "cho-01.md").write_text(
        "may: bat-ky\nloai: code\ntran_phut: 15\n\nPhiếu đang đợi\n",
        encoding="utf-8",
    )
    _write_done_ticket(
        qroot,
        ticket_id="xong-ok",
        machine="may-1",
        status="xong",
        minutes=2.35,
        tok_in=1200,
        tok_out=300,
        body="Kết quả thành công <script>alert(1)</script>",
        mtime_epoch=(fixed_now - timedelta(minutes=8)).timestamp(),
    )
    _write_done_ticket(
        qroot,
        ticket_id="xong-loi",
        machine="may-3",
        status="loi",
        minutes=0.5,
        tok_in=50,
        tok_out=10,
        body="Lỗi thiếu cấu hình",
        mtime_epoch=(fixed_now - timedelta(minutes=45)).timestamp(),
    )
    _write_done_ticket(
        qroot,
        ticket_id="xong-dung",
        machine="may-2",
        status="dung",
        minutes=40.0,
        tok_in=900,
        tok_out=0,
        body="Dừng do quá trần 40 phút",
        mtime_epoch=(fixed_now - timedelta(minutes=20)).timestamp(),
    )

    monitor = bang.QueueMonitor(
        clone_dir=clone_dir,
        repo_url="",
        fetch_interval=30,
        enable_git_sync=False,
        clock_fn=lambda: fixed_now,
    )
    server = bang.create_http_server(monitor, host="127.0.0.1", port=0)
    port = server.server_address[1]
    base_url = f"http://127.0.0.1:{port}"

    srv_thread = threading.Thread(target=server.serve_forever, daemon=True)
    srv_thread.start()
    try:
        # 1. Kiểm tra /api/trang-thai
        with urllib.request.urlopen(f"{base_url}/api/trang-thai", timeout=5) as resp:
            assert resp.status == 200
            assert "application/json" in resp.headers.get("Content-Type", "")
            api_data = json.loads(resp.read().decode("utf-8"))

        assert len(api_data["dang_chay"]) == 1
        assert api_data["dang_chay"][0]["phieu"] == "dang-01"
        assert len(api_data["dang_cho"]) == 1
        assert len(api_data["xong_gan_nhat"]) == 3
        may_api = {m["may"]: m for m in api_data["may"]}
        assert may_api["may-3"]["qua_30_phut"] is True
        assert may_api["may-1"]["qua_30_phut"] is False
        assert may_api["may-2"]["qua_30_phut"] is False

        # 2. Kiểm tra trang chủ `/` tiếng Việt, tự làm mới 30 giây, tô màu trạng thái và máy quá hạn
        with urllib.request.urlopen(f"{base_url}/", timeout=5) as resp_html:
            assert resp_html.status == 200
            html_body = resp_html.read().decode("utf-8")

        assert '<meta http-equiv="refresh" content="30">' in html_body
        assert "1. Đang chạy" in html_body
        assert "2. Đang chờ" in html_body
        assert "3. Xong gần nhất" in html_body
        assert "4. Trạng thái máy" in html_body
        assert "6 phút" in html_body
        assert "tt-xong" in html_body
        assert "tt-loi" in html_body
        assert "tt-dung" in html_body
        assert 'class="qua-han"' in html_body
        assert "Quá 30 phút không hoạt động" in html_body
        assert 'href="/phieu/xong-ok"' in html_body

        # 3. Bấm vào phiếu xem KET-QUA.md (kiểm tra luôn chống XSS)
        with urllib.request.urlopen(f"{base_url}/phieu/xong-ok", timeout=5) as resp_kq:
            assert resp_kq.status == 200
            kq_html = resp_kq.read().decode("utf-8")
        assert "phieu: xong-ok" in kq_html
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in kq_html
        assert "<script>alert(1)</script>" not in kq_html

        with urllib.request.urlopen(f"{base_url}/api/ket-qua/xong-ok", timeout=5) as resp_kq_json:
            assert resp_kq_json.status == 200
            kq_json = json.loads(resp_kq_json.read().decode("utf-8"))
        assert kq_json["phieu"] == "xong-ok"
        assert kq_json["tong_token"] == 1500
        assert "Kết quả thành công" in kq_json["noi_dung"]

        # 4. Phiếu không tồn tại -> 404; mã phiếu xấu -> 400
        with pytest.raises(urllib.error.HTTPError) as exc_404:
            urllib.request.urlopen(f"{base_url}/phieu/khong-co", timeout=5)
        assert exc_404.value.code == 404
        exc_404.value.close()

        with pytest.raises(urllib.error.HTTPError) as exc_400:
            urllib.request.urlopen(f"{base_url}/api/ket-qua/..%2Fbi-mat", timeout=5)
        assert exc_400.value.code == 400
        exc_400.value.close()

        # 5. Chặn mọi phương thức ghi (POST / DELETE -> 405)
        for method in ("POST", "PUT", "DELETE"):
            req = urllib.request.Request(f"{base_url}/api/trang-thai", data=b"{}", method=method)
            with pytest.raises(urllib.error.HTTPError) as exc_405:
                urllib.request.urlopen(req, timeout=5)
            assert exc_405.value.code == 405
            exc_405.value.close()
    finally:
        server.shutdown()
        server.server_close()
        srv_thread.join(timeout=3)


def test_single_instance_lock(tmp_path: Path):
    """Kiểm tra khóa chống chạy chồng nhiều tiến trình bảng."""
    lock_file = tmp_path / "bang.lock"
    with bang.single_instance_lock(lock_file) as first_ok:
        assert first_ok is True
        with bang.single_instance_lock(lock_file) as second_ok:
            assert second_ok is False
    with bang.single_instance_lock(lock_file) as third_ok:
        assert third_ok is True


def test_boundary_30_minutes_and_sync_error_resilience(tmp_path: Path):
    """Kiểm tra ranh giới đúng 30 phút (<=30 xanh, >30 đỏ) và giữ dữ liệu cũ khi git fetch lỗi."""
    tz_vn = timezone(timedelta(hours=7))
    fixed_now = datetime(2026, 11, 15, 10, 0, 0, tzinfo=tz_vn)

    clone_dir = tmp_path / "bang-ranh-gioi"
    qroot = clone_dir / "hang-doi"
    _write_done_ticket(
        qroot,
        ticket_id="dung-30p",
        machine="may-1",
        status="xong",
        minutes=1.0,
        tok_in=10,
        tok_out=5,
        body="Đúng 30 phút",
        mtime_epoch=(fixed_now - timedelta(minutes=30)).timestamp(),
    )
    _write_done_ticket(
        qroot,
        ticket_id="qua-30p-1s",
        machine="may-2",
        status="xong",
        minutes=1.0,
        tok_in=10,
        tok_out=5,
        body="Quá 30 phút 1 giây",
        mtime_epoch=(fixed_now - timedelta(minutes=30, seconds=1)).timestamp(),
    )

    snap = bang.read_queue_snapshot(clone_dir, now=fixed_now)
    by_machine = {m["may"]: m for m in snap["may"]}
    assert by_machine["may-1"]["qua_30_phut"] is False
    assert by_machine["may-2"]["qua_30_phut"] is True

    # Khi repo_url trỏ tới thư mục không tồn tại -> sync_once trả False, ghi loi_dong_bo nhưng vẫn phục vụ dữ liệu sẵn có
    mon = bang.QueueMonitor(
        clone_dir=clone_dir,
        repo_url=str(tmp_path / "khong-ton-tai.git"),
        enable_git_sync=True,
        clock_fn=lambda: fixed_now,
    )
    assert mon.sync_once() is False
    st = mon.get_status()
    assert st["loi_dong_bo"] != ""
    assert len(st["xong_gan_nhat"]) == 2
    html_text = bang.render_dashboard_html(st)
    assert "Lỗi đồng bộ git gần nhất" in html_text



def test_cai_bang_ps1_and_chay_an_bang_vbs(tmp_path: Path):
    """Kiểm tra `chay-an-bang.vbs` và `cai-bang.ps1` (Task Scheduler khi đăng nhập + tường lửa Private 8090)."""
    vbs_file = BANG_DIR / "chay-an-bang.vbs"
    ps1_file = BANG_DIR / "cai-bang.ps1"
    assert vbs_file.is_file()
    assert ps1_file.is_file()

    vbs_text = vbs_file.read_text(encoding="utf-8")
    assert "bang.py" in vbs_text
    assert ", 0, False" in vbs_text

    ps_bin = shutil.which("powershell") or shutil.which("pwsh")
    if ps_bin is None:
        pytest.skip("Máy không có PowerShell để chạy kiểm thử mock cai-bang.ps1")

    out_json = tmp_path / "ket-qua-cai-bang.json"
    clone_mock = tmp_path / "bang-hang-doi"
    log_mock = tmp_path / "bang.log"
    wrapper_ps1 = tmp_path / "mock-cai-bang.ps1"

    cfg_payload = {
        "ScriptPath": str(ps1_file),
        "OutJson": str(out_json),
        "CloneDir": str(clone_mock),
        "LogFile": str(log_mock),
    }
    cfg_file = tmp_path / "cfg.json"
    cfg_file.write_text(json.dumps(cfg_payload, ensure_ascii=False), encoding="utf-8")

    ps_code = f"""
$ErrorActionPreference = "Stop"
$cfg = Get-Content -LiteralPath '{str(cfg_file).replace("'", "''")}' -Raw -Encoding UTF8 | ConvertFrom-Json
$global:__KetQuaMock = @{{
    RemovedRules = @()
    FirewallRule = $null
    Task = $null
    StartedTasks = @()
}}

function global:Remove-NetFirewallRule {{
    param([string]$Name, $ErrorAction)
    $global:__KetQuaMock.RemovedRules += $Name
}}

function global:New-NetFirewallRule {{
    param(
        [string]$Name,
        [string]$DisplayName,
        [string]$Direction,
        [string]$Protocol,
        [int]$LocalPort,
        [string]$Profile,
        [string]$Action,
        $ErrorAction
    )
    $global:__KetQuaMock.FirewallRule = [pscustomobject]@{{
        Name = $Name
        DisplayName = $DisplayName
        Direction = $Direction
        Protocol = $Protocol
        LocalPort = $LocalPort
        Profile = $Profile
        Action = $Action
    }}
    return $global:__KetQuaMock.FirewallRule
}}

function global:New-ScheduledTaskAction {{
    param([string]$Execute, [string]$Argument, [string]$WorkingDirectory)
    return [pscustomobject]@{{
        Execute = $Execute
        Argument = $Argument
        WorkingDirectory = $WorkingDirectory
    }}
}}

function global:New-ScheduledTaskTrigger {{
    param([switch]$AtLogOn, [string]$User)
    return [pscustomobject]@{{
        AtLogOn = [bool]$AtLogOn
        User = $User
    }}
}}

function global:New-ScheduledTaskPrincipal {{
    param([string]$UserId, [string]$LogonType, [string]$RunLevel)
    return [pscustomobject]@{{
        UserId = $UserId
        LogonType = $LogonType
        RunLevel = $RunLevel
    }}
}}

function global:New-ScheduledTaskSettingsSet {{
    param(
        [switch]$AllowStartIfOnBatteries,
        [switch]$DontStopIfGoingOnBatteries,
        [switch]$StartWhenAvailable,
        [string]$MultipleInstances,
        [TimeSpan]$ExecutionTimeLimit,
        [int]$RestartCount,
        [TimeSpan]$RestartInterval
    )
    return [pscustomobject]@{{
        AllowStartIfOnBatteries = [bool]$AllowStartIfOnBatteries
        DontStopIfGoingOnBatteries = [bool]$DontStopIfGoingOnBatteries
        MultipleInstances = $MultipleInstances
        ExecutionTimeLimitMinutes = [double]$ExecutionTimeLimit.TotalMinutes
        RestartCount = $RestartCount
    }}
}}

function global:Register-ScheduledTask {{
    param([string]$TaskName, $Action, $Trigger, $Principal, $Settings, [switch]$Force)
    $global:__KetQuaMock.Task = [pscustomobject]@{{
        TaskName = $TaskName
        Force = [bool]$Force
        Action = $Action
        Trigger = $Trigger
        Principal = $Principal
        Settings = $Settings
    }}
    return $global:__KetQuaMock.Task
}}

function global:Get-NetTCPConnection {{
    param([int]$LocalPort, [string]$State, $ErrorAction)
    return @()
}}

function global:Start-ScheduledTask {{
    param([string]$TaskName)
    $global:__KetQuaMock.StartedTasks += $TaskName
}}

& $cfg.ScriptPath -Cong 8090 -ThuMucClone $cfg.CloneDir -RepoUrl "https://khong-goi-mang.invalid/repo.git" -TepLog $cfg.LogFile | Out-Null
$json = $global:__KetQuaMock | ConvertTo-Json -Depth 6
[System.IO.File]::WriteAllText($cfg.OutJson, $json, (New-Object System.Text.UTF8Encoding($false)))
"""
    wrapper_ps1.write_bytes(b"\xef\xbb\xbf" + ps_code.encode("utf-8"))
    kwargs = {"creationflags": 0x08000000} if os.name == "nt" else {}
    proc = subprocess.run(
        [ps_bin, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(wrapper_ps1)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        **kwargs,
    )
    assert proc.returncode == 0, f"cai-bang.ps1 lỗi: {proc.stderr or proc.stdout}"

    mock_res = json.loads(out_json.read_text(encoding="utf-8"))
    fw = mock_res["FirewallRule"]
    assert fw["Direction"] == "Inbound"
    assert fw["Protocol"] == "TCP"
    assert fw["LocalPort"] == 8090
    assert fw["Profile"] == "Private"
    assert fw["Action"] == "Allow"

    task = mock_res["Task"]
    assert task["TaskName"] == "LINHX-Bang"
    assert task["Force"] is True
    assert task["Trigger"]["AtLogOn"] is True
    assert task["Action"]["Execute"].lower() == "wscript.exe"
    assert "//B" in task["Action"]["Argument"]
    assert "chay-an-bang.vbs" in task["Action"]["Argument"]
    assert "--cong 8090" in task["Action"]["Argument"]
    assert task["Principal"]["LogonType"] == "Interactive"
    assert mock_res["StartedTasks"] == ["LINHX-Bang"]
