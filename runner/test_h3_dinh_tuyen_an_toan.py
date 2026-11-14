from __future__ import annotations

import ctypes
import io
import json
import os
import shutil
import stat
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

import pytest

from runner import hang_doi_git, linhx_runner
from runner._gia_moi_truong import _gia_ram_va_moi_truong_h3  # noqa: F401  (fixture autouse, thay conftest)


def _xoa_thu_muc(duong_dan: Path):
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
    goc_viec = linhx_runner.GOC / "viec"
    viec_da_co = goc_viec.exists()
    tm_goc = goc_viec / f"pytest-tmp-h3-{os.getpid()}-{uuid.uuid4().hex[:8]}"
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


def _git(args, cwd):
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


def _tao_bare_hang_doi(
    tmp_path: Path,
    phieu_moi: dict[str, str],
    phieu_dang: dict[str, str] | None = None,
) -> Path:
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
    for ten, nd in phieu_moi.items():
        (tm_moi / f"{ten}.md").write_text(nd, encoding="utf-8")
    if phieu_dang:
        tm_dang = seed / "hang-doi" / "dang"
        tm_dang.mkdir(parents=True, exist_ok=True)
        for ten, nd in phieu_dang.items():
            (tm_dang / f"{ten}.md").write_text(nd, encoding="utf-8")
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


def test_moi_may_deu_nhan_ca_code_lan_trinh_duyet(tmp_path, monkeypatch):
    bare = _tao_bare_hang_doi(
        tmp_path,
        {
            "01-m1-code": "may: may-1\nloai: code\n\nCode tren may 1",
            "02-m1-td": "may: may-1\nloai: trinh-duyet\n\nTrinh duyet tren may 1",
            "03-m2-code": "may: may-2\nloai: code\n\nCode tren may 2",
            "04-m2-td": "may: may-2\nloai: trinh-duyet\n\nTrinh duyet tren may 2",
            "05-chung-code": "may: bat-ky\nloai: code\n\nCode bat ky cho may 3",
            "06-chung-td": "may: bat-ky\nloai: trinh-duyet\n\nTrinh duyet bat ky cho may 3",
        },
    )
    ghi_nhan = []

    def gia_agy(cfg, viec):
        ghi_nhan.append((cfg["tho"], viec["viec"], viec["loai"]))
        return "xong", f"{cfg['tho']}:{viec['loai']}", "ok", 10, 5

    monkeypatch.setattr(hang_doi_git, "chay_agy", gia_agy)

    for ten_may in ("may-1", "may-2", "may-3"):
        cfg = _clone_may(bare, tmp_path, ten_may)
        kq_a = hang_doi_git.xu_ly_mot_phieu(cfg)
        kq_b = hang_doi_git.xu_ly_mot_phieu(cfg)
        assert kq_a is not None and kq_b is not None
        assert {kq_a["trang_thai"], kq_b["trang_thai"]} == {"xong"}

    theo_may = {}
    for may, _, loai in ghi_nhan:
        theo_may.setdefault(may, set()).add(loai)
    assert theo_may == {
        "may-1": {"code", "trinh-duyet"},
        "may-2": {"code", "trinh-duyet"},
        "may-3": {"code", "trinh-duyet"},
    }


def test_moi_may_toi_da_1_trinh_duyet_nhung_van_nhan_code_va_may_khac_nhan_tiep(tmp_path, monkeypatch):
    # Phieu td-dang-chay cua may-1 dang nam trong dang/ -> may-1 khong duoc nhan them trinh-duyet,
    # nhung van nhan duoc code; con may-2 van nhan duoc phieu trinh-duyet bat-ky.
    bare = _tao_bare_hang_doi(
        tmp_path,
        phieu_moi={
            "01-td-rieng-m1": "may: may-1\nloai: trinh-duyet\n\nPhieu trinh duyet thu 2 cua may-1",
            "02-td-chung": "may: bat-ky\nloai: trinh-duyet\n\nPhieu trinh duyet chung",
            "03-code-m1": "may: bat-ky\nloai: code\n\nPhieu code chay song song voi trinh-duyet",
        },
        phieu_dang={
            "00-td-dang": "may: may-1\nloai: trinh-duyet\nnhan: may-1 2026-11-14T08:00:00+0700\n\nDang chiem man hinh may-1",
        },
    )
    # Ke ca khi LINHX_SO_PHIEU=3, trinh-duyet tren may-1 van bi chan o muc 1
    cfg1 = _clone_may(bare, tmp_path, "may-1", so_phieu=3)
    cfg2 = _clone_may(bare, tmp_path, "may-2", so_phieu=1)

    monkeypatch.setattr(hang_doi_git, "chay_agy", lambda c, v: ("xong", "ok", "ok", 1, 1))

    # may-1 bo qua ca 01-td-rieng-m1 lan 02-td-chung, chi nhan 03-code-m1
    kq_m1_lan1 = hang_doi_git.xu_ly_mot_phieu(cfg1)
    assert kq_m1_lan1 is not None
    assert kq_m1_lan1["viec"] == "03-code-m1"

    # Lan tiep theo tren may-1: chi con 2 phieu trinh-duyet trong khi 00-td-dang chua xong -> tra None
    assert hang_doi_git.nhan_phieu_git(cfg1) is None

    # Trong luc do may-2 khong bi khoa trinh-duyet cua may-1 -> nhan duoc 02-td-chung
    kq_m2 = hang_doi_git.xu_ly_mot_phieu(cfg2)
    assert kq_m2 is not None
    assert kq_m2["viec"] == "02-td-chung"

    # Sau khi 00-td-dang tren may-1 bao xong -> may-1 moi nhan not 01-td-rieng-m1
    hang_doi_git.bao_ket_qua_git(cfg1, {"viec": "00-td-dang"}, "xong", "Xong phieu dau")
    kq_m1_lan2 = hang_doi_git.xu_ly_mot_phieu(cfg1)
    assert kq_m1_lan2 is not None
    assert kq_m1_lan2["viec"] == "01-td-rieng-m1"


def test_gioi_han_linhx_so_phieu_mac_dinh_la_1(tmp_path, monkeypatch):
    bare1 = _tao_bare_hang_doi(
        tmp_path / "p1",
        {
            "c1": "may: bat-ky\nloai: code\n\nCode 1",
            "c2": "may: bat-ky\nloai: code\n\nCode 2",
            "t1": "may: bat-ky\nloai: trinh-duyet\n\nTD 1",
            "t2": "may: bat-ky\nloai: trinh-duyet\n\nTD 2",
        },
    )
    cfg_mac_dinh = _clone_may(bare1, tmp_path / "p1", "may-1")
    khoa = threading.Lock()
    dang_chay = {"code": 0, "trinh-duyet": 0}
    cuc_dai = {"code": 0, "trinh-duyet": 0}

    def gia_agy_mac_dinh(cfg, viec):
        loai = viec["loai"]
        with khoa:
            dang_chay[loai] += 1
            if dang_chay[loai] > cuc_dai[loai]:
                cuc_dai[loai] = dang_chay[loai]
        time.sleep(0.08)
        with khoa:
            dang_chay[loai] -= 1
        return "xong", f"xong {viec['viec']}", "ok", 5, 5

    monkeypatch.setattr(hang_doi_git, "chay_agy", gia_agy_mac_dinh)
    hang_doi_git.vong_git(cfg_mac_dinh, mot_lan=True)
    assert cuc_dai["code"] == 1
    assert cuc_dai["trinh-duyet"] == 1
    tm_kt1 = _kiem_tra_hang_doi(bare1, tmp_path / "p1", "kt1")
    for ma in ("c1", "c2", "t1", "t2"):
        assert (tm_kt1 / "hang-doi" / "xong" / ma / "KET-QUA.md").is_file()


def test_gioi_han_linhx_so_phieu_code_song_song_theo_tho_env(tmp_path, monkeypatch):
    # LINHX_SO_PHIEU=2 doc tu tho.env -> chay dung 2 phieu code song song + 1 trinh-duyet,
    # phieu code thu 3 va phieu trinh-duyet thu 2 phai cho den khi co cho trong.
    bare2 = _tao_bare_hang_doi(
        tmp_path / "p2",
        {
            "code-1": "may: may-1\nloai: code\n\nCode 1",
            "code-2": "may: may-1\nloai: code\n\nCode 2",
            "code-3": "may: may-1\nloai: code\n\nCode 3",
            "td-1": "may: may-1\nloai: trinh-duyet\n\nTD 1",
            "td-2": "may: may-1\nloai: trinh-duyet\n\nTD 2",
        },
    )
    cfg_mau = _clone_may(bare2, tmp_path / "p2", "may-1")
    tep_env = tmp_path / "p2" / "tho.env"
    tep_env.write_text(
        "\n".join(
            [
                "LINHX_NGUON=github",
                "LINHX_THO=may-1",
                "LINHX_SO_PHIEU=2",
                f"LINHX_REPO_HANG_DOI={cfg_mau['repo_hang_doi']}",
                f"LINHX_THU_MUC={cfg_mau['thu_muc']}",
                f"LINHX_DRIVE={cfg_mau['thu_muc_drive']}",
                f"LINHX_LOG_DIR={cfg_mau['thu_muc_log']}",
                "LINHX_NGHI=0.01",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    for k in (
        "LINHX_NGUON",
        "LINHX_THO",
        "LINHX_SO_PHIEU",
        "LINHX_REPO_HANG_DOI",
        "LINHX_THU_MUC",
        "LINHX_DRIVE",
        "LINHX_LOG_DIR",
        "LINHX_NGHI",
    ):
        monkeypatch.delenv(k, raising=False)

    cfg_2 = linhx_runner.doc_env(tep_env)
    assert cfg_2["so_phieu"] == 2

    rao_hai_code = threading.Barrier(2, timeout=8)
    da_vao_rao = []
    dang_2 = {"code": 0, "trinh-duyet": 0}
    max_2 = {"code": 0, "trinh-duyet": 0}
    khoa_2 = threading.Lock()

    def gia_agy_song_song(cfg, viec):
        loai = viec["loai"]
        can_doi_rao = False
        with khoa_2:
            dang_2[loai] += 1
            if dang_2[loai] > max_2[loai]:
                max_2[loai] = dang_2[loai]
            if loai == "code" and len(da_vao_rao) < 2:
                da_vao_rao.append(viec["viec"])
                can_doi_rao = True
        if can_doi_rao:
            # Chung minh 2 phieu code thuc su chay song song trong cung 1 vong_git
            rao_hai_code.wait()
        time.sleep(0.08)
        with khoa_2:
            dang_2[loai] -= 1
        return "xong", f"Hoan tat {viec['viec']}", "ok", 12, 8

    monkeypatch.setattr(linhx_runner, "chay_agy", gia_agy_song_song)
    linhx_runner.vong(cfg_2, mot_lan=True)

    assert max_2["code"] == 2
    assert max_2["trinh-duyet"] == 1
    tm_kt2 = _kiem_tra_hang_doi(bare2, tmp_path / "p2", "kt2")
    for ma in ("code-1", "code-2", "code-3", "td-1", "td-2"):
        nd = (tm_kt2 / "hang-doi" / "xong" / ma / "KET-QUA.md").read_text(encoding="utf-8")
        assert "trang_thai: xong" in nd


class _TienTrinhAgyGia:
    """Tien trinh Popen gia de kiem tra dung nguong 10 phut khong tien va 40 phut toi da."""

    def __init__(self, pid: int = 424242, stdout_ban_dau: bytes = b""):
        self.pid = pid
        self.returncode = None
        self.stdout = io.BytesIO(stdout_ban_dau)
        self.stderr = io.BytesIO(b"")
        self.da_kill = False

    def poll(self):
        return self.returncode

    def kill(self):
        self.da_kill = True
        self.returncode = -9

    def wait(self, timeout=None):
        if self.returncode is None:
            self.returncode = 0
        return self.returncode


def test_dung_agy_khi_10_phut_khong_tien_va_khi_qua_40_phut(tmp_path, monkeypatch):
    bare = _tao_bare_hang_doi(
        tmp_path,
        {
            "01-treo-10p": "may: may-1\nloai: code\n\nPhieu bi treo khong tien do",
            "02-chay-qua-40p": "may: may-1\nloai: trinh-duyet\n\nPhieu van co tien do nhung vuot 40 phut",
        },
    )
    cfg = _clone_may(bare, tmp_path, "may-1")

    ds_pid_taskkill = []
    monkeypatch.setattr(linhx_runner, "_goi_taskkill_cay", lambda pid: ds_pid_taskkill.append(pid))

    # --- Kich ban 1: Khong tien do -> phai dung ngay moc 10 phut (600 giay), KHONG cho toi 40 phut ---
    thoi_gian_gia = [1000.0]
    proc_treo = _TienTrinhAgyGia(pid=51001)

    def ngu_khong_tien(giay):
        thoi_gian_gia[0] += 60.0  # moi nhip tang 1 phut, khong co bat ky thay doi nao

    monkeypatch.setattr(linhx_runner, "_dong_ho", lambda: thoi_gian_gia[0])
    monkeypatch.setattr(linhx_runner, "_ngu", ngu_khong_tien)
    monkeypatch.setattr(linhx_runner, "_tao_tien_trinh_agy", lambda *a, **kw: proc_treo)

    kq_treo = hang_doi_git.xu_ly_mot_phieu(cfg)
    assert kq_treo is not None
    assert kq_treo["trang_thai"] == "dung"
    assert "10 phút không tiến" in kq_treo["nhat_ky"]
    assert proc_treo.da_kill is True
    if os.name == "nt":
        assert 51001 in ds_pid_taskkill
    # Dung o moc 10 phut (600s), khong phai 40 phut (2400s)
    assert 600.0 <= (thoi_gian_gia[0] - 1000.0) < 720.0

    # --- Kich ban 2: Co tien do moi 5 phut (sua file trong thu_muc) -> vuot qua 10/20/30 phut,
    # nhung den moc 40 phut (2400 giay) phai bi dung ---
    thoi_gian_gia[0] = 5000.0
    proc_dai = _TienTrinhAgyGia(pid=51002)
    dem_buoc = [0]

    def ngu_co_tien_do(giay):
        thoi_gian_gia[0] += 300.0  # moi buoc 5 phut (< 10 phut khong tien)
        dem_buoc[0] += 1
        tep_tien = Path(cfg["thu_muc"]) / "tien-do.txt"
        with tep_tien.open("a", encoding="utf-8") as f:
            f.write(f"buoc {dem_buoc[0]}\n")

    monkeypatch.setattr(linhx_runner, "_ngu", ngu_co_tien_do)
    monkeypatch.setattr(linhx_runner, "_tao_tien_trinh_agy", lambda *a, **kw: proc_dai)

    kq_qua_gio = hang_doi_git.xu_ly_mot_phieu(cfg)
    assert kq_qua_gio is not None
    assert kq_qua_gio["trang_thai"] == "dung"
    assert "quá trần 40 phút" in kq_qua_gio["nhat_ky"]
    assert proc_dai.da_kill is True
    if os.name == "nt":
        assert 51002 in ds_pid_taskkill
    assert (thoi_gian_gia[0] - 5000.0) >= 2400.0

    # Kiem tra KET-QUA.md tren nhanh hang-doi ghi dung trang_thai: dung va log jsonl ghi su kien agy_raw
    tm_kt = _kiem_tra_hang_doi(bare, tmp_path, "kt-dung")
    nd_1 = (tm_kt / "hang-doi" / "xong" / "01-treo-10p" / "KET-QUA.md").read_text(encoding="utf-8")
    nd_2 = (tm_kt / "hang-doi" / "xong" / "02-chay-qua-40p" / "KET-QUA.md").read_text(encoding="utf-8")
    assert "trang_thai: dung" in nd_1
    assert "10 phút không tiến" in nd_1
    assert "trang_thai: dung" in nd_2
    assert "quá trần 40 phút" in nd_2

    dong_log_1 = [
        json.loads(x)
        for x in (cfg["thu_muc_log"] / "01-treo-10p.jsonl").read_text(encoding="utf-8").splitlines()
        if x.strip()
    ]
    assert any(d.get("su_kien") == "agy_raw" and d.get("ghi_chu") == "khong_tien" for d in dong_log_1)


def _tien_trinh_con_song(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        STILL_ACTIVE = 259
        k32 = ctypes.windll.kernel32
        h = k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
        if not h:
            return False
        try:
            ma_thoat = ctypes.c_ulong()
            if not k32.GetExitCodeProcess(h, ctypes.byref(ma_thoat)):
                return False
            return ma_thoat.value == STILL_ACTIVE
        finally:
            k32.CloseHandle(h)
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def test_dung_cay_tien_trinh_that_khi_treo_khong_tien(tmp_path, monkeypatch):
    # Dung chinh sys.executable gia lam agy (khong can agy.exe): cha de ra tien trinh con roi cung ngu.
    tep_pid_con = tmp_path / "pid_con.txt"
    tep_wrapper = tmp_path / "wrapper_agy.py"
    tep_wrapper.write_text(
        "import subprocess, sys, time\n"
        "from pathlib import Path\n"
        "kw = {'creationflags': 0x08000000} if sys.platform == 'win32' else {}\n"
        "p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'], **kw)\n"
        f"Path({str(tep_pid_con)!r}).write_text(str(p.pid), encoding='utf-8')\n"
        "sys.stdout.write('khoi dong xong\\n')\n"
        "sys.stdout.flush()\n"
        "time.sleep(60)\n",
        encoding="utf-8",
    )
    tm_viec = tmp_path / "viec-that"
    tm_viec.mkdir()
    cfg = {
        "tho": "may-1",
        "agy": sys.executable,
        "agy_args": "",
        "thu_muc": tm_viec,
        "tran_phut": 1.0,
        "khong_tien_phut": 0.006,  # ~0.36 giay
    }
    viec = {
        "viec": "treo-that",
        "che_do": "thuc",
        "de": "kiem tra dung cay tien trinh",
        "tran_phut": 1.0,
        "khong_tien_phut": 0.006,
    }
    def popen_chuyen_wrapper(cmd, *a, **kw):
        cmd_moi = [sys.executable, str(tep_wrapper)] + list(cmd[1:])
        return linhx_runner._POPEN_GOC(cmd_moi, *a, **kw)

    monkeypatch.setattr(linhx_runner, "_tao_tien_trinh_agy", popen_chuyen_wrapper)
    t0 = time.monotonic()
    tt, kq, nk, tv, tr = linhx_runner.chay_agy(cfg, viec)
    elapsed = time.monotonic() - t0

    assert tt == "dung"
    assert kq is None
    assert "không tiến" in nk
    assert elapsed < 10.0

    assert tep_pid_con.is_file()
    pid_con = int(tep_pid_con.read_text(encoding="utf-8").strip())
    # Cho toi da 2 giay de OS thu hoi bang tien trinh con sau taskkill /T /F hoac killpg
    han = time.monotonic() + 2.0
    while time.monotonic() < han and _tien_trinh_con_song(pid_con):
        time.sleep(0.05)
    assert not _tien_trinh_con_song(pid_con)


def test_dau_git_commit_duoc_tinh_la_co_tien_do(tmp_path):
    repo_con = tmp_path / "repo-viec"
    repo_con.mkdir()
    _git(["init"], repo_con)
    _git(["config", "user.name", "tho"], repo_con)
    _git(["config", "user.email", "tho@linhx.local"], repo_con)
    _git(["config", "commit.gpgsign", "false"], repo_con)
    (repo_con / "a.py").write_text("x = 1\n", encoding="utf-8")
    _git(["add", "-A"], repo_con)
    _git(["commit", "-m", "c1"], repo_con)

    dau_1 = linhx_runner._dau_git_head(repo_con)
    assert dau_1 is not None
    _git(["commit", "--allow-empty", "-m", "c2"], repo_con)
    dau_2 = linhx_runner._dau_git_head(repo_con)
    assert dau_2 != dau_1


def test_ram_trong_duoi_1_5_gb_khong_nhan_phieu_va_du_1_5_gb_thi_nhan(tmp_path, monkeypatch):
    # 1. Kiem tra bo doc RAM thuc te va bo doc /proc/meminfo gia lap
    ram_that = linhx_runner._doc_ram_he_thong_gb()
    assert ram_that is not None and ram_that > 0

    tep_meminfo = tmp_path / "meminfo"
    tep_meminfo.write_text(
        "MemTotal:       16384000 kB\n"
        "MemFree:          512000 kB\n"
        "MemAvailable:    1572864 kB\n",  # dung 1.5 GiB (1.5 * 1024 * 1024 kB)
        encoding="utf-8",
    )
    assert linhx_runner._doc_ram_proc_meminfo_gb(tep_meminfo) == pytest.approx(1.5, rel=1e-6)

    # 2. Kiem tra hang doi GitHub khi RAM < 1.5 GB va khi RAM >= 1.5 GB
    bare = _tao_bare_hang_doi(
        tmp_path,
        {"ram-01": "may: bat-ky\nloai: code\n\nKiem tra nguong RAM 1.5 GB"},
    )
    cfg = _clone_may(bare, tmp_path, "may-1")
    so_lan_goi_agy = [0]

    def gia_agy(c, v):
        so_lan_goi_agy[0] += 1
        return "xong", "Du RAM de chay", "ok", 10, 5

    monkeypatch.setattr(hang_doi_git, "chay_agy", gia_agy)

    # RAM = 1.2 GB (< 1.5 GB) -> khong nhan phieu, phieu van nam nguyen trong moi/
    monkeypatch.setattr(hang_doi_git, "lay_ram_trong_gb", lambda: 1.2)
    assert hang_doi_git.xu_ly_mot_phieu(cfg) is None
    hang_doi_git.vong_git(cfg, mot_lan=True)
    assert so_lan_goi_agy[0] == 0

    # RAM = 1.49 GB (< 1.5 GB) -> van khong nhan
    monkeypatch.setattr(hang_doi_git, "lay_ram_trong_gb", lambda: 1.49)
    assert hang_doi_git.nhan_phieu_git(cfg) is None

    tm_kt = _kiem_tra_hang_doi(bare, tmp_path, "kt-ram-thap")
    assert (tm_kt / "hang-doi" / "moi" / "ram-01.md").is_file()
    assert not list((tm_kt / "hang-doi" / "dang").glob("*.md"))

    # RAM = 1.5 GB (dung bien >= 1.5 GB) -> nhan va xu ly thanh cong
    monkeypatch.setattr(hang_doi_git, "lay_ram_trong_gb", lambda: 1.5)
    kq = hang_doi_git.xu_ly_mot_phieu(cfg)
    assert kq is not None and kq["trang_thai"] == "xong"
    assert so_lan_goi_agy[0] == 1

    tm_kt = _kiem_tra_hang_doi(bare, tmp_path, "kt-ram-du")
    assert not (tm_kt / "hang-doi" / "moi" / "ram-01.md").exists()
    nd_kq = (tm_kt / "hang-doi" / "xong" / "ram-01" / "KET-QUA.md").read_text(encoding="utf-8")
    assert "trang_thai: xong" in nd_kq
    assert "Du RAM de chay" in nd_kq
