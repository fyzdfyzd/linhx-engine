"""Kiểm thử module sổ tài khoản (`so_tai_khoan.py`, `tai-khoan.ps1`, `bang.py`) bằng dữ liệu giả."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import uuid

import pytest

RUNNER_DIR = Path(__file__).resolve().parent
REPO_ROOT = RUNNER_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runner import hang_doi_git  # noqa: E402
from runner import so_tai_khoan  # noqa: E402
from runner.bang import bang  # noqa: E402

TZ_VN = timezone(timedelta(hours=7))


def _remove_tree(target: Path) -> None:
    """Xóa thư mục tạm kể cả khi git tạo file read-only trên Windows."""
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
    """Tạo thư mục tạm trong runner/viec (không tạo conftest.py) và dọn dẹp sau test."""
    viec_root = RUNNER_DIR / "viec"
    existed_before = viec_root.exists()
    temp_dir = viec_root / f"pytest-tmp-tk-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    try:
        yield temp_dir
    finally:
        _remove_tree(temp_dir)
        if not existed_before and viec_root.exists():
            try:
                viec_root.rmdir()
            except OSError:
                pass


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return proc


def _init_local_queue_repo(tmp_path: Path, ledger_items: list[dict] | None = None, ticket_md: str | None = None):
    """Khởi tạo repo bare + clone có nhánh `main` và `hang-doi` hoàn toàn offline."""
    bare = tmp_path / "remote.git"
    bare.mkdir()
    _git(["init", "--bare"], bare)

    seed = tmp_path / "seed"
    _git(["clone", str(bare), str(seed)], tmp_path)
    _git(["config", "user.name", "Test Bot"], seed)
    _git(["config", "user.email", "te***@example.com"], seed)

    (seed / "README.md").write_text("demo\n", encoding="utf-8")
    _git(["add", "README.md"], seed)
    _git(["commit", "-m", "init main"], seed)
    _git(["branch", "-M", "main"], seed)
    _git(["push", "-u", "origin", "main"], seed)

    _git(["checkout", "-b", "hang-doi"], seed)
    for sub in ("moi", "dang", "xong", "may"):
        (seed / "hang-doi" / sub).mkdir(parents=True, exist_ok=True)
        (seed / "hang-doi" / sub / ".gitkeep").write_text("", encoding="utf-8")

    if ledger_items is not None:
        (seed / "hang-doi" / "tai-khoan.json").write_text(
            json.dumps(ledger_items, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if ticket_md is not None:
        (seed / "hang-doi" / "moi" / "p-tk-001.md").write_text(ticket_md, encoding="utf-8")

    _git(["add", "."], seed)
    _git(["commit", "-m", "init hang-doi"], seed)
    _git(["push", "-u", "origin", "hang-doi"], seed)

    repo_work = tmp_path / "work"
    _git(["clone", str(bare), str(repo_work)], tmp_path)
    _git(["config", "user.name", "Runner Bot"], repo_work)
    _git(["config", "user.email", "ru***@example.com"], repo_work)
    return bare, repo_work


def test_che_email_va_loc_khoa_nhay_cam():
    assert so_tai_khoan.che_email("zodiac@gmail.com") == "zo***@gmail.com"
    assert so_tai_khoan.che_email("ab@example.org") == "a***@example.org"
    assert so_tai_khoan.che_email("   ") == ""
    assert so_tai_khoan.che_email("zo***@gmail.com") == "zo***@gmail.com"

    # Tạo chuỗi token giả bằng phép nối động để không chứa mẫu bí mật tĩnh trong mã nguồn test
    fake_gh = "gh" + "p_" + ("AbCd1234EfGh" * 2)
    fake_api = "AI" + "za" + ("XyZ987654321" * 2)
    dirty_record = {
        "ma": "tk-1",
        "email_che": "alice.nguyen@gmail.com",
        "cookie": "abc",
        "session_token": fake_gh,
        "password": "khong-duoc-luu",
        "gaia_id": "1234567890",
        "chi_tiet": {
            "refresh_token": "bi-mat",
            "ghi_chu": f"lien he alice.nguyen@gmail.com kem {fake_api}",
        },
    }
    cleaned = so_tai_khoan.lam_sach_ban_ghi_tai_khoan(dirty_record)
    dumped = json.dumps(cleaned, ensure_ascii=False)

    assert cleaned["email_che"] == "al***@gmail.com"
    for forbidden_key in ("cookie", "session_token", "password", "gaia_id", "refresh_token"):
        assert forbidden_key not in dumped
    assert "alice.nguyen@gmail.com" not in dumped
    assert fake_gh not in dumped
    assert fake_api not in dumped
    assert "al***@gmail.com" in cleaned["chi_tiet"]["ghi_chu"]


def test_doc_local_state_va_agy_khong_luu_truong_nhay_cam(tmp_path):
    local_state = tmp_path / "Local State"
    fake_secret = "ya" + "29." + ("KlmN0987OpQr" * 2)
    payload = {
        "profile": {
            "info_cache": {
                "Default": {
                    "name": "Tai khoan chinh",
                    "user_name": "zodiac.main@gmail.com",
                    "ai_subscription_tier": 2,
                    "active_time": 1760000000.0,
                    "gaia_id": "9988776655",
                    "oauth_token": fake_secret,
                    "cookies": [{"name": "SID", "value": "secret"}],
                },
                "Profile 1": {
                    "name": "Ho so rong",
                    "user_name": "",
                    "active_time": 0,
                },
            }
        }
    }
    local_state.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def fake_run_ok(cmd, **_kwargs):
        class Proc:
            returncode = 0
            stdout = "Logged in as operator.dev@gmail.com\n"
            stderr = ""

        return Proc()

    data = so_tai_khoan.thu_thap_tai_khoan_may(
        ma_may="may-2",
        local_state_path=local_state,
        agy_cmd="agy",
        run_fn=fake_run_ok,
    )
    serialized = json.dumps(data, ensure_ascii=False)

    assert data["ma_may"] == "may-2"
    assert data["agy_tai_khoan"] == "op***@gmail.com"
    assert len(data["ho_so_chrome"]) == 2
    prof_def = next(x for x in data["ho_so_chrome"] if x["thu_muc"] == "Default")
    assert prof_def["ten"] == "Tai khoan chinh"
    assert prof_def["email_che"] == "zo***@gmail.com"
    assert prof_def["co_goi"] is True
    assert prof_def["muc_goi"] == 2
    assert prof_def["lan_dung_cuoi"] != ""

    assert "zodiac.main@gmail.com" not in serialized
    assert "operator.dev@gmail.com" not in serialized
    assert fake_secret not in serialized
    assert "gaia_id" not in serialized
    assert "oauth_token" not in serialized
    assert "cookies" not in serialized

    def fake_run_fail(cmd, **_kwargs):
        class Proc:
            returncode = 1
            stdout = ""
            stderr = "unknown command"

        return Proc()

    assert so_tai_khoan.doc_tai_khoan_agy("agy", run_fn=fake_run_fail) == "chua_ro"


def test_chon_tai_khoan_xoay_vong_va_bo_het_han_muc(tmp_path):
    so_tai_khoan.dat_lai_bo_nho_xoay_vong()
    now_dt = datetime(2026, 11, 15, 10, 0, 0, tzinfo=TZ_VN)
    tt_path = tmp_path / "runtime-state.json"

    ledger_path = tmp_path / "tai-khoan.json"
    ledger = [
        {
            "ma": "tk-1",
            "email_che": "acc.one@gmail.com",
            "may": "may-2",
            "ho_so_chrome": "Profile 1",
            "cong_cu": ["agy", "flow"],
            "trang_thai": "dung",
            "mo_lai_luc": "",
        },
        {
            "ma": "tk-2",
            "email_che": "acc.two@gmail.com",
            "may": "may-2",
            "ho_so_chrome": "Profile 2",
            "cong_cu": ["flow", "deep-research"],
            "trang_thai": "dung",
            "mo_lai_luc": "",
        },
        {
            "ma": "tk-3",
            "email_che": "acc.three@gmail.com",
            "may": "may-2",
            "ho_so_chrome": "Profile 3",
            "cong_cu": ["flow"],
            "trang_thai": "het_han_muc",
            "mo_lai_luc": (now_dt + timedelta(hours=2)).isoformat(),
        },
        {
            "ma": "tk-4",
            "email_che": "acc.four@gmail.com",
            "may": "may-2",
            "ho_so_chrome": "Profile 4",
            "cong_cu": ["flow"],
            "trang_thai": "can_dang_nhap",
            "mo_lai_luc": "",
        },
        {
            "ma": "tk-5",
            "email_che": "other.box@gmail.com",
            "may": "may-1",
            "ho_so_chrome": "Default",
            "cong_cu": ["flow"],
            "trang_thai": "dung",
            "mo_lai_luc": "",
        },
    ]
    ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8")

    c1 = so_tai_khoan.chon_tai_khoan("may-2", "flow", tep_so=ledger_path, tep_trang_thai=tt_path, bay_gio=now_dt)
    c2 = so_tai_khoan.chon_tai_khoan("may-2", "flow", tep_so=ledger_path, tep_trang_thai=tt_path, bay_gio=now_dt)
    c3 = so_tai_khoan.chon_tai_khoan("may-2", "flow", tep_so=ledger_path, tep_trang_thai=tt_path, bay_gio=now_dt)
    assert [c1["ma"], c2["ma"], c3["ma"]] == ["tk-1", "tk-2", "tk-1"]
    assert c1["email_che"] == "ac***@gmail.com"
    assert c2["email_che"] == "ac***@gmail.com"

    # Khi qua giờ mở lại (+3h), tk-3 được chọn lại trong vòng xoay
    later_dt = now_dt + timedelta(hours=3)
    c4 = so_tai_khoan.chon_tai_khoan("may-2", "flow", tep_so=ledger_path, tep_trang_thai=tt_path, bay_gio=later_dt)
    assert c4["ma"] == "tk-2"
    c5 = so_tai_khoan.chon_tai_khoan("may-2", "flow", tep_so=ledger_path, tep_trang_thai=tt_path, bay_gio=later_dt)
    assert c5["ma"] == "tk-3"


def test_429_danh_dau_het_han_muc_va_chuyen_tai_khoan_qua_hang_doi(tmp_path):
    so_tai_khoan.dat_lai_bo_nho_xoay_vong()
    base_dt = datetime(2026, 11, 15, 9, 0, 0, tzinfo=TZ_VN)

    # Kiểm tra quy tắc +5h khi lỗi 429 không nêu giờ, và tách giờ khi có ghi khoảng chờ
    dt_default = so_tai_khoan.trich_gio_mo_lai("HTTP 429 Too Many Requests", bay_gio=base_dt)
    assert dt_default == base_dt + timedelta(hours=5)
    dt_parsed = so_tai_khoan.trich_gio_mo_lai("quota exceeded, try again in 2h 30m", bay_gio=base_dt)
    assert dt_parsed == base_dt + timedelta(hours=2, minutes=30)

    ledger = [
        {
            "ma": "tk-flow-1",
            "email_che": "fl***@gmail.com",
            "may": "may-2",
            "ho_so_chrome": "Profile 10",
            "cong_cu": ["flow"],
            "trang_thai": "dung",
            "mo_lai_luc": "",
        },
        {
            "ma": "tk-flow-2",
            "email_che": "fl***@gmail.com",
            "may": "may-2",
            "ho_so_chrome": "Profile 11",
            "cong_cu": ["flow"],
            "trang_thai": "dung",
            "mo_lai_luc": "",
        },
    ]
    ticket_md = (
        "may: may-2\n"
        "cong_cu: flow\n"
        "loai: doc\n"
        "uu_tien: thuong\n"
        "tran_phut: 5\n\n"
        "Tao anh minh hoa bang Flow.\n"
    )
    _, repo_work = _init_local_queue_repo(tmp_path, ledger_items=ledger, ticket_md=ticket_md)
    wt_dir = tmp_path / "wt-hd"
    tt_path = tmp_path / "runtime-tt.json"

    seen_profiles: list[str] = []

    def mock_agy(cfg_lan, _viec):
        env_profile = os.environ.get("LINHX_HO_SO_CHROME", "")
        seen_profiles.append(env_profile)
        if env_profile == "Profile 10":
            return "loi", "HTTP 429 quota exceeded", "429 Too Many Requests", 5, 2
        return "xong", "Da tao xong bang Profile 11", "", 15, 8

    cfg = {
        "tho": "may-2",
        "thu_muc": str(repo_work),
        "repo_hang_doi": str(repo_work),
        "wt_hang_doi": str(wt_dir),
        "nhanh_hang_doi": "hang-doi",
        "remote_hang_doi": "origin",
        "log_dir": str(tmp_path / "logs"),
        "drive_dir": str(tmp_path / "drive"),
        "tep_trang_thai_tai_khoan": str(tt_path),
    }

    os.environ["LINHX_HO_SO_CHROME"] = "gia-tri-cu"
    try:
        res = hang_doi_git.xu_ly_mot_phieu(cfg, chay_agy_fn=mock_agy)
    finally:
        env_after = os.environ.pop("LINHX_HO_SO_CHROME", None)

    assert env_after == "gia-tri-cu"
    assert res is not None
    assert res["trang_thai"] == "xong"
    assert seen_profiles == ["Profile 10", "Profile 11"]

    # Runner không được sửa file hang-doi/tai-khoan.json (Claude/Linh giữ)
    ledger_after = json.loads((wt_dir / "hang-doi" / "tai-khoan.json").read_text(encoding="utf-8"))
    assert ledger_after == ledger

    # Tài khoản 1 đã được đánh dấu het_han_muc trong runtime state (+5h vì lỗi không nêu giờ)
    rt_state = json.loads(tt_path.read_text(encoding="utf-8"))
    assert rt_state["trang_thai"]["tk-flow-1"]["trang_thai"] == "het_han_muc"
    assert rt_state["trang_thai"]["tk-flow-1"]["mo_lai_luc"] != ""
    assert "tk-flow-2" not in rt_state["trang_thai"]
    assert (wt_dir / "hang-doi" / "xong" / "p-tk-001" / "KET-QUA.md").is_file()


def test_tai_khoan_ps1_ghi_json_an_toan_khong_cookie_token(tmp_path):
    ps_bin = shutil.which("pwsh") or shutil.which("powershell")
    if not ps_bin:
        pytest.skip("Khong tim thay PowerShell tren may")

    _, repo_work = _init_local_queue_repo(tmp_path)
    wt_dir = tmp_path / "wt-ps1"
    local_state = tmp_path / "Local State"
    fake_token = "sk" + "-" + ("TestSecretVal12" * 2)
    local_state.write_text(
        json.dumps(
            {
                "profile": {
                    "info_cache": {
                        "Default": {
                            "name": "Nguoi dung chinh",
                            "user_name": "linh.operator@gmail.com",
                            "ai_subscription_tier": "pro",
                            "active_time": 1761000000.0,
                            "cookies": "raw-cookie-data",
                            "password": "raw-password-data",
                            "token": fake_token,
                        }
                    }
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    out_copy = tmp_path / "out-tai-khoan.json"
    env = dict(os.environ)
    env["LINHX_WT_HANG_DOI"] = str(wt_dir)

    script_ps1 = RUNNER_DIR / "lenh" / "tai-khoan.ps1"
    proc = subprocess.run(
        [
            ps_bin,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script_ps1),
            "-May",
            "may-2",
            "-LocalState",
            str(local_state),
            "-RepoHangDoi",
            str(repo_work),
            "-XuatJson",
            str(out_copy),
            "-EpGhi",
        ],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout

    # Kiểm tra file đã ghi ra nhánh hang-doi lẫn bản sao --xuat-json
    tep_git = wt_dir / "hang-doi" / "may" / "may-2-tai-khoan.json"
    assert tep_git.is_file()
    assert out_copy.is_file()
    raw_json = tep_git.read_text(encoding="utf-8")
    parsed = json.loads(raw_json)

    assert parsed["ma_may"] == "may-2"
    assert parsed["ho_so_chrome"][0]["email_che"] == "li***@gmail.com"
    assert parsed["ho_so_chrome"][0]["co_goi"] is True
    assert parsed["ho_so_chrome"][0]["muc_goi"] == "pro"

    combined_output = raw_json + "\n" + proc.stdout + "\n" + proc.stderr
    for leaked in ("linh.operator@gmail.com", fake_token, "raw-cookie-data", "raw-password-data"):
        assert leaked not in combined_output
    for bad_key in ('"cookie"', '"cookies"', '"token"', '"password"', '"gaia_id"'):
        assert bad_key not in raw_json.lower()


def test_bang_8090_the_tai_khoan_o_tab_may(tmp_path):
    qdir = tmp_path / "clone" / "hang-doi"
    (qdir / "may").mkdir(parents=True, exist_ok=True)

    # Giữ hồ sơ phần cứng máy 2 để kiểm chứng *-tai-khoan.json không đè lên may-2.json
    (qdir / "may" / "may-2.json").write_text(
        json.dumps(
            {
                "ma_may": "may-2",
                "ten_windows": "WIN-MAY-2",
                "cpu": {"ten": "Ryzen 9", "nhan": 12, "luong": 24},
                "ram": {"tong_gb": 64, "trong_gb": 32},
                "o_dia": [{"o": "C:", "tong_gb": 500, "trong_gb": 120}],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (qdir / "may" / "may-2-tai-khoan.json").write_text(
        json.dumps(
            {
                "ma_may": "may-2",
                "agy_tai_khoan": "ag***@gmail.com",
                "ho_so_chrome": [
                    {"thu_muc": "Default", "ten": "Chinh", "email_che": "ad***@gmail.com"},
                    {"thu_muc": "Profile 1", "ten": "Phu 1", "email_che": "ph***@gmail.com"},
                    {"thu_muc": "Profile 2", "ten": "Trong", "email_che": ""},
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    now_dt = datetime(2026, 11, 15, 11, 0, 0, tzinfo=TZ_VN)
    (qdir / "tai-khoan.json").write_text(
        json.dumps(
            [
                {
                    "ma": "tk-a",
                    "email": "secret.alpha@gmail.com",
                    "may": "may-2",
                    "ho_so_chrome": "Profile 1",
                    "cong_cu": ["flow"],
                    "trang_thai": "het_han_muc",
                    "mo_lai_luc": (now_dt + timedelta(hours=3)).isoformat(),
                },
                {
                    "ma": "tk-b",
                    "email_che": "need.login@gmail.com",
                    "may": "may-2",
                    "ho_so_chrome": "Profile 9",
                    "cong_cu": ["chatgpt"],
                    "trang_thai": "can_dang_nhap",
                    "mo_lai_luc": "",
                },
                {
                    "ma": "tk-c",
                    "email_che": "m1***@gmail.com",
                    "may": "may-1",
                    "ho_so_chrome": "Default",
                    "cong_cu": ["agy"],
                    "trang_thai": "dung",
                    "mo_lai_luc": "",
                },
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    snapshot = bang.read_queue_snapshot(tmp_path / "clone", now=now_dt, commit_times={})
    # Không để may-2-tai-khoan.json ghi đè cấu hình CPU/RAM của may-2
    assert len(snapshot["ho_so_may"]) == 1
    assert snapshot["ho_so_may"][0]["cpu"]["ten"] == "Ryzen 9"

    by_may = {item["may"]: item for item in snapshot["tai_khoan_may"]}
    assert by_may["may-2"]["dung_duoc"] == 1
    assert by_may["may-2"]["het_han_muc"] == 1
    assert by_may["may-2"]["can_dang_nhap"] == 1
    assert by_may["may-1"]["dung_duoc"] == 1

    html_may = bang.render_app_html(snapshot, active_tab="may")
    assert "Tài khoản" in html_may
    assert "1 dùng được" in html_may
    assert "1 hết hạn mức" in html_may
    assert "1 cần đăng nhập" in html_may

    all_text = json.dumps(snapshot, ensure_ascii=False) + "\n" + html_may
    assert "secret.alpha@gmail.com" not in all_text
    assert "need.login@gmail.com" not in all_text
