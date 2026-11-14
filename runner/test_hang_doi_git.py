from __future__ import annotations

import os
import shutil
import stat
import subprocess
import threading
import uuid
from pathlib import Path

import pytest

from runner import hang_doi_git, linhx_runner


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
    tm_goc = goc_viec / f"pytest-tmp-{os.getpid()}-{uuid.uuid4().hex[:8]}"
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


def _tao_bare_va_nhanh_hang_doi(tmp_path: Path, phieu_ban_dau: dict[str, str] | None = None):
    bare = tmp_path / "remote.git"
    bare.mkdir(parents=True)
    _git(["init", "--bare"], bare)

    seed = tmp_path / "seed"
    seed.mkdir()
    _git(["init"], seed)
    _git(["config", "user.name", "seed"], seed)
    _git(["config", "user.email", "seed@linhx.local"], seed)
    _git(["config", "commit.gpgsign", "false"], seed)

    # Nhanh main (giong repo that co runner/)
    _git(["checkout", "-b", "main"], seed)
    (seed / "README.md").write_text("linhx-engine\n", encoding="utf-8")
    _git(["add", "-A"], seed)
    _git(["commit", "-m", "khoi tao main"], seed)
    _git(["remote", "add", "origin", str(bare)], seed)
    _git(["push", "origin", "main"], seed)
    _git(["symbolic-ref", "HEAD", "refs/heads/main"], bare)

    if phieu_ban_dau is not None:
        _git(["checkout", "--orphan", "hang-doi"], seed)
        _git(["rm", "-rf", "."], seed)
        tm_moi = seed / "hang-doi" / "moi"
        tm_moi.mkdir(parents=True, exist_ok=True)
        (tm_moi / ".gitkeep").write_text("", encoding="utf-8")
        for ten, noi_dung in phieu_ban_dau.items():
            (tm_moi / f"{ten}.md").write_text(noi_dung, encoding="utf-8")
        _git(["add", "-A"], seed)
        _git(["commit", "-m", "khoi tao hang-doi"], seed)
        _git(["push", "origin", "hang-doi"], seed)

    return bare


def _clone_may(bare: Path, tmp_path: Path, ten_may: str, nhanh: str | None = None) -> dict:
    tm_clone = tmp_path / ten_may
    cmd = ["clone"]
    if nhanh:
        cmd += ["-b", nhanh]
    cmd += [str(bare), str(tm_clone)]
    _git(cmd, tmp_path)
    tm_viec = tmp_path / f"viec-{ten_may}"
    tm_viec.mkdir(parents=True, exist_ok=True)
    return {
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


def _kiem_tra_nhanh_hang_doi(bare: Path, tmp_path: Path, ten_check: str = "kiem-tra") -> Path:
    tm = tmp_path / ten_check
    if tm.exists():
        _git(["fetch", "origin", "hang-doi"], tm)
        _git(["reset", "--hard", "origin/hang-doi"], tm)
    else:
        _git(["clone", "-b", "hang-doi", str(bare), str(tm)], tmp_path)
    return tm


def test_phan_tich_phieu_va_chen_nhan():
    nd1 = "may: may-1\nloai: trinh-duyet\n\nMo trang chu kiem tra."
    p1 = hang_doi_git.phan_tich_phieu(nd1, "p-01")
    assert p1["viec"] == "p-01"
    assert p1["may"] == "may-1"
    assert p1["loai"] == "trinh-duyet"
    assert p1["de"] == "Mo trang chu kiem tra."

    dn1 = hang_doi_git.chen_dong_nhan(nd1, "may-1", "2026-11-14T07:30:00+0700")
    assert "nhan: may-1 2026-11-14T07:30:00+0700" in dn1
    assert dn1.index("nhan: may-1") < dn1.index("Mo trang chu")

    nd2 = "may: bat-ky; loai: code\n\nViet ham tinh tong."
    p2 = hang_doi_git.phan_tich_phieu(nd2, "p-02")
    assert p2["may"] == "bat-ky"
    assert p2["loai"] == "code"
    assert p2["de"] == "Viet ham tinh tong."

    nd3 = "---\nmay: may-2\nloai: khac\nche_do: kiem\ntran_phut: 15\n---\nPing may 2"
    p3 = hang_doi_git.phan_tich_phieu(nd3, "p-03")
    assert p3["may"] == "may-2"
    assert p3["loai"] == "khac"
    assert p3["che_do"] == "kiem"
    assert p3["tran_phut"] == 15
    assert p3["de"] == "Ping may 2"
    dn3 = hang_doi_git.chen_dong_nhan(nd3, "may-2", "2026-11-14T08:00:00+0700")
    assert "nhan: may-2 2026-11-14T08:00:00+0700\n---" in dn3


def test_chon_phieu_dung_may_va_uu_tien_may_rieng(tmp_path, monkeypatch):
    bare = _tao_bare_va_nhanh_hang_doi(
        tmp_path,
        {
            "01-cua-may2": "may: may-2\nloai: code\n\nViec cua may 2",
            "02-bat-ky": "may: bat-ky\nloai: code\n\nViec chung",
            "03-cua-may1": "may: may-1\nloai: trinh-duyet\n\nViec rieng may 1",
        },
    )
    cfg1 = _clone_may(bare, tmp_path, "may-1")
    da_chay = []

    def gia_agy(cfg, viec):
        da_chay.append(viec["viec"])
        return "xong", f"Da xu ly {viec['viec']}", "ok", 120, 45

    monkeypatch.setattr(hang_doi_git, "chay_agy", gia_agy)

    # Lan 1: may-1 phai uu tien phieu rieng 03-cua-may1 truoc 02-bat-ky, bo qua 01-cua-may2
    kq1 = hang_doi_git.xu_ly_mot_phieu(cfg1)
    assert kq1 is not None and kq1["viec"] == "03-cua-may1"

    # Kiem tra lich su commit co buoc nhan (dang/) va buoc xong (xong/)
    tm_kt = _kiem_tra_nhanh_hang_doi(bare, tmp_path, "kt-1")
    log_msg = _git(["log", "--oneline", "-n", "2"], tm_kt)
    assert "xong: 03-cua-may1" in log_msg
    assert "nhan: 03-cua-may1" in log_msg
    noi_dung_commit_nhan = _git(["show", "HEAD~1:hang-doi/dang/03-cua-may1.md"], tm_kt)
    assert "nhan: may-1 " in noi_dung_commit_nhan
    assert not (tm_kt / "hang-doi" / "dang" / "03-cua-may1.md").exists()
    assert (tm_kt / "hang-doi" / "xong" / "03-cua-may1" / "KET-QUA.md").is_file()

    # Lan 2: may-1 nhan not phieu 02-bat-ky
    kq2 = hang_doi_git.xu_ly_mot_phieu(cfg1)
    assert kq2 is not None and kq2["viec"] == "02-bat-ky"

    # Lan 3: chi con phieu cua may-2 -> may-1 khong nhan
    kq3 = hang_doi_git.xu_ly_mot_phieu(cfg1)
    assert kq3 is None
    assert da_chay == ["03-cua-may1", "02-bat-ky"]

    tm_kt = _kiem_tra_nhanh_hang_doi(bare, tmp_path, "kt-1")
    assert (tm_kt / "hang-doi" / "moi" / "01-cua-may2.md").is_file()


def test_hai_runner_tranh_mot_phieu_bat_ky(tmp_path, monkeypatch):
    bare = _tao_bare_va_nhanh_hang_doi(
        tmp_path,
        {"tranh-01": "may: bat-ky\nloai: code\n\nPhieu tranh chap duy nhat"},
    )
    cfg1 = _clone_may(bare, tmp_path, "may-1")
    cfg2 = _clone_may(bare, tmp_path, "may-2")

    rao_can = threading.Barrier(2, timeout=10)
    da_qua_rao = set()
    khoa_set = threading.Lock()
    chay_git_goc = hang_doi_git.chay_git

    def chay_git_co_rao(args, cwd, check=True, timeout=120):
        # Dong bo ca 2 runner ngay truoc lan push giu phieu dau tien de tao xung dot that
        if len(args) >= 2 and args[0] == "push":
            key = str(cwd)
            can_doi = False
            with khoa_set:
                if key not in da_qua_rao and len(da_qua_rao) < 2:
                    da_qua_rao.add(key)
                    can_doi = True
            if can_doi:
                rao_can.wait()
        return chay_git_goc(args, cwd, check=check, timeout=timeout)

    monkeypatch.setattr(hang_doi_git, "chay_git", chay_git_co_rao)

    cac_may_da_chay_agy = []
    khoa_agy = threading.Lock()

    def gia_agy(cfg, viec):
        with khoa_agy:
            cac_may_da_chay_agy.append((cfg["tho"], viec["viec"]))
        return "xong", f"Hoan thanh boi {cfg['tho']}", "ok", 50, 20

    monkeypatch.setattr(hang_doi_git, "chay_agy", gia_agy)

    ket_qua_luong = [None, None]
    loi_luong = []

    def chay_tho(idx, cfg):
        try:
            ket_qua_luong[idx] = hang_doi_git.xu_ly_mot_phieu(cfg)
        except Exception as e:
            loi_luong.append(e)

    t1 = threading.Thread(target=chay_tho, args=(0, cfg1))
    t2 = threading.Thread(target=chay_tho, args=(1, cfg2))
    t1.start()
    t2.start()
    t1.join(timeout=20)
    t2.join(timeout=20)

    assert not loi_luong
    thanh_cong = [x for x in ket_qua_luong if x is not None]
    that_bai = [x for x in ket_qua_luong if x is None]
    assert len(thanh_cong) == 1
    assert len(that_bai) == 1
    assert len(cac_may_da_chay_agy) == 1

    tm_kt = _kiem_tra_nhanh_hang_doi(bare, tmp_path, "kt-tranh-1")
    tep_kq = tm_kt / "hang-doi" / "xong" / "tranh-01" / "KET-QUA.md"
    assert tep_kq.is_file()
    nd_kq = tep_kq.read_text(encoding="utf-8")
    may_thang = cac_may_da_chay_agy[0][0]
    assert f"may: {may_thang}" in nd_kq
    assert f"Hoan thanh boi {may_thang}" in nd_kq
    assert not list((tm_kt / "hang-doi" / "moi").glob("*.md"))
    assert not list((tm_kt / "hang-doi" / "dang").glob("*.md"))


def test_hai_runner_tranh_hai_phieu_khong_mat_ket_qua(tmp_path, monkeypatch):
    bare = _tao_bare_va_nhanh_hang_doi(
        tmp_path,
        {
            "viec-a": "may: bat-ky\nloai: code\n\nViec A",
            "viec-b": "may: bat-ky\nloai: code\n\nViec B",
        },
    )
    cfg1 = _clone_may(bare, tmp_path, "may-1")
    cfg2 = _clone_may(bare, tmp_path, "may-2")

    rao_agy = threading.Barrier(2, timeout=10)

    def gia_agy(cfg, viec):
        # Ca 2 runner cung dang chay agy song song -> khi bao ket qua se co 1 ben phai keo lai va push lai
        rao_agy.wait()
        return "xong", f"{cfg['tho']} xong {viec['viec']}", "ok", 10, 10

    monkeypatch.setattr(hang_doi_git, "chay_agy", gia_agy)

    kq = [None, None]
    t1 = threading.Thread(target=lambda: kq.__setitem__(0, hang_doi_git.xu_ly_mot_phieu(cfg1)))
    t2 = threading.Thread(target=lambda: kq.__setitem__(1, hang_doi_git.xu_ly_mot_phieu(cfg2)))
    t1.start()
    t2.start()
    t1.join(timeout=20)
    t2.join(timeout=20)

    assert kq[0] is not None and kq[1] is not None
    assert {kq[0]["viec"], kq[1]["viec"]} == {"viec-a", "viec-b"}

    tm_kt = _kiem_tra_nhanh_hang_doi(bare, tmp_path, "kt-tranh-2")
    assert (tm_kt / "hang-doi" / "xong" / "viec-a" / "KET-QUA.md").is_file()
    assert (tm_kt / "hang-doi" / "xong" / "viec-b" / "KET-QUA.md").is_file()


def test_linhx_runner_chon_nguon_github_tu_tho_env(tmp_path, monkeypatch):
    bare = _tao_bare_va_nhanh_hang_doi(
        tmp_path,
        {"ping-01": "may: may-3\nloai: code\n\nKiem tra tich hop linhx_runner"},
    )
    cfg_mau = _clone_may(bare, tmp_path, "may-3")

    tep_env = tmp_path / "tho.env"
    tep_env.write_text(
        "\n".join(
            [
                "LINHX_NGUON=github",
                "LINHX_THO=may-3",
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
        "LINHX_REPO_HANG_DOI",
        "LINHX_THU_MUC",
        "LINHX_DRIVE",
        "LINHX_LOG_DIR",
        "LINHX_NGHI",
        "LINHX_NHANH_HANG_DOI",
        "LINHX_REMOTE_HANG_DOI",
        "LINHX_WT_HANG_DOI",
    ):
        monkeypatch.delenv(k, raising=False)

    def cam_goi_mang(*a, **kw):
        raise AssertionError("Khong duoc goi HTTP engine khi LINHX_NGUON=github")

    def gia_chay_agy(cfg, viec):
        (Path(cfg["thu_muc"]) / "ket_qua_code.py").write_text("x = 1\n", encoding="utf-8")
        return "xong", "Ping OK tu may-3", "exit=0", 33, 12

    monkeypatch.setattr(linhx_runner, "goi", cam_goi_mang)
    monkeypatch.setattr(linhx_runner, "chay_agy", gia_chay_agy)

    cfg = linhx_runner.doc_env(tep_env)
    assert cfg["nguon"] == "github"
    assert cfg["tho"] == "may-3"

    linhx_runner.vong(cfg, mot_lan=True)

    tm_kt = _kiem_tra_nhanh_hang_doi(bare, tmp_path, "kt-env")
    nd = (tm_kt / "hang-doi" / "xong" / "ping-01" / "KET-QUA.md").read_text(encoding="utf-8")
    assert "trang_thai: xong" in nd
    assert "may: may-3" in nd
    assert "tep_doi: ket_qua_code.py" in nd
    assert "token: vao=33 ra=12" in nd
    assert "Ping OK tu may-3" in nd
    assert len(nd) <= 2000


def test_cat_ngan_ket_qua_va_xu_ly_loi_agy(tmp_path, monkeypatch):
    bare = _tao_bare_va_nhanh_hang_doi(
        tmp_path,
        {
            "01-dai": "may: bat-ky\nloai: code\n\nTra ve van ban rat dai",
            "02-loi": "may: bat-ky\nloai: code\n\nGay loi bat ngo",
        },
    )
    cfg = _clone_may(bare, tmp_path, "may-1")

    def gia_agy(c, viec):
        if viec["viec"] == "01-dai":
            return "xong", "A" * 5000, "ok", 100, 500
        raise RuntimeError("agy gap su co")

    monkeypatch.setattr(hang_doi_git, "chay_agy", gia_agy)
    linhx_runner.vong(cfg, mot_lan=True)

    tm_kt = _kiem_tra_nhanh_hang_doi(bare, tmp_path, "kt-dai-loi")
    kq_dai = (tm_kt / "hang-doi" / "xong" / "01-dai" / "KET-QUA.md").read_text(encoding="utf-8")
    assert len(kq_dai) <= 2000
    assert "trang_thai: xong" in kq_dai

    kq_loi = (tm_kt / "hang-doi" / "xong" / "02-loi" / "KET-QUA.md").read_text(encoding="utf-8")
    assert "trang_thai: loi" in kq_loi
    assert "agy gap su co" in kq_loi
    assert not list((tm_kt / "hang-doi" / "dang").glob("*.md"))


def test_nhanh_hang_doi_chua_ton_tai_va_clone_truc_tiep_hang_doi(tmp_path, monkeypatch):
    # Truong hop 1: remote chua co nhanh hang-doi -> khong loi, tra ve None
    bare_trong = _tao_bare_va_nhanh_hang_doi(tmp_path / "th1", phieu_ban_dau=None)
    cfg_trong = _clone_may(bare_trong, tmp_path / "th1", "may-1")
    assert hang_doi_git.xu_ly_mot_phieu(cfg_trong) is None

    # Truong hop 2: repo_hang_doi da checkout truc tiep tren nhanh hang-doi + che_do=kiem
    bare_hd = _tao_bare_va_nhanh_hang_doi(
        tmp_path / "th2",
        {"ping-kiem": "may: may-1\nloai: khac\nche_do: kiem\n\nXin chao"},
    )
    cfg_hd = _clone_may(bare_hd, tmp_path / "th2", "may-1", nhanh="hang-doi")
    kq = hang_doi_git.xu_ly_mot_phieu(cfg_hd)
    assert kq is not None and kq["trang_thai"] == "xong"
    tm_kt = _kiem_tra_nhanh_hang_doi(bare_hd, tmp_path / "th2", "kt-th2")
    nd = (tm_kt / "hang-doi" / "xong" / "ping-kiem" / "KET-QUA.md").read_text(encoding="utf-8")
    assert "trang_thai: xong" in nd
    assert "Xin chao" in nd
