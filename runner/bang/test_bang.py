"""Kiểm thử bảng theo dõi web `runner/bang/` với dữ liệu giả (không gọi mạng, không dùng conftest.py)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import http.client
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import threading
import urllib.error
import urllib.parse
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
        assert "Máy (" in html_body
        assert "Đang chạy (" in html_body
        assert "Đang chờ (" in html_body
        assert "Xong gần nhất (" in html_body
        assert "6 phút" in html_body
        assert "tt-xong" in html_body
        assert "tt-loi" in html_body
        assert "tt-dung" in html_body
        assert 'class="qua-han"' in html_body
        assert "Im lặng &gt; 30 phút" in html_body
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


def test_ui_200_va_cac_khoi_chinh_giao_dien_moi(tmp_path: Path):
    """Kiểm tra trang trả 200 và có đủ các khối chính của giao diện mới (không dùng CDN)."""
    tz_vn = timezone(timedelta(hours=7))
    fixed_now = datetime(2026, 11, 15, 10, 30, 0, tzinfo=tz_vn)

    clone_dir = tmp_path / "bang-ui-moi"
    qroot = clone_dir / "hang-doi"
    for sub in ("moi", "dang", "xong", "can-linh", "may"):
        (qroot / sub).mkdir(parents=True, exist_ok=True)

    # 3 máy chạy (may-1, may-2, may-3) để câu đầu trang là "3 máy chạy, 1 cần anh"
    for idx, may_id in enumerate(("may-1", "may-2", "may-3"), start=1):
        t_claim = (fixed_now - timedelta(minutes=idx * 5)).strftime("%Y-%m-%dT%H:%M:%S%z")
        (qroot / "dang" / f"chay-{idx}.md").write_text(
            f"may: {may_id}\nloai: code\ntran_phut: 40\nnhan: {may_id} {t_claim}\n\n"
            f"Làm việc {idx}\n\nnhip: 10:28 {idx * 5}p Bước kiểm tra {idx}\n",
            encoding="utf-8",
        )

    # may-4 rảnh, may-5 kẹt, may-6 im lặng > 30 phút
    _write_done_ticket(
        qroot,
        ticket_id="xong-ranh",
        machine="may-4",
        status="xong",
        minutes=2.0,
        tok_in=300,
        tok_out=80,
        body="Hoàn thành êm",
        mtime_epoch=(fixed_now - timedelta(minutes=6)).timestamp(),
    )
    _write_done_ticket(
        qroot,
        ticket_id="xong-ket",
        machine="may-5",
        status="dung",
        minutes=12.0,
        tok_in=500,
        tok_out=40,
        body="Cần đăng nhập lại Chrome",
        mtime_epoch=(fixed_now - timedelta(minutes=9)).timestamp(),
    )
    _write_done_ticket(
        qroot,
        ticket_id="xong-im-lang",
        machine="may-6",
        status="xong",
        minutes=1.5,
        tok_in=100,
        tok_out=20,
        body="Xong từ lâu",
        mtime_epoch=(fixed_now - timedelta(minutes=50)).timestamp(),
    )

    (qroot / "moi" / "cho-ui.md").write_text(
        "may: may-2\nloai: code\ntran_phut: 20\n\nPhiếu chờ kiểm tra lọc máy\n",
        encoding="utf-8",
    )

    (qroot / "can-linh" / "xong-ket.md").write_text(
        "may: may-5\nphieu: xong-ket\nviec: Mở Chrome xác thực tài khoản\n"
        "lenh: start chrome https://example.local\ngio: 2026-11-15T10:22:00+07:00\n",
        encoding="utf-8",
    )

    (qroot / "may" / "may-1.json").write_text(
        json.dumps(
            {
                "ma_may": "may-1",
                "ten_windows": "WIN-MAY-1",
                "vai_tro": "Máy giao diện",
                "cpu": {"ten": "Core i5", "nhan": 6, "luong": 12},
                "ram": {"tong_gb": 16.0, "trong_gb": 6.0},
                "gpu": [],
                "o_dia": [{"o": "C:", "tong_gb": 256.0, "trong_gb": 120.0}],
                "agy": {"co": True, "duong_dan": "agy", "phien_ban": "2.1.0"},
                "python": "3.12.0",
                "chrome": {"co": True, "profiles": ["Default"]},
                "nhan_phieu": {"so_phieu": 2, "nhan_bat_ky": True},
                "thong_ke_24h": {"xong": 4, "loi": 0},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    monitor = bang.QueueMonitor(
        clone_dir=clone_dir,
        repo_url="",
        enable_git_sync=False,
        clock_fn=lambda: fixed_now,
    )
    server = bang.create_http_server(monitor, host="127.0.0.1", port=0)
    port = server.server_address[1]
    base_url = f"http://127.0.0.1:{port}"
    srv_thread = threading.Thread(target=server.serve_forever, daemon=True)
    srv_thread.start()
    try:
        for route in ("/", "/phieu", "/may"):
            with urllib.request.urlopen(f"{base_url}{route}", timeout=5) as resp:
                assert resp.status == 200
                body = resp.read().decode("utf-8")
                assert "text/html" in resp.headers.get("Content-Type", "")
                if route == "/":
                    home_html = body

        # 1. Câu trạng thái lớn + khối Cần anh làm đỏ + nút Chép lệnh
        assert 'id="hero-headline"' in home_html
        assert "3 máy chạy, " in home_html and "1 cần anh" in home_html
        assert '<section class="can-linh-box">' in home_html
        assert "btn-copy" in home_html and "Chép lệnh" in home_html
        assert "start chrome https://example.local" in home_html

        # 2. Thẻ máy: tên + vai trò, đủ 4 chấm trạng thái, thanh phút/trần, dòng nhịp, nút mở chi tiết
        assert "Máy giao diện" in home_html
        for dot_cls in ("dot-chay", "dot-ranh", "dot-ket", "dot-im-lang"):
            assert dot_cls in home_html
        assert "progress-track" in home_html and "progress-fill" in home_html
        assert "Bước kiểm tra 1" in home_html
        assert 'data-toggle-may="may-1"' in home_html and 'data-detail-may="may-1"' in home_html

        # 3. Ba tab: Tổng quan · Phiếu (đang/chờ/xong 24h, lọc theo máy) · Máy (hồ sơ năng lực, thanh RAM/ổ)
        assert 'data-tab="tong-quan"' in home_html and "Tổng quan" in home_html
        assert 'data-tab="phieu"' in home_html and "Xong 24h (" in home_html
        assert 'data-filter-may="may-1"' in home_html
        assert 'data-tab="may"' in home_html and "bar-track" in home_html

        # 4. Chuẩn hệ thống, sáng/tối tự động, tự làm mới 15s qua fetch, không CDN ngoài
        assert "-apple-system" in home_html
        assert "prefers-color-scheme: dark" in home_html
        assert "--radius: 16px" in home_html
        assert 'fetch("/api/trang-thai"' in home_html and "15000" in home_html
        assert "cdn." not in home_html.lower()
        assert "googleapis.com" not in home_html.lower()
    finally:
        server.shutdown()
        server.server_close()
        srv_thread.join(timeout=3)


_MINI_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x02\x00\x00\x00\x02"
    b"\x08\x02\x00\x00\x00\xfd\xd4\x9as\x00\x00\x00\x12IDATx\x9cc\xfc\xff\xff?"
    b"\x03\x10\x00\x00\x07\x8c\x01\xf9\x85^\x9f\xdd\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _start_test_server(monitor: bang.QueueMonitor):
    """Khởi chạy server HTTP trên cổng ngẫu nhiên 127.0.0.1:0 cho test."""
    server = bang.create_http_server(monitor, host="127.0.0.1", port=0)
    port = server.server_address[1]
    srv_thread = threading.Thread(target=server.serve_forever, daemon=True)
    srv_thread.start()
    return server, port, srv_thread


def _stop_test_server(server, srv_thread) -> None:
    """Dừng server HTTP test gọn gàng."""
    server.shutdown()
    server.server_close()
    srv_thread.join(timeout=3)


def test_tab_du_an_du_6_trang_thai_va_chi_tiet_buoc(tmp_path: Path):
    """Tab Dự án đặt đầu & mặc định, đủ 6 trạng thái bước, cắt 30 dòng log và 6 ảnh ưu tiên ghep-*.png."""
    tz_vn = timezone(timedelta(hours=7))
    fixed_now = datetime(2026, 11, 15, 10, 0, 0, tzinfo=tz_vn)
    han_dt = fixed_now + timedelta(days=2)

    clone_dir = tmp_path / "bang-du-an"
    qroot = clone_dir / "hang-doi"
    for sub in ("moi", "dang", "xong", "can-linh", "du-an"):
        (qroot / sub).mkdir(parents=True)

    goc_anh = tmp_path / "goc-anh-du-an"
    (goc_anh / "t1-dat" / "bang-chung").mkdir(parents=True)

    # Bước 1 (xong-dat): có "Không xung đột: **ĐẠT**" ở Tiêu chí để kiểm tra không bắt nhầm
    _write_done_ticket(
        qroot,
        "t1-dat",
        "may-1",
        "xong",
        5.5,
        1200,
        300,
        "dat: co\n\n### 6. Tiêu chí\n- Không xung đột với main: **ĐẠT**\n- Pytest: 10/10\n",
    )
    _write_done_ticket(qroot, "cong-b1", "claude", "xong", 1.0, 100, 50, "dat: co\nĐã gộp xong.")

    # Tạo 45 dòng log để kiểm tra cắt đúng 30 dòng cuối
    log_lines = [f"dong-log-{idx:02d} trang-thai ok" for idx in range(1, 46)]
    (goc_anh / "t1-dat" / "chay.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    # Tạo 8 ảnh trong bang-chung: 2 ảnh ghep-*.png cũ hơn vẫn phải được ưu tiên lên đầu (tối đa 6 ảnh)
    base_ts = 1_763_100_000.0
    for idx in range(1, 7):
        fp = goc_anh / "t1-dat" / "bang-chung" / f"khung-{idx:02d}.png"
        fp.write_bytes(_MINI_PNG)
        os.utime(fp, (base_ts + 100 + idx, base_ts + 100 + idx))
    for idx, gname in enumerate(("ghep-390x844.png", "ghep-1440x900.png")):
        gfp = goc_anh / "t1-dat" / "bang-chung" / gname
        gfp.write_bytes(_MINI_PNG)
        os.utime(gfp, (base_ts + idx, base_ts + idx))

    # Bước 2 (xong-khong-dat): kiểm cả chữ hoa KHÔNG ở mục Tiêu chí và trường hợp dat: khong
    _write_done_ticket(
        qroot,
        "t2-loi",
        "may-2",
        "xong",
        7.0,
        1000,
        200,
        "### Tiêu chí\n- Ngưỡng 390px không tràn ngang: **KHÔNG**\n",
    )
    is_dat_tc, _ = bang.analyze_ket_qua_dat({}, "### Tiêu chí\n- Đáp ứng toàn bộ: KHÔNG", "xong")
    assert is_dat_tc is False
    is_dat_meta, _ = bang.analyze_ket_qua_dat({"dat": "khong"}, "Đã chạy", "xong")
    assert is_dat_meta is False

    # Bước 3 (cho-claude): phiếu xong hết nhưng xong/cong-claude chưa có
    _write_done_ticket(qroot, "t3-code", "may-1", "xong", 4.0, 900, 150, "dat: co\nXong phần code.")

    # Bước 4 (dang-chay): đang chạy 14 phút / trần 45 phút + dòng nhịp cuối
    t_run = (fixed_now - timedelta(minutes=14)).strftime("%Y-%m-%dT%H:%M:%S%z")
    (qroot / "dang" / "t4-run.md").write_text(
        f"may: may-1\nloai: trinh-duyet\ntran_phut: 45\nnhan: may-1 {t_run}\n"
        "nhip: Đang chụp ảnh 1440px và kiểm tra A6\n\nKiểm thử bước 4\n",
        encoding="utf-8",
    )

    # Bước 5 (cho-linh): chờ người
    # Bước 6 (cho): phiếu còn nằm trong moi/
    (qroot / "moi" / "t6-cho.md").write_text("may: bat-ky\nloai: code\ntran_phut: 30\n\nĐóng gói RC\n", encoding="utf-8")

    (qroot / "du-an" / "du-an-thu.json").write_text(
        json.dumps(
            {
                "ma": "du-an-thu",
                "ten": "Dự án Yên Lam (Thử)",
                "han": han_dt.isoformat(timespec="seconds"),
                "goc_anh": str(goc_anh),
                "buoc": [
                    {"ma": "b1", "ten": "Xây nền", "phieu": ["t1-dat"], "cong": "cong-b1"},
                    {"ma": "b2", "ten": "Đo tiêu chí", "phieu": ["t2-loi"]},
                    {"ma": "b3", "ten": "Chờ cổng Claude", "phieu": ["t3-code"], "cong": "cong-claude"},
                    {"ma": "b4", "ten": "Kiểm thử chạy", "phieu": ["t4-run"]},
                    {"ma": "b5", "ten": "Linh duyệt UI", "nguoi": "Linh", "phieu": []},
                    {"ma": "b6", "ten": "Đóng gói cuối", "phieu": ["t6-cho"]},
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    monitor = bang.QueueMonitor(
        clone_dir=clone_dir,
        repo_url="",
        enable_git_sync=False,
        clock_fn=lambda: fixed_now,
    )
    snap = monitor.get_status()
    assert len(snap["du_an"]) == 1
    da = snap["du_an"][0]
    assert da["ten"] == "Dự án Yên Lam (Thử)"
    assert da["qua_han"] is False
    assert "2 ngày" in da["han_con_lai"]
    assert da["tom_tat_buoc"] == "Đang ở bước b4 (Kiểm thử chạy), việc tiếp theo b5 (Linh duyệt UI)"

    statuses = [s["trang_thai"] for s in da["buoc"]]
    assert statuses == ["xong-dat", "xong-khong-dat", "cho-claude", "dang-chay", "cho-linh", "cho"]

    step_b1 = da["buoc"][0]
    assert len(step_b1["log_cuoi"]) == 30
    assert "dong-log-16" in step_b1["log_cuoi"][0]
    assert "dong-log-45" in step_b1["log_cuoi"][-1]
    assert all("dong-log-15" not in line for line in step_b1["log_cuoi"])
    assert len(step_b1["anh_thu_nho"]) == 6
    assert step_b1["anh_thu_nho"][0]["ten"].startswith("ghep-")
    assert step_b1["anh_thu_nho"][1]["ten"].startswith("ghep-")
    assert step_b1["ket_qua_list"][0]["dat"] is True

    step_b4 = da["buoc"][3]
    assert step_b4["phieu_dang_chay"] == "t4-run"
    assert int(round(step_b4["chay_phut"])) == 14
    assert step_b4["tran_phut"] == 45
    assert "Đang chụp ảnh 1440px" in step_b4["nhip_cuoi"]

    html = bang.render_dashboard_html(snap)
    assert 'data-initial-tab="du-an"' in html
    assert html.index('data-tab="du-an"') < html.index('data-tab="chat-luong"')
    assert html.index('data-tab="chat-luong"') < html.index('data-tab="tong-quan"')
    assert 'id="panel-du-an" data-panel="du-an" role="tabpanel">' in html
    assert 'id="panel-chat-luong" data-panel="chat-luong" role="tabpanel" hidden>' in html
    for cls_dot in (
        "dot-buoc-xong-dat",
        "dot-buoc-xong-khong-dat",
        "dot-buoc-cho-claude",
        "dot-buoc-dang-chay",
        "dot-buoc-cho-linh",
        "dot-buoc-cho",
    ):
        assert cls_dot in html
    assert "14 phút / 45p" in html
    assert "dong-log-45" in html
    assert "/tep?p=" in html


def test_route_tep_bao_mat_va_phuc_vu_anh(tmp_path: Path):
    """Route /tep chỉ GET, phục vụ file hợp lệ dưới goc_anh, chặn .., ngoài gốc, ổ khác, symlink và đuôi lạ."""
    clone_dir = tmp_path / "bang-tep"
    qroot = clone_dir / "hang-doi"
    (qroot / "du-an").mkdir(parents=True)

    goc_anh = tmp_path / "goc_anh"
    goc_ngoai = tmp_path / "goc_anh_ngoai"
    (goc_anh / "sub").mkdir(parents=True)
    goc_ngoai.mkdir(parents=True)

    ok_png = goc_anh / "sub" / "ok.png"
    ok_png.write_bytes(_MINI_PNG)
    ok_log = goc_anh / "sub" / "run.log"
    ok_log.write_text("nhip: ok\n", encoding="utf-8")
    ok_json = goc_anh / "sub" / "do-muc-9.json"
    ok_json.write_text('[{"ma":"A6-01","dat":true}]', encoding="utf-8")

    bad_ext = goc_anh / "sub" / "hack.py"
    bad_ext.write_text("print('khong duoc doc')", encoding="utf-8")

    oversized = goc_anh / "sub" / "qua-lon.log"
    with open(oversized, "wb") as fp:
        fp.seek(bang.MAX_TEP_BYTES + 128)
        fp.write(b"x")

    outside_png = goc_ngoai / "bi-mat.png"
    outside_png.write_bytes(_MINI_PNG)

    # Tạo junction/symlink trỏ từ bên trong goc_anh ra thư mục ngoài gốc để kiểm tra chặn thoát gốc
    link_dir = goc_anh / "cau-noi"
    link_created = False
    if os.name == "nt":
        proc = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link_dir), str(goc_ngoai)],
            capture_output=True,
            text=True,
            creationflags=0x08000000,
        )
        link_created = proc.returncode == 0
    else:
        try:
            os.symlink(goc_ngoai, link_dir, target_is_directory=True)
            link_created = True
        except OSError:
            link_created = False

    (qroot / "du-an" / "p1.json").write_text(
        json.dumps({"ma": "p1", "ten": "P1", "goc_anh": str(goc_anh), "buoc": []}, ensure_ascii=False),
        encoding="utf-8",
    )

    monitor = bang.QueueMonitor(clone_dir=clone_dir, repo_url="", enable_git_sync=False)
    server, port, srv_thread = _start_test_server(monitor)
    try:
        def _req(method: str, target_url: str):
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
            try:
                conn.request(method, target_url)
                resp = conn.getresponse()
                data = resp.read()
                return resp.status, dict(resp.getheaders()), data
            finally:
                conn.close()

        # 1. Phục vụ đúng ảnh .png, .log, .json trong gốc
        st, hdrs, body = _req("GET", f"/tep?p={urllib.parse.quote(str(ok_png), safe='')}")
        assert st == 200
        assert body == _MINI_PNG
        assert hdrs.get("Content-Type") == "image/png"
        assert hdrs.get("X-Content-Type-Options") == "nosniff"

        st_log, hdrs_log, body_log = _req("GET", f"/tep?p={urllib.parse.quote(str(ok_log), safe='')}")
        assert st_log == 200
        assert "text/plain" in (hdrs_log.get("Content-Type") or "")
        assert b"nhip: ok" in body_log

        st_json, hdrs_json, _ = _req("GET", f"/tep?p={urllib.parse.quote(str(ok_json), safe='')}")
        assert st_json == 200
        assert "application/json" in (hdrs_json.get("Content-Type") or "")

        # 2. Chặn thiếu p / file không tồn tại / vượt 20MB
        assert _req("GET", "/tep")[0] == 400
        assert _req("GET", f"/tep?p={urllib.parse.quote(str(goc_anh / 'sub' / 'khong-co.png'), safe='')}")[0] == 404
        assert _req("GET", f"/tep?p={urllib.parse.quote(str(oversized), safe='')}")[0] == 413

        # 3. Chặn leo thư mục .. (thô và mã hóa), ngoài gốc cùng tiền tố, ổ khác, đường dẫn tương đối, đuôi lạ
        trav_raw = str(goc_anh / "sub" / ".." / ".." / "goc_anh_ngoai" / "bi-mat.png")
        assert _req("GET", f"/tep?p={urllib.parse.quote(trav_raw, safe='')}")[0] == 403
        assert _req("GET", f"/tep?p={urllib.parse.quote(str(goc_anh), safe='')}%2F%2e%2e%2Fbi-mat.png")[0] == 403
        assert _req("GET", f"/tep?p={urllib.parse.quote(str(outside_png), safe='')}")[0] == 403
        assert _req("GET", f"/tep?p={urllib.parse.quote('Z:\\o-khac\\anh.png', safe='')}")[0] == 403
        assert _req("GET", "/tep?p=sub%2Fok.png")[0] == 403
        assert _req("GET", f"/tep?p={urllib.parse.quote(str(bad_ext), safe='')}")[0] == 403
        if link_created:
            via_link = goc_anh / "cau-noi" / "bi-mat.png"
            assert _req("GET", f"/tep?p={urllib.parse.quote(str(via_link), safe='')}")[0] == 403

        # 4. Chỉ GET trên /tep (HEAD/POST/DELETE/OPTIONS đều 405)
        ok_q = f"/tep?p={urllib.parse.quote(str(ok_png), safe='')}"
        for blocked_method in ("HEAD", "POST", "DELETE", "OPTIONS"):
            assert _req(blocked_method, ok_q)[0] == 405
    finally:
        _stop_test_server(server, srv_thread)


def test_tab_chat_luong_chua_do_va_du_lieu_day_du(tmp_path: Path):
    """Tab Chất lượng hiện 'Chưa đo' khi thiếu file và đọc đúng file do-muc-9 mới nhất + ảnh ghép + bảng chấm."""
    tz_vn = timezone(timedelta(hours=7))
    fixed_now = datetime(2026, 11, 15, 11, 0, 0, tzinfo=tz_vn)

    clone_dir = tmp_path / "bang-cl"
    qroot = clone_dir / "hang-doi"
    (qroot / "du-an").mkdir(parents=True)

    goc_anh = tmp_path / "goc-cl"
    (goc_anh / "phieu-rc1" / "bang-chung").mkdir(parents=True)
    (goc_anh / "luu").mkdir(parents=True)

    du_an_json = qroot / "du-an" / "cl.json"
    du_an_json.write_text(
        json.dumps(
            {
                "ma": "cl-test",
                "ten": "Dự án Chất lượng",
                "goc_anh": str(goc_anh),
                "buoc": [],
                "chat_luong": {
                    "do_muc_9": str(goc_anh / "**" / "do-muc-9*.json"),
                    "anh_ghep": str(goc_anh / "**" / "ghep-*.png"),
                    "cham": [],
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    monitor = bang.QueueMonitor(
        clone_dir=clone_dir,
        repo_url="",
        enable_git_sync=False,
        clock_fn=lambda: fixed_now,
    )
    snap_empty = monitor.get_status()
    dm9_empty = snap_empty["du_an"][0]["chat_luong"]["do_muc_9"]
    assert dm9_empty["chua_do"] is True
    assert dm9_empty["chi_so"] == []
    html_empty = bang.render_quality_html(snap_empty)
    assert "Chưa đo" in html_empty
    assert "Chưa có ảnh ghép" in html_empty
    assert "Chưa có dữ liệu chấm" in html_empty

    # Bổ sung 2 file do-muc-9 cũ và mới -> phải chọn file mới hơn với đủ 7 chỉ số
    old_m9 = goc_anh / "luu" / "do-muc-9-cu.json"
    old_m9.write_text(
        json.dumps([{"ma": "A6-01", "ten": "Số cũ", "nguong": "<= 1", "te_nhat": "99", "dat": False}]),
        encoding="utf-8",
    )
    os.utime(old_m9, (1_763_100_000.0, 1_763_100_000.0))

    metrics_7 = [
        {"ma": "A6-01", "ten": "Tràn ngang 390px", "nguong": "0 px", "te_nhat": "0 px", "dat": True},
        {"ma": "A6-02", "ten": "Độ cao đường chân", "nguong": "<= 64 px", "te_nhat": "58 px", "dat": True},
        {"ma": "A6-03", "ten": "Khoảng cách nút", "nguong": ">= 8 px", "te_nhat": "10 px", "dat": True},
        {"ma": "A6-04", "ten": "Tương phản chữ", "nguong": ">= 4.5", "te_nhat": "5.1", "dat": True},
        {"ma": "A6-05", "ten": "Ảnh lỗi nứt", "nguong": "0", "te_nhat": "0", "dat": True},
        {"ma": "A6-06", "ten": "Chữ bị cắt góc", "nguong": "0", "te_nhat": "2", "dat": False},
        {"ma": "A6-07", "ten": "Thời gian vẽ khung", "nguong": "<= 150 ms", "te_nhat": "92 ms", "dat": True},
    ]
    new_m9 = goc_anh / "luu" / "do-muc-9-moi.json"
    new_m9.write_text(json.dumps(metrics_7, ensure_ascii=False), encoding="utf-8")
    os.utime(new_m9, (1_763_200_000.0, 1_763_200_000.0))

    ghep_fp = goc_anh / "phieu-rc1" / "bang-chung" / "ghep-so-sanh.png"
    ghep_fp.write_bytes(_MINI_PNG)
    cham_log = goc_anh / "cham-rc2.txt"
    cham_log.write_text("Nhan xet rc2\n", encoding="utf-8")

    du_an_json.write_text(
        json.dumps(
            {
                "ma": "cl-test",
                "ten": "Dự án Chất lượng",
                "goc_anh": str(goc_anh),
                "buoc": [],
                "chat_luong": {
                    "do_muc_9": str(goc_anh / "**" / "do-muc-9*.json"),
                    "anh_ghep": str(goc_anh / "**" / "ghep-*.png"),
                    "cham": [
                        {
                            "rc": "rc-2",
                            "nguoi": "Linh",
                            "diem": "8.5/10",
                            "ghi_chu": "Khớp khung chuẩn",
                            "tep": str(cham_log),
                        }
                    ],
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    snap_full = monitor.get_status()
    cl_full = snap_full["du_an"][0]["chat_luong"]
    assert cl_full["do_muc_9"]["chua_do"] is False
    assert cl_full["do_muc_9"]["tep"] == "do-muc-9-moi.json"
    assert len(cl_full["do_muc_9"]["chi_so"]) == 7
    assert cl_full["anh_ghep"][0]["phieu"] == "phieu-rc1"
    assert cl_full["cham"][0]["rc"] == "rc-2"
    assert cl_full["cham"][0]["tep_url"].startswith("/tep?p=")

    server, port, srv_thread = _start_test_server(monitor)
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/chat-luong", timeout=5) as resp:
            assert resp.status == 200
            html_cl = resp.read().decode("utf-8")
        assert "A6-06" in html_cl and "Chữ bị cắt góc" in html_cl and "Đỏ" in html_cl
        assert "Đạt" in html_cl
        assert "phieu-rc1" in html_cl
        assert "rc-2" in html_cl and "8.5/10" in html_cl and "Khớp khung chuẩn" in html_cl
        assert 'data-panel="chat-luong" role="tabpanel">' in html_cl
    finally:
        _stop_test_server(server, srv_thread)


def _write_done_ticket_with_times(
    qroot: Path,
    ticket_id: str,
    machine: str,
    status: str,
    nhan_iso: str,
    xong_iso: str,
    body: str,
) -> Path:
    """Tạo file giả `hang-doi/xong/<id>/KET-QUA.md` có rõ giờ nhận và giờ xong."""
    t_dir = qroot / "xong" / ticket_id
    t_dir.mkdir(parents=True, exist_ok=True)
    kq = t_dir / "KET-QUA.md"
    kq.write_text(
        f"may: {machine}\ntrang_thai: {status}\nnhan_luc: {nhan_iso}\nxong_luc: {xong_iso}\n"
        f"phut: 10\ntoken: vao=500 ra=120\ntep_doi: (khong)\ndrive: (khong)\n\n{body}\n",
        encoding="utf-8",
    )
    return kq


def test_gantt_thanh_thuc_te_dung_gio_va_keo_toi_hien_tai(tmp_path: Path):
    """Thanh thực tế kéo từ giờ nhận phiếu đầu đến giờ xong phiếu cuối (đang chạy kéo tới now), vạch giờ/hạn & câu ETA."""
    tz_vn = timezone(timedelta(hours=7))
    fixed_now = datetime(2026, 11, 15, 13, 30, 0, tzinfo=tz_vn)
    han_dt = datetime(2026, 11, 15, 16, 0, 0, tzinfo=tz_vn)

    clone_dir = tmp_path / "bang-gantt"
    qroot = clone_dir / "hang-doi"
    for sub in ("moi", "dang", "xong", "can-linh", "du-an"):
        (qroot / sub).mkdir(parents=True)

    # Bước b1: xong gồm 2 phiếu (11:02->11:25 và 11:30->11:50), dự kiến 11:00->12:00
    _write_done_ticket_with_times(
        qroot, "g-b1-p1", "may-1", "xong",
        "2026-11-15T11:02:00+07:00", "2026-11-15T11:25:00+07:00", "dat: co\nXong phần đầu.",
    )
    _write_done_ticket_with_times(
        qroot, "g-b1-p2", "may-2", "xong",
        "2026-11-15T11:30:00+07:00", "2026-11-15T11:50:00+07:00", "dat: co\nXong phần cuối.",
    )

    # Bước b2: đang chạy từ 12:15 (hiện tại 13:30), dự kiến 12:10->14:40
    (qroot / "dang" / "g-b2-run.md").write_text(
        "may: may-1\nloai: code\ntran_phut: 120\nnhan: may-1 2026-11-15T12:15:00+07:00\n"
        "nhip: Đang dựng bảng GANTT\n\nTriển khai UI\n",
        encoding="utf-8",
    )

    # Bước b3: đang chờ trong moi/, dự kiến 14:00->15:00
    (qroot / "moi" / "g-b3-cho.md").write_text(
        "may: bat-ky\nloai: code\ntran_phut: 30\n\nKiểm tra cuối\n",
        encoding="utf-8",
    )

    # Dự án 1 (trễ 5 phút ở bước đang chạy)
    (qroot / "du-an" / "da-gantt.json").write_text(
        json.dumps(
            {
                "ma": "da-gantt",
                "ten": "Dự án GANTT Chính",
                "han": han_dt.isoformat(timespec="seconds"),
                "buoc": [
                    {
                        "ma": "B1",
                        "ten": "Khởi tạo",
                        "phieu": ["g-b1-p1", "g-b1-p2"],
                        "du_kien": {"bat_dau": "2026-11-15T11:00:00+07:00", "xong": "2026-11-15T12:00:00+07:00"},
                    },
                    {
                        "ma": "B2",
                        "ten": "Dựng giao diện",
                        "phieu": ["g-b2-run"],
                        "du_kien": {"bat_dau": "2026-11-15T12:10:00+07:00", "xong": "2026-11-15T14:40:00+07:00"},
                    },
                    {
                        "ma": "B3",
                        "ten": "Chốt phát hành",
                        "phieu": ["g-b3-cho"],
                        "du_kien": {"bat_dau": "2026-11-15T14:00:00+07:00", "xong": "2026-11-15T15:00:00+07:00"},
                    },
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # Dự án 2 (xong sớm 30 phút để kiểm công thức sớm N phút)
    _write_done_ticket_with_times(
        qroot, "g-som-p1", "may-1", "xong",
        "2026-11-15T11:00:00+07:00", "2026-11-15T12:30:00+07:00", "dat: co\nXong sớm.",
    )
    (qroot / "du-an" / "da-som.json").write_text(
        json.dumps(
            {
                "ma": "da-som",
                "ten": "Dự án Xong Sớm",
                "han": han_dt.isoformat(timespec="seconds"),
                "buoc": [
                    {
                        "ma": "S1",
                        "ten": "Làm nhanh",
                        "phieu": ["g-som-p1"],
                        "du_kien": {"bat_dau": "2026-11-15T11:00:00+07:00", "xong": "2026-11-15T13:00:00+07:00"},
                    },
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    monitor = bang.QueueMonitor(
        clone_dir=clone_dir,
        repo_url="",
        enable_git_sync=False,
        clock_fn=lambda: fixed_now,
    )
    snap = monitor.get_status()
    da1 = next(d for d in snap["du_an"] if d["ma"] == "da-gantt")
    da2 = next(d for d in snap["du_an"] if d["ma"] == "da-som")

    assert da1["du_kien_xong_cau"] == "Dự kiến xong 15:05 (trễ 5 phút)"
    assert da2["du_kien_xong_cau"] == "Dự kiến xong 12:30 (sớm 30 phút)"

    truc = da1["gantt_truc"]
    ax_s = bang.parse_iso_datetime(truc["bat_dau"])
    ax_e = bang.parse_iso_datetime(truc["xong"])
    span = (ax_e - ax_s).total_seconds()
    assert ax_s <= datetime(2026, 11, 15, 10, 45, 0, tzinfo=tz_vn)
    assert ax_e >= datetime(2026, 11, 15, 16, 15, 0, tzinfo=tz_vn)
    assert truc["han_co"] is True
    assert truc["hien_tai_gio"] == "13:30"

    b1 = da1["buoc"][0]
    assert b1["du_kien_gio"] == "11:00–12:00"
    assert b1["thuc_te_gio"] == "11:02–11:50"
    assert b1["bi_tre"] is False
    assert b1["gantt"]["co_du_kien"] is True and b1["gantt"]["co_thuc_te"] is True
    exp_b1_start_pct = ((datetime(2026, 11, 15, 11, 2, tzinfo=tz_vn) - ax_s).total_seconds() / span) * 100.0
    exp_b1_end_pct = ((datetime(2026, 11, 15, 11, 50, tzinfo=tz_vn) - ax_s).total_seconds() / span) * 100.0
    assert abs(b1["gantt"]["tt_start_pct_raw"] - exp_b1_start_pct) < 0.05
    assert abs(b1["gantt"]["tt_end_pct_raw"] - exp_b1_end_pct) < 0.05

    b2 = da1["buoc"][1]
    assert b2["du_kien_gio"] == "12:10–14:40"
    assert b2["thuc_te_gio"] == "12:15–…"
    assert b2["thuc_te_dang_chay"] is True
    exp_b2_start_pct = ((datetime(2026, 11, 15, 12, 15, tzinfo=tz_vn) - ax_s).total_seconds() / span) * 100.0
    assert abs(b2["gantt"]["tt_start_pct_raw"] - exp_b2_start_pct) < 0.05
    assert abs(b2["gantt"]["tt_end_pct_raw"] - truc["hien_tai_pct"]) < 0.05

    server, port, srv_thread = _start_test_server(monitor)
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=5) as resp:
            assert resp.status == 200
            html = resp.read().decode("utf-8")
        assert "Dự kiến xong 15:05 (trễ 5 phút)" in html
        assert "Dự kiến xong 12:30 (sớm 30 phút)" in html
        assert "12:10–14:40" in html and "12:15–…" in html
        assert "gantt-bar-dk" in html and "gantt-bar-tt" in html
        assert "gantt-vline-now" in html and "gantt-vline-han" in html
        assert "kanban" not in html.lower()
    finally:
        _stop_test_server(server, srv_thread)


def test_gantt_buoc_tre_tren_15_phut_to_cam_va_ranh_gioi_15p(tmp_path: Path):
    """Bước trễ đúng 15p chưa tô cam; bước trễ > 15p tô cam, hiện 'trễ N phút' và gắn is-step-late."""
    tz_vn = timezone(timedelta(hours=7))
    fixed_now = datetime(2026, 11, 15, 13, 0, 0, tzinfo=tz_vn)

    clone_dir = tmp_path / "bang-tre"
    qroot = clone_dir / "hang-doi"
    for sub in ("moi", "dang", "xong", "can-linh", "du-an"):
        (qroot / sub).mkdir(parents=True)

    # S1: trễ đúng 15 phút -> KHÔNG tô cam
    _write_done_ticket_with_times(
        qroot, "tre-15", "may-1", "xong",
        "2026-11-15T10:00:00+07:00", "2026-11-15T11:15:00+07:00", "dat: co\nĐủ ranh giới 15p.",
    )
    # S2: xong trễ 16 phút -> TÔ CAM
    _write_done_ticket_with_times(
        qroot, "tre-16", "may-1", "xong",
        "2026-11-15T11:00:00+07:00", "2026-11-15T12:16:00+07:00", "dat: co\nQuá ranh giới 1p.",
    )
    # S3: đang chạy quá hạn dự kiến xong 25 phút -> TÔ CAM
    (qroot / "dang" / "tre-25.md").write_text(
        "may: may-2\nloai: code\ntran_phut: 90\nnhan: may-2 2026-11-15T11:30:00+07:00\n"
        "nhip: Vẫn đang chạy\n\nKiểm tra bước trễ\n",
        encoding="utf-8",
    )

    (qroot / "du-an" / "da-tre.json").write_text(
        json.dumps(
            {
                "ma": "da-tre",
                "ten": "Dự án Kiểm Trễ",
                "buoc": [
                    {
                        "ma": "S1",
                        "ten": "Đúng 15p",
                        "phieu": ["tre-15"],
                        "du_kien": {"bat_dau": "2026-11-15T10:00:00+07:00", "xong": "2026-11-15T11:00:00+07:00"},
                    },
                    {
                        "ma": "S2",
                        "ten": "Vượt 16p",
                        "phieu": ["tre-16"],
                        "du_kien": {"bat_dau": "2026-11-15T11:00:00+07:00", "xong": "2026-11-15T12:00:00+07:00"},
                    },
                    {
                        "ma": "S3",
                        "ten": "Đang chạy trễ 25p",
                        "phieu": ["tre-25"],
                        "du_kien": {"bat_dau": "2026-11-15T11:30:00+07:00", "xong": "2026-11-15T12:35:00+07:00"},
                    },
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    monitor = bang.QueueMonitor(
        clone_dir=clone_dir,
        repo_url="",
        enable_git_sync=False,
        clock_fn=lambda: fixed_now,
    )
    snap = monitor.get_status()
    steps = snap["du_an"][0]["buoc"]
    assert steps[0]["bi_tre"] is False and steps[0]["tre_nhan"] == ""
    assert steps[1]["bi_tre"] is True and steps[1]["tre_nhan"] == "trễ 16 phút"
    assert steps[2]["bi_tre"] is True and steps[2]["tre_nhan"] == "trễ 25 phút"

    html = bang.render_dashboard_html(snap)
    assert "is-step-late" in html
    assert "badge-step-late" in html
    assert "gantt-bar-tt st-dang-chay is-late" in html
    assert "trễ 16 phút" in html
    assert "trễ 25 phút" in html
    assert "trễ 15 phút" not in html


def test_gantt_thieu_du_kien_khong_vo(tmp_path: Path):
    """Thiếu trường du_kien, null, rỗng, thiếu nửa đầu/cuối hoặc chuỗi giờ sai không làm vỡ server."""
    tz_vn = timezone(timedelta(hours=7))
    fixed_now = datetime(2026, 11, 15, 14, 0, 0, tzinfo=tz_vn)

    clone_dir = tmp_path / "bang-thieu"
    qroot = clone_dir / "hang-doi"
    for sub in ("moi", "dang", "xong", "can-linh", "du-an"):
        (qroot / sub).mkdir(parents=True)

    _write_done_ticket_with_times(
        qroot, "ok-1", "may-1", "xong",
        "2026-11-15T12:00:00+07:00", "2026-11-15T12:40:00+07:00", "dat: co\nOK.",
    )
    (qroot / "du-an" / "da-thieu.json").write_text(
        json.dumps(
            {
                "ma": "da-thieu",
                "ten": "Dự án Thiếu Dự Kiến",
                "buoc": [
                    {"ma": "M1", "ten": "Không có du_kien", "phieu": ["ok-1"]},
                    {"ma": "M2", "ten": "du_kien null", "phieu": [], "du_kien": None},
                    {"ma": "M3", "ten": "du_kien rỗng", "phieu": [], "du_kien": {}},
                    {"ma": "M4", "ten": "Chỉ có bắt đầu", "phieu": [], "du_kien": {"bat_dau": "2026-11-15T13:00:00+07:00"}},
                    {"ma": "M5", "ten": "Chuỗi hỏng", "phieu": [], "du_kien": {"bat_dau": "khong-hop-le", "xong": "sai"}},
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    monitor = bang.QueueMonitor(
        clone_dir=clone_dir,
        repo_url="",
        enable_git_sync=False,
        clock_fn=lambda: fixed_now,
    )
    snap = monitor.get_status()
    da = snap["du_an"][0]
    assert da["du_kien_xong_cau"] == ""
    assert da["buoc"][0]["du_kien_gio"] == "—"
    assert da["buoc"][0]["thuc_te_gio"] == "12:00–12:40"
    assert da["buoc"][0]["gantt"]["co_du_kien"] is False
    assert da["buoc"][0]["gantt"]["co_thuc_te"] is True
    assert da["buoc"][3]["du_kien_gio"] == "13:00–?"
    assert da["buoc"][4]["du_kien_gio"] == "—"

    server, port, srv_thread = _start_test_server(monitor)
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=5) as resp:
            assert resp.status == 200
            html = resp.read().decode("utf-8")
        assert "Dự án Thiếu Dự Kiến" in html
        assert "Không có du_kien" in html
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/trang-thai", timeout=5) as api_resp:
            assert api_resp.status == 200
            payload = json.loads(api_resp.read().decode("utf-8"))
        assert len(payload["du_an"][0]["buoc"]) == 5
    finally:
        _stop_test_server(server, srv_thread)


def test_gantt_suy_gio_thuc_te_tu_phut_va_mtime_ket_qua(tmp_path: Path):
    """Định dạng KET-QUA.md thật (chỉ có phut + mtime, không có nhan_luc/xong_luc) và dự án dài ngày không vỡ trục."""
    tz_vn = timezone(timedelta(hours=7))
    fixed_now = datetime(2026, 11, 15, 13, 30, 0, tzinfo=tz_vn)

    clone_dir = tmp_path / "bang-mtime"
    qroot = clone_dir / "hang-doi"
    for sub in ("moi", "dang", "xong", "can-linh", "du-an"):
        (qroot / sub).mkdir(parents=True)

    # Phiếu 1: xong lúc 10:40, chạy 20 phút => suy ra bắt đầu 10:20
    t1_end = datetime(2026, 11, 15, 10, 40, 0, tzinfo=tz_vn)
    _write_done_ticket(
        qroot, "real-p1", "may-1", "xong",
        minutes=20.0, tok_in=100, tok_out=50,
        body="dat: co\nXong phiếu 1.",
        mtime_epoch=t1_end.timestamp(),
    )
    # Phiếu 2: xong lúc 11:05, chạy 15 phút => suy ra bắt đầu 10:50
    t2_end = datetime(2026, 11, 15, 11, 5, 0, tzinfo=tz_vn)
    _write_done_ticket(
        qroot, "real-p2", "may-2", "xong",
        minutes=15.0, tok_in=120, tok_out=60,
        body="dat: co\nXong phiếu 2.",
        mtime_epoch=t2_end.timestamp(),
    )

    (qroot / "du-an" / "da-dai-ngay.json").write_text(
        json.dumps(
            {
                "ma": "da-dai-ngay",
                "ten": "Dự án Dài Ngày",
                "buoc": [
                    {
                        "ma": "B1",
                        "ten": "Gom số liệu mtime",
                        "phieu": ["real-p1", "real-p2"],
                        "du_kien": {
                            "bat_dau": "2026-11-15T10:15:00+07:00",
                            "xong": "2026-11-15T11:15:00+07:00",
                        },
                    },
                    {
                        "ma": "B2",
                        "ten": "Nghiệm thu cuối tuần",
                        "phieu": [],
                        "du_kien": {
                            "bat_dau": "2026-11-20T16:00:00+07:00",
                            "xong": "2026-11-20T18:00:00+07:00",
                        },
                    },
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    monitor = bang.QueueMonitor(
        clone_dir=clone_dir,
        repo_url="",
        enable_git_sync=False,
        clock_fn=lambda: fixed_now,
    )
    snap = monitor.get_status()
    da = snap["du_an"][0]
    b1 = da["buoc"][0]
    assert b1["thuc_te_gio"] == "10:20–11:05"
    assert b1["gantt"]["co_thuc_te"] is True
    assert b1["gantt"]["tt_end_pct_raw"] > b1["gantt"]["tt_start_pct_raw"]
    assert 1 <= len(da["gantt_truc"]["moc_gio"]) <= 10

    html = bang.render_dashboard_html(snap)
    assert "10:20–11:05" in html
    assert "Dự án Dài Ngày" in html




