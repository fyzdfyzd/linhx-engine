from __future__ import annotations

from datetime import datetime, timedelta, timezone
import io
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import time
import urllib.request
import uuid

import pytest

from runner import hang_doi_git, ho_so_may, linhx_runner
from runner._gia_moi_truong import _gia_ram_va_moi_truong_h3  # noqa: F401
from runner.bang import bang


def _xoa_thu_muc(duong_dan: Path) -> None:
    if not duong_dan.exists():
        return

    def _xu_ly_loi(fn, p, _):
        try:
            os.chmod(p, stat.S_IWRITE)
            fn(p)
        except OSError:
            pass

    shutil.rmtree(duong_dan, onerror=_xu_ly_loi)


@pytest.fixture
def tmp_path():
    # Dùng thư mục tạm bên trong runner/viec (đã gitignore) theo chuẩn của bộ test runner/
    goc_viec = linhx_runner.GOC / "viec"
    viec_da_co = goc_viec.exists()
    tm_goc = goc_viec / f"pytest-tmp-nhip-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    tm_goc.mkdir(parents=True, exist_ok=True)
    try:
        yield tm_goc
    finally:
        _xoa_thu_muc(tm_goc)
        if not viec_da_co and goc_viec.exists():
            try:
                next(goc_viec.iterdir())
            except StopIteration:
                goc_viec.rmdir()


def _git(args: list[str], cwd: Path) -> str:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    kw = {"creationflags": 0x08000000} if os.name == "nt" else {}
    p = subprocess.run(
        ["git"] + list(args),
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        **kw,
    )
    return p.stdout.strip()


def _tao_bare_hang_doi(tmp_path: Path, phieu_moi: dict[str, str] | None = None) -> Path:
    bare = tmp_path / "remote.git"
    bare.mkdir(parents=True)
    _git(["init", "--bare"], bare)

    seed = tmp_path / "seed"
    seed.mkdir()
    _git(["init"], seed)
    _git(["config", "user.name", "seed"], seed)
    _git(["config", "user.email", "seed@linhx.local"], seed)
    _git(["config", "commit.gpgsign", "false"], seed)
    _git(["checkout", "-b", "main"], seed)
    (seed / "README.md").write_text("linhx-engine\n", encoding="utf-8")
    _git(["add", "-A"], seed)
    _git(["commit", "-m", "init main"], seed)
    _git(["remote", "add", "origin", str(bare)], seed)
    _git(["push", "origin", "main"], seed)
    _git(["symbolic-ref", "HEAD", "refs/heads/main"], bare)

    _git(["checkout", "--orphan", "hang-doi"], seed)
    _git(["rm", "-rf", "."], seed)
    tm_moi = seed / "hang-doi" / "moi"
    tm_moi.mkdir(parents=True, exist_ok=True)
    (tm_moi / ".gitkeep").write_text("", encoding="utf-8")
    for ten, nd in (phieu_moi or {}).items():
        (tm_moi / f"{ten}.md").write_text(nd, encoding="utf-8")
    _git(["add", "-A"], seed)
    _git(["commit", "-m", "init hang-doi"], seed)
    _git(["push", "origin", "hang-doi"], seed)
    return bare


def _clone_may(bare: Path, tmp_path: Path, ten_may: str, **them_cfg) -> dict:
    tm_clone = tmp_path / f"repo-{ten_may}-{uuid.uuid4().hex[:4]}"
    _git(["clone", str(bare), str(tm_clone)], tmp_path)
    tm_viec = tmp_path / f"viec-{ten_may}"
    tm_viec.mkdir(parents=True, exist_ok=True)
    cfg = {
        "nguon": "github",
        "tho": ten_may,
        "agy": "agy-gia",
        "agy_args": "--output-format json",
        "thu_muc": tm_viec,
        "nghi": 0.01,
        "repo_hang_doi": tm_clone,
        "nhanh_hang_doi": "hang-doi",
        "remote_hang_doi": "origin",
        "wt_hang_doi": "",
        "thu_muc_drive": tmp_path / f"drive-{ten_may}",
        "thu_muc_log": tmp_path / f"log-{ten_may}",
    }
    cfg.update(them_cfg)
    return cfg


def _kiem_tra_hang_doi(bare: Path, tmp_path: Path, nhan: str = "kt") -> Path:
    tm = tmp_path / nhan
    if tm.exists():
        _git(["fetch", "origin", "hang-doi"], tm)
        _git(["reset", "--hard", "origin/hang-doi"], tm)
    else:
        _git(["clone", "-b", "hang-doi", str(bare), str(tm)], tmp_path)
    return tm


class _OngDong:
    """Pipe giả cho phép bơm dần các dòng stdout của agy theo từng bước thời gian."""

    def __init__(self):
        self._hang: list[bytes] = []
        self._dong = False

    def them(self, du_lieu: bytes) -> None:
        self._hang.append(du_lieu)

    def ket_thuc(self) -> None:
        self._dong = True

    def read(self, _kich_thuoc: int = 4096) -> bytes:
        while not self._hang and not self._dong:
            time.sleep(0.005)
        if self._hang:
            return self._hang.pop(0)
        return b""

    def close(self) -> None:
        self._dong = True


class _TienTrinhAgyTheoBuoc:
    """Tiến trình Popen giả phục vụ kiểm tra ghi nhịp mỗi 3 phút trong lúc agy đang chạy."""

    def __init__(self):
        self.pid = 60606
        self.returncode = None
        self.stdout = _OngDong()
        self.stderr = io.BytesIO(b"")

    def poll(self):
        return self.returncode

    def hoan_tat(self, ma: int = 0) -> None:
        self.returncode = ma
        self.stdout.ket_thuc()

    def kill(self) -> None:
        self.returncode = -9
        self.stdout.ket_thuc()

    def wait(self, timeout=None):
        if self.returncode is None:
            self.returncode = 0
        return self.returncode


def test_nhip_3_phut_chi_giu_1_dong_cat_120_ky_tu_va_rebase_push(tmp_path, monkeypatch):
    bare = _tao_bare_hang_doi(
        tmp_path,
        {"01-nhip": "may: may-2\nloai: code\n\nChạy kiểm thử tích hợp dài"},
    )
    cfg = _clone_may(bare, tmp_path, "may-2")
    proc_gia = _TienTrinhAgyTheoBuoc()
    lenh_da_goi: list[list[str]] = []
    thoi_gian_gia = [1000.0]
    buoc = [0]
    anh_chup_dang: list[str] = []

    # Bơm dòng đầu tiên trước khi tới mốc 3 phút
    proc_gia.stdout.them("Bước 1: Đang biên dịch gói core\n".encode("utf-8"))

    def tao_proc(cmd, *a, **kw):
        lenh_da_goi.append(list(cmd))
        return proc_gia

    def ngu_theo_nhip(_giay: float) -> None:
        buoc[0] += 1
        if buoc[0] == 1:
            # Tới phút thứ 3 (180s) -> vòng lặp tiếp theo sẽ ghi nhịp lần 1
            thoi_gian_gia[0] += 180.0
            time.sleep(0.02)
        elif buoc[0] == 2:
            # Kiểm tra nhịp lần 1 đã push lên nhánh hang-doi
            tm_kt = _kiem_tra_hang_doi(bare, tmp_path, "kt-nhip")
            anh_chup_dang.append((tm_kt / "hang-doi" / "dang" / "01-nhip.md").read_text(encoding="utf-8"))
            # Giả lập máy khác vừa push 1 file lên nhánh hang-doi để kiểm tra pull --rebase
            (tm_kt / "hang-doi" / "moi" / "99-khac.md").write_text("may: may-9\n\nPhiếu khác\n", encoding="utf-8")
            _git(["config", "user.name", "may-9"], tm_kt)
            _git(["config", "user.email", "may-9@linhx.local"], tm_kt)
            _git(["config", "commit.gpgsign", "false"], tm_kt)
            _git(["add", "-A"], tm_kt)
            _git(["commit", "-m", "them phieu khac"], tm_kt)
            _git(["push", "origin", "hang-doi"], tm_kt)

            # Bơm dòng dài > 120 ký tự cho phút thứ 6
            dong_dai = "Bước 2: " + ("X" * 160) + "\n"
            proc_gia.stdout.them(dong_dai.encode("utf-8"))
            time.sleep(0.03)
            thoi_gian_gia[0] += 180.0  # Tổng cộng 360s (6 phút)
        elif buoc[0] == 3:
            # Kiểm tra nhịp lần 2 đã ghi đè dòng nhịp cũ trên remote (chỉ giữ 1 dòng nhip)
            tm_kt = _kiem_tra_hang_doi(bare, tmp_path, "kt-nhip")
            anh_chup_dang.append((tm_kt / "hang-doi" / "dang" / "01-nhip.md").read_text(encoding="utf-8"))
            proc_gia.stdout.them(
                json.dumps({"status": "SUCCESS", "response": "Đã xong kiểm thử"}).encode("utf-8") + b"\n"
            )
            time.sleep(0.02)
            proc_gia.hoan_tat(0)
        else:
            proc_gia.hoan_tat(0)

    monkeypatch.setattr(linhx_runner, "_tao_tien_trinh_agy", tao_proc)
    monkeypatch.setattr(linhx_runner, "_dong_ho", lambda: thoi_gian_gia[0])
    monkeypatch.setattr(linhx_runner, "_ngu", ngu_theo_nhip)

    kq = hang_doi_git.xu_ly_mot_phieu(cfg)
    assert kq is not None and kq["trang_thai"] == "xong"

    # Đề gửi agy phải chứa câu hướng dẫn CAN-LINH
    assert len(lenh_da_goi) == 1
    de_da_gui = lenh_da_goi[0][2]
    assert linhx_runner.CAU_NHAC_CAN_LINH in de_da_gui

    # Kiểm tra ảnh chụp dang/01-nhip.md ở phút 3 và phút 6
    assert len(anh_chup_dang) == 2
    dong_nhip_1 = [d for d in anh_chup_dang[0].splitlines() if d.startswith("nhip: ")]
    assert len(dong_nhip_1) == 1
    assert " 3p Bước 1: Đang biên dịch gói core" in dong_nhip_1[0]

    dong_nhip_2 = [d for d in anh_chup_dang[1].splitlines() if d.startswith("nhip: ")]
    assert len(dong_nhip_2) == 1  # Chỉ giữ đúng 1 dòng nhip duy nhất
    assert "3p" not in dong_nhip_2[0]
    assert " 6p Bước 2: " in dong_nhip_2[0]
    # Phần dòng cuối của agy không được vượt quá 120 ký tự
    phan_sau_phut = dong_nhip_2[0].split(" 6p ", 1)[1]
    assert len(phan_sau_phut) == 120


def test_nhip_loi_push_thu_3_lan_va_bo_qua(tmp_path, monkeypatch):
    bare = _tao_bare_hang_doi(
        tmp_path,
        {"02-nhip-loi": "may: may-1\nloai: code\n\nKiểm tra lỗi push nhịp"},
    )
    cfg = _clone_may(bare, tmp_path, "may-1")
    viec = hang_doi_git.nhan_phieu_git(cfg)
    assert viec is not None

    dem_push = [0]
    chay_git_goc = hang_doi_git.chay_git

    def chay_git_chan_push(args, cwd, check=True, timeout=120):
        if args and args[0] == "push":
            dem_push[0] += 1
            return subprocess.CompletedProcess(["git"] + list(args), 1, stdout="", stderr="simulated network error")
        return chay_git_goc(args, cwd=cwd, check=check, timeout=timeout)

    monkeypatch.setattr(hang_doi_git, "chay_git", chay_git_chan_push)
    ok = hang_doi_git.ghi_nhip_phieu_git(cfg, "02-nhip-loi", 3.0, "Đang chạy bước 1", gio_chuoi="10:15")
    assert ok is False
    assert dem_push[0] == 3  # Thử đúng 3 lần rồi bỏ qua, không ném lỗi


def test_can_linh_ghi_phieu_va_khong_tao_phieu_tu_sua(tmp_path, monkeypatch):
    # 1. Kiểm tra hàm trích khối CAN-LINH với nhiều biến thể
    assert hang_doi_git.trich_khoi_can_linh(linhx_runner.CAU_NHAC_CAN_LINH) is None
    assert hang_doi_git.trich_khoi_can_linh(
        "Đã dừng.\n`CAN-LINH: Đăng nhập Chrome tài khoản công ty; LENH: start chrome --profile-directory=\"Default\"`"
    ) == ("Đăng nhập Chrome tài khoản công ty", 'start chrome --profile-directory="Default"')
    assert hang_doi_git.trich_khoi_can_linh("CAN-LINH: Bấm Yes hộp thoại UAC trên màn hình") == (
        "Bấm Yes hộp thoại UAC trên màn hình",
        "",
    )

    # 2. Chạy phiếu thật có tu_sua: 2 nhưng trả về CAN-LINH -> phải ghi hang-doi/can-linh/<id>.md và KHÔNG tự sửa
    bare = _tao_bare_hang_doi(
        tmp_path,
        {
            "03-can-linh": (
                "may: may-1\n"
                "loai: trinh-duyet\n"
                "tu_sua: 2\n\n"
                "Mở trang quản trị và tải báo cáo"
            )
        },
    )
    cfg = _clone_may(bare, tmp_path, "may-1")

    def gia_agy_can_linh(_cfg, _viec):
        tra_loi = (
            "Trang yêu cầu xác thực Captcha và đăng nhập lại.\n"
            "CAN-LINH: Đăng nhập lại tài khoản trên Chrome máy 1; LENH: start chrome https://admin.example.com\n"
        )
        return "loi", tra_loi, "exit=1", 120, 45

    monkeypatch.setattr(hang_doi_git, "chay_agy", gia_agy_can_linh)
    kq = hang_doi_git.xu_ly_mot_phieu(cfg)
    assert kq is not None

    tm_kt = _kiem_tra_hang_doi(bare, tmp_path, "kt-can-linh")
    tep_cl = tm_kt / "hang-doi" / "can-linh" / "03-can-linh.md"
    assert tep_cl.is_file()
    meta_cl, _ = bang.parse_markdown_headers(tep_cl.read_text(encoding="utf-8"))
    assert meta_cl["may"] == "may-1"
    assert meta_cl["phieu"] == "03-can-linh"
    assert meta_cl["viec"] == "Đăng nhập lại tài khoản trên Chrome máy 1"
    assert meta_cl["lenh"] == "start chrome https://admin.example.com"
    assert meta_cl["gio"]
    # Không được đẻ phiếu tự sửa khi đã cần người thao tác
    assert not (tm_kt / "hang-doi" / "moi" / "03-can-linh-sua-1.md").exists()


def test_bang_web_can_linh_4_trang_thai_may_va_http_endpoints(tmp_path):
    tz = timezone(timedelta(hours=7))
    now = datetime(2026, 11, 15, 10, 0, 0, tzinfo=tz)
    clone_dir = tmp_path / "bang-clone"
    qroot = clone_dir / "hang-doi"
    for sub in ("moi", "dang", "xong", "can-linh", "may"):
        (qroot / sub).mkdir(parents=True, exist_ok=True)

    # 1. Khi can-linh/ rỗng -> trang chủ ẩn khối "Cần anh làm"
    snap_rong = bang.read_queue_snapshot(clone_dir, now=now, commit_times={})
    assert snap_rong["can_linh"] == []
    html_rong = bang.render_dashboard_html(snap_rong)
    assert '<section class="can-linh-box">' not in html_rong

    # 2. Đưa dữ liệu cho 4 máy + can-linh + may/*.json
    # may-1: đang chạy, có dòng nhip ở cuối
    (qroot / "dang" / "p-chay.md").write_text(
        "may: may-1\n"
        "loai: code\n"
        "nhan: may-1 2026-11-15T09:51:00+07:00\n\n"
        "Dựng giao diện trang chủ\n\n"
        "nhip: 09:57 6p pytest runner -q -> 40 passed\n",
        encoding="utf-8",
    )
    # may-2: vừa xong cách 5 phút -> Rảnh
    (qroot / "xong" / "p-xong").mkdir(parents=True)
    p_xong_kq = qroot / "xong" / "p-xong" / "KET-QUA.md"
    p_xong_kq.write_text(
        "phieu: p-xong\nmay: may-2\ntrang_thai: xong\nphut: 3.20\ntoken: vao=100 ra=50\n\nHoàn tất tốt.\n",
        encoding="utf-8",
    )
    # may-3: dừng/lỗi gần nhất cách 8 phút -> Kẹt kèm lý do
    (qroot / "xong" / "p-ket").mkdir(parents=True)
    p_ket_kq = qroot / "xong" / "p-ket" / "KET-QUA.md"
    p_ket_kq.write_text(
        "phieu: p-ket\nmay: may-3\ntrang_thai: dung\nphut: 10.00\ntoken: vao=0 ra=0\n\n"
        "dừng agy: quá 10 phút không tiến\n",
        encoding="utf-8",
    )
    # may-4: xong từ 50 phút trước -> Im lặng > 30 phút (đỏ)
    (qroot / "xong" / "p-cu").mkdir(parents=True)
    p_cu_kq = qroot / "xong" / "p-cu" / "KET-QUA.md"
    p_cu_kq.write_text(
        "phieu: p-cu\nmay: may-4\ntrang_thai: xong\nphut: 1.00\ntoken: vao=10 ra=10\n\nXong từ lâu.\n",
        encoding="utf-8",
    )
    # Cần Linh
    cl_tep = qroot / "can-linh" / "p-ket.md"
    cl_tep.write_text(
        "may: may-3\n"
        "phieu: p-ket\n"
        "viec: Cấp quyền Admin cho trình cài đặt\n"
        "lenh: powershell -Command \"Start-Process cmd -Verb RunAs\"\n"
        "gio: 2026-11-15T09:53:00+07:00\n",
        encoding="utf-8",
    )
    # Hồ sơ máy (may-1 ổ C < 10GB cảnh báo; may-2 ổ C dư dả)
    (qroot / "may" / "may-1.json").write_text(
        json.dumps(
            {
                "ma_may": "may-1",
                "ten_windows": "DESKTOP-PVHR2CD",
                "vai_tro": "Chrome đăng nhập sẵn",
                "cpu": {"ten": "Intel Core i5", "nhan": 4, "luong": 8},
                "ram": {"tong_gb": 16.0, "trong_gb": 3.5},
                "gpu": [{"ten": "Intel UHD", "vram_gb": 1.0}],
                "o_dia": [{"o": "C:", "tong_gb": 120.0, "trong_gb": 7.2}],
                "agy": {"co": True, "duong_dan": r"C:\bin\agy.cmd", "phien_ban": "agy 2.1.0"},
                "python": "3.11.9",
                "chrome": {"co": True, "profiles": ["Công việc", "Default"]},
                "nhan_phieu": {"so_phieu": 1, "nhan_bat_ky": True, "che_do_nhan": "bat-ky"},
                "thong_ke_24h": {"xong": 5, "loi": 1},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (qroot / "may" / "may-2.json").write_text(
        json.dumps(
            {
                "ma_may": "may-2",
                "ten_windows": "DESKTOP-LNRQBEE",
                "vai_tro": "Máy chính: code, điều phối",
                "cpu": {"ten": "Intel Xeon E5", "nhan": 16, "luong": 32},
                "ram": {"tong_gb": 64.0, "trong_gb": 48.0},
                "gpu": [{"ten": "NVIDIA GTX 1060", "vram_gb": 6.0}],
                "o_dia": [{"o": "C:", "tong_gb": 500.0, "trong_gb": 210.0}],
                "agy": {"co": True, "duong_dan": r"C:\bin\agy.cmd", "phien_ban": "agy 2.1.0"},
                "python": "3.12.2",
                "chrome": {"co": False, "profiles": []},
                "nhan_phieu": {"so_phieu": 3, "nhan_bat_ky": True, "che_do_nhan": "bat-ky"},
                "thong_ke_24h": {"xong": 18, "loi": 0},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    commit_times = {
        "hang-doi/dang/p-chay.md": int((now - timedelta(minutes=3)).timestamp()),
        "hang-doi/xong/p-xong/KET-QUA.md": int((now - timedelta(minutes=5)).timestamp()),
        "hang-doi/xong/p-ket/KET-QUA.md": int((now - timedelta(minutes=8)).timestamp()),
        "hang-doi/xong/p-cu/KET-QUA.md": int((now - timedelta(minutes=50)).timestamp()),
    }
    snap = bang.read_queue_snapshot(clone_dir, now=now, commit_times=commit_times)

    # Kiểm tra dữ liệu JSON cho /api/trang-thai
    assert len(snap["can_linh"]) == 1
    assert snap["can_linh"][0]["viec"] == "Cấp quyền Admin cho trình cài đặt"
    theo_may = {m["may"]: m for m in snap["may"]}
    assert theo_may["may-1"]["trang_thai_may"] == "chay"
    assert theo_may["may-1"]["nhip"] == "09:57 6p pytest runner -q -> 40 passed"
    assert snap["dang_chay"][0]["de"] == "Dựng giao diện trang chủ"  # Không bị lẫn dòng nhip vào đề
    assert theo_may["may-2"]["trang_thai_may"] == "ranh"
    assert theo_may["may-3"]["trang_thai_may"] == "ket"
    assert "10 phút không tiến" in theo_may["may-3"]["ket_ly_do"]
    assert theo_may["may-4"]["trang_thai_may"] == "im-lang"
    assert theo_may["may-4"]["qua_30_phut"] is True

    # Kiểm tra HTML trang chủ: khối đỏ "Cần anh làm" nằm TRƯỚC bảng máy
    html_trang_chu = bang.render_dashboard_html(snap)
    vi_tri_can_linh = html_trang_chu.index("Cần anh làm")
    vi_tri_bang_may = html_trang_chu.index("<th>Đang làm gì</th>")
    assert vi_tri_can_linh < vi_tri_bang_may
    assert "09:57 6p pytest runner -q -&gt; 40 passed" in html_trang_chu
    assert "dừng agy: quá 10 phút không tiến" in html_trang_chu
    assert "Im lặng &gt; 30 phút" in html_trang_chu

    # Kiểm tra HTML trang /may và cảnh báo ổ C < 10 GB
    html_may = bang.render_machines_html(snap)
    assert "Cảnh báo: Ổ C: chỉ còn trống 7.2 GB (&lt; 10 GB)" in html_may
    assert "Máy chính: code, điều phối" in html_may
    assert "Công việc, Default" in html_may

    # Kiểm tra HTTP server thực tế cho /, /may, /api/trang-thai, /api/may
    monitor = bang.QueueMonitor(clone_dir=clone_dir, enable_git_sync=False)
    server = bang.create_http_server(monitor, host="127.0.0.1", port=0)
    port = server.server_address[1]
    import threading

    luong_http = threading.Thread(target=server.serve_forever, daemon=True)
    luong_http.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/trang-thai", timeout=5) as resp:
            du_lieu_api = json.loads(resp.read().decode("utf-8"))
            assert "can_linh" in du_lieu_api
            assert any("nhip" in m for m in du_lieu_api["may"])
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/may", timeout=5) as resp:
            nd_tab_may = resp.read().decode("utf-8")
            assert resp.status == 200
            assert "DESKTOP-PVHR2CD" in nd_tab_may
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/may", timeout=5) as resp:
            du_lieu_may = json.loads(resp.read().decode("utf-8"))
            by_code = {x["ma_may"]: x for x in du_lieu_may["may"]}
            assert by_code["may-1"]["canh_bao_o_c"] is True
            assert by_code["may-2"]["canh_bao_o_c"] is False
    finally:
        server.shutdown()
        server.server_close()
        luong_http.join(timeout=2)


def test_ho_so_may_loc_bi_mat_va_chi_push_khi_thay_doi(tmp_path, monkeypatch):
    # 1. Giả lập Chrome User Data có email, token bí mật trong Local State
    tm_chrome = tmp_path / "chrome-ud"
    tm_chrome.mkdir(parents=True)
    (tm_chrome / "Local State").write_text(
        json.dumps(
            {
                "profile": {
                    "info_cache": {
                        "Default": {
                            "name": "Kênh Chính",
                            "user_name": "linh.bi.mat@company.vn",
                            "gaia_id": "999888777",
                        },
                        "Profile 1": {
                            "name": "linh.ca.nhan@gmail.com",
                            "user_name": "linh.ca.nhan@gmail.com",
                        },
                        "Profile 2": {
                            "name": "Thử nghiệm",
                        },
                    }
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    tep_chrome_exe = tmp_path / "chrome.exe"
    tep_chrome_exe.write_text("fake", encoding="utf-8")

    # 2. Giả lập nhánh hang-doi có phiếu xong/lỗi trong 24h và ngoài 24h
    bare = _tao_bare_hang_doi(tmp_path, {})
    cfg = _clone_may(
        bare,
        tmp_path,
        "may-2",
        vai_tro="Máy chính: code, điều phối",
        so_phieu=3,
        nhan_bat_ky=False,
        ghi_ho_so_may=True,
        token="ghp_BiMatKhongDuocGhi1234567890",
    )
    wt = hang_doi_git.dam_bao_worktree(cfg)
    assert wt is not None

    now_epoch = 1800000000.0
    iso_moi = datetime.fromtimestamp(now_epoch - 3600, tz=timezone.utc).isoformat()
    iso_cu = datetime.fromtimestamp(now_epoch - 40 * 3600, tz=timezone.utc).isoformat()
    for ma, may_p, tt, luc in (
        ("p1", "may-2", "xong", iso_moi),
        ("p2", "may-2", "loi", iso_moi),
        ("p3", "may-2", "dung", iso_moi),
        ("p4", "may-2", "xong", iso_cu),      # Quá 24h -> không đếm
        ("p5", "may-1", "xong", iso_moi),     # Máy khác -> không đếm
    ):
        tm_kq = wt / "hang-doi" / "xong" / ma
        tm_kq.mkdir(parents=True, exist_ok=True)
        (tm_kq / "KET-QUA.md").write_text(
            f"phieu: {ma}\nmay: {may_p}\ntrang_thai: {tt}\nxong_luc: {luc}\n\nKết quả\n",
            encoding="utf-8",
        )
    hang_doi_git._commit_git(wt, "seed", "them lich su xong")
    hang_doi_git.chay_git(["push", "origin", "HEAD:refs/heads/hang-doi"], cwd=wt)

    def gia_chay_agy_ver(cmd, **_kw):
        return subprocess.CompletedProcess(cmd, 0, stdout="antigravity-cli 2.4.1 (user@secret.com)\n", stderr="")

    ho_so = ho_so_may.thu_thap_ho_so_may(
        cfg,
        wt=wt,
        chay_lenh_fn=gia_chay_agy_ver,
        thu_muc_chrome=tm_chrome,
        duong_dan_chrome_exe=str(tep_chrome_exe),
        bay_gio_epoch=now_epoch,
    )

    assert ho_so["ma_may"] == "may-2"
    assert ho_so["ten_windows"]
    assert ho_so["vai_tro"] == "Máy chính: code, điều phối"
    assert ho_so["cpu"]["nhan"] >= 1 and ho_so["cpu"]["luong"] >= 1
    assert ho_so["ram"]["tong_gb"] >= 0 and ho_so["ram"]["trong_gb"] >= 0
    assert isinstance(ho_so["gpu"], list)
    assert isinstance(ho_so["o_dia"], list) and len(ho_so["o_dia"]) >= 1
    assert "2.4.1" in ho_so["agy"]["phien_ban"]
    assert ho_so["python"]
    assert ho_so["chrome"]["co"] is True
    # Profile 1 có tên là email nên phải đổi về tên thư mục "Profile 1", không lộ email!
    assert ho_so["chrome"]["profiles"] == ["Kênh Chính", "Profile 1", "Thử nghiệm"]
    assert ho_so["nhan_phieu"] == {
        "so_phieu": 3,
        "nhan_bat_ky": False,
        "che_do_nhan": "chi-dich-danh",
    }
    assert ho_so["thong_ke_24h"] == {"xong": 1, "loi": 2}

    chuoi_json = json.dumps(ho_so, ensure_ascii=False)
    assert "linh.bi.mat@company.vn" not in chuoi_json
    assert "linh.ca.nhan@gmail.com" not in chuoi_json
    assert "user@secret.com" not in chuoi_json
    assert "ghp_BiMatKhongDuocGhi" not in chuoi_json
    for tu_cam in ("password", "token", "email"):
        assert f'"{tu_cam}"' not in chuoi_json.lower()

    # 3. Kiểm tra chỉ push lên nhánh hang-doi khi hồ sơ thay đổi
    trang_thai_ho_so = [dict(ho_so, ram={"tong_gb": 32.0, "trong_gb": 16.1})]

    def thu_thap_gia(_cfg, wt=None):
        ban = json.loads(json.dumps(trang_thai_ho_so[0]))
        ban["cap_nhat_luc"] = "2026-11-15T10:00:00+0700"
        return ban

    # Lần 1 (khởi động): chưa có file -> ghi và push thành công
    assert hang_doi_git.cap_nhat_ho_so_may_git(cfg, thu_thap_fn=thu_thap_gia) is True
    tm_kt = _kiem_tra_hang_doi(bare, tmp_path, "kt-hoso")
    so_commit_1 = int(_git(["rev-list", "--count", "HEAD"], tm_kt))
    assert (tm_kt / "hang-doi" / "may" / "may-2.json").is_file()

    # Lần 2: chỉ đổi timestamp và dao động RAM rất nhỏ (16.1 -> 16.2 GB) -> KHÔNG push thêm commit
    trang_thai_ho_so[0]["ram"]["trong_gb"] = 16.2
    assert hang_doi_git.cap_nhat_ho_so_may_git(cfg, thu_thap_fn=thu_thap_gia) is False
    tm_kt = _kiem_tra_hang_doi(bare, tmp_path, "kt-hoso")
    so_commit_2 = int(_git(["rev-list", "--count", "HEAD"], tm_kt))
    assert so_commit_2 == so_commit_1

    # Lần 3: vai trò máy hoặc dung lượng trống thay đổi rõ rệt -> push bản mới
    trang_thai_ho_so[0]["vai_tro"] = "Máy chính: code, điều phối, build nặng"
    assert hang_doi_git.cap_nhat_ho_so_may_git(cfg, thu_thap_fn=thu_thap_gia) is True
    tm_kt = _kiem_tra_hang_doi(bare, tmp_path, "kt-hoso")
    so_commit_3 = int(_git(["rev-list", "--count", "HEAD"], tm_kt))
    assert so_commit_3 == so_commit_1 + 1
    du_lieu_moi = json.loads((tm_kt / "hang-doi" / "may" / "may-2.json").read_text(encoding="utf-8"))
    assert du_lieu_moi["vai_tro"] == "Máy chính: code, điều phối, build nặng"


def test_vong_git_cap_nhat_ho_so_luc_khoi_dong_va_moi_60_phut(tmp_path, monkeypatch):
    bare = _tao_bare_hang_doi(tmp_path, {})
    cfg = _clone_may(bare, tmp_path, "may-3", ghi_ho_so_may=True)
    cac_moc_goi: list[float] = []
    thoi_gian_gia = [100.0]

    def cap_nhat_gia(_cfg):
        cac_moc_goi.append(thoi_gian_gia[0])
        return True

    def ngu_gia(_giay):
        # Lần ngủ 1: mới 30 phút (1800s) -> chưa gọi lại; lần ngủ 2: đủ 60 phút (3600s) -> gọi lại rồi dừng vòng
        thoi_gian_gia[0] += 1800.0
        if len(cac_moc_goi) >= 2:
            raise StopIteration("xong-kiem-tra-60-phut")

    monkeypatch.setattr(hang_doi_git, "cap_nhat_ho_so_may_git", cap_nhat_gia)
    monkeypatch.setattr(linhx_runner, "_dong_ho", lambda: thoi_gian_gia[0])
    monkeypatch.setattr(time, "sleep", ngu_gia)

    with pytest.raises(StopIteration):
        hang_doi_git.vong_git(cfg, mot_lan=False)

    # Gọi lúc khởi động (t=100) và gọi lại đúng mốc đủ 60 phút (t=3700), bỏ qua mốc 30 phút (t=1900)
    assert cac_moc_goi == [100.0, 3700.0]

