from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
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
    tm_goc = goc_viec / f"pytest-tmp-h2-{os.getpid()}-{uuid.uuid4().hex[:8]}"
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


def _tao_bare_hang_doi(tmp_path: Path, phieu: dict[str, str]) -> Path:
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
    for ten, nd in phieu.items():
        (tm_moi / f"{ten}.md").write_text(nd, encoding="utf-8")
    _git(["add", "-A"], seed)
    _git(["commit", "-m", "init hang-doi"], seed)
    _git(["push", "origin", "hang-doi"], seed)
    return bare


def test_duong_dan_mac_dinh_drive_va_log(monkeypatch):
    monkeypatch.delenv("LINHX_DRIVE", raising=False)
    monkeypatch.delenv("LINHX_LOG_DIR", raising=False)

    assert hang_doi_git._thu_muc_drive() == Path(r"G:\My Drive\LINHX-VIEC")
    assert hang_doi_git.duong_dan_log_phieu("phieu-01") == Path(r"D:\linhx\linhx-runner\log\phieu-01.jsonl")

    # Chan leo thu muc khi id chua '..' hoac dau gach cheo
    duong_log_la = hang_doi_git.duong_dan_log_phieu("../../bi-mat")
    assert duong_log_la.parent == Path(r"D:\linhx\linhx-runner\log")
    assert ".." not in duong_log_la.name


def test_cat_ket_qua_md_luon_nho_hon_hoac_bang_2000_ky_tu():
    # Ngan -> giu nguyen, khong chen dau cat
    ngan = hang_doi_git.tao_ket_qua_md("p-ngan", "may-1", "xong", "Ket qua ngan gon.", token_vao=10, token_ra=5)
    assert len(ngan) <= 2000
    assert "Ket qua ngan gon." in ngan
    assert "[cat bot]" not in ngan

    # Dung bien 2000 ky tu -> khong cat
    mau_rong = hang_doi_git.tao_ket_qua_md("p-bien", "may-1", "xong", "")
    do_dai_than_vua_khit = 2000 - len(mau_rong) - 1  # -1 cho '\n' cuoi
    vua_khit = hang_doi_git.tao_ket_qua_md("p-bien", "may-1", "xong", "B" * do_dai_than_vua_khit)
    assert len(vua_khit) == 2000
    assert "[cat bot]" not in vua_khit

    # Vuot 1 ky tu va vuot rat xa (Unicode tieng Viet) -> cat <= 2000, giu dau + cuoi
    vuot_nhe = hang_doi_git.tao_ket_qua_md("p-bien", "may-1", "xong", "B" * (do_dai_than_vua_khit + 1))
    assert len(vuot_nhe) <= 2000
    assert "[cat bot]" in vuot_nhe

    van_ban_dai = "MỞ_ĐẦU_BÁO_CÁO\n" + ("Dòng kiểm tra tiếng Việt có dấu số 12345.\n" * 400) + "KẾT_LUẬN_CUỐI_CÙNG"
    kq_dai = hang_doi_git.tao_ket_qua_md(
        "p-dai",
        "may-2",
        "xong",
        van_ban_dai,
        phut=3.5,
        token_vao=9000,
        token_ra=2500,
        tep_doi=[f"thu-muc-con-rat-dai/tep-so-{i:02d}-kiem-tra-gioi-han.py" for i in range(20)],
        drive="G:\\My Drive\\LINHX-VIEC\\p-dai\\" + ("tep-nang-rat-dai-" * 30) + ".zip",
    )
    assert len(kq_dai) <= 2000
    assert "phieu: p-dai\n" in kq_dai
    assert "trang_thai: xong\n" in kq_dai
    assert "MỞ_ĐẦU_BÁO_CÁO" in kq_dai
    assert "KẾT_LUẬN_CUỐI_CÙNG" in kq_dai
    assert "[cat bot]" in kq_dai

    # Khi ket_qua rong, dung nhat_ky dai -> van giu <= 2000 va giu ca exit dau + loi cuoi
    nk_dai = "exit=1 giay=45\n--- stderr ---\n" + ("trace line\n" * 1000) + "ValueError: loi cuoi cung"
    kq_loi = hang_doi_git.tao_ket_qua_md("p-loi", "may-3", "loi", None, nhat_ky=nk_dai)
    assert len(kq_loi) <= 2000
    assert "exit=1 giay=45" in kq_loi
    assert "ValueError: loi cuoi cung" in kq_loi


def test_chep_tep_tren_1mb_sang_drive_va_bo_qua_tep_nho(tmp_path):
    nguon = tmp_path / "viec"
    drive = tmp_path / "gia-drive"
    (nguon / "anh").mkdir(parents=True)

    (nguon / "nho.txt").write_bytes(b"xin chao")
    (nguon / "dung-1mb.bin").write_bytes(b"x" * (1024 * 1024))

    # Chua co file > 1 MB -> khong tao thu muc tren Drive
    assert hang_doi_git.chep_tep_nang_sang_drive(nguon, "h2-01", thu_muc_drive=drive) == []
    assert not (drive / "h2-01").exists()

    # Them 2 file > 1 MB (o goc va thu muc con)
    du_lieu_pdf = b"%PDF-" + (b"p" * (1024 * 1024 + 17))
    du_lieu_png = b"\x89PNG" + (b"i" * (1024 * 1024 + 2048))
    (nguon / "bao-cao.pdf").write_bytes(du_lieu_pdf)
    (nguon / "anh" / "man-hinh.png").write_bytes(du_lieu_png)

    da_chep = hang_doi_git.chep_tep_nang_sang_drive(nguon, "h2-01", thu_muc_drive=drive)
    assert len(da_chep) == 2
    assert (drive / "h2-01" / "bao-cao.pdf").read_bytes() == du_lieu_pdf
    assert (drive / "h2-01" / "anh" / "man-hinh.png").read_bytes() == du_lieu_png
    assert not (drive / "h2-01" / "nho.txt").exists()
    assert not (drive / "h2-01" / "dung-1mb.bin").exists()


def test_xu_ly_phieu_tich_hop_cat_ket_qua_chep_drive_va_ghi_log_jsonl(tmp_path, monkeypatch):
    bare = _tao_bare_hang_doi(
        tmp_path,
        {"h2-full": "may: may-1\nloai: trinh-duyet\n\nChup man hinh va xuat bao cao chi tiet."},
    )
    tm_clone = tmp_path / "repo-may-1"
    _git(["clone", str(bare), str(tm_clone)], tmp_path)

    tm_viec = tmp_path / "viec-may-1"
    tm_viec.mkdir(parents=True)
    # File nang ton tai TRUOC khi nhan phieu -> khong duoc chep nham sang phieu moi
    (tm_viec / "cu-truoc-do.zip").write_bytes(b"z" * (1024 * 1024 + 100))

    tm_drive_gia = tmp_path / "google-drive" / "LINHX-VIEC"
    tm_log_gia = tmp_path / "linhx-runner" / "log"
    monkeypatch.delenv("LINHX_DRIVE", raising=False)
    monkeypatch.delenv("LINHX_LOG_DIR", raising=False)
    monkeypatch.setattr(hang_doi_git, "THU_MUC_DRIVE_MAC_DINH", tm_drive_gia)
    monkeypatch.setattr(hang_doi_git, "THU_MUC_LOG_MAC_DINH", tm_log_gia)

    ket_qua_day_du = "BAT_DAU_PHAN_TICH\n" + ("Chi tiet buoc kiem tra giao dien web.\n" * 250) + "KET_THUC_PHAN_TICH"
    nhat_ky_day_du = "exit=0 giay=18\n--- stderr ---\n" + ("debug line\n" * 300)

    def gia_agy(cfg, viec):
        goc = Path(cfg["thu_muc"])
        (goc / "tom-tat.md").write_text("# Tom tat\nOK\n", encoding="utf-8")
        (goc / "dung-1mb.dat").write_bytes(b"d" * (1024 * 1024))
        (goc / "quay-man-hinh.mp4").write_bytes(b"m" * (1024 * 1024 + 500))
        (goc / "xuat" / "ket-qua.pdf").parent.mkdir(parents=True, exist_ok=True)
        (goc / "xuat" / "ket-qua.pdf").write_bytes(b"k" * (1024 * 1024 + 900))
        return "xong", ket_qua_day_du, nhat_ky_day_du, 1500, 620

    monkeypatch.setattr(hang_doi_git, "chay_agy", gia_agy)

    cfg = {
        "nguon": "github",
        "tho": "may-1",
        "agy": "agy-gia",
        "agy_args": "--output-format json",
        "thu_muc": tm_viec,
        "nghi": 0.01,
        "repo_hang_doi": tm_clone,
        "nhanh_hang_doi": "hang-doi",
        "remote_hang_doi": "origin",
        "wt_hang_doi": "",
    }
    kq = hang_doi_git.xu_ly_mot_phieu(cfg)
    assert kq is not None
    assert kq["trang_thai"] == "xong"
    assert len(kq["tep_drive"]) == 2

    # 1. Kiem tra KET-QUA.md tren nhanh hang-doi <= 2000 ky tu va khong commit file nang hay log
    tm_kt = tmp_path / "kiem-tra-remote"
    _git(["clone", "-b", "hang-doi", str(bare), str(tm_kt)], tmp_path)
    tep_kq = tm_kt / "hang-doi" / "xong" / "h2-full" / "KET-QUA.md"
    assert tep_kq.is_file()
    nd_kq = tep_kq.read_text(encoding="utf-8")
    assert len(nd_kq) <= 2000
    assert "trang_thai: xong" in nd_kq
    assert "BAT_DAU_PHAN_TICH" in nd_kq
    assert "KET_THUC_PHAN_TICH" in nd_kq
    assert str(tm_drive_gia / "h2-full") in nd_kq
    assert "quay-man-hinh.mp4" in nd_kq
    assert "ket-qua.pdf" in nd_kq

    tat_ca_tep_git = [
        p.relative_to(tm_kt).as_posix()
        for p in tm_kt.rglob("*")
        if p.is_file() and not p.relative_to(tm_kt).as_posix().startswith(".git/")
    ]
    assert tat_ca_tep_git == ["hang-doi/xong/h2-full/KET-QUA.md"]

    # 2. Kiem tra Drive: chi chua 2 file > 1 MB moi tao trong phieu h2-full
    assert (tm_drive_gia / "h2-full" / "quay-man-hinh.mp4").stat().st_size == 1024 * 1024 + 500
    assert (tm_drive_gia / "h2-full" / "xuat" / "ket-qua.pdf").stat().st_size == 1024 * 1024 + 900
    assert not (tm_drive_gia / "h2-full" / "tom-tat.md").exists()
    assert not (tm_drive_gia / "h2-full" / "dung-1mb.dat").exists()
    assert not (tm_drive_gia / "h2-full" / "cu-truoc-do.zip").exists()

    # 3. Kiem tra log JSONL day du tren may (<id>.jsonl)
    tep_log = tm_log_gia / "h2-full.jsonl"
    assert tep_log.is_file()
    cac_dong = [json.loads(d) for d in tep_log.read_text(encoding="utf-8").splitlines() if d.strip()]
    su_kien = [d["su_kien"] for d in cac_dong]
    assert su_kien == ["nhan", "ket_qua", "bao_ket_qua"]

    dong_nhan = cac_dong[0]
    assert dong_nhan["viec"] == "h2-full"
    assert dong_nhan["de"] == "Chup man hinh va xuat bao cao chi tiet."

    dong_kq = cac_dong[1]
    assert dong_kq["ket_qua"] == ket_qua_day_du
    assert len(dong_kq["ket_qua"]) > 2000
    assert dong_kq["nhat_ky"] == nhat_ky_day_du
    assert dong_kq["token_vao"] == 1500
    assert dong_kq["token_ra"] == 620
    assert len(dong_kq["tep_drive"]) == 2


def test_chay_agy_that_qua_monkeypatch_subprocess_ghi_agy_raw_vao_jsonl(tmp_path, monkeypatch):
    bare = _tao_bare_hang_doi(
        tmp_path,
        {"h2-raw": "may: bat-ky\nloai: code\n\nKiem tra luu stdout stderr day du"},
    )
    tm_clone = tmp_path / "repo-may-2"
    _git(["clone", str(bare), str(tm_clone)], tmp_path)
    tm_viec = tmp_path / "viec-may-2"
    tm_viec.mkdir(parents=True)
    tm_log = tmp_path / "log-may-2"
    tm_drive = tmp_path / "drive-may-2"

    phan_hoi_dai = "PHAN_HOI_DAU_" + ("X" * 4500) + "_PHAN_HOI_CUOI"
    stderr_dai = "STDERR_DAU_" + ("E" * 9500) + "_STDERR_CUOI"
    stdout_json = json.dumps(
        {
            "status": "SUCCESS",
            "response": phan_hoi_dai,
            "usage": {"input_tokens": 410, "output_tokens": 890},
        },
        ensure_ascii=False,
    )

    subprocess_run_goc = subprocess.run

    def gia_subprocess_run(cmd, *a, **kw):
        if cmd and cmd[0] == "agy-khong-can-ton-tai":
            return subprocess.CompletedProcess(cmd, 0, stdout=stdout_json, stderr=stderr_dai)
        return subprocess_run_goc(cmd, *a, **kw)

    monkeypatch.setattr(linhx_runner.subprocess, "run", gia_subprocess_run)

    cfg = {
        "nguon": "github",
        "tho": "may-2",
        "agy": "agy-khong-can-ton-tai",
        "agy_args": "--output-format json",
        "thu_muc": tm_viec,
        "thu_muc_drive": tm_drive,
        "thu_muc_log": tm_log,
        "nghi": 0.01,
        "repo_hang_doi": tm_clone,
        "nhanh_hang_doi": "hang-doi",
        "remote_hang_doi": "origin",
        "wt_hang_doi": "",
    }
    kq = hang_doi_git.xu_ly_mot_phieu(cfg)
    assert kq is not None and kq["trang_thai"] == "xong"

    tep_log = tm_log / "h2-raw.jsonl"
    cac_dong = [json.loads(d) for d in tep_log.read_text(encoding="utf-8").splitlines() if d.strip()]
    theo_su_kien = {d["su_kien"]: d for d in cac_dong}
    assert "agy_raw" in theo_su_kien
    assert theo_su_kien["agy_raw"]["stderr"] == stderr_dai
    assert len(theo_su_kien["agy_raw"]["stderr"]) > 9000
    assert theo_su_kien["ket_qua"]["ket_qua"] == phan_hoi_dai
    assert theo_su_kien["ket_qua"]["token_vao"] == 410
    assert theo_su_kien["ket_qua"]["token_ra"] == 890

    tm_kt = tmp_path / "kt-raw"
    _git(["clone", "-b", "hang-doi", str(bare), str(tm_kt)], tmp_path)
    nd_kq = (tm_kt / "hang-doi" / "xong" / "h2-raw" / "KET-QUA.md").read_text(encoding="utf-8")
    assert len(nd_kq) <= 2000
    assert "PHAN_HOI_DAU_" in nd_kq
    assert "_PHAN_HOI_CUOI" in nd_kq
