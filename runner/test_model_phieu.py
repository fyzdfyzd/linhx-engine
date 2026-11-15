from __future__ import annotations

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
    # Dùng thư mục tạm bên trong runner/viec (không cần mạng hay ổ ngoài)
    goc_viec = linhx_runner.GOC / "viec"
    viec_da_co = goc_viec.exists()
    tm_goc = goc_viec / f"pytest-tmp-model-{os.getpid()}-{uuid.uuid4().hex[:8]}"
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


def _tao_bare_hang_doi(tmp_path: Path, phieu_moi: dict[str, str]) -> Path:
    bare = tmp_path / f"remote-{uuid.uuid4().hex[:6]}.git"
    bare.mkdir(parents=True)
    _git(["init", "--bare"], bare)

    seed = tmp_path / f"seed-{uuid.uuid4().hex[:6]}"
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
    _git(["add", "-A"], seed)
    _git(["commit", "-m", "init hang-doi"], seed)
    _git(["push", "origin", "hang-doi"], seed)
    return bare


def _clone_may(bare: Path, tmp_path: Path, ten_may: str = "may-2", **them_cfg) -> dict:
    tm_clone = tmp_path / f"repo-{ten_may}-{uuid.uuid4().hex[:4]}"
    _git(["clone", str(bare), str(tm_clone)], tmp_path)
    tm_viec = tmp_path / f"viec-{ten_may}-{uuid.uuid4().hex[:4]}"
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


def _doc_ket_qua_remote(bare: Path, tmp_path: Path, phieu_id: str) -> str:
    tm = tmp_path / f"kt-{uuid.uuid4().hex[:6]}"
    _git(["clone", "-b", "hang-doi", str(bare), str(tm)], tmp_path)
    return (tm / "hang-doi" / "xong" / phieu_id / "KET-QUA.md").read_text(encoding="utf-8")


class _TienTrinhGiaXong:
    def __init__(self, stdout_dict: dict | None = None, returncode: int = 0):
        du_lieu = json.dumps(
            stdout_dict or {"status": "SUCCESS", "response": "ok", "usage": {"input_tokens": 10, "output_tokens": 2}},
            ensure_ascii=False,
        ).encode("utf-8")
        self.stdout = io.BytesIO(du_lieu)
        self.stderr = io.BytesIO(b"")
        self.returncode = returncode
        self.pid = 42424

    def poll(self):
        return self.returncode

    def wait(self, timeout=None):
        return self.returncode

    def kill(self):
        pass


class _LuongChanGia:
    """Luồng giả chặn giống pipe thật: không trả byte nào khi tiến trình đang tính ngầm,
    chỉ trả dữ liệu cuối hoặc EOF khi tiến trình hoàn tất / bị kill."""

    def __init__(self) -> None:
        self._xong = threading.Event()
        self._du_lieu = b""
        self._da_doc = False

    def dong_voi(self, du_lieu: bytes = b"") -> None:
        self._du_lieu = du_lieu
        self._xong.set()

    def read(self, _kich_thuoc: int = -1) -> bytes:
        self._xong.wait(timeout=5.0)
        if self._da_doc:
            return b""
        self._da_doc = True
        return self._du_lieu

    def close(self) -> None:
        self._xong.set()


class _TienTrinhGiaDangChay:
    def __init__(self, pid: int = 71717):
        self.pid = pid
        self.returncode = None
        self.stdout = _LuongChanGia()
        self.stderr = _LuongChanGia()
        self.da_kill = False

    def poll(self):
        return self.returncode

    def hoan_tat(self, phan_hoi: str = "xong") -> None:
        du_lieu = json.dumps(
            {"status": "SUCCESS", "response": phan_hoi, "usage": {"input_tokens": 20, "output_tokens": 5}},
            ensure_ascii=False,
        ).encode("utf-8")
        self.returncode = 0
        self.stdout.dong_voi(du_lieu)
        self.stderr.dong_voi(b"")

    def kill(self):
        self.da_kill = True
        self.returncode = -9
        self.stdout.dong_voi(b"")
        self.stderr.dong_voi(b"")

    def wait(self, timeout=None):
        if self.returncode is None:
            self.returncode = 0
        self.stdout.dong_voi(b"")
        self.stderr.dong_voi(b"")
        return self.returncode


def test_uu_tien_1_header_model_thang_tien_to_va_env_ghi_dau_ket_qua(tmp_path, monkeypatch):
    # 1. Header `model:` thắng tiền tố `dp` trong tên phiếu `yl-dp-chia-viec` và thắng `LINHX_MODEL`,
    #    đồng thời ghi `model: <id thật dùng>` ở dòng đầu tiên của KET-QUA.md.
    monkeypatch.setenv("LINHX_MODEL", "gemini-3.8-flash-low")
    ds_cmd: list[list[str]] = []
    monkeypatch.setattr(
        linhx_runner,
        "_tao_tien_trinh_agy",
        lambda cmd, *a, **kw: (ds_cmd.append(list(cmd)), _TienTrinhGiaXong())[1],
    )

    phieu_txt = (
        "may: may-2\n"
        "loai: code\n"
        "model: gemini-4-argon-high # ghi đè tiền tố dp\n\n"
        "Trả lời ok.\n"
    )
    bare = _tao_bare_hang_doi(tmp_path, {"yl-dp-chia-viec": phieu_txt})
    cfg = _clone_may(
        bare,
        tmp_path,
        agy_args="--output-format json --model gemini-4-carbon-low --model=cu-nua --print-timeout 600s",
    )

    kq = hang_doi_git.xu_ly_mot_phieu(cfg)
    assert kq is not None and kq["trang_thai"] == "xong"
    assert len(ds_cmd) == 1
    cmd = ds_cmd[0]
    assert cmd.count("--model") == 1
    assert not any(arg.startswith("--model=") for arg in cmd)
    vi_tri = cmd.index("--model")
    assert cmd[vi_tri + 1] == "gemini-4-argon-high"
    assert "gemini-pro-orchestrator" not in cmd
    assert "gemini-3.8-flash-low" not in cmd

    nd_kq = _doc_ket_qua_remote(bare, tmp_path, "yl-dp-chia-viec")
    assert nd_kq.splitlines()[0] == "model: gemini-4-argon-high"


def test_uu_tien_2_tien_to_loai_viec_tu_file_json_thang_linhx_model(tmp_path, monkeypatch):
    # 2. Kiểm tra file `runner/model-theo-loai.json` đúng bảng yêu cầu và tên phiếu `<du-an>-<loai>-<viec>`
    #    lấy đoạn thứ 2, ưu tiên hơn `LINHX_MODEL`.
    bang_ky_vong = {
        "dp": "gemini-pro-orchestrator",
        "code": "gemini-pro-orchestrator",
        "test": "gemini-4-argon-high",
        "trien": "gemini-4-argon-high",
        "gop": "gemini-4-hydrogen-high",
        "do": "gemini-4-hydrogen-high",
        "td": "gemini-4-hydrogen-high",
        "kiem": "gemini-4-hydrogen-low",
    }
    assert linhx_runner.TEP_MODEL_THEO_LOAI.is_file()
    assert json.loads(linhx_runner.TEP_MODEL_THEO_LOAI.read_text(encoding="utf-8")) == bang_ky_vong

    monkeypatch.setenv("LINHX_MODEL", "gemini-4-carbon-low")
    ds_cmd: list[list[str]] = []
    monkeypatch.setattr(
        linhx_runner,
        "_tao_tien_trinh_agy",
        lambda cmd, *a, **kw: (ds_cmd.append(list(cmd)), _TienTrinhGiaXong())[1],
    )

    for loai, model_mong_doi in bang_ky_vong.items():
        ds_cmd.clear()
        ma_phieu = f"duan-{loai}-cong-viec-01"
        viec = hang_doi_git.phan_tich_phieu("may: may-2\nloai: code\n\nLàm việc theo tiền tố.", ma_phieu)
        cfg = {
            "tho": "may-2",
            "agy": "agy-gia",
            "agy_args": "--output-format json",
            "thu_muc": tmp_path / f"tm-{loai}",
        }
        tt, _, _, _, _ = linhx_runner.chay_agy(cfg, viec)
        assert tt == "xong"
        cmd = ds_cmd[0]
        vi_tri = cmd.index("--model")
        assert cmd[vi_tri + 1] == model_mong_doi
        assert viec["_model_da_dung"] == model_mong_doi
        kq_md = hang_doi_git.tao_ket_qua_md(ma_phieu, "may-2", tt, "ok", model=viec["_model_da_dung"])
        assert kq_md.splitlines()[0] == f"model: {model_mong_doi}"


def test_uu_tien_3_linhx_model_trong_tho_env_va_bien_moi_truong(tmp_path, monkeypatch):
    # 3. Không có header `model:` và tiền tố tên phiếu không có trong bảng -> dùng `LINHX_MODEL` trong tho.env
    tep_env = tmp_path / "tho.env"
    tm_viec = tmp_path / "viec-env"
    tep_env.write_text(
        f"LINHX_THO=may-2\n"
        f"AGY_CMD=agy-gia\n"
        f"AGY_ARGS=--model model-cu --output-format json\n"
        f"LINHX_MODEL=gemini-3.8-flash-medium\n"
        f"LINHX_THU_MUC={tm_viec}\n",
        encoding="utf-8",
    )
    for bien in ("LINHX_THO", "AGY_CMD", "AGY_ARGS", "LINHX_MODEL", "LINHX_THU_MUC"):
        monkeypatch.delenv(bien, raising=False)

    cfg = linhx_runner.doc_env(tep_env)
    assert cfg["model"] == "gemini-3.8-flash-medium"

    ds_cmd: list[list[str]] = []
    monkeypatch.setattr(
        linhx_runner,
        "_tao_tien_trinh_agy",
        lambda cmd, *a, **kw: (ds_cmd.append(list(cmd)), _TienTrinhGiaXong())[1],
    )

    viec = hang_doi_git.phan_tich_phieu("may: may-2\nloai: code\n\nChạy mặc định theo tho.env.", "yl-khac-01")
    tt, kq, _, _, _ = linhx_runner.chay_agy(cfg, viec)
    assert tt == "xong"
    assert kq == "ok"
    cmd = ds_cmd[0]
    assert cmd.count("--model") == 1
    assert cmd[cmd.index("--model") + 1] == "gemini-3.8-flash-medium"
    assert "model-cu" not in cmd
    assert viec["_model_da_dung"] == "gemini-3.8-flash-medium"


def test_uu_tien_4_khong_gi_thi_giu_agy_args_nhu_cu(tmp_path, monkeypatch):
    # 4. Không header, không khớp tiền tố, không LINHX_MODEL -> giữ AGY_ARGS như cũ và ghi đúng dòng model:
    monkeypatch.delenv("LINHX_MODEL", raising=False)
    ds_cmd: list[list[str]] = []
    monkeypatch.setattr(
        linhx_runner,
        "_tao_tien_trinh_agy",
        lambda cmd, *a, **kw: (ds_cmd.append(list(cmd)), _TienTrinhGiaXong())[1],
    )

    viec1 = hang_doi_git.phan_tich_phieu("may: bat-ky\nloai: code\n\nKhông cấu hình model.", "mac-dinh-01")
    cfg_khong_co = {
        "tho": "may-1",
        "agy": "agy-gia",
        "agy_args": "--output-format json --print-timeout 600s",
        "thu_muc": tmp_path / "viec-md-1",
    }
    tt1, _, _, _, _ = linhx_runner.chay_agy(cfg_khong_co, viec1)
    assert tt1 == "xong"
    assert "--model" not in ds_cmd[0]
    assert ds_cmd[0][-4:] == ["--output-format", "json", "--print-timeout", "600s"]
    assert viec1["_model_da_dung"] == "mac-dinh"
    kq_md1 = hang_doi_git.tao_ket_qua_md("mac-dinh-01", "may-1", tt1, "ok", model=viec1["_model_da_dung"])
    assert kq_md1.splitlines()[0] == "model: mac-dinh"

    viec2 = hang_doi_git.phan_tich_phieu("may: bat-ky\nloai: code\n\nGiữ cờ có sẵn.", "mac-dinh-02")
    cfg_co_san_args = {
        "tho": "may-1",
        "agy": "agy-gia",
        "agy_args": "--output-format json --model claude-sonnet-5-5-medium",
        "thu_muc": tmp_path / "viec-md-2",
    }
    tt2, _, _, _, _ = linhx_runner.chay_agy(cfg_co_san_args, viec2)
    assert tt2 == "xong"
    assert ds_cmd[1][-4:] == ["--output-format", "json", "--model", "claude-sonnet-5-5-medium"]
    assert viec2["_model_da_dung"] == "claude-sonnet-5-5-medium"
    kq_md2 = hang_doi_git.tao_ket_qua_md("mac-dinh-02", "may-1", tt2, "ok", model=viec2["_model_da_dung"])
    assert kq_md2.splitlines()[0] == "model: claude-sonnet-5-5-medium"


@pytest.mark.parametrize(
    "ten_doc",
    [
        "gemini; calc.exe",
        "gemini && whoami",
        "gemini | dir",
        "$(whoami)",
        "`id`",
        "gemini --dangerously-skip-permissions",
        "--dangerously-skip-permissions",
        "-p",
        "../gemini",
        "gemini/../../bin/sh",
        "gemini\n--mode auto",
        "gemini' OR '1'='1",
        'gemini" --agent evil',
        "gemini@latest",
    ],
)
def test_ten_model_doc_bi_tu_choi_khong_goi_agy(tmp_path, monkeypatch, ten_doc):
    # 5. Tên model chứa ký tự ngoài chữ, số, `-`, `.`, `_` (hoặc giả làm cờ `-...`) bị từ chối ngay
    da_goi_popen = [False]

    def cam_goi(*a, **kw):
        da_goi_popen[0] = True
        raise AssertionError("Không được phép khởi chạy agy khi tên model không hợp lệ")

    monkeypatch.setattr(linhx_runner, "_tao_tien_trinh_agy", cam_goi)

    cfg = {
        "tho": "may-2",
        "agy": "agy-gia",
        "agy_args": "--output-format json",
        "thu_muc": tmp_path / "viec-doc",
    }
    viec_doc = {
        "viec": "phieu-doc",
        "che_do": "thuc",
        "de": "Thử chèn lệnh",
        "meta": {"model": ten_doc},
    }
    tt, kq, nk, _, _ = linhx_runner.chay_agy(cfg, viec_doc)
    assert tt == "loi"
    assert kq is None
    assert "tên model không hợp lệ" in nk
    assert da_goi_popen[0] is False

    monkeypatch.setenv("LINHX_MODEL", ten_doc)
    viec_sach = {"viec": "phieu-sach", "che_do": "thuc", "de": "Đề bình thường", "meta": {}}
    tt_env, kq_env, nk_env, _, _ = linhx_runner.chay_agy(cfg, viec_sach)
    assert tt_env == "loi"
    assert kq_env is None
    assert "tên model không hợp lệ" in nk_env
    assert da_goi_popen[0] is False


def test_ten_model_hop_le_chua_chu_so_gach_cham_gach_duoi_va_parse_agy_models():
    ok, sach = linhx_runner.kiem_tra_ten_model("gemini_4.0-custom_v2")
    assert ok is True and sach == "gemini_4.0-custom_v2"

    mau_dau_ra = (
        "Fetching available models...\n"
        "gemini-4-argon-high\tGemini 4 Argon (High)\n"
        "gemini-pro-orchestrator\tOrchestrator (Carbon)\n"
        "gemini_4.0-custom_v2\tCustom Model\n"
    )
    ds = linhx_runner.phan_tich_dau_ra_agy_models(mau_dau_ra)
    assert ds == ["gemini-4-argon-high", "gemini-pro-orchestrator", "gemini_4.0-custom_v2"]


def test_model_la_khong_co_trong_agy_models_canh_bao_va_chay_mac_dinh(tmp_path, monkeypatch):
    # 6. Model không có trong `agy models` -> ghi cảnh báo vào KET-QUA.md, chạy model mặc định, không lỗi
    ds_cmd: list[list[str]] = []
    monkeypatch.setattr(
        linhx_runner,
        "_tao_tien_trinh_agy",
        lambda cmd, *a, **kw: (ds_cmd.append(list(cmd)), _TienTrinhGiaXong())[1],
    )
    monkeypatch.setattr(
        linhx_runner,
        "_doc_ds_model_agy",
        lambda _cfg=None: ["gemini-pro-orchestrator", "gemini-4-hydrogen-low"],
    )

    bare = _tao_bare_hang_doi(
        tmp_path,
        {
            "yl-code-model-la": (
                "may: may-2\n"
                "loai: code\n"
                "model: gemini-99-khong-ton-tai\n\n"
                "Thử model lạ không có trong agy models.\n"
            )
        },
    )
    cfg = _clone_may(
        bare,
        tmp_path,
        agy_args="--output-format json --model model-cu-san-co",
    )

    kq = hang_doi_git.xu_ly_mot_phieu(cfg)
    assert kq is not None
    assert kq["trang_thai"] == "xong"  # không lỗi
    assert len(ds_cmd) == 1
    cmd = ds_cmd[0]
    assert "--model" not in cmd
    assert "gemini-99-khong-ton-tai" not in cmd
    assert "model-cu-san-co" not in cmd

    nd_kq = _doc_ket_qua_remote(bare, tmp_path, "yl-code-model-la")
    assert nd_kq.splitlines()[0] == "model: mac-dinh"
    assert "trang_thai: xong" in nd_kq
    assert "gemini-99-khong-ton-tai" in nd_kq
    assert "agy models" in nd_kq
    assert "mặc định" in nd_kq


def test_cau_chen_cam_background_task_co_trong_moi_de(tmp_path, monkeypatch):
    # 7. Runner tự chèn cuối mọi đề câu "Không dùng background task hay thợ con trừ khi phiếu cho phép; chạy lệnh tiền cảnh."
    cau_bat_buoc = "Không dùng background task hay thợ con trừ khi phiếu cho phép; chạy lệnh tiền cảnh."
    assert linhx_runner.CAU_NHAC_TIEN_CANH == cau_bat_buoc

    ds_cmd: list[list[str]] = []
    monkeypatch.setattr(
        linhx_runner,
        "_tao_tien_trinh_agy",
        lambda cmd, *a, **kw: (ds_cmd.append(list(cmd)), _TienTrinhGiaXong())[1],
    )

    cfg = {
        "tho": "may-2",
        "agy": "agy-gia",
        "agy_args": "--output-format json",
        "thu_muc": tmp_path / "viec-de",
    }
    # Đề ngắn
    tt1, _, _, _, _ = linhx_runner.chay_agy(cfg, {"viec": "de-ngan", "de": "Kiểm tra câu chèn."})
    assert tt1 == "xong"
    de_gui_1 = ds_cmd[0][2]
    assert de_gui_1.endswith(cau_bat_buoc)
    assert de_gui_1.count(cau_bat_buoc) == 1

    # Không chèn trùng nếu đề đã có sẵn câu đó
    de_co_san = f"Làm việc X.\n\n{cau_bat_buoc}"
    assert linhx_runner.ghep_de_gui_agy(de_co_san).count(cau_bat_buoc) == 1

    # Đề dài vượt DE_DAI -> cả file đề và tham số -p đều có câu chèn
    de_dai = "Nội dung chi tiết. " * 400
    tt2, _, _, _, _ = linhx_runner.chay_agy(cfg, {"viec": "de-dai", "de": de_dai})
    assert tt2 == "xong"
    tep_de = Path(cfg["thu_muc"]) / "de-de-dai.md"
    assert tep_de.is_file()
    assert tep_de.read_text(encoding="utf-8").endswith(cau_bat_buoc)
    assert cau_bat_buoc in ds_cmd[1][2]


def test_bo_canh_mac_dinh_20_phut_cpu_tang_va_theo_doi_de_quy_la_co_tien(tmp_path, monkeypatch):
    # 8. Mặc định khong_tien_phut = 20; CPU cây agy tăng trong 2 phút gần nhất = có tiến;
    #    file đổi đệ quy trong theo_doi = có tiến.
    assert linhx_runner.PHUT_KHONG_TIEN_MAC_DINH == 20
    monkeypatch.setattr(linhx_runner, "_goi_taskkill_cay", lambda _pid: None)

    # --- Phần A: Không có file đổi hay stdout mới, nhưng CPU tăng trong cửa sổ 2 phút -> vượt qua 20 phút và xong ở phút 26 ---
    thoi_gian_a = [1000.0]
    cpu_gia_a = [1.0]
    buoc_a = [0]
    proc_cpu = _TienTrinhGiaDangChay(pid=81001)

    def ngu_cpu_tang(_giay: float) -> None:
        buoc_a[0] += 1
        thoi_gian_a[0] += 90.0  # mỗi nhịp 1.5 phút (nằm trong cửa sổ 2 phút gần nhất)
        cpu_gia_a[0] += 0.4     # CPU cây agy tăng thêm 0.4 giây mỗi 1.5 phút
        if (thoi_gian_a[0] - 1000.0) >= 26 * 60.0:
            proc_cpu.hoan_tat("xong-nho-cpu")

    monkeypatch.setattr(linhx_runner, "_dong_ho", lambda: thoi_gian_a[0])
    monkeypatch.setattr(linhx_runner, "_ngu", ngu_cpu_tang)
    monkeypatch.setattr(linhx_runner, "_doc_cpu_cay_agy", lambda _pid: cpu_gia_a[0])
    monkeypatch.setattr(linhx_runner, "_tao_tien_trinh_agy", lambda *a, **kw: proc_cpu)

    cfg_a = {
        "tho": "may-2",
        "agy": "agy-gia",
        "agy_args": "--output-format json",
        "thu_muc": tmp_path / "viec-cpu-tang",
    }
    tt_a, kq_a, _, _, _ = linhx_runner.chay_agy(cfg_a, {"viec": "cpu-01", "de": "Tính toán nặng bằng CPU"})
    assert tt_a == "xong"
    assert kq_a == "xong-nho-cpu"
    assert proc_cpu.da_kill is False

    # --- Phần B: CPU tăng tới phút 6 rồi đứng im hẳn -> dừng đúng sau 20 phút không tiến kể từ phút 6 (tức ~phút 26) ---
    thoi_gian_b = [5000.0]
    cpu_gia_b = [2.0]
    proc_cpu_dung = _TienTrinhGiaDangChay(pid=81002)

    def ngu_cpu_dung(_giay: float) -> None:
        thoi_gian_b[0] += 60.0
        if (thoi_gian_b[0] - 5000.0) <= 360.0:
            cpu_gia_b[0] += 0.5  # chỉ tăng trong 6 phút đầu, sau đó đứng yên

    monkeypatch.setattr(linhx_runner, "_dong_ho", lambda: thoi_gian_b[0])
    monkeypatch.setattr(linhx_runner, "_ngu", ngu_cpu_dung)
    monkeypatch.setattr(linhx_runner, "_doc_cpu_cay_agy", lambda _pid: cpu_gia_b[0])
    monkeypatch.setattr(linhx_runner, "_tao_tien_trinh_agy", lambda *a, **kw: proc_cpu_dung)

    cfg_b = {
        "tho": "may-2",
        "agy": "agy-gia",
        "agy_args": "--output-format json",
        "thu_muc": tmp_path / "viec-cpu-dung",
    }
    tt_b, _, nk_b, _, _ = linhx_runner.chay_agy(cfg_b, {"viec": "cpu-02", "de": "Treo sau phút 6"})
    assert tt_b == "dung"
    assert "20 phút không tiến" in nk_b
    assert proc_cpu_dung.da_kill is True
    da_chay_b = thoi_gian_b[0] - 5000.0
    assert (6 + 20) * 60.0 <= da_chay_b < (6 + 22) * 60.0

    # --- Phần C: CPU đứng im (0.0), nhưng có file đổi đệ quy trong `theo_doi` (kể cả thư mục mới tạo trong lúc chạy) ---
    thoi_gian_c = [9000.0]
    buoc_c = [0]
    tm_theo_doi_moi = tmp_path / "wt-clone-moi"  # chưa tồn tại lúc bắt đầu!
    proc_td = _TienTrinhGiaDangChay(pid=81003)

    def ngu_theo_doi_de_quy(_giay: float) -> None:
        buoc_c[0] += 1
        thoi_gian_c[0] += 600.0  # mỗi bước 10 phút
        tep_sau = tm_theo_doi_moi / "src" / "cap2" / "cap3" / "module.py"
        tep_sau.parent.mkdir(parents=True, exist_ok=True)
        tep_sau.write_text(f"ver = {buoc_c[0]}\n", encoding="utf-8")
        if (thoi_gian_c[0] - 9000.0) >= 30 * 60.0:
            proc_td.hoan_tat("xong-nho-theo-doi")

    monkeypatch.setattr(linhx_runner, "_dong_ho", lambda: thoi_gian_c[0])
    monkeypatch.setattr(linhx_runner, "_ngu", ngu_theo_doi_de_quy)
    monkeypatch.setattr(linhx_runner, "_doc_cpu_cay_agy", lambda _pid: 0.0)
    monkeypatch.setattr(linhx_runner, "_tao_tien_trinh_agy", lambda *a, **kw: proc_td)

    cfg_c = {
        "tho": "may-2",
        "agy": "agy-gia",
        "agy_args": "--output-format json",
        "thu_muc": tmp_path / "viec-td",
    }
    viec_c = hang_doi_git.phan_tich_phieu(
        f"may: may-2\nloai: code\ntheo_doi: {tm_theo_doi_moi}\n\nClone và sửa sâu trong thư mục con.",
        "td-de-quy-01",
    )
    tt_c, kq_c, _, _, _ = linhx_runner.chay_agy(cfg_c, viec_c)
    assert tt_c == "xong"
    assert kq_c == "xong-nho-theo-doi"


def test_doc_cpu_cay_tien_trinh_that_tren_he_dieu_hanh():
    # Kiểm tra hàm đo CPU cây tiến trình thật bằng tiến trình con Python chạy vòng lặp tính toán ngắn
    kw = {"creationflags": 0x08000000} if os.name == "nt" else {}
    ma_con = "t = 0\nfor i in range(2_500_000):\n    t += i * i\nimport time; time.sleep(0.3)\n"
    bo_nho: dict = {}
    proc = subprocess.Popen([sys.executable, "-c", ma_con], **kw)
    try:
        cpu_dau = linhx_runner.doc_cpu_cay_tien_trinh(proc.pid, bo_nho_cay=bo_nho)
        han = time.monotonic() + 3.0
        cpu_sau = cpu_dau
        while time.monotonic() < han:
            time.sleep(0.05)
            cpu_sau = linhx_runner.doc_cpu_cay_tien_trinh(proc.pid, bo_nho_cay=bo_nho)
            if cpu_sau > cpu_dau + 0.01:
                break
            if proc.poll() is not None:
                break
        assert cpu_sau > 0.0
    finally:
        proc.wait(timeout=5)
